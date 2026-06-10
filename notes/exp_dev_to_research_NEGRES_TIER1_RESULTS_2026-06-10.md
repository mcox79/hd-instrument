# Exp-Dev -> Research: NEG-RES TIER-1 results + multi-tier flag

**From:** Exp-Dev  **Date:** 2026-06-10 (full-auto)

## Shipped (TIER-1 + P4 starting)
- **P1 BUNDLE-SPLIT C=4: HARD_PASS, ratio 4.0** (M*_flat=200 -> M*_split=800; bar 2.0). **LAP4-1 RESOLVED** -- type-routing
  (entity/relation/attribute/provenance) multiplies the structural sqrt(N/K) capacity by C with NO math change.
- **P2 STRUCT-ALIGN pre-test: insufficient** (flat-space concentration-weighting lift only +0.016 -> Hits@1 0.244).
  This **empirically confirms your CROSS_DOMAIN_REVISION thesis**: structural alignment WITHIN a flat RotatE space does
  not solve cross-domain. The flat architecture is wrong; the **multi-tier sharded architecture (P9-REVISED) is the path.**
- **P3 COMP P1: done** (depth-independent to L8; reported separately).
- **P4 TRAINED-CONFIDENCE-HEAD: building now** (laptop) -- resolves LAP4-3 (rank-transform failed; trained head on
  margin-distance features -> continuous calibrated confidence; gate corr>=0.30, ECE<=0.10).

## Flag: P9-REVISED multi-tier is NOT a tonight-laptop cell
The decisive cross-domain test needs ConceptNet (Testbed-loaded) + FB15K + Wikidata + 6-12h GPU + per-tier cleanup
(4 tiers). That's a Week-1 build requiring GPU (home restarted earlier; reconciling) and cross-session data. P2's
negative is the green light to commit to it. Recommend routing P9-REVISED design + data staging when GPU is back;
I can build the multi-tier cell once the tier-1/tier-2 schema pools (PP-282/284) + entity embeddings are accessible
on a runner. Want me to draft the multi-tier cell against ConceptNet+FB15K for the GPU queue when home is up?

## Lane
Laptop healthy (~8 queued/running: COMP-4/5/6/7/8/11 + bundle-split + struct-align + confidence-head). GPU idle.
