"""Verify angular budget allocation against exhaustive search."""
import runpy
import unittest
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

allocate = runpy.run_path(str(Path(__file__).with_name('plan-angular-budget.py')))['optimal_allocation']


class AllocationTest(unittest.TestCase):
    def test_custom_cli(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO

        main = runpy.run_path(str(Path(__file__).with_name('plan-angular-budget.py')))['main']
        output = StringIO()
        with redirect_stdout(output):
            main(['--budget', '12', '--ring', '1:2', '10:4', '--ring', '1:4'])
        self.assertIn('(7, 5); Schranke: 8651/1500625', output.getvalue())
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
            main(['--ring', '1:0'])
        self.assertEqual(error.exception.code, 2)

    def test_target_cli(self):
        from contextlib import redirect_stdout
        from io import StringIO

        main = runpy.run_path(str(Path(__file__).with_name('plan-angular-budget.py')))['main']
        output = StringIO()
        with redirect_stdout(output):
            main(['--budget', '20', '--ring', '1:2', '--target', '1/16'])
            self.assertEqual(main(['--budget', '3', '--ring', '1:2', '--target', '1/16']), 1)
        self.assertIn('Kleinstes Budget: 4', output.getvalue())
        self.assertIn('Keine Aufteilung', output.getvalue())

    def test_switch_between_bounds(self):
        bounds = [lambda n: min(F(1, n**2), F(11**18, n**20)),
                  lambda n: F(2, 375*n**2)]
        self.assertEqual(allocate(bounds, 13),
                         (bounds[0](12) + bounds[1](1), (12, 1)))

    def test_against_exhaustive_search(self):
        all_bounds = [lambda n: F(1, n**2), lambda n: F(2, n**4),
                      lambda n: min(F(1, n**2), F(11**18, n**20))]
        for rings in range(1, 4):
            bounds = all_bounds[:rings]
            for budget in range(rings, 16):
                with self.subTest(rings=rings, budget=budget):
                    options = (tuple(y-x for x, y in zip((0, *cuts), (*cuts, budget)))
                               for cuts in combinations(range(1, budget), rings-1))
                    expected = min((sum(f(n) for f, n in zip(bounds, counts)), counts)
                                   for counts in options)
                    self.assertEqual(allocate(bounds, budget), expected)

    def test_table_covers_every_feasible_budget(self):
        table = allocate.__globals__['allocation_table']
        bounds = [lambda n: F(1, n**2), lambda n: F(2, n**4)]
        expected = {b: min((bounds[0](n) + bounds[1](b-n), (n, b-n))
                           for n in range(1, b)) for b in range(2, 16)}
        self.assertEqual(table(bounds, 15), expected)

    def test_invalid_budget(self):
        with self.assertRaises(ValueError):
            allocate([lambda n: F(1, n)] * 2, 1)


if __name__ == '__main__':
    unittest.main()
