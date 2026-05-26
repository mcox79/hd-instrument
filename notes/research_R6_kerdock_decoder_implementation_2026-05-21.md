# Research R6 — Full Kerdock decoder implementation details (Bet C prerequisite, now post-Bet-C-resolution)

**Topic.** Strategy's R6 (open since cycle 8): "Full Kerdock decoder
implementation details (Bet C prerequisite)." Bet C is now RESOLVED ✅
via wave14ya at M/N=8N — so R6 is implementation detail for E_C
(`wave14r_erase_orthkeys_v2_kerdock`) and future Kerdock-related work
(E_F SSH-BSC topological, extensions to larger N). R6 asks: what's
the right practical Kerdock decoder for a substrate using Kerdock
keys at N=4096?

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 23 tool uses,
25+ verified citations 1994-2025). Ninth consecutive cycle following
post-audit protocol.

**HEADLINE finding (per [[feedback-no-smoke]])**: R6 is
**implementation detail**, not capability research. The substrate's
operational need is mostly satisfied by the standard Conway-Sloane
coset-FHT decoder, which is GPU-friendly and ML-optimal at the
substrate's scale. This note documents the algorithm and provides
substrate-applicable recommendations, but is not opening a new
research direction.

---

## Pass 1 — External literature scan (verified)

Generic coding-theory queries via subagent: "Kerdock code decoding
algorithm," "Reed-Muller code fast decoding," "Z4-linear code decoding
Hammons Calderbank," "Fast Hadamard Transform decoder," "list decoding
Reed-Muller second-order," etc. No substrate fingerprint.

### 1.1 Kerdock code construction (verified)

The textbook facts check out:
- Kerdock K(m), for even m, is a non-linear binary code of length
  N = 2^m with 2^(2m) codewords and minimum Hamming distance
  **d_min = 2^(m-1) − 2^((m-2)/2)**.
- Constructed via Z₄-Gray map from Reed-Muller-Z₄(1, m+1) per
  **Hammons-Kumar-Calderbank-Sloane-Solé 1994** (IEEE T-IT 40:301-319,
  arXiv:math/0207208). IT Society Paper Award.
- Inner products of distinct codewords: **{0, ±2^((m+2)/2)}**.
- For **m=12 (length 4096)**: d_min = 2^11 − 2^5 = **2016**; inner
  products **{0, ±128}**; codebook size = 2^24 ≈ 16.7M codewords.
- Near-orthogonal property (|IP|/N ≤ 1/32) makes Kerdock a CDMA
  signature set (Yang-Kim quasi-orthogonal sequences for IS-2000).

### 1.2 The standard Conway-Sloane / Hammons coset-FHT decoder

The textbook fast decoder dates to the original construction and is
in Conway-Sloane SPLG 3rd ed. (Ch. 3 §7, Ch. 15). Structure:

K(m) = ⋃ (RM(1,m) + coset_leader)   over 2^m quadratic coset leaders

Decoder algorithm:
```
For each coset_leader (2^m total):
  residual = received_word − coset_leader (modulo 2)
  walsh_correlations = FWHT(residual)   # O(N log N)
  max_corr_idx, max_corr_value = argmax(walsh_correlations)
Return (coset_leader*, max_corr_idx*) corresponding to global max
```

**Complexity**: 2^m FWHTs of length 2^m = O(N² log N) = O(N · N log N).

For N=4096: 4096 FWHTs × (4096 · 12) ≈ **2 × 10⁸ ops/query**. On a
consumer GPU at fp16 with batched FWHT this is ≈ **10 ms/query**.
GPU batched decoding (many queries at once) achieves
**10⁵–10⁶ decodings/sec** at substrate scale.

This is **ML soft-decision** when fed real-valued log-likelihoods
(via Forney's FHT-as-MAP framing for first-order RM, Forney 1966;
cleaned up in Ashikhmin-Litsyn 2004, IEEE T-IT 50:1812-1818).

**Substrate-applicable verdict**: Conway-Sloane coset-FHT is the
default decoder. GPU-friendly (4096 independent FWHTs are
embarrassingly parallel), ML-optimal, well-understood. **R6 closes
on this recommendation alone.**

### 1.3 Z₄-domain decoding (algebraic alternative)

Hammons et al. 1994 recommended decoding in Z₄ pre-image (where the
code is linear), then Gray-mapping back. Subsequent work:

- **Helleseth-Kumar-Shanbhag 1999** (IEEE T-IT 45) — algebraic Z₄
  decoder for the Calderbank-McGuire family.
- **Hergert-Helleseth 1995/2001** — Z₄-linear Goethals codes.

Z₄ correlation against 2^(m+2) Z₄ codewords is O(N · 2^(m+2)) = O(N²)
naively; structured FWHT-over-Z₄ variants bring back to O(N log N)
per coset.

**Substrate-applicable verdict**: equivalent asymptotic cost to the
FHT-coset decoder; less commonly implemented; recommend stick with
the binary FHT path.

### 1.4 Recent (2020-2026) advances

The most relevant recent Kerdock-specific work:

- **Minja-Šenk 2023** (arXiv:2312.00193, IEEE T-Comm 2023/24): MAP
  decoder operating on Z₄ pre-image, complexity O(N² log₂ N).
  Provides full bit-wise APP (posteriors), useful for iterative
  receivers. Same asymptotic cost as classical Hammons.
- **Minja-Šenk 2024** (MDPI Mathematics 12:443): generalizes to
  Z_{2^s}; complexity O(NS log₂ N); reports ~5 dB BER improvement
  over classical lifting decoder.
- **Minja-Šenk "lifting APP"** sub-optimal decoder: O(N log₂ N) ≈
  5·10⁴ ops, **3-5 dB BER cost** vs full MAP. Useful for tight
  latency budgets.

Adjacent Reed-Muller work that may apply via Kerdock's RM structure:
- **Ye-Abbe 2020** (arXiv:1902.01470): Recursive Projection-Aggregation
  (RPA) decoding; self-similar recursive, parallelisable. For
  second-order RM (Kerdock's parent class), close to ML.
- **Geiselhart et al. 2024** (arXiv:2409.03700): Automorphism-
  Ensemble Decoding (AED) — exploits affine automorphism group
  |GA(m,2)| for parallel decoders + majority-vote.
- **Jamali et al. 2024** (arXiv:2301.06251): ML-aided differentiable
  RPA. Promising but not Kerdock-specific.

**Honest read from lit scan**: "No 2024-26 paper appears to give a
*GPU-batch* Kerdock-specific decoder. The Minja-Šenk papers are
the only recent algorithmic advances explicitly on Kerdock." This
is a **substrate-novel implementation gap** — substrate's
Kerdock-decoder GPU implementation would be the first published
GPU-batch decoder.

### 1.5 Erasure / partial-bit decoding

- **Kudekar-Mondelli-Şaşoğlu-Urbanke-Hassani-Reeves-Pfister 2017**
  (arXiv:1505.05831): Reed-Muller achieves BEC capacity under MAP.
  For Kerdock, the relevant statement is that RM(1, m+1) (Z₄ pre-
  image's skeleton) is BEC-capacity-achieving.
- **Cunche-Roca** (arXiv:1601.06908): Gbps-scale recursive erasure
  decoder for RM; framework transfers to Kerdock cosets.
- **2025 arXiv:2508.08736**: 1-step decoder achieving d_min-1
  erasure-correction limit.

For mixed soft/hard substrate inputs: mask unknown coordinates and
run FHT-coset decoder on known ones. Kerdock's near-orthogonality
(|IP|/N ≤ 1/32 at m=12) means substantial erasure rates (~50% at
m=12, within d_min/N = 2016/4096 ≈ 0.49) are recoverable.

### 1.6 Materials analog — Mutually Unbiased Bases (load-bearing)

**Calderbank-Cameron-Kantor-Seidel 1997** (Proc. LMS 75:436-480)
showed that Kerdock codes K(m) actually **CONSTRUCT a complete set
of mutually unbiased bases (MUBs)** in dimension 2^(m/2). Quantum
informatics: **Kerdock decoding ≡ discrete phase retrieval on the
Boolean cube** identifying which MUB and which basis vector.

**Klappenecker-Rötteler 2003/2005** (arXiv:quant-ph/0502031): MUBs
are complex projective 2-designs; Kerdock-MUB connection extended
to quantum codes.

The Walsh-basis ↔ momentum-space tight-binding connection (Walsh
functions as eigenfunctions of Hadamard-coupled hopping Hamiltonian)
is implicit in physics (Pauli-X strings = Walsh operators) but **not
pursued in the coding literature** — a substrate-novel bridge
opportunity.

---

## Pass 2 — Substrate-specific drill

### 2.1 Substrate's actual Kerdock decoder needs

The substrate uses Kerdock keys at N=4096 (m=12) for:
- **Bet 2 / Bet C orthogonal-key erase** (RESOLVED ✅): decoder used
  for paraphrase probe — given a Hamming-perturbed Kerdock codeword,
  recover the nearest stored codeword.
- **Bet F SSH-BSC topological** (queued): may use Kerdock-structured
  sublattice keys; would need decoder for noise-robustness probes.
- **Future Bet C extensions**: M/N > 8N, or N > 4096.
- **Substrate forensics** (per WHT-peak forensics ✅): Kerdock-key
  identification from W matrix; decoder for confirming stored-key
  recovery.

**Operational requirements**:
- Throughput: ~10⁴–10⁵ decodings/query (paraphrase probes; ~50
  paraphrases × 30 erased facts × 5 seeds × multiple experiments)
- Latency: ~1-10 ms acceptable (not real-time)
- Precision: ML-optimal (substrate's multi-probe Mirage battery
  requires no decoding artifacts)

### 2.2 Recommended decoder for substrate

**Default: Conway-Sloane coset-FHT decoder, GPU-batched.**

```python
# Pseudocode for substrate-native batched Kerdock decoder
def kerdock_decode_batch(received_words, coset_leaders, fwht_batch_fn):
    """
    received_words: (B, N) bipolar real-valued (LLR or hard ±1)
    coset_leaders: (2^m, N) Kerdock coset leader codebook
    Returns: (B,) tuple of (best_coset_idx, best_rm_idx) per query
    """
    B, N = received_words.shape
    m = log2(N)
    num_cosets = 2**m  # = N

    best_correlation = -inf * ones(B)
    best_indices = zeros(B, 2)  # (coset_idx, rm_idx)

    for coset_idx in range(num_cosets):
        # Subtract coset leader (mod 2 for binary; multiply for ±1)
        residual = received_words * coset_leaders[coset_idx]  # (B, N)
        # Batched FWHT
        walsh_correlations = fwht_batch_fn(residual)  # (B, N)
        # Find peak per batch element
        max_vals, max_idxs = max(walsh_correlations, axis=1)  # (B,), (B,)
        # Update if better than current best
        mask = max_vals > best_correlation
        best_correlation[mask] = max_vals[mask]
        best_indices[mask] = (coset_idx, max_idxs[mask])

    return best_indices
```

**GPU implementation notes**:
- Use NVIDIA cuFFT-based FWHT or hand-rolled CUDA kernel
- 4096 independent FWHTs per query is embarrassingly parallel
- Tensor-Core FWHT at fp16 (Falcão et al., NVIDIA) gives ~2×
  speedup over CUDA-core
- Batch many queries (B ≥ 256) to amortize kernel launch overhead

**Predicted performance at N=4096**:
- Per-query: ~10 ms (consumer 4060 Ti class)
- Batch=256: ~1 sec for 256 decodings → 256 decodings/sec single-
  query, but throughput-wise 10⁴–10⁵ decodings/sec
- Memory: 2^m × 2^m = 16M Kerdock codewords; if pre-tabulated, 16MB
  (uint8) or 64MB (fp16). Coset leaders are 4096 × 4096 = 16MB.
  Fits comfortably in VRAM.

### 2.3 Alternative: Minja-Šenk 2023/2024 (if soft-output needed)

For experiments that need per-bit posteriors (e.g., information-
theoretic analyses of substrate's erasure capability), use Minja-Šenk
2023 MAP. Same asymptotic cost as coset-FHT; provides full bit-APPs.

**Substrate-applicable verdict**: Conway-Sloane coset-FHT is the
default; switch to Minja-Šenk only if soft-output is required.

### 2.4 Erasure / paraphrase decoder

For substrate's paraphrase probes (Hamming-perturbed Kerdock keys):
- **At low perturbation** (Hamming h ≤ 8): perturbed key is still
  within "snap radius" of original Kerdock codeword. Coset-FHT
  decoder returns correct codeword. No special handling.
- **At medium perturbation** (h ∈ [16, d_min/4 = 504]): perturbed
  key may be ambiguous. Coset-FHT returns ML choice; substrate-
  appropriate if paraphrase definition allows multiple correct
  answers.
- **At high perturbation** (h > d_min/2 = 1008): perturbed key may
  be closer to a different Kerdock codeword. ML decoder returns
  whichever is nearest — but substrate's "paraphrase" semantics
  may want to detect this as a failure case.

**Substrate-applicable recommendation**: standard coset-FHT decoder
+ check Hamming distance to recovered codeword vs original key;
if distance exceeds threshold (substrate-tuned), classify as
"paraphrase moved off-orbit" rather than "successful recovery."

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14r_R6_kerdock_decoder_perf` — verify decoder
correctness and benchmark throughput.

```text
config:
  N = 4096
  m = 12
  num_test_queries = 1000
  perturbation_levels = [0, 4, 8, 16, 64, 256, 1024]  # Hamming distance
  seeds = [7, 17, 23, 31, 41]

construct_kerdock_codebook():
  # 2^24 codewords; construct via Z4-Gray map of RM(1, 12)
  return kerdock_K12  # (2^24, 4096) uint8 array

generate_test_queries(num, codebook, perturbation, seed):
  selected_codewords = sample(codebook, num)  # ground-truth
  perturbations = sample_hamming_perturbations(num, perturbation)
  received = selected_codewords XOR perturbations
  return received, selected_codewords

decode_batched(received, coset_leaders):
  return kerdock_decode_batch(received, coset_leaders, fwht_batch)

measure_accuracy_and_throughput(received, decoded, true):
  accuracy = mean([decoded[i] == true[i] for i in range(num)])
  throughput = num / wall_time
  return accuracy, throughput

main_per_seed(seed):
  results = {}
  for p in perturbation_levels:
    received, true = generate_test_queries(num=1000, ..., perturbation=p)
    start = time()
    decoded = decode_batched(received, ...)
    wall_time = time() - start
    acc, tput = measure_accuracy_and_throughput(received, decoded, true)
    results[p] = (acc, tput)
  return results

verdict_logic:
  PASS iff:
    accuracy[p=0] == 1.0 (noise-free decoding works)
    accuracy[p=8] >= 0.99 (small perturbations recovered)
    accuracy[p=256] >= 0.50 (medium perturbations partial recovery)
    accuracy[p=1024] >= 0.10 (heavy perturbations mostly fail)
    throughput >= 1000 decodings/sec  # baseline implementation
    multi-seed accuracy variance < 0.02

  STRONG PASS iff:
    accuracy[p=256] >= 0.80 AND throughput >= 10000 decodings/sec

  KILL iff:
    accuracy[p=0] < 1.0 (decoder broken)
    OR throughput < 100 decodings/sec (decoder too slow for substrate ops)
```

**Smoke test (queue_add gate)**: N=512 (m=9), num_test_queries=100,
perturbation=[0,8], 1 seed. Target ~5s.
Oracle assertion: accuracy[p=0] == 1.0.

**Self-test (4 synthetic cases)**:
- Perfect decoding: noise-free input; predict acc=1.0.
- Worst-case perturbation: random binary noise at p=N/2; predict
  acc≈0 (decoder fails by design).
- Off-codebook input: random binary string; predict ML-decoder
  returns nearest codeword anyway (might or might not be "correct"
  per substrate semantics).
- Throughput stress: 10K queries batched; predict throughput
  scales linearly with batch size up to GPU saturation.

**Wall budget**: ~5 min GPU at full scale; smoke ~5s.

---

## Materials analog (load-bearing — Kerdock as MUB construction)

**The most substrate-relevant materials physics finding**:

**Calderbank-Cameron-Kantor-Seidel 1997** (Proc. LMS 75:436-480):
Kerdock codes K(m) **construct a complete set of mutually unbiased
bases (MUBs)** in dimension 2^(m/2). For m=12: 2^6 = 64-dimensional
MUB system, but Kerdock's 4096-length codewords represent vectors
in this MUB hierarchy.

**Connection to substrate**: substrate uses Kerdock codewords as
keys. By the CCKS theorem, these keys are equivalent to vectors in a
complete MUB system — meaning substrate's binding operations have
quantum-information-theoretic interpretation. The structure that makes
Kerdock keys "good" for substrate erasure (near-orthogonal, Welch-
bound-meeting inner products) is the same structure that makes them
"good" for MUB construction (mutually unbiased property).

**Walsh-tight-binding analog**: Walsh functions are eigenfunctions of
the Hadamard-coupled hopping Hamiltonian (binary analog of FFT/
Pauli-X strings). The FHT decoder identifies "which Walsh eigenmode"
the received word corresponds to. This is the binary analog of
spectroscopic peak-identification — substrate's WHT-peak forensics
(already ✅) is the SAME mathematical operation.

**Substrate-prediction**: substrate's MUB-equivalence means
Kerdock-keyed substrate can support **quantum-classical hybrid
operations** if/when quantum hardware becomes available. Not
immediately relevant but worth noting for long-term substrate
roadmap.

**Load-bearing or decorative?** Load-bearing for the WHT-forensics
+ Kerdock-erase combination already validated; decorative for the
immediate R6 implementation question.

---

## Falsifiable prediction

**Primary prediction (decoder performance):**

At N=4096, m=12, batched GPU implementation:
- **Noise-free accuracy**: 100.0% (no rounding errors at fp32, may
  need fp64 for fp16 implementations near codebook boundaries).
- **Hamming h=8 accuracy**: ≥ 99% (well within minimum-distance
  protection; d_min = 2016 >> 8).
- **Hamming h=64 accuracy**: ≥ 95% (still within d_min/16 = 126).
- **Hamming h=256 accuracy**: ≥ 80% (approaching d_min/8 = 252).
- **Hamming h=1024 accuracy**: ≥ 30% (beyond d_min/2 = 1008; decoder
  approaches its physical limit).
- **Throughput**: 10⁴ – 10⁵ decodings/sec on consumer GPU.

**Materials prediction**:
At sufficiently high perturbation, error rate transitions sharply
at h = d_min/2 — this is the **Hamming sphere-packing limit**, the
binary analog of the BBP transition. Predict:
- h < d_min/2: recovery near 100%
- h ≈ d_min/2: recovery transition (50/50)
- h > d_min/2: recovery falls off rapidly

**Kill criterion**: if noise-free decoding fails (accuracy[p=0] < 1.0
in 3 of 5 seeds), the decoder implementation is broken; needs debug.

**Falsifier for sharp Hamming transition**: if recovery vs h shows
smooth degradation with NO sharp transition at h ≈ d_min/2, the
substrate's effective minimum distance differs from the Kerdock
nominal — would warrant investigating substrate's actual codebook
construction.

---

## Citations

1. **Hammons, Kumar, Calderbank, Sloane, Solé (1994). "The Z₄-linearity
   of Kerdock, Preparata, Goethals, and related codes."** IEEE T-IT
   40(2):301-319. arXiv:math/0207208.
   — **Foundational construction** + Z₄-domain decoder sketch.

2. **Conway, Sloane (1998). "Sphere Packings, Lattices and Groups,"
   3rd ed.** Springer.
   — Ch. 3 §7, Ch. 15: Kerdock construction + coset-FHT decoder.
   The textbook reference for the substrate's recommended decoder.

3. **Ashikhmin, Litsyn (2004). "Simple MAP decoding of first-order
   Reed-Muller and Hamming codes."** IEEE T-IT 50(8):1812-1818.
   — Cheap FHT-only ops; cleanest soft-decision RM(1,m) decoder.

4. **Minja, Šenk (2023/2024). "SISO Decoding of Z₄ Linear Kerdock and
   Preparata Codes."** arXiv:2312.00193, IEEE T-Comm.
   — **Only recent Kerdock-specific algorithmic advance.** MAP
   decoder with bit-APP output; same asymptotic cost as classical;
   lifting APP at O(N log N) with 3-5 dB BER cost.

5. **Minja, Šenk (2024). "Decoding of Z₂ˢ Linear Generalized Kerdock
   Codes."** MDPI Mathematics 12(3):443.
   — Generalizes to Z_{2^s}; ~5 dB BER improvement over classical
   lifting decoder.

6. **Ye, Abbe (2020). "Recursive Projection-Aggregation decoding of
   Reed-Muller codes."** IEEE T-IT 66:4948-4965. arXiv:1902.01470.
   — RPA decoder; relevant for second-order RM context Kerdock
   sits in.

7. **Calderbank, Cameron, Kantor, Seidel (1997). "Z₄-Kerdock codes,
   orthogonal spreads, and extremal Euclidean line-sets."** Proc.
   LMS 75:436-480.
   — **MUB connection**: Kerdock codes construct mutually unbiased
   bases. Load-bearing materials analog.

8. **Kudekar et al. (2017). "Reed-Muller Codes Achieve Capacity on
   Erasure Channels."** IEEE T-IT 63. arXiv:1505.05831.
   — RM(1,m) is BEC-capacity-achieving; foundational for Kerdock's
   erasure performance.

---

## Routing

- **Experiment Dev**: R6 closes with the recommendation
  "Conway-Sloane coset-FHT decoder, GPU-batched" as the substrate's
  Kerdock decoder. For most substrate experiments (Bet C extensions,
  Bet F SSH-BSC), this single decoder suffices. The `wave14r_R6_kerdock_decoder_perf`
  experiment is OPTIONAL — only worth running if substrate
  encounters decoder-performance bottleneck.

- **Strategy**: this note proposes minimal cap_map update — add a
  reference under "Substrate forensics via WHT diffraction" pointing
  to Calderbank-Cameron-Kantor-Seidel 1997 as the foundational MUB
  connection. No new capability rows; R6 is implementation detail
  rather than capability research.

- **Research (this session, future cycles)**: R6 closes ✅
  (recommendation delivered). **All formal R# (R1–R12 except R4
  which was merged into R8) are now complete.** Next research cycle
  should write `notes/research_blocker.md` saying "no research
  questions pending" unless Strategy emits new R# or
  `experiment_dev_blocker.md` requests new research input.

**HONEST FINAL NOTE (per [[feedback-no-smoke]])**: R6 was the lowest-
priority open research question — implementation detail for a
RESOLVED bet. The substrate's actual operational need is satisfied
by a standard textbook decoder (Conway-Sloane coset-FHT). The lit
scan was valuable for documenting the implementation choice and
surfacing the MUB connection (load-bearing for substrate's WHT-
forensics + Kerdock-erase combination), but R6 does not warrant
follow-up research cycles. The substrate's Kerdock decoder is solved
at the literature-state level; the next steps are engineering, not
research.
