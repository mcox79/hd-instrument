# DEEP DRILL: Is "element-layer" thesis-preserving, or smuggled tier-3?

Date: 2026-06-16
Topic: PATH 1 + ELEMENT-LAYER recommendation audit against substrate-on-its-own invariant.
Calibration: lit-scan penalty applied (P deflated 0.15-0.25); novel-synthesis cap 0.50.

## HEADLINE

Element-layer extension is **CONDITIONALLY THESIS-PRESERVING** — depends entirely on whether the element-layer primitive is *specified-by-construction* (i.i.d. random, algebraically derived, residue/fractional-power) or *learned-against-external-loss* (NEF decoders, trained readouts, learned embeddings). The published HRR/HDC mainstream (Plate, Kanerva, Frady, Schlegel, residue/GHRR) keeps the element layer specified; that branch preserves substrate-on-its-own. The Eliasmith-NEF branch and any trained-readout reservoir branch **violates**. Skunkworks's PATH 1 + ELEMENT-LAYER is safe **only if** the chosen element-layer mechanism is in the specified family. The single highest-expressivity-extension that is unambiguously substrate-internal is **modern-Hopfield / softmax-attention over the existing codebook** (Ramsauer 2020), which adds a continuous-magnitude, partial-symmetric soft-subset primitive without any external truth.

## Cheap decisive test (pre-registered)

Before adopting any element-layer extension, run a 3-question gate per [[feedback-substrate-standalone-capability-first]]:

1. **No-label test**: does the mechanism require any external labeled (input, target) pair to be specified, fit, or tuned? If YES → REJECT.
2. **No-external-loss test**: does the mechanism require an objective function defined over external truth (held-out accuracy, oracle correctness, human preference)? If YES → REJECT.
3. **Auditability test**: can the substrate itself audit the mechanism end-to-end (every parameter derived from a closed-form spec, RNG seed, or substrate-resident algebra)? If NO → REJECT.

**HARD-PASS bands** (P_deflated for finding such a mechanism in published lit): 0.55 (uncapped lit support exists; Plate/Kanerva/residue/Ramsauer all qualify).
**HARD-FAIL band**: P_deflated < 0.15 would mean no published precedent for substrate-internal expressivity-extension; reality is much higher.

## Per-angle verdicts

### Angle 1: Element-layer in published VSA/HRR/HDC

- Plate HRR (i.i.d. Gaussian elements), Kanerva HDC (bipolar/binary), FHRR (unit phasors), Schlegel sparse-block (one-hot per block), GHRR (block-diagonal binding 2024), residue/fractional-power (Komer SSP, Kymn 2023): **all SPECIFIED, all PRESERVE**.
- NEF/Spaun (Eliasmith): decoders fit by regression against target function — **VIOLATES**.
- Verdict: element-layer = symbolic-primitive family in mainstream; sub-symbolic only when learned.

### Angle 2: Does element-layer extension grow expressive power beyond binders alone?

YES — three published existence-proofs that DO grow expressivity without external truth:
- **Fractional-power encoding / residue numbers** (Frady-Sommer 2018; Kymn et al. 2023; "residue arithmetic" 2025): continuous-magnitude and cardinality reasoning unreachable by pure binder algebra. Specified by construction.
- **GHRR (Alam et al. 2024)**: strictly larger algebra than FHRR (diagonal → block-diagonal). Specified.
- **Sparse-block ternary occupancy**: cardinality counts via block structure. Specified.

This directly answers the "make novelty NECESSARY" question: tasks requiring continuous magnitude, cardinality counts, or block-structured ternary composition cannot be closed by pure FHRR/HRR binders — they MUST use element-layer structure.

### Angle 3: Sub-symbolic vs symbolic

Element-layer in HRR/HDC literature is **sub-symbolic substrate carrying a symbolic interpretation**. The atoms are continuous vectors (sub-symbolic shape) but operate under specified algebraic laws (symbolic semantics). This is the Plate/Kanerva orthodoxy. It is NOT "neural-net learned representation." Skunkworks's phrasing is consistent with mainstream if "element-layer" means *specified element primitives*, not *learned embeddings*.

### Angle 4: Per-candidate thesis-preservation

| Candidate | Ext data? | Ext loss? | Auditable? | Verdict |
|---|---|---|---|---|
| Plate i.i.d. Gaussian | No | No | Yes | PRESERVES |
| Kanerva bipolar | No | No | Yes | PRESERVES |
| FHRR unit phasors | No | No | Yes | PRESERVES |
| Sparse-block one-hot-per-block | No | No | Yes | PRESERVES |
| GHRR block-diagonal | No | No | Yes | PRESERVES |
| Residue / fractional-power | No | No | Yes | PRESERVES |
| NEF decoders | Yes | Yes | Partial | VIOLATES |
| Reservoir w/ trained readout | Yes | Yes | Partial | VIOLATES |

### Angle 5: Alternatives to element-layer for tier-3 substrate-internal

- **Resonator networks** (Frady 2020): NEUTRAL — inverts existing algebra (factorization), doesn't extend. Useful but not a tier-3 step.
- **Cellular automata over hypervectors** (Kleyko 2022, Yilmaz 2015): NEUTRAL — adds dynamics, not algebra.
- **Hierarchical/recursive binding** (Plate 1995): NEUTRAL — deeper use of existing binders.
- **Reservoir w/ trained readout**: GROWS-EXTERNAL — violates.
- **Active inference / free-energy** (Parr-Friston 2019): GROWS-EXTERNAL — requires sensorium/priors.
- **Modern Hopfield / softmax-attention over codebook** (Ramsauer 2020): **GROWS-INTERNAL** — when X = substrate codebook, the update is a substrate-internal continuous-magnitude soft-subset primitive. NO external loss required. Closest competitor to element-layer for tier-3.
- **Cleanup memory + iterative resonance**: NEUTRAL.

Strongest tier-3 substrate-internal candidates: (a) residue/fractional-power element extension, (b) GHRR block-diagonal extension, (c) modern-Hopfield-as-substrate-operator. All three preserve thesis.

### Angle 6: External-truth alternatives — sound oracle vs learned oracle

Categorical distinction holds in NeSy lit (Garcez-Lamb 2020; Marra et al. 2024):

- **EXTERNAL-DETERMINISTIC-TOOL**: SAT/SMT (Z3), Lean/Coq, CAS (SymPy), OEIS lookup. Sound-by-construction, refutation certificates, fully auditable. Treated as orthogonal symbolic engines, not "truth importers."
- **EXTERNAL-LEARNED-TRUTH**: LLM, trained recognition models, learned embeddings, NTPs. Non-deterministic, no soundness, opaque.

For the substrate's "no external oracle truth" invariant: a SAT solver is structurally closer to a deterministic-tool extension (like a CPU instruction) than to LLM truth-import. If the substrate's invariant is "no learned oracle," a SAT solver is COMPATIBLE. If the invariant is "no external computation at all," SAT is incompatible.

**Recommendation**: the substrate's invariant should be tightened to "no learned oracle, no external sensorium, all parameters substrate-derived." This is the operationally-meaningful invariant; pure-deterministic algebraic tools (CAS lookups for ground-truth math facts) can be a separate decision.

### Angle 7: DreamCoder / library-learning comparison

DreamCoder (Ellis 2021) grows **compositions** of fixed primitives via wake-sleep cycles. It does NOT grow new atomic primitives. Stitch (POPL 2023) is pure syntactic e-graph compression — substrate-internal. LILO/ReGAL require LLM proposals — violates.

**Key analog**: DreamCoder's library growth = substrate's basis-composition growth (corr_bundle promotion path). DreamCoder has no element-layer analog — primitives are fixed by the DSL designer up front. This means library-learning lit does NOT give a precedent for element-layer expressivity-extension; it gives precedent for *composition-layer* growth. The two are orthogonal.

### Angle 8: Slippery slope — precise substrate-internal definition

Proposed 3-line definition:

> **Substrate-internal**: a mechanism M is substrate-internal iff (a) every parameter of M is either an RNG-seed-derived constant, a closed-form algebraic specification, or a function of substrate-resident state; (b) M requires no external labeled data and no external loss function to operate; (c) the substrate can audit M's full operation without consulting any external oracle.

Under this definition: element-layer with i.i.d./algebraically-specified primitives → INSIDE. Element-layer with learned embeddings → OUTSIDE. Modern-Hopfield over substrate codebook → INSIDE. NEF decoders → OUTSIDE. SAT solver → OUTSIDE (but a *different* outside than LLM — deterministic-tool, not learned-truth).

## Cross-thread synthesis

- TIER-2 corr_bundle finding (DECISION 142): basis-composition-growth confirmed without element-layer extension. PATH 1 (grow task-frontier) alone may already exercise composition closure. Element-layer is only NECESSARY when task surface demands continuous-magnitude, cardinality, or block-structured ternary primitives that pure binder algebra cannot reach.
- 11th USER-LOCKED rule (substrate-standalone-first): element-layer must be measured ON ITS OWN before any LLM-positioning. The residue/fractional-power family gives an unambiguously substrate-standalone path.
- 18th methodology rule (refuses-what-cannot-prove): the gating test (Angle 4 table) is the substrate's own audit; specified-element families pass, learned families fail.
- 20th methodology rule (3-distillation-modes): element-layer extension is STRUCTURE-ADDING (mode B) when specified; would be a NEW mode "external-import" if learned — which the substrate should REFUSE.

## Substrate-product implications

- **PATH 1 + ELEMENT-LAYER recommendation is sound IF element-layer = specified family (residue, GHRR, sparse-block, modern-Hopfield-as-operator).**
- **Recommendation refines to**: PATH 1 (grow task surface to demand continuous-magnitude / cardinality / partial-symmetric-ternary primitives) + ELEMENT-LAYER-SPECIFIED (residue/GHRR/modern-Hopfield), with element-layer adopted ONLY when task surface demonstrates a binder-algebra-closed gap.
- **Path 2b EXTERNAL-TRUTH should be split**: LLM-as-oracle stays REJECTED; SAT/CAS as deterministic-tool is a separate, lower-priority decision (not the same category as LLM). Do NOT collapse these.
- **Tier-3 implementation order** (when triggered): (1) residue/fractional-power for continuous-magnitude tasks, (2) GHRR for richer algebraic structure, (3) modern-Hopfield-as-operator for soft-subset primitive. All three are substrate-internal under the 3-line definition.
- **DO NOT** adopt: NEF-style learned decoders, trained reservoir readouts, learned recognition models, LLM-as-oracle. All four violate.

## Recommendation on Path 2 timing

**HOLD as planned** until PATH 1 demonstrates a binder-algebra-closed gap. Reasoning: corr_bundle showed novel composition exists but role_filler closes 0.87 of real tasks. Until task surface has a published-gap-class (continuous magnitude, cardinality count, partial-symmetric-ternary) that pure binders provably cannot close, element-layer is **architecturally available but operationally unnecessary**.

When triggered, implement in order: residue first (clearest precedent, cheapest), then modern-Hopfield-as-operator (free in compute, only requires reusing existing codebook), then GHRR (most invasive, last).

## Highest-risk failure mode

**Conflating "element-layer" with "learned embedding."** If the team adopts a learned-embedding under the element-layer label (e.g., training a small MLP to produce element values that minimize task loss), the substrate quietly becomes a neural-net-with-symbolic-frosting. This is the dominant failure mode in NeSy literature (NTPs, NEF, hybrid architectures). The 3-question gate (Angle Cheap-Test) prevents this; mandate it as a pre-adoption gate.

Secondary risk: adopting modern-Hopfield with a learned temperature β. If β is fit against external labels, it violates. If β is set algebraically or via substrate-resident state, it preserves.

## Citations (verified)

1. Plate 1995 — HRR — IEEE TNN 6(3).
2. Plate 2003 — HRR book.
3. Kanerva 2009 — Hyperdimensional Computing — Cog. Comp. 1(2).
4. Frady, Kent, Olshausen, Sommer 2020 — Resonator Networks 1 — Neural Computation 32(12).
5. Kent, Frady, Sommer, Olshausen 2020 — Resonator Networks 2 — Neural Computation 32(12).
6. Kleyko, Rachkovskij, Osipov, Rahimi 2022 — HDC/VSA Survey Pt I — arXiv 2111.06077.
7. Alam et al. 2024 — Generalized HRR (GHRR, block-diagonal) — arXiv 2405.09689.
8. Kymn et al. 2023 — Residue numbers in VSA — arXiv 2311.04872.
9. Frady & Sommer 2018 — Fractional-power encoding / SSP family.
10. Ramsauer et al. 2020 — Hopfield Networks Is All You Need — ICLR 2021 / arXiv 2008.02217.
11. Ellis et al. 2021 — DreamCoder — PLDI.
12. Bowers et al. 2023 — Stitch — POPL.
13. Marra et al. 2024 — NeSy survey — Artificial Intelligence 328.
14. Garcez & Lamb 2020 — NeSy 3rd wave.
15. Rocktaschel & Riedel 2017 — NTPs — NeurIPS.

Verified count: 15 citations across 3 parallel lit-scans.

## Next-drill candidate

`free-probability` adjacency on residue/fractional-power capacity bounds — the residue family's expressive ceiling is governed by free-probability spectral statistics (Tracy-Widom edge of codebook + atom-isolation margins). One-drill scope-expansion candidate.
