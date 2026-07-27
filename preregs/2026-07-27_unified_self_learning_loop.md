# Pre-registration: unified_self_learning_loop_v1

Anchor: `unified_self_learning_loop_v1`
Cell: `experiments/exp_unified_self_learning_loop_v1.py`
Date: 2026-07-27
Author: exp_dev (hdi_exp_dev)
Status: SMOKE=PASS (tiny fresh encoder); FULL pending v2 checkpoint.

## Question (WHAT)
Does wiring the TRAINED scale-encoder (comprehension engine) into the CLS reader loop let the
substrate genuinely LEARN FROM REAL PROSE across cycles -- read (encoder) -> flag-unknowns
(clarify_gate) -> condense/fast-write -> SLEEP-consolidate into a working copy of the foundation --
and IMPROVE its foundation knowledge CONSISTENTLY, with sleep firing every cycle, retention held,
and controls flat? This ends the "ingestion bypasses the reader" gap (architecture correction 2026-07-27).

## Design (brain-faithful CLS loop; reuse, no reinvention)
Imports `experiments.exp_scale_meaning_learn_arc_heldout_v2` (V2) for ALL data-prep (universe/split/
postings/adjacency/grounding), the encoder (TinyTransformer + BPE tokenizer + mlm_train), and the
VET-confirmed leak-proof `relational_eval` probe. Adds ONLY the loop / hippocampal buffer / MDL-gated
sleep / clarify prioritization / controls / curve.

- READ: `TinyTransformer.pooled` (mean-pooled contextual rep) comprehends REAL ARC mention-sentences
  of held-out foundation concepts (cskg_foundation_v1 nodes). NOT templated.
- FLAG: `hdlab/clarify_gate.py` ClarifyGate flags under-known concepts (low accumulated-evidence /
  low rep-coherence confidence). Flag population SHRINKS across cycles.
- CONDENSE + FAST-WRITE: per-concept running-mean rep condenses many mentions; cycle reps append to a
  per-concept episodic buffer (hippocampal fast store).
- SLEEP: `hdlab/learner` (core.per_cluster_gate, MDL two-part code) consolidates the buffer into a
  WORKING COPY of the foundation concept-rep store -- commits only coherent + sufficiently-attested
  evidence, else KEEP_EPISODIC. SLEEP MUST FIRE every cycle (asserted + logged); fixes cycle2's
  sleep=False bug (the #1 bug).
- PROBE (leak-proof): `V2.relational_eval` ranks a held concept's TRUE foundation-neighbour vs
  degree-matched non-neighbours by CONSOLIDATED-rep cosine. Rep has ZERO relational input; predicted
  edge disjoint from read text => genuine generalization. Train-neighbour reps are a FIXED base
  (encoded once); held reps are loop-updated.

Controls (each a full loop variant sharing the cycle-0 init store = foundation-before-loop):
  MAIN read+sleep | NO_READ (frozen) | SCRAMBLED (word-shuffled prose + sleep) | READ_NO_SLEEP (episodic-only).

## Compute architecture
Storage strategy: SHARDED (per-concept rep store; each concept its own vector). NO bundled composition.
Class: (c) mixed. Encoder forward = batched matmul (GPU at FULL); loop/consolidation = light CPU.
SMOKE ran CPU foreground-to-completion. FULL loads the v2 GPU checkpoint -> recommend overnight_queue (GPU).

## Bands (envelope-fail-bands)
### SMOKE (tiny fresh encoder; validates the LOOP MECHANISM only)
Discriminator that MUST fire on a tiny encoder = REAL>SCRAMBLED comprehension (encoder path carries
meaning, not surface bag-of-words). The across-cycle GAIN is DEFERRED to FULL (a 0.53M/250-step
encoder is below the mention-averaging signal threshold; V2 proved the text-rep carries relational
signal only at scale -- MEASURED@data/exp_scale_meaning_learn_arc_heldout_v2 text-alone rel > grounding).
- SMOKE_MECHANISM_PASS iff: loop runs end-to-end (4 arms x n_cycles) AND sleep fires every cycle
  (n_consolidated>=1) AND relational power (n_query>=15) AND clarify fired (flag>=1) AND NO_READ frozen
  AND comprehension_fires (MAIN AUC > SCRAMBLED AUC at cycle-0 AND final).
- gain_on_tiny_encoder reported, NOT gated (expected False/negative on tiny).

### FULL (v2 checkpoint = comprehension engine) -- the real HARD-PASS
- HARD_PASS iff: knowledge_gain_main = AUC[final]-AUC[0] > +0.02 (real-prose knowledge gain) AND
  sleep fires every cycle AND controls_below_main (MAIN[final] > each control[final]) AND retention_ok
  (MAIN AUC never drops below AUC[0]-0.02; no catastrophic forgetting) AND monotone_ish (<=1 dip) AND
  power (n_query>=40) AND comprehension_fires.
- MIDDLE_BAND: gain > 0 but misses a secondary gate (monotonicity / margin / a control).
- HARD_FAIL: gain <= 0 (accumulating real prose does not improve the foundation at scale) -> the
  loop mechanism runs but reading does not consolidate knowledge; route to mechanism iteration
  (coherence-filtered / precision-weighted consolidation instead of plain running mean).

## MEASURED (smoke, tiny fresh encoder)
- verdict: SMOKE_MECHANISM_PASS
  MEASURED@data/exp_unified_self_learning_loop_v1_smoke/metrics.json:verdict
- comprehension_gap_cycle0 = +0.0696 ; comprehension_gap_final = +0.0455 (comprehension_fires=True)
- sleep_fired_every_cycle = True ; n_query_final = 73 ; n_held_concepts = 250
- clarify flag_population_curve = [250,250,0,0] (shrinks) ; NO_READ flat = True
- main_curve = [0.5772, 0.5444, 0.5474, 0.544] ; knowledge_gain_main = -0.0332 (gain_on_tiny=False, deferred)
- controls final: NO_READ 0.5772, SCRAMBLED 0.4985, READ_NO_SLEEP 0.5772

## SCHEMA-VET fields
- final_metrics_atomicity: tmp_replace (os.replace)
- arms_differ_verified: True (held-rep store fingerprints); arms_differ_exempted: [(NO_READ, READ_NO_SLEEP)]
  rationale: both freeze the consolidated store at cycle-0 by construction (distinct mechanism, identical
  committed store -- sleep-off => reading changes nothing; THAT identity is the finding).
- cardinality_ok: n/a (fixed 4 arms x n_cycles; no seed/param sweep axis). cell_chunked: False (single seed).
- start_marker_written: True ; crash_diagnostic_present: True ; heartbeat_present: True
- defensive_error_checking: passed_all_4_patterns
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except)
- deterministic_seeding: True (fixed ints + np.random.default_rng(seed+...) ; no hash()/list(set()) ordering)
- discriminator_reachability: True (comprehension gap +0.069 measured at smoke; well above 0)
- baseline_in_band: True (AUC 0.49-0.59, not saturated, not floor)
- crlb_n/a: relational AUC has no closed-form noise floor for this regime; power gated via n_query.
- calibration_check: default_ok_for_this_regime (ClarifyGate banked M1.8 thresholds; MDL min_compression_ratio=1.0 per Perfors-Tenenbaum)
- real_code_path_exercised: [TinyTransformer, _encode_sentences, _concept_learn_result+per_cluster_gate,
  ClarifyGate, _sleep_consolidate, V2.relational_eval, _build_encoder_from_ckpt] (all in self_test at N~tiny; ckpt round-trip reproduces saved reps)
- substrate_signature_checked: V2.TinyTransformer + relational_eval bound via real calls in self_test
- progress_logging: print_flush_true
- HP_SCOPE: {MAIN_read_sleep: [gain, comprehension, retention, monotone]; controls: [comprehension only, expected below main]}

## Invariants
TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX (symbolic gate + running-mean +
MDL model-selection; no external LLM / no autograd at inference); LEAK-PROOF (predicted edge disjoint
from read text); REAL prose (ARC corpus, not templated). Store LOCAL-ONLY + UNCOMMITTED; NO canonical bank; NO push.

## FULL invocation (Director runs once v2 ckpt lands)
```
.venv/Scripts/python.exe experiments/exp_unified_self_learning_loop_v1.py --full \
  --ckpt data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt --seed 7
```
Metrics -> data/exp_unified_self_learning_loop_v1/metrics.json
Recommend GPU (overnight_queue) -- encoding ~800 held x 96 mentions + base ~all-concepts through the
d=512/6-layer encoder is matmul-heavy; CPU-tractable but slow.
