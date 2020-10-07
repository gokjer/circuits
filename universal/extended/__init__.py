from universal.basic import Equality
from universal.extended.gate import Gate
from universal.extended.circuit import Circuit


def make_equalities(lhs, rhs):
    result = []
    for left, right in zip(lhs, rhs):
        result.append(Equality(variables=[left, right]))
    return result
