import HPP_Control as control
from XYscan import XYscan 
import time

hppcontrol = control.HPP_Control()
xys = XYscan()

P0 = [0.1268, 0.1652, 139.286, 2, 0.5, 0]

hppcontrol.engage_motor()
xys.send_to_hpp(P0)

x1 = 47195
x2 = -21960
x3 = 74445
print('Target Counts: ', [x1, x2, x3])

hppcontrol.Tx_send_only(x1, x2, x3, 's')
# check on target, need to check all of them
while not hppcontrol.Tx_on_target(x1, x2, x3, 2):
    time.sleep(0.5)

time.sleep(2)

x1 = x1 + 20
x2 = x2 - 20
x3 = x3 - 20
print('Target Counts: ', [x1, x2, x3])

hppcontrol.Tx_send_only(x1, x2, x3, 's')
# check on target, need to check all of them
while not hppcontrol.Tx_on_target(x1, x2, x3, 2):
    time.sleep(0.5)

time.sleep(2)

x1 = x1 - 20
x2 = x2 + 20
x3 = x3 + 20
print('Target Counts: ', [x1, x2, x3])

hppcontrol.Tx_send_only(x1, x2, x3, 's')
# check on target, need to check all of them
while not hppcontrol.Tx_on_target(x1, x2, x3, 2):
    time.sleep(0.5)

hppcontrol.disengage_motor()