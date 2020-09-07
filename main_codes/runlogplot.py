import matplotlib.pyplot as plt
import statistics

# Average time
# f = open('runlog.log', 'r')
# time = []
# for line in f:
#     if line[15:19] == 'cost':
#         a = float(line[22:26])
#         if a > 30:
#             time.append(a)
# total = 0
# for i in time:
#     total += i
# print(total/len(time))

# f = open('runlog.log', 'r')
# f2 = open('pos_loss.txt','w+')
# start = False
# fetch = 0
# for line in f:
#     if not start and line[16:32] == 'Alignment Starts':
#         start = True
#         f2.writelines('New Alignment' + '\n')
#         fetch = 1
#         continue
#     if start and (line[15:33] == 'Alignment Finished' or line[21:30] == 'cancelled'):
#         start = False
#         if line[15:33] == 'Alignment Finished':
#             f2.writelines(line[46:52] + '\n')
#         f2.writelines('Alignment finished' + '\n')
#         f2.writelines('*****************' + '\n')
#         continue
#     if start and not fetch and line[10:24] == 'Z optim starts': 
#         fetch = 2
#         continue
#     if start and line[10:16] == 'Failed':
#         fetch = 1
#         continue
#     if start and fetch and line[10:14] == 'Meet':
#         fetch = 0
#         continue
#     if start and fetch:
#         if line[10:14] == 'Time':
#             continue
#         f2.writelines(line[10:])
#         fetch -= 1

def linear_interp(x,y,grid):
    lxy = len(x)
    lgrid = len(grid)
    Y = [0]*lgrid
    for i in range(0,lgrid):
        if grid[i] < x[0]:
            Y[i] = (y[1] - y[0]) * (grid[i] - x[0]) / (x[1] - x[0]) + y[0]
            continue
        if grid[i] > x[lxy-1]:
            Y[i] = (y[lxy-1] - y[lxy-2]) * (grid[i] - x[lxy-2]) / (x[lxy-1] - x[lxy-2]) + y[lxy-2]
            continue
        for j in range(1,lxy):
            if grid[i] >= x[j-1] and grid[i] <= x[j]:
                Y[i] = (y[j] - y[j-1]) * (grid[i] - x[j-1]) / (x[j] - x[j-1]) + y[j-1]
                continue
    return Y

f = open('pos_loss.txt', 'r')
start = False
loss = []
z = []
twelve = []
ten = []
eight = []
five = []
three = []
two = []
one = []
pointeight = []
pointfive = []
pointthree = []
grid = [-12,-10,-8,-5,-3,-2,-1,-0.8,-0.5,-0.3]
for line in f:
    if not start and line[0:3] == 'New':
        start = True
        loss = []
        z = []
        continue
    if start and line[0] == '-':
        loss.append(float(line[0:5]))
        continue
    if start and line[0] == '[':
        count = 0
        a = 0
        for i in range(0,len(line)):
            if line[i] == ',':
                count += 1
                if count == 2:
                    a = i
                elif count == 3:
                    break
        z.append(float(line[a+2:i]))
        continue
    if start and line[0] == '*':
        start = False
        if len(loss) <= 2 or loss[0] > -8:
            continue
        if len(loss) != len(z):
            z.append(z[-1])
        for i in range(0,len(z)):
            z[i] = z[i] - max(z)
        for j in range(1,len(loss)):
            if loss[j] <= loss[j-1]:
                break
        if len(loss[0:j-1]) <= 4:
            continue
        L = loss[0:j-1]
        Z = z[0:j-1]
        plt.plot(L, Z)
        s = linear_interp(L,Z,grid)
        twelve.append(s[0])
        ten.append(s[1])
        eight.append(s[2])
        five.append(s[3])
        three.append(s[4])
        two.append(s[5])
        one.append(s[6])
        pointeight.append(s[7])
        pointfive.append(s[8])
        pointthree.append(s[9])

ftwelve = statistics.median(twelve)
ften = statistics.median(ten)
feight = statistics.median(eight)
ffive = statistics.median(five)
fthree = statistics.median(three)
ftwo = statistics.median(two)
fone = statistics.median(one)
fpointeight = statistics.median(pointeight)
fpointfive = statistics.median(pointfive)
fpointthree = statistics.median(pointthree)
Z = [ftwelve, ften, feight, ffive, fthree, ftwo, fone, fpointeight, fpointfive, fpointthree]
Z = [round(num, 5) for num in Z]
print(Z)
plt.plot(grid, Z, 'ko-', linewidth=3)
plt.grid()
plt.show()
