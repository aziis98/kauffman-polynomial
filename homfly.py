import utils

from functools import cache
from codes import SGCode, HANDED_LEFT
from sympy import symbols, Poly
from utils import log_input_output, depth_print
from polynomial_commons import polynomial_wrapper


v, z = symbols("v z")
d = (v ** (-1) - v) / z


# KnotInfo HOMFLY convention:
# - P(O) = 1
# - P(L_+) / v - P(L_-) * v = P(L_0) * z


@polynomial_wrapper()
@log_input_output
@cache
def homfly_polynomial(link: SGCode) -> Poly:
    """
    Computes the HOMFLY polynomial P(v, z) for a given knot.
    """

    depth_print("ℹ️  not cached...")

    assert len(link.components) > 0

    disconnected_components = link.overlies_decomposition()

    if len(disconnected_components) == 1:
        unknotting_index = link.first_switch_to_std_unknot()

        if unknotting_index == False:
            depth_print("ℹ️  standard unknot form")
            return v**0

        else:
            depth_print("ℹ️  single knotted component")
            depth_print(f"ℹ️  unknotting index: {unknotting_index!r}")

            link_switched = link.switch_crossing(unknotting_index)

            if link.get_crossing_handedness(unknotting_index) == HANDED_LEFT:
                depth_print(f"ℹ️  spliced")
                homfly_spliced = homfly_polynomial(
                    link.splice_h(unknotting_index)
                )

                depth_print(f"ℹ️  switched")
                homfly_switched = homfly_polynomial(link_switched)

                # P(L_+) = v * (P(L_0) * z + P(L_-) * v)
                return v * (
                    homfly_spliced * z + homfly_switched * v
                )

            else:
                depth_print(f"ℹ️  spliced")
                homfly_spliced = homfly_polynomial(
                    link.splice_v(unknotting_index)
                )

                depth_print(f"ℹ️  switched")
                homfly_switched = homfly_polynomial(link_switched)

                # P(L_-) = (P(L_+) / v -  P(L_0) * z) / v
                return 1 / v * (
                    homfly_switched / v - homfly_spliced * z
                )

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

            result *= homfly_polynomial(new_link).simplify()

        return result
