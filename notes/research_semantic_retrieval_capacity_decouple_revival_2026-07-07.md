# Revival drill: can the semantic benefit be captured without the store-collision? (2x-negative discipline)

Date: 2026-07-07. Owner: research (Sonnet main-thread synthesis + 2 parallel Sonnet lit-scan sub-agents).
Trigger: USER-directed revival drill on the CONFIRMED negative
`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08` (composition
FULL VET: SEM_BEAM Hits@10=0.227 HARD_FAIL vs RANDOM_BEAM=0.502, mean edge-cos sem=0.205 vs rand=0.002).
Per [[feedback-2x-means-depth]]: this is a level-2 operational drill on an existing finding, not a
re-run lit-scan verification.

## HEADLINE

**Partial revival, not a full one, and it separates cleanly into "cheap and probably works" vs
"expensive and probably doesn't buy anything new."** Of the 4 candidate mechanisms, (1) decoupled
two-representation and (3) semantics-as-reranker are the SAME architecture wearing two names — the
literature (Hopfield/SDM correlation-capacity theory + retrieve-then-rerank IR practice) independently
supports both halves, and the internal evidence (RANDOM_BEAM already at 0.502, matching/beating the BGE
bar, achieved with ZERO semantic content in the store) proves the store-capacity half is already solved.
What is NOT yet proven is whether BOLTING semantics on as a downstream, store-untouched reranker adds
anything ON TOP of RANDOM_BEAM's 0.502 — that specific combination has never been run. This is the one
real, cheap, low-risk revival candidate. Mechanism (4), sparse/low-overlap semantic codes, has genuine
distinct theoretical support (Willshaw f^2-scaling, Gripon-Berrou clique codes) but requires re-engineering
the entity codebook and composition algebra, with no literature-proven "sweet spot" formula — a real
second-tier research thread, not a cheap test. Mechanism (2), whitened/decorrelated semantic seeding
IN the store, is the worst-fitted of the four to this specific case: the correlation the whitening would
remove IS the semantic signal itself (there is no separable nuisance direction here, unlike the BERT-
whitening literature's removable frequency artifact), and the store is already operating far past its
classical capacity wall (see quantitative check below), which makes it maximally fragile to any residual
correlation. **Honest bottom line: this is a real (if narrow) revival for the reranker form, and a clean,
literature-confirmed closure for the in-store whitening form.**

## Cheap decisive test

**Add ONE new arm to the ALREADY-BUILT cell** (`experiments/exp_conceptnet_semantic_seeded_beam_composition_v1.py`,
already landed HARD_FAIL FULL, metrics at `data/exp_conceptnet_semantic_seeded_beam_composition_v1/metrics.json`):

**SEM_RERANK arm:** run the substrate-native beam exactly as RANDOM_BEAM does (random bipolar entity
codes, beam_k=K, store untouched) to generate the SAME structurally-valid candidate set RANDOM_BEAM
already produces — then, at final scoring only (after the store computation is done, no store code
changes), break ties among the surviving beam candidates using BGE cosine similarity (the SAME cached
BGE-large teacher embedding already used for SEM_K1/SEM_BEAM, keyed by exact CN_ id, already 100% overlap
per the 2026-07-07 prereg — zero new data dependency). This is close to zero marginal cost: no new
encoding, no new store, no new cache — it reuses RANDOM_BEAM's already-computed candidate list and the
already-cached BGE vectors, adding one new scoring/rerank pass.

## Falsifiable predictions

**HARD-PASS (real revival confirmed):** SEM_RERANK Hits@10 >= RANDOM_BEAM (0.502) + 0.03, AND
nontrivial_lift_hits10 improves measurably over RANDOM_BEAM's own nontrivial_lift (-0.729) — i.e. the
gain is concentrated on the harder (nontrivial) queries, not just noise on the easy ones. This would mean
semantic information genuinely helps DISAMBIGUATE among structurally-plausible beam candidates, and the
decoupled architecture captures real semantic benefit while keeping the store fully decorrelated (capacity
untouched by construction — the store never sees a BGE-derived code).

**HARD-FAIL (no revival; clean closure confirmed):** SEM_RERANK Hits@10 <= RANDOM_BEAM + 0.01
(statistically indistinguishable from the no-semantics baseline). This would mean most of RANDOM_BEAM's
residual error is NOT a tie-breaking-among-close-candidates problem — the beam's substrate-native scoring
already usually separates right from wrong candidates cleanly enough that an external semantic prior has
nothing left to contribute. In this case the honest conclusion is the clean closure: "semantics belong in
retrieval, decorrelated codes belong in the store, and RANDOM_BEAM's parity with BGE is already the right
answer" — not a revival, a confirmed design principle.

**MIDDLE (most likely outcome per calibration below):** modest lift in [0.01, 0.03), fidelity-neutral.
Real but small; would support keeping SEM_RERANK as an optional enhancement layer, not an urgent priority,
and would NOT change the core architectural recommendation (store stays decorrelated either way).

## Ranked mechanisms: captures-semantic-benefit x preserves-store-capacity x glass-box-cheap

| Rank | Mechanism | Captures semantic benefit | Preserves store capacity | Glass-box / cost | Verdict |
|---|---|---|---|---|---|
| **1 (tie)** | (1) Decoupled two-representation + (3) Semantics-as-reranker | UNTESTED but well-motivated (BGE used only to disambiguate structurally-valid candidates, never enters the store) | **FULL, proven** — store is bit-identical to RANDOM_BEAM (already measured 0.502, beats/matches BGE bar with zero semantic content) | Cheapest of the four: reuses existing cached BGE vectors + existing beam candidates, one new scoring pass, store dynamics fully inspectable/untouched | **The one real, cheap, low-risk revival candidate.** Not yet run — this note's cheap decisive test. |
| **2** | (4) Sparse / low-overlap semantic codes | MODERATE, literature-plausible (Willshaw f^2-scaling: lower activity fraction -> quadratically lower expected pairwise overlap for same semantic alignment; Gripon-Berrou clique codes show structured-sparse can approach optimal efficiency) | MODERATE-HIGH in theory, UNPROVEN for this store's elementwise-multiply bipolar composition algebra (no direct sweet-spot formula found in lit-scan; would require re-deriving Gate-C shape compatibility for a sparse-binary entity codebook) | HIGH cost: requires redesigning the entity codebook + composition algebra, not a config toggle | A genuine, distinct second-tier research thread (different geometry class than whitening — bit-sparsity, not vector-decorrelation) — worth a future scoping drill, not a cheap test today |
| **3** | (2) Whitened / decorrelated semantic seeding (ZCA/PCA) | LOW-MODERATE — whitening that removes the correlation removes exactly the semantic signal here, because (per the orthogonality-capacity-lever note's own Item 5) the "safe" form of decorrelation only works on a REMOVABLE NUISANCE direction (e.g. BERT-whitening's shared frequency artifact); this encoder's measured Gram spectrum is a continuous power-law with no clean dominant direction to remove, and the correlation IS the semantic content itself, not a separable artifact | MODERATE at best — likely lands on the SAME smooth SEM<->RANDOM interpolation curve (partial correlation, partial capacity loss), not an escape from the tradeoff; SEM_SCRAM_BEAM's own result (edge-cos 0.052, intermediate between rand 0.002 and sem 0.205, yet Hits@10=0.073, WORSE than both extremes) is a live warning that partial/misaligned correlation can be worse than either pure endpoint | MODERATE cost (one linear transform), but real fidelity risk (Item 5's over-decorrelation HARD-FAIL branch) | Worst-fitted of the four to THIS case despite having the most-developed general literature (frame theory, BERT-whitening) — the literature's own alignment-vs-uniformity tension (Wang & Isola 2020) says you cannot push both ways at once when the correlation to kill IS the alignment signal |

## Quantitative sanity check: does the classical alpha_c(rho) formula predict this collapse?

The chain-graded `correlated_key_capacity_rho_sweep_v1` cell (3/3 seeds HARD_PASS) measured
`alpha_c(rho) ~ alpha_0 * (1 - rho^2)`, `alpha_0=0.138` (Loewe 1998, classical single-shot Hebbian wall).
At the composition cell's measured semantic correlation (mean edge-cos rho~0.20), this formula predicts
`alpha_c(0.20) = 0.138*(1-0.04) = 0.132` — **only a ~4% relative capacity reduction.** The ACTUAL measured
effect (RANDOM_BEAM 0.502 -> SEM_BEAM 0.227, a ~55% relative Hits@10 collapse) is more than an order of
magnitude larger than the classical single-shot wall model predicts. **This is itself a load-bearing
finding, not just a caveat:** the composition store is a CHAINED multi-hop cf-RPE store operating at
edges/N_DIM ~0.98 (near-saturation load, per the 2026-07-07 prereg's SCALE NOTE), i.e. already far past the
classical alpha_c=0.138 wall entirely, in a regime the classical Hebbian formula was never derived for.
Near an already-crossed threshold, small correlation increases can produce disproportionately large
(percolation-style, threshold-sensitive) effects — consistent with this project's own
percolation-critical-phenomena adjacency field. **Practical consequence: mechanism (2) (whitening) is
riskier here than the general orthogonality-capacity-lever note implied**, because that note's "safe
targeted lever" analysis assumed operation near/below the classical wall, not deep past it in an
already-overloaded chained-composition regime.

## Cross-thread synthesis

Directly extends, without re-deriving:
1. `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08` — this
   drill is the requested pressure-test of that memory's own recommendation (decouple retrieval from
   store); the recommendation SURVIVES the pressure-test for the reranker form (mechanism 1/3) and is
   REINFORCED for the in-store whitening form (mechanism 2), which the memory's own framing already
   anticipated as the wrong move.
2. `research_orthogonality_capacity_lever_density_cliff_2026-07-07.md` — imports its central finding
   (targeted decorrelation is safe ONLY on a removable nuisance direction; full/genuine-semantic
   decorrelation is self-defeating per Wang & Isola 2020 alignment-vs-uniformity) and applies it to
   conclude mechanism (2) is a poor fit for THIS specific correlation source (which is semantic content,
   not a nuisance artifact) — the same literature that motivated a cautious "maybe" for dedup/whitening in
   general motivates a firmer "no" for whitening this specific semantic-seed correlation.
3. `exp_conceptnet_semantic_seeded_beam_composition_v1` FULL metrics (HARD_FAIL, verified off-disk at
   `data/exp_conceptnet_semantic_seeded_beam_composition_v1/metrics.json`) — all four internal numbers
   used above (RANDOM_BEAM=0.5021, SEM_BEAM=0.2275, SEM_SCRAM_BEAM=0.0730, mean edge-cos sem=0.2045 /
   rand=0.0021 / scram=0.0517) are read directly from that file, not recalled from memory.
4. `correlated_key_capacity_rho_sweep_v1` (3/3 seed CHAIN_GRADE HARD_PASS, verified off-disk at
   `data/exp_correlated_key_capacity_rho_sweep_v1_seed_{7,13,19}/metrics.json`) — supplies the classical
   `alpha_c(rho)` law used in the quantitative sanity check above, and the sanity check itself is a NEW
   cross-thread connection this drill contributes (nobody had previously checked whether the classical
   wall-shift formula's magnitude matches the composition cell's measured collapse — it badly does not,
   which is itself informative about the composition store's operating regime).
5. 2 external lit-scans this cycle (below) — first confirmation that "decouple correlated retrieval from
   decorrelated storage" has independent support in BOTH associative-memory theory (Hopfield/SDM) and IR
   practice (two-tower + rerank), even though no single paper names the combined principle.

## Substrate-product implications

For Director / exp_dev: this drill recommends exactly ONE next action, at near-zero marginal cost — add
a SEM_RERANK arm to the already-built, already-landed `exp_conceptnet_semantic_seeded_beam_composition_v1`
cell (reuse RANDOM_BEAM's beam output + already-cached BGE vectors; one new scoring pass, no new store, no
new encoding). This is the cheapest possible test of the one mechanism this drill identifies as a genuine,
low-risk revival candidate. It does NOT recommend re-attempting in-store semantic seeding (mechanism 2,
whitened or otherwise) at this store's current operating point — the quantitative check above shows this
store is already deep past its classical capacity wall, making any residual in-store correlation
disproportionately risky, and the semantic correlation here has no separable nuisance component to safely
remove. Mechanism (4) (sparse/low-overlap semantic codes) is named as a legitimate future research thread
(a genuinely different geometric lever, with real literature support) but is NOT a cheap test — it would
need its own scoping drill on codebook redesign before any cell is authored, and should not be conflated
with or substituted for the cheap SEM_RERANK test above. If SEM_RERANK HARD_PASSes, that becomes the new
substrate-product-relevant design pattern: "structural composition stays decorrelated/random for capacity;
semantic content is applied ONLY as a final, external, store-untouched reranking/disambiguation layer" —
directly usable for any future KG-completion or multi-hop retrieval feature.

## Citations (verified count)

**2 parallel Sonnet lit-scan sub-agents this cycle**, generic math/CS/ML/IR terms only per
[[feedback-query-privacy-decomposition]] — zero substrate-novel mechanism names, zero numeric parameters
from this project, sent externally.

**Decoupled retrieval-vs-storage sub-agent (9 sources, 6 distinct findings reported):** Two-tower /
dual-encoder retrieval architecture docs (Google Cloud, EmergentMind, Glassdoor Engineering blog);
bi-encoder vs cross-encoder retrieve-then-rerank cost/benefit (ZeroEntropy, Weaviate); Kanerva Sparse
Distributed Memory address/content split (NASA technical report; Kanerva Machine, DeepMind arXiv:1804.01756,
2018); Hopfield network capacity vs correlated patterns / pseudo-orthogonalization (Springer 2014 chapter;
"Effects of Feature Correlations on Associative Memory Capacity," arXiv:2508.01395, 2025 — direct external
confirmation of the SAME qualitative finding as this project's own chain-graded
`correlated_key_capacity_rho_sweep_v1`); DNC/NTM content-addressing key-vs-value separation (Wikipedia;
Acolyer NTM review); LSH candidate generation + exact-verification near-dup detection pipelines. Sub-agent's
own verdict: "strong adjacent precedent, moderate-confidence extension" — no single paper names the
combined principle, but two independent literatures (associative-memory theory, IR practice) converge on
it. Flagged as NOT independently verified beyond a single source: the general claim that no paper unifies
both literatures (an absence-of-evidence claim, not a positive citation).

**Sparse/low-overlap coding sub-agent (10 sources, 8 distinct findings reported):** Willshaw/Palm sparse
associative memory capacity theory (Phys. Rev. A 41:1843, 1990; arXiv:2603.26217) — the f^2 overlap-scaling
law used in this note's ranking table; Gripon & Berrou clique-based sparse associative memories
(arXiv:1411.1224; J. Stat. Phys. 2016); Winner-Take-All Autoencoders (arXiv:1409.2752) and group-sparse
kWTA coding (PMC3403521); Ahmad & Hawkins Sparse Distributed Representations properties paper (direct
statement of the overlap-vs-capacity-vs-false-match tradeoff); mutual-coherence compressed-sensing recovery
bound (arXiv:1508.03117); Sparse Ternary Codes for similarity search (arXiv:1701.07675 — **flagged
unverified beyond abstract/title, full text not extractable**); sparse similarity-preserving hashing
(arXiv:1312.5479); sparse Johnson-Lindenstrauss transforms. Sub-agent's own verdict: "plausible, well-
supported middle ground, not yet a single unified proven law — moderate confidence, not proof-tier."

**Verified count: 19 distinct external sources found via live web search across 2 sub-agents this cycle
(1 of the 19 explicitly flagged as unverified-beyond-title), zero fabricated citations.** This note's
central claims are a SYNTHESIS across these sources plus 4 internal, off-disk-verified measurements
(composition FULL metrics.json, 3-seed correlated-key-capacity metrics.json files, the orthogonality-
capacity-lever note, and the correlation-hurts-capacity memory) — not a single lifted result.

## P_deflated (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

- P(SEM_RERANK arm achieves HARD-PASS, i.e. genuine lift over RANDOM_BEAM concentrated on nontrivial
  queries): undeflated ~0.45-0.55 (mechanistically well-motivated by 2 convergent literatures + the
  store-untouched design eliminates the dominant known failure mode) -> **P_deflated = 0.25-0.35**
  (deflated 0.20 for novel-combination-never-run status; this exact arm has not been tested on this cell).
- P(MIDDLE outcome, modest but real lift): this drill's own modal expectation, **~0.40-0.45** (consistent
  with the general pattern that most single-cycle "add a cheap enhancement layer" cells land in MIDDLE,
  per this project's own base rates).
- P(mechanism 4, sparse/low-overlap codes, would beat mechanism 1/3's ceiling if built): undeflated
  ~0.30-0.35 (real distinct literature support, but no direct sweet-spot proof found) -> **P_deflated =
  0.15-0.20**, capped low because this requires a structural re-encoding this drill has not scoped in
  detail (flagged as a future scoping-drill candidate, not a numeric claim to act on directly).
- P(mechanism 2, whitened in-store seeding, would clear the orthogonality note's own HARD-PASS bar
  at THIS store's operating point): undeflated ~0.15-0.20 (already low in the general note; the
  quantitative alpha_c(rho) mismatch found in this drill is new evidence pushing this LOWER still,
  since the store is shown to already operate far past the regime that formula's small-effect prediction
  assumed) -> **P_deflated = 0.05-0.10**, the weakest and most confidently-closed claim in this note.

## Honest bounds

This is a design-scoping drill, not a dispatched experiment — no cell has been run for SEM_RERANK yet.
The ranking above is a synthesis of internal off-disk-verified measurements (high confidence, these are
real landed VET numbers) plus external lit-scan (moderate confidence, generic-term search, 2 independent
sub-agents, 1 title-only unverified citation flagged). The mechanism-1/3 recommendation is the strongest
claim in this note because it requires the LEAST new inference (the store-capacity half is already proven
by RANDOM_BEAM's landed 0.502; only the reranker's incremental lift is genuinely unknown). The mechanism-2
closure is the second-strongest claim (directly grounded in a literature-confirmed general tension applied
to a specific, already-measured spectral property of this encoder). The mechanism-4 assessment is the
most speculative of the three substantive claims (real literature, zero substrate-specific validation).
