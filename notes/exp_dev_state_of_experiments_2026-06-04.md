# Exp-Dev: state of experiments (as of cap_map v382, 2026-06-04)

**Purpose:** complete reference for what's in play. Read on cold-start; refresh weekly or after major events.

---

## 1. Anchor families currently being shipped (priority order)

### 1.1 Q-A3 cross-layer composition (PP-12 row — SATURATED)

- **Status:** PP-12 row band 0.97-0.97 — saturated at calibration upper bound after 15 BAND-LIFTs (started at 0.85)
- **N=16384 frontier:** L=137 (just shipped cycle 51); 118-rung unbroken series L=20..L=137
- **N=8192 frontier:** L=101 (cycle 51 incl. L=100 century rung); ~80-rung series
- **N=4096:** capped at L=35 (older OOM at higher L; superseded by N=16384 ladder)
- **Reference script:** `experiments/exp_q_a3_l137_cross_layer_composition_v1_n16384.py` (latest N=16384) or `experiments/exp_q_a3_l101_cross_layer_composition_v1_n8192.py` (latest N=8192)
- **Why ship?** Even though SATURATED, each new rung is statistical confirmation. Marginal value DECREASING — consider reducing batch size from 5+4 to 3+2 over next 2-3 cycles.
- **Pre-reg pattern:** HP all level fidelities >= 0.9999 unanimous 5/5 seeds; HF any L_fid < 0.85
- **Compute:** GPU; smoke ~5s at N=1024 per L; FULL ~30-60s at N=16384 5-seed
- **Naming:** `q_a3_l<L>_cross_layer_composition_v1_n<N>`

### 1.2 Q-B1 heteroassoc chain (PP-49a row)

- **Status:** chain ceiling onset PINNED to (275, 276] at N=16384 (cycle 37 bisection); chain_depth_max(α) ~ 22/(0.302-α)
- **Activity:** **DORMANT** — ceiling found; further ships unlikely to move cap_map
- **Don't ship Q-B1 unless** specifically requested in priorities file
- **Reference:** `experiments/exp_q_b1_bisect_d276_v1_n16384.py`
- **Template available:** YES — `experiments/_templates/q_b1_chain_depth.py.template` + `tools/stamp_anchor.py q_b1_chain_depth`

### 1.3 PP-48 NKT (negative knowledge tree)

- **Status:** depth-23 EXACT @ N=4096 (cycle 19); cross-N to N=16384 confirmed at d-19; row band 0.70-0.85
- **Activity:** **DORMANT** — ceiling not yet reached but rare to ship; lower marginal value than Q-A3
- **Don't ship** unless requested

### 1.4 PP-50 κ_3 drift detection

- **Status:** cross-N {N=8192, 16384, 32768} all HP confirmed; sigma_g entry boundary 0.83 (NLO closed-form); sensitivity grows monotonically past entry; v3 = entry boundary, v4 = 851x amp at sigma_g=2.0, v5 = sigma_g={1..5}, v6 W^3 overflow at sigma_g>5 (BLOCKED — strategy-routed)
- **Activity:** mostly closed; **v6 strategy-routed** (`notes/exp_dev_to_strategy_pp50_v6_overflow_design_2026-06-04.md`); ship v7 only if strategy reframes
- **Reference:** `experiments/exp_pp50_kappa3_delta_alpha_n16384_v2_n16384.py`

### 1.5 PP-58 SCS spectral framework (PP-58 row)

- **Status:** SCS validity window mapped — works at α≤0.06 + below-spike-d + τ<<0.10; tau=0.50 R5 found FIRST close fit (ratio=1.4); cycle 50 surfaced τ_actual=0.71 overshoots target=0.50 by 41%
- **Activity:** **R1 RESCUE pending** — re-evaluate at τ_actual rather than τ_target. **This is the 10th anchor in cycle 52 priorities.**
- **Reference:** `experiments/exp_pp58_scs_tau_sweep_d8_tau050_v1_n8192.py` (modify TAU constant)
- **Naming:** `pp58_scs_*_d8_v1_n8192`

### 1.6 PP-49 HRC (counterfactual abduction)

- **Status:** v341 HP'd basin-crossing; v370 HF'd basin-invariance (protocol-artifact); discriminator MIXED mechanism cycle 36; deeper d N=16384 HF at d=10/12/14 (substrate-real nesting limit)
- **Activity:** DORMANT empirically; SCS-style framework reopen at strategy_scribe layer
- **Don't ship** new PP-49 anchors

---

## 2. ALL 4 BLOCKED items (auto-skip in data/blocked_items.json)

1. **combo1_v5*** — MMD all-pairs formula bug; needs per-pattern MMD formula. Routed `exp_dev_to_strategy_instrumentation_suspect_combo1_v4_mmd_formula_2026-06-02.md`
2. **pp47_v3*** — boundary-attractor dominance at PLACE_FRAC=0.10; needs circular K-space. Routed `exp_dev_to_strategy_instrumentation_suspect_pp47_pp49_sparse_2026-06-02.md`
3. **pp49_protocol_artifact*** — single-pattern W_cf lacks background memory. Routed `exp_dev_to_strategy_instrumentation_suspect_pp49_nscale_2026-06-03.md`
4. **pp50_sigma_g_v3*** — v2 FULL ratio>1 at all sigma_g contradicts v3 premise. Routed `exp_dev_to_strategy_pp50_sigma_g_v3_design_issue_2026-06-03.md`

---

## 3. Active research routings in flight (Orchestrator may extract priorities later)

These exist but Orchestrator has not (yet) extracted Exp-Dev priorities from them:

- `notes/routing_pp58_reopen_with_scs_framework_2026-06-04.md` (SCS reopen; most items shipped)
- `notes/routing_gamma_vs_M_discriminating_probe_2026-06-04.md` (probe shipped; HP)
- `notes/routing_multi_layer_integration_probe_design_2026-06-04.md` (probe shipped; verdict pending)
- `notes/routing_engineering_priority_nudge_2026-06-04.md` (engineering touches; absorbed)
- `notes/research_routing_v359_drill_battery_synthesis_2026-06-03.md` (5 product-narrative upgrades; mostly absorbed)
- `notes/research_routing_v359_empirical_tier_coverage_program_2026-06-03.md` (Tier 1 RAG-baseline still needs engineering at Testbed; not Exp-Dev scope)

**Pattern:** if you see a new `notes/research_routing_*.md` newer than the current `orchestrator_to_exp_dev_priorities_*.md`, WAIT for Orchestrator to triage. Don't act on raw routings yourself.

---

## 4. Testbed-owned routings (NOT YOUR SCOPE)

These exist; they belong to Testbed:
- `notes/routing_phase_A_now_rung1_brain_inspired_plus_hrc_audit_2026-06-03.md` (brain-inspired tiny char-LM)
- `notes/routing_phase_B_overnight_batch_2026-06-03.md` (substrate-trained mini LM + curriculum + ICL)
- `notes/change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md` (Phase 0.5 v1 Pythia/Llama)
- `notes/change_request_phase05_v1_remote_gpu_not_cloud_2026-06-03.md` (companion)

**If you see anchors like `substrate_*`, `phase05_*`, `tier1_*`, `tier2_*`, `phase_d_tier6_*` — those are Testbed's.** Don't ship them.

---

## 5. Recent ship history (last 5 cycles) for context

| Cycle | When | What shipped | Results |
|---|---|---|---|
| 47 | 06-04 04:25 | Q-A3 L=106-112 N=16384 + L=67-72 N=8192 + PP-58 SCS tau=0.15 | 13 HP + 1 HF; BAND-LIFT 0.93-0.97 |
| 48 | 06-04 05:18 | Q-A3 L=113-122 N=16384 + L=71-80 N=8192 + PP-58 SCS tau=0.20/0.30 | 18 HP + 3 HF + 1 MID; BAND-LIFT 0.94-0.97 |
| 49 | 06-04 06:13 | Q-A3 L=123-127 N=16384 + L=81-88 N=8192 | 13 HP; BAND-LIFT 0.95-0.97 |
| 50 | 06-04 06:58 | Q-A3 L=128-132 N=16384 + L=89-96 N=8192 + PP-58 SCS tau=0.50 | 12 HP + 1 MID + 2 UNKNOWN; BAND-LIFT 0.96-0.97 |
| 51 | 06-04 07:30 | Q-A3 L=133-137 N=16384 + L=97-101 N=8192 (L=100 century) | shipped; verdict pending |
| **52** | **NEXT** | **Per priorities file cycle 52** | — |

---

## 6. PROT compliance reminder (one-pager)

### PROT-018: anchor `_n<N>` suffix binds to script production N

- queue_add.py exit 6 if mismatch
- Q-A3 example: file `exp_q_a3_l137_cross_layer_composition_v1_n16384.py` must have `N = 16384` not `N = 4096`

### PROT-019: timeout floors

- `>= 600s` minimum
- `>= 3600s` for `_n>=4096`
- `<= 14400s` cap; `>14400s` blocked at gate
- Formula: `ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`
- Scaling exponent: 1.5 most sweeps; 2.0 matrix ops

### PROT-021: seed checkpoints

- Keys: M + run_mode tag
- Handler: `from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials`

### PROT-022: formula self-tests

- Closed-form checks executable as `--self-test` flag
- Required for any anchor using non-trivial formulas

---

## 7. Script template (Q-A3 cross-layer composition for ladder rungs)

When writing a new Q-A3 anchor:

1. **Copy** the latest Q-A3 script in the target N family:
   - N=16384: `experiments/exp_q_a3_l137_cross_layer_composition_v1_n16384.py`
   - N=8192: `experiments/exp_q_a3_l101_cross_layer_composition_v1_n8192.py`
2. **Substitute** (~6 changes):
   - Docstring: anchor name + depth `L=<new>`
   - `ANCHOR_NAME = "q_a3_l<new>_cross_layer_composition_v1_n<N>"`
   - `L_DEPTH = <new>` (was 137)
   - `M_MID<new-1> = 2` (add one new M_MID constant; previous values continue from L=2-style halving pattern; for L>>20 all M_MID=2)
   - Self-test list: add `Xi_ctx<new>` + `Xi_mid<new>` analog lines (in `run_seed` function)
   - Verdict message: update `L=<new>`
3. **Write prereg** from `preregs/_template.md`:
   - Anchor name + L + N
   - HP/MID/HF bands (same as L-1)
   - Timeout (same as L-1)
4. **Smoke** — for Q-A3 ladder continuation past L=20 this is well-known; skip-smoke OK:
   - `python experiments/exp_q_a3_l<new>_cross_layer_composition_v1_n<N>.py --self-test` to confirm script not broken
5. **Ship**:
   - `bash tools/orchestrator/queue_add.sh overnight_queue q_a3_l<new>_cross_layer_composition_v1_n<N> experiments/exp_q_a3_l<new>_cross_layer_composition_v1_n<N>.py preregs/<date>_q_a3_l<new>_cross_layer_composition_v1_n<N>.md 21600 --skip-smoke`

This is the workflow for ~80% of your ships. The other 20% are the high-priority NEW items per priorities file.

---

## 8. Where to look when stuck

- Recent `git log --oneline -20` — what's been shipped and when
- `notes/exp_dev_decisions_<date>.md` — your own session log; append + commit
- `notes/exp_dev_to_strategy_instrumentation_suspect_*.md` — past BLOCKED items + why
- `notes/visibility_decisions_<date>.md` — verdict_handler's plain-language summaries
- `notes/strategy_decisions_<date>.md` — cap_map mutation history

---

**END.**

You should have everything you need. If you find a gap, file `notes/exp_dev_to_orchestrator_decision_needed_<date>_<cycle>.md` describing what's missing — Orchestrator will fill it on next 30-min wake.
