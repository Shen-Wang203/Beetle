f = open("testfile.log","r")
fline = f.readlines()
# print(fline)
for line in reversed(fline):
    if line[10] == '[':
        for i in range(0,len(line)):
            if line[i] == ']':
                break
        print(line[11:i])
        break
f.close()
