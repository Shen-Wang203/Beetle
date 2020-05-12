import HPP_Control_Odrive as control
import math
import time
from XYscan import XYscan 
import Back_Model as BM

hppcontrol = control.HPP_Control()
xys = XYscan()
HPP = BM.BackModel()

hppcontrol.engage_motor()

P0 = [0,0,138,0,0,0]
xys.send_to_hpp(P0)

Tmm = HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
Tcounts = hppcontrol.translate_to_counts(Tmm) 
print('start')
# A sine wave to test
t0 = time.monotonic()
for i in range(0,200):
    setpoint1 = 10000.0 * math.cos((time.monotonic() - t0)*2) - 10000
    setpoint2 = 10000.0 * math.sin((time.monotonic() - t0)*2)
    x1 = Tcounts[0] + setpoint1
    x2 = Tcounts[2] - setpoint1
    x3 = Tcounts[4] - setpoint1
    y1 = Tcounts[1] + setpoint2
    y2 = Tcounts[3] + setpoint2
    y3 = Tcounts[5] + setpoint2
    hppcontrol.Tx_send_only(x1, x2, x3, 's')
    hppcontrol.Ty_send_only(y1, y2, y3, 's')
    time.sleep(0.1)
print('end')
hppcontrol.disengage_motor()