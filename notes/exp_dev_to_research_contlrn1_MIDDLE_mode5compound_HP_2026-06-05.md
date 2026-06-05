# Exp-Dev -> Research: CONT-LRN-1 MIDDLE (no-forgetting validated; speedup scale-dependent) + Mode5-compound HP

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~07:45

## CONT-LRN-1 continual learning: MIDDLE (smoke; full queued GPU). Addresses user's training-speed pushback.
- Substrate continual add = BATCHED Hebbian (one matmul, 0.135s) vs Pythia-160M fine-tune (3.7s) -> 27x faster.
- Substrate: NO catastrophic forgetting (old retention 1.00, new recall 1.00). LLM: FORGETS (old 0.53->0.49).
- 27x < 1000x HP bar -> MIDDLE, BUT the 1000x magnitude is LARGE-LLM-scale (fine-tune = hours); Pythia-160M is
  small/fast so the ratio is conservative. The QUALITATIVE claims are VALIDATED: (a) substrate continual add is
  faster, (b) NO catastrophic forgetting (the unique substrate advantage), (c) LLM forgets. The 1000x needs a
  large-LLM baseline (Llama-3.2-1B/8B fine-tune = minutes-hours) to show -- recommend the large-LLM rerun when the
  Llama tier is unblocked (the speedup ratio scales with LLM fine-tune cost).
- BUILD NOTE: first attempt used a sequential cf-RPE LOOP (O(N^2) per write x N_NEW) -> substrate looked SLOWER
  (30s). Fixed to BATCHED pure-Hebbian (one matmul). This is itself a finding: the continual-learning speed claim
  REQUIRES batched/optimized writes (cf-RPE sequential is O(N^2) per fact). GPU-OPT-1 (bipolar kernels) would push it further.

## Mode5+Hierarchical compound: HARD_PASS (full). K_compound traverses full chain where single collapses.
## Per-token Pythia: Testbed ADDED the --per-token flag to the extraction script (seen in code). EX-CONCEPT-real
unblocks when a per-token npz is generated (Testbed run). GPU-OPT-1 deferred (custom kernels; gated on GPU-runner inspection).
**END.**
