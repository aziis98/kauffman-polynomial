#!/usr/bin/env python3
"""
Raw polynomial computation tool for machine processing.
Outputs polynomials in raw SymPy format without formatting.
"""

import sys
import argparse
import utils
import kauffman
import homfly
import database_knotinfo

from typing import Callable
from codes import SGCode, PDCode
from sympy import Poly

# Available polynomials
AVAILABLE_POLYNOMIALS: dict[str, Callable[[SGCode], Poly]] = {
    "P": homfly.homfly_polynomial,
    "F": kauffman.f_polynomial,
    "L": kauffman.kauffman_polynomial,
}

# Global storage for knotinfo database
all_diagrams = []


def load_diagrams():
    """Load KnotInfo database."""
    global all_diagrams
    all_diagrams = (
        database_knotinfo.link_list()[2:]
        + database_knotinfo.link_list(proper_links=True)[2:]
    )


def knotinfo_by_name(name):
    """Find knot information by name in the database."""
    return next(
        (knot for knot in all_diagrams if knot['name'] == name),
        None
    )


def knotinfo_entry_pd_code(knot_entry) -> PDCode:
    """Get the PD code from a knot entry."""
    if "pd_notation" in knot_entry:
        return PDCode.from_tuples(
            utils.parse_nested_list(
                knot_entry["pd_notation"], paren_spec="[[]]"
            )
        )
    elif "pd_notation_vector" in knot_entry:
        return PDCode.from_tuples(
            utils.parse_nested_list(
                knot_entry["pd_notation_vector"], paren_spec="{{}}"
            )
        )
    else:
        raise ValueError("No valid PD notation found in knot data.")


def compute_polynomial_from_pd(pd_string: str, poly_fn: Callable[[SGCode], Poly]) -> Poly:
    """Compute polynomial from PD code string."""
    pd_raw = eval(pd_string)
    pd = PDCode.from_tuples(pd_raw)
    sg = pd.to_signed_gauss_code()
    return poly_fn(sg).expand()


def compute_polynomial_from_sg(sg_string: str, poly_fn: Callable[[SGCode], Poly]) -> Poly:
    """Compute polynomial from Signed Gauss code string."""
    sg_raw = eval(sg_string)
    sg = SGCode.from_tuples(sg_raw)

    return poly_fn(sg).expand()


def compute_polynomial_from_knotinfo(name: str, poly_fn: Callable[[SGCode], Poly]) -> Poly:
    """Compute polynomial from KnotInfo name."""
    knot_entry = knotinfo_by_name(name)
    if knot_entry is None:
        raise ValueError(f"Knot '{name}' not found in database")

    pd = knotinfo_entry_pd_code(knot_entry)
    sg = pd.to_signed_gauss_code()
    return poly_fn(sg).expand()


COMPUTATION_FUNCTIONS = {
    'pd': compute_polynomial_from_pd,
    'sg': compute_polynomial_from_sg,
    'knotinfo': compute_polynomial_from_knotinfo
}


class SpecsAction(argparse.Action):
    """Custom action to preserve order of inputs."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, 'specs') or namespace.specs is None:
            namespace.specs = []

        input_type_map = {
            '--pd': 'pd',
            '--sg': 'sg',
            '--knotinfo': 'knotinfo'
        }

        input_type = 'unknown'
        if option_string:
            input_type = input_type_map.get(option_string, 'unknown')

        namespace.specs.append((input_type, values))


def main():
    parser = argparse.ArgumentParser(
        description="Raw polynomial computation tool for machine processing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-p', '--polynomial',
        choices=list(AVAILABLE_POLYNOMIALS.keys()),
        required=True,
        help="Polynomial to compute (P=HOMFLY, F=Kauffman F, L=Kauffman L)"
    )

    parser.add_argument(
        '--pd',
        action=SpecsAction,
        dest='specs',
        help="PD notation string, e.g. '[[3,6,4,1],[5,2,6,3],[1,4,2,5]]'",
        metavar='PD_CODE'
    )

    parser.add_argument(
        '--sg',
        action=SpecsAction,
        dest='specs',
        help="Signed Gauss code string, e.g. '[[(+1, -1), (-2, -1)], [(-1, -1), (+2, -1)]]'",
        metavar='SG_CODE'
    )

    parser.add_argument(
        '--knotinfo',
        action=SpecsAction,
        dest='specs',
        help="KnotInfo knot or link name, e.g. '3_1', 'L8a2{0}'",
        metavar='NAME'
    )

    parser.add_argument(
        'knot_names',
        nargs='*',
        help="Knot names as positional arguments"
    )

    args = parser.parse_args()

    # Disable debug output for clean machine processing
    utils.global_debug = False

    # Get polynomial function
    poly_fn = AVAILABLE_POLYNOMIALS[args.polynomial]

    # Collect all inputs in order
    inputs = []

    # Add ordered inputs from options - ensure specs exists and is not None
    if hasattr(args, 'specs') and args.specs is not None:
        inputs.extend(args.specs)

    # Add positional knot names
    for name in args.knot_names:
        inputs.append(('knotinfo', name))

    # If no inputs provided, error
    if not inputs:
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)

    # Load database if needed
    needs_database = any(input_type == 'knotinfo' for input_type, _ in inputs)
    if needs_database:
        load_diagrams()

    # Process each input and output polynomial
    for input_type, input_value in inputs:
        try:
            print(
                COMPUTATION_FUNCTIONS[input_type](input_value, poly_fn)
            )
        except Exception as e:
            print(
                f"Error processing {input_type} '{input_value}': {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
