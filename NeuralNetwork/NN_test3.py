from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
from sklearn.model_selection import train_test_split as t_t_split
import pandas
import random
import numpy as np


from keras.models import load_model
data = pandas.read_csv("output15h33m35s.csv", sep=";")


X = data.values[:,  1:6:3]
X_new = np.asarray([data.values[i:i+10, :6] for i in range(len(X) - 10 )])
X = X_new
Y_1 = data.values[0:X.shape[0],  6:7]
Y_2 = data.values[0:X.shape[0],  6:7]
for i in range(Y_1.shape[0]):
    if Y_2[i]>3:
        Y_2[i] = 1
    else:
        Y_2[i] = 0


NN = load_model("NN_model_speed199.h5")
new_data = NN.predict(X)
print(len(new_data))
for i in range(len(X)):
    print(new_data[0][i],new_data[1][i],Y_1[i],Y_2[i])
