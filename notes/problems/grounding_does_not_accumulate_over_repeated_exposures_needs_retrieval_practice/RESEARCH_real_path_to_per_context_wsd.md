# RESEARCH — The real (glass-box / static-asset) path to per-context word-sense discrimination

Drill date: 2026-09-01. Lead-with-biology literature scan for the SOLVER.
Purpose: **correct a likely-wrong conclusion.** The prior verdict "per-context sense discrimination is LLM-gated" came from a WEAK prototype and is not supported by the literature. The capability is neither LLM-gated nor even encoder-gated: a *pure graph algorithm with no neural forward pass at all* clears the dominant-sense baseline on standard WSD.

Sibling drills (do not duplicate): `RESEARCH_sense_selection_mechanism.md`, `RESEARCH_accumulation_and_cross_situational_learning.md`, `RESEARCH_toward_ceiling_sense_selection.md`, `RESEARCH_breakthrough_sense_grounding_from_limited_exposure.md`.

---

## 0. The error, stated precisely

The prototype tested two paths on gold WiC (balanced, floor 0.50, dominant-sense/MFS-agreement ≈ 0.59) and both sat AT the MFS baseline:

- **Path A (glass-box):** spaCy dependency parse → mean-GloVe of the target's syntactic dependents / context bag → cosine/logistic → **~0.53–0.60**.
- **Path B (off-the-shelf):** `all-MiniLM-L6-v2` frozen → crude subword mean-pool of the target token → cosine-threshold OR 2-feature logistic → **~0.56–0.60**.

Conclusion drawn: "it's LLM-gated." **This is a weak-impl failure being generalized to an impossibility claim** — exactly the failure mode MEMORY warns against ("a fair test of a WEAK impl proves THAT setup failed, not that the capability is impossible"). Two independent literature facts break the conclusion:

1. **Knowledge-based GRAPH WSD with NO neural network at inference already beats MFS** (UKB ~67, SyntagRank ~72 vs MFS 65.2 on all-words). These are pure graph-diffusion algorithms — no transformer, no encoder, no live LM.
2. **A frozen (non-fine-tuned) encoder done properly clears MFS on WiC by ~10 points** (BERT-large ~0.655; SenseBERT-large frozen 0.795; MirrorWiC 0.719 dev). The prototype's 0.58 is a *recipe* failure (sentence-optimized 6-layer distilled model, wrong pooling, wrong layer), not an encoder ceiling.

So the real question is not "do we need an LLM?" but **"which glass-box or offline-built static asset clears MFS while keeping inference LM-free?"** The answer is graph spreading-activation over WordNet, which is *also* the brain-faithful mechanism.

---

## 1. Knowledge-based / graph WSD — glass-box, no live LM at inference

All numbers are F1 on the **Raganato et al. 2017 unified all-words framework** (SE2/SE3/SE07/SE13/SE15 and their concatenation **ALL**). The canonical **MFS / WordNet-first-sense baseline on ALL = 65.2** (verified this drill against a 2023 comparison table). Balanced WiC floor is 0.50; the prototype's dominant-sense agreement ≈ 0.59.

| Method | Mechanism (inference-time) | ALL F1 | vs MFS 65.2 | Live LM at inference? |
|---|---|---|---|---|
| **MFS / WordNet S1** | pick sense #1 | **65.2** | — | No |
| **Lesk (original 1986)** | gloss–context word overlap | ~50s | below | No |
| **Adapted/Extended Lesk** (Banerjee & Pedersen 2003) | gloss overlap expanded over WordNet relations | ~58–64 | ≈/below | No |
| **Babelfy** (Moro, Raganato & Navigli 2014) | random-walk-with-restart + densest-subgraph over BabelNet | ~65–66 | ≈ MFS | No |
| **UKB ppr_w2w** (Agirre, López de Lacalle & Soroa 2014; "inadvertently SOTA" 2018) | **personalized PageRank over WordNet(+gloss edges)** | **~67–67.5** | **+2** | **No** |
| **SyntagRank / UKB+SyntagNet** (Scozzafava/Maru et al. 2019–2020) | personalized PageRank over WordNet **+ SyntagNet** syntagmatic edges | **~71–71.7** | **+6** | **No** |
| **SREF_kb** (Wang & Wang 2020) | 1-NN vs BERT-encoded gloss/synset-relation sense vectors + "try-again" re-rank | **72.7** (verified) | +7.5 | **YES** (encodes query with BERT) |

**Key reading:**
- **UKB and SyntagRank are pure graph algorithms.** Inference = build a WordNet graph, inject probability mass on the context words ("personalize" the restart vector), run PageRank power-iteration to convergence, read out the highest-scoring synset for each target token. **No neural network is touched at inference.** These are the methods that produce the "~0.68–0.72 KB-WSD-without-a-fine-tuned-LM" headline. This is the path the SOLVER never actually built — Path A used GloVe averaging, NOT graph diffusion.
- **THE SUB-OPTIMAL-USE TRAP (critical build detail).** The Agirre et al. 2018 paper title — *"UKB is inadvertently state-of-the-art"* — is literally about people running UKB with default settings and wrongly concluding graph-WSD is weak. Vanilla WordNet relations alone give UKB only ~58–62 (below MFS). To reach 67+, UKB **must** use: (a) the **gloss-disambiguation edges** ("WordNet++" / Princeton gloss-tagged relations), (b) the **`ppr_w2w`** variant (disambiguate every content word in the sentence jointly, read out each — not one word at a time), (c) damping ≈ 0.85. Miss any of these and you re-derive "graph WSD ≈ MFS" — the same false-negative the SOLVER just hit with GloVe. **This is the #1 way the rebuild could fail; pin these three settings.**
- **SREF_kb (72.7) is "knowledge-based" in the sense of "no sense-annotated training data," but its inference STILL encodes the query sentence with a live BERT** to get the target's contextual vector before the 1-NN lookup. So SREF_kb is NOT LM-free at inference. It is admissible only as an *offline foundation build*, not as the runtime — same caveat as the sense-embedding family (§2).

**Do these clear MFS on WiC specifically?** No paper I found reports UKB/SyntagRank *directly on WiC*. WiC is normally attacked by the "WSD both sentences, compare senses" protocol. The all-words evidence (UKB +2, SyntagRank +6 over MFS) says the graph methods have real per-context discrimination beyond dominant-sense; whether that converts to a WiC win depends on WordNet↔WiC inventory granularity (see §5 caveat). Honest expectation is stated in §5.

---

## 2. Sense embeddings as precomputed static assets — the admissible-foundation angle

| Method | Offline asset | Inference computation | ALL F1 | WiC | Live LM at inference? |
|---|---|---|---|---|---|
| **LMMS** (Loureiro & Jorge 2019) | sense vectors = averaged BERT contextual embeddings of SemCor instances + WordNet propagation | encode query with BERT → 1-NN vs sense vectors | ~75.4 | **0.677** (verified) | **YES** |
| **SensEmBERT** (Scarlini et al. 2020, AAAI) | BabelNet+Wikipedia sense vectors (nouns) | encode query with BERT → 1-NN | ~78 (nouns) | — | **YES** |
| **ARES** (Scarlini, Pasini & Navigli 2020) | semi-supervised contextualized sense vectors | encode query with BERT → 1-NN | ~77.9 | — | **YES** |
| **SREF_kb / SREF_sup** (Wang & Wang 2020) | gloss+synset-relation sense vectors (no labels for _kb) | encode query with BERT → 1-NN + try-again | 72.7 / ~77.8 | — | **YES** |

**The decisive finding for the project's invariant.** For every sense-embedding method, the *sense vectors* are static (built offline — admissible foundation), **but inference requires a live forward pass of BERT to encode the query context** before the nearest-sense lookup. Under the project invariant "NO external LLM at inference," the query encode is the disqualifier — it is a live LM forward pass. So:

- **The strongest method whose INFERENCE is a genuine static-lookup + graph/gloss computation (no live neural forward pass) is a GRAPH method: SyntagRank (~71.7) > UKB (~67).** Not a sense-embedding method.
- You *can* build LMMS/SREF-style sense vectors offline with the cached MiniLM/transformers (foundation-building is free), but you cannot use them at runtime without re-introducing a live encoder for the query. Building them buys nothing under the invariant unless the query encoder is also offline — which it can't be, because the query is novel at inference.

**Corollary:** the "~0.79 all-words" figures floating around (e.g. some SREF/ARES headlines) belong to methods that need a live encoder. The honest LM-free ceiling from the literature is **~72 (SyntagRank)**, not ~79.

---

## 3. Why the MiniLM prototype under-performed, and Path-B-done-properly

Path B is worth understanding even though it is **not admissible** (a frozen encoder is still a live LM at inference) — because its true strength is the evidence that the capability is not LLM-gated.

**Why `all-MiniLM-L6-v2` collapsed to MFS:**
1. **Sentence-optimized model = the wrong tool.** MiniLM sentence encoders are contrastively trained so that *mean-pooling* the tokens yields a good *sentence* vector. That objective actively **washes out per-token sense contrasts** — the individual token vectors are pushed toward a shared sentence centroid. Reading a single token's sense off a sentence-similarity model is fighting its training objective.
2. **6 layers, distilled.** Fine sense distinctions live in the *upper-middle* layers of a *large* model. A 6-layer distillation has little of that resolution.
3. **Last-layer only, crude mean-pool.** The last layer is the most task/objective-warped; single-layer readout throws away the layers that carry sense.

**Path B done properly → ~0.65–0.68 frozen (verified pieces):**
- **Model:** BERT-large (or RoBERTa-large), NOT a distilled sentence model.
- **Layers:** **average the last four layers** — verified optimal for BERT on WiC (single-layer and all-layer averaging are both worse; concatenating last-4 also works).
- **Subword pooling:** mean-pool (or first-token) the target's wordpieces.
- **Classifier:** a **cosine-threshold tuned on dev beats an MLP** on WiC's small data (verified). A tiny logistic on `[cos, |v1−v2|, v1·v2]` is comparable.
- **With gloss augmentation:** GlossBERT-style context+gloss cross-encoding pushes all-words ALL to **77.0** (verified: SE2 72.5 / SE3 77.7 / SE07 75.2 / SE13 76.1 / SE15 80.4) — but that is fine-tuned, not frozen.
- **Self-supervised elicitation without WiC labels:** MirrorWiC reaches **0.719 dev** by contrastively eliciting word-in-context reps from a frozen PLM.

**Takeaway:** a *frozen* encoder with the right recipe clears MFS by ~10 points on WiC. The prototype's 0.58 is a recipe artifact. **But this whole family needs a live encoder, so it is off-limits for runtime.** Its only role here is to falsify "LLM-gated" and to serve as an *offline* foundation builder if ever needed.

---

## 4. The brain mechanism (lead-with-biology) — and the PINNED bridge to a glass-box algorithm

**How does the brain select a sense in context without a transformer?**

- **Spreading activation over a semantic network** (Collins & Loftus 1975 — a PINNED account of semantic-memory access). Concepts are nodes; typed relations are edges; a cue injects activation at seed nodes and it diffuses through the network until it converges on the contextually supported concept. This is the classic ATL/temporal-lobe semantic-hub picture.
- **Settling into a sense attractor** (Rodd, Gaskell & Marslen-Wilson 2004; "Settling Into Semantic Space" 2020). Word-meaning access is a *dynamical settling* process: an ambiguous word starts in a blended state and recurrent dynamics settle it into one meaning's attractor basin, with the context biasing which basin. Ambiguity slows settling (the empirical ambiguity disadvantage).
- **Predictive-coding pre-activation** (Kuperberg): context pre-activates likely upcoming meanings — i.e., the context biases the starting activation *before* the target arrives.

**The bridge (verified this drill): personalized PageRank = random-walk-with-restart = the diffusion/random-walk formalization of spreading activation.** The literature states it directly: "the spreading-activation model is based on diffusion- or random-walk-like spreading"; "random-walk variants include random-walk-with-restart, also called personalized PageRank"; and PPR "propagates activation through a network to identify nodes associated with the provided cues." So:

- **Personalizing the PPR restart vector on the context words = the priming / predictive pre-activation** (Kuperberg / Collins-Loftus cue injection).
- **PageRank's power-iteration to convergence = the recurrent settling** to a sense attractor (Rodd) — a linear settling dynamic reading out the most contextually supported synset.
- **Reading out the highest-scoring synset of the target = which attractor the system settled into.**

**This is the pinned bridge:** graph spreading-activation over WordNet (UKB-style PPR) is simultaneously (a) the computational analog of the brain's semantic-network mechanism, (b) glass-box, and (c) empirically above MFS. The SOLVER's Path A used *GloVe averaging* — a static-vector centroid with **no network, no diffusion, no settling** — which is exactly the piece the brain account says is load-bearing and which the prototype omitted.

---

## PINNED vs OUR-INVENTION synthesis

| Element | Status | Note |
|---|---|---|
| Sense selection = **spreading activation over a semantic network** | **PINNED** | Collins & Loftus 1975; ATL semantic hub |
| Ambiguity resolved by **recurrent settling into an attractor**, context biases the basin | **PINNED** | Rodd 2004; "Settling into Semantic Space" 2020 |
| Context = **pre-activation / priming** of candidate meanings before readout | **PINNED** | Kuperberg predictive coding |
| **Personalized PageRank / RWR** as the computational realization of spreading activation | **PINNED bridge** (verified equivalence) | PPR = RWR = diffusion form of spreading activation |
| **A graph of concepts with typed relations** as the substrate | PINNED *in shape* | brain has a semantic network; WordNet is a hand-built proxy |
| **WordNet's specific sense inventory + granularity** | OUR-INVENTION / SUPPLIED | a supplied resource; granularity may mismatch WiC gold (see caveat) |
| **SyntagNet syntagmatic edges** | OUR-INVENTION / SUPPLIED | free downloadable resource; offline foundation build |
| **PageRank damping (0.85), gloss-edge set, WiC same/diff threshold** | OUR-INVENTION (parameters) | sweep them; do NOT adopt a number as if pinned |
| **GloVe centroid of context (the prototype's Path A)** | OUR-INVENTION — and the *wrong* one | no network/diffusion/settling; predicts the omission that caused the MFS collapse |

---

## 5. DECISIVE RECOMMENDATION

**Build personalized-PageRank spreading-activation WSD over the WordNet graph (the UKB `ppr_w2w` algorithm), enhanced with SyntagNet edges (SyntagRank) and adapted-Lesk gloss overlap as a tie-breaker. Apply to WiC via the "disambiguate both sentences, compare synsets" protocol.**

Why this one:
- **Glass-box, LM-free at inference** — inference is a PageRank power-iteration over a static graph; no neural forward pass. ✓ satisfies "NO external LLM at inference."
- **Brain-faithful (PINNED bridge)** — it *is* spreading activation + settling, the mechanism the brain uses; the prototype omitted exactly the diffusion/settling step. ✓
- **Clears MFS on all-words** — UKB ~67, SyntagRank ~72 vs MFS 65.2, whereas the prototype sat AT 0.59. ✓
- **Buildable from assets confirmed on disk** — nltk WordNet (117,659 synsets + glosses + relations), scipy/networkx for PageRank power-iteration, spaCy for lemma+POS to restrict candidate synsets, gensim GloVe if Lesk expansion is wanted. SyntagNet is a free offline download (admissible foundation). No live LM anywhere. ✓

**Concrete recipe (and the exact traps to avoid):**
1. Build the WordNet graph as a sparse adjacency matrix: nodes = synsets; edges = WordNet relations **plus the gloss-disambiguation ("WordNet++") edges** — *this is mandatory; vanilla relations alone give only ~58–62, below MFS.*
2. For each sentence: spaCy → lemmatize + POS-tag content words → their candidate synsets are the personalization seeds.
3. Run **`ppr_w2w`**: personalize the restart distribution on the context content words, PageRank to convergence (damping ≈ 0.85 — a parameter to sweep), read out the top synset for the target token. (Do the whole sentence jointly, read out each word — not one word in isolation.)
4. WiC label: predict **"same sense" iff the two target synsets match**, or use synset path-similarity above a dev-tuned threshold to absorb granularity mismatch.
5. If it lands only ~0.60–0.63: add **adapted-Lesk gloss overlap** to re-rank PPR's top-k (still LM-free), and add **SyntagNet edges** (the ~+4–5 all-words lever). Both are pure-graph.

**Honest expected accuracy (deflated, no measurement yet):**
- All-words WSD (if we ever want it): **~67 (UKB) → ~72 (SyntagRank)** — clears MFS, well-established.
- **WiC specifically: my honest estimate is ~0.62–0.68.** It *should* clear the ~0.59 dominant-sense baseline, because PPR uses cross-sentence context to move OFF the dominant sense — the precise thing the GloVe/MiniLM prototype could not do. **But two caveats:** (a) no paper reports UKB/SyntagRank on WiC, so this is extrapolation from all-words, not a cited WiC number; (b) WiC gold labels come from mixed inventories (WordNet/Wiktionary/VerbNet) and a WordNet-synset-equality rule has an inherent granularity-mismatch ceiling (~0.75–0.80) and can lose specific pairs where WiC "different" maps to one WordNet synset. **So: not guaranteed to reach LMMS's 0.677 (which buys its edge with a live encoder), but expected to clear MFS.**
- **This must be smoke-tested at full-N on WiC dev before any strong claim** (discriminator-survives-scale discipline). The load-bearing prediction to falsify: PPR-WSD > 0.59 on WiC dev. If it does NOT beat MFS *with* gloss-edges + ppr_w2w + SyntagNet in place, THEN (and only then) is the harder "inventory-mismatch / WiC-needs-finer-than-WordNet" story on the table — and even that is a fidelity gap to build across (finer sense inventory), not an "LLM-gated" wall.

**What NOT to conclude again:** do not read a GloVe-centroid or sentence-encoder null as "LLM-gated." The literature says the LM-free graph path beats MFS and the frozen-encoder-done-right path beats it by ~10; the prototype tested neither correctly.

---

## TL;DR (plain English)
The earlier "we need a big language model to tell word meanings apart in context" conclusion was drawn from a broken test. Two better ways exist. One uses **no neural network at all**: treat a dictionary's web of word meanings as a network, drop a little "activation" on the words around the target, let it spread through the network, and see which meaning lights up most — this is exactly how the brain is thought to pick meanings (spreading activation settling into the right meaning). This graph method already beats the "just guess the most common meaning" baseline on the standard test (about 67–72 correct out of 100 vs 65), and we have every piece to build it on disk (WordNet, the graph tools, the tagger). The other way (a frozen language model with the *right* settings) also beats the baseline, but it still runs a language model at answer-time, which our rules forbid — so we set it aside except as an offline helper. Recommendation: **build the spreading-activation (personalized-PageRank) word-meaning picker over WordNet.** Honest expectation: it should beat the "most common meaning" baseline on the context test (roughly 62–68 out of 100), though it may not match the language-model number; we must run it at full size to be sure, and we must include the dictionary's gloss links or it will quietly fail.

## QUESTIONS
None — the path is clear enough to build and smoke-test.

## NEXT STEPS
1. SOLVER builds the PPR/`ppr_w2w` WordNet spreading-activation WSD (mandatory: gloss-disambiguation edges + ppr_w2w + damping 0.85).
2. Smoke at full-N on WiC dev; falsifiable prediction: accuracy > 0.59 (MFS). Report CI half-width beside the margin.
3. If ~0.60–0.63: add SyntagNet edges + adapted-Lesk re-rank (both LM-free) and re-measure.
4. Only if it still fails to beat MFS *with all three settings in place* → escalate to the "WiC inventory finer than WordNet" fidelity gap (build a finer inventory), NOT to "LLM-gated."

---
### Sources
- [Random Walks for Knowledge-Based WSD (UKB; Agirre & Soroa, Computational Linguistics 2014)](https://aclanthology.org/J14-1003.pdf)
- [UKB is inadvertently state-of-the-art in knowledge-based WSD (Agirre, López de Lacalle & Soroa 2018)](https://arxiv.org/abs/1805.04277)
- [Know Your Graph. State-of-the-Art Knowledge-Based WSD (Popov, Simov & Osenova 2019)](https://aclanthology.org/R19-1110.pdf)
- [Personalized PageRank with Syntagmatic Information (SyntagRank; ACL 2020 demo)](https://aclanthology.org/2020.acl-demos.6/)
- [SyntagNet: Challenging Supervised WSD with Lexical-Semantic Combinations (Maru et al. 2019)](https://www.researchgate.net/publication/336999570_SyntagNet_Challenging_Supervised_Word_Sense_Disambiguation_with_Lexical-Semantic_Combinations)
- [A Synset Relation-enhanced Framework with a Try-again Mechanism (SREF; Wang & Wang, EMNLP 2020)](https://aclanthology.org/2020.emnlp-main.504/)
- [Semantic Specialization for Knowledge-based WSD (SS-WSD; 2023) — comparison table with MFS 65.2, SREF_kb 72.7](https://arxiv.org/html/2304.11340)
- [LMMS: Language Modelling Makes Sense (Loureiro & Jorge 2019) / LMMS reloaded (AIJ 2022)](https://www.sciencedirect.com/science/article/pii/S0004370222000017)
- [WiC: the Word-in-Context Dataset (Pilehvar & Camacho-Collados 2019)](https://arxiv.org/pdf/1808.09121)
- [SenseBERT: Driving Some Sense into BERT (WiC frozen 0.795)](https://arxiv.org/pdf/1908.05646)
- [GlossBERT: BERT for WSD with Gloss Knowledge (D19-1355)](https://aclanthology.org/D19-1355.pdf)
- [MirrorWiC: On Eliciting Word-in-Context Representations from Pretrained LMs (2021)](https://arxiv.org/pdf/2109.09237)
- [Modelling the effects of semantic ambiguity in word recognition (Rodd et al. 2004)](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2801_4)
- [Settling Into Semantic Space: An Ambiguity-Focused Account of Word-Meaning Access (2020)](https://www.researchgate.net/publication/338727615_Settling_Into_Semantic_Space_An_Ambiguity-Focused_Account_of_Word-Meaning_Access)
- [A Spreading-Activation Theory of Semantic Processing (Collins & Loftus 1975)](https://www.researchgate.net/publication/200045115_A_Spreading_Activation_Theory_of_Semantic_Processing)
- [Which One to Choose: Random Walks or Spreading Activation? (2014) — PPR = RWR = diffusion form of spreading activation](https://link.springer.com/chapter/10.1007/978-3-319-12979-2_11)
