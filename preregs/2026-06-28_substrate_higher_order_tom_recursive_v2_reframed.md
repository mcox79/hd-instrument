# PRE-REG: substrate_higher_order_tom_recursive_v2_reframed

**Anchor:** `substrate_higher_order_tom_recursive_v2_reframed`
**Author:** exp_dev (hdi_exp_dev sub-agent), 2026-06-28
**Predecessor:** `substrate_higher_order_tom_recursive_v1` MIDDLE_BAND (flat depth profile: d2=0.673, d3=0.633, d4=0.633, d5=0.580 across 3 seeds at N=8192, N_INTERFERENCE=16)
**M3 concern:** #6 (TOM beyond Sally-Anne) — Stage 3 compositional understanding track
**Brain analog:** TPJ + mPFC recursive belief processing (Frith-Frith 2003); recursive-mentalizing requires deeper PFC engagement at higher orders.

## Diagnosis of v1 flat depth profile (test-design failure)

v1 produced d2≈d3≈d4≈d5 (variance ≈0.04 across depths). Three candidate explanations:

(a) substrate handles all depths equally well (true capability)
(b) substrate handles only depth=1; test design saturates higher depths trivially
(c) test ENTITIES are linearly independent; recursive bind/unbind chain is exact at all depths because FHRR bind/unbind is information-preserving when entities don't interfere

Per signal-shape audit: FHRR bind is invertible at zero-noise. v1 added per-level distractors AND an outer interference bank (n_interference=16), yet observed flat substrate accuracy at ~0.6 — which suggests the interference noise was **per-trial-independent** and didn't accumulate as a function of depth. Each depth-d chain encoded its OWN per-level distractors + its OWN interference bank — so depth is irrelevant to noise level.

## Reframe (v2): interference-via-INTERLEAVED-chains

v2 introduces N_chains concurrent TOM chains stored in a SINGLE substrate state. Each chain has the same depth-d nesting structure; queries target the inner-most belief.

At depth=1, N_chains chains can be stored at recall=1.000 if N_chains << capacity.
At depth=d, recursive binding compounds noise per level + per chain:
- expected SNR ~ 1 / sqrt(N_chains * f(d)) where f(d) accumulates per-level distractor mass

Predicted depth-dependent dynamics (THEORETICAL@cell-author):
- (N, N_chains, d) ≈ (8192, 10, 2) → SNR healthy → SUBSTRATE ≈ 0.95
- (N, N_chains, d) ≈ (8192, 10, 5) → SNR degrading → SUBSTRATE ≈ 0.60
- (N, N_chains, d) ≈ (8192, 10, 10) → SNR floor → SUBSTRATE ≈ 0.30
- (N, N_chains, d) ≈ (2048, 50, 4) → above-capacity → SUBSTRATE ≈ chance
- (N, N_chains, d) ≈ (16384, 1, 10) → low interference → SUBSTRATE ≈ 0.80

The test now FORCES depth-dependent dynamics by interleaving multiple chains.

## Hypothesis

Substrate's nested-HRR + cleanup primitive set produces depth-dependent recall **when interleaved with concurrent TOM chains**. The depth-cliff location follows Kanerva-style FHRR capacity scaling:
- cliff_depth ≈ log_4(N / (N_chains * V_locations))
- explicit: at fixed N_chains, deeper chains exceed binding-capacity; at fixed depth, more chains exceed superposition-capacity.

## Functional-requirement decomposition

1. Track depth-d belief chain → primitive = recursive bind (chain-grade @ parietal_v2 / kf1)
2. Decode inner-most belief → primitive = recursive unbind + cleanup attractor (chain-grade @ kf1)
3. Reject interference from N_chains-1 sibling chains → primitive = superposition + cleanup (chain-grade @ sequence_binding 586)

**Signal-shape audit (META_RULE_AP_v3):**
- recursive bind output is HRR vector → recursive unbind input is HRR vector: **SHAPE_MATCH**
- superposition output is HRR vector → cleanup input is HRR vector: **SHAPE_MATCH**
- COMPOSITION_RISK = LOW (chain-grade primitives all signal-shape compatible)

## Sweep (load-bearing)

- depth d ∈ {1, 2, 3, 4, 5, 6, 8, 10} — 8 points
- N (substrate dim) ∈ {2048, 4096, 8192, 16384} — 4 points
- N_chains (concurrent TOM chains) ∈ {1, 5, 10, 50} — 4 points
- Total grid points = 8 × 4 × 4 = **128**

## Arms (3; ARMS-MUST-DIFFER per META_RULE_AF)

1. **ARM_TOM_BIND** = full recursive bind chain (depth-d HRR; substrate mechanism)
2. **ARM_FLAT_BASELINE** = flat single-level bind (no recursion); decode attempts the d-level unwrap on a 1-level bank → noise at d>=2
3. **ARM_RANDOM** = uniform-random argmax over loc codebook (numeric chance floor)

arms-distinct SHA-256 per (d, N, N_chains) cell; bit-distinct required.

## PRE-REG bands (HARD-LOCKED at module init)

### HARD_PASS requires ALL of:
- AT LEAST 30 of 128 cells satisfy: ARM_TOM > ARM_FLAT + 0.30 AND ARM_TOM in (0.30, 0.95) — true MIDDLE_BAND discrimination
- depth-cliff observable: variance(ARM_TOM accuracy across depths) > 0.10 at >=1 (N, N_chains) combo
- positive control: at (N=8192, N_chains=1, d=1) → ARM_TOM >= 0.95 AND ARM_FLAT >= 0.95 (trivial bind sanity)
- capacity-cliff observable: ARM_TOM at (N=2048, N_chains=50, d=5) is BELOW ARM_TOM at (N=16384, N_chains=1, d=5) by >= 0.30
- arms-distinct SHA-256 passes for ALL 128 cells
- cv across seeds at any cell with mean in [0.30, 0.95] is < 0.20
- no cell ARM_TOM >= 0.999 at depth >= 3 with N_chains >= 5 (META_RULE_Q suspect-1000)
- cardinality_ok = True (>=90% of 128 * N_TRIALS * 3 arms completed)

### HARD_FAIL (any):
- **HARD_FAIL_FLAT_DEPTH_PROFILE (NEW; catches v1 bug):** for every (N, N_chains), variance(ARM_TOM across depths) < 0.05 — the v1 bug recurring
- HARD_FAIL_ARMS_IDENTICAL: TOM == FLAT bit-identical for >=10% of cells (recursion not working)
- HARD_FAIL_CARDINALITY_BREACH: completed < 90% of expected
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: >=90% of cells at >=0.99 or <=0.10 (no discrimination)
- ARM_RANDOM at positive-control point (N_chains=1, d=1) > 0.45 (pipeline broken; chance ~0.25)
- META_RULE_Q: any cell ARM_TOM >= 0.999 at d >= 3 with N_chains >= 5

### MIDDLE_BAND (anything else)

## §15 mandatory gates (5+1)

1. **Sweep alignment**: 8 depths × 4 N × 4 N_chains brackets SUB-CAPACITY regime (low N_chains + low d at high N → ARM_TOM ≈ 1.0) AND ABOVE-CAPACITY regime (high N_chains + high d at low N → ARM_TOM ≈ chance) per Kanerva FHRR capacity bound C ~ N / log(K)
2. **Discriminating bracket**: HARD_PASS requires >=30 cells in MIDDLE_BAND with ARM_TOM > ARM_FLAT by >=0.30
3. **Signal-shape audit (META_RULE_AP_v3)**: recursive bind preserves shape (bipolar/FHRR HRR); unbind at depth-d recovers d-th-deepest belief; per-cell shape verification at smoke
4. **Positive control**: at (N=8192, N_chains=1, d=1) → ARM_TOM == ARM_FLAT ≈ 1.000 (trivial bind sanity)
5. **Functional-req decomposition**: "TOM higher-order d-deep" = recursive_bind ∘ superposition_with_N_chains-1_siblings; both primitives chain-grade
6. **HARD_FAIL_FLAT_DEPTH_PROFILE diagnostic**: cell HARD_FAILs if depth-profile variance < 0.05 for ALL (N, N_chains) — that's the v1 bug recurring

## Pre-reg fields (REQUIRED for cardinality + discrimination)

- expected_n_units = 128 * N_TRIALS * 3 arms (smoke: 128 * 20 * 3 = 7680; full: 128 * 50 * 3 = 19200 per seed)
- HARD_FAIL_CARDINALITY_BREACH
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR
- HARD_FAIL_FLAT_DEPTH_PROFILE (NEW)
- HARD_FAIL_ARMS_IDENTICAL (TOM == FLAT for >=10% of cells)
- discriminator_survives_scale (smoke uses 32-cell subset at full N range incl. N=16384)
- CARDINALITY_OK
- META_RULE_AF arms-must-differ per cell
- META_RULE_AG positive control RANDOM in chance band (0.10, 0.45)
- META_RULE_AH atomic final-metrics write
- META_RULE_Q suspect-1000 guard

## Smoke gate (local CPU, 1 seed, REDUCED-GRID)

Smoke at REDUCED grid: 32 cells (4 depths × 4 N × 2 N_chains) at N_TRIALS=20.
- depths_smoke = [1, 3, 6, 10] (1=positive control, 3/6/10=cliff probe; spans full range)
- N_smoke = [2048, 4096, 8192, 16384] (full N range to honor DISCRIMINATOR-MUST-SURVIVE-SCALE)
- N_chains_smoke = [1, 10] (positive control + interference)

Smoke gates (LOCAL CPU; ~5-8 min projected):
- AT LEAST 5 cells in MIDDLE_BAND (ARM_TOM in (0.30, 0.95))
- depth-profile variance across [1, 3, 6, 10] at (N=8192, N_chains=10) is >= 0.10
- positive control: at (N=8192, N_chains=1, d=1) → ARM_TOM >= 0.90
- ARM_RANDOM in [0.10, 0.40] at chance-band check point
- arms-distinct per smoke cell

If smoke HARD_PASS at single seed: dispatch 3 chunked seeds [7, 13, 19] to local_cpu_queue.
If smoke MIDDLE_BAND or HARD_FAIL_FLAT_DEPTH_PROFILE: report + STOP (no full dispatch).
If smoke HARD_FAIL on infrastructure: report HF + atomize negative; route Research.

## Discipline anchors

- META_RULE_AC: all numbers MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ tagged
- META_RULE_AE: chunked dispatch (3 seeds; single-seed-per-cell)
- META_RULE_AF: arms-must-differ SHA-256 pre-flight per cell
- META_RULE_AG: positive-control baseline-in-band (chance ~0.25 for 4 locs)
- META_RULE_AH: atomic final metrics write (tmp + os.replace)
- META_RULE_AN: scope/scale/floor declarations
- META_RULE_AP_v3: signal-shape audit per primitive composition
- META_RULE_Q: suspect-1.000 guard at depth >= 3 with N_chains >= 5
- DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26): smoke uses full N range including N=16384
- CARDINALITY_OK pre-reg field per META_RULE_H discipline

## Capacity / CRLB floor (THEORETICAL@cell-author)

FHRR capacity bound (Kanerva 2009; Plate 1995): N-dim FHRR substrate stores K bound pairs at SNR ~ sqrt(N / (2K)).
For depth-d nesting with N_chains concurrent chains and per_level_distractors=2:
- effective K ≈ N_chains * (1 + per_level_distractors) * d ≈ N_chains * 3 * d
- expected SNR ≈ sqrt(N / (2 * N_chains * 3 * d))

Predicted cliff (SNR-collapse threshold ~ accuracy 0.5 at 4-locs):
- N=8192, N_chains=10: cliff_d ≈ N / (2 * 10 * 3 * 0.5^2) / 4 = floor(N / 60 / 4) ≈ depth 34 (too deep — won't see cliff)
- BUT: per-level distractor accumulation is multiplicative across levels, so effective cliff is much sharper.

Refined prediction (per-level retention factor ~0.85 from v1 d=2 obs):
- d=1: 1.000 (positive control)
- d=3: 0.85^3 ≈ 0.61
- d=5: 0.85^5 ≈ 0.44
- d=10: 0.85^10 ≈ 0.20 (chance floor at 0.25 for 4 locs)

This SHOULD produce a non-flat depth profile at (N=8192, N_chains=10).

If still flat: v2 also has v1-bug; report HARD_FAIL_FLAT_DEPTH_PROFILE and recommend fundamental redesign (e.g. higher-rank tensor TOM encoder; non-bipolar HRR).

## Expected wall time

Smoke (32 cells × 20 trials × 3 arms × 1 seed): ~3-6 min at laptop CPU.
Full (128 cells × 50 trials × 3 arms × 3 seeds, chunked single-seed-per-cell): ~10-20 min per seed = 30-60 min total.

## Routing

- Author: exp_dev sub-agent 2026-06-28
- Smoke runner: local CPU (single seed)
- Full runner: local_cpu_queue (3 single-seed scripts: seeds {7, 13, 19}); pause-gate clean
- Landed VET owner: hdi_skunkworks (post-land)
- M3 banking owner: Research (post-VET)

If 3 seeds cross-agree on depth-cliff location, this promotes TOM higher-order MM → chain-grade-phase-characterization.
