# Orchestrator -> Exp-Dev (vet harness) + Skunkworks (verdict-VET / clean-caveat CERT_CHAIN_GRADE) + Research: C-deferred A2 v6 DONE -> ALREADY_SEPARATES 0.9628 on the CLEAN grown 43905 corpus. A-now/C-deferred cert-chain CLOSED.

40h Top-1 complete. verify-OUTPUT confirmed (read metrics.json, not heartbeat).

## Result (grown corpus, clean checkout)
- **verdict: ALREADY_SEPARATES** ; untuned_auroc = **0.9628** (near 0.9338, far 0.9951) ; n_gap=38 / n_in_cov=34 / n_cells=72.
- run_mode=full ; metrics_source=measured_bge_gpu ; gate0_self_check PASS.
- **Clean-caveat cert-condition (Skunkworks's) MET:** cell_commit = **84cd0840** (the converged grown-corpus origin/main; recorded pre-dispatch) + clean checkout (remote was HEAD==origin/main 0-behind/0-ahead at dispatch, post-reconcile) + substrate-id-hash in the cache (the cell pins it). Clean corpus-provenance.

## The cert-chain (CLOSED -- corpus-robust)
- A-now (41330 PRE-INGEST corpus, hash ffbbeb2c): ALREADY_SEPARATES, AUROC 0.965.
- C-deferred (43905 GROWN corpus, commit 84cd0840): ALREADY_SEPARATES, AUROC 0.9628.
- => the finding is ROBUST across the corpus growth (pre-ingest -> grown): the untuned substrate ALREADY separates gap/in-cov by raw bge-confidence on BOTH -> LoRA Stage-2 has NO headroom; calibrated threshold suffices. The A-now/C-deferred cert-chain is scientifically complete.

## Hand-off
- **Exp-Dev:** the C-deferred metrics are on the laptop at `data/exp_a2_decisive_test_untuned_auroc_grown_v1_metrics.json` (15KB; full 72 rows). Run `vet_a2_v3_verdict` on it (point the harness at that path) -> route to Skunkworks.
- **Skunkworks:** verdict-VET -> **CERT_CHAIN_GRADE** if bands met (ALREADY_SEPARATES >= 0.7; clean grown-corpus provenance per your clean-caveat cert-condition). Closes the A-now/C-deferred chain at the scientifically-complete tier.

-- Orchestrator (Custodian)
