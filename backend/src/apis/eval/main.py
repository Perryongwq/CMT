import tensorflow as tf
import numpy as np
from sklearn.metrics import confusion_matrix
import json


def compare_models(test_ds, best_model_path, latest_model_path):
    best_model = tf.keras.models.load_model(best_model_path)
    latest_model = tf.keras.models.load_model(latest_model_path)

    best_model_results = best_model.evaluate(test_ds, verbose=0)
    latest_model_results = latest_model.evaluate(test_ds, verbose=0)

    comparison = {
        "best_model": {
            "loss": best_model_results[0],
            "accuracy": best_model_results[1]
        },
        "latest_model": {
            "loss": latest_model_results[0],
            "accuracy": latest_model_results[1]
        }
    }

    return comparison




async def load_and_evaluate_model(model_path, test_dataset, websocket=None):
    # Load the model
    model = tf.keras.models.load_model(model_path)

    # Evaluate the model
    loss, accuracy = model.evaluate(test_dataset)

    # Predict the labels
    predictions = model.predict(test_dataset)
    predicted_labels = np.argmax(predictions, axis=1)

    # Get the true labels
    true_labels = np.concatenate([y for x, y in test_dataset], axis=0)

    # Calculate the confusion matrix
    cm = confusion_matrix(true_labels, predicted_labels)

    # Collect model info
    model_info = {
        'input_shape': model.input_shape,
        'layers': [{'name': layer.name, 'class_name': layer.__class__.__name__, 'trainable': layer.trainable}
                   for layer in model.layers]
    }

    # Send the results to the frontend
    if websocket:
        results = {
            'test_loss': loss,
            'test_accuracy': accuracy,
            'confusion_matrix': cm.tolist(),  # Convert the numpy array to a list
            'model_info': model_info
        }
        await websocket.send(json.dumps(results))
