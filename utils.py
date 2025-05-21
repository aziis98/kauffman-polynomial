import functools
from sympy import latex


_global_depth = 0
_global_debug = True


def rotate_to_minimal(l):
    """
    Rotate a list to its minimal representation.
    """
    if len(l) == 0:
        return l
    min_index = l.index(min(l))
    return l[min_index:] + l[:min_index]


def sorted_tuple(t, key=None):
    """
    Sort a tuple and returns it as a tuple for easy destructuring.
    """
    return tuple(sorted(t, key=key))


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
