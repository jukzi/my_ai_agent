"""Reproduce the angular allocation counterexample with exact fractions."""
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


def main():
    bounds = [lambda n: min(F(1, n**2), F(11**18, n**20)),
              lambda n: F(2, 375*n**2)]
    value, counts = optimal_allocation(bounds, 13)
    print(f'Optimale Aufteilung: {counts}; Schranke: {value} ≈ {float(value):.8f}')
    greedy = bounds[0](11) + bounds[1](2)
    print(f'Vergleich 11:2: {greedy} ≈ {float(greedy):.8f}')


if __name__ == '__main__':
    main()
