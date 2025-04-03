from typing import Callable, Union
from dataclasses import dataclass, field
import inspect
import itertools


class NodeIDGenerator:
    _id_counter = itertools.count(start=1)

    @staticmethod
    def next_id() -> int:
        return next(NodeIDGenerator._id_counter)


@dataclass(frozen=True)
class Signature:
    input_type: type
    output_type: type


def get_signature(func: Callable) -> Signature:
    hints = inspect.signature(func).parameters
    input_type = tuple(param.annotation for param in hints.values())
    output_type = inspect.signature(func).return_annotation
    return Signature(input_type=input_type, output_type=output_type)


@dataclass
class Operator:
    func: Callable

    def __post_init__(self):
        self.signature: Signature = get_signature(self.func)
        self.name: str = self.func.__name__

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.func)


NodeID = int


@dataclass
class InputNode:
    input_type: type
    id: NodeID = field(default_factory=NodeIDGenerator.next_id)

    def __hash__(self):
        return self.id


@dataclass
class OperatorNode:
    func: Operator
    inputs: list[Union[InputNode, "OperatorNode"]]
    id: NodeID = field(default_factory=NodeIDGenerator.next_id)

    def __hash__(self):
        return self.id

    def __repr__(self):
        return f"OperatorNode({self.func}, {tuple(dep.id for dep in self.inputs)}, {self.id})"


@dataclass
class OutputNode:
    input: InputNode | OperatorNode
    id: NodeID = field(default_factory=NodeIDGenerator.next_id)

    # output_type : type = field(init=False)
    def __post__init__(self):
        pass

    def __hash__(self):
        return self.id


Node = InputNode | OperatorNode | OutputNode


@dataclass
class ComputationGraph:
    input_nodes: tuple[InputNode]
    operator_nodes: set[OperatorNode]
    output_nodes: tuple[OutputNode]

    @property
    def nodes(self) -> set[Node]:
        return set(self.input_nodes) | self.operator_nodes | set(self.output_nodes)


@dataclass
class DSL:
    terms: dict[str, Operator]


@dataclass(frozen=True)
class SwapOperatorMutation:
    to_swap: OperatorNode
    new_op: Operator


@dataclass(frozen=True)
class SwapDependencyMutation:
    target_node: OperatorNode
    target_input_idx: int
    new_input: InputNode | OperatorNode


@dataclass(frozen=True)
class AddOperatorAsDependencyMutation:
    dep_to_sub: SwapDependencyMutation
    new_input: OperatorNode


Mutation = (
    SwapOperatorMutation | SwapDependencyMutation | AddOperatorAsDependencyMutation
)

# TODO: add a addoperaotr thing: reason: suppose you have f(str, str) -> int and f(int) -> str. If you start with id(int) -> int, the currenty mutations can never use f(str, str) of f(int), since there are no str, but their composition makes sense.
# TODO: also add a remove node
