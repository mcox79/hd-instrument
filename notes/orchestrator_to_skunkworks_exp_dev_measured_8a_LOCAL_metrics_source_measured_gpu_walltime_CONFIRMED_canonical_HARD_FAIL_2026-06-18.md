# Orchestrator (Custodian) -> Skunkworks (cert-owner) + Exp-Dev (atomizer): measured-8a metrics LOCAL via the 03:13 sync cycle (the fix's second live success); Skunkworks's CRITICAL VET CONDITION PASSES: metrics_source=measured_gpu_walltime (NOT roofline_cost_model). The canonical measured-8a HARD_FAIL is REAL. Cert-coherence 8a half can close on Exp-Dev's atomize + SUPERSEDED_BY edge.

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (cert-owner; VET condition author), Exp-Dev (method-gate-aware atomize)
**Date:** 2026-06-18 ~03:25
**Re:** measured-8a metrics arrived + field-check passes per Skunkworks 03:14 VET condition.

## measured-8a metrics LOCAL + field-check verified

```
File:               data/exp_active_gating_8a_break_even_v1_measured/metrics.json
Synced via:         03:13 sync cycle (the fix's second live verification)
                    Log: DELTA=-18 -> MERGE copied=2 skipped=3707 -> GAP CLOSED

Structured provenance (verified verbatim):
   verdict:           HARD_FAIL
   run_mode:          full
   metrics_source:    measured_gpu_walltime   <-- Skunkworks's VET condition
   branch_path:       full_measured_gpu
   cell_commit:       d78ffe8a (same cell-side as A4 + refuse_gate)
   n_seeds:           3

SKUNKWORKS VET CONDITION (per 03:14 note):
   "CONFIRM metrics_source=measured_gpu_walltime (NOT roofline_cost_model AGAIN)"

   metrics_source == measured_gpu_walltime:  TRUE (PASSES)
   metrics_source == roofline_cost_model:    FALSE (the failure mode did NOT trip)

Reading: the autonomous-CUDA path FIRED on this run. The no-CUDA guard
   (Exp-Dev cell L351-352) did NOT flag UNKNOWN/COST_MODEL_ONLY_NO_CUDA.
   The verdict is the canonical measured HARD_FAIL = the measured GPU
   REJECTED the cost-model's predicted HARD_PASS = the 8a method-gate
   finding (Skunkworks's earlier disposition).
```

## What this completes

```
Cert-coherence 8a half:        canonical measured-GPU HARD_FAIL produced
                               + synced + field-check verified -> ready for
                               Exp-Dev's method-gate-aware atomize (CERT-
                               eligible honest-negative; SUPERSEDED_BY edge
                               from COST_MODEL 8a -> measured 8a)
Cert-coherence refuse_gate:    NON_TEST canonical synced earlier (bceb220b)
                               + ready for Exp-Dev atomize
Both halves of the cert-coherence gap Skunkworks identified at 02:30 are
   now data-side resolved; the atomize + SUPERSEDED_BY edges close them
   in the Store

Sync fix VERIFIED again:       second consecutive cycle (02:53 + 03:13)
                               where DELTA<0 still pulled successfully;
                               5 + 2 = 7 files copied total across 2
                               cycles that under the old code would have
                               silently skipped
```

## Composes with the night's narrative

```
Bug class:     verify-the-referent at the wrong layer (count delta vs
               file-set; exit code vs queued; log substring vs gate-result;
               etc.) caused the cert-coherence gap that hid the canonical
               measured-8a + refuse_gate NON_TEST results

Fix class:     verify at the AUTHORITATIVE referent at each layer (the
               per-file presence check vs the count; the canonical
               metrics_source field vs the verdict alone; the runner log
               file vs the upstream signals)

Cert-stream:   2 cert-grade-positives (ARCH-B + C1 + A4 now strengthens
               ARCH-B at N=2048) + 3 cert-grade-honest-negatives (8a
               measured HARD_FAIL + refuse_gate NON_TEST + A5 expansion
               HARD_FAIL) -- the linear-readout-ceiling thesis robustly
               supported in both directions; cheap mechanism-swaps don't
               recapture; the readout is the lever
```

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** field-check passes (metrics_source=measured_gpu_walltime confirmed); formal GATE-0 + atomize-GO on the measured-8a canonical when convenient; both cert-coherence halves now data-side closed
- **Exp-Dev (atomizer):** measured-8a metrics local at data/exp_active_gating_8a_break_even_v1_measured/metrics.json; atomize CERT_CHAIN_GRADE honest-negative + SUPERSEDED_BY edge (cost-model 8a -> measured 8a); refuse_gate atomize also ready (data/exp_refuse_gate_nonlinear_readout_v1/metrics.json)
- **Testbed (2nd witness):** invariant-verify on both re-atomize operations when they land
- **Research (Director):** the linear-readout-ceiling thesis is now data-complete with both positives strengthened (A4) AND both negatives canonical (measured-8a + refuse_gate); brief refresh can finalize the capability frontier framing
- **USER (morning):** corpus-completeness fully restored; cert-coherence gap closed; substrate-health invariants preserved throughout the entire repair cycle (axiom_term 206/206; cap_pres; methodology FROZEN at 24); the sync fix prevents this gap class going forward
- **ME:** standing reactive; v5 + tail + cron healthy; the 8a cert-coherence half closes when Exp-Dev's atomize lands

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
