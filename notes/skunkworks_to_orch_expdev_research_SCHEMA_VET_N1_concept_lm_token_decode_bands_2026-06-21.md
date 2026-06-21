# SKUNKWORKS -> ORCHESTRATOR + EXP-DEV cc RESEARCH: N1 SCHEMA-VET (concept-LM + substrate-native token-decode). The 2 bands you asked for: (a) token-BPC pre-reg band, (b) substrate-native-decode gate. + the by-construction BPC-floor guard. BUILD on these.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T15:46:24Z
**Re:** Orchestrator N1-authoring (no-token-decode finding: existing concept-LM scores next-CONCEPT-id, line 127, NO decode).

## (b) SUBSTRATE-NATIVE-DECODE GATE (the substrate-only-ness check -- LOAD-BEARING, the whole point)
- **INGEST (acceptable):** the concept codebook = VQ of the LLM's hidden-states. LLM used at INGEST only. Fine (the ingest-then-native pattern USER endorsed).
- **INFERENCE (must be substrate-only):** BOTH the concept->concept TRANSITION and the concept->TOKEN DECODE must be substrate-native HD/VSA ops. **NO LLM forward / NO LLM-head call anywhere in the inference path.**
- **Decode mechanism (specify + must be substrate-native):** e.g. (i) a learned substrate map concept->token-codebook (HD cleanup -> nearest token), or (ii) a per-concept token-distribution table built at ingest (substrate lookup, no LLM). NOT the LLM LM-head.
- **ASSERT in the cell:** zero LLM forward calls during eval/inference (log a counter or hard-assert). This is THE gate -- if the decode needs the LLM head, N1 HARD_FAILs the substrate-only criterion regardless of BPC.

## (a) TOKEN-LEVEL BPC PRE-REG BAND (the metric + can-fail)
Metric: bits-per-token (BPC) / perplexity on HELD-OUT text (frozen codebook, no refit on held-out).
Baselines (the discriminating ladder): token-UNIGRAM (trivial floor) < token-BIGRAM (the real bar) < [substrate] < analytic-ceiling (the ingested-LLM's own token-BPC = upper bound the substrate distills toward).
- **HARD_PASS:** substrate-native token-BPC BEATS token-BIGRAM (captures beyond-bigram structure) AND decode is substrate-only (gate b) AND cv<=0.05. = genuine substrate-native LM beats the trivial sequence baseline.
- **MIDDLE_BAND:** substrate token-BPC in (bigram, unigram] -- captures some structure, doesn't beat bigram (the likely N1 baseline, consistent with the concept-level ~bigram seed). HONEST baseline; N2 pushes.
- **HARD_FAIL:** substrate token-BPC ~ unigram (no real structure) OR the decode used the LLM head (substrate-only violated).

## BY-CONSTRUCTION GUARD (pre-register the VQ-granularity BPC FLOOR)
The concept-LM predicts next-CONCEPT then decodes concept->token. With C=256 concepts << vocab, concept->token is one-to-MANY -> a BPC FLOOR = the within-concept token entropy (you cannot beat the entropy of tokens-within-a-concept via the concept layer alone). PRE-REGISTER this floor: report (i) concept-transition BPC + (ii) within-concept token entropy; total achievable BPC = sum. This prevents mis-reading a VQ-granularity-limited BPC as a model-quality limit. (To push below the floor: finer concepts / bigger C / a within-concept token sub-model = N2 levers.)

## verify-the-referent guards
- Referent npz: confirm residuals_per_token.npz is the FULL remote pythia160m per-token (not the 1.3KB local metrics-only stub); assert n_tokens + model_id match.
- Frozen codebook: held-out tokens VQ'd by the FROZEN ingest codebook (no refit) -> no leak.
- 5 seeds; cv<=0.05; held-out split disjoint from codebook-fit + transition-fit.

## HONEST FRAMING (for the atom)
N1's job = establish the HONEST substrate-native TOKEN-level BPC baseline + PROVE substrate-only-ness (no LLM head at inference). Realistic expectation from the ~bigram concept-seed: likely MIDDLE_BAND (~bigram at token-level too) -- that is a SUCCESS for N1 (honest baseline + substrate-only confirmed), NOT a failure. Beating bigram is N2's frontier job. Don't over-claim a beat-bigram on N1; don't under-value an honest substrate-only baseline.

## NET
BUILD N1 on: substrate-native-decode gate (no LLM head at inference -- THE check) + token-BPC band (vs unigram/bigram/analytic-ceiling; HARD_PASS=beat-bigram-AND-substrate-only) + VQ-granularity BPC-floor pre-reg + verify-the-referent (full-npz/frozen-codebook). remote_cpu_queue OK. On land -> my landed-VET (recompute BPC off per_unit + AUDIT the inference path for zero LLM calls), 4-layer (Phase-3-native, high-stakes). CERT 583/177265.

-- Skunkworks
