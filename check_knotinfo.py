from codes import SGCode, PDCode
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
) -> None:
    """
    Print the result of the polynomial check.
    """
    count_size = len(str(total)) + 1

    if matches:
        print(
            f"{str(i + 1).rjust(count_size)}/{total} > {name.ljust(14)} [{bench_time:.2f}s] => Correct"
        )
    else:
        print(
            f"{str(i + 1).rjust(count_size)}/{total} > {name.ljust(14)} [{bench_time:.2f}s] => Wrong"
        )

        prefix = " " * len(
            f"{str(i + 1).rjust(count_size)}/{total} "
        )

        print(f"{prefix}> SG:", sg)
        print(f"{prefix}> PD:", pd)
        print(f"{prefix}> Kauffman (actual):")
        print(f"{prefix}> {p_actual}")
        print(f"{prefix}> Kauffman (expected):")
        print(f"{prefix}> {p_expected}")


def process_entry_worker(queue, index, total_count_for_display, knotinfo_entry, is_link):
    """
    Worker function to process a single knot/link entry.
    To be run in a ProcessPoolExecutor.
    """
    name = knotinfo_entry['name']
    pd_code_key = 'pd_notation_vector' if is_link else 'pd_notation'
    pd_code_str = knotinfo_entry[pd_code_key]
    p_expected_raw = knotinfo_entry['kauffman_polynomial']

    p_expected = parse_expr(p_expected_raw.replace('^', '**')).expand()

    pd_parser_format = '{{}}' if is_link else '[[]]'
    pd = PDCode.from_tuples(parse_nested_list(pd_code_str, pd_parser_format))
    sg = pd.to_signed_gauss_code()

    matches, p_actual, bench_time = process_polynomial(sg, p_expected)
    queue.put((index, name, matches, p_actual, p_expected, sg, pd, bench_time))


def result_processor_thread_func(queue, num_items_to_process, original_total_for_display, first_original_idx_processed):
    """
    Thread function to process results from the queue and print them in order.
    """
    results_buffer = {}
    num_items_printed = 0
    current_expected_original_idx = first_original_idx_processed

    while num_items_printed < num_items_to_process:
        try:
            # Blocking get, timeout can be added if necessary
            item_tuple = queue.get()
        except Exception as e:  # Should ideally be more specific if queue.Empty or other exceptions are expected
            print(f"Error getting from queue: {e}")
            # Potentially break or continue based on error handling strategy
            continue

        original_idx_from_item = item_tuple[0]
        results_buffer[original_idx_from_item] = item_tuple

        while current_expected_original_idx in results_buffer:
            idx_to_print, name, matches, p_actual, p_expected, sg, pd, bench_time = results_buffer.pop(
                current_expected_original_idx)

            print_result(idx_to_print, original_total_for_display,
                         name, matches, p_actual, p_expected, sg, pd, bench_time)

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

    manager = multiprocessing.Manager()

    if args.all_knots:
        knots_list_full = database_knotinfo.link_list()[2:]

        if args.count is not None:
            knots_list_to_process = knots_list_full[:int(args.count)]
        else:
            knots_list_to_process = knots_list_full

        original_total_count = len(knots_list_to_process)

        print(f"Processing {original_total_count} knots...")

        tasks_to_submit = []
        for i, knotinfo_entry in enumerate(knots_list_to_process):
            if i < skip_count:
                count_size = len(str(original_total_count)) + 1
                print(
                    f"Skipping {str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']}"
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
                    executor.submit(process_entry_worker, results_queue,
                                    original_idx, original_total_count, entry_data, False)

            result_thread.join()
        elif original_total_count > 0:
            print("All knots skipped.")

    if args.all_links:
        links_list_full = database_knotinfo.link_list(proper_links=True)[2:]

        if args.count is not None:
            links_list_to_process = links_list_full[:int(args.count)]
        else:
            links_list_to_process = links_list_full

        original_total_count = len(links_list_to_process)

        print(f"Processing {original_total_count} links...")

        tasks_to_submit = []
        for i, knotinfo_entry in enumerate(links_list_to_process):
            if i < skip_count:
                count_size = len(str(original_total_count)) + 1
                print(
                    f"Skipping {str(i + 1).rjust(count_size)}/{original_total_count} > {knotinfo_entry['name']}"
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
                    executor.submit(process_entry_worker, results_queue,
                                    original_idx, original_total_count, entry_data, True)

            result_thread.join()
        elif original_total_count > 0:
            print("All links skipped.")
