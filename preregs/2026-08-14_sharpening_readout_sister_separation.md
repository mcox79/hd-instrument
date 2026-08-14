# PRE-REG: does a SHARPENING (dense/modern-Hopfield) read-out separate PARADIGMATIC SISTERS?

anchor_name: `exp_sharpening_readout_sister_separation_v1`
authored: 2026-08-14
status: COMMITTED BEFORE the experiment file was written and BEFORE any arm was scored.

ASCII-only.

## 0. Prior-work check (MANDATORY, ran before authoring)

`bash tools/substrate_query.sh "dense modern Hopfield sharpening readout separate correlated
sister anchors near neighbour"` -> top hit `dense_hopfield_readout_capacity_correlated_codes_v1`
at cosine **0.3154**; hits 2-5 at 0.293 / 0.291 / 0.289 / 0.279, all BELOW the 0.30 bar.

Prior-work check: `[dense_hopfield_readout_capacity_correlated_codes_v1 @ 0.3154]`. That single
hit is this cell's acknowledged PARENT, not a rediscovery: it measured dense-Hopfield CAPACITY on
synthetic correlated codes and never touched a read-out over real anchors. No prior cell in the KB
applies a sharpening read-out to the near-neighbour or open-vocabulary anchor read-out.

## 1. The defect

The open-vocabulary read-out finds the right NEIGHBOURHOOD and cannot pick the right MEMBER. Every
correct hit in `exp_grounding_readout_known_answer_v1` is a paradigmatic SISTER of the target
(axon->dendrite, artery->vessel, anaphase->telophase, atrium->ventricle).

MEASURED@data/exp_grounding_readout_known_answer_v1/metrics.json -- live open-vocabulary
hit@1 4.80% vs scramble 0.80%, n=4000, 5491 anchors. Real, 6x its floor, 5.2pp short of the 10%
revival gate. Retrieval is NOT the constraint: SELF_RETRIEVAL 0.786.

This is a SEPARATION problem, and separation of CORRELATED codes is exactly what a
sharpening/super-quadratic energy is for.

## 2. The lead, and its honest provenance

MEASURED@data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json (2026-07-14,
FULL, HARD_PASS): dense/modern-Hopfield read-out gives a **3.25x capacity lift on CORRELATED
codes**; scramble floor 0.01; per-correlation lift 6.74x (mild) -> 3.12x (moderate) -> 1.63x
(strong). A supersession check found no later cell on the same eval. It was never wired to a
read-out over real anchors.

**Note the direction of that gradient.** The lift SHRINKS as correlation strengthens (6.74 -> 1.63).
Sisters are the STRONGLY-correlated end. The parent cell's own numbers therefore predict the
SMALL end of its effect here, not the large end. This is stated before the run so that a null
cannot be reframed afterwards as "we expected more".

## 3. THE PRE-DECLARED EXPECTED FAILURE MODE: the codebook SNR wall

MEASURED@data/exp_cleanup_graded_attractor_vs_argmax_v1 (2026-07-20): modern-Hopfield ~= plain
argmax at the cliff; verdict `STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE`.

**The honest prior for this cell is therefore NULL.** If the binding constraint is the
signal-to-noise ratio of the codebook itself -- if the evidence separating target from sister is
not present in the anchor scores at all -- then no cleanup rule, however sharp, can manufacture it,
and this cell returns null. That is the EXPECTED outcome and it is a RESULT: it closes
cleanup-rule fixes as a CLASS for the sister-separation defect.

### 3.1 What distinguishes "sharpening works" from "we are at the SNR wall"

Declared in advance, adjudicated on measured quantities:

| observation | reading |
|---|---|
| accuracy moves at INTERMEDIATE beta with an inverted-U, scrambled-score control stays flat | SHARPENING WORKS |
| entropy curve demonstrably sweeps uniform -> Dirac while accuracy is FLAT at every beta | SNR WALL (mechanism had full dynamic range and the decision was invariant to it) |
| accuracy moves and the scrambled-score control moves as much | NOT separation -- content-blind artifact |
| target's baseline rank among all anchors is deep (median rank >> 1, large `frac_target_outside_top50`) | SNR WALL, corroborated independently of any beta |

The entropy sweep is a GATE, not a report: if the sweep fails to produce both a
normalised-entropy > 0.80 point and a < 0.20 point, the cell has NOT tested sharpening and
returns `SWEEP_DID_NOT_SPAN_THE_RANGE` instead of a verdict.

## 4. PRE-DECLARED DEAD -- not retried here

peel/SIC read-out. `exp_encoder_peel_sic_readout_realcodes_v1` HARD_PASSed (flat argmax 0.204 ->
0.940) and was refuted FIVE HOURS LATER by
`exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1_smoke`: HARD_FAIL,
"NEITHER_READOUT_FIX_LIFTS_RET_AGREE10: best 0.1058 < 0.3 ... the gap is a quantization-resolution
vs neighborhood-crowding problem." That is this exact defect, already attacked by that route,
already failed. No peel/SIC arm appears in this cell.

## 5. THE ANALYTIC TRAP THIS CELL MUST NOT FALL INTO

**A softmax over the TWO eligible candidate scores is analytically pinned to plain argmax.**
softmax is monotone, so `argmax_c softmax(beta*s)_c == argmax_c s_c` for every beta > 0. A cell
that "sharpens" a 2AFC score pair measures nothing.

CITED@hdlab/modern_hopfield_readout.py "RANKING NOTE (load-bearing)" states the same thing for
equal-norm storage: attention-weight ranking == cosine ranking; the only non-trivial object is the
RETRIEVED blend `y = K.T softmax(beta * K q / sqrt(N))`, which re-ranks because it interpolates
neighbouring prototypes toward the query.

**Therefore the sharpening arm is defined as a one-step modern-Hopfield update over the FULL
anchor set, followed by re-scoring.** The pinned 2-candidate softmax is nonetheless RUN, as arm
`S3`, and the cell ASSERTS it is bit-identical to the baseline. A demonstrated trap is cheaper
than a rediscovered one.

CITED@hdlab/multi_hop.py:84-96 -- `beta=None` defaults to `n_dim`, at which the softmax is a Dirac
delta and the "soft" mechanism is a hard argmax; that module records TWO prior cells confounded by
it. This cell does not import `multi_hop`, and reports the ENTROPY of the weight distribution at
every beta rather than assuming any beta softens anything.

## 6. Testbed

`experiments/exp_context_conditioned_near_neighbour_v1.py`, IMPORTED and reused (corpus assets,
split, item construction, anchor-space construction, leak controls L1/L2/L3, `_ctx_masked_multi`).
Nothing is re-implemented; the items and the anchor space are byte-identical to the baseline's.

- 2AFC, chance **0.50 BY CONSTRUCTION** -- the discriminator has range and cannot be floor-pinned.
- MEASURED@data/exp_context_conditioned_near_neighbour_v1/metrics.json: n_items 4000, n_anchors
  2377, n_distinct_target_words 1476, elapsed 243s. Landed A1=0.6395 A2=0.5390 A3=0.4975 A4=0.4800.
- **Live baseline to beat = 0.698**, at d=256 with the graded comparator ON. The landed 0.6395 is
  the PRE-FLIP signed run. **0.69975 is a divisive-normalisation arm that was NEVER SHIPPED**
  (`hdlab/reading_grounding_loop.py:526` defaults `normalise="none"`); **0.7495 is the d=1024 arm,
  also not shipped.** Neither is used as the baseline here. The cell RECOMPUTES the baseline in-run
  rather than quoting it, and reports the recomputed value.

## 7. Arms

Every arm scores the SAME items. All deltas get PAIRED bootstrap CIs.

### 7.1 Primary, 2AFC (chance 0.50)

- `S0_ARGMAX_BASELINE` -- unchanged live read-out: `canonicalize_fast(thresh=-1.0,
  eligible_mask={target, distractor})`.
- `S1_SHARPEN_HOPFIELD[beta]` -- `y = K.T softmax(beta * K q / sqrt(N))` over ALL 2377 anchors via
  `hdlab.modern_hopfield_readout.ModernHopfieldReadout` (WIRED, 10 self-tests), then argmax of
  `cos(y, a_c)` restricted to the two candidates. beta SWEPT, never fixed.
- `S2_SHARPEN_SCRAMBLED_SCORES[beta]` -- **THE CONTROL THAT DECIDES IT.** Identical update, but the
  anchor-score vector is permuted by a fixed deterministic derangement before the softmax. The
  weight distribution is a PERMUTATION of S1's, so its entropy is EXACTLY EQUAL by construction --
  equally sharp, content-blind. If sharpening anything helps equally, the gain is not separation.
- `S3_TWO_CANDIDATE_SOFTMAX[beta]` -- the pinned arm of sec 5; asserted bit-identical to S0.

### 7.2 Secondary and arguably more important: OPEN-VOCABULARY read-out

Same space, same items, all 2377 anchors eligible; correct = the read-out names the masked target.

- `O0_ARGMAX` / `O1_SHARPEN[beta]` / `O2_SHARPEN_SCRAMBLED[beta]` -- as above, unrestricted argmax.
- **SISTER-ERROR CONVERSION -- the finding.** sister(target) := the WordNet LOOSE sibling set
  (`pairs_loose`, 48354 pairs, the predecessor's own criterion). Among items where `O0` was WRONG
  and `O0`'s pick is in sister(target) -> `n_sister_errors`. Of those, how many `O1` gets RIGHT ->
  `n_sister_errors_converted`. Reported for the scrambled control too.
  **Comparison declared in advance: the prior rank-1 common-mode cell converted exactly ZERO.**
  A 2AFC delta WITHOUT sister conversion is a much weaker result and will be reported as such.

### 7.3 SNR diagnostics (no verdict weight, but they adjudicate sec 3.1)

`median_rank_of_target` among all 2377 anchors under the baseline score;
`frac_target_outside_top50`; `frac_items_score_gap_below_1e-3`; mean |gap| for correct vs incorrect.

## 8. MANDATORY FLOORS on every arm

1. **in-cell scramble** -- donor-sentence query (deterministic derangement, disjoint candidates).
   Expected ~0.50 on 2AFC.
2. **frequency baseline** -- pick the corpus-more-frequent candidate. MEASURED 0.4800 at n=4000.
3. **chance** -- 0.50 by construction.
4. **BETWEEN-DRAW sd.** `context_vector`'s projection is a `sha256(word)`-seeded bipolar draw with
   NO salt (hdlab/grounding_acquisition_loop.py:155) -- there is no projection seed to vary without
   forking the live encoder, which would stop the cell measuring the live path. The redraw axis is
   therefore ANCHOR CONSTRUCTION: `R=4` independent profile/eval split seeds, each rebuilding the
   space, giving `between_draw_sd` on S0 and on the best-beta S1 delta. **A gain smaller than the
   variation between draws is not a gain** and is forced to MIDDLE_BAND.

## 9. BANDS -- frozen here, before the run

Let `dS = max_beta(S1[beta]) - S0` (best beta chosen on the PRIMARY, reported with the whole curve,
never as if it were the only beta tried), and `dC = S1[beta*] - S2[beta*]` at that same beta.

- **`HARD_PASS_SHARPENING_SEPARATES_SISTERS`** -- ALL of:
  `dS >= +0.030` and its paired CI excludes 0; `dC >= +0.020` and its paired CI excludes 0;
  `dS > 2 * between_draw_sd`; open-vocab `n_sister_errors_converted / n_sister_errors >= 0.05`
  with the scrambled control converting < 1/3 as many.
- **`SNR_WALL_CLEANUP_RULE_CANNOT_HELP`** (the EXPECTED outcome) -- entropy gate PASSED (sweep
  spans >0.80 and <0.20) AND `|S1[beta] - S0| < 0.020` with CI including 0 at EVERY beta AND
  open-vocab sister conversion <= 0.01. Reading: the constraint is codebook SNR, not the cleanup
  rule; this closes cleanup-rule fixes as a class for this defect.
- **`HARD_FAIL_SHARPENING_IS_CONTENT_BLIND`** -- `dS > 0` but `S2[beta*] - S0 >= dS`.
- **`SWEEP_DID_NOT_SPAN_THE_RANGE`** -- entropy gate failed; no read licensed.
- **`MIDDLE_BAND`** -- anything else, including a real-but-small `dS` that does not clear
  `2 * between_draw_sd`.

META_RULE_L: a HARD_PASS gate cleared by < 5% of its floor -> `MIDDLE_BAND_FLOOR_HUGGING`.

## 10. Instrumentation gates (block the read)

- `SELF_RETRIEVAL >= 0.70` (inherited positive control) -- else `INSTRUMENTATION_SUSPECT`.
- `S0` must reproduce the live read-out: the vectorised baseline must be BIT-IDENTICAL to
  `canonicalize_fast` on a 300-item subsample, else `INSTRUMENTATION_SUSPECT_BASELINE_FORK`.
- `S3` bit-identical to `S0` (sec 5).
- Arms must not be bit-identical to each other (META_RULE_AF), except the declared `S3 == S0`.
- Entropy gate (sec 3.1).
- `content_words` silently drops any token containing a digit; the cell asserts a non-zero query
  norm per item and counts zero-norm queries.

## 11. Engineering

Thread pins before numpy import. Fresh output dir; smoke to a SEPARATE dir. `metrics.json` written
once via tmp + `os.replace`. `sorted(set())`, never `list(set())`. Per-unit checkpoint via
`tools/exp_checkpoint.py`. Deterministic seeding via hashlib only. `except SystemExit: raise`
before `except Exception`. Long runs detached with separate stdout/stderr and a PID.

`hdlab/` is NOT modified by this cell.
