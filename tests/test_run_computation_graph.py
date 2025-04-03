# test_computation_graph.py

from muteit.run_computation_graph import run_computation_graph
from muteit.parse import parse
from muteit.objects import *
from muteit.dsl_utils import get_dsl


def add(x: int, y: int) -> int:
    return x + y


def mul(x: int, y: int) -> int:
    return x * y


def one() -> int:
    return 1


dsl: DSL = get_dsl((add, mul, one))


def program_simple(x: int) -> int:
    x1 = one()  # 1
    x3 = mul(x, x)  # x^2
    return x3


def test_run_simple_program():
    graph = parse(program_simple, dsl)
    result = run_computation_graph(graph, (3,))

    assert result == (9,)


def program_multiple_outputs(x: int) -> tuple[int, int]:
    x1 = one()
    x2 = add(x1, x1)  # 2
    x3 = mul(x, x)  # x^2
    return x2, x3


def test_run_multiple_outputs():
    graph = parse(program_multiple_outputs, dsl)
    result = run_computation_graph(graph, (3,))

    assert result == (2, 9)


def program_reused_variables(x: int) -> int:
    x1 = add(x, x)  # Reusing x1
    x2 = mul(x1, x1)  # Reusing x1 again
    return x2


def test_run_reused_variables():
    graph = parse(program_reused_variables, dsl)
    result = run_computation_graph(graph, (3,))

    assert result == (36,)


def program_multiple_inputs(x: int, y: int) -> int:
    z = add(x, y)
    w = mul(z, z)
    return w


def test_run_multiple_inputs():
    graph = parse(program_multiple_inputs, dsl)
    result = run_computation_graph(graph, (3, 4))

    assert result == (49,)


def program_complex_dependencies(x: int) -> int:
    a = one()  # 1
    b = add(a, a)  # 2
    c = mul(x, x)  # x^2
    d = mul(b, c)  # 2x^2
    e = add(d, x)  # 2x^2 + x
    return e


def test_run_complex_dependencies():
    graph = parse(program_complex_dependencies, dsl)
    result = run_computation_graph(graph, (3,))

    assert result == (21,)
