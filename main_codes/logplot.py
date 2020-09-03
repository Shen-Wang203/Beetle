import matplotlib.pyplot as plt
f = open('runlog\curing79.txt', 'r')
fetch = True
loss = []
loss_minute = []
time = []
pausetime = 0
pauseloss = 0
for line in f:
    if line[10] == '-' and fetch:
        if float(line[10:18]) < -0.6:
            continue
        loss.append(float(line[10:18]))
        loss_minute.append(float(line[10:18]))
        continue
    if line[22:26] == 'ends':
        fetch = True
        continue
    elif line[22:26] == 'star':
        fetch = False
        continue
    elif line[10:14] == 'Meet':
        fetch = True
        continue
    if line[10:14] == 'Time':
        if line[17] == 'm':
            minute = int(line[16]) - 1
        else:
            minute = int(line[16:18]) - 1
        for i in range(0,len(loss_minute)):
            time.append(minute*60 + i * 60/len(loss_minute))
        loss_minute = []
        continue
    if line[18:24] == 'stable' or line[10:15] == 'Pause':
        pauseloss = loss[-1]
        pausetime = len(loss)
        fetch = True

pausetime = time[pausetime-1]
for i in range(0,len(loss)-len(time)):
    time.append(time[-1] + 0.5)

plt.plot(time, loss)
plt.xlabel('Time(s)')
plt.ylabel('IL(dB)')
plt.title('Curing #79 Loss vs Time')
plt.grid()
# yticks for curing25
# plt.yticks([-0.60, -0.55, -0.50, -0.45, -0.40])
if pauseloss != 0:   
    plt.plot(pausetime, pauseloss, 'o')
plt.show()