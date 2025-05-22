from codes import SGCode, PDCode
from kauffman_v2 import f_polynomial
from sympy import parse_expr, symbols, init_printing
from utils import parse_nested_list
from contextlib import redirect_stdout
import database_knotinfo
import io


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


def test_polynomial(k_info, pd, sg) -> bool:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    print(f"{"-" * 30}[{k_info['name'].center(20)}]{"-" * 30}")

    stdout_buff = io.StringIO()
    with redirect_stdout(stdout_buff):
        try:
            p_actual = f_polynomial(sg).expand()
        except Exception as e:
            print(f"Error: {e}")
            p_actual = None

    p_expected = parse_expr(
        k_info['kauffman_polynomial'].replace('^', '**')
    ).expand()

    if p_actual == p_expected:
        print("SG:", sg)
        print("=> Correct")
        return True
    else:
        print(stdout_buff.getvalue())

        print("PD:", pd)
        print("SG:", sg)
        print("=> Wrong")
        print("Kauffman (actual):")
        print(p_actual)
        print("Kauffman (expected):")
        print(p_expected)
        return False


def test_knotinfo_polynomial(k_info, pd_key, paren_spec) -> bool:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    pd_notation_str = k_info[pd_key]
    pd = parse_nested_list(pd_notation_str, paren_spec=paren_spec)

    return test_polynomial(
        k_info,
        pd_notation_str,
        PDCode.from_tuples(pd).to_signed_gauss_code(),  # type: ignore
    )


# knots_list_1 = database_knotinfo.link_list()[2:25]
# for k_data in knots_list_1:
#     result = test_knotinfo_polynomial(k_data, 'pd_notation', '[[]]')
#     if not result:
#         break


knots_list_2 = database_knotinfo.link_list(proper_links=True)[2:50]
for k_data in knots_list_2:
    result = test_knotinfo_polynomial(k_data, 'pd_notation_vector', '{{}}')
    if not result:
        break


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
