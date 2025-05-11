# from polynomials import var, Polynomial

from codes import SignedGaussCode


# a = var("a")
# z = var("z")

from sympy import symbols, Poly, poly

a, z = symbols("a z")

# increasing lists for l
# [l[:i+1] for i in range(len(l))]


def kauffman_polynomial(link: SignedGaussCode):
    unknotting_seq = link.std_unknot_switching_sequence()
    if len(unknotting_seq) == 0:
        return a ** link.writhe()
    else:
        pass


def move_A(link: SignedGaussCode, switching_seq: list[int], index: int) -> SignedGaussCode:
    return (
        link.apply_switching_sequence(switching_seq[:index])
            .splice_h(switching_seq[index])
    )


def move_B(link: SignedGaussCode, switching_seq: list[int], index: int) -> SignedGaussCode:
    return (
        link.apply_switching_sequence(switching_seq[:index])
            .splice_v(switching_seq[index])
    )


def sum_switches(link: SignedGaussCode, switching_seq: list[int]):
    result = 1

    # this is from 0 to the last switch in switching_seq
    for i in range(len(switching_seq)):
        switched_link = link.apply_switching_sequence(switching_seq[:i + 1])

        result += (
            ((-1) ** i) * (kauffman_polynomial(switched_link.splice_h(switching_seq[i]))
                           + kauffman_polynomial(switched_link.splice_v(switching_seq[i])))
        )

    return result
