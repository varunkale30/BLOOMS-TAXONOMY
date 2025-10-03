@echo off
echo ========================================
echo Bloom's Taxonomy Classifier
echo ========================================
echo.

echo Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

echo Checking if .env file exists...
if not exist .env (
    echo .env file not found. Running setup...
    python setup.py
    if errorlevel 1 (
        echo Setup failed. Please check the configuration.
        pause
        exit /b 1
    )
    echo.
)

echo Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting the application...
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
