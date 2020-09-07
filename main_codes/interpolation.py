
# input data including interpolate point and its value
# grid is the new point where we want the interpolate function solution
# return number P is the solutions at the grid points
def barycenteric_interp(x,f,grid):
    n = len(x)
    m = len(grid)
    P = [0]*m
    w = [0]*n

    # Weight function
    for i in range(0,n):
        a = 1
        for j in range(0,n):
            if j != i:
                a = a * (x[i]-x[j])       
        w[i] = a
    for i in range(0,n):
        w[i] = 1 / w[i]

    # Configure numeritor and denomitor
    for j in range(0,m):
        num = 0
        den = 0
        Flag = 0
        for i in range(0,n):
            if grid[j] == x[i]:
                P[j] = f[i]
                Flag = 1
                break
            else:
                num = num + w[i]*f[i]/(grid[j]-x[i])
                den = den + w[i]/(grid[j]-x[i])
        # Polynomial expression
        if Flag == 0:
            P[j] = num/den

    return P

# input data including interpolate point and its value
# grid is the new point where we want the interpolate function solution
# return number P is the solutions at the grid points
# this is linear interpolation between every two sample data pointsI
# x and y has to be Monotonically Increasing/Decreasing
def linear_interp(x,y,grid):
    lxy = len(x)
    lgrid = len(grid)
    Y = [0]*lgrid
    for i in range(0,lgrid):
        if grid[i] < x[0]:
            Y[i] = (y[1] - y[0]) * (grid[i] - x[0]) / (x[1] - x[0]) + y[0]
            continue
        if grid[i] > x[lxy-1]:
            Y[i] = (y[lxy-1] - y[lxy-2]) * (grid[i] - x[lxy-2]) / (x[lxy-1] - x[lxy-2]) + y[lxy-2]
            continue
        for j in range(1,lxy):
            if grid[i] >= x[j-1] and grid[i] <= x[j]:
                Y[i] = (y[j] - y[j-1]) * (grid[i] - x[j-1]) / (x[j] - x[j-1]) + y[j-1]
                continue
    return Y