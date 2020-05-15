import numpy as np 
# import HPP_Control_Odrive as control
import HPP_Control as control
import Back_Model as BM

P0 = [-0.2, 0.4, 138, 2, 0.5, 0]
# P0 = [-0.3113, -0.06255, 138.9585, 2, 0.5, 0]

HPP = BM.BackModel()
HPP.set_Pivot(np.array([[0], [0], [28.5], [0]]))
hppcontrol = control.HPP_Control()
hppcontrol.normal_traj_speed()
hppcontrol.engage_motor()
# takes about 0.168s
def send_to_hpp(R):   
    target_mm = R[:]     
    Tmm = HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
    target_counts = hppcontrol.run_to_Tmm(Tmm, 2)
    real_counts = control.Tcounts_real
    error_log = control.error_log
    if error_log != '':
        error_flag = True
        return False 
    else:
        error_flag = False        
    return True  

send_to_hpp(P0)
hppcontrol.disengage_motor()