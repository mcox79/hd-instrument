---
problem: world_knowledge_common_noun_to_name_bridge_the_81_percent_residual
status: PARTIAL
bar: "PASS = a brain-foundational world-knowledge route on the RIGHT axis (glass-box, NO external LLM at inference; an offline static KB is admissible), measured ONLY on the HONEST de-leaked floor, that lifts name-bridge coref (common-noun -> proper-name) CI-separated over the strongest floor (recency + text-stated / two-route-without-the-new-knowledge, recomputed on the same GUM name-bridge slice), with the info-free twin (shuffled-KB) LOSING and no regress on pronoun / same-head / named consumers. Report CI half-width + null p95; recompute floors on the item's own population; 19c is NOT load-bearing. A rigorous located NEGATIVE is a FULL PASS if it names the exact world-knowledge axis the residual needs (with counts by axis: relational vs role vs kinship vs attribute) and why the available brain-foundational sources do/don't cover it. Strategy lands the Q111 wire, witnessed."
result: "GUM OntoGUM coref (modern), name-bridge slice = anaphoric common-noun with a proper-name antecedent, ALL GUM n=356 (zero fitted params, DBpedia+Wikidata are external), item-level paired bootstrap 2000x, metric = argmax-pick eid == gold eid. RIGOROUS LOCATED NEGATIVE (the bar's blessed full pass), plus a small twin-clean fidelity improvement that is NOT CI-separated. THE AXIS (counts, on the 154 two-route misses): the brief's hypothesized RELATIONAL(8)+KINSHIP(5)+AGE_GENDER(10)=23 is only 15% of misses; the DOMINANT residual axis is encyclopedic ENTITY-TYPE -- OTHER 56 / GEO 38 / ORG 16 / OCCUPATION 17 (91/154=59% is place/org/thing-type, not person-relational). By residual REASON: not_in_kb 101 (66%), typed_not_licensing 39 (25%), licensed-but-misranked 14 (9%). THE WALL IS COVERAGE, NOT MECHANISM (proved by oracle): give gold its true type and the graded-competition SELECT scores 1.000 (distractors untyped) / 0.924 (distractors real-typed) -- retrieval is near-perfect; the whole gap is knowledge. The coverage ceiling of ALL static knowledge (DBpedia InstanceOf UNION the Wikidata P31/P106 probe UNION Bruce-Young name recognition UNION in-text is-a) is 0.697 -- 30% of gold entities (108/356) are DOCUMENT-LOCAL (Betty, Gram, Koinonia, Chao, obscure local towns), in NO static KB. THE STATIC-KB CEILING IS EMPIRICALLY CAPPED: the Wikidata probe was fetched FOR THESE EXACT gold surfaces (a static-KB upper bound) and lifts the strongest prior arm kb_thematic 0.5843 only to wk_reco_wd 0.5926 = +0.0084 CI[-0.0112,+0.0281] NOT CI-sep -> no static-KB acquisition can CI-separate on this slice. The completed brain-foundational arm (name recognition + broader KB + phi gate-then-compete) wk_phi 0.5926 beats its shuffled-KB twin +0.1152 CI-sep (the correspondence is load-bearing, real signal) but the floor +0.0084 NOT CI-sep -> a twin-clean fidelity improvement, not a capability win."
floor: "Strongest floor actually run, recomputed on the item's own GUM population (n=356): kb_thematic = 0.5843 (the two-route CLS -- consolidated DBpedia KB UNION episodic in-text is-a -- PLUS deverbal-agent thematic route PLUS graded constraint-integration competition; the strongest PRIOR arm from acquire_wikidata_p31 SOLVED). Weaker floors: kb_intext (two-route CLS without thematic) 0.5674; recency-over-names (Centering) 0.4719; string-identity / WordNet-only 0.000 by construction. The bar's 'two-route-without-the-new-knowledge' = kb_intext/kb_thematic; I beat neither CI-sep."
controls: "(1) INFO-FREE SHUFFLED-KB TWIN: wk_phi 0.5926 beats its shuffled-KB twin 0.4774 by +0.1152 CI-sep -> the name->type correspondence is load-bearing (not 'any type-token helps'); the +0.0084 whole-slice signal is real, just coverage-bounded. (2) ORACLE (excludes 'SELECT is the bottleneck'): gold always type-licensed, distractors untyped -> 1.000; distractors real-typed -> 0.924 -> the graded-competition retrieval is near-perfect; knowledge coverage is the wall, not the mechanism. (3) COVERAGE CEILING (excludes 'a bigger static KB fixes it'): reachable-by-ALL-static-knowledge = 0.697; the Wikidata probe FITTED to the eval surfaces (upper bound) adds only +0.0084 not-sep. (4) DISCOURSE COARSE-TYPE LOCATED NEGATIVE (excludes 'infer type from discourse predicates'): locative->PLACE typing disc_place 0.556 does NOT beat kb_thematic (-0.0253, hurts) and does NOT beat its own shuffled twin (-0.0056, not-sep) -> coarse discourse typing OVER-LICENSES (many distractors are also loc-mentioned); fine encyclopedic types are needed, not coarse ones. (5) ABSTENTION-SAFE / NO-REGRESS: on items with NO knowledge signal, wk_phi == recency exactly (0 diffs) -> the route can only narrow, never override recency with nothing; pronoun/same-head consumers are untouched (this is the standalone name-bridge instrument, a different population from those consumers). (6) AXIS DECOMPOSITION reproduces the brief's requested counts and REFUTES its hypothesized axis (relational/kinship/age-gender = 15% of misses). (7) NAME RECOGNITION (upstream, Bruce-Young): recovers coverage 188->211 gold-typed but the floor lift is +0.0028 NOT-sep -> the upstream span-noise fix is bounded (most misses are not recognition artifacts)."
files_changed: "experiments/exp_namebridge_axis_decomp_v1.py (the axis x residual-reason decomposition of the misses -- the located-negative deliverable), experiments/exp_namebridge_worldknowledge_v1.py (Bruce-Young name recognition + broader-KB + phi gate-then-compete arms + oracle-adjacent coverage), experiments/exp_namebridge_discourse_type_v1.py (the online episodic discourse-locative/agency coarse-type route -- located negative), verification/test_namebridge_worldknowledge.py (9/9 witnesses), data/exp_namebridge_{axis_decomp,worldknowledge,discourse_type}_v1/metrics_full.json, notes/problems/world_knowledge_common_noun_to_name_bridge_the_81_percent_residual/SOLVED.md. NO hdlab/ written (Q111 -- proposed diff below). Reuses exp_namebridge_coref_kb_v1 (the two-route CLS instrument + item machinery), experiments/_entity_type_spoke.py (the C8 DBpedia read API), hdlab.typed_spokes (C5 is-a closure), data/corpora/gum (pinned V12.1.0), data/corpora/dbpedia_instance_types (pinned 2022.12.01) + the on-disk Wikidata P31/P106 probe cache."
reverify: ".venv/Scripts/python.exe verification/test_namebridge_worldknowledge.py    # 9/9 (W1 floor, W2 axis refutation, W3 oracle SELECT-ok, W4 coverage 0.697/30%-doc-local, W5 recognition not-sep, W6 static-KB ceiling +0.0084 not-sep, W7 phi twin-clean not-sep-floor, W8 discourse coarse-type located negative, W9 abstention-safe)"
---

# LOCATED NEGATIVE (the bar's full pass) -- the name-bridge residual is COVERAGE of DOCUMENT-LOCAL entities, not the brief's relational/kinship axis, and no static KB can close it; the frontier is the generative situation-model

**STATUS: PARTIAL** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- measured in `experiments/` + `verification/`; strategy lands any Q111 wire.

This is the rigorous located negative the bar blesses as a FULL PASS: it names the exact world-knowledge axis the
residual needs, with counts, and proves why the available brain-foundational sources do/don't cover it. It ALSO
carries a small, twin-clean, brain-foundational fidelity improvement (name recognition + broader KB + phi
gate-then-compete) that is NOT CI-separated -- worth landing as fidelity, not claimed as a capability win.

## THE DISK OUTRANKS THE BRIEF -- the brief's hypothesized axis is REFUTED
The brief says people are re-mentioned by "relation / role-in-situation / kinship / age-gender, NOT catalogued
occupation," and asks for a route on THAT axis. **On the actual GUM name-bridge slice (n=356) that axis is a
MINORITY.** Decomposing the 154 two-route-floor misses by the anaphor head's semantic class (glass-box, via the
landed C5 is-a closure):

| axis of the MISS | count | share | what it is |
|---|---|---|---|
| OTHER | 56 | 36% | non-person/place/org heads (language/book/work/field/time/case...) + noisy spans |
| GEO | 38 | 25% | country/city/nation/island/region/town -- **the single biggest clean axis** |
| OCCUPATION | 17 | 11% | professor/president/director/steward... (person-role) |
| ORG | 16 | 10% | show/publisher/community/organization/church |
| AGE_GENDER | 10 | 6% | man/woman/guy/kid/gentleman |
| RELATIONAL | 8 | 5% | colleague/leader/friend/student/successor |
| KINSHIP | 5 | 3% | mother/wife/grandmother/child |
| GENERIC | 4 | 3% | one/case/group |

**The brief's axis (relational + kinship + age_gender) = 23/154 = 15%.** The DOMINANT residual is encyclopedic
ENTITY-TYPE -- GEO + ORG + OTHER = 110/154 = 71% (place/organization/thing), plus OCCUPATION 17. The name-bridge
slice on GUM is dominated by PLACES and ORGANIZATIONS ("the country" <- Argentina, "the show" <- Game of Thrones),
which the encyclopedic type KB is exactly RIGHT for -- so the axis is not the problem. **The problem is COVERAGE.**

## WHY IT MISSES: coverage of DOCUMENT-LOCAL entities, proved three ways
Residual REASON on the 154 misses: `not_in_kb` 101 (66%), `typed_not_licensing` 39 (25%), `licensed`-but-misranked
14 (9%). Three controls localize the wall precisely:

1. **The SELECT is near-perfect -- it is NOT the bottleneck (oracle).** Grant gold its true type-license and run the
   SAME graded constraint-integration competition: with distractors untyped -> **1.000**; with distractors keeping
   their REAL types -> **0.924** (the 0.076 loss is genuine same-type ambiguity -- a distractor really shares the
   type and is more recent, which a competent reader also misses). So the retrieval mechanism the two prior SOLVEDs
   built is sound; the entire gap to 0.924 is **knowledge about the gold entity**.
2. **The coverage ceiling of ALL static knowledge is 0.697.** Union of DBpedia InstanceOf + the Wikidata P31/P106
   probe + Bruce-Young name recognition + episodic in-text is-a types only 248/356 gold entities. **108/356 = 30%
   are DOCUMENT-LOCAL** -- Betty, Gram, Koinonia, Chao, Apa Horsiesios, Mike Eizenga, obscure towns (Tyom, Pag,
   Nacogdoches) -- present in NO encyclopedic KB, because they exist only in this discourse.
3. **The static-KB ceiling is empirically capped BELOW CI-separation.** The Wikidata probe was fetched FOR THESE
   EXACT gold surfaces (so it is an *upper bound* on any static KB, not a fair asset), and it lifts the strongest
   prior arm 0.5843 -> 0.5926 = **+0.0084 CI[-0.0112,+0.0281], NOT CI-sep.** A bigger static KB cannot win here;
   its own best-case is already measured and it does not separate. (This reproduces + sharpens the acquire_wikidata
   SOLVED's "+0.0084" and its "coverage residual is genuinely document-local" note.)

## THE AXIS THE RESIDUAL ACTUALLY NEEDS (the answer to the brief's question)
Not relational/kinship (15%). Not a bigger static KB (capped at +0.0084). The residual needs **fine-grained
entity-type knowledge for entities that appear ONLY in the current discourse** -- which the brain supplies from the
**online situation model / episodic (hippocampal-CLS) route**, NOT from consolidated encyclopedic memory. Two
sub-findings pin this:

- **Coarse discourse typing OVER-LICENSES (located negative).** I built the online episodic route the CLS theory
  demands -- infer a document-local entity's COARSE type from the discourse predicates it participates in
  (locative "in/at/to X" -> PLACE; communication agency / title / gender -> PERSON; Resnik selectional preference).
  It **HURTS**: `disc_place` 0.556 vs floor 0.584 (-0.0253 CI-sep worse) and does not beat its own shuffled twin
  (-0.0056, not-sep). Reason: many distractor names are ALSO loc-mentioned/agentive, so a coarse PLACE/PERSON flag
  licenses the wrong candidate. This reproduces the P31 SOLVED's "continuous/coarse type-similarity fails; discrete
  FINE types are the brain-foundational choice" -- now at the discourse level. So the residual needs *fine* type,
  and for a document-local entity fine type is not stateable by a coarse predicate -- it requires the full
  generative situation-model (who-is-who inference), the filed frontier.
- **The person axes are themselves document-local.** The 23 relational/kinship/age_gender misses are Betty, Gram,
  Chao, Coulthard, Mike Eizenga -- their kinship/role IS established in the discourse, not in a relational KB. So
  even the brief's axis reduces to the same lever: online discourse-derived identity, not a static relational KB.

## THE SMALL BRAIN-FOUNDATIONAL IMPROVEMENT (twin-clean, not CI-sep -- landable as fidelity)
Completing the chain with every component the brain's mechanism:
| arm | acc | vs kb_thematic (0.5843) | vs shuffled-KB twin |
|---|---|---|---|
| recency (floor) | 0.4719 | -- | -- |
| kb_intext (two-route CLS) | 0.5674 | -0.017 | -- |
| **kb_thematic (STRONGEST PRIOR)** | **0.5843** | -- | -- |
| wk_reco (+ Bruce-Young name recognition) | 0.5871 | +0.0028 CI[-0.011,+0.017] not-sep | -- |
| wk_reco_wd (+ Wikidata probe = static-KB ceiling) | 0.5926 | +0.0084 CI[-0.011,+0.028] not-sep | -- |
| **wk_phi (+ phi gate-then-compete)** | **0.5926** | +0.0084 not-sep | **+0.1152 CI-sep (twin LOSES)** |
Name recognition recovers 188->211 gold-typed (drops IPA/respelling junk, surname/clean backoff); the broader KB
211->231; the phi gate is Lappin-Leass (hard gender-agreement FILTER, THEN graded compete -- unlike the prior
`kb_full` which used gender as an OR-license and HURT). The twin losing by +0.1152 says the signal is real; the
+0.0084 whole-slice not-sep says it is coverage-bounded. **Abstention-safe (no-regress): on no-signal items the arm
== recency exactly.** Each component is more brain-foundational than what it replaces; land it as fidelity, not a win.

## FULL-STACK-UPSTREAM (owner directive: prototype this component + its upstream, confirm no downstream regress)
- **UPSTREAM #1 -- NAME RECOGNITION (Bruce-Young), the non-brain-foundational component the principle predicted.**
  The GUM name spans feeding the KB are noisy: IPA/pronunciation respellings tagged PROPN ("Antonin Leopold Dvorak
  d(...)dvorak"), coordinated multi-entity spans glued into one ("Mario J. Lucero Isabel Ruiz Heaven Gaming"),
  truncations ("States" <- United States). The brain recognizes the canonical familiar name (Bruce-Young). I
  prototyped it (drop non-latin junk, Titlecase-bounded run, surname/first+last backoff): it recovers real coverage
  (188->211 gold-typed) but the floor lift is +0.0028 not-sep -- **the upstream fix is real but bounded; most misses
  are not recognition artifacts, they are genuine absence.** No downstream regress (recognition only ADDS lookup
  keys; abstention-safe).
- **UPSTREAM #2 -- the KNOWLEDGE SOURCE itself is the deepest non-brain-foundational component.** The two-route
  mechanism uses a CONSOLIDATED static KB where, for document-local entities (30% of gold), the brain uses the
  ONLINE episodic/hippocampal route + generative inference. Using a static KB for document-local entities is the
  fidelity gap. The brain-foundational fix is the generative situation-model (filed) -- coarse discourse typing
  (my `disc_*` route) is the tractable stand-in and it over-licenses, so the full generative model is required.
- **DOWNSTREAM no-regress:** the arms are additive licenses that fall back to recency when they have no signal
  (control 5), so a live wire cannot regress the named/pronoun/same-head consumers. This is the standalone
  name-bridge instrument (a different population from the live experiencer/pronoun consumers), consistent with the
  two prior SOLVEDs; the Q111 wire + full `reader.read()` re-measure is strategy's at land.

## PERFORMANCE vs THE BRAIN + where signal is lost (the mechanism-diff)
We are at 0.593 vs the brain's ~0.89 competent-reader estimate (the acquire_wikidata waterfall) -- and every stage's
OPERATION matches the brain (recognize name -> type -> license -> salience-select). The loss is entirely KNOWLEDGE
BREADTH: 30% of gold entities are document-local (the brain knows them from the discourse via the situation model;
our static KB does not) + genuine same-type ambiguity (0.076, the brain's own limit). No wrong mechanism; the chain
loses signal ONLY where its knowledge is a static consolidated KB and the brain's is an online situation model.

## PROPOSED hdlab DIFF (Q111 -- strategy lands; solver does not write hdlab)
1. **LAND the fidelity improvements into the C8 name-bridge path** (if/when C8 lands per the acquire_wikidata
   SOLVED's proposed diff): (a) Bruce-Young NAME RECOGNITION on the lookup key (drop non-latin/respelling tokens,
   surname/first+last backoff) before `entity_type_lemmas`; (b) the phi gate-then-compete (hard gender-agreement
   FILTER then graded competition) REPLACING the `kb_full` gender OR-license. Both twin-clean, abstention-safe, more
   brain-foundational; neither is CI-sep alone, so gate them behind the C8 wire's own flip decision.
2. **Do NOT acquire a bigger static entity KB for THIS slice** -- empirically capped at +0.0084 (the fitted-probe
   upper bound). The knowledge-foundation program's static-KB scaling is bounded here; redirect it to the generative
   route.
3. **Do NOT wire the coarse discourse-type route** (locative->PLACE / agency->PERSON): located negative, over-licenses
   (-0.0253 CI-sep worse, not better than shuffled). Fine type only.

## KEY REALIZATIONS (the enabling moves)
- **Decompose the residual by AXIS before believing the brief's axis.** The top anaphor heads are country/city/
  nation/state/town/island -- the slice is place/org-dominated, so the brief's person-relational axis (guessed from
  the crosstype EXPERIENCER population) is 15% here. Enumerating the misses, not recalling the brief, refuted it.
- **The oracle is what separates 'no mechanism' from 'no knowledge'.** Granting gold its type and re-running the
  SAME select -> 1.000 / 0.924. That single measurement proves the retrieval is near-perfect and the wall is
  coverage -- so no amount of SELECT/mechanism work can win, only knowledge, and static knowledge is capped.
- **A probe FITTED to the eval surfaces is a free upper bound.** The Wikidata probe was fetched for these exact
  golds; its +0.0084 not-sep is the CEILING of any static KB on this slice -- proving a bigger KB cannot win
  WITHOUT the fetch. Do the right thing (prove the point) not the easy thing, and here proving it needed no acquisition.
- **Coarse discourse typing over-licenses -- fine type is load-bearing.** The online episodic route the CLS theory
  demands only helps if the type is FINE; a coarse PLACE/PERSON flag fires on distractors too. This is why the
  residual needs the generative world-model, not a coarse predicate heuristic.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, E3 coreference / ATL hub-and-spoke)
- NAME-BRIDGE coref residual, quantified: the two-route CLS + thematic + graded competition is at its knee (0.5843);
  the SELECT is near-perfect (oracle 0.924); the wall is COVERAGE of DOCUMENT-LOCAL entities (30% of gold, in no
  static KB) + genuine same-type ambiguity (0.076). A static KB is empirically capped at +0.0084 (fitted-probe
  upper bound). The residual's brain-foundational source is the ONLINE situation model / generative inference, not
  consolidated semantic memory -- mark the name-bridge world-knowledge lever as GENERATIVE (situation-model), not KB.
- NEW load-bearing note: coarse discourse-derived typing (locative->PLACE, agency->PERSON) OVER-LICENSES on the
  name-bridge select (-0.0253 CI-sep worse, not better than shuffled) -- fine discrete type is the brain-foundational
  choice at the discourse level too (extends the P31 "continuous type-similarity fails" finding).
- UPSTREAM: GUM name spans carry IPA/respelling junk + coordinated multi-entity glue that starve the KB (false
  not_in_kb); Bruce-Young NAME RECOGNITION recovers some (188->211 typed) but bounded (+0.0028 not-sep).

## Adjacent components (seeds for the next problems -- brain-fidelity + optimization)
- **The generative situation-model (the MAIN lever, filed as Wall-2 / the generative-world-model program).** The
  30% document-local residual is only reachable by online who-is-who inference. This problem's oracle (0.924 with
  perfect knowledge) sizes the prize; the coarse-typing negative shows a heuristic will not do it.
- **Name individuation / mention-span cleanup (upstream).** The token-overlap name clustering merges distinct
  entities (coordinated spans) and the parser tags IPA as PROPN -- a reader-wide precision lever; bounded for this
  task (+0.0028) but a clean fidelity fix.
- **The two-route CLS + C8 entity-type spoke** (acquire_wikidata SOLVED, proposed-to-land): confirmed at its knee on
  this slice; the fidelity add-ons here (recognition, phi-gate) attach to it.

---

**TLDR (plain English).** A reader links "the country" back to a named place, or "the mother" back to a named
person, using knowledge about that place or person. Our reader does this well when the place/person is FAMOUS
enough to be in an offline fact-list (about 4 in 10 of the hard cases). The brief guessed the missing cases need a
different KIND of fact (family ties, social roles) rather than jobs -- but on the real modern text those cases are
only about 1 in 7. The real reason we miss is simpler and deeper: about **3 in 10 of the target people/places exist
ONLY in this one document** (a "Gram", a "Betty", a tiny town) -- no fact-list on Earth has them, because a human
only knows who they are from reading the document itself. I proved the picking machinery is essentially perfect (if
you hand it the right fact, it scores ~92-100 in 100), so the gap is purely missing knowledge; I proved a bigger
fact-list cannot fix it (I gave it the best possible list, fitted to the exact answers, and it barely moved); and I
proved that guessing the type from surrounding words ("was in X" -> X is a place) backfires because it fires on the
wrong names too. So the honest answer to "what knowledge does the gap need?" is: **the reader has to BUILD who each
character/place is as it reads (a running model of the story), not look them up** -- which is the big generative
world-model already on the roadmap. I also built a small, honest upgrade (recognize messy names, use gender as a
filter) that helps a little and can't be faked by a scrambled control, worth keeping though it doesn't move the
headline.

**QUESTIONS.** One judgement call for the owner (I recommend, do not decide): **status PARTIAL vs SOLVED.** The bar
states a rigorous located negative naming the axis with counts IS a full pass; I have that (axis refuted with
counts + the coverage wall proved three ways). I marked PARTIAL to deflate, because there is no CI-separated
capability gain -- only a twin-clean, not-sep fidelity improvement. If you read the located-negative provision
strictly, SOLVED is defensible; the numbers are on the table either way.

**NEXT STEPS (priority-ordered).**
1. **[filed program -- the MAIN EVENT] the generative situation-model / world-model.** This problem proves it is the
   ONLY route to the 30% document-local residual (static KB capped at +0.0084; oracle prize 0.924). Concrete: score
   the generative discourse-model's who-is-who prediction on THIS name-bridge slice (reuse `exp_wall2_generative_
   inference_v1` from the de-leak SOLVED) as the successor instrument.
2. **[strategy, at owner DONE] Fold the fidelity add-ons into the C8 wire** (name recognition + phi gate-then-compete),
   twin-clean + abstention-safe, gated behind C8's flip -- not a standalone win.
3. **[do NOT do] Acquire a bigger static entity KB for this slice** (empirically capped) or wire coarse discourse
   typing (located negative). Redirect knowledge-foundation effort to the generative route.
