from dataclasses import dataclass
import re

# Class containing possible token types for lexical processing
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
    QUERRY = 'QUERRY'      
    RULE = 'RULE'             

# Representation of a token with its type, value, and position in the code
@dataclass
class Token:
    type: int
    value: object # Value of the token (can be any type)
    line: int     # Line number where the token was found
    col: int      # Column number where the token was found

    # Method to copy a token
    def copy(self):
        return Token(self.type, self.value, 0, 0)

    # String representation of the token
    def __str__(self):
        return f"{self.type} {self.value} at ({self.line}:{self.col})"

    # Comparison with another token
    def compare(self, o):
        return self.type == o.type and (self.value == o.value or o.type == TokenType.VARIABLE)

    # Returns the token value as a string
    def getStr(self):
        return str(self.value)

# Representation of a composite expression that can contain other tokens
@dataclass
class Composite:
    type = TokenType.COMPOSITE
    head: Token                  
    parameters: list              # List of tokens

    # Copy of the composite expression
    def copy(self):
        parameters = [p.copy() for p in self.parameters]
        return Composite(self.head.copy(), parameters)

    # Formats the parameters according to the provided changes
    def format(self, changes: dict):
        for p in self.parameters:
            if p.type == TokenType.COMPOSITE:
                p.format(changes)
            elif (p.type, p.value) in changes:
                p.type, p.value = changes[(p.type, p.value)]

    # String representation of the composite
    def __str__(self):
        out = f"{self.head.value}("
        for p in self.parameters:
            out += f"{p.value} "
        return out[:-1] + ')'

    # Returns a string representation
    def getStr(self):
        return self.__str__()

    # Comparison with another composite
    def compare(self, o):
        if self.type == o.type and self.head.value == o.head.value and len(o.parameters) == len(self.parameters):
            output = []
            for i in range(len(self.parameters)):
                a = self.parameters[i]
                b = o.parameters[i]
                if a.compare(b) or (a.type == TokenType.VARIABLE and b.type != TokenType.VARIABLE) or (b.type == TokenType.VARIABLE and a.type != TokenType.VARIABLE):
                    output.append([(a.type, a.getStr()), (b.type, b.getStr())])
                else:
                    return False
            return output
        return False

# Representation of a general expression with a type, a head, and a parameter 
@dataclass
class Expression:
    type: str           
    head: object            
    parameter: object       

    # Copy of the expression
    def copy(self):
        return Expression(self.type, self.head.copy(), self.parameter.copy())

    # Formats the expression according to the provided changes
    def format(self, changes: dict):
        for p in [self.head, self.parameter]:
            if p.type in [TokenType.COMPOSITE, TokenType.OPERATION]:
                p.format(changes)
            elif (p.type, p.value) in changes:
                p.type, p.value = changes[(p.type, p.value)]

# Representation of an operation with a head and a list of parameters
@dataclass
class Operation:
    type = TokenType.OPERATION  
    head: object
    parameters: list 

    # Copy of the operation
    def copy(self):
        parameters = [p.copy() for p in self.parameters]
        return Operation(self.head.copy(), parameters)

    # Formats the operation according to the provided changes
    def format(self, changes: dict):
        for p in self.parameters:
            if p.type in [TokenType.COMPOSITE, TokenType.OPERATION]:
                p.format(changes)
            elif (p.type, p.value) in changes:
                p.type, p.value = changes[(p.type, p.value)]

# Definition of regular expressions for lexical processing
regexes = {
    "variable": re.compile("^([A-Z]+)([a-z|A-Z|0-9|_]*)$"), # a variable (starts with uppercase)
    "number": re.compile("^-*([0-9]*).*([0-9]+)$"),        # a number (can be negative)
    "alphanum": re.compile("^[a-z|A-Z|0-9|_]+$"),          # an alphanumeric string
    "non alphanum": re.compile("^'.+'$"),                   # a non-alphanumeric string
    "string": re.compile('^".+"$'),                         # a string enclosed in quotes
}
