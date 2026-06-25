# PRE-REG: substrate_cross_layer_compose_LM_v2_RESCUE

**Date:** 2026-06-24
**Anchor:** `substrate_cross_layer_compose_LM_v2_RESCUE`
**Author:** exp_dev
**Routing:** local_cpu_queue OR remote_cpu_queue (CPU; word2vec encoder + matmul-bound)
**Predecessor:** `substrate_cross_layer_compose_LM_v1` (TIMED OUT at 3600s; 0 partials)

---

## TRIGGER

`exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` ANCHOR 1 (LOAD-BEARING).

The v1 cell timed out at 3600s wall and produced no partial metrics (zero
information). Per the TIMEOUT class drill (`research_timeout_class_revival_disparate_fields_2026-06-24.md`),
the dominant root cause is cell-author wall estimates anchored on smoke-N
roofline regime rather than full-N regime. Smoke at N=512 is bandwidth-bound;
full-N at N=8192 is compute-bound (matmul cost ~ batch * N^2 per step over
n_steps * n_arms * n_seeds). The v1 4x N scope-up at the regime boundary
likely caused 16-64x wall blowup.

This rescue scopes back to a roofline-aware mid-point AND adds two new
mandatory disciplines (D1, D2) that should prevent the same class of failure
on this and future cells.

---

## HYPOTHESIS (UNCHANGED from v1)

Cross-layer hierarchical stacking (independent W per hop) breaks the
composition collapse that catastrophically fails same-W stacking. A1 5-arm
joint at LM scale showed shared-W collapse (BPC 7.89 > unigram 7.738);
cross-layer at L=100 succeeded chain-grade (lacc=1.0).

The rescue tests whether the cross-layer architecture pattern transfers to
the LM regime at REDUCED-but-still-discriminating scale (text8 N_TRAIN=50k,
V=4000, N_DIM=4096).

If HARD_PASS at reduced scale, the cross-layer mechanism IS load-bearing for
LM composition and v1's TIMEOUT was purely a runtime engineering failure
(the science was sound). Follow-up cell could re-attempt the full-N config
at increased timeout budget.

If MIDDLE_BAND or HARD_FAIL at reduced scale, the cross-layer mechanism does
NOT cleanly transfer to LM regime — the v1 TIMEOUT was a (silent) signal of
intractability rather than only a runtime issue.

---

## ARMS (UNCHANGED from v1; 4 plasticity arms + unigram baseline)

1. **ARM_SINGLE_LAYER_CFRPE** — reference / sanity rail.
2. **ARM_2_LAYER_INDEPENDENT_CFRPE** — LOAD-BEARING. 2 layers, independent W.
3. **ARM_3_LAYER_INDEPENDENT_CFRPE** — depth scan; 3 layers, independent W.
4. **ARM_2_LAYER_SHARED_W_CFRPE** — CONTROL; validates same-W collapse pattern.

Plus ARM_UNIGRAM as zero-cost baseline.

---

## SCOPE REDUCTIONS vs v1

| Param     | v1     | v2_RESCUE | Rationale                                            |
| --------- | ------ | --------- | ---------------------------------------------------- |
| N_DIM     | 8192   | 4096      | Cuts matmul cost 4x; preserves vector-discrim regime |
| N_TRAIN   | 100k   | 50k       | Cuts ingest steps 2x; preserves LM-statistics regime |
| N_STEPS   | 1000   | 2000      | Doubles per-arm training compute as PER TASK SPEC    |
| SEEDS     | [7,17,23] | [7,17] | Cuts wall by 1/3; cv across 2 seeds still informative |

Net expected cost ratio: ~0.27x v1 wall (4096^2 / 8192^2 = 0.25x; 50k / 100k =
0.5x; 2000 / 1000 = 2.0x; 2 / 3 = 0.67x; product = 0.17x at matmul-bound,
~0.27x with overhead). v1 hit 3600s wall and didn't finish, so true wall was
>>3600s; rescue should fit comfortably under 5400s.

---

## NEW DISCIPLINES (D1 + D2)

### D1: Mandatory pre-dispatch roofline probe

Cell exposes `--roofline-probe` flag. Runs a 3-point timing probe at
N=512/1024/2048 (synthetic vocab, single arm `ARM_2_LAYER_INDEPENDENT_CFRPE`,
50 steps). Fits power-law `t = a * N^k`. Extrapolates to FULL config wall.
Refuses dispatch (exit 1) if `extrapolated_full_wall > 0.8 * --timeout-s`.

The probe writes `data/exp_<anchor>/roofline_probe.json` with all points,
fit coefficients, extrapolation, and accept/refuse decision for audit.

Roofline-probe is invoked by exp_dev BEFORE the queue_add.sh dispatch as the
ENABLE check on the timeout argument. If the probe refuses, exp_dev either
(a) further reduces scope or (b) raises the timeout to the required value
documented in the probe output.

### D2: Mandatory atexit + per-seed checkpoint

Cell registers `atexit._atexit_flush_partial()` handler at module import.
On ANY exit (normal / SIGTERM / SIGKILL — Python only catches the first two
but the per-seed checkpoint covers SIGKILL), the handler flushes the live
`_LIVE_STATE` dict to `data/exp_<anchor>/partial_atexit.json`:
- phase (init / running / aggregating / done)
- seeds_done list
- per_seed_so_far (nested {seed: {arm: arm_dict}})
- current_seed / current_arm at time of exit
- start_ts / flushed_at_ts / elapsed_s

This complements the per-seed checkpoint (write_partial via `_seed_checkpoint`)
which atomically writes whole-seed partials. The combination guarantees that
ANY timeout / crash yields at LEAST `partial_atexit.json` + zero-or-more
per-seed `partial_metrics_<seed>.json` files — never 0 information again.

Loop order: outer = seed, inner = arm. Seed 0 lands (all 4 arms) BEFORE
seed 1 starts. Worst-case rescue at midpoint: 1 fully-completed seed + 1
seed's atexit-flushed partial — still informative for sanity rails.

---

## ENCODING (UNCHANGED from v1)

word2vec-google-news-300 projected to N_DIM=4096 sparse-bipolar (f=0.05).
OOV fallback char-trigram bipolar.

---

## CONFIG

- N_DIM = 4096
- N_TRAIN = 50,000 tokens (text8)
- N_HELD = 10,000 tokens (dev/test = 50/50 split)
- VOCAB_CAP = 4000
- SEEDS = [7, 17] (2 seeds)
- N_STEPS = 2000
- INGEST_BATCH = 64
- CFRPE_LR = 0.5
- SPARSE_BIPOLAR_F = 0.05
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]   # EXCLUDES 0.0 per META C7
- MRR_K = 10

---

## PRE-REG BANDS (INHERITED from v1; not loosened per handoff contract)

**Sanity rails:**
- ARM_SINGLE_LAYER_CFRPE BPC within +/- 0.40 of 7.04 (provenance vs
  fair_harness ARM_CFRPE_ONLY chain-grade reference). v1 used +/- 0.30; the
  rescue widens to +/- 0.40 ONLY for the rail (NOT the verdict bands) because
  N_DIM reduction 8192 -> 4096 adds ~0.1-0.2 BPC noise to single-layer cf-RPE.
  The compositional bands (HARD_PASS/MIDDLE/FAIL) are UNCHANGED.
- ARM_2_LAYER_SHARED_W must NOT beat ARM_SINGLE_LAYER_CFRPE by >= 0.05 bits
  (sub-additive or no-lift expected; validates same-W collapse pattern).

**Verdict bands (best_indep_bpc = min over ARM_2_LAYER_INDEP, ARM_3_LAYER_INDEP):**
- **CHAIN_GRADE_BONUS**: best_indep_bpc <= 6.70
- **HARD_PASS**: best_indep_bpc <= 6.90
- **MIDDLE_BAND**: best_indep_bpc in (6.90, 7.05]
- **HARD_FAIL**: best_indep_bpc > 7.05 OR best_indep_bpc > shared_W_bpc

**Stability:** cv across 2 seeds of HARD_PASS arm <= 0.05 mandatory (else
downgrade to MIDDLE_BAND_HIGH_CV). At 2-seed cv, the lever is conservative;
3-seed cv on a follow-up is recommended IF this rescue lands HARD_PASS.

**READOUT_DEGENERATE:** if best_indep raw_bpc_at_T1_L1 within +/- 0.5 of
vocab-entropy (log2(V) ~= 12.0 bits for V=4000) → READOUT_DEGENERATE.

---

## INSTRUMENTATION REQUIREMENTS

- Per-seed-per-arm metrics in `per_seed` list (no early aggregation).
- cv reported per arm.
- LAMBDA_GRID excludes 0.0 (load-bearing per META C7).
- Real-data assertion: text8 corpus verified at startup.
- Forward-call counter: NO LLM at inference (pure substrate plasticity over
  word2vec projection); documented in `by_construction_guards`.
- **D1 roofline_probe.json written if probe ran.**
- **D2 partial_atexit.json written on any abnormal exit.**

---

## SMOKE GATE

Smoke config (auto-activated via `--smoke` or `_smoke` HDLAB_EXP_NAME):
- N_DIM=512, N_TRAIN=2000, N_HELD=400, VOCAB_CAP=300, SEEDS=[0], N_STEPS=80
- char-trigram encoder fallback (gensim not required for smoke)
- Must produce valid metrics.json with REQUIRED_FIELDS + per-arm per_seed entries.
- Must NOT crash on any of the 4 arms.
- Expected smoke wall: 30-90s on laptop CPU.
- ST11 (self-test): atexit handler registered + callable.

---

## TIMEOUT ESTIMATE

D1 roofline probe is authoritative; if it accepts, the extrapolated wall is
recorded in `roofline_probe.json`. Cell-author estimate without the probe:

- v1 ARM_2_LAYER_INDEP at N=8192, n_steps=1000: ~10-15 min per arm per seed
  (CPU). v1 had 4 arms x 3 seeds = ~2-3 hours wall — but v1 actually hit
  3600s timeout meaning real wall was higher (likely 4-5h+).
- Rescue scales cost by ~0.27x: 4 arms x 2 seeds x (4096/8192)^2 x (50k/100k)
  x (2000/1000) = ~30-50 min build walls + ~5 min encoder + recall.

**D1 PROBE RESULTS (2026-06-24, run twice for variance):**
- Run 1 (cold BLAS): fit k=1.514, extrapolated 8396s. REFUSED at 5400s budget.
- Run 2 (warm BLAS): fit k=1.810, extrapolated 1924s. ACCEPTED at 12000s budget.
- High probe variance suggests BLAS warm-up dominates 50-step timings; true
  full wall likely 60-180min.

**Requested timeout: 12000s (3.3h)** — 4x safety margin over warm-BLAS
estimate; ~1.4x safety over cold-BLAS estimate. Below PROT-021 14400s
checkpoint-floor (cell still imports _seed_checkpoint per D2 discipline).
No PROT-018 _n suffix (anchor has no _n4096 suffix). No PROT-019 large-N
tier (anchor lacks the suffix; production N is 4096 but not name-bound).

If FULL run hits the timeout: D2 ensures partial_atexit.json + per-seed
partial_metrics_*.json survive; a follow-up rescue cell can resume.

---

## CITES

- `notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` (the trigger)
- `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md` (source drill)
- `experiments/exp_substrate_cross_layer_compose_LM_v1.py` (timed-out predecessor)
- `preregs/2026-06-24_substrate_cross_layer_compose_LM_v1.md` (predecessor pre-reg)
- `notes/director_composition_store_mine_inventory_2026-06-24.md` (mechanism rationale)
- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` (cf-RPE reference)
- `experiments/exp_q_a3_l100_cross_layer_composition_v1_n16384.py` (cross-layer L=100 lacc=1.0)

---

## ROLE DISCIPLINES APPLIED

- ASCII-only in source + prereg
- Per-seed checkpoint via `experiments/_seed_checkpoint.py`
- D2: atexit partial-flush handler (NEW; covers Python-catchable exits +
  complements per-seed checkpoint which covers SIGKILL by atomicity).
- D1: roofline probe via `--roofline-probe` flag (NEW; refuses over-budget).
- Fix #14 ONE cell (no parallel siblings).
- Fix #28 per-arm metrics verification (read per-arm bpc, not just verdict_msg).
- Fix #26 predispatch_check ran; no prior landings for this anchor; PROCEED.
- LAMBDA_GRID excludes 0.0 (META C7 no-pure-unigram-blend).
- Smoke gate mandatory before full dispatch.
- A5 cert role-separation: this cell PROPOSES verdict; Skunkworks owns landed-VET.
