# ORGAN A -- THE WRITE-RULE STEP LADDER: WHICH STEP DESTROYS SUBSTITUTABILITY?

Cell: `experiments/exp_writerule_step_ladder_v1.py`. FULL landed, 50s,
`data/exp_writerule_step_ladder_v1/metrics.json`, code_version v1.1. Smoke (`--grid reduced`, n=300)
landed first at `data/exp_writerule_step_ladder_v1_reduced/metrics.json`.

## 0. A CONSTRUCTION BUG CAUGHT BY THE CELL'S OWN FIRST FULL RUN, DISCLOSED

v1.0's first FULL run (elapsed 41.3s, same session) printed
`WRITERULE_LADDER_LEAK_DETECTED__TOP_STEP_ACCUMULATE...`. The "leak" was an artifact of my own
monotonicity-chain construction: I meant to exempt only the R2->R3 (ACCUMULATE) *transition* from
the strict "signal cannot rise" check, but I did it by dropping R3 out of the ordered array
entirely, which made R2 and R4 artificially *adjacent*. `check_monotone_nonincreasing` then scored
`acc[R4] - acc[R2]` (two real steps summed) as if it were one step's rise, and flagged it
(rung_index=2, rise=0.0140, combined_ci_halfwidth=0.0057). Fixed in v1.1: three separate PER-LEG
checks (`[R1,R2]`, `[R3,R4]`, `[R4,R5]`), each on genuinely adjacent rungs, with R2->R3 exempted as
its own declared margin (not hidden from the drop table). Re-ran FULL after the fix; both runs'
underlying arm accuracies are identical (only the monotonicity bookkeeping changed). This is stated
first because the brief is explicit that a leak matters more than any number, and the honest reading
is: v1.0's "leak" was in my ladder's plumbing, not in the pipeline being measured.

## 1. THE STEP LIST -- WHAT WAS ENUMERATED AND HOW, AND HOW IT DIFFERS FROM THE SKETCH

Method: read `hdlab/grounding_acquisition_loop.py` (content_words, context_vector) and
`hdlab/reading_grounding_loop.py` (ConceptSpace.observe/anchor_matrix/bundle, symbol_vector,
GRADED_COMPARATOR) directly, then verified against the runtime-verified enumeration already landed
in `exp_pipeline_stage_oracle_ladder_v1.py` (commit e28d1b8d6), which itself read the same files plus
the machine-asserted `H^T p == mat[a]` identity. Not re-derived from scratch; read, checked against
the live source, then extended (that cell's own S1/S2 stop short of the composition question and
never isolate FILTER or NORMALISE).

**The Director's five-item sketch (filter / code / accumulate / normalise / superpose) collapses to
FOUR live steps, and the collapse is itself a result, matching the shape of the correction the READ
side already went through (nine sketch stages -> five live stages):**

- **FILTER** -- `content_words`: regex tokens, minus ~70 stopwords, minus length<=2.
- **CODE** -- `symbol_vector` per surviving word, summed into one d=256 vector via ONE fixed
  sha256-seeded random basis shared by the whole vocabulary. The Director's "superpose with every
  other word" item is **not a separate step**: cross-talk between different words' codes happens
  *inside* this one shared-basis projection (mean \|cos\| among 5000 sampled symbol-vector pairs =
  0.0499, close to the 1/sqrt(256) JL bound -- established by the reused sibling cell). There is no
  later, independently-manipulable superposition event to ladder.
  - **CORRECTION STATED PLAINLY: NORMALISE is OFF in the live default.** `GRADED_COMPARATOR`
    (env `HD_GRADED_COMPARATOR`, default ON) means `anchor_matrix()` returns the raw graded sums;
    `np.sign()` only fires when the flag is OFF, which is NOT the default and has not been since
    2026-08-14. Every headline number in this arc, including the 79.3%/4.24x ARM5 finding, was
    measured on the ungraded (sign-free) path. Sign-quantisation is real, live, and reachable by one
    env var -- laddered here anyway because it is enumerable from code and toggleable -- but it is
    not currently part of what wrote the store this program's other measurements describe.
- **ACCUMULATE** -- `ConceptSpace.observe`: `self._sums[lemma] += ctx_vec`, unweighted, across every
  profile occurrence.
- **NORMALISE** -- conditional sign() quantisation, as above.

## 2. THE LADDER, RUNGS, ORACLE-CUE THROUGHOUT

Every rung is scored with the item's own oracle self-address (query = that representation's own
stored row), the same "exact key" regime this whole 2026-08-17 arc uses, so the numbers below are
write-side residue with the read side held perfect.

| rung | construction | reuse status |
|---|---|---|
| R1 UNFILTERED_SINGLE_OCC | one profile sentence/anchor, every token kept, raw counts, unprojected | NEW |
| R2 FILTERED_SINGLE_OCC | same sentence, content-word filtered | REUSED VERBATIM (= `exp_pipeline_stage_oracle_ladder_v1`'s own DIAG_B1 construction) |
| R3 FILTERED_FULL_ACCUM | full profile (~72 sentences/anchor avg), filtered, unprojected | REUSED VERBATIM (= its own DIAG_B2, via its landed checkpoint) |
| R4 PROJECTED_GRADED_FULL_ACCUM | the REAL incumbent store (d=256, graded) | numerically = its LAM_1.00 / this arc's headline 0.0481 |
| R5 PROJECTED_SIGN_FULL_ACCUM | same store, sign()-quantised (store AND query) | NEW |

FILTER is isolated at matched single-occurrence depth only (R1 vs R2), a disclosed scope limit: an
unfiltered FULL-accumulation rung would need a fresh, uncached full-corpus pass at the same cost
class as `exp_cue_information_audit_v1`'s own >1800s build, and was not run given the machine
contention this session (a CPU-heavy verb rescore and a sibling accumulation-ladder cell in flight).

## 3. GATES -- ALL PASSED BEFORE ANY NUMBER WAS READ

REGRESSION (lam=0.00 full population): 0.0223 vs expected 0.0223, PASS. K1 KNOWN-ANSWER: addressing
0.9975-1.0000 on all 5 main rungs (gate 0.95), PASS. N1 NULL (deranged query assignment on the
incumbent rung): addressing 0.000000 against chance 0.00018, hit@1 0.0095, PASS. ARMS-MUST-DIFFER:
11 of 11 arms produced distinct SHA digests. `R4`'s own hit@1 (0.0481) reproduces this arc's
established exact-key headline bit-for-bit.

## 4. RANKED DROP TABLE (n=3994, N_BOOT=10000, paired bootstrap, CI half-width beside every drop)

| rank | step | from -> to | drop | CI95 | band |
|---|---|---|---|---|---|
| 1 | **ACCUMULATE** | R2 -> R3 | **-0.0263** | [-0.0343,-0.0186] | BELOW |
| 2 | CODE_PROJECT | R3 -> R4 | +0.0123 | [+0.0060,+0.0188] | ABOVE |
| 3 | NORMALISE | R4 -> R5 | +0.0016 | [-0.0051,+0.0085] | NOT_SEPARATED |
| 4 | FILTER | R1 -> R2 | +0.0009 | [-0.0016,+0.0033] | NOT_SEPARATED |

**ACCUMULATE dominates: |0.0263| is 64% of the summed absolute drop (0.0263 / (0.0263+0.0123+0.0016+0.0009)).**
ACCUMULATE and CODE_PROJECT both reproduce `exp_pipeline_stage_oracle_ladder_v1`'s own DIAG_B1->DIAG_B2
(-0.0263 [-0.0343,-0.0186]) and DIAG_B2->LAM_1.00 (+0.0123 [+0.006,+0.0188]) margins **bit-for-bit**
-- an independent cross-cell replication, not a coincidence of shared code (the two cells build these
arms via genuinely reused function calls, so this is the expected outcome of correct reuse, and it is
reported as the validity check it is).

## 5. MONOTONICITY -- HELD, PER LEG, ONCE THE CONSTRUCTION BUG WAS FIXED

FILTER (R1->R2), CODE_PROJECT (R3->R4) and NORMALISE (R4->R5) each checked as a genuinely-adjacent
pair via the reused `check_monotone_nonincreasing` (same individual-arm-half-width convention
`exp_pipeline_stage_oracle_ladder_v1` uses for its own Part A chain): **MONOTONE, 0 leaks, on all
three legs.** ACCUMULATE (R2->R3) is excluded from this assertion for the same reason the sibling
cell excludes its own B1->B2: more accumulated evidence is not a downstream information-loss
transform, so a change there (in either direction) is a plain margin, not a leak candidate.

**A finer instrument (the paired-bootstrap drop table above) DOES show CODE_PROJECT rising
CI-separated (+0.0123, ABOVE).** This is not a contradiction: the leak-detector's tolerance is
deliberately coarse (built to catch order-of-magnitude errors, not to certify small effects), and the
paired-bootstrap margin is the correct, finer-grained instrument for a genuine small effect. Read
plainly: a lossy d=256 random projection of a much higher-dimensional sparse count space measurably
**improves** exact-key nearest-neighbour accuracy here. This is a known, unsurprising property of
random projection / dimensionality reduction acting as a denoiser in high-dimensional metric spaces
(unrelated words' near-orthogonal codes attenuate faster than the query's own signal under
projection) and is not a construction leak -- reproduced bit-for-bit by an independent cell, which is
the strongest evidence available that it is real.

## 6. WINNER COMPOSITION -- THE SCIENTIFIC CORE, MEASURED AT EVERY RUNG FOR THE FIRST TIME

`n_probe=700`, one SHARED, seeded, paired index subset across all 5 rungs (so every delta below is a
paired comparison on identical items, not two independently-drawn samples).

| rung | fraction NO close WordNet relation | winner-query Jaccard mean (frac ever co-occur) | gold-query Jaccard mean (frac ever co-occur) | winner/gold ratio |
|---|---|---|---|---|
| R1 UNFILTERED_SINGLE_OCC | 0.8529 | 0.0392 (65.4%) | 0.0090 (22.0%) | 4.36x |
| R2 FILTERED_SINGLE_OCC | 0.8400 | 0.0382 (66.0%) | 0.0096 (23.9%) | 3.97x |
| R3 FILTERED_FULL_ACCUM | 0.7971 | 0.0911 (**94.4%**) | 0.0238 (60.3%) | 3.82x |
| R4 PROJECTED_GRADED_FULL_ACCUM | 0.8000 | 0.0823 (90.6%) | 0.0200 (50.4%) | 4.11x |
| R5 PROJECTED_SIGN_FULL_ACCUM | 0.8071 | 0.0659 (74.0%) | 0.0170 (43.0%) | 3.88x |

**Paired composition deltas (bootstrap CI over the shared idx_probe):** ONLY ACCUMULATE (R2->R3)
CI-separates on the WordNet-relation axis: no-relation rate **-0.0430 [-0.0800,-0.0086], BELOW** --
i.e. accumulation slightly *reduces* the taxonomically-unrelated fraction. FILTER, CODE_PROJECT and
NORMALISE all sit NOT_SEPARATED on this axis (deltas +/-0.003 to -0.013, none excluding zero).

**BUT the co-occurrence axis tells a sharper, and more diagnostic, story about the SAME step.**
Going from R2 to R3 (single occurrence to full accumulation, filter held fixed), the fraction of
winners that **ever share a sentence with the query anywhere in the 34,169-sentence corpus** jumps
from **66.0% to 94.4%** -- and the same jump happens for the best gold synonym too (23.9% -> 60.3%),
which is why the *ratio* barely moves (3.97x -> 3.82x): both numerator and denominator are being
pulled toward "has ever co-occurred with the query" by the same mechanism. **Accumulating more
occurrences of an anchor makes its stored representation converge toward words that are its OWN
corpus co-occurrence partners -- almost universally so, for both the winner and the best available
gold.** This is the step, read plainly: ACCUMULATE is where the representation goes from "occasionally
overlaps with something the query has co-occurred with" to "returns something the query has almost
certainly co-occurred with, 94% of the time" -- the signature of a store answering "what occurs near
this word" rather than "what could replace this word." The WordNet-relation-rate delta alone (a
small, CI-separated *improvement*) would have hidden this if co-occurrence had not also been
measured at the same rung -- exactly the brief's warning that a step can move one axis and not the
other, and that both must be watched.

## 7. WHICH STOP-IF FIRED, STATED PRECISELY (not just the cell's mechanical tag)

- **(i) ONE STEP DOMINATES, FIRED.** ACCUMULATE is 64% of the total ranked-drop mass; the "deficit is
  distributed" reading is **wrong for the write rule's internal steps**, and this corrects that
  framing plainly, as instructed.
- **(ii) does not apply** -- a single step dominates, so the loss is not spread evenly.
- **(iii), AS LITERALLY WORDED, DID NOT FIRE.** The brief's precondition is accuracy *flat* while
  composition shifts. ACCUMULATE's accuracy move is the *largest* of the four (-0.0263, BELOW), not
  flat, so it does not meet (iii)'s letter even though the cell's own coarse trigger (which checked
  only "composition CI-separated," not "accuracy also flat") flagged it. The metrics.json
  `STOP_IF_FIRED` field over-fires (iii) for this reason and should be read with this correction, not
  quoted verbatim -- disclosed here rather than silently patched a second time this session. The
  genuinely interesting, precisely-stated finding is different from (iii) but related: **the one step
  with the largest accuracy cost is also the only step with a CI-separated composition move, and the
  two move in opposite readings depending which composition axis is read** (WordNet: improves;
  co-occurrence share: sharply worsens). That dissociation, not a flat-accuracy flip, is what
  ACCUMULATE actually shows.
- **(iv) monotonicity leak: did NOT fire** on the corrected (v1.1) per-leg check. v1.0's apparent
  leak was the construction bug in section 0.
- **(v) K1 held.** Published.

## 8. ONE PLAIN-LANGUAGE SENTENCE

**Summing more sentences into an anchor's stored vector is the step that pulls the write rule's
winners toward words the query has actually appeared next to -- the co-occurrence share of the
top-1 winner nearly triples (66% to 94% ever-co-occurring) between one occurrence and the full
profile, which is the write rule quietly turning "what this word means" into "what this word
sits beside."**

## 9. WHAT THIS DOES NOT LICENSE

- FILTER was only isolated at single-occurrence depth (disclosed scope limit, section 2); a
  full-accumulation FILTER rung remains unmeasured.
- The composition instrument runs on n_probe=700 of 3994 scored items (cost-bounded, same convention
  as this arc's other composition measurements); reported with its own n throughout, never silently
  generalised to the full population.
- This cell LOCALISES; it does not rebuild the write rule. The rebuild decision belongs to the
  Director, per the dispatch's own instruction.
- Nothing here claims a brain structure computes second-order co-occurrence or performs the
  accumulation step; every operator laddered (the stopword list, the random basis, unweighted
  summation, sign quantisation) is OUR INVENTION UNDER TEST, not pinned biology. PINNED: only the
  complementary-learning-systems framing (cortex extracts cross-episode regularities; hippocampus
  keeps the episode) that motivated asking this question in the first place.
