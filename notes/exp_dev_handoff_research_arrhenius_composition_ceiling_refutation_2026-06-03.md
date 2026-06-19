# exp_dev hand-off -- research: arrhenius-composition-ceiling-refutation deep-dive

**Filed:** 2026-06-03 by research sub-agent.

**Trigger:** Research drill notes/research_drill_arrhenius_composition_ceiling_refutation_deep_dive_2026-06-03.md identified three empirically testable experiments with HARD-PASS/HARD-FAIL thresholds. The ECC model replaces k_c=0.138/alpha; confirmation requires Test A. Filed for exp_dev auto-discovery on next emergency-refill cycle.

**Pause state:** Check data/orchestrator_paused.flag before dispatch. Queue-refill is GATED.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered; exp_dev picks from these)

### 1. ECC baseline -- correct constant-M composition (I-20 closure gate)

- **Anchor pointer:** notes/research_drill_arrhenius_composition_ceiling_refutation_deep_dive_2026-06-03.md, Cheap decisive test A, Sub-question (4), Falsifiable prediction P1/P2/P5.
- **Substrate-product reading:** The constant-M HARD_FAIL is diagnosed as an architecture defect (query type mismatch at decode: each W_k is queried with unbound content instead of bound pattern, giving near-zero overlap with stored bound patterns). Fixing the architecture by enforcing correct causal linking (bound query to W_k, same as Q-A3 but with constant M per stage) is predicted to yield EXACT-1.0 at all depths up to L~100 under the ECC model. HARD-PASS: fidelity >= 0.999 at L=2..10. HARD-FAIL: fidelity < 0.90 at any L <= 10 (would refute ECC model, require accumulation-model 2x drill). This is the I-20 resolution gate: if PASS, ECC is confirmed and product narrative is updated.
- **Tier hint:** GPU smoke (small N, small depth, fast to run). The key is fixing the architecture, not scale.
- **Why now:** This directly resolves I-20 (constant-M composition failure explanation) and either confirms or refutes the ECC model. If ECC is confirmed, drops the k_c=0.138/alpha formula from all product claims.

### 2. Near-capacity ECC soft ceiling -- constant-M alpha=0.10 correct architecture

- **Anchor pointer:** notes/research_drill_arrhenius_composition_ceiling_refutation_deep_dive_2026-06-03.md, Cheap decisive test B, Sub-question (4) table row "constant-M alpha=0.10 correct implementation", Falsifiable prediction P3.
- **Substrate-product reading:** With correct causal linking at alpha=0.10 (72% of capacity), the ECC soft ceiling formula predicts k_c ~ 319 stages (derived from AGS per-stage fidelity m(alpha=0.10) = 0.998407). Testing L=2, 5, 10, 50, 100, 319 with correct implementation gives the first quantitative product spec for near-capacity composition depth. HARD-PASS: fidelity >= 0.99 at L=50. HARD-FAIL: fidelity < 0.95 at L <= 10 (ceiling much earlier than predicted). If confirmed, this yields a precise, alpha-dependent depth guarantee for the product narrative.
- **Tier hint:** GPU full (L=319 needs larger N to be well-conditioned; multi-seed). Depends on anchor 1 passing.
- **Why now:** Opens the quantitative depth guarantee: "at loading alpha per stage, composition succeeds for L stages where L < k_c(alpha)". This is the replacement formula for k_c=0.138/alpha.

### 3. Query-type diagnostic -- minimal fix to original constant-M script

- **Anchor pointer:** notes/research_drill_arrhenius_composition_ceiling_refutation_deep_dive_2026-06-03.md, Cheap decisive test C, Sub-question (1)-(2) architecture analysis.
- **Substrate-product reading:** The architecture-defect hypothesis predicts that adding a single line (re-bind Xi_contents[k-1][q] with Xi_ctxs[k-2][q] to produce the correct query type for W_{k-2}) makes k=2 succeed in the original constant-M script. This is a minimal surgical test: change only the query type, leave M, N, seeds, alpha unchanged. HARD-PASS: k=2 fidelity >= 0.90 after fix. HARD-FAIL: k=2 still empty/garbage (refutes architecture-defect hypothesis; requires re-examining the constant-M HARD_FAIL from scratch). Cheaper than anchor 1 and provides the most direct evidence about the failure mode.
- **Tier hint:** CPU smoke (very fast; single change to existing script; tests one hypothesis directly).
- **Why now:** Cheapest possible confirmation of the architecture-defect hypothesis. If PASS, confirms the diagnosis before investing in anchor 1/2.

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_arrhenius_composition_ceiling_refutation_deep_dive_2026-06-03.md
- Failed anchor script (to diagnose): d:/AI/hd-instrument/experiments/exp_composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096.py
- Q-A3 reference architecture (causal-linking correct): d:/AI/hd-instrument/experiments/exp_q_a3_l14_cross_layer_composition_v1_n4096.py
- Prior Arrhenius drill (I-20 context): d:/AI/hd-instrument/notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md
- Q-A3 halving preregs (empirical success evidence): d:/AI/hd-instrument/preregs/2026-06-03_q_a3_l30_l31_n4096.md
- Issue I-20 (open): referenced in compaction brief d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md

---

## Contract

exp_dev is dispatched with TASK + WHY + CONTRACT + AUTONOMY. exp_dev designs the experiment (N, seeds, queue, thresholds, anchor name, implementation details). The handoff provides the WHY and the prediction structure. exp_dev does NOT receive inline numerical sweep grids or pre-committed cap_map decisions.

## Autonomy declaration

exp_dev decides: which of the 3 anchors to ship first (recommended: anchor 3 cheapest, then anchor 1, then anchor 2), what N and seed count to use, whether smoke vs FULL, which queue tier, anchor names, and ETA. The rank ordering above is a suggestion; exp_dev may reorder based on current queue state and runner availability.
