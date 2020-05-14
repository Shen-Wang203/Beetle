import time
import logging
import XYscan

class Curing_Active_Alignment(XYscan.XYscan):
    def __init__(self):
        super().__init__()
        self.final_adjust = True
        self.stepScanCounts = 4   
        self.Z_amp = 1.2   
        self.tolerance = 2 
        self.scanmode = 's'

        self.minutes = 3
        self.loss_curing_rec = []
        self.pos_curing_rec = []

    def curing_run(self, P0):   
        print('Curing Active Alignment Starts')
        logging.info('Curing Active Alignment Starts')    
        start_time = time.time()
        P = P0[:]
        # record append number 0 as an indicate to enter curing
        self.loss_rec.append(0)
        self.pos_rec.append(0)
        self.pos_curing_rec.append(P0)
        
        while True:
            self.fetch_loss()    
            self.loss_curing_rec.append(self.loss[-1])        
            if self.loss[-1] >= self.loss_criteria:
                end_time = time.time()
                if (end_time - start_time) > self.minutes  * 60:
                    logging.info('Reach Time Limit')
                    print('Reach Time Limit')
                    break
                continue
            else:         
                # as an indicate that we are adjusting the fixture
                self.loss_curing_rec.append(99)       
                P = self.scanUpdate(P, self.scanmode)[:]
                # P2 = self.scanUpdate(P1, self.scanmode)   
                self.pos_curing_rec.append(P)             
    

    def Z_adjust(self, P0):
        pass