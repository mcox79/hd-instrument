# exp_dev handoff: cycle 14 queue refill (2026-06-02)

**Trigger.** Cycle 14 verdict batch completed. Queue empty (gpu_pending=0, cpu_pending=0). Pause flag ABSENT. Queue refill required per pipeline-pacing invariant.

**Cap_map state after v345 commit bdf036d.**
- PP-50 tamper-detection: 0.75-0.90 (was 0.70-0.85; I-12 CLOSED; N=16384 confirmed)
- PP-48 NKT depth: 0.75-0.90 (was 0.70-0.85; depth-13 cross-N at N=8192; depth-17 at 131K nodes)
- Q-A3/PP-12 composition: 0.75-0.90 (UNCHANGED; L=12 ceiling not reached; L=13+ eligible)
- Q-B1/PP-49a chain: band UNCHANGED; depth-55 not ceiling (d55=0.9949>>HP=0.25); depth-60+ eligible
- I-16 OPEN: PP-49 HRC counterfactual depth-5 HARD_FAIL (R1-R5 filed v340)
- PP-48/PP-49 cross-N cloud band-lift pending (local N=32768 HP but cloud combo2-direct not yet confirmed)

**Open handoff opportunities (priority order).**

1. Q-B1/PP-49a chain depth ceiling probe: depth-60 + depth-65 at N=8192. d55=0.9949 at full N means ceiling is far beyond d=55. Depth-60/65 to characterize the actual ceiling.
2. Q-A3/PP-12 composition depth: L=13 at N=4096. L=12 EXACT-1.0; L=13 eligible.
3. PP-48 NKT cross-N at N=8192 depth extension: depth-15 or depth-17 at N=8192 to establish depth x N=8192 cross-N product envelope.
4. PP-48/PP-49 cloud combo2-direct at N=32768 to lift both rows to 0.80-0.95 (pending v339 routing still open).
5. I-16 rescue: PP-49 HRC counterfactual depth-5 rescue variant (R2: increase K for higher baseline_cos).
6. PP-50 kappa3 depth extension: sigma_sep at N=32768 with v3 delta-alpha protocol to confirm N-scaling above v335 founding.

**Contract.** exp_dev designs anchors with preregs per envelope-fail-bands; no inline experiment design in this file. Dispatch via queue_add.sh GPU or CPU as appropriate. Post-ship REMOTE VERIFY per role contract.
