# Pending experiment queue — running list

**Updated:** 2026-06-03 v362 REFILL cycle 2 (5 GPU anchors shipped: Q-A3 L=33..L=36 N=16384 + PP-50 sigma_g N=8192)

**Purpose:** Single source of truth for experiments waiting to be queued by orchestrator. Re-generated each cycle when there's a state change. User can read this anytime to see what's pending.

---

## Currently active (in remote queues — not "pending" for orchestrator)

GPU (overnight_queue):
- q_a3_l26_cross_layer_composition_v1_n16384 (pending) — v361 REFILL; L=26 N=16384 7th rung; SHIPPED 2026-06-03
- q_a3_l27_cross_layer_composition_v1_n16384 (pending) — v361 REFILL; L=27 N=16384 8th rung; SHIPPED 2026-06-03
- q_a3_l28_cross_layer_composition_v1_n16384 (pending) — v361 REFILL; L=28 N=16384 9th rung; SHIPPED 2026-06-03
- q_b1_bisect_d278_v1_n16384 (pending) — v361 REFILL; Q-B1 bisection d=278; onset (275,281] -> this bisect (275+281)//2=278; d293 HF confirmed; SHIPPED 2026-06-03
- pp50_kappa3_delta_alpha_n65536_v1_n65536 (pending) — v361 REFILL; PP-50 6th-rung cross-N N=65536; BAND-LIFT eligible if HP; SHIPPED 2026-06-03
- q_a3_l29_cross_layer_composition_v1_n16384 (pending) — v362 REFILL; L=29 N=16384 10th rung; SHIPPED 2026-06-03
- q_a3_l30_cross_layer_composition_v1_n16384 (pending) — v362 REFILL; L=30 N=16384 11th rung; SHIPPED 2026-06-03
- pp50_kappa3_sigma_g_ext_v2_n4096 (pending) — v362 REFILL; PP-50 I-19 rescue extended sigma_g sweep 0.01..1.20; SHIPPED 2026-06-03
- pp50_kappa3_delta_alpha_n32768_v3_n32768 (pending) — v362 PRIORITY RESCUE; N=65536 OOM -> N=32768 v3 protocol; VRAM 1.26GB; SHIPPED 2026-06-03
- q_a3_l31_cross_layer_composition_v1_n16384 (pending) — v362 PRIORITY; L=31 N=16384 12th rung; smoke all EXACT-1.0; SHIPPED 2026-06-03
- q_a3_l32_cross_layer_composition_v1_n16384 (pending) — v362 PRIORITY; L=32 N=16384 13th rung; smoke all EXACT-1.0; SHIPPED 2026-06-03
- q_a3_l33_cross_layer_composition_v1_n16384 (pending) — v362 REFILL-2; L=33 N=16384 14th rung; PROT-018/019 OK; SHIPPED 2026-06-03
- q_a3_l34_cross_layer_composition_v1_n16384 (pending) — v362 REFILL-2; L=34 N=16384 15th rung; PROT-018/019 OK; SHIPPED 2026-06-03
- q_a3_l35_cross_layer_composition_v1_n16384 (pending) — v362 REFILL-2; L=35 N=16384 16th rung (matches N=4096 ceiling); PROT-018/019 OK; SHIPPED 2026-06-03
- q_a3_l36_cross_layer_composition_v1_n16384 (pending) — v362 REFILL-2; L=36 N=16384 17th rung (BEYOND N=4096 ceiling); PROT-018/019 OK; SHIPPED 2026-06-03
- pp50_kappa3_sigma_g_n8192_v1_n8192 (pending) — v362 REFILL-2; PP-50 sigma_g cross-N 2nd rung N=8192; PROT-018/019 OK; SHIPPED 2026-06-03
- q_a3_l20_cross_layer_composition_v1_n32768 (INFRA_FAIL) — v362 REFILL; N=32768 W=4GB OOM on display GPU; NEEDS CLOUD GPU (headless, >=8GB free VRAM); SHIPPED+FAILED 2026-06-03
- q_a3_l21_cross_layer_composition_v1_n32768 (INFRA_FAIL) — v362 REFILL; same OOM; NEEDS CLOUD GPU; SHIPPED+FAILED 2026-06-03
- q_a3_l24_cross_layer_composition_v1_n16384 (completed)
- q_b1_bisect_d293_v1_n16384 (completed) — HARD_FAIL; confirms collapse window (275,281]; d5=0.880 collapse d40-70

CPU (remote_cpu_queue) — REORDERED 2026-06-03:
- pp56_sherman_morrison_cert_drop_n65536_v5_n65536 (running) — cpu_runner_0 active
- pp49_hrc_depth_parity_discriminator_sweep_v1_n4096 (pending[1]) — Wave-5 Decisive #3
- pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384 (pending[2]) — Wave-5 Decisive #1
- pp58_bbp_discrete_fallback_v1_n16384 (pending[3]) — MOVED UP from [5] to [3]; user priority
- pp55_vsa_binding_n131072_v6_n131072 (pending[4]) — 6th rung cross-N
- pp49_hrc_protocol_artifact_nscale_v1_n8192 (pending[5])
- pp33_mfpt_glauber_n32768_v2_n32768 (pending[6])

---

## Waiting to ship — TIER 1 (next-cycle priority)

### From cycle-26+ carryover (still unshipped)

5. **Q-A3 L=37+ at N=16384** — continue N=16384 depth ladder past L=36 when results arrive (L=33..L=36 SHIPPED v362 refill-2)
6. **Q-B1 bisect d=276 or d=280** — depends on d=278 outcome (HP -> bisect (278,281] -> d=280; MID -> bisect (275,278] -> d=276); DEFERRED until d=278 result arrives
7. **Q-A3 L=22+ at N=32768** — continue N=32768 ladder after L=20/L=21 results arrive (SHIPPED v362)

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

## TESTBED-OWNED (NOT exp_dev queueable; testbed engineering required first)

### Wave 1 AUTHORIZED probes (per `notes/research_routing_v359_wave1_authorized_dispatch_2026-06-03.md`)

User authorized 2026-06-03; total $15-35 cloud + ~2-4 days engineering. **TESTBED session picks up integration checklist** (§2 of routing). exp_dev cannot queue_add these — they require substrate-LM integration scaffolding (anti-Hebbian + HRC wiring + multi-layer composition) BEFORE shipping.

1. **`phase_d_tier6_full_pipeline_4_core_char_lm_v1`** — A100 cloud, $5-10, ~2-4h wall, **3-4 days engineering** (Probe 11+)
   - 4-layer character-LM with NO gradient descent at any layer
   - Tests substrate's 4-primitive joint operation as a training+inference loop
   - HP: BPC ≤ 2× baseline + wall ≤ 0.5× baseline + 4 primitives operational
   - Founds candidate PP-59 row if HP (substrate-native LM training viability)

2. **`substrate_curriculum_learning_small_lm_v1`** — Pythia-160M cloud, $5-15, ~6-12h wall, **2-3 days engineering** (Probe 8)
   - 4 curriculum policies wired (random / difficulty-graded / loss-based active / substrate-curriculum)
   - HP: substrate reaches ≤ best baseline BPC in ≤ 50% of steps
   - Could LIFT PP-52 band if HP

3. **`tier2_substrate_preloaded_icl_pythia410m_v1`** — local GPU or cheap cloud, $5-10, ~6h wall, **2 days engineering** (Probe 2)
   - Pythia-410M; 3 conditions (standard ICL / substrate-loaded ICL / zero-shot)
   - HP: substrate-loaded within ±5pp of standard ICL AND substrate input tokens < 10% AND wall-time per "learning instance" ≥ 50× faster
   - Strengthens Phase 0.5b sub-cell H if HP

**Orchestrator's role**: queue management. When testbed dispatches and verdicts land, dispatch verdict_handler per usual. **No exp_dev queue_add for Wave 1 probes.**

**Decision gates post-Wave 1**: Probe 11+ HP → Phase E candidate ($25-50 Pythia-160M FULL 12-primitive surface; user GO required).

**Optional cascade drill** (not dispatched; awaiting separate user nod): anti-Hebbian contrastive at transformer scale Tier-1 lit-scan ($0 sonnet, ~30 min) for theoretical de-risking before Probe 11+ empirical results land.

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
