# Research drill: feature-agreement as candidate-set pruning for pronoun->entity resolution

SOLVER-side literature drill. Complements the sibling note
`research_pronoun_event_binding_mechanism_2026-08-29.md` (that one covers the BINDING/focus side --
Centering-Cb, situation model, LIFG unification). THIS note covers the ANTECEDENT / CANDIDATE-SET side:
what cheap, glass-box, non-LLM feature-agreement cues the brain uses to PRUNE the pool a pronoun
competes over, and how much they can pay on 19c narrative (LitBank). LEAD-WITH-BIOLOGY. ASCII only.
Date: 2026-08-29.

Live bottleneck (from the binder's measurements): the graded binder competes a pronoun ("he") against
EVERY prior entity because most name mentions lack GENDER. Gender agreement helps but only 22.5% of
name mentions carry a lexical gender cue (Mr/Miss title, or a gazetteer given name); the other 77.5%
are bare surnames ("Darcy") or archaic names with NO mention-level gender. Gender propagates through a
coref cluster once a bound "he" or "Mr Darcy" appears, but the FIRST resolution of a fresh entity is
unconstrained.

Calibration note (lit-scan penalty applied): the QUALITATIVE directions below (graded-not-hard,
cue-based retrieval, animacy as a cheap high-coverage cue, Hobbs coverage) are well-established and
high-confidence. The QUANTITATIVE transfer of any lever to the specific 19c who-did-what metric is
UNCERTAIN and is framed as expected-payoff-pending-VET. The only corpus-measured anchor is the sibling's
+2.2 who-did-what from dropping mis-extracted 1st/2nd-person candidates.

---

## Q1. Is agreement a HARD FILTER or a GRADED CUE in human pronoun resolution?

**Answer: GRADED cue, decisively. The human parser does NOT delete mismatching antecedents before
retrieval; it runs a parallel feature-match that DOWN-WEIGHTS mismatches, and mismatching-but-
feature-sharing distractors demonstrably still compete (retrieval interference / agreement attraction).**

### Mechanism
Antecedent retrieval is content-addressable, cue-based, and parallel (ACT-R-style). On encountering the
pronoun the parser issues a bundle of retrieval cues (gender, number, animacy, structural position,
recency/base-level activation) and every item in memory is activated in proportion to how many cues it
matches. A wrong-gender item is not removed -- it simply receives less activation. When a structurally
illicit or wrong-feature item PARTIALLY matches, it steals activation from the target: this is the
signature "interference" / "attraction" effect (slower reading, illusory acceptability). Cues are
combined by RELIABILITY/diagnosticity, not as an all-or-nothing conjunction -- which is exactly why a
single unreliable cue (gender, on this corpus) should be weighted DOWN, not treated as a gate.

### Key studies
- **Badecker & Straub (2002), JEP:LMC.** Gender/number of grammatically INACCESSIBLE antecedents still
  modulate pronoun/reflexive processing -> features are used as retrieval cues that activate even illicit
  matches; syntactic constraints are violable and interactive, not a pre-retrieval hard gate. The
  foundational "graded, not filter" result.
- **Wagers, Lau & Phillips (2009), JML -- agreement attraction in comprehension.** A number-matching
  non-subject "lure" produces an illusion of grammaticality: the parser erroneously retrieves the lure on
  a partial [+plural] cue match. Direct evidence that a feature acts as a soft retrieval cue that
  mis-fires under partial match, not a clean filter.
- **Dillon, Mishler, Sloggett & Phillips (2013), JML.** Contrasting intrusion profiles: subject-verb
  agreement shows strong feature-attraction while reflexives show much less -> the parser WEIGHTS cues
  differently by dependency type (structural cues can dominate for some dependencies). Confirms
  reliability-weighted cue combination, and that gender/number are among the weighted cues for ordinary
  pronouns.
- **Gonzalez Alonso et al. (2021).** Gender attraction is attested in comprehension -> gender behaves
  like number: a graded, interference-prone cue, not a hard gate. (Attraction is modulated by syncretism
  / cue reliability -- another argument for reliability-weighting rather than deletion.)
- **Lewis & Vasishth (2005), Cognitive Science -- ACT-R cue-based parser.** The computational backbone:
  graded activation + similarity-based interference (fan effect). More feature-sharing competitors ->
  lower activation of the true target -> the value of a cue is precisely that it REDUCES the effective
  competitor set, and its value scales with how few items it leaves matching.

### Glass-box implementable? + expected payoff
YES, and it changes the DESIGN, not just a parameter: **DOWN-WEIGHT wrong-gender candidates by a
reliability-scaled penalty; do NOT DELETE them.** Deletion is only safe when the feature is both PRESENT
and HIGH-reliability; with 77.5% of mentions missing gender and archaic noise on the rest, a hard delete
will silently drop the true antecedent whenever the tag is wrong or absent. A graded penalty degrades
gracefully -- it prunes when gender is present and trustworthy, is a no-op when absent, and costs only a
little (recency/salience can still win) when wrong. This is both the brain-faithful choice AND the
robust one for the missing-cue regime. PINNED (cue-based retrieval is well-established); the penalty
magnitude/weight is OUR-INVENTION -> SWEEP it, scaled by the cue's measured reliability on this corpus.

---

## Q2. How does a reader establish an entity's gender when the name carries NO lexical cue (the 77.5%)?

**Answer: four routes -- (a) cataphoric / later-pronoun assignment, (b) world-knowledge name/role gender,
(c) morphological number, (d) animacy. Of these, ANIMACY and NUMBER are cheap + brain-faithful + fully
glass-box with HIGH coverage; cataphoric CLUSTER-propagation is brain-faithful and implementable; a
period name-gender GAZETTEER is admissible as a static offline asset but has PARTIAL coverage on this
corpus (given names only, not bare surnames).**

### Mechanism + studies, per route

(a) **Cataphoric / later-pronoun gender assignment.** A reader who meets a bare name and later a "he"
retro-assigns masculine to that entity; in true cataphora the reader assigns categorical sex to a not-
yet-named referent from the pronoun itself and searches actively for its host.
  - Kreiner, Sturt & Garrod (2008): a cataphoric reflexive assigns categorical gender to the character
    BEFORE the role noun; when it has, later stereotype-gender incongruity effects vanish. Kazanina et
    al. (2007) / cataphora active-search work: the parser posits and hunts an antecedent for a gender-
    marked pronoun.
  - Glass-box + payoff: YES -- this is a two-pass / cluster-propagation move. Set an entity's gender from
    the FIRST high-confidence bound pronoun and apply it RETROACTIVELY to earlier competitions for that
    cluster. The binder already propagates gender forward within a cluster; the lever is closing the
    FIRST-resolution gap by lookahead. MODERATE payoff -- recovers gender for any entity that ever takes
    a pronoun, but by construction cannot help the very first pronoun of a fresh entity.

(b) **World-knowledge gender of names and role nouns.** Readers activate stereotype/definitional gender
of given names ("Elizabeth"->fem) and role nouns ("nurse"->fem, "king"->masc) inferentially.
  - Osterhout, Bersick & McLaughlin (1997); Carreiras, Garnham, Oakhill & Cain (1996); Kreiner et al.
    (2008); Duffy & Keir (2004). ERP: stereotype violations yield N400 (reading) / P600 (anaphora)
    effects -> the cue is used but DEFEASIBLY (graded, overridable), consistent with Q1.
  - Glass-box + payoff: PARTIAL. A period-appropriate name->gender GAZETTEER and a role-noun gender list
    are STATIC OFFLINE ASSETS (admissible under "foundation is free to build", no runtime LLM). This is
    the single biggest gender-COVERAGE lever for the 77.5% -- BUT the honest cap is that 19c narrative
    refers to characters heavily by BARE SURNAME ("Darcy", "Bingley"), which a given-name gazetteer
    cannot gender. So a name-gender list raises coverage of the given-name subset only; surnames still
    need the honorific fallback (Mr/Miss, already counted in the 22.5%) or route (a) propagation.

(c) **Morphological number.** Singular vs plural mention (they/them vs he/she/it) is read directly off
the token. Number is a canonical retrieval cue (Wagers 2009; the attraction literature is largely a
NUMBER literature). Glass-box + payoff: YES, trivially; see Q3.

(d) **Animacy.** Animacy is a strong, cheaply-computed, early cognitive feature (the animacy hierarchy
is a cross-linguistic universal; Silverstein; Dahl & Fraurud 1996). It gates it (inanimate) vs he/she
(animate human) and, crucially, separates PERSON entities from non-person entities.
  - Dahl & Fraurud (1996): animate/human referents are pronominalized far more (human ~36% of definite
    NPs pronominal vs ~8% non-human in Swedish); animacy drives conceptual accessibility -> it is a
    first-class reference feature the brain uses, not a downstream detail.
  - Glass-box + payoff: YES and HIGH-coverage -- animacy is computable on EVERY mention (NER PERSON type
    / a person-noun lexicon / WordNet person hypernym), unlike gender's 22.5%. See Q3; this is the
    sleeper lever.

### One-line verdict for Q2
Brain-faithful AND glass-box WITHOUT an LLM, in coverage order: NUMBER (full) ~ ANIMACY (full) >>
cataphoric CLUSTER-propagation (entities that ever take a pronoun) > name/role GAZETTEER (given-name
subset only; static asset admissible; surname-heavy 19c caps it).

---

## Q3. Beyond gender: which cheap morphosyntactic / attentional cues is the binder under-using, ranked?

The brain does NOT compete a pronoun against every prior entity -- cue-based retrieval assumes a
SHARPLY LIMITED attentional focus, and Centering formalizes the "small active set". Feature agreement
then discriminates WITHIN that small set. The binder's "competes against every prior entity" is itself a
fidelity gap; several cues below attack it.

**1. SMALL-ACTIVE-SET restriction (Centering Cf window + recency/salience).**
  - Mechanism: the parser keeps a short, salience-ranked list of forward-looking centers (Cf), a few
    clauses deep; the pronoun preferentially binds the backward-looking center (Cb) / top-ranked recent
    Cf, NOT the whole discourse history (Grosz, Joshi & Weinstein 1995; Gordon et al. 1993; cue-based
    retrieval's limited focus, Lewis & Vasishth 2005). Hobbs (1978) confirms the power of the structural
    bundle: syntax + agreement + RECENCY + grammatical-role, with NO semantics, resolves ~88.3%
    (91.7% with a few selectional constraints; ~81.8% on genuinely ambiguous choices).
  - Glass-box + payoff: YES, and it is COVERAGE-INDEPENDENT (works even where every feature is missing).
    Directly fixes the stated bottleneck by shrinking the competitor pool to a recency/salience window.
    Note: the sibling binder ALREADY uses Cb for the binding step; here the lever is using the Cf/recency
    window to BOUND THE CANDIDATE SET, i.e. restricting SET SIZE rather than discriminating features.
    LARGE expected payoff -- set size, not within-set feature discrimination, is the dominating variable.

**2. PERSON (1st/2nd-person exclusion).**
  - Mechanism: in 3rd-person narration, "he/she/they/it" NEVER co-refer with I/we/you (narrator /
    addressee). Person is a phi-feature the parser tracks (Number+Person phi processing; Wagers 2009
    treats person/number as retrieval cues).
  - Glass-box + payoff: YES -- near-perfect reliability, full coverage, near-zero cost. CORPUS-MEASURED:
    the sibling gained +2.2 who-did-what by dropping mis-extracted "I"/"we" candidates. This is direct
    evidence that a cheap person-feature filter pays on THIS task -> promote it from a one-off drop to a
    principled person-agreement filter. LARGE-for-cost.

**3. ANIMACY.**
  - Mechanism: he/she require an animate (human) referent; a strong, early, cheap cognitive feature
    (Dahl & Fraurud 1996; animacy hierarchy). Prunes locations, objects, abstractions, and mis-extracted
    non-person "entities" out of the he/she competition.
  - Glass-box + payoff: YES, HIGH coverage (computable on every mention) -- and gender-INDEPENDENT, so
    it is ADDITIVE to the coverage-capped gender lever and pays exactly where gender is missing. Same
    flavor as the person filter that already gave +2.2 (prune wrong-TYPE candidates), which raises the
    prior that it pays. MODERATE-to-LARGE.

**4. NUMBER (they/them vs singular).**
  - Mechanism: canonical retrieval cue (Wagers, Lau & Phillips 2009). Singular they is RARE in 19c prose,
    so number is CLEANER on this corpus than on modern text -- plural pronouns reliably exclude singular
    entities and vice versa.
  - Glass-box + payoff: YES, cheap and reliable, but LOWER impact (plural-pronoun bindings are a
    minority of who-did-what items). MODERATE.

**5. GENDER (graded down-weight, cluster-propagated).**
  - Mechanism: a genuine but COVERAGE-CAPPED cue on this corpus (22.5% mention-level; ~archaic noise on
    the rest). Best amplified not by tagging more first mentions but by propagating cluster gender from
    the first bound pronoun (route Q2a).
  - Glass-box + payoff: YES as a DOWN-WEIGHT (Q1), not a delete. SMALL-to-MODERATE and coverage-capped;
    marginal value saturates once the active set is already small.

---

## Q4. Does better feature-agreement ALONE substantially improve human-level reference, or does it saturate?

**Answer: the STRUCTURAL bundle (small active set + recency + grammatical role) is a LARGE non-semantic
lever; feature AGREEMENT proper is a SMALLER filter whose marginal payoff SATURATES quickly once the
active set is small and the survivors share features. The residual hard cases are structurally
unresolvable by agreement and need coherence/semantics.**

### Evidence
- Hobbs (1978): ~88-92% with NO semantics -- BUT that number is carried mostly by SYNTAX + RECENCY +
  GRAMMATICAL-ROLE (the set-size/salience machinery), with gender/number agreement as a supporting
  filter. So "no-semantics resolution goes far" is a statement about the STRUCTURAL bundle, not about
  agreement in isolation.
- Agreement is a set-INTERSECTION operation: its value is entirely how many competitors it removes. Once
  Centering/recency has shrunk the pool to ~1-2 salient entities, an extra feature filter has little left
  to cut -- classic diminishing returns / saturation.
- The residual: two same-gender, same-number, same-animacy humans BOTH in the active set ("he" when
  Darcy and Bingley are co-present) is UNRESOLVABLE by any agreement feature and requires
  coherence/implicit-causality/world-knowledge (Winograd-schema-style; the AmbiCoref / implicit-causality
  literature; Hobbs coherence). On 19c narrative, which is dense with same-gender male characters, this
  residual is substantial -> agreement CANNOT close it.
- The one lever in this drill that does NOT saturate the same way is the SET-SIZE restriction (small
  active set / recency window): it is about the SIZE of the competition, not feature discrimination
  within it, and it pays even when every feature is missing -- which is precisely the 77.5% regime.

---

## BOTTOM LINE -- glass-box, non-LLM feature-agreement levers ranked by expected who-did-what payoff on 19c narrative

Ranked by expected payoff (all glass-box, no runtime LLM; PINNED = brain-mechanism established,
INVENTED = our parameterization to sweep):

1. **SMALL-ACTIVE-SET / recency-salience window (Centering Cf)** -- LARGE. Coverage-INDEPENDENT; directly
   fixes the "competes against every prior entity" fidelity bug by bounding the candidate pool. PINNED
   (limited attentional focus; Centering; Hobbs recency). The set SIZE dominates within-set feature
   discrimination. NOTE: distinct from the binder's existing Cb BINDING use -- here Cf bounds the
   CANDIDATE SET.
2. **PERSON (1st/2nd exclusion)** -- LARGE-for-cost, and the ONLY corpus-measured anchor (+2.2 already).
   Near-perfect reliability + full coverage + near-zero cost. Promote the one-off "drop I/we" to a
   principled person-agreement filter. PINNED (phi-feature).
3. **ANIMACY** -- MODERATE-to-LARGE. HIGH coverage (every mention) and gender-INDEPENDENT, so it is
   ADDITIVE and pays exactly where gender is absent. Same prune-wrong-TYPE flavor as the +2.2 person win.
   PINNED (animacy hierarchy; Dahl & Fraurud). Implement via NER PERSON / person-noun lexicon.
4. **NUMBER (they/them)** -- MODERATE. Cheap, reliable, cleaner on 19c than modern (rare singular they),
   but fewer plural-pronoun items. PINNED (canonical retrieval cue).
5. **GENDER (graded down-weight, cluster-propagated from first bound pronoun)** -- SMALL-to-MODERATE,
   COVERAGE-CAPPED (~22.5% mention-level). Use as a reliability-scaled DOWN-WEIGHT, never a hard delete
   (robust to the 77.5% missing regime AND brain-faithful). Amplify via cataphoric cluster-propagation,
   NOT by tagging more first mentions. A period name-gender GAZETTEER (static asset, admissible) raises
   the given-name subset but cannot gender the surname-heavy majority.

**Is any lever large enough to matter, or is agreement fundamentally coverage-capped?**
GENDER specifically is a small, coverage-capped lever on this corpus and its marginal value saturates.
BUT the question's framing ("feature-agreement") should be widened: the LARGE, non-saturating,
coverage-independent wins are the SET-SIZE restriction (small active set) and the PERSON filter, plus the
HIGH-coverage ANIMACY filter -- none of which depend on the 22.5% gender coverage. So the honest verdict
is: **do not pour effort into extracting more gender; pour it into (i) bounding the candidate set to a
recency/salience active set and (ii) full-coverage type filters (person, animacy). Keep gender as a
graded down-weight, cluster-propagated -- a cheap add-on, not the main lever.** This is consistent with
the decomposition already on disk (binding, via a small salient set, is the lever; the entity-side
feature richness is not).

---

## TLDR (plain language)
When the reader meets "he", it should not weigh that word against every character it has ever seen -- the
brain only ever considers a handful of recently-in-focus characters. The biggest cheap win is to shrink
that shortlist to the few most recently prominent characters (this needs no gender at all and fixes the
main problem directly). The next wins are simple type checks the reader can always make: never match a
"he/she" to the narrator's "I/we" (this already bought a measured gain), and never match "he/she" to a
place or an object (only to a person). Actual gender ("is this character male or female?") is only known
for about a fifth of the name mentions in this old-fashioned text, so it is a small helper, not the fix.
When gender IS known it should nudge the ranking, not hard-delete candidates -- because the tag is often
missing or wrong, and deleting the true character by mistake is worse than just down-ranking a few. The
one clean way to get more gender for free is to notice the first time a character is called "he" and
apply that to that character's earlier appearances.

## QUESTIONS
None. (The one open empirical fork -- how much of the who-did-what gap the set-size restriction alone
closes vs the type filters -- is a can-fail experiment for the solver, not a question for the owner.)

## NEXT STEPS (for the solver building the binder; NOT dispatched here)
1. Bound the candidate set to a recency/salience-ranked active window (Centering Cf) BEFORE feature
   scoring -- expected largest, coverage-independent lever; can-fail vs "compete-against-all" floor.
2. Add full-coverage type filters as graded cues: person (1st/2nd exclusion, generalize the +2.2 win)
   and animacy (NER PERSON / person-noun lexicon).
3. Make gender a reliability-scaled DOWN-WEIGHT (not a delete) and add cataphoric cluster-propagation
   (set cluster gender from the first bound pronoun, apply retroactively).
4. Optionally add a static period name-gender gazetteer for the given-name subset (static offline asset,
   no runtime LLM) -- lowest priority, surname-capped.
5. Attribute the lift: ablate each cue; the info-free twin (shuffled active set / random type tags) must
   LOSE; report CI half-width + null p95; recompute the floor on the same population.

---

## SOURCES
- Badecker & Straub (2002), JEP:LMC -- gender/number as violable retrieval cues, not a hard gate.
- Wagers, Lau & Phillips (2009), JML -- agreement attraction in comprehension; cue-based retrieval.
  https://www.academia.edu/615495/Agreement_attraction_in_comprehension_representations_and_processes
- Dillon, Mishler, Sloggett & Phillips (2013), JML -- contrasting intrusion profiles (cue weighting).
- Gonzalez Alonso et al. (2021) -- gender attraction in comprehension.
  https://centaur.reading.ac.uk/96364/1/Gonzalez%20Alonso%20et%20al%202021.pdf
- Lewis & Vasishth (2005), Cognitive Science -- ACT-R cue-based retrieval; similarity interference.
- Grosz, Joshi & Weinstein (1995) -- Centering; Cf/Cb, the small active set.
  http://matt-gardner.github.io/paper-thoughts/2012/08/27/centering.html ;
  Walker, Joshi & Prince (1998) overview: https://ccl.pku.edu.cn/doubtfire/NLP/Discourse_Analysis/Centering_Theory/Walker_Joshi_Prince_98_centering.pdf
- Gordon, Grosz & Gilliom (1993) -- repeated-name penalty; focus as live state.
- Hobbs (1978) naive algorithm -- ~88.3% (91.7% w/ selectional), 81.8% on ambiguous; syntax+agreement+
  recency, no semantics. (Mitkov 1999 survey: https://www.sfu.ca/~mtaboada/lot/readings/Mitkov_1999.pdf)
- Dahl & Fraurud (1996), Animacy in grammar and discourse -- animacy as cheap accessibility cue.
  https://www.semanticscholar.org/paper/Animacy-in-grammar-and-discourse-Dahl-Fraurud/9b4a1a82cebccfb1626b988c8687e3254356880d
- Kreiner, Sturt & Garrod (2008) -- definitional/stereotypical gender in reference; cataphoric assignment.
  https://www.sciencedirect.com/science/article/abs/pii/S0749596X07001040
- Kazanina et al. (2007) / active search in cataphora: https://pmc.ncbi.nlm.nih.gov/articles/PMC4627476/
- Osterhout, Bersick & McLaughlin (1997); Carreiras, Garnham, Oakhill & Cain (1996) -- stereotype gender.
- AmbiCoref / implicit-causality residual (agreement cannot resolve same-feature competitors):
  https://arxiv.org/pdf/2509.14456
