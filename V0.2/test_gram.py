class A:
    def __init__(self):
        self.b = 3

    a = 2

    def plus(self):
        self.a += 3
    

class B(A):
    def __init__(self):
        super().__init__()
    
    def minus(self):
        self.a -= 5
    
