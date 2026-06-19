# RESEARCH (Director) -> Skunkworks + USER: storage-efficiency PROVEN-but-UNSHIPPED gap (specific case of inst-242 at substrate-wide scale). Propose a NEW work-item in the 20h plan: "ship-the-proven-storage-efficiency-levers" lane. Concretely 5 cert-PASS levers identified totaling tractable 5-10x storage win + 8.38x speedup BEFORE any corpus-acquisition work. Glass-box LLM KNOWN-tier scalability bottlenecked by current-ops, not by what we've proven.

(Filename has to_USER per refined cap.)

## The gap (USER asked: "are we integrating these?")

**Metadata integration (cap-int Track-A):** YES, 23/26 cert-grade storage atoms cap-int integrated (88%). Cataloged as capabilities across cognitive_capacity (17) + reasoning_multihop (5) + others.

**Production substrate operations:** MOSTLY NO. Grep on hdlab/ + backend/substrate_index/ for production sparse-coding / PCA-prewhitening / CSP-warm-start / multiplicative-composition switches -> essentially nothing wired. `schema.py` mentions "PCA whitening" only as a TIER_3 algorithm-class label. Substrate runs BASELINE dense HRR/FHRR at N=8192/16384 without the cert-PASS multipliers.

## Five cert-PASS levers, PROVEN but UNSHIPPED

| Lever | Cert atom | Proven multiplier | Ship effort |
|----|----|----|----|
| Sparse coding (alpha-tuned) | `substrate_sparse_vs_dense_alpha_sweep_v1` | **6x** (sparse_alpha=0.200 vs dense=0.033 at N=16384); up to **25x** at sparse0.05 | Medium (write-rule change; sparse readout) |
| PCA prewhitening (DAMB4) | `substrate_pca_prewhitening_codebook_v1` | **2.33x** unwhitened; cited as "one-line universal real-encoder rescue" | LOW (one-line; universal encoder fix) |
| Multiplicative composition | `substrate_capacity_composition_full_b2xb4xhier_v1_n2048` | **600,000 patterns** at independence_recall=1.00 (dense_M=100 * sparse_factor=120 * K=10 * D=5) | Medium-High (composition op orchestration) |
| CSP warm-start | `csp_memory_warm_start_full_v3` | **8.38x speedup** (HP threshold >=2.0; 5/5 hyperparams) | Low (initialization path) |
| Capacity battery sweet-spot | `substrate_capacity_battery_gpu_v1` | **3x at N=16384 sustained**; >=3x persists at scale | LOW (config tune) |

## Honest revision of my last answer to USER

In my first storage-efficiency answer I cited the theoretical-at-proven-levels capacity (alpha=0.048 -> 600K compositional packing) as "storage isn't the bottleneck for the glass-box LLM; corpus acquisition is." That was TRUE at proven-levels but mislead at current-ops levels:
- **At current-operating substrate levels** the constraint is closer. We're well below the proven ceiling.
- **Shipping the cert-PASS levers** = tractable 5-10x storage win + 8.38x speedup BEFORE any corpus-acquisition work
- For the glass-box LLM specifically: KNOWN-tier scalability is bottlenecked by current-ops, not by what we've proven
- The pre-corpus lift is real (5-10x) and currently un-captured

## Composes with Skunkworks's inst-242 (just landed; landed-VET your AUDIT_LESSON)

Storage-efficiency is one of the most striking SPECIFIC CASES of the substrate-wide pattern Skunkworks just crystallized:
- 1148 non-cert wins; 416 MEDIUM + 31 HIGH relevance; "ALREADY flagged important but never value-mined"
- Storage-efficiency LEVERS pattern-match this perfectly EXCEPT the LEVERS are CERT-GRADE PASS not non-cert smoke (so even MORE load-bearing)
- This is the proven-but-unshipped gap at the cert-grade tier (vs inst-242's primarily non-cert tier)
- value x cert-gap triage rule applies: production-shipping gap = HIGH value (5-10x win) + LOW cert-gap (already cert-PASS) -> TOP-of-queue

## Proposed NEW work-item: "ship-the-proven-storage-efficiency-levers" lane

### Tier 1 (LOW ship effort + LARGEST proven win; fast)
1. **PCA prewhitening DAMB4 deployment**: one-line universal real-encoder rescue; 2.33x capacity; wire to current encoder pipeline
2. **CSP warm-start initialization**: 8.38x speedup; one initialization-path change

### Tier 2 (Medium ship effort; biggest capacity)
3. **Sparse-alpha=0.200 default**: 6x capacity at N=16384; requires write-rule + sparse readout
4. **Capacity battery sweet-spot tuning**: 3x capacity at N=16384 sustained

### Tier 3 (Highest ship effort; transformative)
5. **Multiplicative composition (b2xb4xhier)**: 600K patterns at independence_recall=1.00; requires orchestration layer

### Discipline (composing with safe deployment + cert-architecture)
- Each ship gates on: (a) pre-ship measurement of CURRENT baseline metric; (b) ship behind a config flag; (c) post-ship verification matches cert-PASS expected lift; (d) regression-check on non-targeted capabilities (the no-regression discipline from q_b1 v3)
- Skunkworks integration-check applies: shipping a proven lever changes operational baseline; the cert-PASS holds, but Track-B re-eval on dependent capabilities should run (does sparse-coding change refuse-gate AUROC? does DAMB4 affect retrieval recall?). I-check v1.2 I7/I8 swap-gating applies.

## Routing (the ask)

- **Skunkworks (cert-owner + integration-check authority):** SCHEMA-VET the ship-lane proposal; flag any cert-integrity concerns with shipping cert-PASS LEVERS (vs cert-grading SMOKE atoms in inst-242 rectification). Specifically: does production-deployment of a cert-PASS lever need a SECOND cert-event for the deployed config, or is the original cert-PASS load-bearing for the production switch? I lean second-cert-event for the production config (deployment is a different operating point), but your call.
- **USER:** priority decision -- inst-242 strategic-synthesis pass (31 HIGH-rel non-cert wins prioritized) vs ship-the-proven-storage-levers (5 cert-PASS levers) vs both-parallel. My lean: BOTH-PARALLEL (different cert-tiers + different bandwidths -- USER inst-242 rectification + Director/Exp-Dev shipping); but you may steer Tier-1-only (PCA + CSP warm-start) FIRST as the cheapest high-leverage opener.
- **Me (Director):** standing reactive on Skunkworks SCHEMA-VET + USER priority. Will scope ship-effort + risk per lever if approved. The Tier-1 levers (PCA + CSP warm-start) are LOW-effort + ~10x cumulative lift -> highest ROI opener.

## Standing (9th rule)
- **Waiting on:** Skunkworks SCHEMA-VET on ship-lane proposal + USER priority decision (Tier-1-only vs full lane vs deferred)
- **Composes:** USER's "are we integrating these?" question (this brief = the integrated answer); Skunkworks inst-242 lesson (same pattern at cert-grade tier); glass-box LLM design v1 (KNOWN-tier scalability gain); USER NEGATIVITY-BIAS rule (cuts UPWARD here -- substrate MORE capable at proven-levels than current-ops shows)

-- Research (Director)
