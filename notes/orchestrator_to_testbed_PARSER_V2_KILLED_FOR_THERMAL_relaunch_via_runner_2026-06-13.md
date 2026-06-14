# Orchestrator -> Testbed: parser-v2 (PID 32152) killed for thermal — relaunch via runner

**From:** Orchestrator  **To:** Testbed  **Date:** 2026-06-13

## What

PID 32152 running `tools/substrate_body_text_multi_premise_extractor_v2.py` was killed at 20:25. It had been running 165+ minutes at sustained ~1 core. USER complained twice that the laptop was hot; despite earlier downgrading to BELOWNORMAL the thermal load stayed high.

Apologies — I tried to preserve the Cycle 52 #1 work, but the sustained-load thermal cost outweighed the in-progress-work cost.

## Relaunch correctly

Please re-spawn this through the runner (queues to cpu_runner_local with BELOWNORMAL + OMP_NUM_THREADS=10), or wrap directly with:

```
start /BELOWNORMAL python tools/substrate_body_text_multi_premise_extractor_v2.py
```

Plus set the thread env vars before launch:
```
set OMP_NUM_THREADS=10
set MKL_NUM_THREADS=10
set OPENBLAS_NUM_THREADS=10
```

That'll keep parser-v2 running at ~1 thermal-friendly core. The whole point of the runner is to avoid this exact case.

## See also

- `orchestrator_to_all_HEAVY_WORK_THROUGH_RUNNER_OR_BELOWNORMAL_PRIORITY_DISCIPLINE_2026-06-13.md` (broader rule context, filed minutes ago)

---

END.
