#!/usr/bin/env python3
"""Import reviewed WordPress comments as plain JSON data for Hugo."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import gzip
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable


PRIVATE_COMMENT_TYPES = {"comment"}
MAX_COMMENT_DEPTH = 100
BLOCKED_TAGS = {
    "script", "style", "svg", "math", "iframe", "object", "embed", "form",
    "template", "noscript",
}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
BLOCK_TAGS = {"address", "article", "blockquote", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ol", "p", "pre", "section", "table", "tr", "ul"}


def rows(text: str):
    """Parse SQL value tuples using the backup reader's dependency-free parser."""
    i = 0
    size = len(text)
    while i < size:
        if text[i] in ',; \r\n':
            i += 1
            continue
        if text[i] != '(':
            raise ValueError(f"Unexpected SQL tuple at {i}: {text[i:i+30]!r}")
        i += 1
        row = []
        while True:
            if text[i] == "'":
                i += 1
                value = []
                while i < size:
                    c = text[i]
                    i += 1
                    if c == "\\":
                        c = text[i]
                        i += 1
                        value.append({'0':'\0','n':'\n','r':'\r','t':'\t','b':'\b','Z':'\x1a'}.get(c,c))
                    elif c == "'":
                        if i < size and text[i] == "'":
                            value.append("'")
                            i += 1
                        else:
                            break
                    else:
                        value.append(c)
                row.append(''.join(value))
            else:
                start = i
                while text[i] not in ',)':
                    i += 1
                value = text[start:i]
                row.append(None if value == 'NULL' else value)
            if text[i] == ',':
                i += 1
            elif text[i] == ')':
                i += 1
                yield row
                break
            else:
                raise ValueError('Unexpected SQL value separator')


def read_wp_tables(sql_gzip: Path) -> dict[str, list[dict[str, str | None]]]:
    """Read wp_posts/wp_comments from a mysqldump gzip file."""
    wanted = {"wp_posts", "wp_comments"}
    columns: dict[str, list[str]] = {}
    records: dict[str, list[dict[str, str | None]]] = {name: [] for name in wanted}
    current: str | None = None
    with gzip.open(sql_gzip, "rt", encoding="utf-8", errors="strict") as stream:
        for line in stream:
            match = re.match(r"CREATE TABLE `([^`]+)`", line)
            if match:
                current = match[1]
                columns[current] = []
            elif current and (match := re.match(r"  `([^`]+)`", line)):
                columns[current].append(match[1])
            elif current and line.startswith(")"):
                current = None
            elif match := re.match(r"INSERT INTO `([^`]+)` VALUES (.*);\s*$", line):
                table = match[1]
                if table not in wanted:
                    continue
                names = columns.get(table)
                if not names:
                    raise ValueError(f"Missing CREATE TABLE definition for {table}")
                for row in rows(match[2]):
                    if len(row) != len(names):
                        raise ValueError(f"Column count mismatch in {table}")
                    records[table].append(dict(zip(names, row)))
    return records


class _PlainText(HTMLParser):
    """Extract visible text while discarding markup, attributes and active trees."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.blocked: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.blocked:
            if tag not in VOID_TAGS:
                self.blocked.append(tag)
            return
        if tag in BLOCKED_TAGS:
            if tag not in VOID_TAGS:
                self.blocked.append(tag)
        elif tag == "br":
            self.parts.append("\n")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.blocked:
            return
        if tag in BLOCKED_TAGS:
            return
        if tag == "br" or tag in BLOCK_TAGS:
            self.parts.append("\n" if tag == "br" else "\n\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.blocked:
            if tag in self.blocked:
                while self.blocked:
                    popped = self.blocked.pop()
                    if popped == tag:
                        break
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if not self.blocked:
            self.parts.append(data)


def sanitize_text(value: str) -> str:
    parser = _PlainText()
    parser.feed(value)
    parser.close()
    text = "".join(parser.parts).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[\t\f\v ]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _frontmatter(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, Any] = {}
    for line in content[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        try:
            result[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            result[key] = value.strip('"\'')
    return result


def _post_url(post: dict[str, str | None]) -> str:
    slug = (post.get("post_name") or "").strip("/")
    if not slug:
        return ""
    if post.get("post_type") == "page":
        return f"/{slug}/"
    date = post.get("post_date") or ""
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", date)
    return f"/{match[1]}/{match[2]}/{match[3]}/{slug}/" if match else ""


def map_published_pages(posts: Iterable[dict[str, str | None]], site_root: Path) -> dict[str, Path]:
    by_url: dict[str, list[Path]] = defaultdict(list)
    for path in site_root.rglob("*.md"):
        frontmatter = _frontmatter(path)
        url = frontmatter.get("url")
        if isinstance(url, str) and url.startswith("/"):
            by_url[url].append(path)
    mapping: dict[str, Path] = {}
    for post in posts:
        if post.get("post_status") != "publish" or post.get("post_type") not in {"post", "page"}:
            continue
        url = _post_url(post)
        matches = by_url.get(url, [])
        if len(matches) > 1:
            raise ValueError(f"Ambiguous site mapping for WordPress ID {post.get('ID')} at {url}: {matches}")
        if len(matches) == 1:
            mapping[str(post["ID"])] = matches[0]
    return mapping


def _int(value: Any, field: str) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc


def validate_local_date(value: Any, comment_id: Any) -> str:
    date = str(value or "")
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise ValueError(f"Invalid local comment date for ID {comment_id}: {date!r}") from exc
    return date


def normalize_comment_tree(comments: list[dict[str, Any]], actions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply decisions, repair excluded parents, then sort sibling lists chronologically."""
    by_id = {str(c["id"]): c for c in comments}
    if len(by_id) != len(comments):
        raise ValueError("Duplicate comment IDs")
    retained = {cid for cid in by_id if actions[cid]["action"] == "include"}

    def retained_parent(cid: str) -> int:
        seen = {cid}
        parent = _int(by_id[cid].get("parent"), "comment parent")
        while parent:
            parent_id = str(parent)
            if parent_id in seen:
                raise ValueError(f"Comment parent cycle at {cid}")
            seen.add(parent_id)
            candidate = by_id.get(parent_id)
            if candidate is None:
                return 0
            if parent_id in retained:
                return int(parent_id)
            parent = _int(candidate.get("parent"), "comment parent")
        return 0

    # A cycle can be unreachable from root, so inspect retained parent chains directly.
    for cid in retained:
        seen: set[str] = set()
        current = cid
        while current in retained:
            if current in seen:
                raise ValueError(f"Comment parent cycle at {cid}")
            seen.add(current)
            current_parent = _int(by_id[current].get("parent"), "comment parent")
            current = str(current_parent) if current_parent else ""
        # A retained child can pass through excluded ancestors; inspect that chain too.
        current = cid
        seen.clear()
        while current in by_id:
            if current in seen:
                raise ValueError(f"Comment parent cycle at {cid}")
            seen.add(current)
            current_parent = _int(by_id[current].get("parent"), "comment parent")
            current = str(current_parent) if current_parent else ""

    children: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for cid in retained:
        c = by_id[cid]
        children[retained_parent(cid)].append(c)
    for siblings in children.values():
        siblings.sort(key=lambda c: (str(c.get("date") or ""), int(c["id"])))

    ordered: list[dict[str, Any]] = []
    visiting: set[int] = set()

    def visit(parent: int, depth: int) -> None:
        if depth > MAX_COMMENT_DEPTH:
            raise ValueError(f"Comment nesting exceeds safety limit of {MAX_COMMENT_DEPTH}")
        if parent in visiting:
            raise ValueError("Comment tree cycle")
        visiting.add(parent)
        for c in children.get(parent, []):
            cid = str(c["id"])
            action = actions[cid]
            author = action.get("author", c.get("author", ""))
            text = action.get("text", c.get("content", ""))
            record = {
                "id": int(cid),
                "parent_id": retained_parent(cid),
                "author": sanitize_text(str(author)) or "Anonymous",
                "date": str(c.get("date") or ""),
                "text": sanitize_text(str(text)),
            }
            ordered.append(record)
            visit(int(cid), depth + 1)
        visiting.remove(parent)

    visit(0, 0)
    if len(ordered) != len(retained):
        raise ValueError("Unreachable comment tree nodes")
    return ordered


def load_decisions(path: Path, eligible_ids: set[str]) -> dict[str, dict[str, Any]]:
    decisions = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(decisions, dict):
        raise ValueError("Review decisions must be a JSON object keyed by comment ID")
    got = set(map(str, decisions))
    if got != eligible_ids:
        missing = sorted(eligible_ids - got, key=int)
        extra = sorted(got - eligible_ids)
        raise ValueError(f"Review decisions must cover all {len(eligible_ids)} eligible comments; missing={missing[:10]} extra={extra[:10]}")
    for cid, decision in decisions.items():
        if not isinstance(decision, dict) or decision.get("action") not in {"include", "exclude"} or not str(decision.get("reason", "")).strip():
            raise ValueError(f"Decision {cid} needs action include/exclude and a non-empty reason")
        for key in ("author", "text"):
            if key in decision and not isinstance(decision[key], str):
                raise ValueError(f"Decision {cid} {key} override must be a string")
    return {str(k): v for k, v in decisions.items()}


def eligible_comments(comments: Iterable[dict[str, str | None]], mapped: dict[str, Path]) -> list[dict[str, str | None]]:
    candidates = [c for c in comments if c.get("comment_approved") == "1" and c.get("comment_type") in PRIVATE_COMMENT_TYPES]
    unmapped = sorted({str(c.get("comment_post_ID")) for c in candidates if str(c.get("comment_post_ID")) not in mapped})
    if unmapped:
        raise ValueError(f"Approved normal comments target unmapped WordPress post IDs: {unmapped}")
    return candidates


def _write_private_report(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".comments-report-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def import_comments(sql_gzip: Path, decisions_path: Path, site_root: Path, private_report: Path) -> dict[str, Any]:
    tables = read_wp_tables(sql_gzip)
    posts = tables["wp_posts"]
    all_comments = tables["wp_comments"]
    mapped = map_published_pages(posts, site_root)
    eligible = eligible_comments(all_comments, mapped)
    eligible_ids = {str(c["comment_ID"]) for c in eligible}
    decisions = load_decisions(decisions_path, eligible_ids)

    # The private report intentionally preserves sensitive source fields and must stay outside the site/repository.
    report_abs = private_report.resolve()
    if report_abs == site_root.resolve() or site_root.resolve() in report_abs.parents:
        raise ValueError("Private report path must be outside the site root")
    private_rows = []
    for c in all_comments:
        decision = decisions.get(str(c.get("comment_ID")))
        private_rows.append({
            "id": c.get("comment_ID"), "post_id": c.get("comment_post_ID"),
            "status": c.get("comment_approved"), "type": c.get("comment_type"),
            "author": c.get("comment_author"), "email": c.get("comment_author_email"),
            "url": c.get("comment_author_url"), "ip": c.get("comment_author_IP"),
            "agent": c.get("comment_agent"), "content": c.get("comment_content"),
            "action": decision["action"] if decision else "exclude",
            "reason": decision["reason"] if decision else "Not eligible: pending, spam, pingback, or non-comment record",
        })
    _write_private_report(private_report, json.dumps(private_rows, ensure_ascii=False, indent=2) + "\n")

    by_post: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in eligible:
        by_post[str(c["comment_post_ID"])].append({
            "id": str(c["comment_ID"]), "parent": c.get("comment_parent"),
            "date": validate_local_date(c.get("comment_date"), c.get("comment_ID")), "author": c.get("comment_author"),
            "content": c.get("comment_content"),
        })
    # Validate and normalize every post before the first public write.
    normalized: dict[str, list[dict[str, Any]]] = {}
    frontmatter_updates: dict[Path, str] = {}
    for post_id, group in by_post.items():
        normalized[post_id] = normalize_comment_tree(group, decisions)
        page = mapped[post_id]
        content = page.read_text(encoding="utf-8")
        if content.startswith("---\n"):
            close = content.find("\n---", 4)
            if close < 0:
                raise ValueError(f"Malformed frontmatter: {page}")
            head = content[4:close]
            if re.search(r"^comments_id:", head, re.M):
                head = re.sub(r"^comments_id:.*$", f"comments_id: {int(post_id)}", head, flags=re.M)
            else:
                head += f"\ncomments_id: {int(post_id)}"
            frontmatter_updates[page] = "---\n" + head + content[close:]
        else:
            raise ValueError(f"Missing frontmatter: {page}")
    output_root = site_root / "data" / "comments"
    output_root.mkdir(parents=True, exist_ok=True)
    for post_id, records in normalized.items():
        data_file = output_root / f"{post_id}.json"
        data_file.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for page, content in frontmatter_updates.items():
        page.write_text(content, encoding="utf-8")
    output_count = sum(len(records) for records in normalized.values())
    return {"eligible": len(eligible), "included": output_count, "mapped_targets": len(by_post), "private_report": str(private_report)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sql", type=Path, required=True, help="WordPress SQL gzip dump")
    parser.add_argument("--decisions", type=Path, required=True, help="Private review JSON keyed by comment ID")
    parser.add_argument("--site-root", type=Path, required=True, help="Hugo site root (writes data/comments and comments_id frontmatter)")
    parser.add_argument("--private-report", type=Path, required=True, help="Sensitive audit JSON path outside the site root")
    args = parser.parse_args(argv)
    try:
        result = import_comments(args.sql, args.decisions, args.site_root, args.private_report)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"import_comments: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
