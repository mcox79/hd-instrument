# exp_dev hand-off -- research: ant colony stigmergy DEEPER 3x

**Filed:** 2026-06-07 by research sub-agent

**Trigger:** notes/research_drill_natural_analog_ant_colony_DEEPER_3x_2026-06-07.md

**Pause state:** check data/orchestrator_paused.flag before dispatching any anchor.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names anchors + pointers only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. TAU-MIN-FLOOR-AUDIT -- convergence gate (URGENT)

Anchor pointer: research note Part 1.1, Section 5.1.
Substrate-product reading: the Dorigo-Blum (2005) convergence theorem requires tau_min > 0 (non-zero counter floor). Without it, early-accessed keys can lock in via the "rich get richer" dynamic and prevent recovery from stale patterns. This is a correctness audit, not a performance experiment. The question is: does the current Misra-Gries decay sweep allow any active counter to reach exactly 0?
Tier hint: LOCAL (audit + synthetic counter simulation, < 30 min, no GPU needed).
Why now: all downstream convergence claims are contingent on this being true. If the floor is missing, it is a correctness fix before anything else ships.
What success looks like: run decay sweep at alpha=0.10 on 1000-key Zipf-distributed counters for 100 cycles; no counter reaches 0. If any counter reaches 0, implement min_count = epsilon_floor and re-run.

---

### 2. WASSERSTEIN-DECAY-CALIB -- empirical convergence rate validation

Anchor pointer: research note Part 2.3, Section 5.2.
Substrate-product reading: the Wasserstein gradient flow theory predicts the counter distribution converges to the query distribution at rate exp(-alpha * t). If this holds for discrete Misra-Gries counters, then alpha can be calibrated from a target convergence time (T_halflife ~ 1/alpha). This makes per-customer decay a principled product configuration, not a tuning knob.
Tier hint: Remote CPU or local (HotpotQA query distribution shift simulation; no GPU needed; moderate wall time).
Why now: the Wasserstein convergence paper (2026) is new; empirical validation in the discrete counter setting has not been done. If the exponential decay holds, it immediately motivates the per-customer alpha product feature.
HARD-PASS preregistration (for exp_dev): counter W_2 distance to new distribution decays exponentially with fitted slope alpha at the tested decay rate.
HARD-FAIL: no systematic exponential convergence at any tested alpha value.

---

### 3. ALPHA-ENTROPY-MATCH -- per-customer decay tuning by query entropy

Anchor pointer: research note Part 3.3, Section 5.3.
Substrate-product reading: the Fokker-Planck analysis of ACO (2024 paper) predicts that optimal pheromone sensitivity alpha scales with the entropy H_query of the query distribution. High-entropy (diverse) customers need higher alpha; low-entropy (focused) customers need lower alpha. If this holds for substrate Misra-Gries, per-customer alpha becomes a data-driven default, not a manual choice.
Tier hint: Remote CPU (two synthetic customers with different H_query; sweep alpha; measure recall@10 at steady state).
Why now: the Fokker-Planck / Ising model connection means this is testable from the spin-glass framework the substrate already has. It directly extends the ALPHA-ANNEALING capability axis.
HARD-PASS preregistration: optimal alpha for high-entropy customer >= 2x optimal alpha for low-entropy customer.
HARD-FAIL: same optimal alpha for both customers (H_query does not predict optimal alpha).

---

### 4. FEDERATED-TOPOLOGY-RING-STAR -- multi-customer CRDT merge topology

Anchor pointer: research note Part 4.1 and 4.4, Section 5.4.
Substrate-product reading: multi-colony ACO literature predicts ring topology (neighbor-only CRDT merges) preserves per-customer counter diversity better than star topology (all-to-central aggregator), when customer domains are distinct. If confirmed, this informs the federated deployment architecture for multi-customer substrate.
Tier hint: Local or Remote CPU (3 synthetic customer corpora with distinct domains; ring vs star CRDT merge; 10 rounds; measure counter diversity and cross-domain recall).
Why now: the multi-customer architecture is coming. The topology decision should be evidence-based before shard-split ships.
HARD-PASS preregistration: ring topology shows >= 20% more per-customer counter distribution diversity vs star at 10 merge rounds.
HARD-FAIL: ring and star produce indistinguishable counter distributions at 10 rounds.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_ant_colony_DEEPER_3x_2026-06-07.md
- Prior 5x swarm note: d:/AI/hd-instrument/notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
- Dorigo-Blum 2005 TCS convergence theorem: Part 1 of research note (tau_min convergence guarantee)
- Wasserstein gradient flow connection: Part 2 of research note (arxiv 2601.04111)
- Fokker-Planck alpha_c: Part 3 of research note (arxiv 2407.19245)
- Multi-colony topology: Part 4 of research note

---

## Contract

exp_dev is authorized to:
- Queue TAU-MIN-FLOOR-AUDIT to local queue as an audit/smoke anchor.
- Queue WASSERSTEIN-DECAY-CALIB to CPU or local queue.
- Queue ALPHA-ENTROPY-MATCH to CPU queue.
- Queue FEDERATED-TOPOLOGY-RING-STAR to local or CPU queue.
- Prioritize in this order: TAU-MIN-FLOOR-AUDIT first (it is a correctness gate), then WASSERSTEIN-DECAY-CALIB.

exp_dev is NOT authorized to:
- Modify cap_map rows without orchestrator/verdict_handler sign-off.
- Pre-judge which anchors will pass or fail.
- Encode numerical parameters from this note into experiment scripts directly; design the experiment parameters autonomously per the exp_dev role contract.

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns all numerical design decisions. This file provides the scientific question, the success/failure criteria, and the tier hint. exp_dev decides the actual implementation.
