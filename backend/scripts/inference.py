import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import PReLU
from sklearn.preprocessing import LabelEncoder
import pickle

backend_dir = os.path.dirname(os.path.dirname(__file__))
model_dir = os.path.join(backend_dir, 'intelligence')
label_encoder_path = os.path.join(model_dir, 'label_encoder.pkl')

# Load label encoder
with open(label_encoder_path, 'rb') as f:
    le: LabelEncoder = pickle.load(f)

# Load ensemble models
models = [
    load_model(os.path.join(model_dir, f'model_fold_{i}.keras'), custom_objects={'PReLU': PReLU})
    for i in range(1, 6)
]

# Preprocess
def preprocess_image(image: Image.Image) -> np.ndarray:
    img = image.convert('L').resize((32, 32), Image.Resampling.LANCZOS)
    img = np.array(img, dtype='float32') / 255.0
    return img.reshape(1, 32, 32, 1)

# Predict one character
def predict_character(image: Image.Image) -> str:
    img_array = preprocess_image(image)
    avg_pred = sum(model.predict(img_array, verbose=0) for model in models) / len(models)
    predicted_label = np.argmax(avg_pred)
    return le.inverse_transform([predicted_label])[0]

# Predict full word from list of character images
def predict_word_from_images(images: list[Image.Image]) -> str:
    return ''.join(predict_character(img) for img in images)