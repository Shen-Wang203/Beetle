import serial
import time
from HPP_Control import HPP_Control as Run

# while True:
    # commands = input("Enter your commands (starting with the motor number): ")
    # if commands == 'end':
    #     break    
    # commands = commands + '\n'
    # motor_no = int(commands[0])
    # var = str(commands[1:])
    # var = var.encode('utf-8')             
    # else:
    #     print('Wrong Input')     
    #   

# Run.calibration()

# var0 = 'w axis0.error 0' + '\n'
# var1 = 'w axis1.error 0' + '\n'
# Run.T123_send(var0, var1)
# var0 = 'w axis0.controller.error 0' + '\n'
# var1 = 'w axis1.controller.error 0' + '\n'
# Run.T123_send(var0, var1)
# var0 = 'w axis0.motor.error 0' + '\n'
# var1 = 'w axis1.motor.error 0' + '\n'
# Run.T123_send(var0, var1)
# var0 = 'w axis0.encoder.error 0' + '\n'
# var1 = 'w axis1.encoder.error 0' + '\n'
# Run.T123_send(var0, var1)
# var = 'r axis0.encoder.error' + '\n'
# print(Run.T2_send(var))

print(Run().encoder_error_code(1))
Run().check_errors()


# commands = 'w axis0.requested_state 4' + '\n'

# clear error commands
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

# CTRL_MODE_VOLTAGE_CONTROL = 0,
# CTRL_MODE_CURRENT_CONTROL = 1,
# CTRL_MODE_VELOCITY_CONTROL = 2,
# CTRL_MODE_POSITION_CONTROL = 3,
# CTRL_MODE_TRAJECTORY_CONTROL = 4

# commands = 'p 0 10000 0 0' + '\n'
# t 0 -20000 : t motor destination
# f 0
