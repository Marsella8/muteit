from muteit.objects import *
from muteit.dsl_utils import get_dsl
from muteit.parse import parse
from muteit.run_computation_graph import run_computation_graph
from math import sin, pi
import numpy as np
from typing import Union, List, Tuple, Callable
from dataclasses import dataclass
from muteit.engines.random import RandomEngine


@dataclass
class Constant:
    value: float

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Polynomial:
    coefficients: dict[int, float]

    def __str__(self) -> str:
        terms = []
        for power, coeff in sorted(self.coefficients.items(), reverse=True):
            if coeff == 0:
                continue
            if power == 0:
                terms.append(str(coeff))
            elif power == 1:
                terms.append(f"{coeff if coeff != 1 else ''}x")
            else:
                terms.append(f"{coeff if coeff != 1 else ''}x^{power}")
        return " + ".join(terms) if terms else "0"


def add_poly(x: Polynomial, y: Polynomial) -> Polynomial:
    result = {}
    for power, coeff in x.coefficients.items():
        result[power] = result.get(power, 0) + coeff
    for power, coeff in y.coefficients.items():
        result[power] = result.get(power, 0) + coeff
    return Polynomial(result)


def mul_poly(x: Polynomial) -> Polynomial:
    result = {}
    y = Polynomial({1: 1})
    for p1, c1 in x.coefficients.items():
        for p2, c2 in y.coefficients.items():
            power = p1 + p2
            result[power] = result.get(power, 0) + c1 * c2
    return Polynomial(result)


def evaluate(p: Union[Polynomial, Constant], val: float) -> float:
    if isinstance(p, Constant):
        return p.value
    return sum(coeff * (val**power) for power, coeff in p.coefficients.items())


def id(x: Polynomial) -> Polynomial:
    return x


def halve(x: Polynomial) -> Polynomial:
    return Polynomial({k: v / 2 for k, v in x.coefficients.items()})


def x() -> Polynomial:
    return Polynomial({1: 1})


dsl: DSL = get_dsl((add_poly, mul_poly, halve, x))


def program(x: Polynomial) -> Polynomial:
    x1 = halve(x)
    return x1


def calculate_error(
    cg: ComputationGraph, input_values: List[float], target_function: Callable
) -> float:
    try:
        total_error = 0
        for x_val in input_values:
            x_poly = Polynomial({0: 1})
            result = run_computation_graph(cg, (x_poly,))[0]
            computed_output = evaluate(result, x_val)
            target_output = target_function(x_val)
            total_error += abs(computed_output - target_output)
        return total_error
    except Exception:
        return float("inf")


def find_approximation_to_target_function(
    cg: ComputationGraph,
    dsl: DSL,
    input_values: List[float],
    target_function: Callable,
    iterations: int,
) -> Tuple[float, ComputationGraph]:
    """Find best approximation to target function using random search."""
    best_error = float("inf")
    engine = RandomEngine(dsl=dsl, cg=cg, max_nodes=10)

    for i in range(iterations):
        current_error = calculate_error(cg, input_values, target_function)
        if current_error < best_error:
            best_error = current_error

            print(f"Iteration {i}: New best error = {best_error}")
            print(cg.operator_nodes)
            if best_error < 1e-6:
                return best_error

        cg = engine.step()

    return best_error


def main():
    """Main execution function."""
    initial_cg = parse(program, dsl)
    target_function = lambda x: sin(x)
    input_values = list(np.linspace(-pi, pi, 100))
    best_error = find_approximation_to_target_function(
        initial_cg, dsl, input_values, target_function, iterations=100000
    )

    print(f"Final best error: {best_error}")
    print("Best solution found:")


if __name__ == "__main__":
    main()
