# Research: task-regime reframe — is WordNet held-out synonym retrieval the right task shape?

5x-drill 5/5 on Component C (modern-Hopfield readout) HARD_FAIL, commit 4cd1d30ba.
Scope: task-regime framing ONLY (per dispatch instruction). No new experiment designed here.

## HEADLINE

WordNet held-out-synonym-retrieval at N=100/4-sentences-per-concept is not an unfair
task per se, but it is a **confounded** one: at this data scale its dominant
exploitable signal is orthographic shift-invariant substring overlap (a spectrum/
n-gram-kernel regime), and the current surface front-end (`CharPositionalEncoder`,
absolute character-position HRR binding) has near-zero capacity to exploit that
signal for genuinely unseen word-forms. Char-trigram's win is explained by
inductive-bias match, not more data or a smarter concept layer. This means: (1) the
Component-C readout swap was correctly killed — no readout geometry fix can rescue
an encoder-bottlenecked pipeline, so that HARD_FAIL is a true negative, not a task
artifact; (2) the task as currently run cannot distinguish "concept/Hebbian
mechanism is weak" from "surface encoder lacks substring invariance" — those are
conflated; (3) the already-in-flight V2 P1 (VWFA n-gram front end) is the
mechanistically-correct fix, now for a concrete, verified reason (shift/length
invariance), not merely "add a layer"; (4) a genuinely orthogonal task class
(analogy completion / compositional generalization) is needed to test the
concept-level mechanism free of this confound.

## Mechanism trace (verified by direct code read, not assumption)

- `hdlab/char_positional_encoder.py::CharPositionalEncoder.encode_word`: each
  character is HRR-bound (circular convolution) to its **absolute position index**
  within the word, then sign-bundled. This is a classic Kanerva-style slot code:
  it is provably NOT shift-invariant. Two strings sharing a substring at different
  offsets (e.g. any insertion/deletion, or a different-length synonym) produce
  near-orthogonal word-HDs beyond the point of position divergence. Only an exact
  shared PREFIX transfers partial correlation; general substring overlap does not.
- `hdlab/concept_encoder.py::ConceptEncoder.fit`: concept prototype = sign(mean-
  centered accumulated per-training-sentence surface HDs), top-k=2% sparsified
  (competitive/WTA). The prototype is literally built FROM the position-bound
  surface HDs above — it inherits their invariance defect. `encode()`/the cell's
  direct `_surface_encoder.encode_sentence(query)` call bypasses any learned
  adaptation; retrieval is raw cosine between a frozen-hash surface HD of an
  UNSEEN word and this prototype.
- `hdlab/char_trigram_encoder.py::CharTrigramEncoder`: bag-of-overlapping-char-
  trigrams, each trigram independently hashed and sum-bundled. This is shift- and
  length-invariant by construction — a shared substring anywhere in a word
  contributes overlap regardless of position or word length. Classic spectrum-
  kernel behavior (Leslie et al. 2002-class string kernels; k-mer/n-gram bag
  representations are the standard fix for edit-distance-robust text/sequence
  classification under morphological variation, precisely because they discard
  positional binding in favor of shift-invariant substring counts).
- **Training data volume is identical for both arms** (same `training_sentences`,
  `training_labels` list feeds `_fit_concept_encoder` and
  `_build_trigram_prototypes`). The gap is not a data-volume asymmetry; it is an
  inductive-bias asymmetry given the task's actual signal.

This mechanistically explains why char-trigram (r@5=0.28) beats cosine (0.16)
beats Hopfield-readout-on-cosine's-storage (0.05): WordNet glosses/synonyms/
hypernym-phrases share substrings across a concept's own training text and,
often, with its own held-out synonym (compounds, shared roots, shared hypernym
words) — a real, exploitable, low-data signal that only a shift-invariant encoder
can use. Position-bound surface HDs cannot use it at all beyond a lucky shared
prefix, so cosine sits only modestly above the k/N=0.05 chance floor, and Hopfield
softmax re-ranking over the SAME concept-HD storage cannot exceed what cosine's
prototype geometry already contains (confirmed by the cell's own honest framing:
under equal-L2-norm sparse-bipolar storage, `top_k_by_attention` is monotone in
cosine; the only lever is the one-step retrieved-`y` re-ranking, which has nothing
new to work with if the stored prototypes themselves carry no substring signal).

## Task-shape audit — (a) / (b) / (c)

**Verdict: (b)-leaning, with a scale-dependent escape hatch.** At N=100 concepts /
4 sentences-per-concept, WordNet held-out-synonym-retrieval is dominated by
orthographic bag statistics (option b) — not because the task is conceptually
wrong, but because at this data scale there isn't enough cross-concept
distributional co-occurrence for a genuine semantic/associative mechanism to
outcompete direct substring matching. It is theoretically closer to (c) (neutral
probe, mechanism differences would surface at scale) IF AND ONLY IF the surface
front-end had shift-invariant substring generalization in the first place — right
now that precondition is false, so (c)'s premise doesn't hold for the current
architecture. Practical reading: this task, as configured, is currently a
**surface-encoder generalization benchmark wearing a "concept retrieval" label**.
It will keep being won by char-trigram until the surface front-end itself gets
shift/length invariance (V2 P1 direction), independent of anything the
Hebbian/WTA concept layer does.

## Comparison baselines — why char-trigram wins (restated precisely)

Char-trigram is not "smarter" or better-resourced. It has the RIGHT invariance
structure for the specific signal this task offers at this scale (shift-invariant
substring overlap from shared roots/compounds/hypernym phrases in WordNet's
curated glosses). `concept_encoder`'s surface layer has the WRONG invariance
structure (absolute-position binding) for that same signal. This is a spectrum-
kernel-vs-slot-code mismatch, a well-known general phenomenon in sequence
classification under morphological variation — not evidence of a deeper flaw in
the competitive-Hebbian/WTA concept-formation mechanism itself, which sits
downstream of, and is blind to, this specific defect.

## Alternate task classes (ranked)

1. **Analogy completion (a:b :: c:?)** — VSA-native; requires bind/unbind algebra
   over the concept HD space. No bag-of-word/n-gram baseline has a natural
   equivalent (trigram overlap has no notion of "relation"), so this task class is
   structurally immune to the exact confound identified above. Cheapest to build
   from existing WordNet relation metadata (hypernym/hyponym pairs already loaded
   by this cell's corpus loader).
2. **Compositional generalization (novel combination of seen primitives)** — tests
   whether bind/bundle produces correct NEW concept HDs from combinations never
   seen in training. Also immune to the bag-of-word confound; directly tests the
   thing VSA architectures are supposed to be good at (systematicity), rather than
   surface memorization.
3. **Multi-hop / fact-chain retrieval over KG triples** — good long-term probe
   (already-existing `hdlab.kg_traversal` infra), tests associative chaining, but
   more implementation overhead than #1/#2; recommend as a follow-on, not the
   immediate cheap decisive test.

Free-form generation quality was in-scope of the drill question but is ruled out
as an immediate cheap-decisive-test candidate: no cheap, low-implementation-cost
oracle exists for it, and per [[feedback-substrate-doesnt-know-anything]] the
substrate has no general-language ingest yet, so generation-quality framing would
itself be premature.

## Fairness of comparison (Q5)

Confirmed by direct code read: char-trigram gets the IDENTICAL 4-sentences/concept
training text as concept_encoder (same list object passed to both fit functions).
It is not seeing more context, unlabeled text, or extra supervision. Giving
concept_encoder 40x more context would NOT close the gap on its own — the
position-binding defect is a STRUCTURAL invariance mismatch, not a data-starvation
problem. More context could marginally help via increased distributional
co-occurrence density (more chances for query-context words to overlap with
training-context words), but the core defect (query word itself, as a NEW STRING,
produces a near-orthogonal surface HD regardless of corpus size) is untouched by
scaling training volume. This rules out "just add more sentences" as a rescue path
and reinforces that the correct lever is encoder-invariance (V2 P1), not data
volume.

## Stage 4 downstream utility (Q4)

Does WordNet-synonym-retrieval HP predict Stage 4 (glass-box conversational
agent) utility? Partially, and indirectly. Real conversational utility does
eventually require lexical-semantic generalization (paraphrase/synonymy
robustness), so the task is not irrelevant. But as configured (low-data,
position-bound surface front end), a HARD_FAIL here mostly certifies "the surface
encoder lacks shift-invariant substring matching," which is necessary-but-not-
sufficient information for Stage 4 — it says nothing about compositional/relational
capability, which is arguably the more Stage-4-relevant property (an agent needs
to combine and manipulate concepts, not just look up nearest-neighbor strings).
Recommend treating WordNet-synonym-retrieval as a NECESSARY gate for the surface
front end (V2 P1's actual job) and analogy/compositional tasks as the SUFFICIENT
gate for the concept-mechanism's Stage-4-relevant capability.

## Cheap decisive test

Build an analogy-completion probe on the SAME WordNet corpus already loaded by
this cell (`_load_wordnet_atoms`): use existing hypernym-pair metadata to
construct held-out `a:b::c:?` triples (e.g. `hyponym1 : hypernym :: hyponym2 : ?`)
over the same N=100/500-atom pools, same seeds. Baselines: (i) char-trigram
analogy via vector arithmetic on trigram-bag HDs (expected near-chance — trigram
bags have no natural analogy operation, this is the key structural prediction),
(ii) random baseline, (iii) concept_encoder HD analogy via bind/unbind. This
directly tests whether removing the surface-encoder confound reveals a
concept_encoder advantage the WordNet-synonym task was hiding, or whether the
concept/Hebbian mechanism ALSO underperforms once the confound is removed (in
which case the negative evidence generalizes beyond the surface-encoder defect).

## Falsifiable predictions

HARD-PASS (supports "task was confounded; concept mechanism has real signal"):
  concept_encoder analogy-completion accuracy @k=5 exceeds char-trigram-bag
  analogy-completion accuracy @k=5 by >= 0.10, AND char-trigram analogy accuracy
  is within [chance, chance+0.05] (confirms trigram has no analogy mechanism).

HARD-FAIL (supports "concept/Hebbian mechanism also lacks the needed structure,
independent of surface-encoder confound"):
  concept_encoder analogy-completion accuracy @k=5 <= char-trigram-bag analogy
  accuracy @k=5 + 0.03 (no meaningful lift even on a task char-trigram has no
  natural mechanism for) OR concept_encoder analogy accuracy is within
  [chance, chance+0.05] (i.e. concept encoder ALSO can't do relational algebra
  above chance).

MIDDLE_BAND: concept_encoder beats trigram on analogy but by less than the
HARD-PASS margin, or trigram shows unexpected above-chance analogy performance
(would indicate leakage via shared substrings between hypernym-pair members,
requiring a corpus-construction audit before trusting the result).

## Cross-thread synthesis

- Corroborates rather than contradicts the already-in-flight V2 P1 (VWFA +
  late-combine) direction: this drill supplies the MECHANISTIC reason (shift/
  length invariance) V2 P1 is the right lever, rather than "add a dense layer and
  see."
- Confirms Component C's HARD_FAIL (readout-geometry swap) as a TRUE negative:
  readout re-ranking cannot manufacture substring signal that isn't present in
  the stored prototypes. This closes the readout-mechanism-class rescue avenue
  for this specific bottleneck (encoder, not readout) — consistent with
  [[feedback-mechanism-analog-is-not-task-analog]] (a readout swap doesn't touch
  the actual bottleneck stage).
- Extends [[feedback-dont-dismiss-adjacent-methods]] in the other direction: this
  is a case where an adjacent, sensible-looking fix (better readout) was tried
  and correctly killed — the discipline of testing it before assuming was right;
  the reframe is in WHAT stage of the pipeline to fix next, not in whether to
  keep testing readouts.
- Provides string/spectrum-kernel literature grounding (generic CS/math term:
  n-gram / k-mer bag representations as the standard fix for edit-distance-robust
  sequence classification vs. fixed-position slot codes) without any substrate-
  specific terms leaving this note.

## Substrate-product implications

- Do not spend further cycles on Component-C-class readout-geometry rescues for
  the WordNet-synonym task; that mechanism class is closed for this bottleneck.
- V2 P1 (VWFA n-gram front end) is validated as the correct next lever, now with
  a concrete falsifiable mechanism (shift-invariance) rather than a vague "more
  brain-like" justification.
- Before further v3-composed rescue attempts, run the analogy-completion cheap
  decisive test above — it decouples "surface encoder is wrong" from "concept
  mechanism is wrong" and will redirect effort correctly either way.
- This task-regime finding is itself a generalizable pattern check for OTHER
  substrate-content benchmarks: any WordNet-gloss-based or dictionary-style task
  at low N/low-sentences-per-concept should be treated as encoder-confounded
  until the surface front end has verified shift-invariance.

## Citations (verified count: 1, generic-terms-only, no substrate framing used
off-platform)

1. Leslie, Eskin, Noble (2002)-class "spectrum kernel" string-classification
   literature: k-mer/n-gram bag representations are the standard architecture for
   edit-distance-robust sequence classification, as opposed to fixed-position
   (slot-code) representations, which are brittle to insertion/deletion/length
   change. (General knowledge citation; not independently re-verified via live
   web search this cycle — flagged per calibration discipline, treat as P~0.6
   background-knowledge-grade support, not a fresh lit-scan finding.)

## Calibration

- P(this reframe is directionally correct, i.e. task is encoder-confounded and
  readout-class rescue is closed) = 0.62 (deflated from an unadjusted ~0.85 per
  [[feedback-lit-scan-calibration-penalty]]; deflation applied because the
  citation above was not independently re-verified this cycle and because the
  "would 40x context help" claim is argued from mechanism, not measured).
- P(analogy-completion cheap test will show concept_encoder > trigram per
  HARD-PASS band) = 0.45 (capped below 0.50 per novel-synthesis cap; genuinely
  uncharted regime for this specific mechanism).
- Hard-fail thresholds are stated explicitly above in Falsifiable predictions.
