import tensorflow as tf
import numpy as np
import shutil
import zipfile
from fastapi import UploadFile, HTTPException
import os
import time
import aiofiles
import asyncio

async def async_remove(path):
    try:
        if path.is_file() or path.is_symlink():
            await asyncio.to_thread(os.unlink, path.path)
        elif path.is_dir():
            await asyncio.to_thread(shutil.rmtree, path.path)
    except Exception as e:
        print(f'Failed to delete {path.path}. Reason: {e}')

async def clear_temp_directory():
    start_time = time.time()
    temp_dir = 'temp'
    tasks = []

    with os.scandir(temp_dir) as entries:
        for entry in entries:
            tasks.append(asyncio.create_task(async_remove(entry)))

    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"clear_temp_directory executed in {end_time - start_time} seconds")


async def handle_upload(file: UploadFile):
    start_time = time.time()
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    zip_path = os.path.join(temp_dir, file.filename)
    try:
        # Use aiofiles for asynchronous file operation
        async with aiofiles.open(zip_path, 'wb') as out_file:
            # Read the file in chunks
            while True:
                contents = await file.read(1024 * 1024)  # Read in chunks of 1 MB
                if not contents:
                    break
                await out_file.write(contents)

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(zip_path)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="File not found")
    except zipfile.BadZipFile:
        raise HTTPException(status_code=500, detail="Not a zip file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    end_time = time.time()
    print(f"handle_upload executed in {end_time - start_time} seconds")
    return {"message": "File uploaded and extracted successfully"}

def get_info(dataset):
    g_count = 0
    ng_count = 0
    slide_count = 0

    for images, labels in dataset:
        g_count += tf.math.count_nonzero(labels == 0).numpy()
        ng_count += tf.math.count_nonzero(labels == 1).numpy()
        slide_count += tf.math.count_nonzero(labels == 2).numpy()
    return g_count, ng_count, slide_count



#get the dataset info for frontend
def get_dataset_info(dataset, websocket):
    g_count = 0
    ng_count = 0
    slide_count = 0

    for images, labels in dataset:
        g_count += tf.math.count_nonzero(labels == 0).numpy()
        ng_count += tf.math.count_nonzero(labels == 1).numpy()
        slide_count += tf.math.count_nonzero(labels == 2).numpy()
    return g_count, ng_count, slide_count


