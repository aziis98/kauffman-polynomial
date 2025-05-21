from codes import SGCode
from sympy import symbols, Poly

from utils import log_input_output, depth_print, rotate_to_minimal

from functools import cache, wraps

a, z = symbols("a z")
d = (a + 1 / a) / z - 1


def prepare_link(func):
    @wraps(func)
    def wrapper(link: SGCode):
        # return func(link.to_minimal())
        return func(link)

    return wrapper


@log_input_output
@cache
@prepare_link
def kauffman_polynomial(link: SGCode) -> Poly:
    depth_print("ℹ️  not cached...")

    if len(link.components) == 0:
        return 0

    disconnected_components = [*link.unlinked_components().keys()]

    assert len(disconnected_components) > 0

    if len(disconnected_components) == 1:
        single_linked_component = disconnected_components[0]

        unknotting_seq = link.std_unknot_switching_sequence()

        link_rev = link.reverse()
        unknotting_seq_rev = link_rev.std_unknot_switching_sequence()

        if len(unknotting_seq) == 0 or len(unknotting_seq_rev) == 0:
            # if the link is in its standard unknot form
            depth_print("ℹ️  standard unknot form")
            return a ** link.writhe()
        else:
            # there is a single tangle, cases based on how many strands there are
            if len(single_linked_component) == 1:
                depth_print("ℹ️  single knotted component")

                pm_sign = (-1) ** len(unknotting_seq)
                depth_print(
                    f"ℹ️  unknotting seq: {unknotting_seq!r}, sign: {pm_sign}"
                )

                result = (
                    pm_sign
                    * kauffman_polynomial(link.apply_switching_sequence(unknotting_seq)).simplify()
                    + z * sum_switches(link, unknotting_seq)
                )

                pm_sign = (-1) ** len(unknotting_seq_rev)
                depth_print(
                    f"ℹ️  unknotting seq rev: {unknotting_seq_rev!r}, sign: {pm_sign}"
                )

                result_rev = (
                    pm_sign
                    * kauffman_polynomial(link_rev.apply_switching_sequence(unknotting_seq_rev)).simplify()
                    + z * sum_switches(link_rev, unknotting_seq_rev)
                )

                return (result + result_rev) / 2
            else:
                depth_print("ℹ️  multiple linked components")
                result = 0

                for i in single_linked_component:
                    component_result = 0

                    link_part, others, seq = link.split_component(i)

                    pm_sign = (-1) ** len(seq)
                    depth_print(f"ℹ️  sign: {pm_sign}")

                    component_result += (
                        pm_sign * d
                        * kauffman_polynomial(link_part).simplify()
                        * kauffman_polynomial(others).simplify()
                    ) + (
                        z * sum_switches(link, seq)
                    )

                    link_rev = link.reverse(ids=[i])
                    link_part, others, seq = link_rev.split_component(i)

                    pm_sign = (-1) ** len(seq)
                    depth_print(f"ℹ️  sign: {pm_sign}")

                    component_result += (
                        pm_sign * d
                        * kauffman_polynomial(link_part).simplify()
                        * kauffman_polynomial(others).simplify()
                    ) + (
                        z * sum_switches(link_rev, seq)
                    )

                    depth_print(
                        f"ℹ️  component {i} ~> {component_result}")

                    result += component_result

                depth_print(
                    f"ℹ️  final result = {result} / (2 * {len(single_linked_component)})"
                )

                return result / (2 * len(single_linked_component))
    else:
        depth_print("ℹ️  multiple unlinked components")

        result = 1
        for k, component_ids in enumerate(disconnected_components):
            own_crossings = set(
                crossing.id
                for i in component_ids
                for crossing in link.components[i]
                if crossing.is_over()
            ).intersection(
                set(
                    crossing.id
                    for i in component_ids
                    for crossing in link.components[i]
                    if crossing.is_under()
                )
            )

            new_link = SGCode(
                [
                    [
                        c
                        for c in link.components[i]
                        if c.id in own_crossings
                    ]
                    for i in component_ids
                ]
            )

            if k > 0:
                result *= d

            result *= kauffman_polynomial(new_link).simplify()

        return result


def move_A(link: SGCode, switching_seq: list[int], index: int) -> SGCode:
    return (
        link.apply_switching_sequence(switching_seq[:index])
            .splice_h(switching_seq[index])
    )


def move_B(link: SGCode, switching_seq: list[int], index: int) -> SGCode:
    return (
        link.apply_switching_sequence(switching_seq[:index])
            .splice_v(switching_seq[index])
    )


@log_input_output
def sum_switches(link: SGCode, switching_seq: list[int]) -> Poly:
    result = 0

    # this is from 0 to the last switch in switching_seq
    for i in range(len(switching_seq)):
        switched_link = link.apply_switching_sequence(switching_seq[:i + 1])

        result += (
            ((-1) ** i) * (kauffman_polynomial(switched_link.splice_h(switching_seq[i])).simplify()
                           + kauffman_polynomial(switched_link.splice_v(switching_seq[i])).simplify())
        )

    return result
