# Pre-registration: substrate_NESS_envelope_alpha_high_extension_v1

**Date:** 2026-06-25
**Anchor:** substrate_NESS_envelope_alpha_high_extension_v1
**Script:** experiments/exp_substrate_NESS_envelope_alpha_high_extension_v1.py
**Queue:** local_cpu_queue (numpy; ~30min CPU per Research drill estimate)
**Seeds:** [11, 13, 19] (cross-cell consistent; reference cell used [1,2,3])
**ALPHA_FRACS (full):** [0.7, 0.8, 0.85, 0.9, 0.95]

## Promotion context (Tier S #2 / Research DRILL 1 ITEM 3)

Reference cell (`exp_kmax_ness_envelope_corrected_v1` = `exp_kmax_ness_envelope_gpu_v1`)
HARD_PASS chain-grade @ ALPHA_FRAC in [0.3, 0.7]. Verbatim:
```
HARD_PASS: cand2 >= 2x on >=4/5 AND cleanup-extension GENUINELY traverses
(per-hop correct-next-node) AND control genuinely exceeds equilibrium.
ctrl/eq(safe)={0.3: 1.27, 0.4: 1.74, 0.5: 2.44, 0.6: 4.07, 0.7: 8.35}
cand/eq={0.3: 2.12, 0.4: 2.91, 0.5: 4.21, 0.6: 6.17, 0.7: 12.27}
ext_hopfrac={0.3: 1.0, 0.4: 1.0, 0.5: 1.0, 0.6: 1.0, 0.7: 0.99}
ext_genuine=True | n_safe=5
```

LIFT cand/eq is MONOTONICALLY INCREASING through 0.7 (2.12 -> 12.27). ext_hopfrac stays >= 0.99
(degradation BEGINS at 0.7 -- the FIRST sign of cliff). Predicted cliff per Hatano-Sasa NESS
theory: between alpha_frac in [0.85, 0.92].

Research drill: P=0.45 but monotone-trend supports extension; compute ~30min CPU (cheapest in
drill). Closes the NESS envelope question definitively.

## v1 design (alpha-high extension)

- ALPHA_FRACS in {0.7 (rail), 0.8, 0.85, 0.9, 0.95} (5 points; rail + 4 extension)
- All other config matched to reference cell:
  - ALPHA_C = 0.138 (Amit-Gutfreund-Sompolinsky Hopfield critical capacity; INDEPENDENT)
  - K_GRID = [3, 6, 12, 18, 24, 36, 48, 60, 80, 100, 120]
  - N_CHAINS = 24, N = 8192
  - RECALL_THRESH = 0.90 (cleanup-ON gate)
  - GENUINE_FLOOR = 0.30 (cleanup-OFF control floor)
- Per-hop correct-next-node discriminator (ext_hopfrac >= 0.85 = genuine traverse; tightened to
  >= 0.95 for chain-grade gate in this cell vs reference 0.85; HP_EXT_HOPFRAC_MIN = 0.95)

NB: this cell runs CPU numpy (vs reference's GPU torch) -- the reference's WORK ALSO ran via
numpy in the corrected version. At N=8192 and 5 alpha points x 3 seeds, CPU is sufficient. The
"GPU" suffix in the reference is historical; the corrected variant didn't actually need GPU.

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_ALPHA_EXTENSION (chain-grade at alpha_frac=0.85)
- At alpha_frac = 0.85: ratio_to_eq >= **2.0** across seeds
- AND ext_hopfrac >= **0.95** across seeds
- AND ext_hopfrac cv across seeds <= **0.05**

### CHAIN_GRADE_AT_ALPHA_CLIFF
- Chain-grade gate passes at one of {0.8, 0.9, 0.95} but not 0.85
- Envelope extends to identified alpha; cliff identified at next alpha

### MIDDLE_BAND_PARTIAL_EXTENSION
- Some alpha above 0.7 holds ext_hopfrac >= 0.85 (weaker gate from reference cell)
- But no chain-grade gate fires (need ratio>=2.0 AND ext_hopfrac>=0.95 AND cv<=0.05)

### HARD_FAIL_RAPID_DEGRADATION
- NO alpha above 0.7 holds ext_hopfrac >= 0.85 (cliff at af=0.75 or earlier)

### HARD_FAIL_NO_EXTENSION_BEYOND_RAIL
- Chain-grades ONLY at af=0.7 rail; envelope does NOT extend

## Q-discipline guard (BIAS-Q)

If ext_hopfrac >= **0.995** at ALL alpha_fracs through 0.95:
- Verdict carries `[Q-DISCIPLINE: ext_hopfrac >= 0.995 at af=...; suspect saturation]`
- Recommend deeper K_GRID or higher alpha_c
- Flag is documentation, not auto-demotion

## Cross-cell discipline

- ASCII only (verified)
- Substrate-only at inference (numpy; zero LLM forward calls; counter asserted = 0)
- Per-alpha metrics in verdict_msg + per_unit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent; FRESH seeds vs reference's [1,2,3] per
  META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- META_M6: K_eq baseline DERIVED in-cell from INDEPENDENT alpha_c=0.138 (not substrate-tuned)
- META_M7: smoke matches full on N + N_CHAINS + RECALL_THRESH + EXT_GENUINE_THRESH
  Only K_GRID + SEEDS + ALPHA_FRACS reduce in smoke

## Capacity-feasibility analysis

Per-(seed, alpha) wall: dominated by N_CHAINS chains each with W matrix N x N and K hops.
N=8192 -> W is 8192x8192 float32 = 256MB. With N_CHAINS=24 and K up to 120, ~3000 matmuls per
unit. Reference cell measured ~885s total at GPU for 5 alpha x 3 seeds = ~60s per (seed, alpha).

CPU at N=8192: expected ~5-10x slower than GPU = 300-600s per (seed, alpha) = 5-10 min per unit.
With 5 alphas x 3 seeds = 15 units, total wall = 1.25-2.5h.

Drill estimate said 30 min -- this assumed smaller N (perhaps N=1024). At N=8192 production-grade
the realistic CPU wall is closer to 2h. Routing rationale below addresses this.

## Routing rationale

Initially considered GPU but:
- Reference cell ran corrected variant with same N=8192 successfully on GPU at ~885s
- CPU at N=8192 may push wall up to 2h+ -- borderline
- Local CPU runner is what's available; GPU runner is busy with v3 anisotropy + Cell B intent v2 + g1b
- 2h wall is acceptable for local CPU (no other CPU-bound cells queued; we have bandwidth)
- If wall is unacceptably long, can reduce N to 4096 (still well above K_max=120 cleanup bound)

Decision: **route to local_cpu_queue** with generous 7200s (2h) timeout. CPU available.

## Timeout estimate

Formula: timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^2.0 * (FULL_seeds/smoke_seeds) *
                          (FULL_alpha/smoke_alpha))

Smoke wall = 10.4s (3 units at N=1024). N grows 1024 -> 8192 (8x; matmul O(N^2)); seeds 1 -> 3;
alphas 3 -> 5.

ceil(1.5 * 10.4 * 64 * 3 * (5/3)) = ceil(4992s) = ~83 min.

Conservative budget: **timeout_s = 7200 (2h)** -- accounts for K_GRID full sweep + per-unit
checkpoint resume. Below 14400s PROT-021 threshold; checkpoint wired per-(seed, alpha).

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor has no `_n<N>` suffix.
- PROT-019 (large-N timeout floor): no `_n<N>` suffix.
- PROT-020 (GPU queue requires torch): local_cpu_queue path; rule does not apply.
- PROT-021 (long-timeout needs checkpoint): timeout 7200s < 14400s; per-unit checkpoint wired.

## Pre-flight smoke + self-test gate

- Smoke runs with `RUN_MODE=smoke`: N=1024, N_CHAINS=8, K_GRID=[3,6,12,24,40], seeds=[11],
  ALPHA_FRACS=[0.7, 0.85, 0.95]
- Smoke wall measured: 10.4s (well under 180s queue_add cap)
- Self-test asserts T1-T5:
  T1 safe_gate_high admits 0.7..0.95; T2 bipolar +/-1; T3 run_unit end-to-end at N=256;
  T4 bands locked; T5 LLM counter = 0
- Self-test PASSED LOCAL (verified before commit)

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions:
- HARD_PASS_ALPHA_EXTENSION (envelope extends to 0.85)
- CHAIN_GRADE_AT_ALPHA_CLIFF (envelope partially extends with cliff identified)
- MIDDLE_BAND (weak gate only)
- HARD_FAIL_RAPID_DEGRADATION (cliff at 0.75)
- HARD_FAIL_NO_EXTENSION_BEYOND_RAIL (chain-grade only at 0.7 rail)
- Per (seed, alpha_frac) per_unit detail for Skunkworks step-0 re-read

## Strategic significance (decision-grade)

If HARD_PASS_ALPHA_EXTENSION (envelope to 0.85+):
- NESS chain-recall envelope extends 5x in lift (12.27 -> potentially 100x at af=0.95 if monotone holds)
- Substrate-product positioning: "NESS deep-chain recall lifts MASSIVELY past equilibrium ceiling"
- Composes with sequence-binding c3 cells for genuinely deep multi-hop reasoning

If CHAIN_GRADE_AT_ALPHA_CLIFF:
- Cliff identified between 0.7-0.95; honest envelope boundary
- Substrate-product: "envelope safe up to identified cliff; beyond requires alpha-scheduling"

If HARD_FAIL_RAPID_DEGRADATION:
- NESS chain-recall is alpha-bounded; can't extend past 0.7 even though lift is monotone
- The monotone-lift trend at low K_eq becomes degenerate (numerator high, denominator near-zero;
  ext_hopfrac drops as the chain "jumps" rather than traverses)

## Honest negatives possible

- ext_hopfrac may collapse below 0.85 at alpha_frac=0.80 (rapid degradation)
- K_obs may flatten at high alpha (K_eq -> 0 makes ratio_to_eq trivially large without genuine traverse)
- Per-seed variance at high alpha may push cv above 0.05 (NESS is sensitive at extreme alpha)
- At alpha_frac=0.95, K_eq ~ 0.06 -- any K_obs > 0.06 gives ratio_to_eq >> 2.0 trivially;
  the discriminator is whether ext_hopfrac stays >= 0.95 (genuine traversal vs cleanup-jump)

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (T1-T5 PASS)
3. Smoke run PASSED locally -- DONE (verdict HARD_PASS_ALPHA_EXTENSION at smoke; Q-discipline fires)
4. Path-scoped commit BEFORE dispatch (cell + prereg only)
5. Dispatch via `bash tools/orchestrator/queue_add.sh local_cpu_queue substrate_NESS_envelope_alpha_high_extension_v1 experiments/exp_substrate_NESS_envelope_alpha_high_extension_v1.py preregs/2026-06-25_substrate_NESS_envelope_alpha_high_extension_v1.md 7200`
6. File dispatch notification in batch note

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per_alpha_frac ratio_to_eq + ext_hopfrac
  (NOT verdict_msg framing)
- Verify ext_hopfrac cv across 3 seeds at each alpha_frac is <= 0.05 for chain-grade claim
- Compare alpha_frac=0.7 slice to reference cell (sanity check regime parity; expect ratio ~12.27)
- If HARD_PASS_ALPHA_EXTENSION: queue composition with deep-K sequence-binding cell (c3 extension)
- If HARD_FAIL_RAPID_DEGRADATION: queue diagnostic (per-hop correct-next-node curve detailed)
