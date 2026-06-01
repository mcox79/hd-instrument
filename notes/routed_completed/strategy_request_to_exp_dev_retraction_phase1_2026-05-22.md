# Strategy → Experiment Dev: Retraction framework Phase 1 validation — CHEAPEST mechanism gate

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~22:20 EDT
**Topic**: 5th-attempt Research RETRACTION framework Phase 1 validation
**cap_map state**: v137 (commit `f2774f8`)
**Trigger**: 5th-attempt Research delivered RETRACTION framework P=[0.40, 0.55] with 11/11 constraint score (BEST across 5 attempts); Phase 1 tests cheapest of any attempt (~5-15 min CPU/GPU total)

## Context

5th-attempt Research delivered RETRACTION framework: substrate's chain
composition map ψ: C → C is approximately a RETRACTION (r ∘ r = r) onto
22% subset of codewords. 11/11 constraint score (best across 5 attempts).

**Cycle 136 ENDPOINT_COLLAPSED finding (28/100 distinct ≈ 22%) PRE-VALIDATES**
the retraction image fraction at smoke level. Phase 1 tests provide FINAL
substrate-physics gate.

Honest P=[0.40, 0.55] calibration-deflated from 80% prior refutation rate.

## Phase 1 validation tests (~5-15 min CPU/GPU TOTAL)

### Test 1 — Eigenspectrum check (~5 min CPU)

**`wave14_W_eigenspectrum_check_v1`**:

```python
import numpy as np
# Substrate W matrix at N=65536
eigs = np.linalg.eigvalsh(W)
sorted_eigs = np.sort(np.abs(eigs))[::-1]
gap_ratio = sorted_eigs[1] / sorted_eigs[0]
residual_at_50 = gap_ratio ** 50
```

**Verdict criteria**:
- **EIGSPECTRUM_PERRON_CONFIRMS**: gap_ratio < 0.91 (rank → 0 at L=50 confirmed)
- **EIGSPECTRUM_PERRON_REFUTES**: gap_ratio > 0.95 (spectral collapse mechanism wrong)
- **EIGSPECTRUM_PERRON_PARTIAL**: 0.91 ≤ gap_ratio ≤ 0.95 (marginal)

### Test 2 — Idempotence test (~5 min)

**`wave14_retraction_idempotence_v1`**:

```python
def test_idempotence(W, codebook, L=50):
    """Check if psi ∘ psi = psi (retraction property)."""
    K = codebook.shape[0]
    psi_once = np.zeros(K, dtype=int)
    psi_twice = np.zeros(K, dtype=int)
    for k in range(K):
        psi_once[k] = run_chain_argmax(W, codebook, codebook[k], depth=L)
        psi_twice[k] = run_chain_argmax(W, codebook, codebook[psi_once[k]], depth=L)
    idempotence_rate = float(np.mean(psi_once == psi_twice))
    return idempotence_rate
```

**Verdict criteria**:
- **IDEMPOTENCE_RETRACTION_CONFIRMS**: idempotence_rate > 0.95 (retraction property holds)
- **IDEMPOTENCE_RETRACTION_REFUTES**: idempotence_rate < 0.50 (not a retraction)
- **IDEMPOTENCE_RETRACTION_PARTIAL**: 0.50 ≤ rate ≤ 0.95 (partial retraction)

### Test 3 — Destination profile (~10 min)

**`wave14_retraction_destination_profile_v1`**:

```python
def destination_profile(W, codebook, true_codewords, L=50):
    """Are ψ destinations specifically on a 22% subset?"""
    destinations = []
    for c in true_codewords:
        d = run_chain_argmax(W, codebook, c, depth=L)
        destinations.append(d)
    unique_destinations = set(destinations)
    destination_fraction = len(unique_destinations) / len(codebook)
    return destination_fraction, unique_destinations
```

**Verdict criteria**:
- **DESTINATION_RETRACTION_CONFIRMS**: destination_fraction ∈ [0.15, 0.30] (image set ≈ 22%)
- **DESTINATION_RETRACTION_REFUTES**: destination_fraction > 0.5 OR < 0.10 (destinations spread or extreme)
- **DESTINATION_RETRACTION_PARTIAL**: outside CONFIRMS range but in [0.10, 0.50]

### Test 4 — Combined RM(1,m) algebraic check (~5 min, optional)

**`wave14_retraction_rm1m_alignment_v1`** (Agent S sub-hypothesis):

Check if substrate's W dominant eigenvector v₁ aligns with RM(1,m) subcode
of Kerdock codebook (algebraic identification of image set).

```python
def rm1m_alignment_check(W, codebook, kerdock_rm1m_subset):
    eigvecs = np.linalg.eigh(W)[1]
    v1 = eigvecs[:, -1]  # dominant
    alignment = abs(v1 @ kerdock_rm1m_subset.T)
    return alignment.max(), alignment.mean()
```

**Verdict criteria**:
- **RM1M_ALIGNMENT_CONFIRMS**: alignment max > 0.7
- **RM1M_ALIGNMENT_REFUTES**: alignment max < 0.3

## Priority ordering

1. **Test 2 (Idempotence)** — direct retraction property test; if FAILS, mechanism is REFUTED definitively
2. **Test 1 (Eigenspectrum)** — fastest CPU test; validates spectral collapse aspect
3. **Test 3 (Destination profile)** — quantitative image-fraction match (should be ~22% per cycle 136 ENDPOINT_COLLAPSED)
4. **Test 4 (RM(1,m) alignment)** — algebraic identification (lower priority; specific to Kerdock structure)

## Substrate-product implication

**If Phase 1 PASSES (retraction framework CONFIRMED)**:
- Substrate-physics characterization gains theoretical anchor for FIRST TIME across 5 attempts
- Substrate-novel mechanism class: "deterministic retraction map with 22% image fraction"
- Substrate-product positioning: "substrate's chain composition is structured retraction;
  backward-smoother is the canonical inverse"
- 5-attempt research-after-rejection discipline VINDICATED

**If Phase 1 FAILS (retraction framework REFUTED)**:
- 5 mechanism attempts × 0 success = substrate genuinely unprecedented
- Substrate-physics terminal verdict: "structurally constrained (forward-lossy +
  reverse-invertible), mechanism unknown after 5 attempts; substrate empirically
  beyond ALL published classical-Hopfield-class chain-composition frameworks"
- Substrate-product roadmap continues unchanged (Demo 1 + Demo 2 capstones hold)

**If Phase 1 PARTIAL**:
- Retraction framework directionally right but quantitatively imprecise
- Substrate-physics characterization revised to "approximate retraction with structural
  caveats; mechanism partially understood"

## Total cost

3-4 tests; smoke + FULL = 6-8 runs; ~5-15 min CPU/GPU TOTAL.
**This is THE CHEAPEST Phase 1 across 5 attempts** — single eigenspectrum
extraction + idempotence test + destination profile.

## Per [[feedback-no-papers-product-only]]

All 4 tests substrate-product oriented (substrate-physics characterization
feeds substrate-product narrative). Phase 1 is FINAL substrate-physics gate
per user signal "may be the LAST mechanism diagnosis attempt" cycle 134.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 15-30 min per recent Exp Dev pickup
pattern.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
