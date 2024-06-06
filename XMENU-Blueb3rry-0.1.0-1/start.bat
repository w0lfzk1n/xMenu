@echo off

setlocal enabledelayedexpansion

set VENV_DIR=WIN_venv
set VENV_REQUIREMENTS=configs/requirements/venv_requirements.txt
set PROJECT_REQUIREMENTS=configs/requirements/requirements.txt

echo Debug: Script started

goto main

:check_and_create_venv
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)
echo Debug: Pass Check and Create
goto :eof

:activate_venv
if exist %VENV_DIR%\Scripts\activate.bat (
    call %VENV_DIR%\Scripts\activate.bat
) else (
    echo Error: 'venv' not present. Please run 'start.bat install'.
    exit /b 1
)
goto :eof

:deactivate_venv
if exist %VENV_DIR%\Scripts\deactivate.bat (
    call %VENV_DIR%\Scripts\deactivate.bat
)
goto :eof

:install_venv
echo Debug: Starting install_venv
echo.
echo Installing requirements for virtual environment...
pip install -r %VENV_REQUIREMENTS%
call :check_and_create_venv
call :activate_venv
echo +++++++++++++++++++++++++++++++++++++++++++++
echo.
echo Installing requirements for project environment...
pip install -r %PROJECT_REQUIREMENTS%
call :deactivate_venv
echo Installation complete.
echo +++++++++++++++++++++++++++++++++++++++++++++
pause
goto :eof

:start_project
echo +++++++++++++++++++++++++++++++++++++++++++++
echo Debug: Starting project
call :activate_venv
echo Starting the Project...
python run.py
if %errorlevel% neq 0 (
    echo ERROR: Could not start script 'run.py'...
)
call :deactivate_venv
echo Deactivating ENV
echo +++++++++++++++++++++++++++++++++++++++++++++
goto :eof

:display_menu
echo Debug: Displaying menu
echo Please choose an option:
echo 1) Start
echo 2) First Install
echo 3) Exit
set /p option=Option: 
if "%option%"=="1" (
    call :start_project
) else if "%option%"=="2" (
    call :install_venv
    call :start_project
) else if "%option%"=="3" (
    echo +++++++++++++++++++++++++++++++++++++++++++++
    echo We are going to be shut down guys!
    echo Say ya'll prayers Your wives miss ya
    exit /b 0
) else (
    echo +++++++++++++++++++++++++++++++++++++++++++++
    echo Invalid option selected. Exiting...
    exit /b 1
)
goto :eof

:main
echo Debug: Checking arguments
if "%1"=="" (
    call :display_menu
) else if "%1"=="start" (
    call :start_project
) else if "%1"=="install" (
    call :install_venv
    call :start_project
) else (
    echo +++++++++++++++++++++++++++++++++++++++++++++
    echo Nah man, this is XMENU, not some bullshit %1!
    echo It's 'start' 'install' or nothing Got it?!
    exit /b 1
)
goto :eof

goto :main
