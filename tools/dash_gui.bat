@echo off
REM Launcher for the local Tkinter fleet monitor (tools/dash_gui.py).
REM Replaces the web dashboard as the primary day-to-day monitor: no web
REM server, no port, no supervisor/poller process -- just a window that polls
REM tools/inflight_monitor.py inline on its own timer.
REM
REM Uses pythonw.exe (no console window) when available so double-clicking
REM this .bat doesn't leave a console behind the GUI window. Since pythonw
REM swallows stdout/stderr, uncaught startup errors are redirected to a log
REM file next to this script for debugging (the log only fills if something
REM actually crashes -- normal operation writes nothing).
setlocal
set "HERE=%~dp0"
set "LOG=%HERE%dash_gui_launch.log"
set "VENV_PYW=%HERE%..\.venv\Scripts\pythonw.exe"
set "VENV_PY=%HERE%..\.venv\Scripts\python.exe"

if exist "%VENV_PYW%" (
    start "" "%VENV_PYW%" "%HERE%dash_gui.py" 2>>"%LOG%"
    goto :eof
)
if exist "%VENV_PY%" (
    start "" "%VENV_PY%" "%HERE%dash_gui.py" 2>>"%LOG%"
    goto :eof
)
where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" pythonw "%HERE%dash_gui.py" 2>>"%LOG%"
) else (
    start "" python "%HERE%dash_gui.py" 2>>"%LOG%"
)
endlocal
