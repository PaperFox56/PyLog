from interpreter import Interpreter, Parser

'''src = """
` a.
` c(4).
` b(X) :- e(X).
` b(X) :- c(X); d(X).
` d(X) :- c(X), a(X).
` e(45).
` a(5).
? b(X).
"""'''
src = """
` parent(kelly tom).
` child(franck tom).
` child(sally tom).
` parent(X Y) :- child(Y X).
` sibling(X Y) :- parent(Z X), parent(Z Y).
` child(X Y) :- parent(Y X).
? sibling(X Y).
"""

interpreter = Interpreter()
interpreter.interprete(src)


e = ''
while e != '<':
    e = input(">? ")
    if e == '': continue
    if e[0] != '`': e = '?'+e
    if e[-1] != '.': e += '.'
    parser = Parser(e)
    parser.tokenize()
    ast = parser.parse()
    print(ast)
    try:
        interpreter.interprete(e)
    except:
        print("None")

