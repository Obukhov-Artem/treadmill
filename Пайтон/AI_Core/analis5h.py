import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
# data = pandas.read_csv("Arch/dataOctober 30 12 53 16.csv", sep=";")
import glob
# аналог анализ5, но используется несколько предыдущих значений траектории длиной H.
# Эффективность не доказана
all_files = glob.glob("data/All/*.csv")

X, element = [], []
k = 0.005 / 50
H = 10
data = None
for f in all_files:
    if data is None:
        data = pd.read_csv(f, sep=";", header=0, index_col=None)
    else:
        df = pd.read_csv(f, sep=";", header=0, index_col=None)
        data = data.append(df)

data = data.values

for i in data[:, :29]:
    X.append([i[-2] * k, i[2], i[11], i[20], i[8], i[17], i[26]])

X = np.array(X)

nn_data = []
k = (0.005 / 50)

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

nn_speed_treadmill = [0]

new_speed = []
for i in range(1, min(len(body_z), 99999)):
    tr_z_body.append(tr_z_body[i - 1] + body_dz[i] + delta_speed[i])
    tr_foot_1.append(tr_foot_1[i - 1] + foot_dz_1[i] + delta_speed[i])
    tr_foot_2.append(tr_foot_2[i - 1] + foot_dz_2[i] + delta_speed[i])

import json
from keras.initializers import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Reshape, Flatten
from keras.layers.recurrent import LSTM, GRU
import random, math, time
import numpy as np

from keras.models import load_model

speed_treadmill = 0
delta_z = 0
delta_z0 = 0.05
SHAPE = (H,3,)


def award_function(z, last_z):
    if abs(z) <= 0.1:
        return 1
    if abs(z) > 1.1:
        return -10
    if z > 0:
        if z < last_z:
            return 0.5
        else:
            return -1
    else:
        if z > last_z:
            return 0.5
        else:
            return -1


def buildmodel():
    print("Now we build the model")
    model = Sequential()
    model.add(Dense(100, activation='relu', input_shape=SHAPE))
    model.add(Flatten())
    model.add(Dense(200, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(3))
    model.compile(optimizer='adam', loss='mse')
    print("We finish building the model")
    model.summary()
    return model

def buildmodel_lstm():
    print("Now we build the lstm model")
    model = Sequential()
    model.add(GRU(32,
                         dropout=0.1,
                         recurrent_dropout=0.5,
                         return_sequences=True,
                         input_shape=SHAPE))
    model.add(GRU(64, activation='relu',
                         dropout=0.1,
                         recurrent_dropout=0.5))
    model.add(Flatten())
    model.add(Dense(200, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(3))
    model.compile(optimizer='adam', loss='mse')
    print("We finish building the model")
    model.summary()
    return model


def training(model):
    speed_treadmill = 0
    action = [-1, 0, 1]
    ITERATION = 4000
    exp = []
    final_life = 0

    while (len(exp) < 12000):

        # dia = random.randint(2, body_z.shape[0] - 5 - ITERATION)
        z = random.random() * random.choice([-0.2, 0.2])
        zn = random.choice([1, -1])
        speed_treadmill = 0
        life = 0
        reward = 0
        data = []
        for j in range(body_z.shape[0]):
            life += 1
            last_z = z
            last_delta_z = body_dz[j - 1] +  [j - 1]
            last_speed = speed_treadmill
            delta_z = body_dz[j] + delta_speed[j]

            z = z + zn * delta_z - speed_treadmill
            if len(data) <  H :
                speed_treadmill = 0
            else:


                # p = model.predict(np.array([[z, delta_z, speed_treadmill]]))
                p = model.predict(np.array([data[j-H:j]]))
                current_action = action[np.argmax(p)]

                speed_treadmill += current_action * k
            if speed_treadmill >= 1.3:
                speed_treadmill = 1.3
            if speed_treadmill <= -1.3:
                speed_treadmill = -1.3
            reward += award_function(z, last_z)
            data.append([z, delta_z, speed_treadmill])


            if abs(z) > 2:
                break
            # exp.append([last_z, last_delta_z, last_speed, current_action, reward, z, delta_z, speed_treadmill])
            if len(data) >= H+2:
                exp.append([data[j-H-1:j-1], current_action, reward,data[j-H:j]])
        final_life = max(final_life, life)

    print(final_life)
    return exp


def next_batch(exp, model, num_action, gamma, b_size=1000):
    batch = [exp[i] for i in range(b_size)]
    X = np.zeros((b_size, *SHAPE))
    Y = np.zeros((b_size, num_action))
    for i in range(len(batch)):
        last_data, a, r, cur_data = batch[i]
        X[i] = last_data
        Y[i] = model.predict(np.array([last_data]))[0]
        Q = np.max(model.predict(np.array([cur_data]))[0])
        if abs(last_data[-1][0]) > 1:
            Y[i, a] = r
        else:
            Y[i, a] = r + gamma * Q
    return X, Y


NUM_EPOCH = 500
model = buildmodel()
# model = load_model("testing.h5")
result = []
for e in range(NUM_EPOCH):
    t = time.time()
    loss = 0.0
    #lz, ldz, ls, a, r, z, d_z, s_t = 0, 0, 0, 0, 0, 0, 0, 0
    exp = training(model)
    X, Y = next_batch(exp, model, 3, 0.99, 10000)
    loss += model.train_on_batch(X, Y)
    print("*" * 10, e, loss, time.time() - t)
    print("*" * 25)
    if e % 10 == 0:
        result.append([e, loss])
        model.save("qmodel_" + str(e) + ".h5")
print(result)
# speed = 0
# action = [-1, 0, 1]
# z = random.random()
# for i in range(500):
#     z = get_z(z, speed)
#     a = np.argmax(model.predict(np.array([z])))
#     speed += action[a]
#     print(z, action[a], speed)
