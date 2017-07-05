from __future__ import print_function
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import utils
import numpy as np
import random

batch_size = 10
num_classes = 2
epochs = 2

def load_data():
    '''
    batch_files = utils.all_files()
    batch_x = np.asarray([utils.get_image(batch_file) for batch_file in batch_files])
    batch_y = np.asarray([random.randint(0, 1) for batch_file in batch_files])

    return (batch_x, batch_y), (batch_x, batch_y)
    '''
    good_arts_train = utils.all_files("good_arts")
    bad_arts_train = utils.all_files("bad_arts")

    good_arts_test = utils.all_files("good_arts_test")
    bad_arts_test = utils.all_files("bad_arts_test")

    good_train_x = np.asarray([utils.get_image(batch_file) for batch_file in good_arts_train])
    bad_train_x = np.asarray([utils.get_image(batch_file) for batch_file in bad_arts_train])

    train_x = np.concatenate((good_train_x, bad_train_x))

    train_y = np.concatenate((np.asarray([1 for batch_file in good_arts_train]) ,np.asarray([0 for batch_file in bad_arts_train])))

    test_x = np.concatenate((np.asarray([utils.get_image(batch_file) for batch_file in good_arts_test]), np.asarray([utils.get_image(batch_file) for batch_file in bad_arts_test])))
    test_y = np.concatenate((np.asarray([1 for batch_file in good_arts_test]),np.asarray([0 for batch_file in bad_arts_test])))
    
    return (train_x, train_y), (test_x, test_y)


# input image dimensions
img_rows, img_cols = 196, 196
input_shape = (img_rows, img_cols, 3)

# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = load_data()

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

print('x_train shape:', x_train.shape)
print('y_train shape:', y_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(x_test, y_test))

score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])