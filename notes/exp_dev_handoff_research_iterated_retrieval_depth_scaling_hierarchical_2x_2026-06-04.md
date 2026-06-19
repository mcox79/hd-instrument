# exp_dev hand-off -- research: iterated retrieval depth scaling hierarchical 2x

**Filed-by:** research sub-agent 2026-06-04
**Trigger:** notes/research_drill_iterated_retrieval_depth_scaling_hierarchical_2x_2026-06-04.md
**Per [[feedback-no-experiment-design-in-prompts]]:** anchor names, sweep grids, threshold formulas, and cap_map decisions are NOT specified here. exp_dev decides those autonomously.

---

## Pause state block

PAUSE-GATED: exp_dev must check data/orchestrator_paused.flag before dispatching to queue.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (Tier-1 priority): K_max vs alpha algebraic formula validation
- **Anchor pointer:** Verify K_max = c * (1 - alpha/alpha_c)^2 / alpha scaling at multiple alpha values
- **Substrate-product reading:** Algebraic ceiling for single-substrate iterated retrieval depth; if formula holds, K_max at alpha=0.2*alpha_c ~ 47 hops -- directly production-viable for legal/medical reasoning
- **Tier hint:** Tier-1 (cheap CPU, small N, fast smoke)
- **Why now:** Empirical anchor K=12 at alpha=0.5*alpha_c gives c ~ 3.3; two additional alpha values (0.1*alpha_c and 0.9*alpha_c) would confirm or refute the quadratic dependence on (1 - alpha/alpha_c). This is the cheapest decisive test.

### Anchor 2 (Tier-1 priority): Multiplicative hierarchical depth gain D=1 vs D=4
- **Anchor pointer:** Compare K_max(D=1) vs K_max(D=4) at same total association count
- **Substrate-product reading:** If K_max(D=4) >= 2.5x K_max(D=1), the hierarchical partitioning gives multiplicative depth scaling -- this is the KEY production architecture decision
- **Tier hint:** Tier-1 (CPU-viable at N=2048, D=4)
- **Why now:** Empirical D=2 gives K=24 vs K=12 -- exactly 2x. The model predicts near-quadratic gain at D=4. Confirming or refuting this determines whether to invest in D=4-8 ensemble architectures.

### Anchor 3 (Tier-2): Compositional K ratio (stored vs novel chains)
- **Anchor pointer:** K_compositional vs K_stored at same alpha and N
- **Substrate-product reading:** P_deflated=0.30 -- if compositional K >= 0.6 * stored K, substrate can handle cross-domain OOD reasoning; if < 0.3, substrate is retrieval-only not inference-capable
- **Tier hint:** Tier-2 (requires careful chain encoding: store A->B, B->C separately; never store A->C explicitly)
- **Why now:** Determines whether the K=24 gain translates to genuinely NEW reasoning (not just re-execution of stored chains). Most important for product differentiation.

### Anchor 4 (Tier-2): Resonator vs argmax hop depth at same N
- **Anchor pointer:** 3-factor chain, N=2048; compare resonator recovery depth vs argmax iterated retrieval
- **Substrate-product reading:** Model predicts resonator gives ~2.7x depth gain over argmax for factor-composed chains (K ~ 32 hops for N=4096). If confirmed, resonator augmentation is highest-leverage architectural upgrade.
- **Tier hint:** Tier-2 (requires resonator implementation; non-trivial but < 1 day)
- **Why now:** Resonator is the only single-substrate architecture that could achieve K>=30 WITHOUT D-scaling overhead.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_iterated_retrieval_depth_scaling_hierarchical_2x_2026-06-04.md
- K_max formula: Section "Sub-question 1 -- Revised K_max formula"
- Hierarchical scaling law: Section "Sub-question 2 -- Scaling ceiling" table
- Cheap decisive test spec: Section "Cheap decisive test"
- HARD-PASS / HARD-FAIL bands: Section "Falsifiable predictions"
- P_deflated: Section "P_deflated estimates" -- P=0.30 algebraic, P=0.20 implementation

---

## Contract section

exp_dev designs anchors to test the algebraic relationships identified in the research note. exp_dev does NOT need to read the full research note -- the anchor candidates above contain sufficient task + why + substrate-product reading. exp_dev designs sweep grids, threshold formulas, and cap_map decisions autonomously.

## Autonomy declaration

exp_dev has full autonomy over: anchor naming, N/alpha/D sweep values, HARD-PASS/HARD-FAIL threshold formulas, queue routing (CPU vs GPU), ETA estimation, and cap_map annotation recommendations. The research note is a CONSTRAINT SET not a prescription.
