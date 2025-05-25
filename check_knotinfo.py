from codes import SGCode, PDCode

from homfly import homfly_polynomial
from kauffman_v2 import f_polynomial

from sympy import Poly, parse_expr, symbols, init_printing

from utils import parse_nested_list
from contextlib import redirect_stdout

import database_knotinfo
import io
import time
import argparse
import concurrent.futures
import multiprocessing
import threading


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


AVAILABLE_POLYNOMIALS = {
    'homfly': (homfly_polynomial, "homfly_polynomial"),
    'kauffman': (f_polynomial, "kauffman_polynomial"),
}


def process_polynomial(sg: SGCode, p_expected: Poly, poly_func) -> tuple[bool, Poly, float]:
    """
    Tests the specified polynomial for a given knot.
    """
    stdout_buff = io.StringIO()
    start = time.time()

    with redirect_stdout(stdout_buff):
        try:
            p_actual = poly_func(sg).expand()

        except Exception as e:
            print(f"Error calculating polynomial: {e}")
            p_actual = None

    end = time.time()
    bench_time = end - start

    return (p_actual == p_expected, p_actual, bench_time)


def print_result(
    i: int,
    total: int,
    name: str,
    matches: bool,
    p_actual: Poly,
    p_expected: Poly,
    sg: SGCode,
    pd: PDCode,
    bench_time: float,
    poly_name: str,
) -> None:
    """
    Print the result of the polynomial check.
    """
    count_size = len(str(total)) + 1
    # Capitalize the first letter of poly_name for display
    display_poly_name = poly_name.replace("_", " ").capitalize()

    if matches:
        print(
            f"{str(i + 1).rjust(count_size)}/{total} > {name} [{bench_time:.2f}s] => Correct"
        )
    else:
        print(
            f"{str(i + 1).rjust(count_size)}/{total} > {name} [{bench_time:.2f}s] => Wrong"
        )

        prefix = " " * len(
            f"{str(i + 1).rjust(count_size)}/{total} "
        )

        print(f"{prefix}> SG:", sg)
        print(f"{prefix}> PD:", pd)
        print(f"{prefix}> {display_poly_name} (actual):")
        print(f"{prefix}> {p_actual}")
        print(f"{prefix}> {display_poly_name} (expected):")
        print(f"{prefix}> {p_expected}")


def process_entry_worker(queue, index, knotinfo_entry, is_link, poly_func, poly_db_key, poly_name_for_display):
    """
    Worker function to process a single knot/link entry.
    To be run in a ProcessPoolExecutor.
    """
    name = knotinfo_entry['name']
    pd_code_key = 'pd_notation_vector' if is_link else 'pd_notation'
    pd_code_str = knotinfo_entry[pd_code_key]

    assert poly_db_key in knotinfo_entry

    p_expected_raw = knotinfo_entry[poly_db_key]
    p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

    pd_parser_format = '{{}}' if is_link else '[[]]'
    pd = PDCode.from_tuples(parse_nested_list(pd_code_str, pd_parser_format))
    sg = pd.to_signed_gauss_code()

    matches, p_actual, bench_time = process_polynomial(
        sg, p_expected, poly_func)
    queue.put((index, name, matches, p_actual, p_expected,
              sg, pd, bench_time, poly_name_for_display))


def result_processor_thread_func(queue, num_items_to_process, original_total_for_display, first_original_idx_processed):
    """
    Thread function to process results from the queue and print them in order.
    """
    results_buffer = {}
    num_items_printed = 0
    current_expected_original_idx = first_original_idx_processed

    while num_items_printed < num_items_to_process:
        try:
            item_tuple = queue.get()
        except Exception as e:
            print(f"Error getting from queue: {e}")
            continue

        original_idx_from_item = item_tuple[0]
        results_buffer[original_idx_from_item] = item_tuple

        while current_expected_original_idx in results_buffer:
            # Unpack the polynomial name
            idx_to_print, name, matches, p_actual, p_expected, sg, pd, bench_time, poly_name = results_buffer.pop(
                current_expected_original_idx)

            print_result(
                idx_to_print, original_total_for_display,
                name, matches, p_actual, p_expected, sg, pd, bench_time, poly_name
            )

            num_items_printed += 1
            current_expected_original_idx += 1

            if num_items_printed >= num_items_to_process:
                break


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
        '--polynomial',
        choices=list(AVAILABLE_POLYNOMIALS.keys()),
        default="kauffman",
        help=f"Polynomial type: {', '.join(AVAILABLE_POLYNOMIALS.keys())}, the default is the Kauffman F polynomial",
    )
    parser.add_argument(
        '--knots',
        action='store_true',
        help="Include knots from database",
    )
    parser.add_argument(
        '--links',
        action='store_true',
        help="Include links from database",
    )
    parser.add_argument(
        '-c', '--count',
        default=None,
        help="Number of knots to test",
    )
    parser.add_argument(
        '-s', '--skip',
        default=None,
        help="Number of knots to skip, to start processing from a specific index",
    )

    args = parser.parse_args()

    selected_poly_func, selected_poly_db_key = AVAILABLE_POLYNOMIALS[args.polynomial]
    # Use the database key as the name for display, or derive a more friendly one if needed
    poly_name_for_display = selected_poly_db_key

    print(f"Using polynomial: {poly_name_for_display}")

    skip_count = 0
    if args.skip is not None:
        skip_count = int(args.skip)

    manager = multiprocessing.Manager()

    if args.knots:
        knots_list_full = database_knotinfo.link_list()[2:]

        if args.count is not None:
            knots_list_to_process = knots_list_full[:int(args.count)]
        else:
            knots_list_to_process = knots_list_full

        original_total_count = len(knots_list_to_process)

        print(f"Processing {original_total_count} knots...")

        tasks_to_submit = []
        for i, knotinfo_entry in enumerate(knots_list_to_process):
            count_size = len(str(original_total_count)) + 1
            if i < skip_count:
                print(
                    f"{str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']} (skipped)"
                )
            elif selected_poly_db_key not in knotinfo_entry:
                print(
                    f"{str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']} (no {poly_name_for_display} found)"
                )
            else:
                tasks_to_submit.append((i, knotinfo_entry))

        num_tasks_actually_submitted = len(tasks_to_submit)

        if num_tasks_actually_submitted > 0:
            results_queue = manager.Queue()
            result_thread = threading.Thread(
                target=result_processor_thread_func,
                args=(results_queue, num_tasks_actually_submitted,
                      original_total_count, skip_count)
            )
            result_thread.start()

            with concurrent.futures.ProcessPoolExecutor() as executor:
                for original_idx, entry_data in tasks_to_submit:
                    executor.submit(
                        process_entry_worker,
                        results_queue, original_idx, entry_data, False,
                        selected_poly_func, selected_poly_db_key, poly_name_for_display
                    )

            result_thread.join()
        elif original_total_count > 0:
            print("All knots skipped.")

    if args.links:
        links_list_full = database_knotinfo.link_list(proper_links=True)[2:]

        if args.count is not None:
            links_list_to_process = links_list_full[:int(args.count)]
        else:
            links_list_to_process = links_list_full

        original_total_count = len(links_list_to_process)

        print(f"Processing {original_total_count} links...")

        tasks_to_submit = []
        for i, knotinfo_entry in enumerate(links_list_to_process):
            count_size = len(str(original_total_count)) + 1
            if i < skip_count:
                print(
                    f"{str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']} (skipped)"
                )
            elif selected_poly_db_key not in knotinfo_entry:
                print(
                    f"{str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']} (no {poly_name_for_display} found)"
                )
            else:
                tasks_to_submit.append((i, knotinfo_entry))

        num_tasks_actually_submitted = len(tasks_to_submit)

        if num_tasks_actually_submitted > 0:
            results_queue = manager.Queue()
            result_thread = threading.Thread(
                target=result_processor_thread_func,
                args=(results_queue, num_tasks_actually_submitted,
                      original_total_count, skip_count)
            )
            result_thread.start()

            with concurrent.futures.ProcessPoolExecutor() as executor:
                for original_idx, entry_data in tasks_to_submit:
                    executor.submit(
                        process_entry_worker,
                        results_queue, original_idx, entry_data, True,
                        selected_poly_func, selected_poly_db_key, poly_name_for_display
                    )

            result_thread.join()
        elif original_total_count > 0:
            print("All links skipped.")
