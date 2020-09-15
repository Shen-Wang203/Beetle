import PowerMeter as PM
import time
import logging
import interpolation
import HPP_Control as control
import datetime

class XYscan:
    def __init__(self, HPPModel, hppcontrol):
        self.HPP = HPPModel
        self.hppcontrol = hppcontrol

        self.scan_radius = 3000  # 3000 counts, 3000*0.05um = 150um, +-150um
        self.starting_point = [0,0,138,0,0,0]
        self.error_flag = False
        self.limit_Z = 142
        self.tolerance = 5
        self.Z_amp = 4
        self.stepScanCounts = 10
        self.final_adjust = False
        self.larger_Z_flag = False    
        self.second_try = False   
        self.xystep_limit = False
        self.xystep_gobacktolast = True
        self.aggresive_threshold = -12
        self.scanmode_threshold = -4
        self.stepmode_threshold = -2
        self.interpmode_threshold = -2
        self.loss_criteria = -0.4
        self.scanmode = 'c'
        self.zmode = 'normal'
        # Defaul product is 1xN singlemode
        self.product = 2
        self.wait_time = 0.2
        # self.strategy can be:
        # stepping-at-final --> 1
        # interp-at-final  --> 2
        self.strategy = 1
        # self.loss and self.pos record each x or y or z search data, 
        # they will be cleared when a new search in x or y or z starts
        self.loss = []
        self.pos = []
        self.loss_rec = []
        self.pos_rec = []
        self.current_pos = [0,0,138,0,0,0]   
        self.pos_ref = [0,0,138,0,0,0]
        self.x_dir_trend = 1
        self.y_dir_trend = 1
        self.x_dir_old = 1
        self.y_dir_old = 1
        # this backlash is for xy only, not for z
        # unit is counts
        self.x_backlash = 0
        self.y_backlash = 0
        self.loss_current_max = -50.0
        self.pos_current_max = [0,0,138,0,0,0]
        self.loss_fail_improve = 0
        self.meet_crit = False
        # this experimental zstep count means how many times we want to
        # use experimental z stepping. If 0, then means don't use it
        self.experimental_zstep_count = 0
        self.experimental_Zstep_flag = False

    def set_loss_criteria(self, _loss_criteria):
        self.loss_criteria = _loss_criteria

    def set_scan_radius(self, _scan_radius):
        self.scan_radius = _scan_radius
    
    def set_starting_point(self, _starting_point):
        self.starting_point = _starting_point

    def set_limit_Z(self, _limit_Z):
        self.limit_Z = _limit_Z

    def set_Z_amp(self, _Z_amp):
        self.Z_amp = _Z_amp

    def set_angle_flag(self, _bool):
        self.angle_flag = _bool

    # Product 1: VOA
    # Product 2: 1xN
    def product_select(self, _product):
        if _product == 'VOA':
            self.product = 1
            self.interpmode_threshold = -2
            self.stepmode_threshold = -2            
            print('VOA has been selected')
            logging.info('VOA has been selected')
        elif _product == '1xN':
            self.product = 2
            print('SS 1xN has been selected')
            logging.info('SS 1xN has been selected')     
        elif _product == 'Multimode':
            self.product = 3      
            self.scanmode_threshold = -3  
            self.interpmode_threshold = -1.5   
            print('MM 1xN has been selected')
            logging.info('MM 1xN has been selected')         

    def autoRun(self):
        print('A New Alignment Starts')
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        logging.info('A New Alignment Starts, Criteria '+ str(self.loss_criteria)) 
        if self.product == 1:
            logging.info('Product: VOA')
        elif self.product == 2:
            logging.info('Product: SS 1xN')
        elif self.product == 3:
            logging.info('Product: MM 1xN')
        now = datetime.datetime.now()
        logging.info(now.strftime("%Y-%m-%d %H:%M:%S"))
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        start_time = time.time()
        self.send_to_hpp(self.starting_point, doublecheck=False)
        # time.sleep(2)
        self.hppcontrol.slow_traj_speed()
        P0 = self.starting_point[:]
        P1 = P0[:]
        # initials
        self.stepScanCounts = 10
        self.tolerance = 5
        self.scanmode = 'c'
        self.fetch_loss()
        self.loss_current_max = self.loss[-1]
        self.meet_crit = False
        self.error_flag = False
        while not self.error_flag:
            # Select mode and parameters as loss
            if self.mode_select(max(self.loss)):
                P_final = P0[:]
                break

            P1 = self.scanUpdate(P0, self.scanmode)
            if P1 == False and max(self.loss) > -10 and self.scanmode == 'c':
                self.scanmode = 's'
                print('XY continuesly scan failed, change to step scan')
                logging.info('XY continuesly scan failed, change to step scan')
                self.error_flag = False
                continue

            # check error_flag, check_abnormal_loss function can erect this flag
            if self.error_flag:
                P_final = self.pos_current_max[:]
                continue

            # Select mode and parameters as loss
            if self.mode_select(max(self.loss)):
                P_final = P1[:]
                break

            P0 = self.optimZ(P1, doublecheck=False)
                        
            # check error_flag, check_abnormal_loss function can erect this flag
            if self.error_flag:
                P_final = self.pos_current_max[:]

        self.hppcontrol.normal_traj_speed()
        if max(self.loss) > self.loss_current_max:
            self.loss_current_max = max(self.loss)
        print('Auto Alignment Finished, Best Loss: ', self.loss_current_max)
        logging.info('Auto Alignment Finished, Best Loss: ' + str(self.loss_current_max))
        end_time = time.time()
        print('Time costs: ', round(end_time-start_time, 1), ' s')
        logging.info('Time costs: ' + str(round(end_time-start_time,1)) + ' s')
        return P_final

    # return true if meet criteria, otherwise return none
    def mode_select(self, loss0):
        # if <= -12, then continue scan mode, with aggressive zmode
        if loss0 <= self.aggresive_threshold:
            self.scanmode = 'c'
            self.Z_amp = 4
            self.zmode = 'aggressive'
            # self.final_adjust = False
            self.tolerance = 5
            self.wait_time = 0.1
        # if (-12,-4], still continue scan mode, with normal zmode
        elif loss0 <= self.scanmode_threshold:
            self.zmode = 'aggressive'
            self.scanmode = 'c'
            self.Z_amp = 3.0
            self.tolerance = 2
            self.wait_time = 0.1
            # self.final_adjust = False
        # if (-4,-2], and stepping-at-final self.strategy, then step mode
        elif loss0 <= self.stepmode_threshold and self.strategy == 1:  
            # self.scanmode = 's'
            self.scanmode = 'i'
            self.final_adjust = True
            self.tolerance = 2
            self.wait_time = 0.1
            self.stepScanCounts = 4            
            if self.product == 1:
                self.Z_amp = 1.5
                self.zmode = 'normal'
            elif self.product == 2:
                self.Z_amp = 3.0
                self.zmode = 'aggressive'
            elif self.product == 3:
                self.Z_amp = 3.5
                self.zmode = 'normal'
        # if (-4,-2], and interp-at-final self.strategy, then interp mode
        elif loss0 <= self.interpmode_threshold and self.strategy == 2: 
            self.scanmode = 'i'
            self.tolerance = 2
            self.wait_time = 0.1
            self.final_adjust = True
            if self.product == 1:
                self.Z_amp = 1.5
                self.zmode = 'normal'
            elif self.product == 2:
                self.Z_amp = 3.0
                self.zmode = 'aggressive'
            elif self.product == 3:
                self.Z_amp = 3.5
                self.zmode = 'normal'
            # self.final_adjust = False           
        # if (-2,criteria], and stepping-at-final self.strategy, then final adjust 
        elif loss0 <= self.loss_criteria and self.strategy == 1:
            # print('Change to Final_adjust')
            # logging.info('Change to Final_adjust')
            self.zmode = 'normal'
            self.scanmode = 's'
            self.final_adjust = True
            self.stepScanCounts = 4 
            self.tolerance = 2 
            self.wait_time = 0.2
            if self.product == 1:
                self.Z_amp = 1.2
            elif self.product == 2:
                self.Z_amp = 2.5
            elif self.product == 3:
                self.Z_amp = 2.5
        # if (-2,criteria], and interp-at-final self.strategy, then final adjust 
        elif loss0 <= self.loss_criteria and self.strategy == 2:
            # print('Change to Final_adjust')
            # logging.info('Change to Final_adjust')
            self.zmode = 'normal'
            self.scanmode = 'i'
            self.final_adjust = True
            self.tolerance = 2 
            self.wait_time = 0.2
            if self.product == 1:
                self.Z_amp = 1.2
            elif self.product == 2:
                self.Z_amp = 2.5
            elif self.product == 3:
                self.Z_amp = 2.5
        # if > criteria, then exit
        else:
            print('Better than criteria ', self.loss_criteria)
            logging.info('Better than criteria ' + str(self.loss_criteria))
            self.meet_crit = True
            return True
        
        return None


    # need to be T1x or T1y T2y T3y
    def update_current_pos(self, xy, current_count, ori_count):
        _current_pos = self.pos_ref[:]
        if xy == 'x':
            _current_pos[0] = _current_pos[0] + (current_count - ori_count) * 50e-6
        elif xy == 'y':
            _current_pos[1] = _current_pos[1] + (current_count - ori_count) * 50e-6            
        self.current_pos = _current_pos[:]

    # loss and pos save, pos is always current_pos, so update pos first
    def save_loss_pos(self):
        self.loss_rec.append(self.loss[-1])
        self.pos_rec.append(self.current_pos)

    # when success return true, position is updated in self.current_pos
    def Xscan(self, X1_counts, X2_counts, X3_counts):
        # _dir can only be +1 or -1. When -1 means scan from adding counts
        # Purpose of _dir is to follow last correct direction, instead of substract then add counts every time
        # T1x direction is opposite compare to T2x and T3x
        x1start = X1_counts - self.scan_radius * self.x_dir_trend
        x1end = X1_counts + self.scan_radius * self.x_dir_trend
        x2start = X2_counts + self.scan_radius * self.x_dir_trend
        x2end = X2_counts - self.scan_radius * self.x_dir_trend
        x3start = X3_counts + self.scan_radius * self.x_dir_trend
        x3end = X3_counts - self.scan_radius * self.x_dir_trend

        self.loss = []
        self.fetch_loss()
        loss0 = self.loss[-1]
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]
        pos0 = X1_counts
        if self.final_adjust:
            self.hppcontrol.engage_motor()
        # Use T1's position as reference
        self.hppcontrol.Tx_send_only(x1start, x2start, x3start, 't')
        for i in range(0,2):
            if self.active_monitor('x', loss0, pos0):
                index = self.loss.index(max(self.loss)) - 1
                x1_final = self.pos[index] 
                # x1_final = self.pos[index] * 0.75 + self.pos[index + 1] * 0.25
                x2_final = -x1_final + x1start + x2start
                x3_final = -x1_final + x1start + x3start
                self.hppcontrol.Tx_send_only(x1_final, x2_final, x3_final, 'p')
                # check on target, need to check all of them
                timeout = 0
                while not self.hppcontrol.Tx_on_target(x1_final, x2_final, x3_final, self.tolerance):
                    time.sleep(0.2)
                    timeout += 1
                    if timeout > 100:
                        print('Movement Timeout Error')
                        logging.info('Movement Timeout Error')
                        return False
                # if i = 0, x_dir = _dir; if i = 1, x_dir = -_dir
                self.x_dir_trend = self.x_dir_trend * (-2 * i + 1)
                self.update_current_pos('x', x1_final, X1_counts)
                self.check_abnormal_loss(max(self.loss))
                return True
            else:
                if i:
                    # if fail, the fixture needs to go back to the original position
                    self.hppcontrol.Tx_send_only(X1_counts, X2_counts, X3_counts, 'p')
                    timeout = 0
                    while not self.hppcontrol.Tx_on_target(X1_counts, X2_counts, X3_counts, self.tolerance):
                        time.sleep(0.2)
                        timeout += 1
                        if timeout > 100:
                            print('Movement Timeout Error')
                            logging.info('Movement Timeout Error')
                            return False
                    self.update_current_pos('x', X1_counts, X1_counts)
                    return False
                loss0 = self.loss[-1]
                pos0 = self.pos[-2]
                x1mid = pos0
                x2mid = -pos0 + X1_counts + X2_counts
                x3mid = -pos0 + X1_counts + X3_counts
                self.hppcontrol.Tx_send_only(x1mid, x2mid, x3mid, 'p')
                time.sleep(0.2)    
                self.update_current_pos('x', x1mid, X1_counts)        
                self.hppcontrol.Tx_send_only(x1end, x2end, x3end, 't')          

    # when success return true, position is updated in self.current_pos
    def Yscan(self, Y1_counts, Y2_counts, Y3_counts):
        # _dir can only be +1 or -1. When -1 means scan from adding counts
        # Purpose of _dir is to follow last correct direction, instead of substracting then adding counts every time
        y1start = Y1_counts - self.scan_radius * self.y_dir_trend
        y1end = Y1_counts + self.scan_radius * self.y_dir_trend
        y2start = Y2_counts - self.scan_radius * self.y_dir_trend
        y2end = Y2_counts + self.scan_radius * self.y_dir_trend
        y3start = Y3_counts - self.scan_radius * self.y_dir_trend
        y3end = Y3_counts + self.scan_radius * self.y_dir_trend

        self.loss = []
        self.fetch_loss()
        loss0 = self.loss[-1]
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]
        pos0 = Y1_counts
        if self.final_adjust:
            self.hppcontrol.engage_motor()
        # use T1's position as position reference
        self.hppcontrol.Ty_send_only(y1start, y2start, y3start,'t')       
        for i in range(0,2):
            if self.active_monitor('y', loss0, pos0):
                index = self.loss.index(max(self.loss)) - 1
                y1_final = self.pos[index]
                # y1_final = self.pos[index] * 0.75 + self.pos[index + 1] * 0.25
                y2_final = y1_final - y1start + y2start
                y3_final = y1_final - y1start + y3start
                self.hppcontrol.Ty_send_only(y1_final, y2_final, y3_final, 'p')
                # check on target, check all of them
                timeout = 0
                while not self.hppcontrol.Ty_on_target(y1_final, y2_final, y3_final, self.tolerance):
                    time.sleep(0.2)  
                    timeout += 1
                    if timeout > 100:
                        print('Movement Timeout Error')
                        logging.info('Movement Timeout Error')
                        return False
                # if i = 0, y_dir = _dir; if i = 1, y_dir = -_dir
                self.y_dir_trend = self.y_dir_trend * (-2 * i + 1)
                self.update_current_pos('y', y1_final, Y1_counts)
                self.check_abnormal_loss(max(self.loss))
                return True
            else:
                if i:
                    # if fail, go back to original position
                    self.hppcontrol.Ty_send_only(Y1_counts, Y2_counts, Y3_counts, 'p')
                    timeout = 0
                    while not self.hppcontrol.Ty_on_target(Y1_counts, Y2_counts, Y3_counts, self.tolerance):
                        time.sleep(0.2)     
                        timeout += 1
                        if timeout > 100:
                            print('Movement Timeout Error')
                            logging.info('Movement Timeout Error')
                            return False              
                    self.update_current_pos('y', Y1_counts, Y1_counts)
                    return False
                loss0 = self.loss[-1]
                pos0 = self.pos[-2]
                y1mid = pos0
                y2mid = pos0 - Y1_counts + Y2_counts
                y3mid = pos0 - Y1_counts + Y3_counts
                self.hppcontrol.Ty_send_only(y1mid, y2mid, y3mid, 'p')
                time.sleep(0.2)
                self.update_current_pos('y', y1mid, Y1_counts)
                self.hppcontrol.Ty_send_only(y1end, y2end, y3end, 't')               

    # x1_o is counts
    # when success return true, position is updated at self.current_pos
    # return false: 1. movement error (not in final_adjust); 2. loss doesn't change
    # mode is either 't' or 'p' for traj or step positioning mode, default is 'p'
    def Xstep(self, x1_o, x2_o, x3_o, doublecheck, mode='p'):
        print('Start Xstep (loss then pos)')
        logging.info('Start Xstep (loss then pos)')        
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(x1_o)    
        # print(x1_o)  
        # logging.info(x1_o)
        self.save_loss_pos()
        if self.loss_target_check(self.loss[-1]):
            return True
        self.pos_ref = self.current_pos[:]

        # reference counts for pos update
        x1 = x1_o
        x2 = x2_o
        x3 = x3_o
        # old pos for backlash counter
        x10 = x1      
        loss_o = self.loss[-1]
        # After z, let's set the previous direc as 0
        self.x_dir_old = 0
        trend = 1
        same_count = 0
        totalstep = 0
        # print('Direction ', self.x_dir_trend)
        # logging.info('Direction ' + str(self.x_dir_trend))
        while True:
            totalstep += 1
            if self.xystep_limit and totalstep >= 4:
                print('Reach step search limit')
                logging.info('Reach step search limit')
                return True 
            # x2 and x3 are in opposite direction as x1
            x1 = x1 - self.stepScanCounts * self.x_dir_trend
            x2 = x2 + self.stepScanCounts * self.x_dir_trend
            x3 = x3 + self.stepScanCounts * self.x_dir_trend
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(x10, x1, 'x')
            x1 = x1 + counter
            x2 = x2 - counter
            x3 = x3 - counter
            x10 = x1

            if not self.gotoxy(x1, x2, x3, xy='x', doublecheck=doublecheck, mode=mode):
                return False
            # It's important to delay some time after disengaging motor
            # to let the motor fully stopped, then fetch the loss.
            time.sleep(self.wait_time)
            self.update_current_pos('x', x1, x1_o)
            self.fetch_loss()
            self.pos.append(x1)
            # print(x1)  
            # logging.info(x1)
            self.save_loss_pos()
            if self.loss_target_check(self.loss[-1]):
                return True

            if self.product == 1 or self.product == 2:
                bound = self.loss_bound(loss_o)
            elif self.product == 3:
                bound = self.loss_bound_small(loss_o)
            diff = self.loss[-1] - loss_o
            # if descrease, change direction, go back to the old point
            # if increase or the same, continue
            if diff <= -bound:
                # Sometimes during curing, going back will make the loss worse because the mim loss position
                # is drifting along the forwarding direction
                if not self.xystep_gobacktolast and totalstep >= 2:
                    print('Exit without going back')
                    logging.info('Exit without going back')
                    return True
                # go back to the old point
                x1 = x1 + self.stepScanCounts * self.x_dir_trend
                x2 = x2 - self.stepScanCounts * self.x_dir_trend
                x3 = x3 - self.stepScanCounts * self.x_dir_trend
                trend -= 1
                # if trend != 0, then exit
                if trend:
                    print('Over')
                    logging.info('Over')
                    totalstep -= 1
                    break
                self.x_dir_trend = -self.x_dir_trend    
                loss_o = self.loss[-1]    
                print('Change direction')
                logging.info('Change direction')     
                same_count = 0   
                totalstep = 0
            elif diff >= bound:
                trend = 2
                loss_o = self.loss[-1]
                same_count = 0
            else:
                trend = 2
                same_count += 1
                if same_count >= 2:
                    # don't go back at this moment
                    if not self.xystep_gobacktolast:
                        logging.info('Same loss exit without going back')
                        return True
                    x1 = x1 + self.stepScanCounts * self.x_dir_trend * 2
                    x2 = x2 - self.stepScanCounts * self.x_dir_trend * 2
                    x3 = x3 - self.stepScanCounts * self.x_dir_trend * 2
                    logging.info('Same loss exit') 
                    break
        
        # apply backlash counter
        counter = self.apply_xy_backlash_counter(x10, x1, 'x')
        x1 = x1 + counter
        x2 = x2 - counter
        x3 = x3 - counter
        x10 = x1
        if not self.gotoxy(x1, x2, x3, xy='x', doublecheck=doublecheck, mode=mode):
            return False
        time.sleep(self.wait_time)
        self.update_current_pos('x', x1, x1_o)
        self.fetch_loss()
        self.pos.append(x1)
        self.save_loss_pos()
        self.check_abnormal_loss(max(self.loss))
        # unchange
        if max(self.loss) - min(self.loss) < 0.002:
            return False
        if self.loss[-1] < max(self.loss) - 0.04:
            print('X step not best')
            logging.info('X step not best')       
        return True

    # y1_o is counts
    # when success return true, position is updated at self.current_pos
    # return false: 1. movement error (not in final_adjust); 2. loss doesn't change
    # mode is either 't' or 'p' for traj or step positioning mode, default is 'p'
    def Ystep(self, y1_o, y2_o, y3_o, doublecheck, mode='p'):
        print('Start Ystep (loss then pos)')
        logging.info('Start Ystep (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(y1_o)    
        # print(y1_o)  
        # logging.info(y1_o)  
        self.save_loss_pos()
        if self.loss_target_check(self.loss[-1]):
            return True
        self.pos_ref = self.current_pos[:]

        # reference counts for pos update
        y1 = y1_o
        y2 = y2_o
        y3 = y3_o
        # old pos for backlash counter
        y10 = y1         
        loss_o = self.loss[-1]
        # After z, let's set the previous direc as 0
        self.y_dir_old = 0        
        trend = 1
        same_count = 0
        totalstep = 0
        # print('Direction ', self.y_dir_trend)
        # logging.info('Direction ' + str(self.y_dir_trend))
        while True:
            totalstep += 1
            if self.xystep_limit and totalstep >= 4:
                print('Reach step search limit')
                logging.info('Reach step search limit')
                return True 
            y1 = y1 - self.stepScanCounts * self.y_dir_trend
            y2 = y2 - self.stepScanCounts * self.y_dir_trend
            y3 = y3 - self.stepScanCounts * self.y_dir_trend
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(y10, y1, 'y')
            y1 = y1 + counter
            y2 = y2 + counter
            y3 = y3 + counter
            y10 = y1

            if not self.gotoxy(y1, y2, y3, xy='y', doublecheck=doublecheck, mode=mode):
                return False
            time.sleep(self.wait_time)
            self.update_current_pos('y', y1, y1_o)
            self.fetch_loss()
            self.pos.append(y1)
            # print(y1)  
            # logging.info(y1)
            self.save_loss_pos()
            if self.loss_target_check(self.loss[-1]):
                return True
            
            if self.product == 1 or self.product == 2:
                bound = self.loss_bound(loss_o)
            elif self.product == 3:
                bound = self.loss_bound_small(loss_o)
            diff = self.loss[-1] - loss_o
            # if descrease, change direction, go back to the old point
            # if increase or the same, continue
            if diff <= -bound:
                # Sometimes during curing, going back will make the loss worse because the mim loss position
                # is drifting along the forwarding direction
                if not self.xystep_gobacktolast and totalstep >= 2:
                    print('Exit without going back')
                    logging.info('Exit without going back')
                    return True              
                # go back to the previous point
                y1 = y1 + self.stepScanCounts * self.y_dir_trend
                y2 = y2 + self.stepScanCounts * self.y_dir_trend
                y3 = y3 + self.stepScanCounts * self.y_dir_trend
                trend -= 1
                # if trend != 0, exit
                if trend:
                    print('Over')
                    logging.info('Over')
                    totalstep -= 1
                    break
                self.y_dir_trend = -self.y_dir_trend    
                loss_o = self.loss[-1]   
                print('Change direction')
                logging.info('Change direction') 
                same_count = 0          
                totalstep = 0
            elif diff >= bound:
                loss_o = self.loss[-1]
                trend = 2
                same_count = 0
            else:
                trend = 2
                same_count += 1
                if same_count >= 2:
                    # don't go back at this moment
                    if not self.xystep_gobacktolast:
                        logging.info('Same loss exit without going back')
                        return True
                    y1 = y1 + self.stepScanCounts * self.y_dir_trend * 2
                    y2 = y2 + self.stepScanCounts * self.y_dir_trend * 2
                    y3 = y3 + self.stepScanCounts * self.y_dir_trend * 2
                    logging.info('Same loss exit') 
                    break              

        # apply backlash counter
        counter = self.apply_xy_backlash_counter(y10, y1, 'y')
        y1 = y1 + counter
        y2 = y2 + counter
        y3 = y3 + counter
        y10 = y1
        if not self.gotoxy(y1, y2, y3, xy='y', doublecheck=doublecheck, mode=mode):
            return False
        time.sleep(self.wait_time)
        self.update_current_pos('y', y1, y1_o)
        self.fetch_loss()
        self.pos.append(y1)
        self.save_loss_pos()
        self.check_abnormal_loss(max(self.loss))
        # unchange
        if max(self.loss) - min(self.loss) < 0.002:
            return False
        if self.loss[-1] < max(self.loss) - 0.04:
            print('Y step not best')
            logging.info('Y step not best')
        return True

    # x1_o is counts, fixture needs to be at x1_o
    # when success return true, position is updated in self.current_pos
    # return false when: 1. loss doesn't change; 2. motor failed (not in final_adjust)
    # mode is either 't' or 'p' for traj or step positioning mode, default is 'p'
    def Xinterp(self, x1_o, x2_o, x3_o, doublecheck, mode='p'):
        print('Start Xinterp (loss then pos)')
        logging.info('Start Xinterp (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(x1_o)    
        # print(x1_o)  
        # logging.info(x1_o)  
        self.save_loss_pos()
        if self.loss_target_check(self.loss[-1]):
            return True
        self.pos_ref = self.current_pos[:]    
        # step in counts   
        [step, totalpoints] = self.xyinterp_sample_step(self.loss[-1])
        if self.product== 3:
            step = 3 * step
        if totalpoints == 7 and self.x_dir_trend == 1:
            x1 = [x1_o, x1_o-3*step, x1_o+step, x1_o-2*step, x1_o+2*step, x1_o-step, x1_o+3*step]
            x2 = [x2_o, x2_o+3*step, x2_o-step, x2_o+2*step, x2_o-2*step, x2_o+step, x2_o-3*step]
            x3 = [x3_o, x3_o+3*step, x3_o-step, x3_o+2*step, x3_o-2*step, x3_o+step, x3_o-3*step]
        elif totalpoints == 7 and self.x_dir_trend == -1:
            x1 = [x1_o, x1_o+3*step, x1_o-step, x1_o+2*step, x1_o-2*step, x1_o+step, x1_o-3*step]
            x2 = [x2_o, x2_o-3*step, x2_o+step, x2_o-2*step, x2_o+2*step, x2_o-step, x2_o+3*step]
            x3 = [x3_o, x3_o-3*step, x3_o+step, x3_o-2*step, x3_o+2*step, x3_o-step, x3_o+3*step]
        elif totalpoints == 5 and self.x_dir_trend == 1:
            x1 = [x1_o, x1_o-2*step, x1_o+step, x1_o-step, x1_o+2*step]
            x2 = [x2_o, x2_o+2*step, x2_o-step, x2_o+step, x2_o-2*step]
            x3 = [x3_o, x3_o+2*step, x3_o-step, x3_o+step, x3_o-2*step]  
        elif totalpoints == 5 and self.x_dir_trend == -1:
            x1 = [x1_o, x1_o+2*step, x1_o-step, x1_o+step, x1_o-2*step]
            x2 = [x2_o, x2_o-2*step, x2_o+step, x2_o-step, x2_o+2*step]
            x3 = [x3_o, x3_o-2*step, x3_o+step, x3_o-step, x3_o+2*step] 
        elif totalpoints == 3 and self.x_dir_trend == 1:
            x1 = [x1_o, x1_o-step, x1_o+step]
            x2 = [x2_o, x2_o+step, x2_o-step]
            x3 = [x3_o, x3_o+step, x3_o-step]  
        elif totalpoints == 3 and self.x_dir_trend == -1:
            x1 = [x1_o, x1_o+step, x1_o-step]
            x2 = [x2_o, x2_o-step, x2_o+step]
            x3 = [x3_o, x3_o-step, x3_o+step]                      

        # After z, let's set the previous direc as 0
        self.x_dir_old = 0
        x10 = x1_o
        # for i in range(1,totalpoints+1):
        i = 1
        x_ref = [x1_o]
        while i < (totalpoints + 1):
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(x10, x1[i], 'x')
            x1[i] = x1[i] + counter
            x2[i] = x2[i] - counter
            x3[i] = x3[i] - counter
            x10 = x1[i]            
            if not self.gotoxy(x1[i], x2[i], x3[i], xy='x', doublecheck=doublecheck, mode=mode):
                return False
            time.sleep(self.wait_time)
            self.update_current_pos('x', x1[i], x1_o)
            self.fetch_loss()
            self.pos.append(x1[i])
            # print(x1[i])  
            # logging.info(x1[i])
            self.save_loss_pos()
            if self.loss_target_check(self.loss[-1]):
                # larger than start position, then plus steps first, dir_trend is -1
                if x1[i] > x1[0]:
                    self.x_dir_trend = -1
                elif x1[i] < x1[0]:
                    self.x_dir_trend = 1
                return True
            # if current loss is larger than start loss, meaning the direction is right, we dont'
            # need to go to the opposite direction, which is the next iteration
            # print(i)
            # logging.info(i)
            x_ref.append(x1[i])
            i += 1
            if self.loss[-1] > self.loss[0]:
                i += 1               
            if i == totalpoints or i == (totalpoints + 1):
                # max loss is at left edge, need to extend on the left for more steps
                if max(self.loss) == self.loss[1] and x_ref[-1] == x1[totalpoints-2]:
                    x1.append(x1[1] - 1 * step * self.x_dir_trend)
                    x2.append(x2[1] + 1 * step * self.x_dir_trend)
                    x3.append(x3[1] + 1 * step * self.x_dir_trend)
                # max loss is at right edge, need to extend on the right for 2 more steps
                # make sure the loss and position are matched
                elif max(self.loss) == self.loss[-1] and x_ref[-1] == x1[totalpoints-1]:
                    x1.append(x1[-1] + 1 * step * self.x_dir_trend)
                    x2.append(x2[-1] - 1 * step * self.x_dir_trend)
                    x3.append(x3[-1] - 1 * step * self.x_dir_trend)                    
                else:
                    break
                i = totalpoints
        
        # if unchange return false and return to original position
        if max(self.loss) - min(self.loss) < 0.002:
            print('Unchange, go back to previous position')
            logging.info('Unchange, go back to previous position')
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(x10, x1_o, 'x')
            x1_o = x1_o + counter
            x2_o = x2_o - counter
            x3_o = x3_o - counter
            x10 = x1_o         
            self.gotoxy(x1_o, x2_o, x3_o, xy='x', doublecheck=True, mode=mode)
            # time.sleep(self.wait_time)
            self.update_current_pos('x', x1_o, x1_o)
            self.pos.append(x1_o)
            self.save_loss_pos()
            return False
        grid = [*range(int(min(x_ref)), int(max(x_ref))+1, 1)]  
        s = interpolation.barycenteric_interp(x_ref, self.loss, grid)
        x1_final = grid[s.index(max(s))]
        x2_final = -x1_final + x1_o + x2_o
        x3_final = -x1_final + x1_o + x3_o
        # only if counts difference is larger than 1 then go to that counts
        if abs(x1_final - x_ref[-1]) > 1:
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(x10, x1_final, 'x')
            x1_final = x1_final + counter
            x2_final = x2_final - counter
            x3_final = x3_final - counter
            x10 = x1_final         
            # print('move')
            # logging.info('move')
            if not self.gotoxy(x1_final, x2_final, x3_final, xy='x', doublecheck=True, mode=mode):
                return False
            # no need to wait if doublecheck is true
            time.sleep(self.wait_time)
            self.update_current_pos('x', x1_final, x1_o)
            self.fetch_loss()
            self.pos.append(x1_final)
        print('XInterp final: ',x1_final)
        logging.info('XInterp final: ' + str(x1_final))
        # larger than start position, then plus steps first, dir_trend is -1
        if x1_final > x1_o:
            self.x_dir_trend = -1
        elif x1_final < x1_o:
            self.x_dir_trend = 1
        self.check_abnormal_loss(max(self.loss))
        # Final loss is not the max
        if self.loss[-1] < max(self.loss) - 0.04:
            print('X run not best')
            logging.info('X run not best')
        return True


    # y1_o is counts, fixture needs to be at y1_o
    # when success return true, position is updated in self.current_pos
    # return false when: 1. loss doesn't change; 2. motor failed (not in final_adjust)
    # mode is either 't' or 'p' for traj or step positioning mode, default is 'p'
    def Yinterp(self, y1_o, y2_o, y3_o, doublecheck, mode='p'):
        print('Start Yinterp (loss then pos)')
        logging.info('Start Yinterp (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(y1_o)    
        # print(y1_o)  
        # logging.info(y1_o)  
        self.save_loss_pos()
        if self.loss_target_check(self.loss[-1]):
            return True
        self.pos_ref = self.current_pos[:]    
        # step in counts   
        [step, totalpoints] = self.xyinterp_sample_step(self.loss[-1])
        if self.product== 3:
            step = 3 * step
        if totalpoints == 7 and self.y_dir_trend == 1:
            y1 = [y1_o, y1_o-3*step, y1_o+step, y1_o-2*step, y1_o+2*step, y1_o-step, y1_o+3*step]
            y2 = [y2_o, y2_o-3*step, y2_o+step, y2_o-2*step, y2_o+2*step, y2_o-step, y2_o+3*step]
            y3 = [y3_o, y3_o-3*step, y3_o+step, y3_o-2*step, y3_o+2*step, y3_o-step, y3_o+3*step]
        elif totalpoints == 7 and self.y_dir_trend == -1:
            y1 = [y1_o, y1_o+3*step, y1_o-step, y1_o+2*step, y1_o-2*step, y1_o+step, y1_o-3*step]
            y2 = [y2_o, y2_o+3*step, y2_o-step, y2_o+2*step, y2_o-2*step, y2_o+step, y2_o-3*step]
            y3 = [y3_o, y3_o+3*step, y3_o-step, y3_o+2*step, y3_o-2*step, y3_o+step, y3_o-3*step]
        elif totalpoints == 5 and self.y_dir_trend == 1:
            y1 = [y1_o, y1_o-2*step, y1_o+step, y1_o-step, y1_o+2*step]
            y2 = [y2_o, y2_o-2*step, y2_o+step, y2_o-step, y2_o+2*step]
            y3 = [y3_o, y3_o-2*step, y3_o+step, y3_o-step, y3_o+2*step]
        elif totalpoints == 5 and self.y_dir_trend == -1:
            y1 = [y1_o, y1_o+2*step, y1_o-step, y1_o+step, y1_o-2*step]
            y2 = [y2_o, y2_o+2*step, y2_o-step, y2_o+step, y2_o-2*step]
            y3 = [y3_o, y3_o+2*step, y3_o-step, y3_o+step, y3_o-2*step]
        elif totalpoints == 3 and self.y_dir_trend == 1:
            y1 = [y1_o, y1_o-step, y1_o+step]
            y2 = [y2_o, y2_o-step, y2_o+step]
            y3 = [y3_o, y3_o-step, y3_o+step]  
        elif totalpoints == 3 and self.y_dir_trend == -1:
            y1 = [y1_o, y1_o+step, y1_o-step]
            y2 = [y2_o, y2_o+step, y2_o-step]
            y3 = [y3_o, y3_o+step, y3_o-step]         

        # After z, let's set the previous direc as 0
        self.y_dir_old = 0
        y10 = y1_o        
        # for i in range(1, totalpoints+1):
        i = 1
        y_ref = [y1_o]
        while i < (totalpoints + 1):
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(y10, y1[i], 'y')
            y1[i] = y1[i] + counter
            y2[i] = y2[i] + counter
            y3[i] = y3[i] + counter
            y10 = y1[i]  
            # print(y1[i], y2[i], y3[i])
            # logging.info(str(y1[i])+','+str(y2[i])+','+str(y3[i]))
            if not self.gotoxy(y1[i], y2[i], y3[i], xy='y', doublecheck=doublecheck, mode=mode):
                return False
            time.sleep(self.wait_time)
            self.update_current_pos('y', y1[i], y1_o)
            self.fetch_loss()
            self.pos.append(y1[i])
            # print(y1[i])  
            # logging.info(y1[i])
            self.save_loss_pos()
            if self.loss_target_check(self.loss[-1]):
                # larger than start position, then plus steps first, dir_trend is -1
                if y1[i] > y1[0]:
                    self.y_dir_trend = -1
                elif y1[i] < y1[0]:
                    self.y_dir_trend = 1                
                return True
            # if current loss is larger than start loss, meaning the direction is right, we dont'
            # need to go to the opposite direction, which is the next iteration
            # print(i)
            # logging.info(i)
            y_ref.append(y1[i])
            i += 1
            if self.loss[-1] > self.loss[0]:
                i += 1            
            if i == totalpoints or i == (totalpoints + 1):
                # max loss is at left edge, need to extend on the left for more steps
                if max(self.loss) == self.loss[1] and y_ref[-1] == y1[totalpoints-2]:
                    y1.append(y1[1] - 1 * step * self.y_dir_trend)
                    y2.append(y2[1] - 1 * step * self.y_dir_trend)
                    y3.append(y3[1] - 1 * step * self.y_dir_trend)
                # max loss is at right edge, need to extend on the right for 2 more steps
                # make sure the loss and position are matched
                elif max(self.loss) == self.loss[-1] and y_ref[-1] == y1[totalpoints-1]:
                    y1.append(y1[-1] + 1 * step * self.y_dir_trend)
                    y2.append(y2[-1] + 1 * step * self.y_dir_trend)
                    y3.append(y3[-1] + 1 * step * self.y_dir_trend)      
                else:
                    break    
                i = totalpoints 

        # if unchange return false and return to original point
        if max(self.loss) - min(self.loss) < 0.002:
            print('Unchange, go back to previous position')
            logging.info('Unchange, go back to previous position')            
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(y10, y1_o, 'y')
            y1_o = y1_o + counter
            y2_o = y2_o + counter
            y3_o = y3_o + counter
            y10 = y1_o         
            self.gotoxy(y1_o, y2_o, y3_o, xy='y', doublecheck=True, mode=mode)
            # time.sleep(self.wait_time)
            self.update_current_pos('y', y1_o, y1_o)
            self.pos.append(y1_o)
            self.save_loss_pos()
            return False
        grid = [*range(int(min(y_ref)), int(max(y_ref))+1, 1)]  
        s = interpolation.barycenteric_interp(y_ref, self.loss, grid)
        y1_final = grid[s.index(max(s))]
        y2_final = y1_final - y1_o + y2_o
        y3_final = y1_final - y1_o + y3_o
        # only if counts difference is larger than 1 then go to that counts
        if abs(y1_final-y_ref[-1]) > 1:
            # apply backlash counter
            counter = self.apply_xy_backlash_counter(y10, y1_final, 'y')
            y1_final = y1_final + counter
            y2_final = y2_final + counter
            y3_final = y3_final + counter
            y10 = y1_final 
            # print('move')
            # logging.info('move')
            if not self.gotoxy(y1_final, y2_final, y3_final, xy='y', doublecheck=True, mode=mode):
                return False
            # no need to wait if doublecheck is true
            time.sleep(self.wait_time)     
            self.update_current_pos('y', y1_final, y1_o)
            self.fetch_loss()
            self.pos.append(y1_final)
        print('YInterp final: ',y1_final)
        logging.info('YInterp final: ' + str(y1_final))
        # larger than start position, then plus steps first, dir_trend is -1
        if y1_final > y1_o:
            self.y_dir_trend = -1
        elif y1_final < y1_o:
            self.y_dir_trend = 1
        self.check_abnormal_loss(max(self.loss)) 
        # Final loss is not the max
        if self.loss[-1] < max(self.loss) - 0.04:
            print('Y run not best')
            logging.info('Y run not best')               
        return True

    # a1,a2,a3 is the T1,T2,T3 target position
    # xy is either 'x' or 'y'
    # doublecheck is to when disengaged, check again the position, is a bool. 
    # return false when movement error (final_adjust is false)
    # mode is either 't' or 'p' for traj or step positioning mode, default is 'p'
    def gotoxy(self, a1, a2, a3, xy, doublecheck, mode):
        for i in range(0,3):
            if self.final_adjust:
                self.hppcontrol.engage_motor()       
            if xy == 'y': 
                # print('sending y', a1)
                # logging.info('sending y ' + str(a1))
                self.hppcontrol.Ty_send_only(a1, a2, a3, mode)
            else:
                self.hppcontrol.Tx_send_only(a1, a2, a3, mode)
            for timeout in range(0, 50):
                time.sleep(0.07)
                if xy == 'y':
                    if self.hppcontrol.Ty_on_target(a1, a2, a3, self.tolerance):
                        break
                else:
                    if self.hppcontrol.Tx_on_target(a1, a2, a3, self.tolerance):
                        break
            if timeout >= 49:
                print('Movement Timeout Error')
                logging.info('Movement Timeout Error')
                if not self.final_adjust:
                    return False
            if self.final_adjust:
                self.hppcontrol.disengage_motor()
                if doublecheck and xy == 'y':
                    time.sleep(0.1)
                    if self.hppcontrol.Ty_on_target(a1, a2, a3, self.tolerance):
                        return True
                    else:
                        continue
                elif doublecheck and xy == 'x':
                    time.sleep(0.1)
                    if self.hppcontrol.Tx_on_target(a1, a2, a3, self.tolerance):
                        return True
                    else:
                        continue
            return True
        return True
        

    # Based on loss to determine xy interpolation sample step size
    # return step size and total points
    def xyinterp_sample_step(self, loss):
        # (-12,-3]: range 60 counts, step is 20, total 5 points 
        # (-3,-2]: range 52 counts, step is 13, total 5 points
        # (-2,-1]: range 40 counts, step is 10, total 5 points
        # (-1,0]: range 24 counts, step is 6, total 5 points
        if loss <= -12:
            return [25, 5]
        elif loss <= -3:
            return [20, 5]
        elif loss <= -2:
            return [13, 5]
        elif loss <= -1:
            return [10, 5]
        else:
            return [6, 5]

    # Return P1 after XY scan starting from P0, fixture is at P1, the loss is not updated
    # mode can be 's' (step) or 'c' (continusly) or 'i' (interpolation)
    # Need fixture to be at P0 location in the begining, fixture will be at P1 in the end.
    # interpolation mode won't return false
    # return false when 1. scan mode, decrease in both direction;
    #                   2. step mode, loss doesn't change for several steps
    #                   3. interp mode, loss deosn't change for all the sampling points
    #                   4. Motor failed to move, fail on on_target check
    def scanUpdate(self, P0, _mode):
        print('Scan update starts at: ')
        print(P0)
        logging.info('Scan update starts at: ')
        logging.info(P0)
        P1 = P0[:]
        self.current_pos = P0[:]
        Tmm = self.HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
        Tcounts = self.hppcontrol.translate_to_counts(Tmm) 
        # logging.info('Start Tcounts: '+str(Tcounts))
        if _mode == 's':
            if not self.Xstep(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=self.final_adjust):
                print('X step failed')
                logging.info('X step failed')
                self.error_flag = True
                return False
        elif _mode == 'i':
            if not self.Xinterp(Tcounts[0], Tcounts[2], Tcounts[4], doublecheck=False):
                print('X interp failed')
                logging.info('X interp failed')
                self.error_flag = True
                return False 
        else:
            if not self.Xscan(Tcounts[0], Tcounts[2], Tcounts[4]):
                print('X scan failed')
                logging.info('X scan failed')
                self.error_flag = True
                return False                                     
        P1 = self.current_pos[:]
        # x search can errect the flag
        if self.error_flag or self.loss_target_check(max(self.loss)):
            return P1

        if _mode == 's':
            if not self.Ystep(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=self.final_adjust):
                print('Y step failed')
                logging.info('Y step failed')
                self.error_flag = True
                return False
        elif _mode == 'i':
            if not self.Yinterp(Tcounts[1], Tcounts[3], Tcounts[5], doublecheck=False):
                print('Y interp failed')
                logging.info('Y interp failed')
                self.error_flag = True
                return False 
        else:
            if not self.Yscan(Tcounts[1], Tcounts[3], Tcounts[5]):
                print('Y scan failed')
                logging.info('Y scan failed')
                self.error_flag = True
                return False 
        P1 = self.current_pos[:]                                 
        # if self.loss_target_check(max(self.loss)):
        #     return P1        
        if not self.error_flag:
            print('Scan update ends at: ')
            P1 = [round(num, 5) for num in P1]
            print(P1)
            logging.info('Scan update ends at: ')
            logging.info(P1)
            # logging.info('X change: '+str(xdelta)+'; '+'Y change: '+str(ydelta))
        return P1

    # loss bound based on loss value
    def loss_bound(self, _loss_ref):
        x = abs(_loss_ref)
        if x < 0.7:
            bound = 0.002
        elif x < 1.5:
            bound = 0.005
        elif x > 50:
            bound = 4
        else:
            # 50->2.2; 40->1.12; 30->0.54; 20->0.27; 15->0.2; 10->0.15; 8->0.12; 6->0.1; 4->0.064; 3->0.046; 2->0.027; 1-> 0.005
            bound = 0.00003*x**3 - 0.0011*x**2 + 0.0245*x - 0.018
            bound = bound * 0.8
        return bound

    def loss_bound_small(self, _loss_ref):
        x = abs(_loss_ref)
        if x < 0.7:
            bound = 0.0007
        elif x < 1.5:
            bound = 0.003
        elif x > 50:
            bound = 4
        else:
            # 50->2.2; 40->1.12; 30->0.54; 20->0.27; 15->0.2; 10->0.15; 8->0.12; 6->0.1; 4->0.064; 3->0.046; 2->0.027; 1-> 0.005
            bound = 0.00003*x**3 - 0.0011*x**2 + 0.0245*x - 0.018
            bound = bound * 0.5
        return bound

    def loss_bound_large(self, _loss_ref_z):
        x = abs(_loss_ref_z)
        if x < 0.5:
            bound_z = 0.05
        elif x < 0.7:
            # bound_z = 0.5 * x
            bound_z = 0.1
        elif x < 1.2:
            # bound_z = 0.35 * x
            bound_z = 0.3
        elif x < 2:
            bound_z = 0.3 * x 
        elif x < 4:
            bound_z = 0.3 * x
        elif x > 50:
            bound_z = 4
        else:
            # x = 40,   30,   20,   10,   8,    6,    4
            # y = 2.46, 1.84, 1.23, 0.61, 0.49, 0.37, 0.24
            bound_z = 0.06141469*x - 0.001513462
        return bound_z

    # Starting from P0, change only Z to go to P1, 
    # the fixture will be in P1 in the end, and the fixture needs to be in P0 in the beginning
    def optimZ(self, P0, doublecheck):
        print('Z optim starts at (pos then loss): ')
        P0 = [round(num, 5) for num in P0]
        print(P0)
        logging.info('Z optim starts at (pos then loss): ')
        logging.info(P0)
        P1 = P0[:]
        self.loss = []
        self.pos = []
        self.fetch_loss()
        self.pos.append(P1)
        self.save_loss_pos()
        success_num = 0
        loss_o = self.loss[-1]
        if self.experimental_zstep_count and self.product == 2 and loss_o < -2 and loss_o > -16:
            step = self.experimental_Zstep_SS1xN(loss_o)
            print('Experimental Z stepping')
            logging.info('Experimental Z stepping')
            self.experimental_Zstep_flag = True
            self.experimental_zstep_count -= 1
        else:
            self.experimental_Zstep_flag = False
            # Step size is related to loss, for example in -15.72 dB, step size is 15.7 um.
            step_ref = round(abs(self.loss[-1]), 1) * 0.001
            # give step size an amplifier
            step = step_ref * self.Z_amp
            if step < 0.0015 and (self.product == 1 or self.product == 3):
                step = 0.0015
            elif step < 0.002 and self.product == 2:
                step = 0.0025
        _direc0 = 1
        _direc1 = 1
        _z0 = P1[2]
        while True:
            P1[2] = P1[2] + step
            
            # current direction
            if P1[2] > _z0:
                _direc1 = 1
            else:
                _direc1 = -1
            # if direction changed, add extra counts
            if _direc1 != _direc0:
                P1[2] = P1[2] + 0.0002 * _direc1
            # update old position and old direction
            _z0 = P1[2]
            _direc0 = _direc1            
            # goto the position
            if self.final_adjust and not doublecheck:
                self.hppcontrol.engage_motor()
            if not self.send_to_hpp(P1, doublecheck=doublecheck):
                print('Movement Error')
                logging.info('Movement Error')
                if not self.final_adjust:
                    self.error_flag = True
            if self.final_adjust and not doublecheck:
                self.hppcontrol.disengage_motor()
            time.sleep(self.wait_time)
            self.fetch_loss()
            self.current_pos = P1[:]
            self.pos.append(P1[:])
            self.save_loss_pos()
            if self.loss_target_check(self.loss[-1]):
                return P1
            if self.experimental_Zstep_flag:
                break

            if self.product == 1:
                bound = self.loss_bound(loss_o)
            elif self.product == 2:
                bound = self.loss_bound_large(loss_o)
            elif self.product == 3:
                bound = self.loss_bound_small(loss_o)
            diff = self.loss[-1] - loss_o

            # aggressive mode: Z goes forward until loss is 1.5 times of the initial value
            # for instance, loss_o = -15, then until -22.5 dB we stop forwarding Z
            # The purpose is to forward Z more aggressively to faster the process
            # make sure the loss is smaller than -5 and larger than -40, so that larger Z stepping won't be problem
            # the max num of stepping is 6
            if self.zmode == 'aggressive' and min(self.loss) > -40:
                if diff > bound:
                    loss_o = self.loss[-1]
                # for VOA used to be 1.5 times
                if self.loss[-1] > 1.5 * loss_o and success_num < 5:
                    success_num += 1
                    continue            
            
            # if fail (smaller), difference should be smaller than -loss_bound
            if diff < -bound:            
                # if fail, go back to the old point
                P1[2] = P1[2] - step 
                # radio here should be smaller than 0.5 not 0,5, otherwise two steps will go back to the previous position
                step = 0.4 * step                    

                # for VOA, if step size is smaller than minimum resolution, exit
                if self.product == 1 and step < 0.0002:
                    print('Z step is too small')
                    logging.info('Z step is too small')
                    # make sure it will exit
                    success_num = 1
                    # return False   
                # for 1xN, is step size is smaller than 1 um, exit
                elif self.product == 2 and step < 0.0015:
                    # don't go back, we want at least 1um forwarding
                    P1[2] = P1[2] + step/0.4
                    break
                elif self.product == 3 and step < 0.001:
                    # don't go back, we want at least 1um forwarding
                    P1[2] = P1[2] + step/0.4
                    break
                                
                if success_num:
                    # go back to the previous points
                    # give extra value to counter backlash
                    # P1[2] = P1[2] - 0.0002
                    # current direction
                    if P1[2] > _z0:
                        _direc1 = 1
                    else:
                        _direc1 = -1
                    # if direction changed, add extra counts
                    if _direc1 != _direc0:
                        P1[2] = P1[2] + 0.0002 * _direc1
                    # update old position and old direction
                    _z0 = P1[2]
                    _direc0 = _direc1                    
                    # goto the position
                    if self.final_adjust and not doublecheck:
                        self.hppcontrol.engage_motor()
                    if not self.send_to_hpp(P1, doublecheck=doublecheck):
                        print('Movement Error')
                        logging.info('Movement Error')
                        if not self.final_adjust:
                            self.error_flag = True
                    if self.final_adjust and not doublecheck:
                        self.hppcontrol.disengage_motor()
                    time.sleep(self.wait_time)
                    self.current_pos = P1[:]
                    self.fetch_loss()
                    self.pos.append(P1[:])
                    self.save_loss_pos()
                    break
            # if larger than bound, then success and update loss old
            elif diff > bound:
                loss_o = self.loss[-1]
                success_num += 1          
            # if same, then success, but don't update loss old
            else:
                success_num += 1
                # if loss is about the same for 5 times, exit to avoid overrun
                if success_num == 5:
                    break
                # # for 1xN, if loss improved a lot, exit directly   
                # if diff > 0.12 and self.product == 2:
                #     break
                # for multimode if loss is the same, exit directly
                if self.product == 3 and diff > 0:
                    break

        print('Z optim ends at: ')
        P1 = [round(num, 5) for num in P1]
        print(P1)
        logging.info('Z optim ends at: ')  
        logging.info(P1)
        # set current_pos as max loss position temporarily 
        # in order to update the max loss position in check_abnormal_loss function
        self.current_pos = self.pos[self.loss.index(max(self.loss))][:]
        self.check_abnormal_loss(max(self.loss))
        # change current_pos to the correct one
        self.current_pos = P1[:]
        return P1

    # This function determines at each loss, what's the distance to the min loss position in Z
    # l: is the loss; z is the Z_current - Z_minLoss
    # the function returns the left Z distance given the current loss based on lots of previous experiments
    def experimental_Zstep_SS1xN(self, _loss):
        z1 = [-0.36856, -0.23616, -0.18416, -0.13621, -0.08083, -0.05103, -0.03809, -0.02429, -0.02077, -0.01426, -0.00769]
        l = [-16,-12,-10,-8,-5,-3,-2,-1,-0.8,-0.5,-0.3]
        s = interpolation.linear_interp(l, z1, [_loss])
        if _loss < -1:
            # SS 1x1
            # return -round(s[0], 3)-0.025
            # SS 1xN
            return -round(s[0], 3)-0.045
        else:
            # SS 1x1
            # return -round(s[0], 3)-0.015
            # SS 1xN
            return -round(s[0], 3)-0.035

    def check_abnormal_loss(self, loss0):
        if loss0 > self.loss_current_max + 0.005:
            self.loss_current_max = loss0
            self.pos_current_max = self.current_pos[:]
            self.loss_fail_improve = 0
        else:
            if (loss0 < (4 * self.loss_current_max) and loss0 < -10) or loss0 < -55:
                print('Unexpected High Loss, End Program: ', str(loss0))
                logging.info('Unexpected High Loss, End Program: ' + str(loss0))
                self.hppcontrol.engage_motor()
                self.hppcontrol.normal_traj_speed()
                self.send_to_hpp(self.starting_point, doublecheck=False)
                self.hppcontrol.disengage_motor()
                self.error_flag = True

            # x,y and z fail to improve 8 times continuesly, then reset the loss_criteria as current max
            # total 3 rounds of xyz search
            # this is to faster the process
            self.loss_fail_improve += 1
            if self.loss_fail_improve == 8:
                self.loss_fail_improve = 0
                print('Failed to find better loss after tries, go back to current best')
                logging.info('Failed to find better loss after tries, go back to current best')
                self.error_flag = True
                # self.hppcontrol.engage_motor()
                self.send_to_hpp(self.pos_current_max, doublecheck=True)
                # self.hppcontrol.disengage_motor()


    def fetch_loss(self):
        self.loss.append(PM.power_read())

    def loss_target_check(self, _loss):
        if _loss >= self.loss_criteria:
            print('Meet Criteria')
            logging.info('Meet Criteria')
            self.meet_crit = True
            return True

    def apply_xy_backlash_counter(self, oldpos, newpos, xy):
        # current direction
        if newpos > oldpos:
            _direc = 1
        else:
            _direc = -1
        if xy == 'x':
            # if direction changed, add extra counts
            if _direc != self.x_dir_old:
                _counter = self.x_backlash * _direc
            else:
                _counter = 0
            # update old direction
            self.x_dir_old = _direc
        else:
            # if direction changed, add extra counts
            if _direc != self.y_dir_old:
                _counter = self.y_backlash * _direc
            else:
                _counter = 0
            # update old direction
            self.y_dir_old = _direc            
        return _counter


    # Use T1's position as position reference
    def active_monitor(self, xy, loss0, pos0):
        print('Monitor start (loss then pos)')
        logging.info('Monitor start (loss then pos)')
        flag = False
        self.pos = []
        self.loss = []
        trend = 0
        unchange = 0
        self.loss.append(loss0)
        loss_o = loss0
        print(loss0)
        logging.info(loss0)
        self.pos.append(pos0)
        # print(pos0)    
        # logging.info(pos0)
        while not self.error_flag:
            self.fetch_loss()

            if xy == 'x':
                self.pos.append(self.hppcontrol.real_time_counts(1))
            else:
                self.pos.append(self.hppcontrol.real_time_counts(2)) 
            # print(self.pos[-1])  
            # logging.info(self.pos[-1])   
            self.update_current_pos(xy, self.pos[-1], pos0)

            self.save_loss_pos()
            
            loss_diff = self.loss[-1] - loss_o
            bound = self.loss_bound(loss_o)
            if loss_diff <= -bound:
                trend -= 1
                loss_o = self.loss[-1]
            elif loss_diff >= bound: 
                trend = 3
                loss_o = self.loss[-1]
                continue
            else:
                unchange += 1
            # print(trend)
            if trend <= -2: # decreasing
                print(xy + ' scan done: decreasing')  
                logging.info(str(xy) + ' scan done: decreasing')
                flag = False
                break
            if trend == 1: # has a max
                print(xy + ' scan done: has max')
                logging.info(str(xy) + ' scan done: has max')
                flag = True
                break   
            if unchange > 300:
                flag = False
                print('Loss unchanged')
                logging.info('Loss unchanged')
                break   
        return flag

    # takes about 0.168s
    # doublecheck will do second check after disengage the motors
    # if doublecheck is true, don't need engage and disengage before and after this function
    def send_to_hpp(self, R, doublecheck):   
        target_mm = R[:]
        target_mm = [round(num, 5) for num in target_mm]
        print(target_mm)
        logging.info(target_mm)
        # Read real time counts        
        Tmm = self.HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
        # target_counts = self.hppcontrol.run_to_Tmm(Tmm, self.tolerance)
        self.hppcontrol.run_to_Tmm(Tmm, self.tolerance, doublecheck)
        # print(target_counts)
        # real_counts = control.Tcounts_real
        error_log = control.error_log
        if error_log != '':
            # error_flag = True
            return False 
        # else:
            # error_flag = False        
        return True  
