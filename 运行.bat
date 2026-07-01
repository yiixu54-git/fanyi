@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 优先使用当前目录下的 venv
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" main.py
    exit /b
)

REM 否则用系统 pythonw
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw main.py
    exit /b
)

REM 兜底：控制台 python（会有黑窗口）
python main.py
