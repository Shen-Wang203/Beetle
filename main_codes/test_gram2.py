a = [20,2,54,586,18,35]
i = 0

a.append(a[-1]+3)
print(a)
print(len(a))
while i < len(a):
    i += 1
    if a[i-1] > a[0]:
        a.pop(i)
    print(a)