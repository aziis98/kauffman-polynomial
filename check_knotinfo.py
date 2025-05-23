from codes import PDCode
from kauffman_v2 import f_polynomial

from sympy import Poly, parse_expr, symbols, init_printing

from utils import parse_nested_list
from contextlib import redirect_stdout

import database_knotinfo
import io
import time
import argparse
import math


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

    # p_expected = parse_expr(k_info['kauffman_polynomial'].replace('^', '**')).expand()

    # print("SG:", sg)
    # print("Kauffman (actual):")
    # print(p_actual)
    # print("Kauffman (expected):")
    # print(p_expected)

    if p_actual == p_expected:
        return (True, p_actual, bench_time)
    else:
        return (False, p_actual, bench_time)


# knots_list_1 = database_knotinfo.link_list()[2:200]
# for i, k_data in enumerate(knots_list_1):
#     print(f"Test {i + 1}/{len(knots_list_1)}")
#     result = process_knotinfo_polynomial(k_data, 'pd_notation', '[[]]')
#     if not result:
#         break


# for i, k_data in enumerate(list_of_links):
#     print(f"Test {i + 1}/{len(list_of_links)}")
#     result = process_knotinfo_polynomial(k_data, 'pd_notation_vector', '{{}}')
#     if not result:
#         break


# list_of_links = database_knotinfo.link_list(proper_links=True)[2:]
# process_knotinfo_polynomial(list_of_links[1500], 'pd_notation_vector', '{{}}')


def knotinfo_by_name(db, name):
    """
    Find knot information by name in the database.
    """
    return next(
        (knot for knot in db if knot['name'] == name),
        None
    )


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

    args = parser.parse_args()

    if args.all_knots:
        links_list = database_knotinfo.link_list()[2:]

        if args.count is not None:
            links_list = links_list[:int(args.count)]

        count = len(links_list)

        for i, k_data in enumerate(links_list):
            name = k_data['name']
            pd_code = k_data['pd_notation']
            p_expected_raw = k_data['kauffman_polynomial']
            p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

            pd = PDCode.from_tuples(parse_nested_list(pd_code, '[[]]'))
            sg = pd.to_signed_gauss_code()

            matches, p_actual, bench_time = process_polynomial(sg, p_expected)
            if matches:
                print(
                    f"{str(i + 1).rjust(1 + math.ceil(math.log10(count)))}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Correct"
                )
            else:
                print(
                    f"{str(i + 1).rjust(1 + math.ceil(math.log10(count)))}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Wrong"
                )
                print(f"> SG:", sg)
                print(f"> PD:", pd)
                print(f"> Kauffman (actual):")
                print(f"> {p_actual}")
                print(f"> Kauffman (expected):")
                print(f"> {p_expected}")
                break

    if args.all_links:
        links_list = database_knotinfo.link_list(proper_links=True)[2:]

        if args.count is not None:
            links_list = links_list[:int(args.count)]

        count = len(links_list)

        for i, k_data in enumerate(links_list):
            name = k_data['name']
            pd_code = k_data['pd_notation_vector']
            p_expected_raw = k_data['kauffman_polynomial']
            p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

            pd = PDCode.from_tuples(parse_nested_list(pd_code, '{{}}'))
            sg = pd.to_signed_gauss_code()

            matches, p_actual, bench_time = process_polynomial(sg, p_expected)
            if matches:
                print(
                    f"{str(i + 1).rjust(1 + math.ceil(math.log10(count)))}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Correct"
                )
            else:
                print(
                    f"{str(i + 1).rjust(1 + math.ceil(math.log10(count)))}/{count} > {name.ljust(14)} [{bench_time:.2f}s] => Wrong"
                )
                print(f"> SG:", sg)
                print(f"> PD:", pd)
                print(f"> Kauffman (actual):")
                print(f"> {p_actual}")
                print(f"> Kauffman (expected):")
                print(f"> {p_expected}")
                break
