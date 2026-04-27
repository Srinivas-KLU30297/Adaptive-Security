# CyberShield AI Platform

Welcome to the CyberShield AI Forensic and Threat Intelligence Platform.
This application uses advanced AI and machine learning models (Deepfake detection, SDXL detection, Phishing heuristics) to analyze media and URLs.

## Prerequisites
- **Python 3.10+**
- **Node.js 18+**

## Quick Start Guide

### 1. Backend Setup (AI & API)
Open a terminal in the `backend` folder:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Open your MySQL command line or Workbench and run:
```sql
CREATE DATABASE cybershield_db;
```

*(Note: The backend assumes the MySQL username is `root` and the password is `@Sinu8541`. If your friend uses a different MySQL password, they must copy `backend/.env.example` to `backend/.env` and update the `DATABASE_URL` line inside).*

Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Wait for the models to load completely (it will download the AI weights on the first run, which may take a few minutes).*

### 2. Frontend Setup (React UI)
Open a SECOND terminal in the `frontend` folder:
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
- Open `http://localhost:3000` in your browser.
- Log in with the default admin account:
  - **Email:** `admin@cybershield.ai`
  - **Password:** `Admin@123`

### Setting up Email Deliveries (Optional)
If you want to test the automated PDF Email Report dispatch system:
1. Rename `backend/.env.example` to `backend/.env`
2. Enter your Google App Password and email inside the file.
3. Restart the backend server.
