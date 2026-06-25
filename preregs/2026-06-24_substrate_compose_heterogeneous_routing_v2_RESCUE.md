# Prereg: substrate_compose_heterogeneous_routing_v2_RESCUE

**Filed:** 2026-06-24 by exp_dev.
**Cell:** `experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE.py`
**Routing:** local_cpu_queue or remote_cpu_queue (~22min full wall extrapolated by D1 probe)
**Timeout:** 3600s (60min) -- D1 probe says 1308s extrapolated; budget ~2.75x for safety

---

## Strategic context (continuation from TIMEOUT-class drill)

v1 cell (`exp_substrate_compose_heterogeneous_routing_v1.py`) TIMED OUT at 3600s, producing
ZERO information. v1 seed 7 partial (per `data/exp_substrate_compose_heterogeneous_routing_v1/partial_metrics_7.json`)
took 3074s ALONE at N_DIM=8192 N_TRAIN=100k, so 3 seeds would have needed ~9200s.

Per TIMEOUT drill (`notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` ANCHOR 2 +
`notes/research_timeout_class_revival_disparate_fields_2026-06-24.md`): apply disparate-fields
rescue pattern -- smaller units + partial results + new D1/D2 disciplines.

### Mechanism under test (UNCHANGED from v1)

Three brain-canonical heterogeneous-routing composition architectures, all in one cell so
cross-arm comparison is the value:

1. **ARM_BASELINE_FAIR_HARNESS** -- single-bank Hebbian (sanity rail to fair_harness 7.3065)
2. **ARM_THETA_PHASE_TWO_W** -- two W banks, alternating-phase routing (cf-RPE phase 0,
   STDP phase 1, alpha-mixed readout)
3. **ARM_FREQ_ROUTED_K2** -- deterministic frequency-based routing (high-freq -> W_freq cf-RPE,
   low-freq -> W_rare cf-RPE+STDP)
4. **ARM_ORTHOG_SUBSPACE** -- Gram-Schmidt orthogonal subspace split (cf-RPE in subspace 1,
   STDP in subspace 2, concat decode)

If ANY of arms 2/3/4 HARD-PASSes, validates that the substrate's "cf-RPE +12% cap" (which
prior same-W-stacking cells found) is NOT structural -- heterogeneous routing breaks the cap.

## Scope reductions (RESCUE)

| Parameter      | v1        | v2_RESCUE | Rationale                                    |
|----------------|-----------|-----------|----------------------------------------------|
| N_DIM          | 8192      | 4096      | 4x matmul cost reduction (k=2.13 from probe) |
| N_TRAIN        | 100_000   | 50_000    | 2x training-step cost reduction              |
| N_HELD         | 20_000    | 10_000    | Recall cost reduction (small fraction)       |
| SEEDS          | [7,17,23] | [7,17]    | 1.5x seed-count reduction                    |
| N_STEPS/seed   | 1000      | 1000      | UNCHANGED (load-bearing for plasticity)      |
| VOCAB_CAP      | 4000      | 4000      | UNCHANGED (V-floor for discriminator)        |
| TEMP/LAMBDA grids | unchanged | unchanged | grids drive eval cost not training cost     |

Estimated per-seed wall: ~385s (1308s total). 1.5x safety -> ~2000s; choose timeout 3600s for headroom.

## PRE-REG HARD bands (INHERITED from v1 -- NOT loosened per drill)

| Band                       | Trigger                                                              |
|----------------------------|----------------------------------------------------------------------|
| **HARD_PASS_CAP_BROKEN**   | any of ARM_THETA / ARM_FREQ / ARM_ORTHOG BPC <= 6.95                 |
| **HARD_PASS_CHAIN_GRADE**  | best heterogeneous architecture BPC <= 6.80                          |
| **MIDDLE_BAND_PARTIAL**    | best heterogeneous BPC in [6.95, 7.05]                               |
| **MIDDLE_BAND_INTER_GAP**  | best heterogeneous BPC in (7.05, 7.30)                               |
| **MIDDLE_BAND_HIGH_CV**    | best het arm cv > 0.05 (seed-unstable)                               |
| **HARD_FAIL_DECISIVE**     | all 3 heterogeneous arms BPC >= 7.30                                 |
| **HARD_FAIL_PROVENANCE**   | ARM_BASELINE drifts > 0.05 from sanity rail 7.3065 (full mode only)  |
| **HARD_FAIL_LLM_CALL**     | any LLM forward call at inference (substrate-only invariant)         |
| **HARD_FAIL_D1_ROOFLINE**  | D1 roofline probe extrapolates wall > 0.8 * timeout (refuse cleanly) |

Sanity rail tolerance is +/- 0.05 BPC (full mode only -- smoke mode skips provenance).
CV gate (0.05) is mandatory on the best het arm.

## Discriminating-regime metrics (load-bearing, mandatory per drill C5)

| Arm                    | Metric                                | Threshold                                            |
|------------------------|---------------------------------------|------------------------------------------------------|
| ARM_THETA_PHASE_TWO_W  | enc_vs_ret_bank_corr                  | < 0.95 (banks must be distinct content)              |
| ARM_THETA_PHASE_TWO_W  | logit_enc_ret_corr_mean               | reported (per-query Pearson; informational)          |
| ARM_FREQ_ROUTED_K2     | freq_top1_differential                | >= 0.05 (high-freq vs low-freq must differ)          |
| ARM_ORTHOG_SUBSPACE    | orthog_residual_max                   | < 1e-3 (QR split actually orthogonal)                |
| ARM_ORTHOG_SUBSPACE    | cross_subspace_grad_corr_mean_abs     | < 0.70 (updates didn't leak across subspaces)        |

The discriminating metrics are REPORTED per seed (not gates). If they fail along with the
BPC outcome, the verdict_msg will say so; downstream interpretation by Skunkworks.

## NEW disciplines (per TIMEOUT drill D1 + D2)

### D1 ROOFLINE PROBE (mandatory pre-FULL gate)

Before running any FULL seed, the cell times ARM_FREQ_ROUTED_K2 (slowest arm per v1 metrics:
1351s of 3074s seed-7 wall = 44% of per-seed cost) at 3 N_DIM scales (N_DIM/4, N_DIM/2, N_DIM)
with V held at full VOCAB_CAP and N_STEPS reduced to 25. Fits power law t = a * N^k.
Extrapolates to full wall = 2.5 * freq_arm_extrap + 15s overhead per seed * n_seeds.

If extrapolated wall > 0.8 * timeout, the cell writes a HARD_FAIL_D1_ROOFLINE_REFUSE metrics.json
and exits cleanly (no full-run started). Tested locally: probe takes ~10s and predicts 1308s
for the 2-seed FULL at N=4096 (45% of 3600s budget) -> dispatch OK.

### D2 ATEXIT + per-seed checkpoint (mandatory partial-result preservation)

- `_seed_checkpoint.write_partial` already writes `partial_metrics_<seed>.json` atomically
  after EACH seed completes. Re-dispatch resumes from any seed > 0 already done.
- **New for v2_RESCUE**: module-level atexit handler holds a reference to the current-seed
  in-progress per-arm dict. On SIGTERM / timeout / process kill mid-arm, atexit flushes
  `partial_metrics_<seed>_atexit.json` so EVEN A MID-ARM INTERRUPTION leaves some data.
- PROT-021 config-mismatch guard active: `run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode":
  RUN_MODE}` passed to `resumable_seeds`/`aggregate_partials` -- a smoke partial in the same
  out_dir would be REJECTED (won't contaminate FULL aggregate).

## Self-test gates (16 mandatory; verified PASS locally)

ST1 cf-RPE shrinks error / ST2 STDP antisymmetry / ST3 Gram-Schmidt orthogonal split /
ST4 freq-ranks correct / ST5-8 each arm produces nonzero logits + finite discriminating /
ST9 4 arms diversity nonzero / ST10 joint_sweep returns finite / ST11 sparsify nnz /
ST12 LAMBDA_GRID excludes 0.0 / ST13 LLM-call counter = 0 / ST14 ARMS list consistency /
**ST15 D2 atexit handler registered** / **ST16 scope-reduction sanity (N_DIM=4096
N_TRAIN=50000 seeds=2)**.

## Smoke gate (verified PASS locally)

Smoke (N_DIM=1024, N_TRAIN=2000, V=300, synthetic Markov bigram corpus, 1 seed):
- HARD_PASS_CHAIN_GRADE_BONUS, best_het=ARM_FREQ_ROUTED_K2 BPC=6.2926 cv=0.0000
- BASE=5.9458, THETA=6.3791, FREQ=6.2926, ORTHOG=6.3913, uni=8.1936
- All 4 arms produce valid logits + valid discriminating metrics
- elapsed_s=2.35; all REQUIRED_FIELDS present
- Sanity rail FAILS in smoke (BASE=5.95 vs rail 7.31) -- expected; provenance check disabled in smoke

NB: smoke verdict reproduces v1 smoke exactly (same primitives, same code).

## D1 probe result (verified locally, 2026-06-24)

```
N=1024 wall=0.30s (V=4000, n_steps=25)
N=2048 wall=1.35s (V=4000, n_steps=25)
N=4096 wall=5.77s (V=4000, n_steps=25)
fit: a=1.22e-07 k=2.126
per_seed_wall_extrap=654s (all 4 arms); FULL wall_extrap=1308s (21.8 min, 2 seeds)
budget=2880s (0.8 * 3600s) -> DISPATCH OK
```

k=2.126 matches expected matmul-bound O(N^2) scaling on CPU.

## Honest scope / what this does + doesn't show

**Does show:** at reduced N_DIM=4096 + reduced N_TRAIN=50k, whether ANY of 3 heterogeneous-
routing architectures (theta-phase / freq-routed / orthogonal-subspace) drops substrate-LM
BPC below 6.95 (refuting cf-RPE +12% cap claim).

**Does NOT show:**
- Whether the cap holds at FULL v1 scope (N_DIM=8192, N_TRAIN=100k). At reduced N the
  heterogeneous discriminator MAY be weaker -- if MIDDLE_BAND lands, that itself is signal:
  het-routing benefit may scale WITH N (interesting capacity-bound).
- K > 2 routing variants (only K=2 architectures tested).
- Modern-Hopfield cleanup stacked on top of het-routing (orthogonal axis; deferred).
- Generalization beyond text8 V=4000 (corpus-specific).

## Verdict interpretation guide

- **HARD_PASS_CHAIN_GRADE_BONUS** (BPC <= 6.80): heterogeneous routing CONCLUSIVELY breaks
  the cf-RPE cap; route to Skunkworks for landed-VET + chain-grade certification.
- **HARD_PASS_CAP_BROKEN** (6.80 < BPC <= 6.95): same; slightly weaker margin.
- **MIDDLE_BAND_PARTIAL_SIGNAL** (6.95 < BPC <= 7.05): partial benefit; may justify rerun
  at full N to recover discriminator strength (route to Research for revival drill).
- **MIDDLE_BAND_INTER_GAP** (7.05 < BPC < 7.30): marginal; same MM treatment.
- **MIDDLE_BAND_HIGH_CV**: PASS-condition met but cv > 0.05; seed-unstable, NOT certifiable.
- **HARD_FAIL_DECISIVE** (all >= 7.30): cap may indeed be structural; pivot recommended
  (multi-scale hierarchical, hypernetwork, attention-as-compose).
- **HARD_FAIL_PROVENANCE**: encoder/Hebbian pipeline drifted from fair_harness baseline;
  pipeline integrity bug, investigate before re-dispatch.

## Cell-author discipline checklist

- [x] ASCII-only script (`feedback_ascii_only_in_scripts`)
- [x] Selftest exits 0 on `--self-test`
- [x] Smoke exits 0 + produces `metrics.json` with REQUIRED_FIELDS on `--smoke`
- [x] CONFIG_VERSION includes every BPC-affecting param
- [x] D1 roofline probe mandatory before FULL (`HDLAB_RUN_TIMEOUT_S` env honored)
- [x] D2 atexit handler + `_seed_checkpoint` per-seed checkpoint wired
- [x] PROT-021 config-mismatch guard active (`run_config` passed to checkpoint helpers)
- [x] LLM-forward-call counter = 0 asserted before metrics.json write
- [x] Fix #26 predispatch_check.py: PROCEED on both anchor + v1-keyword
- [x] Bands inherited from v1 spec (not loosened per drill instruction)
- [x] Verdict bands ASCII-checked; tier-naming matches Skunkworks downstream parser

## Cites

- `notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` (ANCHOR 2)
- `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md` (drill source)
- `experiments/exp_substrate_compose_heterogeneous_routing_v1.py` (v1 cell that timed out)
- `data/exp_substrate_compose_heterogeneous_routing_v1/partial_metrics_7.json` (v1 seed-7 partial)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (sanity rail 7.3065)
- `experiments/_seed_checkpoint.py` (per-seed checkpoint primitives)
