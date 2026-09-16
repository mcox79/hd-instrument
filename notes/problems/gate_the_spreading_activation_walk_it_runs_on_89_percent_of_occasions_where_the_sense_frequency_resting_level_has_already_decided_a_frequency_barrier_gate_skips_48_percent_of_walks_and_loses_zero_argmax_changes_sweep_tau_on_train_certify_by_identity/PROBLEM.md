---
priority: 147
slug: gate_the_spreading_activation_walk_it_runs_on_89_percent_of_occasions_where_the_sense_frequency_resting_level_has_already_decided_a_frequency_barrier_gate_skips_48_percent_of_walks_and_loses_zero_argmax_changes_sweep_tau_on_train_certify_by_identity
status: OPEN
review:
review_text:
---

# PROBLEM: the graph walk that costs 61% of a read is one term beside the verb's sense-frequency resting level, and on 89% of the occasions it runs it cannot change the answer that level already gives; a frequency-barrier gate (skip the walk when log pf1 - log pf2 >= tau) sized at tau=1.0 on the test documents skips 47.9% of walks and loses zero of the 91 argmax changes -- sweep tau on TRAIN, certify by identity (the pri 146 harness), measure the distribution path at its consumer, and time the composition with the pri 146 memo.

**slug:** `gate_the_spreading_activation_walk_it_runs_on_89_percent_of_occasions_where_the_sense_frequency_resting_level_has_already_decided_a_frequency_barrier_gate_skips_48_percent_of_walks_and_loses_zero_argmax_changes_sweep_tau_on_train_certify_by_identity`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Reordered access / the subordinate-bias effect (Duffy, Morris & Rayner 1988; Rayner & Frazier 1989; Binder & Rayner 1998): context is recruited for BALANCED ambiguous words and not for BIASED ones unless it is strong enough to overcome the dominance -- a barrier gate. The COMPUTATION ('spread only when the base rate has not already decided') is PINNED; the THRESHOLD is ours and is swept, never adopted. ACT-R's retrieval has the same shape (a dominant base-level activation resolves without further cues).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no external tool, dataset or model at inference; offline foundation assets admissible at build time only; parameters swept, never adopted.
> **ONE READER = ONE BRAIN (pri 142 P7.2, applied by pri 136/146):** plastic or per-passage state lives on the SituationReader instance; module-level assets are read-only.
> **THE OWNER'S PROGRAM (2026-09-16, consolidate by brain structure):** REUSE BY STRUCTURE before building (list the organs that already compute this, from notes/STRUCTURE_MAP_2026-09-16.md); a second implementation of an existing computation is a defect; the phase-7 probe asks 'did you re-implement an organ that exists?'.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing 'wall', 'ceiling' or 'negative'.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (detect the landed state from the live modules, never with hasattr on something that may exist for another reason).
> **PATCH IN BYTES with each file's own line endings** (the tree mixes LF and CRLF; assert `git diff -w --stat` == `git diff --stat`); never a delete command; never read `data/corpora/holdout/`; cap cores `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; waits are background shell loops.

## 1. THE PROBLEM IN PLAIN LANGUAGE

Deciding which sense of a verb is meant costs 61 per cent of the time the reader spends on a page (pri 142). pri 146 measured, on twelve modern test pages, that the walk overturns the sense the word's own frequency already favours on only one occasion in nine; on the other eight it runs and cannot change the answer. A reader that only spreads activation when the base rates are close (what people measurably do) would skip about half of the walks and change nothing. The walk stays exactly as it is; only WHEN it runs changes. Prove 'changes nothing' by identity, on every document.

## 2. WHY THIS ONE

It is the largest remaining read-time lever after pri 146's memo (36.4% removed): the walk is 61% of a read, the gate removes ~48% of walk invocations, and the memo removes the repeats; how the two compose in SECONDS is unknown and is step 1. The cost of every board and every solver iteration is the program's bottleneck.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED: the subordinate-bias effect (context recruited for balanced, not biased, ambiguous words) -- the gate's computation. OUR-INVENTION: the barrier as log(pf_top1) - log(pf_top2) on the normalised frequency prior; the threshold tau (swept on TRAIN, reported on TEST).

## 4. MEASURED vs INFERRED (pri 146 phase 7, `experiments/exp_ppr_memo_v1.py --consumers --docs 12`, `data/exp_ppr_memo_v1/consumers.json`)

MEASURED on 12 GUM TEST documents (817 sentences, 1,753 events): 844 walks enter the blend `argmax[log P_freq + lam*log PPR]` (`grounded_semantic_graph.py:248`); the walk overturns the frequency argmax on 91 (10.8%; 0-21.6% per document); permuting every walk moves the sense verdict on 25/841 (3.0%), `sense_posterior_in_context`'s argmax on 363/864 (42.0%), the recorded affect field on 5/1,753 (0.29%). The gate sized on the same run: tau=0.5 skips 518 (61.4%) and loses 5 changes; tau=1.0 skips 404 (47.9%) and loses 0; tau=2.0 skips 113 (13.4%) and loses 0; every one of the 91 overturning walks had a barrier below 1.0 nat (5 in [0.5, 1.0)). THESE ARE TEST DOCUMENTS: tau=1.0 is a SIZING, not a fitted parameter.

INFERRED (verify): that the saving in seconds composes with the memo (the join 'skipped by the gate' x 'would have been a memo hit' is unmeasured); that the distribution path's consumer (`harm_help_arithmetic`) is insensitive to the gate (its argmax moves on 42% of calls when the walk is destroyed, so 'the prior already decides' is NOT a sufficient test there -- measure at the consumer).

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 146's memo (per reader; 36.4%) is landed or landing; build on its identity harness (`--identity`), its honest clock (`--timing`), its consumer recorder (`--consumers`); do not re-derive the counts.
- Do not change the walk (damping, 30 iterations, the graph, the blend's lam): the gate changes WHEN, never WHAT.
- A persistent cross-document activation store is REFUTED by measurement (cross-document cue-set repeat rate 0.00%, pri 146 D); do not build it.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `sed -n 240,260p hdlab/grounded_semantic_graph.py; sed -n 405,425p hdlab/grounded_semantic_graph.py` -- `_blend_pick` (the barrier is computable from `prior` alone, BEFORE the walk is requested) and `select_sense_blended` (where the request is made).
2. `sed -n 685,735p hdlab/force_dynamics_valence.py; sed -n 840,900p hdlab/force_dynamics_valence.py` -- the argmax path (`context_sense_sign`), the distribution path (`sense_posterior_in_context`, lam = `affect_lexicon.SENSE_LAM`), and the three gates a sense choice must survive to reach the record (`force_dynamics_event_type`).
3. `notes/problems/sixty_one_percent_of_a_read_*/GATE_THE_WALK_BRIEF.md` and `SOLVED.md` sections 5-7 -- the sizing and its harness.
4. `git log --oneline -3 -- hdlab/grounded_semantic_graph.py` -- whether pri 146's memo has landed (the gate composes with it).

## 7. THE BAR (can-fail; the gate is certified by IDENTITY)

1. **tau swept on TRAIN** (even-index GUM train documents, or the split the harness names), reported on the 12 TEST documents: the chosen tau's skipped share and lost-change count, plus the whole curve.
2. **Lossless on the argmax path, or the loss counted:** with the gate on, the situation model BYTE-IDENTICAL on every document under the pri 146 harness (a fresh reader per document, full-field comparison); any difference reported per event, never averaged.
3. **The distribution path measured at its consumer:** does `harm_help_arithmetic`'s output change with the gate on? (Its input argmax moves on 42% of calls under the destroyed-walk twin; the gate's effect there must be SHOWN, not assumed.) Report alongside pri 148's finding.
4. **The info-free twin:** a gate that skips the SAME number of walks at random must LOSE (expected ~44 of 91 changes lost at 47.9% skipped, 3 seeds) where the real gate loses 0.
5. **The saving, honestly timed** (paired, alternating, one process, stable pairs only, discards named) with the memo OFF and ON: the composition in seconds, and the join count (gate-skipped walks that would have been memo hits).
6. **Nothing about the walk changes**; the product board byte-identical on every model row with the gate on.
7. **Witness** with the pri 128 tier marker pinning the claims (the gate is a barrier test on the prior alone; identity on the stable set; the twin loses).

## 8. FILES AND ENTRY POINTS

- `hdlab/grounded_semantic_graph.py` (`_blend_pick` :248, `select_sense_blended` :414, `_sense_ppr` :218).
- `hdlab/force_dynamics_valence.py` (`sense_posterior_in_context` :688, `context_sense_sign` :718, `force_dynamics_event_type` :844-895).
- `experiments/exp_ppr_memo_v1.py` (the harness: `--consumers`, `--identity`, `--timing`).

Write ONLY: `experiments/exp_walk_gate_v1.py` (NEW cell; `get_output_dir` per Q115; `--self-test`), `verification/test_walk_gate_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, walk_gate_patch.diff}` (unified diffs against `hdlab/grounded_semantic_graph.py` and, if needed, `hdlab/force_dynamics_valence.py`; never edit hdlab/ directly).

## DO NOT QUOTE / DO NOT REDO

- Do not conclude the walk is useless: it is consumed (3.0% of verdicts, 91 real decisions on 12 documents); the finding is that it is asked 89% of the time where it cannot matter.
- Do not quote tau=1.0 as a result; it is a sizing on TEST.
- Do not quote retired figures (`notes/reference_retired_claims_never_requote.md`). 19c corpora are informational only.

*(filed by strategy 2026-09-16 15:22 from pri 146 phase 7; same-day rule for a located root cause.)*
