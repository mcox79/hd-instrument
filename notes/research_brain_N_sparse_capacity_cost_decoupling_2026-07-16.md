# Research: brain effective dimensionality + can sparse-high-N circumvent the dense-N cost (USER challenge)

Filed by: research (Opus synthesis over 3 parallel Sonnet lit-scan sub-agents: brain population
dimensionality, sparse-code cost/capacity decoupling, sparse-VSA algebra fidelity) plus this
project's own prior on-disk experimental record (heavy reuse, not restated from scratch).
Date: 2026-07-16.
Trigger: USER challenge — "the downsides of a massive N must be circumventable" — decides whether
the substrate should move from dense FHRR N~1024 toward large sparse N.

---

## HEADLINE

**The USER's intuition is PARTIALLY RIGHT, in a precisely specifiable way, and this project
already ran the experiment that shows exactly where it breaks.** Sparse coding is a real,
textbook-grade capacity multiplier (Willshaw/Tsodyks-Feigel'man/Amari: capacity ~ N/(a|ln a|),
peaking at optimal sparsity a*~ln(N)/N, giving ~0.69 bits/synapse vs ~0.29 dense) — but that gain
comes specifically from making the **identity of which k-of-N units are active** the code (a
combinatorial address space of size C(N,k)), not from taking an existing dense code and zeroing
out entries. **This project already tested the wrong version of "sparse" and it HARD-FAILED**
(sparsifying VALUES on the existing dense code: capacity ratio 0.40-0.94 vs dense, i.e. worse) —
diagnosed at the time as "capacity was key-collision-limited, not value-limited; the
Tsodyks-style benefit needs sparse KEYS/PATTERNS, not sparse values"
(`notes/exp_dev_to_research_sparse_value_CLOSED_2026-06-08.md`,
`notes/exp_dev_to_research_DIMSPARSE_result_2026-06-06.md`). Separately, this project already
built and HARD-PASSed a genuinely combinatorial-address sparse code — the block-local sparse
resonator (K active per block, one-hot-per-block structure) — which recovered K4=1.00, K8=1.00
factor-recall, algebra-clean
(`data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json`). **The pieces to do
this correctly already exist on this substrate; they have just never been pointed at the
bundling/associative-capacity question at large N'.** On brain dimensionality: there is no
neuroscience finding that validates Kanerva's N~10^4 as a *measured* population-code
dimensionality — that number is an anatomy-inspired VSA modeling choice, not an empirical result.
Effective/intrinsic dimensionality of real neural populations is consistently far below raw
neuron count and is **task/condition-dependent, not a fixed brain constant** — the brain does not
converge on one operating N; it converges on a *sparsity regime* (region-specific, ~1-5%
cortex, ~2-6% dentate gyrus/CA3, contested for cerebellum) for the same reason (combinatorial
capacity + energy cost + pattern separation), independent of what raw N happens to be available.

P_deflated = 0.40 (see full derivation in Falsifiable-predictions section; underlying capacity
math is well-established/textbook, cross-validated by 3 independent classical derivations, but
(a) no VSA paper in any literature this cycle empirically tests bind/bundle/cleanup beyond
N~512-2048 — a 25-200x extrapolation gap to the N regime this decision is about — and (b) this
project's OWN prior evidence on naive sparsification is a hard negative that must be respected,
capping confidence below the novel-synthesis ceiling of 0.50).

---

## (a) Brain effective dimensionality — honest numbers, with counting caveats

**The single most important methodological point:** "dimensionality" in this literature means at
least three different, routinely-conflated quantities, and none of them is "the" brain N:

1. **Raw substrate size** — neurons anatomically available / recorded (upper bound only, not
   functional).
2. **Effective/intrinsic dimensionality** (participation ratio, PCA elbow, tensor-component
   rank) — a statistical property of population covariance that depends on task/stimulus
   richness, recording modality, and trial count. Gao & Ganguli's own finding (2015, *Curr Opin
   Neurobiol*) is that this number **scales with the number of task conditions**, i.e. it is not
   a fixed brain property, it is an experiment-contingent measurement.
3. **Task-relevant readout subspace** — what a downstream circuit actually reads out; often far
   smaller than either of the above (most decoding/BCI work operates in ~2-10 dimensions even
   when the underlying manifold is richer).
4. **Sparsity (fraction active)** — a related but distinct fourth quantity; a code can be
   simultaneously sparse AND high-dimensional, or dense AND low-dimensional.

**Load-bearing numbers, ranked by how well-replicated they are:**

- **Dentate gyrus / CA3 sparsity: 2-6% of granule cells active per memory representation** —
  the best-replicated number in the whole scan, converging across engram-tagging/IEG studies and
  independent modeling (PMC4867142, PMC8176757, PMC5217096, PMC4312091). Textbook-grade.
- **Cortical population dimensionality is genuinely high for rich stimuli but still << N, and NOT
  a fixed number.** Stringer et al. 2019 (*Nature*, ~10,000 mouse V1 neurons recorded) found the
  natural-image population code follows a smooth 1/n power-law eigenspectrum — much richer than
  an earlier "everything is low-dimensional" narrative — yet still mathematically bounded well
  below raw N by a smoothness constraint. For simpler tasks (motor, decision, working memory),
  Gao & Ganguli-lineage work finds participation-ratio dimensionality of only **~2-30**, scaling
  with condition count. Both are real, well-cited findings about **different task regimes** —
  neither is "the" brain dimensionality.
- **Mixed selectivity raises effective dimensionality above single-variable tuning**
  (Rigotti/Fusi 2013, *Nature*): PFC neurons carry nonlinear conjunctive selectivity, and
  linear-readout task performance (XOR-type problems) requires it — a mechanistic reason cortex
  doesn't sit at minimal dimensionality even though it could. Well-cited, moderately replicated.
- **Cerebellar granule-cell sparsity: contested.** The classical Marr-Albus "codon theory"
  prediction (~5-10% active, motivating Kanerva's own anatomical inspiration for SDM) is now
  challenged by recent in-vivo imaging showing denser, lower-dimensional activity than predicted
  (Frontiers 2022; PMC9815768; arXiv 2003.05647). Treat as an open, actively-revised debate, not
  settled fact — this directly affects how much weight to put on "cerebellum is THE sparse-coding
  exemplar."
- **Cortical "percent active" broadly: genuinely contested, range 1-40% depending on
  method/threshold.** Energy-budget arguments (Attwell & Laughlin 2001) favor low simultaneous
  activity (≤15%, possibly <1%) for metabolic reasons; looser spike/subthreshold criteria give
  much higher numbers. Barth & Poulet (2012) confirm a skewed lognormal firing-rate distribution
  (sparse high-firing tail) without converging on one percentage. **Least well-converged number
  in this set — do not cite a single cortical sparsity percentage as settled.**
- **Concept-cell/MTL sparsity ~0.1%** (Waydo, Kreiman & Koch 2006) — single-study, extrapolated
  from single-unit hit-rates, order-of-magnitude only.
- **Kanerva's N~10^4 premise: NO independent neuroscience validation found.** Every directly
  measured population-code dimensionality in this scan (participation ratio, embedding
  dimension) lands 2-3 orders of magnitude below 10^4 for the task regimes actually studied,
  though Stringer-style "richness scales with stimulus complexity" results leave room for
  larger numbers under sufficiently rich naturalistic input that hasn't been measured that way.
  The historical link is structural/anatomical (SDM was modeled on cerebellar granule-cell
  circuitry, expansion recoding, sparse random addressing) — not a validated "brain operates at
  dimensionality ~10^4" empirical finding. **Treat Kanerva's N as an anatomy-inspired engineering
  choice, not a measured neuroscience constant** — this matters because it means there is no
  brain-derived floor or ceiling that argues FOR any specific target N' on this substrate; the N
  choice has to be justified on the substrate's own capacity/cost math, not on "the brain uses
  N~10^4."

**Is there a principled "operating N," or is it region-dependent?** Region-dependent, with one
unifying invariant: the brain does not converge on one dimensionality, it converges on a
**sparsity regime matched to available N and task demands in each region** (DG very sparse for
one-shot pattern separation of episodic content; cortex moderately sparse for rich sensory
manifolds; cerebellum contested but directionally an expansion-then-selective-readout scheme).
The invariant across regions is the MECHANISM (expand, then sparsify, then let a simple linear
readout exploit the combinatorial address space) — not a fixed number.

---

## (b) Sparsity as cost-circumvention — the crux, with the honest full accounting

**Bottom-line verdict from the literature (converging independently across 3 sub-scans): the
"no downside" intuition is PARTIALLY TRUE and breaks in specific, nameable places — never
disappearing to a literal O(k) free lunch, but genuinely buying a large, real reduction.**

**Where it holds (real, textbook-grade):**
- Combinatorial address-space capacity is real: Willshaw/Buneman/Longuet-Higgins (1969) +
  Tsodyks & Feigel'man (1988) + Amari (1989) independently derive the same rise-then-fall shape —
  capacity per synapse is poor at dense coding (crosstalk dominates), rises with sparsity, peaks
  near optimal sparsity a*~ln(N)/N (~0.69 bits/synapse vs ~0.29 dense/Gardner bound), then FALLS
  again if pushed sparser still (too little redundancy survives cleanup noise). This is the
  mechanism that makes "bounded neurons -> combinatorially large capacity" true: for k<<N,
  C(N,k) vastly exceeds N.
- Structured (block-sparse, one-active-per-block) codes sidestep the density-inflation problem
  ARCHITECTURALLY: bind (within-block circular shift) preserves the one-active-per-block
  invariant automatically, no explicit re-thinning step needed (Frady/Kleyko/Sommer resonator
  program; Hersche et al. factorizer, arXiv:2303.13957). This is the cleanest, best-corroborated
  finding across all 3 sub-scans, and it is EXACTLY the structure this project already built and
  proved algebra-clean (blocklocal-K26, K4=1.00/K8=1.00 recall).

**Where it breaks (specific, quantified costs that do NOT vanish):**
1. **Search/lookup cost is relocated, not eliminated.** Naive Kanerva SDM read/write requires
   Hamming distance to ALL M hard locations — O(M*N), not O(k). Kanerva's own writing flags this
   as the main computational bottleneck; hardware parallelism hides it, it does not remove the
   total work. LSH/ANN buys sublinear-in-M query time but SELLS exact recall (approximate,
   tunable false-positive rate) and pays extra index-memory — a genuine, provable time-space
   tradeoff (no simultaneous small-memory + fast-query + exact-recall regime exists).
2. **A log(N) floor is structural, not an implementation artifact.** Compressed-sensing theory
   (Donoho-Tanner phase transitions; Candès-Tao) proves recovery of a k-sparse signal in
   dimension N needs measurements ~ C*k*log(N/k) — sparsity buys a huge reduction from N down to
   ~k*log(N/k), but N never fully disappears; it re-enters logarithmically. There is no regime
   in the literature where cost is truly independent of N.
3. **Operation-compatibility cost for UNSTRUCTURED sparse codes.** Naive disjunctive/OR bind of
   two independent sparse vectors inflates density (documented ~2x active-bit growth); the fix
   (context-dependent thinning, Rachkovskij & Kussul 2001) is an explicit extra sort/threshold
   pass — real added compute, not free. Frady/Kleyko/Sommer's own complexity analysis shows
   binding cost is O(N) at linear sparsity but degrades to **O((N/beta)*ln N) — worse than
   linear — under extreme sparsity**, directly falsifying "sparser is always cheaper" in the
   unstructured case. Structured block-sparse codes avoid this specific tax (point above), but
   their decode is still O(D_i * sqrt(D_o)) for the factorizer, not O(k) — sub-N but supra-constant.
4. **Superposition catastrophe: a sharp cliff, not smooth degradation.** Both the sparse-VSA and
   this project's own prior lit-scan (`notes/research_brain_capacity_efficient_language_mechanisms_vsa_analogs_2026-07-16.md`)
   independently confirm sparse bundling capacity is roughly flat then collapses sharply past a
   threshold — crosstalk variance crossing signal margin, structurally analogous to Bloom-filter
   saturation. Operationally this means the correct experimental design looks for a THRESHOLD
   crossing, not a trend line.
5. **The optimal sparsity is much sparser than intuition suggests, and barely grows with N.**
   Working the classical a*~ln(N)/N formula: at N=1024, k*~7; at N=50,000, k*~11; at N=100,000,
   k*~11.5. The optimum is nearly FLAT in absolute active-count as N grows by 100x — it is NOT
   "keep the same fraction active," it is "keep roughly the same SMALL absolute count active."
   A design that fixes k=20-100 "because that felt reasonable" would sit 2-14x denser than the
   classical optimum at these N — a real design-parameter risk worth flagging before committing
   to a specific k.
6. **No empirical VSA precedent above N~512-2048.** The largest confirmed operational sparse-VSA
   demonstration in the literature (Hersche et al.) is D=512, 4 blocks; Frady/Kleyko/Sommer's
   binding paper swept only to N~1500. Moving to N'~16,000-100,000 is a 10-200x extrapolation
   beyond any published empirical sparse-VSA result — genuinely uncharted territory, not
   "well-trodden ground with different constants." (This project's own substrate has separately
   run dense-code experiments up to N=16384-32768 for unrelated purposes — meaning the substrate
   is already, incidentally, ahead of the published sparse-VSA empirical envelope in raw N; this
   is a genuine opportunity to generate the first real data point in this size regime, not
   purely a risk.)

**The single most load-bearing distinction for this project specifically:** capacity gain comes
from sparse **KEYS/PATTERNS** (which k-of-N units are active IS the address/identity — a new,
combinatorially large address space), not from sparse **VALUES** (zeroing entries of an
otherwise-fixed-identity dense vector). This project already ran the value-sparsification
experiment and it HARD-FAILED (ratio 0.40-0.94, worse than dense) — fully consistent with, not
contradicting, the literature: value-thinning doesn't touch the combinatorial address space at
all, so of course it bought nothing. The correct sparse code to test is the pattern/key kind
this project has ALSO already built and proven algebra-clean (blocklocal-K sparse resonator) —
it has just never been pointed at the associative-bundling-capacity question this task is about.

---

## Cheap decisive test

**Reuse the existing blocklocal-K sparse resonator code (already built, already HARD-PASS on
factor recall) as a BUNDLING/associative-store code, not just a factorization code, and sweep
total dimension N' at fixed near-optimal per-block active count.**

Arms (all CPU-cheap, reuse existing primitives verbatim where possible):
1. **DENSE_BASELINE** — current dense FHRR N=1024 additive-bundling capacity curve (already
   measured in prior cells — reuse, don't re-run).
2. **BLOCKSPARSE_N1024** — blocklocal-K sparse code at the SAME total dimension N'=1024, k near
   the classical optimum for N=1024 (k*~7, sweep {4,8,16} to bracket it), bundle J items, measure
   max recallable J at fixed recall threshold via the factorizer/resonator decode (NOT brute-force
   argmax — use the already-proven decode primitive).
3. **BLOCKSPARSE_N4096 / N16384** — same code, same near-optimal absolute k (NOT the same
   fraction — per finding (5) above, k should stay roughly flat, not scale with N), total
   dimension raised to N'=4096 and N'=16384. Measure max recallable J at the same recall
   threshold and the same fixed per-item compute budget (active-set-only ops).

**Primary metric:** max bundled items J at >=90% recall, as a function of N', compared against
raw dimension growth (is capacity growth closer to C(N',k) combinatorial, i.e. much faster than
linear in N', or is it flat/sublinear like the value-sparsification result)?

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** capacity (max J at 90% recall) at N'=16384 (near-optimal k) grows by >=4x over
  the DENSE_BASELINE N=1024 capacity, at equal or lower per-item decode compute (active-set-only
  ops, not O(N') brute force) — confirms combinatorial address-space scaling is real on this
  substrate and the structured-block-sparse route is the correct way to buy it.
- **MIDDLE_BAND:** capacity grows 1.5-4x — real but modest lift; worth a second iteration on
  k-tuning or block-width before further scaling N'.
- **HARD-FAIL:** capacity growth <1.5x (flat, matching the value-sparsification ratio 0.40-0.94
  pattern) — this would mean the substrate's associative/bundling capacity ceiling is bottlenecked
  by something upstream of the address-space size (e.g. the codebook/key-generation process
  itself producing collisions independent of how large the nominal address space is) — sparse-
  high-N would NOT rescue it either, and the fix has to happen at the KEY-GENERATION level (how
  codes are chosen to be near-orthogonal), not by adding dimension. This exact HARD-FAIL would be
  the third data point (after the two value-sparsification closures) supporting "this substrate's
  capacity bottleneck is structurally about key/pattern collision, not about available dimension
  or value-density," which would be a strong, convergent, cap_map-worthy finding.
- **Search-cost sanity check (secondary, no compute needed):** confirm the decode path used is
  the resonator/factorizer (sub-N, proven O(D_i*sqrt(D_o))-class cost), NOT a brute-force O(N'*M)
  scan — if a naive nearest-neighbor scan is used instead, any capacity win would be confounded
  by an uncontrolled cost increase and the HARD-PASS reading above would not support a "free
  cost" claim, only a "capacity is real, cost still needs the right decode partner" claim.

---

## Cross-thread synthesis

- `notes/exp_dev_to_research_sparse_value_CLOSED_2026-06-08.md`,
  `notes/exp_dev_to_research_DIMSPARSE_result_2026-06-06.md` — the two existing HARD-FAIL
  closures on naive value-sparsification are NOT contradicted by this drill's literature; they
  are explained by it (sparse values != sparse keys/patterns), and they set the HARD-FAIL bar
  above (capacity growth <1.5x) as the exact signature to watch for again.
- `data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` — the existing
  HARD-PASS structured block-sparse primitive (K4=1.00, K8=1.00 factor recall) is the correct
  reusable building block for the cheap decisive test above; it has never been retargeted at
  bundling/associative capacity specifically (only factorization).
- `notes/scour_prior_work_sparse_retrieval_at_2pct_inventory_2026-07-04.md` — separately
  established that for the SEMANTIC-retrieval encoder task, the code is not the bottleneck (a
  training-objective gap is); that finding is orthogonal to this drill, which is about
  associative/bundling CAPACITY at large N', not semantic-neighbor fidelity. Do not conflate the
  two tasks when reading either note.
- `notes/research_brain_capacity_efficient_language_mechanisms_vsa_analogs_2026-07-16.md` —
  today's companion drill already flagged the sparse-coding capacity-fix menu item and the
  superposition-catastrophe cliff shape; this drill adds the brain-dimensionality grounding, the
  full cost-accounting (search/log(N)/operation-compatibility taxes), and the concrete reuse of
  this project's OWN already-proven block-sparse primitive as the next cheap test — sharpening
  that menu item from "sparse coding, generically" to a specific, already-buildable cell.
- `notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md`
  (Rank 3) — already identified the DGProjection expand+sparsify front-end as untested against
  the bundling-capacity failure mode (only tested against a search/convergence wall previously,
  the wrong failure-mode class). This drill's cheap decisive test is a more specific, block
  structured variant of that same open Rank-3 item — treat as convergent, not duplicate.
- `notes/research_degree_agnostic_sparse_tail_relational_encoding_brain_first_2026-07-08.md` —
  independently converges on "expand then sparsify" (DG-style) as the degree-agnostic mechanism
  for a completely different task (sparse-tail relational encoding); the repeated convergence of
  "expand-then-sparsify" across three independent tasks (bundling capacity, sparse-tail encoding,
  and this drill's brain-N question) is itself a signal the mechanism is load-bearing generically
  on this substrate, not task-specific.
- `notes/research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md` —
  prior SDM drill for a DIFFERENT purpose (noise-robustness cleanup, not capacity) already
  flagged the same O(M*N) search-cost fact this drill's cost-accounting reconfirms
  independently; consistent, not new information, but worth noting the SDM route was scoped for
  robustness, not for the capacity question this drill addresses.

---

## Substrate-product implications

Framed as product roadmap, not publication: the honest answer to "can we get big-N capacity/SNR
without big-N cost" is **yes, partially, via a SPECIFIC mechanism (structured block-sparse
combinatorial addressing) that this substrate has already built and proven algebra-clean, but
no, not for free** — real costs remain in decode complexity (sub-N but supra-constant), in a
log(N) measurement/redundancy floor, and in needing the RIGHT decode partner (resonator/
factorizer, not brute-force scan) to realize the win. The product-relevant framing: "bounded
compute, near-combinatorial capacity, via a proven-in-house sparse code" is a defensible,
differentiated claim (matches the L5 SDM note's LLM-categorical-gap positioning: no LLM
architecture has an analogous distributed-redundancy-with-combinatorial-addressing memory). It
is NOT "unbounded capacity at no cost" — that framing would be false per the log(N) floor and the
decode-complexity floor above, and should never be used in product messaging. The immediate,
concrete next step is the cheap decisive test above: it reuses two already-existing, already-
certified primitives (blocklocal-K resonator decode + the existing dense-N=1024 bundling-capacity
baseline) and requires no new architecture, only a new pairing of two things this project already
has. If it HARD-PASSes, the move from N=1024 to a much larger structured sparse N' becomes a
substrate-native combinatorial-capacity lever with a known, bounded decode-cost tax — a genuinely
new capability tier. If it HARD-FAILs, it converges with the two existing value-sparsification
closures into a strong, three-way-corroborated finding that this substrate's capacity ceiling is
about key/codebook collision, not about available address-space size — which redirects future
capacity work toward codebook-generation quality (near-orthogonality enforcement at the encoding
layer) rather than toward N or sparsity at all.

---

## Citations (verified count)

**~28 distinct sources, all live WebSearch-verified this cycle across 3 independent Sonnet
lit-scan sub-agents**, spanning:
- Brain dimensionality: Liu/Ryan/Tonegawa engram-tagging reviews (PMC8176757, PMC4867142,
  Nature Comms 41467-022-29384-4); dentate gyrus/CA3 sparsity (PMC5217096, PMC4312091); Gao &
  Ganguli 2015 *Curr Opin Neurobiol* + "theory of multineuronal dimensionality" (Ganguli lab);
  Stringer, Pachitariu, Steinmetz, Carandini, Harris 2019 *Nature* (high-dim V1 population
  geometry); Rigotti, Fusi et al. 2013 *Nature* (mixed selectivity); Attwell & Laughlin 2001
  *J Cereb Blood Flow Metab* (energy budget); Barth & Poulet 2012 *Trends Neurosci* (sparse
  firing evidence); Olshausen & Field (sparse coding); cerebellum/Marr-Albus contested-sparsity
  (PMC9815768, arXiv:2003.05647); Waydo, Kreiman & Koch 2006 *J Neurosci* (concept-cell
  sparsity); Kanerva SDM background (Wikipedia, Redwood/Berkeley PDF).
- Sparse cost/capacity accounting: Donoho-Tanner compressed-sensing phase transitions;
  Candès & Tao (2005-06); Kanerva *SDM and Related Models* (O(M*N) search-cost admission);
  Indyk-Motwani LSH lineage; arXiv:1605.02701 (LSH time-space lower bounds); Frady, Kleyko &
  Sommer arXiv:2009.06734 (binding complexity, O((N/beta)*ln N) extreme-sparsity tax); Hersche et
  al. arXiv:2303.13957 (Factorizers for Distributed Sparse Block Codes); Rachkovskij & Kussul 2001
  *Neural Computation* (context-dependent thinning).
- Sparse VSA algebra: Tsodyks & Feigel'man 1988 *Europhys Lett*; Amari 1989 *Neural Networks*;
  Willshaw/Buneman/Longuet-Higgins 1969 *Nature*; Knoblauch/Palm/Sommer 2010/2012 (capacity
  survey); Schlegel et al. arXiv:2001.11797 (VSA comparison, density-inflation measurement);
  Laiho/Poikonen/Kanerva/Lehtonen 2015 BioCAS; Kleyko et al. HDC/VSA surveys arXiv:2111.06077 /
  arXiv:2106.05268; Kleyko et al. Autoscaling Bloom Filter arXiv:1705.03934; Kent, Frady, Sommer,
  Olshausen "Resonator Networks" arXiv:1906.11684; arXiv:2412.00354; Clarkson, Ubaru & Yang
  arXiv:2301.10352.

**Calibration applied per [[feedback-lit-scan-calibration-penalty]]:** underlying capacity math
(Willshaw/Tsodyks-Feigel'man/Amari, cross-derived 3 independent ways) treated as HIGH confidence
(~0.75-0.85). Deflated to P_deflated=0.40 for: (1) zero empirical VSA precedent above N~512-2048,
a 10-200x extrapolation gap to the N regime in question; (2) this project's own prior negative
evidence on naive (value) sparsification, which must weigh against optimism about sparsity
generically even though the specific mechanism being proposed here (pattern/key sparsity via the
already-proven block-sparse primitive) is distinct from what failed; (3) novel-synthesis cap
(this specific graft — reusing the factorizer as a bundling-capacity code at large N' — has never
been tested on this substrate or, per the lit-scan, on any published substrate at this scale).

---

## Next-drill candidate

If the cheap decisive test HARD-PASSes: `sparse-coding-compressed-sensing` (Tier-1b field, already
flagged adjacent to free-probability/AMP-VAMP) — specifically Donoho-Tanner phase-transition
scaling applied directly to this substrate's measured k*/N' operating point, to get a
quantitative prediction for the NEXT N' scaling step before running it.
If it HARD-FAILs: pivot to codebook/key-generation quality as the field to drill next
(near-orthogonality enforcement, structured-not-random key assignment) — the literature basis for
that pivot is already partially in hand from this drill's own Willshaw/Tsodyks discussion of what
"pattern" sparsity actually requires (near-orthogonal key selection, not just any k-active
assignment).
