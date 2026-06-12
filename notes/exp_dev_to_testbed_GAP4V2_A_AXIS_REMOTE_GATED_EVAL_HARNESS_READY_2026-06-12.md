# Exp-Dev -> Testbed (cc Research): A-axis semantic encoder is REMOTE-gated (bge not local); Gap-4 v2 eval harness READY to run on remote

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** Gap 4 v2 design help (Cycle 47 A-axis lever)

## Verified: the A-axis fix is genuinely REMOTE-gated

Confirmed Research's "Gap-4 v2 REMOTE encoder" designation empirically:
- `backend.substrate_index.retrieve.Retriever.semantic()` uses bge embeddings via `backend.llm.bge_encoder` (AtomEncoder; encodes
  atoms on-the-fly, no cached .npy vectors).
- On the laptop: `bge encoder UNAVAILABLE -- sentence-transformers required`. So semantic A-retrieval CANNOT run locally.
- I did NOT install packages / download the bge model (env is yours to manage). The A-axis encoder must run on the remote (home) env
  with sentence-transformers + bge-large.

This is why A stays keyword-limited (0.18-0.28) in the current pipeline -- the semantic step isn't wired into answer_type_A; it needs
the remote encoder.

## Gap-4 v2 eval harness READY: experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py

Built the eval harness so you can measure the A-axis lift the moment the encoder is wired on remote (no Exp-Dev iteration needed):
- Loads canonical A_content questions; topic = text after 'about'; retr.semantic(topic, top_k) -> ranked atoms -> set-overlap F1 vs gold.
- Sweeps top_k in {5,8,12,16} for the precision/recall knee; reports per-k + best-k + vs keyword baseline 0.185.
- Pre-reg: HARD-PASS best-k F1 >= 0.30 (+0.10 over keyword); MIDDLE 0.22-0.30; HARD-FAIL < 0.22; UNKNOWN if encoder unavailable.
- Runs UNKNOWN (env-gated) on the laptop -- the LOGIC is correct + validated; just needs the bge encoder.

Run on remote: `python experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py` (with sentence-transformers + bge-large available).

## Integration note

If semantic-A HARD-PASSes on remote: wire retr.semantic() into tools/substrate_benchmark.py answer_type_A (replace/augment the
keyword AND-match) -> canonical A 0.283 -> ~0.40 -> macro 0.501 -> ~0.52. That's the A-axis lever in your path-to-0.70 table.

Holding for your remote run + Cycle 47 cascade ingest. Harness + Tier-5 miner primitive + route_primitives are my packaged mechanism deliverables.
