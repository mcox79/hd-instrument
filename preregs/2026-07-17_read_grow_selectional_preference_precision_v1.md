# Prereg: read_grow_selectional_preference_precision_v1

**Filed:** 2026-07-17. **Cell:** `experiments/exp_read_grow_selectional_preference_precision_v1.py`.
**Full rationale:** see the cell's own module docstring (this file summarizes the bands/gates for SCHEMA-VET;
the docstring is the load-bearing source, not a restatement to be trusted independently of it).

## Question
Does a glass-box, non-neural verb x argument-CLASS selectional-preference table (WordNet lexnames, PPMI,
learned from TRAIN), used as a post-hoc plausibility gate on the trained transition parser's emitted triples,
raise relation-extraction PRECISION on the held-out UD-EWT slice over (a) the base parser alone and (b) a
meaning-blind surface-frequency control gate?

## Arms
- `BASE_strict_positive_control`: `make_parser_extractor` (74f8de97a) unmodified. Gate-D positive control:
  must reproduce 74f8de97a's own landed numbers at the SAME regime (full: pooled seeds=[7,13,19] n=210,
  precision=0.3472/coverage=0.3095; smoke: seed=7 only, precision=0.28/coverage=0.3286), tolerance 0.02 abs.
- `ARM_SURFACE`: BASE wrapped in a plausibility gate scored by EXACT-MATCH attestation over a surface
  noun-TOKEN table (has this exact verb+object pairing been seen in TRAIN at all?). Meaning-blind control.
- `ARM_SELECTIONAL`: BASE wrapped in the same gate mechanics, scored by add-1-smoothed PPMI over a WordNet
  noun-LEXNAME (argument-class) table. Meaning-conditioned, the actual build.

Both gated arms share IDENTICAL gate mechanics (pass-through on zero TRAIN evidence for the (verb,role)
context; drop if score<=0; keep if score>0) and an IDENTICAL minimum-evidence floor (MIN_CTX_EVIDENCE=3);
they differ in the SCORING FUNCTION -- PPMI is well-behaved over the class table's 27 dense buckets but
pathologically inflates on the surface table's ~4200 sparse per-token keys (CITED@Levy/Goldberg/Dagan 2015),
so the surface arm uses the simpler, more generous exact-match rule instead of PPMI, giving raw frequency its
best chance to succeed before concluding it does not (MEASURED necessity this cycle, not a tuning choice).

## Bands (declared before viewing the FULL outcome; smoke already run for mechanism-fires calibration only)
- `margin_required = max(0.08, 1.5 * sqrt(base_p*(1-base_p)/n_emitted_base))` -- noise-floor-derived, not tuned
  to the observed delta.
- HARD-PASS: `(class_p - base_p) >= margin_required` AND `(class_p - surf_p) >= margin_required` AND
  `arms_differ_verified` AND `positive_control_reproduced` (regime-matched to run_mode) AND `gate_fires`
  (both gated arms: n_eligible>=10, 0.05<=drop_rate<=0.95) AND `class_coverage_sentence_rate >= 0.15`.
- HARD-FAIL: `class_p <= base_p` OR `(class_p - surf_p) < 0.02` OR NOT arms_differ_verified OR NOT gate_fires
  OR `class_coverage_sentence_rate < 0.10`.
- MIDDLE_BAND: otherwise.
- HP_SCOPE: the precision/coverage comparison and gate-fires gates apply to ARM_SELECTIONAL/ARM_SURFACE; BASE
  is scored ONLY as the Gate-D reproduction check.

## Smoke gate status (n=70, seed=7 only; MEASURED this cycle, 3 iterations to reach a clean mechanism-fires
state -- see completion report for full iteration history)
- Iteration 1 (raw add-1 PPMI on both tables): `arms_differ_verified=False` (ARM_SURFACE gate never fired,
  0% drop rate -- vacuous by construction, sparse-token PPMI inflation) + `repro_ok=False` (comparison-regime
  bug: smoke vs pooled-FULL prior mismatch, NOT a real reproduction failure). BLOCKED dispatch, iterated.
- Iteration 2 (added MIN_CTX/MIN_KEY_EVIDENCE=3 floor on PPMI): surface gate still vacuous (0% drop) --
  MEASURED that the floor alone cannot fix PPMI's rare-item inflation at achievable evidence thresholds.
  BLOCKED dispatch, iterated.
- Iteration 3 (ARM_SURFACE switched to exact-match scoring, ARM_SELECTIONAL keeps PPMI): `gate_fires=True`
  (class drop_rate=0.364, surface drop_rate=0.727, both n_eligible=44/44), `arms_differ_verified=True`,
  `repro_ok=True` (base reproduces smoke-regime prior exactly: 0.28/0.3286). CLEARED for FULL dispatch.
  Directional smoke-scale reading (n=70, informative only, NOT the pre-registered discriminator): class_p
  (0.2353) < base_p (0.28) at this small single-seed sample -- HARD_FAIL-shaped at smoke scale, but smoke's
  job here is mechanism-fires verification, not the pre-registered verdict (that is the pooled FULL run).

## Compute / timeout
`--timeout 1200` (measured smoke train_wall_s ~240-390s across runs [likely host-contention variance vs
74f8de97a's own 150-180s]; table build <6s; score <10s; total measured <420s; 1200s retains a real safety
margin). Sequential-CPU, local (run INLINE/foreground -- local_cpu_queue runner intentionally down this
cycle). No GPU/atoms/push/remote-persist. Storage: no_storage.

## Deferred
Error-driven surprisal-scaled update loop (Chang/Dell/Bock; McClosky self-training) -- explicitly gated
behind this cell demonstrating independent signal, per the research note's own sequencing discipline.
