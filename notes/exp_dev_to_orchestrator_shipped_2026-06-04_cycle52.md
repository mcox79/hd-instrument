# Exp-Dev shipped report -- cycle 52

**From:** Exp-Dev session
**To:** Orchestrator
**Date:** 2026-06-04
**Cycle:** 52 (first Exp-Dev cycle in 4-session architecture)
**cap_map version at dispatch:** v382

---

## Summary

Shipped 10 anchors. All 10 SCP'd, gated, `--self-test` passed on remote, and post-ship VERIFIED
present in remote queue.json. Both queues were EMPTY at cycle start (overnight pending=0 running=0;
remote_cpu pending=0 running=1). Runner is already churning: L=138/L=139 completed, L=140 + PP-58
running, remainder pending.

Split: took the saturation-aware option from priorities note #3 (7 N=16384 + 2 N=8192) instead of
the 5+4 default, since PP-12/Q-A3 is SATURATED 0.97 and the N=8192 series is also saturated -- weighted
toward the deeper N=16384 frontier.

---

## Anchors shipped

### GPU (overnight_queue), timeout 21600s each (PROT-019 floor)
| Anchor | L | N | status@report |
|---|---|---|---|
| q_a3_l138_cross_layer_composition_v1_n16384 | 138 | 16384 | completed |
| q_a3_l139_cross_layer_composition_v1_n16384 | 139 | 16384 | completed |
| q_a3_l140_cross_layer_composition_v1_n16384 | 140 | 16384 | running |
| q_a3_l141_cross_layer_composition_v1_n16384 | 141 | 16384 | pending |
| q_a3_l142_cross_layer_composition_v1_n16384 | 142 | 16384 | pending |
| q_a3_l143_cross_layer_composition_v1_n16384 | 143 | 16384 | pending |
| q_a3_l144_cross_layer_composition_v1_n16384 | 144 | 16384 | pending |
| q_a3_l102_cross_layer_composition_v1_n8192 | 102 | 8192 | pending |
| q_a3_l103_cross_layer_composition_v1_n8192 | 103 | 8192 | pending |

L=138-144 extend the N=16384 frontier from L=137 (rungs 119-125; 119-rung+ unbroken series from L=20).
L=102-103 extend the N=8192 frontier past L=101.

### CPU (remote_cpu_queue), timeout 21600s
| Anchor | status@report |
|---|---|
| pp58_scs_tau_actual_d8_v1_n8192 | running |

---

## FLAG 1 -- PP-58 design ambiguity (needs orchestrator confirm next wake)

Spec said "copy pp58_scs_tau_sweep_d8_tau050_v1_n8192.py; set TAU = tau_actual (~0.71); re-run".
I implemented TAU_TARGET = 0.71 in the controlled-asymmetry build, with gamma_SCS evaluated at the
MEASURED tau_actual (matching "evaluate at substrate's actual tau"). Bands per your spec:
HP ratio in [0.85,1.18] OR match_30% >= 0.6; MID ratio in [0.5,2.0] & match<0.6; HF ratio <0.5 or >2.0.

**Caveat found in smoke (N=256):** building with tau_target=0.71 OVERSHOOTS to tau_actual=0.93, so
the substrate operates ABOVE 0.71, not AT it. The overshoot is inherent to the W-build (same mechanism
that turned tau_target=0.50 -> tau_actual=0.71 in cycle 50). Two readings of intent diverge here:
- (A, what I shipped) crank build target to 0.71 -> substrate sits ~0.93; tests SCS in a high-asymmetry regime.
- (B) make the substrate actually OPERATE at tau_actual~0.71 -> requires tau_target~0.50, which REPRODUCES
  cycle 50's W unchanged (already gives ratio=1.416, MIDDLE under the new bands).

Neither reading cleanly "closes the gap." I shipped (A) as the literal reading to keep the (empty) queue
moving; the run is cheap and falsifiable. **If you intended (B) or a calibrated tau_target that yields
tau_actual=0.71, say so and I'll re-ship next cycle.** Note documented in the prereg too.

Note: the reference tau050 script ALREADY computes gamma_SCS at tau_actual (not target), so a pure
"re-evaluate at tau_actual" with the same build is a no-op vs cycle 50.

---

## FLAG 2 -- "completed" GPU anchors with no findable metrics.json

L=138/L=139 show status=completed but `data/<anchor>/metrics.json` is not at the expected remote path
(Get-Content path-not-found). This looks like a recurrence of the L=94/L=95 N=8192 reconciliation issue
you flagged (completed, metrics not written / wrong dir). Surfacing for verdict_handler -- I did not
chase it (verdict territory is yours). Possibly get_output_dir writes under a run_mode/timestamped
subdir; worth a one-time check of the output-dir convention vs where verdict_handler reads.

---

## FLAG 3 -- research-notes-to-orchestrator with buildable experiments (per user directive)

User directed: "any notes to orchestrator that have experiments to build are now for you." I scanned the
newest routings. Findings:
- `routing_consolidated_rescues_5_brain_inspired_hf` + `routing_engineering_priority_nudge`: the concrete
  buildable items (Experiment C rung-1 8-channel orchestration; spectral-monitor scale-gate rerun at
  TRAIN_CHARS=100k-200k; substrate-trained mini-LM rescue) all require the **tiny char-LM scaffold +
  substrate-observer wiring**, which is Testbed engineering and does NOT exist as a stamp-from-template.
  Most are explicitly HOLD pending 5 in-flight research drills (~30-60 min wall). I could not stamp these
  this cycle without that scaffold.
- Tier 1 (spectral-monitor overfitting-sentinel reframe) is annotation-only (strategy_scribe), not an experiment.

**Ask:** if you want me to OWN building the tiny char-LM scaffold (vs Testbed), confirm and I'll scope it
as a multi-cycle engineering item. Otherwise these stay HOLD pending drills + scaffold.

---

## Cadence change (per user directive, this turn)

User: "load up 10 experiments, highest priority, every 30 minutes." Switching my cadence from 15-min to
**30-min, 10 highest-priority anchors per cycle**. ScheduleWakeup armed for 1800s.

---

## Discipline checklist
- PROT-018: all anchors N-suffix verified by gate. OK.
- PROT-019: all timeouts 21600s >= floor for _n>=4096. (PP-58 first attempt at 14400 rejected; re-shipped 21600.) OK.
- PROT-021: seed checkpoints keyed run_mode + L (ladder) / run_mode + seed (PP-58). OK.
- PROT-022: formula self-tests present + passed on remote. OK.
- ASCII-only: all 10 scripts scanned, 0 non-ASCII. OK.
- blocked_items.json: read; no shipped anchor matches a blocked pattern. OK.
- Single atomic commit for the cycle. (this commit)

---

**END.** Next Exp-Dev wake: +30 min.
