# PRE-REGISTRATION — `exp_capacity_ceiling_near_far_v1`

Filed 2026-08-14, BEFORE the cell file exists and BEFORE any arm is scored. Bands frozen at this
commit. Branch `dataprep/mcguffey-graded-corpus`.

Head item set by `notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md`, which
promoted audit row **C7 (representation format / capacity)** from last place to first.

---

## 1. THE QUESTION, AND WHY IT IS THE RIGHT ONE

Two cells and one adversarial review have now established:

- removing the comparator's quantisers is worth +0.0602 at the substrate's live `CTX_D = 256`
  (`0f6459309`), and
- **the unmodified quantised comparator at d=1024 scores 0.7030, beating the graded one at d=256**,
  with the graded advantage shrinking 0.0602 -> 0.047 -> 0.041 across d = 256 / 1024 / 4096
  (landed-VET, `f05b8a88a`).

So the substrate is operating where random-projection crosstalk binds: at d=256, unrelated codes sit
at an expected |cos| of ~1/16, and there are 2,377 concepts in that space. Every fidelity
improvement measured so far has been competing with that.

**The question no one has measured, and the one that actually matters for the program:**

> At the capacity ceiling, does NEAR-NEIGHBOUR discrimination still lag FAR-DISTRACTOR
> discrimination — or does the gap close?

This is decisive in both directions and neither outcome is a dead end:

- **If the gap closes and near-neighbour accuracy rises to a level that is no longer a wall**, then
  the "near-neighbour wall" this program has been attacking for weeks was substantially a CAPACITY
  artifact of d=256, and the correct next move is a dimensionality landing, not another mechanism.
- **If the gap persists at 16x the capacity**, then we have ISOLATED a genuine semantic residual
  that capacity cannot explain, on a task with a working floor — which is the cleanest target this
  program has ever had.

## 2. WHAT IS ALREADY MEASURED (disclosed so the bands cannot be reverse-engineered)

At d=256, n=4000, held out (`data/exp_graded_divisive_comparator_v1/metrics.json` and the VET):

| | NEAR (WordNet strict sibling) | FAR (random non-sibling) | gap |
|---|---|---|---|
| quantised (live) | 0.6395 | 0.6625 | 0.0230 |
| graded | 0.69975 | 0.7328 | 0.0331 |

At d=1024 the quantised NEAR arm scores 0.7030 (VET). **Nothing at d=4096 for the NEAR/FAR GAP, and
no FAR measurement at any d above 256, has been made.** All bands below are on quantities that have
not been measured.

## 3. ARMS

Factorial: `d` in {256, 1024, 4096} x code in {QUANT, GRAD} x distractor in {NEAR, FAR}, = 12 scored
arms, plus a scrambled-context floor for each (d, code) at NEAR = 6 floors, plus `B_FREQ`. 19 total.

- `QUANT` = the live comparator (sign at both composition steps), exactly as `A_SSN`.
- `GRAD` = the wired graded path, exactly as `A_GGZ`.
- `NEAR` = the WordNet dominant-sense sibling distractor (the grandparent's `pairs_strict`).
- `FAR` = a random non-sibling distractor for the same target and the SAME held-out sentence, so
  NEAR and FAR differ ONLY in which distractor the target is compared against.

`d=256 / QUANT / NEAR` must reproduce 0.6395 +/- 0.02 and `d=256 / GRAD / NEAR` must reproduce
0.69975 +/- 0.02, or the run is `INSTRUMENTATION_SUSPECT_BASELINE_DRIFT` and no read is licensed.

## 4. BANDS — frozen

Primary quantities, both at **d=4096, GRAD** (pre-designated; no other cell may meet a band):

- `GAP_4096 = acc(FAR) - acc(NEAR)`
- `NEAR_4096 = acc(NEAR)`

**HARD_PASS_CAPACITY_EXPLAINS_THE_WALL** — `NEAR_4096 >= 0.80` AND `GAP_4096 <= 0.02` AND the gap's
paired-bootstrap CI includes 0. The near-neighbour deficit was capacity.

**HARD_FAIL_WALL_IS_NOT_CAPACITY** — `NEAR_4096 < 0.75` AND `GAP_4096 >= 0.04` with the gap's CI
EXCLUDING 0. Sixteen times the capacity does not close the gap; a genuine semantic residual is
isolated and becomes the program's target.

**MIDDLE_BAND_CAPACITY_PARTIAL** — anything else, reported with the full curve and with the fraction
of the d=256 gap that survives at d=4096.

**HARD_FAIL_DIMENSION_DOES_NOTHING** — `acc(NEAR)` at d=4096 does not exceed `acc(NEAR)` at d=256 by
at least +0.02 with CI excluding 0, for EITHER code. Then the whole capacity reading of the VET is
wrong and this cell refutes its own premise. (Included because it must be able to.)

**HARD_FAIL_FLOOR_BREACH** — any scrambled-context floor at any (d, code) exceeds 0.55.

**INSTRUMENTATION_SUSPECT_BASELINE_DRIFT** — sec 3 reproduction gates fail. Dominates.

## 5. POWER AND RANGE

Discriminator is 2AFC accuracy, chance exactly 0.50, nothing hand-scored — **range by
construction**. Measured MDE_95 for a paired delta in this harness at n=4000 is 0.0163; the gap
bands (+/-0.02, 0.04) and the +0.02 dimension band are at or above it, and the gap is a PAIRED
quantity (same targets, same sentences, only the distractor differs), which is the lowest-variance
form available. n=4000, `MIN_ITEMS = 200`.

## 6. CONTROLS

1. Same items, same target sentences, same held-out split, same leak controls L1/L2/L3 across every
   arm; only `d`, the code, and the distractor identity vary.
2. NEAR and FAR are **paired on the same item**, so the gap is a within-item contrast.
3. Scrambled-context floor at every (d, code).
4. The predecessor's non-fork controls re-run at d=256: anchor matrix byte-identical to
   `hdlab.ConceptSpace.anchor_matrix`, read-out item-for-item agreement with `canonicalize_fast`.
5. **Precision control, new and required for this cell:** the word-code cache is float32 at large d
   to fit in memory. Bipolar +/-1 sums are exact in float32 up to 2^24, so this must be LOSSLESS;
   the self-test asserts float32 and float64 accumulation give BYTE-IDENTICAL anchors at the
   largest d, and the cell aborts if they differ.
6. **Projection-draw control, new and required, because the VET showed the item bootstrap misses
   it:** the whole d=256 measurement is repeated over **3 independent random-indexing draws**, and
   the between-draw sd is reported alongside every CI. No claim in this cell may rest on a
   difference smaller than the between-draw sd.

## 7. ENGINEERING

Thread pins before numpy import; fresh output dirs; smoke to separate dirs; `metrics.json` once via
tmp + `os.replace`; `sorted(set())`; `hashlib` seeds; per-unit checkpoint; ASCII-only; `hdlab/` NOT
modified. Detached run via `Start-Process` with separate stdout/stderr and a PID file. The word-code
cache is cleared between dimensionalities.
