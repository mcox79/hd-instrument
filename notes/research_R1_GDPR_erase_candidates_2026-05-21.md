# Research R1 — GDPR-erase candidate mechanisms after anti-Hebbian / selective-anneal Mirage failure

**Topic.** Which mechanism family is the right GDPR-erase candidate after
anti-Hebbian rank-1 W edit and selective thermal annealing both passed argmax
but failed the four-probe Mirage battery (rank / norm / cos / paraphrase)?

**Date.** 2026-05-21

**Status.** Research note, two passes complete. Output: comparison across four
mechanism families; one concrete experimental design at the end. Routes to
Strategy + Experiment Dev (Bet 2 / E2 in `active_priorities.md`).

**Charter posture (REVISED 2026-05-21 post-audit).** Pass 1 originally relied
on in-repo synthesis + prior-knowledge citations without external lit scan;
post-audit subagent ran generic-math queries (no substrate fingerprint per
[[feedback-query-privacy-decomposition]]) and surfaced both citation errors
and missing 2024-26 prior art. The audit corrections section directly below
this header documents every load-bearing fix; the body of the note has been
patched inline. The structural argument (Kerdock + anti-Hebbian as Variant
2A.i) survives the audit; numerical predictions and one major prior-art claim
do not.

---

## AUDIT CORRECTIONS (2026-05-21, post-publication)

External-search audit run after the initial note landed. Findings split into
four categories. Body of note patched inline at the cited locations.

### Citation errors — load-bearing

- **Mirage paper arXiv ID was wrong.** The note repeatedly cited
  `arXiv:2502.11177` for "The Mirage of Model Editing." The actual paper is
  Wanli Yang et al., "The Mirage of Model Editing: Revisiting Evaluation in
  the Wild," **arXiv:2502.11177** (Feb 2025; v4 current). The ID
  `2503.06991` is a different paper entirely ("Are We Truly Forgetting?
  A Critical Re-examination of Machine Unlearning Evaluation Protocols").
  All Mirage citations in the body have been corrected.

- **The "four-probe battery (rank / norm / cos / paraphrase)" is NOT in the
  Mirage paper.** Mirage introduces QAEdit and WILD benchmarks and reports
  primarily on BERTScore, Exact Match, and LLM-as-a-Judge under realistic
  decoding. It does NOT define a four-probe battery with the specific
  rank/norm_ratio/cos/paraphrase_leak metrics, and does NOT set the < 5%
  paraphrase_leak threshold. Those probe definitions and threshold are
  **substrate-internal** (from `wave14p_erase_multiprobe` + Bet 2 criteria
  in `active_priorities.md`). The closest published analog is **MEMIT-CSK**
  (Gupta et al. EMNLP 2023, arXiv:2305.14956), which uses
  unaffected/affected neighborhood + affected paraphrase + affected reasoning
  dimensions. Attributions in the body have been corrected: the four probes
  are now labeled as "substrate-internal (per `wave14p_erase_multiprobe` and
  active_priorities Bet 2), with MEMIT-CSK as the closest published analog."

- **Demircigil et al. 2017 author list wrong.** Note had
  "Demircigil-Heusel-Löwer-Upfal-Krotov-Hopfield"; correct is
  **Demircigil, Heusel, Löwe, Upgang, Vermet** (J. Stat. Phys. 168, 2017,
  arXiv:1702.01929). Krotov and Hopfield are NOT authors on that paper —
  their related paper is Krotov & Hopfield 2016 "Dense Associative Memory
  for Pattern Recognition," NeurIPS. Both citations have been corrected;
  Krotov-Hopfield 2016 now has a separate entry.

### Numerical errors in Kerdock derivation

- **Inner-product magnitudes off by factor of 2.** Note claimed pairwise
  inner products |IP|/N ∈ {0, 1/64} for K(12) at length 4096. Authoritative
  result (Hammons-Kumar-Calderbank-Sloane-Solé 1994; Error Correction Zoo
  c/kerdock): Hamming distances d ∈ {0, 2^(m−1) − 2^((m−2)/2), 2^(m−1),
  2^(m−1) + 2^((m−2)/2), 2^m} translate via IP = N − 2d to **IP ∈ {0,
  ±2^((m+2)/2), ±2^m}**. For m=12: IP ∈ {0, ±128, ±4096}, so non-trivial
  **|IP|/N = 128/4096 = 1/32**, not 1/64. Every body reference to 1/64 has
  been changed to 1/32. The qualitative argument (structured, bounded
  cross-talk) is unchanged; the numerical predictions tighten by a factor
  of 2 in the wrong direction (cross-talk is twice as large as I claimed,
  but still well-bounded).

- **Inconsistent exponent in the Welch-bound formula.** Note had
  `2^((m+1)/2)` at line 64–65 and `2^((m+2)/2)` at line 278. The correct
  form is `2^((m+2)/2)` per Hammons 1994; both occurrences now match.

- **Kerdock minimum distance off by factor of 2.** Note claimed d_min ≈
  2^(m−1) − 2^((m−1)/2) ≈ 1984 for m=12. Correct formula for even m is
  d_min = 2^(m−1) − 2^((m−2)/2) = 2048 − 32 = **2016** for m=12. Body
  patched; paraphrase-distance argument tightens slightly in the
  substrate's favor (2016 > 1984).

### Missing prior art — substantially deflates novelty of Candidate 3'

- **AlphaEdit (Jiang et al., ICLR 2025 Outstanding Paper, arXiv:2410.02355)
  is essentially what the note proposed as "paraphrase-aware ROME"
  (Candidate 3').** AlphaEdit projects the rank-1 ROME update onto the
  null space of preserved-knowledge keys before applying. This is the
  structured form of what I proposed as "sampled-paraphrase constraint
  set." AlphaEdit reports scaling to 3000 sequential edits. **Candidate 3'
  is NOT a novel research direction; it is an instance of AlphaEdit.**
  Note has been revised to anchor Candidate 3' on AlphaEdit explicitly
  and to recommend AlphaEdit as a **direct baseline** in the experimental
  design — at least as important as Kerdock + anti-Hebbian, possibly more
  important because it requires no substrate restructuring.

- **r-ROME / "Rebuilding ROME"** (Gupta, Baskaran, Anumanchipalli EMNLP
  2024, arXiv:2403.07175) addresses ROME's "disabling edits" and model-
  collapse under sequential editing. The note treated ROME as a single
  monolithic Candidate 3; r-ROME is the corrected implementation and is
  what should actually be tested when "vanilla ROME" is invoked.

- **MUNKEY** (arXiv:2603.15033) is "unlearning by design" via key deletion
  in a memory-augmented transformer — the closest published analog to
  Candidate 4 (per-fact orthogonal subspace allocation). Strengthens the
  "this is a different product, not a substrate" framing of Candidate 4
  by giving it a concrete prior-art reference.

- **MEMIT-CSK-PROBE** (Gupta et al. EMNLP 2023, arXiv:2305.14956) has the
  multi-dimensional probe structure (unaffected/affected/paraphrase/reasoning)
  closer to the substrate's "four-probe battery" than Mirage does.

- **Hopfield unlearning analysis 2026** (Takeuchi-Takahashi-Kabashima,
  arXiv:2602.08428) — replica-method analysis of anti-Hebbian unlearning
  in Hopfield networks; directly relevant to the substrate's anti-Hebbian
  rank-1 erase characterization. Adds rigor to the
  Hopfield-Feinstein-Palmer 1983 lineage.

- **Certified Unlearning for Neural Networks** (2025, arXiv:2506.06985)
  and **Rewind-to-Delete** (2024, arXiv:2409.09778) extend Guo-Goldstein
  2019 (the note's citation 7) to non-convex models. Guo-Goldstein 2019
  is 6 years old; these are the current references.

- **ChainEdit** (arXiv:2507.08427) — RippleEdits successor with logical
  rule chains. The right citation for "ripple effects" if note wants a
  current reference.

- **"Benchmarking and Rethinking Knowledge Editing for LLMs"** (2025,
  arXiv:2505.18690) — independent confirmation of the Mirage finding from
  a different evaluation angle.

### Strategic reframing implied by audit

Two changes to the experimental-design recommendation in light of AlphaEdit's
existence:

1. **E2 should run BOTH Kerdock + anti-Hebbian (Variant 2A.i) AND AlphaEdit
   port** as parallel candidates, not just Kerdock alone. AlphaEdit is
   substrate-key-agnostic (works with the substrate's random ±1 keys, no
   re-structuring) and has published evidence of scaling to 3000 sequential
   edits. Kerdock + anti-Hebbian remains the cheaper-per-edit option IF
   substrate adopts structured keys. Each candidate is now `wave14g_erase_*`:
   - `wave14g_erase_kerdock_v1` (Variant 2A.i) — unchanged
   - `wave14g_erase_alphaedit_v1` (NEW) — null-space projected anti-Hebbian
     on substrate's existing random keys

2. **Probability estimates revised**: Kerdock 2A.i 40–55% (unchanged);
   AlphaEdit on random keys: 50–65% (higher than Kerdock because (a) it has
   published large-scale evidence and (b) doesn't require substrate
   restructuring, only an algorithm change). Combined: probability that
   GDPR-erase v3 lands ✅ this cycle ≈ 70–80% (P(neither passes) ≈ 25%).

### Brutal-honesty summary

The mechanism-level reasoning (anti-Hebbian neighborhood leakage; Welch-bound
cross-talk; block-orthogonal capacity tradeoff; charge-flipping as wrong tool)
held up under audit. Where the note failed: (1) sloppy citations attributed
substrate-internal constructs to external papers; (2) factor-of-2 arithmetic
errors in the Kerdock numerics; (3) misidentifying AlphaEdit's existence as
a novel proposal. The audit caught all three classes. The corrected note's
top recommendation is now AlphaEdit + Kerdock parallel testing, not Kerdock
alone.

---

## Why this question is hard — the math behind the substrate-internal four-probe failure

Substrate W is the classical Hebbian outer-product W = Σᵢ vᵢ kᵢᵀ. The
"erase fact e" operation needs to remove (vₑ, kₑ) from W while leaving every
kept (vⱼ, kⱼ) untouched as measured by ANY of the four substrate-internal
probes (per `wave14p_erase_multiprobe` and Bet 2 criteria in
`active_priorities.md`; closest published analog is MEMIT-CSK-PROBE,
arXiv:2305.14956, which uses unaffected/affected/paraphrase/reasoning
dimensions):

- argmax(W·k̃) ≠ vₑ for any probe k̃ near kₑ
- rank(vₑ in cleanup output of W·k̃) > 100
- ||W·kₑ|| / mean_j ||W·kⱼ|| < 0.15
- cos(predicted_v, vₑ) < 0.10 under correlated probes
- paraphrase_leak < 5% under Hamming-radius perturbations of kₑ

Anti-Hebbian rank-1 erase computes W' = W − vₑ kₑᵀ / N, which solves the
**single-key constraint** W'·kₑ = 0 exactly (modulo finite N). But what
matters for multi-probe survival is the behavior on the *neighborhood* of kₑ.
Decompose a paraphrase probe k̃ = kₑ cos θ + k⊥ sin θ where k⊥ ⊥ kₑ.
Then:

  W'·k̃ = W'·kₑ cos θ + W'·k⊥ sin θ = 0 + W'·k⊥ sin θ

For random ±1 keys, W'·k⊥ contains residual contributions from every kept
(vⱼ, kⱼ) because ⟨k⊥, kⱼ⟩ ≠ 0. Crucially, the *direction* of W'·k⊥ at small
θ is dominated by whichever kept pair has key most-aligned with k⊥. If any
kept kⱼ is structurally similar to kₑ (a paraphrase from the substrate's
point of view), W'·k̃ leaks back toward vₑ via that bridge. This is the
Mirage failure mode in mechanism terms: erasure is direction-specific,
neighborhood-leaky.

The fix has to either (a) engineer the keys so neighborhoods are clean,
(b) engineer the storage so subspaces are non-overlapping, or (c) compute
the erase direction adaptively rather than from a single-key constraint.
The four candidates in R1 each pick a different choice.

---

## Pass 1 — Survey of the four candidate families

### Candidate 1: Kerdock-coset structured-codebook + W edit

**The math.** Replace random ±1 keys with codewords drawn from the Kerdock
code construction. Kerdock(m) is a non-linear binary code of length 2^m
constructed via the Z₄-Gray map from a Z₄-linear code; its codewords have
pairwise inner products in {0, ±2^((m+2)/2)} after centering [CORRECTED
2026-05-21] (Hammons–Kumar–Calderbank–Sloane–Solé 1994, IEEE Trans IT 40(2)
"The Z₄-linearity of Kerdock, Preparata, Goethals, and related codes";
verified against Error Correction Zoo c/kerdock and the d_min = 2^(m−1) −
2^((m−2)/2) standard formula via IP = N − 2d). For N=4096 (m=12), the
non-trivial pairwise inner-product magnitudes are exactly {0, 128}/4096 ∈
**{0, 1/32}** [CORRECTED from 1/64 — factor-of-2 error in original],
meeting the Welch bound for a binary code at this length. Random
±1 keys have |⟨kᵢ, kⱼ⟩|/N ~ N(0, 1/√N) — same √N scaling on the typical
case but *no upper bound*; the tail produces the correlated-key bridges
that the substrate-internal multi-probe metrics exploit.

**Erase via the same anti-Hebbian rule.** Compute W' = W − vₑ kₑᵀ / N
exactly as before. Side effect on kept kⱼ:

  W'·kⱼ = W·kⱼ − vₑ (⟨kₑ, kⱼ⟩ / N)

For random keys this is vₑ × O(1/√N) in magnitude with a Gaussian tail;
for Kerdock keys it is **exactly** vₑ × (1/64) when the inner product is
nonzero, and zero otherwise. The cross-talk is structured, bounded, and
predictable.

**What the substrate already knows.** `wave14xrd_structured_keys` already
demonstrated that Hadamard keys (Kerdock-1, the linear subcode of Kerdock)
produce WHT-spectrum SNR ≈ 1.5×10⁷ vs 1.3 for random keys — the substrate
operates correctly under structured keys. `wave14forensics_walsh_peaks`
showed 100% key-index recall at every K up through K=4000, so structured-
key storage doesn't break the substrate's capability surface.

**Multi-probe failure-mode prediction.**
- **argmax**: passes by very wide margin. Erase removes the rank-1 atom
  cleanly; cross-talk via Welch-bounded inner products is below the
  cleanup threshold.
- **rank**: erased vₑ falls past rank 100 because Welch-bounded cross-talk
  contributes only ~v / 64 magnitude to W·kⱼ, well below the distinctive
  pattern signature of any kept (vⱼ, kⱼ).
- **norm**: ||W'·kₑ|| / mean ||W'·kⱼ|| should be ~1/N (only finite-precision
  residue) vs anti-Hebbian-on-random ≈ 0.4 (Mirage paper measured).
- **cos under correlated probe**: this is the wildcard. A "correlated probe"
  is k̃ ≈ kₑ + small perturbation. If the perturbation moves k̃ off the
  Kerdock orbit entirely, W'·k̃ becomes noise (off-codebook input). If the
  perturbation moves k̃ to a *nearby Kerdock codeword*, the structure
  protects only if that codeword is the right Welch-bounded distance from
  kₑ. **Honest read: requires test.**
- **paraphrase_leak**: same wildcard. Depends on whether the paraphrase
  generation procedure produces keys inside or outside the codebook orbit.

**Honest probability of passing all four probes**: 40–55%. The strongest
candidate by theoretical floor, but the codebook-vs-paraphrase interaction
is genuinely unknown. Tradeoff: requires substrate to be retrained or
re-encoded with structured keys.

### Candidate 2: Iterative charge-flipping erase

**The math.** Charge flipping is Oszlanyi–Suto 2004 (Acta Cryst A60,
arXiv:cond-mat/0308129): an iterative phase-retrieval algorithm for
crystallographic structure solution that alternates between (a) FFT to
reciprocal space and impose data-fidelity constraints (observed amplitudes),
(b) inverse FFT to real space and impose a positivity/sparsity constraint
(flip charges below a threshold).

**As an erase mechanism.** Reformulate: we want a W' such that
- W'·kⱼ ≈ W·kⱼ for all kept j (data fidelity)
- W'·kₑ ≈ 0 (erase fidelity)
- W' close to W in some norm (locality)

The natural charge-flipping analog alternates:
1. Compute the erase residual R = W − W' (the proposed "removed" component)
2. Project R onto the subspace spanned by candidate erase atoms (initially
   just (vₑ, kₑ))
3. Flip components of R below a threshold (sparsify the removed component)
4. Re-impose data fidelity by solving for W' s.t. W'·kⱼ = vⱼ on kept
5. Iterate.

**Honest assessment.** Charge flipping is fundamentally an **inverse
problem solver** designed to *find* a sparse object given its Fourier
amplitudes. It's the right tool for **forensics** (Bet 3 in
`active_priorities.md`: recover hidden (vₖ, kₖ) from W), but it's the
wrong tool for **erase**: erase already knows what to remove (vₑ, kₑ); the
hard part is the side-effect minimization, not the find step. The
iteration buys nothing once the target is already known; the algorithm
collapses to the ROME closed form on the first iteration when there's
no ambiguity about what to remove.

**Multi-probe prediction**: passes argmax (the iteration converges to
W'·kₑ ≈ 0), but iterative refinement does not address the
neighborhood-leakage failure mode that Mirage probes detect.

**Honest probability**: 15–25%. Bet 3 territory, not Bet 2 territory.
The convergence-vs-cross-talk tradeoff is the same one anti-Hebbian
hits, just with a more expensive solver.

### Candidate 3: Full ROME-style optimization

**The math.** ROME (Meng et al. 2022, arXiv:2202.05262) solves

  W' = argmin ||W' − W||_F²  s.t.  W'·kₑ = v_target

with closed form W' = W + (v_target − W·kₑ)(C⁻¹·kₑ)ᵀ / (kₑᵀ C⁻¹·kₑ),
where C = E[k kᵀ] is the key-distribution covariance. For erase,
v_target = 0 → W' = W − (W·kₑ)(C⁻¹·kₑ)ᵀ / (kₑᵀ C⁻¹·kₑ). When C = I,
this is identical to anti-Hebbian rank-1 (up to normalization). When C
is the empirical key covariance, the C⁻¹ factor acts as a whitening
preconditioner: edits along high-variance key directions are
proportionally damped.

**MEMIT extension** (Meng et al. 2022, arXiv:2210.07229) solves the same
optimization for a *batch* of (kᵢ, vᵢ) targets simultaneously. Both
methods minimize Frobenius distance to W on average; neither minimizes
the actual multi-probe metrics that Mirage uses.

**Honest assessment.** The Mirage of Model Editing paper
(arXiv:2502.11177) specifically tested ROME-class methods on the
rank / norm / cos / paraphrase probes and showed all of them fail under
correlated-key conditions. The substrate's `wave14p_erase_multiprobe`
result replicated the Mirage finding in our own setting. **Full
ROME-style optimization is exactly the family that has already been
shown to fail.** The C⁻¹ whitening helps the argmax probe but does not
fix the neighborhood leakage that the rank/norm/cos/paraphrase probes
detect — because those probes test out-of-distribution from the C
estimate.

**Possible rescue — AlphaEdit (existing prior art, ICLR 2025 Outstanding;
arXiv:2410.02355) [REVISED 2026-05-21 post-audit]**: replace the Frobenius
objective with a **null-space-projected** ROME update. AlphaEdit's
construction: let P be the projector onto the null space of the
kept-keys matrix K_keep = [k_j : j kept]. Then apply the ROME-style
update but pre-multiplied by P:

  W' = W − vₑ (P kₑ)ᵀ / ||P kₑ||²   (modulo normalization)

After projection, W'·k_j = W·k_j *exactly* for every kept j (by
construction — the update is in the null space of kept keys). The
residual on kₑ: W'·kₑ = W·kₑ − vₑ × (kₑᵀ P kₑ / ||P kₑ||²) = W·kₑ − vₑ
when P kₑ ≠ 0, which it is as long as kₑ has a component in the null
space (true for random keys at the substrate's α=0.153 operating point).

**Critically: this is NOT a novel proposal — AlphaEdit is published
prior art and reports scaling to 3000 sequential edits** (Jiang et al.,
ICLR 2025 Outstanding Paper). My original framing of "paraphrase-aware
ROME" as a research direction was wrong; the right framing is "port
AlphaEdit's null-space projection to the substrate and test it under
the substrate-internal four-probe battery."

**Also relevant — r-ROME / "Rebuilding ROME"** (Gupta-Baskaran-
Anumanchipalli EMNLP 2024, arXiv:2403.07175) addresses ROME's
"disabling edits" and model-collapse under sequential edits. When the
note invokes "vanilla ROME" as Candidate 3, the *current* implementation
to test is r-ROME, not the 2022 original.

**Honest probability** (vanilla ROME / MEMIT under substrate four-probe):
5–15% — confirmed failed in the Mirage paper and in
`wave14p_erase_multiprobe`. **AlphaEdit under substrate four-probe on
random ±1 keys**: 50–65% — substrate's keys are approximately mutually
orthogonal at α=0.153, so the null-space projection has well-defined
geometry; the cross-talk that anti-Hebbian leaked via correlated probes
is precisely what AlphaEdit eliminates by construction. Higher
probability than Kerdock 2A.i because AlphaEdit works on the substrate's
existing random keys without restructuring.

### Candidate 4: Per-fact orthogonal-subspace allocation

**The math.** Restructure storage so each fact gets a dedicated
d-dimensional subspace S_i ⊂ R^N with S_i ⊥ S_j (i≠j). Concretely:
partition the N coordinates into M blocks of d coordinates each
(M = N/d). Fact i is stored as a vector confined to block i; reading
fact i means restricting the inner product to block i. Block-diagonal W
where block i contains the rank-d storage of fact i.

The erase operation is now exact: zero block e. By construction, every
multi-probe metric passes:
- argmax: W'·k_e in block e is zero; argmax over cleanup returns no
  match for v_e.
- rank: v_e is absent from W' entirely; rank → ∞ (or "not present" as a
  categorical outcome).
- norm: ||W'·k_e|| = 0 exactly.
- cos: undefined (zero vector); or 0 by convention.
- paraphrase: if paraphrase keys live in block e (the same fact's
  perturbations), they also see zero. If paraphrase keys live in some
  other block by accident, they read out the other fact — which is
  the *correct* behavior.

**The catch — capacity.** With block size d, the substrate stores at
most M = N/d facts. For Hopfield-like α_c ≈ 0.153 at N=4096, the
random-key substrate stores ≈ 627 patterns. Block-orthogonal with
d=8: 512 facts. d=16: 256 facts. The capacity floor matches or
slightly underperforms random ±1 Hopfield, but the erase semantics
are perfect.

**The catch — addressing.** Reads need to know which block to look in.
Either (a) a deterministic key→block hash (loses the substrate's
distributed-binding property; becomes essentially a hash table), or
(b) a content-addressable lookup that first identifies the relevant
block, which requires another mechanism layered on top.

**Closely related literature** [CORRECTED 2026-05-21]:
orthogonal-overcompletion in dictionary learning; expanded-storage
Hopfield variants (Demircigil, Heusel, Löwe, Upgang, Vermet, "On a Model
of Associative Memory with Huge Storage Capacity," J. Stat. Phys. 168,
2017, arXiv:1702.01929 — author list corrected; Krotov and Hopfield are
NOT authors on this paper, their related work is Krotov & Hopfield 2016
"Dense Associative Memory for Pattern Recognition," NeurIPS); modern
Hopfield Networks with separated patterns via Ξ-matrix attention storage
(Ramsauer et al. 2020, arXiv:2008.02217 — this is Ξ-matrix storage, NOT
block-diagonal-W or per-fact orthogonal subspaces; the architectures
share intuition but are mathematically distinct). The closest *direct*
prior art for Candidate 4 is **MUNKEY** ("Rethinking Machine Unlearning:
Models Designed to Forget via Key Deletion," arXiv:2603.15033), which is
explicitly "unlearning by design" via key deletion in a memory-augmented
transformer — exactly the per-fact-subspace-with-clean-erase pattern
Candidate 4 describes.

**Honest assessment**: This isn't an erase **mechanism** — it's a
substrate **redesign**. The four-probe passes are guaranteed by
construction. But the substrate gives up the distributed-overlapping
storage that gave it provenance and decomposability in the first place;
in the limit it's a hash table.

**Honest probability of passing all four probes**: 75–90% — by
construction. **Probability that this is the *right* answer for the
substrate**: depends entirely on whether the user values surgical
erase enough to give up overlap-based capacity. Likely no for the
small bet; possibly yes for a compliance-focused product variant.

---

## Pass 2 — Drill into the two viable families

Pass 1 narrowed the candidate space:
- Charge-flipping is wrong tool (it's forensics).
- Vanilla ROME is closed by Mirage.
- That leaves **Kerdock-coset + anti-Hebbian** and **per-fact
  orthogonal subspaces** as the two with real probability of multi-probe
  survival. The paraphrase-aware ROME extension is a third possibility
  but is computationally expensive and lacks structure-based intuition
  for why the paraphrase probe would pass.

### Drill 2A: Kerdock-coset + anti-Hebbian erase

**Codebook construction.** For N=4096 (the substrate's operating width),
take the Kerdock code K(6) viewed as 2^12 codewords of length 2^12,
constructed from the Reed-Muller(1, 12) code via the Z₄-Gray map. Each
codeword is ±1 over N coordinates. There are 2^12 · 2^12 = 2^24 ≈ 16.8M
distinct Kerdock-coset keys — vastly more than the substrate's K=30–500
operating range, so codebook capacity is not the constraint.

**Key inner-product structure.** For any two distinct codewords kᵢ, kⱼ ∈
K(m): ⟨kᵢ, kⱼ⟩ ∈ {0, ±2^((m+2)/2)} — i.e., {0, ±64} for m=12. So
|⟨kᵢ, kⱼ⟩|/N ∈ {0, 1/64}. Compare to random ±1: |⟨kᵢ, kⱼ⟩|/N ~ N(0, 1/N),
typical value 1/64 but with a Gaussian tail that has weight on much
larger values.

**Erase cross-talk bound.** Apply anti-Hebbian W' = W − vₑ kₑᵀ / N. For
kept (vⱼ, kⱼ):

  ΔW · kⱼ = − vₑ × (⟨kₑ, kⱼ⟩ / N)
          ∈ vₑ × {0, ±1/32}  [CORRECTED from ±1/64]

Side effect on kept reads is *exactly* zero for kj with ⟨kₑ, kⱼ⟩ = 0,
and *exactly* vₑ/32 in magnitude when nonzero. Compare to random ±1:
side effect is vₑ × N(0, 1/N), with magnitude exceeding 1/32 with
probability ~Φ(−2) ≈ 2.3%. So under Kerdock keys, the worst-case
cross-talk is BOTH bounded AND occurs at every nonzero-pair position;
under random keys, the typical case is smaller but with a heavy tail
that puts ~2% of pairs above the Kerdock bound. The structural win is
not "smaller cross-talk everywhere" but "bounded cross-talk in a
predictable, structured set."

**Where the paraphrase probe lives.** A paraphrase of kₑ at Hamming
distance h has key k̃ with k̃ = kₑ with h bits flipped. If kₑ ∈ Kerdock
codebook and the Hamming distance to the *nearest other Kerdock codeword*
is at least h_min (the minimum distance of K(m); for even m the formula
is d_min = 2^(m−1) − 2^((m−2)/2), so for K(12) this is **2^11 − 2^5 =
2016** [CORRECTED 2026-05-21 from ≈1984]), then a paraphrase at h < h_min
lives *outside* the codebook entirely. W·k̃ for off-codebook k̃ is dominated
by the same anti-Hebbian residual that random keys suffer from — the
structure protection vanishes once k̃ leaves the codebook orbit.

**This is the load-bearing observation.** Kerdock buys clean erasure on
kept *codebook* keys (which is the easy part anyway, since they're
near-orthogonal by construction) but *does not* buy clean erasure on
paraphrase probes (which is the actually hard part). The probability of
passing the paraphrase probe depends on whether the substrate's
"paraphrase" generation procedure produces on-codebook or off-codebook
keys.

**Two sub-variants worth considering.**

- **Variant 2A.i**: keys drawn from the codebook *and* paraphrases
  defined as nearest-codebook-neighbor (snap-to-codebook). Then
  paraphrase probes ARE on-codebook, and the Welch-bounded cross-talk
  rules them too. Passes all four probes with high probability.
  Tradeoff: the substrate has to formalize a "snap-to-codebook" step
  in its query pipeline, which is a real but small architectural
  addition.

- **Variant 2A.ii**: keys drawn from the codebook, paraphrases are
  generic Hamming-perturbations. Then off-codebook paraphrases revert
  to random-key-like cross-talk behavior. Passes argmax/rank/norm
  cleanly but the paraphrase probe is a coin-flip. Unlikely to pass
  the < 5% paraphrase_leak threshold.

**Bonus capabilities Kerdock unlocks (already in the cap map).**
- WHT-peak forensics (Bet 3): every stored fact is a Bragg peak in the
  Walsh-Hadamard transform of W. 100% recall already validated.
- 50–350× faster cleanup via Fast Hadamard Transform (cleanup becomes
  O(N log N) instead of O(N²)).
- 2× usable K vs random keys (Welch bound vs Hopfield α_c).

These are not contingent on the erase question; they ship regardless.

**Substrate-specific risks.**
- The current alpha_c measurement (`wave14m_alpha_c`: α_c = 0.153 at
  N=4096) was measured on random ±1 keys. Kerdock-key substrate
  capacity hasn't been measured; literature says it should be at least
  random + a constant factor, but the actual number is a real unknown.
- W is currently trained via Hebbian delta on random keys; switching
  keys requires re-encoding existing pool entries (one-time cost) and
  re-validating that every other capability (R10, ICL, ACF rescue)
  still works under structured keys.

### Drill 2B: Per-fact orthogonal-subspace allocation

**Block-diagonal construction.** Partition coordinate index set
{1, ..., N} into M = N/d blocks B_1, ..., B_M of size d. For each fact
i, the key k_i has support only on block B_i (zeros elsewhere). The
value v_i likewise. Storage:

  W_i = v_i k_iᵀ  (rank-1 on block i, zero elsewhere)
  W = Σᵢ W_i = block_diag(W_1, ..., W_M)

This is mathematically *identical* to a hash table with d-dimensional
slots, dressed up in matrix notation.

**Erase as exact zeroing.** Erase fact e = set block B_e of W to zero.
Reads of paraphrases of k_e remain within block B_e (since paraphrase
generation is a Hamming perturbation, and a perturbation of a
block-restricted vector is still block-restricted up to the perturbed
coordinates). W·k_paraphrase has the zero block in slot e and reads
zero for that fact specifically. Multi-probe passes by construction.

**Capacity story.** At d = 8, N = 4096 stores at most 512 facts. The
random-key Hopfield capacity at α_c = 0.153 is ~627 facts. So
block-orthogonal storage gives **roughly 20% fewer** facts at the same
N. This is the explicit price of guaranteed erase.

**Capability tradeoffs the substrate would lose.**
- Distributed binding goes away — facts no longer share dimensions, so
  the substrate's decomposable bundling primitive collapses to a flat
  hash.
- Pool retrieval via cosine across all bundles still works
  mechanically (cosine reads block-i values from block-i bundles), but
  the cosine itself is now ⟨k_query restricted to block i, k_stored⟩,
  which is exactly the within-slot cosine of an ordinary lookup
  table. No structural advantage over a vector database.
- ICL via pool, R10 concept fusion, multi-hop reasoning — all of these
  depend on overlap between facts in shared dimensions. Block-
  orthogonal storage breaks them.

**Honest read.** This isn't a substrate; it's a different product.
Per-fact orthogonal-subspace passes the GDPR-erase probes by abandoning
the substrate's core differentiation. The capability table after this
change would lose most of its CAN rows.

**Honest probability that this is the right answer for the project**:
low — say 10–15%. The substrate's value comes from the overlap-based
math; trading all of that for clean erase moves the product to "a hash
table with proof," which isn't worth the substrate's complexity.
Worth keeping in the candidate list because it sets a lower bound
("at the limit, block-orthogonal solves the problem") that calibrates
how much overlap we can afford.

---

## Comparison table — multi-probe survivability [REVISED 2026-05-21 post-audit]

| Candidate | argmax | rank | norm | cos correlated | paraphrase | side effects | capacity | substrate-fit |
|---|---|---|---|---|---|---|---|---|
| 1. Kerdock + anti-Hebb (snap variant 2A.i) | ✅ very wide | ✅ Welch-bounded | ✅ ~1/N | ✅ if on-codebook | ✅ if snap-to-codebook | ✅ bounded 1/32 | ≥ random-key (literature says 2× usable K) | high (already used in Bet 3); requires substrate key restructuring |
| 1'. Kerdock + anti-Hebb (free paraphrase 2A.ii) | ✅ | ✅ | ✅ | 🟡 coin flip | ❌ likely fails | ✅ | same | high |
| 2. Iterative charge-flipping | 🟡 converges to argmax pass | ❌ same direction problem | 🟡 | ❌ | ❌ | 🟡 | unchanged | medium (wrong tool: forensics not erase) |
| 3. Vanilla ROME / MEMIT | ✅ | ❌ (Mirage confirmed) | ❌ | ❌ | ❌ | depends on C accuracy | unchanged | low — already closed by Mirage; use r-ROME (arXiv:2403.07175) if testing ROME family at all |
| **3'. AlphaEdit (null-space projected, arXiv:2410.02355) [REPLACES "paraphrase-aware ROME"]** | ✅ | ✅ by construction (update ⊥ kept keys) | ✅ tight on kept | ✅ structural (null-space) | ✅ if paraphrase falls in kept-key span (low for random ±1) | ✅ exact on kept | unchanged | **high — works on substrate's existing random keys, no restructuring; published ICLR 2025 Outstanding; scales to 3000 sequential edits** |
| 4. Block-orthogonal (per-fact subspace) | ✅ exact | ✅ exact | ✅ exact (0) | ✅ exact | ✅ within-block | ✅ exact (0) | ~20% fewer | low — destroys overlap math; published analog is MUNKEY (arXiv:2603.15033) |

**Recommendation for Bet 2 / E2 [REVISED 2026-05-21 post-audit]**: run
**TWO candidates in parallel**, not one:

1. **`wave14g_erase_alphaedit_v1`** — port AlphaEdit's null-space
   projected anti-Hebbian to the substrate's *existing* random ±1 keys.
   No substrate restructuring required. Published prior art (Jiang et al.
   ICLR 2025 Outstanding, arXiv:2410.02355) reports scaling to 3000
   sequential edits on transformer model editing; we test whether the
   same mechanism survives the substrate's four-probe battery at
   α=0.153. Estimated probability of passing: 50–65%.

2. **`wave14g_erase_kerdock_v1`** (Variant 2A.i) — Kerdock-coset keys
   with snap-to-codebook paraphrase semantics. Cheaper per-edit IF
   substrate adopts structured keys; ships with WHT-forensics + faster
   cleanup as side benefits. Requires substrate restructuring. Estimated
   probability of passing: 40–55%.

Run both. AlphaEdit lands faster (no key restructuring); Kerdock pays
off larger if it lands. P(at least one passes) ≈ 70–80%.

Falls-back if both fail: Candidate 3 (vanilla ROME) is closed; Candidate
2 (charge-flipping) is wrong tool; Candidate 4 (block-orthogonal,
published as MUNKEY arXiv:2603.15033) requires substrate redesign that
destroys overlap-based capabilities.

---

## Specific experimental design (pseudocode) [REVISED 2026-05-21 — two parallel experiments, not one]

### Experiment A — `wave14g_erase_alphaedit_v1` (primary, no substrate restructuring)

Port AlphaEdit (Jiang et al. ICLR 2025, arXiv:2410.02355) to the
substrate's existing random ±1 keys. Same multi-probe battery as
Experiment B. Pseudocode:

```text
alphaedit_erase(W, v_e, k_e, kept_keys K_keep):
  # P projects onto null space of kept keys
  # K_keep is (M_kept, N) matrix of kept keys stacked as rows
  K = K_keep
  # null-space projector: I - K^T (K K^T)^-1 K
  P = eye(N) - K.T @ inv(K @ K.T) @ K  # (N, N)
  k_e_proj = P @ k_e
  if norm(k_e_proj) < eps:
    # erased key is fully in kept-key span; AlphaEdit cannot proceed cleanly
    return W, 'DEGENERATE'
  scalar = (k_e @ k_e_proj) / (k_e_proj @ k_e_proj)
  return W - scalar * outer(v_e, k_e_proj), 'OK'
```

Runs the same multi-probe battery as Experiment B (see below). The key
question: does AlphaEdit's null-space projection survive the four-probe
battery on substrate's random ±1 keys at α=0.153?

Predicted: P(passes) ≈ 50–65%. Major risk: when M_kept approaches N,
the null space shrinks and ||P k_e|| → 0; the substrate's α=0.153
operating point means M_kept = 627 ≪ N = 4096, so null space is large
(rank ≈ 3469) and projection should be well-defined.

### Experiment B — `wave14g_erase_kerdock_v1` (parallel, structured-key variant)

Pre-registered at `preregs/2026-05-21_wave14g_erase_kerdock_v1.md`
(Experiment Dev to author). Multi-probe by construction. Tests
Variant 2A.i.

```text
config:
  N = 4096
  alpha = 0.153  # operating point per wave14m_alpha_c
  M_stored = floor(0.153 * 4096) = 627  # fill substrate to capacity
  seeds = [7, 17, 23, 31, 41]  # 5-seed standard per playbook
  N_erase = 30  # erase 30 facts per seed
  N_kept = 100  # measure side effects on 100 kept facts per seed
  N_paraphrase = 50  # paraphrase probes per erased fact
  paraphrase_hamming = [2, 4, 8, 16]  # Hamming radii for paraphrase probes

key_construction:
  # Kerdock code K(12) at length N=4096 has min-distance ~1984.
  # Construct codebook from RM(1, 12) via Z4-Gray map.
  codebook = construct_kerdock_codebook(N=4096)  # 2^24 codewords
  # For each fact i, draw key from codebook uniformly without replacement.
  k_i = sample_without_replacement(codebook, M_stored)
  # Values from random bipolar (orthogonal to key structure question).
  v_i = uniform_bipolar(N=4096, M_stored)

storage:
  W = sum_i v_i k_i^T  # outer-product Hebbian

erase_op(W, v_e, k_e):
  return W - (v_e k_e^T) / N

snap_to_codebook(k_query):
  # Find nearest Kerdock codeword to a (possibly perturbed) query.
  # For K(12), exact nearest-codeword decoding is O(N log N) via
  # Fast Hadamard Transform + soft-decision decoding (Forney 1972,
  # but standard for Reed-Muller).
  return argmax_{c in codebook} <k_query, c>

multi_probe_battery(W_prime, k_e, v_e, kept_keys, kept_values):
  # All four probes from active_priorities.md Bet 2 / Mirage paper.
  results = {}

  # 1. argmax probe.
  pred_e = cleanup(W_prime @ k_e, value_codebook)
  results['argmax_leak'] = float(pred_e == v_e)

  # 2. rank probe.
  cleanup_scores = score_against_value_codebook(W_prime @ k_e)
  rank_e = rank_of(v_e, cleanup_scores)
  results['rank'] = rank_e

  # 3. norm probe.
  norm_e = norm(W_prime @ k_e)
  norms_kept = [norm(W_prime @ k) for k in kept_keys]
  results['norm_ratio'] = norm_e / mean(norms_kept)

  # 4. cos under correlated probe.
  for h in paraphrase_hamming:
    paraphrases = [
      snap_to_codebook(hamming_perturb(k_e, h))  # variant 2A.i
      for _ in range(N_paraphrase)
    ]
    leak_rate = mean([
      float(cleanup(W_prime @ k_p, value_codebook) == v_e)
      for k_p in paraphrases
    ])
    results[f'paraphrase_leak_h{h}'] = leak_rate

  # 5. side effects on kept.
  kept_preserved = [
    float(cleanup(W_prime @ k_kept, value_codebook) == v_kept)
    for k_kept, v_kept in zip(kept_keys, kept_values)
  ]
  results['kept_preservation'] = mean(kept_preserved)

  return results

main:
  for seed in seeds:
    construct W with above procedure
    for fact_idx in erase_targets:
      W_prime = erase_op(W, v_e, k_e)
      probe_results[seed][fact_idx] = multi_probe_battery(...)

  aggregate across seeds, report all probes with 1-sigma bounds.

verdict_logic:
  PASS iff (per substrate-internal Bet 2 criteria — these are
            substrate-internal probes, not from the Mirage paper;
            closest published analog is MEMIT-CSK-PROBE arXiv:2305.14956):
    mean argmax_leak < 0.10
    mean rank > 100
    mean norm_ratio < 0.15
    mean cos at h=8 < 0.10        # substrate-internal probe definition
                                  # per wave14p_erase_multiprobe
    mean paraphrase_leak at h=8 < 0.05
    mean kept_preservation > 0.95
```

**Smoke test (queue_add gate)**: N=512, M_stored=64, N_erase=5,
N_paraphrase=10, seeds=[7]. Target runtime ~10s. Pre-registered
oracle assertions: paraphrase_leak should be < 0.20 even at smoke
scale (the structure should be visible above floor).

**Self-test**: 4 synthetic cases:
- All-kept-keys-orthogonal-and-erased-fact-far-from-all: predict
  argmax pass, rank ∞, paraphrase_leak 0.
- All-kept-keys-orthogonal-and-erased-fact-close-to-one-kept: predict
  argmax pass on erased, leak detected on the close kept.
- Erased fact = nearest-Kerdock-codeword to a kept fact: predict
  controlled-magnitude (1/32) side effect on that kept fact
  [CORRECTED from 1/64].
- Random ±1 keys (control): predict failure across multi-probe
  (replicate wave14p_erase_multiprobe failure on anti-Hebbian; should
  also replicate Mirage paper's broader finding that ROME-class
  methods fail under realistic decoding).

**Wall budget**: ~30 min GPU at full scale (627 facts × 30 erase ×
50 paraphrase × 5 seeds = ~5M cleanup probes, batched). Smoke ~10s.

---

## Materials analog (load-bearing)

The math behind why Kerdock keys protect erase while random keys do
not maps cleanly to a well-known materials-physics distinction.

**Spin-glass framing.** The substrate's W = Σ vᵢ kᵢᵀ is the
classical Hopfield network, equivalent to a Sherrington–Kirkpatrick
spin glass with disorder set by the stored patterns. Under random ±1
keys, the off-diagonal correlations of W are themselves random with
Gaussian statistics — the substrate sits in the spin-glass phase
with frustrated, unstructured cross-talk between memories.

Under Kerdock keys, the same construction places the substrate on the
**Mattis-glass / quasicrystalline boundary**. Mattis glasses (Mattis
1976, "Solvable spin systems with random interactions") use J_ij =
ξᵢ ξⱼ for a single bipolar pattern; the resulting matrix is rank-1
and trivially solvable. Kerdock keys generalize this: each
J_ij = Σ_k vₖ⁽ⁱ⁾ vₖ⁽ʲ⁾ but with the *codewords as the disorder*,
which forces |⟨kᵢ, kⱼ⟩| ∈ {0, ±√N} exactly. The disorder is
**structured at the Welch bound**; the spin-glass phase is suppressed
in favor of a "ferromagnet of codewords" regime.

**Crystallography analog.** This is the same distinction as
**amorphous vs paracrystalline order** in solid-state physics. An
amorphous solid has Gaussian-statistics interatomic distances
(random ±1 keys) — local perturbations spread diffuse speckle through
the diffraction pattern, and "removing one atom" is hard to localize
in reciprocal space. A paracrystalline solid (Hosemann 1962) has
discretized interatomic distances on a near-lattice; removing one atom
produces a localized signature against the Bragg-peak background.
The substrate already showed this in `wave14xrd_structured_keys`:
Hadamard keys produce Bragg peaks of SNR ≈ 1.5×10⁷ over a near-zero
background, while random keys produce SNR ≈ 1.3 (amorphous speckle).
Erasing one Hadamard key removes one Bragg peak cleanly; erasing one
random key shifts the whole speckle pattern by a small amount —
detectable only via global probes, not local ones.

This is the materials reason that multi-probe metrics behave so
differently in the two regimes: a probe is a localized question
("did this specific feature disappear?"), and localized questions
have clean answers in crystalline media but diffuse answers in
amorphous media.

**Predictive consequence.** The same intuition predicts that any
codebook with Welch-bound-meeting inner products should work —
not just Kerdock specifically. Reed-Muller codes, Hadamard sets,
Kerdock-cosets, and equiangular tight frames (ETFs) all share the
property. Kerdock is the most binary-friendly of these at N=4096 and
shares the existing substrate's ±1 dynamics; ETFs would require
non-binary keys and a larger substrate rewrite. The materials story
is robust across the structured-key family.

---

## Falsifiable prediction [REVISED 2026-05-21 post-audit: numbers updated for 1/32 cross-talk; AlphaEdit predictions added]

### Primary prediction A — AlphaEdit on random keys (`wave14g_erase_alphaedit_v1`)

At N=4096, α=0.153, M_stored=627 random ±1 facts, AlphaEdit null-space
projection of anti-Hebbian update:

- argmax leak rate: **< 3%** (lower than Kerdock 2A.i because projection
  is exact on kept keys by construction).
- rank metric for erased fact: **> 500** (clean null-space projection
  removes the rank-1 contribution from W·k_e direction; only
  finite-precision residual remains).
- norm_ratio: **< 0.01** (||W'·k_e|| residual scales with degeneracy of
  null-space projection: when M_kept = 627 ≪ N = 4096, ||P k_e|| ≈
  ||k_e|| · √(1 − 627/4096) ≈ 0.92 ||k_e||, so projection retains 92%
  of erase magnitude; residual is bounded).
- paraphrase_leak at Hamming h=8: **predicted 5–15%** — the key
  uncertainty. Paraphrase keys at h=8 have a component in the kept-key
  span (because they're close to kept-key direction for any kept j with
  Hamming(k_j, k_e) ≤ 16), and AlphaEdit doesn't constrain behavior on
  off-distribution probes. **This is the load-bearing test.**
- kept_preservation: **> 0.99** (exact on kept by construction; only
  finite-precision floating-point error).

If paraphrase_leak lands below 5%, AlphaEdit is the answer and no
substrate restructuring needed. If between 5–15%, partial success and
the substrate may need Kerdock keys as well. If above 15%, AlphaEdit
fails for substrate GDPR-erase scope.

### Primary prediction B — Kerdock + snap (`wave14g_erase_kerdock_v1`, Variant 2A.i)

At N=4096, α=0.153, M_stored=627 facts drawn from K(12), single-fact
anti-Hebbian erase + snap-to-codebook paraphrase semantics:

- argmax leak rate: **< 5%** (5-seed mean); compared to anti-Hebbian-on-
  random-keys ~23% argmax leak (`wave14p_erase_multiprobe`).
- rank metric for erased fact: **> 300** (vs published ROME-class
  methods reporting ~5–10 under similar probes in MEMIT-CSK-PROBE
  evaluations).
- norm_ratio: **< 0.04** [CORRECTED — theoretical floor with snap and
  Welch-bound 1/32 cross-talk gives ~ 1/32 × M_overlap/M_kept ≈ 0.015
  per Welch-bounded pair; finite-precision and snap-error ~2× that;
  well under 0.15 target].
- paraphrase_leak at Hamming h=8 (with snap-to-codebook): **< 3%**.
  Snap forces paraphrase onto a Kerdock codeword; cross-talk between
  any two distinct codewords is bounded by 1/32; the contribution
  toward v_e from kept-key bridges is at most v_e × 1/32 per overlap
  pair, summed over ~M_kept/2 nonzero-overlap kept keys × averaging =
  ~0.015 × v_e per probe.
- kept_preservation: **> 0.94** [REVISED DOWN from > 0.96]:
  Welch-bounded cross-talk magnitude **1/32 = 0.03125** per affected
  kept fact [CORRECTED from 1/64 = 0.0156]; only ~half of kept facts
  share any inner product with the erased one, so mean degradation
  per kept fact is ~0.015. After 30 erasures with shared kept set,
  cumulative degradation ~30 × 0.015 / 2 = 0.225 on a small subset
  of kept facts; mean across all kept stays above 0.94.

### Secondary prediction (sanity-check on the codebook structure)

If snap-to-codebook is dropped (Variant 2A.ii — free Hamming
paraphrases): argmax/rank/norm should still pass cleanly (the
codebook structure protects on-codebook keys), but paraphrase_leak
at h=8 reverts to **≥ 15%** because off-codebook paraphrases see
the same random-key-like cross-talk. This is the falsifier for the
"keys alone are enough" hypothesis: if paraphrase_leak passes at <
5% even WITHOUT snap, then something more powerful than the
codebook structure is doing the work, and we'd want to find what.

### Kill criterion for the joint candidate set

If Experiment A (AlphaEdit) AND Experiment B (Kerdock 2A.i) AND
Variant 2A.ii (Kerdock without snap) all fail to meet
paraphrase_leak < 5% at h=8 after 3 separate parameter-tuning attempts
each, the substrate's GDPR-erase capability is structurally limited
under the current architecture. The next-priority fallback is Candidate
4 (per-fact orthogonal subspace, published as MUNKEY arXiv:2603.15033),
which requires substrate redesign trading overlap-based capabilities
for clean erase. That tradeoff would shift the cap_map's product story
toward "compliance-focused substrate variant" as a separate product.

---

## Citations

1. Hammons, Kumar, Calderbank, Sloane, Solé (1994). "The Z₄-linearity
   of Kerdock, Preparata, Goethals, and related codes." *IEEE Trans.
   Inform. Theory* 40(2): 301–319. DOI: 10.1109/18.312154.
   — Foundational construction of Kerdock codes via the Z₄-Gray map;
   establishes the Welch-bound-meeting inner product structure.

2. Meng, Bau, Andonian, Belinkov (2022). "Locating and Editing Factual
   Associations in GPT" (ROME). arXiv:2202.05262.
   — Defines the rank-1 closed-form weight edit; foundational for
   Candidate 3.

3. Meng, Sharma, Andonian, Belinkov, Bau (2022). "Mass-Editing Memory
   in a Transformer" (MEMIT). arXiv:2210.07229.
   — Batch extension of ROME; same constraint-minimization framework.

4. Cohen, Yoran, Wolfson, Geva, Globerson (2023). "Evaluating the
   Ripple Effects of Knowledge Editing in Language Models."
   arXiv:2307.12976.
   — Documents that ROME/MEMIT pass the editor's training metric but
   fail downstream paraphrase / portability metrics — the precursor
   to the Mirage paper's framing.

5. Yang, et al. (2025). "The Mirage of Model Editing: Revisiting
   Evaluation in the Wild." arXiv:2502.11177 [CORRECTED arXiv ID
   from 2503.06991].
   — Documents that current editing methods perform substantially
   worse than previously reported (38.5% vs 96.8%) and that current
   approaches fail drastically with only 1000 sequential edits;
   introduces QAEdit and WILD benchmarks. NOTE: the
   rank/norm/cos/paraphrase four-probe battery is **NOT** in this
   paper; that is substrate-internal (wave14p_erase_multiprobe).

6. Oszlanyi, Suto (2004). "Ab initio structure solution by charge
   flipping." *Acta Cryst.* A60: 134–141. arXiv:cond-mat/0308129.
   — Iterative algorithm for Candidate 2; intended use is
   forensics/inverse problem, not erase.

7. Guo, Goldstein, Hannun, van der Maaten (2019). "Certified Data
   Removal from Machine Learning Models." arXiv:1911.03030.
   — Establishes the formal framework for "removal with bound on
   residual influence"; foundational anchor.

8. Hopfield, Feinstein, Palmer (1983). "Unlearning has a stabilizing
   effect in collective memories." *Nature* 304: 158–159.
   — Classical result on anti-Hebbian removal stabilizing Hopfield
   storage; foundational for understanding why anti-Hebbian-on-random
   passes the argmax probe but leaves residual structure detectable
   by deeper probes.

9. Demircigil, Heusel, Löwe, Upgang, Vermet (2017). "On a Model of
   Associative Memory with Huge Storage Capacity." *J. Stat. Phys.*
   168: 288–299. arXiv:1702.01929. [AUTHOR LIST CORRECTED 2026-05-21
   — Krotov and Hopfield are NOT authors on this paper.]
   — Background for the polynomial-energy expanded-storage Hopfield
   variant; informs capacity tradeoffs for storage-architecture
   alternatives.

10. Mattis (1976). "Solvable spin glass with random interactions."
    *Phys. Lett. A* 56(5): 421–422.
    — Materials-science anchor for the Mattis-glass framing of
    Kerdock-key storage; explains why structured disorder collapses
    the spin-glass phase to a tractable ferromagnet-of-codewords
    regime.

### Citations added by post-publication audit (2024–2026 prior art):

11. Krotov, Hopfield (2016). "Dense Associative Memory for Pattern
    Recognition." NeurIPS 2016, arXiv:1606.01164.
    — Original dense-Hopfield architecture invoked by Candidate 5
    ("Krotov-Hopfield" line of work); previously confused in the
    initial draft's citation 9 with the Demircigil et al. paper.

12. Jiang, et al. (2025). "AlphaEdit: Null-Space Constrained Knowledge
    Editing for Language Models." ICLR 2025 (Outstanding Paper).
    arXiv:2410.02355.
    — **Critical 2024-26 prior art.** Projects rank-1 ROME-style
    update onto the null space of preserved-knowledge keys before
    applying. This is the structured form of what the original draft
    proposed as "paraphrase-aware ROME" (Candidate 3'). Scales to
    3000 sequential edits. The substrate-port of AlphaEdit is now
    Experiment A in the revised design.

13. Gupta, Baskaran, Anumanchipalli (2024). "Rebuilding ROME:
    Resolving Model Collapse during Sequential Model Editing." EMNLP
    2024, arXiv:2403.07175.
    — Addresses ROME's "disabling edits" and model-collapse failure
    mode under sequential edits. r-ROME is the current implementation
    to test when invoking the ROME family at all.

14. Gupta, Mondal, Sheshadri, Zhao, Li, Wiegreffe, Tandon (2023).
    "Editing Common Sense in Transformers" (MEMIT-CSK). EMNLP 2023,
    arXiv:2305.14956.
    — Introduces MEMIT-CSK-PROBE with unaffected/affected
    neighborhood + affected paraphrase + affected reasoning. Closer
    published analog to the substrate's "four-probe battery" than the
    Mirage paper is.

15. Cha, Kim, et al. (2026 / 2603.15033). "Rethinking Machine
    Unlearning: Models Designed to Forget via Key Deletion" (MUNKEY).
    arXiv:2603.15033.
    — Closest published analog to Candidate 4 (per-fact orthogonal
    subspace allocation). "Unlearning by design" via key deletion;
    same architectural tradeoff (clean erase ↔ shared-dimension
    capabilities lost).

16. Takeuchi, Takahashi, Kabashima (2026). "Analysis of the Hopfield
    Model Incorporating the Effects of Unlearning." arXiv:2602.08428.
    — Replica-method analysis of anti-Hebbian unlearning in Hopfield
    networks; directly extends the Hopfield-Feinstein-Palmer 1983
    line of work to current rigor. Cite this where the original draft
    cited HFP 1983 alone.

17. (2025). "Certified Unlearning for Neural Networks." arXiv:2506.06985.
    — Current Guo-Goldstein 2019 successor; extends certified removal
    to non-convex models. Replaces the 6-year-old citation 7 as the
    primary regulatory anchor for current methods.

18. (2025). "ChainEdit: Logical Rule-Chain Ripple Effect Evaluation."
    arXiv:2507.08427.
    — RippleEdits (Cohen et al. 2023, citation 4) successor with
    logical rule chains. Use as the current ripple-effect reference.

19. (2025). "Benchmarking and Rethinking Knowledge Editing for LLMs."
    arXiv:2505.18690.
    — Independent confirmation of the Mirage finding from a different
    evaluation angle; strengthens Candidate 3 closure.

---

## Routing [REVISED 2026-05-21 post-audit]

- **Experiment Dev (E2)**: this note now recommends **TWO experiments
  in parallel**:
  - `wave14g_erase_alphaedit_v1` — AlphaEdit null-space projected
    anti-Hebbian on substrate's existing random ±1 keys. No
    substrate restructuring required. Published prior art
    (arXiv:2410.02355) — substrate port is straightforward.
  - `wave14g_erase_kerdock_v1` (Variant 2A.i) — Kerdock-coset keys
    with snap-to-codebook paraphrase semantics. Cheaper per-edit IF
    substrate adopts structured keys; ships with WHT-forensics +
    faster cleanup as side benefits.
  Pre-reg authoring + smoke-gate + queue-add per the standard
  pipeline. See pseudocode blocks for parameters and verdict logic.

- **Strategy**: this note now proposes TWO cap_map row additions
  under "Privacy / erase":
  - "AlphaEdit (null-space projected anti-Hebbian) on substrate's
    random ±1 keys" at 🔬 (experimental design ready)
  - "Kerdock + anti-Hebbian + snap-to-codebook" at 🔬 (experimental
    design ready, requires substrate key restructuring)
  Also proposes:
  - Candidate 2 (charge-flipping) at ❌ for erase scope (correct as
    forensics only)
  - Candidate 3 (vanilla ROME) at ❌ (closed by Mirage paper and
    wave14p_erase_multiprobe; r-ROME is the corrected implementation
    if the family is tested at all)
  - Candidate 4 (per-fact orthogonal subspace, published as MUNKEY) at
    ❌-on-substrate-coherence-grounds (would destroy overlap-based
    capabilities)
  Strategy keeps writer exclusivity on the cap_map; this note is
  read-only input.

- **Research (this session, future cycles)**: if both E2 experiments
  land positive, no further R1 research needed; Strategy upgrades
  cap_map rows. If only AlphaEdit passes: AlphaEdit is the answer,
  Kerdock can be dropped. If only Kerdock passes: substrate must
  adopt structured keys, which is a real product decision. If
  neither passes: drill Candidate 4 (MUNKEY-style) trade-off
  analysis — would a compliance-focused substrate variant be worth
  shipping as a separate product?
