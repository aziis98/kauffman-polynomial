from codes import PDCode
from kauffman_v2 import f_polynomial

from sympy import Poly, parse_expr, symbols, init_printing

from utils import parse_nested_list
from contextlib import redirect_stdout

import database_knotinfo
import io
import time
import argparse


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


def process_polynomial(sg, p_expected) -> tuple[bool, Poly, float]:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    stdout_buff = io.StringIO()
    start = time.time()

    with redirect_stdout(stdout_buff):
        try:
            p_actual = f_polynomial(sg).expand()

        except Exception as e:
            print(f"Error: {e}")
            p_actual = None

    end = time.time()
    bench_time = end - start

    return (p_actual == p_expected, p_actual, bench_time)


if __name__ == "__main__":
    """
    CLI with --all-knots and --all-links options.
    """

    parser = argparse.ArgumentParser(
        description="Calculate the Kauffman polynomial of a knot or link."
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug traces",
    )
    parser.add_argument(
        '--all-knots',
        action='store_true',
        help="Test all knots",
    )
    parser.add_argument(
        '--all-links',
        action='store_true',
        help="Test all links",
    )
    parser.add_argument(
        '-c', '--count',
        default=None,
        help="Number of knots to test",
    )
    parser.add_argument(
        '-s', '--skip',
        default=None,
        help="Number of knots to skip",
    )

    args = parser.parse_args()

    skip_count = 0
    if args.skip is not None:
        skip_count = int(args.skip)

    if args.all_knots:
        links_list = database_knotinfo.link_list()[2:]

        if args.count is not None:
            links_list = links_list[:int(args.count)]

        count = len(links_list)
        count_size = len(str(count)) + 1

        for i, k_data in enumerate(links_list):
            if i < skip_count:
                print(
                    f"Skipping {str(i + 1).rjust(count_size)}/{count} > {k_data['name']}"
                )
                continue

            name = k_data['name']
            pd_code = k_data['pd_notation']
            p_expected_raw = k_data['kauffman_polynomial']
            p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

            pd = PDCode.from_tuples(parse_nested_list(pd_code, '[[]]'))
            sg = pd.to_signed_gauss_code()

            matches, p_actual, bench_time = process_polynomial(sg, p_expected)
            if matches:
                print(
                    f"{str(i + 1).rjust(count_size)}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Correct"
                )
            else:
                print(
                    f"{str(i + 1).rjust(count_size)}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Wrong"
                )

                prefix = " " * len(
                    f"{str(i + 1).rjust(count_size)}/{count} "
                )

                print(f"{prefix}> SG:", sg)
                print(f"{prefix}> PD:", pd)
                print(f"{prefix}> Kauffman (actual):")
                print(f"{prefix}> {p_actual}")
                print(f"{prefix}> Kauffman (expected):")
                print(f"{prefix}> {p_expected}")

    if args.all_links:
        links_list = database_knotinfo.link_list(proper_links=True)[2:]

        if args.count is not None:
            links_list = links_list[:int(args.count)]

        count = len(links_list)
        count_size = len(str(count)) + 1

        for i, k_data in enumerate(links_list):
            if i < skip_count:
                print(
                    f"Skipping {str(i + 1).rjust(count_size)}/{count} > {k_data['name']}"
                )
                continue

            name = k_data['name']
            pd_code = k_data['pd_notation_vector']
            p_expected_raw = k_data['kauffman_polynomial']
            p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

            pd = PDCode.from_tuples(parse_nested_list(pd_code, '{{}}'))
            sg = pd.to_signed_gauss_code()

            matches, p_actual, bench_time = process_polynomial(sg, p_expected)
            if matches:
                print(
                    f"{str(i + 1).rjust(count_size)}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Correct"
                )
            else:
                print(
                    f"{str(i + 1).rjust(count_size)}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Wrong"
                )

                prefix = " " * len(
                    f"{str(i + 1).rjust(count_size)}/{count} "
                )

                print(f"{prefix}> SG:", sg)
                print(f"{prefix}> PD:", pd)
                print(f"{prefix}> Kauffman (actual):")
                print(f"{prefix}> {p_actual}")
                print(f"{prefix}> Kauffman (expected):")
                print(f"{prefix}> {p_expected}")
