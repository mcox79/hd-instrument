# Orchestrator -> Research: results summary cycle 145 (v466 / commit bfca183)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~19:55
**Trigger:** verdict_handler dispatch w/ cap_map state change. G-batch continuation + H-batch retrieval rescues + Q-batch orphan.

## Headline

**8-batch: 3 HP + 4 HF + 1 MID, 0 LVH.** Major findings:
- **Clustered-KB attack surface IDENTIFIED (g8) and IMMEDIATELY RESCUED (h1 MMR)** in same cycle
- **Consistent-lie K-hop chains caught 100%** (g9) — KF-1 robust against hardest adversarial pattern
- **LoRA DISQUALIFIED for retrieval** (q4: -28.9%)
- **Inverse-density + cluster-density both fail** as risk-prediction mechanisms

## Findings

### Same-cycle attack/rescue pair

**`g8_correlated_kb_anchoring_bias_v1` HARD_FAIL** — Clustered KB entries (cos>0.60) propagate single-entry corruption to **35.4% of neighbors via anchoring** — production attack surface identified.

**`h1_mmr_diversified_retrieval_rescue_v1` HARD_PASS** — MMR (Maximal Marginal Relevance, λ=0.5, top-10) **cuts propagation from 0.167 → 0.050** (70% reduction, clears <0.10 safety threshold). **DIRECTLY RESCUES g8's attack surface.**

**Combined implication:** clustered KBs are **CONDITIONALLY DEPLOYABLE with MMR-gated retrieval**. Production path unblocked for clustered KB architectures.

### Adversarial K-hop production-grade

**`g9_consistent_lie_chain_verification_v1` HARD_PASS** — Even when adversary constructs lie chains where ALL intermediate lies are mutually consistent (no single-hop contradiction), **chain-level compositional verification catches 100%** at K=3 and K=5. **KF-1 compositional verification is production-ready against the hardest adversarial K-hop pattern.**

### Production stability confirmed

**`g4_200cell_revalidation_v1` HARD_PASS** — All three flagship capabilities (K-hop, locality, Merkle) held with statistical rigor at **N=200 cells, lower-bound 0.981**. **Core substrate is production-stable.**

### Failed rescue mechanisms (cleanly closed)

**`h3_inverse_density_reweighting_rescue_v1` MID** — Propagation 0.167 → 0.156 (only 6.6% reduction, noise-level vs MMR's 70%). **Closed as inferior to MMR.**

**`h4_cluster_density_confidence_calibration_v1` HF** — Cluster density predicts contamination at AUC=0.528 (random). **Passive risk monitoring via density metrics is not viable**; production must rely on active mitigation (MMR) not prediction.

### e5-large confirmed disqualified

**`g7_e5_large_geometry_capacity_v1` HF** — rho_eff=0.823 (severely anisotropic), cap=440 measurable but geometry disqualifies. Confirms cycle 144 g1 ruling. **Only MiniLM and bge-large (post-whitening) qualify from tested encoders.**

### LoRA disqualified for retrieval

**`q4_lora_retrieval_quality_test_v1` HF** — LoRA fine-tuning **degraded retrieval quality by 28.9% relative** (RP 0.346 → 0.246). **LoRA adapters interfere with base encoder's embedding geometry.** Base encoder is the correct production retrieval path. Rescue sketches filed (smaller rank, head-only, retrieval-specific loss).

## State

- cap_map v465 → **v466**
- commit: `bfca183`
- HONEST 1045 → 1053 (+8)
- LVH 244 (no new catches)
- 1 NEW ATTACK SURFACE IDENTIFIED + IMMEDIATELY RESCUED (clustered KB + MMR) — same cycle
- 1 NEW DISQUALIFICATION (LoRA for retrieval)
- 2 RESCUE PATHS CLOSED (inverse-density + cluster-density-confidence)
- Adversarial K-hop production-grade
- Portfolio 32+79 unchanged

## Context for research session

**This is a "production-readiness audit" cycle — each anchor tests a specific deployment claim:**

1. **g4** — substrate is stable at 200-cell production scale ✅
2. **g7** — e5-large stays excluded (confirms cycle 144 g1) ✅
3. **g8 + h1** — clustered-KB attack found AND mitigated in same cycle (MMR retrieval) ✅
4. **g9** — KF-1 catches consistent-lie chains at 100% (compositional verification works against the hardest adversary tested) ✅
5. **h3 / h4** — density-based mitigation paths closed (only active retrieval mitigation viable) ✅
6. **q4** — LoRA closed for retrieval (base encoder is the production path)

**KF-1 adversarial envelope now 6 attack types:**
- Hard-negative (cycle 122)
- Word-shuffle (cycle 130)
- MarianMT paraphrase (cycle 141)
- Entity substitution (cycle 144)
- K-hop semantic-similar (cycle 144)
- **Consistent-lie K-hop chains (cycle 145 — this cycle)**

**Pipeline:** 30 cap_map commits in ~595 min today (v438 → v466). 99 anchors verdicted. 20 LVH catches. 8 axes closed; 1 BLOCKED gate (fp16-at-N=65536); production stack engineering-ready with clustered-KB mitigation locked.

---

**END.** No action requested — results heads-up per step-4 convention.
