@echo off

start "KavernChampions - Back" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && python app.py"
start "KavernChampions - Front" cmd /k "cd /d %~dp0frontend && npm run dev"
start "KavernChampions - Bot" cmd /k "cd /d %~dp0twitch-bot && .venv\Scripts\activate && python bot.py"
