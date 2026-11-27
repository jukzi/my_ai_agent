"""Check positive interior simplex rules: one row of barycentric coordinates and a mean weight per node."""
import argparse
from fractions import Fraction
from math import factorial, prod
from pathlib import Path


def indices(length, degree):
    if length == 1:
        yield (degree,)
    else:
        for first in range(degree + 1):
            for rest in indices(length - 1, degree - first):
                yield (first, *rest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('table', type=Path)
    parser.add_argument('dimension', type=int, choices=(2, 3))
    parser.add_argument('degree', type=int)
    parser.add_argument('--tol', default='0', help='absolute residual tolerance (default: exact)')
    parser.add_argument('--homogeneous', action='store_true',
                        help='check only top-degree moments (exact mode only)')
    args = parser.parse_args(argv)
    d = args.dimension
    try:
        tol = Fraction(args.tol)
        if tol < 0 or args.degree < 0:
            raise ValueError('degree and tolerance must be nonnegative')
        if args.homogeneous and tol:
            raise ValueError('--homogeneous requires zero tolerance')
        rows = []
        for i, line in enumerate(args.table.read_text().splitlines(), 1):
            if not line.strip():
                continue
            row = tuple(map(Fraction, line.split()))
            if len(row) != d + 2 or min(row) <= 0 or abs(sum(row[:-1])-1) > tol:
                raise ValueError(f'line {i}: expected positive barycentric coordinates summing to one and a positive weight')
            rows.append(row)
        if not rows:
            raise ValueError('empty table')
    except (OSError, ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    worst = (Fraction(0), (0,) * (d + 1))
    degrees = (args.degree,) if args.homogeneous else range(args.degree + 1)
    for degree in degrees:
        for ex in indices(d + 1, degree):
            target = Fraction(factorial(d)*prod(map(factorial, ex)), factorial(d+degree))
            estimate = sum(row[-1]*prod(x**k for x, k in zip(row[:-1], ex)) for row in rows)
            worst = max(worst, (abs(estimate-target), ex))
    print(f'{len(rows)} Stützstellen; Gewichtssumme: {sum(row[-1] for row in rows)}')
    print(f'Größter absoluter Momentrest: {worst[0]}; Exponenten: {worst[1]}')
    return int(worst[0] > tol)


if __name__ == '__main__':
    raise SystemExit(main())
