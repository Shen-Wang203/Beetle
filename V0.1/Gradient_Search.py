import Back_Model as BM
# import HPP_Control as control
import PowerMeter as PowerMeter
import time
import numpy as np
import matplotlib.pyplot as plt

class Gradient_Search():
    def __init__(self):
        self.start_point = [0,0,138,0,0,0]
        self.learning_rate = 4
        self.beta = 0.9
        self.reduction_ratio = 0.5
        self.start_momentum = [-0.05, -0.05, 0.05, 0.02, 0.02, 0]

    HPP = BM.BackModel()
    HPP.set_Pivot(np.array([[0], [0], [28.5], [0]]))
    # hppcontrol = control.HPP_Control()

    def set_startpoint(self, _startpoint):
        self.start_point = _startpoint
    
    def set_learning_rate(self, _learning_rate):
        self.learning_rate = _learning_rate
    
    def set_beta(self, _beta):
        self.beta = _beta

    def set_reduction_ratio(self, _reduction_ratio):
        self.reduction_ratio = _reduction_ratio
    
    def set_startMomentum(self, _startMomentum):
        self.start_momentum = _startMomentum

    iteration = 0
    pos = []
    loss_rec = []
    _error = False
    def autoRun(self):
        # Initiation
        P1 = self.start_point[:]      
        momentum0 = self.start_momentum
        momentum1 = momentum0[:]
        P2 = P1[:]
        P0 = P1[:]
        self.iteration += 1
        # #Send to fixture, if error occur, return false with value of 99.0
        # if not self.send_to_hpp(P1):
        #     self._error = True
        loss1 = PowerMeter.get_loss_simulate(P1)
        loss2 = 0.0
        loss0 = 0.0
        diff1 = self.diff(P1, loss1)
        self.pos.append(P1)
        self.loss_rec.append(loss1)
        # Main loop
        while not self._error:            
            break_count = 0
            for i in range(0,6):
                momentum1[i] = self.beta * momentum0[i] + (1-self.beta) * diff1[i]
                # self.learning_rate = abs(loss1+0.18) * 4
                delta = self.learning_rate * momentum1[i]               
                # if i < 3:
                #     if abs(delta) < 0.0005:
                #         delta = 0
                #         break_count += 1
                # else:
                #     if abs(delta) < 0.005:
                #         delta = 0
                #         break_count += 1
                # if break_count == 6:
                #     break               
                P2[i] = P1[i] + delta
                
            self.iteration += 1
            # #Send to fixture, if error occur, return false with value of 99.0
            # if not self.send_to_hpp(P2):
            #     self._error = True
            loss2 = PowerMeter.get_loss_simulate(P2)
            if self.iteration > 1000:
                break
            if loss2 > loss1:
                P0 = P1[:]
                P1 = P2[:]
                momentum0 = momentum1[:]
                loss0 = loss1
                loss1 = loss2
                # if loss1 >= -0.3:
                #     print(self.iteration)
                #     return P1, diff1
                #     break
                diff1 = self.diff(P1, loss1)
                self.pos.append(P1)
                self.loss_rec.append(loss1)
            else:
                self.learning_rate = self.reduction_ratio * self.learning_rate
                pass
        print('Iteration:')
        print(self.iteration)
        print('Final position')
        print(P1)
        print('Loss')
        print(loss1)    
        self.plots()            

    def diff(self, P1, loss1):
        delta_xyz = 0.0005
        delta_angle = 0.005
        diff1 = [0,0,0,0,0,0]
        P11 = P1[:]
        # Only find diff in 5 dofs
        for i in range(0,5):
            if i < 3:
                P11[i] = P1[i] - delta_xyz
                self.iteration += 1
                # #Send to fixture, if error occur, return false with value of 99.0
                # if not self.send_to_hpp(P11):
                #     self._error = True
                loss11 = PowerMeter.get_loss_simulate(P11)
                diff1[i] = (loss11 - loss1) / (-delta_xyz)
            else:
                P11[i] = P1[i] - delta_angle
                self.iteration += 1
                # #Send to fixture, if error occur, return false with value of 99.0
                # if not self.send_to_hpp(P11):
                #     self._error = True
                loss11 = PowerMeter.get_loss_simulate(P11)
                diff1[i] = (loss11 - loss1) / (-delta_angle)
            P11[i] = P1[i]
        return diff1
    
    def plots(self):
        # Plot
        plt.close('all')
        x = []
        for i in range(0,len(self.loss_rec)):
            x.append(self.pos[i][0]) 
        z = []
        for i in range(0,len(self.loss_rec)):
            z.append(self.pos[i][2]) 
        Ry = []
        for i in range(0,len(self.loss_rec)):
            Ry.append(self.pos[i][4])         
        print(z)
        plt.figure(1)
        plt.plot(self.loss_rec,'-+')   
        plt.ylabel('Loss')
        plt.xlabel('Iterations')    
        # plt.figure(2)
        # plt.plot(x,'-+')
        # plt.ylabel('X position (mm)')
        # plt.xlabel('Iterations')
        plt.figure(3)
        plt.plot(z,'-+')
        plt.ylabel('Z position (mm)')
        plt.xlabel('Iterations')
        plt.figure(4)
        plt.plot(Ry,'-+')
        plt.ylabel('Ry position (degree)')
        plt.xlabel('Iterations')       
        plt.show()


    # def send_to_hpp(self, R):   
    #     target_mm = R[:]
    #     print(target_mm)
    #     # Read real time counts  
    #     Tcounts_old = control.Tcounts_real         
    #     Tmm = self.HPP.findAxialPosition(R[0], R[1], R[2], R[3], R[4], R[5])
    #     target_counts = self.hppcontrol.run_to_Tmm(Tmm, Tcounts_old, 5)
    #     real_counts = control.Tcounts_real
    #     error_log = control.error_log
    #     if error_log != '':
    #         return False 
    #     return True 