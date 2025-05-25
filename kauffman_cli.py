import time
from typing import Callable
from codes import SGCode, PDCode

import kauffman_v2
import homfly


from sympy import parse_expr, Poly

import utils
import tqdm

import database_knotinfo


AVAILABLE_POLYNOMIALS: dict[str, tuple[Callable[[SGCode], Poly], str | None]] = {
    "P": (homfly.homfly_polynomial, "homfly_polynomial"),
    "F": (kauffman_v2.f_polynomial, "kauffman_polynomial"),
    "L": (kauffman_v2.kauffman_polynomial, None),
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


def knotinfo_entry_pd_code(knot_entry) -> PDCode:
    """
    Get the PD code from a knot entry.
    """
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
        help=f"Polynomial to compute: {', '.join(AVAILABLE_POLYNOMIALS.keys())}. Default is 'F' (Kauffman F polynomial).",
    )
    parser.add_argument(
        "knot_name",
        nargs="?",
        default=None,
        help="Name of the knot or link.",
    )

    args = parser.parse_args()

    utils.global_debug = args.debug

    poly_fn, poly_label = AVAILABLE_POLYNOMIALS[args.polynomial]

    pd: PDCode | None = None
    sg: SGCode
    knot_entry = None

    if args.pd is not None:
        pd = PDCode.from_tuples(
            utils.parse_nested_list(args.pd, paren_spec="[[]]")
        )
        sg = pd.to_signed_gauss_code()
    else:
        print("Loading KnotInfo...")
        load_diagrams()
        print("Done.")

        knot_entry = knotinfo_by_name(args.knot_name)

        if knot_entry is None:
            print(f"Knot '{args.knot_name}' not found.")
            return

        pd = knotinfo_entry_pd_code(knot_entry)
        sg = pd.to_signed_gauss_code()

    print(f"Processing knot: {args.knot_name}")

    if pd:
        print(f"PD Code: {pd!s}")

    print(f"Signed Gauss Code: {sg!r}")

    # this is a random heuristic interpolated from the call count of 13n5110
    print(
        f"Starting computation, estimated call count: {utils.to_human_readable_number(2.16 ** sg.crossings_count())}..."
    )

    if not args.debug:
        utils.progress_bar.set(tqdm.tqdm())

    # Run the polynomial function and measure time
    start_time = time.time()
    p_actual = poly_fn(sg).expand()
    end_time = time.time()

    if not args.debug:
        utils.progress_bar.get().close()
        print(f"Call Count: {utils.progress_bar.get().n}")

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
