@echo off
REM DFIR Vendor Analysis Web Server Startup Script

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask server...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
