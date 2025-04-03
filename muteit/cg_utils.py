from multimethod import multimethod
from .objects import *


@multimethod
def get_predecessors(node: InputNode) -> frozenset[Node]:
    return frozenset()


@multimethod
def get_predecessors(node: OperatorNode) -> frozenset[Node]:
    return frozenset(node.inputs)


@multimethod
def get_predecessors(node: OutputNode) -> frozenset[Node]:
    return frozenset({node.input})


def get_ancestors(node: Node) -> frozenset[Node]:
    all_ancestors = set(get_predecessors(node))

    for predecessor in list(all_ancestors):
        all_ancestors |= get_ancestors(predecessor)

    return frozenset(all_ancestors)


def get_descendants(cg: ComputationGraph, node: Node) -> frozenset[Node]:
    descendants = set()

    for candidate_node in cg.nodes:
        if node in get_predecessors(candidate_node):
            descendants |= {candidate_node}
            descendants |= get_descendants(cg, candidate_node)

    return frozenset(descendants)


def topo_sorted(cg: ComputationGraph) -> list[Node]:
    in_degree = {node: 0 for node in cg.nodes}
    graph = {node: set() for node in cg.nodes}

    for node in cg.nodes:
        for predecessor in get_predecessors(node):
            in_degree[node] += 1
            graph[predecessor].add(node)

    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        current = queue.pop(0)
        result.append(current)

        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(result) != len(cg.nodes):
        raise ValueError("Cycle")

    return result


def deep_copy(cg: ComputationGraph) -> ComputationGraph:
    node_map: dict[Node, Node] = {}

    sorted_nodes = topo_sorted(cg)

    for node in sorted_nodes:
        if isinstance(node, InputNode):
            node_map[node] = InputNode(input_type=node.input_type)

        elif isinstance(node, OperatorNode):
            copied_inputs = [node_map[input_node] for input_node in node.inputs]
            node_map[node] = OperatorNode(func=node.func, inputs=copied_inputs)

        elif isinstance(node, OutputNode):
            node_map[node] = OutputNode(input=node_map[node.input])

    new_input_nodes = tuple(node_map[node] for node in cg.input_nodes)
    new_operator_nodes = {node_map[node] for node in cg.operator_nodes}
    new_output_nodes = tuple(node_map[node] for node in cg.output_nodes)

    return ComputationGraph(
        input_nodes=new_input_nodes,
        operator_nodes=new_operator_nodes,
        output_nodes=new_output_nodes,
    )
