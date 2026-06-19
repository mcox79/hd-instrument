# Research Note: CSP-with-Learning -- Combinatorial Optimization in a Hebbian Associative Substrate

**Date:** 2026-06-01
**Topic:** Substrate-as-Ising-machine with concurrent Hebbian learning (CSP-with-learning)
**Filed-by:** research sub-agent (Sonnet)

---

## HEADLINE

The substrate IS a standard bipolar Ising machine for pure CO problems (well-characterised, capacity-bounded). The NOVEL axis is W = W_csp + W_data superposition: simultaneous CO solving and pattern retrieval. No published work studies this exact dual-objective operating point. Closest precedent (arxiv 2307.16807) uses Hebbian learning to IMPROVE SAT convergence but does NOT store independent data patterns alongside constraint weights. P_deflated(hybrid coexistence above interference floor) = 0.35; pre-register HARD-FAIL at <50% on both objectives.

---

## Axis 1 -- Encoding mapping (substrate IS an Ising machine)

### Formal correspondence

The substrate energy is:

    E(s) = -(1/2) s^T W s,   s in {-1, +1}^N

The standard Ising Hamiltonian for a QUBO lifted to bipolar spins is identical in form. The mapping is exact:

- QUBO: minimise x^T Q x over x in {0,1}^N.  Substitution x_i = (s_i + 1)/2 yields bipolar Ising energy with J_ij = -Q_ij/4 plus linear (field) term h_i = sum_j Q_ij/2.
- MAX-CUT on graph G=(V,E): J_ij = -1/(2N) for each edge (i,j) in E (attractive coupling disfavours alignment; cut edges have s_i != s_j). Cut value = (1/4)(s^T L s) where L is the graph Laplacian.
- 3-SAT clause (x_i OR x_j OR NOT x_k): encodes as a 4-term penalty polynomial in {-1,+1} variables; each clause contributes a rank-3 outer product to W (the WA / Wan-Abdullah method, AIMS Math 2024).

Conclusion: the substrate is a STANDARD BIPOLAR ISING MACHINE. This is not novel; it is the standard Hopfield-CO equivalence (Hopfield and Tank 1985).

### Additive outer-product write and QUBO tension

A Hebbian write W <- W + (1/N) xi xi^T adds rank-1 to W. Encoding a QUBO problem directly requires setting W = J (the coupling matrix), which is a single structured write, NOT the additive outer-product stream used for pattern storage. This is the key structural tension: the Hebbian write protocol is designed for isotropic pattern storage, not for precision-embedding a structured J matrix. Encoding W_csp via one or a few outer products is possible ONLY for low-rank structured graphs (e.g. bipartite planted MAX-CUT is rank-2 in its Laplacian). Dense QUBO requires a different write protocol.

---

## Axis 2 -- Solution quality and comparison to published solvers

### Standard Hopfield-CO (published, well-known)

- TSP (Hopfield and Tank 1985): 10-city instances ~15% above optimal tour length; invalid permutation matrices common; parameter sensitivity high. Simulated annealing dominates at N > 20 cities.
- MAX-CUT (Hopfield dynamics): Achieves trivially >=0.5 * OPT, typically 0.70-0.80 * OPT for random graphs via synchronous descent. Goemans-Williamson SDP gives 0.878 * OPT (best known poly-time bound, tight under Unique Games Conjecture). Standard Hopfield does NOT reach GW bound.
- Memristive Hopfield with noise annealing (Nature Electronics 2020; Sci.Rep. 2021): With weight annealing / noise injection reaches 0.85-0.94 * OPT for dense graphs; competes with Fujitsu Digital Annealer on MQLib benchmark.
- QUBO optimality gap: Standard synchronous Hopfield (zero-temperature) finds local minima, not global optima. Expected gap ~ O(sqrt(N)) above ground state for spin-glass instances. For planted instances with SNR above capacity threshold alpha ~ 0.14, the planted solution is often found.

### Implication for substrate

Pure CO (W = W_csp, no Hebbian data): the substrate behaves as a standard Hopfield solver. Expected solution quality: 0.70-0.85 * OPT for MAX-CUT with synchronous descent. The SKAH-M saddle-hierarchy structure (confirmed cap_map row) may give the substrate a modest advantage over standard Hopfield because saddle-crossing allows descent to escape more local minima. But this is a marginal improvement, not a step change. Adding stochastic perturbation (finite temperature) improves CO quality for standard Hopfield; the same applies here.

---

## Axis 3 -- Concurrent learning (CSP-with-learning, the novel axis)

### Setup

    W = W_csp + W_data

where W_csp encodes a structured constraint problem (e.g. planted MAX-CUT) and W_data = (1/N) sum_{mu=1}^{M} xi_mu xi_mu^T is M random Hebbian patterns.

### Interference analysis (perturbation theory from first principles)

The energy under W_csp + W_data at state s is:

    E(s) = E_csp(s) + E_data(s)

    E_data(s) = -(1/2N) sum_mu (xi_mu . s)^2

For random xi_mu and any fixed state s, (xi_mu . s) ~ N(0, N) so (xi_mu . s)^2 / N -> 1 in expectation. Thus:

    E_data(s) ~ -M/2   (global bias, nearly uniform across ALL states)

The FIRST-ORDER effect is a global energy shift, NOT a reshaping of the landscape. So the CSP optimum s* remains a local minimum PROVIDED the crosstalk FLUCTUATIONS are small. The fluctuation at state s is:

    sigma(E_data(s)) ~ sqrt(M * N) / N = sqrt(M/N)

The CSP signal (gap between optimum and second-best) must exceed sqrt(M/N):

    CSP signal gap >> sqrt(M/N)

For M=20 at N=1024: sqrt(20/1024) ~ 0.14. The planted MAX-CUT gap for a well-planted bipartite instance scales as O(1) in the quadratic energy, so the condition is satisfied at M=20 << N.

### Retrieval side interference

W_csp acts as crosstalk on pattern retrieval. Its contribution to the local field on neuron i when retrieving pattern xi_1 is:

    h_csp(i) = (W_csp xi_1)_i / N ~ O(1/sqrt(N))   [by CLT for random xi_1 against sparse W_csp]

This is the same order as the standard Hopfield crosstalk from M other data patterns. If W_csp is DENSE (e.g. complete-graph MAX-CUT), h_csp can be O(1) per neuron -- this is the dangerous case.

Standard Hopfield retrieval capacity: M <= alpha_c * N with alpha_c ~ 0.138 for exact retrieval. W_csp contributes an effective k_eff "phantom patterns" of crosstalk. k_eff depends on the spectral structure of W_csp (specifically, its Frobenius norm relative to the W_data norm).

### Trade-off envelope (predicted)

Regime 1 (M << alpha_c * N AND CSP signal >> sqrt(M/N)):
Both objectives survive. Expected: CSP quality ~0.75-0.85 * OPT, retrieval accuracy ~90-95% at M << 0.14*N ~ 140.

Regime 2 (M ~ alpha_c * N, at capacity edge):
Retrieval degrades sharply (spin-glass phase). CSP optimum may survive but is harder to find. Expected: CO quality ~0.60-0.70 * OPT, retrieval ~50-70%.

Regime 3 (M > alpha_c * N, over-capacity):
Both fail. Retrieval error explodes. CSP landscape is obscured by spurious attractors from W_data.

Note: the substrate's higher effective capacity (alpha ~ 0.56 per cap_map, vs standard Hopfield 0.138) extends the coexistence regime significantly -- up to M ~ 574 patterns at N=1024 before hard failure, vs M ~ 140 for standard Hopfield.

### Novelty assessment (literature gap)

Published Hopfield-CO work reviewed:

- Hopfield and Tank (1985): fixed W_csp for TSP, no stored patterns.
- DHNN-SAT / WA method (AIMS Math 2024): W encodes SAT constraints; no independent data patterns stored alongside.
- arxiv 2307.16807 (Self-Optimization model, 2023-24): Uses HEBBIAN LEARNING to iteratively modify the constraint-encoding W so it converges to a SAT solution. The learned W IS the constraint solution; it does NOT maintain a static W_csp while appending W_data independently. Key finding in that paper: under some conditions Hebbian updates ERASE constraint information. This is the failure mode of the OPPOSITE case (W_data overwhelming W_csp), NOT the superposition we consider.
- arxiv 2501.04007 (2025): Extends SO model to harder instances. Same structure; no dual-use.
- Nature Electronics 2020 memristive Hopfield: weight annealing for CO, no concurrent pattern storage.
- arxiv 2602.00302 (2026): Neural Ising Machines via unrolling; no dual-use with data memory.
- arxiv 2503.23966 (2026): ML estimates solver parameters, not W superposition.

No paper found studying W = W_csp + W_data with BOTH objectives active simultaneously. The CSP-with-learning hybrid is a GENUINELY NOVEL axis.

P_deflated(coexistence above threshold at M=20, N=1024) = 0.35
  [Raw prior: ~0.55 from perturbation argument; deflated 0.20 per calibration penalty for no published precedent; capped below 0.50 per novel-synthesis cap rule]

P_deflated(useful interference-envelope characterised and exp_dev-actionable) = 0.40
  [One pilot experiment sweeping M from 0 to alpha_c * N could establish the trade-off curve empirically]

---

## Lit-scan section

### Published Hopfield-CO (well-characterised)

| Paper | Finding | Relevance |
|---|---|---|
| Hopfield and Tank 1985 (PNAS) | TSP in Hopfield net; ~15% suboptimal on 10-city | Establishes CO baseline; W = W_csp fixed |
| Goemans and Williamson 1995 | SDP gives 0.878 MAX-CUT bound | Upper bound on poly-time; Hopfield does not reach it |
| Nature Electronics 2020 (memristive Hopfield) | 0.85-0.94 OPT with noise; competitive with DA | Weight annealing; no dual-use |
| Sci.Rep. 2021 (weight annealing) | Confirms memristive Hopfield competitive on MQLib | No concurrent retrieval |
| arxiv 2311.03408 (NN on Ising) | QCBO for NN training on Ising machine | Different direction: NN weights as QUBO |
| arxiv 2602.00302 (Neural Ising unrolling, 2026) | NPIM competitive with learned CO solvers | Unrolled inference; no dual-use |

### SAT-with-Hebbian (closest published work to the hybrid)

| Paper | Finding | Gap from hybrid |
|---|---|---|
| arxiv 2307.16807 (Weber et al. 2023-24) | SO model uses Hebbian resets to CONVERGE to SAT solution; W IS the evolving solution | W is monolithic, not dual; no independent data storage |
| arxiv 2501.04007 (2025) | Extends SO to harder instances | Same structure; no dual-use |
| AIMS Math 2024 (3-SAT DHNN) | WA method encodes 3-SAT into Hopfield W; evaluates solution quality | Fixed W_csp; no data component |

### Concurrent learning and capacity

| Paper | Finding | Relevance |
|---|---|---|
| arxiv 2403.01907 (2024) | alpha_c ~ 0.138 rigorously for standard Hebbian | Establishes crosstalk floor for W_data component |
| arxiv 2401.00335 (2024) | Storkey rule > standard Hebb for capacity | Storkey could extend M before interference dominates |
| arxiv 2504.04879 (2025) | Mixed / spurious fixed points from pattern superposition | Directly relevant: spurious attractors in W_csp + W_data |
| Tandfonline 2004 (high-capacity with constraints) | Connection constraints can increase capacity | Adjacent: constraint as regularizer on W |

CSP-with-learning (W = W_csp + W_data, both objectives active): ZERO direct-precedent papers found.

---

## Cheap decisive test (smoke pre-registration)

Setup: N=1024, 5 seeds.

1. Construct W_csp = planted bipartite MAX-CUT Laplacian: two equal halves, edge probability p_within=0.5 (within each half), p_across=0.1 (between halves). Planted optimal cut is the bipartition; its energy is computable analytically as E_opt = -(p_within - p_across) * (N/2)^2 / (2N) ~ -0.2 * N / 8 = -N/40.
2. Generate M=20 random bipolar patterns {xi_1, ..., xi_20}; add W_data = (1/N) sum_mu xi_mu xi_mu^T.
3. Run synchronous Hopfield descent from 20 random initial states per seed; record final state s.
4. Measure (a) cut_ratio = E_csp(s) / E_csp(s_opt) (as fraction of optimal cut energy; want >= 0.80), (b) retrieval_accuracy = (1/20) sum_mu max(|xi_mu . s| / N, 0) for stored patterns (want >= 0.90 average overlap).

Smoke parameters: N=1024, M=20, 5 seeds, 20 random restarts per seed (100 total descent runs).

### HARD-PASS / MIDDLE / HARD-FAIL

HARD-PASS:
- cut_ratio >= 0.80 on >= 4/5 seeds
- retrieval_accuracy >= 0.90 on >= 4/5 seeds

MIDDLE BAND:
- One objective passes HP, other is middling (0.50-0.80 range)

HARD-FAIL:
- cut_ratio < 0.50 on >= 3/5 seeds, OR
- retrieval_accuracy < 0.50 on >= 3/5 seeds

Predicted: P(HARD-PASS) = 0.35, P(MIDDLE) = 0.40, P(HARD-FAIL) = 0.25.
MIDDLE BAND is the modal expected outcome: retrieval should survive M=20 comfortably, but synchronous descent CO quality is mediocre even in the pure case.

---

## Cross-thread synthesis

Prior substrate findings relevant to this axis:

1. SKAH-M class (cap_map, confirmed 2026-05-27): saddle-hierarchy DAM + non-reciprocal Hopfield. The saddle-crossing dynamics may help the substrate escape CO local minima that trap standard Hopfield, giving a marginal CO quality advantage. This is a cross-thread finding absent from the CO literature.

2. Higher effective capacity (alpha ~ 0.56 vs Hopfield 0.138): extends the coexistence regime to M ~ 574 at N=1024, roughly 4x the standard Hopfield capacity. This means the W_data component can be larger before it drowns the CO signal. This is a quantitative advantage for the hybrid operating mode.

3. Non-equilibrium dynamics (P=0.42 confirmed): non-reciprocal terms in W mean standard CO convergence theorems (Lyapunov / energy monotone) may not strictly apply. The substrate may oscillate between states rather than converging, which can be either beneficial (stochastic search) or harmful (never settling at the CO optimum). Pre-registration should track whether descent terminates cleanly.

4. First-order multi-basin hysteresis (Pred-4, 18x gate confirmed): implies multiple competing attractors. For CO this is a liability (local minima); for the dual-use case it may mean the substrate needs more restarts to find the CO optimum reliably.

Synthesis: The SKAH-M structure and higher capacity both favour the hybrid, but the multi-basin / non-equilibrium properties introduce uncertainty about CO convergence quality. The smoke test should distinguish these effects by comparing W = W_csp alone (baseline CO quality) vs W = W_csp + W_data (hybrid).

---

## Substrate-product implications

1. Dual-use capability: a substrate maintaining M data patterns simultaneously functions as a co-solver for a compatible CO problem. This is a qualitatively different capability class from single-purpose Ising hardware.

2. The critical parameter is M/N. The trade-off curve (CO quality and retrieval accuracy as functions of M/N) is the key characterisation. Current experiment proposes M=20 at N=1024 (M/N=0.020); a follow-up sweep to M/N in {0.02, 0.05, 0.10, 0.14, 0.30, 0.56} would map the full envelope.

3. The SO-model failure mode (arxiv 2307.16807 finding: Hebbian learning can ERASE constraint information) defines the upper bound: M must stay below the regime where W_data reshapes the attractor landscape enough to destroy the CO encoded in W_csp. The HARD ceiling is approximately the capacity threshold.

4. Practical relevance of the hybrid: the dual-use scenario is most natural when: (a) the substrate is already in operational use for pattern retrieval (W_data accumulating), and (b) a compatible CO task arrives that can be encoded in the residual weight budget. This is not a primary use case but an emergent capability of the substrate's architecture.

---

## Citations (verified, 14 total)

1. Hopfield and Tank (1985) PNAS -- Hopfield nets for TSP and CO (foundational)
2. Goemans and Williamson (1995) -- SDP MAX-CUT 0.878 bound
3. Murali et al., Nature Electronics 2020 -- memristive Hopfield for MAX-CUT, power-efficient CO
4. Cai et al., Scientific Reports 2021 -- weight annealing in memristive Hopfield networks
5. arxiv 2307.16807 (Weber et al. 2023-24) -- SO model Hopfield SAT (closest to hybrid)
6. arxiv 2501.04007 (2025) -- Untapped potential in SO model
7. AIMS Math 2024 -- 3-SAT DHNN WA method
8. arxiv 2403.01907 (Barra et al. 2024) -- Hebbian-Hopfield capacity (alpha_c ~ 0.138)
9. arxiv 2401.00335 (2024) -- Benchmarking Hebbian rules for associative memory
10. arxiv 2504.04879 (2025) -- Mixed memories in Hopfield networks
11. arxiv 2602.00302 (2026) -- Neural Ising Machines via unrolling and zeroth-order training
12. arxiv 2503.23966 (2026) -- ML-assisted high-speed CO with Ising machines
13. Glover et al. QUBO tutorial -- QUBO-to-Ising mapping reference
14. Tandfonline 2004 -- High-capacity associative memory with connection constraints

---

## Next-drill candidate

Free-probability / Tracy-Widom (Tier-1, F2) on the spectrum of W_csp + W_data. The spectral structure of the combined matrix determines the interference envelope analytically. Marchenko-Pastur gives the W_data bulk spectrum; W_csp eigenvalues form a rank-K spike above the bulk. The gap between the spike and the bulk edge (Tracy-Widom edge fluctuation) directly quantifies how many M patterns W_data can absorb before the CO signal eigenvalue is swamped. This connects the CSP-with-learning result to the free-probability Tier-1 field (100% yield, 1 drill, directly adjacent).

Acted-on 2026-06-02: CSP source absorbed into Round 6+ cap_map work
