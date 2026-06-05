# exp_dev hand-off -- research: STDP replay decay model design 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** notes/research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file contains TASK + WHY + CONTRACT + AUTONOMY pointers only. Exp-dev designs anchor names, sweep grids, threshold formulas, queue choice, and pre-committed cap_map decisions autonomously.

---

## Why this hand-off exists

B5 STDP-replay cell requires a forgetting mechanism for replay consolidation to have work to do. Research 2x drill (2026-06-04) characterizes three biological decay models (palimpsest / bounded weights / metaplasticity), derives algebraic forgetting timescales for each, and identifies palimpsest decay with alpha=0.003 as the cheapest first-pass implementation that places N=2048 substrate in the detectable forgetting regime near alpha_c. Without this addition, replay cannot selectively strengthen weakened patterns (all patterns remain equally well-stored, replay is redundant). The algebraic test design is fully pre-registered in the research note.

---

## Anchor Candidates (rank-ordered)

### 1. Palimpsest decay + STDP-ordered replay test (HIGHEST PRIORITY)

**Anchor pointer:** Sub-question 5, test arm design in research note
**Substrate-product reading:** Add palimpsest decay (W *= (1-alpha) before each Hebbian write) at N=2048, M=287 patterns (near alpha_c). Compare no-replay / random-replay / STDP-ordered-replay at 10% time budget. HP: STDP-ordered replay achieves >= 1.5x retention ratio vs no-replay. This is the cheapest direct test of whether replay-driven consolidation is algebraically achievable at substrate class scale.
**Tier hint:** CPU smoke (N=2048, M=287, no LM coupling; estimated < 60s per arm; pure numpy, no GPU needed)
**Why-now:** B5 is blocked on this mechanism. Without measurable forgetting, B5 has no consolidation effect to measure. This is the lowest-cost gate that either validates or refutes the palimpsest path before any larger investment.

### 2. Alpha sweep: forgetting rate vs retention ratio (SECOND PRIORITY)

**Anchor pointer:** Sub-question 4 (biological timescale mapping) + Sub-question 5 (WHY-DRILL diagnostics) in research note
**Substrate-product reading:** Sweep alpha over [0.001, 0.003, 0.005, 0.01] at N=2048, M=287. Measure P_correct for no-replay arm across alpha values. Verify that optimal alpha for replay benefit lies in [0.003, 0.005] as algebraically predicted (M_steady ~ 1/alpha ~ M_c at this range). This sweep also validates the algebraic formula M_steady ~ 1/alpha against empirical retention curves.
**Tier hint:** CPU smoke (4 alpha values x 1 arm = 4 cells; fast grid)
**Why-now:** If arm 1 hits HARD-FAIL, alpha sweep identifies whether the issue is alpha too small (no forgetting) vs patterns too random (no sequential structure). Diagnostic first before committing to structured pattern test.

### 3. Structured patterns test (SEQUENTIAL DEPENDENCY)

**Anchor pointer:** Sub-question 5, recommendation for semi-structured Markov-chain patterns in research note
**Substrate-product reading:** Use Markov-chain patterns (transition probability 0.7 to designated next pattern) instead of random iid bipolar. If STDP-ordered replay shows > 1.5x retention over random replay only on structured patterns and not random patterns, that discriminates the hypothesis: STDP replay exploits sequential dependencies, not just repeated exposure. Algebraic prediction: gap STDP - random should be large (up to 1.94x per asymmetric Hopfield capacity result) for structured patterns; ~0 for random.
**Tier hint:** CPU smoke
**Why-now:** Follows arm 1 if HARD-FAIL or MIDDLE-BAND; diagnoses whether pattern structure is the missing variable.

---

## Context Pointers

- Research note (full algebraic derivations, all pre-reg thresholds, WHY-DRILL diagnostics):
  d:/AI/hd-instrument/notes/research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md
- Prior STDP temporal asymmetry drill (asymmetric W algebra, sequence capacity 1.94x):
  d:/AI/hd-instrument/notes/research_drill_stdp_temporal_asymmetry_substrate_2x_2026-06-04.md
- Prior REM-replay drill (replay architecture, energy-guided selection, N>=8192 LM constraint):
  d:/AI/hd-instrument/notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md
- Key algebraic formula: M_steady ~ 1/alpha; alpha_optimal ~ 1/M_c ~ 0.0035 for N=2048
- Critical constraint: B5 test does NOT require LM coupling (pure substrate retrieval test at N=2048 is valid)

---

## Contract

Exp-dev autonomously decides:
- Anchor names, queue routing, timeout estimation
- Exact sweep grid values for alpha (within [0.001, 0.01] range identified)
- Pre-registration of HP/MID/HF bands per envelope-fail-bands protocol
- Whether to combine arms 1+2 into a single multi-cell anchor or ship separately
- cap_map implications after verdict

Exp-dev is NOT asked to:
- Re-derive the algebraic formulas (research note has them)
- Design a different decay model (palimpsest is the recommendation; escalate to orchestrator if disagreement)
- Add LM coupling to this test (pure substrate retention test is the correct scope for B5)

## Autonomy Declaration

Research sub-agent does not commit to cap_map. Exp-dev owns implementation + pre-reg. Verdict-handler owns cap_map update after result. Orchestrator owns sequencing if multiple anchors compete for queue slots.
