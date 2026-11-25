:: Smart Shutdown - Mode 6: Cancel / Abort Auto-Shutdown and Exit
@echo off
@chcp 65001 >nul
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0..\"
set "ENGINE_PATH=%~dp0..\scripts\06_cancel_or_exit_monitor.py"

set "NO_PAUSE="
set "EXTRA_ARGS="
for %%A in (%*) do (
    if /i "%%A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else (
        set "EXTRA_ARGS=!EXTRA_ARGS! %%A"
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

title Smart Shutdown: Cancel / Abort Auto-Shutdown ^& Exit
color 0E

cls
if defined PYTHON_EXE (
    if exist "%ENGINE_PATH%" (
        "%PYTHON_EXE%" "%ENGINE_PATH%" !EXTRA_ARGS!
        if not defined NO_PAUSE (
            echo Press any key to exit...
            pause >nul
        )
        exit /b 0
    )
)

:: Fallback batch cancellation if Python is not present
echo ======================================================================
echo    Smart Shutdown: Option 6 - Exit / Abort Active Shutdown
echo    Developer: Atul Verma (aiprincekumar / aiprincekumar010100@gmail.com)
echo ======================================================================
echo.

shutdown /a >nul 2>nul
if !ERRORLEVEL! equ 0 (
    echo  [SUCCESS] Active Windows system shutdown has been CANCELLED [shutdown /a].
) else (
    echo  [INFO] No Windows system shutdown command was pending.
)

set "LOCK_FILE=%~dp0..\smart_shutdown.lock"
if exist "%LOCK_FILE%" (
    del "%LOCK_FILE%" >nul 2>nul
    echo  [SUCCESS] Cleaned up smart_shutdown.lock.
)
set "LEGACY_LOCK_FILE=%~dp0..\auto_shutdown.lock"
if exist "%LEGACY_LOCK_FILE%" (
    del "%LEGACY_LOCK_FILE%" >nul 2>nul
    echo  [SUCCESS] Cleaned up legacy auto_shutdown.lock.
)

echo.
echo ======================================================================
echo  Smart Shutdown Exit Complete.
echo ======================================================================
echo.
if not defined NO_PAUSE (
    echo Press any key to exit...
    pause >nul
)
exit /b 0
