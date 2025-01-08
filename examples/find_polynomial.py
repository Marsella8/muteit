from muteit.objects import *
from muteit.utils import get_dsl
from muteit.parse import parse
import random
from muteit.get_mutation import get_swap_operator_mutations
from muteit.apply_mutation import apply_swap_operator_mutation

def add(x: float, y: float) -> float:
    return x + y

def mul(x: float, y: float) -> float:
    return x * y

def one() -> float:
    return 1

def neg(x: float) -> float:
    return -x

def sub(x : float, y : float) -> float:
    return x-y

dsl: DSL = get_dsl((add, mul, one, neg, sub))

def program(x : float) -> float:
    a = add(x, x)
    b = one()
    c = add(b,b)
    d = add(a,c)
    return d

cg = parse(program, dsl)

for _ in range(10):
    target = random.choice(list(cg.operator_nodes))
    muts = get_swap_operator_mutations(dsl, target)
    if muts:
        m = next(iter(muts))
        apply_swap_operator_mutation(cg, m)

print(cg)
