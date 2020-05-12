
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
