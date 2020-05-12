import Back_Model as BM
import HPP_Control as control
import PowerMeter as PowerMeter
import time
import numpy as np
import matplotlib.pyplot as plt


class Pattern_Search:
    def __init__(self, dofs):
        # n is the number of dofs
        # dof_start is the staring dof, by default it starts from 0
        self.n = dofs
        self.dof_start = 0
        self.start_point = [0,0,138,0,0,0]
        self.step = 0.05
        # if self.n == 6:    
        #     self.step = [0.05,0.05,0.05,0.05,0.05,0.05]
        # elif self.n == 5:
        #     self.step = [0.05,0.05,0.05,0.05,0.05,0]
        # else:
        #     self.step = [0.05,0.05,0.05,0,0,0]
        self.reduction_ratio = 0.5
        self.acceleration = 2
        self.Zlimit = 138.88

    HPP = BM.BackModel()
    HPP.set_Pivot(np.array([[0], [0], [28.5], [0]]))
    hppcontrol = control.HPP_Control()

    def set_startpoint(self, _start_point):
        self.start_point = _start_point
    
    def set_init_step(self, _init_step):
        self.step = _init_step

    def set_reduction_ratio(self, _reduction_ratio):
        self.reduction_ratio = _reduction_ratio

    def set_acceleration(self, _acceleration):
        self.acceleration = _acceleration
    
    def set_Zlimit(self, _Zlimit):
        self.Zlimit = _Zlimit

    pos_rec = []
    loss_rec = []    
    move_num = 0

    def store_all(self, _p, _loss):
        for i in range(0,len(self.loss_rec)):
            if _p == self.pos_rec[i]:
                return None
        self.pos_rec.append(_p)
        self.loss_rec.append(_loss)

    def autoRun(self):
        R0 = self.start_point[:]      
        #Send to fixture, if error occur, return false
        if not self.send_to_hpp(R0):
            return 
        # loss_R0 = PowerMeter.get_loss_simulate(R0)
        loss_R0 = PowerMeter.power_read()
        self.store_all(R0, loss_R0)
        self.move_num += 1 
        while True:     
            #Detecting Motion from R0 to R1
            # TODO: if false, results has no [0]
            results = self.detecting_move(R0, loss_R0)
            R1 = results[0]
            if R1 == False:
                break
            loss_R1 = results[1]
            
            results = self.pattern_move(R0, R1, loss_R1)
            try:
                R0 = results[0]
                loss_R0 = results[1]
            except:
                # return only False
                break
        
        print('Maximum point')
        print(R0)
        print('Minimum loss (or maximum value)')
        print(PowerMeter.power_read())
        print('Move Number')
        print(self.move_num)
        # self.plots()

    # Input is R0, output is R1 and its loss
    def detecting_move(self, R0, _loss_R0):
        R1 = R0[:]
        _loss_R1 = _loss_R0
        step_ref = round(abs(_loss_R0), 1) * 0.001
        while True:        
            for i in range(self.dof_start, (self.dof_start + self.n)):
                # for angles, step should be larger than 0.01
                if i > 2 and self.step < 0.01:
                    continue
                R1_try = R1[:] 
                R1_try[i] = R1[i] - self.step
                #Send to fixture, if error occur, return false with value of 99.0
                if not self.send_to_hpp(R1_try):
                    return False, 99.0
                # time.sleep(0.5)
                # loss_try = PowerMeter.get_loss_simulate(R1_try)
                loss_try = PowerMeter.power_read()
                self.move_num += 1
                self.store_all(R1_try, loss_try)
                if loss_try > _loss_R1:
                    R1 = R1_try[:]
                    _loss_R1 = loss_try
                else:
                    R1_try[i] = R1[i] + self.step
                    # Add z limit, if z is larger than 139.06 then we continue and keep the old value
                    if R1_try[i] > self.Zlimit:
                        continue
                    #Send to fixture, if error occur, return false with value of 99.0
                    if not self.send_to_hpp(R1_try):
                        return False, 99.0
                    # loss_try = PowerMeter.get_loss_simulate(R1_try)
                    loss_try = PowerMeter.power_read()
                    self.move_num += 1                      
                    self.store_all(R1_try, loss_try)
                    if loss_try > _loss_R1:
                        R1 = R1_try[:]
                        _loss_R1 = loss_try
            
            if _loss_R1 > _loss_R0:
                return R1, _loss_R1
            else:
                # for j in range(0,self.n):
                    # self.step[j] = self.reduction_ratio * self.step[j]
                self.step = self.reduction_ratio * self.step
                R1 = R0[:]
                # Stop Criteria when xyz step is smaller than 10 steps
                if self.step < 0.0005:
                    return False, _loss_R0
                if self.step < (step_ref / 10) and _loss_R0 < -20:
                    R1[2] = R1[2] + step_ref * 15
                    print('A larger Z step')
                    if R1[2] > self.Zlimit:
                        R1[2] = R1[2] - step_ref * 15
                        # step size is 0.45 of the gap
                        R1[2] = R1[2] + 0.45 * (self.Zlimit - R1[2])
                        self.step = step_ref / 5

    
    def pattern_move(self, R0, R1, _loss_R1):
        # Pattern Move 
        while True:
            # Tentative Pattern Move
            # R2 = acceleration*R1 - R0
            R2_t = R1[:]
            for j in range(self.dof_start, (self.dof_start + self.n)):
                R2_t[j] = self.acceleration * R1[j] - R0[j] 
            # Limit on Z
            if R2_t[2] > self.Zlimit:
                R2_t[2] = self.Zlimit
            #Send to fixture, if error occur, return false
            if not self.send_to_hpp(R2_t):
                return False  
            # loss_R2_t = PowerMeter.get_loss_simulate(R2_t)
            loss_R2_t = PowerMeter.power_read()
            self.store_all(R2_t, loss_R2_t)
            self.move_num += 1 
            # Final Pattern Move     
            results = self.detecting_move(R2_t, loss_R2_t)
            R2_f = results[0]
            loss_R2_f = results[1]
            if R2_f == False:
                if loss_R2_f == 99.0:
                    # _error = True
                    return False
                R2_f = R2_t[:]

            # if loss is better, keep it and continue another pattern move
            if loss_R2_f > _loss_R1:
                R0 = R1[:]
                R1 = R2_f[:]
                _loss_R1 = loss_R2_f
            # if loss is worse, exit pattern move, go to detection move
            else:
                R0 = R1[:]
                _loss_R0 = _loss_R1
                break
        
        return R0, _loss_R0


    # takes about 0.168s
    def send_to_hpp(self, R):   
        target_mm = R[:]
        print(target_mm)
        # Read real time counts  
        Tcounts_old = control.Tcounts_real         
        Tmm = self.HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
        target_counts = self.hppcontrol.run_to_Tmm(Tmm, Tcounts_old, 5)
        real_counts = control.Tcounts_real
        error_log = control.error_log
        if error_log != '':
            error_flag = True
            return False 
        else:
            error_flag = False        
        # self.sig1.emit(error_log, target_mm, target_counts, real_counts, error_flag)
        return True  


    def plots(self):
        # Plot
        x = []
        for i in range(0,len(self.loss_rec)):
            x.append(self.pos_rec[i][0]) 
        z = []
        for i in range(0,len(self.loss_rec)):
            z.append(self.pos_rec[i][2]) 
        Ry = []
        for i in range(0,len(self.loss_rec)):
            Ry.append(self.pos_rec[i][4])         
        plt.figure(1)
        plt.plot(self.loss_rec,'-')   
        plt.ylabel('Loss')
        plt.xlabel('Iterations')    
        plt.figure(2)
        plt.plot(x,'-')
        plt.ylabel('X position (mm)')
        plt.xlabel('Iterations')
        plt.figure(3)
        plt.plot(z,'-')
        plt.ylabel('Z position (mm)')
        plt.xlabel('Iterations')
        plt.figure(4)
        plt.plot(Ry,'-')
        plt.ylabel('Ry position (degree)')
        plt.xlabel('Iterations')       
        plt.show()
