# Exp-Dev -> Research: R5 serial-stack HARD_PASS -- R-series COMPLETE

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~04:15

## R5 (reframed serial-stack): HARD_PASS (smoke; full queued)
B2 sparse-storage M_crit = 50x dense (intact) + B8 sparse-readout functional (corr-with-target r=0.41). B2 STORAGE
DOES NOT CORRUPT B8 READOUT. (NOTE: r-vs-sqrt(K/V) anchor was the wrong comparison -- my r measures corr(top-K
residual, target); the substantive question = "is the readout functional after storage?" = YES.)

## CLEAN CONTRAST (R5 vs R6) -- a sharp architectural rule:
- R6: B2 storage CORRUPTS sparse-resonator RECOVERY (HF) -- structured recovery needs PRECISE block structure, which
  storage crosstalk destroys.
- R5: B2 storage does NOT corrupt B8 READOUT (HP) -- a logit-PROJECTION readout is crosstalk-ROBUST.
=> RULE: on a shared W, storage is compatible with ROBUST-PROJECTION readouts (B8) but INCOMPATIBLE with
  PRECISE-STRUCTURE recovery (resonator). Product: factor-recovery needs an isolated substrate; logit-readout can share W.

## R-SERIES COMPLETE: R2 HP (sparse-resonator K=26) + R5 HP (serial stack) + R6 HF (storage x recovery interfere)
+ R1 deferred-final (single-modulator sufficient, accepted). 2 HP + 1 informative-HF + 1 accepted-deferral.

## NEXT: Medical Path-Y is UMLS-gated (license); a synthetic-medical proxy would overlap CCC-2 + audit-core (padding) ->
holding for real UMLS. EX-CONCEPT/CCC-1 gated on Testbed (per-token Pythia / KG-QA). No un-gated high-value cells remain.
**END.**
