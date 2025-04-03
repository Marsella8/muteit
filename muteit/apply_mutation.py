from .objects import *


def apply_swap_operator_mutation(
    cg: ComputationGraph, mut: SwapOperatorMutation
) -> None:
    mut.to_swap.func = mut.new_op


def apply_swap_dependency_mutation(
    cg: ComputationGraph, mut: SwapDependencyMutation
) -> None:
    mut.target_node.inputs[mut.target_input_idx] = mut.new_input


def apply_add_operator_as_dependency_mutation(
    cg: ComputationGraph, mut: AddOperatorAsDependencyMutation
) -> None:
    cg.operator_nodes.add(mut.new_input)
    apply_swap_dependency_mutation(cg, mut.dep_to_sub)
