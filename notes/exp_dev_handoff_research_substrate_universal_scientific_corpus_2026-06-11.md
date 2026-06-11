# exp_dev hand-off — research: substrate as UNIVERSAL SCIENTIFIC CORPUS engine

Filed-by: research (Opus) 2026-06-11
Trigger: research drill delivery notes/research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag (this handoff is structural; queue refill is pause-gated)

Per [[feedback-no-experiment-design-in-prompts]]: anchor candidates are rank-ordered POINTERS to the research note's pre-registered cheap-decisive-test + falsifiable predictions; exp_dev owns the experiment design within the pre-registered bands. No inline experiment math in this handoff.

## Anchor candidates (rank-ordered)

### Anchor 1 — CORPUS-PILOT-1: S2ORC ML slice substrate corpus engine (HIGHEST PRIORITY)

Anchor pointer: notes/research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md sections (b) Cheap decisive test + (c) P1, P2, P3.
Substrate-product reading: gates v1 vertical-substrate product positioning. If P1+P2+P3 all HARD_PASS or 2-of-3 with P3 in MIDDLE band, v1 ML-research-substrate is engineering-ready in 4-8 weeks per north_star timeline. If HARD_FAIL on P2+P3, substrate-as-corpus is purely better-RAG (lower-value commercial wedge).
Tier hint: Tier-2 budget; ~6-12 hr CPU; single workstation; no GPU.
Why now: substrate-on-substrate Tier-3/4/5 program filed today; substrate-on-corpus is the application that ties the program to revenue. Closest test to ship-decision.

### Anchor 2 — CORPUS-LBD-1: Swanson-style ABC discovery on pre-discovery corpus snapshot

Anchor pointer: notes/research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md section (c) P3.
Substrate-product reading: validates the discovery-engine product positioning specifically. The cleanest single-claim test of "substrate finds undiscovered public knowledge"; HARD_PASS = >=3 of 8 historical Swanson cases recovered in top-10 against 100 distractors.
Tier hint: Tier-2 budget; ~6 hr CPU.
Why now: cleanest differentiating capability test; isolates the discovery claim from the retrieval claim. Lower-cost alternative if CORPUS-PILOT-1 budget cannot fit.

### Anchor 3 — CORPUS-INGEST-1: streaming ingestion + drift-detection + sub-shard-split simulation

Anchor pointer: notes/research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md section (d) Ingestion infrastructure + section (c) P1.
Substrate-product reading: validates the ENGINEERING viability of the v1 ingestion pipeline at 1M-paper accumulation. BOCPD drift-detector firing rate, sub-shard split correctness, per-paper trust-weight propagation through citation algebra under streaming write-load.
Tier hint: Tier-2 budget; ~12-24 hr CPU; can run unattended overnight.
Why now: complements CORPUS-PILOT-1 by stressing the OPERATIONS path rather than the QUERY path. Run after CORPUS-PILOT-1 passes; do not run first.

## Context pointers (file paths only)

- notes/research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md (this drill's source)
- notes/research_drill_substrate_proposed_atom_candidates_2x_2026-06-11.md (3-stage gap-detection pipeline; reused for structural-gap detection in P3)
- notes/research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (5-stage validation pipeline; reused for discovery-output filter)
- notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md (4-stack architecture; mirrors corpus engine's substrate primitives)
- notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md (BOCPD-based dialectic methodology; reused in CORPUS-INGEST-1 drift detector)
- notes/research_drill_7_invariants_empirical_validation_2x_2026-06-11.md (audit-mode commercial wedge; integrated in v1 audit endpoint)
- notes/substrate_capability_map.md (cap_map rows under question)
- MEMORY.md entries: PP-225 fact-scaling correction (kb100K Tier-A genuine); substrate v3.2 engineered wrapper (multi-substrate sharding); substrate_static_robust_dynamic_fragile (per-paper trust-weight risk profile)

## Contract section

Per research role contract: exp_dev owns experiment design within pre-registered HARD_PASS / HARD_FAIL / MIDDLE-band thresholds in the source drill note. Research does NOT specify cell-by-cell sizes, hyperparameters, or numerical configs in this handoff (per [[feedback-no-experiment-design-in-prompts]] + [[feedback-query-privacy-decomposition]]). Substrate-novel parameters live ONLY in this repo, never in external queries.

## Autonomy declaration

exp_dev chooses:
- Order in which anchors are shipped (recommended: Anchor 1 first; Anchor 2 OR 3 second per queue load + budget).
- Cell granularity (single-cell-per-anchor vs split per-P-prediction).
- Smoke gate composition (recommended: 5K-paper smoke from S2ORC ML slice to validate ingestion pipeline before 500K full run).
- Whether to integrate any Anchor 2 results into Anchor 1's CORPUS-PILOT-1 verdict OR run as independent verdicts.

Research is available for HP/HF re-calibration if smoke-gate evidence diverges from the pre-registered bands.
