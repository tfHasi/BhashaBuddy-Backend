# -*- coding: utf-8 -*-
"""LeNet5 HTR.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1omvsFN2TDMwhN2Z0VKY-k3asFlje_Ymx
"""

import pandas as pd
import string
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tensorflow as tf
import os
import random
from PIL import Image
from tqdm import tqdm
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, PReLU
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import AdamW
from sklearn.model_selection import StratifiedKFold
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score

from google.colab import drive
drive.mount('/content/drive')

"""### Explanatory Data Analysis"""

data_folder = '/content/drive/MyDrive/handwritten character dataset'

df = pd.read_csv(data_folder + '/english.csv')

df.describe()

df.head()

df.info()

df.label.unique()

"""### Filter Uppercase Labels"""

# Define allowed uppercase characters
uppercase_letters = list(string.ascii_uppercase)

# Filter DataFrame to include only rows with uppercase letters
df_uppercase = df[df['label'].isin(uppercase_letters)].reset_index(drop=True)

# Check the result
print(df_uppercase['label'].unique())
print(df_uppercase.head())

"""### Check Class Imbalances"""

label_counts = df_uppercase['label'].value_counts().sort_index()

print(label_counts)

"""Dataset is perfectly balanced

## Data Preparation
"""

# Label Encoding
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df_uppercase['label_encoded'] = le.fit_transform(df_uppercase['label'])

# Check for missing files
import os

# Join the data_folder path with the image path from the DataFrame
df_uppercase['image_full_path'] = df_uppercase['image'].apply(
    lambda x: os.path.join(data_folder, x)
)
missing = df_uppercase[~df_uppercase['image_full_path'].apply(os.path.exists)]

print(f"Missing files: {len(missing)}")
print(missing[['image', 'image_full_path']])

"""### Explore Data Sample"""

sample = df_uppercase.sample(10)
for i, (path, label) in enumerate(zip(sample['image'], sample['label'])):
    full_path = os.path.join(data_folder, path)
    img = Image.open(full_path)

    # Get size (width, height)
    width, height = img.size
    print(f"Image: {path}, Label: {label}, Size: {width}x{height}")

    plt.subplot(2, 5, i+1)
    plt.imshow(img)
    plt.title(label)
    plt.axis('off')

"""### Data Preprocessing"""

import numpy as np

# Resize and convert to grayscale
def preprocess_image(path, target_size=(32, 32)):
    img = Image.open(path).convert('L')  # 'L' mode = grayscale
    img = img.resize(target_size)
    return np.array(img)

print(np.array(img).shape)

X = []
y = []

for _, row in tqdm(df_uppercase.iterrows(), total=len(df_uppercase)):
    full_path = os.path.join(data_folder, row['image'])
    img_array = preprocess_image(full_path)
    X.append(img_array)
    y.append(row['label_encoded'])

X = np.array(X).reshape(-1, 32, 32, 1)  # Add channel dimension
y = np.array(y)

# Normalize pixel values
X = X / 255.0

"""### Visualize sample(Postprocessing)"""

# Choose 10 random indices
indices = random.sample(range(len(X)), 10)
# Plot
plt.figure(figsize=(10, 4))

for i, idx in enumerate(indices):
    plt.subplot(2, 5, i + 1)
    plt.imshow(X[idx].squeeze(), cmap='gray')  # squeeze to remove single channel
    plt.title(f"Label: {y[idx]}")
    plt.axis('off')

plt.tight_layout()
plt.show()

print(X.shape)

"""### Model Architecture(Custom CNN)"""

def build_model():
    model = Sequential([
        Conv2D(32, kernel_size=(3, 3), input_shape=(32, 32, 1), kernel_initializer='he_normal', padding='same', kernel_regularizer=l2(0.001)),
        PReLU(),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(64, kernel_size=(3, 3), kernel_initializer='he_normal', padding='same', kernel_regularizer=l2(0.001)),
        PReLU(),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(128, kernel_size=(3, 3), kernel_initializer='he_normal', padding='valid', kernel_regularizer=l2(0.001)),
        PReLU(),
        MaxPooling2D(pool_size=(2, 2)),

        Flatten(),
        Dense(128),
        PReLU(),
        Dropout(0.2),
        Dense(64),
        PReLU(),
        Dense(26, activation='softmax')  # 26 uppercase letters
    ])
    return model

"""### K-Fold Cross Validation Model Fit"""

from sklearn.model_selection import train_test_split

# Split into train+val and test (e.g., 90% for training/validation, 10% for final test)
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.1, stratify=y, random_state=42)

# Directory to save models
model_dir = os.path.join(data_folder, 'saved_models')
os.makedirs(model_dir, exist_ok=True)

kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
models = []
accuracies = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X_temp, y_temp)):
    X_train, X_val = X_temp[train_idx], X_temp[val_idx]
    y_train, y_val = y_temp[train_idx], y_temp[val_idx]

    model = build_model()
    model.compile(optimizer=AdamW(learning_rate=0.002),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    early_stop = EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True)
    model.fit(X_train, y_train,
              epochs=30,
              validation_data=(X_val, y_val),
              callbacks=[early_stop],
              verbose=1)

    val_acc = model.evaluate(X_val, y_val, verbose=0)[1]
    print(f"Fold {fold+1} accuracy: {val_acc:.4f}")
    accuracies.append(val_acc)

    # Save model
    model.save(os.path.join(model_dir, f'model_fold_{fold+1}.keras'))
    models.append(model)

"""### Ensemble Soft Voting with the 5 CNNs on test data"""

# Ensemble prediction on final test set
prob_sum = sum(model.predict(X_test, verbose=0) for model in models)
avg_probs = prob_sum / len(models)
y_pred_ensemble = np.argmax(avg_probs, axis=1)

accuracy = accuracy_score(y_test, y_pred_ensemble)
precision = precision_score(y_test, y_pred_ensemble, average='macro')
recall = recall_score(y_test, y_pred_ensemble, average='macro')
f1 = f1_score(y_test, y_pred_ensemble, average='macro')

print(f"\nFinal Evaluation on Hold-Out Test Set:")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

"""### Confusion Matrix"""

cm = confusion_matrix(y_test, y_pred_ensemble)

plt.figure(figsize=(12, 10))
labels = le.classes_
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix - Ensemble Soft Voting (Test Set)")
plt.show()

"""### Custom Images Test"""

# Paths
test_dir = '/content/drive/MyDrive/handwritten character dataset/test'

# Load LabelEncoder
le = LabelEncoder()
le.fit(df_uppercase['label'])

# Preprocess function
def preprocess_image(path):
    img = Image.open(path).convert('L').resize((32, 32), Image.Resampling.LANCZOS)
    return np.array(img, dtype='float32') / 255.0

# Load all models
models = [
    load_model(os.path.join(model_dir, f'model_fold_{i}.keras'), custom_objects={'PReLU': PReLU})
    for i in range(1, 6)
]

# Predict and plot
for fname in sorted(os.listdir(test_dir), key=lambda x: int(os.path.splitext(x)[0])):
    path = os.path.join(test_dir, fname)
    img_array = preprocess_image(path)
    img_input = img_array.reshape(1, 32, 32, 1)
    avg_prob = sum(model.predict(img_input, verbose=0) for model in models) / len(models)
    pred_label = np.argmax(avg_prob)
    pred_char = le.inverse_transform([pred_label])[0]

    plt.imshow(img_array, cmap='gray')
    plt.title(f"{fname}: {pred_char}")
    plt.axis('on')
    plt.show()

"""Almost little to no misclassifications with ensemble soft voting using the 5 models

### Inference Pipeline
"""

from PIL import Image
image_path = os.path.join(data_folder, 'test/6.png')

# Preprocess function
def preprocess_image(path):
    img = Image.open(path).convert('L').resize((32, 32), Image.Resampling.LANCZOS)
    return np.array(img, dtype='float32') / 255.0

# Load and preprocess image
img = preprocess_image(image_path).reshape(1, 32, 32, 1)

# Load all models and perform soft voting
models = [load_model(os.path.join(model_dir, f'model_fold_{i}.keras'), custom_objects={'PReLU': PReLU}) for i in range(1, 6)]
avg_pred = sum(model.predict(img, verbose=0) for model in models) / len(models)
# Decode prediction
predicted_label = np.argmax(avg_pred)

# Fit or load LabelEncoder
le = LabelEncoder()
le.fit(df_uppercase['label'])

# Output result
print("Predicted label (encoded):", predicted_label)
print("Predicted character:", le.inverse_transform([predicted_label])[0])

