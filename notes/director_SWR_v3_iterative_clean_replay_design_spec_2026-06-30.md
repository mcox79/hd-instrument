# SWR v3 iterative clean replay design spec

**Filed:** 2026-06-30 19:15 UTC
**Audience:** hdi_exp_dev (next cell-author)
**Motivation:** Two prior SWR attempts both honest-aborted at smoke. Cell-author a24de6ad insight: "true SWR = iterative clean replay, not bundled outer product" — captures the biologically-accurate mechanism.

---

## Prior SWR attempts (both honest-aborted)

### v1: SWR compressed bundling
- Mechanism: bundle K items into ONE outer-product write per chunk
- Smoke result: K² cross-terms in cortex W; recall DROPS 0.554 → 0.001 as K grows
- Honest-abort by cell-author; mechanism formulation wrong
- File: `experiments/exp_substrate_swr_compressed_bundling_K_sweep_v1_GPU.py` (committed, NOT dispatched)

### v2: SWR multipass clean replay
- Mechanism: multipass — each pass does clean retrieval then writes back
- Smoke result: all N_REPLAY arms = 0.985 (matches v2 CLEAN_VALS baseline)
- Cell-author insight: "single-pass already at ceiling at this regime; multi-pass doesn't lift the clean-vals ceiling"
- Verdict: HARD_PASS, but **likely MM_BC_CEILING** (Hc by-construction trap) — Skunkworks VET pending
- File: `experiments/exp_substrate_swr_multipass_clean_replay_v2_GPU.py` (committed, landed HP)

---

## Why both v1 + v2 are misframed

**v1 (bundling) collapses recall by introducing cross-terms** — bundling K items via outer-product W_t = Σ_i (k_i ⊗ v_i) creates K² interference. Going from 1-item write to 10-item bundled write means signal/noise drops by ~K.

**v2 (multipass) hits ceiling at SMALL M** — at this regime, single-pass clean retrieval ALREADY recovers DIRECT. Multi-pass adds no marginal value because the noise is already negligible. To see multi-pass benefit, need a regime where single-pass DOESN'T recover DIRECT.

**Biological SWR insight:** in hippocampus, replay is iterative SEQUENCE reactivation, not parallel bundling. Each replay step reactivates a single time-slice in order; the replay sequence as a whole transmits the memory trace to cortex. The "compressed" aspect is TEMPORAL compression (10-20x faster than wake), not capacity-bundling.

---

## v3 design: TRUE iterative sequence replay

### Mechanism

```python
def swr_v3_replay(seq_keys, seq_vals, W_cortex, n_replay_passes=5, cleanup_attractor=...):
    """Iterative SEQUENCE replay (not parallel bundling).
    
    For each replay pass: walk sequence in compressed time; for each (k, v) in
    sequence, retrieve k from cortex (with attractor cleanup) and write back
    cleaned v. After N passes, cortex W has been incrementally refined.
    """
    for pass_idx in range(n_replay_passes):
        for k, v in zip(seq_keys, seq_vals):
            # Step 1: retrieve via attractor cleanup (Hopfield/iterative)
            k_clean = cleanup_attractor(k, W_cortex)
            # Step 2: cortex receives cleaned value
            v_predicted = W_cortex @ k_clean
            v_cleaned = cleanup_attractor(v_predicted, codebook_v)
            # Step 3: re-write back to cortex (Hebbian + decay)
            W_cortex = decay_factor * W_cortex + lr * np.outer(v_cleaned, k_clean)
    return W_cortex
```

### Key differences from v1 + v2

- **vs v1 (bundling):** writes are SINGLE items per step (not K-bundled); cross-terms emerge only from sequence-step accumulation, not within-pass interference
- **vs v2 (parallel multipass):** the replay is SEQUENTIAL across time-slices, not parallel attention over codebook; attractor cleanup at EACH step is the load-bearing operation

### Regime where v3 should show benefit

v2 hit ceiling because single-pass at small M was already enough. v3 should be tested at LARGE M where single-pass cleanup is insufficient:

- M = 4096 - 16384 (well above v2's ceiling regime)
- Sequence length = 100 (long enough that early items decay from cortex if not replayed)
- n_replay_passes ∈ {1, 2, 5, 10, 20}
- N_DIM = 8192
- N_cortex = 2048 (so M/N_c can be > 1.0 to stress capacity)

### Discriminator

HARD_PASS:
- Recall(n_replay=20) ≥ Recall(n_replay=1) + 0.20 at chain-grade scale (M=8192)
- Monotonic improvement across n_replay_passes
- cv across 3 seeds ≤ 0.10
- mechanism_hash distinct per n_replay value (META_RULE_AX)
- Not BC-ceiling: at K=20 replay passes, recall < DIRECT_UPPER by ≥ 0.03

MIDDLE_BAND:
- Some lift (≥ 0.10) but not full HP gap
- Or saturation at lower N_REPLAY than expected

HARD_FAIL:
- Replay doesn't lift at all (mechanism broken)
- Or BC-ceiling: all n_replay arms = DIRECT_UPPER (would be Hc trap recurrence)
- Or recall DROPS with more passes (cross-term accumulation; like v1)

### META rules to enforce

- META_RULE_AX: per-n_replay mechanism_hash distinct + per-arm metrics distinct
- META_RULE_AY: verdict logic HARD_FAIL on encoder_pair_distinctness=False
- META_RULE_Q: suspect-1.000 check at high n_replay
- META_RULE_AW: seed-config-identical
- META_RULE_AU + AV
- Discriminator-must-survive-scale: smoke at M=4096+ to verify discriminator fires at FULL M=8192

### Queue + timeout

- Queue: overnight_queue (GPU; iterative attractor + matmul-bound)
- Timeout: 3600s/seed (5 n_replay values × ~100 sequence steps × attractor cleanup = ~600s headroom 6x)
- 3 seeds [7, 13, 19]

---

## Effort estimate

- Cell core (`_substrate_swr_v3_iterative_clean_replay_core.py`): ~250 LoC (uses existing `hdlab.iterative_attractor.iterative_cleanup` for cleanup step + Hebbian write + sequence iteration)
- Per-seed cell entries (3 files): ~120 LoC total
- Pre-reg: ~80 lines
- **Total ~450 LoC; estimated 2 hr authoring**

Much smaller than ANCHOR 4 v4 because it reuses existing hdlab modules (iterative_attractor) + the cell is conceptually simpler (one mechanism family with one parameter sweep).

---

## Composes with Stage 2 NREM picture

If v3 HARD_PASS at chain-grade scale M=8192:
- Independent rescue path from Cell C v2 compartmentalized cortex (which is spatial via K-banks)
- v3 is TEMPORAL rescue via iterative replay
- Combined Ha (cross-term fix) + Hc-compartmentalization (spatial K-banks) + iterative-replay (temporal) = robust Stage 2 NREM closure path
- Each substrate-native; brain-grounded
