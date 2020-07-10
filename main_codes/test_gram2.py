# print([ x if x%2 else x*100 for x in range(1, 10) ])

def ss(anu, bse):
    anu += 1
    print(anu)
    bse += 2
    print(bse)
    return anu

b = 2
b = b + ss(b, 2)
print(b)