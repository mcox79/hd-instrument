# Pending experiment queue — running list

**Updated:** 2026-06-03 v361 exp_dev RESUME cycle (3 RESUME + 2 ADDITIONAL)

**Purpose:** Single source of truth for experiments waiting to be queued by orchestrator. Re-generated each cycle when there's a state change. User can read this anytime to see what's pending.

---

## Currently active (in remote queues — not "pending" for orchestrator)

GPU (overnight_queue):
- q_a3_l24_cross_layer_composition_v1_n16384 (completed) — RESUME; L=24 N=16384 5th rung; ran immediately on ship
- q_b1_bisect_d293_v1_n16384 (running) — ADDITIONAL A; Q-B1 bisection d=293 narrowing (287,300]; SHIPPED 2026-06-03

CPU (remote_cpu_queue):
- pp58_isochoric_kappa3_alpha0p05_n32768_v8_n32768 (running)
- pp56_sherman_morrison_cert_drop_n65536_v5_n65536 (pending)
- pp49_hrc_depth_parity_discriminator_sweep_v1_n4096 (pending) — Wave-5 Decisive #3
- pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384 (pending) — Wave-5 Decisive #1
- pp55_vsa_binding_n131072_v6_n131072 (pending) — 6th rung cross-N
- pp49_hrc_protocol_artifact_nscale_v1_n8192 (pending) — RESUME; PP-49 N-scale validation at N=8192; SHIPPED 2026-06-03
- pp58_bbp_discrete_fallback_v1_n16384 (pending) — RESUME; PP-58 BBP discrete universality; SHIPPED 2026-06-03
- pp33_mfpt_glauber_n32768_v2_n32768 (pending) — ADDITIONAL D; PP-33 MFPT 4th rung N=32768; SHIPPED 2026-06-03

---

## Waiting to ship — TIER 1 (next-cycle priority)

### From cycle-26+ carryover (still unshipped)

5. **PP-12 cross-N at N=16384 with reduced M (OOM workaround)** — GPU; original OOM'd at 22 GB
6. **Q-A3 L=34 + L=35 verdict-driven extensions** — if HP through L=30+ series continues

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
