"""Offline regression tests for the barycentric moment checker."""
import io
import runpy
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

main = runpy.run_path(str(Path(__file__).with_name('check-simplex-cubature.py')))['main']


class SimplexCheckerTest(unittest.TestCase):
    def check(self, text, dimension, degree, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rule.txt'
            path.write_text(text)
            return main([str(path), str(dimension), str(degree), *options])

    def test_triangle_exact_degree(self):
        table = '2/3 1/6 1/6 1/3\n1/6 2/3 1/6 1/3\n1/6 1/6 2/3 1/3\n'
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(self.check(table, 2, 2), 0)
            self.assertEqual(self.check(table, 2, 3), 1)
        self.assertIn('Momentrest: 1/540', out.getvalue())

    def test_tetrahedron_centroid(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(self.check('1/4 1/4 1/4 1/4 1\n', 3, 1), 0)
            self.assertEqual(self.check('1/4 1/4 1/4 1/4 1\n', 3, 2), 1)

    def test_tolerance_and_boundary(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(self.check('1/3 1/3 1/3 99/100\n', 2, 0, '--tol', '1/100'), 0)
            self.assertEqual(self.check('1/3 1/3 1/3 99/100\n', 2, 0), 1)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.check('0 1/2 1/2 1\n', 2, 0, '--tol', '1/100')
        self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
