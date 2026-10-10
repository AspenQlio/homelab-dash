#!/bin/bash
echo "[*] Arrancando Motor Python (Backend)..."
source backend/.venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "[*] Arrancando Pantalla React (Frontend)..."
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
