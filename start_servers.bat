@echo off
echo ==========================================
echo  Online Debate Platform - Server Startup
echo ==========================================
echo.

echo Starting Django API Server (Port 8000)...
start "Django API Server" cmd /k "cd /d %~dp0 && .\.venv\Scripts\activate && python manage.py runserver localhost:8000"

echo.
echo Waiting 3 seconds before starting WebSocket server...
timeout /t 3 /nobreak > nul

echo Starting Daphne WebSocket Server (Port 8001)...
start "Daphne WebSocket Server" cmd /k "cd /d %~dp0 && .\.venv\Scripts\activate && daphne -b localhost -p 8001 onlineDebatePlatform.asgi:application"

echo.
echo ==========================================
echo  Servers are starting up...
echo ==========================================
echo.
echo Django API Server: http://localhost:8000
echo WebSocket Server:   ws://localhost:8001
echo Frontend Demo:      http://localhost:8000/demo/
echo API Documentation:  http://localhost:8000/swagger/
echo.
echo Press any key to open the frontend demo...
pause > nul

start "" "http://localhost:8000/demo/"

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
