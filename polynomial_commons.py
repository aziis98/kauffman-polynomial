import functools
import utils
from codes import SGCode
from typing import Callable, Literal
from sympy import Poly


OptimizationType = Literal['expand', 'relabel', 'to_minimal']


def polynomial_wrapper(optimizations: set[OptimizationType] = {'expand'}):
    def decorator(func: Callable[[SGCode], Poly]) -> Callable[[SGCode], Poly]:
        @functools.wraps(func)
        def wrapper(link: SGCode):
            pb = utils.progress_bar.get()
            pb.update(1)

            # First we convert to minimal rotated form and only then we relabel,
            # this ensures a consistent indexing for the cache.
            if 'to_minimal' in optimizations:
                link = link.to_minimal()
            if 'relabel' in optimizations:
                link = link.relabel()

            result = func(link)

            # finally, for consistency, we expand the result
            if 'expand' in optimizations:
                result = result.expand()

            return result

        return wrapper

    return decorator
