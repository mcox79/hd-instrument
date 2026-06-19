# Prereg — wave14_betB_multitask_diff_corpus_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch for triage-A anchors)
**Routing**: strategy_untested_rows_triage_2026-05-24.md Priority A #5 U1/U7 UNSURE (Multi-task transfer A -> genuinely-different-corpus C); cycle-94 NUMFACTS_2000 retraction left this open
**Script**: `experiments/exp_wave14_betB_multitask_diff_corpus_v1.py`
**Queue**: remote_cpu_queue (CPU; N=2048; small-scale clean Bet B Kovacs A->C variant)

## Hypothesis

The substrate's continual-learning mechanism is tested on A->B->C where C = Python source — but Python source is structurally similar to English at the byte level (lots of ASCII, similar word/punctuation distribution). U1/U7 asks whether the substrate transfers to GENUINELY DIFFERENT-DISTRIBUTION corpus C. We use hex-encoded numerical content (ASCII hex digits) which has very different byte-distribution from prose English (~16 byte-values densely vs 256 byte-values sparse).

## Design

Two-phase A->C (no B intermediate; this is a transfer-not-bridge test):
- Phase A: English text from repo (existing pa.load_corpus_a)
- Phase C: Hex-encoded numerical content (NEW load_hex_corpus)

Single-shared-W with 50% A-replay during Phase C. Measure retention_A and gain_C.

Parameters: N=2048, BATCH=32, EPOCHS_C=3, PHASE_A_EPOCHS=5, BYTES=80K, SEEDS=[7,17,23,31,41].

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: retention_A >= 0.70 AND gain_C >= 0.30 across 5 seeds. Substrate transfers to genuinely-different domain. Substrate-product implication: U1/U7 closed-PASS; new ✅ annotation under continual-learning row.
- **HARD-FAIL**: retention_A <= 0.30 OR gain_C <= 0.05. No effective transfer; catastrophic forgetting OR no learning of C. Substrate-product implication: U1/U7 closed-FAIL; substrate transfer-CL is narrow to same-distribution domains.
- **MIDDLE**: intermediate. Partial transfer.

## Comparison anchors

- Bet B 3-corpus baseline retention_A ~0.73 (same-distribution C = Python source)
- cycle-94 NUMFACTS_2000 was retracted; this is fresh evidence

## Self-test

`python experiments/exp_wave14_betB_multitask_diff_corpus_v1.py --self-test` verifies 8 verdict-tag cases.

## Pre-reg routing impact

- HARD-PASS → cap_map v188 annotation under Bet B continual-learning row: cross-domain transfer ✅
- HARD-FAIL → cap_map v188 U1/U7 closed-FAIL annotation; substrate CL is same-domain only
- MIDDLE → annotation; partial cross-domain transfer
