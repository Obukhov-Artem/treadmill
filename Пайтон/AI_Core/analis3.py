
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

print(data.shape)
for i in data[:, :29]:
    # t11 = np.concatenate(([i[-2] * k], i[0:3], i[6:9]))
    # t12 = np.concatenate(([i[-2] * k], i[9:12], i[15:18]))
    # t13 = np.concatenate(([i[-2] * k], i[18:21], i[24:27]))
    X.append([i[-2] * k, i[2],i[11],i[20],i[8],i[17],i[26]])
    #speed, z, z_f1,z_f2, dz, dz_f1,dz_f2 = 7

X = np.array(X)
num = X.shape[0]
h =10
X2 = np.asarray([X[i:i + h, :] for i in range(num - h)])
speed_treadmill = data[:,27]
Y = [[0,1,0]]
t = 0
for i in range(1,speed_treadmill.shape[0]):
    delta = speed_treadmill[i]-speed_treadmill[i-1]
    if delta == 0:
        Y.append([0,1,0])
        t+=1
    elif delta<0:
        Y.append([1,0,0])
    else:
        Y.append([0,0,1])
Y = np.array(Y)
Y2 = np.array(Y[h:])
print(X.shape)
print(X2.shape)

print(Y.shape)
print(Y2.shape)





from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential, Model
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
num_action = 3

input_layer3 = Input(shape=(X.shape[1], ))
h_layer3 = Dense(50, activation='linear')(input_layer3)
h_layer3 = Dense(50, activation='linear')(h_layer3)
h_layer3 = Dropout(0.4)(h_layer3)
h_layer3 = Dense(100, activation='linear')(h_layer3)
result_layer3 = Dense(1)(h_layer3)
model = Model(inputs=[input_layer3], outputs=[result_layer3])
model.compile(loss='mse', optimizer='adam', metrics=['mae'])
model.summary()
epochs = 10
history3 = model.fit(X, speed_treadmill, epochs=epochs, batch_size=32, validation_split=0.25, verbose=1)
model.save("NN_1.h5")
#
# input_layer2 = Input(shape=(X2.shape[1],X2.shape[2],))
# h_layer2 = Dense(50, activation='linear')(input_layer2)
# h_layer2 = Dense(50, activation='linear')(h_layer2)
# h_layer2 = Flatten()(h_layer2)
# h_layer2 = Dropout(0.4)(h_layer2)
# h_layer2 = Dense(100, activation='relu')(h_layer2)
# result_layer2 = Dense(num_action, activation='softmax')(h_layer2)
# model2 = Model(inputs=[input_layer2], outputs=[result_layer2])
# model2.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# model2.summary()
# history2 = model2.fit(X2, Y2, epochs=epochs, batch_size=64, validation_split=0.15, verbose=1)
# model2.save("NN_2.h5")
p = model.predict(X)
for t in range(len(p)):
    print(p[t], speed_treadmill[t])

r = plt.subplot(1, 1,1)
plt.grid(True)
plt.plot(np.arange(1, epochs + 1), history3.history["mae"], label="accuracy")
#plt.plot(np.arange(1, epochs + 1), history2.history["val_accuracy"], label="accuracy2")
plt.xlabel("Эпоха")
plt.ylabel("Точность")
plt.legend(loc="lower left")
r.set_title("Точность нейронной сети управления", fontsize=12)


plt.savefig('compare.png', dpi=300)
plt.show()


