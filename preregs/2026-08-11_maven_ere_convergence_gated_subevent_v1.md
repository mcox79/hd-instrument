# Pre-reg: MAVEN-ERE convergence-gated SUBEVENT relation task (breadth drive) -- does the mechanism transfer?

Filed by: exp_dev. Trigger: Director breadth drive -- extend the banked causal glass-box win
(F1 14.78 full-dev, 933773243) to a SECOND relation type on the same corpus. Branch
dataprep/mcguffey-graded-corpus. Measurement; STOP after and report. Honest test of transfer, not a
forced win.

## Task
SUBEVENT = binary (SUBEVENT vs no-relation), ~99.4% NONE (even more skewed than causal). One event
is a temporal/structural PART of another (part-whole containment/granularity), NOT causal
connection. Official positive-only micro-F1 via the maven_ere_official_eval port (which ALREADY
scores subevent: REL2ID["subevent"]={"NONE":0,"subevent":1}; official_gold_labels(doc,"subevent")
verified). SOTA (ProtoEM 2023) ~29.73 F1.

## Measure-first diagnostics (disk-verified this cycle, throwaway probes, not persisted)
On train-600 (reusing the shared arc-parse cache):
- Subevent structure DIFFERS from causal: same-sentence only 11.6%, 41.6% of positives are
  long-range (sent-dist >= 5), arg-overlap weak (12.6%), arg-subsumption useless (1.7%). The
  DOMINANT signal is event-type granularity -- coarse container parent types (Hostile_encounter/
  Competition/Catastrophe/Social_event/Military_operation) -> finer child types (Attack/Motion/
  Conquering); 683 concentrated type-pairs among positives.
- forward-order (parent e1 before child e2) = 69.7% of positives.
- Feasibility probe (dev-200): FLOOR (order-only + always-SUBEVENT) F1 3.17; BAG-OF-EVENT-TYPES
  (majority-vote per type-pair) F1 0.0 (base rate 0.6% -> every type-pair majority is NONE, so the
  win is NOT a trivial type-lookup -- the honest confound check clears); GATE F1 5.88; GAM learned
  readout F1 14.49 (ratio 1.0) / 15.85 (ratio 2.0) / 12.57 (ratio 3.0). Mechanism appears to
  transfer; ratio 2.0 optimal here (unlike causal's 1.0 -- selected dev-blind in the real cell).

## Cues (subevent-appropriate; NEVER read subevent_relations)
- order: parent-before-child forward order (necessary gate cue).
- type_compat: TRAIN subevent positive-rate for the ordered (type_A, type_B) pair > 1.5x the TRAIN
  global rate (min support 3).
- arg_overlap: shared content-lemma between the two events' arc-parse argument sets (OWNED
  hdlab.arc_parser + hdlab.pos_tagger; the shared cache's ent sets).
- proximity: sentence distance <= 2.
- learner-only features: same-sentence, adjacent, sent-dist bucket, type-pair rate bucket, parent-
  granularity bucket of type_A, the raw event types tA/tB, window-arg overlap.
GATE (recall proposer) = order AND (type_compat OR arg_overlap OR proximity).

## Arms (official positive-only micro-F1, subevent, dev set; per-arm, NOT aggregated)
1. `order_only_floor` -- order-only + always-SUBEVENT (= honest baseline to beat AND ablation).
2. `gate_only` -- convergence gate + always-SUBEVENT (gate lift over floor).
3. `gate_learned_noarg` -- GAM readout, features WITHOUT arg-overlap/window (learner lift over gate).
4. `full_v2` -- GAM readout, full features incl arg-overlap (headline; arg's marginal contribution).
5. `scramble` -- full_v2 with per-doc non-identity permutation of which mention's evidence (meta +
   ent + win, incl. event TYPE) is consulted; gold on real pairs; GAM trained on REAL train fed
   SCRAMBLED dev features (load-bearing control -- MUST collapse).
Reference baselines: majority (all-NONE -> 0.0 by the metric's structure), bag-of-event-types
majority (the type-lookup confound check).

## Learner
GAM/EBM (hdlab.learner.plugins.gam_plugin; rule-b reuse of hdlab/learner, glass-box additive
log-odds + MDL pairwise interactions), binary {NONE, SUBEVENT}, trained on gate-passed TRAIN pairs
with NONE subsampled to a ratio selected on a TRAIN 80/20 held-out split (dev-blind) from {1,2,3}.

## Data slice
TRAIN 600 docs, DEV full 710 docs (defensible sibling to the causal full-dev number). Reuses the
SHARED arc-parse cache (data/exp_maven_ere_convergence_gated_causal_v2_smoke/_rowcache; ent/win/
mention_meta are task-agnostic; keyed by split+doc_id); no re-parse needed.

## Falsifiable bands (declared BEFORE the run; floor = order_only_floor F1 on THIS slice)
- HARD-PASS (mechanism TRANSFERS): full_v2 >= 1.8 * floor AND full_v2 > gate + 1.0 (learner load-
  bearing) AND scramble_f1 <= 0.5 * full_v2 (collapses) AND (29.73 - full_v2) >= 8 (headroom).
- HARD-FAIL (does NOT transfer): full_v2 < 1.3 * floor OR full_v2 <= gate OR scramble > 0.8 * full_v2.
  A clean negative is a valid result -- subevent's part-whole structure may not suit convergence-
  gating; report plainly.
- MIDDLE_BAND: between -- partial transfer.

## Cell-template mandates (applicable subset)
arms_differ_verified (hash floor/gate/learned/scramble preds), tmp_replace atomic write, except
SystemExit/KeyboardInterrupt before except Exception + crash diagnostic, crlb_n/a (F1 over fixed
corpus slice), calibration_check=adaptive_with_discriminator_gate (ratio dev-blind; full_v2 fires
>0), real_code_path (self-test loads real PosTagger+ArcParser via v2.entity_sets + calls real
gam_plugin), deterministic_seeding (hashlib scramble + fixed subsample seed), no_leak (cue/feature
fns take only structural + parse args; subevent_relations only in official_gold_labels + TRAIN-gold
training), resumable (shared cache reuse).

## HP_SCOPE
`{full_v2: [transfers_climbs, learner_load_bearing, scramble_collapses, headroom_survives],
 others: []}`.

## Compute architecture
(a) sequential-CPU, INLINE-LOCAL, foreground-to-completion (timeout 600000). Arc-parse reused from
the shared cache (no re-parse); cost is Python feature-building over ~1.3M pairs + a closed-form GAM
fit (no SGD/torch/GPU). Est. wall ~2-4 min.

## Guardrails
Branch dataprep/mcguffey-graded-corpus, no origin push, targeted commits only (never git add -A).
self-test PASS -> this measurement -> STOP + report.
