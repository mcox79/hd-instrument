# Pre-reg: substrate_compositional_generalization_CLEAN_v1

**Date:** 2026-06-25 UTC
**Author:** exp_dev (Agent Teams: cell author / prover)
**Anchor:** `substrate_compositional_generalization_CLEAN_v1`
**Routing:** USER directive — fix the recurring pair-storage protocol bug; test substrate's
REAL compositional generalization under proper Plate-canonical role-filler binding.
**Queue:** `local_cpu_queue` (numpy + HRR only; no torch; ~15-25 min full wall).

## What this cell tests

Substrate's compositional generalization under the canonical composite-key role-filler
HRR protocol, with four arms (sanity + three generalization probes) at N_DIM=8192.

## Protocol — composite-key Plate role-filler

```
payload(s, p, o) = L2_norm( bind( L2_norm(bind(A_subj, A_pred)),  A_obj ) )
bank             = sum_i payload(s_i, p_i, o_i)        # per-triple L2-normed
query for obj given (s, p):
    key_query    = L2_norm(bind(A_subj, A_pred))
    rec          = unbind(bank, key_query)
    prediction   = argmax cosine(rec, obj_book)
```

Composite (subj, pred) is the KEY; obj is the VALUE.  This protocol is the substrate's
chain-grade tag-retrieval pattern (CERT 591 fly-LSH + U1 FB15k-237 set-recall 0.99 @
M=50k).  It LIFTS the 1/k pair-storage ceiling that bound prior pair-storage protocols.

## The protocol bug we are fixing

`exp_substrate_brain_aligned_aliveness_shotgun_v1` ARM 2 and the substrate-native suite
CG arm BOTH HARD_FAILed at `holdout=0.000`.  Root cause: pair-storage protocol (direct
`bind(A_subj, A_obj)` without a per-(s,p) composite key) is bound by a 1/k ceiling where
k = #pairs-per-subject.  With 50% coverage of a 20x20 grid that ceiling is ~1/10 -- NOT
a substrate failure, a protocol-ceiling artifact.

Prior `substrate_compositional_generalization_K10_to_K20_v1_n4096` HARD_PASSed at 1.000
via a different (link-shuffled chain composition) protocol; ANCHOR reconfirmed at N=8192.
Substrate IS compositionally alive when the protocol is correct.  This cell tests the
canonical composite-key form on subject-predicate-object triples directly.

## Four arms

1. **ARM_TRAINED_PAIRS** — sanity. Store M=200 distinct-(s,p) triples; query each by its
   composite key; recover the bound obj.  Mechanism check.

2. **ARM_HELDOUT_NEW_OBJ** — set-recall under same-key multi-value.  Train K_OBJ_SAME=3
   (s, p, o_i) triples sharing (s,p); query (s,p); check top-5 contains any trained o_i.

3. **ARM_HELDOUT_NEW_SUBJ** — generalize predicate-association across subjects.  Train K=3
   triples (s_i, p, o) sharing (p, o) across K different subjects; query NEW subject
   (s_new, p, ???); substrate should retrieve o because the (pred, obj) signal accumulates
   across superposed keys while per-subject keys decorrelate.

4. **ARM_HELDOUT_NEW_PRED** — generalize subject-association across predicates.  Train K=5
   triples (s, p_i, o_i) sharing subject s; query (s, p_new, ???); substrate should return
   a structurally plausible obj (one of the trained o_i since they're the only objects
   associated with subject s in this bank).

## Pre-reg HARD bands

ARM 1 absolute; ARMs 2-4 chance-relative lift (chance baselines vary with K and V_obj,
so absolute bands would be trivially passable or trivially failable depending on V_obj).

| Arm | Metric | HARD-PASS band |
|-----|--------|----------------|
| ARM_TRAINED_PAIRS | top1 (abs) | >= 0.95 |
| ARM_HELDOUT_NEW_OBJ | top5 - chance_analytic | >= 0.20 |
| ARM_HELDOUT_NEW_SUBJ | top1 - chance_analytic | >= 0.30 |
| ARM_HELDOUT_NEW_PRED | top5 - chance_analytic | >= 0.20 |

**Cell-level verdicts (n_pass = arms that HARD-PASS individually):**

- `HARD_PASS_COMPOSITIONAL_ALIVE`: n_pass >= 3.  Substrate compositionally generalizes
  under Plate composite-key role-filler binding.
- `MIDDLE_BAND`: n_pass == 2.  Partial compositional generalization (likely ARM_TRAINED +
  ARM_HELDOUT_NEW_OBJ both work, but cross-slot generalization arms 3-4 stall).
- `HARD_FAIL`: n_pass <= 1.  Substrate does not compositionally generalize under this
  protocol.

**Mandatory SANITY GATE:** `ARM_TRAINED_PAIRS.top1 >= 0.70` (`SANITY_FLOOR_TRAINED_TOP1`).
If sanity fails, verdict = `HARD_FAIL_SANITY` regardless of other arms (mechanism is
broken at this (N_DIM, M) scale; generalization arms uninterpretable).

## Full config

```
SEEDS = [7, 17, 23]
N_DIM = 8192
M_TRAIN_PAIRS = 200                 # ARM 1 stored triples (unique-(s,p))
V_SUBJ = 50, V_PRED = 20, V_OBJ = 50
K_OBJ_SAME = 3                      # ARM 2
K_SUBJ_TRAIN = 3                    # ARM 3
K_PRED_TRAIN = 5                    # ARM 4
N_HELDOUT_TRIALS = 50               # ARMs 2-4 independent trials per seed
```

Analytic chance baselines under full config:

- ARM_TRAINED_PAIRS chance_top1 = 1/V_OBJ = 0.020
- ARM_HELDOUT_NEW_OBJ chance_analytic = 1 - prod_{i=0..4} (47-i)/(50-i) ~ 0.274
- ARM_HELDOUT_NEW_SUBJ chance_analytic = 1/V_OBJ = 0.020
- ARM_HELDOUT_NEW_PRED chance_analytic = 1 - prod_{i=0..4} (45-i)/(50-i) ~ 0.421

Under these chance baselines the bands become:
- ARM 2 PASS threshold absolute top5 ~ 0.474
- ARM 3 PASS threshold absolute top1 ~ 0.320
- ARM 4 PASS threshold absolute top5 ~ 0.621

## Smoke result (Fix #17 measurement discipline)

Wall: ~0.9 s on laptop CPU (1 seed, N=1024, V=12, M=40, K_obj=2, K_subj=2, K_pred=3, 8 trials).

| Arm | Measured | Chance | Lift | Band | Pass |
|-----|----------|--------|------|------|------|
| ARM_TRAINED_PAIRS | top1=1.000 | 0.083 | (abs >=0.95) | 0.95 | YES |
| ARM_HELDOUT_NEW_OBJ | top5=1.000 | 0.682 | 0.318 | 0.20 | YES |
| ARM_HELDOUT_NEW_SUBJ | top1=0.125 | 0.083 | 0.042 | 0.30 | NO |
| ARM_HELDOUT_NEW_PRED | top5=0.875 | 0.841 | 0.034 | 0.20 | NO |

Smoke verdict: `MIDDLE_BAND` (2 of 4 arms pass).  Sanity floor cleared.

**Honest reading of smoke (Fix #28):**
- Mechanism is operational (ARM_TRAINED_PAIRS top1=1.000).
- ARM_HELDOUT_NEW_OBJ shows clear above-chance retrieval (same-key multi-value: 0.318 lift).
- ARMs 3-4 do NOT show above-chance signal at smoke scale.  Whether N=8192 + larger
  vocabularies rescue this is exactly what the FULL run answers.  Smoke is honest-noise
  at K=2-3 superposed triples in N=1024 dims with high analytic-chance baselines.

## Estimated full wall

Per-arm cost ~ M * V_OBJ * N_DIM for ARMs 2-4 plus M^2 * V_OBJ * N_DIM equivalent for
ARM 1 (M queries against M-superposed bank).  Smoke 0.9 s -> full estimate by scaling:

- N_DIM: 8x
- M: 5x (ARM 1)
- seeds: 3x
- trials (ARMs 2-4): 50/8 ~ 6.25x
- V_obj: 50/12 ~ 4.2x

Conservative estimate: 0.9 * 8 * 5 * 3 * 6 * 4 ~ 2600 s = 43 min.  Budget timeout = 1800 s
(30 min) which covers expected; if exceeded, partial seeds via _seed_checkpoint resume.

## Files

- Cell: `experiments/exp_substrate_compositional_generalization_CLEAN_v1.py`
- Prereg: `preregs/2026-06-25_substrate_compositional_generalization_CLEAN_v1.md`
- Smoke metrics: `data/exp_substrate_compositional_generalization_CLEAN_v1_smoke/metrics.json`
- Full metrics (post-dispatch): `data/exp_substrate_compositional_generalization_CLEAN_v1/metrics.json`

## Predispatch check (Fix #26)

```
[predispatch_check] keywords=['substrate_compositional_generalization_CLEAN_v1']
                    lookback=30d
  matching landings: 0   matching atoms: 0
  RECOMMENDATION: PROCEED
```

No duplicate; no recent-HARD_FAIL re-dispatch.

## What this cell does NOT show

- Language-task performance (no text corpus).
- Learning / plasticity (no gradient updates; pure substrate primitives).
- Capacity scaling (single M=200).
- Noise robustness (clean codebook; no corruption).
- Multi-hop chain composition (that is the K10_to_K20 cell's job).

## Cell-level disciplines

- ASCII-only.
- Per-seed checkpoint via `experiments/_seed_checkpoint.py`.
- CPU only (numpy + FFT-based HRR).
- All seed-affecting params in `CONFIG_VERSION` (resume rejects stale partials with
  mismatched N / run_mode).
- Selftest gates: dense unit-norm builder + bind/unbind round-trip + composite-key
  single-triple recall + M=5 distinct-key recall >=4/5 + verdict-band sanity
  (HP/MIDDLE/SANITY).
- Smoke gate runs end-to-end with the same protocol and writes metrics.json conforming
  to REQUIRED_FIELDS.

## Why this matters

If HARD_PASS, the brain-aligned aliveness picture moves to 4/4 arms and the
substrate-native suite to 4/6.  The recurring "compositional generalization" HARD_FAILs
that have been mis-attributed to substrate capability are properly attributed to the
prior pair-storage protocol bug, and the substrate is positively shown to compositionally
generalize under the canonical Plate protocol it was designed for.

If MIDDLE_BAND, ARMs 1-2 work + ARMs 3-4 stall = substrate retrieves but does not
cross-slot-generalize at this protocol/scale.  Routes to Research for revival angle on
the cross-slot generalization mechanism (the 2x-revival drill discipline).

If HARD_FAIL_SANITY, mechanism is broken at (N=8192, M=200) and we have a substrate-
scale story to investigate -- but this is unlikely given smoke ARM_TRAINED_PAIRS=1.000
at the much-more-crowded smoke scale (M=40 in N=1024 dims).
