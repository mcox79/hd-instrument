# Research -> Exp-Dev: 2x drill gap fills (cycle 178 negatives)

**From:** Research  **Date:** 2026-06-08 ~02:30  **Re:** Self-audit identified 3 cycle 178
negatives without explicit 2x drill response. Filling per always-research-negatives-2x rule.

## Gap 1: bundle_capacity_cliff_gpu HF (cycle 178)

### Cycle 178 result
- K_crit=200 at N=4096 (0.049N; borderline 0.05 miss)
- Orchestrator framed as "predictable, consistent with √(K-1)"
- HF vs HP threshold of 0.05N; HYPOTHESIS that this matches √(K-1) theory not empirically
  verified

### Anchor: bundle capacity cliff theory-empirical alignment test
- Substrate-product reading: predict K_crit = 0.05 × N × correction-factor; verify
  whether 0.049N at N=4096 matches √(K-1) prediction; test at N=8192 + N=16384 to map
  scaling curve
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: K_crit/N at N=4096/8192/16384 follows √(K-1) within 5%; capacity cliff is
  predictable scaling-law not architectural blocker
- HARD-FAIL: K_crit/N drops as N scales (cliff worsens at production scale)

If HP: cap_map row updates to "K_crit = sqrt(K-1) predictable" — engineering plans
around it.
If HF: bundle capacity needs structural intervention before production.

## Gap 2: resonator K=4 capacity still 0.427 (cycle 178 partial rescue)

### Cycle 178 result
- M-reduction rescue: K=3 0.70 → 0.84 at M=20 (+0.14 partial)
- K=4 still 0.427 (well below threshold)
- Untested: combined N-increase + M-reduction; alternative resonator init schemes;
  resonator at higher iteration count

### Anchor: resonator K=4 multi-axis rescue
- Substrate-product reading: combine N=4096 (vs 2048) + M=20 (vs 30) + higher iteration
  count (e.g., 50 vs 20 default); also test alternative resonator init (warm-start from
  query embedding vs random)
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: K=4 recall >= 0.70 at combined-axis rescue
- BORDER: 0.50-0.70 (partial; might need further parameter search)
- HARD-FAIL: < 0.50 even with combined rescue (K=4 fundamentally limited at production
  N regardless of params)

If HP: resonator viable through K=4 for structured-KB multi-hop with combined-axis
config.
If HF: resonator K-hop is K=2/3-only; multi-hop chains beyond 3 hops need different
mechanism (substrate K-hop direct without resonator factorization).

## Gap 3: mycorrhizal multi-hub coverage still below gate (cycle 178)

### Cycle 178 result
- Multi-hub rescue: 0.41 → 0.62 (+0.21 partial)
- Below 0.70 HP gate
- 911 unique hubs identified; rescue path was "more hubs or better selection" per cycle
  175 footer

### Anchor: mycorrhizal multi-hub similarity-weighted rescue
- Substrate-product reading: weight hub selection by similarity to new-customer's KB
  centroid (vs uniform random hub selection in cycle 178); also test variant with
  per-domain hubs (medical/legal/financial domain-specific seeds)
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: similarity-weighted multi-hub achieves >= 0.70 topic coverage at Q=100
- BORDER: 0.62-0.70 (partial improvement; might need combined per-domain + similarity-weighted)
- HARD-FAIL: < 0.62 (multi-hub mechanism inherently limited; cross-customer warm-start
  needs different mechanism)

If HP: federated warm-start v2.0 capability validated; substrate-as-hub multi-tenant
mature.
If HF: cross-customer transfer is empirically intractable beyond ~60% topic coverage;
substrate ships with per-customer cold-start as production path.

## Cross-references

- Cycle 178 bundle_capacity_cliff HF: notes/orchestrator_to_research_results_summary_2026-06-08_cycle178.md
- Cycle 178 resonator_capacity_rescue MID: same cycle
- Cycle 178 mycorrhizal_multihub MID: same cycle
- Original 2x drill gap fills routing: notes/research_to_exp_dev_2x_negatives_FILL_2026-06-07.md
- Memory rule: feedback-always-research-negatives-2x-strict

---

**Exp-Dev:** authorize all 3 anchors per always-research-negatives-2x rule. Bundle
capacity cliff is the most strategic (validates √(K-1) scaling-law claim or surfaces
production blocker). Resonator K=4 rescue determines structured-KB multi-hop depth.
Multi-hub similarity-weighted rescue determines cross-customer warm-start ceiling.
All CHEAP LOCAL CPU tests (~2-3 hr each).
