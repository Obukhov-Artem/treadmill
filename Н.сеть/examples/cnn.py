from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.models import Sequential
from keras.utils import np_utils
from keras.datasets import mnist
"""
# Load pre-shuffled MNIST data into train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()
print(X_train.shape)
X_train = X_train.reshape(X_train.shape[0], 1, 28, 28)
X_test = X_test.reshape(X_test.shape[0], 1, 28, 28)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255
Y_train = np_utils.to_categorical(y_train, 10)
Y_test = np_utils.to_categorical(y_test, 10)
#Линейный стек слоев. Вы создаете последовательную модель, вызывая keras_model_sequential()функцию, а затем ряд layerфункций:
model = Sequential()
# Слой двумерной свертки (например, пространственная свертка на изображениях).
# Этот слой создает сверточное ядро, которое свернуто с входным слоем для получения тензора выходных данных.сверточные слои.
# По сути представляют собой фильтры, чтобы нейросеть смогла научиться распознавать абстрактные образы.
model.add(Convolution2D(32, (3, 3), activation='relu', input_shape=(1,28,28), data_format='channels_first'))
#усреднение значений фильтров. Обязателен после сверточных слоев;
model.add(MaxPooling2D(pool_size=(2,2)))
#по сути нужен для регуляризаци Главная идея Dropout —
# вместо обучения одной DNN обучить ансамбль нескольких DNN, а затем усреднить полученные результаты.
model.add(Dropout(0.25))
# https://i.stack.imgur.com/Wk8eV.png
#  меняет размерность
model.add(Flatten())
#еще один слой скрытый полносвязный (Dense) слой, который получает данные только с входного слоя
model.add(Dense(128, activation='relu'))

model.add(Dropout(0.5))
#Обратите внимание, что конечный слой имеет выходной размер 10, соответствующий 10 классам цифр.
model.add(Dense(10, activation='softmax'))
#собираем модель
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
# training model
#verbose =0 -ничего не отображать в процессе обучения, 1 - вывод данных о процессе обучения
model.fit(X_train, Y_train,
          batch_size=32, epochs=5, verbose=1)
#оценка модели
score = model.evaluate(X_test, Y_test, verbose=0)
model_json = model.to_json()
# Записываем модель в файл
json_file = open("model_01.json", "w")
model.save_weights("model_01_w.h5")
json_file.write(model_json)
json_file.close()
"""

#testing
from keras.models import model_from_json
import glob
import numpy as np
from PIL import Image
from keras.utils import np_utils
from keras.datasets import mnist
# Load pre-shuffled MNIST data into train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_train.shape
X_train = X_train.reshape(X_train.shape[0], 1, 28, 28)
X_test = X_test.reshape(X_test.shape[0], 1, 28, 28)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255
Y_train = np_utils.to_categorical(y_train, 10)
Y_test = np_utils.to_categorical(y_test, 10)
json_file = open("model_01.json", "r")
loaded_model_json = json_file.read()
json_file.close()
# Создаем модель на основе загруженных данных
loaded_model = model_from_json(loaded_model_json)
# Загружаем веса в модель
loaded_model.load_weights("model_01_w.h5")

loaded_model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

score = loaded_model.evaluate(X_test, Y_test, verbose=0)
print("Точность модели на тестовых данных датасета: %.2f%%" % (score[1] * 100))


# Проверяем модель на тестовых данных
result = []
data = []
start = True
#открытие всех картинок из папки
for filename in glob.glob('images/*.png'):
    img = Image.open(filename)
    result.append(filename.split("\\")[-1])
    #сохраняем только 28х28 пикселей массива в список
    data.append(np.array(img, dtype='uint8')[:,:,0])
# вырезаем из названия цифру - выходное значение
result = [int(i.split(".")[0][0]) for i in result]
# приводим значения к категориям
Y_test_cat = np_utils.to_categorical(result, 10)
# обрабатываем входные данные к тому же виду, что в обучающем множестве
X_test = np.array(data, dtype='float32')
X_test = X_test.reshape(X_test.shape[0], 1, 28, 28)
X_test /= 255
#определяем выход по входу на нашей модели
y_test = loaded_model.predict(X_test)
#возвращаем цифру класса
classes = np.argmax(y_test, axis=1)
# выводим результат и точность модели
print(y_test)
for i in zip(result,classes):
    print(i)
scores = loaded_model.evaluate(X_test, Y_test_cat, verbose=0)
print("Точность модели на тестовых данных: %.2f%%" % (scores[1] * 100))