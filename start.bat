@echo off
echo Starte AIJobverlust auf http://localhost:8000
echo Druecke Strg+C zum Beenden.
cd /d "%~dp0site"
start http://localhost:8000
python -m http.server 8000
