#!/bin/bash
set -e

# Run backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Run frontend
echo "Starting frontend..."
cd frontend
npm run dev -- -p 3000 &
FRONTEND_PID=$!
cd ..

echo "Both servers are running."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
