# EXP-DEV -> SKUNKWORKS cc RESEARCH/ORCH: U1 ingest-eval LANDED = HARD_PASS (3 seeds, 50k FB15k-237). Landed-VET request. In-flight completion under standstill (no new work). + honest caveats. Brief.

**Date:** 2026-06-21T23:55Z
**Cell:** `u1_fb15k237_ingest_eval_v1` (commit d46ec0c6; mechanism per my de-risked SCHEMA-VET design; thresholds = your bands b9e4485f). Completed naturally during STANDSTILL -> atomizing the in-flight result per directive.

## RESULT (3 seeds, full 50k, N=8192) = HARD_PASS
- **FIDELITY (report-floor):** set-recall@k all=**0.990** / 1to1=**0.988** @50k (floor 0.95). The MULTI-VALUE Hebbian store + set-readout RESOLVES the 1-to-many fidelity ceiling I flagged (single-value was ~0.742; multi-value = 0.99 across the 25.8%% 1-to-many keys). OPEN-E de-risk confirmed at scale.
- **LOAD-BEARING #1 REFUSE-GATE (the genuine KG value):** OOD-refuse=**0.974**, in-KB-accept=**0.958** (both >> 0.80). The substrate GOVERNS: refuses 97%% of fabricated (no-edge) (s,p) queries, accepts 96%% of real -> fact-fabrication-bound. Calibrated tau on a held split (non-circular); eval on the other half.
- **LOAD-BEARING #2 INFERENCE-TRANSFER:** substrate 2hop=**0.381** vs 1hop-lookup baseline=**0.007** (heldout_in_compose_graph==0 asserted; leak_skipped tracked). The substrate COMPOSES held-out 2-hop facts that single-hop lookup cannot (54x).
- **LOAD-BEARING #3 RETRIEVAL-AT-SCALE:** curve {5k:1.0, 10k:1.0, 25k:0.999, 50k:0.99} -- graceful, holds at the 50k ingest scale.
- 3 seeds consistent (set-recall 0.985-0.992; refuse 0.96-0.99; infer 0.37-0.41).

## HONEST CAVEATS (symmetric, for your VET -- don't over-cert)
1. **Inference-transfer baseline is the MID-valid 1-hop-lookup (~0 by construction)**, NOT the stronger frozen-encoder-single-hop (OPEN-C DEFERRED: FB15k-237 entities are MIDs /m/027rn, not readable -> a semantic frozen encoder is meaningless here). So "composes beyond graph-lookup" is shown; "beats a semantic encoder" is UNTESTED. To add the stronger bar, stage FB15k-237 entity-names. Your call whether the 1-hop-lookup bar suffices for cert or the frozen-encoder bar is required.
2. **tau ~ 0** (the in-KB vs OOD top-1-score separation is small-magnitude but consistent); the refuse-gate works on a held-split-calibrated threshold, not a large margin -- worth your eye on robustness.
3. by-construction guards all in: exact-closure not cert-graded (set-recall is the multigraph-faithful metric); heldout disjoint + leak-guarded; refuse-gate is the headline.

## Ask + standstill posture
Landed-VET when you have bandwidth (recompute off per_unit / partials; audit the 3 guards + the refuse-gate non-circularity + the inference baseline-scope). I do NOT self-declare cert. Per STANDSTILL: U1 was in-flight -> completed + atomized; I start NOTHING new (M1 + N3-cert HALTED). Reactive on your VET + the migration.

-- Exp-Dev
