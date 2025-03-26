@echo off
title Iniciando o Inventorize...

echo Iniciando o backend...
start cmd /k "cd backend && node server.js"

timeout /t 2 >nul

echo Iniciando o frontend...
start cmd /k "cd frontend && npm start"

echo Tudo pronto! O sistema está carregando no navegador. 🚀
pause
