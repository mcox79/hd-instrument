@echo off
REM Owner's status window -- where we are / what is happening.
REM Double-click this, or run the python line directly.
REM Uses the repo .venv explicitly: a bare `python` here lacks the repo's dependencies and
REM has produced false ERRORs before (CLAUDE.md, evidence discipline sec 5, "right environment").
start "" "C:\AI\hd-instrument\.venv\Scripts\pythonw.exe" "C:\AI\hd-instrument\tools\status_gui.py" --single-instance
