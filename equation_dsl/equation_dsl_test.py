# test_equation_dsl.py
import pytest
from equation_dsl import (
    Literal,
    Var,
    BinaryOp,
    UnaryOp,
    Equation,
    PropertyAccess,
    FunctionCall,
)


def test_number_evaluation():
    num = Literal(5)
    assert num.evaluate({}) == 5


def test_variable_evaluation():
    var = Var("x")
    assert var.evaluate({"x": 10}) == 10
    with pytest.raises(ValueError):
        var.evaluate({})


def test_binary_operation_evaluation():
    x = Literal(5)
    y = Literal(10)
    add_op = BinaryOp(x, "+", y)
    assert add_op.evaluate({}) == 15
    sub_op = BinaryOp(y, "-", x)
    assert sub_op.evaluate({}) == 5
    mul_op = BinaryOp(x, "*", y)
    assert mul_op.evaluate({}) == 50
    div_op = BinaryOp(y, "/", x)
    assert div_op.evaluate({}) == 2.0
    pow_op = BinaryOp(x, "**", Literal(2))
    assert pow_op.evaluate({}) == 25


def test_unary_operation_evaluation():
    x = Literal(5)
    neg_op = UnaryOp("-", x)
    assert neg_op.evaluate({}) == -5
    pos_op = UnaryOp("+", x)
    assert pos_op.evaluate({}) == 5


def test_equation_evaluation():
    x = Literal(5)
    y = Literal(10)

    eq = Equation(x, y)
    assert not eq.evaluate({})

    eq2 = Equation(x, Literal(5))
    assert eq2.evaluate({})


def test_property_access_evaluation():
    class TestObject:

        def __init__(self, a):
            self.a = a
    obj = TestObject(20)
    obj_var = Var("obj")
    prop_access = PropertyAccess(obj_var, "a")
    assert prop_access.evaluate({"obj": obj}) == 20
    with pytest.raises(ValueError):
        PropertyAccess(obj_var, "b").evaluate({"obj": obj})


def test_function_call_evaluation():
    class TestObject:

        def add(self, x, y):
            return x + y
    obj = TestObject()
    obj_var = Var("obj")
    func_call = FunctionCall(
        PropertyAccess(obj_var, "add"), Literal(5), Literal(7)
    )
    assert func_call.evaluate({"obj": obj}) == 12

    with pytest.raises(TypeError):
        FunctionCall(PropertyAccess(obj_var, "add"),
                     Literal(5)).evaluate({"obj": obj})


def test_proxy_variable_evaluation():
    proxy_var = Var("obj")
    assert proxy_var.evaluate({"obj": 42}) == 42
    with pytest.raises(ValueError):
        proxy_var.evaluate({})


def test_proxy_property_access():
    class TestObject:

        def __init__(self, a):
            self.a = a
    obj = TestObject(10)
    proxy_var = Var("test_obj")
    prop_access = PropertyAccess(proxy_var, "a")
    assert prop_access.target == proxy_var
    assert prop_access.property_name == "a"
    assert prop_access.evaluate({"test_obj": obj}) == 10


def test_proxy_function_call():
    class TestObject:

        def add(self, x, y):
            return x + y
    obj = TestObject()
    test_var = Var("test_obj")
    func_call = test_var.add(5, 7)

    assert len(func_call.args) == 2
    assert func_call.evaluate({"test_obj": obj}) == 12


def test_proxy_property_operations():
    class TestObject:
        def __init__(self, a):
            self.a = a

    obj = TestObject(5)
    proxy_var = Var("test_obj")

    assert (proxy_var.a + 5).evaluate({"test_obj": obj}) == 10
    assert (proxy_var.a - 2).evaluate({"test_obj": obj}) == 3
    assert (proxy_var.a * 3).evaluate({"test_obj": obj}) == 15
    assert (proxy_var.a / 2).evaluate({"test_obj": obj}) == 2.5
    assert (proxy_var.a**2).evaluate({"test_obj": obj}) == 25
    assert (5 + proxy_var.a).evaluate({"test_obj": obj}) == 10
    assert (10 - proxy_var.a).evaluate({"test_obj": obj}) == 5
    assert (3 * proxy_var.a).evaluate({"test_obj": obj}) == 15
    assert (10 / proxy_var.a).evaluate({"test_obj": obj}) == 2
    assert (2**proxy_var.a).evaluate({"test_obj": obj}) == 32
    assert (proxy_var.a == 5).evaluate({"test_obj": obj}) is True
    assert (-proxy_var.a).evaluate({"test_obj": obj}) == -5
    assert (+proxy_var.a).evaluate({"test_obj": obj}) == 5
