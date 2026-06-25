# Skunkworks tier ruling -- Cell 3 (SEMANTIC v3 CV_TIGHTENING) + Cell 4 (multihop consolidation v1)

Date: 2026-06-25
Auditor: skunkworks
Verify-off-data: YES -- pulled metrics.json from remote (marsh@home:C:/dev/hd-instrument/data/...) and independently traced arm-level numbers + cell source for by-construction-saturation arithmetic.

## Cell 3: substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING

**RULING: MEASURED_MECHANISM (not chain-grade upgrade from v2)**

Sub-class: `cv_tightening_target_arm_was_already_at_ceiling_in_v2` + `discriminator_arm_A4_degraded_with_scale`.

### Per-arm evidence (5 seeds: 7, 13, 17, 23, 29)

| Arm | v2 (3-seed, cats=8 attrs=12) | v3 (5-seed, cats=12 attrs=16) | Band |
|-----|-----|-----|-----|
| A1 recall5 | mean 0.993, cv=0.010 | mean 0.996, cv=0.006 | >=0.95 PASS both |
| A2 inh_top1 | mean 0.927, cv=0.069 | mean 0.938, cv=0.031 | >=0.80 PASS both |
| **A3 heldout_top1 (PRIMARY)** | **1.000 across all 3 seeds, cv=0.000** | **1.000 across all 5 seeds, cv=0.000** | >=0.85 PASS but at ceiling |
| **A4 compose_top1 (DISCRIMINATOR)** | [0.75, 0.75, 0.625] mean 0.708 cv=0.083 | [0.583, 0.583, 0.500, 0.583, **0.417**] mean 0.533 cv=0.125 | >=0.50 marginal; seed 29 individually 0.417 BELOW band |
| A5 refuse/retention | 1.000/0.941 | 1.000/0.940 | PASS both |
| A6 chain_completeness | 0.944 cv=0.049 | 0.928 cv=0.045 | >=0.70 PASS both |
| max_cv | 0.083 (A2) | **0.125 (A4)** | DEFINITIVE requires <=0.05 |

### Why MM not CHAIN_GRADE_DEFINITIVE

1. **A3 PRIMARY was already at the metric ceiling in v2** (3/3 seeds = 1.000, cv=0.000). The prereg's UPGRADE target was "A3 top1 >= 0.95 AND max_cv <= 0.05 AND >=5/6 arms PASS." A3 cannot be "tightened" further -- it was already perfect. v3 simply re-confirms perfect-by-measure at a slightly larger scale (12 cats * 4 inst = 48 train + 12 heldout vs v2's 32 + 8). The mechanism `instance -> category -> attribute` chain through 1-hop bindings is structurally guaranteed when category and instance->category bindings are stored cleanly -- this is essentially 1-hop category-attribute lookup via a known category atom (the held-out instance's class). At M_basic=144 atoms / N=8192 dims, capacity ratio 0.018 -- well below 1-hop saturation -- so top1=1.000 is the expected ceiling for the under-loaded primitive, not a multi-hop generalization breakthrough.

2. **max_cv WORSENED (0.083 -> 0.125)** because the discriminator arm A4 degraded with scale. A4 (compositional triple from new category+new attribute) dropped from mean 0.708 to mean 0.533 (-25% relative). This is REAL signal that the compositional primitive scales poorly with categories+attrs -- exactly the kind of result that should NOT be hidden inside a "v3 cv-tightening rerun" framing.

3. **Seed 29 fails A4 band individually** (0.417 < 0.50). The verdict mean (0.533) passes, but per-seed-failure-rate of 1/5 at the discriminator arm with cv=0.125 violates the prereg's spirit (CV tightening was the WHOLE POINT of v3).

### Per-USER discrimination requested
- "Was the cv-tightening achieved by adding seeds or by changing task difficulty?"  Neither succeeded. Adding 2 seeds (3 -> 5) drove A2/A3/A5/A6 CV down marginally but A4's CV went UP from 0.083 to 0.125 because the harder scale (cats 8 -> 12, attrs 12 -> 16) made compositional retrieval more variable. Net effect: max_cv increased.
- "At the larger scale, is A3=1.000 still by-construction-perfect or genuinely-hard?"  Still by-construction at this load. M=144 atoms / N=8192 = 0.018 capacity ratio; the held-out instance is bound to a KNOWN category whose attrs are stored; the chain becomes single-hop attribute retrieval through a known intermediate. To make A3 genuinely-hard you would need either (a) the held-out instance bound to NO category in train (true zero-shot), or (b) load M to >=N to push capacity, or (c) hold out the category ITSELF (not the instance) so the chain has no known intermediate.
- "Compare A1/A2/A4/A5/A6 per-arm to v2 -- ceiling or real lift?"  A1+A5+A6 unchanged (all near-ceiling in both); A2 marginally up (0.927 -> 0.938); A4 SIGNIFICANTLY DOWN (0.708 -> 0.533). NO arm shows a CV-tightening WIN at v3 scale; the discriminator arm shows a CV-loosening LOSS.

### Atom
- Path: `data/substrate_index/math/audit.jsonl` append + `data/substrate_index/meta/cert_ledger.jsonl` row
- atom_id: `math::T3/EXP_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING_MM`
- cert_status: `measured_mechanism`
- cert_increment_delta: 0 (no upgrade from v2; v2 already had ALIVE status without DEFINITIVE)
- cert_class: `mechanism_characterization_cv_tightening_failed_discriminator_degraded`

## Cell 4: substrate_multihop_consolidation_memory_v1

**RULING: MEASURED_MECHANISM (by-construction saturation; NOT a Barrier 1 breakthrough)**

Sub-class: `by_construction_saturation_consolidate_immediate_stores_answer_as_1hop_atom` + `apples_to_oranges_regime_vs_prior_beta_sweep_baseline`.

### Per-arm evidence (3 seeds: 7, 17, 23; n_chains=300; V_C=200 V_P=10 N=8192)

| Arm | Seed 7 | Seed 17 | Seed 23 | Mean | What it proves |
|-----|--------|---------|---------|------|----------------|
| ARM_NAIVE_2HOP | 0.825 | 0.835 | 0.880 | 0.847 | 2-hop chained retrieval at THIS regime |
| ARM_CONSOLIDATE_AFTER_THRESH (k=3) | 0.930 | 0.945 | 0.970 | 0.948 | k=3 consolidation works |
| **ARM_CONSOLIDATE_IMMEDIATE (k=1)** | **1.000** | **1.000** | **1.000** | **1.000** | BY-CONSTRUCTION (see below) |
| ARM_HYBRID | 0.885 | 0.895 | 0.920 | 0.900 | LOWER than CONS_IMMEDIATE |
| hop2_oracle_top1 (1-hop with GT bridge) | 0.900 | 0.880 | 0.910 | 0.897 | 1-hop primitive ceiling at this load |

Rail fired: `HOP2_ORACLE_LOW(min=0.880<0.95)` -- the 1-hop primitive itself does not hit 0.95 even with ground-truth bridge. **CONS_IMMEDIATE hits 1.000 not because multi-hop got fixed, but because the answer was stored as a direct 1-hop atom.**

### By-construction saturation -- the load-bearing finding

Reading `arm_consolidate(...)` at `experiments/exp_substrate_multihop_consolidation_memory_v1.py:245-330`, K_THRESH=1 means EVERY chain's (R1, R2) pair gets a compound predicate built, and for EVERY chain a DIRECT atom `(s, R_compound(R1, R2), o)` is APPENDED into the augmented training set before W is built:

```
for j, q in enumerate(queries):
    s, p1, p2, o = q
    if (p1, p2) in pair_to_idx:
        comp_idx = R_primitive.shape[0] + pair_to_idx[(p1, p2)]
        augmented.append((s, comp_idx, o))   # <-- the ANSWER stored as 1-hop atom
        consolidated_chain_idx.append(j)
W = ingest_hebbian(augmented, E, R_combined, sq, n_dim)
```

At retrieval, the consolidated-chain query reads exactly this atom via `bind(s, R_compound(p1,p2)) -> o`. The retrieval is 1-hop recall of a stored 1-hop atom -- topologically identical to U1 chain-grade primitive (already CERT-PASS). At 200 queries * V_C=200 outputs / N=8192, capacity ratio M/N << 1, so top1=1.000 is the EXPECTED ceiling for 1-hop recall at this under-loaded scale -- not evidence the multi-hop ceiling has moved.

Confirming arithmetic from per-seed: `n_compound_predicates_created = [78, 79, 82]` (one per UNIQUE (R1,R2) pair seen; 10*9=90 possible pairs, ~80 actually used at n_chains=300) and `n_consolidated_chains = 200` (every query gets a compound atom written) -- the W stores 600 primitive 1-hop atoms (300 chains * 2 hops) PLUS 200 direct compound 1-hop atoms = 800 atoms at N=8192. The 200 test queries each have their answer pre-encoded as one of those 200 compound atoms.

### Apples-to-oranges vs prior 0.65 baseline

The director_barrier1 spec says Barrier 1 baseline = "0.65 at V_C=200 V_P=10 N=8192 K_SET=20 chains=200" from `exp_substrate_resonator_softchain_beta_sweep_v1` (verdict HARD_FAIL, BASELINE_HARD=0.6500). Cell 4 reports NAIVE=0.847 at "same" V_C/V_P/N. The difference is NOT methodology drift -- it is a regime difference baked into the chain-construction code:

- Prior beta-sweep `make_two_hop_chains(p1=0, p2=1)`: ALL chains use the SAME predicate pair (p1=0, p2=1). 200 chains stress the SINGLE predicate-pair atomic density.
- Cell 4 `make_chains`: each chain samples its own (p1, p2) uniformly from 10 predicates. 300 chains spread across ~90 ordered pairs -- ~3.3 chains per pair-density.

This makes the NAIVE arms not comparable. Cell 4's NAIVE=0.847 reflects a much-sparser predicate-pair-density regime; the 0.65 baseline was a single-pair-saturated stress test. The cell's own sanity-rail (NAIVE expected [0.40, 0.75]) was BLOWN PAST (0.847 > 0.75 ceiling) but the cell did NOT raise `REPRODUCIBILITY_DIVERGENCE`. **The sanity rail caught the regime mismatch; the cell ignored it.**

### Discriminator pre-reg violations

The prereg states:
- "ARM_HYBRID > ARM_CONSOLIDATE_IMMEDIATE proves the picker is doing useful work (NOT just consolidation)."

Observed: HYBRID 0.900 < CONS_IMMEDIATE 1.000. The picker hurts. The architecture-prereg's own win-condition for "hybrid is the right architecture" is violated.

- "ARM_NAIVE_2HOP must NOT trivially hit top1 >= 0.90 ... if observed > 0.85, flag REPRODUCIBILITY_DIVERGENCE in verdict_msg."

Observed: NAIVE 0.847 (under 0.85 threshold strictly but within rounding), seed 23 individually 0.880 (>0.85). REPRODUCIBILITY_DIVERGENCE not flagged.

### Cross-check: NAIVE sanity-rail vs prior 0.65 baseline

DRIFT confirmed -- but the drift is REGIME, not METHODOLOGY error. Same V_C=200 V_P=10 N=8192, different chain-construction (single fixed predicate-pair vs uniform-sampled predicate-pair). Prior beta-sweep was a tight stress test; cell 4 is a loose distribution.

What this means for the "first cell to break Barrier 1" framing: the cell did NOT break Barrier 1 in the regime where Barrier 1 was diagnosed (V_C=200 V_P=10 single-fixed-pair, NAIVE=0.65). It demonstrated that storing the answer as a direct 1-hop atom recovers 1-hop primitive ceiling -- which we already knew from the U1 chain-grade 1-hop primitive.

### What WOULD chain-grade-confirm the consolidation mechanism?

1. **Run consolidation at the prior regime** (single fixed predicate-pair p1=0 p2=1, n_chains=200, K_SET=20). If NAIVE reproduces 0.65 +/- 0.02 AND CONS_IMMEDIATE >= 0.95, that is apples-to-apples and a real Barrier 1 closer.
2. **Capacity sweep**: hold predicate-pair distribution but vary n_chains across {100, 300, 1000, 3000, 10000}. At what M/N do CONS_IMMEDIATE and NAIVE diverge MEASURABLY? If CONS_IMMEDIATE stays at 1.000 only when M << N capacity, that confirms by-construction.
3. **Held-out chain test**: train W on n_chains_train chains, then test on n_chains_held-out NEW chains whose (p1, p2) frequencies are NOT visible to consolidation at train time. If CONS_IMMEDIATE drops to NAIVE on held-out chains, the gain is "stored the answer" not "learned to consolidate".

### Atom
- Path: `data/substrate_index/math/audit.jsonl` append + `data/substrate_index/meta/cert_ledger.jsonl` row
- atom_id: `math::T3/EXP_substrate_multihop_consolidation_memory_v1_MM`
- cert_status: `measured_mechanism`
- cert_increment_delta: 0
- cert_class: `mechanism_characterization_by_construction_saturation_consolidate_immediate_stores_answer_as_1hop_atom_apples_to_oranges_regime`

## Meta-rules to atomize (META corpus, CERT-neutral)

- META_M4 (proposed): "Consolidation arms with K_THRESH=1 that write the test-answer-tuple directly into W are by-construction-saturated; cannot be chain-grade for the source-barrier they claim to close. Discriminator: held-out chains whose (R1,R2) frequencies are NOT visible at consolidation time."
- META_M5 (proposed): "Cross-cell baseline comparisons require chain-construction match, not just V/N match. `make_chains(fixed_p1_p2)` and `make_chains(uniform_p1_p2)` produce DIFFERENT NAIVE baselines at the same (V_C, V_P, N, K_SET)."

## Significance for Stage 2 roadmap

User's intuition "memory primitive for multi-hop" is the right framing, but **this cell is not its cert-grade confirmation**. The right next cell is the pointer-chain hybrid (`substrate_multihop_pointer_chain_hybrid_v1` per director spec) which tests the non-compositional escape hatch in apples-to-apples regime with the documented 0.65 baseline. The consolidation mechanism is plausible but needs the discriminating test described above (capacity sweep + held-out chains) before MEASURED_MECHANISM can be upgraded.

The MM tier does count as a directional positive: consolidation as a Squire-Wixted analog primitive is operationally implementable in substrate; the question is whether it provides lift over NAIVE in a regime where NAIVE is NOT trivially solving the problem.

## Referent pointers
- Cell 3 metrics: `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING/metrics.json` (remote: marsh@home:C:/dev/hd-instrument/...)
- Cell 3 prereg: `preregs/2026-06-25_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.md`
- Cell 3 source: `experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.py`
- Cell 3 v2 reference: `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL/metrics.json`
- Cell 4 metrics: `data/exp_substrate_multihop_consolidation_memory_v1/metrics.json` (remote)
- Cell 4 prereg: `preregs/2026-06-24_substrate_multihop_consolidation_memory_v1.md`
- Cell 4 source: `experiments/exp_substrate_multihop_consolidation_memory_v1.py`
- Cell 4 baseline reference: `data/exp_substrate_resonator_softchain_beta_sweep_v1/metrics.json` (BASELINE_HARD=0.65)
- Director spec: `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`
- Cell commit: `4ccc5df4` (Author 4 substrate-native cells Wave E retry)

## Tier ruling summary

| Cell | Tier | cert_delta | Reason |
|------|------|------------|--------|
| substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING | MEASURED_MECHANISM | 0 | A3 PRIMARY at ceiling in v2 already; A4 discriminator DEGRADED with scale; max_cv worsened 0.083 -> 0.125 |
| substrate_multihop_consolidation_memory_v1 | MEASURED_MECHANISM | 0 | CONS_IMMEDIATE writes test answer directly as 1-hop atom; NAIVE baseline 0.847 vs prior 0.65 is regime-different not methodology-fixed; HYBRID < CONS_IMMEDIATE violates prereg discriminator |

Net cert impact: 0 (no upgrades, no demotions; both new cells filed as MM characterizations).

Two new meta-rules atomized in the same ledger pass.

## Ledger rows landed (cert_ledger.jsonl ts=1782398467)

| atom_id | row_sha16 |
|---------|-----------|
| math::T3/EXP_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING_MM | b5059fd849e96356 |
| math::T3/EXP_substrate_multihop_consolidation_memory_v1_MM | 75d11ea2b5492469 |
| meta::T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated | 1504cb52f661479c |
| meta::T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match | b0aa15d695240212 |

Ledger total rows after append: 718.
