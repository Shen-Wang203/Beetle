def aa():
    for i in range(0,len(y)):
        y[i] += 3
    print(y)

def bb(x):
    x += 3
    xx = [0, x]
    xx[1] = xx[1] + 4
    print(xx)


y = [1,2,3]
aa()
print(y)

x = 4
bb(x)
print(x)