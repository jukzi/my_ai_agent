"""Regression test for the chapter link checker."""
import contextlib
import io
from pathlib import Path
import runpy
import tempfile
import unittest


class LinkCheckTest(unittest.TestCase):
    def test_encoded_cross_page_fragment(self):
        check = runpy.run_path(str(Path(__file__).with_name("check-cubature-links.py")))["main"]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            check.__globals__.update(ROOT=root, CHAPTERS=["index"])
            (root / "index.html").write_text(
                '<a href="mess%20werte.html#gew%C3%B6hnlich">Zum Beispiel</a>'
                '<a href="https://example.org/fehlt.html#fehlt">Extern</a>',
                encoding="utf-8",
            )
            (root / "mess werte.html").write_text('<h2 id="gewöhnlich">Beispiel</h2>', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertFalse(check())
            self.assertIn("1 local HTML links checked; 0 errors.", output.getvalue())

    def test_split_simplex_chapters_are_checked(self):
        check = runpy.run_path(str(Path(__file__).with_name("check-cubature-links.py")))["main"]
        self.assertIn("dreieck", check.__globals__["CHAPTERS"])
        self.assertIn("tetraeder", check.__globals__["CHAPTERS"])

    def test_local_links(self):
        check = runpy.run_path(str(Path(__file__).with_name("check-cubature-links.py")))["main"]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            check.__globals__.update(ROOT=root, CHAPTERS=["index"])
            page = root / "index.html"
            page.write_text('<h1 id="eindeutig">Titel</h1><a href="#eindeutig">OK</a>')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(check())
            with page.open("a") as stream:
                stream.write('<h2 id="eindeutig">Doppelt</h2><a href="#fehlt">Fehlt</a>'
                             '<a href="fehlt.html">Datei fehlt</a>')
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertTrue(check())
            for message in ("2 matching IDs: #eindeutig", "0 matching IDs: #fehlt",
                            "missing file: fehlt.html"):
                self.assertIn(message, output.getvalue())


if __name__ == "__main__":
    unittest.main()
