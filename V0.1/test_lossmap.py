import PowerMeter as PM
import numpy as np 
import time
import logging
# import HPP_Control_Odrive as control
import HPP_Control as control
import Back_Model as BM
import logging

logging.basicConfig(filename='runlog.log', filemode='w', level=logging.INFO)

# -0.3 dB, range(diamter) 10um, 0.2
P0 = [-0.3552, -0.0698, 138.8142, 2, 0.5, 0]
# -5 dB, range(diameter) 40um, 1um
# P0 = [-0.3472, -0.0662, 138.7416, 2, 0.5, 0]
# -10 dB, range(diameter) 60um, 1.5um
# P0 = [-0.3442, -0.068, 138.6216, 2, 0.5, 0]
# -15 dB, range(diameter) 80um, 2um
# P0 = [-0.3402, -0.074, 138.4416, 2, 0.5, 0]
# -20 dB, range(diameter) 140um, 3.5um
# P0 = [-0.3222, -0.082, 138.03, 2, 0.5, 0]


# 20 um range(diameter), 400 counts, +-10um
mapping_range = 0.010
mapping_space = 0.0002
steps = int(mapping_range / mapping_space)

HPP = BM.BackModel()
HPP.set_Pivot(np.array([[0], [0], [28.5], [0]]))
hppcontrol = control.HPP_Control()

tolerance = 2

def send_to_hpp(R):   
    # target_mm = R[:]
    # Read real time counts  
    Tcounts_old = control.Tcounts_real       
    Tmm = HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
    target_counts = hppcontrol.run_to_Tmm(Tmm, Tcounts_old, tolerance)
    # real_counts = control.Tcounts_real
    error_log = control.error_log
    if error_log != '':
        error_flag = True
        return False 
    else:
        error_flag = False        
    return True  

# Original center position P
def mapping(P):
    P0_o = P[0] - mapping_range / 2 - mapping_space
    P[1] = P[1] - mapping_range / 2 - mapping_space
    # y mapping
    for j in range(0, steps+1):
        P[1] = P[1] + mapping_space
        P[0] = P0_o
        # x mapping
        for i in range(0, steps+1):
            P[0] = P[0] + mapping_space
            send_to_hpp(P)
            time.sleep(0.5)
            fetch_loss()
            pos.append(P[:])
            print(P)
            logging.info(loss[-1])
            logging.info(P)
            if loss[-1] > -1.5:
                tolerance = 1
            else:
                tolerance = 2
loss = []
pos = []
    

def fetch_loss():
    loss.append(PM.power_read())

# Need to have engage and disengage in run_to_Tmm function
mapping(P0)




f1 = open('pos_map.txt', 'w+')
f2 = open('loss_map.txt', 'w+')
for i in range(0,len(pos)):
    f1.writelines(str(pos[i]) + '\n')
for i in range(0,len(loss)):
    f2.writelines(str(loss[i]) + '\n')

