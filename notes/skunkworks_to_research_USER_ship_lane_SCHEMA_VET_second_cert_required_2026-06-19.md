# SKUNKWORKS (cert-owner) -> RESEARCH + USER: ship-the-proven-levers lane SCHEMA-VET = APPROVE the concept (value x cert-gap at the CERT tier; proven-but-unshipped is real + high-value; composes inst-242). CERT-RULING on your question: YES -- each production deployment REQUIRES a SECOND cert-event for the deployed config. The LOAD-BEARING reason isn't just "different operating point" -- it's that shipping a lever CHANGES the operational baseline for ALL other capabilities, which can invalidate cert atoms certified against the OLD baseline (EXACTLY the PART_OF-revert cert-integrity break I'm reconciling RIGHT NOW). So the second cert-event MUST include a DEPENDENT-CERT-ATOM regression-check. Tier-order refined by regression-RISK. (Filename has to_research_USER.)

**From:** Skunkworks (cert-owner)  **To:** Research + USER  **Date:** 2026-06-19  **Re:** ship-lane SCHEMA-VET + the second-cert-event ruling.

## APPROVE the ship-lane concept
The proven-but-unshipped gap is real + high-value: 5 cert-PASS levers (sparse 6-25x, PCA 2.33x, multiplicative 600K, CSP warm-start 8.38x speedup, capacity 3x) integrated as CAPABILITIES but NOT wired into production substrate ops (runs baseline dense). This is the value x cert-gap rule at its strongest: HIGH value (5-10x) + LOW cert-gap (already cert-PASS) -> top-of-queue. Composes inst-242 (same proven-but-unsurfaced pattern, here at the CERT tier = even more load-bearing).

## CERT-RULING: second cert-event REQUIRED per deployed config (your lean confirmed -- and STRENGTHENED)
You leaned "second-cert-event because deployment is a different operating point." Correct -- AND there's a stronger, load-bearing reason I just learned the hard way THIS turn:
1. **Different operating point:** the original cert-PASS proves the lever at its TESTED point (specific N, alpha, benchmark). Production is a different point -> the cert-PASS does NOT auto-transfer. The deployed config needs its own PASS (does the lever deliver the proven lift AT the production point?).
2. **THE LOAD-BEARING REASON -- substrate-state-consistency (the PART_OF-revert lesson, live RIGHT NOW):** shipping a lever CHANGES the operational baseline for ALL OTHER capabilities. Every other cert atom (refuse-gate AUROC, retrieval recall, the depth-cliff, the BROAD envelope) was certified against the CURRENT (dense/baseline) state. Ship sparse-coding or PCA, and those atoms' cert-claims may NO LONGER HOLD -- the IDENTICAL failure mode as the +125 PART_OF edges reverting and breaking `partof_broad_after`. A substrate-state change can silently invalidate downstream cert atoms.
- => **the second cert-event MUST include a DEPENDENT-CERT-ATOM REGRESSION-CHECK:** before flipping a lever to production-default, run the affected cert atoms (refuse-gate / retrieval / depth-cliff / etc.) under the NEW baseline + confirm their cert-claims still reproduce. Any that break get re-VET'd (downgrade or re-scope), not silently left stale.

## Tier-order REFINED by regression-RISK (not just ship-effort)
The regression-check SCOPE scales with how much the lever changes the REPRESENTATION:
- **CSP warm-start (8.38x SPEEDUP, init-path):** LOWEST regression-risk -- a speedup/initialization change doesn't alter the representation, so few dependent-cert-atom interactions. **Ship FIRST** (cheapest + safest opener; the regression-check is small).
- **PCA prewhitening (2.33x, encoding):** MEDIUM risk -- changes the ENCODING -> moderate dependent-cert-atom interactions (retrieval/refuse-gate run on encoded vectors). Regression-check the encoder-dependent cert atoms.
- **Capacity sweet-spot (3x, config tune):** LOW-MEDIUM (a config tune; check the capacity-dependent atoms).
- **Sparse-coding (6-25x) + Multiplicative composition (600K):** HIGHEST risk -- change the REPRESENTATION fundamentally -> the BROADEST regression-check (most cert atoms operate on the representation). Ship LAST + most carefully (full dependent-cert-atom sweep).
=> your Tier-1 (PCA + CSP) is right as the opener, but lead with **CSP warm-start** (lowest regression-risk), then PCA. The representation-changers (sparse/multiplicative) need the full regression sweep before they go default.

## Per-ship discipline (composing your list + the regression-check + v1.2)
1. pre-ship: measure the CURRENT baseline metric (the operating point you're changing from).
2. ship behind a config flag (reversible).
3. post-ship: production-point re-validation (lever delivers the proven lift at the production point) = the SECOND cert-event.
4. **DEPENDENT-CERT-ATOM regression-check** (the load-bearing add): the affected cert atoms still reproduce under the new baseline (or re-VET).
5. integration-check v1.2: if the ship changes a capability's current_best (a swap), I7/I8/I9 gate it; the deployed-config cert-event is recorded as the new current_best.

## USER priority input
Both-parallel is cert-fine (inst-242 strategic-synthesis [USER bandwidth] + ship-lane [Director/Exp-Dev bandwidth] are different tiers + lanes). My cert-lean on the ship-ORDER: **CSP warm-start FIRST** (8.38x speedup, lowest regression-risk -- proves the ship-discipline cheaply), then PCA, then the representation-changers with full regression sweeps. Each gated by the second-cert-event + regression-check.

## Routing
- Research: scope ship-effort + the dependent-cert-atom regression-set per lever (which cert atoms does each lever's representation/encoding change touch?). I'll define the regression-check cert-protocol (the pre/post + dependent-atom sweep) -- it's the same protocol I'm building for the PART_OF reconciliation (a substrate-state change -> re-verify dependent cert atoms). One protocol, two uses.
- ME: define the substrate-state-change cert-protocol (covers BOTH the PART_OF re-apply AND the lever-ships) + verdict-VET each deployed-config cert-event.
- USER: priority (both-parallel / Tier-1-only / defer). My lean: both-parallel, CSP-first.

-- Skunkworks (cert-owner)
