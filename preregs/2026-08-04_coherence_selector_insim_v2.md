# Pre-registration: coherence_selector_insim_v2 (2026-08-04)

## Problem (why v1 failed, VET'd)
`coherence_selector_insim_v1` (preregs/2026-08-04_coherence_selector_insim_v1.md,
data/exp_coherence_selector_insim_v1/metrics.json) landed HARD_FAIL: TRAIN coherence
1.000 but held-out EVAL 0.263 -- BELOW the 0.50 RANDOM floor. Machinery was sound (SR
TD converged 0.0221->0.0186 shrinking; ORACLE 1.0/1.0 on both partitions). ROOT CAUSE
(Director-VET'd): v1's node embeddings were i.i.d. RANDOM BIPOLAR PER ENTITY, wholly
independent of graph structure, and TRAIN/EVAL used DISJOINT node-id ranges with zero
shared representational structure. `M_backward` therefore learned an ENTITY-SPECIFIC
transition association (an identity lookup dressed as a learned map) -- there was
nothing to generalize FROM. This is pure memorization by construction, not a mechanism
failure: causal coherence is RELATIONAL (the true antecedent is the one whose
EFFECT-FEATURES match the outcome, independent of which entities are involved), but v1
computed it over raw entity identity.

## Hypothesis
A backward SR-transport map `M_backward`, trained via the SAME TD(0) delta-rule
(`train_sr_transport`) on REVERSED transitions collected ONLY over a TRAIN partition,
will discriminate a graph-connected TRUE antecedent from a graph-disconnected but
narratively-more-recent DISTRACTOR on HELD-OUT EVAL episodes drawn over NOVEL entities
(never seen during SR training) -- IF entity embeddings are built so that a small
CONTENT-TYPE vocabulary (analogous to action-type / effect-type) RECURS identically
across TRAIN and EVAL, and the causal grammar (which types cause which) is fixed and
shared. This makes coherence a computation over STRUCTURAL/RELATIONAL features that
recur across episodes, not over entity identity, per the task brief's diagnosis and fix.

## Mechanism (reuse, brain-structure-tagged; NO new organ; unchanged from v1 except
representation construction)
- **SR-transport backward map**: `experiments.exp_pfc_gate_cfrpe_trained_v2.
  train_sr_transport` (TD(0) delta-rule), called on REVERSED (effect_idx,
  predecessor_idx) transitions collected by `collect_rollout_transitions` over a
  TRAIN-partition-only reversed adjacency. Brain structure: hippocampal-striatal
  successor representation (Dayan 1993 / Stachenfeld 2017), Foster & Wilson 2006
  reverse replay / Mattar & Daw 2018 need x gain.
- **Scoring**: `reach_value(outcome_E, candidate_E, M_backward)`, reused verbatim.
- **Anti-tautology / NO_REPLAY_LOCAL floor**: `reach_control_targetcos` (M:=identity),
  reused verbatim.
- **Situation-model buffer**: `hdlab.situation_model_accumulate.AccumulateRegister`,
  reused as glass-box sanity (buffer, not scorer) -- unchanged from v1.
- **Abstain-band control-flow**: `hdlab.self_improving_loop.decide_keep_or_revert` /
  `ABSTAIN_BAND_DEFAULT`, reused verbatim over the reach margin.
- **Recency floor**: literal narrative-position comparison, unchanged from v1.

## THE FIX -- what changed vs v1 (representation construction, not the mechanism)
1. **Shared content-type vocabulary** (`N_TYPES=10` bipolar `TYPE_VECTOR`s, generated
   once per seed). Every entity (TRAIN and EVAL, disjoint node-id ranges) independently
   draws a type from this SAME vocabulary -- the type recurs across partitions even
   though no entity does.
2. **Fixed causal grammar**: a random bijection `RULE: type -> type`, generated once
   per seed and used identically in both partitions. A directed CAUSES edge
   `cause -> effect` exists only when `RULE[type(cause)] == type(effect)`.
3. **Entity embedding** = `TYPE_VECTOR[type(entity)]` with a small (5%) per-entity
   bit-flip for individuality, type-dominated by construction.
4. **Distractor construction hardened**: the distractor must have a type that does
   NOT satisfy the grammar relation to the outcome (not merely "wasn't sampled as an
   edge") -- removes an ambiguity where a same-type-but-unsampled node would be a
   structurally-plausible cause yet scored as a "wrong" pick under the strict
   edge-only ground truth.
5. Everything else (SR training procedure, selectors, abstain-gating, floors, oracle,
   multi-seed, glass-box margins) is UNCHANGED from v1.

## One variable
The entity-representation construction (type-structural vs the v1 pure-identity
embedding) and the resulting selector comparison. Graph-generation procedure,
selectors, SR training procedure, seeds, N_DIM all held fixed vs v1 except where the
representation fix requires the type/grammar apparatus described above.

## Arms (floors that MUST fail + the organ under test + positive control)
1. `RECENCY` -- pre-registered to score 0% (distractor always narratively later).
2. `RANDOM` -- pre-registered ~50%.
3. `NO_REPLAY_LOCAL` -- raw cosine, M:=identity -- pre-registered ~50% (true/distractor
   types are DIFFERENT types by the grammar, so raw cosine carries no rule signal).
4. `COHERENCE_REVERSE_REPLAY` (organ under test) -- `reach_value` via `M_backward`,
   abstain-gated (abstain scored as incorrect, conservative).
5. `ORACLE` (positive control) -- must be 100%/100% (train/eval).

## Generalization / compositional test (this is what makes v2 fair AND able to succeed)
`M_backward` is trained ONLY on TRAIN-partition rollout transitions; its TRAIN-partition
entities never overlap EVAL-partition entities (disjoint node-id ranges, asserted on
disk: `train_eval_entity_overlap == 0`). What DOES recur between TRAIN and EVAL is the
type vocabulary and the grammar (`train_eval_type_overlap_frac == 1.0`, asserted). A
result that holds only because entities recur is impossible by construction; a result
that holds is attributable to the grammar/type structure recurring.

## Anti-memorization controls (mandatory, reported honestly regardless of outcome)
1. **Novel-entity EVAL** (primary metric): as above.
2. **Shuffled-structure control**: re-score the SAME EVAL episodes (identical
   true/distractor labels) with EVAL entities' embeddings replaced by i.i.d. RANDOM
   bipolar vectors UNRELATED to type (i.e. v1's exact construction, reproduced in-cell
   as the ablation), `M_backward` held fixed. This destroys the type-recurrence signal;
   coherence accuracy under this control MUST collapse toward chance (pre-registered
   ceiling `<=0.65`) for the mechanism's win to be attributed to structural recurrence
   rather than a spurious cue. `structural_lift = coherence_eval - shuffled_eval` must
   be `>=0.15`.
3. **Recurring-entity exclusion**: `train_eval_entity_overlap == 0` asserted every
   seed (structural, not probabilistic) -- rules out "it only works when the entity
   recurs" as an alternative explanation for a pass.

## Multi-seed
5 seeds (7, 17, 23, 31, 41); each seed independently redraws type vocabulary, grammar,
embeddings, edges, episodes.

## Pre-registered PASS/FAIL bands (EVAL partition, mean over seeds)
- **HARD-PASS**: ORACLE positive control (train+eval >=0.999) AND
  `train_eval_entity_overlap==0` construction-clean AND `COHERENCE_REVERSE_REPLAY`
  EVAL accuracy (conservative) `>=0.75` AND beats RECENCY/RANDOM/NO_REPLAY_LOCAL each
  by `>=0.15` absolute AND glass-box margin positive in every seed AND shuffled-
  structure control `<=0.65` with `structural_lift>=0.15`.
- **MIDDLE-BAND**: beats floors on novel-entity EVAL but misses one HARD-PASS
  sub-gate (accuracy floor, lift margin, or the shuffled-structure attribution check)
  -- read as right-mechanism-class/underpowered, not a refutation.
- **HARD-FAIL**: does not beat RECENCY and RANDOM and NO_REPLAY_LOCAL on novel-entity
  EVAL, OR glass-box margin not consistently positive. Per brain-faithful-losing =
  presumed-impl-bug-first: inspect `sr_diag.err_first` vs `err_last` before any
  structural conclusion.
- **GATE_FAILED_ANTI_MEMORIZATION_CONSTRUCTION**: entity/type overlap assertions fail
  -- the test itself is mis-constructed, no verdict trustable.

## Secondary (reported, does NOT gate verdict)
Transfer-probe on the Director-verified real-text `multi_candidate_causal_attribution`
items, time-boxed; if unavailable/incompatible in the time-box, reported honestly as
NOT RUN.

## Guards
`torch.Generator` / `np.random.default_rng` per-seed sub-seeding; `sorted(set())`
iteration where applicable; no `hash()`-seed; resumable per-seed via
`experiments._seed_checkpoint`; atomic store writes (`os.replace`); glass-box (every
scalar traceable to `reach_value` / `reach_control_targetcos` / graph ground truth /
type-grammar ground truth); no borrowed embedding/LLM/parser as the mechanism.

## Honest scope caveats (stated before running)
- The sim (type-vocabulary + fixed grammar + bipolar codebook) is a NAMED SUBSTITUTE
  for experienced causal episodes with recurring content structure -- single-hop
  CAUSES edges gated by a single type-to-type rule is a simplification of real
  narrative causal chains (which may be multi-hop, conjunctive, or involve richer
  feature bundles than one scalar "type"). A win here licenses "the mechanism-class
  generalizes when causal structure is represented via RECURRING content features
  rather than entity identity," not "narrative causal attribution at large is solved."
- `N_TYPES=10` is a modest vocabulary size chosen for a clean, well-powered signal at
  `V_TRAIN=V_EVAL=260` (~26 entities/type); this is a favorable-but-not-degenerate
  regime, not a stress test of vocabulary scale.
- n=5 seeds is a within-cell multi-seed stability check, not a large-N study.
