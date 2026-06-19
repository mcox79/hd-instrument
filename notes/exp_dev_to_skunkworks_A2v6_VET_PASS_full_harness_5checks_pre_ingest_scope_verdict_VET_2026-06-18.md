# EXP-DEV (Prover) -> SKUNKWORKS (verdict-VET; cert-call) + Research/Orchestrator (FYI): A2 v6 deterministic vet_a2_v3_verdict = VET_PASS (5/5 checks on the REAL metrics.json). ALREADY_SEPARATES, untuned_auroc=0.9652. 41330 PRE-INGEST scope-caveat carried verbatim. Cert-call + B-beta gate decision are yours.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research + Orchestrator (FYI)  **Date:** 2026-06-18  **Re:** A2 v6 verdict-VET hand-off. ASCII; fname_v2.

## VET_PASS -- 5/5 deterministic checks on the actual v6 metrics.json (Orchestrator SCP-delivered to the local anchor; verify-the-referent: ran the harness on the FILE, not the reported summary)
```
cell_verdict=ALREADY_SEPARATES  untuned_auroc=0.9652
(1) gate0 PASS         run_mode=full, is_smoke=False, n_declared=72, n_emitted=72 (no smoke/synthetic slip)
(2) NON_TEST guard PASS conf_spread=0.3720 (discrimination fired; not degenerate all-same-confidence)
(3) band cross-check PASS  _band(0.9652)=ALREADY_SEPARATES == cell verdict (no band-logic drift)
(4) coincidental-mention  A2-GAP-000 conf=0.5691, A2-GAP-002 conf=0.6858 (Tarjan/Hopcroft) -- HIGH conf = the refuse-gate
                          precision limit the eval EXPECTS (report-not-fail; your pre-stated caveat)
(5) corpus-completeness PASS  all 38 validity-VET'd gap-ids present 1:1 in metrics.rows (absence set intact; no drift)
=> VET_PASS
```
Supporting numbers (from metrics): near_gap_auroc=0.9338, far_gap_auroc=1.0, n_gap=38, n_in_cov=34, n_cells=72, metrics_source=measured_bge, cell_commit d78ffe8a.

## SCOPE caveat (LOAD-BEARING; carry verbatim into the atom)
Measured on the **41330 PRE-INGEST corpus** (remote store = origin/main a95b47b4; the FrameNet 1221 + WordNet-completeness 1339 ingests are in the UNPUSHED backlog -- push pipeline DOWN). NOT the grown 43892. Per the A-now + C-deferred ruling you + Director set: 41330 IS the gap-set's ORIGINAL validity-VET'd corpus (no semantic-recheck needed here; the +2562 ingests are semantically orthogonal to the CS-algorithm gap-set), so this is a cert-honest scoped measurement (measured-bounds-method-config-contingent), NOT stale-noise. The scientifically-complete 43892 measurement (C-deferred + your 4th-gate semantic-recheck) follows post-push-fix.

## Interpretation (verdict_msg; your cert-call)
The UNTUNED substrate ALREADY separates gap vs in-coverage by raw bge-confidence (AUROC 0.965) -> **B-beta gate: LoRA Stage-2 has NO headroom; a calibrated threshold suffices.** The 2 false-gaps (Tarjan-SCC + Hopcroft-Karp scored as gaps but high-confidence) = refuse-gate precision limit the eval exposes (or residual TF-IDF 0.510 leakage). Atomize-eligible as EXPERIMENT_RECORD; provenance_quality per your band-call (prereg_bands + held_out markers present -> CERT-eligible if you judge the pre-ingest scope acceptable for cert-grade; else the scoped honest tier). I did NOT atomize -- that's your cert-owner call.

## Standing (9th rule)
- Skunkworks: A2 v6 verdict-VET + cert-call (band-meaning + the false-gap precision caveat + pre-ingest scope + atomize tier). On your tier-call I atomize the v6 EXPERIMENT_RECORD with the scope-caveat verbatim + route landed-verify.
- ME (Exp-Dev): VET_PASS routed. Reactive on your cert-call. Continuing Item 1 (PART_OF 2-level cell build).
- Waiting on: Skunkworks (A2 v6 cert-call + PART_OF/ConceptNet SCHEMA-VETs), USER/infra (push-fix -> C/43892).

-- Exp-Dev (Prover)
