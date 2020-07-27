a = [0,0,140,-0.3,-0.4,0]
file1 = open("initial_pos.txt","r")
b = file1.read()
print(b+'esd')
file1.close()

b = a[:]
print(b)

c = 72
minute = c // 60
second = c % 60
print(str(minute) + "' " + str(second) + "''")