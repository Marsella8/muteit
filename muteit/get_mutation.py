from .objects import *
from .cg_utils import get_descendants
from itertools import product

def is_subtype(sub_sig: Signature, super_sig: Signature) -> bool:

    if len(sub_sig.input_type) != len(super_sig.input_type):
        return False
    # Contravariance
    input_compatible = all(is_subtype_base(super_arg, sub_arg) 
                         for sub_arg, super_arg in zip(sub_sig.input_type, super_sig.input_type, strict=True))
    
    # Covariance
    output_compatible = is_subtype_base(sub_sig.output_type, super_sig.output_type)
    
    return input_compatible and output_compatible

def is_subtype_base(sub_type: type, super_type: type) -> bool:
    if sub_type == super_type:
        return True
        
    if hasattr(sub_type, '__origin__') and hasattr(super_type, '__origin__'):
        if sub_type.__origin__ != super_type.__origin__:
            return False
        return all(is_subtype_base(s, t) for s, t in zip(sub_type.__args__, super_type.__args__))
    
    try:
        return issubclass(sub_type, super_type)
    except TypeError:
        return False

def get_operators_with_compatible_signature(target: Operator, dsl: DSL) -> set[Operator]:
    return {op for op in dsl.terms.values() if is_subtype(op.signature, target.signature) and op != target}

def get_swap_operator_mutations(dsl: DSL, target: OperatorNode) -> set[SwapOperatorMutation]:
    compatible_ops = get_operators_with_compatible_signature(target.func, dsl)
    mutations = {SwapOperatorMutation(target, op) for op in compatible_ops}
    return mutations

def get_dependencies_with_compatible_signature_and_dependency(
    computation_graph: ComputationGraph,
    target: OperatorNode,
    target_input_idx: int
) -> set[Node]:
    required_type = target.func.signature.input_type[target_input_idx]
    
    descendants = get_descendants(computation_graph, target)
    
    compatible_nodes = set()
    
    for node in computation_graph.nodes:
        if node in descendants or node == target:
            continue
        if isinstance(node, InputNode):
            output_type = node.input_type
        elif isinstance(node, OperatorNode):
            output_type = node.func.signature.output_type
        elif isinstance(node, OutputNode):
            continue

        if is_subtype_base(output_type, required_type):
            compatible_nodes.add(node)
    
    return compatible_nodes

def get_swap_dependency_mutations(computation_graph : ComputationGraph, target: OperatorNode, target_input_idx: int) -> set[Node]:
    compatible_ops = get_dependencies_with_compatible_signature_and_dependency(computation_graph, target, target_input_idx)
    mutations = {SwapDependencyMutation(target, target_input_idx, op) for op in compatible_ops}
    return mutations

def get_operators_with_compatible_output_type(dsl: DSL, required_type: type) -> set[Operator]:
    return {
        op for op in dsl.terms.values() 
        if is_subtype_base(op.signature.output_type, required_type)
    }

def get_potential_inputs_for_operator(
    computation_graph: ComputationGraph,
    operator: Operator,
    target: OperatorNode
) -> list[list[Node]]:
    descendants = get_descendants(computation_graph, target)
    valid_inputs: list[list[Node]] = []
    
    for input_type in operator.signature.input_type:
        valid_nodes_for_position = set()
        
        for node in computation_graph.nodes:
            if node in descendants or node == target or isinstance(node, OutputNode):
                continue
                
            if isinstance(node, InputNode):
                node_output_type = node.input_type
            elif isinstance(node, OperatorNode):
                node_output_type = node.func.signature.output_type
            
            if is_subtype_base(node_output_type, input_type):
                valid_nodes_for_position.add(node)
        
        valid_inputs.append(list(valid_nodes_for_position))
    
    return valid_inputs

def get_add_operator_as_dependency_mutations(
    computation_graph: ComputationGraph,
    dsl: DSL,
    target: OperatorNode,
    target_input_idx: int
) -> set[AddOperatorAsDependencyMutation]:
    required_type = target.func.signature.input_type[target_input_idx]
    mutations = set()
    
    compatible_operators = get_operators_with_compatible_output_type(dsl, required_type)
    
    for operator in compatible_operators:
        potential_inputs = get_potential_inputs_for_operator(computation_graph, operator, target)
        
        if all(potential_inputs) and len(potential_inputs) == len(operator.signature.input_type):
            
            for input_combination in product(*potential_inputs):
                new_operator_node = OperatorNode(
                    func=operator,
                    inputs=list(input_combination)
                )
                
                swap_mutation = SwapDependencyMutation(
                    target_node=target,
                    target_input_idx=target_input_idx,
                    new_input=new_operator_node
                )
                
                mutation = AddOperatorAsDependencyMutation(
                    dep_to_sub=swap_mutation,
                    new_input=new_operator_node
                )
                
                mutations.add(mutation)
    
    return mutations
