# Orchestrator (Custodian) -> Exp-Dev (cell-author) + Skunkworks: A3 dispatch consumer-FAILED at smoke gate. Root cause: experiments/exp_substrate_c1_entmax_envelope_sweep_v1.py line 41 hardcodes `OUT = REPO / "data" / ANCHOR` -- it does NOT honor HDLAB_EXP_NAME env var that queue_add sets. queue_add expects metrics at `data/exp_<HDLAB_EXP_NAME>/metrics.json` (per its line 17 contract); cell writes to `data/substrate_c1_entmax_envelope_sweep_v1/metrics.json`. Path mismatch -> validation fails -> queue_add exit=1 -> consumer moves manifest to failed/. The UserWarning at line 70 (CUDA allocator) was incidental noise; smoke actually exited 0 with HARD_PASS verdict. Fix is one-line cell change (mirror A4's pattern at exp_substrate_arch_b_replicate_n2048_v1.py:29-30).

**From:** Orchestrator (Infrastructure Custodian)
**To:** Exp-Dev (cell-author; fix lane), Skunkworks (cert; A3 SCHEMA-VET author)
**Date:** 2026-06-18 ~04:22
**Re:** Exp-Dev 04:17 A3-not-consumed flag; runner-log-first investigation per A4 lesson.

## Direct evidence (consumer log + gate log on remote)

```
[2026-06-18 07:19:04] PID=19440 PROCESS c1_entmax_envelope_sweep_v1.json
[2026-06-18 07:19:12] PID=19440 FAIL c1_entmax_envelope_sweep_v1.json:
                        queue_add exit=1 -- python.exe :
                        C:\dev\hd-instrument\experiments\exp_substrate_
                        c1_entmax_envelope_sweep_v1.py:70: UserWarning:

Gate log (data/gate_log_exp_substrate_c1_entmax_envelope_sweep_v1_smoke.txt):
   UserWarning: expandable_segments not supported on this platform
     (Triggered internally at ... CUDAAllocatorConfig.h:28)
     return (torch.randint(0, 2, shape, generator=g, device=device).float() * 2 - 1)
   [substrate_c1_entmax_envelope_sweep_v1] N=512 cluster=8 noise=0.15: ...
   [substrate_c1_entmax_envelope_sweep_v1] N=1024 cluster=8 noise=0.15: ...
   [substrate_c1_entmax_envelope_sweep_v1] run_mode=smoke device=cuda -> HARD_PASS
     cells=2 discriminating=2 non_disc=0 wins=2 win_frac=1.00 ...
     C1 ENVELOPE HOLDS: ...
```

The smoke ITSELF exits 0 with HARD_PASS (the C1 envelope IS holding). The
UserWarning is incidental (same warning A4's cell emits on the same CUDA
allocator config; A4 succeeded with it). So why did queue_add return exit=1?

## Root cause: cell doesn't honor HDLAB_EXP_NAME

```
C1 cell (line 40-41):
   ANCHOR = "substrate_c1_entmax_envelope_sweep_v1"
   OUT = REPO / "data" / ANCHOR       <-- writes to data/substrate_c1_entmax_envelope_sweep_v1/

A4 cell (line 28-30) -- the correct pattern:
   ANCHOR = "substrate_arch_b_replicate_n2048_v1"
   _EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
   OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
                          <-- writes to data/exp_<HDLAB_EXP_NAME>/

queue_add contract (queue_add.py line 17):
   "Script supports --smoke and exits 0, producing metrics.json at
    data/exp_{HDLAB_EXP_NAME}/metrics.json with required fields"

queue_add sets env: HDLAB_EXP_NAME=c1_entmax_envelope_sweep_v1_smoke
queue_add expects metrics at: data/exp_c1_entmax_envelope_sweep_v1_smoke/metrics.json
Cell writes metrics to: data/substrate_c1_entmax_envelope_sweep_v1/metrics.json
   -> queue_add doesn't find them -> validation fails -> exit 1
   -> consumer moves manifest to failed/
```

## Fix (one-line cell change; Exp-Dev's lane)

Change C1 cell lines 40-41 from:
```python
ANCHOR = "substrate_c1_entmax_envelope_sweep_v1"
OUT = REPO / "data" / ANCHOR
```

To (mirroring A4 line 28-30):
```python
ANCHOR = "substrate_c1_entmax_envelope_sweep_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
```

After fix + commit + push: re-dispatch with fresh name (the original
manifest is now in failed/; a fresh name avoids any duplicate-checking
confusion). The 120s self-test gate + sync-fix will all run clean.

## My self-check on the pattern

Same pattern Exp-Dev called out in our memory: cell-readiness checklist
requires honoring HDLAB_EXP_NAME (per the metrics-provenance-gate
discipline). A4 + refuse_gate + measured-8a all use it correctly. C1
cell is the outlier -- it predates the standardization, perhaps.

Diagnostic discipline applied: runner-log-first (read the gate log; found
the smoke succeeded + UserWarning was incidental); pattern-match against
known-good cell (A4 has the right pattern); identified the exact line
mismatch. Did NOT escalate as "consumer broken" or "queue_add broken" --
the consumer + queue_add are doing the right thing (rejecting a cell
that violated the metrics-path contract).

## Composes with the night's verify-the-referent theme

```
A4 dispatch-stall:    queue.json status=completed vs runner log (the
                      authoritative did-it-run referent)
Sync delta-gating:    global count vs per-file set diff (the right
                      file-set referent)
queue_add exit-0:     consumer trust vs queue-PENDING-entry (the right
                      consumer-side referent)
C1 path mismatch:     contract-doc-vs-cell-impl (the right cell-side
                      referent: "where did the cell ACTUALLY write?")

Same class. The discipline catches each by going one layer DEEPER than
the upstream signal.
```

## Standing / who I'm waiting on (9th rule)

- **Exp-Dev (cell-author):** one-line fix at experiments/exp_substrate_c1_entmax_envelope_sweep_v1.py:40-41 to honor HDLAB_EXP_NAME (mirror A4 pattern); commit + push; I re-dispatch with a fresh name (no naming collision; original in failed/)
- **Skunkworks (cert-owner):** A3 SCHEMA-VET PASS already done (the pre-reg + design); this is a cell-impl bug, not a design issue; if you want a SCHEMA-VET ratify on the one-line fix, say so
- **Research (Director):** GPU-track temporarily stalled (A3 was the priority); brief delay ~1 cycle until cell fix lands
- **USER (morning):** A3 dispatch stall diagnosed + cell-impl bug; not a substrate issue; reactive fix; will redispatch on cell fix
- **ME:** standing for Exp-Dev's cell fix; will re-dispatch immediately when commit lands; v5 + tail + cron healthy

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
