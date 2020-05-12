import PowerMeter as PowerMeter
import time
import numpy as np
from Pattern_Search import Pattern_Search


class Pattern_SimplexGradient(Pattern_Search):
    def __init__(self, dofs):
        super().__init__(dofs)
        self.V = 100
        self.role = 3      
        self.smin = self.n + 1
        self.smax = self.n + 1
        self.pmax = 4 * (self.n + 1)
        if self.n == 6:
            self.norm_b_max = 2.449  # sqrt(6)
        elif self.n == 5:
            self.norm_b_max = 2.236  # sqrt(5)
        elif self.n == 3:
            self.norm_b_max = 1.732  # sqrt(3)
        else:
            pass


    def autoRun(self):
        p0 = self.start_point[:]
        #Send to fixture, if error occur, return false with value of 99.0
        # if not self.send_to_hpp(p0):
        #     return False, 99.0     
        loss_p0 = PowerMeter.get_loss_simulate(p0)
        self.store_all(p0, loss_p0)
        while len(self.loss_rec) < self.smin:
            #Detecting Motion from p0 to p1
            results = self.detecting_move(p0, loss_p0)
            p1 = results[0]
            if p1 == False:
                break
            # TODO: identify fixture error and stop the program
            loss_p1 = results[1]
            self.store_all(p1, loss_p1)

            # Pattern move from p1 to p0
            results = self.pattern_move(p0, p1, loss_p1)
            p0 = results[0]
            loss_p0 = results[1]
            if not p0:
                break
            # TODO: identify fixture error and stop the program

        while True:
            [Y_k, Y_k_loss] = self.get_Y_points(p0, loss_p0)
            if not Y_k:
                # TODO: end program imediately
                print('get_Y error')
            
            simplex_grad = self.simplexGradient(Y_k, Y_k_loss)
            try:
                if not simplex_grad:
                    # TODO: end program
                    print('gradient error')
            except:
                pass

            b_detecting = self.poll(simplex_grad)

            # Detecting move based on simplex gradient
            for i in range(0,self.n*2):
                p_try = p0[:]
                for j in range(0,self.n):
                    if j > 2 and self.step < 0.005:
                        continue
                    p_try[j] = p0[j] + b_detecting[i][j]  * self.step
                if p_try[2] > self.Zlimit:
                    continue
                #Send to fixture, if error occur, return false with value of 99.0
                # if not self.send_to_hpp(p0):
                #     return False, 99.0     
                loss_p_try = PowerMeter.get_loss_simulate(p_try)
                self.store_all(p_try, loss_p_try)
                if loss_p_try > loss_p0:
                    p1 = p_try[:]
                    loss_p1 = loss_p_try
                    break
            
            # Detecting move failed
            if i == self.n*2-1: 
                self.step = self.reduction_ratio * self.step
                if self.step < 0.0005:
                    # End the program
                    break
            # Pattern search if detecting move success
            else: 
                p_try = self.search(simplex_grad, p1)
                #Send to fixture, if error occur, return false with value of 99.0
                # if not self.send_to_hpp(p0):
                #     return False, 99.0     
                loss_p_try = PowerMeter.get_loss_simulate(p_try)
                self.store_all(p_try, loss_p_try)
                if loss_p_try > loss_p1:
                    p0 = p_try[:]
                    loss_p0 = loss_p_try
                else:
                    p0 = p1[:]
                    loss_p0 = loss_p1




    # First point is p0
    def get_Y_points(self, _p0, _loss_p0):
        a = np.asarray(_p0)
        Y_k = []
        Y_k_loss = []
        Y_k.append(_p0)
        Y_k_loss.append(_loss_p0)
        radius = self.role * self.norm_b_max * self.step
        for i in range(len(self.loss_rec)-1, -1, -1):
            b = np.asarray(self.pos_rec[i])
            norm = np.linalg.norm(a-b)
            if norm <= radius and norm != 0:
                Y_k.append(self.pos_rec[i])
                Y_k_loss.append(self.loss_rec[i])
                if len(Y_k) >= self.smax:
                    break
        if len(Y_k) < self.smin:
            return False, 0
        return Y_k, Y_k_loss

    # Simplex gradient based on p0, return a numpy array(1xn) whose dimension is the same as n
    def simplexGradient(self, _Y_k, _Y_k_loss):
        # Determined Case
        num_pnt = len(_Y_k)
        x0 = np.asarray(_Y_k[0][0:self.n])
        y0 = _Y_k_loss[0]
        S = np.zeros((self.n, num_pnt-1))
        F = np.zeros((num_pnt-1, 1))
        for i in range(1,num_pnt):
            xi = np.asarray(_Y_k[i][0:self.n])
            yi = _Y_k_loss[i]
            S[:, i-1] = np.transpose(xi - x0)
            F[i-1, :] = yi - y0
        try:
            simp_grad = np.linalg.solve(np.transpose(S), F) 
            # Change from nx1 to 1xn vector
            return simp_grad.reshape((self.n,))
        except:
            return False
    
    # From p1 to p0
    def search(self, _simp_grad, p1):
        radius = self.role * self.norm_b_max * self.step
        delta = radius * _simp_grad / np.linalg.norm(_simp_grad)
        delta = delta.tolist()
        p0 = p1[:]
        for i in range(0,self.n):
            p0[i] = p1[i] + delta[i]
        return p0
    
    def mesh(self):
        pass

    def poll(self, _simp_grad):
        b = []
        norm_grad = np.linalg.norm(_simp_grad)
        loop0 = [-1,0,1]
        loop1 = [-1,0,1]
        loop2 = [-1,0,1]
        if self.n == 3:
            loop1 = [0]
            loop2 = [0]
            _simp_grad = np.append(_simp_grad, [0,0,0])
        elif self.n == 5:
            loop2 = [0]
            _simp_grad = np.append(_simp_grad, [0])
        else:
            pass
        for i in loop0:
            for j in loop0:
                for k in loop0:
                    for l in loop1:
                        for m in loop1:
                            for n in loop2:
                                b.append([i,j,k,l,m,n])

        cos = []
        for i in range(0,len(b)):
            barray = np.asarray(b[i])
            cs = np.dot(_simp_grad, barray) / (norm_grad * np.linalg.norm(barray))
            cos.append(cs)
        
        b_poll = []
        for i in range(0,len(b)):
            maxindex = cos.index(max(cos))
            b_poll.append(b[maxindex])
            cos[maxindex] = 0

        return b_poll