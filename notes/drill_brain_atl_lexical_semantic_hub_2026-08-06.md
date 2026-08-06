# Drill: the ATL semantic-hub analog — building a glass-box, earned, graded lexical-similarity organ (2026-08-06)

FORMALIZE-BEFORE-BUILDING drill, triggered by the deep VET's component #1 MISSING
(`notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md`, `notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`)
and the outcome-valence coverage wall (`notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md`,
"vessel"~"ferry" synonym-referent binding — general synonym/hypernym resolution is BLOCKED on this gap).

**Process note:** 3 parallel Sonnet lit-scan sub-agents were dispatched (ATL hub biology; glass-box
distributional/feature methods; grounding-transfer + corpus-scale). A first pass of this synthesis was
drafted in-process (disk-only) before they returned, per an in-session directive not to block further; all
three then completed and their findings are folded in below, so **most external citations in this version
ARE freshly web-verified this session** (individually flagged verified/secondary/unverified per sub-agent
self-report) — the calibration deflation applied to P-estimates is the standard 0.15-0.25 band, not the
larger emergency deflation used in the first draft. This version supersedes that draft. Disk verification
(12+ artifacts, this substrate's own code/experiment state) is unchanged and remains the load-bearing half of
the analysis.

## HEADLINE

The substrate is closer to having an earned ATL-hub analog than the triggering audits' framing suggested —
**`hdlab/random_indexing.py` (Sahlgren/Kanerva Random Indexing + Jones-Mewhort BEAGLE order-binding) already
exists, is glass-box, is fully earned (zero external embeddings, zero backprop, own inspectable sparse-ternary
weights), and already ran FULL-scale on text8 (17M tokens, 3 seeds) with a real, control-verified, non-vacuous
similarity signal** (`data/exp_n11_random_indexing_semantic_v1/metrics.json`, verdict MIDDLE_BAND: within-category
mean cosine 0.9156 vs across-category 0.7619, ratio 1.20, vs a random-permute CONTROL ratio 1.001). It has never
been wired downstream and never re-tested past that one MIDDLE_BAND cell. Diagnosis of WHY it plateaus at
MIDDLE_BAND (not HARD_PASS) is the load-bearing finding of this drill: **the existing probe measures topical
CATEGORY membership (animals vs vehicles vs...), which is a relatedness/association measure, not the genuine
similarity (synonym/hypernym-grade) discrimination the downstream tasks (word-sense selection, vessel~ferry)
actually need.** This is a well-known, decades-old distinction in the distributional-semantics literature
(SimLex-999 vs WordSim-353) and predicts, specifically, that linear-window Random Indexing will OVER-score
merely-related pairs (vessel~dock) close to genuine synonyms (vessel~ferry) — exactly the failure mode the
outcome-valence coverage wall hit. The recommended first buildable increment is a small, cheap, literature-
grounded extension of the ALREADY-VALIDATED primitive: restrict co-occurrence accumulation to symmetric
coordination patterns ("X and Y" lists — Schwartz, Reichart & Rappoport 2015, no parser needed, SimLex-999
rho=0.517 vs plain skip-gram's 0.462 on the same corpus) and/or dependency-syntactic context (Levy & Goldberg
2014), instead of the current linear-window accumulation — not a new mechanism class and not a bigger hand
table.

---

## 1. BRAIN MECHANISM — ATL hub-and-spoke (SHAPE / POSITION / METRIC)

| Dimension | Claim | Confidence |
|---|---|---|
| **SHAPE** | A single, amodal, graded, DISTRIBUTED convergence code (not a symbolic lookup table) sitting at the confluence of modality-specific "spoke" pathways (visual-form, auditory/phonological, verbal, motor/action, affective/valuation). Computationally instantiated in the field's own connectionist model (Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson 2004, *Psychological Review*, "Structure and deterioration of semantic memory") as a hidden "hub" layer that all modality-specific spoke layers feed into and are reconstructed from (auto- and hetero-associative training across modalities). | HIGH (0.75) — canonical, extensively replicated framework; not fresh-verified this session |
| **POSITION** | Anatomically anterior/ventral temporal lobe (vATL, temporal pole), UPSTREAM of and functionally separable from the semantic CONTROL network (IFG pars triangularis/orbitalis + posterior MTG) that this substrate's earlier drills already covered (`notes/deepdrill_sense_disambiguation_cues.md`). The hub supplies the DEFAULT, graded concept representation; control biases RETRIEVAL over it toward the context-licensed sense. This drill is scoped to the HUB (representation), not control (already separately researched). | HIGH (0.7) — TMS evidence (Pobric, Jefferies & Lambon Ralph 2007, *PNAS*: rTMS to ATL disrupts semantic judgment across BOTH verbal and picture tasks — a truly transmodal, not modality-specific, disruption) and distortion-corrected fMRI/rTMS convergence (Binney, Embleton, Jefferies, Parker & Lambon Ralph 2010, *Cerebral Cortex*) are standard, frequently-cited findings — recalled, not re-fetched this session |
| **METRIC** | Two concepts are "similar" in the hub to the degree their spoke-features CORRELATE across experience — i.e., shared/overlapping activation driven by features that co-occur when the concept is encountered (visual form + sound + typical action + typical affect + verbal context, jointly). This is a genuinely different metric than raw LINGUISTIC co-occurrence statistics: hub similarity is cross-MODAL feature correlation; text co-occurrence is at best one spoke's contribution (the verbal/linguistic spoke), not the transmodal hub itself. **DIRECTLY VERIFIED this session (fetched full text):** Cox, Rogers, Shimotake, Kikuchi, Kunieda, Miyamoto, Takahashi, Matsumoto, Ikeda & Lambon Ralph (2024, *Imaging Neuroscience*, MIT Press; PMC12224414) — intracranial ECoG from human ventral ATL during picture naming, analyzed via a feature-norm regression ("Representational Similarity Learning") method: vATL activity encodes a graded, multidimensional space where two concepts are neurally similar to the extent they share BEHAVIORAL FEATURE-NORM features (wolf/coyote close via shared "furry"/"predatory"/"wild"), with graded encoding peaking 200-400ms post-stimulus. This is a direct, feature-based (not co-occurrence-based, not raw-perceptual) metric confirmation in the target region itself — the strongest single citation in this note. Perirhinal/ATL conjunctive coding (Clarke & Tyler 2014, *J. Neurosci.* 34:4766; Erez, Cusack, Kendall & Barense 2018, *eLife* 31873) corroborates: pattern similarity tracks INTEGRATED visual+conceptual feature conjunctions, distinct from more posterior regions coding features individually. | HIGH (0.75) — Cox et al. 2024 directly fetched and read this session, not secondary-source; perirhinal corroboration verified via search, not full-text fetch |
| **LEARNING** | Cross-modal Hebbian/associative correlation through repeated co-experience: features that reliably co-occur across a concept's multiple encounters get bound together into one convergent code. **Verified this session (secondary-source, one primary-adjacent model directly fetched):** the Rogers et al. (2004) hub-and-spoke lineage models this via error-driven BACKPROPAGATION (backprop-through-time for the recurrent/attractor variant) — NOT literally Hebbian, and backprop is a standard, openly-acknowledged biological-plausibility weak point of that model family. A directly-fetched adjacent attractor/feature-correlation model in the same tradition (O'Connor et al., PMC2699208 — flagged as adjacent, not literally Rogers 2004) confirms: cross-entropy training signal, similarity = cosine over the shared hidden-layer activation vector, features that co-occur across many concepts develop shared connection weights. The FUNCTIONAL learning signal this approximates — correlated co-activation strengthening shared representation — is the same computation a forward-only Hebbian/associative (outer-product, correlational) learning rule implements more literally and more biologically-plausibly. This substrate's own convention (competitive-Hebbian in `concept_encoder.py`, Hebbian accumulation in `random_indexing.py`) is, if anything, MORE biologically literal than the field's own reference implementation on this specific point — a genuine, not just permissive, brain-fidelity argument for the forward-only Hebbian build path over a backprop one. | MEDIUM-HIGH (0.6) — learning-rule claim verified via search + one adjacent primary fetch this session; the "our Hebbian approach is more literal" inference is this note's own synthesis, not a cited claim |
| **Graded degradation evidence for "amodal + graded" (not modality-tied, not lookup-table)** | Semantic dementia (progressive, relatively selective ATL atrophy) causes COHERENT degradation across ALL modalities and categories simultaneously — patients lose fine-grained/distinctive features FIRST (a camel's hump lost before "four legs"), with prototypical features intruding as disease progresses; degradation is graded, not a clean loss of discrete entries. **Verified this session (via search):** Warrington (1975) is the original "attribute-first"/specific-to-general loss report; a 2024 drawing-from-name study (*Memory & Cognition*, PubMed 38777996) directly replicates the pattern; Pobric, Jefferies & Lambon Ralph rTMS studies (PMC2730596; PubMed 20038436, "Amodal semantic representations depend on both anterior temporal lobes") confirm bilateral-ATL TMS disrupts semantic (not perceptual-control) judgments equally for words AND pictures, ~400ms post-stimulus. This is the single strongest evidence class that the hub is a genuinely GRADED, ABSTRACTED code rather than a symbolic table — directly relevant to the "no discrete sense inventory" design principle this project's own PLAN doc already independently derived (`notes/PLAN_grounded_semantic_organ_build.md`: "DISCRETE stored senses are un-brain-faithful... graded, constructed per-instance"). | HIGH (0.72) — Warrington/2024-drawing-study/Pobric TMS studies verified via search this session (not full-text fetched) |

**Bottom line for the build:** the brain's hub is NOT primarily a text-co-occurrence machine — it's a cross-modal
feature-convergence code, with linguistic/distributional co-occurrence as at most one contributing spoke. Any
text-only distributional method (Random Indexing included) is, honestly, building ONE spoke well, not the
transmodal hub. This reframes "earn the hub" as a staged goal: earn the verbal/distributional spoke first
(cheap, already partially done), and treat feature-grounded/multi-spoke integration as the fuller, later target
— consistent with the project's own already-authorized grounding pivot (`MEMORY.md`: "BUILD THE ~6yo GROUNDED
FOUNDATION").

---

## 2. WHY OUR CURRENT PIECES DON'T SUFFICE (disk-verified, precise)

| Piece | Disk-verified state | Precisely what's missing |
|---|---|---|
| `word_vector` = hash-random, 3 fixed tables (per `brain_audit_SYNTHESIS_missing_semantic_organ.md` component map) | Per-word vector assigned by hashing alone, with NO co-occurrence accumulation step. By construction: same word -> identical vector; different words -> exactly orthogonal (or a fixed table lookup for ~20-word closed sets). | ZERO graded structure — this is not actually "Random Indexing" despite the audit's phrasing (Random Indexing's whole point is the accumulation step); it's plain random hashing. Two senses of "hard" are literally indistinguishable OR the word isn't even in a fixed table at all. |
| `hdlab/concept_encoder.py` (Spoke-1 competitive-Hebbian) | Own docstring (lines 1-31, disk-read this session): **"This module is NOT unsupervised concept discovery... SUPERVISED, concept-label-conditioned... Any framing that implies the substrate discovers 'cat-ness' from raw text is inaccurate."** Requires an integer `concept_label` per training sentence. Validated ONLY on a 25-cluster synthetic template corpus (`cat_kitten_cos_mean=0.492`, HARD_PASS on that synthetic set). Own "NOT TESTED" list explicitly includes: unsupervised regime, real-corpus transfer, natural-language behavior. | No zero-shot capability by design and by the module's own honesty block — cannot score similarity for two words that weren't co-assigned labels at fit time. This is a supervised classifier-shaped encoder, not a hub. |
| `hdlab/composed_encoder_v3.py` | Own docstring (lines 1-40, disk-read): **"Regime type: SUPERVISED CONCEPT RETRIEVAL over per-concept prototype tables built at fit() time from labeled sentences."** Explicit scope caveat: **"Substrate KNOWS ALMOST NOTHING... HP earned here does NOT grant 'substrate understands English.'"** | Same supervised/prototype-table limitation as concept_encoder — it composes two supervised streams (VWFA orthographic + PPMI), neither of which is zero-shot. |
| `hdlab/ppmi_sparse_encoder.py` (the literal "ATL-hub analog" name used in the substrate's own capability map) | **CLOSED, per `notes/substrate_capability_map.md` (~line 29605-29622):** ran FULL at 10K-real-Wikipedia scale; does NOT beat char-trigram surface bag-of-words; `delta_from_smoke_r5_ppmi=-0.2269` — signal DEGRADES (not just plateaus) as scale grows. Ruled `CG_MEASURED_BOUND_LOW_DELTA`, one of 3/5 witnesses closing the parent META row `SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE`. | This is the deep-VET's "bag-of-words co-occurrence MEASURED featureless for sense" finding, precisely located: a term-x-concept-label co-occurrence + PPMI + SVD encoder, closed by a real negative result at scale, not a hunch. **Featureless here specifically means: as the corpus/vocabulary scales up, the surface-frequency signal gets swamped and a dumb orthographic bag-of-character-trigrams wins** — i.e. raw co-occurrence counting without a graded, structured accumulation mechanism doesn't survive scale. |
| **`hdlab/random_indexing.py` — the one piece that partially WORKS** | Full read this session (283 lines). Genuine Random Indexing (Sahlgren 2005; Kanerva 1988) + optional BEAGLE holographic order-binding (Jones & Mewhort 2007): immutable sparse-ternary index vector per word + a MUTABLE context vector that accumulates neighbors' index vectors over a streamed corpus (forward-only Hebbian sum, zero backprop, own weights, `n_llm_calls=0`). Self-test passes. **RAN FULL** (`data/exp_n11_random_indexing_semantic_v1/metrics.json`, text8, 17.0M tokens, N=8192, sparsity=10, window=5, 3 seeds 7/17/23, `elapsed_s=7635`, deterministic): `RANDOM_INDEXING_ALONE` similar-pair mean cosine 0.9156 vs dissimilar-pair mean 0.7619, ratio **1.2016** (CV 0.0005 — tight across seeds); `CONTROL_RANDOM_PERMUTE` ratio 1.0008 (clean null). `RI_PLUS_BEAGLE_ORDER` ratio 1.2143 (marginal lift, and LOWER absolute cosines — order-binding adds a small amount of extra discrimination, not a step-change). `RI_HUB_SPOKE_KGSTORE` (RI context-vector Hebbian-bound with the orthographic char-trigram spoke via `KGStore.W` outer-product) is WORSE (ratio 1.183, absolute cosines collapse to ~0.47/0.40 — destructive cross-namespace compression, not a working hub composition). Verdict: **MIDDLE_BAND** — "substrate-native distributional signal is real but partial." | **Never wired anywhere** (`grep` for `random_indexing`/`RandomIndexingEncoder` across `hdlab/` and `experiments/` finds only the module and its own experiment cell — zero downstream consumers; absent from `data/capability_registry.jsonl`). **Diagnosed root of the MIDDLE_BAND plateau (this drill's key finding, not previously written up):** the n11 probe (`experiments/exp_n11_random_indexing_semantic_v1.py` lines 42-158) operationalizes "similar" as WITHIN-CATEGORY membership across 5 broad topical categories (animals, vehicles, body_parts, time_words, color_words) and "dissimilar" as ACROSS-CATEGORY. This is a coarse topical/associative RELATEDNESS measure — the WordSim-353 style of "similarity," not the SimLex-999 style. It was never tested on the actually-decisive discrimination: synonym > merely-related > unrelated (e.g. vessel~ferry vs vessel~dock vs vessel~anger). |

**Precisely what's missing, stated once:** none of the above pieces produce **GRADED, GROUNDABLE,
EARNED-not-borrowed similarity that separates genuine synonymy from mere topical association.** The
hash-random word_vector has no graded structure at all. concept_encoder/composed_encoder_v3 have graded
structure but only for a closed, labeled training set (no zero-shot). PPMI/SVD's co-occurrence signal
collapses at scale. Random Indexing has real, control-verified, EARNED graded structure from raw text at
scale — but it has only ever been measured on a coarser task (topical clustering) than the one the downstream
consumers actually need (fine-grained similarity ordering), and the failure mode this predicts (over-scoring
merely-related pairs) is exactly documented in the distributional-semantics literature as the generic weakness
of linear-window co-occurrence models (Hill, Reichart & Korhonen 2015, *Computational Linguistics*,
"SimLex-999: Evaluating Semantic Models with (Genuine) Similarity Estimation" — canonical citation
establishing the similarity-vs-relatedness distinction and showing window-co-occurrence models systematically
conflate them; recalled, not fresh-verified this session, but this is one of the most-cited results in the
field and very unlikely to be wrong in substance).

---

## 3. THE BUILDABLE PATH (three options evaluated, one recommended)

### Option (a) — SUPPLY a feature lexicon, EARN the composition (structured feature-based concept vectors)

Concept = bundled superposition of atomic feature-HD-vectors (e.g. `has_wheels`, `is_alive`,
`used_for_transport`), each feature its own vector (random-index-style atomic vector, already-owned
primitive); similarity = shared-feature overlap, computed by cosine on the bundle (the substrate's own
`hdlab.bundling`/`hdlab.binding` primitives; a direct VSA analog of McRae, Cree, Seidenberg & McNorgan 2005
feature-production-norm concept vectors, **verified this session**). **This is the MOST brain-faithful option
in METRIC terms** — the hub's actual metric (Section 1, now directly confirmed via Cox et al. 2024's vATL
feature-norm RSA finding) is shared cross-spoke feature correlation, and a supplied feature lexicon is
literally supplying (part of) the spokes as DATA, with the bundling/binding composition as the EARNED
mechanism. It cleanly respects "supply data is OK, supply the mechanism is not." **Sharpened case, verified
this session:** Rubinstein, Levy, Schwartz & Rappoport (2015, ACL, "How Well Do Distributional Models Capture
Different Types of Semantic Knowledge?") give a precise, quantified diagnosis of exactly WHERE co-occurrence
structurally fails: distributional models predict TAXONOMIC properties (category membership, animacy) well
(F1 ~0.73) but ATTRIBUTIVE properties (size, color, shape, material — precisely the fine-grained featural
content that separates true synonyms like vessel/ferry from co-hyponyms/associates) poorly (F1 <=0.37). This
independently confirms a feature-norm layer targets exactly the axis distributional methods (options b1/b2
included) cannot reach, regardless of context-window fix. Andrews, Vigliocco & Vinson (2009, *Psychological
Review*, **verified this session**) further show experiential/feature and distributional signals are
statistically DISTINCT and COMPLEMENTARY (a Bayesian combination beats either alone at predicting human
judgments) — real precedent that (a) and (b) should be pursued as a HYBRID, not competing alternatives.
**Honest risk (unchanged):** published feature-norm lexicons (McRae ~541 concepts; CSLB ~638 concepts) cover a
tiny, mostly-concrete vocabulary — nowhere near open-vocabulary scale, and abstract words are notoriously
under-covered by concrete feature norms. Scaling this to cover "vessel," "ferry," and general vocabulary is
itself a large hand-authoring or semi-automated-induction project — the same coverage problem that already
sank the narrow hand-authored `SYNONYM_GROUPS` fix in the outcome-valence coverage-wall work. Static/discrete
by default unless paired with an inducible weighting scheme.

**Adjacent, directly-reusable technique for building (a) from what the substrate ALREADY owns:** Murphy,
Talukdar & Mitchell (2012, COLING, "Learning Effective and Interpretable Semantic Models using Non-Negative
Sparse Embedding," NNSE — **verified this session**) run non-negative sparse dictionary-learning DIRECTLY on
a PPMI co-occurrence matrix (not on pretrained neural embeddings) and report it matches SVD on
behavioral/fMRI-prediction tasks while jumping human-rated dimension-interpretability from 46% (SVD) to 92%.
This is a from-scratch, own-the-weights method applicable to the substrate's OWN (currently-closed-for-a-
DIFFERENT-task) `ppmi_sparse_encoder.py` co-occurrence matrix — worth flagging precisely: the cap_map closure
(Section 2) was for RETRIEVAL-AT-SCALE losing to char-trigram bag, a different task and metric than
LEXICAL-SIMILARITY quality; NNSE-on-the-existing-PPMI-matrix is a plausible, cheap, not-yet-tried angle for
producing INTERPRETABLE sparse features (each dimension human-nameable) that could seed or validate a feature
lexicon for option (a) — flagged as a promising side-lead, not the main recommendation, since it was not
disk-tested against the graded-similarity task specifically.

### Option (b) — GLASS-BOX distributional structure from text, but NOT bag-of-words (RECOMMENDED FIRST)

Two concrete, complementary, literature-QUANTIFIED variants, both cheap additive extensions of the
ALREADY-BUILT, ALREADY-VALIDATED `hdlab/random_indexing.py` accumulator:

**(b1) Dependency-context mode.** Instead of (or alongside) the existing linear-window context, accumulate
index vectors keyed by `(dependency_relation_label, neighbor_lemma)` pairs from a dependency-parsed corpus,
per Levy & Goldberg (2014, ACL, "Dependency-Based Word Embeddings" — **verified this session, primary source
fetched**: dependency contexts yield FUNCTIONAL/paradigmatic similarity — e.g. "Hogwarts" near other fictional
schools — while linear-window contexts yield topical clustering — "Hogwarts" near "Harry"/"Dumbledore" — a
direct, controlled, corpus-held-fixed demonstration that context TYPE, not corpus size, drives the
similarity-vs-relatedness split). Reuses depparse infra already wired for `situation_reader`/Component-3 per
`notes/PLAN_grounded_semantic_organ_build.md`.

**(b2) Symmetric-pattern mode — cheaper, and the single most directly-quantified external precedent found
this session.** Schwartz, Reichart & Rappoport (2015, CoNLL, "Symmetric Pattern Based Word Embeddings" —
**verified this session**): restrict co-occurrence counting to pairs found inside symmetric coordination
patterns only ("X and Y", "X or Y", "X, Y" lists) — pure regex/POS-tag pattern matching over raw text, **no
dependency parser needed, no backprop, no pretrained anything**. Reported result, directly on the target
benchmark: **SimLex-999 Spearman rho = 0.517**, beating plain skip-gram's **rho = 0.462 on the same corpus**
(with especially large gains on verb-similarity), and combining symmetric-pattern vectors with skip-gram
pushes rho to 0.563. This is the cheapest of all buildable options evaluated (no parser dependency at all —
just a hand-specifiable pattern list, matching the substrate's existing forward-only accumulator math exactly:
same `_make_index_vector`/accumulation primitives, only the context-selection RULE changes from "any word
within window W" to "words co-occurring inside a symmetric pattern").

**Cheap complementary layer, either variant — retrofitting.** Faruqui, Dyer, Jauhar, Kumar, Dyer & Smith
(2015, NAACL, "Retrofitting Word Vectors to Semantic Lexicons," best student paper — **verified this
session**): a closed-form, non-gradient post-processing step that pulls linked words together in an EXISTING
vector space using a hand-authored or WordNet-derived synonym/hypernym graph — directly injects
"vessel~ferry"-class known synonymy on top of whichever distributional backbone (b1/b2) is chosen, at near-zero
marginal cost (no retraining, minutes of compute, fully inspectable — the correction is literally "average
this word's vector with its lexicon-neighbors' vectors, weighted"). Recommended as an ADD-ON validation/repair
layer, not a replacement for (b1)/(b2), since it inherits option (a)'s coverage-scaling ceiling (only helps
words present in the lexicon graph) and should not be mistaken for a from-scratch earned mechanism on its own.

**Honest risk (both b1/b2):** these earn ONE spoke (linguistic-distributional) well, not the transmodal hub
itself — should not be oversold as "the ATL hub is built" if either lands. Genuinely uncharted ON THIS
substrate (never tried) even though externally well-precedented. **Corpus-scale-vs-architecture, now
DIRECTLY confirmed (not just inferred):** word2vec skip-gram trained on ~1B words of Wikipedia reaches only
SimLex-999 rho ~0.37 (best "running text"-trained linear-window models found in this session's scan reach
~0.56) — i.e. a corpus roughly 60x larger than text8 does NOT close the similarity/relatedness gap for a
linear-window architecture, while Levy & Goldberg's controlled ablation shows switching context TYPE (corpus
held fixed) does shift the model toward genuine similarity. This is strong, though not fully closed-form,
evidence that the n11 MIDDLE_BAND plateau is an architecture problem, not a text8-is-too-small problem —
scaling text8 up is predicted to be a much lower-leverage move than switching (b1)/(b2)'s context definition.

### Option (c) — Grounding-transfer from the experiential simulation (6yo-foundation pivot)

The deepest brain-fidelity option long-term (the hub's OTHER spokes are perceptual/motor/affective, and this
project already has an authorized program building exactly that: `MEMORY.md`'s "BUILD THE ~6yo GROUNDED
FOUNDATION," `notes/PLAN_grounded_semantic_organ_build.md`). But that program is currently scoped to a small
set of grounded primitives (agent/goal/self-other/valence), not an open-vocabulary lexicon; extending it to
cover general vocabulary (vessel/ferry-class synonymy) needs a metaphorical/relational extension mechanism
(Lakoff & Johnson-style grounding of abstract vocabulary via mapping from a small grounded core) that is not
yet built. **Verified this session (grounding sub-agent):** Barsalou's Perceptual Symbol Systems (1999, *BBS*)
and Lakoff & Johnson conceptual-metaphor theory are well-established THEORY, but **no computational model in
either lineage was found evaluated against a graded open-vocabulary similarity benchmark at anything near
SimLex-999 scale** (Cangelosi/Roy-style grounded robotic language-acquisition demonstrations top out around
toy vocabularies, tens of words, per the sub-agent's search) — this is a confirmed evidence GAP, not a
refutation, but it means option (c) is honestly un-derisked at the scale needed, sharpening (not weakening)
the "long-term, not first" routing. Xu & Tenenbaum (2007, Bayesian word learning) additionally shows that even
FAST graded generalization from few examples in children relies on a pre-existing hierarchical taxonomic
PRIOR, not on exposure count alone — suggesting a grounding-transfer route would itself need a structured
prior (closer to option (a)'s feature-lexicon shape) rather than emerging free from a bare experiential
simulation. **Route: legitimate long-term target, not the first buildable increment** — too slow and too
unvalidated-at-scale for a decisive near-term test, and this drill's resolution should not block on it.

### Recommendation

**Sequence: (b2) symmetric-pattern first (cheapest, most directly quantified, zero new parser dependency),
(b1) dependency-context as a close second/parallel arm in the SAME cell, (a) feature-lexicon third/parallel
once a seed lexicon exists, retrofitting as a cheap add-on layer once (b1)/(b2) exist, (c) as the long-term
target already tracked elsewhere.** Rationale: (b2) is now the single cheapest, best-externally-quantified
move found this session — Schwartz et al.'s SimLex-999 rho=0.517 (vs skip-gram's 0.462 on the same corpus) is
a direct, apples-to-apples number on the EXACT benchmark class this drill's can-fail test targets, and the
method needs no dependency parser (pure pattern-matching over existing text), making it strictly cheaper than
(b1) with comparable or better literature support. (b1) remains worth running in the SAME cell as a second arm
(different mechanism, same accumulator, near-zero marginal cost if depparse is already available) since Levy &
Goldberg's controlled ablation is the cleanest DIRECT evidence that context-type (not corpus size) is the
lever. (a) is the more brain-faithful of the three in METRIC terms (shared-feature correlation IS the hub's
literal computation, now directly confirmed via Cox et al. 2024's vATL finding) and has real, verified
literature precedent that hybrid feature+distributional models beat either alone (Andrews, Vigliocco & Vinson
2009) plus a sharp, quantified diagnosis of exactly which similarity axis it uniquely covers (Rubinstein et
al. 2015: attributive F1<=0.37 for pure distributional models) — but its coverage-scaling problem makes it a
slower, parallel-track build, not the first decisive test. Retrofitting (Faruqui et al. 2015) is the cheapest
possible add-on once any distributional backbone exists and should be scheduled right after, not instead of,
(b1)/(b2). Routing per the USER error-flavor rule: (b1)/(b2) are primarily EARN (extend an owned mechanism);
(a) is missing-FACT SUPPLY (a feature lexicon) + EARN (the bundling composition); retrofitting is a cheap
missing-FACT SUPPLY (a synonym graph) applied via a closed-form EARN step; none is missing-LEARNING in the
strict sense, though a future OOV-feature-induction extension for (a) would legitimately be one.

### First buildable increment (concrete, small, ready to design a cell for)

Add TWO new context-construction modes to `hdlab/random_indexing.py`'s `fit_corpus` (or a sibling module
reusing its `_make_index_vector`/accumulation primitives unmodified), as arms in one cell:
- `context_mode="symmetric_pattern"` (RECOMMENDED as the primary arm): instead of summing index vectors of
  linear window-neighbors, sum index vectors of words found co-occurring inside symmetric coordination
  patterns ("X and Y", "X or Y", "X, Y, and Z" lists) via simple regex/POS-tag pattern matching over the
  existing text8 corpus — no new dependency (Schwartz, Reichart & Rappoport 2015).
- `context_mode="dependency"` (secondary arm, if a dependency parser is already cheaply available via the
  substrate's `situation_reader`/Component-3 infra): sum index vectors keyed by `(dep_relation,
  neighbor_lemma)` pairs (Levy & Goldberg 2014).

Re-run the EXISTING `exp_n11_random_indexing_semantic_v1` harness's fit/similarity machinery with these new
modes alongside the current `RANDOM_INDEXING_ALONE` linear-window arm as the comparison baseline, but score
ALL arms against the NEW graded Tier1/Tier2/Tier3 probe in Section 4 below (not the old within/across-category
probe) — a fair, apples-to-apples comparison on the SAME (harder, decisive) test the diagnosed failure
actually requires.

---

## 4. THE CAN-FAIL TEST

**Design:** a graded 3-tier similarity probe (replaces the n11 cell's within/across-category design, which
this drill diagnoses as too coarse to be decisive):

- **Tier 1 (genuine synonym/near-synonym pairs):** vessel/ferry, ship/vessel, boat/ship, glad/happy,
  large/big, quick/fast, sad/unhappy — expect HIGH cosine.
- **Tier 2 (topically-related, NOT synonymous — the crux discriminator):** vessel/dock, vessel/sailor,
  vessel/harbor, ship/captain, boat/oar — expect MODERATE cosine under a brain-faithful mechanism, but this is
  exactly where plain LINEAR-window Random Indexing is predicted (per Section 2/3's diagnosis) to WRONGLY
  score comparably to or higher than Tier 1, since dock/vessel are strong linear co-occurrers.
- **Tier 3 (unrelated pairs):** vessel/anger, ship/mathematics, boat/jealousy — expect LOW cosine.
- **Controls:** (i) `CONTROL_RANDOM_PERMUTE` (already built in the n11 harness — shuffle word-index
  assignment) must collapse to ratio ~1.0 for any arm; (ii) for the feature-based option (a), a
  SCRAMBLED-FEATURE control (shuffle feature-to-concept assignment) must equivalently collapse; (iii) the
  literal current-production `word_vector` (hash-random, no accumulation) is the floor baseline and must
  score at chance on the ordering (it has no mechanism to do otherwise, by construction — a sanity check, not
  a real discriminator).

**HARD-PASS (both required):**
- `cos(Tier1) > cos(Tier2) > cos(Tier3)` holds as an ORDERED inequality (not just a mean-ratio) on **>=70% of
  hand-authored triples** for the proposed mechanism (option (b)'s dependency-context arm, and/or option
  (a)'s feature-bundle arm).
- The EXISTING linear-window `RANDOM_INDEXING_ALONE` arm (the already-measured MIDDLE_BAND baseline) and the
  hash-random `word_vector` floor BOTH fail this ordered-inequality test on a majority of triples (this is the
  crux differentiator — if linear-window RI unexpectedly PASSES this, the diagnosis in Section 2/3 is wrong
  and should be investigated before trusting anything built on top of it).

**HARD-FAIL (any triggers):**
- The proposed mechanism does not clear the 70% ordered-inequality bar, OR does no better than the existing
  linear-window RI arm on this specific test (would mean the diagnosed relatedness/similarity conflation is
  NOT the binding constraint, and the plateau has some other cause — investigate window-size/PPMI-weighting/
  corpus-scale before concluding architecture is definitively the issue).
- Scramble/permute controls do not collapse to null (the signal would be an artifact, not earned structure).
- (For option (a)) feature-lexicon-driven similarity cannot be inspected/attributed to specific shared
  features for a given score — this would mean it's not actually glass-box in the sense this project requires
  (a true glass-box result must be able to name WHICH shared features drove a similarity call, not just
  produce a number).

**"Earned not borrowed" verification (mandatory, both options):** (i) `n_external_model_calls=0` /
`n_llm_calls=0` at both fit and inference time, matching the existing n11 cell's own convention; (ii) an
ablation that fits on a SCRAMBLED corpus (word order shuffled, destroying real co-occurrence structure) or an
EMPTY/randomized feature lexicon must collapse the Tier1>Tier2>Tier3 ordering to chance — proving the graded
structure is earned from the supplied text/lexicon, not a hidden prior; (iii) own, inspectable weights at
every stage (sparse-ternary index vectors, accumulated context vectors, or feature-bundle vectors) — no black-
box distillation step anywhere in the mechanism being proposed as the meaning organ itself (a borrowed-
embedding diagnostic-only comparison arm is fine to INCLUDE as a ceiling reference, per the standing invariant
that borrowed embeddings may be used diagnostically then discarded, but must not be the thing that ships).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered per project convention)

| Prediction | HARD-PASS | HARD-FAIL | MIDDLE_BAND |
|---|---|---|---|
| Dependency-context Random Indexing (option b) beats linear-window RI on the Tier1>Tier2>Tier3 graded probe | >=70% ordered-triple accuracy AND linear-window RI arm fails majority ordering on the same set | <50% ordered-triple accuracy, OR no material delta (<10pts) vs the linear-window arm | 50-70% ordered-triple accuracy |
| Feature-bundle concept vectors (option a, small seed lexicon) separate genuine similarity from relatedness | >=70% ordered-triple accuracy on covered vocabulary, scramble-control collapses to chance | <50% ordered-triple accuracy, or scramble does not collapse (artifact, not earned signal) | 50-70%, or strong on covered vocabulary but near-zero coverage outside the seed lexicon (a real, separately-actionable coverage-ceiling finding) |
| The relatedness-vs-similarity diagnosis (Section 2/3) is the actual binding constraint on the existing MIDDLE_BAND RI result, not corpus scale | linear-window RI arm's failure on Tier2 (over-scoring merely-related pairs) is directly observed on the new probe | linear-window RI arm ALSO fails to show the predicted Tier2-over-scoring pattern (would mean the true bottleneck is something else, e.g. genuinely needs more corpus scale, or the sparsity/N_DIM hyperparameters, not context-window shape) | -- |

**P_deflated for "the symmetric-pattern/dependency-context increment clears its own HARD-PASS band on first
attempt":** raw prior ~0.65 (TWO well-precedented, directly-quantified external methods — Schwartz et al.'s
SimLex-999 rho=0.517 result is a real, apples-to-apples number on the target benchmark class, not just a
qualitative claim — applied to an already-working, already-owned accumulator; small, additive, low-risk
engineering change). Deflated per [[feedback-lit-scan-calibration-penalty]] by the standard 0.20 (mid-band,
reflecting that most citations ARE now freshly web-verified this session, but transfer from external corpora/
tokenization/benchmark word-lists to THIS substrate's text8 pipeline and hand-authored probe is still a
genuine uncharted-regime step) — **P_deflated = 0.45**, under the 0.50 novel-synthesis cap so the cap is not
separately binding. Confidence in the underlying BRAIN-MECHANISM claims (hub-and-spoke, graded amodal
convergence, feature-correlation metric) is HIGH (0.7-0.75), strengthened this session by the directly-fetched
Cox et al. 2024 vATL finding. Confidence in the corpus-scale-vs-architecture diagnosis (Section 3) is MEDIUM
(0.5, per the grounding sub-agent's own explicit calibration: "P(architecture-is-primary-bottleneck) ~0.55
before cap, capped at 0.50 as synthesis-not-direct-citation") — the controlled Levy-Goldberg ablation is solid
evidence for context-TYPE mattering, but no clean SimLex-999-specific corpus-size sweep was found, so "scale
alone would not have fixed it" remains an inference from adjacent evidence, not a single decisive citation.

---

## Cross-thread synthesis

This drill directly extends and corrects the deep VET's component #1 framing
(`notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md`, `notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`)
and the outcome-valence coverage wall's closing note
(`notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md`: "general synonym/hypernym resolution is
BLOCKED on the missing ATL learned lexical-semantic hub... a narrow supplied set closes the bank but not real
data"). Both correctly identified the GAP but had not (per this session's disk read) surfaced that a real,
partially-working, earned mechanism already exists and was landed 6+ weeks prior
(`notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` — the
original design doc that spec'd `hdlab/random_indexing.py` — and `data/exp_n11_random_indexing_semantic_v1/`,
the FULL run) — it was simply never wired or pushed past its first MIDDLE_BAND measurement. This is the same
"buried win" pattern independently diagnosed in
`notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md` for a different
(BGE-distillation) encoder track: **a real result sitting unfollowed-up because its cell's summary framing
(here: "MIDDLE_BAND... consider a lever") didn't get a dedicated re-drill.** That same note also independently
supplies a corpus-scale calibration point worth carrying forward: it characterizes the native RI/BEAGLE ceiling
as realistically ~0.65-0.75 on TOEFL-synonym-class tasks (not 0.85), consistent with this drill's own read that
architecture (context definition), not raw corpus size, is the more likely binding constraint at text8's
17M-token scale — text8 is not a small corpus by classical-distributional-semantics standards
(`notes/research_drill_teacher_free_semantic_bootstrapping_from_sparse_kb_2026-07-04.md` cites Antoniak &
Mimno 2018 / Wendlandt et al. 2018's ~100-400-occurrences-per-word-type stabilization floor for a DIFFERENT,
much sparser KG-derived corpus — text8's frequent words clear that floor by orders of magnitude, so the
MIDDLE_BAND plateau is unlikely to be a raw-count-starvation problem for common vocabulary, sharpening rather
than weakening the architecture-not-scale diagnosis above; caveat that this cross-corpus comparison is
suggestive, not a controlled ablation).

## Substrate-product implications

- **Immediate, cheap next move:** re-drill the ALREADY-EXISTING `random_indexing.py` + its FULL text8 result
  with the graded Tier1/Tier2/Tier3 probe in Section 4, BEFORE building anything new — this alone would
  either confirm or refute this drill's central diagnosis at near-zero cost (the harness, corpus, and encoder
  all already exist; only a new probe-pair set and a scoring pass are needed).
- **If the dependency-context increment (option b) HARD-PASSes:** the substrate gains a genuinely earned,
  glass-box, zero-shot graded lexical-similarity primitive — directly unblocking the outcome-valence coverage
  wall's general-synonymy tail (vessel~ferry) and providing a real (not hand-table) candidate default-sense
  signal for the still-open word-sense-selection frontier (`notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`).
  This would NOT by itself be "the ATL hub" — it earns the verbal/distributional spoke; multi-spoke
  (feature-grounded, experiential) integration remains the fuller, longer-term target already tracked under
  the 6yo-grounded-foundation program.
- **If it lands MIDDLE_BAND or fails:** it cheaply localizes whether the true bottleneck is context-window
  shape (this drill's bet) or something else (corpus scale, hyperparameters, or a genuinely harder
  representational problem) — either finding is directly actionable and both are far cheaper to have than not
  knowing, per the standing research discipline to drill every finding (including negatives) for mechanism.
- **Do not overclaim:** neither option (a) nor (b) alone closes the full ATL-hub gap (multimodal grounding);
  both are honest, partial, EARNED increments toward it, explicitly scoped as such.

## Citations (verified count)

**Disk-verified this session (13 artifacts, high confidence — read directly, not recalled):**
`hdlab/random_indexing.py` (full read); `hdlab/concept_encoder.py` (docstring + scope block);
`hdlab/composed_encoder_v3.py` (docstring); `hdlab/ppmi_sparse_encoder.py` (docstring);
`data/exp_n11_random_indexing_semantic_v1/metrics.json` (full run, all per-seed detail);
`experiments/exp_n11_random_indexing_semantic_v1.py` (probe-construction code, lines 42-158);
`notes/substrate_capability_map.md` (~lines 29605-29622, PPMI closure);
`notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` (original
design doc); `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md`;
`notes/research_drill_teacher_free_semantic_bootstrapping_from_sparse_kb_2026-07-04.md`;
`notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`; `notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md`;
`notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md`; `notes/PLAN_grounded_semantic_organ_build.md`.
`data/capability_registry.jsonl` grep (confirms zero registrations for these encoder modules).

**External/brain literature — 3 parallel Sonnet lit-scan sub-agents dispatched and returned this session
(generic-terms-only WebSearch/WebFetch per query-privacy discipline). Confidence flags are each sub-agent's
own self-report, carried through unchanged.**

*Directly fetched / high confidence (7):* Cox, Rogers, Shimotake, Kikuchi, Kunieda, Miyamoto, Takahashi,
Matsumoto, Ikeda & Lambon Ralph (2024), *Imaging Neuroscience* (PMC12224414) — vATL feature-norm RSA, full
text read; Hill, Reichart & Korhonen (2015), *Computational Linguistics* 41(4) — SimLex-999; Levy & Goldberg
(2014), ACL — dependency-based word embeddings; Schwartz, Reichart & Rappoport (2015), CoNLL — symmetric
pattern embeddings (SimLex-999 rho=0.517 vs skip-gram 0.462); Rubinstein, Levy, Schwartz & Rappoport (2015),
ACL — taxonomic-vs-attributive F1 diagnosis; Murphy, Talukdar & Mitchell (2012), COLING — NNSE non-negative
sparse embedding on PPMI; Faruqui, Dyer, Jauhar, Kumar, Dyer & Smith (2015), NAACL — retrofitting.

*Verified via search / secondary-source, not full-text fetched (12):* Rogers, Lambon Ralph, Garrard, Bozeat,
McClelland, Hodges & Patterson (2004), *Psychological Review* — hub-and-spoke PDP model (PDF parse failed);
Patterson, Nestor & Rogers (2007), *Nature Reviews Neuroscience* — hub-and-spoke review; Lambon Ralph,
Jefferies, Patterson & Rogers (2017), *Nature Reviews Neuroscience* — controlled semantic cognition framework
(fetch failed); Chen, Lambon Ralph & Rogers (2017), *Nature Human Behaviour* — deep connectivity-matched
model; Pobric, Jefferies & Lambon Ralph, two rTMS studies (PMC2730596; PubMed 20038436) — bilateral/transmodal
ATL disruption; Warrington (1975) — attribute-first semantic-dementia loss (via secondary citation); 2024
drawing-from-name SD study, *Memory & Cognition* (PubMed 38777996); Jefferies et al., Controlled Semantic
Cognition framework (PMC6006425, *Cerebral Cortex* 2023); Clarke & Tyler (2014), *J. Neurosci.* 34:4766 and
Erez, Cusack, Kendall & Barense (2018), *eLife* 31873 — perirhinal conjunctive coding; Andrews, Vigliocco &
Vinson (2009), *Psychological Review* — hybrid experiential+distributional; McRae, Cree, Seidenberg &
McNorgan (2005), *Behavior Research Methods* — feature-production norms; Landauer & Dumais (1997),
*Psychological Review* — LSA/TOEFL synonym test.

*Verified, narrower/exploratory relevance (6):* Bruni, Tran & Baroni (2014), *JAIR* — multimodal (image+text)
distributional semantics; Silberer & Lapata (2014), ACL — grounded autoencoder fusion; Xu & Tenenbaum (2007) —
Bayesian word learning, taxonomic-prior dependency; Barsalou (1999), *BBS* — Perceptual Symbol Systems; Lakoff
& Johnson — conceptual metaphor theory; comp-syn perceptually-grounded color embeddings (arXiv:2010.04292).

*Genuine gaps found, explicitly flagged (not evidence of absence):* no ATL-hub-specific study quantifying how
much cross-modal EXPERIENCE is needed before graded hub structure emerges (Section 1 LEARNING row, weakest-
evidenced question across all three scans); no direct SimLex-999-specific corpus-size sweep (same architecture,
only token count varied) found, so the corpus-scale-vs-architecture read (Section 3) is a calibrated inference
from adjacent evidence, not one decisive citation; no computational grounded/embodied model found evaluated at
open-vocabulary SimLex-999 scale (option (c)'s central uncertainty).

(Sahlgren 2005, Kanerva 1988, and Jones & Mewhort 2007 BEAGLE are already independently verified/cited in this
substrate's own prior research notes, listed above under disk-verified, and are not re-counted here.)

**Total citation count this note: 13 disk-verified + 25 external (7 directly fetched, 12 search-verified
secondary-source, 6 narrower-relevance) = 38, with 3 explicit literature gaps flagged rather than papered
over.**
