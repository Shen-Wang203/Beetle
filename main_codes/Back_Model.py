import numpy as np
import math

# R = 50
# L = 78.5

def MRz(Rz):
    return np.array([[math.cos(math.radians(Rz)), -math.sin(math.radians(Rz)), 0, 0],
                     [math.sin(math.radians(Rz)), math.cos(math.radians(Rz)),  0, 0],
                     [0                         , 0                         ,  1, 0],
                     [0                         , 0                         ,  0, 1]])

def MRy(Ry):
    return np.array([[math.cos(math.radians(Ry)) , 0, math.sin(math.radians(Ry)), 0],
                     [0                          , 1,                          0, 0],
                     [-math.sin(math.radians(Ry)), 0, math.cos(math.radians(Ry)), 0],
                     [0                          , 0,                          0, 1]])    

def MRx(Rx):
    return np.array([[1,                          0,                           0, 0],
                     [0, math.cos(math.radians(Rx)), -math.sin(math.radians(Rx)), 0],
                     [0, math.sin(math.radians(Rx)),  math.cos(math.radians(Rx)), 0],
                     [0,                          0,                           0, 1]])     

def MT(x,y,z):
    return np.array([[1, 0, 0, x],
                     [0, 1, 0, y],
                     [0, 0, 1, z],
                     [0, 0, 0, 1]])

class BackModel:
    def __init__(self):
        self.R = 50
        self.L = 78.5
        self.r = 50 / math.cos(math.radians(30))
        self.pivotPoint = np.array([[0], [0], [0], [0]])
        pass 
    
    def set_Pivot(self, newPoint):
        self.pivotPoint = newPoint
    
    def set_R(self, newR):
        self.R = newR
        self.r = newR / math.cos(math.radians(30))
    
    def set_L(self, newL):
        self.L = newL
        
    def findAxialPosition(self, x, y, z, Rx, Ry, Rz):
        z = z - 65.9221 - 8

        a = np.array([[0],                                  [self.r],     [0], [1]]) - self.pivotPoint
        b = np.array([[self.r*math.cos(math.radians(150))], [self.r*0.5], [0], [1]]) - self.pivotPoint
        c = np.array([[self.r*math.cos(math.radians(-150))],[self.r*-0.5],[0], [1]]) - self.pivotPoint
        d = np.array([[0],                                  [-self.r],    [0], [1]]) - self.pivotPoint
        e = np.array([[self.r*math.cos(math.radians(-30))], [self.r*-0.5],[0], [1]]) - self.pivotPoint
        f = np.array([[self.r*math.cos(math.radians(30))],  [self.r*0.5], [0], [1]]) - self.pivotPoint

        aa = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),a))))
        bb = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),b))))
        cc = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),c))))
        dd = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),d))))
        ee = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),e))))
        ff = np.dot(MT(x,y,z),np.dot(MRx(Rx),np.dot(MRy(Ry),np.dot(MRz(Rz),f))))

        Mbc = [[(bb[0]+cc[0])/2],
               [(bb[1]+cc[1])/2],
               [(bb[2]+cc[2])/2],
               [1]]
        Mde = [[(dd[0]+ee[0])/2],
               [(dd[1]+ee[1])/2],
               [(dd[2]+ee[2])/2],
               [1]]
        Mfa = [[(ff[0]+aa[0])/2],
               [(ff[1]+aa[1])/2],
               [(ff[2]+aa[2])/2],
               [1]] 

        Vbc = [[cc[0]-bb[0]],
               [cc[1]-bb[1]],
               [cc[2]-bb[2]]]
        Vde = [[ee[0]-dd[0]],
               [ee[1]-dd[1]],
               [ee[2]-dd[2]]]
        Vfa = [[aa[0]-ff[0]],
               [aa[1]-ff[1]],
               [aa[2]-ff[2]]]

        #Find the position of T1(x,y,-pivotPoint(3))
        s = float(Mbc[0][0])
        t = float(Mbc[1][0])
        u = float(Mbc[2][0] + self.pivotPoint[2][0])
        p = float(Vbc[0][0])
        q = float(Vbc[1][0])
        r = float(Vbc[2][0])

        if p == 0:
            T1y = t + r*u/q
            T1x = s - (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        elif q == 0:
            T1x = s + r*u/p
            T1y = t - (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        else:
            A = 1 + (p/q)**2
            B = 2 * p * r * u / (q**2)
            C = (r * u)**2/(q**2) + u**2 - self.L**2   

            T1x1 = s + 0.5*B/A - 0.5*(B**2-4*A*C)**0.5/A
            T1x2 = s + 0.5*B/A + 0.5*(B**2-4*A*C)**0.5/A
            T1y1 = t + r*u/q + p*s/q - p*T1x1/q
            T1y2 = t + r*u/q + p*s/q - p*T1x2/q

            if T1x1 > T1x2:
                T1x = T1x2
                T1y = T1y2
            else:
                T1x = T1x1
                T1y = T1y1

        #Find the position of T2
        s = float(Mde[0][0])
        t = float(Mde[1][0])
        u = float(Mde[2][0] + self.pivotPoint[2][0])
        p = float(Vde[0][0])
        q = float(Vde[1][0])
        r = float(Vde[2][0])

        if p == 0:
            T2y = t + r*u/q
            T2x = s + (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        elif q == 0:
            T2x = s + r*u/p
            T2y = t - (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        else:
            A = 1 + (p/q)**2
            B = 2 * p * r * u / (q**2)
            C = (r * u)**2/(q**2) + u**2 - self.L**2   

            T2x1 = s + 0.5*B/A - 0.5*(B**2-4*A*C)**0.5/A
            T2x2 = s + 0.5*B/A + 0.5*(B**2-4*A*C)**0.5/A
            T2y1 = t + r*u/q + p*s/q - p*T2x1/q
            T2y2 = t + r*u/q + p*s/q - p*T2x2/q

            if T2x1 < T2x2:
                T2x = T2x2
                T2y = T2y2
            else:
                T2x = T2x1
                T2y = T2y1    

        #Find the position of T3
        s = float(Mfa[0][0])
        t = float(Mfa[1][0])
        u = float(Mfa[2][0] + self.pivotPoint[2][0])
        p = float(Vfa[0][0])
        q = float(Vfa[1][0])
        r = float(Vfa[2][0])

        if p == 0:
            T3y = t + r*u/q
            T3x = s + (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        elif q == 0:
            T3x = s + r*u/p
            T3y = t + (self.L**2-u**2-(r*u)**2/(q**2))**0.5
        else:
            A = 1 + (p/q)**2
            B = 2 * p * r * u / (q**2)
            C = (r * u)**2/(q**2) + u**2 - self.L**2   

            T3x1 = s + 0.5*B/A - 0.5*(B**2-4*A*C)**0.5/A
            T3x2 = s + 0.5*B/A + 0.5*(B**2-4*A*C)**0.5/A
            T3y1 = t + r*u/q + p*s/q - p*T3x1/q
            T3y2 = t + r*u/q + p*s/q - p*T3x2/q

            if T3x1 < T3x2:
                T3x = T3x2
                T3y = T3y2
            else:
                T3x = T3x1
                T3y = T3y1  

        #The T points location at pivot point coordinate
        # Tt = [T1x, T1y, T2x, T2y, T3x, T3y]
        #The T points location at original/center coordinate
        T1x = T1x + self.pivotPoint[0][0]
        T1y = T1y + self.pivotPoint[1][0]
        T2x = T2x + self.pivotPoint[0][0]
        T2y = T2y + self.pivotPoint[1][0]
        T3x = T3x + self.pivotPoint[0][0]
        T3y = T3y + self.pivotPoint[1][0]
        T = [T1x, T1y, T2x, T2y, T3x, T3y]
        return T