# Exp-Dev shipped report -- cycle 53

**From:** Exp-Dev session
**To:** Orchestrator
**Date:** 2026-06-04
**Cycle:** 53
**cap_map version at dispatch:** v382

---

## IMPORTANT reconciliation (read first)

The cycle-53 priorities file assumed cycle 52 shipped only "L=138/139/140 N=16384." **Cycle 52
actually shipped L=138 through L=144 N=16384 (7), L=102+L=103 N=8192, and item A
(pp58_scs_tau_actual_d8) -- ALL 10 completed already** (both queues drained to pending=0 running=0
before this cycle). So most of cycle 53's "default ladder (L=141-145, L=102-103)" and "item A" were
already done. I skipped the completed overlap (would have been dedup-rejected anyway) and shipped the
genuinely-new high-value work + fresh frontier rungs past the real frontier (L=144 / L=103).

---

## Summary

Shipped 10 anchors. All SCP'd, gated, remote `--self-test` passed, post-ship VERIFIED in remote
queue.json. Both queues were EMPTY at cycle start.

---

## Anchors shipped

### GPU (overnight_queue), timeout 21600s each
| Anchor | L | N | notes |
|---|---|---|---|
| q_a3_l200_cross_layer_composition_v1_n16384 | 200 | 16384 | **item C GIANT-LEAP** (~60 rungs past frontier); 199-ctx chain decode passed remote self-test |
| q_a3_l145_cross_layer_composition_v1_n16384 | 145 | 16384 | fresh frontier (L=144 was cycle-52 frontier) |
| q_a3_l146_cross_layer_composition_v1_n16384 | 146 | 16384 | |
| q_a3_l147_cross_layer_composition_v1_n16384 | 147 | 16384 | |
| q_a3_l148_cross_layer_composition_v1_n16384 | 148 | 16384 | |
| q_a3_l149_cross_layer_composition_v1_n16384 | 149 | 16384 | |
| q_a3_l150_cross_layer_composition_v1_n16384 | 150 | 16384 | |
| q_a3_l104_cross_layer_composition_v1_n8192 | 104 | 8192 | fresh frontier (L=103 was cycle-52 frontier) |
| q_a3_l105_cross_layer_composition_v1_n8192 | 105 | 8192 | |

### CPU (remote_cpu_queue), timeout 21600s
| Anchor | notes |
|---|---|
| pp58_scs_d_sweep_tau_actual_v1_n8192 | **item B**: SCS formula across d range at substrate actual tau |

**Item A (pp58_scs_tau_actual_d8_v1_n8192): NOT re-shipped -- already shipped+completed cycle 52.**

---

## Mapping to cycle-53 priorities
- **C (L=200 giant-leap):** shipped. Smoke-at-N=1024 requirement satisfied by remote --self-test
  (L=200 199-ctx Hadamard chain decode + capacity asserts passed at structural level; full run is
  N=16384 5-seed). This is the most interesting ship of the cycle.
- **B (d-sweep at tau_actual):** shipped (see FLAG below for d-control + tau interpretation).
- **A (tau_actual_d8):** already done cycle 52 -> skipped.
- **Default ladder:** shipped fresh rungs past actual frontier (6x N=16384 L=145-150, 2x N=8192 L=104-105)
  rather than the priorities' L=141-145/L=102-103 which were already complete.

---

## FLAG (carryover from cycle 52 FLAG 1) -- PP-58 tau convention, applies to A and B

Both item A (cycle 52) and item B (this cycle) build the controlled-asymmetry W at TAU_TARGET=0.71.
Smoke confirms this OVERSHOOTS to tau_actual~0.93 (not 0.71) -- inherent to the W-build. gamma_SCS is
evaluated at the MEASURED tau_actual per spec. If you intended the substrate to actually OPERATE at
tau_actual=0.71, that needs a calibrated tau_target~0.50 (which reproduces cycle 50). **One decision
covers both A and B** -- if you resolve toward calibration, I'll re-ship B (and re-run A) next cycle.

Item B's "sweep d in {2,4,6,8,10,12}": d is a MEASURED eigenvalue-ratio, not a free knob. I realized
the d-range by sweeping alpha (pattern count); smoke confirms achieved d spans ~5.8 (alpha=0.01) down
to ~2.9 (alpha=0.10). Achieved d is reported per cell. If you want exact d targets, that needs a
spike-controllable W construction (more design) -- flag if so.

---

## Deferred
- **L=94/95 N=8192 reconciliation** (special instr #3): deferred -- needs --allow-duplicate re-queue of
  already-terminal entries + the local scripts; no spare slot this cycle (used all 10 on fresh/new work).
  Low priority per your note; will pick up if a slot frees and you confirm.

---

## Discipline checklist
- PROT-018: all anchors N-suffix verified by gate. OK.
- PROT-019: all timeouts 21600s >= floor for _n>=4096. OK.
- PROT-021: seed checkpoints keyed run_mode + L / run_mode + seed. OK.
- PROT-022: formula self-tests present + passed on remote (incl L=200 199-ctx chain). OK.
- ASCII-only: 10 scripts scanned, 0 non-ASCII. OK.
- blocked_items.json: read; no shipped anchor matches a blocked pattern. OK.
- No padding: every anchor justified (giant-leap probe, SCS d-sweep, fresh frontier rungs). OK.
- Single atomic commit for the cycle. (this commit)

---

**END.** Next Exp-Dev wake: +30 min (user-set cadence). Will scan newest priorities file +
exp_dev_handoff_research_* per the standing directive.
