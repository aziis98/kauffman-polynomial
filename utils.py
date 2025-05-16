import functools


_global_depth = 0


def depth_print(*args):
    """
    Just print but with depth and tree symbols.
    """
    global _global_depth
    # Ensure all args are strings for join, and use tree prefix
    print(f"{_global_depth * '│  '}{' '.join(map(str, args))}")


def log_input_output(func):
    """
    Decorator to log the inputs and outputs of a function with tree symbols.
    Logs function name, arguments, return value, and any exceptions raised.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _global_depth

        func_name = func.__name__
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        # Prefix for the current function call level
        call_prefix = _global_depth * '│  '

        # ascii error: ❌

        print(
            f"{call_prefix}● {func_name}({signature})"
        )

        try:
            _global_depth += 1
            result = func(*args, **kwargs)
            _global_depth -= 1  # Decrement after function call, back to call_prefix level

            print(
                f"{call_prefix}└─▶ {result!r}"
            )
            return result
        except Exception as e:
            # _global_depth was incremented before func call.
            # If exception occurs in func, _global_depth is 1 level too deep.
            # We print the exception at the call_prefix level.
            print(
                f"{call_prefix}└─▶ ❌ {e!r}"
            )
            _global_depth -= 1  # Ensure depth is restored before re-raising
            raise e

    return wrapper
