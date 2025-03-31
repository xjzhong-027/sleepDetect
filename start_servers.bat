@echo off
echo Starting Sleep Monitoring System Backend Services...

:: 设置Python环境变量（如果需要的话）
:: set PATH=%PATH%;C:\Python39

:: 启动姿势检测服务器
start "Posture Server" cmd /k "cd backend && python posture_server.py"

:: 等待姿势服务器启动
timeout /t 2 /nobreak

:: 启动情绪和睡眠监测服务器
start "Detection Server" cmd /k "cd backend && python detect.py"

:: 等待检测服务器启动
timeout /t 2 /nobreak

:: 启动睡眠报告服务器
start "Report Server" cmd /k "cd backend && python sleep_report_server.py"

echo.
echo All backend services have been started.
echo Please check the individual command windows for any errors.
echo.
echo Press any key to close this window...
pause > nul 