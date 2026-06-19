# exp_dev hand-off -- research: substrate-proposed atom-candidate generation (2x DEEP)

Filed-by: research:opus
Date: 2026-06-11
Trigger: 2x DEEP drill on Tier-3 substrate-on-substrate self-extension gate
Source research note: d:/AI/hd-instrument/notes/research_drill_substrate_proposed_atom_candidates_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors + pointers; exp_dev does experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 -- ATOM-PIPE-A (Stage 1-2 only smoke; <2 hr CPU)

- Anchor pointer: build gap-detect (density-valley + spectral-eigengap + algebraic-blend) + propose (cluster-center + algebraic-blend + slerp) on a reference KB of N=200 accepted atoms; observe candidate distribution; NO validation stage yet.
- Substrate-product reading: gate the full Tier-3 pipeline; if Stage 1-2 emit zero candidates in expected gap regions, no point building Stage 3.
- Tier hint: Tier-A smoke (CPU, <2 hr, single-seed).
- Why now: cheapest decisive test of whether substrate gap-detect has any signal at all.

### Anchor 2 -- ATOM-PIPE-B (Stage 1-3 full pipeline cheap decisive test; <2 hr CPU)

- Anchor pointer: 4-part cheap decisive test from research note (holdout-recall + decoy-reject + cluster-quality + cross-domain). Pre-registered HARD-PASS/HARD-FAIL in note.
- Substrate-product reading: this is the Tier 3 gate. Pass = substrate self-extension viable substrate-only.
- Tier hint: Tier-A decisive (CPU, ~2 hr, single-seed initial then n=5 multi-seed on PASS).
- Why now: Tier-3 gate is on the substrate-on-substrate progression critical path.

### Anchor 3 -- ATOM-PIPE-C (decoy-injection calibration cell)

- Anchor pointer: synthesize K=100 random-vector decoys + K=20 hand-crafted near-miss decoys (mimic algebraic-blend output but with wrong structural relations); measure rejection rate; calibrate accept-threshold percentile.
- Substrate-product reading: anti-AM/Eurisko-laundering guard. Without this, accepted atoms drift toward noise.
- Tier hint: Tier-A QC cell (CPU, ~30 min).
- Why now: needed BEFORE ATOM-PIPE-B if first-pass decoy distribution unavailable.

### Anchor 4 -- ATOM-PIPE-D (algebraic-blend vs cluster-center redundancy check)

- Anchor pointer: emit candidates via both algebraic-blend (Fauconnier-Turner via substrate binding op) and cluster-center; measure Jaccard overlap.
- Substrate-product reading: if overlap >80%, drop cluster-center channel; pipeline simpler.
- Tier hint: Tier-A ablation (CPU, <1 hr).
- Why now: drops pipeline LOC by ~30% if redundant.

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_proposed_atom_candidates_2x_2026-06-11.md (this drill's source)
- d:/AI/hd-instrument/notes/research_drill_historical_ai_self_representation_2x_2026-06-11.md (AM/Eurisko failure modes; same drill cycle)
- d:/AI/hd-instrument/memory/substrate_v32_engineered_wrapper_2026-06-11.md (substrate primitives available to pipeline)
- d:/AI/hd-instrument/memory/substrate_representation_artifacts_rescued_2026-06-10.md (cross-domain consistency rescue precedent)
- d:/AI/hd-instrument/memory/drill_pattern_temporal_contextual_not_structural_2026-06-11.md (P-class guidance for pipeline components)

## Contract

- ATOM-PIPE-A: smoke gate. PASS = >=10 candidates in gap regions; FAIL = 0 candidates -> gap-detect overhaul required.
- ATOM-PIPE-B: pre-registered HARD-PASS in source note (holdout-recall >=0.70, decoy-reject >=0.90, silhouette_density >=0.30, eigengap_ratio >=1.5, cross-domain >=2/3). HARD-FAIL: holdout-recall <0.50 OR decoy-reject <0.70 OR silhouette_density <0.15 -> pipeline insufficient substrate-only -> hybrid (substrate proposes, LLM-judge accepts) is the fallback at Tier-B confidence.
- ATOM-PIPE-C: PASS = rejection rate >=0.90 on random decoys AND >=0.70 on near-miss decoys; FAIL = either <0.70 -> validation stage too weak.
- ATOM-PIPE-D: report Jaccard; no pass/fail (ablation cell).

## Autonomy declaration

exp_dev decides: cell decomposition, seed schedule (single vs n=5), exact KB construction (use existing reference KB if shape matches; otherwise build new), how to operationalize "structural relation" count concretely (binding-partner test + role-filler match + nearest-neighbor on accepted-atom graph at threshold tau), runner allocation (likely all CPU; GPU not required).

Research-side will NOT pre-specify experiment design (per [[feedback-no-experiment-design-in-prompts]]). If exp_dev finds the pre-registered thresholds need adjustment for the actual reference KB shape, research is reachable via a strategy_request_to_research_*.md routing file.
