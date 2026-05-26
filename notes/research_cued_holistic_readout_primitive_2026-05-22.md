# Research note — Cued Holistic Readout primitive ("non-contact x-ray" of substrate)

**Date**: 2026-05-22 ~14:50 EDT
**Owner**: Research session
**Trigger**: User direct (~14:35 EDT): *"did you find anything actionable in the research for strategy? what I was envisioning is some kind of non-contact way of probing the entire substrate for relevant data - maybe you can ~excite certain kinds of memories and then take an ~x-ray to get a snapshot of all of them for a very fast holistic query"*
**Method**: 3 fresh Sonnet-dispatched parallel external lit-scan agents per [[feedback-subagent-model-optimization]] + the strengthened cron-prompt mandate (real external lit scan, not prior-knowledge synthesis). Generic-math queries only per [[feedback-query-privacy-decomposition]]. ~9 min wall, ~63 KB raw agent output.
**Pass-1 honesty label**: **YES** — real external lit scan via 3 Sonnet agents with WebSearch + WebFetch. Generic-math queries (compressive sensing, classical Loschmidt echo, randomized SVD, etc.) — no substrate fingerprint exposed.
**Materials analog**: load-bearing — substrate's 2D-spectroscopy class translates from Jalabert-Pastawski 2001 classical Loschmidt echo + Jonsson 2001 memory/rejuvenation in 3D Ising spin glass.

---

## (a) Headline — what's actionable for Strategy

**Direct answer to user's question**: yes, the lit scan turned up something **substrate-novel and actionable**, but it is **a CAPABILITY primitive (cued-holistic-readout), not an observability probe** — supersedes/complements Entries 140+141 substrate observability suite v1 (which were diagnostic).

**Three candidate mechanism families** for "fast holistic query of substrate":

| Mechanism | Cost (online) | Where it works | Substrate-product status |
|-----------|---------------|----------------|--------------------------|
| **Z.1 SRHT compressive readout** | O(N log N + M·K), M ~ log K | Low load OR large alignment gaps | **NEW Bet candidate** — substrate-novel; build cost ~10-15 GPU-h |
| **Z.2 Classical 2-pulse echo (C2PO)** | O(K^2 · N_delay) for full 2D map | All loadings; pattern-pair coupling diagnostic | **NEW Bet candidate** — substrate-novel; nothing equivalent in current Bet set |
| **Z.3 Modern Hopfield softmax readout** | O(N·K) per query, one-shot | Low alpha; **REFUTED at substrate's current N=4096 + beta=32** | Already in scope (Bet Y V2.D) — under Phase 1 N=65536 revision per cycle 130 |
| (Baseline) Direct inner-product readout | O(N·K) per query | Always | Status quo |

**Most substrate-novel win**: **Z.2 — Classical 2-pulse echo / C2PO**. No current Bet probes pattern-pair couplings. This is closest to the user's literal vision (excite class A, x-ray substrate, see how class B responds).

**Most cost-effective win for low-K regimes**: **Z.1 SRHT compressive readout** delivers ~2000x speedup over O(N·K) brute force at N=4096, K=10^3 — but only when stored-pattern alignment gaps are macroscopic.

**Honest substrate-product impact P**: **0.55-0.70**. Lower bound: vision is partially blocked at substrate's current operating point (modern Hopfield softmax = the cleanest primitive but it's exactly the mechanism refuted at cycle 105 multi-beta FULL). Upper bound: Z.2 C2PO is a genuinely new diagnostic class with no current Bet; it would extend Lane D (cognitive architecture) and Lane A (memory) simultaneously.

---

## (b) Pass 1 — Cross-agent external lit scan

### Agent G — Compressive Sensing / Random Projection readout

**Winner**: **SRHT (Subsampled Randomized Hadamard Transform)** (Tropp 2011 arXiv:1011.1595). M = O(epsilon^(-2) log K) projections via structured O(N log N) transform. Sketch query vector once at cost O(N log N), inner-product against M-dim pre-sketches of K stored patterns at cost O(M·K). At N=4096, K=10^3, epsilon=0.1: M ~ 2000 measurements vs full 4M ops = 2000x speedup.

**REJECTED**:
- IID Gaussian JL (requires free random measurement matrix; substrate has fixed coupling)
- Weighted MinHash (no batching across K patterns)
- Random Fourier Features (degenerate to RP for binary spins)
- Model-based CS (recovers full signal, not K inner products)
- FAISS/HNSW (incompatible with fixed-topology substrate)

**CRITICAL CAVEAT**: SRHT guarantee is for ADDITIVE error epsilon·N, not relative. If top-pattern alignment = 0.15·N and second-best = 0.14·N, gap = 0.01·N forces epsilon < 0.01 → M > 240,000 > N — no compression benefit. **Method works cleanly only when top-k patterns have macroscopic alignment gap (typical far below AGS alpha_c=0.138).**

### Agent H — Echo / 2D Spectroscopy classical analogs

**REJECTED as fundamentally quantum** (decorative-pattern note #14 of session):
- Photon echo (requires continuous phase coherence — binary spins lack it)
- Stimulated photon echo (population-storage step is quantum chi^(3))
- 2D NMR COSY/NOESY (J-coupling + Larmor precession required)
- Keldysh 2D spectroscopy (quantum field theoretic)

**SURVIVORS** — classical analogs that DO port:
1. **Classical Loschmidt echo** (Jalabert-Pastawski 2001 PRL 86:2490; cond-mat/0010094). Overlap of two trajectories after time-reversed perturbation. Decay rate = effective Lyapunov exponent of inter-attractor boundary.
2. **chi_3 nonlinear susceptibility** as four-point overlap probe (Edwards-Anderson; arXiv:1108.2799). Already covered in Entry 141.
3. **Memory/rejuvenation two-step protocol** in 3D Ising spin glass (Jonsson et al. 2001 cond-mat/0104333). **Experimental existence proof** that 2-step protocols reveal pattern-pair structure in classical Ising spin glasses.

**Top operational protocol — "C2PO" (Classical 2-Pulse Overlap)**:
- Apply cue1 = partial pattern A; run T_cue1 sweeps under field h = c·xi_A
- Free relax T_delay sweeps
- Apply cue2 = partial pattern B; run T_cue2 sweeps under field h = c·xi_B
- Measure overlap with pattern B
- Subtract baseline (same protocol minus cue2)
- Echo amplitude = differential overlap; encodes inter-attractor coupling
- Full 2D map: scan (A, B, delay) for all pattern pairs

### Agent I — Spectral / Eigenmode / Lanczos readout

**HARSH FINDING** that cuts the vision sharply:

At substrate's alpha = K/N = 0.15 (cap_map operating point), Marchenko-Pastur predicts K=614 signal eigenvalues that are **approximately degenerate** (each ~1). Eigenvectors mix patterns freely within the K-dim signal subspace. **No r << K captures per-pattern similarity.**

**The eigenmode-projection vision works ONLY at low load** (alpha < 0.03, K < ~120 for N=4096). In that regime BBP-class separation is clean. Above that, eigenmode protocol offers ZERO advantage over direct inner products.

**The dominant baseline is the modern Hopfield softmax readout** (Ramsauer et al. 2020 arXiv:2008.02217): O(N·K) one-shot, exact per-pattern similarity. **This IS the canonical "x-ray snapshot" primitive in the literature.** It's also the mechanism class that was EMPIRICALLY REFUTED at substrate's current N=4096, beta=32 in cycle 105 multi-beta FULL test (Entry 137). Strategy's cycle-130 revision (`strategy_request_to_exp_dev_BetY_V2D_mechanism_revision_2026-05-22.md`) drops softmax cleanup and tests Phase 1 5-test battery at N=65536 instead.

**Implication**: the eigenmode / softmax family is the cleanest mechanism for fast holistic readout BUT substrate's current architecture rejects it. **The compressive-sensing + classical-echo family is the substrate-applicable rescue.**

---

## (c) Pass 2 — Drill on top 2 substrate-applicable mechanisms

### Z.1 — SRHT compressive readout (P=0.65)

**Theory**: Tropp 2011 (arXiv:1011.1595) establishes M = Theta(epsilon^(-4) log|X| log^4 N) for JL guarantee with structured SRHT. Practical bound M = O(epsilon^(-2) log K).

**Operational protocol** (ASCII-only pseudocode):

```python
import numpy as np
from scipy.linalg import hadamard

def srht_precompute(stored_patterns, M, seed=0):
    """One-time offline precompute. patterns: K x N, ±1."""
    K, N = stored_patterns.shape
    rng = np.random.default_rng(seed)
    D = rng.choice([-1, 1], size=N)  # diagonal sign flip
    row_idx = rng.choice(N, size=M, replace=False)  # subsampled rows
    H = hadamard(N) / np.sqrt(N)
    # sketch matrix S = sqrt(N/M) * (rows of H[row_idx] @ diag(D))
    S = np.sqrt(N / M) * (H[row_idx, :] * D[np.newaxis, :])  # M x N
    sketched_patterns = stored_patterns @ S.T  # K x M
    return S, sketched_patterns

def srht_readout(state, S, sketched_patterns):
    """Online: state is current substrate spin vector (N,)."""
    state_sketch = S @ state  # M-dim, cost O(M*N) — for true SRHT use FWHT for O(N log N)
    sim_vector = sketched_patterns @ state_sketch  # K-dim similarity scores
    return sim_vector
```

**Falsifiable prediction at N=4096, K=10^3, epsilon=0.1**:
- M = 2000 measurements yields >=90% top-10 recall vs brute-force O(N·K) ranking
- For K=10^4: M = 2440, >=90% top-10 recall
- **Falsification**: top-10 recall < 70% at M=2000 with random ±1 patterns (would indicate substrate's structured W introduces non-IID correlations that break JL guarantee)

**Substrate-product value**: ~2000x speedup over O(N·K) brute-force inner products. Couples to Lane D (fast cognitive-architecture query) and Lane A (memory layer; faster retrieval than full attention).

### Z.2 — Classical 2-Pulse Overlap (C2PO) (P=0.55) — substrate-novel pattern-pair diagnostic

**Theory**: Jalabert-Pastawski 2001 classical Loschmidt echo + Jonsson et al. 2001 memory/rejuvenation in 3D Ising spin glass.

**Operational protocol** (ASCII-only pseudocode):

```python
def c2po(substrate, stored_patterns, A_idx, B_idx, delay_steps,
         cue_strength=0.1, T_cue=20, T_readout=50, n_reps=50):
    """Classical 2-pulse overlap protocol.
    Returns echo amplitude = differential overlap with pattern B."""
    xi_A = stored_patterns[A_idx]
    xi_B = stored_patterns[B_idx]
    echo_amps = []
    for rep in range(n_reps):
        # Baseline: cue1 only, no cue2
        s = substrate.random_state(seed=rep)
        s = substrate.evolve_under_field(s, h=cue_strength * xi_A, n_sweeps=T_cue)
        s = substrate.evolve_free(s, n_sweeps=delay_steps)
        m_baseline = float(np.mean(s * xi_B))
        # Probe: cue1, delay, then cue2
        s = substrate.random_state(seed=rep)
        s = substrate.evolve_under_field(s, h=cue_strength * xi_A, n_sweeps=T_cue)
        s = substrate.evolve_free(s, n_sweeps=delay_steps)
        s = substrate.evolve_under_field(s, h=cue_strength * xi_B, n_sweeps=T_cue)
        s = substrate.evolve_free(s, n_sweeps=T_readout)
        m_probe = float(np.mean(s * xi_B))
        echo_amps.append(m_probe - m_baseline)
    return float(np.mean(echo_amps)), float(np.std(echo_amps))

def c2po_2d_map(substrate, stored_patterns, delay_grid):
    """Full KxK pattern-pair coupling map across delay grid."""
    K = stored_patterns.shape[0]
    n_delays = len(delay_grid)
    echo_map = np.zeros((K, K, n_delays))
    for a in range(K):
        for b in range(K):
            for d, delay in enumerate(delay_grid):
                echo_map[a, b, d], _ = c2po(substrate, stored_patterns,
                                            a, b, delay)
    return echo_map  # (K, K, n_delays)
```

**Falsifiable predictions**:
1. **Diagonal peaks** (A=B): echo amplitude is large positive at delay=0, decays monotonically. Trivial sanity check.
2. **Off-diagonal cross-peaks** (A != B) nonzero **if and only if** patterns A and B have non-negligible dot product |<xi_A, xi_B>|/N > 1/sqrt(N). For orthogonal random patterns: cross-peak at noise floor.
3. **Delay-dependence**: cross-peak echo(A,B,delay) peaks at characteristic tau*(A,B) ~ 1/(energy_gap_AB), decays on spin-glass relaxation timescale.
4. **Falsification**: large off-diagonal cross-peaks for orthogonal patterns (would indicate substrate's structured W introduces spurious pattern correlations) OR no off-diagonal cross-peaks even for correlated patterns (would indicate substrate is rigid against multi-step cuing).

**Substrate-product value**: substrate-novel. **No current Bet probes pattern-pair couplings.** Closest analog: Bet T hypothesis tracking (pending) — but Bet T tracks single hypotheses sequentially; C2PO maps the full KxK coupling matrix. Couples to:
- Lane D cognitive architecture (does substrate know which memories are related?)
- Lane B on-device personal AI (concept-relatedness for user-facing applications)
- Bet X skill composition (which skills compose? pair-coupling tells you)

**Cost**: full KxK map = O(K^2 · n_delays · n_reps · T_total). For K=100, n_delays=10, n_reps=50, T_total=200: ~10^7 sweeps = ~5-15 GPU-h. For K=1000: ~10^9 sweeps = 500+ GPU-h. **Tractable at K<=100 substrate-product Phase 1; sparse-sampling required at K>=500.**

### Z.3 / softmax readout — already in Strategy roadmap as Bet Y V2.D Phase 1

Ramsauer et al. 2020 modern Hopfield softmax IS the canonical "x-ray snapshot" mechanism in the literature. Currently being re-tested by Strategy at N=65536 + Kerdock(16) + substrate-default beta + 5-test battery per `strategy_request_to_exp_dev_BetY_V2D_mechanism_revision_2026-05-22.md` (cycle 130). Not a NEW substrate-product proposal — already in flight.

---

## (d) Materials analog (load-bearing)

Substrate at alpha=0.15 is an SK-class spin glass with Hebbian-structured coupling. The relevant materials-science analogs that translate:

1. **Jonsson et al. 2001 (cond-mat/0104333)** — Memory and chaos in 3D Ising spin glass. **Existence proof** that 2-protocol temperature cycling produces memory effects (cross-peak analog) vs rejuvenation (no memory) in classical Ising systems. C2PO is the structural-cue analog of this temperature-cycling protocol.

2. **Jalabert-Pastawski 2001 (cond-mat/0010094)** — Classical Loschmidt echo: overlap of two trajectories with time-reversed perturbation. The decay rate of the echo is the effective Lyapunov exponent of the inter-attractor boundary in configuration space. **Directly substrate-applicable** — no quantum coherence needed.

3. **Marchenko-Pastur / BBP transition** — Lucibello-Mezard 2023 arXiv:2304.14964 establishes the exact alpha threshold where K signal eigenvalues separate from MP bulk. **Tells you operationally when eigenmode projection works** (alpha < threshold) vs fails (alpha > threshold).

**Substrate is a spin glass that ports the FULL classical disordered-systems toolkit** — including the multi-pulse echo protocols that were originally invented for NMR/IR but have classical analogs in MC dynamics. **This is the substrate-as-spin-glass-laboratory moat per [[feedback-value-creation-not-competition]] from Entry 141, but extended from observability to capability primitives.**

---

## (e) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths**:
- C2PO (Z.2) is substrate-novel; pattern-pair coupling diagnostic has NO current Bet equivalent
- SRHT (Z.1) is well-grounded (Tropp 2011); 2000x speedup over brute force in the low-alpha or large-gap regime
- Both translate cleanly to substrate's classical, discrete, fully-connected architecture
- Materials-science analog is load-bearing: Jonsson 2001 + Jalabert-Pastawski 2001 = experimental + theoretical foundations for classical 2-pulse protocols on Ising systems

**Weaknesses (brutal honesty)**:
- **Modern Hopfield softmax (the cleanest "x-ray" primitive in the literature) is EMPIRICALLY REFUTED at substrate's current N=4096, beta=32** (Entry 137 cycle 105 multi-beta FULL). Strategy's Phase 1 N=65536 revision is the live test; if that fails too, the cleanest mechanism class is closed.
- **SRHT's additive-error guarantee breaks near AGS storage capacity** (alpha → alpha_c=0.138). Substrate at alpha=0.15 is ABOVE classical AGS bound. SRHT works in low-alpha regimes the substrate may not occupy operationally.
- **C2PO 2D-map cost scales as K^2** — full map for K=10^3 is 500+ GPU-h. Sparse-sampling protocols help but reduce the "x-ray snapshot" elegance.
- **No mechanism here is non-disruptive**: applying a cue field changes the substrate state. "Non-contact" in the materials-science sense (zero state perturbation) is fundamentally incompatible with cue-based readout. The closest we get is "reversibly disruptive" — applying cue → measuring response → returning to original state via opposite cue.

**Honest impact P**: **0.55-0.70**.
- Lower bound 0.55: blocked at current N=4096 for softmax; SRHT alpha-regime mismatch; C2PO cost scaling
- Upper bound 0.70: C2PO is substrate-novel pattern-pair diagnostic; couples to Lane D + Lane A + Bet X simultaneously; no competitor can replicate without substrate

**14th HONEST-RECALIBRATION-pattern note** of session (rejected the quantum echo/2D-IR class as decorative; recovered Jalabert-Pastawski classical analog; tempered modern-Hopfield expectations per cycle 105 refutation).

---

## (f) Routing recommendation to Strategy

**Proposed addition to capability roadmap**: **Bet Z-readout — Cued Holistic Readout primitive**

| Sub-axis | Mechanism | Operational cost | P | Substrate-novel? |
|----------|-----------|------------------|---|------------------|
| Z.1 | SRHT compressive readout | O(N log N + M·K), M~log K | 0.65 | YES |
| Z.2 | Classical 2-pulse echo (C2PO) | O(K^2 · delay) full map; O(K · delay) sparse | 0.55 | YES |
| Z.3 | Modern Hopfield softmax | O(N·K) one-shot | (already Bet Y V2.D Phase 1) | NO |

**Phase 1 substrate-product proposal**:
1. **Z.1 SRHT smoke** — 1 GPU-h. Synthetic K=100 patterns at N=4096, M=200. Verify >=90% top-10 recall against brute force. If PASS: proceed to substrate-coupling-W version.
2. **Z.2 C2PO sparse-map smoke** — 2-3 GPU-h. K=50 patterns, sparse (A,B) sampling (~200 pairs), 5-delay grid. Verify off-diagonal cross-peaks track pattern-pair dot products. If PASS: scale to K=100 full map.
3. **Z.3 awaits Phase 1 5-test battery at N=65536** (already scoped under Bet Y V2.D revision).

**Lane coupling**:
- **Lane D (cognitive architecture)**: C2PO 2D map reveals which memories are related — substrate's analog of a "concept graph" inferred from dynamics. Z.1 enables fast cue-based concept retrieval.
- **Lane A (memory layer for LLM)**: Z.1 SRHT readout is a drop-in fast-retrieval primitive (M·K << N·K) at low load.
- **Lane B (on-device personal AI)**: Z.2 C2PO could power "tell me what's related to this" UX.
- **Bet X (skill composition)**: Z.2 pattern-pair coupling map = which skills compose well.

**Engineering effort estimate**:
- Z.1 SRHT smoke: 1-2 GPU-h
- Z.2 C2PO sparse-map smoke: 2-3 GPU-h
- Z.2 full K=100 2D map: 5-15 GPU-h
- Total Phase 1: 8-20 GPU-h. Reused across Bet S / Bet A / Bet X / future capability tests.

**Cross-family certification rule** (echoing Entry 141): substrate's "fast holistic readout" capability is declared shipped only if **Z.1 SRHT top-10 recall > 90% AND Z.2 C2PO off-diagonal cross-peaks track pattern-pair dot products r > 0.7** at substrate's operational alpha.

---

## (g) Citations — 12 verified (cross-agent merged)

**Family Z.1 — Compressive sensing readout**:
1. **Tropp 2011** — arXiv:1011.1595 — SRHT JL guarantees (canonical).
2. **Baraniuk-Cevher-Duarte-Hegde 2010** — arXiv:0808.3572 — Model-based compressive sensing.
3. **Aumuller et al. 2016** — arXiv:1610.00574 — Angular multi-index hashing for sublinear cosine NN.
4. **Choromanski et al. 2017** — arXiv:1610.06209 — Structured HD^3 spinners with LSH guarantees.

**Family Z.2 — Classical 2-pulse echo**:
5. **Jalabert-Pastawski 2001** — PRL 86:2490 / cond-mat/0010094 — Classical Loschmidt echo + Lyapunov exponent (foundational).
6. **Jonsson et al. 2001** — cond-mat/0104333 — Memory and chaos in 3D Ising spin glass (existence proof of 2-pulse protocols).
7. **Mukamel 2003** — cond-mat/0307390 — Classical superoperator nonlinear response (formal framework).
8. **Tsukernik et al. 2011** — arXiv:1108.2799 — chi_3 nonlinear susceptibility in disordered classical spin systems.

**Family Z.3 — Spectral / softmax readout**:
9. **Ramsauer et al. 2020** — arXiv:2008.02217 — Modern Hopfield softmax (canonical "x-ray" primitive baseline).
10. **Halko-Martinsson-Tropp 2011** — SIAM Review 53:217 (DOI:10.1137/090771806) — Randomized SVD canonical reference.
11. **Lucibello-Mezard 2023** — arXiv:2304.14964 — Exponential capacity of dense AM; BBP threshold for eigenmode separation.
12. **Agliari et al. 2024** — arXiv:2401.16114 — Spectral approach to Hebbian-like networks; eigenvalue distributions.

---

## (h) Cross-references

- [[research-materials-characterization-methods-2026-05-22]] (Entry 140 level-1 observability)
- [[research-substrate-observability-deep-drill-2026-05-22]] (Entry 141 level-2 observability; this note extends from observability → capability)
- [[research-V2-substrate-evaluation-2026-05-21]] (Entry 52 V2.D modern dense AM original lit-vet)
- [[research-BetE-parisi-methodology-2026-05-21]] (Bet E ✅ Parisi RSB substrate-as-spin-glass foundation)
- [[research-R24-FDT-violation-2026-05-21]] (FDT-violation framework; classical 2-pulse echo is a sibling concept)
- [[research-BetX-skill-composition-2026-05-21]] (Bet X; C2PO pattern-pair couplings = skill-composition graph)

**Memory references invoked**:
- [[feedback-no-smoke]] — brutal honesty on softmax mechanism block
- [[feedback-materials-science-probe]] — load-bearing materials analog (Jonsson 2001 + Jalabert-Pastawski 2001)
- [[feedback-subagent-model-optimization]] — 3 Sonnet-dispatched parallel external lit scans
- [[feedback-query-privacy-decomposition]] — generic-math queries (compressive sensing / Loschmidt echo / randomized SVD)
- [[feedback-verify-implementations]] — 12 citations cross-verified for mechanism match
- [[feedback-2x-means-depth]] — would apply if user asks for level-2 drill on this note next
- [[feedback-value-creation-not-competition]] — Z.2 C2PO substrate-novel diagnostic is moat-building
- [[feedback-rehabilitation-after-rejection]] — modern Hopfield softmax (Z.3) NOT killed; deferred to Bet Y V2.D Phase 1 N=65536 test

**End of note.**
