# BhashaBuddy-Backend

This is the **FastAPI backend** for the BhashaBuddy App — an AI-powered educational platform for children aged 8–14. The backend handles speech and handwriting inference, level/task logic, WebSocket communication, and Firebase integration.

---

## 🚀 Tech Stack

- **FastAPI**
- **TensorFlow / Keras**
- **Firebase Admin SDK**
- **WebSockets**
- **Python 3.10+**

---

## ✅ Prerequisites

1. **Python 3.10+**
2. **Firebase Project**
3. **Keras/TensorFlow models**
4. **A virtual environment tool** (e.g., `venv` or `virtualenv`)

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/tfHasi/BhashaBuddy-Backend.git
cd backend
```

---

### 2. Create and Activate Virtual Environment

#### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup Firebase Admin SDK

1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Navigate to your project → ⚙️ Project Settings → Service Accounts.
3. Click **"Generate new private key"** and download the `firebase-credentials.json` file.
4. Place this file in the project root (or wherever your app expects it).

Your directory should now look like:

```
backend/
├── main.py
├── firebase-credentials.json
├── requirements.txt
├── intelligence/
....
```

---

## ▶️ Running the Server

Run the app with `uvicorn`:

```bash
uvicorn main:app --reload
```

- The app will start at `http://127.0.0.1:8000`
- WebSocket endpoint: `ws://127.0.0.1:8000/ws`
- Use `--host 0.0.0.0` to make it accessible from Android emulators

---

## 📦 Features

- ✍️ Multi-model handwriting recognition using ensemble soft voting
- 🔤 Character-by-character prediction based on task words
- 🔊 Real-time inference over WebSockets
- 🔒 Firebase Auth verification and Firestore integration

---

## 🔐 Environment Variables

You can use a `.env` file for:

```
FIREBASE_CREDENTIALS_B64=B64 string here
```

---

## Contribution

Feel free to open issues or submit PRs. Be sure to follow the code structure and naming conventions.

---

### Made With Love ❤️

