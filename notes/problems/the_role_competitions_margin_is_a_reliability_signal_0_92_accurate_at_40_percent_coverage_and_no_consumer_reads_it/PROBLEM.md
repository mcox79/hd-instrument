---
priority: 106
slug: the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it
status: OPEN
review:
review_text:
---

# PROBLEM: the role competition knows when it is right -- the MARGIN between its top two role activations separates correct from wrong labels at AUC 0.716 (99 in 100 correct at 20% coverage, 92 in 100 at 40%, against a base of 75) -- but every consumer (affected-entity resolver, state register, harm/help reader, the board's agent pick) reads only the hard label string; the brain passes confidence down with the decision

**slug:** `the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it` -- **opened:** 2026-09-13 by strategy from pri 103's round-2 finding (closed 20:10): `coarse_role_posterior` exists and nothing reads it; replacing the label with the posterior at a consumer HURT (-0.020 CI-sep, because the abstention itself carries competence), while the margin as a RELIABILITY signal is clean.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Decisions in the brain travel with their confidence (the balance of evidence; Kiani & Shadlen 2009: certainty read from the same accumulator that makes the choice), and downstream integration weights each input by its reliability (Ernst & Banks 2002; precision-weighted fusion). A consumer that fuses a role label with other evidence (salience, recency, parallelism, a verb's selectional preference) should weight the role by its margin, not treat every label as equally sure. Name the structure and the computation per consumer: fused score = sum_i w_i x cue_i with w_role = f(margin), f a monotone count-calibrated map (the reliability curve pri 103 measured), never a hand-set threshold.
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (`coarse_role_posterior`, `coarse_role_supports`, `net_activation`; pri 103's `agent_competition_pick_conf` pattern), the consumers: `hdlab/affected_entity_resolver.py` (Kehler-Rohde salience x Principle B x parallelism -- a fusion already), `hdlab/copular_binding.py` / the state register, `hdlab/force_dynamics_valence.py` (patient pick), `experiments/exp_board_agent_slot_ud_v1.py` (the board's agent read -- an island today), `experiments/_diag_agent_dimension_live_chain.py`. Pri 103's `posterior_consumer_metrics.json` holds the reliability curve.
> 3. **GENERALIZE.** Every consumer of a role label; also the heads rung's posterior (the same mechanism one rung up; pri 103 measured marginalisation as -0.027 because that posterior is mis-centred -- calibrate, do not marginalise).
> 4. **WALL -> DEEPER.** If weighting does not help a consumer, check whether that consumer's other cues are themselves uncalibrated (fusing a calibrated cue with uncalibrated ones can lose); report per consumer.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the reliability map is counts (margin bins -> accuracy); sweep bin width only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Populations: the affected-entity real-prose probe (standing 0.393) and its gold (`experiments/exp_affected_entity_token_history_gum_v1.py` lineage), the board's who_did_what_patient (0.7944) and agent (island 0.8271; live chain 0.84 tie vs positional 0.84), the state dimension (0.812), the harm/help live gold (24/24); twin = margins shuffled across items; floor = the hard label.
> 7. **ADJACENT.** If the live chain's agent read with margin-weighted fusion beats the positional floor CI-separated, strategy re-points the board's agent dimension at the chain (one structure, no islanded copies) -- report that number explicitly.
> 8. **COMPLETION BAR.** At least one consumer up CI-separated with the margin-weighted fusion (affected entity or patient or the chain's agent read), no consumer down, twin at floor, the reliability map as counts with an observe path -- OR a numbered located negative per consumer.

**(PHASE DIAGRAM.)** Bin width and the fusion weights' prior are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** The margin is only as good as the heads; measure under gold and live heads separately and report the gap.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The organ that decides who did what can tell how sure it is, and when it is sure it is almost always right. Nobody downstream asks. We want the readers that combine this decision with other clues to trust it in proportion to its confidence, the way the brain does.

## 2. WHY THIS ONE
It is a measured, unread signal at the rung under two board abilities, the cheapest kind of gain (no new knowledge, a hand-off repaired), and the standing rule: every rung hands down a graded signal.

## 3. MEASURED vs INFERRED
- **MEASURED (pri 103):** margin AUC 0.716; 0.99 accuracy at 20% coverage, 0.92 at 40%, base 0.755; posterior REPLACING the label at the agent read -0.0204 CI-sep.
- **INFERRED (prove with a number):** margin-weighted fusion lifts at least one consumer CI-separated.

## 4. ALREADY TRIED / DO NOT REDO
Replacing the MAP label with the posterior (REFUTED: the abstention carries competence); marginalising the heads posterior (REFUTED: mis-centred).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/graded_role_assigner.py`, `hdlab/affected_entity_resolver.py`, `notes/problems/the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels/SOLVED.md` (sections 14-16, 19), `experiments/_diag_agent_dimension_live_chain.py`, `notes/BRAIN_MATH_REFERENCE.md` (role and fusion rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_role_margin_weighted_consumers_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/role_margin_consumers_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it), candidate assets under `data/hook_state/` only. Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any supervised parser at inference. Do NOT read gold labels while deciding.
