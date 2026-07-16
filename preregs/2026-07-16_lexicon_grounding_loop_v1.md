# Pre-reg: exp_lexicon_grounding_loop_v1 (smallest grounding-loop on the REAL CoDEx foundation)

Filed: 2026-07-16 by hdi_exp_dev. Cell: `experiments/exp_lexicon_grounding_loop_v1.py`.
Source design: `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md`
section (b)/(c); Director steer DELTA 1 (anchor to CoDEx, 4 arms + negatives) and DELTA 2
(`notes/research_grounding_vsa_unbind_geometry_derisk_2026-07-16.md`: geometry de-risk).

## Question
Does the proven glass-box VSA role-filler scaffold, filled with the REAL CoDEx foundation's OWN
concept vectors, YIELD an actual foundation fact on unbind AND reject fabricated claims
(non-vacuous grounding)? First concrete join of language STRUCTURE with foundation CONTENT, verified
against the real external graph (train/valid/test rows) + real pre-built negatives (non-circular).

## Foundation (real, on disk)
`data/codex_claimvalidity/raw/` -- CoDEx Wikidata subset. Q-id entities, P-id relations. Restricted
to 3 clean transitive-verb-like relations: P27 (is-citizen-of, 1.31 obj/subj), P1412 (speaks, 1.38),
P106 (has-occupation, 7.31 -- multi-valued, handled by the any-true-object metric). No entity2text/
relation2text label files on disk -> Q-ids/P-ids are glass-box-legal; human-readable labels DEFERRED.
Foundation size (measured): 1620 entities, 3 relations, 14812 known facts (train+valid+test),
1490 held-out positives, 1862 real negatives.

## Mechanism (glass-box; MEASURED-clean)
Each Q-id/P-id gets a fixed random FHRR unit-phasor code (the substrate's native KG-node code
assignment; NOT a proxy). Foundation memory F[s] = superposition over known (s,r,o) of
bind(v_rel[r], v_ent[o]) -- relation-keyed role-filler binding (RELATION as role, OBJECT as filler,
SUBJECT as the queried bundle). Retrieve: unbind F[s] by v_rel[r] + nearest-neighbor cleanup over the
relation's object-range; validate: resonance Re<F[s], bind(v_rel[r],v_ent[o])>/N.

## Arms (4 + baseline, per DELTA 1)
- BOUND-REAL (= ORACLE-LEXICON, identity Q-id->code): held-out valid+test positives.
- RANDOM (control/negative): ungrounded random relation key -> unbind off-manifold -> chance.
- MEMORIZED (overfit control): same grounded memory, train-seen positives (fidelity ceiling ref).
- SCRAMBLE / MUST-FAIL: real *_negatives.txt; must be rejected >=90% (vacuousness gate).
- baseline: most-common-object-per-relation (frequency baseline).

## HARD-PASS / HARD-FAIL bands (from research note (b)/(c) + DELTA 1; NOT loosened)
HARD-PASS (all of): BOUND-REAL held-out any-true-object retrieval - modal-object baseline >= 0.20;
  |BOUND-REAL - MEMORIZED| <= 0.10; negatives rejected >= 0.90 at 90% positive recall; AUC(pos,neg)
  >= 0.55 (>0.05 above chance); BOUND-REAL - RANDOM >= 0.05.
HARD-FAIL (any of): BOUND-REAL - RANDOM < 0.05; AUC <= 0.55 OR neg-rejection < 0.50 (vacuous);
  MEMORIZED - BOUND-REAL >= 0.20 (rote lookup, not recall).
MIDDLE otherwise.

### DEVIATION FLAG (honest scope; bars NOT loosened)
With raw random-phasor codes the loop RECALLS + VALIDATES real facts and REJECTS real negatives on the
external graph. It is NOT a link-prediction/generalization test (random codes have no similarity
structure to generalize over -- separate later question needing learned/structured codes). "Held-out"
here = fidelity-uniformity across the real graph + non-vacuousness on real external negatives. The
BOUND-REAL=MEMORIZED=1.0 outcome is therefore a CONSTRUCTION-clean recall result, not a capability win
over a learned baseline; the genuinely informative teeth are (a) RANDOM collapses to chance -> grounding
is load-bearing, (b) real negatives rejected non-vacuously. Flagged so no downstream over-read frames
this as link-prediction. exact-match retrieval (~0.26) is reported alongside any-true-object (multi-valued
P106 conflation) for full transparency.

## Geometry de-risk (DELTA 2)
BOUND-REAL uses fresh random phasors = ORACLE-LEXICON (identity), so any unbind failure is
GEOMETRY/BINDING, not a lexicon rule. Emitted 3 pre-flight diagnostics on the codebook: coherence
excess over the Welch floor, participation-ratio/effective-rank, degree-similarity Spearman. Added a
STRESSED-geometry isolation arm: an adverse codebook (low effective-rank + degree-hubness,
unit-modulus-legal) run through the SAME oracle-lexicon loop. Attribution: >=15pt BOUND-REAL drop +
diagnostic elevated -> GEOMETRY_IS_BOTTLENECK; <=5pt -> GEOMETRY_NOT_BOTTLENECK. Fix lever if it bites:
sparse-expansion pattern-separator (NOT whitening -- whitening HARD_FAILed on a sibling mechanism here).
No fitted additive_map X exists on disk -> stressed codebook is a SYNTHETIC stand-in; the real-vector
probe (load fitted X, lift k=24 -> N unit-phasors) is the flagged next step, hook left one lever away.

## Compute architecture
Class (b) sequential-CPU with justification: tiny (dim<=4096, ~1620 entities, ~15k stored facts,
<=5 seeds); cell IS the glass-box FHRR reference-primitive validation over the real graph (bit-exact
CPU); full wall ~4.5min (dominated by N=4096 Gram eigendecomposition for the diagnostics). Local numpy,
no queue/GPU/atoms/push (like exp_nativelang_svo_vsa_probe_v1). Storage: F[s] bundles a subject's facts
= the tested single-hop associative-memory mechanism (no chained/multi-hop composition); bundled correct.

## SCHEMA-VET fields
- arms_differ_verified: true (per-query score-array hash-test at smoke gate; POS vs NEG arrays differ).
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
- except-ordering: SystemExit/KeyboardInterrupt re-raised before except Exception (no BaseException/bare).
- crlb / discriminator_reachability: THEORETICAL -- resonance positive self-term = 1.0, negative
  crosstalk ~ sqrt(deg/N); separable at N>=512; HARD-PASS thresholds reachable. discriminator_reachable: true.
- baseline_in_band: true -- modal baseline ~0.51, RANDOM ~chance (0.04-0.12), both in (0.05,0.95);
  BOUND-REAL mechanism saturates at 1.0 but the RANDOM control + negatives gate provide the
  discriminating band (grounded 1.0 vs random chance; 100% reject vs vacuous 0%).
- discriminator_survives_scale: true -- N sweep {512,1024,2048,4096}; RANDOM stays chance, gap survives.
- multi_seed_gate: 5 seeds full / 3 smoke; AUC reported per-seed; reject if mean AUC within 0.05 of 0.5.
- deterministic_seeding: true -- fixed int seeds; sorted() vocab ordering; no hash()/list(set()).
- start_marker_written / crash_diagnostic_present: true. heartbeat: N/A (cell wall < 15min).
- calibration_check: default_ok_for_this_regime (FHRR primitives bit-exact; random-phasor geometry
  benign per emitted diagnostics -- participation_ratio ~min(M,N), degree-corr ~0).

## Cardinality
EXPECTED_N_UNITS = n_seeds x n_N = 5 x 4 = 20 (full). cardinality_ok reported via sweep length.

## Dispatch
Local numpy cell; run inline to completion (foreground, ~4.5min) -> actual verdict, NOT a queue handoff
(COMPLETE-OR-HANDOFF satisfied). Commit locally. No atomize / no origin push (held for user auth).
