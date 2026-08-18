# WHAT CAN WE TEACH THIS THING WITH, THAT ISN'T CHEATING AND ISN'T AN LLM?

**Research drill, 2026-08-18, at HEAD `0f8a3254a`. LEADS WITH BIOLOGY, ENDS WITH AN ENUMERATION OF
WHAT IS ACTUALLY ON DISK. Authored no cell, ran no experiment, dispatched nobody.**

---

## 0. THE TRAP. READ THIS BEFORE ANY NUMBER IN THIS NOTE.

**The instrument we score on DEFINES ITS OWN ANSWER USING WORDNET.** Verified in the instrument
source this session, not taken on trust:

- `experiments/exp_dissociation_score_instrument_v1.py:304` `build_wordnet_synonym_candidates()`
  builds SET_P by walking `wn.synsets(w)` -- **SET_P IS WordNet synonymy** (with zero co-occurrence).
- The same file builds SET_S by taking high-co-occurrence pairs and then **EXCLUDING** WordNet
  synonyms and WordNet near-neighbours. Measured in the landed population diagnostics:
  `n_excluded_wn_exact_synonym = 36`, `n_excluded_wn_near_path_sim_ge_thresh = 839`.
  **So WordNet defines BOTH sides of the label, not just the positive side.**
- The known-answer arm IS WordNet path similarity, reading **0.9599 [0.9441, 0.9739]**.

**THEREFORE: ANY SUPERVISION SIGNAL DERIVED FROM WORDNET -- SYNONYMS, HYPERNYMS, GLOSSES, OR
ANYTHING COMPUTED FROM THEM -- TRAINS ON THE TEST.** A write rule supervised that way would score
high and mean nothing.

**And the fitted oracle at 0.8629 is EXACTLY THIS.** It is a logistic regression *fitted on the
WordNet labels*. It is a **CEILING DIAGNOSTIC** proving the information is extractable from the
counts. **IT IS NOT A CANDIDATE BUILD AND MUST NEVER BE DESCRIBED AS ONE.**

Every candidate below carries an explicit **CIRCULARITY VERDICT**. Anything that fails is marked
**CIRCULAR -- UNUSABLE AS SUPERVISION**, however well it would score.

**AND THE HONEST HEADLINE: MOST OF THE SIGNALS THAT LOOK LIKE SUPERVISION ARE CIRCULAR.** Every
resource on disk that says "these two words mean the same thing" is either WordNet, or contains
WordNet, or is a hand-curated synonym list built for the same purpose. That is the finding, and it
is not a disappointment -- it is what forces the answer to be a *structural* one rather than a
label-lookup one.

---

## 1. THE ANSWER IN PLAIN LANGUAGE (one paragraph; read this if you read nothing else)

We cannot teach the system with any list of synonyms, because every synonym list we own either IS
the answer sheet or was built from it. What we CAN teach it with is something a child gets and we
have not been using: **the grammatical job a word does in a sentence.** Two words that can replace
each other -- "network" and "web", "purpose" and "function" -- turn up as the *subject of the same
verbs* and the *object of the same verbs*, even when they never appear in the same sentence as each
other. Nothing in that observation consults a dictionary; it comes straight out of a parser reading
raw text. And we already have it: a file on disk, `data/selectional_preferences_v1/`, holds **41,529
verb-plus-role slots** ("use/OBJECT", "reach/SUBJECT") with the words that fill each one, extracted
by our own glass-box parser from plain Wikipedia text, **covering 90.0% of the 617 words the
instrument scores.** It contains no WordNet and no LLM. **The second thing we can teach it with is
being wrong about which word fills a slot** -- when the system expects one filler and gets another,
that mismatch is a learning signal computed against *other words in the same job*, not against the
word's own history. That distinction matters enormously, because the one prediction-error experiment
we ran and killed compared a word only to **itself**. The honest caveat, and it is a real one: our
whole "we need a teacher" diagnosis rests on experiments that ALL represented a word's context as an
**unordered bag of the words in its sentence**, which is the single most co-occurrence-flavoured
choice available -- so before we spend anything on teaching, we must check whether simply recording
*which job* each context word held is enough on its own.

---

## 2. THE CIRCULARITY AUDIT -- EVERY CANDIDATE, WITH ITS VERDICT

Provenance below was **measured off disk this session**, not recalled. Method is stated per row.

### 2.1 CIRCULAR -- UNUSABLE AS SUPERVISION

| candidate | how the circularity was measured | verdict |
|---|---|---|
| **WordNet synonymy / hypernymy / glosses** | The instrument's `build_wordnet_synonym_candidates()` IS this; known-answer arm IS WordNet path sim 0.9599 | **CIRCULAR. Total. Not usable at any strength.** |
| **The fitted PPMI+SVD oracle (0.9670 / 0.9606 / 0.8629)** | Fitted by `LogisticRegression` on the WordNet-derived P/S labels (`C1_FITTED_ORACLE` in `data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json`) | **CIRCULAR BY CONSTRUCTION. CEILING DIAGNOSTIC ONLY.** |
| **ConceptNet `/r/Synonym`** | Streamed all 34,074,917 rows of `data/conceptnet/conceptnet-assertions-5.7.0.csv.gz`; of 222,156 English-English Synonym edges, **88,524 are `/d/wordnet/3.1`** (40%); the rest are Wiktionary/dbpedia synonym lists | **CIRCULAR -- 40% literally WordNet, and the remaining 60% is the SAME CONSTRUCT (a curated synonym list). UNUSABLE.** |
| **ConceptNet `/r/SimilarTo`** | Same scan: 30,280 en-en edges, **21,244 `/d/wordnet/3.1`** (70%) | **CIRCULAR. UNUSABLE.** |
| **ConceptNet `/r/IsA`** | Same scan: 230,137 en-en edges, **74,802 `/d/wordnet/3.1`** (33%), plus 88,237 OpenCyc | **CIRCULAR IN PART, AND CONSTRUCT-ADJACENT THROUGHOUT (co-hyponymy under a shared parent is what SET_P mostly is). UNUSABLE.** |
| **ConceptNet `/r/MannerOf`, `/r/Entails`** | Same scan: MannerOf **12,702 of 12,715 = 99.9% `/d/wordnet/3.1`**; Entails **405 of 405 = 100%** | **CIRCULAR AT ORIGIN despite being labelled `CN` inside our CSKG artifact. See 2.3 -- this is why a source LABEL is not a provenance check.** |
| **WordNet gloss cache** (`data/wordnet_gloss_cache_v1.json`, 1.78 MB) and `data/wordnet_noun_semantics_kb_v1/v2` | Named WordNet on their face | **CIRCULAR. UNUSABLE.** |
| **Any pretrained embedding table** (`data/gensim_cache/` 3.1 GB: word2vec-google-news-300, glove-wiki-gigaword-300, fasttext-wiki-news; `data/gensim_cache_v2/` 1.7 GB) | Owner ruling + a prior cell measuring **0.4376 BPC attributable to Google-News knowledge** | **DISQUALIFIED AS A MEANING SOURCE by standing invariant, independently of circularity. Admissible ONLY as a ceiling reference.** |

### 2.2 CONSTRUCT-ADJACENT -- USABLE AS AN INDEPENDENT VALIDATOR, NOT AS SUPERVISION

| candidate | measured | verdict |
|---|---|---|
| **SimLex-999** (`data/encoder_eval_benchmarks/simlex999.txt`) | Columns read off disk: `word1 word2 POS SimLex999 conc(w1) conc(w2) concQ Assoc(USF) SimAssoc333 SD(SimLex)`. **573 of 999 pairs have BOTH members inside our 5,491 anchors; only 23 pairs touch the 617 eval words** -- i.e. nearly disjoint from the evaluation population. It carries a free-association column (`Assoc(USF)`) and an association flag, so it separates similarity from association **the same way our instrument does**, from human ratings rather than WordNet. | **STRONG SECOND INSTRUMENT.** Not supervision: it is the same construct as the test, so training on it is training on a different sample of the test. **PROVENANCE CAVEAT I COULD NOT CLOSE OFF DISK: I did not verify whether SimLex's pair-SELECTION consulted WordNet. Treat its WordNet-independence as UNVERIFIED until someone checks the source paper; use it as a secondary readout, never as a gate, until then.** |
| **SimVerb-3500** (`data/encoder_eval_benchmarks/`, with `PROVENANCE_simverb.md` on disk) | Present, not coverage-measured this session | Same class. Worth measuring; our eval population is 100% NOUNS (see 4.1), so a verb instrument is a generalisation check, not a substitute. |
| **WordSim-353** | Present (`wordsim353_combined.csv`) | Same class, and it conflates similarity with relatedness -- weaker than SimLex for our purpose. |

### 2.3 GENUINELY INDEPENDENT OF THE EVALUATION GOLD

These are the ones that survive. Each is independent because **nothing in its construction ever
asked whether two words mean the same thing.**

| candidate | what relation it encodes | independence evidence |
|---|---|---|
| **Typed verb-argument slots** (`data/selectional_preferences_v1/selectional_slots_v1.pkl`) | `(verb_lemma, ROLE) -> {filler: count}`, ROLE in {SUBJ, OBJ, IOBJ, obl:<prep>} | Extracted by our own perceptron parser from raw SimpleWiki text. **No lexical database anywhere in the pipeline.** Fully independent. |
| **Thematic event/verb-arg pairs** (`data/thematic_relations_v1/thematic_edges_v1.pkl`) | event co-occurrence + verb-argument pairs from the same corpus | Same pipeline, same independence. |
| **CSKG, WordNet-free subset** | AtLocation / CapableOf / UsedFor / LocatedNear / HasSubevent / ATOMIC social-inference / MayHaveProperty | **96.33% of edges carry no WordNet at any level of provenance** (measured in 2.4 below). The synonymy/taxonomy relation family was DROPPED at build time. |
| **CSKG Visual-Genome subset** | object relations derived from **images**, not text | Cross-modal by construction; no lexical resource involved. |
| **Human sensorimotor / affective / acquisition norms** (Lancaster, Brysbaert, Warriner, Kuperman AoA, Binder) | per-word experiential ratings on perceptual and action dimensions | Ratings collected from human participants asked how strongly they experience a word through each sense/effector. **Nothing in the rating task references synonymy.** Residual risk: the word LISTS were assembled from prior norm sets, provenance of list assembly unverified; the RATINGS are certainly independent. |
| **Our own corpus, re-represented** (dependency-typed contexts over the write rule's own 34,169 sentences) | context = (neighbour word, grammatical relation) rather than (neighbour word) | It is our own text. No external resource at all. |
| **Prediction error against another stream** | residual between an expectation and an observation | Computed from our own corpus. Independent -- but see section 3, the one we ran was a *self*-prediction and it is a measured null. |

### 2.4 THE CSKG CONTAMINATION CHECK -- ASKED PROPERLY, NOT ASSUMED

The brief said: *the CSKG is a merge of several sources and may CONTAIN WordNet -- check, do not
assume.* It does contain WordNet. Here is exactly how much, and there is a clean subset.

**Method:** streamed all 16 shards of `data/cskg_foundation_v1/edges_shard_*.jsonl` (1,213,912
edges) and cross-tabulated `relation` against the per-edge `source` field. Then, because a source
LABEL is not a provenance check, I re-derived the origin of the ConceptNet-labelled relations from
the raw `conceptnet-assertions-5.7.0.csv.gz` dump.

**Step 1 -- by the artifact's own source label:**

| source | edges | share |
|---|---|---|
| AT (ATOMIC) | 696,152 | 57.35% |
| VG (Visual Genome) | 257,130 | 21.18% |
| CN (ConceptNet) | 214,890 | 17.70% |
| WD (Wikidata) | 13,812 | 1.14% |
| FN (FrameNet) | 12,128 | 1.00% |
| **WN (WordNet)** | **11,903** | **0.98%** |
| **CN\|WN** | **7,897** | **0.65%** |

**WordNet-labelled = 19,800 edges = 1.63%.** And it is confined to exactly two relations:
`/r/PartOf` (11,260 WN + 7,897 CN|WN, of 29,577 total) and `/r/MadeOf` (643 of 2,517). **Every other
relation in the artifact is 0% WordNet-labelled.**

**Step 2 -- the label undercounts. Origin check against the raw ConceptNet dump** (34,074,917 rows
streamed):

| relation | en-en edges in raw ConceptNet | share from `/d/wordnet/3.1` |
|---|---|---|
| `/r/Entails` | 405 | **405 = 100%** |
| `/r/MannerOf` | 12,715 | **12,702 = 99.9%** |
| `/r/PartOf` | 13,077 | 9,066 = 69% |
| `/r/MadeOf` | 545 | 0% (all `/d/conceptnet/4/en`) |
| `/r/HasA` | 5,545 | 0% |

So CSKG's `CN`-labelled `/r/MannerOf` (12,068 edges) and `/r/Entails` (391 edges) are **WordNet
troponymy and WordNet verb entailment wearing a ConceptNet label.** This is a concrete instance of
the standing rule that a registry/label-first audit is structurally blind: the artifact's own
metadata says 1.63%, the origin check says ~2.9%.

**Step 3 -- the clean subset, and it is large.** Dropping the four contaminated relations entirely
(`/r/PartOf`, `/r/MadeOf`, `/r/MannerOf`, `/r/Entails`) plus every WN-labelled edge leaves
**1,169,359 of 1,213,912 edges = 96.33%, with zero WordNet at any level of provenance.**

**Step 4 -- and the most important part, which I nearly missed.** The CSKG build **already drops the
entire synonymy/taxonomy relation family.** From `experiments/exp_cskg_foundation_v1.py:45-47`:

> `# Locked from the FULL relation-column distribution (measured this session). DROP: RelatedTo, Synonym,`
> `# Antonym, FormOf, DerivedFrom, IsA, HasContext, EtymologicallyRelatedTo, SimilarTo, DistinctFrom,`
> `# DefinedAs, InstanceOf, fn:HasLexicalUnit, /r/dbpedia/*, EtymologicallyDerivedFrom, SymbolOf, mw:SameAs.`

and the cell carries a self-test (lines ~695-710) that feeds it a synthetic `/r/Synonym fire ->
blaze` edge and asserts `blaze` never becomes a node. **So the single most dangerous contamination
route into this asset was closed at build time and is regression-tested.** Credit where it is due:
whoever wrote that cell pre-empted this exact audit.

**VERDICT ON THE CSKG: INDEPENDENT AND USABLE, at 96.33% of its edges, with the contaminated
portion precisely enumerable and droppable.**

---

## 3. BIOLOGY FIRST: WHAT ACTUALLY SUPERVISES THE CORTICAL SEMANTIC SYSTEM

The prior drill (`96caca8de`,
`notes/what_supervision_the_brain_has_that_we_do_not_error_driven_learning_drill_2026-08-18.md`,
56.0 KB, read in full this session) named four candidates -- prediction error, cross-modal
correspondence, consequences of use, replay -- each with a PINNED-vs-THEORY label and published
objections at full strength. **I do not repeat that work; I build on it and correct one of its
conclusions.** This section does the one thing it could not: take the measured null seriously and
decompose it.

### 3.1 THE MEASURED NULL, AND WHAT IT DOES AND DOES NOT RULE OUT

`exp_predictive_coding_write_gate_dissociation_v1` (`e822eeaaf`, FULL) swept a prediction-error write
gate. Gating harder raised AUC monotonically 0.0961 -> 0.1526 -> 0.2268 -> **0.3079** against
`A0_INCUMBENT` 0.0710 -- **+0.2369 [0.1921, 0.2831], CI-separated above.** Then `N1_RANDOM_GATE`
(same machinery, **same acceptance RATE**, fires at random) read **0.3007 [0.2546, 0.3485]**; paired
**P1 vs N1 = +0.0071 [-0.0565, +0.0703], NOT SEPARATED.** *Writing FEWER occurrences helps; selecting
the RIGHT ones does not.*

That is a clean, well-controlled negative and it must not be softened. **But it is a negative about
ONE SITE and ONE TARGET, not about the signal.** Three things get conflated whenever it is quoted as
"prediction error is dead":

**(a) THE SIGNAL -- is an error computed at all?** This is the part with pinned neural evidence
(mouse V1 L2/3 mismatch responses scaling linearly with error magnitude, opposing input signs,
emerging only after learning; human ECoG pre-onset predictive information; N400 graded by cloze) and
the part with live objections (a synaptic-depression account reproduces the mismatch negativity; a
9-lab N=334 pre-registered replication failed on the article-elicited N400 while replicating the noun
effect). **Our cell did not test this at all.** It did verify the signal was healthy: over 33,907
occurrences the residual had mean 0.4497, spread 0.1595, and the pre-registered degeneracy test did
NOT fire. So the null is about the mechanism, not a broken signal -- which the cell stated correctly.

**(b) THE SITE -- where does the error act? This is where our implementation diverges from the
biology, and it is the most important correction in this note.** We implemented the error as a
**BINARY GATE ON WHETHER TO WRITE AT ALL.** The brain does not do that. The best-supported cortical
plasticity form is the **three-factor / neo-Hebbian rule**: pre- and post-synaptic co-activation sets
an **eligibility trace** -- a flag at the synapse -- and a **third factor** (a phasic neuromodulator
carrying reward, surprise or novelty) arriving later **multiplies** that flag, setting the **sign and
magnitude** of the change. The write is never *skipped*; it is *scaled*, and it can be scaled
negative. Support for eligibility traces on behavioural timescales is now direct, including in
cortical layer 2/3 pyramidal cells under delayed neuromodulator application.

**Why this is operational rather than philosophical.** The 6.21 null fired because `N1_RANDOM_GATE`
matched the **acceptance rate**: the whole measured gain was writing less. **A signed multiplicative
rule writes EVERY occurrence.** Its token count is identical to the incumbent's **by construction**,
so the failure mode that produced the null *cannot occur* -- and the identity-matched control becomes
trivially available instead of hard to design. **A rate-matched control is only informative against a
rule that changes the rate; against a rule that fixes the rate at 100%, the correct mandatory control
is a magnitude-permuted twin.**

**(c) THE TARGET -- what is the error computed AGAINST?** Ours compared each occurrence to **the
word's OWN running accumulator**. That is a self-prediction: the word is asked to predict itself, and
the residual measures only how unusual this occurrence is *for that word*. Nothing in that comparison
can discover that two words which never co-occur belong together, because the two accumulators never
meet. The brain's error signals are computed against **something else**: another modality's
expectation of the same referent, a downstream consequence, or **the population of other items that
occupy the same role**. Every one of those is a comparison *across items*. Ours was not.

**WHAT IS RULED OUT:** prediction error, computed against a word's own history, applied as a binary
admit/reject gate on writes, on this corpus, on this instrument -- dead, CI-separated null against a
rate-matched twin. **WHAT IS NOT RULED OUT:** an error computed against another stream, applied as a
signed multiplicative modulation of a write that always happens. *That is not a rescue narrative. It
is a different site and a different target, and it arrives with a control that is stronger than the
one that killed the first version, not weaker.*

### 3.2 CROSS-MODAL CORRESPONDENCE -- THE PRIOR DRILL SAID WE DO NOT HAVE IT. MEASURED, THAT IS WRONG.

The prior drill rated the transmodal hub the strongest signal in principle (PINNED: semantic
dementia's cross-modal, category-general impairment; causal inhibitory rTMS over ATL; ATL damage
impairing *acquisition* of new concepts) then concluded *"Do not build the substitutability fix on
this signal now; name it as the ceiling case and move on"*, on the grounds that we lack grounded data.

**Measured off disk this session, that premise does not hold.** We hold:

- **Lancaster sensorimotor norms**, 39,707 words x 11 perceptual/action dimensions -- **80.5% of the
  5,491 anchors, 90.3% of the 617 eval words.**
- **Brysbaert concreteness** 80.7% / 90.4%. **Kuperman AoA** 80.8% / 92.7%. **Warriner VAD** 64.2% /
  82.8%.
- **CSKG Visual-Genome subset**, 257,130 relations derived from **images** -- 36.0% / 57.9%.

The literature has already built the object this would supervise toward: a **sensorimotor distance**
measure over the 11 Lancaster dimensions, explicitly positioned against WordNet-derived and
corpus-derived similarity, reported as comparably explanatory, capturing variance those measures
miss, and effective for abstract as well as concrete concepts.

**The limits, stated honestly, are severe.** (i) **11 dimensions cannot separate 5,491 words**; as a
supervision *target* for a 21,576-column reweighting it is a brutal bottleneck. (ii) There is a
specific reason to expect it may not discriminate *here*: SET_S pairs are high-co-occurrence same-POS
nouns from shared domains ("calcium/carbonate", "connective/tissue") and will tend to share a
sensorimotor profile much as SET_P pairs do. **A low-dimensional rating score is at real risk of
behaving like the constant/prototype floor -- which reads 0.5431, the STRONGEST of our four floors.**
(iii) Binder's 65 dimensions would discriminate far better but covers **5.0% of anchors / 9.2% of the
eval words** -- unusable at this population size. (iv) "The hub is trained BY cross-modal error"
remains **THEORY** (the Rogers/McClelland PDP account); the hub's existence and causal necessity is
what is pinned.

**CORRECTION, plainly: cross-modal grounding data is NOT unavailable to us. It is on disk at 90.3%
coverage of the scored population. What is genuinely uncertain is whether 11 dimensions carry enough
resolution -- and that is a measurable question, not a reason to skip it.**

### 3.3 THE DEVELOPMENTAL FACT THAT IS DIRECTLY ABOUT OUR METRIC

Children's word associations undergo a **syntagmatic-to-paradigmatic shift** at roughly ages six to
nine: early associations are co-occurrence-based ("dog" -> "barks"), later ones category- and
substitutability-based ("dog" -> "cat"). **That is our instrument's axis, in a developing brain.**
Early networks are described as shaped by experiential co-occurrence, with paradigmatic organisation
emerging as lexical knowledge consolidates.

**Two readings, and I flag which is which.** Supporting the build: the shift is a *change in what
gets recorded*, arriving after a long co-occurrence-dominated period -- exactly our position (AUC
0.0710, deeply syntagmatic). **The competing reading, which is the falsifier the prior drill correctly
nominated:** a substantial literature attributes the shift to **reading acquisition**, i.e. to
literacy instruction rather than accumulated predictive experience. If that is the causal story then
the shift is driven by an external teaching signal our system is equally entitled to, and "the brain
gets there unsupervised" is wrong. **I could not resolve this from a scan and will not pretend
otherwise; the literature is divided. It is one of the two named shelve conditions in section 7.**

### 3.4 THE MECHANISM THE BIOLOGY POINTS AT, NAMED PRECISELY

Putting (a), (b), (c) together with the developmental fact and the discriminative-learning tradition:

> **A CUE-COMPETITION RULE OVER GRAMMATICAL ROLES.** The cue is a *slot* -- a verb plus a grammatical
> role: `use/OBJ`, `reach/SUBJ`. The outcome is the *filler* that actually turns up. The system holds
> an expectation over fillers for each slot; when a filler arrives, the residual between expectation
> and observation is applied as a **signed, multiplicative** update to filler representations --
> strengthening the observed one and **DISCOUNTING the ones already predicted.** That discounting is
> **blocking**, and blocking is the one part of this picture that is causally pinned rather than
> inferred: optogenetic dopamine activation at reward delivery causes *unblocking*, letting a
> normally-blocked cue acquire value.

Why this produces substitutability specifically, and it is not hand-waving: **two words that fill the
same slots compete for the same outcome, so the rule moves them together WITHOUT THEIR EVER
CO-OCCURRING** -- which is exactly SET_P, where co-occurrence is zero by construction. And the
discounting term is the direct antidote to the failure our AUC records: the collocate that always
turns up beside a word is precisely the cue that gets *discounted* once already predicted. The
discriminative-learning line puts it sharply: contiguity / simple co-occurrence is "neither sufficient
nor necessary"; what matters is how much uncertainty a cue removes.

**PINNED vs OUR-INVENTION, per element, as the standing rule requires:**

| element | status |
|---|---|
| an error-like comparison is computed in cortex during language | **PINNED** (mouse V1 mismatch units; human ECoG pre-onset predictive information; N400/cloze) -- with the adaptation account and the failed 9-lab article-N400 replication as live objections |
| cue competition / blocking, discounting already-predicted cues | **PINNED CAUSALLY** (optogenetic unblocking) -- in the reward domain, not the linguistic one |
| the write is a *scaled* eligibility trace, not an admit/reject gate | **PINNED** as the general cortical plasticity form (three-factor neo-Hebbian rules; eligibility traces on behavioural timescales in cortical L2/3) |
| language cortex is sensitive to dependency structure beyond linear word order | **PINNED** (left anterior temporal pole and left IFG favouring dependency structures, left posterior STG favouring phrase structures; neural signals modulated by hierarchical structure beyond linear encodings; dependency-length effects across the fronto-temporo-parietal language network) |
| **that the semantic write rule is INDEXED BY GRAMMATICAL ROLE** | **OUR INVENTION UNDER TEST.** No recording shows a cortical semantic code keyed by dependency label. Do not present this as brain-derived. |
| **that the specific algebra (a delta rule over slot-filler expectations) is the cortical one** | **OUR INVENTION UNDER TEST.** The Rao-Ballard/Friston laminar assignment is inferred from anatomy plus modelling, not recorded. |
| binding a filler to a role as a first-class stored object | **UNPINNED** -- and per the standing 08-16 finding, no recording shows neurons computing an algebraic binding over two full-rank vector codes. **Our core operation is our-invention-under-test, not biology.** |

**The frame this obeys.** The *computation* -- separating items by the company they keep in a
structured slot, with an error residual as the learning signal and a verifier that is not the
generator -- is derived from a problem we share with cortex, so we copy it. The *parameters* -- how
many roles, what learning rate, what decay -- come from constraints we do not share, so we **sweep**
them and never adopt a published value.

---

## 4. WHAT IS ACTUALLY ON DISK -- AND EXACTLY HOW I ENUMERATED IT

### 4.0 METHOD, STATED SO IT CAN BE CHECKED OR FAULTED

**I enumerated from the filesystem, then reconciled -- never the reverse.** The standing rule exists
because two audits on 2026-08-13 each missed a whole working subsystem by asking "does the registry
match disk?" instead of "what is on disk?", and **62 of 141 modules have no registry row at all.**

1. **`scratch/enumerate_data_assets_2026-08-18.py`** -- an `os.walk` over
   `D:/AI/hd-instrument/data`, sizing with `os.path.getsize` (apparent size; `du` is unreliable in
   this environment, reporting a 512 KB `st_blocks` floor per file, which once produced an estimate
   wrong by ~600x). **`data/foundation/` is PRUNED from the walk and was never opened.** Output:
   `scratch/data_asset_enumeration_2026-08-18.json`.
2. **`scratch/supervision_source_coverage_2026-08-18.py`** -- per-asset coverage against the two
   populations, both extracted from disk this session:
   - the **5,491 anchors** from `scratch/sparse_code_real_task/real_cache.npz["anchors"]`;
   - the **617 eval words** from `data/exp_dissociation_score_instrument_v1/units.jsonl`, unit key
     **`POPULATION|v1.7|full`**.
     **A trap I fell into and corrected, recorded because the next reader will hit it:** that file
     also holds superseded `v1.4` / `v1.5` / `v1.6` populations at 430 / 513 / 242 pairs. Taking the
     *largest* gives 513 pairs / 1,065 words -- **the wrong population.** Key on the version string
     explicitly, never on size.
3. **Provenance cross-checks by streaming the raw sources**: all 16 CSKG edge shards (1,213,912
   edges) and the full 34,074,917-row ConceptNet 5.7 assertions dump.
4. **`grep -r` over `tools/` and `experiments/` TIMED OUT REPEATEDLY** (5 min, twice), and the
   `Glob`/`Grep` tools both timed out at 20 s on this repo. I substituted a bounded `os.walk` +
   per-file read in Python, skipping files over 3 MB. **That is how the prior art in 4.4 was found. A
   search that times out is not an absence.**

**`director_kb_query.py` / `substrate_query.sh` were NOT used** -- documented STALE (ingest
livelock). I did not run them and am **not** reporting a timeout as "no prior work"; the enumeration
above is the substitute.

**`data/foundation/`** -- **EXISTS** (`ls -ld` returns a directory dated 2026-08-12). **Reported from
a parent-directory listing ONLY. NOT DESCENDED INTO, NOT OPENED, NOT SIZED.** It is READ-ONLY with no
backup and is excluded from every number below.

### 4.1 THE POPULATIONS, WITH A LIMIT NOBODY HAS BEEN FLAGGING

- **5,491 anchors**, zero missing from the count matrix.
- **242 SET_P pairs + 242 SET_S pairs; 617 distinct words** (336 in P, 351 in S, 70 shared).
- **The count matrix: 5,491 x 21,576, nnz 1,074,605, density 0.0091, 1,824,296 total tokens.**
- **EVERY MATCHED PAIR IS A NOUN.** Verified: the POS counter over both sets is `{'n': 242}`. The
  matching diagnostics show adjectives (346 P-candidates), verbs (1,697) and adverbs (115) **all
  dropped entirely at the caliper** for want of matchable SET_S partners. **Every Organ A number ever
  quoted is a NOUN number on 242 matched pairs.** It should not be generalised to the lexicon, and a
  successor instrument should be built to recover verbs.
- **The context definition, verified in source, and it is the load-bearing fact of section 5.3:**
  `exp_cue_information_audit_v1.raw_counts_for_window(sentence, target)` is
  `Counter(w for w in content_words(sentence) if normalize_lemma(w) != target_lemma)`. **The context
  is the WHOLE SENTENCE as an unordered bag of content words.** No window, no order, no position, no
  grammatical relation. The corpus is **34,169 sentences** cached in
  `scratch/cue_information_audit_v1/buckets_full.npz`.

### 4.2 THE SHAPE OF `data/`

`os.walk` visited **8,712 directories**. `data/` holds **9,958 top-level entries = 8,098 directories
+ 1,860 files**, of which **7,858 directories are `exp_*` result dumps** and **240 are everything
else**. **Total apparent size excluding `data/foundation/`: 157.6 GB**, with 1,360 files >= 5 MB. By
extension: `.pt` 79.7 GB (403 files), `.npz` 33.5 GB (1,457), `.ckpt` 13.0 GB (13), `.json` 7.5 GB
(34,475), `.npy` 6.7 GB (92), `.jsonl` 4.7 GB (1,724), `.txt` 1.9 GB (3,209).

**Reconciliation:** the standing accounting figure is "~26 GB of data assets ... the live path opens
~28 MB". Measured today `data/` is **157.6 GB**. That does not refute the accounting claim, which was
scoped to *assets* -- the bulk here is checkpoints and batch results (`lambda_batch_results` 36.4 GB,
`cell2_results` 20.6 GB, `substrate_director_kb_v1` 16.4 GB, `skypilot_results` 11.9 GB,
`llama_1b_results` 7.5 GB across 20,007 files). **But "~26 GB" should not be re-quoted as the size of
`data/`.**

### 4.3 THE KNOWLEDGE ASSETS, WITH RELATION TYPE, WORDNET INDEPENDENCE, AND MEASURED COVERAGE

Coverage columns: **A** = share of the 5,491 anchors; **E** = share of the 617 eval words. All
measured this session.

| asset (path under `data/`) | relation it encodes | WordNet-independent? | A | E |
|---|---|---|---|---|
| **`selectional_preferences_v1/selectional_slots_v1.pkl`** (14.7 MB) | **`(verb_lemma, ROLE) -> {filler: count}`**, ROLE in {SUBJ, OBJ, IOBJ, obl:*}. **41,529 slots, 14,669 distinct fillers, 944,990 slot observations** from 737,488 parsed SimpleWiki sentences | **YES, fully.** Parser output over raw text; no lexical database in the pipeline | **69.8%** | **90.0%** |
| **`thematic_relations_v1/thematic_edges_v1.pkl`** | event pairs (420,910 at count>=2) + verb-argument pairs (160,500), same corpus | **YES** | not measured | not measured |
| **`cskg_foundation_v1/`** (258 MB, 16 shards) | 33 relation types over 482,588 nodes / 1,213,912 edges: AtLocation, CapableOf, UsedFor, LocatedNear, HasSubevent, ATOMIC social inference, MayHaveProperty | **96.33% YES** (see 2.4); Synonym/IsA/SimilarTo family dropped at build and regression-tested | 77.9% all / **71.0% clean** | 95.5% all / **91.9% clean** |
| -- CSKG **Visual Genome** subset (257,130 edges) | object co-occurrence and properties from **images** -- the only cross-modal relation we own | **YES** | 36.0% | 57.9% |
| -- CSKG **ATOMIC** subset (696,152 edges) | if-then social/event inference about persons | **YES** | 34.0% | 49.4% |
| -- CSKG **FrameNet** subset (12,128 edges) | frame-element relations | **YES** | 3.2% | 5.8% |
| **`grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`** (17.2 MB) | 11 perceptual / action-effector strength dimensions per word | **YES** (human ratings; word-list assembly provenance unverified) | **80.5%** | **90.3%** |
| **`grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt`** | 1 concreteness dimension | **YES** | 80.7% | 90.4% |
| **`grounding_testbed/AoA_51715_words.csv`** (Kuperman) | age of acquisition | **YES** | 80.8% | 92.7% |
| **`grounding_testbed/Ratings_Warriner_et_al.csv`** | valence / arousal / dominance | **YES** | 64.2% | 82.8% |
| **`corpora/binder/binder2016_ratings.csv`** | **65** experiential dimensions -- by far the richest | **YES** | **5.0%** | **9.2%** -- too sparse to use |
| **`conceptnet/conceptnet-assertions-5.7.0.csv.gz`** (498 MB) | full ConceptNet 5.7 incl. Synonym / IsA / SimilarTo | **NO for the similarity relations** (2.1); usable only relation-by-relation | -- | -- |
| **`corpora/ud_english_ewt/`** (17 MB; 14,621 sentences, 229,711 tokens) | gold dependency parses -- **supplies the PARSER**, not per-anchor contexts | **YES** | 68.4% (lemma vocab) | 86.4% |
| **`corpora/simplewiki/simplewiki_clean_v1.txt`** (251 MB) | raw text | **YES** | -- | -- |
| **`corpora/textbook_*`** (6 OpenStax books) | raw text; **112,989 cleaned lines measured today** (documented figure 117,642 -- likely a line-vs-sentence difference; **do not quote 117,642 as verified**) | **YES** | -- | -- |
| **`corpora/mcguffey_graded/`, `mcguffey_readers/`** (3.6 + 2.2 MB) | graded readers, 7 levels | **YES** | -- | -- |
| **`corpora/breadth_v1/`, `litbank/`, `worldtree/`, `race/`, `onestop/`, Gutenberg texts** | raw / annotated text | **YES** | -- | -- |
| **`atomic_kb/`** (59 MB) | ATOMIC v4 source CSVs | **YES** | -- | -- |
| **`verbnet_affectedness_lexicon_v1_corrected/lexicon.json`** (2.3 MB) | VerbNet-derived affectedness | **YES of WordNet** (VerbNet is a separate resource) | -- | -- |
| **`encoder_eval_benchmarks/`** (SimLex-999, SimVerb-3500, WordSim-353) | human similarity ratings | **construct-adjacent** -- validators, not supervision (2.2). SimLex: **573/999 pairs inside the anchors, only 23 touching the eval 617** | 13.1% | 20.7% |
| **`wordnet_gloss_cache_v1.json`, `wordnet_noun_semantics_kb_v1/v2`** | WordNet | **NO -- CIRCULAR** | -- | -- |
| **`gensim_cache/`, `gensim_cache_v2/`** (4.8 GB: word2vec-google-news-300, glove-wiki-gigaword-300, fasttext) | pretrained embeddings | **DISQUALIFIED as a meaning source** by standing invariant; ceiling reference only | -- | -- |
| **`foundation/`** | **NOT OPENED. Existence reported from the parent listing only.** | unknown by design | -- | -- |

**CSKG usable-degree detail, because node presence is not the same as usable signal.** In the
WordNet-free subgraph, of the 617 eval words: **50 at degree 0, 102 at 1-4, 129 at 5-19, 336 at
>=20** (median 23). Across the 5,491 anchors the median degree is only **4**, with **1,592 at degree
0**. **And there is a coverage asymmetry that must be controlled: SET_P has 222/242 pairs with both
members present (149 at degree >=5); SET_S has only 199/242 (139 at >=5).** A score that is defined
more often for P than for S inflates a rank-sum AUC for reasons that have nothing to do with meaning.

**Selectional-slot usable-degree detail -- same caution, larger effect.** Median distinct slots per
covered eval word is **114** (per anchor: 35). **SET_P: 218/242 pairs with both members present, 196
with both at >=20 slots. SET_S: 185/242 present, 132 at >=20.** **This asymmetry is the single
biggest artifact risk in the build below and it is why that build carries a coverage-matched arm.**

### 4.4 THE PRIOR ART THAT MOST CONSTRAINS THIS -- AND IT IS A PRIOR NEGATIVE. DISCLOSE IT FIRST.

Found by the bounded `os.walk` of 4.0 step 4, not by a registry query.

**`experiments/selectional_preference_extractor_v1.py` already exists and produced the slot asset.**
It is not a thing to build -- it is a thing to REUSE, and its header already did the brain-fidelity
work: it names the brain structure (**verb-argument / thematic-role structure carried by posterior
middle temporal gyrus and ANGULAR GYRUS, dissociable from the anterior-temporal taxonomic hub --
PINNED via a lesion double dissociation and a pMTG-vs-AG TMS dissociation**); it names the pinned
developmental fact (**slot-filler organisation is prior to taxonomic organisation to ~7 years**,
which is section 3.3's shift seen from the other side); and it labels its own inventions (the slot
definition, the passive-alternation mapping, attaching the case preposition to obliques, the count
gates). It reuses `hdlab.pos_tagger`, `hdlab.arc_parser`, `hdlab.arc_labeler` and the definitional
graph's own `normalize_lemma`, **verified by runtime import rather than grep** -- those three
front-end modules are imported inside a function body in `hdlab/reading_grounding_loop.py` and are
invisible to static search. Three other cells consume it. It takes `corpus_bytes` / `max_sentences`,
so **it can be re-run on our own corpus.**

**AND THE PART THAT MUST NOT BE BURIED: this route has already been measured, and it FAILED.**
`data/exp_selectional_constraint_bridge_v1/metrics.json` (FULL):
**`SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR`**. It asked whether deriving a *held-out*
word's code from the selectional restrictions of the verbs it is an argument of beats copying a
co-occurring neighbour's code, on the identical stratum / scorer / n / pool / gold, against four
floors. It did not -- and MEMORY records it as **CI-separated BELOW neighbour-copying.** The cell was
well built: five `N1_NULL_SLOT_REWIRE` seeds, five `N2_NULL_RANDOM_TARGET` seeds, an oracle bridge,
an arms-must-differ gate passing on all 19 arms, and a mechanism-distinctness check showing the
selectional and neighbour-copy channels barely overlap (mean Jaccard **0.0133**; 38.6% of words with
**zero** source overlap) -- so the null is about the mechanism, not a degenerate duplicate.

**Why that null does not settle the question this drill asks -- stated precisely, not waved away.**
Per the standing rule that **no number crosses scorers or populations**:

| | the bridge cell (measured null) | the question here (un-measured) |
|---|---|---|
| task | **CONSTRUCT** a code for a word never stored, from its slots | **RE-REPRESENT** the contexts of words already stored |
| scorer | Spearman rho on pair similarity, **CI half-width ~0.1122** | rank-sum AUC vs 0.5, CI half-width ~0.02-0.05 |
| population | 337 bridged / 308 stratum (259 N, 27 V, 22 A) | 242 + 242 matched noun pairs, 617 words |
| floors | rho: orthographic 0.0503, frequency -0.00002, constant-prototype **-0.2253** | AUC: 0.5000 / 0.4901 / 0.4664 / **0.5431** |
| a hit would mean | inductive generalisation to unseen words | the store encodes substitutability rather than co-occurrence |

**These are different questions.** But the negative is real, it is on the same asset, and it deflates
the prior substantially -- carried through explicitly in 6.0. *The cell's own `HOW_TO_READ_A_NULL`
field puts it best: "A miss is a fact about OUR IMPLEMENTATION -- our slot definition, our estimator,
our target space -- and never about selectional bridging."*

---

## 5. THE RANKING -- FOUR AXES, EACH STATED SEPARATELY

### 5.1 THE TABLE

Axes: **(a) BRAIN FIDELITY** -- pinned neural evidence vs a cognitive-theory label; **(b)
INDEPENDENCE FROM THE EVAL GOLD**; **(c) COVERAGE** on 5,491 anchors / 617 eval words; **(d) SURVIVES
NO-LLM**.

| # | candidate supervision signal | (a) BRAIN FIDELITY | (b) INDEPENDENCE | (c) COVERAGE (A / E) | (d) NO-LLM |
|---|---|---|---|---|---|
| **1** | **Slot-filler cue competition** -- error computed against the *population of other fillers of the same (verb, ROLE) slot*, applied as a signed multiplicative update | **HIGH but MIXED.** PINNED: pMTG/angular-gyrus verb-argument structure dissociable from the taxonomic hub; blocking causally pinned (optogenetic unblocking); eligibility-trace three-factor form pinned in cortical L2/3; slot-filler organisation developmentally prior to taxonomic. **OUR INVENTION: that the semantic write is INDEXED BY ROLE, and the specific delta algebra.** | **FULL.** Parser over raw text; no lexical database anywhere | **69.8% / 90.0%**, median 114 slots per covered eval word. **Coverage ASYMMETRY P>S (218 vs 185 pairs) is the main hazard** | **YES.** Perceptron tagger + hashed perceptron parser + a delta rule. Read time is a table lookup |
| **2** | **Typed dependency contexts, UNSUPERVISED** -- context = (neighbour, relation) instead of (neighbour) | Same PINNED base as #1 for structure-sensitivity in language cortex; the *indexing* claim is ours | **FULL** -- our own corpus, re-represented | Whole corpus; parser UAS **0.7868** is the limiter | **YES** |
| **3** | **Cross-modal correspondence via sensorimotor norms** -- predict the 11-dim Lancaster profile from the count row; residual drives the write | **HIGH on the hub** (semantic dementia; causal rTMS; ATL damage impairs acquisition). **THEORY-ONLY that the hub is TRAINED BY cross-modal error** | **FULL** (human experiential ratings; list-assembly provenance unverified) | **80.5% / 90.3%** -- the best coverage of any candidate | **YES** |
| **4** | **CSKG WordNet-free relational neighbourhood** -- two words with similar relational neighbourhoods | **LOW-MEDIUM.** Relational/schema knowledge is real, but a crowd-sourced assertion graph is a cognitive-theory artifact, not a neural structure | **96.33% of edges** verified WordNet-free at origin | **71.0% / 91.9%**, but **median anchor degree 4; 1,592 anchors at degree 0**; P>S asymmetry again | **YES** |
| **5** | **Visual Genome image-derived relations** -- the only literally cross-modal data we own | Same hub evidence as #3, and this is the *right modality* rather than a rating proxy | **FULL** | **36.0% / 57.9%** -- covers barely half the eval words | **YES** |
| **6** | **Prediction error against a word's own accumulator, as a write gate** | Signal pinned; **SITE WRONG** (binary gate, not a scaled eligibility trace); **TARGET WRONG** (self-prediction) | FULL | full corpus | YES |
| **7** | **Consequences of use** (reward / task outcome) | **BEST-PINNED error signal in neuroscience** (causal optogenetic dopamine RPE) | FULL | **effectively zero** -- we have no task loop delivering outcomes over these 5,491 words | YES |
| **8** | **Replay / offline consolidation** | PINNED (sharp-wave-ripple suppression impairs consolidation; targeted memory reactivation aids vocabulary) | FULL | n/a | YES |
| **X** | **WordNet / ConceptNet-synonymy / the fitted oracle / pretrained tables** | -- | **ZERO or DISQUALIFIED** | -- | -- |

### 5.2 READING THE TABLE

- **#6 is measured dead in the configuration we ran** and its verdict does not transfer to a
  different site and target (3.1). It stays on the list as a *component*, not as a build.
- **#7 fails on COVERAGE, not on biology** -- it is the best-pinned signal in the whole list and we
  have nothing to apply it to. The prior drill's bandwidth objection (~85 verbatim repetitions needed
  for a scalar outcome to shape a high-dimensional geometry) stands. **Do not build it; do not
  dismiss it either -- it is what a task loop would unlock.**
- **#8 computes no error.** It re-supplies samples and multiplies whatever signal exists. **It is a
  force multiplier on #1 or #3, never a standalone answer.**
- **#4 and #5 are usable but thin.** #5 is the theoretically right modality with the wrong coverage;
  #4 has the coverage but a median anchor degree of 4, and its relations (AtLocation, UsedFor,
  ATOMIC social inference) are about *situations*, which is closer to the syntagmatic axis we are
  already saturated on than to the paradigmatic one we need.
- **#3 has the best coverage and the cleanest independence**, and its specific risk is named in 3.2:
  11 dimensions may behave like the constant/prototype floor, which at **0.5431** is the strongest
  floor we have.
- **#1 and #2 are the same machinery at two levels of ambition** -- #2 is the unsupervised
  representation change, #1 adds the learning signal on top of it. **They belong in one cell, with #2
  as #1's mandatory baseline.**

### 5.3 THE UN-RUN VARIABLE THAT SCOPES THE WHOLE "WE NEED SUPERVISION" CONCLUSION

**This is the part of the drill I did not expect to find and it changes the recommended order.**

Verified in source (4.1): every arm in Organ A -- the five write-rule steps, PPMI, PPMI+SVD at k in
{50,100,300,500}, second-order cosine, the tuned-count sweep T0-T4, and SGNS -- consumed contexts
built by `raw_counts_for_window`, i.e. **the whole sentence as an unordered bag of content words**.
That is the single most co-occurrence-flavoured context definition available. And the instrument
measures *exactly* the axis on which that choice is known to matter: the published result is that
**window/bag contexts yield broad TOPICAL similarity while dependency contexts yield FUNCTIONAL,
co-hyponym similarity** -- the difference between "Rome ~ ancient" and "Rome ~ Florence". **SET_P is
the second kind. SET_S is the first kind. Our AUC of 0.0710 is the textbook signature of a
bag-of-words context, measured on the instrument built to detect it.**

**A sharp observation about the falsifier we ran.** `exp_tuned_count_unsupervised_dissociation_v1`
was dispatched because Levy, Goldberg & Dagan showed a *tuned count* method matches SGNS. It was the
right instinct and it was executed well. **But those authors have a second paper, and it is the one
that speaks to our exact metric: dependency-based contexts, which separate functional from topical
similarity. We ran the hyperparameter paper as the falsifier and not the representation paper.**
Tuning moved us 0.0519 -> 0.1144; the representation was never varied.

**I nearly reported this as un-run and it is NOT. Correcting myself before asserting it.**
`exp_writerule_filter_superpose_gate_v1` (FULL, `34d3fdbab`, metrics re-read today) contains
`F3_SYNTACTIC_NEIGHBOURS_ONLY`: keep only tokens in a direct 1-hop dependency relation with the
target -- its syntactic head plus its direct dependents -- built with the same persisted UD
front-end. **It reads 0.4876, CI half-width 0.0114, i.e. [0.4762, 0.4990], CI-separated BELOW 0.5.**

**But look at what F3 actually varied, because this is the whole point.** F3 is a **FILTER**: it
changes *which* words get counted and **throws the dependency label away**. Its result sits exactly
where a narrow window sits -- `F4_W1` 0.4959, **F3 0.4876**, `F4_W2` 0.4731, `F4_W5` 0.4561 -- which
is what you expect from something that is, functionally, a tighter window. **The mechanism in the
dependency-context literature is not "restrict to syntactic neighbours." It is that the RELATION
LABEL BECOMES PART OF THE CONTEXT IDENTIFIER**: `scientist/nsubj` and `scientist/dobj` are two
*different* contexts. That labelling is the entire mechanism -- it is what makes "discovers" and
"finds" share contexts (both take `scientist` as subject) while "discovers" and "scientist" do not
(they occupy different slots). **Drop the label and you collapse straight back to co-occurrence
within a syntactic radius.**

**So the honest statement is narrower and better than the one I first drafted: syntactic
NEIGHBOURHOOD was tested and failed at 0.4876. TYPED context -- where the grammatical relation is
part of what gets stored -- has never been tested on this instrument.** F3's result *strengthens*
this reading rather than weakening it: restricting which words count moved the store toward chance,
consistent with the organ-level finding that interventions destroying information move toward 0.5. It
did not change what a context *is*.

**And note what changing the context type means structurally: a context stops being a WORD and
becomes a (WORD, ROLE) PAIR.** That is a binding, and it is the substrate's own core operation. It is
an ORGAN A **CODE**-step change, not another FILTER-step change -- which matters, because CODE has
been "exonerated twice", both times with the context type held fixed as a bag of words.

---

## 6. THE ONE TO BUILD, AND ITS CHEAPEST CAN-FAIL TEST

### 6.0 THE RECOMMENDATION, WITH ITS PRIOR STATED HONESTLY

> **BUILD ONE CELL: `exp_typed_role_context_write_rule_dissociation_v1`. It contains the unsupervised
> typed-context arm (the falsifier) and the supervised slot-competition arm (the supervision answer)
> in the same cell, on the same floors, because the first is the mandatory baseline for the second.**

**Why one cell and in this order.** The precedent is explicit and it was vindicated three weeks of
work ago: drill `96caca8de` demanded a falsifier of the unsupervised premise *before* any supervised
arm, the Director ran it (`120cfefae`), and it changed the headline. The same logic applies with more
force here, because this falsifier varies the **representation** rather than the hyperparameters.
**If typed contexts clear 0.5 unsupervised, then the missing ingredient was never a learning signal
and every supervised build would have been solving the wrong problem.**

**P estimates, deflated as the standing calibration rule requires** (lit-scan deflation 0.15-0.25;
novel synthesis capped at 0.50), and further deflated for the 4.4 prior negative and for F3:

| outcome | my estimate |
|---|---|
| typed contexts (unsupervised) CI-clear 0.5 above all four floors | **0.15** |
| typed contexts CI-separated above the label-permuted control but still below 0.5 | 0.35 |
| supervised slot-competition arm CI-clears 0.5 | **0.20** |
| the cell returns a clean, well-controlled negative that closes context-type as a variable | **0.45** |

**These are low, and I am not dressing them up.** The value here is not a high hit probability; it is
that **no outcome is uninformative** -- a clean negative closes the last un-varied dimension of Organ
A and makes the supervision conclusion enormously stronger than it is today, where it rests on arms
that all shared one context definition.

### 6.1 NON-NEGOTIABLE PRECONDITIONS

1. **LICENCE GATE.** Reproduce all 8 DSI regression checks at **delta 0.0000** and the `STREAM` gate
   (rebuild A0 from the cached occurrence stream; require `mean_cos = 1.000000`). **If any check
   misses, ABORT -- no number in the cell is readable.**
2. **REUSE, DO NOT FORK.** Front-end via `hdlab.pos_tagger` / `hdlab.arc_parser` /
   `hdlab.arc_labeler`; slot logic via `experiments/selectional_preference_extractor_v1.py`
   (`corpus_bytes` / `max_sentences` parameters); lemmatisation via
   `hdlab.reading_grounding_loop.normalize_lemma`. **Verify each by runtime import, not grep** -- the
   front-end modules are imported inside a function body and are invisible to static search.
   The learning rule expands **`hdlab/predictive_coding.py`** (WIRED, 15 consumers). **Do not touch
   `hdlab/learner/`** -- it is an MDL symbolic-hypothesis engine and cannot learn a real-valued
   matrix.
3. **NO HYPERPARAMETER MAY BE SELECTED ON THE 242 PAIRS.** 37.6% of pair-member words appear in more
   than one pair; anything tuned on this population becomes a second oracle. Fix a priori, or select
   on the word-disjoint held-out population the tuned-count cell already built (`n_pool_anchors_
   word_disjoint_from_eval = 4874`, 54 matched pairs).
4. **ONE VARIABLE.** The primary arm re-extracts typed contexts from **our own 34,169 sentences**, so
   the only thing changing versus `A0` is the context type. The 737,488-sentence SimpleWiki asset is
   a **separate SCALE arm** with its own bag-of-words twin at the same corpus, never a substitute.
5. **NO LLM anywhere; no pretrained table imported.** Assert both in `metrics.json` as the sibling
   cells do.

### 6.2 ARMS

**Reference (loaded from cache, not recomputed):** `A0_INCUMBENT` 0.0710; `K1_KNOWN_ANSWER`
(WordNet path sim) 0.9599 -- **calibration only, NEVER a training target**; `N0_RANDOM_VECTOR_STORE`
0.4862; and for context, `F3_SYNTACTIC_NEIGHBOURS_ONLY` 0.4876 and `F4_W1/W2/W5`
0.4959 / 0.4731 / 0.4561.

**Treatment:**

- **`U1_TYPED_CONTEXT`** -- context identifier = `(neighbour_lemma, relation, direction)` over 1-hop
  arcs; plain counts; cosine. **The falsifier.**
- **`U2_TYPED_PPMI_SVD`** -- U1 with the shift-tuned PPMI+SVD settings already selected on the
  word-disjoint held-out set (`k_shift=15, k=50, p=0.5`), carried over unchanged so no new tuning
  happens on the eval population.
- **`U3_ROLE_ONLY`** -- context = the relation label alone, neighbour identity discarded. A ceiling
  on how much the ~40-way role distribution can carry by itself. **If U3 is close to U1, the
  neighbour is doing nothing and U1 is a POS-profile in disguise.**
- **`S1_SLOT_COMPETITION`** -- the supervised arm. For each occurrence of word *w* in slot
  *(v, ROLE)*: form the slot's expectation over fillers, take the residual against the observed
  filler, and apply it as a **signed multiplicative** update -- reinforcing the observed filler and
  **discounting already-predicted ones**. **Every occurrence is written; only sign and magnitude
  vary. Token count is identical to `A0` by construction.**
- **`S2_SLOT_COMPETITION_REPLAY`** -- S1 with a second pass over the same occurrences (replay as a
  multiplier, per 5.2). Only run if S1 fires.
- **`X1_SENSORIMOTOR_ERROR`** -- the cross-modal arm: predict the 11-dim Lancaster profile from the
  count row; residual modulates the write. **Include it only if the cell has budget; it is candidate
  #3 and its floor risk is real. If omitted, say so; do not report it as untested-because-refuted.**

### 6.3 FLOORS, KNOWN-ANSWER, NULL, AND THE MANDATORY CONTROLS

**Four floors, RECOMPUTED on this population, never imported** (they will regression-match at delta
0.0 because the population is identical -- that match is the licence, not a substitute for
recomputing): `F_ORTHOGRAPHIC` 0.5000 (+/-0.0125), `F_FREQUENCY` 0.4901 (+/-0.0519), `F_SCRAMBLE`
0.4664 (+/-0.0515), `F_CONSTANT_PROTOTYPE` 0.5431 (+/-0.0516). **The gate is a CI-separated margin
over `max(all four)` = 0.5431, not over 0.5.** Report the CI half-width and the permutation-null p95
beside every margin, and state tie conventions both ways.

**MANDATORY CONTROLS. Four arms produced apparent CI-separated wins on 2026-08-17 that their own
controls destroyed. None of these is optional.**

| control | what it holds identical | what it destroys | what it decides |
|---|---|---|---|
| **`N1_LABEL_PERMUTED`** *(identity-matched -- THE decisive one for U1)* | same parses, same arcs, same neighbour identities, same token count, same context-vocabulary size, same label marginal | the correspondence between a neighbour and its role | **If U1 is not CI-separated ABOVE N1, the typing is not the variable and the direction is dead.** This is the direct descendant of `N1_RANDOM_GATE`. |
| **`N2_RANDOM_TYPING`** | vocabulary inflation and sparsity (each arc gets a uniformly random label from the same K) | all syntactic content | separates a real effect from the geometry change that typing causes by inflating the context space |
| **`N3_MAGNITUDE_PERMUTED`** *(identity-matched -- THE decisive one for S1)* | every update magnitude, the full magnitude distribution, and a 100% write rate | which occurrence gets which magnitude | **If S1 is not CI-separated ABOVE N3, the gain is the magnitude distribution, not the error.** Note a rate-matched control is *inapplicable* here -- S1 writes everything -- which is precisely why 6.21's failure mode cannot recur. |
| **`N4_UNTRAINED`** | architecture, dimensions, initialisation | all learning | **required per learned arm** -- a random-init arm BEAT the trained one on 2026-08-17 (`T5` 0.4417 vs its untrained control at exactly 0.5000) |
| **`N5_COVERAGE_MATCHED`** | restricts to pairs where both P and S members clear a pre-registered slot-degree threshold | the P>S coverage asymmetry (218 vs 185 pairs present; 196 vs 132 at >=20 slots) | **the biggest artifact risk in this cell.** Report both the full-population AUC and the coverage-matched AUC; if they disagree, the coverage-matched one is the result |
| **`N6_PARSE_NOISE`** | everything except arc correctness (corrupt x% of arcs, sweep x) | parse quality | bounds how much the parser's **UAS 0.7868** costs, so a null is not silently a parser artifact |

**Null arm:** permutation null over the P/S labels, `N_PERM >= 2000`, with p95 reported at this n.

**Second, independent instrument (secondary readout, not a gate):** SimLex-999, **573 of 999 pairs
inside the anchors and only 23 touching the eval 617** -- near-disjoint, human-rated, and it carries
its own association column so it separates similarity from relatedness the way our instrument does.
**Its WordNet-independence is UNVERIFIED (2.2); verify before it is ever load-bearing.**

### 6.4 PRE-REGISTERED STOP-IFS, EVALUATED IN THIS ORDER

1. **LICENCE fails** (any of the 8 checks off delta 0.0, or `STREAM` mean_cos < 1.000000) -> **ABORT.
   Report nothing else.**
2. **`U1` NOT CI-separated above `N1_LABEL_PERMUTED`** -> **the typing is not the variable.** Report
   the null, close context-type as an Organ A variable, and go to supervision with the prior in 6.0
   lowered further.
3. **`U1` ~ `U3_ROLE_ONLY`** -> U1 is a part-of-speech profile in disguise, not a lexical-context
   effect. Say so; do not report it as a context-type win.
4. **`U1` CI-separated above `N1` but still CI-separated BELOW `max(floors)` = 0.5431** -> typing
   helps and does not clear. **Report the margin; do NOT call it a win.** Proceed to `S1`.
5. **`S1` NOT CI-separated above `N3_MAGNITUDE_PERMUTED`** -> the error signal is not the variable at
   this site and target either. **That would be the second independent negative on prediction error
   and it should be treated as decisive for the signal, not just the site.**
6. **Full-population and `N5_COVERAGE_MATCHED` AUCs disagree by more than a CI width** -> the
   coverage-matched number is the result, and the difference is itself reportable as an artifact
   measurement.
7. **`N6_PARSE_NOISE` shows the metric is steeply sensitive to arc corruption** -> the binding
   constraint is parse quality (UAS 0.7868), not the mechanism. That is a different build (a better
   parser), and it should be named rather than absorbed.
8. **Any arm CI-clears 0.5431 above all four floors AND both its controls** -> **Organ A REOPENS.**
   The 6.23 closure would be scoped to bag-of-words contexts and must be re-worded, not quietly
   amended.

### 6.5 WHAT MAKES THIS CHEAP

The parser, the labeler, the tagger, the slot extractor, the instrument, the floors, the matched
population and the checkpoint machinery all exist and are landed. The new code is the context-key
construction (one function), the delta rule (an expansion of `hdlab/predictive_coding.py`), and the
six controls. The corpus is 34,169 sentences. **The extractor already parsed 737,488 sentences in
2,297 s, so our own corpus is a few minutes of parsing.** This is hours, not days -- and per the
standing rule, cheap is acceptable here because this probe is *measuring whether the current
direction's premise holds*, not *setting* the direction.

---

## 7. THE SHELVE CRITERION -- BRAIN-FRAMED, NEVER PERFORMANCE-FRAMED

**NO AUC SHELVES EITHER DIRECTION.** What would have to be true about the biology:

**SHELVE the role-indexed write rule (#1/#2) only if BOTH:**

1. The reported dependency-structure sensitivity in left anterior temporal pole, left IFG and left
   posterior STG is shown to reduce to **linear distance and working-memory load** rather than
   structural role -- i.e. the dependency-length effects are a memory confound and there is no
   role-specific coding; **AND**
2. The **slot-filler-before-taxonomic** developmental ordering (the pinned fact
   `selectional_preference_extractor_v1` builds on) fails to replicate, or is shown to be an artifact
   of the elicitation task rather than of how children's semantic memory is organised.

**SHELVE the cross-modal supervision route (#3/#5) only if BOTH:**

1. The transmodal hub's role in **acquiring** new conceptual knowledge is shown to be
   retrieval/selection rather than representation-formation -- i.e. ATL damage impairs *access*, not
   the *building* of the code; **AND**
2. Hub convergence is shown to be architecturally hardwired rather than experience-trained, so that
   cross-modal correspondence does not shape the semantic code at all.

**SHELVE THE WHOLE ERROR-DRIVEN PROGRAMME only if ALL THREE** (this is the prior drill's criterion,
which I adopt unchanged because it is correctly framed, plus one addition of my own):

1. The cortical **pre-onset predictive signal** fails replication; **AND**
2. Mismatch responses reduce to **synaptic depression / adaptation**; **AND**
3. **(my addition, from 3.3)** the children's **syntagmatic-to-paradigmatic shift** proves to be
   driven by **literacy instruction** rather than accumulated predictive experience. *If that third
   condition alone turns out true, it does not shelve the programme -- it INVERTS it: it would mean
   the brain gets there with an external teaching signal too, and our search for an unsupervised
   route is the thing that was mis-specified.* **That is the highest-value open literature question
   in this note and it is worth a dedicated drill.**

---

## 8. WHAT THIS DRILL DOES NOT LICENSE

- **It does not license quoting 0.8629 as a capability.** It is a fitted oracle on the WordNet
  labels -- a ceiling diagnostic. **Provenance caveat:** 0.8629 lives in the docstring of
  `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py` (measured 2026-08-18, deterministic given
  pinned seeds) and in `notes/corpus_capacity_ppmi_svd_ceiling_2026-08-18.md`. **It is NOT in the
  landed `metrics.json`, which still carries only 0.9670 / 0.9606.** Either amend the artifact or
  file a superseding note; the next reader will otherwise pick up the leaked pair-level figure.
- **It does not license calling the CSKG "WordNet-free".** 96.33% of its edges are. Name the
  fraction and the four excluded relations.
- **It does not license treating SimLex-999 as an independent gold.** Its construction provenance is
  unverified by me.
- **It does not license generalising any Organ A number beyond NOUNS.** All 242 matched pairs are
  nouns; verbs and adjectives were dropped at the caliper.
- **It does not overturn the 6.21 prediction-error null.** That null stands exactly as measured. What
  this note argues is that it was a null about a **binary gate** against a **self-prediction**, and
  it names the site and target the biology actually specifies.
- **It does not claim dependency contexts are brain-derived.** Language cortex's sensitivity to
  dependency structure is pinned; **that the semantic write rule is indexed by grammatical role is
  OUR INVENTION UNDER TEST** and must be labelled that way in the pre-registration.
- **It does not claim the recommended build will work.** My own estimate is **0.15** that the
  unsupervised arm clears, **0.20** for the supervised arm, and **0.45** that the most valuable
  outcome is a clean negative.
- **I did not run the substrate KB query** (documented stale) and I am not reporting that as an
  absence of prior work -- the disk enumeration is the substitute, and it found the prior art in 4.4
  that a KB query would normally have surfaced.

---

## 9. SOURCE POINTERS

**On disk (all read this session):** `experiments/exp_dissociation_score_instrument_v1.py`;
`experiments/exp_cue_information_audit_v1.py`; `experiments/exp_corpus_capacity_ppmi_svd_ceiling_v1.py`;
`experiments/exp_cskg_foundation_v1.py`; `experiments/selectional_preference_extractor_v1.py`;
`hdlab/arc_parser.py`; `hdlab/predictive_coding.py`;
`tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`;
`data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json`;
`data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json`;
`data/exp_writerule_filter_superpose_gate_v1/metrics.json`;
`data/exp_selectional_constraint_bridge_v1/metrics.json`;
`data/exp_depparse_hashed_cpu_v1/metrics.json`; `data/cskg_foundation_v1/`;
`data/selectional_preferences_v1/`; `data/grounding_testbed/`;
`notes/what_supervision_the_brain_has_that_we_do_not_error_driven_learning_drill_2026-08-18.md`;
`notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sections 6.15, 6.20-6.23.

**Scripts written by this drill.** Because this note cites them as the provenance of numbers, they
are **PROMOTED out of `scratch/` per the standing rule** (a durable file must not cite into a
directory that gets wiped):

- **`tools/audit_data_asset_enumeration.py`** -- `os.walk` over `data/`, pruning and never opening
  `data/foundation/`. Produces the 4.2 figures.
- **`tools/audit_supervision_source_coverage.py`** -- per-asset coverage against the 5,491 anchors
  and the 617 v1.7 eval words, plus the CSKG relation-x-source cross-tab. Produces the 4.3 table.

Their JSON outputs remain in `scratch/` as regenerable artifacts and are **not** cited as
provenance: `scratch/data_asset_enumeration_2026-08-18.json`,
`scratch/supervision_coverage_2026-08-18.json`,
`scratch/dsi_population_v17_full_2026-08-18.json`, `scratch/anchors_5491_2026-08-18.json`.
Re-run either script to regenerate.

**Literature consulted this session (generic-term web scan; lit-scan deflation applied):**
dependency-based vs window-based word embeddings and the functional/co-hyponym vs topical
distinction; neural evidence for syntactic dependency-structure sensitivity in language cortex
beyond linear word order (anterior temporal pole / IFG vs posterior STG; dependency-length effects);
the syntagmatic-to-paradigmatic shift in children and the competing reading-acquisition account;
three-factor neo-Hebbian learning rules, eligibility traces and neuromodulatory third factors in
cortical L2/3; Rescorla-Wagner discriminative learning and cue competition in the mental lexicon;
the Lancaster sensorimotor norms and the sensorimotor-distance grounded similarity measure.

**A deliberate omission, and it is deliberate:** I did **not** compute a diagnostic AUC for any
candidate signal on the 242 pairs, though I had every input loaded and it would have taken minutes.
**Peeking would convert every arm in section 6 into a second oracle** -- precisely the hazard the
37.6% word-overlap finding exposed. The pre-registration has to be written blind, and it is.
