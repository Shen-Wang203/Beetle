import time
import logging
import XYscan

class Curing_Active_Alignment(XYscan.XYscan):
    def __init__(self, HPPModel, hppcontrol):
        super().__init__(HPPModel, hppcontrol)  
        self.tolerance = 2 
        self.scanmode = 's'

        self.minutes = 7
        self.step_Z = 0.001
        self.loss_curing_rec = []
        self.pos_curing_rec = []

    # Product 1: VOA
    # Product 2: 1xN
    # Overwrite function, step_z is determined by products
    def product_select(self, _product):
        if _product == 'VOA':
            self.product = 1
            self.step_Z = 0.0005
        elif _product == '1xN':
            self.product = 2
            self.step_Z = 0.001

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
        self.loss = []
        self.wait_time = 0.3
        
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
            while max(self.loss) < self.loss_criteria and not self.error_flag:
                P = self.Zstep(P)
                P = self.scanUpdate(P, self.scanmode)
        
        print('Pre-Curing done. Loss criteria ', self.loss_criteria)
        logging.info('Pre-Curing done. Loss criteria ' + str(self.loss_criteria))
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
        self.wait_time = 0.3
        start_time = time.time()
        curing_active = True
        curing_active_flag = False
        while not self.error_flag:         
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
                        print('XY Values dont change')
                        logging.info('XY Values dont change')
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
        _direc1 = -1
        _direc0 = 1
        _z0 = P1[2]
        while True:
            P1[2] = P1[2] + self.step_Z * _direc1
            
            if P1[2] > _z0:
                _direc1 = 1
            else:
                _direc1 = -1
            if _direc1 != _direc0:
                P1[2] = P1[2] + 0.0002 * _direc1
            _z0 = P1[2]
            _direc0 = _direc1
            self.hppcontrol.engage_motor()
            if self.send_to_hpp(P1):
                self.hppcontrol.disengage_motor()
                time.sleep(0.3)
                self.fetch_loss()
                self.current_pos = P1[:]
                self.save_loss_pos()
            else:
                print('Movement Error')
                logging.info('Movement Error')
                self.error_flag = True                
            
            if self.product == 2:
                bound = self.loss_bound_zstep(loss_o)
            elif self.product == 1:
                bound = self.loss_bound(loss_o)
            diff = self.loss[-1] - loss_o
            if diff <= -bound:
                # go back to the old position
                P1[2] = P1[2] - self.step_Z * _direc1
                trend -= 1
                if trend:
                    print('Over')
                    logging.info('Over')
                    break
                _direc1 = -_direc1
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
                    P1[2] = P1[2] - self.step_Z * _direc1 * 5 - 0.0002 * _direc1
                    print('Value doesnt change in Z')
                    logging.info('Value doesnt change in Z')
                    break

        if P1[2] > _z0:
            _direc1 = 1
        else:
            _direc1 = -1
        if _direc1 != _direc0:
            P1[2] = P1[2] + 0.0002 * _direc1
        _z0 = P1[2]
        _direc0 = _direc1        
        self.hppcontrol.engage_motor()   
        if not self.send_to_hpp(P1):
            print('Movement Error')
            logging.info('Movement Error')
            self.error_flag = True
        self.hppcontrol.disengage_motor()
        time.sleep(0.3)
        self.current_pos = P1[:]
        # if same_count >= 5:
        #     return False
        self.check_abnormal_loss(max(self.loss))
        return P1

    # Over-write function, disable loss_fail_improve
    def check_abnormal_loss(self, loss0):
        if loss0 > self.loss_current_max:
            self.loss_current_max = loss0
        elif (loss0 < (2.5 * self.loss_current_max) and loss0 < -10) or loss0 < -55:
            print('Unexpected High Loss, End Program')
            logging.info('Unexpected High Loss, End Program')
            # self.hppcontrol.engage_motor()
            self.hppcontrol.normal_traj_speed()
            # self.send_to_hpp(self.starting_point)
            self.hppcontrol.disengage_motor()
            self.error_flag = True

    def loss_bound_zstep(self, _loss_ref_z):
        x = abs(_loss_ref_z)
        if x < 0.5:
            bound_z = 0.03
        elif x < 1:
            bound_z = 0.05
        elif x < 2:
            bound_z = 0.08
        else:
            bound_z = 0.1
        return bound_z