---
problem: the_reader_has_no_copular_is_a_binding_schema
status: SOLVED
bar: "PASS = an is-a/attribute binding readout (glass-box, NO LLM) that, on a clean predicate-complement gold (nominal + adjectival + identity copular clauses), answers \"what/who is X\" and \"what property does X have\" CI-separated over the strongest simple floor (e.g. most-recent-noun, string-overlap) with an info-free binding-SHUFFLE twin LOSING CI-separated, AND does not regress the existing entity/state registers (an explicit no-regression check). Report CI half-width + null p95; recompute the floor on the same population. A rigorous located NEGATIVE -- predication cannot be bound above the floor by a faithful role-filler schema, with the reason -- is a FULL PASS."
result: "The is-a/attribute binding READ-BACK answers 'what/who is X' at recall 0.6718 / precision 0.7690 on 451 gold copular predications (UD-EWT test; nominal is-a + adjectival + identity), CI-separated +0.1685 [+0.1136,+0.2172] hw=0.0518 nullp95=0.0518 over the most-recent-noun floor (0.5033), with the info-free binding-SHUFFLE twin LOSING +0.2195 [+0.1767,+0.2625] recall / +0.2322 precision CI-sep. THE FIX (label-robust copula-anchored detection, prototyped) raises it to recall 0.8182 (+0.1463 [+0.1114,+0.1833] CI-sep over base; twin still loses +0.2949 recall CI-sep), the gain CONCENTRATED on the identity weak point (adj +0.102, is-a +0.194, identity +0.247). Glass-box Higgins TYPE classifier 0.9690 coarse. Register-independent (modern 0.900->1.000, archaic 0.450->0.700 with the fix). No-regression: state_register self-test 11/11 + the typed binding feeds it and round-trips ('what is Ahab?'->captain, 'what is the room?'->cold)."
floor: "Strongest simple floor ACTUALLY RUN, recomputed on the same 451-clause population = most-recent-noun / parse-free positional holder (extract_entity_states_positional): read-back recall 0.5033, precision 0.3969. Info-free SHUFFLE twin (keep the detected property, bind a RANDOM preceding nominal as holder): recall 0.4523. The binding beats BOTH CI-separated; the fix beats both by more."
controls: "(1) most-recent-noun POSITIONAL floor recomputed on the same population -> excludes 'any copula-anchored heuristic wins' (binding beats it +0.1685 CI-sep). (2) info-free binding-SHUFFLE twin (random holder, matched property/count) -> excludes 'the holder binding is noise' (twin loses +0.2195 recall / +0.2322 precision CI-sep for base; +0.2949 / +0.2017 for the fix). (3) PROCESS MAP stage decomposition (451 gold -> 319 detected -> 303 bound -> 297 typed) -> LOCATES the residual loss at DETECTION (the arc labeler's `cop` recall), not binding (95% lossless given detection) -> excludes 'binding is the bottleneck'. (4) per-Higgins-type gradient (adj 0.746 > is-a 0.621 > identity 0.466) + gold-detection ceiling (0.807) -> excludes 'the loss is uniform'; it is concentrated in identity/equative. (5) NO-REGRESSION: landed state_register self-test 11/11 unchanged + typed binding composes -> excludes 'the readout breaks the existing registers'. (6) register-independence on a controlled modern<->archaic matched set -> excludes 'this is a modern-text artifact'. Each control excludes a specific alternative."
files_changed: "experiments/exp_copular_is_a_binding_readout_v1.py (process map + typed is-a/attribute read-back + floor + shuffle twin + THE FIX + symmetric-identity arm + glass-box Higgins classifier), experiments/exp_copular_is_a_binding_register_and_noregress_v1.py (register-independence controlled set + no-regression), verification/test_copular_is_a_binding_organ.py (scaffold-free witness, 10/10), notes/problems/the_reader_has_no_copular_is_a_binding_schema/research_copular_is_a_binding_2026-09-02.md (4-lane full-text brain drill), notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_identity_gain_ci.py (persisted: identity-only gain CI + specificational typing), notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_precision_and_identity_residual.py (persisted: fix precision-cost deflation + identity residual decomposition), notes/problems/the_reader_has_no_copular_is_a_binding_schema/IDEAL_copular_is_a_architecture_2026-09-02.md (the ideal 6-stage brain-faithful system + research gaps), notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_isa_inheritance_feature_overlap.py (persisted: is-a inheritance via feature-overlap -- located gap), notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_signal_loss_waterfall.py (persisted: exact per-stage brain-vs-us signal-loss waterfall), notes/problems/the_reader_has_no_copular_is_a_binding_schema/SOLVED.md. REUSES (unmodified): experiments/_copular_nominal_events.extract_entity_states (the sibling's binding primitive), hdlab.state_register (landed, the read-back store), the in-substrate pos_tagger/arc_parser/arc_labeler. NO hdlab/ file changed -- proposed diff below (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_copular_is_a_binding_organ.py"
---

# SOLVED -- the is-a/attribute binding readout answers "what/who is X" CI-separated over the floor, twin loses; and the process map + prototyped fix locate and close the residual (detection, worst on identity)

**Status: SOLVED (WIP until `owner_verdict: DONE`).** The bar is met on a clean 451-clause copular gold covering
all three sub-types (nominal is-a + adjectival + identity). No `hdlab/` file changed; the exact wire is proposed
below for strategy to land (Q111). Glass-box, NO external LLM at inference (the invariant).

## Honest framing first: what was already built vs what this adds
The CORE binding primitive -- `extract_entity_states` (for each `cop` arc, PROPERTY = the predicate head, HOLDER
= its nsubj) -- was ALREADY built and validated by the sibling problem `the_event_detector_misses_copular_and_
nominal_predication_events` (0.677R/0.872P pair recovery on UD-EWT), and `hdlab.state_register` (landed, not
wired) already holds ADJECTIVAL/NOMINAL state values with read-back queries. I **reuse both** (per the reuse
discipline; I did not reinvent the binding). What this submission genuinely ADDS, and why it is not a re-derivation:
1. **Proves the binding clears THIS bar** -- the "what/who is X" read-back on a TYPED clean gold covering identity,
   CI-separated over the most-recent-noun floor with the shuffle twin losing, with CIs + null p95 (the sibling
   measured pair-recovery, never the floor-separated read-back the bar demands, and never the identity split).
2. **The PROCESS MAP** that locates the residual capability loss precisely (owner asked: "map the entire process
   to see where we lose capability, chase up and down the substrate").
3. **The prototyped FIX** to that weak point (owner asked: "prototype a fix to that") -- +0.146 recall CI-sep.
4. **The Higgins predicational/identificational TYPING** (absent everywhere) + the brain-pinned **symmetric
   identity** representation.
5. **Register-independence** (the sibling only hand-adjudicated 22 OOD fires) + an explicit **no-regression** check.

## The opening move -- how the BRAIN does this (drill: `research_copular_is_a_binding_2026-09-02.md`, 4 full-text lanes)
The copula BE is a near-empty functional carrier; the meaning is the PREDICATION RELATION binding the complement
to the subject ENTITY node (Higgins 1979; Mikkelsen 2011). The drill PINNED the cues and the two distinct binding
types, and -- importantly -- told me where NOT to overclaim:
- **PINNED cue inventory** (Van Praet & Davidse 2015 corpus N=2926; Mikkelsen 2011): an ADJECTIVE complement can
  ONLY be predicational (CUE 12, the cheapest hard gate); proper-name/definite complement -> identity; indefinite
  -> strong predicational prior; possessive "his wife" = a GENUINE AMBIGUITY zone; base rate ~74% predicational.
  My glass-box classifier implements these and scores 0.969 coarse.
- **PINNED: equative identity is SYMMETRIC and hippocampal** (CA3 recurrent auto-association; Rizzuto & Kahana
  2001; causal: Bunsey & Eichenbaum 1996 -- hippocampal lesion abolishes BACKWARD associative access). So identity
  is a symmetric relational link, distinct from property attribution; I implement + measure that.
- **PINNED: category is-a is EMERGENT feature-overlap, NOT an explicit hypernym hierarchy** (ATL hub-and-spoke;
  Rogers 2004; Patterson 2007). => a distributional/grounded is-a is more brain-faithful than a WordNet graph.
- **OPEN/THIN (I do NOT claim these):** the predicational-vs-identity NEURAL dissociation is untested -- the
  ATL-property vs hippocampal-identity split is a well-motivated EXTRAPOLATION, not a direct result; my typing
  claim rests on the SURFACE cues (PINNED), not a neural dissociation. Equative subject/predicate assignment is a
  genuinely contested syntax problem with NO online-processing literature -- so the parser's equative wall is an
  expected gap, not a bug.

## What I measured (the bar, met with power) -- `exp_copular_is_a_binding_readout_v1.py`, UD-EWT test, n=451 gold
| arm | read-back recall | precision | vs floor / vs twin |
|---|---|---|---|
| most-recent-noun FLOOR | 0.5033 | 0.3969 | -- |
| info-free SHUFFLE twin | 0.4523 | 0.5368 | -- |
| **base binding read-back** | **0.6718** | 0.7690 | **+0.1685 [.114,.217] CI-sep over floor; +0.2195 over twin CI-sep** |
| **+ THE FIX (label-robust)** | **0.8182** | 0.6150 | **+0.1463 [.111,.183] CI-sep over base; +0.2949 over its twin CI-sep** |

- **The bar is met by the base read-back alone:** CI-separated over the strongest simple floor, twin losing,
  CIs + null p95 reported, floor recomputed on the same population, no-regression demonstrated.
- **Register-independent** (`exp_..._register_and_noregress_v1.py`, controlled matched set): modern 0.900->1.000,
  archaic 0.450->0.700 with the fix; classifier 1.000 modern / 0.750 archaic. The MECHANISM works on both; the
  archaic residual is the modern-trained parser/tagger degrading on inversions ("Cold was the chamber") and
  archaic copulas ("was become") -- a nameable parser-OOD gap, consistent with the sibling's 0.64-0.73 OOD.

## Do we understand exactly where we lose capability? YES -- the PROCESS MAP (owner: chase up and down the substrate)
Driving the honest end-to-end pipeline (substrate tagger -> parser -> labeler -> binding -> typing) on the 451
gold clauses, capability retained per stage:

| stage | retained | lost here | what it is |
|---|---|---|---|
| 0 gold copular clause | 451 | -- | the population |
| 1 predicate DETECTED | 319 | **132 (29%)** | **the arc labeler's `cop` recall -- THE dominant loss** |
| 2 holder BOUND | 303 | 16 (5%) | near-lossless once detected |
| 3 TYPED correctly | 297 | 6 (2%) | the glass-box classifier is near-free |

And the loss is **concentrated by Higgins type** -- the capability-loss gradient:

| type | n | base bind recall | WHY it's lost |
|---|---|---|---|
| predicational adjectival | 275 | 0.7455 | (state_register's clean territory) |
| predicational nominal (is-a) | 103 | 0.6214 | labeler misses `cop` on the copula token even when the tree is right |
| **identificational (identity)** | **73** | **0.4658** | **DOUBLE wall: labeler mislabels the predicate `nsubj`/`root` (equative reversal) AND, even given the gold predicate, the parser tree finds the holder only 56%** |

**Root cause, pinned:** the loss is DETECTION, specifically the arc labeler's low `cop` recall (given gold
detection + a tree-position holder, read-back rises 0.672 -> 0.807 -- a METHOD-SPECIFIC probe, not a hard ceiling:
the fix's label+tree+positional UNION actually reaches 0.818, so holder recovery has more headroom than the
single-method probe showed). It is worst on the identity type because equatives ("NP is NP", both referring)
reverse subject/predicate -- a genuinely hard, contested syntactic problem the modern-trained parser mishandles.

## Prototyping the FIX to that component (owner: "can you prototype a fix to that?")
**Brain-faithful principle:** the copula is a transparent CLOSED-CLASS carrier -- predication detection must NOT
be gated on a fragile dependency label (the brain does not miss "Ahab is a captain"). `robust_cop` fires on each
copula/linking TOKEN and recovers the predicate from the parse TREE (head of the copula, else next content head)
and the holder from the tree (nominal child preceding the copula, else nearest preceding nominal) -- bypassing the
`cop` label -- gated to skip existential expletives and aux-of-a-main-verb. Unioned with the label path:
- **recall 0.672 -> 0.818 (+0.1463 CI-sep), the info-free twin still loses +0.2949 CI-sep**; precision 0.769 ->
  0.615 (a real recall/precision trade; part is genuine over-fire, part is gold-narrowness -- the fix fires on
  copular clauses outside my narrow typed gold).
- The gain is **exactly where capability was lost:** identity +0.247 (0.466->0.712), is-a +0.194, adjectival
  +0.102 -- it closes the identity weak point most. **The identity-type gain is itself CI-separated:** +0.2466
  [+0.153,+0.347] on the n=73 identity subset (doc-bootstrap) -- not a whole-set artifact.
- **The precision cost is REAL, now quantified (not hand-waved):** of the 231 fix fires outside the narrow typed
  gold, **53.7% are genuinely spurious over-fire** (not a gold cop predicate), ~46% are real copular clauses the
  NARROW gold excluded (PP/clausal/expletive subjects, or a real predicate with a different holder). So the
  precision drop is about half genuine over-fire, half gold-narrowness -- which is why the LANDED default is the
  high-precision label path and the fix is the recall-max option.
- **The identity residual is now fully decomposed:** the fix still misses 21/73 identity clauses -- **13 (detection:
  the hardest equatives/clefts/specificational-inversions the copula-anchored path still can't find) + 8 (holder:
  the equative subject/predicate reversal the positional heuristic still mis-orders).** Still detection-dominated;
  the holder 8 need discourse topicality (a document-level cue -- UD-EWT is sentence-level, so a follow-on).
- **Brain-pinned symmetric identity** (CA3 auto-association): scoring identity as an unordered/symmetric link
  recovers the equative-reversal cases the parser mis-orders (identity 0.712 -> 0.726). Small here (UD-EWT
  equatives are mostly canonical order) but the faithful representation, and it grows with reversal-heavy prose.

## Does distinguishing predicational from identificational matter? (the bar's INFERRED question)
Yes, two ways. (1) The **capability loss is type-specific** -- identity is the weak point (0.466), so TYPING is
what lets the fix route it (the symmetric identity treatment). (2) The types have **different correct read-backs**:
predicational -> a PROPERTY/is-a value routed to state_register ("what is Ahab? -> captain"; "what is the room? ->
cold", both verified); identificational -> a SYMMETRIC IDENTITY link that belongs with coreference (Dijksterhuis
2024). A type-BLIND store conflates "his wife" (identity) with "a captain" (category) -- storing an identity as a
category is the mis-route the brain avoids. The glass-box classifier does the split at 0.969 (surface cues; the
neural dissociation itself is OPEN, so I claim only the cue-based typing).

## What I did NOT establish / what I would withdraw first
- **The COPULAR result is IN-DOMAIN for the UD-trained parser** (UD-EWT is the only `cop`-annotated treebank on
  disk). Register-independence is shown on a CONTROLLED authored matched set + the sibling's 19c hand-adjudication,
  NOT on a large 19c gold `cop` treebank (none exists). **Withdraw first:** the archaic absolute numbers (n=20,
  authored) -- they show the mechanism is register-independent and the fix helps, but the archaic 0.700 is a small
  controlled estimate, not a powered 19c measurement.
- **The is-a CATEGORY link / inheritance ("X is a doctor" -> "X is a person") is NOT built here.** It is a real,
  brain-pinned follow-on (feature-overlap, not a WordNet hierarchy -- Rogers/Patterson), routed below.
- **The precision cost of the fix (0.769->0.615) is real.** The high-precision operating point is the label-based
  base (0.769); the high-recall point is the fix. I report both, like the sibling's confident-vs-recall-max split.
- **The neural predicational/identity dissociation is an extrapolation** (drill: OPEN). I claim only surface-cue
  typing + the symmetric-identity representation (CA3-pinned).
- **Measured at the glass-box `extract_entity_states`/parser level, NOT end-to-end through the live
  `SituationReader.read()`** (which consumes conll files), and the read-back is WITHIN-CLAUSE (holder = the nsubj
  token), NOT a canonical-entity query resolved across a discourse via coref. The full "what is X for a canonical
  entity across the passage" composition (binding + coref) is a plumbing wire, not yet measured end-to-end. This
  matches the sibling's methodology (its entity-state dimension was also measured at `extract_entity_states`).
- **The fix's genuine over-fire (53.7% of non-gold fires) is not yet gated down.** A tighter existential/cleft/
  aux-chain gate could raise the recall-max precision; I did not chase it because the high-precision label path is
  the landed default (the operating-point split already handles the precision concern).

## FURTHER PUSHES (owner-directed deepening: "any more we can push here?" + adjacent-component fidelity)
**(A) The identity-weak-point recovery is CI-separated on its own subset** (not a whole-set artifact): base
0.466 -> fix 0.712 on the n=73 identity clauses, +0.2466 [+0.153,+0.347] doc-bootstrap. So the fix demonstrably
closes the exact place capability was lost. **The typing handles the reversible specificational family** (the
PINNED CUE 1): "The winner is John" / "The captain is Ahab" / "The best option is the hotel" all type as identity
via the definiteness/proper-name cue -- the specificational=identity-family clauses my definiteness rule was
built to catch.

**(B) is-a INHERITANCE is the deepest remaining brain-foundational lever -- I PROTOTYPED the ideal mechanism and
LOCATED the gap** (`prototype_isa_inheritance_feature_overlap.py`; the full ideal is `IDEAL_copular_is_a_
architecture_2026-09-02.md`). The drill PINNED that category assignment AUTO-ACTIVATES a property online (Duffy &
Keir 2004) and that the ATL represents is-a as EMERGENT FEATURE-OVERLAP, NOT a symbolic hypernym graph (Rogers
2004; Patterson 2007). I built a glass-box PPMI-SVD feature-overlap space from raw reading (no LLM; 1.2M-3.9M
tokens) and tested is-a recovery against WordNet hypernym gold, on the FREQUENCY-MATCHED 2AFC (chance 0.5 --
superordinates are frequent, so a raw 2AFC is confounded and inflates every method to 0.67-0.78; the matched test
is the honest one). n=12855 pairs:
- **Pure feature-overlap (symmetric cosine) carries only a WEAK is-a signal: 0.666 +/-0.008** -- barely above
  chance, and on ranking it barely surfaces the superordinate (top-10 ~0.10). CONFIRMS the drill's prediction:
  distributional overlap is mostly RELATEDNESS (doctor~nurse~hospital), not is-a DIRECTIONALITY.
- **The proper DIRECTIONAL feature-inclusion measure (WeedsPrec) is the best: 0.685 +/-0.008, CI-separated ABOVE
  symmetric cosine** (the brain-faithful lever -- a superordinate's contexts INCLUDE its hyponym's; distributional-
  inclusion hypothesis, Geffet & Dagan 2005; Weeds & Weir; Santus). But the gain is MODEST (+0.019). Entropy-based
  generality gating (0.665) WASHES OUT once frequency is controlled -- it was riding the confound (an honest
  correction: on the confounded 2AFC + top-10 ranking it looked like the winner; it is not).
**Honest status:** is-a inheritance is only WEAKLY supported by glass-box feature-overlap even with the right
directional measure (best 0.685). The brain-faithful DIRECTION (feature inclusion) is confirmed as the lever but
is insufficient alone -- a bounded FOLLOW-ON (routed below) that likely needs a hybrid with the grounded semantic
graph (WordNet is-a as a static foundation asset -- admissible, not an LLM). The ideal MECHANISM is now specified
and the gap is LOCATED precisely (directionality is the lever; a distributional space alone under-delivers).

**(C) The identity->coreference route is the other high-fidelity opportunity.** The drill PINNED that coreference
reactivates hippocampal concept cells (Dijksterhuis 2024) and equative identity is symmetric/hippocampal (CA3).
Our identity typing is done (0.969) but the identity link is not yet MERGED into the coref system -- so "she is
his wife" types correctly but does not yet make she==his-wife co-refer. That merge is the faithful home for the
identity type (a symmetric relational bind), routed below.

## HOW WE COMPARE TO THE BRAIN, AND WHERE WE LOSE SIGNAL -- the exact waterfall (owner-directed)
`prototype_signal_loss_waterfall.py`. The brain comprehends clear copular predication at ~CEILING (a fluent
reader essentially never fails "what was Ahab?" for a clear clause), PLUS it inherits (doctor->person) and resolves
the holder to a canonical cross-sentence entity for free. Our best system (the fix) vs that reference:

| stage | our retention (of 451 gold) | signal lost here | EXACT divergence from the brain |
|---|---|---|---|
| gold clause (brain ~1.00) | 451 (1.000) | -- | -- |
| **1 DETECTION** | 390 (0.865) | **-0.135 (61 clauses)** | brain detects predication HOLISTICALLY + INCREMENTALLY from the closed-class copula, no full parse; we use a BATCH parser (UAS 0.79) whose tree is wrong on the hardest equatives/clefts/specificational-inversions (13 of the 61 are identity) |
| **2 HOLDER binding (= fix 0.818)** | 369 (0.818) | **-0.047 (21 clauses)** | brain resolves equative subject/predicate by INFORMATION STRUCTURE (topicality/givenness -- the discourse-old NP is subject); we use SYNTACTIC POSITION, which mis-orders equative reversals (8 of the 21 holder errors are identity, from only 73/451 identity clauses -- disproportionate) |
| **TYPING (separate axis)** | 0.969 | -0.031 | brain uses the FULL cue inventory (reversibility, pronominalization, demonstrative, info-structure) + DEFERS on the possessive ambiguity zone; we use a cue SUBSET (AP/proper-name/definiteness) + FORCE the ambiguity zone. Loss concentrated in identity (0.849 vs 0.99 predicational) |
| **4 INHERITANCE** | ~0 built | **-~1.0 (whole capability)** | brain AUTO-activates category properties via FEATURE-INCLUSION in the ATL hub (directional); our glass-box feature-overlap only WEAKLY supports it (WeedsPrec 0.685 freq-matched 2AFC) -- we bind "doctor" but cannot infer "person" |
| **5 CANONICAL-ENTITY (coref)** | within-clause only | not composed | brain binds to a CANONICAL entity via hippocampal concept-cell reactivation across coref (Dijksterhuis 2024); we bind to the nsubj TOKEN, no cross-sentence resolution |
| **6 PERSISTENCE** | brain-faithful | ~0 | CLOSEST to the brain: state_register default-persists + cancels on contradiction (Dowty inertia; Iatridou perfect) |

**Net absolute gap:** brain ~1.0 -> us 0.818 on the core binding (a 0.18 gap: 0.135 detection + 0.047 holder), PLUS
two whole capabilities the brain has and we do not yet (automatic inheritance; cross-sentence entity resolution),
PLUS a 0.031 typing gap. **The single ROOT divergence behind losses 1, 2, and 5:** the brain is INCREMENTAL,
PREDICTIVE, and DISCOURSE-CONTEXTUALIZED -- it integrates detection + typing + binding + coref + inheritance in ONE
online pass using running discourse context; we run a BATCH, MODULAR pipeline (parse whole sentence -> extract ->
type -> bind) with NO discourse context at detection/binding time and no predictive integration. That one
architectural difference is why the parser fails on hard constructions (batch not incremental), why the holder
fails on equatives (no discourse givenness), and why coref is not composed (modular) -- and it is exactly the
incremental predictive parser + situation-model context the substrate has repeatedly named as its one big lever.

## KEY REALIZATIONS (the enabling moves)
1. **Check the existing organs BEFORE building.** Three organs already covered most of the binding
   (`extract_entity_states`, `state_register`, `definitional_extraction`). Re-deriving the binding would have been
   the duplication trap; instead I reused it and built ONLY the genuinely-absent pieces (typing, fix, process map,
   register/no-regression). *The value is proving it clears THIS bar + the typing + the located fix, not the bind.*
2. **The process map turned "identity is weak" into an actionable root.** Decomposing 451->319->303->297 showed the
   loss is DETECTION (the labeler), not binding -- so the fix targets detection, and the gold-detection ceiling
   (0.807) bounded exactly how much was recoverable BEFORE building the fix.
3. **The copula is closed-class, so don't gate on its label.** The single move that recovered +0.146 was refusing
   to depend on the arc labeler's `cop` output and reading the predication off the copula token + tree instead --
   a brain-faithful "the functional carrier is transparent" principle, not a tuned heuristic.
4. **The research changed a claim I would have gotten wrong.** I was about to call the is-a link a "taxonomic
   hierarchy" (the brief's framing). The drill PINNED that the ATL hub is feature-overlap, not a hypernym graph --
   so a distributional is-a is the faithful substrate, and I do not claim a WordNet hierarchy as brain-faithful.
5. **Equative identity is symmetric, and that is hippocampal.** The CA3 auto-association + rat-lesion evidence
   turned "should identity be ordered or symmetric?" from a guess into a PINNED design choice.

## Adjacent components -- capability / limitation / brain status / next-problem opportunity
| component | capability now | limitation (on-disk) | brain status | next-problem opportunity |
|---|---|---|---|---|
| **arc labeler `cop` recall** | ~0.71 on copular predicates; worse on equatives | mislabels predicate `nsubj`/`root` in "NP is NP" | equative subject-choice = topicality (PINNED); no online-processing lit | **the equative subject/predicate assignment problem** -- an information-structure (givenness/topicality) cue, the field's one consensus lever; the fix's symmetric-identity sidesteps it but a real parser fix is higher-fidelity |
| **is-a inheritance** | NOT built | binding stores the property token, no category link | feature-overlap in ATL hub (PINNED, NOT a hierarchy) | **the is-a category link into the grounded/distributional space** -- inheritance ("doctor -> person") via feature-overlap (Duffy & Keir online activation; graded, minimalist bar) |
| **state_register wiring** | landed, NOT on the live reader path | no `track_state` flag in situation_reader | Kimian state = HOLDER+PROPERTY (PINNED) | **wire state_register + the entity-state slot into the live reader** (couples with the sibling's queued copular landing) |
| **identity -> coref** | typed, not yet merged | identity link not fed to the coref system | coref reactivates hippocampal concept cells (PINNED) | **route identity copulas into coreference** (X == Y merge) -- a symmetric relational bind |

## PROPOSED hdlab DIFF (strategy lands it -- Q111)
1. In `hdlab/situation_reader.py`, behind a new DEFAULT-OFF flag (`bind_entity_states`, coupled to the sibling's
   queued `copular_nominal_events`), add `SituationModel.entity_states: List[EntityState]` and route each `state`-
   sort copular node to it via the binding: HOLDER = the predicate's nsubj (labeled parse), PROPERTY = the
   predicate; TYPE it with the glass-box Higgins classifier (`exp1.predicted_type`) -- predicational (property/is-a)
   vs identificational (identity). Reference impl: `experiments/exp_copular_is_a_binding_readout_v1.py`.
2. **Detection: adopt the label-robust `robust_cop` path** (fire on the closed-class copula + tree, gated) as the
   detector for the entity-state route -- it lifts copular read-back recall +0.146 CI-sep, concentrated on the
   identity type, at a reported precision cost; default the DETECTION to the high-precision label path and expose
   `robust_cop` as a recall-max option (mirrors the sibling's confident-vs-recall-max split).
3. Route **predicational** states into `hdlab.state_register` (`apply_state(entity, value)`; the read-back is its
   `state_at`/`is_in_state`/`had_been`) and **identificational** links as a SYMMETRIC identity edge fed to the
   coreference system (X == Y). No `state_register`/`world_state_register` change -- no-regression verified.
4. Fold the AUDIT UPDATE below into `BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **Copular is-a/attribute BINDING is recoverable + CI-separated** (read-back 0.672 over most-recent-noun 0.503,
  twin loses; fix 0.818). PINNED: predication binds the complement to the subject entity node, TYPED predicational
  (property/is-a) vs identificational (SYMMETRIC identity). The is-a is EMERGENT feature-overlap (ATL hub), NOT a
  hypernym hierarchy (correct the brief's "taxonomic hierarchy" wording). Equative identity is symmetric/hippocampal
  (CA3; Bunsey & Eichenbaum lesion). The predicational-vs-identity NEURAL dissociation is OPEN (extrapolation).
- **The copular-binding residual is a DETECTION (arc-labeler `cop`-recall) gap, worst on the equative identity
  type** (base 0.672 -> gold-detection ceiling 0.807; identity 0.466). The label-robust copula-anchored detector
  recovers +0.146 CI-sep. Refines the sibling's "`cop` is a high-fidelity local signal": `cop` PRECISION is high
  but RECALL is low, and the recall miss is concentrated in nominal/equative complements -- a real lever.
- **Arc labeler equative reversal:** in "NP is NP" the labeler labels the predicate `nsubj`/`root` (subject/
  predicate ambiguity); the consensus resolver is topicality/givenness (no online-processing lit) -- a candidate
  follow-on problem.

## TLDR (plain language)
A lot of what a story says is not an action but a state of being: "Ahab was a captain", "the room was cold", "she
was his wife". The reader could see that such a sentence happened but could not record WHAT the person or thing
IS, so asking "what was Ahab?" got nothing. I built the read-back that attaches the after-the-verb description to
the character, and it answers correctly far more often than the best simple guess (nearest noun), while a scrambled
version does much worse -- so the signal is real, not luck. I then mapped the whole pipeline to find where it still
fails, and the answer was precise: the grammar step that spots the linking "is/was" misses it about a third of the
time, and worst of all on identity sentences ("she is his wife"), where the grammar can't tell which side is the
subject. So I built a fix: since "is/was" is a tiny fixed set of words, don't rely on the fragile grammar label --
find the linking word directly and read the description off the sentence structure. That lifted the score from 67%
to 82%, and the biggest jump was exactly on the identity sentences that were failing worst. I checked it works on
old-fashioned prose too, and that it doesn't break the existing state-tracking. Three kinds of "X is Y" -- a
property ("cold"), a category ("a captain"), and an identity ("his wife") -- are told apart correctly 97% of the
time, and I follow the brain in treating identity as a two-way link (the brain stores such links both directions,
via the hippocampus).

## QUESTIONS
None blocking. One judgement call, flagged: the FIX trades precision (0.77->0.62) for recall (0.67->0.82). I
default the LANDED detector to the high-precision label path and expose the recall-max fix as an option (matching
the sibling's operating-point split). If the owner wants recall-max as the default on the entity-state route, the
fix is ready.

## NEXT STEPS
1. **Land the wire** (proposed diff above): `SituationModel.entity_states` + the typed binding, default-off,
   coupled with the sibling's queued copular landing. Route predicational -> state_register, identificational ->
   symmetric identity edge to coref.
2. **File the is-a inheritance follow-on** ("X is a doctor" -> "X is a person") as a feature-overlap link into the
   grounded/distributional space (NOT a WordNet hierarchy -- Rogers/Patterson), graded per the minimalist bar.
3. **File the equative subject/predicate assignment follow-on** -- a topicality/givenness cue (the field's one
   consensus lever) to fix the labeler's equative reversal; the symmetric-identity treatment sidesteps it now.
4. **Route identity copulas into coreference** (X == Y merge) -- the brain-faithful home for identity (hippocampal
   relational binding; Dijksterhuis 2024).
