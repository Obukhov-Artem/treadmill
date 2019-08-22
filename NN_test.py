from keras.layers import *
from keras.preprocessing.text import *
from keras import Sequential
from string import ascii_letters
from keras.utils.np_utils import to_categorical as to_cat
import random
import numpy as np

from keras.models import load_model

"""
X = data.values[:,  1:6:3]
X_new = np.asarray([data.values[i:i+10, 1:6:3] for i in range(len(X) - 10 )])
Y = data.values[:5990,  6:7]
X = X_new
"""
X = np.array([[0.23517764, 0.22677994],
 [0.2357204,  0.2262882 ],
 [0.2359041,  0.22665167],
 [0.23599005, 0.22702813],
 [0.23653579, 0.22667813],
 [0.24019635, 0.22622693],
 [0.24713361, 0.22613263],
 [0.25621927, 0.22646403],
 [0.26691449, 0.22748649],
 [0.25108421, 0.22898757]])
NN = load_model("NN_treadmill574.h5")
new_data = NN.predict(X.reshape(-1,10,2))
for i in range(len(X)):
    print(new_data[i])
