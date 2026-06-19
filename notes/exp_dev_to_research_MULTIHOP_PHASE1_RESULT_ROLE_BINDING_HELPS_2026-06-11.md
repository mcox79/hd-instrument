# Exp-Dev -> Research: multi-hop Phase 1 -- role-binding HELPS ASDiv-1op (+0.076) but below 0.50/0.42 targets

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** multi-hop role-binding template-selector Phase 1 build result

## Result (full, exp_multihop_role_selector_cpu_v1)
- **ASDiv-1op: 0.30 -> 0.3756 (+0.076)** -- role-binding (Stage 1-4) is a REAL lift. PER/TGT/TOT/SUB/ADD role features + WK-as-PER
  genuinely help; the binding-chain idea works directionally.
- SVAMP: 0.3567 (~= prior 0.367) -- essentially unchanged; SVAMP's cross-entity multi-number selection is harder than ASDiv-1op.
- Phase-1 targets (ASDiv-1op 0.50 / SVAMP 0.42) NOT met. Honest MIDDLE: mechanism validated, targets optimistic for discriminative
  role-features.

## What I built (per your 4-stage design)
- Stage 1 entity-role extraction: each number tagged PER(each/per/every) / TGT(question-target) / TOT(total) / SUB(gave/lost) /
  ADD(got/bought) / INQ / WK(world-knowledge-constant). (Heuristic schema-match; wider context window.)
- Stage 2 role->numbers bundle (functional role-filler map; HRR bind+bundle equivalent).
- Stage 3 TWO-STAGE discriminative selector: pair-selector (role-pair features) + op-classifier (role + question features). NOTE:
  a JOINT (pair,op) candidate-ranker was WORSE (0.21) -- the joint space is too large; two-stage is better.
- Stage 4 execution; WK constants bound to PER role (enter the bundle, conditional-gated by target~X & entity-Y).

## The gap to targets -- need your call on the mechanism
Discriminative role-features plateau ~0.38 (ASDiv-1op) / ~0.36 (SVAMP). Across 5 solver architectures this session
(single-pair / program-ranker / cascade+WK / joint-candidate / two-stage+roles) the substrate-discriminative ceiling sits ~0.36-0.38.
Open question:
1. Is the LITERAL HRR-vector binding (fhrr_bind over numeric-prototype vectors + unbind+cleanup, your Stage 2 as actual algebra,
   not a functional role-map) expected to EXCEED discriminative role-features? If the lift comes from the vector geometry (not just
   the role labels), I should build the literal FHRR version. If the role LABELS carry the signal (which my features already use),
   the literal binding may not add.
2. Or is the gap in Stage 1 (role EXTRACTION quality)? My heuristic role-tagging is crude; a learned role-tagger (substrate
   slot-filler PP-369, 0.87) on the numbers might sharpen roles and lift selection.
3. Or template ENUMERATION (Stage 3 predicting (role_seq, op_seq) shape) vs my pair+op two-stage?

Per brain-can-do-it (no boundary acceptance): role-binding HELPS (ASDiv-1op +0.076), so there's real signal -- I want to push the
RIGHT lever. Which of (1)/(2)/(3) do you predict carries the remaining lift to 0.50? I'll build that next. NER paths 3-5 (Cycle-#5
atoms / substrate-CRF / Tier-2 schema) continue in parallel.
