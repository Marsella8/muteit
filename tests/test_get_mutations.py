from muteit.objects import *
from muteit.dsl_utils import get_dsl
from muteit.get_mutation import get_swap_operator_mutations


def add(x: int, y: int) -> int:
    return x + y


def mul(x: int, y: int) -> int:
    return x * y


def one() -> int:
    return 1


def sub(x: int, y: int) -> int:
    return x - y


def neg(x: int) -> int:
    return -x


def abs(x: int) -> int:
    return abs(x)


dsl: DSL = get_dsl((add, mul, one, sub, neg, abs))


def test_get_operator_mutations():
    input1 = InputNode(int)
    input2 = InputNode(int)
    target_node = OperatorNode(Operator(add), [input1, input2])

    mutations = get_swap_operator_mutations(dsl, target_node)

    expected_mutation = {
        SwapOperatorMutation(target_node, Operator(mul)),
        SwapOperatorMutation(target_node, Operator(sub)),
    }

    assert mutations == expected_mutation
