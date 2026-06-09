@echo off
cd /d C:\dev\hd-instrument
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -u -m backend.kb.wikidata_dump_ingest --dump data/wikidata_dump/latest-truthy.nt.bz2 --n-triples 100 --output-dir C:/tmp/wikidata_smoke 1> C:\Users\marsh\wikidata_smoke.out 2> C:\Users\marsh\wikidata_smoke.err
echo EXIT_CODE=%ERRORLEVEL% >> C:\Users\marsh\wikidata_smoke.out
