import serial
import time
import logging

# Timeout:
# set timeout to x seconds (float allowed) returns immediately when the requested number of bytes are available, 
# otherwise wait until the timeout expires and return all bytes that were received until then.
# readline(): read a '\n' terminated line. Do specify a timeout when opening the serial port otherwise it could 
# block forever if no newline character is received. readlines() ends with either '\n' or timeout

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

# # Company Small PC
# # COM86: T3
# Tser3 = serial.Serial('COM86', 115200, timeout=None, stopbits=1)
# # COM88: T1
# Tser1 = serial.Serial('COM88', 115200, timeout=None, stopbits=1)
# # COM87: T2
# Tser2 = serial.Serial('COM87', 115200, timeout=None, stopbits=1)
# time.sleep(.5)

# For small PC
# while True:
#     stationNum = input('Control Box #: ')
#     if stationNum == '1':
#         # Company Small PC
#         # COM86: T3
#         Tser3 = serial.Serial('COM89', 115200, timeout=None, stopbits=1)
#         # COM88: T1
#         Tser1 = serial.Serial('COM90', 115200, timeout=None, stopbits=1)
#         # COM87: T2
#         Tser2 = serial.Serial('COM91', 115200, timeout=None, stopbits=1)
#     elif stationNum == '2':
#         pass
#     elif stationNum == '3':
#         pass
#     elif stationNum == '4':
#         pass
#     elif stationNum == '5':
#         pass
#     elif stationNum == '0':
#         # Company Small PC
#         # COM86: T3
#         Tser3 = serial.Serial('COM86', 115200, timeout=None, stopbits=1)
#         # COM88: T1
#         Tser1 = serial.Serial('COM88', 115200, timeout=None, stopbits=1)
#         # COM87: T2
#         Tser2 = serial.Serial('COM87', 115200, timeout=None, stopbits=1)
#     else:
#         print('Wrong input')
#         continue
#     time.sleep(.5)
#     break
#
# # For cube PC
# while True:
#     stationNum = input('Control Box #: ')
#     # Shen's PC
#     # if stationNum == '1':
#     #     # COM15: T3
#     #     Tser3 = serial.Serial('COM23', 115200, timeout=None, stopbits=1)
#     #     # COM17: T1
#     #     Tser1 = serial.Serial('COM24', 115200, timeout=None, stopbits=1)
#     #     # COM20: T2
#     #     Tser2 = serial.Serial('COM26', 115200, timeout=None, stopbits=1)
#
#     # Jerry's laptop####################################################
#     if stationNum == '1':
#         # COM15: T3
#         Tser3 = serial.Serial('COM5', 115200, timeout=None, stopbits=1)
#         # COM17: T1
#         Tser1 = serial.Serial('COM6', 115200, timeout=None, stopbits=1)
#         # COM20: T2
#         Tser2 = serial.Serial('COM8', 115200, timeout=None, stopbits=1)
#     ####################################################################
#
#     elif stationNum == '2':
#         # COM27: T2
#         Tser2 = serial.Serial('COM27', 115200, timeout=None, stopbits=1)
#         # COM28: T1
#         Tser1 = serial.Serial('COM28', 115200, timeout=None, stopbits=1)
#         # COM32: T3
#         Tser3 = serial.Serial('COM32', 115200, timeout=None, stopbits=1)
#     elif stationNum == '3':
#         # COM35: T2
#         Tser2 = serial.Serial('COM35', 115200, timeout=None, stopbits=1)
#         # COM36: T1
#         Tser1 = serial.Serial('COM36', 115200, timeout=None, stopbits=1)
#         # COM38: T3
#         Tser3 = serial.Serial('COM38', 115200, timeout=None, stopbits=1)
#     elif stationNum == '4':
#         # COM43: T2
#         Tser2 = serial.Serial('COM43', 115200, timeout=None, stopbits=1)
#         # COM42: T1
#         Tser1 = serial.Serial('COM42', 115200, timeout=None, stopbits=1)
#         # COM46: T3
#         Tser3 = serial.Serial('COM46', 115200, timeout=None, stopbits=1)
#     elif stationNum == '5':
#         pass
#     elif stationNum == '0':
#         # COM15: T3
#         Tser3 = serial.Serial('COM15', 115200, timeout=None, stopbits=1)
#         # COM17: T1
#         Tser1 = serial.Serial('COM17', 115200, timeout=None, stopbits=1)
#         # COM20: T2
#         Tser2 = serial.Serial('COM20', 115200, timeout=None, stopbits=1)
#     else:
#         print('Wrong input')
#         continue
#     time.sleep(.5)
#     break


# # Control Box #1
# # COM5: T3
# Tser3 = serial.Serial('COM5', 115200, timeout=None, stopbits=1)
# # COM6: T1
# Tser1 = serial.Serial('COM6', 115200, timeout=None, stopbits=1)
# # COM4: T2
# Tser2 = serial.Serial('COM4', 115200, timeout=None, stopbits=1)

# Control Box #4
# COM9: T3
Tser3 = serial.Serial('COM9', 115200, timeout=0.1, stopbits=1)
# COM10: T1
Tser1 = serial.Serial('COM10', 115200, timeout=0.1, stopbits=1)
# COM8: T2
Tser2 = serial.Serial('COM8', 115200, timeout=0.1, stopbits=1)


error_log = ''
Tcounts_real = [0,0,0,0,0,0]
Tcounts_old = [0,0,0,0,0,0]
# 1 means positive direction, -1 means negative direction
direction = [1,1,1,1,1,1]
backlash_counter = [0,0,0,0,0,0]

class HPP_Control:
    def __init__(self):    
        # counter backlash, extra counts, default as 4
        self.backlash = 4
        self.limit = []
        self.A = self.define_fixture()

    def define_fixture(self):
        # A1x = 188030 - -85.796144 / 50e-6 = 1.903953e6
        # A1y = 180000 - 9.55 / 50e-6       = -11000
        # A2x = 183400 + 38.123072 / 50e-6  = 9.4586144e5
        # A2y = 190250 - -73.022182 / 50e-6 = 1.65069364e6
        # A3x = 194300 + 38.123072 / 50e-6  = 9.567614e5
        # A3y = 179350 - 92.122182 / 50e-6  = -1.66309364e6
        # Beetle #
        while True:
            BeetleNum = input('Beetle #: ')
            if BeetleNum == '1':
                x1 = 193050
                y1 = 187450
                x2 = 192010
                y2 = 189780
                x3 = 183700
                y3 = 187400
            elif BeetleNum == '2':
                x1 = 192120
                y1 = 187570
                x2 = 186840
                y2 = 187150
                x3 = 183500
                y3 = 183820
            elif BeetleNum == '3':
                x1 = 188040
                y1 = 183300
                x2 = 180030
                y2 = 183880
                x3 = 185180
                y3 = 184270
            elif BeetleNum == '4':
                x1 = 188920
                y1 = 188310
                x2 = 184950
                y2 = 181650
                x3 = 183790
                y3 = 183540
            elif BeetleNum == '5':
                x1 = 188710
                y1 = 180590
                x2 = 180400
                y2 = 187880
                x3 = 182640
                y3 = 180670
            elif BeetleNum == '0':
                x1 = 188030
                y1 = 180000
                x2 = 183400
                y2 = 190250
                x3 = 194300
                y3 = 179350
            else:
                print('Wrong input')
                continue
            A1x = x1 - (-85.796144) / 50e-6
            A1y = y1 - 9.55 / 50e-6      
            A2x = x2 + 38.123072 / 50e-6  
            A2y = y2 - (-73.022182) / 50e-6 
            A3x = x3 + 38.123072 / 50e-6  
            A3y = y3 - 92.122182 / 50e-6 
            self.limit = [x1, y1, x2, y2, x3, y3]
            return [A1x, A1y, A2x, A2y, A3x, A3y]

    # set backlash, if 0 then there is no backlash counter
    def set_backlash(self, _backlash):
        self.backlash = _backlash

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

    #Maximum send string is about 30, which is 30x10 bits, it takes 300/115200 = 2.6ms
    #if return message is 30 too, overall it will take 5.2ms.
    # Because timeout is None, readline() will wait until \n has received, so we don't need to delay a time
    def T1_send(self, var):
        var = var.encode('utf-8')
        Tser1.write(var)
        return Tser1.readline().decode('utf-8')

    def T1_send_only(self, var):
        var = var.encode('utf-8')
        Tser1.write(var)        

    def T2_send(self, var):
        var = var.encode('utf-8')
        Tser2.write(var)
        return Tser2.readline().decode('utf-8')

    def T2_send_only(self, var):
        var = var.encode('utf-8')
        Tser2.write(var)        

    def T3_send(self, var):
        var = var.encode('utf-8')
        Tser3.write(var)
        return Tser3.readline().decode('utf-8')

    def T3_send_only(self, var):
        var = var.encode('utf-8')
        Tser3.write(var)

    #Send all six commands, with return value
    def T123_send(self, var0, var1):
        return self.T1_send(var0), self.T1_send(var1), self.T2_send(var0), self.T2_send(var1), self.T3_send(var0), self.T3_send(var1)
    
    # Without return value
    def T123_send_only(self, var0, var1):
        self.T1_send_only(var0)
        self.T2_send_only(var0)
        self.T3_send_only(var0)
        self.T1_send_only(var1)
        self.T2_send_only(var1)
        self.T3_send_only(var1)           

    def Tx_send_only(self, x1, x2, x3, mode):
        # Counter backlash, if direction changed, add extra counts
        # global Tcounts_real
        global direction
        global backlash_counter
        global Tcounts_old
        _direc = direction[:]
        count_temp = [x1, 0, x2, 0, x3, 0]
        for i in [0,2,4]:
            if count_temp[i] > Tcounts_old[i]:
                _direc[i] = 1
            elif count_temp[i] < Tcounts_old[i]:
                _direc[i] = -1

            Tcounts_old[i] = count_temp[i]

            if _direc[i] != direction[i]:
                backlash_counter[i] = backlash_counter[i] + self.backlash * _direc[i]

            count_temp[i] = count_temp[i] + backlash_counter[i]
        direction = _direc[:]
        # print('Backlash: ', backlash_counter)

        if mode == 't':
            var1 = 't 0 ' + str(count_temp[0]) + '\n'
            var2 = 't 0 ' + str(count_temp[2]) + '\n'
            var3 = 't 0 ' + str(count_temp[4]) + '\n'
        else:
            var1 = 'p 0 ' + str(count_temp[0]) + ' 0 0' + '\n'     
            var2 = 'p 0 ' + str(count_temp[2]) + ' 0 0' + '\n' 
            var3 = 'p 0 ' + str(count_temp[4]) + ' 0 0' + '\n' 
        var1 = var1.encode('Utf-8')
        var2 = var2.encode('Utf-8')
        var3 = var3.encode('Utf-8')     
        Tser1.write(var1)
        Tser2.write(var2)
        Tser3.write(var3)


    def Ty_send_only(self, y1, y2, y3, mode):
        # Counter backlash, if direction changed, add extra counts
        # global Tcounts_real
        global direction
        global backlash_counter
        global Tcounts_old
        _direc = direction[:]
        count_temp = [0, y1, 0, y2, 0, y3]
        for i in [1,3,5]:           
            if count_temp[i] > Tcounts_old[i]:
                _direc[i] = 1
            elif count_temp[i] < Tcounts_old[i]:
                _direc[i] = -1

            Tcounts_old[i] = count_temp[i]

            if _direc[i] != direction[i]:
                backlash_counter[i] = backlash_counter[i] + self.backlash * _direc[i]
        
            count_temp[i] = count_temp[i] + backlash_counter[i]
        direction = _direc[:]
        # print('Backlash: ', backlash_counter)

        if mode == 't':
            var1 = 't 1 ' + str(count_temp[1]) + '\n'
            var2 = 't 1 ' + str(count_temp[3]) + '\n'
            var3 = 't 1 ' + str(count_temp[5]) + '\n'
        else:
            var1 = 'p 1 ' + str(count_temp[1]) + ' 0 0' + '\n'     
            var2 = 'p 1 ' + str(count_temp[3]) + ' 0 0' + '\n' 
            var3 = 'p 1 ' + str(count_temp[5]) + ' 0 0' + '\n' 
        var1 = var1.encode('Utf-8')
        var2 = var2.encode('Utf-8')
        var3 = var3.encode('Utf-8')     
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
    # real counts, doesn't include backlash counts
    def T_get_counts(self, T, xy):
        global Tcounts_real

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
            if xy == 'x':
                Tcounts_real[0] = int(Tcount)
            else:
                Tcounts_real[1] = int(Tcount)
        elif T == 2:
            Tser2.write(var)
            Tcount = Tser2.readline().decode('utf-8')
            if xy == 'x':
                Tcounts_real[2] = int(Tcount)
            else:
                Tcounts_real[3] = int(Tcount)
        else:
            Tser3.write(var)
            Tcount = Tser3.readline().decode('utf-8')
            if xy == 'x':
                Tcounts_real[4] = int(Tcount)
            else:
                Tcounts_real[5] = int(Tcount)

        return int(Tcount)
    

    def Tx_on_target(self, x1, x2, x3, tolerance):
        global backlash_counter

        # real counts minus backlash counts
        # x1_current = self.T_get_counts(1, 'x') - backlash_counter[0]
        # x2_current = self.T_get_counts(2, 'x') - backlash_counter[2]
        # x3_current = self.T_get_counts(3, 'x') - backlash_counter[4]

        x1_current = self.real_time_counts(1) - backlash_counter[0]
        x2_current = self.real_time_counts(3) - backlash_counter[2]
        x3_current = self.real_time_counts(5) - backlash_counter[4]

        # Check if within target
        if x1_current < (x1 - tolerance) or x1_current > (x1 + tolerance):
            return False
        elif x2_current < (x2 - tolerance) or x2_current > (x2 + tolerance):
            return False
        elif x3_current < (x3 - tolerance) or x3_current > (x3 + tolerance):
            return False
        else:
            return True


    def Ty_on_target(self, y1, y2, y3, tolerance):
        global backlash_counter

        # real counts minus backlash counts
        # y1_current = self.T_get_counts(1, 'y') - backlash_counter[1]
        # y2_current = self.T_get_counts(2, 'y') - backlash_counter[3]
        # y3_current = self.T_get_counts(3, 'y') - backlash_counter[5]

        y1_current = self.real_time_counts(2) - backlash_counter[1]
        y2_current = self.real_time_counts(4) - backlash_counter[3]
        y3_current = self.real_time_counts(6) - backlash_counter[5]        

        # Check if within target
        if y1_current < (y1 - tolerance) or y1_current > (y1 + tolerance):
            return False
        elif y2_current < (y2 - tolerance) or y2_current > (y2 + tolerance):
            return False
        elif y3_current < (y3 - tolerance) or y3_current > (y3 + tolerance):
            return False
        else:
            return True

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
        # All send once
        #Full calibration sequence
        var0 = 'w axis0.requested_state 3' + '\n'
        var1 = 'w axis1.requested_state 3' + '\n'
        self.T123_send_only(var0, var1)      

        # # Send X first, then y. This is can avoid drive voltage shortage issue
        # var0 = 'w axis0.encoder.is_ready 0' + '\n'
        # var1 = 'w axis1.encoder.is_ready 0' + '\n'
        # self.T123_send_only(var0, var1)
        # var0 = 'w axis0.requested_state 3' + '\n'
        # self.T1_send_only(var0)
        # self.T2_send_only(var0)
        # self.T3_send_only(var0)
        # var0 = 'r axis0.encoder.is_ready' + '\n'
        # while (int(self.T1_send(var0)) + int(self.T2_send(var0)) + int(self.T3_send(var0))) < 3:
        #     time.sleep(0.5)
        # var1 = 'w axis1.requested_state 3' + '\n'
        # self.T1_send_only(var1)
        # self.T2_send_only(var1)
        # self.T3_send_only(var1)  


    # Under testing
    def calibration_from_random(self):
        # 17.6 is one circle 0.5mm, and half range is 9mm, which is we need 18*17.6 = 316.8
        var1 = 'w axis1.config.general_lockin.finish_distance 180' + '\n'
        self.T3_send_only(var1)
        # Lockin spin
        var1 = 'w axis1.requested_state 9' + '\n'
        self.T3_send_only(var1)

        var1 = 'r axis1.encoder.index_found' +  '\n'
        timecount = 0
        while int(self.T3_send(var1)) == 0:
            time.sleep(1)
            timecount += 1
            if timecount > 10:
                var1 = 'w axis1.motor.config.direction -1' + '\n'
                self.T3_send_only(var1)
                var1 = 'w axis1.config.general_lockin.finish_distance 220' + '\n'
                self.T3_send_only(var1)
                var1 = 'w axis1.requested_state 9' + '\n'
                self.T3_send_only(var1)               
                timecount = 0
                var1 = 'r axis1.encoder.index_found' +  '\n'
        
        var1 = 'w axis1.motor.config.direction 1' + '\n'
        self.T3_send_only(var1)
        var1 = 'w axis1.requested_state 7' + '\n'
        self.T3_send_only(var1)



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
        # T1x =  Tmm[0] / 50e-6 + 1.903953e6
        # T1y =  Tmm[1] / 50e-6 - 11000 
        # T2x = -Tmm[2] / 50e-6 + 9.4586144e5
        # T2y =  Tmm[3] / 50e-6 + 1.65069364e6
        # T3x = -Tmm[4] / 50e-6 + 9.567614e5
        # T3y =  Tmm[5] / 50e-6 - 1.66309364e6
        T1x =  Tmm[0] / 50e-6 + self.A[0]
        T1y =  Tmm[1] / 50e-6 + self.A[1] 
        T2x = -Tmm[2] / 50e-6 + self.A[2]
        T2y =  Tmm[3] / 50e-6 + self.A[3]
        T3x = -Tmm[4] / 50e-6 + self.A[4]
        T3y =  Tmm[5] / 50e-6 + self.A[5]
        Tcounts= [int(round(T1x)), int(round(T1y)), int(round(T2x)), int(round(T2y)), int(round(T3x)), int(round(T3y))]
        return Tcounts


    def safecheck(self, Tcounts):
        global error_log
        error_log = ''
        if Tcounts[0] > (self.limit[0] - 10000) or Tcounts[0] < (self.limit[0]-17.7*20000):
            print('T1x Out of Range')
            error_log = 'T1x Out of Range' + '\n'
            return False
        elif Tcounts[1] > (self.limit[1] - 10000) or Tcounts[1] < (self.limit[1]-17.7*20000):
            print('T1y Out of Range')
            error_log = 'T1y Out of Range' + '\n'
            return False
        elif Tcounts[2] > (self.limit[2] - 10000) or Tcounts[2] < (self.limit[2]-17.7*20000):
            print('T2x Out of Range')
            error_log = 'T2x Out of Range' + '\n'
            return False
        elif Tcounts[3] > (self.limit[3] - 10000) or Tcounts[3] < (self.limit[3]-17.7*20000):
            print('T2y Out of Range')
            error_log = 'T2y Out of Range' + '\n'
            return False
        elif Tcounts[4] > (self.limit[4] - 10000) or Tcounts[4] < (self.limit[4]-17.7*20000):
            print('T3x Out of Range')
            error_log = 'T3x Out of Range' + '\n'
            return False
        elif Tcounts[5] > (self.limit[5] - 10000) or Tcounts[5] < (self.limit[5]-17.7*20000):
            print('T3y Out of Range')
            error_log = 'T3y Out of Range' + '\n'
            return False
        else:
            return True    

    # real counts, doesn't include backlash counts
    def real_time_counts(self, axis):
        global Tcounts_real
        #Check real counts
        if axis == 0:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            # var0 = 'f 0' + '\n'
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            # var1 = 'f 1' + '\n'
            try: 
                T1_real_count = int(self.T1_send(var0))
                T2_real_count = int(self.T1_send(var1))
                T3_real_count = int(self.T2_send(var0))
                T4_real_count = int(self.T2_send(var1))
                T5_real_count = int(self.T3_send(var0))
                T6_real_count = int(self.T3_send(var1))  
            except:
                T1_real_count = 299999
                T2_real_count = 299999
                T3_real_count = 299999
                T4_real_count = 299999
                T5_real_count = 299999
                T6_real_count = 299999
            Tcounts_real = [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
            return [T1_real_count, T2_real_count, T3_real_count, T4_real_count, T5_real_count, T6_real_count]
        elif axis == 1:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            try: 
                Tcounts_real[0] = int(self.T1_send(var0))
            except:
                # if fail, return a fake value for on_target check
                Tcounts_real[0] = 299999
            return Tcounts_real[0]
        elif axis == 2:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            try:
                Tcounts_real[1] = int(self.T1_send(var1))
            except:
                Tcounts_real[1] = 299999
            return Tcounts_real[1]
        elif axis == 3:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            try:
                Tcounts_real[2] = int(self.T2_send(var0))
            except:
                Tcounts_real[2] = 299999
            return Tcounts_real[2]
        elif axis == 4:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            try:
                Tcounts_real[3] = int(self.T2_send(var1))
            except:
                Tcounts_real[3] = 299999
            return Tcounts_real[3]
        elif axis == 5:
            var0 = 'r axis0.encoder.shadow_count' + '\n'
            try:
                Tcounts_real[4] = int(self.T3_send(var0))
            except:
                Tcounts_real[4] = 299999
            return Tcounts_real[4]
        elif axis == 6:
            var1 = 'r axis1.encoder.shadow_count' + '\n'
            try:
                Tcounts_real[5] = int(self.T3_send(var1)) 
            except:
                Tcounts_real[5] = 299999
            return Tcounts_real[5]
        else:
            print("Cannot indentify axis #")

    # consider backlash
    def on_target(self, Tcounts, tolerance):
        global backlash_counter

        #find real time counts for all axis
        T_current = self.real_time_counts(0)
        # print('Encoder counts before: ', T_current)
        # Consider backlash
        for i in range(0,6):
            T_current[i] = T_current[i] - backlash_counter[i]
        # print('Encoder counts after: ', T_current)

        # Check if within target
        if T_current[0] < (Tcounts[0] - tolerance) or T_current[0] > (Tcounts[0] + tolerance):
            return False
        elif T_current[1] < (Tcounts[1] - tolerance) or T_current[1] > (Tcounts[1] + tolerance):
            return False
        elif T_current[2] < (Tcounts[2] - tolerance) or T_current[2] > (Tcounts[2] + tolerance):
            return False
        elif T_current[3] < (Tcounts[3] - tolerance) or T_current[3] > (Tcounts[3] + tolerance):
            return False
        elif T_current[4] < (Tcounts[4] - tolerance) or T_current[4] > (Tcounts[4] + tolerance):
            return False
        elif T_current[5] < (Tcounts[5] - tolerance) or T_current[5] > (Tcounts[5] + tolerance):
            return False
        else:
            # print('Axial Real Position')
            # print(T_current)
            return True

    def send_counts(self, Tcounts):
        global direction
        global backlash_counter
        global Tcounts_old
        _direc = direction[:]
        _Tcounts = Tcounts[:]
        # print('Old counts: ', Tcounts_old)
        for i in range(0,6):
            if _Tcounts[i] > Tcounts_old[i]:
                _direc[i] = 1
            elif _Tcounts[i] < Tcounts_old[i]:
                _direc[i] = -1

            if _direc[i] != direction[i]:
                backlash_counter[i] = backlash_counter[i] + self.backlash * _direc[i]
            # Give backlash counter, if direction unchanged, keep the same backlash counter
            _Tcounts[i] = _Tcounts[i] + backlash_counter[i]
        direction = _direc[:]
        # print('Real counts: ', _Tcounts)
        # print('Backlash', backlash_counter)

        change_num = 20000
        # change_num = 4000
        # Send T1x
        if abs(_Tcounts[0] - Tcounts_old[0]) < change_num:
            var = 'p 0 ' + str(_Tcounts[0]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(_Tcounts[0]) + '\n'
        self.T1_send_only(var)

        # Send T1y
        if abs(_Tcounts[1] - Tcounts_old[1]) < change_num:
            var = 'p 1 ' + str(_Tcounts[1]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(_Tcounts[1]) + '\n'
        self.T1_send_only(var)

        # Send T2x
        if abs(_Tcounts[2] - Tcounts_old[2]) < change_num:
            var = 'p 0 ' + str(_Tcounts[2]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(_Tcounts[2]) + '\n'
        self.T2_send_only(var)

        # Send T2y
        if abs(_Tcounts[3] - Tcounts_old[3]) < change_num:
            var = 'p 1 ' + str(_Tcounts[3]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(_Tcounts[3]) + '\n'
        self.T2_send_only(var)

        # Send T3x
        if abs(_Tcounts[4] - Tcounts_old[4]) < change_num:
            var = 'p 0 ' + str(_Tcounts[4]) + ' 0 0' + '\n'
        else:
            var = 't 0 ' + str(_Tcounts[4]) + '\n'
        self.T3_send_only(var)

        # Send T3y
        if abs(_Tcounts[5] - Tcounts_old[5]) < change_num:
            var = 'p 1 ' + str(_Tcounts[5]) + ' 0 0' + '\n'
        else:
            var = 't 1 ' + str(_Tcounts[5]) + '\n'
        self.T3_send_only(var)

        Tcounts_old = Tcounts[:]


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

    def run_to_Tmm(self, Tmm, tolerance):
        global error_log
        global Tcounts_real
        _Tcounts = self.translate_to_counts(Tmm) 
        # print('Commands counts: ', _Tcounts)
        # self.engage_motor()
        # Do safety check, make sure the commands are within the travel range
        if self.safecheck(_Tcounts):
            # Send commands to controllers via UART
            self.send_counts(_Tcounts)
        else:
            self.disengage_motor()
            return _Tcounts
        timeout = 0
        # Set on target tolerance as +-tolerance counts
        while not self.on_target(_Tcounts, tolerance):
            # if errors exist, disengage motors, exit the loop
            time.sleep(0.1)
            timeout += 1
            if timeout > 100:
                self.disengage_motor()
                for i in range(0,6):
                    if abs(_Tcounts[i] - Tcounts_real[i]) > 20:
                        print('Motor ' + str(i+1) + ' Timeout Error')
                        error_log = error_log + 'Motor ' + str(i+1) + ' Timeout Error' + '\n'
                return _Tcounts
            # if self.check_errors():
            #     return _Tcounts
        # self.disengage_motor()
        # print('+++++++++')
        return _Tcounts
