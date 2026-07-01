# M3 Cortex M1.3 — Stochastic Noise Injection at Substrate Boundary

**Author:** hdi_research (Director)
**Date:** 2026-07-01
**Load-bearing constraint:** 5x research drill 2026-06-30 confirmed substrate determinism is STRUCTURAL (bipolar bit-flip + L2-renorm gives exact cos = 1 - 2·flip_frac, std=0). Substrate CANNOT produce intermediate-confidence-band signal internally. M3 cortex layer MUST inject stochastic coupling at the substrate boundary.

**References:**
- `~/.claude/projects/d--AI/memory/project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md`
- `notes/research_deterministic_substrate_noise_model_5x_drill_2026-06-30.md`
- `notes/director_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`
- Substrate router M1.1 scaffold at `substrate_router/{api,router,test_router_smoke}.py`

## Problem statement

Intermediate-confidence-band adaptive cells (refuse-gate adaptive-tau, sliding-window tau, Kalman/EWMA gating, SWR iterative cleanup) all failed at substrate level because they need an input distribution with `variance > 0` at the decision boundary. Substrate's canonical noise process (bipolar bit-flip + L2-renorm) is a **count statistic**: given `p` flipped bits out of `N`, cosine to original = `1 - 2p/N` **exactly**, with `std = 0` across trials. Adaptive cells expecting a continuous confidence PDF over the interval `[τ_low, τ_high]` see a delta at a single value and refuse-gate/tau selection has no signal to work with.

**Cortex must inject stochastic coupling at the boundary between substrate reads/writes and the adaptive mechanism** so that:
1. Substrate stays deterministic (preserves capacity bounds, cross-seed reproducibility, cross-cell hash-distinctness disciplines, cert-architecture guarantees).
2. Adaptive cells see the noisy input distribution they need.
3. The injected noise is **calibrated to task regime** (SNR, temperature, or corruption level are cortex-level control knobs, not substrate-internal).

## Design

### Module: `substrate_router/noise_channel.py` (new)

```
NoiseChannel:
    inject(vec: Tensor, regime: str, rng: Generator) -> Tensor
```

**Signature (in Tensor shapes):**
- `vec`: `(B, N)` real-float for HRR / `(B, N)` complex64 for FHRR / `(B, N)` int8 for bipolar
- `regime`: str in {`clean`, `light`, `moderate`, `heavy`, `catastrophic`}; maps to `sigma` via table
- `rng`: `torch.Generator` for reproducibility

**Return shape:** same as input; values noise-corrupted per encoder-specific rule.

### Noise-injection modes (5 mechanism classes; encoder-aware)

Each mode has a per-encoder implementation. All modes preserve `L2(vec)` post-injection (L2-renorm final step).

| Mode | Applied to | Mechanism | Distribution at boundary |
|---|---|---|---|
| `additive_gaussian` | HRR real, FHRR real-part | `vec + sigma * N(0, I_N)`; then L2-renorm | Continuous PDF on cosine domain; std = f(sigma, N) |
| `additive_complex_gaussian` | FHRR complex | `vec + sigma * (N(0,I) + iN(0,I))/sqrt(2)`; then L2-renorm on complex norm | Continuous PDF on phase + magnitude |
| `bernoulli_flip_stochastic` | bipolar int8 | Per-bit `Bernoulli(p=p_flip)` then flip; then re-encode L2 | Discrete integer flip-count, but binomial dispersion gives non-degenerate PDF across trials — this fixes the current bit-flip determinism at the trial level (the substrate's problem is that flip_count is DETERMINED via `n_bits*flip_frac`; making it stochastic Bernoulli restores the trial-level PDF) |
| `dropout_mask` | any encoder | Per-index `Bernoulli(p=1-drop_frac)` zero-mask; L2-renorm | Sparse noise; distribution controlled by drop_frac |
| `temperature_softmax` | on similarity scores post-substrate-read | `softmax(scores / T)` where T is regime-dependent | Confidence distribution over readout candidates |

**Key insight:** modes 1-4 are pre-substrate (noise on input encoding before write OR on cue before read). Mode 5 is post-substrate (noise on readout probability). Adaptive cells select mode based on where they need the confidence signal.

### Regime → sigma table (calibration; update per empirical evidence)

| Regime | Additive sigma | Bernoulli p_flip | Dropout drop_frac | Temperature T |
|---|---|---|---|---|
| clean | 0.00 | 0.00 | 0.00 | 1.0 |
| light | 0.05 | 0.02 | 0.05 | 1.5 |
| moderate | 0.15 | 0.08 | 0.15 | 2.5 |
| heavy | 0.35 | 0.20 | 0.30 | 5.0 |
| catastrophic | 0.60 | 0.40 | 0.50 | 10.0 |

Calibrated so that `cosine(vec, inject(vec, 'moderate'))` ≈ 0.85 (empirically consistent with refuse-gate mid_flip=0.40 point where adaptive-tau v2 was supposed to fire but didn't).

## Integration with substrate router (M1.3+)

**Current M1.1 flow (deterministic):**
```
route(query) → intent_classifier(query) → KG_lookup(intent) → return outcome
```

**M1.3 flow (with stochastic boundary):**
```
route(query, regime='moderate') →
    query_noisy = noise_channel.inject(query, regime, cortex_rng)
    intent = intent_classifier(query_noisy)  # sees noisy input distribution
    candidates = KG_lookup(intent)           # deterministic substrate read
    scores_noisy = noise_channel.inject(candidates.scores, regime='post_softmax', T=2.5)
    return refuse_gate(scores_noisy) OR top_k
```

**Refuse-gate integration (unblocks deferred v3):**
- Adaptive-tau v3 was deferred because substrate-internal stochastic redesign would break determinism guarantees.
- With cortex noise_channel: refuse-gate operates on `scores_noisy` (has intermediate-confidence-band PDF). Adaptive-tau can now fire.
- Tau sliding-window updates based on the noisy score distribution, not the substrate's deterministic output.

## What noise_channel does NOT do

- Does NOT modify substrate's internal state (Store atoms unchanged; W_c / W_h weights unchanged; encoder codebooks unchanged).
- Does NOT modify substrate's read/write API (`bind`, `unbind`, `bundle`, `cleanup` all remain deterministic).
- Does NOT interfere with cross-seed reproducibility (the noise `rng` is cortex-scoped; substrate rng seeds untouched).
- Does NOT enter the cert-ledger provenance chain (cortex is a separate audit layer per M3 milestone).

## Test plan (M1.3 verification)

### Smoke tests (`substrate_router/test_noise_channel_smoke.py`)

1. **Determinism check:** with fixed rng seed, `inject(vec)` returns identical output. 100 trials.
2. **PDF check:** with 1000 different rng seeds, `inject(vec, 'moderate')` outputs distribute continuously; `std > 0.01` on cosine to `vec`.
3. **L2 preservation:** post-inject L2 norm within `1e-6` of original L2 norm.
4. **Encoder specialization:** each of bipolar/HRR-real/FHRR-complex takes the correct mode; type-check refuses wrong-mode application.
5. **Regime monotonicity:** cosine(vec, inject(vec, r)) decreases monotonically for r in [clean, light, moderate, heavy, catastrophic].

### Integration tests (`substrate_router/test_router_with_noise_smoke.py`)

1. **Baseline:** router without noise_channel; 20/20 hand-crafted-bank smoke pass (same as M1.1).
2. **With noise 'moderate':** router with noise_channel injected; refuse-gate v3 fires on borderline queries where M1.1 always returned top-1. Adaptive-tau can now differentiate confidence bands.
3. **Cross-regime:** same query at 'clean' vs 'moderate' vs 'heavy' → refuse-gate confidence decreases monotonically; refuse-rate increases monotonically.

## Sequencing

- **Phase 1 (M1.3):** ship `noise_channel.py` + 5 smoke tests + basic router integration. ~3-5 cycles.
- **Phase 2 (M1.4):** wire adaptive-tau v3 through cortex noise-channel; unblock the deferred cell family.
- **Phase 3 (M1.5):** wire SWR-like iterative cleanup with noise injection (unblock SWR family which was deferred at substrate level).
- **Phase 4 (M1.6):** calibrate regime sigmas empirically on a 200-query cert benchmark; lock table.

## Consequences for deferred cells

Previously-deferred cells that unblock with cortex noise-channel:
1. **Refuse-gate adaptive-tau v3** — unblocked; ships M1.4.
2. **SWR iterative clean replay v3+** — unblocked at cortex layer; ships M1.5. Substrate-native SWR remains permanently deferred per 5x drill.
3. **Any intermediate-confidence-band mechanism** — unblocked when applicable.

Cells that STAY closed-negative (substrate structural, not fixable at cortex):
1. Substrate-native barrier 1 hint derivation (5 drills HF).
2. Substrate-native hierarchical planning (5 cells / 4 mechanism classes HF).
3. Substrate-native long-narrative Q2 coref (2 drills HF).

Cortex layer is the compensation channel for the first three; the substrate-native versions remain closed.

## Risks + open questions

1. **Calibration drift:** the regime→sigma table may need per-encoder tuning. Ship v1 with the table above; iterate based on empirical evidence.
2. **Rng-injection bookkeeping:** cortex-scoped rng must NOT leak into substrate rng (otherwise cross-seed determinism at substrate level is broken). Enforce via `NoiseChannel` owning its own `torch.Generator` instance passed at construct time.
3. **Cell-author interaction:** future adaptive cells must declare noise-mode requirements in pre-reg (e.g. `NOISE_MODE=temperature_softmax`, `REGIME=moderate`). This is a new pre-reg field.
4. **Cost:** cortex-level noise injection is per-query, not per-cell. Overhead is `O(N)` per inject call. For 200-query cert benchmark: ~200 × 8192 × 4 bytes = ~6.5 MB extra memory, negligible.

## Next action

Spawn `hdi_exp_dev` to author `substrate_router/noise_channel.py` + 5 smoke tests. Pre-reg the smoke gates. Then integration wire through router. No FULL dispatch until cell-author + smoke pass.

Expected timeline to M1.3 milestone: 3-5 cycles (author + smoke + integration + calibrate).
