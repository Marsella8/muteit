from dataclasses import dataclass, field
from muteit.objects import *
from collections import deque
from muteit.get_mutation import *
from muteit.apply_mutation import *
import random
from typing import Deque
from muteit.cg_utils import deep_copy


@dataclass
class RandomEngine:
    dsl: DSL
    cg: ComputationGraph
    max_nodes: int
    history_buffer: Deque[ComputationGraph] = field(
        default_factory=lambda: deque(maxlen=10)
    )

    def __post_init__(self):
        self.history_buffer.append(deep_copy(self.cg))

    def step(self) -> ComputationGraph:
        current_cg = deep_copy(self.cg)

        if len(current_cg.nodes) < self.max_nodes:
            mutation_type = random.choice(
                ("swap_operator", "swap_dependency", "add_operator", "rollback")
            )
        else:
            mutation_type = random.choice(
                ("swap_operator", "swap_dependency", "rollback")
            )

        match mutation_type:
            case "swap_operator":
                mutations = get_all_swap_operator_mutations(current_cg, self.dsl)
                if mutations:
                    mutation = random.choice(list(mutations))
                    apply_swap_operator_mutation(current_cg, mutation)

            case "swap_dependency":
                mutations = get_all_swap_dependency_mutations(current_cg)
                if mutations:
                    mutation = random.choice(list(mutations))
                    apply_swap_dependency_mutation(current_cg, mutation)

            case "add_operator":
                mutations = get_all_add_operator_as_dependency_mutations(
                    current_cg, self.dsl
                )
                if mutations:
                    mutation = random.choice(list(mutations))
                    apply_add_operator_as_dependency_mutation(current_cg, mutation)

            case "rollback":
                if len(self.history_buffer) > 1:
                    current_cg = deep_copy(self.history_buffer[-2])

        self.cg = current_cg
        self.history_buffer.append(deep_copy(current_cg))

        return current_cg
