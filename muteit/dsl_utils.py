from .objects import *
from typing import Iterable

def get_dsl(terms: Iterable[Callable]) -> DSL:
    return DSL({f.__name__: Operator(f) for f in terms})
