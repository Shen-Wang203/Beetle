import interpolation

x = [-3,-4,-2.3]
y = [0] * 3
for i in range(0,3):
    y[i] = x[i]**2 + 3

grid = [*range(-3,9,2)]
s = interpolation.barycenteric_interp(x,y,grid)
a = grid[s.index(max(s))]
print(s)
print(a)
# file1 = open('pos.txt', 'r') 
# Lines = file1.readlines()

# loss = []
# for line in Lines:
#     line = line[:-2:]
#     loss.append(float(line))

# plt.plot(loss,'-+') 
# plt.ylabel('dB')
# plt.xlabel('Iterations') 
# plt.title('Loss change')
# plt.show()

# num = 0
# z = []
# for line in Lines:
#     a = 0
#     b = 0
#     num = 0
#     for i in range(0,len(line)):
#         if line[i] == ' ':
#             num += 1
#             if num == 1:
#                 a = i
#             if num == 2:
#                 b = i
#     z.append(float(line[a+1:b-1]))

# plt.plot(z,'-+') 
# plt.ylabel('mm')
# plt.xlabel('Iterations') 
# plt.title('X change')
# plt.show()
