# Research drill — Relation-comprehension reader: thematic roles + glass-box prior art (2026-07-18)

Biology-led drill grounding the CURRENT thrust: reading GROWS RELATIONS among already-known
words. Question: how does the brain assign the arguments of a verb to their roles ("who did what
to whom"), and what glass-box (non-LLM) prior art exists for extracting relations/propositions
from SIMPLE text that we can BUILD ON? Deliverable = blueprint + honest gap-map for a glass-box
relation-comprehension reader.

Substrate-KB concept-query first (USER-locked discipline): top hits weak (cosine ~0.33: generic
"argumentation", wordnet "part_to_whole_relation", one streaming-extraction drill note). **Prior
arc work on glass-box thematic-role / relation-comprehension reading: NONE.** Closest referent =
the project's prior hand-rules extraction (~0.44 on COMPLEX textbook prose). This is a fresh
concept for the arc.

Lit-scan calibration penalty applied throughout (P estimates deflated 0.15–0.25; novel-synthesis
P capped 0.50). Prior work is credited to build ON, never "taken".

---

## TOP-LINE

1. **The brain does NOT parse-then-interpret; it assigns thematic roles incrementally from
   CONVERGING, WEIGHTED cues** — word order, animacy, case/morphology, prepositions, verb bias,
   real-world plausibility all vote in parallel (competition model). "The dog bit the man" vs
   "the man bit the dog" is disambiguated by WORD ORDER in English; in a case-marking language the
   morpheme carries it. The neural read-out (N400 = fit / retrieval, P600 = structural
   reanalysis / conflict-resolution) shows role assignment is a two-track process that can DETECT
   its own errors (the "semantic P600" on reversal anomalies like *the meal that the diner ate*).
   This is the biology to imitate: **role assignment = weighted multi-cue competition + a
   conflict/repair signal**, not deterministic parsing.

2. **The core operation IS binding** — the "who did what to whom" problem is textbook Jackendoff /
   the neural binding problem, and it is precisely the operation classical connectionism could NOT
   do cleanly and that VSA was built to solve (Gayler 2004, "VSAs answer Jackendoff's challenges").
   **Our native bind/unbind/resonator is the mechanism the field reaches for.** Frontier-2
   advantage is real here, with a caveat (below): binding is our strength; the GAP is text → the
   correct role-filler assignment (the "encoder"), not storing/querying it once assigned.

3. **Glass-box extraction on SIMPLE SVO is MUCH more tractable than on complex prose.** The project's
   ~0.44 was on complex textbook prose; the OpenIE literature is explicit that complexity (multiple
   clauses, shared arguments, infinitival subjects) is where transparent extractors fail, and that
   *restructuring complex → simple clauses* is the standard fix. Grade-1 SVO is already in the
   "simple clause" regime where rule-based + shallow-parse extractors do well. Realistic glass-box
   accuracy on grade-1-like SVO: **plausibly 0.80–0.95 on clean single-clause declaratives**, with
   coref and the 2-relation composition being the real difficulty drivers — NOT the SVO extraction
   itself. (Deflated estimate; needs a fair cell to confirm, see §D.)

4. **Recommended build:** a glass-box SRL-style reader = shallow dependency/POS cues →
   verb-frame lookup (PropBank/VerbNet-style, but LEARNED not hand-coded per the 07-18 anchor) →
   role-filler BIND on the substrate → proposition written to the situation model → coref overlay
   binds mentions across sentences. This is a **hybrid: brain-faithful multi-cue role assignment,
   substrate-native binding for the representation.** Lead the reader from FIXED hand-rules toward
   a LEARNED role-assigner (the 07-18 glass-box≠hand-rules mandate).

---

## (a) BIOLOGY — how the brain assigns roles + binds fillers

### Thematic role assignment = weighted multi-cue competition (the core)
- **Thematic roles / theta-roles** (agent, patient/theme, recipient/goal, location, instrument…)
  are the argument slots a verb opens. The "thematic hierarchy" (Agent > Recipient > Theme >
  Location…) governs how arguments preferentially map to syntactic positions (subject, object).
- **The brain uses converging cues, weighted by their reliability in the language** (MacWhinney &
  Bates, Competition Model): in English WORD ORDER dominates (pre-verbal NP → agent); in richly
  case-marked languages the CASE morpheme dominates and word order is freer; ANIMACY and real-world
  PLAUSIBILITY bias assignment ("the key opened the door" → key is instrument not agent);
  PREPOSITIONS explicitly tag roles ("to X" → recipient, "in X" → location). This is why *"eggs in
  the nest"* → `in(eggs, nest)` is easy: the preposition is a near-deterministic role tag.
- Implication for us: **role assignment is a scoring/competition over cues, not a parse tree.** A
  glass-box reader can implement this literally as a weighted vote — inspectable, and the weights
  are learnable from data (Competition Model is itself a learning theory).

### Syntactic bootstrapping + construction grammar (how the mapping is LEARNED)
- **Gleitman's syntactic bootstrapping (1990):** children infer a verb's meaning AND its role
  structure from the SYNTACTIC FRAME it appears in — "the cat meeped the bird" tells you *meep*
  takes an agent + patient before you know what meep means. **Structure-mapping (Fisher):** a
  one-to-one bias — N nouns around the verb ⇒ N participant roles. This is directly relevant: our
  substrate already GROUNDS word meanings up front, so the harder half of bootstrapping is done;
  what remains is the frame → role-count → role-assignment mapping, which is the LEARNABLE part.
- **Construction Grammar (Goldberg):** argument-structure CONSTRUCTIONS are themselves form→meaning
  pairings (the ditransitive "X VERB Y Z" *means* transfer, largely independent of the verb).
  Constructions give a small, enumerable inventory of frames for grade-1 text: intransitive (SV),
  transitive (SVO), ditransitive (SVOO), locative/prepositional (SVO-PP). **A glass-box reader can
  carry this inventory explicitly** — a handful of constructions covers almost all simple SVO.

### Neural signatures + the binding operation
- **N400** (~300–500 ms, centro-parietal negativity): ease of semantic integration / retrieval fit.
  Larger when the filler is a poor semantic fit for the role.
- **P600** (~500–900 ms, posterior positivity): structural reanalysis / conflict resolution. The
  **"semantic P600" on thematic-role REVERSAL anomalies** (*the meal the diner ate*) is the key
  finding: the brain notices when plausibility and syntax DISAGREE about who-did-what and spends
  effort to repair. **Two-track: a fit signal AND a structural-conflict/repair signal.**
- **The binding problem for language** (Jackendoff's challenges; van der Velde & de Kamps
  neurocomputational model): the brain must bind a filler to a role WITHOUT smearing ("man bites
  dog" ≠ "dog bites man" though the same words are active). Classical connectionism's superposition
  smears these; **VSA/HDC was designed to solve exactly this** (Gayler 2004). Role-filler binding
  with schematic knowledge (Marcus-style variable binding) is an active glass-box research line.

### Comprehension = building a proposition / situation model (Kintsch)
- **Kintsch Construction-Integration:** sentences decompose into PROPOSITIONS (predicate-argument
  units with a truth value — literally `fed(Ned, hen)`), which accrete into a **textbase** (network
  of propositions) and then integrate with prior knowledge into a **situation model**. Coref /
  anaphora bind mentions ("she" → hen) to entities ACROSS sentences.
- This is a near-exact spec for our target: text → propositions → a growing relational store, with
  the coref overlay doing cross-sentence entity binding. **Kintsch's proposition = our relation
  triple; Kintsch's situation model = our growing foundation.** We should adopt his vocabulary.

---

## (b) GLASS-BOX ENGINEERING PRIOR ART (build ON + credit; realistic accuracy)

Three transparent, non-LLM traditions, in increasing "openness":

1. **Semantic Role Labeling (SRL) — PropBank / FrameNet / VerbNet.** The canonical "who did what to
   whom" task. Input: sentence + predicate; output: labeled argument spans (ARG0=agent,
   ARG1=patient, ARGM-LOC=location…). **Accuracy (credit CoNLL-2005/2008 lines):** ~78 F1
   span-based (CoNLL-05 metric), ~84 F1 dependency-based (CoNLL-08) for classical/early-neural
   systems; modern ~86–88. Crucially these numbers are on FULL newswire (WSJ/Brown) — hard prose.
   On grade-1 SVO the argument-identification subproblem is far easier. PropBank frame files
   (verb-specific role inventories) are a ready-made, inspectable lexicon we can seed the reader's
   verb-frame table from. **This is the closest existing task to our goal and the one to build on.**

2. **Dependency parsing.** Gives typed head→dependent arcs (nsubj, obj, iobj, obl). For clean SVO,
   the subject/object arcs map almost directly to agent/patient. Transparent, fast, mature
   (transition-based parsers are fully inspectable). A dependency parse + a role-mapping table IS a
   lightweight glass-box SRL for simple text.

3. **Open Information Extraction (OpenIE).** Schema-free (subject, relation, object) triples
   straight from text (TextRunner→ReVerb→OLLIE→ClausIE→Stanford OpenIE→OpenIE6). **Literature is
   explicit and load-bearing for us:** OpenIE systems handle SHORT/SIMPLE sentences well; they FAIL
   on complex grammar (multi-clause, shared arguments, infinitival/clausal subjects); the standard
   remedy is *sentence restructuring* (complex → simplified independent clauses). **This directly
   supports the thesis that grade-1 SVO is a tractable regime and the project's ~0.44 was a
   COMPLEXITY artifact, not a floor on the operation.** ClausIE in particular is rule-based over a
   dependency parse — fully glass-box.

**Realistic glass-box accuracy on grade-1-like clean SVO (deflated):** relation-triple extraction
0.80–0.95 for single-clause declaratives with a known verb; the accuracy killers are (i) coref
resolution (she/it → the right entity), (ii) composing 2 relations across sentences, (iii) any
non-canonical construction (passive "the hen was fed by Ned" flips surface order — needs the
passive construction rule). None of these is a fundamental wall for a glass-box reader; each is a
named, enumerable case. Contrast complex textbook prose (~0.44): there the wall is clause structure,
which grade-1 text does not have.

**Credit:** SRL/PropBank (Palmer, Gildea, Kingsbury); FrameNet (Fillmore); VerbNet (Kipper-Schuler);
OpenIE lineage (Etzioni/Banko TextRunner, Fader ReVerb, Mausam OLLIE/OpenIE6, Del Corro ClausIE,
Angeli Stanford OpenIE); competition model (MacWhinney & Bates); syntactic bootstrapping (Gleitman;
Fisher structure-mapping); construction grammar (Goldberg); propositions/situation model (Kintsch,
van Dijk); binding-problem-for-language (Jackendoff; van der Velde & de Kamps); VSA-answers-
Jackendoff (Gayler); role-filler binding (Marcus; Webb/schematic role-filler).

---

## (c) MAP TO SUBSTRATE — STRENGTH vs GAP

| Sub-operation | Brain / prior art | Substrate today | Verdict |
|---|---|---|---|
| Word meaning grounding | grounded (dictionary/teacher stand-in) | DONE (up-front) | STRENGTH |
| Role-filler BIND (fed·agent·Ned) | binding problem; VSA-native | native bind/unbind/resonator | **STRENGTH (Frontier-2 candidate)** |
| Proposition store (textbase) | Kintsch network | bundle/superposition + store | STRENGTH |
| Cross-sentence coref bind (she→hen) | anaphora resolution | packaged coref overlay | STRENGTH (exists) |
| Situation model accretion | Kintsch integration | growing foundation store | STRENGTH (aligned) |
| **Text → role assignment (the encoder)** | multi-cue competition; SRL | **hand-rules only, ~0.44 on hard prose** | **GAP — the whole game** |
| Construction inventory (SVO/ditransitive/passive/locative) | Goldberg constructions | not represented | GAP (small, enumerable) |
| Conflict/repair (semantic-P600 analog) | N400/P600 two-track | none | GAP (nice-to-have; enables self-correction) |

**Read:** everything DOWNSTREAM of role assignment is a substrate strength (binding, storing,
coref, accretion). The single real GAP is the ENCODER: text → correct role-filler assignment. That
is where the 07-18 pivot points — move it from fixed hand-rules to a LEARNED glass-box role-assigner.

---

## FRONTIER-2 FLAG — is native binding an ADVANTAGE here?

**Qualified YES, but locate it precisely.** The binding literature is unambiguous that role-filler
binding is the hard, unsolved-in-connectionism operation and that VSA is the principled answer
(Gayler; the recent "attention as binding" VSA-reading of transformers). So the REPRESENTATION of
"who did what to whom" is a genuine substrate-native advantage — we get clean, unbind-queryable,
interference-free role-filler structure by construction, where neural nets get approximate/soft
binding. Two honest caveats (per no-over-claim + strategic-reads-run-ahead disciplines):

- The advantage is in STORING and QUERYING the proposition, not in DERIVING it from text. The
  derivation (the encoder) is a separate, still-open problem where we have NO native edge — an LLM's
  soft attention is currently better at the messy cue-integration than our hand-rules. So Frontier-2
  advantage = "the substrate holds who-did-what-to-whom more cleanly once assigned," NOT "the
  substrate reads roles off text better."
- Whether the clean binding *translates into a downstream reasoning win* over a system that just
  stores triples in a table is the empirical question — binding pays off under COMPOSITION and
  MULTI-CONSTRAINT query (ties to the reasoning-theory anchor: resolution scales with #constraints).
  Single-relation storage is homophily-solvable and would NOT showcase the advantage (v3-refuted
  lesson). **Design the demonstrator around 2-relation composition + coref, not single triples.**

Recommendation: build the reader brain-faithful FIRST (multi-cue competition encoder + native
binding), nail it as the baseline, THEN test whether native binding beats a triple-table under
composition — do not lead with the native-advantage claim (nail-the-baseline-first discipline).

---

## (d) FAIR-TEST DESIGN for the relation reader (USER standing: fair every time)

Design gate (can-fail / real-baseline / difficulty-on / one-variable) applied to this task:

1. **Independent gold, not construction-determined.** Gold relations must come from an EXTERNAL
   source (hand-annotated by a different process / a held-out human-labeled slice), NOT emitted by
   the same generator that made the sentences — else a HARD_PASS is tautological
   (synthetic-toy-corpus-construction-determined trap). Prefer real grade-1 readers over a
   self-generated toy grammar for the load-bearing claim.
2. **Real baseline.** Compare against (i) a raw dependency-parse→role-map extractor and (ii) an
   OpenIE tool (ClausIE / OpenIE6) on the SAME sentences. Beating "abstain-all" or a strawman is
   not a result. If a mature OpenIE tool gets 0.9 on our simple SVO, our reader must be measured
   against 0.9, not against zero.
3. **Difficulty actually ON.** Include the cases that make it fail: passives (surface-order flip),
   required coref (she/it), 2-relation composition across sentences, a role-reversal minimal pair
   ("dog bit man" vs "man bit dog") to prove the reader is role-SENSITIVE not bag-of-words. A test
   with frac=0 hardness (all canonical active SVO, no coref) is vacuous.
4. **One variable per arm.** To isolate the encoder from the store, hold the corpus fixed and vary
   ONLY the encoder (hand-rules vs learned); to isolate binding-advantage, hold the encoder fixed
   and vary ONLY the store (native bind vs triple-table).
5. **Two distinct gold types, scored separately:** (a) RELATION-gold (exact triple match, precision
   /recall/F1 — the extraction metric), and (b) COMPREHENSION-Q (answer "who fed the hen?" by
   querying the store — the end-to-end metric). Report both; they can diverge (good extraction, bad
   query, or vice-versa) and the divergence is diagnostic.
6. **Traps to avoid:** (i) counting a triple correct when coref was NOT actually resolved (score
   coref separately); (ii) lexical-overlap shortcuts (the reversal minimal-pair guards this);
   (iii) letting the grounding dictionary leak the answer; (iv) reporting F1 on a corpus where the
   generator only ever produces canonical SVO (difficulty-off); (v) scoring "constructed works" as
   "capability" — a toy corpus where every sentence is trivially parseable proves construction, not
   reading (caveat-interpretation discipline).

---

## (e) HONEST LITERATURE GAPS

- **The combination law for competing role cues is under-specified.** The Competition Model says
  cues are weighted by reliability, but the exact glass-box combination function (weighted sum? max?
  branch/route? — cf. the surprise-axes "integration is a branch not a sum" finding) is not settled.
  We would DEFINE it; that is genuine (capped) novelty, not a lookup.
- **N400/P600 do NOT map one-to-one onto lexical vs syntactic** (the reviews explicitly say this) —
  so a "P600 = repair" analog in our reader is an INSPIRATION, not a validated mechanism to copy
  literally. Don't over-fit the architecture to the ERP labels.
- **Learned-yet-glass-box role assignment is the thin part of the literature.** SRL went neural
  (opaque) for its best numbers; the transparent systems (ClausIE, dependency+rules) are strong on
  simple text but plateau on hard text. The specific target — a LEARNED, self-improving, INSPECTABLE
  role-assigner (the 07-18 mandate) — sits in a genuine gap between transparent-but-static and
  accurate-but-opaque. This is where our contribution would live.
- **No prior art on VSA-native reading of role structure from raw text at grade-1 scale that also
  demonstrates a downstream composition advantage.** The VSA-binding papers assume roles are already
  assigned; the SRL/OpenIE papers assign roles but store in tables. Bridging the two (assign → native
  bind → composition win) is unclaimed territory — the honest novelty, P capped 0.50.

---

## SUGGESTED NEXT BUILD (scoping only — NO dispatch per task)

A glass-box relation-comprehension reader cell, staged:
1. Construction inventory (SV / SVO / SVOO / SVO-PP / passive) as an explicit, inspectable table.
2. Multi-cue role assigner (word-order + preposition + animacy vote) → role-filler BIND on substrate.
3. Situation-model store + coref overlay for cross-sentence binding.
4. Fair eval per §D: real grade-1 sentences, independent gold, ClausIE/OpenIE6 + dependency baselines,
   difficulty-ON (passives, coref, 2-relation composition, reversal minimal pairs), RELATION-F1 AND
   comprehension-Q scored separately.
5. Then the Frontier-2 test: native bind vs triple-table under 2-relation composition (isolate the
   store; hold encoder fixed).

Sequencing per nail-the-baseline-first: brain-faithful multi-cue encoder as the baseline, optimize to
frontier, THEN test the native-binding advantage — do not lead with the native claim.

---

### Sources (credit — build ON, not take)
- SRL / PropBank: [Dependency-based SRL of PropBank (CoNLL-08)](https://dl.acm.org/doi/10.5555/1613715.1613726),
  [Accurate parsing of the proposition bank](https://www.academia.edu/10670845/Accurate_parsing_of_the_proposition_bank),
  [PropBank / SRL history](https://mbrenndoerfer.com/writing/history-propbank-semantic-role-labeling)
- OpenIE simple vs complex: [Survey on Open IE](https://andrefreitas.org/papers/coling-open-survey.pdf),
  [OpenIE from conjunctive sentences (ClausIE-style)](https://www.cse.iitd.ac.in/~mausam/papers/coling18.pdf),
  [Canonical context-preserving OpenIE from complex sentences](https://www.sciencedirect.com/science/article/pii/S0950705123002058)
- N400 / P600 / thematic roles: [Functional role of N400 & P600 (PMC review)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8419728/),
  [ERP correlates of thematic role assignment (active vs passive)](https://www.sciencedirect.com/science/article/abs/pii/S0911604419301290),
  [Semantic reversal anomalies under the microscope](https://www.biorxiv.org/content/10.1101/788976.full.pdf)
- Syntactic bootstrapping / constructions: [Developmental origins of syntactic bootstrapping (Fisher, PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7004857/),
  [Syntactic bootstrapping (Wikipedia overview)](https://en.wikipedia.org/wiki/Syntactic_bootstrapping)
- Kintsch propositions / situation model: [Construction-Integration (Kintsch 1988)](https://condor.depaul.edu/dallbrit/extra/hon207/readings/kintsch-1988-construction-integration.pdf),
  [Text comprehension, memory, and learning (Kintsch 1994)](https://andymatuschak.org/files/papers/Kintsch%20-%201994%20-%20Text%20comprehension,%20memory,%20and%20learning.pdf)
- Binding problem / VSA: [The neural binding problem(s) (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3538094/),
  [VSAs answer Jackendoff's challenges (Gayler)](https://arxiv.org/pdf/cs/0412059),
  [Learning role-filler binding with schematic knowledge](https://arxiv.org/pdf/1902.09006),
  [How the brain solves the binding problem for language (van der Velde & de Kamps)](https://www.researchgate.net/publication/5373533_How_the_brain_solves_the_binding_problem_for_language_A_neurocomputational_model_of_syntactic_processing),
  [Attention as binding: VSA perspective](https://arxiv.org/pdf/2512.14709)
