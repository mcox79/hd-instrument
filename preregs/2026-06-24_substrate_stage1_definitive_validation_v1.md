# Pre-registration: substrate_stage1_definitive_validation_v1

**Date:** 2026-06-24
**Anchor:** substrate_stage1_definitive_validation_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23], **8 arms x 3 seeds**

## USER directive

"One final battery of tests to show definitively that these settings / what you've landed on work like you expect AND to test around the edges."

## Scientific question

Today's Stage 1 substrate arc landed several chain-grade ingredients independently (substrate-OWNED encoder + sparse-bipolar f=0.02 + rank-1 Hebbian W + role-tagged HRR + CRISPR append-only + Wave14R K50 + tau-gate refuse + audit-trail v3). This cell INTEGRATES them into ONE comprehensive substrate-native battery at production scale (N=8192) on synthetic concept data (no encoder leakage) with explicit edge probes.

If STAGE_1_CHAIN_GRADE_ALIVE (>=5 of 8 arms HARD_PASS), the substrate-product story is rigorously validated. If gaps revealed, we have a clean roadmap for Stage 2 attention.

## 8 arms (substrate-native; Lane 1)

1. **ARM_CORE_STORAGE_RETRIEVAL** at M=2000 — production-scale 1-hop recall sanity
2. **ARM_CAPACITY_EDGE_SWEEP** M in {500, 2000, 10000, 25000} — find capacity cliff
3. **ARM_MULTIHOP_WAVE14R_K50** K in {1,5,10,20,50} — sparse traversal at production
4. **ARM_COMPOSITIONAL_GEN_OBJ_AXIS** — Plate role-filler; reproduce +0.724 lift from CLEAN_v1
5. **ARM_COMPOSITIONAL_GEN_CROSS_SLOT** — subj+pred axis (expected HARD_FAIL; documents edge)
6. **ARM_CL_APPEND_ONLY_5_DOMAINS** — CRISPR append-only across 5 phases; forget~0 expected
7. **ARM_NOISE_ROBUSTNESS_SIGMA_SWEEP** sigma in {0.5, 1, 2, 4, 8} relative-to-key — find noise cliff
8. **ARM_REFUSE_GATE_HARD_DISCRIMINATOR** — tau-gate + joint-refusal training (sparse-bipolar f=0.02 keys)

## Pre-registered HARD bands (per task spec)

- **ARM_CORE**: top1 >= 0.95 at M=2000 (HARD_PASS expected; sanity)
- **ARM_CAPACITY**: M_cliff_at_95pct_min >= 5000 (descriptive PASS gate)
- **ARM_MULTIHOP**: K=20 top1 >= 0.85 AND K=50 top1 >= 0.40
- **ARM_COMP_OBJ**: lift_over_chance >= +0.50 (HARD_PASS; reproduces CLEAN_v1 +0.724)
- **ARM_COMP_CROSS_SLOT**: top1 - chance >= +0.30 (expected NOT to pass; HARD_FAIL acknowledged documents edge)
- **ARM_CL_APPEND_ONLY**: forget < 0.05 (CHAIN-GRADE expected)
- **ARM_NOISE_ROBUSTNESS**: sigma_cliff_at_80pct_mean >= 1.0 (descriptive PASS gate)
- **ARM_REFUSE_GATE**: refuse_acc_unknown >= 0.80 AND retention_known >= 0.95

## Cell-level verdict

- **STAGE_1_CHAIN_GRADE_ALIVE**: >=5 of 8 arms HARD_PASS at production with documented edges
- **STAGE_1_PARTIAL**: 3-4 arms HARD_PASS
- **STAGE_1_GAPS**: <=2 arms HARD_PASS (substrate Stage 1 has bigger problems than today suggests)

## Smoke evidence (informs band calibration)

Smoke at N=1024 / V_C=200 / 1 seed (wall 0.7s post-vectorization):
- ARM_CORE top1=1.000 (M=200; PASS sanity)
- ARM_CAP m_cliff=1500 / curve {100:1.0, 500:1.0, 1500:1.0} (PASS for smoke band)
- ARM_MULTIHOP per_K {1:0.77, 5:0.42, 20:0.22} (FAIL at smoke; expected — N=1024 noise floor; full N=8192 should clear bands per Wave14R reference)
- ARM_COMP_OBJ top5=0.700 lift=0.600 (PASS)
- ARM_COMP_CROSS top1=1.000 lift=0.980 (PASS at smoke; small V_OBJ + K_subj=5 makes it pass; full V_OBJ=50 is the discriminating regime per CLEAN_v1)
- ARM_CL forget=0.0000 p1_recall=0.200 cap=3x (PASS forget by construction)
- ARM_NOISE sigma_cliff=2.0 / per_sigma {0.5:1.0, 2.0:1.0} (PASS; relative-to-key noise scaling fixed)
- ARM_REFUSE refuse=1.0 retention=0.0 tau*=0.05 (FAIL at smoke; tau-sweep tie-degeneracy on small split; full V_K=200/V_U=80 + joint-train margin>=0.05 should resolve)

Smoke partial PASS count = 5/8 = mechanically STAGE_1_CHAIN_GRADE_ALIVE at smoke. Full N=8192 expected to PASS MH + REFUSE (resolving smoke failures), CROSS_SLOT expected to FAIL (per CLEAN_v1) → cell expected to land at 5-6 of 8 PASS at full → STAGE_1_CHAIN_GRADE_ALIVE most likely.

## Calibration rationale

- ARM_CORE / ARM_COMP_OBJ / ARM_CL bands directly from chain-grade reference cells today (substrate_concept_kg_storage_retrieval_v1 / substrate_compositional_generalization_CLEAN_v1 / substrate_cl_crispr_append_only_v1).
- ARM_MULTIHOP bands from Wave14R K50 reference (K=20 top1>=0.85 per phase14r reference; K=50>=0.40 generous floor accounting for substrate-native synthetic vs the original concept-domain setting).
- ARM_REFUSE bands directly from substrate_tau_gate_refuse_training_v1 (refuse_acc>=0.80, retention>=0.95).
- ARM_CAP / ARM_NOISE are descriptive — they identify cliffs and PASS if the cliff is above a substrate-native useable threshold.
- ARM_COMP_CROSS_SLOT band pre-reg'd to FAIL (lift>=0.30 is the bar; expected lift<0.30) per CLEAN_v1's findings; documents the substrate edge honestly.

## Apples-to-apples checklist (master bias)

- **Lane 1 declared**: substrate-native capability.
- **All arms use SAME substrate primitives**: sparse-bipolar f=0.02 + 1/sqrt(fN) amplitude (where sparse used) + rank-1 Hebbian outer-product W + role-tagged HRR binding (Plate canonical).
- **SYNTHETIC data only**: no text8 / no Pythia / no word2vec / no bge encoder (no encoder leakage per Stage 1 foundations memory).
- **Single primary metric per arm**: declared in arm docstring and metrics.json.
- **CONFOUND_AUDIT per arm**: chance baseline reported; per-seed entries; cv across seeds.
- **By-construction-saturation guards**: ARM_CL forget=0 is by-construction (orthogonal slabs); flagged in arm result + cell verdict.
- **Corpus provenance**: synthetic random concept graphs; reported per-arm.
- **NO transformer/word-bigram baselines** — Lane 1 substrate-native only.

## D1 roofline probe (per Skunkworks TIMEOUT drill)

D1 probe at FULL N=8192 (measured directly):
- CAP M=25k ingest: 17s
- MH 1-trial K=50 cleanups: 44s (NAIVE per-chain sequential; VECTORIZED below to ~0.4s/trial)
- REFUSE joint-train naive 5x200 np.outer: 591s (VECTORIZED below to ~0.5s/iter)

**Vectorization adopted** (mandatory after D1 measurement):
- ARM_MULTIHOP: lockstep chain advance (all 50 chains per trial advance hop-by-hop in 1 batched matmul) → ~50x speedup
- ARM_REFUSE: batched outer-product (E[o_b].T @ keys_b) per iter instead of 200 np.outer calls → ~1000x speedup

Per-seed FULL wall estimate (vectorized): CORE 1s + CAP 20s + MH 40s + COMP 2s + CL 2s + NOISE 1s + REFUSE 2s = **~70s/seed × 3 seeds = ~210s total ~3.5 min**.

**timeout_s = 1800** (30 min) gives ~8x safety margin against measured wall.

## D2 checkpoint + atexit

- Per-seed `partial_seed{seed}_{run_mode}.json` with CONFIG_VERSION gate (smoke partials rejected in full mode by design — different SEEDS list).
- Atomic write via `.tmp + os.replace`.
- `atexit` hook writes `exit_heartbeat.json` with completion timestamp + n_seeds completed (D2 mandatory per TIMEOUT drill).

## N-suffix section

Anchor has NO `_n<N>` suffix; PROT-018 N/A. Production N_DIM=8192 declared in script's FULL config block (RUN_MODE != "smoke" branch).

## REQUIRED_FIELDS (queue gate)

Cell emits `metrics.json` with: `anchor_name`, `verdict`, `verdict_msg`, `run_mode`, `n_seeds`, `config_version`, `per_seed` (list, one entry per seed × all 8 arms), `elapsed_s`, `summary`, `DESIGN_NOTE`, `config` (per-arm grids).

## Fix #28 discipline note

The cell's verdict logic reads per-seed per-arm metrics and aggregates ACROSS seeds; the verdict_msg explicitly cites per-arm means + cv (not just a summary string). Skunkworks / cert-owner should re-derive each cited number from per_seed before tiering. The cell-level verdict (STAGE_1_*) is descriptive of the integrated battery, NOT a single chain-grade cert claim — per-arm Skunkworks-VET decides chain-grade status of each individual arm.

## What this cell DOES NOT do (scope)

- Does NOT test substrate-as-LM (token-level BPC; out-of-scope per Lane 1).
- Does NOT integrate audit-trail v3 (separate cell substrate_audit_trail_pipeline_integration_v1 covers that).
- Does NOT include isotonic calibration arm (cell-author Step-0 analytic predicted HARD_FAIL; skipped to avoid known false-floor).
- Does NOT test the Stage 1 encoder choice (substrate-OWNED encoder uses random codebooks here; substrate_encoding_shotgun_native_v2_BUGFIX is the encoder-comparison cell).

The 8 arms cover STORAGE + RETRIEVAL + MULTI-HOP + COMPOSITION + CL + NOISE + REFUSE = the substrate-product MEMORY+COMPOSITION+RETRIEVAL story. Encoder choice + LM probability + audit trail are separate cells in flight.
