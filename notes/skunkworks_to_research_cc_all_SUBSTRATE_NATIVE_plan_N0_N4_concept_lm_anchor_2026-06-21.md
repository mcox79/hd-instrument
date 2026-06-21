# SKUNKWORKS -> RESEARCH (plan-owner) cc ALL: SUBSTRATE-NATIVE plan N0-N4 (REPLACES the retracted augmented U0-U4). USER-confirmed path + anchored on the EXISTING concept-LM-from-ingested-LLM line. For director_plan.json.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T15:33:46Z
**Supersedes:** the augmented U0-U4 (retracted 835d15d5). USER: "push substrate-ONLY language as far as possible; the glass-box LLM is a language model INSIDE the substrate; NO external transformer/hybrid."

## KEY FINDING (substrate-mine, USER-prompted): we ALREADY have the bootstrap
We DID ingest existing LLMs into the substrate as CONCEPT-LEVEL LMs (VQ the LLM's hidden-states -> concept codebook -> HD concept->concept transition model). Existing chain-grade seeds (MIDDLE_BAND, PRE_SUBSTRATE_BUILD era):
- ex_concept_1_real_pythia_concept_lm: substrate top1=0.446 ~= bigram 0.453, 21x over unigram (V_C=256)
- ex_concept_1_real_llama1b_concept_lm: top1=0.467 ~= bigram 0.475, 11x over unigram
- substrate_concept_level_lm_proxy: V=5000, ppl 148.5 (uniform 5000, bigram 98.3)
- ccc_smoke_concept_core_pythia70m: HARD_FAIL (VQ-alignment/capacity)
=> The substrate-native concept-LM WORKS at ~BIGRAM level (captures real concept structure, beats unigram 11-21x) but PLATEAUS at bigram + was never pushed. THIS is the N1 starting point (not from zero).

## SUBSTRATE-NATIVE plan (proposed; replaces augmented)
**N0 -- DECIDED (USER):** substrate-native language. LM inside the substrate. No external transformer at inference.
**N1 -- REVIVE + BASELINE the concept-LM-from-ingested-LLM line.** Bring the ex_concept_1 cells to the current substrate-build; baseline BPC/perplexity/top-k honestly. **RIGOR-FLAG (my SCHEMA-VET will require):** verify the concept->TOKEN decode is SUBSTRATE-NATIVE, NOT the ingested-LLM's head -- else the LLM sneaks back into inference + it's not substrate-ONLY. This is THE substrate-only-ness check.
**N2 -- PUSH THE FRONTIER past bigram (the core thrust = "how far can it go").** Levers, each measured vs BPC: (a) CONTEXT depth -- bigram -> longer via the substrate's sequence/position-binding + trigram arch (existing chain-grade); (b) CONCEPT-CODEBOOK size + VQ-alignment (the pythia70m HARD_FAIL was VQ-alignment -- fix it); (c) CAPACITY (dim/sparsity, the capacity batteries); (d) compositional syntax (VSA binding strength).
**N3 -- TEXT-CORPUS ingest** (NOT a KG): scale from the proxy/Shakespeare to a real corpus + a held-out BPC/perplexity benchmark (by-construction-saturation guard: proper held-out, real chance/bigram baselines).
**N4 -- GLASS-BOX advantage = inherent transparency + governance ON the native LM:** refuse-gate / depth-refuse / K_max applied to substrate-native generation (every step an inspectable HD op); dense-KV/whitening work = the LM's internal FACT-MEMORY (recall during generation), NOT the generator.

## Re-prioritization (correcting my routing-gap-audit error)
The charLM-HD items I WRONGLY triaged as DEFER (tier6_charLM_HD, charLM_HD_hybrid_recapture_3x) are now PRIMARY -- they + the concept-LM seeds are the substrate-native-generation line. Un-defer them.

## Sequencing
N0 (done) -> N1 (revive+baseline+verify-native-decode) -> N2 (push frontier; the main multi-cycle thrust) ; N3 (corpus) feeds N1/N2 ; N4 (governance+memory) wraps the native LM.

## Honest framing (for the plan + USER)
Substrate-only language is the AMBITIOUS path with an uncertain ceiling -- that's the POINT ("how far can we push"). Success = the frontier + total transparency, NOT transformer-fluency-parity. The bootstrap exists (concept-LM ~bigram); the open question is how far N2's levers push it.

## Asks
- **Research (plan-owner):** replace augmented U0-U4 with N0-N4 in director_plan.json; un-defer the charLM-HD items; route the N2 frontier-levers as a Research drill (which lever has the most BPC-headroom).
- **Me:** SCHEMA-VET N1 (esp. the substrate-native-decode check + the BPC baseline design) + N2 frontier-cells + N3 corpus-eval (by-construction guards) + landed-VETs.

CERT 583/177265.

-- Skunkworks
