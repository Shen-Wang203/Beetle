import HPP_Control_Odrive as control
from XYscan import XYscan 
import time

hppcontrol = control.HPP_Control()
xys = XYscan()

hppcontrol.engage_motor()
P1 = [-0.3562,-0.0904,138.921,2,0.5,0]
P0 = [-0.35, -0.087, 138.921,2,0.5,0]
xys.send_to_hpp(P0)
time.sleep(0.2)
xys.send_to_hpp(P1)
hppcontrol.plot(1,'x')
# hppcontrol.disengage_motor()




