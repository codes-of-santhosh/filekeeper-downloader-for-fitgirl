@echo off
setlocal enabledelayedexpansion
title FileKeeper Downloader - Automatic Installer

echo =====================================================================
echo           FileKeeper Batch Downloader for FitGirl Repacks
echo                     Automatic Setup & Installer
echo =====================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [X] Python was not found on your system!
    echo Please install Python 3.10+ from https://python.org and make sure to
    echo check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [*] Python detected successfully.
python --version
echo.

:: 2. Upgrade pip & install requirements
echo [*] Installing required libraries and dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Some dependencies encountered errors during installation.
) else (
    echo [V] All Python packages installed successfully.
)
echo.

:: 3. Check aria2c.exe
if not exist "aria2c.exe" (
    echo [*] Downloading aria2c high-speed engine...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip' -OutFile 'aria2.zip'; Expand-Archive -Path 'aria2.zip' -DestinationPath 'aria2_temp' -Force; Copy-Item 'aria2_temp\*\aria2c.exe' -Destination 'aria2c.exe'; Remove-Item -Recurse -Force 'aria2.zip', 'aria2_temp'"
    if exist "aria2c.exe" (
        echo [V] aria2c.exe downloaded and set up successfully.
    ) else (
        echo [!] Could not auto-download aria2c.exe. Please ensure aria2c.exe is in the folder.
    )
) else (
    echo [V] aria2c engine is ready.
)
echo.

:: 4. Create Desktop Shortcut via VBScript
echo [*] Creating Desktop shortcut for FileKeeper Downloader...
set SCRIPT_DIR=%~dp0
set TARGET_PATH=%SCRIPT_DIR%run.bat
set ICON_PATH=%SCRIPT_DIR%assets\icon.ico

:: Create run.bat if not present
(
echo @echo off
echo cd /d "%%~dp0"
echo start "" pythonw main.py
) > "%SCRIPT_DIR%run.bat"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'FileKeeper Downloader.lnk')); $s.TargetPath = '%TARGET_PATH%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; if (Test-Path '%ICON_PATH%') { $s.IconLocation = '%ICON_PATH%' }; $s.Save()"

echo [V] Desktop shortcut created: "FileKeeper Downloader"
echo.
echo =====================================================================
echo    Installation Complete! You can now launch FileKeeper Downloader
echo    from your Desktop or by running run.bat.
echo =====================================================================
echo.
pause
