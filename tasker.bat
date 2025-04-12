@echo off
SET VENV_DIR=.venv

:: Check if venv exists
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    
    echo Installing requirements...
    call %VENV_DIR%\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
)

:: Activate venv and run app
call %VENV_DIR%\Scripts\activate.bat
python main.py

pause