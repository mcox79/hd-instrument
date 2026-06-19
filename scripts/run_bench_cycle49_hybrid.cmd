@echo off
cd /d C:\dev\hd-instrument
if not exist logs mkdir logs
C:\dev\hd-instrument\.venv\Scripts\python.exe tools\substrate_benchmark.py --questions data\substrate_index\benchmark_corpus_v3_60q.jsonl --use-router > logs\bench_cycle49_hybrid.log 2>&1
