import pandas
import matplotlib.pyplot as plt
import numpy as np

#data = pandas.read_csv("data\Kirill\dataOctober 30 13 06 51.csv", sep=";")
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


def nn(z, speed, model):
    action = [-1, 0, 1]
    p = model.predict(np.array([z]))
    a = np.argmax(p)
    # print(speed,p, z)
    # print("*"*10)
    if speed + action[a]>255:
        return 255
    if speed + action[a]<-255:
        return -255
    return speed + action[a]

def nn2(z,d_z, speed, model):
    action = [-1, 0, 1]
    p = model.predict(np.array([[z,d_z, speed]]))
    a = action[np.argmax(p)]
    speed += a * 0.005
    if speed >= 1.3:
        speed = 1.3
    if speed <= -1.3:
        speed = -1.3
    print(speed, z, d_z,p)
    return speed


def get_data(data,new_body, new_foot_1,new_foot_2, speed):
    k = (0.005 / 50)
    data[0][0] = speed*k
    data[1][0] = speed*k
    data[2][0] = speed*k
    data[0][3] = new_body
    data[1][3] = new_foot_1
    data[2][3] = new_foot_2
    return data


NN = load_model("testing_new.h5")
data = data.values
nn_data = []
k = (0.005 / 50)
for i in data[:, :29]:
    t11 = np.concatenate(([i[-2] * k], i[0:3], i[6:9]))
    t12 = np.concatenate(([i[-2] * k], i[9:12], i[15:18]))
    t13 = np.concatenate(([i[-2] * k], i[18:21], i[24:27]))
    nn_data.append([t11, t12, t13])

nn_data = np.array(nn_data)


print(data.shape)
body_z = data[:, 2]
body_dz = data[:, 8]
speed_treadmill = data[:, 27] * 0.005
delta_speed = data[:, 27] * (0.005 / 50)
foot_z_1 = data[:, 11]
foot_z_2 = data[:, 20]
foot_dz_1 = (data[:, 17])
foot_dz_2 = (data[:, 26])
foot_dz_all = (data[:, 17] + data[:, 26])
tr_z_body = [body_z[0]]
alg_1_z_body = [body_z[0]]
nn_body = [body_z[0]]

tr_foot_1 = [foot_z_1[0]]
tr_foot_2 = [foot_z_2[0]]
nn_foot_1 = [foot_z_1[0]]
nn_foot_2 = [foot_z_2[0]]

alg_1_speed_treadmill = [0]

nn_speed_treadmill = [0]

foot_dz_all = [0]
foot_dz_all2 = [0]
new_speed = []
h = 20
my_speed = 0
NUM =4000
for i in range(1, min(len(body_z),NUM)):
    tr_z_body.append(tr_z_body[i - 1] + body_dz[i] + delta_speed[i])
    tr_foot_1.append(tr_foot_1[i - 1] + foot_dz_1[i] + delta_speed[i])
    tr_foot_2.append(tr_foot_2[i - 1] + foot_dz_2[i] + delta_speed[i])



    speed = alg_lin_1(alg_1_z_body[i - 1])

    alg_1_speed_treadmill.append(speed * 0.005)
    alg_1_z_body.append(alg_1_z_body[i - 1] + body_dz[i] + delta_speed[i] - speed * (0.005 / 50))


    #z = get_data(nn_data[i-1],nn_body[i-1],nn_foot_1[-1],nn_foot_2[-1], my_speed)

    # speed, z, z_f1,z_f2, dz, dz_f1,dz_f2 = 7
    # my_speed = nn(np.array([my_speed,nn_body[i - 1],nn_foot_1[i - 1],nn_foot_2[i - 1],
    #                        body_dz[i], foot_dz_1[i], foot_dz_2[i]]), my_speed, NN)
    # #my_speed = nn(z, my_speed, NN)
    my_speed = nn2(nn_body[i - 1], body_dz[i], my_speed, NN)

    nn_speed_treadmill.append(my_speed)
    new_body = nn_body[i - 1] + body_dz[i] + delta_speed[i] - my_speed/50
    new_foot_1 = nn_foot_1[i - 1] + foot_dz_1[i] + delta_speed[i] - my_speed/50
    new_foot_2 = nn_foot_2[i - 1] + foot_dz_2[i] + delta_speed[i] - my_speed/50

    nn_body.append(new_body)
    nn_foot_1.append(new_foot_1)
    nn_foot_2.append(new_foot_2)

    # m_foot = max([(j) for j in foot_dz_1[i:max(i - h, 0):-1]] + [(j) for j in foot_dz_2[i:max(i - h, 0):-1]])
    # m_foot2 = max([abs(j) for j in foot_dz_1[i:max(i - h, 0):-1]] + [abs(j) for j in foot_dz_2[i:max(i - h, 0):-1]])
    # foot_dz_all.append(m_foot)
    # foot_dz_all2.append(m_foot2)
foot_dz_all = np.array(foot_dz_all)
print(foot_dz_all[:5])
graph = True
x = [i / 50 for i in range(min(len(body_z),NUM))]
# plt.plot(range(len(body_z)),body_z)
if graph:

    fig, ax = plt.subplots()
    ax1 = ax.twinx()
    # ax.plot(x, body_z, color='orange',label="body_z")
    # ax1.plot(x, speed_treadmill, color='red',label="speed_treadmill")
    ax.plot(x, tr_z_body, color='yellow', label="tr_z_body")
    ax.plot(x, alg_1_z_body, color='orange', label="alg_1_z_body")
    ax.plot(x, nn_body, color='red', label="nn_z_body")
    ax1.plot(x, alg_1_speed_treadmill, color='green', label="alg_1_speed_treadmill")
    ax1.plot(x, nn_speed_treadmill, color='blue', label="nn_speed_treadmill")
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
    ax.plot(x, tr_foot_1, color='r')
    ax.plot(x, tr_foot_2, color='g')
    ax1.plot(x, speed_treadmill, color='b')
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
    # ax.plot(x, new_speed, color='g')
    ax1.plot(x, speed_treadmill, color='b')
    ax.set_ylabel('Z')
    ax1.set_ylabel('speed treadmill')
    ax.set_title("Скорость ног на дорожке ")
    plt.show()
