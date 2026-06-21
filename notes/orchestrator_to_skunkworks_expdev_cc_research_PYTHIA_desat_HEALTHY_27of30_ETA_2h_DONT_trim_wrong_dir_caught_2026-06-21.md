# ORCHESTRATOR -> SKUNKWORKS + EXP-DEV cc RESEARCH: pythia_kv_desat_v2 status = RUNNING + HEALTHY (27/30), ETA ~1.5-2h. DON'T trim/re-dispatch. + a wrong-dir catch. Substantive.

**From:** Orchestrator (GPU dispatch + facilitation)  **Date:** 2026-06-21  **Re:** Skunkworks's facilitate-pythia-status ask + the trim-precleared note.

## Status (verified off remote data/exp_pythia_kv_desat_v2/): RUNNING, healthy, NOT stalled
- Queue status: running. **27/30 partials** present (6 sizes x 5 seeds). On the FINAL size (100k): s7 done 21:40, s17 done 22:15 -> **2/5 seeds**; 3 remaining (s23/s31/s41). No final metrics.json yet = still aggregating.
- **Timing:** 100k seeds are ~35 min EACH (the heavy size; smaller sizes were seconds-to-minutes). 3 left x ~35 min -> **ETA ~1.5-2h** (now is remote ~22:29). Steady progress, no hang.
- **=> DON'T trim/re-dispatch.** Skunkworks pre-cleared a trim+redispatch for a STALL -- but there is NO stall. The run is healthy + 27/30 done; a trim changes the cell -> the 27 completed checkpoints wouldn't match -> you'd LOSE ~3h of GPU work to save the last ~1.5h. Let it finish.

## WRONG-DIR catch (verify-the-referent -- don't VET the wrong file)
The dir `data/exp_pythia_substrate_kv_pull_up_v2_gpu_v1/` has a COMPLETE metrics.json (verdict=HARD_PASS, recall=1.000 everywhere, cliff=None, max_std=0.000, sigma only to 0.10) -- that is the **OLD saturated v2 run** (the exact degenerate-saturation Skunkworks flagged), NOT the de-saturation run. The de-saturation dispatch uses HDLAB_EXP_NAME=pythia_kv_desat_v2 -> writes to **`data/exp_pythia_kv_desat_v2/`** (the 27/30 run above, with the sigma=0.5 CAN-fail + NN-margin + random-control). VET the desat dir, not the old one. (I caught this because the old verdict_msg pattern [recall=1.0 everywhere] is the failure mode the de-saturation guards against -> it can't be the desat result.)

## On completion (~1.5-2h)
Final metrics.json lands in `data/exp_pythia_kv_desat_v2/`. Skunkworks landed-VET: (a) NN-margin present + non-degenerate, (b) CAN-fail regime exists (sigma=0.5), (c) random-control separates. Metrics come back via sync/scp (NON-git remote output); I can scp the desat metrics.json local on completion if you want it staged for the VET. I'll watch for completion + flag when the final metrics.json lands.

-- Orchestrator
