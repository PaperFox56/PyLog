from Token import *
from Tree import Tree
from parser import Parser
from parser import classify


class Interpreter:
    def __init__(self):
        self.env = []
        self.tree = None
        self.line = 0
        self.depth = 0

    def EVAL(self, querry):
        # We first have to find a rule which head have the same name and arity than the current querry
        line = 0
        for rule in self.env:
            line += 1
            r = self.tree.insert(line, False)
            if r:
                self.tree.back()
                continue
            elif r == False:
                if len(self.tree.current.children) == 0:
                    self.tree.current.value[-1] = True
                    self.tree.back()
                    continue
            output = querry.compare(rule.head)
            if output:
                #print(line, querry, rule.head)
                if querry.type == TokenType.ATOM:
                    result = False
                    if not rule.parameter: # No parameters, so we found the answer
                        result = True
                    else: # We have to check if the parameter is an operator
                        if rule.parameter.type == TokenType.OPERATION:
                            result = bool(self.solve(rule.parameter, line))
                        else: result = bool(self.EVAL(rule.parameter))
                    if not result: self.tree.current.value[-1] = True; self.tree.back()
                    return result
                elif querry.type == TokenType.COMPOSITE:
                    # In this case, we match only if for each parameter in the querry there is either an parameter with the same value, or a variable
                    #print(output)
                    out = {}
                    goal = 'check'
                    done = True
                    #print(rule)
                    if not rule.parameter:
                        for k, v in output:
                            if k[0] == v[0] == TokenType.VARIABLE: # We have a problem here
                                done = False
                            elif k[0] == TokenType.VARIABLE:
                                out[k] = v
                                goal = 'find'
                    else: # It's time to unify all of this
                        temp = {}
                        for k, v in output:
                            if v[0] == TokenType.VARIABLE and k[0] != TokenType.VARIABLE:
                                temp[v] = k
                        new = rule.copy()
                        new.format(temp)
                        result = None
                        if rule.parameter.type == TokenType.OPERATION:
                            result = self.solve(new.parameter, line)
                        else:
                            result = self.EVAL(new.parameter)
                        if result:
                            if type(result) == dict:
                                new.head.format(result)
                            output = querry.compare(new.head)
                            #print(output)
                            for k, v in output:
                                if k[0] == v[0] == TokenType.VARIABLE: # We have a problem here
                                    done = False
                                elif k[0] == TokenType.VARIABLE:
                                    out[k] = v
                                    goal = 'find'
                        else: done = False
                    if done:
                        self.tree.back()
                        if goal == 'find': return out
                        else: return True
            self.tree.current.value[-1] = True
            self.tree.back()

    def solve(self, operation: Operation, line):
        def _solve(p, line):
            if p.type == TokenType.OPERATION:
                return self.solve(p, line)
            else:
                return self.EVAL(p)
        prev = None
        output = {}
        result = _solve(operation.parameters[0], line)
        if operation.head.value == ',':
            i = 0
            while result and i < 10:
                i += 1
                if type(result) == dict:
                    output.update(result)
                    new = operation.parameters[1].copy()
                    new.format(result)
                    result = _solve(new, line)
                    if result:
                        if type(result) == dict: output.update(result)
                        if not check(output): result = _solve(operation.parameters[0], line)
                    else: result = _solve(operation.parameters[0], line);
        elif operation.head.value == ';':
            if result:
                return result
            else:
                result = solve(operation.parameters[1])
                if result:
                    return result
        if output == {}: return True
        return output


    def interprete(self, src):
        parser = Parser(src)
        parser.tokenize()
        ast = parser.parse()
        if type(ast) == Exception: print(ast)
        else:
            for expression in ast:
                if expression.type == TokenType.RULE:
                    self.env.append(expression)
                else:
                    self.tree = Tree()
                    result = True
                    results = []
                    i = 0
                    while result and i < 10:
                        self.tree.current = self.tree.root
                        result = self.EVAL(expression.head)
                        if not result in results:
                            results.append(result)
                            self.PRINT(result)
                        #print(self.tree)
                        i += 1
                        #break

    def PRINT(self, data):
        if type(data) == dict:
            out = ''
            for k in data:
                out += f'{k[1]} := {data[k][1]}  '
            print('    ', out[:-2])
        else: print('    ', data)

def check(val: dict):
    a = val.values()
    # We have to check if two different variables don't have the same value
    return len(a) == len(set(a))
