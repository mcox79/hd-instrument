# EXPOSITORY vs NARRATIVE reading gap -- drill synthesis (director fold of 3 lit-scans)

**Filed:** Director, 2026-07-18. **Status:** research synthesis, HYPOTHESIS-pending (P_deflated ~0.5; lit-scans flagged own uncertainties). Drills: expository-linguistics/comprehension (ab76d2a6), genus/definition-extraction (a7ef8df6), scientific-IE-ceiling/macro (a80a1228). Parent a7415c0a fanned out; director synthesized.

## The negative drilled
Reader is validated ONLY on grade-2/3 NARRATIVE. The ONE expository attempt (biology re-reading ddfd17f34) HARD_FAILED at ~0.40 with wrong-GENUS errors. USER goal = read textbooks. This characterizes WHY expository is harder + whether the learned-reader plan covers it.

## Verdict: 1 fix (covered), 3 real MISSING components, 1 real bound, narrative-first

**COVERED-with-addition -- the genus fix (our specific negative):**
- Wrong-genus (grabbed a string-near noun) is a DOCUMENTED Hearst-pattern failure. Fix = dependency-path from definiendum to genus (NOT adjacency; DHPs/Roller-Kiela) + TAXONOMIC-COHERENCE gate (reject a genus inconsistent with the known is-a hierarchy; OntoLearn/WebIsA pruning). Catches polysaccharide->acid directly. Human syntactic-bootstrapping = same shape (syntax proposes candidates, semantic-type filters prune). MAPS onto the plan: definition = a learned construction (WCL span-labeling, not fixed rules) + the coherence-gate pointed at the taxonomy. LARGELY COVERED.

**MISSING pieces (do NOT transfer from narrative -- must be added for textbooks):**
1. **TECHNICAL-TERM GROUNDING (HIGH).** Base-first assumes vocab pre-grounded (true for grade-2). In textbooks new terms are NOT pre-grounded -> the ~98% coverage threshold FAILS. Fix = define-then-ground bootstrap (learn the term from the text's OWN definition, then use it). The base-first grounding assumption BREAKS on expository; this is the biggest deviation.
2. **NOMINAL/BRIDGING COREF (HIGH).** In narrative, PRONOUNS dominate (what we built: deixis/pronoun coref). In science text, NOMINAL/definite-NP + BRIDGING reference dominates ("the enzyme... the reaction... this process"), over very long chains (CRAFT: >23% links span up to 12k words). Our pronoun-centric coref does NOT transfer. New component (often KB-augmented).
3. **DE-NOMINALIZATION (MED).** Science prose packs events into noun phrases ("the crystallization of X" = Halliday grammatical metaphor). Need an unpacking step to recover predicate-argument ("X crystallizes") before the relation is extractable. Not in the plan.

**SPECULATIVE (lit gap -- treat as hypothesis, NOT a planned component):**
- MACRO-STRUCTURE (Meyer's 5 expository structures: compare/contrast, cause/effect, etc.). RST parsing is mature but the Meyer-taxonomy computational version is UNDERSTUDIED. "section-structure disambiguates sentence relations" = a hypothesis to test, not an established technique.

**REAL BOUND (honest ceiling):**
- Unsupervised/weakly-grounded scientific relation+hypernym extraction runs ~15-25 F1 BELOW supervised (distant-sup ~43 vs supervised ~61; even SemEval domain winners needed hybrid supervised+unsupervised). So learn-from-near-nothing on technical text will be substantially sub-supervised. Fair-bar, not a failure.

## Brain-check + recommendation: NARRATIVE-FIRST (brain-faithful)
Humans ALSO find expository harder + knowledge-gated, and acquire it YEARS LATER, layered on narrative fluency (Chall's stage-3 "reading to learn"; the 4th-grade shift). So narrative-first is the brain's own curriculum, not a shortcut. RECOMMENDATION:
- Build the learned NARRATIVE reader first (grounded vocab + pronoun coref + event situation-model) = Stage-2 as planned.
- Treat EXPOSITORY as a SEPARATE LATER LAYER (the "reading to learn" stage) with its own named components: technical-term grounding-from-definitions + nominal/bridging coref + definition-as-construction + taxonomy-coherence gate + de-nominalization.
- Textbooks WAIT until the narrative reader works. BUT: design Stage-2 so it does NOT bake in narrative-only assumptions that block those additions (esp. keep coref + grounding + the coherence-gate extensible to nominal/bridging + technical-term-bootstrap + taxonomy).

## Caveats
Lit-synthesis, hypothesis-pending. Scans flagged: exact WCL/coverage numbers unverified; genus-in-definitions not isolated in human literature; Meyer-macro-structure computationally understudied (speculative). Established+well-cited: SciERC/ScienceIE (term-typing), CRAFT (nominal-coref-dominates), distant-vs-supervised F1 gap. Does not need a heavy cert-VET (research characterization, not an experiment verdict); load-bearing pieces re-checkable against the cited datasets if a build depends on them.
