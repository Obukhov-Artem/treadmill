from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential, Model
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
import pandas
import random
import numpy as np

data = pandas.read_csv("data.csv", sep=";")


X = data.values[:, :6]
X_new = np.asarray([data.values[i:i+10,:6] for i in range(len(X) - 10 )])
X = X_new[:5900,  :]
Y_1 = X_new[5:5905,  :]
Y_2 = data.values[:5900,  6:7]

input_layer = Input(shape=(10, 6,))
h_layer1 = Dense(100, activation='linear')(input_layer)
h_layer2 = Flatten()(h_layer1)
h_layer3 = Dense(50, activation='linear')(h_layer2)
h_layer4 = Dropout(0.2)(h_layer3)
h_layer5 = Dense(100, activation='linear')(h_layer4)
h_layer6 = Dense(60, activation='linear')(h_layer5)
result_layer = Reshape((10, 6))(h_layer6)
model_predict = Model(inputs=[input_layer], outputs=[result_layer])
model_predict.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
model_predict.summary()


input_layer = Input(shape=(10, 6,))
h_layer1 = Dense(100, activation='relu')(input_layer)
h_layer2 = Flatten()(h_layer1)
h_layer3 = Dense(50, activation='relu')(h_layer2)
h_layer4 = Dropout(0.2)(h_layer3)
h_layer5 = Dense(100, activation='relu')(h_layer4)
h_layer6 = Dense(10, activation='relu')(h_layer5)
result_layer = Dense(1, activation="relu")(h_layer6)
model_speed = Model(inputs=[input_layer], outputs=[result_layer])
model_speed.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
model_speed.summary()



import matplotlib.pyplot as plt

 
hh1 = model_predict.fit(X, Y_1, epochs=10, batch_size=32, validation_split=0.25, verbose=1)
hh2 = model_speed.fit(X, Y_2, epochs=10, batch_size=32, validation_split=0.25, verbose=1)
plt.figure()
N = 10
plt.grid(True)
plt.plot(np.arange(1, N + 1), hh1.history["loss"], label="Модель прогнозирования движений (Ошибка)", color="#00ff00",linewidth =3)
# plt.plot(np.arange(1, N+1), history.history["accuracy"], label="accuracy")
plt.xlabel("Эпоха")
plt.ylabel("Ошибка")
plt.legend(loc="lower left")
plt.show()

plt.figure()
plt.grid(True)
plt.plot(np.arange(1, N + 1), hh1.history["acc"], label="Модель прогнозирования движений (Точность)", color="#ff0000",linewidth =3)
plt.xlabel("Эпоха")
plt.ylabel("Точность")
plt.legend(loc="lower right")
plt.show()

plt.figure()
N = 10
plt.grid(True)
plt.plot(np.arange(1, N + 1), hh2.history["loss"], label="Модель распознавания движений  (Ошибка)", color="#00ff00",linewidth =3)
# plt.plot(np.arange(1, N+1), history.history["accuracy"], label="accuracy")
plt.xlabel("Эпоха")
plt.ylabel("Ошибка")
plt.legend(loc="lower left")
plt.show()

plt.figure()
plt.grid(True)
plt.plot(np.arange(1, N + 1), hh2.history["acc"], label="Модель распознавания движений  (Точность)", color="#ff0000",linewidth =3)
plt.xlabel("Эпоха")
plt.ylabel("Точность")
plt.legend(loc="lower right")
plt.show()

input_layer = Input(shape=(10, 6,))
h1 = model_predict(input_layer)
result_layer = model_speed(h1)
speed_predict = Model(inputs=input_layer, outputs=result_layer)
speed_predict.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
speed_predict.summary()

import time
name_time = str(time.time())[-4:-1]
model_predict.save("NN_model_predict"+name_time+".h5")
model_speed.save("NN_model_speed"+name_time+".h5")
speed_predict.save("NN_speed_predict"+name_time+".h5")
