# -*- coding: utf-8 -*-
"""EPICS_rough.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AXntCCtEmg-t-CWTe2gOpVpdI3ymscOJ
"""

from google.colab import drive
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow.keras import models,layers
import matplotlib.pyplot as plt
import keras

import os

directory = '/content/drive/MyDrive/Pest_V2/Pest_V2'
print(os.listdir(directory))

IMAGE_SIZE = 312
BATCH_SIZE = 30
CHANNELS = 3
EPOCHS = 80

dataset = tf.keras.preprocessing.image_dataset_from_directory('/content/drive/MyDrive/Pest_V2/Pest_V2',shuffle = True,image_size = (IMAGE_SIZE,IMAGE_SIZE), batch_size = 32)

class_names = dataset.class_names
print(class_names)

plt.figure(figsize=(10,10))
for image_batch, label_batch in dataset.take(1):
  for i in range(12):
    ax = plt.subplot(3,4,i+1)
    plt.imshow(image_batch[i].numpy().astype('uint8'))
    plt.title(class_names[label_batch[i]])
    plt.axis('off')

def get_dataset_partition_tf(ds,train_split=0.8,val_split=0.1,test_split=0.1,shuffle=True,shuffle_size =10000):
  ds_size = len(ds)
  if shuffle:
    ds = ds.shuffle(shuffle_size,seed=12)
  train_size = int(train_split*ds_size)
  val_size = int(val_split*ds_size)

  train_ds = ds.take(train_size)

  val_ds = ds.skip(train_size).take(val_size)
  test_ds = ds.skip(train_size).skip(val_size)
  return train_ds,val_ds,test_ds

train_ds,val_ds,test_ds=get_dataset_partition_tf(dataset)

print(len(train_ds))
print(len(val_ds))
print(len(test_ds))

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
test_ds = test_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)

resize_rescale = tf.keras.Sequential([
    layers.experimental.preprocessing.Resizing(IMAGE_SIZE,IMAGE_SIZE),
    layers.experimental.preprocessing.Rescaling(1.0/255)
     ])

data_augmentation = tf.keras.Sequential([
    layers.experimental.preprocessing.RandomFlip('horizontal_and_vertical'),
    layers.experimental.preprocessing.RandomRotation(0.2)
])

input_shape= (BATCH_SIZE,IMAGE_SIZE,IMAGE_SIZE,CHANNELS)
n_classes = 10
model = models.Sequential([
    resize_rescale,
    data_augmentation,
    layers.Conv2D(32,(3,3), activation='relu',input_shape=input_shape),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(32,(3,3), activation='relu',input_shape=input_shape),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3), activation='relu',input_shape=input_shape),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3), activation='relu',input_shape=input_shape),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3), activation='relu',input_shape=input_shape),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(64,activation='relu'),
    layers.Dense(n_classes,activation = 'softmax')

])
model.build(input_shape = input_shape)

model.summary()

model.compile(
    optimizer='adam',
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits = False),
    metrics=['accuracy']
)

history = model.fit(
    train_ds,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose =1,
    validation_data=val_ds
)

scores = model.evaluate(test_ds)

plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(range(EPOCHS),acc,label='Training Accuracy')
plt.plot(range(EPOCHS),val_acc,label='Validation Accuracy')
plt.legend(loc='lower right')

model = keras.models.load_model('/content/drive/MyDrive/Models')

model.save('my_model.keras')

model.save('my_model.h5')

#for mobile app development

import tensorflow as tf
from tensorflow import keras
keras_model_path = 'my_model.h5'
keras_model = keras.models.load_model(keras_model_path)
converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
tflite_model = converter.convert()


tflite_model_path = 'my_model.tflite'
with open(tflite_model_path, 'wb') as f:
    f.write(tflite_model)

import numpy as np
for images_batch,labels_batch  in test_ds.take(1):
  first_image = images_batch[0].numpy().astype("uint8")
  first_label = labels_batch[0].numpy()

  print('first image to predict')
  plt.imshow(first_image)
  print("actual label:",class_names[first_label])

  batch_prediction = model.predict(images_batch)


  print(class_names[np.argmax(batch_prediction[0])])

def prediction_func(image,model):
  image = tf.keras.utils.load_img(image, target_size=(312, 312))
  input_image = np.expand_dims(image, axis=0)
  prediction = model.predict(input_image)
  print(class_names[np.argmax(prediction)])
  plt.imshow(image)

prediction_func("/content/drive/MyDrive/12/IMG_4924.jpg",model)

model = keras.models.load_model('/content/drive/MyDrive/Models')