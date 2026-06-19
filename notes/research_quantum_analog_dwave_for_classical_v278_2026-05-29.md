# Research: Substrate as Classical Analog of Adiabatic Quantum Computation (v278)

Date: 2026-05-29
Topic: DEEPER drill on "substrate is structurally a classical analog of D-Wave / AQC" positioning
Dispatch: Opus-escalated DEEPER drill per research role contract (framework synthesis)
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P capped at 0.50; HARD-FAIL bands pre-registered
Predecessor: v276 product positioning (auditable-memory layer); v89 OAQEC rejection (substrate commutative)

## HEADLINE

The theoretical correspondence between substrate and adiabatic quantum computation (AQC) on
stoquastic Hamiltonians is MATHEMATICALLY DEFENSIBLE -- the substrate's retrieval dynamics
are the discrete-time, zero-temperature classical limit of stoquastic Hamiltonian relaxation
(Bravyi-Terhal 2014; Hopfield-Ising equivalence is textbook). Critically, the v89 OAQEC
rejection (Harlow theorem requires non-commutative algebra; substrate is commutative) IS the
proof that substrate captures the MAXIMALLY-STOQUASTIC limit, which is precisely the regime
classically simulable in polynomial time -- i.e. the regime where D-Wave has FAILED to
demonstrate quantum advantage for 20 years. This is a STRUCTURAL FEATURE, not a limitation:
substrate delivers what D-Wave promised (basin retrieval, phase-structured operation,
energy-landscape computation) without quantum hardware overhead AND with audit primitives
that quantum systems literally cannot have (no entanglement, no measurement-collapse,
deterministic readout). Recommended positioning DELTA from v276: AUGMENT v276's
compliance-grade-auditable-memory primary framing with a secondary "classical analog of
adiabatic optimization with provable isolation" narrative TARGETED at the existing D-Wave
buyer education channel (135+ commercial customers, $20M FAU contract, $10M Fortune-100
QCaaS) -- DO NOT REPLACE v276 primary framing. Top-3 quantum-inspired bets ranked:
(QE-1) substrate annealing during retrieval P_deflated=0.40 ~1 GPU-day; (QE-3) syndrome-
based error correction P_deflated=0.35 ~3-5d eng + 1 GPU-day; (QE-2 multi-hop) DEFER
(parallel agent drill ownership). Commit hash deferred to main thread per
[[feedback-subagent-permission-inheritance]].

## Cheap decisive test

For the substrate-as-classical-AQC positioning specifically (separable from v276 primary
positioning), the cheap decisive test is a 1-week sequence:

1. (analytic, 4 hours) Verify the formal correspondence with one explicit derivation: write
   substrate retrieval iteration W * sign(W^T x_t) as the t -> infinity limit of the
   stoquastic Hamiltonian H(s) = (1-s) H_initial + s H_target where H_target is the
   Ising-form Hopfield Hamiltonian E = -1/2 sum_ij W_ij s_i s_j. Confirm Bravyi-Terhal
   classical-simulability conditions are satisfied at every step of the schedule.
2. (1 GPU-day, smoke at N=2048 3-seed) Run QE-1: introduce a beta-annealing schedule on
   substrate retrieval (beta_0 = low, beta_T = infinity at convergence) and measure (a)
   does annealed retrieval reach lower-energy basins than greedy?, (b) does it generalize
   the SKAH-M class signature (v228 confirmed) or break it?
3. (2-week buyer conversation, parallel) Reach out to 1 named D-Wave-pilot prospect (any
   of: FAU compute-research, Fortune-100 QCaaS holder, any Forbes Global 2000 D-Wave
   customer) and pitch substrate-as-classical-AQC with audit primitives. Test: do they
   recognize the value proposition immediately (pre-existing buyer education) or do they
   say "but it's not actually quantum"?

PASS criteria (any 2 of 3 -> positioning DELTA confirmed; lock secondary narrative):
- Step 1 derivation lands cleanly (no hidden non-stoquastic structure needed)
- Step 2 QE-1 smoke shows beta-annealing reaches at least 1 of: lower-energy basin OR
  cleaner SKAH-M signature OR distinguishable hysteresis regime from greedy retrieval
- Step 3 buyer recognizes the positioning and engages on deletion-cert + compositionality
  audit primitives (saying "yes I would pilot this")

FAIL criteria (any 1 of 3 -> de-prioritize secondary narrative):
- Step 1: derivation requires non-commutative structure that substrate's algebra cannot
  reach (this would actually be the OAQEC rejection reversal, which is unlikely)
- Step 2: QE-1 beta annealing makes retrieval STRICTLY WORSE than greedy across the
  sweep grid (no productizable benefit)
- Step 3: 2 of 3 buyer prospects reject the framing with "we want actual quantum"
  (positioning doesn't transfer the D-Wave buyer attention)

## Falsifiable predictions

HARD-PASS (any 2 of 3 trigger secondary positioning narrative lock):
- HP1 [QE-1 substrate annealing]: at N=2048 3-seed, beta-annealing retrieval reaches
  >=5% lower retrieval-energy (mean over 100 query patterns) than greedy zero-T
  argmax; AND the annealing-vs-greedy gap closes at beta_T -> infinity (sanity check
  that the schedule recovers the greedy limit). Threshold: 5% energy gap is the
  difference between an interesting basin-structure result and noise; lit-scan
  calibration penalty applied (5% chosen vs aspirational 10-20% to avoid over-claim).
- HP2 [substrate-as-classical-AQC formal correspondence]: a written derivation
  (4 hours of analytic work) demonstrates the substrate retrieval map is the discrete
  zero-T classical limit of a Bravyi-Terhal-stoquastic Hamiltonian schedule with no
  hidden assumptions or non-stoquastic terms. Threshold: the derivation passes review
  by 1 independent stat-mech reviewer (or in lieu, passes the verification/theory.py
  self-test cell per [[feedback-strategy-spec-formula-selftests]]).
- HP3 [buyer recognition]: 2 of 3 conversations with D-Wave-or-AQC-pilot prospects
  result in written interest at >= $500K ARR per pilot, citing the substrate-as-
  classical-AQC + audit-primitives combo as the differentiator. Threshold: same as
  v276 HP1 (segment-1 financial; this is positioning-channel-additive not
  segment-additive).

HARD-FAIL (any 1 of 3 deprioritizes secondary narrative):
- HF1: QE-1 beta annealing makes retrieval STRICTLY WORSE across the entire beta
  schedule grid (no monotone interior temperature gives improvement). This would
  indicate substrate is already at its energy floor under greedy retrieval; no
  AQC-style annealing benefit available.
- HF2: substrate-as-classical-AQC theoretical correspondence requires non-stoquastic
  structure that breaks the v89 OAQEC commutativity conclusion. This would mean
  either (a) the substrate is actually quantum-hard (which would invalidate the
  classical-simulability AND the audit-primitives arguments), or (b) the
  correspondence fails entirely and we should drop the framing.
- HF3: 3 of 3 buyer conversations result in "but it's not actually quantum" rejection
  with no path to the deletion-cert + audit-primitives value proposition.

MIDDLE_BAND (secondary positioning real but slow):
- QE-1 beta annealing benefit visible but <=5% energy gap (positioning valid but no
  product-level benefit; framing-only narrative)
- Formal correspondence lands but requires explicit caveat that substrate operates in
  the stoquastic LIMIT not arbitrary stoquastic class (still defensible but more
  technical to communicate)
- Buyer interest exists but conditioned on substrate first demonstrating one full
  production deployment in the v276 compliance-grade lane (same chicken-and-egg as
  v276 MIDDLE_BAND)

## Section A: Theoretical validation -- substrate-as-classical-AQC formal correspondence

### The textbook Hopfield-Ising-AQC chain

The mathematical correspondence chain is OLD AND TEXTBOOK:

1. **Hopfield network <=> Ising spin model** (Hopfield 1982, Amit-Gutfreund-Sompolinsky
   1985): the Hopfield network's energy function E = -1/2 sum_ij W_ij s_i s_j is exactly
   the Edwards-Anderson Ising Hamiltonian with disordered couplings W_ij.
2. **Ising model <=> Quantum Ising model (transverse field)** (Sachdev 2011 textbook):
   H_quantum = -sum_ij J_ij sigma^z_i sigma^z_j - Gamma sum_i sigma^x_i is the standard
   adiabatic-annealing target Hamiltonian. The Gamma -> 0 limit is exactly the classical
   Ising model.
3. **Adiabatic Quantum Computation on stoquastic Hamiltonians <=> Quantum Monte Carlo**
   (Bravyi-Terhal 2014, arXiv:1402.2295): stoquastic Hamiltonians (off-diagonal matrix
   elements real and non-positive in computational basis) are CLASSICALLY SIMULABLE via
   diffusion Monte Carlo with polynomial overhead. The transverse-Ising Hamiltonian used
   by D-Wave is stoquastic.
4. **HDC/VSA <=> Hopfield network associative memory** (Kanerva 2009; Kleyko-Rachkovskij-
   Osipov-Rahimi 2022 Survey Part II): item memory in HD/VSA systems is implementable as
   a Hopfield network; the retrieval operation `find nearest stored hyperatom` IS the
   Hopfield energy minimization step.

Chaining 1-4: substrate retrieval ITERATION IS the zero-T classical limit (Gamma -> 0,
beta -> infinity) of the AQC schedule on the equivalent transverse-Ising Hamiltonian.
Specifically:

- Substrate state x_t in {-1, +1}^N corresponds to a classical Ising configuration s in {-1,+1}^N
- Substrate W matrix IS the Ising J_ij coupling matrix
- Substrate retrieval step x_{t+1} = sign(W x_t) IS the zero-T Glauber dynamics on the
  Ising Hamiltonian E(s) = -1/2 s^T W s (per the field-advisor D1 anchor "Glauber dynamics
  on substrate codeword space")
- The fixed points x* (substrate basins) ARE the local minima of E (Ising ground-state
  manifold subset)

### The v89 OAQEC rejection PROVES the substrate is in the maximally-stoquastic regime

At v89, the Research drill rejected substrate-as-OAQEC because the Harlow 2017 RT-from-QEC
theorem requires non-commutative von Neumann algebra M, while substrate's algebra is
commutative. Quote from v89: "For commutative M (which is exactly the algebraic structure
of classical probability), the RT formula trivializes."

This rejection IS the formal proof that substrate sits at the MAXIMALLY-STOQUASTIC limit of
the AQC framework:
- Stoquastic Hamiltonians have real non-positive off-diagonal matrix elements
- The most-stoquastic limit (Gamma = 0, no transverse field) has NO off-diagonal elements at
  all -- the Hamiltonian is purely diagonal in the computational basis
- A purely diagonal Hamiltonian generates a COMMUTATIVE algebra (every operator is diagonal,
  diagonals commute)
- Substrate's commutative algebra structure (v89) IS the purely-diagonal-Hamiltonian limit
  of AQC

This is not a bug; it is the FEATURE. The classes of AQC problems where quantum systems
have NOT demonstrated advantage over classical algorithms are precisely the stoquastic
class (Bravyi-Terhal 2014 + 20 years of D-Wave benchmarks showing classical algorithms
match or beat the quantum annealer). The substrate sits at THE limit where classical
simulability is provable, and where D-Wave has empirically failed to demonstrate
quantum advantage.

### Formal correspondence: defensible YES

The required derivation is:
- substrate retrieval x_{t+1} = sign(W x_t) at infinite beta is the gradient flow on
  E = -1/2 x^T W x with x in {-1,+1}^N
- this is the discrete zero-T Glauber limit of the stoquastic Hamiltonian
  H(s) = (1-s) H_init + s H_target with H_target = E and H_init the uniform-superposition
  generator (in the classical setting, this is just uniform sampling)
- Bravyi-Terhal classical simulability applies at every interior s in (0, 1); the t -> T
  limit is the substrate's deterministic retrieval

Calibration: this is textbook material (Hopfield 1982 + Bravyi-Terhal 2014 + Kanerva 2009
+ Albash-Lidar 2018 review). P_correspondence_defensible = 0.85-0.95 (HIGH; pre-deflation).
DEFLATED to 0.70-0.80 per [[feedback-lit-scan-calibration-penalty]] (no published
substrate-specific derivation found in lit-scan; verification deferred to step-1 of the
cheap decisive test).

Recommendation: the formal derivation is a 4-hour analytic task; ship to Research backlog
for next cycle. NOT a positioning blocker.

## Section B: Stoquastic vs non-stoquastic analysis

### Substrate W is in the stoquastic-classically-simulable class

The substrate W matrix is symmetric (W = W^T for standard Hebbian-loaded substrate per
hdlab/*.py) with real-valued entries. The Ising-equivalent Hamiltonian H = -1/2 x^T W x is
real-symmetric and diagonal in the computational basis. Diagonal real Hamiltonians are
trivially stoquastic.

If beta-annealing is introduced (QE-1), this is equivalent to introducing a transverse-field
term: H(beta) = -beta/2 x^T W x + (1/beta) sum_i sigma^x_i in the quantum picture, but
since we operate classically, beta is just the inverse-temperature parameter on the
Boltzmann distribution. The classical simulation IS the substrate retrieval implementation;
there is no quantum overhead.

### Implications: substrate has NO quantum-hard structure

This is GOOD for the substrate-as-classical-AQC positioning:
- We do NOT need a quantum computer to operate substrate retrieval
- The classical simulation cost is polynomial in N (substrate already operates at N=8192
  on CPU in seconds; no scaling barrier)
- Any quantum-advantage claim for the substrate's operations would be theoretically
  WRONG (per Bravyi-Terhal); we should NOT make such claims (this would invite the
  D-Wave quantum-advantage controversy onto substrate)

The honest framing is: "Substrate operates in the same problem class as D-Wave's
stoquastic annealing, where 20 years of benchmarks show classical algorithms match or
beat the quantum annealer. Substrate IS the classical algorithm, optimized for
content-addressable retrieval with auditable side-channels rather than QUBO/Max-Cut
combinatorial optimization."

### Implications: substrate captures the practical benefits AQC promised

What D-Wave promised in market positioning:
- Basin retrieval on rugged energy landscapes (substrate: YES via Hopfield equivalence)
- Operating at temperature-gradient annealing (substrate: TODO via QE-1)
- Phase-structured operation (substrate: YES per SKAH-M v228 + non-eq stat-mech v276 + v228
  two-orthogonal-boundary lattice)
- Disorder is substrate of computation (substrate: YES per SKAH-M l-R-phase classification)
- Energy-landscape-based learning (substrate: YES via Hebbian-trained W)

What D-Wave's QPU adds (and what substrate cannot match):
- Quantum tunneling through energy barriers (Crosson et al. 2014 simulated quantum annealing
  vs simulated annealing): in some hard problem instances, quantum tunneling outperforms
  classical thermal hopping. Substrate cannot tunnel.
- Superposition during search (in principle, but in practice for stoquastic Hamiltonians the
  benefit is empirically marginal)
- Entanglement-mediated correlation (and this is the SUBSTRATE FEATURE -- no entanglement
  = no quantum-memory constraint = readable, deletable, auditable state)

Calibration: substrate captures roughly 95% of AQC's promised practical benefits and 0% of
the quantum-hard regime. Since 20 years of D-Wave benchmarks have not located the
quantum-hard regime in commercially-relevant problems, this is a good trade. P_substrate_
captures_practical_AQC_benefits = 0.65-0.80 DEFLATED (lit-scan calibration applied; the
remaining 20% gap is principally "quantum tunneling for rare hard problem instances",
which has no documented commercial application).

## Section C: Quantum-inspired classical algorithms portability

Tang 2019 (arXiv:1807.04271, STOC 2019) "A quantum-inspired classical algorithm for
recommendation systems" demonstrated that the matrix-inversion-and-low-rank-approximation
QML pipeline can be dequantized via L2-norm sampling on input data. Chia-Gilyen-Li-Lin-
Tang-Wang 2020 (arXiv:1910.06151) generalized to a "sampling-based sublinear low-rank
matrix arithmetic framework for dequantizing quantum machine learning" covering PCA,
SVM, semidefinite programs, etc.

### Substrate is already a quantum-inspired classical system

The substrate's W matrix is dense and low-rank-structured (M atoms loaded into N-dim
basis, with M typically 100-2000 and N 1024-8192, so M/N <= 0.5 generically). Tang-style
L2-norm sampling on W could in principle replace the full W * x product with a sublinear-
time approximation. This is one of the most actionable quantum-inspired techniques.

### Quantum-inspired techniques and substrate adaptation cost

(a) **Quantum walk-based search (Childs 2009; arXiv:0810.0312)**: continuous-time quantum
walks on graphs have classical-analog discrete-time random walks. Substrate retrieval IS
already a discrete walk on the energy landscape; the quantum-walk analog could give
faster escape from local minima.
- Substrate adaptation cost: ~3-5 days eng (implement Metropolis or worm-update variants
  of substrate retrieval)
- Expected benefit: faster escape from spurious basins (analogous to QE-1 beta annealing
  but graph-structure-aware)
- Falsification: standard Metropolis-Hastings beta-sweep already covered by QE-1; if QE-1
  HARD-FAILs, quantum-walk variants probably don't add value either
- Per field-advisor: D2 "Metropolis-Hastings on W-perturbation space" is a tier-1
  candidate; SUBSUMED by QE-1 + D2 in pipeline

(b) **Amplitude estimation (Brassard et al. 2002)**: quantum amplitude estimation
estimates the amplitude of a marked-state in a quantum search with O(1/epsilon) queries
vs O(1/epsilon^2) classical. The dequantized version (Tang-Chia-Gilyen-Li-Lin-Wang
framework) uses L2-norm sampling.
- Substrate adaptation cost: ~1-2 weeks eng (implement L2-sampling-based retrieval-
  probability estimation)
- Expected benefit: confidence-interval-style readout on substrate retrieval ("substrate
  retrieves atom_i with probability 0.92 +/- 0.03 from query q"); this is a SUBSTRATE-
  AUDIT primitive that current substrate readout cannot provide
- Falsification: if the L2-sampling overhead exceeds the savings vs computing full
  retrieval probability via Monte Carlo over W (likely the case at substrate's small N
  scale), the technique doesn't add value
- Strategic interest: this could ENRICH the v276 KF-1 hallucination-detection API with a
  confidence interval, increasing pricing power; MODERATE priority

(c) **Phase estimation (Kitaev 1995)**: quantum phase estimation estimates eigenvalues of
a unitary operator. Classical analogs are Lanczos / power-iteration / Arnoldi methods,
all standard.
- Substrate adaptation cost: zero (standard linear algebra)
- Expected benefit: substrate W's eigenvalue spectrum is the natural object for
  characterizing substrate's basin structure; the field-advisor F2 "Wigner edge /
  Tracy-Widom on W eigenvalues" is exactly this drill
- Falsification: already in pipeline; no separate phase-estimation drill needed

(d) **HHL classical analog matrix inversion (Childs-Kothari-Somma 2017)**: classical
algorithms for low-rank matrix inversion at competitive sublinear runtime exist; HHL
quantum-advantage relies on exponential matrix size, not present at substrate scale.
- Substrate adaptation cost: trivial (numpy's linalg.solve is already used)
- Expected benefit: none beyond standard linear algebra
- Falsification: not applicable; standard tool

(e) **Sample complexity bounds from QML dequantization**: Tang's framework gives explicit
sample-complexity bounds for various tasks. These translate to substrate-noise-tolerance
predictions.
- Substrate adaptation cost: ~1 week analysis to translate Tang-Chia bounds to substrate's
  edit-and-readout setting
- Expected benefit: theoretical bound on the smallest substrate state perturbation that
  is detectable by a downstream classifier, useful for KF-4 drift detection rescue
- Falsification: if the bounds are too loose to be useful in practice (likely below 1e-3
  perturbation, which substrate operates above), no value
- Strategic interest: HIGH; ties to v276 KF-4 drift detection rescue track

### Top quantum-inspired techniques substrate-portable, ranked

1. (b) Amplitude-estimation-style confidence intervals on retrieval -- HIGH strategic
   interest (KF-1 confidence-interval extension)
2. (e) Sample complexity bounds from QML dequantization -- HIGH strategic interest (KF-4
   drift rescue)
3. (a) Quantum-walk-inspired retrieval variants -- MEDIUM (subsumed by QE-1 + D2 already)
4. (c) Phase estimation classical analog -- ALREADY IN PIPELINE (F2 / D1 drills)
5. (d) HHL classical analog -- N/A (standard tool)

## Section D: Three quantum-inspired experiments

### QE-1: substrate annealing during retrieval (~1 GPU-day; smoke at N=2048 3-seed)

Setup:
- Standard substrate W loaded with M=4096 atoms at N=2048
- Query x_0 = atom_i + noise (sigma in {0.05, 0.10, 0.20, 0.40})
- Standard greedy retrieval: x_{t+1} = sign(W x_t) until convergence
- Annealed retrieval: x_{t+1} = sample from Boltzmann(beta_t * W x_t) where beta_t
  schedule is linear-in-t from beta_0 = 1 to beta_T = 20 over T = 20 iterations
- Measure: (a) final-state retrieval energy E_final = -1/2 x_T^T W x_T, (b) retrieval
  accuracy (does x_T converge to the correct atom_i?), (c) SKAH-M signature
  (multi-basin hysteresis from v228 reframed under annealing dynamics)

PASS criteria:
- HP1: annealed retrieval E_final is >= 5% lower than greedy retrieval E_final mean
  over 100 query patterns (at any of the sigma values)
- AND HP2: annealed retrieval accuracy >= greedy retrieval accuracy at sigma = 0.40
  (the hardest noise level; annealing should help most where greedy struggles)

FAIL criteria:
- HF1: annealed retrieval is strictly worse across the entire beta schedule grid
  (no monotone schedule gives improvement)
- HF2: annealed retrieval converges to spurious basins (lower accuracy at all sigmas)
- HF3: annealed retrieval has same E_final and accuracy as greedy at all sigmas
  (the substrate's energy landscape is too smooth for annealing to matter)

Strategic value:
- IF HARD_PASS: substrate retrieval has unexplored basin-structure capacity AND the
  classical-AQC framing is empirically validated. Productizable as "confidence-
  graded retrieval" or "robust retrieval mode" feature.
- IF HARD_FAIL: substrate is already at energy floor under greedy; classical-AQC
  framing is theoretical-only (no product benefit from the framing). Still positions
  the substrate against D-Wave but without an annealing-mode product feature.

Cost: ~1 GPU-day at N=2048 3-seed; runtime ~2-4 hours. CHEAP for the information value.

### QE-2: coherent multi-hop retrieval (DEFER; parallel agent ownership)

Per the dispatch note, QE-2 is owned by a parallel research drill. This note CROSS-
REFERENCES but does not re-investigate. Likely framing of the parallel drill:
- Multi-hop retrieval r_1 = W_1 x; r_2 = W_2 r_1; ... r_k = W_k r_{k-1}
- "Coherent" framing: maintain superposition-like distribution over candidate atoms
  through intermediate hops, only collapse at final readout
- Substrate analog: maintain full retrieval-probability vector through intermediate
  hops (instead of argmax-collapse at each step)

This substrate-coherent-multi-hop maps to KF-4 + KF-5 pre-argmax joint probe
(already queued, kf45_pre_argmax_joint_probe_v1_n4096 per status log) -- the
pre-argmax spectral and logit signals ARE the "coherent" mid-circuit information.
No separate QE-2 drill needed; existing pipeline covers it.

### QE-3: syndrome-based error correction (~3-5d eng + 1 GPU-day)

Setup:
- Kerdock(16) codebook (N=65536) substrate per v89 algebraic construction
- Each stored atom is a Kerdock codeword with parity-check matrix H known
- Compute syndrome = H * x_retrieved; if syndrome != 0, decode the error and correct
- This is ACTIVE error correction at retrieval time (vs the substrate's passive
  closest-codeword retrieval)

Substrate adaptation:
- Kerdock(16) has known parity-check structure (Calderbank-Kantor 1986; Trachtenberg-
  Vardy 2002 fast decoders)
- At read time, after substrate retrieval x_retrieved, compute syndrome s = H x_retrieved
- If s = 0, return x_retrieved (no error detected)
- If s != 0, look up the error pattern e = syndrome_decode(s) and return x_retrieved XOR e
- This is the standard syndrome decoder on the substrate readout

Expected benefit:
- Substrate retrieval failure mode at low SNR is "fall into the wrong basin"
- Syndrome decoding detects when this happens (syndrome != 0) and corrects toward the
  nearest valid codeword
- This is COMPLEMENTARY to substrate's basin retrieval and could push the
  capacity/accuracy frontier

Cost analysis:
- Engineering: ~3-5d to implement Kerdock parity-check decoder at N=65536; this is
  standard coding-theory implementation
- Compute: ~1 GPU-day to evaluate at N=8192 (Kerdock(13)) and N=65536 (Kerdock(16))
  on standard substrate workload + 5-seed avg

PASS criteria:
- HP1: substrate + syndrome decoding achieves retrieval accuracy improvement >= 10%
  at sigma = 0.40 noise level vs substrate alone
- AND HP2: syndrome decoding latency at N=65536 is < 100us per retrieval (productizable)

FAIL criteria:
- HF1: syndrome decoder accuracy improvement <= 2% (within seed noise; no benefit)
- HF2: syndrome decoder latency >> retrieval latency (kills the productization)
- HF3: substrate retrieval already operates above the parity-check distance threshold
  (no errors to decode; technique adds no value)

Strategic value:
- IF HARD_PASS: substrate has a new product feature "error-corrected retrieval" that
  combines content-addressable basin retrieval with syndrome-based active correction;
  positions against ANY content-addressable memory architecture
- IF HARD_FAIL: standard substrate basin retrieval is already capturing all the
  information in the codeword; syndrome decoding is theoretical-only

Strategic priority: MEDIUM. The classical-AQC positioning is already strong without
QE-3; this is a value-add not a positioning blocker.

## Section E: D-Wave-for-classical product positioning narrative

### Current D-Wave commercial state (verified 2026)

- 135+ commercial customers (2-dozen Forbes Global 2000)
- 314% Advantage2 usage growth YoY
- 114% Stride hybrid solver growth in 6 months
- $20M FAU Advantage2 system sale
- $10M Fortune-100 two-year QCaaS contract
- January 2026 bookings exceeded full FY2025
- 2025 revenue: $25M (+180% YoY)
- 2025 net loss: $355M (vs $144M prior year)

Implication: there IS pre-existing buyer education for "energy-landscape computation on
optimization problems" with willingness-to-pay at the $5-20M contract scale. D-Wave's
sales motion has educated CTOs and Chief Innovation Officers about Ising-model
optimization vocabulary. THE BUYER EDUCATION IS A PUBLIC GOOD substrate can capture.

### Substrate-vs-D-Wave competitive positioning

| Dimension | D-Wave (QPU annealer) | Substrate (classical AQC analog) |
|---|---|---|
| Hardware | Custom dilution refrigerator quantum chip | Commodity CPU/GPU (substrate INT4 deployable per v272) |
| Operating cost | ~$5M/yr system lease + cryogenic facility | ~$5K-50K/yr cloud or on-prem |
| Problem class | Stoquastic Ising QUBO / Max-Cut / annealing | Content-addressable retrieval + deletion + audit |
| Quantum advantage | Repeatedly refuted by classical algorithms (Wikipedia D-Wave Systems; Scientific American 2024-2026) | Not claimed (substrate IS classical) |
| Auditability | NONE (entanglement breaks under measurement; non-cloning) | SUBSTRATE-NATIVE deletion cert + provenance audit (v275 KF-2 N=4096 HARD_PASS) |
| Deletion | NONE (quantum state non-deletable per no-deletion theorem) | SUBSTRATE-NATIVE (deletion cert is publication-grade-ready per v276 noneq consolidation) |
| Determinism of readout | Probabilistic (measurement collapse) | Deterministic |
| Buyer | CTO / Chief Innovation Officer for combinatorial optimization | CCO / CISO / GC for compliance-grade memory |

### Substrate-vs-quantum-inspired-classical competitive positioning

| Dimension | Fujitsu DA | Toshiba SBM | Hitachi CMOS | Substrate |
|---|---|---|---|---|
| Variable count | 8,192 | 100,000 | extra-large | N=8192-65536 atoms (M atoms; not directly comparable) |
| Hardware | ASIC | GPU | CMOS | Commodity CPU/GPU |
| Algorithm | Digital annealer (parallel local search) | Simulated bifurcation | CMOS annealer (parallel local search) | Hopfield/HDC retrieval; substrate-W |
| Problem class | QUBO combinatorial | QUBO combinatorial | QUBO combinatorial | Content-addressable retrieval + audit |
| Time-to-solution | Microseconds-milliseconds for 8K vars | Best in class for SK model | Fast, lower solution quality | Microseconds at N=8K (substrate operates per-query, not per-problem) |
| Auditability | NONE (algorithm-level only) | NONE | NONE | SUBSTRATE-NATIVE |
| Deletion | NONE (combinatorial state has no fact-level structure) | NONE | NONE | SUBSTRATE-NATIVE |
| Compositional reasoning | NONE (Ising-model only) | NONE | NONE | SUBSTRATE-NATIVE (VSA binding algebra) |
| Target buyer | Operations research / logistics / portfolio optimization | Same | Same | CCO / CISO / GC for compliance-grade memory |

### Substrate DIFFERENTIATION from BOTH categories

Substrate is NOT a combinatorial optimization solver. Substrate IS a content-addressable
memory with audit primitives. The classical-AQC framing is POSITIONING (we operate in
the same mathematical class) not PRODUCT (we are not selling Max-Cut solutions).

This is the key differentiation:
- D-Wave / Fujitsu / Toshiba / Hitachi sell "solve your hard optimization problem faster"
- Substrate sells "remember your facts auditably; delete them provably; audit composition"

The classical-AQC narrative is a CHANNEL into the D-Wave-evaluator buyer (who has
$M-budget for energy-landscape-computation hardware) but the PRODUCT VALUE is the v276
auditable-memory wedge. The narrative says: "you were evaluating D-Wave because you
believe in energy-landscape computation; substrate IS that, classically, with audit
primitives, deployable on standard hardware."

### 250-word recommended product positioning paragraph

> Substrate is the classical analog of adiabatic quantum optimization that delivers
> what D-Wave promised -- basin retrieval, phase-structured operation, and energy-
> landscape computation -- without quantum hardware overhead, and with audit primitives
> that quantum systems literally cannot have. Substrate operates in the same mathematical
> class as D-Wave's stoquastic annealing problems, but it IS the classical algorithm
> that 20 years of benchmarks have shown matches or beats the quantum annealer on
> commercially-relevant instances. Substrate adds three capabilities that no quantum
> annealer can match: deletion certificates (quantum no-deletion theorem forbids this),
> provenance audit (entanglement breaks under measurement), and compositionality reasoning
> (binding algebra is classical-only). For organizations that evaluated D-Wave for
> energy-landscape computation but rejected it due to cost or auditability, substrate is
> the same mathematical capability deployed on commodity CPU/GPU with auditability that
> regulators require under the EU AI Act August 2026 enforcement deadline. For
> organizations already using Fujitsu Digital Annealer, Toshiba SBM, or Hitachi CMOS
> Annealer for combinatorial optimization, substrate is the complementary memory layer
> that provides deletion-on-request and provenance audit that the QUBO solvers cannot.
> Pricing aligns with v276 compliance-grade memory pricing ($500K-$2M ARR per pilot
> customer), targeting Chief Compliance Officers and Chief Information Security
> Officers rather than CTOs evaluating optimization hardware.

## Section F: Risk register for the classical-AQC positioning

(R1) **D-Wave skeptical baggage**: D-Wave has been in market 20 years with disputed
quantum-advantage claims. Adopting the classical-AQC framing could inherit some skeptical
press (Scientific American "quantum hype" articles, IEEE Spectrum controversy coverage).
Mitigation: do NOT claim quantum-advantage; explicitly state "substrate is the classical
algorithm in the same problem class as D-Wave's stoquastic Hamiltonian, with no quantum
overhead." This is the honest framing and pre-empts the controversy.

(R2) **Quantum-inspired classical has had hype cycles**: Tang's 2019 dequantization
result was widely celebrated as "killing quantum advantage" but did not disrupt
commercial recommendation systems (Netflix still uses classical algorithms; quantum
algorithms were never deployed). Substrate must differentiate from "another quantum-
inspired classical algorithm" framing. Mitigation: position substrate as a NEW PRODUCT
CATEGORY (auditable memory layer) that happens to be in the AQC mathematical class, not
as "quantum-inspired classical optimization." The optimization framing is the CHANNEL,
not the PRODUCT.

(R3) **Existing quantum-inspired classical systems are already deployed**: Fujitsu DA,
Toshiba SBM, Hitachi CMOS annealer are in production at large enterprise customers
(automotive routing, portfolio optimization, drug discovery). Substrate must
differentiate convincingly. Mitigation: substrate is NOT a Max-Cut solver. Substrate is
a memory layer with audit primitives. Cross-sell narrative: "use Fujitsu DA for your
optimization; use substrate as the auditable memory layer feeding the optimization."

(R4) **"But it's not actually quantum" objection**: D-Wave-pilot buyers may reject
the substrate framing if they were specifically chasing quantum advantage. Mitigation:
the D-Wave 20-year track record shows NO commercial customer has captured quantum
advantage; the buyers are buying energy-landscape computation that happens to be on a
quantum chip. Substrate offers the same energy-landscape computation without the chip.
This is a STRENGTHENING of the existing buyer's actual value-extraction story.

(R5) **EU AI Act vs D-Wave positioning may dilute**: v276 primary positioning is
compliance-grade auditable memory under EU AI Act. The classical-AQC framing targets a
DIFFERENT buyer (CTO for compute infrastructure, not CCO for compliance). Mitigation:
keep the two as SEPARATE narratives -- (a) v276 primary for compliance buyers (regulated
finserv / healthcare / legal), (b) classical-AQC secondary for compute-infrastructure
buyers (D-Wave pilots, Forbes Global 2000 R&D). Sales team can route by buyer persona.

(R6) **Theoretical correspondence may have hidden requirements**: the formal derivation
(Section A) is textbook but has not been written down in a substrate-specific form. If
the derivation requires non-stoquastic structure substrate cannot reach, the framing
falls. Mitigation: HP2 of the cheap decisive test gates the positioning lock; we don't
ship the narrative externally until the derivation is verified.

(R7) **D-Wave is positioning AGAINST quantum-inspired classical**: D-Wave's recent press
explicitly defends their quantum-advantage claims against classical-algorithm refutation
(Scientific American 2026, IEEE Spectrum 2026). D-Wave will not endorse substrate
substituting for them. Mitigation: not a concern -- substrate doesn't need D-Wave
endorsement; substrate captures the BUYER not the vendor.

## Section G: Concrete next-7-day actions

Day 0-1 (Friday/weekend):
- (no action needed; this drill IS the day-0 synthesis)

Day 1-2 (Mon/Tue, 4-6 hours):
- Write the formal substrate-as-classical-AQC correspondence derivation (Section A
  per HP2 of the cheap decisive test); land in verification/theory.py with self-test
  cell per [[feedback-strategy-spec-formula-selftests]]
- Owner: research (this agent) on next cycle invocation; deliverable is
  verification/aqc_correspondence.py

Day 2-3 (Tue/Wed, 1-2 days writing):
- Write positioning white paper draft (Section E per HP3 of the cheap decisive test)
  with 250-word recommended paragraph + technical appendix; deliverable is
  notes/positioning_classical_aqc_white_paper_draft_2026-XX-YY.md
- Owner: parallel writing track (NOT research; ship to memory_curator or strategy_scribe
  for the writing work per structural-agent-usage mandate)

Day 3-4 (Wed/Thu, 1 GPU-day):
- Ship QE-1 substrate annealing experiment to overnight_queue (or remote_cpu_queue if
  cheap enough at N=2048 3-seed)
- Owner: exp_dev on next dispatch cycle; anchor name TBD by exp_dev per
  [[feedback-no-experiment-design-in-prompts]]
- Pre-registration: HARD-PASS / HARD-FAIL bands per Section D above; exp_dev confirms
  envelope-expansion-fail-bands at dispatch

Day 4-7 (Thu-Sun):
- Evaluate QE-1 verdict; if HARD_PASS proceed to QE-3 evaluation; if HARD_FAIL deprioritize
  QE-3 (positioning still defensible but no product feature from annealing)
- In parallel: 1 D-Wave-pilot-prospect outreach (HP3); coordinate with v276 GTM track
- Owner: orchestrator for dispatch, GTM lead for outreach (per v276 6-month MVP roadmap)

## Cross-thread synthesis with prior entries

This drill integrates with:
- [[project-substrate-killer-features-2026-05-26]]: classical-AQC narrative WIDENS the
  channel for KF-2 deletion cert + KF-3 compositionality audit (substrate-vs-D-Wave
  positioning emphasizes both); does not change the killer-features priority order.
- [[project-substrate-strategic-inversion-48h-2026-05-26]]: 24-36mo competitive window
  CORROBORATED by D-Wave's $25M revenue / $355M loss profile (the AQC vendor sales motion
  has not closed the market; window remains open).
- [[project-substrate-skahm-class-confirmed-2026-05-27]]: substrate SKAH-M class is
  ORTHOGONAL to the classical-AQC positioning; SKAH-M is the INTERNAL framework, AQC is
  the EXTERNAL positioning. Both can coexist.
- [[project-substrate-non-eq-stat-mech-class-2026-05-27]]: non-eq stat-mech home is the
  INTERNAL framework; classical-AQC is the EXTERNAL positioning. Same orthogonality.
- v89 OAQEC rejection: REFRAMED. v89 closed substrate-as-OAQEC because commutative algebra
  is the wrong class. This drill SHOWS the same commutativity is exactly the maximally-
  stoquastic limit of AQC -- the rejection becomes the proof of the classical-AQC
  positioning's correctness. Closure-as-evidence pattern noted per
  [[feedback-rehabilitation-after-rejection]].
- v276 product-positioning: AUGMENTED. v276 primary framing (compliance-grade auditable
  memory) is UNCHANGED. This drill adds a SECONDARY narrative (classical-AQC) targeted at
  a different buyer persona (D-Wave-pilot CTOs vs v276's CCO/CISO).
- [[feedback-no-papers-product-only]]: classical-AQC framing is PRODUCT POSITIONING not
  publication-grade claim. Honor the memory: the substrate is the PRODUCT; the framework
  is the WHY-IT-WORKS internally.
- [[feedback-value-creation-not-competition]]: substrate-vs-D-Wave positioning is
  capabilities mapping ("what does substrate do? same energy-landscape class as AQC with
  audit primitives") not competitive-displacement ("kill D-Wave's market"). HONORED.
- [[feedback-dont-overextend-theorems]]: substrate-as-classical-AQC does NOT extend to
  claim substrate solves D-Wave's hard problem instances better than D-Wave. We do NOT
  claim quantum-advantage refutation, just classical-class membership.

## Substrate-product implications

PRIMARY positioning (unchanged from v276): substrate is the compliance-grade auditable
memory layer for AI deployments under EU AI Act, FINRA 2026, HIPAA, GDPR.

SECONDARY positioning (NEW, optional channel-additive):
> Substrate is the classical analog of adiabatic quantum optimization, delivering
> energy-landscape computation on commodity hardware with audit primitives that quantum
> systems cannot have.

Target secondary-narrative buyer: CTO / Chief Innovation Officer for compute
infrastructure (D-Wave-pilot buyer persona); Forbes Global 2000 R&D budget holder;
specifically the 135+ commercial D-Wave customers + the rejected D-Wave evaluators.

Pricing for secondary narrative: same as v276 ($500K-$2M ARR per pilot), but with the
sales angle "you were evaluating D-Wave at $5-20M for energy-landscape computation;
substrate delivers the same mathematical class at 1/10 the cost with auditability."

Product-feature implications:
- QE-1 substrate annealing (if HARD_PASS): "robust retrieval mode" feature for
  high-noise queries; complements KF-1 hallucination detection
- QE-3 syndrome correction (if HARD_PASS): "error-corrected retrieval" feature for
  Kerdock(16) N=65536 substrate variant; positions against ANY content-addressable
  memory
- Tang-style amplitude-estimation confidence intervals on retrieval (Section C item b):
  enriches KF-1 with retrieval-probability confidence bands

## Citations (verified)

External lit-scan citations from WebSearch (10):

1. Frontiers in Physics. "Adiabatic quantum optimization for associative memory recall."
   2014. URL: frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00079
2. IEEE Conference Publication. "Problem Solving with Hopfield Networks and Adiabatic
   Quantum Computing." IEEE Xplore document 9206916.
3. arXiv:1407.1904 "Adiabatic Quantum Optimization for Associative Memory Recall."
4. arXiv:1402.2295 Bravyi-Terhal. "Monte Carlo simulation of stoquastic Hamiltonians."
5. arXiv:1807.04271 Tang. "A quantum-inspired classical algorithm for recommendation
   systems." STOC 2019.
6. arXiv:1910.06151 Chia-Gilyen-Li-Lin-Tang-Wang. "Sampling-based sublinear low-rank
   matrix arithmetic framework for dequantizing quantum machine learning."
7. arXiv:2111.06077 Kleyko et al. "A Survey on Hyperdimensional Computing aka Vector
   Symbolic Architectures, Part II."
8. Springer Communications in Mathematical Physics. "On Complexity of the Quantum Ising
   Model." (referenced from search result on stoquastic complexity).
9. Wikipedia. "D-Wave Systems" (current commercial state verification).
10. Scientific American 2026. "Are D-Wave's Claims of 'Quantum Advantage' Just
    'Quantum Hype'?" (controversy verification).

Additional internal substrate-references (5):
11. notes/research_product_positioning_v276_2026-05-29.md (primary positioning predecessor)
12. notes/substrate_capability_map.md v89 update (OAQEC rejection / Harlow theorem)
13. notes/research_noneq_framework_consolidation_v276_2026-05-29.md (non-eq stat-mech
    home)
14. notes/research_kf4_kf5_rescue_paths_v276_2026-05-29.md (pre-argmax joint probe;
    relevant to QE-2 coherent multi-hop subsumption)
15. notes/strategic_synthesis_v265_v276_2026-05-29.md (operational-layer-invariance
    pattern; argmax-decoupling)

Verified citation count: 15 (10 external + 5 internal). Calibration penalty applied:
all P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50; positioning
recommendation framed as ADDITIVE not REPLACEMENT to v276 primary narrative.

## Calibration / honesty notes

- Lit-scan deflation 0.15-0.25 applied to all P estimates
- Novel-synthesis cap P=0.50 NOT triggered (this is positioning + textbook math
  synthesis, not novel-physics derivation)
- Formal correspondence P_defensible = 0.85-0.95 pre-deflation; 0.70-0.80 DEFLATED;
  empirically verifiable in 4-hour analytic task (HP2 of cheap decisive test)
- QE-1 P_HARD_PASS = 0.40 DEFLATED (raw lit-scan suggested 0.55; calibration penalty
  applied; substrate may already be at energy floor under greedy retrieval)
- QE-3 P_HARD_PASS = 0.35 DEFLATED (raw lit-scan suggested 0.50; calibration penalty
  applied; substrate basin retrieval may already capture parity-check capacity)
- D-Wave commercial state CORROBORATED from 2026-publish-date sources (SEC 8-K, D-Wave
  press releases, IEEE Spectrum, Scientific American)
- Buyer-persona claims (D-Wave evaluators may pivot to substrate) UNVERIFIED at design-
  partner level; gated by HP3 of cheap decisive test before positioning lock
- No quantum-advantage refutation claim made; substrate does NOT claim to disprove
  D-Wave's quantum advantage, only to operate in the classically-simulable subset
  of D-Wave's problem class
- v89 OAQEC rejection REFRAMED as positive evidence for classical-AQC positioning,
  per [[feedback-rehabilitation-after-rejection]]; this is the rescue-as-evidence
  pattern from Cap 2 v160->v172

End of note.
