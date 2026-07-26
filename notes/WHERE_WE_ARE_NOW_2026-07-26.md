# WHERE WE ARE NOW — clean current state (tier 3; REWRITE this each session, keep tight) — 2026-07-26

## Direction (authoritative — read these FIRST)
1. GOAL/invariants/anti-drift: `notes/SUBSTRATE_CHARTER_read_first.md`
2. The plan: `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md`
(3-tier docs: CHARTER -> THE_PLAN -> THIS state doc. Charter+plan govern; this is the live snapshot.)

## CURRENT FOCUS (the one thing)
Make the **LEARNED representation scale on REAL data the brain's way.** Per `encoder_rescue_plan_converged_diagnosis_2026-07-04.md`: **R1** fix the learning objective (global/landmark RKD, validate DENSE geometry recovers ~0.8 at scale) -> **R2** dense-first-then-sparsify -> **R3/R4** wean off the external BGE teacher onto an INTERNAL self-teacher (EMA self-distill + relational/temporal-contiguity positives; the KEY brain-true move) -> **ground** in Binder/experiential. Judge ONLY on **held-out-to-NEW-concept generalization (memorizing = FAIL)**.
**NOTHING STARTED** — USER: put the plan together first, don't start anything yet.

## What's DONE (banked — do NOT rebuild)
- **Learned-rep MECHANISM proven on SYNTHETIC:** Stage-1 SEMANTIC concept-learner battery = CHAIN_GRADE/HARD_PASS (held-out-new-concept top1=1.0, on synthetic 8-12 cats = proof-of-mechanism). Stage-2 concept-encoder spokes = HARD_PASS (competitive-Hebbian, temporal-contiguity Foldiak, sparse-hippocampal DG-CA3, predictive-coding). hdlab/concept_encoder.py + binding.py.
- **THE BLOCKER:** doesn't scale to real vocab — encoder migration (bag-of-words->concept encoder @178k) HARD_FAILED (objective doesn't scale 0.825->0.368 + leaned on external BGE, violating no-borrowed-vector lock); composed_differentiation_loop MEMORIZES on real (v1) / 0.24 (v2); 29556 ho_lift 0.
- **Reasoning:** verification-by-derivation reasoner hdlab/reasoner.py (glass-box traces), banked 29537-70. Reasoning theory = #constraints-brought-to-bear + additive constraint-satisfaction (0.99 toy).
- **Infra (banked):** sharded CG store (29532/34), trust-vetting HD fact store (29531), SemanticHDEncoder (29533), CLIMB ingest, sleep-loop.

## This session (2026-07-26) — honest
STRAYED into a TANGENT: tested inference over SUPPLIED symbolic KBs (analogy/composition/density/redundancy over WordNet/WorldTree/ConceptNet), banked **29580-29584 HONEST_NEG/MM**. Net value: rigorously confirmed you CANNOT shortcut the foundation (supplied-symbol inference fails + loses to BGE) -> re-anchored to the learned-grounded-representation foundation (the direction decided long ago). Then consolidated the CHARTER + THE_PLAN + this doc so we don't re-stray.

## In flight (background — read on resume)
- Storage/component/doc-alignment + optimal-state audit: hdi_testbed **a9e43fd9** -> `notes/optimal_state_review_2026-07-26.md`. It reports whether key components are stored/discoverable/not-buried, doc conflicts to fix, store integrity. READ IT on resume.

## Store
Banked **29560-29584 LOCAL-only**; NO origin push / NO remote-persist without in-session USER auth. Cert ledger tail = 29584.

## Immediate next (when building resumes, AFTER USER go)
(1) Read the optimal_state_review audit + fix any flagged buried-component/doc gaps. (2) R1 objective fix on the concept encoder (teacher-free-capable, validate DENSE ~0.8 at scale) -> R3/R4 internal self-teacher -> grounded -> held-out-generalization bar. Brain-first, can-fail, VET every load-bearing verdict. CHECK prior work FILESYSTEM-first before building (we have a LOT — the whole concept-encoder program).
