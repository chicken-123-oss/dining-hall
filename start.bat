@echo off
title 论坛服务器
cd /d d:\claw\forum
chcp 65001 >nul

echo ==============================
echo  检查环境...
echo ==============================

D:\Python\python\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请确认路径 D:\Python\python\python.exe
    pause & exit /b 1
)

D:\Python\python\python.exe -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    D:\Python\python\python.exe -m pip install flask flask-cors
)

echo ==============================
echo  启动论坛服务器...
echo ==============================
start "Forum Server" D:\Python\python\python.exe d:\claw\forum\app.py

echo 等待服务启动...
timeout /t 3 /nobreak >nul

echo ==============================
echo  启动内网穿透 (cpolar)...
echo ==============================
start "cpolar tunnel" D:\cpolar\cpolar.exe http 5001

echo.
echo ==============================
echo  全部启动完成！
echo  本地访问: http://127.0.0.1:5001
echo  公网地址: 请查看 cpolar 窗口
echo ==============================
echo.
pause
