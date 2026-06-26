# Pre-reg: substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure

**Date:** 2026-06-25
**Anchor:** substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure
**Cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only.py
**Queue:** remote_cpu_queue (numpy CPU; matmul-bound; structurally-identical to v2b minus V phase scan)
**Run-mode:** full (self-test PASS; V=10000-only single-V scan)
**Author:** Exp-Dev (cell author; dispatches via tools/orchestrator/queue_add.sh)
**Parent cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py
**Parent prereg:** preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md

## Why v2c (substantive scope change vs v2b)

v2b shipped a 4-arm V phase-diagram scan over V_GRID = [200, 1000, 4000, 10000]
with 3 seeds and N_TRAIN = V * 100. It hit the 3h timeout at 9/12 phase points
completed (V=200, V=1000, V=4000 across seeds 7/17/23). V=10000 did not complete
on any seed -- the V=10000 cells were the dominant cost because N_TRAIN at
V=10000 was 1M tokens (4x V=4000) and Hebbian outer-product builds + held BPC
both scale with N_TRAIN.

v2c closes the V=10000 phase point ONLY:

1. **V_GRID = [10000] ONLY** (no phase scan; single V value).
2. **N_TRAIN locked to 400000** (NOT V*100 = 1M per v2b's rule). This is the
   load-bearing scope narrowing: the wall budget now estimates 1-2h/seed x 3
   seeds = 3-6h, within the 4h timeout = 14400s buffer with --timeout 14400.
3. **Same 4 arms** (RANDOM / OLSHAUSEN / DEEPWALK / KOHONEN).
4. **Same 3 seeds** [7, 17, 23] (apples-to-apples with v2b for merge).
5. **Same other config** (N_DIM=8192, SPARSE_F=0.02, K_WTA=5, INGEST_CHUNK=8192).
6. **CONFIG_VERSION schema retag:** `subUnsupAnisBio-v2c-V10000_ONLY_CLOSURE`.

## Key finding from v2b 9/12 partials (motivates v2c band design)

The biology arms in v2b show a **CAPACITY-DEPENDENT phase transition** NOT a
uniform Mu-Viswanath confirmation, when read off top1 accuracy:

| V    | N/V  | DeepWalk lift  | Olshausen lift |
|------|------|----------------|----------------|
| 200  | 41   | +0.061         | +0.030         |
| 1000 | 8.2  | +0.011         | +0.011         |
| 4000 | 2.0  | -0.011         | +0.006         |
| 10000| 0.82 | UNKNOWN        | UNKNOWN        |

(N/V = N_TRAIN / V = ratio of tokens-seen-per-vocab; in v2c at N_TRAIN=400000,
V=10000 -> N/V = 40 measured-in-tokens but only 0.82 if normalized to the
v2b V=10000 design which would have had N_TRAIN=1M = N/V=100. v2c's
N_TRAIN_FIXED=400000 means N/V=40 = mid-regime vs v2b's V=200 N/V=41 and
v2b's V=1000 N/V=8.2 -- so the per-token data-richness is closer to v2b
V=200, but the vocab is the largest yet at 10000.)

**Predictions at V=10000 with v2c's N_TRAIN=400000:**

- DeepWalk hurts more (capacity-tight; bigram-graph structure can't be
  encoded into a vocab 5x denser than v2b V=4000), OR
- All 4 arms collapse into a narrow band (capacity exhausted; mechanism no
  longer discriminates), OR
- Surprising biology arm revival because 400k training tokens give Olshausen
  / Kohonen enough updates per output dim to differentiate (revival angle).

## Pre-reg HARD bands at V=10000 (PROSPECTIVE; locked at module init via assert)

The v2c V=10000 classifier operates on **top1 accuracy** (not BPC) because:
1. At V=10000 the BPC of all arms is in the ~log2(10000) = 13.3 limit
   regime where small relative BPC differences are noise-dominated.
2. top1 accuracy is more robust at the capacity-tight regime (Q discipline,
   2026-06-24 BIAS-13).
3. Random-chance top1 = 1/V = 1/10000 = 1e-4; a real signal needs to be
   measurably above this floor with tight CV.

The v2b BPC-based per-arm classifier is **PRESERVED for cross-cert continuity**
(reads same metrics; runs alongside the v10k top1 classifier).

### v2c V=10000 cell-level classifications (top1-based)

- **HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED:** at V=10000,
  - DeepWalk top1 <= RANDOM_top1 - 0.005 (DeepWalk hurts), AND
  - |OLSHAUSEN_top1 - RANDOM_top1| <= 0.005 (Olshausen ties), AND
  - top1 cv <= 0.05 across 3 seeds on ALL 4 arms.
  -> Wave D revival angle CLOSED; substrate-product locks in WITHOUT biology
     encoder upgrade. Confirms capacity-dependent phase transition extends to
     production V (and continues v2b V=4000 trend monotonically).

- **HARD_PASS_BIOLOGY_ARM_REVIVAL:** at V=10000,
  - 1+ biology arm BEATS RANDOM by >= 0.005 absolute on top1, AND
  - top1 cv <= 0.05 across 3 seeds on ALL 4 arms.
  -> Wave D revival angle OPENS; Path C anisotropic encoder gets revival drill.

- **MIDDLE_BAND_ALL_CONVERGE:** at V=10000, all 4 arms within +/- 0.005 of
  RANDOM_top1. -> Capacity exhausted; structure no longer discriminates;
  informative null but no chain-grade story.

- **HARD_FAIL_NULL_AT_V10000:** all 4 arms top1 < 0.001 (i.e. all collapse
  to near-noise-floor; random_chance = 1e-4 here). -> Capacity exhausted
  BEFORE mechanism matters; cell breaks down before signal appears.

- **HARD_FAIL_CELL_BREAKS:** NaN at production matmul OR sigma0_recall < 0.5
  on ANY arm. -> Implementation broke at V=10000 scale; not a science finding.

- **MIDDLE_BAND (catch-all):** no v2c band fires cleanly; mixed signals or
  cv too high. -> Inconclusive.

### Per-arm-at-V classifier (UNCHANGED from v2b; v2b-cert-compat)

The v2b BPC-based classifier remains in `detail.classifications` for
cross-cert continuity. v2c bands take precedence for cell-level verdict
when V=10000 is present.

- HP_CHAIN_GRADE_BPC_LIFT >= 0.20 + sigma0 >= 0.95 + cv <= 0.05
- HP_BPC_LIFT >= 0.10 + sigma0 >= 0.90
- HF_NULL_BPC_BAND <= 0.05 + sigma0 >= 0.90
- CONFOUND_SIGMA0 < 0.90 (Skunkworks META_RULE_sigma0_cleanup_integrity_gate)
- HF_HURTS_BPC_GAIN >= 0.10

## P_deflated estimates

- HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED (predicted): 0.40
  (extrapolates the v2b V=200/1000/4000 monotonic trend; capacity-tight regime
  predicts biology hurts).
- HARD_PASS_BIOLOGY_ARM_REVIVAL (Wave D revival): 0.15
  (would require Olshausen / Kohonen to outperform random; mostly null priors
  except brain-prior modest +0.10 per USER 2026-06-22).
- MIDDLE_BAND_ALL_CONVERGE (capacity exhausted, narrow band): 0.30
  (all 4 arms cluster within +/-0.005 -- structure stops mattering).
- HARD_FAIL_NULL_AT_V10000 (full collapse): 0.05
  (low; v2b V=4000 didn't collapse; capacity tight but not gone).
- HARD_FAIL_CELL_BREAKS (NaN / sigma0 breakdown): 0.05
  (low; v2b V=4000 didn't break; NaN protection preserved from v2b).
- MIDDLE_BAND catch-all: 0.05
  (low; band coverage is meant to be exhaustive).

## Composition with existing v2b partials

The 9/12 partials from v2b remain valid evidence (V=200/1000/4000 across
seeds 7/17/23). v2c adds V=10000 across seeds 7/17/23 = 3 new partials.

**Final phase-diagram analysis (after v2c lands):**
- Combine v2b 9 partials + v2c 3 V=10000 partials = 12 phase points total.
- Plot per-arm top1 lift vs N/V ratio across V in [200, 1000, 4000, 10000].
- Read off whether v2b's monotonic phase-transition trend extrapolates.

Note: v2c uses N_TRAIN=400000 at V=10000 (vs v2b's V*100=1M). This is a
scope change; the trend-extrapolation is qualitative not quantitative. If
v2c V=10000 shows the predicted DeepWalk negative-lift behavior, the
extrapolation is confirmed despite the N_TRAIN difference. If v2c shows
revival, USER may want a follow-up cell at N_TRAIN=1M to disambiguate.

## Discriminator at V=10000

- random_chance top1 = 1/V = 1/10000 = 1e-4.
- v2b V=4000 RANDOM top1 was ~0.04 (well above random_chance 1/V=2.5e-4).
- Expected v2c V=10000 RANDOM top1: ~0.01-0.02 (capacity-tighter regime).
- 0.005 absolute lift in top1 is meaningful in this regime (50% relative
  effect on top of a 0.01 baseline).

## Operating disciplines

- **D2 atexit + per-(V, seed) checkpoint** MANDATORY (atexit synth recovers
  partials on timeout; per-(V=10000, seed) units written via
  `_seed_checkpoint.write_partial_key`).
- **Self-test gate** PASS LOCALLY before commit + dispatch (T1-T9 including
  v2c-NEW T6a/b/c/d/e v10k cell-level classifier coverage).
- **Pre-flight smoke gate** at V=2000, 1 seed, locally on `.venv` (matmul
  scale-up infrastructure test; <30s wall).
- **Pre-reg + cell committed BEFORE dispatch** (uncommitted laptop notes
  invisible to autonomous pipeline -> GATE_FAIL prereg-not-found).
- **Path-scoped commits** (no `git add -A`; canonical Store in repo).
- **ASCII only** (no unicode in scripts or verdict_msg).
- **Per Fix #28:** per-arm metrics in `detail.by_arm_V_agg`; verdict_msg
  cites them; load-bearing classifier reads metrics not msg.
- **Per Fix #20:** no pipe-tail subprocess monitoring (atexit synthesizer
  + mtime polling).
- **Per Fix #17:** timeout = 14400s (4h) for V=10000 x 3 seeds full run.
  Wall budget estimate: 1-2h/seed x 3 seeds = 3-6h; 4h cap is safety
  buffer; atexit synthesizer recovers partial (V=10000, seed) units on
  timeout.
- **Per Fix #26 (pre-dispatch verify-the-referent):** PROCEED (anchor
  new; 0 prior landings; 0 prior atoms; no duplicate-dispatch risk).
- **Per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm:**
  sigma0 < 0.90 triggers CONFOUND_FAIL FIRST before any mechanism claim.
  v2c HARD_FAIL_CELL_BREAKS additionally fires on sigma0 < 0.50.

## Routing

- **Queue:** remote_cpu_queue (numpy CPU; matmul-bound; no torch).
- **Timeout:** 14400 seconds (4h).
- **Routing-sanity gate:** numpy script; no large-N literal (N_DIM=8192
  is below the 16384 routing-warn threshold). Clean route.
- **Push:** harness-DENIED; dispatch via `tools/orchestrator/queue_add.sh`
  which handles SCP + SSH + remote queue_add.py + post-ship verification.

## Self-test PASS evidence (LOCAL gate before commit)

Run `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only.py --self-test`:

Coverage:
- T1: char-trigram bipolar output
- T2: sparse_bipolar fraction-f exactness
- T3: all 4 arms produce shape + sigma0 cleanup >= 0.90 + isfinite all-true
- T4: anisotropy_diagnostic returns required keys
- T5: build_hebbian_W_np + path_a_bpc finite + positive + top1/top5 in [0, 1]
- T6a: v10k HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED fires
- T6b: v10k HARD_PASS_BIOLOGY_ARM_REVIVAL fires
- T6c: v10k MIDDLE_BAND_ALL_CONVERGE fires
- T6d: v10k HARD_FAIL_NULL_AT_V10000 fires
- T6e: v10k HARD_FAIL_CELL_BREAKS fires (sigma0 < 0.5)
- T7: v10k band-threshold constants are exactly the prereg values
- T8: per-(V, seed) checkpoint key shape composes
- T9: V_GRID_FULL = [10000] only AND N_TRAIN_FIXED = 400000 (scope-lock)

## Pre-flight smoke (V=2000; 1 seed; expected <30s wall)

Smoke is structurally-identical to v2b V=200 smoke but at V=2000 to
exercise the scale-up infrastructure tested for the V=10000 tail.
Validates NaN-free at scale-up matmul before paying the production V=10000
wall.

## Cites

- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py
  (immediate parent; structurally identical except V_GRID + N_TRAIN scope)
- preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md
  (parent prereg; per-arm-at-V BPC classifier ported verbatim)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py (original v1 base)
- experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py (rail 7.3065 reference; v2c dormant V=4000)
- Olshausen-Field 1996 Nature 381:607-609 (V1 sparse coding)
- Moraitis et al. 2107.05747 (SoftHebb forward-only Hebbian)
- Perozzi et al. 2014 (DeepWalk)
- Kohonen 1982 (SOM topographic maps)
- USER directive 2026-06-25 (basis-vs-use-case)
- USER directive 2026-06-22 (substrate-native; no labels at basis)
- Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm
- Mu-Viswanath spectrum-of-decisions framework (capacity-tight regime expected to suppress anisotropy lift)

-- Exp-Dev
