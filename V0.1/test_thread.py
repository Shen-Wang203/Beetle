#from Pattern_Search import Pattern_Search
# from Gradient_Search import Gradient_Search
# import matplotlib.pyplot as plt
import PowerMeter as PM
# import numpy as np 
import time
# from XYscan import XYscan 
import HPP_Control as control
import threading

class Te():
    hppcontrol = control.HPP_Control()

    def fetch_loss(self):
        while not self.stop_thread:          
            # time.sleep(0.02)
            # print('PW')
            # print(PM.power_read())
            self.loss.append(PM.power_read())
            self.fetch_flag = True
        
    
    # e1 = threading.Event()
    fetch_flag = False
    stop_thread = False
    loss = []
    pos = []

    def speedtest(self):
        self.stop_thread = False
        fetch_l = threading.Thread(target=self.fetch_loss)
        fetch_l.start()
        for i in range(0,20):
            print('**')
            time.sleep(0.005)
        self.stop_thread = True


    def trun(self):
        xy = 'x'
        i = 0        
        # self.stop_thread = False
        fetch_l = threading.Thread(target=self.fetch_loss)
        fetch_l.setDaemon(True)
        fetch_l.start()
        # time.sleep(0.05)
        self.stop_thread = False
        # self.e1.clear()
        while True:
            # time.sleep(0.005)            
            if xy == 'x':
                var = 'f 0' + '\n'
            else:
                var = 'f 1' + '\n'
            # print(int(self.hppcontrol.T1_send_fast(var)))
            self.pos.append(int(self.hppcontrol.T1_send_fast(var)))

            i += 1
            # self.e1.wait()
            # self.e1.clear()
            while not self.fetch_flag:
                pass
            self.fetch_flag = False
            if i >= 20:  
                self.stop_thread = True             
                return
        

    def run(self):
        for i in range(0,5):
            self.trun()
            print('*******')

aa = Te()
print(PM.power_read())
print('****')
aa.run()
# aa.speedtest()
print(len(aa.loss))
print('!!!')
print(len(aa.pos))
