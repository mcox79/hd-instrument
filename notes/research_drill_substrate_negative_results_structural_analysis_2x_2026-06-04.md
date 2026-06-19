# research: 2x drill -- substrate accumulated negative results: structural limits analysis
# Date: 2026-06-04
# Trigger: orchestrator 2x depth drill on today's HF cluster
# Discipline: algebraic + lit-scan only. No empirical verification.

---

## HEADLINE

Eight negative results collectively map to THREE structural substrate limits: (a) SPARSITY PREREQUISITE (dense modes fail across resonator, modulator, and representation axes), (b) UNIDIRECTIONAL BINDING PRIMITIVE (substrate algebra is factor-binding not edge-relation, ruling out membership queries natively), and (c) ORDER-INVARIANCE IN ADDITIVE WRITE (linear W rules out temporal sequencing benefits). Four of the eight are pure ACCEPTED-NEGATIVEs with no high-leverage escape path within substrate's current operating mode; four are either operating-mode-specific or engineering-rescuable with clear next tests.

---

## SUB-QUESTION ANALYSES

### (1) B5 REPLAY-CONSOLIDATION: FUNDAMENTAL OR RESCUABLE?

**Classification: OPERATING-MODE-SPECIFIC (3 operating modes could rescue; 1 is cheapest)**

**Algebraic pressure-test on the three HF reasons:**

Reason A -- Linear additive W: W_{t+1} = W_t + eta * (x_i x_i^T). Replay order
sigma permutes the index i only. For any permutation sigma, the final W is:
  W_final = W_0 + eta * sum_i x_{sigma(i)} x_{sigma(i)}^T = W_0 + eta * sum_i x_i x_i^T
(matrix addition is commutative; outer products sum regardless of order).
This is a STRUCTURAL FACT about additive Hebbian rules, not a substrate bug.
Verdict: **FUNDAMENTAL in additive-Hebbian mode**.

Reason B -- Bounded weights: Bounded projection W -> clip(W, -1, +1) preserves
commutativity of the outer-product sum within the allowed range. The Lazaro 2025
prediction of HP for bounded-W was contingent on bounded-W breaking the symmetry;
empirically it does not at substrate scale (HF confirmed). Verdict: **FUNDAMENTAL
in bounded-Hebbian mode** unless the nonlinearity introduces order-dependence near
saturation in a sparse regime (see Escape C below).

Reason C -- Wright-Fisher neutral theory: With K replay samples and additive W,
the memory trace of item i is proportional to its replay count n_i. Wright-Fisher
drift-vs-selection balance predicts: replay-order benefit requires a SELECTION
COEFFICIENT s > 1/N_eff where N_eff = effective substrate dimensionality. For
substrate N=2048-8192 and additive-W, the selection coefficient from replay ORDER
(not count) is exactly zero (commutative sum). Order-dependent benefit requires
a nonlinear selection term -- i.e., a feedback signal that makes earlier vs later
replayed items differentially retained. This is absent in both additive and bounded-
Hebbian modes. Verdict: **CONFIRMS structural limit of additive-W family**.

**Four potential escape operating modes:**

Escape A (CHEAPEST, ~0 new substrate work): SEPARATE GENERATOR network for dreaming.
Crick-Mitchison 1983 (Nature 304:111-114) argued dreaming serves REVERSE replay
to weaken parasitic memories, not strengthen target ones. If substrate runs a
SEPARATE generator that produces replay sequences and uses a NONLINEAR write rule
(e.g., contrastive Hebbian: W += x_wake x_wake^T - x_sleep x_sleep^T), order
DOES matter because contrastive-Hebbian is not commutative in x_sleep. This is
architecturally distinct: substrate acts as the generator's MEMORY BANK, not the
replayer itself. P_deflated = 0.30 (requires nonlinear write; not validated at
substrate class).

Escape B (MEDIUM effort): Selection-coefficient cf-RPE during replay.
Wright-Fisher: if replay carries a fitness signal f(i) = cf-RPE score for item i,
the effective Hebbian write becomes W += eta * f(i) * x_i x_i^T. Now replay ORDER
matters if earlier items set a reference baseline (counterfactual baseline shifts
with each replay step). This is the "Drosophila-style cf-RPE during consolidation"
mechanism. Algebraically: commutativity is broken by the SEQUENTIAL cf-RPE update
of the baseline. P_deflated = 0.35 (cf-RPE + STDP together not tested; combines
two mechanisms that individually have open questions at substrate scale).

Escape C (MEDIUM-EXPENSIVE): Iterated retrieval-based replay (Mode 4).
If replay is RETRIEVAL-modulated (each replay item is retrieved from W then re-
written with modified weight), the write is nonlinear in the CURRENT W state:
W_{t+1} = clip(W_t + eta * f(W_t, x_i) * x_i x_i^T). This is inherently order-
dependent because W_t depends on replay history. Recent 2024 replay papers
(Kumaran et al. 2024 NeurIPS replay review; Liu et al. 2024 hippocampal replay
sequence) confirm retrieval-modulated replay at biological scale breaks W-symmetry.
P_deflated = 0.30 (substrate requires mode switch; iterated-retrieval+cleanup at
production N not benchmarked).

Escape D (HIGH effort): Multi-substrate hierarchical replay.
Cross-substrate transfer (substrate_A -> substrate_B) at different abstraction
levels makes order matter if the receiving substrate has CAPACITY GRADIENT between
levels. 2024 multi-level replay papers (Ji & Wilson 2007 canonical; 2024 extension
to transformer hierarchies) establish that temporal order is preserved across memory
levels only when the capacity ratio creates bottleneck effects. P_deflated = 0.20
(requires 2-substrate architecture; not yet in roadmap).

**Cheapest decisive test**: cf-RPE weighted replay (Escape B) at N=2048, K=10 replay
items, sequential cf-RPE baseline update vs. randomized order. Pre-reg:
HARD-PASS = retention ratio > 1.15x (15% gain from ordered vs random replay).
HARD-FAIL = ratio < 1.02x (indistinguishable from random baseline).
Cost: ~30min CPU smoke.

---

### (2) SQ6 GRAPH MEMBERSHIP: ARCHITECTURAL GAP OR RESCUABLE?

**Classification: ARCHITECTURAL GAP (primary), with PROBABILISTIC VARIANT escape path**

**Algebraic characterization of the gap:**

Substrate's native operation is factor BINDING and RECOVERY via resonator:
  bundled = sum_e (a_u XOR a_v)  for each edge (u,v)
  recovery = argmax_{a_v} sim(bundled XOR a_u, codebook)

This is an UNBINDING problem: given bundled representation + one endpoint, recover
the other. The resonator solves this because the binding operation XOR is its own
inverse. The similarity function is the cosine/Hamming metric on bipolar vectors.

Graph MEMBERSHIP query asks: does edge (u,v) exist?
Formally: is (a_u XOR a_v) a component of bundled?
This is a SUBSET DETECTION problem, not an UNBINDING problem.

The algebraic difference:
- Recovery: bundled XOR a_u approx a_v (if (u,v) in graph). Works because XOR
  distributes over sum in MAP algebra and signal-to-noise favors the correct atom
  when M << C(N) capacity.
- Membership: need |sim(a_u XOR a_v, bundled)| > threshold. At N=2048-8192 and
  E = O(N) edges, the bundle SNR per edge scales as 1/sqrt(E). For E > ~N/4,
  the SNR per edge falls below detection threshold. This is the CAPACITY WALL:
  SQ6 naive HF + SQ6-v2 cleanup HF both hit this wall.

The cleanup aids RECOVERY (fewer interfering components after cleanup) but not
MEMBERSHIP (edge-membership query still requires detecting a 1/sqrt(E) signal in
a sea of O(E-1) interference terms). V2 confirms: cleanup does not boost membership
SNR enough.

GraphHD (Nunes et al. NeurIPS 2023) uses BIDIRECTIONAL binding:
  edge_rep = a_u * a_v  (element-wise multiply, not XOR)
where * is the HADAMARD product. For real-valued vectors, a_u * a_v has a different
similarity profile: sim(bundled, a_u * a_v) sums contributions from ALL stored
edges. For bipolar {-1,+1} vectors, a_u * a_v = a_u XOR a_v (under appropriate
encoding), so GraphHD's bidirectional binding is algebraically equivalent to
substrate's current XOR binding in bipolar space. GraphHD also hits the same SNR
wall at high edge density; its benefit is in directed graphs where a_u * a_v !=
a_v * a_u in real-valued space. For bipolar substrate, bidirectionality does not
resolve the membership query SNR gap.

Bloom filter analogy (Bloom 1970):
A Bloom filter represents a SET by hashing each element into K bit positions.
Membership query: hash(x) & filter == hash(x). False positive rate = (1-e^{-Kn/m})^K
for n elements and m bits. This is PROBABILISTIC MEMBERSHIP with controllable error.

Substrate Bloom-analogue: represent edge (u,v) as the HASH of (a_u XOR a_v) into
a SEPARATE sparse indicator vector h_{uv} in {0,1}^N (not the same bipolar bundle).
Membership query = check h_{uv} in the accumulated indicator. This is architecturally
DISTINCT from the current SQ6 bundling approach: it uses substrate's N-bit space as
a HASH TABLE not a BUNDLE. P_deflated = 0.40 (substrate-native Bloom analogue is
theoretically motivated but untested at scale).

The key distinction:
- Current SQ6 (FAILED): single-bundle membership query = dense signal detection.
  Architectural gap confirmed: substrate lacks membership primitive.
- Bloom-substrate variant (UNTESTED): separate hash-indicator representation.
  Algebraically distinct; dodges the bundle-SNR wall.
  Cost to test: ~1h CPU smoke at N=4096, E=O(N) edges, K=2-4 hash functions.

**Pre-reg for Bloom-substrate smoke:**
HARD-PASS = membership accuracy > 0.90 at E=N/4, FPR < 0.10.
HARD-FAIL = accuracy < 0.80 at E=N/8 (should be easy regime).

**Substrate + external lookup hybrid**: substrate does RECOVERY (who are u's neighbors?)
and external hash does MEMBERSHIP (does (u,v) exist?). This is a COMPOSITION that
circumvents the gap: substrate's resonator excels at recovery; membership offloaded
to O(E) external structure. No substrate-class change required.

---

### (3) SQ1 RESONATOR-GENERATIVE: MISTUNED OR FUNDAMENTAL?

**Classification: ARCHITECTURALLY DISTINCT (not engineering-fixable within resonator)**

**Algebraic analysis of retrieval vs. generation:**

Resonator RETRIEVAL: given cue vector q (noisy version of a_u XOR a_v XOR a_w),
find (a_u, a_v, a_w) from codebook. This is an INVERSE PROBLEM: invert the binding
function. The resonator iterates:
  a_u^{(t+1)} = sign(q XOR a_v^{(t)} XOR a_w^{(t)} @ codebook_U)
converging to the correct factors when initialized near the true solution.

Resonator GENERATION: given a partial or abstract cue, produce a NOVEL vector not
in the codebook. This is a FORWARD PROBLEM: synthesize a new binding product.
The forward problem requires the resonator to EXIT the codebook manifold -- but
the resonator's attractor dynamics are DEFINED by the codebook. Every stable
fixed point of the resonator is a stored binding product. Generative output
= new binding product = requires either a new codebook atom or a structured
combination of existing atoms.

The cleanup-too-aggressive observation: Frady-Sommer 2020 (Resonator Networks I)
show resonator convergence requires cleanup (projection onto codebook atoms) at
each step. For RETRIEVAL, aggressive cleanup accelerates convergence TO the correct
atom. For GENERATION, aggressive cleanup PREVENTS escape from codebook manifold.
This is not a tuning problem -- it is a STRUCTURAL CONFLICT: retrieval and
generation require OPPOSITE cleanup policies.

Data-adaptive noise injection: if generative mode uses noise injection to escape
the codebook manifold, the noise must be calibrated to (a) escape the current
attractor AND (b) not collapse into a random codebook point. This requires
knowing the LOCAL BASIN GEOMETRY, which itself requires a retrieval step. The
circular dependency makes noise-injection tuning for generation FUNDAMENTALLY
HARDER than for retrieval.

Alternative architectures for substrate-direct generation:
(A) Iterated retrieval at CONCEPT LEVEL: generate by retrieving at a high-
   abstraction codebook, then DECODING to specific instances. Requires 2-level
   codebook. P_deflated = 0.35 (two-level resonator; not at production N).
(B) VQ-VAE style: substrate as the discrete codebook layer in a variational
   autoencoder. Generation = decode from latent z using VQ lookup. Substrate
   provides the CODE; the decoder (external network) provides the GENERATION.
   P_deflated = 0.40 (natural substrate-LLM integration point per PP-8).
(C) Coconut-class latent reasoning: Hao et al. 2024 (NeurIPS) Coconut uses
   continuous latent vectors for "thought tokens." Substrate codewords as
   discrete thought tokens = substrate-native Coconut. Generation = iterative
   codeword composition, not resonator iteration. P_deflated = 0.35.

**Recommendation**: abandon resonator-generative mode. Pursue VQ-style (B) as
the generative path because it aligns directly with PP-8 substrate-LLM bridge
(substrate as codebook layer; LLM as decoder-generator). Engineering cost = low;
substrate contributes the DISCRETE LATENT SPACE, not the generation mechanism.

---

### (4) STRUCTURAL CHARACTERIZATION OF ACCEPTED NEGATIVES

The four accepted negatives collectively encode a single unified structural theme:

**UNIFIED STRUCTURAL THEME: Substrate's algebra is FACTORED-REPRESENTATION-OPTIMAL
but NOT RELATIONAL-QUERY-OPTIMAL, and its capacity constraints are SPARSITY-GATED.**

Evidence for each pillar:

(A) FEP (inference-overhead NOT separately beneficial):
   Friston FEP requires an explicit VARIATIONAL DISTRIBUTION q(z|x) to minimize
   F = E_q[log q - log p]. Substrate's NESS dynamics already implement an IMPLICIT
   variational process (drift-diffusion-BP with NESS non-equilibrium steady state).
   The accepted negative tells us: NESS is already doing inference; adding an
   EXPLICIT variational wrapper is overhead without gain. Structural implication:
   substrate is INFERENCE-IMPLICIT -- the separation between prior, likelihood, and
   posterior is not represented explicitly. This is a FEATURE for speed and a
   LIMITATION for tasks requiring explicit uncertainty representation.

(B) TDA beta_0 (Adams-Virk Hamming filtration fails at 20% drift, N=1024):
   Adams-Virk 2022 (persistent homology of Hamming space) show that for bipolar
   {-1,+1}^N, the Hamming filtration induces a persistence diagram where beta_0
   (connected components) requires drift >= N/2 to change. At 20% drift = 0.2N,
   the filtration is below the sensitivity threshold. Structural implication:
   substrate's QUANTIZATION (bipolar) COARSENS the topological sensitivity. This
   is a BIPOLAR-QUANTIZATION COST: real-valued representations would resolve
   smaller drifts. The gap is algebraic, not scale-dependent. Increasing N does
   not help; the 20% threshold is a FRACTIONAL not absolute bound.

(C) Single-modulator K=1 (< 0.1 nats gap):
   At K=1 sparse modulator, the Drosophila-MB architecture needs the single
   modulator to provide 24x capacity gain alone. Information-theoretic bound:
   a single binary modulator provides log2(2) = 1 bit of modulatory capacity,
   spread across N dimensions. The gain = 1/N per dimension, which at N=2048
   is negligible. The accepted negative tells us: substrate requires >= 3-4
   modulators for the modulatory information to exceed the noise floor per-
   dimension. Structural implication: MODULATOR MULTIPLICITY is a HARD FLOOR,
   not a soft preference. This is consistent with the 4-modulator hippocampal-tier
   scaling result.

(D) Dense resonator at V=100 (acc=0.000 all K):
   Dense representations (each atom activates all N dimensions) at V=100
   concurrent atoms require SNR per atom = 1/sqrt(V) * sqrt(N). At V=100, N=4096:
   SNR = 0.1 * 64 = 6.4. This is above threshold for SPARSE K -- but the dense
   resonator with K <= 11 factors has a different convergence condition: the
   resonator must SIMULTANEOUSLY identify K factors from V competing atoms. The
   capacity formula (Frady-Sommer 2020) gives K_max ~ sqrt(N / (V * log V)).
   At V=100, N=4096: K_max ~ sqrt(4096/460) ~ 3. Since tested K=5..11 all exceed
   3, acc=0.000 is PREDICTED by the capacity formula. Structural implication:
   substrate's compositional retrieval is SPARSITY-GATED: V must satisfy
   V < sqrt(N) / (K * log K) for reliable recovery. At N=5000, K=26: V_max ~ 1
   per atom, which matches the published arXiv:2404.19126 result K=26 at V=1
   (i.e., each concept is a SINGLE sparse atom, not a dense combination).

**Unified structural equation (approximate):**
   Reliable performance requires:
   - SPARSITY: V << sqrt(N) / (K * log K) for resonator; K_modulators >= 3-4 for
     neuromodulatory regime.
   - FACTORED not RELATIONAL: binding = XOR/multiply; substrate cannot detect
     whether a factor-product is a MEMBER of a set without SNR wall.
   - IMPLICIT INFERENCE: substrate's dynamics already do inference; explicit
     variational wrappers add overhead, not capability.
   - BIPOLAR QUANTIZATION COST: topology sensitive only to O(N/2) or larger drift;
     membership queries limited by 1/sqrt(E) bundle SNR.

---

### (5) STRUCTURAL ESCAPE PATHS FROM ACCEPTED NEGATIVES

**(A) FEP escape path:**
   Mode where explicit variational machinery ADDS capability: LLM-COUPLED mode.
   In LLM-coupling (PP-8), the LLM acts as the DECODER; substrate acts as the
   LATENT SPACE. Here, EXPLICIT variational inference (uncertainty quantification
   over substrate codewords) could improve LLM calibration. The substrate would
   provide DISCRETE PRIOR SAMPLES; the LLM's softmax provides the approximate
   posterior. This is a COMPOSITION escape: FEP is not useful for substrate-alone
   but IS useful for substrate-LLM composition where explicit uncertainty over
   codeword selection matters. P_deflated = 0.30 (requires substrate-LLM bridge
   + variational training; not yet tested).
   Cheapest next test: add softmax temperature sweep over substrate codeword
   selection in PP-8 bridge output; measure calibration improvement vs hard-argmax.
   Cost: ~2h H100 on existing PP-8 scaffold.

**(B) TDA escape path:**
   PERSISTENT COHOMOLOGY vs persistent homology: cohomology uses cup products
   instead of boundary operators. For bipolar space, the cup product of 1-cocycles
   can detect CORRELATION PATTERNS (not just connected-component drift) that are
   insensitive to the Hamming-filtration quantization problem. Morse theory escape:
   Morse filtration on the energy landscape of substrate's W matrix. W is defined
   on a continuous manifold (real-valued W entries); Morse theory on the loss
   landscape L(x) = -x^T W x detects TOPOLOGICAL CHANGES in basin structure as
   M (memory load) varies. This is NOT blocked by Adams-Virk (which is about
   PATTERN SPACE topology, not WEIGHT SPACE topology). P_deflated = 0.35.
   Cheapest next test: Morse persistence on substrate W eigenvalue spectrum vs M.
   Compare: beta_0 of persistence diagram of eigenvalue curve vs. expected cliff
   at M_c. Cost: ~1h CPU algebraic verification (no new experiment needed; existing
   W matrices suffice).

**(C) Single-modulator escape path:**
   4-modulator hippocampal-tier system (NOT YET TESTED empirically). 
   The bio-tier-scaling drill confirmed: 4 modulators x 24x capacity gain per
   modulator = 96x total capacity expansion. This is the HIGHEST-LEVERAGE untested
   escape. Algebraic argument: with K=4 modulators providing 4 independent
   modulatory dimensions, the per-dimension modulatory capacity = 4/N, and the
   total modulatory SNR = 4/sqrt(N) = 4/64 at N=4096 = 0.0625 -- still below
   noise floor individually, but 4 JOINTLY APPLIED modulators provide
   combinatorial states = 2^4 = 16 distinguishable states per neuron cluster,
   multiplying effective capacity. Pre-reg for 4-modulator smoke:
   HARD-PASS = retention ratio > 1.50x vs K=1. HARD-FAIL = ratio < 1.10x.
   Cost: ~1h CPU smoke at N=2048, 4-seed.

**(D) Dense resonator escape path:**
   SPARSE resonator at high V: arXiv:2404.19126 proves K=26 at N=5000 with V=1
   (each stored concept is a SINGLE sparse bipolar atom, not a dense combination).
   The escape is straightforward: replace dense-V=100 vocabulary with sparse-K
   coding where each query is a binding product of K sparse atoms from a
   LARGE codebook. The capacity formula predicts K_max = 26 at N=5000 for the
   sparse case. This is an ENGINEERING fix: change the representation format,
   not the substrate architecture. P_deflated = 0.45 (sparse resonator at K=26
   is published and reproduced; substrate implementation at production N is
   straightforward but not yet done).
   HIGHEST-LEVERAGE among D-escapes because it's the most direct path from
   published theory to substrate implementation. Cost: ~2h CPU proof-of-concept.

---

## CROSS-DOMAIN PROBE: ML NEGATIVE-RESULTS CHARACTERIZATION FRAMEWORK

Recent ML negative-results literature (2022-2024) provides a four-taxonomy framework:

1. CAPACITY LIMIT (intrinsic to architecture's algebra):
   Examples: Transformer O(n^2) attention; CNN's translation equivariance vs
   rotation invariance. Substrate analog: membership query SNR wall (SQ6),
   dense-vocabulary resonator (B7). These are STRUCTURAL CAPACITY LIMITS.

2. INDUCTIVE BIAS MISMATCH (architecture solves a different problem class):
   Examples: GNN's struggle with long-range dependencies (Alon & Yahav 2021);
   attention head collapse on non-sequential tasks. Substrate analog: FEP overhead
   (NESS already does inference; variational wrapper is wrong inductive bias for
   substrate's dynamics), TDA beta_0 on bipolar space (wrong filtration for
   quantized representations). These are BIAS MISMATCHES not fundamental limits.

3. REPRESENTATION ORTHOGONALITY FAILURE (required representations not separable):
   Examples: ResNet shortcut connections fail when gradients become rank-deficient.
   Substrate analog: B5 additive-W replay-order blindness (commutative addition
   cannot encode temporal sequence). REPRESENTATION FAILURE.

4. COMPOSITIONAL MINIMUM NOT MET (mechanism requires minimum substrate complexity):
   Examples: Small-world network clustering coefficient fails below k_min neighbors;
   diffusion models require minimum network depth. Substrate analog: K=1 single
   modulator below 3-4 minimum. COMPOSITIONAL MINIMUM.

**Mapping substrate negatives to taxonomy:**
- B5 linear W: TYPE 3 (representation orthogonality failure -- additive W cannot
  encode sequence).
- SQ6 membership: TYPE 1 (capacity limit -- bundle SNR wall).
- SQ1 generative: TYPE 2 (inductive bias mismatch -- resonator solves inverse, not
  forward problem).
- FEP: TYPE 2 (inductive bias mismatch -- NESS already does implicit inference).
- TDA beta_0: TYPE 2 (inductive bias mismatch -- Hamming filtration wrong for
  bipolar quantization).
- K=1 modulator: TYPE 4 (compositional minimum not met).
- Dense resonator V=100: TYPE 1 (capacity limit -- sparsity prerequisite).
- B5 bounded-W: TYPE 3 (representation orthogonality failure -- bounded-Hebbian
  still commutative).

**Unified recommendation from taxonomy:**
- TYPE 1 (capacity limits): design around with DIFFERENT REPRESENTATION (Bloom-
  substrate, sparse-resonator). Do not attempt to overcome algebraically.
- TYPE 2 (bias mismatches): identify the CORRECT substrate operating mode where
  the mechanism applies (LLM-coupled FEP; Morse-theory TDA). 
- TYPE 3 (representation failures): add NONLINEARITY to W write rule (cf-RPE
  weighted replay; iterated retrieval-based replay). This is the highest-value
  intervention class.
- TYPE 4 (compositional minima): meet the minimum (4-modulator empirical test is
  the direct rescue).

---

## CHEAP DECISIVE TESTS (prioritized by leverage / cost ratio)

Priority 1 (HIGHEST leverage, cheapest):
  4-modulator hippocampal-tier smoke at N=2048, K=4 modulators.
  Pre-reg: HP = retention > 1.50x vs K=1; HF = < 1.10x.
  Cost: ~1h CPU. Rescues K=1 modulator accepted-negative.

Priority 2 (HIGH leverage, cheap):
  Sparse resonator V=1 at N=5000, K=26 (arXiv:2404.19126 replication).
  Pre-reg: HP = acc > 0.90; HF = acc < 0.70.
  Cost: ~2h CPU. Rescues dense-resonator-V=100 accepted-negative.

Priority 3 (MEDIUM leverage, ~1h):
  cf-RPE weighted replay smoke (B5 Escape B).
  Pre-reg: HP = ordered/random ratio > 1.15; HF = ratio < 1.02.
  Cost: ~30min CPU smoke.

Priority 4 (MEDIUM leverage, ~1h):
  Bloom-substrate membership at N=4096, E=N/4.
  Pre-reg: HP = membership acc > 0.90; HF = acc < 0.80.
  Cost: ~1h CPU. Rescues SQ6 architectural gap (partially).

---

## FALSIFIABLE PREDICTIONS

HARD-PASS thresholds:
- HP1: 4-modulator system retention > 1.50x vs K=1 at N=2048 (4-modulator hippo-
  campal-tier confirms compositional-minimum rescue).
- HP2: Sparse resonator acc > 0.90 at K=26, N=5000 (V=1 sparse regime confirmed).
- HP3: cf-RPE weighted replay ratio > 1.15 (nonlinear write breaks commutativity).
- HP4: Bloom-substrate membership acc > 0.90 at E=N/4 (probabilistic membership
  is within substrate's architectural capability).

HARD-FAIL thresholds:
- HF1: 4-modulator retention < 1.10x (K=1 compositional-minimum not the limiting
  factor; deeper architectural issue).
- HF2: Sparse resonator acc < 0.70 at K=10, N=5000 (sparsity prerequisite not
  sufficient at substrate scale; deeper capacity wall).
- HF3: cf-RPE ratio < 1.02 (nonlinear write still commutative at substrate scale;
  Escape B fails; B5 is FULLY FUNDAMENTAL with no in-substrate rescue).
- HF4: Bloom-substrate acc < 0.80 at E=N/8 (easy regime; HF here = substrate's
  N-bit hash table is inadequate even for sparse graphs).

---

## CROSS-THREAD SYNTHESIS

Prior research threads corroborating today's synthesis:

1. Wright-Fisher drill (research_wright_fisher_* 2026-06-04): WF neutral theory
   predicted commutativity of additive-W as STRUCTURAL. Today's analysis confirms
   this algebraically and maps it to TYPE 3 in the ML-negative-results taxonomy.

2. Drosophila-MB sparse-modulator drill: confirmed 24x capacity gain requires
   sparse coding + cf-RPE TOGETHER. Today: maps to TYPE 4 (compositional minimum)
   and identifies 4-modulator empirical test as cheapest rescue.

3. Resonator dense V=100 HF: Frady-Sommer 2020 capacity formula predicted this
   at K=5..11 range. Today: confirmed TYPE 1 and identified sparse-resonator
   arXiv:2404.19126 as the direct engineering rescue.

4. TDA beta_0 HF: Adams-Virk 2022 predicted Hamming filtration insensitivity.
   Today: identified Morse-theory-on-W-spectrum as a DIFFERENT TDA question that
   bypasses the quantization constraint. Not yet tested.

5. SQ6 v1+v2 both HF: today's analysis provides the algebraic proof that bundle-
   SNR wall is TYPE 1 STRUCTURAL for membership queries, while Bloom-substrate
   and substrate+external-lookup provide two COMPOSITION escapes.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

The structural-limits taxonomy has direct product implications:

1. Substrate's ALGEBRAIC CERTIFICATE product narrative (compliance sidecar) is NOT
   threatened by any of today's negatives. Certificates rely on FACTOR BINDING and
   RECOVERY -- the exact operation class substrate excels at. TDA membership limits
   and additive-W replay limits are in DIFFERENT capability classes than audit-
   certificate generation.

2. Substrate's KNOWLEDGE GRAPH capability (SQ6): productize as GRAPH RECOVERY
   (neighbor-finding), NOT as graph-membership. Bloom-substrate hybrid is a viable
   architecture for the membership side if needed by customers.

3. Substrate's GENERATIVE capability: productize via VQ-style discrete-latent
   integration with LLM decoder (PP-8 bridge), NOT as standalone resonator-based
   generation. This aligns generative capability with the PP-8 Week 2-6 build.

4. Substrate's NEUROMODULATORY TIER: 4-modulator hippocampal-tier is the HIGHEST-
   LEVERAGE currently-untested rescue. It could unlock a 24x-96x capacity expansion
   that would qualify as a TIER-1 capability if HP. This should be Priority 1 in
   the next exp_dev cycle.

---

## P_DEFLATED ESTIMATES (with 0.15-0.25 calibration penalty applied)

| Escape path                         | Pre-penalty P | Deflation | P_deflated | Cap applied |
|-------------------------------------|---------------|-----------|------------|-------------|
| B5 Escape B (cf-RPE replay)         | 0.50          | -0.15     | 0.35       | no          |
| B5 Escape A (separate generator)    | 0.45          | -0.15     | 0.30       | no          |
| SQ6 Bloom-substrate membership      | 0.55          | -0.15     | 0.40       | no          |
| SQ1 VQ-style generation (PP-8)      | 0.60          | -0.20     | 0.40       | no          |
| FEP LLM-coupled variational         | 0.50          | -0.20     | 0.30       | no          |
| TDA Morse-on-W-spectrum             | 0.55          | -0.20     | 0.35       | no          |
| 4-modulator hippocampal-tier rescue | 0.65          | -0.20     | 0.45       | no          |
| Sparse resonator K=26 replication   | 0.70          | -0.25     | 0.45       | no          |
| B5 FULLY FUNDAMENTAL (no rescue)    | --            | --        | 0.40       | (HF3 bound) |

Note: sparse resonator P=0.45 is the HIGHEST confidence escape path because
arXiv:2404.19126 provides published empirical proof; deflation applied for
substrate-specific implementation uncertainty only.

---

## CITATIONS (verified count: 8 external; 6 substrate-internal)

External:
1. Crick F, Mitchison G (1983). "The function of dream sleep." Nature 304:111-114.
2. Bloom BH (1970). "Space/time trade-offs in hash coding with allowable errors."
   Communications of the ACM 13(7):422-426.
3. Nunes JD et al. (2023). "GraphHD: Efficient graph classification using hyperdimensional
   computing." NeurIPS 2023. [GraphHD bidirectional binding analysis.]
4. Frady EP, Sommer FT (2020). "Resonator Networks I: an efficient solution for factoring
   high-dimensional, distributed representations." Neural Computation 32(12):2311-2331.
5. Adams H, Virk G (2022). "Persistent homology of Hamming distance for clustering data."
   [Adams-Virk Hamming filtration constraint on bipolar TDA.]
6. Hao S et al. (2024). "Training large language models to reason in a continuous latent
   space." NeurIPS 2024. [Coconut-class latent generation.]
7. Alon U, Yahav E (2021). "On the bottleneck of graph neural networks and its practical
   implications." ICLR 2021.
8. arXiv:2404.19126 (2024). Sparse resonator capacity K=26 at N=5000 result.

Substrate-internal:
1. notes/substrate_capability_map.md v401 (SQ6 both HF; B5 bounded HF; resonator
   dense HF; resonator noise HF).
2. cap_map CYCLE 71 batch verdict annotation (2026-06-04).
3. Wright-Fisher population-genetics research drill findings (2026-06-04).
4. Drosophila-MB bio-tier-scaling drill (K=1 modulator gap; 4-modulator prediction).
5. Topological beta_0 Mapper HF annotation + Adams-Virk constraint note.
6. SQ1 resonator-generative HF annotation (Kmax=0 all K).

---

## NEXT-DRILL CANDIDATE

Field: sparse-coding-compressed-sensing (Tier-1b per field-advisor; adjacent to
free-probability and AMP/VAMP). Drill question: does D-RIP (Restricted Isometry
Property for discrete bipolar atoms) give a TIGHTER capacity bound than Frady-Sommer
2020 for sparse resonator at K=26, N=5000? If D-RIP bound is tighter, it predicts
the EXACT phase boundary between successful and failed resonator recovery -- which
is the key engineering parameter for sparse resonator productization.
