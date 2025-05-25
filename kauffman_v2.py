from functools import cache
from codes import SGCode
from sympy import symbols, Poly
from utils import log_input_output, depth_print
from polynomial_commons import polynomial_wrapper


a, z = symbols("a z")
d = (a + 1 / a) / z - 1


@polynomial_wrapper(optimizations={'expand', 'relabel', 'to_minimal'})
@log_input_output
@cache
def kauffman_polynomial(link: SGCode) -> Poly:
    depth_print("ℹ️  not cached...")

    if len(link.components) == 0:
        return 0

    disconnected_components: list[list[int]] = link.overlies_decomposition()

    assert len(disconnected_components) > 0

    if len(disconnected_components) == 1:
        unknot_index = link.first_switch_to_std_unknot()

        link_rev = link.reverse()
        unknot_index_rev = link_rev.first_switch_to_std_unknot()

        if unknot_index == False or unknot_index_rev == False:
            depth_print("ℹ️  standard unknot form")
            return a ** link.writhe()
        else:
            depth_print(f"ℹ️  applying skein")
            link_switched = link.switch_crossing(unknot_index)
            link_spliced_h = link_switched.splice_h(unknot_index)
            link_spliced_v = link_switched.splice_v(unknot_index)

            depth_print(f"ℹ️  splice h, lambda = [{unknot_index}...]")
            k_link_spliced_h = kauffman_polynomial(link_spliced_h)

            depth_print(f"ℹ️  splice v, lambda = [{unknot_index}...]")
            k_link_spliced_v = kauffman_polynomial(link_spliced_v)

            depth_print(f"ℹ️  switch, lambda = [{unknot_index}...]")
            k_link_switched = kauffman_polynomial(link_switched)

            return (
                z * (k_link_spliced_h + k_link_spliced_v)
                - k_link_switched
            )

    else:
        depth_print(f"ℹ️  split link: {disconnected_components}")

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

            result *= kauffman_polynomial(new_link)

        return result


def f_polynomial(link: SGCode) -> Poly:
    return (a ** (-link.writhe())) * kauffman_polynomial(link)
