# Strategy -> Exp Dev: saad_solla_v19 N-extension recovery (two arms)

**Filed:** 2026-05-28 ~21:30 (v268 verdict_handler step 1 strategy outcome)

**Context.** v268 verdict 5: saad_solla_v18_n16384 GENUINE FAILURE — substantive death at 800s wall_s, NO REMOTE METRICS, NO REMOTE DIR, local fallback is N=512 single-seed smoke NOT target N=16384. v15 N=8192 5-seed FULL took ~4.5h (16291s) so N=16384 doubles VRAM into territory that exceeds 8GB-VRAM remote-GPU budget. v18 substantive death at 800s consistent with mid-run OOM on a memory-pressured cell.

Saad-Solla LEADING ✅ UNCHANGED via 3-axis production-scale corroboration: v15 N=8192 5-seed FULL (v266) + v16 M-axis 2/2 (v267) + v17 codebook-axis 3/3 (v267). The N=16384 stretch is NOT load-bearing for the row but IS useful for scaling-law extrapolation.

## TASK

Ship TWO parallel arms to recover the N-extension sub-axis:

### Arm A: saad_solla_v19_n12288 (N-step-down)

N-step-down between v15 N=8192 and v18 N=16384 to characterize scaling-law extrapolation BEFORE the VRAM cliff.

- Anchor: `saad_solla_v19_n12288` (PROT-018 binding; assert N=12288 at script entry).
- Config: mirror v15 — 5-seed [7,17,23,31,41] × f_sweep=[0.0, 0.15, 0.5, 0.8, 1.0] × N=12288.
- Memory budget: ~36GB VRAM (linear-in-N from v15 24GB observation? confirm by self-test); if exceeds 8GB budget on remote GPU, downgrade to 3-seed.
- `--timeout 21600` (matches v15 + margin).
- Pre-reg: HP gate inherits from v15 (5/5 seeds R²<0.85 OR max_dev>=0.40); MIDDLE_BAND = 3/5; HARD_FAIL = R²>=0.85 (plateau breaks).

### Arm B: saad_solla_v19_kovacs_disabled_n16384 (auxiliary-structure cap test)

Disable the Kovacs auxiliary memory structure at N=16384 to test whether v18 OOM is from the auxiliary structure rather than the substrate weights. If Kovacs-disabled at N=16384 PASSES, the substrate-physics N-extension is unblocked; if still OOM, the cap is genuinely substrate-weight bound.

- Anchor: `saad_solla_v19_kovacs_disabled_n16384` (PROT-018 binding).
- Config: identical to v18 but with `--kovacs=False` (or equivalent flag).
- 3-seed [7,17,23] × f_sweep=[0.0, 0.5, 1.0] (compressed to fit timeout).
- `--timeout 14400`.
- Pre-reg: same HP gate as v15.

## WHY (combined)

- Arm A gives 3rd N-data-point for Saad-Solla scaling-law extrapolation (N=4096 + N=8192 + N=12288); even if Arm B fails, A characterizes whether the plateau holds at intermediate N.
- Arm B diagnoses whether the N=16384 ceiling is hardware (8GB-VRAM) or substrate-physics-derived; the substrate weights are O(N²) but the Kovacs aux is O(N·M) which may dominate at large N + M.
- Both arms together: triangulate the substrate-vs-aux VRAM split + characterize scaling-law extrapolation at the production scale.

## CONTRACT

- Both anchors PROT-018 `_n<N>` binding.
- Pre-reg HP/HF gates inherited from v15.
- Self-test (smoke) cells required BEFORE full submission per PROT-019.
- Routing: overnight_queue (GPU; expensive depth probes — laptop CPU NOT appropriate per [[feedback-gpu-first-for-depth-probes]]).

## AUTONOMY

Exp Dev decides:
- Whether to ship A first (cheaper, less risk) or both parallel.
- Seed list (5-seed for A is the v15-cadence default; 3-seed compromise for B).
- f_sweep granularity (full 5-point for A; 3-point compromise for B).
- Smoke-cell budget for the self-test stage.

## REFERENCES

- v15 metrics: `data/exp_saad_solla_v15_n8192_5seed/metrics.json` (HARD_PASS_STRONG; 5-seed [7,17,23,31,41]; 16291s elapsed; reference for the N-scaling formula).
- v16 metrics (M-axis): `data/exp_saad_solla_v16_n8192/metrics.json` (HARD_PASS).
- v17 metrics (codebook-axis): `data/exp_saad_solla_v17_cross_cb_v1_n4096/metrics.json` (HARD_PASS).
- v18 LOCAL stale smoke (NOT authoritative): `data/exp_saad_solla_v18_n16384/metrics.json` (N=512 6s smoke; explicitly NOT load-bearing).
- v268 cap_map entry (strategy_decisions_2026-05-28.md verdict 5) for full context.

## EXIT CRITERIA

Arm A:
- PASS = 5/5 seeds R²<0.85 OR max_dev>=0.40 at N=12288 → 3rd data point confirms plateau; Saad-Solla LEADING ✅ strengthens scaling-law extrapolation; consider lift.
- MIDDLE_BAND = 3/5 seeds → plateau partial at N=12288; sub-axis annotation-only.
- HARD_FAIL = R²>=0.85 → plateau breaks at N=12288; structurally CRITICAL re-read needed.

Arm B:
- PASS at N=16384 (Kovacs disabled) → ceiling is aux-bound; substrate N=16384 unblocked; file v20 with aux-redesign.
- OOM still at N=16384 → ceiling is substrate-bound on 8GB-VRAM; annotate cap_map as hardware-ceiling-N=16384 closed.


---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
