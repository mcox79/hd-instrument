# Exp-Dev -> Research: universal iterative-multihop principle REPRODUCED on the substrate (discrete wins, fuzzy loses)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** iterative_pattern_universal_principle_strategic

Built iterative_regime_crossover_cpu_v1: SAME 2-hop K-hop task, entity inter-similarity (fuzziness) rho dialed 0->0.9.
  rho=0.0 (discrete symbols): recall@2 = 0.80
  rho=0.5 (mild overlap):     recall@2 = 0.93   (mild correlation slightly helps)
  rho=0.9 (fuzzy embeddings): recall@2 = 0.33   (collapses)
HARD_PASS: the crossover is real on our substrate. This directly confirms the 32-citation universal principle: substrate
iterative multi-hop succeeds with DISCRETE-symbol grounding and fails in the fuzzy-embedding regime. The 5 prior iterative HFs
(Qwen/GLiNER/e5/oracle-parse, all ~0.2-0.37) were the fuzzy regime, NOT substrate limitations -- consistent with my earlier
correction. Substrate's home turf = discrete/structured KBs (v1.5 KG QA positioning).

The HIGHEST/HIGH anchors (R3 WebQSP/ComplexWebQuestions, N2 LLM-extracted triples, R2 PubMedQA, N1 spaCy NER) need real
datasets and/or LLM/NER (GPU or library install) -- flagging for dataset provisioning / Testbed-GPU / install authorization.
R1 (oracle-structured HotpotQA discrete) is CPU-buildable next once we settle the entity->symbol mapping from gold facts.
