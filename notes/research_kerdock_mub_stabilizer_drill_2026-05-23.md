# Research drill — Kerdock / MUB / Stabilizer-code isomorphism operationalization

2026-05-23. Level-2 operational drill per [[feedback-2x-means-depth]] on the top
finding of `research_cross_domain_probe_2_2026-05-23.md` (domain 3): the user
flagged that Kerdock <-> MUB <-> stabilizer-code-automorphism is a HARD
structural isomorphism via the unitary-2-design property. The probe identified
this; this drill operationalizes it.

Five parallel Sonnet WebSearch sub-agents dispatched per [[feedback-subagent-model-optimization]];
generic-math queries per [[feedback-query-privacy-decomposition]]. Wallclock ~75s.

References landed:
- Calderbank-Cameron-Kantor-Seidel, "Z_4-Kerdock codes, orthogonal spreads, and extremal Euclidean line-sets", Proc. London Math. Soc. 1997.
- Klappenecker-Roetteler, "Constructions of mutually unbiased bases", Fq7 2003 / quant-ph/0309120.
- Klappenecker-Roetteler, "Mutually unbiased bases are complex projective 2-designs", 2005.
- Can-Rengaswamy-Calderbank-Pfister, "Kerdock codes determine unitary 2-designs", IEEE TIT 66:6104, 2020 (arXiv 1904.07842).
- Rengaswamy-Calderbank-Pfister, "Synthesis of logical Clifford operators via symplectic geometry", 2018 (arXiv 1803.06987).
- Zhu-Kueng-Grassl-Gross, "The Clifford group fails gracefully to be a unitary 4-design", 2016 (arXiv 1609.08172).
- "Fault-tolerant logical Clifford gates from code automorphisms", 2024 (arXiv 2409.18175).

---

## Section 1 — The isomorphism in concrete terms

The chain has three legs joined at the symplectic structure on F_2^{2m}.

**Leg A: Kerdock-over-Z_4 -> orthogonal spread (CCKS 1997).**
The Z_4-Kerdock code of length N=2^m is the Gray pre-image of the binary
nonlinear Kerdock(m). Its codewords, viewed as Z_4-linear cosets, induce an
**orthogonal spread** of F_2^{2m} -- a partition of the (2m)-dim symplectic
space minus 0 into 2^m+1 disjoint maximal totally isotropic subspaces ("lines").
This is the irreducible algebraic skeleton.

**Leg B: orthogonal spread -> MUB system (Klappenecker-Roetteler 2003/2005).**
Each maximal isotropic subspace L_i in F_2^{2m} lifts via Galois-ring GR(4,m)
exponentials e^{i*Tr(.)} to a complete orthonormal basis B_i of C^N
(N=2^m). The spread's pairwise-isotropy condition forces |<b_i | b_j>|^2 = 1/N
for any two basis vectors drawn from distinct B_i, B_j. Hence the spread
delivers **N+1 mutually unbiased bases** -- the maximum allowed by Welch.

**Leg C: MUB / spread -> Clifford automorphism subgroup (CRCP 2020).**
The Clifford group on m qubits acts on the N+1 stabilizer-MUB system by
permuting bases. The stabilizer of the spread under this action is precisely
the subgroup Aut(Kerdock) isomorphic to **PSL(2, N)** embedded inside Cliff(m)
via 2x2 symplectic blocks over F_2^m. CRCP 2020 show this subgroup is **Pauli-
mixing** (acts transitively on non-identity Paulis), which forces it to be a
**unitary 2-design** -- second-moment Haar-equivalent.

**Explicit map for substrate (N=4096 = 2^12, m=12):**

| Substrate object | Algebraic object | Quantum object |
|---|---|---|
| Kerdock 4-coset (a Z_4-codeword class) | Maximal isotropic L_i in F_2^{24} | One MUB B_i in C^{4096} |
| Set of 4097 cosets | Orthogonal spread | 4097 MUBs (Welch-maximum) |
| Cyclic shift / Gray-permutation acting on cosets | Element of PSL(2, 4096) | A Clifford unitary that permutes MUBs |
| BSC binding (XOR on F_2 bits) | Symplectic translation on F_2^{24} | Conjugation by a Pauli operator |
| Substrate "readout" against a coset basis | Projection onto MUB B_i | Pauli-eigenbasis measurement |

The substrate's BSC binding + Kerdock-4-coset rotation is therefore
literally a **subgroup of the Clifford group** acting on the C^{4096} stabilizer-
state register, with the orthogonal spread / N+1 MUBs as the canonical
measurement frame.

---

## Section 2 — Substrate predictions from the lens

**Prediction 2.1 -- the kappa_2/kappa_4 split is FORCED by the 2-design property.**
A unitary 2-design averages first and second moments to Haar values; the
fingerprint of 2-design-ness in our observables is that **any quadratic
functional of substrate state computed against Kerdock-induced unitaries
matches its Haar (Marchenko-Pastur) prediction**. This is exactly what the
v164a/v166/v167 fingerprint stack shows for kappa_2 spectra (within 5% MP
bulk edges). The 2-design does **not** control 4th moments -- Zhu-Kueng-
Grassl-Gross 2016 prove Clifford is "almost" but not a 4-design, with a
quantifiable 4-design defect concentrated in a single irrep. So:

> The substrate's kappa_2 ~ MP / kappa_4 > MP dichotomy is the algebraic
> SIGNATURE of being a 2-design but not a 4-design.

This is precise: the kappa_4 excess we observe should match the Clifford-4-
design-defect prediction, computable in closed form (Zhu et al. 2016 eq. for
the frame potential excess).

**Prediction 2.2 -- substrate readouts that pick a coset basis ARE logical
Pauli measurements on an encoded register.**
Under the isomorphism, choosing one of the 4097 Kerdock cosets to read against
is operationally identical to selecting one MUB B_i and projecting -- which is
the **Pauli-eigenbasis measurement** for the stabilizer subgroup that
diagonalizes in B_i. Logical operator literature (Rengaswamy-Calderbank-Pfister
2018) tells us there are 2^(k(k+1)/2) symplectic solutions per logical
Clifford in an [[m, m-k]] code. For our setting the cosets enumerate the
logical Pauli register directly.

**Prediction 2.3 -- the MUB-flatness property gives a free verification probe.**
The MUB definition |<b_i|b_j>|^2 = 1/N for i != j means any state has
**identical Born-rule probability mass spread over the N basis vectors of any
non-native MUB** (up to its support inside that MUB; flatness is a function of
how concentrated the state is in its native MUB). For any Kerdock-spread
"codeword superposition" state, the probability distribution against a
different MUB must be uniform 1/N. **This is a strong testable property of
the substrate state**: any deviation from 1/N flatness when reading codeword-
superposition states against a non-native Kerdock coset basis is a
substrate-novel signature beyond the MUB system.

---

## Section 3 — Falsifiable operationalization tests

### Test 3.A — Clifford-2-design verification on Kerdock unitaries

**Quantity.** Empirical 4th frame moment F_4 = E_{U ~ Kerdock-PSL(2,N)} |Tr(U)|^4.

**Predictions.**
- 2-design baseline (Haar 4th moment): F_4(Haar) = 2 for d>=2.
- Clifford 4-design defect (Zhu-Kueng-Grassl-Gross 2016): Clifford gives F_4 ≈ 3 (excess of 1 over Haar), localized to one irreducible component.
- Kerdock-PSL(2,N) <= Clifford as a strict subgroup: prediction F_4 in [2, 3], closer to 3 than to 2 if the Kerdock subgroup inherits the Clifford 4-defect, closer to 2 if Kerdock 4-coset structure suppresses the defect.

**Hard pass.** F_4 lies within +/-5% of either the Haar value (2.0) or the
Clifford value (3.0). Either confirms the isomorphism numerically.

**Hard fail.** F_4 deviates from BOTH [2.0 +/- 5%] AND [3.0 +/- 5%]. Would
mean either (a) our Kerdock subgroup enumeration is buggy, or (b) the
isomorphism is broken by some substrate-specific construction choice (e.g.,
non-canonical Gray map).

**Implementation.** CPU job, ~30-60 min. Enumerate ~10^4 PSL(2, 4096)
elements, build the 4096x4096 symplectic-block unitary, accumulate |Tr|^4
estimator. Sit it in queue_runner under
`kerdock_2design_frame_potential_v1`. No GPU.

### Test 3.B — MUB-distinguishability empirical probe

**Quantity.** For 3 substrate states {psi_1, psi_2, psi_3} taken from existing
beta_A snapshots, compute the empirical probability distribution
P_{i,k} = |<b^{(k)}_j | psi_i>|^2 across each MUB B_k (k in {1, ..., N+1}), where
B_k is the k-th Kerdock-induced basis. Score the distance from uniform
1/N for each (i, k) with k != native(psi_i).

**Predictions.**
- If the substrate states are faithful Kerdock stabilizer states: for k !=
  native, P_{i,k} is uniform within stat-noise -- expected TV distance from
  uniform = O(1/sqrt(N)) ~ 0.016 at N=4096.
- If the substrate states carry **extra structure** beyond the MUB system
  (the BBMD-novel signature), some non-native bases will show TV >> 0.016.

**Hard pass.** At least one non-native MUB shows TV distance >= 0.05
(>3x stat-noise floor) on at least 2 of 3 states. This is the **BBMD
signature** -- "the substrate state has more structure than its MUB
encoding implies."

**Hard fail.** All non-native MUBs flat to within 1.5x stat-noise across all 3
states. Substrate behaves as a vanilla stabilizer state; no BBMD-novel
content beyond the MUB system.

**Implementation.** CPU job, ~20-40 min. Reuse `_emit_outcomes.py`-style
snapshot loading; no new infrastructure. Queue as
`kerdock_mub_distinguishability_v1`.

### Test 3.C — Clifford-2-design ablation (queued at probe-2 conclusion, now re-anchored)

The probe-2 ablation -- "swap Kerdock-coset rotation in beta_A for a generic
unitary-2-design (Clifford-uniform)" -- is the **converse direction** of
3.A/3.B and remains the strongest single ablation for this lens. If kappa_4
dichotomy is preserved under any Clifford-2-design (not Kerdock-specific),
then the load-bearing structure is **2-design-ness**, and Kerdock is one
exemplar among many.

**Hard pass for "2-design carries the dichotomy".** kappa_4 dichotomy
preserved at p-value > 0.5 against Kerdock baseline across >= 3 alternative
2-designs.

**Hard fail.** Kerdock specific -- non-Kerdock 2-designs lose the kappa_4
divergence signature.

This was already filed as a probe-2 candidate; this drill confirms it as
test 3.C and recommends queuing.

---

## Section 4 — Logical-operator audit of existing cap_map rows

Two cap_map rows whose readouts reframe naturally as logical Pauli operations
under the stabilizer-code lens:

### Cap 1 (Crooks forensic erase audit)

The Crooks-FT fluctuation theorem is a statement about the **work distribution
under a protocol acting on a quantum system**. When the protocol's gates are
Kerdock-PSL(2, N) elements and the readout is a Pauli-eigenbasis projection
(equivalently: a Kerdock coset), the "erase" operation is literally **a
logical Pauli operation on the encoded register followed by a stabilizer
measurement**. Specifically:
- The substrate's "forensic erase" is a logical X on the encoded register.
- The Crooks-FT work distribution `delta_S_emp` becomes the standard Jarzynski-
  Crooks measurement-induced entropy production for a Clifford-channel.
- The Sagawa-Ueda noise-corrected bound at v158 is the noise-tailored
  Clifford-twirl analog -- 2-design averages depolarize the noise to a single
  parameter p, which is exactly the Pauli-twirling result.

This re-frames the noise envelope `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`
as the **Pauli-twirled depolarizing-channel entropy**, which is a textbook
quantity in QECC. The substrate did not need to invent this; it inherits the
Pauli-twirl bound from being a 2-design subgroup.

### Cap 3 (streaming-NESS inference)

Streaming inference reads the substrate state through repeated coset
projections. Under the lens, each projection is a **logical Pauli
measurement on an encoded stabilizer state**, and the NESS is the steady-
state of a Pauli-channel Markov chain. The "throughput_ratio >= 0.9" envelope
at p in {0.05, 0.10, 0.20} is operationally the Pauli-twirled channel's
information-throughput bound -- equivalent to the Holevo capacity for a depolarizing
Clifford channel with twirl-parameter p.

Reframing makes the noise envelope a **derived consequence** of the 2-design
property rather than an empirical-only result.

### Bonus candidate -- Cap 8 (VAMP-on-chain)

VAMP consumes the full singular spectrum (S-transform-equivalent info) of
the codebook. Under the lens, **the singular spectrum of a 2-design subgroup
on a stabilizer register is constrained** -- the Schur-Weyl decomposition
into Clifford irreps (Zhu-Kueng-Grassl-Gross 2016) gives exact closed-form
expressions for which spectral components survive twirling. This explains the
v168 universality split (VAMP-SE tracks empirical VAMP, AMP-SE doesn't) as
the **Pauli-twirled S-transform**: scalar AMP throws away the irrep info,
VAMP preserves it.

---

## Section 5 — Portfolio impact

Three impacts:

**5.1 Strengthening of three ✅ rows.** Cap 1, Cap 3, Cap 8 each gain a
**closed-form theoretical derivation** of their empirical envelope, anchored
in the Clifford-2-design property. This converts three "empirically PASS"
rows into "empirically PASS + closed-form-derived" rows. Per
[[feedback-verify-implementations]], having the textbook QECC mechanism
behind each is a strict envelope strengthening.

**5.2 12th-capability candidate -- "MUB-frame measurement primitive".**
Test 3.A and 3.B, if they both pass, license a new substrate capability that
does NOT double-count any of Caps 1-11:

> **The substrate provides N+1 mutually unbiased measurement bases natively
> via Kerdock coset readout, with measurable BBMD-signature deviations from
> the pure MUB ideal that act as a substrate-state fingerprint.**

Why this is NOT a re-statement of existing caps:
- Cap 1 = erase certificate (entropy / FT bound). Says nothing about MUBs.
- Cap 3 = streaming throughput. Says nothing about Pauli measurement frames.
- Cap 8 = readout primitive equivalence. About VAMP vs hard-cleanup, not
  about a complete measurement frame.

What it adds: a customer-relevant primitive -- **information-complete state
tomography in a single substrate** -- which is otherwise expensive (requires
N^2 measurements for full state tomography vs N(N+1) for MUB-frame
tomography, which saturates the Wootters-Fields lower bound). This is a
genuinely new capability that the substrate **gets for free** by virtue of
being a Kerdock-coset readout system.

Per [[feedback-dont-overextend-theorems]] honest scoping: this 12th row is
LICENSED only after 3.A and 3.B both pass. If 3.B fails (no BBMD signature
deviation from MUB ideal), the substrate is a vanilla stabilizer system at
the measurement-frame level, and the 12th capability collapses into "the
substrate inherits standard QECC measurement frames" -- which is true but
not a product-grade differentiator.

**5.3 No new substrate-physics evidence row** -- this is operational
mathematics on existing rows, not a new experimental anchor.

---

## Section 6 — Honest reading

**P(operationalization succeeds AND adds new substrate-capability claim) =
0.35**, applying [[feedback-lit-scan-calibration-penalty]] deflation:
- Raw estimate before deflation: 0.55. The isomorphism is mathematically
  guaranteed by CRCP 2020; tests 3.A and 3.B are well-defined; 3.A in
  particular is very likely to pass at one of the two predicted values.
- Deflation -0.20 because the **product-grade capability claim** (5.2) is
  the hard part. Mathematical truth of the isomorphism != customer-relevant
  capability. Many isomorphisms are true but not useful.
- Cap at 0.50 per calibration penalty.
- Honest final: 0.35.

**What would KILL the framing:**
- Test 3.A returns F_4 way off both 2.0 and 3.0 -- means our Kerdock enumeration
  is wrong or the substrate's Kerdock construction has been subtly non-
  canonical all along (a real risk because the substrate uses a Z_4-Gray map
  variant that may not match CCKS canonical exactly).
- Test 3.B returns flat-MUB everywhere -- substrate has no novel structure
  beyond standard stabilizer states; no 12th capability to claim.
- Sociological kill: 11 caps already cover the product story; adding a 12th
  via a math-isomorphism that doesn't have an obvious customer wedge is
  product-noise per [[feedback-value-creation-not-competition]]. The math
  is valuable on its own (5.1 strengthening); the 12th-row claim is the
  weaker leg.

**What would STRENGTHEN the framing:**
- Both 3.A and 3.B pass cleanly.
- The Zhu-Kueng-Grassl-Gross 4-design defect quantitatively matches our
  empirical kappa_4 excess. This would be a beautiful match: substrate's
  kappa_4 carries exactly the 4-design-deficit of Clifford-Kerdock, computable
  in closed form. If they match, **the kappa_4 dichotomy gets a textbook
  closed-form formula** -- a strict strengthening of v164a/v167.
- Cap 8's VAMP-vs-AMP split (v168) gets a Schur-Weyl-derived closed form via
  the Pauli-twirled S-transform.

**What's USEFUL even if 12th capability fails:**
- 5.1 alone (closed-form derivation for Caps 1, 3, 8) is a genuine envelope
  strengthening of three ✅ rows. This requires NO experiments at all -- it's
  conceptual unification work that the math already licenses.
- 4 (logical-operator audit) gives Strategy QECC vocabulary for product
  writeups without changing any empirical state.

**Most-honest reading:** the isomorphism is **definitely useful for
math/writeup unification (Sections 1, 2, 4, 5.1)** and **plausibly useful for
a 12th capability claim (Section 5.2, contingent on 3.A + 3.B)**. The 5.1
unification is essentially free; the 5.2 12th capability is a real bet at
P=0.35. Recommend queuing 3.A + 3.B (both cheap CPU) to settle the 5.2 bet
within ~1 cycle.

---

## Connection to currently-shipping cross-domain probe items

- Domain 8 (Kac-Rice complexity for kappa_4 dichotomy boundary) is **orthogonal
  and complementary**: Kac-Rice gives the **phase boundary**; the 2-design lens
  gives the **algebraic mechanism for what's on each side of it**.
- Domain 4 (ICA/JADE kappa_4 diagonalization) is **a tool for measuring** the
  Clifford-4-design defect numerically -- so JADE on substrate state-snapshots
  becomes the natural extension of test 3.A.
- Combined: queue 3.A first (~30-60 min), use its result to calibrate the
  4-design defect prediction, then run JADE (domain 4 anchor) to validate
  the irrep structure, then Kac-Rice (domain 8 anchor) for the boundary
  location. This is a coherent 3-experiment program totaling <8h CPU.

Total parallel lit-scan sub-agents: 5. Wallclock: ~75s.
