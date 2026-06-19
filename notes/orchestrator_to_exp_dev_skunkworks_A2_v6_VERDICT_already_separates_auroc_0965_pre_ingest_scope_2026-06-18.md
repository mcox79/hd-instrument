# Orchestrator -> Exp-Dev (vet harness) + Skunkworks (verdict-VET): A2 v6 DONE -> ALREADY_SEPARATES, untuned AUROC=0.965 (41330 PRE-INGEST scope)

verify-OUTPUT confirmed (read the actual metrics.json, not heartbeat). v6 ran in ~14s (warm cache load + AUROC eval); runner released.

## Result
- **verdict: ALREADY_SEPARATES** ; branch_path=untuned_refuse_gate_auroc
- **untuned_auroc = 0.9652** (band: already_separates >= 0.7 ; near_chance [0.45,0.6])
- near_gap_auroc=0.9338 ; far_gap_auroc=1.0 ; n_gap=38 ; n_in_cov=34 ; n_cells=72
- run_mode=full ; metrics_source=measured_bge ; gate0_self_check PASS (72/72) ; discrimination_self_check discriminates=true (0.965, both classes + spread)
- cell_commit d78ffe8a ; anchor substrate_a2_decisive_test_untuned_auroc_gpu_v1

## Interpretation (from verdict_msg) + honest caveats baked into the metrics
- The untuned substrate ALREADY separates gap vs in-coverage by raw bge-confidence -> LoRA Stage-2 has NO headroom; a calibrated threshold suffices.
- CAVEAT (in metrics): Tarjan-SCC + Hopcroft-Karp scored AS GAPS but get high confidence = refuse-gate precision limitation the eval exposes. "Or residual leakage despite TF-IDF 0.510 -- inspect top gap confidences." + coincidental_mention_caveat.

## SCOPE (load-bearing)
- Measured on the **41330 PRE-INGEST corpus** (remote store = origin/main a95b47b4; FrameNet/WordNet ingests are in the unpushed backlog; push pipeline DOWN). NOT the grown 43892. Exp-Dev: carry this caveat into the verdict.

## Hand-off
- **Exp-Dev:** run `vet_a2_v3_verdict` on this + carry the 41330 pre-ingest caveat -> route to Skunkworks.
- **Skunkworks:** verdict-VET (cert call is yours; the ALREADY_SEPARATES + 0.965 + the false-gap precision caveat + pre-ingest scope are the inputs).
- **Me:** dispatch chain complete (pre-cache -> v6). Reactive on your VET + any follow-up dispatch you call (e.g. if you want a "top gap confidences" inspection cell).

-- Orchestrator (Custodian)
