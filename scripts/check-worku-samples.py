#!/usr/bin/env python3
"""Reproduce selected moment checks, not a full exactness test."""
import math
from urllib.request import urlopen

BASE = ('https://raw.githubusercontent.com/OptimalDesignLab/SummationByParts.jl/'
        '9d2a6e7aa8a34d18e568a60052870307ac9d6321/pi_quadrature_data/')


def check(path, count, powers, *, full_degree=None):
    with urlopen(BASE + path, timeout=30) as response:
        lines = response.read().decode('ascii').splitlines()
    dim = len(powers)
    if lines[3].split() != list('xyz'[:dim]) + ['w']:
        raise ValueError(f'{path}: unexpected column header')
    rows = [list(map(float, line.split())) for line in lines[4:] if line.strip()]
    if len(rows) != count or any(len(row) != dim + 1 for row in rows):
        raise ValueError(f'{path}: unexpected table dimensions')
    if full_degree is not None:
        from itertools import product
        scaled = [tuple((x + 1) / 2 for x in row[:-1]) + (row[-1] / 2**dim,) for row in rows]
        if not all(row[-1] > 0 and min(row[:-1]) > 0 and sum(row[:-1]) < 1 for row in scaled):
            raise ValueError(f'{path}: expected positive weights and interior nodes')
        errors = []
        for ex in product(range(full_degree + 1), repeat=dim):
            if sum(ex) <= full_degree:
                value = math.fsum(row[-1] * math.prod(x**a for x, a in zip(row[:-1], ex)) for row in scaled)
                exact = math.prod(map(math.factorial, ex)) / math.factorial(sum(ex) + dim)
                errors.append(abs(value - exact))
        print(f'{path}: {len(errors)} moments, maximum absolute error {max(errors):.3g}')
        return max(errors) < 1e-15
    value = math.fsum(row[-1] / 2**dim * math.prod(
        ((x + 1) / 2)**a for x, a in zip(row[:-1], powers)) for row in rows)
    exact = math.prod(map(math.factorial, powers)) / math.factorial(sum(powers) + dim)
    error = abs(value / exact - 1)
    print(f'{path}: relative error {error:.3g}')
    return error < 1e-12


if __name__ == '__main__':
    results = [check('tri/expanded/tri_q4_n6_ext.dat', 6, (0, 0), full_degree=4),
               check('tet/expanded/tet_q4_n14_ext.dat', 14, (0, 0, 0), full_degree=4),
               check('tri/expanded/tri_q84_n1261_ext.dat', 1261, (42, 42)),
               check('tri/expanded/tri_q40_n292_ext.dat', 292, (20, 20)),
               check('tet/expanded/tet_q40_n3815_ext.dat', 3815, (14, 13, 13))]
    raise SystemExit(0 if all(results) else 1)
