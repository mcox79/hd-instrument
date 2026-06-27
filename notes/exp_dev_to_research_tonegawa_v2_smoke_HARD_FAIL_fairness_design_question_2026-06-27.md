# exp_dev -> research: tonegawa sparse-ensemble v2 smoke HARD_FAIL (fairness; design question)

**Filed:** 2026-06-27
**Cell:** cortex_schema_tonegawa_sparse_ensemble_v2
**Smoke verdict:** HARD_FAIL (FAIRNESS REGIME SATURATION; fairness-gate correctly fired)
**Queue action:** NOT DISPATCHED (per "smoke HARD_FAIL fairness -> surface to research, DON'T silent-fail")
**Recipient:** research (drill author)

## 1-line summary

cell authored + cert-grade hardening + self-tests PASS | smoke HARD_FAIL (PROTOTYPE/NO_SCHEMA saturate at 1.000 even at K=100; TONEGAWA underperforms baselines by -0.13) | NOT QUEUED (design question for research); proposed v3 fork-paths in prereg

## Smoke metrics (K=100, N_DIM=1024, BCC=0.45, DRIFT=0.45, PERTURB=0.50, WCN=0.70; seed=7)

| arm | recall@5 | role status |
|-----|----------|-------------|
| ARM_NO_SCHEMA | 1.000 | SATURATED (fair-floor violated) |
| ARM_PROTOTYPE_CENTROID | 1.000 | SATURATED (fair-middle violated) |
| ARM_TONEGAWA_SPARSE_K20 | 0.870 | underperforms baselines by -0.130 |
| ARM_TONEGAWA_SPARSE_K10 | 0.628 | k-sensitivity confirmed (k=10 worse) |
| ARM_DIAG_RANDOM_SPARSE_K20 | 0.048 | false-accept floor honest (chance 5/100) |

## What the diagnostic data tells us (verify-the-referent)

The sparse-ensemble MECHANISM is implemented correctly:
- DIAG_RANDOM at 0.048 ~ chance (5/K_clusters with TOP_K_RECALL=5) -> sparse-overlap scoring is fair
- K10 < K20 -> sparsity is the meaningful axis (k matters)
- K20 >> RANDOM -> structured codes carry signal

But the **regime is wrong for the mechanism**: in well-separated K=100 clusters
at BCC=0.45 with N_DIM=1024, PROTOTYPE_CENTROID trivially wins because cosine
captures cluster identity at this scale. k-WTA is a LOSSY compression of the
centroid -> it can only LOSE in regimes where cosine already saturates.

Tested 3 progressively-harder regimes during smoke calibration:
- K=8, BCC=0.35: all arms 1.000 (chance floor 5/8 too high)
- K=40, BCC=0.35, drift=0.25: NO_SCHEMA + PROTOTYPE + TONEGAWA all 1.000
- K=40, BCC=0.45, drift=0.45, WCN=0.70, perturb=0.50: TONEGAWA drops to 0.917 but PROTOTYPE stays 1.000
- K=100, BCC=0.45 same: PROTOTYPE still 1.000; TONEGAWA 0.870

## Root-cause diagnosis (mechanism-design level)

The drill TOP-2's "capacity@95%-recall" advantage requires BUNDLED memory where
all K schemas SHARE one substrate vector and queries unbind. v2 implements
isolated-bank retrieval (each cluster is its own row in a (K, N_SCHEMA_CELLS)
bank). Cosine baselines win trivially because there's no interference between
schemas to bound.

**The brain-grounded Tonegawa advantage emerges where:**
- Multiple schemas coexist in shared cortical sheet (bundled)
- Cluster centroids partially alias (overlapping retrieval cues)
- High K relative to substrate capacity (interference-dominated regime)

v2's regime hits NONE of these.

## Proposed v3 fork-paths (research to choose)

**Option A: v3 BUNDLED capacity test**
- Bundle all K sparse-schema-codes into ONE vector: `S = sum_k XOR(schema_id_k, sparse_code_k)`
- Query unbinds: `s_query = XOR(schema_id, S)`; match against k-WTA(s_query)
- PROTOTYPE_CENTROID analog: `C = sum_k XOR(schema_id_k, centroid_k)` (dense bundle)
- TONEGAWA should win here as K grows (sparse codes have lower crosstalk than dense centroids)

**Option B: v3 HIPPO-HANDOFF regime**
- Push BCC to 0.55-0.65 (BEYOND drill's [0.30, 0.45]); centroids partially alias
- TONEGAWA k-WTA assigns DISTINCT sparse subsets even when centroids overlap (DG pattern-separation)
- PROTOTYPE collapses to mean of overlapping centroids -> drops below 0.95 baseline floor

**Option C: drop Tonegawa for now**
- Brain-grounded mechanism doesn't win in cosine-baseline-saturating regimes
- v3 fork to a different drill mechanism (A2 sufficient-statistics, A3 information-bottleneck)

## Artifacts

- `experiments/exp_cortex_schema_tonegawa_sparse_ensemble_v2.py` (cert-grade; selftests PASS)
- `preregs/2026-06-27_cortex_schema_tonegawa_sparse_ensemble_v2.md` (bands + diagnosis + v3 paths)
- `data/exp_cortex_schema_tonegawa_sparse_ensemble_v2/metrics.json` (smoke HARD_FAIL data)

## What I'm NOT doing

- NOT queueing full dispatch (would waste ~10-15 CPU-min; smoke already shows HARD_FAIL pattern is regime-not-cell)
- NOT silent-failing (per USER directive 2026-06-26 + meta-rule)
- NOT modifying cell to FORCE PASS (would be Q-discipline violation)

## What I AM doing

Surfacing honestly; cell is cert-grade and ready for either v3 redesign or
research-directed regime change.
