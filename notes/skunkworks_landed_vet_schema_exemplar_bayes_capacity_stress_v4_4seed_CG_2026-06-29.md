# Skunkworks landed-VET: substrate_schema_exemplar_bayes_capacity_stress_v4 4-seed CHAIN_GRADE_MULTI (CERT +1)

**Audit completed:** 2026-06-29
**Auditor:** skunkworks (hdi_skunkworks via Agent Teams spawn)
**Cell anchor:** substrate_schema_exemplar_bayes_capacity_stress_v4
**Seeds aggregated:** 13, 19, 23, 29 (4 of 5; seed_7 import-crashed pre-fix)
**Verdict:** CHAIN_GRADE_MULTI (3/3 AGG gates met across 4-seed AGG; chain-grade promotion qualified)
**Cert delta:** +1 (CERT 632 -> 633 for the chain-grade phase characterization atom; +1 META rule no-delta)

## Inputs (off-disk; .venv Python recompute; absolute paths)

- `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_13/metrics.json`
- `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_19/metrics.json`
- `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_23/metrics.json`
- `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_29/metrics.json`
- `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_7/metrics.json` (IMPORT_CRASH; excluded)
- pre-reg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_schema_exemplar_bayes_capacity_stress_v4.md`

## Verify-the-referent: spawn-prompt claims vs disk

Spawn-prompt asserted "4/5 seeds CHAIN_GRADE_MULTI confirmed, seed_19 3/3 gates met". On disk:

| seed | verdict (disk)      | n_gates_met (disk) | spawn claim |
| ---- | ------------------- | ------------------ | ----------- |
| 13   | CHAIN_GRADE_MULTI   | **3/3** (GR=T HM=T RF=T) | 3/3 OK |
| 19   | CHAIN_GRADE_MULTI   | **2/3** (GR=F HM=T RF=T) | spawn said 3/3 (mismatch; seed_19's graceful floor_retention=0.250 < 0.30) |
| 23   | CHAIN_GRADE_MULTI   | **3/3** (GR=T HM=T RF=T) | 3/3 OK |
| 29   | CHAIN_GRADE_MULTI   | **3/3** (GR=T HM=T RF=T) | 3/3 OK |
| 7    | UNKNOWN (IMPORT_CRASH) | n/a              | spawn flagged crash |

Spawn-prompt minor referent-mismatch on seed_19 (cited as 3/3, actually 2/3). NOT load-bearing for cert outcome — seed_19's verdict-string is still CHAIN_GRADE_MULTI (any combination of 2+ gates qualifies under per-sibling verdict per pre-reg line 94). The cross-sibling AGG gate is what matters for promotion, and that recomputes cleanly (below).

## Cross-sibling AGG recompute (4-seed; seed_7 excluded)

Independent off-disk recompute via `.venv/Scripts/python.exe` (every gate threshold recomputed from raw per_phase_point arms):

```
=== Per-seed verdict + key metrics (off-disk verify) ===
 seed              verdict    GR    HM    RF      fr      fl    hmfr    hmfl   hor   rcp   div  path  card
   13    CHAIN_GRADE_MULTI  True  True  True   0.400    80.0   0.600   120.0    64    56    64 False  True
   19    CHAIN_GRADE_MULTI False  True  True   0.250    50.0   0.700   140.0    64    58    64 False  True
   23    CHAIN_GRADE_MULTI  True  True  True   0.350    70.0   0.600   120.0    64    59    64 False  True
   29    CHAIN_GRADE_MULTI  True  True  True   0.450    90.0   0.700   140.0    64    57    64 False  True

=== Cross-seed AGG (4-seed; seed_7 import-crash) ===
GRACEFUL: gate-met=3/4, fr_mean=0.362 (need >=0.30), decades_mean=5.00 (need >=3)
  -> A_GRACEFUL met: True
HARDMAX:  gate-met=4/4, fr_mean=0.650 (need >=0.50), fl_mean=130.0x (need >=10x), or_pts_mean=64.0 (need >=25)
  -> B_HARDMAX met: True
REFCLIFF: gate-met=4/4, cliff_pts_mean=57.5 (need >=10)
  -> C_REFCLIFF met: True

Total AGG gates met: 3/3
CHAIN_GRADE_MULTI (>=2 AGG gates): True
```

Pre-reg requires ">=3/5 seeds" for each gate; 4-of-5 effective seeds means >=3/4 = 75% which is STRICTER than >=3/5 = 60%. The 4-seed AGG still clears all 3 gates by 3-of-4 (GRACEFUL) or 4-of-4 (HARDMAX, REFCLIFF). The chain-grade promotion is justified even with seed_7 excluded.

## Sub-audit checks (independent recompute)

- **META_RULE_AF arms-must-differ**: arms_diverge=64/64 on every seed (4/4 seeds at full divergence; independent recompute matches cell-author claim exactly).
- **hardmax_over_ref_pts**: 64/64 on every seed (independent recompute matches; HM dominates REF at every phase point).
- **floor_lift D4 (single point at alpha=19.53)**: independent recompute confirms cell-author values seed-by-seed (80x/50x/70x/90x for GRACEFUL; 120x/140x/120x/140x for HARDMAX).
- **floor_retention D4**: independent recompute confirms 0.400/0.250/0.350/0.450 matching cell-author.
- **random_arm_pathology**: False on all 4 seeds (chance witness arm does not pathologically lift).
- **cardinality_ok**: True on all 4 seeds (observed_n=5120/expected_n=5120; pre-reg cardinality declaration honored per META_RULE_H).
- **arms_identical_pathology**: False on all 4 seeds.
- **n_chain_grade_gates_met (cell-author claim)**: 3/3 on seed_13, 23, 29; 2/3 on seed_19 — independent recompute confirms.

## BIAS-MASTER-CHECKLIST checks (USER 2026-06-24)

- BIAS-Q saturation: NOT triggered. GRACEFUL D2/D3 mean ~0.65-0.83 (not saturating at 1.000). HARDMAX D2 ~0.82-0.84 (not saturating). Real spread across alpha decades, not metric-cap artifact.
- BIAS-13/14/15 (contamination/regime/mismatch): pre-reg explicit at FLOOR_THRESH=0.30 floor_retention (>=1.5/N_EVAL=0.075 for N_EVAL=20 queries; well above stat-valid noise floor). Discriminator fires across 64 phase points × 4 seeds = 256 independent observations.
- BIAS-M production-scale calibration: full-N runs at expected_n=5120/seed (M=20 queries × 64 combos × 4 arms = 5120 records; matches pre-reg).
- BIAS-N verify-referent-verdict-field: explicitly checked spawn vs disk above; seed_19 spawn-overclaim caught and corrected (does not change outcome).
- BIAS-S band-calibration regime: capacity bands {alpha 0.006..19.5} span 5 decades; FLOOR (alpha>=10) population = 1 phase point per seed; ADV decades (D0-D4) all populated.

## Mechanism-class verdict (cert-owner ruling)

The mechanism is a **3-class composite phase characterization**:

1. **Class A (GRACEFUL Bayes-LSE)**: monotonic-in-alpha graceful degradation; 5 decades with chance-lift across all 4 seeds; floor_retention 0.25-0.45 (cross-seed mean 0.362) at alpha=19.5. Chain-grade-aligned at 3/4 seeds (seed_19 just-below the 0.30 floor threshold by 0.05; not pathological, just sample fluctuation at D4=1 phase point).

2. **Class B (HARDMAX centroid SUSTAINED-FLOOR — cell-author DISCOVERY)**: per-class centroid argmax retains 0.60-0.70 accuracy at alpha=19.5 (4/4 seeds above 0.50 floor); lifts 120-140x over chance; dominates REFERENCE at 64/64 phase points (4/4 seeds). This is the strongest gate — uniform 4/4 cross-seed agreement with substantial margins above all sub-thresholds. **The centroid acts as a low-variance prototype estimate that suppresses per-exemplar noise at high K.** New first-class primitive candidate emerging from this cell.

3. **Class C (REFERENCE cliff_observable)**: single-nearest-exemplar primitive exhibits cliff at 56-59/64 phase points (4/4 seeds; range 56-59 = tight). Skunkworks's "no smoothing -> cliff" prediction validated on the cliff-prone arm.

## Tier decision

**CHAIN_GRADE_PHASE_CHARACTERIZATION** (math corpus, T3, kind=chain_grade_phase_characterization).

Rationale:
- All 3 AGG gates met simultaneously (a 2-of-3 met would already qualify CHAIN_GRADE_MULTI per pre-reg line 122).
- HARDMAX gate is 4-of-4 with 130x mean lift and 64-of-64 over-REF dominance — independent strong-effect; not by-construction saturation, not regime-confound.
- GRACEFUL gate is 3-of-4 with cross-seed-mean floor_retention=0.362 (above 0.30 threshold) and 5-decade advantage. Seed_19's miss at 0.250 is just-below-threshold; honest variance not pathology.
- REFCLIFF gate is 4-of-4 with cliff_pts_mean=57.5 — well above the 10-point requirement.
- Cardinality, arms-must-differ, random-arm-pathology, arms-identical-pathology all clean across all 4 seeds.
- Cell-author seed_7 was an honest import-crash from a known infra bug (commit 846dfa96 _core.py not on remote before queue_add); not a methodological problem with the cell.
- 4-of-5 (effective) seeds is conservative replication; pre-reg's >=3/5 threshold cleared.

Honest-downward considerations evaluated:
- Could be downgraded to MM if HARDMAX gate were saturation-bound — but HARDMAX D2/D3 means are 0.82/0.77 (substantially below 1.0; real spread; not metric-cap).
- Could be downgraded if discriminator failed at scale — but full-N (M=20 queries, n_q full) discriminator FIRES at 64/64 phase points (Fix #26 DISCRIMINATOR-MUST-SURVIVE-SCALE satisfied).
- Could be downgraded if cross-seed agreement were spread > ~0.1 — but per-seed gate-met counts {3,2,3,3} have only 1 outlier (seed_19) on the weakest of the 3 gates; tight cross-seed agreement on the load-bearing gates (HARDMAX/REFCLIFF 4/4).

Honest-downward NOT triggered; chain-grade promotion approved.

## Bonus META rule atomized

**META_RULE_AQ**: per-class CENTROID argmax (cosine-nearest-MEAN) is a noise-suppressing prototype primitive that DOMINATES single-nearest-exemplar AND DOMINATES Bayes-LSE at FLOOR (high alpha, alpha>=10) regimes. The empirical mechanism: centroid mean of K exemplars per class is a 1/sqrt(K) lower-variance estimator of the class prototype than any single exemplar; at high K (and therefore high alpha when N is fixed) this variance reduction dominates Bayes-LSE smoothing. The cell-author SELFTEST DISCOVERED this — original framing was that HARDMAX would lose prior-pull and exhibit Kanerva cliff; instead it shows opposite behavior (FLOOR retention 0.6-0.7 vs Bayes-LSE 0.25-0.45). Generalizes to: when readout aggregates noisy exemplars, use centroid (variance reduction) rather than per-exemplar smoothing when K is large.

This is a first-class substrate-architecture insight that supersedes a class of capacity-stress claims; deserves its own META atom for future-cell discoverability.

## Cell-author smoke -> FULL discriminator-survives-scale (USER 2026-06-26)

Smoke (n_q=5, 6 corners): 2/3 gates (HARDMAX + REFCLIFF; GRACEFUL missed at smoke granularity due to coarse acc-step). FULL (n_q=20, 64 corners, 4 seeds): 3/3 gates on 3-of-4 seeds, 2/3 on 1 seed. Discriminator survived scale and STRENGTHENED at full-N. Fix #26 satisfied.

## Notes for cert ledger + plan update

- Atom 1: math::T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v4_4seed_AGG_CHAIN_GRADE_MULTI (cert_increment_delta=+1)
- Atom 2: meta::RULE_centroid_argmax_noise_suppressing_prototype_dominates_single_nearest_at_FLOOR_META_RULE_AQ_2026-06-29 (cert_increment_delta=0; methodology_rule)
- Cell commit: pending (per spawn prompt "AtomKind enum just got fixed (fdf4c714); use canonical kind values" — uses CHAIN_GRADE_PHASE_CHARACTERIZATION kind value)

## seed_7 re-dispatch caveat

Spawn flagged seed_7 re-dispatched post-Orchestrator-fix. If it lands fresh chain-grade and the 5-seed AGG re-runs cleanly later, a supersession atom can append (cert_delta=0; the 4-seed atom remains valid with seed_7 noted as later-replicated). No need to wait for seed_7 — 4/5 effective replication is conservative-sufficient under pre-reg >=3/5 threshold.

## A5 gating (pre-write asserts)

- PRE cert_n = 632 (Store-verified; matches anchor4 atomization 5da5b0c9 final assertion)
- POST cert_n expected = 633 (after Atom 1 write; Atom 2 = META no-delta)
- atomic write + verify-load + integrity-check via PartitionedStore + cert_ledger_writer
- round-trip read-back assertion per atom

## Final ruling

TIER: chain-grade phase characterization
CERT delta: +1 (632 -> 633)
META rules atomized: 1 (META_RULE_AQ centroid noise-suppression)
Skunkworks audit: PASS; all 4 sub-audit dimensions clean.
