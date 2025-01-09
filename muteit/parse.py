from typing import Callable
from .objects import *

import inspect
import ast


import ast


def _get_statements(f : Callable):
    source = inspect.getsource(f)
    tree = ast.parse(source)
    body = tree.body[0].body
    return list(body)

def program_is_well_shaped(f: Callable, dsl : DSL) -> bool:
    statements = _get_statements(f)
    
    assigned_vars = set()
    for stmt in statements:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if target.id in assigned_vars:
                        return False
                    assigned_vars.add(target.id)

    for stmt in statements[:-1]:
        if isinstance(stmt, ast.Assign):
            if not isinstance(stmt.value, ast.Call):
                return False 
            func_name = stmt.value.func.id
            if func_name not in [term.name for term in dsl.terms]:
                return False

    last_stmt = statements[-1]
    if isinstance(last_stmt, ast.Return):
        if isinstance(last_stmt.value, ast.Name):
            return True
        elif isinstance(last_stmt.value, ast.Tuple):
            for element in last_stmt.value.elts:
                if not isinstance(element, ast.Name):
                    return False
            return True
    return False

def _get_input_nodes(f : Callable, var_name_to_node_mapping : dict[str, Node]) -> tuple[InputNode]:
    input_nodes = tuple(InputNode(tp) for tp in get_signature(f).input_type)
    argument_names = [param.name for param in inspect.signature(f).parameters.values()]
    var_name_to_node_mapping |= dict(zip(argument_names, input_nodes))
    return input_nodes

def _get_operator_nodes(f : Callable, dsl : DSL, var_name_to_node_mapping : dict[str, Node]) -> frozenset[OperatorNode]:
    statements = _get_statements(f)[:-1]
    nodes = set()
    for asst in statements:
        var_name = asst.targets[0].id
        func = dsl.terms[asst.value.func.id]
        deps = [var_name_to_node_mapping[a.id] for a in asst.value.args]
        node = OperatorNode(func, deps)
        nodes.add(node)
        var_name_to_node_mapping[var_name] = node
    return nodes

def _get_output_nodes(f: Callable, var_name_to_node_mapping: dict[str, Node]) -> tuple[OutputNode]:

    stmt = _get_statements(f)[-1]

    if isinstance(stmt.value, ast.Name):
        dep_node = var_name_to_node_mapping[stmt.value.id]
        return (OutputNode(dep_node),)
    elif isinstance(stmt.value, ast.Tuple):
        output_nodes = []
        for element in stmt.value.elts:
            if not isinstance(element, ast.Name):
                raise ValueError
            dep_node = var_name_to_node_mapping[element.id]
            output_nodes.append(OutputNode(dep_node))
        return tuple(output_nodes)

def parse(f: Callable, dsl: DSL) -> ComputationGraph:
    var_name_to_node_mapping = {}
    input_nodes = _get_input_nodes(f, var_name_to_node_mapping)        
    operator_nodes = _get_operator_nodes(f, dsl, var_name_to_node_mapping)
    output_nodes = _get_output_nodes(f, var_name_to_node_mapping)
    
    return ComputationGraph(
        input_nodes=input_nodes,
        operator_nodes=operator_nodes,
        output_nodes=output_nodes
    )
