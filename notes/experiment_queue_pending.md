# Pending experiment queue — running list

**Updated:** 2026-06-03 USER-PRIORITY second 5 batch SHIPPED (5 GPU anchors queued to overnight_queue; remote verify PASS 5/5)

**Purpose:** Single source of truth for experiments waiting to be queued by orchestrator. Re-generated each cycle when there's a state change. User can read this anytime to see what's pending.

---

## Active in overnight_queue (pending -- second batch USER-PRIORITY 2026-06-03)

GPU (overnight_queue) -- v371 SECOND BATCH 2026-06-03:
- q_a3_l62_cross_layer_composition_v1_n16384 (pending) -- C: L=62 N=16384 43rd rung; SHIPPED+REMOTE_VERIFIED; timeout=21600s
- q_a3_l63_cross_layer_composition_v1_n16384 (pending) -- C: L=63 N=16384 44th rung; SHIPPED+REMOTE_VERIFIED; timeout=21600s
- q_a3_l37_cross_layer_composition_v1_n8192 (pending) -- D: L=37 N=8192 17th cross-N rung; SHIPPED+REMOTE_VERIFIED; timeout=21600s
- q_a3_l38_cross_layer_composition_v1_n8192 (pending) -- D: L=38 N=8192 18th cross-N rung; SHIPPED+REMOTE_VERIFIED; timeout=21600s
- pp50_kappa3_delta_alpha_n16384_v3_fine_sigma_g_n16384 (pending) -- B: PP-50 fine sigma_g={0.1,0.3,0.5,0.7,0.9} envelope shape; SHIPPED+REMOTE_VERIFIED; timeout=21600s

## Deferred from second batch (not shipped this cycle)

- A: pp58_bbp_dense_n16384 -- PP-58 BBP-dense N=16384 (6th anchor; deferred to next batch; priority when queue empties)
- G: pp58_isochoric_bbp_gate45_n8192 -- PP-58 isochoric BBP gate=4.5 N=8192 v2 (RESOLVE LVH #213; deferred to next batch)

---

## Currently active (in remote queues -- status=completed awaiting verdict)

GPU (overnight_queue) -- USER-PRIORITY first 5 batch 2026-06-03:
- q_a3_l60_cross_layer_composition_v1_n16384 (COMPLETED) -- USER-PRIO; L=60 N=16384 41st rung; self-test=2.2s; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s; already ran
- q_a3_l61_cross_layer_composition_v1_n16384 (COMPLETED) -- USER-PRIO; L=61 N=16384 42nd rung; self-test=2.3s; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s; already ran
- q_a3_l35_cross_layer_composition_v1_n8192 (COMPLETED) -- USER-PRIO; L=35 N=8192 15th cross-N rung; self-test=2.0s; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s; already ran
- q_a3_l36_cross_layer_composition_v1_n8192 (COMPLETED) -- USER-PRIO; L=36 N=8192 16th cross-N rung; self-test=2.2s; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s; already ran
- pp49_hrc_deeper_d_d10_d12_d14_v1_n16384 (COMPLETED) -- USER-PRIO; PP-49 d=10/12/14 isolation probe; self-test=2.0s; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s; already ran

GPU (overnight_queue) -- v370 REFILL 2026-06-03 cycle 39 (all completed):
- q_a3_l58_cross_layer_composition_v1_n16384 (COMPLETED)
- q_a3_l59_cross_layer_composition_v1_n16384 (COMPLETED)
- q_a3_l33_cross_layer_composition_v1_n8192 (COMPLETED)
- q_a3_l34_cross_layer_composition_v1_n8192 (COMPLETED)
- pp50_kappa3_delta_alpha_n16384_v2_n16384 (COMPLETED)

GPU (overnight_queue) -- v369 REFILL 2026-06-03 (completed cycle):
- pp50_kappa3_delta_alpha_n16384_v1_n16384 (FAILED -- exit 3221226505 Windows CUDA AV; re-shipped as v2 above)
- pp49_hrc_cross_n_d4_d6_d8_v1_n16384 (completed)
- q_a3_l56_cross_layer_composition_v1_n16384 (completed)
- q_a3_l57_cross_layer_composition_v1_n16384 (completed HARD_PASS)
- pp58_isochoric_bbp_protocol_v1_n8192 (completed)

GPU (overnight_queue) -- v368 REFILL 2026-06-03 (completed cycle):
- q_a3_l54_cross_layer_composition_v1_n16384 (pending) -- v368 REFILL; L=54 N=16384 35th rung; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s
- q_a3_l55_cross_layer_composition_v1_n16384 (pending) -- v368 REFILL; L=55 N=16384 36th rung; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s
- q_a3_l31_cross_layer_composition_v1_n8192 (pending) -- v368 REFILL; L=31 N=8192 11th cross-N rung; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s
- q_a3_l32_cross_layer_composition_v1_n8192 (pending) -- v368 REFILL; L=32 N=8192 12th cross-N rung; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s
- pp50_kappa3_delta_alpha_n8192_v1_n8192 (pending) -- v368 REFILL; PP-50 first N=8192 rung; kappa_3 drift-detection sensitivity; SHIPPED+REMOTE_VERIFIED 2026-06-03; timeout=21600s

Note: L=52/L=53 N=16384 and L=30 N=8192 were discovered already completed in remote queue (outside cap_map v368 window); verdicts pending processing by verdict_handler.

Previously active v367 REFILL (all completed):
- q_a3_l49..l51_cross_layer_composition_v1_n16384 (completed)
- q_b1_bisect_d276_v1_n16384 (completed)
- q_a3_l29_cross_layer_composition_v1_n8192 (completed)
Also completed outside v368 window: q_a3_l52+l53 N=16384, q_a3_l30 N=8192

Previously shipped (all completed or in progress as of v363):
- q_a3_l39..l42_cross_layer_composition_v1_n16384 (v363 batch; results pending)
- q_b1_bisect_d277_v1_n16384 (running per v363 refill)
- q_a3_l20..l38_cross_layer_composition_v1_n16384 (all completed)

Previously shipped (all completed as of v363):
- q_a3_l20..l38_cross_layer_composition_v1_n16384 (all completed) — L=20..L=38 N=16384 confirmed HARD_PASS
- q_b1_bisect_d275/278/281/287/293_v1_n16384 (all completed)
- q_a3_l20_cross_layer_composition_v1_n32768 (INFRA_FAIL) — N=32768 W=4GB OOM; NEEDS CLOUD GPU
- q_a3_l21_cross_layer_composition_v1_n32768 (INFRA_FAIL) — same OOM

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

## Waiting to ship — TIER 1 (next-cycle priority)

### From v363 refill (queue has 3 pending/running; add more when those complete)

1. **Q-A3 L=43+ at N=16384** — continue depth ladder past L=42 when results arrive
2. **Q-B1 bisect d=276** — depends on d=277 outcome (HP -> window (277,278]; MID -> bisect (275,277])
3. **PP-49 cross-N at N=16384** — PP-49 experiment family has no N=16384 rung yet (v363 B candidate)

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
