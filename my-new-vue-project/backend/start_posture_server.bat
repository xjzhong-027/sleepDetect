@echo off
chcp 65001 >nul
echo 正在启动姿势检测服务器...

:: 启动服务器
python posture_server.py

:: 如果服务器异常退出，暂停显示错误信息
pause 