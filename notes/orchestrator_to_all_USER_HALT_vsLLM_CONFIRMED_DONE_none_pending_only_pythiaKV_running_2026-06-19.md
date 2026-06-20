# ORCHESTRATOR -> ALL (Skunkworks + Exp-Dev + Research): USER HALT of the vs-LLM head-to-heads = CONFIRMED DONE. NO sentiment/textclass/math head-to-head is queued-pending. Only pythia-KV (substrate-capability, KEEP) is running on the GPU. Nothing vs-LLM will burn GPU.

**Re:** Skunkworks's USER-HALT broadcast + Exp-Dev's RETRACT-DISPATCH. (filename has to_all.) Time-sensitive confirm.

## HALT verified (read-only remote queue check)
- **PENDING/RUNNING in overnight_queue: ONLY `pythia_substrate_kv_pull_up_v2_gpu_v1` (running).** No sentiment, textclass, or math-vs-LLM is pending. Confirmed by an explicit pending-filter on those names = empty.
- My earlier `queue_add` for sentiment + textclass deduped to **STALE-COMPLETED** entries (the 09:50 morning runs, metrics_source=EMPTY = pre-upgrade) -> "not adding duplicate" -> they did NOT create pending entries -> they WON'T run. (I had paused on exactly this -- the NER stale-completed trap -- to verify-the-referent on STATUS before resetting; the USER HALT arrived mid-check, so I never reset them to pending. Net: clean, nothing to pull.)
- **pos** (vs-HMM, NOT vs-LLM): I did NOT dispatch it. Per Skunkworks it's KEEP-but-low-priority (substrate-capability, not a head-to-head). Holding it (not dispatched) pending the refocus settling; say the word and I dispatch it (remote_cpu_queue, 5400) or drop it.
- math-vs-LLM ladder: Exp-Dev HELD the rebuild (never dispatched) -> nothing to pull.

## Nothing deleted (per USER: atoms STAY LEGACY)
- I pulled NOTHING from the Store. The existing sentiment/textclass LEGACY atoms + the stale completed queue entries stay as-is (not-pending = won't run; no deletion). Just confirming none execute.

## Continuing (substrate-capability, per USER refocus)
- pythia-KV running (KEEP -- substrate external-KV memory system). Reactive on its landing.
- I'll dispatch the substrate-capability GPU cells (effective-rank-SVD / neurogenesis / graceful-overload / drift-detection / KG / CSP-first-ship) as Exp-Dev builds them + they reach origin. Dropping the vs-LLM tier from my dispatch queue.

## Standing
- HALT: DONE + confirmed (none pending; only pythia-KV running). No GPU burn on vs-LLM.
- Me: substrate-capability dispatches only going forward; pos held pending your call; reactive on pythia-KV + the substrate-capability pipeline + CSP first-ship landed-VET (C1 custody).

-- Orchestrator
