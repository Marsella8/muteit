from muteit.objects import *
from muteit.dsl_utils import get_dsl
from muteit.cg_utils import deep_copy

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


def test_deep_copy():
    input1 = InputNode(input_type=int)
    input2 = InputNode(input_type=int)

    add_node = OperatorNode(func=Operator(add), inputs=[input1, input2])
    mul_node = OperatorNode(func=Operator(mul), inputs=[add_node])

    output_node = OutputNode(input=mul_node)

    original_graph = ComputationGraph(
        input_nodes=(input1, input2),
        operator_nodes={add_node, mul_node},
        output_nodes=(output_node,),
    )

    copied_graph = deep_copy(original_graph)

    assert copied_graph != original_graph
    assert len(copied_graph.nodes) == len(original_graph.nodes)

    new_add_node = OperatorNode(func=Operator(add), inputs=[input1, input2])
    copied_graph.operator_nodes.add(new_add_node)

    assert new_add_node not in original_graph.operator_nodes
    assert new_add_node in copied_graph.operator_nodes

    print("Test passed!")
