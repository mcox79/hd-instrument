# Learned glass-box PARSER blueprint: clause-segmentation (coordination) + NP-head-finding
Research drill (biology-led, prior-art-credited) — Director, 2026-07-18
Grounding the VET-confirmed wall (a7ecb244): the reader's ONE remaining wall is the HAND-RULE PARSER
(clause-splitter orphans coordinated verbs; NP-parser grabs false heads/args). Coref + grounding HELD.

Prior arc work on glass-box clause-seg / NP-parsing: **NONE** (substrate concept-query returned only
generic lexical resources — wordnet `coordinating_conjunction`, GO `head segmentation` — and unrelated
`Coordination` hits from parietal/WM phase-diagram notes). This is new territory for the reading arc.

Scope: research/scoping ONLY. No cell dispatch, no push.

---

## TOP-LINE
Two named failures, two DIFFERENT downstream harms, two DIFFERENT difficulty levels:
- **NP-head errors** ("the first strawberry" -> patient="first"; manner-PP-as-location; ordinal-as-location)
  -> drive the **foundation false-positives (~40%)**. This is the **EASIER, more tractable** learned
  component (base-NP chunking is a ~92 F1 solved problem; head-finding is near-deterministic) AND it is
  where the substrate has a genuine **grounding EDGE** (a grounded-object token is the likely NP head).
- **Clause-seg / coordination errors** (shared-subject orphaning: "X v1-ed and v2-ed Y" loses X for v2)
  -> drive the **composition-degrade**. This is the **HARDER** component (best transparent clause-ID F1
  ~79 on newswire; coordination-boundary is a *named* hard sub-problem) and it maps onto the discourse
  "state-of-mind" overlay (keep the subject active across the conjunction) that is already the NEXT-BUILD.

**RECOMMENDED FIRST learned component: NP-HEAD-FINDING (grounding-biased head selector).** Higher leverage
because it is the easier win, plays to a substrate strength (grounding), attacks the more quantified harm
(the ~40% FP rate), sits FIRST in the natural shallow-parse pipeline (chunk NPs -> then clauses), and a
clean NP-head is a prerequisite: clause-seg that hands garbage heads to the role-assigner still yields bad
tuples. Clause-seg/coordination follows as component #2, leaning on the discourse overlay for the shared
subject. **Honest caveat:** fixing these two attacks the two *named* failure modes and should recover a
large fraction of both harms, but it will NOT be a clean 1.0 — PP-attachment (manner-vs-location) is
genuinely ambiguous even for SOTA, and a residual tail (relative/complement clauses, nested coordination)
will keep leaking. Strategic read = hypothesis pending a landed fair-test, not a fact.

---

## (a) BIOLOGY / PSYCHOLINGUISTICS — how the brain does it

### A1. Clause segmentation + COORDINATION (shared subject / gapping / RNR)
- **Incremental, predictive parsing.** The brain assigns hierarchical structure word-by-word as input
  arrives; it does not wait for the clause to end. When a downstream word violates the running commitment
  it triggers **reanalysis** — the garden-path effect (Frazier/Ferreira lineage). Clause-boundary
  garden-paths (e.g. "After Mary dressed the baby played") are a canonical case where the parser must
  revise a mis-attached NP across the clause boundary. ERP correlate = the **P600** for syntactic
  reanalysis/repair (though P600 amplitude tracks *ongoing difficulty/confusion*, not necessarily
  *successful* repair — do not over-read it as a clean "repair" signal). Source: Fodor/Frazier garden-path
  literature; clause-boundary revision studies (Memory & Cognition 2023, PMC10805993).
- **Shared-subject coordination is handled by keeping the subject ACTIVE in working memory**, not by
  re-deriving it. In "X verb1-ed and verb2-ed Y", the brain does not orphan verb2 — it holds X in a
  working-memory buffer and re-binds it as the agent of the second verb. This is precisely the mechanism
  our reader lacks (the hand-splitter drops X). Biologically this is a **working-memory / discourse-state**
  function, not a lexical one — which is *why it maps onto the "state-of-mind" overlay* rather than the
  tokenizer.
- **Gapping** ("Sam ordered coffee and Fred [ ] tea") and **Right-Node-Raising** ("[Sam likes] but
  [Fred dislikes] the debates") are *sharing/ellipsis* mechanisms: material is shared across conjuncts and
  physically absent from one. Psycholinguistically these are resolved heavily by **prosody and focus** —
  contrastive accent on the non-shared remnants plus a pause before the shared material. Gapping remnants
  must be *major syntactic constituents*. Key implication for us (see brain-check on test design below):
  **the brain uses PROSODY to resolve coordination ellipsis, and text has none** — so a text-only parser
  is working with strictly less signal than the brain, and its fair ceiling is correspondingly lower.
  Sources: Hartmann (RNR & Gapping: prosodic deletion); Chaves (disunity of RNR); ScienceDirect S0024384103001438.

### A2. Noun-phrase parsing (head + modifiers as ONE unit, correct head)
- The brain treats an NP as a single referential unit built around a **head noun**, with determiners,
  adjectives, and ordinals as **modifiers that restrict** the head, not as the referent. "the first
  strawberry" refers to a *strawberry* (head), with "first" restricting *which* — the brain never takes
  "first" as the thing lifted. Semantic/world knowledge (plausibility of a referent) strongly constrains
  head selection: only *strawberry* is a plausible liftable object; "first" and "lifting" are not object
  concepts. This is exactly the grounding-as-prior the substrate can exploit.
- **PP-attachment** ("the man with the telescope") is a classic *bounded-ambiguity* case the brain
  resolves with plausibility + recency + prosody, and where it *also fails* (genuine ambiguity, good-enough
  reads). The manner-vs-location PP problem in our failures ("lifting ... with a X" as instrument/manner
  vs "on the Y" as location) is the same argument/adjunct distinction.
- **Good-enough processing** (Ferreira): the brain does NOT always build a full correct syntactic tree;
  it builds a good-enough *interpretation* and discards structure. Relevant brain-check: **the brain
  itself makes confident wrong NP/PP guesses** under time pressure — so "the parser sometimes gets the
  head/attachment wrong" is *brain-faithful*, not a disqualifying bug. The fix for the residual is
  substrate-NATIVE (exploit exact grounding), not "be more brain-like."

### A3. LEARNED + usage-based (not innate rules)
- **Construction grammar (usage-based).** Coordination and complex-NP structure are learned form-meaning
  *constructions*, acquired item-by-item then abstracted, governed by **entrenchment** (frequency) and
  **preemption**. Diessel: complex sentences (incl. coordinate clauses) emerge ~age 2 out of simpler
  biclausal units; children generalize coordination gradually from concrete instances. Takeaway: a
  **learned construction inventory** ("NP -> Det (Adj|Ord)* HEAD-NOUN", "S -> NP VP and VP [shared NP]")
  is the biologically-motivated replacement for the fixed hand-rules, and it is *learnable from examples*.
  Sources: Diessel, *The Acquisition of Complex Sentences* (Cambridge); Tomasello construction-grammar +
  first-language-acquisition; Dunn, frequency-vs-association constraint selection (arXiv 1904.05529).

---

## (b) GLASS-BOX ENGINEERING PATH (build-on + credit; non-LLM, transparent)

### B1. NP-head-finding (the recommended FIRST component)
- **Base-NP chunking is a solved, transparent problem.** Ramshaw & Marcus 1995 ("Text Chunking Using
  Transformation-Based Learning") cast chunking as IOB tagging and hit **F1 ~92** on the CoNLL-2000 base-NP
  set — the de-facto standard for years, with fully inspectable transformation rules. Later transparent
  learners (perceptron/CRF/SVM taggers) reach ~93-94. **Credit:** Ramshaw & Marcus 1995; CoNLL-2000
  chunking shared task (Tjong Kim Sang & Buchholz).
- **Head selection: near-deterministic rules + a learned tie-breaker.** Collins (1999, Appendix A)
  head-percolation tables ("Skippy the Kangaroo" -> head *Kangaroo*) are a transparent, widely-used
  baseline (implemented as Stanford `CollinsHeadFinder`). **Known limitation to credit honestly:** Penn
  Treebank leaves NP-*internal* structure flat, and Collins-model NP-internal recovery was *significantly
  worse than overall* due to lack of lexical info — fixed later by Vadas & Curran 2011 ("Parsing Noun
  Phrases in the Penn Treebank") who added NP-internal annotation + richer head heuristics. **Credit:**
  Collins 1999; Vadas & Curran 2011.
- **How grounding HELPS head-finding (substrate edge).** Head rules choose the rightmost noun by default;
  they fail exactly when a modifier is noun-like or when ordinals/adjectives get grabbed. The substrate
  already has **grounded vocab** — an object-grounded token ("strawberry") is a strong prior for the head,
  and a non-grounded modifier ("first", "lifting") is a strong prior for NOT-head. A learned head selector
  with a *grounded-object feature* is a transparent, high-precision fix for "patient=first". This is the
  brain's semantic-plausibility constraint, made *exact* by the substrate's grounding table.

### B2. Clause-segmentation + coordination (component #2)
- **Clause identification is a named, harder shared task.** CoNLL-2001 (Tjong Kim Sang & Déjean) — best
  transparent system Carreras & Màrquez 2001 (boosted decision trees) at **F1 78.63** on WSJ section 21;
  the field ranged 50-68 for others. Newswire is far harder than grade-3 narrative, so simple-narrative
  clause-ID should sit meaningfully higher — but 78.6 on hard text is the honest anchor for "transparent
  learned clause-seg is imperfect." **Credit:** Tjong Kim Sang & Déjean, CoNLL-2001; Carreras & Màrquez 2001.
- **Coordination-boundary detection is a *known hard sub-problem*, and there is parser-free prior art.**
  SOTA parsers show a measured *error increase* on conjunctive sentences. Transparent lines to build on:
  (i) **similarity + replaceability of conjuncts** — coordinated conjuncts are syntactically/semantically
  parallel and mutually substitutable (Ficler & Goldberg 2016, I17-1027); (ii) **parser-free pipelines** —
  coordinator identification -> conjunct-boundary detection (CoRec, arXiv 2311.18712); (iii) symmetry/
  alignment models. For the *shared-subject* case specifically, the operational rule "a bare VP conjunct
  after `and` inherits the most recent subject NP" is a transparent, learnable construction — and the
  *biologically correct* implementation is to **read the held subject out of the working-memory / discourse
  overlay**, not to re-parse. **Credit:** Ficler & Goldberg 2016; CoRec 2023.
- **Argument/adjunct (PP) distinction = the manner-vs-location leak.** Transparent SRL practice: an "instr"
  PP headed by *with* is a core-ish Arg2; *locative/manner/temporal* PPs are adjuncts, often separable by
  simple features (animacy, preposition identity, position). "in the morning" is ruled a time-adjunct by
  *lacking* core-argument features. The substrate's grounding gives exactly those features for free
  (grounded-location vs grounded-instrument vs abstract). **Credit:** PropBank argument conventions;
  syntax-aware SRL (arXiv 1903.05260).

### B3. Realistic accuracy on SIMPLE narrative
Grade-3 narrative is short, mostly SVO, low embedding depth — so transparent learned NP-chunk/head should
land **high (~90+ span-F1)** and clause-seg **meaningfully above the 78.6 newswire anchor**. The *hard*
minority = exactly the difficulty-on cases we must include: coordinated VPs (shared subject), complex NPs
(ordinal+noun, PP-modified), and manner/location PPs.

---

## (c) SUBSTRATE STRENGTH vs GAP
- **STRENGTH.** (1) Grounding table = an exact semantic-plausibility prior for head-finding and
  argument/adjunct classification — the brain's plausibility constraint made *exact and inspectable*.
  (2) Glass-box: the learned construction inventory is directly readable/auditable (unlike an LLM parser).
  (3) The discourse "state-of-mind" overlay (NEXT-BUILD) is the natural home for held-subject coordination —
  reuse, not new machinery. (4) Coref + grounding already HELD, so the parser fix is *localized*.
- **GAP.** (1) No prosody — the brain's primary coordination-ellipsis cue is absent from text, capping the
  fair ceiling below human. (2) Learned components need **gold training/eval spans** on grade-3 text
  (clause boundaries + NP-head spans) — a real annotation cost. (3) Genuine PP-attachment ambiguity has an
  irreducible tail even with grounding. (4) Nested/deep coordination and relative/complement clauses are
  beyond the two named fixes.

---

## (d) FAIR TEST (design-gate compliant: real baseline / can-fail / difficulty-on / one variable)
- **Task & metric:** gold **clause-boundary spans** and gold **NP-head spans** (+ head token) on held-out
  real grade-3 narrative; report **span Precision / Recall / F1** (head-token accuracy separately). Span-F1
  is unsaturated and telemetry-sensitive -> can-fail discriminator, not by-construction.
- **Can-fail REAL baseline:** the CURRENT hand-rule clause-splitter + hand-rule NP-parser (not a strawman /
  abstain-all). The learned component must BEAT it on span-F1 to earn its place.
- **Difficulty ON:** the eval set MUST include the failure cases — coordinated VPs (shared subject),
  ordinal/adjective+noun NPs, and PP-modified NPs (manner vs location). No frac=0 "all simple SVO" set;
  no smoke-only hardness. Report simple vs hard slices separately so a win isn't diluted by easy SVO.
- **One variable:** swap ONLY the parser stage (hand-rule -> learned); hold grounding, coref, role-assigner,
  composition fixed. Downstream metric (composition MRR + foundation FP-rate) is the *outcome* read, but the
  primary discriminator is upstream span-F1 so the attribution is clean.
- **Brain-check on the TEST DESIGN:** because text has no prosody and the brain *itself* makes confident
  wrong PP/coordination guesses (good-enough), the fair bar is "**substantially beat the hand-rule splitter
  and approach transparent-parser F1 on simple narrative**" — NOT perfection. Grounding is our
  prosody-substitute (the brain's semantic-plausibility route), made exact.

---

## (e) HONEST GAP-MAP — do these two fixes plausibly un-degrade composition + clean the foundation?
- **Likely YES for the bulk, NO for a clean 1.0.** The two components are aimed at the two *empirically
  localized* harms: NP-head -> the ~40% foundation FPs; shared-subject clause-seg -> the composition
  degrade. Both are attackable with transparent, credited prior art, and grounding gives a real edge on the
  head-finding half. Expect a large recovery of both.
- **Residual tail (do not over-claim):** genuine PP-attachment ambiguity (manner/location), nested
  coordination, relative/complement clauses, and gapping/RNR (which the brain resolves with prosody we
  don't have) will keep leaking. If the landed fair-test shows the FP-rate and composition-degrade *dominated*
  by these tail cases rather than the two named ones, then it IS a bigger parse problem and the next move is
  a fuller learned shallow parser, not two point-fixes.
- **Sequencing:** NP-head-finding FIRST (easier, grounding-advantaged, prerequisite, attacks the quantified
  FP harm, natural pipeline order) -> then shared-subject clause-seg SECOND (harder, reuse the state-of-mind
  overlay for the held subject). This is also the natural build order: clean NP-heads make the clause-seg
  eval interpretable.

---

## Credits (learn-from + build-on)
Ramshaw & Marcus 1995 (transformation-based chunking); CoNLL-2000 chunking (Tjong Kim Sang & Buchholz);
Collins 1999 (head-percolation); Vadas & Curran 2011 (Penn Treebank NP-internal structure); Tjong Kim Sang
& Déjean / Carreras & Màrquez 2001 (CoNLL-2001 clause identification); Ficler & Goldberg 2016 (coordination
boundary via similarity/replaceability); CoRec 2023 (parser-free coordination recognition); Diessel
(acquisition of complex sentences); Tomasello (usage-based construction grammar); Ferreira/Frazier
(good-enough & garden-path processing); Hartmann / Chaves (RNR & gapping prosody). All borrowed-and-credited;
the substrate-native contributions are the *grounding-biased head selector* and *reading the held subject
out of the discourse overlay* — genuinely new framings, credited as built on the above.
