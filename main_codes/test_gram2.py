# print([ x if x%2 else x*100 for x in range(1, 10) ])

def ss(anu, bse):
    anu += 1
    print(anu)
    bse += 2
    print(bse)
    return anu

loss = [1,7,4]
pos = []
p0 = [1,2,1]
p1 = [3,2,1]
p2 = [5,3,2]
pos.append(p0)
pos.append(p1)
pos.append(p2)
current_pos = []
current_pos = pos[loss.index(max(loss))][:]
print(current_pos)