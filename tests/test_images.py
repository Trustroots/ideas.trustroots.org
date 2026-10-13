"""Verify all generated local images and the restored historical media."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit


class Images(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.sources = []
        self.feed(document)

    def handle_starttag(self, tag, attributes):
        if tag == "img":
            self.sources.append(dict(attributes).get("src", ""))


class SiteImages(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]
    generated = Path(os.environ.get("SITE_TEST_DIR", "public"))
    prefix = urlsplit(os.environ.get("SITE_BASE_URL", "https://ideas.trustroots.org/")).path.rstrip("/")

    def test_all_local_image_references_resolve_to_images(self):
        references = set()
        for page in self.generated.rglob("*.html"):
            for source in Images(page.read_text()).sources:
                url = urlsplit(source)
                if url.netloc:
                    continue
                with self.subTest(page=page, image=source):
                    self.assertTrue(source, "Empty image URL")
                    if url.path.startswith("/"):
                        self.assertTrue(url.path.startswith(self.prefix + "/"))
                        path = self.generated / unquote(url.path[len(self.prefix):]).lstrip("/")
                    else:
                        path = page.parent / unquote(url.path)
                    self.assertTrue(path.is_file(), "Missing local image: " + source)
                    head = path.read_bytes()[:1024]
                    self.assertTrue(
                        head.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a"))
                        or (head.startswith(b"RIFF") and head[8:12] == b"WEBP")
                        or b"<svg" in head,
                        "Local image URL points to a non-image file: " + source,
                    )
                    references.add(source)
        self.assertGreater(len(references), 200, "Expected the complete post image collection")

    def test_restored_images_are_published_in_their_original_posts(self):
        manifest = json.loads((self.root / "data/recovered-images.json").read_text())
        self.assertEqual(len(manifest), 22)
        self.assertEqual(len({record["path"] for record in manifest}), 22)
        for record in manifest:
            with self.subTest(image=record["path"]):
                data = (self.root / "static" / record["path"].lstrip("/")).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                page = self.generated / record["post_url"].strip("/") / "index.html"
                sources = Images(page.read_text()).sources
                self.assertIn(self.prefix + record["path"], sources)


if __name__ == "__main__":
    unittest.main()
