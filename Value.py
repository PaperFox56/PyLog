from dataclasses import dataclass

@dataclass
class Value:
    type = 0
    value = None

@dataclass
class Composite:
    type = ValueType.COMPOSITE
    arity = 0
    head: Value
    parameters = []


class ValueType:
    ATOME = 0
    NUMBER = 1
    VARIABLE = 2
    COMPOSITE = 3
