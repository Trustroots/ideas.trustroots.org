"""Check archived discussions against the public data and generated Hugo pages."""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


class Discussion(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.comments = {}
        self.current = None
        self.body_level = 0
        self.level = 0
        self.body_tags = []
        self.feed(document)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = attrs.get("class", "").split()
        if "archived-comment" in classes:
            identifier = int(attrs["id"].removeprefix("comment-"))
            if identifier in self.comments:
                raise AssertionError("Duplicate rendered comment anchor")
            self.current = {"parent": int(attrs["data-parent-id"]), "text": ""}
            self.comments[identifier] = self.current
        if self.body_level:
            self.body_tags.append(tag)
        if "comment-body" in classes:
            self.body_level = self.level + 1
        if tag not in {"br", "hr", "img", "input", "meta", "link", "wbr", "source"}:
            self.level += 1

    def handle_endtag(self, tag):
        self.level -= 1
        if self.body_level and self.level < self.body_level:
            self.body_level = 0

    def handle_data(self, data):
        if self.body_level:
            self.current["text"] += data


class ArchivedComments(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]
    generated = Path(os.environ.get("SITE_TEST_DIR", "public"))

    def test_public_records_and_rendered_threads_match(self):
        identifiers = set()
        mapped = set()
        deepest = 0
        for page in (self.root / "content").rglob("*.md"):
            source = page.read_text()
            match = re.search(r"^comments_id:\s*[\"']?(\d+)", source, re.M)
            if not match:
                continue
            post_id = match[1]
            self.assertNotIn(post_id, mapped, "A discussion belongs to one page")
            mapped.add(post_id)
            records = json.loads((self.root / "data/comments" / (post_id + ".json")).read_text())
            url = re.search(r'^url:\s*[\"\']([^\"\']+)', source, re.M)[1]
            document = (self.generated / url.strip("/") / "index.html").read_text()
            parsed = Discussion(document)
            self.assertEqual(len(parsed.comments), len(records))
            self.assertIn("Archived discussion", document)
            self.assertEqual(parsed.body_tags, [], "Comment bodies must contain only escaped text")
            by_id = {record["id"]: record for record in records}
            for record in records:
                with self.subTest(comment=record["id"]):
                    self.assertEqual(set(record), {"id", "parent_id", "author", "date", "text"})
                    self.assertNotIn(record["id"], identifiers)
                    identifiers.add(record["id"])
                    rendered = parsed.comments[record["id"]]
                    self.assertEqual(rendered["parent"], record["parent_id"])
                    self.assertEqual(rendered["text"].strip(), record["text"].strip())
                    ancestors = set()
                    cursor = record
                    while cursor["parent_id"]:
                        self.assertNotIn(cursor["id"], ancestors, "Reply cycle")
                        ancestors.add(cursor["id"])
                        self.assertIn(cursor["parent_id"], by_id, "Parent belongs to same page")
                        cursor = by_id[cursor["parent_id"]]
                    deepest = max(deepest, len(ancestors))
        self.assertEqual(len(identifiers), 136, "Reviewed historical import count")
        self.assertEqual(len(mapped), 28, "Reviewed historical page count")
        self.assertEqual(deepest, 5, "Preserve the deepest original reply thread")
        comparison = json.loads((self.root / "data/comments/590.json").read_text())
        self.assertEqual(len(comparison), 18)
        self.assertEqual(mapped, {path.stem for path in (self.root / "data/comments").glob("*.json")})

    def test_comments_are_absent_from_search_and_feeds(self):
        search = (self.generated / "search-index.json").read_text()
        feed = (self.generated / "index.xml").read_text()
        for document in (search, feed):
            self.assertNotIn("archived-comment", document)
            self.assertNotIn("#comment-", document)
        # Choose distinctive long comments rather than common phrases that may
        # also occur in articles. Every full comment must remain outside feeds.
        for path in (self.root / "data/comments").glob("*.json"):
            for record in json.loads(path.read_text()):
                text = record["text"]
                if len(text) > 180:
                    self.assertNotIn(text, json.dumps(json.loads(search), ensure_ascii=False))
                    self.assertNotIn(text, feed)

    def test_hugo_escapes_literal_markup_and_does_not_autolink(self):
        hugo = os.environ.get("HUGO_BINARY") or shutil.which("hugo")
        self.assertTrue(hugo, "Set HUGO_BINARY or install Hugo for rendering tests")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "layouts/partials").mkdir(parents=True)
            (root / "content").mkdir()
            (root / "data/comments").mkdir(parents=True)
            (root / "hugo.toml").write_text('baseURL="https://example.test/"\ndisableKinds=["taxonomy", "term", "RSS", "sitemap"]\n')
            (root / "layouts/baseof.html").write_text('{{ block "main" . }}{{ end }}')
            (root / "layouts/home.html").write_text('Fixture')
            shutil.copyfile(self.root / "layouts/single.html", root / "layouts/single.html")
            shutil.copyfile(self.root / "layouts/partials/archived-comments.html", root / "layouts/partials/archived-comments.html")
            for name in ("post-taxonomies", "sidebar"):
                (root / "layouts/partials" / (name + ".html")).write_text("")
            (root / "content/fixture.md").write_text('---\ntitle: Fixture\ncomments_id: 42\n---\nArticle only.\n')
            text = '<script>alert("test")</script> & https://example.test/plain\n\nSecond paragraph'
            record = {"id": 123, "parent_id": 0, "author": '<img src=x onerror="test">', "date": "2015-01-02 03:04:05", "text": text}
            (root / "data/comments/42.json").write_text(json.dumps([record]))
            result = subprocess.run([hugo, "--source", str(root), "--minify", "--panicOnWarning"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            document = (root / "public/fixture/index.html").read_text()
            parsed = Discussion(document)
            self.assertEqual(parsed.comments[123]["text"], text)
            self.assertEqual(parsed.body_tags, [])
            self.assertNotIn("<script>", document)
            self.assertNotIn("<img", document)
            self.assertNotIn('href="https://example.test/plain', document)


if __name__ == "__main__":
    unittest.main()
