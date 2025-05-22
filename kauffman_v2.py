from codes import SGCode
from sympy import symbols, Poly

from utils import log_input_output, depth_print, get_depth

from functools import cache, wraps

a, z = symbols("a z")
d = (a + 1 / a) / z - 1


_fn_calls_count = 0


def wrap_before(func):
    @wraps(func)
    def wrapper(link: SGCode):
        global _fn_calls_count
        if get_depth() == 0:
            _fn_calls_count = 0

        _fn_calls_count += 1

        depth_print("ℹ️  wrapping before...")
        # K8_18
        # simple: 1004
        # cache: 936
        # cache, relabel: 814
        # cache, relabel, to_minimal: 999 (???)
        # result = func(link.to_minimal())
        result = func(link.relabel().to_minimal())

        if get_depth() == 0:
            print(f"Call Count: {_fn_calls_count}")

        return result

    return wrapper


@wrap_before
@log_input_output
@cache
def kauffman_polynomial(link: SGCode) -> Poly:
    depth_print("ℹ️  not cached...")

    if len(link.components) == 0:
        return 0

    disconnected_components = [*link.unlinked_components().keys()]

    assert len(disconnected_components) > 0

    if len(disconnected_components) == 1:
        unknotting_seq = link.std_unknot_switching_sequence()

        link_rev = link.reverse()
        unknotting_seq_rev = link_rev.std_unknot_switching_sequence()

        if len(unknotting_seq) == 0 or len(unknotting_seq_rev) == 0:
            depth_print("ℹ️  standard unknot form")
            return a ** link.writhe()

        else:
            depth_print("ℹ️  single knotted component")
            link_switched = link.switch_crossing(unknotting_seq[0])
            link_spliced_h = link_switched.splice_h(unknotting_seq[0])
            link_spliced_v = link_switched.splice_v(unknotting_seq[0])

            return (
                z * (kauffman_polynomial(link_spliced_h) +
                     kauffman_polynomial(link_spliced_v))
                - kauffman_polynomial(link_switched)
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

            result *= kauffman_polynomial(new_link).simplify()

        return result
