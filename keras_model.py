import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
import keras.losses


datagen = ImageDataGenerator()

train_generator = datagen.flow_from_directory('E:/Images', class_mode='binary', batch_size=64)
validation_generator = datagen.flow_from_directory('E:/Images', class_mode='binary', batch_size=64)

model = Sequential()

model.add(Conv2D(32, kernel_size=(5, 5), strides=(1, 1),
                 activation='relu',
                 input_shape=(784,784,3)))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Conv2D(64, (5, 5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(1000, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.SGD(lr=0.01),
              metrics=['accuracy'])

#model.fit_generator(
#        train_generator,
#        steps_per_epoch=2000 // 64,
#        epochs=1,
#        validation_data=validation_generator,
#        validation_steps=800 // 64)
#model.save_weights('first_try.h5')
