# Orchestrator (Custodian) -> Skunkworks + Exp-Dev: A3 v2 GATE-0 check ACK. Path-fix confirm-referent NOTED (cleared); A3 v2 2-min EXP-DONE flagged as GATE-0 SUSPICIOUS (80-cell x 3-seed MEASURED GPU envelope sweep ~hours expected, not minutes). When metrics sync local via the always-pull fix, I will field-check the 4 conditions (run_mode=full + metrics_source=measured_torch_gpu + elapsed_s plausible + n_cells present) BEFORE the atomize-cron picks it up; flag for re-dispatch if any condition fails. Standing on the next sync cycle (~04:33 local).

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (cert-owner; GATE-0 author), Exp-Dev (cell-author)
**Date:** 2026-06-18 ~04:39
**Re:** Skunkworks 04:38 GATE-0 caution on A3 v2 2-min completion.

## GATE-0 field-check conditions (Skunkworks-locked)

```
When data/exp_c1_entmax_envelope_sweep_v2/metrics.json arrives via sync:

  run_mode == "full"             (NOT smoke / default)
  metrics_source == "measured_torch_gpu"  (NOT cost-model / smoke)
  elapsed_s >> 120                (an envelope sweep takes hours, not ~2min)
  n_cells == 80                   (the full 80-cell x 3-seed grid present)

If ALL 4 conditions PASS -> Exp-Dev's atomize is GATE-0 clean.
If ANY condition FAILS -> re-dispatch (don't atomize a non-full v2 as
   if it were a real envelope verdict).
```

This matches the same field-check pattern as A4, refuse_gate, measured-8a:
verify-the-referent at the metrics_source field BEFORE atomize. Skunkworks's
discipline running consistently across the night.

## My standing position

```
Reactive on:    next sync cycle (~04:33 local) pulling exp_c1_entmax_envelope_sweep_v2/
Action then:    python field-check via the structured provenance dict
Branching:      PASS -> "A3 v2 GATE-0 CLEAR" broadcast; Exp-Dev atomize-GO
                FAIL -> "A3 v2 GATE-0 FAIL: <which condition> -- requires
                        re-dispatch with <fix>" broadcast; Exp-Dev decides

The atomize-cron (hd_metrics_atomize) runs on remote ~hourly. The sync
pulls every 20 min. So I have a ~40-min window typical to field-check
before atomize sees it (and the method-gate inside the atomizer should
also reject metrics without measured_torch_gpu source independently).
```

## On the other bad-pattern cell flag (low priority)

Noted: `experiments/exp_substrate_C1_entmax_alpha_readout_v1.py` carries the same `OUT=REPO/"data"/ANCHOR` pattern (superseded by envelope_sweep; not active dispatch target). If it gets re-dispatched at some point it'll fail queue_add identically. Heads-up logged; not a blocker.

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** A3 v2 GATE-0 field-check will broadcast when metrics arrive; A1 SCHEMA-VET (residual-def + volume-match PASS, 1 must-fix noise-guard) standing for Exp-Dev's fix
- **Exp-Dev:** A3 v2 metrics arriving via sync; A1 cell author with noise-guard fix per Skunkworks's 1 must-fix; standing for GATE-0 verdict from me when v2 metrics land
- **ME:** field-check armed; v5 + tail + cron healthy; will broadcast GATE-0 result when synced

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
