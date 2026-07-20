# Scour: foundation-core build-drill + prior-art (3x per element) — learned similarity codebook / contrastive coherence loop / homeostatic stabilizer

**Date:** 2026-07-20. **Filed by:** research (3 parallel Sonnet lit-scan lanes, one per element, Opus synthesis).
**Trigger:** direct build-drill request for the #1 build (missing learning system, CPCL redesign) — the
learned similarity-structured codebook + contrastive coherence loop + homeostatic stabilizer that must be
built as ONE integrated glass-box system, replacing the VET-confirmed-null CPCL-v1 (random content codes +
bag-of-words next-sentence target + in-sample memorization).
**Method note (2x/overlap discipline):** checked recent research deliveries first; the closest sibling is
`research_vsa_learned_reader_prior_art_scour_2026-07-18.md` (learned VSA role-filler *parsing* into
structure — a different question: that note asked "who learns to bind text into role-filler vectors,"
this note asks "how do we build the content-vector geometry, the training signal, and the stability rule
underneath any such learner"). No direct prior scour on codebook-construction / coherence-target /
homeostasis exists in `notes/`; this is genuinely new ground for this arc.

---

## HEADLINE

All three elements have a strong, directly-adoptable prior-art anchor, and none requires inventing new
mathematics — but the codebook element's evidence is weakest at our actual corpus floor (~100k-1M words),
the coherence element has the single best glass-box precedent found this session (a *pre-existing,
already-published, zero-neural-net* implementation), and the homeostatic element has zero direct VSA/HDC
precedent and rests on cross-literature analogy. **Best adoptable prior art per element: (1) codebook =
Random-Indexing/BEAGLE binding algebra (Kanerva/Sahlgren/Jones & Mewhort/Recchia) with PPMI-style
co-occurrence weighting blended in from the count-based lineage; (2) coherence-loop = Barzilay & Lapata
entity-grid + Guinaudeau & Strube's unsupervised graph-out-degree scorer, hardened with ALBERT-SOP's
same-document-order-swap negative design; (3) homeostatic = Oja's rule as the primary per-step stabilizer,
with a slow Turrigiano-style EMA scalar layered on only if a second failure mode appears empirically.**
The integrated foundation is buildable NOW on our corpus with existing, ported/adapted prior art — no
element requires a from-scratch invention — but this is a **hypothesis-pending-VET synthesis, not a
verified combination**: no single cited paper does all three together, corpus-size evidence at our exact
floor is thin-to-absent for element 1, and element 3 has no direct VSA citation at all.

---

## ELEMENT 1 — Learned similarity-structured codebook

### 3x build (what each method does, mechanically)
- **Random Indexing** (Kanerva/Sahlgren): assign each context a random sparse near-orthogonal index vector;
  bundle (sum) the index vectors of everything a word co-occurs with. Incremental, no full matrix, no SVD.
- **BEAGLE** (Jones & Mewhort): context vector = bundle of co-occurring words' identity vectors; order
  vector = circular-convolution-bind of neighboring words within a window, summed across the corpus. Both
  bind (convolution) and bundle (addition) are literally the substrate's own VSA operators already.
- **HAL/LSA**: co-occurrence matrix (directional-windowed for HAL, document-level tf-idf for LSA) then
  (for LSA) truncated SVD to a dense low-rank space.
- **PPMI+SVD**: co-occurrence counts -> pointwise mutual information -> clip negative (PPMI) -> optional
  SVD. Levy & Goldberg (2014) proved skip-gram/word2vec implicitly factorizes a shifted-PMI matrix — PPMI
  and neural embeddings are two compression recipes for the *same underlying statistic*.
- **Mapping onto VSA bind/bundle**: Random Indexing and BEAGLE are natively VSA-compatible — no adapter
  needed, their construction *is* the bind/bundle algebra. PPMI+SVD and HAL/LSA produce dense,
  norm-unconstrained vectors that need an adapter (sign-threshold/binarize, or bind-once against a random
  role vector as an item-memory seed, or — per Kleyko et al.'s HyperEmbed — skip SVD entirely and
  bind-and-sum the PPMI-weighted counts directly into hypervectors).

### Prior art (who built glass-box distributional HD/VSA codebooks)
- Kanerva, Kristoferson & Holst (2000, CogSci) — original Random Indexing; Sahlgren (multiple, RI
  monograph + Karlgren & Sahlgren 2001, TOEFL 64.5-67%); Widdows & Cohen — **Semantic Vectors** open-source
  package (Java) implementing RI + Reflective RI, directly portable/adoptable.
- Jones & Mewhort (2007, Psych. Review) — BEAGLE; Recchia, Jones, Sahlgren & Kanerva (2015, *Computational
  Intelligence & Neuroscience*) — direct head-to-head of convolution (BEAGLE/HRR) vs. random-permutation
  binding, finding **parity on small corpora**, divergence only at Wikipedia-scale (permutation cheaper at
  scale). **wikiBEAGLE** (GitHub) is a usable reference implementation.
- Landauer, Foltz & Laham (1998) — LSA/TOEFL 65% (canonical citation); Lund & Burgess (1996) — HAL; both
  have mature open-source ports (gensim `LsiModel`/`TruncatedSVD`; S-Space package's HAL implementation;
  HiDEx tool).
- Levy & Goldberg (2014, NeurIPS) + Levy, Goldberg & Dagan (2015, TACL) — PPMI+SVD vs. SGNS equivalence and
  parity-with-matched-hyperparameters; 2020s low-resource-NLP literature explicitly argues **PPMI (with
  smoothing) outperforms neural embeddings specifically as corpora shrink**, because count-based methods
  have no large hidden parameter count to overfit/starve.
- Kleyko et al.'s HyperEmbed (IJCNN 2020/2021) — turns n-gram/PMI-style statistics into HDC vectors via
  direct bind-and-sum, sidestepping the SVD-adapter problem.

### Corpus-size / accuracy data (the load-bearing risk flag)
- **None of the four methods has a published benchmark run inside our exact 99k-1M-word floor.** Closest
  data points: RI's original TOEFL demo used a "modest" corpus (exact word count not pinned down in
  available sources) — the method is explicitly designed to scale down (memory grows with vocabulary, not
  corpus size), which is favorable but not proven. BEAGLE's quantitative benchmarks (priming-RT
  correlations) all ran on the **~11M-word TASA corpus** — an order of magnitude above our range — but
  Recchia et al. 2015's convolution-vs-permutation parity result is a genuine small-corpus data point in
  spirit (relative behavior, not absolute floor). LSA/HAL benchmarks range from ~3.2M words (small end) up
  to billions; literature explicitly warns **LSA quality degrades as corpus size shrinks**. PPMI+SVD's best
  evidence is *comparative* (beats neural embeddings when both are small), not an absolute accuracy
  guarantee at 100k words.

### Open-source portability
Semantic Vectors (RI), wikiBEAGLE (BEAGLE), gensim/S-Space/HiDEx (LSA/HAL) all directly portable. PPMI+SVD
needs no dedicated package — assembled from `scipy.sparse` + `sklearn.decomposition.TruncatedSVD`, arguably
the easiest to implement as fully auditable glass-box steps (count -> PMI arithmetic -> clip -> SVD).

### ADOPT / ADAPT / BUILD-FRESH call
**ADOPT the Random-Indexing/BEAGLE binding algebra** (Kanerva, Sahlgren, Jones & Mewhort, Recchia et al.) as
the structural mechanism — zero adapter cost, already the substrate's own operators, and the one lineage
with a direct (if indirect-in-scale) small-corpus-parity result. **ADAPT PPMI-style weighting** (Levy &
Goldberg lineage) into the bundling step — weight each context's contribution to a word's bundled vector by
its PPMI score rather than raw count, borrowing the low-resource-robustness argument from the count-based
literature without abandoning the VSA-native construction. **No BUILD-FRESH needed** — this is a credited
recombination of two existing lineages that (per the 07-18 sibling scour's own finding about the
learned-binding vs. compressed-VSA literatures) have stayed under-cross-pollinated; crediting Kanerva,
Sahlgren, Jones & Mewhort, Recchia, Levy & Goldberg, Widdows & Cohen, Kleyko et al. throughout.

**Deflated confidence: raw lane estimates 0.55-0.60 (already self-deflated by the lane); applying the
mandatory 0.15-0.25 lit-scan calibration penalty on top (corpus-size evidence gap is the dominant
uncertainty) -> P_deflated = 0.32.**

---

## ELEMENT 2 — Contrastive coherence loop

### 3x build (mechanism + why each fixes the naive-NSP failure mode)
- **ALBERT SOP** (Lan et al. 2019): BERT's NSP negative = a *different-document* segment, which lets the
  model solve NSP via topic-shift alone (Lan et al.'s own diagnostic: NSP-trained model solves SOP at only
  52% — chance). SOP's negative = the *same* two segments with order *swapped*, holding topic constant,
  forcing genuine sequence/discourse-coherence learning. This is the near-exact precedent named in this
  task's own trigger context.
- **Entity-grid coherence** (Barzilay & Lapata 2005/2008, + Elsner & Charniak 2011, + Guinaudeau & Strube
  2013, + Nguyen & Joty 2017): represent a document as entities x sentences, cells = grammatical role
  (Subject/Object/Other/Absent); score coherence from the statistics of role-transition patterns across
  sentences (Centering Theory-motivated). **Guinaudeau & Strube (2013) is the standout finding of this
  entire scour: a fully deterministic, zero-neural-net, closed-form coherence score** (average out-degree
  of a bipartite sentence-entity graph) — no training, no learned discriminator, just graph arithmetic.
- **ELECTRA RTD** (Clark et al. 2020): replace masked-LM's sparse 15%-of-tokens reconstruction with a dense
  per-token binary real/replaced classification (~6.7x more gradient signal per batch than MLM); the hard
  part (a *plausible* corruption) inherently needs a trained generator — a naive frequency-based glass-box
  corruption risks recreating NSP's own shortcut-solvability problem (Clark et al.'s own ablation shows
  unigram-sampled replacements hurt performance vs. a trained generator's replacements).
- **InfoNCE/CPC** (van den Oord, Li & Vinyals 2018): the general mathematical umbrella — score true
  continuation vs. sampled negatives via a softmax/ranking objective. SOP, entity-grid ranking, and RTD are
  all specific instances of this pattern; useful as the LOSS FORM to unify the other signals, not as an
  independent glass-box signal itself (CPC's own implementation needs learned continuous representations).

### Prior art / glass-box portability (explicit per method)
- SOP: neural-only in its original form, BUT its *target construction* (real-order vs. swapped-order label)
  is free/deterministic bookkeeping — the label-generation is glass-box even though ALBERT's *scorer* isn't.
  Non-neural lineage predates it: Lapata 2003 probabilistic sentence-ordering, Barzilay & Lee 2004 HMM
  content models.
- Entity-grid: **the strongest hit in the whole scour** — Barzilay & Lapata's original SVM-over-hand-features
  ranker and Guinaudeau & Strube's graph out-degree score are BOTH pre-existing, published, deterministic
  implementations requiring no trained neural net at all. Original experiments used ~100 train + ~100 test
  documents per genre with ~20 permutations each — several orders of magnitude smaller than
  BERT/ALBERT/ELECTRA's billion-token corpora, i.e. this signal has documented low-data viability.
- ELECTRA RTD: neural-only in every instance found; no symbolic version exists because the plausibility-
  generation step is inherently model-based.
- InfoNCE/CPC: neural-only as literally implemented; high value purely as the mathematical loss-form
  template.

### ADOPT / ADAPT / BUILD-FRESH call
**ADOPT entity-grid coherence + Guinaudeau & Strube's graph-out-degree scorer** as the core glass-box
coherence target — extract entity + grammatical role per rival parse, build the transition grid, score via
out-degree (or transition-frequency likelihood vs. corpus background), prefer the rival scoring higher under
true order vs. a shuffled control. **ADAPT ALBERT SOP's negative-construction design** (same-document,
order-swapped, not cross-document) as the specific negative-sampling scheme layered onto the entity-grid
scorer — this directly ports the task's own cited near-exact precedent into the one method family that is
already glass-box, rather than requiring a trained Transformer. **ADOPT InfoNCE's ranking-loss form** (not
its neural implementation) as the update-rule wrapper: true-parse score vs. sampled-negative scores,
combined multiplicatively/softmax-style into the weight-update signal. **DEFER ELECTRA RTD** — its core
strength depends on a trained plausible-corruption generator that is hard to get glass-box-cheaply without
risking the same shortcut-solvability failure the original CPCL-v1 null already demonstrated; revisit only
if a cheap, non-trivially-detectable frequency-matched corruption scheme can be shown to work.
**Explicit must-read flag**: "Rethinking Self-Supervision Objectives for Generalizable Coherence Modeling"
(arXiv 2110.07198) specifically critiques shuffle-test/permutation self-supervision as potentially gameable
by shallow lexical/local cues — the lane could not fully extract its argument (PDF fetch garbled); this is a
mandatory pre-build read, and its concern should become an explicit must-fail control (see predictions
below) rather than being waved off.

**Deflated confidence: raw lane estimate for entity-grid alone was the highest of this whole session (0.75,
self-deflated by the lane); applying the mandatory 0.15-0.25 penalty -> P_deflated = 0.50 (capped at the
novel-synthesis ceiling per calibration discipline, since the SOP-negative-design + entity-grid combination
itself is this note's own synthesis, not a cited combination).**

---

## ELEMENT 3 — Homeostatic scaling / stabilizer

### 3x build (mechanism + math, each method)
- **Turrigiano synaptic scaling**: multiplicative rescaling of ALL of a unit's weights toward a target
  average-activity set-point, on a slow timescale relative to Hebbian plasticity. Two standard computational
  forms: leaky integral control (u̇ = k_u·e − ω_u·u on an activity-error signal) or a discrete slow-gain
  update (Δα ∝ (target_rate − actual_rate)/τ_hp).
- **Oja's rule**: Δw = η(xy − y²w) — a first-order approximation to "Hebbian update, then renormalize to
  unit norm," done implicitly/locally with no explicit norm computation. Provably converges to the
  principal eigenvector at ‖w‖=1. Generalizes to multiple components via Sanger's rule (Generalized Hebbian
  Algorithm, adds a Gram-Schmidt-like deflation term across units).
- **BCM**: ΔW ∝ x·y·(y−θ_M), with the modification threshold θ_M itself sliding as a super-linear
  (typically quadratic) function of recent average squared activity — a *selectivity-sharpening*/competitive
  mechanism (originally modeling visual-cortex orientation tuning), not primarily a magnitude stabilizer.

### Prior art
- Turrigiano, Leslie, Desai, Rutherford & Nelson (1998, *Nature*); Turrigiano (2008, *Cell*, "The
  Self-Tuning Neuron"); Turrigiano & Nelson (2004, *Nat. Rev. Neurosci.*); Tetzlaff et al. (2011,
  *Frontiers Comp. Neurosci.*) — synaptic scaling stabilizes circuit connectivity in combination with other
  plasticity mechanisms.
- Oja (1982, *J. Math. Biology*); Sanger (1989, *Neural Networks*, GHA/multi-component extension).
- Bienenstock, Cooper & Munro (1982, *J. Neuroscience*); Cooper & Bienenstock retrospective ("BCM theory at
  30"); Izhikevich & Desai (2003) linking BCM's sliding threshold to averaged STDP.
- **HDC/VSA-specific: no dedicated named paper found.** Closest available material: Kleyko et al.'s HDC/VSA
  survey (ACM Computing Surveys, Parts I/II) documents standard bundling normalization (divide-by-count or
  binary-majority clipping) as a *fixed construction-time* convention, not a learned/activity-dependent
  homeostat; general neuromorphic-Hebbian literature explicitly prefers Oja's local multiplicative-decay
  trick over explicit global L2 renormalization specifically because a global-norm reduction is
  non-local/hardware-unfriendly — this is an analogy, not a direct VSA citation.

### Minimal adoptable form / cost
- Oja: `w <- w + eta*(x*y - y^2*w)` — reuses quantities already computed in the forward pass (y, y^2), zero
  new persistent state, no global reduction. Cheapest and most local of the three.
- Turrigiano: one running-average-activity scalar + one slow multiplicative gain correction per unit —
  cheap, but a second state variable layered on top of the Hebbian step, not embedded in it.
- BCM: one running-average-squared-activity scalar (theta) + one nonlinear multiply per update — reshapes
  the learning rule's sign structure itself, more machinery than a pure stabilizer needs.

### ADOPT / ADAPT / BUILD-FRESH call
**ADOPT Oja's rule** as the primary per-step stabilizer for the Hebbian-style hypervector update — cheapest,
most local, provably stable, needs no new state beyond what the forward pass already computes. **ADAPT
Turrigiano-style scaling** as a secondary, slower-timescale layer, added ONLY if empirical drift in mean
activity level persists after Oja's per-step norm control (Oja controls ‖w‖, not necessarily the mean output
rate under a shifting input distribution) — this is cheap to bolt on later, no interaction with the Oja
mechanics required. **DEFER/BUILD-FRESH-IF-NEEDED-LATER: BCM** — explicitly excluded from the minimal
recommendation; it solves a different problem (competitive selectivity/sharpening) than "keep this update
numerically stable," and would only become relevant if the goal later shifts toward emergent
selective/sparse tuning rather than pure stability.

**Deflated confidence: raw lane estimate for Oja was 0.6 (self-deflated); this is the WEAKEST-cited element
of the three (zero direct HDC/VSA precedent, pure cross-literature analogy) — applying the full 0.25 end of
the mandatory penalty range -> P_deflated = 0.35.**

---

## Cheap decisive test (single pilot, gates the whole integrated build)

Build a small end-to-end pilot on the existing ~99k-1M-word corpus, one component at a time, gated
sequentially (cheapest/most-certain-first):
1. **Codebook pilot**: construct vectors via Random-Indexing/BEAGLE-style bind+bundle with PPMI-weighted
   context contributions; spot-check geometry with a small hand-built synonym/antonym probe set (a
   TOEFL-style mini-test, ~20-40 items drawn from the substrate's own grounded vocabulary — cheap, no
   external LLM needed to construct if hand-curated from the existing lexicon).
2. **Coherence-loop pilot**: extract entity+role grids from existing rival-parse output already produced by
   the substrate's hand-rule parser (no new parsing work); compute Guinaudeau & Strube out-degree score on
   true-order vs. same-document order-swapped (SOP-style) negatives over the existing small corpus; check
   for above-chance separation.
3. **Stabilizer pilot**: wrap the codebook's Hebbian bundling update in Oja's-rule decay; run for N update
   steps and check for bounded norm growth (no divergence/NaN) vs. an un-stabilized control that should
   visibly drift/blow up.
Each pilot is cheap (no GPU, small corpus, existing parser output) and gates the next — if (1) fails
(no synonym-geometry signal at all), do not proceed to wire the coherence loop against a broken codebook.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, deflated)

**Prediction 1 (codebook, P=0.32):** Random-Indexing/BEAGLE bind+bundle construction with PPMI-weighted
contributions, built on the substrate's own 99k-1M-word corpus, produces a similarity geometry where
hand-curated synonym pairs score higher cosine similarity than random word pairs at a rate clearly above
chance.
HARD-PASS: >=70% pairwise-ranking accuracy on a >=30-item synonym-vs-random probe set (comparable in spirit
to the TOEFL-synonym benchmark's ~65-67% published range, adjusted for our much smaller corpus).
HARD-FAIL: <=55% (statistically indistinguishable from chance at this sample size) — would indicate the
corpus-size floor genuinely is below what count/co-occurrence methods need, confirming the risk flagged in
the corpus-size literature review above (LSA-degrades-with-corpus-size caution applies to the whole family).

**Prediction 2 (coherence loop, P=0.50, capped at novel-synthesis ceiling):** entity-grid + Guinaudeau &
Strube out-degree scoring, using ALBERT-SOP-style same-document order-swapped negatives, discriminates true
sentence order from swapped order on held-out substrate-corpus documents at a rate clearly above chance,
WITHOUT collapsing to a shallow lexical-overlap shortcut (the arXiv 2110.07198 gameability concern).
HARD-PASS: >=65% true-vs-swapped discrimination accuracy AND performance does not degrade to
chance when local lexical-overlap features are ablated/controlled for (the explicit must-fail control this
note is flagging per the gameability critique).
HARD-FAIL: discrimination accuracy <=55% (chance), OR discrimination that disappears when lexical-overlap
features are controlled for (confirming the shallow-shortcut concern and requiring a harder negative-
construction scheme before this becomes a trustworthy training signal).

**Prediction 3 (stabilizer, P=0.35):** Oja's-rule-decayed Hebbian bundling update remains bounded (no
divergence, no NaN, no runaway magnitude growth) over an extended run where an otherwise-identical
unstabilized Hebbian control visibly diverges or collapses to a degenerate (all-one-direction) state.
HARD-PASS: stabilized run's vector norms stay within a bounded band (e.g. within 2x of initial norm) over
the full run while the unstabilized control exceeds that band or NaNs.
HARD-FAIL: stabilized run ALSO diverges/collapses, or the unstabilized control does NOT diverge either
(meaning the stabilizer is solving a problem that wasn't actually present at our scale — a null-result-by-
construction risk worth checking explicitly before crediting the stabilizer with anything).

**Overall integrated-system prediction (P capped at 0.50 per novel-synthesis discipline):** the three
elements, wired together (Oja-stabilized PPMI-weighted RI/BEAGLE codebook feeding an entity-grid+SOP
contrastive coherence loop), train to a stable, non-degenerate state on the existing corpus and produce a
coherence-loop discrimination signal that beats the original CPCL-v1 null. HARD-FAIL for the whole
integration: if Prediction 1 OR Prediction 3 hard-fails, the integration cannot proceed as designed (broken
codebook geometry or an unstable update loop each independently sink the whole pilot) — this is a genuine
AND-gate, not three independent shots.

---

## Cross-thread synthesis

- **Directly answers, at the mechanism level, what `research_vsa_learned_reader_prior_art_scour_2026-07-18.md`
  left as an abstract "learned role-selection mechanism" gap** — that note found the missing piece was a
  learned, comprehension-scored construction-induction mechanism but did not specify the underlying content-
  vector geometry or the training signal; this note supplies both, plus the stability rule neither prior
  note addressed at all.
- **Confirms, rather than overturns, the substrate's existing choice of bind=convolution/bundle=addition**
  (per the 07-17 sibling scour's cataloguing of Plate/Kanerva/Eliasmith) — Random Indexing and BEAGLE are not
  an alternative algebra, they are the SAME algebra with a corpus-driven (not random) construction recipe,
  directly addressing the CPCL-v1 null's "random content codes" root cause.
- **The task's own cited ALBERT NSP-vs-SOP precedent is confirmed as a near-exact match** by an independent
  lit-scan lane that did not have that framing pre-loaded (query privacy discipline respected — generic
  terms only) — this is a genuine convergent-finding, not a search artifact, strengthening confidence in the
  entity-grid+SOP combination specifically.
- **New risk surfaced that neither prior VET drill flagged**: the shuffle-test/permutation-based coherence
  signal gameability critique (arXiv 2110.07198) — this is a must-fail control that should be added to
  whatever cell design implements Prediction 2, not discovered after the fact.

---

## Substrate-product implications

1. The honest, narrow, defensible claim: this note assembles three separately-published, separately-credited
   mechanisms (RI/BEAGLE binding algebra + PPMI weighting; entity-grid coherence + SOP-style negative
   construction; Oja's-rule stabilization) into one glass-box training loop for the substrate's own content
   codebook — it does NOT claim a new binding algebra, a new coherence theory, or a new learning-rule
   mathematics. All three are credited, none are re-derived as novel.
2. Three cheap, sequenced, existing-corpus pilots are now open (per the Cheap decisive test section above),
   each gating the next, each requiring no GPU and no new grounding/data-collection work — reuses the
   substrate's own existing parser output and corpus.
3. A concrete must-fail control (lexical-overlap ablation on the coherence-discrimination signal) is now
   pre-registered before any cell design work starts, directly forestalling a repeat of the CPCL-v1 failure
   mode (a self-supervised target that looks like it's working but is secretly solving a shortcut).
4. The weakest link, honestly flagged: element 3 (homeostatic stabilizer) has zero direct VSA/HDC precedent
   — if the integrated pilot fails, this is the first place to look for a construction-specific reason (e.g.
   Oja's PCA-alignment side-effect fighting against whatever geometry the codebook/coherence loop need,
   rather than a pure stability failure).

---

## Citations (verified count)

**3 parallel Sonnet lit-scan lanes this cycle, ~40 distinct external primary sources located this session**
across the three elements (see each lane's own citation list, reproduced in full in the per-element sections
above): element 1 (~15 sources: Kanerva/Sahlgren RI lineage, Widdows & Cohen Semantic Vectors, Jones &
Mewhort BEAGLE, Recchia et al. 2015, Landauer/Foltz/Laham LSA, Lund & Burgess HAL, Levy & Goldberg 2014/2015,
Kleyko et al. HyperEmbed); element 2 (~12 sources: Lan et al. ALBERT, StructBERT, Barzilay & Lapata,
Elsner & Charniak, Guinaudeau & Strube, Nguyen & Joty, Clark et al. ELECTRA, van den Oord et al. CPC, plus
the flagged-not-fully-read arXiv 2110.07198 gameability critique); element 3 (~15 sources: Turrigiano et al.
1998/2008, Turrigiano & Nelson 2004, Tetzlaff et al. 2011, Oja 1982, Sanger 1989, Bienenstock/Cooper/Munro
1982, Izhikevich & Desai 2003, Kleyko et al. HDC survey, Hebbian-Descent/RMS-EMA neuromorphic analogy
papers). All URLs preserved in each lane's own report; none re-verified independently by the synthesizing
pass beyond cross-checking internal consistency across the three lanes — per calibration discipline this
absence-of-independent-re-verification is folded into the deflation applied above, not treated as
additional confidence.

---

## Status

Written per research-agent contract. USER-locked discipline applied: **no `exp_dev_handoff_*.md` or
`strategy_request_to_*.md` routing files written** (ferry mechanism deprecated per current session
instructions) — every actionable pointer (ADOPT/ADAPT/BUILD-FRESH calls, cheap decisive test, falsifiable
predictions with pre-registered HARD-PASS/HARD-FAIL thresholds, must-fail gameability control) is delivered
inline above. No cap_map or strategy files modified.
