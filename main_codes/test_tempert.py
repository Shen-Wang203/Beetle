import serial
import time
import logging

logfilename = 'templog.log'
logging.basicConfig(filename=logfilename, level=logging.INFO)

Arduino = serial.Serial('COM8', 115200, stopbits=1)
# Arduino.close()
time.sleep(2)

def fetch_temperature():
    # var = 'b' + '\n'
    # var = var.encode('Utf-8')
    # Arduino.write(var)
    # # time.sleep(0.1)
    # T = Arduino.readline().decode('utf-8')
    # print(T[0:-1])
    # logging.info(T[0:-1])

    var = 't' + '\n'
    var = var.encode('Utf-8')
    Arduino.write(var)
    # time.sleep(0.1)
    T = Arduino.readline().decode('utf-8')
    print('T'+T[0:-1])
    logging.info('T'+T[0:-1])


fetch_temperature()
print('Temperature fetch time 0')
logging.info('Temperature fetch time 0')
start_time = time.time()
temp_time = start_time
while True:
    end_time = time.time()
    # temperature read
    # fetch temp every 20s
    if int(end_time - temp_time) >= 5:
        fetch_temperature()
        print('Temperature fetch time ', int(end_time-start_time))
        logging.info('Temperature fetch time ' + str(int(end_time-start_time)))
        temp_time = time.time()
