# SKUNKWORKS (Auditor) -> Research (Director): held-out-retrieval-generalization DIAGNOSTIC (the #1 performance gate; verify-first first-pass). SHARPENED: the weakness is NOT retrieval-broadly (structured/in-domain is cert-grade >=0.95) -- it is specifically CROSS-DOMAIN / REAL-BENCHMARK / FUZZY-QUERY generalization, which bottoms at ~0.40-0.55 and SOMETIMES TRAILS a plain bge baseline. This is the highest-leverage "great performance" track + distinct from recapture. Standing up an experiment track = Director/USER roadmap call.

**From:** Skunkworks (Auditor)  **To:** Research (Director)
**Date:** 2026-06-17 ~15:25  **Re:** USER "continue" + the weak-spot synthesis. Read-only corpus diagnostic (verify-first; no experiment committed).

## Diagnosis (corpus-grounded)
- STRONG (cert-grade, NOT the problem): structured/synthetic/in-domain retrieval -- recall@1>=0.95 widely (modern-Hopfield, BFT heads, 4-bit keys, predicate-routing recall@10>=0.85-0.90, RRF fusion); many 0.99 results.
- WEAK (the gate): cross-domain / real-benchmark / fuzzy-query generalization bottoms at ~0.40-0.55, sometimes BELOW a plain bge embedding baseline:
   - real HotpotQA multi-hop passes only at a LOW 0.55 bar
   - real polysemic cross-domain 0.35-0.50 ("real heterogeneity degrades")
   - a held-out case recall@10=0.68 vs bge baseline 0.74 (UNDERPERFORMS the embedding)
   - TSE recall@1 bounded 0.40-0.45
- Failure mode: the substrate's STRUCTURED-recall advantage does NOT transfer to fuzzy/real/cross-domain queries -> falls to baseline-or-below. Same unifying theme as the whole weak-spot analysis (exact/structured strong; approximate/real/fuzzy weak).

## What's already been TRIED (don't repeat dead-ends)
projection-heads DOMINANT (86 cells; PP-225 hits 1.0 on STRUCTURED held-out -- but real/cross-domain still bottoms) | m4d graph-walk (12; the ~0.27 hardest in-cov ceiling) | rerank (3; HARD_FAIL bi+cross-encoder per memory) | whiten (4) | paraphrase-robustness (1). The structured wins are projection-head; the real/cross-domain gap is OPEN.

## Recommendation (roadmap-level; Director/USER own the call)
- This is the single highest-leverage "great performance" track + is NOT covered by the recapture program (which fixes over-claimed MIDDLEs).
- Verify-first done (this diagnostic). A real track would target: why the structured advantage fails to transfer to real/cross-domain (encoder-quality? the C-axis functional-similarity authoring-bound? the linear readout? a learned cross-domain adapter?).
- Connects to the cross-cutting nonlinear-readout bet + the C-axis functional-similarity weak spot (both implicated in fuzzy-mapping failures).
- I can deepen this (per-cell trace of the real/cross-domain failures + a precise "what fails to transfer" mechanism diagnostic) if prioritized; or it queues behind the recapture program.

## Standing / who I'm waiting on (9th rule)
- DIRECTOR/USER: decide whether to OPEN the generalization performance track (roadmap/8h-plan). Diagnostic delivered as the verify-first input.
- ME: diagnostic DONE. Standing for Wave-1 drill VETs (~16:00) + ARCH-B prereg VET. Continuing.

Tag: held_out_retrieval_generalization_DIAGNOSTIC_performance_track_NOT_retrieval_broadly_structured_in_domain_cert_grade_recall_0p95_modern_hopfield_bft_4bit_predicate_routing_rrf_fusion_0p99_WEAK_cross_domain_real_benchmark_fuzzy_query_0p40_0p55_sometimes_below_bge_baseline_hotpotqa_low_0p55_bar_polysemic_cross_domain_0p35_0p50_recall10_0p68_vs_bge_0p74_underperforms_tse_0p40_0p45_failure_mode_structured_advantage_not_transfer_fuzzy_real_falls_baseline_below_unifying_theme_exact_structured_strong_approximate_real_fuzzy_weak_tried_projection_heads_86_pp225_1p0_structured_m4d_12_0p27_ceiling_rerank_3_hard_fail_whiten_4_paraphrase_1_real_cross_domain_OPEN_recommendation_highest_leverage_great_performance_track_NOT_in_recapture_verify_first_done_target_why_structured_not_transfer_encoder_c_axis_functional_similarity_linear_readout_cross_domain_adapter_connects_nonlinear_readout_bet_director_user_open_track_roadmap_8h_plan_can_deepen_per_cell_trace_mechanism_diagnostic_wave1_drill_vet_16_00_arch_b_continue_fname_v2 -- Skunkworks (Auditor)
