"""Reproduce the seven-point orientation comparison using exact arithmetic."""
from fractions import Fraction as F


def optimal_variances(weights, limit):
    """Yield (budget, variance coefficient) for optimal integer allocations."""
    counts = [1] * len(weights)
    squares = [w * w for w in weights]
    for budget in range(len(weights), limit + 1):
        yield budget, sum(s / k for s, k in zip(squares, counts))
        # Each point offers a decreasing sequence of marginal gains.
        i = max(range(len(weights)),
                key=lambda i: squares[i] / (counts[i] * (counts[i] + 1)))
        counts[i] += 1


def optimal_variances_dp(weights, limit):
    """Independently minimize over all splits into positive measurement counts."""
    best = {0: F(0)}
    for weight in weights:
        square = weight**2
        costs = [F(0)] + [square / k for k in range(1, limit + 1)]
        best = {
            budget: min(previous + costs[budget - used]
                        for used, previous in best.items() if used < budget)
            for budget in range(min(best) + 1, limit + 1)
        }
    return best


def main():
    single = [F(2, 7)] + [F(5, 36)] * 4 + [F(5, 63)] * 2
    direct = [F(2, 7)] + [F(5, 72)] * 8 + [F(5, 126)] * 4
    sigma2 = F(1, 50)**2
    choice = F(1, 2160)**2
    assert sum(single) == sum(direct) == 1
    # Start when every floor(N*w) is positive. Proportional rounding
    # bounds the excess above sigma²/N by this decreasing sum.
    smallest = min(direct)
    cutoff = (smallest.denominator + smallest.numerator - 1) // smallest.numerator
    while sigma2 * sum(F(1, cutoff**2 * int(cutoff * w)) for w in direct) >= choice:
        cutoff += 1
    a = dict(optimal_variances(single, cutoff - 1))
    b = dict(optimal_variances(direct, cutoff - 1))
    assert a == optimal_variances_dp(single, cutoff - 1)
    assert b == optimal_variances_dp(direct, cutoff - 1)
    delta = {n: choice + sigma2 * (a[n] - b[n]) for n in b}
    wins = [n for n, d in delta.items() if d < 0]
    ties = [n for n, d in delta.items() if d == 0]
    assert cutoff == 76 and not ties
    print('Analytische Garantie ab:', cutoff)
    assert wins == [*range(13, 17), *range(18, 26), *range(32, 41)]
    print('Losentscheid besser:', ', '.join(map(str, wins)))
    print('Direktes Mittel dauerhaft besser ab:', max(wins + ties) + 1)


if __name__ == '__main__':
    main()
