import time
import logging
import XYscan

class Curing_Active_Alignment(XYscan.XYscan):
    def __init__(self, HPPModel, hppcontrol):
        super().__init__(HPPModel, hppcontrol)  
        self.tolerance = 2 
        self.scanmode = 's'

        self.minutes = 7
        self.step_Z = 0.0005
        self.z_dir = -1
        self.loss_curing_rec = []
        self.pos_curing_rec = []

    def pre_curing_run(self, P0):   
        print('Pre-Curing Active Alignment Starts')
        logging.info(' ')
        logging.info('++++++++++++++++++++++++++++++')
        logging.info('Pre-Curing Active Alignment Starts')   
        logging.info('++++++++++++++++++++++++++++++') 
        P = P0[:]
        # record append number 0 as an indicate to enter curing
        self.loss_rec.append(0)
        self.pos_rec.append(0)
        self.pos_curing_rec.append(P0)
        
        # Alignment after glue
        self.fetch_loss()
        self.loss_current_max = self.loss[-1]
        # if loss is too low, exit the program
        if self.loss[-1] < -30:
            return False
        if self.loss[-1] <= self.loss_criteria:
            P = self.scanUpdate(P, self.scanmode)
            self.final_adjust = True
            self.stepScanCounts = 4         
            while max(self.loss) < self.loss_criteria:
                P = self.Zstep(P)
                P = self.scanUpdate(P, self.scanmode)
        
        return P
                   
    # End: time reach or loss doesn't change
    # Loss_criteria at curing should be 0.5 smaller than alignment, while still 0.5 smaller than spec
    # This can help guarantee the final loss is within spec   
    def curing_run(self, P0):
        print('Curing Active Alignment Starts')
        logging.info(' ')
        logging.info('++++++++++++++++++++++++++++++')
        logging.info('Curing Active Alignment Starts') 
        logging.info('++++++++++++++++++++++++++++++')
        P = P0[:]
        # record append number 0 as an indicate to enter curing
        self.loss_rec.append(0)
        self.pos_rec.append(0)
        self.pos_curing_rec.append(P0)
        self.fetch_loss()
        self.loss_current_max = self.loss[-1]


        self.final_adjust = True
        self.stepScanCounts = 4
        start_time = time.time()
        curing_active = True
        curing_active_flag = False
        while True:         
            end_time = time.time()
            if (end_time - start_time) > self.minutes  * 60:
                logging.info('Reach Time Limit')
                print('Reach Time Limit')
                break             
                       
            time.sleep(0.5)
            self.fetch_loss()    
            self.loss_curing_rec.append(self.loss[-1])   

            if curing_active and self.loss[-1] < self.loss_criteria:
                # as an indicate that we are adjusting the fixture
                self.loss_curing_rec.append(99)    
                # If fail, run the second time, if fail again, exit   
                for i in range(0,2):
                    P1 = self.scanUpdate(P, self.scanmode)
                    if P1 == False:
                        print('XY Value doesnt change')
                        logging.info('XY Value doesnt change')
                        if i:
                            print('End program')
                            logging.info('End program')
                            curing_active = False
                            if curing_active_flag:
                                # import sys 
                                # sys.exit()
                                return P
                            else:
                                break
                    else:
                        P = P1[:]    
                        break     
                self.pos_curing_rec.append(P)        
                if curing_active and max(self.loss) < self.loss_criteria:
                    P = self.Zstep(P)
                    self.pos_curing_rec.append(P)                       
            elif (not curing_active) and self.loss[-1] < (self.loss_criteria - 0.5):
                    curing_active = True
                    curing_active_flag = True
                    print('Loss is high, trying again')
                    logging.info('Loss is high, trying again')
            


    def Zstep(self, P0):
        print('Start Zstep (pos then loss)')
        logging.info('Start Zstep (pos then loss)')  
        P1 = P0[:]      
        self.loss = []        
        self.pos = []
        logging.info(P0)
        self.fetch_loss()   
        self.save_loss_pos()
        loss_o = self.loss[-1]

        trend = 1
        same_count = 0
        self.z_dir = -1
        while True:
            P1[2] = P1[2] + self.step_Z * self.z_dir
            
            self.hppcontrol.engage_motor()
            if self.send_to_hpp(P1):
                self.hppcontrol.disengage_motor()
                time.sleep(0.2)
                self.fetch_loss()
                self.current_pos = P1[:]
                self.save_loss_pos()
            else:
                print('Movement Error')
                logging.info('Movement Error')
                self.error_flag = True                
            
            bound = self.loss_resolution(loss_o)
            diff = self.loss[-1] - loss_o
            if diff <= -bound:
                # go back to the old position with extra value
                P1[2] = P1[2] - self.step_Z * self.z_dir - 0.0002 * self.z_dir
                trend -= 1
                if trend:
                    print('Over')
                    logging.info('Over')
                    break
                self.z_dir = -self.z_dir
                loss_o = self.loss[-1]
                print('Change direction')
                logging.info('Change direction')
                same_count = 0
            elif diff >= bound:
                trend = 2
                loss_o = self.loss[-1]
                same_count = 0
            else:
                trend = 2
                same_count += 1
                if same_count >= 5:
                    P1[2] = P1[2] - self.step_Z * self.z_dir * 5 - 0.0002 * self.z_dir
                    print('Value doesnt change in Z')
                    logging.info('Value doesnt change in Z')
                    break
        
        self.hppcontrol.engage_motor()   
        if not self.send_to_hpp(P1):
            print('Movement Error')
            logging.info('Movement Error')
            self.error_flag = True
        self.hppcontrol.disengage_motor()
        time.sleep(0.2)
        self.current_pos = P1[:]
        # if same_count >= 5:
        #     return False
        return P1

    # Over-write function, disable loss_fail_improve
    def check_abnormal_loss(self, loss0):
        if loss0 > self.loss_current_max:
            self.loss_current_max = loss0
        elif (loss0 < (2.5 * self.loss_current_max) and loss0 < -10) or loss0 < -55:
            print('Unexpected High Loss, End Program')
            logging.info('Unexpected High Loss, End Program')
            self.hppcontrol.engage_motor()
            self.hppcontrol.normal_traj_speed()
            self.send_to_hpp(self.starting_point)
            self.hppcontrol.disengage_motor()
            import sys
            sys.exit()