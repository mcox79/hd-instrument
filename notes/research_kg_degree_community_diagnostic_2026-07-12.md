# Research: KG degree-distribution / community-structure diagnostic — the graph-shape prerequisite for reasoning-vs-frequency and for a factorized map-builder (2026-07-12)

Synthesis drill, 3 parallel Sonnet lit-scan sub-agents (degree/topology stats vs link-prediction difficulty and
popularity-baseline strength; graph-structural prerequisites for TEM-style reusable relation-operators; brain
semantic-network community/schema structure) + director on-disk re-read of everything already measured about CSKG's
actual topology. **Design-only cycle, no local compute, per the no-local-smokes lock** — the deliverable is a
pre-registered, REMOTE-runnable diagnostic spec, not a set of already-computed numbers. This closes a next-drill
candidate flagged 3x across `research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`,
`research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`, and the field advisor's own Tier-1b
`network-science-graph-theory` entry.

---

## HEADLINE

1. **We already have three-quarters of the raw material for this diagnostic sitting on disk, unprocessed into the
   specific statistics this mission asks for.** `cskg_commonsense_core_kcore_density_gate_2026-07-10.md` measured
   the full k-core decomposition (full graph: 2,159,195 nodes, max degree 11,037, avg-deg 4.79; cross-cutting
   subgraph: 501,391 nodes, avg-deg 4.73, degeneracy 147; 12-core = 23,632 nodes @ avg-deg 38.4) and
   `data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json` shows the ACTUAL graph the fair-test ran on
   (`k_core: 12`, N=25,752 entities, 29 relations, backdoor_r=0.3118 FAILING the <0.20 gate, POP winning the
   high-degree tertile 0.4155 vs ROTATE 0.3955). **What is missing is not the graph — it is the specific
   statistics**: Gini coefficient of the degree distribution, a proper Clauset-Shalizi-Newman power-law exponent
   fit, max/mean-degree ratio measured WITHIN the 12-core test graph itself (not the pre-core-extraction full
   graph), a global clustering coefficient, a Louvain/Leiden modularity score with community-vs-relation-type
   cross-tab, and a per-relation cardinality-heterogeneity profile. None of these six numbers has been computed yet
   on this substrate — this drill's job is to specify exactly how to compute them and what they would mean.
2. **The literature gives no single formula linking degree-skew to popularity-baseline strength, but it gives
   several independently strong, converging proxies — and one genuinely alarming 2025 result that changes how the
   whole cheap-decisive-test question should be read.** Aiyappa, Wang, Kim, Seckin, Yoon, Ahn & Kojaku ("Implicit
   Degree Bias in the Link Prediction Task," ICML 2025, arXiv:2405.14985) show that **standard negative-sampling
   link-prediction evaluation is ITSELF implicitly degree-biased** — a pure-degree null predictor becomes
   near-optimal under the standard protocol, independent of any property of the learned model. This means the
   already-observed `backdoor_r=0.31` failure on our own cell is not just a property of the GRAPH's skew, it may
   partly be a property of the EVALUATION PROTOCOL itself — a genuinely new, more actionable framing than
   "the graph is too skewed," because protocol fixes (degree-corrected negative sampling, per Aiyappa et al.) are
   cheaper than architecture fixes. This should be folded into the next fit-design cycle regardless of what this
   diagnostic's graph-shape numbers come back as.
3. **Per-relation cardinality heterogeneity, not aggregate graph skew, is the most load-bearing and best-evidenced
   finding this drill surfaced for the "does a shared relation-operator even make sense" question.** TransH (Wang
   et al., AAAI 2014) already stratifies FB15k relations into 1-1/1-N/N-1/N-N (~24/23/29/24% split) specifically
   because a single global relation vector fails once a relation mixes cardinality regimes; TransR/TranSparse/RotatE
   extend this with the same underlying complaint — RotatE (Sun et al., ICLR 2019, arXiv:1902.10197) proves TransE
   cannot represent symmetric relations at all. **CSKG's own dominant cross-cutting relations are known, named,
   heterogeneous-by-construction**: ATOMIC's `xEffect`/`xWant`/`oReact`-class relations are inherently one-to-many
   (one event has many plausible effects) while `PartOf`/`AtLocation`/`Causes` are closer to 1-1 or 1-N in a
   structurally different, more constrained way. **This drill's single sharpest, most falsifiable prediction is
   that the 29 relations in the actual test graph are NOT uniform in cardinality pattern, and that the relations
   with the WORST cardinality purity are exactly the ones already flagged as symmetric/1-to-N-hard in the sibling
   drill** (`research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md`
   — SYNONYM-class symmetric relations, IS_A-class 1-to-N relations) — i.e. this diagnostic should reproduce, from
   pure graph structure with zero model training, the SAME functional-form gap that drill found by testing model
   fits directly. If it does, that is strong independent triangulation from a completely different method
   (structural statistics vs. trained-model residuals) on the same conclusion.
4. **Commonsense KGs are explicitly, by their own authors' design principle, schema-poor relative to curated KGs —
   this is a real structural risk for the factorized-operator idea, not a hypothetical one.** CSKG's own paper
   (Ilievski, Szekely & Zhang, arXiv:2012.11490) states a design principle of deliberately *"blurring the
   distinction between objects, classes, words, actions, frames, and states"* when merging ConceptNet/ATOMIC/Visual
   Genome/Wikidata/FrameNet/Roget — the opposite of Freebase/Wikidata's clean type system. Krompaß, Baier & Tresp
   (ISWC 2015, arXiv:1508.02593) show type/schema-constrained models beat schema-agnostic ones specifically because
   type structure gives a block model the shared operator can exploit — **CSKG lacking a clean type system is
   direct evidence AGAINST an easy win for a shared per-relation operator, independent of degree skew.** This is
   the single most important literature fact for Part B of the mission (does CSKG's structure support a
   TEM-style factorized map-builder): the answer may be "partially, and unevenly across relation types," not a
   clean yes/no, and the diagnostic below is designed to measure exactly where the boundary falls.
5. **The brain's own factorized-map machinery is not schema-agnostic either — it specifically credits and exploits
   community/modular structure, and independent brain evidence supports the general shape of the graph-shape
   question this drill was dispatched to answer.** Semantic-network literature (Steyvers & Tenenbaum 2005;
   Borge-Holthoefer & Arenas 2010, *Entropy*) establishes small-world + non-trivial modularity as a structural
   constant of human semantic networks, with communities aligning to taxonomic/thematic clusters, not a flat graph.
   Schema theory (Tse et al. 2007 *Science*; McClelland/Kumaran/Hassabis 2016 *Neuron*) explicitly frames rapid
   schema-based learning as working BECAUSE new facts are assimilated into an existing, internally-consistent
   relational template — a graph-community-shaped mechanism, not a generic "prior knowledge helps" claim. The TEM
   literature (Whittington et al. 2020 *Cell*; Garvert/Dolan/Behrens 2017 *eLife*; Schapiro et al. 2013/2016) shows
   the hippocampal-entorhinal system extracting and generalizing over EXACTLY this kind of community/graph
   structure when it exists (temporal community structure, abstract relational maps) — direct empirical
   confirmation, not just architectural plausibility, that the brain's factorized-map machinery specifically
   exploits schema/community structure rather than working schema-agnostically. **Net: the brain literature does
   not license "any graph will do" — it independently predicts the same thing the KGE literature predicts, that
   the factorized-operator idea needs the graph to actually HAVE exploitable community/schema regularity, and
   should degrade specifically where that regularity breaks down** (heterogeneous relations, low-modularity
   regions, peripheral/rare concepts).

**Calibration note:** points 3 and 4 combine well-established individual literature facts (TransH/RotatE cardinality
critique; CSKG's own stated design principle) with a specific prediction about how they will show up in THIS
substrate's specific 29-relation test graph, not directly measured anywhere in the literature. Per calibration
discipline this synthesis is capped at **P=0.50** even though the individual supporting facts are each high
confidence — see the falsifiable-predictions section for per-claim deflated values.

---

## A. What matters, per the literature (sub-question by sub-question)

**Degree distribution / skew (lit-scan A):**
- Power-law exponent: use Clauset-Shalizi-Newman MLE fitting (arXiv:0706.1062) with KS-distance goodness-of-fit,
  NOT log-log least-squares (badly biased in the tail). No paper directly regresses gamma against
  popularity-baseline win-rate in KG link prediction — this specific linkage is a reasonable network-theory
  inference, not a sourced finding (flagged, not fabricated).
- Gini coefficient of degree: used extensively in recommender-system popularity-bias work (arXiv:2308.01118
  survey) but not found applied numerically inside a KG link-prediction paper specifically — this drill's
  application of Gini-of-degree to a KG context is itself a small novel-synthesis step, capped accordingly.
- Max/mean-degree ratio: confirmed generic diagnostic (ratio near 1 = random-graph-like; far from 1 =
  hub-dominated/scale-free). The KG-specific empirics that DO exist (Shomer et al. WWW 2023 arXiv:2302.05044;
  Mohamed et al. UAI 2020 PMLR 124:1059) confirm degree bias is real and give strat-hits@k/strat-MRR as the
  standard unbiased-under-skew metric — which is exactly the fair/degree-tertile methodology already in use on
  this substrate's own cells. Numeric cross-dataset ratios (FB15k-237 vs WN18RR vs NELL-995) could not be
  extracted this cycle (PDF parse failures) — treat as a gap, not silently filled.
- Clustering coefficient: higher clustering favors triadic-closure/common-neighbor methods over degree-only
  ranking, with one source citing an empirical ~0.27-0.37 boundary separating regimes (generic-network literature,
  not KG-specific).
- Community/modularity: general link-prediction literature (arXiv:2202.00961) connects community-preserving
  embeddings to prediction gains; no paper found explicitly contrasting popularity-baseline vs. embedding
  performance WITHIN vs. ACROSS communities — a genuine literature gap this diagnostic can fill empirically for
  the first time on this substrate's own graph.
- Core-periphery: Borgatti-Everett model and successors (arXiv:1202.2684, arXiv:2202.04455) are mature, but no
  source links core-periphery position directly to popularity-baseline dominance — again inferential, not sourced.
- Relation-type-specific degree/cardinality: **the strongest-evidenced sub-question of the seven** — TransH's
  1-1/1-N/N-1/N-N stratification (Wang et al. AAAI 2014) is exactly the kind of per-relation profiling this
  mission asks for, and Aiyappa et al. (ICML 2025, arXiv:2405.14985) is a genuinely new, high-value finding: **the
  standard link-prediction evaluation protocol ITSELF is implicitly degree-biased**, independent of the graph or
  the model — a pure-degree null predictor is near-optimal under standard negative sampling. This reframes part of
  "does frequency's moat grow" as partly a MEASUREMENT artifact fixable by degree-corrected negative sampling, not
  purely a graph-shape property. High priority to fold into the next fit/eval redesign regardless of this
  diagnostic's other findings.

**Factorized map-builder prerequisites (lit-scan B):**
- No formal SBM-style theorem exists connecting block structure to "one shared relation operator suffices," but
  Krompaß, Baier & Tresp (ISWC 2015, arXiv:1508.02593) give strong empirical support: type/schema-constrained
  models beat schema-agnostic ones on curated KGs, because type structure gives the model a block structure to
  exploit.
- Schema-aware/type-constrained KGE (TKRL, JOIE, and 2023 type-augmented KGE work) consistently shows type
  regularity helps relation generalization — convergent, high-confidence literature.
- Per-relation pattern heterogeneity is the best-evidenced finding: TransE/RotatE/TransR/TranSparse all motivate
  relation-specific or entity-pair-adaptive representations because single relations mix structurally different
  sub-populations (RotatE's proof that TransE cannot even represent symmetric relations; TransR's rationale that
  e.g. "location-contains" spans country-city, country-university, continent-country as structurally different
  sub-patterns).
- Commonsense KGs are explicitly schema-poor by design (CSKG's own stated "blurring" principle,
  arXiv:2012.11490), with dedicated noise-detection work existing specifically because of this (GOLD framework,
  arXiv:2310.12011) — no paper quantifies purity specifically for mereological/causal/taxonomic relation subsets
  (a genuine gap this diagnostic can fill).
- Modularity's effect on the shared-operator idea is NOT directly addressed in the literature — reasoning from the
  type-constraint literature, high modularity only HELPS if community boundaries coincide with type/schema
  boundaries; modularity without schema-alignment would be a bad sign (per-community operators would be needed
  instead of one global operator per relation). This is this drill's own inference, flagged as such, not a sourced
  claim.

**Brain-grounding (lit-scan C, Part D of mission):**
- Semantic networks reconstructed from free-association/feature norms show established small-world + non-trivial
  modularity (Steyvers & Tenenbaum 2005; Borge-Holthoefer & Arenas 2010), with communities corresponding to
  taxonomic/thematic clusters — not a flat, homogeneous graph.
- Schema theory (Tse et al. 2007; McClelland/Kumaran/Hassabis 2016) explicitly credits rapid one-shot learning to
  assimilation into an existing, internally CONSISTENT relational template — a community/schema-shaped mechanism,
  not generic prior knowledge.
- TEM and the hippocampal statistical-learning literature (Whittington et al. 2020; Garvert/Dolan/Behrens 2017;
  Schapiro et al. 2013/2016) show this machinery specifically extracting and generalizing over community/graph
  structure WHEN IT EXISTS — direct empirical support (not just architectural plausibility) that the brain's
  factorized map exploits schema/community regularity rather than working schema-agnostically. The explicit "what
  breaks factorization" claim (irregular/exception-heavy domains) is present in TEM's framing but less deeply
  quantified than the positive claim.
- Core-periphery structure is well documented in semantic/lexical networks (hub-and-spoke ATL hub hypothesis;
  *Science Advances* 2021 core-periphery typology) but the specific claim that peripheral/rare concepts get LESS
  benefit from schema-based one-shot generalization than core concepts is a plausible, currently untested
  inference in the literature — not a stated finding. This is directly the same shape of question as this
  substrate's own low/mid/high degree-tertile stratification, and is exactly what the diagnostic below can test.

---

## B. TEM prerequisite verdict (mission Part B, answered directly)

**Does CSKG's likely structure (commonsense, mereological/causal) support a factorized map-builder?**
Best-current-evidence answer, capped at the novel-synthesis ceiling: **partially, and unevenly across relation
types — not a clean yes.** The convergent literature signal (CSKG's own stated schema-blurring design principle +
the TransH/RotatE cardinality-heterogeneity critique + the brain's own requirement that its factorized machinery
needs schema/community regularity to exploit) points toward a graph where SOME relations (the more
mereological/causal/spatial ones: `PartOf`, `AtLocation`, `Causes`, `LocatedNear`) are closer to the clean,
consistent, TransH-style 1-N/N-1 regime a shared operator handles well, while OTHERS (the ATOMIC event-effect
relations `xEffect`/`xWant`/`oReact`-class, and the lexical `SYNONYM`/`IS_A` relations already flagged in the
sibling drill) are exactly the heterogeneous, symmetric, or hub-forming relations the literature says break a
single global operator. **This is a testable, relation-by-relation empirical question, not a single graph-wide
verdict** — which is exactly why the diagnostic below is designed to report a PER-RELATION profile, not just one
aggregate modularity number.

---

## C. Concrete REMOTE-runnable diagnostic design (pre-registered)

**Scope:** pure graph computation, zero training, zero GPU required (CPU-only, `remote_cpu_queue`-class job,
matching the existing k-core gate's compute class). Runs on data already on disk — no new acquisition.

**Graphs to measure (three, for direct before/after comparison):**
1. **Full CSKG** (2,159,195 nodes / 5,167,463 simple edges) — already partially characterized, re-derive the
   missing statistics below.
2. **Cross-cutting commonsense subgraph** (501,391 nodes / 1,184,796 simple edges) — the spine used for the
   density/percolation gates.
3. **The ACTUAL 12-core test graph** (N=25,752 / 511,164 core edges / 29 relations) that
   `course_c_rotate_cskg_l2_seed_17_gpu1024_v1` ran the fair-test on — **this is the load-bearing graph for this
   mission**, since it is literally the object the frequency-vs-geometry race is measured on; the other two are
   context.

**Statistics to compute on each, all standard library calls (networkx / igraph / powerlaw / python-louvain or
leidenalg — no custom math needed):**

1. **Degree distribution + power-law fit**: full degree sequence, `powerlaw` package MLE fit (Clauset-Shalizi-Newman
   method) for gamma + x_min + KS-distance goodness-of-fit vs. lognormal/exponential alternatives (per the CSN
   discipline — do not eyeball a log-log slope).
2. **Gini coefficient** of the degree sequence (standard closed-form: `G = sum_i sum_j |d_i - d_j| / (2 n^2 mean(d))`).
3. **Max-degree-to-mean-degree ratio**, computed WITHIN each induced subgraph specifically (the existing full-graph
   max-degree=11,037 number is NOT valid for the 12-core subgraph — this must be re-measured on the induced core,
   since k-core extraction caps the degree distribution's low end but not necessarily its skew).
4. **Global clustering coefficient / transitivity** (networkx `average_clustering` + `transitivity`).
5. **Per-relation degree profile**: for each of the 29 relations (test graph) / 58 relations (full graph), compute
   subject-degree and object-degree distributions SEPARATELY, classify cardinality pattern via the TransH-style
   ratio test (fraction of subjects with >1 object per this relation vs. fraction of objects with >1 subject),
   and flag symmetric relations (edges appearing in both directions between the same pair at above-chance rate).
6. **Community detection + modularity**: Louvain or Leiden community detection on each graph, report modularity Q,
   number of communities, community-size distribution, AND (the schema-alignment check) a cross-tabulation of
   community membership against (a) relation-type composition within each community and (b) source-provenance tag
   (ATOMIC / ConceptNet / WordNet / Wikidata / FrameNet / Roget / VisualGenome, already present in CSKG's `source`
   column) — this operationalizes the "do communities correspond to schema-consistent blocks" question directly,
   using data already in the TSV.
7. **Core-periphery structure**: reuse the ALREADY-COMPUTED k-core decomposition (density gate note) rather than
   re-deriving from scratch — the k=12-14 floor band (23,632 -> 10,731 nodes @ deg 38-55) vs. the k>=20 ultra-dense
   kernel (1,634-3,037 nodes @ deg 128-184) IS a core-periphery structure already on disk. New measurement needed:
   cross-reference which nodes fall in the k>=20 ultra-dense kernel against the degree-tertile boundaries already
   used in `course_c_rotate_cskg_l2_seed_17_gpu1024_v1`'s HIGH tertile, to test directly whether the frequency
   baseline's win is concentrated specifically in this small ultra-dense kernel (a sharp, localized core) or
   diffused across the whole high tertile (a broad, gradual effect) — this is a weak-point-localization measurement
   in the spirit of the fairness+localization discipline, distinguishing "frequency wins everywhere above a soft
   threshold" from "frequency wins only inside a small identifiable hub kernel."
8. **Fair-stratum-size-vs-degree-cutoff curve**: sweep the low/mid/high degree-tertile cutoff across a range of
   percentile thresholds (e.g. 10th/25th/33rd/50th/67th/75th/90th percentile of degree) and plot, at each cutoff:
   (a) fraction of ENTITIES below the cutoff (the "fair" population size), (b) fraction of TOTAL EDGE MASS incident
   on entities below the cutoff. This is the direct empirical measurement of the scaling drill's HEADLINE point 4
   prediction (fair stratum grows in absolute count but shrinks as a share of total mass) — but measured on the
   REAL graph's actual degree distribution rather than inferred from generic Barabasi-Albert theory.

**Compute class:** all eight measurements are O(N log N) to O(N + E) graph algorithms on graphs up to 2.16M
nodes/5.2M edges — well within CPU-only remote_cpu_queue capability, no GPU needed, no adaptive-batch-sizing
concerns of the kind that already caused a HARD_FAIL_CARDINALITY_BREACH on a training cell at similar node count
(that failure was PyTorch GPU memory during embedding training, not graph computation, so it does not transfer as
a risk here — flagged explicitly to avoid over-generalizing a training-specific OOM to an unrelated CPU-graph job).

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

**Prediction 1 — the actual 12-core test graph is meaningfully less hub-dominated than the raw full graph, but
still skewed enough that frequency has real leverage (not the full-graph 11,037-max-degree extreme, not a flat
random graph either).**
HARD-PASS: measured max/mean-degree ratio on the 12-core test graph falls in a moderate band (roughly 10-50x,
i.e. clearly scale-free but not the full-graph's extreme hub concentration) AND Gini coefficient falls in
0.35-0.60 (moderate inequality by the generic inequality-literature convention, not the >0.6 "extreme inequality"
band).
HARD-FAIL: max/mean ratio exceeds 100x OR Gini exceeds 0.70 on the 12-core graph itself — meaning even after
core-extraction (which should already have trimmed the sparsest, least-connected tail), the graph is STILL
extremely hub-dominated, predicting frequency's moat will be severe and hard to dilute by any construction choice
short of relation-type-specific handling.
P_deflated = **0.40** (moderate-band outcome is the modal literature expectation for k-core-extracted commonsense
graphs, but genuinely unmeasured on this specific graph — capped below the novel-synthesis ceiling).

**Prediction 2 — per-relation cardinality heterogeneity reproduces the functional-form gap already found by
direct model-residual analysis, using pure graph structure and zero training.**
HARD-PASS: the per-relation cardinality-purity scores (Prediction 2b methodology, TransH-style) rank
`SYNONYM`-class/symmetric relations and `IS_A`-class 1-to-N relations as the LOWEST-purity (most heterogeneous)
relations in the 29-relation set, matching the sibling drill's independent model-residual-based finding that these
relation types are the hardest for a single shared operator.
HARD-FAIL: cardinality-purity scores show no correlation with the sibling drill's already-identified problem
relations — would mean the functional-form gap is NOT visible in pure graph structure and is instead an artifact
specific to the trained model's fit, a genuinely informative negative that would narrow where to look for the
mechanism.
P_deflated = **0.45** (this is the single sharpest, most triangulable prediction in this drill — two independent
methods, model-residuals and pure-graph-structure, predicting the same relations should fail if the underlying
cause really is relation-type heterogeneity rather than something fit-specific).

**Prediction 3 — modularity/community structure exists but does NOT cleanly align with relation-type/schema
boundaries (the schema-poor commonsense-KG prediction).**
HARD-PASS (supports factorized map-builder, partially): modularity Q > 0.30 on the 12-core test graph (clear
community structure by the generic modularity-interpretation convention) AND community membership shows
meaningfully non-uniform relation-type/source-provenance composition (i.e. communities ARE schema-flavored, even
if not perfectly typed) — this would mean a per-community or per-schema-cluster relational operator (rather than
one single global operator per relation) is a promising, buildable direction.
HARD-FAIL (too hub-dominated / schema-poor, frequency-favoring): modularity Q < 0.15 (weak/no community
structure) OR communities show near-uniform relation-type mixing (no schema alignment at all) — this would mean
CSKG's cross-cutting core is closer to a single undifferentiated blob than a schema-structured graph, predicting
that NO factorization scheme keyed on community/topology alone will help, and that any workable schema must come
from an EXOGENOUS type system (imposed, not discovered) — directly consistent with the Krompaß/Baier/Tresp finding
that type-constrained models need the type system to be GIVEN, not mined.
P_deflated = **0.30** (deflated hard — CSKG's own stated design principle explicitly disclaims schema-cleanliness,
which is genuine evidence toward the HARD-FAIL side; capped rather than pushed lower because commonsense graphs
CAN still show emergent topological modularity even without an explicit type system, per the general semantic-network
literature in Part A).

**Prediction 4 — the frequency baseline's win is localized to a small, sharply-identifiable hub kernel, not
diffused across the whole high-degree tertile (weak-point localization).**
HARD-PASS: cross-referencing the k>=20 ultra-dense kernel (1,634-3,037 nodes, already on disk) against the
high-degree tertile used in the fair-test cell shows the POP-vs-ROTATE/ADDITIVE margin (0.4155 vs 0.3955/0.3213)
concentrates specifically within this small kernel, with the REMAINDER of the high tertile showing a much smaller
or absent POP advantage — this would mean a targeted fix (e.g. excluding or specially handling the ultra-dense
kernel) could reclaim most of the high-degree tertile for geometry, a cheap, localized intervention.
HARD-FAIL: the POP advantage is roughly uniform across the entire high-degree tertile, not concentrated in the
small kernel — meaning the frequency advantage is a broad property of "being above the tertile cutoff," not a
localized hub-kernel effect, and no cheap kernel-specific fix would help; the fix has to be a relation-level or
architecture-level change (per Predictions 2-3), not a node-population carve-out.
P_deflated = **0.35** (genuinely open; the existing core-periphery data suggests a sharp kernel exists structurally,
but whether the PERFORMANCE effect concentrates there specifically, versus just correlating loosely with degree
generally, has not been measured).

---

## Cross-thread synthesis

- Directly reuses and extends `cskg_commonsense_core_kcore_density_gate_2026-07-10.md`'s k-core infrastructure
  (`scratchpad/kcore.py`) — Prediction 4's core-periphery cross-reference is a near-zero-marginal-cost addition to
  data already computed, not a new acquisition.
- Directly complements `research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`, which used the same
  cross-cutting graph for a DIFFERENT structural question (seeded reachability to a grounded anchor set). That
  drill's Control C already found (via the Vincent-Lamarre dictionary-graph analogy, untested on CSKG specifically)
  that graph-centrality and semantic/exogenous properties can be inversely related — this drill's community/schema
  question is a sibling structural audit on the SAME graph, and both should be read together before any map-builder
  design commits to using topology (centrality, community, or core-membership) as a proxy for anything semantic.
- Directly extends `research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`'s HEADLINE point 4
  (frequency's moat grows with scale per Barabasi-Albert theory) by replacing the THEORETICAL inference with a
  DIRECT MEASUREMENT plan (the fair-stratum-size-vs-degree-cutoff curve, Diagnostic item 8) on the actual graph
  rather than generic scale-free growth theory — this is strictly cheaper and more decisive than that drill's own
  proposed multi-N scaling ladder, and should likely run BEFORE it, since it uses data already in hand at zero new
  acquisition cost.
- Directly extends `research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md`'s
  functional-form diagnosis (TransE cannot represent SYNONYM/IS_A) — Prediction 2 above is a structural,
  training-free replication attempt of that drill's model-residual finding, and if it triangulates, gives the
  functional-form conclusion a second, independent, cheaper form of evidence.
- New fact this drill adds that no sibling note surfaced: **the Aiyappa et al. (ICML 2025) finding that standard
  link-prediction evaluation protocol is ITSELF implicitly degree-biased** — this reframes part of the
  `backdoor_r=0.31` gate failure as potentially a fixable evaluation-protocol artifact, not purely an
  architecture or graph-shape problem, and should be checked (degree-corrected negative sampling) independent of
  what this diagnostic's community/modularity numbers show.

---

## Substrate-product implications

- **The honest current claim:** "we know the actual 12-core test graph is dense enough to reason over (already
  proven) and we know frequency wins the high-degree tertile (already measured) — but we do NOT yet know whether
  that graph has the kind of schema/community regularity a factorized map-builder needs, whether the frequency
  win is a broad property of high degree or concentrated in a small identifiable hub kernel, or whether part of
  the observed confound is a fixable evaluation-protocol artifact rather than a real graph-shape or architecture
  problem. All three are now cheap, pre-registered, remote-runnable, zero-training graph computations away from
  being known."
- **This diagnostic should run BEFORE the next architecture iteration (e.g. the HAKE-hybrid build already flagged
  in `research_next_form_decision_from_first_result_hake_hybrid_2026-07-12.md`) commits further compute**, because
  Prediction 2/3's outcome directly informs whether a single global HAKE-style operator per relation is even the
  right ambition, versus a per-community or per-schema-cluster operator design, versus accepting that frequency's
  win on hub concentrations needs a targeted carve-out rather than a better global fit.
- **The Aiyappa et al. degree-biased-evaluation-protocol finding is a near-free, high-leverage check**: before
  attributing the `backdoor_r=0.31` failure entirely to graph shape or model architecture, verify whether
  degree-corrected negative sampling shifts the correlation — if it does, part of the fix is in the EVALUATION
  harness, which is cheaper to change than any architecture redesign.
- **A community/schema-informed map-builder, if Prediction 3 HARD-PASSes even partially, becomes a concretely
  scoped next build**: per-community relation operators (or relation operators gated on source-provenance/
  schema-cluster membership) rather than one global operator per relation type — directly actionable, with the
  community-detection output itself supplying the partition to build against.

---

## Citations (verified count)

**On-disk, read in full this cycle:** `cskg_commonsense_core_kcore_density_gate_2026-07-10.md`;
`research_grounding_percolation_reachability_cskg_audit_2026-07-11.md`;
`research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`;
`research_cskg_prior_art_novelty_due_diligence_2026-07-10.md`;
`data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json` (config + gates fields read directly).
**5 on-disk sources.**

**External literature (3 parallel Sonnet lit-scans, generic network-science/ML/cognitive-science terms only, no
substrate-novel names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Degree/topology vs. link-prediction difficulty:* Clauset, Shalizi & Newman (2009, SIAM Review, arXiv:0706.1062);
Mohamed, Parambath, Kaoudi & Aboulnaga (Popularity-Agnostic Evaluation, UAI 2020, PMLR 124:1059); Shomer, Jin,
Wang & Tang (KG-Mixup/Degree Bias, WWW 2023, arXiv:2302.05044); Aiyappa, Wang, Kim, Seckin, Yoon, Ahn & Kojaku
(Implicit Degree Bias in Link Prediction, ICML 2025, arXiv:2405.14985); Wang, Zhang, Feng & Chen (TransH, AAAI
2014); Borgatti & Everett core-periphery model (survey arXiv:1202.2684, arXiv:2202.04455); "A Survey on Popularity
Bias in Recommender Systems" (arXiv:2308.01118); "Modularity-Aware Graph Autoencoders" (arXiv:2202.00961);
"Link Prediction with Node Clustering Coefficient" (arXiv:1510.07819).

*TEM/factorized map-builder prerequisites:* Krompaß, Baier & Tresp (Type-Constrained Representation Learning,
ISWC 2015, arXiv:1508.02593); Xie et al. (TKRL, IJCAI 2016); Bordes et al. (TransE, NeurIPS 2013); Sun, Deng, Nie
& Tang (RotatE, ICLR 2019, arXiv:1902.10197); Ilievski, Szekely & Zhang (CSKG, arXiv:2012.11490); Hwang et al.
(COMET-ATOMIC2020, AAAI 2021, arXiv:2010.05953); GOLD commonsense-KG noise-detection framework (arXiv:2310.12011).

*Brain semantic-network community/schema structure:* Steyvers & Tenenbaum (2005, *Cognitive Science*); Borge-
Holthoefer & Arenas (2010, *Entropy*, "Semantic Networks: Structure and Dynamics"); Tse et al. (2007, *Science*);
McClelland, Kumaran & Hassabis (2016, *Neuron* review); van Kesteren, Ruiter, Fernández & Henson (2012, *J
Neurosci* review); Whittington et al. (TEM, *Cell* 2020); Garvert, Dolan & Behrens (2017, *eLife*); Schapiro et
al. (2013/2016, temporal community structure in hippocampus); core-periphery typology in semantic networks
(*Science Advances* 2021).

**Total: 5 on-disk sources read in full + 26 external sources across 3 parallel lit-scans = 31 verified checks.**

---

## Intuitive summary

We asked: what does the actual SHAPE of our knowledge graph — how lopsided its popularity is, and whether it's
organized into consistent neighborhoods or one big undifferentiated blob — tell us about (a) how hard the
popularity-guessing baseline will be to beat as things scale, and (b) whether a "build a small reusable rulebook of
relationships" design (the map-builder direction) can actually work on this graph.

The literature doesn't hand us a single magic number, but it gives several strong, complementary rulers, and we
already have most of the graph measurements needed to use them sitting on disk from earlier work — we just haven't
run the specific six calculations (skew ratio, inequality score, clustering, neighborhood/community detection,
per-relationship-type consistency, and a "does the fair zone shrink as things grow" curve) yet. This note specifies
exactly how to run all six cheaply, on a machine, with no training involved — pure counting and graph math.

Two things stood out as genuinely new and actionable. First, a very recent (2025) finding says the STANDARD WAY
the field measures "did you beat the popularity guess" is itself quietly biased toward popularity — meaning part
of our own worrying result (an unwanted popularity leak) might be partly a measurement-ruler problem, fixable
cheaply, not only a real graph-shape or design problem; worth checking before assuming the worst. Second, whether
our knowledge graph has real "neighborhoods" (consistent clusters where relationships behave predictably) is
directly testable, and if it does, it opens a concrete, buildable next step: relationship rules that are shared
within a neighborhood rather than one rule trying to cover the whole graph. If it doesn't, that tells us — cheaply,
before building anything more elaborate — that we'd need to bring in an outside classification scheme rather than
expecting the graph to hand us one. The brain's own version of this system doesn't work schema-agnostically either
— it specifically leans on consistent neighborhoods when they exist — so this isn't a made-up standard, it's the
same requirement biology runs into.
