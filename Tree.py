
class Tree:
    def __init__(self):
        self.root = Node(None, None)
        self.current = self.root

    def push(self, *value):
        if type(value[0]) == tuple: value = value[0]
        new = Node(self.current, list(value))
        if self.current: self.current.children.append(new)
        else: self.root = new
        self.current = new

    def remove(self):
        if not self.current: return None
        out = self.current
        self.current = out
        return out
    '''
    def insert(self, *value):
        new = Node(self.current, list(value))
        if self.current and len(self.current.children) > 0:
            if self.current.children[-1].value != value:
                self.current.children.append(new)
                self.current = new
            else: return True
        else: self.current.children.append(new); self.current = new'''

    def insert(self, *value):
        # Ok, I know it seem weird, but as I'm too lazy to create a new Tree class, I will just overwrite the <insert> method whenever I'll need '''
        new = Node(self.current, list(value))
        if len(self.current.children) > 0:
            for c in self.current.children:
                if c.value[:-1] == new.value[:-1]:
                    self.current = c; return c.value[-1]
            else:
                #print(self.current.children[-1].value[:-1], new.value[:-1])
                self.current.children.append(new)
                self.current = new
            # What do u want me to say. Of course it done with the ass, but if I do everthing carefully it wont break... I hope
        else: self.push(value)

    def back(self):
        if not self.current is self.root:
            self.current = self.current.parent

    def __str__(self):
        return self.root.__str__()

class Node:
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        self.children = []

    def __str__(self, t=1):
        out = str(self.value)
        for c in self.children:
            out += '\n'+"    "*t + c.__str__(t+1)
        return out
