@echo off
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
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Python topilmadi!
    echo      https://python.org dan yuklab o'rnating.
    pause
    exit /b
)

:: Kutubxonalarni o'rnatish (agar kerak bo'lsa)
echo  [*] Kutubxonalar tekshirilmoqda...
pip install -r requirements.txt -q --disable-pip-version-check

echo.
echo  [*] Bot ishga tushmoqda...
echo.

:: Botni ishga tushirish
python main.py %*

echo.
pause
