"""Smoke-test generated HTML or the deployed site using only Python's stdlib."""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.images = []
        self.links = []
        self.words = []
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "img":
            self.images.append(attrs)
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])

    def handle_data(self, data):
        self.words.append(data)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check(args):
    base = args.base_url.rstrip("/") + "/"
    prefix = urlsplit(base).path

    def read(relative):
        if args.live:
            url = urljoin(base, relative) + "?revision=" + args.revision
            with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=20) as response:
                return response.read()
        return (Path(args.directory) / relative).read_bytes()

    if args.revision:
        require(read("revision.txt").decode().strip() == args.revision,
                "Published revision differs from the requested commit")
    page = Page(read("comparison-of-hospitality-exchange-platforms/index.html").decode())
    text = " ".join(page.words)
    for expected in ("Couchers", "Servas", "Workaway", "WWOOF", "HelpX",
                     "Worldpackers", "Price", "Federation", "Nostr"):
        require(expected in text, "Comparison content missing: " + expected)
    require("24 May 2020" not in text, "Historical comparison was published instead of the update")
    require("{{<" not in text, "Unrendered Hugo shortcode")
    counts = Counter(image.get("src") for image in page.images)
    for filename, alt in (("trustroots-symbol.svg", "Trustroots logo"),
                          ("bewelcome.svg", "BeWelcome logo"),
                          ("couchers.png", "Couchers.org logo")):
        src = prefix + "brand/" + filename
        require(counts[src] == 2, "Logo missing from a comparison table: " + filename)
        require(all(image.get("alt") == alt for image in page.images if image.get("src") == src),
                "Missing accessible logo label: " + filename)
        data = read("brand/" + filename)
        require(data.startswith(b"\x89PNG\r\n\x1a\n") if filename.endswith(".png") else b"<svg" in data,
                "Logo URL does not return an image: " + filename)
    post = "2025/11/08/keep-trustroots-free-forever-ever/"
    require(prefix + post in page.links, "Nostr context link is not internal or has the wrong base path")
    require(b"<html" in read(post + "index.html"), "Internal post link is broken")
    require(prefix + "comparison-of-hospitality-exchange-platforms/" in page.links,
            "Attribution link is not internal")
    for link in page.links:
        host = (urlsplit(link).hostname or "").lower()
        require(not any(host == domain or host.endswith("." + domain)
                        for domain in ("couchsurfing.com", "hospitalityclub.org")),
                "Unwanted outbound comparison link: " + link)
    require(ET.fromstring(read("index.xml")).tag == "rss", "RSS feed is invalid")
    print("PASS: revision, comparison content, six logos, internal links and RSS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--directory")
    source.add_argument("--live", action="store_true")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--revision", default="")
    parser.add_argument("--attempts", type=int, default=1)
    args = parser.parse_args()
    for attempt in range(args.attempts):
        try:
            check(args)
            break
        except (AssertionError, OSError, ET.ParseError) as error:
            if attempt + 1 == args.attempts:
                raise SystemExit(str(error))
            print(f"Waiting for Pages propagation ({attempt + 1}/{args.attempts}): {error}", flush=True)
            time.sleep(10)
