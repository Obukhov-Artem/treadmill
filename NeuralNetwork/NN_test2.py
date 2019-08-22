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

#import pylab
#from mpl_toolkits.mplot3d import Axes3D

#fig = pylab.figure()
#axes  = Axes3D(fig)

X = data.values[:,  :6]
X_new = np.asarray([data.values[i:i+10,:6] for i in range(len(X) - 10 )])
Y = data.values[:5990,  6:7]
X = X_new

NN = load_model("NN_model_predict514.h5")
new_data = NN.predict(X)
n =2000
#x,y,z = X[:n,0,:1].reshape(n), X[:n,0,1:2].reshape(n), X[:n,0,2:3].reshape(n,1)

#axes.scatter(x, y, z )

#pylab.show()
import csv
with open("res.csv", "w", newline='') as out_file:
    writer = csv.writer(out_file, delimiter=';')
    for row in zip(X,new_data):
        writer.writerow(row)
#for i in range(5900):
#    print(X[i], new_data[i])
