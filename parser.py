from Token import *


class Parser:
    def __init__(self, src):
        self.src = src
        self.i = 0
        self.tokens = []
        # Debugging tools
        self.line = 1
        self.col = 1

    def tokenize(self):
        """ Create a list of tokens from the source code """
        while self.i < len(self.src):
            next = self.getNextToken()
            if next.value != "":
                self.tokens.append(classify(next))

    def getNextToken(self) -> Token:
        """ Get the next tokens from the source code """
        token = Token(TokenType.NONE, "", self.line, self.col)
        self.col += 1
        c = self.src[self.i]
        #print(self.col, c)
        if c in (' ', '\n', '\t'):
            self.i += 1
            if c == '\n': self.line += 1; self.col = 1
        elif c == '-':
            token.value = '-'
            self.i += 1
            if self.i < len(self.src) and (isDigit(self.src[self.i]) or c == '.'):
                c = self.src[self.i]
                while isDigit(c) or c in ('.', '-', '+', 'e'):
                    token.value += c
                    self.i += 1
                    self.col += 1
                    if self.i >= len(self.src): break
                    c = self.src[self.i]
                self.col -= 1
        elif isAlphanumerical(c): # alphanumerical characters and underscore
            while isAlphanumerical(c):
                token.value += c
                self.i += 1
                #print(c, self.col)
                self.col += 1
                if self.i >= len(self.src): break
                c = self.src[self.i]
            self.col -= 1
        elif c == '\'': # non alphanumerical characters
            token.value = self.getSurroundedBy('\'')
        elif c == '\"': # string
            token.value = self.getSurroundedBy('"')
        elif c == ':': # This symbol ":-"
            self.i += 1
            token.value = c
            if self.i < len(self.src) and self.src[self.i] == '-':
                self.i += 1
                self.col += 1
                token.value = ":-"
        else: self.i += 1; token.value = c; #print(c, self.col)
        return token

    def getSurroundedBy(self, ch):
        text = ""
        self.i += 1
        c = self.src[self.i]
        while c != ch:
            text += c
            self.i += 1
            #print(c, self.col)
            self.col += 1
            if self.i >= len(self.src): return '@'
            c = self.src[self.i]
        self.col += 1
        self.i += 1
        return ch+text+ch

    def parse(self):
        """ Transform the tokens' list in a list of prolog's rules """
        stack = []
        ast = []
        for i in range(len(self.tokens)):
            token = self.tokens[i]
            if token.value == '.': # End of instruction
                if stack.pop(0).value == "`":
                    expressionType = TokenType.RULE
                else:
                    expressionType = TokenType.QUERRY
                if len(stack) == 1:
                    if stack[0].type in [TokenType.COMPOSITE, TokenType.ATOM]:
                         ast.append(Expression(expressionType, stack[0], None))
                    else: return Exception(f"SyntaxError in token {stack[0]} > bad type")
                else:
                    temp = []
                    while len(stack) > 1:
                        temp.insert(0, stack.pop())
                        if temp[0].type == TokenType.OPERATOR:
                            if len(temp) > 2: return Exception(f"SyntaxError in line {token.line} > invalid expression")
                            if temp[0].value == ':-':
                                stack.append(Expression(expressionType, stack.pop(), temp[1])) # Get the head
                            else:
                                stack.append(Operation(temp[0], [stack.pop(), temp[1]])) # Get the head
                            temp = []
                    ast.append(stack.pop())
                    if len(temp) != 0: return Exception(f"SyntaxError in line {token.line} > invalid expression")
                stack.clear()
                continue
            stack.append(token)
            if token.value == ')':
                # Try to fing the last opening bracket
                found = False
                temp = []
                while len(stack) > 0:
                    temp.insert(0, stack.pop())
                    if temp[0].type == TokenType.SEPARATOR and temp[0].value == '(':
                        found = True
                        break
                if found:
                    stack.append(Composite(stack.pop(), [])) # Get the head
                    for j in range(1, len(temp)-1): # Then the arguments
                        tok = temp[j]
                        if tok.type in [TokenType.NUMBER, TokenType.STRING, TokenType.COMPOSITE, TokenType.ATOM, TokenType.VARIABLE]:
                            stack[-1].parameters.append(tok)
                        else: return Exception(f"SyntaxError in token {tok} > bad parameter type")
                else: return Exception(f"SyntaxError in token {token} > closed bracket never opened")
        if len(stack) != 0: return Exception(f"SyntaxError in line {token.line} > invalid expression")
        return ast


def classify(token: Token):
    if regexes["number"].match(token.value): token.type = TokenType.NUMBER; token.value = float(token.value)
    elif regexes["string"].match(token.value): token.type = TokenType.STRING
    elif regexes["variable"].match(token.value): token.type = TokenType.VARIABLE
    elif regexes["alphanum"].match(token.value) or regexes["non alphanum"].match(token.value):
        token.type = TokenType.ATOM
    elif token.value in '().': token.type = TokenType.SEPARATOR
    elif token.value in [',', ';', ':-']: #, '+', '-', '*', '/', '%']:
        token.type = TokenType.OPERATOR
    return token

def isAlphanumerical(c):
    return 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122 or c == '_' or 48 <= ord(c) <= 57
def isDigit(c):
    return 48 <= ord(c) <= 57

if __name__ == "__main__":
    src = """
` mother(a b).
` child(X Y) :- mother(Y X).
` child(X Y) :- mother(Y Z), sibling(Z X).
? mother(a b).
"""
    parser = Parser(src)
    parser.tokenize()
    ast = parser.parse()
    #for t in parser.tokens:
    #    print(t, end="  ")
    #print('\n')
    if type(ast) == Exception:
        print(ast)
    else:
        for t in ast:
            print(t)
