"""Exact regression checks for the unit-ball reproducing kernel."""
import io
import runpy
import sys
from contextlib import redirect_stderr, redirect_stdout
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path

kernel = runpy.run_path(str(Path(__file__).with_name('check-ball-ten-nodes.py')))['kernel']


def moment(e):
    if any(k % 2 for k in e):
        return F(0)
    return F(3 * prod(prod(range(k - 1, 0, -2)) for k in e),
             prod(range(sum(e) + 3, 0, -2)))


class BallKernelTest(unittest.TestCase):
    def test_reproduces_quadratics(self):
        # Each test interpolates K(u,x) as a polynomial in x by finite differences.
        zero = (0, 0, 0)  # Also used as the constant term's exponent tuple.
        axes = [tuple(int(i == j) for i in range(3)) for j in range(3)]
        add = lambda a, b: tuple(x + y for x, y in zip(a, b))
        for u in [zero, *axes, (F(1, 5), F(-2, 7), F(1, 3))]:
            constant = kernel(u, zero)
            terms = {zero: constant}
            for e in axes:
                plus, minus = kernel(u, e), kernel(u, tuple(-x for x in e))
                terms[e] = (plus - minus) / 2
                terms[add(e, e)] = (plus + minus) / 2 - constant
            for i, e in enumerate(axes):
                for f in axes[i + 1:]:
                    terms[add(e, f)] = kernel(u, add(e, f)) - kernel(u, e) - kernel(u, f) + constant
            for e in product(range(3), repeat=3):
                if sum(e) <= 2:
                    self.assertEqual(sum(c * moment(add(e, k)) for k, c in terms.items()),
                                     prod(x**j for x, j in zip(u, e)), (u, e))

    def test_diagonal(self):
        for r in (F(0), F(1, 2), F(1)):
            u = (r, F(0), F(0))
            self.assertEqual(kernel(u, u), F(100, 21) + F(105, 4)*(r*r-F(5, 21))**2)


class BallCheckerCliTest(unittest.TestCase):
    def check(self, text):
        checker = Path(__file__).with_name('check-ball-ten-nodes.py')
        with TemporaryDirectory() as directory:
            table = Path(directory) / 'nodes.txt'
            table.write_text(text)
            out, err = io.StringIO(), io.StringIO()
            with patch.object(sys, 'argv', [str(checker), str(table)]), redirect_stdout(out), redirect_stderr(err):
                with self.assertRaises(SystemExit) as result:
                    runpy.run_path(str(checker), run_name='__main__')
        return result.exception.code, out.getvalue(), err.getvalue()

    def test_inexact_nodes_report_exact_pair_residual(self):
        status, out, _ = self.check(''.join(f'{i}/10 0 0\n' for i in range(10)))
        self.assertEqual(status, 1)
        self.assertIn('K(1, 2) = 493/80', out)

    def test_invalid_nodes(self):
        distinct = ''.join(f'{i}/10 0 0\n' for i in range(9))
        for text, diagnosis in [('0 0 0\n' * 10, 'ten distinct triples'),
                                (distinct + '11/10 0 0\n', 'outside the unit ball')]:
            with self.subTest(diagnosis=diagnosis):
                status, _, err = self.check(text)
                self.assertEqual(status, 2)
                self.assertIn(diagnosis, err)


if __name__ == '__main__':
    unittest.main()
