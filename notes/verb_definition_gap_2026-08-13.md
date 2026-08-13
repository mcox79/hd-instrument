# The verb-definition gap: why the extracted foundation is noun-only

Scoping pass, 2026-08-13. NOTHING WAS IMPLEMENTED. `hdlab/definitional_extraction.py` was read,
not modified. All counts below are recomputed off disk in this pass; no number is carried over
from a prior note.

---

## 1. THE GAP, VERIFIED OFF DISK

**File counted:** `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`
**Rows:** 2,092 facts / 1,734 unique terms / 1,056 unique genus heads.
Pattern mix: COPULA 648, GLOSSARY_COLON 519, APPOSITIVE 495, CALLED 422, REFERS_TO 8.
(v4 = 1,956 rows, v3 = 1,751 rows; v5 is the current head and the file the 2,092 figure refers to.)

**Taggers used — two independent checks, neither a heuristic guess:**

1. **spaCy `en_core_web_sm`** (statistical PTB tagger), run IN CONTEXT on each fact's
   `source_sentences[0]`. The `definiendum_surface` was aligned to the parse by CHARACTER
   OFFSET (`Doc.char_span(..., alignment_mode="expand")`), and the fine-grained tag of the
   span's syntactic root was read. All 2,092 spans aligned.
2. **WordNet 3.0** (vendored, via nltk) sense profile of the fact's `subject_head_lemma`
   and of the genus head `object`.

**Result — defined term (definiendum):**

| measure | count | of 2,092 |
|---|---|---|
| span-root tagged NN / NNP / NNS / NNPS | 1,916 | 91.6% |
| span-root tagged VB* (any verb tag) | 91 | 4.4% |
| head lemma with a WordNet **verb sense and NO noun sense** | **0** | **0.0%** |
| head lemma with any WordNet verb sense (all also have noun senses: `cycle`, `plant`, `bond`) | 414 | 19.8% |

**Result — genus head (`object`):**

| measure | count |
|---|---|
| tagged NN / NNS / NNP / NNPS | 1,924 |
| tagged VB* | 87 (all VBN/VBG participles inside a reduced relative: `caused`, `resulting`, `associated`) |
| WordNet **verb sense and NO noun sense** | **0** |

**Hand-inspection of the 91 VERB-tagged definienda — all are artifacts, none is a verb definition:**

- *run-on definienda from news text*: `('think mining', 'think', VBP)`, `('modi', 'said', VBD)`,
  `('IFPI Direction', 'said', VBD)` — the COPULA subject span swallowed a matrix verb.
- *deverbal nominals / gerunds tagged VBG but functioning as NOUNS*: `budding`, `splicing`,
  `supercoiling`, `annealing`, `poaching`, `overharvesting`, `hunting`, `cloning` (31 gerund-final
  terms total). `budding: a form of asexual reproduction ...` is a NOUN definition of a nominal.
- *spaCy mis-tags of a lowercase sentence-initial glossary key*: `capsid`, `cellulose`,
  `macromolecule`, `thylakoid`, `prokaryote`, `solute`, `hornwort` all tagged VB purely because
  the "sentence" is `term: definition` with no other finite verb.

**Independent confirmation:** zero of a hand list of 24 classic process verbs
(`respire, metabolize, diffuse, evaporate, digest, replicate, transcribe, translate, oxidize,
secrete, excrete, photosynthesize, ferment, germinate, dissolve, erode, ...`) appears as a
defined term. Two facts have an infinitival definiens (`channelrhodopsin -> "to express the gene
for a protein"`, `nucleosomes -> "to form structures"`) and both are parse errors, not verb
definitions.

### VERDICT: THE 0/2,092 FIGURE HOLDS. The foundation is noun-only.

**But the more useful measured fact is the second-order one.** 119 facts (5.7%) already have a
PROCESS-flavoured genus head — `process` 52, `mechanism` 10, `reaction` 9, `method` 9, `event` 7,
`change` 7, `response` 6, `movement` 6, `technique` 5, `pathway` 2, `cycle` 2, `action` 2, `act` 1,
`activity` 1. So the store DOES contain process concepts. What it contains about them is
`transcription ISA process`. The verbal payload — *copying the information in a cell's DNA into
mRNA* — is discarded by the head-extraction step. **The gap is not only "no verbs as terms"; it
is "the predicate is thrown away even when we do fire on a process definition."**

---

## 2. WHY EACH OF THE 5 PATTERNS CANNOT FIRE ON A VERB DEFINITION

Two causes are shared by all five, then one structural reason each.

**SHARED CAUSE A — the definiendum nominal gate.** `_mk()` line 482 calls
`_is_nominal_or_unknown(dfd_lemma)` and returns `None` if the lemma is in WordNet but has no noun
sense. Verified: `_is_nominal_or_unknown('respire') == False`, `('breathe') == False`,
`('oxidize') == False`. A verb definiendum is refused before any pattern-specific logic runs. This
gate was ADDED DELIBERATELY (self-test case (g), to kill `additionally -> melting`); it is correct
for adverbs and wrong for verbs, and it cannot be relaxed without restoring that regression.

**SHARED CAUSE B — the head walk truncates exactly where the predicate starts.** `definiens_head()`
takes the last noun of the LEADING NP, and `_NP_BOUNDARY` (lines 139-158) contains `of, that,
which, when, to, by, in, through` — i.e. every connector that introduces the verbal content of a
process definition. Verified: `definiens_head("the process by which light energy is converted")`
= `process`; `definiens_head("the process of copying the information in DNA")` = `process`.

| pattern | one-line structural reason it cannot yield a verb definition |
|---|---|
| **COPULA** (`_RE_COPULA`, l.250) | The definiens group is hard-required to open with a determiner — `(?P<dfs>_DET\s+[A-Za-z]...)` — so a bare VP predicate (`occurs when ...`, `converts light into sugar`) can never match; and where it does match a process NP, cause B collapses the definiens to `process`. |
| **GLOSSARY_COLON** (`_RE_COLON`, l.241) | Same `_DET`-initial requirement on the definiens, which is why the textbook's own determinerless glossary style FAILS: `transcription: process through which messenger RNA forms` extracts NOTHING, while inserting "the" makes it extract (verified both ways) — plus `_FINITE_VERB` bans any verb in the definiendum, so a verb key is refused. |
| **APPOSITIVE** (`_RE_APPOS`, l.260) | The appositive slot is an NP bracket by construction — definiendum is a single `[A-Za-z][A-Za-z'\-]{1,30}` token before a comma and the definiens must again be `_DET + NP` — so a comma-set participial or infinitival gloss (`, converting light into sugar,`) is not matchable, and the definiendum token is nominal-gated. |
| **CALLED** (`_RE_CALLED`, l.354) | The naming direction is right for processes (it DOES fire on `The process of removing introns and reconnecting exons is called splicing`), but the antecedent is fed straight into `definiens_head()`, so a VP antecedent is reduced to its container noun: the banked fact is `splicing ISA process`, never `splicing = remove(introns) + reconnect(exons)`. |
| **REFERS_TO** (`_RE_REFERS`, l.361) | The definiendum is a SINGLE token with no space (`{1,30}` with no `\s`), so a multiword verb phrase cannot be the subject; the definiens head is again NP-head, yielding `semantics ISA process`, `perception ISA information`, `reliability ISA ability`. |

---

## 3. SOURCE-TEXT SURVEY — do verb / process definitions exist in expository text?

**Corpora scanned** (mcguffey deliberately excluded per instruction):
`data/corpora/textbook_biology_2e/cleaned/biology_2e.clean.txt`,
`data/corpora/textbook_anatomy_physiology_2e/cleaned/anatomy_physiology_2e.clean.txt`,
`data/corpora/textbook_psychology_2e/cleaned/psychology_2e.clean.txt`.
**72,319 sentences** (25-400 chars, headings stripped). Provenance below is `[FILE:line]` against
those cleaned files. A second, smaller corpus — `data/corpora/process_articles_v1/process_articles.json`,
1,229 sentences — was scanned as a cross-check and is quoted separately.

`extr` = the current extractor banked at least one fact on that sentence; `weak` = at least one
banked fact whose genus head is a contentless container (`process/act/way/means/...`).

| candidate pattern | hits | % of 72,319 | extr | weak |
|---|---|---|---|---|
| P1 `To X is to Y` (true verb gloss) | 46 | 0.064% | 1 | 0 |
| P8 `X means to V` | 18 | 0.025% | 1 | 0 |
| P11 `X means <CLAUSE>` | 57 | 0.079% | - | - |
| P2 `<Nom> is a/the process of V-ing / in which ...` | 101 | 0.140% | 70 | 57 |
| P3 `<Nom> occurs/begins/happens when <CLAUSE>` | 71 | 0.098% | 2 | 0 |
| P4 `... process/mechanism/method by which <CLAUSE>` | 123 | 0.170% | 18 | 16 |
| P5 `<VP/process NP> is called X` | 357 | 0.494% | 225 | 45 |
| P6 `During <process-nom>, <CLAUSE>` | 550 | 0.761% | 17 | 0 |
| P7 `X refers to the process/ability/way ...` | 9 | 0.012% | 6 | 2 |
| P9 `occurs/works by V-ing` | 43 | 0.059% | 1 | 0 |
| P10 `X is the ability/tendency to V` | 19 | 0.026% | 15 | 0 |
| **union of P2/P3/P4/P6/P10** | **818** | **1.13%** | | |

### FINDING 3a (NEGATIVE, and it is a real result)

**Expository science text essentially never defines a bare VERB.** All 46 P1 hits and all 18 P8
hits were read by hand. Genuine verb glosses: **3 in 72,319 sentences (0.004%)**, and one of those
is a Latin-root vocabulary table, not running prose:

- `[ANAT:7545] rectus | straight | To RECTify a situation is to straighten it out.`
- `[BIO:15371] Homeostasis means to maintain dynamic equilibrium in the body.`
- `[BIO:15492] In Latin, omnivore means to eat everything.`

The other 43 P1 hits are PURPOSIVE, not definitional, and would be pure false positives for any
`to X is to Y` rule: *"the role of ethics in scientific research is to ask such questions"*
`[BIO:379]`; *"One way to control gene expression, therefore, is to alter the longevity of the
protein"* `[BIO:6946]`; *"their primary function, which is to limit blood loss"* `[ANAT:13407]`;
*"The most accurate way to determine population size is to simply count all of the individuals"*
`[BIO:21593]`. Likewise 15 of 18 P8 hits are the noun `means` (*"as a means to migrate"*), not the
verb `means`.

**So: if the plan is to harvest verb definitions of the form "to respire is to...", the corpus does
not contain them and the plan fails on data, not on code.**

### FINDING 3b (POSITIVE, and it is the actual opportunity)

**English expository text defines processes by NOMINALIZING them and putting the predicate in a
complement clause.** 818 such sentences (1.13%) in this corpus. This is a linguistic universal of
the register, not an accident of OpenStax: the term is `transcription`, and the verb lives in
`of copying ...` / `by which ... forms` / `occurs when ...`. **The verb content is present and
abundant; it is one syntactic step away from where the current head-extractor stops looking.**

#### Group A — `<Nom> occurs / begins / happens WHEN <clause>` (event-condition definition; 71 hits, extractor gets 2)

1. `[BIO:967]` "Dissociation occurs when atoms or groups of atoms break off from molecules and form ions." -> NOTHING
2. `[BIO:5634]` "Nondisjunction occurs when homologous chromosomes or sister chromatids fail to separate during meiosis, resulting in an abnormal chromosome number." -> NOTHING
3. `[BIO:5703]` "A translocation occurs when a chromosome segment dissociates and reattaches to a different, nonhomologous chromosome." -> NOTHING
4. `[BIO:6554]` "Translation begins when an initiator tRNA anticodon recognizes a start codon on mRNA bound to a small ribosomal subunit." -> NOTHING
5. `[BIO:7773]` "Behavioral isolation occurs when the presence or absence of a specific behavior prevents reproduction." -> NOTHING
6. `[BIO:14709]` "Self-pollination occurs when the pollen from the anther is deposited on the stigma of the same flower, or another flower on the same plant." -> NOTHING
7. `[BIO:18289]` "Abduction occurs when a bone moves away from the midline of the body." -> NOTHING
8. `[BIO:18545]` "Muscle contraction occurs when sarcomeres shorten, as thick and thin filaments slide past each other, which is called the sliding filament model of muscle contraction." -> NOTHING
9. `[BIO:8622]` "Rabies transmission occurs when saliva from an infected mammal enters a wound." -> NOTHING
10. `[BIO:18120]` "Ossification begins as mesenchymal cells form a template of the future bone." -> NOTHING

#### Group B — `<Nom> is a/the process|mechanism|method OF V-ing / BY WHICH <clause>` (101 + 123 hits; extractor fires but banks `process`)

11. `[BIO:1714]` "Magnification is the process of enlarging an object in appearance." -> banked `magnification ISA process`
12. `[BIO:3151]` "Hydrolysis is the process of breaking complex macromolecules apart." -> banked `hydrolysis ISA process`
13. `[BIO:3956]` "Transcription is the process of copying the information in a cell's DNA into a special form of RNA called messenger RNA (mRNA); ..." -> banked `transcription ISA process`
14. `[BIO:15862]` "Ingestion is the process of taking in food through the mouth." -> banked `ingestion ISA process`
15. `[BIO:22219]` "Foraging is the act of searching for and exploiting food resources." -> banked `foraging ISA act`
16. `[ANAT:2292]` "Differentiation is the process by which unspecialized cells become specialized to carry out distinct functions." -> banked `differentiation ISA process`
17. `[BIO:2674]` "Phagocytosis (the condition of "cell eating") is the process by which a cell takes in large particles, such as other cells or relatively large particles." -> NOTHING
18. `[BIO:9389]` "Ammonification is the process by which ammonium ion (NH4+) is released from decomposing organic compounds." -> NOTHING
19. `[BIO:20873]` "Fertilization is the process in which sperm and egg fuse to form a zygote." -> NOTHING
20. `[ANAT:13595]` "Hemostasis is the physiological process by which bleeding ceases." -> banked `hemostasis ISA process`

#### Group C — determinerless glossary line `term: process by/in/through which <clause>` (a large slice of P4; extractor gets ZERO)

21. `[BIO:1676]` "transcription: process through which messenger RNA forms on a template of DNA" -> NOTHING
22. `[BIO:1680]` "translation: process through which RNA directs the protein's formation" -> NOTHING
23. `[BIO:2547]` "facilitated transport: process by which material moves down a concentration gradient (from high to low concentration) using integral membrane proteins" -> NOTHING
24. `[BIO:3262]` "aerobic respiration: process in which organisms convert energy in the presence of oxygen" -> NOTHING
25. `[BIO:5741]` "translocation: process by which one chromosome segment dissociates and reattaches to a different, nonhomologous chromosome" -> NOTHING
26. `[BIO:7669]` "convergent evolution: process by which groups of organisms independently evolve to similar forms" -> NOTHING
27. `[BIO:9278]` "conjugation: process by which prokaryotes move DNA from one individual to another using a pilus" -> NOTHING
28. `[BIO:5802]` "transformation: process in which external DNA is taken up by a cell" -> NOTHING

#### Group D — `During/In <process-nom>, <clause>` (frame elaboration; 550 hits, extractor gets 17)

29. `[BIO:3427]` "During glycolysis, glucose is oxidized to pyruvate while NAD+ is reduced to NADH." -> NOTHING
30. `[BIO:1874]` "During protein synthesis, ribosomes assemble amino acids into proteins." -> NOTHING
31. `[BIO:2770]` "During photosynthesis, plants use the energy of sunlight to convert carbon dioxide gas (CO2) into sugar molecules, like glucose (C6H12O6)." -> NOTHING
32. `[BIO:3151]` "During hydrolysis, water is split, or lysed, and the resulting hydrogen atom (H+) and a hydroxyl group (OH-), or hydroxide, are added to the larger molecule." -> NOTHING
33. `[BIO:5899]` "During DNA replication, each of the two strands that make up the double helix serves as a template from which new strands are copied." -> NOTHING
34. `[BIO:15474]` "During digestion, food particles are broken down to smaller components, and later, they are absorbed by the body." -> NOTHING

#### Group E — `<VP / process NP> is called X` (VP-antecedent naming; 357 hits, 225 extracted but 45 weak-genus)

35. `[BIO:3849]` "This process is called carbon fixation, because CO2 is "fixed" from an inorganic form into organic molecules." -> banked `carbon fixation ISA process`
36. `[BIO:3163]` "This very direct method of phosphorylation is called substrate-level phosphorylation." -> banked `substrate-level phosphorylation ISA method`
37. `[BIO:3171]` "The production of ATP using the process of chemiosmosis is called oxidative phosphorylation because of the involvement of oxygen in the process." -> NOTHING
38. `[BIO:3916]` "Communication between cells is called intercellular signaling, and communication within a cell is called intracellular signaling." -> banked `intercellular signaling ISA cell` (WRONG head)

#### Group F — `X is the ability/tendency TO V` (19 hits, 15 extracted, all banking `ability`)

39. `[BIO:17092]` "Vision is the ability to detect light patterns from the outside environment and interpret them into images." -> banked `vision ISA ability`
40. `[PSY:4946]` "The confirmation bias is the tendency to focus on information that confirms your existing beliefs." -> banked `confirmation bias ISA tendency`
41. `[ANAT:460]` "Responsiveness is the ability of an organism to adjust to changes in its internal and external environments." -> banked `responsiveness ISA ability`

#### Group G — `X means <CLAUSE>` (57 hits, mostly anaphoric "This means that ..." noise; the real ones)

42. `[PSY:4218]` "Reinforcement means you are increasing a behavior, and punishment means you are decreasing a behavior."
43. `[PSY:5108]` "Standardization means that the manner of administration, scoring, and interpretation of results is consistent."
44. `[BIO:8043]` "TSD means that individuals develop into males if their eggs are incubated within a certain temperature range, or females at a different temperature range."
45. `[ANAT:11605]` "Anosmia means that food will not seem to have the same taste, though the gustatory sense is intact, and food will often be described as being bland."

#### Cross-check corpus `process_articles_v1` (1,229 sentences) — same shape, smaller

46. `[combustion/Combustion]` "Incomplete combustion occurs when the supply of air is limited, or poor." -> NOTHING
47. `[erosion_weathering/Erosion]` "Wind erosion occurs when wind moves pieces of earth materials." -> NOTHING
48. `[photosynthesis/Photosynthesis]` "Photosynthesis is the process by which plant cells containing chlorophyll produce food substances (glucose and starch) from carbon dioxide and water, and oxygen is released." -> NOTHING
49. `[phase_change/Melting]` "Melting is the process of changing something from a solid into a liquid (like metal into liquid metal)." -> banked `melting ISA process`
50. `[water_cycle/Water cycle]` "This whole process in which water evaporate and falls on the land and later flows back in river and pond is known as water cycle" -> banked `water cycle ISA process`

Counts here: P6 42, P2 6, P3 4, P4 4 of 1,229 sentences (~4.6% union) — the same distribution as
the textbooks, so the shape is not an OpenStax artifact.

---

## 4. PROPOSED VP- / PROCESS-HEADED PATTERNS (design only, NOT implemented)

Ordered by (evidence density x structural cleanliness). Every example is a real corpus sentence
quoted above. Note that these do NOT propose a "verb definiendum" — the corpus says that would be
harvesting ~3 sentences. They propose keeping the PREDICATE that the current head walk discards,
attached to the nominalized term that the corpus actually uses.

**VP1 — PROCESS_OF: `<TERM> is a|the <process-noun> OF <V-ing NP>`**
- Trigger: existing COPULA match where `definiens_head()` returns a member of a PROCESS-CONTAINER
  set (`process, act, mechanism, method, technique, reaction, response, movement, series, phenomenon`)
  AND the container is followed by `of <V-ing>`.
- Head-extraction rule: emit a SECOND slot, not a replacement — keep `TERM ISA process` and add
  `TERM PREDICATE (lemma_of(V-ing), head_noun_of(object NP))`, i.e. `transcription ->
  (copy, information)`. The V-ing token immediately after `of` is the predicate; its object is the
  head of the following NP by the existing `definiens_head()` applied to the post-verb span.
- Failure mode: `of`-complements that are NOT the predicate — "Foraging is the act of searching
  for AND exploiting food resources" gives two verbs and coordination must not be silently
  truncated to the first; also `of`+noun ("the process of chemiosmosis") has no V-ing and must
  refuse rather than take the noun.
- Real hits: `[BIO:3151]` "Hydrolysis is the process of breaking complex macromolecules apart.";
  `[BIO:15862]` "Ingestion is the process of taking in food through the mouth."
- Evidence density: 101 sentences; 70 already produce a (weak) fact, so this is a strict upgrade
  of rows we already bank.

**VP2 — BY_WHICH: `<TERM> is a|the <process-noun> BY|IN|THROUGH WHICH <finite clause>`**
- Trigger: `_NP_BOUNDARY` currently kills the walk at `by/in/which`; instead, on a
  PROCESS-CONTAINER head, capture the relative clause after `by which | in which | through which |
  whereby`.
- Head-extraction rule: the clause's MAIN VERB is the predicate; its subject is the clause's
  leading NP head and its object the post-verb NP head. `differentiation -> (become, specialized)`
  with subject `cells`. Passive clauses invert (agent optional): "light energy IS CONVERTED to
  chemical energy" -> `(convert, light energy -> chemical energy)`.
- Failure mode: the main verb of the relative clause is not identifiable by surface rule alone in
  coordinated or embedded clauses ("...produce food substances ... and oxygen is released" has
  two); needs a real clause segmenter or it will pick the wrong verb. Also `is/are` as the clause
  verb is contentless and must be skipped to the predicate complement.
- Real hits: `[ANAT:2292]` "Differentiation is the process by which unspecialized cells become
  specialized to carry out distinct functions."; `[BIO:9389]` "Ammonification is the process by
  which ammonium ion (NH4+) is released from decomposing organic compounds."
- Evidence density: 123 sentences, only 18 currently extracted.

**VP3 — DETERMINERLESS GLOSSARY: `term: process|type of ... which <clause>`**
- Trigger: relax `_RE_COLON`'s `_DET`-initial requirement on the definiens to
  `(?:_DET\s+)?<noun>` when the definiens' first content word is a PROCESS-CONTAINER noun.
- Head-extraction rule: as VP2 on the trailing relative clause; the definiendum is already the
  clean line-initial glossary key so no term-boundary risk is added.
- Failure mode: dropping the determiner requirement is exactly the guard that was TIGHTENED on
  2026-08-12 to stop mid-sentence colons producing false definitions (`cell -> nucleoid`
  regression, self-test case (c)). It must be re-gated some other way — line-anchored `^` plus a
  short (<=4 token) definiendum plus a PROCESS-CONTAINER first word, and the existing regression
  test must be re-run, not assumed.
- Real hits: `[BIO:3262]` "aerobic respiration: process in which organisms convert energy in the
  presence of oxygen"; `[BIO:7669]` "convergent evolution: process by which groups of organisms
  independently evolve to similar forms"
- Evidence density: a large fraction of the 123 P4 hits; currently yields exactly ZERO facts, so
  this is pure new supply.

**VP4 — OCCURS_WHEN: `<TERM> occurs|begins|happens|takes place WHEN|AS|IF <finite clause>`**
- Trigger: a new pattern; no existing regex can match it (COPULA needs `is/are` + a determiner).
  Definiendum = the pre-verbal NP (reuse `build_term()` unchanged); definiens = the `when`-clause.
- Head-extraction rule: this is NOT an ISA relation and must NOT be banked as one. Emit
  `TERM ENABLING_CONDITION (verb, subject-head, object-head)` from the subordinate clause —
  `nondisjunction -> (fail-to-separate, chromosomes)`. The genus stays unknown; that is honest.
- Failure mode: `occurs` also takes non-definitional adjuncts ("Little evaporation occurs because
  of the cold temperatures" `[BIO:21265]`, "Menstruation occurs after progesterone levels drop"
  `[BIO:20711]` — arguably fine, but "This occurs because ..." with an anaphoric subject must be
  refused). Pronominal / demonstrative subjects (`this`, `it`, `that`) are the dominant false
  positive and must be gated out.
- Real hits: `[BIO:967]` "Dissociation occurs when atoms or groups of atoms break off from
  molecules and form ions."; `[BIO:18289]` "Abduction occurs when a bone moves away from the
  midline of the body."
- Evidence density: 71 sentences in the textbooks + 4 in process_articles_v1; currently 2 yield
  anything (and those 2 are unrelated side-matches).

**VP5 — VP_CALLED: `<VP or process NP> is called|known as <TERM>`**
- Trigger: the existing `_RE_CALLED` match, but branch when the antecedent's `definiens_head()`
  is a PROCESS-CONTAINER or the antecedent contains `of <V-ing>`.
- Head-extraction rule: keep the existing `TERM ISA <container>` row AND add the predicate from
  the antecedent's `of <V-ing> ...` span, same reader as VP1: "The process of removing introns and
  reconnecting exons is called splicing" -> `splicing -> (remove, introns) + (reconnect, exons)`.
- Failure mode: this is the highest-yield pattern (357 hits, 225 already extracting) and therefore
  the highest-risk one: the CALLED antecedent is unbounded to the left and already produces wrong
  heads today (`intercellular signaling ISA cell`, `[BIO:3916]`). Adding a predicate reader on top
  of an antecedent that is sometimes mis-bounded will produce confidently wrong predicates.
  Should be gated behind a left-boundary fix, not shipped alongside it.
- Real hits: `[BIO:3849]` "This process is called carbon fixation, because CO2 is "fixed" from an
  inorganic form into organic molecules."; `[BIO:3171]` "The production of ATP using the process
  of chemiosmosis is called oxidative phosphorylation ..."

**Deliberately NOT proposed:** a `To X is to Y` verb-gloss pattern. Measured yield 1 real sentence
in 72,319 with 45 purposive false positives at the same trigger. The data does not support it.

---

## 5. WHAT I COULD NOT VERIFY

- **Whether any of these patterns would produce a GOOD fact.** This pass measured presence and
  extractability, not quality. No hand-scoring rubric was run on hypothetical output; the 64%
  MEANINGFUL v5 hand-score does not transfer to a predicate-valued relation nobody has scored yet.
- **Whether the store's consumers can even hold a predicate-valued fact.** Every row in
  `definitional_facts_v5.jsonl` is `(subject, relation=GROUNDED_MEANING, object)` with a single
  string object. A `(verb, arg1, arg2)` payload needs a schema decision I did not make and did not
  check downstream (`reading_grounding_loop.py` was off-limits this pass).
- **Whether VP2/VP3/VP4 can find the clause's main verb without a parser.** I asserted it is
  surface-findable; I did NOT implement or measure it. The coordinated-clause cases in the quoted
  sentences (Group A #1, #8; Group B #13) are visibly hard. If a parser is needed, that is a
  different (larger) build than "add a regex".
- **Precision of the survey triggers.** Hits were hand-checked for P1/P8/P11 only (all 121 read).
  P2-P6 counts are REGEX HITS with a 12-30 sentence eyeball each, not hand-scored precision. The
  550 P6 `During` hits in particular are certainly inflated with non-definitional frame sentences.
- **The other three textbook corpora** (`chemistry_2e`, `concepts_biology`, `microbiology`) and the
  117,642-sentence OpenStax corpus were NOT scanned; the 1.13% process-definition rate is measured
  on biology + anatomy + psychology only.
- **Whether the 0-verb fact is causally responsible for anything downstream.** It is a real
  property of the store; that it BLOCKS a given capability is a claim this pass did not test.
