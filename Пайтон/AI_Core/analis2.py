import pandas
data = pandas.read_csv("Kirill\dataOctober 30 13 13 46.csv", sep=";")
data = data.values
print(data.shape)
body_z = data[:,2]
body_dz = data[:,8]
speed_treadmill = data[:,27]*0.005
delta_speed = data[:,27]*(0.005/50)
foot_z_1 = data[:,11]
foot_z_2 = data[:,20]
foot_dz_1 = (data[:,17]+delta_speed)
foot_dz_2 = (data[:,26]+delta_speed)
tr_z_body = [body_z[0]]
tr_foot_1 = [foot_z_1[0]]
tr_foot_2 = [foot_z_2[0]]
for i in range(1,len(body_z)):
    tr_z_body.append(tr_z_body[i-1]+body_dz[i]+delta_speed[i])
    tr_foot_1.append(tr_foot_1[i-1]+foot_dz_1[i]+delta_speed[i])
    tr_foot_2.append(tr_foot_2[i-1]+foot_dz_2[i]+delta_speed[i])

import matplotlib.pyplot as plt
import numpy as np

#plt.plot(range(len(body_z)),body_z)

x=[i/50 for i in range(len(body_z))]
fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(x,body_z,color='r')
ax1.plot(x,speed_treadmill,color='b')
ax.set_ylabel('Z')
ax1.set_ylabel('speed treadmill')
ax.set_title("Положение человека на дорожке")
plt.show()

fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(x,tr_z_body,color='r')
ax1.plot(x,speed_treadmill,color='b')
ax.set_ylabel('Z')
ax1.set_ylabel('speed treadmill')

ax.set_title("Положение человека в пространстве без учета сдвига дорожки")
plt.show()
fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(x,foot_z_1,color='r')
ax.plot(x,foot_z_2,color='g')
ax1.plot(x,speed_treadmill,color='b')
ax1.set_ylabel('speed treadmill')
ax.set_ylabel('Z')
ax.set_title("Положение ног на дорожке")
plt.show()

fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(x,foot_dz_1,color='r')
ax.plot(x,foot_dz_2,color='g')
ax1.plot(x,speed_treadmill,color='b')
ax.set_ylabel('Z')
ax1.set_ylabel('speed treadmill')
ax.set_title("Скорость ног на дорожке на дорожке")
plt.show()



fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(x,tr_foot_1,color='r')
ax.plot(x,tr_foot_2,color='g')
ax1.plot(x,speed_treadmill,color='b')
ax.set_ylabel('Z')
ax1.set_ylabel('speed treadmill')

ax.set_title("Положение ног в пространстве без учета сдвига дорожки")
plt.show()
# d = {}
# k = {}
# for i in range(data.shape[0]):
#     key = data[i][9]
#     d[key] = d.get(key,0)+data[i][12]
#     k[key] = k.get(key,0)+1
#
# res = {}
# for i in d.keys():
#     res[i] = d[i]/k[i]
# del res[0.0]
# t = len(res.keys())
# ssum = 0
# import matplotlib.pyplot as plt
# plt.scatter(res.keys(), res.values())
# plt.show()
# y = []
# for i in res.keys():
#     print(i,res[i])
#     y.append(res[i]/abs(i))
# print(sum(y)/t)
#
# plt.bar(res.keys(),y)
# plt.show()