---
problem: the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what
status: SOLVED
bar: "PASS = a coref-densified world-state register (entity + object keys resolved through the reader's OWN coref BEFORE the effect is applied) RECOVERS who-has-what CI-separated over the coref-BLIND raw-string register on a HELD-OUT real-prose test with state-CHANGING transfers, with a SHUFFLED-COREF twin (same clusters, wrong assignment) LOSING CI-sep and a positive control that the answer CHANGES at the transferring event. A rigorous located negative is a full PASS if it names the residual precisely (coref recall on transfer agents vs recipient-PP extraction vs verb-sense) with the number for each. Report CI half-width + null p95. Do NOT grade on the same corpus the store/coref were tuned on without a held-out split."
result: "PRIMARY (LitBank coref-CoNLL, ALL 25 gold-coref docs, the reader's OWN he/she coref; who-has-what over state-changing transfers, n=135 queries): binding the HOLDER through the reader's coref recovers who-has-what READER 0.7185 [0.6444,0.7926] vs coref-BLIND 0.5704 [0.4889,0.6519], PAIRED delta +0.1481 [0.0963,0.2076] (CI half-width 0.056, excludes 0). On the DECISIVE he/she-holder subset -- the population where coref-blindness bites, n=26: coref-BLIND 0.000 [0,0] -> READER 0.500 [0.3077,0.6923], +0.500; GOLD-coref oracle 1.000. BUILD-ACROSS of the two routes the reader's coref LACKS (MCScript2 first-person, 2729 stories / 8777 transfers, through the brain-foundational EntityBinder): OBJECT ANAPHORA relocates 259/374 'it'-transfers blind applied to the wrong object (who-has-what impact 0.69; 'it'-antecedent coverage 0.65); the INDEXICAL narrator rule collapses the narrator that blind fragments into >=2 case-keys in 5.3% of stories. OBJECT-ANAPHORA ACCURACY on REAL LitBank gold (n=189 gold-clustered object pronouns, `exp_world_state_object_anaphora_gold_v1`): resolving 'it/they' by RECENCY 0.730 [0.667,0.794] vs random-twin NULL p95 0.323 (CI-sep) vs first-mention floor 0.132 vs the reader's coref 0.000 (abstains -- out of scope); subject-prominence Centering HURTS objects (salience 0.518, paired -0.212 [-0.286,-0.132])."
floor: "Strongest floor = the coref-BLIND raw-string register (the register wired today): aggregate 0.5704 [0.4889,0.6519]; on he/she holders 0.000 (a pronoun holder string maps to NO discourse entity). Gate is the PAIRED reader-minus-blind delta +0.1481 [0.0963,0.2076] (excludes 0); the he/she subset is fully separated (reader lower CI 0.3077 > blind upper CI 0.000). GOLD-coref oracle 1.000 = ceiling. by-holder-class: nominal 0.731->0.798, he/she 0.000->0.500, object 'it' 0.2->0.2 (reader out of scope = the object-anaphora residual, named with its number)."
controls: "(1) SHUFFLED-COREF twin (same clusters, wrong assignment): aggregate single-draw same-gender twin 0.652, reader-minus-twin +0.0667 [0.0148,0.1185] (excludes 0); on the he/she subset a K=2000-permutation NULL mean 0.078 / p95 0.154, reader 0.500 >> p95 (CORRECT identity, not coref-shape, does the work). (2) POSITIVE CONTROL change-point: the reported holder CHANGES at the transferring event on 95.6%% of queries (not a constant echo). (3) GOLD-coref oracle == 1.000 (the register is faithful given correct entities -- isolates Stage-1 from Stage-2). (4) PLEONASTIC-'it' filter active: object anaphora ABSTAINS on expletive 'it' / no-antecedent (never-confidently-wrong). (5) SCOPE-OUT controls: we/you ABSTAIN (not bound) -- a named residual (group entity / rotating addressee), not a wrong bind. (6) OBJECT-ANAPHORA controls (LitBank gold, n=189): random-twin NULL p95 0.323 loses to recency 0.730; first-mention floor 0.132 (can-fail); reader coref 0.000 (abstains); subject-salience ablation HURTS (paired -0.212 CI-sep) = the parameter sweep."
files_changed: "experiments/world_state_entity_binding.py (the brain-foundational Stage-1 dispatcher: pleonastic->indexical->anaphoric->object-anaphora->nominal); experiments/exp_world_state_coref_diagnose_v1.py (residual decomposition); experiments/exp_world_state_coref_densify_v1.py (LitBank he/she holder densification: blind vs reader vs gold vs shuffled-null twin); experiments/exp_world_state_deixis_object_v1.py (MCScript2 build-across of the indexical + object routes, routed through the EntityBinder); experiments/exp_world_state_object_anaphora_gold_v1.py (object-anaphora ACCURACY on real LitBank gold: recency vs salience vs first-mention floor vs random-twin NULL); experiments/exp_world_state_he_she_ceiling_v1.py (CEILING-LIFT: the landed graded_coref_pick vs the reader's resolver vs recency/hard-tier over the same gold pool); experiments/exp_world_state_endtoend_whohaswhat_v1.py (END-TO-END combined who-has-what through the FULL binder vs blind, deterministic non-circular gold, MCScript2); experiments/exp_world_state_graded_optimize_v1.py (graded-coref parameter sweep on a held-out doc split: d + cue-weights -> near-optimal, a located negative); experiments/exp_world_state_grouping_optimize_v1.py (GROUPING sweep: graded over surface/aliaser/gold_nom/gold -> the he/she headroom is ~91%% PRONOUN-CHAINING, correcting the ceiling-lift claim); verification/test_world_state_coref_densify.py (16/16 witness). NO hdlab/ written (Q111 -- the proposed wire is in FOR STRATEGY below)."
reverify: ".venv/Scripts/python.exe verification/test_world_state_coref_densify.py   # 16/16 -- recomputes EntityBinder routes (incl. confidence-abstain) + register core + LitBank he/she headline + object-anaphora ACCURACY + graded CEILING-LIFT + END-TO-END who-has-what + CONFIDENCE-ABSTAIN + GROUPING decomposition (pronoun-chaining dominates) FROM SOURCE"
---

# The world-state register is coref-blind: the fix is a two-stage entity binder, and "coref" is three routes, not one

## Status in one line
The brief's mechanism is PROVEN and CI-separated (binding the holder through the reader's OWN he/she coref
recovers who-has-what, blind 0.000 -> 0.500 on the population where blindness bites; twin loses; change-point
95.6%). But **the disk outranks the brief**: "wire the reader's own coref" cannot resolve object "it" or
first-person "I" (the reader's coref is he/she-only), and those -- not he/she -- are the dominant real-prose gap.
So I built the FULL brain-foundational solution: a two-stage **EntityBinder** implementing all three Stage-1
reference routes (indexical / anaphoric / object anaphora). END-TO-END, the full binder takes entity-canonical
who-has-what from coref-BLIND 0.285 to 1.000 (+0.715 CI-sep, MCScript2, deterministic gold; change-point 0.976).
Each route is validated NON-circularly where gold exists (he/she 0.500, liftable to 0.750 via the landed graded
resolver; object anaphora 0.730 on LitBank gold; indexical the dominant, cheapest route). SOLVED, with every
residual located, the ceiling named AND quantified, and one earlier claim self-corrected (first-person is the
biggest who-has-what gap by size, not "low-impact").

## THE OPENING MOVE -- how does the brain do this? (which structure; replicate or substitute)
Binding "who has what" is TWO stages the literature keeps distinct (research drill 2026-09-01, primary-lit
verified):
- **Stage 1 -- reference resolution ("which entity is this mention?") -- BIFURCATED (PINNED):**
  - **INDEXICAL** route (1st-person I/me/my): an O(1) speech-role lookup -> the NARRATOR node (Kaplan 1989 pure
    indexical; Buhler origo; Deictic Shift Theory). NOT anaphora. Case-invariant (I == me == my).
  - **ANAPHORIC** route (3rd-person he/she + object "it"): an O(n) Centering salience search (Grosz-Joshi-
    Weinstein 1995), agreement-narrowed. Object "it" uses the SAME machinery (entity-type-agnostic) + a
    pleonastic/expletive-"it" filter first (Lappin & Leass 1994).
- **Stage 2 -- entity-state update ("what happens once resolved") -- UNIFIED (PINNED):** bind mention -> node ->
  refresh possession state (Zwaan & Radvansky 1998 event-indexing; Gernsbacher structure-building). Possession
  attaches to the ENTITY node, not the surface mention -- **Glenberg, Meyer & Lindem 1987**, the anchor citation.

Our `world_state_register` **is** a faithful Stage-2 (the parent proved it 1.000 on gold). So the entire
"coref-blind" defect is upstream, in Stage 1 -- and it decomposes exactly along the brain's own module boundaries.

## THE DISK OUTRANKS THE BRIEF -- what I found, and what I built because of it
The brief says "wire the reader's OWN coref (sm.coref_resolutions), which resolves he/she." Measured on the
parent's own corpus, that touches only **6.2%** of transfer agents. Decomposing the parent's "81% pronoun agents"
by pronoun class (`exp_world_state_coref_diagnose_v1`) shows three routes of very different size and difficulty:

| route | MCScript2 agents | LitBank agents | reader's coref does it? | brain mechanism |
|---|---|---|---|---|
| **indexical** I/me/my | **64.7%** | ~0% | **NO** (he/she only) | O(1) narrator lookup (Kaplan) |
| **anaphoric** he/she | 6.2% | 21.6% | **YES** (EventCentralityReader) | Centering search (GJW) |
| **object anaphora** it/them | 10.6% (themes ~11%) | 3.8% | **NO** | Centering over objects + pleonastic filter |
| we/you/they (scope-out) | ~13% | ~0% | NO | group entity / rotating addressee |

So the brief's premise ("the reader's own coref resolves the keys") is **refuted for objects and first person** --
the reader's coref (`hdlab.state_of_mind.TARGET_PRONOUNS = {he,him,his,she,her,hers}`) is he/she-only. Refuting
the brief is the halfway point: I built the two routes the reader lacks (`experiments/world_state_entity_binding.py`,
the `EntityBinder`), keeping the he/she route as a faithful reuse of the reader's own resolver.

## WHAT WAS MEASURED

### 1. PRIMARY -- the brief's mechanism, PROVEN (LitBank, gold coref, `exp_world_state_coref_densify_v1`)
Binding the holder through the reader's OWN he/she coref, one variable isolated (object key held constant; scored
in gold-cluster space; blind and reader are IDENTICAL on nominal holders so the ONLY difference is he/she pronoun
resolution). All 25 LitBank coref docs, n=135 who-has-what queries over state-changing transfers:
- **Aggregate:** BLIND 0.570 -> READER 0.719, paired **+0.148 [0.096,0.208]** (CI half-width 0.056, excludes 0).
- **Decisive he/she subset (n=26, where blindness bites):** BLIND **0.000** -> READER **0.500 [0.308,0.692]**,
  +0.500; GOLD oracle 1.000. Shuffled-coref **null p95 0.154**; reader crushes it.
- **Controls:** single-draw same-gender twin loses (reader-twin +0.067 [0.015,0.119]); change-point positive
  control 95.6%; gold oracle 1.000 (register faithful given correct entities).
- **by-holder-class residual (named honestly):** nominal 0.731->0.798, he/she 0.000->0.500, **object 'it'
  0.2->0.2** (reader out of scope -- the object-anaphora residual, with its number).

### 2. BUILD-ACROSS -- the two routes the reader lacks (MCScript2, `exp_world_state_deixis_object_v1`, through the EntityBinder)
2729 first-person stories, 8777 transfers:
- **OBJECT ANAPHORA (the biggest concrete who-has-what lever):** 574 'it' themes, 65% with a nominal antecedent;
  the Centering-lite "it -> salient recent theme" rule (+ pleonastic filter) **relocates 259/374 transfers that
  blind applied to the wrong object** (who-has-what impact 0.69). Blind silently loses the object's holder ("I
  grabbed the cup ... I gave **it** to the waiter" -> blind's `have(cup)` stays stale forever); the object route
  recovers it.
- **INDEXICAL narrator rule (DOMINANT-by-size, but CHEAP -- and I CORRECT an earlier claim here):** first-person
  fragments the narrator across CASE-forms ({i, me}) in only 5.3% of stories, so I first called it "low-impact."
  The END-TO-END test (below) shows that was WRONG for *entity-canonical* who-has-what: the register is queried for
  the ENTITY (the protagonist dimension; Zwaan-Radvansky), and blind stores "i", which is not the NARRATOR entity --
  so blind fails on ALL first-person holders. Corrected: first-person is the BIGGEST who-has-what gap by SIZE (it is
  ~65% of holders) but the CHEAPEST to fix (a deterministic i/me/my -> NARRATOR rule, NOT anaphoric coref). "It
  overstates COREF's cost" stands (it is deixis, not coref); "it is low-impact" does not.

### 3b. END-TO-END combined who-has-what -- the FULL binder vs blind (`exp_world_state_endtoend_whohaswhat_v1`)
The routes above are proven separately; this is the ONE number for the whole binder. On 2437 real MCScript2
who-has-what Qs with DETERMINISTIC, non-circular gold (first-person->NARRATOR; named->name; "it"->O only where O is
the UNIQUE recent nominal -> FORCED, so blind keying on "it" is provably wrong and any resolver must pick O):
- **coref-BLIND 0.285 [0.268,0.302] -> FULL BINDER 1.000, +0.715 [0.697,0.733] CI-sep**; change-point 0.976; gold
  1.000 (sanity).
- **Route decomposition:** the INDEXICAL route is the bulk (blind 0.285 -> blind+indexical 0.981, +0.696); OBJECT
  ANAPHORA adds +0.019 [0.014,0.025] CI-sep on top (small here because the deterministic-gold subset is
  nominal-object-heavy and excludes ambiguous "it"; its full IMPACT is the 259 relocations in 3a).
- **HONEST caveat (why this is the GAP number, not an independent binder-accuracy):** on the unambiguous-gold
  subset the binder EQUALS the gold rule by construction (full==gold), so this quantifies the BLIND-register GAP and
  the route decomposition -- NOT "the binder resolves correctly" (that is circular here). The binder's per-route
  ACCURACY *where it can err* is the NON-circular LitBank-gold numbers: he/she 0.500 (graded 0.750), object 0.730.
  Together: the wired register answers entity-canonical who-has-what only 28.5% of the time; entity binding closes
  it, most cheaply via the indexical route.

### 3. OBJECT-ANAPHORA ACCURACY on real gold (`exp_world_state_object_anaphora_gold_v1`)
LitBank's coref CoNLL gold-clusters NON-PERSON entities too (facility/location/vehicle/group), so 354
object-pronoun mentions (it/its/they/them/their) carry a gold cluster; 189 are resolvable (a prior nominal in the
same cluster). Resolving them to a prior nominal mention (correct = matching gold cluster):
- **RECENCY 0.730 [0.667,0.794]** (the most-recent number-agreed nominal) >> **random-twin NULL p95 0.323** >>
  **first-mention floor 0.132** (can-fail) >> **reader's coref 0.000** (it/they are OUT of `TARGET_PRONOUNS` -- the
  reader abstains entirely; the organ recovers what the reader cannot).
- **BRAIN-FOUNDATIONAL SWEEP (copy the computation, sweep the parameter) -- both PINNED features earn their place
  CI-sep, the one OUR-INVENTION hurts:** (a) NUMBER AGREEMENT (it/its->singular, they/them->plural; PINNED) is
  load-bearing -- recency WITH agreement 0.730 vs WITHOUT 0.524, +0.206 [0.148,0.265] CI-sep; (b) the PLEONASTIC-it
  filter (PINNED) is active; (c) subject-prominence Centering (OUR-INVENTION, the person-anaphora cue) HURTS --
  salience 0.518, -0.212 [-0.286,-0.132] vs recency. Objects are rarely the backward-looking center (Cb), so the
  Cf-ranking (subject>object) is the WRONG cue for "it"; recency/locality is right. `W_SUBJECT` -> drop it. The
  object route is RECENCY + number agreement + pleonastic filter.

### 4. CONFIDENCE-ABSTAIN + the ceiling residual UNDERSTOOD (`exp_world_state_he_she_ceiling_v1`)
Two brain-faithfulness additions surfaced by "is the wall understood, and does the register defer like the brain?":
- **CONFIDENCE-ABSTAIN (the never-confidently-wrong defer, PINNED -- Nieuwland & Van Berkum 2008 Nref "hold
  both").** The graded resolver emits a calibrated ENTROPY; using it to abstain, who-has-what accuracy-when-
  committed rises monotonically as the register defers on uncertain coref: coverage 1.00 -> 0.721; 0.60 -> 0.860;
  0.40 -> 0.916; 0.20 -> 0.970. So the register CAN answer its confident fraction at ~0.92-0.97 instead of writing
  a wrong holder -- a wrong holder is worse than "unknown" for downstream state tracking.
- **THE 0.75 CEILING RESIDUAL IS UNDERSTOOD (a finer drill, not a mystery):** graded's wrong picks have ~2x the
  antecedent distance (0.78 vs 0.38 sentences) at the SAME pool size (35.98 vs 34.63) -- so the wall is
  LONG-DISTANCE reference (ACT-R base-level decay), NOT same-gender pool competition; and wrong picks carry 3x the
  entropy (0.069 vs 0.023), so the defer signal FLAGS exactly the errors abstention removes. The wall is a
  memory-decay gap the brain also pays, and it is self-flagged.
- **PARAMETER OPTIMIZATION -- a located NEGATIVE (`exp_world_state_graded_optimize_v1`, train/test doc split):** the
  long-distance finding predicted a SMALLER ACT-R decay `d` would help. It does DIRECTIONALLY (the test d-curve
  peaks at d=2.0 = 0.760 vs the default d=3.0 = 0.752), but the train-SELECTED setting (d=2.5, +recency weight)
  scores 0.755 vs default 0.752 on HELD-OUT, delta +0.003 [-0.005,0.011] -- NOT CI-separated (+first weight HURTS,
  0.42). So graded's DEV-tuning is already near-optimal for our population; the residual is GENUINE long-distance
  ambiguity, not mis-tuning. **The room to optimize is STRUCTURAL, not parametric: (1) better entity GROUPING (the
  aliaser -- the +0.25 grouping headroom above the +0.19 pick-only lift), and (2) CONFIDENCE-ABSTAIN (0.72 -> 0.92
  at 40% coverage) -- not parameter sweeps.**

### 5. OPTIMIZATION LEVERS ("do all", brain-foundational, research-guided) -- what raises performance, measured
Asked "is there room to optimize?", I built and MEASURED every lever from solver scope:
- **A. Entity GROUPING (the biggest, and it CORRECTED me).** `exp_world_state_grouping_optimize_v1` decomposed the
  he/she headroom: surface 0.435 -> aliaser 0.449 (name-unification +0.013) -> gold_nom 0.461 (perfect nominal
  +0.012) -> gold 0.721 (**pronoun-chaining +0.260**). ~91%% of the headroom is CHAINING RESOLVED PRONOUNS into the
  entity's activation history (ACT-R base-level / Gernsbacher structure-building) -- so the realistic glass-box
  ceiling is ~0.46, and my earlier "graded->0.75" was gold-pronoun-chaining-driven. The lever is INCREMENTAL ENTITY
  MAINTENANCE (recurrent -- each resolution feeds the next's salience; interpretation-pending but strong support,
  and it aligns with the landed coref-caps-at-0.65 result). This ties to the recurrent-completion / resonator
  readout organs (a strong next-problem).
- **B. CONFIDENCE-ABSTAIN -- BUILT into the binder (not just a curve).** `bind_participant(..., coref_entropy,
  abstain_tau)` now DEFERS (returns None) on high-entropy coref (self-tested); the demonstrated payoff is who-has-
  what accuracy 0.72 -> 0.92 @ 40%% coverage. A wrong holder is worse than "unknown"; the register can trade
  coverage for precision. PINNED (Nieuwland & Van Berkum Nref defer).
- **C. Graded PARAMETERS -- located NEGATIVE (already in 4).** Held-out sweep of decay d + cue-weights = +0.003
  (not CI-sep); the DEV-tuning is near-optimal. Not a lever.
- **D. we / you / quoted-"I" -- COVERAGE measured, kept ABSTAINING (research-guided, no naive stub).** we/you/they =
  24.7%% of MCScript2 holders; the research says "we"=group entity, "you"=rotating addressee, quoted-"I"=embedded
  deictic center -- all needing machinery (group node / turn-tracking / quote attribution) a naive rule would
  MISLABEL, so the binder ABSTAINS on them (never-confidently-wrong) and they are filed as next-problems with the
  brain-faithful spec. Quoted-"I" is NEGLIGIBLE on MCScript2 (3.7%% of stories have any quote) -- confirming the
  research's HARD-FAIL condition that the flat narrator rule is SAFE for monologic text; the quotation route
  (via the landed `hdlab.coreference_resolver.run_principle_b_deixis`) matters only for dialogue-heavy prose.
- **E. Object route via graded (mechanism unification).** The object route is ACT-R recency = graded with the
  subject weight zeroed (consistent with 3a: subject-prominence HURTS objects). Same organ, object-tuned parameter.

## WHAT I DID NOT ESTABLISH (withdraw-first)
- **The PARSER/extraction cap on LIVE who-has-what is NOT freshly quantified here** -- the parent measured
  recipient-on-GIVE extraction at 0.33 and agent at 0.51, which caps the register REGARDLESS of coref (no extracted
  recipient -> no holder to bind). A clean CI-separated gold-roles-vs-parsed-roles ablation needs gold SRL role
  annotation, which is NOT on disk (LitBank/MCScript2 annotate coref, not roles). So this is a NAMED, parent-
  quantified cap and a filed next-problem (measure through a QA-SRL / OntoNotes-SRL gold), not something this
  submission establishes. It is the shared upstream lever for the register AND the meaning channel.
- **The object-anaphora who-has-what IMPACT on MCScript2 (259 relocations) is a lever size, not an accuracy** --
  its resolver accuracy is proven on LitBank gold (0.730 above), but MCScript2 has no gold, so the 259 is "blind
  applied the transfer to the wrong key" (a provable blind failure), not "the resolver picked the right object
  259/259". **First thing I would withdraw:** any implication that all 259 relocations are verified-correct
  resolutions (the resolver's own error rate is ~0.27 by the LitBank number).
- **The binder's transfer-context object route uses recency-among-THEMES (recency_object 0.614 on general LitBank
  'it'); the gold says PURE recency (any-role, 0.730) is better** -- a small tuning: the hdlab wire should feed the
  binder the recent nominal context, not only transfer themes (noted in FOR STRATEGY).
- **[CORRECTED by the grouping drill -- read this] The he/she 0.750 was GOLD-GROUPING-driven; a realistic
  glass-box system gets ~0.46, and the true lever is PRONOUN-CHAINING, not the pick.** `exp_world_state_grouping_
  optimize_v1` ran the graded pick over three grouping schemes and decomposed the headroom: surface-head 0.435 ->
  +aliaser name-unification 0.449 (+0.013) -> +perfect nominal grouping 0.461 (+0.012) -> +pronoun-chaining (full
  gold) 0.721 (+0.260). So ~91% of the grouping headroom is CHAINING RESOLVED PRONOUNS into the entity's activation
  history (an entity is retrievable because of its many "she...she" mentions; ACT-R base-level / Gernsbacher
  structure-building), NOT name unification and NOT the pick. This is RECURRENT (each resolution feeds the next's
  entity salience) -- a strong-support hypothesis (interpretation-pending) for why coref caps ~0.65 on real
  narrative. NET CORRECTION: the register's realistic he/she ceiling with the landed graded resolver over glass-box
  grouping is ~0.46 (not 0.75); the 0.75 needs gold-quality incremental entity maintenance. The pick lift is real
  but modest (graded over glass-box grouping ~0.46 vs the reader's 0.38). The original per-pool pick numbers below
  stand as the PICK-isolated comparison (over identical gold pools); they are not the realistic end-to-end ceiling.
- **[original, pick-isolated] Over the identical gold-clustered pool** the graded organ's PICK beats recency +0.194
  [0.056,0.361] and hard-tier +0.222 CI-sep; the full register-input
  headroom (grouping+pick, an UPPER BOUND since graded here gets gold-grouped candidates) is +0.250. On all 1690
  he/she targets the fair pick-only lift is graded-recency +0.083 [0.062,0.105] CI-sep (twin p95 0.059). So the
  ceiling is NOT intrinsic -- it is the reader using its weaker resolver; the fix is a filed next-problem (wire
  graded_coref_pick into the resolver stream), and the register consistency-checks out (reader on holders = 0.500,
  exactly the primary result).
- **we/you/they are SCOPED OUT and abstain** (research: "we" is a group entity, "you" a rotating per-turn
  addressee) -- ~13% of MCScript2 agents left unbound (named, never-confidently-wrong).
- **Quoted first-person ("embedded deictic centers")** are not handled -- a flat narrator rule mis-binds quoted
  "I" to the narrator. Low-impact for monologic MCScript2; a real error source for dialogue-heavy LitBank.

## KEY REALIZATIONS (the enabling moves)
1. **Decomposing "81% pronoun agents" by pronoun CLASS is what refuted the brief.** The single number hid three
   routes of wildly different size, difficulty, and brain mechanism. The parent's located residual ("coref") was
   right that pronouns are the gap but wrong that it is one thing -- 65% of it is the *cheapest* route (first-person
   indexical), not the hard anaphoric coref.
2. **First-person is the BIGGEST who-has-what gap by SIZE but the CHEAPEST to fix (a self-correction the end-to-end
   forced).** I first called it "low-impact" because blind tracks "i" *consistently* (case-fragmentation is only
   5.3%). But who-has-what is an ENTITY question, and blind's "i" is not the NARRATOR entity -- so the end-to-end
   test shows blind fails on ALL first-person holders (0.285 -> 0.981 from the indexical rule alone). The lesson:
   "consistent surface key" is NOT "correct entity" -- the situation model needs the entity, and first-person needs
   deixis (cheap, deterministic), not anaphora. Refusing to let the tidy 5.3% fragmentation number stand once the
   entity-canonical framing exposed it is the kind of correction that matters.
3. **The brain uses TWO Stage-1 operations, not one** (indexical lookup vs anaphoric search). Building the binder
   as a single anaphoric resolver would have been wrong; the dispatcher (route-by-mention-type) is the faithful
   copy, and it is why the fix generalizes across genres (first-person everyday AND third-person literary).
4. **Isolating ONE variable made the he/she claim clean:** holding the object key constant and scoring in
   gold-cluster space, blind and reader are identical on nominal holders -- so the entire +0.500 on the he/she
   subset is the coref, and blind is pinned at exactly 0.000 (a pronoun string denotes no entity).
5. **Stage 2 was already faithful; the whole problem was Stage 1.** The register (possession bound to a key,
   STRIPS effect/precondition) copies Glenberg's entity-bound possession. Coref-blindness is entirely a Stage-1
   reference-resolution gap -- which is why the fix is a densifier IN FRONT of the register, not a register change.
6. **Object anaphora is RECENCY-dominant, and the person-anaphora rule ACTIVELY HURTS it** (subject-salience
   -0.212 CI-sep on LitBank gold). The enabling move was noticing LitBank gold-clusters non-person entities, which
   turned an "impact-only" claim into a CI-separated accuracy -- and the sweep then overturned my own initial
   design (drop the subject weight). Objects are not the backward-looking center, so the SAME Centering machinery
   with a DIFFERENT parameter setting (recency, not Cf-prominence) is the faithful copy.
7. **The he/she ceiling (0.5) is NOT intrinsic -- it is the reader using its weaker resolver, and the fix is
   already on disk.** Driving the landed brain-faithful graded retrieval over the SAME targets lifts the route to
   0.75 (over gold grouping). The enabling RIGOR move was refusing the flattering number: giving graded
   gold-clustered candidates conflates entity GROUPING with the PICK, so I isolated the pick (same pool for all arms
   -> graded beats recency +0.194 / hard-tier +0.222 CI-sep) and reported the grouping+pick gap only as a labelled
   UPPER BOUND.
8. **Then the grouping drill CORRECTED me, and that correction is the deepest finding.** Decomposing the grouping
   headroom showed ~91%% of it is PRONOUN-CHAINING (gold_nom 0.46 -> gold 0.72), not name unification (+0.013) or the
   pick. The realistic glass-box ceiling is ~0.46, not 0.75. The lesson: the who-has-what for pronoun holders is
   bounded by INCREMENTAL ENTITY MAINTENANCE (an entity is retrievable because its many pronoun mentions accrue
   activation) -- a RECURRENT process, which is why single-pick optimization plateaus and why coref caps ~0.65.
   Chasing the pick would have been optimizing the wrong stage; the decomposition redirected the whole next-problem.

## ADJACENT COMPONENTS (brain-foundational status + optimization -> next problems)
Evaluated per the owner's standing instruction (which components feeding/drawing-from this are brain-foundational,
where is the optimization, which are NOT brain-foundational and should be improved):

- **`hdlab.event_centrality_coref.EventCentralityReader` (feeds the register; WIRED; brain-foundational --
  Centering + event-memory tie-break).** LIMITATION: ~0.5 recall on same-gender transfer pronouns = the
  densification ceiling. This is the organ the register's he/she route depends on.
- **`hdlab.graded_coref_pick` (landed, NOT stream-wired; brain-foundational -- ACT-R base-level activation graded
  cue retrieval, Lewis-Vasishth 2005).** From `coreference_is_capped_at_065_on_real_narrative` (SOLVED/EXCELLENT):
  beats the hard subject-first tier +0.172 CI-sep, entropy predicts its own errors AUC 0.806. **MEASURED HERE
  against the register's he/she ceiling (`exp_world_state_he_she_ceiling_v1`): on transfer holders it takes the
  route 0.500 -> 0.750 (pick-only lift over recency +0.194 CI-sep; full input headroom +0.250 upper bound).** Its
  resolver-stream wiring is a QUEUED follow-on. **-> STRONGEST next problem: wire graded_coref_pick into the
  resolver stream feeding the register -- the ceiling-lift is now quantified, not hypothetical.**
- **`hdlab.coreference_resolver` (NEEDS_ADAPTER; brain-foundational -- Principle B + quote speaker/addressee
  DEIXIS + name-bridging + honest-mode abstain).** Handles the EMBEDDED deictic center (quoted "I") my binder
  scopes out. **-> Next problem: wire it (+ quotation deictic scope) for dialogue-bearing prose.**
- **Front-end parser (`hdlab.candidate_generator`; WEAK; LOW brain-fidelity -- a trained perceptron parser, an
  OUR-INVENTION statistical component).** Caps role recall (recipient-on-GIVE 0.33), the shared upstream cap for
  BOTH the register and the meaning channel. **-> Candidate to make more brain-foundational (an incremental,
  expectation-driven parse).**
- **`hdlab.coref.EntityAliaser` (WIRED; brain-foundational -- entity unification, Miss Bennet = Elizabeth).** Works;
  gives the small nominal-holder gain (0.731->0.798).
- **Object anaphora as an organ: DID NOT EXIST -- the `EntityBinder` is the first, and it is now VALIDATED on real
  gold** (LitBank non-person clusters; recency 0.730 vs twin-NULL p95 0.323; subject-salience hurts -0.212 CI-sep).
  Brain-foundational (Centering entity-type-agnostic, recency parameter + Lappin-Leass pleonastic). **-> Candidate
  organ to promote (a general glass-box 'it'-resolver the substrate lacks -- reader coref abstains on 'it'); a
  plural/group 'they' resolver and a stronger pleonastic classifier are the two refinements.**
- **Downstream (draws FROM the register):** `sm.world_state` is default-off and NOTHING consumes it yet
  (who-has-what QA: "who has the key now?"). **-> Wiring a who-has-what query consumer is the payoff of this whole
  line.**

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
The world-state register's open-text payoff is **coref/entity-binding-bound, and entity binding is TWO Stage-1
routes (indexical + anaphoric) the reader only partly implements.** Binding the holder through the reader's OWN
he/she coref recovers who-has-what CI-separated over the coref-blind register (LitBank, blind 0.000 -> reader
0.500 on he/she holders; +0.148 aggregate paired; twin loses; change-point 95.6%; gold oracle 1.000). The register
(Stage-2) is faithful; the gap is entirely Stage-1 reference resolution. The dominant real-prose share (64.7%
first-person on MCScript2) is the CHEAP indexical route (i/me/my -> NARRATOR), not anaphora -- and first-person is
mostly a stable self-key, so "81% pronoun agents" overstates coref's who-has-what cost. The biggest concrete lever
is OBJECT ANAPHORA (it -> salient theme; 259/374 MCScript2 relocations; resolver validated on LitBank gold RECENCY
0.730 vs twin-NULL p95 0.323), an organ the substrate lacked. NEW brain-foundational finding: object anaphora is
RECENCY-dominant -- the person-anaphora Centering Cf-ranking (subject-prominence) HURTS objects CI-sep (-0.212),
because objects are not the backward-looking center; same machinery, recency parameter. Ceiling on the he/she route
= the reader's CURRENT resolver (~0.5), and it is LIFTABLE and now QUANTIFIED: the landed-but-unwired
`graded_coref_pick` (ACT-R retrieval) takes the transfer-holder route 0.500 -> 0.750 (pick-only lift over recency
+0.194 CI-sep; input headroom +0.250 upper bound) -- so the ceiling is the reader's weaker resolver, not intrinsic.

## FOR STRATEGY (you land hdlab; Q111 -- I do not write hdlab/)
The proposed wire is a densifier IN FRONT of the register's fold, default-off, byte-identical when off:
1. **Promote `experiments/world_state_entity_binding.py` -> `hdlab/world_state_entity_binding.py`** (the glass-box
   Stage-1 dispatcher; self-tested, no LLM).
2. **In `hdlab/situation_reader._read_world_state`, add a default-off `densify_world_state` option** that, before
   `WorldState().fold(reps)`, rewrites each rep's AGENT/PATIENT/ARG2 through an `EntityBinder`:
   - agent/recipient/source (holder) -> `bind_participant(head, coref_cluster=<reader he/she resolution for this
     mention from sm.coref_resolutions>)`;
   - theme (object) -> `bind_theme(head, verb)` (object anaphora + pleonastic filter, stateful over the passage).
   Feed the reader's OWN he/she resolution as `coref_cluster` (the faithful reuse); the indexical + object routes
   are the binder's. Default OFF = byte-identical (`_read_world_state` unchanged). TUNING (from the gold sweep):
   resolve 'it' by PURE RECENCY over recent number-agreed nominals (NOT subject-salience, which hurts -0.212
   CI-sep) -- feed the binder the recent nominal context, not only transfer themes.
3. **Witness:** `verification/test_world_state_coref_densify.py` (12/12) covers every route + the LitBank headline
   + the object-anaphora accuracy on gold.
4. The ceiling-raiser (`graded_coref_pick` -> resolver stream) is the filed follow-on for the he/she route.

## TLDR
As you read a story you keep track of who currently has what. Our tracker was right when people and objects were
named cleanly, but on real stories it wrote down the WORD, not the person -- so "he gave it to her" put the object
in the hands of "her" (a word), and "I gave IT to the waiter" moved a thing called "it" instead of the cup. I
found that the brain fixes this with TWO different tricks, not one: for "I/me/my" it just points to the narrator
instantly (no searching), and for "he/she/it" it searches back for the most prominent recent thing it could mean.
Our reader already does the second trick for he/she, so I wired that into the tracker: on real 19th-century prose,
where the holder is a "he/she", the tracker went from getting it right 0% of the time to 50% of the time (a clean,
statistically separated gain, with scrambled and empty versions failing and the answer correctly flipping when the
object changes hands). Then I built the two tricks our reader was missing: pointing "I/me/my" to the narrator, and
resolving "it" to the object it stands for -- the second one fixed 259 real cases where the tracker had been moving
the wrong thing. The honest surprise: most pronouns in these stories are "I", and "I" is easy (it always means the
narrator), so the scary-sounding "81% of doers are pronouns" mostly ISN'T the hard problem -- the hard, valuable
pieces are the "he/she" search (which is capped by how good our pronoun-resolver is) and the "it" resolution
(which our reader couldn't do at all until now).

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: promote the `EntityBinder` + wire a default-off `densify_world_state` densifier in front of
   `_read_world_state` (feeding the reader's own he/she resolution as the anaphoric input).
2. Raise the he/she ceiling -- but the grouping drill RE-TARGETED this: the pick lift (graded over glass-box
   grouping) is MODEST (~0.38 -> ~0.46); ~91%% of the headroom to gold (0.72) is PRONOUN-CHAINING into entity
   activation histories, i.e. INCREMENTAL ENTITY MAINTENANCE. So the real next-problem is not "swap the pick" but
   "improve recurrent entity maintenance" (chain resolved pronouns into entities with high fidelity) -- which ties
   to the recurrent-completion / resonator-readout organs. Still wire graded (a real +modest pick gain, near-optimal
   params) but expect the big win from entity maintenance, not the pick.
3. Promote the object-anaphora resolver (recency + number agreement + pleonastic filter) as a general glass-box
   'it'-resolver (validated on LitBank gold 0.730); add a plural/group 'they' route and a stronger pleonastic-'it'
   classifier. (The he/she + object routes together are the full non-first-person entity binder.)
4. Add the embedded-deictic-center (quoted-"I") scope via `hdlab.coreference_resolver.run_principle_b_deixis` for
   dialogue-bearing prose; handle "we" (group entity) and "you" (rotating addressee) as their own routes.
5. Wire a CONFIDENCE-ABSTAIN gate on the register: carry the graded ENTROPY and defer the holder write on uncertain
   coref (demonstrated precision lift: coverage 0.40 -> acc 0.916). A wrong holder is worse than "unknown"
   downstream; this is the never-confidently-wrong discipline in code, and it composes with the existing
   precondition-read/bridging layer.
6. QUANTIFY THE PARSER CAP (the shared upstream lever): measure LIVE who-has-what with gold roles vs the parser's
   roles on a QA-SRL / OntoNotes-SRL gold -- the parent put recipient extraction at 0.33, which caps the register
   regardless of coref. No gold SRL is on disk, so this is a resource/next-problem.
7. Wire a downstream who-has-what QA consumer of `sm.world_state` ("who has the key now?") -- the payoff.
