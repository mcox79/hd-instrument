# Pre-registration: exp_c5_fair_goal_owner_primacy_v1

**Anchor:** c5_fair_goal_owner_primacy_v1
**Cell:** experiments/exp_c5_fair_goal_owner_primacy_v1.py
**Bank:** experiments/data/goal_owner_fair_v1.jsonl (62 rows total: the original 42 rows unchanged +
20 NEW rows with `trap_type: "primacy"`, additive)
**Dispatch:** LOCAL-ONLY, in-process foreground, NOT queue-dispatched, no push.
**Cites:** notes/skunkworks_goldvet_fair_goal_owner.md (095d3a876); experiments/exp_c5_fair_goal_owner_v1.py; hdlab/goal_owner_select.py; experiments/exp_component5_gold_role_isolated_v1.py.

## Gating problem (why this cell exists)
Independent Skunkworks gold-VET (notes/skunkworks_goldvet_fair_goal_owner.md) confirmed the v1 fair
bank is a genuine RECENCY trap (28/28) but flagged a residual PRIMACY/SUBJECT confound: on that
bank the goal-holder P is ALWAYS simultaneously the S1 grammatical subject, the first-mentioned
entity, AND the goal-holder, so a trivial primacy/first-mention/subject picker also scores 28/28
(1.0) -- ABOVE the system's 0.6429. The audit's explicit recommendation: add items where P is
NOT first-mentioned / NOT the S1 subject, so primacy and subject baselines fail too. This cell is
that fix.

## Bank design (hand-authored, verified gold, additive)
- N=20 NEW 4-sentence vignettes (`trap_type: "primacy"`): S1 introduces the DISTRACTOR D first
  (D is named, unrelated filler action -- first-mentioned AND S1's subject). S2 introduces P WITH
  the goal (12 explicit-psych-verb / 8 action-implied, reusing the CORE bank's exact vetted goal
  sentences verbatim). S3 names D again (second unrelated filler action -- D's second mention).
  S4 is the outcome clause (reusing the CORE bank's exact vetted outcome sentence verbatim,
  pronoun-only, one polarity trigger).
- By construction: first-mention=D, S1-subject=D, nearest-subject(S3)=D, majority-count=D (2
  mentions vs P's 1) -- all four position heuristics point at the WRONG entity.
- Generation+lexicon-verification script (scratch, not shipped) mechanically checked all 20 new
  rows against the REAL V2_DESIRE / V2_OUTCOME_UNMET / V2_OUTCOME_MET lexicons (reused bit-identical
  from the v1 bank's own verification): 0/20 problems (first pass, disk-verified -- reusing the
  CORE bank's already-vetted S2/S4 sentences verbatim eliminated the lexicon-collision risk class
  that required 8 fixes on the original 42-row bank).

## Mechanism under test (reused verbatim, zero new hdlab code)
Identical organs to v1: GeneralRecencyEntityResolver / ContentMatchResolver / build_positions /
type_sentence_events (experiments/exp_component5_gold_role_isolated_v1.py);
hdlab.goal_owner_select.directed_goal_outcome_score (wired promotion);
hdlab.self_improving_loop.decide_keep_or_revert (wired promotion). NEW in this cell (harness-only,
no new hdlab code): `baseline_first_mention` and `baseline_nearest_subject`, both simple structural
reads over the same `_ordered_tokens` / `GeneralRecencyEntityResolver.subject_entity` primitives v1
already uses.

## Four baselines (all reported, all must be < 0.5 for validity)
(a) recency-to-outcome (whole-passage resolver, outcome slot). (b) first-mention/primacy (earliest
roster entity named in the full passage). (c) nearest-subject (resolved subject of the sentence
immediately preceding the outcome sentence). (d) majority-class (most explicit-name mentions,
earliest-mention tiebreak, structural, never hand-set).

## Metric + scramble control
System accuracy on the FULL 20-item primacy-trap subset (all 20 are genuine four-way traps by
construction, no divergent-subset filtering needed -- every item is discriminating). Scramble
control: role-scramble (GOAL role's owner relabeled to the foil for the content candidate only,
text/gold unchanged; identical non-vacuous-scramble pattern reused from v1) must collapse the
system's gain over the max baseline by >=50% relative, or the instrument does not discriminate.

## PRE-REGISTERED CAN-FAIL (instrument validity, not pipeline quality)
The instrument is VALID iff ALL of:
1. ALL FOUR position baselines (recency, first-mention, nearest-subject, majority) score < 0.5 on
   the primacy-trap subset (ideally 0.0 by construction -- reported, not hardcoded).
2. `n_primacy == 20` and deterministic across 3 seeds (cardinality_ok).
3. `all_four_way_trap == True` (every item independently re-verified in self-test to be a genuine
   four-way trap, not just labeled as one).
4. Scramble collapses the system's primacy-subset gain over the max baseline by >=50% relative (or
   both scrambled/unscrambled are non-vacuously zero, flagged `scramble_vacuous`).

If instrument_valid: report `system_accuracy_primacy` honestly as the REAL goal-binding capability
number -- a low score is an honest finding, not a cell failure. Keep the explicit_psych vs
action_implied decomposition (predict explicit > 0, action_implied ~ 0, mirroring the same
generative-inference gap confirmed on the core recency-trap bank).

## SCHEMA-VET / cell-template fields
- `cell_chunked`: false (single-cell, 3-seed loop, per-seed checkpointed via tools/exp_checkpoint.py).
- `cardinality_ok`: EXPECTED_N_UNITS = 3 seeds; verdict logic raises RuntimeError if `len(per_seed) < 3`.
- `arms_differ_verified`: True (self-test 3/5 asserts baseline != content-match candidate on a
  genuine trap).
- `final_metrics_atomicity`: "tmp_replace" (os.replace pattern, single-shot).
- `crlb_n/a`: "no continuous-noise discriminator; discrete owner-match accuracy over a hand-authored
  bank, not a capacity/CRLB-bound cell."
- `baseline_in_band`: n/a per META_RULE_AG -- all four baselines are DELIBERATELY 0.0 by
  construction (the whole point of this cell); the discriminating signal is the SYSTEM's score.
- `discriminator_reachability`: true (system can score anywhere in [0,1]; the action_implied subset
  structurally caps recovery at explicit-only, an honest ceiling not a saturation artifact).
- `except SystemExit: raise` ordering: present, grep-verified no bare `except:`/`except BaseException`.
- `start_marker_written` / `crash_diagnostic_present`: both present.
- `heartbeat_present`: not applicable -- cell completes in <1s (elapsed_s=0.53s full run, disk-
  verified), well under any hang-detection threshold; per-seed print-progress lines serve the same
  observability purpose at this scale.

## Gold-VET (rule c, triple-check)
See notes/goldvet_fair_goal_owner_primacy_v1.md for the full write-up. Summary: (1) mechanical
lexicon-collision pass (script, 0/20 problems, disk-verified); (2) structural gold-VET re-derived
from the SAME resolvers/baselines the harness scores with (self-test 1/5: all 20 items are genuine
FOUR-WAY traps -- recency, first-mention, nearest-subject, AND majority all land on the foil, not
the owner); (3) mention-count-by-construction (self-test 2/5: foil=2, owner=1 on every item -- the
structural cause of the majority-baseline trap); (4) manual read (all 20 items, this session,
reusing the core bank's already-manually-verified goal/outcome sentence pairs verbatim); (5)
honest-gap confirmation (self-test 4/5: all 8 action_implied items honestly miss GOAL typing,
mirroring the core bank's confirmed gap, not a bug).

## DISK-VERIFIED RESULT (2026-08-05, 3 seeds, deterministic)
`data/exp_c5_fair_goal_owner_primacy_v1/metrics.json`: verdict=INSTRUMENT_VALID_FULLY_FAIR_PRIMACY_TRAP.
recency=0.0, first_mention=0.0, nearest_subject=0.0, majority=0.0 (all four baselines at the floor,
exactly as constructed). system_accuracy_primacy=0.6 (12/20); system_scrambled_accuracy_primacy=0.0
(full collapse, non-vacuous). system_accuracy_explicit=1.0 (12/12); system_accuracy_action_implied=0.0
(0/8) -- the same generative-inference gap confirmed on the core bank, now also confirmed on a bank
where NO position heuristic can win by luck. `beats_every_position_heuristic=True`.
This 0.6 (not 0.6429 -- different N/subset) is the number that survives the audit's caveat: it beats
every one of the four position heuristics on an instrument where none of them can win by
construction, so it is the first honest, fully-fair goal-binding capability number.

## Flagged for independent Skunkworks gold-VET
This bank extension + harness is authored by exp_dev (cell-author role) and mechanically self-VET'd
per the above, but per the task contract it is NOT yet treated as canonical until an independent
Skunkworks (AUDIT-ONLY role) pass confirms the gold + instrument-validity gates from a fresh read,
same as v1.
