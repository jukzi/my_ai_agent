"""Exact test for ten rational nodes of a degree-four unit-ball rule."""
import argparse
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path


def dot(u, v):
    return sum(x*y for x, y in zip(u, v))


def kernel(u, v):
    a, b, t = dot(u, u), dot(v, v), dot(u, v)
    return 1 + 5*t + F(175, 12)*(a-F(3, 5))*(b-F(3, 5)) + F(35, 2)*(t*t-a*b/3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('table', type=Path, help='one x y z triple per line; fractions allowed')
    args = parser.parse_args()
    try:
        nodes = [tuple(map(F, line.split())) for line in args.table.read_text().splitlines() if line.strip()]
    except (OSError, ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    if len(nodes) != 10 or any(len(u) != 3 for u in nodes) or len(set(nodes)) != 10:
        parser.error('expected ten distinct triples')
    if any(dot(u, u) > 1 for u in nodes):
        parser.error('node outside the unit ball')
    for (i, u), (j, v) in combinations(enumerate(nodes, 1), 2):
        value = kernel(u, v)
        if value:
            print(f'Not exact: K({i}, {j}) = {value}')
            return 1
    print('Exact; weights for the volume mean:')
    for u in nodes:
        print(1/kernel(u, u))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
