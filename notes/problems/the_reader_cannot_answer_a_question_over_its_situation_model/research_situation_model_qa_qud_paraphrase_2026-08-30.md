# Research drill 2x: the brain-faithful paraphrase-invariant question / QUD representation (2026-08-30)

Follow-on to `research_situation_model_qa_brain_mechanism_2026-08-30.md` (fix #2, the least-pinned
link: generalization). Full synthesis in the task transcript; durable citable digest here.

## THE ANSWER
The brain does NOT store a question as a phrasing or a bag of cue words. It decomposes every question
into **interrogative force + an ontological ANSWER-TYPE**, and represents the question as the CONSTRAINT
an answer must satisfy (a typed open slot). That decomposition is a LANGUAGE UNIVERSAL, so it is
paraphrase-invariant BY CONSTRUCTION: "where is X" / "in what place/spot/room is X" / "what's X's
location" all yield the type LOCATION independently of shared words. The wh-word carries the type; when
it underdetermines (what/which, or a polar question with no wh-word), the HEAD NOUN + predicate frame
supply it.

## Verdicts (PINNED / OUR-INVENTION)
- **The question representation = a TYPED OPEN SLOT denoting the set/partition of possible answers.**
  PINNED. Hamblin 1973 alternatives; Groenendijk & Stokhof 1984 partition; Roberts 2012 QUD; the
  set-partition hypothesis of wh-comprehension is separately lesionable in agrammatic aphasia
  (J. Neurolinguistics ~2008). Cue-based retrieval (Lewis & Vasishth 2005) is the mechanism that FILLS
  the slot, not the representation.
- **Generalization engine = wh-word ontological answer-type + predicate/head-noun frame.** STRONGLY
  PINNED at the computational level. Interrogative words decompose UNIVERSALLY into a Q-element + a
  Semantic Indicator Element (PERSON/THING/PLACE/TIME/REASON/MANNER/QUANTITY/SELECTION) -- found even in
  sign languages (Cysouw, lexical typology; Leiden typology thesis). Ginzburg co-propositionality =
  paraphrase-invariance defined over answerhood. Underdetermined what/which -> the HEAD NOUN determines
  the type (Li & Roth 2002 COLING; "Classifying What-Type Questions by Head Noun Tagging" COLING 2008).
  The wh->answer-type MAP is legitimately hardcodable BECAUSE it is a universal, not a corpus artifact.
- **Discrete lookup switch = OUR-INVENTION at the neural-implementation level.** The brain does graded
  lexical-semantic activation feeding a retrieval race; emit SOFT, possibly-multiple type activations,
  and make the head-noun resolver graded (distributional similarity to type prototypes), not a hard hit.
- **Anticipatory answer-type maintenance is real.** PINNED. Active filler strategy; Sustained Anterior
  Negativity / LAN maintain an open wh-dependency; retrieval orientation + mPFC completes partial cues
  (lossy -- consistent with the substrate's "partial cue is structurally capped" rule).
- **Polar questions (no wh-word) = a DIFFERENT mode (proposition verification -> truth-value), not a
  dimension in the router.** Acquired later than wh-questions; distinct neural profile. Build separately.
- **Multi-dimensional questions ("why did she go there" = cause+space+entity):** the wh-word sets the
  PRIMARY answer-type; other constituents are SECONDARY retrieval constraints (do not force one winner).

## Reference architecture
SEM (Franklin et al. 2020) role-filler-bound reconstruction; Lewis & Vasishth (2005) retrieval race;
QUALM (Lehnert 1978) + QUEST (Graesser & Franklin 1990) glass-box question-type->retrieval-strategy
precedents (right idea, brittle hand-coding, no graded/paraphrase generalization).

## Build recommendation (applied here)
Replace the cue-table with a **wh-ontology answer-type router**: (1) tiny fixed wh->type map (universal),
SOFT activations; (2) head-noun/predicate resolver via WordNet lexname/hypernymy (glass-box, no LLM) --
'spot'->location, 'moment'->time, 'reason'->cause; (3) polar/verification as a separate path (deferred);
(4) multi-dimensional = primary + secondary constraints. MEASURE two things: paraphrase robustness AND
**novel-cue-word generalization** (held-out cue words never in any table) -- the metric that separates
the wh-ontology router from the cue-table.

IMPLEMENTED + MEASURED in exp_situation_model_qa_v1: wh-ontology router routes novel cue words 1.00 vs
cue-table 0.40 vs exact-keyword 0.00 (all-paraphrase 1.00/0.78/0.39). Confidence the MECHANISM is what
the brain does: high (PINNED). Head-noun resolver via WordNet works; the drill's further rec is to wire
the substrate's own `distributional_meaning_channel` as the resolver (a standing wiring debt).
