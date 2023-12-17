
import tensorflow as tf
from apis.train.main import train_model
from apis.train.utilis.dataset_info import handle_upload
from apis.train.utilis.dataset_info import clear_temp_directory
from typing import List
from fastapi import File, UploadFile, Form, WebSocket, HTTPException
from fastapi import APIRouter, UploadFile
from schemas.trainresult import TrainingResult
import os
import json
import asyncio
import numpy as np
from fastapi import BackgroundTasks
from core.config import Settings  
from apis.train.utilis.dataset_info import get_info
from tensorflow.keras.preprocessing import image_dataset_from_directory
import asyncio


router= APIRouter()

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dataset_dir = os.path.join(backend_dir, "temp","dataset")
validation_dir = os.path.join(backend_dir, "temp" ,"validation")

#handle the upload of the train & valid dataset
@router.post("/upload")
async def upload_files(dataset: UploadFile = File(...), validation: UploadFile = File(...)):
    await clear_temp_directory()
    print(dataset_dir)
    print(validation_dir)
    # Use asyncio to handle file uploads concurrently
    dataset_result, validation_result = await asyncio.gather(
        handle_upload(dataset),
        handle_upload(validation)
    )
    # dataset_result = handle_upload(dataset)
    # validation_result = handle_upload(validation)
    Train_ds = image_dataset_from_directory(dataset_dir, labels="inferred", batch_size=Settings.BATCHSIZE, image_size=Settings.IMGSIZE, seed=Settings.SEED)
    g_count, ng_count, slide_count = get_info(Train_ds)
    Test_ds = image_dataset_from_directory(validation_dir, labels="inferred", batch_size=Settings.BATCHSIZE, image_size=Settings.IMGSIZE, shuffle=False, seed=Settings.SEED)
    val_g_count, val_ng_count, val_slide_count = get_info(Test_ds)

    dataset_info = {
        'train_dataset': {
            'g_count': int(g_count),
            'ng_count': int(ng_count),
            'slide_count': int(slide_count)
        },
        'validation_dataset': {
            'val_g_count': int(val_g_count),
            'val_ng_count': int(val_ng_count),
            'val_slide_count': int(val_slide_count)
        }
    }
    #create schema to return the dataset info
    #check if need to use async 

    return {"dataset": dataset_result, "validation": validation_result, "dataset_info": dataset_info}

@router.post("/train")
async def train_endpoint(background_tasks: BackgroundTasks, epochs: int, optimizer_name: str, learning_rate: float):
    print(dataset_dir)
    print(validation_dir)
    # Add the train_model function to background tasks
    background_tasks.add_task(
        train_model,
        dataset_dir=dataset_dir,
        validation_dir=validation_dir,
        epochs=epochs,
        verbose=1,
        optimizer_name=optimizer_name,
        learning_rate=learning_rate,
    )
    #need to await response
    return {"message": "Training started"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Parse the received data as JSON
                data_json = json.loads(data)
                epochs = int(data_json['epochs'])
                dataset_dir = data_json['dataset_dir']
                validation_dir = data_json['validation_dir']
                optimizer_name = data_json['optimizer']
                learning_rate = float(data_json['learning_rate'])


                # Validate the provided directory paths
                if not os.path.isdir(dataset_dir) or not os.path.isdir(validation_dir):
                    await websocket.send_text("The provided directory paths are invalid or inaccessible.")
                    continue

                # Assuming the directories are already present on the server and paths are correctly provided by the client
                await train_model(
                    dataset_dir=dataset_dir, 
                    validation_dir=validation_dir, 
                    epochs=epochs, 
                    verbose=1, 
                    optimizer_name= optimizer_name,
                    learning_rate= learning_rate,
                    websocket=websocket
                )

            except json.JSONDecodeError:
                await websocket.send_text("Please send a valid JSON with the number of epochs and directories.")
            except ValueError:
                await websocket.send_text("Please send a valid number of epochs.")
            except KeyError:
                await websocket.send_text("Please provide all required data: epochs, dataset_dir, and validation_dir.")
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()




