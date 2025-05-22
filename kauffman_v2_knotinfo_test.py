from codes import PDCode
from kauffman_v2 import f_polynomial
from sympy import parse_expr, symbols, init_printing
from utils import parse_nested_list
from contextlib import redirect_stdout
import database_knotinfo
import io


a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


def test_knot_polynomial(k_info, pd_key, paren_spec) -> bool:
    """
    Tests the Kauffman polynomial for a given knot.
    """
    print(f"{"-" * 30}[{k_info['name'].center(20)}]{"-" * 30}")

    pd_notation_str = k_info[pd_key]
    pd = parse_nested_list(pd_notation_str, paren_spec=paren_spec)

    sg = PDCode.from_tuples(pd).to_signed_gauss_code()  # type: ignore

    stdout_buff = io.StringIO()
    with redirect_stdout(stdout_buff):
        p_actual = f_polynomial(sg).expand()

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


# knots_list_1 = database_knotinfo.link_list()[2:50]
# for k_data in knots_list_1:
#     result = test_knot_polynomial(k_data, 'pd_notation', '[[]]')
#     if not result:
#         break

knots_list_2 = database_knotinfo.link_list(proper_links=True)[2:50]
for k_data in knots_list_2:
    result = test_knot_polynomial(k_data, 'pd_notation_vector', '{{}}')
    if not result:
        break
