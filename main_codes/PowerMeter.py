import time
import math
import visa
import logging
from StaticVar import StaticVar


PM_ADDR = str(12)
# POWER = str(0)
rm = visa.ResourceManager()
PM = rm.open_resource('GPIB0::'+PM_ADDR+'::INSTR')

def get_loss_simulate(Ipt):
    Rx = Ipt[3] - 1.06 
    Ry = Ipt[4] - 0.32
    Rz = Ipt[5]
    x = Ipt[0] + 0.101 - 1.2 * math.sin(math.radians(Ry)) * math.cos(math.radians(Rx))
    y = Ipt[1] + 0.4518 + 1.2 * math.sin(math.radians(Rx)) * math.cos(math.radians(Ry))
    z = Ipt[2] - 139.0434    

    # loss = -1.25 + math.exp(-4*(x**2+y**2+z**2+Rx**2+Ry**2+Rz**2)) + 0.5*math.exp(-((x**2+y**2+z**2+Rx**2+Ry**2+Rz**2)**0.5-1.5)**2)
    loss = -1.18 + math.exp(-4*(x**2+y**2+z**2+Rx**2+Ry**2+Rz**2))
    # time.sleep(0.02)
    return loss

def powermeter_init():
    time.sleep(0.5)
    print('PM wavelength: '+ PM.query('SENS:CHAN1:POW:WAV?'))
    time.sleep(0.2)
    print('PM receiving power: '+PM.query('READ:CHAN1:POW?'))

def power_read():
    powerRead = float(PM.query('READ1:POW?'))
    time.sleep(0.02)
    powerRead2 = float(PM.query('READ1:POW?'))
    powerRead = (powerRead + powerRead2) * 0.5
    while powerRead > 0:
        powerRead = float(PM.query('READ1:POW?'))
    print(powerRead)
    logging.info(powerRead)
    StaticVar.IL = round(powerRead, 3)
    return powerRead