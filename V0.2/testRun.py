import PowerMeter as PM
import Back_Model as BM
import numpy as np 
import time
import logging
from XYscan import XYscan 
# import HPP_Control_Odrive as control
import HPP_Control as control
from Curing_Align import Curing_Active_Alignment

logfilename = 'runlog.log'
logging.basicConfig(filename=logfilename, filemode='w', level=logging.INFO)

HPP = BM.BackModel()
HPP.set_Pivot(np.array([[0], [0], [52.62], [0]]))
hppcontrol = control.HPP_Control()

P0 = [0,0,138,-1.5,1,0]

xys = XYscan(HPP, hppcontrol)
hppcontrol.engage_motor()
hppcontrol.normal_traj_speed()
xys.set_starting_point(P0)
xys.set_limit_Z(145)
xys.set_loss_criteria(-0.3)
P1 = xys.autoRun()

# cure = Curing_Active_Alignment(HPP, hppcontrol)
# cure.set_starting_point(P0)
# cure.set_loss_criteria(max(xys.loss_rec)-0.03)
# cure.curing_run(P1)

# hppcontrol.disengage_motor()
# hppcontrol.normal_traj_speed()
# file1 = open("pos.txt","w+")
# file2 = open("loss.txt","w+")
# file3 = open('Curing_loss.txt', 'w+')
# file4 = open('Curing_pos.txt', 'w+')
# a = xys.pos_rec[:]
# b = xys.loss_rec[:]
# c = cure.loss_curing_rec[:]
# d = cure.pos_curing_rec[:]
# for i in range(0,len(a)):
#     file1.writelines(str(a[i]) + '\n')
# for i in range(0,len(b)):
#     file2.writelines(str(b[i]) + '\n')
# for i in range(0, len(c)):
#     file3.writelines(str(c[i]) + '\n')
# for i in range(0, len(d)):
#     file4.writelines(str(d[i]) + '\n')
