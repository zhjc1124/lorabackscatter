import time, datetime
import numpy as np
from math import sin, cos, sqrt, atan2, radians


def distance(a, b):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = a[0]
    lon1 = a[1]
    lat2 = b[0]
    lon2 = b[1]

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000
    return distance


# with open('2020-09-30_11-50-16.log') as f:
#     lines = f.readlines()

# timestamps = []
# for line in lines:
#     times = line.split(',')[0]
#     timearray = time.strptime(times, "%Y-%m-%d_%H:%M:%S")
#     timestamp = int(time.mktime(timearray))
#     timestamps.append(timestamp)


# for i in range(len(timestamps)-1):
#     if timestamps[i+1] - timestamps[i] != 1:
#         print(i, timestamps[i], timestamps[i+1])


with open('1601437824_840462.txt') as f:
    lines = f.readlines()


standardp = [float(lines[0].split(',')[0]), float(lines[0].split(',')[1])]
standardh = float(lines[0].split(',')[2])
ps = []
hs = []
vs = []
ds = []
for line in lines:
    ps.append(distance(standardp, [float(line.split(',')[0]), float(line.split(',')[1])]))
    hs.append(float(line.split(',')[2])-standardh)
    vs.append(float(line.split(',')[4]))
    ds.append(sqrt(ps[-1]**2+hs[-1]**2))


print(max(ps))
print(max(hs))
print(max(ds), vs[np.argmax(ds)])
print(max(vs), ds[np.argmax(vs)])
