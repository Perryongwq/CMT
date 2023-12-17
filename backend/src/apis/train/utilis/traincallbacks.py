import tensorflow as tf
import tensorflow.keras.callbacks as cb
import asyncio
import json

class TrainingCallback(cb.Callback):
    def __init__(self, websocket):
        self.websocket = websocket
        self.loop = asyncio.get_event_loop()

    def on_epoch_end(self, epoch, logs=None):
        data = {
            'status': 'epoch_end',
            'epoch': epoch,
            'accuracy': round(logs.get('accuracy'),3),
            'loss': round(logs.get('loss'),3),
            'val_accuracy': round(logs.get('val_accuracy'),3),
            'val_loss': round(logs.get('val_loss'),3)
        }
        print("Sending data to frontend:", data)  # Diagnostic print
        try:
            asyncio.run_coroutine_threadsafe(self.websocket.send_text(json.dumps(data)), self.loop)
        except Exception as e:
            print("Error sending data:", e)  # Log any exception
            