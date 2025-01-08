from muteit.objects import *
from muteit.utils import get_dsl
from muteit.apply_mutation import apply_swap_operator_mutation

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

def test_apply_swap_operator_mutation():
    input1 = InputNode(int, 0)
    input2 = InputNode(int, 1)
    target_node = OperatorNode(Operator(add), (input1, input2), 2)
    output_node = OutputNode(target_node, 3)
    
    computation_graph = ComputationGraph(
        input_nodes=[input1, input2],
        operator_nodes={target_node},
        output_nodes=[output_node],
    )

    
    mutation = SwapOperatorMutation(target_node, Operator(mul))
    new_graph = apply_swap_operator_mutation(computation_graph, mutation)

    assert target_node == OperatorNode(Operator(mul), (input1, input2), 2)
