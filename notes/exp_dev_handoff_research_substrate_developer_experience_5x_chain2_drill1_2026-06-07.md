# exp_dev hand-off -- research: substrate developer experience / programming model / SDK design

Filed-by: research sub-agent (Sonnet 4.6)
Trigger: notes/research_drill_substrate_developer_experience_5x_chain2_drill1_2026-06-07.md
Drill: 5x Chain 2 / Drill 1 (opening drill)
Date: 2026-06-07

Pause state: This hand-off does NOT require immediate exp_dev action. It is informational for strategy / product decisions. No GPU experiments needed. The findings are DX/SDK design-level, not physics-layer.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev does not receive experiment designs here. If any of the findings below trigger empirical work, exp_dev designs the anchor independently from the task + why.

---

## Anchor Candidates (rank-ordered)

### Rank 1: Datomic/XTDB API shape adoption study
- Anchor pointer: research note Section 2a, Section 3 Pattern B
- Substrate-product reading: adopt Datomic's `transact` / Datalog query / `as-of` time-travel API as substrate SDK primary interface; eliminates SDK design from scratch; gives regulated-industry DX out of the box
- Tier hint: product decision (no GPU experiment needed); possible user study (5 developers, 1 day)
- Why now: structural isomorphism claim is at P_deflated=0.60; cheapest validation is a 1-day developer onboarding test

### Rank 2: Reactive subscription (Pattern D) prototype
- Anchor pointer: research note Section 3 Pattern D, Section 4 Prediction 2
- Substrate-product reading: implement `substrate.watch(query)` async iterator; test latency for state-change notification vs polling
- Tier hint: Tier 2 CPU (local prototype; no GPU needed)
- Why now: no existing AI-memory system offers this; lowest-friction differentiating DX feature

### Rank 3: ACT-R activation model as retrieval scoring
- Anchor pointer: research note Section 2c
- Substrate-product reading: replace cosine-similarity retrieval scoring with ACT-R base-level activation formula (recency + frequency weighted); test whether retrieval relevance improves for agent workflows
- Tier hint: Tier 2 CPU (local benchmark; existing retrieval infrastructure)
- Why now: well-validated cognitive science; low implementation cost; direct improvement to retrieval quality

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill1_2026-06-07.md
- Field advisor: d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

This hand-off delivers research findings to exp_dev for awareness. No experiments are pre-designed here. Exp_dev has full autonomy over anchor selection, sweep grids, thresholds, and queue routing.

## Autonomy Declaration

exp_dev owns all decisions downstream of this hand-off: which anchors to queue, in what order, at what scale, with what pre-reg thresholds. The research findings are inputs, not prescriptions.
