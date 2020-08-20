f = open('templog.txt','r')
temp = []
for line in f:
    try:
        temp.append(float(line[10:15]))
    except:
        continue

file1 = open("temp.txt","w+")
for i in range(0,len(temp)):
    file1.writelines(str(temp[i]) + '\n')