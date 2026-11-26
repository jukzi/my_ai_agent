"""Check a Lebedev angle table (degrees, weights summing to one)."""
import argparse
from fractions import Fraction
from math import cos, sin, radians, prod, fsum, isfinite
from pathlib import Path


def moment(i, j, k):
    if (i | j | k) & 1:
        return Fraction(0)
    def odd_product(n):
        return prod(range(n, 0, -2))
    return Fraction(prod(odd_product(e - 1) for e in (i, j, k)),
                    odd_product(i + j + k + 1))


def worst_error(nodes, degree):
    return max((abs(fsum(w*x**i*y**j*z**k for x,y,z,w in nodes)
                    - float(moment(i,j,k))), (i,j,k))
               for i in range(degree+1) for j in range(degree-i+1)
               for k in range(degree-i-j+1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('table', type=Path)
    parser.add_argument('degree', type=int)
    parser.add_argument('--tol', type=float, default=1e-12)
    args = parser.parse_args()
    if args.degree < 0 or not isfinite(args.tol) or args.tol <= 0:
        parser.error('degree must be nonnegative and tolerance positive and finite')
    nodes = []
    for number, line in enumerate(args.table.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            az, polar, w = map(float, line.split())
            if not (-180 <= az <= 180 and 0 <= polar <= 180 and isfinite(w)):
                raise ValueError('angle out of range or non-finite weight')
        except ValueError as exc:
            parser.error(f'line {number}: {exc}')
        a, p = radians(az), radians(polar)
        nodes.append((cos(a)*sin(p), sin(a)*sin(p), cos(p), w))
    if not nodes:
        parser.error('table is empty')
    error, exponents = worst_error(nodes, args.degree)
    print(f'{len(nodes)} rows; weight sum {fsum(row[3] for row in nodes):.16g}')
    print(f'Maximum moment residual: {error:.6g}, exponents {exponents}')
    return int(error > args.tol)


if __name__ == '__main__':
    raise SystemExit(main())
