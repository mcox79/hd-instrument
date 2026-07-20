# Learned glass-box MENTION / ENTITY detector — blueprint + honest gap-map

Research drill, 2026-07-18. Biology-led; credits prior work (learn-from + build-on, never "take").
Grounds the NEXT THRUST after v4 HARD_FAIL VET `ada2392b`: the reader collapsed on REAL
grade-2 text and the root was localized to MENTION/ENTITY DETECTION (hand-rule detector grabbed
"great","brown","more","robin","bugs" as entities -> garbage mentions STARVED the built-and-verified
role-assigner + coref + composition downstream; RELF1 0.217, precision 0.153). Scoping only —
NO cell dispatch, NO push.

Prior-arc concept-check (mandatory pre-drill): substrate_query "mention entity detection noun
phrase chunking parser referent" -> top hits = FrameNet "Mention" frame (cosine 0.43, just the
lexeme) + `research_to_exp_dev_BANKED..RESONATOR_COREFERENCE_2026-06-11.md` (cosine 0.37). That
prior note is DOWNSTREAM (resonator coref GIVEN clean mentions) — a consumer, not the detector.
**Prior arc work on a LEARNED mention/entity DETECTOR: NONE. The detector is unbuilt.**

---

## TOP-LINE

Mention detection is the RIGHT first component of the learned parser, and it is very likely the
cheapest high-leverage fix — but "un-starves the built machinery" is a HYPOTHESIS, not a fact yet.
The biology says entity identification is a real, dedicated, *learned* subsystem (determiner-frame +
grounding/concreteness + given-new), not an epiphenomenon of full parsing — so building it as a
standalone first component is brain-faithful, not a shortcut. The engineering prior art is mature and
transparent (base-NP chunking, ~93-94 F1 on *harder* newswire with word+POS window features; classic
coref does mention detection as an explicit high-recall-then-filter stage). Grade-2 narrative is
*easier* than the benchmark genre (short, concrete, non-recursive NPs), and the substrate has a
glass-box asset the newswire chunkers lacked: an exact grounding/concreteness lookup over its concept
atoms, which is precisely the neural axis the brain uses to tell a referring THING from a modifier.

**RECOMMENDED FIRST MOVE (cheap, before building the learned detector): the ORACLE-MENTION
upper-bound test.** Inject GOLD mention spans into the existing pipeline, hold role-assigner/coref/
composition fixed, measure RELF1. This bounds the prize: if oracle mentions -> RELF1 recovers to good,
mention-starvation is CONFIRMED the bottleneck and the learned detector is worth building; if RELF1
stays poor, the downstream has its OWN real-text failures and a mention detector alone will not
un-starve it. Run the oracle first (info-ceiling-before-fix-cell discipline), THEN build the learned
detector against that ceiling.

---

## (a) BIOLOGY — how the brain identifies referring entities

**Referential tracking is a dedicated subsystem keyed on determiners + NP structure, not word-by-word.**
The determiner system together with sentential grammar orchestrates the interplay of NP types that
jointly build referential coherence over narrative time: an *indefinite* NP ("a robin") introduces a
NEW discourse entity; a *definite* NP ("the robin") refers back to an existing one (given/new). The
brain instantiates and then TRACKS "discourse entities" — abstract referents — as narrative unfolds.
This maps directly onto our overlay's entity instantiation (state-of-mind arc): the same object the
overlay wants to instantiate is the object the brain's referential system builds.
([Kaan/Van Berkum-tradition ERP work on old vs new referents](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2019.00398/full);
[ERPs reflect discourse-referential processing](https://scispace.com/pdf/event-related-brain-potentials-reflect-discourse-referential-c919cfl4rm.pdf))

**Head noun + modifiers = ONE referent (exactly our failure mode).** The entity introduced by a
*major constituent* of a sentence is more accessible as a referent than entities introduced by
*component* NPs embedded inside it — the brain prioritizes the whole-NP referent over its parts
("the little brown robin" is ONE accessible entity; "brown" is not a competing referent).
([Processing of Reference and the Structure of Language: complex NPs, Lang. & Cog. Processes](https://www.tandfonline.com/doi/abs/10.1080/016909699386266))
Referential AMBIGUITY (an NP that could pick out two candidates) elicits a frontally-dominant sustained
negativity (the "Nref") ~300-400 ms after noun onset — evidence the referential machinery fires fast
and automatically. Plural referents recruit extra bilateral superior-parietal integration (multiple
representations to track) — reference is a genuine tracking/binding load, not lexical lookup.
([neural representation of plural discourse entities](https://www.sciencedirect.com/science/article/abs/pii/S0093934X14001114))

**Entity vs modifier/predicate — grounding/concreteness is the neural discriminator.** Concrete,
imageable nouns (a THING you can point to) elicit larger N400/N700, faster responses, and recruit
sensorimotor grounding relative to abstract/relational words. This concreteness axis is a real neural
signature separating referring concept-nouns from abstract modifiers, quantifiers ("more"), and
predicates. So the brain's "is this an entity?" decision fuses TWO cues: syntactic frame (determiner
context, NP position) AND grounding (does this token evoke a grounded, pointable concept?). Our
hand-rule detector had NEITHER cue reliably — it grabbed "great","brown","more" because it lacked the
grounding gate and the determiner-frame gate.
([Concreteness ERP/behavioral effects, lexical decision](https://www.sciencedirect.com/science/article/abs/pii/S0093934X13000217);
[fine-grained concreteness effects across tasks, ERP](https://pmc.ncbi.nlm.nih.gov/articles/PMC12100582/))

**It is LEARNED and usage-based, not innate rules.** Children detect distributional regularities in
word strings from ~12 months. Determiners ("the","a","this") are the single most reliable distributional
cue that following material is a noun/NP — the most frequent noun contexts contain a function-word,
especially a determiner. By 14 months infants treat new nouns in referential contexts as naming
object-KINDS, fusing distributional and grounded (semantic) cues (joint distributional + semantic
bootstrapping). The adult system is a usage-based CONSTRUCTION INVENTORY built by entrenchment of
frequent frames — which is exactly why a LEARNED detector (determiner-frame + distributional slot +
grounding), not a hand-rule, is the brain-faithful design.
([Ambridge et al., why UG needn't be assumed](https://sites.socsci.uci.edu/~lpearl/courses/readings/AmbridgeEtAl2014_LanguageUG.pdf);
[When Meaning Is Not Enough: distributional+semantic cues in child-directed speech](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5516671/);
[developmental origins of syntactic bootstrapping](https://pmc.ncbi.nlm.nih.gov/articles/PMC7004857/))

## (b) GLASS-BOX ENGINEERING PATH — build-on + credit

The task has a mature, transparent (non-LLM, inspectable-feature) prior art. Build on it, credit it.

- **Abney (1991) — chunks.** A chunk = a non-recursive phrase from the parse tree ending in the head
  of the phrase. The "base NP" is the non-recursive core of a noun phrase. This is the exact unit we
  want: the referring NP without the recursive machinery. (Abney, "Parsing by chunks", 1991.)
- **CoNLL-2000 shared task (Sang & Buchholz, 2000)** — the standard, still-cited benchmark for chunking;
  defines the BIO/IOB span-labeling formulation (Begin/Inside/Outside tags) we would reuse.
  ([Intro to the CoNLL-2000 shared task](https://arxiv.org/pdf/cs/0009008))
- **Transparent LEARNED chunkers and their realistic accuracy (the honest numbers):**
  - Memory-based shallow parsing (Daelemans, Buchholz, Veenstra / Sang) — **NP-chunking F1 ≈ 93.8 on WSJ**,
    features = word + POS in a ±4 window (18 features), fully inspectable exemplar retrieval.
    ([Memory-Based Shallow Parsing, JMLR 2002](https://www.jmlr.org/papers/volume2/tks02a/tks02a.pdf))
  - CoNLL-2000 winning system (Kudo & Matsumoto SVMs) — **F1 ≈ 93.48**, window of words+POS+surrounding tags.
  - CRF chunkers (Sha & Pereira) — **low-90s F1**, arbitrary transparent features + global sequence consistency.
  - (BiLSTM-CRF reaches ~97 but that is neural; we stay glass-box and take the ~93-94 transparent tier as
    the credible target on *harder-than-ours* text.)
    ([Shallow parsing with CRFs](https://www.scribd.com/document/788354436/Shallow-Parsing-with-Conditional-Random-Fields))
- **Mention detection in classic coref (Lee et al. 2013, Stanford deterministic sieve).** Mention detection
  is an EXPLICIT upstream stage: a HIGH-RECALL algorithm selects ALL NPs + pronouns + named-entity mentions,
  then precision-oriented sieves/filters remove non-mentions. Design lesson we adopt: the *detector favors
  recall* (the linker/downstream cannot recover a missed mention), and precision is bought back downstream.
  ([Deterministic coreference, entity-centric precision-ranked rules, Comp. Ling. 2013](https://direct.mit.edu/coli/article/39/4/885/1463/Deterministic-Coreference-Resolution-Based-on);
  [mention detection survey](https://dl.acm.org/doi/10.1007/s10489-021-02878-2))

**The glass-box recipe for our substrate:** BIO span-labeler (learned, transparent — CRF/perceptron/
memory-based exemplar, NOT an LLM) over grade-2 tokens, features =
{ determiner/function-word frame (tiny closed class), distributional slot signature, and —
substrate-native — a GROUNDING GATE: is this token a grounded concrete concept-noun in our concept
atoms? }. High-recall candidate generation (all determiner-headed spans + grounded nouns + pronouns)
then a learned/transparent filter. Head-match + span metrics.

## (c) SUBSTRATE STRENGTH vs GAP

STRENGTH
- **Grounding gate is native and exact.** The concreteness axis the brain uses to separate entities from
  modifiers is, for us, a deterministic glass-box lookup over concept atoms (WordNet/FrameNet/concept index):
  "is this token a grounded, pointable concept-noun?" Newswire chunkers had no such feature — we have the
  brain's discriminator for free. This should directly kill the "great/brown/more" false positives.
- **Determiners are a tiny closed class** — the strongest distributional cue is trivially learnable/encodable.
- **Downstream consumers are BUILT + verified** (learned role-assigner, resonator coref, composition) and
  waiting on clean mentions — the fix is upstream of already-working machinery.
- **Transparent sequence labeling** (BIO) is a small, fully-inspectable learned model — glass-box by construction.

GAP
- **No in-substrate POS tagger.** The classic chunker's dominant feature is POS. We must either (i) lean on
  grounding + determiner-frame + distributional slot as a POS-surrogate, or (ii) learn a lightweight POS/word-class
  jointly. This is the single biggest port risk and the honest weak point.
- **No gold mention spans on grade-2 text** for training/eval — must build a small, can't-be-gamed gold set
  (hand-annotate, or adapt an annotated children's/simple-narrative corpus if one exists).
- **Genre shift.** The ~93-94 F1 numbers are WSJ newswire with good POS. Cross-genre POS/chunk degradation is
  real and documented. MITIGANT: grade-2 is *simpler* than WSJ (short sentences, concrete vocab, almost all
  base-NPs, little recursion/coordination) — the very complexity that hurts is largely absent, and base-NP
  chunking is the non-recursive case. Net: unfamiliar genre but easier task; do not assume newswire F1
  transfers, measure it.
  ([POS/chunk cross-genre degradation](https://arxiv.org/pdf/1905.08920))

## (d) FAIR-TEST DESIGN (design-gate compliant)

- **Gold mention spans** on a held-out set of REAL grade-2 passages (the same text v4 collapsed on),
  hand-annotated; keep a clean unseen slice.
- **Metric:** mention span precision / recall / F1, reported BOTH exact-span and relaxed head-match.
- **CAN-FAIL baseline (mandatory, floor):** the CURRENT hand-rule detector (the one that grabbed
  "great/brown/more"); report its P/R/F1 — this is the number to beat. Plus two reference baselines:
  "every content word is a mention" (high-recall/low-precision ceiling on recall) and "grounding-lookup
  noun only" (isolates the grounding gate's contribution).
- **Telemetry-sensitive discriminator:** perturb the grounding gate / determiner feature -> F1 MUST move
  (verify before tiering; not analytically pinned).
- **Difficulty ON:** REAL grade-2 text, not smoke/toy text; no frac=0 fuzzing.
- **ONE variable:** learned-vs-hand-rule detector, downstream pipeline held FIXED -> measure whether clean
  mentions un-starve role-assignment/coref/composition (RELF1 delta). No confound.
- **Info-ceiling arm (run FIRST):** GOLD mentions injected (oracle) with downstream fixed -> the RELF1 this
  reaches is the UPPER BOUND the learned detector can deliver; the learned-detector RELF1 is then read
  against that ceiling, not against perfection.

## (e) HONEST GAPS + is this the RIGHT first component?

**YES — mention detection is the correct first learned-parser component**, on four grounds: the VET
localized the root here; it is a well-posed, well-benchmarked, transparent-learnable task (~93 F1 prior
art on harder text); it is UPSTREAM so one fix feeds clean input to THREE built consumers (coref
antecedent pool, role-assigner argument slots, relation-extraction args); and it is independently
gold-testable without needing full-parse gold. Building it standalone is brain-faithful (biology says
entity ID is its own learned subsystem), not a shortcut.

**Honest caveats (caveat-interpretation discipline — these are hypotheses pending VET):**
1. **"Un-starves the machinery" is NOT yet proven.** Clean mentions are NECESSARY but may not be SUFFICIENT:
   once fed clean mentions, the role-assigner/composition may surface their OWN real-text failures
   (attachment, PP-attachment, verb argument structure) that were previously MASKED by mention garbage.
   The oracle-mention test is designed to measure exactly this — the RELF1 delta tells us how much was
   mention-starvation vs deeper parse gaps. Do not claim "cheapest fix solves it" until the oracle arm lands.
2. **POS-surrogate risk.** If grounding + determiner-frame + distributional slot cannot substitute for POS
   on grade-2 text, we inherit a joint POS-learning problem — larger than "just mention detection".
   Grade-2 simplicity is the mitigant but must be measured.
3. **Learned mention-detector vs full learned parse.** Mention detection is the right FIRST piece, but the
   long-game (glass-box learned reading, per the 07-18 pivot) is a full learned, self-improving parser.
   Mention detection is the wedge that un-blocks the built pieces and validates the learned-glass-box
   approach on the component where we already know the wall is; it is not the whole parser.
4. **Brain-check on outcome (do not pre-assume):** the brain's good-enough parsing also produces confident
   wrong guesses (spurious firing) — expect the learned detector to have a real precision/recall envelope,
   not perfection. If grade-2 mention detection hits a genuine wall even with the grounding gate, the brain
   likely hits the SAME wall and the fix becomes substrate-native (Frontier-2), not brain-faithful.

### Recommended sequencing
1. **Oracle-mention upper-bound cell** (cheap, no new model): inject gold mentions, downstream fixed,
   measure RELF1 ceiling. Bounds the prize + confirms/refutes the mention-starvation hypothesis.
2. If ceiling is good -> **build the learned glass-box BIO mention-detector** (grounding gate + determiner
   frame + distributional slot; high-recall-then-filter), fair-tested against the hand-rule floor on gold
   grade-2 spans.
3. Read learned-detector RELF1 against the oracle ceiling; the gap = detector quality headroom, the ceiling
   itself = how much of the v4 collapse was mention-starvation.

---

### Sources
- Discourse referents / determiners / old-vs-new: [Frontiers ERP old vs new referents](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2019.00398/full), [ERPs reflect discourse-referential processing](https://scispace.com/pdf/event-related-brain-potentials-reflect-discourse-referential-c919cfl4rm.pdf)
- Complex NP / head-vs-component accessibility: [Processing of Reference and the Structure of Language](https://www.tandfonline.com/doi/abs/10.1080/016909699386266)
- Plural discourse entities (parietal tracking load): [neural representation of plural discourse entities](https://www.sciencedirect.com/science/article/abs/pii/S0093934X14001114)
- Concreteness / grounding as entity discriminator: [ERP/behavioral concreteness in lexical decision](https://www.sciencedirect.com/science/article/abs/pii/S0093934X13000217), [fine-grained concreteness ERP across tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC12100582/)
- Usage-based / distributional acquisition: [Ambridge et al. 2014](https://sites.socsci.uci.edu/~lpearl/courses/readings/AmbridgeEtAl2014_LanguageUG.pdf), [When Meaning Is Not Enough](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5516671/), [developmental origins of syntactic bootstrapping](https://pmc.ncbi.nlm.nih.gov/articles/PMC7004857/)
- Chunking prior art: [CoNLL-2000 shared task intro](https://arxiv.org/pdf/cs/0009008), [Memory-Based Shallow Parsing JMLR](https://www.jmlr.org/papers/volume2/tks02a/tks02a.pdf), [Shallow parsing with CRFs](https://www.scribd.com/document/788354436/Shallow-Parsing-with-Conditional-Random-Fields)
- Mention detection in coref: [Deterministic coreference, precision-ranked rules](https://direct.mit.edu/coli/article/39/4/885/1463/Deterministic-Coreference-Resolution-Based-on), [mention detection survey](https://dl.acm.org/doi/10.1007/s10489-021-02878-2)
- Cross-genre POS/chunk degradation: [domain adaptation for POS tagging of noisy text](https://arxiv.org/pdf/1905.08920)
