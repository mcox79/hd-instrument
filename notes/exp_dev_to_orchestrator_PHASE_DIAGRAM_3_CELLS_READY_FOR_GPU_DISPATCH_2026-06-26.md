# exp_dev -> orchestrator: 3 phase-diagram cells READY FOR GPU DISPATCH

**Filed-by:** exp_dev (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26 directive "what about phase diagram build out?" via Research routing-correction handoff `notes/exp_dev_handoff_research_remote_routing_correction_phase_diagram_buildout_2026-06-26.md`.

## Status: SMOKE_PASS x 3; ready for orchestrator-led overnight_queue dispatch

I authored + smoke-tested 3 phase-diagram extension cells locally. All 3 SMOKE_PASS at laptop-CPU regime. Cannot dispatch to remote per harness-denied push; orchestrator owns push + queue_add for overnight_queue (GPU).

## Cells

### 1. Multi-hop depth ceiling sweep (depths 20/25/30)

- **Script:** `experiments/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.py`
- **Prereg:** `preregs/2026-06-26_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.md`
- **Anchor:** `phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1`
- **Smoke verdict:** SMOKE_PASS (PART_15=1.000, PART_20=0.960, PART_25=1.000, PART_30=0.920)
- **Extends:** prior chain-grade depth-15 (0.808 cv=0.024); maps depth ceiling
- **ETA:** ~3-5 min GPU wall; **--timeout 1200**

### 2. WM K-ceiling sweep (K=32768)

- **Script:** `experiments/exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1.py`
- **Prereg:** `preregs/2026-06-26_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1.md`
- **Anchor:** `phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1`
- **Smoke verdict:** SMOKE_PASS (mechanism end-to-end; rail-drift documented OK at smaller smoke N)
- **Extends:** prior MIDDLE_BAND K=4096/8192/16384 (by-construction-saturation); pushes K=32768 (8x past chain-grade)
- **ETA:** ~5-8 min GPU wall; **--timeout 1800**

### 3. Capacity sweep at N=16384 with V_C in {2000, 4000, 8000}

- **Script:** `experiments/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1.py`
- **Prereg:** `preregs/2026-06-26_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1.md`
- **Anchor:** `phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1`
- **Smoke verdict:** SMOKE_PASS (KNN sentinel + VC arms OK)
- **Maps:** production-scale V_C axis (audit-device inherits V_C_IN<=2000; this maps to 4x production)
- **ETA:** ~2-3 min GPU wall; **--timeout 1200**

## Dispatch contract for orchestrator

For each cell:
1. **Push** to origin/main (harness-DENIED for exp_dev; orchestrator authorized for push)
2. **Pre-flight smoke on REMOTE GPU** with HDLAB_EXP_NAME=<anchor>_smoke; verify gpu_util_p50 >= 50% per Fix #24
   - If gpu_util < 30%, route back to me as numpy-only cell (defeats GPU purpose)
3. **queue_add** each cell to overnight_queue with --prereg + --timeout per above; HDLAB_EXP_NAME=<anchor>
4. **Verify cell-spec arrives on remote** per REMOTE VERIFY discipline

## Smoke disciplines satisfied (laptop CPU)

- Self-test PASS for all 3 (formula + bands + LLM=0 + GPU assertion bypassed for smoke)
- Smoke run produced metrics.json + verdict for all 3
- Substrate-only-decode gate (_LLM_CALL_COUNTER=0) asserted in all 3
- Pre-reg bands LOCKED at module init in all 3 (regression sanity assert in self-test)
- ASCII-only; per-seed checkpoint; atexit synthesizer (resumable on crash)

## What I cannot do (per harness gates)

- Push to origin/main (laptop notes invisible to remote until pushed)
- Restart remote runners / heartbeat checks
- Verify remote GPU util before dispatch
- queue_add to remote queues (requires push)

Orchestrator: 3 cells ready for pickup. Tools you need:
- `git push origin main` (harness allowed for sync-task role)
- SSH to marsh@home for remote GPU smoke + queue_add via remote CLI
- `tools/queue_add.py overnight_queue <anchor> experiments/<script> --prereg preregs/<file>.md --timeout <s>` on remote OR via remote SSH

## Notes on USER directive matching

USER asked for {8192, 16384, 32768} on WM K-sweep; existing v1 cell already ran 4096/8192/16384 at saturation. My v1 dispatches {4096(rail), 8192, 16384, 32768} -- honors the USER's literal K-set + adds 4096 as the chain-grade reproduce rail. K=32768 is the genuinely novel ceiling probe.

USER asked for {20, 25, 30} multi-hop depths; prior chain-grade was at depth 15. My v1 dispatches {15(rail), 20, 25, 30}.

USER asked for V_C {2000, 4000, 8000} at N=16384; my v1 dispatches exactly that.

-- exp_dev (Opus 4.7-1M)
