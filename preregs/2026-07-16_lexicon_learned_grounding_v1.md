# Pre-reg: exp_lexicon_learned_grounding_v1

Date: 2026-07-16. Author: exp_dev. Local/CPU. NO queue/GPU/atoms/push.
Cell: `experiments/exp_lexicon_learned_grounding_v1.py`
Research basis: `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md`
  section (b) 3-arm test, section 3 the glass-box multi-cue learner, section (c) Predictions 2 + 3.
Companion: `experiments/exp_lexicon_grounding_loop_v1.py` (ORACLE-identity grounding loop, HARD_PASS) --
  this cell SWAPS the oracle identity map for a LEARNED glass-box lexicon table.
Tolerance-Principle bar: `notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md`.

## Decisive question (fixed by Director)
Can a GLASS-BOX co-occurrence lexicon-learner (cross-situational tracking + softened mutual-exclusivity
+ syntactic-role gating + provisional fast-mapping -- section 3) LEARN correct word-form -> foundation-
concept mappings from a tiny paired curriculum (NO hidden embedding, NO LLM), then feed the LEARNED (not
oracle) word-phasors into the proven FHRR role-filler scaffold to yield a real grounded fact on unbind,
for HELD-OUT novel word-combinations? Isolate the LEARNING RULE from the geometry confound.

## Method
- FOUNDATION (controlled, benign geometry BY CONSTRUCTION so failure is attributable to the LEARNING
  RULE, not the codebook): 12 concepts (8 noun + 4 verb), i.i.d. random FHRR unit-phasor codes. NOT the
  full CoDEx FPE encoding (that concentrates geometry -- a separate encoding problem). Benign asserted:
  participation-ratio > 0.8*min(M,N), coherence_mu < 0.2.
- PAIRED CORPUS: SVO word-triples (subj in 6 animates, verb in 4, obj in 8 nouns; space=192). Train subset
  + DISJOINT held-out (novel COMBINATIONS of KNOWN words). Leak guard (asserted in run_cell): held-out
  triples disjoint from train; every held-out word seen in train.
- LEARNER (glass-box countable table `word -> {concept_id: weight}` + exemplar_count): (1) competitive
  cross-situational alignment (each fact-concept distributes unit mass across explaining words prop. to
  current belief -- normalization = soft ME); (2) syntactic-role gating (ABLATABLE; word slot -> noun/verb
  category restricts candidates); (3) explicit softened ME penalty; (4) provisional fast-map elimination.
- ARMS (4): LEXICON-LEARNED (learner over train -> held-out) / ORACLE-LEXICON (true map, upper bound +
  attribution) / RANDOM (word->fresh random phasor -> cleanup vs foundation = chance) / MEMORIZED-overfit
  (learned table on SEEN combos -- isolates compositional recovery from rote lookup).
- METRIC: (a) held-out word->concept MAPPING accuracy as a CONVERGENCE CURVE vs exemplar budget
  {2,4,8,16,32,64,120}, gating ON vs OFF, against the Tolerance bar (V=12 -> e<=floor(V/lnV)=4 ->
  converged >= 0.667); (b) downstream grounded OBJECT/SUBJECT retrieval on novel combos (unbind role,
  nearest-neighbor vs foundation concept range; chance = 1/8 noun candidates).
- Sweep N in {512,1024,2048}, seeds {1..5}. Sequential-CPU, tiny (<15s wall). Storage: per-sentence
  role-filler bundle, single-hop unbind (no chained composition) -> bundled correct.

## Envelope-fail-bands (set BEFORE full run; from note section b/c)
- HARD-PASS: LEXICON-LEARNED mapping_acc >= Tolerance bar (0.667) within the train budget AND held-out
  grounded OBJECT retrieval within <= 0.10 of ORACLE AND >= 0.30 above RANDOM AND MEMORIZED-seen does not
  inflate held-out (mem_seen - held-out <= 0.10 => genuine compositional, not rote).
- HARD-FAIL: learner does not converge (mapping_acc < 0.50 at full budget), OR converges to systematically
  wrong mappings, OR held-out retrieval indistinguishable from RANDOM (< 0.05 above), OR held-out collapses
  vs memorized-seen (>= 0.20 gap = rote).
- MIDDLE otherwise.
- Prediction 3 (secondary, reported NOT gating verdict): role-gating cuts the exemplar budget to reach the
  Tolerance bar by >= 25% vs no-gating; ALSO report early-regime mean map-accuracy advantage of gating.

## Compute architecture
- Class: (b) sequential-CPU with justification. Cell IS the glass-box learning-rule reference over benign
  codes; tiny (12 concepts, N<=2048, <=120 exemplars, <=5 seeds, gating on/off); wall < 15s. No GPU batch.
- Storage: bundled (per-subject/per-sentence role-filler bundle; single-hop unbind, no multi-hop chain).

## Schema-vet fields
- arms_differ_verified: true (LEARNED vs RANDOM per-query score arrays hash-checked at self-test).
- final_metrics_atomicity: tmp_replace.
- baseline_in_band: true (RANDOM ~0.13-0.20 in (0.05,0.95); ORACLE ~1.0; LEARNED climbs between).
- discriminator survives scale: N in {512,1024,2048}; ORACLE ~1.0, RANDOM chance, gap survives.
- crlb/reachability: cleanup among 8 noun candidates, 3-term superposition crosstalk ~sqrt(3/N) << inter-
  code separation at N>=512 -> ORACLE retrieval reachable ~1.0; RANDOM pinned at 1/8 by construction.
- deterministic_seeding: true (fixed int seeds; sorted() vocab; rng.permutation on seeded generator; no
  hash()/list(set())).
- discriminator-fires: RANDOM must-fail control at chance; empty-corpus learner must NOT converge
  (vacuous-pass guard); convergence curve telemetry-sensitive (more exemplars -> higher map acc, asserted).
- start_marker_written / crash_diagnostic_present / except-SystemExit-ordering: yes.
- progress_logging: n/a (timeout_s << 1800; flush=True line-buffered stdout anyway).

## MEASURED (this cell, FULL) @ data/exp_lexicon_learned_grounding_v1/metrics.json
- verdict = HARD_PASS (run_mode=full, 5 seeds, N in {512,1024,2048}).
- mapping_acc = 1.000 (converges; crosses Tolerance bar at ~8 exemplars, full by ~32).
- held-out OBJECT: LEARNED=1.000 == ORACLE=1.000 (gap 0.000) >> RANDOM~0.13-0.20; MEMORIZED-seen inflation
  = 0.000 (genuine compositional recovery, NOT rote).
- Prediction 3: budget-to-Tolerance-bar gating_on=8 == off=8 (NO >=25% reduction, p3_pass=False), BUT a
  consistent early-regime map-accuracy advantage of gating = +0.092 (0.33/0.55/0.82 vs 0.17/0.43/0.73 at
  budgets 2/4/8). Honest read: gating helps in the low-exemplar regime but both converge by ~16 exemplars,
  so it does not meet the note's HARD >=25% budget-reduction bar in this small-V regime.
