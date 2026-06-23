# Next-iteration composition cells (contingency spec)

**Date**: 2026-06-23
**Author**: Director (this session)
**Trigger condition**: if the current 4-way GPU ablation (Path C + brain_full_compose + PC_hierarchy + sparse_competitive_readout + fresh_W_BPC_v2) HARD_FAILs on substrate-as-LM (no arm beats unigram BPC 7.738), THESE are the next cells to dispatch.

Per the **brain-existence-proof principle** (USER 2026-06-23): brain proves these mechanisms work; failure of current composition = composition not quite right yet; iterate the design, do not pivot away.

---

## Brain mechanism gaps in current compose (ranked by leverage)

### Gap A: Neuromodulator gating (DOPAMINE/ACh/SEROTONIN analog)

**Brain**: dopamine modulates plasticity rate (LTP/LTD); ACh modulates attention/encoding; serotonin modulates mood/state-gating. Each is a SCALAR signal applied to W updates.

**Substrate analog**: maintain per-substrate `modulator` scalar(s) that multiply the Hebbian learning rate; condition on context (e.g., "novelty" = high dopamine = high learning rate; "familiar" = low dopamine = low learning rate).

**Cell spec**: `substrate_neuromodulator_gated_compose_LM_v1`
- 3 modulator signals: dopamine_gate (novelty-driven), ACh_gate (attention-driven), serotonin_gate (state-driven)
- W update: `W += dopamine_gate * ACh_gate * outer(error, input)` (multiplicative gating)
- Compare: ARM_BRAIN_FULL_COMPOSE (current cell) vs ARM_BRAIN_FULL_PLUS_NEUROMOD (this cell)
- Pre-reg HARD_PASS: BPC < UNIGRAM - 0.3 (neuromod-gated beats no-gating)
- Cost: ~30-60min GPU

### Gap B: Sleep-replay scheduling (CLS REPLAY DURING IDLE)

**Brain**: hippocampus replays memories to cortex during sleep/idle; substrate's current CLS-replay runs DURING ingest. Brain's idle-replay improves consolidation by `~2x` per night.

**Substrate analog**: interleave ingest with replay cycles; alternate forward-only Hebbian writes with replay-driven backward consolidation passes.

**Cell spec**: `substrate_sleep_replay_consolidation_LM_v1`
- Phase 1: ingest text8 100k tokens (forward-only)
- Phase 2: idle-replay sample sub-batches from hippocampus W (small fast W) and write to cortex W (large slow W) with mod_gating
- Phase 3: BPC eval on held-out
- Pre-reg HARD_PASS: BPC < ARM_BRAIN_FULL - 0.3 (idle-replay lifts beyond write-time CLS)
- Cost: ~60-90min GPU

### Gap C: NMDA-style multiplicative non-linearity at substrate "synapses"

**Brain**: NMDA receptors give multiplicative effects (coincidence detection); dendritic integration is non-linear.

**Substrate analog**: W stores `outer(prev, next)` but readout could include multiplicative terms: `score = (W @ cue) * cleanup(cue)` where cleanup is a learned gating signal.

**Cell spec**: `substrate_nmda_multiplicative_readout_LM_v1`
- 4 readout arms: linear (current), multiplicative_self_gating, multiplicative_context_gating, NMDA-analog (coincidence between top-K codebook + context)
- Pre-reg HARD_PASS: multiplicative_NMDA beats linear by 0.5 bits BPC
- Cost: ~30-45min GPU

### Gap D: Larger corpus + more training passes

**Brain**: years of dense sensory data. Current text8 100k = ~3min of speech equivalent.

**Substrate analog**: text8 1M tokens (10x current); 3 training passes per arm (3x current).

**Cell spec**: `substrate_brain_full_compose_1M_v1`
- Same architecture as brain_full_compose but with N_TRAIN=1M; 3 passes; alpha decay
- Pre-reg HARD_PASS: BPC < UNIGRAM (composition closes gap at larger data; brain-existence-proof argues for ~6.6 BPC bigram-level)
- Cost: ~3-6hr GPU

### Gap E: Multi-W substrate (separate cortical regions per context)

**Brain**: different cortical regions for different domains (language in temporal cortex; spatial in parietal; etc).

**Substrate analog**: instead of one large W, maintain K=4-8 specialized W matrices; route input to most-appropriate W via Tonegawa-allocation.

**Cell spec**: `substrate_multi_region_W_compose_LM_v1`
- K=4 W matrices at N=2048 each (same total parameters as 1×N=8192)
- Routing: input → similarity to W_centroids → softmax → W_chosen for write/read
- Pre-reg HARD_PASS: multi-W beats single-W by 0.3 bits BPC
- Cost: ~45-90min GPU

### Gap F: Theta-gamma nested oscillations (lock-in attention extended)

**Brain**: theta (5Hz) carries 7±2 gamma (40Hz) cycles. Each gamma cycle holds ONE item. Theta sweeps through them.

**Substrate analog**: 2-frequency lock-in (theta_k=1 + gamma_k=31). Bind item at gamma; sequence theta. Compose with working memory HRR-slots.

**Cell spec**: `substrate_theta_gamma_nested_oscillation_LM_v1`
- Extends lock-in mega-scale finding to TWO frequencies nested
- Pre-reg HARD_PASS: theta-gamma beats single-lock-in by 0.2 bits BPC
- Cost: ~30-45min GPU

---

## Dispatch ordering (if current cells HARD_FAIL)

Priority by P_revival (brain-existence-proof asymmetric calibration):
1. **Gap A neuromodulator** (P=0.65) — brain has 3 distinct neuromod systems; substrate-native easy
2. **Gap B sleep-replay** (P=0.60) — extends CLS-replay (already chain-grade-eligible)
3. **Gap D larger corpus** (P=0.55) — sample-complexity question; brain uses years of data
4. **Gap F theta-gamma nested** (P=0.55) — extends lock-in mega-scale (chain-grade)
5. **Gap C NMDA multiplicative** (P=0.50) — adds non-linearity; speculative substrate-native
6. **Gap E multi-W** (P=0.45) — substantial architectural change

Author cells in this order; dispatch in waves of 2-3 to balance GPU + CPU load.

---

## Cross-cutting iteration principles (apply to all v2/v3 cells)

- **Same fair-comparison harness** as current cells (V=4000, N_DIM=8192, seeds=[7,17,23], fresh W per arm)
- **Brain-existence-proof framing**: cap P at 0.75 for brain-grounded mechanisms with substrate-native paths
- **Composition over ablation**: prefer testing FULL+new_mechanism vs FULL alone (additive lift)
- **WordSim353 sanity** mandatory for any encoder-touching cell (ensures learned encoding is semantic)
- **Brain-sparsity sanity** for any sparse-readout cell (cortical 1-3% firing rate band)
- **Per-arm metrics** read via `tools/peek_arm_metrics.py` before any framing (Fix #28)

---

## If ALL gap A-F cells HARD_FAIL

Substrate-as-LM may be genuinely capped at the rank-1 Hebbian floor regardless of composition. Pivot acknowledged in cert ledger:
- META atom: `substrate_as_LM_genuinely_capped_at_rank1_hebbian_floor_despite_brain_architecture_composition`
- Substrate-product pivot: refuse-aware-knowledge-store (lock-in + Shannon envelope + KG storage + refuse_gate) as the substrate-product, NOT substrate-as-LM
- Lock-in + working memory + sparse-bipolar + cleanup still substrate-product-relevant as refuse-aware substrate
