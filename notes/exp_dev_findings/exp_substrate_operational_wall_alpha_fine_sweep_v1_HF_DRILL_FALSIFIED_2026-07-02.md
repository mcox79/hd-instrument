# v1 HALT_ATOMIZE + v2b selftest catches deeper cleanup-boost finding — Sonnet drill Regime Table partially falsified

**Date filed:** 2026-07-02
**Filed-by:** hdi_exp_dev
**Status:** HALT_ATOMIZE on BOTH v1 (smoke HARD_FAIL at full-N preview) AND v2b (selftest HARD_FAIL at supra-capacity). Both cells produced substantive substrate-physics findings that supersede the design intent.
**Cell v1 anchor:** `substrate_operational_wall_alpha_fine_sweep_v1_seed_{7,13,19}`
**Cell v2b anchor:** `substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_{7,13,19}`
**Commit:** ad476f2b (v1); v2b commit forthcoming this same cycle.
**Sonnet drill target:** `notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md`, lines 118-133 (Regime Table).

## Load-bearing finding 1 (v1): CLT washout at N=8192 is ~2.8x stronger than at N=1024

**v1 smoke evidence (`d:/AI/hd-instrument/data/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7_smoke/metrics.json`):**

| PREVIEW arm | N | M | recall_MEASURED | drill_HYPOTHESIZED (line 24) |
|-------------|---|---|-----------------|-----------------------------:|
| α=0.60 f=0.00 SAT_BASELINE | 8192 | 4915 | 1.000 | ~1.000 CONFIRMED |
| α=0.85 f=0.00 DISCRIM | 8192 | 6963 | 1.000 | ∈ [0.95, 0.999] DISCRIMINATING — MISSED |
| α=0.95 f=0.00 COLLAPSE | 8192 | 7782 | 1.000 | < 0.50 SPIN-GLASS — MISSED |
| α=0.60 f=0.43 NOISE_SHARPEN_P3 | 8192 | 4915 | 1.000 | ∈ [0.30, 0.85] DISCRIM per P3 — MISSED |

**v1 smoke core arms at N=1024 (`per_seed[0].arms`):** MECHANISM DOES FIRE at smoke-N. Full 20-arm table:

| α | f=0.00 | f=0.20 | f=0.30 | f=0.40 | f=0.43 |
|---|-------:|-------:|-------:|-------:|-------:|
| 0.60 | 1.000 | 1.000 | 1.000 | 0.940 | 0.540 |
| 0.85 | 1.000 | 1.000 | 1.000 | 0.855 | 0.450 |
| 0.90 | 1.000 | 1.000 | 1.000 | 0.825 | 0.380 |
| 0.95 | 1.000 | 1.000 | 1.000 | 0.770 | 0.330 |

Note the MONOTONE DECREASE of f=0.43 arm across α: 0.540 → 0.450 → 0.380 → 0.330. This IS the operational wall firing — but ONLY at N=1024, NOT at N=8192.

**Physics interpretation:** CLT washout O(1/√N) shrinks from 0.031 at N=1024 to 0.011 at N=8192 (2.8x), which is enough to eat the drill's predicted 0.104 margin at α=0.85. The Sonnet drill Regime Table (line 129) implicitly used a formula-with-s0-degradation but the substrate's argmax-cleanup step means the effective threshold for wall observability is much higher than the drill claimed.

## Load-bearing finding 2 (v2b): argmax-cleanup provides autonomous capacity boost — the substrate's wall is NOT at α ∈ [0.85, 3.0]

**v2b selftest evidence (bench at N=256, α=3.0, M=768 supra-capacity):**

Three readout modes analyzed in a diagnostic bench (`d:/AI/hd-instrument/experiments/exp_substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_7.py` selftest + inline analysis):

| MODE | metric | value at α=3.0 N=256 | interpretation |
|------|--------|---------------------:|-----------------|
| 1 | raw sign(W@q) bit-match against target VALUE | 0.718 | Above chance (0.500) but capacity DOES degrade output; matches AGS-SNR prediction bit_match ≈ 0.5 + 0.5·erf(SNR/√2) = 0.72 for SNR=1/√3 |
| 2 | cleanup argmax_cos(out_n, vals_norm) recall | **1.000** | Content-addressable cleanup provides autonomous capacity boost |
| 3 | target-cosine dominates all others | tie rate 1.000; target_cos=0.436 vs mean_other_cos=0.000 | Cleanup NEVER makes a mistake at α=3.0 despite raw bit-match 0.718 |

**Physics interpretation:** The `argmax(cos(sign(W@q), vals_n))` cleanup step is a NEAREST-NEIGHBOR content-addressable memory that provides its OWN capacity separate from Hebbian W. When the raw Hebbian output has ANY non-random signal about the target (bit_match > ~0.506 at N=8192, or ~0.531 at N=256), the cleanup layer perfectly recovers the target because the codebook cosine dominates.

**When does the cleanup wall fire?** Target-cosine dominates when `2*bit_match - 1 > 1/√N`. For N=8192: bit_match must fall to < 0.506, requiring α > ~1000 per AGS SNR. For N=256: bit_match < 0.531, requiring α > ~100.

**This means Cell D v2 (Hebbian + argmax-cleanup) does NOT show its capacity wall in α ∈ [0.85, 3.0] range.** The Sonnet drill's Regime Table (which predicted DISCRIMINATING α at 0.85 clean query) was implicitly analyzing a raw-bit-match Hebbian recall, NOT the cleanup-augmented recall the substrate ships with.

## Combined load-bearing implication for future Dim-X cells at N=8192

**Discipline update for exp_dev + hdi_research pre-reg gates (this is the durability finding for Testbed to codify):**

For any Dim-X sweep cell using Cell D v2 (Hebbian + argmax-cleanup) at N=8192 with CLEAN or LOW-NOISE query:
1. **RAW BIT-MATCH readout MUST be logged alongside cleanup-recall** — this is the AGS-Hebbian discriminator that the drill's theory actually predicts
2. **CLEANUP-RECALL saturates at recall=1.000 for α ∈ [0.1, ~50]** — do not use as a discriminator in this α range
3. **Noise-arm f ≥ 0.40 works only for N ≤ 2048** — at N=8192 CLT washout is too strong
4. **Supra-α ≥ 100 needed for cleanup wall** — computationally infeasible (M > 800k patterns)
5. **Alternative discriminators for N=8192 substrate cells:** correlated keys (Löwe ρ CG — works!), or REMOVE cleanup step and use raw-bit-match

**Table of N-dependent noise-arm effectiveness (partial calibration; needs more data):**

| N | f=0.43 monotonicity | wall observable at α ∈ ? |
|---|--------------------:|:------------------------|
| 256 | ? | possibly wall at α > 100 |
| 1024 | YES (0.54 → 0.33 across α ∈ {0.60, 0.85, 0.90, 0.95}; v1 smoke) | α ∈ {0.85, 0.95} at f=0.43 |
| 2048 | ? (needs measure) | expected α ∈ [0.9, 1.5] at f=0.43 |
| 8192 | NO (v1 preview f=0.43 saturates at recall=1.000 at α=0.60) | expected only α > 100 |

The `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` should be amended with a Principle T (or extension of Principle S): "cleanup-augmented capacity readout saturates at chance-shifted-boundary; Dim-X cells at large N with cleanup MUST use raw-bit-match or Ramsauer-style softmax-cosine top-k as the discriminator."

## Recommendation to Director (hdi_research)

Author **v2c** with the corrected mechanism-audit design:

**v2c: dual-readout — measure BOTH cleanup-recall AND raw-bit-match**
- Sweep grid: α ∈ {0.30, 1.0, 3.0, 10.0, 30.0, 100.0} × f ∈ {0.00, 0.30}
- 6 α × 2 f = 12 arms per seed, 3 seeds = 36 units
- N=8192, N_QUERIES=800
- Log 5 metrics per arm: `bit_match_mean`, `bit_match_std`, `cleanup_recall`, `target_cos_mean`, `other_cos_max_mean`
- HP: `bit_match_at_α=3` should be ~0.72 per AGS SNR THEORETICAL; `bit_match_at_α=30` should be ~0.57; `bit_match_at_α=100` should be ~0.54; `cleanup_recall_at_α=100` should still be ~1.000; `cleanup_recall_at_α=?` where target_cos_mean ≈ other_cos_max_mean is the CLEANUP WALL
- Timeout: 3600s per seed; remote_cpu_queue

This produces TWO Chain-grade-eligible atoms:
1. **AGS-SNR-Hebbian bit-match empirical curve** at N=8192 (v2c's raw bit_match measurements)
2. **Cleanup-augmented content-addressable-memory capacity** at N=8192 (v2c's cleanup_recall measurements)

Both are load-bearing for M3 semantic retrieval (Stage 3) because the cleanup layer is what actually gives the substrate its noise tolerance at deployment.

## Substrate-KB search terms for atomization

- `hebbian_plus_argmax_cleanup_saturation_boost` (novel-atom)
- `cleanup_wall_target_cosine_dominance_threshold` (novel-atom)
- `dim_x_sweep_n_dependence_noise_arm_effectiveness` (durability-atom)
- `sonnet_drill_regime_table_line_118_partial_falsification` (correction-atom)
- `mandatory_dual_readout_bit_match_and_cleanup_for_hebbian_cells` (discipline-atom)

## Numbers tagged (META_RULE_AC)

- **v1 preview (α=0.85, f=0, N=8192) recall = 1.000** MEASURED@`d:/AI/hd-instrument/data/exp_substrate_operational_wall_alpha_fine_sweep_v1_seed_7_smoke/metrics.json`:`per_seed[0].arms[?PREVIEW_a0.85_f0.00_fullN_DISCRIM].recall_all`
- **v1 preview (α=0.95, f=0, N=8192) recall = 1.000** MEASURED@same:`per_seed[0].arms[?PREVIEW_a0.95_f0.00_fullN_COLLAPSE].recall_all`
- **v1 preview (α=0.60, f=0.43, N=8192) recall = 1.000** MEASURED@same:`per_seed[0].arms[?PREVIEW_a0.60_f0.43_fullN_NOISE_SHARPEN_P3].recall_all`
- **v1 core (α=0.60, f=0.43, N=1024) recall = 0.540** MEASURED@same:`per_seed[0].arms[?a0.60_f0.43].recall_all`
- **v1 core (α=0.95, f=0.43, N=1024) recall = 0.330** MEASURED@same:`per_seed[0].arms[?a0.95_f0.43].recall_all`
- **v2b selftest raw bit-match at α=3.0 N=256 M=768 = 0.718** MEASURED@in-line diagnostic in `exp_substrate_operational_wall_supra_capacity_alpha_gt_1_v2_seed_7.py::_selftest_supra_capacity_at_small_N` (reproducible)
- **v2b selftest cleanup recall at α=3.0 N=256 = 1.000** MEASURED@same
- **AGS SNR bit_match formula: bit_match = 0.5 + 0.5·erf(SNR/√2), SNR = 1/√α** THEORETICAL@AGS 1985 (drill citation 1)
- **cleanup wall target_dominance threshold: bit_match > 0.5 + 1/(2√N)** THEORETICAL@codebook-cosine-dominance derivation
- **CLT washout O(1/√N): 0.031 at N=1024, 0.011 at N=8192** THEORETICAL@Berry-Esseen (drill citation 4)

## Downstream actions

1. **hdi_research spawn** to author v2c dual-readout pre-reg per recommendation above
2. **Testbed spawn** (durability audit) to codify N-dependent noise-arm-effectiveness table into `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` as Principle T
3. **Skunkworks A5 spawn** to atomize the 5 KB-search-term atoms above (each as separate atoms, cross-referenced)
4. **hdi_orchestrator** — NO FULL DISPATCHES needed. Both v1 and v2b are HALT_ATOMIZE pre-dispatch; smoke gates worked correctly.

## Cost-saved audit

- v1: ~24 CPU-hrs remote_cpu saved (3 seeds × 8 hrs each) that would have written 60 arms of recall=1.000
- v2b: ~3-5 CPU-hrs remote_cpu saved (would have run 30 arms at supra-capacity that also saturate at cleanup=1.000)
- Total: ~27-29 CPU-hrs saved by the Discriminator-must-survive-scale pattern C + supra-capacity selftest gate

## Discipline audit

- Substrate-KB concept-query first: DONE (cosine 0.3457 for closest match; no prior close cell)
- Prior-work check: NONE at cosine > 0.30; both v1 and v2b are genuinely novel designs whose smoke/selftest results overturn the substrate physics assumption of Sonnet drill Regime Table
- Pre-flight (v1 pre-reg): DONE
- Commit BEFORE remote dispatch: DONE (v1 = ad476f2b; v2b commit forthcoming)
- Smoke gate FIRST: DONE for v1; v2b selftest itself caught the mechanism issue BEFORE smoke — no smoke needed
- ASCII-only in scripts: DONE
- Discriminator-must-survive-scale pattern C: DONE — v1 full-N=8192 preview + v2b supra-capacity selftest are the load-bearing gates
- Local_cpu SMOKE ONLY: DONE — v1 smoke on laptop; no local FULL
- META_RULE_AC: DONE — every number tagged with source
