
import os
import matplotlib.pyplot as plt
import json
import asyncio
from pathlib import Path
from datetime import datetime
import numpy as np

#Apis & Setting import
from apis.train.utilis.dataset_info import get_dataset_info
from apis.train.utilis.traincallbacks import TrainingCallback
from core.config import Settings   


#TensorFlow Library
import tensorflow as tf
import tensorflow.keras.callbacks as cb
import tensorflow.keras.models as Models
import tensorflow.keras.layers as Layers
import tensorflow.keras.optimizers as Optimizer
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model

            
#Main Train Model
#improvement to add options to reduceLRonPlateau
#options for callbacks- earlystopping , best model , latest model ---> go thru eva model 
#Historical for training using db-sql
# json setting, data or history is db-sql

async def train_model( dataset_dir, validation_dir,epochs,verbose, optimizer_name, learning_rate, websocket= None):
    batchSize = Settings.BATCHSIZE
    imgSize = Settings.IMGSIZE
    inputShape = Settings.INPUTSHAPE
    seed = Settings.SEED
    ker = Settings.KER
    sker = Settings.SKER
    parent = os.path.dirname(os.path.dirname(__file__))
    print(parent)

    Train_ds = image_dataset_from_directory(dataset_dir, labels="inferred", batch_size=batchSize, image_size=imgSize, seed=seed)
    g_count, ng_count, slide_count = get_dataset_info(Train_ds, websocket)
    Test_ds = image_dataset_from_directory(validation_dir, labels="inferred", batch_size=batchSize, image_size=imgSize, shuffle = False, seed=seed)
    val_g_count, val_ng_count, val_slide_count = get_dataset_info(Test_ds, websocket)

    dataset_info = {
        'status': 'dataset_info',
        'g_count': int(g_count),
        'ng_count': int(ng_count),
        'slide_count': int(slide_count),
        'val_g_count': int(val_g_count),
        'val_ng_count': int(val_ng_count),
        'val_slide_count': int(val_slide_count)
    }
    if websocket is not None:
        await websocket.send_text(json.dumps(dataset_info))

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = Train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    test_ds = Test_ds.cache().prefetch(buffer_size=AUTOTUNE)

    checkpoint_dir= os.path.join(parent, "model")
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, "checkpoint.h5")
    history_dir = os.path.join(parent, "history")
    os.makedirs(history_dir, exist_ok=True)

    if os.path.exists(checkpoint_path):
        print("Resuming from checkpoint.")
        model = load_model(checkpoint_path)
    else:
        model = Models.Sequential([
            Layers.Rescaling(1./255, input_shape=inputShape),
            Layers.RandomFlip(mode="horizontal_and_vertical", seed=seed),
            Layers.Conv2D(16,kernel_size=ker, activation='relu',padding='same'),
            Layers.Conv2D(32,kernel_size=sker, activation='relu',padding='same'),
            Layers.MaxPool2D(2,2),
            Layers.Conv2D(64,kernel_size=ker, activation='relu',padding='same'),
            Layers.Conv2D(128,kernel_size=sker, activation='relu',padding='same'),
            Layers.MaxPool2D(3,2),
            Layers.Conv2D(256,kernel_size=ker, activation='relu',padding='same'),
            Layers.Conv2D(512,kernel_size=sker, activation='relu',padding='same'),
            Layers.AveragePooling2D(3),
            Layers.Flatten(),
            Layers.Dropout(0.3),
            Layers.Dense(3,activation='softmax')])
    
    #optimizer Selection 
    if optimizer_name.lower() == 'adam':
        optimizer  =Optimizer.Adam(learning_rate=learning_rate)
    elif optimizer_name.lower() == 'sgd':
        optimizer = Optimizer.SGD(learning_rate=learning_rate)
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer_name}")

    model.compile(optimizer=optimizer,loss='sparse_categorical_crossentropy',metrics=['accuracy'])

    #callbacks
    reduce_lr = cb.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=0.00001, verbose=1)
    es = cb.EarlyStopping(monitor='val_loss', patience=7, verbose=1, mode='min')
    log_dir="logs/fit/" + datetime.now().strftime("%Y%m%d_%H%M%S")
    tensorboard = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    # Save the best model based on validation loss
    best_model_callback = ModelCheckpoint(checkpoint_path, monitor='val_loss', save_best_only=True, verbose=1)
    #call back
    callbacks = [es,reduce_lr,tensorboard,best_model_callback]
    if websocket:
        ws_callback = TrainingCallback(websocket)
        callbacks.append(ws_callback)

    # Train the model
    final_history = None
    # original code
    for epoch in range(epochs):
        history = model.fit(
            train_ds,
            validation_data=test_ds,
            epochs=1,
            verbose=verbose,
            #additional
            callbacks =callbacks)
        final_history = history.history

        # Send an update to the frontend
        update = {
            'epoch': epoch,
            'loss': history.history['loss'][0],
            'accuracy': history.history['accuracy'][0],
            'val_loss': history.history['val_loss'][0],
            'val_accuracy': history.history['val_accuracy'][0],
        }
        #if no web socket
        if websocket is not None:
            await websocket.send_json(update)

    model_save = os.path.join(parent,"model", datetime.now().strftime("%Y%m%d_%H%M%S_") + "model.h5")
    model.save(model_save)

     #if no websocket
    if websocket is not None:
        save_message={
            'status': 'model_saved',
            'model_path': model_save
        }
        await websocket.send_text(json.dumps(save_message))



#DB last portion can do ( hist data is last idea)