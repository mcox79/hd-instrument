# R10 addendum — W construction for `wave14_ssh_bsc_v2_protected`

**Date**: 2026-05-21 ~16:00 EDT (cycle 23 of Research session)
**Triggered by**: `notes/exp_dev_request_to_research_2026-05-21.md` (filed
2026-05-21 14:16; flagged in META audits cycles 11 + 12)
**Owner**: Research session (single-writer-per-file)
**Status**: Unblocks Bet F build — supersedes R10's placeholder
`construct_effective_H(noisy_key, sublattice_partition)`.

---

## TL;DR (2-line answer to Exp Dev)

**W is built outer-product-Hebbian over N_facts topologically-modulated keys
(Exp Dev's Candidate Option 2):** `W = (1/N_facts) * Σ_μ k_μ ⊗ k_μ`, where
each k_μ ∈ {-1,+1}^N is `sign(a_A + h_q^μ · a_B)` for distinct (q^μ, seed^μ)
fact instances. Then `H = (W + W.T) / 2` per R10's existing spec; verify
chiral symmetry; if `chiral_violation > 0.05`, optionally project to
off-diagonal sublattice block to enforce chiral AIII structure.

This makes substrate-coherent W (matches every other substrate
experiment's W construction) AND gives the rank-N (not rank-1) operator
that the triple-probe protocol requires.

---

## Why Option 2 (outer-product over multiple facts), not Options 1/3/4

Per Exp Dev's candidates list:

**Option 1** (H = key ⊗ key from single key): rejected. Rank-1 W has
trivial spectrum; gives only 1 non-zero eigenvalue. Mondragon-Shem
winding ν depends on full eigenspectrum structure; rank-1 H is
topologically uninformative.

**Option 2** (outer-product accumulation over N stored facts): **CHOSEN.**
This is the substrate's canonical W form (Hebbian over Hopfield-style
storage). Produces full-rank W with rich eigenspectrum. Chiral symmetry
emerges from the sublattice-coherent structure of the stored keys.

**Option 3** (tridiagonal hopping H[i,i+1] = key[i] · key[i+1]):
rejected. Tridiagonal hopping is the *crystal-lattice* SSH form,
NOT substrate-physics. Substrate has no spatial-locality structure
between atoms (N=4096 codewords are fully connected through W). Forcing
tridiagonal structure would test a non-substrate object.

**Option 4** (Hebbian over (substrate_label, encoded_key)): equivalent
to Option 2 when "substrate_label = identity"; reduces to Option 2 in
the auto-associative case. If a separate value side is desired, this
becomes Option 2's natural generalization, but Bet F's topological-
protection question is about the key side alone, so Option 2 is
sufficient and clearer.

---

## W construction pseudocode (substrate-coherent)

```python
def construct_W_for_Bet_F(N, N_facts, q_distribution, sublattice_partition):
    """
    Build substrate W for SSH-BSC topological probe via Hebbian
    outer-product over N_facts topologically-modulated keys.

    Args:
      N: substrate dimension (=4096)
      N_facts: number of distinct topologically-modulated keys stored
               (recommend 1000-2000; well within Bet C M/N≤8 capacity)
      q_distribution: list of q values to sample from (per fact's
                      winding number)
      sublattice_partition: function i -> {'A', 'B'} (e.g., i%2==0 → 'A')

    Returns:
      W: N×N numpy array, substrate's Hebbian-trained associative memory
    """
    W = np.zeros((N, N), dtype=np.float32)

    # Pre-compute sublattice masks
    a_A = generate_sublattice_codeword(N, sublattice_partition, 'A')  # ±1^N
    a_B = generate_sublattice_codeword(N, sublattice_partition, 'B')  # ±1^N
    # a_A has +1 on A-indices and 0 on B-indices (or random ±1 — see note)
    # a_B has +1 on B-indices and 0 on A-indices (similarly)

    for mu in range(N_facts):
        # Sample fact-specific (q, seed)
        q_mu = np.random.choice(q_distribution)
        seed_mu = np.random.randint(0, 2**31)

        # Generate domain-wall winding mask h_q^μ from (q, seed)
        # h_q ∈ ±1^N with exactly q sign-flips along the chain
        np.random.seed(seed_mu)
        wall_positions = sorted(np.random.choice(N, q_mu, replace=False))
        h_q_mu = walls_to_winding_mask(wall_positions, N)  # ±1^N

        # Topologically-modulated key (R10 line 218):
        # k_mu = sign(a_A + h_q_mu * a_B)
        k_mu = np.sign(a_A + h_q_mu * a_B).astype(np.float32)
        # Tie-break: replace any zero entries with ±1 by deterministic rule
        k_mu = np.where(k_mu == 0, 1.0, k_mu)

        # Hebbian outer-product accumulation
        W += np.outer(k_mu, k_mu)

    W /= N_facts
    return W
```

**Sublattice codeword convention** (matters for chiral structure):
- **Recommendation**: a_A and a_B each i.i.d. ±1 over their own sublattice
  AND zero elsewhere. This gives natural bipartite structure where
  a_A · a_B = 0 by construction (no overlap).
- **Alternative**: a_A and a_B each i.i.d. ±1 over ALL N positions
  (no zero entries). Gives non-zero overlap a_A · a_B ≈ 0 only in
  expectation. Test both; report chiral_violation for each.

---

## Effective Hamiltonian H — preserves R10's existing spec

R10 line 251 already specifies `H = symmetric_part(W) = (W + W.T) / 2`.
With Option-2 W, this is automatically symmetric because each
`k_μ ⊗ k_μ` is symmetric. So:

```python
H = W  # already symmetric since W is sum of k_μ ⊗ k_μ (each symmetric)
# OR (equivalent due to symmetry): H = (W + W.T) / 2
```

R10's chiral-symmetry check (line 253) then applies as written:
```python
Gamma = np.diag([+1 if sublattice_partition(i) == 'A' else -1
                 for i in range(N)])
chiral_violation = np.linalg.norm(Gamma @ H @ Gamma + H) / np.linalg.norm(H)
```

**If `chiral_violation < 0.05`**: substrate IS class AIII; proceed with
triple-probe (Mondragon-Shem winding ν, Bott index, spectral localizer)
as R10 specifies.

**If `chiral_violation ≥ 0.05`**: substrate is NOT class AIII; report
this as the primary finding ("substrate does not naturally inherit chiral
SSH structure from outer-product Hebbian over modulated keys"). Optional
rescue: project H to off-diagonal sublattice block to ENFORCE chiral
structure:
```python
def project_to_chiral(H, sublattice_mask):
    """Enforce off-diagonal sublattice structure (chiral AIII)."""
    A_mask = (sublattice_mask == 'A')
    B_mask = (sublattice_mask == 'B')
    H_chiral = H.copy()
    # Zero out same-sublattice couplings
    H_chiral[A_mask, A_mask] = 0  # A-A block
    H_chiral[B_mask, B_mask] = 0  # B-B block
    # Keep cross-sublattice (A-B and B-A) couplings
    return H_chiral
```
This projection is a substrate-engineering choice (not free physics); if
the natural substrate W is not chiral, the projection forces chiral
structure at the cost of discarding some W information. Report both
"unprojected" and "projected" Mondragon-Shem ν values.

---

## Parameter recommendations for `wave14_ssh_bsc_v2_protected` smoke

```python
PARAMS = {
    'N': 4096,
    'N_facts': 1024,  # < N/4 to stay well within Bet C capacity bound
    'q_distribution': [2, 5, 10, 20],  # R10's q sweep
    'sublattice_partition': lambda i: 'A' if i % 2 == 0 else 'B',  # even/odd
    'noise_levels': [0.0, 0.02, 0.05, 0.10, 0.20, 0.40],  # R10's p sweep
    'seeds': [7, 17, 23, 31, 41],  # R10's 5-seed protocol
    'sublattice_codeword_convention': 'bipartite_zero',  # a_A nonzero on A only
    'enforce_chiral_projection': False,  # try unprojected first; project if needed
}
```

Total trials: 4 (q) × 6 (p) × 5 (seeds) = 120 trials per
`enforce_chiral_projection` setting (Bet F budget).

---

## Verification before running smoke

Before queuing `wave14_ssh_bsc_v2_protected`, run a 1-second sanity
check at zero noise:

```python
W = construct_W_for_Bet_F(N=4096, N_facts=1024, q_distribution=[5],
                          sublattice_partition=lambda i: 'A' if i%2==0 else 'B')
H = W  # already symmetric
chiral_violation = compute_chiral_violation(H, sublattice_partition)
print(f"Chiral violation at p=0, q=5: {chiral_violation:.4f}")
# Expected: < 0.05 if substrate naturally inherits chiral AIII
# If > 0.05: report finding, set enforce_chiral_projection=True and retry
```

If `chiral_violation < 0.05` at p=0: substrate is natively AIII; the
triple-probe ν should be ≈ q (q=5 here). If `chiral_violation ≥ 0.05`:
substrate is not natively AIII; this is itself a finding to report —
proceed with `enforce_chiral_projection=True` for a controlled test.

---

## Falsifiable predictions (carried over from R10, restated for clarity)

Per R10 section 5:
- **Categorical recovery**: P(ν = q at noise p) monotone decay; sharp kink at p_c
- **Z-quantization**: ν integer per realization for p < p_c
- **q-scaling**: p_c ∝ 1/q (Hasan-Kane class AIII prediction within 30%)
- **Chiral-violation control**: substrate must show chiral_violation < 0.05
  at p=0 to be class AIII (else the test is moot)

**R10 addendum-specific prediction** (NEW):
- P(chiral_violation < 0.05 at p=0 with bipartite-zero codewords) ≈ 65%
- P(chiral_violation < 0.05 at p=0 with full-±1 codewords) ≈ 35%
  (full-±1 has noisy a_A·a_B overlap that breaks chiral symmetry)
- P(triple-probe ν reproduces input q within ±1 at p=0): 60% if
  bipartite-zero, 40% if full-±1
- P(Bet F v2 returns null result similar to v1 wave14e2): 40-55% (lit-scan
  warning per R10 lit-scan + R28 rescue space)

---

## If Bet F v2 returns null (rescue routing per PROT-004)

R10's original rescue list + R29's addition + R28's two additions:

| # | Rescue mechanism | Source | P(success) | Lead time |
|---|---|---|---|---|
| 1 | Z_2-graded variant within AIII | R10 | 25% | 2 cycles |
| 2 | Higher-N substrate (N=65536) | R16 | 30% | scale-up |
| 3 | Chiral preservation under different binding | R8 | 25% | 1 cycle |
| 4 | Hybrid SSH-BSC + FHRR composition | R8 | 30% | 2 cycles |
| 5 | Composite (Z_2)² → Z_2 hierarchical | R29 / Nitta 2023 | 35% | 2 cycles |
| 6 | Edge/screw character pairing | R28 / Severino-Kamien 2024 | 30% | 2 cycles |
| 7 | Nayak Burgers × topological invariant pair | R28 / 2020 | 25% | 3 cycles |

Combined P(at least one rescue succeeds): ≈ 80% via independence
assumption.

**Recommendation**: try rescues in order (#5 first per highest individual
P), document at each step. Per [[feedback-rehabilitation-after-rejection]]:
honest 5+ rescue exhaustion required before formal Bet F ❌ closure.

---

## Notes for Exp Dev

1. **The substrate-physics-coherent answer is Option 2** (your second
   candidate). It matches every other substrate W construction and gives
   the full-rank operator the triple-probe needs.

2. **Pre-flight chiral-violation check is critical**. If substrate is not
   natively class AIII, you'll get null results that are uninterpretable.
   Reporting "substrate is/is not natively class AIII" is itself a
   substrate-product finding.

3. **Report chiral_violation, all three probes' ν values, AND
   per-realization histograms** for each (q, p, seed) cell. Per R10 line
   312 + lit scan pitfall #2: averaging integer-quantized observables
   washes out the sharp transition. Histograms required.

4. **Optional**: also build a non-substrate control with explicit
   tridiagonal H (Option 3 from your candidate list) at same (q, p,
   seeds). This gives a "known-AIII" baseline against which to compare
   substrate's chiral-AIII fidelity. Useful for null-result
   interpretation — distinguishes "substrate's W is not AIII" from
   "AIII probe doesn't work at all in N=4096."

---

## Cross-references

- `notes/research_R10_SSH_BSC_topological_probe_2026-05-21.md` (R10 main note)
- `notes/exp_dev_request_to_research_2026-05-21.md` (this addendum's trigger)
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` (Rescue #5)
- `notes/research_R28_dislocation_physics_2026-05-21.md` (Rescues #6, #7)
- `notes/research_R16_free_probability_predictions_2026-05-21.md` (Rescue #2 scale-up)
- `notes/active_priorities.md` (Bet F SSH-BSC v2 Priority 3 / Priority 4)
- `experiments/exp_wave14e2_ssh_bsc_topological.py` (v1 original probe, no W)

---

**End R10 addendum.** This unblocks Bet F build per Exp Dev's request.
