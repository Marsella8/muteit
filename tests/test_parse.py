from muteit.parse import parse
from muteit.objects import *
from muteit.utils import get_dsl

def add(x : int, y : int) -> int:
    return x + y

def mul(x : int, y : int) -> int:
    return x * y

def one() -> int:
    return 1

dsl = get_dsl((add, mul, one))


# Programs outside the test functions

def program_simple(x: int) -> int:
    x1 = one()  # 1
    x2 = add(x1, x1)  # 2
    x3 = mul(x, x)  # x^2
    return x3

def program_multiple_outputs(x: int) -> tuple[int, int]:
    x1 = one()
    x2 = add(x1, x1)  # 2
    x3 = mul(x, x)    # x^2
    return x2, x3

def program_reused_variables(x: int) -> int:
    x1 = one()
    x1 = add(x1, x1)  # Reusing x1
    x1 = mul(x1, x1)  # Reusing x1 again
    return x1

def program_multiple_inputs(x: int, y: int) -> int:
    z = add(x, y)
    w = mul(z, z)
    return w

def program_complex_dependencies(x: int) -> int:
    a = one()         # 1
    b = add(a, a)     # 2
    c = mul(x, x)     # x^2
    d = mul(b, c)     # 2x^2
    e = add(d, x)     # 2x^2 + x
    return e


# Test functions

def test_simple_program():
    graph = parse(program_simple, dsl)
    
    assert len(graph.input_nodes) == 1
    assert graph.input_nodes[0].input_type == int
    
    assert len(graph.operator_nodes) == 3
    operators = {node.func.name for node in graph.operator_nodes}
    assert operators == {'one', 'add', 'mul'}
    
    assert len(graph.output_nodes) == 1

def test_multiple_outputs():
    graph = parse(program_multiple_outputs, dsl)
    
    assert len(graph.input_nodes) == 1
    assert len(graph.operator_nodes) == 3
    assert len(graph.output_nodes) == 2

def test_reused_variables():
    graph = parse(program_reused_variables, dsl)
    
    assert len(graph.input_nodes) == 1
    assert len(graph.operator_nodes) == 3
    assert len(graph.output_nodes) == 1

def test_multiple_inputs():
    graph = parse(program_multiple_inputs, dsl)
    
    assert len(graph.input_nodes) == 2
    assert len(graph.operator_nodes) == 2
    assert len(graph.output_nodes) == 1

def test_complex_dependencies():
    graph = parse(program_complex_dependencies, dsl)
    
    assert len(graph.input_nodes) == 1
    assert len(graph.operator_nodes) == 5
    assert len(graph.output_nodes) == 1
    
    mul_nodes = [n for n in graph.operator_nodes if n.func.name == 'mul']
    add_nodes = [n for n in graph.operator_nodes if n.func.name == 'add']
    one_nodes = [n for n in graph.operator_nodes if n.func.name == 'one']
    
    assert len(mul_nodes) == 2
    assert len(add_nodes) == 2
    assert len(one_nodes) == 1
