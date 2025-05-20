from codes import SGCode, PDCode
from kauffman import kauffman_polynomial
from sympy import symbols, poly, simplify, init_printing, factor


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing(use_unicode=True)


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


def test_kauffman_trefoil():
    # trefoil
    link_sgc = SGCode.from_tuples([
        [(+1, +1), (-2, +1), (+3, +1),
         (-1, +1), (+2, +1), (-3, +1)]
    ])

    L_trefoil = factor(simplify(kauffman_polynomial(link_sgc)), z)
    print(L_trefoil)

    assert L_trefoil == ((-2*a - a**(-1)) + (1 + a**(-2))
                         * z + (a + a**(-1))*z**2).simplify()
