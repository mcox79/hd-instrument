# exp_dev hand-off -- research: LVH245 MMR + pinv combined pipeline topology fragility 2x

Filed-by: research sub-agent
Trigger: notes/research_drill_LVH245_mmr_pinv_combined_topology_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered)

### 1. mmr_pinv_combined_5seed_lambda05_propagation_v1 (cheapest decisive test)
- Substrate-product reading: directly tests whether seed7 failure (propagation=0.143 vs threshold 0.10) is a 1-in-3 corner case or a systemic ~30-35% failure rate; determines if combined pipeline HP claim is possible at lambda=0.5 or requires architectural change
- Tier hint: CPU smoke; <20 min wall; Tier-1 (blocks combined-pipeline HP claim)
- Why now: current 2/3 pass rate (cycle 148) is ambiguous; 5-seed sweep resolves it cheaply; the research drill predicts MIDDLE-BAND (3-4/5 pass) not HARD-PASS, which means the combined pipeline HP claim needs to be re-grounded

### 2. mmr_pinv_combined_5seed_lambda03_propagation_v1 (cheapest rescue probe)
- Substrate-product reading: tests whether lowering lambda from 0.5 to 0.3 (more diversity weight) eliminates the seed7 topology failure; if HARD-PASS, TA-lambda at 0.3 is the production default and no architectural change is needed
- Tier hint: CPU smoke; <20 min wall; Tier-2 (rescue path gate)
- Why now: lambda=0.3 is a zero-engineering parameter change; if it resolves seed7, it is the fastest path to a valid combined-pipeline HP claim; research drill gives P_deflated=0.35 for this rescue

### 3. mmr_pinv_topology_stratified_spectral_gap_v1 (characterize production risk)
- Substrate-product reading: measures propagation suppression on 3 KB types with controlled spectral gap (high/medium/low separation); determines whether seed7-style failure is a corner case (low-gap only) or a production-scale risk (also medium-gap); critical for deciding whether DPP is required for general production deployment
- Tier hint: CPU; 30-60 min wall; Tier-2 (production risk assessment)
- Why now: the research drill identifies that real production KBs (Wikipedia, entity-rich KGs) have HIGHER hub centrality than synthetic test KBs; this synthetic topology sweep bounds the real production failure rate

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_LVH245_mmr_pinv_combined_topology_2x_2026-06-07.md
- Cycle 148 results (LVH #245): seed7=0.143 FAIL; seeds 0 and 42 PASS; pinv recall 1.0 unanimous
- Cycle 146 MMR UNCONDITIONAL lock: notes/research_POST_COMPACTION_BRIEF_2026-06-07.md (line 51)
- Cap map: d:/AI/hd-instrument/data/cap_map.md (look for MMR propagation suppression row)
- Production architecture: whitening + pseudoinverse + MMR (lambda=0.5, K=10) is the locked stack

---

## Contract

exp_dev owns: anchor design, sweep grids, threshold formulas, queue routing, pre-reg bands, self-test verification.
research handed off: anchor names, WHY, tier hints, context pointers.
exp_dev does NOT inherit specific numerical thresholds from this file as binding contracts -- it pre-registers its own per [[feedback-envelope-expansion-fail-bands]].

## Autonomy Declaration

exp_dev has full autonomy over anchor implementation, smoke-gate design, and queue placement. The three anchors above are ordered by strategic priority (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]); exp_dev may reorder, split, or combine based on current queue state and runner availability. Anchor 1 should run BEFORE anchor 2; anchor 3 can run in parallel with either.
