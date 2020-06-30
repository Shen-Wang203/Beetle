import PowerMeter as PM
import time
import numpy as np
import logging
import interpolation
import HPP_Control as control

class XYscan:
    def __init__(self, HPPModel, hppcontrol):
        self.HPP = HPPModel
        self.hppcontrol = hppcontrol

        self.scan_radius = 5000  # 5000 counts, 5000*0.05um = 250um, +-250um
        self.starting_point = [0,0,138,0,0,0]
        self.step_Rxy = 0.5
        self.step_Rz = 0
        self.reduction_ratio = 0.5
        self.error_flag = False
        self.limit_Z = 142
        self.tolerance = 5
        self.Z_amp = 4
        self.stepScanCounts = 10
        self.angle_flag = False
        self.final_adjust = False
        self.larger_Z_flag = False
        self.loss_criteria = -0.3
        self.final_adjust_threshold = -2.0
        self.stepmode_threshold = -4.0
        self.interpmode_threshold = -12.0
        self.scanmode = 'c'
        self.zmode = 'normal'

        self.loss = []
        self.pos = []
        self.loss_rec = []
        self.pos_rec = []
        self.current_pos = [0,0,138,0,0,0]    
        self.pos_ref = [0,0,138,0,0,0]
        self.x_dir = 1
        self.y_dir = 1
        self.loss_current_max = -60.0
        self.loss_fail_improve = 0


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

    def autoRun(self):
        print('A New Alignment Starts')
        logging.info(' ')
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        logging.info('A New Alignment Starts') 
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        self.send_to_hpp(self.starting_point)
        # time.sleep(2)
        self.hppcontrol.slow_traj_speed()
        P0 = self.starting_point[:]
        P1 = P0[:]
        self.scanmode = 'c'
        retry_num = 0
        self.loss = [-60]
        while not self.error_flag:
            # Select mode and parameters as loss
            if self.mode_select(max(self.loss)):
                P_final = P0[:]
                break

            # only continue scan mode can return false
            P1 = self.scanUpdate(P0, self.scanmode)
            if P1 == False:
                if max(self.loss) > -10 and self.scanmode == 'c':
                    self.scanmode = 's'
                    print('XY continuesly scan failed, change to step scan')
                    logging.info('XY continuesly scan failed, change to step scan')
                    self.error_flag = False
                    continue
                else:
                    if self.scanmode == 'c':
                        print('XY continuesly scan failed')
                        logging.info('XY continuesly scan failed')
                    else:
                        print('XY step scan failed')
                        logging.info('XY step scan failed')                        
                    P_final = P0[:]
                    break
            
            # if max(self.loss) > -15 and self.angle_flag:
                # P1 = self.optimRxy(P1)
                # if P1 == False:
                #     break
                # # angle flag to determine whether angle are optimized
                # self.angle_flag = False         
            
            # Select mode and parameters as loss
            if self.mode_select(max(self.loss)):
                P_final = P1[:]
                break

            P0 = self.optimZ(P1)
            # Return False Reason 1: Z step is too small
            # Return False Reason 2: Unexpected high loss
            if P0 == False:
                if not self.final_adjust and max(self.loss) > self.stepmode_threshold:
                    print('Change to Final_adjust(Z optim failed once)')
                    logging.info('Change to Final_adjust(Z optim failed once)')
                    self.final_adjust = True
                    self.stepScanCounts = 4    
                    self.tolerance = 2           
                    P0 = P1[:]      
                else:
                    # come to here: 
                    # 1. Z fail and loss < -5, still interp mode
                    # 2. Z fail and loss between (-5,-2), step mode and final adjust is on
                    # 3. Z fail and loss smaller than -2, step mode and final adjust is on
                    if max(self.loss) < self.loss_criteria and retry_num < 1:
                        print('Another Try')
                        logging.info('Another Try')
                        P0 = P1[:]
                        step_ref = round(abs(self.loss[-1]), 1) * 0.001
                        # Z back off
                        P0[2] = P0[2] - step_ref * 30
                        self.hppcontrol.engage_motor()
                        self.send_to_hpp(P0)
                        self.loss_current_max = -20.0
                        retry_num += 1
                    else:
                        if max(self.loss) < self.loss_criteria:
                            P_final = self.scanUpdate(P1, self.scanmode)
                        else:
                            P_final = P1[:]
                        break

        self.hppcontrol.normal_traj_speed()
        return P_final

    # return true if meet criteria, otherwise return none
    def mode_select(self, loss0):
        # if <= -12, then continue scan mode
        if loss0 <= self.interpmode_threshold:
            self.Z_amp = 4
            self.zmode = 'aggressive'
        # if (-12,-4], then interp(or still continue scan) mode 
        elif loss0 <= self.stepmode_threshold:
            # self.scanmode = 'i'
            self.zmode = 'normal'
            self.Z_amp = 2
            self.tolerance = 2
        # if (-4,-2], then step mode
        elif loss0 <= self.final_adjust_threshold:  
            self.zmode = 'normal'
            self.scanmode = 's'
            self.Z_amp = 1.5
            self.tolerance = 2
        # if (-2,criteria], then final adjust 
        elif loss0 <= self.loss_criteria:
            print('Change to Final_adjust')
            logging.info('Change to Final_adjust')
            self.zmode = 'normal'
            self.scanmode = 's'
            self.final_adjust = True
            self.stepScanCounts = 3 
            self.Z_amp = 1.2
            if max(self.loss) > -1.0:
                # self.tolerance = 1
                pass
            else:
                self.tolerance = 2 
        # if > criteria, then exit
        else:
            print('Better than criteria')
            logging.info('Better than criteria')
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

    # Change the acce to 500 c/s, then 
    def Xscan(self, X1_counts, X2_counts, X3_counts):
        # _dir can only be +1 or -1. When -1 means scan from adding counts
        # Purpose of _dir is to follow last correct direction, instead of substract then add counts every time
        # T1x direction is opposite compare to T2x and T3x
        x1start = X1_counts - self.scan_radius * self.x_dir
        x1end = X1_counts + self.scan_radius * self.x_dir
        x2start = X2_counts + self.scan_radius * self.x_dir
        x2end = X2_counts - self.scan_radius * self.x_dir
        x3start = X3_counts + self.scan_radius * self.x_dir
        x3end = X3_counts - self.scan_radius * self.x_dir

        self.fetch_loss()
        loss0 = self.loss[-1]
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]
        pos0 = X1_counts
        # Use T1's position as reference
        self.hppcontrol.Tx_send_only(x1start, x2start, x3start, 't')
        for i in range(0,2):
            if self.active_monitor('x', loss0, pos0):
                index = self.loss.index(max(self.loss)) - 1
                x1_final = self.pos[index] 
                # x1_final = self.pos[index] * 0.75 + self.pos[index + 1] * 0.25
                x2_final = -x1_final + x1start + x2start
                x3_final = -x1_final + x1start + x3start
                self.hppcontrol.Tx_send_only(x1_final, x2_final, x3_final, 's')
                # check on target, need to check all of them
                timeout = 0
                while not self.hppcontrol.Tx_on_target(x1_final, x2_final, x3_final, self.tolerance):
                    time.sleep(0.1)
                    timeout += 1
                    if timeout > 200:
                        print('Movement Timeout Error')
                        logging.info('Movement Timeout Error')
                        return False
                # if i = 0, x_dir = _dir; if i = 1, x_dir = -_dir
                self.x_dir = self.x_dir * (-2 * i + 1)
                self.update_current_pos('x', x1_final, X1_counts)
                self.check_abnormal_loss(max(self.loss))
                if x1_final - X1_counts:
                    return x1_final - X1_counts 
                else:
                    return 1
            else:
                if i:
                    # if fail, the fixture needs to go back to the original position
                    self.hppcontrol.Tx_send_only(X1_counts, X2_counts, X3_counts, 's')
                    timeout = 0
                    while not self.hppcontrol.Tx_on_target(X1_counts, X2_counts, X3_counts, self.tolerance):
                        time.sleep(0.1)
                        timeout += 1
                        if timeout > 200:
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
                self.hppcontrol.Tx_send_only(x1mid, x2mid, x3mid, 's')
                time.sleep(0.2)    
                self.update_current_pos('x', x1mid, X1_counts)        
                self.hppcontrol.Tx_send_only(x1end, x2end, x3end, 't')          


    def Yscan(self, Y1_counts, Y2_counts, Y3_counts):
        # _dir can only be +1 or -1. When -1 means scan from adding counts
        # Purpose of _dir is to follow last correct direction, instead of substracting then adding counts every time
        y1start = Y1_counts - self.scan_radius * self.y_dir
        y1end = Y1_counts + self.scan_radius * self.y_dir
        y2start = Y2_counts - self.scan_radius * self.y_dir
        y2end = Y2_counts + self.scan_radius * self.y_dir
        y3start = Y3_counts - self.scan_radius * self.y_dir
        y3end = Y3_counts + self.scan_radius * self.y_dir

        self.fetch_loss()
        loss0 = self.loss[-1]
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]
        pos0 = Y1_counts
        # use T1's position as position reference
        self.hppcontrol.Ty_send_only(y1start, y2start, y3start,'t')       
        for i in range(0,2):
            if self.active_monitor('y', loss0, pos0):
                index = self.loss.index(max(self.loss)) - 1
                y1_final = self.pos[index]
                # y1_final = self.pos[index] * 0.75 + self.pos[index + 1] * 0.25
                y2_final = y1_final - y1start + y2start
                y3_final = y1_final - y1start + y3start
                self.hppcontrol.Ty_send_only(y1_final, y2_final, y3_final, 's')
                # check on target, check all of them
                timeout = 0
                while not self.hppcontrol.Ty_on_target(y1_final, y2_final, y3_final, self.tolerance):
                    time.sleep(0.1)  
                    timeout += 1
                    if timeout > 200:
                        print('Movement Timeout Error')
                        logging.info('Movement Timeout Error')
                        return False
                # if i = 0, y_dir = _dir; if i = 1, y_dir = -_dir
                self.y_dir = self.y_dir * (-2 * i + 1)
                self.update_current_pos('y', y1_final, Y1_counts)
                self.check_abnormal_loss(max(self.loss))
                if y1_final - Y1_counts:
                    return y1_final - Y1_counts
                else:
                    return 1
            else:
                if i:
                    # if fail, go back to original position
                    self.hppcontrol.Ty_send_only(Y1_counts, Y2_counts, Y3_counts, 's')
                    timeout = 0
                    while not self.hppcontrol.Ty_on_target(Y1_counts, Y2_counts, Y3_counts, self.tolerance):
                        time.sleep(0.1)     
                        timeout += 1
                        if timeout > 200:
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
                self.hppcontrol.Ty_send_only(y1mid, y2mid, y3mid, 's')
                time.sleep(0.2)
                self.update_current_pos('y', y1mid, Y1_counts)
                self.hppcontrol.Ty_send_only(y1end, y2end, y3end, 't')               

    # x1_o is counts
    def Xstep(self, x1_o, x2_o, x3_o):
        print('Start Xstep (loss then pos)')
        logging.info('Start Xstep (loss then pos)')        
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(x1_o)    
        print(x1_o)  
        logging.info(x1_o)
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]

        x1 = x1_o
        x2 = x2_o
        x3 = x3_o
        loss_o = self.loss[-1]
        trend = 1
        same_count = 0
        while True:
            # x2 and x3 are in opposite direction as x1
            x1 = x1 - self.stepScanCounts * self.x_dir
            x2 = x2 + self.stepScanCounts * self.x_dir
            x3 = x3 + self.stepScanCounts * self.x_dir
            if self.final_adjust:
                self.hppcontrol.engage_motor()
            self.hppcontrol.Tx_send_only(x1, x2, x3, 's')
            timeout = 0
            while not self.hppcontrol.Tx_on_target(x1, x2, x3, self.tolerance):
                time.sleep(0.1)
                timeout += 1
                if timeout > 200:
                    print('Movement Timeout Error')
                    logging.info('Movement Timeout Error')
                    return False
            if self.final_adjust:
                self.hppcontrol.disengage_motor()
            self.update_current_pos('x', x1, x1_o)
            self.fetch_loss()
            self.pos.append(x1)
            print(x1)  
            logging.info(x1)
            self.save_loss_pos()

            bound = self.loss_resolution(loss_o)
            diff = self.loss[-1] - loss_o
            # if descrease, change direction, go back to the old point
            # if increase or the same, continue
            if diff <= -bound:
                # go back to the old point
                x1 = x1 + self.stepScanCounts * self.x_dir
                x2 = x2 - self.stepScanCounts * self.x_dir
                x3 = x3 - self.stepScanCounts * self.x_dir
                trend -= 1
                # if trend != 0, then exit
                if trend:
                    print('Over')
                    logging.info('Over')
                    break
                self.x_dir = -self.x_dir    
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
                    x1 = x1 + self.stepScanCounts * self.x_dir * 5
                    x2 = x2 - self.stepScanCounts * self.x_dir * 5
                    x3 = x3 - self.stepScanCounts * self.x_dir * 5
                    break
        
        if self.final_adjust:
            self.hppcontrol.engage_motor()
        self.hppcontrol.Tx_send_only(x1, x2, x3, 's')
        timeout = 0
        while not self.hppcontrol.Tx_on_target(x1, x2, x3, self.tolerance):
            time.sleep(0.1)
            timeout += 1
            if timeout > 200:
                print('Movement Timeout Error')
                logging.info('Movement Timeout Error')
                return False
        if self.final_adjust:
            self.hppcontrol.disengage_motor()
        self.update_current_pos('x', x1, x1_o)
        self.check_abnormal_loss(max(self.loss))
        if same_count >= 5:
            return False       
        if x1 - x1_o:
            return x1 - x1_o
        else:
            return 1

    # y1_o is counts
    def Ystep(self, y1_o, y2_o, y3_o):
        print('Start Ystep (loss then pos)')
        logging.info('Start Ystep (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(y1_o)    
        print(y1_o)  
        logging.info(y1_o)  
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]

        y1 = y1_o
        y2 = y2_o
        y3 = y3_o
        loss_o = self.loss[-1]
        trend = 1
        same_count = 0
        while True:
            y1 = y1 - self.stepScanCounts * self.y_dir
            y2 = y2 - self.stepScanCounts * self.y_dir
            y3 = y3 - self.stepScanCounts * self.y_dir
            if self.final_adjust:
                self.hppcontrol.engage_motor()
            self.hppcontrol.Ty_send_only(y1, y2, y3, 's')
            timeout = 0
            while not self.hppcontrol.Ty_on_target(y1, y2, y3, self.tolerance):
                time.sleep(0.1)
                timeout += 1
                if timeout > 200:
                    print('Movement Timeout Error')
                    logging.info('Movement Timeout Error')
                    return False
            if self.final_adjust:
                self.hppcontrol.disengage_motor()
            self.update_current_pos('y', y1, y1_o)
            self.fetch_loss()
            self.pos.append(y1)
            print(y1)  
            logging.info(y1)
            self.save_loss_pos()

            bound = self.loss_resolution(loss_o)
            diff = self.loss[-1] - loss_o
            # if descrease, change direction, go back to the old point
            # if increase or the same, continue
            if diff <= -bound:
                # go back to the old point
                y1 = y1 + self.stepScanCounts * self.y_dir
                y2 = y2 + self.stepScanCounts * self.y_dir
                y3 = y3 + self.stepScanCounts * self.y_dir
                trend -= 1
                # if trend != 0, exit
                if trend:
                    print('Over')
                    logging.info('Over')
                    break
                self.y_dir = -self.y_dir    
                loss_o = self.loss[-1]   
                print('Change direction')
                logging.info('Change direction') 
                same_count = 0          
            elif diff >= bound:
                loss_o = self.loss[-1]
                trend = 2
                same_count = 0
            else:
                trend = 2
                same_count += 1
                if same_count >= 5:
                    y1 = y1 + self.stepScanCounts * self.y_dir * 5
                    y2 = y2 + self.stepScanCounts * self.y_dir * 5
                    y3 = y3 + self.stepScanCounts * self.y_dir * 5
                    break              

        if self.final_adjust:
            self.hppcontrol.engage_motor()
        self.hppcontrol.Ty_send_only(y1, y2, y3, 's')
        timeout = 0
        while not self.hppcontrol.Ty_on_target(y1, y2, y3, self.tolerance):
            time.sleep(0.1)
            timeout += 1
            if timeout > 200:
                print('Movement Timeout Error')
                logging.info('Movement Timeout Error')
                return False
        if self.final_adjust:
            self.hppcontrol.disengage_motor()
        self.update_current_pos('y', y1, y1_o)
        self.check_abnormal_loss(max(self.loss))
        if same_count >= 5:
            return False
        if y1 - y1_o:
            return y1 - y1_o
        else:
            return 1

    # x1_o is counts, fixture needs to be at x1_o
    def Xinterp(self, x1_o, x2_o, x3_o):
        print('Start Xinterp (loss then pos)')
        logging.info('Start Xinterp (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(x1_o)    
        print(x1_o)  
        logging.info(x1_o)  
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]    
        # step in counts   
        step = self.xyinterp_sample_step(self.loss[-1]) / 0.05

        x1 = [x1_o, x1_o-step, x1_o-2*step, x1_o-3*step, x1_o+step, x1_o+2*step, x1_o+3*step]
        x2 = [x2_o, x2_o+step, x2_o+2*step, x2_o+3*step, x2_o-step, x2_o-2*step, x2_o-3*step]
        x3 = [x3_o, x3_o+step, x3_o+2*step, x3_o+3*step, x3_o-step, x3_o-2*step, x3_o-3*step]
        for i in range(1,7):
            self.hppcontrol.Tx_send_only(x1[i], x2[i], x3[i], 's')
            timeout = 0
            while not self.hppcontrol.Tx_on_target(x1[i], x2[i], x3[i], self.tolerance):
                time.sleep(0.1)
                timeout += 1
                if timeout > 200:
                    print('Movement Timeout Error')
                    logging.info('Movement Timeout Error')
                    return False
            self.update_current_pos('x', x1[i], x1_o)
            self.fetch_loss()
            self.pos.append(x1[i])
            print(x1[i])  
            logging.info(x1[i])
            self.save_loss_pos()

        grid = [*range(int(x1_o-3*step), int(x1_o+3*step+1), 2)]
        s = interpolation.barycenteric_interp(x1,self.loss,grid)
        x1_final = grid[s.index(max(s))]
        x2_final = -x1_final + x1_o + x2_o
        x3_final = -x1_final + x1_o + x3_o
        self.hppcontrol.Tx_send_only(x1_final, x2_final, x3_final, 's')
        # check on target, need to check all of them
        timeout = 0
        while not self.hppcontrol.Tx_on_target(x1_final, x2_final, x3_final, self.tolerance):
            time.sleep(0.1)
            timeout += 1
            if timeout > 200:
                print('Movement Timeout Error')
                logging.info('Movement Timeout Error')
                return False
        self.update_current_pos('x', x1_final, x1_o)
        print('XInterp final: ',x1_final)
        logging.info('XInterp final: ' + str(x1_final))
        self.check_abnormal_loss(max(self.loss))
        if x1_final - x1_o:
            return x1_final - x1_o 
        else:
            return 1


    # y1_o is counts, fixture needs to be at y1_o
    def Yinterp(self, y1_o, y2_o, y3_o):
        print('Start Yinterp (loss then pos)')
        logging.info('Start Yinterp (loss then pos)')  
        self.loss = []        
        self.pos = []
        self.fetch_loss()
        self.pos.append(y1_o)    
        print(y1_o)  
        logging.info(y1_o)  
        self.save_loss_pos()
        self.pos_ref = self.current_pos[:]    
        # step in counts   
        step = self.xyinterp_sample_step(self.loss[-1]) / 0.05

        y1 = [y1_o, y1_o-step, y1_o-2*step, y1_o-3*step, y1_o+step, y1_o+2*step, y1_o+3*step]
        y2 = [y2_o, y2_o-step, y2_o-2*step, y2_o-3*step, y2_o+step, y2_o+2*step, y2_o+3*step]
        y3 = [y3_o, y3_o-step, y3_o-2*step, y3_o-3*step, y3_o+step, y3_o+2*step, y3_o+3*step]
        for i in range(1,7):
            self.hppcontrol.Ty_send_only(y1[i], y2[i], y3[i], 's')
            timeout = 0
            while not self.hppcontrol.Ty_on_target(y1[i], y2[i], y3[i], self.tolerance):
                time.sleep(0.1)
                timeout += 1
                if timeout > 200:
                    print('Movement Timeout Error')
                    logging.info('Movement Timeout Error')
                    return False
            self.update_current_pos('y', y1[i], y1_o)
            self.fetch_loss()
            self.pos.append(y1[i])
            print(y1[i])  
            logging.info(y1[i])
            self.save_loss_pos()

        grid = [*range(int(y1_o-3*step), int(y1_o+3*step+1), 2)]
        s = interpolation.barycenteric_interp(y1,self.loss,grid)
        y1_final = grid[s.index(max(s))]
        y2_final = y1_final - y1_o + y2_o
        y3_final = y1_final - y1_o + y3_o
        self.hppcontrol.Ty_send_only(y1_final, y2_final, y3_final, 's')
        # check on target, need to check all of them
        timeout = 0
        while not self.hppcontrol.Ty_on_target(y1_final, y2_final, y3_final, self.tolerance):
            time.sleep(0.1)
            timeout += 1
            if timeout > 200:
                print('Movement Timeout Error')
                logging.info('Movement Timeout Error')
                return False
        self.update_current_pos('y', y1_final, y1_o)
        print('YInterp final: ',y1_final)
        logging.info('YInterp final: ' + str(y1_final))
        self.check_abnormal_loss(max(self.loss))
        if y1_final - y1_o:
            return y1_final - y1_o 
        else:
            return 1


    # Based on loss to determine xy interpolation sample step size
    def xyinterp_sample_step(self, loss):
        # loss = [-20, -15, -10, -5, -1]
        # step size in um, in counts will be [90, 70, 50, 30, 20]
        step_size = [5, 4, 3, 1.5, 1]
        if loss <= -20:
            return step_size[0]
        elif loss <= -15:
            return step_size[1]
        elif loss <= -10:
            return step_size[2]
        elif loss <= -5:
            return step_size[3]
        else:
            return step_size[4]

    # Return P1 after XY scan starting from P0, fixture is at P1, the loss is not updated
    # mode can be 's' (step) or 'c' (continusly) or 'i' (interpolation)
    # Need fixture to be at P0 location in the begining, fixture will be at P1 in the end.
    # interpolation mode won't return false
    # return false when 1. scan mode, decrease in both direction;
    #                   2. step mode, loss doesn't change for several steps
    #                   3. Motor failed to move, fail on on_target check
    def scanUpdate(self, P0, _mode):
        print('Scan update starts at: ', P0)
        logging.info('Scan update starts at: ' + str(P0))
        P1 = P0[:]
        self.current_pos = P0[:]
        Tmm = self.HPP.findAxialPosition(P0[0], P0[1], P0[2], P0[3], P0[4], P0[5])
        Tcounts = self.hppcontrol.translate_to_counts(Tmm) 
        logging.info('Start Tcounts: '+str(Tcounts))
        if _mode == 's':
            xdelta = self.Xstep(Tcounts[0], Tcounts[2], Tcounts[4])
        elif _mode == 'i':
            xdelta = self.Xinterp(Tcounts[0], Tcounts[2], Tcounts[4])
        else:
            xdelta = self.Xscan(Tcounts[0], Tcounts[2], Tcounts[4])
        if xdelta:
            P1[0] = P1[0] + 50e-6 * xdelta
        else:
            if _mode == 's':
                print('X step failed')
                logging.info('X step failed')
                self.error_flag = True
                return False
            else:
                print('X scan failed')
                logging.info('X scan failed')
                self.error_flag = True
                return False                
        
        if _mode == 's':
            ydelta = self.Ystep(Tcounts[1], Tcounts[3], Tcounts[5])
        elif _mode == 'i':
            ydelta = self.Yinterp(Tcounts[1], Tcounts[3], Tcounts[5])
        else:
            ydelta = self.Yscan(Tcounts[1], Tcounts[3], Tcounts[5])
        if ydelta:
            P1[1] = P1[1] + 50e-6 * ydelta
        else:
            if _mode == 's':
                print('Y step failed')
                logging.info('Y step failed')
                self.error_flag = True
                return False
            else:
                print('Y scan failed')
                logging.info('Y scan failed')
                self.error_flag = True
                return False                
        print('Scan update ends at: ', P1)
        logging.info('Scan update ends at: ' + str(P1))
        logging.info('X change: '+str(xdelta)+'; '+'Y change: '+str(ydelta))
        return P1

    # loss bound based on loss value
    def loss_resolution(self, _loss_ref):
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

    # Starting from P0, change only Z to go to P1, 
    # the fixture will be in P1 in the end, and the fixture needs to be in P0 in the beginning
    def optimZ(self, P0):
        print('Z optim starts at (pos then loss): ')
        print(P0)
        logging.info('Z optim starts at (pos then loss): ')
        logging.info(P0)
        P1 = P0[:]
        self.loss = []
        self.fetch_loss()
        # self.current_pos = P0[:]
        self.save_loss_pos()
        success_num = 0
        loss_o = self.loss[-1]
        # Step size is related to loss, for example in -15.72 dB, step size is 15.7 um.
        step_ref = round(abs(self.loss[-1]), 1) * 0.001
        # give step size an amplifier
        step = step_ref * self.Z_amp
        if step < 0.0015:
            step = 0.0015
        while True:
            P1[2] = P1[2] + step

            if P1[2] > self.limit_Z:
                P1[2] = P1[2] - step
                # step size is 0.45 of the gap
                step = 0.45 * (self.limit_Z - P1[2])
                if step > 0.0007:
                    step = 0.0007
                if step < 0.0002:
                    print('Z step is too small')
                    logging.info('Z step is too small (by Z limit)')
                    return False 
                print('Regulated by Z limit')
                logging.info('Regulated by Z limit')
                P1[2] = P1[2] + step
            
            if self.final_adjust:
                self.hppcontrol.engage_motor()
            if self.send_to_hpp(P1):
                if self.final_adjust:
                    # time.sleep(0.1)
                    self.hppcontrol.disengage_motor()
                self.fetch_loss()
                self.current_pos = P1[:]
                self.save_loss_pos()
            else:
                print('Movement Error')
                logging.info('Movement Error')
                self.error_flag = True
            
            # aggressive mode: Z goes forward until loss is 2 times of the initial value
            # for instance, loss_o = -15, then until -22.5 dB we stop forwarding Z
            # The purpose is to forward Z more aggressively to faster the process
            # make sure the loss is smaller than -5 and larger than -40, so that larger Z stepping won't be problem
            if self.zmode == 'aggressive' and max(self.loss) < -5 and min(self.loss) > -40:
                if self.loss[-1] > 1.5 * loss_o:
                    success_num += 1
                    continue

            bound = self.loss_resolution(loss_o)
            diff = self.loss[-1] - loss_o
            # if fail (smaller), difference should be smaller than -loss_resolution
            if diff < -bound:            
                # if fail, go back to the old point
                P1[2] = P1[2] - step 
                # step = self.reduction_ratio * step
                # radio here should be smaller than 0.5 not 0,5, otherwise two steps will go back to the previous position
                step = 0.4 * step                    
                
                # if step size is smaller than minimum resolution, exit
                if step < 0.0002:
                    print('Z step is too small')
                    logging.info('Z step is too small')
                    return False    
                
                # if loss is still high and step size is small enough, we will larger the step to 
                # jump out of the local minimum
                if step < step_ref / 12 and max(self.loss) < -15 and self.larger_Z_flag:
                    # A larger step size
                    step = step_ref * 15
                    P1[2] = P1[2] + step
                    print('A larger Z step')
                    logging.info('A larger Z step')
                    if P1[2] > self.limit_Z:
                        P1[2] = P1[2] - step
                        # step size is 0.45 of the gap
                        step = 0.45 * (self.limit_Z - P1[2])
                        P1[2] = P1[2] + step
                        print('Larger Z step is regulated by Z limit')
                        logging.info('Larger Z step is regulated by Z limit')
                    # make sure it will exit for next XY scan round
                    success_num = 1           
                    # Only do larger Z step once 
                    self.larger_Z_flag = False
                
                if success_num:
                    # go back to the best points
                    # give extra value to counter backlash
                    P1[2] = P1[2] - 0.0002
                    if self.final_adjust:
                        self.hppcontrol.engage_motor()
                    if not self.send_to_hpp(P1):
                        print('Movement Error')
                        logging.info('Movement Error')
                        self.error_flag = True
                    if self.final_adjust:
                        # time.sleep(0.1)
                        self.hppcontrol.disengage_motor()
                    self.current_pos = P1[:]
                    break
            # if larger than bound, then success and update loss old
            elif diff > bound:
                loss_o = self.loss[-1]
                success_num += 1 
            # if same, then success, but don't update loss old
            else:
                success_num += 1
        print('Z optim ends at: ', P1)
        logging.info('Z optim ends at: ' + str(P1))      
        self.check_abnormal_loss(max(self.loss))
        return P1

    def check_abnormal_loss(self, loss0):
        if loss0 > self.loss_current_max:
            self.loss_current_max = loss0
            self.loss_fail_improve = 0
        elif (loss0 < (2.5 * self.loss_current_max) and loss0 < -10) or loss0 < -55:
            print('Unexpected High Loss, End Program')
            logging.info('Unexpected High Loss, End Program')
            self.hppcontrol.engage_motor()
            self.hppcontrol.normal_traj_speed()
            self.send_to_hpp(self.starting_point)
            self.hppcontrol.disengage_motor()
            import sys
            sys.exit()
        else:
            # x,y and z fail to improve 6 times continuesly, then reset the loss_criteria as current max
            # this is to faster the process
            self.loss_fail_improve += 1
            if self.loss_fail_improve == 6:
                self.loss_criteria = self.loss_current_max - 0.01


    def fetch_loss(self):
        self.loss.append(PM.power_read())


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
        print(pos0)    
        logging.info(pos0)
        while True:
            self.fetch_loss()

            self.pos.append(self.hppcontrol.T_get_counts(1, xy))   
            print(self.pos[-1])  
            logging.info(self.pos[-1])   
            self.update_current_pos(xy, self.pos[-1], pos0)

            self.save_loss_pos()
            
            loss_diff = self.loss[-1] - loss_o
            bound = self.loss_resolution(loss_o)
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
    def send_to_hpp(self, R):   
        target_mm = R[:]
        print(target_mm)
        logging.info(target_mm)
        # Read real time counts        
        Tmm = self.HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
        # target_counts = self.hppcontrol.run_to_Tmm(Tmm, self.tolerance)
        self.hppcontrol.run_to_Tmm(Tmm, self.tolerance)
        # print(target_counts)
        # real_counts = control.Tcounts_real
        error_log = control.error_log
        if error_log != '':
            # error_flag = True
            return False 
        # else:
            # error_flag = False        
        return True  

