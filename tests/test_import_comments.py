import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "import_comments.py"
SPEC = importlib.util.spec_from_file_location("import_comments", SCRIPT)
import_comments = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(import_comments)


class SanitizeTextTests(unittest.TestCase):
    def test_plain_text_preserves_paragraphs_and_decodes_entities(self):
        self.assertEqual(
            import_comments.sanitize_text("<p>Hello &amp; welcome</p><p>Second<br>line</p>"),
            "Hello & welcome\n\nSecond\nline",
        )

    def test_link_keeps_only_visible_text(self):
        result = import_comments.sanitize_text('<a href="https://private.example/path?q=secret">Visible label</a>')
        self.assertEqual(result, "Visible label")
        self.assertNotIn("private.example", result)
        self.assertNotIn("secret", result)

    def test_active_and_hidden_subtrees_are_removed(self):
        source = "before<script>script secret</script><style>css secret</style><svg><text>svg secret</text></svg><math>math secret</math><iframe>frame secret</iframe><object>object secret</object><form>form secret</form><template>template secret</template><noscript>noscript secret</noscript>after"
        self.assertEqual(import_comments.sanitize_text(source), "beforeafter")

    def test_void_blocked_element_does_not_hide_following_text(self):
        self.assertEqual(import_comments.sanitize_text("before<embed>after<br>end"), "beforeafter\nend")


class TreeTests(unittest.TestCase):
    def actions(self, *ids):
        return {str(i): {"action": "include", "reason": "reviewed"} for i in ids}

    def test_public_schema_is_allowlisted(self):
        comment = {
            "id": "10", "parent": "0", "date": "2015-01-02 03:04:05",
            "author": "<b>A&amp;B</b>", "content": "<p>Text</p>",
            "email": "private@example.test", "ip": "192.0.2.1", "url": "https://private.test",
        }
        record, = import_comments.normalize_comment_tree([comment], self.actions(10))
        self.assertEqual(set(record), {"id", "parent_id", "author", "date", "text"})
        self.assertEqual(record["author"], "A&B")
        self.assertEqual(record["text"], "Text")
        self.assertNotIn("private", str(record))

    def test_excluded_parent_is_skipped_to_retained_ancestor(self):
        comments = [
            {"id": "1", "parent": "0", "date": "2015-01-01", "author": "A", "content": "root"},
            {"id": "2", "parent": "1", "date": "2015-01-02", "author": "B", "content": "excluded"},
            {"id": "3", "parent": "2", "date": "2015-01-03", "author": "C", "content": "child"},
        ]
        actions = self.actions(1, 2, 3)
        actions["2"]["action"] = "exclude"
        result = import_comments.normalize_comment_tree(comments, actions)
        self.assertEqual([(r["id"], r["parent_id"]) for r in result], [(1, 0), (3, 1)])

    def test_six_comment_nodes_are_allowed_and_safety_limit_is_100(self):
        comments = [{"id": str(i), "parent": str(i - 1) if i > 1 else "0", "date": f"2015-01-{i:02d}", "author": "A", "content": "x"} for i in range(1, 7)]
        self.assertEqual(len(import_comments.normalize_comment_tree(comments, self.actions(*range(1, 7)))), 6)
        comments = [{"id": str(i), "parent": str(i - 1) if i > 1 else "0", "date": f"2015-{1 + (i - 1) // 28:02d}-{1 + (i - 1) % 28:02d}", "author": "A", "content": "x"} for i in range(1, 102)]
        with self.assertRaisesRegex(ValueError, "safety limit of 100"):
            import_comments.normalize_comment_tree(comments, self.actions(*range(1, 102)))

    def test_cycle_and_duplicate_ids_rejected(self):
        cycle = [
            {"id": "1", "parent": "2", "date": "a", "author": "A", "content": "x"},
            {"id": "2", "parent": "1", "date": "b", "author": "A", "content": "x"},
        ]
        with self.assertRaisesRegex(ValueError, "cycle"):
            import_comments.normalize_comment_tree(cycle, self.actions(1, 2))
        duplicate = [cycle[0], dict(cycle[0])]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            import_comments.normalize_comment_tree(duplicate, self.actions(1))

    def test_unmapped_parent_becomes_root_and_siblings_sort_by_date_then_id(self):
        comments = [
            {"id": "8", "parent": "404", "date": "2015-01-02", "author": "A", "content": "later"},
            {"id": "7", "parent": "0", "date": "2015-01-01", "author": "A", "content": "first"},
            {"id": "6", "parent": "0", "date": "2015-01-01", "author": "A", "content": "same date"},
        ]
        result = import_comments.normalize_comment_tree(comments, self.actions(6, 7, 8))
        self.assertEqual([r["id"] for r in result], [6, 7, 8])
        self.assertEqual(result[-1]["parent_id"], 0)


class MappingTests(unittest.TestCase):
    def test_approved_normal_comment_with_unmapped_target_fails(self):
        source = [{"comment_ID": "4", "comment_post_ID": "404", "comment_approved": "1", "comment_type": "comment"}]
        with self.assertRaisesRegex(ValueError, "unmapped WordPress post IDs"):
            import_comments.eligible_comments(source, {})

    def test_only_published_post_or_page_with_unique_matching_frontmatter_url(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "post.md").write_text('---\ntitle: Post\nurl: "/2015/06/05/example/"\n---\n', encoding="utf-8")
            (root / "page.md").write_text('---\ntitle: Page\nurl: "/about/"\n---\n', encoding="utf-8")
            posts = [
                {"ID": "590", "post_type": "post", "post_status": "publish", "post_date": "2015-06-05 10:00:00", "post_name": "example"},
                {"ID": "591", "post_type": "page", "post_status": "publish", "post_date": "2015-06-05 10:00:00", "post_name": "about"},
                {"ID": "592", "post_type": "post", "post_status": "draft", "post_date": "2015-06-05 10:00:00", "post_name": "example"},
            ]
            mapping = import_comments.map_published_pages(posts, root)
            self.assertEqual(set(mapping), {"590", "591"})
            self.assertEqual(mapping["590"], root / "post.md")

    def test_duplicate_frontmatter_url_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("one.md", "two.md"):
                (root / name).write_text('---\ntitle: Duplicate\nurl: "/2015/06/05/example/"\n---\n', encoding="utf-8")
            post = {"ID": "590", "post_type": "post", "post_status": "publish", "post_date": "2015-06-05 10:00:00", "post_name": "example"}
            with self.assertRaisesRegex(ValueError, "Ambiguous site mapping"):
                import_comments.map_published_pages([post], root)


class DecisionTests(unittest.TestCase):
    def test_decisions_must_cover_every_eligible_id_and_include_reasons(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "decisions.json"
            path.write_text('{"1":{"action":"include","reason":"reviewed"}}', encoding="utf-8")
            self.assertEqual(set(import_comments.load_decisions(path, {"1"})), {"1"})
            with self.assertRaisesRegex(ValueError, "cover all"):
                import_comments.load_decisions(path, {"1", "2"})
            path.write_text('{"1":{"action":"exclude","reason":"  "}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-empty reason"):
                import_comments.load_decisions(path, {"1"})

    def test_local_dates_are_validated_and_preserved(self):
        self.assertEqual(import_comments.validate_local_date("2015-06-05 11:51:14", 7), "2015-06-05 11:51:14")
        with self.assertRaisesRegex(ValueError, "Invalid local comment date"):
            import_comments.validate_local_date("2015-02-30 11:51:14", 7)


if __name__ == "__main__":
    unittest.main()
