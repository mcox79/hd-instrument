# Prereg: pos_data_efficiency_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** deepen substrate WINS / low-data-regime positioning (Research aux-features-shrink discovery).

## Motivation
Quantify the substrate's data efficiency on its strongest capability (POS, full-data 0.95). Train the structured-perceptron POS
tagger at [25,50,100,250,500,1000,2500] sentences; report the accuracy curve. Commercial value: niche-domain / few-shot / small-corpus.

## Pre-registered verdict
- HARD_PASS: POS >= 0.90 with <= 250 train sentences (strong low-data efficiency).
- MIDDLE_BAND: >= 0.90 by 1000.
- HARD_FAIL: needs > 1000 for 0.90.
Reports the full curve + smallest-n-for-0.90.

Smoke (25/50/100): 0.711/0.782/0.837 (climbing); full run (to 2500) decisive on n90.
