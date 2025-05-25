import time
import utils
import tqdm
import re

import kauffman_v2
import homfly

from typing import Callable
from codes import SGCode, PDCode
from sympy import symbols, parse_expr, Poly

import database_knotinfo

# Add colorama for colored output
from colorama import init, Fore, Back, Style
init(autoreset=True)


AVAILABLE_POLYNOMIALS: dict[str, tuple[Callable[[SGCode], Poly], str | None]] = {
    "P": (homfly.homfly_polynomial, "homfly_polynomial"),
    "F": (kauffman_v2.f_polynomial, "kauffman_polynomial"),
    "L": (kauffman_v2.kauffman_polynomial, None),
}


z = symbols("z")
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


def print_header(text: str):
    """Print a styled header."""
    print("")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{text:^60}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")


def print_section(title: str, content: str = ""):
    """Print a styled section."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}▶ {title}{Style.RESET_ALL}")
    if content:
        print(f"  {content}")


def print_success(text: str):
    """Print success message."""
    print(f"{Fore.GREEN}{Style.BRIGHT}✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message."""
    print(f"{Fore.RED}{Style.BRIGHT}✗ {text}{Style.RESET_ALL}")


def print_info(text: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")


def format_polynomial(poly: Poly) -> str:
    """Format polynomial for better readability."""
    poly_str = str(Poly(poly, z).as_expr())
    # Add some basic formatting
    if len(poly_str) > 80:
        # split at " + z**" or " - z**"
        poly_str = re.sub(r'(\s*[\+\-]\s*z\*\*[0-9]+)', r'\n   \1', poly_str)

    return poly_str


def kauffman_cli():
    """
    Command-line interface for the Kauffman polynomial.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate knot/link polynomials with enhanced output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 8_18                    # Compute F polynomial for knot 8_18
  %(prog)s -p P 3_1               # Compute HOMFLY polynomial for trefoil
  %(prog)s --pd "[[1,3,2,4]]"     # Use PD code directly
        """
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug traces",
    )
    parser.add_argument(
        '--pd',
        help="PD notation string (e.g., '[[1,3,2,4],[3,1,4,2]]')",
    )
    parser.add_argument(
        '-p', '--polynomial',
        choices=list(AVAILABLE_POLYNOMIALS.keys()),
        default="F",
        help=f"Polynomial to compute: {', '.join(AVAILABLE_POLYNOMIALS.keys())}. Default is 'F' (Kauffman F polynomial).",
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help="Disable colored output",
    )
    parser.add_argument(
        "knot_name",
        nargs="?",
        default=None,
        help="Name of the knot or link (e.g., '3_1', '8_18', 'L2a1')",
    )

    args = parser.parse_args()

    # Disable colors if requested or not available
    if args.no_color:
        global Fore, Back, Style

        class _DummyColor:
            def __getattr__(self, name): return ""
        Fore = Back = Style = _DummyColor()

    utils.global_debug = args.debug

    poly_fn, poly_label = AVAILABLE_POLYNOMIALS[args.polynomial]
    poly_name = {
        "P": "HOMFLY Polynomial",
        "F": "Kauffman F Polynomial",
        "L": "Kauffman L Polynomial"
    }.get(args.polynomial, f"{args.polynomial} Polynomial")

    print_header(f"Knot Polynomial Calculator")
    print_info(f"  Computing: {poly_name}")

    pd: PDCode | None = None
    sg: SGCode
    knot_entry = None
    knot_name = args.knot_name or "Custom PD Code"

    if args.pd is not None:
        print_section("Input", "Using provided PD code")
        try:
            pd = PDCode.from_tuples(
                utils.parse_nested_list(args.pd, paren_spec="[[]]")
            )
            sg = pd.to_signed_gauss_code()
            knot_name = "Custom PD Code"
            print_success("PD code parsed successfully")
        except Exception as e:
            print_error(f"Failed to parse PD code: {e}")
            return
    else:
        if not args.knot_name:
            print_error("Please provide either a knot name or --pd option")
            return

        print_section("Database", "Loading KnotInfo database...")

        load_start = time.time()
        load_diagrams()
        load_time = time.time() - load_start

        print_success(
            f"Database loaded ({load_time:.2f}s, {len(all_diagrams)} entries)")

        print_section("Lookup", f"Searching for '{args.knot_name}'...")
        knot_entry = knotinfo_by_name(args.knot_name)

        if knot_entry is None:
            print_error(f"Knot '{args.knot_name}' not found in database")
            print_info(
                "Available knots include: 3_1, 4_1, 5_1, 5_2, 6_1, 6_2, 6_3, ..."
            )
            return

        print_success(f"Found knot: {args.knot_name}")

        try:
            pd = knotinfo_entry_pd_code(knot_entry)
            sg = pd.to_signed_gauss_code()
        except Exception as e:
            print_error(f"Failed to extract PD code: {e}")
            return

    print_section("Knot Analysis")
    print(f"  Name: {Style.BRIGHT}{knot_name}{Style.RESET_ALL}")
    if pd:
        print(f"  PD Code: {pd!s}")
    print(f"  Signed Gauss Code: {sg!r}")
    print(
        f"  Crossings: {Style.BRIGHT}{sg.crossings_count()}{Style.RESET_ALL}")
    print(
        f"  Writhe: {Style.BRIGHT}{sg.writhe()}{Style.RESET_ALL}")

    # Improved complexity estimation
    crossing_count = sg.crossings_count()
    estimated_calls = 2.16 ** crossing_count

    print_section("Computing Polynomial", f"Running {poly_name}...")
    print(
        f"  Estimated steps: {Fore.YELLOW}{utils.to_human_readable_number(estimated_calls)}{Style.RESET_ALL} calls"
    )

    # Setup progress bar with better description
    if not args.debug:
        progress_desc = f"  Computing {args.polynomial} polynomial"
        progress_bar = tqdm.tqdm(
            desc=progress_desc,
            unit=" calls",
            dynamic_ncols=True,
            colour='green'
        )
        utils.progress_bar.set(progress_bar)

    # Run the polynomial function and measure time
    start_time = time.time()
    p_actual = poly_fn(sg).expand()
    end_time = time.time()

    elapsed_time = end_time - start_time

    if not args.debug:
        utils.progress_bar.get().close()
        actual_calls = utils.progress_bar.get().n
        calls_per_second = actual_calls / elapsed_time if elapsed_time > 0 else 0

        print_success(f"Computation completed!")
        print(
            f"  Actual calls: {Style.BRIGHT}{utils.to_human_readable_number(actual_calls)}{Style.RESET_ALL}")
        print(
            f"  Rate: {Style.BRIGHT}{utils.to_human_readable_number(calls_per_second)}{Style.RESET_ALL} calls/sec")

    print_section("Performance")
    print(
        f"  Elapsed time: {Style.BRIGHT}{elapsed_time:.3f}{Style.RESET_ALL} seconds")

    print_section("Results")
    print(
        f"  {Style.BRIGHT}Polynomial ({args.polynomial}):{Style.RESET_ALL}"
    )
    formatted_poly = format_polynomial(p_actual)
    print(f"    {Fore.CYAN}{formatted_poly}{Style.RESET_ALL}")

    # Verification section
    print_section("Verification")
    if poly_label and knot_entry and knot_entry.get(poly_label):
        try:
            p_expected_raw = knot_entry[poly_label]
            p_expected = parse_expr(p_expected_raw.replace("^", "**")).expand()
            matches = p_actual == p_expected

            print(
                f"  {Style.BRIGHT}Expected Polynomial ({poly_label}):{Style.RESET_ALL}"
            )
            formatted_expected_poly = format_polynomial(p_expected)
            print(f"    {Fore.CYAN}{formatted_expected_poly}{Style.RESET_ALL}")

            print()
            if matches:
                print_success("Polynomials match!")
            else:
                print_error("Polynomials don't match!")
                print(
                    f"  {Fore.YELLOW}This might indicate a computation error or database inconsistency{Style.RESET_ALL}")

        except Exception as e:
            print_error(f"Verification failed: {e}")
    else:
        print(
            f"  {Style.BRIGHT}No reference polynomial available for verification{Style.RESET_ALL}"
        )

    print_header("Computation Complete")


if __name__ == "__main__":
    kauffman_cli()
