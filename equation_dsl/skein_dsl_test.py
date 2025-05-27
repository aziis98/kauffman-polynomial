from equation_dsl import Var
from codes import SGCode
from homfly import homfly_polynomial


import sympy


def format_expression_string(s: str, w: int = 4) -> str:
    lines = []
    level = 0
    indent = " " * w
    buf = ""
    for char in s:
        if char == '(':
            lines.append(indent * level + buf + ':')
            level += 1
            buf = ""
        elif char == ')':
            if buf:
                lines.append(indent * level + buf)
                buf = ""
            level -= 1
        elif char == ',':
            if buf:
                lines.append(indent * level + buf + char)
            else:
                lines[-1] += char if lines else lines.append(
                    indent * level + char)
            buf = ""
        elif not char.isspace():
            buf += char
    if buf:
        lines.append(indent * level + buf)
    return "\n".join(lines)


def test_skein_dsl():
    print()

    homfly = Var("homfly")

    L = Var("L")

    v = Var("v")
    z = Var("z")

    # homfly equation: P(L+) / v - P(L-) * v = P(L0) * z
    equation = (
        homfly(L.positive) / v - homfly(L.negative) * v
        ==
        homfly(L.positive.splice) * z
    )
    print(format_expression_string(repr(equation)))

    sg_hopf = SGCode.from_tuples([
        [(+1, +1), (+2, -1)],
        [(-1, +1), (-2, -1)],
    ])
    sg_hopf_switched = sg_hopf.switch_crossing(1)
    sg_hopf_spliced_h = sg_hopf_switched.splice_h(1)

    assert equation.evaluate(
        {
            'homfly(L.positive)': homfly_polynomial(sg_hopf),
            'homfly(L.negative)': homfly_polynomial(sg_hopf_switched),
            'homfly(L.positive.splice)': homfly_polynomial(sg_hopf_spliced_h),
            'v': sympy.symbols('v'),
            'z': sympy.symbols('z'),
        },
        eval_action=sympy.simplify
    ) is True
