import serial
import time
# # Cube PC
# # COM15: T3
# Tser3 = serial.Serial('COM15', 115200, timeout=None, stopbits=1)
# # COM17: T1
# Tser1 = serial.Serial('COM17', 115200, timeout=None, stopbits=1)
# # COM20: T2
# Tser2 = serial.Serial('COM20', 115200, timeout=None, stopbits=1)
# time.sleep(.5)

# # Personal PC
# # COM15: T3
# Tser3 = serial.Serial('COM5', 115200, timeout=None, stopbits=1)
# # COM17: T1
# Tser1 = serial.Serial('COM4', 115200, timeout=None, stopbits=1)
# # COM20: T2
# Tser2 = serial.Serial('COM6', 115200, timeout=None, stopbits=1)
# time.sleep(.5)

# Company Small PC
# COM86: T3
Tser3 = serial.Serial('COM86', 115200, timeout=None, stopbits=1)
# COM88: T1
Tser1 = serial.Serial('COM88', 115200, timeout=None, stopbits=1)
# COM87: T2
Tser2 = serial.Serial('COM87', 115200, timeout=None, stopbits=1)
time.sleep(.5)

error_log = ''
Tcounts_real = [0,0,0,0,0,0]

class HPP_Control:

    def __init__(self):      
        #Maximum send string is about 30, which is 30x10 bits, it takes 300/115200 = 2.6ms
        #if return message is 30 too, overall it will take 5.2ms.
        self.short_delay = 0.005
        # long_delay = 0.1


    #Close ports
    def close_ports(self):
        Tser1.close()
        Tser2.close()
        Tser3.close()

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

    # Because timeout is None, readline() will wait until \n has received, so we don't need to delay a time
    def T1_send(self, var):
        var = var.encode('utf-8')
        Tser1.write(var)
        # time.sleep(self.short_delay)    
        # if Tser1.in_waiting:
        return Tser1.readline().decode('utf-8')

    def T1_send_only(self, var):
        var = var.encode('utf-8')
        Tser1.write(var)        

    def T2_send(self, var):
        var = var.encode('utf-8')
        Tser2.write(var)
        # time.sleep(self.short_delay)    
        # if Tser2.in_waiting:
        return Tser2.readline().decode('utf-8')

    def T2_send_only(self, var):
        var = var.encode('utf-8')
        Tser2.write(var)        

    def T3_send(self, var):
        var = var.encode('utf-8')
        Tser3.write(var)
        # time.sleep(self.short_delay)    
        # if Tser3.in_waiting:
        return Tser3.readline().decode('utf-8')

    def T3_send_only(self, var):
        var = var.encode('utf-8')
        Tser3.write(var)

    #Send all six commands, with return value
    def T123_send(self, var0, var1):
        return self.T1_send(var0), self.T1_send(var1), self.T2_send(var0), self.T2_send(var1), self.T3_send(var0), self.T3_send(var1)
    
    # Without return value
    def T123_send_only(self, var0, var1):
        return self.T1_send_only(var0), self.T1_send_only(var1), self.T2_send_only(var0), self.T2_send_only(var1), self.T3_send_only(var0), self.T3_send_only(var1)           

    def Tx_send_only(self, x1, x2, x3, mode):
        if mode == 't':
            var1 = 't 0 ' + str(x1) + '\n'
            var2 = 't 0 ' + str(x2) + '\n'
            var3 = 't 0 ' + str(x3) + '\n'
        else:
            var1 = 'p 0 ' + str(x1) + ' 0 0' + '\n'     
            var2 = 'p 0 ' + str(x2) + ' 0 0' + '\n' 
            var3 = 'p 0 ' + str(x3) + ' 0 0' + '\n' 
        var1 = var1.encode('Utf-8')
        var2 = var2.encode('Utf-8')
        var3 = var3.encode('Utf-8')     
        # Time delay between first and last send is 2*11*10/115200 = 1.9ms
        # If acceleration is smaller than 554000, the counts is less than 1 during this time   
        Tser1.write(var1)
        Tser2.write(var2)
        Tser3.write(var3)

    def Ty_send_only(self, y1, y2, y3, mode):
        if mode == 't':
            var1 = 't 1 ' + str(y1) + '\n'
            var2 = 't 1 ' + str(y2) + '\n'
            var3 = 't 1 ' + str(y3) + '\n'
        else:
            var1 = 'p 1 ' + str(y1) + ' 0 0' + '\n'     
            var2 = 'p 1 ' + str(y2) + ' 0 0' + '\n' 
            var3 = 'p 1 ' + str(y3) + ' 0 0' + '\n' 
        var1 = var1.encode('Utf-8')
        var2 = var2.encode('Utf-8')
        var3 = var3.encode('Utf-8')     
        # Time delay between first and last send is 2*11*10/115200 = 1.9ms 
        # If acceleration is smaller than 554000, the counts is less than 1 during this time   
        Tser1.write(var1)
        Tser2.write(var2)
        Tser3.write(var3)        

    # # for total (send and receive) byte less than 26
    # def T1_get_counts(self, var):
    #     var = var.encode('utf-8')
    #     Tser1.write(var)
    #     time.sleep(0.003)    
    #     # for use with 'f 0' commands, return float current counts
    #     if Tser1.in_waiting:
    #         fstr = Tser1.readline().decode('utf-8')
    #         for i in range(0,len(fstr)):
    #             if fstr[i] == ' ':
    #                 break
    #         return float(fstr[0:i])

    # T is 1 2 or 3; xy is 'x' or 'y'
    def T_get_counts(self, T, xy):
        if xy == 'x':
            # var = 'f 0' + '\n'
            var = 'r axis0.encoder.shadow_count' + '\n'
        else:
            # var = 'f 1' + '\n'   
            var = 'r axis1.encoder.shadow_count' + '\n'     
        var = var.encode('utf-8')
        if T == 1:
            Tser1.write(var)
            Tcount = Tser1.readline().decode('utf-8')
            # Tcount = Tser1.read_until(terminator=' ').decode('utf-8')
        elif T == 2:
            Tser2.write(var)
            Tcount = Tser2.readline().decode('utf-8')
            # Tcount = Tser2.read_until(terminator=' ').decode('utf-8')
        else:
            Tser3.write(var)
            Tcount = Tser3.readline().decode('utf-8')
            # Tcount = Tser3.read_until(terminator=' ').decode('utf-8')
        return int(Tcount)
    
    def check_errors(self):
        global error_log
        var0 = 'r axis0.error' + '\n' 
        var1 = 'r axis1.error' + '\n'
        M1_error = int(self.T1_send(var0))
        M2_error = int(self.T1_send(var1))
        M3_error = int(self.T2_send(var0))
        M4_error = int(self.T2_send(var1))
        M5_error = int(self.T3_send(var0))
        M6_error = int(self.T3_send(var1))

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
        

    def clear_errors(self):
        global error_log
        error_log = ''
        var0 = 'w axis0.error 0' + '\n'
        var1 = 'w axis1.error 0' + '\n'
        self.T123_send_only(var0, var1)
        var0 = 'w axis0.controller.error 0' + '\n'
        var1 = 'w axis1.controller.error 0' + '\n'
        self.T123_send_only(var0, var1)
        var0 = 'w axis0.motor.error 0' + '\n'
        var1 = 'w axis1.motor.error 0' + '\n'
        self.T123_send_only(var0, var1)
        var0 = 'w axis0.encoder.error 0' + '\n'
        var1 = 'w axis1.encoder.error 0' + '\n'
        self.T123_send_only(var0, var1)
        print('Errors are cleared')
        error_log = 'Errors are cleared'

    def calibration(self):
        #Full calibration sequence
        var0 = 'w axis0.requested_state 3' + '\n'
        var1 = 'w axis1.requested_state 3' + '\n'
        self.T123_send_only(var0, var1)      

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
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            # var0 = 'f 0' + '\n'
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            # var1 = 'f 1' + '\n'
            T1_real_count = int(self.T1_send(var0))
            T2_real_count = int(self.T1_send(var1))
            T3_real_count = int(self.T2_send(var0))
            T4_real_count = int(self.T2_send(var1))
            T5_real_count = int(self.T3_send(var0))
            T6_real_count = int(self.T3_send(var1))    
            Tcounts_real = [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
            return [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
        elif axis == 1:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            return int(self.T1_send(var0))
        elif axis == 2:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            return int(self.T1_send(var1))
        elif axis == 3:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            return int(self.T2_send(var0))
        elif axis == 4:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            return int(self.T2_send(var1))
        elif axis == 5:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            return int(self.T3_send(var0))
        elif axis == 6:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            return int(self.T3_send(var1)) 
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
        change_num = 20000
        # change_num = 4000
        # Send T1x
        if abs(Tcounts[0] - Tcount_old[0]) < change_num:
            var = 'p 0 ' + str(Tcounts[0]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(Tcounts[0]) + '\n'
        self.T1_send_only(var)

        # Send T1y
        if abs(Tcounts[1] - Tcount_old[1]) < change_num:
            var = 'p 1 ' + str(Tcounts[1]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(Tcounts[1]) + '\n'
        self.T1_send_only(var)

        # Send T2x
        if abs(Tcounts[2] - Tcount_old[2]) < change_num:
            var = 'p 0 ' + str(Tcounts[2]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(Tcounts[2]) + '\n'
        self.T2_send_only(var)

        # Send T2y
        if abs(Tcounts[3] - Tcount_old[3]) < change_num:
            var = 'p 1 ' + str(Tcounts[3]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(Tcounts[3]) + '\n'
        self.T2_send_only(var)

        # Send T3x
        if abs(Tcounts[4] - Tcount_old[4]) < change_num:
            var = 'p 0 ' + str(Tcounts[4]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(Tcounts[4]) + '\n'
        self.T3_send_only(var)

        # Send T3y
        if abs(Tcounts[5] - Tcount_old[5]) < change_num:
            var = 'p 1 ' + str(Tcounts[5]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(Tcounts[5]) + '\n'
        self.T3_send_only(var)

    def engage_motor(self):
        # Send T1x close-loop
        var0 = 'w axis0.requested_state 8' + '\n'
        var1 = 'w axis1.requested_state 8' + '\n'
        self.T123_send_only(var0, var1)

    def disengage_motor(self):
        # Send T1x Idle
        var0 = 'w axis0.requested_state 1' + '\n'
        var1 = 'w axis1.requested_state 1' + '\n'
        self.T123_send_only(var0, var1) 

    def slow_traj_speed(self):
        # 43 byte, time 43 * 10 / 115200 = 4ms
        var0 = 'w axis0.trap_traj.config.accel_limit 500' + '\n'
        var00 = 'w axis0.trap_traj.config.decel_limit 500' + '\n'
        var000 = 'w axis0.trap_traj.config.vel_limit 500' + '\n'
        var1 = 'w axis1.trap_traj.config.accel_limit 500' + '\n'
        var11 = 'w axis1.trap_traj.config.decel_limit 500' + '\n'
        var111 = 'w axis1.trap_traj.config.vel_limit 500' + '\n'
        self.T123_send_only(var0, var1)
        self.T123_send_only(var00, var11)    
        self.T123_send_only(var000, var111)

    def normal_traj_speed(self):
        # 43 byte, time 43 * 10 / 115200 = 4ms
        var0 = 'w axis0.trap_traj.config.accel_limit 70000' + '\n'
        var00 = 'w axis0.trap_traj.config.decel_limit 70000' + '\n'
        var000 = 'w axis0.trap_traj.config.vel_limit 100000' + '\n'
        var1 = 'w axis1.trap_traj.config.accel_limit 70000' + '\n'
        var11 = 'w axis1.trap_traj.config.decel_limit 70000' + '\n'
        var111 = 'w axis1.trap_traj.config.vel_limit 100000' + '\n'
        self.T123_send_only(var0, var1)
        self.T123_send_only(var00, var11) 
        self.T123_send_only(var000, var111)


    def debug(self):
        while True:
            debug = input("Enter your debug commands (starting with Motor #): ")
            if debug == 'exit':
                break
            debug = debug + '\n'
            try:
                motor_no = int(debug[0])
            except:
                print('Wrong input, start with motor #') 
                continue   
            var = str(debug[1:])
            if motor_no == 1 or motor_no == 2:
                print(self.T1_send(var))
            elif motor_no == 3 or motor_no == 4:
                print(self.T2_send(var))
            elif motor_no == 5 or motor_no == 6:
                print(self.T3_send(var))
            else:
                print('Wrong input, cannot identify motor #')
        return None

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
