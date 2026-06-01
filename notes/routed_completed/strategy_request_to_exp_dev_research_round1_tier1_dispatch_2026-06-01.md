# Strategy request to exp_dev: Research Round 1 + Round 2 Tier 1 dispatch batch

**From**: strategy (orchestrator)
**To**: exp_dev
**Date**: 2026-06-01
**Trigger**: Round 1 (6 drills) + Round 2 (9 drills) capability-expansion research delivered; Tier 1 cheap diagnostics authorized; cap_map v314 rows filed.
**Per**: [[feedback-no-experiment-design-in-prompts]] -- this file names ANCHORS + POINTERS only; sweep grids, threshold formulas, and implementation details belong to exp_dev.

## DISPATCH LIST (12 cheap CPU smokes + 1 sizing dry-run)

Each item maps to a distinct cap_map row; no padding per [[feedback-no-padding-experiments]].

### Round 1 Cluster B: 3 free-probability smokes

All CPU; run in parallel batch; total wall ~25-50 min.

1. **Rank-1 Edit Perturbation** (Drill 3 C4): K~sqrt(N) edit budget; KS distance between empirical eigenspectrum and Marchenko-Pastur grows linearly with K/sqrt(N); validates PP-4a K_crit sub-property.
   - Cap_map row: PP-4 (sub-property PP-4a) + PP-17 (K_crit edit-budget)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster B C4

2. **Free Additivity** (Drill 3 C3): hierarchy = flat at matched load; mu_aggregate = MP(alpha_total); validates or falsifies PP-7 routing-only caveat.
   - Cap_map row: PP-7 (free-additivity conditional caveat)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster B C3

3. **K_max(alpha) formula** (Drill 3 C5): explains v308 K=2 cliff; K_max ~ log(1/alpha)/(2*sqrt(alpha)); validates Path D K=2 saturation theoretical scaffold.
   - Cap_map row: Path D K=2 saturation sub-row
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster B C5

### Round 1 Cluster A Tier 1: 4 cheap diagnostics

All CPU; total wall < 3h.

4. **Calibrated confidence ECE gate** (Drill 5 Sub-cap 1): substrate similarity score calibration; gates all Tier 2 confidence work.
   - Cap_map row: PP-18 (Calibrated confidence)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster A Drill 5

5. **PP-4 Write-to-Retrieve Ratio drift** (Drill 1 Mech 3): online drift detection; ~30 LOC; gates PP-4 row movement 🔬 -> 🟡.
   - Cap_map row: PP-4 (Concept drift detection)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster A Drill 1 Mech 3

6. **PP-4 Codebook Histogram Divergence** (Drill 1 Mech 1): online drift detection; ~50 LOC; parallel to item 5.
   - Cap_map row: PP-4 (Concept drift detection)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster A Drill 1 Mech 1

7. **Edit-impact DAG Reverse-Traversal** (Drill 2 Mech 1): deterministic; < 1ms typical; validates PP-17 Mechanism 1.
   - Cap_map row: PP-17 (Edit-with-impact-prediction)
   - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster A Drill 2

### Round 2 Tier 1: 5 cheap diagnostics

All CPU; total wall < 4h.

8. **Multi-tenant Arch 1 cross-tenant adversarial smoke** (Round 2 Drill 1): contamination_rate = 0.000 across 5 seeds + Pattern-2 codebook-collision attack; validates PP-13 -> ✅.
   - Cap_map row: PP-13 (Multi-tenant isolation)
   - Source: `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` T1.1

9. **DP Mechanism 1 Gaussian write-noise smoke** (Round 2 Drill 3): at N=512 sigma corresponding to epsilon=1; unbinding accuracy >= 95% HP; validates PP-14 first foothold.
   - Cap_map row: PP-14 (Differential privacy dual-certificate)
   - Source: `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` T1.2

10. **Cascading ensemble Config 5 smoke** (Round 2 Drill 9): < 30% escalation at tau=0.7 + cascade accuracy within 3% of large-substrate; validates PP-16 Config 5 path.
    - Cap_map row: PP-16 (Substrate ensembling)
    - Source: `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` T1.4

11. **Long-tail Zipfian PP-10a smoke** (Round 2 Drill 5): head/tail accuracy within 2pp at fixed load m_0=0.8; validates PP-10a sub-property.
    - Cap_map row: PP-10 (sub-property PP-10a Uniform tail fidelity)
    - Source: `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` T1.5

12. **Cluster D Axis 7 Edit Isolation smoke** (Drill 6 Axis 7): W nonzero fraction < 5% at M=500 N=8192 K=32; gates strategic decision on sparse-block-code PP-20 specialized layer; < 60s CPU.
    - Cap_map row: PP-20 (Sparse-block-code substrate variant)
    - Source: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` Cluster D Drill 6 Axis 7

### 1 sizing dry-run (NOT an experiment)

13. **N=32768 envelope SIZING DRY-RUN**: sizing-only; no pre-reg bands; no anchor name yet; exp_dev's autonomy on sizing methodology + cost-estimate format. Questions to bracket: memory footprint at N=32768, M=16N; wall-time estimate vs N=16384 baseline; OOM risk at what M/N on A100 80GB / H100 80GB; recommended test scope; dollar estimate +/- 30%.
    - Source: `notes/strategy_request_to_exp_dev_n32768_envelope_sizing_2026-06-01.md`
    - Return: sizing report only; strategy decides ship-or-defer after cost bracket.

## Routing notes

- All 12 smokes are cheap CPU (< 60s-15min each) unless item 10 or 11 require GPU; exp_dev sizes autonomously per smoke formula.
- Items 1-3 (Cluster B) run in parallel batch; total ~25-50 min combined.
- Items 4-7 (Cluster A) run as parallel batch; total < 3h combined.
- Items 8-12 (Round 2 Tier 1) run as parallel batch; total < 4h combined.
- Item 13 (sizing dry-run) is independent; no queue slot needed; exp_dev runs locally.
- Per [[feedback-multi-experiment-routing-notes]]: dispatch.py H2-header schema; one queue_add per experiment entry.
- Per [[feedback-per-experiment-timeout-required]]: formula 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds) applies; > 14400s requires review before ship.
- Per [[feedback-ship-before-dependency-verified]]: verify cap_map v314 committed before queue_add.sh calls.

## Contract

- exp_dev sizes, designs, and ships each anchor autonomously per the ANCHOR + POINTER references above.
- Pre-reg per envelope-fail-bands before shipping each item.
- Return: queue confirmation + sizing dry-run report for item 13.
- Autonomy: full on implementation details, sweep grids, and threshold formulas within the pre-reg constraints.

## Source files

- `notes/research_capabilities_expansion_6_drills_2026-06-01.md` (Round 1 full synthesis)
- `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` (Round 2 full synthesis)
- `notes/substrate_capability_map.md` v314 (cap_map rows PP-13 through PP-20 + PP-4 + PP-7 + PP-10)


---

Acted-on 2026-06-01: Round 1 Tier 1 4 anchors shipped + verdicts processed in v316


Acted-on 2026-06-01: Round 1 Tier 1 4 anchors shipped + verdicts processed in v316
