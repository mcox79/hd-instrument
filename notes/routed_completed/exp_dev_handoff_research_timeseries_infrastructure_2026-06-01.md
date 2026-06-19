# exp_dev hand-off -- research: timeseries_infrastructure

**Filed-by**: research sub-agent (2026-06-01)
**Trigger**: Research note d:/AI/hd-instrument/notes/research_timeseries_infrastructure_2026-06-01.md identifies a cheap decisive test (less than 5 min CPU) that resolves the go/no-go on algebraic time-tag range query -- a prerequisite for any time-series product claim.

**Pause state**: Honor data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor name, sweep grid, threshold formula, and queue choice.

---

## Anchor candidates (rank-ordered)

### Candidate 1 (CHEAPEST -- laptop CPU smoke, less than 5 min)

**Anchor pointer**: time-tag XOR range query correctness
**Substrate-product reading**: Does XOR time-binding (m_t = xi_t XOR tau_t) support algebraic range queries? This is the load-bearing mechanism for the regulated time-series compliance sidecar product story. If it fails, the product claim requires temporal codebook redesign before shipping.
**Tier hint**: laptop CPU scoping smoke (not a FULL run). N=1024, K=10, 5-seed. Pure Python.
**Why-now**: HP-3 (TSDB compliance gap) is already PASSED from lit-scan. HP-1 (range query correctness) is the only remaining cheap gate before time-series product claims can be made. Cost is less than 5 min.

HARD-PASS if in-window accuracy >85% AND out-of-window contamination <20%.
HARD-FAIL if in-window accuracy <50% OR out-of-window contamination >40%.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_timeseries_infrastructure_2026-06-01.md
- Cap map (time-series context): d:/AI/hd-instrument/notes/substrate_capability_map.md (rows PP-9, PP-15, PP-20, PP-32; COMPLIANCE SIDECAR GTM section)
- Existing deletion cert work: cap_map PP-9, PP-20 rows
- Adjacent confirmed capability: algebraic deletion (used in multiple validated anchors)

---

## Contract

exp_dev designs the experiment and chooses anchor name, pre-reg thresholds, and queue. exp_dev does NOT need to follow this hand-off's phrasing -- it is context only.

## Autonomy declaration

exp_dev is autonomous on: anchor name, exact N/K choices within the smoke budget, sweep grid, threshold formula derivation, queue assignment, and timeout calculation.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
