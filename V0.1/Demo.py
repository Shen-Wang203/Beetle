import Back_Model as BM
from HPP_Control import HPP_Control as Run
import numpy as np
import time

P1 = [[0, 0, 138, 0, 0, 0],
     [2, 0, 138, 0, 0, 0],
     [-2, 0, 138, 0, 0, 0],
     [0, 0, 138, 0, 0, 0],
     [0, -2, 138, 0, 0, 0],
     [0, 2, 138, 0, 0, 0],
     [0, 0, 138, 0, 0, 0],
     [0, 0, 140, 0, 0, 0],
     [0, 0, 136, 0, 0, 0],
     [0, 0, 138, 0, 0, 0],
     [0, 0, 138, 3, 0, 0],
     [0, 0, 138, -3, 0, 0],
     [0, 0, 138, 0, 0, 0],
     [0, 0, 138, 0, 3, 0],
     [0, 0, 138, 0, -3, 0],
     [0, 0, 138, 0, 0, 0],
     [0, 0, 138, 0, 0, 3],
     [0, 0, 138, 0, 0, -3],
     [0, 0, 138, 0, 0, 0],
     [0, 0, 138, -3, 0, 0],
     [0, 0, 138, -3, -3, 0],
     [0, 0, 138, 0, -3, 0],
     [0, 0, 138, 3, -3, 0],
     [0, 0, 138, 3, 0, 0],
     [0, 0, 138, 3, 3, 0],
     [0, 0, 138, 0, 3, 0],
     [0, 0, 138, -3, 3, 0],
     [0, 0, 138, -3, 0, 0],
     [0, 0, 138, 0, 0, 0]
     ]

P2 = [[0, 0, 138, 0, 0, 0],
     [0, 0, 138.1, 0, 0, 0],
     [0.1, 0, 138.1, -0.6, 0.2, 0],
     [0.1, -0.05, 138.05, -0.6, 0.2, 0],
     [0.06, -0.03, 138.05, -0.62, 0.21, 0],
     [0.05, -0.03, 138.05, -0.62, 0.213, 0],
     [0.054, -0.036, 138.053, -0.616, 0.210, 0]
    ]

P3 = [[0, 0, 138, 0.2, -4, 0],
      [0, 0, 138, 0, -2, 0],
      [0, 0, 138, 0, 2, 0],
      [0, 0, 138, 0, 2, 0],
      [0, 0, 138, 0, 4, 0],
      [0, 0, 138, 0, 2, 0]
     ]


# Create a HPP fixture object
HPP = BM.BackModel()
error_flag = False

while True:
    commands = input("Enter your commands: ")
    if commands == 'end':
        break    
    elif commands == 'start':
        Run().calibration()
        print('Calibrating...')
        time.sleep(15)
        if Run().check_errors():
            Run().disengage_motor()
            break
        # Read real time counts for all axis
        Tcounts_old = Run().real_time_counts(0)
    elif commands == 'clear':
        Run().clear_errors()
    elif commands == 'demo':
        num = input("Enter Demo #: ")
        if int(num) == 1:
            P = P1
            HPP.set_Pivot(np.array([[0], [0], [0], [0]]))
        elif int(num) == 2:
            P = P2
            HPP.set_Pivot(np.array([[0], [0], [0], [0]]))
        else:
            P = P3
            HPP.set_Pivot(np.array([[0], [0], [75], [0]]))
        # Engage motors, Run() close-loop controls
        Run().engage_motor()
        # Read real time counts
        Tcounts_old = Run().real_time_counts(0)
        # Set error flag as false
        error_flag = False
        #Demo loop
        for i in range(0, len(P)):
            # Calculate each linear axial's position from given platform position
            Tmm = HPP.findAxialPosition(P[i][0], P[i][1], P[i][2], P[i][3], P[i][4], P[i][5])
            # print(Tmm)
            # A function that can translate position value in mm to encoder counts
            Tcounts = Run().translate_to_counts(Tmm)
            print('Target: ')
            print(Tcounts)
            # Do safety check, make sure the commands are within the travel range
            if Run().safecheck(Tcounts):
                # Run() commands to controllers via UART
                Run().send_counts(Tcounts, Tcounts_old)
                Tcounts_old = Tcounts
            else:
                error_flag = True
                break
            while not Run().on_target(Tcounts):
                #if errors exist, exit the loop, disengage motors
                if Run().check_errors():
                    error_flag = True
                    break
            if error_flag:
                break
        Run().disengage_motor()
    elif commands == 'debug':
        Run().debug()
    elif commands == 'counts':
        num = input("Enter your axis #: ")
        print(Run().real_time_counts(int(num)))
    elif commands == 'close':
        Run().engage_motor()
        #go to a reset position so that index can be found on next startup.
        T_reset = [-20000, -20000, -20000, -20000, -20000, -20000]
        Tcounts_old = Run().real_time_counts(0)
        Run().send_counts(T_reset, Tcounts_old)
        while not Run().on_target(T_reset):
            #if errors exist, exit the loop, disengage motors
            if Run().check_errors():
                Run().disengage_motor()
                break
        Run().disengage_motor()
    elif commands == 'goto':
        goto = input("Enter your target position (seprate with ,): ")
        comma = []
        for i in range(0,len(goto)):
            if goto[i] == ',':
                comma.append(i)
        try:
            X = float(goto[0:comma[0]])
            Y = float(goto[comma[0]+1:comma[1]])
            Z = float(goto[comma[1]+1:comma[2]])
            Rx = float(goto[comma[2]+1:comma[3]])
            Ry = float(goto[comma[3]+1:comma[4]])
            Rz = float(goto[comma[4]+1:])
        except:
            print('Wrong input')
        # print([X, Y, Z, Rx, Ry, Rz])
        # Read real time counts
        Tcounts_old = Run().real_time_counts(0)
        Tmm = HPP.findAxialPosition(X, Y, Z, Rx, Ry, Rz)  
        Tcounts = Run().translate_to_counts(Tmm) 
        print('Target: ')
        print(Tcounts)
        Run().engage_motor()
        # Do safety check, make sure the commands are within the travel range
        if Run().safecheck(Tcounts):
            # Run() commands to controllers via UART
            Run().send_counts(Tcounts, Tcounts_old)
            Tcounts_old = Tcounts
        else:
            error_flag = True
            continue
        while not Run().on_target(Tcounts):
            #if errors exist, exit the loop, disengage motors
            if Run().check_errors():
                error_flag = True
                break
        Run().disengage_motor()
    else:
        print('Wrong Input')     

Run().close_ports()


#Some Odrive commands
# commands = 'w axis0.requested_state 4' + '\n'

# Clear Errors:
# w axis0.error 0

# r vbus_voltage
# r axis0.encoder.shadow_count

# AXIS_STATE_UNDEFINED = 0,           //<! will fall through to idle
# AXIS_STATE_IDLE = 1,                //<! disable PWM and do nothing
# AXIS_STATE_STARTUP_SEQUENCE = 2, //<! the actual sequence is defined by the config.startup_... flags
# AXIS_STATE_FULL_CALIBRATION_SEQUENCE = 3,   //<! Run() all calibration procedures, then idle
# AXIS_STATE_MOTOR_CALIBRATION = 4,   //<! Run() motor calibration
# AXIS_STATE_SENSORLESS_CONTROL = 5,  //<! Run() sensorless control
# AXIS_STATE_ENCODER_INDEX_SEARCH = 6, //<! Run() encoder index search
# AXIS_STATE_ENCODER_OFFSET_CALIBRATION = 7, //<! Run() encoder offset calibration
# AXIS_STATE_CLOSED_LOOP_CONTROL = 8,  //<! Run() closed loop control
# AXIS_STATE_LOCKIN_SPIN = 9,       //<! Run() lockin spin
# AXIS_STATE_ENCODER_DIR_FIND = 10,




