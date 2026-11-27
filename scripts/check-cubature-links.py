#!/usr/bin/env python3
"""Check local HTML links in the cubature chapters (no network needed)."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = "index fehler quadrat gauss dreieck tetraeder dreieck-tetraeder kreis kreisring wuerfel viele-dimensionen messungen quellen".split()


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = Counter()
        self.links = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "a" and attrs.get("href"):
            self.links.append((self.getpos()[0], attrs["href"]))


def main():
    pages = {ROOT / (name + ".html"): Page(ROOT / (name + ".html")) for name in CHAPTERS}
    errors = []
    checked = 0
    for path, page in pages.copy().items():
        for line, href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.suffix != ".html":
                continue
            checked += 1
            if not target.is_file():
                errors.append(f"{path.name}:{line}: missing file: {href}")
            elif url.fragment:
                if target not in pages:
                    pages[target] = Page(target)
                count = pages[target].ids[unquote(url.fragment)]
                if count != 1:
                    errors.append(f"{path.name}:{line}: {count} matching IDs: {href}")
    for error in errors:
        print(error)
    print(f"{checked} local HTML links checked; {len(errors)} errors.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
