# TasteBridge dev launcher: force the correct venv, ignore any other venv
if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
& "$PSScriptRoot\venv\Scripts\Activate.ps1"
python --version
python -m uvicorn main:app --port 8000
