# 5x Convergence Drill — Memory Goal: Exact Spec + Brain Mechanism

**Filed by:** research (Opus synthesis of 5 parallel Sonnet lit-scans, generic-math-terms-only per query-privacy)
**Date:** 2026-07-05
**Scope:** Constructive build spec for robust glass-box associative memory. NOT a vs-LLM comparison. Hub-rescue result (exp_deep_reasoning_hub_robustness_v1) treated as a GIVEN data point per dispatch instructions — another agent is VET-ing it; this note does not re-verify it, only reasons about what it implies and what comes next.

---

## HEADLINE

Five independent literatures (hippocampal neuroscience, cognitive psychology, VSA/HDC theory, modern ML associative memory, information theory) converge on **the same load-bearing mechanism**: protect a compact, unique **index/pointer** to a memory rather than trying to make raw superposed/bundled/associative-strength retrieval robust directly. This is *exactly* the shape of our own empirical hub-rescue win (PROTECTED/INDEX binding: deg5+ recovery 0.261→0.727). The brain has a 50-year-old, heavily-replicated existence proof for this exact fix (hippocampal indexing theory). The capacity ceiling is NOT a wall at practical scale — real information-theoretic walls (Gardner/Cover ≈2N) sit far above where we or biology currently operate; the gap between "typical practice" and "the wall" is compute/engineering cost, not physics. The genuine open gap: nobody (biology, VSA literature, or us) has published what happens to iterative-resonator-style cleanup specifically under shared/reused (hub) factors, and nobody has tested whether protecting hubs taxes raw non-hub capacity. That is the next decisive experiment.

---

## A. WHAT WE WANT — exact spec + measurable success criteria

**Functional requirement (first-pass, sharpened from user's opening spec):**
Given a substrate at dimension N, store M distinct memory atoms bound/composed via algebra (bind/unbind/bundle), such that:
1. Any stored atom is retrievable by content-addressed query, INCLUDING atoms with high "degree" (many other stored atoms reference/bind-through them — the hub case).
2. Bind/unbind/bundle algebra round-trips reliably on REAL stored atoms (not synthetic toy vectors).
3. Every stored memory is inspectable (decomposable into constituent atoms) and editable (swap one binding without full retrain) — glass-box, not a black box.
4. Degradation under load is graceful (soft cost curve), not a cliff, up to a pre-registered capacity target.

**MVP success criteria (numbers, functional-requirement-first):**
| Metric | MVP floor | Rationale |
|---|---|---|
| deg1 (leaf) exact recall | ≥0.95 | Already met: 1.0 per algebra-on-real-atoms (a97751df) |
| deg5+ (hub) exact recall, WITH protection | ≥0.65-0.70 | Already met once: 0.727 per hub-rescue (unverified generalization — see decisive test) |
| deg5+ (hub) exact recall, WITHOUT protection | n/a (baseline) | Measured 0.21-0.261 — this is the problem statement, not a target |
| Bind/unbind/bundle round-trip fidelity, non-hub atoms | ≥0.95 | Matches existing algebra-gate = 1.000 result |
| Bind/unbind/bundle round-trip fidelity, protected hub atoms | ≥0.70 | UNTESTED — flagged gap |
| Capacity M/N at graceful degradation | ≥0.30 | Matches our own measured capacity_alpha ≈0.30 at N=16384 (PROT-022, CF-RPE/Hebbian consistent 3 seeds) |
| Inspectability | decompose any bundle → constituent (byte,position) atoms | Already validated (`decompose_K_cliff`) |
| Editability | swap one binding via residual+rebind | Already validated but not stress-tested (no multi-seed, no query-integration test) |

**"Done" (full spec):**
- Capacity-scaled associative memory with graceful degradation characterized ACROSS the full hub-degree spectrum (deg1 through deg20+, not just a deg5+ bucket), at loads approaching the measured capacity_alpha ceiling, with the protection scheme active and its capacity *cost* quantified.
- Multi-seed, query-integration-tested editing (not demo-only).
- An explicit, quantified answer to "is our current operating point closer to the classical-Hopfield-type cost curve (~0.138N) or to the true combinatorial wall (~2N)?" — see section F.

---

## B. HOW THE BRAIN DOES IT — existence proof, concrete mechanism

The brain unambiguously solves this class of problem (you retrieve facts about "home," your own name, or any other concept referenced by thousands of memories, without catastrophic interference) using a specific, well-characterized circuit:

1. **Dentate gyrus pattern separation.** DG has ~5-10x more granule cells than downstream CA3, but only ~2-5% fire per input — a sparse random expansion recode that orthogonalizes overlapping inputs *before* they reach the associative store. (Marr 1971; O'Reilly & McClelland 1994, *Hippocampus*; Yassa & Stark 2011, *Trends Neurosci*; Knierim & Neunuebel 2016.)
2. **CA3 attractor pattern completion.** Dense recurrent collaterals form a Hopfield-like autoassociative network that reconstructs a full pattern from a partial cue, operating on the *already-separated* sparse DG codes as keys. Theoretical capacity ≈ connectivity / sparseness², i.e. sparser codes buy much higher capacity for fixed synapse count. (Marr 1971; Treves & Rolls 1994; Rolls 2007/2013.)
3. **Complementary Learning Systems (CLS).** Two systems, not one: fast/sparse/pattern-separated hippocampal encoding for individual episodes, slow/distributed/overlapping cortical learning for shared statistical structure, linked by offline replay. This exists specifically because a single high-plasticity system would let new episodes sharing a feature with an old one overwrite it (catastrophic interference). (McClelland, McNaughton & O'Reilly 1995, *Psych Review*; O'Reilly et al. 2014 update.)
4. **Hippocampal INDEXING theory — the critical mechanism.** Teyler & DiScenna (1986); Teyler & Rudy (2007 update): *the hippocampus does not store the content of an experience — it stores a sparse, pattern-separated INDEX that points to the distributed neocortical ensembles holding the actual content.* Two episodes sharing a hub feature get **distinct indices** even though they point to overlapping cortical content — interference is confined to the cheap, sparse, easily-separated index layer and never propagates into the expensive, shared content representation. This is the direct biological analog of "protect the index, not the content."
5. **Cognitive-science mirror (independent behavioral confirmation).** The fan effect (Anderson 1974: retrieval slows as more facts attach to one concept) is *not* rescued by raw associative strength — it is rescued by **integrating facts into one coherent representation** or by a **distinctive retrieval cue** (the "cue-overload principle": a cue's effectiveness is inversely related to how many items are attached to it). Famous/highly-familiar concepts show the *fastest* retrieval of all conditions specifically because rich pre-existing integrated knowledge protects new facts — the opposite of naive fan-dilution. (Anderson & Reder 1999; Myers/Smith-Adams-Schorr integration studies; Teyler/Rudy indexing theory as the plausible neural implementation of this behavioral pattern — a strong structural analogy, not directly co-tested.)

**Existence-proof framing:** because the brain demonstrably handles concepts with orders-of-magnitude more associations than any lab fan-effect study tests (a familiar name, a home address, common function words), and does so via index/content separation, this is not a speculative target — it's a floor. Any substrate mechanism reproducing this separation should, in principle, scale at least as far as biology does.

---

## C. 5x CONVERGENCE — load-bearing consensus + divergence

**Convergent mechanism (5/5 angles, independently arrived at):**

| Angle | Convergent finding |
|---|---|
| Neuroscience | Hippocampal index (sparse, pattern-separated) points to distributed cortical content; interference confined to index layer (Teyler & Rudy) |
| Cognitive science | Fan effect rescued by integration/distinctive cue, NOT raw associative strength — same "separate the pointer from the content" logic at the behavioral level |
| VSA/HDC | Rotation/key-seeded "protected" binding (bind content to a unique orthogonal-per-role index) is architecturally exact regardless of reuse frequency; plain bundling is NOT — Clarkson, Ubaru & Yang (2023, arXiv:2301.10352) give the explicit quantitative form: **dimension requirement scales as O(K²)** in K = an item's reuse/hub-degree. This is a formal statement of "plain superposition punishes hubs quadratically" |
| Modern ML | DNC's usage/allocation-gated write addressing and the "attention sink" literature (Xiao et al. 2023) both special-case high-traffic slots as a structurally distinct, protected class rather than letting them compete on equal footing with ordinary content |
| Info theory | Crosstalk SNR ~ √(N/M) is a smooth, continuous degradation with no inherent discontinuity — it is DESIGNED to be pushed back by architecture (redundancy, higher-order energy, protected addressing), which is exactly what index-protection does |

**This matches our own empirical result exactly.** PROTECTED/INDEX binding: deg5+ recovery 0.261→0.727 (+0.466) is the substrate independently re-discovering the same fix biology uses. That convergence is the single strongest finding of this drill — treat it as elevated-confidence (not proof, but a genuine cross-validated direction), subject to the calibration cap below.

**Divergence / genuine gaps (important — do not paper over):**

1. **Iterative resonator not helping hubs (+0.056 only) has NO direct precedent either way in the VSA literature.** The VSA lit-scan explicitly found no paper testing resonator/factorizer behavior when a factor is shared across many simultaneously-factorized composites — a real literature gap, not a refutation.
2. **But Modern-Hopfield theory supplies an analogous explanation nobody asked for directly:** correlated/clustered patterns in classical and dense Hopfield networks produce a combinatorial proliferation of spurious mixture-state attractors (~3^p growth with pattern count p). A resonator network IS an iterative attractor-cleanup process; a hub factor shared across many bindings is exactly the "correlated pattern cluster" condition that breeds spurious attractors. This is a genuine cross-domain synthesis produced by this drill (Modern-Hopfield correlated-pattern theory → predicts resonator-on-hub underperformance) that no single lit-scan angle produced alone. Treat as a plausible mechanism for the resonator null result, not a confirmed one.
3. **Cognitive-science "integration into one coherent unit" may be a DISTINCT mechanism from pure indexing**, not just a restatement of it. Indexing separates pointer from content; integration merges multiple facts about a hub into a single consolidated representation. These are complementary, not identical — worth treating as a second candidate build (a "consolidated hub atom" that pre-merges facts about a hub before storage) alongside protected/index binding, rather than assuming one subsumes the other.
4. **MoE/product-key literature diverges from the index-protection story** — those fixes redistribute traffic/expand addressable space rather than protecting content; useful as evidence that "hub congestion" is a recognized cross-architecture failure mode, but not evidence for our specific fix.

---

## D. AUGMENT BEYOND BIOLOGY — where high-energy compute exceeds sparse biological capacity

The information-theory scan gives concrete, quotable numbers at N=8192 (order-of-magnitude anchors from published scaling laws, not precise substrate-specific predictions):

- **True combinatorial wall** (Gardner/Cover counting bound, αc=2): ≈**16,000** associations. No amount of compute rescues past this — genuine information-theoretic converse (matches Θ(k log(n/k)) sparse-recovery lower bound, Do Ba/Indyk/Price/Woodruff 2010).
- **Classical Hopfield-type quadratic-energy cost curve** (αc≈0.138, Amit-Gutfreund-Sompolinsky): ≈**1,130**. This is an architecture-specific cost, NOT a wall — modern dense/higher-order energy functions (Krotov & Hopfield 2016; Ramsauer et al. 2020) provably push capacity toward exponential-in-N, showing 0.138N was always a cost of the *specific quadratic write rule*, not an information floor.
- **Typical sparse biological/VSA operating point:** tens-to-low-hundreds of items at N~10,000 (Gallant & Okaywe 2013; Frady/Kleyko/Sommer-style bundling curves) — biology runs far below even the conservative Hopfield figure because DG-style sparse coding (2-5% activity) is optimized for *metabolic* efficiency, not for approaching the information wall.
- **Our own measured operating point:** capacity_alpha ≈**0.30** at N=16384 (PROT-022, consistent across 3 seeds, CF-RPE ≈ Hebbian, delta=0.002) → at N=8192 this projects to ≈**2,458** items. That is already ~2.2x above the classical-Hopfield reference and roughly 1 order of magnitude above typical sparse-VSA practice, while still ~6.7x below the hard combinatorial wall.

**Implication:** we are NOT metabolically constrained the way biology is. Levers biology cannot afford but we can, all consistent with our own already-validated engineering wins:
- Higher-order / denser energy functions (our M3/M5 spec already lists n=3 cubic-tensor writes, O(N²) capacity per substrate).
- Algebraic redundancy / erasure coding (already HARD_PASS in our system: PP-354 FHRR Reed-Solomon parity recovers lost shards at recall=1.000).
- More cleanup iterations, higher precision (float32/64) — biology runs on noisy, low-precision spiking hardware; we don't have to.
- Wider N and index-dimension budgets specifically reserved for protection (a form of "spend compute, not cleverness," which biology structurally cannot do).

**Efficient-sparse baseline stays the fallback.** DG-style sparse pattern separation is the guaranteed-safe, low-compute reference point (our current write scheme already beats it). High-energy augmentation is the stretch goal toward the wall, not a replacement for having a working sparse baseline first.

---

## E. SUBSTRATE FIT + FIRST BUILD

**What we already have (data points, not re-litigated here):**
- Hub-rescue: PROTECTED/INDEX binding, deg5+ recovery 0.261→0.727 (+0.466); iterative resonator does not help (+0.056); collision_frac 0.85. (exp_deep_reasoning_hub_robustness_v1 — being VET'd elsewhere, treated as given.)
- Algebra-on-real-atoms (a97751df): deg1 exact=1.0, uniform-degree 0.74-0.92, deg5+ exact=0.21 WITHOUT protection (need top-k) — this is the baseline problem statement the hub-rescue fixes.
- Dense-projected key-value recall 0.83-0.96 (learned-key/attention-style addressing — structurally the modern-ML "attention as Hopfield retrieval" analog from Section C).
- Capacity_alpha ≈0.30 at N=16384, 3-seed-consistent (Hebbian ≈ CF-RPE, delta=0.002) — real measured capacity reference point.
- Engineering-wrapper precedent (PP-353 write-lock, PP-355 per-tier importance, PP-366 excitability-gating, PP-354 erasure coding): the substrate repeatedly demonstrates that a wrapper-layer policy — not a core algebra change — can deliver strong, HARD_PASS-grade results. PROTECTED/INDEX binding is exactly this class of fix, which is a good sign for feasibility (precedent for "wrapper fixes work here" already exists 4+ times).
- Mycorrhizal multi-hub rescue (MIDDLE_BAND, coverage 0.41→0.62): a partial prior attempt at multi-hub robustness; below HP gate, hub-count sweep and N-scaling still open — directly relevant prior art for the decisive test below.

**Exact remaining gap (three specific unknowns, not vague):**
1. Does PROTECTED/INDEX recall hold across the FULL hub-degree spectrum (deg2, 3, 4 — not just the deg5+ bucket already measured), and does it hold as load M grows toward the capacity_alpha≈0.30 ceiling, or does the fix itself degrade under load?
2. Does protecting hubs cost raw non-hub capacity? An index vector has its own dimension footprint — we have never measured capacity_alpha WITH protection active vs the unprotected baseline.
3. Does bind/unbind/bundle algebra fidelity hold on PROTECTED atoms specifically (not just plain atoms)? Algebra-gate=1.000 was measured on the unprotected write path; unknown on the protected path.

**Single most decisive next experiment (cheap CPU sweep, no GPU needed):**
A joint capacity × hub-degree sweep at N=8192 (or reuse the already-validated N=16384 config): vary load M/N ∈ {0.1, 0.2, 0.3, 0.4} × hub-degree bucket ∈ {1, 2, 3, 5, 10, 20+} with PROTECTED/INDEX binding active throughout, measuring (a) exact recall per (load, degree) cell, (b) bind/unbind/bundle round-trip fidelity per (load, degree) cell on protected atoms, (c) raw non-hub capacity_alpha with protection active vs the existing unprotected baseline. This single sweep directly answers all three gaps above and settles whether "hub-robust recall + reliable algebra, at capacity scale" (the MVP+full spec combined) holds or breaks, in one CPU-only run.

---

## Cheap decisive test (pre-registered, per contract)

**Test:** the joint capacity × hub-degree sweep described in Section E immediately above.

**HARD-PASS** (all three must hold):
- Hub (deg5+) recall ≥0.65 across ALL tested loads up to M/N=0.3 (protection doesn't collapse under realistic load, not just at the single load point already measured).
- Bind/unbind/bundle fidelity on protected hub atoms ≥0.70 at M/N=0.3.
- Non-hub capacity_alpha WITH protection active is within 10% of the unprotected baseline (≈0.30) — protection doesn't materially tax raw capacity.

**HARD-FAIL** (any one triggers):
- Hub recall drops below 0.40 at M/N=0.2 or lower (protection collapses well before the capacity ceiling — doesn't scale).
- Non-hub capacity_alpha drops by >25% with protection active (protection is too expensive — robs non-hub capacity to buy hub robustness).
- Algebra fidelity on protected atoms <0.40 (protection breaks the very algebra it's supposed to preserve).

**MIDDLE BAND:** partial pattern (e.g. holds at low load, degrades at higher load; or capacity cost lands in the 10-25% range — real but not disqualifying). Routes to a follow-up rescue: reserve a larger fixed index-dimension budget, or apply the already-HARD_PASS erasure-coding primitive (PP-354) to shore up the cost.

---

## Falsifiable predictions (summary table)

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| Protected hub recall generalizes across degree spectrum + load | ≥0.65 @ deg5+, all loads ≤0.3 M/N | <0.40 @ M/N≤0.2 |
| Protection preserves non-hub capacity | within 10% of unprotected 0.30 baseline | >25% capacity loss |
| Algebra survives on protected atoms | ≥0.70 round-trip fidelity | <0.40 round-trip fidelity |
| Resonator-hub failure explained by correlated-pattern spurious states (Modern-Hopfield analogy) | Spurious-state count measurably rises with hub reuse count K in a follow-up diagnostic | No relationship between K and spurious-state count found |

---

## Cross-thread synthesis

Connects to: algebra-on-real-atoms (a97751df, the baseline hub-collapse problem this rescue addresses); dense-projected KV recall cert (learned-key addressing precedent); capacity_alpha PROT-022 (N=16384 measurement, the capacity reference point this drill's decisive test extends); "Plate bound too pessimistic for sharded FHRR" memory anchor (consistent with our capacity_alpha already beating classical-Hopfield reference — the theoretical pessimism is being outperformed in practice, same direction as this drill's Section D); mycorrhizal multi-hub rescue (MIDDLE_BAND 0.41→0.62, direct prior-art precedent for the hub-count-sweep now proposed as the decisive test); PP-353/354/355/366 engineering-wrapper precedents (establishes that protected/index binding is the SAME CLASS of fix that has repeatedly HARD_PASSed here before). Does not touch or contradict "SUBSTRATE KNOWS NOTHING" — this is a structural/algebraic storage-and-retrieval question, orthogonal to semantic/world-knowledge claims.

---

## Substrate-product implications

An auditable, glass-box associative memory that is hub-robust via a brain-validated mechanism (protect the index, not the content) is a genuine, defensible product property: "every stored fact — including your most-referenced entities — is retrievable through a protected index, individually inspectable and editable, with a 50-year biological existence proof that this specific mechanism scales to hub-degree interference without collapse." This composes directly with the already-banked audit/deletion-certificate narrative (PP-9 and related cryptographic-deletion work): if the index IS the deletable unit, deleting an index while leaving distributed content unreachable is a cleaner mechanical match to "prove this fact was deleted" than deleting diffuse superposed content directly — worth flagging as a design constraint for whoever builds the deletion-cert integration next, not a promise it's already solved.

---

## F. HONEST RATING (no smoke — GOOD/MEDIOCRE/BAD)

**GOOD:** The mechanism convergence itself. Five independent literatures, searched separately with no shared framing, land on the same fix, and that fix is not merely theoretical — it already produced our best empirical hub result (0.261→0.727). This is the strongest, most load-bearing finding of the drill and it is GOOD, not smoke: it is corroborated by 50+ years of hippocampal literature (existence proof) and by an independent quantitative VSA result (Clarkson/Ubaru/Yang 2023's O(K²) scaling law explains WHY plain bundling fails hubs and WHY protection is the principled fix, not just an empirical accident).

**GOOD, with real headroom:** Capacity. Our measured operating point (capacity_alpha≈0.30, N=16384) already beats the classical-Hopfield-quadratic reference (0.138) and sits far below the true combinatorial wall (~2N). The remaining gap to "done" is compute/engineering cost (denser energy functions, redundancy, precision) — not a fundamental limit. Quantified at N=8192: wall≈16,384, classical-Hopfield-cost≈1,130, our-current-empirical≈2,458, typical-sparse-practice≈tens-hundreds.

**MEDIOCRE / genuinely unresolved (flag honestly, do not round up):**
- Whether PROTECTED/INDEX binding preserves raw non-hub capacity, or taxes it, is completely untested. This is a real unknown, not a formality — index vectors cost dimension budget somewhere.
- Whether the fix generalizes across the full degree spectrum (not just the single deg5+ bucket measured once) is untested.
- The resonator-doesn't-help-hubs result has no direct literature precedent either way — the Modern-Hopfield correlated-pattern explanation offered in Section C is a plausible analogy, not a verified mechanism. Per calibration discipline this stays capped, not elevated to a confirmed finding.
- Cognitive-science "integration" as a possibly-distinct second mechanism (Section C.3) is currently pure hypothesis — zero substrate-side testing.

**BAD, as a stated baseline (not a criticism — it's the honest starting point the rescue exists to fix):** unprotected hub recall (0.21-0.261 exact at deg5+) is genuinely bad in isolation. The story here is not "hubs are fine" — it's "hubs are bad by default, and one specific brain-grounded fix measurably rescues them once, pending generalization."

**Proven-vs-speculative split:**
- PROVEN: the brain solves hub-scale interference via index/content separation (hippocampal indexing theory, 1986-2020, heavily replicated, high confidence).
- PROVEN (provisionally — pending the separate VET already in progress, not re-litigated here): our own hub-rescue reproduces the same mechanism direction empirically, once, at one load point.
- SPECULATIVE: that protection generalizes across degree spectrum and load without taxing non-hub capacity; that cognitive-integration is a useful second, distinct mechanism for us; that resonator-hub failure is explained by correlated-pattern spurious-state proliferation specifically (plausible analogy only).

**Is the capacity limit a WALL or a compute cost?** Answered directly: at N=8192, there IS a genuine information-theoretic wall (Gardner/Cover, ≈2N≈16,384 — provably no compute rescues past this), but it sits ~6.7x above our current empirical operating point (≈2,458) and ~14x above the classical-Hopfield reference. Everything between "typical practice" and "the wall" is compute/engineering cost that high-energy non-biological compute is explicitly allowed to spend (per standing ground rule — bio-efficiency is a baseline/proof, not a constraint). The practical ceiling we should currently worry about is a cost curve, not a wall.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):** naive confidence in "the convergent mechanism is correct and sufficient" would run ~0.75-0.80 given 5/5 convergence plus an existing empirical hit. Deflating 0.15-0.25 for uncharted-regime lit-scan calibration, and capping novel-synthesis (the "this generalizes to full spec at scale" claim specifically, which is NOT yet validated) at 0.50 per rule:

**P_deflated = 0.50 (capped)** for "protected/index binding generalizes to hub-robust recall + reliable algebra at capacity scale" as a full-spec claim. Confidence in "the mechanism direction itself is correct" (not yet the full-spec generalization) is higher, ~0.65, but the capped number is the one that governs dispatch priority per rule.

---

## Citations (verified count)

52 distinct citations were surfaced across the 5 independent lit-scans, each with an author/year and, in the large majority of cases, a live URL fetched by the sub-agent via WebSearch/WebFetch (arXiv, PubMed, ScienceDirect, PLOS, Nature, Frontiers, NeurIPS proceedings). Honesty note on "verified": each sub-agent independently retrieved and cited its own sources; this synthesis did not re-fetch and independently cross-check every URL a second time, so treat these as single-source-verified (real, live, sub-agent-confirmed) rather than double-verified. Highest-value citations for follow-up reading if the decisive test needs deeper grounding:
- Teyler & DiScenna 1986 / Teyler & Rudy 2007 (hippocampal indexing theory — the core biological mechanism)
- Anderson 1974 / Anderson & Reder 1999 (fan effect + rescue-by-integration)
- Clarkson, Ubaru & Yang 2023, arXiv:2301.10352 (VSA capacity O(K²) scaling in hub-degree — direct formal match to our problem)
- Frady, Kent, Olshausen, Sommer 2020, arXiv:2007.03748 (resonator networks — the mechanism our own resonator-null-result concerns)
- Krotov & Hopfield 2016 / Ramsauer et al. 2020, arXiv:2008.02217 (dense/modern Hopfield capacity + correlated-pattern spurious states)
- Gardner 1988; Amit, Gutfreund & Sompolinsky 1985; Do Ba, Indyk, Price & Woodruff 2010 (the true vs. cost-curve capacity distinction underlying Section D/F)

---

## Next-drill candidate

Field: `network-science-graph-theory` (Tier-1b, adjacent to spin-glass/free-probability) — pool retrieval under realistic power-law hub-degree distributions is structurally a graph/expander-spectrum problem; a follow-up drill mapping our hub-degree buckets onto expander/Ramanujan spectral-gap bounds could give a theoretical prediction for the decisive test's expected shape before it's run. Second candidate: `sparse-coding-compressed-sensing` (Tier-1b) — direct match to Section D's capacity-wall-vs-cost-curve distinction, could sharpen the exact N=8192 numbers beyond the order-of-magnitude anchors used here.
