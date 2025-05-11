from codes import SignedGaussCode
from kauffman import kauffman_polynomial
from sympy import symbols

a, z = symbols("a z")


def test_kauffman_trivial():
    link_sgc = SignedGaussCode.from_tuples([])

    assert kauffman_polynomial(link_sgc) == a ** 0


def test_kauffman_infinity():
    link_sgc = SignedGaussCode.from_tuples([[(1, -1), (-1, -1)]])

    assert kauffman_polynomial(link_sgc) == a ** -1
