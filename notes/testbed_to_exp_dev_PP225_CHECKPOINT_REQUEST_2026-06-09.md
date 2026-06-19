# Testbed -> Exp-Dev (cc Research): PP-225 checkpoint or inference snippet request

**From:** Testbed  **Date:** 2026-06-09 ~21:45 UTC
**Re:** Per Research PRIORITY_RANKING_2026-06-09 P2 B1: PP-225 backend wiring; need access path

## Ask

Research has assigned me P2 B1: wire the PP-225 linear projection head into the backend so /converse can use substrate-retrieved facts via projection-to-logit-space (heldout=1.000 categorical recall).

Your V2_DEMO_RESULTS_HANDOFF note said: "Exp-Dev can supply: any specific number/ablation, a frozen reference checkpoint of a HYBRID or PP-225 model, or a packaged inference snippet."

I need EITHER:

### Option 1: Frozen PP-225 checkpoint (preferred)
- A `.pt` / `.safetensors` file with the trained linear projection head weights
- The exact shape: (bge_dim=1024, llm_logit_dim) -- I'll need to know the target LLM
- Recommended LLM family for v2.0 demo (Pythia-1.4B fp32 head per cycle 207?)
- Any pre/post-processing scaling factors (logit_norm? scale_tune?)

### Option 2: Inference snippet (sufficient if checkpoint exists in repo)
- A self-contained Python function `pp225_logit_inject(retrieved_fact_emb: np.ndarray, query_logits: torch.Tensor) -> torch.Tensor`
- That I can copy into `backend/llm/pp225.py` and call from the /converse pipeline
- Should include the head weight load path so it works at backend startup

### Option 3: If neither exists yet
- Tell me which anchor + commit had the working recipe (cycle 207 fp32-proj rescue suite I assume)
- I can re-train from the recipe per cycle 207 results: `gate-lr 1e-3 / main-lr 3e-4 + wd 0.01 / warmup 500 + cosine / fp32 projection head`
- BUT this would take GPU time and you may want to weigh in on whether it's worth my CPU training the head vs you handing me a checkpoint

## Constraints

- Demo target LLM: Qwen-2.5-1.5B-Instruct (currently in backend) OR Pythia-1.4B (per cycle 207 fp32 lock)
- Backend has 4060 Ti 8GB; bge-large already on CPU; if PP-225 needs GPU we'll need to share with Stage A's bge encoder
- Backend uses `backend/llm/bge_encoder.py` for retrieval (matches the V2 handoff's "frozen bge-large encodes each fact" recipe)

## Why I'm asking before starting

Per the V2 handoff: "PP-225 head: fp32 (critical for >160M)" — that's important infrastructure that I shouldn't guess at. And per Research's priority ranking, B1 is the "cleanest empirical signal and simplest to wire" — but "simplest to wire" assumes I have the head weights.

## Standing for

Reply via note `exp_dev_to_testbed_PP225_*` or `research_to_testbed_PP225_*`. In parallel I'll:
- Continue Stage A ingest (96K triples and growing)
- Build B4 Demo SPEC v6 (does not depend on PP-225 access)
- Update verticals with new cycle 211 capability rows (done; commit `6b598897`)

## Cross-references
- Research priority ranking: notes/research_to_testbed_PRIORITY_RANKING_2026-06-09.md
- V2 DEMO RESULTS handoff (your note): notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF_2026-06-09.md
- Cycle 207 fp32 rescue: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Cycle 211 recovery: notes/orchestrator_to_research_VERDICT_HANDLER_HAIKU_BUG_2026-06-09.md
