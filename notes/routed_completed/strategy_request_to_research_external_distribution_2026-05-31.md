# Routing: research — external-distribution priority list (6 priorities)

**From**: orchestrator
**To**: research
**Date**: 2026-05-31
**Source**: external-Claude discussion synthesis brought back by user
**Calibration**: [[feedback-lit-scan-calibration-penalty]] applies — deflate external-Claude work-plan claims 0.10-0.20 (numeric specifics + sequencing reasonable; some claims pre-date today's verdicts)
**Cap_map state when filed**: v297 (commit eb86886). Cap_map JUST compacted (commit 8728223) — main file is 80% smaller; full history in `notes/substrate_capability_map_history.md`.

## Orchestrator's pre-filing evaluation

The document is well-sequenced but predates today's verdict cascade. Specifically:
- Adversarial sub-row ALREADY moved RED -> YELLOW today (a_query_sim first viable defense, G8_HARD_PASS, cap_map v297).
- Path D ALREADY HARD_PASSED past 32N today (G7_HARD_PASS).
- Modern Hopfield 16N corroborated CPU + cloud-GPU today (C9 second-source).
- D1 query-margin-gate ALREADY HARD_FAILED today; verdict_handler routed R2/R3/R4 rescue ladder — work on D7 (testbed P6 in this doc) should sequence AFTER any orchestrator-side update on whether a_query_sim subsumes the D7 motivation (probably yes for codebook-collision; D7 was originally aimed at edit-semantics 99.4% breach).

Numerical claims worth verifying in research drill:
- TCFT degradation: var_ratio 0.20 -> 0.33 -> 0.50 -> 0.66 across M/N = 0.25 -> 0.5 -> 1.0 -> 2.0 at N=16384. Orchestrator does not have direct visibility into when this specific data was captured; research should verify the source anchor before designing Phase 1 analysis.
- Path B sub-capacity boundary at M in {500, 1000, 2000}: research should verify against most recent Path B characterization (T5 cap_map context).

Below: the 6 research priorities as filed, lightly annotated.

## Priority 1 — Substrate-LLM Week 1 Feasibility Smoke (GO/NO-GO)

**Strategic gate** for the 7-8 week PP-8 build commitment. Three scenarios designed to surface substrate-distinctive value vs vanilla LLM:
- A. Edit-then-query coherence (50 facts, mid-conversation edit, before/after query comparison)
- B. Deletion-with-certificate generation (100 facts, 10 deletions with audit cert, query the deleted info)
- C. Multi-hop reasoning with audit (relational facts, 3-5 hop traversal, audit trail comparison)

**GO**: integration works, distinctive value in >=2 of 3 scenarios, coherent generation, within Week 0 latency budget.
**NO-GO**: incoherent generation, no distinctive value, latency exceeds budget.
**MIDDLE**: marginal value or degraded quality.

**Prerequisites**: Phi-3 Missing 7 #3 + #4 complete tonight (testbed-owned; gated on V2 24h drain ~21:11 ET).

**Cap_map ref**: PP-8 row v292+; current P=0.30-0.45 with 8GB-local-GPU constraint (RTX 4060 Ti).

**Cost**: ~3-5 days focused research, local GPU primarily.

**Orchestrator caveat**: this is the load-bearing test for the largest current strategic bet. Apply sharp pre-reg discipline before starting (HP/HF criteria in writing, no ex-post threshold drift).

## Priority 2 — TCFT Degradation Mechanism Analysis

**Goal**: Mechanistic understanding of why TCFT var_ratio degrades with M/N; identify recovery to extend operating envelope; update compliance positioning.

**Phase 1** (analytical): decompose existing var_ratio data into multi-probe variance + codebook-collision + W-saturation components. Build empirical model.
**Phase 2** (targeted probes): test the dominant-mechanism hypothesis at small scale.
**Phase 3** (recovery): for the dominant mechanism, design recovery + test at multiple M/N points.

**Cost**: ~6-8h analysis + ~3-5h small probe runs (CPU local).

**Orchestrator caveat**: verify the source dataset for the var_ratio numerics before designing Phase 1. Phase 2/3 anchors should be filed as `strategy_request_to_exp_dev_*` routing files when research is ready.

## Priority 3 — Cross-Framework Probe (overdue per 24-48h cadence)

Pick 1+ of:
- A. Percolation theory on Path D's per-hop independence (G7 HARD_PASS past 32N strengthens this probe's relevance)
- B. Sparse-coding NTK on Path B sub-capacity behavior
- C. Free probability on non-equilibrium statistical mechanics (extends substrate's SKAH-M class anchoring)

Each: ~3-5h analysis, theoretical positioning doc.

**Per [[feedback-aggressive-cross-domain-research]] + [[feedback-periodic-scope-expansion]]**: this is overdue. Pick the framework probe with highest substrate-decision impact, not the most-novel one. Probe A is most aligned with today's G7 result.

## Priority 4 — Compositionality Audit API Design Drill

**Goal**: 30-60min drill answering API spec / atoms tracked / granularity / storage cost / latency overhead. Followed by design doc writeup (~2h).

**Output**: API specification with calibrated engineering effort estimate.

**Orchestrator note**: this is the prerequisite for the killer-feature engineering work the testbed has been queueing toward. Cheap; high-leverage gate.

## Priority 5 — Substrate-LLM Build Week 1 Detailed Planning (CONTINGENT on P1 GO)

Detailed plan for Weeks 2-6 covering Q-Former architecture, QLoRA fine-tuning, multi-hop Rescue C, 4-condition evaluation, 3 ablations, 4 bespoke benchmarks, contamination check.

**DO NOT START** unless P1 lands GO. If P1 NO-GO or MIDDLE, pivot to deepening Pattern B with production LLM (testbed-owned).

## Priority 6 — Path B Sub-Capacity Production Characterization

Boundary mapping at M in {500, 1000, 2000}, depth 5-10, identify exact boundary + interpolation behavior. ~3-5 GPU hours or ~$0.10 Lambda.

**Orchestrator note**: file as `strategy_request_to_exp_dev_*` when research is ready to ship this anchor. Verify against T5's latest characterization first (per the pre-filing-evaluation flag above).

## Cross-session dependencies (research-affecting)

- Phi-3 Missing 7 #3 + #4 (testbed) tonight -> Week 1 feasibility smoke design (research P1).
- Research P1 PASS -> Research P5 detailed planning AND testbed Pattern B with Anthropic API.
- Research P1 NO-GO -> both pivots: research to substrate-physics rolling drill cadence, testbed to deepening Pattern B as primary product narrative.
- Research P2 completion -> Testbed TCFT recovery engineering (sequential).

## How to file deliverables

- Research notes: `notes/research_<topic>_<date>.md`
- Decisions log: append to `notes/research_decisions_2026-05-31.md` (or next-day file)
- Cap_map-bumping findings: `notes/strategy_request_to_strategy_<topic>_<date>.md` to orchestrator
- Experiment-dispatch needs: `notes/strategy_request_to_exp_dev_<topic>_<date>.md` to orchestrator
- Status_log: `log_event(source='research', ...)` after each substantive deliverable

## Files referenced

- This routing file (closes after research reads + moves to `routed_completed/`)
- Source: external-Claude discussion synthesis brought back by user 2026-05-31 (per [[feedback-research-synthesis-external-discussion-cycle]])
- Cap_map v297: `notes/substrate_capability_map.md` (compacted version; full history in `..._history.md`)
- Today's verdicts: commits eb86886 (cloud 3-pack), 7fc06b5 (multi_hop confound), b116da9 (Modern Hopfield CPU + D1 fail + C3 PP-2 foothold), a560442 (C6+C7 CPU char), c079b71 (CPU recovery batch)


---
**Acted-on 2026-06-01:** P3+P4 delivered and accepted (cap_map v305->v306 caveat updates + NEW PP-12 row); P2 BLOCKED on source verification (orchestrator read: external doc cited hypothetical degradation curve not measured data; mean_var_ratio=3.2e-8 in cap_map vs 0.20-0.66 doc sequence -- six orders of magnitude discrepancy); P1/P5/P6 remain pending elsewhere.
