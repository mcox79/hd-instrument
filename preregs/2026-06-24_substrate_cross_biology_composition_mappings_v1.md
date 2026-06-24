# Pre-registration: substrate_cross_biology_composition_mappings_v1

**Date:** 2026-06-24
**Anchor:** substrate_cross_biology_composition_mappings_v1
**Script:** experiments/exp_substrate_cross_biology_composition_mappings_v1.py
**Queue:** remote_cpu_queue (~60min wall per drill estimate; 4500s timeout)
**Timeout:** 4500s (75min)
**Drill source:** notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md
**Strategic context:** 7 non-brain biological systems CONVERGE on near-decomposability + weak coupling as universal composition principle. Substrate same-W stacking VIOLATES this. This cell tests 3 substrate-native mappings derived from non-brain biology.

## Why this cell (load-bearing)

USER directive: drill how OTHER biological systems solve composition. Drill output: 7 systems (gene regulation, signal transduction, immune system, ant colony stigmergy, cellular compartmentalization, Hox positional code, MAPK scaffold) converge on near-decomposability + weak-coupling-between-specialized-modules. The substrate's same-W stacking is the architectural OPPOSITE of this universal biology principle. If ANY of the 3 mappings HARD_PASSes, substrate-native composition unlocks via non-brain-biology design principles.

P_deflated = 0.65 per drill (deflated from 0.85 raw; 7 independent biology systems converge; 0.20 lit-scan calibration penalty).

## Hypothesis

Near-decomposability + weak-coupling architectures (kinetic insulation / combinatorial positional code / stigmergic indirect coordination) BREAK substrate composition collapse because the collapse is an architectural consequence of same-W stacking — not a substrate-capacity cap. Three biology-inspired architectures redundantly probe weak-coupling:

1. **ARM_SCAFFOLD_KINETIC** — MAPK scaffold analog: cf-RPE on W_cf, STDP on W_stdp; slow cross-W transfer (mix small fraction every 100 steps)
2. **ARM_HOX_COMBINATORIAL_3AXIS** — Hox developmental analog: 3 orthogonal W matrices, each updated by ONE mechanism only; final logit = additive combination
3. **ARM_STIGMERGIC_SHARED_CACHE** — ant colony stigmergy analog: shared cache vector; mechanisms write/read via cache; NO direct W-to-W coupling

## Design — four arms

| Arm | Architecture | Plasticity | Coupling | Notes |
|-----|--------------|-----------|----------|-------|
| ARM_BASELINE_CFRPE_K1 | K=1 single bank | cf-RPE | none | Reference rail to A3 7.0707 ± 0.05 |
| ARM_SCAFFOLD_KINETIC | 2 banks W_cf, W_stdp at full N_DIM | cf-RPE on W_cf; STDP on W_stdp | Slow cross-W transfer every 100 steps: W_cf += eps * W_stdp, W_stdp += eps * W_cf | Bio anchor: MAPK kinetic insulation; weak coupling NOT zero coupling |
| ARM_HOX_COMBINATORIAL_3AXIS | 3 banks W_A, W_B, W_C at full N_DIM, on 3 orthogonal subspaces | cf-RPE writes W_A; STDP writes W_B; sparse-amp writes W_C | None (orthogonal subspaces) | Bio anchor: Hox AP/PD/DV axes; readout = sum of cosine on 3 axes |
| ARM_STIGMERGIC_SHARED_CACHE | 1 bank W + shared cache vector P (dim N_DIM) | cf-RPE writes W AND deposits onto P; STDP writes W AND deposits onto P with decay; sparse-amp reads P to modulate W | Indirect via P only; mechanisms never directly modify each other | Bio anchor: ant pheromone trails; stigmergic environment |

**Encoder:** word2vec-google-news-300 → Gaussian-project(300→8192) → L2 → sparse-bipolar f=0.05 → L2. Identical to fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR. Apples-to-apples: ALL arms use SAME encoding; ONLY composition architecture varies.

**Plasticity primitives (frozen from A1 chain-grade source):**
- cf-RPE: iterative dW = (Nxt - Ctx @ W.T)^T @ Ctx / batch; lr=0.5
- STDP: dW = (Nxt^T @ Ctx - Ctx^T @ Nxt) / batch; w=0.5
- Sparse-amp: amplify top-k by abs magnitude (no update — only modulates)

**Architecture details:**

ARM_SCAFFOLD_KINETIC:
```
W_cf, W_stdp both zeros at start
At each step:
  cf-RPE update on W_cf
  STDP update on W_stdp
At step % 100 == 0: cross-W transfer (slow exchange):
  W_cf  += SCAFFOLD_TRANSFER_EPS * W_stdp
  W_stdp += SCAFFOLD_TRANSFER_EPS * W_cf
Readout: pred = L2(ctx @ (W_cf + W_stdp).T)
         logits = pred @ E.T
```

ARM_HOX_COMBINATORIAL_3AXIS:
```
N_DIM_AXIS = N_DIM // 3 (2730 for N_DIM=8192; remainder pads first axis)
QR decomposition of Gaussian(N_DIM, N_DIM) -> P_orth
P_A = P_orth[:, :N_DIM_A]  (frequency axis)
P_B = P_orth[:, N_DIM_A:N_DIM_A+N_DIM_B]  (temporal axis)
P_C = P_orth[:, N_DIM_A+N_DIM_B:]  (rarity axis)
W_A (N_DIM_A x N_DIM_A): cf-RPE updates only
W_B (N_DIM_B x N_DIM_B): STDP updates only
W_C (N_DIM_C x N_DIM_C): sparse-amp updates only
Each axis projects encoder via P_A.T, P_B.T, P_C.T (each is [N_DIM, N_DIM_K])
Readout: cos_A(h, codebook) + cos_B(h, codebook) + cos_C(h, codebook)
         where each axis-cos uses axis-projected vectors
```

ARM_STIGMERGIC_SHARED_CACHE:
```
W zeros at start
P (cache vector dim N_DIM) zeros at start
TAU_FAST = 10, TAU_MED = 100 (decay rates)
At each step:
  dW_cf = cf-RPE update
  W += dW_cf
  P += sign(dW_cf.sum(axis=0)) (bipolar pheromone)
  P *= (1 - 1/TAU_FAST)  (fast decay)

  dW_stdp = STDP update
  W += STDP_W * dW_stdp
  P += STDP_W * sign(dW_stdp.sum(axis=0))
  P *= (1 - 1/TAU_MED)  (medium decay)

  # sparse-amp READS P to modulate W
  modulation = sigmoid(P.norm()) * 0.05
  # No direct modification; tracked via P_USAGE metric

Readout: pred = L2(ctx @ W.T)
         logits = pred @ E.T
P_USAGE_METRIC: ||P|| trajectory (must vary nontrivially)
```

**Readouts:**
- BASELINE_CFRPE_K1: `pred = L2(ctx @ W.T); logits = pred @ E.T`
- SCAFFOLD_KINETIC: `pred = L2(ctx @ (W_cf + W_stdp).T); logits = pred @ E.T`
- HOX_3AXIS: `logits = (E @ P_A.T @ pred_A.T) + (E @ P_B.T @ pred_B.T) + (E @ P_C.T @ pred_C.T)` (axis-projected cosine sum)
- STIGMERGIC: `pred = L2(ctx @ W.T); logits = pred @ E.T` (cache is internal coordination, not output)

**Eval grids:**
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per META C7)
- Joint (T, λ) sweep on dev half; report best on test half

## Pre-registered threshold bands (HARD)

Sanity rail fires BEFORE verdict bands.

| Verdict | Condition |
|---------|-----------|
| HARD_FAIL_LLM_CALL | `_LLM_CALL_COUNTER > 0` (substrate-only invariant) |
| HARD_FAIL (all bio arms fail) | All 3 biology-inspired arms compute-fail all seeds |
| HARD_FAIL_PROVENANCE_BASELINE | ARM_BASELINE_CFRPE_K1 BPC drifts > ±0.05 from 7.0707 (A3 cf-RPE coarse reference) |
| MIDDLE_BAND_HIGH_CV | best_bio arm cv > 0.05 across seeds |
| HARD_PASS_CHAIN_GRADE_BONUS | best_bio BPC ≤ 6.80 AND cv ≤ 0.05 (substantial gain) |
| HARD_PASS_NEAR_DECOMPOSABILITY | best_bio BPC ≤ 6.95 AND cv ≤ 0.05 (near-decomposability works in substrate) |
| MIDDLE_BAND | best_bio BPC in [6.95, 7.05] |
| MIDDLE_BAND_INTER_GAP | best_bio BPC in (7.05, 7.20) |
| HARD_FAIL_DECISIVE | all 3 bio arms BPC ≥ 7.20 (substrate composition resists weak-coupling) |

## Discriminating-regime metrics (mandatory)

Each biology-inspired arm must demonstrate the architecture has MEASURABLE distinct effect from same-W stacking. Reported in `detail.by_arm_agg[arm].discriminating_per_seed`:

- **ARM_SCAFFOLD_KINETIC:**
  - `w_cf_vs_w_stdp_corr` — cosine between vec(W_cf) and vec(W_stdp); must be < 0.95 (banks store distinct content; weak coupling preserved)
  - `transfer_rate_effect` — small SCAFFOLD_TRANSFER_EPS implies more decomposable; logged scalar
  - `n_cross_transfers` — count of cross-W transfer events
- **ARM_HOX_COMBINATORIAL_3AXIS:**
  - `axis_a_ablation_lift` — BPC delta when only axis A used (per-axis ablation contribution)
  - `axis_b_ablation_lift`
  - `axis_c_ablation_lift`
  - `axis_orthog_residual_max` — max |P_A.T @ P_B|, |P_A.T @ P_C|, |P_B.T @ P_C|; must < 1e-3
  - All 3 axis contributions must be non-zero when included vs ablated (each axis contributes); per-axis lift differential > 0.01 BPC means HONEST 3-axis use
- **ARM_STIGMERGIC_SHARED_CACHE:**
  - `cache_norm_max` — peak ||P|| across stream (must be > 0.1 to confirm stigmergy engaged)
  - `cache_norm_mean` — mean ||P|| across stream
  - `cache_decay_observed` — measured decay (P should NOT saturate; should fluctuate)
  - `cache_utilization_score` — proxy: variance of ||P|| over stream

## Outcome plan for each verdict

- **HARD_PASS_CHAIN_GRADE_BONUS (best_bio ≤ 6.80):** Substrate-native composition via non-brain biology vindicated decisively. Atomize as chain-grade-eligible cross-biology lift. Identify WHICH bio principle wins; route to Strategy for next-cycle deeper drill. Route to Skunkworks for landed-VET.

- **HARD_PASS_NEAR_DECOMPOSABILITY (best_bio ≤ 6.95):** Near-decomposability principle works in substrate. Atomize as MEASURED_MECHANISM with chain-grade-pending. Route to Research for 2x revival drill: which mechanism is load-bearing in winning architecture?

- **MIDDLE_BAND / INTER_GAP:** partial biology principle benefit. Route to Research for next-drill: end-to-end tuned weak-coupling rates / 4th biology system (gene regulation cooperative-AND-gating, immune affinity maturation, sigma-factor switching).

- **HARD_FAIL_DECISIVE (all 3 bio BPC ≥ 7.20):** substrate composition resists weak-coupling architecture too. Honest finding for USER. Route to Research for architectural pivot.

- **HARD_FAIL_PROVENANCE_BASELINE:** encoder/cf-RPE pipeline mismatch. Debug before any biology interpretation.

- **HARD_FAIL_LLM_CALL:** substrate-only invariant broken. Patch + re-dispatch.

## Smoke gate (load-bearing)

**Smoke scale:** N_DIM=1024, N_TRAIN=2000 synthetic markov-bigram, 1 seed, 80 steps, V=300.

**Smoke encoder:** clean synthetic gaussian (NOT word2vec state) per memory rule.

**Smoke MUST verify:**
- All 4 arms produce non-null, non-sentinel, finite BPC / top1 / mrr
- All instrumentation self-tests pass at small scale
- Scaffold-kinetic produces W_cf and W_stdp distinct (corr < 0.95)
- Hox-3-axis produces orthog_residual_max < 1e-3 + 3 axes contribute non-trivially
- Stigmergic produces ||P|| > 0 and < saturation
- LLM call counter == 0
- raw_bpc_at_T1_L1 finite for all arms (DEGEN gate)
- All 4 arm logits non-identical pairwise (diversity check)

**Smoke wall target:** < 180s.

Provenance rails OFF at smoke scale (V/N differ structurally; absolute BPC will diverge by construction).

## Timeout estimate

**Per-seed wall on CPU (estimated from cf-RPE + STDP matmul ops at N_DIM=8192, V=4000, n_steps=1000, batch=64):**

- ARM_BASELINE_CFRPE_K1 (single bank cf-RPE, 1000 steps): ~150s/seed
- ARM_SCAFFOLD_KINETIC (2 banks at 8192×8192, 1000 steps + cross-transfer): ~350s/seed
- ARM_HOX_COMBINATORIAL_3AXIS (3 banks at ~2730×2730 each + per-axis ops + QR): ~250s/seed
- ARM_STIGMERGIC_SHARED_CACHE (1 bank 8192×8192 + cache writes): ~250s/seed
- Encoder + corpus per seed: ~50s
- Joint sweep + bookkeeping per arm: ~10s × 4 = 40s
- Discriminating metrics (corr / norm / ablation): ~10s/arm × 3 arms = 30s

**Per-seed total ~1120s ≈ 18.7min**
**3 seeds: ~56min**
**With 1.3× safety: ~73min ≈ 4380s**

**timeout_s = 4500 (75min)** — fits drill's ~60min estimate with safety margin. No PROT-019 trigger (no _nN suffix). PROT-021: timeout < 14400 so checkpoint optional but imported anyway for safety.

## What this does NOT show

- Does NOT test SCAFFOLD_TRANSFER_EPS sweep (fixed at 0.01; sweep is future work)
- Does NOT test 4 or 5 Hox axes (3 fixed per drill)
- Does NOT test alternative stigmergy decay schedules (TAU_FAST/MED fixed)
- Does NOT test other 4 non-brain biology principles (gene regulation cooperative-AND, immune mutate-and-select, cellular compartmentalization, sigma-factor switching) — covered in L4/L5 drill if primary HARD_PASSes
- Does NOT test composition of multiple bio arms in one cell (e.g., scaffold-kinetic + stigmergic stacked)
- Does NOT test text8 at larger N_TRAIN or different vocab cap
- HARD_FAIL_DECISIVE does NOT rule out non-brain biology under different conditions (different encoder, larger N, longer training, alternative cross-coupling rates)

## Cites

- notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md (drill source)
- USER directive 2026-06-24: drill OTHER biology systems for composition strategies
- data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json (A3 cf-RPE reference 7.0707)
- experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py (A1 cf-RPE + STDP primitives source)
- experiments/exp_substrate_compose_heterogeneous_routing_v1.py (2-bank architectural template)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (encoder provenance 7.3065 Hebbian)
- Skunkworks META C7 (LAMBDA_GRID excludes 0.0)
- Fix #26 (predispatch verify-the-referent — passed: PROCEED; 0 prior matching landings)
- Fix #28 (per-arm metrics ONLY; discriminating-regime metrics mandatory)
- USER 2026-06-23 (smoke clean synthetic data; not substrate state)
- USER 2026-06-22 (bias audit D — use word-bigram baseline as SECONDARY; here covered by unigram baseline since fair-harness rail is identical pipeline)
