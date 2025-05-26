from codes import SGCode, PDCode
from kauffman import kauffman_polynomial
from sympy import symbols

from homfly import homfly_polynomial


v, z = symbols("v z")


def test_homfly_infinity():
    # hopf
    link_sgc = SGCode.from_tuples([
        [(-1, 1), (1, 1)]
    ])

    P_result = homfly_polynomial(link_sgc)
    P_expected = (v**0)

    P_result = P_result.simplify().expand()
    P_expected = P_expected.simplify().expand()

    print(P_result)
    print(P_expected)

    assert P_result == P_expected


def test_homfly_hopf():
    # hopf
    link_sgc = SGCode.from_tuples([
        [(+1, -1), (-2, -1)],
        [(-1, -1), (+2, -1)],
    ])

    P_result = homfly_polynomial(link_sgc)

    P_expected = (
        # L2a1{1}
        # v / z - v**3 / z + v * z

        # L2a1{0}
        1/(v ** 3*z)-1/(v*z)-z/v
    )

    P_result = P_result.simplify().expand()
    P_expected = P_expected.simplify().expand()

    print(P_result)
    print(P_expected)

    assert P_result == P_expected


def test_trefoil():
    link_sgc = SGCode.from_tuples([
        [(+1, +1), (-2, +1), (+3, +1),
         (-1, +1), (+2, +1), (-3, +1)]
    ])

    P_result = homfly_polynomial(link_sgc)
    P_expected = (
        (2*v ** 2-v ** 4)+v ** 2*z ** 2
    )

    P_result = P_result.simplify().expand()
    P_expected = P_expected.simplify().expand()

    print(P_result)
    print(P_expected)

    assert P_result == P_expected


def test_homfly_K4_1():
    link_sgc = SGCode.from_tuples([
        [
            (1, 1), (-4, -1), (3, -1), (-1, 1),
            (2, 1), (-3, -1), (4, -1), (-2, 1)
        ]
    ])

    P_result = homfly_polynomial(link_sgc)
    P_expected = (
        (v ** (-2)-1+v ** 2)-z ** 2
    )

    P_result = P_result.simplify().expand()
    P_expected = P_expected.simplify().expand()

    print(P_result)
    print(P_expected)

    assert P_result == P_expected


def test_homfly_K6_1():
    link_sgc = PDCode.from_tuples([
        [1, 7, 2, 6], [3, 10, 4, 11], [5, 3, 6, 2],
        [7, 1, 8, 12], [9, 4, 10, 5], [11, 9, 12, 8]
    ]).to_signed_gauss_code()

    p_K6_1 = homfly_polynomial(link_sgc)
    p_K6_1_expected = (
        z ** 0 * (v ** (-2) - v ** 2 + v ** 4) +
        z ** 2 * (-1 - v ** 2)
    ).expand()

    print(p_K6_1)
    print(p_K6_1_expected)

    assert p_K6_1 == p_K6_1_expected
