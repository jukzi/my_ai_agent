"""Reproduce the angular allocation counterexample with exact fractions."""
import argparse
from fractions import Fraction as F


def optimal_allocation(bounds, budget):
    """Return (bound, counts), with at least one point per ring."""
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
    return best[budget]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Minimize the sum of angular error bounds.')
    parser.add_argument('--budget', type=int, default=13)
    parser.add_argument('--ring', action='append', nargs='+', metavar='A:p',
                        help='one ring; list alternatives A:p for min(A/n**p); A may be a fraction')
    parser.add_argument('--target', metavar='EPS',
                        help='find the smallest budget up to --budget with bound <= EPS')
    args = parser.parse_args(argv)
    bounds = [lambda n: min(F(1, n**2), F(11**18, n**20)),
              lambda n: F(2, 375*n**2)]
    try:
        if args.ring:
            bounds = []
            for ring in args.ring:
                terms = []
                for spec in ring:
                    a, p = spec.split(':')
                    coefficient, exponent = F(a), int(p)
                    if coefficient < 0 or exponent <= 0:
                        raise ValueError('A must be nonnegative and p a positive integer')
                    terms.append((coefficient, exponent))
                bounds.append(lambda n, terms=terms: min(a / n**p for a, p in terms))
        value, counts = optimal_allocation(bounds, args.budget)
        if args.target is not None:
            target = F(args.target)
            if target < 0:
                raise ValueError('target must be nonnegative')
            if value > target:
                print('Keine Aufteilung erreicht die Zielschranke im Budget.')
                return 1
            lo, hi = len(bounds), args.budget
            # Each supplied bound is nonincreasing in the point count.
            while lo < hi:
                mid = (lo + hi) // 2
                if optimal_allocation(bounds, mid)[0] <= target:
                    hi = mid
                else:
                    lo = mid + 1
            value, counts = optimal_allocation(bounds, lo)
            print(f'Kleinstes Budget: {lo}')
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    print(f'Optimale Aufteilung: {counts}; Schranke: {value} ≈ {float(value):.8f}')
    if args.target is not None or args.ring or args.budget != 13:
        return
    greedy = bounds[0](11) + bounds[1](2)
    print(f'Vergleich 11:2: {greedy} ≈ {float(greedy):.8f}')


if __name__ == '__main__':
    raise SystemExit(main())
