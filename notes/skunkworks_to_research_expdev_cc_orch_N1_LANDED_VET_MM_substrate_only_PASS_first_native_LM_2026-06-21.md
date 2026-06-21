# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: N1 LANDED-VET = MIDDLE_BAND honest baseline + SUBSTRATE-ONLY gate PASSES (verified off cell code). The FIRST substrate-native LM EXISTS + is genuinely substrate-only + beats unigram. + instrumentation flag for the N2 chain-grade run.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T23:33:37Z
**Cell:** exp_n1_concept_lm_substrate_native_token_decode_v3_1 (full, 3-seed; v2/v3 were broken iterations [bpc 1614 / inverted bigram] -- v3_1 canonical).

## RESULT (off verdict_msg; per_unit NOT exposed -- see flag)
substrate_bpc=5.00 | unigram=6.33 | bigram=3.84 | ceiling=2.70 | distillation_gap=2.30 bits | sub_top1=0.433 (uni 0.276 / big 0.473).
=> **beats unigram (5.00<6.33 = captures real structure) but NOT bigram (5.00>3.84).** Per my N3 absolute-floor bands: NOT HARD_PASS (HARD_PASS = sub < bigram) -> **MIDDLE_BAND.** Honest first baseline -- matches my prior + the ~bigram concept-seed (sub_top1 0.433).

## SUBSTRATE-ONLY GATE: PASS (THE load-bearing check -- verified off cell code, not the report)
- Decode = sparse-codebook cleanup (argmax C@activated) + count-based decode-memory D (argmax D.T@concept_vec) -- numpy, NO torch model forward at inference (cell lines 269-274 "Substrate-native: no LLM head, no transformer inference").
- BOUNDARY (lines 24-25): Pythia-160m runs ONCE at INGEST (residuals -> VQ codebook); NOT called at inference. = exactly the ingest-then-native pattern (USER-endorsed).
- => the substrate-native LM is GENUINELY substrate-only (no external transformer at inference). The USER's core requirement is MET. The MIDDLE_BAND is a real substrate-only result, not LLM-in-the-loop.

## INSTRUMENTATION FLAG (required before the N2 chain-grade run)
metrics.json detail={} + per_unit=[] (empty) -> I could NOT recompute BPC off per_unit NOR get cv. For MIDDLE_BAND the tier is clear off verdict_msg, but a future CHAIN-GRADE N2 run (beats-bigram) MUST expose: (a) per_unit BPC + cv<=0.05; (b) the zero-LLM-call assertion LOGGED in metrics (not just a code-comment) -- a landed-VET must audit it from data; (c) the VQ-floor decomposition (concept-transition-BPC + within-concept-entropy) per my N1 SCHEMA-VET. Exp-Dev: add these to the cell's metrics for N2.

## MILESTONE (positive, honest)
The FIRST substrate-native LM exists, is substrate-only-verified, and beats unigram -> the USER's substrate-native vision is FEASIBLE. The gap to bigram (and the 2.30-bit ceiling gap) is N2's job -- the coupled levers I de-risked: context-depth x codebook-granularity (floor-masks; dfb41903) + VQ-quality. N1 = the honest baseline; N2 = push past bigram.

## Tier + next
MIDDLE_BAND (substrate-only PASS; beats-unigram-not-bigram). 4-layer: L1-me off cell-code+verdict_msg (per_unit unavailable -> flagged). Not chain-grade (doesn't beat bigram) -> honest baseline, NOT a forced pass. Reactive: N2 levers (Research drill) + the instrumentation fix for the chain-grade run. CERT 583/177266 (MIDDLE_BAND CERT-neutral).

-- Skunkworks
