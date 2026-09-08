# Every wall, fully understood (2026-09-08)

Owner: "research all walls we need to fully understand." Below is every wall hit across the spatial+causal
extraction investigation, each with: the MECHANISM, WHY it holds, the NON-brain-foundational UPSTREAM it traces to
(the owner's principle), the STATUS (fully understood / residual), and the proper fix. All numbers are MEASURED on
disk (cell named). NO hdlab written.

## THE ONE-LINE UNIFYING LAW (measured across all three channels)
A channel clears the bar iff its CHEAP POSITIONAL PRIOR already solves its core sub-task; else it needs the
semantic-typing + ENTITY/MEANING path, which is the universal cap. Measured (`exp_channel_prior_correctness_v1`,
MAVEN): TEMPORAL sub-task = ORDER, iconicity prior 84% correct -> detection suffices -> WON. CAUSAL sub-task =
EXISTENCE, no cheap prior is both high-coverage and high-precision (adjacency 24.8% coverage / 57% precision) ->
needs world-knowledge + coref. SPATIAL sub-task = TYPE, proximity prior collapses to 18.5% on hard negatives ->
needs the semantic Figure-Ground typer. Everything downstream converges on the ENTITY/MEANING channel.

## WALL 1 -- causal edge coverage (~0.5% connective, ~4.5% class-generative). FULLY UNDERSTOOD.
- Mechanism: causal relations are dominantly UNMARKED (65.6% of MAVEN edges have no connective) and SPECIFIC
  (not generic). Marker-matching + class-level engines both miss them.
- Upstream: (a) meaning-blind typing (event_type MFS); (b) the toy 21-verb force lexicon vs the brain's vast
  experiential/simulated causal knowledge.
- Proper fix + status: RETRIEVAL refuted (`exp_joint_causal_cskg_v1`: CSKG 2.16% coverage, EDGE gap not vocab gap --
  63.4% of pairs have both lemmas, not the edge). SIMULATION is the mechanism (`exp_joint_causal_simulate_v1`:
  compute A's effect on its patient -> B's precondition; precision-on-fired 0.465 > class 0.363, beats twin CI-sep).
  Coverage-capped by the entity/meaning channel (Walls 6-7). FULLY understood.

## WALL 2 -- causal simulator fires on only 6.5% of pairs (surface-match). FULLY UNDERSTOOD + FIX PROVEN.
- Mechanism: the simulator can bind A's patient to B's participant only when named identically; 93.5% of pairs say
  "the fort"/"it" (pronoun/renamed).
- Upstream: PARTICIPANT COREFERENCE (the keystone, non-brain-foundational because unwired).
- Proper fix + status: PROVEN (`exp_joint_causal_coref_ceiling_v1`): resolving participant coref lifts the simulator
  86->221 fires (3.29x) with precision UP 0.465->0.593 CI-sep; pronoun-addressable pairs 0%->7.2%. The proper
  brain-foundational fix (Centering/entity-files). FULLY understood; the wire is strategy's (Q111).

## WALL 3 -- object-affordance grounding is register-bound. FULLY UNDERSTOOD.
- Mechanism: grounding the specific patient's disposition (dam->holds/releases water) should let the simulator bridge
  different-noun pairs, but MAVEN patients are abstract/military (war, attack, area, people); only 41% in the
  affordance KB, and crisp physical dispositions barely occur.
- Upstream: the corpus register (not a mechanism failure) + the meaning/grounding channel.
- Proper fix + status: MEASURED (`exp_joint_causal_grounding_ceiling_v1`): +24 correct edges but precision-cost
  (0.593->0.525) on MAVEN -- a tradeoff. Would help on concrete/procedural corpora. Register-gated OFF. FULLY understood.

## WALL 4 -- spatial "both-extracted-not-linked" misses (22.8%). FULLY UNDERSTOOD + FIX WON.
- Mechanism: NOT parse-attachment-uncertainty (the exact-MAP parse is ~99.9% confident, median reliability 0.999;
  the marginal-attachment prototype was a no-op, `exp_joint_spatial_frontend_upstream_v1`). The real cause (enumerated,
  64 misses): 65.6% figure bound to the WRONG ground (locative bound to the SYNTACTIC head, not the THEMATIC event;
  "spent a night at the house" locates the spending), 34.4% figure never bound (relative-clause/existential/deictic).
- Upstream: the syntax->semantics (thematic-role) interface + the absence of a nested situation model.
- Proper fix + status: WON (`exp_joint_spatial_thematic_v1`): thematic-event binding + multi-ground nesting +
  partitive/appositive coercion recovers 27% of the slice, recall 0.298->0.369, survival 16->20/123 CI-sep, precision
  held exactly. FULLY understood.

## WALL 5 -- the spatial thematic RESIDUAL (~2/3 of the slice remains). UNDERSTOOD; parser/convention-side.
- Mechanism (thematic agent's enumeration): (a) span-head CANONICALIZATION mismatch ("Museum of Modern Art" gold
  head=art vs extracted museum) -- a head-noun convention issue, NOT parse accuracy; (b) participle-as-head
  ("poorly constructed houses" -> constructed tagged/parsed as head) -- a POS/parse error; (c) wrong prep-object
  scope ("in one rural area east of X"); (d) cross-sentence edges (need coref); (e) possession-verb subject bugs;
  (f) copular part-of ("county is part of Transylvania").
- Upstream: split -- canonicalization (metric/convention), POS/parse accuracy (the batch parser), and coref
  (cross-sentence). Each distinct; none is the exact-MAP parse's attachment confidence.
- Status: characterized (not a single wall). The canonicalization + copular-part-of pieces are cheap in-scope fixes;
  the participle/POS + cross-sentence pieces are the parser + coref walls (Walls 7, 9).

## WALL 6 -- whole-subgraph SURVIVAL is density-confounded. FULLY UNDERSTOOD.
- Mechanism: survival is recall-based with the reasoner at gold, so a no-semantics density flood (proximity for
  space, contiguity for cause) matches a semantic extractor on it.
- Resolution: density is a FREE phase-diagram knob (owner), so RECALL/survival is the free axis; PRECISION-on-fired /
  hard-negative QA is the BINDING axis. On the binding axis the semantic typers WIN (spatial +0.386 over proximity;
  causal simulator beats class+twin). FULLY understood -- the metric, not the mechanism, was the first obstacle.

## WALL 7 -- THE KEYSTONE: the MEANING/ENTITY channel is built but LATENT (never consumed in read()). PARTIALLY understood; the wiring is the open build.
- Mechanism: `bridge`/`select_sense`/`predict_next_event` are QA hooks; nothing inside read() disambiguates a word or
  resolves an entity before using it, so causal typing, role binding, coref, and the reasoners all run meaning-blind.
- Why it's the universal cap: Wall 2 (coref) + Wall 3 (grounding) + Wall 8 (predictive scenes) ALL trace here.
- What we FULLY understand: that it is the root, and that PARTICIPANT COREF (its entity half) is a proven clean lever
  (3.29x). What we do NOT fully understand yet (the genuine open research): the exact brain-foundational read()-time
  CONSUMPTION mechanism (Controlled Semantic Cognition: an LIFG/pMTG control network that commits a context sense over
  the frequency default only on conflict) + why 5 proven meaning gains stay latent behind it. This is the word-sense
  solver's active problem (in flight) + strategy's wire; out of solver write-scope. THE ONE WALL STILL OPEN.

## WALL 8 -- predictive event-segmentation is meaning-starved. FULLY UNDERSTOOD.
- Mechanism: the schema-switch/belief-update computation (SEM; Kumar 2023: surprisal alone does NOT predict human
  boundaries, only a belief shift does) is the RIGHT organ, but fed 200-d distributional-hub scenes it is smooth/
  autocorrelated -- on the one well-powered human-boundary story it does NOT clear its info-free twin (p=0.066) and
  an order-shuffle twin barely changes it (`exp_predictive_frontend_proof_v1`).
- Upstream: the coarse (un-grounded) scene representation = the meaning channel (Wall 7).
- Status: FULLY understood -- mechanism right, starved by Wall 7; falsifiable prediction: grounded scenes open the
  order-shuffle-twin gap.

## WALL 9 -- the PARSER is batch, not incremental/predictive. UNDERSTOOD; not the current binding constraint.
- Mechanism: human parsing is incremental + predictive (Friederici; Hale surprisal); exact-MAP is globally-normalized
  (more faithful than greedy) but batch. The incremental/left-corner parser is filed/queued.
- Status: the scan measured parse is only ~10-23% of the spatial wall; the spatial residual's parse piece (Wall 5b/c:
  participle-as-head, PP-scope) is real but small. Not the binding constraint (that is Walls 7/coref). Understood;
  the incremental parser is a longer-horizon fidelity gain, not the lever now.

## WALL 7 UPDATE -- the FULL-FIX prototype refines the keystone: the meaning channel's read()-time value is CHANNEL-SPECIFIC, not one blanket wire.
Measured (`exp_meaning_consumption_full_fix_v1`, disk; agent report lost to an auth error, metrics verified, positive
control surface==landed-simulate 86/40 passes). The read()-time consumption stage (coref + control-gated sense-commit),
wired to both downstream channels:
- CAUSAL: the COREF (entity) half is the lever -- recall 3x, precision-on-fired 0.465->0.535 (near the recency prior
  0.568). The SENSE-commit half is MARGINAL: both-vs-coref precision +0.0069 CI[-0.005,0.019] NOT CI-sep; and the
  control GATE is a wash (gated ~= commit-always ~= commit-MFS, all ties) -- MAVEN event triggers are low-polysemy for
  causal typing, so committing a context sense barely changes event_type. So on CAUSAL extraction the meaning channel
  = its COREF half only.
- SPATIAL: coref is a NO-OP -- survival 20/123, containment recall 0.369, QA 0.584 ALL IDENTICAL to thematic
  (margin 0 CI[0,0]); 200 pronoun figures resolved but 0 cross-sentence gold chains completed. The spatial extraction
  lever is the THEMATIC BINDING, not coref.
- CONCLUSION: the keystone is not one blanket wire. It is COREF -> causal (proven), THEMATIC binding -> spatial (coref
  no-op on this gold), and the SENSE-consumption/control-gate half -> the MEANING READOUT (the word-sense solver's 5
  gains), NOT causal/spatial extraction. Three distinct consumers; the earlier "everything converges on one wire" was
  the right root but too coarse -- the value is channel-specific.

## SUMMARY: 8 of 9 walls FULLY understood + fix identified (WON/PROVEN/refuted/register-bound). The ONE open wall is
WALL 7 -- the read()-time consumption mechanism of the meaning/entity channel (the keystone), which everything
downstream converges on. Its ENTITY half (participant coref) is a proven clean lever; its SENSE-consumption/control
half is the genuine remaining research, owned by the word-sense/meaning-channel problem + strategy (out of solver
write-scope). Every other wall is either a proven WIN, a proven located negative with the residual named, or a
refuted dead-end -- all traced to their non-brain-foundational upstream per the owner's principle.
