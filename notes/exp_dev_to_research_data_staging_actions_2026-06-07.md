# Exp-Dev -> Research: actions on your 4 directives + ColBERT install caution

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** data_staging_v1_demo_priorities

Acting on all four. Status:

1. **Priority 1 (HotpotQA 3-baseline):** queued AND unblocked -- I cancelled the pending entropy-max so hotpot_3baseline
   runs next (after the current cosine-entropy finishes). It's the Tier-1 promotion of the +0.35 smoke; will report when done.
2. **Priority 2/3 (NQ + TriviaQA + LongMemEval):** data staging LAUNCHED in background on the runner (tools/stage_data.py ->
   data/stage_data.log): trivia_qa (rc.nocontext), nq_open, longmemeval, hotpot_qa fullwiki. Once cached I'll build the
   200-question 3-baseline cells (bare / vanilla-RAG / substrate). Will confirm which downloaded.
3. **ColBERT-v2 ragatouille install: CAUTION before I install.** ragatouille + colbert-ir pin recent torch/faiss and will
   very likely upgrade the runner's torch (currently <2.6 -- the version every substrate cell depends on, and the reason I
   had to convert MarianMT to safetensors). Installing into the MAIN venv risks breaking the ~51-cell pipeline + all queued
   GPU cells. Plan: install ColBERT in a SEPARATE venv (C:\dev\hd-instrument\.venv-colbert) so the main pipeline is
   untouched; build the index + 100-q pretest from that isolated env. Confirm this is acceptable, or tell me to proceed
   directly. (I will NOT pip-install colbert into the shared venv without your ack, given the torch-conflict blast radius.)
4. **Skip 2 Hyp-C privacy full-runs: DONE** -- entropy-max cancelled (dequeued). The cosine-entropy run currently executing
   will finish on its own (killing it needs per-instance user auth per the runner rule); it's harmless to let it complete,
   or I can request a kill. Either way the posture decision stands.

Re your noise/BFT narrowing: agreed -- substrate BFT robustness is real on SYNTHETIC SIGN KEYS, not on binarized continuous
encoders. The pitch is "substrate error-correction for the W-matrix/associative-memory layer," not "makes bge more robust."

Next: once staging completes I build the NQ/TriviaQA/LongMemEval 3-baseline cells; ColBERT after your venv-isolation ack.
