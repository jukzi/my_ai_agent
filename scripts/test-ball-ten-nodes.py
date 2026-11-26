"""Exact regression checks for the unit-ball reproducing kernel."""
import runpy
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


if __name__ == '__main__':
    unittest.main()
