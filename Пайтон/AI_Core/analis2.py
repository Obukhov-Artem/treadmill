import pandas
import matplotlib.pyplot as plt
import numpy as np
data = pandas.read_csv("two side.csv", sep=";")

moving = False

def alg_lin_1(z):
    max_speed = 255
    tr_len = 1
    safe_zona = 0.15
    if z < 0:
        zn = -1
    else:
        zn = 1
    z = abs(z)
    if z < safe_zona:
        return 0
    elif safe_zona <= z <= tr_len:
        delta = tr_len - safe_zona
        if z * 255 <= max_speed:
            speed = (z - safe_zona) * max_speed / (delta)
            if speed < 25:
                speed = 25

            return zn * min(max_speed, speed)
        else:

            return zn * max_speed
    elif z > tr_len:
        return zn * max_speed
    else:
        return 0

def alg_lin_2(z):
    global moving
    max_speed = 255
    tr_len = 1
    safe_zona = 0.15
    if z < 0:
        zn = -1
    else:
        zn = 1
    z = abs(z)
    if moving:
        if z < safe_zona / 2:
            moving = False
            return 0
        elif safe_zona / 2 <= z <= safe_zona:
            delta = tr_len - safe_zona
            speed = (z - safe_zona / 2) * max_speed / (delta)
            if 0 < speed < 40:
                speed = 40
            else:
                speed = min(90, speed)  # testing!!!

            return zn * min(max_speed, speed)
        elif safe_zona <= z <= tr_len:

            delta = tr_len - safe_zona
            if z * 255 <= max_speed:
                speed = (z - safe_zona / 2) * max_speed / (delta)

                # print("work zona")
                return zn * min(max_speed, speed)
            else:

                # print("far zona speed")
                return zn * max_speed
        elif z > tr_len:
            # print("far zona")
            return zn * max_speed
        else:
            return 0
    else:
        if z < safe_zona:
            return 0
        elif safe_zona <= z <= tr_len:
            moving = True
            delta = tr_len - safe_zona
            if z * 255 <= max_speed:
                speed = (z - safe_zona) * max_speed / (delta)
                if speed < 5:
                    safe_zona = 0

                # print("work zona")
                return zn * min(max_speed, speed)
            else:

                # print("far zona speed")
                return zn * max_speed
        else:
            return 0
from keras.models import load_model

def nn(z,speed,model):
    action = [-10, 0, 10]
    a = np.argmax(model.predict(np.array([z])))

    return speed+action[a]

NN = load_model("testing_new.h5")
data = data.values
print(data.shape)
body_z = data[:,2]
body_dz = data[:,8]
speed_treadmill = data[:,27]*0.005
delta_speed = data[:,27]*(0.005/50)
foot_z_1 = data[:,11]
foot_z_2 = data[:,20]
foot_dz_1 = (data[:,17])
foot_dz_2 = (data[:,26])
foot_dz_all = (data[:,17]+data[:,26])
tr_z_body = [body_z[0]]
alg_1_z_body = [body_z[0]]

alg_1_speed_treadmill = [0]
alg_2_z_body = [body_z[0]]

alg_2_speed_treadmill = [0]
tr_foot_1 = [foot_z_1[0]]
tr_foot_2 = [foot_z_2[0]]
foot_dz_all = [0]
foot_dz_all2 = [0]
new_speed = []
h = 20
my_speed = 0
for i in range(1,len(body_z)):
    tr_z_body.append(tr_z_body[i-1]+body_dz[i]+delta_speed[i])
    speed = alg_lin_1(alg_1_z_body[i-1])
    alg_1_speed_treadmill.append(speed*0.005)
    alg_1_z_body.append(alg_1_z_body[i-1]+body_dz[i]+delta_speed[i]-speed*(0.005/50))

    my_speed = nn(alg_2_z_body[i-1],my_speed,NN)
    alg_2_speed_treadmill.append(my_speed*0.005)
    alg_2_z_body.append(alg_2_z_body[i-1]+body_dz[i]+delta_speed[i]-my_speed*(0.005/50))


    tr_foot_1.append(tr_foot_1[i-1]+foot_dz_1[i]+delta_speed[i])
    tr_foot_2.append(tr_foot_2[i-1]+foot_dz_2[i]+delta_speed[i])
    m_foot = max([(j) for j in foot_dz_1[i:max(i-h,0):-1]]+[(j) for j in foot_dz_2[i:max(i-h,0):-1]])
    m_foot2 = max([abs(j) for j in foot_dz_1[i:max(i-h,0):-1]]+[abs(j) for j in foot_dz_2[i:max(i-h,0):-1]])
    foot_dz_all.append(m_foot)
    foot_dz_all2.append(m_foot2)
foot_dz_all = np.array(foot_dz_all)
print(foot_dz_all[:5])
graph = True
x=[i/50 for i in range(len(body_z))]
#plt.plot(range(len(body_z)),body_z)
if graph:

    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    # ax.plot(x, body_z, color='orange',label="body_z")
    #ax1.plot(x, speed_treadmill, color='red',label="speed_treadmill")
    ax.plot(x, alg_1_z_body, color='orange',label="alg_1_z_body")
    ax.plot(x, alg_2_z_body, color='green',label="alg_2_z_body")
    ax1.plot(x, alg_1_speed_treadmill, color='red',label="alg_1_speed_treadmill")
    ax1.plot(x, alg_2_speed_treadmill, color='blue',label="alg_2_speed_treadmill")
    ax.set_ylabel('Z')
    ax1.set_ylabel('speed treadmill')
    ax.set_title("Положение человека на дорожке")
    fig.legend()
    plt.show()
else:
    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    ax.plot(x, tr_z_body, color='r')
    ax1.plot(x, speed_treadmill, color='b')
    ax.set_ylabel('Z')
    ax1.set_ylabel('speed treadmill')

    ax.set_title("Положение человека в пространстве без учета сдвига дорожки")
    plt.show()
    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    ax.plot(x, foot_z_1, color='r')
    ax.plot(x, foot_z_2, color='g')
    ax1.plot(x, speed_treadmill, color='b')
    ax1.set_ylabel('speed treadmill')
    ax.set_ylabel('Z')
    ax.set_title("Положение ног на дорожке")
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
    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    # ax.plot(x,foot_dz_1,color='r')
    # ax.plot(x,foot_dz_2,color='g')
    ax.plot(x, body_z, color='r')
    ax.plot(x, foot_z_1, color='y')
    ax.plot(x, foot_dz_all, color='black')
    #ax.plot(x, new_speed, color='g')
    ax1.plot(x, speed_treadmill, color='b')
    ax.set_ylabel('Z')
    ax1.set_ylabel('speed treadmill')
    ax.set_title("Скорость ног на дорожке ")
    plt.show()



