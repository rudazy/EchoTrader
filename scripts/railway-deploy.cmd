@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0railway-deploy.ps1"
exit /b %ERRORLEVEL%