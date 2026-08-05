# Pre-registration: exp_c5_fair_goal_owner_v1

**Anchor:** c5_fair_goal_owner_v1
**Cell:** experiments/exp_c5_fair_goal_owner_v1.py
**Bank:** experiments/data/goal_owner_fair_v1.jsonl (42 rows: 28 core trap items + 14 no-distractor twins)
**Dispatch:** LOCAL-ONLY, in-process foreground, NOT queue-dispatched, no push.
**Cites:** notes/testfairness_audit_goal_owner.md (ff6f93a9a); notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md (6df2083db); hdlab/goal_owner_select.py; experiments/exp_component5_gold_role_isolated_v1.py.

## Prior-work check (SUBSTRATE-KB, mandatory)
`bash tools/substrate_query.sh "fair goal owner test recency trap distractor gender matched divergent subset baseline"` -> top cosine=0.2676, all 5 hits below the 0.30 threshold and topically unrelated (process-log chunks). NOT a rediscovery. The task brief's own pointers (testfairness_audit_goal_owner.md, DRILL_SYNTHESIS) were read in full directly, as instructed -- they are the WHY, not a prior implementation of this instrument.

## Gating problem (why this cell exists)
Per the audit: the prior real-text goal-owner numbers (0.64-0.71) measured upstream syntactic-subject resolution, not goal->owner binding. Gold was the miner's own subject-pick (trivial baseline scores ~100% by construction); the Component-5 organ decided ~1 real item across both prior banks (candidate_divergence_rate ~0.0-0.06); outcome_spans were auto-extracted trailing text often about a different character; the task was sentence-local (no maintained goal across a genuine distractor). Nothing about goal-owner is measurable until a fair instrument exists.

## Bank design (hand-authored, verified gold)
- N=28 core 3-sentence vignettes: S1 (protagonist P + goal, 18 explicit-psych-verb / 10 action-implied-no-goal-word), S2 (gender-matched distractor D, unrelated action), S3 (outcome clause, pronoun-only reference to P, one polarity trigger word).
- N=14 no-distractor twins (S2 dropped) for a subset of the core items -- sanity control, system must not regress.
- Gold: owner=P (goal-holder, decoupled from outcome-sentence subject), outcome_polarity (unmet/met). Hand-authored, no auto-extracted spans.
- Generation+lexicon-verification script (scratch, not shipped) mechanically checked all 42 rows against the REAL V2_DESIRE / V2_OUTCOME_UNMET / V2_OUTCOME_MET lexicons (exp_self_extension_grounded_realprose_v1, reused bit-identical) before finalizing: 0/42 problems on the committed bank (initial draft caught 8 lexicon-collision defects, all fixed and re-verified).

## Mechanism under test (reused verbatim, zero new hdlab code)
GeneralRecencyEntityResolver / ContentMatchResolver / build_positions / type_sentence_events (experiments/exp_component5_gold_role_isolated_v1.py) generate the two candidate whole-passage resolutions; hdlab.goal_owner_select.directed_goal_outcome_score (wired promotion) scores each; hdlab.self_improving_loop.decide_keep_or_revert (wired promotion) gates adoption.

## Three baselines (all reported)
- (a) goal-sentence-subject picker (GeneralRecencyEntityResolver on S1 alone) -- construction CEILING, expected ~1.0.
- (b) recency-to-outcome (GeneralRecencyEntityResolver whole-passage, outcome slot) -- the TRAP FLOOR; on the DIVERGENT subset this is 0.0 BY CONSTRUCTION (divergent := recency != gold), reported not hardcoded.
- (c) majority-class (most explicit-name mentions, earliest-mention tiebreak) -- structural, never hand-set.

## Metric + scramble control
Score on the DIVERGENT subset only (N reported explicitly, never averaged into the full bank). Scramble control: role-scramble (GOAL role's owner relabeled to the foil for the content candidate only, text/gold unchanged; the established non-vacuous-scramble pattern from exp_component5_gold_role_isolated_v1) -- must collapse the system's gain over the recency floor or the instrument does not discriminate.

## PRE-REGISTERED CAN-FAIL (instrument validity, not pipeline quality)
The instrument is VALID iff ALL of:
1. `recency_floor_divergent < 0.5` (the trap is real).
2. `ceiling_accuracy >= 0.9` (construction is sane -- P is genuinely S1's subject).
3. `n_divergent >= 10` and deterministic across seeds (cardinality_ok).
4. Scramble collapses the system's divergent-subset gain over recency by >=50% relative (or both scrambled/unscrambled are non-vacuously zero, flagged `scramble_vacuous`).

If instrument_valid: report `pipeline_beats_recency_fair` honestly (system_accuracy_divergent > recency_floor_divergent). A low pipeline score on a valid instrument is an honest finding, not a cell failure -- the PRIMARY deliverable is the valid instrument itself.

## SCHEMA-VET / cell-template fields
- `cell_chunked`: false (single-cell, 3-seed loop, per-seed checkpointed via tools/exp_checkpoint.py).
- `cardinality_ok`: EXPECTED_N_UNITS = 3 seeds; verdict logic raises RuntimeError if `len(per_seed) < 3`.
- `arms_differ_verified`: True (self-test 4/6 asserts baseline != content-match candidate on a genuine trap).
- `final_metrics_atomicity`: "tmp_replace" (os.replace pattern, single-shot).
- `crlb_n/a`: "no continuous-noise discriminator; this is a discrete owner-match accuracy over a hand-authored bank, not a capacity/CRLB-bound cell."
- `baseline_in_band`: n/a per META_RULE_AG (this cell's baselines are DELIBERATELY at 0.0/1.0 by construction -- the "trap floor" and "construction ceiling" are meant to be extreme, not mid-band; the DISCRIMINATING signal is the SYSTEM's divergent-subset score, not the baselines).
- `discriminator_reachability`: true (system can score anywhere in [0,1] on the divergent subset; not saturated by construction since typing_miss items structurally cap explicit-psych-only recovery).
- `except SystemExit: raise` ordering: present, grep-verified no bare `except:`/`except BaseException`.
- `start_marker_written` / `crash_diagnostic_present`: both present.
- `heartbeat_present`: not applicable -- cell completes in <1s (elapsed_s=0.22s full run), well under any hang-detection threshold; per-seed print-progress lines serve the same observability purpose at this scale.

## Gold-VET (rule c, triple-check)
See notes/goldvet_fair_goal_owner_bank_v1.md for the full write-up. Summary: (1) mechanical lexicon-collision pass (script, 0/42 problems); (2) structural gold-VET re-derived from the SAME resolver the harness scores with (self-test 1/6: all 28 core items are genuine traps, naive recency lands on the foil not the owner); (3) leakage guard (self-test 2/6: foil always present, real choice); (4) twin sanity (self-test 3/6: all 14 twins resolve correctly without a distractor); (5) honest gap confirmation (self-test 5/6: all 10 action_implied items honestly miss GOAL typing, not a harness bug).

## Flagged for independent Skunkworks gold-VET
This bank + harness is authored by exp_dev (cell-author role) and mechanically self-VET'd per the above, but per the task contract it is NOT yet treated as canonical until an independent Skunkworks (AUDIT-ONLY role) pass confirms the gold + instrument-validity gates from a fresh read.
