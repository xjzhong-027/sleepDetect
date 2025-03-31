@echo off
echo Changing to project directory...
cd /d E:\sleep_vue

echo Starting services...

:: 启动姿势检测服务
start "Posture Detection Service" cmd /k "python backend/posture_detect.py"

:: 启动情绪检测服务
start "Emotion Detection Service" cmd /k "python backend/detect.py"

echo Services have been started.
echo Please check the command windows for any errors.
echo.
echo Service URLs:
echo - Posture Detection: http://127.0.0.1:5001
echo - Emotion Detection: http://127.0.0.1:5000