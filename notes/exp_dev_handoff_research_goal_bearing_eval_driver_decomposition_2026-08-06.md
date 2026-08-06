# exp_dev hand-off — research: goal-bearing eval driver decomposition (did-it-happen vs verb-pole vs goal-relation)

**Filed-by:** research (direct corpus analysis, no lit-scan sub-agents — internal eval decomposition), 2026-08-06.
**Trigger:** `notes/research_goal_bearing_eval_driver_decomposition_2026-08-06.md` — full per-item table, distribution, ceiling estimates, and falsifiable predictions live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below beyond the HARD-PASS/HARD-FAIL bars already pre-registered in the cited research note's "Cheap decisive test" / "Falsifiable predictions" sections — the cell-author owns translating those into concrete pre-reg + code.

## Why this hand-off exists

The cited note answers the open question from `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` TOP ("COMBINED DICTIONARY+CONSEQUENCE TOOL -> HARD_FAIL + THE DEEP REFRAME"): on the 36-item OOV subset of `experiments/data/goal_bearing_modern_eval_v1.jsonl`, did-it-happen (occurrence/negation/failure/achievement detection) is the largest primary-driver bucket (15/36, 42%) with the highest standalone ceiling (up to 17/36, 47%), versus verb-valence-dictionary's hard 2/36 (6%) ceiling — confirming the reframe hypothesis. But the analysis also found goal-relation (owner-attribution + goal-congruence) is comparably large (13/36 primary, 36%) and load-bearing on 69% of items overall, including as a REQUIRED companion on 7 of did-it-happen's own 15 primary items (owner/subject mismatch cases). The corrected build target is did-it-happen wired as an input SIGNAL into the existing goal-congruence organ, not a standalone detector evaluated in isolation.

## Anchor candidates (rank-ordered)

1. **[Primary] Did-it-happen occurrence/negation-scope detector, wired as an additional signal into the existing goal-congruence organ (the one diagnosed HARD_FAIL in the combined dictionary+consequence-tool cycle).**
   - Anchor pointer: research note "Cheap decisive test" + Prediction 1.
   - Substrate-product reading: this is the direct fix for the diagnosed gap — the congruence organ's SHAPE is already right (per prior brain-fidelity work); it has been starved of the occurrence/negation input this analysis shows is the single largest missing signal. Reuse existing dependency-parse/negation-scope machinery already in the substrate rather than building a new parser.
   - Tier hint: the negation-scope detection itself is well-precedented (standard NLP negation-cueing task); the novel-synthesis risk is entirely in the WIRING — how the occurrence signal is consumed by the congruence organ without short-circuiting it (see the two numeric-threshold items below, which must NOT flip to correct-by-accident if the wiring is right).
   - Why now: closes the exact gap identified in the BACKUP doc's deep-reframe block; five prior HARD_FAILs all attacked verb-pole exclusively (5.6% ceiling on this eval) — this is the first anchor aimed at the eval's actual dominant failure mode.
   - HARD-PASS / HARD-FAIL bars: pre-registered in the research note's "Cheap decisive test" and Prediction 1 sections — do not loosen without flagging the deviation explicitly in the pre-reg file.

2. **[Secondary, gates Prediction 2] Owner-attribution / subject-goal-owner mismatch resolution, reusing coreference-resolver machinery (Centering/Cb backward-search) rather than a new organ.**
   - Anchor pointer: research note Prediction 2 + per-item table rows tagged secondary=D (owner/subject mismatch), specifically the 7 items where did-it-happen alone is insufficient: `lw_laurie_flower_table_amy`, `agg_anne_pudding_sauce_mouse_ch16`, `race_german_dog`, `race_davey_wiffle`, `onestop_malala`, `onestop_hunt_crowdfunding`, `onestop_limal_dating`.
   - Substrate-product reading: tests whether owner-attribution is genuinely a separate, comparably-sized lever from occurrence-detection (as this analysis claims) or whether did-it-happen alone already covers those 7 items (which would refute part of this analysis's framing). Per [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]: this is coreference/relational-antecedent-retrieval, reuse the existing coreference_resolver rather than islanding a new mechanism.
   - Tier hint: should run alongside or immediately after anchor 1, same eval, incremental — not a separate cycle.
   - Why now: directly informs whether the "goal-relation is load-bearing on 69% of items" claim in the research note is real before further investment in relational-binding infrastructure.

3. **[Tertiary, only if anchors 1-2 land] Numeric-threshold / quantity-vs-goal-target comparison, isolated on the 2 decisive counter-example items.**
   - Anchor pointer: research note Prediction 3 + rows `race_chen_situps` (30 sit-ups vs 35-threshold goal) and `onestop_carle_madeinfrance` (96.9% vs 100%/"entirely possible" goal).
   - Substrate-product reading: these 2 items are proof that BOTH verb-valence dictionary AND did-it-happen detection are actively misled (positive-reading verb / positive surface markers, but gold is unmet against a strict numeric bar) — a distinct third component (typed numeric goal-target + comparison) is required. Cheap to isolate: only 2 items, both already fully diagnosed in the research note.
   - Tier hint: defer until anchors 1-2 have landed results — building threshold-comparison machinery on top of an unvalidated occurrence+attribution core is premature, and the sample size (n=2) is too small to prioritize standalone.
   - Why now: not yet — sequenced explicitly behind anchors 1-2, per the research note's own Prediction 3/4 framing.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_goal_bearing_eval_driver_decomposition_2026-08-06.md` — this drill's full per-item table (36 OOV + 8 control items), distribution, ceiling estimates, falsifiable predictions, cheap decisive test.
- `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` TOP — "COMBINED DICTIONARY+CONSEQUENCE TOOL -> HARD_FAIL + THE DEEP REFRAME" block, the trigger for this drill and the baseline the cell-author should diff against.
- `experiments/data/goal_bearing_modern_eval_v1.jsonl` — the eval itself (44 items, only source of truth for this analysis).
- Whatever cell/module currently implements the existing goal-owner selector + outcome-valence goal-congruence organ (per CURRENT FOCUS banner, cert 220, "BUILT+WIRED... goal-owner selector, outcome-valence goal-congruence") — locate via capability_registry query before building anything new; this hand-off's anchor 1 is a WIRE, not a fresh build.
- Existing coreference_resolver module (Centering/Cb backward-search) referenced in [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]] — anchor 2 should reuse this, not build a parallel organ.

## Contract section

- Cell-author owns: concrete pre-reg (exact negation-cue list or reused parser component, exact wiring point into the congruence organ, exact held-out vs eval-item split if any), smoke gate, dispatch.
- Must NOT evaluate the did-it-happen detector as a standalone scorer in isolation from the congruence organ — the research note's central finding is that standalone evaluation is the wrong frame (owner-mismatch defeats bare occurrence-detection on 7/15 of its own primary items). The wiring point is the load-bearing design decision.
- Must report per-item pass/fail against the SAME 36-item table in the research note (id-for-id), not an aggregate accuracy number alone, so regressions on previously-correct items are visible.
- Must explicitly check the 2 numeric-threshold items (`race_chen_situps`, `onestop_carle_madeinfrance`) do NOT flip to correct-by-accident — that would indicate the occurrence signal is overriding rather than feeding the congruence check (a vacuousness/fairness gate, not a bonus).
- HARD-PASS/HARD-FAIL bars are pre-registered in the research note's "Cheap decisive test" and "Falsifiable predictions" sections — do not loosen at pre-reg time without flagging the deviation explicitly in the pre-reg file.

## Autonomy declaration

Research does not prescribe exact negation-cue lists, exact parser reuse mechanics, exact wiring API into the congruence organ, or exact smoke-scale parameters beyond "reuse existing dependency-parse/negation-scope machinery" and "reuse existing coreference_resolver" as directional anchors. Cell-author has full autonomy over implementation detail, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note, and subject to the "wire, don't island" constraint (anchor 1 and anchor 2 are signal-additions to existing organs, not new parallel mechanisms).
