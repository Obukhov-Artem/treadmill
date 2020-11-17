import numpy as np
import pandas
import random


from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential, Model
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
import matplotlib.pyplot as plt
import time

X,Y = [],[]
epochs = 10
# H.append(h_act)
# X.append([round(z, 4), round(speedh, 3)])  # 1nn+2nn
# X11.append([round(z, 4), round(speedh, 3), speed])  # 1nn+2nn
# Y2.append(status)  # 2nn
# X3.append([round(z, 4), round(speedh, 3), status, speed])  # 3nn
# Y3.append(action)  # 3nn
# S.append(speed)  # 3nn
x_shape = (3,7)
num_action = 3
input_layer3 = Input(shape=x_shape)
h_layer3 = Dense(100, activation='relu')(input_layer3)
h_layer3 = Dense(100, activation='relu')(h_layer3)
h_layer3 = Dropout(0.4)(h_layer3)
h_layer3 = Dense(200, activation='relu')(h_layer3)
h_layer3 = Dense(400, activation='relu')(h_layer3)
result_layer3 = Dense(num_action, activation='sorfmax')(h_layer3)
model = Model(inputs=[input_layer3], outputs=[result_layer3])
model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
model.summary()


history1 = model.fit(X, Y, epochs=epochs, batch_size=128, validation_split=0.25, verbose=1)

name_time = str(time.time())[-4:-1]
model.save("NN_treadmill.h5")


plt.figure(figsize=(14, 5))
r = plt.subplot(1, 3, 1)
plt.grid(True)
plt.plot(np.arange(1, epochs + 1), history1.history["accuracy"], label="accuracy")
plt.xlabel("Эпоха")
plt.ylabel("Точность")
plt.legend(loc="lower left")
r.set_title("Точность нейронной сети прогнозирования", fontsize=12)
r.set_ylim([0, 1])


"""
from keras.models import load_model
model = load_model("NN_treadmill.h5") 



num_ex = 50
from alg import Alg

A = Alg()
s_0 = [i for i in S[:num_ex]]
s_a = []
s_n = []
z_0 = [i[0] for i in X[:num_ex]]
z_a = []
z_n = []
z = X3[h][0]
z2 = X3[h][0]
z2l = X3[h][0]

z2h = X1[0]
dz =0
speed_n = 0
speed_l = 0
action_n = [0, 1, -1]
times = [i for i in range(num_ex)]
for i in range(0,num_ex):
    s = A.main_while(z)
    z = z + shag * H[i] - shag_treadmill * s
    z_bufer = np.array([z2h])
    predict_z = model_1.predict(z_bufer)
    res1 = model_2.predict(predict_z)[0]
    predict_status = np.argmax(res1)

    x3_new = np.array([[predict_z[0][0], dz, action_n[predict_status], speed_n]])

    res2 = model_3.predict(x3_new)[0]
    predict_action = np.argmax(res2) - 2*(max_speed/speed_temp)
    # print(predict_action,Y3[i], x3_new)
    speed_n += predict_action*speed_temp
    if speed_n > max_speed:
        speed_n = max_speed
    if speed_n < -max_speed:
        speed_n = -max_speed

    z2 = z2 + shag * H[i] - shag_treadmill * speed_n
    #print(z2,speed_n)
    dz = z2 - z2l
    z2h = np.append(z2h[1:], [[z2, dz,speed_n]], axis=0)

    z2l = z2

    z_a.append(z)
    s_a.append(s)
    z_n.append(z2)
    s_n.append(speed_n)

E = sum(i for i in z_0 if i > 0) - sum(i for i in z_0 if i < 0)
EA = sum(i for i in z_a if i > 0) - sum(i for i in z_a if i < 0)
EN = sum(i for i in z_n if i > 0) - sum(i for i in z_n if i < 0)
print(E, E / num_ex)
print(EA, EA / num_ex)
print(EN, EN / num_ex)
plt.figure(figsize=(14, 9))
plt.plot(times, z_0, "--",label="Эталон",linewidth=2, color="#ababab")
plt.plot(times, z_a, ":",label="Классический метод",linewidth=5, color="#777777")
plt.plot(times, z_n, "-",label="Нейросетевой метод",linewidth=2, color="black")
plt.legend()
plt.ylabel("Положение объекта")
plt.xlabel("Время")
plt.title("Анализ положения объекта")
plt.grid(True)

plt.savefig('compare1.png', dpi=300)
plt.show()


plt.figure(figsize=(14, 9))
plt.plot(times, s_0, "--",label="Эталон",linewidth=2, color="#ababab")
plt.plot(times, s_a, ":",label="Классический метод",linewidth=5, color="#777777")
plt.plot(times, s_n, "-",label="Нейросетевой метод",linewidth=2, color="black")
plt.legend()
plt.ylabel("Скорость системы")
plt.xlabel("Время")
plt.title("Анализ скорости системы")
plt.grid(True)
plt.savefig('compare2.png', dpi=300)
plt.show()
#      print("s=",s)
#      print("-"*22)

# for i in range(10):
#     print(X1[i],Y1[i])
#     print()
#     print(X[i],Y2[i])
#     print()
#     print(X3[i],Y3[i])
#     print()
#     print("-"*22)

"""