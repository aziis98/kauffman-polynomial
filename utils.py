import logging
import functools


_global_depth = 0


def depth_print(*args):
    """
    Just print but with depth
    """
    global _global_depth
    print(f"{_global_depth * '  '}{' '.join(args)}")


def log_input_output(func):
    """
    Decorator to log the inputs and outputs of a function.
    Logs function name, arguments, return value, and any exceptions raised.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _global_depth

        func_name = func.__name__
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        print(
            f"{_global_depth * '  '}{func_name}: {signature}"
        )

        try:
            _global_depth += 1
            result = func(*args, **kwargs)
            _global_depth -= 1

            print(
                f"{_global_depth * '  '}=> {result!r}"
            )
            return result
        except Exception as e:
            print(
                f"{_global_depth * '  '}!> {e!r}"
            )
            raise e

    return wrapper
