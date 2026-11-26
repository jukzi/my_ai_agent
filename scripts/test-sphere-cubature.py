"""Regression test for the Lebedev checker; no network or extra packages."""
import subprocess
import sys
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
            return subprocess.run([sys.executable, str(CHECKER), str(path), str(degree)],
                                  capture_output=True, text=True)

    def test_published_rule(self):
        for degree, status in [(3, 0), (4, 1)]:
            with self.subTest(degree=degree):
                result = self.check_table(TABLE, degree)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn('Maximum moment residual:', result.stdout)

    def test_wrong_normalization(self):
        self.assertEqual(self.check_table(TABLE.replace('0.166666666666667', '0.1'), 0).returncode, 1)

    def test_invalid_angle(self):
        result = self.check_table(TABLE + '0 181 0.1\n', 3)
        self.assertEqual(result.returncode, 2)
        self.assertIn('line 7:', result.stderr)


if __name__ == '__main__':
    unittest.main()
