import numpy as np 
# import HPP_Control_Odrive as control
import HPP_Control as control
import Back_Model as BM

P0 = [0,0,138,-1.5,1,0]

HPP = BM.BackModel()
HPP.set_Pivot(np.array([[0], [0], [52.62], [0]]))
hppcontrol = control.HPP_Control()
hppcontrol.normal_traj_speed()
hppcontrol.engage_motor()
# takes about 0.168s
def send_to_hpp(R):      
    Tmm = HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
    hppcontrol.run_to_Tmm(Tmm, 2)    
    return True  

send_to_hpp(P0)
hppcontrol.disengage_motor()