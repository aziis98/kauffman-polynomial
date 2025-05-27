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


homfly = Var("homfly")
L = Var("L")
v = Var("v")
z = Var("z")

# homfly equation: P(L+) / v - P(L-) * v = P(L0) * z
HOMFLY_EQUATION = (
    homfly(L.positive) / v - homfly(L.negative) * v
    ==
    homfly(L.splice_h) * z
)


def test_skein_dsl():
    print()
    print(format_expression_string(repr(HOMFLY_EQUATION)))

    sg_hopf = SGCode.from_tuples([
        [(+1, +1), (+2, -1)],
        [(-1, +1), (-2, -1)],
    ])
    sg_hopf_switched = sg_hopf.switch_crossing(1)
    sg_hopf_spliced_h = sg_hopf_switched.splice_h(1)

    assert HOMFLY_EQUATION.evaluate(
        {
            'homfly(L.positive)': homfly_polynomial(sg_hopf),
            'homfly(L.negative)': homfly_polynomial(sg_hopf_switched),
            'homfly(L.splice_h)': homfly_polynomial(sg_hopf_spliced_h),
            'v': sympy.symbols('v'),
            'z': sympy.symbols('z'),
        },
        eval_action=sympy.simplify
    ) is True


def test_skein_dsl_sympy():
    var_homfly_L_positive = sympy.symbols('homfly_L_positive')
    var_homfly_L_negative = sympy.symbols('homfly_L_negative')
    var_homfly_L_splice_h = sympy.symbols('homfly_L_splice_h')
    var_v = sympy.symbols('v')
    var_z = sympy.symbols('z')

    sympy_eq = HOMFLY_EQUATION.evaluate(
        {
            'homfly(L.positive)': var_homfly_L_positive,
            'homfly(L.negative)': var_homfly_L_negative,
            'homfly(L.splice_h)': var_homfly_L_splice_h,
            'v': var_v,
            'z': var_z,
        },
        equality=sympy.Eq,
    )

    print("SymPy equation:")
    print(format_expression_string(repr(sympy_eq)))

    # solve the equation for homfly(L.positive)
    homfly_positive_solution = sympy.solve(
        sympy_eq,
        var_homfly_L_positive
    )
    print("homfly(L.positive) solution:")
    print(f"{homfly_positive_solution}")
    assert len(homfly_positive_solution) == 1
    assert homfly_positive_solution[0].expand() == (
        (var_homfly_L_splice_h * var_z + var_homfly_L_negative * var_v) * var_v
    ).expand()

    # solve the equation for homfly(L.negative)
    homfly_negative_solution = sympy.solve(
        sympy_eq,
        var_homfly_L_negative
    )
    print("homfly(L.negative) solution:")
    print(f"{homfly_negative_solution}")
    assert len(homfly_negative_solution) == 1
    assert homfly_negative_solution[0].expand() == (
        (var_homfly_L_positive / var_v - var_homfly_L_splice_h * var_z) / var_v
    ).expand()
