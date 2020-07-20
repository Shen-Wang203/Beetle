import Back_Model as BM
import HPP_Control as control
import numpy as np
import time
from PyQt5 import QtCore
import logging
from StaticVar import StaticVar
from XYscan import XYscan 
from Curing_Align import Curing_Active_Alignment

error_flag = False 

class CMDInputThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.cmd = ''
        self.currentPosition = [0,0,138,0,0,0]
    #error_log, target_mm, target_counts, real_counts
    sig1 = QtCore.pyqtSignal(str, list, list, list, bool)
    # Motor status signal
    # 0: Idle
    # 1: Running
    # 2: Auto-alignment runnning
    # 3: Pre-curing running
    # 4: Curing running
    sig2 = QtCore.pyqtSignal(int)

    def setcmd(self, cmdtext):
        self.cmd = cmdtext

    def run(self):
        self.enter_commands(self.cmd)

    def stop(self):
        self.terminate()

    #Create a HPP fixture object
    HPP = BM.BackModel()
    HPP.set_Pivot(np.array([[0], [0], [52.62], [0]]))
    hppcontrol = control.HPP_Control()

    logfilename = 'runlog.log'
    # Create a new log file each time the program is launched
    # logging.basicConfig(filename=logfilename, filemode='w', level=logging.INFO)
    # Append the logg file to the existing one
    logging.basicConfig(filename=logfilename, level=logging.INFO)

    P1 = [  [0, 0, 138, 0, 0, 0],
            [4, 0, 138, 0, 0, 0],
            [-4, 0, 138, 0, 0, 0],
            [0, 0, 138, 0, 0, 0],
            [0, -4, 138, 0, 0, 0],
            [0, 4, 138, 0, 0, 0],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 142, 0, 0, 0],
            [0, 0, 134, 0, 0, 0],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 138, 4, 0, 0],
            [0, 0, 138, -4, 0, 0],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 138, 0, 4, 0],
            [0, 0, 138, 0, -4, 0],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 138, 0, 0, 4],
            [0, 0, 138, 0, 0, -4],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 138, -4, 0, 0],
            [0, 0, 138, -3, -3, 0],
            [0, 0, 138, 0, -4, 0],
            [0, 0, 138, 3, -3, 0],
            [0, 0, 138, 4, 0, 0],
            [0, 0, 138, 3, 3, 0],
            [0, 0, 138, 0, 4, 0],
            [0, 0, 138, -3, 3, 0],
            [0, 0, 138, -4, 0, 0],
            [0, 0, 138, 0, 0, 0]
        ]

    P2 = [  [0, 0, 138, 0, 0, 0],
            [0, 0, 138.1, 0, 0, 0],
            [0.1, 0, 138.1, -0.6, 0.2, 0],
            [0.1, -0.05, 138.05, -0.6, 0.2, 0],
            [0.06, -0.03, 138.05, -0.62, 0.21, 0],
            [0.05, -0.03, 138.05, -0.62, 0.213, 0],
            [0.054, -0.036, 138.053, -0.616, 0.210, 0],
            [0.054, -0.036, 138.053, -0.616, 0.240, 0],
            [0.054, -0.036, 138.053, -0.636, 0.240, 0],
            [0.057, -0.056, 138.053, -0.636, 0.240, 0],
            [0.057, -0.052, 138.056, -0.636, 0.240, 0],
            [0.057, -0.052, 138.05, -0.636, 0.240, 0]
        ]

    P3 = [  [0, 0, 138, 0, -4, 0],
            [0, 0, 138, 0, -2, 0],
            [0, 0, 138, 0, 0, 0],
            [0, 0, 138, 0, 2, 0],
            [0, 0, 138, 0, 4, 0],
            [0, 0, 138, 0, 2, 0],
            [0, 0, 138, 0, 0, 0]
        ]

    def enter_commands(self, cmd):
        commands = cmd  
        global error_flag
        error_flag = False
        error_log = ''
        target_counts = [0,0,0,0,0,0]
        target_mm = [0,0,138,0,0,0]
        real_counts = [0,0,0,0,0,0]

        if commands == 'calib':
            error_log = ''
            self.hppcontrol.calibration()
            self.sig2.emit(5)
            # print('Calibrating...')
            time.sleep(18)
            error_flag = False
            if self.hppcontrol.check_errors():
                error_flag = True
            # Read real time counts for all axis
            control.Tcounts_old = self.hppcontrol.real_time_counts(0)

        elif commands == 'clear':
            self.hppcontrol.clear_errors()
        
        elif commands[0:4] == 'demo':
            error_log = ''
            num = commands[4]
            if int(num) == 1:
                P = self.P1
                self.HPP.set_Pivot(np.array([[0], [0], [0], [0]]))
            elif int(num) == 2:
                P = self.P2
                self.HPP.set_Pivot(np.array([[0], [0], [0], [0]]))
            else:
                P = self.P3
                self.HPP.set_Pivot(np.array([[0], [0], [75], [0]]))
            # Engage motors, do close-loop controls
            self.hppcontrol.engage_motor()
            self.sig2.emit(1)
            # Read real time counts
            # Tcounts_old = self.hppcontrol.real_time_counts(0)
            # Set error flag as false
            error_flag = False
            
            #Demo loop
            for i in range(0, len(P)):
                target_mm = [P[i][0], P[i][1], P[i][2], P[i][3], P[i][4], P[i][5]]
                # Calculate each linear axial's position from given platform position
                Tmm = self.HPP.findAxialPosition(P[i][0], P[i][1], P[i][2], P[i][3], P[i][4], P[i][5])
                # A function that can translate position value in mm to encoder counts
                Tcounts = self.hppcontrol.translate_to_counts(Tmm)
                target_counts = Tcounts[:]
                # Do safety check, make sure the commands are within the travel range
                if self.hppcontrol.safecheck(Tcounts):
                    # Send commands to controllers via UART
                    self.hppcontrol.send_counts(Tcounts)
                else:
                    error_flag = True
                    break
                while not self.hppcontrol.on_target(Tcounts, 2):
                    #if errors exist, exit the loop, disengage motors
                    if self.hppcontrol.check_errors():
                        error_flag = True
                        break
                if error_flag:
                    break
                real_counts = control.Tcounts_real[:]
                self.sig1.emit(error_log, target_mm, target_counts, real_counts, error_flag)
        
        elif commands == 'debug':
            error_log = ''
            self.hppcontrol.debug()
        
        elif commands == 'counts':
            num = input("Enter your axis #: ")
            print(self.hppcontrol.real_time_counts(int(num)))

        elif commands == 'close':
            error_log = ''
            self.hppcontrol.engage_motor()
            self.sig2.emit(1)
            #go to a reset position so that index can be found on next startup.
            T_reset = [-2000, -2000, -2000, -2000, -2000, -2000]
            target_counts = T_reset[:]
            # Tcounts_old = self.hppcontrol.real_time_counts(0)
            self.hppcontrol.send_counts(T_reset)
            while not self.hppcontrol.on_target(T_reset, 2):
                #if errors exist, exit the loop, disengage motors
                if self.hppcontrol.check_errors():
                    self.hppcontrol.disengage_motor()
                    self.sig2.emit(0)
                    break
            real_counts = control.Tcounts_real
        
        elif commands[0:4] == 'goto':
            error_log = ''
            # goto = input("Enter your target position (seprate with ,): ")
            commands.replace(' ', '')
            goto = commands[4:]
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
                error_log = 'Wrong Input'
                return
            target_mm = [X, Y, Z, Rx, Ry, Rz]
            print('Command mm: ', target_mm)       
            Tmm = self.HPP.findAxialPosition(X, Y, Z, Rx, Ry, Rz)  
            
            self.hppcontrol.engage_motor()
            self.sig2.emit(1)
            target_counts = self.hppcontrol.run_to_Tmm(Tmm, 2)
            real_counts = control.Tcounts_real
            self.currentPosition = target_mm[:]

        elif commands == 'align':
            xys = XYscan(self.HPP, self.hppcontrol)
            self.hppcontrol.engage_motor()
            self.sig2.emit(2)
            P0 = [0,0,139,-0.3,0.5,0]
            xys.set_starting_point(P0)
            
            if StaticVar.productType == "VOA":
                xys.product_select('VOA')
            elif StaticVar.productType == "1xN":
                xys.product_select('1xN')
                
            xys.second_try = False
            # self.xys.set_loss_criteria(-0.2)
            P1 = xys.autoRun(strategy=1) 
            # P1 = xys.autoRun(strategy=2)           
            self.currentPosition = P1[:]
            target_mm = P1[:]
            real_counts = control.Tcounts_real
            # we don't use target_counts in gui now so just set it as a random value
            target_counts = [0,0,0,0,0,0]

        elif commands == 'precure':
            cure = Curing_Active_Alignment(self.HPP, self.hppcontrol)
            self.hppcontrol.engage_motor()
            self.sig2.emit(3)
            if StaticVar.product_select == "VOA":
                cure.product_select('VOA')
            elif StaticVar.product_select == "1xN":
                cure.product_select('1xN')
            cure.set_loss_criteria(max(self.xys.loss_rec)-0.03)
            P1 = cure.pre_curing_run(self.currentPosition)
            self.currentPosition = P1[:]
            target_mm = P1[:]
            real_counts = control.Tcounts_real
            # we don't use target_counts in gui now so just set it as a random value
            target_counts = [0,0,0,0,0,0]

        elif commands == 'curing':
            cure = Curing_Active_Alignment(self.HPP, self.hppcontrol)
            self.sig2.emit(4)
            if StaticVar.product_select == "VOA":
                cure.product_select('VOA')
            elif StaticVar.product_select == "1xN":
                cure.product_select('1xN')
            P1 = cure.curing_run(self.currentPosition)
            self.currentPosition = P1[:]
            target_mm = P1[:]
            real_counts = control.Tcounts_real
            # we don't use target_counts in gui now so just set it as a random value
            target_counts = [0,0,0,0,0,0]

        elif commands == 'disarm':
            target_mm = self.currentPosition[:]
            self.hppcontrol.normal_traj_speed()
        else:
            print('Wrong Input')     

        error_log = control.error_log
        if error_log != '':
            error_flag = True
        self.sig1.emit(error_log, target_mm, target_counts, real_counts, error_flag)
        self.hppcontrol.disengage_motor()
        self.sig2.emit(0)

    def close_ports(self):
        self.hppcontrol.close_ports()


    #Some Odrive commands
    # commands = 'w axis0.requested_state 4' + '\n'

    # Clear Errors:
    # w axis0.error 0

    # r vbus_voltage
    # r axis0.encoder.shadow_count



    # AXIS_STATE_UNDEFINED = 0,           //<! will fall through to idle
    # AXIS_STATE_IDLE = 1,                //<! disable PWM and do nothing
    # AXIS_STATE_STARTUP_SEQUENCE = 2, //<! the actual sequence is defined by the config.startup_... flags
    # AXIS_STATE_FULL_CALIBRATION_SEQUENCE = 3,   //<! run all calibration procedures, then idle
    # AXIS_STATE_MOTOR_CALIBRATION = 4,   //<! run motor calibration
    # AXIS_STATE_SENSORLESS_CONTROL = 5,  //<! run sensorless control
    # AXIS_STATE_ENCODER_INDEX_SEARCH = 6, //<! run encoder index search
    # AXIS_STATE_ENCODER_OFFSET_CALIBRATION = 7, //<! run encoder offset calibration
    # AXIS_STATE_CLOSED_LOOP_CONTROL = 8,  //<! run closed loop control
    # AXIS_STATE_LOCKIN_SPIN = 9,       //<! run lockin spin
    # AXIS_STATE_ENCODER_DIR_FIND = 10,


