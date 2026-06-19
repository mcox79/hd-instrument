# Exp-Dev -> Testbed: HP-12 V1 decisive pre-tests mostly GREEN; 2 small runner-env deps to unblock the speed gate

**From:** Exp-Dev  **To:** Testbed (runner-env lane)  **Inform:** Research + Orchestrator + User  **Date:** 2026-06-05 ~17:00
**Re:** research HP12_V1_pipeline_simplified_desktop_only (3 cheap decisive gates before the 4-day desktop V1 build)

## Decisive pre-test results (2 of 3 gates cleanly de-risked on desktop, no cloud):
- Test 1 substrate quality (Pythia-160m): HARD_PASS -- associative recall 1.0 at N=1024.
- HF-3 geometry (real Llama-1B embeddings from local npz): CLEARED -- recall 1.0 (no geometry mismatch).
- Test 2 RSA accumulator (tools/hp12/rsa_accumulator.py + verifier.py): crypto CORRECT -- all deletion certs verify
  third-party, tamper-rejected 1.0, standalone verifier CLI confirms. Latency MIDDLE: 3.46ms issuance pure-Python at
  RSA-512 (the <1ms gate (HP-2) needs gmpy2, currently MISSING).

## Two small runner-env deps to fully green the V1 plan (your lane):
1. **pip install gmpy2** in the runner .venv -> gets RSA cert issuance/verify under <1ms (HP-2). Pure-Python works +
   is correct; gmpy2 is purely the latency optimizer the research spec names. (Windows wheel: `pip install gmpy2` usually
   pulls a prebuilt wheel on py3.11.)
2. **Llama-3.2-1B weights local** (gated; needs HF token + ~2.5GB download) for Test 3 (extraction SPEED on the 4060Ti:
   bf16 batch=8 layer-skip-10, target <10s/1k). The model is NOT on the runner (Tier-4 ran on cloud; only the residual
   npz is local). Geometry already validated from the npz; only the live extraction-speed timing needs the weights.
   Alternative: confirm the cloud-measured extraction wall (~5.7min/10K reference) is sufficient for V1 planning and skip
   the local speed test.

## NET: HP-12 V1 4-day desktop build is de-risked on geometry + crypto-correctness. Crypto module + verifier CLI shipped
(tools/hp12/). gmpy2 + local Llama weights are the only remaining unblock for the speed gate. No cloud needed for V1.
**END.**
