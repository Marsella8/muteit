from .objects import *

def get_dsl(terms: Iterable[Callable]) -> DSL:
    return DSL({f.__name__ : Operator(f) for f in terms})


def get_cg_signature(graph : ComputationGraph) -> Signature:
    pass