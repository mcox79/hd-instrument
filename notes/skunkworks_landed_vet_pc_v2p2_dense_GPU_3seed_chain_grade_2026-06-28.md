# Skunkworks landed-VET: pattern_completion v2.2 dense cliff grid GPU 3-seed -> CHAIN-GRADE PROMOTION (CERT +2)

**Date:** 2026-06-28 (post-handoff from orchestrator off-disk verify)
**Auditor:** Skunkworks (Opus 4.7 1M, agent-spawn)
**Verdict:** CHAIN-GRADE PHASE CHARACTERIZATION + CHAIN-GRADE SCALING LAW (CERT N: 628 -> 630, +2)

## Audit dispositions

| Atom | Disposition | Delta |
|------|-------------|-------|
| [1] seed_7  HARD_PASS_LOCALIZED_CLIFF (math; EXPERIMENT_RECORD) | per-seed evidence | 0 |
| [2] seed_13 HARD_PASS_LOCALIZED_CLIFF (math; EXPERIMENT_RECORD) | per-seed evidence | 0 |
| [3] seed_19 HARD_PASS_LOCALIZED_CLIFF (math; EXPERIMENT_RECORD) | per-seed evidence | 0 |
| [4] CROSS-SEED AGG chain_grade_phase_characterization (math; CAPABILITY_MAP) | CHAIN-GRADE | +1 |
| [5] SCALING-LAW cliff(N)=0.40+0.0065*log2(N) R^2=0.97 (math; RESEARCH_FINDING) | CHAIN-GRADE | +1 |
| [6] META env_var_contract amendment (meta; DISCIPLINE_RULE_AMENDMENT) | meta-rule | 0 |

## SCHEMA-VET (pre-reg validation)

Pre-reg path: `preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid.md`

All 5 §15 SCHEMA-VET gates pass:
- A) effective-vs-nominal-parameter audit: PASS (corruption_frac is directly applied, no composition layer)
- B) functional-requirement decomposition: PASS (single primitive: pattern completion = retrieve clean from corrupted)
- C) signal-shape compatibility: PASS (single-primitive cell; no composition)
- D) substrate-as-canonical query-first: PASS (v1 phase-diagram + v2 narrow + v2.1 narrow chain documented)
- E) discriminator-survives-scale: PASS (smoke at N=16384 with cliff-edge corruption 0.48 produced 0.985 SAT confirming cliff above 0.48; smoke gates 4-7 documented PASS per prereg lines 184-191)

Meta-rules declared: AC (arms differ SHA-256), AE (bands locked at module init), AF (arms differ per-point), AG (CRLB pre-validated), AH (number tagging), AN (empirical baseline for iterative), H (cardinality_ok), J (no silent except), L (band-floor = MB). All recorded.

## Off-data recompute (independent of verdict_msg)

`.venv/Scripts/python.exe` recompute from SCP'd remote metrics at:
- `d:/AI/hd-instrument/data/_audit_skunkworks/v2p2_dense_GPU/seed_{7,13,19}/metrics.json`

Source-of-truth paths (remote where cells ran):
- `marsh@home:C:/dev/hd-instrument/data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}_GPU/metrics.json`

### Per-seed cardinality + tier recount

| Seed | observed | expected | tier counts (independent recompute) | mismatches |
|------|----------|----------|--------------------------------------|-----------|
| 7    | 180      | 180      | SAT=69 HP=12 MB=18 FLOOR=57 HF=24 (n_disc=30) | 0/180 |
| 13   | 180      | 180      | SAT=69 HP=12 MB=18 FLOOR=60 HF=21 (n_disc=30) | 0/180 |
| 19   | 180      | 180      | SAT=69 HP=12 MB=18 FLOOR=57 HF=24 (n_disc=30) | 0/180 |

All 3 reported tier_counts confirmed bit-exact via independent re-tiering from raw `top1_substrate` + `top1_random` + pre-reg bands. Per-point `verdict_tier_per_point` matches across 540 total phase points.

### Cliff_locator cross-seed (smallest corruption where top1_sub < 0.50 per (N, T))

```
(N, T)         s7      s13     s19     identical?  SD
(2048, 1)      0.47    0.47    0.47    True        0.00000
(2048, 5)      0.47    0.47    0.47    True        0.00000
(2048, 20)     0.47    0.47    0.47    True        0.00000
(4096, 1)      0.48    0.48    0.48    True        0.00000
(4096, 5)      0.48    0.48    0.48    True        0.00000
(4096, 20)     0.48    0.48    0.48    True        0.00000
(8192, 1)      0.485   0.485   0.485   True        0.00000
(8192, 5)      0.485   0.485   0.485   True        0.00000
(8192, 20)     0.485   0.485   0.485   True        0.00000
(16384, 1)     0.49    0.49    0.49    True        0.00000
(16384, 5)     0.49    0.49    0.49    True        0.00000
(16384, 20)    0.49    0.49    0.49    True        0.00000
```

**ALL_IDENTICAL across 3 seeds × 12 (N, T) combos = 36 cliff measurements.**

### Suspect-1.000 / by-construction-saturation check (per discipline R + Q)

The SD=0.00000 across seeds at every (N, T) initially looks like Q-suspect "vacuous identical-result" pattern. Skunkworks investigated:

- Raw `top1_substrate` values at fixed (N, T, corruption) DO vary by seed: e.g., at N=2048, T=5, c=0.460:
  - seed_7  = 0.696
  - seed_13 = 0.722
  - seed_19 = 0.666
  - SD ≈ 0.03 (real seed variation)

- The cliff_locator coincidence happens because all 3 seeds first cross 0.50 at the SAME 0.005 grid step (e.g. 0.470 at N=2048). This is **honest grid-quantization**, not by-construction-saturation.

- Discriminator FIRES cleanly: top1 transitions from ~0.86 (c=0.455) to ~0.13 (c=0.480) across only 5 grid steps (0.025 corruption span). Localized.

- Conclusion: Q-suspect FLAG raised but cleared by underlying-raw-value variance check. Cross-seed SD at grid resolution is bounded by the 0.005 step size, NOT by mechanism degeneracy. Result is honestly chain-grade.

### CRLB consistency

| N | CRLB_pred | empirical (3-seed × 3-T mean) | delta | delta_pct |
|---|-----------|-------------------------------|-------|-----------|
| 2048  | 0.4610 | 0.47000 | +0.0090 | +1.94% (ABOVE CRLB) |
| 4096  | 0.4725 | 0.48000 | +0.0075 | +1.60% (ABOVE CRLB) |
| 8192  | 0.4805 | 0.48500 | +0.0045 | +0.93% (ABOVE CRLB) |
| 16384 | 0.4862 | 0.49000 | +0.0038 | +0.78% (ABOVE CRLB) |

**Correction of orchestrator handoff framing:** orchestrator said "empirical cliffs ~0.005-0.01 BELOW CRLB consistent with attractor geometry". Skunkworks off-data recompute shows the direction is INVERTED: empirical cliffs are ~0.4-2.0% ABOVE CRLB (substrate tolerates higher corruption than pure CRLB 1-step noise-floor predicts).

Physical interpretation unchanged (consistent with attractor geometry; Hopfield basin gives positive headroom over pure noise floor), but the framing direction must be corrected before downstream cites.

CRLB-form fit: cliff(N) = 0.5 - C × sqrt(log(M=500)/N) → implied C across N: 0.545, 0.513, 0.545, 0.513 → mean=0.529 (SD=0.018). Pure CRLB-1step C=sqrt(2)≈1.414. Substrate is 0.374 of pure-CRLB-noise-floor scaling = ~37% (CRLB-1step is overly conservative for this attractor geometry).

### Functional form fit (cliff vs N)

```
cliff(N) = 0.40000 + 0.00650 × log2(N)
R^2 = 0.965714
RSS = 7.5e-06; TSS = 2.19e-04

N=2048  : actual=0.47000  predicted=0.47150  resid=-0.00150
N=4096  : actual=0.48000  predicted=0.47800  resid=+0.00200
N=8192  : actual=0.48500  predicted=0.48450  resid=+0.00050
N=16384 : actual=0.49000  predicted=0.49100  resid=-0.00100
```

Max |resid| = 0.002 (sub-grid precision; well within 0.005 grid resolution). **Chain-grade scaling-law eligible.**

Validity envelope: N ∈ [2048, 16384] (fitted); extrapolation valid log2-linear to N=32768; CRLB-form preferred beyond N=16384.

### GPU verification

- `backend = torch.cuda` (all 3 seeds)
- `device = cuda` (all 3 seeds)
- `gpu_name = NVIDIA GeForce RTX 4060 Ti` (all 3 seeds)
- `gpu_util_estimate = 0.95` (all 3 seeds)
- `peak_mem_mb` range: 40.4 - 285.6 MB (matches pre-reg budget at N=16384 M=500)
- `elapsed_s`: 23.21, 23.83, 24.34 (cell-reported); sum of per-point elapsed: 22.91, 23.53, 23.97 (consistent; small Python init overhead)
- **NOT by-construction-CPU-saturated:** matmul-bound `Q_t @ X^T` at N=16384 M=500 dominates; GPU is doing the work.

### Substrate-only-decode gate

- `n_llm_calls = 0` across all 3 seeds.
- `substrate_only_decode_gate = PASS`.

### Arms differ (SHA-256)

| Seed | substrate_hash (first 16) | random_hash (first 16) | differ |
|------|---------------------------|------------------------|--------|
| 7    | c0af8d30471c51ba | e300a9e0e85c8796 | True |
| 13   | f18c5bab17f90d2a | 401e0c4bf83767fb | True |
| 19   | 36571675aba21902 | 0cf07dc351243c3e | True |

### Random arm sanity

| Seed | random_arm mean top1 | expected (1/M=1/500) |
|------|----------------------|----------------------|
| 7    | 0.0017 | 0.002 |
| 13   | 0.0018 | 0.002 |
| 19   | 0.0017 | 0.002 |

Random floor calibrated. Discriminator (sub - rnd) of HP+MB atoms (n_disc=30 per seed) is meaningful.

## Composes-with (sibling phase characterizations in 2026-06-28 dispatch cycle)

- **WM K-cliff v3 chain-grade** (commit 7274bafb): K_cliff(B) = 256 × B
- **sequence_binding K-cliff chain-grade** (commit 68714d0e): seq-binding cliff per N
- **Pattern_completion v2.2 dense GPU** (this audit batch): cliff(N) = 0.40 + 0.0065 × log2(N)

This is the 3rd-of-3 chain-grade phase-characterization promotion in the 2026-06-28 cell-author+orchestrator dispatch cycle.

## Supersedes

- `math::T3/EXP_pattern_completion_corruption_cliff_v2p1_narrow_regime_CROSS_SEED_AGG_3_of_3_MM_2026-06-28` (v2.1 narrow MM atom; promoted to chain-grade via dense grid v2.2)

The 3 DISPATCH_INFRA_FAILURE atoms (v2.2 prior run) STAND as evidence for the META rule lesson (env_var_contract); they are NOT superseded by this audit because they record a separate observed failure mode (infrastructure dispatch refusal), not a substrate hypothesis test outcome.

## Stage 1 phase-coverage update

Pattern_completion: MID/MID → HIGH per characteristics-table BACKUP UPDATE #25 (chain-grade phase-characterization landed; scaling law landed; localized cliff observed at 0.005-grid resolution; N-scaling matches CRLB direction).

## META RULE AMENDMENT (atom 6, meta corpus)

`META_RULE_AMENDMENT_runner_v2_env_var_contract_HDLAB_QUEUE_must_be_set_in_child_env_for_gpu_mandate_cells_to_execute_unblocked_pc_v2p2_dense_promotion_path`

Skunkworks SCHEMA-VET §15 should add a 6th gate:

> **F) `env_var_contract_for_gpu_mandate`**: pre-reg with GPU-mandate cell MUST declare `PRESERVE_ENV_VARS=HDLAB_QUEUE` (or equivalent) in cell header, AND runner_v2 must be at commit >= 9f9c74fe.

Evidence:
- runner_v2_prod patch: commit `9f9c74fe`
- sibling cell adoption: task_vector K-cliff cells commit `6b8426a2`
- this audit's chain-grade promotion was unblocked by the patch (25s/seed GPU vs 30min/seed CPU = ~72x speedup)

## Skunkworks audit red flags (none load-bearing for verdict)

1. **Orchestrator handoff framing of CRLB delta direction is inverted** (BELOW should be ABOVE). Cross-seed delta is +0.4 to +2.0% above CRLB. Atomized correctly in chain-grade atom metadata; downstream cites should use atom field `crlb_empirical_direction = "ABOVE_CRLB"`.
2. **Cross-seed cliff_locator SD = 0** at every (N, T). FLAG investigated: underlying raw values vary by 0.03-0.05 across seeds at fixed (N, T, c); grid-quantization at 0.005 step compresses to identical locator. Honestly identical, not vacuous.

Neither red flag changes the verdict; both are recorded in atom metadata for downstream auditors.

## Off-data recompute script

`d:/AI/hd-instrument/data/session_local/skunkworks/_v2p2_dense_GPU_audit.py`

Run with `.venv/Scripts/python.exe`. All numbers in this note traceable to that script's stdout against the SCP'd metrics files.

## Atomization tool

`d:/AI/hd-instrument/tools/atomize_skunkworks_pc_v2p2_dense_GPU_3seed_chain_grade_2026-06-28.py`

DRY-run validates all 6 atoms construct cleanly with proper AtomKind enums + provenance_quality fields. Apply with `--apply` flag.
