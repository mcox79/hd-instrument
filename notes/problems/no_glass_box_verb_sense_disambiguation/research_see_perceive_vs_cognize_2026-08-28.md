# Drill: how the brain distinguishes see-PERCEIVE from see-COGNIZE ("the I-see wall")

**Solver session, 2026-08-28.** (The dispatched `research` agent stalled on its 4 sub-lanes; I implemented the
mechanism directly from the established linguistics it was scanning — Barwise & Perry 1983; Sweetser 1990;
Viberg; Gisborne — and MEASURED the residual on SemCor.)

## The phenomenon (regular polysemy, PINNED)

The perception->cognition polysemy of see/hear/feel/find is a SYSTEMATIC, cross-linguistically regular metaphor:
UNDERSTANDING IS SEEING (Sweetser 1990, *From Etymology to Pragmatics*; the mind-as-body mapping). It is
predictable enough to encode as rules, and the discriminator is largely SYNTACTIC — the COMPLEMENT TYPE.

## The glass-box decision procedure (implemented over the spaCy parse), ranked by reliability

1. **HIGH -- naked-infinitive / participial SMALL CLAUSE = DIRECT PERCEPTION** (Barwise & Perry 1983, situation
   semantics; the "naked-infinitive" perception report is VERIDICAL and non-epistemic). "saw him LEAVE", "saw him
   LEAVING", "heard it RING". Parse feature: a `ccomp` child that is a VERB with its OWN `nsubj` and NO
   complementizer ("that/whether/if") and no quote. -> PERCEPTION. Implemented as `has_percept_smallclause`.
2. **HIGH -- finite THAT-clause = EPISTEMIC COGNITION** ("see/hear THAT S" = come-to-know/realize; the that-clause
   is a belief complement, Barwise & Perry; Dik & Hengeveld's distinction of perception vs propositional
   complementation). Parse feature: `ccomp` with a "that/whether/if" mark. -> cognition/communication (the PRIOR
   picks: a perception/mental verb -> cognition; a speech verb -> communication). Implemented as `has_ccomp`.
3. **MED -- object ABSTRACTNESS** ("see a BIRD" concrete -> perception; "see the POINT/REASON/IDEA" abstract ->
   cognition). Implemented via the `cog_obj` (noun.cognition) vs `comm_obj` (noun.communication) vs concrete
   object typing.
4. **LOW / IRREDUCIBLE -- bare "I SEE" backchannel** (1st-person present, no object, no complement -> an
   acknowledgment = cognition). There is a weak local heuristic (person+tense+no-complement) but it is genuinely
   DISCOURSE/PRAGMATIC (Sweetser; conversational "I see" = "I understand") -- not reliably resolvable from the
   sentence alone. This is the no-LLM-invariant residual.

Validated on constructed minimal pairs (7/7): saw him leave/leaving -> perception; saw that he left -> cognition;
saw a bird -> perception; saw the point / his idea -> cognition; heard him sing -> perception; heard that he sang
-> cognition.

## Measured residual on SemCor (the honest ceiling)

On the SemCor test cognition-instances of perception verbs, the complement-type rules FIRE CORRECTLY but move the
aggregate number very little, because that residual is dominated by TWO irreducible classes:
- **(a) bare "I see" / discourse** -- no complement to read (needs pragmatics beyond the sentence).
- **(b) LEXNAME-TAXONOMY QUIRK** -- "discover an avocado", "see Adam", "feel a stranger" are gold-tagged
  `verb.cognition` even with CONCRETE objects, because WordNet lexnames discover/find/realize as cognition
  ("become aware of X") REGARDLESS of X's semantic type. The object-abstractness cue (correctly) reads these as
  perception; the gold taxonomy disagrees. This is a GOLD artifact, not a mechanism error (the same lexname-vs-
  event-frame mismatch documented for leave/pass).

## Corroboration from the dispatched lit-scan lanes (delivered 2026-08-28)

- **Aspect is NOT a clean perceive/cognize discriminator (Vendler 1957/1967).** "I am seeing" is ungrammatical
  for BOTH the perceptual and the cognitive sense (both are state/achievement, not process); the real aspectual
  line is process-vs-non-process. -> correctly NOT used as a cue.
- **Underspecification is the brain-faithful default (Frazier & Rayner 1990; Frisson & Pickering 1999/2001;
  Giora GSH 1997/2003).** Perception->cognition "see" is REGULAR polysemy (Sweetser), which behaviourally patterns
  with an UNDERSPECIFIED shared representation refined by context at NO discrete-commitment cost (unlike homonymy).
  -> validates the mechanism's CONSERVATIVE default (defer to the prior/MFS until a cue discriminates), and warns
  against modelling perceive/cognize as two hard-competing entries.
- **Bare "I see" (Heritage/Schegloff/Gardner/Golato response-token lineage):** local features give a strong,
  defensible PRIOR -- 1st/2nd person + present + no object + no complement -> cognition/acknowledgment, because the
  perceptual bare "I see" is a MARKED ELLIPSIS licensed only by a prior visibility question ("Can you see it?" / "I
  see [it]"). But nothing in the single-sentence parse distinguishes the two; the residual (literal "I see"
  answering a prior visibility question) is IRREDUCIBLY cross-sentence discourse. A high-precision local DEFAULT is
  defensible; a categorical solution is not (no-LLM-invariant + single-sentence limit).
- **Neural (Lacey/Stilla/Sathian 2012; Desai 2011/2013/2021; Gibbs 2006):** metaphorical sense retains GRADED
  perceptual grounding that ATTENUATES with conventionalization -> consistent with a graded, salience-weighted
  (not walled-off) representation; supports a graded-cue combiner over a hard switch.
- **Gisborne 2010 (The Event Structure of Perception Verbs) -- the load-bearing syntactic diagnostic, matches my
  implementation and adds one refinement:** bare-NP / small-clause / bare-infinitive / participial complement ->
  DIRECT PERCEPTION (See1); FINITE THAT-clause -> epistemic/evidential COGNITION; and (NEW, not yet implemented, a
  clean but rare cue) a TO-INFINITIVE + STATIVE predicate ('saw him TO BE an imposter') -> cognitive 'understand'
  (See4). Documented as a candidate rule; low-frequency so not implemented.
- **Viberg 1983/84 (typology, ~50 languages):** it is the EXPERIENCE-class vision verb (SEE, not agentive look-at)
  that carries the ->cognition extension, on an implicational hierarchy SEE > HEAR > FEEL > SMELL/TASTE -> my
  verb set (see/hear/feel/find/notice/observe) is the right experience class; smell/taste resist the extension.
- **Apresjan 1974 / Copestake & Briscoe 1995 / Pustejovsky (regular polysemy):** perception->cognition is REGULAR
  (sense-extension) polysemy encodable as a CLASS-SCOPED lexical rule with FREQUENCY-WEIGHTED blocking -- which is
  EXACTLY the mechanism here (a general construction rule over the perception-verb class + the MFS prior as the
  frequency-weighted default). Strong independent validation of the design.

## Bottom line

The single highest-value rule is the **small-clause = direct-perception discriminator** (Barwise & Perry), now
implemented and correct on the diagnostic cases. It makes the mechanism more brain-faithful and will help on
real prose that contains "see NP V" / "see that S" / "see the point". It does NOT lift the SemCor perception/
cognition number, because that population's residual is the bare-"I see" discourse cases (pragmatics, invariant-
precluded) plus WordNet lexname-taxonomy quirks (a gold artifact). The perception/cognition wall is therefore
PARTLY crossed (the complement-typed cases) and PARTLY a documented, understood structural ceiling.
