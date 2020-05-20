class A:
    def __init__(self):
        self.b = 3

    a = 2

    def plus(self):
        self.a += 3
    
    def doubleplus(self):
        self.plus()
        self.plus()


class B(A):
    def __init__(self):
        super().__init__()
    
    def minus(self, anum, bnum):
        y = anum[:]
        yy = bnum[:]
        self.a -= 5
        y[0] = y[0] + self.a
        return y
    
    def plus(self):
        self.a += 6

ob = B()
x = ob.doubleplus()
print(ob.a)