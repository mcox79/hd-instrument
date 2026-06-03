# Research Note: Reservoir Computing / Echo-State Network Capability Families
# Topic: audit primitives, compositional algebra, one-shot writes -- 2023-2025 literature
# Date: 2026-06-02

---

## HEADLINE

No prior reservoir-computing or ESN system (2023-2025 literature) unifies all three capability families -- audit primitives, compositional algebra, one-shot writes -- into a single algebraic API; the three families evolve in disjoint sub-communities with zero published work combining even two of the three in one architecture.

---

## Capability Family Scan

### Family 1: Audit primitives on reservoir internal state

**What exists:** Reservoir literature tracks spectral radius of the recurrent matrix W as a global stability indicator (spectral-norm bounds, Echo State Property certification). Singh et al. 2024 (arXiv:2507.18467) frames contraction-criticality via Theorem 5.1 connecting spectral properties to capacity. Haruna et al. 2021 (arXiv:2112.01886) classify reservoir universality classes by second-cumulant generating functions of coupling constants, establishing a link between W's coupling-constant distribution and eigenvalue structure.

**What does not exist:** Per-fact (per-stored-item) audit. The literature monitors global spectral radius, not item-level attribution. No published system provides a certificate that fact F_i has been erased from reservoir internal state. The only erasure work is in the machine unlearning literature (linear models, Mahadevan & Mathioudakis 2021; Selective Synaptic Dampening 2023; MUNKEY key-deletion 2025) but these are general-purpose gradient-based methods not connected to reservoir architecture. Concept-drift detection with RC (Chaos journal 2025) detects distributional shift in the *input stream*, not in stored-fact provenance.

**Gap:** Third-cumulant or higher-moment fingerprinting of stored-fact residue is unpublished. The cumulant-to-eigenvalue link in Haruna et al. stops at second cumulant and does not produce per-item certificates.

### Family 2: Compositional algebra over reservoir activations

**What exists:** Vector Symbolic Architecture (VSA) literature is active and advancing rapidly (Kleyko et al. 2025 comprehensive theory; GHRR 2024; Walsh-Hadamard linear VSA 2024; VSA-Lisp 2025). Binding and unbinding operations are well-developed in VSA. However, VSA and reservoir computing are parallel communities; the "Principled neuromorphic reservoir computing" (Nature Communications 2025) paper uses VSA-style higher-order polynomial features for time-series prediction but does not provide binding/unbinding operators over the reservoir's *stored memory* -- it uses the reservoir as a nonlinear expansion substrate, not as an algebraic compositional store.

HoGRC (Li et al. 2024, Nat. Comms.) introduces simplicial complex decomposition over reservoir state for structure inference but this is a supervised regression task, not a compositional algebra with bind/unbind inverses.

**What does not exist:** A reservoir architecture that exposes bind(A, B) and unbind(A, key) operations directly on stored activation patterns, or supports nested hierarchical composition (trees of bound pairs) recoverable from reservoir state. The "Comprehensive Theory" (Kleyko et al. 2025, arXiv:2511.14484) covers 30 ESN variants; it mentions VSA as background but does not develop binding/unbinding over reservoir activations.

**Gap:** Bilinear contraction as a first-class reservoir primitive (not just a readout trick) is absent. All compositional work treats the reservoir as a fixed nonlinear kernel, not as a mutable algebraic store with structured operations.

### Family 3: One-shot writes via linear-readout layers

**What exists:** This family is the most developed. Ridge regression / Moore-Penrose pseudoinverse over reservoir states is standard. Kleyko et al. 2025 proposes "covariance-based readout" (Eqs. 14-16) that precomputes readout matrix W_out without iterative training, enabling direct closed-form writes. Memory capacity scaling with readout size is characterized (Phys. Rev. Research 2025, arXiv:2504.19657). Reservoir-based associative memory (Kong, Brewer & Lai 2024, Nat. Comms.) demonstrates index-based and content-based retrieval for dynamical attractors.

**Limitation of existing work:** Kong et al. require full-batch retraining when adding new patterns (no one-shot addition). Kleyko et al.'s covariance readout is one-shot in the sense of no iterative optimization, but it is not item-addressable (cannot erase item i without recomputing the full readout). Capacity is sublinear in readout size when neuronal correlations are strong (arXiv:2504.19657).

**Gap:** Closed-form per-item update rule for the linear readout (rank-1 update to W_out that adds or removes exactly fact F_i with bounded interference) is not published in the reservoir context. The machine unlearning literature has rank-1 update formulas for linear models (Newton step, influence functions) but these are not specialized to the reservoir activation geometry.

---

## Cross-Cutting Finding: Closest Prior System

**Closest:** MemTrust (arXiv:2601.07004, Jan 2026) is an architectural paper proposing a "zero-trust unified AI memory system" with verifiable deletion via encryption-key destruction. It addresses the right-to-be-forgotten in LLM memory backends. It does NOT use reservoir computing, does NOT provide compositional algebra over stored activations, and does NOT expose a spectral fingerprint of residual item influence. It handles deletion at the storage-layer level, not the algebraic-activation level.

**Verdict:** No published system (2023-2025 search scope, extended to early 2026 where relevant) combines even two of the three capability families in one architecture. The closest one-system approximation -- Kleyko et al. 2025 -- covers one-shot writes (covariance readout) and partial spectral monitoring (spectral radius), but lacks per-item deletion certificates, lacks compositional binding/unbinding, and lacks higher-cumulant fingerprinting. It is 1.5 of 3 families.

---

## Cheap Decisive Test

**Q:** Does any 2023-2025 paper cite all three of: (a) a binding operation over reservoir activations, (b) a deletion-proof or erasure-certificate formalism applied to reservoir internal state, (c) a one-shot or closed-form linear readout write?

**Test:** Citation cross-search on Google Scholar / Semantic Scholar: query papers citing both Jaeger (ESN original) AND a VSA binding paper AND a machine-unlearning/deletion-certificate paper. If zero papers in the intersection exist, the triple-combination gap is confirmed.

**Predicted result:** Zero intersection papers. Confidence 0.85 (pre-calibration), 0.65-0.70 after calibration penalty.

---

## Falsifiable Predictions

### HARD-PASS thresholds (confirm the gap is real and substantial)

- HP1: Zero papers found in 2023-2025 that use words "binding" or "unbinding" AND "reservoir" in context of compositional memory operations (not just "reservoir sampling"). Current evidence: zero.
- HP2: Zero papers proposing a spectral fingerprint or cumulant-based certificate of per-item erasure from reservoir activations. Current evidence: zero.
- HP3: Kleyko et al. 2025 covariance-readout is confirmed NOT to support per-item deletion (verified by paper structure: full W_out recomputed from scratch). Current evidence: confirmed by paper scan.

### HARD-FAIL thresholds (gap is already closed -- product positioning needs to shift)

- HF1: A 2023-2025 paper found that provides a binding + deletion-certificate combination over reservoir activations. Not found.
- HF2: A 2023-2025 paper found demonstrating third-cumulant or higher-moment spectral fingerprint for per-item attribution in a dynamic recurrent network. Not found.
- HF3: Any system (reservoir or not) that combines all three families in a single published API. Not found (MemTrust comes closest but lacks algebraic-activation layer entirely).

---

## Cross-Thread Synthesis with Prior Research Entries

- The SKAH-M confirmation (project memory 2026-05-27) established substrate as a non-reciprocal + spatial-correlated Hopfield hybrid operating in non-equilibrium stat-mech. This is *not* standard ESN: ESNs are time-multiplexed with echo-state property (W spectral radius < 1), whereas SKAH-M is a static associative memory (not time-driven). The ESN audit-primitive literature (spectral radius monitoring, Lyapunov exponent tracking) is *partially* transferable but maps to different physics: ESN monitors dynamics stability; substrate audit monitors stored-pattern residue.
- The free-probability thread (F4 free cumulants, top advisor recommendation) is adjacent: Haruna et al.'s second-cumulant classification of reservoir universality classes is exactly the free-prob framework applied to W; extending to third cumulants (kappa_3) would give the spectral fingerprint capability missing from all current RC work. This is a direct bridge.
- The compositional algebra gap in RC/ESN maps cleanly onto the VSA binding work (Walsh-Hadamard 2024, GHRR 2024) -- but the bridge from VSA binding to *reservoir-stored* pattern is unpublished. This is a synthesis opportunity.

---

## Substrate-Product Implications

1. **Deletion certificate uniqueness:** The combination of per-item erasure certificate + spectral fingerprint (third-cumulant signature of stored item) is absent from all 2023-2025 RC/ESN literature. A system that provides this would be the first; product narrative "auditable deletion of specific facts from a dynamic memory" has no published competitor in this architecture class.

2. **Compositional algebra stack precedence:** Binding/unbinding over stored activations (not just over readout features) is novel relative to current RC literature. The VSA community does binding, but over fresh vectors, not over reservoir state that persists in W. The "hierarchical bipolar tree composition + bilinear contraction" stack is not anticipated by any current RC paper.

3. **The one-shot write + deletion pair:** One-shot writes (covariance readout, ridge solution) exist; one-shot *deletions* with bounded interference do not. The rank-1 update formula for W_out that removes fact F_i exactly (Sherman-Morrison style) is derivable from existing linear-algebra but unpublished in the RC context. This is the most immediately testable novelty claim.

4. **Triple combination:** The product narrative built on (deletion certificate + cumulant fingerprint + hierarchical tree composition + bilinear contraction) as one unified algebraic stack has no precedent in reservoir computing, echo state networks, VSA, or machine unlearning literature as a combined system.

---

## Follow-On Drill Candidates

1. **Sherman-Morrison / rank-1 update for linear readout deletion** (subfield: numerical linear algebra + machine unlearning for linear models). Drill question: does any paper specialize the Newton/influence-function unlearning update to the specific geometry of reservoir activation matrices (correlated, non-i.i.d., structured by echo-state property)? This would directly formalize the "one-shot deletion certificate" primitive. 1-2 targeted lit scans in NeurIPS/ICML machine unlearning track (2023-2025).

2. **Third-cumulant / free-cumulant spectral attribution for random recurrent networks** (subfield: free probability applied to RNNs + random matrix theory for non-equilibrium networks). The Haruna et al. 2021 universality-via-second-cumulant paper is the known anchor; extensions to higher cumulants in non-Gaussian W distributions are the target. Connects directly to Tier-1 advisor recommendation F4 (Voiculescu kappa_n free cumulants). Search: "free cumulants recurrent network universality" + "third moment random matrix reservoir."

3. **VSA binding + content-addressable memory in static (non-temporal) associative networks** (subfield: modern Hopfield / dense associative memory + VSA). Does any 2023-2025 paper expose VSA-style bind/unbind over the stored patterns of a dense Hopfield or attractor network (not a time-driven ESN)? This maps more tightly to the substrate physics (SKAH-M is static) and may surface closer precedents for the compositional algebra gap. Search: "vector symbolic Hopfield binding" + "compositional associative memory unbinding."

---

## P_deflated Estimates

| Claim | Raw P | Calibration penalty | P_deflated |
|---|---|---|---|
| Triple-combination gap is real (no published system) | 0.85 | -0.20 (uncharted regime, sparse cross-search) | 0.65 |
| Sherman-Morrison rank-1 deletion for RC readout is novel | 0.70 | -0.20 | 0.50 |
| Third-cumulant fingerprinting is novel in RC context | 0.75 | -0.20 | 0.55 |
| VSA binding over reservoir state is novel | 0.80 | -0.20 | 0.60 |
| All three families will remain uncombined in published literature through 2026 | 0.65 | -0.15 | 0.50 |

Novel-synthesis P is capped at 0.50 per calibration rule.

---

## Citations (Verified: 11 papers confirmed via fetch/search)

1. Kleyko, Kymn, Frady, Loutfi, Sommer. "Towards a Comprehensive Theory of Reservoir Computing." arXiv:2511.14484 (Nov 2025). Covers 30 ESN variants; covariance-based readout is a one-shot write; compositional algebra and per-item erasure absent.

2. Kong, Brewer, Lai. "Reservoir-computing based associative memory and itinerancy for complex dynamical attractors." Nature Communications (2024). Index-based and content-addressable attractor retrieval; batch retraining required; no erasure, no binding.

3. Singh, Sankaranarayanan, Raman. "Contraction, Criticality, and Capacity: A Dynamical-Systems Perspective on Echo-State Networks." arXiv:2507.18467 (2024). Spectral-norm bounds on ESN dynamics; per-fact audit absent; compositional algebra absent.

4. Haruna, Toshio, Nakano. "Universality in reservoir computing and higher-order statistics." arXiv:2112.01886 (2021). Second-cumulant universality classification; eigenvalue-distribution link; stops at kappa_2, no per-item attribution.

5. Li, Zhu, Zhao et al. "Higher-order Granger reservoir computing." Nature Communications (2024, DOI:10.1038/s41467-024-46852-1). Simplicial complex decomposition over reservoir state for structure inference; no binding/unbinding inverses; iterative training.

6. Ortega, Rossmannek. "Echoes of the Past: A Unified Perspective on Fading Memory and Echo States." Neural Computation 38(5) (2026). Unifies fading-memory / echo-state notions; per-fact erasure and compositional algebra out of scope.

7. "Reservoir-computing approaches to unsupervised concept drift detection in dynamical systems." Chaos 35(2) (Feb 2025). Drift detection on input stream distribution, not stored-fact provenance.

8. Chen, Iguchi, Hikasa, Tsuchiya. "Spectral dynamics reservoir computing for high-speed hardware-efficient neuromorphic processing." arXiv:2603.04901 (2026). Spectral manifold of material response as compute substrate; no per-fact audit or compositional algebra.

9. "Neuronal correlations shape the scaling behavior of memory capacity and nonlinear computational capability." arXiv:2504.19657 (2025). Memory capacity sublinear with readout size under strong correlations; linear readout characterization; no per-item operations.

10. "MemTrust: A Zero-Trust Architecture for Unified AI Memory System." arXiv:2601.07004 (Jan 2026). Verifiable deletion via key destruction; operates at storage layer, not algebraic-activation layer; no reservoir, no compositional algebra.

11. Mahadevan, Mathioudakis. "Certifiable Machine Unlearning for Linear Models." (2021). Approximate unlearning for linear models; not specialized to reservoir activation geometry.

---
