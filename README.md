# 🧠 NeuroSeek – Multimodal AI Parkinson’s Risk Screening System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-orange)
![React Native](https://img.shields.io/badge/Mobile-React%20Native-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

# 📌 Overview

**NeuroSeek** is a multimodal AI-based Parkinson’s Disease risk screening system designed to estimate Parkinson’s risk using neurological behavioral signals.

The system analyzes three modalities:

- ✍️ Handwriting patterns  
- 🎤 Speech characteristics  
- 🚶 Gait motion patterns  

Predictions from each modality are combined using **weighted multimodal fusion** to produce a final **Parkinson's risk score**.

NeuroSeek is designed as a **mobile-first AI screening platform** with a scalable FastAPI backend, database integration, and explainability support.

⚠️ **Disclaimer:** NeuroSeek is a research and screening support tool and does not replace professional medical diagnosis.

---

# 🏗️ System Architecture

```
                ┌─────────────────────────────┐
                │  Mobile App (React Native) │
                │                             │
                └──────────────┬─────────────┘
                               │ REST API
                               ▼
                ┌─────────────────────────────┐
                │       FastAPI Backend       │
                │                             │
                │ • JWT Authentication        │
                │ • Screening API             │
                │ • ML Model Inference        │
                │ • Multimodal Fusion         │
                │ • Explainability Layer      │
                │ • Audit Logging             │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌─────────────────────────────┐
                │       PostgreSQL DB         │
                │                             │
                │ • Users                     │
                │ • Patients                  │
                │ • Screenings                │
                │ • Audit Logs                │
                └─────────────────────────────┘
```

---

# 📱 Mobile Application

NeuroSeek includes a **React Native mobile application** that enables users to perform Parkinson’s screening.

Current features:

- User authentication (JWT-based secure login)  
- Patient registration & management  
- Multimodal screening (Handwriting + Speech + Gait)  
- Step-based screening workflow  
- Real-time ML inference  
- Risk score visualization  
- Screening history (user-specific secure access)  
- Report generation with risk interpretation  

---

# 🧠 AI Modules

## ✍️ Handwriting Module

Model:  
ResNet-18 CNN  

Dataset:  
PaHaW Parkinson Handwriting Dataset  

Tasks:

- Spiral drawing classification  
- Wave drawing classification  

Output:  
Motor Abnormality Risk Score (0–1)

---

## 🎤 Speech Module

Architecture:

Mel Spectrogram  
↓  
ResNet-18 CNN  

Audio preprocessing:

- 16 kHz mono standardization  
- 3-second normalization  
- Log Mel-spectrogram conversion  

Explainability:

Grad-CAM heatmaps on spectrograms  

---

## 🚶 Gait Module

Architecture:

MediaPipe Pose Extraction  
↓  
150-frame temporal sequence  
↓  
1D CNN  

Input Features:

272 features  
(136 joints × x,y coordinates)

Output:

Gait Parkinson Risk Score (0–1)

---

# 🔬 Multimodal Fusion

NeuroSeek combines predictions using **weighted late fusion**.

Final Risk Score:

```
Risk = 0.40 × Handwriting
     + 0.15 × Speech
     + 0.45 × Gait
```

Risk Levels:

| Score | Risk Level |
|------|-------------|
| < 0.55 | Normal |
| 0.55 – 0.75 | Moderate |
| > 0.75 | High |

---

# 🔐 Security & Data Privacy

- JWT-based authentication system  
- User-specific data isolation  
- Secure API endpoints using token validation  
- Screening data filtered per logged-in user  
- Prevention of cross-user data access  

---

# 📊 Explainable AI

NeuroSeek integrates explainability techniques to improve model transparency.

Speech  
Grad-CAM heatmaps on Mel Spectrogram  

Gait  
Pose-based temporal motion analysis  

Handwriting  
CNN activation visualization *(implemented in backend)*  

---

# 📂 Project Structure

```
Neuroseek/
│
├── backend/
│
│   ├── app/
│   │
│   │   ├── api/
│   │   │   └── routes/
│   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── model_loader.py
│   │
│   │   ├── models/
│   │   │   ├── patient.py
│   │   │   └── screening.py
│   │
│   │   ├── schemas/
│   │
│   │   ├── services/
│   │   │   ├── inference_service.py
│   │   │   ├── gait_feature_extractor.py
│   │   │   └── gradcam_service.py
│   │
│   │   └── main.py
│   │
│   ├── ml_models/
│   │
│   └── requirements.txt
│
├── frontend/
│   └── React Native Mobile App
│
└── README.md
```

---

# 🚀 API Endpoints

### Authentication

POST /register  
POST /login  
GET /profile  

### Patients

GET /patients  
POST /patients  
PUT /patients/{patient_id}  
DELETE /patients/{patient_id}  

### Screenings

POST /screenings/handwriting  
POST /screenings/speech  
POST /screenings/gait  
POST /screenings/full  

### Reports

GET /screenings/history  

---

# ⚙️ Backend Setup

Clone repository

```
git clone https://github.com/Akhil-AK-009/NeuroSeek.git
cd NeuroSeek/backend
```

Create virtual environment

```
python -m venv venv
```

Activate environment (Windows)

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

Run backend server

```
uvicorn app.main:app --reload
```

---

# 📘 API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 📦 Model Storage Policy

Large ML models are **not stored in GitHub**.

Models must be placed locally in:

```
backend/ml_models/
```

Example:

```
spiral_model.pth
wave_model.pth
speech_best_finetuned.pth
gait_binary_v1.pth
```

---

# 🛠️ Tech Stack

Backend

Python 3.10  
FastAPI  
SQLAlchemy ORM  
PostgreSQL  
JWT Authentication  

Machine Learning

PyTorch  
torchvision  
torchaudio  
MediaPipe  
scikit-learn  
NumPy  

Mobile Frontend

React Native  
Expo  
Axios API Integration  

Deployment (Upcoming)

Docker  
Render (Backend Hosting)  
Supabase (Database)  

---

# 🔐 Ethics & Responsible AI

NeuroSeek is designed as a **screening support system**.

It does **not replace professional medical diagnosis** and should always be used alongside clinical evaluation.

---

# 📈 Future Roadmap

Upcoming improvements:

- Full Dockerized deployment  
- Cloud hosting (Render / AWS)  
- Explainability visualization in frontend  
- Screening analytics dashboard  
- Role-based access control  
- CI/CD pipeline  
- Model performance monitoring  

---

# 👨‍💻 Author

**Akhil A K**  
BCA Artificial Intelligence Student  
Multimodal AI Systems & Health-Tech Research