@echo off
cd /d C:\dev\hd-instrument
if not exist C:\dev\hd-instrument\data\wikidata_dump mkdir C:\dev\hd-instrument\data\wikidata_dump
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -u scripts\download_wikidata_dump.py > C:\Users\marsh\wikidata_download.log 2> C:\Users\marsh\wikidata_download.err
