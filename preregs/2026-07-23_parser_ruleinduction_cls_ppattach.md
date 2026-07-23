# Prereg: exp_parser_ruleinduction_cls_ppattach_v1

Filed BEFORE running (bands fixed below; no ex-post thresholds). INLINE-LOCAL FOREGROUND-TO-COMPLETION
per contract (no queue, no remote).

## Hypothesis under test

The 3x null (29441 / 29480 / 29482: a parameter-free similarity-vote TIES the linear
prototype-averaging consolidator on parser-error correction) is a property of the LINEAR LEARNER
CLASS, not the task -- because linear (Hebbian outer-product / centroid-averaging) readouts and
cosine-similarity kNN votes are provably the same function class (nearest-centroid IS a linear
readout; Duda & Hart). FIX = swap in a glass-box NONLINEAR generalizer (explicit IF-THEN feature
CONJUNCTIONS via sequential-covering rule induction + a two-part-code MDL gate, Perfors & Tenenbaum
2009) that can carve regions neither a linear map nor a similarity vote can represent (canonical
example: XOR, CITED Minsky & Papert 1969 -- provably not linearly separable, and not recoverable by
an additive/bundled-similarity vote either, since similarity in that representation is driven by
per-feature overlap, not conjunctions).

## Arms (ONE variable = learner class; features + data + split held constant on the real task)

- ARM_LINEAR: 29480's prototype-averaging Hebbian consolidator (`consolidate_store` /
  `store_predict`, n_cycles=6, replay_frac=0.5) -- REUSED CODE, not reimplemented. Null baseline.
- ARM_SIMVOTE: 29480's parameter-free cosine-similarity k=5 kNN vote (`knn_predict`) -- REUSED
  CODE. The load-bearing bar everything must beat.
- ARM_RULEIND: NEW. Sequential-covering decision-list over explicit feature-VALUE conjunctions
  (size <=2) extracted from the SAME schema/relationally-bound feature set 29480 already uses
  (`instance_feats`: V lemma, N1 lemma, N1 upos, P form, N2 lemma, distance buckets) minus the
  V-lemma feature (excluded from candidate rules: on a verb-disjoint held-out split any V-based
  rule has zero held-out coverage by construction, so it would only waste rule budget -- this
  mirrors why ARM_MEMORIZE structurally floors on this split). MDL gate (two-part code: bits to
  name the rule + bits to encode exceptions, vs bits to encode the covered cluster's label entropy
  under the null/no-rule model) admits a candidate only if it genuinely COMPRESSES; uncovered
  residual cases stay EPISODIC (exact discrete-key lookup only, same floor logic as ARM_MEMORIZE).
  ARM_NORULES (freeze-equivalent must-fail control): identical code path with rule induction
  forced off (max_rules=0) -- forces every case to the episodic-only floor.

## Positive control task (mechanism verification -- NOT a language-capability claim)

Synthetic balanced 4-quadrant task: 2 binary "rule" features a in {0,1}, b in {0,1}; gold label =
XOR(a,b) ("XOR1" iff a!=b else "XOR0"). Each instance additionally carries a "topic" DISTRACTOR
independent of (a,b): every instance shares 4 IDENTICAL topic-tag features with all other
same-topic instances (15 topics total) -- a real-ish surface/lexical-overlap confound, deliberately
a STRONGER raw-feature-overlap magnet than the 2 signal bits (so kNN's nearest neighbors are
topic-mates first, and topic carries zero label information). Same encoding pipeline as the real
task (hashlib-coded dense bipolar signatures, additive bundle, reusing `BASE._feat_code`).
CITED (Minsky & Papert 1969): XOR is not linearly separable -- this defeats ARM_LINEAR regardless
of the topic construction. An earlier construction (independent per-instance noise tags from a
small shared vocabulary) was tuned and REJECTED before this prereg was finalized: it failed to
defeat ARM_SIMVOTE (kNN is itself a universal nonparametric approximator and trivially separates 4
well-clustered quadrants when noise doesn't structurally dominate); the topic-magnet construction
was calibrated via a 3-seed sweep (this is legitimate mechanism/test-construction engineering, not
p-hacking of the real data) to robustly defeat both ARM_LINEAR and ARM_SIMVOTE while ARM_RULEIND
(topic-blind by construction) recovers the label exactly. 70/30 train/test split, 3 seeds (0,1,2),
200 instances/seed (50/quadrant).

## Real test (the actual claim)

Reuses 29480's UD-EWT PP-attachment error harvest VERBATIM (imported, not re-implemented): the
same arc-eager transition parser (trained TRAIN-only), the same out-of-sample DEV+TEST PP-instance
extraction, the same verb-disjoint 60/40 seen/held split, the same 3 seeds (7, 13, 19), same
`frac_seen=0.6`. Only the LEARNER on top of the harvested (signature, gold_class) case pairs
changes across arms.

## Bands (fixed before running)

### Control (mechanism check; explicitly not a substrate-language claim)
- HARD_PASS_CONTROL: ruleind_ctrl_acc >= 0.90 AND (ruleind_ctrl_acc - simvote_ctrl_acc) >= 0.20
  AND (ruleind_ctrl_acc - linear_ctrl_acc) >= 0.20, all 3 seeds.
- HARD_FAIL_CONTROL (rule-inducer itself is broken -- fix before trusting the real arm):
  ruleind_ctrl_acc < 0.75 OR either margin < 0.05.
- MIDDLE_BAND_CONTROL: otherwise.

### Real (headline)
Reuses 29480's own pre-registered beat-margin conventions directly (same lineage, same units:
held-out net_gain = loop_acc - base_acc):
- BEAT_MARGIN_HARD_PASS = 0.05 (absolute net_gain margin)
- BEAT_MARGIN_HARD_FAIL = 0.02
- SCRAMBLE_COLLAPSE_MIN = 0.15 (heldout_fix_rate drop, case<->correction shuffled pre-induction)
- NORULES_FLAT_MAX = 0.02 (freeze-equivalent control: max_rules=0 must leave net_gain ~flat)

- HARD_PASS_REAL: ARM_RULEIND beats ARM_SIMVOTE net_gain by >=0.05 (all seeds) AND beats
  ARM_LINEAR net_gain by >=0.05 (all seeds) AND scramble collapse >= 0.15 AND ARM_NORULES flat
  (|net_gain| <= 0.02) AND all-seed ruleind net_gain > 0 AND leak_clean.
- HARD_FAIL_REAL (honest negative -- task is similarity-shaped for this data, not the learner
  class): ruleind ties or loses to simvote (margin < 0.02) DESPITE control=HARD_PASS (mechanism
  verified capable). Brain-check: PP-attachment resolution is the standard psycholinguistic
  lexical-frequency account (Ratnaparkhi 1994; Whittemore et al. 1990) -- a HARD_FAIL_REAL would
  match a real, documented human bound (exemplar/analogical parsing, Daelemans et al. 1999), not a
  substrate defect.
- MIDDLE_BAND_REAL: otherwise (partial signal; localize which condition failed).

### Overall (combined)
- CONTROL=HARD_FAIL -> `RULEIND_MECHANISM_BROKEN` (do not trust the real-arm comparison; fix the
  inducer first).
- CONTROL=HARD_PASS AND REAL=HARD_PASS -> `HARD_PASS_LEARNER_CLASS_WAS_THE_NULL` (hypothesis
  confirmed: nonlinear rule-induction breaks the 3x null).
- CONTROL=HARD_PASS AND REAL=HARD_FAIL -> `HARD_FAIL_TASK_IS_SIMILARITY_SHAPED` (honest: the null
  was the DATA, not the learner; look elsewhere for beyond-similarity structure).
- otherwise -> `MIDDLE_BAND`.

## Compute architecture
Class (b) sequential-CPU (justified: parser train + PP harvest reused from 29480's own <6min
budget; rule induction over a few hundred SEEN failure cases with candidate search capped to the
top-60 most frequent singles for pairing -- seconds per seed). LOCAL-ONLY, foreground-to-completion;
no queue, no push, no remote-persist, no hdlab mutation, no atom bank (skunkworks VETs).
Deterministic: OMP/MKL/OPENBLAS=1, `np.random.default_rng` fixed int seeds, hashlib feature codes
(no `hash()`-seeded RNG), `sorted(set(...))` splits.

## Cell-template gates declared
- arms_differ_verified: hash test over ARM_LINEAR / ARM_SIMVOTE / ARM_RULEIND predicted-class
  tuples on held-out (real task), at smoke gate.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit / KeyboardInterrupt raised before except Exception (no bare/BaseException).
- cardinality_ok: expected n_seed_rows = len(seeds) for both control (3) and real (3); asserted.
- calibration_check: adaptive_with_discriminator_gate (MDL purity_thresh=0.75 / min_coverage=3
  gate; scramble + norules controls verify fire).
- crlb_n/a: generalization accuracy/net-gain measurement, not a capacity/CRLB-bound cell.
- baseline_in_band: real task reuses 29480's baseline_in_band check (0.05 < base_acc < 0.95);
  control task baseline is exactly-balanced 50/50 by construction (declared n/a, not a ceiling
  check).
- deterministic_seeding: true.
- progress_logging: print_flush_true.

## Smoke profile
Single seed (real: seed=7, dev_cap=900 matching 29480's smoke; control: seed=0, n_per_quadrant=20)
-- must show non-vacuous PP-error harvest (n_fail>0), non-empty rule induction on control
(n_rules>=2), and the discriminator (ruleind vs simvote/linear) computed without exception before
FULL runs.
