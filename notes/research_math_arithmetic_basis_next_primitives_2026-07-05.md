# Research: envelope-push on MATH capability — next arithmetic primitives after ADD (HARD_PASS)

**Date:** 2026-07-05
**Trigger:** Director envelope-push drill (per [[feedback-research-every-finding-for-mechanism-and-envelope-push]]) on
`exp_math_rns_add_chain_v1`, which landed FULL HARD_PASS (verified off-disk:
`data/exp_math_rns_add_chain_v1/metrics.json`, `verdict=HARD_PASS`, `run_mode=full`, arm A exact-add = **1.000** at
all 3 moduli regimes (M=504/5168/70520), control B (random-codebook) collapses to **0.003/0.000/0.000**, control C
(scrambled-modulus) collapses to **0.012/0.002/0.002**, 10-step chains hold at 1.000, equality-check accept/reject
both 1.000 — even tighter than the pre-registered 0.90/0.15/0.05 bands). Scope: MULTIPLICATION, COMPARISON/ORDERING,
SUBTRACTION as the next primitives toward the core-mathematics/self-reasoning north star. Design/scoping only, per
Director instruction — **no dispatch, no routing files** (USER-locked ferry-deprecation override; this note is the
sole deliverable).
**Discipline:** scoured `experiments/exp_math_rns_add_chain_v1.py` (full source read) and the parent design note
(`notes/research_math_capability_translation_first_cell_2026-07-05.md`) before dispatch. 4 parallel Sonnet lit-scans
(generic math/CS/neuro terms only, no substrate-novel mechanism names off-platform per
[[feedback-query-privacy-decomposition]]). Lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis
capped at 0.50; explicit HARD-FAIL bands below).

---

## HEADLINE

**Subtraction is free (already implicitly certified by the landed add cell's own exact homomorphism). Comparison
needs one small NEW cross-field borrow (a classical Residue-Number-System hardware trick with zero prior VSA/HDC
precedent — genuine novel-synthesis, capped P). Multiplication has a NAMED, CITABLE mechanism already in the
substrate's own primary reference paper — but a fresh read of that paper (via lit-scan, not assumption) shows it is
NOT free like addition: it requires decoding one operand mid-pipeline and restricting all moduli to PRIMES, refining
(not confirming) the prior 2026-06-23 drill's "500-1000 line / second binding operator" estimate down to roughly
150-250 lines — smaller than 06-23 feared, but still real new engineering, unlike subtraction's near-zero cost.**
Ranked build order for the self-reasoning north star: **subtract -> compare -> multiply**, because subtract+compare
are what the already-flagged self-VET/numeric-threshold-logic gap (`notes/research_self_reasoning_capability_gap_2026-07-05.md`)
actually needs, while multiply serves the broader "core mathematics" arithmetic vision but is not on that critical
path. A parallel discrete-logarithm ("index calculus") re-encoding scheme was investigated and **explicitly rejected**
as an alternative multiplication route: it would require a Zech's-logarithm lookup table to restore addition in the
log domain, i.e. it would UNDO the just-proven free-addition mechanism rather than extend it — the paper's own
decode-then-exponentiate operator is the better-fitted choice because it sits *on top of* the existing additive
encoding rather than replacing it.

---

## Q1 — MULTIPLICATION: does it admit an exact substrate operation, or a different encoding?

**Answer: a different (but related, and already-published) mechanism — not a new re-encoding scheme, a second
OPERATOR layered on the same phasor encoding.**

The substrate's own cited primary reference — Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen, "Computing
with Residue Numbers in High-Dimensional Representation" (*Neural Computation* 2024, arXiv:2311.04872) — **already
defines a multiplication operator** (called `star`/⋆ in the paper), confirmed independently by a fresh lit-scan of
the paper itself plus its direct 2025 follow-up ("Hey Pentti, We Did (More of) It!", arXiv:2511.08767, which reuses
the identical mechanism). The mechanism, as characterized by the lit-scan:

- The paper's base encoding already puts the raw integer directly in the phasor **exponent** (`z(x) = z^x`), which
  is *why* addition falls out for free (`z(x1+x2) = z(x1) ⊙ z(x2)`, plain elementwise product — exactly what the
  landed add cell implements).
- Multiplication is the **mirror-image cost**: because the integer lives in the exponent (not as a log), computing
  `z(x1*x2)` requires **decoding one operand back to a concrete integer** (via per-sub-block codebook argmax — the
  substrate's own `decode_residues()`, already proven, no CRT stitch even needed for this sub-step), then
  **elementwise-exponentiating the other operand's phasor by that decoded integer** (`z(x1)^x2`), with a
  modular-inverse "anti-base" correction term, **and moduli restricted to PRIMES** (the paper requires this for the
  correction to be well-defined).
- This is asymmetric (one operand must leave pure-vector form mid-pipeline) and needs new prime-only moduli
  (the landed add cell's regimes — `(7,8,9)`, `(16,17,19)`, `(40,41,43)` — are NOT all-prime; a multiply cell needs
  fresh coprime **all-prime** triples, e.g. `(5,7,11)` M=385, `(13,17,19)` M=4199, `(37,41,43)` M=65231).
- Numerically low-risk: the exponent used per sub-block is bounded by `(m_i - 1)` (small, <100 in-scale), so
  floating-point phase drift from `angle * exponent` is the same order of magnitude the add cell's own codebook
  construction (`phase = 2*pi/m * r * k`) already handles exactly at 1.000 — **not** a new precision risk.

**A discrete-log ("index calculus") re-encoding was investigated as an alternative and rejected.** In an LNS
(logarithmic number system), representing a value by its discrete log w.r.t. a primitive root mod a prime makes
multiplication free (log-domain addition), but the lit-scan confirms this is a genuine **duality, not a free lunch**:
addition becomes hard in the log domain (historically solved only via a **Zech's-logarithm** lookup table, Zech 1849 /
Jacobi ~1846 — itself an O(m)-size correction table, not an algebraic shortcut), and zero has no discrete log at all
(needs an out-of-band sentinel). Adopting this scheme substrate-wide would **break the just-proven exact-add
mechanism** (forcing it through a Zech-log table) rather than compose with it. The paper's own `star` operator is
the better-fitted choice precisely because it reuses the SAME base encoding the add cell already certified, adding
multiplication as a second, independent operation rather than a competing representation.

**Feasibility:** MODERATE reuse (per-sub-block decode + CRT-decode-of-result both 100% reused from the landed add
cell; the new pieces are a prime-only moduli table, a phasor-integer-power helper (~10-20 lines), and the
anti-base/modular-inverse correction). Est. **~150-250 new lines** — smaller than the 2026-06-23 drill's "500-1000
line, second binding operator, qFHRR bridge" estimate (that estimate was scoped for the harder JOINT add+multiply+
compare build; this note narrows it further now that the specific mechanism is confirmed from the primary paper
itself, mirroring how the add cell itself came in at ~100-200 lines against a similar prior overestimate).

---

## Q2 — COMPARISON/ORDERING: derivable from residues, or needs magnitude decode?

**Answer: needs a magnitude decode step — but a cheap one, reusing subtraction + the already-proven CRT decode, NOT
a new decode mechanism.** This is the honest, well-documented limitation of ANY residue/RNS representation: individual
residues carry no place-value/order information by design (that absence of carry/order structure is *why* RNS is
carry-free and parallel in the first place) — confirmed by the lit-scan as the standard, textbook characterization
(Szabó & Tanaka 1967, the classical RNS-arithmetic reference).

Three known families of RNS comparison method surfaced, ranked by fit to the substrate's existing machinery:

1. **Half-range sign-detection (the recommended v1 mechanism).** If the true dynamic range of the operands is kept
   below `M/2`, then computing `d = (a-b) mod M` (via the conjugate-phasor subtraction below) and checking whether
   the CRT-decoded `d` falls in `[0, M/2)` vs `[M/2, M)` recovers the exact SIGN of `a-b` — confirmed real, standard,
   and correctly characterized by the lit-scan (Hung & Parhami 1994, *Computers & Mathematics with Applications*;
   general RNS signed-range convention `-floor(M/2) <= X <= floor((M-1)/2)`). This reuses subtraction (below) and the
   add cell's own CRT-decode verbatim — **no new decode mechanism**, only a dynamic-range convention (choose/verify
   `M > 2 * max_operand_range`) and a threshold test against `M/2`.
2. **Mixed-Radix Conversion (MRC)** — converts residues into a positional (place-value) representation supporting
   digit-by-digit comparison without full weighted reconstruction (Szabó & Tanaka 1967; Griffin/Tudor/Wigley).
   Higher fidelity for N-ary ranking but O(n^1.5)-O(n^2) sequential conversion cost and materially more new code —
   not recommended for v1.
3. **Core/Diagonal function** (Akushsky et al. 1977; Dimauro/Impedovo/Pirlo 1993) — adds redundant moduli for a fast
   monotonic rank estimate that generalizes cleanly to sorting N values (the half-range trick does not — it is
   inherently pairwise). Flagged as a **v2 stretch enhancement** (useful later for ranking multiple cert-ledger
   claims by confidence in one pass), not required for the first comparison cell.

**Genuine open gap, confirmed by lit-scan:** neither the substrate's own primary VSA/HDC reference (Kymn et al.
2024) nor its follow-ups (Hanley/Tomkins-Flanagan/Kelly 2025; qFHRR) define ANY comparison/ordering operator — "no
inequality, ordering, or '<' operator is defined or discussed anywhere" in that literature. This IS the actual
"different from addressing" primitive the Director's question anticipated: comparison is a **cross-field borrow**
(classical RNS hardware arithmetic -> the substrate's phasor/VSA representation), not a direct precedent —
genuinely novel-synthesis, hence capped P below.

**Known failure modes (flagged as HARD-FAIL controls, not glossed over):** exactly at `d = M/2` the result is
**undefined/overflow**, not a sign (naive `< M/2` vs `>= M/2` mis-handles this silently); if the dynamic-range
assumption (`|a-b| < M/2`) is violated, the sign comes back **silently wrong** with no detectable error signal from
the residues alone. Both should be explicit control arms in the v1 cell (a deliberate out-of-range trial that must
be caught/flagged, not silently mis-sign).

**Feasibility:** HIGH reuse (subtraction + CRT-decode both already-proven; comparison v1 needs only the M/2
threshold rule + an explicit overflow/out-of-range control arm). Est. **~50-100 new lines**, cheaper than
multiplication, and — unlike multiplication — needs NO prime-moduli constraint (can reuse the landed add cell's
exact REGIMES verbatim, provided the trial-value generator respects `M/2` headroom).

---

## Q3 — SUBTRACTION: trivial (conjugate phasor) or not?

**Trivial — confirmed, essentially a free corollary of the already-certified exact group homomorphism, not a new
claim requiring dispatch-worthy risk.** Given `enc(a) = exp(i * 2*pi*k*a/m)`, the complex conjugate is
`conj(enc(a)) = exp(-i*2*pi*k*a/m) = exp(i*2*pi*k*(m-a)/m) = enc(m-a) = enc(-a mod m)` — i.e. conjugation IS the
additive-group inverse, by elementary group theory, and this is exactly the operation the landed cell's own
`homomorphism_selftest()` already exercises implicitly (the group `(Z_m, +)` the add cell certified is, by
definition, a group — every element already has a certified inverse). `bind(enc(a), conj(enc(b))) = enc(a-b mod m)`
follows immediately; no new operator, no new codebook, no new moduli constraint. This is the same kind of
non-novel-restatement carve-out the parent note applied to its own prediction #5 (exact-match-as-self-consistency-
primitive) — P is **not** deflated by the full novel-synthesis penalty here, only lightly, to allow for a real but
narrow implementation-bug risk (sign convention off-by-one in the conjugate step; verified below).

**Feasibility:** TRIVIAL. Est. **~20-30 new lines** (a `conjugate()` helper + arm wiring + a control that verifies
`bind(enc(a), conj(enc(a))) == enc(0)` for all `a` — the additive-inverse identity check). Should ship FIRST, both
because it is free and because it is a literal prerequisite sub-step of the comparison cell's `d = (a-b) mod M`
above (build subtraction as a shared helper both cells import, not duplicated).

---

## Q4 — MINIMAL ENABLING BASIS FOR SELF-REASONING, AND BUILD ORDER

**Ranked build order: (1) SUBTRACT, (2) COMPARE, (3) MULTIPLY.**

| Rank | Cell | Mechanism sketch | Reuse | New code (est.) | P_deflated | Why this rank |
|---|---|---|---|---|---|---|
| 1 | `exp_math_rns_subtract_conjugate_v1` | `bind(enc(a), conj(enc(b)))` = `enc(a-b mod M)`; reuse add cell's codebooks/CRT-decode verbatim | ~95% (add cell verbatim + conjugate) | ~20-30 lines | **0.85** (non-novel corollary of an already-exact-verified homomorphism; light deflation only for implementation-bug risk, not mechanism risk) | Free, and a literal prerequisite for #2 |
| 2 | `exp_math_rns_compare_halfrange_v1` | subtract (above) -> CRT-decode difference -> threshold vs `M/2` (sign detection); explicit overflow/out-of-range control arm | ~80% (subtract + CRT-decode reused; NEW: M/2 convention + range-violation control) | ~50-100 lines | **0.45** (capped novel-synthesis; classical-RNS-to-VSA cross-field borrow, zero direct precedent, but mechanism itself is textbook/low-math-risk) | Directly closes the flagged self-VET/numeric-threshold-logic gap (`research_self_reasoning_capability_gap_2026-07-05.md`) — the actual missing self-reasoning primitive |
| 3 | `exp_math_rns_multiply_decode_exponentiate_v1` | decode operand B's per-sub-block residues (no CRT needed) -> exponentiate operand A's phasor per sub-block by that residue -> CRT-decode result; ALL-PRIME moduli required | ~70% (codebook + per-sub-block decode + CRT-decode reused; NEW: prime-moduli table, phasor-power helper, anti-base correction) | ~150-250 lines | **0.40** (mechanism is named/citable in the field's own canonical paper — less invented-from-scratch than comparison — but zero prior in-substrate HARD_PASS precedent for this specific operator, plus a new moduli constraint) | Extends toward general "core mathematics" arithmetic (word problems, scaling, compound predicates) but is NOT on the self-reasoning critical path the way compare is |

**Why subtract+compare, not multiply, is the enabling basis for self-reasoning-about-own-mechanisms:** the
2026-07-05 self-reasoning gap audit (`notes/research_self_reasoning_capability_gap_2026-07-05.md`) explicitly named
the missing piece as "a deeper substrate-native VET/entailment-checking capability (**numeric threshold logic**)."
That is precisely subtract+compare — "is this retrieval margin above threshold," "is confidence >= 0.7," "does
claim X's numeric field exceed claim Y's" — not multiplication. Exact-equality (already proven, HARD_PASS) tells the
substrate *same vs different*; compare tells it *which is bigger / does this satisfy a bound* — the missing
ingredient for real VET/threshold logic over its own cert-ledger. Multiply is a genuine next rung for the broader
"core mathematics" vision (arithmetic word problems, the 2026-06-23 drill's compound-predicate goal), but it is
honestly a **parallel**, not a **prerequisite**, track relative to self-reasoning.

---

## CHEAP DECISIVE TEST (one line per candidate cell)

- **Subtract:** does `bind(enc(a), conj(enc(b)))` decode to exactly `(a-b) mod M` for random `a,b` across all 3
  already-proven moduli regimes, and does `bind(enc(a), conj(enc(a)))` decode to exactly 0 (additive-inverse
  identity)?
- **Compare:** does `sign((a-b) mod M vs M/2)` correctly recover `a>=b` / `a<b` for >=0.95 of trials when
  `|a-b| < M/2` is respected, AND does a deliberate out-of-range control trial (`|a-b| >= M/2`) get flagged/caught
  rather than silently mis-signed?
- **Multiply:** does decode-one-operand + exponentiate-the-other + CRT-decode achieve >=0.90 exact-match on `a*b mod M`
  across >=3 all-prime moduli regimes, with a random-exponent control (exponentiate by a WRONG decoded residue) and
  a non-prime-modulus control (deliberately reuse a composite modulus) both collapsing toward 0 (confirms
  prime-cyclicity is load-bearing, not incidental)?

---

## FALSIFIABLE PREDICTIONS (HARD-PASS / HARD-FAIL)

1. **Subtraction is exact via conjugate-phasor bind.**
   HARD-PASS: exact-match >=0.99 across all 3 regimes, cv<=0.10, additive-inverse identity holds exactly.
   HARD-FAIL: <0.90 at any regime (would indicate a sign-convention bug, not a mechanism failure — group inverse of
   an exact homomorphism cannot genuinely fail).
   P_deflated = **0.85**.

2. **Half-range sign detection correctly recovers ordering when the dynamic-range convention is respected.**
   HARD-PASS: sign-accuracy >=0.95 when `|a-b| < M/2` is enforced by the trial generator; the deliberate
   out-of-range control is either explicitly flagged as invalid OR its silent-wrong-sign rate is reported (not
   buried) as a named limitation.
   HARD-FAIL: sign-accuracy <0.70 even within the valid dynamic range (would mean the CRT-decode-then-threshold
   trick does not transfer cleanly at substrate scale), OR the out-of-range control silently passes undetected in
   >50% of violating trials without being reported.
   P_deflated = **0.45** (capped novel-synthesis; cross-field borrow, no VSA precedent, though textbook in classical
   RNS arithmetic).

3. **Multiplication via decode-then-exponentiate is exact under all-prime moduli.**
   HARD-PASS: exact-match >=0.90 across >=3 all-prime moduli regimes, cv<=0.10; random-exponent control and
   composite-modulus control both collapse to <=0.15.
   HARD-FAIL: exact-match <0.60 at any regime, OR either control fails to collapse (>=0.40) — would indicate the
   prime-cyclicity requirement is not actually load-bearing at substrate scale, or a leak in the anti-base
   correction.
   P_deflated = **0.40** (mechanism is named/citable in the primary reference, but zero in-substrate precedent for
   this specific operator, first-time all-prime moduli selection, and the asymmetric decode-mid-pipeline step is a
   genuinely new pipeline shape relative to the pure-vector add cell).

4. **Discrete-log (LNS) re-encoding is NOT the right multiplication route for this substrate** (a rejected-alternative
   claim, reported for completeness).
   This is a structural argument, not slated for its own cell: adopting LNS/discrete-log encoding would require a
   Zech's-logarithm table to restore addition in log-domain, i.e. would trade the just-proven FREE exact-add
   mechanism for a table-lookup-dependent one. P = **0.80** that this structural argument holds (i.e. that the
   decode-then-exponentiate `star` operator remains the better-fitted choice) — not fully novel-synthesis-capped
   since it is a comparative architecture judgment grounded directly in the (now lit-confirmed) mechanics of both
   options, not an untested empirical claim.

---

## CROSS-THREAD SYNTHESIS

- **With `exp_math_rns_add_chain_v1` (HARD_PASS, verified above):** that cell certified the exact additive group
  homomorphism this entire drill's mechanism sketches build on (subtract = additive inverse of the SAME group;
  compare = threshold-test on the SAME group's CRT-decode; multiply = a SECOND, independent operator layered on the
  SAME base encoding). No thread here contradicts or revises the add cell's own result — this is a pure extension.
- **With `notes/research_math_capability_translation_first_cell_2026-07-05.md` (parent design note):** that note's
  cross-thread synthesis flagged the 2026-06-23 drill's "500-1000 line joint add+multiply+compare RHC" estimate as
  scoped to the HARDER joint problem, and predicted add-only would come in at ~100-200 lines (confirmed: it landed
  HARD_PASS). This note extends the same scope-narrowing pattern: multiply-alone (now that the exact mechanism is
  identified from the primary paper) narrows further to ~150-250 lines, and compare-alone (a genuinely separate,
  previously-undiscussed operation) narrows to ~50-100 lines — the JOINT estimate was pessimistic largely because it
  bundled three operations of very different actual cost, not because any single one is as expensive as feared.
- **With `notes/research_self_reasoning_capability_gap_2026-07-05.md` (self-VET gap audit):** that note explicitly
  named "numeric threshold logic" as the missing ingredient for substrate-native self-consistency-checking beyond
  exact-match retrieval, with "no active math-scoping doc found on disk this session." This note IS that scoping —
  compare (rank 2) is the concrete mechanism that closes the named gap, at low cost (~50-100 lines, high reuse).
- **With the VSA/HDC literature itself:** the lit-scan's clearest finding is that comparison/ordering is a genuine
  gap in the field, not just in this substrate — no VSA/HDC paper found defines an inequality operator on
  residue/phasor-encoded numbers. If the substrate's compare cell HARD_PASSes, this would be a legitimate
  substrate-novel contribution (a first-of-its-kind operator in this representation family), not merely
  reproducing a known result — worth flagging to Strategy as a potential differentiator, though the P_deflated=0.45
  cap on prediction #2 reflects that this is exactly the kind of claim requiring empirical confirmation before any
  such framing.
- **With the brain-grounding thread:** grid cells (Sreenivasan & Fiete 2011) ground addition/addressing (already
  cited, already used). For multiplication, the closest literal brain analog surfaced by lit-scan is **not** grid
  cells but log-polar cortical retinotopic mapping (Schwartz 1980) and the Weber-Fechner/logarithmic-magnitude
  tradition (Dehaene 2003) — both real, mainstream-but-contested findings about logarithmic/ratio-scaled neural
  codes. Because this drill recommends the decode-then-exponentiate `star` operator (not a log-domain re-encoding),
  these brain findings are **not directly load-bearing** for the recommended multiply mechanism — they would only
  become relevant if a future drill revisits the (rejected-for-now) discrete-log route. Reported honestly as a
  non-applicable brain-grounding lead, not stretched to fit.
- **With the USER core-mathematics strategic vision:** consistent with the parent note's framing, these three cells
  remain near-term, concrete, standard-arithmetic-primitive cells — not a claim toward "substrate discovers new
  mathematics" (that stays long-horizon, per the existing memory framing). The genuine connection to the
  self-improvement north star runs through compare (rank 2), specifically, not through multiply.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- **If subtract + compare both HARD_PASS (likely, low cost):** the substrate gains a complete `{+, -, ==, <, <=, >,
  >=}` numeric primitive set — the minimum needed to express real VET/threshold logic over its own cert-ledger
  ("is claim A's confidence >= claim B's," "does this retrieval margin clear the discriminator floor," "rank these
  N candidate claims") without any external Python script doing that comparison on its behalf. This is the concrete
  next step in closing the "ALL substrate self-reasoning today is external" gap named in the 07-05 audit.
- **If multiply HARD_PASSes:** the substrate gains standalone exact multiplication, completing calculator-class
  arithmetic (`+, -, x, compare`) and unlocking compound natural-language-arithmetic predicates ("X earned twice Y,"
  scaling/proportion word problems) from the 2026-06-23 drill's compound-predicate goal, at the narrowed ~150-250
  line cost rather than the originally-feared full-RHC build.
- **If compare's out-of-range control reveals the silent-wrong-sign failure mode is common at realistic operand
  ranges:** this would be an important, prominently-reported negative — it would mean any downstream self-VET use
  of comparison needs an explicit dynamic-range guard (a real engineering requirement, not a rare edge case), and
  should gate whether compare ships as a "safe to compose" primitive or a "use with an explicit range-check wrapper"
  primitive.
- **Cap_map row candidate:** if subtract+compare HARD_PASS, this is grounds for Strategy to extend whatever
  `cap_math_*` row the add cell opens to include a `numeric_threshold_logic` sub-capability distinct from
  arithmetic-composition — Strategy decides, research does not modify cap_map.

---

## CITATIONS (verified, this drill's external count = 38 across 4 lit-scans; re-confirms 3 sources already cited in
the parent note, marked *)

**Lit-scan 1 — Logarithmic Number Systems / Zech's logarithm / discrete-log multiplication (15 sources):**
1. Zech's logarithm — Wikipedia (Zech 1849, *Tafeln der Additions- und Subtractions-Logarithmen*; Jacobi ~1846 prior use)
2. "Some Comments on Zech's Logarithms" — ResearchGate 3077582
3. "A method for computing addition tables in GF(p^n)" (Corresp.) — IEEE Xplore doc 1056178
4. "Interpolation of the Zech's Logarithm: Explicit Forms" — Springer 10.1007/978-3-030-84122-5_33
5. Irish logarithm — Wikipedia (Ludgate's related mechanical-multiplication index system)
6. Logarithmic number system — Wikipedia
7. Alam, S.A., Garland, J., Gregg, D. (2021). "Low-precision Logarithmic Number Systems: Beyond Base-2."
   arXiv:2102.06681
8. Parhami, B. "Computing with Logarithmic Number System Arithmetic" — UCSB ECE preprint
9. "Logarithmic Number System" — *Arithmetic Circuits for DSP Applications*, Wiley, ch. 7
10. Primitive root modulo n — Wikipedia (existence theorem: n in {1,2,4,p^k,2p^k})
11. Multiplicative group of integers modulo n — Wikipedia (Z/2^kZ non-cyclic structure for k>=3)
12. UC Irvine Math 180B lecture notes — "Primitive Roots, Indices and the Discrete Logarithm"
13. Index calculus algorithm — Wikipedia
14. ellipticnews blog — "What on earth is 'index calculus'?" (terminology-disambiguation source)
15. Claus Diem (U. Leipzig) — "What is Index Calculus?" talk slides

**Lit-scan 2 — Residue Number System magnitude comparison (14 sources):**
16. Szabó, N.S. & Tanaka, R.I. (1967). *Residue Arithmetic and its Applications to Computer Technology*. McGraw-Hill.
17. Residue number system — Wikipedia
18. Griffin, Tudor & Wigley. "The Mixed-Radix Chinese Remainder Theorem and Its Applications to Residue Comparison."
19. "An Algorithm for Magnitude Comparison in RNS based on Mixed-Radix Conversion II."
20. Akushsky, Burcev & Pak (1977). "A new positional characteristic of non-positional codes and its application."
    *Coding Theory and Optimization of Complex Systems*, Nauka, Alma-Ata.
21. Dimauro, Impedovo & Pirlo (1993). "A new magnitude function for fast numbers comparison in the residue number
    system." *IEEE Trans. Computers.*
22. Dimauro, Impedovo & Pirlo — follow-up, "RNS architectures for the implementation of the diagonal function."
23. Hung, C.Y. & Parhami, B. (1994). "An approximate sign detection method for residue numbers and its application
    to RNS division." *Computers & Mathematics with Applications* 27(4):23-35.
24. "The Study of Monotonic Core Functions and Their Use to Build RNS Number Comparators." MDPI Electronics
    10(9):1041.
25. "RNS Number Comparator Based on a Modified Diagonal Function." MDPI Electronics 9(11):1784.
26. "Construction of Akushsky Core Functions Without Critical Cores." MDPI Mathematics 12(21):3399.
27. "Sign Detection and Signed Integer Comparison for the 3-Moduli Set {2^n +/-1, 2^{n+k}}."
28. "Residue Number System Comparison revisited, a software perspective." arXiv:2605.18415.
29. "A New Algorithm to Compare the Magnitude of Two RNS Numbers." arXiv:1612.09168.

**Lit-scan 3 — brain/psychophysics logarithmic-magnitude coding (9 sources):**
30. Schwartz, E.L. (1980). "Computational anatomy and functional architecture of striate cortex: A spatial mapping
    approach to perceptual coding." *Vision Research* 20(8).
31. Schwartz, E.L. (1981). "Cortical anatomy, size invariance, and spatial frequency analysis." *Perception.*
32. Fechner, G. (1860). *Elemente der Psychophysik.*
33. Stevens, S.S. (1957). "On the psychophysical law." *Psychological Review* 64(3).
34. Dehaene, S. (2003). "The neural basis of the Weber-Fechner law: a logarithmic mental number line." *Trends in
    Cognitive Sciences* 7(4):145-147.
35. Nieder, A. & Miller, E.K. (2003). (monkey number-tuning data, cited within Dehaene 2003's discussion.)
36. Gallistel, C.R. & Gelman, R. (1992). (linear-scale-with-scalar-variability alternative account.)
37. Greenwood, D.D. (1961). "Critical bandwidth and the frequency coordinates of the basilar membrane." *J. Acoust.
    Soc. Am.* 33(10):1344-1356.
38. Greenwood, D.D. (1990). "A cochlear frequency-position function for several species — 29 years later." *J.
    Acoust. Soc. Am.* 87(6):2592-2605.

**Lit-scan 4 — VSA/residue-HD multiplication & comparison operators (re-confirms 3 already-cited* + 1 new):**
- Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen (2024). *Neural Computation*; arXiv:2311.04872. *
  (re-read specifically for the `star`/multiplication operator's mechanics, not just the addition result already
  used by the landed cell.)
- Hanley, Tomkins-Flanagan & Kelly (2025). "Hey Pentti, We Did (More of) It! A Vector-Symbolic Lisp With Residue
  Arithmetic." arXiv:2511.08767. *
- qFHRR: "Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic."
  arXiv:2604.25939. *
- Frady, Kent, Sommer, Olshausen. "Integer Factorization with Compositional Distributed Representations."
  arXiv:2203.00920. (NEW — the resonator-network decode subroutine the `star` operator leans on.)

Both lit-scan 2's finding that comparison/ordering is entirely absent from VSA/HDC literature, and lit-scan 4's
direct confirmation of exactly how `star` works (decode-then-exponentiate, prime-moduli-required), are the two
most decision-relevant findings of this drill — both independently verified by a lit-scan reading the specific
named source, not inferred from the parent note's prior general citation of the same paper.

---

## PRE-REGISTERED HARD-PASS / HARD-FAIL THRESHOLDS (summary table for future exp_dev pickup)

| Cell | HARD-PASS | HARD-FAIL |
|---|---|---|
| `exp_math_rns_subtract_conjugate_v1` | exact-match >=0.99, cv<=0.10, all 3 regimes; additive-inverse identity exact | <0.90 at any regime |
| `exp_math_rns_compare_halfrange_v1` | sign-accuracy >=0.95 within valid range; out-of-range control explicitly flagged/reported | sign-accuracy <0.70 within valid range, OR silent-wrong-sign rate on out-of-range control unreported |
| `exp_math_rns_multiply_decode_exponentiate_v1` | exact-match >=0.90, cv<=0.10, >=3 all-prime regimes; random-exponent + composite-modulus controls both <=0.15 | exact-match <0.60 at any regime, OR either control >=0.40 (leak / non-load-bearing prime constraint) |

Autonomy note: exp_dev owns exact grid points, seed counts, prime-moduli selection, queue routing, and timeout for
all three cells per [[feedback-no-experiment-design-in-prompts]]-equivalent discipline (this note names mechanism +
bands, not implementation minutiae). All three are LOCAL-CPU-feasible (numpy-scale, no GPU), same class as the
landed add cell.

---

*Research complete 2026-07-05. Internal scour: full read of `experiments/exp_math_rns_add_chain_v1.py` and its
landed `metrics.json` (verified off-disk before any claim), plus the parent design note, before external dispatch.
4 parallel Sonnet lit-scans (LNS/Zech-log; RNS comparison; brain log-magnitude coding; VSA/RHC multiplication-and-
comparison), generic terms only, no substrate-novel mechanism names off-platform. Lit-scan calibration applied
(deflate 0.15-0.25; novel-synthesis cap 0.50 on predictions 2 and 3; prediction 1 exempted as a non-novel corollary
of an already-exact-verified homomorphism, matching the parent note's own carve-out precedent). HARD-FAIL
thresholds mandatory and specified for every prediction. Design only, per Director instruction — no dispatch, no
routing files (USER-locked ferry-deprecation override; all actionable content delivered in this note).*
