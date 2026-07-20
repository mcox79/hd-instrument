# PRE-REG: Confidence-gated codebook consolidation (real-data validation of the reliability-gate CG)

Date: 2026-07-20
Cell: experiments/exp_confidence_gated_codebook_consolidation_v1.py
Anchor: exp_confidence_gated_codebook_consolidation_v1
Author: hdi_exp_dev (Director task hand-off; brain-drill note
  notes/research_brain_confidence_weighted_learning_consolidation_2026-07-20.md)
Queue: LOCAL only. SMOKE runs to completion in foreground. FULL dispatches via
  `local_cpu_queue` (queue_add.sh) -- NOT remote_cpu_queue/overnight_queue, because those queues
  require an `origin/main` push and this task's contract is explicitly "NO origin push,
  NO remote-persist". Deviation note: the standing USER-LOCKED rule
  (`feedback_no_local_smokes_route_all_execution_to_remote_USER_2026-07-11` /
  "SMOKE ONLY on local_cpu_queue") is overridden HERE only because remote is structurally
  unavailable under the no-push contract; runtime is bounded (~10-15 min target) so laptop
  impact is short. Flagged for Director/User visibility in the completion report.
needs_orchestrator_store_sync: True

## WHAT / WHY

Real-data validation of the reliability-gate CG lineage (atom 29376, "independent-channel
reliability gate", which was validated only on an INJECTED-error SYNTHETIC regime; its own
scope bound explicitly states "real-data untested"). This cell asks: does gating a REAL
consolidation step -- the STEP1 codebook build (`exp_learned_codebook_generalization_gate_v1.py`,
atom 29368, text8 PPMI/SVD, held-out word-similarity AUC 0.927) -- by a SELF-GENERATED
(non-injected, non-ground-truth) reliability signal produce a genuine, telemetry-sensitive,
can-fail net benefit on the SAME held-out discriminator that already proved non-construction-
determined for the ungated codebook?

Full design rationale, brain literature (Yu & Dayan 2005 precision-weighting; Kepecs/Lak
confidence-as-byproduct; Lisman & Grace 2005 hippocampal-VTA salience-gated LTP; McClelland-
McNaughton-O'Reilly 1995 CLS salience-weighted replay), and the 6 construction-determinism guards
are in `notes/research_brain_confidence_weighted_learning_consolidation_2026-07-20.md` -- read
that note first; this pre-reg only states the CONCRETE deviations from its suggested design and
the exact bands.

## DEVIATION FROM THE DRILL NOTE'S SUGGESTED SIGNAL (stated explicitly, per honesty discipline)

The drill note recommends reusing atom 29367's S1 (the reader's LCCP learned cue-competition
score) as the self-generated confidence signal, scored per SENTENCE/PASSAGE. This is NOT
mechanically reusable here: S1 requires the LCCP argument-structure reader to run over
syntactically well-formed SENTENCES, but text8 (the corpus STEP1's codebook is built from) has
**no punctuation, capitalization, or sentence boundaries at all** (it is a stripped, lowercased,
concatenated Wikipedia token stream) -- there is no parseable sentence unit for LCCP to score.
Forcing sentence segmentation onto text8 to manufacture an S1 score would itself be a fresh,
untested construction, reintroducing exactly the kind of "derive a fresh proxy" risk the drill
note says this design is meant to AVOID (contrasted against the six failed self-supervised
patient-selection derivations).

Per the task's own CONTRACT (explicit candidate list: "per-observation count / context-consistency
/ PMI-stability / a learned confidence") and its explicit AUTONOMY grant, this cell instead uses a
**corpus-native, per-WORD split-half PPMI-stability signal** -- matching the codebook build's own
natural unit (the codebook assigns ONE vector per vocabulary word, built from that word's PPMI
row; a word-level reliability signal is the correct granularity for this build, not a sentence-
level one). This keeps the SAME mechanism class the brain literature converges on (a genuinely
self-referential test-retest/consistency signal, no ground truth touched, echoing Lisman-Grace's
"novelty computed from the system's own encoding statistics") while being honestly matched to the
actual substrate this cell gates.

## THE SIGNAL (self-generated; never injected; never ground-truth-derived)

For each vocabulary word `w` (vocab built from the FULL token stream, standard `build_vocab`):
1. Split the token stream in HALF by POSITION (first 50% of tokens = half A, second 50% = half B;
   deterministic, no `hash()`/`list(set())` ordering -- fixed slice per PROT-023).
2. Build `cooc_A`, `cooc_B` and `ppmi_A`, `ppmi_B` from each half independently, over the SAME
   fixed vocabulary `w2i` (words absent from a half get an all-zero PPMI row in that half).
3. `confidence(w) = cosine(ppmi_A[w,:], ppmi_B[w,:])` computed via sparse row-wise dot/norm
   (never densifies the V x V matrix). Since PPMI values are non-negative, this cosine is
   naturally in `[0, 1]` -- no separate rescaling needed. A word absent from either half (zero
   row) gets `confidence = 0.0` (no evidence = no reliability claim), by definition, not by tuning.

This is a genuine **test-retest consistency** signal: does this word's distributional signature
replicate across two disjoint slices of the same corpus? It is computed ENTIRELY from corpus
co-occurrence counts -- it never touches wordsim353/simlex999 (the held-out evaluation set) at
any point, and it is computed BEFORE the gated codebook is built (no lookahead).

## GATING MECHANISM (soft, multiplicative, on the PPMI matrix pre-SVD)

`build_codebook_weighted(ppmi, weights, N, seed)`: scale PPMI row `i` by `weights[i]` (sparse
diagonal-matrix product `diag(weights) @ ppmi`), THEN run the identical `TruncatedSVD` step the
STEP1 cell already uses for its `ppmi_svd` arm, THEN L2-normalize rows (identical post-processing
to STEP1). This changes which words' co-occurrence structure dominates the FITTED shared
low-rank subspace (a genuine "consolidation strength" analogy: unreliable words shape the shared
geometry less) while every word still receives a final embedding via projection + renormalization.
Uniform weights (`ones(V)`) are a mathematical no-op relative to STEP1's own `ppmi_svd` arm --
this is the Gate-D positive-control: the `ungated` arm here must reproduce STEP1's original
0.927 AUC (within seed-to-seed tolerance) at the matched regime, or the pipeline has drifted.

## ARMS (ONE variable = the per-word weight vector fed into `build_codebook_weighted`; everything
else -- corpus, vocab, window, N, seeds, TruncatedSVD params, held-out pairs -- is IDENTICAL)

- `ungated`   : weights = 1 for all words (= STEP1's ppmi_svd arm; REAL baseline; Gate-D repro).
- `gated`     : weights = confidence(w) (the genuine, self-generated reliability-weighted arm).
- `shuffled`  : weights = confidence(w) permuted across words with a FIXED seed (31415, via
                `np.random.default_rng(31415).permutation(V)` -- never `hash()`). MUST NOT help
                (destroys the word<->confidence correspondence; if it still helps, the effect is
                generic regularization/shrinkage, not the confidence signal's content).
- `inverted`  : weights = 1 - confidence(w). MUST HURT (deliberately over-trusts the least
                stable/reliable words -- operationalizes the Ackerman-et-al. miscalibration
                failure mode as an explicit adversarial arm; the "can-hurt" probe).
- `oracle`    : weights = a LOWER-ESTIMATION-NOISE ceiling on the SAME construct, NOT a
                ground-truth/gold-label oracle: `min-max-normalized log(1 + word_count)` over the
                full-corpus vocabulary counts already computed by `build_vocab`. Rationale: word
                frequency is a directly-measurable (zero split-sampling-noise) quantity that is
                *expected* to correlate with true distributional-profile reliability (more
                observations = less sampling noise in the co-occurrence estimate), so it serves as
                an idealized, noise-free version of "how much should this word's row be trusted" --
                never touches wordsim/simlex, still 100% self-generated from corpus statistics, but
                cleaner than the 2-way-split proxy used in the real `gated` arm. DIAGNOSTIC ONLY,
                explicitly OUT of HARD_PASS/HARD_FAIL scope (HP_SCOPE below); run at 1 seed only
                (compute-proportionality -- it is not the claim under test).

`HP_SCOPE`: `{"ungated": ["gate_d_repro"], "gated": ["hard_pass_lift", "hard_fail_no_lift"],
"shuffled": ["must_not_help"], "inverted": ["must_hurt"], "oracle": [] }` -- oracle carries NO
HARD_PASS/HARD_FAIL gate; it is reported for context only.

## HELD-OUT METRIC (identical to STEP1; no new eval machinery)

Held-out TRUE-vs-RANDOM AUC (Mann-Whitney U) on wordsim353 + simlex999 top-tercile pairs vs
frequency-matched random re-pairings -- the EXACT discriminator STEP1 already validated as
non-construction-determined (monotone ladder random(0.496) < ri(0.738) < ppmi_rp(0.868) <
ppmi_svd(0.927)). Reused verbatim via import from
`experiments/exp_learned_codebook_generalization_gate_v1.py` (no reimplementation drift):
`load_tokens, build_vocab, build_cooc, build_ppmi, _l2norm_rows, load_wordsim, load_simlex,
cos_pairs, auc_true_vs_random, make_true_random_sets`.

## SIGNIFICANCE TEST (paired bootstrap over held-out pairs, not just seed-count)

Because the baseline (`ungated` ~0.927) is near an operative ceiling, a small but CONSISTENT lift
is the expected win shape (per the drill note). Rather than relying only on 3 seeds for
significance, each seed ALSO gets a paired bootstrap over the held-out TRUE/RANDOM pair indices
(resample pair indices with replacement, recompute AUC for `gated` and `ungated` on the SAME
resampled indices each draw -- a paired design that cancels common held-out sampling noise between
arms) -- `n_boot=2000`, fixed seed per bootstrap call (`20260720 + seed`). Reports mean lift, and
one-sided `p = P(bootstrap_diff <= 0)` (want small for "gated beats ungated").

## PRE-REGISTERED BANDS (before running; NOT tuned to pass)

**HARD_PASS** (checked at FULL, 3 seeds for the 4 core arms):
- `gated` beats `ungated`: mean AUC lift over 3 seeds `>= +0.01` absolute, positive sign in
  ALL 3 seeds, AND per-seed paired-bootstrap `p < 0.05` in `>= 2/3` seeds.
- `shuffled` collapses to ungated: `|mean(auc_shuffled) - mean(auc_ungated)| < 0.01` across seeds
  (no residual "any weighting helps" artifact).
- `inverted` significantly underperforms BOTH ungated and gated: mean AUC deficit vs ungated
  `>= 0.01` absolute, negative sign in ALL 3 seeds, per-seed paired-bootstrap (vs ungated)
  `p < 0.05` in `>= 2/3` seeds.
- Gate-D repro: `ungated` AUC within `0.02` absolute of STEP1's original 0.927 (matched regime).
- Distributional precondition: confidence has genuine spread (`std >= 0.05`, not saturated with
  `>90%` of mass in any single 0.05-wide bin).

**HARD_FAIL** (any one kills the candidate):
- `gated` within noise of `ungated` (no seed-consistent lift `>= 0.01`, or bootstrap doesn't clear
  `p<0.05` in `>=2/3` seeds) -- most likely outcome per the drill note's own deflated P (~0.35).
- `gated` UNDERPERFORMS `ungated` on a real task with no adversarial manipulation (the
  miscalibration failure mode manifesting for real).
- `shuffled` performs comparably to `gated` (`|mean(auc_shuffled) - mean(auc_gated)| < 0.005`) --
  proves any lift is generic regularization, not the confidence signal's content.
- Confidence distribution degenerate (`std < 0.02` or `>95%` mass in one bin) -- kill BEFORE full
  run if caught at smoke; if only visible at full, report as HARD_FAIL_DEGENERATE_SIGNAL.
- Gate-D repro fails (`|ungated - 0.927| > 0.05`) -- pipeline drift, not a real result; investigate
  before trusting any other arm.

**MIDDLE_BAND**: anything else (e.g. right-direction lift that misses the 0.01 margin or the
bootstrap-p bar in only 1/3 seeds; or `inverted` hurts but `shuffled` also drifts).

## DISCRIMINATOR-MUST-SURVIVE-SCALE (Option B+C hybrid)

Baseline is near-ceiling (0.927) at FULL scale, giving LESS separating room than at SMOKE scale
(historical STEP1 smoke baseline ~0.850, more headroom). Smoke here is used as a **preview of
ARM ORDERING** (does `gated` >= `ungated` > `shuffled` >~ `ungated`, `inverted` < `ungated`
directionally), NOT as proof of the exact HARD_PASS margin, which can only be assessed at FULL
given the near-ceiling ungated baseline. If smoke shows the WRONG ordering outright (e.g. gated
clearly worse than ungated by a wide margin, or shuffled clearly beating gated), that is grounds
to re-examine the mechanism before FULL dispatch (per DISCRIMINATOR-MUST-SURVIVE-SCALE discipline)
-- reject-if-saturated does not strictly apply here (baseline isn't saturated at 1.0, it is
near-ceiling by construction of an already-strong prior result) but a wrong-direction smoke result
is still an abort signal.

## COMPUTE ARCHITECTURE

Class (b) sequential-CPU, justified: `TruncatedSVD` (scipy/sklearn randomized solver over sparse
PPMI) has no GPU-batched equivalent in this codebase; this is a Stage-3 foundation-diagnostic
GATE question (compute-proportionality discipline), not a magnitude-of-mechanism claim needing a
heavy training fit -- CPU-sequential SVD fits (measured ~26s/fit at V=10000, k=1024 on synthetic
PPMI-density-matched sparse data) are the cheapest decisive method. FULL regime: 4 core arms x 3
seeds = 12 fits + oracle x 1 seed = 13 fits, plus one full-corpus cooc/PPMI build and one
half-split cooc/PPMI build (2x) -- target wall time ~8-12 min. Timeout set generously
(`1500s = 25 min`) for real-world PPMI density variance vs the synthetic timing probe.

## CELL-TEMPLATE MANDATES (declared; machine-checked at self-test/smoke)

- `cell_chunked`: false (single-shot cell, no per-seed chunking; runtime is short enough that a
  mid-run failure loses one FULL attempt, not hours of work).
- `arms_differ_verified`: true (hash-check across the 5 arm codebooks per seed).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit/KeyboardInterrupt: raise` BEFORE `except Exception` (no bare/BaseException).
- `crlb_n/a`: "distributional-geometry generalization test reusing STEP1's own no-crlb declaration;
  no argmax/capacity noise floor."
- `baseline_in_band`: n/a in the AG sense (there is no failure-arm saturation risk here; the
  `ungated` baseline is EXPECTED near-ceiling by design, that is the STEP1 result being built on --
  the relevant precondition check is the CONFIDENCE DISTRIBUTIONAL SPREAD gate above, not a
  baseline-in-[0.05,0.95]-band gate).
- discriminator survives scale: Option B+C hybrid (see above).
- `HARD_PASS` strictly above floor + 5% band-width: the `>=0.01` lift margin on a metric with
  `[0.927, 1.0]` operative headroom (`~0.073` band) is `~14%` of remaining headroom, comfortably
  above a bare `>=0` floor.
- `HP_SCOPE`: declared above (oracle excluded from HP/HF gates).
- `cardinality_ok`: `EXPECTED_N_UNITS = 4*3 + 1 (oracle, 1 seed) = 13` for FULL;
  `4*3 + 1 = 13` for SMOKE too (matched arm/seed count at reduced corpus scale).
- per-unit failure-class instrumentation: no bare `except`.
- `calibration_check`: `"default_ok_for_this_regime"` -- the confidence signal uses no tunable
  threshold (continuous multiplicative weight); the ONLY registered constant (bootstrap `n_boot`,
  permutation seed `31415`) is fixed before any result is observed.
- all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
- `real_code_path`: self-test constructs REAL `build_cooc`/`build_ppmi`/`build_codebook_weighted`/
  confidence computation at toy scale (V~20, few hundred tokens), not a synthetic-only branch.
- `substrate_signature`: n/a (no KGStore/fit-module call; pure numpy/scipy/sklearn).
- `guard_baseline_valid`: n/a (no control-vs-POP-baseline break-guard in this cell).
- `deterministic_seeding`: true -- all RNG draws use fixed integer seeds
  (`31415` shuffle, `20260720+seed` bootstrap, `TIEBREAK`-style not needed here since AUC uses
  exact Mann-Whitney rank stat with no ties requiring random tiebreak at this pair volume); no
  `hash()`/`list(set())` ordering anywhere.
- `progress_logging`: `print_flush_true` (heartbeat line per arm x seed unit; FULL target wall time
  ~8-12 min, under the mandatory 30-min threshold but heartbeats included regardless per repo norm).

## ROUTE TO VET

Adversarial VET audit targets (stated for Skunkworks): (1) is the confidence signal GENUINELY
self-generated -- never touches wordsim/simlex, never touches gold, computed strictly before the
held-out eval step, verify by code-reading `compute_split_half_confidence` takes no eval-split
argument; (2) does `inverted` genuinely hurt (the can-hurt/telemetry-sensitivity probe) -- verify
the reported deficit is not an artifact of a sign bug that also makes `gated` look good by the same
bug; (3) Gate-D repro of STEP1's 0.927 baseline at matched regime -- verify the `ungated` arm truly
reproduces (not a silently-different pipeline).

Respect `data/orchestrator_paused.flag` before any dispatch. Local/queue only -- NO origin push,
NO remote-persist. Commit locally by path only.
