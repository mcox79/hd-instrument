# exp_dev hand-off -- research: substrate cross-discipline analogue surfacing 2x DEEP

**Filed-by:** Research (Opus)
**Date:** 2026-06-12
**Trigger:** Research drill 2x DEEP -- see [d:/AI/hd-instrument/notes/research_drill_substrate_cross_disc_analogue_surfacing_2x_2026-06-12.md]
**Pause state:** Honor `d:/AI/hd-instrument/data/orchestrator_paused.flag` if set. exp_dev decides ship vs hold per pause gate.

Per [[feedback-no-experiment-design-in-prompts]]: this file lists pointers, anchor candidates, and ranking only. exp_dev OWNS experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST priority) -- CROSS-DISC-PILOT-1
- **Anchor pointer:** "Substrate-Cross-Disc-PILOT-1" -- see Section (b) Cheap decisive test in parent note
- **Substrate-product reading:** validate cross-partition analogue surfacing as a Tier-2 wrapper feature -- foundation for USABILITY (Findings 18 Gap 6 closure follow-on)
- **Tier hint:** Tier-2 wrapper, no core changes (per substrate_v32_engineered_wrapper)
- **Why-now:** science 13-category taxonomy LANDED Day 2; cross-partition algebra-vec cosine now STRUCTURALLY VALID; window opens
- **Estimated cost:** < 4 hr CPU; ~30 min Research rubric
- **HARD-PASS:** >= 5 pairs score 2 on productivity rubric (see parent (b))
- **HARD-FAIL:** zero pairs score 2

### Anchor 2 -- CROSS-DISC-MULTIPLEX-1 (gated on Anchor 1 pass)
- **Anchor pointer:** Strategy 2 implementation -- multiplex community detection with k-clique percolation across 4 layers (algebra + semantic + slipnet-relation + content-ref)
- **Substrate-product reading:** higher-order analogue (4+ atom communities) -- highest Tier-5 leverage
- **Tier hint:** Tier-2 wrapper + multiplex graph library (networkx or graph-tool)
- **Why-now:** gated by Anchor 1 (need cosine pipeline validated first)
- **Estimated cost:** ~2-3 hr CPU + ~1 hr Research community-audit

### Anchor 3 -- CROSS-DISC-SLIPNET-GATE-1 (always-on; runs alongside Anchor 1 + 2)
- **Anchor pointer:** Strategy 4 implementation -- slipnet-relation typed triangle gate
- **Substrate-product reading:** false-positive rate gate; required for production deployment of Strategy 1+2
- **Tier hint:** Tier-2 bundle reading slipnet-relation atoms; no new primitives
- **Why-now:** gate efficacy (P4) is load-bearing for Strategy 1 production claim
- **Estimated cost:** ~1 hr CPU (small)

### Anchor 4 -- CROSS-DISC-ABC-1 (gated on Anchor 1 pass)
- **Anchor pointer:** Strategy 3 implementation -- Swanson ABC triple discovery via typed-relation bridge
- **Substrate-product reading:** publishable-hypothesis generation channel
- **Tier hint:** Tier-2 (composes slipnet + algebra-vec)
- **Why-now:** complementary to Anchor 2; surfaces 3-atom triples Strategy 2 might miss
- **Estimated cost:** ~1 hr CPU + ~2 hr Research rubric

### Anchor 5 -- CROSS-DISC-PRODUCTIVITY-DASHBOARD
- **Anchor pointer:** add productivity tracking to substrate-self-index metrics.py (per parent note Section "Productivity tracking")
- **Substrate-product reading:** Tier-5 measurement instrument -- enables sustained-rate P5 claim
- **Tier hint:** lightweight, ~50 lines in metrics.py
- **Why-now:** without this, Tier-5 sustained-rate claim is unmeasurable
- **Estimated cost:** ~30 min

## Context pointers (file paths, not summaries)

- Parent drill note: d:/AI/hd-instrument/notes/research_drill_substrate_cross_disc_analogue_surfacing_2x_2026-06-12.md
- Findings 18 endorsement (science taxonomy): d:/AI/hd-instrument/notes/research_to_testbed_FINDINGS_18_ENDORSED_SCIENCE_TAXONOMY_INCOMING_2026-06-11.md
- Findings 18 usability gap (origin): d:/AI/hd-instrument/notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md
- Two-axes substrate architecture memory: d:/AI/hd-instrument/notes/substrate_two_axes_semantic_vs_content_referenced_2026-06-11.md
- Engineered-wrapper pattern: d:/AI/hd-instrument/notes/substrate_v32_engineered_wrapper_2026-06-11.md
- 5-tier progression (Tier-5 self-discovery): d:/AI/hd-instrument/notes/substrate_on_substrate_5_tier_progression_2026-06-11.md
- Methodology rule 8 (us OR substrate): d:/AI/hd-instrument/notes/substrate_content_sources_us_or_substrate_2026-06-11.md
- Substrate index modules: d:/AI/hd-instrument/backend/substrate_index/ (algebra_index.py, relate.py, retrieve.py, metrics.py)

## Contract

- exp_dev OWNS smoke gate + queue add + REMOTE VERIFY per envelope-fail-bands
- exp_dev OWNS pre-reg of HARD_PASS/HARD_FAIL within envelope (research has pre-registered AT THE STRATEGY LEVEL; exp_dev tunes to cell-level)
- exp_dev can REJECT any anchor and route back to Research with reason
- Research provides rubric scoring on PILOT-1 output within 1 day of HARD_PASS

## Autonomy declaration

exp_dev decides:
- Ship order (Anchor 1 first; Anchors 2-5 conditional on Anchor 1 outcome)
- Smoke vs full envelope
- Whether to bundle anchors into one cell or split
- Queue lane (CPU local; nothing here needs GPU)
- Cell-level pre-reg parameters (cosine thresholds, k-clique parameters, etc.)
