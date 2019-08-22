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
data = pandas.read_csv("data.csv", sep=";")


X = data.values[:,  1:6:3]
X_new = np.asarray([data.values[i:i+10, 1:6:3] for i in range(len(X) - 10 )])
Y = data.values[:5990,  6:7]
X = X_new

NN = load_model("NN_treadmill574.h5")
new_data = NN.predict(X)
for i in range(len(X)):
    print(new_data[i],Y[i])
