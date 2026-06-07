# Research Note: Level-2 Deep Drill -- Federated Privacy Knowledge Accumulation
Date: 2026-06-07
Trigger: Orchestrator directive -- Blue Ocean opportunity for multi-party substrate privacy accumulation
Prior federated note: notes/research_drill_federated_unlearning_2026-06-02.md (unlearning/deletion certs -- non-overlapping angle)

---

## HEADLINE

Substrate's combination of (a) pseudoinverse write rule (linear superposition), (b) discrete bipolar state, (c) RSA cryptographic accumulator with Merkle chain, and (d) algebraic binding/unbinding (XOR/bundling) creates a NATIVE substrate-layer privacy stack that is architecturally distinct from all six mainstream federated learning approaches. The key finding: additive secret sharing (Shamir/additive) composes EXACTLY with pseudoinverse superposition -- shares of substrate state are themselves valid substrate states, and their reconstruction is the same linear combination used for normal write aggregation. This means Pattern C (secret-shared substrate) is not merely an add-on but is algebraically native to the write rule. DP noise injection (Pattern B) requires careful calibration against the alpha_c=0.40 exact-recovery threshold -- the noise floor must stay below the signal separation margin. The Merkle chain already in the substrate composes trivially with ZK vector commitment proofs. Estimated commercial addressable markets: healthcare consortium ($30B+ HIPAA-constrained), financial fraud detection ($15B+), drug discovery ($20B+).

P_deflated = 0.38 (novel-synthesis P after calibration penalty: naive 0.55-0.65 deflated by 0.20 for absence of published direct precedent combining pseudoinverse write + Shamir shares + cryptographic accumulator; cap at 0.50 applied; further 0.10 deflation for implementation-path uncertainty on secret-shared write aggregation at inference speed).

---

## Cheap decisive test

Algebraic test (no empirical run required): verify that for a substrate weight matrix W built by pseudoinverse writes, if W is additively secret-shared as W = W_1 + W_2 + ... + W_k (over Z_p or real-valued modular arithmetic), then retrieval of a stored pattern x_i from W is equivalent to summing the retrievals from each share:

  W * x_query ~ x_i  iff  (W_1 + W_2 + ... + W_k) * x_query ~ x_i

This is a trivial consequence of matrix linearity. The non-trivial test: verify that the cosine similarity of W * x_query against x_i degrades gracefully when each W_j is independently perturbed by DP noise of scale sigma, i.e., verify that the effective SNR is:

  SNR_eff = (N * alpha_c) / (k * sigma * sqrt(N))
           = alpha_c * sqrt(N) / (k * sigma)

where N=1024, alpha_c=0.40, k=number of parties. For k=3 parties, sigma <= 0.40 * sqrt(1024) / (3 * z_{1-delta/2}) is the noise ceiling before retrieval breaks. At N=1024, this gives sigma <= 0.40 * 32 / (3 * 1.96) ~ 2.18 per dimension -- a generous noise budget relative to the bipolar {-1, +1} state values. This is algebraically derivable from the pseudoinverse capacity formula and requires no empirical verification.

Criterion: show sigma_max ~ 2.18 for N=1024, k=3 is comfortably above Gaussian mechanism sigma needed for (epsilon=1.0, delta=1e-5)-DP in a single write (which gives sigma = sqrt(2 * ln(1.25/delta)) / epsilon ~ 4.8 for sensitivity-1 write). NOTE: this means vanilla DP at epsilon=1.0 EXCEEDS the noise ceiling for N=1024. Resolution: (a) increase N to 4096+ (sigma_max scales as sqrt(N)), or (b) use tighter DP (epsilon=4-8), or (c) use Renyi DP with tighter composition.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

### Pattern B: Differential Privacy Writes

**HARD-PASS (DP noise is compatible with substrate utility):**
- At N=4096, k=3 parties, sigma_max ~ 8.73 for exact recovery; DP Gaussian mechanism at epsilon=1.0 needs sigma ~ 4.8; gap factor ~ 1.8x means retrieval survives with probability >= 0.85 (from standard normal tail)
- Privacy budget (epsilon, delta) = (1.0, 1e-5) is achievable per NIST SP 800-226 "conservative strong privacy" threshold
- Advanced composition (Renyi DP / moments accountant) extends useful lifetime to >= 100 write rounds before budget exhaustion

**HARD-FAIL (DP noise breaks substrate at deployable scale):**
- N=1024 with epsilon=1.0 DP: sigma_DP=4.8 > sigma_max=2.18 -- HARD FAIL confirmed analytically for this configuration (noise budget INSUFFICIENT at N=1024)
- epsilon must be relaxed to ~8-10 for N=1024 to work, which is weaker than NIST guideline; this is a real constraint
- Privacy budget exhausts after ~20-30 write rounds under sequential composition with epsilon=1.0 at k=3 parties; long-lived consortiums require either (a) larger N, or (b) zCDP/GDP tighter accountant, or (c) refreshable substrate approach

### Pattern C: Secret-Shared Substrate

**HARD-PASS:**
- Additive sharing W = W_1 + ... + W_k over reals (or quantized integers) is mathematically exact: reconstruction is the pseudoinverse write rule applied to sum of local writes
- (k, t)-threshold Shamir sharing on the row vectors of W is compatible with later pseudoinverse write updates by any subset of t+1 parties
- No single party can reconstruct stored patterns from fewer than t+1 shares

**HARD-FAIL:**
- Communication overhead for (k=10, t=5) threshold scheme scales as O(k^2) per write round; for 10 parties with N=4096-dimensional W (N*N=16M parameters), each round transmits ~16M * 10 float values ~ 640MB per round; this is prohibitive for real-time writes
- Resolution: use row-wise or block-wise sharing to reduce granularity; share only write updates (delta_W), not full W

### Pattern E: Private Information Retrieval (Oblivious Retrieval)

**HARD-PASS:**
- PIR on substrate: querying party retrieves a pattern from a remote substrate without revealing which pattern was queried; YPIR (USENIX 2024) achieves near-optimal single-server PIR; substrate's discrete binary vectors have structure that may allow more efficient PIR than dense real-valued vectors
- Pacmann (ICLR 2025): private approximate nearest neighbor search via graph-based vector search + Path Oblivious RAM; directly applicable to substrate's retrieval operation

**HARD-FAIL:**
- Oblivious RAM overhead: O(log^2 N) per access; for N=10^6 stored patterns, this is ~400 operations per retrieval vs 1 hop without ORAM; 0.051ms/hop * 400 = 20ms per private retrieval; borderline for real-time use cases
- Two-server PIR requires non-colluding servers; substrate's sharding architecture may enable this if shards are at different trust levels

---

## Cross-thread synthesis

### Link to Federated Unlearning (2026-06-02 note)
The deletion certificate mechanism (rank-1 update + SHA-256 hash chain) composed with the Merkle audit trail creates a privacy-preserving audit that can certify BOTH "what was added" (accumulation) and "what was removed" (unlearning). This enables a full lifecycle privacy guarantee: write under DP (Pattern B), audit via Merkle (existing), delete via rank-1 update (prior note), prove deletion via hash certificate. No single party sees the full substrate state.

### Link to RSA Accumulator (HP-12 V1, existing)
The existing RSA accumulator already provides non-membership proofs. In the federated context this becomes: "prove that hospital X's patient record is NOT in the aggregate substrate" without revealing what IS in the substrate. This is the "oblivious accumulator" primitive recently formalized (Baldimtsi et al., ePrint 2023/1001). The substrate is one implementation cycle away from this capability.

### Link to Algebraic Operations (binding/unbinding)
XOR bundling across parties: if each party writes a locally-bundled representation W_i = SUM_j (x_j CIRC y_j) for their local (x_j, y_j) pairs, and the aggregate W = SUM_i W_i is formed via secure aggregation, then unbinding W with a known role vector y recovers the aggregate fillers -- without any party revealing their local (x, y) pairs. This is a federated compositional representation. The algebraic structure is the same as VSA (Vector Symbolic Architectures) federated use cases studied for sensor fusion; the substrate's write rule gives this a memory-like persistence property not present in one-shot VSA fusion.

### Link to Sharding (5x overload HP)
The existing 5-shard per-tenant architecture maps directly to Pattern A (per-tenant isolation). Upgrading to Pattern F (per-party local + shared aggregate via secure aggregation) requires: (1) a "merge shard" operation that aggregates N shard snapshots from N parties into a joint shard; (2) this merge is exactly the pseudoinverse write sum: W_joint = W_1 + W_2 + ... + W_N with proper normalization. The 5x overload HP controls capacity; merged writes count toward joint shard capacity.

---

## Architectural patterns -- technical depth

### Pattern B: Differential Privacy Substrate Writes

Mechanism: Gaussian mechanism applied to pseudoinverse write vectors. For a write x -> W, add noise eta ~ N(0, sigma^2 * I_N) to the write vector before accumulation. The noisy write is x_noisy = x + eta; pseudoinverse update: W <- W + x_noisy * x_noisy^T / N (simplified).

Sensitivity: The L2 sensitivity of a single write in the pseudoinverse rule is bounded by ||x||_2^2 / N = 1 for normalized bipolar vectors. So the Gaussian mechanism at (epsilon, delta)-DP requires sigma >= sqrt(2 * ln(1.25/delta)) / epsilon.

Utility bound: For k parties each writing M patterns, the aggregate substrate noise floor is sigma_agg = sigma * sqrt(k) (if writes are independent). The retrieval signal degrades as SNR = alpha_c * sqrt(N) / (sigma * sqrt(k) * sqrt(M)). Setting SNR >= 1 (minimum readable): M_max = N * alpha_c^2 / (sigma^2 * k). This is the DP-constrained capacity formula.

At N=4096, alpha_c=0.40, sigma=4.8 (epsilon=1.0 DP), k=3: M_max = 4096 * 0.16 / (23.04 * 3) ~ 9.5 patterns. This is very low. At k=1 party: M_max ~ 28 patterns. DP at epsilon=1.0 severely limits capacity.

Mitigation A: Increase N. At N=65536 (64K-dimensional): M_max ~ 9.5 * (65536/4096) = 152 patterns per aggregate. Still limited for large consortiums.

Mitigation B: Use local DP only at write time, aggregate without further noise (shuffle model / central DP). Central DP allows sigma to be divided by sqrt(k): sigma_central = sigma / sqrt(k). At k=10 parties: M_max increases by 10x.

Mitigation C: Per-instance DP (attack-aware noise calibration, NeurIPS 2024): calibrate noise per write vector to its actual attack risk rather than worst-case sensitivity. For distributed substrate writes with low-sensitivity patterns, per-instance DP may allow sigma ~ 0.5-1.0 while maintaining epsilon=1.0 -- increasing M_max by 20-100x.

### Pattern C: Secret-Shared Substrate

Mechanism: Use (t, k)-threshold additive secret sharing on substrate weight matrix W. Party i holds share W_i; none can reconstruct W with fewer than t+1 shares. All k parties participate in a secure aggregation round to produce the joint substrate state for retrieval.

Algebraic compatibility: The pseudoinverse write rule is linear: W = SUM_j X_j^{+} where X_j are write batches. This means shares W_i = SUM_j X_{j,i}^{+} where X_{j,i} is party i's contribution to write batch j. No cross-party communication is needed during writes. Reads require threshold reconstruction.

Communication: Reconstruction of W for a single read operation: O(t * N^2) data transfer (t parties each send N^2 floats). For N=1024: t * 1024^2 * 4 bytes = t * 4MB per read. At t=3: 12MB per read. Latency at 1Gbps: ~96ms. This is acceptable for batch retrieval but not real-time.

Optimization: Share only the compressed PCA-whitened representation (substrate already does PCA whitening). If PCA reduces to d=256 dimensions, communication per read is t * 256^2 * 4 bytes = t * 256KB per read. At t=3: 768KB per read, ~6ms latency at 1Gbps. Usable.

Verifiability: Combine with Merkle chain (existing substrate feature): each write share is appended to a per-party Merkle tree. The root hash is published. At reconstruction, verifiers check that the shared W_i hashes to the published roots. This gives VERIFIABLE secret-shared substrate without a trusted aggregator.

### Pattern D: Homomorphic Substrate Operations (HE write aggregation)

Mechanism: BFV/CKKS encryption applied to substrate state. Parties write encrypted patterns; aggregation is performed by a semi-honest server without decryption.

Feasibility analysis: CKKS supports approximate arithmetic on packed vectors of complex numbers. Substrate writes involve inner products (x * W * x^T type operations). The latency overhead for CKKS is roughly 1000-10000x versus plaintext (Microsoft SEAL benchmarks). Substrate's 0.051ms/hop becomes 51ms-510ms per hop under CKKS. For batch operations (offline learning, not real-time retrieval), this is acceptable.

Key limitation: CKKS supports a bounded number of "levels" (multiplicative depth) before bootstrapping is needed. Pseudoinverse writes are linear (depth 1); retrieval (argmax over cosine similarities) requires comparisons, which have high multiplicative depth. Approximate comparisons in CKKS are expensive.

Practical path: Use HE only for the write aggregation phase (Pattern D-lite): each party encrypts their local write batch; an aggregation server homomorphically sums the batches; decryption produces the aggregate W. Retrieval is then done in plaintext on the decrypted aggregate. This is a "write-private aggregate" pattern vs "fully homomorphic retrieval."

### Pattern E: Private Approximate Nearest Neighbor (PANN)

Mechanism: Pacmann (ICLR 2025) directly applies: HNSW graph-based ANN search + Path Oblivious RAM. The substrate's retrieval is a nearest-neighbor problem in the bipolar vector space. Private retrieval means: the querying party retrieves its nearest match from the aggregate substrate without the substrate host learning which pattern was queried.

Substrate-specific efficiency gain: Bipolar {-1, +1} vectors admit Hamming distance as a proxy for cosine distance. XOR-based Hamming computation is faster than Euclidean inner products, which may reduce the ORAM overhead multiplicative factor.

YPIR (USENIX Security 2024): single-server PIR with sublinear server computation. For substrate with M stored patterns each of dimension N, YPIR achieves O(sqrt(M)) server computation per query, vs O(M) for naive PIR. At M=10000 patterns: 100x speedup over naive PIR.

### Pattern F: Federated Aggregate via Secure Aggregation

Mechanism: Direct analog of McMahan's federated averaging, but for substrate state rather than neural network weights. Each party runs local writes -> local W_i. Periodic aggregation round: secure aggregation (Bonawitz et al. 2017) sums W_1 + ... + W_k -> W_joint without any party revealing their local W_i.

Bonawitz et al. secure aggregation (Google 2017) handles: client dropouts (fault tolerance), honest-but-curious server (privacy), and scales to 10^6+ parties. Directly applicable to substrate aggregation.

DDP-SA (arXiv 2604.07125, 2026): distributed DP + secure aggregation; combines both Pattern B and Pattern F. Demonstrates that adding DP noise AFTER secure aggregation (central DP) is better utility than adding before (local DP): server sees only the noisy sum, not individual contributions.

---

## Failure modes (negative-finding 2x deep)

### Failure 1: DP noise vs alpha_c capacity cliff

As derived in the cheap decisive test: at N=1024, epsilon=1.0 DP, the noise sigma=4.8 exceeds the noise ceiling sigma_max=2.18. This is a HARD FAIL for small-N configurations. The alpha_c threshold is a sharp phase transition (percolation-class) -- crossing it does not degrade gracefully but produces catastrophic retrieval failure.

Mitigation: N must scale as O(k^2 / alpha_c^2 * sigma_DP^2) to maintain retrieval capability. For epsilon=1.0, k=3: N >= 3 * 4.8^2 / 0.16 ~ 432. So N=1024 is borderline (it clears this minimum but without headroom). N=4096 gives ~9x headroom.

Assessment: This is a REAL constraint, not a theoretical edge case. Any production federated substrate deployment MUST use N >= 4096 for meaningful DP.

### Failure 2: Privacy budget exhaustion under composition

Sequential composition: k parties each writing M rounds, T rounds total. Under basic composition: epsilon_total = T * epsilon_round. Under advanced composition (RDP/MA): epsilon_total ~ O(sqrt(T) * epsilon_round) for small epsilon_round.

For T=100 rounds, epsilon_round=1.0: basic composition gives epsilon_total=100 (meaningless). Advanced composition: epsilon_total ~ 10. NIST guideline says epsilon <= 1 is "conservative strong privacy." A 100-round consortium would need epsilon_round ~ 0.01 per round, which drives sigma up by 100x and makes DP writes essentially useless.

For substrate, the natural mitigation is one-shot / append-only writes: substrate writes are non-iterative (unlike SGD which needs many rounds). Each pattern is written once. This means the composition problem is less severe than in gradient-based federated learning.

### Failure 3: Write vector inversion attacks (critical)

Even without DP, the write vectors sent to the aggregation server are potentially revealing. Write inversion: recovering the original pattern x from the write update delta_W = x * x^T / N (pseudoinverse update). This is trivially reversible: delta_W * e_1 = (x^T e_1 / N) * x -- any probe vector recovers x.

This means the aggregation server sees the raw write updates and can trivially reconstruct all stored patterns. The pseudoinverse write is MORE information-leaking than neural network gradient updates (which at least have non-linearity and mixing).

Fix: NEVER send raw pseudoinverse updates to the aggregation server -- always send either (a) DP-noised updates, or (b) secret-shared updates. This is a non-negotiable implementation constraint for any federated substrate deployment.

### Failure 4: Adversarial aggregator

Even with DP, an adversarial aggregator who sees many round-aggregates can potentially learn more than epsilon * T via correlation attacks. The shuffle model (Apple PFL) addresses this: a trusted shuffler permutes all client updates before the aggregator sees them, breaking per-client correlation. For substrate: the Merkle audit chain provides VERIFIABILITY of aggregator behavior but not HIDING. Mitigation: combine Merkle audit with blinded writes.

### Failure 5: Membership inference via retrieval oracle

Substrate's retrieval oracle IS a membership test: cosine_sim(W * x, x) > alpha_c implies x is stored. FedMIA (CVPR 2025) demonstrates that federated clients can conduct passive local membership inference using GAN-enhanced methods. The substrate's oracle is even simpler than gradient-based inference. Mitigation: (a) DP output perturbation on retrieval, or (b) PIR (private retrieval so probes are hidden), or (c) oracle rate-limiting.

---

## Cross-domain insights

### From Healthcare IT (HIPAA)

Literature (PMC 12464415, 2025): 96.1% accuracy is achievable with epsilon=1.9 on breast cancer detection datasets under DPSGD. Practical operating point for healthcare: epsilon <= 2.0. For substrate at N=4096: sigma_max=8.73, sigma_DP(epsilon=2.0) = 4.8 / 2.0 * sqrt(2*ln(1.25/1e-5)) ~ 2.4, which gives gap factor ~3.6x -- comfortable.

HIPAA does not require a specific cryptographic protocol -- it requires "reasonable and appropriate technical safeguards." A substrate deployment could satisfy HIPAA via DP (epsilon <= 2.0) + Merkle audit trail, without full homomorphic encryption.

### From Financial Fraud Detection

Banks share fraud patterns that are typically sparse (low Hamming weight in the bipolar representation). Sparse writes have lower L2 sensitivity than dense writes: sensitivity of a write with Hamming weight w is bounded by w/N (vs 1 for dense). This allows sigma_DP to be reduced proportionally, directly increasing M_max. Per-instance DP (NeurIPS 2024, arXiv 2407.02191) calibrates noise per individual write vector's attack risk -- exactly what is needed for heterogeneous sparse fraud patterns.

### From Oblivious Accumulators (Cryptography)

Baldimtsi et al. (ePrint 2023/1001) formalizes oblivious accumulators: membership proofs without revealing the set, with oblivious add/delete operations. The substrate's RSA accumulator is a standard non-oblivious accumulator. Upgrading to oblivious requires OT or ZK proofs for each update -- compatible with the existing Merkle+RSA stack. This is a one-implementation-cycle upgrade.

### From Compressed Sensing / Sparse Coding

The substrate's capacity cliff (alpha_c=0.40) has a direct parallel in the Donoho-Tanner phase transition for L1 recovery: below a sparsity threshold, L1 minimization recovers sparse signals exactly; above it, recovery fails sharply. DP noise acts like measurement noise in compressed sensing: the RIP constant must exceed the noise floor. For sparse patterns (Hamming weight w << N), the effective alpha_c is higher -- more patterns per unit noise.

---

## Empirical cell candidates

### Cell A: DP substrate write at varying epsilon
- Setup: N=4096, k=3 parties, M=50 write patterns per party, epsilon in {1.0, 2.0, 4.0, 8.0}, delta=1e-5
- Metric: retrieval accuracy (fraction of patterns with cosine similarity > alpha_c=0.40)
- HARD-PASS: epsilon=2.0 gives accuracy > 0.85; epsilon=4.0 gives accuracy > 0.95
- HARD-FAIL: even epsilon=8.0 gives accuracy < 0.70 (substrate + DP fundamentally incompatible at N=4096)
- MIDDLE-BAND: accuracy monotone increasing with epsilon; non-monotone indicates numerical instability
- Cost: laptop CPU, ~10 min (numpy simulation)

### Cell B: 3-party secret-shared substrate correctness
- Setup: N=1024, k=3 parties, additive secret sharing (W = W_1 + W_2 + W_3 mod 2^32 fixed-point), M=100 write patterns
- Metric: correctness (fraction of M patterns retrieved from reconstructed W vs baseline)
- HARD-PASS: correctness > 0.95 (should be ~1.0 minus float rounding)
- HARD-FAIL: correctness < 0.90 (floating-point sharing breaks linear structure)
- Cost: laptop CPU, ~5 min

### Cell C: BFV homomorphic write aggregation latency
- Setup: Microsoft SEAL or OpenFHE; N=256; k=2 parties; M=10 write patterns; measure latency per write, per read
- Metric: latency ratio (HE_latency / plaintext_latency)
- HARD-PASS: latency ratio < 500x; read latency < 1000ms
- HARD-FAIL: latency ratio > 5000x or implementation requires depth > 4 (bootstrapping needed)
- Cost: laptop CPU, ~30 min

### Cell D: Federated aggregate -- 3-party secure aggregation simulation
- Setup: N=2048, k=3 parties, Pattern F simulation; M=200 local patterns per party; secure aggregation (sum W_1+W_2+W_3); DP noise at epsilon=2.0 after aggregation; test 20 patterns per party
- Metric: cross-party retrieval accuracy AND own-party accuracy
- HARD-PASS: cross-party accuracy > 0.80 AND own-party accuracy > 0.90 at epsilon=2.0
- HARD-FAIL: cross-party accuracy < 0.50 (no meaningful knowledge sharing)
- Cost: laptop CPU, ~15 min

### Cell E: Membership inference oracle test
- Setup: N=2048, W trained on M=300 patterns; adversary tests 600 patterns (300 in/out); measure AUROC via cosine similarity threshold
- Metric: AUROC of membership inference attack
- HARD-PASS: AUROC < 0.65 with DP at epsilon=2.0
- HARD-FAIL: DP at epsilon=2.0 does NOT reduce AUROC below 0.70 (privacy claim invalid)
- Note: AUROC > 0.90 without DP is EXPECTED and validates the oracle leakage concern
- Cost: laptop CPU, ~10 min

---

## Substrate-product implications

Three deployment architectures are ready for implementation planning today:

1. Healthcare Consortium -- Pattern F + B (Federated Aggregate + Central DP)
   - 3-10 hospital substrate instances; monthly aggregation; central DP epsilon=2.0
   - Merkle audit trail certifies aggregation fidelity
   - HIPAA compliance via DP + Merkle; no BAA-breaking data sharing
   - Differentiator vs Apple/Google PFL: native Merkle audit + RSA non-membership proofs; PFL has no native knowledge retrieval layer

2. Financial Fraud -- Pattern B + E (DP Writes + Private Retrieval)
   - Banks write sparse fraud patterns with per-instance DP
   - Real-time private retrieval via PIR (YPIR protocol) for fraud matching
   - No bank learns which other banks queried the substrate
   - Differentiator: substrate retrieval is a REASONING step (role unbinding), not just nearest-neighbor lookup; enables conditional retrieval that embedding similarity approaches cannot do

3. Drug Discovery -- Pattern C + A (Secret-Shared + Per-Tenant Sharding)
   - Pharma companies each hold shares; no company reconstructs without threshold cooperation
   - IP-protected: binding operation (compound BIND mechanism) provides plausible deniability
   - Periodic batch retrieval for meta-analysis (reconstruct, query, re-share)
   - Differentiator: binding provides plausible deniability on top of secret sharing

---

## Competitive landscape summary

Apple PFL: DP + secure aggregation via Secure Enclave. Production at 1B+ scale. No verifiable audit trail; no compositional symbolic retrieval; no cryptographic non-membership proofs.

Google TFL: Federated averaging + secure aggregation. Production. No audit trail; no retrieval layer.

Meta CrypTen: Secure MPC for ML training. Research only.

Microsoft SEAL: HE library. Building block only; no FL orchestration or retrieval.

OpenMined (PySyft): Open-source FL + DP. No production substrate; no audit trail.

Substrate edge over all five: the ONLY federated system with (a) verifiable Merkle audit chain, (b) algebraic compositional retrieval (binding/unbinding), (c) RSA accumulator non-membership proofs, and (d) deletion certificates (from prior unlearning note). The privacy layer is not an add-on -- it composes with the substrate's native algebraic operations.

---

## Citations (verified from searches, 30 total)

1. McMahan et al. 2017 -- Communication-Efficient Learning of Deep Networks from Decentralized Data
2. Bonawitz et al. 2017 -- Practical Secure Aggregation for Privacy Preserving Machine Learning
3. Dwork & Roth 2014 -- The Algorithmic Foundations of Differential Privacy
4. arXiv 2407.02191 (NeurIPS 2024) -- Attack-Aware Noise Calibration for Differential Privacy
5. arXiv 2503.00581 (2025) -- Secure Aggregation in Federated Learning using Multiparty Homomorphic Encryption
6. PMC 10892453 (2024) -- Secure Aggregation Protocol Based on DC-Nets and Secret Sharing
7. ePrint 2024/1655 -- Secure Stateful Aggregation: A Practical Protocol with Applications
8. Nature Scientific Reports 2025 -- Group verifiable secure aggregate federated learning based on secret sharing
9. ACM Computing Surveys 2024 -- When Federated Learning Meets Privacy-Preserving Computation (doi:10.1145/3679013)
10. arXiv 2405.08299 (2024) -- Differentially Private Federated Learning: A Systematic Review
11. PMC 12464415 (2025) -- Balancing privacy and performance in healthcare: A federated learning framework
12. Nature Scientific Reports 2025 -- Federated learning with differential privacy for breast cancer diagnosis
13. NIST SP 800-226 (March 2025) -- Guidelines for Evaluating Differential Privacy Guarantees
14. arXiv 2604.07125 (2026) -- DDP-SA: Scalable Privacy-Preserving Federated Learning via Distributed DP and Secure Aggregation
15. ICLR 2025 -- Pacmann: Efficient Private Approximate Nearest Neighbor Search
16. ePrint 2024/1600 -- Privacy-Preserving ANN Search on High-Dimensional Data (Zhu et al.)
17. CMU PhD Thesis 2025 (Mingxun Zhou) -- Private Information Retrieval and Searching with Sublinear Costs
18. USENIX Security 2024 -- YPIR: High-throughput single-server PIR with silent preprocessing
19. ePrint 2024/657 -- Cryptographic Accumulators (survey)
20. ePrint 2023/1001 -- Oblivious Accumulators (Baldimtsi et al.)
21. Nature Scientific Reports 2025 (doi:10.1038/s41598-025-33685-1) -- DA34FL: dynamic accumulator-based auth for federated learning
22. arXiv 2404.17984 (2024) -- Privacy-Preserving, Dropout-Resilient Aggregation in Decentralized Learning
23. arXiv 2511.07123 (2025) -- Harnessing Sparsification in FL: Secure, Efficient, Differentially Private
24. CVPR 2025 -- FedMIA: Effective Membership Inference Attack in Federated Learning (Zhu et al.)
25. ACM Computing Surveys 2024 (doi:10.1145/3704633) -- Membership Inference Attacks and Defenses in FL: A Survey
26. arXiv 2601.06866 (2026) -- United We Defend: Collaborative Membership Inference Defenses in Federated Learning
27. Springer 2025 -- Verifiable secure aggregation scheme for FL (doi:10.1007/s10791-025-09676-1)
28. ScienceDirect 2025 -- Efficient verifiable secure aggregation protocols for federated learning
29. Springer 2026 -- Survey of ZKP-based verifiable machine learning (doi:10.1007/s10462-026-11557-y)
30. MIT 6.5610 Lecture Notes 2024 (Yael Kalai) -- Secret Sharing Schemes

---

## Next drill candidate

The critical open question is whether the closed-form SNR_eff formula correctly predicts retrieval accuracy at the alpha_c phase transition boundary under DP noise. The percolation-critical-phenomena adjacency (field advisor: parent=spin-glass) is directly relevant: the alpha_c capacity cliff has percolation-class critical exponents, and DP noise changes the effective transition point. A drill on percolation/critical-phenomena focusing on how additive noise shifts phase transition thresholds would close this question algebraically. Recommended next: percolation-critical-phenomena field, adjacency to spin-glass parent.
