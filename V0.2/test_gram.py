class A:
    def __init__(self):
        self.b = 3

    a = 2

    def plus(self):
        self.a += 3
    

class B(A):
    def __init__(self):
        super().__init__()
    
    def minus(self, x):
        y = x[:]
        self.a -= 5
        y[0] = y[0] + self.a
        return y
    

ob = B()
x = [1,2,3]
x = ob.minus(x)[:]
print(x)
print(ob.minus(x))