# exp_dev hand-off -- research: mycorrhizal DEEPER 3x (currency exchange + game theory)

Filed-by: research sub-agent (2026-06-07)
Trigger: research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns experiment design. This file provides context pointers and anchor candidates ranked by P_deflated x cost. exp_dev selects and designs.

---

## Anchor candidates (rank-ordered)

### Rank 1: Extension B -- Standing priming parameter (P_deflated = 0.70, cost = 1 day)

Anchor pointer: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md, section "Extension B"
Substrate-product reading: federated customers run at lower contradiction threshold than isolated customers, providing an immediate detection quality lift with zero architecture change. One configuration parameter.
Tier hint: Tier C (local, no GPU required)
Why now: lowest cost, highest P_deflated in the 3x drill. Can be dispatched immediately as a smoke test. Pre-conditions: existing contradiction detection baseline established.
Pre-reg bands: HARD-PASS >15% detection rate lift at <10% FP rate increase; HARD-FAIL <5% lift.

### Rank 2: Cheap decisive test -- Grasso 2025 coupled simulation (P_deflated = 0.75 for simulation validity, cost = 30 min)

Anchor pointer: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md, section "Cheap decisive test"
Substrate-product reading: simulate the Grasso 2025 coupled biomass equations with substrate-LLM parameter mapping. Confirm that the mutualistic attractor is reachable from physically plausible starting conditions. This is a DESIGN GATE, not a product feature -- runs before engineering investment in any LLM coupling architecture.
Tier hint: Tier C (local CPU, pure Python, 30 min)
Why now: gates all LLM coupling engineering. If dynamics diverge (HARD-FAIL), the coupling design needs revision before any implementation. $0, 30 min.
Pre-reg bands: HARD-PASS dynamics converge to mutualistic attractor for >=90% of starting conditions in plausible parameter range; HARD-FAIL divergence for realistic LLM quality ranges.

### Rank 3: Extension A -- Tiered-channel federated routing (P_deflated = 0.65, cost = 1-2 weeks)

Anchor pointer: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md, section "Extension A"
Substrate-product reading: domain-tagged routing uses within-domain (low DP noise) vs cross-domain (high DP noise) channels. Reduces per-query DP privacy budget by estimated 40-60% for domain-specific queries.
Tier hint: Tier C (local; routing layer change)
Why now: DP budget is a scalability constraint for federation. Any reduction extends the deployment envelope.
Pre-reg bands: HARD-PASS >30% budget reduction for same-domain queries at <5% quality loss; HARD-FAIL <10% budget reduction.

### Rank 4: Extension E -- Binding mineralization tiers (P_deflated = 0.65, cost = 1 week)

Anchor pointer: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md, section "Extension E"
Substrate-product reading: bindings above corroboration threshold C_min switch to near-zero decay rate. Prevents adversarial dislodging of well-established facts. Direct EU AI Act Article 12 compliance benefit (persistent audit trail).
Tier hint: Tier C (local; decay model modification)
Why now: security hardening before enterprise deployment. Low implementation risk.
Pre-reg bands: HARD-PASS mineralized bindings survive 100 adversarial attempts at <0.1% error rate; HARD-FAIL dislodged by <10 attempts.

### Rank 5: Extension C -- Allelopathic negative signal propagation (P_deflated = 0.55, cost = 1-2 weeks)

Anchor pointer: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md, section "Extension C"
Substrate-product reading: NEW from 3x drill. DP-protected high-confidence contradiction list propagates via existing batch federation to reduce trust scores network-wide for known-false assertion patterns. Distinct from event-triggered JA alert (5x Extension 2).
Tier hint: Tier B (remote CPU for at-scale test; local smoke)
Why now: reuses existing batch federation infrastructure. Marginal engineering cost for a qualitatively new capability (network-wide misinformation suppression).
Pre-reg bands: HARD-PASS >20% trust reduction for known-false assertions, <5% false suppression; HARD-FAIL >10% false suppression.

---

## Context pointers

- Research note (3x drill): d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md
- Prior 5x note: d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Prior exp_dev handoff (v195 template): d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

---

## Contract section

exp_dev owns: experiment design, pre-reg, dispatch, smoke gate, queue_add.sh, post-ship verify.
Research provided: anchor candidates rank-ordered by P_deflated x cost, mechanism summaries, pre-reg band suggestions (exp_dev can override).
Orchestrator owns: pause gate check, cap_map update after verdict.

## Autonomy declaration

exp_dev may: select any subset of anchors above; reorder; combine into batch; adjust pre-reg bands based on current queue state; add own smoke gates.
exp_dev must NOT: dispatch if data/orchestrator_paused.flag exists; modify research note; skip pre-reg.
