# Research -> Exp-Dev: Batch H AUTHORIZED -- G8 MMR rescue (4 cells; ~35 min CPU; $0)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~10:15
**Re:** exp_dev_handoff_research_clustered_KB_anchoring_propagation_2x_2026-06-07.md (G8 rescue 2x drill)
**Subject:** User authorized Batch H. 4 cells implement MMR / inverse-density / cluster-density confidence rescue paths for G8 GENUINE security finding. CPU; $0; ~35 min total.

---

## User authorized Batch H

Per G8 rescue 2x drill: clustered-KB anchoring propagation is the day's one GENUINE security finding (the only Drill C adversarial prediction that survived empirical refutation). Drill ranks MMR (Carbonell-Goldstein 1998) as primary rescue with algebraic prediction propagation 0.341 -> <0.10.

---

## 4 cells (ranked by drill priority)

### H1: MMR-diversified retrieval (RESCUE-A primary)
- **Anchor pointer:** research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md Section 2 RESCUE-A; G8 original setup (rho_cluster=0.75, k=10, M=100 patterns)
- **Why now:** CHEAPEST decisive test; ~20 lines Python; no retraining; strongest lit precedent
- **Test:** MMR reranking (lambda=0.5) over G8-equivalent clustered KB; measure propagation vs G8 baseline 0.341
- **Wall:** ~5 min CPU
- **HP:** propagation < 0.10 (confirms primary rescue; G8 row -> CONDITIONAL PASS with MMR mitigation)
- **MID:** 0.10-0.20 (partial rescue; document constraint)
- **HF:** > 0.20 (MMR insufficient; escalate to RESCUE-B/D)
- **Strategic value:** Production gate decisive

### H2: MMR lambda x rho_cluster operating envelope
- **Anchor pointer:** drill note Section 4 + RESCUE-A cells R-A2/R-A3
- **Why now:** Maps safe deployment region; identifies operating envelope for production
- **Test:** 3x3 grid lambda in {0.3, 0.5, 0.7} x rho_cluster in {0.4, 0.6, 0.8}; measure propagation per cell
- **Wall:** ~18 min CPU (9 cells, ~2 min each)
- **Strategic value:** Tells deployment teams when MMR is required vs optional

### H3: Inverse-density reweighting (RESCUE-B)
- **Anchor pointer:** drill note Section 2 RESCUE-B; cell R-B1
- **Why now:** Independent rescue mechanism cross-check; low cost
- **Test:** Density-weighted retrieval over G8-equivalent clustered KB
- **Wall:** ~5 min CPU
- **Strategic value:** Two independent production-grade mitigations gives deployment flexibility

### H4: Cluster-density confidence calibration (RESCUE-D)
- **Anchor pointer:** drill note Section 2 RESCUE-D; cell R-D1
- **Why now:** Production API surface candidate; lowest cost
- **Test:** Measure whether cluster_density_score predicts propagation rate (Brier score)
- **Wall:** ~5 min CPU
- **Strategic value:** Even if H1/H2/H3 don't deploy, calibrated propagation_risk flag adds observable value at near-zero cost; client-facing safety feature

---

## Total estimate

- Sequential CPU: ~35 min
- Parallel CPU: ~18 min
- Cost: $0 (no GPU; no cloud)

---

## Strategic value

### If H1 confirms (propagation < 0.10)
- G8 grounding-robustness row upgrades from HARD_FAIL to CONDITIONAL PASS
- Production deployment for clustered-domain KBs (medical, legal, scientific) gets documented mitigation
- The day's one genuine adversarial security finding gets a clean engineering answer
- Comparison table updates: clustered-KB anchoring becomes "production-deployable with MMR diversification"

### If H2 maps safe envelope
- Deployment teams get clear guidance on when MMR is required
- rho_cluster threshold for safety identified
- Production API can flag high-risk queries

### If H3/H4 confirm independent rescue
- Two/three independent mitigation paths gives deployment flexibility
- API surface includes cluster-density propagation_risk flag

---

## Cross-references

- G8 verdict (HARD_FAIL): exp_dev_to_research_batchG_complete_F123_mismatch_2026-06-07.md
- G8 rescue drill full: research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md
- G8 rescue exp_dev handoff: exp_dev_handoff_research_clustered_KB_anchoring_propagation_2x_2026-06-07.md
- Drill C adversarial adaptive (which identified clustered-KB risk): research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds (per your judgment within drill's algebraic predictions), queue assignments. Pre-reg per envelope-fail-band protocol. ASCII-only.

H1 is the production gate; ship it first. H2 maps envelope. H3/H4 are parallel independent rescues.

## Autonomy

You may:
- Combine cells if more efficient (e.g., H1 + H2 in single sweep)
- Skip H3/H4 if H1 confirms strongly (propagation < 0.05 means single rescue is sufficient)
- Add adjacent rescue cells if intermediate results suggest follow-ups

---

**END.**

**Exp-Dev:** Batch H authorized (4 cells; ~35 min CPU; $0). H1 MMR is the production gate. If propagation < 0.10 confirmed: G8 row upgrades to CONDITIONAL PASS; clustered-KB deployment unblocked with documented mitigation.

**User:** Batch H (4 cells) routed to Exp-Dev. Closes today's one genuine adaptive security finding with known-art rescue (MMR Carbonell-Goldstein 1998). $0; ~35 min.

**Orchestrator + Testbed:** Visibility only.
