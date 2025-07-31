Write-Host "🧱 Starting LEGO Collection Manager..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Set Flask environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Start the Flask application
Write-Host "Starting Flask development server..." -ForegroundColor Yellow
Write-Host "Open your browser to: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

python app.py

Read-Host "Press Enter to exit"
