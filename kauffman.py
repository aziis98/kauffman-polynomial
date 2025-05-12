from codes import SignedGaussCode
from sympy import symbols

from utils import log_input_output, depth_print

from functools import cache

a, z = symbols("a z")
d = (a + 1 / a) / z - 1


@log_input_output
@cache
def kauffman_polynomial(link: SignedGaussCode):
    depth_print("[i] not cached...")

    if len(link.components) == 0:
        return 0

    disconnected_components = [*link.unlinked_components().keys()]

    assert len(disconnected_components) > 0

    if len(disconnected_components) == 1:
        single_linked_component = disconnected_components[0]
        unknotting_seq = link.std_unknot_switching_sequence()

        if len(unknotting_seq) == 0:
            # if the link is in its standard unknot form
            depth_print("[i] standard unknot form")
            return a ** link.writhe()
        else:
            # there is a single tangle, cases based on how many strands there are
            if len(single_linked_component) == 1:
                depth_print("[i] single knotted component")
                unknotting_seq_rev = unknotting_seq[::-1]
                link_rev = link.reverse()

                return ((
                    (-1) ** (len(unknotting_seq) + 1)
                    * kauffman_polynomial(link.apply_switching_sequence(unknotting_seq))
                    + z * sum_switches(link, unknotting_seq)
                ) + (
                    (-1) ** (len(unknotting_seq_rev) + 1)
                    * kauffman_polynomial(link_rev.apply_switching_sequence(unknotting_seq_rev))
                    + z * sum_switches(link_rev, unknotting_seq_rev)
                )) / 2
            else:
                depth_print("[i] multiple linked components")
                result = 0

                for i in single_linked_component:
                    target_component, others, seq = link.split_component(i)

                    result += (
                        (-1) ** (len(seq) + 1) * d
                        * kauffman_polynomial(target_component)
                        * kauffman_polynomial(others)
                    ) + (
                        z * sum_switches(link, seq)
                    )

                    seq_rev = seq[::-1]

                    result += (
                        (-1) ** (len(seq_rev) + 1) * d
                        * kauffman_polynomial(target_component.reverse())
                        * kauffman_polynomial(others)
                    ) + (
                        z * sum_switches(link.reverse(ids=[i]), seq_rev)
                    )

                return result / (2 * len(single_linked_component))
    else:
        depth_print("[i] multiple unlinked components")

        result = 1
        for k, component_ids in enumerate(disconnected_components):
            new_link = SignedGaussCode(
                [link.components[i] for i in component_ids]
            )

            if k > 0:
                result *= d

            result *= kauffman_polynomial(new_link)

        return result


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


@log_input_output
def sum_switches(link: SignedGaussCode, switching_seq: list[int]):
    result = 0

    # this is from 0 to the last switch in switching_seq
    for i in range(len(switching_seq)):
        switched_link = link.apply_switching_sequence(switching_seq[:i + 1])

        result += (
            ((-1) ** i) * (kauffman_polynomial(switched_link.splice_h(switching_seq[i]))
                           + kauffman_polynomial(switched_link.splice_v(switching_seq[i])))
        )

    return result
