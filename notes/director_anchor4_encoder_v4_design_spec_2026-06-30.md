# ANCHOR 4 encoder family v4 design spec — encoder-specific code paths

**Filed:** 2026-06-30 19:10 UTC
**Audience:** hdi_exp_dev (next cell-author)
**Motivation:** Skunkworks a4bfdc71 caught v3 as 6th phantom-FULL (partial): dense triplet (binary_bipolar / hrr_real / fhrr) BIT-IDENTICAL to 6 decimal places. v3 fix moved from 0/5 distinct (v1 rerun) to 2/5 distinct (v3 sparse_bipolar + sparse_real wired). Dense triplet still phantom.

---

## Root cause (per Skunkworks forensic)

v3 cell uses ONE binding mechanism path for "dense bipolar/real-valued binding regardless of HRR vs FHRR vs raw." The `_substrate_anchor4_encoder_family_phase_diagram_v3_core.py` mechanism doesn't actually invoke FFT (HRR), complex-multiplication (FHRR), or XOR/sign (binary) differently — it routes them all through the same outer-product Hebbian write + time-decay computation.

The `working_set_retention` metric depends only on (N_atoms, n_days, decay_rate, capacity_load) — encoder-INDEPENDENT scalars. Encoder dtype/dim labels are correctly set (FHRR labeled complex64 dim_eff=N/2) but DO NOT FLOW into the metric.

---

## Required v4 fix

### 1. Encoder-specific binding code paths

Each encoder must invoke its OWN binding operation:

```python
def bind_binary_bipolar(a, b):
    """XOR-equivalent for ±1 bipolar: sign(a * b). One-hot XOR for binary inner."""
    return (a * b).astype(np.float32)  # element-wise; result still in {-1, +1}

def bind_hrr_real(a, b):
    """Circular convolution via FFT. Different from element-wise mult."""
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.real(np.fft.ifft(fa * fb)).astype(np.float32)

def bind_fhrr_complex(a_complex, b_complex):
    """FHRR phase-binding: element-wise complex multiplication."""
    return (a_complex * b_complex).astype(np.complex64)

def bind_sparse_bipolar(a_sparse, b_sparse):
    """Sparse bipolar bundling: AND on indices + sign vote."""
    # implementation per sparse_bipolar library
    ...

def bind_sparse_real(a_sparse_real, b_sparse_real):
    """Sparse real outer-product followed by top-k retention."""
    ...
```

**Critical:** dense triplet must produce DIFFERENT W (or equivalent) matrices after binding. FFT vs element-wise vs complex-multiply are mathematically distinct; if implemented correctly, mechanism_hash will differ.

### 2. Pre-flight distinctness gate

```python
def verify_encoder_distinctness(encoders, seed):
    """Pre-flight check: bind a fixed test pair under each encoder; mechanism_hash must differ."""
    test_a = generate_test_vec(seed, n_dim=1024)
    test_b = generate_test_vec(seed + 1, n_dim=1024)
    hashes = {}
    for name, encoder in encoders.items():
        result = encoder.bind(encoder.encode(test_a), encoder.encode(test_b))
        h = hashlib.sha256(result.tobytes()).hexdigest()[:16]
        if h in hashes.values():
            raise RuntimeError(
                f"ENCODER_HASH_COLLISION: {name} == {[n for n, hv in hashes.items() if hv == h][0]} "
                f"(hash={h}). Cell HARD_FAILs pre-dispatch (META_RULE_AY)."
            )
        hashes[name] = h
    return hashes
```

Run this at cell entry; HARD_FAIL the cell if any 2 encoder hashes collide. Avoids landing FULL with phantom encoders.

### 3. Verdict-emitter discipline (META_RULE_AY)

```python
def emit_verdict(per_arm_metrics, encoder_pair_distinctness):
    """Verdict-emitter must HARD_FAIL on any False in encoder_pair_distinctness."""
    if not all(encoder_pair_distinctness.values()):
        failed = [pair for pair, ok in encoder_pair_distinctness.items() if not ok]
        return ("HARD_FAIL", f"ENCODER_PAIR_DISTINCTNESS_FAILED: {failed}")
    # ... then HP/MB/HF banding logic
```

NOT just suspected-1.000 META_RULE_Q — but ALSO this verdict-level enforcement.

### 4. Regime where saturation doesn't mask

v3 had 13/18 phase cells saturate to bit-identical 1.000 at higher capacity (N≥8192 OR load=1.0 mid cells). Saturation hid encoder differences. v4 fix:
- Lower N: use N=2048 / 4096 / 8192 (drop N=16384 from main grid; keep as scaling-check only)
- Higher load: load_capacity = {2.0, 4.0, 8.0, 12.0} (push past v3's max of 5.0)
- Higher noise: add explicit noise floor sigma=0.1 to recency_decode_acc computation
- Goal: NO cell should hit recall=1.000 at any (N, load, decay) combination

### 5. Regime: lower-capacity + higher-load + noise

```python
# v3 regime (caused saturation):
# N_DIMS = [1024, 2048, 4096, 8192, 16384]
# LOADS = [1.0, 2.0, 5.0]
# DECAYS = [30, 60, 180]

# v4 regime:
N_DIMS = [2048, 4096, 8192]      # drop 1024 (too small) + 16384 (saturates)
LOADS = [2.0, 4.0, 8.0, 12.0]   # push higher load
DECAYS = [30, 60, 180]           # keep
NOISE_SIGMA = 0.1                # add noise floor to retain mechanism resolution
```

Phase grid: 3 N × 4 LOAD × 3 DECAY = 36 cells per encoder. 5 encoders × 36 = 180 cells per seed. 3 seeds.

### 6. Discriminator

HARD_PASS:
- All 5 encoder mechanism_hashes distinct (encoder_pair_distinctness all True)
- ≥ 4 of 5 encoders pass per-encoder Pareto-AUC dominance ≥ 0.85 individually (within-encoder TD-dominates-RD)
- Cross-encoder metric distinctness: ≥ 7 of 10 pairs show |Δ recency_decode| ≥ 0.05 averaged across grid
- NO cell has bit-identical metrics across encoders (META_RULE_Q saturation check)
- cv across seeds ≤ 0.10

MIDDLE_BAND:
- 4/5 encoder hashes distinct (one collision) OR 5/10 pairs differ
- Some cells saturate but most discriminate

HARD_FAIL:
- Any encoder hash collision (pre-flight gate fires)
- Verdict-emitter ENCODER_PAIR_DISTINCTNESS_FAILED (META_RULE_AY)
- > 50% phase cells saturate to 1.000 (META_RULE_Q tripped)

### 7. Queue + timeout

- Queue: overnight_queue (GPU; multi-encoder + multi-load matmul-bound)
- Timeout: 1800s/seed (180 phase cells × ~5s/cell GPU = ~900s headroom 2x)
- 3 seeds [7, 13, 19]
- META_RULE_AW: all 3 seeds use IDENTICAL config (N_DIMS, LOADS, DECAYS, NOISE_SIGMA, encoders)

---

## Effort estimate

- Cell core (`_substrate_anchor4_encoder_family_phase_diagram_v4_core.py`): ~400 LoC (5 encoder-specific binding ops + pre-flight gate + verdict-emitter)
- Per-seed cell entries (3 files): ~200 LoC total
- Pre-reg: ~120 lines
- **Total ~720 LoC; estimated 3-4 hr authoring per a2e6c3b4's careful budget**

This is the focused "encoder family fix" cell — not a full new architecture. The 5 encoder-specific binding ops are mathematically distinct (FFT vs element-wise vs complex-multiply vs sparse-OR) — if implemented correctly, mechanism_hash distinctness is automatic.

---

## Composes with related META rules

- META_RULE_AX (arm-distinctness across family axis): pre-flight gate enforces this
- META_RULE_AY (verdict-HARD_FAIL on self-reported distinctness False): verdict-emitter enforces this
- META_RULE_Q (suspect-1.000): regime selection (lower N + higher load + noise) prevents this
- META_RULE_AW (seed-config-identical): all 3 seeds use same regime
- META_RULE_AU + AV: routed_queue + run_mode=full per dispatched JSON
