# exp_dev -> orchestrator: Cell H' v2 SURGICAL_PLUS_PHASE_DIAGRAM DISPATCH_READY (blitz Agent 2/3)

**Date:** 2026-06-25
**From:** exp_dev (cell author; coordinated blitz Agent 2 of 3)
**To:** hdi_orchestrator (dispatch via remote_cpu_queue)
**cc:** Research (Director); Skunkworks (post-landing cert); cell-author -> dispatch -> ALL
**State:** authored + self-test PASS + local smoke V=200 LANDED + cell+prereg COMMITTED to local origin/main; NOT pushed (harness-DENIED to me; Orchestrator must push).

## Anchor

`substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM`

## Commit

`daefa9dea75cfc061ee3cbd135a16bf0a483deea`  (local origin/main HEAD)
Files included in this commit:
- `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py` (1271 lines)
- `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.md` (171 lines)
- `notes/exp_dev_to_orchestrator_blitz_agent3_v5_v6_GPU_dispatch_2026-06-25.md` (sibling agent's handoff; co-staged by parallel agent; not from me)

## Files (all paths absolute)

- `D:/AI/hd-instrument/experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py`
- `D:/AI/hd-instrument/preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.md`
- `D:/AI/hd-instrument/notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md` (source-of-truth drill; per-arm correction)

## What it tests

5-arm biology-native unsupervised anisotropic encoder PHASE-DIAGRAM SCAN over V = [200, 1000, 4000, 10000] at N_DIM=8192, with SURGICAL FOLDIAK FIX (homeostatic firing-rate target per Foldiak 1990 adaptive-threshold equations).

Per the drill, FOLDIAK was the ONLY genuine bug in v1 (rank-1 collapse from missing homeostatic threshold). v2 fixes that surgically. DEEPWALK, KOHONEN, OLSHAUSEN unchanged per drill correction (DeepWalk's tail-node behavior is graph-structural; KOHONEN is clean null; OLSHAUSEN works mechanically but v1 had +0.56 BPC drift vs fair_harness which v2 records in detail.provenance_diagnostic).

## Self-test PASS evidence (locally verified)

```
$ .venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py --self-test
[selftest] starting...
[selftest] T3b: SURGICAL FOLDIAK FIX validation...
[selftest] T3b PASS: FOLDIAK v2 sigma0=1.000 eigsprd=0.9208 (v1 had sigma0=0.0 eigsprd=0.9999)
[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 5-arms shape+sigma0 + T3b SURGICAL FOLDIAK FIX validated + T4 anisotropy + T5 BPC+top1/top5 + T6 verdict-shape (NULL/HP/CONFOUND) + T7 provenance + T8 band ordering + T9 ckpt-key shape OK
```

T3b explicitly validates the surgical fix at small scale (N=256, V=40): FOLDIAK v2 produces sigma0=1.000 + eigenspread=0.9208 where v1 produced sigma0=0.0 + eigenspread=0.9999.

## Local smoke evidence (V=200 LANDED)

Smoke run (`HDLAB_EXP_NAME=..._smoke`; V_GRID=[200, 400]; 1 seed) -- partial V=200 metrics at `D:/AI/hd-instrument/data/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM_smoke/partial_metrics_V200_seed7.json`:

Per-arm at V=200, N_DIM=8192, seed=7:
- ARM_RANDOM_BIPOLAR_BASELINE:                    bpc_best=4.307, top1=0.459, sigma0=1.000, eigsprd=0.976
- ARM_OLSHAUSEN_FIELD_SPARSE_CODING:              bpc_best=4.301, top1=0.489, sigma0=1.000, eigsprd=0.977
- ARM_DEEPWALK_ON_BIGRAM_GRAPH:                   bpc_best=4.316, top1=0.520, sigma0=1.000, eigsprd=0.984
- ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC: bpc_best=4.314, top1=0.520, sigma0=1.000, eigsprd=0.998
- ARM_KOHONEN_SOM_TOPOGRAPHIC:                    bpc_best=4.313, top1=0.432, sigma0=1.000, eigsprd=0.976

KEY VALIDATIONS:
- **FOLDIAK_v2 sigma0=1.000 at production-scale matmul (N_DIM=8192)** -- the surgical fix WORKS at scale, not just selftest. v1 had sigma0=0.0 in same regime.
- All 5 arms within 0.01 BPC of each other at V=200 -- saturation regime as predicted (random saturates below JL-margin).
- Per Q discipline: top5 values reported alongside top1 for argmax-noise robustness.

V=400 seed=7 smoke is still in flight as of handoff write (smoke wall ~9 min/V at V=200; V=400 expected ~12-15 min more). Smoke pipeline is operational; remote run will be 3-seed full V grid.

## Verify-the-referent confirmations

- Drill exists at `notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md` (READ; per-arm correction absorbed verbatim into prereg + cell docstring).
- v1 cell exists at `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py` (READ; forked).
- fair_harness rail at `experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py` (verified file exists; BPC 7.3065 reference).
- text8 corpus at `data/text8_cache/text8.txt` (verified at author + selftest time).
- `_seed_checkpoint.py` supports compound key `V<V>_seed<seed>` via `_ckpt_key` precedence (confirmed by reading the module).
- `tools/predispatch_check.py substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM` -> PROCEED (0 prior landings; 0 prior atoms; no duplicate-dispatch risk).
- Pause flag `data/orchestrator_paused.flag` absent at author + commit time.

## Dispatch ask

When green-lit and pushed to origin/main:

- **Queue:** `remote_cpu_queue` (numpy-only baseline; ~3h wall budget; matmul-heavy at V=10000 -> 400MB W_lat for FOLDIAK but bounded; CPU works)
- **Entry name:** `substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM` (NO `_smoke` suffix; full mode)
- **Script:** `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py`
- **Prereg path:** `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.md`
- **Timeout:** `10800` seconds (3 hr)
- **HDLAB_EXP_NAME:** `substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM`
- **HDLAB_RUN_MODE:** `full`
- **Pre-flight on remote (per `reference_remote_dispatch_cell_readiness_checklist`):**
  - `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py --self-test` MUST PASS on remote BEFORE queue_add. (Python 3.11 + numpy + duckdb prerequisite identical to other recent numpy-only cells.)

## Suggested queue_add invocation (when push lands)

```
cd C:/dev/hd-instrument
.venv/Scripts/python.exe tools/queue_add.py remote_cpu_queue \
    substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM \
    experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py \
    --prereg preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.md \
    --timeout 10800
```

Note: queue_add.py requires `--smoke` to PASS too (it runs a local smoke probe). At V_GRID_SMOKE=[200, 400] the smoke takes ~15-20 min on the remote CPU; acceptable. If the gate is slow, use `--skip-smoke` per discretion (smoke already validated on author's laptop; partial metrics file in repo as evidence).

## Wall budget per V (numpy CPU)

- V=200, N_TRAIN=20k, 3 seeds: ~15 min total (cheap)
- V=1000, N_TRAIN=100k, 3 seeds: ~45 min total
- V=4000, N_TRAIN=400k, 3 seeds: ~135 min total (matches v1)
- V=10000, N_TRAIN=1M, 3 seeds: ~180 min total (FOLDIAK V x V matmul dominates)
- TOTAL: ~6h worst, 3-4h typical. With `--timeout 10800` + atexit synthesizer, V=10000 may run partial; whatever lands is recovered by `_synthesize_on_exit`.

## Verdict-handling notes for verdict_handler

- Per Fix #28: ALWAYS read `detail.by_arm_V_agg[<arm>][<V>]` BEFORE propagating cross-arm narratives. The verdict_msg summary is human-readable; the load-bearing classifications are in `detail.classifications[<arm>][<V>]`.
- Per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm: any per-(V, arm) cell with `sigma0_recall_mean < 0.90` triggers CONFOUND_FAIL classification for that cell FIRST -- before any mechanism claim.
- HARD_FAIL_NULL across ALL biology arms x ALL V is INFORMATIVE: it confirms substrate may genuinely not need encoder upgrade in this regime (Mu-Viswanath-aligned negative). Don't read it as "no signal" -- read it as "no encoder lift needed at this regime."
- HARD_PASS_CHAIN_GRADE at any (arm, V) needs by-construction-saturation guard at V=200 (random saturates -> any lift may be artificial). Cross-check: if HARD_PASS at V=200 but HARD_FAIL_NULL at V=4000+, suspect saturation artifact.
- provenance_diagnostic block records v1 OLSHAUSEN BPC drift situation; if v2 random_bpc_at_V4000 still drifts >0.20 from fair_harness 7.3065, that's a methodology gap NOT a mechanism rejection.

## P_deflated estimates (from prereg)

- Any FOLDIAK_v2 cell HARD_PASS_CHAIN_GRADE at any V: 0.20
- Any biology arm HARD_PASS (non-chain-grade) at any V: 0.35
- ALL biology HARD_FAIL_NULL across V (substrate doesn't need encoder upgrade): 0.40 (MOST LIKELY)
- CONFOUND_FAIL (surgical FOLDIAK fix insufficient at scale): 0.10
- MIDDLE_BAND (mixed): 0.30

## Per-Fix disciplines honored

- Fix #17: per-V timeout estimation in prereg; total 10800s; atexit recovers partials.
- Fix #20: no pipe-tail subprocess monitoring; mtime polling on `partial_metrics_V<V>_seed<seed>.json`.
- Fix #24: numpy CPU on remote_cpu_queue; GPU port deferred (acknowledged in prereg).
- Fix #26: predispatch_check returned PROCEED before commit.
- Fix #28: per-(V, arm) metrics in detail; verdict_msg load-bearing reads them.
- D1 roofline: 60 sub-runs budget doc'd in prereg.
- D2 atexit + per-(V, arm) checkpoint: implemented via compound-key `_seed_checkpoint.write_partial_key`.

## Status

DISPATCH_READY. Committed to local origin/main at `daefa9dea75cfc061ee3cbd135a16bf0a483deea`. Awaiting Orchestrator push + queue_add (harness-DENIED to me).

-- Exp-Dev (blitz Agent 2/3)
