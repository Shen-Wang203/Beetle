import time
import math
import visa
import logging
from StaticVar import StaticVar


PM_ADDR = '12'
channel = 2
if channel == 1:
    querytext = 'READ1:POW?'
else:
    querytext = 'READ2:POW?'
# POWER = str(0)
rm = visa.ResourceManager()
PM = rm.open_resource('GPIB0::'+PM_ADDR+'::INSTR')

# PW_ref = float(PM.query('sens1:pow:ref? toref'))
# print(PW_ref)
file1 = open("refs.txt","r")
StaticVar.PW_ref = float(file1.read())
file1.close()

def power_read():
    # Read unit is in dBm
    powerRead1 = float(PM.query(querytext))
    time.sleep(0.02)
    powerRead2 = float(PM.query(querytext))
    powerRead = (powerRead1 + powerRead2) * 0.5
    if powerRead > 10:
        if abs(powerRead1 - powerRead2) > 100:
            powerRead = float(PM.query(querytext))
        else:
            powerRead = -90.0
    # Minuse reference to get dB
    powerRead = powerRead - StaticVar.PW_ref
    powerRead = round(powerRead, 4)
    print(powerRead)
    logging.info(powerRead)
    StaticVar.IL = round(powerRead, 3)
    return powerRead

def power_read_noprint():
    # read unit is in dBm
    powerRead1 = float(PM.query(querytext))
    time.sleep(0.02)
    powerRead2 = float(PM.query(querytext))
    powerRead = (powerRead1 + powerRead2) * 0.5
    if powerRead > 10:
        if abs(powerRead1 - powerRead2) > 100:
            powerRead = float(PM.query(querytext))
        else:
            powerRead = -90.0
    # Change to dB
    powerRead = powerRead - StaticVar.PW_ref
    StaticVar.IL = round(powerRead, 3)

def power_read_dBm():
    # read unit is in dBm
    powerRead1 = float(PM.query(querytext))
    time.sleep(0.02)
    powerRead2 = float(PM.query(querytext))
    powerRead = (powerRead1 + powerRead2) * 0.5
    if powerRead > 0:
        if abs(powerRead1 - powerRead2) > 100:
            powerRead = float(PM.query(querytext))
        else:
            powerRead = -90.0
    return powerRead