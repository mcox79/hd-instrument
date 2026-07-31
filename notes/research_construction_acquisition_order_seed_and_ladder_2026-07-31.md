# Research Drill C — Developmental acquisition order of constructions: seed set + difficulty ladder

Filed by: research (Sonnet). 2026-07-31.
Governing constraint: brain/human-foundational first; glass-box always (USER 2026-07-31).
Prior threads consulted: `notes/research_grammar_construction_resources_for_role_assignment_2026-07-20.md`,
`notes/research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`,
`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md` (Broca's/position-default
finding), `notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md`.
Curriculum artifact checked directly: `data/corpora/mcguffey_graded/manifest.json` + `grading_report.json`.

## HEADLINE

Human acquisition order is well-documented and gives a near-total answer to "what's next": children master
**reference (naming/entity individuation) -> canonical agent-patient thematic roles (SVO) -> negation/wh-questions
-> LOCAL cross-clause binding (Principle A, reflexives) -> DISCOURSE coreference/pronoun resolution (still
error-prone to age 6-7) -> non-canonical role order (passives, object-relatives — late, age 4-6+, and the
"revise-the-default-parse" cost never fully disappears even in adults) -> complement/adverbial clauses ->
conditionals/discourse connectives (age 4+) -> full causal/intentional situation-model integration (school-age
and beyond)**. This is not one study but a convergent macro-sequence across five independent research programs
(Brown 1973, Tomasello 2003, Diessel 2004, Chien & Wexler 1990, MacWhinney's Competition Model), each individually
well-established, stitched into a single ordered chain at LOW-MEDIUM confidence as a *unified* sequence (each
step is solid; the total ordering is a synthesis). Recommended competency #3 = **cross-sentence coreference /
entity re-identification under pronoun+definite-NP reference**, built directly on competencies #1 (entity-identity)
and #2 (thematic-roles), and it is developmentally EARLIER and mechanistically SIMPLER than non-canonical role
order (passive/object-relative) — so the McGuffey curriculum order (roughly monotonic lexical/syntactic
difficulty by grade) is broadly right-shaped but needs one explicit correction: it does not yet expose or grade
constructions by SYNTACTIC type (passive frequency, relative-clause density, coreference-chain length) — only by
lexical/surface metrics — so a construction-level annotation pass is needed before the ladder can be trusted for
ordering constructions #4+ (non-canonical role order) correctly.

## Cheap decisive test

Before committing engineering effort to competency #3 (coreference), run one cheap corpus check that is fully
decisive about WHETHER competency #2 (thematic-roles) is actually a prerequisite substrate for #3, matching the
Kintsch/Zwaan claim that "you need to know 'she'=Mary before you can link the proposition containing 'she' to
the proposition containing 'Mary'":

- Take the trained competency-#2 module (thematic-role assignment on canonical/active sentences), freeze it, and
  measure cross-sentence coreference accuracy on McGuffey g1-g2 passages with pronoun chains, USING the frozen
  role-assignment output as a feature vs NOT using it (ablation).
- **HARD-PASS**: role-conditioned coreference accuracy beats role-blind by >=10 points absolute AND both beat a
  recency-only baseline (most-recent-matching-gender-NP) by >=5 points. This confirms role-assignment output is
  a genuine substrate for coreference, matching Kintsch's textbase-construction dependency claim, and licenses
  building competency #3 as a module that CONSUMES competency #2's output rather than a fresh independent module.
- **HARD-FAIL**: role-conditioned and role-blind are statistically indistinguishable (<3 points), or recency-only
  baseline already saturates McGuffey g1-g2 pronoun chains (>90% accuracy) — meaning g1-g2 pronoun resolution is
  too easy (short chains, one candidate referent) to be a discriminating test at all, and the real test must move
  to g3+ where multiple same-gender referents appear. Cost: ~1 day corpus annotation + 1 cheap eval script, no
  new training run required if #2's module already exists.

## Falsifiable predictions

1. **Order prediction (macro-sequence).** If the substrate's construction-competency library is built in
   developmental order, then training/exposing competency N+1 AFTER competency N is fully consolidated will show
   FASTER acquisition (fewer curriculum passes to reach criterion) than training N+1 from scratch without N, for
   the pair (role-assignment -> coreference) specifically.
   - HARD-PASS: >=20% reduction in passes/steps-to-criterion for coreference when role-assignment competency is
     already consolidated vs a from-scratch control.
   - HARD-FAIL: no measurable difference (<5%) — would falsify the "coreference builds on roles" dependency claim
     and imply competency #3 should be chosen independently of #2's output.

2. **Non-canonical-order-is-hard prediction.** The already-measured encoder finding (frozen v2 MLM cross-voice
   agent/patient probe = 0.18/0.16, BELOW chance 0.50, "position-default" — see
   `notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`) is the textbook
   Broca's-aphasia / canonical-sentence-strategy signature (Bever 1970; Caramazza & Zurif 1976). Prediction: this
   same failure mode will resurface, structurally identically, whenever competency-N training exposes
   non-canonical role order for the FIRST time (passives, object-relatives, object-clefts) — i.e. it is not an
   encoder-specific bug but the generic default-position-binding-must-be-overridden mechanism that also makes
   these constructions late/hard for children and effortful for adults.
   - HARD-PASS: when a future "non-canonical role order" competency is trained, its LEARNING CURVE shows the same
     shape as competency #2's canonical-order curve did — i.e. it eventually reaches criterion, just later/slower
     — matching "children DO eventually master passives, just late" rather than a permanent ceiling.
   - HARD-FAIL: the non-canonical-order competency shows a hard ceiling well below competency #2's asymptote even
     with matched training budget — would indicate a genuine architectural (not just curriculum-ordering)
     limitation requiring the override mechanism itself (voice-morphology-triggered role reassignment) to be
     built as its own explicit mechanism, not just "more of the same training."

3. **Curriculum-grading prediction.** If McGuffey g1-g6's ACTUAL construction-type distribution (passive rate,
   object-relative rate, pronoun-chain length, distinct-referent count per passage) is annotated, it should track
   grade level in the SAME direction the lexical metrics already confirmed do (g1: 100% grade-1-vocab coverage,
   falling monotonically to 60.7% by g6, per `grading_report.json`).
   - HARD-PASS: passive-clause rate and object-relative rate both show a positive, statistically detectable
     (not necessarily strictly monotonic — g1 lexical/sentence-length metrics have one dip at g5 already) trend
     from g1 to g6.
   - HARD-FAIL: passive/relative-clause rates are flat or NON-monotonic across grades (i.e., McGuffey grades by
     vocabulary but NOT by syntax) — this is a live possibility per the lit-scan (readability formulas like
     Flesch-Kincaid measure sentence length + syllables, NOT subordination/passive/relative density — several
     corpus studies flag this as a real gap between formula-grade and construction-grade). If HARD-FAIL, the
     curriculum needs a supplementary construction-complexity annotation and possibly re-ordering within grades
     (some g1 passages may contain passives that a strict acquisition-order curriculum would defer, and some g4+
     passages may be construction-simple despite higher lexical score).

## Cross-thread synthesis

- **Ties directly to the certified encoder-wall finding** (`brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`):
  the measured cross-voice below-chance inversion is EXACTLY the developmental/adult canonical-sentence-strategy
  literature's signature (Bever 1970's canonical sentence strategy; Ferreira 2003's "misinterpretation of
  noncanonical sentences" showing the SAME agent-first bias persists in adults under any load; Caramazza & Zurif
  1976's Broca's-aphasia parallel already cited in that note). This is now triple-grounded: brain lesion data,
  adult psycholinguistic processing data, AND child-acquisition-order data all point to the same mechanism — a
  fast default positional agent-first binding that requires active, effortful, LATE-maturing override by
  voice/case/agreement cues. The substrate's failure is not a bug to patch with more data; it is the textbook
  starting state before the override mechanism is built. This substantially raises confidence (from the prior
  note's single brain-lesion analogy) that the fix is a dedicated OVERRIDE mechanism (voice-morphology-triggered
  role reassignment), not more canonical-order training data.
- **Ties to `research_dynamic_reindexing_voice_invariant_role_2026-07-30.md`**: that note already names
  "position-default heuristic (first-NP=agent)" as failure arm (C) in its own falsification design — this drill
  supplies the independent developmental-literature confirmation that arm (C) is not an idiosyncratic training
  artifact but the universally-observed human default state pre-override.
- **Ties to `research_grammar_construction_resources_for_role_assignment_2026-07-20.md`** and
  `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md` (not re-read in full this
  cycle per KB-check discipline — both are scoped to competency #2's construction, not acquisition ORDER, so no
  duplication; this drill is complementary, not redundant).
- **MacWhinney's Competition Model is the single most substrate-relevant unifying frame** found this cycle: cue
  validity (availability x reliability) predicts BOTH why English passives are hard (word-order cue is dominant
  and gets reversed) AND gives a general recipe for ordering ANY future competency — rank constructions by how
  strongly they conflict with an already-entrenched high-validity cue in the substrate's own training distribution,
  not by a fixed universal list. This is a testable, substrate-native (not borrowed-mechanism) design principle.

## Substrate-product implications

1. **Concrete competency #3 recommendation: cross-sentence coreference / entity re-identification via
   pronoun + definite-NP reference**, consuming competency #2's role-assignment output as an input feature
   (per the cheap decisive test above), not built as an independent from-scratch module. This is earlier and
   easier than passive/non-canonical-role-order per the acquisition literature (DPBE resolves ~6-7yrs but the
   COARSE recency/parallelism-based coreference strategy is present very early, well before passive mastery at
   4-6yrs+) and it directly extends the growing-library philosophy: same modular-allocation pattern as
   competency #1->#2, now #2->#3 with an explicit CONSUMES-edge between modules (a new structural pattern worth
   keeping — competencies may form a DAG, not just a flat list).
2. **Non-canonical role order (passive, object-relative, object-cleft) should be competency #4 or later, NOT #3.**
   It is developmentally late (age 4-6+, later than coreference's coarse early strategies), requires an explicit
   OVERRIDE mechanism (not just more exposure), and the substrate has ALREADY hit this exact wall (below-chance
   cross-voice probe) — meaning when we do build it, budget for a dedicated override-mechanism design (voice/case
   morphology gating a role-reassignment step), not incremental fine-tuning of the existing position-default
   module. This reframes the prior "voice-invariant role" thread's problem correctly: it is not competency #2
   generalizing poorly, it is the NEXT competency (non-canonical override) not yet existing.
3. **Curriculum ordering DOES matter now (unlike single-competency probes where order gave no benefit)**: because
   competencies form a dependency chain, presenting McGuffey material in an order that FIRST saturates canonical
   role-assignment + coreference before densely exposing passives/relatives should measurably speed acquisition
   of the harder competency (falsifiable prediction #1 above) — this is the first curriculum-ordering claim in
   this program that is both brain-grounded and internally testable.
2. **McGuffey g1-g6 needs a syntactic-construction annotation pass** (passive rate, relative-clause rate,
   pronoun-chain length/referent count per passage) as a NEW, cheap corpus-processing step — current
   `grading_report.json` only tracks lexical/surface metrics (sentence length, syllables, Flesch-Kincaid, vocab
   coverage), which the lit-scan confirms is a KNOWN gap between readability-formula grade and construction
   grade. Until this exists we cannot verify or trust that g1-g6 syntactic difficulty tracks acquisition order;
   it may (basal-reader traditions do informally simplify syntax) or may not (formulas don't enforce it). This is
   a concrete, cheap (corpus-only, no training) next step that directly resolves falsifiable prediction #3.
4. Recommended MUTABLE SEED SET (predefine these; let the system self-discover finer sub-types within each):
   1. entity-identity (CERTIFIED)
   2. thematic-roles / canonical agent-patient-action (IN PROGRESS)
   3. cross-sentence coreference (pronoun + definite-NP reference), consuming #2 — RECOMMENDED NEXT
   4. non-canonical role order (passive, object-relative, cleft) — requires override mechanism, defer until #3 solid
   5. negation and polarity (developmentally early, ~parallel to #2/#3, cheap, should be picked up opportunistically
      whenever curriculum density permits rather than strictly gated behind #3/#4)
   6. complement/adverbial clause structure (finite complements: think/know/want — earliest complex-clause type
      per Diessel; should follow #4, not precede it)
   7. conditionals + discourse connectives (age 4+, later than #6)
   8. full situation-model integration: causal event chains + protagonist/goal tracking across a narrative
      (Kintsch/Zwaan's situation-model level) — LAST, since it requires #3 (entity chains) as textbase input plus
      #6/#7 (causal/conditional clause structure) as its event-linking vocabulary.
   DO NOT predefine finer sub-competencies within each (e.g. don't hand-split "passive" from "object-cleft" a
   priori) — let curriculum exposure drive within-competency differentiation per the modular-allocation philosophy
   already adopted for #1/#2.

## Citations (verified count: 27 unique sources across 3 parallel lit-scans)

Developmental order / morpheme & construction acquisition:
- Brown, R. (1973). *A First Language*. 14-morpheme MLU-stage order (Stage I-V).
- Tomasello, M. (2003). *Constructing a Language*; Verb Island hypothesis (Tomasello 1992).
- Ninio, A. "No Verb Is an Island" (contests strong verb-island insularity).
- Goldberg, Casenhiser & Sethuraman (2004). Construction learning via Zipfian frequency distribution.
- Diessel, H. (2004). *The Acquisition of Complex Sentences*; Diessel & Tomasello (2001) finite complements.

Non-canonical order / passive / relative-clause difficulty:
- Bever, T. (1970). Canonical sentence strategy.
- Ferreira, F. (2003). Misinterpretation of noncanonical sentences (adult residual bias).
- Maratsos et al. (1985); Horgan (1978). Short/actional-verb passives precede full/non-actional passives.
- Borer & Wexler; Wexler "By the Way, Children Don't Know By" — maturational account of full-passive lag.
- Gibson (1998, 2000). Dependency Locality Theory.
- Van Dyke & Lewis. Similarity-based interference in retrieval.
- Frazier & Clifton; Aoshima et al. (2002). Active Filler Strategy.
- MacWhinney & Bates. Competition Model — cue validity (availability x reliability).
- Chan et al. Children's understanding of agent-patient relations (cue competition cross-linguistic).
- Caramazza & Zurif (1976); Grodzinsky. Broca's-aphasia trace-deletion parallel (already cited in prior encoder note).

Coreference / situation models / graded readers:
- Chien & Wexler (1990). Delay of Principle B Effect.
- Arnold, Brown-Schmidt & Trueswell tradition. Discourse prominence in pronoun resolution ("Who's she?").
- Hartshorne & Snedeker (2012). Implicit-causality verb bias.
- Kintsch (1988); Kintsch & van Dijk (1978). Construction-Integration model, textbase/situation-model levels.
- Zwaan, Langston & Graesser (1995); Zwaan & Radvansky (1998). Event-Indexing Model (5 dimensions).
- Readability-formula critiques: Flesch-Kincaid/Lexile measure lexical/surface features, not construction type
  (multiple corpus studies flagged in lit-scan, e.g. Hsiao et al. on complex syntax in children's books; BUCLD46
  passive-frequency-in-children's-books study).

Calibration note (per [[feedback-lit-scan-calibration-penalty]]): each INDIVIDUAL claim above is well-established
(textbook-level for Brown/Chien-Wexler/Gibson/MacWhinney/Kintsch/Zwaan). The UNIFIED macro-sequence and the
substrate-mapping claims (competency DAG, cue-validity-as-ordering-principle, curriculum-ordering-now-matters)
are my own synthesis layered on top — deflating those specifically by 0.20 per the mandatory penalty.

## P estimates (deflated)

- P(coreference is the correct competency #3, i.e. developmentally next after roles) = 0.60 (raw ~0.80, -0.20
  calibration; well-supported by acquisition-order literature but the CONSUMES-#2 architecture claim is untested)
- P(non-canonical role order requires a dedicated override mechanism, not just more training) = 0.55 (raw ~0.75,
  -0.20; strongly analogically supported by brain+adult+child convergence but not yet substrate-tested)
- P(McGuffey g1-g6 syntactic complexity already tracks acquisition order without supplementation) = 0.35 (raw
  ~0.50, -0.15; readability-formula literature explicitly flags this as unverified/likely gap) — capped below
  0.50 per novel-synthesis cap since this is an untested extrapolation to a specific corpus.
- P_deflated (overall headline confidence) = 0.50

## Next-drill candidate

`mcguffey_construction_annotation` (new, cheap, corpus-only field): annotate McGuffey g1-g6 for passive rate,
relative-clause rate, and pronoun-chain/referent-count per passage, to directly resolve falsifiable prediction #3
above. This is NOT a literature drill — it's a corpus-processing task best handed to exp_dev/skunkworks as a cheap
script, not re-dispatched to research. Secondary research candidate if capacity allows: implicit-causality verb
bias acquisition timing vs syntactic-cue acquisition timing (flagged medium-confidence gap in Q1 above) — would
sharpen the ordering between competency #3's sub-cues (recency/parallelism vs semantic-verb-bias), useful once
competency #3 is under construction and needs its own internal difficulty ladder.
