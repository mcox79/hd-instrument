# Prereg: exp_situation_model_goal_outcome_dimension_v1 (2026-08-04)

## Claim under test
The discourse-scale grounded-reading wall is a REPRESENTATION GAP (brain drill
`notes/research_discourse_scale_grounded_integration_brain_drill_2026-08-04.md`, adjudicated (c)):
the live situation-model register carries `role_vocab=["agent","mentioned"]` (disk-verified
`tools/read_anne_glassbox_v2_honest_ledger.py:428`) -- NO GOAL / CAUSATION / OUTCOME dimension --
so grounded appraisal reading a LOCAL window has nothing dispersed to integrate and fires ~1.4%
flat on naturalistic goal-block prose.

FIX (reuse-don't-reinvent): extend the situation-model accumulate organ with a GOAL / OUTCOME
dimension set, MIRRORING how `hdlab/situation_model_accumulate.CausalLinkRegister` added
CAUSE/EFFECT meta-roles on the SAME `AccumulateRegister` organ (atom 29609,
bind/bundle/unbind/cleanup, reused bit-identical). As the reader processes a passage
sentence-by-sentence, ACCUMULATE across the discourse, bound to the goal-owner ENTITY: (a) the
GOAL (an animate owner wants X), (b) the ACTION taken against it (withhold/omission), (c) the
OUTCOME (goal MET vs UNMET) -- EVEN when dispersed across non-adjacent sentences. Then the
grounded appraisal (VIEW-2 goal-outcome read, reused bit-identical from
`experiments/exp_self_extension_grounded_realprose_v1.py`) reads goal-blocking OFF the ACCUMULATED
register, not off a local 2-sentence window.

## Brain structures
- GOAL + CAUSATION + OUTCOME dimensions = Zwaan event-indexing (intentionality/causation) over the
  DMN situation model (Zwaan & Radvansky 1998; Lerner 2011 DMN paragraph-scale integration).
- accumulate-bind-unbind organ = hippocampal relational binding (Ranganath & Ritchey 2012 PMAT),
  reused as one substrate across dimension types (mirrors CausalLinkRegister's CAUSE/EFFECT reuse).
- appraisal read = OFC/vmPFC outcome-value appraisal over the represented situation
  (Moors/Scherer/Frijda 2013; Kintsch C-I).
- entity attribution across dispersed sentences = coreference (hippocampal antecedent retrieval);
  the naive recency-shaped resolver is the KNOWN FALSIFIED failure mode (coref recency-trap 0/4,
  MEMORY 2026-08-03) -- explicitly probed by the recency control.

## Design (deterministic, multi-seed, glass-box, contamination-clean)
- TREATMENT: `GoalOutcomeRegister(AccumulateRegister)` -- role_vocab
  ["GOAL","ACTION_AGAINST","OUTCOME_UNMET","OUTCOME_MET"] on the SAME organ (subclass, extends
  role_vocab + adds per-entity role bookkeeping + `appraise(entity)`, mirroring CausalLinkRegister).
  Accumulate all sentences' entity-attributed typed events; `appraise(goal_owner)` decodes each
  written slot (unbind+cleanup) and fires goal_blocked = (GOAL present) AND (net OUTCOME UNMET).
- BASELINE: the EXISTING `view2_goal_outcome` (bit-identical import) applied to each 2-sentence
  LOCAL window; fire = any window fires. Reproduces "reading local windows".
- EVAL: naturalistic goal-block items (mcca_004_amy_warning + theatre_refusal + 4 more implicit
  goal-block passages in FULL discourse context, goal/action/outcome DISPERSED across non-adjacent
  sentences) vs matched non-goal-block controls (goal-MET, outcome-trap noise, physical-harm).
- RECENCY control: separate probe items where the correct outcome-owner is NOT the most recent
  entity (pronoun trap); GOLD-annotated; report whether the appraisal binds the RIGHT event or the
  most-recent (right-event binding accuracy).
- No gold-answer leakage: attribution + appraisal never read the class label. Lexicons/goal-schema
  are proper-noun-free ~6yo supplied KNOWLEDGE (allowed), NOT tuned to individual test items.

## Pre-registered bands (vs the ~1.4% flat naturalistic baseline)
- HARD_PASS (wall cracks): TREATMENT fires on goal-block >=0.5 AND on controls <0.1 (clear
  separation) AND recency binding accuracy >=0.5 (binds the right event, not most-recent) AND
  TREATMENT > BASELINE on goal-block.
- MIDDLE_BAND (routes binding-selector): TREATMENT fires >=0.5 on goal-block, controls <0.1, but
  recency binding accuracy < 0.5 -- the dimensions are tracked but the dispersed goal-outcome
  binding privileges recency (the known coref falsification one level up).
- HARD_FAIL (representation extension insufficient): TREATMENT goal-block fire rate < 0.1 (still
  flat) -- the slots are tracked but appraisal still can't read them; re-open (a)/(b).

## Guards
Glass-box; NO borrowed embedding/LLM/parser as mechanism; AccumulateRegister / normalize_tokens /
view2_goal_outcome / V1_WITHHOLD / V2_* lexicons reused bit-identical; deterministic; multi-seed
(5); resumable per-seed; local-only (no queue/remote/push); ASCII-only. n on real items small
(6 goal-block + 6 control + 3 recency) -- DIRECTIONAL, stated.

Cites: notes/research_discourse_scale_grounded_integration_brain_drill_2026-08-04.md;
hdlab/situation_model_accumulate.py (CausalLinkRegister CAUSE/EFFECT pattern, atom 29609);
experiments/exp_self_extension_grounded_realprose_v1.py (VIEW-2 grounded read).
