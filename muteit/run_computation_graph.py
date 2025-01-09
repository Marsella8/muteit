from .objects import *
from .cg_utils import topo_sorted

def run_computation_graph(graph: ComputationGraph, inputs: tuple) -> tuple:

    results = dict(zip(graph.input_nodes, inputs, strict=True))

    for node in topo_sorted(graph): #TODO: brittle, change to have a topo sort generator
        if isinstance(node, OperatorNode):
            func = node.func.func
            dependencies = [results[dep_id] for dep_id in node.inputs]
            results[node] = func(*dependencies)
        if isinstance(node, OutputNode):
            results[node] = results[node.input]
    return tuple(results[node] for node in graph.output_nodes)

