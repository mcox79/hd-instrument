# PRE-REG: c5_generative_goal_typing_action_frame_v1 (2026-08-05)

## WHY
notes/drill_brain_goal_owner_flow.md + notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md diagnosed
goal-typing as LEXICALLY GATED (a psych/desiderative verb -> GOAL) where the brain GENERATIVELY infers a
goal from an action sequence with no goal-word (Trabasso goal-plans; TPJ/dmPFC mentalizing). The fair
instrument `experiments/data/goal_owner_fair_v1.jsonl` (trap_type=="recency", the "core" 28+14 bank in
`exp_c5_fair_goal_owner_v1.py`) contains 10 `verb_type=="action_implied"` core items with NO goal-word;
that cell's own self-test (#5) asserts these ALL miss GOAL typing under the current lexicon typer -- an
honest, pre-existing, documented gap. This cell is the fix-attempt + measurement.

## MECHANISM (glass-box, generative, verb-lemma-independent)
`action_frame_feats(sentence)`: a purely STRUCTURAL (not lemma-keyed) feature extractor over the
action-frame/telos construction -- "X V ... to VP" (a purpose-infinitival clause attached to an
agentive matrix clause). Feature `purpose_to_no_det` fires when the sentence contains a token "to"
immediately followed by a token that is NOT a determiner/possessive (the/a/an/his/her/its/their/this/
that/my/your/our) -- the standard syntactic distinction between an infinitival complement ("to fetch
water") and a prepositional NP complement ("to the well"). This is FRAME-general: it never inspects the
matrix verb's identity, so it generalizes to any verb taking a purpose-infinitive, not a fixed lexicon.
A second feature `has_directional_pp` (toward/into/up/down/out/across/off/along) is a co-occurring cue.

hdlab/learner (config-only MDL plugin registry, the OOV-induction reuse pattern) INDUCES the rule
`purpose_to_no_det -> GOAL` from a hand-authored FIT set (8 positive / 8 negative sentences) via the
`ruleind` plugin (MDL-gated sequential-covering conjunctions, `hdlab/learner/plugins/ruleind_plugin.py`,
itself reused bit-identical) -- the mechanism (frame->goal inference) is EARNED via MDL model-selection
over declared features, not hand-written as an if-statement. FIT-set main verbs {ran, hurried, marched,
sailed, drove, hiked, sprinted, journeyed} are DISJOINT from the TEST bank's action_implied main verbs
{set (out), climbed, carried, walked, rowed} -- held-out generalization, asserted programmatically in
self-test.

WIRE POINT: the induced typer is spliced in by monkeypatching the single name
`exp_component5_gold_role_isolated_v1.type_sentence_events` (the module-global the reused
`build_positions` function calls at runtime) inside a context manager, so `exp_c5_fair_goal_owner_v1.
run_seed` -- and every baseline/scoring/scramble/adoption-gate organ it calls (GeneralRecencyEntityResolver,
ContentMatchResolver, directed_goal_outcome_score, decide_keep_or_revert) -- run BIT-IDENTICAL to the
fair cell, with only the typer swapped. Zero re-implementation of the harness.

## EVAL
Run `exp_c5_fair_goal_owner_v1.run_seed(seed)` for seeds [0,1,2] twice: once with the ORIGINAL
lexicon-only typer (condition=lexical_only, the documented 0/N baseline) and once with the generative
typer patched in (condition=generative). Report, per condition, restricted to `verb_type=="action_implied"`
core rows: N, N_divergent, system_accuracy_divergent. Also report `verb_type=="explicit_psych"` rows
(no-regression check) and the overall recency_floor_divergent (positional-baseline gate) for BOTH
conditions.

## PRE-REGISTERED BANDS
- HARD_PASS: generative condition's action_implied divergent-subset accuracy >= 0.5 (materially above
  the 0/N lexical-only floor), AND explicit_psych divergent-subset accuracy UNCHANGED between conditions
  (no regression), AND recency_floor_divergent stays 0.0 in both conditions (instrument still fair, gate
  reused unchanged), AND the scramble control collapses the generative condition's gain on the
  action_implied divergent subset (>=50% relative collapse, or both scrambled/unscrambled non-vacuously
  0), AND the FIT/TEST verb-disjointness assertion holds.
- PARTIAL/MIDDLE_BAND: action_implied divergent accuracy > 0 but < 0.5, OR scramble does not fully
  collapse (flag, still an honest partial finding), OR no-regression holds but gain is small.
- HARD_FAIL: action_implied divergent accuracy stays 0 (frame->goal inference did not fire or did not
  propagate through ContentMatchResolver's open-goal state), OR explicit_psych items regress, OR
  recency_floor_divergent becomes nonzero (instrument corrupted), OR FIT/TEST verbs overlap (held-out
  claim invalid).

## GUARDS
glass-box; ASCII-only; deterministic given seed; 3 seeds; atomic metrics write; resumable per
(condition, seed) unit via `tools/exp_checkpoint.py`; LOCAL-ONLY, in-process foreground, not
queue-dispatched, no push (per task brief). `cell_chunked`=false (single-process, <10s total, no
per-seed cross-process risk). `progress_logging`="print_flush_true" (n/a, well under 30min).

## Cites
notes/drill_brain_goal_owner_flow.md; notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md;
experiments/exp_c5_fair_goal_owner_v1.py; hdlab/learner/ (registry.py, core.py,
plugins/ruleind_plugin.py); hdlab/goal_owner_select.py; hdlab/self_improving_loop.py.
