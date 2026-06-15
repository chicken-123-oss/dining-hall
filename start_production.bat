@echo off
chcp 65001 >nul
title 论坛生产环境服务器
cd /d d:\claw\forum

echo ==============================
echo  豆腐脑战争论坛 - 生产环境
echo ==============================
echo.

:: 检查 Python
D:\Python\python\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请确认路径
    pause & exit /b 1
)

:: 检查依赖
echo [1/3] 检查依赖...
D:\Python\python\python.exe -c "import flask, flask_cors, waitress" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    D:\Python\python\python.exe -m pip install -r requirements.txt
)

:: 初始化数据库
echo [2/3] 初始化数据库...
D:\Python\python\python.exe -c "from app import init_db; init_db()"

:: 启动服务
echo [3/3] 启动生产服务器...
echo 本地访问: http://127.0.0.1:5001
echo 按 Ctrl+C 停止服务
echo ==============================
echo.

:: 使用 waitress 启动（生产级 WSGI 服务器）
D:\Python\python\python.exe -m waitress --host=0.0.0.0 --port=5001 --threads=4 app:app

pause