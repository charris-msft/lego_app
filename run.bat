@echo off
echo 🧱 Starting LEGO Collection Manager...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the Flask application
echo Starting Flask development server...
echo Open your browser to: http://localhost:5000
echo.
python app.py

pause
