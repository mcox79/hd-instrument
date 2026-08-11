# Pre-reg: MAVEN-ERE convergence-gated causal v2 -- does the approach CLIMB or PLATEAU?

Filed by: exp_dev. Trigger: Director follow-up on the v1 HARD-PASS -- drive a DECISIVE v2 that
answers ONE question: does the convergence-gate approach CLIMB meaningfully above the honest
order+majority floor, or TOP OUT there? Branch `dataprep/mcguffey-graded-corpus`. Measurement
(not a full 613k run); STOP after this and report.

## Critical baseline reframe (Director, VET-hard)
The honest baseline to beat is NOT the trap-check's 1.62 -- it is the v1 ABLATION arm
(order + majority-positive-label), MEASURED@data/exp_maven_ere_convergence_gated_causal_v1_smoke/
metrics.json:arms.ablation = F1 7.40. The v1 gate added only +4.15 over that (11.55). v2's bar is
beating 7.40 MEANINGFULLY with the gate + added levers load-bearing.

## Prior-work check (SUBSTRATE-KB)
Same top hit as v1 (cosine=0.3916 design_crutch_discriminative_selection_multicue_convergence) --
same mechanism class, different benchmark; that build's discriminator landed MIDDLE_BAND with an
incomplete scramble collapse, carried forward as the reason scramble-collapse stays load-bearing.
No new MAVEN-ERE prior work.

## Measure-first diagnostics (disk-verified this cycle, throwaway probes, not persisted)
On the v1 100-doc dev slice (93,308 pairs, 2,544 gold positives):
- The gate over-fires on NONE: fires on 13,439 NONE vs 1,217 positive pairs -> precision is the
  ceiling (6.78%), not labeling. Of 1,217 gate-covered positives, 993 already get the right label;
  perfect labeling lifts recall only 39.0% -> 47.8% (Lever-2-as-relabel is MODEST).
- Every single cue is weak: connective 3.8%, order 4.6%, window-arg 4.6%, type_compat 6.8%
  precision (base rate 2.7%). A stricter gate (order + >=2 others) lifts precision to 9.1% but
  craters recall to 5.2% -> F1 ~6.6 (WORSE). So a hand-tuned stricter gate is not the answer.
- Lever 1 (entity-continuity via real arc-parse arguments) alone: precision 4.8% ~ the window cue
  (no juice as a standalone cue). BUT same-sentence AND shared-entity = 9.6% precision -- a
  NON-ADDITIVE interaction a flat OR-gate cannot represent.
- Lever 2 (GAM/EBM learned readout, `hdlab.learner.plugins.gam_plugin`, additive log-odds +
  pairwise-interaction terms -- rule b: reuse hdlab/learner, do NOT hand-roll) over the gate-passed
  candidate set, balanced (1:1) training: F1 13.86, P 11.0, R 18.7 -- a real precision-filter climb
  over the gate (11.55). Collapses at 3:1 subsample (fragile operating point; balanced is the a
  priori default, selected dev-blind on a TRAIN held-out split in the real cell, not tuned on dev).

## Two levers (reuse owned organs; READ THE CODE)
1. ENTITY-CONTINUITY cue (Lever 1): per event mention, extract argument-noun lemmas via the OWNED
   glass-box `hdlab.arc_parser.ArcParser` (persisted UD-EWT hashed-perceptron, loaded not
   retrained) + `hdlab.pos_tagger.PosTagger` -- syntactic dependents of the trigger, its nominal
   head, and nominal siblings. Cross-event continuity = shared content lemma. (situation_model_
   accumulate.CausalLinkRegister is the WIRE target for downstream causal-EDGE STORAGE if this
   climbs; for a boolean shared-entity cue the lemma-set overlap is the compute-proportional
   substitute -- the FHRR register would be pure decoration for this contract, scoped out as in v1.)
   Enters BOTH as a gate cue (arm gate_plus_entity) and as a learner feature (full_v2).
2. LEARNED READOUT (Lever 2): the convergence gate proposes a recall-oriented candidate set; a GAM/
   EBM learned readout (`hdlab.learner.plugins.gam_plugin`, glass-box: JSON-inspectable per-feature
   log-odds shape tables + MDL-gated pairwise interactions) decides {NONE, CAUSE, PRECONDITION} per
   gate-passed pair -- learning both the positive/NONE precision filter AND the CAUSE-vs-PRECOND
   label from TRAIN cue-patterns (supervised on TRAIN gold, applied to DEV = train/dev split, NOT
   leak). Trained on gate-passed TRAIN pairs with the NONE class subsampled to a balanced ratio;
   the ratio is selected on a TRAIN held-out split (dev-blind), from {1.0, 1.5, 2.0}.

## Data slice (larger, well-powered, resumable per-unit)
- DEV: first 200 dev docs from valid.jsonl, deterministic sort by doc id (never list(set())/hash()).
- TRAIN: first 600 train docs (learner fit + type-table + baselines), same deterministic sort.
- Per-doc feature-row extraction (the expensive arc-parse step) is checkpointed via
  `tools/exp_checkpoint.py` (unit_key = split+doc_id); a killed run resumes, losing at most the
  in-flight doc. Resume order deterministic.

## Arms (all official positive-only micro-F1, causal task, SAME dev slice)
1. `order_majority_floor` -- order-only gate + connective/majority label (= v1 ablation; the
   baseline to beat, AND the gate-removed ablation control).
2. `gate_only` -- convergence gate (order + >=1 of {connective, window-arg, type}) + connective/
   majority label (v1 real; isolates the gate's lift over the floor).
3. `gate_plus_entity` -- convergence gate with entity-continuity added as a 5th convergence cue +
   connective/majority label (isolates Lever 1 AS A GATE CUE).
4. `gate_learned_noentity` -- gate-passed candidate set + GAM readout, feature set WITHOUT the
   entity cue (isolates Lever 2, the learner, over the hard gate).
5. `full_v2` (= gate_learned_withentity) -- gate-passed candidate set + GAM readout, FULL feature
   set including entity + pairwise interactions (isolates entity's marginal contribution to the
   learner; the headline v2 arm).
6. `scramble` -- full_v2 with a per-doc deterministic non-identity permutation of which mention's
   textual evidence (meta + window-arg + entity) is consulted; gold stays on the real mention
   pairs; the GAM (trained on REAL train features) is fed SCRAMBLED dev features (load-bearing
   control -- MUST collapse).
- Baselines majority / adjacent-sentence / bag-of-event-types recomputed on the SAME slice via the
  existing trap-check functions (imported, not reimplemented), reported alongside.

## Per-lever decomposition (reported explicitly)
- Gate lift = gate_only - floor.
- Lever-1-as-gate-cue lift = gate_plus_entity - gate_only.
- Lever-2 (learner) lift = gate_learned_noentity - gate_only.
- Lever-1-in-learner lift = full_v2 - gate_learned_noentity.

## Falsifiable bands (declared BEFORE the run; floor = order_majority_floor F1 on THIS slice)
- HARD-PASS (approach CLIMBS -> justify continued investment): full_v2 >= 1.8 * floor AND full_v2 >
  gate_only + 1.0 (levers load-bearing beyond the gate) AND scramble_f1 <= 0.5 * full_v2 (scramble
  collapses) AND (31.96 - full_v2) >= 8 (real headroom to SOTA preserved).
- HARD-FAIL / PLATEAU (approach bounded on MAVEN-ERE): full_v2 < 1.3 * floor (no meaningful lift
  above the honest floor) OR full_v2 <= gate_only (levers add nothing over the hard gate) OR
  scramble_f1 > 0.8 * full_v2 (lift not scramble-clean = artifact).
- MIDDLE_BAND (climbs but approaching plateau): between the two -- a real, scramble-clean lift over
  floor and gate, but short of 1.8x floor; honest read = diminishing per-layer returns toward a
  weak-cue ceiling well below SOTA. Report the plateau plainly; a bounded approach is a valid
  finding that sends the keep-climbing-vs-pivot-to-(B) question up to the director.

## Cell-template mandates (applicable subset; single bounded local pass, not GPU/sweep dispatch)
- arms_differ_verified (hash real vs learned vs scramble prediction vectors), final_metrics_
  atomicity: tmp_replace, except SystemExit/KeyboardInterrupt: raise before except Exception,
  crash-diagnostic writes CELL_CRASHED metrics.
- crlb_n/a: official F1 over a fixed real corpus slice; no closed-form noise floor. Feasibility =
  the DEV-measured floor + the diagnostic ceilings above.
- calibration_check: adaptive_with_discriminator_gate -- the GAM subsample ratio + type_compat
  threshold are selected on TRAIN (dev-blind); discriminator-fires check = full_v2 fires >0
  positive predictions on dev, else halt.
- real_code_path_exercised: self-test loads the REAL PosTagger + ArcParser + calls the REAL
  gam_plugin.learn/apply on a tiny synthetic doc set.
- deterministic_seeding: true (scramble + subsample use hashlib/fixed-seed RNG, never Python
  hash()/list(set())).
- no_leak: cue/feature functions take only structural mention-meta + parse-derived args; causal_
  relations is read only by official_gold_labels (eval) and the learner's TRAIN-gold training
  (train/dev split, not dev leak) -- asserted structurally in self-test.
- resumable: per-doc exp_checkpoint caching (cell_chunked in spirit; single-process).
- progress_logging: print_flush_true (arc-parse loop over 800 docs may run minutes; heartbeat lines
  every 25 docs).

## HP_SCOPE
`{full_v2: [climbs_above_floor, levers_load_bearing, scramble_collapses, headroom_survives],
 gate_only: [], gate_plus_entity: [], gate_learned_noentity: [], order_majority_floor: [],
 scramble: []}` -- only full_v2 claims the HARD-PASS gates; the rest are decomposition references
/ controls.

## Compute architecture
(a) sequential-CPU, INLINE-LOCAL, foreground-to-completion (timeout 600000). Justification: pure
Python + a per-sentence structured-perceptron POS-tag + arc-parse (cached once per doc) + a
closed-form GAM fit (no SGD, no torch, no GPU-batchable matmul). Estimated wall time: ~800 docs x
~0.18s parse = ~2.5 min + GAM fit/eval seconds. Compute-proportional: cheapest decisive method for
a go/no-go trajectory question.

## Guardrails
Branch dataprep/mcguffey-graded-corpus, no origin push, targeted commits only (never git add -A).
self-test PASS -> this measurement -> STOP and report. No auto-scale to the full pair space.

## AMENDMENT-1 (2026-08-11, Director maturation drive): FULL-DEV confirmation
Scaled the DEV evaluation from the 200-doc slice to the FULL MAVEN-ERE dev set (710 docs,
613,706 candidate pairs, 13,624 gold positives) with EVERYTHING ELSE IDENTICAL -- same 600-doc
TRAIN fit, same convergence gate, same GAM readout, same dev-blind ratio selection (=1.0), same
official positive-only micro-F1, same floor + scramble + ablation controls. The dev slice is now
parameterized (`--n-dev-docs 710 --anchor ...`); the arc-parse row cache is shared + keyed by
(split, doc_id) so the 600 train + first-200 dev extractions are reused (resumable per-unit). This
turns "F1 15.10 on a 200-doc slice" into a defensible FULL-DEV number.
MEASURED@data/exp_maven_ere_convergence_gated_causal_v2_fulldev/metrics.json (official positive-only
micro-F1, causal task, full 710-doc dev):
  order_majority_floor 5.93 (P 3.10 R 69.75) | gate_only 10.31 (+4.38) |
  gate_plus_entity 10.21 (-0.10, Lever-1 gate cue INERT) |
  gate_learned_noentity 14.86 (+4.55 learner lift) | full_v2 14.78 (P 11.49 R 20.73) |
  scramble 3.48 (collapses, <0.5x full_v2, below floor) | best trap baseline 0.73 | SOTA 31.96.
Verdict HARD-PASS: full_v2 = 2.49x floor, > gate+1, scramble-clean, headroom 17.2 pts.
The ~15.10 HELD at full scale (14.78, -0.32 from the slice = within noise; floor also dropped
7.28->5.93 so the ratio-to-floor rose to 2.49x). Learner is the load-bearing lever; the
entity-continuity lever is INERT at full scale too (-0.10 gate cue / -0.08 learner feature).
