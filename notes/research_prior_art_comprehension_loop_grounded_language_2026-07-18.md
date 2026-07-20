# Prior-art scour: incremental comprehension loop + grounded language learning

Filed by: research (Sonnet lit-scan x4 dispatched, Opus/Sonnet synthesis)
Date: 2026-07-18
Trigger: director request — "who has computationally built (1) the incremental reading-comprehension
loop, and (2) grounded language learning" — feeds a director synthesis alongside 3 sibling scours
(VSA-language, semantic-parsing, neurosymbolic-reading).

Calibration penalty applied throughout per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis
P capped at 0.50, all P estimates deflated 0.15-0.25 off naive.

---

## HEADLINE

**Both halves of what we're calling "the compress-and-carry comprehension loop" and "grounded relation
learning" are pre-existing, named, computationally-implemented research programs — not novel theory.**
The comprehension loop is essentially Kintsch & van Dijk's Construction-Integration (CI) model (1978,
1988) plus its direct computational descendants (Landscape Model, Rabovsky's Sentence Gestalt model,
Franklin/Gershman's SEM). Grounded relation-learning from weak/ambiguous supervision is essentially
Artzi & Zettlemoyer's world-validated CCG induction (2013) and the Chen/Mooney/Kate ambiguous-grounded-
supervision line, both predating this project by 10-45 years. **Credit these by name; do not frame
either as a novel theoretical contribution.** Where a real (unverified, hypothesis-pending) opening
exists is narrower and lower on the stack: a VSA-native, glass-box, at-scale INSTANTIATION of
mechanisms the literature specified only as small trained RNNs, hand-authored propositional networks,
or narrow block/gridworld demonstrations — and the specific choice of a curated ontology/dictionary
as the "world" a relation-learner validates against, which is closer to KB-distant-supervision
(a literature this scour did NOT cover and flags as a follow-up gap) than to any of the sensorimotor-
grounding lines surveyed here.

---

## Part A — Incremental comprehension loop: closest models

### A1. Kintsch's Construction-Integration model (Kintsch 1988, *Psychological Review*; Kintsch 1998
book) + van Dijk & Kintsch macrostructure/macro-rules (1978, *Psychological Review*; 1983 book)

**What it computes.** Two-phase cycle, run per clause/sentence (granularity is a free modeling
parameter, not theory-derived):
- *Construction* (bottom-up, deliberately noisy): parse the text unit into propositions; each
  proposition/word spreads activation into long-term-memory associates (near-neighbors, multiple word
  senses, plausible inferences) **without discourse filtering** — producing an overinclusive, often
  self-contradictory candidate network (nodes = propositions/elaborations, edges = a weighted
  connectivity matrix W, weighted mostly by argument overlap).
- *Integration* (the actual settling computation): an activation vector is repeatedly post-multiplied
  against W, renormalized (negatives clamped, sum-to-one) each pass, until it reaches a fixed point.
  Weakly-connected/contradicted nodes lose activation and drop out; mutually-reinforcing nodes survive.
  This is literal **spreading activation as constraint satisfaction**, explicitly framed by Kintsch as
  a symbolic/connectionist hybrid.
- *Carry-forward*: a buffer holds a recency/importance-selected subset of the settled activation vector
  from cycle N into cycle N+1's construction phase — the closest published "situation-so-far" data
  structure at the micro level (a decaying, refreshed propositional graph, not a fixed-size vector).
- *Compression to gist* (van Dijk macro-rules): **deletion** (drop propositions not presupposed by
  later material), **generalization** (replace an instance-sequence with its superordinate), and
  **construction** (replace a script-consistent sequence with the single global-event proposition it
  instantiates) are applied recursively, layer by layer, compressing microstructure into macropropositions
  — explicitly claimed to happen online during reading (working-memory-forced), not just at
  recall/summary time, with the macrostructure-so-far acting as a top-down schema that constrains
  what looks "coherent" in later cycles.

**Achieved.** Explained disambiguation-over-a-short-lag for homographs, recall/reading-time tied to
argument overlap and node centrality, macrostructure-driven recall dominance (one of the most-replicated
findings in text-comprehension research), individual working-memory-capacity effects.

**Limits.** Propositionalization (parsing raw text into the proposition nodes) is done **by hand** or
semi-automatically by the modeler — CI does the settling, not the parsing or the knowledge-acquisition.
The knowledge net (elaborations/associates) is hand-specified or supplied by an external, separately-
trained semantic-space model (LSA, see A2). **The macro-rules are never formalized as a runnable
algorithm in the original theory** — this is an acknowledged 45-year-old gap, not something this scour
is inventing. Granularity is a free parameter.

### A2. Landscape Model (Zwaan, van den Broek et al.) + LSA-automated weighting

Direct computational descendant of CI: same cyclic settling process, but connections are drawn from a
broader coherence-relation set (referential/causal/spatial/goal, per Zwaan & Radvansky's situation-model
dimensions) plus explicit activation decay (leaky-integrator carry-forward across several cycles, not a
hard reset). One implemented variant swaps hand-coded coherence judgments for **LSA cosine similarity**
(Landauer & Dumais 1997 SVD-reduced co-occurrence space) to auto-generate the construction-phase weights.
This is the strongest available demonstration that CI's settling mechanism runs on **automatically
derived** (not hand-coded) weights and still reproduces human cycle-by-cycle reading data — i.e. the
best template for "how do you actually implement CI's construction phase without a human hand-authoring
the knowledge net per passage," which is exactly the missing piece in the 1978/1988 papers. **Limit:**
LSA itself is a static, corpus-pretrained bag-of-contexts space — no online learning at read time, no
syntax/compositionality, and it supplies candidates but the settling/picking is still CI's separate
machinery. Only semantic *similarity* is automated; causal/spatial/goal coherence relations still
require hand-coding in the classic Landscape Model.

### A3. Sentence Gestalt model (Rabovsky, Hansen & McClelland 2018, *Nature Human Behaviour*; built on
McClelland/St. John/Taraban 1989)

**What it computes.** A recurrent network with an *update* net and a *query* net. Each incoming word
is combined with the **previous SG hidden-state** to produce an updated SG vector — a running,
distributed, probabilistic representation of "what event is being described," literally a compressed
situation model carried forward and updated per word. The query net is trained to answer thematic-role
questions from the current SG state (the training signal that shapes the representation). N400 (a
comprehension-difficulty ERP signature) is modeled as the **magnitude of change** the incoming word
induces in the SG state — an explicit update-magnitude/prediction-error signal, not raw activation.

**Achieved.** Reproduces 16 distinct qualitative N400 phenomena (cloze-probability, semantic-relatedness/
priming, plausibility, role-reversal-but-plausible sentences, role-filler-count effects) from one uniform
mechanism; later scaled from a hand-built synthetic microworld corpus to a large naturalistic text corpus.

**Limits.** Small learned architecture, originally trained on synthetic/microworld sentences (not open
text) before the 2021 scale-up; shallow, so some latency-invariance phenomena aren't captured; the
"gist" state is an opaque trained RNN hidden vector — not inspectable/decomposable the way a symbolic
propositional network or a glass-box VSA vector could in principle be.

**This is the single closest published exemplar of the literal architecture we're describing** ("predict
next chunk, compare to what's read, update+compress a running situation model, carry forward") — but it
is a small opaque neural net proven on synthetic/microworld data, not a general large-scale reader.

### A4. Structured Event Memory (SEM) — Franklin, Norman, Ranganath, Zacks & Gershman 2020, *Psych. Review*
(building on Reynolds/Zacks/Braver 2007 and Zacks' Event Segmentation Theory)

**What it computes.** A probabilistic generative model over sequences of structured symbolic scenes.
An event schema is a learned RNN "event model" predicting how the current scene's features evolve one
step ahead. At each new scene, SEM computes each active schema's prediction error; if no schema explains
the new scene well, it infers an **event boundary** and instantiates/selects a new schema via a
**Bayesian nonparametric (Chinese-Restaurant-Process-like) clustering process** — an open-ended,
growing repertoire of event types learned without pre-specifying how many exist. Post-boundary, the
chosen schema updates online, so the same schema gets recognized/reused across episodes (schema
generalization).

**Achieved.** Human-comparable event-segmentation agreement on naturalistic video/activity stimuli;
reproduces classic memory phenomena (better memory near event boundaries, schema-consistent intrusions);
demonstrates CRP-like schema discovery finding a sensible number of event types unsupervised.

**Limits.** Requires pre-structured symbolic scene input (does not learn to segment raw perception);
granularity fixed by input sampling rate; does not itself model text/discourse (propositions, coreference)
— its bridge to the CI/situation-model tradition is conceptual ("settle until surprised, then reset"),
not a shared implementation.

**This is the cleanest fully-computational, quantitatively-specified instance of "compress-and-replace
under a running model, triggered by prediction error"** — the mechanism most directly answering "when do
we start a NEW situation model vs. keep updating the current one," which CI/Landscape/SG leave largely
implicit or heuristic (recency-based buffer, not error-triggered).

### A5. Supplementary: surprisal theory (Hale 2001; Levy 2008) and cue-based retrieval (Lewis & Vasishth
2005, ACT-R)

Surprisal (-log P(word|context), computed via an incremental probabilistic Earley parser maintaining a
full distribution over live parses) gives the cleanest "predict distribution over continuations, compare
to actual next word" half of the loop, and Levy shows it's equivalent to KL-divergence/belief-revision
cost — but **has no compression/gist step at all**: the carried-forward state is the exact, uncompressed
parse-probability distribution. Lewis & Vasishth's ACT-R model gives a different, useful piece: memory
as a flat, content-addressable pool of "chunks" scored by base-level activation (recency/frequency decay)
+ spreading activation from retrieval cues − fan-effect interference, explaining agreement-attraction and
locality effects — a candidate mechanism for how OUR carried-forward context should be scored/retrieved,
but again no separate gist/compression layer (memory is just the chunk pool).

### Also load-bearing as *framing*, not mechanism: Christiansen & Chater's "Now-or-Never bottleneck" /
Chunk-and-Pass (2016, *BBS*)

Theoretical argument (not a single quantitative model) that because raw linguistic input decays almost
immediately, comprehension is FORCED into multi-level compress-and-pass-upward processing at every
level (acoustic→phonological→lexical→syntactic→discourse) to free low-level buffers — i.e. our
"compress and carry forward" isn't an optional design choice, it's the only way any resource-bounded
comprehender (biological or substrate) can work. Good motivating citation for product framing; not
itself adoptable code/algorithm.

---

## Part B — Grounded language learning: closest models

### B1. Steels' naming games / Talking Heads / Fluid Construction Grammar (Steels 1995 *Artificial Life*;
Steels & Kaplan *Talking Heads* 1999-2001, open-access book; Steels FCG papers)

**Mechanism.** Population of agents plays repeated two-agent language games over a shared perceptual
context. Each agent keeps a scored word(construction)-to-meaning association table; on success both
raise the used association's score (and inhibit competitors), on failure they lower it / repair via a
sub-game. Grounding comes from a **discrimination-game** over real feature vectors extracted from actual
camera scenes (Talking Heads ran on real robots across multiple cities, not simulation-only) — categories
are self-invented by the agent's own perceptual discrimination process, not handed a symbolic label.
Fluid Construction Grammar extends the identical scored-table mechanism from single words to full
form-meaning constructions, with invention/abduction/induction repair operators producing emergent
grammatical agreement, word order, and case systems purely from communicative pressure.

**Achieved.** Convergent shared lexicons grounded in real camera-derived scenes across physically
distributed real robots; emergent grammar phenomena in simulated multi-agent worlds.

**Limits.** Modest vocabularies (tens of words), small agent populations (single digits to a few dozen),
never demonstrated at open-vocabulary/LLM scale; object segmentation is still fairly engineered.

### B2. Cross-situational statistical word learning: Frank, Goodman & Tenenbaum 2009 (*Psych. Science*)
and Yu & Ballard 2007 (*Neurocomputing*)

**Mechanism.** At each of many scenes, the learner sees an utterance plus a **hand-specified candidate-
referent set** standing in for the perceived scene. Because within one scene the true word→referent
mapping is ambiguous, evidence accumulates across scenes until it converges. Yu & Ballard adapt
statistical-machine-translation alignment (IBM Model 1, EM) plus real caregiver gaze/prosody cues as
extra alignment features. Frank/Goodman/Tenenbaum instead run full Bayesian joint inference over the
lexicon AND each utterance's intended referent, explicitly modeling that some words (verbs, function
words) don't map to any object referent at all — beating pure co-occurrence-counting and pure
gaze-following baselines on real CHILDES-style annotated corpora.

**Achieved.** Explains mutual exclusivity, fast-mapping/one-trial learning, use of social/intentional
cues; a 2023 review (PMC10400455) catalogs **19 distinct such models**.

**Limits.** Grounding here is thin: a hand-specified candidate-object list stands in for perception, not
real vision. Per the 2023 review, almost all 19 models handle **simple noun-object mappings only** —
verbs, relations, and multi-word phrases remain comparatively unexplored in this specific literature.

### B3. Weak/denotational semantic parsing grounded in an executable world: Artzi & Zettlemoyer 2013
(*TACL*), building on Clarke/Goldwasser/Chang/Roth 2010 (CoNLL) and Liang/Jordan/Klein 2011 (ACL)

**Mechanism.** Grounded, weighted CCG with typed lambda-calculus logical forms using **Neo-Davidsonian
event semantics** — actions are event-typed objects with relational/prepositional modifiers as
intersective constraints, plus "stateful" predicates evaluated against world-state at action-sequence
start vs. end, plus an "implicit actions" slot for steps instructions don't spell out. Learning uses
**zero gold logical forms** — only a validation function V(candidate-action-sequence) → {match, no-match}
against either a full demonstration trace or just the final resulting state. Algorithm alternates: (1)
GENLEX-style lexical induction restricted to entries used in the highest-scoring VALID parse (coarse-to-
fine pruning of a huge candidate lexicon), (2) a margin-based perceptron-style update using the
validation signal (not a gold loss) to separate valid from invalid parses.

**Achieved.** 60% more instruction sequences executed correctly than prior SOTA on a navigation-
instruction benchmark; weak (final-state-only) supervision performs nearly as well as full-trace
supervision; ablations show both joint parse+execution and implicit-action modeling are load-bearing
(removing either roughly halves sequence accuracy).

**Limits.** Single domain (indoor navigation); needs a small hand-built seed lexicon (~12 sequences,
141 entries) to bootstrap; worst-case-exponential (empirically tractable) evaluation.

**This is the strongest available precedent for "learn RELATIONS (not just nouns) from grounded, weak/
ambiguous supervision" — directly on-topic for a system that wants to learn relation meaning from text
grounded against an ontology rather than gold relation-labels.**

### B4. Ambiguous-grounded-supervision EM line: Kate & Mooney 2007 (KRISPER, AAAI) and Chen & Mooney
2008 (sportscasting, ICML)

**Mechanism.** Training pairs are (sentence, SET of candidate meaning-representations) with no gold
alignment. A bipartite-matching pruning step removes provably-wrong sentence–MR edges; remaining
candidates are treated as equally likely, a weighted string-kernel-SVM parser (KRISP) is trained, then
re-scored and re-assigned via Hungarian-algorithm maximum-weight matching each iteration (a hard-EM loop,
converging in ≤6 iterations). Chen & Mooney extend this to real RoboCup soccer commentary paired with
an unaligned symbolic game-state stream, learning a bidirectional synchronous-CFG-style parser+generator,
plus a separate "what's worth narrating" component.

**Achieved.** Near-fully-supervised F-measure despite training-time ambiguity up to 7 candidate MRs per
sentence; human-quality-rated generated soccer commentary from real (if narrow-domain) data.

**Limits.** Simple, mostly one-predicate-per-utterance semantics (per the 2024 construction-grammar
survey's classification); single narrow domain per demonstration; batch iterative retraining, not truly
online/incremental.

### B5. Cangelosi's "sensorimotor toil vs. symbolic theft" grounding transfer (Cangelosi & Harnad 2001;
Cangelosi & Riga 2006)

**Mechanism.** Neural-network/robotic learner first grounds basic action/object categories via direct
embodied sensorimotor training ("toil"). Higher-order/abstract words are then acquired cheaply not via
more embodied training but via **compositional linguistic definitions over already-grounded primitives**
("theft") — the new word's grounding is inherited from its components' prior grounding. RL variants tie
this to communicative/task reward instead.

**Achieved.** Small closed vocabularies of basic + composite action words on simulated humanoid (iCub)
or two-robot setups.

**Limits.** Only small vocabularies; composite-word definitions must be handed in as curated strings
(no autonomous discovery of which primitives compose a new meaning); relational binding across many
grounded entities beyond hierarchical action-composition is limited. This IS one of the few threads
that grounds verbs/actions (not just nouns), which is relevant to "learning relations."

### B6. Modern RL grounded agents: DeepMind Hermann et al. 2017 and BabyAI (Chevalier-Boisvert et al. 2019)

**Hermann et al.:** vision+language+action modules trained end-to-end with A3C in a 3D simulated world;
**RL reward alone produced no learning at all** — grounding only emerged once unsupervised auxiliary
losses (next-frame prediction, language-reconstruction-from-vision) were added. With those, the agent
learned ~59+ words with ~90% zero-shot compositional generalization to novel word combinations.

**BabyAI:** headline negative result — imitation learning needed **8,431 to 408,500+ demonstrations**
depending on instruction complexity, and RL underperformed imitation by 2-10x; the paper's own stated
conclusion is that mainstream deep learning needs "an improvement of at least three orders of magnitude"
in sample efficiency before human-in-the-loop compositional grounded-language training is practical.

**This is the strongest available honest ceiling: as of 2019, the mainstream ML literature's own
verdict is that compositional grounded language learning is NOT sample-efficient** — a load-bearing
caveat against any claim that a dictionary-grounded relation-learner will be cheap or fast by default.

### B7. Construction-grammar induction (grounded, developmentally-inspired): Chang's Embodied
Construction Grammar / Bayesian Model Merging (2004/2008 dissertation); Alishahi & Stevenson 2008;
Bannard/Lieven/Tomasello 2009

Chang's mechanism: mapping operators (simple + relational mapping) create item-based relational
constructions; reorganization operators (merge/join/split) generalize/factor them under an MDL
objective — incrementally builds relational constructions bottom-up in a way that matches child
developmental stages (throw-ball + throw-block → throw-toy, etc.). **Closest fit for incremental,
relational, developmentally-faithful grammar learning** — but hand-given lexicon/ontology, no grounding
in an actual perceptual/situation model (meanings are pre-annotated, not abductively inferred), and
toy-scale (~100-200 tokens). A 2024 survey of 31 such models (Doumen, Schmalz, Beuls & Van Eecke,
arXiv:2407.07606) concludes explicitly: **no model to date simultaneously achieves broad-domain scale,
genuinely usage-based learning from raw situated interaction, and full bidirectional constructionist
properties** — this is a confirmed, current (2024) literature gap, not a strawman.

### B8. Grounding verbs/relations specifically in perception/motor primitives: Siskind 1995/2001
(force-dynamic event-logic), Bailey 1997 (x-schema motor grounding)

Siskind grounds verb meaning as a **temporal-logic formula over tracked relational primitives**
(contact/support/attachment) extracted from block-manipulation video; Bailey grounds action verbs as
parameter settings of concurrent/sequential motor-control programs on a simulated arm. Both explicitly
ground relations/predicates (not object nouns), at small block-world/simulated-arm scale, with hand-
engineered low-level relational-feature extraction.

### B9. SHRDLU (Winograd 1972) — the cautionary baseline

Hand-coded procedural semantics over a hand-built blocks-world microworld; zero learning. Universally
cited as the demonstration that hand-authored grounding is brittle and doesn't transfer — the historical
motivation for every learned approach above (B1-B8), not itself a candidate mechanism to adopt.

**Confirmed literature gap (flag for follow-up, not covered by this scour):** no paper was found across
all four sub-scans that grounds relations extracted from free TEXT/dialogue against an independent
world/ontology model the way B3 (Artzi & Zettlemoyer) does for instruction-following. The closest hits
are interactive-dialogue grounding systems (attribute/object-property grounding through robot dialogue),
not general relation-extraction-from-text-against-a-KB. **This scour did not search the KB-distant-
supervision literature (Mintz et al. 2009 "Distant supervision for relation extraction without labeled
data," and its many descendants) — that line is the closest published analog to "learn relations from
text validated against an existing symbolic knowledge base" and should be the very next drill**, not
one of the frameworks surveyed here.

---

## Cheap decisive test

Two audits, zero compute, binary/inspectable outcomes — check the current implementation against the
two mechanisms the literature specifies precisely and ours may or may not yet have:

1. **Settling-vs-single-pass audit (comprehension side).** Does our "integrate into situation model"
   step build a weighted candidate set and iterate to a fixed point (CI/Landscape-style constraint
   satisfaction — repeated matrix-multiply-and-renormalize until stable), or does it take a single
   greedy/argmax score per chunk? Read the actual integration code path.
2. **Boundary-trigger audit (comprehension side).** Is a new "situation model" instance started only
   on a fixed chunk-size schedule, or on an explicit prediction-error threshold (SEM-style) that can
   fire mid-chunk or skip a boundary if the model is still predicting well? Read the chunking/reset logic.
3. **Grounding-signal audit (grounding side).** Does relation-learning currently use pure co-occurrence/
   frequency counting (Frank-Goodman/Yu-Ballard-tier — thin, noun-analog-only per B2), or does it check
   a candidate relation's parse against an execution/validation-style query on the ontology (Artzi-tier
   — B3, the only surveyed mechanism demonstrated to learn relations, not just nouns, from weak
   supervision)?

## Falsifiable predictions

**HARD-PASS** (current design already matches or exceeds the closest named precedent on that axis):
- Audit 1 finds iterative fixed-point settling over a weighted candidate graph, not single-pass
  scoring → comprehension integration is at CI/Landscape-parity.
- Audit 2 finds an explicit prediction-error-triggered boundary/reset mechanism → comprehension
  segmentation is at SEM-parity (the most advanced precedent found).
- Audit 3 finds an execution/validation-style check against the ontology (parse → query → match/
  mismatch), not just co-occurrence counting → grounding is at Artzi-parity (the only precedent that
  learns relations, not just nouns, from weak supervision).

**HARD-FAIL** (current design is below the surveyed literature's own baseline — should not be marketed
or reasoned about as matching a 1978-2020 computational mechanism until built):
- Audit 1 finds single-pass greedy scoring with no iteration to a fixed point → integration is
  currently BELOW 1988-era CI; the "compress-and-carry loop" framing is aspirational, not implemented,
  on this axis.
- Audit 2 finds only fixed-size/fixed-schedule chunking with no error-triggered boundary logic →
  segmentation is currently below the 2007-2020 event-segmentation literature's own baseline.
- Audit 3 finds pure co-occurrence/frequency counting for relations with no validation/execution check
  → grounding is currently at the THINNEST end of the surveyed spectrum (noun-analog cross-situational
  level per B2), not yet at the relation-learning level (B3) that is the actual target capability.

## Cross-thread synthesis

Prior 07-17/07-18 drills (`research_brain_efficiency_language_acquisition_substrate_map_2026-07-17.md`,
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`,
`research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md`) independently
converged, via biology + general-ML literature, on three substrate primitives (predictive-error scoring,
schema-fit gating, recurrence-before-consolidation) and diagnosed the missing piece as variable-cost,
reactivation-capable, schema-gated consolidation. **This scour closes the loop by naming the exact
cognitive-science precedents for those same mechanisms**: predictive-error scoring ≈ surprisal
(Hale/Levy, A5) and SG-state-change (Rabovsky, A3); schema-fit gating ≈ SEM's Bayesian-nonparametric
schema selection (A4); and the still-missing "when to start a new model vs. keep updating" decision is
precisely SEM's error-triggered event-boundary mechanism, not yet cited in the prior drills. On the
grounding side, the prior drills did not touch grounded-language-acquisition literature at all — this
scour supplies that missing half and identifies the single most load-bearing adjacent gap (KB-distant-
supervision, Mintz et al. 2009) as the next drill, since none of the 4 sub-scans' frameworks (Steels,
cross-situational, Artzi/Zettlemoyer, sportscasting) actually match our "ontology as world" setup as
closely as distant supervision would.

## Substrate-product implications

Not a publication opportunity — this scour is about not re-deriving 45-year-old mechanisms from scratch
and about being honest with ourselves about where the frontier already sits. Concretely for the build:
(1) adopt CI's construction/integration vocabulary and the 3-level surface→textbase→situation-model
stack as the design vocabulary for our loop, crediting Kintsch/van Dijk explicitly in any internal docs;
(2) if audit 1/2 come back HARD-FAIL, prioritize building fixed-point settling + error-triggered
boundary detection before claiming the loop is "working" — these are the two concrete, well-specified,
already-solved-in-the-literature pieces we may be missing, not open research problems; (3) for grounding,
prioritize a validation/execution-style relation-learning signal (Artzi-style: does a candidate relation's
parse check out against the ontology) over pure co-occurrence counting, since co-occurrence-only is
proven in the literature to plateau at noun-level grounding; (4) do NOT market "learns compositional
grounded relations" as if it were cheap — BabyAI's own 2019 verdict is that mainstream ML needs 3 orders
of magnitude more sample-efficiency for this exact capability, so any claimed sample-efficiency advantage
from the dictionary-grounding approach is the single highest-value, highest-scrutiny claim to make and
must be tested hard before repeating externally.

## Citations (verified count)

Approximately 55 distinct sources were surfaced and cross-checked (paper title + author + year, with a
working link found via WebSearch/WebFetch) across the four parallel sub-scans: ~13 in the CI/situation-
model scan, ~14 in the surprisal/predictive-reading scan, ~15 in the grounded-learning-I scan, ~15 in the
SHRDLU/denotational-parsing/construction-grammar scan (including one full-paper reads of Kate & Mooney
2007, Artzi & Zettlemoyer 2013, Clarke et al. 2010, and the 2024 construction-grammar survey). Not
independently re-verified by this synthesis pass beyond the sub-agents' own link retrieval — treat as a
lit-scan-tier citation count, not a certified bibliography.

---

P_deflated:
- P(the comprehension-loop concept itself is theoretically novel) = 0.10 (very low — it is essentially
  Kintsch/van Dijk CI, a 45-year-old named model; deflated per calibration rule from an already-low
  naive estimate).
- P(a VSA-native, glass-box, at-scale instantiation of that loop is a genuine, currently-unclaimed
  contribution) = 0.40 (capped near the 0.50 novel-synthesis ceiling; every prior computational
  instantiation found — CI, Landscape, Sentence Gestalt, SEM — is either hand-authored/opaque-RNN or
  small-scale/synthetic-corpus; an inspectable, at-scale version would be new, but this is unverified
  and the calibration penalty applies).
- P(grounded relation-learning from an ontology-as-world is already solved by surveyed literature,
  wholesale adoptable with no new work) = 0.15 (low — closest precedent, Artzi & Zettlemoyer, needs a
  hand-built seed lexicon + narrow single-domain demonstration; general relation-learning from free text
  against a KB was NOT found in this scour and is flagged as an open gap requiring its own drill).
