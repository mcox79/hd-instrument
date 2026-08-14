# PRE-REGISTRATION — `exp_graded_divisive_comparator_v1`

Filed 2026-08-13, BEFORE the cell file exists and BEFORE any arm is scored. Every arm, band, floor,
control and stopping rule below is frozen at this commit. Branch `dataprep/mcguffey-graded-corpus`.

Parent audit: `notes/comparator_component_fidelity_audit_2026-08-13.md` (`4e35b5cb7`).
Testbed: the landed context-conditioned near-neighbour cell `367ce167f`
(`experiments/exp_context_conditioned_near_neighbour_v1.py`, prereg `42792834c`).

---

## 1. THE ONE QUESTION

The audit's rank-1 and rank-2 fidelity gaps are a single arithmetic defect at two sites: the
comparator ends every composition in a **per-component magnitude-destroying normalisation**
(`np.sign`), where the brain applies **divisive normalisation with a POOL-SHARED denominator**
(Carandini & Heeger 2012 *Nat Rev Neurosci* 13:51-62) onto a **dense graded low-effective-dimensional
code** (Huth 2012/2016; Tiesinga 2023). `sign(shared + distinctive) = sign(shared)` wherever
`|shared| > |distinctive|`, so our composition is a PROTOTYPE OPERATOR, and prototype drift with
within-category coordinate confusion is the semantic-dementia signature (Rogers et al. 2004
*Psychol Rev* 111:205-235) — our exact failure mode.

**Q: does replacing the binarisation with a graded code + population divisive normalisation improve
near-neighbour discrimination in context, with the scrambled-context floor still at chance?**

This changes ARITHMETIC ONLY. No new information, no new features, no new corpus, no training, no
tuned parameter. The four refuted routes all added INFORMATION to this same arithmetic.

## 2. WHY THIS TESTBED

The context-conditioned 2AFC task is the only current measurement with (a) genuine range, (b) a
working floor that sits at chance (scrambled context 0.4975 vs chance 0.5000), and (c) a
discriminator that is **range-by-construction**: 2AFC accuracy in [0,1] with chance exactly 0.50 and
NOTHING hand-scored. Two cells this week were undecidable because their discriminator gated on a
hand-scored quantity; that cannot happen here.

Item construction, leak controls L1/L2/L3, the per-word `hashlib`-seeded PROFILE/EVAL split, the
WordNet STRICT dominant-sense near-neighbour criterion, the deterministic donor derangement and the
paired bootstrap are REUSED BYTE-FOR-BYTE from the landed cell. The only thing that changes between
this cell and its parent is the comparator arithmetic.

## 3. ARMS — a 2 x 2 x 4 factorial over the three arithmetic decisions

Three binary/quaternary factors, each a specific line of live code:

- **ENC** — how one sentence becomes a vector (`grounding_acquisition_loop.py:132`).
  - `S` = `np.sign(sum of word random-index vectors)` — LIVE.
  - `G` = the raw graded sum, sign removed.
- **AGG** — how encounters become a concept (`reading_grounding_loop.py:446`).
  - `S` = `np.sign(sum of sentence vectors)` — LIVE.
  - `G` = the raw graded sum (already held in `ConceptSpace._sums`).
- **NORM** — the normalisation pool.
  - `N` = none — LIVE.
  - `C` = per-dimension CENTERING against the population mean (removes the shared component).
  - `Z` = per-dimension CENTER + divide by population sd — divisive normalisation with the
    population as the pool.
  - `ZA` = `Z` applied to the ANCHOR field only, query left raw.

Normalisation pools, fixed here so they are not a post-hoc choice: **anchors** are normalised by the
per-dimension mean/sd of the ANCHOR MATRIX; **queries** are normalised by the per-dimension mean/sd
of the PROFILE-SENTENCE population under the same ENC (profile sentences are held out from scoring,
so no eval item contributes to its own normaliser). `ZA` normalises anchors only.

16 arms `A_<ENC><AGG><NORM>`. Two are named:

- **`A_SSN` = LIVE.** Byte-equivalent to the landed cell's ARM 1. Positive control, not a treatment.
- **`A_GGZ` = PRIMARY.** The brain-faithful comparator. **Pre-designated here as the single
  treatment arm.** The other 14 arms are the FACTORIAL DECOMPOSITION and carry **NO VERDICT WEIGHT**;
  they exist to attribute any effect to ENC vs AGG vs NORM. No band may be met by a non-primary arm.

Floors and baselines (scored, verdict-relevant):
- **`F_SSN_SCRAM`** — LIVE arm, query replaced by a different item's real sentence (the landed
  derangement). Landed value 0.4975.
- **`F_GGZ_SCRAM`** — PRIMARY arm, same derangement. **The one-variable floor.**
- **`B_FREQ`** — pick the corpus-more-frequent candidate. Landed value 0.4800.
- **CHANCE** = 0.5000 by construction (2 candidates).

## 4. BANDS — frozen

Primary contrast **d = acc(A_GGZ) - acc(A_SSN)**, paired bootstrap over items (all arms score the
SAME items), 5,000 resamples, seed 20260813, plus a cluster bootstrap by target word.

**HARD_PASS** (conjunction, all five):
1. `d >= +0.05`
2. `d` bootstrap CI excludes 0
3. `F_GGZ_SCRAM <= 0.55` — the gain is specific to THIS context
4. `A_GGZ - CHANCE > 0` with CI excluding 0
5. `A_SSN` reproduces the landed 0.6395 within +/- 0.02 — otherwise the harness, not the
   hypothesis, is what changed

**MIDDLE_BAND_FLOOR_HUGGING** — HARD_PASS met but `d < 0.05 * 1.05` (META_RULE_L strict margin).

**MIDDLE_BAND_REAL_BUT_SMALL** — `0 < d < 0.05`, CI excludes 0, floor clean. Reported as a real but
sub-threshold effect; does NOT license a build.

**HARD_FAIL_BINARISATION_NOT_THE_LEVER** — `d` CI includes 0. The audit's rank-1/rank-2 gaps are
refuted as the binding constraint on this task, and the head item moves to C4 (multiplicative gain).

**HARD_FAIL_BINARISATION_WAS_LOAD_BEARING** — `d < 0` with CI excluding 0. A genuinely possible and
genuinely informative outcome: `sign()` would then be doing real work (equalising the influence of
high-frequency dimensions), and the brain-faithful direction would be gain-before-quantisation
rather than no quantisation. **This is what makes the test able to fail.**

**HARD_FAIL_FLOOR_BREACH** — `F_GGZ_SCRAM > 0.55`. Any gain is context-nonspecific and void.

**INSTRUMENTATION_SUSPECT_LIVE_ARM_DRIFT** — gate 5 fails. Dominates all other verdicts; no read is
licensed.

**INSTRUMENTATION_SUSPECT_READOUT_FORK** — the direct 2-candidate read-out used by all 16 arms does
not agree ITEM-FOR-ITEM with `hdlab.reading_grounding_loop.canonicalize_fast(thresh=-1.0,
eligible_mask=...)` on the LIVE arm. Dominates. (This is the control that stops the new harness from
being a silent fork of the substrate's own read-out.)

## 5. POWER

Landed run at n=4000: `d_A1_minus_A2 = 0.1005`, CI [0.0795, 0.1227], half-width ~0.0216, i.e.
bootstrap MDE_95 ~ 0.021 for a paired delta at this n. The HARD_PASS delta of +0.05 is 2.3x the MDE.
Analytic paired-binomial floor `1.96*sqrt(0.5/n) = 0.0155` at n=4000. Discriminator reachable.
`MIN_ITEMS = 200` hard gate; below that the run stops with `INSUFFICIENT_ITEMS_NO_READ` rather than
reading an underpowered result.

## 6. CONTROLS

1. **One-variable isolation.** Every arm scores the SAME items, the SAME candidate pairs, the SAME
   held-out sentences, from the SAME cached corpus assets. Only the arithmetic differs.
2. **Scrambled-context floor per arm** (`F_*_SCRAM`) — a floor that can genuinely fail, already
   demonstrated to sit at chance for the live arm.
3. **Read-out non-fork control** — item-for-item agreement with `canonicalize_fast` on the LIVE arm
   (sec 4, `INSTRUMENTATION_SUSPECT_READOUT_FORK`).
4. **Encoder byte-identity control** — the graded encoder's `np.sign(...)` MUST equal
   `hdlab.grounding_acquisition_loop.context_vector` on real sentences, asserted in the self-test.
   This proves ENC=G is hdlab's own math with one operation removed, not a re-implementation.
5. **Landed-value reproduction** — `A_SSN` must reproduce 0.6395 +/- 0.02 (sec 4 gate 5).
6. **Self-retrieval positive control** — >= 0.70, per arm, as in the parent cell.
7. **Arms-differ digest check** (META_RULE_AF) — per-arm sha256 of the choice vector; two arms may
   not be bit-identical.
8. **Far-distractor secondary** for LIVE and PRIMARY — no verdict weight; parallels the parent.

## 7. WHAT WOULD MAKE ME ABANDON THE AUDIT'S RANK-1 GAP

`HARD_FAIL_BINARISATION_NOT_THE_LEVER` with a clean floor and a reproduced LIVE arm. In that case
the measured field geometry (shared component 0.5841 -> 0.0000) is real but **decoupled from task
performance**, which is the same decoupling already observed for read-out stability
(`192521a7f`: F3 stabilises argmax but licenses no quality claim). I will report that explicitly
rather than reframing the null.

## 8. ENGINEERING

Thread pins before `import numpy`. Fresh output dirs; smoke writes to SEPARATE dirs from full.
`metrics.json` once via tmp + `os.replace`. `sorted(set())` never `list(set())`. `hashlib` seeds,
never builtin `hash()`. Per-unit checkpoint via `tools/exp_checkpoint.py`. ASCII-only. `hdlab/` is
NOT modified by this cell; if the result licenses a promotion, that is a separate landing with a
`verification/` witness.

Compute: sequential CPU, local, detached via `Start-Process` with separate stdout/stderr redirects
and a PID file.
