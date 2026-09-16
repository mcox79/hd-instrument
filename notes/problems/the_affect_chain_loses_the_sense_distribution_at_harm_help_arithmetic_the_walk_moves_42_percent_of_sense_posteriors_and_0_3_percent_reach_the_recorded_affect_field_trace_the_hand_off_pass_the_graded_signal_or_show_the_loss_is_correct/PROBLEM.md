---
priority: 148
slug: the_affect_chain_loses_the_sense_distribution_at_harm_help_arithmetic_the_walk_moves_42_percent_of_sense_posteriors_and_0_3_percent_reach_the_recorded_affect_field_trace_the_hand_off_pass_the_graded_signal_or_show_the_loss_is_correct
status: OPEN
review:
review_text:
---

# PROBLEM: the graded sense distribution the meaning organ hands to the affect chain is almost entirely lost before the record: destroying every walk moves `sense_posterior_in_context`'s argmax on 42.0% of calls (363/864) and the recorded affect field on 0.29% of events (5/1,753), because the sign is used only as an override when the word-level cascade has none and `_assign_affect` reports nothing unless the animacy-axis override fired -- trace the hand-off rung by rung, pass the graded signal where it is lost, or show with the brain's math that the loss is the right decision.

**slug:** `the_affect_chain_loses_the_sense_distribution_at_harm_help_arithmetic_the_walk_moves_42_percent_of_sense_posteriors_and_0_3_percent_reach_the_recorded_affect_field_trace_the_hand_off_pass_the_graded_signal_or_show_the_loss_is_correct`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The brain combines graded evidence with reliability weights (Ernst & Banks 2002) and does not discard a distribution at a boolean gate; a hand-off that keeps only 'did the override fire' is a point estimate where the upstream produced a distribution. The owner's rule: trace the end consumer's signal requirement chain by chain (produced / read / LOST) and repair hand-offs to pass GRADED signal; a downstream regression after a BF upstream is repaired at the consumer, never by reverting the rung.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no external tool, dataset or model at inference; offline foundation assets admissible at build time only; parameters swept, never adopted.
> **ONE READER = ONE BRAIN (pri 142 P7.2, applied by pri 136/146):** plastic or per-passage state lives on the SituationReader instance; module-level assets are read-only.
> **THE OWNER'S PROGRAM (2026-09-16, consolidate by brain structure):** REUSE BY STRUCTURE before building (list the organs that already compute this, from notes/STRUCTURE_MAP_2026-09-16.md); a second implementation of an existing computation is a defect; the phase-7 probe asks 'did you re-implement an organ that exists?'.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing 'wall', 'ceiling' or 'negative'.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (detect the landed state from the live modules, never with hasattr on something that may exist for another reason).
> **PATCH IN BYTES with each file's own line endings** (the tree mixes LF and CRLF; assert `git diff -w --stat` == `git diff --stat`); never a delete command; never read `data/corpora/holdout/`; cap cores `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; waits are background shell loops.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The reader works out, for each event, which sense of the verb is meant and how much it helps or harms whom, as a spread of probabilities. pri 146 found that scrambling that spread completely changes what the next organ receives on nearly half of all events, yet changes what the reader finally records on one event in three hundred. Either the spread is being thrown away at a hand-off where it should count, or discarding it is the right decision and must be shown to be right with the brain's arithmetic. Today nobody knows which.

## 2. WHY THIS ONE

It is a located signal loss on the affect chain (the harm/help and state readings feed the state row and the emotion arm), it is the same class of defect as LOCATED items 11/19/20 (a graded upstream read as a point estimate downstream), and pri 147's gate cannot be certified on the distribution path until this consumer's sensitivity is understood.

## 3. HOW THE BRAIN DOES THIS (frame)

PINNED: reliability-weighted cue combination (Ernst & Banks 2002); the sense competition resolves to a distribution, not a winner (the resting-level + context blend, pri 98/100). OUR-INVENTION: the override rule ordering (word-level cascade first, sense sign only when it has none), the `stage == "event"` reporting gate in `_assign_affect`.

## 4. MEASURED vs INFERRED (pri 146 phase 7A, 12 GUM test docs)

MEASURED: 844 walks; the walk overturns the frequency argmax on 91 (10.8%); every walk permuted -> the (sign, affecting) verdict moves on 25/841 (3.0%), `sense_posterior_in_context`'s argmax on 363/864 (42.0%), the recorded affect field on 5/1,753 (0.29%). Three code facts: the walk is one term beside the SemCor resting level (lam = `affect_lexicon.SENSE_LAM` = 4.0); its sign is used only as an override when the word-level cascade has none (`affecting is False` abstains); `_assign_affect` reports nothing unless the animacy-axis override fired.

INFERRED (verify): that the 42% -> 0.29% collapse is at `harm_help_arithmetic` (the posterior is one term there) and at the `stage == "event"` gate, in that order; that passing the graded posterior to the state/affect record moves the board's state row or the emotion arm (measure both; the emotion arm is pri 138's bar too).

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 98 (Wolff force dynamics), pri 100 (sense-keyed affect norm; `sense_posterior_in_context` is its consumer hook), pri 14 (the result-state arm): read their SOLVED.md before touching the chain; they own the arithmetic.
- Do not re-derive pri 146's counts; reuse `--consumers` and extend it to record the posterior at every rung.

## 6. VERIFY BEFORE YOU START

1. `sed -n 685,735p hdlab/force_dynamics_valence.py; sed -n 840,900p hdlab/force_dynamics_valence.py` -- the two paths and the three gates.
2. `grep -n "harm_help_arithmetic" hdlab/*.py` -- every consumer of the posterior.
3. `grep -n "_assign_affect" hdlab/situation_reader.py` and the `stage == "event"` gate inside it -- the reporting gate.
4. `data/exp_ppr_memo_v1/consumers.json` -- the per-call record.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **The chain traced with counts:** at each rung (the blend -> the posterior -> harm_help_arithmetic -> the event verdict -> the affect record) the number of events whose value moves under the destroyed-walk twin, so the loss is placed at a line.
2. **A decision per rung:** LOST-AND-WRONG (the graded signal should pass: repair as a diff, measure the state row / emotion arm / harm-help gold with CI and twin) or LOST-AND-RIGHT (show with the brain's arithmetic why the distribution must collapse there, with the number it would cost to pass it).
3. **No regression** on the affect gold (pri 14's harm/help 36 items; the state row) at the byte-identity step; the flips named with cause after the repair.
4. **Plastic:** any weight introduced has an observe path; parameters swept.
5. **Witness** pinning the claims.

## 8. FILES AND ENTRY POINTS

- `hdlab/force_dynamics_valence.py`, `hdlab/affect_lexicon.py`, `hdlab/situation_reader.py` (`_assign_affect`), `hdlab/grounded_semantic_graph.py`.
- `experiments/exp_ppr_memo_v1.py --consumers` (the recorder to extend).

Write ONLY: `experiments/exp_affect_chain_signal_v1.py` (NEW cell; `get_output_dir`; `--self-test`), `verification/test_affect_chain_signal_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, affect_chain_patch.diff}`.

## DO NOT QUOTE / DO NOT REDO

- Do not quote the 0.29% as 'the walk does not matter'; quote the rung where the loss happens.
- Do not quote retired figures. 19c corpora informational only.

*(filed by strategy 2026-09-16 15:22 from pri 146 phase 7; same-day rule for a located root cause.)*
