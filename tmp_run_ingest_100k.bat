@echo off
cd /d C:\dev\hd-instrument
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m backend.kb.wikipedia_ingest --n-articles 100000 --max-sentences-per-article 2 --output-dir data\substrate_state\wikipedia_100k --batch-size 64 --checkpoint-every 5000 > C:\Users\marsh\wikipedia_ingest.log 2> C:\Users\marsh\wikipedia_ingest.err
