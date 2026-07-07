@echo off
echo ============================================================
echo   DocStamp Pro — Iniciando...
echo ============================================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale o Python 3.11+ em: https://python.org/downloads
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado.
echo.

REM Instala dependencias se necessário
if not exist ".deps_installed" (
    echo [1/2] Instalando dependencias pela primeira vez...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias.
        pause
        exit /b 1
    )
    echo instalado > .deps_installed
    echo [OK] Dependencias instaladas!
    echo.
) else (
    echo [OK] Dependencias ja instaladas.
    echo.
)

echo [2/2] Iniciando DocStamp Pro...
echo.
start "" pythonw.exe main.py
echo [OK] DocStamp Pro aberto!
timeout /t 2 >nul
