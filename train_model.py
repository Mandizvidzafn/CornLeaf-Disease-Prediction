import tensorflow as tf
from keras._tf_keras.keras.optimizers import Adam
from keras._tf_keras.keras.preprocessing.image import ImageDataGenerator
from keras._tf_keras.keras.models import Model
from keras._tf_keras.keras.layers import Dense, GlobalAveragePooling2D
from keras._tf_keras.keras.applications import ResNet50
import os
data_dir = 'dataset' # dataset folder with subfolders for each class to be trained
img_size = (224, 224)
batch_size = 32
datagen = ImageDataGenerator(validation_split=0.2, rescale=1./255)
train_data = datagen.flow_from_directory(data_dir,
 target_size=img_size,
 batch_size=batch_size,
 subset='training',
 class_mode='categorical')
val_data = datagen.flow_from_directory(data_dir,
 target_size=img_size,
 batch_size=batch_size,
 subset='validation',
 class_mode='categorical')
# Load base model
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224,
3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
preds = Dense(train_data.num_classes, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=preds)
for layer in base_model.layers:
 layer.trainable = False
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_data, validation_data=val_data, epochs=5)
model.save('model/plant_disease_model.h5')