# Pre-registration: wave14y_erase_kerdock_v3

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14y_erase_kerdock_v3.py](../experiments/exp_wave14y_erase_kerdock_v3.py)
Priority source: follow-up to [wave14v_erase_kerdock_v2](../experiments/exp_wave14v_erase_kerdock_v2.py)
verdict `KERDOCK_V2_OVERCAPACITY_PASS` (validated at M_stored ≤ 2N)
Author: experiment_dev session, pipeline tick 10

## Why

v2 with the 2-coset codebook validated multi-probe Mirage protection
through M_stored=2N=8192. The codebook ran out at 2N. To extend the
envelope further requires more cosets.

v3 builds a 4-coset codebook (4N=16384 codewords) and tests M_stored in
{8192, 12288, 16384} = {2N, 3N, 4N}. Same comparison: Kerdock arm with
snap vs correlated-key arm.

## Codebook construction (4-coset via Maiorana-McFarland)

Same idea as v2 but with 4 cosets, using the Maiorana-McFarland (MM)
construction for guaranteed pairwise nondegeneracy.

**MM setup.** For N = 2^k with k = 2t (even), index each bit position
x ∈ {0,1}^k by splitting it into x_lo = lower t bits, x_hi = upper t
bits. Treat each as an element of GF(2)^t = GF(2^t) (identifying bit
vectors with field elements via the polynomial representation).

For any b ∈ GF(2^t), define

    Q_b(x) = x_lo · (b * x_hi) over GF(2)

where * is GF(2^t) multiplication and · is dot product over GF(2).

**Properties:**
- For b = 0: Q_0(x) = 0 (the trivial quadratic; coset 0 is just H).
- For any b ≠ 0: Q_b is bent — |Walsh(Q_b)(d)| = 2^{k/2} for all d.
- For any b ≠ c: Q_b - Q_c = Q_{b-c} (since the construction is
  GF(2^t)-linear in b), so Q_b - Q_c is also bent when b ≠ c.

This gives 2^t MM bent functions, parameterized by b ∈ GF(2^t), with
ALL pairwise differences also bent. The Kerdock-style nondegeneracy
condition (Welch-bound pairwise IPs) holds for any subset.

**For v3 we use 4 cosets** chosen as b ∈ {0, 1, α, α^2} where α is a
primitive element of GF(2^t). All 6 pairwise differences are nonzero
elements of GF(2^t) (since these 4 elements are linearly independent
modulo subtraction). All 6 differences are bent by the property above.
The codebook is:

    [H ; H ⊙ q_1 ; H ⊙ q_α ; H ⊙ q_{α^2}]    (shape 4N × N)

where q_b[x] = (-1)^{Q_b(x)} and ⊙ is row-wise element-wise multiply.

**For full mode** (N = 4096, k = 12, t = 6): GF(2^6) with primitive
polynomial p(x) = x^6 + x + 1. α = 2 in integer rep.

**For smoke** (N = 1024, k = 10, t = 5): GF(2^5) with primitive
polynomial p(x) = x^5 + x^2 + 1. α = 2 in integer rep. (Note: smoke
uses N=1024 instead of v1/v2's N=512 because MM requires even k; k=9
at N=512 is odd.)

**Verification (smoke oracle):** the constructed codebook should have
- within-coset max |IP|/N < 1e-6 (Hadamard rows are orthogonal; q_b
  multiplies all rows by the same sign vector and preserves orthogonality)
- max |IP|/N across ALL pairs (4*N choose 2 = 32M pairs at full) equal
  to exactly 2^{k/2}/N = 1/sqrt(N) (Welch bound). For N=4096: 1/64.

## Hypothesis

At N=4096 with the 4-coset codebook, M_stored sweep {8192, 12288, 16384}
(= {2N, 3N, 4N}), 5 seeds:

- Kerdock arm passes all 5 Mirage probes at every M_stored.
- Correlated-key arm (rank-L bottleneck) fails at every M_stored ≥ N.

## Multi-probe success criteria (per M_stored)

Same five as v1/v2, at α=1.0:

1. argmax_leak < 0.05
2. mean_rank > M_stored × 0.3
3. norm_ratio < 0.15
4. paraphrase_leak < 0.05 at Hamming h=8 (with snap for Kerdock arm)
5. kept_preservation > 0.95

For PASS verdict: Kerdock arm passes all 5 at every M_stored AND
Correlated arm fails ≥ 2 of {rank, norm, paraphrase} at any M_stored.

## Kill criterion

- Kerdock arm fails at M_stored=4N (= 16384): structured-keys
  protection bounded somewhere in (2N, 4N]; closes the v3 envelope.

(With MM construction the codebook is guaranteed bent by construction;
no "construction-failed" branch.)

## Verdict labels (4)

- `KERDOCK_V3_EXTENDS_TO_4N` — Kerdock arm passes through M=4N; envelope
  extends to 4N=16384 at N=4096
- `KERDOCK_V3_DECAYS_AT_<M>` — Kerdock fails at some M > 2N; envelope
  sized in (2N, M)
- `KERDOCK_V3_CORRELATED_PASSES` — control arm unexpectedly passes;
  audit setup (matches the v2 contrast check)
- `KERDOCK_V3_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. Codebook cross-coset max IP is exactly the Welch bound: 1/sqrt(N).
   For N_smoke=1024 (k=10): 1/32 = 0.03125. Tight band: (0.030, 0.033).
   For N_full=4096 (k=12): 1/64 = 0.015625.
2. Within-coset IPs near zero: max |IP|/N < 1e-6 (each coset = H rows
   element-wise multiplied by a single sign vector q_b; orthogonality
   of H rows is preserved).
3. All 4 b values produce distinct codewords (full codebook has 4N
   distinct rows): pairwise IP between H[a] and (H ⊙ q_b)[a] is
   (1/N) sum (-1)^{Q_b(x)} = (1/N) Walsh(Q_b)(0). For nonzero b, this
   has |value| = 1/sqrt(N). So they're distinct from H rows.
4. Snap-to-codebook identity check (already used in v2): snap(c) = c
   for c in the codebook.

## Pre-mortem (3 failure causes)

1. **GF(2^t) arithmetic bug**: simple polynomial-reduction error
   could make multiplication incorrect, breaking the MM bent property.
   Mitigation: smoke oracle 1 checks the Welch bound exactly; if it's
   off, GF arithmetic is wrong.

2. **Snap-to-codebook at 4N=16384 codewords is more compute-heavy**:
   per snap = matmul (B, N) @ (4N, N).T = B × 4N similarities. At
   B=600 paraphrases per erase × 5 erases × 5 seeds × ... still
   feasible (~16M ops per snap × O(thousands) snaps = ~16 G ops on
   GPU). Should be <1 min.

3. **Multi-probe inflation at M=4N**: with 16384 stored values, the
   rank threshold = M*0.3 = 4915. Achieving mean_rank > 4915 across
   30 erased items is possible only if anti-Hebbian erase actually
   pushes v_e past rank 4915 in the M-codebook. Per v2: at M=8192,
   mean_rank was over 0.3*8192 = 2458. Scale to M=16384, expectation
   is ~4900+ if the structure holds. If it doesn't, decay verdict.

## Operational definition

Reuses v2 functions: `make_kerdock_2coset_codebook` (extended to 4
cosets), `snap_to_codebook_batch`, `multi_probe_with_snap`, and v1's
`make_correlated_keys`, `antihebbian_erase`, `hamming_perturb`.

New helper: `make_kerdock_4coset_codebook(N, gen_cpu, max_attempts=50)`
- Build coset 0 = H, coset 1 = H * q_1 (canonical)
- Sample Q_2, Q_3 from random off-diagonal upper-triangular binary
  matrices
- Verify all 6 pairwise XOR quadratics nondegenerate (via Walsh-FHT amp check)
- Return stack of 4 cosets (4N codewords)

## Cited mechanism / sources

- Same as v2 plus:
- Hammons-Kumar-Calderbank-Sloane-Solé 1994 — full Kerdock with 2^(m+1)
  cosets, of which v3 uses 4 (a sparse subset)
- Walsh-Hadamard nondegeneracy check: standard signal-processing tool;
  a quadratic form Q over GF(2)^k is "bent" (max nonlinearity) iff its
  Walsh spectrum is flat at 2^(k/2)

## Expected runtime

- Smoke (N=512, M_stored=[256, 1024, 2048], 1 seed, 1 hamming, 2 arms):
  ~5-10 s
- Full (N=4096, M_stored=[8192, 12288, 16384], 5 seeds, 3 hamming, 2
  arms): estimated 3-7 min on GPU

## What product decision this enables

- `EXTENDS_TO_4N` → cap_map Bet 2 envelope upgrades to M ≤ 4N. Strong
  product claim.
- `DECAYS_AT_<M>` → explicit envelope in (2N, 4N).
- `CODEBOOK_FAILED` → routes to proper finite-field Kerdock construction
  next cycle (engineering work, not substrate issue).
