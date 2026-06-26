# Skunkworks tier ruling -- 5-artifact late-dispatch wave (3 cells + 1 routing + 2 META)

Date: 2026-06-25 (late evening; UTC 2026-06-26T~02:30Z)
Auditor: skunkworks (audit-only; A5-gated atomization; spawn-and-die teammate)
Method: independent recompute off `metrics.json` per_seed + per_M (NOT verdict_msg framing);
smoke metrics independently verified where artifacts present; existing META atom + Store
state cross-checked off `data/substrate_index/`.

## Headline (read first)

CERT N: 599 -> 600 (+1 from Artifact 2 chain-grade only). Total atoms: +6 (math: +4, meta: +2).

| # | Artifact | Tier ruling | Delta | Sub-class |
|---|---|---|---|---|
| 1 | anisotropy rescue v2 calibrated meter | **MEASURED_MECHANISM** (Q-discipline saturation override of Director's chain-grade-candidate) | 0 | mechanism_characterization |
| 2 | hierarchical 2-level partition routing M=10M | **CHAIN_GRADE** (inherits Cell 1 caveat-class) | +1 | pre_reg_pass |
| 3 | CSP-gated iterated cleanup v1 | **HARD_FAIL / honest_negative** (4th Barrier-1 attempt) | 0 | pre_reg_miss_proven_bound |
| 4 | WM K-extension cleanup-per-slot v2 | **HARD_FAIL / honest_negative** (strict pre-reg override of cell's MIDDLE_BAND tag) | 0 | pre_reg_miss_proven_bound |
| 5a | META_BARRIER_1_QUADRUPLE_NEGATIVE | meta_rule / discipline_meta (extends TRIPLE; does NOT supersede) | 0 | discipline_meta |
| 5b | META_M7 smoke regime-match | meta_rule / discipline_meta (atomizes the prior-deferred candidate per better-framing) | 0 | discipline_meta |

Key Skunkworks correctness overrides this batch (per recurring pattern):
- **Artifact 1 (override Director chain-grade-candidate -> MM):** 4/4 working arms at >=0.995 hits cell's own Q_SUSPECT_SATURATION=0.995 band; cannot discriminate WHICH rescue mechanism is load-bearing at M=10k corpus regime. 55x rescue (0.018 -> 0.997) IS measured; MM tier is honest.
- **Artifact 4 (override cell's MIDDLE_BAND -> HARD_FAIL):** load-bearing pre-reg claim was "cleanup-per-slot extends K-ceiling"; K-ceiling UNCHANGED at 64 for both arms; +0.014 K128 lift below noise floor cv=0.012. Honest_negative on the pre-reg bar.

## Verify-off-data table (every cited metric independently recomputed)

### Artifact 1 -- anisotropy rescue v2 (per_unit[seeds].by_M["M10000"])

| arm | seed 11 | seed 13 | seed 19 | mean | cv | metric.json verdict cite |
|---|---|---|---|---|---|---|
| arm1_raw | 0.0187 | 0.0173 | 0.018 | **0.0180** | 0.041 | raw=0.018 OK |
| arm_A_cerebellar_K5 | 0.0507 | 0.0573 | 0.0467 | **0.0516** | 0.103 | A=0.051 OK |
| arm_Ap_dense_5x | 0.062 | 0.0627 | 0.0607 | **0.0618** | 0.017 | Ap=0.062 OK |
| arm_B_fly_lsh | 0.998 | 0.9967 | 0.9967 | **0.9971** | 0.001 | Bfly=0.997 OK |
| arm_B_charikar | 1.0 | 1.0 | 1.0 | **1.0000** | 0.000 | Bchar=1.000 OK |
| arm_C_compose | 0.996 | 0.996 | 0.996 | **0.9960** | 0.000 | C=0.996 OK |
| arm_D_meter | 1.0 | 1.0 | 1.0 | **1.0000** | 0.000 | D=1.000 OK |

Per-arm rescue factors (relative to raw=0.018):
- arm_A_cerebellar_K5: 2.86x (insufficient at expand5x; cerebellum uses 1000x)
- arm_B_fly_lsh: **55.4x** (load-bearing rescue magnitude)
- arm_B_charikar: 55.6x
- arm_C_compose: 55.3x
- arm_D_meter: 55.6x

**Q-discipline saturation analysis:** 4 of 4 working arms at >= 0.995. Cell's OWN bands metadata: `Q_SAT=0.995`. All 4 fired. Per by-construction-saturation tiering (Skunkworks-correctly-overrides-Director MEMORY rule 2026-06-23), default classification is MM not chain-grade when arms saturate equivalently. Discriminator-gap regime (M=100k adversarial-similarity keys) is required for chain-grade-confirmed promotion.

### Artifact 2 -- hierarchical 2-level routing (per_seed[i].per_M[M].arm_*)

M=1M:
| arm | seed 11 | seed 13 | seed 19 | mean | cv |
|---|---|---|---|---|---|
| 2LEVEL | 0.975 | 0.975 | 0.96 | **0.9700** | 0.007 |
| SINGLE | 0.95 | 0.945 | 0.945 | **0.9467** | 0.003 |
| FLAT | 0.505 | 0.495 | 0.465 | **0.4883** | 0.035 |

M=10M:
| arm | seed 11 | seed 13 | seed 19 | mean | cv |
|---|---|---|---|---|---|
| 2LEVEL | 0.98 | 0.97 | 0.985 | **0.9783** | 0.006 |
| SINGLE | 0.96 | 0.955 | 0.975 | **0.9633** | 0.009 |
| FLAT | 0.275 | 0.305 | 0.33 | **0.3033** | 0.074 |

Routing accuracy = 1.000 across all M for both 2LEVEL and SINGLE arms (by-construction caveat, inherited from Cell 1 chain-grade tier).

Pre-reg bands evaluated:
- `HARD_PASS_M10M_2LEVEL >= 0.80`: **PASS** (0.9783; margin +0.178)
- `CHAIN_GRADE_M10M_2LEVEL >= 0.70`: **PASS** (margin +0.278)
- `HARD_PASS_CV <= 0.05`: **PASS** (cv=0.006)
- `Q_SUSPECT_SATURATION (>= 0.995)`: **NOT FIRED** (0.9783 < 0.995)

Discriminator-gap analysis: 2LEVEL/FLAT = 0.9783/0.3033 = **3.23x** at M=10M; massive separation, not by-construction-saturation territory. 2LEVEL/SINGLE = +1.5pp lift over SINGLE arm (which IS Cell 1's chain-grade architecture extended to M=10M).

### Artifact 3 -- CSP-gated multi-hop iterated cleanup (per_seed[i].arm_csp_*)

| arm | seed 7 | seed 17 | seed 23 | mean | cv |
|---|---|---|---|---|---|
| baseline_hrr_2hop | 0.605 | 0.670 | 0.675 | **0.6500** | 0.049 |
| csp_gated_2hop | 0.24 | 0.19 | 0.205 | **0.2117** | 0.099 |
| csp_gated_5hop | 0.055 | 0.025 | 0.010 | **0.0300** | 0.624 |
| csp_gated_10hop | 0.0 | 0.005 | 0.010 | **0.0050** | 0.816 |

Per-step accuracy (CSP 5HOP seed 7): `[0.535, 0.245, 0.115, 0.080, 0.055]`
Per-hop survival ratio: ~0.46 (consistent across seeds). Geometric chain-cleanup decay 0.46^5 ~ 0.020 matches observed 0.030 mean. Mechanism cleanly measures own failure; not implementation bug.

Pre-reg bands evaluated:
- `HP_2hop >= 0.80`: **FAIL** (0.2117 vs 0.80; margin -0.59)
- `HP_5hop >= 0.50`: **FAIL** (0.030 vs 0.50; margin -0.47)
- `HP_10hop >= 0.20`: **FAIL** (0.005 vs 0.20; margin -0.195)
- `HF_5hop < 0.20`: **FIRED** (0.030 below floor; mechanism HURTS)
- baseline sanity [0.62, 0.68]: 1/3 BREACH (seed 7 = 0.605 below)
- Mid-tier `mid_5hop = [0.20, 0.30]`: 0.030 below mid-band

Mechanism HURTS at 2hop (baseline 0.65 -> CSP 0.21; absolute loss -0.44). All pre-reg HP bars missed by concrete margin; HF floor fired. honest_negative / pre_reg_miss_proven_bound is correct subclass.

### Artifact 4 -- WM K-extension cleanup-per-slot (per_seed[i].by_arm[ARM].per_K_per_sigma)

| K | sigma | NAIVE (mean over 11/13/19) | CLEANUP (mean over 11/13/19) | cleanup - naive |
|---|---|---|---|---|
| 32 | 1.0 | 1.0000 | 1.0000 | 0.0000 |
| 64 | 1.0 | 1.0000 | 0.9987 | -0.0013 |
| 128 | 1.0 | 0.9076 | 0.9219 | +0.0143 |
| 256 | 1.0 | 0.5547 | 0.5560 | +0.0013 |
| 512 | 1.0 | 0.2331 | 0.2389 | +0.0058 |

K-ceiling (>=0.95 at sigma=1.0): NAIVE=64, CLEANUP=64 (**SAME**)

Pre-reg bands evaluated:
- `HP_CLEANUP_K128_SIGMA10 >= 0.95`: **FAIL** (0.9219 vs 0.95; margin -0.028)
- `HP_cv <= 0.07`: PASS (cv=0.012)
- `HF_cleanup <= naive`: NOT fired (cleanup marginally beats naive at K128)

Override of cell's internal MIDDLE_BAND tag: the load-bearing pre-reg claim is "cleanup-per-slot extends K-ceiling" (per cell prereg framing and DESIGN_NOTE: "theta-gamma WM refresh"). K-ceiling UNCHANGED at 64. The +0.0143 lift at K128 is within noise of cv=0.012. Cell's MIDDLE_BAND tag captures "cleanup in [0.80, 0.95]" but the PRE-REG BAR was 0.95 + ceiling extension; both load-bearing claims missed. Per cert-owner strict pre-reg interpretation: honest_negative.

### Artifact 5b -- META_M7 evidence (off-data smoke + full reads)

Direct verification of smoke-vs-full sign-flip on the 2 cells with preserved smoke artifacts:

(1) pointer-chain hybrid v2 (`exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_smoke` + full):
- smoke summary: `HARD_PASS_BREAK_CEILING: BASELINE=0.6450 POINTER_2HOP=0.9800 POINTER_5HOP=0.78`
- full summary: `HARD_FAIL_POINTER_NO_LIFT: POINTER_2HOP=0.4250 POINTER_5HOP=0.1217`
- Loss: 5HOP -0.658 absolute; 2HOP -0.555 absolute. 3 dimensions reduced (N: 8192->2048; pointer_n_chains: 200->50; n_seeds: 3->1).

(2) CSP-gated iterated cleanup v1 (`exp_substrate_multihop_csp_gated_iterated_cleanup_v1_smoke` + full):
- smoke per_seed[7].arm_csp_gated_iter_5hop.top1 = 0.62
- full mean csp_gated_5hop = 0.0300
- Loss: -0.590 absolute. 4 dimensions reduced (N: 8192->2048; csp_n_chains: 200->50; max_depth: 10->5; n_seeds: 3->1).

(3) WM-scaffold v1 (`exp_substrate_multihop_wm_scaffolded_v1`): full WM_5HOP=0.122; the Director-cited smoke=0.78 cannot be independently re-verified off-data because no standalone smoke metrics.json dir exists for this cell. Logged as SUPPORTING-INDIRECT evidence only per Fix #28 default under-claim.

Why M7 atomized now (vs prior DEFER): broader framing is now load-bearing (capacity-sensitive dimensions generally, not n_chains specifically). 2 directly-verified instances meet the BIAS-14 threshold for META atomization; 1 supporting-indirect strengthens but is honestly tagged as such.

## Cross-cell composition observations (per Director request)

### If Artifact 1 had promoted to chain-grade-confirmed
The proposed multi-path KG retrieval composition (dense KV + partition routing + LSH-fanout rescue + hierarchical 2-level) would have been chain-grade. Per the Q-discipline saturation override, Artifact 1 is MM-tier this batch; the composition path is QUEUED-PENDING the M=100k adversarial-similarity discriminating-regime follow-up. Capability gain is bounded but real at M=10k; promotion regime is well-defined.

### Artifact 3 + 4 + prior 3 multi-hop HARD_FAILs -> META_BARRIER_1_QUADRUPLE
This composition LANDED (Artifact 5a). The existing META_BARRIER_1_TRIPLE atom is preserved as the 3-instance evidence-trail; the new QUADRUPLE atom adds CSP-gated as the 4th independent attempt and strengthens the substrate-product-permanent positioning. Both atoms remain in Store and cross-reference each other.

### Artifact 5b META_M7 + prior META_M2 + M5 + M6 -> 4-rule rail-discipline set
- M2: rail tolerance must match referent config OR widen by capacity drift
- M5: cross-cell baseline comparisons require chain-construction match
- M6: NAIVE-baseline must be DERIVED from current-cell regime parameters, NOT copied
- M7: smoke regime must match full along EVERY capacity-sensitive dimension

The 4-rule set is the canonical rail-derivation-provenance-regime-match discipline for any cell author + landed-VET pass.

## Concerns considered and rejected

### Artifact 1 -- "why not chain-grade-candidate as Director proposed?"

Director's default was chain-grade-candidate with "needs M=100k adversarial follow-up" caveat. Per by-construction-saturation tiering, when cell's own Q_SUSPECT_SATURATION band fires for 4/4 working arms, the cert-owner default is MM not chain-grade. The 55x rescue magnitude IS measured and is the cert-claim; the chain-grade VS MM distinction is about WHICH mechanism is load-bearing among the 4 saturating arms. At M=10k the answer is "can't tell"; chain-grade-confirmed requires the discriminator. This is the same pattern as g1 generation cell (USER 2026-06-22 directly endorsed Skunkworks-overrides-Director on by-construction-saturation; MEMORY rule).

### Artifact 2 -- "is the by-construction routing accuracy a saturation issue?"

Cell 1 (single-level partition routing at M=1M) was tiered chain-grade despite same caveat. Artifact 2 inherits exactly that caveat-class with consistent evidence pattern (3.2x discriminator gap, tight cv, +1.5pp lift over Cell 1's architecture). The mechanism is honest because partition-id is realistic in many KG settings; the by-construction caveat documents the boundary, not a fraud. If we were to retract chain-grade here, we'd need to retract Cell 1 too -- and there's no fresh evidence to support that.

### Artifact 4 -- "is cell's MIDDLE_BAND tag enough? Why override to HARD_FAIL?"

Cell's MIDDLE_BAND captures the cosmetic fact that CLEANUP @ K128 sits in [0.80, 0.95]. But the load-bearing pre-reg CLAIM was "cleanup-per-slot extends K-ceiling" (per DESIGN_NOTE: "theta-gamma WM refresh"). K-ceiling = 64 for BOTH arms; the claim is REFUTED. Per cert-owner strict pre-reg interpretation, the right tier is HARD_FAIL / honest_negative (proven NEGATIVE bound) -- the cell measures what it claims to measure and the answer is "mechanism does NOT extend the K-ceiling". This is in line with the cert-owner's recurring pattern of strict pre-reg interpretation vs cell's softer self-tag.

### META_M7 -- "is WM-scaffold smoke evidence too weak?"

The Director's claim "WM_5HOP smoke=0.78 -> full=0.122" cannot be independently verified off-data because no standalone smoke metrics.json artifact exists for WM-scaffold. Per Fix #28 default under-claim, WM-scaffold is tagged SUPPORTING-INDIRECT in the META metadata (NOT counted in the 2-direct instances). The META atom is supported by pointer-chain v2 + CSP-gated v1 alone; WM-scaffold strengthens but does not change the count. This is honest cert-trail accounting.

## Cert-N impact (per ledger-delta-sum convention)

| atom | cert_status | delta | CERT_N after |
|---|---|---|---|
| anisotropy rescue v2 MM | measured_mechanism | 0 | 599 |
| hierarchical 2-level routing | chain_grade | +1 | **600** |
| CSP-gated HARD_FAIL | honest_negative | 0 | 600 |
| WM K-extension HARD_FAIL | honest_negative | 0 | 600 |
| META_BARRIER_1_QUADRUPLE | meta_rule | 0 | 600 |
| META_M7 smoke regime-match | meta_rule | 0 | 600 |

**CERT_N: 599 -> 600 (+1 delta). Total atoms: +6 (math: +4; meta: +2).**

## Disciplines honored this spawn

- Verify-OFF-DATA: every cited metric independently recomputed from per_seed / per_M / per_arm in `metrics.json`
- Verify-the-referent: smoke metrics independently read where artifacts present (pointer-chain v2 + CSP-gated v1); WM-scaffold smoke flagged as SUPPORTING-INDIRECT only
- Q-discipline saturation: Artifact 1 4/4 arms at >=0.995 triggers cell's OWN Q_SUSPECT_SATURATION band -> MM override of Director chain-grade-candidate
- Fix #28 default UNDER-claim: WM-scaffold smoke flagged as not-directly-verified
- by-construction-saturation tiering (Skunkworks-overrides-Director pattern): Artifact 1 demoted from chain-grade-candidate to MM
- A5-gated atomize: PRE snapshot (CERT_N=599, axiom=206, cap_pres 6/6) + atomic add_atom per atom + fresh-Store round-trip + POST snapshot (CERT_N=600, axiom=206, cap_pres 6/6)
- cert_ledger A5 PRE/POST gates per-row (CERT_N delta verified for chain-grade atom)
- Idempotency: atomize tool aborts if any atom_id already present; whole batch entirely-new or entirely-present
- Path-scoped commit (caller responsibility): tool + ruling note + atoms.jsonl files + cert_ledger.jsonl explicitly staged; NEVER `git add -A` / `.`
- Foreground execution (Fix #20); no subprocess pipes
- ASCII only

## Referent pointers (absolute paths)

- Atomize tool: `D:/AI/hd-instrument/tools/skunkworks_atomize_5_artifact_late_wave_2026-06-25.py`
- Ruling note (this file): `D:/AI/hd-instrument/notes/skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25.md`
- Metrics (verified off-data):
  - `D:/AI/hd-instrument/data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`
  - `D:/AI/hd-instrument/data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json`
  - `D:/AI/hd-instrument/data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1/metrics.json`
  - `D:/AI/hd-instrument/data/exp_substrate_working_memory_v2_extended_K_with_cleanup_per_slot/metrics.json`
  - `D:/AI/hd-instrument/data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_smoke/metrics.json` (META_M7 evidence)
  - `D:/AI/hd-instrument/data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1_smoke/metrics.json` (META_M7 evidence)
- Dispatch context notes (read):
  - `D:/AI/hd-instrument/notes/exp_dev_to_research_5cell_tier_A_B_batch_DISPATCHED_2026-06-25.md`
  - `D:/AI/hd-instrument/notes/exp_dev_to_research_anisotropy_rescue_4arm_v2_DISPATCHED_2026-06-25.md`
  - `D:/AI/hd-instrument/notes/research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md`
  - `D:/AI/hd-instrument/notes/research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`
  - `D:/AI/hd-instrument/notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`
- Prior tier ruling (META_M6 + DEFER for smoke-floor): `D:/AI/hd-instrument/notes/skunkworks_tier_ruling_pointer_chain_v2_plus_META_M6_2026-06-25.md`
- cert_ledger writer helper: `D:/AI/hd-instrument/tools/cert_ledger_writer.py`
- atomize-template reference: `D:/AI/hd-instrument/tools/atomize_audit_lesson_template_SAFE.py`

## For Director routing (out of this spawn's scope)

1. **Artifact 1 promotion path:** dispatch `exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1` (regime: M=100k Pythia residuals with consecutive-token stride-1 adversarial similarity; if sparse-fan-in Bfly survives and Bchar/D degrade, isolate sparse fan-in as load-bearing mechanism -> chain_grade promotion eligible). This is the canonical promotion regime for the MM tier.

2. **Cross-cell composition unlock (pending Artifact 1 promotion):** once Artifact 1 is chain-grade-confirmed, can compose with Artifact 2 hierarchical routing for a multi-path KG retrieval (sparse-LSH-rescued-encoder + partition routing + hierarchical 2-level). Cert-grade composition.

3. **META_BARRIER_1_QUADRUPLE enforcement:** Director should adopt the rebuttal-check in pre-dispatch decisions per Fix #26. Substrate-native multi-hop cells at random-bipolar isotropic regime should be refuse-dispatched unless they meet the fundamental-novelty criterion (anisotropic encoder / structured corpus / learned attention / external scaffold delegation).

4. **META_M7 enforcement:** exp_dev cell-author discipline should adopt the operational fix (match capacity-sensitive dimensions OR explicitly bound expected sign-stability OR keep n_seeds >= 3 at minimum even at smoke). This catches the suspect-1.000 smoke-pass artifact that 2 cells this week showed.

-- Skunkworks, 2026-06-25 (cert-owner / auditor; spawn-and-die teammate)
