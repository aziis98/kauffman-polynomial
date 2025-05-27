import operator

from codes import SGCode
from equation_dsl import Var
from generic_skein_algorithm import generic_unknot_skein_polynomial
from sympy import symbols, simplify
from functools import reduce


def test_synthetic_homfly():
    v, z = symbols("v z")
    d = (v ** (-1) - v) / z

    homfly = Var("homfly")
    LL = Var("L")

    # homfly equation: P(L+) / v - P(L-) * v = P(L0) * z
    synthetic_homfly_polynomial = generic_unknot_skein_polynomial(
        homfly,
        [
            homfly(LL.positive) / v - homfly(LL.negative) * v
            ==
            homfly(LL.splice_h) * z
        ],
        case_std_unknot=lambda _: 1,
        case_disjoint=lambda rec, components: (
            d ** (len(components) - 1) *
            reduce(
                operator.mul,
                (rec(c) for c in components),
                1
            )
        )
    )

    sg_hopf = SGCode.from_tuples([
        [(+1, -1), (-2, -1)],
        [(-1, -1), (+2, -1)],
    ])

    P_result = synthetic_homfly_polynomial(sg_hopf)
    P_expected = (
        1/(v ** 3*z)-1/(v*z)-z/v
    )

    assert simplify(P_result) == simplify(P_expected)


def test_synthetic_writhe():
    writhe = Var("writhe")
    LL = Var("L")

    # writhe equation: W(L+) = W(L0) + 1, W(L-) = W(L0) - 1
    writhe_polynomial_func = generic_unknot_skein_polynomial(
        writhe,
        [
            writhe(LL.positive) == writhe(LL.splice_h) + 1,
            writhe(LL.negative) == writhe(LL.splice_v) - 1,
        ],
        case_std_unknot=lambda _: 0,
        case_disjoint=lambda rec, components: (
            sum(rec(c) for c in components)
        )
    )
    sg_trefoil = SGCode.from_tuples([
        [(+1, +1), (-2, +1), (+3, +1),
         (-1, +1), (+2, +1), (-3, +1)]
    ])

    P_result = 1 + writhe_polynomial_func(sg_trefoil)
    P_expected = 3

    assert simplify(P_result) == simplify(P_expected)
