@echo off
cd /d C:\dev\hd-instrument
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -u -m backend.kb.wikidata_dump_ingest --dump data/wikidata_dump/latest-truthy.nt.bz2 --n-triples 50000000 --output-dir data/substrate_state/wikidata_truthy_50m --batch-size 128 --checkpoint-every 50000 > C:\Users\marsh\wikidata_ingest.log 2> C:\Users\marsh\wikidata_ingest.err
