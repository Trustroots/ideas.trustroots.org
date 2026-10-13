"""Exercise the smoke checks against real Hugo output and broken copies."""
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import check


class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(os.environ.get("SITE_TEST_DIR", "public"))
        for filename in (
            "comparison-of-hospitality-exchange-platforms/index.html",
            "2025/11/08/keep-trustroots-free-forever-ever/index.html",
            "brand/trustroots-tree-white.svg", "brand/bewelcome.svg",
            "brand/couchers.png", "index.xml",
        ):
            target = self.root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / filename, target)
        (self.root / "revision.txt").write_text("current-commit\n")
        self.args = SimpleNamespace(
            directory=str(self.root), live=False, revision="current-commit",
            base_url=os.environ.get("SITE_BASE_URL", "https://trustroots.github.io/ideas.trustroots.org/"),
        )

    def test_current_site_passes(self):
        check(self.args)

    def test_stale_deployment_fails(self):
        (self.root / "revision.txt").write_text("previous-commit\n")
        with self.assertRaisesRegex(AssertionError, "Published revision"):
            check(self.args)

    def test_missing_table_logos_fail(self):
        page = self.root / "comparison-of-hospitality-exchange-platforms/index.html"
        page.write_text(page.read_text().replace("brand/couchers.png", "brand/missing.png"))
        with self.assertRaisesRegex(AssertionError, "Logo missing"):
            check(self.args)

    def test_html_instead_of_image_fails(self):
        (self.root / "brand/couchers.png").write_text("<html>Not found</html>")
        with self.assertRaisesRegex(AssertionError, "does not return an image"):
            check(self.args)

    def test_wrong_base_path_fails(self):
        self.args.base_url = "https://example.org/wrong-path/"
        with self.assertRaisesRegex(AssertionError, "Logo missing"):
            check(self.args)


if __name__ == "__main__":
    unittest.main()
