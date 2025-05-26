import functools
import utils
from codes import SGCode
from typing import Callable, Literal
from sympy import Poly


OptimizationType = Literal['expand', 'relabel', 'to_minimal']


def polynomial_wrapper(optimizations: set[OptimizationType] = {'expand'}):
    """
    A decorator factory for polynomial computation functions that applies common optimizations.

    This decorator wraps functions that compute polynomials from SGCode objects, providing
    a standardized way to apply preprocessing and postprocessing optimizations.

    Args:
        optimizations (set[OptimizationType], optional): A set of optimization types to apply.
            Defaults to {'expand'}. Available optimizations:
            - 'to_minimal': Convert the link to minimal rotated form before processing
            - 'relabel': Relabel the link for consistent indexing (useful for caching)
            - 'expand': Expand the resulting polynomial for consistency

    Returns:
        Callable: A decorator that can be applied to functions with signature
        (SGCode) -> Poly to add the specified optimizations.

    Note:
        The decorator also updates a progress bar on each function call.
        Optimizations are applied in a specific order: to_minimal, then relabel
        (before function execution), then expand (after function execution).
    """
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

            # Finally, for consistency, we expand the result
            if 'expand' in optimizations:
                result = result.expand()

            return result

        return wrapper

    return decorator
