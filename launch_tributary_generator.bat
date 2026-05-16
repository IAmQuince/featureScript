@echo off
setlocal EnableExtensions

REM Tributary Generator single-click Windows launcher.
REM Keep this file at the repository root.
REM It sets PYTHONPATH to ./src and launches the live preview GUI.

cd /d "%~dp0"

if not exist "src\tributary_geometry\gui_app.py" (
    echo ERROR: Could not find src\tributary_geometry\gui_app.py
    echo Make sure this BAT file is being run from the extracted repository root.
    pause
    exit /b 1
)

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
set "TG_PYTHON="

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "TG_PYTHON=py -3"
    goto :run_app
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "TG_PYTHON=python"
    goto :run_app
)

echo ERROR: Python was not found on PATH.
echo Install Python 3.10+ or add it to PATH, then run this launcher again.
pause
exit /b 1

:run_app
echo Launching Tributary Generator live preview...
%TG_PYTHON% -m tributary_geometry.gui_app
set "TG_EXIT=%ERRORLEVEL%"
if not "%TG_EXIT%"=="0" (
    echo.
    echo Tributary Generator exited with code %TG_EXIT%.
    echo A diagnostic may be available in the reports folder if the app started far enough to write one.
    pause
)
exit /b %TG_EXIT%
