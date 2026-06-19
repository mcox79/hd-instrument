# Post-reset exp_dev priority order

Filed 2026-05-29 in response to user strategic content drop (v269 integration).

## Context
User is offline ~24h+. Both queues PAUSED awaiting desktop reset. After reset:
- ONLOGON schtasks will spawn fresh runners with the NEW runner_v2_prod.py
  bytecode (schema fix from 32b1337). The dispatch-misclassification bug
  stops biting on first new-runner pickup.
- Queue.json on disk persists across reset.
- 23 anchors currently pending — keep most but reshuffle priority.
- 2 in-flight runs will be lost on reset (tcft_erase_robustness_v1 + c3_tcft_phase_v1).

## Pre-reset engineering landed (d95cf18)
- `experiments/_bit_precision.py` helper: quantize/dequantize/quantize_roundtrip
  + precision_metadata for FP32 / FP16 / INT8 / INT4 / INT2 / INT1. 12/12 tests
  pass. Ready to plug into any script with a `--bit-precision` arg.
- `experiments/llm_benchmarks/` LLM-1 scaffold: edit-benchmark harness with
  CounterFact / ZsRE / SequentialEdit dataset stubs, SubstrateEditMethod
  (KF-2-style), baseline stubs (ROME/MEMIT/AlphaEdit/MEND), efficacy /
  specificity / paraphrase metrics. 21/21 tests pass. Phase-2 work
  documented at `notes/llm_benchmark_harness_2026-05-29.md`.

## Priority order for post-reset refill

Tier-1 (ship FIRST after unpause; pre-reset queue already covers some):

1. **BE-1 precision floor mapping** (cheapest path to category-defining
   cost differentiation; ~2 GPU days).
   - Retrofit ONE script first (recommend `exp_kf2_cross_codebook_v2_n8192.py`
     since it's the strongest recent HARD_PASS) with `--bit-precision` arg
     using the helper at `experiments/_bit_precision.py`. Apply
     `quantize_roundtrip(W, args.bit_precision)` after substrate storage
     step but BEFORE retrieval. Log precision_metadata to metrics.json.
   - Then SHIP 6 anchors: kf2_be1_fp32 / fp16 / int8 / int4 / int2 / int1.
     Use the same N=8192 Kerdock setup with only `--bit-precision` differing.
   - If KF-2 holds at INT4: retrofit and sweep KF-1, TCFT, Bet B (6 anchors each).
   - Justifies the 100-1000x deployment cost differentiation claim.

2. **Phase region C/D probe** (β > β_c unexplored; ~2 GPU days).
   - Region C: M < M_c, β > β_c (e.g. M_frac=4, β=64)
   - Region D: M > M_c, β > β_c (e.g. M_frac=12, β=64)
   - Run KF-1 / KF-2 / TCFT / Saad-Solla at each. 4 anchors per region.
   - The phase-lattice steerability story REQUIRES this data.

3. **KF-4 posterior-entropy rescue v4** (already routed at v269; ~half GPU day).
   - Apply KF-1 posterior-entropy mechanism to drift detection.

4. **Pre-existing queue anchors** that align with v269 strategy:
   - t1_beta_v3 / t2_codebook_v3 (axis resolution)
   - axis1 chunks 8/9/10 (boundary tail coverage)
   - saad_solla v18/v19/v20 / bet_b variants (Tier-1 reanchor)
   - bid_order_parameter_v5 N=12288 / N=16384 (use working v5 variant,
     NOT the timeout-prone v3/v4 normalized family)

Tier-2 (ship second wave after Tier-1 results, ~1 week):

5. **Experiment 6 unprobed-regime survey** (5 cheap probes; ~3 GPU days).
   - cleanup-strength sweep
   - time-dependent driving (periodic edit-query cycles)
   - very-low-M (M_frac < 1.0)
   - very-high-β (β > 100)
   - very-large-N where possible (N=16384 with checkpoint)

6. **Experiment 1 full KF x phase-region map** (4-5 GPU days, ONLY if Tier-1
   region C/D probe shows qualitatively different behavior).

7. **BE-2 bits-per-stored-fact info-theoretic comparison** (~1 GPU day).

Tier-3 (multi-week engineering tracks; parallel to GPU work):

8. **LLM-1 baseline impl** (Phase-2 of harness; ~1 week to add ROME baseline).
9. **LLM-3 retrieval vs vector DB** (commercially significant; ~2 weeks).
10. **LLM-6 hallucination benchmarks** (validates KF-1 elevation; ~2-3 weeks).

EXPLICITLY DEFERRED (bandwidth):
- LLM-2 continual learning
- LLM-4 ICL
- LLM-5 generation quality

## Hard rules for exp_dev (4-layer)
- ASCII-only per [[feedback-ascii-only-in-scripts]]
- NO `_n<N>` in name unless command really passes `--N <N>` (60d2147)
- --timeout REQUIRED per [[feedback-per-experiment-timeout-required]]:
  `_n4096` >= 14400s, `_n8192` >= 21600s, batteries >= 86400s (PROT-019 tiers)
- All scripts honor HDLAB_EXP_NAME (7d39e13)
- REMOTE VERIFY each ship via SSH read-back
- Each anchor JUSTIFIED — reference cap_map row or v269 LIFT
- HIGH-importance status_log entry per [[feedback-for-you-tab-primary-channel]]

## When to fire
Trigger: orchestrator removes PAUSED files from both queue dirs after user
returns and confirms reset complete.

Until then: queue.json holds 23 pending anchors safely; do not modify.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
