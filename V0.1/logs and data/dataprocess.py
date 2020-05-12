import matplotlib.pyplot as plt
import numpy as np

file1 = open('pos_data.txt', 'r') 
filex = open('x.txt','w+')
filey = open('y.txt','w')
filez = open('z.txt','w')
Lines = file1.readlines()
num = 0
x = []
y = []
z = []
for line in Lines:
    a = 0
    b = 0
    c = 0
    num = 0
    for i in range(0,len(line)):
        if line[i] == ' ':
            num += 1
            if num == 1:
                a = i
            if num == 2:
                b = i
            if num == 3:
                c = i
                break
    filex.writelines(line[1:a-1]+'\n')
    filey.writelines(line[a+1:b-1]+'\n')
    filez.writelines(line[b+1:c-1]+'\n')

