# Exp-Dev -> Testbed: v8 fix acknowledged (excellent root-cause) -- deferring v8 queue per user Pythia-first priority

**From:** Exp-Dev  **To:** Testbed  **Inform:** User + Orchestrator  **Date:** 2026-06-04 ~22:25

The TOKENIZERS_PARALLELISM fork-deadlock root-cause + watchdog (os._exit(99) @ 120s) + PROGRESS_EVERY=25 + GPU-mem
logging is an excellent fix -- it explains BOTH v6 (doc 70300) and v7 (doc 0) silent hangs and converts any future
stall to a fast-fail. v7 already killed (GPU free).

HOLD on queuing v8 right now: user chose (this session) "kill v7 + DEFER Llama-audit + run Pythia-160M extraction
NOW + prioritize substrate-intrinsic-LLM (Tier-6/Tier-4/Stage-A)". So GPU priority = Pythia extraction (your lane)
> Tier-4/EX-CONCEPT > Stage-A > capacity reruns > v8 Llama. Recommend:
1. Testbed run PYTHIA-160M extraction first (user-prioritized; unblocks EX-CONCEPT-real + Tier-4).
2. Queue v8 (Llama) after Pythia, OR whenever GPU is free of priority work -- the watchdog makes it safe to run
   unattended now. I can queue v8 for you on your go, or you queue it; either works. Just confirm sequencing so we
   don't double-occupy the GPU. (Right now GPU has my 2 quick capacity-reruns displaced by the v7 kill; free after.)
**END.**
