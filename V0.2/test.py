# import matplotlib.pyplot as plt
import PowerMeter as PM
import numpy as np 
import time
import logging
from XYscan import XYscan 
# import HPP_Control_Odrive as control
import HPP_Control as control
from Curing_Align import Curing_Active_Alignment

logging.basicConfig(filename='runlog.log', filemode='w', level=logging.INFO)

xys = XYscan()
cure = Curing_Active_Alignment()
hppcontrol = control.HPP_Control()
hppcontrol.engage_motor()
hppcontrol.normal_traj_speed()
xys.set_starting_point([-0.26, 0.38, 138.3, 2.5, 0.5, 0])
# xys.set_starting_point([-0.2116, 0.34855, 138.35806, 2, 0.5, 0])
xys.set_limit_Z(145)
xys.set_loss_criteria(-0.3)
# xys.set_angle_flag(True)
xys.set_angle_flag(False)
P0 = xys.autoRun()


cure.set_loss_criteria(max(xys.loss_rec)-0.03)
cure.curing_run(P0)

hppcontrol.disengage_motor()
hppcontrol.normal_traj_speed()
file1 = open("pos.txt","w+")
file2 = open("loss.txt","w+")
file3 = open('Curing_loss.txt', 'w+')
file4 = open('Curing_pos.txt', 'w+')
a = xys.pos_rec[:]
b = xys.loss_rec[:]
c = cure.loss_curing_rec[:]
d = cure.pos_curing_rec[:]
for i in range(0,len(a)):
    file1.writelines(str(a[i]) + '\n')
for i in range(0,len(b)):
    file2.writelines(str(b[i]) + '\n')
for i in range(0, len(c)):
    file3.writelines(str(c[i]) + '\n')
for i in range(0, len(d)):
    file4.writelines(str(d[i]) + '\n')

# hppcontrol.slow_traj_speed()
# hppcontrol.engage_motor()
# while True:
#     goto = input("Enter your target position (seprate with ,): ")
#     comma = []
#     for i in range(0,len(goto)):
#         if goto[i] == ',':
#             comma.append(i)
#     try:
#         X = float(goto[0:comma[0]])
#         Y = float(goto[comma[0]+1:comma[1]])
#         Z = float(goto[comma[1]+1:comma[2]])
#         Rx = float(goto[comma[2]+1:comma[3]])
#         Ry = float(goto[comma[3]+1:comma[4]])
#         Rz = float(goto[comma[4]+1:])
#     except:
#         print('Wrong input')

#     P0 = [X,Y,Z,Rx,Ry,Rz]
#     xys.send_to_hpp(P0)
# hppcontrol.disengage_motor()


# ps = Pattern_Search(5)
# hppcontrol = control.HPP_Control()
# hppcontrol.engage_motor()
# ps.set_init_step = 0.05
# ps.set_acceleration(2)
# # ps.set_startpoint([-0.2,-0.02,138.82,2,0.5,0])
# ps.set_startpoint([-0.1,0,138,0,0,0])
# ps.autoRun()
# hppcontrol.disengage_motor()

# psg = Pattern_SimplexGradient(5)
# psg.autoRun()
# vc = []
# a = [1,0,0,2,2,0]
# b = [1,1,3,0,1,1]
# c = [1,2,1,1,2,1]
# d = [0,2,0,1,1,2]
# e = [2,1,4,2,2,0]
# f = [2,1,2,0,2,0]
# # # g = [0,0,1,0,1,0]
# vc.append(a)
# vc.append(b)
# vc.append(c)
# vc.append(d)
# vc.append(e)
# vc.append(f)
# # vc.append(g)
# print(len(vc))
# # print(np.asarray(vc[2][0:3]))
# f = [0,1,2,3,4,5]
# grad = psg.simplexGradient(vc,f)
# print(grad)
# grad = np.append(grad, [0])
# barray = np.asarray([1,1,0,1,0,0])
# print(np.dot(grad,barray))
# cos = np.dot(grad,barray) / (np.linalg.norm(grad) * np.linalg.norm(barray))
# print(cos)
# aa = psg.search(grad, a)
# print(aa)

# a = [2,1,2,0,2,0]
# for i in range(0,len(vc)):
#     if a == vc[i]:
#         print('find')

# gs = Gradient_Search()
# gs.set_learning_rate(4)
# gs.set_reduction_ratio(0.5)
# gs.set_beta(0.9)
# gs.autoRun()

# Combination of pattern search and gradient search
# ps = Pattern_Search()
# gs = Gradient_Search()
# res_gs = gs.autoRun()
# pos_gs = res_gs[0]
# step_gs = res_gs[1]
# print(pos_gs)
# print(step_gs)
# ps.set_startpoint(pos_gs)
# ps.set_init_step(step_gs)
# ps.autoRun()

# MyFile=open('loss.txt','w')

# test = [0,2.3,139.9,0.2,1,0]
# test2 = [2,3,139.4,0.3,1,0]
# test3 = [1,3.5,138.3,0.4,1.2,0]
# pos = []
# pos.append(test)
# pos.append(test2)
# pos.append(test3)
# print(pos)
# y = -1.9
# y1 = -1.6
# y2 = -1.4
# loss = []
# loss.append(y)
# loss.append(y1)
# loss.append(y2)
# print(loss)

# xx = np.asarray(pos)
# np.savetxt('pos', xx, delimiter=',')
# x = []
# for i in range(0,len(loss)):
#     x.append(pos[i][0]) 
# print(x)
# plt.plot(x, loss)
# plt.show()



# class A:
#     def __init__(self):
#         self.cmd = ''
    
#     Anum = 4

#     def opt(self):
#         self.Anum += 1
#         # print(PM.power_read())
#         _x = 20
#         def asub():
#             self.Anum = 3
#             y = _x + self.Anum
#             logging.info('running in asub')
#             return y

#         def bsub():
#             return asub() + 3

#         yy = bsub()
#         logging.info('output is: ' + str(yy))


# class B(A):
#     def __init__(self):
#         A.__init__(self)
#         self.value = 3

#     def set_value(self, a):
#         self.value = a

#     def print_(self):
#         print(self.value)
    
#     def plus_one(self, a):
#         a = a + 1

# inst = A()
# inst.opt()
# print(inst.Anum)
# logging.info(inst.Anum)
