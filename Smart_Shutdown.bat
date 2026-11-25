@echo off
@chcp 65001 >nul
setlocal EnableDelayedExpansion
:: Smart Shutdown - Direct Unified Desktop GUI Launcher

title Smart Shutdown
color 0B

set "SCRIPT_DIR=%~dp0"
set "ENGINE_PATH=%~dp0smart_shutdown.py"

:: Filter --no-pause and collect remaining CLI flags
set "NO_PAUSE="
set "FORWARD_ARGS="
for %%A in (%*) do (
    if /i "%%~A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else (
        if defined FORWARD_ARGS (
            set "FORWARD_ARGS=!FORWARD_ARGS! %%A"
        ) else (
            set "FORWARD_ARGS=%%A"
        )
    )
)

:: Verify Python Installation
set "PYTHON_EXE="

:: 1. Check .local bin python
if exist "%USERPROFILE%\.local\bin\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\.local\bin\python.exe"
)

:: 2. Check if python is in PATH
if not defined PYTHON_EXE (
    where python >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        set "PYTHON_EXE=python"
    )
)

:: 3. Check user's .venv python
if not defined PYTHON_EXE (
    if exist "%USERPROFILE%\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\.venv\Scripts\python.exe"
    )
)

:: 4. Check AppData Programs Python
if not defined PYTHON_EXE (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
    )
)

:: 5. Check Program Files Python
if not defined PYTHON_EXE (
    for /d %%D in ("%ProgramFiles%\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python was not found on this machine!
    echo Please install Python 3.10+ or add it to PATH.
    if not defined NO_PAUSE pause
    exit /b 1
)

:: Verify engine script existence
if not exist "%ENGINE_PATH%" (
    echo [ERROR] Smart Shutdown engine not found at:
    echo %ENGINE_PATH%
    if not defined NO_PAUSE pause
    exit /b 1
)

:: Launch Unified Desktop GUI directly or forward explicit CLI flags
if defined FORWARD_ARGS (
    "%PYTHON_EXE%" "%ENGINE_PATH%" !FORWARD_ARGS!
) else (
    "%PYTHON_EXE%" "%ENGINE_PATH%" --gui
)
set "EXIT_CODE=!ERRORLEVEL!"
exit /b !EXIT_CODE!
