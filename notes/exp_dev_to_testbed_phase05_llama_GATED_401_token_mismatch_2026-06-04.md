# Exp-Dev -> Testbed + User: Llama v4 blocked on GATED-REPO 401 (runner token lacks license access)

**From:** Exp-Dev  **To:** Testbed + User  **Inform:** Orchestrator  **Date:** 2026-06-04

## v4 progressed past datasets -> now blocked at the model gate
After installing `datasets` (v3 root cause), v4 got through step2 (datasets) + step5 (torch import) to
`tokenizer.from_pretrained(meta-llama/Llama-3.2-1B) START`, then HARD_FAILED at 20.3s with:

  401 Client Error. Access to model meta-llama/Llama-3.2-1B is restricted... gated repo.
  You must have access to it and be authenticated.

## Diagnosis: TOKEN MISMATCH (not a script bug)
Testbed's ready-to-queue note said license acceptance was "DONE -- verified via model_info + AutoConfig +
AutoTokenizer all returning OK with our .hf_token". But the RUNNER's effective token (the one the script
picks up at runtime -- HF_TOKEN env / cached login on the 4060 Ti runner account) gets a 401. So the token
that has the accepted license (Testbed's .hf_token) is NOT the token the runner script authenticates with.

## Action needed (User / Testbed -- NOT re-queue yet)
ONE of:
1. Ensure the runner uses the licensed token: have the script load Testbed's verified `.hf_token` explicitly
   (e.g., `from_pretrained(..., token=<that token>)`), OR set HF_TOKEN on the runner to that token, OR
   `huggingface-cli login` on the runner account with the licensed token; OR
2. Accept the Llama-3.2 license for whatever account owns the runner's current HF_TOKEN.
Verify on the runner directly:
  `.venv\Scripts\python.exe -c "from transformers import AutoConfig; AutoConfig.from_pretrained('meta-llama/Llama-3.2-1B')"`
should return OK (no 401) before re-queue.

## I have STOPPED re-queueing Llama
Per your contention note: the failed Llama was crash-looping + collaterally failing concurrent GPU jobs
(it false-flagged my hierarchical run and failed the resonator). Killed the procs; no pending Llama entries
remain. I will NOT re-queue Llama again until you confirm the runner's token resolves the 401 (re-issue a
ready-to-queue note). Meanwhile the GPU is fed with substrate experiments.

## Silver lining
v3/v4 stage-logging worked perfectly -- localized two distinct blockers in two runs (datasets missing -> 401
gated). Once the token is fixed, v4 should run end-to-end (model download ~2.5GB to F:\hf_cache, then extract).

**END.**
