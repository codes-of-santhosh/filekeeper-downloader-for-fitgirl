@echo off
cd /d "%~dp0"
if exist "dist\FileKeeper-Downloader-FitGirl.exe" (
    start "" "dist\FileKeeper-Downloader-FitGirl.exe"
) else (
    start "" pythonw main.py
)
