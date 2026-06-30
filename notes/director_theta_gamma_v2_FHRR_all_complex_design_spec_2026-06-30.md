# Theta-gamma phase binding v2 design spec — FHRR all-complex codebook

**Filed:** 2026-06-30 19:25 UTC
**Audience:** hdi_exp_dev (next cell-author)
**Motivation:** a24de6ad's theta-gamma v1 honest-abort at smoke: K_SEQ=50 cyclic-shift baseline saturates 1.000 (regime too easy or hybrid bipolar+phase implementation wrong). Phase arms degraded to 0.10-0.30. Cell-author flagged need for "FHRR all-complex codebook redesign."

---

## v1 failure analysis

v1 used HYBRID encoding: bipolar HD vectors (real-valued ±1) + phase-only sequence binding. The phase binding tried to encode sequence position by multiplying bipolar HD by a complex-phase factor, but the resulting hybrid representation didn't have consistent complex semantics:

- Bipolar binding (cyclic shift) saturated at K_SEQ=50 (too easy)
- Phase arms degraded to 0.10-0.30 (representation broken)
- The mixing of bipolar real-values with complex phases produced a non-standard form that neither binding op handled cleanly

---

## Brain mechanism reminder (what we're modeling)

In hippocampus + cortex, items are bound to sequence position via **theta-gamma coupling**:
- Theta rhythm (~6-10 Hz) provides a cycle
- Each theta cycle contains 5-7 gamma bursts (40-100 Hz)
- Items at distinct gamma phases within a theta cycle are bound into sequence position
- This is HOW the brain encodes "first this, then that, then that" without needing extra dimensions

Mathematical analog: items are encoded as **complex-valued HD vectors** (FHRR); sequence position is encoded as a **phase rotation** that gets element-wise multiplied with the item HD. The full sequence representation is the SUM of phase-multiplied items.

---

## v2 design: all-complex FHRR

### Codebook

```python
# All codes are complex64 with unit-magnitude per element
def make_fhrr_codebook(n_items: int, n_dim: int, rng) -> np.ndarray:
    """Random unit-phase complex codebook [n_items, n_dim] (complex64)."""
    phases = rng.uniform(0, 2 * np.pi, size=(n_items, n_dim))
    return np.exp(1j * phases).astype(np.complex64)

def make_phase_codebook(n_positions: int, n_dim: int, rng) -> np.ndarray:
    """Random unit-phase position codes [n_positions, n_dim]."""
    return make_fhrr_codebook(n_positions, n_dim, rng)
```

### Theta-gamma phase binding

```python
def theta_gamma_bind(item_hd_complex, position_hd_complex):
    """Element-wise complex multiplication = phase addition.
    
    Mathematically: bind = item * position; result has phase = phase(item) + phase(position).
    This is the FHRR canonical binding op.
    """
    return item_hd_complex * position_hd_complex

def theta_gamma_unbind(bound_hd_complex, position_hd_complex):
    """Inverse: bound * conj(position) = item * position * conj(position) = item (when position is unit-magnitude)."""
    return bound_hd_complex * np.conj(position_hd_complex)
```

### Sequence encoding

```python
def encode_sequence(items_hd_complex, positions_hd_complex):
    """Bundle phase-bound items into one sequence HD.
    
    seq = sum_i(items[i] * positions[i])  -- complex sum; result is complex
    """
    return (items_hd_complex * positions_hd_complex).sum(axis=0)

def decode_sequence_at_position(seq_hd_complex, position_hd_complex, item_codebook_complex):
    """Recover item at given position.
    
    1. Unbind: candidate = seq * conj(position)
    2. Cleanup: argmax over codebook similarity
    
    Similarity = abs(<candidate, codebook[i]>) for complex inner product.
    """
    candidate = seq_hd_complex * np.conj(position_hd_complex)
    # Inner product in complex space; take magnitude (rotation-invariant similarity)
    scores = np.abs(item_codebook_complex.conj() @ candidate)
    return int(np.argmax(scores))
```

### Theta-gamma nested rhythm

The full brain mechanism nests gamma INSIDE theta:
- Theta cycle index `t` ∈ {0, 1, ..., n_theta_cycles - 1}
- Gamma phase within theta `g` ∈ {0, 1, ..., n_gamma_per_theta - 1}
- Item at (t, g) gets position code = theta_code[t] * gamma_code[g]

```python
def theta_gamma_nested_encode(items, theta_assignments, gamma_assignments,
                              theta_codebook, gamma_codebook):
    """Items at (t, g) bound to theta_code[t] * gamma_code[g]; sequence = sum."""
    position_codes = theta_codebook[theta_assignments] * gamma_codebook[gamma_assignments]
    return (items * position_codes).sum(axis=0)
```

### Arms

```python
ARMS = [
    "NO_POSITION",            # bundle items without position binding (chance baseline)
    "CYCLIC_SHIFT",           # v1's bipolar baseline (real-valued; sat at K=50)
    "FHRR_FLAT_PHASE_8",      # FHRR all-complex; flat position; 8 distinct phases
    "FHRR_FLAT_PHASE_32",     # 32 distinct phases (more positions)
    "FHRR_NESTED_THETA_GAMMA", # nested theta(8) * gamma(8) = 64 positions
]
```

### Discriminator

HARD_PASS:
- FHRR variants discriminate K_SEQ cliff differently than CYCLIC_SHIFT (log2 separation ≥ 0.3)
- All 5 arms produce DISTINCT K_SEQ cliffs (cross-arm |Δ| ≥ 0.1)
- mechanism_hash distinct per arm (META_RULE_AX)
- NESTED arm shows distinct cliff from FLAT_PHASE_64 (nesting actually helps)
- cv across seeds ≤ 0.10
- No suspect-1.000 saturation at K_SEQ ≤ 50 (META_RULE_Q)

MIDDLE_BAND:
- Some FHRR variants discriminate but ≤ 3 of 5 arms differ
- NESTED not significantly better than FLAT (theta-gamma doesn't add)

HARD_FAIL:
- All arms saturate at K_SEQ=50 (regime too easy)
- All FHRR variants identical to CYCLIC_SHIFT (encoder not wired)
- META_RULE_AX fails (arm hashes collide)

### Regime to avoid saturation

v1 had CYCLIC_SHIFT saturating 1.000 at K_SEQ=50 N=2048. v2 needs higher difficulty:

```python
K_SEQ_SWEEP = [50, 100, 200, 500, 1000, 2000]  # push past v1's max
N_DIM = 4096                                    # smaller N (less capacity headroom)
ITEM_VOCAB_SIZE = 10000                         # larger vocab (more discrimination)
POSITION_SLOTS = 64                             # for FHRR phases; matches NESTED THETA*GAMMA
NOISE_SIGMA = 0.05                              # add noise at retrieval
```

### Queue + timeout

- Queue: overnight_queue (GPU; complex matmul-bound)
- Timeout: 1800s/seed (5 arms × 6 K_SEQ values × ~1s/cell = ~30s; 60x headroom)
- 3 seeds [7, 13, 19]
- META_RULE_AW: identical (N_DIM, K_SEQ_SWEEP, ITEM_VOCAB, POSITION_SLOTS, NOISE_SIGMA, arms) across seeds

---

## Effort estimate

- Cell core (`_substrate_theta_gamma_v2_FHRR_all_complex_core.py`): ~300 LoC (FHRR codebook + binding/unbinding + sequence encode/decode + 5 arms + verdict)
- Per-seed cell entries (3 files): ~120 LoC total
- Pre-reg: ~100 lines
- **Total ~520 LoC; estimated 2-3 hr authoring**

Smaller than ANCHOR 4 v4 (~720 LoC) because the FHRR primitives are mathematically clean (one binding op = element-wise complex multiply); no encoder-family branching.

---

## Composes with substrate phase diagram axes (per `notes/director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`)

- Axis I (Sequence encoding): goes from positional-shift-only to FLAT-phase + NESTED-phase (2 new primitives)
- Axis J (Order binding): goes from cyclic-shift only to FHRR phase-multiply (1 new primitive)
- Axis A (Vector type): exercises FHRR genuinely (v3 dense triplet phantom caught binary_bipolar/hrr_real/fhrr collapsing; v2 here uses FHRR ALONE end-to-end so the encoder MUST flow into the metric)

If HARD_PASS: a single cell promotes 3 axis families from "untested at chain-grade" to "1 of 4-6 primitives CG." Substantial TRUE phase diagram coverage gain.

---

## Composes with theta-gamma biology + Stage 1 sequence binding

- Sequence binding K-cliff (Stage 1) chain-grade primitive exists at positional shift
- v2 here adds theta-gamma phase binding as alternative primitive
- If NESTED arm HP: confirms brain-grounded theta-gamma rhythm is more efficient than positional shift for long sequences (K_SEQ > 200)
- If only FLAT_PHASE arm HP: confirms FHRR phase binding is competitive with cyclic shift; nesting adds nothing
- Brain analog: each theta cycle holds 5-7 gamma items; allows compositional sequence representations
