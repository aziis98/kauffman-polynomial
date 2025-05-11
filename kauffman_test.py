from codes import SignedGaussCode, PDCode
from kauffman import kauffman_polynomial
from sympy import symbols, poly, simplify, init_printing


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing(use_unicode=True)


def test_kauffman_trivial():
    # single unknot
    link_sgc = SignedGaussCode.from_tuples([[]])

    assert kauffman_polynomial(link_sgc) == 1


def test_kauffman_trivial_2():
    # two unknots
    link_sgc = SignedGaussCode.from_tuples([[], []])

    assert kauffman_polynomial(link_sgc) == d


def test_kauffman_trivial_2():
    # three unknots
    link_sgc = SignedGaussCode.from_tuples([[], [], []])

    assert kauffman_polynomial(link_sgc) == d * d


def test_kauffman_infinity():
    """
    Test the Kauffman polynomial for the infinity link and its mirror
    """

    assert kauffman_polynomial(
        SignedGaussCode.from_tuples(
            [[(1, +1), (-1, +1)]]
        )
    ) == a ** +1

    assert kauffman_polynomial(
        SignedGaussCode.from_tuples(
            [[(1, -1), (-1, -1)]]
        )
    ) == a ** -1


def test_kauffman_hopf():
    # hopf
    link_sgc = SignedGaussCode.from_tuples([
        [(-1, -1), (+2, -1)],
        [(+1, -1), (-2, -1)],
    ])

    L_hopf = simplify(kauffman_polynomial(link_sgc))

    print(L_hopf)

    assert L_hopf == -(a + 1/a)/z + 1 + (a + 1/a)*z
