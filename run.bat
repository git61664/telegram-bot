@echo off
setlocal
cd /d "%~dp0"
title DLS Auto Bot
echo.
echo  =====================================
echo   DLS Auto Bot - Ishga tushirilmoqda
echo  =====================================
echo.

:: Administrator huquqi tekshirish
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Administrator huquqi kerak!
    echo      Ushbu faylni o'ng tugma ^> "Run as administrator" bilan oching.
    echo.
    pause
    exit /b
)

:: Python mavjudligini tekshirish
set "PYTHON="
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYTHON (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
)
if not defined PYTHON (
    where py >nul 2>&1
    if not errorlevel 1 set "PYTHON=py"
)
if not defined PYTHON (
    echo  [!] Python topilmadi!
    echo      https://python.org dan yuklab o'rnating.
    pause
    exit /b
)

:: Kutubxonalarni o'rnatish (agar kerak bo'lsa)
echo  [*] Kutubxonalar tekshirilmoqda...
"%PYTHON%" -m pip install -r requirements.txt -q --disable-pip-version-check

echo.
echo  [*] Bot ishga tushmoqda...
echo.

:: Botni ishga tushirish
"%PYTHON%" main.py %*

echo.
pause
