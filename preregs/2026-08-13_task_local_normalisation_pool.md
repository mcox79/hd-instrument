# PRE-REGISTRATION — `exp_task_local_normalisation_pool_v1`

Filed 2026-08-14, BEFORE the cell file exists and BEFORE any arm is scored. Bands frozen at this
commit. Branch `dataprep/mcguffey-graded-corpus`.

Parent audit: `notes/comparator_component_fidelity_audit_2026-08-13.md` row **C4**.
Predecessor: `exp_graded_divisive_comparator_v1` HARD_PASS (`0f6459309`), wired at `542fb7754`.

---

## 1. WHAT THE PREDECESSOR LEFT OPEN

Cell 1 confirmed the audit's C1/C2 gap (remove the quantisers: +0.0585 of the +0.0602 total) and
**refuted the pool half of it**: global-field divisive normalisation was NULL on the graded code
(+0.0018, CI [-0.0030,+0.0065]) even though it removes a shared component worth 58% of every
anchor's norm.

The mechanism I inferred, and which this cell tests rather than assumes: **a component shared by
BOTH candidates contributes near-equally to both cosines and therefore nearly cancels in a
two-candidate argmax, however much it dominates the geometry.** If that is right, the failure was
the POOL, not the operation — and the brain names the correct pool. Divisive normalisation's
denominator is the **concurrently active population** (Carandini & Heeger 2012 *Nat Rev Neurosci*
13:51-62), which at decision time is the two candidates, not the 2,377-anchor store. Independently,
semantic control applies **multiplicative gain to the task-relevant dimensions** rather than
selecting from a candidate list (Chiou & Lambon Ralph 2018 *Cortex*, DCM, F(2,34)=3.86, p=.03), and
distinctive features — those present in FEW concepts — are privileged in the computation of word
meaning (Cree, McNorgan & McRae; Tyler & Moss CSA).

**These are the same operation.** Normalising each dimension by the pool of currently active
candidates divides DOWN the dimensions on which both candidates are strongly active (the shared
features) and leaves standing the dimensions where only one is (the distinctive features). Task-
local divisive normalisation IS distinctive-feature privileging IS semantic-control gain. That
convergence is why this is the next build and not a cheaper diagnostic.

## 2. THE OPERATION

For an item with candidate anchors `a`, `b` (graded, from the wired `freeze_graded` path) and
context query `q`:

    pool_j = |a_j| + |b_j|
    g_j    = 1 / (sigma + pool_j)                    <- Carandini-Heeger, n=1, pool = active set
    score  = cos(q * g, a * g)   vs   cos(q * g, b * g)

`sigma` is a semi-saturation constant and is **NOT a tuned knob**: it is fixed at the MEAN of
`pool_j` over all dimensions and all items, computed from the anchor field itself. A sensitivity
sweep over sigma is reported as a SECONDARY diagnostic with NO verdict weight.

The gain is symmetric in the two candidates, so it cannot leak the answer. It is applied to the
query and to both anchors (a channel gain, not an anchor-specific transform).

## 3. ARMS

- **`R_LIVE`** — the fully quantised live comparator. Reference. Must reproduce 0.6395 +/- 0.02.
- **`R_BASE`** — `A_GGZ`, the predecessor's HARD_PASS arm. **The baseline the primary contrast is
  measured against.** Must reproduce 0.6997 +/- 0.02. Deliberately the HARDER of the two available
  baselines (`A_GGN` scored 0.6980) so the contrast cannot be flattered by baseline choice.
- **`P_LOCAL`** — the operation in sec 2. **PRE-DESIGNATED PRIMARY, the only treatment arm.**
- **`S_DIFF`** — ablation: `g_j = |a_j - b_j|` (mean-normalised), a pure contrast weighting. Tests
  whether the DIVISIVE FORM matters or whether any contrast weighting would do. No verdict weight.
- **`W_WRONGPOOL`** — **the decisive control.** Identical operation, but `g` is computed from a
  DIFFERENT item's candidate pair (the predecessor's deterministic derangement), then applied to
  this item's comparison. Same arithmetic, same statistics, WRONG pool. If this reproduces
  `P_LOCAL`'s gain, the gain is a generic variance filter and NOT task-local control.
- **`F_LOCAL_SCRAM`** — `P_LOCAL` with a different item's real sentence as the query. Floor.
- **`F_BASE_SCRAM`** — `R_BASE` scrambled. Floor. Predecessor value 0.5065.
- **`B_FREQ`** — corpus-frequency baseline. Predecessor value 0.4800.

## 4. BANDS — frozen

Primary contrast **d = acc(P_LOCAL) - acc(R_BASE)**, paired bootstrap over items, 5,000 resamples,
seed 20260813, plus a cluster bootstrap by target word.

**HARD_PASS** (conjunction, all five):
1. `d >= +0.03`
2. `d` CI excludes 0
3. `acc(P_LOCAL) - acc(W_WRONGPOOL) > 0` with CI excluding 0 — the gain is TASK-LOCAL, not generic
4. `F_LOCAL_SCRAM <= 0.55`
5. `R_LIVE` reproduces 0.6395 +/- 0.02 AND `R_BASE` reproduces 0.6997 +/- 0.02

**Why +0.03 and not the predecessor's +0.05, stated in advance so it cannot be read as band
shopping:** the baseline has moved from 0.6395 to 0.6997, so the same absolute delta is a larger
share of the remaining headroom; and the measured MDE_95 for a paired delta at n=4000 in this
harness is **0.0163**, so +0.03 is 1.8x MDE and remains a can-fail bar. The band was chosen from
the MEASURED MDE, not from any observed effect — no arm of this cell has been scored.

**MIDDLE_BAND_FLOOR_HUGGING** — HARD_PASS met but `d < 0.03 * 1.05` (META_RULE_L).

**MIDDLE_BAND_REAL_BUT_SMALL** — `0 < d < 0.03`, CI excludes 0, controls clean.

**HARD_FAIL_GENERIC_NOT_TASK_LOCAL** — `d >= +0.03` with CI excluding 0, BUT gate 3 fails
(`W_WRONGPOOL` reproduces the gain). The apparent win is a generic variance filter. **This is the
control designed to reproduce the win from the wrong source, and it OUTRANKS the pass.**

**HARD_FAIL_GAIN_ADDS_NOTHING** — `d` CI includes 0. Audit row C4 is refuted on this task; the head
item moves to C7 (representation format / capacity) or to a thresholded-decision testbed where the
predecessor's null on global normalisation predicts a gain.

**HARD_FAIL_GAIN_HURTS** — `d < 0` with CI excluding 0. Suppressing shared dimensions would then be
destroying signal the comparator needs, which would be evidence AGAINST distinctive-feature
privileging as implemented here and would send the next drill back to the biology.

**HARD_FAIL_FLOOR_BREACH** — `F_LOCAL_SCRAM > 0.55`.

**INSTRUMENTATION_SUSPECT_BASELINE_DRIFT** — gate 5 fails. Dominates; no read licensed.

## 5. SECONDARY, EXPLICITLY NO VERDICT WEIGHT

1. **sigma sensitivity**: `P_LOCAL` at sigma in {0.25x, 0.5x, 1x, 2x, 4x} the pre-registered value.
   Reported so the pre-registered choice can be seen in context. A band may NOT be met by any arm
   other than the sigma = 1x one.
2. **FAIR-TEST DIAGNOSTIC — is the substrate capacity-bound at d=256?** `R_BASE` and `P_LOCAL`
   re-run at d in {256, 1024}. This exists because a null for C4 would be uninterpretable if random-
   indexing crosstalk at d=256 (expected |cos| ~ 1/16 between unrelated codes) is the dominant
   limiter. It informs the NEXT cell's design; it decides nothing here.
3. Far-distractor accuracy for `R_BASE` and `P_LOCAL`, as in both predecessors.

## 6. CONTROLS

Every arm scores the SAME items with the SAME candidates from the SAME cached corpus assets; item
construction, leak controls L1/L2/L3, the held-out PROFILE/EVAL split and the donor derangement are
IMPORTED from `exp_context_conditioned_near_neighbour_v1`, and the encoders and read-out are
IMPORTED from `exp_graded_divisive_comparator_v1`, so the arithmetic under test is the only
difference. The predecessor's four non-fork controls (encoder byte-identity to
`hdlab.context_vector`; anchor matrix byte-identity to `ConceptSpace.anchor_matrix`; read-out
item-for-item agreement with `canonicalize_fast` on the LIVE arm; self-retrieval >= 0.70) are
re-run here and must all still hold.

## 7. ENGINEERING

Thread pins before `import numpy`; fresh output dirs; smoke to separate dirs; `metrics.json` once
via tmp + `os.replace`; `sorted(set())`; `hashlib` seeds; per-unit checkpoint; ASCII-only.
`hdlab/` is NOT modified by this cell. Detached run via `Start-Process` with separate stdout/stderr
redirects and a PID file.
