# PRE-REG: Novel-atom generalization on the REAL text8 PPMI-SVD codebook (v1)

Date: 2026-07-20
Cell: experiments/exp_novel_atom_real_codebook_generalization_v1.py
Anchor: exp_novel_atom_real_codebook_generalization_v1
Author: hdi_exp_dev (Director-authorized revival per atom 29380's named decisive-test criterion)
Queue: LOCAL (run to completion in foreground; ~70-150s wall for the full corpus+SVD+decode pipeline,
measured via pilot -- CPU only)
needs_orchestrator_store_sync: True
local_write_only_no_origin_push_no_remote_persist: True

## WHAT / WHY (the make-or-break revival)

Atom 29380 (exp_novel_atom_generalization_codebook_binding_v1) HARD_PASS'd (codebook_derived=0.776) in a
SYNTHETIC linear-shared-latent world, then a nonlinear-feature-to-code stress test showed the result
collapses to chance (0.036) the moment the generative map is even mildly nonlinear -- the synthetic world's
LINEARITY, not genuine novel-atom generalization, was doing the work. The VET (skunkworks landed-VET,
2026-07-20) demoted the cell to MEASURED_MECHANISM and named the decisive, non-construction-determined
revival test: run the SAME integration (learned feature->code induction + free binding + cleanup) on the
REAL text8 PPMI/SVD codebook (atom 29368, exp_learned_codebook_generalization_gate_v1, held-out relatedness
AUC=0.927), where the feature->code relationship is GENUINELY nonlinear (PPMI's log-ratio transform + a
data-driven SVD eigenrotation of the full VxV PPMI matrix) and cannot be trivially recovered by a linear
ridge fit on a lower-dimensional sketch of the same raw counts. This cell IS that revival test.

## Prior-work check (substrate-KB concept-query, MANDATORY before authoring)
Ran `bash tools/substrate_query.sh "real text8 PPMI SVD codebook held-out word novel atom generalization
binding cleanup composition nonlinear"`. Top-5 hits all concern "Compositional generalization" (skill
composition research notes, FB15k237/WordNet multihop CG audits) at cosine 0.3242-0.3428 -- ADJACENT
(compositional-generalization is the broader family) but NOT the same axis (none concern real-codebook
feature-induction, PPMI-SVD, or the synthetic-vs-real construction-determinism question this cell tests).
Top hit cosine=0.3428 is above the 0.30 threshold, so flagging per protocol, but reading it (notes/research_
BetX_skill_composition_2026-05-21.md "Compositional generalization context") confirms it is a conceptual
skill-composition drill unrelated to this cell's specific mechanism. **Prior-work check: NONE at
cosine>0.30 on the actual axis tested (nearest true match is atom 29380 itself, the cell this directly
revives, and atom 29368, the codebook cell this integrates with -- both already-known, credited, cited
pointers, not a rediscovery).**

## THE WORLD (real, not synthetic)
1. Corpus: text8, n_tokens=8,000,000, vocab_size=10000, window=5, min_count=5 -- IDENTICAL to the codebook
   CG cell's FULL regime (atom 29368) for direct comparability. Reuses that cell's own
   load_tokens/build_vocab/build_cooc/build_ppmi/sparse_ternary_projection/build_codebook functions
   directly (import; same code path as the credited/validated cell, not a reimplementation).
2. TRUE code table: ppmi_svd codebook (N=1024, TruncatedSVD seed=7) -- the "already-structured ground-
   truth space" every atom (seen or held-out) is registered into.
3. HELD-OUT ("novel") words: F_NOVEL=30, vocabulary rank 800-4800 (stride-selected, deterministic, no
   hash()/list(set())), count range measured 160-1013 occurrences in the 8M-token corpus (verified via a
   pilot vocab-frequency probe before finalizing the band -- excludes the top-800 function-word band and
   the very-rare tail, ensuring enough occurrences for multiple independent noisy partial-row draws).
4. SEEN words: V - F_NOVEL = 9970 words. The induction map is fit ONLY on their (feature, true-code) pairs.

## THE FEATURE->CODE MAP (why this dodges the 29380 linear-construction trap)
FEATURE(word) = PPMI-transformed co-occurrence row, projected through a FIXED sparse-ternary random
projection R_feat (V->D_FEAT=256, structurally identical to the codebook cell's own "ppmi_rp" arm). For
SEEN words this uses the FULL corpus row; for HELD-OUT words this uses a PARTIAL, NOISY row built from a
random ~30% subsample of that word's OWN occurrence positions in the token stream (a REAL noisy
observation -- under-sampled usage, not synthetic Gaussian noise). TARGET (true code) = the ppmi_svd
embedding, a DATA-DRIVEN SVD eigenrotation of the FULL V=10000-dim PPMI matrix -- the induction map only
sees a D_FEAT=256-dim random-projection sketch, so exact linear recovery is information-theoretically
precluded (unlike 29380's world, where FEATURE and TARGET were EXACT linear images of an identical shared
latent by explicit construction).

**Pilot-verified (BEFORE finalizing bands, not post-hoc):** even the CHEAT case (ridge applied to the
held-out word's FULL, non-partial feature -- the best case, no held-out-specific noise) caps at mean
cosine-to-true ~0.49 across RIDGE_ALPHA in {0.1, 1, 10, 100} (alpha=10 selected, cos=0.4899, best of the
sweep) -- confirming the map is genuinely imperfect BEFORE any additional real-sampling noise, i.e. NOT
trivially/exactly recoverable. With the REAL partial/noisy feature (the actual eval condition), mean cosine
drops modestly to ~0.42-0.49 across held-out words (smoke-scale pilot) -- a real but bounded generalization
signal, the honest analog of the synthetic cell's calibrated OBS_SIGMA middle band.

## ARMS (ONE variable = how the HELD-OUT word's bound filler code is produced)
- `codebook_derived` [genuine]: ridge induction map W (fit on SEEN (feature,true-code) pairs only,
  alpha=10.0) applied to a FRESH partial/noisy real feature draw of the held-out word.
- `handed_ceiling` [ceiling-only control]: the held-out word's TRUE ppmi_svd code, handed directly.
- `random_code` [true chance/format-only floor]: independent unit-norm random Gaussian vector.
- `memorize_prototype` [naive-similarity baseline]: 1-NN over SEEN words' FULL features (Euclidean) vs the
  held-out word's PARTIAL feature draw; predicts the nearest SEEN word's TRUE code.

## HONEST CALIBRATION DEVIATION FROM THE SYNTHETIC CELL'S TEMPLATE (pilot-discovered BEFORE dispatch)
In atom 29380's synthetic world, held-out atoms were i.i.d. random with NO semantic-neighborhood
structure, so memorize_prototype was structurally guaranteed ~0.000 (a genuine "should-fail" control). A
smoke-scale pilot (V=6000, F_NOVEL=20, 100-candidate table) measured memorize_prototype=0.225 vs
random_code=0.000 -- i.e. on REAL vocabulary, memorize_prototype carries REAL, non-zero signal (a held-out
word's nearest SEEN neighbor by raw-feature similarity is often ALSO close to it in ppmi_svd code-space --
exactly what "words with similar meaning cluster" means). This is reported honestly rather than forced into
the synthetic template's "should collapse to 0" expectation; the ARM is KEPT (per the task contract, which
names "a memorize-prototype / flat should-fail baseline") but its INTERPRETATION is corrected: the
discriminating question becomes "does the REGRESSION-based induction map (using the held-out word's own
real features) add value beyond NAIVE nearest-neighbor prototype matching" -- a sharper, more demanding
version of the make-or-break question than the synthetic cell required. random_code remains the literal
chance/format-only floor and is the arm the contract's "(a) >> chance AND >> random-code (c)" clause binds
to most directly.

## PRE-REGISTERED BANDS (declared from the pilot sweep BEFORE the final calibrated multi-seed run; see
Calibration Sweep Log below for the actual numbers measured before band-freeze)
- **HARD_PASS**: codebook_derived_acc >= 0.20 AND (codebook_derived_acc - random_code_acc) >= 0.15 AND
  (codebook_derived_acc - memorize_prototype_acc) >= 0.05 [genuine induction beats naive similarity] AND
  ceiling_check(mechanics) >= 0.90.
- **HARD_FAIL**: codebook_derived_acc <= 0.05 (collapse toward the random/format floor) OR
  (codebook_derived_acc - random_code_acc) <= 0.03 (no better than a content-free code) OR
  (codebook_derived_acc - memorize_prototype_acc) <= 0.00 (the learned induction map adds NO value over
  trivial nearest-neighbor similarity -- the specific "genuine induction" claim from atom 29380's
  synthetic-world HARD_PASS does not hold on real, nonlinear structure).
- **MIDDLE_BAND**: beats random_code clearly (direction correct, real content survives composition) but
  the margin-over-memorize_prototype clause is neither clearly positive (>=0.05) nor clearly failing
  (<=0.00) -- i.e. genuinely ambiguous whether the regression map adds value.
- Sanity gates (block interpretation if violated): `baseline_in_band` = ceiling_check_mechanics_acc_mean
  (handed-code decode of DISTRACTOR/SEEN in-candidate-table words, through the SAME real-dense-HRR
  bind/bundle/unbind/cleanup pipeline) >= 0.90 -- confirms mechanics work with REAL codebook vectors (not
  assumed from the synthetic FHRR-phasor cell, since this cell uses the HRR real-circular-convolution
  dispatch path, a genuinely different empirical question); `cardinality_ok` = 12/12 units (3 seeds x 4
  arms); `arms_differ_verified` (per-seed pairwise hash-distinct novel-query prediction arrays, exempted
  only for pairs both >0.95 accuracy).
Band-floor (META_RULE_L): CHANCE_FLOOR = 1/150 = 0.00667 (THEORETICAL, F_NOVEL=30 + N_DISTRACTOR=120
candidates); the HARD_PASS codebook target (>=0.20) sits 30x above this floor.

## CALIBRATION SWEEP LOG (MEASURED via pilot scripts BEFORE the cell was written / bands frozen; numbers
tagged MEASURED@<throwaway pilot script, not the production cell -- production cell reproduces the
identical logic and is the officially landed source>)
- Alpha sweep (smoke-scale corpus, V=6000, F_NOVEL=20, cheat/full-feature case): alpha=0.1 -> cos=0.4846;
  alpha=1.0 -> cos=0.4861; alpha=10.0 -> cos=0.4899 [SELECTED]; alpha=100.0 -> cos=0.4338 (over-
  regularized). RIDGE_ALPHA=10.0 fixed before any full-scale run.
- Smoke-scale (V=6000, F_NOVEL=20, 100-candidate table, K_EVAL=20, single eval-seed): ceiling_check=1.000;
  codebook_derived=0.3275; handed_ceiling=1.000; random_code=0.000; memorize_prototype=0.2250 --
  codebook_derived CLEARLY beats memorize_prototype here (+0.1025 margin) -- discriminator fires, mechanics
  sound, proceed to FULL.
- FULL-scale single-seed probe (V=10000, F_NOVEL=30, 150-candidate table, K_EVAL=20): ceiling_check=1.000;
  codebook_derived=0.3050; handed_ceiling=1.000; random_code=0.0150; memorize_prototype=0.3233 --
  MARGIN FLIPS NEGATIVE at full scale (a genuine, not noise-driven, regime difference -- worth the 3-seed
  confirmation below before trusting a single draw).
- FULL-scale 3-seed final (V=10000, F_NOVEL=30, 150-candidate table, K_EVAL=40, seeds=[7,13,19]):
  codebook_derived mean=0.3144 (std=0.0116); handed_ceiling mean=1.0000; random_code mean=0.0042
  (std=0.0031); memorize_prototype mean=0.3431 (std=0.0024). Margin vs random = +0.310 (huge, ~75x chance
  floor -- real content clearly survives composition). Margin vs memorize_prototype = -0.029 (consistently
  negative across all 3 seeds, not noise -- std of the DIFFERENCE is small since both track the same held-
  out-word difficulty structure). **This measured full-scale result is expected to trigger HARD_FAIL via
  the vs-memorize-margin clause** (declared here BEFORE the officially-landed cell run, per META_RULE_AC --
  this is a HYPOTHESIZED-from-pilot number pending MEASURED confirmation from the production cell's own
  landed metrics.json, not itself the landed verdict).

## DISCRIMINATOR-FIRES / SURVIVES-SCALE
Smoke (reduced corpus, V=6000) explicitly showed codebook_derived >> memorize_prototype (a DIFFERENT sign
than the eventual FULL result) -- this is itself informative: the discriminator DOES fire in both
directions across scale (not saturated/vacuous at either regime), and the FULL-scale sign flip is reported
honestly as a genuine regime-dependent finding, not smoothed over. Per DISCRIMINATOR-MUST-SURVIVE-SCALE
Option A, FULL was run directly (cheap, ~150s) rather than trusting the smoke-scale extrapolation.

## SCHEMA-VET fields
- compute_architecture: (b) sequential-CPU with justification -- closed-form ridge (numpy linalg.solve,
  D_FEAT=256, ~9970 SEEN rows, instant), vectorized PPMI-transform + sparse-ternary projection per
  held-out draw (900-1200 draws total, each O(V) -- a few seconds), fully vectorized real-dtype HRR
  bind/bundle/unbind/cleanup per scene batch. Total wall ~150s for the whole pipeline (corpus load + vocab
  + cooc + ppmi + SVD + ridge fit + 3-seed x 4-arm decode); GPU batching would not meaningfully help at
  this scale (dominated by SVD + Python-loop partial-row construction, not matmul).
- storage_strategy: no_storage (single-scene bind-then-query per example; no multi-item chained storage).
- cardinality_ok: EXPECTED_N_UNITS = len(seeds)*len(ARMS) = 3*4 = 12.
- arms_differ_verified: per-seed pairwise SHA256 hash of novel-query prediction arrays across the 4 arms;
  exemption only when a colliding pair is BOTH >0.95 accuracy.
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: "classification-accuracy generalization over C=150 discrete candidates; closed-form chance
  floor = 1/150 = 0.00667 (THEORETICAL), used as discriminator context, not a CRLB."
- discriminator_reachability: True -- pilot-verified codebook_derived spans from ~0.31-0.33 (real regime)
  down toward chance (random_code ~0.004-0.015) and up to 1.0 (handed_ceiling); the memorize_prototype
  comparison is genuinely two-sided (fires positive at smoke-scale, negative at full-scale).
- baseline_in_band: ceiling_check_mechanics_acc_mean >= 0.90; pilot-measured 1.000 at both smoke and full
  scale (real dense-HRR bind/bundle/unbind/cleanup mechanics sound with actual PPMI-SVD codebook vectors,
  not just random Gaussian HRR vectors -- a genuinely new empirical confirmation vs the synthetic FHRR
  cell).
- calibration_check: adaptive_with_discriminator_gate (RIDGE_ALPHA selected via a documented sweep on
  cheat-case cosine-to-true, not tuned to force a PASS on the composition accuracy; the sweep in fact
  precedes and is BLIND to the eventual full-scale memorize_prototype comparison).
- cell_chunked: False (single process, 3-seed sweep internal with per-unit atomic aggregation).
- start_marker_written: True; crash_diagnostic_present: True; heartbeat_present: True (per-stage progress
  prints, flushed).
- defensive_error_checking: passed_all_4_patterns.
- nondeterminism: fixed integer seeds throughout (FEAT_PROJ_SEED/CODE_SEED/ROLE_SEED/DISTRACTOR_SEED module
  constants + per-seed np.random.default_rng(seed) / composite integer seeds e.g. seed*100000+int(i)); NO
  hash()-derived seeds, NO list(set()) ordering (PROT-023 compliant) -- held-out/SEEN split built via
  `[i for i in range(V) if i not in held_set]` (deterministic range iteration, not set-order-dependent).
- progress_logging: print_flush_true (wall time well under 1800s; heartbeat included defensively).

## Positive control / mechanics sanity (Gate D analog)
Self-test exercises: (a) unitary-HRR bind/unbind round trip on a tiny real-dtype vector (cos > 0.99); (b)
the REAL tokenizer/vocab/cooc/ppmi/build_codebook functions at tiny scale (V~15-20 toy corpus, not a
synthetic-only branch -- Gate F.1); (c) the REAL partial-row builder + PPMI-transform + ridge induction
pipeline at tiny scale; (d) decode_scenes with a handed TRUE code on a clean toy world decodes exactly
(100%); (e) ceiling_check helper runs and returns a valid [0,1] accuracy. `ceiling_check` in the FULL/smoke
run is the load-bearing mechanics-sanity gate (>= 0.90 required before any arm's result is interpretable).

## Functional Requirements (Gate E)
1. Register a genuinely novel (held-out) atom into the SAME real, corpus-derived structured code space
   from its OWN partial/noisy real feature observation -- addressed by the ridge induction map (`codebook_
   derived` arm), analog of hippocampal fast-mapping into pre-existing cortical structure.
2. Bind the derived code into a multi-role scene using the FIXED, content-agnostic HRR binding operator --
   addressed by hdlab.binding.bind/unbind (real dtype -> FFT circular convolution) + unitary role codes,
   reused unmodified from the substrate's existing HRR primitive (no new binding mechanism authored).
3. Retrieve/cleanup via similarity to the REAL candidate code table -- addressed by dot-product argmax
   cleanup against the 150-candidate table (30 held-out + 120 SEEN distractors), the same mechanism as the
   codebook cell's own held-out generalization test, now composed through binding rather than tested in
   isolation.
4. Distinguish genuine content-generalization from trivial similarity-matching -- addressed by the
   memorize_prototype comparison (see Honest Calibration Deviation above) and the random_code true-chance
   control.

## Composition edges (Gate C)
- codebook CG cell (PPMI-SVD codebook, real dense vectors) -> this cell's TRUE code table: SHAPE_MATCH
  (identical (V,N) L2-normalized dense real format, same seed/params).
- this cell's derived/handed/random/memorize focal codes -> hdlab.binding.bind (HRR real-dtype path):
  SHAPE_MATCH (all are (N,) or (S,N) float32 dense real vectors; HRR bind dispatches on dtype, verified via
  self-test round trip).
- decode_scenes cleanup -> candidate table cosine/dot argmax: SHAPE_MATCH (both L2-normalized, dot=cosine).

## Reproduce prior chain-grade result as positive control (Gate D)
The codebook CG cell's own held-out generalization AUC=0.927 is NOT re-run here (this cell CITES and
CONSUMES its codebook build functions directly, same code path, same corpus params -- not a
reimplementation subject to invocation-mismatch risk). The mechanics-reproduction control specific to THIS
cell's new axis (composing real dense codes through HRR bind/bundle/unbind/cleanup, which the codebook cell
never tested) is `ceiling_check` -- reproduces a "known-should-work" decode (handed TRUE code, SEEN/
distractor word, same regime) at the SAME (N, R, candidate-table-size) as the main experiment, required
>=0.90 before any arm's result is interpreted.

## Report format
One line: real-derived vs ceiling vs random-code vs chance + derived-code cosine + verdict + next.
