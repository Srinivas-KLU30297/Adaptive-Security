@echo off
cd /d %~dp0backend
echo Starting CyberShield AI Backend...
uvicorn app.main:app --reload --reload-dir . --reload-dir ../ml_worker --host 0.0.0.0 --port 8000
