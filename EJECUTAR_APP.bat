@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SecureTask API
echo ============================================================
echo   SecureTask API  -  Ejecutar la aplicacion (demo)
echo ============================================================
echo.
set PYCMD=python
where python >nul 2>&1 || set PYCMD=py -3
if not exist ".venv\Scripts\python.exe" (
  echo [1/2] Creando entorno virtual e instalando dependencias ^(solo la 1a vez^)...
  %PYCMD% -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip -q
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt -q
) else (
  echo [1/2] Entorno ya preparado.
)
echo [2/2] Iniciando el servidor en http://localhost:8000 ...
start "SecureTask API - servidor (no cerrar durante la demo)" ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
timeout /t 6 >nul
start "" http://localhost:8000/docs
echo.
echo  La app esta corriendo. Se abrio la documentacion interactiva (Swagger):
echo     http://localhost:8000/docs     (probar los endpoints)
echo     http://localhost:8000/health
echo.
echo  Para DETENER la app, cierra la ventana titulada "SecureTask API - servidor".
pause
