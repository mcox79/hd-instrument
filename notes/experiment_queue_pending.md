# Pending experiment queue — running list

**Updated:** 2026-06-03 v360 exp_dev ship cycle (Wave-5 + supplementary)

**Purpose:** Single source of truth for experiments waiting to be queued by orchestrator. Re-generated each cycle when there's a state change. User can read this anytime to see what's pending.

---

## Currently active (in remote queues — not "pending" for orchestrator)

GPU (overnight_queue):
- q_b1_bisect_d281_v1_n16384 (running) — final Q-B1 bisection narrowing
- q_a3_l20_cross_layer_composition_v1_n16384 (pending) — Q-A3 cross-N N=16384 first rung
- q_a3_l21_cross_layer_composition_v1_n16384 (pending) — Q-A3 cross-N N=16384 second rung
- pp58_bbp_spectral_gap_calibration_v1_n16384 (pending) — Wave-5 Decisive #2; BBP calibration; SHIPPED 2026-06-03
- q_a3_l22_cross_layer_composition_v1_n16384 (pending) — supplementary C; L=22 N=16384 depth ladder; SHIPPED 2026-06-03
- q_a3_l23_cross_layer_composition_v1_n16384 (pending) — supplementary C; L=23 N=16384 depth ladder; SHIPPED 2026-06-03

CPU (remote_cpu_queue):
- pp58_isochoric_kappa3_alpha0p1_n16384_v6_n16384 (running)
- pp55_vsa_binding_n65536_v5_n65536 (pending)
- pp58_isochoric_kappa3_alpha0p05_n32768_v8_n32768 (pending)
- pp56_sherman_morrison_cert_drop_n65536_v5_n65536 (pending)
- pp49_hrc_depth_parity_discriminator_sweep_v1_n4096 (pending) — Wave-5 Decisive #3; parity discriminator; SHIPPED 2026-06-03
- pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384 (pending) — Wave-5 Decisive #1; MFPT N-scaling; SHIPPED 2026-06-03

---

## Waiting to ship — TIER 1 (next-cycle priority)

### From research routing v359 drill battery synthesis (SHIPPED 2026-06-03)

1. ~~**`pp58_bbp_spectral_gap_calibration_v1_n16384`**~~ **ACTIVE** (overnight_queue) — DECISIVE Wave-5 #2
2. ~~**`pp49_hrc_depth_parity_discriminator_sweep_v1_n4096`**~~ **ACTIVE** (remote_cpu_queue) — DECISIVE Wave-5 #3
3. ~~**`pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384`**~~ **ACTIVE** (remote_cpu_queue) — DECISIVE Wave-5 #1

### From cycle-26+ carryover

4. **Q-B1 d-293 N=16384** — final bisection of d-275/d-300 window (depending on d-281 verdict)
5. **PP-12 cross-N at N=16384 with reduced M (OOM workaround)** — GPU; original OOM'd at 22 GB
6. **Q-A3 L=34 + L=35 verdict-driven extensions** — already shipped this cycle but include cells L=36+ if HP

---

## Waiting to ship — TIER 2 (when bandwidth allows)

### From v343 backlog (mostly exhausted)
- Wave-3 lit-scan items (4 items, research-side — route to /research)

### Strategy-side cap_map row revisions (per v359 routing §2; not empirical experiments)
- PP-52 framing update (Hebbian = GD fixed-point + 500-5000× wall, retire 1000× FLOPs gate)
- PP-49a Q-B1 envelope (chain_depth_max(α) = 22/(0.302-α); B=4 multi-bank extension)
- PP-12 / Q-A3 ECC unlimited-depth upgrade
- PP-50 κ_3 envelope 4.6× wider (σ_g_crit = 0.833 not 0.18)
- PP-33 MFPT N^(1/3) hypothesis re-OPENED contingent on Wave-5 #1 outcome

These go via /strategy_scribe (annotation-only). Defer to cap_map v361 strategy_scribe pass.

---

## Blocked (waiting on research)

Per `data/blocked_items.json`:
- `combo1_v5*` — needs per-pattern MMD formula spec
- `pp47_v3*` — needs circular K-space topology spec

---

## How to use this file

- Orchestrator main thread updates this on every cycle that ships or receives new research routings
- User can read it anytime to see what's queued
- Items dispatched to exp_dev should be removed/checked-off
- Mark items "ROUTING-PARKED" when research input is needed
