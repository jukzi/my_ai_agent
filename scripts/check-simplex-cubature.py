"""Check positive interior simplex rules: one row of barycentric coordinates and a mean weight per node."""
import argparse
from collections import Counter
from itertools import permutations
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
    parser.add_argument('--symmetric', action='store_true',
                        help='verify exact permutation symmetry and check one moment per orbit')
    parser.add_argument('--cartesian', action='store_true',
                        help='read d reference-simplex coordinates and append the missing barycentric coordinate')
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
            if args.cartesian:
                if len(row) != d + 1:
                    raise ValueError(f'line {i}: expected {d} Cartesian coordinates and a weight')
                coords, weight = row[:-1], row[-1]
                row = (*coords, 1 - sum(coords), weight)
            if len(row) != d + 2 or min(row) <= 0 or abs(sum(row[:-1])-1) > tol:
                raise ValueError(f'line {i}: expected positive barycentric coordinates summing to one and a positive weight')
            rows.append(row)
        if not rows:
            raise ValueError('empty table')
        if args.symmetric:
            counts = Counter(rows)
            for row, count in counts.items():
                if any(counts[point + (row[-1],)] != count
                       for point in set(permutations(row[:-1]))):
                    raise ValueError('table is not invariant under barycentric permutations')
    except (OSError, ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    worst = (Fraction(0), (0,) * (d + 1))
    degrees = (args.degree,) if args.homogeneous else range(args.degree + 1)
    factorials = [factorial(k) for k in range(d + args.degree + 1)]
    # Reuse the same coordinate powers across all barycentric monomials.
    powers = [(row[-1], [tuple(x**k for k in range(args.degree + 1))
                         for x in row[:-1]]) for row in rows]
    for degree in degrees:
        for ex in indices(d + 1, degree):
            if args.symmetric and ex != tuple(sorted(ex)):
                continue
            target = Fraction(factorials[d]*prod(factorials[k] for k in ex), factorials[d+degree])
            estimate = sum(weight*prod(axis[k] for axis, k in zip(axes, ex))
                           for weight, axes in powers)
            worst = max(worst, (abs(estimate-target), ex))
    print(f'{len(rows)} Stützstellen; Gewichtssumme: {sum(row[-1] for row in rows)}')
    print(f'Größter absoluter Momentrest: {worst[0]}; Exponenten: {worst[1]}')
    return int(worst[0] > tol)


if __name__ == '__main__':
    raise SystemExit(main())
