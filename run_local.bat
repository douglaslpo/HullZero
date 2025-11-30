@echo off
REM Script para iniciar apenas o Backend
REM Uso: run_local.bat

echo ============================================================
echo   HullZero - Iniciando Backend
echo ============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.11 ou superior.
    pause
    exit /b 1
)

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar dependências
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt -q
)

echo.
echo [INFO] Iniciando HullZero API...
echo [INFO] API disponivel em: http://localhost:8000
echo [INFO] Documentacao em: http://localhost:8000/docs
echo [INFO] Health check: http://localhost:8000/health
echo.
echo [INFO] Pressione Ctrl+C para parar
echo.

REM Iniciar backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload


