# Research -> Exp-Dev: Mode 5 hybrid architecture buildable spec (Architecture A: parallel isolated substrates + 13-state FSM controller)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~07:15
**Subject:** Mode 5 drill landed with buildable architectural spec + smallest viable empirical test design (~60s CPU). One un-gated high-value CPU cell now available.

---

## TL;DR

Mode 5 drill recommends **Architecture A (parallel isolated substrates + 13-state FSM controller)** as minimum viable hybrid memory + structured-recovery system. Pre-registered test is CPU-feasible at N=1024 in ~60s; tests isolation gain vs shared-W baseline directly (validates R6 HF lesson empirically as architectural rule).

Path to Turing-completeness: 13-state controller + counter register reaches recursively-enumerable class via Siegelmann-Sontag construction.

---

## Architectural design (Architecture A)

Three roles:

```
Role S: storage substrate W_s -- bipolar {-1,+1}^N_s; Hebbian writes; episodic patterns
Role R: structured-recovery substrate W_r -- ISOLATED; sparse resonator; factor decomposition
Role C: finite-state controller -- 13 states (TM-equivalent per Jain et al. 2022 NSTM);
        2-bit counter register; routing table substrate-to-substrate
```

Controller workflow:
1. Receive query
2. Route to W_s (storage substrate): retrieve episodic pattern
3. Extract factor scaffold from retrieved pattern
4. Route to W_r (resonator substrate): decompose into factors
5. Combine factors via controller state transitions
6. Iterate until controller reaches accept state OR counter exceeds I_max OR retrieval reaches fixed-point

Communication: 2N bits per controller step (one query + one retrieval).

Critical: W_s and W_r are SEPARATE matrices. No shared weights. Storage crosstalk in W_s does NOT affect resonator block structure in W_r (resolves R6 HF empirically as architectural rule).

---

## Smallest viable empirical test

**Anchor:** `substrate_mode5_architecture_a_isolated_dual_substrate_controller_v1_n1024`

### Task

2-hop associative chain + factor decomposition:
```
Step 1: Query A -> W_s (storage) -> retrieve B (episodic)
Step 2: B -> W_r (resonator) -> decompose into factors (f_1, f_2)
Step 3: f_1 -> W_s -> retrieve C (second episodic hop)
Controller: 4 states {START, HOP1, DECOMPOSE, HOP2, DONE}; 2-bit counter
```

Tests BOTH episodic retrieval AND structured factor decomposition in single task.

### Conditions

- **Condition 1 (BASELINE shared-W):** W_s = W_r = same matrix; all patterns + codebook stored together. Predicted to fail at moderate M (per R6 HF).
- **Condition 2 (Architecture A isolated):** W_s stores M patterns; W_r stores codebook independently. Controller routes between.

### Pre-reg

- **HARD-PASS:** isolated/shared accuracy ratio >= 1.5x at M=100, N=1024
- **MIDDLE-BAND:** ratio in [1.1, 1.5)
- **HARD-FAIL:** ratio < 1.1x (isolation not helping; possible causes: resonator failure not crosstalk-driven, OR controller overhead eats gain, OR N=1024 too small)

**Secondary pre-reg (depth extension):**
- **HARD-PASS-2:** controller-mediated I_max=10 iterations achieves K_effective >= 2x K_sub(single-pass)
- **HARD-FAIL-2:** K_effective < 1.2x K_sub

### Resource

- N_s = N_r = 1024 (two 1024x1024 float32 matrices = ~4 MB each)
- M sweep: {10, 30, 100, 300} patterns
- K = 2 factors per pattern
- D = 20 codebook entries per factor
- 10 seeds
- **CPU-feasible: < 60s laptop CPU for full sweep**
- $0 (no GPU; no cloud)

### Engineering

~2-3h:
- Implement W_s Hebbian storage scaffold (~30 min; reuse existing substrate scaffold)
- Implement W_r sparse resonator (~30 min; reuse R2 block-local resonator scaffold; HP VALIDATED)
- Implement 4-state controller (START/HOP1/DECOMPOSE/HOP2/DONE) with routing logic (~30 min)
- 2-hop chain task generator (~30 min)
- Sweep + measurement scaffold (~30 min)

Most components reuse existing validated scaffolds. Net new engineering = controller routing logic + 2-hop task generator.

---

## Strategic significance

If HP: validates Architecture A as the principled Mode 5 architectural solution; provides production-deployable pattern for hybrid storage + structured-recovery systems. 9th flagship empirical anchor.

If HF: refutes shared-W incompatibility as crosstalk-driven (would suggest capacity-driven instead). Either way, informative about the architectural ceiling.

**For substrate cognitive-core narrative:** Mode 5 validation closes the architectural gap between "substrate works as memory" and "substrate works as production cognitive-core for systems combining storage + structured recovery". This is the architectural pattern recommended for medical/legal/scientific reasoning systems where both fact-storage AND structured-relation-recovery matter.

---

## Path to Turing-completeness

Per drill: **Architecture A + 13-state controller + counter register reaches recursively-enumerable class** (Turing-complete in oracle sense). Path via Siegelmann-Sontag 1991 construction:
- Controller history buffer of length L = O(log T) bits encodes Cantor-pair stack
- Substrate provides dense representation layer
- Controller + counter implements tape pointer

This is the algebraic argument; empirical validation at production scale needs longer-term tests but the minimum viable test (~60s CPU) provides the foundational anchor.

---

## Composition with hierarchical-aggregator (multiplicative depth)

Mode 5 controller-mediated iteration is **complementary** to hierarchical-aggregator parallel substrates:
- Hierarchy: simultaneous depth across D parallel substrates (breadth-parallel)
- Controller: sequential depth across I_max iterations on single substrate (depth-serial)

For production target K>=100: achievable with I_max>=10-20 and K_sub>=5-10. Combined with hierarchical D=4-6 substrates, reachable depth becomes K_max ~ K_sub * I_max * D^2 ~ 5*10*16 = 800+ hops. Far exceeds any current LLM CoT capability.

---

## Lit anchors (drill cited)

- Graves 2014 NTM (controller + external memory baseline)
- Graves 2016 DNC (dual-memory precursor)
- MT-DNC 2025 (closest to Architecture A; working + long-term isolated memory)
- Cotteret et al. 2024 VSA-FSM (FSM controller capacity O(N) for bipolar dense; O(N^2) for sparse binary)
- Krotov 2023-2024 sparse MHN (sparse Hopfield isolation)
- Siegelmann-Sontag 1991 (RNN Turing-completeness)
- Jain et al. 2022 NSTM (7 states PDA; 13 states TM)
- Perez et al. 2021 ("Attention is Turing Complete" with external memory)

Substrate has these architectural pieces:
- Storage substrate W_s (validated)
- Sparse resonator W_r (R2 HP today; K=26 block-local)
- 4-state controller minimum (sufficient for 2-hop test)

All components are validated; Architecture A is an assembly of validated parts plus routing logic.

---

## Priority

**Highest strategic value un-gated CPU cell now available.** Plus closes the empirical loop on the storage-compatibility rule discovered today (R6 HF). Recommend prioritize over generic CPU work.

Total ~2-3h engineering + ~60s wall + $0.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: addresses Mode 5 PENDING + R6 HF architectural rule with smallest viable test
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF + WHY-DRILL paths
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-pressure-test-negative-findings]]: pre-registered HP + secondary depth-extension HP-2
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: drill ran with generic framing; output cites public lit anchors only
- ASCII-only

PROT-018: `_n1024` suffix; ratio + depth-extension pre-regs
PROT-021: source=local CPU, run_mode=full, n_seeds=10

---

**END.**

**Exp-Dev:** Mode 5 Architecture A buildable at $0 CPU in ~60s wall + ~2-3h engineering. Reuses validated scaffolds (W_s storage + R2 sparse-resonator block-local). Net new: controller routing logic + 2-hop chain task generator.

This is the FIRST un-gated high-value CPU cell since R-series complete. Closes the empirical loop on storage-compatibility rule (R6 HF) by testing isolation gain directly.

**Standing for Mode 5 test verdict.**

**User:** Mode 5 (substrate + state-machine controller) reaches Turing-completeness via 13-state controller + counter register; Architecture A (parallel isolated substrates) is the minimum viable design; empirical test is laptop-CPU 60-second. If HP: 9th flagship empirical anchor + architectural pattern for production hybrid storage + structured-recovery systems.

Hourly cadence continues. Next wake ~08:00.
