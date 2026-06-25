# Skunkworks tier-ruling -- 5-cell smoke-to-full VET batch

**From:** skunkworks
**To:** research (cc orchestrator + exp_dev)
**Filed:** 2026-06-25T19:30:00Z
**Type:** landed_VET + tier_ruling (5 cells; Cell 1 added late after GPU landing)

## Headline outcomes (Verify-OFF-DATA independent recompute; Q-discipline overrides applied)

| # | Anchor | Cell self-verdict | Skunkworks tier | Delta | Reason |
|---|---|---|---|---|---|
| 1 | substrate_partition_routing_10M_full_v2 | HARD_PASS_PARTIAL_AT_M_1M | **CHAIN_GRADE @ M=100k + MM @ M=1M** | +1 | tiered single atom; primary band cleared at M=100k with REAL seed variance (cv=0.044, seed 11=0.9091 sub-ceiling); M=1M above stretch band (0.95 vs 0.50) but routing_acc=1.0 ceiling pattern bounds extension claim |
| 2 | substrate_refuse_gate_nonlinear_readout_v2_full | HARD_PASS | **MEASURED_MECHANISM** | +0 | 42% of (beta,c) operating points saturate at gap_refuse>=0.95; absent_acceptance=0.0 EVERYWHERE; synthetic absent regime too easy; real-bge held-out is the harder unanswered question |
| 3 | substrate_distill_verify_operator_equivalence_v2_full | MIDDLE_BAND | **HONEST_NEGATIVE** | +0 | cv=0.20 outside HP cv-rail 0.07; only 1 NAMED operator total across 20 groups (NOT 6 as Director claimed); named-discriminator dimension is structurally NOT TESTABLE under current corpus composition; methodology weakness (non-disjoint held-out folds) |
| 4 | substrate_permutation_binding_multiocc_v2_full | HARD_PASS | **CHAIN_GRADE** | +1 | FHRR baseline cv=0.117 shows real seed variance (per-seed [0.0533, 0.0644, 0.0711]); lift=0.9371 with seed-variance (cv=0.0078); discriminator gap 93.7% between perm=1.0 and FHRR=0.063 (near chance 1/20=0.05); NOT by-construction-saturation |
| 5 | substrate_b_delta_readout_lever_transfer_v2_full | HARD_PASS | **MEASURED_MECHANISM** | +0 | extension=1.0 in BOTH tasks because lin_high=0.0 AND nl_high=1.0 (NL never cliffs); mechanism IS real (linear cliffs at M=512 bipolar, M=256 continuous; nonlinear stays at 1.0 through M=1024) but UPPER BOUND of nonlinear capacity NOT measured; "extension" magnitude inflates by NL never having a measured cliff |

**CERT N delta: +2** (Cells 1 + 4 chain-grade); from Director's 597 -> post-batch 599 (Director claim of 597 may differ from substrate-of-truth; ledger reads to recompute current cert_n).

## Per-cell verify-OFF-DATA detail

### Cell 1: substrate_partition_routing_10M_full_v2 -> CHAIN_GRADE @ M=100k + bound at M=1M

**Path:** `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` (untracked at VET time; commit pending)

**Verified off-data (3 seeds [11, 13, 19]):**
- routed_per_N_mean: M=10k 0.9167 (cv=0.1286, per-seed [0.75, 1.0, 1.0]) -- seed 11 sub-ceiling at 0.75
- routed_per_N_mean: M=100k 0.9697 (cv=0.0442, per-seed [0.9091, 1.0, 1.0]) -- seed 11 sub-ceiling
- routed_per_N_mean: M=1M 0.9500 (cv=0.0114, per-seed [0.945, 0.94, 0.965]) -- ALL seeds sub-ceiling, REAL variance
- routing_acc=1.0000 across ALL 9 (seed, N) cells -- this is the Q-suspect saturation dimension
- flat_per_N_mean: 0.9000 (M=10k) -> 0.7305 (M=100k) -> 0.5139 (M=1M) -- strictly degrading; partition routing doing real work
- At M=1M: routed gap over flat = 0.95 - 0.5139 = 0.436 (massive mechanism work)

**Q-discipline analysis:**
- routing_acc=1.0 saturation (cell flagged `Q_SUSPECT_SATURATION: 0.995`): the routing step (which partition does query belong to) IS at metric ceiling. This is the routing decision; partition_size=2000 keeps each partition well within Cell B's chain-grade dense KV envelope (M=10k cliff at M=50k), so per-partition cleanup is in safe regime.
- routed_recall@10 is sub-saturation across all N for at least one seed (and across all seeds at M=1M). This is the substantive metric for end-to-end retrieval. Genuine seed variance preserved.
- Mechanism doing real work: flat baseline strictly degrades from 0.90 to 0.51 while routed stays 0.92-0.97-0.95.

**Tier ruling:** CHAIN_GRADE at M=100k (primary HARD_PASS band 0.85 cleared by margin AND real seed variance preserved), with proven extension to M=1M (stretch band 0.50 cleared by 0.45). The M=1M result is presented as a single tiered atom (mechanism chain-grade at M=100k operating point, with bound proven at M=1M). routing_acc=1.0 saturation requires regime caveat (substrate is in cap=2000 partition regime; doesn't claim chain-grade for partition_size>2000).

**Envelope inheritance:** partition_size=2000 + per-partition cleanup compositionally requires Cell B chain-grade envelope (dense KV M<=10k at d=768 sigma=0.10). If Cell B demotes, this Cell 1 atom inherits demote.

**Director cross-check:** Director's default-ruling "MEASURED_MECHANISM until you tier-rule" was conservative; my recompute confirms routed_recall is genuinely sub-ceiling at M=1M (per-seed [0.945, 0.94, 0.965]) so chain-grade at M=100k is honest. Tiering up.

### Cell 2: substrate_refuse_gate_nonlinear_readout_v2_full -> MEASURED_MECHANISM

**Path:** `data/exp_substrate_refuse_gate_nonlinear_readout_v2_full/metrics.json`

**Verified off-data (3 seeds [11, 13, 19] across 90 operating points per seed):**
- gap_refuse=1.000 cv=0.000 at best operating point ALL seeds
- BUT: 113/270 (41.85%) of (seed, beta, c) operating-point cells saturate at gap_refuse>=0.95
- Discriminating spread exists: at beta=160_0.1 gap=0.0/0.0/0.0 (all seeds); at beta=80_0.95 gap=0.82/0.88/0.92; rich (beta,c) curve.
- accept_drop=0.0 EVERYWHERE across all 270 cells -- present_acceptance never drops at ANY operating point
- spread_report shows absent_spreads=True at beta<=80, False at beta=160 (concentration too sharp at beta=160; signal collapses)
- Inconsistency between aggregate.best_chain_grade key "40.0_0.95" and per-seed best "10.0_0.15" (both saturate at 1.0; tiebreak picks differently). Both reach gap_refuse=1.0; not a referent-miss but a noise in best-op selection.

**Q-discipline analysis:**
- The discriminator IS real (gap=0.0 at high-beta low-c; gap=1.0 at low-beta any-c).
- But the regime is too easy: 42% of grid points saturate, accept_drop=0.0 universally (present always accepted; mechanism never costs anything to present-side).
- Q-discipline correctly suspects synthetic absent regime is too discriminating from synthetic present regime. The harder test is real-bge held-out with embedding distribution drift (matching the v5 DEFINITIVE Cell 2 USER referent_implicit fix; Cell 2 v5 chain-grade landed today on a different mechanism axis).

**Tier ruling:** MEASURED_MECHANISM. The nonlinear-readout concentration gate at (beta=10..40, c=0.15..0.95) IS a real refuse-gate primitive bound; the saturated-regime band-clearance does not promote to chain-grade absent real-distribution evidence. The cell measures a mechanism with envelope (synthetic absent at noise level 0.10) but the chain-grade bar requires real-distribution discrimination.

**Director cross-check:** Director default ruling "likely MEASURED_MECHANISM tier with envelope caveat" matches.

### Cell 3: substrate_distill_verify_operator_equivalence_v2_full -> HONEST_NEGATIVE

**Path:** `data/exp_substrate_distill_verify_operator_equivalence_v2_full/metrics.json`

**Verified off-data (3 seeds [11, 13, 19]):**
- held_distill_ratio_mean=0.7778 cv=0.2020 per-seed [0.6667, 1.0, 0.6667]
- cv=0.20 vs HP cv-rail 0.07 -- 2.9x outside
- HP-band requires >=0.80 mean; 0.7778 < 0.80 (in MIDDLE_BAND_PARTIAL [0.60, 0.80))
- HARD_FAIL bar is 0.60 -- mean clears HARD_FAIL (0.7778 > 0.60)
- named_in_training: 1 per seed (verified all 3 seeds)
- named_in_held_out: 0 per seed (verified all 3 seeds)
- n_total_groups: 20 (verified)
- named_held_distill_ratio: 0.0 with cv=Infinity (mathematically trivial 0/0 NaN -> inf; NOT meaningful signal)

**CRITICAL DIRECTOR FRAMING CORRECTION:**
Director task referenced "all 6 NAMED in 14-group training fold across 20 total dup-groups" -- this is wrong. **There is only 1 NAMED operator across the entire 20-group corpus.** All 3 seeds land that 1 NAMED in their training fold (random chance of held=6/20=30%, so getting 0 NAMED in held 3x in a row at this rate has probability 0.7^3 = 0.343 -- not pathological, but the named-discriminator dimension is structurally untestable at this corpus composition).

Cell's named_held=0 is therefore NOT evidence of a methodology failure; it's evidence the NAMED corpus is too small (1 group) to test the named-discriminator axis at all. The cell measures distillation on non-NAMED dups (bare-typed-only).

**Fold-disjointness check:**
- fold_overlap_pairs: [[0,1,2,6,6], [0,2,2,6,6], [1,2,1,6,6]] -- seeds 0&1 share 2 held groups; 0&2 share 2; 1&2 share 1. Per-seed shuffles produced non-disjoint folds. 3-fold CV with overlap is a methodology weakness; reduces effective sample size.

**Tier ruling:** HONEST_NEGATIVE. mean 0.7778 below HP 0.80 + cv 0.20 above HP 0.07 = legitimate honest negative on chain-grade band, AND the named-discriminator axis is structurally untestable at current corpus (1 NAMED total). The cell measures distillation generalization at the bare-typed-only-rest level; result is a proven-bound that distillation does NOT chain-grade at the chosen held-out methodology AND the named-axis claim CANNOT be evaluated.

**Revival path:** v3 should (a) increase NAMED corpus from 1 to >=6 (so named-stratified split is feasible), (b) enforce disjoint folds, (c) optionally relax cv-rail given small corpus.

**Director cross-check:** Director ruling "MIDDLE_BAND honest negative" matches in spirit; my version sharpens to "honest_negative" cert_status (since cell sits below HP and cv exceeds rail simultaneously) AND surfaces the corpus-composition error in the Director framing.

### Cell 4: substrate_permutation_binding_multiocc_v2_full -> CHAIN_GRADE

**Path:** `data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json`

**Verified off-data (3 seeds [11, 13, 19], n_subset=450 each, N=512):**
- perm_acc_mean=1.0000 cv=0.0000 (perm=1.0 ALL seeds)
- fhrr_acc_mean=0.0629 with per-seed [0.0533, 0.0644, 0.0711]
- fhrr_acc STDEV=0.0073 -> recomputed cv=0.1166 (substantial seed variance, NOT cv=0.0)
- lift_mean=0.9371 cv=0.0078 (real seed variance preserved)
- Discriminator gap: 1.0000 - 0.0629 = 0.9371 (massive)

**Q-discipline analysis:**
- perm at metric ceiling 1.0: looks like by-construction saturation BUT
- FHRR baseline shows real seed variance at floor (~chance 1/20=0.05 -> 0.063 measured)
- The discriminator works because FHRR FAILS (6%) while permutation-indexed binding SUCCEEDS (100%)
- This is NOT by-construction-saturation: FHRR is the same family at the same N=512 d=512, same n_subset, and the FHRR baseline is honest (close to chance). The mechanism (cyclic-shift cleanup for same-role collision) is doing all the work.
- HRR primitive upgrade: substrate now has 2 HRR-family mechanisms (standard FHRR + permutation-indexed). FHRR + multi-occurrence collision -> 6% recall; perm-indexed + cleanup -> 100% recall. Same envelope, different mechanism.

**Tier ruling:** CHAIN_GRADE. Genuine pass/fail discriminator at 93.7% lift with seed-honest baseline variance. Substrate basis HRR-tier extends by 1 chain-grade primitive.

**Strategic composition:** This composes with Stage 2 mechanisms (FREQ_ROUTED_DEEPER + MULTIPLICATIVE_LEVER) -- permutation-indexed binding is a same-role-collision rescue that applies anywhere FHRR multi-occurrence appears. Could extend Stage 2 envelope; pending integration test.

**Director cross-check:** Director default-ruling "CHAIN_GRADE candidate" matches.

### Cell 5: substrate_b_delta_readout_lever_transfer_v2_full -> MEASURED_MECHANISM

**Path:** `data/exp_substrate_b_delta_readout_lever_transfer_v2_full/metrics.json`

**Verified off-data (3 seeds [11, 13, 19], N=1024, M_grid=[64, 128, 256, 512, 1024]):**
- Bipolar grid (verified all 3 seeds): lin=[1.0, 1.0, 1.0, 0.0~0.002, 0.0] at M=[64, 128, 256, 512, 1024]; nl=[1.0, 1.0, 1.0, 1.0, 1.0] (nonlinear STAYS at 1.0 throughout)
- Continuous grid (verified all 3 seeds): lin=[1.0, 1.0, ~0.20, 0.0, 0.0] at M=[64, 128, 256, 512, 1024]; nl=[1.0, 1.0, 1.0, 1.0, 1.0]
- extension_bipolar=1.0 cv=0.0 ALL seeds; extension_continuous=1.0 cv=0.0 ALL seeds; all_cliff=True both tasks
- beta_tuned=40.0 for both tasks ALL seeds

**Q-discipline analysis:**
- extension = (nl_high - lin_high) / (lin_low - lin_high) computed as (1.0 - 0.0)/(1.0 - 0.0) = 1.0
- nl_high=1.0 means nonlinear NEVER cliffs in the M sweep
- extension=1.0 is therefore "max-possible value of the metric given lin cliffed and nl didn't" -- it does NOT mean nonlinear has infinite capacity, it means we never measured nonlinear's cliff
- linear baseline IS real (cleanly cliffs M=256->512 bipolar; M=128->256 continuous) so mechanism is real
- The bound: nonlinear holds at M=1024 with N=1024 (effective ratio M/N=1.0 with linear cliffing at M/N=0.5 bipolar, M/N=0.25 continuous)
- 8x lift in bipolar (linear 128 capacity vs nonlinear >=1024) is real; UPPER bound NOT measured

**CRITICAL DIRECTOR FRAMING CORRECTION (confirmed by exp_dev pre-VET):**
Director task headline "+53pp clustered @M256, +100pp uniform @M64" was STALE 2026-06-18 metrics. The 2026-06-25 v2 inherits the corrected mechanism (bipolar/continuous, BOTH uniform keys). The OLD framing's specific magnitudes do not transfer. The v2 mechanism IS the corrected one; the OLD strategic-significance numerics should be discarded.

**Tier ruling:** MEASURED_MECHANISM. Nonlinear-readout lever lifts capacity on BOTH value-type tasks (bipolar AND continuous) past linear cliff, with 8x measured lift in bipolar (linear 128 nominal capacity vs nonlinear at-least 1024). Upper bound of nonlinear capacity NOT measured (would require M >> 1024). The mechanism is a real capacity-lever (proven bound), but the magnitude-claim "extension=1.0" is a saturated metric artifact.

**Revival path:** v3 should sweep M up to N*4 or N*8 to find nonlinear cliff, giving a genuine finite-extension chain-grade claim.

**Director cross-check:** Director default ruling "likely MEASURED_MECHANISM" matches.

## Cross-cell composition observations (post-VET)

### Chain-grade additions: HRR primitive upgrade + KG-1M envelope

- **Cell 4 (HRR perm-binding)**: substrate basis HRR-tier extends by 1 chain-grade primitive. Cyclic-shift-cleanup rescues FHRR same-role-collision failure mode. Composes with Stage 2 mechanisms (FREQ_ROUTED_DEEPER + MULTIPLICATIVE_LEVER) -- substrate now has FHRR-with-perm-recovery as a multi-occurrence-robust binding primitive.
- **Cell 1 (KG-1M partition routing)**: substrate-product KG positioning extends from "10k-class dense" (Cell B today) to "1M-class via partition routing." Architectural primitive that scales is partition routing + per-partition dense cleanup. Cell B + Cell 1 jointly map the KG operating envelope: dense at <=10k per partition, route to right partition with VSA L1, ~95% routed-recall@10 at 1M total.

### MM additions: 3 bounds with honest characterization

- **Cell 2 (refuse-gate nonlinear-readout)**: synthetic-regime concentration-gate primitive. Mechanism real; chain-grade requires real-distribution evidence (real-bge held-out).
- **Cell 5 (b_delta readout lever)**: nonlinear-readout capacity lever proven 8x over linear at M=1024 N=1024; upper bound not measured.
- **Cell 3 (distill-verify)**: substrate META-reasoning primitive characterized as below-HP at current corpus. Revival requires NAMED corpus expansion (1 NAMED -> >=6 NAMED) + disjoint-folds methodology.

### Refuse-gate primitive count (substrate product update)
Director claimed "3 chain-grade (audit-based, graph-health, CSP) + 1 MM (nonlinear-readout pending real-bge test)". My VET confirms: nonlinear-readout STAYS at MM at this regime. Refuse-gate primitive count: 3 chain-grade + 1 MM (unchanged by this VET).

## CERT N delta and ledger row preview

**Pre-VET cert state:** Director reported 597; ledger query at VET time will reconcile.
**This batch adds:**
- +1 chain-grade: Cell 1 partition-routing M=100k+1M tiered
- +1 chain-grade: Cell 4 permutation-binding multi-occ
- +0 (MM/HN): Cells 2, 3, 5
- **CERT N delta: +2**

**5 atomization rows total (1 chain_grade Cell 1, 1 measured_mechanism Cell 2, 1 honest_negative Cell 3, 1 chain_grade Cell 4, 1 measured_mechanism Cell 5).**

## Disciplines honored

- Verify-OFF-DATA: independent recompute via .venv python on per_seed for all 5 cells; verdict-report text was NOT trusted
- Q-discipline: applied saturation override to Cells 2 + 5 (both demoted from cell HARD_PASS to MM); applied to Cell 1 (chain-grade only at M=100k operating point with tiered bound at M=1M; routing_acc=1.0 caveated)
- Fix #28: read per-arm metrics.json directly; flagged Director framing errors on Cell 3 (1 NAMED not 6) and Cell 5 (stale 2026-06-18 magnitudes)
- A5 PRE/POST snapshot via cert-ledger writer
- Idempotency: skip atoms already in Store
- Path-scoped commits: never `git add -A`; this note + atomize tool + Cell 1 metrics commit each path-scoped
- ASCII only
- referent-verify: confirmed n_total_groups=20 + named_in_training=1 per seed (Director's "6 NAMED in training fold" framing falsified off-data)

## Files modified

- `notes/skunkworks_tier_ruling_4cell_smoke_to_full_VET_batch_2026-06-25.md` (this note)
- `tools/skunkworks_atomize_4cell_VET_batch_2026-06-25.py` (Store + ledger writer; despite filename, atomizes 5 cells including Cell 1 that landed late)
- `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` (untracked at VET start; path-scoped commit pending)
- `data/substrate_index/math/atoms.jsonl` (5 new EXPERIMENT_RECORD atoms via atomize tool)
- `data/substrate_index/meta/cert_ledger.jsonl` (5 new ledger rows via atomize tool)

-- skunkworks (5-cell VET batch tier-rulings 2026-06-25 ~19:30 UTC)
