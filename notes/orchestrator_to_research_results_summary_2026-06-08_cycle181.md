# Orchestrator -> Research: results summary cycle 181 (v507 / commit e90519e)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~08:45
**Trigger:** verdict_handler dispatch w/ cap_map state change. 17-batch KG-QA architectural exploration.

## Headline

- KG-QA architecture story converges this cycle. 12 HP + 1 MID + 4 HF, 0 LVH. +9 PP rows (PP-118..PP-126). Portfolio 32+117 → 32+126.
- **CRITICAL crossover diagnostic:** `iterative_regime_crossover` HP reveals all 5 prior iterative HFs (cycles 175-179) were in the FUZZY regime; discrete-symbol KGs work cleanly (83.3% recall) vs fuzzy at 43.3%. The iterative failures were substrate physics in the wrong operating mode, not substrate failure.
- **REVIVE closure:** `substrate_llm_triples_khop_gpu` HF + oracle HP. Qwen-1.5B extracted only 70% of bridge entities → 18.3% recall; given oracle triples, substrate K-hop=1.0. Extraction is the only gap. 7B+ LLM extractor is the next path.
- Production multi-hop architecture established: native-first cascade router (PP-123) at 0.853 accuracy (best-of-both 0.653) at 48% cost; two-stage disambig (PP-125) "fuzzy finds door, native walks graph" 0.820; single-shot attention on triples = 1.000 (PP-99 mechanism applied to discrete substrate).
- PPR family CLOSED: both spreading-activation (HF 0.229) and matrix-PPR (HF 0.328). Native substrate K-hop is the correct graph primitive.
- Discrete vs fuzzy KG-QA: 80× recall advantage (0.800 vs 0.010). Confirms product encoding choice.
- Markov PP-116 rescue MID: N-scaling 0.800 → 0.867, doesn't reach HP. Needs sharpening, not more N.

## Findings

### Multi-hop architecture (8 HP)
- `iterative_regime_crossover` HP: discrete 0.833 vs fuzzy 0.433. 32-citation universal principle reproduced. Iterative failures were regime, not architecture.
- `oracle_structured_hotpot_discrete` HP: 100% Hotpot recall with oracle structure. Substrate complete once NL→triple solved.
- `substrate_kg_triples_khop` HP: 2-hop 0.805, 3-hop 0.735. PP-119 production KG-QA gate GREEN for discrete.
- `substrate_legal_citation_snowball` HP: 100% 3-hop citation closure, 50 seeds. PP-120 automated case-law product.
- `cascade_native_first_router` HP: 0.853 vs best-of-both 0.653 at 48% cost. PP-123 production architecture.
- `beam_retrieval` HP: +7 recall points over greedy on 2-hop. PP-124 top-B recovers bridges.
- `two_stage_disambig_khop` HP: fuzzy disambig + native K-hop 0.820. PP-125 hybrid architecture.
- `single_shot_attention_triples` HP: recall@2=1.000 on triples. PP-99 applied to discrete = perfect.
- `parallel_subq_fuzzy` HP: parallel decomposition 1.000 in fuzzy regime (where iterative was 0.43). PP-126.

### Substrate primitives (3 HP)
- `nesting_depth` HP: 1.000 at d=2/4/8/12/16. Rich nested schemas to depth 16. PP-118.
- `binding_entropy_routing` HP: AUC=0.948 distinguishing answerable. PP-121 native routing signal.
- `rrf_fusion` HP: +53% recall over best single ranker. PP-122 hybrid native+fuzzy.
- `discrete_vs_fuzzy_kgqa` HP: 0.800 vs 0.010, 80× advantage. Confirms encoding choice.

### REVIVE 5th experiment
- `substrate_llm_triples_khop_gpu` HF: Qwen-1.5B 70% bridge extraction → 18.3% recall. **Oracle K-hop = 1.0.** Extraction is the only gap. 7B+ next.

### Closures
- `ppr_spreading_activation` HF: 0.229. PPR family closed (alongside ppr_matrix_khop HF 0.328).
- `ppr_matrix_khop` HF: 0.328 at 9.1 iterations. PPR closed. Native K-hop is the substrate graph primitive.

### Markov rescue (MID)
- `markov_transition_nscale` MID: N=2048→8192, 0.800→0.867. Diminishing returns; binding sharpening needed not more N.

## State

- cap_map v506 → v507
- commit: e90519e
- HONEST 1342 → 1359 (+17)
- LVH 263 unchanged
- Portfolio 32+117 → 32+126 (+9 PP rows: PP-118..PP-126)

## Context

This cycle resolves the multi-hop saga at the architectural level. The cycle-181 `iterative_regime_crossover` finding is the critical diagnostic: discrete-symbol regime gives substrate 83.3% on the same 32-citation universal principle that fuzzy regime gave 43.3%. The 5 iterative HFs (cycles 175-179: bge-large, K=3, GLiNER, e5-large, plus the LLM-decompose at 1.5B) were all in the fuzzy regime — substrate physics, not substrate failure. The substrate works; the operating mode was wrong.

The companion result is the REVIVE 5th experiment: LLM-extracted triples + substrate K-hop. Qwen-1.5B extracted only 70% of bridge entities, dropping end-to-end to 18.3%. But given oracle triples, substrate K-hop = 1.0 recall. This is mechanistically clean: the substrate side is complete; the extraction side is the only remaining gap. 7B+ LLM extractor is the high-P next path.

The production multi-hop architecture is now established: native-first cascade router (PP-123) gets 0.853 accuracy at 48% cost of always-fuzzy; two-stage disambig (PP-125) routes "fuzzy finds the door, native walks the graph" at 0.820; single-shot attention on triples = 1.000 (PP-99 mechanism applied to discrete substrate); parallel sub-query decomposition (PP-126) recovers the fuzzy regime at 1.000 cost of 2 parallel lookups. RRF fusion (PP-122) adds 53% recall as a hybrid layer.

PPR family is closed: both spreading-activation (HF 0.229) and matrix-PPR (HF 0.328) failed. Native substrate K-hop is the correct graph primitive — no need for Personalized PageRank style spreading.

Discrete vs fuzzy KG-QA shows 80× recall advantage for discrete encoding (0.800 vs 0.010). This confirms the product encoding choice at the QA level.

Markov transition (PP-116) rescue came in MID — N-scaling improves 0.800 → 0.867 but doesn't reach the 0.90 HP gate. Diminishing returns; binding sharpening is the next axis.

Pipeline: 66 commits v438→v507. 406 anchors verdicted. 39 LVH catches.

---

END. No action requested.
