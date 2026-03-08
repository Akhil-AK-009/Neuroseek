# 🧠 NeuroSeek – Multimodal AI Parkinson’s Risk Screening System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-orange)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

# 📌 Overview

**NeuroSeek** is a multimodal AI-based Parkinson’s Disease screening system designed to estimate Parkinson’s risk using three neurological signals:

- ✍️ Handwriting Analysis  
- 🎤 Speech Analysis  
- 🚶 Gait Analysis  

The system integrates these signals using **weighted multimodal fusion** to produce a **final Parkinson risk score**.

NeuroSeek is designed as a **mobile-first AI screening platform** with a scalable FastAPI backend, database integration, and explainability support.

⚠️ **Disclaimer:** NeuroSeek is a research and screening support tool and does not replace professional medical diagnosis.

---

# 🏗️ System Architecture

```
                ┌─────────────────────────────┐
                │  Mobile App (React Native) │
                │       (Planned UI)         │
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

- 16kHz mono standardization  
- 3-second normalization  
- Log Mel-spectrogram conversion  

Explainability:

Grad-CAM on Mel Spectrogram

---

## 🚶 Gait Module

Architecture:

MediaPipe Pose Extraction  
↓  
150-frame temporal sequence  
↓  
1D CNN  

Input features:

272 features  
(136 joints × x,y)

Output:

Gait Parkinson Risk Score (0–1)

---

# 🔬 Multimodal Fusion

NeuroSeek combines predictions using **weighted late fusion**.

Final Risk Score =  
0.30 × Handwriting  
0.20 × Speech  
0.50 × Gait  

Risk Levels:

| Score | Risk |
|------|------|
| < 0.35 | Normal |
| 0.35 – 0.65 | Moderate |
| > 0.65 | High |

---

# 📊 Explainable AI

NeuroSeek integrates explainable AI components.

Speech  
Grad-CAM heatmaps on Mel Spectrogram

Gait  
Pose-based motion pattern analysis  
Temporal gait feature interpretation

Handwriting  
CNN activation visualization (planned)

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
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── model_loader.py
│   │   │
│   │   ├── models/
│   │   │   ├── patient.py
│   │   │   └── screening.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │   ├── inference_service.py
│   │   │   └── gait_feature_extractor.py
│   │   │
│   │   └── main.py
│   │
│   ├── ml_models/
│   │
│   └── requirements.txt
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

Single modality screening:

POST /screenings/handwriting  
POST /screenings/speech  
POST /screenings/gait-video  

Full multimodal screening:

POST /screenings/full  

Query screening results:

GET /screenings/patient/{patient_id}  
GET /screenings/{screening_id}

Administrative operations:

DELETE /screenings/{screening_id}  
PUT /screenings/{screening_id}/restore

---

# ⚙️ Backend Setup

Clone repository

```
git clone https://github.com/yourusername/NeuroSeek.git
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

backend/ml_models/

Example:

ml_models/  
spiral_model.pth  
wave_model.pth  
speech_best_finetuned.pth  
gait_binary_v1.pth  

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

Deployment (planned)

Docker  
Cloud hosting  

Frontend (planned)

React Native mobile app

---

# 🔐 Ethics & Responsible AI

NeuroSeek is designed for **research and screening support**.

It does **not replace clinical diagnosis** and must always be used alongside professional medical evaluation.

---

# 📈 Future Roadmap

Upcoming improvements:

- MediaPipe gait retraining pipeline  
- Grad-CAM visualization export  
- SHAP explainability integration  
- Dockerized backend deployment  
- Cloud deployment (AWS / Azure)  
- Screening analytics dashboard  
- Role-based access control  
- CI/CD pipeline  

---

# 👨‍💻 Author

**Akhil A K**  
BCA Artificial Intelligence Student  
Multimodal AI Systems & Health-Tech Research