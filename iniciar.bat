@echo off
title COLIH Captacao — Iniciando servidor...
cd /d "%~dp0"

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║     COLIH Captacao — Sistema de Medicos   ║
echo  ║     Salvador, Bahia                       ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Verificar Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale em https://python.org
    pause
    exit /b 1
)

:: Instalar dependencias se necessario
if not exist backend\venv (
    echo [1/3] Criando ambiente virtual...
    python -m venv backend\venv
)

echo [2/3] Ativando ambiente e instalando dependencias...
call backend\venv\Scripts\activate.bat
pip install -q -r backend\requirements.txt

echo [3/3] Iniciando servidor FastAPI na porta 8000...
echo.
echo  Sistema disponivel em: http://localhost:8000
echo  Pressione CTRL+C para encerrar
echo.

:: Abrir navegador apos 2 segundos
start "" timeout /t 2 /nobreak >nul && start http://localhost:8000

:: Iniciar servidor (sem --reload para nao interferir na sincronizacao)
cd backend
..\backend\venv\Scripts\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000

pause
