# NeuroSeek

NeuroSeek is a multimodal AI-based screening system for early risk assessment of Parkinson’s Disease.

##  Project Overview

NeuroSeek integrates three modalities:

- ✍ Handwriting Analysis
- 🎤 Speech Analysis
- 🚶 Gait Analysis

The system uses a reliability-weighted late fusion strategy:

p_final = 0.30 * Handwriting + 0.20 * Speech + 0.50 * Gait

## Backend Architecture

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic Migrations
- JWT Authentication
- Docker (Planned)
- React Native Frontend (Planned)

##  Current Status

Backend development in progress.

