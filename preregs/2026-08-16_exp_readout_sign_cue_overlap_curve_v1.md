# PRE-REG: exp_readout_sign_cue_overlap_curve_v1

**Written and committed BEFORE the cell was run.** Author: exp_dev. Date: 2026-08-16.
Branch `dataprep/mcguffey-graded-corpus`. Parent read-out: `exp_grounding_readout_known_answer_v1`
(C3), arm `B5_OPEN_REAL`.

ASCII-only. No external LLM at any point (asserted at runtime over `sys.modules`, not by
inspection).

---

## 0. PREMISE CHECK FIRST (PLAN R12: verify a spec's premise by RUNTIME RECONSTRUCTION)

The dispatch brief asserted "the live read-out signs". That premise was checked by RUNTIME
OBSERVATION before this cell was designed, not by grep: `numpy.sign` was monkeypatched with a
caller-frame recorder and the REAL C3 harness functions were then driven end to end
(`tools/audit_readout_sign_sites.py`, outputs `scratch/readout_sign_sites_G1.json` and
`_G0.json`).

**Result, under the LIVE default `HD_GRADED_COMPARATOR=1`:**

| read-out phase | `np.sign` calls reached |
|---|---|
| 1 ENCODE one encounter (`context_vector_masked`) | **0** |
| 2 ACCUMULATE the whole space (`ConceptSpace.observe`) | **0** |
| 3 FIELD (`ConceptSpace.anchor_matrix`) | **0** |
| 4 QUERY (`ConceptSpace.bundle`) | **0** |
| 5 COMPARE (`canonicalize_fast`) | **0** |
| 6 COMPARE via the reference `canonicalize` | **1** -- `hdlab/reading_grounding_loop.py:757` |
| 7 held-out-sentence query then compare | **0** |

Under `HD_GRADED_COMPARATOR=0` (the pre-2026-08-14 production convention) the same trace reaches
FOUR switch-aware sites: `hdlab/grounding_acquisition_loop.py:160` (`context_vector`, per
encounter), `hdlab/reading_grounding_loop.py:506` (`anchor_matrix`, the field),
`:520` (`bundle`, the query) and `:806` (`canonicalize_fast`, the query at compare time).

**So the brief's premise is HALF TRUE and the half that is true is the half nobody has measured:**

- The C3 **measurement** path (`canonicalize_fast`) does **NOT** sign under the live default.
  Turning the switch off there is exactly `exp_graded_path_vs_orthographic_floor_v1`, which
  measured **+0.0015, CI [-0.0055,+0.0083], NULL** (STATUS DO-NOT-REDO 34). That null is the
  **f = 100% point of the curve this cell runs** and this cell must REPRODUCE it there.
- The **production grounding decision** path still signs, at a site the switch does not reach:
  `canonicalize` (`:757`) hardcodes `np.sign(new_raw_sum)` UNCONDITIONALLY. It is called live at
  `reading_grounding_loop.py:1273` (inside `_make_grounding_gate.gate`) and `:1492` (inside
  `checkpoint`, the banking path). Measured on 200 C3 items under the live graded default, it
  **disagrees with `canonicalize_fast` on 37.0% of items** (126/200 agree;
  `scratch/canonicalize_divergence.json (tools/audit_canonicalize_divergence.py)`). Its own licensing self-test
  (`_selftest_canonicalize_fast_matches_reference`, `:1793`) is **blind to this** because every
  query it tests is bipolar scaled by a positive constant, for which `sign()` is the identity up
  to a positive scalar.

**Therefore the prior null does NOT cover this cell's `A_GS` arm (graded field, SIGNED query),
which is precisely the `:757` configuration, at any cue overlap.** This is the arm the enumeration
licensed and it is why the cell is not a re-run of a closed experiment.

**DISCLOSED AND NOT FIXED:** the `:757` switch-blindness and the blind self-test are a real defect
in a live-path file. This cell does not edit `hdlab/`. It measures.

---

## 1. THE QUESTION

The terminal `sign()` is FREE under an exact key and CI-SEPARATED EXPENSIVE under a partial cue on
a synthetic hub-and-spoke object (0.9668 -> 0.7018 at 50% cue overlap,
`exp_hub_spoke_partial_cue_curve_v1`, `479752925`). **Does that axis dependence reproduce on the
REAL open-vocabulary read-out?**

The C3 read-out queries with `space.bundle(L)` -- the item's OWN fully accumulated context sum.
That is an exact key. Production at question time never has one. So: measure signed versus graded
**across a cue-overlap curve**, not at a single point.

## 2. WHAT IS MEASURED, AND ON WHAT

**Task: the REAL read-out.** `exp_grounding_readout_known_answer_v1` B5_OPEN_REAL, unchanged --
open-vocabulary argmax over every anchor except the lemma's own and its normalized-lemma siblings.
Corpus, buckets, space construction, item construction and gold sets are IMPORTED from that cell,
not re-implemented. Identical scorer / n / pool / gold across every arm.

- n_items = 4000, n_anchors = 5491 (full run), d = 256.
- Gold = WordNet 3.0 generous meaning set (`C3.gold_meaning_set`), self and morphological variants
  removed.
- Reported per arm: **open-vocabulary hit@1**, **fraction of gold in the top 50**, **median rank**.
  NO 2AFC number is used as a headline (STATUS DO-NOT-REDO 34/35: a two-choice gain may not be
  carried onto this pool).
- Paired bootstrap, 5000 resamples, shared resample indices across ALL arms so any contrast is
  paired.

## 3. THE ARMS

Four read-out conventions, all on the SAME graded accumulation (`ConceptSpace.observe` accumulates
the raw graded sum regardless of the switch, `reading_grounding_loop.py:462-466`):

| arm | field | query | what it is |
|---|---|---|---|
| `GG` | graded | graded | the LIVE default (`GRADED_COMPARATOR=1`) |
| `SS` | signed | signed | the pre-2026-08-14 production convention (`:506`+`:520`/`:806`) |
| `GS` | graded | **signed** | **the `canonicalize`:757 configuration -- switch-blind, live, never measured** |
| `SG` | signed | graded | completes the 2x2; the docs call this "worse than either" |

Signed field is `np.sign(mat)` and signed query is `np.sign(q)`; a self-test asserts these are
BIT-IDENTICAL to what `ConceptSpace.anchor_matrix()` / `.bundle()` actually return when the module
constant `GRADED_COMPARATOR` is monkeypatched to False (the environment is inert after import).

## 4. THE CUE AXIS -- TWO INDEPENDENT MODELS

Both are **OUR-INVENTION-BEING-TESTED**, not brain facts. Two are run because a result that holds
under only one operationalisation is weaker than one that holds under both.

**MODEL A -- dimension substitution.** `q_f` keeps the target's own bundle on a random
`ceil(f*d)` dimensions and takes a donor item's bundle on the rest. Chosen to match
`exp_hub_spoke_partial_cue_curve_v1` exactly so the two measurements are comparable. Note that
elementwise selection and `sign()` COMMUTE, so under Model A the order of mixing and signing is
not a free choice and cannot be a confound.

**MODEL B -- evidence subsample.** `q_f` is the sum of the target's context vectors over a nested
random subset of `ceil(f*n_profile)` of its OWN profile sentences, accumulated in the original
insertion order so that `f = 1.00` is BIT-IDENTICAL to `ConceptSpace.bundle(L)`. This is the
brain-honest model: a real query carries fewer encounters, and evidence magnitude -- the thing
`sign()` destroys -- is exactly what shrinks.

`f` in {1.00, 0.80, 0.50, 0.20, 0.00}. At `f = 0.00` both models return the donor's vector, which
is the pre-existing scramble floor.

**Plus a third, non-synthetic cue: `H_SENT`, a single HELD-OUT SENTENCE as the query** -- what
production actually has at question time. Reported on its own row with its own n (items carrying a
held-out sentence), never merged into the curve.

## 5. FLOORS AND CONTROLS -- THEY FAIL INDEPENDENTLY

**FLOORS (standalone, on the identical scorer/n/pool/gold).** A floor is not an ablation of the
system under test; each of these is a complete alternative channel.

- `F_ORTHO` -- character-trigram profile only, ZERO substrate signal (`MS.trigram_matrix`). This is
  the floor that BEATS us: 0.0870 [0.0783,0.0960] versus our 0.0480.
- `F_FREQ` -- pick the most frequent eligible anchor.
- `F_SCRAMBLE_G` / `F_SCRAMBLE_S` -- donor query against the graded / signed field (= the
  `f = 0.00` point).

**KNOWN-ANSWER ARM (licenses the INSTRUMENT).** `K_SELF` -- the same query with the target's own
anchor left ELIGIBLE. Must return the target at >= 0.99 at `f = 1.00`. Plus the harness's own 2AFC
self-retrieval positive control, which must be >= 0.70.

**NULL ARM (licenses the EFFECT).** `N_NULLCONTENT` -- a field of random bipolar sums with matched
per-anchor observation counts, scored identically. Must sit at the gold base rate.

These fail independently: a failing known-answer arm voids every number in the cell; a failing null
arm voids the effect but not the instrument.

## 6. PRE-REGISTERED VALIDITY GATES (PV) -- all must pass or the cell reports INSTRUMENT_STILL_LOOSE

| id | gate |
|---|---|
| PV1 | `MA_f100_GG` reproduces the landed C3 headline **0.0480** to 1e-9 |
| PV2 | `MA_f100_SS` reproduces the landed `A9_GRADED_OFF` **0.0465** to 1e-9 (proves the prior null IS the f=1 point) |
| PV3 | `F_ORTHO` reproduces the landed `A6_TRIGRAM_ONLY` **0.0870** to 1e-9 |
| PV4 | `MB_f100_GG` is BIT-IDENTICAL to `MA_f100_GG` (the two cue models share their endpoint by construction) |
| PV5 | the cue axis is what it is labelled: mean `cos(q_f, q_1.00)` strictly decreasing in `f` for BOTH models |
| PV6 | no-overlap control: at `f = 0.00` every arm sits at or below its matched scramble floor |
| PV7 | known-answer `K_SELF` >= 0.99 at `f = 1.00`, AND 2AFC self-retrieval >= 0.70 |
| PV8 | null-content arm within 0.01 of the gold base rate |
| PV9 | arms-must-differ: sha256 over each arm's hit vector; the ONLY collisions permitted are the pre-declared `MA_f100_* == MB_f100_*` endpoint identities and `MA_f000_* == MB_f000_*` |
| PV10 | signed field/query construction bit-identical to the REAL switch (monkeypatched module constant, real methods called) |
| PV11 | no external LLM: assert no `openai`/`anthropic`/`transformers`-API module in `sys.modules` |

## 7. THE BANDS -- WHAT COUNTS AS A RESULT

Two questions are decided SEPARATELY and must never be reported as one.

**Q1 -- IS THE SIGN AXIS-DEPENDENT? (a within-system contrast, NOT a capability claim.)**
The discriminator is the **difference in differences**:
`DiD = (GG - SS)@f_low - (GG - SS)@f=1.00`, paired bootstrap, per cue model.

- `SIGN_COSTS_MORE_UNDER_PARTIAL_CUE` -- DiD > 0 with CI excluding zero at `f = 0.50` or `f = 0.20`.
- `SIGN_IS_AXIS_INDEPENDENT` -- DiD CI includes zero at EVERY f. Then the prior null generalises
  off the exact-key point and the lead is dead. **This is a real, reportable outcome and no tuning
  is permitted to escape it.**
- `SIGN_COSTS_LESS_UNDER_PARTIAL_CUE` -- DiD < 0, CI excluding zero. Also reportable.

**Q2 -- IS ANY ARM ACTUALLY GOOD? (the capability claim, and the bar is the floor.)**
An arm is called GOOD at a given `f` only if its hit@1 is **CI-SEPARATED ABOVE
max(F_ORTHO, F_FREQ, F_SCRAMBLE)** on the identical scorer/n/pool/gold. Never a bare number.
PRE-DECLARED EXPECTATION: **no arm clears this at any f.** The spelling floor is 1.8x our hit@1 at
the exact key and the curve can only degrade us. Q1 can therefore be answered POSITIVE while Q2 is
answered NEGATIVE, and that combination must be stated in exactly those words.

**FAIL BAND (envelope-fail).** If `MA_f100_GG != 0.0480` or `K_SELF < 0.99` or self-retrieval
< 0.70, the cell publishes NO quality number and reports `INSTRUMENT_STILL_LOOSE`.

**STOP-IF.** No threshold, floor definition or arm key in this file may be changed after the run.
If a gate fires, it is reported fired.

## 8. BRAIN-FIDELITY BLOCK (PLAN R13 -- all four parts, mandatory)

**(a) BRAIN STRUCTURE.** The operation under test sits at the read-out of an **anterior temporal
lobe semantic hub** fed by **modality spokes**, queried under a **partial cue**, which in the brain
is resolved by **CA3 recurrent collaterals** completing from a degraded pattern (paired with
**dentate gyrus** separation). Those are neural systems, not cognitive labels.

**What pins hard sign-quantisation of a population code? NOTHING, and we say so.** Cortical and
hippocampal neurons carry **GRADED firing rates**; a population code's information is in the rate
vector, not in a per-neuron 1-bit threshold. Cortical gain control is **divisive normalisation with
a pool-shared denominator** (Carandini & Heeger 2012, *Nat Rev Neurosci* 13:51-62), which
**preserves** the ratios that `sign()` flattens to 1. We have found **no biological fact that pins
a terminal per-component sign** anywhere in this pipeline. **`sign()` is OUR CONVENIENCE** -- a
1-bit code is cheap, fast and hashable -- and it is exactly the class of substitution the owner has
named as how we lose. This cell is a measurement of the cost of that substitution, not a defence
of it.

Honest counterweight, stated so this is not a one-sided brief: the graded switch's own MECHANISM
story was WITHDRAWN (`f05b8a88a`), an unmodified `sign()` at d=1024 BEATS graded at d=256, and
divisive normalisation measured +0.00175 with a CI including zero for us -- because cosine is
invariant to a scalar denominator. So "graded is brain-faithful" does not by itself predict a win.

**(b) ORGAN REUSE.** Enumerated FROM DISK first, then reconciled to
`data/capability_registry.jsonl` -- never the reverse.

REUSED, imported and called, NOT re-implemented:
`hdlab/reading_grounding_loop.py` (`ConceptSpace`, `context_vector_masked`, `canonicalize_fast`,
`canonicalize`, `normalize_lemma`), `hdlab/grounding_acquisition_loop.py` (`context_vector`),
`experiments/exp_grounding_readout_known_answer_v1.py` (corpus, buckets, space, items, gold,
`_is_variant`), `experiments/exp_meaning_supply_separation_v1.py` (`trigram_matrix`),
`tools/exp_checkpoint.py`.

BUILT BY THIS CELL: nothing durable. No `hdlab/` module is added or edited. The two cue models and
the 2x2 field/query factorisation are measurement scaffolding that lives inside the cell.

Registry reconciliation is reported in the metrics as a residue both ways; the registry is not
edited (a sibling agent owns it).

**(c) EVERY CHOICE TAGGED.**

| choice | tag |
|---|---|
| meaning lives in a hub fed by modality spokes, each keeping its own address | PINNED-BY-EVIDENCE |
| CA3 completes from a partial cue; DG separates; they are a matched pair | PINNED-BY-EVIDENCE |
| neurons carry graded rates; nothing pins a terminal per-component sign | PINNED-BY-EVIDENCE (as an ABSENCE: no source pins the quantiser) |
| divisive normalisation has a pool-shared denominator | PINNED-BY-EVIDENCE (and measured NULL for us, for a stated mathematical reason) |
| "partial cue" = dimension substitution from a donor item (Model A) | OUR-INVENTION-BEING-TESTED |
| "partial cue" = subsample of the item's own encounters (Model B) | OUR-INVENTION-BEING-TESTED |
| cosine over a stacked anchor matrix as the retrieval metric | OUR-INVENTION-BEING-TESTED (there is no cosine in the brain; the honest analogue is a settling trajectory whose metric is UNPINNED) |
| a single held-out sentence as the production cue | PINNED-BY-EVIDENCE that the brain queries from an occasion, OUR-INVENTION that one sentence is the right unit |

**(d) SHELVE / REVIVAL CRITERION, BRAIN-FRAMED, never performance-framed.**
If the sign turns out to cost nothing at any cue overlap, the correct conclusion is NOT "the sign
is fine". It is: **this read-out has no completer in front of it, so a degraded cue is never
completed, only scored** -- the DG-without-CA3 diagnosis. The revival criterion is then
`retest the quantiser once a CA3-shaped completion stage sits between the cue and the field`,
never `retest if the number improves`. Conversely, if the sign does cost more under a partial cue,
the brain-framed reading is that a 1-bit code discards exactly the evidence-strength signal a
recurrent completer would need to settle on, which raises the priority of the completer rather
than of the quantiser alone.

## 9. WHAT THIS CELL CANNOT SETTLE (stated before the run)

- It measures the READ-OUT. It does not change the encoder, and every arm shares an encoder that
  is measurably the structure-axis null. A geometry with no meaning in it cannot be rescued by
  changing how it is quantised, and no number here licenses the opposite claim.
- The `:757` production-grounding site is measured as a READ-OUT CONFIGURATION (`GS`). This cell
  does not re-run the reading loop and does not measure what the banked store would contain if
  `:757` followed the switch.
- Both cue models are ours. A different degradation model could give different numbers.
- NO COMPLETER IS BUILT. This measures the code with no CA3-shaped pattern completion in front of
  it. That is the current substrate, not the brain.

---

## 9b. AMENDMENTS AFTER THE SMOKE GATE, BEFORE THE FULL RUN (2026-08-16, dated)

The smoke run (`data/exp_readout_sign_cue_overlap_curve_v1_smoke/metrics.json`, 716 anchors,
300 items, 20 s) returned `INSTRUMENT_STILL_LOOSE` on PV8 and PV9. Both are recorded here with
their DIRECTION before the full run, per the standing rule that a gate change made after seeing
data must be visible.

**A1 -- PV9's digest moves from the HIT vector to the PICK vector. DIRECTION: TIGHTENS.**
The gate as written digested each arm's correctness vector. At an approximately 5% hit rate over
300 items that vector is a 300-bit summary at 5% density, so two arms that make *entirely
different wrong picks* produce the *identical* digest. The smoke run demonstrated exactly this: 16
arms collided, including `MA_f050_SS` with `MA_f000_SS` -- arms whose queries are provably
different vectors. **The gate was measuring the wrong object.** It now digests the arm's PICK
vector (the argmax anchor index per item), which is strictly more sensitive: any two arms that
differ in even one pick now differ. Hit digests are still reported, they simply no longer gate.
NO THRESHOLD IS CHANGED.

**A2 -- `K_SELF_GG` and `K_SELF_SS` are added to the permitted-identity set. DIRECTION: LOOSENS,
and it is stated as loosening.** These are the KNOWN-ANSWER arms. PV7 requires both to return the
target on >= 99% of items; two arms both at 1.0000 are identical BY CONSTRUCTION, and a gate that
demands the known-answer arms differ from each other is incoherent with the gate that demands they
both succeed. This removes exactly two arms from the collision check. Every measurement arm and
every floor remains in it. NO THRESHOLD IS CHANGED.

**A3 -- PV8 is NOT changed, and the smoke failure is diagnosed as UNDERPOWER, in advance.**
Observed at smoke: null-content 0.04667 against a gold base rate of 0.03336, a gap of 0.01333.
At n=300 the standard error of that rate is 0.01037, so the pre-registered +-0.01 band is **0.96
standard errors wide** -- a gate that narrow cannot pass at smoke scale even when the null is
perfectly at base rate, and the observed gap is only 1.29 SE. At n=4000 the standard error is
0.00284, the band is **3.52 standard errors wide**, and the gate becomes a real test.
**The threshold is NOT touched. If PV8 fails at FULL scale, that is a real leak in the null arm
and the cell must report `INSTRUMENT_STILL_LOOSE`.** This prediction is recorded before the full
run so that its confirmation is evidence and not a rationalisation.

**A5 -- MODEL A's substituted dimensions now come from MANY donors, one per dimension, instead of
from ONE donor's whole vector. DIRECTION: this FIXES A DEGENERATE ARM; it is not a threshold
change.** The smoke run proved the original construction vacuous. With a single donor supplying
every non-target dimension, that donor's OWN anchor row sits in the eligible pool as a near-exact
match, so the argmax returns the donor rather than degrading gracefully. Measured at smoke:
`MA_f020_SS`, `MA_f050_SS` and `MA_f020_GS` returned the donor on **300 of 300 items**, giving
pick vectors BIT-IDENTICAL to the `f = 0.00` floor -- the "50% cue overlap" arm was not measuring a
degraded cue at all, it was measuring "is the donor in the target's gold set". The graded arm was
damaged the same way (280 distinct picks of 300). The fix: each substituted dimension takes its
value from an INDEPENDENTLY drawn anchor (never the target or its normalized-lemma siblings), so
the non-target part of the cue is incoherent noise rather than one coherent competitor. This is
also what the sibling cell `exp_hub_spoke_partial_cue_curve_v1` actually did -- it degraded each
spoke independently -- so the two measurements become comparable rather than only nominally alike.
The donor draw is fixed per (item, dimension) across all `f`, so the curve stays NESTED.

Consequences, all recorded: `f = 0.00` now means ZERO target content (a multi-donor mixture),
which is a cleaner no-overlap control; and the single-donor scramble floor is restored as its own
STANDALONE arm `F_SCRAMBLE_G` / `F_SCRAMBLE_S` (query = one donor's whole bundle), which is the
construction the landed cells used and whose landed value is 0.01375. It is no longer an alias.
PV6 now reads: at `f = 0.00` every arm sits at or below the matched scramble floor.
NO THRESHOLD IS CHANGED, and PV1/PV2/PV3 are unaffected because they are all at `f = 1.00`.

**A6 -- `F_SCRAMBLE_G == F_SCRAMBLE_S` is added to the permitted-identity set. DIRECTION: LOOSENS,
and the mechanism is ANALYTICALLY PINNED and REPRODUCED FROM DISK.** With one donor's whole bundle
as the query, that donor's own anchor row is an exact match at cosine ~1 in BOTH the graded and the
signed field, so the argmax is the donor under either convention -- quantisation cannot change a
self-match. This is not a new artefact of this cell: the landed
`data/exp_graded_path_vs_orthographic_floor_v1/metrics.json` carries
`F_SCRAMBLE_ON` and `F_SCRAMBLE_OFF` at the same 0.01375 with the **identical sha256 digest**
`4596b30dc13e9692`. Reproducing that identity is evidence the floor is constructed the same way,
not evidence of a collision. It is exactly this mechanism that A5 removes from the CURVE arms.

**A4 -- observation recorded before the run, not a change.** MODEL B degrades the cue far more
gently than MODEL A: at smoke, measured cos to the exact key is 0.956 / 0.828 / 0.632 at
f = 0.80 / 0.50 / 0.20, versus MODEL A's 0.782 / 0.518 / 0.262. That is expected -- a subsample of
one word's own encounters stays similar to their sum -- and PV5 still passes. It means MODEL B is
the WEAKER manipulation of the two and a null there is less informative than a null under MODEL A.
The `H_SENT` arm (a single held-out sentence) is the extreme point of MODEL B's axis and carries
that end of the range.

---

## 10. HOUSEKEEPING

Runner: `cpu_runner_local` for the smoke gate; the full run blocks in-session per the operator's
instruction. `--self-test` asserts VALUES, not absence of errors. Thread pins set in the `.py`
before numpy is imported. Per-unit checkpoint via `tools/exp_checkpoint`, `sorted(set())` resume
order, atomic `os.replace` metrics write, `except SystemExit: raise` before `except Exception`.
`progress_logging`: every score pass prints a flushed progress line (the run exceeds 1800 s).
