@echo off
echo Installing Trust Wallet Agent Kit CLI...
call npm install -g @trustwallet/cli@0.19.1
twak --version
echo.
echo Next steps:
echo   1. Get API keys from https://portal.trustwallet.com/dashboard/apps
echo   2. twak init --api-key YOUR_ACCESS_ID --api-secret YOUR_HMAC_SECRET
echo   3. twak wallet create --password YourSecurePass1
echo   4. Add TWAK_* vars to .env
echo   5. python scripts\twak_bootstrap.py
pause