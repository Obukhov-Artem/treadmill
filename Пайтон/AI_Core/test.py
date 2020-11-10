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
data = pandas.read_csv("data2/data3.csv", sep=";")



X = data.values[:, 2:3]
input_num,dims_num = X.shape
#X_new = np.asarray([data.values[i:i+10,:6] for i in range(len(X) - 10 )])
#X = np.reshape( X_new, (X_new.shape[0], X_new.shape[1], 6))
Y = data.values[:,  9:10]

NN = load_model("testing_new.h5")

for i in range(len(X)):
    action = [-1, 0, 1]
    a = np.argmax(NN.predict(X[i]))
    print(X[i],Y[i], action[a])