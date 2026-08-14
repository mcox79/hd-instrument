# PRE-REGISTRATION -- rank-1 COMMON-MODE removal on the near-neighbour 2AFC read-out

- **anchor_name:** `exp_rank1_common_mode_removal_v1`
- **cell:** `experiments/exp_rank1_common_mode_removal_v1.py`
- **date:** 2026-08-14
- **step:** STEP 3 of `notes/SUBSTRATE_STRATEGY.md` (`5f850770b`)
- **organ:** G3 (neuromodulatory / per-dimension gain), applied to the B1/B2/B3 anchor field
- **STATUS: every band, arm, floor and stopping rule below is frozen BEFORE any arm is scored.**

---

## 0. BRAIN-FIDELITY SCOPE -- CARRIED HONESTLY, NOT AS A LICENCE

This cell tests an **operation-class-compatible ENGINEERING fix**. It is **NOT** a claim that the
anterior temporal semantic hub performs decorrelation.

- Decorrelation is **UNPINNED for cortex** and **NOT-LICENSED** as "the semantic hub does this."
- Real decorrelating organs exist and are cited only as evidence that the operation class is
  biological, not that it lives in our organ: olfactory-bulb whitening via structured granule-cell
  inhibition; V1 adaptation equalising response across neurons; cortex cancelling shared input to
  near-zero correlation. **None of these is the semantic hub.**
- **HARD CAUTION, pre-registered:** cortex's top principal components are MEANINGFUL (Huth 2012
  *Neuron* 76:1210 -- PC1 mobility/animacy, PC2 social). **Top-PC removal is NOT brain-licensed.**
  Common-mode (shared MEAN DIRECTION) removal is the closer operation. Arm `P4_TOP_PC` is included
  ONLY as a separate, explicitly **non-brain-licensed** arm and **carries no verdict weight**.
- This is **NOT** the Carandini-Heeger error corrected at `notes/ORGAN_MAP.md` sec 3.1. That
  correction says a **pool-shared SCALAR denominator** cannot change a two-candidate cosine argmax,
  because cosine is scale-invariant. A shared **ADDITIVE** component is a different object: removing
  `(a . u)u` from each anchor changes the cosine argmax whenever the two anchors' norms or their
  projections onto `u` differ. The two are not the same operation and the correction does not apply.

**ENGINEERING PRECEDENT, credited (learn-from and build-on, never "steal"):**
- Mu, J. & Viswanath, P. (2018). *All-but-the-Top: Simple and Effective Postprocessing for Word
  Representations.* ICLR 2018. (mean subtraction, then top-D PC removal)
- Timkey, W. & van Schijndel, M. (2021). *All Bark and No Bite: Rogue Dimensions in Transformer
  Language Models Obscure Representational Quality.* EMNLP 2021.
- Kovaleva, O. et al. (2021). *BERT Busters: Outlier Dimensions that Disrupt Transformers.* ACL
  Findings 2021.

**PRIOR-WORK CHECK (substrate KB + repo grep), disclosed:**
`bash tools/substrate_query.sh "common mode removal whitening decorrelation anchor space rank-1
mean direction"` -> top hit cosine **0.376** (`4. Whitening / decorrelation`,
`notes/brain_fidelity_audit_native_binding_comprehension_2026-07-30.md`); no atom above 0.38.
Repo grep found a genuine 2026-06-21 arc -- `notes/skunkworks_to_research_expdev_cc_orch_WHITENING_
REVIVAL_DE_RISKED_cpu_poc_CONFIRMS_mechanism_isotropize_recovers_ARM1_2026-06-21.md` -- where
mean-centering recovered a collapsed dense-KV superposition (0.0035 -> 0.806) and shrinkage-ZCA
reached 0.843 at `cm_frac=0.999`. **That is a DIFFERENT testbed** (synthetic/learned-key
superposition recall, not the live reading path's near-neighbour 2AFC) at a **different common-mode
regime** (0.999 vs our 0.58/0.35). This cell is therefore **not a rediscovery of the mechanism** --
it is the first test of it on the live read-out. The prior arc is the reason the mechanism is
plausible and is credited as such, and it RAISES the prior that `P1` moves something; that is
exactly why the random-direction control below is non-negotiable.

---

## 1. WHY THIS IS NOT A FIFTH REPEAT OF A DEAD ROUTE

Four reweighting attempts failed on this organ: distinctiveness weighting as log-IDF; differentia
supply; genus supply; the near/far diagnostic. `notes/ORGAN_MAP.md` (organ G3, 2026-08-14
decorrelation-drill addition) identifies why: **whitening is per-dimension gain IN THE RIGHT BASIS,
and all four applied gain in the WRONG basis** -- per RAW dimension, the basis the vectors happen to
arrive in, which is not the basis the redundancy lives in.

**ESTIMABILITY is the separator.** Covariance here is estimated ACROSS concepts (2000+ anchors),
not per-dimension within a concept (~70 encounters). **Rank-1 mean removal needs `O(d)` samples and
IS estimable at `d=256`. Full covariance at `d=4096` with 2377 concepts is rank-deficient and is
NOT** -- `O(d^2)` = 65k-16M samples. **Full-covariance whitening is PARKED-BY-SAMPLE-SIZE and is
NOT attempted here.** It must not be queued off the back of this cell's result either way.

---

## 2. TESTBED, BASELINE AND FLOORS (all same-corpus, same-metric, same-run)

**Testbed:** `experiments/exp_context_conditioned_near_neighbour_v1.py` -- near-neighbour 2AFC over
WordNet dominant-sense siblings from SimpleWiki, chance **0.50 BY CONSTRUCTION**. Items, leak
controls (L1/L2/L3), profile/eval split, anchor construction and the read-out are REUSED UNCHANGED;
this cell imports them rather than re-implementing them.

**Live-path baseline to beat: 0.6980** at `d=256` under the graded default
(`hdlab/reading_grounding_loop.GRADED_COMPARATOR` ON, `38f7a0d5c`).
**`0.7495` is the `d=1024` arm and was NOT shipped -- it is not quoted as the live path anywhere in
this cell.** The `0.6395` figure in `data/exp_context_conditioned_near_neighbour_v1/metrics.json` is
the pre-flip `sign()` run and is superseded by the graded default.

**FLOORS, measured IN-CELL, on EVERY arm:**
1. **SCRAMBLE floor** -- the same arm's mechanism with a deranged donor sentence as the query
   (predecessor measured **0.4975**). Per-arm, recomputed.
2. **FREQUENCY floor** -- pick the corpus-more-frequent candidate (**0.4803**). Arm-invariant,
   computed once.
3. **CHANCE** -- 0.50 by construction.
4. **BETWEEN-PROJECTION-DRAW SD** -- the sd of accuracy across `K=20` independent random rank-1
   draws. **A gain smaller than the variation between random draws is NOT a gain.**

---

## 3. ARMS

All arms score **the SAME items** against **the SAME anchor space**, differing ONLY in a rank-1
linear map applied to both the anchor rows and the query before the cosine argmax. `d=256`.

| arm | operation | role |
|---|---|---|
| `P0_BASELINE` | identity | baseline, unchanged live path |
| `P1_COMMON_MODE` | remove `(x . u)u`, `u` = unit-normalised mean of L2-normalised anchors | **PRIMARY** |
| `P2_RANDOM_DIR` | remove `(x . v)v`, `v` a random unit direction, `K=20` draws | **THE CONTROL THAT MATTERS** |
| `P3_RANDOM_MATCHED` | subtract a FIXED random vector of the same norm as P1's mean removed component, `K=20` draws | matched-magnitude control |
| `P4_TOP_PC` | remove PC1 of the mean-centred anchor matrix | **NON-BRAIN-LICENSED**, no verdict weight |
| `P5_MEAN_SUBTRACT` | `x - mean(anchors)` (Mu & Viswanath step 1) | literal centering, reported |

**Estimation set:** `u`, PC1 and the mean are estimated from the FULL anchor population, which is
built from HELD-OUT profile sentences only and carries **no item labels**. Unsupervised, so no
answer leak; disclosed because it is in-sample with respect to the anchor set.

**Projection applied to BOTH anchors and query** (a change of basis applies to everything in the
space). Anchors-only is reported as a labelled secondary diagnostic with NO verdict weight.

---

## 4. BANDS -- FROZEN

Primary statistic: `d_P1 = acc(P1_COMMON_MODE) - acc(P0_BASELINE)`, **paired bootstrap** (arms share
items), 5000 resamples, seed fixed.

Let `mu_rand = mean_k acc(P2 draw k) - acc(P0)` and `sd_rand` = sd over the K draws
(the BETWEEN-PROJECTION-DRAW sd).

- **`HARD_FAIL_PERTURBATION_ARTIFACT`** (evaluated FIRST, dominates): `mu_rand >= d_P1`.
  Removing a random direction helps as much as removing the common mode -> the gain is perturbation,
  not decorrelation. **This is the band the four dead routes died for want of.**
- **`HARD_FAIL_NO_EFFECT`**: paired-bootstrap CI of `d_P1` INCLUDES 0.
- **`HARD_PASS`**: `d_P1 >= +0.03` AND CI excludes 0 AND `d_P1 > mu_rand + 2*sd_rand`
  AND P1's own scramble floor `<= 0.55`.
- **`MIDDLE_BAND_REAL_BUT_SMALL`**: `+0.01 <= d_P1 < +0.03`, CI excludes 0, and
  `d_P1 > mu_rand + 2*sd_rand`.
- **`MIDDLE_BAND`**: anything else.
- **META_RULE_L STRICT MARGIN 5%:** a `HARD_PASS` whose `d_P1` clears `+0.03` by less than 5% of the
  floor (i.e. `< 0.0315`) is DEMOTED to `MIDDLE_BAND_FLOOR_HUGGING`.
- **`INSTRUMENTATION_SUSPECT`** (overrides every band): the identity-projection positive control
  (sec 6) is not bit-identical to `canonicalize_fast`, or self-retrieval `< 0.70`.

**Power (CRLB).** Paired-binomial `se(delta) = sqrt(p_disc/n)`. At `n=4000` and a conservative
`p_disc=0.10`, `se=0.0050` and `mde_95=0.0098 < 0.03` -> **discriminator_reachability TRUE.**
Reported `mde_95` per delta is `1.96 * bootstrap sd`.

**Signs are pre-declared: a NEGATIVE `d_P1` is a real, reportable outcome and lands in
`HARD_FAIL_NO_EFFECT` or `MIDDLE_BAND`. Nothing is re-designated after seeing an arm.**

---

## 5. THE COMMON-MODE FRACTION IS ITSELF A REPORTED MEASUREMENT

`notes/ORGAN_MAP.md` B3 records **`||field mean|| / ||anchor|| = 0.5841` under `sign()` and `0.3545`
under GRADED**, from `experiments/diag_anchor_field_geometry_v1.py` (400 concepts x 70 held-out
sentences). The live default flipped to GRADED on 2026-08-14.

**PRE-DECLARED PREDICTION:** measured on THIS cell's anchor field under the graded default, the
common-mode fraction will be **nearer 0.35 than 0.58**. The cell reports three definitions --
`||mean a|| / mean ||a||`, the shared-direction ENERGY fraction, and mean pairwise cosine -- under
BOTH graded and `sign()` fields, and states plainly whether the 58% figure reproduces. **If it does
not, that is reported as a correction to the strategy doc's framing, not buried.**

---

## 6. POSITIVE CONTROLS AND GATES (all must pass, or the run yields no read)

- **IDENTITY-PROJECTION EQUIVALENCE (the licence for the vectorised scorer).** `P0_BASELINE`'s
  per-item correct/incorrect boolean vector must be **BIT-IDENTICAL** (sha256) to the vector
  produced by `hdlab.reading_grounding_loop.canonicalize_fast` over the same items. If it is not,
  the vectorised path is a FORK and the run is `INSTRUMENTATION_SUSPECT`.
- **SELF_RETRIEVAL_SANITY >= 0.70** (held-IN profile sentence vs one random other anchor).
- **META_RULE_AF arms-must-differ:** per-arm sha256 of the choice vector; two bit-identical scored
  arms is an assertion failure. (`P2`/`P3` draws are exempt from each other only where a draw
  provably does nothing; the P0/P1/P4/P5 set is not.)
- **META_RULE_AG baseline in band:** `0.05 < acc(P0) < 0.95`.
- **META_RULE_H cardinality:** `EXPECTED_N_UNITS` = scored arms x scales, checkpointed per unit via
  `tools/exp_checkpoint.py`.
- **DISCRIMINATOR-MUST-SURVIVE-SCALE:** multi-scale smoke at `n_items` in `(150, 600)` before FULL
  at `MAX_ITEMS=4000`. The statistic's load axis is `n_items`.
- **no bare `except`; `except SystemExit: raise` BEFORE `except Exception`; metrics written once via
  tmp + `os.replace`; `sorted(set())` never `list(set())`; thread pins before `numpy` import; SMOKE
  writes to a SEPARATE output directory.**

---

## 7. SECONDARY -- SISTER-TERM SEPARATION (pre-declared, NO verdict weight)

The read-out's known failure: it reliably retrieves paradigmatic neighbours (axon->dendrite,
artery->vessel) and cannot pick the right member. **If common-mode removal separates members WITHIN
a neighbourhood, that is a more important finding than the 2AFC delta**, so it is measured here
rather than deferred.

OPEN-VOCABULARY read-out over ALL anchors on the same held-out eval sentences, per arm:
- `top1_exact` -- argmax over all anchors is the target
- `top1_sibling_not_target` -- argmax is a WordNet loose-criterion sibling of the target but not the
  target: **the sister-term failure rate**
- `neighbourhood_hit_at_1` -- argmax in `{target} U siblings(target)`
- `sister_conversion` -- among items where `P0`'s top-1 was a sibling-not-target, the fraction that
  `P1` converts to exact. **This is the operational form of "separates members within a
  neighbourhood."**

Reported for every arm. Declared secondary; it cannot rescue a `HARD_FAIL` and cannot create a
`HARD_PASS`.

---

## 8. WHAT A RESULT DOES AND DOES NOT LICENCE

- A `HARD_PASS` licences **wiring `P1` into the read-out DEFAULT-OFF behind an explicit flag, with a
  verification witness**, and nothing more. It does **not** licence a brain claim about the hub, and
  it does **not** licence full-covariance whitening.
- A `HARD_FAIL_PERTURBATION_ARTIFACT` closes rank-1 removal on this read-out and must be recorded as
  such on `notes/ORGAN_MAP.md` G3, superseding the drill's optimism.
- A `HARD_FAIL_NO_EFFECT` is scoped to **this basis, this `d`, this read-out, this corpus** -- it is
  NOT "decorrelation is impossible," which would be the narrow-failure-to-impossible error.
- STEP 4 (`d=256 -> 1024`) remains STRICTLY AFTER this cell so capacity is not confounded with basis.
