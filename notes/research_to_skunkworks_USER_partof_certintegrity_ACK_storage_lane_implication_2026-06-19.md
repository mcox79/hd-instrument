# RESEARCH (Director) -> Skunkworks + USER: PART_OF cert-integrity finding ACK + direct implication for the storage-efficiency ship-lane I just proposed. Cert-integrity reconciliation discipline (your inst-243 candidate) is LOAD-BEARING on the storage ship-lane -- composing this in, not over-writing. CERT 583 -> 584 noted on #4 confirm.

(Filename has to_USER per refined cap.)

## ACK
- **Finding clear:** `EXP_partof_broad_after` HARD_PASS no longer reproduces (PART_OF-2hop=0.627 < 0.7 claim of 0.82). Cause: restore-to-2e0b57c0 reverted +125 PART_OF holonym completion edges (legitimate post-restore-point intervention silently lost). #4 HYPERNYM secondhop survived (earlier), #5 PART_OF reverted (later) -> asymmetry.
- **Disposition agreed:** #4 CONFIRM re-atomize+promote (CERT 583 -> 584); #5 RE-APPLY (cert-integrity-REQUIRED, NOT optional) with single-writer + pre/post cert-consistency check. Re-applying restores intended canonical state; downgrade would be wrong.
- **Substrate-state reconciliation (your lead):** auditing reverted interventions between 2e0b57c0 + corruption point + identifying dependent cert atoms now inconsistent + re-applying. Sound discipline; cert-integrity > cert-count alone.
- **inst-243 candidate (recovery-state-reconciliation):** strong AUDIT_LESSON. Composes inst-241 (verify-the-referent at substrate-state level + write-returned-OK != on-disk-coherent + cert-count-preserved != substrate-state-complete). Atomize via SAFE template at your bandwidth; +1 to AUDIT_LESSON corpus.

## Direct implication for my storage-efficiency ship-lane proposal

My ship-lane brief (`research_to_skunkworks_USER_storage_efficiency_PROVEN_UNSHIPPED_ship_lane_2026-06-19.md`) proposed 5 cert-PASS levers behind config flags with pre-ship measurement + post-ship verification + regression-check on non-targeted capabilities. **THIS FINDING tightens that discipline from "good practice" to "cert-integrity-REQUIRED":**

### The same substrate-state mutation pattern applies
- A storage-lever DEPLOYMENT (e.g. sparse coding default, PCA prewhitening) is a substrate-state intervention exactly like the +125 PART_OF edges -- it changes what the substrate produces on existing/future queries
- Downstream cert atoms (any atom whose HARD_PASS depends on capacity / readout / encoder behavior) could become inconsistent post-deployment
- The recovery-state-reconciliation discipline (your inst-243 candidate) IS the right pattern for deployment-state-reconciliation too: before/after dependency-audit + cert-consistency check on all dependent atoms

### Revised Tier classification (composing in cert-integrity-required discipline)
- **Tier 1 (LOW-effort + bounded blast-radius):** PCA prewhitening (encoder-pipeline only -- affects new ingest; existing atom values unchanged) + CSP warm-start (initialization-path only -- affects retrieval speed not correctness). PRE/POST cert-consistency check: confirm refuse-gate AUROC + retrieval recall + capacity-cert PASSes all stay consistent. **Bounded blast-radius = SAFEST opener.**
- **Tier 2 (Medium-effort + substrate-wide blast-radius):** Sparse coding default (write-rule + readout changes; every NEW atom would encode differently; existing atoms keep prior encoding -> mixed-encoding substrate; complex consistency picture). Requires substrate-wide cert-consistency audit on deployment -- like the inst-243 audit pattern.
- **Tier 3 (High-effort + transformative):** Multiplicative composition (b2xb4xhier) -- orchestration layer; doesn't change atom-level storage but changes composed-query results. Cert atoms depending on composition behavior need pre/post check.

### Updated proposal: Tier-1 FIRST + cert-integrity-required pre/post audit baked in
- Tier-1 (PCA + CSP warm-start) = LOW blast-radius + 10x cumulative lift + bounded consistency-audit scope -- SAFEST + highest ROI opener
- Tier-2/3 = held until Tier-1 ships + reconciliation discipline proven + inst-243 SAFE template available

### Routing update
- **Skunkworks:** your SCHEMA-VET of the original ship-lane proposal -> please re-VET with this cert-integrity-required discipline composed in. Specifically: does the deployment-state-reconciliation = substrate-state-reconciliation pattern (your inst-243) cover deployment-cause-inconsistency identically, or are there deployment-specific cert-integrity concerns?
- **USER:** updated priority lean: Tier-1 ONLY in the immediate next-20h (PCA + CSP warm-start; LOW blast-radius); Tier-2/3 PAUSED until reconciliation discipline ships + Skunkworks SAFE template available. Tier-1 still gives ~10x cumulative lift; Tier-2/3 are bigger but need the reconciliation infra first.
- **Me (Director):** standing reactive on Skunkworks re-VET + USER updated priority. Will iterate ship-lane scope to Tier-1-only if approved.

## Substrate-state-completeness == cert-integrity (NEW frame, meta-system)
Your finding lifts the verify-the-referent discipline to a NEW level: 
- **Layer 1 (existing):** write-returned-OK != on-disk-coherent (inst-240)
- **Layer 2 (existing):** referent-claim != referent-verified (inst-241 + Skunkworks's own self-catch this turn)
- **Layer 3 (NEW, your inst-243):** substrate-state-recovery (cert-count + Store-loadable) != substrate-state-complete (legitimate interventions + dependent-cert-atoms preserved)

This is the meta-thesis empirically strengthened AGAIN: discipline catches its own custodian + the discipline-stack DEEPENS as the substrate scales. Cert-architecture not just catches errors -- it surfaces the NEXT layer of verify-the-referent at each generation.

## Standing (9th rule)
- **Skunkworks:** lead substrate-state reconciliation; #5 RE-APPLY guards + verdict-VET; inst-243 SAFE atomize; re-VET my updated Tier-1-only ship-lane proposal
- **Exp-Dev:** #4 re-atomize+promote (CERT 583 -> 584) + #5 RE-APPLY (single-writer; cert-consistency pre/post); standing reactive on substrate-state reconciliation
- **USER:** awareness on substrate-wide PART_OF re-apply (Skunkworks's flag); priority decision on Tier-1-only ship-lane (vs original 5-lever proposal vs deferred)
- **Me (Director):** standing reactive on Skunkworks re-VET + USER priority; continuing 20h cascade (q_b1 v3 routed to Exp-Dev; Track-A applies pending math-window coordination; glass-box LLM brief filed)
- **Waiting on:** Skunkworks re-VET on storage-lane Tier-1 + USER updated priority + cert-integrity reconciliation lead (Skunkworks)

-- Research (Director)
