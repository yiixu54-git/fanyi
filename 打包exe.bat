@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   屏幕翻译工具 - 打包为独立 exe
echo ============================================
echo.

REM 检查是否有虚拟环境
if not exist "venv\Scripts\pip.exe" (
    echo [!] 未找到 venv 虚拟环境
    echo [!] 请先运行『安装依赖.bat』
    echo.
    pause
    exit /b 1
)

echo [1/3] 安装 PyInstaller ...
call "venv\Scripts\pip.exe" install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [错误] 安装 PyInstaller 失败
    pause
    exit /b 1
)

echo.
echo [2/3] 正在打包（首次约 3~5 分钟，请耐心等待）...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
call "venv\Scripts\pyinstaller.exe" build.spec --clean --noconfirm
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo.
echo ============================================
echo    exe 已生成：dist\屏幕翻译.exe
echo ============================================
echo.
echo 可以把 dist\屏幕翻译.exe 复制到任何 Windows 电脑
echo 上直接双击运行，不需要 Python 环境。
echo.
echo （首次运行会自动下载 OCR 模型约 20MB）
echo.

REM 直接打开 dist 文件夹
explorer dist
pause
