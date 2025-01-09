from muteit.objects import *
from muteit.utils import get_dsl
from muteit.parse import parse
import random
from muteit.get_mutation import get_swap_operator_mutations, get_swap_dependency_mutations, get_add_operator_as_dependency_mutations
from muteit.apply_mutation import apply_swap_operator_mutation, apply_swap_dependency_mutation
from muteit.run_computation_graph import run_computation_graph

from math import sin, pi
import numpy as np

def add(x: float, y: float) -> float:
    return x + y

def mul(x: float, y: float) -> float:
    return x * y

def one() -> float:
    return 1

def neg(x: float) -> float:
    return -x

def inv(x : float) -> float:
    return float('inf') if abs(x)< 1e-8 else 1/x

dsl: DSL = get_dsl((add, mul, one, neg, inv))

def program(x: float) -> float:
    x1 = inv(x)
    return x1

def apply_random_mutation(cg: ComputationGraph, dsl: DSL) -> None:
    mutation_type = random.choice(["operator_swap", "dependency_swap", "add_operator"])
    
    if mutation_type == "operator_swap":
        eligible_nodes = list(cg.operator_nodes)
        if eligible_nodes:
            target = random.choice(eligible_nodes)
            muts = get_swap_operator_mutations(dsl, target)
            if muts:
                m = random.choice(list(muts))
                apply_swap_operator_mutation(cg, m)
                
    elif mutation_type == "dependency_swap":
        eligible_nodes = [p for p in cg.operator_nodes if len(p.inputs) > 0]
        if eligible_nodes:
            target_node = random.choice(eligible_nodes)
            target_idx = random.randint(0, len(target_node.inputs)-1)
            muts = list(get_swap_dependency_mutations(cg, target_node, target_idx))
            if muts:
                m = random.choice(muts)
                apply_swap_dependency_mutation(cg, m)
          
    else:  # add_operator
        eligible_nodes = [p for p in cg.operator_nodes if len(p.inputs) > 0]
        if eligible_nodes:
            target_node = random.choice(eligible_nodes)
            target_idx = random.randint(0, len(target_node.inputs)-1)
            muts = list(get_add_operator_as_dependency_mutations(cg, dsl, target_node, target_idx))
            if muts:
                m = random.choice(muts)
                apply_swap_dependency_mutation(cg, m.dep_to_sub)
                cg.operator_nodes.add(m.new_input)
def find_approximation_to_target_function(
    cg: ComputationGraph, dsl: DSL, input_values: list[float], target_function, iterations: int
) -> ComputationGraph:
    best_error = float("inf")

    for i in range(iterations):
        try:
            total_error = 0
            for x in input_values:
                computed_output = run_computation_graph(cg, (x,))[0]
                target_output = target_function(x)
                total_error += abs(computed_output - target_output)

            if total_error < best_error:
                best_error = total_error
                print(f"Iteration {i}: New best error = {best_error}")
                print(cg)
            if total_error == 0:
                return 0

        except Exception as e:
            print(e)
            continue
        apply_random_mutation(cg, dsl)
        
        if len(cg.operator_nodes) > 5:
            cg = parse(program, dsl)

    return best_error


# Example usage:
initial_cg = parse(program, dsl)
target_function = lambda x: sin(x)
input_values = np.arange(-pi, pi, 2*pi / 50)
print(input_values)
best_error = find_approximation_to_target_function(
    initial_cg, dsl, input_values, target_function, iterations=10_000_000
)

print(best_error)
