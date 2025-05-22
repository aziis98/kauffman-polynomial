from codes import PDCode
from kauffman_v2 import f_polynomial
from sympy import parse_expr, symbols, init_printing
from utils import parse_nested_list
from contextlib import redirect_stdout
import database_knotinfo
import io
import time


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


def process_polynomial(k_info, pd, sg) -> bool:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    print(f"{"-" * 30}[{k_info['name'].center(20)}]{"-" * 30}")

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

    p_expected = parse_expr(
        k_info['kauffman_polynomial'].replace('^', '**')
    ).expand()

    print("SG:", sg)
    print("PD:", pd)
    print("Kauffman (actual):")
    print(p_actual)
    print("Kauffman (expected):")
    print(p_expected)

    if p_actual == p_expected:
        print(f"=> Correct {bench_time:.2f}s")
        return True
    else:
        print("=> Wrong")
        return False


def process_knotinfo_polynomial(k_info, pd_key, paren_spec) -> bool:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    pd_notation_str = k_info[pd_key]
    pd = parse_nested_list(pd_notation_str, paren_spec=paren_spec)

    return process_polynomial(
        k_info,
        pd_notation_str,
        PDCode.from_tuples(pd).to_signed_gauss_code(),  # type: ignore
    )


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


list_of_links = database_knotinfo.link_list(proper_links=True)[2:]
process_knotinfo_polynomial(list_of_links[1500], 'pd_notation_vector', '{{}}')


def knotinfo_by_name(db, name):
    """
    Find knot information by name in the database.
    """
    return next(
        (knot for knot in db if knot['name'] == name),
        None
    )


# test_polynomial(
#     {
#         'name': '?',
#         'kauffman_polynomial': '1',
#     },
#     '?',
#     SGCode.from_tuples([
#         [
#             (+4, -1), (+1, +1), (+2, +1), (-5, +1),
#         ],
#         [
#             (-6, +1), (-4, -1), (+3, +1), (-2, +1),
#         ],
#         [
#             (-1, +1), (+6, +1), (+5, +1), (-3, +1),
#         ]
#     ]),
# )

# test_polynomial(
#     {
#         'name': '?',
#         'kauffman_polynomial': '1',
#     },
#     '?',
#     SGCode.from_tuples([
#         [(+1, -1), (+6, +1), (+5, +1), (-3, +1)],
#         [(+4, -1), (-1, -1), (+2, +1), (-5, +1)],
#         [(-6, +1), (-4, -1), (+3, +1), (-2, +1)]
#     ]),
# )
