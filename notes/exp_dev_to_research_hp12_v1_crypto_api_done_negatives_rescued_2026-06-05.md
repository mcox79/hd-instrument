# Exp-Dev -> Research: HP-12 V1 crypto+API DONE (gmpy2), 3/4 negatives rescued, capabilities hold at N=4096

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + Testbed + User  **Date:** 2026-06-05 ~16:30

## HP-12 V1 build progress (desktop, $0):
- Day-1 crypto: DONE. gmpy2 refactor of tools/hp12/rsa_accumulator.py (Testbed installed gmpy2 2.3.0). Cert issuance
  0.058ms at RSA-512 demo config (was 3.46ms pure-Python) -> Test 2 HARD_PASS. Standalone verifier.py stays pure-Python
  (third-party portability). gmpy2 enables V2 2048-bit production (~2ms, further optimizable).
- Day-3 backend: DONE (e2e live-ingest/query/delete/verify, 0 phantom).
- Day-4 API surface: DONE + HARD_PASS. tools/hp12/api.py SubstrateKB with 4 endpoints (post_fact/query/delete_fact/
  get_audit). e2e test: all endpoints functional, query recall 1.0, every audit cert third-party-verified 1.0, 0 phantom,
  retention 1.0.
- REMAINING V1: frontier-LLM-contrast script (ROME 38% / MEMIT 29% residual recall vs substrate categorical) + the
  5-min screen recording (manual). Test 3 extraction-SPEED still deferred (Llama-1B weights gated; Testbed Ask-2 on hold).

## SPARSE-V2 negative rescues (full verdicts):
- V2-1 theta-burst-endpoint: HARD_PASS (+44pp multi-step over iterated K=1; lookahead direction holds).
- V2-2 hadamard-bipolar-expansion: MIDDLE (2.8x capacity; source-rank-bounded, matches your 1.5-4x prediction).
- V2-4 kgram-XOR-scaling: HARD_PASS (k=3 reaches trigram-class at N=4096; Phase-3 scaling path validated).
- V2-3 HotpotQA-1B: NOT built (needs gated Llama-1B weights local; Testbed Ask-2 deferred per your recommendation).
3 of 4 rescuable negatives empirically rescued. Cross-cutting sparse-write insight noted (your drill lane).

## Capabilities consolidated at Phase-2 N=4096: HARD_PASS (single-hop/multi-hop/analogical/counterfactual all 1.0).

## Queues: CPU = crypto(re-run) + API-surface; GPU idle (model-load->cloud; gmpy2 done, Llama-weights + faiss = Testbed).
**END.**
