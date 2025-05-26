from codes import SGCode, PDCode
from kauffman_closed import kauffman_polynomial
from sympy import symbols, poly, simplify, init_printing, factor


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

    assert kauffman_polynomial(link_sgc) == d


def test_kauffman_trivial_3():
    # three unknots
    link_sgc = SGCode.from_tuples([[], [], []])

    assert kauffman_polynomial(link_sgc) == d * d


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


# def test_kauffman_K4_1():
#     # figure-8
#     # link_pd = PDCode.from_tuples([
#     #     (4, 2, 5, 1), (8, 6, 1, 5), (6, 3, 7, 4), (2, 7, 3, 8)
#     # ])

#     # print(link_pd.to_signed_gauss_code())

#     link_sgc = SGCode.from_tuples([
#         [(1, 1), (-4, -1), (3, -1), (-1, 1), (2, 1), (-3, -1), (4, -1), (-2, 1)]
#     ])

#     L_figure8 = kauffman_polynomial(link_sgc)
#     L_figure8_expected = (
#         (a + a**(-1))*z**3 + (a**2 + 2 + a**(-2))*z**2 +
#         (-a - a**(-1))*z**1 + (-a**2 - 1 - a**(-2))*z**0
#     )

#     assert L_figure8.expand() == L_figure8_expected.expand()


# def test_kauffman_K5_1():
#     link_pd = PDCode.from_tuples([
#         (2, 8, 3, 7), (4, 10, 5, 9), (6, 2, 7, 1), (8, 4, 9, 3), (10, 6, 1, 5)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()

#     kL_K5_1 = kauffman_polynomial(link_sgc)
#     kL_K5_1_expected = (
#         z**4 * (a + a**(-1)) +
#         z**3 * (1 + a**(-2)) +
#         z**2 * (-4*a - 3*a**(-1) + a**(-3)) +
#         z**1 * (-2 - a**(-2) + a**(-4)) +
#         z**0 * (3*a + 2*a**(-1))
#     )

#     assert kL_K5_1.expand() == kL_K5_1_expected.expand()


# def test_kauffman_K5_2():
#     link_pd = PDCode.from_tuples([
#         (8, 2, 9, 1), (10, 7, 5, 8), (4, 10, 1, 9), (2, 5, 3, 6), (6, 3, 7, 4)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()

#     kL_K5_2 = kauffman_polynomial(link_sgc)
#     kL_K5_2_expected = (
#         z**4 * (a + a**(-1)) +
#         z**3 * (a**2 + 2 + a**(-2)) +
#         z**2 * (-2*a - a**(-1) + a**(-3)) +
#         z**1 * (-2*a**2 - 2) +
#         z**0 * (a + a**(-1) - a**(-3))
#     )

#     assert kL_K5_2.expand() == kL_K5_2_expected.expand()

# def test_kauffman_K6_1():
#     link_pd = PDCode.from_tuples([
#         (1, 7, 2, 6), (3, 10, 4, 11), (5, 3, 6, 2),
#         (7, 1, 8, 12), (9, 4, 10, 5), (11, 9, 12, 8)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()

#     kL_K6_1 = kauffman_polynomial(link_sgc)
#     kL_K6_1_expected = (
#         (a + a**-1) * z**5
#         + (a**2 + 2 + a**-2) * z**4
#         + (-3*a - 2*a**-1 + a**-3) * z**3
#         + (-3*a**2 - 4 + a**-4) * z**2
#         + (2*a + 2*a**-1) * z**1
#         + (a**2 + 1 - a**-4) * z**0
#     )

#     assert kL_K6_1.expand() == kL_K6_1_expected.expand()


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


# def test_kauffman_K5_2():
#     link_pd = PDCode.from_tuples([
#         (4, 7, 5, 8), (6, 1, 7, 2), (10, 5, 1, 6), (8, 3, 9, 4), (2, 9, 3, 10)
#     ])

#     link_sgc = link_pd.to_signed_gauss_code()
#     print(link_sgc)
#     print(f"write: {link_sgc.writhe()}")

#     kL_K5_2 = kauffman_polynomial(link_sgc).simplify().expand()
#     kL_K5_2_expected = (
#         z**4 * (a + a**(-1)) +
#         z**3 * (a**2 + 2 + a**(-2)) +
#         z**2 * (-2*a - a**(-1) + a**(-3)) +
#         z**1 * (-2*a**2 - 2) +
#         z**0 * (a + a**(-1) - a**(-3))
#     ).simplify().expand()

#     print(kL_K5_2)
#     print(kL_K5_2_expected)

#     assert kL_K5_2 == kL_K5_2_expected


# def test_kauffman_K6_1():
#     link_pd = PDCode.from_tuples([
#         (8, 2, 9, 1), (12, 3, 1, 4), (10, 5, 11, 6),
#         (2, 8, 3, 7), (6, 9, 7, 10), (4, 11, 5, 12)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()
#     print(link_sgc)
#     print(f"write: {link_sgc.writhe()}")

#     kL_K6_1 = kauffman_polynomial(link_sgc).simplify().expand()
#     kL_K6_1_expected = (
#         (a + a**-1) * z**5
#         + (a**2 + 2 + a**-2) * z**4
#         + (-3*a - 2*a**-1 + a**-3) * z**3
#         + (-3*a**2 - 4 + a**-4) * z**2
#         + (2*a + 2*a**-1) * z**1
#         + (a**2 + 1 - a**-4) * z**0
#     ).simplify().expand()

#     print(kL_K6_1)
#     print(kL_K6_1_expected)

#     assert kL_K6_1 == kL_K6_1_expected


# def test_kauffman_K6_2():
#     link_pd = PDCode.from_tuples([
#         (11, 3, 12, 2), (9, 5, 10, 4), (1, 6, 2, 7),
#         (3, 9, 4, 8), (5, 11, 6, 10), (7, 12, 8, 1)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()
#     print(link_sgc)
#     print(f"write: {link_sgc.writhe()}")

#     kL_K6_2 = kauffman_polynomial(link_sgc).simplify().expand()
#     kL_K6_2_expected = (
#         (a + a**-1)*z**5
#         + (a**2 + 3 + 2*a**-2)*z**4
#         + (-2*a + 2*a**-3)*z**3
#         + (-3*a ** 2 - 6 - 2*a**-2 + a**-4)*z**2
#         + (-a**-1 - a**-3)*z**1
#         + (2*a**2 + 2 + a**-2)*z**0
#     ).simplify().expand()

#     print(kL_K6_2)
#     print(kL_K6_2_expected)

#     assert kL_K6_2 == kL_K6_2_expected


# def test_kauffman_K6_3():
#     link_pd = PDCode.from_tuples([
#         (8, 1, 9, 2), (6, 4, 7, 3), (12, 6, 1, 5),
#         (10, 7, 11, 8), (2, 9, 3, 10), (4, 12, 5, 11)
#     ])

#     print(link_pd.to_signed_gauss_code())

#     link_sgc = link_pd.to_signed_gauss_code()
#     print(link_sgc)
#     print(f"write: {link_sgc.writhe()}")

#     kL_K6_3 = kauffman_polynomial(link_sgc).simplify().expand()
#     kL_K6_3_expected = (
#         (a + a**-1)*z**5
#         + (2*a**2 + 4 + 2*a**-2)*z**4
#         + (a**3 + a + a**-1 + a**-3)*z**3
#         + (-3 * a**2 - 6 - 3*a**-2)*z**2
#         + (-a**3 - 2*a - 2*a**-1 - a**-3)*z**1
#         + (a**2 + 3 + a**-2)*z**0
#     ).simplify().expand()

#     print(kL_K6_3)
#     print(kL_K6_3_expected)

#     assert kL_K6_3 == kL_K6_3_expected
