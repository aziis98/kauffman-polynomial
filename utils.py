import functools
from sympy import latex


import re


from typing import Literal

_global_depth = 0
_global_debug = True


def parse_nested_list(
    text: str,
    paren_spec: str = '{{}}',
    separator: str = ','
) -> list[list[int]]:
    outer_open: str = paren_spec[0]
    outer_close: str = paren_spec[3]
    inner_open: str = paren_spec[1]
    inner_close: str = paren_spec[2]

    text = text.strip()

    if not (text.startswith(outer_open) and text.endswith(outer_close)):
        raise ValueError(
            f"Mismatched outer delimiters: Expected '{outer_open}' and '{outer_close}'"
        )

    core_content = text[len(outer_open):-len(outer_close)].strip()
    inner_list_re_pattern = rf"{re.escape(inner_open)}\s*((?:\d+\s*(?:{re.escape(separator)}\s*\d+)*)?)\s*{re.escape(inner_close)}"

    return [
        [
            int(n.strip())
            for n in c.split(separator) if n.strip()
        ]
        if c.strip() else []
        for c in re.findall(inner_list_re_pattern, core_content)
    ]


def rotate_to_minimal(l):
    """
    Rotate a list to its minimal representation.
    """
    if len(l) == 0:
        return l
    min_index = l.index(min(l))
    return l[min_index:] + l[:min_index]


def sign_str(n, mode: Literal[None, 'sup', 'sub'] = None):
    SIGN_MAP = {
        None: {1: "+", -1: "-", 0: "0"},
        'sup': {1: "⁺", -1: "⁻", 0: "0"},
        'sub': {1: "₊", -1: "₋", 0: "₀"}
    }

    if n > 0:
        return SIGN_MAP[mode][1]
    elif n < 0:
        return SIGN_MAP[mode][-1]
    else:
        return SIGN_MAP[mode][0]


def sorted_tuple(t, key=None):
    """
    Sort a tuple and returns it as a tuple for easy destructuring.
    """
    return tuple(sorted(t, key=key))


def get_depth():
    """
    Get the current depth of the tree.
    """
    global _global_depth
    return _global_depth


def depth_print(*args):
    """
    Just print but with depth and tree symbols.
    """
    global _global_depth, _global_debug
    # Ensure all args are strings for join, and use tree prefix

    if _global_debug:
        print(f"{_global_depth * '│  '}{' '.join(map(str, args))}")


def log_input_output(func):
    """
    Decorator to log the inputs and outputs of a function with tree symbols.
    Logs function name, arguments, return value, and any exceptions raised.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _global_depth, _global_debug

        func_name = func.__name__
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        # Prefix for the current function call level
        call_prefix = _global_depth * '│  '

        # ascii error: ❌

        if _global_debug:
            print(
                f"{call_prefix}● {func_name}({signature})"
            )

        try:
            _global_depth += 1
            result = func(*args, **kwargs)
            _global_depth -= 1  # Decrement after function call, back to call_prefix level

            # try to simplify if sympy object
            new_result = result
            if hasattr(result, "simplify"):
                new_result = (
                    str(result.expand())
                    .replace("**", "^")
                    .replace("*", " * ")
                )

            if _global_debug:
                print(
                    f"{call_prefix}└─▶ {new_result}"
                )
            return result
        except Exception as e:
            if _global_debug and _global_depth == 0:
                print(
                    f"❌ {e!r}"
                )
            elif _global_debug:
                print(
                    f"❌ {args!r} {kwargs!r}"
                )
            _global_depth -= 1  # Ensure depth is restored before re-raising
            raise e

    return wrapper


_global_args_stack = []


def get_arg_stack():
    global _global_args_stack

    return _global_args_stack


def track_arg_stack(func):
    """
    Decorator to log the call depth of a function with tree symbols.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _global_args_stack

        _global_args_stack.append(args)
        result = func(*args, **kwargs)
        _global_args_stack.pop()

        return result

    return wrapper
