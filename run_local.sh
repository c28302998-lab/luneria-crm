#!/bin/bash
echo "Запуск локальной версии Luneria CRM..."

echo "1. Установка зависимостей Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install python-multipart
# Запуск миграций / seed.py для SQLite
export DATABASE_URL="sqlite:///./luneria_local.db"
export SECRET_KEY="local_secret"
python seed.py

echo "2. Запуск Backend (порт 8000)..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "3. Установка зависимостей Frontend..."
cd ../frontend
npm install

echo "4. Запуск Frontend (порт 3000)..."
npm run dev &
FRONTEND_PID=$!

echo "========================================="
echo "Сервер работает на http://localhost:8000"
echo "Сайт работает на http://localhost:3000"
echo "========================================="
echo "Нажмите Ctrl+C чтобы остановить оба сервера"

trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
