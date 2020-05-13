import time
import logging
import XYscan

class Curing_Active_Alignment(XYscan.XYscan):
    def __init__(self):
        super().__init__()
        self.minutes = 3
        self.final_adjust = True
        self.stepScanCounts = 4   
        self.Z_amp = 1.2   
        self.tolerance = 2 
        self.scanmode = 's'

    def curing_run(self, P0):   
        print('Curing Active Alignment Start')
        logging.info('Curing Active Alignment Start')    
        start_time = time.time()

        while True:
            self.fetch_loss()            
            if self.loss[-1] >= self.loss_criteria:
                end_time = time.time()
                if (end_time - start_time) > self.minutes  * 60:
                    logging.info('Reach Time Limit')
                    print('Reach Time Limit')
                    break
                continue
            else:
                P1 = self.scanUpdate(P0, self.scanmode)
                # P2 = self.scanUpdate(P1, self.scanmode)                
    

    def Z_adjust(self, P0):
        pass