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


def main():
    single = [F(2, 7)] + [F(5, 36)] * 4 + [F(5, 63)] * 2
    direct = [F(2, 7)] + [F(5, 72)] * 8 + [F(5, 126)] * 4
    sigma2 = F(1, 50)**2
    choice = F(1, 2160)**2
    assert sum(single) == sum(direct) == 1
    # This upper bound on the direct plan's excess measurement variance
    # decreases for every subsequent budget.
    cutoff = len(direct) + 1
    while len(direct) * sigma2 / (cutoff * (cutoff - len(direct))) >= choice:
        cutoff += 1
    a = dict(optimal_variances(single, cutoff - 1))
    b = dict(optimal_variances(direct, cutoff - 1))
    delta = {n: choice + sigma2 * (a[n] - b[n]) for n in b}
    wins = [n for n, d in delta.items() if d < 0]
    ties = [n for n, d in delta.items() if d == 0]
    assert cutoff == 163 and not ties
    assert wins == [*range(13, 17), *range(18, 26), *range(32, 41)]
    print('Losentscheid besser:', ', '.join(map(str, wins)))
    print('Direktes Mittel dauerhaft besser ab:', max(wins + ties) + 1)


if __name__ == '__main__':
    main()
