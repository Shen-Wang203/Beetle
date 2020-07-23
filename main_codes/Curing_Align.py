import time
import logging
import XYscan

class Curing_Active_Alignment(XYscan.XYscan):
    def __init__(self, HPPModel, hppcontrol):
        super().__init__(HPPModel, hppcontrol)  
        self.tolerance = 2 
        # self.scanmode = 'i'
        # this backlash is for xy only, not for z
        # unit is counts
        self.x_backlash = -1
        self.y_backlash = 0

        self.minutes = 20
        self.step_Z = 0.0008
        self.loss_curing_rec = []
        self.pos_curing_rec = []
        self.xycount = 0
        self.later_time_flag = False

    # Product 1: VOA
    # Product 2: 1xN
    # Overwrite function, step_z is determined by products
    def product_select(self, _product):
        if _product == 'VOA':
            self.product = 1
            self.step_Z = 0.0005
        elif _product == '1xN':
            self.product = 2
            self.step_Z = 0.0008

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
        self.current_pos = P[:]
        self.loss = []
        self.wait_time = 0.2
        
        # Alignment after glue
        self.fetch_loss()
        self.loss_current_max = self.loss[-1]
        # if loss is too low, exit the program
        if self.loss[-1] < -30:
            return False
        if self.loss[-1] <= self.loss_criteria:
            P = self.scanUpdate(P)
            self.final_adjust = True
            self.stepScanCounts = 4         
            while max(self.loss) < self.loss_criteria and not self.error_flag:
                P = self.Zstep(P)
                if self.loss_target_check(self.loss[-1]):
                    break
                P = self.scanUpdate(P)
        
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
        self.loss = []
        self.fetch_loss()
        self.loss_current_max = self.loss[-1]
        self.current_pos = P[:]

        self.final_adjust = True
        self.stepScanCounts = 4
        self.wait_time = 0.2
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
                    P1 = self.scanUpdate(P)
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

    # End: time reach or loss doesn't change
    # Loss_criteria at curing should be 0.5 smaller than alignment, while still 0.5 smaller than spec
    # This can help guarantee the final loss is within spec   
    def curing_run2(self, P0):
        print('Curing Active Alignment Starts')
        logging.info(' ')
        logging.info('++++++++++++++++++++++++++++++')
        logging.info('Curing Active Alignment Starts. Loss Critera ' + str(self.loss_criteria)) 
        logging.info('++++++++++++++++++++++++++++++')
        P = P0[:]
        # record append number 0 as an indicate to enter curing
        self.loss_rec.append(0)
        self.pos_rec.append(0)
        self.pos_curing_rec.append(P0)
        self.loss = []
        self.fetch_loss()
        self.loss_current_max = self.loss_criteria
        self.current_pos = P[:]

        self.final_adjust = True
        self.stepScanCounts = 6
        self.wait_time = 0.2
        start_time = time.time()
        curing_active = True
        curing_active_flag = False
        while not self.error_flag:         
            end_time = time.time()
            if (end_time - start_time) > self.minutes  * 60:
                logging.info('Reach Time Limit')
                print('Reach Time Limit')
                break             
            elif (end_time - start_time) > 300 and not self.later_time_flag:
                logging.info('Reach 5 min')
                print('Reach 5 min')
                self.later_time_flag = True
                self.wait_time = 0.4

            time.sleep(0.7)
            self.fetch_loss()    
            self.loss_curing_rec.append(self.loss[-1])   
            self.check_abnormal_loss(self.loss[-1]) 

            if curing_active and self.loss[-1] < self.loss_criteria:
                # as an indicate that we are adjusting the fixture
                self.loss_curing_rec.append(99)    
                # Z back if xy search failed for 3 times
                if self.xycount == 3:
                    P = self.Zstep(P)
                    # P = self.Zstep_back(P)
                    self.pos_curing_rec.append(P)  
                    self.xycount = 0
                    self.fetch_loss()
                    if self.loss_target_check(self.loss[-1]):
                        continue

                P1 = self.scanUpdate(P)
                if P1 == False:
                    print('XY Values dont change')
                    logging.info('XY Values dont change')
                    print('Pause program')
                    logging.info('Pause program')
                    curing_active = False
                    if curing_active_flag:
                        return P
                    self.error_flag = False
                else:
                    P = P1[:]         
                self.pos_curing_rec.append(P)    
                self.xycount += 1
            elif curing_active and self.loss[-1] >= self.loss_criteria:
                self.xycount = 0
            elif (not curing_active) and self.loss[-1] < (self.loss_criteria - 0.5):
                curing_active = True
                curing_active_flag = True
                self.xycount = 0
                print('Loss is high, trying again')
                logging.info('Loss is high, trying again')

        end_time = time.time()
        print('End curing program, total time: ', round(end_time-start_time,1), ' s')
        logging.info('End curing program, total time: ' + str(round(end_time-start_time,1)) + ' s')
        
        
    def Zstep_back(self, P0):
        print('Z Back 0.8um')
        logging.info('Z Back 0.8um')         
        P1 = P0[:]
        P1[2] = P1[2] - 0.0008
        self.hppcontrol.engage_motor()
        if self.send_to_hpp(P1):
            self.hppcontrol.disengage_motor()
            time.sleep(0.2)
            self.current_pos = P1[:]
        else:
            print('Movement Error')
            logging.info('Movement Error')
            self.error_flag = True         
        return P1

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
                time.sleep(0.2)
                self.fetch_loss()
                self.current_pos = P1[:]
                self.save_loss_pos()
            else:
                print('Movement Error')
                logging.info('Movement Error')
                self.error_flag = True                
            if self.loss_target_check(self.loss[-1]):
                return P1


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
        time.sleep(0.2)
        self.current_pos = P1[:]
        # if same_count >= 5:
        #     return False
        self.check_abnormal_loss(max(self.loss))
        return P1

    # Over-write function, disable loss_fail_improve
    def check_abnormal_loss(self, _loss0):
        if _loss0 > self.loss_current_max:
            self.loss_current_max = _loss0
            self.pos_current_max = self.current_pos[:]
            self.loss_criteria = self.loss_current_max - 0.03
        elif (_loss0 < (2.5 * self.loss_current_max) and _loss0 < -10) or _loss0 < -55:
            print('Unexpected High Loss, End Program')
            logging.info('Unexpected High Loss, End Program')
            # self.hppcontrol.engage_motor()
            self.hppcontrol.normal_traj_speed()
            # self.send_to_hpp(self.starting_point)
            self.hppcontrol.disengage_motor()
            self.error_flag = True
    
    # Need to over-write this function because we need to search in y first
    # Return P1 after XY scan starting from P0, fixture is at P1, the loss is not updated
    # Need fixture to be at P0 location in the begining, fixture will be at P1 in the end.
    def scanUpdate(self, P0):
        print('Scan update starts at: ')
        print(P0)
        logging.info('Scan update starts at: ')
        logging.info(P0)
        P1 = P0[:]
        self.current_pos = P0[:]
        Tmm = self.HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
        Tcounts = self.hppcontrol.translate_to_counts(Tmm) 

        # if not self.Ystep(Tcounts[1], Tcounts[3], Tcounts[5], travelmode='p'):
        if not self.Yinterp(Tcounts[1], Tcounts[3], Tcounts[5]):
            print('Y step failed')
            logging.info('Y step failed')
            self.error_flag = True
            return False              
        P1 = self.current_pos[:]
        # previous search can errect the flag
        if self.loss_target_check(max(self.loss)) or self.error_flag:
            return P1  
        
        # if not self.Xstep(Tcounts[0], Tcounts[2], Tcounts[4], travelmode='p')]:
        if not self.Xinterp(Tcounts[0], Tcounts[2], Tcounts[4]):
            print('X step failed')
            logging.info('X step failed')
            self.error_flag = True
            return False               
        P1 = self.current_pos[:]
        if self.loss_target_check(max(self.loss)):
            return P1
        if not self.error_flag:
            print('Scan update ends at: ')
            print(P1)
            logging.info('Scan update ends at: ')
            logging.info(P1)
        return P1

    # smaller step size
    def xyinterp_sample_step(self, loss):
        # (-4,-3]: range 52 counts, step is 13, total 5 points 
        # (-3,-2]: range 44 counts, step is 11, total 5 points
        # (-2,-1]: range 28 counts, step is 7, total 5 points
        # (-1,0]: range 20 counts, step is 5, total 5 points
        if loss <= -12:
            return [16, 5]
        elif loss <= -3:
            return [13, 5]
        elif loss <= -2:
            return [11, 5]
        elif loss <= -1:
            return [7, 5]
        else:
            # for final 5min, change to 3-point interp
            # step is 6, total 3 points, range 12 counts
            if self.later_time_flag:
                return [6, 3]
            else:
                return [5, 5]
    
    def loss_target_check(self, _loss):
        if _loss >= self.loss_criteria:
            print('Meet Criteria: ', round(self.loss_criteria,3))
            logging.info('Meet Criteria: ' + str(round(self.loss_criteria,3)))
            self.xycount = 0
            return True