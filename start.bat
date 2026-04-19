@echo off

start "KavernChampions - Back" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && python app.py"
start "KavernChampions - Front" cmd /k "cd /d %~dp0frontend && npm run dev"
