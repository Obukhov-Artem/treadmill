from keras.models import Sequential, Model
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D, Input, Reshape, BatchNormalization
from keras.layers.core import Dense, Activation, Dropout, Flatten
import numpy as np
from sklearn.preprocessing import StandardScaler
import keras
import random

# подготавливаем данные
x_raw = []
y_raw = []
for i in range(1, 100001):
    a, b = random.randint(1, 20), random.randint(1, 20)
    x_raw.append([a, b])
    if a <= 10 and b <= 5:
        y_raw.append(0)
    elif 10 < a <= 20 and 5 < b < 15:
        y_raw.append(1)
    elif a < 10 and b > 5:
        y_raw.append(2)
    else:
        y_raw.append(3)
print(x_raw[0])
X = np.array(x_raw)
Y = np.array(y_raw)
scaler = StandardScaler()
X = scaler.fit_transform(X)
print(X[0], X.shape)
print(Y[0], Y.shape)
X_train, X_test, Y_train, Y_test = X[:90000], X[90000:], Y[:90000], Y[90000:]
Y_train = keras.utils.np_utils.to_categorical(Y_train,4)
Y_test = keras.utils.np_utils.to_categorical(Y_test,4)

# model
model = Sequential([Dense(10, activation="relu", input_shape=(2,)),
                    Dense(4, activation='softmax')
                    ])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
model.fit(X_train, Y_train, epochs=3, batch_size=32, validation_data=(X_test, Y_test), shuffle=True)
score = model.evaluate(X_test, Y_test)
print(score[0], score[1])

# real test


from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

X_predict = np.array([[23, 24], [40, 12], [79, 3], [-4, 49]])
X_predict = scaler.fit_transform(X_predict)
y_predict0 = [0, 1, 3, 2]
y_predict = model.predict(scaler.fit_transform(X_predict))
print(y_predict)
print([np.argmax(y) for y in y_predict])
