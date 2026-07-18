@echo off
echo ============================================================
echo   DocStamp Pro — Script de Build
echo ============================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.11+ em https://python.org
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [2/4] Limpando builds anteriores...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "DocStampPro.spec" del DocStampPro.spec

echo.
echo [3/4] Gerando executavel .exe...
pyinstaller ^
    --name "DocStampPro" ^
    --onefile ^
    --windowed ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "fitz" ^
    --hidden-import "bcrypt" ^
    main.py

if errorlevel 1 (
    echo [ERRO] Falha ao gerar executavel.
    pause
    exit /b 1
)

echo.
echo [4/4] Concluido!
echo.
echo O executavel foi gerado em: dist\DocStampPro.exe
echo Copie o arquivo dist\DocStampPro.exe para os computadores dos funcionarios.
echo.
pause
