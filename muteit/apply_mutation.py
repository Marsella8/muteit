from .objects import *

def apply_swap_operator_mutation(cg: ComputationGraph, mut: SwapOperatorMutation) -> None:
    mut.to_swap.func = mut.new_op
