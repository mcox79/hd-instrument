# Prereg: exp_self_extension_grounded_realprose_v1 (grounded 2nd view for REAL-prose self-extension)

**Date:** 2026-08-04. **Local-only:** no queue / remote / push. **Deterministic, multi-seed (8), resumable per-seed.**

## Question
Can the self-extension loop (exp_self_extension_loop_v1) MINT a `goal-blocker` type on **REAL
implicit-goal-block prose** (withholding / spite / omission, NO explicit connective) using **two
GENUINELY INDEPENDENT GROUNDED views**, without breaking the anti-drift guarantee?

## Motivation (v1's honest limitation)
v1 mints goal-blocker on a controlled synthetic set and is anti-drift-validated by ablation, BUT its
2nd view was a discourse/purpose-**connective** cue with a **recall gap** on naturalistic prose: the
one REAL ruler item `grapp_mcca_004` (Amy's goal to be warned, blocked by Jo's WITHHOLDING — "let her
take care of herself", omission/spite, no connective) trips the novelty residual (0.373) but the
connective 2nd view does NOT fire, so the real item would NOT mint. Real-prose self-extension was
bounded by the 2nd view's recall.

## The build (grounded 2nd view; supplied goal-schema KNOWLEDGE, not the reading mechanism)
- **VIEW 1 (typing / novelty)** — ARGUMENT STRUCTURE: who WITHHELD/did what to/from whom. Grounded
  lexical argument-structure typer (reuses `coreference_resolver.normalize_tokens`) → feature-atom
  bundle → `hdlab.predictive_coding` novelty residual vs a **harm-only** seed library (threshold 0.25,
  same organ/threshold as v1). PROPOSES. Brain: DMN/mPFC agent-goal + Trabasso goal-plan; left
  IFG/pMTG relational argument binding; VTA-RPE / cortical predictive coding for novelty.
- **VIEW 2 (independent 2nd view)** — GOAL-OUTCOME grounding: does an animate goal-owner's goal end up
  left **UNMET** as a consequence? Grounded goal-schema (agent-has-goal / goal-object / goal-UNMET);
  an animate-owner **desire** gates the schema, and the net OUTCOME valence is APPRAISED by
  ACCUMULATING outcome events over the passage in the **validated** situation-model register
  (`hdlab.situation_model_accumulate.AccumulateRegister`, atom 29609 — bind/bundle/unbind/cleanup,
  reused bit-identical) and reading the terminal valence. DISPOSES. Brain: OFC/vmPFC outcome-value
  appraisal over the situation model (Kintsch C-I / Zwaan event indexing).

## The crux (VET hardest): independence of two GROUNDED views
Both views grounded ⇒ independence is NOT free (NELL/CPL: a candidate cross-checked against ITSELF
drifts). Engineered + measured:
- **Disjoint lexicon** (self-test asserts ZERO token overlap between all VIEW-1 and VIEW-2 lexicons).
- **Disjoint mechanism** (HD novelty residual vs FHRR outcome-appraisal).
- **THE metric — co-fire-on-noise rate**: if the two grounded views fire TOGETHER on noise
  (correlated) anti-drift breaks. Noise passages are seeded with OUTCOME-TRAP words
  (sank/fell/lost/down) so the test is DISCRIMINATING (a naive outcome detector false-fires; a
  grounded goal-schema, which requires an animate desirer, must not).

## Pre-registered predictions / pass bands (majority of 8 seeds)
- **MINT on real prose**: real withholding items (`mcca_004`, `theatre_refusal`) pass BOTH grounded
  gates (enter minting); the goal-blocker type is minted with a REAL item among its confirmations.
- **C1** noise → no spurious mint (full). **C2** redundant-harm → no goal mint (incl. REAL harm items).
- **C3** utility-lift: goal-block attribution up after minting; no harm regression.
- **C4** ablation: residual-only (no 2nd view) DRIFTS (mints a spurious noise type); full does not.
- **INDEPENDENCE**: co-fire-on-noise rate == 0 AND co-fire-on-harm rate == 0.
- **HONEST boundary predictions**: spite-by-DESTRUCTION (`book_burning`, block = a destructive act,
  not a withhold) is NOT typed as goal-blocker by the withhold-grounded view 1 (impoverished
  signature); the borderline intercession (`mcca_003`) does not enter minting. These are REPORTED,
  not forced to pass.

## Verdict logic
`REAL_PROSE_SELF_EXTENSION_WORKS` iff mints_goal ∧ real_withhold_mints ∧ C1 ∧ C2 ∧ C3 ∧ C4 ∧ INDEP.
`MINTS_BUT_VIEWS_NOT_INDEPENDENT_WOULD_DRIFT` if it mints on real prose but co-fires on noise (honest
negative — the make-or-break failure). `INDEPENDENT_ANTIDRIFT_HOLDS_BUT_REAL_PROSE_RECALL_GAP` if
independence holds but the grounded view still can't catch implicit blocking on real prose.

## Test set
Synthetic (K=8/class): implicit goal-block (withholding, NO purpose connective), noise (outcome-trap
seeded), redundant-harm. REAL (n=6, VERBATIM from `data/corpora/little_women/cleaned` + gold ruler,
Director-selected + glass-box role-annotated, DIRECTIONAL): `mcca_004` (withholding), `theatre_refusal`
(withholding), `book_burning` (spite-destruction boundary), `mcca_003` (borderline), `mcca_001` +
`mcca_005` (harm controls).

## Guards / caveats
Glass-box; NO borrowed embedding/LLM/parser as mechanism; predictive_coding / self_improving_loop /
normalize_tokens / situation_model_accumulate reused bit-identical; supplied goal-schema is a
proper-noun-free lexical asset NOT tuned to the test items; view-1 argument binding is co-occurrence
level (glass-box proxy, no dependency parser); real n small (power = synthetic set); minted type NAME
is an arbitrary placeholder. Cites: `experiments/exp_self_extension_loop_v1.py`,
`preregs/2026-08-04_self_extension_loop_v1.md`, `notes/brain_component_functional_map_2026-08-04.md`.
