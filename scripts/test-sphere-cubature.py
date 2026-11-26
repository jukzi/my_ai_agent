"""Regression test for the Lebedev checker; no network or extra packages."""
import io
import runpy
import sys
from contextlib import redirect_stdout, redirect_stderr
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name('check-sphere-cubature.py')
# Published lebedev_003.txt, John Burkardt's Lebedev data collection:
# https://people.sc.fsu.edu/~jburkardt/datasets/sphere_lebedev_rule/lebedev_003.txt
TABLE = '''0 90 0.166666666666667
180 90 0.166666666666667
90 90 0.166666666666667
-90 90 0.166666666666667
90 0 0.166666666666667
90 180 0.166666666666667
'''


class SphereCheckerTest(unittest.TestCase):
    def check_table(self, text, degree):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rule.txt'
            path.write_text(text)
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(sys, 'argv', [str(CHECKER), str(path), str(degree)]), \
                    redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exit_info:
                    runpy.run_path(str(CHECKER), run_name='__main__')
            return SimpleNamespace(returncode=exit_info.exception.code,
                                   stdout=stdout.getvalue(), stderr=stderr.getvalue())

    def test_published_rule(self):
        for degree, status in [(3, 0), (4, 1)]:
            with self.subTest(degree=degree):
                result = self.check_table(TABLE, degree)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn('Maximum moment residual:', result.stdout)

    def test_published_weighted_rule(self):
        # https://people.sc.fsu.edu/~jburkardt/datasets/sphere_lebedev_rule/lebedev_005.txt
        axes = TABLE.replace('0.166666666666667', '0.066666666666667')
        corners = ''.join(f'{az} {polar} 0.075\n'
                          for az in (45, -45, 135, -135)
                          for polar in ('54.735610317245346', '125.264389682754654'))
        for degree, status in [(5, 0), (6, 1)]:
            with self.subTest(degree=degree):
                result = self.check_table(axes + corners, degree)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn('14 rows;', result.stdout)

    def test_wrong_normalization(self):
        self.assertEqual(self.check_table(TABLE.replace('0.166666666666667', '0.1'), 0).returncode, 1)

    def test_invalid_angle(self):
        result = self.check_table(TABLE + '0 181 0.1\n', 3)
        self.assertEqual(result.returncode, 2)
        self.assertIn('line 7:', result.stderr)


if __name__ == '__main__':
    unittest.main()
