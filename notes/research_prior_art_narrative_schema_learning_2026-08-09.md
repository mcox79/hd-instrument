# Prior-art survey: learning narrative schemas/scripts/event knowledge from text (2026-08-09)

Build-on pillar of the grounded self-growing narrative-comprehension program. Method: 4 parallel
Sonnet lit-scan sub-agents (WebSearch/WebFetch, generic public academic terms only, no
substrate-novel names off-platform), each reading primary sources (ACL Anthology / AAAI proceedings
/ EMNLP / arXiv) directly rather than relying on secondary summaries where possible; findings
synthesized and cross-checked against this project's own on-disk organs
(`hdlab/event_bundle.py`, `hdlab/schema_exemplar_bayes.py`, `hdlab/learner`,
`hdlab/coreference_resolver.py`). All four lit-scans completed and are incorporated below — this
is a live-verified survey, not a from-memory draft. Prior work = LEARN-FROM + BUILD-ON + CREDIT,
never reinvent silently.

## HEADLINE

The field has a mature, LARGELY GLASS-BOX lineage for inducing event chains/schemas from raw text
via coreference + co-occurrence counting (Chambers & Jurafsky 2008/2009 and its direct
descendants through 2015) — fully adoptable, and it maps cleanly onto THREE organs we already own
on disk (`hdlab/event_bundle.py` FHRR role-slot event binding, `hdlab/schema_exemplar_bayes.py`
Bayesian schema routing, `hdlab/learner` MDL structure-selection). Separately, at least SEVEN
commonsense/eventuality knowledge graphs (ATOMIC, ATOMIC-2020's symbolic half, ConceptNet, GLUCOSE,
ASER, DeScript, CausalBank) are downloadable STATIC data, license-clear or research-use-clear,
ingestible with zero neural inference cost. Two genuine gaps were CONFIRMED BY LIVE SEARCH from two
independent sub-agents each (not just absence-of-memory): (1) no prior work does INCREMENTAL /
ONLINE / SELF-EXTENDING script or schema induction — every method surveyed, 2008 through the 2023
LLM-prompting era, is a single batch fit/construction pass, frozen after; (2) no prior work applies
VSA / HRR / TPR-style binding to script or narrative-schema representation specifically (the
closest analogues are generic sequence-permutation encoding and visual-scene resonator-network
binding, neither of which is narrative/event-schema work). Both gaps match, and now give live-search
confirmation to, the identical gap already flagged (independently, from the concept-grounding lane)
in `notes/research_script_half_synthesis_2026-08-09.md`.

## 1. ADOPTABLE / build-on subset (glass-box, no-LLM-at-inference-compatible)

### 1a. Chambers & Jurafsky narrative chains + schemas — the core lineage

**Chambers & Jurafsky 2008, "Unsupervised Learning of Narrative Event Chains" (ACL 2008, pp.
789-797).** Method: PMI between (verb, dependency-relation) event-slots sharing a coreferring
"protagonist" argument, computed from raw counts over Gigaword (1994-2004); a chain's score for a
candidate event = sum of pairwise PMIs (paper's Eq. 3); temporal order added via a separately
trained SVM (on TimeBank) predicting before/other between event pairs; discrete chains produced by
agglomerative clustering on PMI scores. Produces partially-ordered event chains anchored to one
shared participant (example: a "Prosecution Chain" arrest->charge->plead->convict->sentence).
Fully glass-box — every formula given, reimplementable, no learned opaque weights beyond a small
linear/SVM ordering classifier. Authors explicitly do NOT claim narrative cloze is solvable even by
humans, only that it is a comparative metric; discrete clustering mixes unrelated events under
data sparsity (e.g. an "Employment" chain absorbing obituary events because TimeBank lacks
obituaries); no participant-role typing until the 2009 follow-up; fully dependent on noisy
automatic parsing/coreference. **Maps onto our substrate**: reuse `hdlab/coreference_resolver.py`
(already WIRED, canonical) verbatim for protagonist-chain extraction — the SAME argument-tracking
job it already does for entity identity; store each chain-event as an `hdlab/event_bundle.py`
role-slot-bound vector (PRED+AGENT+PATIENT+TENSE, already built, byte-identical to the validated
`role_slot_summarizer` primitive); the PMI relatedness TABLE is a new, thin, purely symbolic count
structure computed OVER the chains — no new binding math needed, only a new counting/scoring layer
on organs we already have.

**Chambers & Jurafsky 2009, "Unsupervised Learning of Narrative Schemas and their Participants"
(ACL-IJCNLP 2009, pp. 602-610).** Extends chains to typed **narrative schemas**: the shared
argument is scored via a similarity function rewarding head-word/CBC-cluster overlap across the
WHOLE chain, not just pairwise PMI; schemas built by a greedy algorithm ("narsim", threshold beta)
merging verbs into existing chains or spawning new ones, reasoning jointly over all of a verb's
argument slots. Produces schemas = sets of typed chains with induced semantic-role-like participant
clusters (e.g. POLICE={police, agent, authorities} in a criminal-prosecution schema). Fully
glass-box (deterministic counts + head-word clustering + greedy PMI-weighted merging, no neural
components). Reported precision: only 67% of "misaligned" verb-to-frame mappings land in an
ADJACENT FrameNet frame; argument-role precision 72% (65% excluding Person/Org classes); authors
attribute most errors to parser/coref mistakes, not the induction algorithm. **Maps onto our
substrate**: this is the concrete missing "one level up" primitive — `event_bundle.py` already
binds ROLES within ONE event; a schema is a bundle of chains keyed by SCHEMA-ROLE (protagonist /
obstacle / instrument), structurally the SAME bind-then-bundle recipe one level higher
(bind(schema_role_key, chain_aggregate_vector), bundle across roles). Not yet built anywhere in
this project, but a direct structural extension of validated code — the concrete next-build target
in section 10.

### 1b. Statistical script learning — orthogonal refinements, same family

**Jans, Bethard, Vulic, Moens 2012, "Skip N-grams and Ranking Functions for Predicting Script
Events" (EACL 2012, pp. 336-344).** "Skip n-grams" here = literal k-skip bigram counting over
event sequences (0/1/2 intervening events allowed), NOT word2vec-style embedding skip-grams.
Compares three purely count-based ranking functions (C&J-style unordered PMI, an order-sensitive
PMI, and a bigram conditional-probability score) and introduces Recall@N as a more stable metric
than average-rank. Fully glass-box (count/probability-table arithmetic). Best configuration reaches
Recall@50 ~= 0.52 on Reuters — a real but modest absolute number, worth noting for calibration.
Trivial extension of the PMI table above (richer count structure, no new organ).

**Pichotta & Mooney 2014, "Statistical Script Learning with Multi-Argument Events" (EACL 2014,
pp. 220-229).** Extends chains to full relational events v(subject, object, prep-object); to avoid
needing exact-entity co-occurrence counts, entities are rewritten onto template variables
{x,y,z,Other} (their Algorithm 1) so evidence generalizes across specific entities; inference
maximizes summed log-probability over the generalized templates. Glass-box (smoothed count tables +
argmax). Best joint system: Recall@10=0.245, accuracy-with-partial-credit=0.549 — again modest,
and the entity-substitution scheme caps out around 3 shared entities per event pair. **Directly
validates our representation choice**: `event_bundle.py`'s PRED/AGENT/PATIENT/TENSE role-slot
vector is ALREADY multi-argument in exactly this sense — the FHRR binding already represents an
event as one joint multi-slot object, not a decomposed per-argument chain. The chain-level
PMI/count layer (1a) is the piece still missing on top.

**Pichotta & Mooney 2016, "Learning Statistical Scripts with LSTM Recurrent Neural Networks" (AAAI
2016, pp. 2800-2806).** Flattens documents into 5-component event-token sequences (verb, subject,
object, prep-object, preposition), trains a standard LSTM via next-step cross-entropy, beam search
(width 50) at inference — explicitly billed as "the first to apply LSTMs to script learning."
**Confirmed REFERENCE-ONLY**: nonlinear gating + dense learned embeddings, inference is beam search
over a trained network's softmax outputs, not hand-derivable arithmetic. Absolute cloze scores
remain low (best R25=0.152 entities / 0.061 nouns) — low enough that the authors themselves fall
back to a human 5-point Likert MTurk eval to get an interpretable number, because most obviously-
inferable facts are never explicitly stated in text and automatic cloze can't capture them. What IS
adoptable: the framing (event chain as sequence-prediction target) — we get this for free by
scoring next-event ranking through the PMI table / schema router instead of an LSTM.

**Rudinger, Rastogi, Ferraro, Van Durme 2015, "Script Induction as Language Modeling" (EMNLP 2015,
pp. 1681-1686).** Trains a Log-Bilinear (LBL) discriminative model — context/target vectors + bias,
next-event probability = softmax of a bilinear dot product over the previous N events, trained via
noise-contrastive estimation — against unigram/PMI/bigram baselines. Borderline glass-box: the
scoring function is a few closed-form equations (dot product + softmax, far simpler than an LSTM,
no gating), but the context/target vectors are themselves gradient-trained opaque parameters, so it
sits between pure-PMI glass-box and full black-box neural. **The paper's own explicit framing is
the field's central validity dilemma, worth stating precisely**: either discriminative LMs are
simply better at narrative cloze, OR narrative cloze is not a valid evaluation of genuine script
knowledge at all — the authors do not resolve which. Absolute performance stayed modest (avg
rank ~= 294, Recall@10 ~= 36.6%). This sets the bar our own cheap decisive test (section 6) must
clear: beat a frequency/count baseline by a REAL margin, not just beat chance.

**Frermann, Titov, Pinkal 2014, "A Hierarchical Bayesian Model for Unsupervised Induction of
Script Knowledge" (EACL 2014, pp. 49-57)** and **Orr, Tadepalli, Doppa, Fern, Dietterich 2014,
"Learning Scripts as Hidden Markov Models" (AAAI 2014).** Frermann et al.: a fully generative
Bayesian model over small CROWDSOURCED Event Sequence Descriptions (Regneri et al. 2010's corpus,
not raw newswire) — draws an event-type permutation from a Generalized Mallows Model (per-type
temporal-flexibility dispersion), event/participant optionality via Binomials, lexical realization
via Multinomials with a WordNet-informed asymmetric Dirichlet prior tying synonyms together;
inference via collapsed Gibbs + slice sampling. Every conditional distribution and update rule is
specified in closed form — fully glass-box. Honest finding worth preserving: performance is MIXED,
not uniformly better than the pipeline-based Regneri et al. 2010 baseline (paraphrase F1 ~=0.72 vs
~=0.69; ordering F1 ~=0.71 vs ~=0.78) — ablations show large drops on some scenarios without the
Generalized Mallows Model or the WordNet-informed prior, and the model relies on WordNet, so it
isn't purely corpus-unsupervised. Orr et al.: an HMM over "scene" states, fit via EM, glass-box in
the same sense. **Maps onto our substrate directly**: this is the concrete prior-art ANCESTOR for
the "MDL/Bayesian structural-form selection for scripts" gap already named in
`research_script_half_synthesis_2026-08-09.md` (which flagged Kemp & Tenenbaum 2008 as never
applied to scripts and named Orr et al. as the "closest" work — this drill confirms BOTH Orr et al.
and Frermann et al. are direct, adoptable generative-model ancestors, with Frermann et al.'s honest
mixed-result already a useful calibration data point). Adapt Frermann/Orr's generative structure
into `hdlab/learner`'s existing `hypothesis_space_spec` contract (declare "number of script
clusters / scene states" as a candidate hypothesis class; `mdl_select()` picks the compressing
structure; `per_cluster_gate()` already enforces the must-beat-null discipline) — reuses the SAME
MDL engine already wired for the condenser and rule-inducer.

**Balasubramanian, Soderland, Mausam, Etzioni 2013, "Generating Coherent Event Schemas at Scale"
(EMNLP 2013, pp. 1721-1731).** "Rel-grams": co-occurrence statistics over Open-IE triples
(extracted via OLLIE) with arguments mapped to 29 WordNet-derived semantic types; builds a
weighted "Rel-graph," generates schemas by seeding high-connectivity tuples and running
**Personalized PageRank** over the local subgraph (a standard, deterministic linear-algebra
iteration, no neural net), then merges arguments into "actors" via coreference/relation-sharing
heuristics. From 1.8M NYT articles: 320K tuples, 2K+ schemas released. Human eval: 92%
topic-coherent / 94% valid / 81% actor-coherent, a real improvement over Chambers' 82%/61%/59% —
though authors' own error analysis attributes 47% of invalid tuples to upstream Open-IE extraction
errors (n-ary relations truncated to binary). Fully glass-box. Secondary-priority adoptable recipe
for scale-up beyond DesireDB; maps onto extending `outcome_event_extraction.py` /
`parse_goal_extraction.py` plus a new PageRank-graph pass.

### 1c. Weber et al. tensor-based event composition — confirmed independent mathematical convergence

**Weber, Balasubramanian, Chambers 2018, "Event Representations with Tensor-Based Compositions"
(AAAI 2018, arXiv:1711.07611).** Two composition variants over predicate/subject/object embeddings:
a Predicate Tensor model (a genuine trilinear/3-way tensor contraction, generating a
predicate-specific tensor on the fly) and a Role-Factored Tensor model (two pairwise bilinear
contractions — predicate-with-subject, predicate-with-object — combined via learned linear role
maps, fewer parameters, generalizes to n-ary events). **This is now CONFIRMED, not merely
inferred, as the key finding for our mapping**: the composition operator, GIVEN trained parameters,
is a closed-form deterministic multilinear/bilinear algebraic function — no recurrence, no
attention, no gating — literally a polynomial sum-of-products over vector components that a human
auditor could write out and verify by hand for any input triple. This is the most glass-box-
reproducible of every neural method surveyed (more so than Modi & Titov's sigmoid-MLP composition,
far more than the LSTM). Reported numbers: Role-Factored model reaches 43.5% hard-similarity
accuracy vs 5.2% for plain additive averaging, and 72.1% vs 14.3% on Coherent MCNC (CMCNC, a
hand-curated harder eval variant they introduce because standard MCNC is "overly sensitive to
frequency cutoffs... and errors in preprocessing tools," citing Chambers 2017 below) — the largest
reported gap in this whole survey. Calibration-relevant honest finding: the MORE expressive
Predicate Tensor model actually UNDERPERFORMS the simpler Role-Factored model on cloze tasks — more
parameters did not monotonically help. **We do not need to adopt this paper's training procedure**
— the substrate already has the compressed FHRR equivalent (circular-convolution/bipolar binding)
at zero training cost. Cited here as independent literature confirmation that role-filler
tensor/convolution composition is a legitimate, strongly-validated way to represent events for
narrative prediction — `event_bundle.py`'s design is not a substrate-only idiosyncrasy, it is
mathematically convergent with a separately-motivated, empirically strong 2018 AAAI result. (A
2018 EMNLP follow-up by the same group, Weber/Shekhar/Balasubramanian/Chambers, "Hierarchical
Quantized Representations for Script Generation," swaps in a VQ-VAE-style discrete latent hierarchy
for script GENERATION — full neural encoder/decoder, reference-only, not adoptable.)

## 2. SUPPLIABLE DATA resources (glass-box grounding, live-verified)

| Resource | Contents / scale | Construction | Verdict |
|---|---|---|---|
| **ATOMIC** (Sap et al. 2019 AAAI) | 877,108 if-then triples, 309,515 nodes, 24,313 base events, 9 relation types (xIntent/xNeed/xAttr/xEffect/xWant/xReact + oEffect/oWant/oReact) | Crowdsourced (MTurk), base events mined from stories/books/Ngrams/Wiktionary idioms; 86.2% of annotations judged valid | **SUPPLIABLE** — plain triple-store lookup |
| **Event2Mind** (Rashkin et al. 2018 ACL) | ~25K events, 3 dimensions (intent, xReact, oReact); direct ATOMIC precursor | Crowdsourced | **SUPPLIABLE** but superseded in coverage by ATOMIC — low priority |
| **ATOMIC-2020** (Hwang et al. 2021 AAAI) | 1.33M tuples, 23 relation types across social-interaction / event-centered (Causes, HinderedBy, xReason, isAfter, isBefore, HasSubEvent, isFilledBy) / physical-entity groups | Crowdsourced extension of ATOMIC; symbolic graph and the neural COMET-2020 generator are architecturally SEPARABLE releases | **MIXED** — the 1.33M-tuple TSV (allenai.org/data/atomic-2020) is fully suppliable/glass-box on its own; COMET-2020 is reference-only, needed only for inference over events NOT already in the graph |
| **ConceptNet 5.5** (Speer, Chin, Havasi 2017 AAAI) | General multilingual graph, 34 relation types; event/causal-relevant subset: `Causes`, `HasSubevent`, `HasFirstSubevent`, `HasLastSubevent`, `HasPrerequisite`, `MotivatedByGoal`, `CausesDesire`, `ObstructedBy` | Merged expert (WordNet etc.) + crowdsourced (Open Mind Common Sense) + games-with-a-purpose | **SUPPLIABLE** — CC BY-SA 4.0, bulk TSV download; only ~25% overlap with ATOMIC's event coverage per the ATOMIC paper (largely complementary, not redundant). `cskg_foundation_v1` already ingests a ConceptNet-derived slice — verify coverage of the `HasSubevent`/`HasFirstSubevent`/`HasLastSubevent`/`MotivatedByGoal` relations specifically before re-drilling |
| **GLUCOSE** (Mostafazadeh et al. 2020 EMNLP) | ~670K specific causal statements + generalized inference rules across 10 causal dimensions, grounded in ROCStories 5-sentence narratives | Crowdsourced semi-structured elicitation (not automatic, not LLM-generated) | **SUPPLIABLE** — static (context, dimension, specific-statement, general-rule) tuples usable standalone; a separate GPT-2-based generalizer exists but the annotated data isn't gated behind it. Already flagged "on-point" for goal-outcome causal comprehension in the script-half note |
| **ASER** (Zhang, Liu, Pan, Song, Leung 2020, WWW/TheWebConf, arXiv:1905.00270) | ASER 1.0: 194M unique eventualities, 64M edges, 15 relation types (PDTB-style: Result, Reason, Condition, Contrast, etc.); later "core"/"full" releases scale to ~438M eventualities/648M edges | **Fully AUTOMATIC**: dependency-parse-pattern eventuality extraction + discourse-connective-pattern relation linking over 11B+ tokens (Yelp, Wikipedia, subtitles, news) — NO neural component in construction | **SUPPLIABLE, and the construction METHOD is itself glass-box-reimplementable** — MIT-licensed code + data on GitHub. Uniquely strong: if we ever want to BUILD a similar resource ourselves (not just ingest one), this pipeline needs no external LLM at any stage. Caveat: reflects text-stated causality (reporting bias ATOMIC's crowdsourcing was designed to avoid); edges are co-occurrence-weighted, individually noisier than ATOMIC's validated triples |
| **CausalBank** (Li, Ding, Liu 2020 IJCAI) | 314M (cause, effect) sentence-pair tuples (133M "because"-mode + 181M "therefore"-mode) | Fully automatic causal-connective template matching over 5.14TB preprocessed Common Crawl | **SUPPLIABLE** — GitHub release; precision bounded by explicit-connective coverage (misses implicit causality), but zero-cost to ingest at scale |
| **DeScript** (Wanzare, Zarcone, Thater, Pinkal 2016 LREC) + **Regneri/OMICS-family crowdsourced scripts** | DeScript: 40 scenarios x ~100 Event Sequence Descriptions each (~4,000 ESDs), plus partial alignments; Regneri et al. 2010 (ACL, "Learning Script Knowledge with Web Experiments"): induces a Temporal Script Graph (DAG, partial order over paraphrase-clustered event types) from crowdsourced ESDs via **Multiple Sequence Alignment** (bioinformatics-derived, algorithmic not learned — fully glass-box); OMICS (Honda Research / MIT Open Mind Common Sense lineage, Gupta & Kochenderfer AAAI-04): ~175 household tasks, 14-122 crowdsourced narratives each, raw (no formal alignment step confirmed) | Crowdsourced web experiments + algorithmic alignment | **SUPPLIABLE** — small but extremely clean, human-curated Schank-style scripts; ideal as a hand-checkable seed set / eval fixture (SFB1102 Saarland hosting), not a coverage source at scale — crowdsourcing doesn't extend to open-domain the way corpus-mining does |

## 3. REFERENCE-ONLY LLM/neural work — not adoptable at inference, what to borrow instead

**COMET** (Bosselut et al. 2019 ACL) fine-tunes a GPT-family transformer on ATOMIC/ConceptNet seed
tuples to GENERATE novel if-then inferences at inference time. **Confirmed reference-only** — any
completion requires running the trained transformer; not a fixed lookup table. The paper's own
generated output was NOT found released as a standalone static dataset (confirmed absence, not
just unchecked).

**ATOMIC-10X / Symbolic Knowledge Distillation** (West, Bhagavatula, Hessel, Jiang, Hwang, Le Bras,
Lu, Welleck, Choi, NAACL 2022 / arXiv 2021) is the actual "generate-with-a-big-model-then-freeze-
into-a-static-graph" precedent: prompts GPT-3 across the ATOMIC relation schema, filters with a
trained critic, releases the FILTERED graph as static tuples (reported to exceed human-authored
ATOMIC on the studied inference types) plus a smaller reference-only distilled generator
(COMET-DISTILL). **MIXED verdict**: the frozen filtered ATOMIC-10X graph itself is suppliable
(glass-box lookup, GitHub: peterwestai2/symbolic-knowledge-distillation); the generation pipeline
and COMET-DISTILL remain neural/reference-only. Quality is bounded by GPT-3 + critic-filtering
fidelity, not human judgment, so treat as noisier than hand-crowdsourced ATOMIC.

**Li, Zhang, Wang, Huang, Cho, Ji, Han, Voss 2021 EMNLP, "The Future is not One-dimensional:
Complex Event Schema Induction by Graph Modeling for Event Prediction."** A graph neural network
over a Temporal Complex Event Schema (events + arguments + temporal/argument-relation edges),
moving beyond linear chains to graph-structured schemas; releases the ODiN schema corpus (6,399
documents) + code, beats human-authored schemas by >17.8% HITS@1 on future-event prediction. Not
LLM-based (GNN message-passing, still opaque/reference-only at inference), but the modern
non-LLM neural high-water mark, and its OUTPUT (schema graphs) is a static, released artifact
usable without rerunning the GNN — a suppliable-data candidate distinct from the induction
mechanism.

**LLM-prompted schema induction (2023-era)**: Li et al., "Open-Domain Hierarchical Event Schema
Induction by Incremental Prompting and Verification" (INCSCHEMA, ACL 2023, arXiv:2307.01972) and
Regan, Zhang et al., "Human-in-the-Loop Schema Induction" (ACL 2023 demo, arXiv:2302.13048) both
explicitly use an LLM (GPT-3/3.5) as the induction mechanism, the second adding an interactive
human-curation loop. **Confirmed reference-only** for the induction mechanism. What is
statically reusable: the released schema libraries (ODiN, RESIN-11 evaluation sets, the induced
schema graphs themselves) — these are static graph artifacts suppliable as fixed background
knowledge, treating the LLM's role as a one-time OFFLINE knowledge-compilation step whose output
FORMAT (typed event/argument graph) we can consume without ever invoking an LLM at our own
inference time. Note carefully: "INCSCHEMA" is incremental PROMPTING within constructing ONE
schema in a single pass, NOT incremental growth of a schema library across successive documents
over time — see section 5, this is the closest near-miss to our own novelty claim, and it still
misses it.

## 4. Eval methodology precedent + VSA/HRR/TPR-to-event-structure adjacency (both CONFIRMED live)

**Narrative Cloze** (Chambers & Jurafsky 2008): leave-one-event-out prediction within an induced
chain. **Multiple-Choice Narrative Cloze (MCNC)** (Granroth-Wilding & Clark 2016, AAAI, "What
Happens Next? Event Prediction Using a Compositional Neural Network Model"): the field-standard
hardened variant — true held-out event + randomly-sampled distractors from other documents, small
fixed-size pick. Model-agnostic protocol, directly adoptable regardless of what scores it (the
GW&C model itself is a trained compositional neural net, reference-only). **Confirmed, sharper
validity critique than initially cited**: Chambers 2017, "Behind the Scenes of an Evolving Event
Cloze Test" (LSDSem workshop, ACL Anthology W17-0905) directly argues automatic MCNC evaluation is
biased toward high-frequency, low-information events (a baseline that always predicts a frequent
verb like "said" is "an extremely strong baseline"), oversensitive to frequency cutoffs and NLP-
preprocessing errors, with distractor generation now fully automated rather than curated for
genuinely script-relevant events; proposes human-curated evaluation sets as a fix (Weber et al.
2018's CMCNC, section 1c, is exactly this fix in practice). Combined with Rudinger et al. 2015's
separate "either discriminative LMs are better, or the metric isn't valid" dilemma (section 1b),
this sets a hard bar: **any narrative-chain mechanism we build must beat a frequency baseline by a
real, pre-registered margin, and survive an order-scrambling control** — both already built into
section 7's HARD-PASS/HARD-FAIL bands below, now with two independent literature sources backing
the concern rather than one.

**VSA/HRR/TPR-to-event-structure adjacency — CONFIRMED NEGATIVE by two independent live searches**
(not an absence-of-memory claim; both sub-agents searched from multiple angles — direct
author/keyword search on Smolensky/Plate bibliographies, topic-adjacent surveys, and generic
"VSA+script/schema/narrative" phrasings — and found nothing). Smolensky 1990 ("Tensor Product
Variable Binding and the Representation of Symbolic Structures in Connectionist Systems,"
*Artificial Intelligence* 46(1-2)) is the direct mathematical ancestor of our binding primitive —
outer-product role/filler binding, summed across roles, unbound via inner product — but its own
worked examples are structured propositions/parse trees, not multi-event narrative chains, and no
follow-up applies it to scripts. Plate 1995 ("Holographic Reduced Representations," *IEEE Trans.
Neural Networks* 6(3):623-641) compresses this via circular convolution — the direct ancestor of
our FHRR bind/bundle math — with sequence-storage examples but again nothing script/narrative-
specific (confirmed via Plate's own publication list, d-reps.org — no title referencing script,
schema, or narrative). The two closest analogues found: (a) generic VSA/HDC permutation-based
sequence encoding (Kleyko et al.'s two-part ACM Computing Surveys HDC/VSA review) — a real, directly
adoptable mechanical building block for encoding a chain's TEMPORAL ORDER (permute a filler vector
by position before bundling, per Kanerva 2009, "Hyperdimensional Computing," *Cognitive
Computation* 1(2)) once individual events are already bound, complementary to the PMI relatedness
scoring (which supplies WHICH events belong together, not what ORDER); and (b) Chen et al. 2021
(PeerJ, "Learning to perform role-filler binding with schematic knowledge") — thematically the
closest title found, but on inspection uses RNNs with external memory (Fast Weights, Differentiable
Neural Computers), NOT VSA/HRR, for role-filler binding of schematic events — a false-positive on
title alone, genuinely not the same mechanism. A third near-analogue, Resonator Networks (Frady,
Kleyko, Sommer et al., arXiv:2208.12880 / *Nature Machine Intelligence* 2024), applies VSA-style
role-filler binding to VISUAL scene factorization (object-identity x position x pose), a close
structural cousin but not narrative/event work. **This confirmed negative means the schema-bundle
primitive named in section 1a is not merely a novel-for-us extension but genuinely novel-for-the-
field** — calibrated accordingly in section 9.

## 5. THE HONEST GAP — CONFIRMED by live search, our genuine novel-synthesis claim

Every method surveyed across BOTH lineages — classic statistical (Chambers & Jurafsky 2008/2009,
Jans 2012, Balasubramanian 2013, Pichotta & Mooney 2014/2016, Rudinger 2015, Frermann 2014, Orr
2014, Modi & Titov 2014, Peng & Roth 2016) and modern neural/LLM-based (Weber 2018 + its 2018 VQ-VAE
follow-up, GW&C 2016, COMET/ATOMIC-2020/ATOMIC-10X, Li et al. 2021 GNN schema induction, the 2023
LLM-prompted INCSCHEMA/Human-in-the-Loop lineage, SHIELD 2024) — is a **single batch fit/construction
pass over a fixed corpus, frozen after**. This is now a CONFIRMED negative from two independent live
searches, not an absence-of-memory claim: one sub-agent found only class-incremental EVENT-TYPE
DETECTION work (e.g. "Incremental Prompting: Episodic Memory Prompt for Lifelong Event Detection,"
arXiv:2204.07275) as the nearest hit — that is supervised classifier incremental learning over
event TYPES, not incremental accumulation of script/schema WORLD-KNOWLEDGE (event chains, typical
orderings) from a streaming corpus, a genuinely different problem. The other found INCSCHEMA's
"incremental prompting" is incremental PROMPTING STAGES within constructing ONE schema in a single
pass, not incremental growth of a schema LIBRARY across successive documents over time. **Neither
is our gap.** Combined with the section 4 VSA/HRR/TPR negative and this project's already-BUILT
acquisition/consolidation infrastructure (`hdlab/predictive_coding.py` novelty gate,
`hdlab/self_improving_loop.py` coherence-gated keep/revert, `hdlab/hippocampal_encoder.py` CLS
discrete-budget replay — all cataloged with real measured status, not aspirationally, in
`research_psych_acquisition_consolidation_loop_2026-08-09.md`), the genuinely novel combination
this program would build is: **glass-box PMI/count-based narrative-chain induction (Chambers &
Jurafsky family, well-precedented, modest-but-real absolute performance) + FHRR schema-bundle
representation (structurally novel one-level extension of an already-validated primitive,
mathematically convergent with Weber et al.'s independently-validated tensor composition) + MDL
structure selection over script form (Frermann/Orr-precedented math, newly wired through the owned
`hdlab/learner` engine) + periodic consolidation-gated growth (the acquisition-loop drill's
already-designed closed loop, reused one level up)** — run as a standing INCREMENTAL process, not a
one-shot fit. No cited work does all four; each piece individually has direct literature precedent
(nothing invented from nothing), only the COMBINATION and the online/incremental operating mode are
new. This keeps the novel-synthesis claim honest: a wiring/combination claim, not a
from-scratch-mechanism claim.

## 6. Cheap decisive test

Reuse `hdlab/coreference_resolver.py` to extract protagonist argument chains from a real DesireDB
(or ROCStories-scale) text slice; store each chain-event as an `hdlab/event_bundle.py` role-slot
vector; build a plain PMI relatedness table over the chains (Chambers & Jurafsky 2008's exact
formula, unmodified). Evaluate next-event prediction via an MCNC-style task (1 true held-out event
+ 4 random distractors from other chains/documents, 5-way pick) against TWO controls: (i) a
most-frequent-event FREQUENCY BASELINE (per Rudinger 2015 / Chambers 2017's validity concern — must
beat this, not merely beat chance), and (ii) a PAIRSCRAMBLE / scrambled-chain-order negative control
(per this project's standing pairscramble-must-collapse relation gate — if scrambling event order
within a chain doesn't hurt ranking accuracy, the mechanism isn't using order/relatedness, only
bag-of-event frequency).

## 7. Falsifiable predictions

**HARD-PASS** (both required):
- PMI-chain next-event ranking beats the frequency baseline by >= 10 percentage points MCNC
  accuracy on >= 100 held-out chains. (Calibration note: the literature's OWN absolute numbers are
  modest — Jans et al. Recall@50 ~=0.52, Pichotta & Mooney 2014 Recall@10=0.245, Rudinger et al.
  avg rank ~=294 — so a 10pp MARGIN over frequency, not a high absolute score, is the right bar.)
- Scrambled-chain-order control degrades ranking accuracy by a real margin (>= 8pp) relative to
  true-order chains — confirms genuine order/relatedness-sensitivity, satisfying the
  pairscramble-must-collapse gate.

**HARD-FAIL** (either triggers, subject to the mandatory harness pre-check below):
- PMI-chain accuracy is within 3pp of the frequency baseline on >= 100 held-out chains.
- Scrambled-order accuracy is statistically indistinguishable from true-order accuracy
  (order-blind mechanism).
- **Mandatory pre-check before accepting either as a negative** (per standing "flat result = broken
  experiment, not a ceiling" discipline): confirm protagonist argument-chain extraction actually
  fires on >= 50% of the eval-slice documents at a real (not degenerate) average chain length first
  — a flat result driven by near-empty chains (coreference/parse pipeline not firing on this
  register of text) is a harness bug, not a mechanism verdict.

## 8. Cross-thread synthesis

Extends `notes/research_script_half_synthesis_2026-08-09.md` (STATIC representation/relation side —
VerbNet end-state predicates, FrameNet Subframe/Precedes, ATOMIC-as-lookup, Kintsch construction-
integration settle mechanism, Schank/SAM/PAM/MOP lineage — named the self-extension + MDL-structure
gaps at a high level) with the LEARNING/INDUCTION side specifically: how the field extracts
scripts/chains/schemas FROM raw text, method-by-method, live-verified, with concrete owned-organ
mapping for each. The two notes are complementary: that note answers "what glass-box structure
already encodes goal<->outcome relations," this note answers "how would we grow our OWN schema
library from exposure, and what prior art gets us there, verified." Also cross-references
`notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`'s already-designed
propose/verify + periodic-consolidation closed loop (built for WORD/construction acquisition) as
the exact mechanism the section-5 "periodic consolidation-gated growth" leg of this program's novel
combination would reuse one level up, at SCHEMA/CHAIN granularity instead of lexical/construction
granularity — same engine, new content type, per the standing "comprehension is a growing library
of construction competencies" discipline.

## 9. Substrate-product implications

If the section 5 combination is built and clears the section 7 bands, the substrate gains a
narrative-schema library that GROWS from ordinary reading rather than requiring either (a)
hand-authored Schank-style scripts (expensive, doesn't scale past a curated scenario list) or (b)
an LLM-based induction pipeline at inference time (violates the glass-box/no-external-LLM
invariant, and is confirmed reference-only per section 3). Every piece of the mapped design — the
PMI table, the FHRR schema-bundle vectors, the MDL structure choice, the consolidation pass that
promotes a library entry to a banked schema — is independently inspectable: a user could ask "why
does the substrate believe event X follows event Y in this scenario" and get a traceable answer
(PMI count + source documents + which consolidation pass banked it), categorically unavailable from
any neural/LLM-based schema-induction alternative surveyed in section 3, including the modern GNN
and LLM-prompted lineages. This extends the same auditability differentiator already identified as
the substrate's defensible edge in the goal-achievement arc to the schema/script layer specifically.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

Verification status upgraded from the initial foreground draft: all 4 dispatched Sonnet lit-scans
completed and are incorporated above (live primary-source verification, not from-memory citation).
Remaining flagged uncertainties, now narrowed to specifics: exact ATOMIC license text
[UNVERIFIED]; Granroth-Wilding & Clark 2016's exact distractor-count parameter [UNVERIFIED, drawn
from secondary summary]; SMILE-as-a-standalone-corpus distinct from DeScript/Regneri
[UNVERIFIED — likely the shared Saarland project name, not an independent resource]. Standard
lit-scan calibration deflation still applies given this remains an uncharted-for-us regime (no
published work does our proposed combination). **P(the section 6 cheap decisive test clears its
section 7 HARD-PASS bands) = 0.42** — base rate: the direct ancestors (Chambers & Jurafsky 2008,
Jans et al. 2012) DO beat frequency-style baselines on their own corpora, but the field's own
absolute numbers are consistently modest (Recall@50~0.52, avg rank~294, Recall@10~0.245), and
Rudinger 2015 / Chambers 2017 both independently document that a nontrivial share of apparent gains
on this exact task type is frequency-bias rather than genuine structure — this tempers the naive
optimism the raw "beats baseline" framing would suggest, hence 0.42 rather than higher, on top of
deflation for untested generalization from Gigaword/NYT-scale news corpora to DesireDB-register
prose and for the added novel-synthesis step (routing PMI scores through `event_bundle.py` vector
storage, no direct precedent). **P(the full section 5 combination — chain induction + FHRR
schema-bundle + MDL structure selection + incremental consolidation — clears an end-to-end
novel-synthesis eval, once each piece independently clears) is capped at 0.50** per the mandatory
novel-synthesis cap; not further estimated numerically since no such eval is yet designed (a
downstream build decision, not part of this literature-survey deliverable).

## 10. Recommended next build (ranked; folded into this deliverable per no-routing-files discipline)

1. **Cheapest, highest-confidence-precedent**: build the PMI narrative-chain layer (section 1a) on
   the ALREADY-WIRED `coreference_resolver.py` + `event_bundle.py`, run the section 6 cheap decisive
   test on a real DesireDB slice. Zero new mechanism risk beyond wiring — every piece has a
   2008-2014-era direct literature ancestor with published numbers to compare against.
2. **Second, if (1) clears**: build the schema-bundle one-level extension (section 1a) —
   bind(schema_role_key, chain_vector), bundle across roles — the concrete, structurally-motivated
   new primitive, not yet built anywhere in this project or (per section 4's confirmed negative) the
   literature.
3. **Third**: wire Frermann/Orr-style script-structure selection through `hdlab/learner`'s existing
   `hypothesis_space_spec` contract (section 1b) to pick the number of scenario clusters /
   scene-states automatically, rather than hand-fixing it. Pre-register against Frermann et al.'s own
   honest mixed-result finding (not automatically better than a simpler pipeline) as the calibration
   anchor.
4. **Fourth, the actual novel-synthesis unification**: reuse the already-designed propose/verify +
   periodic-consolidation closed loop from `research_psych_acquisition_consolidation_loop_2026-08-09.md`
   at schema/chain granularity instead of lexical granularity — do NOT attempt before (1)-(3) each
   independently clear, same anti-confound discipline that note's own section 8 applies to its own
   two halves.
5. **Parallel, low-cost, any time**: ingest ConceptNet's `HasSubevent`/`HasFirstSubevent`/
   `HasLastSubevent`/`Causes`/`MotivatedByGoal` edges (verify current `cskg_foundation_v1` coverage
   first) and the GLUCOSE causal-statement dataset (~670K tuples) as static grounding data —
   independent of the chain-induction build, pure data-supply per the PIVOT discipline ("supplying
   DATA is fine"). ASER and CausalBank are lower-priority scale-up options if DesireDB-scale grounding
   proves insufficient.

## Citations (verified count = 4 completed live Sonnet lit-scans, primary-source-read where
reachable; ~45 distinct citations checked)

Chambers & Jurafsky 2008 ACL pp.789-797; Chambers & Jurafsky 2009 ACL-IJCNLP pp.602-610; Jans/
Bethard/Vulic/Moens 2012 EACL pp.336-344; Balasubramanian/Soderland/Mausam/Etzioni 2013 EMNLP
pp.1721-1731; Pichotta & Mooney 2014 EACL pp.220-229; Pichotta & Mooney 2016 AAAI pp.2800-2806;
Rudinger/Rastogi/Ferraro/Van Durme 2015 EMNLP pp.1681-1686; Frermann/Titov/Pinkal 2014 EACL
pp.49-57; Orr/Tadepalli/Doppa/Fern/Dietterich 2014 AAAI; Modi & Titov 2014 CoNLL (arXiv:1312.5198);
Peng & Roth 2016 ACL; Weber/Balasubramanian/Chambers 2018 AAAI (arXiv:1711.07611);
Weber/Shekhar/Balasubramanian/Chambers 2018 EMNLP (arXiv:1808.09542); Granroth-Wilding & Clark 2016
AAAI; Chambers 2017 LSDSem (ACL Anthology W17-0905); Sap et al. 2019 AAAI (ATOMIC); Rashkin et al.
2018 ACL (Event2Mind); Hwang et al. 2021 AAAI (ATOMIC-2020); Bosselut et al. 2019 ACL (COMET); West/
Bhagavatula/Hessel/Jiang/Hwang/Le Bras/Lu/Welleck/Choi 2022 NAACL (ATOMIC-10X / Symbolic Knowledge
Distillation); Speer/Chin/Havasi 2017 AAAI (ConceptNet 5.5); Mostafazadeh et al. 2020 EMNLP
(GLUCOSE); Zhang/Liu/Pan/Song/Leung 2020 WWW (ASER, arXiv:1905.00270); Li/Ding/Liu 2020 IJCAI
(CausalBank); Regneri/Koller/Pinkal 2010 ACL; Wanzare/Zarcone/Thater/Pinkal 2016 LREC (DeScript);
Gupta & Kochenderfer AAAI-04 (OMICS); Li/Zhang/Wang/Huang/Cho/Ji/Han/Voss 2021 EMNLP (ODiN complex
event schema); Li et al. 2023 ACL (INCSCHEMA, arXiv:2307.01972); Regan/Zhang et al. 2023 ACL demo
(Human-in-the-Loop Schema Induction, arXiv:2302.13048); Smolensky 1990 *Artificial Intelligence*
46(1-2) (TPR); Plate 1995 *IEEE Trans. Neural Networks* 6(3) (HRR); Kanerva 2009 *Cognitive
Computation* 1(2) (hyperdimensional computing); Kleyko et al. ACM Computing Surveys 2022 Parts I/II
(VSA/HDC survey); Chen et al. 2021 PeerJ (role-filler binding, RNN/DNC not VSA — near-miss,
confirmed not the same mechanism); Frady/Kleyko/Sommer et al. arXiv:2208.12880 / *Nature Machine
Intelligence* 2024 (resonator networks, visual not narrative).
