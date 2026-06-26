# Prereg: substrate_multihop_beam_search_with_WM_candidates_v1

**Date:** 2026-06-25
**Author:** exp_dev (USER-directed)
**Cell:** experiments/exp_substrate_multihop_beam_search_with_WM_candidates_v1.py
**Anchor:** substrate_multihop_beam_search_with_WM_candidates_v1
**Routing:** local_cpu_queue
**Driver:** USER 2026-06-25: "with our PFC we should be able to do the brain analog easily no? We should try that, since we already have PFC" + "We're not going to live with the ceiling we know it can be done"

## Strategic significance

6th multi-hop attempt. Prior 5 (pointer-chain-v2, wm-scaffold, csp-gated, consolidation-v3, pfc-chunked-2hop) all HARD_FAILed at 5-hop chain. Per-step accuracy 0.69 -> 0.485 -> 0.31 -> 0.205 -> 0.145 in the pointer chain; 5-hop cumulative ~0.122. Chunked 2-hop restart gave +0.04 lift but ceiling held.

**The architectural lever not yet tested:** parallel multi-candidate beam search. Brain analog: PFC + hippocampus + dorsal striatum maintain MULTIPLE candidate plans in parallel and prune by reward prediction. Substrate already has the 3 primitives chain-grade individually:
- WM multi-bank (today, chain-grade K=1024 at N=4096): holds W candidate continuations
- CSP confidence (today, HARD_PASS): per-hop confidence score
- HRR 2-hop binding (today, sanity rail 0.65): per-hop retrieval

Hypothesis: top-1 sequential cleanup discards information at every hop; if the correct continuation is in top-K (e.g. K=3, K=5) at each hop, beam-of-W maintains it. By final hop, picking max-confidence chain among W candidates recovers correct answer with substantially higher probability than top-1.

Information-theoretic intuition: per-hop top-K=3 hit-rate at hop 1 is ~0.85 (vs top-1 0.69); beam W=5 with top-K=3 enumerates 5^5 = 3125 candidate chains, with the correct one in the beam with probability ~ (1-(1-(top-K-recall))^W)^depth. For top-K-3-recall ~ 0.85, W=10 beam should keep correct chain with prob ~ 0.85^5 = 0.44 even before CSP-pruning aids ranking.

## Mechanism (parallel candidate beam search)

For each k-hop query:
1. At hop 0: query subject = starting candidate (single chain)
2. At each hop i:
   - For each current chain: retrieve top-K candidates via per-hop cleanup (argpartition on cleanup scores)
   - Each current chain branches into K continuations
   - Keep beam_width=W best continuations by per-hop cleanup-score (substrate-native ranking; no LLM call)
   - WM-bank slot count = W (uses multi-bank WM primitive bank-as-candidate-slot)
3. At final hop: pick chain with highest composite score (sum of log per-hop cleanup scores)

Substrate-only at inference (no LLM forward calls; only numpy ops on bipolar atoms).

## Arms (5)

- ARM_BASELINE_HRR_2HOP -- beta-sweep verbatim regime (sanity rail [0.62, 0.68]; matches pointer-chain v2)
- ARM_SINGLE_TOP1_5HOP -- reproduces pointer-chain v2 single-chain (rail ~0.122)
- ARM_BEAM_W2_TOPK3_5HOP -- beam_width=2, top_k_per_hop=3
- ARM_BEAM_W5_TOPK3_5HOP -- beam_width=5, top_k_per_hop=3
- ARM_BEAM_W10_TOPK5_5HOP -- beam_width=10, top_k_per_hop=5

## Pre-reg bands (LOCKED at module init via assert)

- **HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM**: ARM_BEAM_W10_TOPK5_5HOP top1 >= 0.50 AND monotonic in beam_width (W2 < W5 < W10) AND cv <= 0.07
- **HARD_PASS_PARTIAL**: ARM_BEAM_W10_TOPK5_5HOP top1 >= 0.30 (lift over 0.122 rail; partial scaling)
- **HARD_FAIL_BEAM_DOESNT_HELP**: ARM_BEAM_W10_TOPK5_5HOP top1 < 0.20 (6th multi-hop attempt also fails; beam is not the lever either)
- **SANITY_BREACH**: ARM_BASELINE_HRR_2HOP outside [0.62, 0.68] in 2/3+ seeds

## Config

- N_DIM = 8192 (consistent with prior 5 multi-hop attempts for apples-to-apples)
- V_CONCEPTS = 200
- V_PREDICATES = 10
- K_SET = 20
- N_CHAINS = 200
- Seeds [7, 17, 23] (cross-cell consistent)
- max_depth = 5 (5-hop barrier; same regime as prior 5 attempts)
- Substrate-only; ASCII; per-arm metrics (Fix #28)

## META disciplines

- META_M6: baseline ARM_BASELINE_HRR_2HOP measured in-cell at current regime (not copied from prior)
- META_M7: smoke must match full on N_DIM, V_C, V_P, K_SET (capacity-sensitive); only N_CHAINS + SEEDS reduce
- META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module init via assert
- Q-discipline: any arm >= 0.995 flagged as suspect saturation
- ASCII-only; no unicode in scripts

## Routing

- local_cpu_queue (numpy-only; CPU-feasible at this scale; estimated wall ~1h for 3 seeds full)
- No GPU dependency
- Timeout: 7200s (2h with 2x headroom over 1h estimate)

## Reference cells

- exp_substrate_multihop_pointer_chain_v2 (per-hop primitive cell; per-step decay 0.69->0.145)
- exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1 (5th attempt HARD_FAIL; per-chunk 0.54->0.265->0.20)
- exp_substrate_working_memory_multi_bank_routing_v1 (chain-grade K=1024; bank-as-slot primitive)
- exp_csp_first_ship_v1 (CSP confidence primitive; HARD_PASS warm-start)
