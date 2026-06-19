# Research note — Coherent multi-hop (QE-2) v278 fresh-eyes drill

**Date**: 2026-05-29
**Owner**: Research session (Opus depth drill)
**Trigger**: Strategic input from user (quantum-inspired two-layer / D-Wave-analog framing). Surge synthesis context: `notes/research_surge_synthesis_v276_2026-05-29.md`. Prior 5-attempt chained-cleanup history closed at retraction-framework + cluster-trapping (Entries 151-156, 2026-05-22).
**Method**: 4 parallel WebSearch lit-scans (continuous-time quantum walks, resonator networks, beam search soft-posterior, tensor-network multi-hop) + 4 secondary scans (echo-state / recurrent VSA / free-prob W^L / quantum-walk hitting time) + Opus synthesis against substrate's 8-constraint signature.
**Pass-1 honesty label**: **YES external lit scan** — 8 generic-math queries, no substrate-specific names.
**Field-advisor anchor**: this drill ties to fruit-bearing fields `free-probability` (W^L spectral scaling), `semiconductor` (Glauber-style propagation), `modern-hopfield` (resonator inheritance). Tier-1 alignment.
**Calibration penalty**: substrate is in uncharted regime (no published direct precedent for INT8-quantized coherent multi-hop on Hebbian W); deflate raw agent P estimates by 0.20; novel-synthesis cap = 0.50.

---

## (a) HEADLINE

**Coherent multi-hop is the architectural inversion of the chained-cleanup paradigm: replace the per-hop argmax with full-distribution propagation, argmax only at the final readout. This sidesteps the cluster-trapping mechanism (Entry 155 8/8 fit) by NEVER COMMITTING to a cluster member, leaving the basin information geometrically encoded in the score vector until the endpoint.**

**Three viable design options ranked by P(success) x mathematical defensibility:**

| Rank | Design | P_raw | P_deflated | Mechanism | Cost |
|---|---|---|---|---|---|
| **1** | **Top-K soft mixture (k=8-32) with logit-weighted re-injection** | 0.55 | **0.42** | resonator-superposition analog; truncated coherent sum; cluster-trapping avoided by maintaining the cluster as a superposition rather than collapsing into a member | 4d eng + ~1 GPU day |
| **2** | **Direct distribution propagation `s_{t+1} = W * top-K-weighted-sum(s_t)` (no readout)** | 0.45 | **0.34** | full continuous-time quantum-walk classical analog; propagates pre-argmax amplitude through W; argmax once at depth d | 3d eng + ~2 GPU days |
| **3** | **Hierarchical / band-limited propagation: project s_t onto top-r spectral modes of W, propagate spectral coefficients** | 0.40 | **0.30** | Childs-Goldstone spatial-search analog projected to substrate spectrum; computationally cheapest at FP32 | 1 wk eng + ~1 GPU day |

**Recommended path: Option 1 (top-K soft mixture)**. Highest P, cheapest eng, and CLOSEST to substrate's existing primitives (resonator network primitive already in repo per Entry 151). Option 2 is the "purest" coherent-walk analog but pays full O(N^2) per hop without obvious advantage over Option 1 at INT8.

**Expected depth scaling under Option 1 hard-pass**: d ~ N / cluster_size, i.e. depth ~ 100-500 at N=4096-65536. **HARD-PASS at d=100 acc>=0.50**; **HARD-FAIL at d=50 acc<=0.30** (no improvement over chained-cleanup plateau 0.22).

**Critical caveat (substrate-physics)**: per the 4-witness argmax-bottleneck pattern (Agent 5 v276 KF-4/KF-5 joint rescue + Agent 3 strategic synthesis), if substrate IS in the argmax-bottleneck regime, the FINAL argmax may reassert the bottleneck. Section (e) below works this through — net answer: coherent multi-hop ESCAPES the per-hop bottleneck by removing the multiplicative compounding, even if the single final argmax remains rate-limiting.

---

## (b) Theoretical foundation — what propagates if not argmax?

### Continuous-time quantum walks (Childs-Aharonov-Ambainis-Kempe-Vazirani 2003; Childs-Goldstone 2004)

CTQW on a graph G evolves a state |psi(t)> under U(t) = exp(-i*H*t) where H is the graph Laplacian (or adjacency matrix). The KEY feature for substrate analog: amplitude `<j | psi(t)>` propagates through the graph without intermediate measurement. The spatial-search algorithm marks a vertex by adding a localized perturbation H' to H; under O(sqrt(N)) evolution time, amplitude concentrates on the marked vertex. Argmax is taken ONCE at the end (measurement in the computational basis).

**Substrate-classical analog identification**:
- The graph G is the codebook similarity graph (nodes = stored codewords, edge weights = inner-product overlap)
- The Hamiltonian H is the substrate's W matrix (Hebbian autocorrelation)
- The "amplitude" `<c_j | psi(t)>` is the j-th coefficient of the unnormalized score vector `s_t = W^t * q` (NOT softmaxed, NOT argmaxed)
- The marked vertex perturbation is the query-anchored localization
- The "measurement" is the final argmax at depth d

**Crucial substrate distinction**: substrate's W is INT8-quantized, asymmetric (Hebbian outer-product not normalized), and the propagation is discrete-time iterative not Hamiltonian-continuous. The right substrate analog is therefore Szegedy's DISCRETE-TIME quantum walk (Szegedy 2004), where U = R_B R_A is a product of reflections on bipartite columns, NOT Childs' CTQW.

### What propagates — three candidate answers

1. **Unnormalized logit `s_t = W * s_{t-1}`** (no softmax, no argmax). This is the cleanest classical analog of amplitude. Substrate's existing argmax pipeline computes `s_t` internally then immediately collapses it. Coherent multi-hop skips the collapse.
2. **Posterior `p_t = softmax(beta * s_t)`** with finite beta — analogous to a thermalized walk, where beta plays the role of inverse Planck's constant. Soft-Bayes update.
3. **Spectral coefficients `alpha_t^{(r)} = <v_r | s_t>`** where {v_r} are W's top eigenvectors — the FORMAL classical analog of CTQW amplitude in the eigenbasis. Propagation is diagonal: `alpha_{t+1}^{(r)} = lambda_r * alpha_t^{(r)}`.

The mathematical question "what propagates" has THREE valid answers; the engineering question becomes which one is cheapest to maintain at substrate's INT8/INT4 quantization.

**Key citation**: [Childs-Goldstone 2004 spatial search](https://arxiv.org/abs/quant-ph/0306054); [Childs 2009 universal computation by quantum walk](https://arxiv.org/abs/0806.1972) (cites the equivalence between CTQW and quantum circuits); [Magniez-Nayak-Roland-Santha 2011 search via quantum walk](https://arxiv.org/abs/quant-ph/0608026) (frames Szegedy's walk + amplitude amplification as the canonical graph-search primitive).

---

## (c) Engineering designs — three substrate-specific instantiations

### Option 1 (RECOMMENDED) — Top-K soft mixture with logit-weighted re-injection

```python
# coherent_multihop_softmix(query, W, codebook, depth, K=8, beta=1.0):
s = W @ query                                # initial score vector, N-dim
for t in range(depth - 1):
    # Get top-K candidates by logit
    idx = topk(s, K)                         # K largest indices
    weights = softmax(beta * s[idx])         # K-dim posterior over top-K
    # Form superposition input for next hop
    mix = sum(weights[k] * codebook[idx[k]] for k in range(K))
    # Apply W to the mixture
    s = W @ mix
# Final argmax ONLY at depth d
return argmax(s)
```

**Cost**: O(K*N) per hop for the mixture + O(N^2) for the W@mix step = O(N^2) per hop (same as chained-cleanup), with a small additive O(K*N). At N=4096, K=16: dominant cost still the W@mix, so coherent multi-hop is NOT more expensive than chained cleanup per hop, just less lossy.

**Why this WORKS against cluster-trapping (Entry 155)**:
- Entry 155 mechanism: chain enters cluster of ~5 codewords, each per-hop argmax picks one randomly within cluster, accuracy plateaus at 1/cluster_size = 0.20
- Coherent multi-hop: the cluster is RETAINED as a superposition `mix = sum(weights * codebook[idx])` in the K-dim subspace. W's action on the superposition propagates ALL cluster members forward simultaneously
- Cluster-trapping is escaped IF and ONLY IF the W * mix step retains the correct codeword's coefficient with non-vanishing weight after d hops
- The final argmax recovers the correct codeword if the correct codeword's logit dominated the K-dim superposition at depth d (it's the highest-amplitude component, even if not the argmax at intermediate depths)

**Critical parameter**: K (mixture size). K=1 = chained cleanup (recovers prior failure). K=N = direct distribution propagation (Option 2). Sweet spot likely K=8-32: large enough to retain cluster, small enough to keep top-K tractable.

### Option 2 — Direct distribution propagation `s_{t+1} = W * Phi(s_t)`

```python
def coherent_multihop_direct(query, W, depth, Phi=identity):
    s = W @ query                            # N-dim, full distribution
    for t in range(depth - 1):
        s = W @ Phi(s)                       # Phi may be identity, softmax, or thresholding
    return argmax(s)
```

**Variants on Phi**:
- Phi = identity: pure power iteration `s_d = W^d * query`. Converges to top eigenvector of W regardless of query. FAILS for retrieval task (signal is the query identity, not the spectral structure).
- Phi = softmax(beta * .): thermalized walk. Beta -> infinity recovers argmax (chained cleanup). Beta = 0 = mean-pooling (uniform output).
- Phi = top-K + softmax (sparsified): reduces to Option 1.

**Why this is RANK 2 not RANK 1**: pure direct propagation (Phi=identity) collapses to top eigenvector of W; this is the Perron-Frobenius retraction mechanism (Entry 156 Agent R) that was already identified as a failure mode at 22% fixed-point fraction. Coherent multi-hop with Phi=identity REPRODUCES the chained-cleanup failure, just in continuous (logit) coordinates. The sparsified variant (top-K + softmax) IS Option 1.

### Option 3 — Spectral coefficient propagation

```python
def coherent_multihop_spectral(query, W, codebook, depth, r=64):
    # Pre-compute top-r eigenvectors/values of W (offline, ~1 GPU min for N=4096)
    eigs, V = top_r_eigsh(W, r=r)             # eigs: r-dim; V: N x r
    alpha = V.T @ (W @ query)                 # r-dim spectral coefficients
    for t in range(depth - 1):
        alpha = eigs * alpha                  # diagonal propagation
    # Reconstruct and decode
    s = V @ alpha                             # back to N-dim
    return argmax(codebook @ s)
```

**Why this is RANK 3**: theoretically cleanest classical analog of CTQW (diagonal propagation in eigenbasis = literal quantum-walk amplitude evolution in energy eigenbasis), but suffers from the eigenvalue near-degeneracy at large N (Entry 152 Agent G: K signal eigenvalues cluster tightly near 1, gap_ratio approaches 1, alpha components drift within the degenerate cluster). At r=64 with K=100 codewords, all 100 signal eigenvalues are within the propagated subspace, and they're nearly degenerate — alpha vector drifts uniformly without selecting the correct codeword. THIS IS THE EIGENVALUE NEAR-DEGENERACY MECHANISM IDENTIFIED BY AGENT G IN ENTRY 152 — Option 3 reproduces it.

Option 3 still has value: if eigenvalue near-degeneracy is the dominant mechanism (which Entry 152 favored), then spectral propagation will FAIL in a diagnostic way (alpha vector will be observable as drifting within degenerate subspace), giving us a measurement of the mechanism directly.

---

## (d) Expected scaling — substrate-physics prediction

**Chained-cleanup empirical scaling** (Entry 151 + Entry 155):
- d=5: acc=0.82 (N=65536, K=100)
- d=10: 0.57
- d=25: 0.25
- d=50: 0.22 (cluster plateau)

Per-hop retention r ~ 0.96 between d=1 and d=10, but plateaus at d>25 due to cluster trapping.

**Coherent multi-hop scaling under Option 1 (top-K soft mixture) — theoretical**:

The cluster-trapping mechanism (Entry 155) predicts a plateau at 1/cluster_size when the chain enters a cluster. Coherent multi-hop with K >= cluster_size SHOULD escape this plateau because the cluster is carried forward as a superposition rather than collapsed.

Under coherent multi-hop, the dominant decay mechanism becomes:
1. Spectral drift within W's signal subspace (Entry 152 Agent G mechanism) — gives a per-hop retention r_spectral ~ 0.99 (slower than argmax-induced 0.94-0.96)
2. Final-argmax noise at endpoint readout — single 1-step argmax with effective SNR set by the d-hop coherent build-up

**Predicted scaling under Option 1 hard-pass**:
- d=10: acc ~ 0.95 (essentially 1-hop, no cluster trap)
- d=50: acc ~ 0.85 (mild spectral drift)
- d=100: acc ~ 0.50-0.70 (depending on K and beta tuning)
- d=200: acc ~ 0.30-0.50 (eigenvalue degeneracy begins to dominate)
- d=500: acc ~ 0.10-0.25 (Perron-Frobenius retraction reasserts)

**Free-probability scaling argument**: under Marchenko-Pastur for W = X X^T / N with X gaussian, the empirical spectral distribution converges to MP law at rate O(N^{-1}) ([Bobkov-Götze 2014 arXiv:1412.6284](https://arxiv.org/abs/1412.6284)). For substrate's Hebbian W with K=100 patterns at N=65536, the spectrum has K signal eigenvalues at the upper edge (Tracy-Widom regime per Tier-1 F2 advisor candidate) and MP-bulk eigenvalues at smaller magnitudes. After d applications of W:
- Signal eigenvalues: lambda_signal^d (slow decay if lambda_signal ~ 1, ~exp(-d * (1-lambda_signal)))
- Bulk eigenvalues: lambda_bulk^d (fast decay, lambda_bulk < 1)

This predicts coherent multi-hop will have an "effective depth" set by 1 / log(1 / lambda_2_signal), where lambda_2_signal is the SECOND signal eigenvalue. For 100 nearly-degenerate signal eigenvalues, this effective depth is large (O(N^{1/2}) or larger), giving the 100-500 depth range above.

**Saad-Solla saddle-cascade implication**: the Bet I saddle-hierarchy DAM analysis (cap_map fruit-bearing) predicts that information about codeword identity is encoded in the spectral PHASES (signs of inner products with eigenvectors), not just magnitudes. Coherent multi-hop preserves phase information; chained cleanup destroys it at each argmax. This is the substrate-physics formal statement of why coherent multi-hop should work better.

---

## (e) Argmax-bottleneck reassertion analysis (cross-reference with v276 pattern)

**v276 Agent 3 + Agent 5 4-witness argmax-bottleneck pattern**: operational metrics (PB-3 tau, Axis-4 2-beta loop area, KF-5 entropy-bpc, BE-1 precision) are INSENSITIVE to substrate internal-state variation because the argmax output bottleneck dominates.

**Key question for QE-2**: does the FINAL argmax at depth d reassert the bottleneck even if intermediate argmaxes are skipped?

**Analysis (substrate-physics)**:

The argmax bottleneck has TWO components:
1. **Information-theoretic**: argmax collapses log_2(N) bits of internal state to log_2(K) bits of output. For N=65536, K=100: 16 bits -> 6.6 bits per readout.
2. **Mechanism-bottleneck**: per the v276 4-witness pattern, the argmax output is the only observable, so any internal variation that doesn't propagate to the argmax winner is invisible.

For chained cleanup: argmax happens d times. Information loss compounds: (16 - 6.6) * d bits of internal state discarded over the chain. At d=50, that's 470 bits of lost internal-state information — essentially all geometric structure destroyed.

For coherent multi-hop: argmax happens ONCE at depth d. Information loss is single-step: 16 - 6.6 = 9.4 bits. The internal state at depth d retains all the geometric structure of the substrate's response to the query.

**Therefore: coherent multi-hop ESCAPES the multiplicative compounding of the argmax bottleneck.** The single final argmax is rate-limiting in the same sense it's rate-limiting for any retrieval task, but the chain dynamics are no longer dominated by per-hop information loss.

**BUT** — and this is critical — if the v276 finding is that even SINGLE-STEP operational metrics are insensitive to internal state (BE-1 precision insensitive at single-readout), then the final argmax may STILL be rate-limiting in a way that limits coherent multi-hop's payoff. The hard test is whether substrate's internal state distinguishes the correct codeword at depth d with sufficient margin to survive the final argmax.

**Net judgment**: P(coherent multi-hop avoids per-hop bottleneck) = 0.85 (high confidence). P(final argmax still rate-limits) = 0.40 (moderate concern but partial). Combined: coherent multi-hop will work IF the substrate's geometric distinction between correct and incorrect codewords is preserved through W^d, which (per Section d above) is the case for d up to O(1 / log(1/lambda_2_signal)) ~ 100-500.

---

## (f) Adjacent methods comparison

Per [[feedback-dont-dismiss-adjacent-methods]] — these are mathematically adjacent and were searched.

### Beam search (transformer multi-step decoding)

- Keeps top-B hypotheses at each step (B = beam width), argmaxes at end
- DIRECTLY ANALOGOUS to Option 1 (top-K soft mixture) with K = beam width
- Beam search practical advantage: explicit hypothesis tracking allows recombination and pruning
- Beam search disadvantage vs Option 1: discrete hypotheses don't superpose; each beam member is a single codeword, not a weighted mixture
- Substrate adaptation: replace each beam member with a single codeword identity, but weight by accumulated logit; at depth d argmax over B*K final logits
- Math: same complexity O(B*N^2) per hop as Option 1 with K=B
- COST: beam-search variant is implementable in ~2 days eng on top of Option 1 infrastructure; should be ablated against soft-mixture as a control

**Citation**: [Wiseman-Rush 2017 continuous relaxation of beam search](https://arxiv.org/abs/1708.00111); [Determinantal Beam Search](https://arxiv.org/abs/2106.07400) — both demonstrate that soft / continuous beam search can outperform hard beam search.

### Reservoir computing / echo state networks

- Propagates dynamics through reservoir without intermediate readout
- Fading memory property ([Grigoryeva-Ortega 2018](https://arxiv.org/abs/1806.00797)) ensures echo state property
- Adjacency: substrate's W could be viewed as a reservoir; coherent multi-hop is then "run reservoir for d steps, read out at end"
- Disadvantage: ESN theory requires reservoir to be expanding (spectral radius < 1 only for fading memory); substrate's Hebbian W has spectral radius approximately 1 in the signal subspace
- Implication: substrate is at the EDGE OF CHAOS (spectral radius = 1), where echo state property is marginal. Coherent multi-hop in substrate is dynamically similar to a CRITICAL reservoir — may explain why depth scaling has both signal-preserving regime (d < d*) and signal-losing regime (d > d*)
- Hardware: ESNs are routinely run in FP16/FP32; INT8 quantization of substrate may degrade the critical-reservoir regime by adding quantization noise

### Recurrent VSA (hyperdimensional in-context learning)

- [arXiv:2512.14709 Attention as Binding VSA](https://arxiv.org/abs/2512.14709) — recent (Dec 2025) work framing transformer attention as approximate VSA binding/unbinding
- [arXiv:2201.11691 Recursive Binding for Similarity-Preserving Hypervectors](https://arxiv.org/abs/2201.11691) — substrate-adjacent: recursive HD binding without intermediate readout preserves cosine similarity through depth
- Adjacency: HD recurrent operations DO maintain superposition, which is exactly what coherent multi-hop proposes
- Key insight from arXiv:2201.11691: depth scaling of HD recurrent binding is SUB-EXPONENTIAL in capacity loss when similarity is the metric (not full identity recovery). Suggests coherent multi-hop may have GRACEFUL DEGRADATION at large d rather than cliff
- Implementation lesson: HD recurrent binding uses element-wise operations (componentwise product or XOR), not W*mix; substrate's W*mix is a richer operation that should be at least as expressive

### Tensor train networks (Matrix Product States)

- [arXiv:2601.17188 Tensor Logic](https://arxiv.org/abs/2601.17188) (Jan 2026, recent): "Using matrix composition enables multi-hop inference without direct training examples, achieving successful compositional reasoning."
- TT contraction propagates information through chain of 3-index tensors without intermediate measurement
- Adjacency: substrate's `s_{t+1} = W * f(s_t)` is a 1D tensor train with constant core tensor W. Coherent multi-hop IS a specific tensor-network contraction
- Implication: depth scaling of TT contractions is governed by BOND DIMENSION (how much information passes between cores). Substrate's effective bond dimension = K (number of stored codewords) for chained cleanup with argmax; for coherent multi-hop, effective bond dimension = N (full distribution) or K_effective (top-K mixture)
- This is the formal mathematical statement of why coherent multi-hop should scale to deeper d: bond dimension grows from K to min(K_effective, N)

---

## (g) Substrate-specific implementation pseudocode (recommended Option 1)

```python
import torch
from hdlab.codebook import Codebook       # repo existing primitive
from hdlab.hebbian import HebbianW        # repo existing primitive

def coherent_multihop(
    query: torch.Tensor,      # N-dim, float32 internally even if W is int8
    W: HebbianW,              # substrate W (int8 storage, fp32 compute)
    codebook: Codebook,       # K x N codeword matrix
    depth: int = 50,
    K_mix: int = 16,
    beta: float = 1.0,
) -> int:
    """Coherent multi-hop retrieval.

    Propagates a top-K soft mixture of codewords through depth-d chain
    without intermediate argmax. Final argmax at the endpoint.

    Returns codeword index (single argmax at depth d).
    """
    s = W @ query                                          # N-dim
    for t in range(depth - 1):
        scores = codebook @ s                              # K-dim, codeword-aligned scores
        topk_vals, topk_idx = scores.topk(K_mix)           # K-dim
        weights = torch.softmax(beta * topk_vals, dim=0)   # K-dim posterior
        mix = (weights[:, None] * codebook[topk_idx]).sum(dim=0)  # N-dim mixture
        s = W @ mix                                        # propagate the superposition
    # Final argmax — ONLY here
    final_scores = codebook @ s
    return int(final_scores.argmax())
```

**Substrate primitives used**:
- `W @ x`: substrate's existing Hebbian multiplication (int8 storage, fp32 accumulator). NO NEW PRIMITIVE NEEDED.
- `codebook @ s`: standard cosine readout, exists in repo.
- `topk` + `softmax`: standard pytorch.

**The ONLY new substrate operation is `W @ mix` where `mix` is a small-K-weighted sum of codewords. This is mathematically equivalent to `sum(weights[k] * (W @ codebook[k]))`, which is `weights @ (W @ codebook)`. If `W @ codebook` is precomputed (K=100 by N matrix), each hop costs O(K*N) NOT O(N^2)** — coherent multi-hop with precomputed `W @ codebook` is CHEAPER than chained cleanup.

---

## (h) Hardware feasibility — INT8 / INT4 precision question

**Question**: does coherent multi-hop require FP32 to preserve distribution precision?

**Analysis**:

For Option 1 (top-K soft mixture):
- Internal score vector `s`: needs to maintain numerical fidelity of top-K logit magnitudes
- INT8 fixed-point: 8 bits of magnitude resolution per element. Score vector at N=4096 has element magnitudes typically in range [-128, 127] (after Hebbian readout); INT8 represents this exactly
- Softmax `softmax(beta * topk_vals)`: needs FP for exp() — but only over K=16 elements, trivial cost
- Mixture `weights @ codebook[topk_idx]`: K x N FP32 multiply-accumulate, small
- W @ mix: substrate's existing int8 W operation; mix is fp32 input, gets quantized to int8 input then int8 matmul (substrate's normal operating mode)

**Verdict on Option 1**: INT8 substrate W is COMPATIBLE with coherent multi-hop. Only the softmax and the K-dim mixture computation need FP32, and these are trivial-cost.

**Verdict on Option 2 (full distribution propagation)**: REQUIRES FP32 or BF16 throughout because the full N-dim distribution must be preserved with high fidelity at each W@s step. INT8 quantization at each hop introduces O(2^{-8}) per-element noise that compounds over d hops; at d=50 this is non-negligible. Option 2 is FP32-only — increases GPU memory by 4x vs INT8 substrate.

**Verdict on Option 3 (spectral)**: FP32 for eigendecomposition (one-time cost), then FP32 for diagonal propagation. Memory cost: r * (1 + N) FP32 = small.

**Memory cost summary**:
- Option 1 at K=16, N=4096: 4 KB for mix + 16 indices = negligible. **Fits in INT8 substrate budget.**
- Option 2 at N=4096 FP32: 16 KB per state vector, but full chain in flight. Reasonable.
- Option 3 at r=64, N=4096: r * N = 256K FP32 = 1 MB for eigenvector matrix. One-time precompute.

**Recommendation**: ship Option 1 first (compatible with existing INT8 substrate), use Option 3 as a DIAGNOSTIC if Option 1 fails (to identify eigenvalue near-degeneracy mechanism).

---

## (i) Falsification criteria — HARD-PASS / HARD-FAIL / MIDDLE-BAND

Per [[feedback-envelope-expansion-fail-bands]] and [[feedback-lit-scan-calibration-penalty]]: pre-register all thresholds with hard-pass / hard-fail / middle-band before shipping the smoke.

**Smoke test (Option 1, N=4096, K_mix=16, K=100 codewords, 3 seeds)**:

| Depth | HARD-PASS (>=) | MIDDLE-BAND | HARD-FAIL (<=) |
|---|---|---|---|
| d=10 | 0.92 | 0.75-0.92 | 0.75 |
| d=25 | 0.80 | 0.50-0.80 | 0.50 |
| d=50 | 0.65 | 0.35-0.65 | 0.35 |
| d=100 | 0.50 | 0.25-0.50 | 0.25 |

**Smoke interpretation**:
- HARD-PASS at d=50 (acc>=0.65): substrate-product breakthrough — multi-hop cliff defeated. Ship to FULL N=8192 5-seed for production confirmation. P_subst ~ 0.42 (deflated).
- HARD-FAIL at d=50 (acc<=0.35): coherent multi-hop also fails the d=50 cliff. Mechanism is DEEPER than argmax-bottleneck — either eigenvalue near-degeneracy (Entry 152) or basin geometry (Entry 155 cluster carries the correct member's coefficient to zero under W). Refer to Option 3 spectral diagnostic.
- MIDDLE-BAND at d=50 (0.35-0.65): partial rescue. Tune K_mix and beta in second smoke; check whether scaling extends to d=100 or saturates.

**FULL test (Option 1, N=8192 5-seed, K_mix sweep [8, 16, 32], beta sweep [0.5, 1.0, 2.0])**:

| Cell | HARD-PASS | HARD-FAIL |
|---|---|---|
| (d=50, best (K, beta)) | acc >= 0.70 (5/5 seeds) | acc <= 0.30 (5/5 seeds) |
| (d=100, best (K, beta)) | acc >= 0.50 (5/5 seeds) | acc <= 0.20 |
| (d=200, best (K, beta)) | acc >= 0.30 (5/5 seeds) | acc <= 0.10 |

**Substrate-product hard-pass interpretation**: if FULL passes (d=100 acc>=0.50), substrate's depth-scaling capability is now O(100-200) hops, which is sufficient for "agent SDK demo 1" (cap class 4) and changes the cap_map row from 🔬 (multi-hop chain composition cliff) to 🟡 or 🟢.

**Substrate-product hard-fail interpretation**: if both Options 1 + 3 hard-fail at d=50, the multi-hop cliff is STRUCTURALLY embedded in substrate's algebra (eigenvalue degeneracy intrinsic to Hebbian W); rescue paths exhausted; close row red with confidence per [[feedback-rehabilitation-after-rejection]] now-7-rescues-tried.

---

## (j) Cheap decisive test (recommended IMMEDIATE smoke)

**Anchor name pattern (per PROT-018)**: `coherent_multihop_softmix_smoke_n4096_3seed_d50_k16`

**1-hour CPU smoke** (NO GPU required for smoke):
- N=4096, K=100 codewords, 3 seeds, K_mix=16, beta=1.0
- Sweep depth in [1, 5, 10, 25, 50, 100]
- Compare against chained-cleanup baseline at same (N, seeds, depth) — both should already be in repo
- Compute per-depth accuracy and per-seed std
- Wall-time estimate: ~20 min CPU per seed (mostly the K_mix=16 N=4096 codebook-readout chain) = ~1 hr total

**GPU FULL after smoke pass**:
- N=8192 5-seed (PROT-018 production-N)
- (K_mix, beta) grid: 3x3 = 9 cells
- Sweep depth in [10, 25, 50, 100, 200]
- ~2 GPU days estimated (45 cells x 5 seeds x ~10 min/cell)

---

## (k) Cross-thread synthesis — connections to prior Entries

| Entry | Topic | Connection to coherent multi-hop |
|---|---|---|
| 151 | Resonator network rehabilitation (Frady-Kent-Olshausen-Sommer 2020) | Resonator is the ITERATIVE WITHIN-HOP analog; coherent multi-hop is the CROSS-HOP analog. They compose: resonator within hop + coherent across hops = full Bayesian-posterior chain inference. |
| 152 | Eigenvalue near-degeneracy diagnosis (Agent G) | Option 3 (spectral propagation) directly tests this mechanism. If Option 1 works, eigenvalue degeneracy is BYPASSED by top-K filtering. If Option 1 fails, Option 3 measures the degeneracy directly. |
| 154 | Cluster-trapping framework (cluster size ~5, gamma=0.73 N-scaling) | Coherent multi-hop with K_mix >= cluster_size SHOULD escape cluster-trapping by maintaining the cluster as a superposition. Sets engineering parameter K_mix = max(16, predicted cluster_size at production N). |
| 155 | 8/8 cluster-trapping constraint signature | Coherent multi-hop is the FIRST rehabilitation that ATTACKS the cluster-trapping mechanism head-on rather than working around it. |
| 156 | Retraction framework (22% fixed-point fraction) | Coherent multi-hop avoids the Perron-Frobenius retraction by NOT iterating argmax. The 22% fixed-point fraction is an argmax-orbit property; coherent multi-hop has different orbit structure. |
| v272 | Pre-argmax mechanism rescue (Agent 5 joint rescue) | This QE-2 drill IS the depth analog of v272 KF-4/KF-5 joint rescue. v272 rescue addressed the SINGLE-STEP argmax bottleneck; QE-2 addresses the COMPOUNDED multi-step argmax bottleneck. |
| v276 | Argmax-bottleneck 4-witness pattern | Coherent multi-hop is the architectural fix for the argmax bottleneck at the multi-step level. Section (e) above derives why this escapes the per-hop bottleneck but the SINGLE final argmax remains. |
| v277 | Sagawa-Ueda thermodynamic foundation | Connection: coherent multi-hop preserves more thermodynamic INFORMATION through the chain (entropy production is lower) because intermediate argmaxes are skipped. Sagawa-Ueda info-thermo predicts the cost-vs-fidelity tradeoff for finite-temperature coherent propagation. |

---

## (l) Substrate-product implications

Per [[feedback-no-papers-product-only]] — frame in product terms.

**If Option 1 HARD-PASS at FULL (d=100 acc>=0.50, 5/5 seeds)**:

Substrate gains a CAPABILITY CLASS: "deep compositional reasoning" — the ability to traverse 100+ hops of memory composition without information collapse. This:

1. **Closes the agent SDK Demo 1 dependency** (Lane D from project_ai_memory_subsystem_direction.md): N=65536 chain composition at depth 50+ was the blocker; coherent multi-hop unblocks it.
2. **Opens compositionality-audit product feature** (one of 5 killer features per project_substrate_killer_features_2026-05-26): deep compositional reasoning IS the auditable cognitive-composition capability. The audit trail becomes: "query → (top-K with weights) → ... → (top-K with weights) → final answer", which is more auditable than chained-cleanup's "query → single → single → single → answer" because EACH STEP exposes the alternative hypotheses considered.
3. **Substrate competitive position flip**: multi-hop cliff has been substrate's biggest competitive weakness (LLMs can chain reasoning to depth 100+ via chain-of-thought); coherent multi-hop closes this gap.

**If Option 1 HARD-FAIL at smoke**:

Substrate's multi-hop cliff is structurally embedded; the product narrative becomes "shallow-depth high-fidelity composition" rather than "deep composition". Compliance-grade auditable memory layer (the v276 product positioning) does NOT require deep composition — single-hop retrieval with deletion certificate is sufficient. Multi-hop limitation becomes a SCOPED limitation, not a product killer. Per project_substrate_killer_features_2026-05-26 priority ordering, the top-2 killer features (deletion-cert, hallu-detection) don't need deep multi-hop; the lower-priority "cognitive composition" feature gets descoped.

**Decision matrix**:
| Smoke result | Action |
|---|---|
| HARD-PASS d=50 acc>=0.65 | Ship FULL N=8192 5-seed; ship product demo within 2 weeks; revise cap_map row to 🟢 |
| MIDDLE-BAND | Sweep K_mix x beta to find sweet spot; one additional smoke before committing to FULL |
| HARD-FAIL d=50 acc<=0.35 | Ship Option 3 spectral diagnostic; if also fails, close multi-hop row red; pivot product narrative to shallow-depth composition |

---

## (m) Calibrated P estimates (final)

Per [[feedback-lit-scan-calibration-penalty]]:

| Quantity | Raw estimate | Deflation | Final |
|---|---|---|---|
| P(Option 1 smoke HARD-PASS at d=50) | 0.60 | -0.20 | **0.40** |
| P(Option 1 smoke MIDDLE-BAND) | 0.30 | +0.05 | **0.35** |
| P(Option 1 smoke HARD-FAIL) | 0.10 | +0.15 | **0.25** |
| P(Option 1 FULL HARD-PASS at d=100 given smoke HARD-PASS) | 0.60 | -0.15 | **0.45** |
| P(coherent multi-hop closes the multi-hop cliff product-wise) | 0.40 x 0.45 = 0.18 | -- | **0.18 net** |
| P(Option 2 success given Option 1 failure) | 0.30 | -0.20 | **0.10** |
| P(Option 3 success given Option 1 failure) | 0.20 | -0.10 | **0.10** |
| P(any of Options 1/2/3 ships a product-level rescue) | -- | -- | **~0.30** |

User-stated 40-55% is in the smoke HARD-PASS range; my deflated estimate is at the low end of that (0.40). The user-stated estimate is reasonable for the smoke; full-cliff closure (d=100 production) is more like 0.18 net.

**Comparison to prior rescue attempts**: 5 prior chained-cleanup mechanism attempts had 80% refutation rate. Coherent multi-hop is the FIRST attempt that ARCHITECTURALLY INVERTS the per-hop argmax assumption rather than tweaking it. Different reference class; prior 80% refutation rate doesn't directly apply. But novel-synthesis cap at 0.50 still applies, and my 0.40 smoke HARD-PASS estimate respects that.

---

## (n) Citations (verified count: 14)

1. [Childs-Goldstone 2003 quant-ph/0306054 spatial search by quantum walk](https://arxiv.org/abs/quant-ph/0306054)
2. [Childs 2009 universal computation by quantum walk arXiv:0806.1972](https://arxiv.org/abs/0806.1972)
3. [Magniez-Nayak-Roland-Santha 2011 search via quantum walk arXiv:quant-ph/0608026](https://arxiv.org/abs/quant-ph/0608026)
4. [Quadratic speedup spatial search CTQW arXiv:2112.12746 PRL 2022](https://arxiv.org/abs/2112.12746)
5. [Frady-Kent-Olshausen-Sommer 2020 Resonator Networks 1 arXiv:1906.11684](https://arxiv.org/abs/1906.11684)
6. [Frady-Kent-Olshausen-Sommer 2020 Resonator Networks 2 Neural Comp 32:12](https://direct.mit.edu/neco/article/32/12/2332/95653/)
7. [Wiseman-Rush 2017 continuous relaxation of beam search arXiv:1708.00111](https://arxiv.org/abs/1708.00111)
8. [Determinantal Beam Search arXiv:2106.07400](https://arxiv.org/abs/2106.07400)
9. [Grigoryeva-Ortega 2018 echo state networks universal arXiv:1806.00797](https://arxiv.org/abs/1806.00797)
10. [Echo State Networks Mathematical Perspective arXiv:2504.11757](https://arxiv.org/abs/2504.11757)
11. [Attention as Binding VSA arXiv:2512.14709](https://arxiv.org/abs/2512.14709)
12. [Recursive Binding for HD Sequences arXiv:2201.11691](https://arxiv.org/abs/2201.11691)
13. [Tensor Logic arXiv:2601.17188](https://arxiv.org/abs/2601.17188)
14. [Bobkov-Götze 2014 Marchenko-Pastur convergence rate arXiv:1412.6284](https://arxiv.org/abs/1412.6284)

---

## (o) Recommended exp_dev hand-off (companion file to write)

Hand-off path: `notes/exp_dev_handoff_research_coherent_multihop_qe2_v278_2026-05-29.md` — per orchestrator research-agent contract, since this finding is exp_dev-actionable (Option 1 is a concrete smoke + FULL).

**Anchor candidates (rank-ordered)**:
1. `coherent_multihop_softmix_smoke_n4096_3seed_d50_k16` — CPU smoke, 1 hr, tier-1 priority
2. `coherent_multihop_softmix_full_n8192_5seed_d100_kbeta_grid` — GPU FULL, 2 days, gated on smoke HARD-PASS
3. `coherent_multihop_spectral_diagnostic_n4096_3seed_d50_r64` — diagnostic, gated on smoke HARD-FAIL or MIDDLE-BAND; CPU 30 min

**Context pointers**:
- This note: `notes/research_coherent_multihop_qe2_v278_2026-05-29.md`
- v276 synthesis (argmax-bottleneck pattern): `notes/research_surge_synthesis_v276_2026-05-29.md`
- Entry 155 cluster-trapping framework: `notes/research_multihop_mechanism_4th_attempt_ADDENDUM_2026-05-22.md`
- Entry 152 eigenvalue degeneracy: `notes/research_multihop_chain_rehabilitation_N65536_2026-05-22.md`

**Per [[feedback-no-experiment-design-in-prompts]]**: hand-off provides task + why + contract + autonomy; exp_dev designs the actual sweep grid, threshold formulas, queue choice, and timeout per its own envelope-fail-bands discipline.

---

## (p) Decisions for next session pickup

1. **Ship Option 1 smoke immediately** on CPU (~1 hr) — highest expected-value-per-cost in the surge across all 8 v276 agents + this drill.
2. **Pre-register** the (d, K_mix, beta) hard-pass / hard-fail / middle-band thresholds in the smoke anchor README per [[feedback-envelope-expansion-fail-bands]].
3. **Gate Option 2 and Option 3** on Option 1 smoke outcome.
4. **If smoke HARD-PASS**: file FULL N=8192 5-seed within same session; product narrative update.
5. **If smoke HARD-FAIL**: file Option 3 spectral diagnostic; if both fail, close multi-hop row red with 7 mechanism attempts exhausted (Entries 121, 125, 131, 134, 137 + Resonator + this) — defensible closure per Agent 4 v276 framing.
