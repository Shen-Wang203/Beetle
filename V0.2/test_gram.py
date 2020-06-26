class A:
    def __init__(self):
        self.b = 3

    a = 2

    def plus(self):
        self.a += 3
    
    def doubleplus(self):
        self.plus()
        self.plus()

class C:
    def __init__(self, aa):
        self.a_class = aa
        self.c = 2

    def times(self):
        return self.a_class.b * 4


class B(C):
    def __init__(self, bb):
        super().__init__(bb)
    
    def plus(self):
        return self.a_class.b + 6
        

ob_a = A()
ob_c = C(ob_a)
ob_b = B(ob_a)
print(ob_b.plus())