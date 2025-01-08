from .objects import *

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
