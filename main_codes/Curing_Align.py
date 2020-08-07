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
        # backlash 2 when stepscancounts is 4
        self.x_backlash = 2
        self.y_backlash = 2
        self.x_solid = False
        self.y_solid = False

        self.minutes = 35
        self.step_Z = 0.001
        self.loss_curing_rec = []
        self.pos_curing_rec = []
        self.xycount = 0
        self.zcount = 0
        self.zcount_loop = 0
        self.later_time_flag = False
        self.epoxy_about_to_solid_flag = False
        self.xsearch_first= True
        self.mode = 'p'
        self.doublecheck_flag = False
        self.buffer = 0.03

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
        # self.hppcontrol.slow_traj_speed_2()
        # record append number 0 as an indicate to enter curing
        self.loss_rec.append(0)
        self.pos_rec.append(0)
        self.pos_curing_rec.append(P0)
        self.loss = []
        self.fetch_loss()
        self.loss_current_max = self.loss_criteria + 0.01
        self.current_pos = P[:]

        self.final_adjust = True
        self.stepScanCounts = 4
        self.doublecheck_flag = False
        # wait time only works during interp, if doublecheck is on, no need to wait or wait for a short time for powermeter to response
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
            elif (end_time - start_time) > 1800 and (end_time - start_time) < 1802:
                print('Reach 30 min')
                logging.info('Reach 30 min')
            elif (end_time - start_time) > 300 and not self.later_time_flag:
                # 3min to 120 degree; 7min to 240 degree. Later time is 10min, epoxy solid at about 12min
                # 3min to 120 degree; 6min to 210 degree, later time is 9min, epoxy solid at about 11-12min
                # 3min to 120 degree; 5min to 190 degree, later time is 6min, epoxy solid at about 8min
                # 3min to 120 degree; 8min to 190 degree, later time is 7min, epoxy solid at about 
                logging.info('Reach 5 min')
                print('Reach 5 min')
                self.later_time_flag = True
                # self.doublecheck_flag = True
                self.wait_time = 0.3
                # self.mode = 't'               
                # for late time, loose the loss criteria to reduce movement times
                # self.loss_criteria = self.loss_criteria - 0.01
                # self.loss_current_max = self.loss_criteria + 0.02
            elif (end_time - start_time) > 360 and (end_time - start_time) < 365:
                logging.info('Reach 6 min')
                print('Reach 6 min')
                self.step_Z = 0.0007
                # self.doublecheck_flag = False
    
            time.sleep(0.5)
            self.fetch_loss()    
            self.loss_curing_rec.append(self.loss[-1])   
            self.check_abnormal_loss(self.loss[-1]) 
            # if loss is within the buffer range for 50s, then we assume the epoxy is solid already
            if self.later_time_flag and len(self.loss) == 100 and curing_active:
                print('Loss is stable, pause the program')
                logging.info('Loss is stable, pause the program')
                curing_active = False
                if curing_active_flag:
                    return P

            if curing_active and self.loss[-1] < (self.loss_criteria - self.buffer):
                self.buffer = 0
                # as an indicate that we are adjusting the fixture
                self.loss_curing_rec.append(99)    
                # Z back if xy search failed for 2 times
                if self.xycount == 2:
                    if self.zcount_loop >= 2:
                        P = self.Zstep(P)
                        self.zcount_loop = 0
                    else:
                        P = self.Zstep_back(P)
                        self.zcount_loop += 1
                    self.pos_curing_rec.append(P)  
                    self.xycount = 0
                    self.zcount += 1
                    self.fetch_loss()
                    if self.loss_target_check(self.loss[-1]):
                        self.loss = []
                        continue
                
                self.xycount += 1
                P1 = self.scanUpdate2(P)
                if P1 == False:
                    print('X or Y Values dont change')
                    logging.info('X or Y Values dont change')
                    if self.x_solid and self.y_solid:
                        print('Pause program')
                        logging.info('Pause program')
                        curing_active = False
                        if curing_active_flag:
                            return P
                    self.error_flag = False
                else:
                    P = P1[:]         
                self.pos_curing_rec.append(P)    
                self.loss = []
                # if fail to meet criteria for 3 rounds, then we loose the criteria
                if self.zcount == 1 and not self.later_time_flag and self.xycount == 2:
                    self.loss_criteria = self.loss_criteria - 0.01
                    # self.loss_current_max = self.loss_criteria + 0.02
                    print('Lower criteria 0.01dB')
                    logging.info('Lower criteria 0.01dB')
                    self.zcount = 0
                    # allow one more xy after lower criteria
                    self.xycount = 1
                elif self.zcount == 1 and self.later_time_flag and self.xycount == 1:
                    self.loss_criteria = self.loss_criteria - 0.01
                    # self.loss_current_max = self.loss_criteria + 0.02
                    print('Lower criteria 0.01dB')
                    logging.info('Lower criteria 0.01dB')
                    self.zcount = 0 
                    self.xycount = 1                   
            elif curing_active and self.loss[-1] >= self.loss_criteria:
                self.xycount = 0
                self.zcount = 0
                self.zcount_loop = 0
                if self.later_time_flag:
                    self.buffer = 0.02
                else:
                    self.buffer = 0.03
                # powermeter error is about 0.002, need to cancel that
                self.loss_criteria = self.loss[-1] - 0.002
            elif (not curing_active) and self.loss[-1] < (self.loss_criteria - 0.5):
                curing_active = True
                curing_active_flag = True
                self.xycount = 0
                print('Loss is high, trying again')
                logging.info('Loss is high, trying again')

        end_time = time.time()
        self.hppcontrol.normal_traj_speed()
        print('End curing program, total time: ', round(end_time-start_time,1), ' s')
        logging.info('End curing program, total time: ' + str(round(end_time-start_time,1)) + ' s')
        
        
    def Zstep_back(self, P0):
        print('Z Back ', self.step_Z*1000, 'um')
        logging.info('Z Back ' + str(self.step_Z*1000) + 'um')         
        P1 = P0[:]
        P1[2] = P1[2] - self.step_Z
        # self.hppcontrol.engage_motor()
        if self.send_to_hpp(P1, doublecheck=True):
            # self.hppcontrol.disengage_motor()
            # doublecheck is true, no need to wait
            # time.sleep(0.2)
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
        _direc0 = -1
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
            # self.hppcontrol.engage_motor()
            if self.send_to_hpp(P1, doublecheck=True):
                # self.hppcontrol.disengage_motor()
                # if doublecheck is true, no need to wait
                # time.sleep(0.2)
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
        # self.hppcontrol.engage_motor()   
        if not self.send_to_hpp(P1, doublecheck=True):
            print('Movement Error')
            logging.info('Movement Error')
            self.error_flag = True
        # self.hppcontrol.disengage_motor()
        # time.sleep(0.2)
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
            self.loss_criteria = self.loss_current_max - 0.01
        elif (_loss0 < (2.5 * self.loss_current_max) and _loss0 < -10) or _loss0 < -55:
            print('Unexpected High Loss, End Program')
            logging.info('Unexpected High Loss, End Program')
            # self.hppcontrol.engage_motor()
            self.hppcontrol.normal_traj_speed()
            # self.send_to_hpp(self.starting_point, doublecheck=False)
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
        about_to_solid = False
        Tmm = self.HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
        Tcounts = self.hppcontrol.translate_to_counts(Tmm) 

        # Return false only when unchanged
        # if not self.Xstep(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=self.doublecheck_flag):
        if not self.x_solid:
            if not self.Xinterp(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=self.doublecheck_flag, mode=self.mode):
                print('X step unchange')
                logging.info('X step unchange')
                if self.later_time_flag:
                    self.error_flag = True
                    self.x_solid = True
                    return False               
        P1 = self.current_pos[:]
        # previous search can errect the flag
        if not self.x_solid and (self.loss_target_check(max(self.loss)) or self.error_flag):
            return P1  
        # Epoxy is about to be solid
        if (max(self.loss) - min(self.loss)) < 0.05 and not self.epoxy_about_to_solid_flag:
            about_to_solid = True

        # Return false only when unchanged
        # if not self.Ystep(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=self.doublecheck_flag):
        if not self.y_solid:
            if not self.Yinterp(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=self.doublecheck_flag, mode=self.mode):
                print('Y step unchange')
                logging.info('Y step unchange')
                if self.later_time_flag:
                    self.error_flag = True
                    self.y_solid = True
                    return False         
        P1 = self.current_pos[:]        
        if not self.y_solid and self.loss_target_check(max(self.loss)):
            return P1
        # Epoxy is about to be solid
        if (max(self.loss) - min(self.loss)) < 0.05 and not self.epoxy_about_to_solid_flag and about_to_solid:
            print('Epoxy is about to be solid')
            logging.info('Epoxy is about to be solid')
            self.epoxy_about_to_solid_flag = True
            self.wait_time = 0.1
            # self.tolerance = 1
            # self.doublecheck_flag = True

        if not self.error_flag:
            print('Scan update ends at: ')
            print(P1)
            logging.info('Scan update ends at: ')
            logging.info(P1)
        return P1

    # Need to over-write this function because we need to search in y first
    # Return P1 after XY scan starting from P0, fixture is at P1, the loss is not updated
    # Need fixture to be at P0 location in the begining, fixture will be at P1 in the end.
    def scanUpdate2(self, P0):
        print('Scan update starts at: ')
        print(P0)
        logging.info('Scan update starts at: ')
        logging.info(P0)
        P1 = P0[:]
        self.current_pos = P0[:]
        about_to_solid = False
        Tmm = self.HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
        Tcounts = self.hppcontrol.translate_to_counts(Tmm) 

        # Add search sequence option
        for i in range(0,2):
            if self.xsearch_first:
                # Return false only when unchanged
                if not self.x_solid and not self.Xstep(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=self.doublecheck_flag, mode=self.mode):
                # if not self.x_solid and not self.Xinterp(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=self.doublecheck_flag, mode=self.mode):
                    print('X step unchange')
                    logging.info('X step unchange')
                    if self.later_time_flag:
                        self.error_flag = True
                        self.x_solid = True
                        return False               
                P1 = self.current_pos[:]
                # previous search can errect the flag
                if not self.x_solid and (self.loss_target_check(max(self.loss)) or self.error_flag):
                    # if meet target on x, then x first
                    if not self.xsearch_first:
                        self.xsearch_first = True
                    return P1  
                self.xsearch_first = False
                continue
                
            # Return false only when unchanged
            if not self.y_solid and not self.Ystep(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=self.doublecheck_flag, mode=self.mode):
            # if not self.y_solid and not self.Yinterp(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=self.doublecheck_flag, mode=self.mode):
                print('Y step unchange')
                logging.info('Y step unchange')
                if self.later_time_flag:
                    self.error_flag = True
                    self.y_solid = True
                    return False         
            P1 = self.current_pos[:]        
            if not self.y_solid and (self.loss_target_check(max(self.loss)) or self.error_flag):
                # Change x or y search priority based on which one has larger movements
                if self.xsearch_first:
                    self.xsearch_first = False
                return P1
            self.xsearch_first = True

        # Change x or y search priority based on which one has larger movements
        if abs(P1[0] - P0[0]) > (abs(P1[1] - P0[1])+0.0001) and not self.xsearch_first:
            self.xsearch_first = True
        elif (abs(P1[0] - P0[0])+0.0001) < abs(P1[1] - P0[1]) and self.xsearch_first:
            self.xsearch_first = False

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
            # if self.later_time_flag:
            #     return [6, 3]
            # else:
            #     return [5, 5]
            if self.later_time_flag:
                return [5, 3]
            elif self.epoxy_about_to_solid_flag:
                return [3, 3]
            else:
                # return [10, 3]
                return [7, 3]
    
    # loss bound based on loss value
    def loss_bound(self, _loss_ref):
        x = abs(_loss_ref)
        if x < 0.7:
            bound = 0.004
        elif x < 1.5:
            bound = 0.005
        elif x > 50:
            bound = 4
        else:
            # 50->2.2; 40->1.12; 30->0.54; 20->0.27; 15->0.2; 10->0.15; 8->0.12; 6->0.1; 4->0.064; 3->0.046; 2->0.027; 1-> 0.005
            bound = 0.00003*x**3 - 0.0011*x**2 + 0.0245*x - 0.018
            bound = bound * 0.8
        return bound

    def loss_target_check(self, _loss):
        if _loss >= self.loss_criteria:
            print('Meet Criteria: ', round(self.loss_criteria,4))
            logging.info('Meet Criteria: ' + str(round(self.loss_criteria,4)))
            self.xycount = 0
            self.zcount = 0
            self.zcount_loop = 0
            if self.later_time_flag:
                self.buffer = 0.02
            else:
                self.buffer = 0.03
            # powermeter error is about 0.002, need to cancel that
            self.loss_criteria = _loss - 0.002

            if _loss > self.loss_current_max:
                self.loss_current_max = _loss
                self.pos_current_max = self.current_pos[:]
                self.loss_criteria = self.loss_current_max - 0.01
            
            return True