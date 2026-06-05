# Exp-Dev -> Orchestrator + User: HP-12 V1 killer-demo build COMPLETE (only manual screen recording remains)

**From:** Exp-Dev  **To:** Orchestrator + User  **Inform:** Research + Testbed  **Date:** 2026-06-05 ~16:50

## HP-12 V1 (certified per-fact deletion killer demo) -- all software deliverables DONE + HARD_PASS:
| Deliverable | Status | Result |
|---|---|---|
| Day-1 crypto (RSA accumulator + verifier CLI, gmpy2) | HARD_PASS | cert issuance 0.058ms @ RSA-512; tamper-rejected; third-party verifier |
| Day-3 demo backend (live-ingest/query/delete/verify e2e) | done | recall 1.0, certs verified, 0 phantom, retention 1.0 |
| Day-4 HIPAA API surface (tools/hp12/api.py, 4 endpoints) | HARD_PASS | all endpoints e2e, certs third-party-verified, 0 phantom |
| Frontier-LLM contrast (extraction attack) | HARD_PASS | post-deletion residual 0% under 3 attacks vs ROME 38%/MEMIT 29% (published) |

## Shipped artifacts (reusable):
- tools/hp12/rsa_accumulator.py (gmpy2-accelerated; pure-Python fallback)
- tools/hp12/verifier.py (standalone third-party cert verifier CLI; stdlib-only, shareable)
- tools/hp12/api.py (SubstrateKB: post_fact / query / delete_fact / get_audit)
- tools/hp12/frontier_contrast.py (contrast table + structural-impossibility argument)
- 4 validation cells (decisive crypto, e2e backend, API surface, extraction-attack contrast) all queued + HARD_PASS

## REMAINING for HP-12 V1 (NOT Exp-Dev's lane):
1. The 5-minute SCREEN RECORDING (manual; per research V1 demo flow). Backend + API + verifier + contrast are all ready
   to drive it. Demo config: RSA-512 (headline <1ms latency; disclaim "V2 = 2048-bit + gmpy2 production").
2. Optional: live Llama-1B extraction-SPEED timing (Test 3) -- needs Testbed Ask-2 (gated weights, currently deferred).

## Deferred / V2 (not blocking V1 demo):
- faiss HNSW env hang (V2 1M-fact scale; Testbed: Linux cloud box ~$0.50)
- 2048-bit production crypto latency (gmpy2 path shipped; ~2ms, further optimizable)

## Phase 4: per research TOP-5 sequencing, starts AFTER HP-12 V1 demo lands. Phase-4a infra notes read (awareness only;
not started -- sentence_transformers also missing for the MiniLM PHASE4A-1 item). Awaiting demo-ships signal to begin.

**Question for User/Orchestrator:** HP-12 V1 software is demo-ready. Do you want to record the demo now, or have me
proceed with anything else first? Phase 4 is staged and ready to begin on your go.
**END.**
