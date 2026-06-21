# ORCHESTRATOR -> ALL: driving N1 cell authoring NOW (USER "implement the plan"). VERIFY-THE-REFERENT finding sharpens the N1 rigor flag. N1 routes to remote_cpu_queue (full npz is remote-only).

**From:** Orchestrator
**Date:** 2026-06-21T15:43Z

## Verify-the-referent finding (off data + code, not the report)
The existing concept-LM bootstrap `ex_concept_1_real_pythia_concept_lm_v1` is REAL but is a next-CONCEPT predictor, NOT yet a token LM:
- `metrics.json`: substrate_top1 = 0.446 ~= bigram_markov 0.453, 21x over unigram 0.021, MIDDLE_BAND. CONFIRMED off data.
- The cell scores next-CONCEPT-ID accuracy (argmax over a random bipolar codebook of cleanup(W @ C[concept_t])). It has **NO concept->token decode** anywhere (cell line 127).

## This sharpens the N1 substrate-only-ness gate
Skunkworks's N1 rigor-flag was "verify the concept->TOKEN decode is substrate-native, not the LLM head." Sharper truth: **there is no decode yet.** N1 must ADD a substrate-native concept->token decode AND measure a real TOKEN-level metric (bits-per-token / perplexity), with the LLM's LM-head kept out of inference entirely. That is exactly where "substrate-only" bites.

## Data availability
Local `data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/` has ONLY `metrics.json` (1.3KB); the full `residuals_per_token.npz` lives on the remote runner (marsh@home). => **N1 dispatches to remote_cpu_queue** (no local copy to clobber-check; no GPU contention with the whitening run).

## Lane (single-session dispatch; no ambiguous parallel)
- **Orchestrator:** driving the N1 cell authoring now (reproduce next-concept baseline + ADD substrate-native concept->token decode + token-level BPC vs token-unigram/bigram/analytic-ceiling). I dispatch on land.
- **Exp-Dev (session):** take N2 frontier-levers prep + N3 corpus scope. Do NOT duplicate N1.
- **Skunkworks:** N1 SCHEMA-VET will need (a) the token-level BPC pre-registered band and (b) the substrate-native-decode mechanism check (no LLM head in inference). Codebook is LLM-derived at INGEST = acceptable; transition + decode must be substrate-native at INFERENCE.

-- Orchestrator
