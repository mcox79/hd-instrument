# Research: contextual ENCODING vs sense-DISCRIMINATION for rare-sense selection — glass-box mechanism candidates

Filed by: research sub-agent, 2026-09-03. Topic: `reader_meaning_channel` / word-sense selection —
drill requested directly (context-representation angle, not the frequency-prior angle already
tested). 3 parallel Sonnet lit-scan sub-agents dispatched (computational contextualization
mechanisms; attractor/recurrent neuro mechanisms; sense-discrimination-vs-encoding dissociation
evidence), synthesized here by the director agent.

**Field advisor note:** `research_field_advisor.py` was run at cycle start per the standing ritual;
its candidate list (free-probability, Glauber dynamics, etc.) is built for the substrate-physics
scope and is not adjacent to this cognitive-neuroscience/NLP question — noted, not applied, same
disposition as the 2026-08-23 and 2026-08-13 companion notes on this topic.

## HEADLINE

**The bag-of-context-words average is capped for a structural reason the literature independently
converges on from two directions, and the fix is upstream of every lever already tried on this
substrate.** (1) Psycholinguistics: for the specific case named in the prompt — a rare sense whose
context shares TOPIC with its dominant twin — the brain does not discriminate among fixed sense
representations; related/polysemous senses share ONE representation that is dynamically reshaped by
context (Klepousniotou & Baum 2007; Rodd, Gaskell & Marslen-Wilson 2002's "ambiguity advantage" for
related-but-not-unrelated senses; Messi & Pylkkänen 2025's MEG/RSA finding that a continuous
"every-context-gets-its-own-embedding" model beats any categorical selection-among-alternatives
model). (2) Pre-transformer computational semantics reached the same conclusion independently:
Erk & Padó (2008, 2010) and Thater, Fürstenau & Pinkal (2011) built genuinely contextualized word
representations WITHOUT a flat context average, by filtering/weighting context words by their
SYNTACTIC/DEPENDENCY relation to the target — precisely the "governor/frame" cue the psycholinguistics
deepdrill (2026-08-05) independently found to be the single strongest, fastest, near-categorical LOCAL
disambiguating signal. **Both literatures name the same missing ingredient: the query representation
needs to be built from syntactically-structured local context, not a flat topic-level bag — and this
is a different, upstream lever from every one already tested here (frequency-prior additive term:
REFUTED; per-dimension multiplicative gain: HARD_FAIL on estimation noise; attractor settling:
explicitly not recommended).**

## Mechanism candidates — PINNED vs speculative, glass-box feasibility, brain structure

**1. Syntax/dependency-filtered second-order context vectors** (Erk & Padó, *A Structured Vector
Space Model for Word Meaning in Context*, EMNLP 2008, ACL D08-1094; Thater, Fürstenau & Pinkal,
*Word Meaning in Context: A Simple and Effective Vector Model*, ACL/IJCNLP 2011, I11-1127).
**Mechanism, verified this pass:** instead of averaging every content word in a window, weight/gate
context words by their DEPENDENCY RELATION to the target (subject-of, object-of, PP-argument, etc.);
Thater et al.'s "second-order" step additionally substitutes each context word's OWN distributional
context, one level of composition deeper than raw co-occurrence. **Brain mapping: PINNED as a
computational analogue of the governor/frame cue** — Hare, McRae & Elman 2003 "Sense and structure"
(verified 2026-08-05 deepdrill) shows verb-argument-structure expectations are themselves
sense-specific and jointly constrain governor and argument; the N400/frontal-negativity literature
(same deepdrill) shows this cue acts within ~100-200ms, before the slower discourse-context
signal. **Glass-box feasibility: HIGH.** Needs only a dependency parser (already in-wheelhouse per
the 2026-07-21 note's VerbNet-frame disambiguator) plus a co-occurrence table over
SemCor/word2vec-scale text — no neural training required. **This is the single most promising
candidate to prototype next** (see cheap decisive test below).

**2. Exemplar-based retrieval instead of per-sense centroid averaging** (Erk & Padó, *Exemplar-Based
Models for Word Meaning in Context*, ACL 2010, P10-2017 — verified: retrieves the k stored training
CONTEXT INSTANCES most similar to the query context and votes/weights over them, never collapsing a
sense's training contexts into one averaged vector). **Brain mapping: SPECULATIVE-BUT-PRINCIPLED** —
grounds in Nosofsky's Generalized Context Model (the canonical exemplar-theory account of
categorization: similarity-weighted voting over ALL stored exemplars, `s(x,y)=exp(-λ·d(x,y)^p)`,
no compact prototype) and in this project's OWN already-PINNED finding (Tyler & Moss Conceptual
Structure Account, cited at ORGAN_MAP C4) that averaging/pooling washes out weakly-correlated
DISTINCTIVE features — exactly the failure mode that makes a rare sense's discriminating context
instances disappear into a centroid dominated by its topic-sharing twin's many more instances.
**Glass-box feasibility: HIGH**, cheaper than #1 — no parsing needed, just don't collapse the
accumulator (same "graded quantity built and thrown away one line before use" pattern already
diagnosed at ORGAN_MAP B3, applied to context instances instead of anchor dimensions).

**3. Small recurrent "Sentence Gestalt"-style contextual encoder** (Rabovsky, Hansen & McClelland,
*Nature Human Behaviour* 2018 — full text read this pass). **Mechanism, PINNED from direct read:**
a genuinely tiny (Input 74 / Hidden1 100 / SG-gestalt 100 / Hidden2 100 / Output 176 units) recurrent
network whose SG-layer hidden state is a running, word-by-word-updated "meaning so far" — the
literal contextualized representation, computed with the FULL sentence history rather than a
window average, and validated against **16 distinct N400 phenomena** with N400 defined as the
magnitude of the SG-state update (`SUₙ = Σᵢ|aᵢ(wₙ)−aᵢ(wₙ₋₁)|`), which doubles as the training
signal. **Brain mapping: PINNED**, the strongest brain-validation of any candidate here — this IS a
published computational model of the N400. Companion model, also read in full this pass: Nour
Eddine, Brothers, Wang, Spratling & Kuperberg (*Cognition* 2024) — a hand-coded (not trained),
genuinely iterative predictive-coding network (20 settling steps, rise-then-fall error dynamics
matching the N400 waveform's time course) with frequency encoded as feedback-weight strength and
context as top-down clamping — an alternative small glass-box architecture with the same
"meaning-as-running-state" property, though its "precision" is NOT a distinct learned parameter as
sometimes framed in secondary sources (verified from primary text). **Glass-box feasibility:
MEDIUM** — both are inspectable and tiny relative to any transformer, but both require training/
hand-coding a new component rather than reusing existing SemCor/word2vec-scale infrastructure
directly; the SG-model's published training corpus is a hand-built artificial microworld, not real
text, so porting it to this substrate's actual corpus is itself unbudgeted work. **This is the
architecturally closest thing to "what BERT/BEM do that a bag-of-words does not," and the ceiling
candidate if #1/#2 under-deliver — not the first thing to build.**

**4. Attractor settling on the EXISTING representation** (Rodd, Gaskell & Marslen-Wilson,
*Cognitive Science* 2004 — mechanism partly re-verified this pass: frequency shapes attractor-basin
geometry via training, context is an external bias on a multi-cycle settling trajectory,
similar/related senses converge to one broad basin producing the "ambiguity advantage," dissimilar
senses form competing basins that slow settling). **Do not re-propose on this substrate's current
representation** — already explicitly declined at ORGAN_MAP C4 on Tyler & Moss CSA grounds
(distinctive features are weakly correlated, and attractor settling is DRIVEN by correlational
structure, so it would make near-neighbour discrimination WORSE, not better). This scan's finding
does not change that verdict: Rodd 2004's basins are shaped by TRAINING on many prior encounters,
which is a different lever than settling dynamics applied post-hoc to a single query vector. If
either #1 or #2 lands, #4 remains available as the brain's own compensator for the residual cost —
not before.

## Question 4 answered directly: discrimination or encoding?

**Encoding, for the case in the prompt — but the answer is genuinely type-dependent, not universal,
and that dissociation IS the evidence.** Klepousniotou & Baum (2007) and Klepousniotou, Titone &
Romero (2008): RT/priming for metonymic (highly-overlapping) polysemes tracks degree of sense-overlap
and patterns with a shared, contextually-modulated representation; homonyms pattern differently,
consistent with competition among genuinely separate representations. Rodd, Gaskell & Marslen-Wilson
(2002, *J Mem Lang* 46:245-266) is the cleanest behavioral dissociation: related senses (e.g.
"twist") SPEED UP lexical decision relative to unambiguous controls; unrelated senses (e.g. "bark")
SLOW IT DOWN — the same ambiguity-count variable produces opposite effects depending on whether the
senses are related, which a pure discrimination-among-N-candidates account cannot explain but a
"more related senses = richer single representation" account predicts directly. Messi & Pylkkänen
(2025, *J Neurosci* 45(19)) — MEG + RSA, read via search this pass, scoped to noun/verb ambiguity —
found no categorical (discrete-sense) model matched the brain data as well as an "All-Embeddings"
model in which every contextualized token use gets its own point in a continuous space; flag as
CONFOUNDED with syntactic-category change, not pure lexical-sense selection, but the direction is
unambiguous. Frisson (2009, *Lang & Ling Compass* 3:111-127, theoretical/behavioral, not neural)
and Pustejovsky's Generative Lexicon (1995, theoretical/computational-linguistics, not neural) both
independently argue senses are not enumerated-then-selected but generated/particularized from a
richer underlying structure — convergent with, but not independent evidence for, the same
conclusion. **The prompt's own framing ("our query is topic-level and cannot separate a rare sense
from its dominant twin that shares the topic") is exactly the polysemy/related-sense case where this
literature says discrimination-among-fixed-alternatives is the wrong frame — the WordNet gloss
targets (candidate output space) are fine; the query CONSTRUCTION is the gap.**

## Cheap decisive test

Build arm 1 (syntax-filtered second-order context vector) as a drop-in replacement for the flat
bag-of-context-words query, holding everything else fixed (same WordNet gloss targets, same argmax
decision rule, same corpus). No training, no new representation format — a dependency parse +
relation-typed co-occurrence table over existing SemCor/corpus text. Score on the same rare-sense
held-out set already used to measure the 0.33/0.35 ceiling, split into TOPIC-CONFOUNDED items (rare
sense's context shares topic with its dominant twin — the case this whole drill targets) vs
TOPIC-DISTINCT items (control bucket, where a flat bag should already do fine).

## Falsifiable predictions

**Arm 1 — syntax-filtered second-order context vector (primary).**
- **HARD-PASS:** accuracy on TOPIC-CONFOUNDED rare-sense items improves over the flat-bag baseline
  by a CI-separated margin, AND the gain is concentrated on TOPIC-CONFOUNDED items specifically
  (larger than on TOPIC-DISTINCT items) — reproducing the predicted mechanism (syntactic structure
  helps exactly where topic alone cannot discriminate), not a generic "more structure helps"
  artifact.
- **HARD-FAIL:** no CI-separated gain over the flat-bag floor; OR the gain is reproduced equally by
  a same-cardinality RANDOM subset of context words (control for "fewer/sparser context words helps"
  rather than "syntactically-relevant ones help" — this control is mandatory, not optional, per this
  project's own repeated finding that a sparser/smaller representation can look like a win on a
  rank-based metric for reasons having nothing to do with information content); OR the arm fails to
  clear the scrambled-context and frequency/MFS floors already established for this problem.
- P_deflated: **0.40** (raw ~0.55-0.65 from two independently-converging literatures — psycholinguistic
  governor/frame primacy + pre-transformer computational semantics both naming syntactic filtering as
  the fix — deflated 0.20-0.25 per the mandatory lit-scan penalty; no source tests this exact
  combination — syntax-filtered context vectors feeding WordNet gloss-target argmax — directly).

**Arm 2 — exemplar retrieval instead of centroid averaging.**
- **HARD-PASS:** k-NN-over-training-instances beats centroid-averaging by a CI-separated margin on
  rare-sense items, concentrated on senses with FEW training exemplars (where centroid dilution by
  a topic-sharing dominant twin's many more instances is most severe).
- **HARD-FAIL:** no gain; OR the gain does not survive replacing retrieved exemplars with same-count
  RANDOM noise vectors (mandatory positive-information control, per this project's own "an empty/
  degenerate representation can score perfectly on a rank metric" finding — tie-density and both
  rank conventions must be reported, not just the optimistic one).
- P_deflated: **0.35** (support is more indirect — Tyler & Moss CSA plus one direct NLP precedent,
  Erk & Padó 2010, rather than two independently-converging literatures).

**Arm 3 — small recurrent contextual encoder (ceiling candidate, not first-build).** No falsifiable
prediction registered this cycle — flagged as the next drill if arms 1-2 under-deliver, since it
requires a build decision (train vs. port an existing SG-model implementation) this note does not
make.

## Cross-thread synthesis (this project's own prior work)

- **`reader_meaning_channel` REFUTED (per ORGAN_MAP / STATUS.md):** the additive frequency-prior arm
  proposed in `research_wsd_context_conditioned_sense_selection_2026-08-23.md` was built and did NOT
  clear the most-frequent-sense floor (0.4702 vs 0.4778, not separated). **This drill's two primary
  candidates are a DIFFERENT lever** — they change the CONTEXT QUERY CONSTRUCTION, not the decision
  rule's scoring terms, so the frequency-prior refutation does not bear on them directly.
- **ORGAN_MAP C3 (semantic control / multiplicative per-dimension gain):** built and HARD_FAILED
  (`exp_task_local_normalisation_pool_v1`, d=-0.0220 CI[-0.034,-0.0097]) for an ESTIMATION-NOISE
  reason — 256-dim / ~70-obs-per-concept regime, worst-estimated dimensions are the largest-
  anchor-difference ones — strictly blocked behind B4 (representation capacity). **Arms 1-2 here are
  NOT blocked behind B4 the same way**: arm 1 adds a different information source (syntactic
  structure) to query construction rather than re-estimating per-dimension gains on the same noisy
  256-dim anchors; arm 2 sidesteps per-dimension estimation entirely by comparing whole instance
  vectors via existing similarity, never computing a new per-dimension statistic.
- **ORGAN_MAP C4 (attractor settling):** explicitly declined to build on this representation
  (Tyler & Moss CSA: distinctive features are weakly correlated, so attractor settling would worsen
  near-neighbour discrimination). This drill's candidate #2 (exemplar retrieval) draws on the SAME
  Tyler & Moss finding but applies it oppositely and constructively: if pooling/averaging is what
  destroys distinctive signal, the fix is to NOT pool (retrieve instances) rather than to add
  recurrent dynamics on top of an already-pooled representation.
- **ORGAN_MAP B3 (across-occurrence accumulation):** already-diagnosed pattern — "the graded quantity
  is built and thrown away one line before use" (a genuine graded accumulator exists, then gets
  discarded via `np.sign`). Arm 2's exemplar-retrieval proposal is the SAME diagnosed pattern one
  level up: individual context instances are computed, then thrown away by collapsing into a
  per-sense centroid before use.
- **2026-08-05 deepdrill** (governor/frame cue ranking): independently arrived at "governor/frame is
  the strongest, fastest, near-categorical LOCAL override" from pure psycholinguistics/neuroscience
  evidence (Badre & Wagner 2005/2007; Hare, McRae & Elman 2003; MEG timing PMC5840520). This drill's
  arm 1 is the direct computational implementation of that same finding, independently corroborated
  by the pre-transformer NLP literature (Erk & Padó; Thater et al.) — a genuine cross-thread
  convergence, not a restatement.
- **2026-07-21 note** (VerbNet frame-matching for verb-sense affectedness): already establishes that
  a dependency parse is in-wheelhouse and VerbNet per-sense frame data already exists — the
  infrastructure arm 1 needs (parse + relation-typed context weighting) substantially overlaps with
  infrastructure already scoped for a different (verb-affectedness) problem.
- **2026-08-13 lit-scan** (near-neighbour semantic control): pins the CSA distinctive-feature-fragility
  finding this drill's arm 2 builds on, and separately flags the 2026 PNAS hippocampal pattern-
  separation-by-meaning finding as SINGLE-STUDY/contested — this drill's new attempt to find a
  hippocampal contextual-COMPLETION (not separation) account for lexical retrieval specifically
  came back empty (Davis & Gaskell 2009 CLS account is about learning NEW word forms, not
  disambiguating existing ones) — a genuine gap, not just an unsearched corner.

## Substrate-product implications

The concrete, low-risk next build is arm 1: a dependency-filtered second-order context vector
replacing the flat bag-of-context-words average, holding the WordNet-gloss comparator and argmax
decision unchanged. It requires no new training, reuses parsing infrastructure already scoped for
the verb-affectedness problem, and is NOT blocked behind the representation-capacity issue (B4) that
stopped the mechanistically-correct C3 implementation. If it clears the HARD-PASS bar with the
predicted topic-confound-concentrated asymmetry, that is evidence the SPECIFIC mechanism (syntactic
local structure, not just "more information") is right. If it HARD-FAILs cleanly, arm 2 (exemplar
retrieval) is the next test — a different, near-zero-additional-infrastructure lever attacking the
same diagnosed failure (averaging destroys the discriminating minority signal) from the storage side
rather than the input-construction side. Arm 3 (small recurrent contextual encoder) is the
brain-validated ceiling case, held in reserve — it is the only candidate that would give a genuinely
BERT/BEM-like representation (computed over full sentence history, not a window) while staying
glass-box and orders of magnitude smaller than a transformer, but it requires a build decision this
note does not make.

## Citations (verified count)

**19 distinct primary sources**, each cross-checked by at least one of the three lit-scan sub-agents
via live WebSearch/WebFetch this pass (not from memory), 4 read in full via direct PDF fetch (marked):
Erk & Padó 2008 (EMNLP, ACL D08-1094); Erk & Padó 2010 (ACL P10-2017); Thater, Fürstenau & Pinkal
2011 (ACL/IJCNLP I11-1127); Reisinger & Mooney 2010 (NAACL, **read in full**); Huang et al. 2012
(ACL, **read in full**); Nosofsky GCM (1986, canonical, verified via multiple independent sources);
Melamud, Goldberger & Dagan 2016 (CoNLL K16-1006, context2vec); Rodd, Gaskell & Marslen-Wilson 2004
(*Cognitive Science* 28:89-104); Rabovsky, Hansen & McClelland 2018 (*Nat Hum Behav* 2:693-705,
**read in full**); Rabovsky 2020 (*Neuropsychologia*, verified-via-secondary-source); Rabovsky &
McRae 2014 (*Cognition*, verified-via-secondary-source, NOT independently read this pass — flagged
as the next-most-valuable single fetch); McClelland, McNaughton & O'Reilly 1995 (*Psychol Rev*);
Kumaran, Hassabis & McClelland 2016 (*Trends Cogn Sci* 20:512-534); Davis & Gaskell 2009
(*Phil Trans R Soc B* 364:3773-3800); Nour Eddine, Brothers, Wang, Spratling & Kuperberg 2024
(*Cognition* 246:105755, **read in full**); Klepousniotou & Baum 2007 / Klepousniotou, Titone &
Romero 2008 (verified via PMC review PMC5114844); Rodd, Gaskell & Marslen-Wilson 2002
(*J Mem Lang* 46:245-266); Frisson 2009 (*Lang & Ling Compass* 3:111-127, partially verified —
Wiley-blocked full fetch, triangulated via secondary sources); Pustejovsky 1995 (Generative Lexicon,
trained-knowledge-only for book content, mechanism independently confirmed via search); Messi &
Pylkkänen 2025 (*J Neurosci* 45(19):e0409242025, verified via search, title/authors/journal
confirmed, abstract not directly fetched); Pylkkänen, Llinás & Murphy (MEG polysemy study, verified
via listing, abstract not directly fetched). Plus 18 sources carried forward from the 2026-08-23 /
2026-08-13 / 2026-08-05 companion notes (governor/frame ranking, CSC/CSA, Bayesian-attractor
equivalence) — not re-verified this pass, cited by reference to those notes' own verification.

## Caveats on this note

- Per the mandatory lit-scan calibration penalty, all P estimates above are deflated 0.15-0.25 from
  the raw synthesis estimate and novel-synthesis P is capped at 0.50.
- Several sources were PDF-fetch-blocked (Frisson 2009 full text, Erk & Padó 2008/2010's literal
  equations, Thater et al. 2011's literal formula, Rodd 2004's literal equations) — mechanism
  descriptions above are inferred from what was fetched (abstracts, secondary reviews, GitHub repos),
  not verbatim-quoted, per the standing "do not invent detail past what was fetched" instruction.
- This note does not itself run the cheap decisive test — building the dependency-filtered
  second-order context vector and re-scoring the existing held-out rare-sense set (with the
  mandatory random-subset control) is the next actionable step, handed off separately.
- `research_field_advisor.py`'s candidate list is scoped to substrate-physics and was checked but not
  applicable here, matching the disposition of the three prior notes on this topic.
