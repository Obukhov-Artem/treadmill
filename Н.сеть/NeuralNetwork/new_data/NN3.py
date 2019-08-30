from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential, Model
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
import pandas
import random
import numpy as np
import glob
"""
all_files = glob.glob("*.csv")

li = []

for filename in all_files:
    df = pandas.read_csv(filename, sep=";")
    li.append(df)

data = pandas.concat(li, axis=0, ignore_index=True)
print(data.shape)
"""
data = pandas.read_csv("test.csv", sep=";")
X = data.values[:, :6]
X_new = []
for i in range(1,X.shape[0]):
    current = []
    for j in range(0,6):
        current.append(X[i,j]-X[i-1,j])
    X_new.append(current)
X_new = np.array(X_new)
SAMPLES = 5
X = np.asarray([X_new[i:i+SAMPLES,:6] for i in range(X.shape[0] - SAMPLES )])
print()
X = X[:X.shape[0],  :]
print(X[0],X[1])
print(X.shape)
X_predict = X[:X.shape[0]- SAMPLES*4,  :]
X_speed = np.asarray([X_new[i:i+SAMPLES*3,:6] for i in range(X.shape[0] - SAMPLES*3 )])
Y_speed = to_cat(data.values[SAMPLES*3:X.shape[0] ,  6:7],4)
Y_predict = np.asarray([X_new[i:i+SAMPLES*3,:6] for i in range(SAMPLES, X.shape[0] - SAMPLES*3 )])
#print(X.shape,Y_1.shape,Y_2.shape)
print(X.shape,X_speed.shape,Y_speed.shape, X_predict.shape, Y_predict.shape)

input_layer = Input(shape=(SAMPLES, 6,))
h_layer1 = Dense(100, activation='linear')(input_layer)
h_layer2 = Flatten()(h_layer1)
h_layer3 = Dense(50, activation='linear')(h_layer2)
h_layer4 = Dropout(0.1)(h_layer3)
h_layer5 = Dense(100, activation='linear')(h_layer4)
h_layer6 = Dense(SAMPLES*3*6, activation='linear')(h_layer5)
result_layer = Reshape((SAMPLES*3, 6))(h_layer6)
model_predict = Model(inputs=[input_layer], outputs=[result_layer])
model_predict.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
model_predict.summary()


input_layer = Input(shape=(SAMPLES*3, 6,))
h_layer1 = Dense(100, activation='relu')(input_layer)
h_layer2 = Flatten()(h_layer1)
h_layer3 = Dense(100, activation='relu')(h_layer2)
h_layer4 = Dropout(0.1)(h_layer3)
h_layer5 = Dense(100, activation='relu')(h_layer4)
result_layer = Dense(4, activation="softmax")(h_layer5)
model_speed = Model(inputs=[input_layer], outputs=[result_layer])
model_speed.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model_speed.summary()


model_speed.fit(X_speed, Y_speed, epochs=15, batch_size=64, validation_split=0.20, verbose=1)

 
model_predict.fit(X_predict, Y_predict, epochs=15, batch_size=64, validation_split=0.20, verbose=1)
"""
input_layer = Input(shape=(SAMPLES, 6,))
h1 = model_predict(input_layer)
result_layer = model_speed(h1)
speed_predict = Model(inputs=input_layer, outputs=result_layer)
speed_predict.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
speed_predict.summary()
"""
import time
name_time = str(time.time())[-5:-1]
model_predict.save("NN_predict"+name_time+".h5")
model_speed.save("NN_speed"+name_time+".h5")
#speed_predict.save("NN_speed_predict"+name_time+".h5")
