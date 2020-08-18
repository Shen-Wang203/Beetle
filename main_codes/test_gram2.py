import serial
import time
Arduino = serial.Serial('COM4', 115200, timeout=0.1, stopbits=1)
time.sleep(2)

for i in range(0,4):
    var = 'b' + '\n'
    var = var.encode('Utf-8')
    Arduino.write(var)
    time.sleep(0.5)
    T = Arduino.readline().decode('utf-8')
    print(T[0:-1])

    var = 't' + '\n'
    var = var.encode('Utf-8')
    Arduino.write(var)
    time.sleep(0.5)
    T = Arduino.readline().decode('utf-8')
    print(T[0:-1])


