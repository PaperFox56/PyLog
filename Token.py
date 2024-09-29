from dataclasses import dataclass
import re

class TokenType:
    NONE = 'NONE'
    ATOM = 'ATOM'
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    VARIABLE = 'VARIABLE'
    OPERATOR = 'OPERATOR'
    OPERATION = 'OPERATION'
    COMPOSITE = 'COMPOSITE'
    SEPARATOR = 'SEPARATOR'
    # Expression types
    QUERRY = 'QUERRY'
    RULE = 'RULE'

@dataclass
class Token:
    type: int
    value: object
    line: int
    col: int

    def copy(self):
        return Token(self.type, self.value, 0, 0)

    def __str__(self):
        return f"{self.type} {self.value} at ({self.line}:{self.col})"

    def compare(self, o):
        return self.type == o.type and (self.value == o.value or o.type == TokenType.VARIABLE)

    def getStr(self):
        return str(self.value)

@dataclass
class Composite:
    type = TokenType.COMPOSITE
    head: Token
    parameters: list

    def copy(self):
        parameters = []
        for p in self.parameters:
            parameters.append(p.copy())
        return Composite(self.head.copy(), parameters)

    def format(self, changes: dict):
        for p in self.parameters:
            if p.type == TokenType.COMPOSITE:
                p.format(changes)
            # This part as to be read many times
            elif (p.type, p.value) in changes: p.type, p.value = changes[(p.type, p.value)]

    def __str__(self):
        out = f"{self.head.value}("
        for p in self.parameters:
            out += f"{p.value} "
        return out[:-1]+')'

    def getStr(self):
        return self.__str__()

    def compare(self, o):
        if self.type == o.type and self.head.value == o.head.value and len(o.parameters) == len(self.parameters):
            output = []
            for i in range(len(self.parameters)):
                a = self.parameters[i]
                b = o.parameters[i]
                if a.compare(b) or (a.type == TokenType.VARIABLE and b.type != TokenType.VARIABLE) or (b.type == TokenType.VARIABLE and a.type != TokenType.VARIABLE):
                    output.append([(a.type, a.getStr()), (b.type, b.getStr())])
                else: return False
            return output
        return False

@dataclass
class Expression:
    type: str
    head: object
    parameter: object

    def copy(self):
        return Expression(self.type, self.head.copy(), self.parameter.copy())

    def format(self, changes: dict):
        for p in [self.head, self.parameter]:
            if p.type in [TokenType.COMPOSITE, TokenType.OPERATION]:
                p.format(changes)
            # This part as to be read many times
            elif (p.type, p.value) in changes: p.type, p.value = changes[(p.type, p.value)]

@dataclass
class Operation:
    type = TokenType.OPERATION
    head: object
    parameters: list

    def copy(self):
        parameters = []
        for p in self.parameters:
            parameters.append(p.copy())
        return Operation(self.head.copy(), parameters)

    def format(self, changes: dict):
        for p in self.parameters:
            if p.type in [TokenType.COMPOSITE, TokenType.OPERATION]:
                p.format(changes)
            # This part as to be read many times
            elif (p.type, p.value) in changes: p.type, p.value = changes[(p.type, p.value)]

regexes = {
"variable": re.compile("^([A-Z]+)([a-z|A-Z|0-9|_]*)$"),
"number": re.compile("^-*([0-9]*).*([0-9]+)$"),
"alphanum": re.compile("^[a-z|A-Z|0-9|_]+$"),
"non alphanum": re.compile("^'.+'$"),
"string": re.compile('^".+"$'),
}
