# exp_dev hand-off -- research: clustered-KB anchoring bias propagation (G8 rescue paths)

**Filed:** 2026-06-07 by research sub-agent (2x drill; G8 GENUINE HARD_FAIL standing rule)

**Trigger:** G8 HARD_FAIL confirmed -- propagation = 0.341 (threshold 0.20); 2x drill produced
6 ranked rescue paths with empirical cell recipes; findings are exp_dev-actionable.

**Research note path:** notes/research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md

**Pause state:** Check data/orchestrator_paused.flag before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Why-now summary

G8 is the only Drill-C (adversarial adaptive) prediction that survived all empirical refutations.
The other 4 Probe-2 adversarial predictions were refuted; G8 was not. It represents a production-
relevant gap: ANY clustered-domain KB deployment (medical, legal, scientific) will exhibit
propagation = 0.341 under unclustered retrieval -- 1.7x the 0.20 safety threshold.

The rescue paths are algebraically grounded and implementation-ready. RESCUE-A (MMR) is the highest-
priority empirical test because: (a) it is the cheapest implementation (~20 lines Python, no
retraining), (b) it has the strongest lit-precedent (Carbonell-Goldstein 1998), (c) the algebraic
prediction is propagation < 0.10 post-MMR. If confirmed, this upgrades the grounding-robustness cap
row from HARD_FAIL to CONDITIONAL PASS.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue capacity)

### Anchor 1: MMR-diversified retrieval rescue (RESCUE-A empirical confirmation)
- **Anchor pointer:** notes/research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md
  Section 2 RESCUE-A; and G8 original empirical setup (rho_cluster=0.75, k=10, M=100 patterns)
- **Substrate-product reading:** MMR reranking (lambda=0.5) over G8-equivalent clustered KB; measure
  propagation vs G8 baseline (0.341). If propagation < 0.10: grounding-robustness row upgrades to
  CONDITIONAL PASS (MMR required). This is the gate for any clustered-domain production deployment.
- **Tier hint:** Local or CPU (no model training; post-retrieval reranking only; fast)
- **Why now:** Cheapest decisive test; algebraic prediction is unambiguous; production gate

### Anchor 2: MMR lambda sweep + rho_cluster curve
- **Anchor pointer:** Section 4 of research note (propagation-vs-rho_cluster pre-registered predictions)
  + RESCUE-A cells R-A2/R-A3 (lambda sweep [0.3, 0.5, 0.7] x rho_cluster [0.4, 0.6, 0.8])
- **Substrate-product reading:** Maps the safe operating region for MMR. Identifies whether lambda=0.5
  is sufficient or higher lambda required for tight clusters (rho > 0.75). Pre-reg: rho < 0.30 is
  safe without MMR; rho > 0.30 requires MMR at lambda >= 0.5.
- **Tier hint:** CPU (3x3 grid, 9 cells, ~2 min each; ~18 min total)
- **Why now:** Second cheapest test; provides the operating envelope map

### Anchor 3: Inverse-density reweighting (RESCUE-B empirical)
- **Anchor pointer:** Section 2 RESCUE-B of research note (density-weighted retrieval; cell R-B1)
- **Substrate-product reading:** Alternative to MMR that operates via item-weight modulation rather
  than greedy reranking. If both RESCUE-A and RESCUE-B confirm propagation suppression, we have two
  independent production-grade mitigations -- important for deployment flexibility.
- **Tier hint:** CPU (density estimation adds ~1ms per query; single-config test)
- **Why now:** Independent rescue cross-check; low cost; validates the density-signal hypothesis

### Anchor 4: Cluster-density confidence calibration (RESCUE-D empirical)
- **Anchor pointer:** Section 2 RESCUE-D of research note (cell R-D1; Brier score calibration check)
- **Substrate-product reading:** Measures whether cluster_density_score predicts propagation rate
  (calibrated confidence output). This is a non-blocking product feature: even if RESCUE-A/B/C are
  not deployed, a calibrated propagation_risk flag in the API surface adds observable value at
  near-zero cost.
- **Tier hint:** Local or CPU (single density computation per query; fastest possible cell)
- **Why now:** Production API surface candidate; lowest cost of all rescue cells

---

## Context pointers (file paths, not summaries)

- notes/research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md (this research note)
- notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md (Refutation-4: COINCIDENTAL
  for correlated KBs; G8 closes that gap)
- G8 original verdict: data/exp_<G8_anchor_name>/metrics.json (exp_dev knows the anchor name)

---

## Contract

exp_dev owns: anchor naming, queue routing, sweep grid design, threshold band selection, ETA,
smoke vs full profile decision, pre-reg format, post-ship verification.

Research provided: mechanism analysis, ranked rescue paths with P_deflated, falsifiable predictions
with HP/MID/HF pre-reg at the CONCEPTUAL level, cross-domain lit-scan. The numerical threshold
values in the research note are ALGEBRAIC PREDICTIONS, not mandated pre-reg bounds -- exp_dev
sets the actual experimental thresholds per its own pre-reg discipline.

## Autonomy declaration

exp_dev decides independently: which subset of the 4 anchor candidates to ship, in which order, at
which queue tier, and with what profile parameters. Orchestrator approval required only if the
combined dispatch exceeds the authorized cloud cost envelope or requires paused-queue override.
