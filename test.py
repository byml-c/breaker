class A:
    def __init__(self, a):
        self.x = a
        self.x(self, 1, 2)
        print(self.c)

def B(self, a, b):
    self.c = 1
    print(a+b)

b = A(B)