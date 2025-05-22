from codes import SGCode, PDCode
from kauffman_v2 import kauffman_polynomial, f_polynomial
from sympy import Poly, symbols, simplify, init_printing


from typing import Callable

a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


def test_kauffman_trivial():
    # single unknot
    link_sgc = SGCode.from_tuples([[]])

    assert kauffman_polynomial(link_sgc) == 1


def test_kauffman_trivial_2():
    # two unknots
    link_sgc = SGCode.from_tuples([[], []])

    assert kauffman_polynomial(link_sgc) == (d).expand()


def test_kauffman_trivial_3():
    # three unknots
    link_sgc = SGCode.from_tuples([[], [], []])

    assert kauffman_polynomial(link_sgc) == (d * d).expand()


def test_kauffman_infinity():
    """
    Test the Kauffman polynomial for the infinity link and its mirror
    """

    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(1, +1), (-1, +1)]]
        )
    ) == a ** +1

    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(1, -1), (-1, -1)]]
        )
    ) == a ** -1

    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(-1, 1), (1, 1)]]
        )
    ) == a ** +1

    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(-1, -1), (1, -1)]]
        )
    ) == a ** -1


def test_kauffman_hopf():
    # hopf
    link_sgc = SGCode.from_tuples([
        [(+1, -1), (-2, -1)],
        [(-1, -1), (+2, -1)],
    ])

    L_hopf = simplify(kauffman_polynomial(link_sgc))

    print(L_hopf)

    assert L_hopf == (-(a + 1/a)/z + 1 + (a + 1/a)*z).simplify()


def test_kauffman_hopf_mirror():
    # hopf mirror
    link_sgc = SGCode.from_tuples([
        [(+1, +1), (-2, +1)],
        [(-1, +1), (+2, +1)],
    ])

    L_hopf = simplify(kauffman_polynomial(link_sgc))
    print(L_hopf)

    assert L_hopf == (-(a + 1/a)/z + 1 + (a + 1/a)*z).simplify()

    # hopf mirror different numbers
    link_sgc = SGCode.from_tuples([
        [(+1, +1), (-2, +1)],
        [(+2, +1), (-1, +1)]
    ])

    L_hopf = simplify(kauffman_polynomial(link_sgc))
    print(L_hopf)

    assert L_hopf == (-(a + 1/a)/z + 1 + (a + 1/a)*z).simplify()

    # hopf mirror 1-rotated
    link_sgc = SGCode.from_tuples([
        [(-2, +1), (+1, +1)],
        [(+2, +1), (-1, +1)]
    ])

    L_hopf = simplify(kauffman_polynomial(link_sgc))
    print(L_hopf)

    assert L_hopf == (-(a + 1/a)/z + 1 + (a + 1/a)*z).simplify()


def test_kauffman_infinity_3():
    """
    Test the Kauffman polynomial with a link with two curls
    """

    # signs: +1, +1
    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(1, +1), (-1, +1), (2, +1), (-2, +1)]]
        )
    ) == a ** +2

    # signs: +1, -1
    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(1, +1), (-1, +1), (2, -1), (-2, -1)]]
        )
    ) == 1

    # signs: -1, -1
    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(1, -1), (-1, -1), (2, -1), (-2, -1)]]
        )
    ) == a ** -2

    # misc
    assert kauffman_polynomial(
        SGCode.from_tuples(
            [[(-1, -1), (2, -1), (-2, -1), (1, -1)]]
        )
    ).simplify() == a ** -2


def test_kauffman_trefoil():
    # trefoil
    link_sgc = SGCode.from_tuples([
        [(+1, +1), (-2, +1), (+3, +1),
         (-1, +1), (+2, +1), (-3, +1)]
    ])

    L_trefoil = kauffman_polynomial(link_sgc)
    L_trefoil_expected = (
        (-2*a - a**(-1)) + (1 + a**(-2)) * z + (a + a**(-1))*z**2
    )

    assert L_trefoil.simplify() == (L_trefoil_expected).simplify()


def test_kauffman_K4_1():
    # figure-8
    # link_pd = PDCode.from_tuples([
    #     (4, 2, 5, 1), (8, 6, 1, 5), (6, 3, 7, 4), (2, 7, 3, 8)
    # ])

    # print(link_pd.to_signed_gauss_code())

    link_sgc = SGCode.from_tuples([
        [(1, 1), (-4, -1), (3, -1), (-1, 1), (2, 1), (-3, -1), (4, -1), (-2, 1)]
    ])

    L_figure8 = kauffman_polynomial(link_sgc)
    L_figure8_expected = (
        (a + a**(-1))*z**3 + (a**2 + 2 + a**(-2))*z**2 +
        (-a - a**(-1))*z**1 + (-a**2 - 1 - a**(-2))*z**0
    )

    assert L_figure8.expand() == L_figure8_expected.expand()


def test_kauffman_K5_1():
    link_pd = PDCode.from_tuples([
        (2, 8, 3, 7), (4, 10, 5, 9), (6, 2, 7, 1), (8, 4, 9, 3), (10, 6, 1, 5)
    ])

    link_sgc = link_pd.to_signed_gauss_code()
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K5_1 = kauffman_polynomial(link_sgc)
    kL_K5_1_expected = (
        z**4 * (a + a**(-1)) +
        z**3 * (1 + a**(-2)) +
        z**2 * (-4*a - 3*a**(-1) + a**(-3)) +
        z**1 * (-2 - a**(-2) + a**(-4)) +
        z**0 * (3*a + 2*a**(-1))
    )

    assert kL_K5_1.expand() == kL_K5_1_expected.expand()


def test_kauffman_K5_2():
    link_pd = PDCode.from_tuples([
        (4, 7, 5, 8), (6, 1, 7, 2), (10, 5, 1, 6), (8, 3, 9, 4), (2, 9, 3, 10)
    ])

    link_sgc = link_pd.to_signed_gauss_code()
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K5_2 = kauffman_polynomial(link_sgc).simplify().expand()
    kL_K5_2_expected = (
        z**4 * (a + a**(-1)) +
        z**3 * (a**2 + 2 + a**(-2)) +
        z**2 * (-2*a - a**(-1) + a**(-3)) +
        z**1 * (-2*a**2 - 2) +
        z**0 * (a + a**(-1) - a**(-3))
    ).simplify().expand()

    print(kL_K5_2)
    print(kL_K5_2_expected)

    assert kL_K5_2 == kL_K5_2_expected


def test_kauffman_K6_1():
    link_pd = PDCode.from_tuples([
        (8, 2, 9, 1), (12, 3, 1, 4), (10, 5, 11, 6),
        (2, 8, 3, 7), (6, 9, 7, 10), (4, 11, 5, 12)
    ])

    print(link_pd.to_signed_gauss_code())

    link_sgc = link_pd.to_signed_gauss_code()
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K6_1 = kauffman_polynomial(link_sgc).simplify().expand()
    kL_K6_1_expected = (
        (a + a**-1) * z**5
        + (a**2 + 2 + a**-2) * z**4
        + (-3*a - 2*a**-1 + a**-3) * z**3
        + (-3*a**2 - 4 + a**-4) * z**2
        + (2*a + 2*a**-1) * z**1
        + (a**2 + 1 - a**-4) * z**0
    ).simplify().expand()

    print(kL_K6_1)
    print(kL_K6_1_expected)

    assert kL_K6_1 == kL_K6_1_expected


def test_kauffman_K6_2():
    link_pd = PDCode.from_tuples([
        (11, 3, 12, 2), (9, 5, 10, 4), (1, 6, 2, 7),
        (3, 9, 4, 8), (5, 11, 6, 10), (7, 12, 8, 1)
    ])

    print(link_pd.to_signed_gauss_code())

    link_sgc = link_pd.to_signed_gauss_code()
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K6_2 = kauffman_polynomial(link_sgc).simplify().expand()
    kL_K6_2_expected = (
        (a + a**-1)*z**5
        + (a**2 + 3 + 2*a**-2)*z**4
        + (-2*a + 2*a**-3)*z**3
        + (-3*a ** 2 - 6 - 2*a**-2 + a**-4)*z**2
        + (-a**-1 - a**-3)*z**1
        + (2*a**2 + 2 + a**-2)*z**0
    ).simplify().expand()

    print(kL_K6_2)
    print(kL_K6_2_expected)

    assert kL_K6_2 == kL_K6_2_expected


def assert_sg(f: Callable[[SGCode], Poly], sg: SGCode, expected_poly: Poly):
    p = f(sg).simplify().expand()
    expected_poly = expected_poly.simplify().expand()

    print(f"{sg}")
    print(f"Writhe: {sg.writhe()}")
    print(f"Result: {p}")
    print(f"Expected: {expected_poly}")

    assert p == expected_poly


def assert_pd(f: Callable[[SGCode], Poly], pd: PDCode, expected_poly: Poly):
    assert_sg(f, pd.to_signed_gauss_code(), expected_poly)


def test_kauffman_K6_3():
    assert_pd(
        kauffman_polynomial,
        PDCode.from_tuples([
            (8, 1, 9, 2), (6, 4, 7, 3), (12, 6, 1, 5),
            (10, 7, 11, 8), (2, 9, 3, 10), (4, 12, 5, 11)
        ]),
        (a + a**-1)*z**5
        + (2*a**2 + 4 + 2*a**-2)*z**4
        + (a**3 + a + a**-1 + a**-3)*z**3
        + (-3 * a**2 - 6 - 3*a**-2)*z**2
        + (-a**3 - 2*a - 2*a**-1 - a**-3)*z**1
        + (a**2 + 3 + a**-2)*z**0
    )


def test_kauffman_K7_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (1, 9, 2, 8), (3, 11, 4, 10), (5, 13, 6, 12),
            (7, 1, 8, 14), (9, 3, 10, 2), (11, 5, 12, 4),
            (13, 7, 14, 6)
        ]),
        (-3*a**(-8)-4*a**(-6))*z**(0)
        + (a**(-13)-a**(-11)+a**(-9)+3*a**(-7))*z**(1)
        + (a**(-12)-2*a**(-10)+7*a**(-8)+10*a**(-6))*z**(2)
        + (a**(-11)-3*a**(-9)-4*a**(-7))*z**(3)
        + (a**(-10)-5*a**(-8)-6*a**(-6))*z**(4)
        + (a**(-9)+a**(-7))*z**(5)
        + (a**(-8)+a**(-6))*z**(6)
    )


def test_kauffman_K7_2():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [2, 10, 3, 9], [4, 14, 5, 13], [6, 12, 7, 11],
            [8, 2, 9, 1], [10, 8, 11, 7], [12, 6, 13, 5],
            [14, 4, 1, 3]
        ]),
        (-a**(-8)-a**(-6)-a**(-2))*z**(0)
        + (3*a**(-9)+3*a**(-7))*z**(1)
        + (4*a**(-8)+3*a**(-6)+a**(-2))*z**(2)
        + (-4*a**(-9)-6*a**(-7)-a**(-5)+a**(-3))*z**(3)
        + (-4*a**(-8)-3*a**(-6)+a**(-4))*z**(4)
        + (a**(-9)+2*a**(-7)+a**(-5))*z**(5)
        + (a**(-8)+a**(-6))*z**(6)
    )


def test_kauffman_K7_3():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [1, 9, 2, 8], [3, 11, 4, 10], [5, 1, 6, 14],
            [7, 13, 8, 12], [9, 3, 10, 2], [11, 5, 12, 4],
            [13, 7, 14, 6]
        ]),
        (-2*a**(-8)-2*a**(-6)+a**(-4))*z**(0)
        + (-2*a**(-11)+a**(-9)+3*a**(-7))*z**(1)
        + (-a**(-10)+6*a**(-8)+4*a**(-6)-3*a**(-4))*z**(2)
        + (a**(-11)-a**(-9)-4*a**(-7)-2*a**(-5))*z**(3)
        + (a**(-10)-3*a**(-8)-3*a**(-6)+a**(-4))*z**(4)
        + (a**(-9)+2*a**(-7)+a**(-5))*z**(5)
        + (a**(-8)+a**(-6))*z**(6)
    )


def test_kauffman_K7_4():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [2, 10, 3, 9], [4, 12, 5, 11], [6, 14, 7, 13],
            [8, 4, 9, 3], [10, 2, 11, 1], [12, 8, 13, 7],
            [14, 6, 1, 5]
        ]),
        (-a**(-8)+2*a**(-4))*z**(0)+(4*a**(-9)+4*a**(-7))*z**(1)
        + (2*a**(-8)-3*a**(-6)-4*a**(-4)+a**(-2))*z**(2)
        + (-4*a**(-9)-8*a**(-7)-2*a**(-5)+2*a**(-3))*z**(3)
        + (-3*a**(-8)+3*a**(-4))*z**(4)
        + (a**(-9)+3*a**(-7)+2*a**(-5))*z**(5)
        + (a**(-8)+a**(-6))*z**(6)
    )


def test_kauffman_K7_5():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [2, 10, 3, 9], [4, 2, 5, 1], [6, 14, 7, 13],
            [8, 12, 9, 11], [10, 4, 11, 3], [12, 6, 13, 5],
            [14, 8, 1, 7]
        ]),
        (-a**(-8)+2*a**(-4))*z**(0)
        + (-a**(-11)+a**(-9)+a**(-7)-a**(-5))*z**(1)
        + (-2*a**(-10)+a**(-8)-3*a**(-4))*z**(2)
        + (a**(-11)-2*a**(-9)-4*a**(-7)-a**(-5))*z**(3)
        + (2*a**(-10)-a**(-6)+a**(-4))*z**(4)
        + (2*a**(-9)+3*a**(-7)+a**(-5))*z**(5)
        + (a**(-8)+a**(-6))*z**(6)
    )


def test_kauffman_K7_6():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [1, 13, 2, 12], [3, 9, 4, 8], [5, 1, 6, 14],
            [7, 10, 8, 11], [9, 3, 10, 2], [11, 6, 12, 7],
            [13, 5, 14, 4]
        ]),
        (a**(-6)+2*a**(-4)+a**(-2)+1)*z**(0)
        + (-a**(-7)+2*a**(-3)+a**(-1))*z**(1)
        + (-2*a**(-6)-4*a**(-4)-4*a**(-2)-2)*z**(2)
        + (a**(-7)-a**(-5)-6*a**(-3)-4*a**(-1))*z**(3)
        + (2*a**(-6)+2*a**(-4)+a**(-2)+1)*z**(4)
        + (2*a**(-5)+4*a**(-3)+2*a**(-1))*z**(5)
        + (a**(-4)+a**(-2))*z**(6)
    )


def test_kauffman_K7_7():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            [1, 10, 2, 11], [3, 13, 4, 12], [5, 14, 6, 1],
            [7, 5, 8, 4], [9, 2, 10, 3], [11, 9, 12, 8],
            [13, 6, 14, 7]
        ]),
        (2+2*a**2+a**4)*z**(0)
        + (a**(-1)+3*a+2*a**3)*z**(1)
        + (-3*a**(-2)-7-6*a**2-2*a**4)*z**(2)
        + (a**(-3)-3*a**(-1)-8*a-4*a**3)*z**(3)
        + (3*a**(-2)+4+2*a**2+a**4)*z**(4)
        + (3*a**(-1)+5*a+2*a**3)*z**(5)
        + (1+a**2)*z**(6)
    )


def test_kauffman_K8_01():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([[1, 9, 2, 8], [3, 7, 4, 6], [5, 12, 6, 13], [7, 3, 8, 2], [
                           9, 1, 10, 16], [11, 15, 12, 14], [13, 4, 14, 5], [15, 11, 16, 10]]),
        (-a**(-6)-a**(-4)-a**2)*z**(0)
        + (-3*a**(-5)-3*a**(-3))*z**(1)
        + (6*a**(-6)+7*a**(-4)+a**2)*z**(2)
        + (7*a**(-5)+5*a**(-3)-a**(-1)+a)*z**(3)
        + (-5*a**(-6)-8*a**(-4)-2*a**(-2)+1)*z**(4)
        + (-5*a**(-5)-4*a**(-3)+a**(-1))*z**(5)
        + (a**(-6)+2*a**(-4)+a**(-2))*z**(6)
        + (a**(-5)+a**(-3))*z**(7)
    )


def test_kauffman_K8_02():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([[1, 10, 2, 11], [3, 13, 4, 12], [5, 15, 6, 14], [7, 1, 8, 16], [
                           9, 2, 10, 3], [11, 9, 12, 8], [13, 5, 14, 4], [15, 7, 16, 6]]),
        (-a**(-6)-3*a**(-4)-3*a**(-2))*z**(0)
        + (-a**(-9)-a**(-7)+a**(-5)+a**(-3))*z**(1)
        + (a**(-10)-a**(-8)+3*a**(-6)+12*a**(-4)+7*a**(-2))*z**(2)
        + (2*a**(-9)-2*a**(-7)-a**(-5)+3*a**(-3))*z**(3)
        + (2*a**(-8)-5*a**(-6)-12*a**(-4)-5*a**(-2))*z**(4)
        + (2*a**(-7)-2*a**(-5)-4*a**(-3))*z**(5)
        + (2*a**(-6)+3*a**(-4)+a**(-2))*z**(6)
        + (a**(-5)+a**(-3))*z**(7)
    )


def test_kauffman_K8_03():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([[6, 2, 7, 1], [14, 10, 15, 9], [10, 5, 11, 6], [12, 3, 13, 4], [
                           4, 11, 5, 12], [2, 13, 3, 14], [16, 8, 1, 7], [8, 16, 9, 15]]),
        (a**(-4)-1+a**4)*z**(0)
        + (-4*a**(-1)-4*a)*z**(1)
        + (-3*a**(-4)+a**(-2)+8+a**2-3*a**4)*z**(2)
        + (-2*a**(-3)+8*a**(-1)+8*a-2*a**3)*z**(3)
        + (a**(-4)-2*a**(-2)-6-2*a**2+a**4)*z**(4)
        + (a**(-3)-4*a**(-1)-4*a+a**3)*z**(5)
        + (a**(-2)+2+a**2)*z**(6)
        + (a**(-1)+a)*z**(7)
    )

#
# Classical Links from KnotInfo
#


def test_kauffman_L2a1_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (4, 1, 3, 2), (2, 3, 1, 4)
        ]),
        a ** 2 - a / z - a ** 3 / z + a * z + a ** 3 * z
    )


def test_kauffman_L2a1_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (4, 2, 3, 1), (2, 4, 1, 3)
        ]),
        a ** (-2) - 1 / (a ** 3 * z) - 1 / (a * z) + z / a ** 3 + z / a
    )


def test_kauffman_L4a1_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (6, 1, 7, 2), (8, 3, 5, 4), (2, 5, 3, 6), (4, 7, 1, 8)
        ]),
        -a**4 + a**3/z + a**5/z + a*z-2*a**3*z-3*a**5*z +
        a**2*z**2 + a**4*z**2 + a**3*z**3 + a**5*z**3
    )


def test_kauffman_L4a1_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (6, 2, 7, 1), (8, 4, 5, 3), (2, 8, 3, 7), (4, 6, 1, 5)
        ]),
        -a**(-4) + 1/(a**5*z) + 1/(a**3*z) + z/a**7-(2*z)/a**5 -
        (3*z)/a**3 + z**2/a**6 + z**2/a**4 + z**3/a**5 + z**3/a**3
    )


def test_kauffman_L5a1_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (6, 1, 7, 2), (10, 7, 5, 8), (4, 5, 1, 6), (2, 10, 3, 9), (8, 4, 9, 3)
        ]),
        -1 + 1/(a*z) + a/z-(2*z)/a-4*a*z-2*a**3*z-z**2 + a**4*z**2 +
        z**3/a + 3*a*z**3 + 2*a**3*z**3 + z**4 + a**2*z**4
    )


def test_kauffman_L5a1_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (8, 2, 9, 1), (10, 7, 5, 8), (4, 10, 1, 9), (2, 5, 3, 6), (6, 3, 7, 4)
        ]),
        -1 + 1/(a*z) + a/z - (2*z)/a - 4*a*z - 2*a**3*z - z**2 + a**4*z**2 +
        z**3/a + 3*a*z**3 + 2*a**3*z**3 + z**4 + a**2*z**4
    )


def test_kauffman_L6a1_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (6, 1, 7, 2), (10, 3, 11, 4), (12, 8, 5, 7), (8, 12, 9, 11),
            (2, 5, 3, 6), (4, 9, 1, 10)
        ]),
        -a**4 + a**3/z + a**5/z - z/a - a**3*z - 2*a**5*z - 3*z**2 -
        3*a**2*z**2 + z**3/a + a**5*z**3 + 2*z**4 + 3*a**2*z**4 +
        a**4*z**4 + a*z**5 + a**3*z**5
    )


def test_kauffman_L6a1_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (10, 2, 11, 1), (6, 4, 7, 3), (12, 10, 5, 9), (8, 6, 9, 5),
            (2, 12, 3, 11), (4, 8, 1, 7)
        ]),
        -a**(-4) + 1/(a**5*z) + 1/(a**3*z) - z/a**9 - z/a**5 - (2*z)/a**3 -
        (3*z**2)/a**8 - (3*z**2)/a**6 + z**3/a**9 + z**3/a**3 +
        (2*z**4)/a**8 + (3*z**4)/a**6 + z**4/a**4 + z**5/a**7 + z**5/a**5
    )


def test_kauffman_L6a2_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (8, 1, 9, 2), (12, 5, 7, 6), (10, 3, 11, 4), (4, 11, 5, 12),
            (2, 7, 3, 8), (6, 9, 1, 10)
        ]),
        a**6 - a**5/z - a**7/z - 2*a**3*z + 3*a**5*z + 3*a**7*z - 2*a**9*z -
        a**4*z**2 - 2*a**6*z**2 - a**8*z**2 + a**3*z**3 - 2*a**5*z**3 -
        2*a**7*z**3 + a**9*z**3 + a**4*z**4 + 2*a**6*z**4 + a**8*z**4 +
        a**5*z**5 + a**7*z**5
    )


def test_kauffman_L6a2_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (10, 2, 11, 1), (12, 6, 7, 5), (8, 4, 9, 3), (4, 8, 5, 7),
            (2, 12, 3, 11), (6, 10, 1, 9)
        ]),
        a**(-6) - 1/(a**7*z) - 1/(a**5*z) - (2*z)/a**9 + (3*z)/a**7 +
        (3*z)/a**5 - (2*z)/a**3 - z**2/a**8 - (2*z**2)/a**6 - z**2/a**4 +
        z**3/a**9 - (2*z**3)/a**7 - (2*z**3)/a**5 + z**3/a**3 + z**4/a**8 +
        (2*z**4)/a**6 + z**4/a**4 + z**5/a**7 + z**5/a**5
    )


def test_kauffman_L6a3_0():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (8, 1, 9, 2), (2, 9, 3, 10), (10, 3, 11, 4), (12, 5, 7, 6),
            (6, 7, 1, 8), (4, 11, 5, 12)
        ]),
        a**6 - a**5/z - a**7/z + 6*a**5*z + 4*a**7*z - a**9*z + a**11*z -
        3*a**6*z**2 - 2*a**8*z**2 + a**10*z**2 - 5*a**5*z**3 - 4*a**7*z**3 +
        a**9*z**3 + a**6*z**4 + a**8*z**4 + a**5*z**5 + a**7*z**5
    )


def test_kauffman_L6a3_1():
    assert_pd(
        f_polynomial,
        PDCode.from_tuples([
            (10, 2, 11, 1), (2, 10, 3, 9), (8, 4, 9, 3), (12, 6, 7, 5),
            (6, 12, 1, 11), (4, 8, 5, 7)
        ]),
        a**(-6) - 1/(a**7*z) - 1/(a**5*z) + (6*z)/a**7 + (4*z)/a**5 -
        z/a**3 + z/a - (3*z**2)/a**6 - (2*z**2)/a**4 + z**2/a**2 -
        (5*z**3)/a**7 - (4*z**3)/a**5 + z**3/a**3 + z**4/a**6 + z**4/a**4 +
        z**5/a**7 + z**5/a**5
    )


# def test_kauffman_L6a4_0_0_part_1():
#     assert_sg(
#         f_polynomial,
#         SGCode.from_tuples([
#             [
#                 (+4, -1), (+1, +1), (+2, +1), (-5, +1),
#             ],
#             [
#                 (-6, +1), (-4, -1), (+3, +1), (-2, +1),
#             ],
#             [
#                 (-1, +1), (+6, +1), (+5, +1), (-3, +1),
#             ]
#         ]),
#         # correct?
#         z/a - 2/(a*z) + 1/(a*z**3) - z**2/a**2 + 4/a**2 - 3/(a**2*z**2) + z/a**3 - 3/(a**3*z) + 3/(a**3*z**3) - 2*z**2/a**4 + 7/a**4 -
#         6/(a**4*z**2) + z/a**5 - 3/(a**5*z) + 3/(a**5*z**3) - z**2/a**6 +
#         4/a**6 - 3/(a**6*z**2) + z/a**7 - 2/(a**7*z) + 1/(a**7*z**3)
#     )

# # broken


# # [[+1⁻, -6⁻, +5⁺, -3⁺], [+4⁻, -1⁻, +2⁺, -5⁺], [+6⁻, -4⁻, +3⁺, -2⁺]]
# def test_kauffman_L6a4_0_0():
#     assert_pd(
#         f_polynomial,
#         PDCode.from_tuples([
#             (6, 1, 7, 2), (12, 8, 9, 7), (4, 12, 1, 11), (10, 5, 11, 6),
#             (8, 4, 5, 3), (2, 9, 3, 10)
#         ]),
#         1 + 2/z**2 + 1/(a**2*z**2) + a**2/z**2 - 2/(a*z) - (2*a)/z -
#         8*z**2 - (4*z**2)/a**2 - 4*a**2*z**2 + z**3/a**3 - z**3/a -
#         a*z**3 + a**3*z**3 + 6*z**4 + (3*z**4)/a**2 + 3*a**2*z**4 +
#         (2*z**5)/a + 2*a*z**5
#     )


# def test_kauffman_L6a4_1_0():
#     assert_pd(
#         f_polynomial,
#         PDCode.from_tuples([
#             (6, 2, 7, 1), (12, 5, 9, 6), (4, 12, 1, 11), (10, 8, 11, 7),
#             (8, 3, 5, 4), (2, 9, 3, 10)
#         ]),
#         1 + 2/z**2 + 1/(a**2*z**2) + a**2/z**2 - 2/(a*z) - (2*a)/z -
#         8*z**2 - (4*z**2)/a**2 - 4*a**2*z**2 + z**3/a**3 - z**3/a -
#         a*z**3 + a**3*z**3 + 6*z**4 + (3*z**4)/a**2 + 3*a**2*z**4 +
#         (2*z**5)/a + 2*a*z**5
#     )


# def test_kauffman_L6a4_0_1():
#     assert_pd(
#         f_polynomial,
#         PDCode.from_tuples([
#             (6, 1, 7, 2), (12, 7, 9, 8), (4, 9, 1, 10), (10, 6, 11, 5),
#             (8, 4, 5, 3), (2, 12, 3, 11)
#         ]),
#         1 + 2/z**2 + 1/(a**2*z**2) + a**2/z**2 - 2/(a*z) - (2*a)/z -
#         8*z**2 - (4*z**2)/a**2 - 4*a**2*z**2 + z**3/a**3 - z**3/a -
#         a*z**3 + a**3*z**3 + 6*z**4 + (3*z**4)/a**2 + 3*a**2*z**4 +
#         (2*z**5)/a + 2*a*z**5
#     )


# def test_kauffman_L6a4_1_1():
#     assert_pd(
#         f_polynomial,
#         PDCode.from_tuples([
#             (6, 2, 7, 1), (12, 6, 9, 5), (4, 9, 1, 10), (10, 7, 11, 8),
#             (8, 3, 5, 4), (2, 12, 3, 11)
#         ]),
#         1 + 2/z**2 + 1/(a**2*z**2) + a**2/z**2 - 2/(a*z) - (2*a)/z -
#         8*z**2 - (4*z**2)/a**2 - 4*a**2*z**2 + z**3/a**3 - z**3/a -
#         a*z**3 + a**3*z**3 + 6*z**4 + (3*z**4)/a**2 + 3*a**2*z**4 +
#         (2*z**5)/a + 2*a*z**5
#     )

def test_kauffman_K8_18_1():
    link_pd = PDCode.from_tuples([
        # Untangle
        (12, 2, 13, 1), (14, 3, 15, 4), (16, 6, 1, 5), (2, 7, 3, 8),
        (4, 10, 5, 9), (6, 11, 7, 12), (8, 14, 9, 13), (10, 15, 11, 16)

        # KnotInfo
        # (6, 2, 7, 1), (8, 3, 9, 4), (16, 11, 1, 12), (2, 14, 3, 13),
        # (4, 15, 5, 16), (10, 6, 11, 5), (12, 7, 13, 8), (14, 10, 15, 9)
    ])

    print(link_pd.to_signed_gauss_code())

    link_sgc = link_pd.to_signed_gauss_code()
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K8_18 = kauffman_polynomial(link_sgc).simplify().expand()
    kL_K8_18_expected = (
        z**7 * (3*a + 3*a**-1)
        + z**6 * (6*a**2 + 12 + 6*a**-2)
        + z**5 * (4*a**3 + 3*a + 3*a**-1 + 4*a**-3)
        + z**4 * (a**4 - 9*a**2 - 20 - 9*a**-2 + a**-4)
        + z**3 * (-4*a**3 - 9*a - 9*a**-1 - 4*a**-3)
        + z**2 * (3*a**2 + 6 + 3*a**-2)
        + z**1 * (a + a**-1)
        + z**0 * (a**2 + 3 + a**-2)
    ).simplify().expand()

    print(kL_K8_18)
    print(kL_K8_18_expected)

    # a**5*z**3 - 3*a**5*z + 3*a**5/z - a**5/z**3 - 3*a**4*z**4 + 13*a**4*z**2 - 14*a**4 + 5*a**4/z**2 + 7*a**3*z**5 - 16*a**3*z**3 + 9*a**3*z + 5*a**3/z - 5*a**3/z**3 + 6*a**2*z**6 - 17*a**2*z**4 + 37*a**2*z**2 - 46*a**2 + 20*a**2/z**2 + 3*a*z**7 + 12*a*z**5 - 45*a*z**3 + 40*a*z - 10*a/z**3 + 12*z**6 - 28*z**4 + 48*z**2 - 63 + 30/z**2 + 3*z**7/a + 12*z**5/a - 45*z**3/a + 40*z/a - 10/(a*z**3) + 6*z**6/a**2 - 17*z**4/a**2 + 37*z**2/a**2 - 46/a**2 + 20/(a**2*z**2) + 7*z**5/a**3 - 16*z**3/a**3 + 9*z/a**3 + 5/(a**3*z) - 5/(a**3*z**3) - 3*z**4/a**4 + 13*z**2/a**4 - 14/a**4 + 5/(a**4*z**2) + z**3/a**5 - 3*z/a**5 + 3/(a**5*z) - 1/(a**5*z**3)

    assert kL_K8_18 == kL_K8_18_expected


# def test_kauffman_K8_18_2():
#     link_pd = PDCode.from_tuples([
#         # Untangle
#         # (12, 2, 13, 1), (14, 3, 15, 4), (16, 6, 1, 5), (2, 7, 3, 8),
#         # (4, 10, 5, 9), (6, 11, 7, 12), (8, 14, 9, 13), (10, 15, 11, 16)

#         # KnotInfo
#         (6, 2, 7, 1), (8, 3, 9, 4), (16, 11, 1, 12), (2, 14, 3, 13),
#         (4, 15, 5, 16), (10, 6, 11, 5), (12, 7, 13, 8), (14, 10, 15, 9)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()
#     print(link_sgc)
#     print(f"write: {link_sgc.writhe()}")

#     kL_K8_18 = kauffman_polynomial(link_sgc).simplify().expand()
#     kL_K8_18_expected = (
#         z**7 * (3*a + 3*a**-1)
#         + z**6 * (6*a**2 + 12 + 6*a**-2)
#         + z**5 * (4*a**3 + 3*a + 3*a**-1 + 4*a**-3)
#         + z**4 * (a**4 - 9*a**2 - 20 - 9*a**-2 + a**-4)
#         + z**3 * (-4*a**3 - 9*a - 9*a**-1 - 4*a**-3)
#         + z**2 * (3*a**2 + 6 + 3*a**-2)
#         + z**1 * (a + a**-1)
#         + z**0 * (a**2 + 3 + a**-2)
#     ).simplify().expand()

#     print(kL_K8_18)
#     print(kL_K8_18_expected)

#     # a**4*z**4 + 4*a**3*z**5 - 4*a**3*z**3 + 6*a**2*z**6 - 8*a**2*z**4 + a**2*z**2 + 2*a**2 + 3*a*z**7 + a*z**5 - 3*a*z**3 - 3*a*z + 12*z**6 - 21*z**4 + 5*z**2 + 6 + 3*z**7/a - z**5/a + z**3/a - 7*z/a + 6*z**6/a**2 - 10*z**4/a**2 + 2*z**2/a**2 + 4/a**2 + 2*z**5/a**3 + 2*z**3/a**3 - 4*z/a**3 + 2*z**4/a**4 - 2*z**2/a**4 + a**(-4)

#     assert kL_K8_18 == kL_K8_18_expected


def test_kauffman_K8_18_3():
    link_sgc = SGCode.from_tuples([
        [
            (+1, +1),
            (-2, -1),
            (+3, -1),
            (-4, +1),
            (+5, +1),
            (-6, -1),
            (+2, -1),
            (-7, +1),
            (+4, +1),
            (-8, -1),
            (+6, -1),
            (-1, +1),
            (+7, +1),
            (-3, -1),
            (+8, -1),
            (-5, +1),
        ]
    ])
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    kL_K8_18 = kauffman_polynomial(link_sgc).simplify().expand()
    kL_K8_18_expected = (
        z**7 * (3*a + 3*a**-1)
        + z**6 * (6*a**2 + 12 + 6*a**-2)
        + z**5 * (4*a**3 + 3*a + 3*a**-1 + 4*a**-3)
        + z**4 * (a**4 - 9*a**2 - 20 - 9*a**-2 + a**-4)
        + z**3 * (-4*a**3 - 9*a - 9*a**-1 - 4*a**-3)
        + z**2 * (3*a**2 + 6 + 3*a**-2)
        + z**1 * (a + a**-1)
        + z**0 * (a**2 + 3 + a**-2)
    ).simplify().expand()

    print(kL_K8_18)
    print(kL_K8_18_expected)

    # a**5*z**3 - 3*a**5*z + 3*a**5/z - a**5/z**3 - 3*a**4*z**4 + 13*a**4*z**2 - 14*a**4 + 5*a**4/z**2 + 7*a**3*z**5 - 16*a**3*z**3 + 9*a**3*z + 5*a**3/z - 5*a**3/z**3 + 6*a**2*z**6 - 17*a**2*z**4 + 37*a**2*z**2 - 46*a**2 + 20*a**2/z**2 + 3*a*z**7 + 12*a*z**5 - 45*a*z**3 + 40*a*z - 10*a/z**3 + 12*z**6 - 28*z**4 + 48*z**2 - 63 + 30/z**2 + 3*z**7/a + 12*z**5/a - 45*z**3/a + 40*z/a - 10/(a*z**3) + 6*z**6/a**2 - 17*z**4/a**2 + 37*z**2/a**2 - 46/a**2 + 20/(a**2*z**2) + 7*z**5/a**3 - 16*z**3/a**3 + 9*z/a**3 + 5/(a**3*z) - 5/(a**3*z**3) - 3*z**4/a**4 + 13*z**2/a**4 - 14/a**4 + 5/(a**4*z**2) + z**3/a**5 - 3*z/a**5 + 3/(a**5*z) - 1/(a**5*z**3)

    assert kL_K8_18 == kL_K8_18_expected
