from codes import SGCode, HANDED_LEFT, HANDED_RIGHT
from sympy import symbols, Poly, poly

from utils import log_input_output, depth_print, get_depth
from functools import cache, wraps


v, z = symbols("v z")
d = (v ** (-1) - v) / z


# _fn_calls_count = 0


def wrap_before(func):
    @wraps(func)
    def wrapper(link: SGCode):
        # global _fn_calls_count
        # if get_depth() == 0:
        #     _fn_calls_count = 0

        # _fn_calls_count += 1

        # depth_print("ℹ️  wrapping before...")
        result = func(link.relabel())

        # if get_depth() == 0:
        #     print(f"Call Count: {_fn_calls_count}")

        return result

    return wrapper


# KnotInfo
# P(O) = 1,   P(L_+) / v - P(L_-) * v = P(L_0) * z

@wrap_before
@log_input_output
@cache
def homfly_polynomial(link: SGCode) -> Poly:
    depth_print("ℹ️  not cached...")

    assert len(link.components) > 0

    disconnected_components = [*link.unlinked_components().keys()]
    if len(disconnected_components) == 1:
        unknotting_seq = link.std_unknot_switching_sequence()

        if len(unknotting_seq) == 0:
            depth_print("ℹ️  standard unknot form")
            return v**0

        else:
            depth_print("ℹ️  single knotted component")
            depth_print(f"ℹ️  unknotting seq: {unknotting_seq!r}")

            link_switched = link.switch_crossing(unknotting_seq[0])

            if link.get_crossing_handedness(unknotting_seq[0]) == HANDED_LEFT:
                link_spliced = link.splice_h(unknotting_seq[0])

                return v * (
                    z * homfly_polynomial(link_spliced)
                    + v * homfly_polynomial(link_switched)
                )

            else:
                link_spliced = link.splice_v(unknotting_seq[0])

                return 1 / v * (
                    homfly_polynomial(link_switched) / v
                    - z * homfly_polynomial(link_spliced)
                )

    else:
        depth_print("ℹ️  multiple unlinked components")

        result = v**0
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
