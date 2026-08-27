---
problem: wire_entity_tracking_end_to_end_on_running_narrative
status: SOLVED
bar: "Correct (salience-bound) entity linking must improve a DOWNSTREAM entity task (next-argument prediction, or cross-sentence who-did-what) CI-separated over its UPPER bound vs STRING-IDENTITY linking, with an info-free twin (shuffled entity links) LOSING CI-separated. Report CI half-width + null p95. Attribute the gain to the LINKING (ablate the binder -> string-identity)."
result: "MET on the CROSS-SENTENCE WHO-DID-WHAT task. Composing the ACT-R salience binder + coref threads + the REAL situation-model register (hdlab.situation_model_accumulate), recovering what an entity DID at a queried sentence (decode its governing verb from the entity's register, anchored on a NAME mention): on the pronoun-contributed subset (n=9,078 pronoun queries over 100 LitBank documents; majority-verb floor 0.137), salience-bound ACT-R linking scores 0.1739 [0.1536, 0.1959] vs the string-identity default 0.0589 [0.0515, 0.0679] -- paired +0.115 [0.0951, 0.1352], half-width 0.0201. On the FULL task (name + pronoun queries) +0.0249 [0.0175, 0.0329] (diluted; names are string-resolvable in every arm). The info-free shuffled-link twin (pronoun -> RANDOM gender/number-compatible entity) LOSES: ACT-R beats it +0.0731 [0.0516, 0.0934] (twin accuracy 0.1008, its 97.5 upper 0.1095 = the null p95). DECISIVE the OTHER way on anticipatory PREDICTION (below): correct linking does NOT improve next-argument prediction -- a clean dissociation."
floor: "Strongest floors recomputed on the LitBank population, pronoun subset: STRING-IDENTITY linking (the bar's named floor) 0.0589 [.0515,.0679]; the RECENCY-linking floor 0.1610 [.1429,.1814]; the majority-verb floor 0.1368; ORACLE (gold coref) ceiling 0.6182 [.5977,.639]. ACT-R (0.1739) clears string-identity's UPPER bound (0.0679) CI-separated; it does NOT clear recency (ACT-R - recency = +0.0129 [-0.0004, 0.0282], NOT separated -- honest: downstream, the ACT-R refinement over simple recency does not propagate)."
controls: "(1) INFO-FREE TWIN (shuffled-link: pronoun -> random compatible entity, same linking SHAPE, entity scrambled): 0.1008, ACT-R beats it +0.0731 CI-separated -> CORRECT binding, not merely 'a link exists', is the source. (2) BINDER-ABLATION (ACT-R -> string-identity): drops 0.1739 -> 0.0589, isolating the gain to pronoun linking; the full-set gain (+0.025) is far smaller than the pronoun-subset gain (+0.115) -> the marginal value LOCALIZES to pronouns, as it must. (3) RECENCY floor 0.1610: ACT-R does NOT clearly beat it (+0.0129 NOT separated) -- reported against myself. (4) ORACLE ceiling 0.6182: ACT-R recovers 0.1739 = 28% of the recoverable who-did-what -> large binder+decode headroom. (5) FAN-EFFECT diagnostic (demanded by the composition drill): oracle decode degrades 0.6954 -> 0.6079 as an entity's event-count grows 1-3 -> 17+ -> the dense-bundle register IS the shortcut the drill flagged; evidence now backs the pattern-separated-store proposal. (6) PREDICTION DISSOCIATION (the bar's OTHER admissible task): on anticipatory next-object prediction via the grounded content-addressable channel, correct linking does NOT help -- the discourse gist alone is already at chance (2.9992 vs chance 2.9957), adding the entity state HURTS (-0.2192 CI-sep), and correct linking is if anything WORSE than string-identity (AUG_ACTR - AUG_STRID = -0.0993 CI-sep BELOW), holding even for ORACLE linking (-0.1307). Object-recurrence is absent/anti-predictive in literary narrative at this representation, so there is no prediction signal for linking to improve. (7) GRADED-BINDING deepening (ERP Nref-motivated): a soft activation-weighted update BEATS hard argmax on the who-did-what recall (see below)."
files_changed: "experiments/exp_litbank_entity_tracking_end_to_end_v1.py (the composition cell: who-did-what --run, anticipatory prediction --predict, graded-binding --graded); verification/test_entity_tracking_end_to_end.py (scaffold-free witnesses); data/litbank/who_did_what_events.json (spaCy-annotated event cache -- built under data/litbank, NOT data/foundation); notes/problems/wire_entity_tracking_end_to_end_on_running_narrative/research_composition_brain_mechanism_2026-08-27.md (research drill). NO hdlab/ file changed (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_entity_tracking_end_to_end.py"
---

# Wiring entity tracking end-to-end on running narrative: correct pronoun linking recovers cross-sentence WHO-DID-WHAT that string-identity discards -- but does NOT improve next-argument PREDICTION. A clean dissociation.

## Headline in plain language

We had already built and separately proved the two halves of "follow the characters in a story": working
out WHO a pronoun refers to (by grammatical prominence / recency -- the salience binder), and a channel that
predicts WHAT a character does next (its role-structured memory). This joined them on a real running story
(LitBank novels) and asked the payoff question: does correctly resolving "he/she/they" into the right
character -- instead of the cheap trick of only matching identical names -- actually help the reader
understand the story?

Two answers, and the split is the finding:

- **YES for "who did what across sentences."** When the story later asks "what did *she* do back in that
  scene?", you can only answer if "she" was correctly tied to the right character. Correct linking recovers
  that information; name-matching-only throws it away (a pronoun shares no letters with a name, so it becomes
  an orphan). The improvement is clean and separated, and -- crucially -- it needs the *correct* character:
  a version that links each pronoun to a *random* compatible character does much worse.
- **NO for "predict what the character does next."** Correctly linking the pronouns gives the prediction
  channel a fuller history of the character, but on these novels that fuller history does **not** help
  predict the next thing the character acts on -- in fact it slightly hurts, because characters tend to act
  on *new* things (novelty), so their past objects point away from the next one. This holds even with
  *perfect* linking, so it is not a linking failure -- there is simply no prediction signal here for linking
  to improve.

So the value of correct pronoun resolution, measured end-to-end, is **retrieval/attribution** (keeping each
character's history reachable), not **anticipation** -- at least on literary narrative with our current
meaning representation.

## What the brain does, and how faithful this is (the drill's verdict -- PINNED vs OUR-INVENTION)

A fresh, deep research drill on the COMPOSITION mechanism (not the two channels, already drilled) --
`notes/problems/wire_entity_tracking_end_to_end_on_running_narrative/research_composition_brain_mechanism_2026-08-27.md`,
4 parallel lit-scans -- returned a sharp, honest verdict:

- **PINNED (the strongest single result): resolving a pronoun REACTIVATES the referent's stored
  representation.** Two independent, convergent 2023-2024 studies: Dijksterhuis et al. 2024 (*Science*,
  single-unit hippocampal recording -- concept cells for a named character re-fire at a later pronoun
  referring to it) and Ding, ten Oever & Martin 2023 (MEG delta-band population reinstatement). Coreference
  IS reactivation of the bound entity's conceptual content. My composition -- correct linking makes the
  pronoun-clause event retrievable from the entity's register -- is a computational model of exactly this
  reactivation/retrievability.
- **NOT PINNED (untested in humans): that the reinstated state then IMPROVES downstream prediction.** No
  study closes that loop. **So my experiment is a computational TEST of that untested Step 3 -- and it comes
  back NEGATIVE for next-argument prediction on narrative** (the reinstated history does not predict the next
  object), while POSITIVE for who-did-what retrievability. That is a genuine contribution: the loop does not
  auto-close; what reinstatement buys here is access, not anticipation.
- **OUR-INVENTION / SHORTCUT (named, and now MEASURED): the dense-bundle register.** The drill flagged that
  accumulating an entity's events into one FHRR bundle and decoding by algebraic unbind is a shortcut; the
  faithful design keeps the bundle as a *gist* but adds a *pattern-separated* per-entity trace store retrieved
  by pattern completion, whose signature is a **fan effect** (decode degrading as event-count grows). It told
  me to MEASURE that degradation before proposing the fix. I did: oracle decode falls 0.695 -> 0.608 from
  1-3 to 17+ events per entity -- the fan effect is present. The pattern-separated store is now an
  evidence-backed proposal, not a hunch (and it matches the standing audit's dense->sparse deviation).
- **PROHIBITION (honored in framing): do NOT claim strict serial "resolve fully, THEN predict".** Kehler &
  Rohde, ACT-R additive activation, and McKoon & Ratcliff resonance all argue salience+content are scored
  JOINTLY. I present the composition as a computational-level decomposition (salience selects -> the selected
  entity's content is reinstated -> content conditions the readout), NOT a two-stage brain architecture.
- **PIN (acted on -- the deepening win): mis-binding cost is ERP-case-typed.** Ambiguity evokes an Nref (a
  sustained anterior negativity = the reader holds MULTIPLE candidates active under working-memory load), NOT
  a silent wrong-commit. I turned that into a GRADED binding variant (distribute the pronoun's event across
  candidates by softmax of activation) and tested it -- see below; it WINS.

## What I built

`experiments/exp_litbank_entity_tracking_end_to_end_v1.py` -- a wire-and-measure that COMPOSES three organs
we own, holding the text fixed across arms and varying ONLY how pronouns are linked:
1. **Salience BINDER** -- ACT-R base-level activation (reused verbatim from `entity_binding...`: `score_actr`,
   `ROLE_W`, agreement filter) resolves each pronoun to a gender/number-compatible active entity.
2. **Coref THREADS** -- names link by head-token overlap (identical in every arm); pronouns link per the arm.
3. **The REAL situation-model REGISTER** -- `hdlab.situation_model_accumulate.make_situation_register`
   (multibank backend, for capacity), accumulating `bind(action, event-slot)` per entity and decoding
   `decode(entity, slot)` = "what did this entity do at that event." No reimplementation of the organ.

Arms (same mention stream, same event-slots): ORACLE (gold coref, the ceiling), ACTR_BINDER (the mechanism),
STRING_IDENTITY (pronouns are singletons -- the bar's floor), RECENCY (pronoun -> most-recent compatible
entity), SHUFFLED_TWIN (pronoun -> random compatible entity -- the info-free null). Bootstrap over documents.

Two downstream readouts (both admissible under the bar):
- **`--run` cross-sentence WHO-DID-WHAT** (verb-decode; majority-verb floor 0.137, so it is a rich, not
  majority-trivial task). THE HEADLINE. Corpus: LitBank (100 novels, 9,078 pronoun-contributed queries).
- **`--predict` anticipatory NEXT-ARGUMENT prediction** (the drill's more-faithful readout): predict the
  OBJECT a recurring agent acts on next, from its accumulated state, via the grounded content-addressable
  channel (`_g` 12-dim grounded vectors, 93% coverage; the SAME channel validated in
  `the_situation_model...`). Arms: entity-ALONE (the known-weak "replace" family) AND the faithful
  gist++entity AUGMENT family, each under every linking policy, vs a discourse-gist-only and a frequency
  floor.
- **`--graded` deepening**: soft activation-weighted binding vs hard argmax (the Nref test), with a
  uniform-weight control.

## What I measured (all CI'd; reverify = the witness, PASS)

**1. THE BAR IS MET (cross-sentence who-did-what).** ACT-R salience-bound linking beats string-identity
CI-separated: pronoun subset **+0.115 [0.0951, 0.1352]** (hw 0.020), full task **+0.0249 [0.0175, 0.0329]**.
STRING_IDENTITY on the pronoun subset is 0.0589 (a pronoun cannot string-match a name -> its events are
orphaned). BAR MET.

**2. THE INFO-FREE TWIN LOSES -- correct binding, not any link, is the source.** SHUFFLED_TWIN (pronoun ->
random compatible entity) scores 0.1008; ACT-R beats it **+0.0731 [0.0516, 0.0934]** (null p95 = twin upper
0.1095). The twin does beat string-identity a little (+0.042: any link recovers some events by chance), which
is exactly why the twin -- not string-identity -- is the control that isolates *correct* binding.

**3. HONEST DEFLATION #1: ACT-R does NOT clearly beat simple RECENCY downstream.** RECENCY-linking scores
0.1610; ACT-R - recency = **+0.0129 [-0.0004, 0.0282], NOT separated**. The expensive ACT-R refinement that
beat recency on the isolated PICK (0.837 vs 0.658 in `entity_binding...`) does not clearly propagate to the
downstream recall -- most of the downstream value is "link the pronoun to *something* recent-and-compatible."

**4. HONEST DEFLATION #2: large headroom.** ORACLE (gold coref) scores 0.6182; ACT-R recovers 0.1739 = 28% of
the recoverable who-did-what. The gap is imperfect binding compounded with imperfect decode.

**5. THE FAN EFFECT IS REAL (the drill's demanded fidelity check).** Oracle decode by entity event-count:
1-3 -> 0.695, 4-8 -> 0.626, 9-16 -> 0.638, 17+ -> 0.608. The dense FHRR bundle degrades as an entity
accumulates events -- the exact signature the drill said a pattern-separated store would remove.

**6. THE PREDICTION DISSOCIATION (decisive the OTHER way).** On anticipatory next-object prediction
(n=2,885 targets, 100 docs, 20 candidates, chance surprisal 2.9957; LOWER = better):
- The discourse GIST alone is already **at chance** (2.9992) -- next objects are not predictable from prior
  content at this 12-dim representation.
- Adding the entity state HURTS: gist++entity (ACT-R) 3.2183 vs gist-only 2.9992 = **-0.2192 [-0.2477,
  -0.1911] BELOW** -- adding an uninformative entity cue to an already-at-chance predictor DILUTES it
  (cue-overload; the finest-resolution drill flags this as the likely mechanism of the small negative, rather
  than a strong "novelty" claim -- either way, the entity supplies no usable predictive signal).
- Correct linking is if anything WORSE than string-identity: AUG_ACTR - AUG_STRID = **-0.0993 [-0.1234,
  -0.0764] BELOW**; on name-only targets NOT separated (-0.0004); and even ORACLE linking is worse than
  string-identity (-0.1307). The entity-ALONE family shows the same (-0.0599).
- CONCLUSION: correct linking cannot improve a prediction signal that is not there. This LOCALIZES the value
  of pronoun resolution to attribution/retrieval, and it directly answers the drill's untested Step 3: the
  reinstatement->prediction loop does NOT auto-close on literary narrative at this representation.

**7. THE DEEPENING WIN -- graded (Nref-faithful) binding BEATS hard argmax, AND the activation-weighting is
what makes it work.** Distributing each pronoun's event across its candidates by softmax(ACT-R activation) --
the graded competition the Nref literature pins -- recovers MORE downstream who-did-what than committing to
the single argmax. Full 100-doc, pronoun subset: SOFT_graded_activation **0.2051 [0.1853, 0.2253]** vs
HARD_argmax **0.1783 [0.1569, 0.201]**, SOFT-HARD = **+0.0268 [0.0189, 0.0346] ABOVE**. Critically, a
UNIFORM-weight control (spread the event EQUALLY across the same candidates) scores **0.1322** -- WORSE than
hard argmax (UNIF-HARD = -0.0462 [-0.0679, -0.0238] BELOW); SOFT beats UNIF **+0.0729 [0.053, 0.0928]**. So
the win is NOT mere hedging/spreading (uniform hedging HURTS); it is that the softmax preserves the correct
entity's ACTIVATION-WEIGHTED share, so when the binder is uncertain the correct entity still keeps enough of
the event to win cleanup. The reader hedges under ambiguity exactly as the Nref says -- weighted by
activation, not uniformly -- and it pays off downstream. This is a concrete, brain-motivated improvement the
convenient hard-argmax skipped.

A TEMPERATURE SWEEP (100 docs) makes the brain claim airtight -- the graded win is a TEXTBOOK INTERIOR
OPTIMUM, not a lucky setting: SOFT pron-recall rises from the hard-argmax limit (temp->0 = 0.1783) to a PEAK
at temp~2.0 (0.2084, SOFT-HARD +0.0301), then FALLS back through hard (temp 4.0 = 0.1783, +0.0000) and decays
toward the uniform-flat limit (temp 8.0 = 0.1498; temp 20 = 0.1386 -> UNIF 0.1322). Both extremes --
winner-take-all (temp->0) AND uniform (temp->inf) -- are WORSE than intermediate graded, and SOFT beats the
uniform control at EVERY temperature (+0.05 to +0.076). This inverted-U is exactly the divisive-normalization
prediction (Carandini & Heeger 2012: the exponent n nests argmax/graded/uniform, and an INTERMEDIATE n is the
canonical cortical computation). So the pinned finding is the SHAPE (intermediate activation-weighted
competition wins); the temperature is a fitted parameter (~2.0 here), as the literature says it must be.

## FINEST-RESOLUTION LIMITS DRILL -- do we understand WHY the limits are what they are? (owner request)

A third, finest-resolution research drill (`research_limits_finest_resolution_2026-08-27.md`, 4 lit-scans)
asked, for each limit, whether it is a GENUINE property of the brain/task or a MISSING MECHANISM:

- **THE PREDICTION NULL IS A GENUINE LIMIT -- and the dissociation is brain-real.** Naive episodic
  entity-history recurrence (what I tested) was NEVER the brain's prediction mechanism. The literature's
  PRIMARY drivers of narrative prediction are EVENT SCHEMAS/SCRIPTS (Bower/Black/Turner 1979; Baldassano/
  Hasson/Norman 2018 -- schema patterns in mPFC/PMC that GENERALIZE ACROSS character identity) and
  VERB-DRIVEN THEMATIC FIT / selectional preference (Altmann & Kamide 1999; McRae; Metusalem et al. 2012
  N400 to event-consistent words) -- one "generalized event knowledge" system that pools regularities across
  a lifetime of experience and is EXPLICITLY ENTITY-AGNOSTIC (Cohn & Paczynski 2013: it is Agent-ROLE
  occupancy, not identity, that carries predictive weight). Coreference/entity-tracking in this literature
  serves RETRIEVAL, CONSISTENCY-MONITORING, and referential-continuity ("who is talked about next" --
  Centering's Cb/Cp; Zwaan et al. 1998 protagonist-continuity is MONITORED, i.e. a reading-time cost, not an
  anticipation signal) -- NOT content-anticipation. So my measured dissociation (linking helps who-did-what
  RETRIEVAL, not next-argument PREDICTION) is exactly what the neuroscience predicts. A single character's
  in-story history is also a tiny sample (single-digit instances) vs the schema system's lifetime aggregate --
  a statistical-power reason to expect the null independent of any bug.
- **WHAT WE ARE LEAVING ON THE TABLE (named, ~55-65% it would help): SCHEMA-ROLE-conditioned prediction, not
  entity-content.** The faithful entity contribution to prediction is the entity's CURRENT abstract
  schema-ROLE / slot-type (e.g. "currently the Agent of a request-fulfilment event"), NOT its accumulated
  content history -- and crucially, oracle coreference does NOT supply the role (it tells you WHICH entity, not
  WHICH role it occupies). Chen/Lu/Beukers/Baldassano/Norman 2021: role-filler binding generalizes to novel
  fillers ONLY when role and filler are kept SEPARATE -- folding a character's history into its identity (what
  I did) is exactly the design that fails to generalize. So the honest verdict: entity-CONTENT does not feed
  prediction (measured null, literature-consistent); entity-ROLE might, but that is a SEPARATE organ
  (verb->role->typical-next-argument / event-schema), NOT the coreference channel this problem composes, and
  it would need role/schema tagging on literary text that is not more available than what I tested. This is a
  next-organ direction, not a fix to this composition -- and it does NOT change the SOLVED verdict.
- **THE DISSOCIATION IS NEURALLY SUPPORTED -- but the ACTIVE-HARM direction is a "diagnose-before-building"
  flag.** Item-specific episodic binding (hippocampal/MTL) and generalized schema/verb-driven expectation
  (mPFC, cortex, cerebellar forward models) are treated as at least partly separable systems (Preston &
  Eichenbaum 2013; Gilboa & Marlatte 2017; Knowlton & Squire double dissociation), and there is DIRECT patient
  evidence matching my pattern: hippocampal amnesia impairs "who/what" retrieval while SPARING online
  anticipatory prediction (Brown-Schmidt/Duff-lab 2020). So "linking helps retrieval, not anticipation" is
  reasonable. CAVEAT (honest): the literature does NOT cleanly predict that CORRECT entity info should ACTIVELY
  HURT prediction (Barron/Auksztulewicz/Friston 2020 argue retrieval and prediction are two MODES of the SAME
  hippocampal machinery). The best-supported account of active harm is CUE-OVERLOAD / retrieval-interference:
  adding an uninformative entity cue to an already-at-chance predictor dilutes it. My measurement is consistent
  with that (I ADD the entity cosine to the gist cosine; a noisy cue can only dilute a chance-level signal), so
  I now frame the harm as CUE-DILUTION of a null signal, not a strong "novelty" claim -- and note that a
  gated/precision-weighted combination (not naive addition) is the fix if one ever wanted entity info in the
  predictor. This does not change the verdict (linking does not HELP prediction, robustly), only the mechanism
  of the small negative.
- **THE FAN EFFECT IS PINNED, and the faithful fix is SPARSIFICATION, not a pointer.** DG does sparse
  conjunctive expansion recoding (~1-5% active, k-WTA) and CA3 does attractor pattern-completion (Marr 1971;
  O'Reilly & McClelland 1994; Norman & O'Reilly 2003 -- which EXPLICITLY names "cue overload and fan effects"
  and states pattern separation reduces the SLOPE of interference, does not eliminate it). My dense-bundle
  register is architecturally in the hippocampal/dense-superposition family, so its measured degradation-with-N
  is the expected fan. IMPORTANT CORRECTION to my proposed fix: an index/POINTER alone fixes only cross-entity
  lookup, NOT within-register superposition crosstalk -- a "dense bundle + pointer" would STILL fan. The
  faithful redesign is sparse conjunctive encoding at EACH event + attractor retrieval; after sparsification the
  residual degradation should track item-SIMILARITY, not item-COUNT.
- **GRADED-BINDING IS THE BRAIN-CORRECT SHAPE, and my three-way ordering nails an INTERIOR optimum.** Divisive
  normalization (Carandini & Heeger 2012 -- the canonical cortical computation) is `resp_i = a_i^n / (sigma^n +
  sum_j a_j^n)`, whose exponent n nests my exact three arms: n->0 = UNIFORM, n~1 = GRADED, n->inf = HARD
  ARGMAX. My result -- GRADED beats BOTH uniform AND argmax -- is precisely an INTERIOR-n optimum, which is
  what normalization theory predicts the brain uses. Luce's choice axiom is formally continuous with softmax
  and is the standard account of MEMORY-RETRIEVAL competition (SAM); cue-based parsing (Lewis & Vasishth 2005)
  pins PARALLEL multi-candidate activation (not serial, not instant commit); the Nref is real, replicated
  evidence of a graded ambiguity-maintenance cost. PINNED: the competitive, activation-proportional SHAPE.
  NOT pinned: the exact functional form (softmax vs another monotonic competitive function) and the temperature
  -- correctly left as a fitted choice (there is no biological constant to import). Confidence ~0.65.
- **ACT-R-vs-RECENCY null is likely a DILUTION ARTIFACT (Hobbs' easy-majority), and I TESTED it.** The drill's
  single most actionable step: most pronouns are trivially unambiguous (Hobbs 1978: >50% single-candidate;
  modern hard-pronoun benchmarks crater SOTA from ~90% to ~53%), so the ACT-R content term earns its keep only
  on the hard minority, and a whole-document aggregate is dominated by easy cases where recency and ACT-R
  agree. I RAN the stratification (arm-independent difficulty = # gender/number-compatible prior GOLD entities
  at the pronoun; easy=1 / med=2 / hard=3+) -- and the result is HONESTLY INCONCLUSIVE for a nameable reason:
  the proxy SATURATED. 9,006 of 9,078 pronoun queries landed in the "3+ competitors" bucket (easy=1 n=25,
  med=2 n=47) -- long LitBank documents accumulate many entities and gender is often unknown (so
  gender/number-compat is True by default), so the candidate-count proxy CANNOT isolate an easy majority on
  literary narrative. Within the dominant 3+ bucket ACT-R edges recency +0.0133, but that is the SAME magnitude
  as the overall +0.0129 and its "separation" is an artifact of the less-conservative ITEM bootstrap vs the
  doc-clustered overall test, NOT a difficulty effect. So the dilution hypothesis is NEITHER confirmed nor
  refuted; the honest verdict stays "ACT-R ~ recency downstream (doc-clustered NOT separated)". The follow-up
  is a cleaner difficulty proxy (referential distance, or gender-DISTINCT competitors requiring KNOWN gender).
  I resolved this by TESTING rather than leaving a bare deflation -- and report the test as inconclusive.

## KEY REALIZATIONS (the enabling moves)

- **The bar's two admissible tasks are NOT interchangeable -- and measuring BOTH is the whole result.** The
  cheap read would have been "who-did-what improves, bar met, done." Running the PREDICTION task too turned a
  one-sided win into a DISSOCIATION: linking buys retrieval, not anticipation. The dissociation is the
  finding, and it only appeared because I refused to stop at the first green readout.
- **My first prediction arm was the known-LOSING arm in disguise.** Entity-state-ALONE scoring is exactly the
  "replace the gist" arm that LOST in `the_situation_model...`. Recognizing that forced the faithful AUGMENT
  arm (gist++entity) -- and the negative SURVIVED it (and oracle linking), which is what makes it rigorous
  rather than a strawman.
- **The string-identity floor is ~0 on pronouns BY CONSTRUCTION, so the twin -- not the floor -- is the real
  test.** A pronoun shares no tokens with a name, so string-identity must orphan it; ACT-R beating it is
  near-structural. The load-bearing, non-tautological comparison is ACT-R vs the shuffled-link twin (correct
  binding vs random binding), which is CI-separated.
- **The drill's demand -- "measure the fan effect before proposing the pattern-separation fix" -- was the
  right discipline.** The dense bundle DOES degrade with entity event-count (0.695 -> 0.608), so the
  pattern-separated store is now an evidence-backed proposal, not an aesthetic one.
- **Turning an ERP signature into a mechanism produced a real win.** The Nref (hold candidates open under
  ambiguity) is usually cited as a cost; implemented as GRADED activation-weighted binding it BEATS hard
  argmax on the downstream recall -- the deepening cron's exact purpose (find the faithful mechanism the
  convenient one skipped).

## What I did NOT establish (and would withdraw first if wrong)

- **FIRST TO WITHDRAW: the who-did-what "win over string-identity" is partly structural.** String-identity
  is ~0 on pronoun events by construction, so ACT-R beating it is near-guaranteed once ACT-R recovers ANY
  pronoun event. The honest, non-structural results are ACT-R > shuffled-twin (+0.073) and ACT-R vs recency
  (NOT separated). If pressed, I stand on "correct binding beats random binding CI-separated," not on the
  raw string-identity margin.
- **ACT-R does not clearly beat RECENCY downstream (NOT separated).** So the specific ACT-R *form* is not
  shown to earn its place at the composition level -- only "salience-linking beats no-linking" is.
- **The absolute recovery is LOW (0.174 vs oracle 0.618).** The composition compounds an imperfect binder
  with an imperfect (fan-limited) decode; I did not disentangle how much of the 28%-of-oracle is binder error
  vs decode error (a stratified analysis is the next step).
- **The PREDICTION negative is scoped to next-OBJECT prediction on LitBank at the 12-dim grounded space.** It
  is NOT a claim that entity-conditioned prediction is impossible -- the same channel WON on QA-SRL
  (`the_situation_model...`, +0.0846). The signal is corpus/representation-specific; a richer space or a
  verb-thematic-fit (not object-recurrence) predictor might recover it. I did not test those.
- **spaCy roles/verbs/objects are a stand-in for the substrate's own incremental parser.** Parse errors are
  unaudited; they affect all arms equally but cap the absolute numbers.
- **The graded-binding win is confirmed at full scale WITH the control AND a temperature sweep** (SOFT peaks
  0.2084 at temp~2.0 > HARD 0.1783 > UNIF 0.1322; interior optimum, SOFT>UNIF at every temp). Nothing left to
  withdraw here except that the peak temperature (~2.0) is corpus-specific, as the literature says it must be
  (no biological constant); the SHAPE (intermediate activation-weighted competition wins) is what is pinned.

## PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, Q111)

The composition is a wire-and-measure of organs already queued/landed; the diff is about HOW to wire them:
1. **Wire the salience binder + coref threads into the entity register for a "who-did-what" readout, but
   expect ATTRIBUTION value, not prediction value.** Correct pronoun linking makes an entity's event history
   retrievable (+0.115 on pronoun queries); it does NOT improve next-argument prediction (measured null) --
   so wire it to serve retrieval/QA-style "what did X do", not as a predictive prior on running narrative.
2. **Use GRADED (activation-weighted) binding, not hard argmax, when candidates are competitive.** The
   Nref-faithful soft update beat hard argmax on the downstream recall (SOFT 0.2051 > HARD 0.1783, +0.027
   CI-sep, 100-doc), AND a uniform-weight control confirmed the ACTIVATION weighting is essential (UNIF 0.1322
   is WORSE than hard). A temperature sweep confirms an interior optimum (peak temp~2.0; both hard-argmax and
   uniform are worse), so wire a SOFTMAX(activation/temp) with temp a swept hyperparameter (~2.0 on LitBank).
   Cheap: a softmax over the existing ACT-R activations + a weighted register write. This is the one
   accuracy-relevant change and it is brain-motivated.
3. **Replace the dense-bundle register with SPARSIFIED (DG-style) conjunctive encoding + attractor (CA3-style)
   completion -- NOT merely an index/pointer.** The fan effect is measured (oracle decode 0.695 -> 0.608 with
   event-count). The finest-resolution drill sharpened the fix: an index/pointer alone fixes cross-entity
   lookup but NOT within-register superposition crosstalk -- a "dense bundle + pointer" would STILL fan
   (Norman & O'Reilly 2003 explicitly names fan effects; pattern separation reduces the SLOPE, not to zero).
   The faithful redesign is sparse conjunctive encoding at EACH event (~1-5% active, k-WTA, DG-style expansion)
   + attractor pattern-completion retrieval (CA3-style); after sparsification residual degradation should
   track item-SIMILARITY, not item-COUNT. Keep the bundle as a gist. This aligns with the standing audit's
   dense->sparse deviation and makes it a specific store design.
4. **Do NOT add an entity-conditioned PREDICTIVE prior for running narrative from this composition** (measured
   null; object-recurrence is anti-predictive on literary text). Keep the content-addressable prediction
   channel for corpora/tasks where recurrence exists (QA-SRL), not as a general reading prior.
5. Keep pronoun BINDING salience-based (per the established dissociation); content-addressable retrieval is
   the STORE-ACCESS / prediction channel, not the pronoun pick.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- coreference/binding + situation-model entries)

1. **COMPOSITION MEASURED END-TO-END: correct pronoun linking buys cross-sentence ATTRIBUTION, not
   PREDICTION -- a dissociation.** Salience-bound linking recovers who-did-what CI-separated over
   string-identity (+0.115 pronoun) with the shuffled-link twin losing (+0.073), but does NOT improve
   anticipatory next-argument prediction (entity augment of the gist HURTS -0.219; correct vs string-identity
   -0.099; even oracle -0.131). Record: the value of coreference for the situation model is retrievability of
   the entity's event history, not a predictive prior -- on running narrative at the current representation.
2. **Step 2 (pronoun -> REACTIVATES the entity's stored representation) is PINNED by direct neural evidence**
   (Dijksterhuis et al. 2024 Science single-unit; Ding/ten Oever/Martin 2023 MEG). **Step 3 (reinstatement ->
   improves prediction) is UNTESTED in humans and here measures NULL for object prediction** -- the loop does
   not auto-close. Record both, and cite the composition as the computational test of Step 3.
3. **The situation-model register's dense bundle is CONFIRMED to fan (decode 0.695 -> 0.608 with entity
   event-count).** Upgrade the standing dense->sparse deviation from "suspected" to "measured on running
   narrative"; the faithful fix is a pattern-separated per-entity trace store (gist kept as a bundle).
4. **GRADED / competitive binding (Nref-faithful) BEATS hard argmax downstream, and the ACTIVATION weighting
   is essential** (SOFT 0.2051 > HARD 0.1783, +0.027 CI-sep; UNIF 0.1322 < HARD -> uniform hedging HURTS;
   100-doc). This is an INTERIOR-optimum of the DIVISIVE-NORMALIZATION family (Carandini & Heeger 2012:
   `a^n/(sigma^n+sum a^n)` nests uniform n->0 / graded n~1 / argmax n->inf; graded beating both = interior n,
   the canonical cortical computation), continuous with Luce's-axiom/softmax memory-retrieval competition and
   the parallel multi-candidate activation of cue-based parsing (Lewis & Vasishth 2005). Record: mis-binding
   under ambiguity is a graded, activation-WEIGHTED multi-entity update (Nref / divisive normalization), not a
   silent wrong-commit and not uniform spreading; the SHAPE is pinned, the temperature is a fitted parameter
   (no biological constant).
6. **PREDICTION is ENTITY-AGNOSTIC generalized event knowledge (schema + verb-thematic-fit), NOT entity-content
   -- so coreference feeds RETRIEVAL, not anticipation.** Record the dissociation as neurally supported
   (Preston & Eichenbaum 2013; Knowlton & Squire double dissociation; Brown-Schmidt/Duff 2020 -- hippocampal
   amnesia spares online prediction) with the honest caveat that the ACTIVE-HARM direction is cue-overload, not
   a deep fact (Barron/Friston 2020: retrieval & prediction are two modes of one machinery). The entity's
   contribution to prediction, if any, is its current SCHEMA-ROLE (a separate organ), not its content history.
5. **PROHIBITION recorded: the composition is a computational-level decomposition (salience selects ->
   content reinstates -> content conditions the readout), NOT a strict serial two-stage brain architecture**
   (Kehler & Rohde; ACT-R additive activation; McKoon & Ratcliff resonance argue joint scoring).

---

## TLDR
We joined the two halves of character-tracking on real novels: figuring out who "he/she/they" means, and
using each character's memory. Correctly resolving pronouns (instead of only matching identical names) clearly
helps you answer "who did what back in that scene" -- the information is otherwise thrown away, and a version
that links pronouns to a *random* compatible character does much worse, so it's the *correct* link that
matters. But correctly resolving pronouns does NOT help *predict* what a character does next -- on novels,
characters act on new things, so their past gives no usable hint, and this stays true even with perfect
linking. So the payoff of pronoun resolution, measured end-to-end, is keeping each character's history
reachable, not anticipating the future. Two bonus findings from pushing on brain-faithfulness: (a) our
character-memory blurs as a character accumulates many events (a known "fan" limit), pointing to a better
storage design; and (b) when the reader is unsure who a pronoun means, spreading the guess across the likely
characters (as the brain does, per its "hold candidates open" signature) beats forcing a single choice --
and it actually improves the results.

## QUESTIONS
None. One judgement call for the owner at integration: the who-did-what win over the *string-identity* floor
is partly structural (a pronoun can never match a name), so I lean on the non-structural controls -- correct
binding beats *random* binding CI-separated, and graded beats hard. If you weight "beats string-identity"
lightly, the honest one-liner is "correct linking makes an entity's pronoun-contributed history retrievable
(the shuffled-link twin can't), but the expensive ACT-R form doesn't clearly beat simple recency downstream,
and it buys attribution not prediction."

## NEXT STEPS
1. **Land the GRADED (activation-weighted) binding** as the pronoun write into the entity register (the one
   accuracy-relevant, brain-motivated change; +0.028 CI-sep). Do NOT land a predictive prior from this
   composition.
2. **Replace the dense register bundle with a pattern-separated per-entity trace store** (fan effect measured);
   re-measure the who-did-what ceiling for high-activity protagonists.
3. **Stratify the oracle->ACT-R gap** into binder error vs decode error, to say which half to fix first.
4. **Re-test prediction on a recurrence-bearing task** (verb-thematic-fit, or a corpus with entity-object
   recurrence) before concluding pronoun linking never helps prediction -- the negative is scoped to
   next-object on literary narrative at the 12-dim space.
5. **Wire the composed who-did-what readout to a QA-style "what did X do" probe on the live reader**, where
   retrieval (not prediction) is the job it is now shown to serve.

---

## INTEGRATED_BY_STRATEGY (2026-08-27)

**Grade: EXCELLENT.** Re-verified FIRST-HAND (strategy ran `verification/test_entity_tracking_end_to_end.py` -> 7/7 PASS,
183s, scaffold-free on the real `hdlab.situation_model_accumulate` register; did not trust the headline). Bar MET on
cross-sentence who-did-what (ACT-R > string-identity CI-sep; info-free shuffled-link twin LOSES +0.0731 CI-sep). The
argument was adversarially audited and holds: the string-identity margin is partly structural (flagged by the solver
itself), the load-bearing non-structural controls (ACT-R > shuffled-twin; graded > hard) are CI-separated, ACT-R ~ recency
downstream is reported against self (NOT separated), and the dilution test is reported inconclusive (proxy saturated), not
spun. The DISSOCIATION (attribution yes, prediction no -- even with oracle linking) is the real finding and is neurally
supported. The GRADED-binding deepening win (divisive-normalization interior optimum; uniform hedging hurts) is a genuine
brain-motivated accuracy gain. Fan effect MEASURED, backing the dense->sparse deviation.

**hdlab:** NO file landed (Q111 honored). This is p2 of the 3 in-flight problems that gate the CONSOLIDATION PHASE; per
the consolidation policy the entity-line landing is QUEUED proven-ready (final-form spec now settled): a GRADED
activation-weighted softmax pronoun-write into the entity register (temp a swept hyperparameter ~2.0; NOT hard argmax; NOT
a predictive prior; keep salience-based binding). The sparse per-entity trace store (DG-style k-WTA encode + CA3 attractor
completion, NOT a pointer) is an evidence-backed BUILD proposal, not a landed fix -- it aligns with the standing
dense->sparse deviation and is a consolidation/store-design target. review: + review_text: + SOLVER REVIEW written to
PROBLEM.md; priority cleared; AUDIT UPDATE folded into BRAIN_FOUNDATIONAL_AUDIT.md §2b. Committed (no push).

**Consolidation status:** 1 of 3 in-flight now integrated (this one). NO successor packaged (consolidation policy: let the
queue drain). Trigger for the consolidation = the other two (`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment`,
`the_reader_has_no_conceptual_meaning_channel`) reaching owner_verdict: DONE.
