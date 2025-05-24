import operator
from typing import Union, Dict, Any
import math


def _ensure_expression(value):
    if isinstance(value, Expression):
        return value
    elif isinstance(value, (int, float)):
        return Number(value)
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


class Variable:
    """Represents a variable in an equation"""

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Variable('{self.name}')"


class Expression:
    """Base class for mathematical expressions"""

    def __add__(self, other):
        return BinaryOp(self, '+', other)

    def __sub__(self, other):
        return BinaryOp(self, '-', other)

    def __mul__(self, other):
        return BinaryOp(self, '*', other)

    def __truediv__(self, other):
        return BinaryOp(self, '/', other)

    def __pow__(self, other):
        return BinaryOp(self, '**', other)

    def __radd__(self, other):
        return BinaryOp(other, '+', self)

    def __rsub__(self, other):
        return BinaryOp(other, '-', self)

    def __rmul__(self, other):
        return BinaryOp(other, '*', self)

    def __rtruediv__(self, other):
        return BinaryOp(other, '/', self)

    def __rpow__(self, other):
        return BinaryOp(other, '**', self)

    def __neg__(self):
        return UnaryOp('-', self)

    def __pos__(self):
        return UnaryOp('+', self)

    def __eq__(self, other):  # type: ignore
        """Override == operator to create equations"""
        return Equation(self, other)


class Number(Expression):
    """Represents a numeric value"""

    def __init__(self, value: Union[int, float]):
        self.value = value

    def evaluate(self, _: Dict[str, Any]) -> Union[int, float]:
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Number({self.value})"


class Var(Expression, Variable):
    """Represents a variable that can be used in expressions"""

    def __init__(self, name: str):
        Variable.__init__(self, name)
        Expression.__init__(self)

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        if self.name not in variables:
            raise ValueError(f"Variable '{self.name}' is not defined")
        return variables[self.name]

    def __str__(self):
        return self.name


class PropertyAccess(Expression):
    """Represents property access like x.a"""

    def __init__(self, obj: Expression, property_name: str):
        self.obj = obj
        self.property_name = property_name

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        obj_val = self.obj.evaluate(variables)  # type: ignore
        if hasattr(obj_val, self.property_name):
            return getattr(obj_val, self.property_name)
        else:
            # If the object doesn't have the property, look for it in variables
            prop_key = f"{self.obj}.{self.property_name}"
            if variables and prop_key in variables:
                return variables[prop_key]
            raise ValueError(
                f"Property '{self.property_name}' not found on {self.obj}")

    def __str__(self):
        return f"{self.obj}.{self.property_name}"


class FunctionCall(Expression):
    """Represents function calls like x.a(y, z)"""

    def __init__(self, obj: Expression, func_name: str, *args):
        self.obj = obj
        self.func_name = func_name
        self.args = [_ensure_expression(arg) for arg in args]

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        obj_val = self.obj.evaluate(variables)  # type: ignore
        arg_vals = [
            arg.evaluate(variables)  # type: ignore
            for arg in self.args
        ]

        # First try to call the method on the object
        if hasattr(obj_val, self.func_name):
            method = getattr(obj_val, self.func_name)
            if callable(method):
                return method(*arg_vals)  # type: ignore

        # If that fails, look for a custom function in variables
        func_key = f"{self.obj}.{self.func_name}"
        if variables and func_key in variables:
            func = variables[func_key]
            if callable(func):
                return func(obj_val, *arg_vals)  # type: ignore

        # As a fallback, treat it as a mathematical function notation
        # like f(x) = x^2, where we look up the function definition
        if variables:
            # Look for function definitions like "x.a" -> lambda obj, *args: ...
            if func_key in variables and callable(variables[func_key]):
                return variables[func_key](obj_val, *arg_vals)

        print(f"Available functions for {self.obj}:")
        for key in variables.keys():
            if key.startswith(f"{self.obj}."):
                print(f"  - {key}")

        raise ValueError(
            f"Function '{self.func_name}' not found on {self.obj}"
        )

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.obj}.{self.func_name}({args_str})"


class ProxyVar(Expression, Variable):
    """A proxy variable that intercepts property access and function calls"""

    def __init__(self, name: str):
        Variable.__init__(self, name)
        Expression.__init__(self)

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        if self.name not in variables:
            raise ValueError(f"Variable '{self.name}' is not defined")

        return variables[self.name]

    def __getattr__(self, name: str):
        """Intercept property access to create PropertyAccess objects"""
        if name.startswith('_'):  # Don't intercept private attributes
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'")

        return ProxyProperty(self, name)

    def __call__(self, *args):
        """Intercept function calls to create FunctionCall objects"""
        return FunctionCall(self, self.name, *args)

    def __str__(self):
        return self.name


class ProxyProperty:
    """Represents a property that can be accessed or called as a function"""

    def __init__(self, obj: Expression, property_name: str):
        self.obj = obj
        self.property_name = property_name

    def __call__(self, *args):
        """When called as a function, create a FunctionCall expression"""
        return FunctionCall(self.obj, self.property_name, *args)

    def __add__(self, other):
        return PropertyAccess(self.obj, self.property_name) + other

    def __sub__(self, other):
        return PropertyAccess(self.obj, self.property_name) - other

    def __mul__(self, other):
        return PropertyAccess(self.obj, self.property_name) * other

    def __truediv__(self, other):
        return PropertyAccess(self.obj, self.property_name) / other

    def __pow__(self, other):
        return PropertyAccess(self.obj, self.property_name) ** other

    def __radd__(self, other):
        return other + PropertyAccess(self.obj, self.property_name)

    def __rsub__(self, other):
        return other - PropertyAccess(self.obj, self.property_name)

    def __rmul__(self, other):
        return other * PropertyAccess(self.obj, self.property_name)

    def __rtruediv__(self, other):
        return other / PropertyAccess(self.obj, self.property_name)

    def __rpow__(self, other):
        return other ** PropertyAccess(self.obj, self.property_name)

    def __eq__(self, other):
        return PropertyAccess(self.obj, self.property_name) == other

    def __neg__(self):
        return -PropertyAccess(self.obj, self.property_name)

    def __pos__(self):
        return +PropertyAccess(self.obj, self.property_name)

    def __str__(self):
        return f"{self.obj}.{self.property_name}"


class BinaryOp(Expression):
    """Represents a binary operation between two expressions"""

    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
    }

    def __init__(self, left: Union[Expression, int, float], op: str, right: Union[Expression, int, float]):
        self.left = _ensure_expression(left)
        self.op = op
        self.right = _ensure_expression(right)

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        left_val = self.left.evaluate(variables)  # type: ignore
        right_val = self.right.evaluate(variables)  # type: ignore

        if self.op not in self.OPERATORS:
            raise ValueError(f"Unsupported operator: {self.op}")

        return self.OPERATORS[self.op](left_val, right_val)

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"


class UnaryOp(Expression):
    """Represents a unary operation on an expression"""

    OPERATORS = {
        '-': operator.neg,
        '+': operator.pos,
    }

    def __init__(self, op: str, operand: Union[Expression, int, float]):
        self.op = op
        self.operand = self._ensure_expression(operand)

    def _ensure_expression(self, value):
        if isinstance(value, Expression):
            return value
        elif isinstance(value, (int, float)):
            return Number(value)
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        operand_val = self.operand.evaluate(variables)  # type: ignore

        if self.op not in self.OPERATORS:
            raise ValueError(f"Unsupported unary operator: {self.op}")

        return self.OPERATORS[self.op](operand_val)

    def __str__(self):
        return f"{self.op}{self.operand}"


class Equation:
    """Represents an equation with left and right sides"""

    def __init__(self, left: Expression, right: Expression):
        self.left = _ensure_expression(left)
        self.right = _ensure_expression(right)

    def evaluate_left(self, variables: Dict[str, Any]) -> Union[int, float]:
        return self.left.evaluate(variables)  # type: ignore

    def evaluate_right(self, variables: Dict[str, Any]) -> Union[int, float]:
        return self.right.evaluate(variables)  # type: ignore

    def is_satisfied(self, variables: Dict[str, Any], tolerance: float = 1e-10) -> bool:
        """Check if the equation is satisfied given variable values"""
        print(f"Environment: {variables!r}")

        left_val = self.evaluate_left(variables)
        right_val = self.evaluate_right(variables)

        return left_val == right_val or abs(left_val - right_val) < tolerance

    def __str__(self):
        return f"{self.left} = {self.right}"

# Mathematical functions


class MathFunction(Expression):
    """Represents mathematical functions like sin, cos, log, etc."""

    FUNCTIONS = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'ln': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'sqrt': math.sqrt,
        'abs': abs,
    }

    def __init__(self, func_name: str, argument: Union[Expression, int, float]):
        self.func_name = func_name
        self.argument = _ensure_expression(argument)

    def evaluate(self, variables: Dict[str, Any]) -> Union[int, float]:
        if self.func_name not in self.FUNCTIONS:
            raise ValueError(f"Unsupported function: {self.func_name}")

        arg_val = self.argument.evaluate(variables)  # type: ignore
        return self.FUNCTIONS[self.func_name](arg_val)

    def __str__(self):
        return f"{self.func_name}({self.argument})"
