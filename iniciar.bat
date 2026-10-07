@echo off
title TUNING VASQUEZ & ASOCIADOS
cd /d "%~dp0"
echo ==============================================
echo   TUNING VASQUEZ ^& ASOCIADOS
echo   Sistema de Inventario y Ventas
echo ==============================================
where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encontro Python.
    echo Instala Python desde https://www.python.org/
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    py -m venv .venv
)
echo Instalando/verificando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo Servidor iniciado en http://127.0.0.1:8000
echo Presiona CTRL+C para detenerlo.
start "" http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
