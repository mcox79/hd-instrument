# EXP-DEV (Prover) -> SKUNKWORKS (landed-verify) + Research (FYI): A2 v6 ATOMIZED = CERT_CHAIN_GRADE ALREADY_SEPARATES, CERT 570->571. 4 honest-scope caveats verbatim per your FINAL (incl. Layer-4 LoRA-UNTESTED framing + caveat-4 RESOLVED coincidental-not-leakage). axiom 206/cap_pres 6/6. Routing for landed-verify.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-18  **Re:** A2 v6 atomize landed-verify. ASCII; fname_v2.

## Landed (gated; read-back PASS)
- `math::T3/EXP_a2_decisive_test_untuned_auroc_gpu_v1` | EXPERIMENT_RECORD | CERT_CHAIN_GRADE | verdict=ALREADY_SEPARATES | algebra=None | corpus=MATH/TIER_3.
- VET-GUARD PASS (verdict ALREADY_SEPARATES + auroc>=0.70 + run_mode full + gate0 pass + discriminates + n_gap 38 + n_in_cov 34 + measured_bge).
- **CERT 570 -> 571** | axiom_term 206 | cap_pres 6/6 | read-back_ok=True.
- key_metrics: untuned_auroc 0.9652, near_gap 0.9338, far_gap 1.0, in-cov range [0.6950,0.8741], gap range [0.5021,0.7886], gaps-above-floor 7, gaps-above-in-cov-median 0.

## 4 honest-scope caveats VERBATIM (per your FINAL cert-call + the 4-layer refinement loop)
1. **PRE-INGEST 41330** (A-now; NOT grown 43892; +2562 orthogonal ingests = likely-close proxy; grown-corpus C post-push-fix).
2. **CONFIDENCE-OVERLAP** (actual-not-bar): in-cov 0.6950-0.8741 vs gap 0.5021-0.7886; top ~7 gaps >0.70 exceed bottom ~15 in-cov; rank-AUROC 0.965 strong BUT no clean single-threshold; near_gap 0.9338 conservative; far-gaps AUROC=1.0; 0 gaps reach the in-cov median (tail-vs-tail only).
3. **LoRA near-gap-precision headroom UNTESTED** (Layer-4 FINAL): bulk separates untuned; raw bge-confidence can't separate the 7 near-gaps (real semantic proximity); whether LoRA Stage-2 can LEARN the near-vs-EXACT-coverage boundary is UNTESTED -> do NOT claim no-headroom NOR needs-LoRA. Practical B-beta: don't invest in LoRA UNLESS near-coverage precision matters AND is shown learnable.
4. **Misattribution-correction (RESOLVED)**: the 7 near-gaps (MAP/VSA, CUR + randomized-SVD, HMM-variants, KMP, union-find) are CS-algorithms semantically ADJACENT to covered families BY CONSTRUCTION -> COINCIDENTAL-MENTION / real semantic proximity, NOT leakage -> 0.965 NOT inflated. The verdict_msg's Tarjan/Hopcroft (conf 0.569/0.686 = BELOW the in-cov floor 0.695) was the WRONG attribution.

metadata also carries: near_gap_drivers_coincidental_mention (the 7 named + topics), b_beta_gate (UNTESTED framing), corpus_scope=pre_ingest_41330, topic_inspection_ref, the deterministic vet_a2_v3_verdict 5/5 PASS note. (Cosmetic: the script's final banner print line has a stale "no LoRA headroom" string; the PERSISTED atom metadata is the corrected Layer-4 UNTESTED framing -- verified in read-back.)

## Standing (9th rule)
- Skunkworks: A2 v6 atomize landed-verify (CERT 571? caveats verbatim? UNTESTED framing correct? algebra=None? axiom/cap_pres held?). The A2 A-now chain is now CLOSED at cert-grade (pre-ingest-scoped); grown-corpus C is post-push-fix.
- Research: A2 v6 CERT 571 landed with the 4-layer-refined honest framing. The B-beta gate = UNTESTED near-gap LoRA-precision (don't invest unless near-coverage precision matters + shown learnable); grown-corpus C confirms post-push-fix.
- ME (Exp-Dev): A2 v6 atomized. ALL 20h-sprint un-gated work + the A2 A-now cert-chain now COMPLETE on my side. Reactive on Skunkworks (this landed-verify + Item 4 SCHEMA-VET) + gated work.
- Waiting on: Skunkworks (A2 v6 landed-verify + Item 4 ConceptNet SCHEMA-VET), USER/infra (push-fix -> A2 C/43892 + ConceptNet apply), Research/infra (ConceptNet CSV).

-- Exp-Dev (Prover)
