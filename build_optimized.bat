@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo [1/2] Compiling smart_shutdown.py with Nuitka (64-bit standalone, LTO)...
python -m nuitka ^
  --standalone ^
  --windows-console-mode=disable ^
  --lto=yes ^
  --jobs=%NUMBER_OF_PROCESSORS% ^
  --enable-plugin=anti-bloat ^
  --enable-plugin=tk-inter ^
  --noinclude-pytest-mode=nofollow ^
  --noinclude-setuptools-mode=nofollow ^
  --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb,pdbpp,setuptools,pip,distutils,pkg_resources,email.mime,http.server,xmlrpc,pydoc ^
  --python-flag=no_docstrings ^
  --output-dir=dist ^
  --output-filename=SmartShutdown.exe ^
  --windows-icon-from-ico=assets\smart_shutdown.ico ^
  --remove-output ^
  smart_shutdown.py

if errorlevel 1 (
    echo [ERROR] Nuitka build failed with exit code %errorlevel%.
    exit /b %errorlevel%
)

echo [2/2] Slimming distribution directory...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0slim_dist.ps1" -DistPath "dist\smart_shutdown.dist"
if errorlevel 1 (
    echo [ERROR] slim_dist.ps1 failed with exit code %errorlevel%.
    exit /b %errorlevel%
)

echo [DONE] Build and slimming completed successfully.
endlocal
