# c3 compressed-sequence-replay v1 — DISPATCHED

**Date:** 2026-06-22T15:16Z
**Cell:** `experiments/exp_c3_compressed_sequence_replay_v1.py`
**Cell commit:** `a27939c5`
**Pre-reg:** `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (commit `4affa96e`)
**Queue:** `remote_cpu_queue` (entry `c3_compressed_sequence_replay_v1`)
**Status at dispatch:** RUNNING on cpu_runner_0 on marsh@home
**Timeout budget:** 3600s
**Author:** Exp-Dev (single-spawn pipeline per Fix #11 template)

## What this cell tests

Brain-drill #5 sequence-binding primitive. Given K=20 facts ingested as point writes
to W, does an offline "sleep" pass over U1 that Hebbian-binds ordered adjacent pairs
(k_{t-1}, k_t) into a separate sequence matrix S enable substrate sequence-recall
that pure point-writes cannot do?

4-arm discriminating regime (Fix #16):
- **NONE** -- no sleep pass; baseline (predicted recall <= 0.20)
- **COMPRESSED** -- ordered adjacent pairs into S (the proposed mechanism;
  predicted recall >= 0.80 at depth 5)
- **UNORDERED** -- same total pairs, random within-sequence (tests whether ORDER
  is load-bearing; predicted < COMPRESSED by >= 0.30)
- **ONLINE_NO_GAP** -- ordered pairs at ingest, no offline pass (tests whether
  the OFFLINE schedule matters in software; honest scope: software has no
  Hebbian window, so D ~= B is the predicted HARD_PASS_PLUS outcome)

## Smoke + timing measurement

Local smoke (K=8 N_DIM=1024, single seed): HARD_PASS in 0.8s.
- NONE d5 = 0.000 (correct null)
- COMPRESSED d5 = 1.000 (mechanism fires)
- UNORDERED d5 = 0.000 (order discriminator confirms order-binding mechanism)
- ONLINE_NO_GAP d5 = 1.000 (honest scope confirmed: software has no Hebbian window)
- delta(B-A) = 1.000; order_delta(B-C) = 1.000
- substrate_only=True (zero LLM calls); W_unchanged=True (sleep pass does not
  modify W matrix — assertion holds)

Full-config single-seed measurement (Fix #17, MANDATORY pre-full-dispatch):
- N_DIM=4096, K=20, N_SEQ=10, 4 arms, 5 depths, 40 probes/depth
- Single-seed wall: **84s** (vectorized W/S via K^T@K matmul)
- Full-grid extrapolation (3 seeds): ~252s ≈ **~4.5 min**
- Well within drill estimate (~5 min remote_cpu) AND well within 3600s timeout

Full-config single-seed result (already at ceiling — not a harness mis-spec, the
mechanism is just decisive at α=200/4096=0.05 load):
- COMPRESSED: 1.0 at every depth [1, 3, 5, 7, 10]
- NONE: 0.0 at every depth
- UNORDERED: 0.125 at d1, 0.0 at d3+ (order discriminator firing at depth)
- ONLINE_NO_GAP: 1.0 at every depth (matches COMPRESSED; honest scope confirmed)

## SCHEMA-VET self-check (pre-dispatch)

- [x] ANCHOR_NAME / CONFIG_VERSION / _LLM_CALL_COUNTER module-level Assign nodes
- [x] run_mode detection: --smoke / HDLAB_RUN_MODE / HDLAB_EXP_NAME `_smoke` suffix
- [x] per_unit per (seed, arm, depth) in metrics.json
- [x] cv across seeds computed in verdict()
- [x] Pre-reg direction enforced (B > A; B > C; W unchanged)
- [x] 4-arm discriminating regime (Fix #16); CAN-fail check + ceiling check in detail
- [x] Substrate-only-decode gate (`zero_llm_calls_at_inference` logged + checked)
- [x] atexit + SIGTERM synthesize-from-partials (TODO #9 pattern)
- [x] allow_synthetic=True correctly justified (by-design synthetic-bipolar keys;
      `CORPUS_PROVENANCE = "synthetic_bipolar_keys_sequences"` recorded)
- [x] Resumable via `_seed_checkpoint` with PROT-021 config-mismatch guard
- [x] ASCII-only (no unicode)
- [x] Self-tests pass (NONE_d1 <= 0.30; COMPRESSED_d1 >= 0.60; LLM=0)
- [x] Remote `--self-test` PASS in 2.9s post-SCP (confirmed by queue_add gate)
- [x] Pre-reg note committed pre-dispatch (commit `4affa96e`)
- [x] Cell file committed pre-dispatch (commit `a27939c5`)
- [x] Pause flag re-checked immediately before queue_add (absent)

## Pre-reg bands (recap)

**HARD_PASS:** B_d5 >= 0.80 AND A_d5 <= 0.20 AND delta(B-A) >= 0.50 AND
B - C >= 0.30 AND cv <= 0.05 AND zero LLM calls AND W unchanged.

**MIDDLE_BAND:** B_d5 in [0.50, 0.80) with delta(B-A) >= 0.30.

**HARD_FAIL:** delta(B-A) < 0.20 OR C >= B (order doesn't matter; just pair-density)
OR substrate-only-decode gate violated OR W modified by sleep pass.

## Asks (post-land)

- **Skunkworks:** independent landed-VET — re-derive numbers from per_unit; verify
  corpus provenance recorded; check substrate-only gate; ratify or adjust verdict;
  A5-gated Store write if chain-grade; route negative to Research if not chain-grade.
- **Research:** if HARD_PASS, the c3 + drill #1 kWTA composition is the next
  natural cell (real-token bigram-gap closure path); if HARD_FAIL, USER STANDING
  symmetric revival routing — alternative binding primitives (HRR convolution,
  FHRR) per drill #5 Prediction 5.

## Honest scope (mandatory)

The cell tests sequence-binding via ordered-pair outer-products on synthetic
bipolar keys with DISJOINT keys across sequences. The result generalizes to
"Hebbian-superposition substrate with disjoint-key sequences." It does NOT yet
generalize to real-token LM decode (Phase 2 c3_real_tokens), reused-key sequences
(capacity bound on S unknown), or compositional inference chains (drill #3 follow-on).
The biological MOTIVATION for compression (Hebbian window 200ms) does NOT directly
transfer to software; what transfers is the ARCHITECTURE (separate sequence
matrix, ordered-pair Hebbian writes). The Arm D ONLINE_NO_GAP control makes this
explicit in the pre-reg.

## Artifacts

- Cell: `experiments/exp_c3_compressed_sequence_replay_v1.py` (commit `a27939c5`)
- Pre-reg: `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (commit `4affa96e`)
- Local smoke metrics: `data/exp_c3_compressed_sequence_replay_v1_smoke/metrics.json`
- Local timing-run metrics: `data/exp_c3_compressed_sequence_replay_v1_timing/metrics.json` (single-seed dry-run for Fix #17 measurement; not the cert-candidate)
- Full metrics (pending): `data/exp_c3_compressed_sequence_replay_v1/metrics.json` after remote land

-- Exp-Dev, single-spawn experiment-lifecycle per Fix #11 pipeline template.
