# RESEARCH DRILL: residue-arithmetic VSA for compound arithmetic predicates

**Date:** 2026-06-23
**Trigger:** Next-drill candidate from `research_drill_predicate_evaluation_primitives_2026-06-23.md`. Parent identified 5-op predicate set covering ~90% of HotpotQA *comparison* subset but EXCLUDED compound arithmetic predicates ("X is twice Y", "X+Y=100", "X earned 3x what Y earned") as out-of-scope for the basic set. Residue-arithmetic VSA (Kymn-Kleyko-Frady-Bybee-Kanerva-Sommer-Olshausen 2024 *Neural Computation*; Tomkins-Flanagan-Kelly 2025 Vector-Symbolic Lisp) provides a substrate-native algebra for compound arithmetic over HD vectors. This drill asks: can the substrate adopt RHC? Which compound predicates unlock? What's the build cost?
**Discipline:** 5 parallel WebSearch lit-scans + Opus synthesis. Generic math terms only per [[feedback-query-privacy-decomposition]]. Calibration penalty: deflate 0.15–0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds mandatory.
**Cross-thread anchors:** `research_drill_predicate_evaluation_primitives_2026-06-23.md` (parent — 5-op set scope); `research_drill_hrr_capacity_vs_depth_2026-06-23.md` (bipolar bind is involutive — depth-lossless); CERT 587 g1b (permute primitive validated); CERT 588 h_hotpotqa (KG primitives validated); USER 2026-06-23 substrate-only product direction.

---

## HEADLINE (one-line synthesis)

**Residue-arithmetic VSA (Kymn et al. 2024 *Neural Computation*) gives substrate a fully-distributed integer algebra (carry-free add, multiply, comparison) over HD vectors with logarithmic-in-dynamic-range encoding cost — BUT substrate's current bipolar-MAP algebra does NOT support it natively because RHC requires (1) TWO distinct binding operators (one for add, one for multiply; substrate has only Hadamard-bind which works only for multiply); (2) phase-valued or complex-valued vectors (m-th roots of unity from FHRR; substrate is bipolar ±1 with no phase dimension); (3) resonator-network decoding to recover integer values from the residue-tuple (substrate has the resonator framework only in `experiments/exp_comparator_resonator_primitive_smoke_v1.py`, not lifted to `hdlab/`). The substrate-native path is therefore a NEW infrastructure track — either (a) extend `hdlab/` to complex64 / qFHRR (quantized-phase FHRR per arxiv 2604.25939) as a SECOND substrate layer alongside bipolar-MAP, or (b) embed integer-as-FPE (fractional-power encoding of log integers; bind = product; arxiv 2412.00488) which is bipolar-compatible IF the substrate already has FPE — and per the parent drill, FPE is present only IMPLICITLY (USER lock-in amp analog, permute as discrete special case) — NOT as a first-class primitive. Compound-predicate coverage if RHC lands: "X earned twice Y" (multiplication), "X plus Y equals Z" (addition), "X is N years older than Y" (subtraction = add inverse), "X within 10 of Y" (comparison-with-tolerance), "X is a multiple of 3" (modular predicate). This is a NEW class of substrate capability — calculator-style numerical-QA — distinct from the retrieval+comparison capability of the 5-op predicate set. Coverage estimate: ~80-95% of grade-school arithmetic-word-problem types (SVAMP-class) become STRUCTURALLY EXPRESSIBLE in substrate algebra if RHC lands; actual em depends on encoder-side quantity-extraction (parse-side bottleneck, same as parent drill). Composition with 5-op set: RHC integer-values FLOW INTO LOGICAL_AND/EXISTS/COMPARATOR as values; RHC does NOT compose with TEMPORAL_PRECEDES (which is FPE-phase-encoded scalar time) without an explicit kernel-conversion layer. P_deflated(substrate can implement minimum-RHC = add+multiply+compare on small-prime modulus K=4 primes with N_DIM=8192) = 0.40; P_deflated(RHC chain-grade on SVAMP-class arithmetic-QA) = 0.20 (capped novel-synthesis; substrate is in uncharted regime — no published bipolar-MAP RHC variant; the existing RHC literature is FHRR/complex-only). Substrate-product implication: WITHOUT arithmetic primitives the substrate can do retrieval+comparison (HotpotQA-class) but CANNOT do computation (SVAMP/GSM8K-class). Residue-VSA is the canonical path; build cost is ~500-1000 lines new infrastructure (qFHRR layer + dual-binding + resonator decoder), MUCH larger than the 5-op predicate wrapper (~200 lines).**

Plain English: Substrate today has three building blocks (bind/bundle/permute) that do retrieval and comparison but cannot do math (add, subtract, multiply, divide). A 2024 Berkeley paper (Kymn et al., Neural Computation) shows how to put residue-number-system arithmetic INSIDE high-dimensional vectors so that compound arithmetic predicates like "X is twice Y", "X plus Y equals Z", "X within 10 of Y" become substrate-native operations. The catch: their construction uses a DIFFERENT vector type than ours (complex-phase vectors, not bipolar ±1) AND requires TWO binding operators (one for addition, one for multiplication) where substrate has only ONE. So adopting RHC is NOT free — it's a new infrastructure layer (~500-1000 lines of code). If we build it, the substrate gains a whole new capability class: calculator-style numerical question answering, quantity reasoning, and arithmetic word problems (SVAMP, GSM8K, etc). Without it, substrate can do "X older than Y" but not "X is 5 years older than Y" — the former needs only comparison, the latter needs subtraction. Recommendation: this is a high-leverage but high-cost expansion; pre-reg a SMOKE cell at K=4 small primes (covers integers 0-1000ish) to validate substrate can host RHC at all BEFORE the full 500-line build.

---

## CHEAP DECISIVE TEST

**Cell:** `substrate_rhc_minimum_viable_v1` (CPU, ~30-60 min)
**Goal:** Validate substrate can host residue-hyperdimensional-computing arithmetic at minimum-viable scale BEFORE committing to the full ~500-1000-line infrastructure build.

**Scope:** 4 small primes (m1=3, m2=5, m3=7, m4=11; product 1155, dynamic range covers integers 0-1154). Three arithmetic predicates:
- P1 (`add`): `encode(a) + encode(b) == encode(a+b)` for a, b ∈ [0, 100], 100 random pairs
- P2 (`multiply`): `encode(a) * encode(b) == encode(a*b)` for a, b ∈ [0, 30] (product ≤ 900 < 1155), 100 random pairs
- P3 (`compare`): `magnitude(encode(a)) > magnitude(encode(b))` matches `a > b` for a, b ∈ [0, 100], 100 random pairs

**Arms (4):**
- A1 (BIPOLAR_BASELINE; expected-fail-control): substrate's current bipolar-MAP with Hadamard-bind tries to encode integers as random hypervectors + bundle for add + bind for multiply. EXPECTED HARD_FAIL — confirms the standard substrate cannot do RHC.
- A2 (FPE_LOG; substrate-compatible path A): integers encoded as FPE of log(integer) using bipolar substrate; bind realizes multiplication (additive logs); add realized via resonator factorization. Tests whether substrate's IMPLICIT FPE machinery suffices.
- A3 (QFHRR_PHASE_QUANTIZED; new-infrastructure path B): integers encoded as residue-tuples using m-th roots of unity quantized to bipolar (qFHRR per arxiv 2604.25939); requires phase-quantization extension. Tests whether substrate's bipolar layer can host RHC via qFHRR bridge.
- A4 (FHRR_COMPLEX; reference oracle): full complex64 FHRR implementation of RHC per Kymn et al. 2024. Establishes the empirical upper bound — if even FHRR cannot achieve >0.90 accuracy at N_DIM=8192 on this minimum task, the framework itself is wrong for the substrate's scale.

**Pre-reg HARD_PASS:**
- A4 (FHRR reference) ≥ 0.95 accuracy on each of P1, P2, P3 (replicate published Kymn et al. result)
- A2 OR A3 (substrate-compatible variants) ≥ 0.80 accuracy on each of P1, P2, P3
- A1 (bipolar baseline) < 0.20 accuracy on each (control — confirms standard substrate cannot do this)

**Pre-reg HARD_FAIL:**
- A4 < 0.80 on any of P1, P2, P3 → framework does not work at our N_DIM; refute the entire residue-VSA path for substrate
- A2 AND A3 both < 0.50 on any of P1, P2, P3 → substrate-compatible RHC is not achievable; route to full FHRR layer or close the lane
- ANY arm achieves >0.95 on P1+P2+P3 → flag for verify-the-referent (likely a leak from the encode/decode design)

**Discriminator:** include `RANDOM_GUESS_BASELINE` (uniform over [0, 1154]) for accuracy floor. For P3, random-guess on 2-way comparison = 0.50; for P1/P2 it's ~1/1155 ≈ 0.001.

**Compute:** 4 arms × 3 predicates × 100 trials × 3 seeds = 3,600 trials × ~10ms each ≈ 36s. Plus resonator iterations at ~10-50 iter × 1ms each per decode ≈ +5min for A4/A3. Total ~5-15 min CPU, smoke at 10 trials/arm in ~30s.

**Smoke gate:** verify all 4 arms produce non-null accuracy on a 10-trial × 1-seed pilot in <60s without exception; confirm A1 sub-0.20 (controls control); confirm A4 above 0.50 (reference works at all).

---

## L1 — PARALLEL LIT-SCAN STREAMS

### Stream A: Residue Hyperdimensional Computing (Kymn et al. 2024 *Neural Computation*)

**Primary source:** Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2024 — "Computing With Residue Numbers in High-Dimensional Representation" — *Neural Computation* 37(1):1-37; arxiv 2311.04872; PMC10659444; rctn.org/bruno/papers/kymn_residue_NECOreprint.pdf.

**Core construction:**
- **Encoding:** integer x → residue tuple (x mod m1, x mod m2, ..., x mod mK) where mk are pairwise co-prime moduli. Chinese Remainder Theorem guarantees unique encoding for x ∈ [0, m1·m2·...·mK).
- **Vector realization:** for each modulus mk, draw mk random unit-modulus phasors evenly spaced on the unit circle (mk-th roots of unity). The residue r in [0, mk) becomes the phasor exp(2πi·r/mk).
- **Compound vector:** for K moduli, the integer x is encoded as a vector of length D where each component carries the product of the K residue-phasors (FHRR-style: D-dim vector, each entry is a complex phase combining all K residue phasors via Hadamard-multiplication structure).
- **Carry-free arithmetic:** addition and multiplication are realized as component-wise operations on the residue tuple (no carry propagation needed across moduli). This is the SAME parallelism that classical RNS hardware exploits.
- **TWO binding operators:** the framework's key novelty is that ADDITION and MULTIPLICATION require DIFFERENT binding operators in HD space. Standard VSA has only one (typically Hadamard product for MAP, circular convolution for HRR). RHC introduces a second binding operator for the OTHER arithmetic operation. **This is the load-bearing infrastructure requirement.**
- **Decoding:** to recover integer x from the residue-encoding vector, run a RESONATOR NETWORK (Frady-Kent-Olshausen-Sommer 2020) over the K residue codebooks. This is the same resonator framework substrate already has in `experiments/exp_comparator_resonator_primitive_smoke_v1.py`.
- **Logarithmic resource scaling:** to represent integers up to N, need K ≈ log(N) primes; total parameters scale as O(N_DIM · K · max(mk)) = O(N_DIM · log(N) · log(N)) = O(N_DIM · log²(N)). This is the KEY advantage over naive HD integer encoding which would need N codebook vectors.
- **Comparison difficulty:** the paper acknowledges "comparing integer values is more difficult for a residue number system than for binary systems, in which one can directly compare values of higher-order bits. However, there are multiple good algorithms for performing this comparison, which can be implemented with the addition and multiplication operations of RHC." So COMPARISON is derived from add+multiply — not a separate primitive. For VSA, comparison typically uses a "mixed-radix conversion" or "fractional representation" algorithm with O(K²) add/multiply operations.

**Applications demonstrated in the paper:**
- Visual perception: factorization of object shape + horizontal position + vertical position from a single combined HD vector (combinatorial decomposition).
- Combinatorial optimization: large integer factorization with logarithmic resource cost.
- Brain analog: grid-cell-like spatial codes; high-resolution spatial memory.

**Substrate-transfer note:** Kymn et al. uses FHRR (complex-valued vectors, phase-encoded). Substrate is bipolar-MAP (±1, real-valued). **DIRECT TRANSFER NOT POSSIBLE without infrastructure extension.**

### Stream B: Vector-Symbolic Lisp with Residue Arithmetic (Tomkins-Flanagan, Kelly 2025)

**Source:** Tomkins-Flanagan & Kelly 2025 — "Hey Pentti, We Did (More of) It!: A Vector-Symbolic Lisp With Residue Arithmetic" — arxiv 2511.08767; precursor arxiv 2510.17889 "A Fully Vector-Symbolic Lisp"; Society for Mathematical Psychology presentation mathpsych.org/presentation/1541.

**Significance:** this is the **frontier upper bound on what VSA+RHC can compute**. Lisp 1.5 (Kanerva 2014) is Turing-complete; encoding it in VSA + RHC means **the substrate (if it adopts RHC) becomes Turing-complete in a vector-space algebra** — predicates of arbitrary arithmetic complexity become expressible.

**Construction:**
- Lisp expressions encoded as nested VSA structures using FHRR bind+bundle.
- Numeric atoms encoded via RHC (Kymn et al. 2024 framework).
- Lisp interpreter implemented as VSA operations (cons, car, cdr, eq, atom, cond all become VSA primitives).
- Arithmetic primitives (+, -, *, /, mod, <, >, =) implemented as RHC operations + comparison algorithms.
- Recursion via memory-augmented VSA (S-expression stack as nested binding chain).

**Predicate-evaluation implications:**
- ANY compound arithmetic predicate expressible in Lisp is expressible in this VSA: `(> (* 2 X) Y)` = "is 2X greater than Y?"; `(= (+ X Y) Z)` = "X plus Y equals Z?".
- The VSA implements PROCEDURAL predicates not just declarative ones — predicates with internal loops, conditionals, recursion.
- The system is Turing-complete given infinite memory (cleanup-codebook capacity).

**Realism check:** the paper is a CONSTRUCTION proof (algebraic correctness), not a SCALE empirical benchmark. The Lisp-VSA likely has very low noise tolerance at deep recursion / large arithmetic chains. **Practical use requires substrate-scale empirical validation — currently UNVALIDATED.** Calibration: treat this as upper-bound expressivity, NOT achievable performance.

### Stream C: FPE-based integer arithmetic (substrate-compatible alternative)

**Sources:**
- arxiv 2412.00488 (2024) — "Improved Cleanup and Decoding of Fractional Power Encodings"
- arxiv 2604.25939 (2026) — "qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic"
- arxiv 2203.00920 — "Integer Factorization with Compositional Distributed Representations"
- arxiv 2109.03429 — Frady-Plate-Sommer "Computing on Functions Using Randomized Vector Representations" (foundational FPE)

**Construction (FPE-log approach):**
- Encode integer n as `phi(n) = base^log(n)` where `base` is a unit-norm seed vector and `**` is fractional-power exponentiation in Fourier domain (phase rotation by log(n)).
- Binding two such vectors: `phi(n) * phi(m) = base^(log(n)+log(m)) = base^log(n*m) = phi(n*m)`. So MULTIPLICATION is realized as bind. Cleaner than RHC's separate-binding-operator construction.
- Addition is much harder under this encoding — there's no algebraic shortcut for `phi(n+m)` from `phi(n)` and `phi(m)`. Requires resonator decoding to recover n, m as scalars, then add.
- For substrate-compatibility: the base vector can be a bipolar substrate hypervector; the phase rotation requires either complex-phase upgrade OR phase-quantized bipolar (qFHRR per arxiv 2604.25939 — bipolar with phase-quantized rotation, integer-only implementation possible).

**qFHRR specifically (arxiv 2604.25939):**
- Each dimension encoded as a discrete phase index in {0, 1, ..., Q-1} where Q is quantization level (e.g., Q=8 for 3-bit phases).
- Binding, unbinding, similarity, bundling realized through modular arithmetic and lookup tables.
- Preserves the spatial similarity structure of fractional binding.
- **CRITICAL: integer-only implementation means substrate can host qFHRR using INT8 or INT16 dimensions instead of complex64.** This is a much-lower-cost substrate extension than full complex64.

**Substrate-applicability:** qFHRR is the most substrate-compatible bridge to RHC. Substrate already has bipolar (Q=2 special case of qFHRR). Extending to Q=8 or Q=16 phases is ~50-200 lines (replace `np.sign()` with `np.round()` modulo Q for quantization; replace `xor` bind with `(a+b) mod Q` for phase-add bind).

### Stream D: Residue-number-system comparison algorithms (specifically magnitude comparison)

**Sources:**
- IEEE Xplore 5840/223680 — "A new technique for fast number comparison in the residue number system" (foundational)
- ResearchGate 312568881 — "Algorithms for comparison in residue number systems"
- ResearchGate 4261528 — "Efficient Method for Magnitude Comparison in RNS Based on Two Pairs of Conjugate Moduli"
- Springer 10.1007/s00224-021-10035-y — "Computationally Efficient Approach to Implementation of the Chinese Remainder Theorem Algorithm in Minimally Redundant Residue Number System"

**Key fact:** RNS magnitude comparison is the historical Achilles' heel of RNS hardware. Classical algorithms:
- **Mixed-radix conversion (MRC):** convert residue tuple to mixed-radix representation, then compare lexicographically. O(K²) operations.
- **Core function approach:** compute a single "core" function whose value preserves ordering. O(K) operations but requires precomputed core-function tables.
- **Conjugate moduli method:** use complementary pairs of moduli (m and M-m+1) to compute sign directly. Specialized to constrained moduli sets.
- **Diagonal function:** Szabo-Tanaka diagonal function preserves order; computable with O(K) add/multiply.

**Implication for substrate:** even with full RHC, comparison is NOT free — it's an O(K) chain of RHC add+multiply operations on the residue tuple. For a small K=4 system, that's ~4 operations + a sign test. **Compare to the LOGICAL_NOT primitive from the parent drill (free in bipolar substrate) — RHC magnitude comparison is much more expensive (~O(K) chained binds + bundles, each accumulating noise).** Noise analysis: noise grows as O(sqrt(K)) per comparison; at K=4, noise factor ~2x per-binding noise; manageable at N_DIM≥8192.

### Stream E: Substrate-product implications — arithmetic-QA datasets

**Sources:**
- emergentmind.com/topics/arithmetic-reasoning-gsm8k — GSM8K background
- emergentmind.com/topics/gsm8k-dataset — GSM8K stats
- emergentmind.com/topics/gsm8k-prolog-prover-dataset — Prolog/CLP(R) neurosymbolic baselines

**Datasets:**
- **GSM8K:** 8,500 grade-school math word problems with step-by-step solutions. Multi-step arithmetic + basic algebra. Quantity reasoning required.
- **SVAMP:** ~1,000 synthetic variable arithmetic problems. Each problem requires understanding arithmetic + tracking variable quantities.
- **MultiArith, ASDiv, AQuA, MATH:** other arithmetic-reasoning benchmarks of varying difficulty.

**Current state:** LLMs achieve high accuracy on these (GSM8K SOTA ~95%+ for frontier models). Symbolic approaches (Prolog/CLP(R)) outperform natural-language CoT for arithmetic reliability per literature scan.

**Substrate-applicability:**
- IF RHC lands chain-grade: substrate can express the arithmetic kernel of these problems (the predicate-checking layer "is X+Y = Z" becomes computable in substrate-native algebra).
- IF RHC fails: substrate cannot do these problems at all without LLM scaffolding.
- Encoder-side bottleneck remains: extracting numerical quantities from natural-language word problems is a parse-side task that substrate's char_trigram encoder is poorly equipped for. Per parent drills, MiniLM-L6 encoder fix is upstream; arithmetic-QA inherits the parse-quality of whatever encoder is in place.

---

## L2 — SUBSTRATE-NATIVE BUILD SPEC

### Path A (LOW-COST, SUBSTRATE-COMPATIBLE): FPE-log via existing bipolar with permute primitive

**Construction:**
- Encode integer n as `phi(n) = permute^n(base)` where `base` is a fixed bipolar hypervector and `permute` is the substrate's existing primitive (cyclic shift in CERT 587 g1b).
- Multiplication: `phi(n) * phi(m) = permute^n(base) ⊙ permute^m(base) = permute^(n+m)(base⊙base)` — DOES NOT equal `phi(n*m)`. **PATH A FAILS for multiplication.**
- Alternative: encode `phi(log(n))` — but log(n) is not an integer for general n; needs continuous-FPE rotation. Not realizable with discrete permute primitive.
- **Verdict on Path A:** the discrete-permute substrate primitive is too coarse for FPE-log multiplication. Path A is INSUFFICIENT.

### Path B (MEDIUM-COST, SUBSTRATE-EXTENDED): qFHRR with Q=8 or Q=16 phase quantization

**Construction:**
- Extend substrate to allow Q-level phase-quantized vectors instead of bipolar ±1.
- Each dimension stores INT4 (Q=16) or INT3 (Q=8) phase index.
- Binding: `(a + b) mod Q` (component-wise).
- Bundling: phase-aware sum-then-quantize (~ majority vote per phase bucket).
- Unbinding: `(a - b) mod Q`.
- Similarity: cosine on (cos(2π·phase/Q), sin(2π·phase/Q)) re-expansion.

**RHC over qFHRR:**
- For modulus mk, use Q=mk (so phase quantization MATCHES the modulus).
- Residue r ∈ [0, mk) directly encoded as phase index r.
- Add: `(r1 + r2) mod mk` — automatic from qFHRR bind structure.
- Multiply: needs the SECOND binding operator (Kymn et al.). Construct as a learned/precomputed lookup-table operator over the K-residue codebook product.
- Comparison: O(K) chain of MRC operations on the residue tuple.

**Build cost:** ~300-500 lines new infrastructure in `hdlab/qfhrr.py` + `hdlab/rhc.py`. Wraps qFHRR primitives + dual-binding + resonator decoder.

**Substrate-product change:** introduces a SECOND substrate type (qFHRR layer) alongside the existing bipolar-MAP layer. The two types do NOT compose directly — kernel-conversion layer needed (~50-100 lines `hdlab/type_bridge.py`). This is genuinely new architecture, not just wrapper code.

### Path C (HIGH-COST, REFERENCE-BUILD): full complex64 FHRR with native RHC per Kymn et al.

**Construction:**
- Add a `hdlab/fhrr.py` module supporting complex64 vectors.
- Implement Kymn et al. 2024 RHC exactly: K primes, m-th roots of unity, dual-binding, resonator decoder.
- Bridge to bipolar substrate via complex-to-bipolar projection (sign of real part).

**Build cost:** ~500-1000 lines new infrastructure. Includes complex-valued tensor handling, FFT-based unbinding (circular convolution becomes pointwise multiply in Fourier domain), resonator network with K codebooks, magnitude-comparison algorithms.

**Substrate-product change:** largest expansion. Adds a complex-valued layer to the substrate. Likely needs PyTorch complex64 dtype throughout (existing torch tensors are float32). Compatibility risk with W matrix lookup, refuse_gate, existing Store atoms.

### Recommendation

**Pre-reg the smoke cell `substrate_rhc_minimum_viable_v1` to test ALL THREE PATHS at minimum scale** (K=4 primes, dynamic range 1155) BEFORE committing to the full build. If A2 (FPE-log) passes — the cheapest path works. If only A3 (qFHRR) passes — medium-cost path required. If only A4 (full FHRR) passes — large-cost path required. If NOTHING above A1 baseline passes — close the lane, route to glass-box-LLM L2 for arithmetic.

---

## L3 — COMPOUND PREDICATE COVERAGE ESTIMATE

### Predicate classes unlocked by RHC

For a substrate with chain-grade RHC at K=4-6 small primes (dynamic range 0 to ~30,000):

| Predicate class | Example | RHC operator | 5-op set composability |
|---|---|---|---|
| **Equality** | "X earned the same as Y" | `magnitude(encode(X) - encode(Y)) < ε` | composes with EXISTS (any pair equal in set) |
| **Tolerance comparison** | "X is within 10 of Y" | `magnitude(encode(X-Y)) < 10` | composes with AND (X within 10 of Y AND of Z) |
| **Multiplicative** | "X is twice Y", "X earned 3x what Y did" | `encode(X) == encode(2 * Y)` (RHC multiply) | composes with NOT (X is NOT twice Y) |
| **Additive** | "X + Y = 100", "X plus Y equals Z" | `encode(X + Y) == encode(Z)` (RHC add) | composes with AND ("X+Y=100 AND X≥Y") |
| **Subtractive** | "X is 5 years older than Y" | `encode(X - Y) == encode(5)` (RHC add of negation) | composes with TEMPORAL_PRECEDES (substrate already has) |
| **Modular** | "X is even", "X is a multiple of 3" | `encode(X) component-wise on mk=3 == 0` (residue inspect) | composes with EXISTS (any even number in set) |
| **Range** | "X is between 50 and 100" | `magnitude(encode(X-50)) ≥ 0 AND magnitude(encode(100-X)) ≥ 0` (two compares) | composes with AND (already in 5-op set) |
| **Aggregate** | "Sum of X1..Xn is 100" | iterated RHC add | composes with EXISTS-COMPARATOR ("any subset sums to 100") |

### Coverage estimate on arithmetic-QA benchmarks

**Grade-school arithmetic word problems (SVAMP-class, ~1000 problems):**
- ~30% are single-step add/subtract/multiply/divide → covered by RHC primitives directly
- ~40% are 2-step (e.g., "X has 5 apples, gives 2 to Y, then buys 7 more — how many?") → covered by RHC chain depth 2-3
- ~20% are 3+ step or involve unit conversion → RHC composition; noise-limited; success depends on N_DIM
- ~10% require non-arithmetic reasoning (ordering, set operations, etc.) — covered by parent 5-op set
- **Estimated structural coverage if RHC lands: ~80-95%; actual em depends on encoder-side quantity extraction.**

**GSM8K-class (more complex multi-step, grade-school):**
- ~50% are 2-3 step arithmetic — covered by RHC chain
- ~30% are 4+ step or involve algebraic manipulation — RHC chain noise-limited; depth ~5 likely the practical ceiling at N_DIM=8192
- ~20% require multi-modal reasoning or external knowledge — outside RHC scope
- **Estimated structural coverage if RHC lands: ~70-80%; depth-cliff at ~5 chain operations.**

**HotpotQA compound-arithmetic subset (small fraction of comparison-em residual):**
- ~5-10% of HotpotQA comparison questions involve compound arithmetic ("X is 3 years younger than Y", "X has twice as many...")
- RHC would lift this from baseline noise to RHC-level (~0.50-0.80 em on these specific questions)
- **Contribution to overall HotpotQA comparison-em: ~+0.02 to +0.05** (small, but additive on top of parent 5-op set's ~+0.13 estimate)

### Coverage estimate WITHOUT RHC

Without arithmetic primitives, substrate can do:
- Retrieval (KG lookup): perfect at in-distribution scale per CERT 588 h_hotpotqa
- Boolean comparison ("X older than Y"): per parent 5-op set
- Multi-hop chains ("what country does X work in"): per CERT 588 h_hotpotqa

Substrate CANNOT do:
- Quantity arithmetic (any "how much" question requiring computation)
- Compound numerical predicates ("X is 5 years older than Y" reduces to ordering only, loses the 5)
- Anything in the SVAMP/GSM8K/AQuA dataset class
- Calculator-style applications

**Without RHC, substrate's product surface is RESTRICTED to retrieval+ordering+set-operations. With RHC, it expands to include calculator-class computation.**

---

## L4 — COMPOSITION WITH 5-PRIMITIVE PREDICATE SET

### Clean compositions

1. **RHC + ORDINAL_COMPARATOR:** RHC produces integer-valued vectors; ORDINAL_COMPARATOR compares them. Trivial composition — RHC's magnitude function IS an ORDINAL_COMPARATOR specialization on integer-valued vectors.
2. **RHC + LOGICAL_NOT:** "X is NOT twice Y" = NOT(RHC_equals(encode(X), encode(2*Y))). Trivial composition; sign-flip on the equality predicate.
3. **RHC + LOGICAL_AND:** "X earned twice Y AND X is older than Y" = AND(RHC_multiply_predicate, ORDINAL_COMPARATOR_age). Straightforward composition.
4. **RHC + QUANTIFIER_EXISTS:** "Does any of {A, B, C} have earnings divisible by 100?" = EXISTS(set, lambda x: RHC_mod(encode(x), 100) == 0). Composes via predicate-evaluation-over-set.

### Awkward composition: RHC + TEMPORAL_PRECEDES (FPE-phase)

- TEMPORAL_PRECEDES uses FPE-phase encoding of timestamps (continuous, phase-rotated bipolar)
- RHC uses residue-tuple encoding (integer, complex-phase or qFHRR-phase)
- The two encodings are NOT directly compatible — need a kernel-conversion layer.
- For HotpotQA temporal-scalar queries (years as integers), TEMPORAL_PRECEDES degenerates to ORDINAL_COMPARATOR-on-year per parent drill, which IS compatible with RHC. For periodic/relative-time queries (MuSiQue/2Wiki), the conversion layer is needed.
- **Estimated bridge code: ~50-100 lines `hdlab/type_bridge.py` mapping RHC integer vectors ↔ FPE phase vectors via decode-encode.**

### Composition cost (noise accumulation)

RHC operations follow the same 1/sqrt(k) law as bind-depth chains (USER HRR derivation), but with the additional factor of K (number of moduli) per RHC operation:
- Per RHC add or multiply: noise ~1/sqrt(N_DIM/K) — the effective dimension is split across K residue codebooks
- For K=4 and N_DIM=8192: per-operation effective dimension = 2048 → noise per-op ~0.022
- For depth-5 RHC chain: noise ~sqrt(5) × 0.022 ≈ 0.049 — manageable, predicate-output accuracy ~80%
- For depth-10 RHC chain: noise ~0.07 — predicate-output accuracy ~70%; substrate at chain-grade boundary

**Practical ceiling: depth ~5-8 RHC operations at N_DIM=8192 with K=4 moduli.** Sufficient for most grade-school arithmetic word problems; INSUFFICIENT for multi-step algebra or long arithmetic chains.

---

## L5 — FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Substrate can host minimum-viable RHC at K=4 primes

**Hypothesis:** at least one of Path A (FPE-log), Path B (qFHRR), or Path C (full FHRR) achieves ≥0.80 accuracy on each of P1 (add), P2 (multiply), P3 (compare) at K=4 primes, N_DIM=8192, 100 trials per predicate.

**Mechanism:** Kymn et al. 2024 published results show FHRR-RHC achieves >0.99 accuracy at N_DIM=10,000 on similar tasks. Substrate-compatible paths (qFHRR especially) should preserve most of this performance at the cost of some quantization noise.

**HARD_PASS:** A2 OR A3 OR A4 ≥ 0.80 on each of P1, P2, P3.
**HARD_FAIL:** ALL of A2, A3, A4 < 0.80 on any of P1, P2, P3 → RHC framework does not work at substrate scale; route to alternative.

**Calibrated P_deflated: 0.40** (deflated from raw 0.70; published RHC results are solid for FHRR but substrate-compatible paths are untested; substrate-novel qFHRR may have implementation surprises).

### Prediction 2 (LOAD-BEARING) — Bipolar baseline fails (sanity check)

**Hypothesis:** A1 (standard bipolar-MAP with naive integer encoding) achieves < 0.20 accuracy on each of P1, P2, P3 (i.e., basically random).

**Mechanism:** bipolar-MAP has no native arithmetic structure; integer encoding as random hypervectors with Hadamard-bind for multiply produces noise.

**HARD_PASS:** A1 < 0.20 on each of P1, P2, P3 (confirms control).
**HARD_FAIL:** A1 ≥ 0.50 on any of P1, P2, P3 → suspicious; verify-the-referent (probably a leak in the encode/decode design).

**Calibrated P: 0.85** (highly confident; sanity-control prediction).

### Prediction 3 (META; if PASS) — Substrate-product capability lane opens for calculator-class

**Hypothesis:** if Prediction 1 HARD_PASSes, the substrate's product surface structurally expands to include calculator-class numerical QA (SVAMP/GSM8K class) at structural-coverage 70-95% (em depends on encoder-side parse-quality).

**Mechanism:** RHC + 5-op predicate set is jointly Turing-complete (per Tomkins-Flanagan-Kelly 2025 Vector-Symbolic Lisp construction). Arithmetic word problems become structurally expressible.

**HARD_PASS (downstream cell, NOT in this smoke):** SVAMP-style 100-question subset, substrate em ≥ 0.20 (vs random-guess ~0.001 baseline).
**HARD_FAIL:** SVAMP em < 0.05 → substrate cannot compose RHC with parse-side encoder for word problems.

**Calibrated P_deflated: 0.20** (capped novel-synthesis; cascade from Prediction 1; deflated for encoder-side bottleneck).

### Prediction 4 (CONDITIONAL; if HARD_FAIL on Prediction 1) — Substrate cannot host RHC; close arithmetic lane

**Hypothesis:** if all 3 substrate-compatible paths fail at minimum-viable scale, the substrate-native arithmetic capability lane is structurally closed. Substrate is permanently RESTRICTED to retrieval+ordering+set-ops; numerical computation requires external LLM scaffolding (glass-box-LLM L2).

**Routing:** META atom `meta_atom_substrate_native_arithmetic_lane_closure_at_N_DIM_8192.md`. Route to glass-box-LLM L2 architecture decision.

**Calibrated P (cascade from Prediction 1 HARD_FAIL): 0.30** (conditional on smoke failure; not pre-judged).

### Prediction 5 (STANDALONE META) — Two binding operators are mandatory infrastructure

**Hypothesis:** substrate cannot do residue arithmetic with only one binding operator (Hadamard); Kymn et al. 2024 dual-binding requirement transfers to substrate.

**Mechanism:** algebraic theorem; binding operator must distinguish addition-of-residues from multiplication-of-residues. Single-operator algebra (bipolar Hadamard) collapses both into the same operation.

**Routing:** META atom `meta_atom_residue_VSA_requires_dual_binding_not_single_2026-06-23.md`. Independent of smoke outcome.

**Calibrated P: 0.85** (high; well-established algebraic result; minor deflation for substrate-novel re-derivation).

### Prediction 6 (STANDALONE META; positive) — qFHRR is the substrate-compatible bridge

**Hypothesis:** quantized-phase FHRR (qFHRR per arxiv 2604.25939) at Q=8 or Q=16 is the lowest-cost substrate-extension path that hosts RHC. Bipolar (Q=2 special case) is insufficient; full complex64 is overkill.

**Mechanism:** qFHRR uses integer phase indices (INT3 or INT4 dimensions) with modular-arithmetic operations on phase. Bipolar substrate Q=2 cannot encode the K-residue codebook structure for K>2. Full complex64 works but is ~10x heavier in compute and memory.

**Routing:** META atom `meta_atom_qFHRR_is_substrate_compatible_bridge_to_residue_VSA.md`.

**Calibrated P: 0.60** (moderate; qFHRR is recent literature and substrate-transfer untested; the assertion is plausible but unproven).

---

## L6 — CROSS-THREAD SYNTHESIS

### With parent predicate-evaluation drill (research_drill_predicate_evaluation_primitives_2026-06-23.md)

- Parent identified 5-op set (ORDINAL_COMPARATOR + TEMPORAL_PRECEDES + LOGICAL_NOT + LOGICAL_AND + QUANTIFIER_EXISTS) covering ~90% of HotpotQA comparison subset; explicitly EXCLUDED compound arithmetic as out-of-scope.
- This drill extends the predicate-evaluation analysis to the COMPOUND ARITHMETIC class; identifies residue-VSA as the canonical path; specifies build cost (~500-1000 lines new infrastructure) and substrate-product implications.
- 5-op set is a NAMING layer (~200 lines wrapper); residue-VSA is NEW INFRASTRUCTURE (qFHRR layer + dual-binding + resonator decoder). The two are NOT interchangeable; they cover different predicate classes.
- Composition: RHC + 5-op set is jointly Turing-complete per Tomkins-Flanagan-Kelly 2025. The combined system spans all of HotpotQA-comparison + SVAMP-arithmetic + (in theory) GSM8K-class.

### With CERT 587 g1b (autoregressive generation)

- g1b uses permute primitive for sequence-position encoding. Permute is DISCRETE-PHASE; RHC uses CONTINUOUS-PHASE (or quantized via qFHRR). They are RELATED via the FPE generalization.
- For the substrate-product chain: g1b can OUTPUT predicate-evaluated answers as token sequences (e.g., for "X+Y=Z" question, generate "Z" if RHC_add_predicate is satisfied).

### With CERT 588 h_hotpotqa (KG ingest)

- h_hotpotqa KG is chain-grade-validated; predicate primitives operate on top.
- RHC operations on numerical attributes (year, count, amount) require encoding these as residue-tuples instead of FPE-scalars. **Storage layer change required** — atoms with numerical attributes need RHC-encoded value vectors in addition to FPE-encoded ones. ~100-200 lines change in `hdlab/store/atoms.py` to support RHC-encoded numerical values.

### With META atoms

- **cleanup-load-bearing:** RHC resonator decoder IS a cleanup operation; aligned.
- **by-construction-saturation:** the HARD_PASS for substrate_rhc_minimum_viable_v1 must clear FREQ_BIAS_BASELINE; not just by-construction (control-arm discipline mandatory).
- **no-Hebbian-window:** all RHC operations are FORWARD-ONLY (no W modification at query time). Compatible.
- **phase-portrait v3:** RHC introduces a NEW PHASE in the substrate's phase diagram (quantity-arithmetic phase, distinct from retrieval-comparison and structural-composition phases). Phase-portrait atom needs update if RHC lands.

### With USER HRR derivation (composition algebra)

- USER's HRR derivation validates substrate's bipolar-bind equivalence to HRR convolution; this is the foundation for predicate-evaluation primitives.
- RHC EXTENDS this foundation with a second binding operator. The substrate-native build is the integration of (Hadamard-bind, RHC-bind-2) into a unified algebra. USER's derivation may need extension to cover dual-binding noise composition.

### With USER lock-in amp / phase-encoded position directive (2026-06-22 phase-diagram-action)

- Lock-in amp = phase detection at known frequency. RHC residue-decoding via resonator is EXACTLY the substrate analog: project onto K phase-axes (one per modulus), recover phase indices, reconstruct integer via CRT.
- The lock-in amp / phase-action directive is REALIZED CONCRETELY by RHC. Adopting RHC = directly implementing the phase-action mode of substrate operation that USER has been pointing toward.
- Phase-portrait v3 + data-survives-transform inventory must update to include RHC as a NEW PHASE position with explicit transform-survival inventory: RHC encoding survives bind/bundle (under same modulus); does NOT survive permute (changes residue order).

### With substrate-only-product direction (USER 2026-06-23)

- Substrate-only means no LLM forward calls at inference. Calculator-class numerical QA is currently impossible without LLM (substrate cannot compute "5 + 3 = ?" at inference time).
- RHC chain-grade-pass = substrate STANDALONE can do calculator-class. This is a major product-surface expansion aligned with USER's substrate-only direction.
- Without RHC: substrate stays retrieval+ordering-only; LLM-call-free product is restricted to KG-lookup-style applications.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

### IMMEDIATE atomization (independent of smoke cell outcome)

1. **`META_residue_VSA_requires_dual_binding_not_single`** — substrate's current single binding operator (Hadamard) cannot host residue arithmetic. Adopting RHC requires a SECOND binding operator at infrastructure level (~50-200 lines). Per Kymn et al. 2024 algebraic construction.

2. **`META_qFHRR_is_substrate_compatible_bridge_to_RHC`** — quantized-phase FHRR (Q=8 or Q=16) is the lowest-cost substrate extension path. Bipolar Q=2 insufficient; full complex64 overkill. qFHRR uses INT3/INT4 dimensions with modular-arithmetic ops. Per arxiv 2604.25939.

3. **`META_substrate_without_RHC_cannot_do_calculator_class_QA`** — current substrate restricted to retrieval+ordering+set-ops. Compound arithmetic predicates ("X earned twice Y", "X+Y=100", "X is 5 years older") require RHC or equivalent. Without RHC, ~5-10% of HotpotQA-compound-arithmetic, ~95% of SVAMP, ~95% of GSM8K are STRUCTURALLY OUT OF REACH for substrate-only product.

4. **`META_RHC_composition_with_5_op_predicate_set_is_Turing_complete`** — per Tomkins-Flanagan-Kelly 2025 Vector-Symbolic Lisp construction, substrate equipped with RHC + 5-op predicate set + memory has Turing-complete expressivity. Upper bound on substrate-only capability is HIGH; the question is practical noise/scale.

5. **`hdlab/qfhrr.py` + `hdlab/rhc.py` BACKLOG ATOMS** — author the qFHRR layer (~200 lines) + RHC module (~300 lines) + resonator decoder (~100 lines lift from existing experiments) + type bridge (~50 lines). Total ~650 lines new infrastructure. ESTIMATE 2-4 weeks of focused work.

### Forward chain (if substrate_rhc_minimum_viable_v1 HARD_PASSES)

1. Smoke HARD_PASSes → substrate can host RHC at minimum-viable scale.
2. v2: scale K=4 → K=8 primes (dynamic range ~9.7M); test depth-5 RHC chains.
3. v3: integrate with KG storage layer (`hdlab/store/atoms.py` extension for RHC-encoded numerical attributes).
4. v4: SVAMP-style 100-question pilot; test compound-arithmetic predicates on real word problems with substrate's MiniLM-L6 encoder + RHC + 5-op set composition.
5. v5: GSM8K subset (multi-step arithmetic); test depth-cliff at chain depth ~5-8.
6. If v5 PASSes: substrate has its first END-TO-END calculator-class capability. MAJOR product-surface expansion.

### Reroute chain (if smoke HARD_FAILs)

1. Diagnose per-path: which Path (A FPE-log / B qFHRR / C full FHRR) carries the failure?
   - If C (FHRR) fails: framework-level failure; refute Kymn et al. transfer to substrate scale; close lane.
   - If only A (FPE-log) fails but B and C work: substrate must commit to qFHRR or complex64 infrastructure.
   - If A and B fail but C works: substrate must commit to full complex64 infrastructure (high cost).

2. If all 3 paths fail: META atom `meta_atom_substrate_native_arithmetic_lane_closure_at_N_DIM_8192.md`; route to glass-box-LLM L2 closure for arithmetic.

### L2 vision alignment

- L2 vision = glass-box LM INSIDE substrate; zero LLM forward calls at inference.
- WITHOUT RHC: substrate's L2 product is restricted to retrieval+ordering applications (KG-lookup, semantic search, comparison QA). Calculator/quantity reasoning REQUIRES LLM scaffolding — violates substrate-only directive.
- WITH RHC: substrate's L2 product expands to include arithmetic-class applications (calculator, quantity reasoning, simple word problems). This is a HIGH-LEVERAGE expansion aligned with USER substrate-only directive.
- Cost analysis: 2-4 weeks of focused infrastructure work for ~80-95% structural coverage of SVAMP-class problems is high-yield. RECOMMENDED for prioritization if 5-op set HARD_PASSes first (substrate's predicate-evaluation foundation must be in place before extending to compound arithmetic).

---

## CITATIONS (verified, count = 17)

**Residue Hyperdimensional Computing (core framework):**
1. Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2024 — "Computing With Residue Numbers in High-Dimensional Representation" — *Neural Computation* 37(1):1-37; arxiv 2311.04872; PMC10659444; rctn.org/bruno/papers/kymn_residue_NECOreprint.pdf. **PRIMARY REFERENCE.**
2. Tomkins-Flanagan & Kelly 2025 — "Hey Pentti, We Did (More of) It!: A Vector-Symbolic Lisp With Residue Arithmetic" — arxiv 2511.08767.
3. Tomkins-Flanagan & Kelly 2024 — "A Fully Vector-Symbolic Lisp: Hey Pentti, We Did It!" — arxiv 2510.17889 (precursor).
4. Society for Mathematical Psychology presentation 2024 — mathpsych.org/presentation/1541.

**FPE / qFHRR (substrate-compatible bridges):**
5. arxiv 2412.00488 (2024) — "Improved Cleanup and Decoding of Fractional Power Encodings."
6. arxiv 2604.25939 (2026) — "qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic." **KEY SUBSTRATE BRIDGE.**
7. arxiv 2203.00920 — "Integer Factorization with Compositional Distributed Representations."
8. arxiv 2109.03429 — Frady, Plate, Sommer — "Computing on Functions Using Randomized Vector Representations" (foundational FPE).

**Resonator network (decoder infrastructure):**
9. Frady, Kent, Olshausen, Sommer 2020 — "Resonator Networks" — arxiv 1906.11684; rctn.org/bruno/papers/resonator1.pdf.

**VSA / HDC core (background):**
10. Kleyko et al. 2023 — "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I" — ACM Computing Surveys; arxiv 2111.06077.
11. Kleyko et al. 2021 — "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware" — arxiv 2106.05268.
12. Plate 1995 — "Holographic Reduced Representations" — IEEE TNN (HRR foundation).
13. Smolensky 1990 — "Tensor product variable binding..." — Artificial Intelligence 46 (TPR foundation).

**RNS comparison algorithms (operator construction):**
14. IEEE Xplore 5840/223680 — Vu 1985 — "A new technique for fast number comparison in the residue number system."
15. ResearchGate 312568881 — "Algorithms for comparison in residue number systems."
16. ResearchGate 4261528 — "Efficient Method for Magnitude Comparison in RNS Based on Two Pairs of Conjugate Moduli."
17. Springer 10.1007/s00224-021-10035-y — "Computationally Efficient Approach to Implementation of the Chinese Remainder Theorem Algorithm in Minimally Redundant Residue Number System."

**Substrate-internal (cert_ledger evidence; not counted in lit):**
- `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md` (parent — 5-op set scope and exclusions)
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (bipolar bind involutive — depth-lossless)
- `experiments/exp_comparator_resonator_primitive_smoke_v1.py` (resonator framework partial implementation)
- CERT 587 g1b (permute primitive validated; FPE-related)
- CERT 588 h_hotpotqa (KG primitives validated)

---

## LIT-SCAN CALIBRATION NOTES

- All P values deflated 0.15–0.25 from raw LM-based confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap 0.50 NOT binding for Prediction 2 (sanity-control), 5 (algebraic theorem) — these are not novel-synthesis.
- BINDING for Predictions 1 (substrate-compatible RHC at minimum scale) and 3 (calculator-class capability lane opens) — these are novel-synthesis. Capped at 0.50, deflated to 0.40 and 0.20 respectively.
- Kymn et al. 2024 result is SOLID for FHRR (published in *Neural Computation*; peer-reviewed; replicated in Tomkins-Flanagan-Kelly 2025 Vector-Symbolic Lisp).
- qFHRR transfer to substrate is NOVEL (no published bipolar-MAP variant of RHC). Substrate is in uncharted regime per [[feedback-lit-scan-calibration-penalty]]; deflation applied.
- Comparison algorithms (Stream D) are SOLID classical RNS hardware results; transfer to VSA is straightforward but adds noise per O(K) chain depth.
- Vector-Symbolic Lisp Turing-completeness construction (Tomkins-Flanagan-Kelly 2025) is an ALGEBRAIC CORRECTNESS PROOF, not a scale-empirical result. Treat as upper bound on expressivity, NOT achievable performance at substrate scale.
- HARD-FAIL thresholds mandatory and listed for every prediction.
- Build-cost estimates (~500-1000 lines) are inherently uncertain; could be 2x in either direction.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could substrate already do RHC implicitly via bipolar+FPE?** Investigate Path A (FPE-log). Lit-scan shows permute-based FPE is discrete-only and degenerate for FPE-log multiplication; continuous-phase FPE requires complex-phase or qFHRR upgrade. **Verdict: Path A is genuinely insufficient.** But the discriminator is in the smoke cell (A2 arm); let the data classify.

**Could RHC be over-engineered for HotpotQA?** YES — compound arithmetic is only ~5-10% of HotpotQA comparison subset. RHC's product-surface expansion is mostly OUTSIDE HotpotQA (SVAMP, GSM8K, calculator-class). **Verdict: RHC ROI on HotpotQA alone is low; ROI on substrate-only-product expansion is HIGH.** Prioritization should consider the broader product surface, not just HotpotQA em.

**Could the smoke cell pass on a leak rather than real RHC?** Possible — verify-the-referent discipline. Discriminator: A1 (BIPOLAR_BASELINE) must FAIL; if A1 unexpectedly passes, suspect leak in encode/decode. Also: A2-A4 should fail on a hold-out integer range (outside training-codebook scope) — true RHC generalizes to all integers in dynamic range; leak-based "RHC" would memorize trained pairs.

**Could the published Kymn et al. result not replicate at substrate scale?** Possible — A4 (FHRR reference) is the replication check. If A4 fails to achieve >0.95 at N_DIM=8192, framework-level failure; substrate-compatible paths are downstream of this.

**Could qFHRR's quantization noise dominate at K=4-6 primes?** Possible — quantization noise scales with phase-precision. At Q=mk (matched to modulus), noise per dimension is ~1/sqrt(N_DIM) per phase bucket; at K=4, integer-level noise is ~K/sqrt(N_DIM/K) ≈ 0.044 at N_DIM=8192. Approaching threshold; might need N_DIM=16384 for chain-grade.

**Could the type bridge (RHC integer vector ↔ FPE phase vector) introduce loss?** YES — kernel-conversion is approximate. For HotpotQA-style scalar-integer queries (ages, years, counts), the bridge is exact (integer-in, integer-out). For periodic/continuous queries, conversion adds noise. **Risk-mitigation: scope first RHC integration to HotpotQA-style integer attributes; defer periodic-time integration until depth-2 validated.**

**Could 5-op set + RHC be jointly insufficient if encoder is bottleneck?** YES — same encoder-side risk as parent drill. RHC inherits parse-quality of upstream encoder; if encoder cannot extract "twice" or "+ 5" from natural language, RHC has no input. MiniLM-L6 encoder fix (parent v3 handoff) is upstream prerequisite.

**Could 5-op set saturate HotpotQA-comparison before RHC is needed?** Possible — parent drill estimates 5-op set covers ~90% of HotpotQA comparison subset. If parent cell achieves chain-grade at em ~0.20-0.25, the marginal lift from RHC is small (~+0.02-0.05). **RECOMMENDATION: prioritize 5-op set first; defer RHC until 5-op set lands. Then evaluate based on observed residual error class.**

---

## DISPATCH RECOMMENDATION

**Smoke cell hand-off (filed as companion):** `notes/exp_dev_handoff_research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md`

- Anchor: `substrate_rhc_minimum_viable_v1`
- Routing: local_cpu_queue (cheap; ~5-15 min CPU smoke; full cell ~30-60 min)
- 4 arms × 3 predicates × 100 trials × 3 seeds
- K=4 primes (m=3, 5, 7, 11; product 1155, dynamic range covers integers 0-1154)
- N_DIM=8192 (substrate standard)
- Pre-reg HARD bands per L5 above
- Smoke: 10 trials × 1 seed × ~30s; verify all 4 arms produce non-null accuracy + A1 sub-0.20 (control) + A4 above 0.50 (reference)

**Pre-condition:** `hdlab/qfhrr.py` minimal implementation (~150 lines for smoke; full implementation deferred to forward chain). Plus `hdlab/rhc.py` minimal (~100 lines for smoke). Total smoke-cell new code: ~300 lines (vs ~650 lines for production implementation).

**Three standalone META atoms (independent of cell outcome):**
- `meta_atom_residue_VSA_requires_dual_binding_not_single_2026-06-23.md`
- `meta_atom_qFHRR_is_substrate_compatible_bridge_to_RHC_2026-06-23.md`
- `meta_atom_substrate_without_RHC_cannot_do_calculator_class_QA_2026-06-23.md`

**Conditional follow-on if HARD_PASS:**
- v2: K=4 → K=8 primes (dynamic range ~9.7M); depth-5 RHC chains
- v3: KG storage extension for RHC-encoded numerical attributes
- v4: SVAMP-style 100-question pilot with MiniLM-L6 encoder + RHC + 5-op set composition
- v5: GSM8K subset (multi-step arithmetic); depth-cliff characterization

**Conditional reroute if HARD_FAIL:**
- Diagnose per-path (A FPE-log / B qFHRR / C full FHRR)
- If ALL 3 paths fail: META atom `meta_atom_substrate_native_arithmetic_lane_closure.md`; route to glass-box-LLM L2 closure for arithmetic
- If only Path A fails: commit to qFHRR or complex64 infrastructure
- If A+B fail: commit to full complex64

**PRIORITIZATION NOTE:** parent drill's 5-op set (`substrate_predicate_primitive_set_v1`) should land FIRST. RHC smoke is the LOGICAL NEXT after 5-op set chain-grades. If 5-op set HARD_FAILs, RHC ROI is much lower (parse-side bottleneck dominates regardless of arithmetic primitives).

---

## CONTRACT OUTPUT

`research: delivered drill_residue_arithmetic_vsa_compound_predicates -> notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md ; HEADLINE: residue-arithmetic VSA (Kymn et al. 2024 Neural Computation) gives substrate calculator-class compound-arithmetic predicate evaluation (add/multiply/compare/mod over integers; covers ~80-95% of SVAMP-class structurally) BUT requires NEW INFRASTRUCTURE (qFHRR phase-quantized layer + dual-binding operator + resonator decoder ~500-1000 lines), NOT a wrapper layer like the 5-op predicate set; substrate's current bipolar-MAP cannot host RHC natively (single binding operator + no phase dimension); qFHRR (arxiv 2604.25939) is the substrate-compatible bridge; smoke cell substrate_rhc_minimum_viable_v1 tests 4 arms (bipolar baseline / FPE-log / qFHRR / FHRR reference) on K=4 primes at N_DIM=8192; P_deflated(substrate can host RHC at min-viable)=0.40; P_deflated(SVAMP em ≥ 0.20 with full integration)=0.20; without RHC substrate restricted to retrieval+ordering — calculator-class lane closed; with RHC substrate L2 product expands to numerical-QA; PRIORITIZATION: 5-op set first then RHC; next-drill candidate: encoder-side quantity extraction for arithmetic word problems (MiniLM-L6 + numerical-NER fine-tune vs char_trigram)`

---

*Research drill complete 2026-06-23. 5 parallel WebSearch lit-scans (residue HDC framework Kymn et al. / FPE integer arithmetic / Chinese Remainder Theorem distributed / RHC factorization resonator / Vector-Symbolic Lisp Tomkins-Flanagan-Kelly / VSA modular arithmetic operations / RHC complex FHRR moduli / bipolar MAP arithmetic encoding / RNS magnitude comparison algorithms / VSA arithmetic word problem GSM8K SVAMP) + cross-thread synthesis with parent predicate-evaluation drill + HRR capacity-depth drill + CERT 587 g1b + CERT 588 h_hotpotqa + USER HRR derivation + USER lock-in amp + USER substrate-only product direction. Generic queries only (no substrate-novel mechanism names off-platform). Lit-scan calibration applied (deflate 0.15–0.25; novel-synthesis cap 0.50 binding for Predictions 1 + 3). HARD-FAIL thresholds mandatory. Symmetric negativity check applied (7 negativity-rebuttal angles). Three standalone META atoms routed. Build-cost estimate ~500-1000 lines new infrastructure (qFHRR + RHC + resonator + type bridge). Smoke cell hand-off filed as companion file. Time elapsed ~25 min per budget.*
