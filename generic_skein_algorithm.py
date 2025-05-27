import functools
import utils

from polynomial_commons import polynomial_wrapper
from equation_dsl import Expression
from codes import HANDED_LEFT, SGCode
from typing import Callable
from sympy import solve, symbols, Poly, Eq, Expr
from utils import depth_print


KnotPoly = Callable[[SGCode], Poly]


SingleComponentPoly = KnotPoly
MultiComponentPoly = Callable[[KnotPoly, list[SGCode]], Poly]


def generic_unknot_skein_polynomial(
    f: Expression,
    eqs: list[Expression],
    case_std_unknot: SingleComponentPoly = lambda _: 1,
    case_disjoint: MultiComponentPoly | None = None
) -> Callable[[SGCode], Poly]:
    """
    A generic skein polynomial function that can be used to construct different polynomial types.
    The algorithm is based on unrolling to the standard unknot form and applying skein relations.

    Args:
        f (Expression): The polynomial var for which the skein polynomial is computed.
        eqs (list[Expression]): A list of equations that define the skein relations.
        case_std_unknot (SingleComponentPoly, optional): A function that handles the case of a standard unknot.
            Defaults to returning 1.
        case_disjoint (MultiComponentPoly | None, optional): A function that handles the case of disjoint links.
            Defaults to None, which raises an error if disjoint links are encountered.

    Returns:
        Callable[[SGCode], Poly]: A function that computes the polynomial for a given SGCode.
    """

    name = str(f)

    var_eval_L_positive = symbols(f'{name}_L_positive')
    var_eval_L_negative = symbols(f'{name}_L_negative')
    var_eval_L_splice_h = symbols(f'{name}_L_splice_h')
    var_eval_L_splice_v = symbols(f'{name}_L_splice_v')

    sympy_eqs = [
        eq.evaluate(
            {
                f'{name}(L.positive)': var_eval_L_positive,
                f'{name}(L.negative)': var_eval_L_negative,
                f'{name}(L.splice_h)': var_eval_L_splice_h,
                f'{name}(L.splice_v)': var_eval_L_splice_v,
            },
            equality=Eq,
        )
        for eq in eqs
    ]

    # solve the equation for poly(L.positive)
    poly_positive_solution = solve(
        sympy_eqs,
        var_eval_L_positive,
    )[var_eval_L_positive]
    poly_negative_solution = solve(
        sympy_eqs,
        var_eval_L_negative,
    )[var_eval_L_negative]

    print(f"ℹ️  {name} polynomial equations:")
    print(f"ℹ️  {name}(L.positive): {poly_positive_solution}")
    print(f"ℹ️  {name}(L.negative): {poly_negative_solution}")

    @polynomial_wrapper()
    def skein_polynomial(link: SGCode) -> Poly:
        assert len(link.components) > 0, "Link must have at least one component"

        disconnected_components = link.overlies_decomposition()

        if len(disconnected_components) == 1:
            unknotting_index = link.first_switch_to_std_unknot()

            if unknotting_index == False:
                depth_print("ℹ️  standard unknot form")
                return case_std_unknot(link)
            else:
                depth_print("ℹ️  single knotted component")
                depth_print(f"ℹ️  unknotting index: {unknotting_index!r}")

                if link.get_crossing_handedness(unknotting_index) == HANDED_LEFT:
                    depth_print(f"ℹ️  positive crossing")

                    rec_evals: dict[Expr, Poly] = {}

                    if poly_positive_solution.has(var_eval_L_splice_h):
                        depth_print(f"ℹ️  spliced h")
                        rec_evals[var_eval_L_splice_h] = skein_polynomial(
                            link.splice_h(unknotting_index)
                        )
                    if poly_positive_solution.has(var_eval_L_splice_v):
                        depth_print(f"ℹ️  spliced v")
                        rec_evals[var_eval_L_splice_v] = skein_polynomial(
                            link.splice_v(unknotting_index)
                        )
                    if poly_positive_solution.has(var_eval_L_negative):
                        depth_print(f"ℹ️  switched")
                        rec_evals[var_eval_L_negative] = skein_polynomial(
                            link.switch_crossing(unknotting_index)
                        )

                    return poly_positive_solution.subs(rec_evals)
                else:
                    depth_print(f"ℹ️  negative crossing")

                    rec_evals: dict[Expr, Poly] = {}

                    if poly_negative_solution.has(var_eval_L_splice_h):
                        depth_print(f"ℹ️  spliced h")
                        rec_evals[var_eval_L_splice_h] = skein_polynomial(
                            # WARNING: switched for negative crossing
                            link.splice_v(unknotting_index)
                        )
                    if poly_negative_solution.has(var_eval_L_splice_v):
                        depth_print(f"ℹ️  spliced v")
                        rec_evals[var_eval_L_splice_v] = skein_polynomial(
                            # WARNING: switched for negative crossing
                            link.splice_h(unknotting_index)
                        )
                    if poly_negative_solution.has(var_eval_L_positive):
                        depth_print(f"ℹ️  switched")
                        rec_evals[var_eval_L_positive] = skein_polynomial(
                            link.switch_crossing(unknotting_index)
                        )

                    return poly_negative_solution.subs(rec_evals)
        else:
            if case_disjoint is None:
                raise ValueError(
                    "case_disjoint must be provided for disjoint links")

            return case_disjoint(skein_polynomial, [
                link.sublink(component_ids)
                for component_ids in disconnected_components
            ])

    return skein_polynomial
