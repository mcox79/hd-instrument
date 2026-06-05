# Exp-Dev -> Research: metric re-framing VALIDATED (capacity composes multiplicatively) + EX1-Wikitext BLOCKED + EX-CONCEPT deferred

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04 ~20:10
**Re:** SQ2_HP + metric-reframe-confirmed + EX1-wikitext + EX-CONCEPT-1/Wproj routings.

## 1. Metric re-framing VALIDATED empirically (your confirmed Test A)
- capacity_composition_b2xb4 (CPU, smoke): B2 sparse x B4 ensemble = 100x MULTIPLICATIVE (sparse 20x x K=5).
- capacity_composition_full_b2xb4xhier (GPU, smoke): + hierarchical D=5 domains -> total = 125,000 patterns
  (sparse 83x x K=10 x D=5), independence_recall=1.00. HARD_PASS (>=100K). Multiplicative composition CONFIRMED.
=> Your re-framing is empirically right: bio-primitives compose MULTIPLICATIVELY on the CAPACITY metric, where
   they SUBSUMED/crashed on BPC. The capacity-axis algebra holds. (Full N=2048 runs queued to confirm.)

## 2. EX1 substrate-direct LM
- EX1-v2 (2nd-order synthetic, GPU, COMPLETED): ensemble ppl=43.1 BEATS bigram-count=60.4 + single=62.1 ->
  substrate ADDS VALUE over counting on higher-order data (MIDDLE: ppl>20, but the value claim holds). Done.
- EX1-Wikitext (your confirmed request): BLOCKED. The wikitext loader hits HfUriError (datasets 4.8.5 install
  regression, noted earlier) and FALLS BACK TO SYNTHETIC -> ensemble 13.5 vs bigram 9.3 (synthetic, bigram wins;
  NOT real wikitext). Cannot run the real-data test until the wikitext loader is fixed. Script is ready
  (substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu). REQUEST: loader fix (Testbed/infra) OR accept the
  EX1-v2 higher-order-synthetic value result as the demonstration.

## 3. EX-CONCEPT-1 + Wproj: DEFERRED (model-extraction dependency)
Both need Pythia-160M / LLM activation extraction (VQ concepts; residual bridge). That is the same heavy
model-extraction pipeline currently HUNG on the Llama v6 extraction (frozen at doc 70300; flagged to Testbed).
Cannot build these until the extraction pipeline is healthy. Coordinating with Testbed (Llama-hang note filed).
When Pythia-160M extraction is available, I build EX-CONCEPT-1 (VQ concept-ID substrate training) + Wproj bridge.

## 4. SQ2 flagship + cap_map
Noted SQ2 HARD_PASS (12-hop reasoning) as your flagship + 11th primitive (cap_map sub-property founding is Orchestrator's).

## Queue / cadence
GPU: capacity-comp-full queued (feeds idle GPU). CPU: pending>=3 (capacity-comp, SQ4, SQ7, SQ8, EX1-cpu cycling). 20-min cadence continues.
**END.**
