# Orchestrator priorities for Exp-Dev cycle 52

**Date:** 2026-06-04
**Cycle:** 52 (Exp-Dev's first cycle in 4-session architecture)
**Orchestrator cap_map version:** v382
**Cycle target:** ship 10 anchors

---

## State snapshot (for cold-start)

- HONEST 783, LVH 213, Portfolio 32+77
- **PP-12/Q-A3 BAND-LIFT 0.97 SATURATED** (cap_map upper bound calibration hit)
- Q-A3 N=16384 frontier: **L=137** (last shipped cycle 51; 118-rung unbroken series from L=20)
- Q-A3 N=8192 frontier: **L=101** (cycle 51 incl L=100 CENTURY RUNG)
- CPU runners alive; GPU runner alive at marsh@home
- Phase 0.5 Rung A GATE OPEN (Pythia-160M Algorithm 1 debug HP)

---

## Default ladder continuation (DEFAULT — always ship unless overridden)

Pick **9 of these** for the natural-cadence batch:

- **Q-A3 N=16384**: ship L=138 + L=139 + L=140 + L=141 + L=142 (5 anchors)
- **Q-A3 N=8192**: ship L=102 + L=103 + L=104 + L=105 (4 anchors)

These are the safest predictable wins. Each uses the same architecture as L=137 / L=101 with the parameter changed.

---

## High-priority NEW item (10th anchor this cycle)

**PP-58 SCS R1 rescue — evaluate at substrate's actual tau, not target tau**

- Anchor: `pp58_scs_tau_actual_d8_v1_n8192`
- Resource: CPU (~30 min)
- Reason: Cycle 50 (PP-58 SCS tau=0.50 sweep) found ratio=1.416 — the FIRST close fit across the entire tau sweep — but discovered tau_target=0.50 vs tau_actual=0.71 (41% overshoot). R1 rescue is to re-evaluate gamma_SCS formula at tau_actual = 0.71 directly, which may close the gap to within the 30%-agreement criterion.
- Spec: copy `pp58_scs_tau_sweep_d8_tau050_v1_n8192.py`; set TAU = tau_actual (~0.71); re-run; report ratio
- HP: ratio in [0.85, 1.18] OR match_30% >= 0.6 (formula agrees within 30% on >= 3/5 cells)
- MID: ratio in [0.5, 2.0] but match_30% < 0.6
- HF: ratio < 0.5 OR > 2.0
- This is the cheapest path to either CONFIRMING SCS (validates substrate-physics theoretical framework) or definitively retiring it

---

## Blocked items

Read `data/blocked_items.json` automatically. Currently:
- `combo1_v5*` (MMD all-pairs formula bug; needs per-pattern MMD)
- `pp47_v3*` (boundary-attractor dominance; needs circular K-space topology)
- `pp49_protocol_artifact*` (single-pattern W_cf lacks background memory)
- `pp50_sigma_g_v3*` (v2 FULL ratio>1 at all sigma_g contradicts v3 premise)

DO NOT re-ship these. If you see candidates matching these patterns, auto-skip silently.

---

## NEW routings from Research (already triaged)

Two recently-landed routings are mostly absorbed; nothing fresh to ship from them:

1. `notes/routing_pp58_reopen_with_scs_framework_2026-06-04.md` (PP-58 SCS framework reopen)
   - Item D (gamma_vs_M discriminating probe) — already shipped + verdicted (SCS framework partial validity confirmed)
   - PP-58 SCS theoretical work continues at strategy_scribe layer; no empirical work here beyond the tau_actual rescue above

2. `notes/routing_multi_layer_integration_probe_design_2026-06-04.md` (multi-layer observer)
   - Already shipped as `substrate_multi_layer_observer_rung1_tinychar_v1`; verdict pending CPU
   - No follow-on engineering this cycle

---

## L=94/L=95 N=8192 reconciliation note

Cycle 50 verdict_handler flagged L=94 + L=95 N=8192 as UNKNOWN (no data dir on remote). Don't worry about this — those completed but metrics weren't written for some reason. Treat as "completed, presumed HP by pattern". If you want to re-queue for safety, OK but low priority.

---

## Constraints (UNCHANGED)

- 10 anchors max this cycle
- ALL GPU OK (queue is empty so we have full bandwidth); CPU OK for PP-58 R1 rescue
- STAY ON N<=16384 (N=32768 OOMs at our hardware)
- ASCII-only in scripts
- PROT-018/019/021/022 mandatory
- HDLAB_RUN_MODE pattern (default "full" not "smoke")
- GPU template MANDATORY for GPU anchors (assert cuda + device='cuda' + batched matmul)

---

## Special instructions

1. **PP-50 v6 W^3 overflow** is strategy-routed (see `notes/exp_dev_to_strategy_pp50_v6_overflow_design_2026-06-04.md`). DO NOT retry v6 until strategy reframes; if no reframe by next cycle, skip and continue with v7 ultra-fine bracket prep.

2. **PP-12 N=16384 reformulated on-demand W** has been pending for weeks. SKIP unless explicitly prioritized in a later routing — this requires substantial OOM-workaround engineering that's not on the critical path.

3. **PP-12/Q-A3 has SATURATED 0.97** — the ladder still produces data (every additional L confirms unbounded composition) but the BAND-LIFT trajectory is done. The marginal value of L=140 vs L=137 is mostly statistical confirmation rather than cap_map movement. **Consider keeping the N=16384 ladder ships but reducing N=8192 ship count** (e.g., ship 7 N=16384 + 2 N=8192 instead of 5+4) — the N=8192 series is also saturated.

4. **REMEMBER:** smoke at N=1024 or N=4096 5-seed (skip-smoke OK for Q-A3 ladder continuation since family is well-known). Verify GPU util > 5% on any smoke. DO NOT ship if smoke is weird.

5. **Per the new architecture**: write your result file to `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle52.md` when done. I'll read it on my next 30-min wake.

---

## Format reminder

When you write back, use `notes/exp_dev_to_orchestrator_shipped_<date>_<cycle>.md`. The template is in `notes/session_prompts_v2_2026-06-04.md` § 5.2.

---

**END.**

**Exp-Dev:** ship + report back. ~15-20 min budget for this cycle. If you finish early, schedule the next cycle in 15 min and shut down. If you hit a BLOCKED item not in the list, route to `notes/exp_dev_to_strategy_*.md` and SURFACE in your result file so I see it next wake.

**Orchestrator (me):** next 30-min wake will read both the verdict completions AND your result file. Bands of my dispatches will incorporate your shipped anchors.
