import interpolation
import matplotlib.pyplot as plt
loss = [-1.4031,-1.3295,-1.247,-1.1969,-1.1528,-1.1302,-1.0559,-1.0173,-0.9505,-0.8985,-0.8521,-0.7902,-0.726,-0.6927,-0.6528,-0.6005,-0.582,-0.5429,-0.4965,-0.4796,-0.4584,-0.4377,-0.4085,-0.4006,-0.3906,-0.3733,-0.362,-0.3584,-0.3461,-0.3493];
pos = [12460,12468,12476,12484,12492,12500,12508,12516,12524,12532,12540,12548,12556,12564,12572,12580,12588,12596,12604,12612,12620,12628,12636,12644,12652,12660,12668,12676,12684,12692]



# go back to the overall best point using interp method
grid = [*range(int(min(pos)), int(max(pos))+1, 1)]  
s = interpolation.barycenteric_interp(pos, loss, grid)
print(grid[s.index(max(s))])
plt.plot(pos, loss, 'r')
# plt.plot(grid, s, 'b--')
plt.show()