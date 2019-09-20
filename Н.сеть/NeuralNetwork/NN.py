from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
import pandas
import random
import numpy as np

data = pandas.read_csv("data.csv", sep=";")


X = data.values[:,  1:6:3]
X_new = np.asarray([data.values[i:i+10, 1:6:3] for i in range(len(X) - 10 )])
Y = data.values[:5990,  6:7]
print(X_new.shape, X_new[5000],Y[5000])
X = X_new
print(Y.shape, Y[0])
#variant 3


X = data[:, 0:6]
X = X.reshape((-1, 10, 6))
Y = data[1:61, 0:6]
Y = Y.reshape((-1, 10, 6))
print(Y)
X_train, Y_train, X_test, Y_test = X[:5000],Y[:5000],X[5000:],Y[5000:5990]
model = Sequential()
model.add(Dense(100, activation="relu", input_shape=(10, 2,)))
model.add(Flatten())
model.add(Dense(50, activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(100, activation="relu"))
model.add(Dense(10, activation="relu"))
model.add(Dense(1, activation="sigmoid"))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()
model.fit(X, Y, epochs=20, batch_size=100, validation_split=0.2, shuffle=True)
score = model.evaluate(X_test, Y_test)
print(score)
"""
X_train, Y_train, X_test, Y_test = X[:5000],Y[:5000],X[5000:],Y[5000:5990]
model = Model()
input_layer = Input(shape=(x_size,))
h_layer1 = Dense(100, activation='relu')(input_layer)
h_layer2 = Dropout(0.4)(h_layer1)
h_layer3 = Dense(100, activation='relu')(h_layer2)
result_layer1 = Dense(len(categories[0]), activation='softmax')(h_layer3)
result_layer2 = Dense(len(categories[1]), activation='softmax')(h_layer3)
result_layer3 = Dense(len(categories[2]), activation='softmax')(h_layer3)
result_layer4 = Dense(len(categories[3]), activation='softmax')(h_layer3)
model = Model(inputs=[input_layer], outputs=[result_layer1,result_layer2,result_layer3,result_layer4])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()
model.add(Dense(100, activation="relu", input_shape=(10, 2,)))
model.add(Flatten())
model.add(Dense(50, activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(100, activation="relu"))
model.add(Dense(10, activation="relu"))
model.add(Dense(1, activation="relu"))
model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
model.summary()
model.fit(X, Y, epochs=20, batch_size=100, validation_split=0.2, shuffle=True)
score = model.evaluate(X_test, Y_test)
print(score)
"""

import time
name_time = str(time.time())[-4:-1]
model.save("NN_treadmill"+name_time+".h5")