import time
import database_knotinfo
import utils
from codes import SGCode, PDCode

import kauffman_v2
from kauffman_v2 import f_polynomial, kauffman_polynomial


from sympy import parse_expr, symbols, init_printing
from utils import parse_nested_list


init_printing(use_unicode=True)
a, z = symbols("a z")


AVAILABLE_POLYNOMIALS = {
    "F": (f_polynomial, "kauffman_polynomial"),
    "L": (kauffman_polynomial, None),
}

all_diagrams = []


def load_diagrams():
    global all_diagrams
    all_diagrams = (
        database_knotinfo.link_list()[2:]
        + database_knotinfo.link_list(proper_links=True)[2:]
    )


def knotinfo_by_name(name):
    """
    Find knot information by name in the database.
    """
    return next(
        (knot for knot in all_diagrams if knot['name'] == name),
        None
    )


# kauffman_cli --polynomial F 8_18

def kauffman_cli():
    """
    Command-line interface for the Kauffman polynomial.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate the Kauffman polynomial of a knot or link."
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug traces",
    )
    parser.add_argument(
        '--pd',
        help="PD notation string",
    )
    parser.add_argument(
        '-p', '--polynomial',
        choices=list(AVAILABLE_POLYNOMIALS.keys()),
        default="F",
        help=f"Polynomial type: {', '.join(AVAILABLE_POLYNOMIALS.keys())}",
    )
    parser.add_argument(
        "knot_name",
        nargs="?",
        default=None,
        help="Name of the knot or link.",
    )

    args = parser.parse_args()

    kauffman_v2.optimizations = {'to_minimal', 'relabel', 'expand'}
    utils.global_debug = args.debug

    poly_fn, poly_label = AVAILABLE_POLYNOMIALS[args.polynomial]

    pd: PDCode | None = None
    sg: SGCode
    knot_entry = None

    if args.pd is not None:
        sg = PDCode.from_tuples(
            parse_nested_list(args.pd, paren_spec="[[]]")
        ).to_signed_gauss_code()
    else:
        print("Loading KnotInfo...")
        load_diagrams()
        print("Done.")

        knot_entry = knotinfo_by_name(args.knot_name)

        if knot_entry is None:
            print(f"Knot '{args.knot_name}' not found.")
            return

        knot_code: list[list[int]]

        if "pd_notation" in knot_entry:
            knot_code = parse_nested_list(
                knot_entry["pd_notation"], paren_spec="[[]]"
            )
        elif "pd_notation_vector" in knot_entry:
            knot_code = parse_nested_list(
                knot_entry["pd_notation_vector"], paren_spec="{{}}"
            )
        else:
            raise ValueError(
                "No valid PD notation found in knot data."
            )

        pd = PDCode.from_tuples(knot_code)
        sg = pd.to_signed_gauss_code()

    print(f"Processing knot: {args.knot_name}")

    if pd:
        print(f"PD Code: {pd!s}")
    print(f"Signed Gauss Code: {sg!r}")

    # Initialize pretty printing
    start_time = time.time()
    p_actual = poly_fn(sg).expand()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    print(f"Writhe: {sg.writhe()}")

    print(f"Polynomial (actual):\n{p_actual}")

    if poly_label and knot_entry and knot_entry[poly_label]:
        p_expected_raw = knot_entry[poly_label]
        p_expected = parse_expr(p_expected_raw.replace("^", "**")).expand()
        matches = p_actual == p_expected

        # print(f"Polynomial (raw):\n{p_expected_raw}")
        print(f"Polynomial (expected):\n{p_expected}")
        print(f"=> Match: {matches}")


if __name__ == "__main__":
    kauffman_cli()


# [[8,1,9,2],[15,3,16,2],[18,5,19,6],[20,7,1,8],[4,9,5,10],[13,11,14,10],[17,13,18,12],[3,15,4,14],[11,17,12,16],[6,19,7,20]]


# [[12,2,13,1],[15,2,16,3],[18,5,19,6],[20,7,1,8],[13,9,14,8],[3,11,4,10],[16,12,17,11],[9,15,10,14],[4,17,5,18],[6,19,7,20]]

# [[8,1,9,2],[14,4,15,3],[18,5,19,6],[20,7,1,8],[2,9,3,10],[15,11,16,10],[17,13,18,12],[4,14,5,13],[11,17,12,16],[6,19,7,20]]


# [[(-1, +1), (+10, +1), (-2, +1), (+1, +1), (-3, +1), (+9, +1), (-10, +1), (+2, +1), (+5, -1), (-7, -1), (+6, -1), (-8, -1), (-9, +1), (+3, +1), (+4, -1), (-5, -1), (+7, -1), (-6, -1), (+8, -1), (-4, -1)]]
