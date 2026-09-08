---
problem: report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure
status: PARTIAL
bar: "LIVE common-noun RESOLUTION accuracy beats the live floor CI-separated on MODERN gold (GUM), reported with a doc-level paired-bootstrap CI. The info-free twin (bridge fires to a RANDOM type-compatible antecedent) LOSES CI-separated. NO regress: pronoun and named-antecedent (kb) consumers byte-identical or up. A rigorous NEGATIVE is a full pass (e.g. 'the live path's same-head binding already captures the nominal view, so the re-port ties -- subsumption, located and counted')."
result: "The brief's mechanism (re-port the two levers onto hdlab.commonnoun_binder) is REFUTED on the live path, and the real cause is LOCATED. On the DEPLOYED binder mention-schema + binding, per-mention common-noun RESOLUTION accuracy = 0.4904 (GUM modern TEST, n=2855 anaphoric common-noun mentions, metric = resolved-referent nominal-dominant gold eid == mention eid) -- BELOW same-head string-identity 0.5412 (delta -0.0508, CI[-0.0739,-0.0308]), REPLICATING the URG defect (0.4879) on the actual deployed binding. Re-porting the levers: de-pollution is a NO-OP (the binder clusters only non-pronoun mentions, so its dominants are already nominal -- subsumption, confirmed); the NON-WRITING type bridge, GENERALIZED past the binder's person-gate, is a real lever (0.5201, +0.0298 over base CI[+0.0234,+0.0372], twin LOSES +0.0210 CI[+0.0157,+0.0270], person-gate removal is +0.0235 CI[+0.0180,+0.0295] of the gain) -- but it only reaches PARITY with string-identity (delta -0.0210, CI[-0.0458,+0.0008] includes 0), NOT a CI-separated beat. The DEFICIT is the binder's BINDING, isolated: the URG/typed-coref resolution binding on the SAME live schema scores 0.5485, +0.0581 over the deployed binder CI[+0.0454,+0.0695]; and the COMMITTED hdlab.typed_coref organ BEATS string-identity +0.0259 CI[+0.0134,+0.0385] CI-sep on this exact population and beats the deployed binder +0.0767 CI[+0.0547,+0.0995]. The FULL fix ported onto the EXACT live dict-mention SCHEMA (typed_coref_liveschema_resolve: 3-view de-pollution + generalized non-writing bridge w/ appos/copula + name-token + typed-spokes seeds) = 0.5664, BEATS string-identity +0.0252 CI[+0.0126,+0.0375] CI-sep, recovers the organ (0.5671), beats the deployed binder +0.0760 CI-sep, beats the reduced port +0.0179 CI-sep (the seeds close the gap), twin loses +0.0256 CI-sep -- so the fix is proven on the exact schema the wire consumes, not just the population. So the live common-noun RESOLUTION consumer should be served by the typed_coref binding, NOT the LitBank-clustering binder; the live CI-separated win is achievable + PROVEN on the live schema, but requires a Q111 hdlab wire + a new resolution instrument-arm, not a re-port of levers onto the binder."
floor: "Strongest floor actually run on the SAME n=2855 GUM-TEST anaphoric common-noun population: same-head STRING-IDENTITY keyed by the GUM gold lemma = 0.5412 (POSITIVE CONTROL: identical to the URG board floor 0.5412 -- confirms the dict-schema scorer reproduces the board instrument). Binder's own-lemmatizer string-identity = 0.5156. Deployed binder = 0.4904 (below both). typed_coref organ = 0.5671 (beats the floor CI-sep)."
controls: "(1) POSITIVE CONTROL: dict-schema string-identity == URG board floor 0.5412 exactly (population + scorer match). (2) FAITHFULNESS: the resolve mirror (bridge=off) is BYTE-IDENTICAL to hdlab.commonnoun_binder.situation_predict on all 137 test docs (9065 labels) -> the measured binder_base IS the deployed binder. (3) NO-REGRESS BY CONSTRUCTION: the non-writing bridge arms produce byte-identical CLUSTER LABELS to base -> sm.entities + the separate reader pronoun stream are byte-unchanged (the WRITING type-license changes labels, which is exactly why p11 measured a pronoun drag -0.0172). (4) INFO-FREE TWIN (bridge fires but resolves to a RANDOM gn-compatible prior referent) LOSES CI-sep under BOTH the binder binding (+0.0210) and the URG binding (+0.0259) -> the type signal is load-bearing, not 'any reach'. (5) NAME no-regress: generalized bridge vs base +0.0024 CI[+0.0008,+0.0045] (improves, not a regress). (6) p11 WRITING type-license is a wash-to-negative on resolution (+0.0021 CI incl 0). (7) De-pollution SUBSUMED: the binder never writes pronouns to its referents, so nominal-dominant == full-dominant by construction (measured no-op). (8) OOD GENERALIZATION (GENTLE, out-of-domain, n=275): the defect + fix replicate (binder 0.5273 < floor 0.5709; fix 0.5964, +0.0255 = the GUM +0.0252) -- direction+magnitude, underpowered for CI-sep."
files_changed: "experiments/exp_commonnoun_binder_live_report_v1.py, verification/test_commonnoun_binder_live_report.py, data/exp_commonnoun_binder_live_report_v1/metrics.json, notes/problems/report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure/SOLVED.md, notes/problems/report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure/BRAIN_FOUNDATIONAL_ANALYSIS_2026-09-08.md. NO hdlab/ writes (Q111 -- proposed wire stated in section 6). Reuses data/corpora/gum/ (pinned V12.1.0, on disk) + hdlab.{commonnoun_binder,typed_coref,typed_spokes,coref,event_centrality_coref} + experiments.{gum_coref,exp_unified_referent_gum_v1}."
reverify: ".venv/Scripts/python.exe verification/test_commonnoun_binder_live_report.py    # 19/19 (+ W1 faithfulness + W2 no-regress asserted inline; incl W10 full-fix-on-live-schema, W12 OOD-GENTLE, W13 world-knowledge-headroom oracle, W14 encyclopedic-route prototype, W15 reasoning-route located-negative, W16 occupation-KB reconciliation on the honest de-leaked floor); recomputes every headline from source on the full GUM modern TEST"
---

# PARTIAL -- the levers do NOT survive a re-port onto the DEPLOYED binder; the deficit is the binder's BINDING, and the committed typed_coref organ is the fix

**STATUS: PARTIAL** (solver scope; FINALIZED per strategy 2026-09-08 -- WIP until the owner marks DONE). Glass-box, NO
external LLM at inference (THE invariant). NO `hdlab/` written -- the mechanism + the fix are proved in `experiments/` +
`verification/`; the Q111 wire is proposed in section 6.

> ### STRATEGY RULING 2026-09-08 -- de-leak + handoffs (folded in)
> - **DE-LEAK CONFIRMED (this measurement is already honest).** Strategy ruled the reader's GOLD-coref inheritance (the
>   `_apply_commonnoun_gate` peek that yields the ~0.80-0.86 reader numbers) is a LEAK. **My pipeline does NOT use it:**
>   the resolver decides from head-match / type comparator / gn / recency; `gold_eid` is used ONLY for SCORING and the
>   anaphoric-population definition (`is_ana`) -- never in a resolution decision (the one exception, the `bridge_oracle`
>   arm, is explicitly a CEILING). So all my numbers (0.49-0.58) ARE the honest de-leaked floor, NOT the leaked path.
> - **HANDOFF 1 -> `replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering`:** my honest-floor
>   binder measurement (deployed binder = 0.4904 on per-mention resolution WITHOUT the gold-inheritance gate) + the
>   two-part diff (typed_coref binding is the fix; the deployed binder's binding is the deficit) feed that problem. I do
>   NOT build the de-leaked binder here.
> - **HANDOFF 2 -> `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual`:** the encyclopedic-route
>   prototype + the diagnosis feed that problem. RECONCILIATION (strategy flagged the occupation-KB axis as a located
>   negative): my COARSE person-typing (person-name -> person-CATEGORY anaphor) is +0.0102 CI-sep on the HONEST floor and
>   its anaphor-type match beats a person-REACH control +0.0053 CI-sep (witness W16) -- so it is a REAL type constraint,
>   DISTINCT from the specific occupation-KB (name->exact-occupation, coverage-bounded = the located negative). Per
>   strategy, do NOT reuse the specific occupation-KB axis in that wire; my coarse-person-typing data is for that
>   problem's solver to reconcile, not this problem's headline.
> - **The typed-coref diagnosis (deficit = the binder's binding; typed_coref = the fix; type comparator half-wired to
>   is-a only) is accepted and feeds the new problems.** This problem is finalized.

The brief asked me to re-port the two brain-faithful levers (typed NOMINAL de-pollution; a NON-WRITING type bridge) onto
the live `hdlab.commonnoun_binder` path and prove the live common-noun RESOLUTION lifts CI-separated. I did the re-port
faithfully, and it does NOT lift CI-separated -- it reaches parity. Following the disk instead of the brief, I then
located WHY, and the answer changes the recommended wire.

## The result (GUM modern TEST, odd docs, n=2855 anaphoric common-noun mentions; metric = resolved-referent nominal-dominant gold eid == mention eid; identical population + scorer to the URG board instrument)

| arm | resolution acc | vs string-identity 0.5412 |
|---|---|---|
| **string-identity (board lemma) -- FLOOR** | **0.5412** | -- (== URG board floor: positive control) |
| string-identity (binder's own lemmatizer) | 0.5156 | -0.0256 |
| **deployed binder (commonnoun_binder, the LIVE path)** | **0.4904** | **-0.0508 CI[-0.0739,-0.0308] (BELOW -- replicates the URG defect 0.4879)** |
| binder + p11 WRITING type-license | 0.4925 | wash over base (+0.0021 CI incl 0); p11 also drags pronoun -0.0172 |
| binder + NON-WRITING bridge, PERSON-scoped (faithful re-port) | 0.4967 | -0.0445 |
| **binder + NON-WRITING bridge, GENERALIZED to all nouns** | **0.5201** | **-0.0210 CI[-0.0458,+0.0008] -> PARITY, NOT a beat** |
| binder + generalized bridge, info-free TWIN | 0.4991 | (type signal destroyed -> loses to the generalized bridge +0.0210 CI-sep) |
| URG binding on the SAME live schema, no bridge | 0.5173 | -0.0239 |
| URG binding on the SAME live schema + generalized bridge (REDUCED port) | 0.5485 | +0.0074 CI[-0.0147,+0.0271] (parity); +0.0581 over the deployed binder CI-sep |
| **FULL fix on the EXACT live dict SCHEMA (typed_coref_liveschema)** | **0.5664** | **+0.0252 CI[+0.0126,+0.0375] CI-SEP (BEATS); +0.0179 over the reduced port CI-sep (the appos/name seeds); twin loses +0.0256 CI-sep** |
| **committed hdlab.typed_coref organ (Doc schema; the fix)** | **0.5671** | **+0.0259 CI[+0.0134,+0.0385] CI-SEP (BEATS); +0.0767 over the deployed binder CI-sep** |
| **fix + ENCYCLOPEDIC route (WordNet instance-of + PERSON-typing; offline)** | **0.5765** | **+0.0354 over floor CI-sep; +0.0102 over the fix CI[+0.0054,+0.0157] CI-sep; twin loses +0.0326** (strong = DBpedia C8, sibling +0.0955 name-slice) |
| fix + REASONING route (situation-model role-fit; agentive nominalization) | 0.5678 | +0.0014 over the fix CI[0.0,+0.0032] **NOT CI-sep = LOCATED NEGATIVE** (only ~6/2855 role-resolvable; re-recognition is knowledge-bound, not local-role-bound) |
| **fix + ALL brain-foundational routes (taxonomic+encyclopedic+role-fit)** | **0.5769** | **+0.0105 over the fix CI[+0.0057,+0.0160] CI-sep; +0.0357 over floor** (encyclopedic-dominated) |
| _ORACLE type comparator (perfect world knowledge; CEILING)_ | _0.7492_ | _+0.2081 CI[+0.1847,+0.2344] over floor; +0.1828 over the fix -> the world-knowledge headroom (upper bound: includes inference-only + noisy pairs)_ |

**NAME no-regress:** generalized bridge vs base +0.0024 (improves). **De-pollution:** structurally SUBSUMED (no-op).

## 0. How the brain does this (PINNED vs OUR-INVENTION) -- and where the deployed organ deviates
- **PINNED (Ariel 1990 Accessibility).** A definite common noun is CONTENT/TYPE-addressed: it retrieves the
  type-identified antecedent, and a referent's IDENTITY is anchored on its naming/nominal descriptions (not on transient
  pronoun pointers). The typed de-pollution + type bridge levers implement this.
- **PINNED (Nieuwland Nref hold-under-uncertainty).** A low-confidence type bridge resolves the current reference for
  comprehension but does NOT commit the merge -- the non-writing bridge.
- **PINNED (type-compatibility is domain-general).** The brain bridges "the vehicle" -> "a car" for OBJECTS, not only
  for persons. There is no person-specific coref-resolution circuit.
- **OUR-INVENTION in the DEPLOYED binder (the deviation this problem exposes).** `commonnoun_binder.situation_predict`
  was promoted from a LitBank CHARACTER-clustering win; it carries three cluster-F1-oriented mechanisms that are
  OUR-INVENTIONS, not the brain's resolution operation: (a) a PERSON-GATE (`person_synset is None` -> pure head-grouping,
  and the type_license branch lives INSIDE the person branch); (b) MODIFIER-SPLIT ("the old man" != "the young man"); (c)
  an EVENT-CENTRALITY situation gate for >=2 same-head candidates. On modern GUM per-mention RESOLUTION these HURT
  (binder 0.4904 vs the URG binding 0.5485 on the identical schema).

## 1. What I built
`experiments/exp_commonnoun_binder_live_report_v1.py`:
- **A GUM -> binder-dict-schema loader** (`doc_to_binder_mentions`): builds the exact `is_pronoun/midx/sent_idx/
  sent_role_rank/span_toks/head/gender/name_gender/number` stream the deployed binder consumes, from a `gum_coref.Doc`,
  carrying the gold eid + gold lemma for scoring. Identical construction across all arms (fair).
- **A byte-faithful mirror of the deployed binder** (`situation_predict_resolve`) that (i) tracks gold eids per referent
  and emits per-mention RESOLUTION results scored INCREMENTALLY exactly like the URG board instrument, and (ii) adds the
  two levers: `bridge in {off,write,nowrite}` and `bridge_scope in {person,all}`. **Faithfulness is proven**: with the
  levers off it produces labels BYTE-IDENTICAL to `hdlab.commonnoun_binder.situation_predict` on all 137 test docs (9065
  labels). The non-writing arms produce byte-identical labels to base (no-regress by construction).
- **The URG/typed-coref resolution binding on the SAME live schema** (`urg_binding_resolve`): hard-gn + most-recent
  same-head + generalized non-writing bridge, dropping the binder's person-gate / modifier-split / situation-gate. This
  isolates the binding as the variable.
- **The committed organ arm**: runs `hdlab.typed_coref.TypedCorefResolver(bridge=True, bridge_write=False,
  type_comparator="typed_spokes")` on the same GUM population -- the resolution binding that SHOULD carry the live
  consumer.
- **The FULL fix ported onto the EXACT live dict SCHEMA** (`typed_coref_liveschema_resolve`): the full typed_coref
  logic -- routes by GUM gold mtype like the organ, 3-view card with NOMINAL de-pollution (pronouns write the full card
  only), generalized (NO person-gate) non-writing type bridge seeded by `coref_type_license` + in-text appos/copula
  is-a (from the Doc parse, which the live reader supplies) + name-token containment, ACT-R salience selector -- on the
  reader's mention-dict stream. This is the drop-in reference for the Q111 wire; it recovers the organ (0.5664 vs
  0.5671) and beats string-identity CI-sep on the exact schema the wire consumes.
Scored with the URG doc-level paired bootstrap (`exp_unified_referent_gum_v1._paired_boot`), floor recomputed on the
same n=2855 population.

## 2. What I measured (and what it means)
1. **The premise is real on the LIVE path.** The deployed binder trails string-identity by -0.051 CI-sep-below (0.4904
   vs 0.5412) -- the same defect the URG proxy showed (0.4879), now confirmed on the ACTUAL deployed binding.
2. **The brief's mechanism is REFUTED.** Re-porting the levers onto the binder does not beat string-identity. De-pollution
   is a NO-OP (the binder never writes pronouns to its referents, so its dominants are already nominal -- the exact
   "subsumption, located and counted" the brief flags as a valid negative). The generalized non-writing bridge is a real,
   twin-controlled lever (+0.0298 over base CI-sep, twin loses CI-sep), and removing the binder's PERSON-GATE is the
   load-bearing part of it (+0.0235 CI-sep) -- but the sum reaches only PARITY with string-identity (0.5201, CI includes
   0), because the binder's binding starts ~0.05 below the floor and the bridge cannot make up the whole gap.
3. **The deficit is the BINDING, isolated.** The URG resolution binding on the SAME live schema is +0.0581 over the
   deployed binder CI-sep (0.5485 vs 0.4904); the committed typed_coref organ is +0.0767 over it CI-sep and BEATS
   string-identity +0.0259 CI-sep (0.5671). So the schema is fine and the levers are right -- the binder's cluster-F1
   binding (person-gate + modifier-split + situation-gate) is the wall.
4. **The right wire is not "levers onto the binder"; it is "swap the resolution consumer to the typed_coref binding".**
   The binder is the correct organ for the CLUSTERING consumer (`sm.entities`, cluster-F1 on LitBank characters); the
   typed_coref organ is the correct one for per-mention RESOLUTION (what downstream binding needs). They serve different
   consumers and should not be conflated.

## 3. Controls (all clean; witness 12/12)
- POSITIVE CONTROL: dict-schema string-identity == URG board floor 0.5412 exactly (n=2855) -> the scorer/population match.
- FAITHFULNESS: resolve(bridge=off) byte-identical to the hdlab binder on 9065 labels -> binder_base IS the deployed path.
- NO-REGRESS BY CONSTRUCTION: non-writing arms byte-identical labels -> sm.entities + pronoun stream byte-unchanged.
- TWIN LOSES CI-sep under both bindings -> the type signal is load-bearing.
- NAME no-regress (+0.0024, improves). p11 WRITING type-license is a wash-to-negative on resolution (its live cost is the
  pronoun drag p11 already measured, because it changes cluster labels).

## 4. What I did NOT establish / would withdraw first
- **I did NOT produce a CI-separated LIVE win via the re-port the brief specified.** That is the honest headline and the
  first thing to withdraw if a reviewer requires the win to come from the binder itself: it does not.
- **The live CI-separated win (organ, 0.5671) is measured on the live POPULATION + schema, but is not yet WIRED into the
  reader.** The reader currently has NO scored common-noun RESOLUTION dimension -- it scores pronoun coref (`coref_acc`)
  and clusters entities (`sm.entities`); the common-noun gate is default OFF and only changes `sm.entities`. So this win
  is board-invisible today; realizing it needs a Q111 hdlab wire + a new resolution instrument-arm (section 6). If a
  reviewer requires a moved LIVE board dim, that clause is unmet until those two land.
- **The reduced vs full port is now RESOLVED, not a caveat.** `urg_binding_resolve` (0.5485) is a reduced port (skips
  the appos/copula + name-token bridge seeds) and only reaches parity; the FULL port `typed_coref_liveschema_resolve`
  (0.5664, +0.0179 over the reduced port CI-sep) BEATS string-identity CI-sep on the EXACT live dict schema and recovers
  the organ. So the win is proven on the live schema, not only on the Doc/population -- the earlier "reduced port" caveat
  is closed.
- **OOD robustness (GENTLE, out-of-domain vs GUM, n=275 anaphoric common):** the defect + the fix GENERALIZE off GUM --
  the deployed binder trails string-identity (0.5273 vs 0.5709) and the full live-schema fix beats it (0.5964, +0.0255
  over the floor, matching the GUM effect +0.0252 almost exactly). The CI includes 0 (n=275 is underpowered: only 26
  GENTLE docs), so this is a DIRECTION+MAGNITUDE replication, honestly NOT a CI-separated OOD claim. **No parameters
  tuned on TEST** (structural levers).

## 5. Performance vs the brain + full-stack upstream (owner's directive)
- **Where we lose signal, itemized:** a competent reader resolves the different-head slice ("the company"->Google) with
  world knowledge; the deployed binder loses signal at THREE OUR-INVENTION binding choices before that even matters --
  the person-gate (excludes the bridge on objects, ~half the different-head slice), modifier-split (splits correct
  same-head merges on GUM), and the event-centrality tie-break (a LitBank-scene heuristic). Each is a fidelity gap vs the
  brain's content/recency-addressed definite resolution.
- **WHERE WE LOSE THE MOST SIGNAL, QUANTIFIED (oracle type comparator, witness W13):** with a PERFECT type comparator
  (bridge licenses iff gold-coreferent = perfect encyclopedic/taxonomic/scenario knowledge, SAME bridge structure), the
  live-schema fix would score 0.7492 -- +0.2081 over string-identity CI[+0.1847,+0.2344] and +0.1828 over our
  WordNet-seeded fix CI[+0.1625,+0.2059]. So the type comparator is the DOMINANT lever, and ~88% of the achievable
  headroom (0.183 of 0.208) is WORLD KNOWLEDGE the WordNet(C5) comparator misses. The comparator's OPERATION is
  brain-foundational (content-addressed different-head retrieval from the ATL semantic hub -- the oracle uses the
  identical structure); the KNOWLEDGE BASE is the gap. The missing knowledge is (a) ENCYCLOPEDIC instance-of
  ("Google"->company, "Argentina"->country) and (b) SCHEMA/SCENARIO associative anaphora ("restaurant"->"the waiter";
  Sanford-Garrod). The residual to ~1.0 above 0.749 is anaphors with no antecedent-linkable prior (first-mention
  definites, bridging inference, split/plural antecedents) -- genuine situation-model inference, not antecedent-linking.
- **The encyclopedic KB is BUILT and brain-foundational but NOT WIRED (and its asset is unshipped here).** `hdlab.typed_spokes`
  carries the C8 DIRECTED ENTITY-TYPE SPOKE (DBpedia InstanceOf 2022.12.01: `entity_type_lemmas`/`type_licenses`/
  `available_entity_type`) -- the ATL's encyclopedic route, a static offline asset (invariant-safe, no inference LLM). The
  sibling problem `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` already measured the two-route
  (KB UNION in-text is-a, a CLS design) name-bridge lift at +0.0955 CI-sep on the name-bridge slice. BUT `typed_coref`
  imports only `coref_type_license` (C5/WordNet) -- it does NOT use the C8 encyclopedic route, and `data/frontend_assets/`
  is empty in this working copy (the 548MB asset is gitignored / not rebuilt), so `available_entity_type()` abstains here.
  So the type comparator upstream of the resolution bridge is a brain-foundational component that is HALF-WIRED (taxonomic
  route only) -- exactly the "a brain-foundational lever underperforms because an upstream component is not fully wired /
  present" pattern.
- **Upstream mention/parse is clean on GUM:** the mention detector = gold, the POS/parse = gold -- not the bottleneck
  here. The non-brain-foundational components are (i) the deployed binder's BINDING (person-gate + modifier-split +
  event-centrality, LitBank-clustering OUR-INVENTIONS applied to resolution -- fixed by the typed_coref binding) and
  (ii) the type comparator's INCOMPLETE KNOWLEDGE (WordNet only, missing the encyclopedic + schema routes).
- **No downstream consumer regresses** from the proposed direction: the binder stays exactly as-is for the clustering
  (`sm.entities`) consumer; the resolution stream is ADDITIVE (a new consumer), and the non-writing bridge is
  byte-identical in clustering.

## 6. Proposed hdlab WIRE (Q111 -- strategy lands; solver does not write hdlab/)
The recommendation is NOT the brief's (do not add the levers to `commonnoun_binder` -- measured parity, not a win). It is:
1. **Serve the reader's common-noun RESOLUTION consumer from `hdlab.typed_coref.TypedCorefResolver`
   (`bridge=True, bridge_write=False, type_comparator="typed_spokes"`), NOT `commonnoun_binder`.** Port `resolve_doc` onto
   the reader's dict-mention stream (the FULL port: process pronouns writing to the full card only for salience/gender +
   the nominal de-pollution; seed the bridge with `coref_type_license` + apposition/copula is-a + name-token containment;
   generalized to ALL common nouns -- no person-gate). **Drop-in reference:
   `experiments/exp_commonnoun_binder_live_report_v1.typed_coref_liveschema_resolve` -- the FULL port already runs on the
   reader's dict-mention schema and scores 0.5664 (+0.0252 over string-identity CI-sep, recovering the organ 0.5671).**
   The `commonnoun_binder`-based `urg_binding_resolve` is the reduced proof that the binding swap alone is +0.0581 over
   the binder CI-sep. Keep `commonnoun_binder` for the CLUSTERING (`sm.entities`) consumer -- do not change it.
2. **Add a scored common-noun RESOLUTION instrument-arm to the reader** (`board_commonnoun_resolution_dimension`) reusing
   this cell's metric (resolved-referent nominal-dominant gold eid == mention eid) on GUM, so the win is board-VISIBLE.
   Today the reader has no such dim (a "board-invisible proven win needs its own instrument-arm").
3. **Per no-more-default-off:** the resolution stream is ADDITIVE (new consumer; clustering byte-identical), so it can be
   ON by default -- it does not touch `coref_acc` or `sm.entities`. Do NOT flip the binder's WRITING `type_license`
   (p11: -0.0196 + pronoun drag). If a downstream consumer (affect experiencer / goal binding) is switched to READ the
   per-mention resolution stream, measure that consumer's own metric before flipping it (impact-analyse per no-more-default-off).

## 7. AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, E3 coreference / common-noun)
- **`hdlab.commonnoun_binder` is a cluster-F1 organ, NOT a resolution organ, and it is person-gated.** On modern-GUM
  per-mention common-noun RESOLUTION it scores 0.4904, BELOW string-identity 0.5412 and BELOW the URG binding 0.5485 on
  the identical schema (delta +0.0581 CI-sep). Its person-gate + modifier-split + event-centrality tie-break are
  LitBank-character OUR-INVENTIONS that hurt resolution. Mark the binder OUR-INVENTION-for-clustering; it should not be
  the substrate for the resolution consumer.
- **The person-gate specifically is non-brain-foundational for coref** (the brain type-bridges objects). Removing it
  (generalizing the bridge to all common nouns) is a measured +0.0235 CI-sep lever even inside the binder.
- **The typed_coref organ (URG binding) is confirmed the brain-foundational RESOLUTION path** -- it BEATS string-identity
  +0.0259 CI-sep on the live GUM population; the prior E3 note stands, now with the live-path caveat that the DEPLOYED
  binder is a different (clustering) organ and does not carry this win.

## KEY REALIZATIONS (the enabling moves)
- **Read the DEPLOYED organ, not the proxy.** The whole result turned on noticing that the live `commonnoun_binder` is a
  person-gated LitBank CLUSTER-F1 former with a completely different binding than the URG proxy the win was proven on --
  so "re-port the levers" was the wrong frame; the binding itself was the untested variable.
- **Isolate the binding by holding the schema fixed.** Running the URG binding AND the deployed binder on the identical
  dict-mention stream (+0.0581 CI-sep) is what proved the deficit is the binding, not the schema or the levers -- the
  single measurement that redirected the recommendation.
- **A byte-identity faithfulness assert makes "no-regress" free.** Because the non-writing arms reproduce the deployed
  binder's labels exactly, the pronoun/entity no-regress is by construction, not by a fragile separate measurement -- and
  it also cleanly explains p11's pronoun drag (the WRITING version changes labels; the non-writing one cannot).
- **De-pollution was subsumed for a STRUCTURAL reason, not a null result.** The binder never admits pronouns to its
  referents, so there is no pollution to remove -- the lever is a no-op here by construction, which is a located finding,
  not a failed experiment.
- **An oracle with a PERFECT comparator, then DECOMPOSED, separates knowledge from inference.** The +0.18 oracle
  headroom looked like "just add a KB", but decomposing it by antecedent type showed ~73% is discourse multi-description
  + parse noise (situation-model inference, not a lookup) -- which is why the reasoning route is a located negative HERE
  and re-recognition is KNOWLEDGE-bound, not local-reasoning-bound. The ceiling number alone would have mis-directed the
  next build; the decomposition is what made it honest.
- **Verify the de-leak on your OWN code, not by assertion.** Strategy flagged gold-coref inheritance as a leak; rather
  than assume, I traced every `gold_eid` use and confirmed it touches only SCORING + the anaphoric-population definition,
  never a resolution decision -- so my numbers are the honest floor, not the leaked 0.80-0.86. The check is what let the
  result stand under the ruling.
- **A "located negative elsewhere" is not automatically your result -- isolate the mechanism.** Strategy flagged the
  occupation-KB axis as a located negative; a control (person-name licenses ANY anaphor = "reach", vs requiring a
  person-CATEGORY anaphor = "type") showed the anaphor-type match is load-bearing +0.0053 CI-sep -- so COARSE
  person-typing is a real, distinct mechanism from the coverage-bounded SPECIFIC occupation-KB. Reconcile, do not
  conflate.

## TLDR (plain English)
We had already taught a stand-in scorer to recognise a thing by a plain noun ("the vehicle" = the car mentioned earlier)
better than a dumb same-word rule. This job was to move that fix into the reader's REAL machinery and check it still wins.
It does not -- and the reason is important: the reader's real machinery for this is a tool built for grouping CHARACTERS
in old novels, and that tool is actually WORSE than the dumb same-word rule at the recognise-per-mention job on modern
text (it scores about 49 right per 100 vs the rule's 54). Bolting our two fixes onto it only brings it up to a TIE with
the rule, not a win -- one fix does nothing here (it fixes a contamination this tool never had), and the other helps only
once we remove a needless restriction the tool has (it only bridges people, never objects). The real fix is not to patch
that tool: it is to use the RIGHT tool we already built (the typed resolver), which on the reader's own data scores 57 per
100 and beats the dumb rule cleanly. So: the specific plan in the brief is refuted, we found and proved the correct
alternative, and it needs a wiring step (owned by the other session) plus a new scoreboard line to make the gain visible.

## QUESTIONS
None blocking; FINALIZED per strategy 2026-09-08. Status stays PARTIAL (solver scope): the brief's specific re-port is
refuted, but the underlying goal (a brain-foundational live common-noun resolution that beats the dumb rule) is achieved
+ measured on the HONEST de-leaked floor via the typed_coref binding, and the diagnosis feeds the two new posted problems
(the de-leaked binder replacement; the world-knowledge name-bridge residual). Nothing awaited from me.

## NEXT STEPS (priority-ordered; strategy owns any hdlab landing, Q111)

> ### FLAGGED HIGH-PRIORITY FOLLOW-ON PROBLEM (the knowledge gap -- owner-directed 2026-09-08)
> **The dominant remaining lever is the ENTITY-TYPE / WORLD-KNOWLEDGE KB, and its assets are absent in this working copy.**
> The type comparator's OPERATION is brain-foundational but its KNOWLEDGE is incomplete: (1) the STRONG encyclopedic
> route -- the built-but-unshipped C8 DBpedia entity-type spoke (`hdlab.typed_spokes.type_licenses`; sibling-proven
> +0.0955 CI-sep on the name slice) -- needs its OFFLINE DBpedia dump rebuilt (a naive live-API acquisition was tried +
> refuted: ~65% API-fail + noisy surfaces); (2) the SCHEMA/associative route needs a ConceptNet slice (API down / assets
> absent), which would ALSO restore the DEGRADED taxonomic part-whole route (WordNet-only in this copy). Oracle-measured
> total headroom above the current fix is +0.18 (though ~73% of that is discourse multi-description = the generative
> world-model program, not a KB). **Recommend filing as a HIGH-PRIORITY sibling: "rebuild + wire the entity-type/world-
> knowledge KB (DBpedia C8 + ConceptNet) into the resolution bridge".** It is the single biggest brain-fidelity + accuracy
> lever left on this chain; it is static-offline + invariant-safe; and the mechanism to consume it is already prototyped
> here (`encyc=True` arm). See BRAIN_FOUNDATIONAL_ANALYSIS_2026-09-08.md sec 2b/2d.

### A. INTEGRATE INTO THE LIVE READER (this problem; strategy lands the hdlab edit, Q111)
1. **HIGH -- wire the RESOLUTION consumer to `hdlab.typed_coref`, NOT `commonnoun_binder` (section 6.1).** Port
   `resolve_doc` onto the reader's dict-mention stream (full port: pronoun-stream de-pollution + appos/copula + name-token
   seeds + generalized bridge). Drop-in ref: `typed_coref_liveschema_resolve` (0.5664 on the live schema, +0.0252 over
   string-identity CI-sep). Keep `commonnoun_binder` for the CLUSTERING (`sm.entities`) consumer -- unchanged.
2. **HIGH -- add the `board_commonnoun_resolution` instrument-arm (section 6.2)** so the win is board-visible; the reader
   scores no common-noun resolution dim today. Additive/read-only -> can be ON by default (no-regress by construction).

### B. HANDED OFF to the two new posted problems (strategy ruling 2026-09-08; do NOT solve here)
3. **-> `replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering`:** my HONEST de-leaked floor
   (deployed binder 0.4904 on per-mention resolution, no gold-inheritance) + the two-part diff (typed_coref binding = the
   fix; the binder's binding = the deficit) are the handoff. Strategy lands the de-leaked binder.
4. **-> `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual` (the FLAGGED high-priority lever above):**
   the ENCYCLOPEDIC-route prototype (WordNet instance-of + coarse person-typing, +0.0102 CI-sep on the honest floor,
   twin loses; strong version = DBpedia C8 offline dump, sibling +0.0955) + the SCHEMA route (blocked on ConceptNet
   acquisition) + the RECONCILIATION (coarse person-typing is a REAL type constraint, W16, DISTINCT from the specific
   occupation-KB located-negative -- do NOT reuse that axis) are the handoff. The dominant residual is situation-model
   INFERENCE = the generative-world-model program, not a KB.

### C. DO NOT REDO (measured, on the honest floor)
- p11 WRITING type-license (wash on resolution + pronoun drag); de-pollution on the binder (no-op by construction);
  the person-scoped bridge alone (the person-gate is the ceiling); adding the levers to `commonnoun_binder` as the
  resolution fix (measured parity, not a win -- the binding is the deficit); the situation-model ROLE-FIT reasoning route
  for THIS task (located negative, +0.0014 not-sep, ~6/2855 addressable -- re-recognition is knowledge-bound); the
  specific occupation-KB axis in the world-knowledge wire (strategy: located negative). MEDIUM/optional: de-restrict the
  binder's person-gate for its CLUSTERING consumer (+0.0235 CI-sep inside the binder) -- a separate `sm.entities` follow-on.

## INTEGRATED_BY_STRATEGY (2026-09-08) -- EXCELLENT
Reverified 19/19 first-hand. LANDED (Q111): a per-mention common-noun RESOLUTION consumer served by `hdlab.typed_coref` (`sm.commonnoun_resolution`, additive/default-on, clustering byte-identical) + the C8 encyclopedic route into the type comparator (live 0.5394->0.5482, +0.0326 CI-sep over the fair floor) + a board arm `board_commonnoun_resolution_dimension` (`0349d0dd1`, `27b3dc64e`; witness `test_commonnoun_resolution_wire.py` 5/5). AUDIT UPDATE folded (binder = cluster-F1 not resolution + person-gated; typed_coref = the BF resolution path). Full inventory = ledger CONT-26 + audit S2b. status:INTEGRATED, priority dropped.
