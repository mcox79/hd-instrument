---
priority: 96
slug: far_coordination_needs_the_meaning_channel_the_distant_parallel_conjunct_is_a_co_argument_not_a_position
status: OPEN
review:
review_text:
---

# PROBLEM: a quarter of all coordination links span nine or more words and the governor gets essentially none of them (recall ~0.016) — every positional rule was proven insufficient; the distant parallel conjunct has to be found by MEANING (it is the co-argument that shares the other conjunct's role), which is the meaning channel's job

**slug:** `far_coordination_needs_the_meaning_channel_the_distant_parallel_conjunct_is_a_co_argument_not_a_position` — **opened:** 2026-09-13 by strategy from the coordination solver's located frontier (owner-DONE pri 95, integrated 12:42: near coordination 0.535 = the structural ceiling of a nearest-like-class rule; far coordination 0.016).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does a reader link "the board approved the merger, the layoffs that followed it, the closure of two plants, AND the sale of the fleet"? Not by distance: by recognising that "sale" fills the SAME role for the SAME governor ("approved") as "merger" — a co-argument read (Lewis & Vasishth 2005 retrieval with the governor's slot as the cue; Frazier/Munn parallelism over MEANING, not position). Name the structure and state the computation in our organs' terms: the candidate left conjunct is the nominal whose selectional fit to the right conjunct's governor slot is highest (the typed-plausibility organ `hdlab/typed_selectional_preference`, the semantic hub `hdlab/semantic_hub`, the grounded graph `hdlab/grounded_semantic_graph`).
> 2. **REUSE.** `attachment_arm.coord_sites` (the parallel-head finder: its LEFT-conjunct retrieval is the nearest like-class head — replace/extend THAT retrieval with a meaning-scored one), `parallelism_boost` (teacher), `typed_selectional_preference` (slot fit), `semantic_hub` (similarity of the two conjuncts: coordinated things tend to be alike), `grounded_semantic_graph.select_sense`. The solver's five refuted positional levers are in `notes/problems/coordination_is_parallel_structure_.../SOLVED.md` §4c — do not re-try them.
> 3. **GENERALIZE.** Nominal, verbal and adjectival coordination; lists with three or more conjuncts; conjuncts separated by relative clauses and parentheticals.
> 4. **WALL -> DEEPER.** If the meaning score does not separate the true far conjunct from the nearer distractor, measure WHY: is the plausibility store silent on the pair (coverage), or wrong (quality)? Report the split; a coverage wall is a foundation-growth item, a quality wall is a mechanism item.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the mixing of meaning score vs locality as an operating point; never adopt a number.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700, gold categories, BOTH decodes (`experiments/_diag_decode_incremental.py`), against the CURRENT live asset (conj 0.382 incr / 0.391 map1; NEAR 0.535, FAR 0.016 per the solver's split at 9 tokens); report near and far separately; UAS not down; twin (shuffled meaning scores) at the positional baseline.
> 7. **ADJACENT.** Coordinated NPs are one plural participant for coreference and who-did-what; report which downstream reads would change; do not edit them.
> 8. **COMPLETION BAR.** FAR-conjunct recall up CI-separated over the current asset under both decodes with NEAR not down and UAS not down, twin at baseline, witness green, knowledge in counts/assets with an online observe path — OR a numbered located negative that names the missing input (coverage vs quality) with counts.

**(PHASE DIAGRAM.)** The meaning/locality mixing weight, the similarity threshold, the candidate window are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Categories: the live count organ (CCONJ 0.991 on test). Governor: the attachment arm with the in-order decode (live). Plausibility store: self-grown from the chain's own reading (BF_SPIRIT; UD-shaped seed — a provenance caveat). If the far read needs a store the chain does not yet grow, say exactly which.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a list runs long ("the merger, the layoffs that followed, the closure of two plants, and the sale of the fleet"), the reader has to link the last item back to the first one, nine or more words away. Today it links to whatever like word is nearest, which is almost always wrong at that distance: it gets about 2 in 100 of these links. People do it by meaning: the last item is the kind of thing that fits the same slot as the first. We want the reader to use the meaning organs it already has to find the distant partner.

## 2. WHY THIS ONE
A quarter of all coordination links are this far; they are the one coordination lever left after the parallel-structure landing (near links are at their structural ceiling); and the solver proved five positional levers cannot reach them. The meaning channel is the owner-endorsed main event; this is a bounded, measurable use of it.

## 3. MEASURED vs INFERRED
- **MEASURED (solver, 2026-09-13, cap 2500 full asset):** NEAR (<9 tokens, n=172) 0.535; FAR (9+, n=61 = 26% of conj) 0.016. Refuted for far: skip-PP L 0.415 < 0.551; chain-top L +0.02 ceiling; slot-sharing via plausibility 0.365 < 0.391 (store too sparse/noisy at the time); coordinator HOLD bonus NULL; distance-invariant decode bonus: far unchanged.
- **INFERRED (prove with a number):** a meaning-scored left-conjunct retrieval (slot fit + conjunct similarity) lifts far recall well above 0.1 without hurting near.

## 4. ALREADY TRIED / DO NOT REDO
The five levers above, as built. Slot-sharing is refuted ONLY as built on the current store; a coverage-vs-quality split of that store on the far pairs is the first measurement, not a re-run.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py` (coord_sites, parallelism_boost, the cue set, decode), `notes/problems/coordination_is_parallel_structure_.../SOLVED.md` (§4c in particular), `hdlab/typed_selectional_preference.py`, `hdlab/semantic_hub.py`, `experiments/_diag_decode_incremental.py`, `notes/BRAIN_MATH_REFERENCE.md` (coordination row), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_far_coordination_meaning_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (do NOT edit hdlab/ or tools/ directly — strategy lands it). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser at inference or as a teacher. Do NOT read the treebank's trees while learning. Do NOT call 0.68 a ceiling.
