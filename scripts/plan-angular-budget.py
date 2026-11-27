"""Reproduce the angular allocation counterexample with exact fractions."""
import argparse
from fractions import Fraction as F


def allocation_table(bounds, budget):
    """Return optimal (bound, counts) for every feasible budget up to budget."""
    if not bounds or budget < len(bounds):
        raise ValueError('need at least one point per ring')
    best = {0: (F(0), ())}
    for i, bound in enumerate(bounds, 1):
        costs = {n: bound(n) for n in range(1, budget - len(bounds) + 2)}
        best = {
            b: min((value + costs[b - used], counts + (b - used,))
                   for used, (value, counts) in best.items() if used < b)
            for b in range(i, budget - len(bounds) + i + 1)
        }
    return best


def optimal_allocation(bounds, budget):
    return allocation_table(bounds, budget)[budget]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Minimize the sum of angular error bounds.')
    parser.add_argument('--budget', type=int, default=13)
    parser.add_argument('--ring', action='append', nargs='+', metavar='BOUND',
                        help='one ring; alternatives A:p for A/n**p or C@r for C*r**n/(1-r**n)')
    parser.add_argument('--target', metavar='EPS',
                        help='find the smallest budget up to --budget with bound <= EPS')
    parser.add_argument('--radial-bound', default='0',
                        help='fixed radial error bound added to the angular bound')
    parser.add_argument('--details', action='store_true',
                        help='show the weighted angular contribution of each ring')
    args = parser.parse_args(argv)
    bounds = [lambda n: min(F(1, n**2), F(11**18, n**20)),
              lambda n: F(2, 375*n**2)]
    try:
        if args.ring:
            bounds = []
            for ring in args.ring:
                terms = []
                for spec in ring:
                    if '@' in spec:
                        c, r = map(F, spec.split('@'))
                        if c < 0 or not 0 < r < 1:
                            raise ValueError('C must be nonnegative and 0 < r < 1')
                        terms.append(lambda n, c=c, r=r: c*r**n / (1-r**n))
                        continue
                    a, p = spec.split(':')
                    coefficient, exponent = F(a), int(p)
                    if coefficient < 0 or exponent <= 0:
                        raise ValueError('A must be nonnegative and p a positive integer')
                    terms.append(lambda n, a=coefficient, p=exponent: a / n**p)
                bounds.append(lambda n, terms=terms: min(term(n) for term in terms))
        radial = F(args.radial_bound)
        if radial < 0:
            raise ValueError('radial bound must be nonnegative')
        table = allocation_table(bounds, args.budget)
        value, counts = table[args.budget]
        if args.target is not None:
            target = F(args.target)
            if target < 0:
                raise ValueError('target must be nonnegative')
            target -= radial
            if value > target:
                print('Keine Aufteilung erreicht die Zielschranke im Budget.')
                return 1
            lo, hi = len(bounds), args.budget
            # Each supplied bound is nonincreasing in the point count.
            while lo < hi:
                mid = (lo + hi) // 2
                if table[mid][0] <= target:
                    hi = mid
                else:
                    lo = mid + 1
            value, counts = table[lo]
            print(f'Kleinstes Budget: {lo}')
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    print(f'Optimale Aufteilung: {counts}; Schranke: {value} ≈ {float(value):.8f}')
    if args.details:
        for i, (bound, count) in enumerate(zip(bounds, counts), 1):
            print(f'Kreislinie {i}: {count} Punkte; Winkelschranke: {bound(count)}')
    if radial:
        print(f'Gesamtschranke (Winkel + Radius): {value + radial}')
    if args.target is not None or args.ring or radial or args.budget != 13:
        return
    greedy = bounds[0](11) + bounds[1](2)
    print(f'Vergleich 11:2: {greedy} ≈ {float(greedy):.8f}')


if __name__ == '__main__':
    raise SystemExit(main())
