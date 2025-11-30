@echo off
REM Script para verificar status no Windows

echo 🔍 Verificando status...

REM Verificar Backend (Porta 8000)
netstat -ano | findstr :8000 | findstr LISTEN > NUL
if %ERRORLEVEL% EQU 0 (
    echo ⚙️  Backend (8000): ONLINE
) else (
    echo ⚙️  Backend (8000): OFFLINE
)

REM Verificar Frontend (Porta 5173)
netstat -ano | findstr :5173 | findstr LISTEN > NUL
if %ERRORLEVEL% EQU 0 (
    echo 📱 Frontend (5173): ONLINE
) else (
    echo 📱 Frontend (5173): OFFLINE
)

pause
