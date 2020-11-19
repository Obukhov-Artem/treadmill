
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
#data = pandas.read_csv("Arch/dataOctober 30 12 53 16.csv", sep=";")
import glob
all_files = glob.glob("data/All/*.csv")


X, element = [], []
k = 0.005 / 50
data = None
for f in all_files:
    if data is None:
        data = pd.read_csv(f, sep=";", header=0, index_col=None)
    else:
        df = pd.read_csv(f, sep=";", header=0, index_col=None)
        data = data.append(df)

data = data.values

#
# X = np.array(X)

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
for i in range(1, min(len(body_z),99999)):
    tr_z_body.append(tr_z_body[i - 1] + body_dz[i] + delta_speed[i])
    tr_foot_1.append(tr_foot_1[i - 1] + foot_dz_1[i] + delta_speed[i])
    tr_foot_2.append(tr_foot_2[i - 1] + foot_dz_2[i] + delta_speed[i])

import json
from keras.initializers import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Reshape,Flatten
from keras.layers.recurrent import LSTM
import random, math, time
import numpy as np

from keras.models import load_model

speed_treadmill = 0
delta_z = 0
delta_z0 = 0.05
SHAPE = (7,)





def award_function(z,last_z):
    if z>0:
        if z<last_z:
            return 1
        else:
            return -1
    else:
        if z>last_z:
            return 1
        else:
            return -1

    if abs(z)>1:
        return -10

def buildmodel():
    print("Now we build the model")
    model = Sequential()
    model.add(Dense(100, activation='selu', input_shape=SHAPE))
    model.add(Dense(150, activation='selu'))
    model.add(Dropout(0.3))
    model.add(Dense(50, activation='selu'))
    model.add(Dense(3))
    model.compile(optimizer='adam', loss='mse')
    print("We finish building the model")
    model.summary()
    return model


def training(model):
    speed_treadmill= 0
    action = [-5, 0, 5]
    ITERATION =5000
    exp = []
    final_life = 0
    reward = 0
    while(len(exp)<15100):

        dia = random.randint(2, body_z.shape[0] - 5 - ITERATION)
        start_pos = random.random() * random.choice([-0.1, 0.1])
        z = start_pos+body_dz[0]
        z_foot1 = start_pos+foot_dz_1[0]
        z_foot2 = start_pos+foot_dz_2[0]
        zn = 1
        speed_treadmill= 0
        life = 0
        for j in range(1,body_z.shape[0]):
            life+=1

            last_speed  =speed_treadmill

            last_z = z
            last_delta_z  =body_dz[j-1]+delta_speed[j-1]
            delta_z  =body_dz[j]+delta_speed[j]
            z = z + zn*delta_z-speed_treadmill

            last_z_foot1 = z_foot1
            last_delta_foot1  =foot_dz_1[j-1]+delta_speed[j-1]
            delta_foot1  =foot_dz_1[j]+delta_speed[j]
            z_foot1 = z_foot1 + zn*delta_foot1-speed_treadmill

            last_z_foot2 = z_foot2
            last_delta_foot2  =foot_dz_2[j-1]+delta_speed[j-1]
            delta_foot2  =foot_dz_2[j]+delta_speed[j]
            z_foot2 = z_foot2 + zn*delta_foot2-speed_treadmill


            # if random.random() < 0.1:
            #     current_action = random.choice(action)
            #     p = current_action
            # else:
            p = model.predict(np.array([[z,delta_z,z_foot1,delta_foot1,z_foot2,delta_foot2, speed_treadmill]]))
            index = np.argmax(p)
            current_action = action[index]

            speed_treadmill += current_action*k
            if speed_treadmill >= 1.3/50:
                speed_treadmill = 1.3/50
            if speed_treadmill <= -1.3/50:
                speed_treadmill = -1.3/50
            zn = 1
            if z < 0:
                zn = -1
            if abs(z) < 0.1:
                reward += 2
            elif zn * (z - last_z) < 0:
                reward += 1
            else:
                reward -= 1
            #reward+= award_function(z,last_z)
            #print(j,"z=",z,"speed=",speed_treadmill/k,"r=",reward,"act=",p )
            if abs(z)>2:
                break
            last_vector = [last_z,last_delta_z,last_z_foot1,last_delta_foot1,last_z_foot2,last_delta_foot2,last_speed]
            vector = [z,delta_z,z_foot1,delta_foot1,z_foot2,delta_foot2, speed_treadmill]
            exp.append([last_vector, index, reward, vector])
        final_life = max(final_life,life)
        #print()
        #print()
        #print()

    print(final_life)
    print("z=",z,"speed=",speed_treadmill/k,"r=",reward,"act=",p )
    return exp

def training0(model):
    speed_treadmill= 0
    action = [-5, 0, 5]
    exp = []
    final_life = 0
    reward = 0
    while(len(exp)<20100):

        start_pos = random.random() * random.choice([-0.3, 0.3])
        z = start_pos+body_dz[0]
        z_foot1 = start_pos+foot_dz_1[0]
        z_foot2 = start_pos+foot_dz_2[0]
        zn = 1
        speed_treadmill= 0
        life = 0
        for j in range(1,body_z.shape[0]):
            life+=1

            last_speed  =speed_treadmill

            last_z = z
            last_delta_z  =body_dz[j-1]+delta_speed[j-1]
            delta_z  =body_dz[j]+delta_speed[j]
            z = z + zn*delta_z-speed_treadmill

            last_z_foot1 = z_foot1
            last_delta_foot1  =foot_dz_1[j-1]+delta_speed[j-1]
            delta_foot1  =foot_dz_1[j]+delta_speed[j]
            z_foot1 = z_foot1 + zn*delta_foot1-speed_treadmill

            last_z_foot2 = z_foot2
            last_delta_foot2  =foot_dz_2[j-1]+delta_speed[j-1]
            delta_foot2  =foot_dz_2[j]+delta_speed[j]
            z_foot2 = z_foot2 + zn*delta_foot2-speed_treadmill
            zn = 1
            index = 1
            if z < 0:
                zn = -1
            speed_k = min(255, abs(z * 255)) * k
            if abs(z)<0.1:
                index =1
                if speed_treadmill>0:
                        index = 0
                else:
                    index = 2

            else:
                if speed_k > abs(speed_treadmill):
                    if z>0:
                        index = 2
                    else:
                        index = 0
                else:
                    if z>0:
                        index = 0
                    else:
                        index = 2
                if abs(z)>0.7:
                    if z>0:
                        if speed_treadmill<0:
                            index = 2
                    else:
                        if speed_treadmill>0:
                            index = 0

            current_action = action[index]

            speed_treadmill += current_action*k
            if speed_treadmill >= 1.3/50:
                speed_treadmill = 1.3/50
            if speed_treadmill <= -1.3/50:
                speed_treadmill = -1.3/50
            if abs(z)<0.1:
                reward += 2
            elif zn * (z - last_z) < 0:
                reward += 1
            else:
                reward -= 1
            if abs(z)>2:
                break
            last_vector = [last_z,last_delta_z,last_z_foot1,last_delta_foot1,last_z_foot2,last_delta_foot2,last_speed]
            vector = [z,delta_z,z_foot1,delta_foot1,z_foot2,delta_foot2, speed_treadmill]
            print(j,speed_k/k,"z=",z,"speed=",speed_treadmill/k,"r=",reward,"act=",action[index])
            exp.append([last_vector, index, reward, vector])
        final_life = max(final_life,life)
    return exp


def next_batch(exp, model, num_action, gamma, b_size=1000):
    batch = [exp[i] for i in range(b_size)]
    X = np.zeros((b_size, *SHAPE))
    Y = np.zeros((b_size, num_action))
    for i in range(len(batch)):
        last_vector, a, r, vector = batch[i]
        X[i] = last_vector
        Y[i] = model.predict(np.array([last_vector]))[0]
        Q = np.max(model.predict(np.array([vector]))[0])
        if abs(last_vector[0])<0.3:
            Y[i, a] = r + gamma * Q
        else:
            Y[i, a] = r
    return X, Y


NUM_EPOCH = 500
model = buildmodel()
#model = load_model("testing.h5")
result = []
exp = training0(model)
X, Y = next_batch(exp, model, 3, 0.99, 20000)
model.fit(X, Y,validation_split=0.2,epochs=20,verbose=1)
exp = training0(model)
X, Y = next_batch(exp, model, 3, 0.99, 15000)
model.train_on_batch(X, Y)
for e in range(NUM_EPOCH):
    t = time.time()
    loss = 0.0
    exp = training(model)
    X, Y = next_batch(exp, model, 3, 0.99, 15000)
    loss += model.train_on_batch(X, Y)
    print("*"*25)
    print("---"*10,e, loss, time.time()-t)
    print("*"*25)
    if e%10 == 0:
        result.append([e,loss])
        model.save("qmodel_"+str(e)+".h5")
print(result)
# speed = 0
# action = [-1, 0, 1]
# z = random.random()
# for i in range(500):
#     z = get_z(z, speed)
#     a = np.argmax(model.predict(np.array([z])))
#     speed += action[a]
#     print(z, action[a], speed)
