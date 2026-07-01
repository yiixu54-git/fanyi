@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   屏幕翻译工具 - 依赖安装
echo ============================================
echo.

REM 创建虚拟环境（可选，避免污染全局环境）
if not exist "venv" (
    echo [1/3] 创建虚拟环境 venv ...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败，请确认已安装 Python 3.8+
        pause
        exit /b 1
    )
)

echo [2/3] 升级 pip ...
call "venv\Scripts\python.exe" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/3] 安装依赖 ...
call "venv\Scripts\pip.exe" install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ============================================
echo   安装完成！双击『运行.bat』即可启动。
echo ============================================
pause
