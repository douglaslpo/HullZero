@echo off
REM Script para iniciar a aplicação HullZero (Backend + Frontend) no Windows

echo ============================================================
echo   🚀 HullZero - Iniciando Aplicação Completa
echo ============================================================

REM 1. Backend
echo.
echo 📦 Configurando Backend...

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependências...
pip install -r requirements.txt > NUL 2>&1

echo Inicializando banco de dados...
python init_complete.py --skip-tests

echo Iniciando API...
start /B python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1
echo ✅ Backend iniciado em background

REM 2. Frontend
echo.
echo 🎨 Configurando Frontend...
cd frontend

if not exist node_modules (
    echo Instalando dependências do frontend...
    call npm install > NUL 2>&1
)

echo Iniciando Frontend...
start /B npm run dev > ..\frontend.log 2>&1
echo ✅ Frontend iniciado em background

cd ..

REM 3. Resumo
echo.
echo ============================================================
echo   ✨ Aplicação HullZero rodando!
echo ============================================================
echo 📱 Frontend: http://localhost:5173
echo ⚙️  Backend:  http://localhost:8000
echo 📚 Docs API: http://localhost:8000/docs
echo.
echo Para parar a aplicação, execute: parar_aplicacao.bat
echo Logs em: backend.log e frontend.log
pause
