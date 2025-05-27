from __future__ import annotations

import operator
from typing import Dict, Any, Callable
from sympy import Symbol


class Expression:
    """Base class for mathematical expressions"""

    @staticmethod
    def ensure(value: Any) -> Expression:
        if isinstance(value, Expression):
            return value
        elif isinstance(value, (int, float, str, bool, Symbol)):
            return Literal(value)
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

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

    def __getattr__(self, item: str) -> PropertyAccess:
        """Access properties like x.a"""
        return PropertyAccess(self, item)

    def __call__(self, *args) -> FunctionCall:
        """Call functions like f(y, z)"""
        return FunctionCall(self, *args)

    def __eq__(self, other) -> Expression:  # type: ignore
        return Equation(self, other)

    def evaluate(self,
                 variables: Dict[str, Any],
                 eval_action: Callable[[Any], Any] | None = None,
                 equality=operator.eq
                 ) -> Any:
        """Evaluate the expression given a dictionary of variable values"""
        raise NotImplementedError("Subclasses must implement evaluate method")


class Literal(Expression):
    """Represents a numeric value"""

    def __init__(self, value: Any):
        self.value = value

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        if eval_action:
            return eval_action(self.value)

        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Literal({self.value!r})"


class Var(Expression):
    """Represents a variable that can be used in expressions"""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        if self.name not in variables:
            raise ValueError(f"Variable '{self.name}' is not defined")

        if eval_action:
            return eval_action(variables[self.name])

        return variables[self.name]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var({self.name})"


class PropertyAccess(Expression):
    """Represents property access like x.a"""

    def __init__(self, receiver: Expression, property_name: str):
        self.target = Expression.ensure(receiver)
        self.property_name = property_name

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        obj_val = self.target.evaluate(variables, eval_action, equality)

        if hasattr(obj_val, self.property_name):
            result = getattr(obj_val, self.property_name)
            if eval_action:
                return eval_action(result)
            return result

        prop_key = f"{self.target}.{self.property_name}"
        if variables and prop_key in variables:
            if eval_action:
                return eval_action(variables[prop_key])
            return variables[prop_key]

        raise ValueError(
            f"Property '{self.property_name}' not found on {self.target}"
        )

    def __str__(self):
        return f"{self.target}.{self.property_name}"

    def __repr__(self):
        return f"PropertyAccess({self.target!r}, {self.property_name!r})"


class FunctionCall(Expression):
    """Represents function calls like f(y, z)"""

    def __init__(self, obj: Expression, *args):
        self.receiver = obj
        self.args = [Expression.ensure(arg) for arg in args]

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        # Check if the function is already evaluated in variables, this
        # supports a special syntax like "a.b(c, d)"
        func_name = f"{str(self.receiver)}({','.join(str(arg) for arg in self.args)})"
        if func_name in variables:
            return variables[func_name]

        receiver_val = self.receiver.evaluate(variables, eval_action, equality)
        arg_vals: list[Any] = [
            arg.evaluate(variables, eval_action, equality)
            for arg in self.args
        ]

        if not hasattr(receiver_val, '__call__'):
            raise ValueError(f"Object '{self.receiver}' is not callable")

        if eval_action:
            return eval_action(receiver_val(*arg_vals))

        return receiver_val(*arg_vals)

    def __str__(self):
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{self.receiver}({args_str})"

    def __repr__(self):
        args_repr = ', '.join(repr(arg) for arg in self.args)
        return f"FunctionCall({self.receiver!r}, {args_repr})"


class BinaryOp(Expression):
    """Represents a binary operation between two expressions"""

    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
    }

    def __init__(self, left: Any, op: str, right: Any):
        self.left = Expression.ensure(left)
        self.op = op
        self.right = Expression.ensure(right)

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        left_val = self.left.evaluate(variables, eval_action, equality)
        right_val = self.right.evaluate(variables, eval_action, equality)

        if self.op not in self.OPERATORS:
            raise ValueError(f"Unsupported operator: {self.op}")

        result = self.OPERATORS[self.op](left_val, right_val)

        if eval_action:
            return eval_action(result)

        return result

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return f"BinaryOp({self.op!r}, {self.left!r}, {self.right!r})"


class UnaryOp(Expression):
    """Represents a unary operation on an expression"""

    OPERATORS = {
        '-': operator.neg,
        '+': operator.pos,
    }

    def __init__(self, op: str, operand: Any):
        self.op = op
        self.operand = Expression.ensure(operand)

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        operand_val = self.operand.evaluate(variables, eval_action, equality)

        if self.op not in self.OPERATORS:
            raise ValueError(f"Unsupported unary operator: {self.op}")

        result = self.OPERATORS[self.op](operand_val)

        if eval_action:
            return eval_action(result)
        return result

    def __str__(self):
        return f"{self.op}{self.operand}"

    def __repr__(self):
        return f"UnaryOp({self.op!r}, {self.operand!r})"


class Equation(Expression):
    """Represents an equation with left and right sides"""

    def __init__(self, left: Any, right: Any):
        self.left = Expression.ensure(left)
        self.right = Expression.ensure(right)

    def evaluate(self, variables: Dict[str, Any], eval_action: Callable[[Any], Any] | None = None, equality=operator.eq) -> Any:
        left_val = self.left.evaluate(variables, eval_action, equality)
        right_val = self.right.evaluate(variables, eval_action, equality)

        print(f"Evaluating equation: {left_val} == {right_val}")

        return equality(left_val, right_val)

    def __str__(self):
        return f"{self.left} = {self.right}"

    def __repr__(self):
        return f"Equation({self.left!r}, {self.right!r})"
