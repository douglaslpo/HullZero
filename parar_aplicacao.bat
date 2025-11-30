@echo off
REM Script para parar a aplicação HullZero no Windows

echo 🛑 Parando HullZero...

REM Parar Python (Backend)
taskkill /F /IM python.exe /T > NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend parado.
) else (
    echo ⚠️  Backend não estava rodando ou erro ao parar.
)

REM Parar Node (Frontend)
taskkill /F /IM node.exe /T > NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend parado.
) else (
    echo ⚠️  Frontend não estava rodando ou erro ao parar.
)

echo ✨ Tudo limpo.
pause
