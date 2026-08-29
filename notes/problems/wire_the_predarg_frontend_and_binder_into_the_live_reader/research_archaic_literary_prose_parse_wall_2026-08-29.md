# Brain mechanism of reading complex/archaic literary prose — the parse-wall drill

Research drill seeding p8 (`role_assignment_is_untested_on_archaic_literary_prose`) and informing
`wire_the_predarg_frontend_and_binder_into_the_live_reader`. Author: hdi_research (Director).
Date: 2026-08-29. Lit-scan calibration penalty applied (interpretations flagged SPECULATIVE; PINNED = a
primary result directly on the claim). Sibling drill (already on disk, do not duplicate):
`research_quotative_copula_role_assignment_2026-08-29.md` — this one goes deeper on the archaic-prose
*parse* wall, not the quotative/copula residuals.

## Bottom line (one screen)

- **The human does NOT build a full syntactic tree and then read roles off it.** Role assignment is
  **incremental, lexically driven, graded parallel constraint-satisfaction** — verb-class argument
  expectations + thematic fit + animacy + morphology/agreement + word order + discourse prominence are
  combined *as each word arrives*, before/without a complete parse. So a **"parse-first → then route
  roles" pipeline is the wrong SHAPE**; the faithful shape makes the dependency parse **one graded cue
  among several, not a gate**. (PINNED: MacDonald 1994; McRae 1998; Altmann & Kamide 1999; Frank & Bod
  2011; eADM 2006.)
- **Why long/inverted/archaic sentences break the PARSER but not the human:** the biggest lever is
  **exposure / domain adaptation** — the human has statistically learned these constructions
  (Wells/MacDonald 2009), the modern-newswire-trained parser has not (Gildea 2001: 86.3→80.6 F1,
  news→literature). Memory-limit effects (Gibson DLT; Lewis-Vasishth) and prediction (Kuperberg-Jaeger)
  hit both, but the human absorbs them via chunking/retrieval + good-enough underspecification
  (Swets 2008) that a rigid parser lacks.
- **Free indirect discourse speaker/viewpoint** is assigned by **the same prominence computation the
  substrate already has** (the Centering incumbent tier + subjecthood cue + graded binder): the FID
  anchor is the locally *prominent* protagonist — proper-name-in-subject beats indefinite-in-object
  (Saure, Hinterwimmer & Jordan-Bertinelli 2023). No new organ needed; route unattributed
  evaluative/epistemic sentences through topic/subject prominence, not a quotative verb cue.
- **Recommendation (point 4), ranked by yield × brain-fidelity:** **B (reframe role assignment as
  incremental multi-cue constraint-satisfaction) ≳ A (feed it an offline period-ADAPTED parse cue) > D
  (low-confidence abstain / good-enough underspecification) > C (memory/chunking for deep embedding).**
  A standalone period-retrained parser still feeding the *same* parse-then-route pipeline is the
  lower-fidelity half-measure; the fidelity win is demoting the parse to one cue.

---

## 1. Full parse tree, or incremental constraint-satisfaction before the parse? — INCREMENTAL (PINNED)

The evidence is strongly against "build the tree, then assign roles":

- **Lexically driven constraint-satisfaction, not tree-first.** MacDonald, Pearlmutter & Seidenberg
  (1994, *Psychological Review* 101(4):676-703) — syntactic ambiguity resolution is graded constraint
  satisfaction driven by lexical/probabilistic information, not serial tree-building. This is the
  canonical statement of the constraint-based lexicalist view.
- **Thematic fit is a first-class, graded constraint integrated *with* syntax.** McRae,
  Spivey-Knowlton & Tanenhaus (1998, *JML* 38(3):283-312): verb-specific thematic fit (how good a
  typical agent/patient the noun is) shapes parsing *simultaneously* with structural cues — roles are
  "verb-specific concepts," not slots filled after parsing.
- **Roles are assigned anticipatorily, before the argument exists.** Altmann & Kamide (1999,
  *Cognition* 73(3):247-264): the verb's argument expectations drive eye fixations to the likely filler
  *before* it is encountered ("the boy will eat…" → cake). Role/filler binding runs ahead of the parse.
- **Human reading times track SEQUENTIAL, not hierarchical, structure.** Frank & Bod (2011,
  *Psychological Science* 22(6):829-834): across probabilistic models, hierarchical-structure models did
  **not** explain word-by-word reading time over and above sequential-structure models — i.e. building a
  full hierarchical tree is not what generates online expectations. This is the sharpest single result
  against a "full-parse-first" shape. (Caveat/SPECULATIVE: contested — later naturalistic-listening work,
  e.g. Nelson et al. 2017 PNAS, finds hierarchical predictions; the safe read is that a *complete* tree
  is not a prerequisite for incremental role assignment, not that hierarchy is never used.)
- **eADM** (Bornkessel-Schlesewsky & Schlesewsky 2006, *Psychological Review* 113(4):787-821, PMID
  17014303): comprehenders compute argument *prominence* from animacy/case/voice/position incrementally
  and assign the highest generalized role early — a multi-cue, parse-light role computation.

**Verdict on the pipeline SHAPE.** "Parse → then route roles" is **OUR-INVENTION in shape** (functionally
admissible as an engineering substrate, but not the brain's shape). The faithful shape is **graded
parallel constraint-satisfaction** where verb-class expectation + thematic fit + animacy + agreement +
word order + discourse prominence are combined incrementally, and the dependency parse is **one
constraint source, not the seat/gate of role assignment.** The substrate's quotative/copula/animacy
fixes already push this way (they inject lexical + animacy + linear cues *on top of* the parse) — that
is the fidelity direction, not a patch.

## 2. Why the PARSER breaks where the human does not — the four levers, ranked

The question is specifically the *parser-vs-human gap* on archaic literary prose. Ranked by how much of
that gap each explains:

**(a) Exposure / domain adaptation — BIGGEST lever, and the one most specific to the parser gap (PINNED).**
- Human side: Wells, Christiansen, Race, Acheson & MacDonald (2009, *Cognitive Psychology*
  58(4):250-271, PMID 18922516) — manipulating adults' *reading experience* over weeks improved
  object-relative-clause processing via statistical learning of the constructions' distributional
  patterns. Skilled readers of Dickens are *domain-adapted* to 19c constructions; MacDonald &
  Christiansen (2002, *Psychological Review* 109:35-54) argue much of what looks like a working-memory
  limit is really experience with the construction.
- Parser side (the exact analog): Gildea (2001, "Corpus Variation and Parser Performance," EMNLP) — a
  WSJ-newswire-trained parser drops from **86.3 F1 on WSJ to 80.6 F1 on Brown (literature)**; the
  degradation is a *domain-shift* effect, not a competence ceiling. Our modern-UD-EWT parser (UAS ~0.79)
  is in exactly this situation on LitBank. **This lever is what the human has and the parser lacks — it
  is the root of the wall.** Partly and cheaply replicable in a glass-box: a **STATIC OFFLINE-BUILT
  asset** adapted to period text is admissible under the invariant (no LLM at inference).

**(d) Good-enough / strategic underspecification — cheap, high-fidelity, high relevance (PINNED).**
- Ferreira & Patson (2007, *Lang. & Linguistics Compass* 1(1-2):71-83); Ferreira, Bailey & Ferraro
  (2002, *Current Directions* 11(1):11-15): comprehenders run a heuristic route first and a full-parse
  route only under demand.
- Swets, Desmet, Clifton & Ferreira (2008, *Memory & Cognition* 36(1):201-216, PMID 18323075):
  readers **do not fully parse ambiguous structure when the task does not require it** — an ambiguity
  *advantage* appears under shallow questions and disappears under deep ones. Depth of parsing is
  task-gated. Implication for us: the reader should not be forced to commit a full role assignment where
  the parse is unreliable — abstaining / falling back to lexical-linear cues is *brain-faithful*, not a
  cop-out. Cheaply replicable (an abstain/confidence policy).

**(b) Working memory / chunking / retrieval — explains sentence-LENGTH & embedding difficulty for BOTH
(PINNED), so it is a smaller part of the parser-*vs-human* gap.**
- Gibson (1998, "Linguistic complexity: locality of syntactic dependencies," *Cognition* 68(1):1-76,
  PMID 9775516) — Dependency Locality Theory: storage cost (open predictions) + integration cost
  (distance to the head). Long-distance dependencies in embedded/inverted sentences strain memory.
- Lewis & Vasishth (2005, *Cognitive Science* 29(3):375-419) — sentence processing as cue-based,
  content-addressable memory retrieval with similarity-based interference; explains why deep embedding
  and repeated similar NPs (common in literary prose) cause errors.
- Futrell, Gibson & Levy (2020, *Cognitive Science* 44(3):e12814, PMID 34018239) — lossy-context
  surprisal unifies memory-limit and expectation effects: difficulty = surprisal given a *lossy* memory
  of context. The human copes with length via chunking + graceful forgetting; a rigid parser holds a
  brittle full analysis. Medium cost to replicate (reuse the substrate's graded binder as cue-based
  retrieval).

**(c) Prediction / anticipation — highest fidelity, hardest to build glass-box without an LM (PINNED
mechanism, partial replicability).**
- Altmann & Kamide (1999) as above; Kuperberg & Jaeger (2016, *Language, Cognition and Neuroscience*
  31(1):32-59, PMC4850025): comprehension is **probabilistic prediction at multiple levels**, framed as
  inferring the event that best explains the input using cues of varying reliability — essentially the
  generative/constraint-satisfaction view again. Much of the human's robustness to a hard sentence is
  that they *predict* the upcoming argument from the verb and world knowledge. Partly available to us
  already: the landed `predicate_argument_frontend` + thematic-fit cues *are* verb-class expectation;
  full probabilistic next-word prediction is the part we cannot cheaply do glass-box.

**Ranking of levers for THIS gap:** (a) exposure/domain-adaptation ≫ (d) good-enough underspecification
> (b) memory/chunking > (c) prediction. Cheapest-to-replicate glass-box: **(a) offline-adapted cue
statistics and (d) an abstain policy** — both cheap, both directly attack the wall.

## 3. Free indirect discourse — speaker/viewpoint with no overt "said X" (PINNED, evidence class:
acceptability + reference-resolution, not online ERP)

- **The anchor is the locally PROMINENT protagonist.** Saure, Hinterwimmer & Jordan-Bertinelli (2023,
  *Zeitschrift für Sprachwissenschaft* 42(2):341-372, DOI 10.1515/zfs-2023-2009): in an acceptability
  experiment varying narrator type, an unmarked FID segment is anchored to the protagonist that "stands
  out" — **a proper-name-in-subject-position protagonist is strongly preferred as the FID
  thinker/speaker over an indefinite-NP-in-object-position one.** Prominence = grammatical function +
  referring-expression type + topicality (the Kaiser & Trueswell prominence tradition).
- **The viewpoint holder is the discourse topic / most accessible entity** — the same Centering
  backward-looking-center machinery that governs pronoun resolution; FID inherits the current
  perspectival center. Supporting: eADM prominence (2006); reading-experiment work on the "dual voice"
  of FID (Sotirova 2004); and preserved, automatic FID perspective-taking even in ASD (PMC8292616),
  suggesting the anchor computation is robust and does not require explicit mentalizing effort.
- **SPECULATIVE caveat:** the pins are acceptability/reference-resolution and text-linguistic, not a
  moment-by-moment ERP that isolates "who is speaking" at the FID onset. Also epistemic/evaluative cues
  (modals, deixis, exclamatives, "surely", "poor X") shift viewpoint to a character and are a known FID
  signal, but I found no online-processing study quantifying their weight.

**Decision-useful bridge:** FID viewpoint assignment is **not a new mechanism** — it is the substrate's
existing prominence stack (incumbent Centering tier + subjecthood cue + graded who-did-what binder).
The fix is a **trigger**: when a sentence carries thought/perception/evaluation content but no overt
attribution verb, assign its implicit speaker = the current prominent topic (the binder's incumbent),
rather than defaulting to positional agent or a quotative rule.

## 4. Concrete recommendation for the glass-box HD substrate — ranked by yield × brain-fidelity

Options considered (no external LLM at inference; a STATIC OFFLINE-BUILT asset is allowed):

| Option | Yield | Brain-fidelity | Verdict |
|---|---|---|---|
| **A. Offline-ADAPT the parse cue to period text** (retrain/self-train cue statistics on 19c prose as a static asset; or bootstrap silver parses) | **High** (attacks the measured OOD root; Gildea gap) | **High** — domain adaptation IS the human's advantage (Wells 2009) | Do now; but keep it a *cue*, not a gate |
| **B. Reframe role assignment as incremental multi-cue constraint-satisfaction** (verb-class expectation + thematic fit + animacy + agreement + word order + discourse prominence; parse = one graded cue) | **High** (long-term; unblocks all residuals) | **Highest** — this is the brain's actual shape (MacDonald, McRae, eADM, Frank & Bod) | The fidelity target; bigger build |
| **D. Good-enough abstain / underspecification** (when parse confidence low, fall back to lexical-linear cues or abstain; don't force a wrong full role) | **Medium** (insurance; prevents confident-wrong) | **High** (Swets 2008; Ferreira) | Cheap; pair with A and B |
| **C. Memory/chunking mechanism** (cue-based retrieval / clause segmentation for deep embedding) | **Medium** (helps depth, not OOD constructions) | **High** (Gibson DLT; Lewis-Vasishth) | Later; only if embedding depth is the residual |

**Ranked: B ≳ A > D > C.** The single most fidelity-improving change is **B** (demote the parse to one
graded cue in constraint-satisfaction); the single highest *immediate yield* is **A** (an offline
period-adapted parse cue directly closes the measured OOD gap and *is* the human's domain-experience
mechanism). They are complementary, and **A alone — a period-retrained parser still feeding the same
parse-then-route pipeline — is the lower-fidelity half-measure**, because it fixes the cue quality but
keeps the wrong shape. **D** is cheap insurance that is itself brain-faithful and should ship alongside.
**C** is real but targets sentence *length*, which is a smaller part of the parser-vs-human gap than OOD
*constructions*.

**Practical sequence for p8/the wiring:** (1) MEASURE the OOD parse gap on archaic vs modern prose (p8's
core task — quantifies A's headroom and D's trigger threshold); (2) ship D (a low-confidence abstain +
lexical-linear fallback) as the cheap immediate guard; (3) build toward B (route roles through graded
multi-cue constraint-satisfaction with the parse as one cue — the substrate's quotative/copula/animacy
cues are already the seed); (4) add A (offline period-adapted cue statistics as a static asset) to lift
the parse cue's quality; (5) C only if deep-embedding residual remains after A+B+D.

---

## Primary sources (author, year, venue; PMID/DOI where available)

- MacDonald, Pearlmutter & Seidenberg (1994). Lexical nature of syntactic ambiguity resolution.
  *Psychological Review* 101(4):676-703.
- McRae, Spivey-Knowlton & Tanenhaus (1998). Modeling thematic fit in on-line sentence comprehension.
  *JML* 38(3):283-312.
- Altmann & Kamide (1999). Incremental interpretation at verbs. *Cognition* 73(3):247-264.
  doi:10.1016/S0010-0277(99)00059-1.
- Frank & Bod (2011). Insensitivity of the human sentence-processing system to hierarchical structure.
  *Psychological Science* 22(6):829-834. doi:10.1177/0956797611409589.
- Bornkessel-Schlesewsky & Schlesewsky (2006). eADM. *Psychological Review* 113(4):787-821. PMID 17014303.
- Wells, Christiansen, Race, Acheson & MacDonald (2009). Experience and sentence processing: statistical
  learning and relative clause comprehension. *Cognitive Psychology* 58(4):250-271. PMID 18922516.
- MacDonald & Christiansen (2002). Reassessing working memory. *Psychological Review* 109(1):35-54.
- Gildea (2001). Corpus Variation and Parser Performance. *EMNLP 2001*:167-202 region (ACL W01-0521);
  WSJ 86.3 → Brown 80.6 F1.
- Ferreira, Bailey & Ferraro (2002). Good-enough representations. *Current Directions in Psychological
  Science* 11(1):11-15.
- Ferreira & Patson (2007). The good enough approach to language comprehension. *Language and
  Linguistics Compass* 1(1-2):71-83.
- Swets, Desmet, Clifton & Ferreira (2008). Underspecification of syntactic ambiguities: evidence from
  self-paced reading. *Memory & Cognition* 36(1):201-216. PMID 18323075.
- Gibson (1998). Linguistic complexity: locality of syntactic dependencies. *Cognition* 68(1):1-76.
  PMID 9775516.
- Lewis & Vasishth (2005). An activation-based model of sentence processing as skilled memory retrieval.
  *Cognitive Science* 29(3):375-419.
- Futrell, Gibson & Levy (2020). Lossy-context surprisal. *Cognitive Science* 44(3):e12814. PMID 34018239.
- Kuperberg & Jaeger (2016). What do we mean by prediction in language comprehension? *Language,
  Cognition and Neuroscience* 31(1):32-59. PMC4850025.
- Levy (2008). A noisy-channel model of rational human sentence comprehension under uncertain input.
  *EMNLP 2008*:234-243.
- Saure, Hinterwimmer & Jordan-Bertinelli (2023). An experimental investigation of the interaction of
  narrators' and protagonists' perspectival prominence in narrative texts. *Zeitschrift für
  Sprachwissenschaft* 42(2):341-372. doi:10.1515/zfs-2023-2009.
- Sotirova (2004/2006). The 'dual voice' of free indirect discourse: a reading experiment (text-linguistic).
- (ASD FID perspective-taking, preserved/automatic) *PMC8292616*.

## Prior arc work (experiment_index — checked, do not re-derive)
- Role/thematic lineage LANDED: `exp_thematic_role_labeler_cue_integration_v1` (HARD_PASS),
  `exp_coherence_role_compat_score_selector_v1` (constraint-satisfaction), `exp_situation_reader_frame_arity_gate_gold_v1`,
  `exp_read_grow_construction_induction_dop_fragments_v1` (surprisal/construction induction, HARD_PASS).
- Parser lineage: 79 cells under "parser," 74 landed (attachment/coref residuals). No prior cell measures
  parse accuracy on archaic vs modern prose — that is p8's open gap.
- Sibling drill: `research_quotative_copula_role_assignment_2026-08-29.md` (quotative/copula/linear-fallback fidelity).

## TLDR (plain language)
Skilled readers do not build a full grammar diagram of a Dickens sentence and then work out who did
what. They assign roles word-by-word from the verb's expectations, how alive each thing is, agreement,
word order, and who the passage is "about" — the grammar parse is just one hint among many. That is why
our automatic parser, trained on modern news, struggles on 200-year-old prose while a person does not:
the person has *read a lot of that kind of writing* and learned its shapes (the same reason a
news-trained parser loses about six points of accuracy when moved to literature). People also cope by
not fully parsing what the moment does not require, and by chunking long sentences. For "she thought"
passages with no "said X," the reader just treats the person the passage is currently about as the
speaker — which is exactly the "who is the topic" skill our reader already has. Fix, best first: make
role assignment a weighted vote of many cues (with the parse as one vote), feed it a parser tuned
offline on old prose, let it abstain when unsure, and only add sentence-chunking if deep nesting is
still the problem afterward.

## Questions
None.

## Next steps
1. p8 first MEASURES the modern-vs-archaic parse gap (quantifies option A's headroom + sets option D's
   abstain threshold) — this drill says that measurement is the right opening move.
2. The wiring problem should treat the parse as ONE cue (option B shape), not a gate — ship a
   low-confidence abstain + lexical-linear fallback (option D) as the cheap immediate guard.
3. FID: route unattributed thought/perception/evaluative sentences through the existing incumbent-topic
   prominence (the graded binder), not a quotative rule — no new organ.
