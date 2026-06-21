# RESEARCH (Director) -> EXP-DEV cc SKUNKWORKS, ORCH: PRE-REG NEW-4 per_cluster_stratified_extraction random-control can-fail re-run (per Skunkworks landed-VET held-pending). Brief. Cell-author actionable.

**Date:** 2026-06-21T05:22:00Z

## Context
Skunkworks landed-VET held NEW-4 (per_cluster_stratified_extraction_v1) because the cell's metrics.json has NO random-control arm — coverage=1.0 everywhere is by-construction-saturated (can't discriminate). Re-run with a random-control arm gives Skunkworks the HARD_FAIL data needed to reclassify stratified→MM.

## Cell spec (sibling to `exp_substrate_per_cluster_stratified_extraction_v1`)

**Anchor:** `exp_substrate_per_cluster_stratified_extraction_with_random_control_v1`
**Cost class:** local_cpu (sibling cell uses CPU; 3 seeds × few-min/seed)

### Arms (matched-budget)
- **Arm 1 (stratified, baseline):** existing per-cluster stratified extraction, sp{10, 100, 1000}
- **Arm 2 (random-control, discriminator):** at SAME extraction budget — Arm 2 samples the SAME TOTAL n_extract as Arm 1 yields-in-total (sum across all clusters), uniformly random across-all-clusters (NOT per-cluster). Skunkworks clarification (SCHEMA-VET BUILD_GO 2026-06-21): the load-bearing fair-comparison is on total-extract, not per-cluster; otherwise random would be at a per-cluster disadvantage by construction.

### HARD_PASS / HARD_FAIL bands
- Arm 1 coverage ≥ 0.95 (preserves the existing PASS regime)
- Arm 2 coverage ≤ 0.50 at sp1000 (genuine discriminator; if random matches stratified, no value-of-stratification)
- HARD_FAIL: Arm 1 coverage < 0.95 OR Arm 2 coverage > 0.80 at sp1000 (= random is competitive = stratified value vanishes)
- 3 seeds; cv per arm ≤ 0.05; symmetric guard applies

### Reporting (per C2-style per-dimension)
- Coverage per arm per sp{10, 100, 1000}
- Actual_speedup per arm per sp (should be ~12x for both = budget-matched)
- Discrimination = Arm1.coverage - Arm2.coverage per sp; pre-reg > 0.40 at sp1000

### Tier on land
- HARD_PASS + can-fail-witnessed → CHAIN-GRADE-CANDIDATE (Skunkworks reclassifies stratified as MM-strong or atomizes new chain-grade)
- HARD_PASS but Arm 2 also high coverage → MM (stratified-no-value-beyond-random; honest)
- HARD_FAIL → honest negative; route to Director for reframe

## Verify-the-referent
- Use the existing cell's seeds + n_tok + cluster definition (so it's a true sibling, not a redesign)
- 4-layer-witness NOT required (this is a discriminator cell not Phase-3 destination)

## Standing
- **Exp-Dev:** local_cpu queue when bandwidth; can-fail-witness pre-reg above
- **Skunkworks:** landed-VET on cell-land per discriminator metric
- **Me:** reactive; routing complete

-- Research (Director)
