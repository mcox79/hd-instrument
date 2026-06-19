# exp_dev Routing: Cycle 33 Queue Refill

**Date:** 2026-06-03
**Trigger:** v364 CYCLE 33 verdict batch processed; GPU overnight_queue at 0 pending.
**Pause flag:** ABSENT (ACTIVE)
**Cap_map version:** v364

## Open strategic questions (priority order)

### Q1 (HIGH): PP-12/Q-A3 -- push L=37+ at N=16384
Current state: N=16384 series {L=20..L=36} = 14 rungs, all EXACT-1.0000. FIRST L=36 in project.
L=36+ N=16384 would establish a multi-rung lead over N=4096 (currently 1-rung lead) and unlock band-lift.
Contract: L=37 (and optionally L=38) at N=16384, 5-seed full, GPU. Pre-reg vs q_a3_l33_l36_n16384 pattern.

### Q2 (MEDIUM): PP-12/Q-A3 -- extend N=4096 ceiling chase to L=36+
Current state: N=4096 series L=2..L=35 all EXACT; L=36 not tested at N=4096.
L=36 N=4096 would close the 2-N cross-N at L=36 and confirm N-independence of the ceiling position.
Contract: L=36 at N=4096, 5-seed full, GPU. Fast wall expected (~1s).

### Q3 (MEDIUM): PP-12/Q-A3 -- N=8192 cross-N gap L=26..L=36
Current state: N=8192 series {L=19,L=22,L=23,L=24,L=25}; L=26..L=36 at N=8192 pending.
Contract: L=26, L=27, L=28 at N=8192 (GPU, 5-seed); bridges gap toward L=36.

### Q4 (LOW-MEDIUM): PP-50 sigma_g protocol audit (R2 baseline)
Current state: sigma_g_crit~0.833 RETRACTED; R1 protocol audit is free (no compute); R2 is sigma_g=0 baseline.
Contract: Run sigma_g=0 baseline check at N=4096 and N=8192 (expected ratio=1.0; confirms formula calibration). CPU, fast (<1min each).

## Autonomy
exp_dev selects which of Q1-Q4 to dispatch, sizes appropriately (no padding), and designs anchors with pre-reg bands. GPU queue is primary. CPU queue for Q4 if warranted.
