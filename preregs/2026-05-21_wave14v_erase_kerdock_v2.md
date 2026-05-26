# Pre-registration: wave14v_erase_kerdock_v2

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14v_erase_kerdock_v2.py](../experiments/exp_wave14v_erase_kerdock_v2.py)
Priority source: follow-up to [wave14r_erase_orthkeys_v1](../experiments/exp_wave14r_erase_orthkeys_v1.py)
(STRUCT_KEYS_FIX_MIRAGE) + [wave14r_orthkeys_capsweep](../experiments/exp_wave14r_orthkeys_capsweep.py)
(CAPSWEEP_ROBUST); R1 Variant 2A.i full implementation
Author: experiment_dev session, pipeline tick 7

## Why

Bet 2 v1 + capsweep validated FIX_MIRAGE for Hadamard-orthogonal keys at
M_stored ≤ 3200 (≤ 0.78 × N=4096). That whole envelope is BELOW the
orthogonal codebook capacity (M ≤ N). The remaining question is:

**Does multi-probe Mirage protection survive at M_stored > N when using a
Welch-bound structured codebook?**

R1's recommendation was Kerdock K(m) with snap-to-codebook paraphrase
semantics. The full Kerdock K(11) has 2^22 codewords of length 2^12=4096.
v2 implements a tractable subset: the **2-coset Kerdock-like codebook**
(2N = 8192 codewords), which gives the right cross-talk structure for
testing M_stored up to 2N.

This is the load-bearing test of R1's "structured keys break Mirage via
bounded pairwise inner products." If Kerdock breaks Mirage at M > N
while random ±1 does not, the cap_map row gets ✅ with envelope M ≤ 2N.
If both break or both survive, the structural-keys story needs revision.

## Codebook construction (the load-bearing math)

For N=2^(m+1) (here m+1=12, N=4096):

- **Coset 0**: N rows of the Sylvester Hadamard matrix H. Each row a is
  the codeword c_{a,0}[x] = (-1)^{<a,x>} where <a,x> is the bit dot-product
  mod 2. All pairwise inner products within coset 0 are exactly 0 (rows
  of H are orthogonal).
- **Coset 1**: the same N rows multiplied element-wise by the quadratic
  sign vector q_1[x] = (-1)^{Q_1(x)} where Q_1(x) = x_0·x_1 + x_2·x_3 + ...
  + x_{m-1}·x_m is the canonical nondegenerate quadratic boolean form.
  Within-coset-1 pairs are orthogonal (q_1 is the same factor for all
  rows in coset 1, so the IP equals the within-coset-0 IP which is 0).
- **Cross-coset pairs** (one from coset 0, one from coset 1): IP/N = the
  Walsh transform of q_1 at the bit-XOR of the two row indices. For
  nondegenerate Q_1 (m+1 even), |Walsh(q_1)| = 2^{(m+1)/2} for all inputs.
  So |IP|/N = 2^{(m+1)/2} / N = 2^6 / 2^{12} = **1/64** exactly. This is
  the Welch bound for binary codes at this length.

The 2-coset codebook is a subset of full Kerdock K(11) (which spans 2^22
codewords across many cosets). 2 cosets suffice for testing M_stored ≤ 2N.

## Hypothesis

At N=4096 with the 2-coset Kerdock codebook, M_stored sweep
{2000, 4096, 6144, 8192} (covering 0.5N, 1N, 1.5N, 2N), 5 seeds:

- The Kerdock arm preserves all 5 Mirage probes at every M_stored.
- The random ±1 control arm fails at least one Mirage probe at M_stored
  ≥ N (because typical pairwise IP max grows with M, exceeding Welch
  bound for random keys).
- At M_stored = 2000 (below N), both arms pass (replicates v1).

The cross-coset IP=1/64 is the critical structural constant: it's
*exactly* the typical IP of random ±1 keys at this N (1/√N = 1/64), but
random has Gaussian tails that exceed it. Kerdock pairs are either
exactly 0 or exactly 1/64 — no tails.

## Multi-probe success criteria (per M_stored, all required)

Same five as v1, at α=1.0:

1. argmax_leak < 0.05
2. mean_rank > M_stored × 0.3
3. norm_ratio < 0.15
4. paraphrase_leak < 0.05 at Hamming h=8 (with snap-to-codebook for
   Kerdock arm; raw paraphrase for random arm)
5. kept_preservation > 0.95

For PASS verdict, the Kerdock arm must satisfy all 5 at every M_stored
AND the random arm must fail at least 2 of {rank, norm, paraphrase} at
some M_stored ≥ N (i.e., the contrast must be real, not "both pass").

## Kill criteria

- Kerdock arm fails ≥ 2 deep probes at M_stored = N or 2N: structured-
  keys family does NOT extend to over-capacity regime. Closes the v2
  claim; v1 stays the substrate's only validated envelope.
- Random arm passes all probes at every M_stored: contradicts the v1
  hypothesis (that structure matters); audit setup.

## Verdict labels (5)

- `KERDOCK_V2_OVERCAPACITY_PASS` — Kerdock passes all M, random fails
  somewhere at M ≥ N; v2 hypothesis confirmed.
- `KERDOCK_V2_DECAYS_AT_<M>` — Kerdock works at lower M but fails at
  some over-capacity M; envelope characterized.
- `KERDOCK_V2_KERDOCK_FAILS_TOO` — both arms fail at over-capacity;
  structured-keys family doesn't extend.
- `KERDOCK_V2_RANDOM_SURPRISINGLY_OK` — random arm passes everywhere;
  the v1 finding's mechanism story (Welch-bound matters) needs revision.
- `KERDOCK_V2_INCONCLUSIVE` — missing data.

## Oracle assertions (smoke mode)

1. **Codebook cross-coset IP exactly 1/N_smoke^{1/2}** (= 1/sqrt(N_smoke)).
   `oracle.assert_in_range("cross_coset_max_ip", max_cross_ip,
   (1/sqrt(N) * 0.9, 1/sqrt(N) * 1.1))`. Verifies the Welch-bound
   construction is correct. If off by more than 10%, Q_1 is degenerate
   or the construction has a sign error.
2. **Within-coset IPs are zero**: max within-coset |IP| < 1e-6.
3. **Snap-to-codebook is identity for original codewords**: snap(c) = c
   for c in the codebook (no perturbation). Catches snap bugs.

## Pre-mortem (3 failure causes)

1. **Q_1 not actually nondegenerate**: if Q_1 collapses to a linear form
   for some bit-vector x, the Walsh transform amplitudes won't all be
   2^{(m+1)/2}, and the "exactly 1/64" cross-coset IP claim is wrong.
   Mitigation: oracle assertion 1 catches this.
2. **Snap-to-codebook returns wrong sign**: snap returns the closest
   codeword's *direction* but we need the signed cosine match. If sign
   is wrong, snapped paraphrase reads -v_e instead of +v_e, leak rate
   inflated. Mitigation: oracle 3 catches via identity test.
3. **At M=2N, the codebook IS the substrate's full storage**: substrate
   has 8192 keys stored, codebook has 8192 codewords. Anti-Hebbian erase
   removes one rank-1 atom; remaining 8191 atoms span the same space as
   the codebook. Reads of paraphrases might collapse to ~uniform over
   8192 facts, not zero. This isn't a *bug* but a regime change — what
   does it mean for the verdict?  Decision in prereg: count toward
   verdict normally; verdict_msg notes if this regime fires.

## Operational definition

- N = 4096
- M_stored sweep: {2000, 4096, 6144, 8192}
- Two arms: Kerdock 2-coset + snap; random ±1 + raw paraphrase
- α = 1.0 (validated optimal from v1)
- n_erase = 30, n_kept_probe = 100, n_paraphrase = 20, paraphrase_h ∈ {4, 8, 16}
- 5 seeds
- Erase: same anti-Hebbian rank-1 as v1 (matches wave14q convention)
- Multi-probe: argmax_leak, mean_rank, norm_ratio, paraphrase_leak per h,
  kept_preservation; reported per (arm, M_stored).

## Cited mechanism / sources

1. Hammons-Kumar-Calderbank-Sloane-Solé 1994 — original Kerdock
   construction via Z₄-Gray map.
2. Sylvester 1857 — Hadamard matrix recursive construction; the v2 code
   uses this directly for coset 0.
3. Mirage of Model Editing (arXiv:2503.06991) — multi-probe battery.
4. wave14r_erase_orthkeys_v1 (own work) — v1 STRUCT_KEYS_FIX_MIRAGE that
   this experiment extends to over-capacity regime.

## Expected runtime

- Smoke (N=512, M=300, 1 seed, 1 hamming radius, 2 arms): ~5-10 s
- Full (N=4096, 4 M values, 5 seeds, 4 hamming radii, 2 arms): estimated
  3-7 min on GPU

## What product decision this enables

- `OVERCAPACITY_PASS` → cap_map row "GDPR-grade erase under
  Welch-bound-structured keys at M ≤ 2N" upgrades to ✅. The substrate
  operates beyond orthogonal-codebook capacity.
- `DECAYS_AT_<M>` → envelope sized at the failure M; cap_map row stays
  ✅ with an explicit upper bound.
- `KERDOCK_FAILS_TOO` → structured-keys family is bounded at M ≤ N;
  v1's envelope is the substrate's full erase capability.
- `RANDOM_SURPRISINGLY_OK` → audit v1's contrast; maybe v1's
  "correlated" arm was just a wave14p replication artifact and random
  ±1 doesn't actually break at this scale.
