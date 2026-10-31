@echo off
rem Startet den lokalen Webserver für die EPROM-Web-App und öffnet sie im Browser.
rem Fenster schließen = Server beenden.
cd /d "%~dp0web"
set URL=http://127.0.0.1:8765/index.html

rem Browser kurz verzögert öffnen, damit der Server schon läuft.
rem Web Serial gibt es nur in Chrome/Edge, daher Chrome bevorzugen.
start "" /b cmd /c "timeout /t 1 >nul & (start chrome "%URL%" 2>nul || start msedge "%URL%")"

echo EPROM Programmer laeuft auf %URL%
echo Zum Beenden dieses Fenster schliessen.
python -m http.server 8765 --bind 127.0.0.1
if errorlevel 1 (
  echo.
  echo Server konnte nicht starten: Python installiert? Port 8765 schon belegt?
  pause
)
