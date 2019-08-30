# example of making predictions for a regression problem
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, LSTM, RNN, Embedding, Input
from keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np

# generate regression dataset

x_raw = []
y_raw = []
xscaler, yscaler = StandardScaler(),StandardScaler()
for i in range(1, 10001):
    x_raw.append([i])
    y_raw.append([i+50])
X = np.array(x_raw)
Y = np.array(y_raw)
X = xscaler.fit_transform(X)
Y = yscaler.fit_transform(Y)
means_ = yscaler.mean_
scale_ = yscaler.scale_
print(means_, scale_)
# define and fit the final model
input_layer = Input(shape=(1,))
h_layer = Dense(15, activation='relu', kernel_initializer="glorot_uniform")(input_layer)
h_layer = Dense(100, activation='relu', kernel_initializer="glorot_uniform")(h_layer)
result_layer = Dense(1,  kernel_initializer="glorot_uniform")(h_layer)
model = Model(inputs=[input_layer], outputs=[result_layer])
model.compile(loss='mse', optimizer='adam')
model.fit(X, Y, epochs=25, verbose=1, validation_split=0.2)

# new instances where we do not know the answer
Xnew = np.array([[10], [20], [4.4], [9.6]])
y_predict = [i + 50 for i in Xnew]

# make a prediction
ynew = model.predict(xscaler.transform(Xnew))

# show the inputs and predicted outputs
for i in range(len(Xnew)):
    print("X=%s, Predicted=%s, Right=%s" % (Xnew[i], yscaler.inverse_transform(ynew[i]), y_predict[i]))
