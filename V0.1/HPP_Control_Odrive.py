import serial
import time
import odrive

# odrivetool rate-test

T1 = odrive.find_any(serial_number="208739844D4D")
T2 = odrive.find_any(serial_number="208339834D4D")
T3 = odrive.find_any(serial_number="205C39844D4D")
time.sleep(0.5)

error_log = ''
Tcounts_real = [0,0,0,0,0,0]

class HPP_Control:

    def __init__(self):      
        # self.short_delay = 0.005
        # long_delay = 0.1
        pass

    #Error code interpretation
    def axis_error_code(self, code):
        switcher = {
            0x00: "ERROR_NONE",
            0x01: "ERROR_INVALID_STATE",
            0x02: "ERROR_DC_BUS_UNDER_VOLTAGE",
            0x04: "ERROR_DC_BUS_OVER_VOLTAGE",
            0x08: "ERROR_CURRENT_MEASUREMENT_TIMEOUT",
            0x10: "ERROR_BRAKE_RESISTOR_DISARMED",
            0x20: "ERROR_MOTOR_DISARMED",
            0x40: "ERROR_MOTOR_FAILED",
            0x80: "ERROR_SENSORLESS_ESTIMATOR_FAILED",
            0x100: "ERROR_ENCODER_FAILED",
            0x200: "ERROR_CONTROLLER_FAILED",
            0x400: "ERROR_POS_CTRL_DURING_SENSORLESS",
            0x800: "ERROR_WATCHDOG_TIMER_EXPIRED",
        }
        return switcher.get(code, "Invalid Code")

    def motor_error_code(self, code):
        switcher = {
            0x00: "ERROR_NONE",
            0x01: "ERROR_PHASE_RESISTANCE_OUT_OF_RANGE",
            0x02: "ERROR_PHASE_INDUCTANCE_OUT_OF_RANGE",
            0x04: "ERROR_ADC_FAILED",
            0x08: "ERROR_DRV_FAULT",
            0x10: "ERROR_CONTROL_DEADLINE_MISSED",
            0x20: "ERROR_NOT_IMPLEMENTED_MOTOR_TYPE",
            0x40: "ERROR_BRAKE_CURRENT_OUT_OF_RANGE",
            0x80: "ERROR_MODULATION_MAGNITUDE",
            0x100: "ERROR_BRAKE_DEADTIME_VIOLATION",
            0x200: "ERROR_UNEXPECTED_TIMER_CALLBACK",
            0x400: "ERROR_CURRENT_SENSE_SATURATION",
            0x800: "ERROR_INVERTER_OVER_TEMP",
            0x1000: "ERROR_CURRENT_UNSTABLE",
        }
        return switcher.get(code, "Invalid Code")

    def encoder_error_code(self, code):
        switcher = {
            0x00: "ERROR_NONE",
            0x01: "ERROR_UNSTABLE_GAIN",
            0x02: "ERROR_CPR_OUT_OF_RANGE",
            0x04: "ERROR_NO_RESPONSE",
            0x08: "ERROR_UNSUPPORTED_ENCODER_MODE",
            0x10: "ERROR_ILLEGAL_HALL_STATE",
            0x20: "ERROR_INDEX_NOT_FOUND_YET",
        }
        return switcher.get(code, "Invalid Code")

    def controller_error_code(self, code):
        switcher = {
            0x00: "ERROR_NONE",
            0x01: "ERROR_OVERSPEED",
        }
        return switcher.get(code, "Invalid Code")

    # send X positions
    def Tx_send_only(self, x1, x2, x3, mode):
        if mode == 't':
            T1.axis0.controller.move_to_pos(x1)
            T2.axis0.controller.move_to_pos(x2)
            T3.axis0.controller.move_to_pos(x3)
        else:
            T1.axis0.controller.pos_setpoint = x1
            T2.axis0.controller.pos_setpoint = x2
            T3.axis0.controller.pos_setpoint = x3

    def Ty_send_only(self, y1, y2, y3, mode):
        if mode == 't':
            T1.axis1.controller.move_to_pos(y1)
            T2.axis1.controller.move_to_pos(y2)
            T3.axis1.controller.move_to_pos(y3)
        else:
            T1.axis1.controller.pos_setpoint = y1
            T2.axis1.controller.pos_setpoint = y2
            T3.axis1.controller.pos_setpoint = y3   

    # T is 1 2 or 3; xy is 'x' or 'y'
    def T_get_counts(self, T, xy):
        if T == 1:
            if xy == 'x':
                Tcount = T1.axis0.encoder.shadow_count 
            else:
                Tcount = T1.axis1.encoder.shadow_count
        elif T == 2:
            if xy == 'x':
                Tcount = T2.axis0.encoder.shadow_count 
            else:
                Tcount = T2.axis1.encoder.shadow_count          
        else:
            if xy == 'x':
                Tcount = T3.axis0.encoder.shadow_count 
            else:
                Tcount = T3.axis1.encoder.shadow_count  
        return Tcount
    
    # TODO: test
    def check_errors(self):
        global error_log
        M1_error = T1.axis0.error
        M2_error = T1.axis1.error
        M3_error = T2.axis0.error
        M4_error = T2.axis1.error
        M5_error = T3.axis0.error
        M6_error = T3.axis1.error

        odrive.get_errors(T1)
        odrive.get_errors(T2)
        odrive.get_errors(T3)

        #if have errors, return true
        if (M1_error + M2_error + M3_error + M4_error + M5_error + M6_error) != 0:
            self.error_explain([M1_error, M2_error, M3_error, M4_error, M5_error, M6_error]) 
            self.disengage_motor()    
            return True
        else:
            error_log = ''
            return False

    def error_explain(self, axial_error):
        string = ''
        global error_log
        error_log = ''
        for i in range(0,len(axial_error)):           
            if axial_error[i] == 0x40: #Motor failed
                var = 'motor.error' + '\n'
                if i == 0 or i == 2 or i == 4:
                    var = 'r axis0.'  + var
                else:
                    var = 'r axis1.' + var
            elif axial_error[i] == 0x100: #Encoder failed
                var = 'encoder.error' + '\n'
                if i == 0 or i == 2 or i == 4:
                    var = 'r axis0.'  + var
                else:
                    var = 'r axis1.' + var            
            elif axial_error[i] == 0x200: #Controller failed
                var = 'controller.error' + '\n'
                if i == 0 or i == 2 or i == 4:
                    var = 'r axis0.'  + var
                else:
                    var = 'r axis1.' + var
            else:
                var = '' #Axis failed

            if var == '':
                string = string + 'Axial ' + str(i+1) + ' error: ' + self.axis_error_code(axial_error[i]) +'\n'
                # print(string)
                continue
            elif i <= 1:
                code = self.T1_send(var)
            elif i <= 3:
                code = self.T2_send(var)
            else:
                code = self.T3_send(var)

            if var[8] == 'm':
                string = string + 'Motor ' + str(i+1) + ' error: ' + self.motor_error_code(int(code[-4:])) + '\n'
                # print(string)
            elif var[8] == 'e':
                string = string + 'Encoder ' + str(i+1) + ' error: ' + self.encoder_error_code(int(code[-4:])) + '\n'
                # print(string)
            elif var[8] == 'c':
                string = string + 'Controller ' + str(i+1) + ' error: ' + self.controller_error_code(int(code[-4:])) + '\n'
                # print(string)
        print(string)
        error_log = string
        
    # TODO: test
    def clear_errors(self):
        global error_log
        error_log = ''

        odrive.clear_errors(T1)
        odrive.clear_errors(T2)
        odrive.clear_errors(T3)

        print('Errors are cleared')
        error_log = 'Errors are cleared'

    def calibration(self):
        #Full calibration sequence  
        T1.axis0.requested_state = 3
        T1.axis1.requested_state = 3
        T2.axis0.requested_state = 3
        T2.axis1.requested_state = 3
        T3.axis0.requested_state = 3
        T3.axis1.requested_state = 3        

        # #Index Search
        # var0 = 'w axis0.requested_state 6' + '\n'
        # var1 = 'w axis1.requested_state 6' + '\n'
        # T123_send_only(var0, var1)    
        
        # #wait for index search to finish
        # time.sleep(5)

        # #Encoder Offset Calibration
        # var0 = 'w axis0.requested_state 7' + '\n'
        # var1 = 'w axis1.requested_state 7' + '\n'
        # T123_send_only(var0, var1)



    # T1x: 
    # Real: -95.346144 + 9.5 + 0.05 = -85.796144 mm ; Counts: 188030
    # T1Y:
    # Real: 9.55 mm                                 ; Counts: 180000
    # T2X:
    # Real: 47.673072 - 9.5 - 0.05 = 38.123072 mm   ; Counts: 183400
    # T2Y:
    # Real: -82.572182 + 9.5 + 0.05 = -73.022182 mm ; Counts: 190250
    # T3X:
    # Real: 47.673072 - 9.5 - 0.05 = 38.123072 mm   ; Counts: 194300
    # T3Y:
    # Real: 82.572182 + 9.5 + 0.05 = 92.122182 mm   ; Counts: 179350
    # Counts = (+-)Real / 50e-6 + A (T2x and T3x are -, the others are +)
    # A1x = 188030 - -85.796144 / 50e-6 = 1.903953e6
    # A1y = 180000 - 9.55 / 50e-6       = -11000
    # A2x = 183400 + 38.123072 / 50e-6  = 9.4586144e5
    # A2y = 190250 - -73.022182 / 50e-6 = 1.65069364e6
    # A3x = 194300 + 38.123072 / 50e-6  = 9.567614e5
    # A3y = 179350 - 92.122182 / 50e-6  = -1.66309364e6
    def translate_to_counts(self, Tmm):
        T1x =  Tmm[0] / 50e-6 + 1.903953e6
        T1y =  Tmm[1] / 50e-6 - 11000 
        T2x = -Tmm[2] / 50e-6 + 9.4586144e5
        T2y =  Tmm[3] / 50e-6 + 1.65069364e6
        T3x = -Tmm[4] / 50e-6 + 9.567614e5
        T3y =  Tmm[5] / 50e-6 - 1.66309364e6
        Tcounts= [int(round(T1x)), int(round(T1y)), int(round(T2x)), int(round(T2y)), int(round(T3x)), int(round(T3y))]
        return Tcounts


    def safecheck(self, Tcounts):
        global error_log
        error_log = ''
        if Tcounts[0] > 187030 or Tcounts[0] < -181300:
            print('T1x Out of Range')
            error_log = 'T1x Out of Range' + '\n'
            return False
        elif Tcounts[1] > 179000 or Tcounts[1] < -197140:
            print('T1y Out of Range')
            error_log = 'T1y Out of Range' + '\n'
            return False
        elif Tcounts[2] > 176058 or Tcounts[2] < -186284:
            print('T2x Out of Range')
            error_log = 'T2x Out of Range' + '\n'
            return False
        elif Tcounts[3] > 188710 or Tcounts[3] < -180777:
            print('T2y Out of Range')
            error_log = 'T2y Out of Range' + '\n'
            return False
        elif Tcounts[4] > 193300 or Tcounts[4] < -177160:
            print('T3x Out of Range')
            error_log = 'T3x Out of Range' + '\n'
            return False
        elif Tcounts[5] > 182450 or Tcounts[5] < -192000:
            print('T3y Out of Range')
            error_log = 'T3y Out of Range' + '\n'
            return False
        else:
            return True    

    def real_time_counts(self, axis):
        global Tcounts_real
        #Check real counts
        if axis == 0:
            T1_real_count = T1.axis0.encoder.shadow_count
            T2_real_count = T1.axis1.encoder.shadow_count
            T3_real_count = T2.axis0.encoder.shadow_count
            T4_real_count = T2.axis1.encoder.shadow_count
            T5_real_count = T3.axis0.encoder.shadow_count
            T6_real_count = T3.axis1.encoder.shadow_count  
            Tcounts_real = [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
            return [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
        elif axis == 1:
            return T1.axis0.encoder.shadow_count
        elif axis == 2:
            return T1.axis1.encoder.shadow_count
        elif axis == 3:
            return T2.axis0.encoder.shadow_count
        elif axis == 4:
            return T2.axis1.encoder.shadow_count
        elif axis == 5:
            return T3.axis0.encoder.shadow_count
        elif axis == 6:
            return T3.axis1.encoder.shadow_count
        else:
            print("Cannot indentify axis #")


    def on_target(self, Tcounts, tolerance):
        #find real time counts for all axis
        T_real = self.real_time_counts(0)

        #Check if within target
        if T_real[0] < (Tcounts[0] - tolerance) or T_real[0] > (Tcounts[0] + tolerance):
            return False
        elif T_real[1] < (Tcounts[1] - tolerance) or T_real[1] > (Tcounts[1] + tolerance):
            return False
        elif T_real[2] < (Tcounts[2] - tolerance) or T_real[2] > (Tcounts[2] + tolerance):
            return False
        elif T_real[3] < (Tcounts[3] - tolerance) or T_real[3] > (Tcounts[3] + tolerance):
            return False
        elif T_real[4] < (Tcounts[4] - tolerance) or T_real[4] > (Tcounts[4] + tolerance):
            return False
        elif T_real[5] < (Tcounts[5] - tolerance) or T_real[5] > (Tcounts[5] + tolerance):
            return False
        else:
            # print('Axial Real Position')
            # print(T_real)
            return True


    def send_counts(self, Tcounts, Tcount_old):
        change_num = 10000
        # change_num = 4000
        # Send T1x
        if abs(Tcounts[0] - Tcount_old[0]) < change_num:
            T1.axis0.controller.pos_setpoint = Tcounts[0]
        else:
            T1.axis0.controller.move_to_pos(Tcounts[0])

        # Send T1y
        if abs(Tcounts[1] - Tcount_old[1]) < change_num:
            T1.axis1.controller.pos_setpoint = Tcounts[1]
        else:
            T1.axis1.controller.move_to_pos(Tcounts[1])

        # Send T2x
        if abs(Tcounts[2] - Tcount_old[2]) < change_num:
            T2.axis0.controller.pos_setpoint = Tcounts[2]
        else:
            T2.axis0.controller.move_to_pos(Tcounts[2])

        # Send T2y
        if abs(Tcounts[3] - Tcount_old[3]) < change_num:
            T2.axis1.controller.pos_setpoint = Tcounts[3]
        else:
            T2.axis1.controller.move_to_pos(Tcounts[3])

        # Send T3x
        if abs(Tcounts[4] - Tcount_old[4]) < change_num:
            T3.axis0.controller.pos_setpoint = Tcounts[4]
        else:
            T3.axis0.controller.move_to_pos(Tcounts[4])

        # Send T3y
        if abs(Tcounts[5] - Tcount_old[5]) < change_num:
            T3.axis1.controller.pos_setpoint = Tcounts[5]
        else:
            T3.axis1.controller.move_to_pos(Tcounts[5])

    def engage_motor(self):
        # Send T1x close-loop
        T1.axis0.requested_state = 8
        T1.axis1.requested_state = 8
        T2.axis0.requested_state = 8
        T2.axis1.requested_state = 8
        T3.axis0.requested_state = 8
        T3.axis1.requested_state = 8  

    def disengage_motor(self):
        # Send T1x Idle
        T1.axis0.requested_state = 1
        T1.axis1.requested_state = 1
        T2.axis0.requested_state = 1
        T2.axis1.requested_state = 1
        T3.axis0.requested_state = 1
        T3.axis1.requested_state = 1  

    def slow_traj_speed(self):
        T1.axis0.trap_traj.config.vel_limit = 500
        T1.axis0.trap_traj.config.accel_limit = 500
        T1.axis0.trap_traj.config.decel_limit = 500
        T1.axis1.trap_traj.config.vel_limit = 500
        T1.axis1.trap_traj.config.accel_limit = 500
        T1.axis1.trap_traj.config.decel_limit = 500

        T2.axis0.trap_traj.config.vel_limit = 500
        T2.axis0.trap_traj.config.accel_limit = 500
        T2.axis0.trap_traj.config.decel_limit = 500
        T2.axis1.trap_traj.config.vel_limit = 500
        T2.axis1.trap_traj.config.accel_limit = 500
        T2.axis1.trap_traj.config.decel_limit = 500

        T3.axis0.trap_traj.config.vel_limit = 500
        T3.axis0.trap_traj.config.accel_limit = 500
        T3.axis0.trap_traj.config.decel_limit = 500
        T3.axis1.trap_traj.config.vel_limit = 500
        T3.axis1.trap_traj.config.accel_limit = 500
        T3.axis1.trap_traj.config.decel_limit = 500

    def normal_traj_speed(self):
        T1.axis0.trap_traj.config.vel_limit = 100000
        T1.axis0.trap_traj.config.accel_limit = 70000
        T1.axis0.trap_traj.config.decel_limit = 70000
        T1.axis1.trap_traj.config.vel_limit = 100000
        T1.axis1.trap_traj.config.accel_limit = 70000
        T1.axis1.trap_traj.config.decel_limit = 70000

        T2.axis0.trap_traj.config.vel_limit = 100000
        T2.axis0.trap_traj.config.accel_limit = 70000
        T2.axis0.trap_traj.config.decel_limit = 70000
        T2.axis1.trap_traj.config.vel_limit = 100000
        T2.axis1.trap_traj.config.accel_limit = 70000
        T2.axis1.trap_traj.config.decel_limit = 70000

        T3.axis0.trap_traj.config.vel_limit = 100000
        T3.axis0.trap_traj.config.accel_limit = 70000
        T3.axis0.trap_traj.config.decel_limit = 70000
        T3.axis1.trap_traj.config.vel_limit = 100000
        T3.axis1.trap_traj.config.accel_limit = 70000
        T3.axis1.trap_traj.config.decel_limit = 70000

    def debug(self):
        while True:
            debug = input("Enter your debug commands: ")
            if debug == 'exit':
                break
            exec(debug)

    def plot(self, T, xy):
        if T == 1:
            if xy == 'x':
                odrive.start_liveplotter(lambda:[T1.axis0.encoder.pos_estimate, T1.axis0.controller.pos_setpoint])
            else:
                odrive.start_liveplotter(lambda:[T1.axis1.encoder.pos_estimate, T1.axis1.controller.pos_setpoint])
        elif T == 2:
            if xy == 'x':
                odrive.start_liveplotter(lambda:[T2.axis0.encoder.pos_estimate, T2.axis0.controller.pos_setpoint])
            else:
                odrive.start_liveplotter(lambda:[T2.axis1.encoder.pos_estimate, T2.axis1.controller.pos_setpoint])
        else:
            if xy == 'x':
                odrive.start_liveplotter(lambda:[T3.axis0.encoder.pos_estimate, T3.axis0.controller.pos_setpoint])
            else:
                odrive.start_liveplotter(lambda:[T3.axis1.encoder.pos_estimate, T3.axis1.controller.pos_setpoint])            

    def run_to_Tmm(self, Tmm, Tcounts_old, tolerance):
        _Tcounts = self.translate_to_counts(Tmm) 
        # self.engage_motor()
        # Do safety check, make sure the commands are within the travel range
        if self.safecheck(_Tcounts):
            # Send commands to controllers via UART
            self.send_counts(_Tcounts, Tcounts_old)
        else:
            self.disengage_motor()
            return _Tcounts
        # Set on target tolerance as +-tolerance counts
        while not self.on_target(_Tcounts, tolerance):
            # if errors exist, disengage motors, exit the loop
            pass
            # if self.check_errors():
            #     return _Tcounts
        # self.disengage_motor()
        return _Tcounts
