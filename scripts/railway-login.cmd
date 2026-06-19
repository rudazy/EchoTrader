@echo off
cd /d "%~dp0.."
echo.
echo EchoTrader Railway Login
echo ========================
echo.
echo If your browser did not open automatically, use browserless login.
echo Railway will print a URL and pairing code - open the URL in any browser.
echo.
pause
railway login --browserless
echo.
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Browserless failed. Trying default login...
    railway login
)
echo.
railway whoami
echo.
pause