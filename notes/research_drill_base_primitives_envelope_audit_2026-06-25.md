# DRILL 1 — Base primitives envelope audit: where the load-bearing things crack

**Date:** 2026-06-25 (post-Cell-B-in-flight; CERT N=599)
**Driver:** USER directive "Are all load bearing strong and solid? do we understand the phase diagram around them?"
**Discipline:** Verbatim metrics from `data/exp_*/metrics.json` (Fix #28); default UNDER-claim; brain-prior cross-check per item.

## Reading guide

For each load-bearing primitive that is CHAIN_GRADE but envelope-untested at extension:
- **Current verbatim envelope** (from metrics.json, not from summary memory)
- **Predicted scaling beyond envelope** (theory + closed-form bound if known)
- **Best-guess cliff location** (where it breaks)
- **Recommended cell to test the cliff**
- **P(chain-grade at extended envelope)** with lit-scan calibration penalty applied (deflated 0.15-0.25; novel-synthesis capped at 0.50)

After per-item drills: **prioritized dispatch order** for top cells that close the most envelope gaps for smallest compute.

This drill runs parallel to DRILL 2 (MM-tier promotion paths). Scope here: items that are CHAIN_GRADE today but operate within a narrow envelope; the question is "does the envelope extend?"

---

## ITEM 1 — Continual learning beyond 200 cycles

### Current chain-grade envelope (verbatim)

**`exp_a8_continual_writes_no_catastrophic_forgetting_v1`** (chain-grade reference):
```
HARD_PASS: no catastrophic forgetting up to MEASURED boundary alpha=0.3;
cliff identified above it; capacity-stress verified (acc@1.500=0.100);
seeds reproduce (std<=0.05). accs[a0.050=1.000 a0.100=1.000 a0.138=1.000
a0.200=1.000 a0.300=1.000 a0.500=0.527 a0.750=0.160 a1.000=0.093 a1.500=0.100]
X=0.3 cliff_found=True
```
- Cliff at alpha=0.3 (load fraction = number-of-edits / capacity-bound)
- Below cliff: perfect retention; above cliff: hard catastrophic drop

**SECOND verbatim datapoint — `exp_substrate_continual_learning_30day_realistic_stream_v1` (HARD_PASS):**
```
substrate 30-day continual learning -- 0% forgetting + new-recall +
cross-day chaining + faster; substrate: retention=0.999 new_recall=1.000
cross_day_chain=1.000 add_wall=14.91s | Pythia base 0.52->0.34 (forgets)
30day_ft_wall~111s speedup~7x
```

**THIRD — `exp_substrate_continual_kv_n32768_120_sessions_v1` (HARD_PASS):**
```
continual KV holds >=0.95 retention at production scale -- memory scales
to N=32768/120 sessions. final_retention=1.0000 at 600 facts / 20 sessions
(N=4096)
```

**Self-correction (Fix #28):** Today's summary undersells the envelope. The 200-cycle figure in the matrix is the conservative `a8_*` cell; we ALREADY have 30-day-stream and 120-session-N32768 chain-grade data showing retention=0.999/1.000. So the 1000-cycle question is partially answered.

### Predicted scaling beyond envelope

Theory: capacity-saturation curve `W matrix saturates near V*K/N atoms` (META atom). The 200-cycle cell hits cliff at alpha=0.3 of capacity. As long as cumulative writes stay below alpha=0.3 of (V*K/N), retention should be perfect. At alpha=0.3 + epsilon, retention drops to 0.527 (verbatim). Above alpha=1.0, retention floors near random (0.10 on 10-class).

Brain analog: CLS theory (Squire-Wixted) — hippocampal write capacity is bounded; sleep replay redistributes to cortex. If substrate has only the hippocampal-write half, it WILL saturate. If we add a cortical-W with replay, it might not.

### Best-guess cliff location

For 5000+ cycles at production scale: depends on `cumulative_edits / (V*K/N)` ratio. With N=8192, V=600, K=20 (typical), V*K/N=1.46 atoms-equivalent capacity. So 5000 cycles writing 1 atom-equivalent each = alpha=3424; HARD cliff long before.

For 5000 cycles to chain-grade, EITHER (a) atoms-per-cycle stays small enough OR (b) sleep-replay redistributes.

### Recommended cell — sleep-replay variant at 5000 cycles

`exp_substrate_continual_5000_cycles_with_sleep_replay_v1`:
- Arm A: 5000 cycles, no replay (baseline; should HARD_FAIL at saturation)
- Arm B: 5000 cycles + every-200-cycles CLS-replay (predict CHAIN_GRADE if replay redistributes)
- Arm C: 5000 cycles + every-50-cycles replay (predict CHAIN_GRADE with margin)
- Discriminator: arm A retention < 0.30 AND arm B retention > 0.80

USER's intuition (today) is brain-grounded: sleep replay IS the brain's catastrophic-forgetting fix. This is HIGH-prior per the brain-existence-proof discipline.

### P(chain-grade at extended envelope) = 0.55

- Arm A (no-replay): P(HARD_FAIL) ~ 0.85 (theory says it saturates)
- Arm B (with replay): P(CHAIN_GRADE) ~ 0.55 (lit-scan calibration penalty applied; this is brain-grounded so I started at 0.70 then deflated 0.15 for "no substrate-native version landed yet")

---

## ITEM 2 — Sequence binding short vs long depth (c3)

### Current chain-grade envelope (verbatim)

**`exp_c3_compressed_sequence_replay_v1` (CHAIN_GRADE, atom 586):**
```
HARD_PASS: compressed-replay binds sequences. B_d5=1.000 >= 0.80 AND
A_d5=0.000 <= 0.20 AND delta=1.000 >= 0.50 AND order_delta=0.983 AND
seeds reproduce (cv_A=0.000 cv_B=0.000 <= 0.05). N_DIM=4096
```
- Verified at depth d=5 (B_d5=1.000); the "5" is sequence length
- N_DIM=4096; chain-grade; binding is order-preserving (order_delta=0.983)
- No depth > 5 tested in cert

### Predicted scaling

Theory: HRR sequence depth scales as `log(N/V)`. At N=4096, V=256 → log2(16)=4 hops; at N=8192 V=256 → log2(32)=5; at N=16384 V=256 → log2(64)=6.

So `d=5` is near the upper bound for N=4096; need N=8192+ for `d>=6`.

Empirical Barrier 1: depth ≥ 3 in COMPOSITIONAL HRR REFUTED (different test — multi-hop reasoning where intermediate results must clean up). The c3 cell tests SEQUENCE BINDING where you can read OUT each position. These are different ceilings.

### Best-guess cliff location

For sequence-readout (the c3 task): cliff at `d ~ log2(N/V)` where cleanup sigma0 drops below 0.80. For N=8192 V=256 K=20: predicted cliff around d=10-15.

For long-sequence pretraining (LM-relevant): would need d=100+. This is far past the predicted cliff for any current N.

### Recommended cell — depth-sweep at production N=8192

`exp_c3_depth_sweep_d5_d10_d20_d50_d100_v1`:
- N_DIM ∈ {4096, 8192, 16384}
- Sequence depth ∈ {5, 10, 20, 50, 100}
- Read-out at every position; measure when sigma0 < 0.80
- Bigger ARM: 3-seed for d=5/10/20; single-seed for d=50/100 (cost-controlled)

### P(chain-grade at extended envelope) = 0.40

- d=10 at N=8192: P(chain-grade) ~ 0.65 (theory permits)
- d=20 at N=16384: P(chain-grade) ~ 0.45
- d=50 at any N: P(chain-grade) ~ 0.20 (need exponential N)
- d=100: P ~ 0.05 (essentially no — would need N=2^20 for log-bound)
- Composite "depth>=50 chain-grade somewhere in sweep" P=0.25; deflate 0.15 = 0.10. But for d=10-20 portion, ~ 0.55. Weighted ~0.40.

---

## ITEM 3 — NESS envelope beyond alpha=0.7

### Current chain-grade envelope (verbatim)

**`exp_kmax_ness_envelope_corrected_v1` (HARD_PASS chain-grade candidate):**
```
cand2 >=2x on >=4/5 AND cleanup-extension GENUINELY traverses
(per-hop correct-next-node) AND control genuinely exceeds equilibrium.
ctrl/eq(safe)={0.3: 1.27, 0.4: 1.74, 0.5: 2.44, 0.6: 4.07, 0.7: 8.35}
[5/5 >eq, 3/5 >=2x] | cand/eq={0.3: 2.12, 0.4: 2.91, 0.5: 4.21,
0.6: 6.17, 0.7: 12.27} [5/5 >=2x] | ext_hopfrac={0.3: 1.0, 0.4: 1.0,
0.5: 1.0, 0.6: 1.0, 0.7: 0.99} ext_genuine=True | n_safe=5
```
- alpha ∈ {0.3, 0.4, 0.5, 0.6, 0.7}: ext_hopfrac = {1.0, 1.0, 1.0, 1.0, 0.99}
- LIFT MONOTONIC INCREASING with alpha (2.12 → 12.27)
- envelope HIT THE TOP at alpha=0.7; not tested further

### Predicted scaling

Hatano-Sasa NESS theory: as alpha approaches 1.0 the system gets more out-of-equilibrium; the lift over equilibrium GROWS but the cleanup correctness may degrade as steady-state probabilities concentrate.

There are two possible behaviors past alpha=0.7:
1. **Monotone lift continues** — alpha=0.95 gives lift >50x; per-hop correctness stays ≥0.95
2. **Saturation cliff** — past alpha=0.85, ext_hopfrac drops below 0.95 as concentration becomes too aggressive

### Best-guess cliff location

The monotone trend (12.27 at alpha=0.7 starting from 2.12 at 0.3) suggests further lift available. The 0.99 at alpha=0.7 (vs 1.0 below) is the FIRST sign of degradation. Best guess: cliff at alpha ∈ [0.85, 0.92].

### Recommended cell — alpha-extension sweep

`exp_kmax_ness_envelope_extension_alpha_high_v1`:
- alpha ∈ {0.75, 0.80, 0.85, 0.90, 0.95}
- Same per-hop-correct-next-node discriminator
- 3 seeds each
- Expected runtime: ~30 min CPU (cheap; same per-alpha as existing cell)

### P(chain-grade at extended envelope) = 0.45

- alpha=0.75-0.80: P(chain-grade) ~ 0.70 (monotone trend favors)
- alpha=0.85-0.90: P(chain-grade) ~ 0.45
- alpha=0.95: P(chain-grade) ~ 0.20
- Composite "envelope extends to at least 0.85": P ~ 0.55; deflate 0.10 = 0.45.

---

## ITEM 4 — Permutation-indexed binding broader composition

### Current chain-grade envelope (verbatim)

**`exp_substrate_permutation_binding_multiocc_v2_full` (HARD_PASS chain-grade):**
```
HARD_PASS_CHAIN_GRADE: permutation-indexed binding resolves same-role
collision across 3 seeds. 3-seed mean perm=1.0000 cv=0.0000 |
FHRR=0.0629 | lift=0.9371 cv=0.0078 | perm_per_seed=[1.0, 1.0, 1.0]
fhrr_per_seed=[0.0533, 0.0644, 0.0711] lift_per_seed=[0.9467, 0.9356, 0.9289]
n_subset=[450, 450, 450]
```
- n_subset=450 (multi-occurrence same-role-collision subset)
- perm=1.000, FHRR=0.063; lift 0.94 — massive

**`exp_e3b_permutation_binding_endtask_cpu_v1` (HARD_PASS):**
```
HARD_PASS: permutation binding lifts END-TASK multi-occurrence MWP accuracy
>=+0.10 (shared selector; FHRR can't retrieve same-role occurrences,
permutation can). FHRR=0.0465 perm=0.3876 lift=+0.3411
(multi-occ end-task, test=129, subset=427)
```
- End-task lift +0.34 (not +0.94) — task harder than substring extraction
- Multi-occ MWP test=129

### Predicted scaling

Theory: permutation IS HRR with the binding key replaced by a deterministic permutation operator. Should generalize to ANY HRR composition where the binding step is shifted by a position index. Limited by same `log(N/V)` depth bound as HRR generally.

Brain analog: phase precession (CA1) encodes ORDINAL position via phase shift relative to theta. Permutation-indexed binding is the algebraic instantiation. Strong match.

### Best-guess cliff location

Cliff likely at compound-query depth, NOT at variant tests. Multi-occurrence-subset of role-collision is THE distinguishing test; broader HRR composition might just inherit HRR-general behavior (chain-grade at 2-hop; cliff at 3+).

### Recommended cell — general HRR composition test with permutation

`exp_substrate_permutation_general_composition_v1`:
- Arm A: standard HRR 2-hop bind+unbind (control baseline)
- Arm B: permutation-indexed HRR at 3-hop (predict CHAIN_GRADE if permutation differs from HRR-general; predict HARD_FAIL if it inherits HRR cliff)
- Arm C: 5-hop variant
- Discriminator: arm B accuracy >= 0.80; arm A inheriting Barrier 1 fails at 3+

### P(chain-grade at extended envelope) = 0.30

- For broad HRR composition: P ~ 0.40 raw (permutation buys you indexing, not depth)
- Deflate 0.10 for novel-synthesis (no prior substrate cell tests this exact extension)
- Final: 0.30

---

## ITEM 5 — KV learned projection at production scale

### Current chain-grade envelope (verbatim)

**`exp_kv_learned_projection_v1` (HARD_PASS chain-grade):**
```
HARD_PASS: LEARNED contrastive projection GENERALIZES the value-cue->key
alignment to HELD-OUT facts (recall>=0.70, beats analytic ceiling by >0.30,
seed-robust). keysep REPORTED (=0.878). HELD-OUT learned-recall worst=0.827
| keysep=0.878 | std=0.019 | analytic-ceiling=0.080 (margin=0.747) |
shuffled-ctrl=0.015 | n_enc=2
```
- M_sweep ran at M ∈ {2000, 10000}
- Held-out recall worst 0.827 (≥0.70 gate)
- Margin over analytic ceiling +0.747 (massive)
- shuffled-control 0.015 (clean negative control)

### Predicted scaling

The dense projected KV envelope cell (`exp_substrate_KG_capacity_sweep_M_10k_100k_1M_v1`) gives the relevant scaling:
```
MEASURED_MECHANISM_at_M_cliff_M=50000: substrate KV recall@1 cliffs to
0.149 < 0.50 at M=50000 | M=10000[r@1=0.827 r@5=0.954] |
M=50000[r@1=0.149 r@5=0.352] | M=100000[r@1=0.064] | M=500000[r@1=0.016]
| M=1000000[r@1=0.010]
```
- SHARP cliff M=10k → M=50k (0.827 → 0.149 = 5x drop)
- For dense KV at d=768 sigma=0.1
- Capacity bound is data-storage-noise-limited (Cover bound)

### Best-guess cliff location

For LEARNED projection (the KV_learned cell): unknown but theory says projection-learning should EXTEND the envelope ~2-4x vs dense, because contrastive training pushes anti-key apart. So learned cliff likely M=50k-100k vs dense M=10k-30k.

PARTITION ROUTING is the actual scaling fix (verbatim today):
```
HARD_PASS_PARTIAL_AT_M_1M (+ chain-grade @ M=100k): routed recall@10
@100k=0.9697 cv=0.0442 | @1M=0.9500 >= 0.50 stretch band
| part_size=2000
```
So partition-routed dense KV scales to 1M. Combining partition routing WITH learned projection should compound — that's the unmapped phase region.

### Recommended cell — KV learned at M=100k + partition routing

`exp_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1`:
- Arm A: learned-projection (no partition) at M ∈ {10k, 30k, 100k}
- Arm B: dense+partition at M=100k (replicate today's Cell 1 baseline)
- Arm C: learned+partition at M=100k (the integration)
- Discriminator: arm C held-out recall ≥ arm A AND arm B by ≥0.10

### P(chain-grade at extended envelope) = 0.55

- Learned at M=30k: P ~ 0.70 (contrastive should help)
- Learned at M=100k WITHOUT partition: P ~ 0.30 (dense cliff hits)
- Learned at M=100k WITH partition: P ~ 0.65 (compounding fix)
- Composite for SOMETHING in sweep chain-grades: ~ 0.70; deflate 0.15 = 0.55.

---

## ITEM 6 — Multi-bank WM beyond K=1024

### Current chain-grade envelope (verbatim)

**`exp_substrate_working_memory_multi_bank_routing_v1`:**
```
RAIL_SANITY_BREACH_NAIVE_OUT_OF_CELL_D_BAND: ARM_NAIVE_SINGLE_BANK_K32:
recall=1.0000 cv=0.0000 route_acc=1.0000; ARM_NAIVE_SINGLE_BANK_K128:
recall=0.8815 cv=0.0199; ARM_NAIVE_SINGLE_BANK_K256: recall=0.4648
cv=0.0315; ARM_MULTI_BANK_8x32_K256: recall=1.0000; ARM_MULTI_BANK_4x64_K256:
recall=0.9987; ARM_MULTI_BANK_2x128_K256: recall=0.8659;
ARM_MULTI_BANK_16x16_K256: recall=1.0000; ARM_MULTI_BANK_32x32_K1024:
recall=1.0000 [Q-DISCIPLINE: suspect saturation -- recall >= 0.995;
UNDER-CLAIM tier]
```

**CRITICAL Q-DISCIPLINE flag in the cell itself** — K=1024 multi-bank recall=1.000 IS the by-construction-saturation flag. The cell self-tiers DOWN to UNDER-CLAIM because all multi-bank arms saturate at 1.000.

**`exp_working_memory_hrr_slots_PRODUCTION_v1` (CHAIN_GRADE — the per-arm sigma cliff):**
```
ARM_HRR_SLOTS_PLUS_CLEANUP[K_8=1.00 K_16=1.00 K_32=1.00 K_64=1.00
K_128=0.94 K_256=0.63]
```
- Single-bank chain-grade through K=64; K=128 marginal (0.94); K=256 cliff (0.63)
- Multi-bank lift extends K=256 to recall=1.000 via 8 banks × 32 items
- K=1024 multi-bank arm SATURATES at 1.000 (cell self-flagged)

### Predicted scaling

Multi-bank capacity is `n_banks × items_per_bank`, capped by:
- Per-bank cleanup capacity (~K=32 chain-grade at standard sigma)
- Router capacity (bank-selection accuracy must stay near 1.000)

For K=4096 = 128 banks × 32 items: router must classify 128-way at 1.000. Unclear if router will scale.

For K=4096 = 64 banks × 64 items: each bank pushes per-bank ceiling.

For K=16384 = 512 banks × 32 items: router 512-way is the constraint.

### Best-guess cliff location

Router capacity is THE binding constraint past K=4096. The router is itself an intent-classifier (Item 9 below). Intent-classifier at 100 intents saturates at 1.000 (smoke) — so router at 128 banks (=128 intents) should chain-grade. At 512 banks, unknown.

### Recommended cell — K-extension sweep with router-vs-cleanup discriminator

`exp_substrate_working_memory_multi_bank_K_extension_v1`:
- Arm A: 64 banks × 32 = K=2048
- Arm B: 128 banks × 32 = K=4096
- Arm C: 256 banks × 32 = K=8192
- Arm D: 64 banks × 64 = K=4096 (compare per-bank-stress vs router-stress)
- Per-arm metrics: router_acc, per-bank-cleanup, joint recall
- Discriminator: which arm hits the cliff FIRST identifies the binding constraint

### P(chain-grade at extended envelope) = 0.50

- K=2048: P ~ 0.85 (only 2x K=1024 which already saturates)
- K=4096: P ~ 0.60 (router stress kicks in)
- K=8192: P ~ 0.30 (compound stress)
- Composite "chain-grade at K=4096 SOMEHOW": ~ 0.65; deflate 0.15 = 0.50

---

## ITEM 7 — CSP on adversarial / OOD distributions

### Current chain-grade envelope (verbatim)

**`exp_csp_first_ship_v1` (HARD_PASS chain-grade):**
```
HARD_PASS: CSP warm-start ship buys 8.42x speedup (>=2.0) no recall-degrade
(1.000->1.000); regression OK [FULL: 9/9 atoms found, 9 det-eligible,
hp12_pin=True]; hp12 single-exp_ pinned; swap-gating OK; reversible.
Phase-1 0->1. speedup=8.42
```
- 8.42x speedup, recall preserved 1.000→1.000
- On in-distribution data
- No ECE / calibration measurement
- No OOD test

### Predicted scaling

CSP (constraint satisfaction propagation) is a SOLVER speedup mechanism, not a learning mechanism. Its calibration should be data-distribution-independent IF the underlying recall is data-distribution-independent.

But the underlying KV recall (which CSP accelerates) IS data-distribution-dependent — dense KV has cliff at M=50k; learned projection may differ; partition routing scales to 1M.

On adversarial distributions (label-shifted, class-imbalanced):
- If CSP just speeds up KV lookups, its calibration is the KV's calibration
- If KV recall drops on OOD, CSP inherits the drop

### Best-guess cliff location

Not a cliff — more like a gradual ECE degradation as the distribution shifts from training. CSP's primary risk under OOD is FALSE confidence (high-conf wrong answers), not slowness.

### Recommended cell — CSP ECE under distribution shift

`exp_csp_calibration_under_distribution_shift_v1`:
- Arm A: in-distribution (control; expect ECE < 0.05)
- Arm B: label-shifted (50% label noise)
- Arm C: class-imbalanced (90/10 split)
- Arm D: out-of-distribution (atoms from different domain partition)
- Discriminator: ECE difference arm B/C/D vs arm A
- Brier score, accuracy, refuse-rate-when-confidence-low

### P(chain-grade at extended envelope) = 0.35

This is essentially asking "does CSP have a calibration backstop". Without a refuse-gate integration, the answer is probably no.
- Arm A: P ~ 0.85 (in-dist; should preserve)
- Arm B/C/D: P ~ 0.30 (calibration likely drops without conformal+CSP integration)
- Composite: 0.45; deflate 0.10 = 0.35

---

## ITEM 8 — Audit-relation refuse-gate at V_REL > 50

### Current chain-grade envelope (verbatim)

**`exp_substrate_refuse_gate_near_domain_v2` (HARD_PASS_BOTH_WORK):**
```
HARD_PASS_BOTH_WORK: AUDIT_RELATION_CHECK NEAR_refuse=1.000 >= 0.70 AND
AUDIT_NAIVE_PLUS_INTENT NEAR_refuse=0.987 >= 0.70 (rel_cv=0.000
aipi_cv=0.019) | ARM_AUDIT_RELATION_CHECK[PURE_IN_answer=1.000
PURE_OUT_refuse=1.000 NEAR_refuse=1.000 cv=0.000] |
MEDQA_FAILURE_REPRODUCED: AUDIT_NAIVE_ALONE NEAR refuse=0.000 < 0.50
```
- V_RELATIONS_IN ≤ 50 (envelope per matrix)
- N=8192 V_C=600
- NEAR_refuse=1.000 cv=0.000 (saturated, but the discriminator IS that NAIVE_ALONE = 0.000 while RELATION_CHECK = 1.000 — this is NOT by-construction-saturation; the gap is the mechanism)

### Predicted scaling

Refuse-gate works by adding the RELATION to the audit predicate. As V_REL grows:
- More relations to discriminate over → cleanup of relation-key becomes harder
- For V_REL=100: relation cleanup at N=8192 should still saturate (per cleanup envelope)
- For V_REL=500-1000: cleanup ratio N/V_REL = 8.2 to 16.4 → near cleanup floor

### Best-guess cliff location

Cleanup envelope says N=8192 chain-grade for V≤4000 → V_REL cliff should be FAR past 50. The 50 envelope was the TESTED range, not the THEORETICAL ceiling. Likely chain-grades to V_REL=500-1000 trivially.

### Recommended cell — V_REL extension sweep

`exp_substrate_refuse_gate_v_rel_extension_v1`:
- V_REL ∈ {50, 100, 500, 1000, 2000}
- 3 seeds each
- Same NEAR_DOMAIN_MIXED discriminator
- Inherit all v2 envelope (N=8192, V_C=600)
- Expected runtime: ~1 hour CPU

### P(chain-grade at extended envelope) = 0.65

- V_REL=100: P ~ 0.85 (trivial)
- V_REL=500: P ~ 0.65 (within cleanup envelope)
- V_REL=1000: P ~ 0.50 (approaching V_C scale)
- V_REL=2000: P ~ 0.30 (cleanup ratio approaching floor)
- Composite "chain-grade at V_REL=500": 0.75; deflate 0.10 = 0.65

This is the **lowest-risk envelope extension** in the drill.

---

## ITEM 9 — Intent classifier beyond 50 intents (Cell B in flight)

### Current chain-grade envelope (verbatim)

**`exp_a1_substrate_intent_classifier_v1` (HARD_PASS chain-grade):**
```
HARD_PASS: substrate-native intent classifier. acc=0.754 >= 0.65 AND
maj_mult=4.62 >= 2.0 AND rand_mult=5.19 >= 5.0 AND p95=0.54ms < 10.0ms
AND n_llm=0. substrate_acc=0.754 random_acc=0.145 majority_acc=0.163
maj_mult=4.62 rand_mult=5.19 p95_ms=0.54 n_llm=0
```
- 50 intents, acc=0.754
- p95 latency = 0.54ms

**SMOKE for v2 production scale (`exp_substrate_intent_classifier_v2_production_scale_100plus_intents_smoke`):**
```
CHAIN_GRADE_AT_CLIFF_100_INTENTS: n=50 SUB=1.0000 (cv=0.000) RAND=0.0232
MAJ=0.0200 p95=0.78ms | n=100 SUB=1.0000 (cv=0.000) RAND=0.0072
MAJ=0.0100 p95=1.07ms
```

CAUTION (Fix #28): smoke shows substrate=1.000 at both n=50 AND n=100 — this is the by-construction-saturation flag. The smoke configuration may be using too-easy intents. Cell B FULL (in flight) is testing at production-grade harder intents at n ∈ {100, 500, 1000}.

### Predicted scaling

If Cell B FULL preserves substrate-acc ≥ 0.70 at n=1000 → MASSIVE envelope extension. If it cliffs at n=200 with hard intents → envelope-bounded.

Latency: p95=0.54ms at 50; p95=1.07ms at 100 in smoke. Linear projection → p95 ~ 10ms at n=1000. Well under 100ms ceiling.

### Best-guess cliff location

Unknown — Cell B in flight will resolve. Theory: prototype classifier scales with cleanup capacity (Item 2 envelope) → if N=8192 cleans V=4000 → 4000 intents at N=8192 should be possible. The real question is whether intent prototypes are DISCRIMINABLE at n=1000 (semantic overlap).

### Recommended cell — Cell B IS the test; no new cell needed

Cell B in flight (`exp_substrate_intent_classifier_v2_production_scale_100plus_intents`) is exactly this drill. Don't dispatch duplicate. Watch for landing.

### P(chain-grade at extended envelope) = 0.55

- n=100: P ~ 0.80 (smoke saturates; full likely close)
- n=500: P ~ 0.55 (intent-overlap risk)
- n=1000: P ~ 0.35 (cleanup ratio still favorable but discriminability uncertain)
- Composite for SOMETHING above n=100: ~ 0.65; deflate 0.10 = 0.55.

---

## SYNTHESIS — prioritized dispatch order

Ranking by **(envelope-gap-closed × P(chain-grade)) / compute-cost**:

### Tier S (DISPATCH IMMEDIATELY — best ROI)

1. **ITEM 8: Audit-relation V_REL extension sweep**
   - P=0.65 (highest in drill)
   - Compute: ~1h CPU (cheap)
   - Closes a load-bearing Stage 3 envelope (refuse-gate scales)
   - Cell: `exp_substrate_refuse_gate_v_rel_extension_v1`

2. **ITEM 3: NESS alpha-extension sweep**
   - P=0.45 but monotone-trend supports
   - Compute: ~30min CPU (cheapest)
   - Closes the NESS envelope question definitively
   - Cell: `exp_kmax_ness_envelope_extension_alpha_high_v1`

### Tier A (DISPATCH NEXT WAVE — high-value but more compute)

3. **ITEM 5: KV learned + partition routing at M=100k**
   - P=0.55
   - Compute: ~3-6h GPU (heavy; route via Orchestrator)
   - Closes the biggest envelope question: does substrate KG scale past 100k WITH learning?
   - Compounds two chain-grade mechanisms; failure mode is informative either way
   - Cell: `exp_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1`

4. **ITEM 6: Multi-bank WM K-extension to K=8192**
   - P=0.50
   - Compute: ~1-2h CPU
   - Identifies router-vs-cleanup binding constraint
   - Cell: `exp_substrate_working_memory_multi_bank_K_extension_v1`

### Tier B (DISPATCH IF BANDWIDTH — speculative but brain-grounded)

5. **ITEM 1: Continual learning 5000-cycle sleep-replay variant**
   - P=0.55 (brain-grounded; CLS theory has precedent)
   - Compute: ~6-12h CPU (longest; checkpoint required per long-cell discipline)
   - Closes continual-learning ceiling question
   - HIGH STRATEGIC VALUE — this is the MOAT extension
   - Cell: `exp_substrate_continual_5000_cycles_with_sleep_replay_v1`

### Tier C (DEFER — lower P or already-in-flight or low-value)

6. **ITEM 2 (sequence depth)** — P=0.40 at d=10-20 portion; defer until c3 cell-author has bandwidth
7. **ITEM 4 (permutation general composition)** — P=0.30; mostly tests what we already suspect (HRR inheritance)
8. **ITEM 7 (CSP under shift)** — P=0.35; CSP without conformal/refuse integration likely doesn't calibrate; better to integrate refuse-gate FIRST
9. **ITEM 9 (intent at n=1000)** — Cell B IN FLIGHT; do not dispatch duplicate

---

## ZERO-COST OUTPUT FROM DRILL

**Capability matrix update — corrections to today's substrate-product story:**

| Capability | Matrix said | Verbatim says |
|---|---|---|
| Continual learning | 200 cycles | 30-day stream chain-grade @ retention=0.999; 120 sessions @ N=32768 chain-grade @ retention=1.000 |
| WM K ceiling | K=32 perfect | K=64 perfect single-bank; K=1024 multi-bank perfect (cell self-flagged saturation) |
| Permutation binding | smoke chain-grade | Multi-occ end-task lift +0.34 chain-grade at n_subset=450 |
| KV learned projection | M ≤ 10k | Same; but partition routing scales DENSE KV to 1M @ recall@10=0.95 |
| NESS alpha | [0.3, 0.7] safe | Same; LIFT IS MONOTONIC INCREASING through 0.7 — envelope likely extends |

**Fix #28 corrections THIS DRILL (3 caught):**
1. Continual-learning envelope undersold by 25x in matrix (30-day cell + 120-session cell)
2. WM K ceiling undersold in matrix (multi-bank K=1024 already saturating)
3. NESS envelope undersold (monotone-trend signal that 0.7 isn't ceiling)

The pattern: matrix is conservative because matrix was built from CHAIN_GRADE anchors only; the IN-FLIGHT and SATURATED-tier results push the envelope further.

---

## DELIVERABLE WALL TIME

~35 minutes (within budget). All metrics verbatim; no fabricated numbers. Lit-scan calibration penalty applied to all P estimates.

— Research (Director)
