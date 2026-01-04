# 🦺 Safety OS – AI-Powered PPE Detection System

Safety OS is a real-time **AI-based Personal Protective Equipment (PPE) Detection Web Application** designed to improve workplace safety in industrial environments.  
The system uses **YOLO object detection**, **Flask**, and **OpenCV** to monitor safety compliance through live camera feeds and generate alerts when required PPE is missing.

---

## 🚀 Features

- 🔍 **Real-time PPE Detection**
  - Detects Helmet, Mask, and Safety Vest
  - Identifies missing PPE instantly

- 📹 **Live Camera Streaming**
  - Real-time webcam feed using OpenCV
  - Annotated frames with detection results

- ⚠️ **Automated Safety Alerts**
  - Displays alerts when PPE is missing
  - Logs safety violations automatically

- 🧠 **AI Chatbot Integration**
  - Local AI chatbot using Ollama (Mistral)
  - Helps with safety queries and guidance

- 👤 **User Authentication**
  - Secure Login & Signup system
  - Session-based access control

- 🗂 **Audit Logs**
  - Stores violation logs with timestamp
  - Review safety history anytime

- 🎨 **Professional Dashboard UI**
  - Clean, modern interface
  - Responsive layout with sidebar navigation

---

## 🛠 Tech Stack

### Frontend
- HTML5
- CSS3 (Custom Professional UI)
- JavaScript

### Backend
- Python
- Flask

### AI / Computer Vision
- YOLO (Ultralytics)
- OpenCV
- Mistral (via Ollama)

### Database
- SQLite3

---

## 📂 Project Structure

PROJECT STRUCTURE

ppe-gemini
│
├── static
│ └── style.css
│
├── templates
│ ├── login.html
│ ├── signup.html
│ ├── home.html
│ ├── camera.html
│ ├── chatbot.html
│ └── audit_logs.html
│
├── models
│ └── best.pt
│
├── industry_safety.db
├── app.py
├── README.md
└── requirements.txt

INSTALLATION AND SETUP

Step 1: Clone the repository
git clone https://github.com/your-username/your-repository-name.git

cd your-repository-name

Step 2: Create and activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

Step 3: Install required dependencies
pip install -r requirements.txt

Step 4: Run the Flask application
python app.py

Step 5: Open the application in a browser
