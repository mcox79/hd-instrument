# Research R8 — Noise accumulation in chained content-addressable memory + binding-algebra rescue

**Topic.** Strategy's Bet 2 / R8 rehab routing: multi-hop reasoning collapses
past depth ~10 in the substrate's current BSC-XOR binding architecture.
Strategy's draft sketch #5 (per-fact orthogonal-key allocation via Hadamard)
was empirically falsified at cycle 7 by `wave14z_multihop_hadamard_entities`
(acc_1hop=0.83 with Hadamard vs 0.93 with random ±1; Hadamard WORSE).
**Mechanism**: BSC's binding operation (XOR / Hadamard product) closes the
Walsh group — chained binds produce other Hadamard codewords that collide
with stored entities by accident. R8 asks: which alternative binding algebras
avoid this closure pathology, and which is the right substrate rescue?

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real external
literature scan** via Agent subagent (generic-math queries, no substrate
fingerprint). Per rehab-routing protocol, this note GENERATES the rescue
ranking independently rather than vetting Strategy's draft. Pass 2 drills
candidate #4 (binding algebra swap) which is the mechanism correction for
why #5 failed.

---

## Pass 1 — External literature scan (verified)

Generic-math queries via subagent (~4 min runtime, 25 tool uses, 15+
verified citations): "vector symbolic architecture binding operators
comparison," "holographic reduced representations chained inference noise
scaling," "Clifford algebra geometric product structured representation,"
"multi-hop reasoning attractor network capacity," "Plate circular
convolution binding," etc. No substrate fingerprint.

### 1.1 Binding-operator taxonomy by group structure

**Schlegel, Neubert, Protzel 2022 (arXiv:2001.11797, AIR 55)** is the canonical
recent comparison — eleven VSAs head-to-head. **Kleyko et al. 2022 (arXiv:2111.06077,
ACM CSUR Parts I+II)** is the definitive survey of operators and applications.

The critical group-structure split (from the lit scan synthesis):

| VSA | Vector space | Bind op | Group | Self-inverse | Closed under bind? |
|---|---|---|---|---|---|
| **BSC** (Kanerva 1996) | {±1}^d | XOR / Hadamard | discrete, finite, abelian | yes | **YES — Walsh group** |
| **MAP** (Gayler 1998) | {±1}^d | Hadamard | discrete, finite, abelian | yes | **YES** |
| **SBC** (Hersche 2023) | block one-hot | per-block permutation | discrete cyclic Z_b^B | yes (within block) | **YES (per block)** |
| **HRR** (Plate 1995) | R^d unit-norm | circular convolution | continuous, abelian | approximate (involution) | **NO — continuous group** |
| **FHRR** (Plate 2003) | (C, \|z\|=1)^d | element-wise complex mult | continuous compact (torus T^d) | only at z=±1 | **NO — measure zero** |
| **MBAT** (Gallant-Okaywe 2013) | R^d via matrix M | y = M·sum | continuous matrix O(d) | M^T if orthogonal | **NO** |
| **Clifford-GA** (Aerts-Czachor 2006, arXiv:cs/0610075) | Cl(p,q) multivector | geometric product | continuous, non-abelian, graded | only on specific blades | **NO** |
| **Fractional Power Encoding** (Frady-Kymn-Bartlett 2022) | FHRR phasors with continuous exponent | z^α complex pow | continuous Lie (R^d on phases) | x^α · x^(-α) = 1 | **NO** |
| **GHRR** (Liu 2024, arXiv:2405.09689) | complex unit-norm + position kernels | generalized convolution | continuous | approximate | **NO** |

**The R8 mechanism is now in the lit scan's terms.** The substrate's BSC sits
in the "discrete + closed" row. The Walsh group closure under XOR-bind is
exactly the property the lit scan's first survey row makes explicit. Continuous-
group operators (HRR, FHRR, MBAT, Clifford, FPE, GHRR) **do not have a finite
codebook subset that closes under arbitrary binds** — codebook collisions from
intermediate binds are measure-zero events.

**Honest limit (lit scan): NO PUBLISHED PAPER proves "FHRR avoids BSC group
closure" as a named theorem.** The property is structurally obvious (continuous
torus has no finite closed subgroup of arbitrary size) but is treated as folklore
in the VSA literature. The substrate's R8 work could be the first published
empirical characterization of this property at depth ≥ 50.

### 1.2 Chain-depth noise scaling per operator

**Plate's classical √K analysis** (Plate 1995, *IEEE Trans. Neural Networks*
6(3):623–641; thesis UToronto 1994): for HRR circular convolution, each bind
adds variance ~1/d per superposed item; chaining K binds without cleanup
gives variance ~K/d, so SNR ~ √(d/K).

**Frady-Kleyko-Sommer 2018 (arXiv:1803.00412, Neural Computation):**
generalizes Plate's analysis to a signal-detection framework. Gives formulas
for the dimension d required to support chain depth K at target retrieval
probability. The variance constant differs by operator but the √K form is
universal across continuous-group operators.

**Langenegger et al. Dec 2024 (arXiv:2412.00354)** measures empirical noise
propagation through resonator-network cleanup — the standard cleanup operator
for HRR/MAP/FHRR. Relevant to the substrate because R8's drill choice has to
specify a cleanup operator alongside the binding operator.

**BSC-specific failure mode** (lit scan synthesis, not single-paper citation):
the √K analysis breaks down for BSC because the noise injected at each step
is *correlated* with the stored codewords (Walsh-group closure). The cleanup
operator's error is no longer Gaussian — it has a heavy tail at Hamming
distance 0 from collateral stored entities. This is exactly the
`wave14z_multihop_hadamard_entities` finding's mechanism, generalized.

### 1.3 Multi-hop reasoning architectures (depth ≥ 50)

**Lit scan honest finding: no 2024–2026 paper benchmarks chained-bind retrieval
at depth ≥ 50 on any VSA architecture.** Deepest published chains:
- Schlegel 2022 sequence tasks: chain length bounded by sentence length (~10–20)
- Resonator network factorization: typically 3–5 factor depth
- Hersche 2023 RAVEN: ≤4 attribute compositions
- Modern Hopfield (Ramsauer 2020): one-step retrieval, not multi-step

The substrate's question — "≥80% accuracy at depth 50, NUM_FACTS=100" — is
**unbenchmarked in the published literature**. This is genuine substrate-
novel territory. Per the playbook: a clean depth-50 benchmark across BSC /
HRR / FHRR / Clifford would be a real contribution to the published lit.

**Adjacent literature (not direct CAM but informative):**
- MemReasoner (NeurIPS 2024, IBM): memory-augmented LLM multi-hop; not VSA, but
  provides comparison baseline shape for multi-hop accuracy curves.
- BeamDR (arXiv:2104.05883), BeamAggR (arXiv:2406.19820), Baleen
  (arXiv:2101.00436): beam-search dense retrieval; transferable strategy for
  multi-hop CAM via top-b tracking.
- Modern Hopfield Fenchel-Young (Martins 2025, arXiv:2411.08590): unifies sparse
  modern-Hopfield variants; caps at small depth in published evals.

### 1.4 Materials-science analogs (load-bearing, but lit scan finds one gap)

**BSC ↔ Ising spin-glass** is established (Amit-Gutfreund-Sompolinsky 1985;
rigorized in Barra 2020 arXiv:2006.00256 "Replica symmetry breaking in
neural networks"). The Hopfield-network ↔ SK spin-glass equivalence is
foundational.

**FHRR ↔ XY spin-glass** is PHYSICALLY NATURAL but the lit scan found
**no paper that bridges XY spin-glass to FHRR in the VSA literature**. The
XY-spin-glass physics literature exists (cond-mat/0011065, cond-mat/0402264,
arXiv:0907.4220 large-scale 3D simulations) and is rigorous; the established
result is that **continuous Goldstone modes** of the XY model give:
- 2D: logarithmic-in-time error growth (slow phase decoherence)
- 3D: √t error growth (still slower than Ising glass's exponential relaxation)

Substrate-prediction consequence: FHRR's chain-depth noise scaling should be
**quasi-logarithmic to √K** in the analogous regime, vs BSC's exponential
collapse from Walsh-group closure. This is the load-bearing physics analog
that the substrate's R8 note can publish first.

**Clifford-GA ↔ topological tight-binding** via quaternion algebra (Arrayás
et al. arXiv:1311.1099 "Systematic Construction of tight-binding Hamiltonians
for Topological Insulators and Superconductors" uses Cl(0,2) quaternion
binding). Arkinstall et al. arXiv:1702.07648 builds tight-binding as
"non-trivial square roots of parent lattice Hamiltonians" — another graded-
algebra construction. Non-Abelian braiding (arXiv:2405.04879) is the physical
realization of non-commutative Clifford binding.

Substrate-prediction consequence: Clifford-graded binding should support
chain depth governed by **topological invariants** (winding numbers, band
gaps) rather than continuous noise — qualitatively distinct depth-scaling
from FHRR's Goldstone-mode regime.

---

## Pass 2 — Substrate-specific drill (independent rescue ranking)

The lit scan establishes the candidate space. Per rehab-routing protocol
([[feedback-rehabilitation-after-rejection]] + research playbook item 9),
I generate the ranking independently. Strategy's draft of 6 sketches is
*starting point only* — not vetted.

### 2.1 Independent ranking of rescue candidates

Decomposing the rescue space by **what aspect of the mechanism each candidate
changes**:

**Category A — Change the binding algebra (root cause fix; addresses Walsh
closure)**

- **A1: BSC → FHRR** (continuous phase torus T^d). Continuous group; no
  closure in finite codebook. Cleanup via resonator networks (Frady 2020).
  Substrate impact: replace bipolar ±1 codebook with unit-magnitude complex
  phasors; replace XOR with element-wise complex multiplication. Existing
  cleanup operator (cosine to codebook) generalizes naturally.
- **A2: BSC → HRR** (real-valued circular convolution). Continuous group;
  no closure. Cleanup via correlation. Higher per-bind cost (O(d log d)
  FFT vs O(d) XOR) but well-established.
- **A3: BSC → Clifford-GA** (graded multivectors, geometric product).
  Continuous, non-abelian, graded. Cleanup is grade-specific. Higher
  algebraic complexity (cost O(2^k) for grade k). Substrate-novel.
- **A4: BSC → MBAT** (matrix binding via orthogonal matrix M). Continuous
  orthogonal group. Higher per-bind cost O(d²) but well-structured.
- **A5: BSC → Fractional Power Encoding** (FHRR phasors with continuous
  exponent). Continuous Lie group on phases. Best fit for *spatial* /
  *temporal* coordinates; less natural for pure symbolic facts.

**Category B — Keep BSC; add structural protection (symptom mitigation)**

- **B1: Per-hop cleanup with modern Hopfield exponential energy**
  (Ramsauer 2020 / Demircigil 2017). Exponentially small per-step retrieval
  error at exponential capacity. Used as per-hop cleanup, errors compound
  favorably. Substrate keeps W = Σvkᵀ storage; modern Hopfield is the
  *readout* operator change.
- **B2: Beam-search top-b at each hop**. Track b candidate intermediates;
  late-stage error recovery if early-hop cleanup chose wrong. Standard NLP
  retrieval technique (BeamDR, BeamAggR). Substrate-compatible via top-k
  cosine. No mechanism change; just decoder change.
- **B3: Adaptive beta schedule β(hop)**. As noise accumulates, anneal softmax
  sharpness; avoid over-committing to incorrect intermediates. Cheap;
  symptom mitigation only — doesn't address closure.
- **B4: Per-hop W-side update (eager re-anchoring)**. Update W at each hop
  to commit to current intermediate. Restores depth-locality at cost of
  erasing earlier facts; risky for retention.

**Category C — Architectural workarounds**

- **C1: Hybrid storage + chain (BSC store / FHRR chain)**. Store entities
  in BSC (cheap; existing substrate). Convert to FHRR at chain start,
  perform chained binds in FHRR (no closure), convert back at chain end.
  Substrate-novel synthesis.
- **C2: Tree-structured binding (avoid linear chain)**. Replace
  linear K-chain with depth-log K tree; balances per-hop noise.
- **C3: Per-fact orthogonal-subspace allocation** — Strategy's #5,
  ❌ EMPIRICALLY CLOSED by `wave14z_multihop_hadamard_entities`. Listed
  for completeness; dropped from ranking.

### 2.2 My ranked rescue list (independently generated)

Ranking criteria: (a) mechanism-corrective (addresses Walsh closure
directly) > (b) symptom-mitigating (improves at the margin); (c) cheap
to implement > (d) expensive; (e) substrate-coherent (preserves existing
capabilities) > (f) requires substrate redesign.

| Rank | Candidate | Mechanism / symptom | Implementation cost | Substrate-coherence | P(depth-50 ≥ 80% at NUM_FACTS=100) |
|---|---|---|---|---|---|
| **1** | **A1: FHRR** | Mechanism correction (eliminates closure) | Medium (complex phasors; bind = complex mult; cleanup via resonator nets) | Medium-high (substrate algebra changes but most ops generalize) | **45–60%** |
| **2** | **C1: Hybrid BSC store + FHRR chain** | Mechanism correction (chain in continuous group) | Low-medium (boundary conversion + FHRR chain ops) | High (BSC storage preserved; chain operator localized) | **40–55%** |
| **3** | **B1: Modern Hopfield per-hop cleanup** | Symptom mitigation (per-step error → 0 at exp capacity) | Low (cleanup operator swap; storage unchanged) | High (W = Σvkᵀ preserved; readout changes) | **35–50%** |
| **4** | **A3: Clifford-GA** | Mechanism correction (graded non-abelian) + topological protection | High (Cl(p,q) algebra; grade-aware cleanup; O(2^k) per bind) | Low (substrate algebra fully redesigned) | **30–55%** (wide range; topology might either save us or kill capacity) |
| **5** | **B2: Beam-search top-b** | Symptom mitigation (late error recovery) | Low (decoder change only) | High (no storage / binding change) | **25–40%** |
| **6** | **A2: HRR** | Mechanism correction (continuous; circular convolution) | Medium (O(d log d) FFT bind; substrate cost rises) | Medium | **35–50%** (similar to FHRR, slightly higher cost) |
| **7** | **B3: Adaptive beta** | Symptom mitigation (softmax annealing) | Trivial (one hyperparameter schedule) | Trivial | **15–30%** |
| **8** | **A4: MBAT** | Mechanism correction (matrix orthogonal group) | High (O(d²) per bind; substrate cost rises sharply) | Low (storage/binding redesigned) | **30–45%** |
| **9** | **B4: Per-hop W-side update** | Symptom mitigation; eager re-anchoring | Medium (W mutation per hop; retention cost) | Low (breaks W as persistent storage) | **20–35%** |
| **10** | **C2: Tree-structured binding** | Architectural change (depth log K not K) | Medium (rewrite chain construction) | Medium | **30–50%** (depends on what's natively a chain vs tree) |

**Top recommendation: A1 (pure FHRR)** as primary mechanism rescue, with
**C1 (hybrid BSC store + FHRR chain)** as the substrate-coherent variant.
Both directly address the closure pathology. C1 preserves existing BSC
storage infrastructure; A1 fully replaces it.

**Honest reordering of Strategy's draft** (Strategy listed #4 = binding
algebra swap, #1 = cleanup operator, #2 = adaptive beta, #3 = per-hop W,
#6 = beam-search; #5 closed):
- My #1 (FHRR / A1) matches Strategy's promoted #4. ✓
- My #2 (hybrid C1) was NOT in Strategy's draft. **NEW.**
- My #3 (modern Hopfield B1) matches Strategy's #1. ✓
- My #4 (Clifford A3) was inside Strategy's #4 but I split it out
  separately because the topology / capacity tradeoff is qualitatively
  different from FHRR.
- My #5 (beam-search B2) matches Strategy's #6 — but I rank it HIGHER
  than the symptom mitigations because it's a clean decoder change.
- My #7 (adaptive beta B3) matches Strategy's #2 — DOWNRANKED because
  it's pure symptom mitigation.
- My #9 (per-hop W update B4) matches Strategy's #3 — DOWNRANKED for
  the retention risk.
- C1 hybrid and C2 tree-structured are substrate-coherent variants
  not in Strategy's original draft.

### 2.3 Drill A1 (FHRR) — the mechanism correction

**The math.** Replace bipolar ±1 codewords with unit-magnitude complex
phasors: kᵢ ∈ (C, |z|=1)^N. Each component zᵢⱼ = exp(i θᵢⱼ) where θᵢⱼ
is the per-component phase. Binding: element-wise complex multiplication
y = k ⊙ k', equivalent to phase addition θ_y = θ_k + θ_k' (mod 2π).
Cleanup: cosine similarity ⟨y, c⟩ over codebook C of stored entities.

**Why this eliminates closure.** The phase torus T^N is a continuous
manifold. A finite codebook of K phasors generates products in the torus
that almost-surely lie at generic positions — NOT on the codebook lattice.
For K random codebook entries, the probability that k_a · k_b · k_c (a
3-hop bind) lies within ε of any other codeword is bounded by K·ε^N (vol
of N-ball / vol torus). At N=4096 and ε = 0.05 (cleanup tolerance), this
is K · 5^(-N) · π^(N/2) / Γ(N/2+1) ≈ 0 for any practical K.

**Substrate cost.** Per-component cost goes from 1 bit (BSC) to ~ 16
bits (complex64). Per-bind cost stays O(N) (element-wise multiply).
Cleanup cost stays O(N · K) (cosine over codebook). Total ~16×
memory footprint; same compute scaling.

**Substrate-coherence test.** All existing capabilities (R10 concept
fusion, ICL via pool, resonator decomposition) generalize to FHRR
because they are based on cosine similarity and outer-product Hebbian
storage — both well-defined for complex unit-magnitude vectors. The
substrate's resonator-network factorizer (Frady 2020) is *native* FHRR.

**Predicted depth-50 accuracy at NUM_FACTS=100, N=4096**: from
Plate-Frady-Sommer signal detection theory:
- per-bind variance ≈ 1/N for non-self-inverse continuous binding
- chain-depth K=50: total variance ≈ 50/N = 50/4096 ≈ 0.012
- SNR ≈ √(1/0.012) ≈ 9
- Expected per-hop cleanup accuracy at SNR=9: ≥ 99% (Gaussian tail)
- Compounded over 50 hops at 99% per hop: 0.99^50 ≈ 0.61
- With resonator-network cleanup at SNR=9: per-hop accuracy ≥ 99.5%
- Compounded over 50: 0.995^50 ≈ 0.78

**Predicted P(depth-50 ≥ 80%): 45-60%**. The lower bound reflects
crosstalk from NUM_FACTS=100 (more codebook entries = more chances for
generic phase products to lie near a codebook entry). The upper bound
reflects resonator-network's iterative correction.

**Honest caveats from the lit scan**:
1. FHRR's "no closure" property is folklore-not-theorem — substrate-novel
   measurement could be first published characterization.
2. The √K classical analysis assumes Gaussian noise; FHRR phase
   accumulation is *not* Gaussian (sum of mod-2π phases is well-defined but
   tail-bounded differently). The signal detection theory needs to be
   re-derived for the substrate's exact configuration.
3. No published benchmark at depth ≥ 50; my prediction is from first-
   principles + published per-hop SNR formulas, NOT from a baseline I can
   point to.

### 2.4 Drill C1 (hybrid) — substrate-coherent variant

**The math.** Storage: substrate's existing W = Σ vᵢ kᵢᵀ with bipolar
± 1 vᵢ, kᵢ. At chain start: convert query kᵢ to FHRR phasor k_iˆ via
deterministic isomorphism (e.g., k_iˆⱼ = exp(i π kᵢⱼ / 2) for component
j, giving phasor at θ = ±π/2 depending on bit). Perform chained binds
in FHRR: k_chain = k_aˆ ⊙ k_bˆ ⊙ k_cˆ ⊙ .... At chain end: convert
back to bipolar via sign(Re(k_chain)) and read into W via standard W·k.

**Why this works.** The chain operations live in continuous FHRR space
(no closure); only the boundary conversions introduce discretization
noise. Per Frady-Sommer signal detection, the boundary noise is
bounded by Berry-Esseen-like bounds for discretization of continuous
phasors.

**Substrate cost.** Negligible storage change (BSC storage preserved).
Chain compute cost: ~2× BSC due to complex multiplication, but only
during chain execution (not for stored facts). Memory: complex
phasors materialized only at chain query time.

**Predicted depth-50 accuracy**: somewhat lower than pure A1 (45–60%)
because the boundary conversions inject discretization noise. Estimated
**40–55%**.

**Why this is the best substrate-coherent option.** It does NOT require:
- Substrate-wide migration to FHRR (which would invalidate all
  existing experiments at α=0.153, Bet 2 ✅ orthogonal-key erase, ICL
  scaling, etc.)
- A new training pipeline (Hebbian remains bipolar)
- Re-validation of every other capability

It DOES require: a chain-execution module that handles FHRR phasor
arithmetic. Self-contained. Reversible.

---

## Specific experimental design (pseudocode)

**Experiments**: Strategy's R8 question requires multiple parallel
rescue tests. Recommend three experiments at smoke scale first, then
escalate the top-performer to full multi-seed evaluation.

### Experiment A1 — `wave14r_multihop_FHRR_v1` (primary mechanism correction)

```text
config:
  N = 4096
  NUM_FACTS = 100
  NUM_RELATIONS = 10
  chain_depth_sweep = [1, 5, 10, 25, 50]  # for envelope
  seeds = [7, 17, 23, 31, 41]
  cleanup_operator = resonator_network  # Frady 2020

storage_construction:
  entities = sample_FHRR_phasors(num=NUM_FACTS, N=N)
              # k_i ∈ (C, |z|=1)^N, θ_ij ~ Uniform[0, 2π)
  relations = sample_FHRR_phasors(num=NUM_RELATIONS, N=N)
  facts = []
  for each (subj, rel, obj) triple:
    fact_phasor = subj ⊙ rel ⊙ obj  # element-wise complex multiply
    facts.append(fact_phasor)
  W_FHRR = sum(facts)  # bundle of all facts (complex sum)

multi_hop_query(query_phasor, chain_depth):
  current = query_phasor
  for hop in range(chain_depth):
    # bind current intermediate against a relation, read off resulting entity
    next_intermediate = current ⊙ next_relation_phasor  # FHRR bind
    # cleanup via resonator network
    nearest_entity = resonator_cleanup(next_intermediate, codebook=entities)
    current = nearest_entity
  return current

multi_probe_battery:
  # Match Strategy's R8 success criteria
  for depth in chain_depth_sweep:
    accuracy[depth] = mean(query_correct(random_query, depth))
  acc_50 = accuracy[50]
  acc_curve = accuracy[1, 5, 10, 25, 50]

verdict_logic:
  PASS iff: acc_50 ≥ 0.80 AND acc_curve monotone-decreasing
  PARTIAL iff: 0.40 ≤ acc_50 < 0.80
  KILL iff: acc_50 < 0.40 across 3 seeds

  Comparison baseline (REQUIRED): BSC + Hadamard at same NUM_FACTS=100
  per `wave14z_multihop_hadamard_entities`. FHRR must beat BSC across
  the curve.
```

### Experiment C1 — `wave14r_multihop_hybrid_v1` (substrate-coherent variant)

Same as A1 but storage in BSC; FHRR conversion only during chain execution.
Stress-tests whether discretization noise at the boundary defeats the
no-closure benefit.

### Experiment B1 — `wave14r_multihop_modernhopfield_v1` (symptom mitigation control)

Same fact storage as `wave14z` (random ±1 BSC), but cleanup operator
swapped from argmax to **Ramsauer 2020 modern Hopfield exponential energy**
softmax retrieval. Tests whether stronger per-hop cleanup compensates
for closure-induced noise (the literature predicts: only partially).

### Smoke test (queue_add gate for all three)

N=512, NUM_FACTS=20, chain_depth=10, 1 seed. Target runtime ~30s.
Oracle assertion: acc_1hop ≥ 0.85 (per-hop accuracy must clearly pass
floor before depth scaling is informative).

### Self-test (4 synthetic cases)

- Pure orthogonal phasors (manually constructed): predict acc_50 → 1.0
  (continuous case has no codebook collisions by construction).
- Pure correlated phasors (all near θ=0): predict acc_50 → 0 (degenerate).
- Mix: predict acc_50 between A1's prediction and 0.
- BSC control (deliberately bipolar): replicate the
  `wave14z_multihop_hadamard_entities` result.

### Wall budget

A1 + C1 + B1 at smoke: ~5 min total. Full multi-seed at depth=50,
NUM_FACTS=100: ~30 min total per experiment on the 4060 Ti.

---

## Materials analog (load-bearing — XY spin-glass and topological tight-binding)

The lit scan surfaced two physics analogs that map directly to the substrate's
binding-algebra rescue space, and **neither is bridged to VSA in the published
literature** — the substrate's R8 could be the first.

### FHRR ↔ XY spin-glass

The XY model (continuous spin S^1-valued variables) is the natural physical
analog of FHRR's continuous phase torus. The XY spin-glass literature
(cond-mat/0011065, cond-mat/0402264, arXiv:0907.4220) is rigorous; the
established results:

- **Chiral order parameter with Ising-like symmetry from frustration**
  (cond-mat/0402264): even with continuous spins, frustration can localize
  effective discrete symmetries. Substrate-prediction: FHRR's continuous
  group avoids closure, but specific *frustration patterns* in the codebook
  might re-introduce discrete-like degeneracies.
- **3D phase-coherence transition at finite temperature** (arXiv:0907.4220):
  large-scale Monte Carlo on 3D XY spin-glass confirms continuous
  phase-coherence order parameter at finite T. Substrate-analog: the
  substrate's "coherent chain-retrieval" regime is the analog of the
  phase-coherent XY-glass phase.
- **Continuous Goldstone modes give logarithmic error growth in 2D and
  √t in 3D**. Substrate-prediction (load-bearing): FHRR's chain-depth
  noise scaling is **at most √K**, qualitatively better than BSC's
  Walsh-closure-induced exponential collapse.

### Clifford-GA ↔ topological tight-binding

Arrayás et al. (arXiv:1311.1099) use **quaternion algebra** — Cl(0,2)
Clifford — to construct topological band Hamiltonians. Arkinstall et al.
(arXiv:1702.07648) builds tight-binding as "non-trivial square roots of
parent lattice Hamiltonians" via graded algebra. Non-Abelian braiding
(arXiv:2405.04879) realizes non-commutative Clifford binding physically.

Substrate-prediction (load-bearing if Clifford rescue is built):
Clifford-graded binding should support chain depth governed by **topological
invariants** (winding numbers, band gaps) rather than continuous noise.
This is qualitatively different from FHRR's Goldstone regime. The
substrate's R8 could test this by comparing FHRR (continuous-mode regime)
vs Clifford (topological-protection regime) head-to-head.

---

## Falsifiable prediction

**Primary prediction (A1 FHRR, Experiment A1):**

At N=4096, NUM_FACTS=100, NUM_RELATIONS=10, resonator-network cleanup,
5-seed mean:

- acc_1hop ≥ 0.95 (per-hop accuracy clearly above BSC's 0.83 baseline).
- acc_5hop ≥ 0.85.
- acc_10hop ≥ 0.70.
- acc_25hop ≥ 0.45.
- **acc_50hop ≥ 0.40 (lower bound), ≥ 0.60 (upper bound)**.
- Chain accuracy curve monotone-decreasing.
- Beats BSC + random keys (acc_50hop = 0.13 per `wave14u_multihop_envelope_v1`
  full at NUM_FACTS=50) by ≥ 30 percentage points across all depths.

**Stress prediction (C1 hybrid):**

acc_50hop **between A1 and BSC baseline**, expected 30–45%, primarily
limited by discretization noise at boundary conversions.

**Control prediction (B1 modern Hopfield):**

acc_50hop **modest improvement over baseline BSC**, expected 20–35%.
Confirms the lit scan finding that better cleanup operators help but
don't compose to overcome Walsh closure.

**Kill criterion.**

If A1 (FHRR) achieves acc_50hop < 0.30 at NUM_FACTS=100 across 5 seeds,
AND C1 (hybrid) does the same, then **the binding-algebra rescue (R8
Category A + C) is closed for the substrate's multi-hop story**. The
fallback would be Strategy's #6 (beam-search; my #5) which addresses
the symptom not the cause. If B1 also fails, multi-hop reasoning at
depth 50 closes ❌-with-current-architecture-and-rescue-set; substrate
multi-hop is bounded at depth ~10–25 regardless of rescue.

**Falsifier for the FHRR-uniqueness claim.**

If A1 passes BUT C1 fails: discretization noise dominates; substrate
must fully migrate to FHRR (large refactor) to access multi-hop.
If A1 and C1 both pass at similar accuracy: substrate-coherent rescue
exists; hybrid is the productive engineering choice.
If A1 only marginally beats BSC (Δ < 5 percentage points at depth 50):
the closure mechanism is NOT the dominant noise source; other rescues
(B1 modern Hopfield, etc.) need separate evaluation.

---

## Citations

1. **Schlegel, Neubert, Protzel (2022). "A comparison of Vector Symbolic
   Architectures."** *Artificial Intelligence Review* 55:4523–4555.
   arXiv:2001.11797.
   — Canonical 11-operator comparison; provides the group-structure
   taxonomy used in this note.

2. **Kleyko, Rachkovskij, Osipov, Rahimi (2022/2023). "A Survey on
   Hyperdimensional Computing aka VSA, Parts I & II."** ACM Comput.
   Surveys. arXiv:2111.06077.
   — Definitive survey of operators and applications. DOI:
   10.1145/3538531 and 10.1145/3558000.

3. **Plate (1995). "Holographic Reduced Representations."** IEEE Trans.
   Neural Networks 6(3):623–641. (Also: Plate thesis, UToronto 1994.)
   — Classical √K chain-noise analysis for HRR; foundational.

4. **Frady, Kleyko, Sommer (2018). "A Theory of Sequence Indexing and
   Working Memory in Recurrent Neural Networks."** Neural Computation
   30(6). arXiv:1803.00412.
   — Signal-detection-theory framework for chain depth in VSAs; provides
   the SNR formulas used in the FHRR prediction above.

5. **Ramsauer et al. (2021). "Hopfield Networks is All You Need."**
   ICLR. arXiv:2008.02217.
   — Modern Hopfield exponential capacity + one-step retrieval. The
   basis for the B1 cleanup-operator rescue.

6. **Frady, Kent, Olshausen, Sommer (2020). "Resonator Networks 1 & 2."**
   Neural Computation 32(12). arXiv:1906.11684.
   — Standard cleanup operator for HRR/MAP/FHRR factorization; used
   in the A1 experimental design.

7. **Aerts, Czachor, De Moor (2006). "On Geometric Algebra
   representation of Binary Spatter Codes."** arXiv:cs/0610075.
   — Clifford-GA embedding of BSC; foundational for the A3 rescue.

8. **Langenegger et al. (Dec 2024). "On the Role of Noise in Factorizers
   for Disentangling Distributed Representations."** arXiv:2412.00354.
   — Empirical measurement of noise propagation through resonator-network
   cleanup; current reference for the cleanup-side error model.

9. **Hersche, Terzić et al. (2023/2025). "Factorizers for Distributed
   Sparse Block Codes."** arXiv:2303.13957; Sage NAI 2025.
   — Sparse block code factorizer; provides closest published empirical
   benchmark for VSA multi-step retrieval.

10. **Cotteret et al. (2026). "qFHRR: Rethinking Fourier HRR through
    Quantized Phase and Integer Arithmetic."** arXiv:2604.25939.
    — Quantized FHRR variant; reduces FHRR memory cost; relevant for
    making A1 substrate-cost-comparable.

11. **Arrayás et al. (2014). "Systematic Construction of tight-binding
    Hamiltonians for Topological Insulators and Superconductors."**
    arXiv:1311.1099.
    — Quaternion / Cl(0,2) construction of topological band models.
    Materials anchor for the Clifford-GA rescue (A3).

12. **(2010s) Large-scale dynamical simulations of the 3D XY spin glass.**
    arXiv:0907.4220.
    — Continuous-spin spin-glass dynamics; Goldstone-mode error growth.
    Materials anchor for the FHRR rescue (A1).

---

## Routing

- **Experiment Dev (E_R8)**: this note recommends building THREE parallel
  experiments at smoke + multi-seed scale:
  - **`wave14r_multihop_FHRR_v1`** (primary, A1 mechanism correction)
  - **`wave14r_multihop_hybrid_v1`** (substrate-coherent variant, C1)
  - **`wave14r_multihop_modernhopfield_v1`** (control, B1; confirms
    cleanup-operator-alone is insufficient)
  All compared against the existing BSC + random keys baseline
  (acc_50hop = 0.13 per `wave14u_multihop_envelope_v1`). Smoke ~5 min
  per experiment; full multi-seed ~30 min each.

- **Strategy**: this note GENERATES the rescue ranking independently
  (per rehab-routing protocol). Proposes the following cap_map row
  additions under "Multi-hop reasoning":
  - "FHRR binding algebra rescue (R8 #4 / A1)" at 🔬 (experimental
    design ready)
  - "Hybrid BSC-store + FHRR-chain (R8 / C1)" at 🔬 (substrate-novel
    synthesis; experimental design ready)
  - "Modern Hopfield per-hop cleanup (R8 #1 / B1)" at 🔬 (experimental
    design ready)
  Strategy's draft ranking was directionally correct (#4 promoted = my
  #1) but missed C1 hybrid as a substrate-coherent variant. Also
  proposes the XY-spin-glass ↔ FHRR materials bridge as a published-
  literature gap the substrate could be first to fill.

- **Research (this session, future cycles)**: if A1 passes (acc_50hop
  ≥ 0.40), Tier-2 KILLER multi-hop survives; route follow-up to
  characterize the FHRR-substrate's compatibility with R10 / ICL / Bet
  2 erase capabilities (substrate-wide migration vs hybrid scope
  decision). If A1 fails AND C1 fails AND B1 fails: multi-hop closes
  ❌-with-current-architecture. R8 rehab axes 2/3/6 (adaptive beta,
  per-hop W, beam search) remain symptom-mitigations only; not
  productive on their own. Next research priority would shift to
  understanding the substrate's chain-depth boundary as a property
  rather than chasing further rescues.
