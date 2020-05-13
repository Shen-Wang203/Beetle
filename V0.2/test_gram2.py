file3 = open('Curing_loss.txt', 'w+')
c = [1,2,1,2,4,2]
for i in range(0,len(c)):
    file3.writelines(str(c[i]) + '\n')