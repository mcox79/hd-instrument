@echo off
echo === ensure datasets package is installed ===
C:\dev\hd-instrument\.venv-demo\Scripts\pip show datasets 2>nul | findstr /I Name || C:\dev\hd-instrument\.venv-demo\Scripts\pip install datasets 2>&1 | findstr /I Successfully

echo.
echo === sanity batch: 100 articles ===
cd /d C:\dev\hd-instrument
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m backend.kb.wikipedia_ingest --n-articles 100 --max-sentences-per-article 2 --output-dir data\substrate_state\wikipedia_sanity --batch-size 32 --checkpoint-every 50 2>&1
echo.
echo === inspect output ===
dir C:\dev\hd-instrument\data\substrate_state\wikipedia_sanity /b 2>nul
echo.
echo === first 3 facts ===
powershell -Command "Get-Content C:\dev\hd-instrument\data\substrate_state\wikipedia_sanity\facts.jsonl -Head 3"
echo.
echo === stats ===
type C:\dev\hd-instrument\data\substrate_state\wikipedia_sanity\stats.json
