"""Offline tests for the published-table sample checker."""
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


class SampleCheckTest(unittest.TestCase):
    def setUp(self):
        self.check = runpy.run_path(str(Path(__file__).with_name(
            "check-worku-samples.py")))["check"]

    def check_table(self, table, **options):
        with patch.dict(self.check.__globals__, urlopen=lambda *a, **kw:
                        BytesIO(("metadata\nmetadata\n\n" + table).encode("ascii"))):
            with redirect_stdout(StringIO()):
                return self.check("fixture.dat", 1, (1, 0), **options)

    def test_centroid_integrates_linear_moment(self):
        self.assertTrue(self.check_table("x y w\n-0.3333333333333333 -0.3333333333333333 2\n"))

    def test_rejects_incorrect_moment(self):
        self.assertFalse(self.check_table("x y w\n0 -0.5 2\n"))

    def test_full_check_distinguishes_linear_and_quadratic_exactness(self):
        centroid = "x y w\n-0.3333333333333333 -0.3333333333333333 2\n"
        self.assertTrue(self.check_table(centroid, full_degree=1))
        self.assertFalse(self.check_table(centroid, full_degree=2))

    def test_full_check_rejects_boundary_nodes_and_negative_weights(self):
        for row in ("-1 -0.5 2", "-0.3 -0.3 -2"):
            with self.subTest(row=row):
                with self.assertRaisesRegex(ValueError, "positive weights and interior nodes"):
                    self.check_table(f"x y w\n{row}\n", full_degree=1)

    def test_rejects_incorrect_columns(self):
        with self.assertRaisesRegex(ValueError, "column header"):
            self.check_table("w x y\n2 -0.5 -0.5\n")


class SymmetricTetrahedronTest(unittest.TestCase):
    def test_positive_eight_point_rule_moments_through_degree_three(self):
        from fractions import Fraction as F
        from itertools import product
        from math import factorial, prod

        # Reduce powers using t² = t/12 + 1/80. The two group weights
        # have mean t = 0, so only the constant coefficient contributes.
        for powers in product(range(4), repeat=4):
            degree = sum(powers)
            if degree > 3:
                continue
            values = []
            for corner in range(4):
                a, b = F(1), F(0)
                for coordinate, exponent in enumerate(powers):
                    slope = 3 if coordinate == corner else -1
                    for _ in range(exponent):
                        a, b = a/4 + b*slope/80, a*slope + b/4 + b*slope/12
                values.append(a)
            exact = F(6 * prod(map(factorial, powers)), factorial(degree + 3))
            self.assertEqual(sum(values)/4, exact, powers)


class SymmetricTriangleTest(unittest.TestCase):
    def test_exact_degree_four_group_moments(self):
        from fractions import Fraction as F

        # Pairs represent a + b sqrt(10), with exact rational coefficients.
        def mul(x, y):
            a, b = x
            c, d = y
            return a*c + 10*b*d, a*d + b*c

        A = (F(-2, 9), F(1, 9))
        B = (F(2, 45) - 2*A[0]/15, -2*A[1]/15)
        m2, m3, m4 = F(1, 36), F(1, 270), F(1, 810)
        # Eliminate m1 from m2 = A*m1+B and m3 = A*m2+B*m1.
        self.assertEqual(mul(A, (m3-A[0]*m2, -A[1]*m2)),
                         mul(B, (m2-B[0], -B[1])))
        self.assertEqual(tuple(a*m3+b*m2 for a, b in zip(A, B)), (m4, 0))
        # The fifth centered coordinate moment is 10 times m5.
        # Its nonzero radical coefficient rules out equality with the
        # rational exact mean on the unit triangle.
        fifth = tuple(10*(a*m4+b*m3) for a, b in zip(A, B))
        self.assertEqual(fifth[1], F(1, 1215))

        # Expand every barycentric monomial in the group parameter t.
        from itertools import product
        from math import factorial, prod

        moments = [(F(1), F(0)), (F(0), F(0)), (m2, 0), (m3, 0), (m4, 0)]
        # Divide by B using its conjugate to obtain the first shift moment.
        reciprocal = (B[0], -B[1])
        norm = mul(B, reciprocal)[0]
        moments[1] = tuple(x / norm for x in mul((m3-A[0]*m2, -A[1]*m2), reciprocal))
        for powers in product(range(5), repeat=3):
            degree = sum(powers)
            if degree > 4:
                continue
            total = [F(0), F(0)]
            for corner in range(3):
                coefficients = [F(1)]
                for index, power in enumerate(powers):
                    slope = 2 if index == corner else -1
                    for _ in range(power):
                        coefficients = [a/3 + slope*b for a, b in
                                        zip(coefficients + [F(0)], [F(0)] + coefficients)]
                self.assertTrue(all(isinstance(c, F) for c in coefficients))
                for j in range(2):
                    total[j] += sum(c*m[j] for c, m in zip(coefficients, moments)) / 3
            exact = F(2 * prod(map(factorial, powers)), factorial(degree + 2))
            self.assertEqual(total, [exact, 0], powers)



    def test_positive_six_point_rule_through_degree_three(self):
        from fractions import Fraction as F
        from itertools import product
        from math import factorial, prod

        # Reduce modulo t² = (2/15)t + 1/36. The weighted mean of t is zero.
        for powers in product(range(4), repeat=3):
            degree = sum(powers)
            if degree > 3:
                continue
            total = F(0)
            for corner in range(3):
                a, b = F(1), F(0)
                for coordinate, exponent in enumerate(powers):
                    slope = 2 if coordinate == corner else -1
                    for _ in range(exponent):
                        a, b = a/3 + b*slope/36, a*slope + b/3 + 2*b*slope/15
                total += a
            exact = F(2 * prod(map(factorial, powers)), factorial(degree + 2))
            self.assertEqual(total/3, exact, powers)


class SignedSimplexTest(unittest.TestCase):
    def test_signed_rules_fail_fourth_moment(self):
        from fractions import Fraction as F
        for size, high, low, center, outer, expected in (
            (3, F(3,5), F(1,5), -F(9,16), F(25,48), F(14,225)),
            (4, F(1,2), F(1,6), -F(4,5), F(9,20), F(5,192)),
        ):
            with self.subTest(size=size):
                value = center * F(1,size)**4 + outer * (high**4 + (size-1)*low**4)
                self.assertEqual(value, expected)
                self.assertNotEqual(value, F(24, size*(size+1)*(size+2)*(size+3)))

    def test_minimal_signed_rules_through_degree_three(self):
        from fractions import Fraction as F
        from itertools import product
        from math import factorial, prod

        cases = [(3, F(3, 5), F(1, 5), -F(9, 16), F(25, 48)),
                 (4, F(1, 2), F(1, 6), -F(4, 5), F(9, 20))]
        for size, high, low, center_weight, outer_weight in cases:
            for powers in product(range(4), repeat=size):
                degree = sum(powers)
                if degree > 3:
                    continue
                with self.subTest(size=size, powers=powers):
                    value = center_weight * F(1, size)**degree
                    value += outer_weight * sum(
                        high**a * low**(degree-a) for a in powers)
                    exact = F(factorial(size-1) * prod(map(factorial, powers)),
                              factorial(degree+size-1))
                    self.assertEqual(value, exact)


class KeastRuleTest(unittest.TestCase):
    def test_eleven_point_rule_fails_fifth_moment(self):
        from fractions import Fraction as F
        from math import comb

        # In the six-point orbit the signs occur equally often.
        pair_mean = sum(comb(5, k) * F(1, 4)**(5-k) * F(5, 224)**(k//2)
                        for k in (0, 2, 4))
        value = (-F(148, 1875) * F(1, 4)**5
                 + F(343, 7500) * (F(11, 14)**5 + 3*F(1, 14)**5)
                 + 6*F(56, 375)*pair_mean)
        self.assertEqual(value - F(1, 56), F(1, 3136))

    def test_eleven_point_rule_through_degree_four(self):
        from fractions import Fraction as F
        from itertools import combinations, product
        from math import factorial, prod

        for powers in product(range(5), repeat=4):
            degree = sum(powers)
            if degree > 4:
                continue
            value = -F(148, 1875) * F(1, 4)**degree
            value += F(343, 7500) * sum(
                F(11, 14)**k * F(1, 14)**(degree-k) for k in powers)
            # Pair opposite sign patterns; their odd radical terms cancel.
            for plus in combinations(range(4), 2):
                a, b = F(1), F(0)
                for index, power in enumerate(powers):
                    sign = 1 if index in plus else -1
                    for _ in range(power):
                        a, b = a/4 + sign*b*F(5, 224), sign*a + b/4
                value += F(56, 375) * a
            exact = F(6 * prod(map(factorial, powers)), factorial(degree+3))
            self.assertEqual(value, exact, powers)


class TetrahedronBoundaryRuleTest(unittest.TestCase):
    def test_vertices_and_edge_midpoints_have_exact_degree_two(self):
        from fractions import Fraction as F
        from itertools import combinations, product
        from math import factorial, prod

        def apply(powers):
            vertices = sum(prod(F(i == j)**k for j, k in enumerate(powers))
                           for i in range(4))
            edges = sum(prod(F(j in edge, 2)**k for j, k in enumerate(powers))
                        for edge in combinations(range(4), 2))
            return -vertices/20 + edges/5

        for powers in product(range(3), repeat=4):
            degree = sum(powers)
            if degree <= 2:
                self.assertEqual(apply(powers), F(6 * prod(map(factorial, powers)),
                                                   factorial(degree + 3)), powers)
        self.assertEqual(apply((3, 0, 0, 0)), F(1, 40))
        self.assertNotEqual(apply((3, 0, 0, 0)), F(1, 20))


class TriangleBoundaryRuleTest(unittest.TestCase):
    def test_one_interior_point_rule_through_degree_four(self):
        from fractions import Fraction as F
        from itertools import combinations, product
        from math import factorial, prod

        # On each edge, t and 1-t are the two roots of t²-t+1/6.
        # Reduce the edge monomial to a+b*t; summing over roots gives 2*a+b.
        for powers in product(range(5), repeat=3):
            degree = sum(powers)
            if degree > 4:
                continue
            value = F(9, 20) * F(1, 3)**degree
            value -= F(1, 60) * sum(k == degree for k in powers)
            for i, j in combinations(range(3), 2):
                if powers[3-i-j]:
                    continue
                a, b = F(1), F(0)
                for _ in range(powers[i]):
                    a, b = -b/6, a+b
                for _ in range(powers[j]):
                    a, b = a+b/6, -a
                value += (2*a+b)/10
            exact = F(2 * prod(map(factorial, powers)), factorial(degree+2))
            self.assertEqual(value, exact, powers)

    def test_centroid_vertices_and_edge_midpoints_have_exact_degree_three(self):
        from fractions import Fraction as F
        from itertools import combinations, product
        from math import factorial, prod

        nodes = [(F(9, 20), (F(1, 3),) * 3)]
        nodes += [(F(1, 20), tuple(F(i == j) for j in range(3)))
                  for i in range(3)]
        nodes += [(F(2, 15), tuple(F(j in edge, 2) for j in range(3)))
                  for edge in combinations(range(3), 2)]

        def apply(powers):
            return sum(w * prod(x**k for x, k in zip(point, powers))
                       for w, point in nodes)

        self.assertEqual(sum(min(point) > 0 for _, point in nodes), 1)
        self.assertTrue(all(w > 0 for w, _ in nodes))
        for powers in product(range(4), repeat=3):
            degree = sum(powers)
            if degree <= 3:
                exact = F(2 * prod(map(factorial, powers)), factorial(degree + 2))
                self.assertEqual(apply(powers), exact, powers)
        self.assertEqual(apply((4, 0, 0)) - F(1, 15), F(1, 180))


class TetrahedronOneInteriorTest(unittest.TestCase):
    def test_equal_budget_mean_tradeoff(self):
        from fractions import Fraction as F
        from itertools import product

        total = 6 * F(1, 4)**5
        for point in product(range(6), repeat=4):
            if sum(point) == 5 and min(point) == 0:
                total += (2 if sorted(point) == [0, 1, 1, 3] else 1) * F(point[0], 5)**5
        self.assertEqual(total / 70, F(891731, 22400000))
        quadratic = 6 * F(1, 4)**2
        for point in product(range(6), repeat=4):
            if sum(point) == 5 and min(point) == 0:
                quadratic += (2 if sorted(point) == [0, 1, 1, 3] else 1) * F(point[0], 5)**2
        self.assertEqual(quadratic / 70, F(1739, 14000))

        bias = total / 70 - F(1, 56)
        factor = F(32, 105)**2 / 6 + 6 * F(25, 288)**2 + 4 * F(99, 8960)**2
        factor += 12 * sum(F(w)**2 for w in ('35/2304', '85/8064', '25/896'))
        extra_variance = (factor - F(1, 70)) / 2500
        self.assertLess(F('0.00491')**2, extra_variance)
        self.assertLess(extra_variance, F('0.004915')**2)
        self.assertGreater(bias**2, extra_variance)
        self.assertGreater((quadratic / 70 - F(1, 10))**2, extra_variance)

        # Same budget, but at the four degree-two nodes (17/17/18/18).
        from math import sqrt
        four_factor = (F(2, 17) + F(2, 18)) / 16
        self.assertEqual(four_factor, F(35, 2448))
        t = 1 / (4 * sqrt(5))
        four_bias = ((0.25 + 3*t)**5 + 3*(0.25 - t)**5) / 4 - float(F(1, 56))
        four_mse = four_bias**2 + float(four_factor / 2500)
        self.assertAlmostEqual(four_mse, 6.116738845442506e-6, delta=1e-12)
        self.assertLess(four_mse, float(factor / 2500))


    def test_measurement_table_against_exact_budget_optimization(self):
        from fractions import Fraction as F

        groups = [(1, F(32, 105)), (12, F(25, 288)), (4, F(99, 8960)),
                  (12, F(35, 2304)), (12, F(85, 8064)), (12, F(25, 896))]
        weights = [w for count, w in groups for _ in range(count)]
        # For each extra budget, minimize over all allocations so far.
        optimum = [F(0)] + [None] * 17
        for weight in weights:
            optimum = [min(optimum[e-j] + weight**2 / (1+j)
                           for j in range(e+1) if optimum[e-j] is not None)
                       for e in range(18)]
        for budget, center, boundary in ((53, 1, 1), (54, 2, 1), (57, 5, 1),
                                          (69, 5, 2), (70, 6, 2)):
            reads = [center] + [boundary] * 12 + [1] * 40
            self.assertEqual(sum(reads), budget)
            self.assertEqual(sum(w*w/r for w, r in zip(weights, reads)),
                             optimum[budget-53], budget)

    def test_first_boundary_repeat_is_measurement_58(self):
        from fractions import Fraction as F

        center = F(32, 105)
        largest_boundary = max(map(F, ('99/8960', '35/2304', '85/8064',
                                      '25/288', '25/896')))
        self.assertEqual(largest_boundary, F(25, 288))
        boundary_gain = largest_boundary**2 / 2
        for repeats in range(1, 5):
            self.assertGreater(center**2 / (repeats * (repeats + 1)), boundary_gain)
        self.assertLess(center**2 / (5 * 6), boundary_gain)

        # Once each of the twelve largest boundary weights has two reads,
        # the next center read beats every remaining boundary option.
        other_boundary = max(map(F, ('99/8960', '35/2304', '85/8064', '25/896')))
        center_gain = center**2 / (5 * 6)
        self.assertGreater(center_gain, largest_boundary**2 / (2 * 3))
        self.assertGreater(center_gain, other_boundary**2 / 2)


    def test_fifty_three_point_rule_variance_bounds_for_all_shared_budgets(self):
        from fractions import Fraction as F

        center = F(32, 105)**2
        face = 12 * F(25, 288)**2
        rest = 4 * F(99, 8960)**2 + 12 * sum(
            F(w)**2 for w in ('35/2304', '85/8064', '25/896'))
        # Bounds for N times the variance factor: N=53, 54–69,
        # and N>=70 by repeating a full 70-measurement plan.
        bounds = (53*(rest + center + face),
                  69*(rest + center/2 + face),
                  140*(rest + center/6 + face/2))
        for bound in bounds:
            self.assertLess(bound, F(116, 35)**2)

    def test_two_positive_face_triples_require_separated_shifts(self):
        from fractions import Fraction as F

        wed = F(13, 70)/3 - F(1, 20)
        wdg = 2 * F(1, 1680)
        # The ratio of these moments is a weighted mean of g/E.
        near_d_max = F(1, 3) - 3 * wdg / wed
        # Positive face centroids consume part of the mass 1/70.
        far_d_threshold = wdg / F(1, 70)
        self.assertLess(near_d_max, far_d_threshold)
        self.assertEqual(near_d_max / 3, F(1, 90))
        self.assertEqual(far_d_threshold / 3, F(1, 6)**2)

    def test_degree_five_35_point_shifts_are_separated(self):
        from fractions import Fraction as F

        near_d = F(13, 3780) / F(29, 630)
        far_d = F(1, 840) / F(1, 70)
        self.assertEqual(near_d / 3, F(13, 522))
        self.assertEqual(far_d / 3, F(1, 36))
        self.assertLess(near_d, far_d)

    def test_face_centroids_sharpen_35_point_edge_weight_bound(self):
        from fractions import Fraction as F

        # Removing a single orbit gives affine corrected moments. Their
        # determinant has degree at most two, so three exact checks suffice.
        for k in (F(0), F(4, 77), F(2, 35)):
            m2, m3, m4 = [F(x) - k*F(-1, 6)**j for j, x in zip(
                (2, 3, 4), ('29/1890', '11/5670', '13/34020'))]
            self.assertEqual(m2*m4 - m3*m3, F(1, 476280) - 11*k/272160)
        self.assertLess(F(4, 77), F(2, 35))

    def test_degree_five_rest_moments_from_simplex_integrals(self):
        from fractions import Fraction as F
        from itertools import combinations
        from math import factorial, prod

        def rest(*factors):
            powers = [sum(i in factor for factor in factors) for i in range(4)]
            degree = sum(powers)
            return (F(6 * prod(map(factorial, powers)), factorial(degree + 3))
                    - F(32, 105) * F(1, 4)**degree)

        pairs = list(combinations(range(4), 2))
        mass = rest()
        e = sum(rest(pair) for pair in pairs)
        e2 = sum(rest(a, b) for a in pairs for b in pairs)
        self.assertEqual((mass, e, e2), (F(73, 105), F(13, 70), F(1, 20)))
        self.assertEqual((mass/3-e, mass/9-2*e/3+e2),
                         (F(29, 630), F(13, 3780)))
        triples = list(combinations(range(4), 3))
        self.assertEqual(sum(rest(triple) for triple in triples), F(1, 70))
        self.assertEqual(sum(rest(pair, triple) for pair in pairs for triple in triples),
                         F(1, 280))
        # The prescribed centroid weight accounts for the entire B moment.
        self.assertEqual(rest(tuple(range(4))), 0)
        g = (0, 1, 2)
        self.assertEqual(rest(g), F(1, 280))
        self.assertEqual(rest(g, (0,), (0,)) - 2*rest(g, (0, 1))
                         + rest(g, (1,), (1,)), F(1, 1680))

    def test_triangle_triple_and_sextuple_cannot_match_face_moments(self):
        from fractions import Fraction as F

        mean, variance = F(39,146), F(3,5329)
        def e(t):
            return F(1,3)-3*t*t

        def cubic(t):
            return 2*t**3-F(23,8)*t*t+F(25,432)

        left, right = F('-0.136'), F('-0.135')
        self.assertLess(cubic(left), 0)
        self.assertGreater(cubic(right), 0)
        self.assertGreater(e(left), mean)
        self.assertLess(mean-variance/(e(right)-mean), F(1,4))
        self.assertGreater(F(3,16)-F(5,8)/4, F(1,48))

        left, right = F('0.1499'), F('0.1500')
        self.assertGreater(cubic(left), 0)
        self.assertLess(cubic(right), 0)
        self.assertTrue(0 < mean-e(left) < mean-e(right) < F(1,500))
        self.assertGreater(mean+500*variance, F(1,3))

    def test_recover_three_face_group_weights_from_shift_moments(self):
        from fractions import Fraction as F

        # Synthetic data: test the inversion, not existence of a degree-five rule.
        shifts = (F(-1, 12), F(1, 18), F(1, 5))
        weights = (F(1, 7), F(2, 7), F(4, 7))
        m2, m3, m4 = (sum(w*t**j for w, t in zip(weights, shifts))
                      for j in (2, 3, 4))
        for i, t in enumerate(shifts):
            u, v = (x for j, x in enumerate(shifts) if j != i)
            self.assertEqual((m4-(u+v)*m3+u*v*m2)/(t*t*(t-u)*(t-v)), weights[i])

    def test_degree_five_39_point_layout_and_obstructions(self):
        from fractions import Fraction as F
        from itertools import product

        layouts = [(h, v, k, e) for h, v, k, e in product(
            (6, 7, 9), range(2), range(2), range(4))
            if 4*h + 4*v + 6*k + 12*e == 38]
        self.assertEqual(layouts, [(7, 1, 1, 0)])
        self.assertGreater(F(1, 4)/288, 0)  # null test at edge midpoints
        self.assertEqual(F(1, 840)/F(1, 70), F(1, 12))
        self.assertLess(F(13, 3780)/F(29, 630), F(1, 12))

    def test_nonnegative_shift_certificate_excludes_open_edge_nodes(self):
        from fractions import Fraction as F

        def certificate(x, y):
            return x*x/3-x*y-(y/3-x*x)/6+(x/3-y)/144

        m2, m3, m4, m5 = map(F, ('29/1890', '11/5670', '13/34020', '43/408240'))
        self.assertEqual(m4/3-m5-(m3/3-m4)/6+(m2/3-m3)/144, 0)
        # Both edge expressions are polynomials of degree at most two in x.
        for x in (F(0), F(1, 36), F(1, 9)):
            self.assertEqual(certificate(x, (x-F(1,27))/2), (F(1,3)-3*x)/288)
        # Both expressions have degree at most five in the face shift.
        for t in map(F, range(6)):
            self.assertEqual(certificate(t*t, t**3), t*t*(F(1,3)-t)*(t-F(1,12))**2)

    def test_degree_five_37_point_remaining_orbit_types(self):
        from itertools import product

        layouts = set()
        for center, triples, sextuples, vertices, midpoints, edges in product(
                range(2), range(4), range(2), range(2), range(2), range(4)):
            face_size = center + 3*triples + 6*sextuples
            # The chapter rules out three or four nodes per open face.
            if face_size < 5 or 4*face_size + 4*vertices + 6*midpoints + 12*edges != 36:
                continue
            # One sextuple with edge nodes fails the E moment.
            if (center, triples, sextuples, edges) == (0, 0, 1, 1):
                continue
            layouts.add((center, triples, sextuples, vertices, midpoints, edges))
        self.assertEqual(layouts, {(0, 2, 0, 0, 0, 1), (0, 3, 0, 0, 0, 0),
                                   (0, 1, 1, 0, 0, 0)})

    def test_degree_five_37_point_face_sextuple_with_edge_nodes(self):
        from fractions import Fraction as F

        # Local face moments fix E on the sextuple. On any edge,
        # E = x(1-x) = 1/4 - (x-1/2)**2 cannot exceed this value.
        face_e = (1 - F(3, 2)*F(1, 1680)/F(1, 280))/3
        self.assertEqual(face_e, F(1, 4))
        boundary_mass = 1 - F(32, 105)
        required_e = F(3, 10) - F(32, 105)*F(3, 8)
        self.assertEqual(required_e - boundary_mass*face_e, F(1, 84))

    def test_last_35_point_arrangement_is_impossible(self):
        from fractions import Fraction as F
        from itertools import product

        # The expressions have degree at most five in each variable.
        for v, k in product(map(F, range(6)), repeat=2):
            a, b, c, d, e = [F(x)-v/3**j-k*F(-1,6)**j for j,x in zip(
                (0,2,3,4,5), ('73/105','29/1890','11/5670','13/34020','43/408240'))]
            D, U, T = b*d-c*c, b*e-c*d, c*e-d*d
            self.assertEqual((T*b*D-U*(U*b-c*D)+T*T*a)*2032510040064000,
                             -8+196*k+147*k*k+v*(672-19992*k-15435*k*k)
                             +v*v*(-14112+493920*k))
            self.assertEqual((U-2*D/3)*1905120, -1+49*k+v*(42-735*k))
        self.assertLess(-14112+F(493920,49), 0)
        self.assertLess(-8+4+F(147,49**2)+672*F(4,735), 0)
        self.assertEqual(42-735*F(2,35), 0)

    def test_degree_five_35_point_vertex_weight_bound(self):
        from fractions import Fraction as F
        from itertools import product

        # The determinant identity is at most quadratic in each variable.
        for v, k in product(map(F, range(3)), repeat=2):
            mass = F(73, 105)-v-k
            first = F(29, 630)-v/3-k/12
            second = F(13, 3780)-v/9-k/144
            self.assertEqual(mass*second-first**2,
                             F(1, 3675)-v/20-k/1680+v*k/16)
        upper = F(4, 735)
        self.assertEqual(F(1, 3675), upper/20)
        self.assertGreater(F(1, 20)-F(2, 35)/16, 0)
        self.assertGreater(F(1, 1680)-upper/16, 0)

    def test_degree_five_35_point_edge_weight_bound(self):
        from fractions import Fraction as F

        ed_rest = F(13, 70)/3 - F(1, 20)
        dg_rest = 2 * F(1, 1680)
        edge_ed = F(1, 4) * (F(1, 3) - F(1, 4))
        self.assertEqual(edge_ed, F(1, 48))
        # Off-center face nodes have g/E < 1/9, so their ED
        # contribution exceeds nine times their Dg contribution.
        self.assertEqual((ed_rest - 9*dg_rest) / edge_ed, F(2, 35))

    def test_degree_five_35_point_sextuple_obstructions(self):
        from fractions import Fraction as F

        e = (1 - F(3, 2) * F(1, 1680) / F(1, 280)) / 3
        self.assertEqual(e, F(1, 4))  # same E as at an edge midpoint
        self.assertEqual(F(1, 20) - e * F(13, 70), F(1, 280))

        # With positive face-centroid weights, W*g < 1/70,
        # so the displaced group's D exceeds the edge-midpoint value.
        self.assertEqual(F(1, 840) / F(1, 70), F(1, 12))
        self.assertLess(F(13, 3780) / F(29, 630), F(1, 12))

    def test_face_sextuples_with_vertices_and_face_centroids_are_impossible(self):
        from fractions import Fraction as F

        # E*(1/3-E) vanishes at vertices and face centroids.
        wed = F(13, 70)/3 - F(1, 20)
        wdg = 2 * F(1, 1680)
        self.assertEqual(wdg / wed, F(1, 10))  # g/E
        # Positivity at the face centroids forces W*g < 1/70.
        e_upper = F(1, 3) - wdg / F(1, 70)
        # E² >= 3*g and E > 0 imply E >= 3*g/E.
        e_lower = 3 * wdg / wed
        self.assertEqual((e_upper, e_lower), (F(1, 4), F(3, 10)))
        self.assertGreater(e_lower, e_upper)

    def test_single_six_point_orbit_per_face_degree_five_obstructions(self):
        from fractions import Fraction as F

        # A single face orbit fixes E by the weighted difference moment.
        face_e = (1 - F(3, 2) * (F(1, 1680) / F(1, 280))) / 3
        self.assertEqual(face_e, F(1, 4))
        self.assertEqual(F(1, 20) - face_e * F(13, 70), F(1, 280))

        # With face centroids instead of vertices, D = 1/3 - E
        # vanishes at those centroids and is constant on the other nodes.
        d = F(13, 3780) / F(29, 630)
        displaced_mass = 2 * F(1, 1680) / d
        self.assertEqual(displaced_mass - 4 * F(1, 280), F(3, 1820))

    def test_face_centroids_cannot_complete_two_positive_orbits(self):
        from fractions import Fraction as F

        # A zero shift changes only the zeroth shift moment. The nonzero
        # shifts still obey the recurrence with S=5/12 and P=1/36.
        total_boundary_mass = F(73, 105)
        m2, m3 = F(29, 1890), F(11, 5670)
        S, P = F(5, 12), F(1, 36)
        m1 = (S*m2 - m3)/P
        displaced_mass = (S*m1 - m2)/P
        self.assertEqual(displaced_mass, F(389, 210))
        self.assertEqual(total_boundary_mass - displaced_mass, -F(81, 70))

    def test_vertices_and_two_face_orbits_force_degenerate_moments(self):
        from fractions import Fraction as F

        def moments(v):
            return [F(x) - v / 3**j for j, x in zip(
                (0, 2, 3, 4, 5), ('73/105', '29/1890', '11/5670',
                                    '13/34020', '43/408240'))]

        # Both sides are polynomials of degree at most five in v.
        # Agreement at six distinct rational values proves the identity.
        for v in range(6):
            a, b, c, d, e = moments(F(v))
            D, U, T = b*d-c*c, b*e-c*d, c*e-d*d
            self.assertEqual(T*b*D - U*(U*b-c*D) + T*T*a,
                             -F((42*v-1)**2, 254063755008000))
            # At degree at most five, the same six checks verify the
            # displaced-mass identity for the case with face centroids.
            self.assertEqual(U*(U*b-c*D) - T*b*D, (F(389, 210)-v)*T*T)
        self.assertEqual(F(73, 105)-F(389, 210), -F(81, 70))
        _, b, c, d, _ = moments(F(1, 42))
        self.assertEqual(b*d-c*c, 0)

    def test_degree_five_positive_thirty_one_point_orbit_reduction(self):
        from fractions import Fraction as F
        from itertools import product

        # At least three points per open face. A single face centroid
        # is optional, plus any number of distinct triples or sextuples.
        face_counts = {c + 3*t + 6*s for c, t, s in product(range(2), range(3), range(2))}
        # Three points per face already exceed the positive mass budget.
        self.assertGreater(F(32, 105) + 12*F(9, 140), 1)
        splits = [(4*f, 4*v, 6*m, 12*e)
                  for f in sorted(face_counts & set(range(4, 8)))
                  for v, m, e in product(range(2), range(2), range(3))
                  if 4*f + 4*v + 6*m + 12*e == 30]
        self.assertEqual(splits, [(24, 0, 6, 0)])
        # For one sextuple per face, the local moment fixes E=1/4,
        # the same value as at the six edge midpoints.
        self.assertEqual(F(13, 70) - F(73, 105)/4, F(1, 84))

    def test_positive_face_centroids_cannot_fix_edge_midpoint_shifts(self):
        from fractions import Fraction as F

        lo, hi = F(39, 1000), F(4, 77)
        # Subtracting a positive centroid mass lowers the eliminated
        # expression by T²*C, so the original numerator must be positive.
        self.assertLess(196*lo + 147*lo**2 - 8, 0)
        for k, expected in ((lo, F(911, 1905120000)), (hi, F(17, 20956320))):
            b, c, d, e = [F(x) - k*F(-1, 6)**j for j, x in zip(
                (2, 3, 4, 5), ('29/1890', '11/5670', '13/34020', '43/408240'))]
            D, U = b*d-c*c, b*e-c*d
            self.assertEqual(U - 2*D/3, expected)
            self.assertGreater(expected, 0)

    def test_edge_midpoints_force_shifts_outside_open_faces(self):
        from fractions import Fraction as F

        def terms(k):
            a,b,c,d,e = [F(x)-k*F(-1, 6)**j for j,x in zip(
                (0,2,3,4,5), ('73/105','29/1890','11/5670','13/34020','43/408240'))]
            D,U,T = b*d-c*c, b*e-c*d, c*e-d*d
            return T*b*D-U*(U*b-c*D)+T*T*a, D, U-2*D/3

        # The eliminated expression has degree at most five.
        for k in map(F, range(6)):
            self.assertEqual(terms(k)[0], -(8-196*k-147*k*k)/2032510040064000)
        lo, hi = F(39,1000), F(1,25)
        self.assertLess(terms(lo)[0], 0)
        self.assertGreater(terms(hi)[0], 0)
        for k in (lo, hi):
            self.assertTrue(all(x > 0 for x in terms(k)[1:]))

    def test_two_face_orbits_have_inconsistent_degree_five_moments(self):
        from fractions import Fraction as F

        m0, m2, m4 = F(73, 105), F(29, 1890), F(13, 34020)
        m3 = (F(1, 70) - m0/27 + m2)/2
        m5 = (F(1, 2520) - m2/27 + m4)/2
        determinant = m4 - m3*m3/m2
        self.assertNotEqual(determinant, 0)
        S = (m5 - m4*m3/m2)/determinant
        P = (S*m3 - m4)/m2
        self.assertEqual((S, P), (F(5, 12), F(1, 36)))
        m1 = (S*m2 - m3)/P
        self.assertEqual(m2 - S*m1 + P*m0, -F(9, 280))

    def test_twenty_one_point_rule_optimal_plan_at_budget_53(self):
        from fractions import Fraction as F

        groups = ((1, F(32, 105), 5), (4, F(1, 168), 1),
                  (4, -F(81, 280), 5), (12, F(16, 105), 2))
        self.assertEqual(sum(count*r for count, _, r in groups), 53)
        self.assertEqual(sum(count*w*w/r for count, w, r in groups), F(33073, 147000))
        self.assertGreater(min(w*w/(r*(r-1)) for _, w, r in groups if r > 1),
                           max(w*w/(r*(r+1)) for _, w, r in groups))

    def test_symmetric_twenty_one_point_rule(self):
        from fractions import Fraction as F
        from itertools import permutations, product
        from math import factorial, prod

        groups = [((F(1, 4),)*4, F(32, 105)), ((1, 0, 0, 0), F(1, 168)),
                  ((F(1, 3),)*3 + (0,), -F(81, 280)),
                  ((F(1, 2), F(1, 4), F(1, 4), 0), F(16, 105))]
        nodes = [(point, weight) for seed, weight in groups
                 for point in set(permutations(map(F, seed)))]
        self.assertEqual(len({point for point, _ in nodes}), 21)
        self.assertEqual(sum(min(point) > 0 for point, _ in nodes), 1)
        sixth_moment = sum(w * point[0]**6 for point, w in nodes)
        self.assertEqual(sixth_moment - F(1, 84), F(1, 3360))
        for powers in product(range(6), repeat=4):
            degree = sum(powers)
            if degree <= 5:
                value = sum(w * prod(x**k for x, k in zip(point, powers))
                            for point, w in nodes)
                exact = F(6 * prod(map(factorial, powers)), factorial(degree+3))
                self.assertEqual(value, exact, powers)

    def test_degree_five_boundary_grid(self):
        from fractions import Fraction as F
        from itertools import product
        from math import factorial, prod

        weights = {(5, 0, 0, 0): F(99, 8960), (4, 1, 0, 0): -F(35, 2304),
                   (3, 2, 0, 0): F(85, 8064), (3, 1, 1, 0): F(25, 288),
                   (2, 2, 1, 0): -F(25, 896)}
        grid = [(tuple(F(k, 5) for k in point), weights[tuple(sorted(point, reverse=True))])
                for point in product(range(6), repeat=4) if sum(point) == 5 and min(point) == 0]
        self.assertEqual(len(grid), 52)
        # A sixth-degree moment distinguishes exact degree five from six.
        sixth = F(32, 105) * F(1, 4)**6 + sum(w * point[0]**6 for point, w in grid)
        self.assertEqual(sixth, F(34359, 2800000))
        self.assertNotEqual(sixth, F(1, 84))
        for powers in product(range(6), repeat=4):
            degree = sum(powers)
            if degree > 5:
                continue
            value = F(32, 105) * F(1, 4)**degree
            value += sum(weight * prod(x**k for x, k in zip(point, powers))
                         for point, weight in grid)
            self.assertEqual(value, F(6 * prod(map(factorial, powers)), factorial(degree+3)), powers)


if __name__ == "__main__":
    unittest.main()
