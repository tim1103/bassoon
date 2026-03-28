@echo off
chcp 65001 >nul
echo ================================
echo   浙江省新高考选课排课系统
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查并安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/3] 初始化数据目录...
if not exist "data" mkdir data

echo.
echo [3/3] 启动系统...
echo.
echo =================================
echo   系统即将启动，请稍候...
echo   访问地址：http://localhost:8080
echo =================================
echo.

python app.py

pause
