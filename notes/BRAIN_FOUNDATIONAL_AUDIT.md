# BRAIN-FOUNDATIONAL AUDIT — the whole substrate against the brain it reconstructs

**updated: 2026-08-26** · living document, edit in place · **THE single reconciled map of substrate-vs-brain.**
Reconciles the three prior audits onto one list: `ORGAN_MAP.md` (38 organs, per-organ brain-math, 08-22),
`component_brain_fidelity_ledger.md` (14 components, 07-30), `LONG_TERM_PLAN.md` §4 (phases, 08-16). Where
they disagree, this file is the current view and names what went stale.

**Provenance / honesty scope:** the per-organ fidelity verdicts below are carried from `ORGAN_MAP.md` (read in
full 2026-08-26), not independently re-derived this pass; the whole-brain coverage is from a full read of all
155 `hdlab/*.py` docstrings. Treat verdicts as "as-audited," re-verify before acting on any single one. Numbers
are as-quoted from their source cells and do not cross scorers/populations.

---

## 1. THE HEADLINE (plain language)

We mapped 38 "organs" the brain uses to read, mean, remember and reason, plus the systems around them.

- **Only 5 of 38 organs compute the brain's actual equation.** For **12** neuroscience has written down the
  equation, so "build the brain's version" is even a well-posed instruction; for **14** the core operation is a
  mystery *even in neuroscience*, so we are inventing (honestly labelled) — including **our single most central
  operation, binding**. **7 organs began this session absent in code; several were built this session** (the N400
  coherence monitor; the feature-similarity meaning read-out; the additive content-addressable retrieval organ — see §2b).
- **~54% of the code is unreachable** from any live entry point — built-but-unwired islands.
- **🧠 THE CONVERGENCE (the load-bearing insight from this session's integrations): ONE brain operation is the answer
  almost everywhere we looked — additive, cue-based, content-addressable RETRIEVAL (Lewis & Vasishth 2005).** It is the
  fix for binding (E1), the consolidated-memory read (E2), coreference (E3), the fan effect (context reinstatement = one
  more cue feature), AND — newly — reversible-sentence PARSING (filler-gap role binding = "retrieve the filler from a
  partial cue"; the discrete rule is its noise→0 limit). Five problems that looked unrelated are ONE operation reused.
  **This is why the retrieval organs were built RETRIEVAL-FIRST.**
- **🧭 BUT THE COMPOSITION WAS MEASURED END-TO-END (2026-08-26, §2b) AND IT RE-POINTS THE PROGRAMME: the binding
  constraint is the FRONT-END (event/role extraction), NOT the memory/retrieval stages.** Composed into a real reading
  task, the organs work perfectly on CLEAN inputs (event 1.000) but the whole reader scores BELOW a trivial "always say
  agent" floor end-to-end — every downstream organ is swamped by a front-end that mislabels who-did-what-to-whom
  (misassignment-dominant). A brain-faithful verb-argument front-end recovers most of it (0.48→0.74 CI-sep). So the
  retrieval convergence is REAL (the organs are the right operation, validated on clean inputs + partial on meaning cues)
  but its live payoff is FRONT-END-GATED. **The next lever is the front-end (verb-argument role assignment), not more
  downstream organs — and the learned organ for it already exists, islanded (`thematic_role_labeler.py`).**
- **The single biggest MEMORY defect (real, but downstream of the front-end): we ask every question of the WRONG memory**
  — the fast episodic "sketchpad," never the consolidated long-term store (read path is exact-key, no partial-cue
  retrieval). *(The once-co-headline `sign()` "averaging machine" defect was REFUTED this session; it survives only as a
  binding-site guardrail. And FHRR binding is now CONFIRMED faithful — a published model, SEM/Franklin 2020 — see §5 #1.)*
- **The systems we DO build well are lopsided toward reading:** coreference, goals/reward, valence, and
  metacognition are richly built; **Theory of Mind is absent, dedicated meaning-selection (semantic control) is
  thin, and the speaking side is essentially one file.** This substrate is a reader, not a speaker.
- **Corrected this pass:** the 07-30 ledger called coreference and discourse "ABSENT." That is **stale** — both
  are now substantially built. And the meaning step is **no longer "empty" (see §7):** on a fair test it beats
  frequency; it is unwired, not absent.

---

## 2. HOW THIS DOC IS USED (it is a living, shared reference)

- **Every solver brief references this file.** A solver reads the entry for the system it is touching before it
  starts, so it inherits the brain frame and the known deviation instead of re-deriving it.
- **Solvers report deviations/updates they find.** If, during the work, a solver discovers the fidelity verdict
  here is wrong, stale, or incomplete — or finds a new deviation — **that goes in the submission** (a short
  "AUDIT UPDATE" note), and **the strategy session incorporates it here at integration.** The audit improves as
  the work proceeds; it is not frozen.
- **Marking convention:** each entry carries the brain structure, whether the brain's equation is **PINNED**
  (neuroscience fixes it) or **UNPINNED/CONTESTED** (we are inventing — an OUR-INVENTION-UNDER-TEST, not a
  replication), our organ (or ABSENT), a fidelity verdict, and the specific gap/deviation.

---

## 2b. AUDIT UPDATES (from integrated solver work + strategy fidelity extensions — newest first)

- **2026-09-03 (INTEGRATION — the reader's who-did-what CANDIDATE SOURCE is a deployment ceiling: it reads candidates from the CoRef column (gold patient present only 0.82) instead of opening a discourse referent for EVERY NP; referent-per-NP lifts effective end-to-end 0.4698→0.8054. EXCELLENT, owner-DONE).** Problem `open_a_discourse_referent_for_every_np_not_just_coref_mentions` (the P5 I filed; a solver solved it), reverified **10/10** first-hand. Measured THROUGH the live `SituationReader().read()` (only the mention SOURCE swapped, everything else identical), scorer pick==gold_head, abstention=wrong, 25 real LitBank docs. NEW PINNED-AND-MEASURED: comprehension INTRODUCES a discourse referent for EVERY NP head (Kamp 1981 DRT / Heim 1982 FCS; MTL concept cells + hippocampal indexing; open-broad-then-revise, Van Berkum Nref) and coreference is a DOWNSTREAM linking pass, NOT the candidate source — the discrete referent struct is a defensible OUR-INVENTION (no dedicated neural file-opener attested, Nieuwland 2019). Wiring referent-per-NP as the live source: honest cleaned-DO instrument (n=149) **0.4698→0.8054, +0.3356 CI[+0.262,+0.416]** (over null); full noisy population (n=1354, ~76% oblique-contaminated) +0.0473 CI-sep; candidate-coverage lever reproduced 0.8183→0.9705 (+0.1521); WHO-HAS-WHAT theme coverage +0.1151. CONTROLS (decisive): the info-free twin (matched-count random-position referents) LOSES **and ACTIVELY HURTS** vs coref (−0.13/−0.07) → the RIGHT complete NP set carries signal, not count; NO-REGRESSION (rnp reproduces the noun-supplied eval, Δ≈0); DESIGN — referent-per-NP as the SOLE source (0.805) BEATS the additive union (0.403) → REPLACE, don't ADD (the DRT order, theory + numbers agree). GENERALIZATION: introduction is register-INVARIANT (0.983 modern / 0.978 19c) where the coref LINKER is OOD on 19c (0.818) — register-sensitivity lives in the trained linker, as DRT predicts. BRAIN-COMPARISON: rnp 0.805 = 95% of the competent reader (spaCy 0.846); the IDEAL composition (referent-per-NP + frame detector + construction-aware selector) reaches 0.904–0.913 ≥ competent; shuffled-candidate twin collapses 0.235. Two adjacent caps (both routed): (a) 19c POS noun recall 0.914 — the brain-faithful FIX is a determiner/name FRAME detector (NP identified by its syntactic frame, function-word bootstrapping — Abney 1991) lifting introduction 0.914→0.931 (+0.017 CI-sep, twin loses), register-robust by construction (closed-class survives archaic prose); (b) the proximity-primary SELECTOR (the brain is thematic-fit-dominant) — and the KEY FINDING: on multi-DO the fit is CONSTRUCTIONAL (Goldberg double-object/naming +0.040/+0.146 CI-sep) NOT lexical co-occurrence (a distributional re-rank adds +0.007 n.s. over constructions), reconciling the fit-dominant literature with the parent's fenced grounded-fit negative. **WIRE LANDED (§6, default-off, witness 9/9, commit `2f8305116`): `hdlab/referent_per_np.py` (`referent_per_np_source`, BYTE-FAITHFUL to the validated `build_source('rnp')`) + a `referent_per_np` flag swapping the mention source in `read()`. ⚠️ KEPT DEFAULT-OFF (measured turn-on blocker the solver's who-did-what-only measurement missed): flipping it ON regresses `coref_acc` 0.4818→0.0200 — the source gives non-coref heads FRESH SINGLETON clusters and the "coref demoted to a LINKING pass" the DRT design assumed (merge co-referring referents into clusters) is NOT wired, so cluster-based coref collapses. The +0.336 who-did-what is real; the −0.46 coref hit gates the flip on `wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on` (FILED). A live coref-consumer re-validation is exactly what the no-default-off rule caught.** HONEST BOUNDS (solver): no hdlab edited (proved via a runtime monkeypatch of the mention source — first to withdraw if the landed wire diverges); the modern SOURCE delta is INFERRED (no modern gold-coref corpus on disk — rests on register-invariant introduction + the parent's modern selection recovery); full-population absolutes are on the known-noisy gold (lead with cleaned-DO). **Follow-ons FILED: `construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set` (P4, the READY selection successor); the register-native noun POS/NP-type-gating route folds into the existing register-robust-detection line (P6).**

- **2026-09-03 (INTEGRATION — the who-did-what front-end's 22% SILENT ABSTENTION is a recoverable OUR-INVENTION precision-gate artifact, NOT a parser gap: effective end-to-end 0.629→0.985. EXCELLENT, owner-DONE).** Problem `the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses`, reverified **65/65** first-hand. The reader picks the patient right ~98% WHEN it answers but stays SILENT on 22% of answerable clean-19c clauses; the silence is three OUR-INVENTION precision gates mis-firing on 19c prose, never "the parser could not find the noun" (the updated arc-eager parser recovers only 1/669 — abstention is not parse-quality). **THE FLOOR MOVED DURING THE WORK (a discipline exemplar): the stored `wired_pick` 0.6293 went STALE as `np_head_reduce` + `predict_revise` landed mid-flight → recomputed first-hand against the CURRENT live reader 0.7877 (predict_revise +0.0643); the structural recovery lifts it to 0.9851 (+0.1973 CI[+0.1689,+0.2272] CI-sep, info-free random-clause twin loses, no main-gold regression), now primarily an ACCURACY fix (65 of 75 remaining wrong picks) + the 47 verb_subcat + 20 no-event abstentions.** NEW PINNED (the ideal glass-box pipeline, each stage brain-pinned): referent-per-NP candidate source (Kamp 1981 DRT / Heim 1982), Davidsonian per-verb coverage (Davidson 1967), NP-head (Williams 1981 RHR / Abney 1987 DP-head), structural direct-object filter, Competition-Model role assignment (Bates & MacWhinney), animacy for ditransitive (Bresnan 2007), predictive-confidence abstain (Van Herten 2005 — flag, NEVER auto-revise). **ARCHITECTURE FINDING: ROUTING beats FLAT composition** — piling every stage on every clause MIS-FIRES (0.898 canonical); routing the focused structural rule on canonical + the full multi-cue competition only on the non-canonical residual restores 0.985 (+0.087 CI-sep) — the brain's good-enough-default + targeted-reanalysis (Ferreira; Christiansen & Chater). **LOCATED NEGATIVES:** a verb-ID heuristic/learned-combiner HARD_FAILS on 19c (recovery 0.05 at FP≤1.0 — needs a TRAINED joint-decoded parser with beam, scaffolded + characterized — filed P6); non-canonical is GATED ON THE MEANING CHANNEL not the parser (structural cues recover it 4× to 0.29 cleaned but 0.70 residual needs the generative situation model — the who-did-what patient decision is measured HEAD-INDEPENDENT, so a better parser does not move it). Honest §0h self-correction: several exploratory "parser-gated" conclusions were reinvention of landed work, corrected against the substrate map. **CLEAN WIRE OWED (§0g, default-off, RE-MEASURED on the current substrate — the floor moves): the STRUCTURAL-DO candidate filter** (restrict patient candidates to BARE post-verbal nominals, no intervening preposition, before the pick — subsumes the `verb_subcat` hard veto, recovers the 47 + intransitive precision 0.975, +0.0045 main gold) into `_read_events_wired`/the `_cands` primitive (ref impl `exp_whodidwhat_composed_pipeline_v1.composed_who_did_what`). **Follow-ons FILED: `open_a_discourse_referent_for_every_np_not_just_coref_mentions` (P5 — the biggest real-world lever, +0.15 candidate coverage, referent-per-NP) + `register_robust_event_detection...` (P6 — the trained joint predicate model). DO NOT land: the grounded-valence selection cue / any verb-ID heuristic (refuted).**

- **2026-09-03 (INTEGRATION — THE NORTH-STAR CONTINUATION: the a_s "which SPECIFIC rare sense" lever is RAISED 0.198→0.326 by the brain's BIASED-COMPETITION readout; the brief's own event/role TARGET is a rigorous located NEGATIVE; and CLEAN-FOUNDATION-BEFORE-LEARNER-ON is now a MEASURED REQUIREMENT. EXCELLENT, owner-DONE).** Problem `build_sg_lite_self_supervised_scale_generative_sense_predictor` (advancing the parent north star), reverified **12/12** first-hand (strict document-disjoint SemCor, subordinate senses, subject-weighted, n=2676; MFS 0.6831; a_s floors NB 0.198 / centroid 0.22; every net over MFS CI-sep, twins lose). **NEW PINNED-AND-MEASURED (the brain-foundational FIX): sense disambiguation is BIASED COMPETITION / controlled semantic cognition (LIFG/pMTG — Jefferies 2013; Lambon-Ralph 2017; word-level precision-weighting — Feldman-Friston), NOT context averaging.** The naive flat-context query is a TOPIC blur (~= the model mean 0.28) that cannot separate a rare sense from its topic-sharing dominant twin; weighting each context word by its DIAGNOSTICITY (spread of its cosine across the candidate glosses, max−mean) reaches a_s **0.307 (+0.0389 CI-sep [+0.019,+0.059]) on 41M-token w2v and 0.326 (APEX, +0.0430 CI-sep) on 277M** (the fix STACKS with richer embeddings), the shuffled-diagnosticity twin LOSING CI-sep (+0.0381 — the CORRECT words carry the signal); it beats the top-k key-side variant and is the most brain-faithful arm. **LOCATED NEGATIVE (refutes the brief's OWN proposed mechanism): the Sentence-Gestalt EVENT/ROLE-filler prediction TARGET does NOT raise a_s** — 4 convergent tests (frozen readout, end-to-end replacement, fusion, under the best readout; right-role NOT CI-above wrong-role; role loses to next-word), because point role-filler prediction is the WRONG SHAPE for a gloss-reconstruction readout (next-word aligns with gloss clouds; a point role-filler does not). The gestalt/event objective stays PINNED as the comprehension objective (St. John & McClelland 1990); the fidelity gap is the READOUT (role-specific selectional fit), not the target. **KNOWLEDGE is the dominant ingredient but BOUNDED + must be CLEAN:** a_s rises with corpus 8M 0.255 → 41M 0.280 → 277M 0.291 (paired CI-sep, sharp to ~40M then slow — a signpost not a wall), and gloss→rich knowledge is +0.081 CI-sep (larger than any readout tweak) — BUT ⚠️ **raw/organic growth REGRESSES a_s (−0.015, same pattern as raw `learn_from_text` co-occurrence 0.274→0.267); only CONSOLIDATED SyntagNet-quality knowledge helps (+0.025..+0.058).** So the "clean foundation before learner-on" north star is now a PINNED REQUIREMENT with numbers: uncontrolled growth is NEGATIVE, not neutral — a consolidation/quality gate must precede any learner-on. **CEILING (triangulated, 3 drills + 5 prototypes): the wall past ~0.35 glass-box is CONTEXTUAL INPUT ENCODING** (one sense-conflated vector per surface form) — a small glass-box encoder on frozen w2v cannot cross it (< the parameter-free bag), and static multi-sense embeddings are a brain-unfaithful dead-end; SOTA 0.53 needs a genuinely contextual encoder = the transformer/invariant fork (OWNER decision, presented). DO-NOT-OVERCLAIM: a_s ~0.33 is far below human (~0.6–0.7 subordinate; the 0.72 figure is OVERALL) — the residual is contextual encoding + grounding, glass-box-HARD but understood, NOT an LLM requirement. Corroborates the WSD-graph organ (a_s 0.27 < topic-w2v 0.33) and P1's readout retraction below. **WIRE LANDED (Q111): the biased-competition readout MECHANISM promoted VERBATIM (asset-independent pure numpy) → `hdlab/diagnostic_context_wsd.py`** (`diagnostic_context_scores` / `diagnosticity` / flat baseline; the caller supplies context+gloss vectors from any space); witness `test_diagnostic_context_wsd_organ.py` 7/7 (mechanism + shuffled-diag twin loses + fallback). HONEST BOUND: this BANKS the a_s-lifting mechanism; its LIVE wiring into the WSD `select_sense`/`read()` path + the on-vs-off WiC measurement (before any default-on, per the no-default-off rule) is OWED — the meaning read-out's live consumer is the same DEBT the P1 entry names. **Follow-on FILED: `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner` (the owner-flagged TOP lever).** Infra flag for the orchestrator: `tools/orchestrator/queue_add.sh` returns rc=1 for a healthy cell (the remote runner venv is healthy; the failing step is in scp/ssh/nltk-check).

- **2026-09-03 (INTEGRATION — FORWARD PREDICTION IS REPRESENTATION-BOUNDED: the ~200-d ATL hub + composed-exemplar predictor is the lever, and it IS the north-star P1's shared representation. EXCELLENT, owner-DONE).** Problem `upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub`, reverified 11/11 + no-regression first-hand. PINNED-AND-MEASURED: the reader's 12-d sensorimotor SPOKE collapses same-category role-fillers (the located representational loss); a ~200-d register-native distributional HUB (ATL hub — Lambon Ralph 2017; Patterson 2007 hub-and-spoke) + a verb-prior CENTROID base + precision-weighted agent-COMPOSED exemplar sharpening (Bicknell 2010 agent×verb; Frankland & Greene 2015 role-filler binding; Friston precision) beats the spoke **+0.076 MRR held-out (2.4x)** AND **+0.069 on the LIVE reader** (measured brain-faithfully as broad graded pre-activation, n=12,463, NOT the coarse error-flag), all three info-free twins (agent-shuffle / verb-shuffle / hub-shuffle) losing CI-sep; transfers cross-task to WiC sense discrimination **+0.027 CI-sep** (the shared representation P1 needs) + recovers the OOV coverage tail (Resnik/Clark-Weir taxonomic backoff, 88%→96%). FHRR untouched (this changes only the filler CONTENT code + composition). The COMPOSITIONAL route saturates at ~2 bound arguments (measured bounded-tuple ceiling) — the boundary that points to the generative situation-model prior (P1). **LANDED (Q111):** the ~200-d hub SHIPPED as the static foundation asset `data/frontend_assets/hub_ppmi_svd_200d.pkl` (12.5 MB, the SAME hub P1 reads) + `HubComposedPredictor` promoted to `hdlab/composed_hub_predictor.py` (byte-faithful). **Reader surprisal-predictor swap NOT defaulted (USER no-default-off rule, MEASURED reason): the +0.069 improves EventRecord surprisal METADATA consumed by no default-on scored metric, and the fitted store is 124 MB (+122 MB/process) vs the spoke's 2 MB — a 124 MB load for a dormant signal.** Realized value = P1's shared representation (shipped); the surprisal-hub is available (store rebuildable) for the abstention/coverage consumer.

- **2026-09-03 (INTEGRATION — COPULAR is-a/attribute BINDING is now a live reader dimension: "what/who is X" is answerable where the base reader gave 0/376. EXCELLENT, owner-DONE).** Problem `the_reader_has_no_copular_is_a_binding_schema`, reverified 10/10 + 6/6 first-hand. PINNED: the copula BE is a near-empty functional carrier — the meaning is the PREDICATION relation binding the complement to the subject ENTITY node (Higgins 1979; Mikkelsen 2011; Maienborn 2005 Kimian states; Bemis & Pylkkanen 2011 LATL), TYPED predicational (property/is-a) vs identificational (SYMMETRIC identity — hippocampal CA3 auto-association; Bunsey & Eichenbaum lesion abolishes backward access). CORRECTS the brief's wording: category is-a is EMERGENT FEATURE-OVERLAP in the ATL hub, NOT a hypernym hierarchy (Rogers 2004; Patterson 2007); and text-derivable is-a is RELATION EXTRACTION (Hearst "X is a Y" — the copula IS the read-time is-a edge), NOT distributional similarity (every overlap measure caps ~0.69/chance — Shwartz 2017). MEASURED: read-back recall 0.672 CI-sep +0.1685 over the most-recent-noun floor (0.503), shuffle twin loses; label-robust fix → 0.818 (identity +0.247, itself CI-sep). The residual is DETECTION (arc-labeler `cop` recall, worst on equatives), not binding (95% lossless given detection); the arc-eager tree lifts the labeled base +0.111 CI-sep. The predicational/identity NEURAL dissociation is OPEN (extrapolation; only surface-cue typing claimed, 0.969). **WIRE LANDED (Q111, default-off):** promoted `hdlab/copular_binding.py` (`extract_entity_states` + Higgins `predicted_type`, byte-faithful to the experiment) + a `bind_entity_states` flag on `SituationReader` → `sm.entity_states` (typed `EntityState`) + `sm.state_register` (predicational read-back, `state_at('ahab')=['captain']`). Witness `test_copular_is_a_binding_landing_organ.py` 5/5. OWED follow-ons (NOT this wire): is-a INHERITANCE foundation (Hearst-harvest, offline-admissible), identity→coref symmetric merge, `robust_cop` recall-max default; a register-native parser for the ~13% hardest equatives (arc-eager does not move the 19c ceiling).

- **2026-09-03 (INTEGRATION — THE PARSER/ROLE FRONT-END IS FIXED: NP-HEAD reduction lifts EVERY who-did-what consumer +0.20; a high-value repair of the DOMINANT error mode, not ceiling polish. EXCELLENT, SOLVED).** Problem `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning` (owner-DONE), reverified **45/45** first-hand. NEW PINNED-AND-MEASURED: the reader's role assigners grab the WRONG word inside a noun phrase — a compound MODIFIER ("iron gate" → iron) or a genitive POSSESSOR ("the undertaker's shop" → undertaker) — on ~1/3 of clean 19c clauses; **96% (204/212) of the LANDED assigners' who-did-what misses are exactly this NP-head error.** Reducing each candidate to its NP HEAD before the role pick (Stage A: Right-hand Head Rule for compounds — Williams 1981; DP-head for genitives — Abney 1987; bracket-closure is neurally real — Nelson 2017 ECoG / Ding 2016 / Pallier 2011) lifts patient selection to 0.9806 (+0.0628 CI-sep above its permutation null; chunk-shuffle twin ties the floor → head IDENTIFICATION carries the signal, not candidate-dropping; held-out both halves; NO modern regression, qasrl +0.128 LARGER on modern) and **lifts EVERY consumer +0.20 first-hand — resolve_patient/hybrid_role_patient 0.683→0.888, competition_pick 0.671→0.873, route_predicate_arguments(theme, end-to-end) 0.683→0.888, twins fail — the full parser-free NP-head stack is +0.35 end-to-end (live reader 0.629 → 0.981, 78%→100% coverage).** We are AT/ABOVE the 19c parse ceiling: a full modern parser (spaCy) scores 0.9297 < ours (spaCy is itself degraded on 19c), so POS/parse is NOT the lever — constituent-head identification is. The CASE cue (he/him, who/whom) is a faithfully-built REAL cue (position-neutralized 2AFC 1.00 vs 0.51) with ZERO availability on canonical-active DO gold (0/669 — objects are full nouns, not case-marked pronouns; the decisive fronted-object regime is 0.05% of sentences) — a rigorous located NEGATIVE that is the Competition Model's/eADM's OWN prediction (case = high-reliability, near-zero-availability outside pronouns), not an implementation failure. **WIRE LANDED (Q111, two sites the solver proved, one shared rule, all DEFAULT-OFF = byte-identical):** promoted `hdlab/np_head_reduce.py` (byte-exact to the validated prototypes); a `np_head_reduce` flag on the PRIMITIVES (`resolve_patient`, `hybrid_role_patient`, `competition_pick`, `route_predicate_arguments`) that ALL consumers funnel through (the +0.20), AND a `np_head_reduce` flag on `SituationReader` that fixes the reader's own POSITIONAL path (filter `noms` to NP heads → `_assign_roles` 0.7728→0.9477) + the ROUTER path (pass-through). Witnesses: `test_np_head_reduce_wire_landing_organ.py` 3/3 + reader default-off byte-identical / flag-on fires (52/104 events); registered `np_head_reduce_wire_v1`. **OWED (consequences of the fix):** (a) flipping the flag default-ON is a SEPARATE owner decision; (b) the ~20 role-output organs (bound_event_backbone, event_bundle, causation_typing, possession_operators, hd_fact_store, world_state_register, reasoner, ...) inherit the fix when a consumer enables it — RE-RUN + RE-VALIDATE anything tuned on the OLD (wrong) patient outputs; (c) the 22% coverage/abstention gap is a separate filed problem. STRATEGIC: this is the shared parser/role front-end cap under who-did-what, world-state recipient/patient, and (via the role stream) coref — the +0.20 propagates broadly.

- **2026-09-03 (INTEGRATION — THE NORTH STAR: the meaning-channel sense-selection wall is RE-LOCALIZED from the generative SOURCE (a_s) to the DECISION RULE; the net-gain see-saw is BROKEN glass-box; the "needs-an-LLM" ceiling is DEMOLISHED. EXCELLENT).** Problem `the_meaning_channel_needs_a_generative_world_knowledge_situation_model_that_predicts_the_specific_sense` (owner-DONE, PARTIAL advancing the parent), reverified **8/8** first-hand. **CORRECTS this problem's OWN parent framing (the sense-selection §2b entries below + P1's premise): the binding limit is NOT a_s (the generative source) — it is the DECISION RULE.** NEW PINNED-AND-MEASURED: reordered access is ADDITIVE, never suppressive (Duffy-Morris-Rayner) — the dominant sense is always accessed by frequency, context only ADDS activation to a subordinate; and precision is EXPECTED reliability estimated from context richness, NON-margin (Feldman-Friston — the posterior's own sharpness rewards a false-confident peak). The brain-faithful rule `score(s) = log prior(s) + gamma·reliability·relu(z(L(s)))` (additive, facilitatory-only, non-margin precision, margin only an abstention gate) NETS **+0.0124 over the MFS floor held-out CI[0.007,0.0176] CI-sep** (dominant preserved 0.950, no see-saw; shuffled-situation twin loses +0.0049 CI-sep) where the parent's gated HARD-FLIP was −0.0013 CI-sep BELOW — the see-saw was the hard-flip's dominant-erasure (c_d~1.0), not a_s. A small net over near-oracle MFS IS the brain's regime (human all-words ~0.72 vs MFS ~0.66). **a_s LOCATED NEGATIVE:** the static world-knowledge source raises a_s only ~0.27 (< the co-occurrence readout ~0.33), and the LEARNED generative predictor's exciting a_s 0.43 / net +0.052 was **cross-DOCUMENT leakage** — a strict disjoint-document foundation collapses it to a_s 0.198 / net −0.038 (scramble control confirms). **CEILING DEMOLISHED (a retraction):** the earlier "the human-level a_s residual needs inference-time reconstruction = an LLM" line is WRONG and WITHDRAWN — the ~0.4 rare-sense figure is a property of the nearest-centroid READOUT (structurally MFS-biased), not of neural sense selection; a glass-box RECONSTRUCTION-MATCH readout on a self-supervised generative gestalt gives a_s 0.280 > centroid 0.220 > overfit NB 0.198 AND generalizes (corroborated: BEM lifts rare-sense F1 37.0→52.6 at fixed model size by the same readout switch; UKB+SyntagNet, a pure glass-box graph, rivals supervised WSD; Nour-Eddine-Kuperberg's N400 model is a ~13k-unit network, not an LLM). **WIRE LANDED (Q111):** the PROVEN additive decision rule → `hdlab/semantic_control.additive_reordered_read` (byte-exact to `exp_generative_situation_sense_selector_v2._additive_pick`; default-safe, `resolve` untouched; witness 3/3; registered `semantic_control_additive_reordered_read_v1`). HONEST BOUND: this lands the generalizing lever INTO the organ; the meaning organ's LIVE wiring into `read()` is a separate DEBT-3 step (islands). The a_s lever is the OPEN north-star continuation (SG-lite self-supervised SCALE — the run is in flight — + a role-filler prediction target). No hdlab wire for the a_s negative.
  **THREE HYGIENE CORRECTIONS (surfaced by this problem's adjacent-component audit; recorded here so §2b/§3 reflect them):** (1) the 2026-08-27 coref "cue-based-activation HARD_FAILED" line is POPULATION-SPECIFIC and REVERSED on real narrative — graded ACT-R cue-based retrieval WINS there (0.775; the landed `graded_coref_pick`). (2) `predictive_reader` is NO LONGER an "inert island" — it is validated LIVE behind a default-off `predict_surprisal` flag. (3) `distributional_meaning_channel` must NOT be quoted as a general meaning read-out — it is SUBSTITUTABILITY-only (WordSim rho −0.24); do not cite it as semantic similarity.

- **2026-09-02 (INTEGRATION — TWO owner-DONE that CONVERGE on ONE wall: the "which SPECIFIC one" problem = a rich learned ORTHOGONAL individuation/meaning representation = the north-star P1; both EXCELLENT).** Reverified first-hand (composition-cleaned-gold 22/22; coherence-prior 8/8 + 4/4).
  1. **COMPOSITION-as-SELECTION is REFUTED at power; the who-did-what selection residual is 89% STRUCTURAL; composition is REAL as PREDICTION and REPRESENTATION-bounded (problem `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold`, EXCELLENT).** CORRECTS the parent's §2b entry below: the parent's +0.076 agent-composition selection margin (n=171) was SMALL-SAMPLE NOISE — the solver built the cleaned gold at scale (n=669, precision 98.5%) and it separates only 7% of the time at n=171; at power COMPOSED ties its agent-shuffle twin (+0.007 ns). NEW PINNED-AND-MEASURED (Competition Model, Bates & MacWhinney): English who-did-what is WORD-ORDER-DOMINANT — nearest-post-verbal = patient 0.918 on clean direct objects (the "+0.158 over position" beat a WEAK farthest-noun floor), the residual is 89% STRUCTURAL (NP-head chunking +0.043 CI-sep → 0.981; morphological case MEASURED ABSENT), only ~11% semantic; thematic fit changes SELECTION only at syntactic ambiguity, and the 19c gold is 100% active (0 passive) so that regime is ABSENT. The Bicknell agent×verb effect is a PREDICTION/N400 phenomenon, not a selection choice — WRONG INSTRUMENT. On the RIGHT instrument (forward prediction) composition is REAL (+0.032 MRR CI-sep) and REPRESENTATION-bounded: DEAD in the organ's 12-d grounded spoke, ALIVE in a ~200-d hub proxy; a precision-weighted composed-EXEMPLAR predictor over the hub beats `predictive_reader`'s current method +0.083 CI-sep = 2.3x held-out MRR (de-risked to a class; keep FHRR; "MORE IDEAL" Bayesian multi-cue integration is an HONEST NEGATIVE — the bottleneck is cue QUALITY = the representation, not the integration op). ABSOLUTE-UNDERSTANDING reframe: exact next-word prediction is near an intrinsic ceiling (~164 patients/verb); on the brain's graded frequency-controlled 2AFC the system is genuinely competent (verb-level fit 0.72; agent-composition +0.018 CI-sep; a multi-participant situation model +0.035 CI-sep, oblique-shuffle loses). NO hdlab wire (located negative). **BOARD INTEGRITY: the 19c who-did-what GOLD is ~76% oblique-contaminated (honest cleaned direct-object ~0.92) — caveat added to the baseline board.** Measured levers routed to two follow-ons (structural NP-head/case selection; the composed-exemplar prediction upgrade).
  2. **The COHERENCE NEXT-MENTION PRIOR is REFUTED (a near-DUPLICATE of an already-dead problem); the real fix is a LEARNED cue-INTEGRATOR bounded by the ENTITY-INDIVIDUATION REPRESENTATION (problem `who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde`, PARTIAL, EXCELLENT).** The solver CAUGHT that the coherence prior was already owner-DONE dead (2026-08-29 `the_reader_has_no_coherence_next_mention_prior`), reproduced the premise exactly, and confirmed it stays dead after entity-maintenance (do NOT land a coherence prior). NEW PINNED-AND-MEASURED: Kehler-Rohde is LEARNED cue INTEGRATION, not a prior — a glass-box LM-free conditional-softmax cue-integrator (wiring existing `phi_agreement_keep` + `situation_model_accumulate`) recovers the chain bucket 0.614→0.668 (+0.054 CI-sep, shuffled-cue twin loses), LEARNABLE WITHOUT GOLD (self-sup +0.060 ~= gold +0.063), CALIBRATED posterior (entropy AUC 0.807 → realizable defer = the brain's Nref). The score-loss drills to the ROOT: integrator 0.677, oracle 0.905; the 23% ">=1 cue right but wrong" is NOT the combiner (integration EXHAUSTED — no combiner beats the learned integrator) — the ENTITY-INDIVIDUATION representation (the 12-d individuation cue) is the wall, and sharper glass-box reps don't beat it (redundant, not orthogonal). NO hdlab wire (prior refuted; the integrator is a gold-nominal-grouping/animacy-filtered PROTOTYPE, wide CIs — an optional default-off Q111 wire, coref-quality-bound). Honest bound: realizable glass-box ceiling ~0.67 (the 0.905 oracle needs the answer to gate).
  3. **THE CONVERGENCE (the strategic headline — both solvers state it explicitly).** This coref individuation residual, the WSD sense-selection a_s residual (`wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector`), and the composition-as-PREDICTION representation bound are ONE WALL: the **"which SPECIFIC one"** problem — pick/predict the specific rare sense / the specific referent / the specific expected word — none of which a flat 12-d code or a co-occurrence graph or a coherence prior can do; the fix is a **rich, learned, ORTHOGONAL individuation/meaning representation** (a ~200-d ATL-grade hub, carved by usage), read top-down. This is the north-star **P1** (`the_meaning_channel_needs_a_generative_world_knowledge_situation_model...`), which now carries a pre-registered TARGET (the 0.905 coref oracle) + an INSTRUMENT (the score-loss decomposition) from these two problems. P1's brief is sharpened accordingly.

- **2026-09-02 (INTEGRATION — register-native parse/POS data is the WRONG 19c lever; SELECTION (agent-composed thematic-fit) is the right one; EXCELLENT located-negative + deconfounded positive).** Problem `register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging` (owner-DONE), reverified **13/13** first-hand. **CORRECTS the parser §2b entry below's implicit "PP-attachment is the 19c wall" framing:** PP-attachment is only **8.1%** of the 19c who-did-what reach residual (W7), and the "19c verb-ID collapses −0.10" that motivated the brief is **87% COPULA-as-AUX** — correct UPOS, not tagger error (W8, AUX 548/629); genuine archaic open-class mistag is 2.2% and frequent-frames register tagging is net-negative (W2 −0.010). So a gold-19c-parse/POS corpus caps at ~8% and MISSES the lever. NEW PINNED-AND-MEASURED: the 19c who-did-what bottleneck is SELECTION (which noun is the verb's argument, 27% reachable-but-mispicked), it bites the meaning/thematic-fit STORE not the grammar (a structured store beats its verb-shuffle twin +0.081 CI-sep on MODERN but TIES on 19c — W9 — register-drift is a knowledge-poverty wall, not a parse wall), and its faithful mechanism is COMPOSITION P(patient|agent,verb) built from RAW exposure (no gold): on the CLEANED direct-object gold the verb-specific thematic-fit signal is REAL (+0.097 CI-sep over verb-shuffle, W12) and composition beats its info-free agent-shuffle twin +0.076 CI[+0.029,+0.123] (W13) — the agent×verb conjunction is real (a positive prediction of conjunctive binding, Frankland-Greene). CRITICAL MEASUREMENT FLAG: the 19c who-did-what GOLD is ~85% oblique-contaminated (the contamination was the confound hiding the store signal — W11 ties on full gold, W12 separates on cleaned) → **the baseline board's 19c who-did-what arm (~0.14) is scored against a contaminated gold; clean it before quoting a 19c selection number.** PARSER-SERVICE REFINEMENT: the parser's ONLY real 19c service to who-did-what is emitting TYPED argument slots (nsubj/obj/obl) to BUILD the store — NOT PP-attachment, NOT register tagging (so the DEBT-2 parser-wire's "deeper PP-role routing" is de-prioritized as a 19c lever). No hdlab wire (located negative; the parse/POS-data framing is retired). Follow-ons FILED: `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold` (priority 2 — the demonstrated-real lever + gold-cleaning) and `the_reader_has_no_copular_is_a_binding_schema` (priority 4 — base reader 0/376 on predicate complements, register-independent, ~23% of the population). Exemplary disk-outranks-brief (refuted the brief's own MEASURED premise + deconfounded a real lever the noisy gold hid).

- **2026-09-02 (DEBT-2 WIRING ROUND, owner-authorized #1-on-recovery — wire (b) COREF DENSIFIER LANDED).** Promoted `experiments/world_state_entity_binding.py` → `hdlab/world_state_entity_binding.py` VERBATIM (byte-identical; stdlib-only, self-contained) and landed a default-off `densify_world_state` sub-flag of `track_world_state` on `_read_world_state`: each world-state HOLDER (AGENT + recipient/source ARG2) is keyed to the canonical DISCOURSE-ENTITY via the promoted `EntityBinder` (indexical I/me→NARRATOR; he/she→the reader's OWN resolved coref cluster, supplied by a `(sent_idx, pronoun-head)→cluster` map built from `sm.coref_resolutions` — NO new resolver, NO gold at inference; object it→recency theme via `bind_theme`; nominal→head; we/you/pleonastic→abstain→dropped), so possession attaches to the entity node (John…he…him → one key), not the surface mention (Glenberg/Meyer/Lindem 1987). This is the brain-foundational Stage-1 reference-resolution point of the parent problem, LIVE. Registered `world_state_densify_live_reader_v1`; witness `test_world_state_densify_landing_organ.py` 4/4 (default-off world-state grid == raw-head recompute byte-exact; promotion byte-identical + dispatch battery identical across cores; densify-on canonicalizes a constructed list john/he→C5/I→NARRATOR/mary + object it→recency cup; wire FIRES on real 19c prose, e.g. 'my'→NARRATOR). **HONEST BOUND (not bookkeeping-inflated):** the +0.148 who-has-what is the ISOLATED gold-aligned LEVER (measured by `exp_world_state_coref_densify_v1` on the baseline board's RIGHT corpus, twin loses); this wire lands the ENTITY-KEYED representation LIVE so the STATE dimension is no longer a raw-string island — there is NO downstream live who-has-what consumer scoring `sm.world_state` yet, so it moves NO live board number (the yield shows on the board's isolated arm, and the coherence next-mention prior P3 is the residual). Burns the (b) item of the DEBT-2 round; the live-reader import set grows by `hdlab.world_state_entity_binding` (lazy, flag-on).

- **2026-09-02 (INTEGRATION — two owner-DONE: the top-down sense selector DECISIVELY re-localizes the meaning channel to GENERATION; incremental entity-maintenance lifts who-has-what via long-distance re-instatement).** Both reverified first-hand (top-down 4/4, entity-maintenance 12/12); both EXCELLENT.
  1. **TOP-DOWN SENSE SELECTOR (a rigorous POWERED located negative = full PASS).** The directional predictive-error detector (domI = N400 on the DOMINANT reading) is CONFIRMED (AUC 0.71 struct_domI > 0.69 sym > 0.66 bag — >> the brief's claimed ~0.51; the disk corrected the brief). But the top-down override does NOT net-beat the MFS frequency floor (best NET −0.0013 CI-sep BELOW) — a BASE-RATE SEE-SAW (dominant senses 0.98, subordinate only ~30% of items). DECOMPOSED: net = fired·[p·a_s − (1−p)·c_d] with p~0.48 (detector precision), **a_s~0.33 (override accuracy = 'which SPECIFIC rare sense' = GENERATION from a world-knowledge situation model — THE binding limit)**, c_d~0.64; break-even needs p·a_s~0.34, we get ~0.16. Detection is maxed/cheaply-improvable; the readout is NOT the fix — a_s is the WORLD-KNOWLEDGE SOURCE. This DECISIVELY re-localizes the north star to the GENERATIVE half → filed P1 `the_meaning_channel_needs_a_generative_world_knowledge_situation_model...`. Exemplary honesty: RETRACTED a smoke 'Zwaan dimension signature' that didn't replicate at power. WIRE: TIER-1 INSTRUMENT-only (the directional detector as `semantic_control`'s frequency-independent trigger; NOT a default — the override doesn't net-gain) = scoped DEBT-2.
  2. **INCREMENTAL ENTITY-MAINTENANCE (SOLVED).** A recurrent loop chaining each resolved he/she pronoun back into the picked entity's ACT-R activation history (over the near-optimal graded pick) raises he/she who-has-what +0.0573 held-out / +0.0647 all-docs CI-sep, **100%-attributed to entity-maintenance** (surgical: identical pick+candidates, only histories differ), **entirely long-distance re-instatement** (far ≥2-back 0.261→0.471 = 43% of the bucket gap; near inert), twin loses. NEW brain findings: SOFT 'hold both' LOSES to HARD commit (attractors SETTLE — CA3/Hopfield, a self-correction); pick×maintenance are COUPLED (the loop helps the graded pick +0.065 but HURTS the rigid hard-tier −0.025 → wire graded pick + loop TOGETHER); decay-robust d=2/3/4, flips at d=1 (the lever exists BECAUSE memory decays). Residual = the missing COHERENCE next-mention PRIOR (29.4% of errors structurally-dominated) → filed P3 `who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde`. WIRE: default-off `graded_chain` path over `graded_coref_pick` (the reader has the chain primitive on its WEAKER centrality pick) = scoped DEBT-2.
  **CONVERGENCE HOLDS + SHARPENS:** the meaning channel's remaining gains are in the GENERATIVE situation model (a_s = which specific sense); the who-has-what residual is the coherence prior; the parser/role front-end (P2, in flight) is the shared LIVE cap. All three point at building the reader's own TOP-DOWN situation/comprehension model.


- **2026-09-02 (INTEGRATION — three owner-DONE at once: the improved parser + a parser SERVICE SPEC; the coref-densifier EntityBinder; the grow-the-graph LOCATED NEGATIVE that re-points the meaning channel to TOP-DOWN COMPREHENSION).** Three problems folded in together, each reverified first-hand (parser 8/8, coref-densifier 18/18, grow-the-graph 4/4); all three EXCELLENT.
  1. **THE PARSER is improved AND its service contract is now SPEC'd (problem `the_extraction_front_end_parser_is_the_cross_task_bottleneck…`, EXCELLENT).** A genuinely better glass-box parser — arc-eager incremental heads + Zhang-Nivre 2011 rich non-local STRUCTURAL features (dependents/valency/head-of-stack = a structured working-memory buffer; Now-or-Never, Christiansen & Chater 2016) — lifts UD-EWT test UAS **0.775→0.842 gold-POS (+0.067, 3-seed CI-sep)**, who-did-what patient +0.033 CI-sep (HARD +0.090; 19c LitBank +0.106), per-argument attach precision up across obj/subj/passive/oblique, and RESOLVES the prior buried-subject long-arc regression; it emits a CALIBRATED abstain/drop signal (Platt on the arc-eager margin: **ECE 0.153→0.026**, dropped-bottom-20% concentrates errors 4.2x, N7 entropy AUC 0.694/0.764 vs shuffled-twin ~chance). THE HEADLINE (owner-driven re-centering): a precise **PARSER SERVICE SPEC** — measuring all 9 brain-foundational consumers' head-dependence (not assuming it), one parser serves them all iff it supplies the FIVE levers **(1) UPOS + (2) verb-lemma + (3) voice + (4) accurate 1-best PP-CHAIN attachment (the SOLE high-precision head demand + the ONLY measured parse ceiling, oracle-PP +0.10–0.18) + (5) a calibrated abstain** — and NOT general head-accuracy (the wired patient organ is head-INDEPENDENT + label-free, already 0.541/0.411), NOT dependency labels (the arc_labeler is measured-HARMFUL for role recovery, −0.030 modern / −0.107 on 19c), NOT an n-best distribution (no consumer uses one; the graded_competition MAP theorem). Honest scope: general UAS improved but is NOT the load-bearing lever; the two biggest levers (register-robust UPOS, PP-chain attachment accuracy) are DATA-BOUNDED (need gold target-register parse/POS — self-training, global-beam training, and word-clusters are all refuted on disk). WIRE: the arc-eager parse operator is PROMOTED to `hdlab/arceager_parser.py` self-contained (verified BYTE-FAITHFUL 6/6; WIRING_MAP DEBT-1 burned; registered `arceager_parser_operator_v1`; asset `data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz`); the reader-integration (a default-off `parser='arceager'` route needing a POS source + `attach_conf`→`graded_competition` + calibrated-abstain→`predict_revise` drop-trigger + routing `predicate_argument_frontend` through the improved parser) is a scoped DEBT-2 wiring round. Follow-on FILED: `register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging` (priority 2, the two data-bounded levers combined).
  2. **THE WORLD-STATE REGISTER's coref-blindness is fixed by a two-stage EntityBinder — and "coref" is THREE routes, not one (problem `the_world_state_register_is_coref_blind…`, EXCELLENT).** Disk-outranks-brief: "reuse the reader's own coref" cannot resolve object 'it' or first-person 'I' (the reader's coref is he/she-only), so the solver decomposed the parent's "81% pronoun agents" by CLASS (indexical I/me 64.7% on MCScript2 / anaphoric he/she 21.6% on LitBank / object-anaphora 'it') and built the two routes the reader lacked. PINNED (research-verified): Stage-1 reference is BIFURCATED — indexical O(1) narrator lookup (Kaplan 1989) vs anaphoric O(n) Centering salience search (Grosz-Joshi-Weinstein 1995); Stage-2 possession-state update is unified and already faithful (Zwaan-Radvansky 1998; Glenberg-Meyer-Lindem 1987) — so the whole defect is upstream in Stage-1, along the brain's own module boundaries. MEASURED (CI-sep, floors+twins+change-point): binding the holder through the reader's OWN he/she coref recovers who-has-what aggregate 0.570→0.719 (**+0.148 [0.096,0.208]**; on the he/she-holder subset where blindness bites 0.000→0.500, gold oracle 1.000, shuffled-coref null p95 0.154); **object-anaphora resolution by RECENCY 0.730** [0.667,0.794] vs random-twin p95 0.323 vs first-mention floor 0.132 vs the reader's coref 0.000 (abstains) — NEW brain-foundational finding: subject-prominence Centering HURTS objects (paired −0.212 CI-sep) because objects are not the backward-looking center, so the SAME Centering machinery with a RECENCY (not Cf-ranking) parameter is the faithful copy; end-to-end who-has-what blind 0.285→full binder 1.000 (+0.715 CI-sep); POWERED bridging/impossible-action detection blind 71.5%-false-flag (actively harmful)→densified 0%. Honest self-correction (the deepest finding): the he/she ceiling is GROUPING-bound — ~91% of the headroom is PRONOUN-CHAINING into entity activation histories (incremental entity maintenance; ACT-R base-level / Gernsbacher structure-building), so the realistic glass-box ceiling is ~0.46 not 0.75 and the graded pick is near-optimal (a located negative — parameter sweep +0.003, not CI-sep). WIRE: the EntityBinder is self-contained + ready to promote to `hdlab/world_state_entity_binding.py`; a default-off `densify_world_state` flag in front of `_read_world_state` (indexical + object-anaphora routes self-contained; the he/she route needs the reader's mention-level coref stream plumbed in) is a scoped DEBT-2 wiring round. Follow-on FILED: `incremental_entity_maintenance_pronoun_chaining_for_who_has_what` (priority 3, the ~91% ceiling lever).
  3. **GROWING the meaning graph from reading is a rigorous LOCATED NEGATIVE that re-points the whole meaning channel to TOP-DOWN COMPREHENSION (problem `the_semantic_graph_is_static…`, EXCELLENT located-negative — a full PASS under the bar).** A graph grown from reading (66,843 context-disambiguated, PPMI, cross-situational, precision-gated edges; VERIFIED ≠ static, sum|dT|=5398) does NOT beat the static WordNet++ graph on WSD (Raganato argmax −0.0088; powered subordinate-override: growth HURTS rare senses −0.0148), and the ROOT CAUSE is established from ~8 controlled angles: the discriminating signal for rare/subordinate sense selection is TOP-DOWN STRUCTURED COMPREHENSION (predictive coding; the N400 = the semantic prediction error), NOT local co-occurrence — five bottom-up routes (PPMI/BCM growth, graded settling, three gold-blind detectors, a continuous-rep prototype, a flat-discourse prototype) all fail consistently. CONFIRMED brain sub-mechanism: naive Hebbian/PPMI growth is rich-get-richer (frequency-dominance rho=0.36; helps dominant, starves rare); the brain's HOMEOSTATIC BCM sliding-threshold fix rescues rare senses (+0.0155 CI-sep over PPMI) but only reaches PARITY with static. READ-SIDE POSITIVE (validated, controlled): the graded COMPETITIVE-SETTLING readout recovers subordinate senses **+0.19 over discrete argmax**, context-driven (beats shuffled-context +0.17 CI-sep), strongest for HOMONYMS (Rodd/Klepousniotou); `semantic_control` reproduces. NOT a ceiling — the route to a positive is building the comprehension model (bootstrapping senses + comprehension; Yu & Smith / Srinivasan). WIRE: TIER-1 = the read organ (reordered-access → competitive settling → `semantic_control`) is a real read-side meaning-channel upgrade AND the grounded-graph-organ's DEBT-2 completion ('emit the settled vector, not an argmax synset') — a scoped DEBT-2 wiring round; TIER-2 = do NOT wire the discrete-edge growth (confirmed non-improvement).
  4. **THE STRATEGIC CONVERGENCE (why these three landing together matters more than any one).** All three independently point at the SAME lever — TOP-DOWN STRUCTURED COMPREHENSION (the reader's own situation model): the graph-learner PROVES bottom-up growth cannot do rare-sense selection (the signal lives at the TOP of the hierarchy, not in local co-occurrence); the parser is the front end that GATES comprehension (its measured service spec — UPOS/lemma/voice/PP-chain + an abstain — is exactly what a comprehension model needs from its input); and the coref ceiling IS comprehension-level ENTITY TRACKING (pronoun-chaining = incremental entity maintenance, a recurrent situation-model process). This re-frames the north star (LEARNER-ON via a clean foundation): the missing organ is the reader's OWN situation model as a TOP-DOWN PREDICTIVE-CODING sense selector, into which the parser feeds and out of which sense selection + entity maintenance fall. FILED as priority-1 `wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector` — the convergence point of all three recent owner-DONE submissions.

- **2026-09-01 (INTEGRATION + CORRECTION — the register-native store: the domain lever is REAL but JOINT-only, the parent's +0.149 was LEAKAGE, and the PARSER is the cross-task ceiling, EXCELLENT).** Problem `the_selectional_event_store…register_native_corpus` (owner-DONE), reverified **5/5+2** first-hand. **CORRECTS the p5 §2b row below:** on a genuinely DISJOINT corpus the MARGINAL verb→object store TIES the out-of-domain store (W4 −0.007, frac≤0=0.73) — so p5's headline **+0.149 marginal domain lever was topical near-leakage** (leave-one-sentence-out on the TEST corpus); it does NOT transfer to a disjoint corpus. NEW PINNED-AND-MEASURED: the domain lever is REAL but lives in the JOINT (subj,verb,obj) FHRR event code (science FHRR +0.035 CI-sep over simplewiki; verb-shuffled twin loses +0.094; wrong-domain fiction loses −0.140; leakage-guarded n_leak=0; volume excluded — simplewiki has MORE triples yet loses) — a positive prediction of conjunctive binding (Frankland-Greene): register knowledge is a property of who-did-what-TO-what structure, not verb→typical-object preference. THE CROSS-TASK VERDICT (the deep dive, owner-driven, composing owner-DONE organs): who-did-what 0.474→0.658 (68% chance→human), then EXHAUSTIVELY SATURATED — no store-gate/agreement/soft-AND/generative/grounded-12d/animacy trick moves it; signal-loss decomposition shows parse-correct = **0.989**, the entire residual is parse-attach failure (35.2% gold-not-attached), and the substrate's own parser LOSES to spaCy `en_core_web_sm` (+0.073). So the **PARSER is the highest-compounding cross-task lever** — THREE convergent lines (this store + the world-state register's "highest-COMPOUNDING lever" + p5's "the sole lever is a better parser"). No hdlab wire (the proposed integrators `graded_role_assigner`/`convergent_cue_reader` are NOT in the live reader, and the store's value is SATURATED at the current parser — it is a validated per-domain ASSET whose live payoff is parser-gated, used on parse-BROKEN items 0.308 vs 0.145, NOT parse-correct items). ISSUED the parser follow-on (priority 1), written MULTI-OBJECTIVE per the owner's directive that improvements did NOT transfer across the parser's ~8 distinct needs (recall-vs-precision; richer-PP-roles helped world-state but HURT patients −0.051; store helps broken-parse but hurts correct-parse; biggest-modern-lever is a net-loss on 19c; 1-best ≠ the distribution the graded organs need). RETIRES the deferred p5 verb-role (marginal) wire's domain-lift premise (a disjoint domain gives the marginal selector NO lift). Grade EXCELLENT (exemplary disk-outranks-brief: refuted the brief's own MEASURED premise).

- **2026-09-01 (PROMOTION + SCOPE-SHARPENING — the north-star meaning organ is now in `hdlab/`, and the reframe target is precisely located).** PROMOTED the grounded semantic graph organ to `hdlab/grounded_semantic_graph.py` VERBATIM + SELF-CONTAINED (inlined ~14 primitives from three experiment cells; NO experiments imports), verified FIRST-HAND 3/3 (builds 117,659 synset nodes / 1,025,488 edges; differentiates 'bank' river≠money; BYTE-EXACT to the experiment organ's `select_sense` on 6 ambiguous probes). Registered `grounded_semantic_graph_organ_v1`; WIRING_MAP DEBT 1 (promotion) burned for this organ. NEW SCOPE FINDING that sharpens the queued reframe (corrects the loose "reframe canonicalize" framing): `reading_grounding_loop.canonicalize` is **NOT** in the live `situation_reader.read()` path — it is the OFFLINE grounding/CONSOLIDATION write-path (foundation building) and does CONCEPT-ANCHOR merging by cosine, NOT WordNet sense selection. So the reframe FLAT→GRAPH is a **MEASURED re-architecture** of a LOAD-BEARING consolidation function (the bar: does graph-diffusion grounding beat flat-cosine grounding on a held-out grounding task?), and it **COMPOSES with the in-flight pri-1 grow-the-graph-from-reading learner** (pri-1 = the WRITE/GROW half; the reframe = the READ half). Deferred as a sequenced DEBT-2 unit (do it after pri-1 lands, or as its own measured unit) — NOT a rushed change to a load-bearing function. The brain-foundational COMPLETION (emit the graded SETTLED PPR activation vector, not an argmax synset — +0.067 AUC richer) rides WITH the reframe. Follows the belief_timeline/state_register promote→wire pattern.

- **2026-09-01 (INTEGRATION + WIRE — the situation model's mutable WORLD-STATE / STATE dimension is BUILT and WIRED, EXCELLENT).** Problem `situation_model_has_no_mutable_world_state_register` (owner-DONE, PARTIAL = mechanism+learning SOLVED with the full control battery, open-text a located coref residual), reverified **36/36** first-hand. NEW PINNED-AND-MEASURED: the situation model maintains a MUTABLE current state updated by event EFFECTS and read by event PRECONDITIONS (Zwaan & Radvansky 1998 event-indexing; STRIPS Fikes & Nilsson 1971); possession `have(holder,obj)` is the maximally-mutable predicate — object availability tracks the CURRENT relation to the protagonist, NOT last mention (Glenberg/Meyer/Lindem 1987). Register 1.000 vs the strongest stateless floor `last_obj_mention` 0.750 (+0.250 CI-sep, null p95 0.026); all three info-free twins LOSE (order-shuffle 0.546, bind-shuffle 0.659, empty 0.250); change-point 100%/0%; precondition-read detects violations 1.000 vs ever-had 0.512 (+0.488). Operators FROM WHAT WE HAVE (FrameNet 105 transfer verbs / 13 frames WITH the recipient role the stock front-end lacked — the FRAME→STRIPS-effect map is the one authored PINNED computation; verb membership + roles come from FrameNet) and LEARNABLE (OOV transfer verbs induced from observed possession transitions recover FrameNet gold 1.000 vs shuffle 0.417, abstains on non-transfer). **CLOSES the aligner's #1 named adjacent gap** (the aligner §2b entry below seeded this) — and CONFIRMS the aligner's finding that order is CONVENTIONAL not causal: the downstream serve-test shows the register does NOT break the ~0.59 before/after order wall (a mutable register is structurally IDLE for everyday-script ordering — so the register is correctly a STATE organ, not an order organ). REUSES the existing `location_register` (SPACE, at/loc) + `state_register` (ENTITIES, open/broken) — builds only the genuinely-missing possession + mutable-forward-application + precondition-READ layer. **WIRE LANDED (Q111, WIRING_MAP):** promoted `experiments/world_state_register.py`→`hdlab/world_state_register.py` + `experiments/possession_operators.py`→`hdlab/possession_operators.py` VERBATIM; a default-off `track_world_state` flag on `SituationReader` folds the reader's OWN events into `sm.world_state` (has/holder_of/is_open/unmet_preconditions), operators from the cached FrameNet lexicon (no nltk at inference). Registered `world_state_dimension_live_reader_v1`; witness `test_world_state_register_landing_organ.py` 4/4 (default-off byte-identical; flag-on register == recompute through BOTH hdlab + experiments cores BYTE-EXACT; promoted-core mechanism; the wire builds correct mutable possession on a known transfer). **HONEST BOUND:** the wire lands the CAPABILITY (mechanism-proven, byte-faithful); LIVE who-has-what on real prose is COREF/parser-recall-bound (81% pronoun agents — the register faithfully folds whatever the reader extracts, so 19c extraction noise flows through). The register-through-coref open-text re-measure + frame-SENSE selection are the located follow-ons. Flip default-ON is a SEPARATE owner decision.

- **2026-09-01 (INTEGRATION — the NORTH-STAR meaning organ: a grounded semantic GRAPH read by SPREADING ACTIVATION clears the sense-selection wall, EXCELLENT).** Problem `promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ` (owner-DONE), reverified 5/5 first-hand. This is the p3 finding built into an organ: sense selection is RELATIONAL, not feature-cosine — so read WordNet as a NETWORK diffused over, not a flat lookup. NEW PINNED-AND-MEASURED: personalized PageRank == random-walk-with-restart == the diffusion form of SPREADING ACTIVATION (Collins & Loftus 1975) settling into a sense attractor (Rodd 2004), over WordNet + MFS-disambiguated gloss edges + ConceptNet thematic edges. CLEARS the context-shuffle twin on gold HELD-OUT WiC (+0.0521 CI[0.0229,0.0807], excludes 0) — the FIRST time our meaning channel beats the dominant-sense null on a real per-context task — AND beats MFS on the field-standard Raganato ALL all-words WSD (+0.0295 CI-sep, ~UKB 67.3 level, glass-box/LM-free). Controls locate the levers WITH NUMBERS: gloss edges are load-bearing (NO_GLOSS ~ MFS), disambiguated glosses required (undisambiguated do NOT clear the twin), IC-weighting is NEUTRAL-TO-NEGATIVE (not the lever), the grounded-node ablation SHRINKS the margin (grounded features are a context-FREE lift, not the per-context lever — the RELATION structure is), damping-sweep robust. The residual is LOCATED to two NAMED components (context-signal strength: the full SyntagNet graph + freq-weighted seeding), NOT WordNet granularity/coverage. HONEST CROSS-TASK BOUNDARY: on SemCor all-words WSD the frequency prior MFS beats the walk (pure 0.39; +prior 0.58 < MFS 0.73) — a scope limit reported, locating the missing reliability-weighted-control component (`semantic_control`, landed-but-unwired). This reframes the reader's grounding write-path from a FLAT store to the GRAPH (the audit's "meaning organs are unwired islands" debt). WIRE QUEUED (WIRING_MAP): promote `grounded_semantic_graph_organ.py` + reframe `reading_grounding_loop.canonicalize`. Follow-ons (not yet issued): the brain-foundational COMPLETION (emit the graded SETTLED activation vector, not an argmax label — +0.067 AUC richer, held-out CI-sep) + the LEARNED graph (grow/retune/own-granularity; the north-star, specced in `LEARNED_GRAPH_brain_mechanism_spec.md`; naive co-occurrence learning is a clean NEGATIVE — the faithful fix is context-DISAMBIGUATED self-trained edges). NEW owner-authorized data assets: SyntagNet 1.0 + the Raganato WSD framework.

- **2026-09-01 (INTEGRATION — the verb-role selectional store is DOMAIN/REGISTER-RELATIVE; the corpus is the lever, EXCELLENT).** Problem `the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store` (p5, owner-DONE), reverified 10/10 first-hand. NEW PINNED-AND-MEASURED: verb-specific selectional preference / thematic fit is an EXEMPLAR (instance) distribution, NOT a centroid — a nearest-exemplar k-NN over GROUNDED OBJ fillers picks the patient CI-sep over the coarse holistic prior (+0.102), the verb-role MEAN centroid (+0.067 — the INSTANCE distribution is the lever, not richer features), and position-only (+0.143); the verb-KEYING does the work (verb-shuffled twin loses +0.097); it generalizes to UNSEEN fillers by grounded similarity (+0.062) and replicates in GloVe-300. CORRECTS the `predictive_reader` audit row: the coarse 12-d grounded CENTROID is a valid violation GATE but a poor WHICH-argument SELECTOR — a verb-keyed exemplar store IS the selector. DEPLOYMENT: a construction-conditional (position × exemplar, word-order down-weighted at non-canonical structure — Competition Model cue weighting) selector beats the LIVE wired reader 0.481→0.508 (+0.027 CI-sep). THE DEFINITIVE FINDING (oracle-ladder dissection, ruled out with NUMBERS): who-did-what role assignment is bounded by DOMAIN MATCH of the selectional/event corpus (+0.149, ~80% of the gap) — NOT grounding/features (grounded adds +0.20 over memorization), NOT the mechanism (FHRR binding faithful), NOT the combiner (a learned arbitrator ties the better single system), NOT parse cleanliness (+0.036). This UNIFIES with the 19c register-drift wall (an in-domain store beats the modern one +0.081; the modern parser also degrades on archaic prose — a two-layer located negative). Front-end who-did-what role assignment sits at ~0.35× human normalized; the wall = domain-matched knowledge. WIRE QUEUED (WIRING_MAP): `hdlab/verb_role_exemplar_selector.py` (loads a 14.7MB offline `selectional_slots_v1.pkl`; `select_patient` via k-NN grounded similarity) → the `predict_revise` drop-fill target selector + a construction-conditional role tie-breaker; acceptance gate = `test_verbrole_exemplar_which_arg.py` 10/10. The #1 follow-on is ISSUED (`the_selectional_event_store…register_native_corpus`, priority 2). NON-LEVERS (do NOT re-attempt): Binder-65/GloVe-300 features, a learned combiner/arbitration, parser register-adaptation via self-training.

- **2026-09-01 (FOLD-IN — three owner-DONE at once: predict-and-revise WIRED [EXCELLENT], the grounding ceiling is REPRESENTATION-bound [EXCELLENT, a located negative], the event aligner's PRODUCT mechanism is REFUTED [STRONG]).** Three problems folded in together, reverified first-hand.
  1. **⚡ WIRED `predict_revise` — the reader now RECOVERS the who-did-what it DROPS (p2 predict-and-revise, EXCELLENT, 8/8 + 4/4).** The batch parse takes itself as truth and drops the patient when it precedes the verb (passive / object-relative / pre-verbal gap). LANDED a default-off `predict_revise` flag: a post-read pass fills each dropped ('?') patient by REUSING the validated `relcl_resolver.resolve_patient` (active-filler filler-gap; Frazier & Flores d'Arcais; Stowe 1986) with a nearest-nominal position fallback, preserving the original on additive `EventRecord.patient_prerevise`. PINNED-AND-MEASURED: recovers who-did-what CI-sep over the batch parse on BOTH modern QA-SRL (+0.060) and 19c LitBank (+0.059), gains localizing to non-canonical constructions (passive 0.29→0.57), canonical recall PROTECTED. The gain is a STRUCTURAL DROP-FILL (no surprisal gate needed — the drill refuted p2's re-selection route from the recall side). Corrects the `predictive_reader`/N400 line: the surprisal FLAG is a violation gate, but RECALL of the dropped structure is the lever, via the filler-gap resolver, not surprisal-gated reanalysis. Registered `predict_revise_live_reader_v1`; witness 4/4 (111/111 fills byte-exact to the validated drill).
  2. **🧠 The 59% grounding-accumulation ceiling is REPRESENTATION-bound, at the SELECTION level (p3 retrieval-practice, EXCELLENT located negative).** Retrieval practice, faithfully built (Mozer 2009 MCM), CANNOT select a correct grounding above chance on the CONSOLIDATION_FAIL population. Drilled to bedrock: the correct anchor is RETRIEVABLE (top-10 ~85% under EVERY encoder incl. the parser — the encoder is NOT the wall) but SELECTABLE by NO distributional read-out (nearest/bg-subtract/distilled/supervised all ~chance). The SENSE signal is genuinely ABSENT from distributional co-occurrence (whisky~weddings ≠ whisky~brandy); sense is TAXONOMIC/RELATIONAL (ATL hub; Mirman 2017). CORRECTS the earlier "context-encoder / p2-parser is the deepest meaning lever" line — refuted head-to-head. The fix is a GROUNDED (ATL) sense-SELECTION, promoted to the north-star meaning organ (`promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ`): the reader owns WordNet as a FLAT lookup; the grounding-accumulation ceiling and the sense-selection wall are the SAME structural wall (flat store, not a relational GRAPH read by spreading activation).
  3. **🧩 The event-aligner's PRODUCT combination rule is REFUTED; the FEATURE SET (particle + 2nd-arg) is the lever (aligner, STRONG near-positive).** A grounded conjunctive event code separates similar events (get-IN vs get-OUT) — but the soft-AND (multiplicative) PRODUCT ties/loses the additive SUM (−0.002 n.s.); what matters is that the particle/2nd-arg is IN the code and kept as a distinct category (a grounded cosine can't tell in/out apart — opposites look alike). Isolated probe (n=52,030): particle/2nd-arg ablation collapses alignment 0.926→0.608 CI-sep. End-to-end reaches a near-positive (0.591) but the residual is the weak LEARNED canonical ORDER (co-occurrence, not cause). NEW fidelity finding: `transitive_ordering` is a TOTAL order, a type-error for the PARTIAL order of scripts (abstain on causally-independent pairs). Seeded the mutable world-state register (packaged) + the causal-enablement order foundation. No wire (neither the negative nor the near-positive earned one; the follow-ons are the value).

- **2026-09-01 (INTEGRATION — reasoning, a located negative) — 🧠 INTEGRATED (EXCELLENT): the reader CAN reason over its own situation model and the reasoning STEP is brain-faithful, but reasoning is capped by SEMANTIC EVENT-ALIGNMENT PRECISION (DG/CA3 pattern separation) — NOT by extraction (loop-closer refuted that) and NOT by a knowledge gap (90-98% in-passage).** Problem `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference` (p6, owner-DONE, PARTIAL = a full-PASS located negative), reverified 15/15 first-hand. `situation_reader` temporal reasoning is now DRIVEN + MEASURED LIVE end-to-end on a real modern inference benchmark (MCScript2 before/after, n=1128). NEW PINNED-AND-MEASURED: the episodic WHEN dimension (`timeline_register`) is a VALIDATED reasoning signal — the reused `transitive_ordering` read-out beats a shuffled-timeline twin CI-sep (+0.036 [0.0044,0.0671]) and recovers true order under narrative reordering (0.737 vs 0.263) — but is NOT sufficient for MCScript2 inference (ties the similarity + text-position floors). `transitive_ordering` GENERALIZES to a NEW domain (temporal script-order), confirming it as the substrate's ONE general cognitive-map / relational-integration organ (PINNED; Behrens 2018; Whittington TEM 2020; transitive inference = Dusek & Eichenbaum). THE COMPOUND-WALL VERDICT, discriminated by a chain of controlled experiments each refuting a cheaper hypothesis: the binding residual is SEMANTIC cross-narrative event ALIGNMENT = the brain's DG/CA3 PATTERN-SEPARATION function (keep similar events from colliding). **RECONCILES + REFINES the p4 §2b entry (below):** p4 named FRONT-END ROLE ASSIGNMENT (agent-role 0.271) as the ecological who-did-what bottleneck — still true for who-did-what — but for the REASONING task the loop-closer REFUTED "extraction is the binding wall" (a clean spaCy supplied-grammar parse raised coverage 0.36→0.74 with accuracy flat at chance), so the reasoning-specific residual is event-alignment precision, not extraction. NEW DEVIATION on the two event-identity organs (each fails a DIFFERENT half): `bound_event_backbone` is conjunctive but EXACT-HASH → OVER-separates (kills paraphrase, the 0.48 symbol-tie); `content_addressable_retrieval` is graded but ADDITIVE → UNDER-separates (the fan effect, ~40% mis-align). THE FIX (de-risked by a gold-free headroom drill: 98% of confusable pairs separable by particle/arg/prep; 51% of Qs hinge on a particle the code ignores) = a grounded CONJUNCTIVE event code with a soft-AND (multiplicative) per-role kernel — PACKAGED as the assignable follow-on `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner` (priority 4). Two OPTIONAL low-cost substrate fixes OWED: persist `frame_induction`'s >90s recompute to disk (perf); key `timeline_register` events by `(lemma, sent_idx)` not lemma alone (the "got in" vs "got out" de-dup fidelity limit). No hdlab wire landed (the capability did not clear the floor). Exemplary self-correction: the solver REFUTED its OWN "just fix the parser" conclusion via the loop-closer.

- **2026-09-01 (INTEGRATION + WIRE — the ASSEMBLY completion) — 🧩 INTEGRATED (EXCELLENT) + LANDED the TIERED BOUND-EVENT-TOKEN BACKBONE: the reader now stores the JOINT the parallel silos could not — the BINDING PROBLEM is fixed, and DEBT 2 (the assembly) is REAL, not just composed.** Problem `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token` (p4, owner-DONE), reverified **10/10** first-hand. CORRECTS the §1/§2b framing that "turning all dimension flags ON COMPOSES but does not BIND (interaction byte-exactly 0)" → the fix is now WIRED: a default-off `bind_event_tokens` flag on `SituationReader` builds `sm.event_tokens` (ONE FHRR bound token per event over {AGENT,PATIENT,PRED,TENSE}) + `sm.episodic_store` via a NEW thin assembler `hdlab/bound_event_backbone.py` that COMPOSES existing organs (`binding` + `n400_coherence_monitor` + `hippocampal_encoder`). PINNED MECHANISM (copied operation-for-operation): comprehension builds ONE bound event token indexed on all dimensions (Zwaan & Radvansky 1998; Franklin 2020 SEM); same-event recognition = CA3 pattern completion (Marr 1971); the decisive control is RECOMBINATION — same items rebound differently — the conjunctive-memory double dissociation (Konkel & Cohen 2009); the brain MUST CHUNK because one passage-scale superposition collapses ~1/√M (Plate/Frady). MEASURED (both genres, bootstrap CIs): JOINT coref 1.000 CI-ABOVE late-fusion-of-marginals 0.600 (sep +0.400) on LitBank old fiction AND UD-EWT modern web; BINDING-SHUFFLE collapses it (pos-recognition 1.000→0.12 while marginals untouched — the conjunctive-memory signature); info-free twin null; MUST-CHUNK fires (flat single bundle 1.0→0.40 @ M=256 while multibank + DG/CA3 hold); cued retrieval 1.00 (bound token) vs 0.01 (silo, chance 1/M — a capability class the silo LACKS); NECESSITY (beyond the bar) — under PARAPHRASE grounded distributed binding 0.379 BEATS symbolic-exact 0.217 (chance). NEW FIDELITY DEVIATIONS LOGGED (owner "drill all walls"): (1) the ecological bottleneck is FRONT-END ROLE ASSIGNMENT (agent-role 0.271 while event recall 0.953) — the integration gap is the parser, NOT the binding codec; (2) `hippocampal_encoder` CA3-COMPLETION is LOW-FIDELITY (it DG-separates the retrieval cue; DG is an ENCODING op, retrieval should be EC→CA3-DIRECT; single-step Hebbian collapses to a dominant attractor under iteration) — the DIRECT similarity route completes 1.00, so the store is usable today, but a faithful CA3 completer is a scoped follow-on; DG SEPARATION itself is HIGH-fidelity (holds the store flat to M=256 — the prior DG HARD_FAILs were on the WRONG tier, re-scope CONFIRMED); (3) the `n400_coherence_monitor` tau=1.5 under-segments some long-coherent passages (OUR-INVENTION, sweepable); (4) the grounded/distributional FUSION wall is CORPUS-SIZE-bound (UD-EWT ~12.5k sentences exhausted — a large-corpus distributional spoke, not compute, is the lever; the `reader_meaning_channel`). NEW ANALYTIC RECORD: a single passage-level superposition of event tokens is LINEAR → its readout = SUM of marginals → it IS the silo (corr 0.95) — which is WHY the shared token must be TIERED (chunked + pattern-separated), converting "must chunk" from an assertion into an identity. Witness `test_bound_event_backbone_landing_organ.py` 5/5 (default-off byte-identical on 219 events + all 219 tokens torch-EQUAL the validated cell + `resolve`==`joint_decide` 30/30 + tiered store assembled). Registered `bound_event_token_backbone_live_reader_v1`. This is the step from the reader HAVING features to the reader UNDERSTANDING which goes with which — **the prerequisite for reasoning (p6)**. Flip-on default-off/owner-gated.

- **2026-08-31 (WIRING ROUND) — ⚡ WIRED: `predict_surprisal` LANDED into the live reader — `predictive_reader` is no longer an island (island in code → the FIRST live node of the prediction-error hierarchy).** Default-off `predict_surprisal` flag on `SituationReader`: a post-read pass exposes per-event `EventRecord.patient_surprisal` + `pred_precision` (the N400 error-RISK FLAG) + an optional `low_confidence` abstain, computed via the promoted `hdlab.predictive_reader` loaded from a persisted QA-SRL-fitted foundation asset (`data/frontend_assets/predict_surprisal_predictor_v1.pkl`, 1.9MB, roundtrip byte-faithful). Witness `test_predict_surprisal_landing_organ.py` 4/4 (default-off byte-identical; flag-on `patient_surprisal` == an independent recompute BYTE-EXACT on 55 scored events; abstain correct; asset integrity). Added `PredictiveReader.save/load`. Registered `predict_surprisal_live_reader_v1`. Corrects the entry below: "wire QUEUED" → **WIRED default-off**. Do NOT wire auto-revision (proven NEGATIVE). Remaining queued reader-wire: `track_belief`.

- **2026-08-31 — ⚡ INTEGRATED (EXCELLENT): `predictive_reader` (N400 forward-prediction surprisal) is NO LONGER inert-in-evidence — validated LIVE as an error-RISK FLAG + a working ABSTAIN decision; the auto-revise decision is a DECOMPOSED negative (the reader's residual errors are STRUCTURAL, parser-recall-bound).** Problem `the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision`, reverified 8/8 first-hand. CORRECTS the §1/§2b "predictive_reader = inert island" line → "island in code; validated LIVE as a flag/abstain signal, `predict_surprisal` default-off wire QUEUED." MEASURED (through the LIVE read(), n=2606 QA-SRL patient items, reader error-rate 0.40): INFORMATIVE — live per-argument surprisal predicts the reader's OWN who-did-what errors AUC 0.651 [0.630,0.672] CI-sep, shuffle-surprisal twin p95 0.519 (loses); ACTIONABLE — surprisal-abstain lifts committed accuracy at 80% coverage +0.035 [0.022,0.050] CI-sep; GRADED (precision-weighted, CI-sep); GENERALIZES to 19c LitBank (AUC 0.624, twin loses). NEW PINNED-AND-MEASURED (4 drills): comprehension runs TWO DISSOCIABLE STREAMS — the N400 thematic-fit FLAG (surprisal; Hale/Levy/Michaelov) + the LIFG/semantic-P600 STRUCTURAL-conflict monitor (Thompson-Schill; Van Herten & Kolk). Surprisal is a RISK FLAG, not a verdict (parse-as-truth == the info-free null); the brain's action is withhold/re-read, NOT auto-revise (Ferreira/Gibson good-enough). THE WALL, decomposed + built-across 7 probes to an evidence-forced terminus: auto-revise FAILS (−0.002), and the DECISIVE test shows the reader's wrong pick is NO more similar to gold than a random competitor (0.221 vs 0.229) → the errors are STRUCTURAL (wrong entity), which is WHY every semantic signal fails (richer 1024-d space made it WORSE; the crude count beat the brain-faithful confusability). English who-did-what binds STRUCTURALLY → the residual is SILENT PARSE-COVERAGE failures, unflaggable by any plausibility/self-consistency signal → the sole lever is a better parser (the predictive parser, filed). WIRE: (a) the adjacent hdlab bug FIXED — `frame_induction.is_passive_real` bounded `range(lo, min(v_idx, len(tokens)))` (was IndexError ~1/1300 sentences). (b) `predict_surprisal` default-off flag QUEUED (WIRING_MAP; the first live node of the prediction-error hierarchy — needs an offline-fitted PredictiveReader asset + an additive EventRecord surprisal field; the live driver imports only promoted hdlab organs). Do NOT wire auto-revision (proven NEGATIVE).

- **2026-08-31 — 🧠 INTEGRATED (EXCELLENT): the BELIEF/ToM event source is NOT object-moves — it is a CONTENT-GENERAL, SOURCE-TAGGED propositional attitude fed by LANGUAGE ABOUT MINDS (4 channels).** Problem `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose`, reverified 19/19 first-hand. CORRECTS the §1 "ToM absent"/prior belief entries: the belief organs (`belief_timeline` sample-and-hold, `belief_partition`, `perceptual_access_ledger`) are PINNED-faithful + promoted, and their 0.902 was GOLD-fed/constructed — now DRIVEN from the reader's OWN extraction on a REAL POWERED population. FIDELITY CORRECTION (research drill, Koster-Hale 2017/2014; Saxe; Dodell-Feder 2011; Zwaan): the brief's Sally-Anne OBJECT-MOVE source is (a) empirically ~ABSENT from real prose (0 objects with ≥2 extracted moves / 8 LitBank books; ~1 move/book, mostly idioms) and (b) the WRONG mechanism — the object-move false-belief task is a developmental DIAGNOSTIC; the mentalizing network (TPJ/mPFC) holds a content-general, source-tagged propositional attitude fed by language about minds (channel-density: narrator-epistemic + testimony 4.2× object-moves). PINNED MECHANISM: drive belief from FOUR channels — narrator-epistemic + testimony (DOMINANT; belief VALUE read off mental/speech verbs, substrate-native, NO spaCy) + perception + INFERENCE (3-schema exclusion/transitive-spatial/modus-ponens, evidence-gated) — reality separate, ignorance = None (Butterfill & Apperly registration: knows/stale/ignorant). MEASURED on FANToM info-access ToM (Kim 2023, external, n=3572 judgments): reader 0.893 vs strongest floor 0.665 (+0.228 CI-sep), beats a shuffled-order twin (+0.138) AND a random-presence twin (+0.337) CI-sep, false-belief says-ignorant 0.939 vs beliefless 0.000; LitBank narrative slice corroborates (knowledge-state +0.429 CI-sep). Every extraction gap routed to a VETTED organ (status → `state_register`, recovers 0.60 > a stronger parser 0.40, NOT intrinsic; open-ended value → WordNet synonym+entailment, NOT the REJECTED `distributional_meaning_channel`/`conceptual_meaning` — vetting caught two wrong picks; location → the shared PARSER-RECALL ceiling, converges with SPACE → p2). WIRE: QUEUED (`track_belief` on SituationReader, the lazy-adapter track_space pattern; WIRING_MAP DEBT 2) — the reader lazily imports the experiment-side belief adapter (`_belief_reader` imports `experiments._space_reader` + `experiments.state_register`, so NOT a clean single-file promotion — the lazy adapter, like track_space, avoids that). A substantial multi-channel assembly landing = its own focused effort; flip-on default-off/owner-gated.

- **2026-08-31 — 🎯 INTEGRATED (STRONG): the learner runs ON CONTINUALLY and stays safe + beneficial at the brain-faithful EMA slow-anchor — extends the CLS safe-growth entry (§2b 08-25) from a fixed batch to a LIFELONG live canary.** Problem `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite`, reverified 7/7 first-hand. The anti-drift lever is ONE parameter — the slow anchor store's CONSOLIDATION RATE `eta`; read-out each round = keep-both(slow anchor, fast grown) via `hdlab.cls_growth`. CORRECTION: the offline aligned-continual "drift" (0.114→0.196) was an anchor-DECAY artifact (running fusion halves the anchor each round), NOT a ceiling. FIDELITY: a FROZEN anchor is only PARTIAL fidelity (word meaning is slowly + continuously updated over a lifetime — Winocur & Moscovitch trace-transformation); the faithful anchor is a slowly-consolidated small-`eta` EMA (Kumaran 2016 slow store; mean-teacher) — a COMPUTATIONAL-LEVEL SUBSTITUTE for synaptic consolidation (Fusi 2005 cascade / EWC 2017), reproducing anti-forgetting via an external slow store, honestly labeled. MEASURED (full 5M→15M, 6 rounds, two downstreams + a biology domain-shift round): the stability-plasticity FRONTIER — terminal corruption AND gain both rise monotonically with `eta`; the strict-safe `eta` (corruption CI-upper<0.15) is CORPUS-DEPENDENT (frozen on old fiction; ≤0.1 on held-out MODERN). All 5 gates pass on modern (corruption CI-upper 0.137; gain +0.110, twin loses; rollback protects, 16-seed random control fails; no drift); the EMA anchor holds under a NEW-DOMAIN shift with no extra drift while the no-anchor decay control worsens. HONEST negative (old-fiction EMA CI-upper 0.179>0.15) = a located statistical-POWER artifact (n_base_right=403), NOT drift (the DECAY control CI-sep worse at same n; reliability arm tested+rejected). WIRE LANDED (Q111): the anti-drift SLOW-ANCHOR primitive `align_and_fuse` (Procrustes-aligned keep-both EMA; alpha=`eta`) + `procrustes_rotation`/`_l2norm_rows` PROMOTED VERBATIM (byte-identical) into `hdlab/cls_growth.py` as a DEFAULT-OFF ISLAND, composing with the already-landed `make_ensemble_sim`+`rollback_gate` (witness `test_cls_growth_anchor_primitive_organ.py` 5/5 incl. byte-equality → faithful promotion, no drift; registered `cls_growth_anchor_primitive_v1`). The reader-side `learner_growth` read-out flag is BLOCKED on `reader_meaning_channel` (the live `read()` consults no meaning store) → NOT landed (documented, not faked). Flipping growth ON by default is a SEPARATE owner decision on this evidence.

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT — component scan of `information_foraging`, 0 prior audit coverage, verdict-independent): a HIGH-FIDELITY PINNED organ that is LEVERAGE-CAPPED downstream — and it CONVERGES with the definitional scan on the real bottleneck (CONSOLIDATION).** (a) FIDELITY: PINNED/HIGH — the Marginal Value Theorem patch-leaving rule (Charnov 1976; Constantino & Daw 2015 discrete form `kappa*s_i >= rho_i*h`; `rho` update; threshold-moves-with-environment Hayden 2011; two `rho` timescales Wittmann 2016), currency = uncertainty-reduction-per-effort (Oudeyer & Kaplan learning-progress = g'(t)). Overstaying is NOT hand-coded (normative optimum only; a structural self-test scans its own source for a bias term) — one of the ~5 organs that compute the brain's ACTUAL equation, the OPPOSITE of a placeholder. (b) GENERALIZATION/EFFICACY: WIRED (substrate slot H2 "what to read next + when to leave"; `corpus_registry` shelf; MVT leave on grounding-yield; registry `information_foraging_mvt_leave_rule` WIRED) — BUT `substrate.py` records a FIXED schedule OUT-SCORES foraging on reading yield (0.0743 vs 0.0617). NOT a fidelity failure: the binding constraint is DOWNSTREAM CONSOLIDATION (the integrated `the_reader_cannot_choose_what_to_read_next` diagnostic: 66% of words read ≥4× never ground; single-averaging consolidation is the wall). (c) WIRING: live. (d) GAP+LEVERAGE (HIGH, clean-foundation): the foraging organ is fidelity-COMPLETE; its leverage is capped by the consolidation/depth bottleneck. **CONVERGENCE:** TWO input-side organs now point at the SAME downstream wall — `definitional_extraction` (last round: writes garbage genus facts) and `information_foraging` (this round: can't beat a fixed schedule) — both bottlenecked on CONSOLIDATION (how encounters become durable, clean knowledge). With p3 having just PROVEN growth is SAFE, making growth STICK (retrieval-practice-not-reread, Karpicke & Roediger 2008; CLS interleaved replay) is the highest-leverage next clean-foundation problem — the natural brief for the vacant solver.

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT — component scan of `definitional_extraction`, 0 prior audit coverage, verdict-independent): the KB's definition-reader has ~0 PRECISION on NARRATIVE — it writes GARBAGE genus facts into `hd_fact_store` (the clean foundation the learner grows on).** This is the first audit of a LIVE organ (substrate slot R1 "read a definition out of running prose") that had NO coverage and NO witness. (a) FIDELITY: the FRAMING is PINNED and sound — explicit definitional learning is a fast single-exposure DECLARATIVE/hippocampal relational bind (definiendum↔genus), the one-shot half of the CLS pair vs the slow distributional cortical accumulator (`canonicalize`). But the EXTRACTION is OUR-INVENTION: surface regex patterns (COPULA/APPOSITIVE/GLOSSARY_COLON/CALLED/REFERS_TO) + a shallow right-most-noun-before-a-clause-boundary head heuristic (explicitly "not a parser"). The weak link is the APPOSITIVE/COPULA patterns have NO genus-plausibility / definiendum-novelty / genre gate. (b) GENERALIZATION — FAILS on the reader's own corpus (MEASURED this scan, `extract_definitions` over 8 LitBank docs / 726 sentences): 19 definitions fire (0.026/sent — definitions ARE rare in narrative) and ~ALL 19 are FALSE POSITIVES — the APPOSITIVE pattern matches ordinary narrative comma-NPs as if the second defines the first (`window→tripod`, `arm→nap`, `hall→better`, `girls→eldest`, `brother→baronet`, `hour→musician`; COPULA `vanity→beginning`). Positive control holds (expository `A nephron is the functional unit of the kidney` → `nephron→unit`, correct), so the organ is not broken — it is CORPUS/GENRE-MISMATCHED: built+exemplified on EXPOSITORY prose, precision ≈0 on NARRATIVE. This is the corpus-confound in a new place: a proper definition defines a NOVEL COMMON NOUN (nephron); narrative "X is/, a Y" predicates a property of a NAMED PARTICULAR (a character) = an entity-STATE, not a KB genus fact. The organ never had an organ witness (registry `witness=None`) and its 2026-08-12 validation note is a grounding-loop probe, not a precision/recall on real narrative → a constructed-domain organ never stress-tested on the reading corpus (owner rule: a constructed-domain win is not a capability until held-out). (c) WIRING: WIRED, NOT an island — substrate slot R1 → consumed by `hd_fact_store` (the KB) + `reading_grounding_loop` (definitional gate). So the false positives ACTUALLY reach the KB unless a downstream gate catches them; there IS a `reading_grounding_loop._make_definitional_gate` + a `low_information_filter_pmi_flatness_gate` (registry status VET_PENDING — unverified). The adjacent sibling `definitional_predicate_v61` is already EXCLUDED in the substrate ("fires on 1 of 375 definitional sentences — 0.27% of its population") — the opposite failure (recall≈0), so BOTH definitional organs are miscalibrated. (d) GAP + LEVERAGE (MEDIUM-HIGH, clean-foundation path): the gap is a DEFINITION-vs-narrative-predication PRECISION gate before the KB write — discriminate genus-DEFINITION (novel common-noun definiendum, taxonomic genus) from CHARACTERIZATION (named-particular definiendum → route to the p3 copular/nominal ENTITY-STATE dimension, HOLDER→PROPERTY, NOT a definition). Leverage: `definitional_extraction` writes to `hd_fact_store` = the clean foundation the learner-on program is GATED on; garbage genus facts ARE the "dirty foundation." So precision here directly serves the North-Star clean-foundation gate, and it composes with the already-built p3 copular/nominal STATE reader (the same "X is a Y" surface, disambiguated by definiendum type). Also owed: a real organ witness (precision/recall on narrative vs expository gold). NOT packaged (queue full: p2–p6); seeds a "gate the definition-reader / verify the downstream KB definitional gate actually suppresses narrative false-positives" problem when a slot opens. ⚠️ Honest scope: precision judged by inspection of the 19 firings (definiens spans truncated in the probe); the false-positive direction is unmistakable but a graded gold + the downstream-gate check would quantify it.

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT scan — the active-register tier of the binding backbone) — the reader's
  within-EVENT ROLE binding is ALREADY LIVE + PINNED; the p4 tiered-backbone should EXTEND it, not build from scratch.**
  De-risks the highest-leverage queued problem (`the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event
  _token`). (a) FIDELITY: PINNED — `event_bundle.encode_event` binds (PRED, AGENT, PATIENT, TENSE) into ONE joint token
  via the validated M1.7 role-slot binding [`event_vec = quantize(Σ_r bind(role_key[r], filler_r))`, glass-box unbindable];
  `situation_focus`/`ChunkedFocus` (Cowan 2001 ~4-chunk focus, PINNED) holds these bound event bundles as the active WM
  register. So the ROLE dimensions ARE bound (a JOINT token, not marginals) — the p4 silos are specifically the NON-role
  dimensions (causation / time / space / belief), computed as SEPARATE lists (`typed_causal_links` / `timeline_order` /
  `sm.locations`) and NEVER bound onto the event token. This SHARPENS p4: the fix is not "build a binding backbone from
  scratch" — it is EXTEND the existing role-bound event token to also carry causation/time/space (more role-slots on
  encode_event). (b) WIRING: `situation_focus` is WIRED (live in `_read_events`); `situation_model_multibank` is an ISLAND
  — and it is the EXACT capacity fix for the p4 1/√M collapse: it routes an entity's events across n_banks independent
  sub-bundles (per-bank load = events/n_banks) to avoid the single-superposition cross-talk wall (the measured decode
  regression 89.8%→67.2% when too many events cram one register). So the p4 "tiered, not one superposition" prescription
  maps to: SWAP the active register `ChunkedFocus` (superposition + chunking, collapses) → `situation_model_multibank`
  (slotted, flat). (c) GAP/LEVERAGE: the tiered-backbone = (i) EXTEND `encode_event` to bind the non-role dimensions onto
  the event token, (ii) SWAP `ChunkedFocus` → `situation_model_multibank` for the active register, (iii) + the
  `n400_coherence_monitor` boundary + `hippocampal_encoder` episodic tiers p4 named. The role-binding + capacity tiers are
  BUILT (one live, one island) — the solver builds ON them. Recorded for the p4 solver (verdict-independent).

- **2026-08-31 — 🧩 INTEGRATED (EXCELLENT): the assembled reader is N PARALLEL SILOS, not one integrated situation model
  — the defect is the BINDING PROBLEM (marginals vs joint); the fix is a TIERED bound-event-token backbone (all tiers are
  built islands).** Problem `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`, reverified 19/19 first-hand.
  FINDING (byte-exact): turning all dimension flags ON COMPOSES but does not BIND — perturbing the shared event set leaves
  every other dimension byte-identical (interaction exactly 0), with exactly ONE real interaction point (role-routing
  consumes the event set). So "no-regression" is TRIVIALLY true; composition-without-interaction is not integration. Each
  dimension stores the MARGINALS (set of agents/times/causes); nothing stores the JOINT (which-goes-with-which) — the
  BINDING PROBLEM. Demonstrated on the real FHRR algebra with a NON-GAMEABLE discriminator: bound JOINT token
  disambiguation 1.00 + binding-shuffle SENSITIVE; marginal SILO 0.44 (chance) + shuffle-INVARIANT (the first constructed
  proof failed honestly at type-cardinality 1). FIDELITY: PINNED — comprehension builds ONE bound event token indexed on
  all dimensions (Zwaan & Radvansky event-indexing; SEM/Franklin 2020), and the brain MUST CHUNK (a single passage
  superposition collapses ~1/√M [0.99@64→0.12@512]; a slotted multibank stays flat) → the faithful token is TIERED. NEW
  MAP (every tier is a BUILT hdlab ISLAND, none reader-wired): `slot_attention_wm`/`situation_model_multibank` (slotted
  active register), `n400_coherence_monitor` (prediction-error event-boundary flush/reset), `hippocampal_encoder`
  (DG-sparse + CA3 + CLS episodic store). INSTRUMENT-COUPLING (corrects a QA-capstone caveat): the QA temporal/causal
  golds derive from sm.events which the tense-agnostic keystone rewrites (temporal Qs 106→0) — an INSTRUMENT artifact, NOT
  a reader regression; the fix is reading sm.timeline_order (0.89 vs the broken 0.36). DG-WRONG-TIER REHAB: DG/hippocampal
  prior HARD_FAILs were on the active-read tier, NOT DG's faithful episodic-store job — do NOT re-quote as a ceiling.
  **🔗 RECONCILIATION (owner-prompted): this does NOT contradict the prior "separate stores are optimal" findings
  (`the_entity_store_is_a_dense_bundle_that_fans` factorized two-system; `one_store_does_two_jobs` sparse cortex; keep-both
  CLS) — those are separation by FUNCTION/TIMESCALE (KEPT by the fix); the silos here are the absence of within-EVENT
  BINDING (a different, orthogonal axis). And `dimensional_phase_diagram_audit` INDEPENDENTLY found the same wall ("the
  wall is front-end LINKING, not capacity"). Binding-within-an-event and separation-across-stores are complementary;
  the tiered-backbone fix keeps the validated slotted/factorized stores and ADDS within-event binding.** STRATEGIC
  REFRAME: the assembly is no longer "wire dimension N+1" — it is "assemble the tiered binding backbone so all dimensions
  bind to ONE event token" (packaged as the p4 problem, ranked above reasoning — a prerequisite for it). NO default
  flag-flip (only role_route is aggregate-positive + instrument-safe).

- **2026-08-31 — 🎯 INTEGRATED THE NORTH-STAR CAPSTONE (EXCELLENT): learn-by-reading turns ON safe AND beneficial on the
  clean foundation.** Problem `turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation`, reverified FIRST-HAND
  (8/8 full-solution + 5/6 core; see the honest discrepancy). FIDELITY: PINNED — Complementary Learning Systems keep-both-
  stores growth (McClelland/O'Reilly 1995); reliability-WEIGHTED fusion = optimal cue combination (Ernst & Banks 2002 /
  Friston precision) — the best operating point. MEASURED: a safe+beneficial on-state EXISTS at full scale (non-gated
  keep-both + reliability fusion, corruption 0.09–0.11 < the 0.15 pre-reg, +0.0596±0.0027 over 3 seeds all CI-sep, fix/
  break 9.4); the info-free growth twin HURTS (real learned structure, not more-words); rollback rolls back naive+
  adversarial (random control fails); generalizes to a 2nd task + survives the substrate's OWN arc_parser (no external
  tool at inference). NEW PINNED CATEGORY INSIGHT (a re-drawing of the map): schema-congruence GATING is CONFIRMATION-
  BIASED on the DISTRIBUTIONAL meaning learner (MORE corruption) but WORKS on the EPISODIC is-a fact-store (AUC 0.868) →
  schema-gating belongs on the fact-store, NOT the learner. HONEST BOUNDARY (names the remaining half of the mission):
  growth helps SIMILARITY-reducible comprehension strongly (+0.06 paraphrase) but inference MC-QA only marginally (+0.005,
  MCScript2) — REASONING (the situation-model half) is the North Star's remaining frontier. ⚠️ Honest reverify: 5/6 core
  (the 1 non-reproducing check is "CLS_CLEAN beneficial" at smoke — the schema-gated arm bar-5 refutes, so consistent;
  the "every keep-both arm" headline is thereby slightly overstated). **STATUS: the CAPABILITY is PROVEN + INTEGRATED;
  the default-off CLS safe-growth SWITCH landing is QUEUED (store-touching, careful); flipping growth ON live is a
  SEPARATE owner-gated step. The learner is un-gated on evidence.**

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT scan — the next assembly dimension: BELIEF/ToM) — `belief_timeline` +
  `perceptual_access_ledger` are PINNED-faithful + promoted but a PURE ISLAND, and their validation rests on GOLD events +
  CONSTRUCTED passages — so wiring them is a SOLVER end-to-end problem (the SPACE template), NOT a clean landing. CORRECTS
  the §1 "ToM absent" (stale) AND the FORWARD_BACKLOG "mostly my-landings" (wrong).** (a) FIDELITY: strongly PINNED —
  per-agent belief kept SEPARATE from reality (TPJ/mPFC mentalizing; Saxe & Kanwisher 2003), updates ONLY on OBSERVED
  events (seeing→knowing; Wimmer & Perner 1983), composed as a PIECEWISE-CONSTANT sample-and-hold over story-time
  (default-persist/temporal inertia; Dowty 1986 — the same persistence SPACE + entity-state use) read at the query time,
  with event ORDER from the (landed) temporal-order register. A faithful GENERALIZATION of `belief_partition` from n=1 to
  n changes. The observation front-end is a STICKY REGISTRATION LEDGER (Butterfill & Apperly 2013), not a boolean re-
  evaluated at query time — a well-drilled replacement for the naive keyword extractor (0.808). (b) GENERALIZATION — the
  gap: `exp_belief_timeline_live_e2e_v1` scores 0.902 "live" on AUTHOR-CONSTRUCTED multi-event passages where the EVENTS
  are GOLD (anchored by sent_idx) and only the observation-BIT is extracted live (arms LIVE/ORACLE/FLOOR). So the belief
  timeline has NEVER been driven end-to-end from the reader's OWN event extraction on natural narrative — the number is
  belief-composition-over-gold-events + a live observation-gate on constructed prose. (c) WIRING: grep 0/0 — not imported
  by situation_reader/substrate; no live hdlab consumer. PROMOTED (DEBT-1) but UNWIRED (DEBT-2 pending). (d) GAP/LEVERAGE:
  ALL pieces are promoted/landed (belief_timeline, belief_partition, perceptual_access_ledger, the timeline_register for
  ORDER) EXCEPT the composition INTO the live reader driven by its OWN extraction. So the next Phase-B problem is a SOLVER
  END-TO-END VALIDATION (like SPACE): does composing the reader's own event stream → timeline_register → perceptual_access
  observation-gate → belief_timeline answer "what did A believe at T" on REAL narrative, CI-sep over floors, twin losing?
  The extraction front-end is now much stronger (keystone + copular/nominal + verb_subcat), so it MAY now be feasible — but
  it must be MEASURED on real prose, and the likely limiter is the same parser-recall ceiling SPACE hit. **Recorded, NOT
  packaged (queue full: p1/p2/p4). Seeds the next Phase-B problem when a slot opens.**

- **2026-08-31 — INTEGRATED (SPACE, STRONG): the reader gains its 4th situation-model dimension (WHERE) end-to-end on real
  prose; the deep finding CONVERGES with the prediction-error scan.** Problem `the_reader_has_no_spatial_location_dimension
  _end_to_end`, reverified 13/13 first-hand. FIDELITY: PINNED — per-entity LOCATION as STATE updated by motion events and
  PERSISTING between updates (Zwaan & Radvansky event-indexing SPACE; categorical/topological nodes, Rinck) — confirmed by
  the 63× persistence distance-signature. NEW PINNED (built + measured): noisy-channel comprehension = parse-as-EVIDENCE
  fused with a persistence PRIOR, NOT parse-as-truth (Levy/Gibson; hippocampal pattern-completion) — decisively: parse-as-
  TRUTH sits AT the info-free null (0.111 vs p95 0.112) and a stronger general parser (spaCy) does NOT beat the in-substrate
  prior, so the LEVER is the PRIOR and the ceiling is parser RECALL (the LIKELIHOOD term), not parse quality; embedded SPACE
  updates gated by VERIDICALITY (Kuperberg P600); caused-motion relocates the THEME (Goldberg); goal-bias is animacy-
  modulated (Lakusta & Landau 2012). MEASURED deviation: extraction recovers ~25→35% of true motion events on real prose.
  **🔗 CONVERGENCE (load-bearing): SPACE arrived — through a DIFFERENT dimension — at the SAME conclusion as the
  predictive_reader scan below: the ceiling is the missing FORWARD-PREDICTION / predict-and-revise prior. Two independent
  dimensions pointing at one gap is why the prediction-error first step was PACKAGED (`the_forward_prediction_organ_is_inert
  _wire_its_surprisal_into_a_live_decision`, p2).** LANDING QUEUED (`track_space` default-off flag → sm.locations). The
  situation-model dimension count is now: entities/coref, TIME, CAUSATION, SPACE (4 of the 5 Zwaan dimensions wired-or-
  queued; BELIEF/ToM promoted-but-unwired).

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT scan — the FORWARD half of predictive coding) — `predictive_reader` is
  PINNED-at-computation + held-out-validated but a PURE INERT ISLAND (never computed on any live path); sharpens the
  prediction-error direction with concrete wiring reality.** Scanned the word/feature-level forward predictor.
  (a) FIDELITY: the CORE COMPUTATION is PINNED — forward prediction / pre-activation of expected GROUNDED features, the
  error IS the signal, surprisal = −log P under softmax competition (Hale 2001; Levy 2008; Michaelov 2024 — LM surprisal
  is the best single account of the N400); predict MEANING features not word-FORM (Nieuwland 2018); precision-weighted by
  selectional-preference concentration (Friston constraint strength). INVENTION-under-test (swept, honestly labelled): the
  role-specific centroid instantiation, the softmax temperature, the grounded space as feature basis. (b) GENERALIZES:
  real held-out QA-SRL — predictive surprisal beats reactive +0.199 and an info-free wrong-verb twin +0.095; the frequency
  confound excluded THREE ways; surprisal tracks distributional thematic-fit Spearman 0.239; discriminates reversible role
  assignment AUC 0.619. Honest modest size (12-dim grounded ceiling — the isolation effect is a graded SIGNAL, not a
  standalone accuracy lift). (c) WIRING — ENUMERATED (not a single grep): the ONLY hdlab reference is
  `incremental_parser.py`, which imports `PredictiveReader` as an injectable TYPE (`predictor: Optional[PredictiveReader]
  = None`) and runs the structural core with prediction INERT when `predictor is None` (the default). `situation_reader`
  and `substrate` do NOT import it; no live caller ever CONSTRUCTS/injects a predictor, and `incremental_parser` is itself
  default-off. So predictive_reader's surprisal is NEVER computed on any live reader path -- a PURE INERT ISLAND (the
  registry's `integration_status: WIRED` means promoted+registered, NOT called-at-inference; strict status = ISLAND).
  (d) GAP/LEVERAGE: this is the FORWARD half of predictive coding; `n400_coherence_monitor` is the BACKWARD event-coherence
  half (also default-off), `slot_attention_wm` the WM-gating level (island), and `gap_detector` the memory-novelty level
  (wired but ablation-AMBIGUOUS). So the substrate has BUILT the prediction-error hierarchy at 4 levels but 3 are inert
  islands and the 1 wired node does not demonstrably fire a decision. The organ's docstring names its live value: a graded
  difficulty/anticipation SIGNAL that should feed write-gating / N400 confidence / the relcl route-conflict — NONE of which
  consume it today. **This CONCRETELY confirms the roadmap's "prediction error is the biggest fidelity-vs-wiring gap"
  synthesis. NOT packaged: it is a COORDINATED program (wire the forward signal into a downstream decision + prove the gate
  fires with a positive control), owner-direction-pending per `LEARNER_ON_ROADMAP.md`; the queue is full + correctly ranked.
  Surfaced for the owner's DIRECTION call.**

- **2026-08-31 (strategy, ARCHITECT HEARTBEAT scan — the who-did-what IDENTITY half) — `graded_role_assigner` is
  PINNED-faithful, held-out-validated, and WIRED on the assembly path (NOT an island); the who-did-what stack is now
  coherently wired.** Scanned the IDENTITY organ adjacent to the PRESENCE gate just landed. (a) FIDELITY: PINNED —
  role assignment is graded, PARALLEL cue integration (MacWhinney & Bates Competition Model; the additive-cue→softmax
  IS the Bayesian posterior, McClelland 2013; runs over the landed `graded_competition`). The load-bearing fidelity
  insight is ROUTE-DON'T-REPLACE: a flat integrator is NET-NEGATIVE (wrecks canonical), so `hybrid_role_patient` keeps
  `resolve_patient` byte-identical on confident/canonical routes and invokes the competition ONLY on the non-canonical
  fall-through (strong passive / relativizer-less object gap / unaccusative sole theme). Faithful. (b) GENERALIZES: real
  held-out (n=4078 role_balanced gold): +0.0242 CI-sep on the non-canonical slice, net-positive +0.0113 overall, canonical
  PRESERVED, shuffled-validity twin LOSES, seed-robust. Honest modest magnitude. (c) WIRING — CORRECTS a likely "island"
  read: `situation_reader` reaches it on the OPT-IN `role_route != "positional"` assembly path (`_read_events_wired` →
  `_router_roles` → `route_predicate_arguments` [predicate_argument_frontend, live] → `hybrid_role_patient`). The DEFAULT
  reader (positional) does NOT use it. So it is ASSEMBLY-wired, not a hard island (wiring_debt's direct-import scan
  undercounts it — like arc_parser, read "import-reachable / assembly-active"). (d) GAP/LEVERAGE: the just-landed
  `verb_subcat_gate` (PRESENCE) is a POST-READ pass → it composes with BOTH the positional and the assembly IDENTITY
  paths. So the who-did-what stack is now coherent: PRESENCE (verb_subcat, wired simple / graded queued) × IDENTITY
  (graded_role_assigner, assembly-wired, faithful) × ENTITY (coref, 3× solved). The organ's OWN named residual —
  reduced-relatives needing "verb-subcat SUPPLY" — is now partly supplied (verb_subcat landed). **No new problem: the
  full-stack ALL-FLAGS-ON composition + measurement is exactly the OPEN p4 `the_assembled_reader_is_never_tested_as_a_whole`
  (WIP by a solver) — this scan CONFIRMS p4 is the correct validation gate and the queue is right. The remaining fidelity
  ceiling is the GRADED verb_subcat upgrade (queued, DEBT 2).**

- **2026-08-31 (strategy, Q111, ARCHITECT HEARTBEAT) — LANDED: `verb_subcat` wired into the live reader (default-off
  `verb_subcat_gate`) — the who-did-what PRESENCE half now reaches the reader.** Promoted the p2 reference organ →
  `hdlab/verb_subcat.py`; the reader suppresses a spurious patient on low-transitivity verbs (post-read transitivity gate,
  the version validated through read(): patients 147→112, == SubcatGateReader byte-for-byte). FIDELITY: PINNED basis
  (verb subcat is stored lexically — Levin/VerbNet — AND learned distributionally — Trueswell/Garnsey verb bias; the
  dual WordNet-frame + corpus P(obj|verb) asset). **DEVIATION FLAGGED: the wired gate is the SIMPLE lexical-propensity
  threshold, NOT the brain-faithful GRADED Competition-Model cue integration (`patient_present`, the softmax posterior
  that WON on QA-SRL, 0.30→0.49). The graded gate is the higher-fidelity target; it is UNWIRED because the reader does
  not yet expose POS + the patient token index at role-assignment time — a mid-`_read_events` plumbing gap (WIRING_MAP
  DEBT 2). So this landing closes the ISLAND (verb_subcat now reaches the reader) but the FIDELITY ceiling is the graded
  upgrade.** The three-way who-did-what decomposition is now: PRESENCE (verb_subcat, wired simple / graded queued) ×
  IDENTITY (graded_role_assigner) × ENTITY (coref, 3× solved). Registered `verb_subcat_gate_live_reader_v1`.

- **2026-08-31 — INTEGRATED (p2 EXCELLENT): the incremental parser as a ROLE lever is a fidelity ERROR; the real who-did-what
  precision lever is verb-SUBCATEGORIZATION.** Problem `wire_the_incremental_parser_as_the_reader_extraction_front_end`, reverified
  16/16 first-hand. (i) `incremental_parser_v1` — precision-only (incremental vs batch +0.145 P / +0.093 F1 CI-sep), NO role gain;
  restricting the role binder to the parser's bounded buffer LOWERS patient acc 0.726→0.696 (a recall/fidelity error). PINNED brain
  fact: role-binding is a SEPARATE cue-based retrieval stream with independent input access (Frankland & Greene 2015; Lewis &
  Vasishth 2005; McElree 2006) — structure-BUILDING and role-BINDING are distinct organs (Beber 2025), so hard-restricting the
  binder to the builder's set is un-faithful. Verdict: keep the incremental parser DEFAULT-OFF precision-only; NOT the role lever;
  no dead role-flag (registry note corrected). (ii) NEW organ `verb_subcat_v1` (reference `experiments/ref_verb_subcat_organ_v1.py`,
  BUILT/UNWIRED, WIRE_CANDIDATE default-off) — the who-did-what PRESENCE half: a graded Competition-Model presence gate over a dual
  WordNet-frame + corpus-P(obj|verb) basis (Levin/VerbNet lexical + Trueswell/Garnsey distributional). AUC ~0.78–0.81 CI-sep over a
  hard subcat gate AND pure syntax; who-did-what id 0.30→0.49 (do-no-harm); twin ~0.5; unknown-verb safe. FIDELITY: PINNED mechanism
  (subcat stored lexically + learned distributionally; presence = graded cue integration = the same softmax/Bayesian posterior as the
  deployed binder). The three-way who-did-what decomposition is now explicit: PRESENCE (verb_subcat) × IDENTITY (graded_role_assigner)
  × ENTITY (coref).

- **2026-08-31 — INTEGRATED (p5 STRONG): the event detector now preserves TENSE compositionally (Reichenbach), unblocking a shared
  event set for the TIME dimension.** Problem `the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension`, reverified 12/12
  first-hand. FIDELITY: PINNED — event DETECTION stays tenseless (neo-Davidsonian event variable, Bach 1986), and temporal LOCATION is
  a SEPARATE compositional parse of the verb group (main verb + auxiliary chain) into a Reichenbach tense × aspect × voice triple
  (Reichenbach 1947; Zwaan & Radvansky TIME; LAN→P600 / LIFG composition) — reading the same morphosyntax the language network reads.
  In-substrate word-tense 0.770 CI-sep over placeholder/majority/twin; aspect 0.987 / voice 0.933; recall preserved EXACTLY (tense is
  a label on already-detected tokens → free). NEW PINNED sub-mechanism: non-finite forms carry no independent tense and INHERIT it from
  the controlling finite verb (sequence-of-tense; Ogihara/Abusch) — the apparent "wall" was a category error, dissolved by mark-and-
  inherit (oracle-anchor 0.876 = the finite ceiling). REFINEMENT to the keystone's boundary note: the tense-preserving variant it
  called for now exists; landing it (QUEUED, default-off) lets the TIME dimension consume ONE is_pp-faithful event set.

- **2026-08-31 — INTEGRATED (p3 EXCELLENT): event-detection COMPLETENESS — copular STATES + deverbal NOMINAL events recovered
  tense-agnostically.** Problem `the_event_detector_misses_copular_and_nominal_predication_events`, reverified 14/14 first-hand.
  FIDELITY: PINNED — event-hood is NOT verb-slot-bound (neo-Davidsonian; Bach 1986). COPULAR = a distinct KIMIAN STATE (Maienborn 2005)
  read off the droppable-copula `cop` DEPENDENCY relation (binding HOLDER+PROPERTY, Bemis & Pylkkänen LATL) — recovered CLEANLY (UD
  recall 0.7951→0.9448 +0.1497 CI-sep, cop-class precision 0.857). DEVERBAL NOMINAL events route through the verb machinery (Garbin 2012)
  via event-denoting-ness (WordNet ATL) + argument structure (Grimshaw LIFG) + boundedness (Hopper foreground) — recovered with a recall
  win (LitBank +0.0873, MAVEN cross-corpus +0.1845 CI-sep) but a context-bounded precision. NEW PINNED deviation: the bare-nominal
  event/kind decision is intrinsically DISCOURSE-MODEL-BOUND (episodic event-token individuation, Renoult & Rugg; 3 local proxies
  can-fail-tested, none crosses) → the faithful fix is the incremental parser + situation model, not a static cue. REFINEMENT to the
  keystone's "parser too noisy at UAS 0.79" verdict: fidelity is RELATION-DEPENDENT — the `cop` relation is HIGH-fidelity (0.857) even at
  UAS 0.79 (local relations recoverable). The reader's ENTITY-STATE dimension (HOLDER,PROPERTY) is built + validated (de-risks the
  copular consumption) but UNWIRED into the live reader (QUEUED with the copular/nominal landing).

- **2026-08-31 — LANDED (strategy, Q111, owner-authorized assembly): the TIME dimension is now WIRED INTO the canonical reader
  (default-off `timeline_register` flag) — the 2nd assembly (DEBT 2) dimension, after causation.** The reader gains an ADDITIVE
  `sm.timeline_order` (whole-passage chronological event order incl. flashbacks) via the validated temporal-order register
  (`experiments/_temporal_order_register.py`, lazily imported). FIDELITY: PINNED — whole-passage temporal-order reconstruction
  (Zwaan & Radvansky TIME; Reichenbach) via a toposort of tense/aspect + connective constraints + the clause-level PLUPERFECT
  binder (recovers flashbacks the narrow per-sentence "had"-gated `_read_timeline` drops). This directly closes the fidelity gap
  the earlier TIME scan named (`_read_timeline` = a narrow "had"-gated flashback detector). DEFAULT OFF = byte-identical (the
  register is NOT imported; `_read_timeline`/`sm.timeline_frames` untouched). VERIFIED: witness PASS first-hand — flag-on
  `timeline_order` == the register's own output byte-for-byte (faithful, no new logic), a pluperfect flashback correctly
  reordered (chrono hidden→opened→read vs narration opened→hidden→read); causation witness still 3/3 (additive edit, no
  regression). NO spaCy (uses the substrate's own temporal front-end), NO LLM. Registered `timeline_register_live_reader_v1`.
  ⚠️ SCOPE: additive whole-passage ORDER field; it does not yet REPLACE the per-sentence timeline_frames nor feed `_read_causation`
  (both are the register's fuller wiring, a follow-on). The register stays experiment-side (lazy) — its hdlab promotion (~25
  importers) is a separate nicety, not required for the reader wiring.

- **2026-08-31 — INTEGRATED (p4, owner-DONE, EXCELLENT): a brain-faithful within-store CONSISTENCY-CLEANUP organ (schema-
  congruence) detects injected wrong facts CI-separated over every floor + the twin — the North-Star DOWNSTREAM clean-foundation
  half. With p4 done, BOTH clean-foundation halves are solved.** Reverified 15/15 first-hand. FIDELITY: PINNED — schema-
  congruence / conflict monitoring (ACC/mPFC; van Kesteren; Ghosh & Gilboa) + CLS + Friston precision + assimilation-to-gist
  (Winocur & Moscovitch). The gap it fills is exact: source-trust INGEST-VET is stuck at 0.500 (it cannot pick which side of a
  conflict is wrong; all 101 injected facts survive it) and a frequency/degree prior LOSES (0.325). EXEMPLARY SELF-CORRECTION
  (outranks its headline): a leave-one-out audit showed the relational (member-Jaccard) arm leaks the subject's own membership →
  collapses to chance under strict subject-LOO (0.522); the honest LOO-CLEAN signal is the CONTEXT/distributional arm (0.770).
  KEY STRUCTURE: consistency is a DENSITY PHASE TRANSITION (chance below indep-pair-fraction ~0.2, near-perfect above); the real
  definitional store is SUBCRITICAL (0.036), so densifying the foundation with WordNet hypernym chains (an ADMISSIBLE static
  offline asset — the foundation-is-free pivot; glass-box, NO LLM) crosses the boundary → far AUC 0.8826 (twin 0.5745) / near
  0.7967 LOO-clean. Plus a coherence CONFIDENCE tier + INSUFFICIENT_SUPPORT verdict + schema-based CORRECTION (assimilation-to-
  gist 0.979 vs 0.042). HONEST BOUNDS (reported): conditional on a dense-enough store; demonstrated on is-a/taxonomic facts.
  LANDING QUEUED (Q111): a consistency-cleanup pass over `hd_fact_store` (LOO-clean scorer + confidence tier + INSUFFICIENT_
  SUPPORT, WordNet-densified, default-off; STORE-write hazards apply). **🎯 NORTH-STAR MILESTONE: BOTH clean-foundation halves
  now solved — extraction-in (p1, landed) + consistency-of-stored (p4) — the gate the learner-on program was waiting on.**

- **2026-08-31 — LANDED (strategy, Q111, owner-authorized): the CAUSATION dimension is now WIRED INTO the canonical reader
  behind a default-off `causation_typed` flag — the FIRST assembly (DEBT 2) dimension in the live reader.** The reader gains
  `sm.typed_causal_links` (CAUSE/ENABLE/PREVENT + endstate) via `hdlab/causation_typing.py`, composing the validated force-
  dynamic typer (p2) + graded Hopper-Thompson event-hood gate (p3). FIDELITY: PINNED — Talmy/Wolff force dynamics (patient-side
  force-sum types CAUSE vs ENABLE vs PREVENT within a clause) + Hopper-Thompson transitivity/grounding (only a foregrounded
  event is a causal-arc candidate). Promoted `force_dynamics_lexicon` + `patient_tendency` → hdlab; created
  `hdlab/causation_typing.py`. DEFAULT OFF = byte-identical (no spaCy/experiment import on the default path). VERIFIED: the port
  is BYTE-IDENTICAL to the validated `WiredCausationReader` across 11 configs (constructed + full LitBank), and the witness
  `test_causation_typed_landing_organ.py` confirms end-to-end through the canonical reader (off byte-identical; flag fires
  flood→CAUSE/let→ENABLE/prevent→PREVENT; canonical == validated byte-for-byte) → inherits p2's within-clause AUTO 0.833 and
  p3's open-text precision gate (`causation_foreground_gate=True` opt-in). ⚠️ SCOPE (honest): the WSD/literalness chain
  (`frame_sense_disambiguator` → `idiom_gate`/`sense_selprefs`/`context_prior` + `_literalness_gate`, ~2000 lines) STAYS in
  experiments/ and is imported LAZILY only when the flag is on — its own separate queued promotion
  (`no_glass_box_verb_sense_disambiguation`), NOT dragged into hdlab. spaCy/nltk are permitted (not LLMs) and load only when the
  flag is on. Registered `causation_typed_live_reader_v1`. This is the first burn-down of the ASSEMBLY the owner authorized;
  the next assembly dimensions (temporal/state/space/roles) follow the same default-off pattern.

- **2026-08-31 — INTEGRATED (p3, owner-DONE, STRONG): a GRADED Hopper-Thompson event-hood gate raises open-text causal-link
  PRECISION over both floors with recall held EXACTLY — the Stage-1 foreground filter the p2 causation drop named.** Reverified
  11/11 first-hand. PINNED: only FOREGROUNDED, high-transitivity events are causal-arc candidates (Hopper & Thompson 1980
  transitivity/grounding; the three cleanest legs — ASPECT + INDIVIDUATION + REALIS — with naming/stative vetoes). precision
  0.3015→0.3818 vs ungated (+0.0803 CI-sep) AND vs the p2 dep-label stopgap 0.2970 (+0.0848); recall held EXACTLY (p2 n=42
  0.8333==0.8333) where the stopgap regressed to 0.810; the info-free shuffled-event-hood twin (abstention COUNT held constant)
  LOSES (+0.0801 CI-sep) — excludes the abstain-more confound; removal analysis 84.5% non-events (base 30.1%). GENERALIZES
  (owner-priority): CI-sep across genre + held-out doc halves + CROSS-CORPUS on MAVEN/Wikipedia different-scheme (+0.0266).
  Additive/byte-identical base. Honest self-correction (dropped weak grounding + sense-gate-redundant legs → lift more than
  doubled; leg alignment independently justified, aspect fg/bg gap +0.337 vs grounding +0.009). LANDING QUEUED, COUPLED with the
  p2 causation landing (one default-off `causation_typed` path: Stage-1 foreground gate → Stage-2 force typer; do NOT land the
  gate alone). Honest bound: absolute open-text precision still ~0.38 (removes 35% of the over-fire; residual is the next lever).

- **2026-08-31 — INTEGRATED (p6, owner-DONE, STRONG, rigorous NEGATIVE): retrieval interference among similar memories is
  confirmed to be similar-competitor cue-overload (NOT event-count) — the right-axis organ ALREADY EXISTS and both candidate new
  cues are rigorous negatives; the residual is STRUCTURAL. NO reader landing.** Reverified 18/18 first-hand (held-out LitBank
  pronoun coref n=3,378). REFRAME CONFIRMED: the who-did-what event-count proxy content floor 0.398 and naive recency TIE (0.402)
  — interference is content×context, not count. The landed `graded_antecedent_pick` owns the axis (0.676 vs content 0.521,
  +0.155 CI-sep; shuffled-context twin loses). BOTH new cues RIGOROUS NEGATIVES: the brief's multi-timescale TCM context adds
  -0.001 NOT_SEP; gender's marginal over the already-landed PERSON cleanup is +0.003 NOT_SEP (number +0.004) — vindicates the
  landed organ's own "gender is a non-lever" note. RESIDUAL IS STRUCTURAL: reachable ceiling 0.921 (7.9% cataphora unreachable),
  72% of errors gold-present-but-not-most-accessible, two combiners (additive 0.650 / Boltzmann 0.659) converge ~0.10 below the
  oracle-of-cues 0.763 (combination rule is not the bottleneck — the info isn't in these cues). Self-corrected a v7 person/gender
  conflation via a PERSON-vs-GENDER decomposition. NO hdlab landing (both new cues negative; right organ already landed) — the
  route "add a memory-axis cue to beat retrieval interference" is CLOSED; the residual is a Centering/accessibility ranking
  problem, recorded in WIRING_MAP non-debt.

- **2026-08-31 — COMPONENT SCAN + WIRING CORRECTION (strategy, verdict-independent): `arc_parser` is conditionally imported
  behind the DEFAULT-OFF `role_route` flag (not default-live — a wiring_debt static-scan overcount), it is a UAS~0.79 BATCH
  parser (not brain-faithful), and it is the SHARED parse front-end that both the assembly role path AND the learner-on
  structured-context channel depend on — so p2 (incremental parser) is a shared prerequisite for both.** (a) FIDELITY: a
  glass-box hashed arc-factored AVERAGED-PERCEPTRON dependency parser (per-arc best-minus-second margin = a calibrated abstain
  signal — a nice glass-box feature). But an arc-factored BATCH parser is NOT how the brain parses (the brain is INCREMENTAL,
  left-to-right — exactly p2's thesis); it is an OUR-INVENTION engineering parser, a means to get dependency structure, not a
  brain-mechanism claim. (b) GENERALIZATION: reproduces exp_depparse_hashed_cpu_v1's UAS ~0.79 on UD-EWT — mediocre (modern
  parsers hit 0.90+), and this 0.79 is exactly the ceiling the p1 keystone flagged ("precision is gated on PARSER FIDELITY…
  works at gold accuracy, not UAS 0.79"). (c) WIRING — CORRECTION to my own prior "islanded" shorthand: `situation_reader`
  imports `ArcParser` via `_load_frontend()` ONLY when `role_route != "positional"` (the opt-in assembly path); the DEFAULT
  (`role_route="positional"`) never loads it (positional role assignment, no parse) → byte-identical default. So it is an
  OPT-IN, default-off organ, NOT default-live. ⚠️ wiring_debt's static import-scan counts the import LINE as "live", so its
  "19 live imports" OVERCOUNTS the true DEFAULT-live set (it includes flag-gated default-off imports like arc_parser) — read
  that number as "import-reachable", not "default-active". (d) CROSS-CUTTING LEVERAGE: `arc_parser` is the CURRENT parse
  front-end for BOTH (i) the assembly role path (opt-in) and (ii) the learner-on STRUCTURED-CONTEXT channel (last round's
  finding — the dependency-typed learner needs a parse). p2 `wire_the_incremental_parser…` (validated +0.0352 F1 over this
  batch parse, brain-faithful incremental) directly addresses BOTH of arc_parser's weaknesses (not-incremental + UAS-0.79-cap)
  → p2 is a SHARED PREREQUISITE for the assembly AND the learner-on landing, which reinforces its priority-2 ranking. NOT a
  fresh problem (p2 already covers it); recorded to correct the wiring count + strengthen p2's cross-cutting rationale.

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent, CONFIRMATORY + CONNECTIVE): `reading_grounding_loop` (the
  North Star's learn-by-reading ENGINE) is a PINNED, wired, honestly-controlled mechanism; its Route B store is the SAME
  reading spoke that feeds `meaning_fusion` — so the meaning read-out and the learner's grounding foundation share it. No fresh
  gap; the "foundation too noisy" bottleneck is downstream QUALITY (p4 territory).** (a) FIDELITY: PINNED — fast-mapping + slow
  statistical accumulation (ATL semantic hub: repeated coherent CONTEXTS of use, not one-shot; Distributional Hypothesis, Firth
  1957). It reuses the validated FLAG→LIBRARY→CONSOLIDATE→GATE→BANK→PROMOTE architecture (grounding_acquisition_loop,
  HARD_PASS-validated for valence); since general word-meaning has NO polarity vote, the vote-margin gate DEGENERATES to a pure
  EXPOSURE gate (≥MIN_CONFIRM=4 occurrences), and the grounding decision rides on `schema_consistency_split_half` — does a
  word's context-of-use COHERE across INDEPENDENT encounters (split-half reliability; Warren 2014 coherence-not-vote-agreement
  guard). Exemplary honesty: it explicitly frames itself as a DELIBERATELY STRONGER re-test of a prior AUC-0.527 negative
  (diagnosed as exposure-volume/diversity-limited on a 1685-token homogeneous passage, NOT impossible — the USER
  narrow-failure-≠-impossible discipline) with ~2 orders more text + diverse registers + a SCRAMBLE-CONTEXT control. (b)
  GENERALIZATION: the engine is proven-in-principle (the learner is PROVEN-but-OFF); its OUTPUT cleanliness is the open question,
  not the mechanism. (c) WIRING: WIRED — a LIVE entry point (substrate slots P3 "provenance", B3 "many encounters → a concept",
  FILLED). ⚠️ Route B (the SEPARABLE co-occurrence store, `track_context_counts`/`observe_context_counts`) is DEFAULT-OFF
  (byte-identical when off) and turned on for the OFFLINE meaning build — correct (consolidation is slow, run offline). (d)
  CONNECTIVE FINDING (no fresh problem): Route B IS the reading spoke `meaning_fusion` consumes — so last week's conceptual-
  channel landing (into meaning_fusion) and the learner's grounding foundation share this substrate; AND the grounding criterion
  (exposure + split-half COHERENCE across encounters) is itself a form of CONSISTENCY — it relates to p4 (knowledge-store
  consistency-cleanup), which handles the "foundation too noisy" downstream QUALITY that keeps the learner OFF. Confirmatory:
  the learn-by-reading engine is sound and wired; the bottleneck is the cleanliness of what it grounds (p4), not the engine.
  NOT packaged (queue full).

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent): `gap_detector` is a PINNED CA1 match/mismatch NOVELTY comparator
  that IS wired (substrate H1) — but its downstream effect is ablation-AMBIGUOUS, and it is itself a PREDICTION-ERROR organ,
  which sharpens the synthesis: the substrate computes prediction error at FOUR levels; three are islands and the ONE wired one
  may be functionally disconnected.** (a) FIDELITY: PINNED and sophisticated — CA3/DG pattern completion (iterative_attractor,
  imported verbatim) picks the best-matching known fact; the margin is the cosine between the probe and that match read BEFORE
  the attractor settles (a post-settle read would trivially converge and be uninformative — a subtle error correctly avoided).
  This is the hippocampal CA1 comparator / novelty-detection mechanism (Lisman & Grace 2005): expected/retrieved vs actual/
  incoming. The codebook rebuilds from `HDFactStore.live_facts()` (consolidation-status-aware), so it tracks the store's real
  state. (b) GENERALIZATION: MECHANISM self-tests only (known-exact margin=1, wholly-novel low, 2-of-3 intermediate, ablation
  collapses, scramble flips, empty-KB all-gap) — construction-proven, not held-out-at-scale. (c) WIRING: WIRED (substrate slot
  H1 "do I already know this"; built by ReadingLoopState). ⚠️ BUT substrate.py records that ABLATING gap_detector ALONE CHANGED
  NOTHING (moved no counter) — it fires, but its downstream effect on the read-out is ambiguous (cannot distinguish "does
  nothing" from "switch did not fire"; the same class as the consolidation written-but-never-read finding). (d) THE SYNTHESIS
  EXTENSION (high leverage): gap_detector is a PREDICTION-ERROR organ (novelty = my memory did not predict this incoming fact).
  So the substrate computes prediction error at FOUR levels — forward-semantic (`predictive_reader`), event-coherence
  (`n400_coherence_monitor`), WM-gating (`slot_attention_wm` PBWM), and memory-novelty (`gap_detector` CA1). THREE are islands;
  the ONE that is wired (gap_detector) is ablation-AMBIGUOUS. So prediction error is both UNDER-WIRED and, where wired, possibly
  functionally INERT. AND this one is the LEARNER-ON GATE (gap → gather → learn): if the gap signal does not reach a downstream
  decision, the learn loop is disconnected. The missing measurement = a POSITIVE CONTROL that forces the gap switch to fire and
  shows its output changes a downstream decision (distinguishing inert from not-fired). ⚠️ Intersects the heavily-worked
  consolidation/ablation findings — do NOT re-package naively; it sharpens the prediction-error direction (the biggest lever),
  it is not a fresh standalone problem. NOT packaged (queue full).

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent, CONFIRMATORY): `hippocampal_encoder` is a PINNED, faithful CLS
  primitive that IS wired into the live substrate — a positive datapoint (few organs are both brain-faithful AND live). No new
  gap; one candidate refinement intersects a KNOWN structural cap (do not re-tread).** (a) FIDELITY: PINNED and well-built — the
  canonical CLS pipeline: DG random EXPANSION → top-K sparsify (pattern SEPARATION; Dentate-Gyrus analog, ~1% active), CA3
  Hebbian outer-product auto-associator (pattern COMPLETION; Marr 1971), optional CLS replay to cortex (McClelland/O'Reilly
  1995; Wilson/McNaughton 1994 SWS replay). It EXPLICITLY avoids the prior naive `sparse_engram_allocation` WTA-collision
  mechanism. (b) WIRING: WIRED — built in `substrate.py` slot D3 ("one-shot episodic write"); one of the 19 live modules (via
  substrate, the memory backbone; the comprehension reader uses `ChunkedFocus` for WM — a different layer). (c) PARAMETERS:
  sparsity ~1% is a SWEPT parameter (DG ~1-3%; defensible, not adopted-from-a-constraint). (d) THE ONE CANDIDATE REFINEMENT +
  WHY IT IS NOT A FRESH GAP: CA3 `settle()` is ONE-STEP (`sign(W @ cue)`), whereas the brain's CA3 is a RECURRENT attractor
  (multi-iteration settling to a fixed point). BUT (i) a recurrent option already exists in-module (`from hdlab.iterative_
  attractor import iterative_cleanup`), and (ii) partial-cue completion is ALREADY known STRUCTURALLY CAPPED
  (`store_survives_a_partial_cue`, owner-DONE — an exact-key number does not transfer to a partial cue; a floor is cleared by
  UNDERSTANDING, not by adding iterations), so recurrent settling almost certainly does NOT rescue it. Do NOT re-package
  "make CA3 recurrent" naively — it intersects that structural cap. CONCLUSION: the core episodic-write primitive is sound;
  this scan is a confirmatory positive, NOT a problem seed. (Contrast: this is the brain-faithful, wired end of the substrate —
  the systematically-UNWIRED end is the prediction-error control signal, per the WM/segmentation/predictive-reader synthesis.)

- **2026-08-31 — COMPONENT SCAN + CROSS-CUTTING SYNTHESIS (strategy, verdict-independent): the reader's WORKING MEMORY is a
  wired Cowan-4 BUNDLE (`ChunkedFocus`/`EventBundleCodec`); the more brain-faithful `slot_attention_wm` (per-slot PBWM
  prediction-error-gated state) is an ISLAND — AND this completes a pattern: PREDICTION ERROR is the brain's central control
  signal, the substrate has BUILT every piece, and wires NONE into the live reader's core operations.** (a) FIDELITY: the wired
  WM is a Cowan-4 role-slot BUNDLE (sum of bound role-filler pairs into one bounded focus, unbind to read) — capacity-correct
  (Cowan-4 PINNED) but mechanism-SIMPLIFIED: no separate maintained per-entity slots, no prediction-error-gated updates.
  `hdlab/slot_attention_wm.py` is the fuller PINNED mechanism (WM = active maintenance of K full-d entity-state slots, per-slot
  PBWM update from its OWN prediction error — O'Reilly-Frank 2006; learned content-based addressing, role-general/position-
  invariant — Frankland-Greene; Locatello 2020 slot attention). (b) GENERALIZATION: `slot_attention_wm` is a LEARNED organ
  (addr/gate/role-key nets trained jointly with an unfrozen encoder) — unvalidated here; the wired bundle is deterministic. (c)
  WIRING: `slot_attention_wm` is a FULL ISLAND (imported by no hdlab module). (d) ⚠️ RE-TREAD CAVEAT: naive bundle-replacement
  is an INTEGRATED NEGATIVE (`the_bundle_destroys_meaning_but_replacing_it_hurts`, owner-DONE) + store findings (dense-bundle-
  that-fans; register-renorm-breaks-serial-readout). `slot_attention_wm`'s learned, prediction-error-gated design is DIFFERENT
  in kind, but any WM problem MUST gate against that negative — do NOT re-package "replace the bundle" naively.
  🔗 **THE SYNTHESIS (the real value — spans this week's scans): PREDICTION ERROR is the systematically-UNWIRED control signal.**
  The brain uses prediction error as its universal control: PBWM WM gating (write when surprised), EST event boundaries
  (segment at prediction-error peaks), N400 coherence (detect incoherence), forward selectional prediction (Friston free-energy
  binds them). The substrate has BUILT each piece — `predictive_reader` (forward), `n400_coherence_monitor` (backward),
  `slot_attention_wm` (PBWM WM gate), and the EST event-boundary need (scene-segmentation scan) — and **wires NONE into the live
  reader**, which uses fixed/deterministic proxies everywhere (fixed-window scenes, bundle WM summed unconditionally, no forward
  prediction). This is the substrate's single biggest FIDELITY-vs-WIRING gap and it aligns with the standing "reader is
  feed-forward where the brain is predictive" thesis + the reasoning/predictive-architecture direction. NOT packaged (queue
  full: p2 open + 3 awaiting review); recorded as a candidate STRATEGIC direction (a coordinated "wire prediction error into the
  reader's core operations" program) — surface to the owner, do not force a brief.

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent): the reader's SCENE segmentation is a FIXED 5-sentence window
  (`i // LOCAL_WINDOW`) — an OUR-INVENTION placeholder for a PINNED brain computation (Event Segmentation Theory: event
  boundaries at PREDICTION-ERROR peaks), and the real segmentation organs are ISLANDS. This composes the two predictive-coding
  halves already scanned into one functional output (event boundaries).** (a) FIDELITY: the live coref scopes "scenes" by
  `sid_fixed = [i // LOCAL_WINDOW]` (LOCAL_WINDOW=5) — a fixed window, INVENTED. The brain segments at prediction-error
  boundaries (Zacks & Swallow 2007 EST; boundaries where the predicted next state diverges), variable-length, not every-5. (b)
  GENERALIZATION: a fixed window cannot fit variable scene lengths (a scene may be 1 or 20 sentences); it cannot generalize by
  construction. (c) WIRING: the reader imports ONLY `parse_conll_sentences` (a mechanical utility) from `hdlab/scene_segment.py`
  — NOT that module's actual scene logic (LEVER 2: cue-based scene-boundary detection via closed-class time/location adjuncts
  "the next day / meanwhile / years later" + character-set turnover; LEVER 1: topical-protagonist-per-scene coref, VALIDATED for
  the cross-sentence coref residual). Those levers are an ISLAND. `hdlab/n400_coherence_monitor.py` (the backward prediction-
  error/coherence mechanism) is ALSO an island (not imported by `situation_reader`/`substrate`). (d) GAP + LEVERAGE: the
  brain-faithful path is EVENT BOUNDARIES FROM PREDICTION ERROR — compose `predictive_reader` (forward, scanned 2026-08-31) +
  `n400_coherence_monitor` (backward) → a coherence-drop boundary signal → the scene structure coref/focus already consume,
  REPLACING the fixed window. A cheaper first upgrade is `scene_segment`'s cue-based detector (already validated for coref).
  MEDIUM-HIGH leverage: scene structure gates coref (the topical-protagonist lever was validated on the residual) and event
  boundaries organize the whole situation model. This is the "one lever, multiple payoffs" pattern — the two predictive-coding
  halves I scanned this week (predictive_reader + n400) unify into event segmentation. NOT packaged (queue full: p2 open + 3
  awaiting review); seeds an event-segmentation problem when a slot opens. ⚠️ MIND: the gen stress-test flagged the N400
  SEGMENTER as DOES-NOT-HOLD at its old operating point — so the faithful build must be re-measured at the real operating point,
  not assumed from the isolation result.

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent): `predictive_reader` (the forward half of predictive coding) is
  a PINNED, well-grounded organ but a default-off ISLAND reachable ONLY through `incremental_parser` (also an island) — so
  wiring p2 (incremental parser) is the vehicle that brings the forward-prediction signal into the live reader.** (a) FIDELITY:
  PINNED — verb+role pre-activates the expected argument's GROUNDED features (selectional-preference centroid; Altmann & Kamide
  1999, McRae 1998), error = -log P softmax surprisal (Hale 2001, Levy 2008, Michaelov 2024), precision-weighted by selectional
  concentration (Friston). Predicts MEANING features not word-form (Nieuwland 2018). The forward complement to
  `n400_coherence_monitor` (backward event-coherence half) — two levels of one predictive hierarchy. NOT a placeholder. (b)
  GENERALIZATION: honestly MODEST in isolation (its own docstring: "construction-proven; the isolation effect is modest,
  ceiling'd by the grounded space; NOT a standalone accuracy lift; MEASURE on the live reader"); live value is a graded
  difficulty/anticipation SIGNAL. (c) WIRING: ISLAND — not imported by `situation_reader`/`substrate`; imported ONLY by
  `hdlab/incremental_parser.py` (itself an island). (d) TWO FINDINGS: **(i) TRANSITIVE-WIRING PAYOFF — `predictive_reader` is a
  dependency of the just-opened p2 `wire_the_incremental_parser…` (prediction ON = selectional preference for competing
  post-verbal nominals); wiring p2 brings BOTH organs live, so p2's payoff includes activating the forward-prediction signal
  that targets the two-animate who-did-what gap (`the_live_front_end_mislabels_who_did_what_to_whom`).** (ii) SHARED-CEILING
  FIDELITY LEVER — `predictive_reader` predicts in the COARSE grounded space (grounded_similarity caps sofa/couch = apple/orange
  = dog/cat at 0.45), the same ceiling found in the meaning work; a richer feature basis (the now-wired conceptual channel /
  distributional space) is a fidelity/optimization lever for prediction PRECISION. Neither packaged (queue full + correctly
  ranked); recorded to strengthen p2 and seed a future prediction-basis problem.

- **2026-08-31 — COMPONENT SCAN (strategy, verdict-independent): the reader's TIME dimension (`_read_timeline`) is a NARROW
  past-perfect FLASHBACK detector, not general temporal-order reconstruction — AND it is INDEPENDENT of the p1 keystone flag
  (a precise correction to my own boundary note).** (a) FIDELITY: the reader's TIME read is gated on `"had" in toks` — it fires
  ONLY on past-perfect sentences, reconstructing chrono order via tense/aspect + connectives (`M.reconstruct_order_timeline`)
  and flagging reordered (flashback) frames. That is a PARTIAL proxy for the PINNED brain computation (event-model temporal
  indexing / Reichenbach event-reference-speech time; Zwaan & Radvansky TIME dimension): it MISSES ordering carried by
  connectives (after/before/then/when), tense shifts without "had", and aspect — an OUR-INVENTION narrow lexical trigger, not
  the before/after relational computation. (b) WIRING: `_read_timeline` IS wired (called in `read()`), but the "had" gate makes
  it rarely fire; `hdlab/graded_temporal_context.py` is an ISLAND (reader doesn't import it); a full `temporal_order_register`
  is NOT promoted (only `experiments/_temporal_ordering*`). So the TIME dimension is thinly served. (c) KEYSTONE-FLAG
  INTERACTION (the timely check): `_read_timeline` uses `M.extract_events_punct` for its OWN event detection — INDEPENDENT of
  `tense_agnostic_events` (which only affects `_read_events` via `_extract_events`). So the flag does NOT corrupt TIME today;
  my landed boundary note is a correct FORWARD caution (a future SHARED event set would need a tense-PRESERVING detector, else
  TIME breaks), NOT a present breakage — clarified in the code comment. (d) GAP + LEVERAGE: a faithful TIME dimension =
  general temporal-order reconstruction (connectives + tense + aspect + Reichenbach), which NEEDS real tense — so the QUEUED
  tense-PRESERVING detector variant (p1 follow-on) is a SHARED dependency serving both a proper TIME dimension AND the
  shared-event-set architecture. Connects to the QA capstone's "when +0.55 [tense-shared caveat]". Medium leverage; a candidate
  future problem (NOT packaged — queue is full + correctly ranked). Seeds the next temporal problem when a slot opens.

- **2026-08-31 — INTEGRATED + LANDED (p1, owner-DONE, EXCELLENT, THE KEYSTONE): the reader's event detector was TENSE-GATED
  (missed present-tense finite verbs 100%, capping event recall ~0.33); the brain-faithful fix (tense-agnostic UPOS==VERB
  detection) is now WIRED into the live reader behind a default-off flag, lifting end-to-end event recall 0.33→0.95.**
  Reverified 11/11 first-hand. FIDELITY: PINNED — event detection is tense-agnostic, lexical-category-based (neo-Davidsonian
  event variable; LIFG/pMTG structure-building references no tense; PAST is the harder discourse-linked form, so gating on
  tense was backwards — Bastiaanse 2011). GENERALIZATION (the owner-priority check, PASSED): CI-separated on THREE pre-existing
  golds — UD-EWT + modern QA-SRL (genre change) + 19c LitBank (century change); two info-free twins lose; precision neutral/
  improving; home-grown UD tagger (NO LLM). END-TO-END through the LIVE `SituationReader.read()` (0.381→0.966), not gold
  isolation. LANDED: `hdlab/situation_reader.py` `tense_agnostic_events` flag (default OFF = byte-identical; on = 104→219
  events 2.11x through the canonical reader; witness `test_tense_agnostic_events_organ.py`). BOUNDARY (OUR-INVENTION, honest):
  placeholder tense → the TIME dimension must not consume the flag until a tense-preserving variant is validated. **KEYSTONE for
  the assembly (DEBT 2): every downstream dimension reads off the event set, so this flag is the prerequisite to re-measuring
  the assembly at real recall.** Seeded: copular/nominal-predication recall (UPOS==VERB excludes them); the incremental parser
  (one lever, three payoffs). precise_voice role wire QUEUED (synthetic-mention caveat). Registered
  `extraction_frontend_tense_agnostic_detector_v1`.

- **2026-08-31 — INTEGRATED (p5, owner-DONE, STRONG): the covariation causal-graph typer types CAUSE-vs-PRECONDITION on
  held-out MAVEN-ERE with power (balanced 0.772 vs structural floor 0.546, +0.226 CI-sep, coverage 1.0) — but open-text/
  single-document transfer is a RIGOROUS NEGATIVE, so NO live-reader landing.** Reverified 16/16 first-hand. FIDELITY: PINNED —
  covariation/contingency causal induction (Cheng causal power) + a hierarchical type-role schema; it GENERALIZES to UNSEEN
  type-pairs (schema 0.581 vs memorized-lookup chance 0.500 — a schema, not a lookup), robust to type-noise, physical>intentional
  (phys-AUC 0.684 vs 0.570 — a measured mechanism boundary). HONEST BOUND (the load-bearing finding): covariation needs OBSERVED
  CONTINGENCY, so it fails on never-co-observed pairs (organ 0.671 < structural 0.705 on unseen) and on cross-genre narrative;
  the earlier cross-genre negative was WITHDRAWN as instrument-confounded, then re-tested clean within-MAVEN. **NO reader landing
  (correct no-landing): the reader reads SINGLE documents where cross-document contingency is absent — wiring it would ride the
  open-text negative. FUTURE HOME = CORPUS-level causal knowledge (the knowledge-store p4 / the learner), which sees the whole
  corpus.** Recorded in WIRING_MAP non-debt. No hdlab file changed.

- **2026-08-31 — COMPONENT SCAN + CROSS-CUTTING INSIGHT (strategy, verdict-independent): `location_register` (SPACE) is a
  PINNED brain computation but a default-off ISLAND — AND the assembly's per-dimension wirings all share ONE dependency: the
  extraction/parse front-end. So p1 (the SOLVED extraction fix) is a KEYSTONE for the assembly, not just downstream measurement.**
  ✅ **p1 NOW INTEGRATED + LANDED (entry above) — the keystone flag is live (default-off); the assembly can now turn it on and
  re-measure each dimension at real recall.**
  (a) FIDELITY: PINNED — per-entity location STATE updated ONLY by motion events, PERSISTING between updates (Zwaan & Radvansky
  1998 event-indexing SPACE; hippocampal place / entorhinal grid; Rinck 1997 rules out metric coords for narrative space →
  categorical topological scene nodes, OUR-INVENTION-swept but well-grounded). A genuine brain-computation organ, not a
  placeholder; spaCy-free tracking core, adapter-agnostic (consumes abstract motion events `(entity,kind,node,t)`). (b) WIRING —
  THE GAP: `situation_reader`/`substrate` do NOT import it; the reader only labels "location" as ONE role-filler among
  goal/source/path/etc. (situation_reader:719), it does NOT track per-entity location over discourse time. SPACE is unwired — the
  QA capstone HARD-ABSTAINS on "where". Wiring it needs the MOTION-EVENT adapter (`experiments/location_register.py`, parser-
  dependent). (c) THE CROSS-CUTTING FINDING (the real value of this round): the TWO DEBT-2 dimension wirings examined — CAUSATION
  (the queued p2 landing needs `_literalness_gate`, which drags `frame_sense_disambiguator` + `idiom_gate` + **spaCy**) and SPACE
  (needs the motion-event parse adapter) — are BOTH gated on the reader's extraction/parse FRONT-END. `p1
  the_extraction_front_end…` (SOLVED, recall 0.332→0.954, awaiting owner verdict) IS that front-end. So integrating p1 would
  materially de-risk EVERY dimension of the assembly (DEBT 2), because each dimension's adapter reads off the same extraction. →
  p1 is a keystone; the assembly should follow p1's integration, not precede it. (No priority change — p1 is already prio 1 and
  correctly ranked; this sharpens WHY. Recorded for the owner's review-p1-first recommendation.)

- **2026-08-31 — INTEGRATED (p2, owner-DONE, STRONG): the FORCE-DYNAMIC TYPER is validated END-TO-END through the LIVE reader's
  causation read (with the reader's OWN automatic extraction) — the reader can now type CAUSE/ENABLE/PREVENT within a clause.**
  Reverified 12/12 first-hand. AUTO 3-way 0.833 [0.714,0.929] > majority-CAUSE/untyped floor 0.429 CI-sep (+0.143); force-class-
  shuffle twin p95 0.524 loses; PREVENT positive control 11/13 vs 0/13 (only a force-dynamic representation encodes a prevented,
  never-happened endstate — a capability the untyped reader structurally lacks). FIDELITY: PINNED — within-clause causative
  extraction (actor-first eADM role binding); CAUSE/ENABLE/PREVENT is CONSTRUCTION-GENERAL (Goldberg; Talmy/Wolff force dynamics),
  so typing is DOMAIN-GENERAL not physical-only (physical-only 0.762 LOSES — a load-bearing, measured brief deviation). AUDIT
  CORRECTION vindicated: the earlier scan/stress-test verdict that the typer "does not generalize" is TRUE at the FULL-open-text
  operating point (fires ~16%, twin indistinct) but the typer HOLDS on the within-clause causative domain it is scoped to — the two
  are consistent, and open-text precision is the SEPARATE Stage-1 gap. NEW DEVIATION NAMED (OUR-INVENTION, honestly bounded): open-
  text causal encoding is a by-product of EVENT-MODEL construction decided at EVENT-NODE grain (only a FOREGROUNDED event is a
  causal-arc candidate; Zwaan & Radvansky, Hopper; causal-by-default, Sanders) — a foreground/event-hood PRECISION FILTER that
  nothing owns (a measured tradeoff gate exists, default-OFF: cleans descriptive prose 22→17 but regresses curated 0.833→0.810).
  hdlab LANDING QUEUED (Q111, the assembly DEBT 2 — CausalLink.ctype+endstate_reached; promote lexicon/patient-tendency/literalness
  → hdlab; default-OFF `causation_typed` flag in `_read_causation`, byte-identical off). Foreground/event-hood gate PACKAGED as the
  next problem; the `no_glass_box_verb_sense_disambiguation` reframe ("read force-eventhood off the arguments") noted.

- **2026-08-30 — LANDED (strategy, Q111, owner-directed): the CONCEPTUAL IDENTITY channel is now WIRED INTO the general meaning
  read-out (`meaning_fusion`) — DEMAND-ROUTED, default-off. The reader's meaning read-out now has BOTH dissociable systems.**
  Closes the wiring gap the conceptual_meaning scan named (entry below). `hdlab/meaning_fusion.py` gained an OPT-IN, demand-routed
  path: demand='relatedness' (DEFAULT, unchanged reading+grounded z-fusion) | demand='similarity' → the ATL conceptual hub
  (`conceptual_meaning`), gradable-adjective pairs → the scalar ruler via `meaning_operation_router` (magnitude injected, else an
  HONEST conceptual fallback) | demand='rating' → z-fuse both. ROUTING NOT POOLING (the fidelity lever): the similarity signal is
  never averaged into the relatedness pool. FIDELITY: PINNED — two dissociable meaning systems + semantic-control operation
  selection (LIFG/pMTG; Controlled Semantic Cognition). DEFAULT-OFF ⇒ the object is byte-identical (self_test + prior witness
  unchanged). WITNESS `verification/test_meaning_fusion_conceptual_routing.py` PASS first-hand, scaffold-free (recomputes SimLex/
  WordSim): wiring fidelity — `meaning(demand='similarity')` routes to & EQUALS `conceptual.similarity` on all 999 SimLex pairs;
  the identity WIN — conceptual 0.521 vs the associative route 0.245 on SimLex **similarity (+0.2761 CI[0.2096,0.3448], CI-sep)**;
  dissociation preserved (lower bound) — conceptual does NOT CI-sep beat associative on WordSim **relatedness** (conc−assoc CI
  upper 0.132, spans 0), so pooling would only pollute relatedness; shuffled-similarity twin LOSES CI-sep. ⚠️ **HONEST SCOPE
  (disk outranked the compaction-snapshot brief): (1) the associative comparator is the GROUNDED spoke alone (cheap static asset);
  the reading spoke (slow live read) deepens relatedness and yields the FULL crossover — separately proven — so (3) is a lower
  bound. (2) The QA capstone has NO meaning/vocabulary dimension (`coref/events/salience/temporal/causal/location/belief`), so
  "re-measure end-to-end via the QA instrument" does NOT literally apply; the faithful end-to-end for a word-meaning read-out is
  its OWN naturalistic task (WordSim relatedness + SimLex/SimVerb similarity), which is where the dissociation lives. (3)
  `meaning_fusion` itself is STILL not imported by `situation_reader`/`substrate` — this joins the standalone meaning ISLANDS
  (WIRING-DEBT #3), it is NOT the assembly (#2). Wiring the composed read-out into the live reader remains an open step.**
  Registered `meaning_fusion_conceptual_identity_channel_v1`.

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `conceptual_meaning` (the ATL meaning-IDENTITY hub) GENERALIZES
  and is BRAIN-FAITHFUL — but it is an ISLAND, so the live reader STILL has no meaning-identity system (a high-value wiring gap).**
  ✅ **ADDRESSED by the landing above (the conceptual channel is now wired into `meaning_fusion`, default-off).**
  (a) FIDELITY: PINNED — the ATL amodal conceptual hub (Controlled Semantic Cognition; Lambon Ralph/Jefferies/Patterson/Rogers
  2017): meaning-IDENTITY (what a word IS) via a WordNet definitional/taxonomic feature bag with DISTINCTIVE-feature privileging
  (global-IDF, the sparse-space analog of the ATL op). Glass-box static asset, no LLM. (b) GENERALIZATION (a genuine positive):
  validated on PRE-EXISTING human gold — SimLex-999 rho 0.521 vs a steelmanned GloVe-300 0.371 (+0.15 CI-sep), SimVerb 0.499 vs
  0.220, shuffled-gloss twin LOSES, and a DOUBLE DISSOCIATION holds (conceptual→similarity, associative→relatedness). Bounded
  only by WordNet coverage (OOV). (c) WIRING — THE GAP: imported by NEITHER `situation_reader` NOR `meaning_fusion`; only by
  `convergent_cue_reader` + `meaning_operation_router`, which are THEMSELVES islands. The LIVE meaning read-out (`meaning_fusion`)
  fuses the distributional (reading) + grounded spokes only — NO conceptual channel. So the reader remains AT CHANCE on
  meaning-IDENTITY (the exact gap this organ was built to fix) because it is unwired. (d) LEVERAGE + PATH: HIGH — wiring the
  conceptual channel into the live meaning dispatch gives the reader its missing second meaning system. The path already exists
  and is queued: `meaning_operation_router` (built to route gradable-adjective→magnitude else→conceptual gloss; "wire into the
  LIVE meaning dispatch, default-off until wired") → add conceptual as a spoke in `meaning_fusion`. **A top WIRING-DEBT (DEBT 3,
  standalone meaning islands) candidate — a Q111 landing (router + conceptual channel → meaning_fusion), NOT a new build; the
  queue is full so seeded, not packaged. Re-measure the fused read-out end-to-end after wiring (the QA capstone instrument).**

- **2026-08-30 — THE NON-CANONICAL ROLE COLLAPSE IS A PARSE-QUALITY PROBLEM, NOT A THEMATIC-FIT PROBLEM (a rigorous negative
  that REDIRECTS to p1)** (from integrated `grounded_role_assignment_via_verb_keyed_thematic_fit`, owner-DONE, SOLVED/STRONG;
  reverified 14/14 first-hand). The McGuffey migration exposed that role assignment collapses on non-canonical order (0.288);
  the brief hypothesized grounded thematic-fit + a conflict gate. RESULT (two regimes, noisy-channel theory): on CLEAN parses
  the fix is STRUCTURAL ROUTING not fit (route_only 0.9858 beats word-order + graded_role CI-sep, no canonical regression — fit
  does not CI-separate); on WEAK parses the fit gate beats both floors + generalizes to unseen pairs but has an IRREDUCIBLE
  canonical tradeoff (P1 fails, the rigorous-negative P2 clause met with power). **PINNED: thematic fit belongs ONLINE, competing
  DURING attachment (Lewis-Vasishth; MacDonald; Levy noisy-channel), NOT as a post-hoc override — a post-hoc gate cannot separate
  override-when-conflicting from leave-alone-when-not.** The real fix = PARSE QUALITY: a modern dependency parser (spaCy,
  substrate-native, NO LLM) scores structural roles 0.9959 balanced non-canonical, dominating word-order/graded_role/every fit
  gate — the admissible-interim ceiling; the brain-faithful target is an INCREMENTAL cue-integrated PREDICTIVE structure-builder.
  **THIS IS p1's DIAGNOSIS** (`the_extraction_front_end_recovers_only_a_third_of_events_and_roles`, in-progress): the
  non-canonical role stage is a big recall loss and its fix is a better/incremental parser — the solver's ready-made
  `FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md` is the 8-section brief for it, ready-to-lift IF p1's diagnosis confirms the
  incremental parser is a distinct build. **FENCED dead-ends (do NOT re-open): thematic-fit fit-vector work, the post-hoc fit
  gate, fused-always / linear-sum / precision-weighted (all hurt canonical); the count-fit signal is largely SEEN-PAIR
  MEMORIZATION (twin edge does not survive to unseen).** hdlab: a routing precision-fix to `graded_role_assigner` (restrict the
  override to reliable strong-passive markedness, +0.081 CI-sep, fit-independent) QUEUED — needs end-to-end live-reader
  validation first (the phase-gate trap: isolation ≠ live reader).

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `event_centrality_coref` (LIVE-WIRED) is a MIDDLE_BAND organ
  whose core thesis is CONTRADICTED by later integrated coref work → a re-measurement / possible-demotion candidate.**
  (a) FIDELITY: breaks same-gender coref ties by EVENT CENTRALITY — a Cowan-4 ChunkedFocus of role-slot event bundles is queried
  (HD unbind+cleanup) so the memory is decision-load-bearing (fixes the write-only-witness gap). Brain-relevant IN PRINCIPLE
  (event structure feeds reference), BUT the event extraction is POSITIONAL (first-mention = subject proxy, NOT true SRL — the
  docstring flags it) and it rides on the Cowan-4 focus that a prior scan found rarely fires on real text (median ~1 event/entity).
  (b) GENERALIZATION: registry verdict = **MIDDLE_BAND** (marginal, not a CI-separated win), and it was an ORPHAN before wiring.
  (c) WIRING: LIVE (6 refs in `situation_reader`, `EventCentralityReader`). (d) THE GAP: its load-bearing thesis — "event/
  situation MEMORY disambiguates the same-gender coref residual" — is **contradicted by the integrated coref-residual work**
  (`the_coref_residual_needs_a_discourse_focus_stack` + the discourse-fact reasoner): the residual is GRAMMAR-FILTER (person/
  animacy phi-agreement) + DISCOURSE-FOCUS bound, and a commonsense/memory KB is measured DEAD (~2-3%) there — so an
  event-memory tie-break is expected to be marginal, matching its MIDDLE_BAND verdict. The LANDED phi-agreement pre-filter
  (`graded_coref_pick.phi_agreement_keep`) is the recall-safe grammar fix for the same tie. **ACTION: re-measure
  event_centrality_coref's live contribution AGAINST the landed phi-filter (does its event-memory tie-break add anything over
  grammar agreement on real LitBank same-gender ties, or is it redundant/marginal?); a wiring-review candidate for demotion if
  it does not clear the phi-filter. Seeded — not packaged (the coref path is covered by p3 + the landed phi-filter; this is a
  live-organ value re-check, apply the generalization method's real-operating-point re-measurement).**

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `hd_fact_store` (the substrate knowledge base) VETS SOURCE-TRUST,
  NOT CORRECTNESS — this is the North Star "noisy foundation" mechanism, on disk.** (a) FIDELITY: facts stored as glass-box
  role-slot-bound hypervectors — `quantize(bind(REL,rel)+bind(ARG0,subj)+bind(ARG1,obj)+bind(SOURCE,src)+bind(TRUST,trust))`,
  every field (incl. provenance + trust) recovered by unbind+cleanup (never a plaintext copy); reuses the validated EventBundleCodec
  binding (computationally faithful role-filler binding; the bipolar-sign impl is the known deviation). Adds per-domain cleanup +
  a subject-relation HD conflict key + INGEST-VET (trust-ranked REPLACE/COMBINE/FLAG/DROP). (b/d) THE GAP (its own docstring is
  explicit): **"INGEST-VET is SOURCE-TRUST vetting, NOT correctness vetting… a clean (non-conflicting) fact simply STORES — there
  is no internal uncertainty gate."** So the store accepts whatever is extracted from a trusted source and only resolves
  CONFLICTS by source rank — there is NO organ verifying a stored fact is TRUE or CONSISTENT with the rest of the knowledge.
  **Foundation cleanliness therefore = extraction quality (p1 `the_extraction_front_end…`) + source curation, with a missing
  CORRECTNESS/CONSISTENCY cleanup** — exactly the consolidation/cleanup organ the learner-on roadmap named as the DISCONNECTED
  MISSING LINK (`[[learner-on-organizing-frame]]`: the cleaned cortical store is written-but-never-read). (c) WIRING: wired into
  the SUBSTRATE (the KB / `director_kb_query`), not the live reader. **CONVERGENCE:** this confirms the North Star diagnosis at
  the fact-store level — the learner is held OFF because the foundation is noisy, and the noise enters precisely HERE (source-trust
  ingest with no correctness gate); the two levers are p1 (cleaner extraction upstream) + the consolidation/cleanup organ
  (correctness/consistency downstream). Seeded — NOT packaged (p1 + the roadmap own it; this sharpens WHERE the noise enters).

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `situation_focus` (ChunkedFocus) — brain-faithful (Cowan)
  but its chunking win is a HIGH-LOAD constructed self-test that likely RARELY FIRES at the real operating point (the same
  collapse the generalization audit just measured for the entity store).** (a) FIDELITY: PINNED — Cowan (2001) bounded-capacity
  focus of attention (~4±1 chunks) with hierarchical chunking (oldest units compress into a nested Level-2 CHUNK past CAPACITY);
  glass-box, reuses the validated bipolar bind/quantize. Genuinely the brain's operation. (b) GENERALIZATION: the win
  (FlatFocus DEGRADES with load / ChunkedFocus RECOVERS recent items) is demonstrated by CONSTRUCTED self-tests
  (`_selftest_flat_degrades_chunked_recovers_recent`) on synthetic high-load event streams — **NO held-out / real-text evidence
  that chunking helps live reading.** (c) WIRING: imported by `situation_reader` (ChunkedFocus), but historically flagged in the
  island/shelve audits (capability_integration_ledger 07-28; wired-vs-islands 07-25 item a) — live-imported, value un-witnessed.
  (d) GAP + LEVERAGE (converges with the just-integrated generalization audit): chunking only ENGAGES when active units exceed
  CAPACITY (~4), but the audit measured that on real text the median entity carries **~1 event (87% ≤ 3)** — so on real reading
  the focus likely rarely exceeds capacity and **chunking rarely fires**, i.e. its +recovery win lives at a high-load operating
  point that real narrative seldom reaches (the SAME pattern as the separated entity store, +0.94 synthetic → +0.06 real,
  busy-entities-only). **ACTION: apply the audit's meta-lesson — re-measure ChunkedFocus-vs-FlatFocus at the REAL focus-load
  distribution on live reading (does the reader's active focus ever exceed ~4 on real narrative? does chunking then help?);
  expected outcome busy-context-only, like the store. Seeded (not packaged — the queue is full with p1/p2/p5/p6; this is a
  re-measurement that folds into the generalization method / the p1 extraction work's operating-point analysis).**

- **2026-08-30 — THE GENERALIZATION STRESS-TEST RE-BASELINES THE SUBSTRATE: three credited wins DO NOT generalize on real text,
  one shrinks 15–60×, and the meta-lesson is to re-measure at the REAL operating point** (from integrated
  `stress_test_which_organ_wins_actually_generalize_on_held_out_text`, owner-DONE, SOLVED/EXCELLENT; reverified 34/34 first-hand).
  A ledger over 33 keyword-flagged organs (10 false positives already validated n=995..28,569; 9 already-negatives; 13 fragile) +
  4 positive-controlled reruns on pre-existing corpora. **VERDICTS (each corrects a credited or assumed capability):**
  (i) SEPARATED CONTENT-ADDRESSABLE STORE (`content_addressable_retrieval` / `the_entity_store_is_a_dense_bundle_that_fans`
  cluster): synthetic +0.94 → real **+0.06** on LitBank (28,569) — HOLDS-DIRECTIONALLY, MAGNITUDE-COLLAPSES; concentrated in the
  ~13% busy entities (≥4 events); 87% of real entities carry ≤3 events where FLAT is already ≥0.98. **WIRE FOR BUSY ENTITIES
  ONLY**; DG-at-retrieval HURTS distinct-address codes (use it only for confusable/fan addresses). (ii) `force_dynamics_typer`
  (WHY/causal): DOES NOT HOLD on MAVEN-ERE (n=9,698) — fires on only **16.1%** of real causal relations, twin-indistinguishable
  where it fires (+0.018 NOT_SEP), loses to majority −0.679. It is explicit-PHYSICAL-predication only. (iii) `n400_coherence_monitor`
  event segmenter: DOES NOT HOLD (boundary-F1 0.122 vs synthetic 0.987; content-novelty is the wrong signal — real boundaries
  track situation-model dimensions, Zwaan-Radvansky/Zacks). (iv) CONSOLIDATION sparse-selective-replay store: DOES NOT HOLD
  (selective − uniform-twin −0.009 NOT_SEP; the brain-faithful need-priority arm ALSO ties → prioritized replay is genuinely no
  lever on real cross-domain interference). **TWO PINNED SUCCESSORS gate-cleared → BUILD (packaged p5/p6):** real causation is
  COVARIATION-based causal-GRAPH inference (Trabasso/van den Broek; Kintsch; Kuperberg 2011; Feng 2021 ALE; left IFG/MTG+rostral
  mPFC — force-dynamic verbs have a VERIFIED ABSENCE of neural study), scorer beats twin +0.094 / majority +0.056 on the 84% the
  typer misses; retrieval interference is SIMILAR-COMPETITOR CUE-OVERLOAD (Van Dyke & McElree 2006; Radvansky & Zacks falsify
  event-count), content under-determines at 0.398, TCM context reinstatement is the disambiguator (combination = the unbuilt
  step). **THE META-PATTERN (adopt substrate-wide): a synthetic headline is set by the OPERATING POINT/POPULATION — a fact about
  the corpus, not the mechanism; re-measure every organ at the real operating point before crediting it.** **THE BIGGEST LEVER
  (flagged, packaged p1): the EXTRACTION FRONT-END (~0.32 event/role recall) — every organ number here used GOLD extraction; the
  front-end dominates end-to-end and caps every dimension.** `generalization_audit.py` confirmed to over-flag ~2.5× (reading the
  n is the whole job; a held-out-n column is queued).

- **2026-08-30 — THE SITUATION MODEL GETS A QA READ-OUT, AND IT IS A WIRING-DEBT DIAGNOSTIC** (from integrated
  `the_reader_cannot_answer_a_question_over_its_situation_model`, owner-DONE, SOLVED/STRONG; reverified 8/8 first-hand over
  16,587 questions). A unified glass-box QA interface routes a structure-dependent question to the dimension holding the answer
  and reads it OFF the accumulated model, never re-reading — **PINNED: the Kintsch textbase-vs-situation-model dissociation IS
  the floor** (bridging/causal/spatial/temporal probes are unanswerable from surface memory). The ROUTER is a SOFT + PARALLEL +
  THRESHOLD-GATED cue-race (Lewis & Vasishth 2005; abstain = a feeling-of-knowing gate), with a wh-word ANSWER-TYPE + WordNet
  head-noun ontology (Roberts QUD; Cysouw wh→ontology universal) — dimension→subsystem specialization is real (PPA/space,
  time-cells/order, pSTS/who, mPFC/cause, TPJ/belief); reference architecture SEM (Franklin 2020). **GENERALIZATION (the excellent
  core):** the wh-ontology router generalizes to novel cue words (1.00 vs cue-table 0.40 vs keyword 0.00) and PRESERVES answer
  accuracy under paraphrase (coref 0.556→0.556) where a keyword router COLLAPSES (→0.071) — a paraphrase-robust routing win, not
  a keyword switch. **KEY CROSS-CUTTING FINDING — the capstone QUANTIFIES THE WIRING DEBT end-to-end:** why/causal LOSES
  (0.442 vs 0.652) because the live causal dimension is a connective PLACEHOLDER while the real `force_dynamics_typer` (0.929) is
  built-but-UNWIRED; where / who-believes correctly HARD-ABSTAIN (1.00 / 0.96) because `location_register` / `belief_partition`
  are built-but-unwired ISLANDS (never-tracked, glass-box honest — NOT wrong answers). **This QA interface is now the END-TO-END
  MEASUREMENT INSTRUMENT for the assembly / wiring-debt burn-down:** each dimension organ wired into the live reader gets its
  end-to-end payoff re-measured with it (the queued p2 causation-wiring is the first — it should turn the causal NEGATIVE into a
  win). OUR-INVENTION-flagged: the abstain threshold + the WordNet head-noun resolver (queued swap → the idle
  `distributional_meaning_channel`). Honest bounds: temporal shares its tense signal with its gold (withdraw-first); coref is the
  existing coref reframed (real +0.087, not new capability); corpus-untested (LitBank 19c only). hdlab: query API + dimension
  wiring QUEUED.

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `frame_induction` (OOV verb thematic-frame induction) —
  brain-faithful + generalization-FIRST by design, but its held-out generalization is UN-WITNESSED as an organ → a prime
  target for the p4 generalization stress-test (feeds p4, does not seed a new problem).** (a) FIDELITY: PINNED — Gleitman
  (1990) SYNTACTIC BOOTSTRAPPING (induce a novel verb's frame, AGENT vs EXPERIENCER, from the CONSTRUCTIONS it appears in),
  run through the centralized `hdlab/learner` as a CONFIG-ONLY expand (zero edits to learner core — disciplined). The
  construction-cue encoder (sentential complement / degree-modification / progressive) is SUPPLIED; the construction→frame
  mapping is EARNED. (b) GENERALIZATION: built FOR it — "the verb lemma is NEVER a feature," so an induced hypothesis transfers
  to a held-out novel verb by construction overlap (the explicit fix for a shelved perceptron's ~92% feature-leak
  near-memorization). **BUT there is NO dedicated held-out organ witness in `verification/`** — the "transfers to novel verbs"
  claim rests on scattered experiment cells (exp_bridge1 / exp_c5_*), not a clean named held-out test → a generalization-EVIDENCE
  gap (the owner's first-class check: a design-for-generalization is not a witnessed generalization). (c) WIRING: LIVE (7 refs in
  `situation_reader`); notably it is the LEARNER used live on a bounded, safe induction task. (d) ROLE + LEVERAGE: the OOV
  trigger is `lemma not in VERB_FRAMES` and VERB_FRAMES is a **228-verb HAND-AUTHORED** table, so frame_induction is the live
  fallback that must catch the novel PSYCH verbs (cherish/loathe/crave — subj=EXPERIENCER) the default (subj=AGENT) mislabels;
  its generalization is load-bearing there but un-witnessed. **ACTION: hand p4 (`stress_test_which_organ_wins_actually_generalize`)
  frame_induction as a concrete target — write the held-out novel-psych-verb witness (train on in-vocab, test on held-out OOV
  psych verbs, lemma-blind twin must lose). No new problem packaged (p4 already owns this).**

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `event_bundle` (EventBundleCodec) — CLEAN + well-founded,
  NO new gap (a confirmatory scan; logged so a future scan skips it).** (a) FIDELITY: encodes an event as
  `quantize(Σ_r bind(role_key[r], filler[r]))` — role-filler binding is the PINNED computational op; the only deviation is the
  known BIPOLAR `sign()`-on-a-bundle implementation, ALREADY documented as a wrong-op (graded > sign; the "16× dims → +0.0843,
  largest measured single lever" representation-format note; cross-ref the §-list sites `situation_focus`/`role_slot_summarizer`/
  `event_bundle`). Not a new find. (b) GENERALIZATION: it is a CODEC, not a task-gold organ — round-trips cleanly at ~4 role
  pairs, α=4/N_DIM << the 0.138 bundle-collapse wall (capacity-argued; self-test asserts bit-identity vs
  `role_slot_summarizer.summarize_flat`). Multi-event capacity is correctly DELEGATED to the store level (the fan is
  `situation_model_accumulate`'s, addressed by `factorized_entity_store` + set-return). (c) WIRING: LIVE (imported by
  `situation_reader`). NO bipolar-vs-FHRR algebra clash — the FHRR register binds `(role, event_INDEX)`, indexing events rather
  than holding bipolar content, so the two algebras are cleanly factored (my initial interoperability worry did not hold on
  disk). (d) LEVER: the graded-readout / dims lever is known + appropriately deprioritized in favor of the brain-faithful
  graded/sparse direction. **No problem seeded — event_bundle is correctly scoped, live-wired, and already-characterized.**

- **2026-08-30 — THE FORCE-DYNAMIC READER GETS A LITERALNESS VETO GATE (grounded-simulation-by-default, abstain on violation)
  — and it UNBLOCKS the causation wiring** (from integrated `the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate`,
  owner-DONE, SOLVED/EXCELLENT; reverified 7/7 first-hand — the reverify upgraded a stale frontmatter number: held-out RACE
  generalization is CI-separated at n=130, +0.089 [0.033,0.158], not the `result:` line's n=55 not-CI-sep). PINNED: grounded
  simulation (Bergen/Barsalou) is attempted BY DEFAULT and VETOED on a detected violation — a selectional violation over the
  force roles (antagonist/agonist + the Talmy motion-GROUND; known-abstract → figurative; Wilks / N400), an opaque stored-unit
  VOBJ idiom (Giora), or a bad attachment. Grounded simulation is GRADED not gated (LIT>MET>IDIOM>ABS; Raposo & Desai) → the
  gate's target is CONVENTIONAL-figurative + idiom. **KEY FIDELITY FINDING (converges with `no_glass_box_verb_sense_disambiguation`):
  the compositional WSD frame-POSTERIOR is a FALLIBLE literalness cue — net-NEGATIVE, left OFF; the reliable levers are
  ROLE-CONCRETENESS + the VOBJ stored-unit idiom.** OUR-INVENTION-flagged: the concreteness threshold + the idiom inventory
  (both generalization-tested: threshold-robust c_min 0.15–0.50; WordNet IS-A generalizes to novel nouns — boulder engages,
  bureaucracy vetoes). GENERALIZES (owner priority, STRUCTURAL — zero fit params): fire-precision 0.716 vs floor 0.560 (+0.156
  CI-sep); END-TO-END halves figurative mislabels 0.89→0.41 through the real typer; held-out unseen essay genre +0.089 CI-sep;
  2nd blind adjudicator κ=0.93. **hdlab:** the gate's landing is COUPLED with the causation live-wiring — wire gate + force
  typer + patient-tendency into `_read_causation` (engage only on ENGAGE_PHYSICAL). ADJACENT GAPS SEEDED: the FORCE_NONPHYSICAL
  bin has no consumer (a social/institutional-force reader); concrete-role conventional metaphor ('opened up', 'run the company')
  caps essay-prose generalization (a context-WSD / metaphor inventory).

- **2026-08-30 — COMPONENT SCAN (strategy, verdict-independent): `context_grounded_valence` (LIVE-WIRED reader organ) — its
  animacy axis GENERALIZES but its FORCE-VERB identification is a TEST-FITTED HAND LIST; the fix already exists on the shelf.**
  (a) FIDELITY: partly brain-grounded — biased-competition event assembly (Desimone & Duncan) + a WordNet ANIMACY axis + a
  frozen appraisal-sim theta valuation; the animacy override is PINNED-ish. (b) GENERALIZATION: the animacy axis is CERTIFIED
  OPEN-VOCAB (Bopen=1.000, 5 seeds; scramble→0.400 twin loses; no subset-A regression) — a genuine positive, NOT the word-list
  brittleness we feared. BUT the force-verb gate `FORCE_CLASS_HARM_REAL` = `FORCE_CLASS_HARM ∪ {batter,clobber,wallop,pummel,
  maul,claw,crack,wrench,twist}` is a CLOSED, TEST-FITTED hand list (the organ's own docstring flags it) — literally the
  Bopen/Bgap test verbs → it will NOT recognize force-verbs outside that set (the same "principle generalizes, hand-list does
  not" pattern the McGuffey migration flagged for the animacy cue). Also SCOPED-OPEN honest gaps: body-part animacy (WordNet
  routes body-parts to inanimate; `BODY_PART_SUPPLEMENT` patches only 9 words), abstract-harm-vs-goal-noun, beneficiary/
  social-relational valence. (c) WIRING: LIVE (imported by `situation_reader`, 5 refs) — NOT an island. (d) GAP + LEVERAGE + FIX:
  replace `FORCE_CLASS_HARM_REAL` with the ALREADY-INTEGRATED `force_dynamics_typer`'s FrameNet Causation-family lexicon
  (~300 verbs whose class assignment PREDATES any test gold; cached `data/force_dynamics_lexicon_v1/lexicon.json`) — a
  generalization-safe, pre-existing force-verb source AND a wiring CONSOLIDATION (reuse the better organ). Low-risk but
  behaviour-touching (must preserve the certified Bopen=1.000 + no regression), so it is a SMALL SOLVER PROBLEM (validate the
  swap generalizes), not a silent strategy edit — SEEDED, not packaged (queue has 2 available; captured for a free slot).

- **2026-08-30 — THE ROLE EVAL MIGRATES McGUFFEY→MODERN, AND McGUFFEY'S ROLE EVAL WAS DEGENERATE + THE ORGAN DOES NOT
  GENERALIZE TO MODERN NON-CANONICAL ORDER** (from integrated `the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text`,
  owner-DONE, SOLVED/EXCELLENT; reverified 19/19 first-hand — the owner's ~10×-requested corpus-age fix). Built a modern
  situation-model role eval from UD-EWT gold parse (330 passages / 700 in-scope queries; transparent UD-deprel→role, no LLM).
  **MEASURED:** (1) McGuffey's role eval is DEGENERATE — 90.85% "agent", so a trivial always-agent floor (0.908) BEATS the
  celebrated vargs organ (0.856); the original eval never gated against the strongest majority-class floor (only a
  positional-reader 0.517 + twin 0.627). **The celebrated McGuffey role number was partly a degenerate-eval artifact.**
  (2) On modern text the vargs front-end does NOT clear its floor (0.596 < 0.659) and COLLAPSES on non-canonical order to
  0.288 (CI-sep below floor) — McGuffey's ~0% non-canonical rate structurally HID it (the corpus-age confound made numeric).
  **PINNED (the fix, re-deriving the owner-DONE `graded_role_assigner`):** thematic role = GRAMMATICAL FUNCTION (parse) +
  VOICE, NOT surface position — the front-end's bug is reading roles off AUXILIARIES ("has/is/was"), not the content verb; a
  passive-aware content-verb assigner recovers non-canon 0.288→0.559 CI-sep (voice-scrambled twin loses). Cue integration is
  PRECISION/RELIABILITY-WEIGHTED with a conflict-validity GATE (Ernst & Banks 2002; Gibson noisy-channel 2013; Feldman &
  Friston precision=gain; MacWhinney Competition Model conflict-validity) — NOT a linear cue-sum (which reaches neither
  domain; two on-disk wrong approaches fenced: scalar-over-fused inert, margin-gating HARD_FAIL); grounded thematic-fit is
  construction-independent (non-canon 0.688 vs surface 0.039). **OUR-INVENTION-flagged:** the reliability estimator (the
  surprisal/route-conflict gate) is the sole un-built piece of the flagship follow-on. **hdlab:** TWO landings QUEUED (Q111,
  dedicated) — swap the default eval to modern UD-EWT + retire degenerate McGuffey-as-primary (diffuse across ~9 hdlab files;
  re-baselining implications); land the existential/expletive-"there" subject-override into `graded_role_assigner` + rebuild
  the who-did-what cache. **CORPUS-AGE CONFOUND STATUS: role eval now MODERN (UD-EWT), coref eval MODERN-ish (19c LitBank,
  owner-DONE); GAP — no single modern NARRATIVE corpus on the shelf has BOTH gold coref AND gold roles (46.6% of modern
  core-args are pronouns, string-identity-invisible).** Self-correction: 87% of the reported "inversion wall" was the solver's
  own existential-"there" gold mislabeling (fixed); genuine inversion is a PARSE problem (83% quotative, landed rule handles it).

- **2026-08-30 — THE COREF RESIDUAL IS A HARD-PHI-AGREEMENT VIOLATION, NOT A FOCUS/CENTERING GAP: the flat Centering Cb /
  Grosz-Sidner focus-stack is REFUTED as the residual's fidelity gap** (from integrated `the_coref_residual_needs_a_discourse_focus_stack`,
  owner-DONE, SOLVED/EXCELLENT; reverified 45/45 first-hand, recomputes through the real `graded_antecedent_pick`). A faithful
  push/pop focus stack given the STRONGEST oracle segmentation (gold quote spans + paragraph breaks + entity-topic-shift)
  diverges from finer token-locality in **1/420** and does NOT beat it (0.481 vs 0.479 NOT_SEP; twin ties) — the ~50-60% focus
  share was a speculative by-elimination estimate, now disproven. **The real, brain-faithful lever = HARD PHI-AGREEMENT on the
  candidate pool:** the substrate's `_gn_compat` is PERMISSIVE (unknown person/gender/animacy pass), so the pool (~45 candidates)
  admits grammatically-impossible antecedents — above all the discourse PARTICIPANT (the narrator "I"/"we", the most salient
  entity, grabbed for every "he"/"she"). **PINNED:** person-feature agreement (the speech-act "persons" vs the 3rd-person
  "non-person"; Benveniste 1966; Mancini 2011 person-violation N400) + animacy (an obligatory selectional constraint;
  McRae/Ferretti) are OBLIGATORY, immediately-established, cross-linguistically UNIVERSAL anaphora constraints (Cysouw 2003;
  Silverstein 1976); **HARD EXCLUSION is MORE faithful than a graded down-weight** — recall 1.000 confirms the corpus essentially
  never violates it. GENDER is the PRINCIPLED EXCEPTION (a freshly-named entity's gender is not established at the pronoun, so it
  cannot fire causally; positive gender was a leak using future mentions). **OUR-INVENTION-flagged:** the refined pure-participant
  proxy (≥50% 1st/2nd-person mentions AND never 3rd-person-narrated = the true narrator, not a talkative character) + the lexical
  animacy lexicon. **Validated through the ACTUAL landed resolver:** lifts n=9139 0.786→0.841 (+0.054 CI-sep, recall 0.996);
  residual 0.057→0.219; **generalizes** (1st-person +0.147, 3rd-person +0.006 no-regression, threshold-robust, no-gold-NER beats
  gold = anti-cute-trick). **hdlab:** `is_discourse_participant` + `phi_agreement_keep` appended to `graded_coref_pick.py`
  (additive/opt-in, callers byte-unchanged); reader-wiring coupled with the assembly. **Convergence:** this + the coherence-prior
  refutation + the static-KB-dead drills now TRIANGULATE the coref residual as a GRAMMAR-FILTER problem (candidate-set quality),
  not a world-knowledge / focus / interference problem. Residual not closed: they/them (animacy-unconstrained), finer
  clause-locality, ~2-3% semantic core.

- **2026-08-30 — THE CAUSATION TENDENCY INPUT IS BUILT: a 4-cue additive Wolff force-sum resolves CAUSE-vs-ENABLE
  for tendency-ambiguous verbs** (from integrated `causation_typing_needs_a_patient_tendency_estimator`, owner-DONE,
  SOLVED/EXCELLENT; reverified 22/22 + 8/8 MODERN + 3/3 generalization first-hand). The `force_dynamics_typer` read
  CAUSE/ENABLE/PREVENT from the VERB, but tendency-ambiguous verbs ("the key opened the gate" ENABLE vs "the wind
  opened the gate" CAUSE) need the patient-tendency bit (lexicon-capped 0.500). **PINNED:** the tendency signal is a
  patient-side FORCE SUM T = magnitude + affordance + directional + letting, sign(T) = concordance with the affector
  (Wolff 2007 force-sum + concordance read-out; Wolff & Song 2003 patient disposition + gravity as force terms; Talmy
  1988 causing-vs-letting — LETTING is a DISTINCT mechanism: the affector removes a restraint, not patient tendency).
  Held-out 1.000 beats BOTH real floors CI-sep (lexicon 0.500 AND the proven magnitude term 0.675); the combination
  rule is proven ADDITIVE vs winner-take-all (+0.337 CI-sep); added cues win ONLY where magnitude is silent (coverage).
  **OUR-INVENTION-flagged:** the affordance/letting lexicons (affordance labile-half CSKG CapableOf-corroborated,
  inert-half core-physics; verb-gate DERIVED from the causative-inchoative alternation, not a hand-list; inclined-surface
  schema IS-A-grounded, generalizes to knoll/ravine). **The NEURAL ENABLE-vs-CAUSE dissociation is an honest UNPINNED GAP.**
  **hdlab:** landing QUEUED-BUT-GATED — promote `_patient_tendency.py` as the typer's tendency input, but the causation
  LIVE-WIRING is BLOCKED on a word-sense / literal-vs-figurative / amod-attachment gate (every residual over-fire is a
  sense/attachment error; the estimator is conservative — fires 0.9% on unfiltered web text — and correctly abstains on
  the figurative/agentive majority). That gate is the DEMONSTRATED boundary + the packaged prerequisite.

- **2026-08-30 — GOALS/ToM × TIME COMPOSITION IS BUILT: a per-agent BELIEF TIMELINE that answers "what did A know at time T"**
  (from integrated `the_reader_has_no_belief_timeline_what_an_agent_knew_when`, owner-DONE, SOLVED/EXCELLENT; reverified 70/70
  first-hand, scaffold-free — recomputes the live e2e from source). Generalizes `belief_partition` from an n=1 snapshot to n
  ordered observation-gated changes: belief_A(X,T) = the latest event about X that A OBSERVED with order ≤ T, persisting
  between observations (Dowty inertia), ordered by the REAL `temporal_order_register`, read out on the substrate's OWN
  belief_partition FHRR organs. **Capability (not the constructed 1.000): LIVE end-to-end 0.902 [0.805,0.976] vs the
  timeline-agnostic (current-belief-only) floor 0.463 [0.317,0.634], CI-separated**, with the REAL observation-cue extractor
  (`perceptual_access_ledger`, 0.951) in the loop; oracle 1.000, gap 0.098 = the observation front-end residual. Composition
  with the REAL time register is LOAD-BEARING (register-order 1.000 vs narration-order 0.000 on flashback prose). **PINNED:**
  per-agent belief separate from reality (TPJ/mPFC, Saxe); observation-gating seeing→knowing (Wimmer & Perner); sample-and-hold
  persistence (Dowty; the frame problem); register-ordered chronology (Reichenbach; MTL); curse-of-knowledge decoupling
  (Birch & Bloom). **OUR-INVENTION-flagged:** the FHRR bind() algebra (unpinned neurally, defensible computational model —
  SEM/Franklin 2020), the closed inference-schema set, thresholds/tempering. **hdlab:** landing QUEUED (Q111 — promote
  `experiments/belief_timeline.py` → `hdlab/belief_timeline.py`, default-off standalone, built purely on belief_partition/
  binding/graded_temporal_context; reader wiring coupled). The ToM dimension moves from a single current-belief snapshot to a
  full over-time timeline (stale belief / dramatic irony / deception). Next: the observation-cue front-end residual (the 0.098
  live gap).

- **2026-08-30 — DISCOURSE-LEVEL CAUSAL-NETWORK EDGE-TYPING IS A DEAD REAL-TEXT LEVER: a rigorous three-fold-enumerated
  NEGATIVE that BOUNDS the CAUSATION dimension** (from integrated `causation_is_typed_per_clause_not_across_the_causal_network`,
  owner-DONE, SOLVED/STRONG; reverified 15/15 first-hand, scaffold-free — recomputes every headline incl. the real-text
  negative). The Wolff typer types CONSTRUCTED cross-event edges perfectly (NET 1.000 vs placeholder 0.271, isolated from
  single-clause 0.729, built-across by a 2nd intentional front-end feeding the SAME typer) — a MECHANISM demo. **But on REAL
  cross-sentence causation the typer 0.158 (3/19) does NOT beat majority-CAUSE 0.842 (16/19)**, enumerated with counts: real
  cross-sentence non-CAUSE causation is (1) RARE (prevention/enabling packs WITHIN a clause = the single-clause typer's
  domain), (2) lexically UNCOVERED (genuine ENABLE uses open/unlock, absent from the FrameNet force lexicon; abstains 13/19),
  (3) MENTAL for the bulk (a different brain system). **Two NON-CIRCULAR positives survive and are load-bearing for fidelity:**
  graded necessity reproduces Trabasso & van den Broek's causal-weight ordering (rho 1.000 vs twin p95 0.771 — the discrete
  CAUSE/ENABLE/PREVENT read-out is a lossy projection of a graded necessity rep), and the force-configuration model predicts
  human causal-verb judgments (CICL, Cao et al. 2023: r=0.948 vs shuffle-twin p95 0.350, non-circular — config decoded from
  the stimulus, target is independent human data). **hdlab: NO landing** into real causal-network typing (net-zero,
  brain-faithfully); the graded-necessity read-out is a constructed demo (not landed); the human validation confirms the
  already-landed `force_dynamics_typer`. **ROUTE CLOSED:** causation value lives in the single-clause typer + the
  graded-necessity representation + modern-corpus revalidation (the p1 corpus-migration removes the 200yr LitBank/McGuffey
  confound this drill flagged). Do NOT build a discourse edge-typer expecting a real-text capability win.

- **2026-08-30 — THE DISCOURSE-FACT REASONER, MEASURED TWO-SIDED ON REAL TEXT (REFINE): world knowledge is a
  LOW-VALIDITY cue for competitive coreference, and the brain correctly gives it near-zero weight** (from integrated
  `the_discourse_fact_reasoner_is_unvalidated_on_natural_text`, owner-DONE, SOLVED/EXCELLENT; reverified 11/11 first-hand,
  scaffold-free). The parent organ scored 0.998 on a CONSTRUCTED population with idealized extraction + exact KG edges;
  on real LitBank (100 novels, SELF-extracted facts, no oracle) the fact-bridge fired blind does NOT beat the salience
  floor (DEV weight 0; forced-on HURTS 0.68–0.78 vs floor 0.805 CI-sep below). A rich-entity action-history model (93%
  coverage) ALSO collapses — the **law**: for the hard cases the gold antecedent is the LEAST-mentioned entity, so ANY
  discourse-content bridge (type OR history) is anti-correlated with it → the syntactic binder owns the residual, not
  memory. **PINNED:** world knowledge integrates as a continuous graded Bayesian PRIOR (McRae 1998; Metusalem 2012;
  Kehler & Rohde 2013), NOT via a reliability gate — so the measured net-zero is the CORRECT brain-faithful calibration,
  and NO observable gate recovers a win (oracle ceiling only +0.021). **Positive domain (honest, gated):** on the ~15%
  fact-present sliver, fusing the fact into the real resolver LIFTS 0.837→0.961 CI-sep (twin crashes); on the 85%
  complement it HURTS blind → unconditional weight 0. **hdlab:** NO landing into competitive coref (net-zero,
  brain-faithfully) and NO fact-reliability gate (intrinsic dead end) — the organ's value is fact-GIVEN downstream tasks
  (QA / bridging), a future landing. **TRIANGULATES** the assembly's independent coref-residual drill (both measured a
  commonsense KB dead ~2-3% on the anti-typical residual) → the residual is discourse-focus / syntactic-binder bound,
  NOT world-knowledge bound (a strong two-drill convergence; the next problem = a Grosz-Sidner focus stack). ⚠️ the
  strongest "net-zero = correct calibration" equivalence claim is VET-pending — do not let a brief lean on it un-VET'd.

- **2026-08-29 — THE ASSEMBLY: the live reader's role path is WIRED through parse → event-semantic router → graded binder,
  and it beats the positional incumbent end-to-end** (from integrated `wire_the_predarg_frontend_and_binder_into_the_live_reader`,
  owner-DONE, SOLVED/STRONG; reverified 10/10 + 6/6 + 2/2 first-hand, the +0.247 role lift reproduced THROUGH the live
  `SituationReader.read()` class). This is the first POSITIVE assembly result — validated role organs beating the live reader
  on the exact instrument a prior generic wiring LOST on. **Fidelity findings (load-bearing for the next phase):**
  (1) **the LANDED `predicate_argument_frontend` has a QUOTATIVE-INVERSION gap** — it computes the COMM VerbNet class but uses
  it only for recipients, never to assign the postverbal speaker of "said Fred" as AGENT; adding it is +0.253 CI-sep and is
  the single largest role error on narrative dialogue. PINNED-in-principle (FrameNet Statement / VerbNet say-37.7 / eADM
  animacy proto-agent, Bornkessel-Schlesewsky 2006); the exact positional mechanism is OUR-INVENTION-UNDER-TEST.
  (2) **`situation_reader`'s role path was POSITIONAL/parse-free**; routing a parse through the router + a good-enough
  positional FALLBACK lifts role accuracy +0.225 CI-sep. The parse is a CONSTRAINT SOURCE not a gate (McRae/MacDonald
  incremental role assignment); the HYBRID fallback is Ferreira good-enough dual-route (PINNED) and halves regression.
  (3) **the "parse-then-route" SHAPE is itself a fidelity gap** — skilled reading assigns roles INCREMENTALLY word-by-word
  before a full tree (MacDonald 1994 / McRae 1998 / Frank & Bod 2011); the faithful next build demotes the parse to ONE
  graded cue (the islanded `hdlab/thematic_role_labeler` Competition Model is the existing substrate). (4) **COPULA /
  predicate-nominal roles are an unhandled residual, 7× larger on real literature** (15.5% no-verb on 19c prose vs 2.1% on
  McGuffey) — a copula-argument rule is a higher-value fix on real text than McGuffey suggested. (5) **the archaic-prose
  parse is NOT a who-did-what wall** (the real arc parse TIES gold, -0.005 NOT_SEP; recovers 93.6% of governing-verb
  attachments on Dickens) — converges with the retired corpus-age parse confound; who-did-what is bound by COREFERENCE,
  not parse quality. (6) **the coref residual is DISCOURSE-FOCUS / topic-shift bound, NOT world-knowledge bound** — a
  research drill BUILT an oracle and measured a commonsense KB resolving only ~2-3% (WordNet 0.02 / CSKG 0.028 at 0.868
  coverage), refuting the solver's own initial meaning-bound hypothesis; the brain-faithful lever is a Grosz-Sidner (1986)
  focus-STACK / Kehler-Rohde QUD entity-tracker (structural, KB-free) — the seeded next problem (⚠️ that oracle cell is
  disk-verified but NOT independently VET'd; VET "KB is dead" before a brief leans on it). **Honest bound (surfaced to the
  owner, caps the grade at STRONG):** vs the content-lemma COUNTING floor the wired reader wins +0.264 CI-sep on the
  incumbent's inputs but only +0.022 (CI touches 0) on its OWN matched representation — per the "recompute the floor on the
  item's own representation" rule the matched store is the fair floor, so the reader went from LOSING to counting (prior
  attempt) to TYING/edging it while decisively beating its prior self; the clean CI-separated word-counting win is NOT yet
  reached (the coref residual is the remaining lever). hdlab 3-part diff landed by strategy (Q111).

- **2026-08-29 — THE SITUATION MODEL now has the ENTITIES(state) dimension: a per-entity STATE-HISTORY register** (from
  integrated `the_situation_model_tracks_no_entity_state_history`, owner-DONE, SOLVED/EXCELLENT; reverified 61/61 first-hand
  after regenerating the full metrics — the committed artifact was a `--no-real-baseline` smoke run, a setup issue not a
  defect). Closes the gap the SPACE/TIME entries flagged ("entity STATE history is ABSENT"). **PINNED:** aspect binds a
  state to an entity and routes it to the entity/resultant layer (Ferretti/Kutas/McRae 2007); states default-persist
  (Dowty); the perfect's currency is a CANCELLABLE default, NOT entailed-closed → pluperfects are NOT auto-closed (a
  research drill corrected a naive auto-close design); telic = closable target-state + permanent occurrence-fact
  (Parsons/Kratzer); state MATCHING is the ATL semantic hub (Patterson 2007), not lexical. **REJECTED (drill):** an aspect
  confidence-discount — Vos et al. 2025 found the perfect is the MORE reliable state cue (opposite the hypothesis), so it
  was correctly not built. **Measured:** TRACKING 1.000 vs the strongest stateless floor 0.719 (twins lose, empty register
  = chance, distance-robust); SEMANTIC guarded WordNet matcher 0.950 vs exact-string 0.350 (3 load-bearing guards —
  privative / open-vs-closed scale / typed antonymy; "is X unwell?" matches "ill"); **LIVE-ORGAN SERVE — improves the
  ACTUAL hdlab CorefReader on state-decisive same-gender pronouns from chance 0.54 → 0.96** (register re-ranks the real
  coref's candidate pool by state-consistency; the shuffled-states twin collapses; the live coref genuinely resolves
  real-LitBank, baseline 0.327/582). **OUR-INVENTION-swept:** the extraction patterns + antonym lexicon + interval
  representation. **DEVIATIONS:** real-prose extraction is coverage-0.331 / precision-~0.65, bound by spaCy on 19c syntax
  (the shared corpus-age parse cap — retired at aggregate by the archaic integration but real for extraction); the interval-
  CLOSURE (antonym-supersession) channel has ~0 natural incidence in LitBank (proven on construction gold). **Landing
  QUEUED:** the spaCy-free CORE → `hdlab/state_register.py` (sibling of `location_register`), extraction adapter stays
  experiment-side; wiring into the ENTITIES/coref stack is coupled reader work (part of the assembly).
- **2026-08-29 — THE SITUATION-MODEL CAUSATION DIMENSION now has a FORCE-DYNAMIC TYPER (CAUSE/ENABLE/PREVENT); the live
  `_read_causation` was a connective/adjacency PLACEHOLDER** (from integrated `causation_has_no_force_dynamic_typing`,
  owner-DONE, SOLVED/EXCELLENT; reverified 16/16 first-hand). **Mechanism PINNED:** force dynamics (Talmy 1988; Wolff 2007)
  — CAUSE/ENABLE/PREVENT fall out of a discrete truth-table over (patient-tendency, concur/oppose, endstate-reached);
  precedence GATES (the integrated TIME register — 1.000 vs 0.000 serve), force dynamics TYPES, plausibility validates.
  Typing beats BOTH the placeholder (0.929 vs 0.190) AND precedence-only CI-sep on connective-neutral pairs; force-class-
  shuffle twin loses; PREVENT killer 0.900 vs 0.000 (only force dynamics represents a prevented endstate). **OUR-INVENTION-
  WITH-A-MEASURED-BOUND:** the verb-lexicon (FrameNet Causation family, 422 verbs — EXTERNAL, escapes the construction-proof;
  ENABLE barely lexicalized, 1/391) + the patient-tendency input (world-knowledge — a lexicon caps CAUSE-vs-ENABLE at 0.500
  for tendency-ambiguous verbs, but Wolff's force ARITHMETIC recovers it from AFFECTOR MAGNITUDE: weak→ENABLE/strong→CAUSE,
  a glass-box estimator lifts 0.500→1.000). **APPLICABILITY BOUND:** most narrative causation is connective-linked clause
  pairs (the Trabasso NETWORK level) that force dynamics LABELS but a verb lexicon doesn't type. **CITATION CORRECTION:** the
  causation meta-analysis is Feng, Wang, Liu, Wang, Tian & Fan (2021) Front. Hum. Neurosci. 15:666179 (localizes discourse
  causal inference generally; does NOT dissociate CAUSE/ENABLE/PREVENT) — NOT "Kang et al. 2021" (a misattribution in the
  brief/scoping/probe). **Landing QUEUED** (promote `_force_dynamics_lexicon.py` + a TYPED `CausalLink` into
  `situation_reader._read_causation`). Deviation: large-scale automatic-extraction real-text unestablished (#1 follow-on).
- **2026-08-29 — CORPUS-AGE PARSE CONFOUND: SUSPECTED-UNMEASURED → MEASURED-BOUNDED (RETIRED for the aggregate — organ-level
  conclusions that trust the spaCy parse STAND)** (from integrated `role_assignment_is_untested_on_archaic_literary_prose`,
  owner-DONE, SOLVED/EXCELLENT — a rigorous negative + a built fix; reverified 26/26 first-hand). **The wholesale fear is
  REFUTED:** spaCy's subject-ID is NOT CI-separably degraded on 19c literary prose (LitBank 0.94 ≥ modern 0.89, flat to 40+
  tokens; 70% of literary subjects are easy pronouns); correcting ALL 59 role errors in the coref cache moves coref accuracy
  by −0.0009 (a shuffle positive control DOES move it 0.61→0.53, so the null is meaningful; ~10–20% error needed to degrade,
  actual ~0.6%). So every organ that reads the spaCy role (coref subjecthood, Centering tier, SPACE motion gate, who-did-what)
  is NOT confound-capped in aggregate — a standing worry is retired. **ONE CHARACTERIZED EXCEPTION:** subject-verb INVERSION
  ("replied he" → spaCy tags "he" a direct object) + archaic morphology, +0.22 CI-sep, ~4–12/1000 verbs (dialogue). **FIX
  BUILT (PINNED — Competition Model/eADM; Bresnan; Iatridou & Embick; Pinker & Ullman): a glass-box POSITION-DOMINANT +
  cue-OVERRIDE subject stage** (case / conditional-trigger / locative-inversion unaccusative-class / quote-aware +
  a stored archaic-morphology lexicon) — inversion 0.47→0.83 CI-sep, twin loses, register-invariant, lifts modern too
  (no regression); the cue-first REPLACEMENT was self-refuted (position-dominant+override is faithful, = `graded_role_assigner`'s
  design). **EME EXTREME:** Shakespeare (165× denser morphology) collapses spaCy's POS tagger (subject acc 0.07) but the
  cascade + stored lexicon recovers to 0.75 (respects case — thee-accusative control 0.78). **Landing QUEUED** (add the
  cue-override subject stage to `graded_role_assigner` + rebuild the who-did-what cache) — a concrete INPUT to the assembly (p3).
- **2026-08-29 — THE REGISTER WRITE PATH IS FIXED (asymmetric leaky recency write + salience-gated consolidation); and the
  SUPERPOSITION-REGISTER FORM IS NOW PINNED AT THE READOUT LEVEL (a partial retirement of "VSA binding unpinned")** (from
  integrated `the_register_write_path_has_a_hard_capacity_wall`, owner-DONE, SOLVED/EXCELLENT; reverified 11/11 first-hand).
  **The write mechanism:** a CONTINUOUS asymmetric leaky/recency write `S = λ·S + bind(role, item)` holds recent-4 recovery
  = 1.000 at every load N∈{16..768}, where the STRONGEST flat floor (flat sum read by the landed `decode_serial` theta-gamma
  readout — not a strawman) collapses past N=64 (0.100@256); CI-separated from N=128 (+0.825→+0.975); shuffled-key twin
  ~0.02. **PINNED:** asymmetric leaky recency = MEASURED/PINNED-WEAK (Warden & Miller 2007; Konecky 2017 primate-PFC
  monotonic recency gradient; geometric λ^age is the faithful per-trace form; the graded curve 1.00/0.958/0.508 reproduces
  the 66/45/39 shape — a hard bounded QUEUE is a STEP and is LESS faithful). **The single-store trade is fundamental** (leaky
  UNIFORM collapses 0.45→0.019 → a 2nd store is brain-necessary — NOT an option). **Second store:** a salience-gated commit
  into the existing `HDFactStore` — salience = weighted-OR(prediction-error, schema-congruence) (SLIMM U-shape; Tse
  2007/2011; van Kesteren 2012; Lisman-Grace; Redondo-Morris) — recovers 0.643 of salient events vs the FIFO/eviction-order
  floor 0.247 (+0.395 CI-sep); **commit-most-salient, NOT oldest-evicted = PINNED (P=0.78); PE MUST be an INDEPENDENT
  channel** (the self-derived-salience negative control does NOT beat FIFO — faithfully reproduces the on-disk
  `exp_attention_salience_reliability_gate` HARD_FAIL; VTA/LC compute PE in a separate circuit). **FIDELITY DEEPENING:** the
  single-timescale leak is a first-order approximation — the brain holds a SPECTRUM of timescales (Bernacchia 2011 power-law
  reservoir; Murray 2014 hierarchy); a multi-timescale cascade extends the recency window ~3× CI-sep (reach 43 vs single 6)
  without sacrificing recent, reach stays FINITE (2nd store still needed). **AUDIT UPGRADE (Watters 2026, PMC12893052):**
  primate frontal WM is a GAIN-WEIGHTED SUPERPOSITION that BEATS slots → **the substrate's superposition-register FORM is now
  PINNED at the population-code READOUT level** — a dent in the "VSA binding is UNPINNED → our-invention" framing: it is
  unpinned at the bind() ALGEBRA level, but the superposition READOUT form now has direct primate support. **DEVIATION
  remaining:** not run real-text end-to-end (the wall is an FHRR-algebra property, content-agnostic — the synthetic load
  sweep is the correct instrument; the reading-score lift is a landing follow-on); the salience channels are MODELLED, not
  read from the live PE/MDL organs. **Landing QUEUED** (a `leak` param, default-off/byte-identical, + a `register_consolidation`
  salience-gate helper — full diff in `PROPOSED_HDLAB_DIFF.md`).
- **2026-08-29 — THE SITUATION MODEL NOW HAS A DISCOURSE-FACT-STORE + BRIDGING RESOLUTION organ (the comprehension→REASONING
  frontier), PROVEN on inter-sentential fact-decisive reference; and the coref-residual lever is REFINED — it is the
  SYNTACTIC binder, NOT the fact store** (from integrated `situation_model_has_no_discourse_fact_reasoning`, owner-DONE,
  SOLVED/EXCELLENT; reverified 25/25 first-hand). **NEW organ:** a reading-built, queryable per-entity discourse-fact store
  + 2-hop bridging RESOLUTION (glass-box, no LLM) recovers inter-sentential fact-decisive reference the fact-BLIND reader
  cannot (0.998 vs 0.504 chance, +0.494 CI-sep, ALL controls at chance — info-free twin, KG-only-null, ablation; the
  KG-only-null at chance closes the parent's "KB connects but can't discriminate" puzzle — it lacks the discourse-specific
  binding). **PINNED:** the COMPUTATION (Garrod-Sanford BONDING/RESOLUTION; Kintsch CI; hippocampal relational binding +
  pronoun-driven concept-cell reactivation; Haviland-Clark +181ms bridging cost). **OUR-INVENTION-UNDER-TEST:** the FHRR
  representation + confidence threshold. **FIDELITY CLOSURES BUILT:** (1b) the 2nd bridge hop's symbolic hard match →
  GRADED PPMI+SVD distributional coherence (ATL PDP analog) that GENERALIZES to held-out edges 0.700 vs symbolic chance
  0.492 (ATL-distributional deviation partly CLOSED, not just named); (1c) the dense FHRR bundle's crosstalk wall (~K/D
  capacity law) is held FLAT to K=512 by hippocampal PATTERN SEPARATION (relation-indexed, Marr 1971 DG) — dense is adequate
  at D≥1024 for realistic per-entity load K~64, sparse/indexed is the faithful scaling store. **COREF-RESIDUAL entry
  REFINED:** the earlier "the residual's real lever is the situation model accumulating specific-discourse facts" is REFUTED
  by measurement — a reading-built fact store is DEAD on the anti-typical residual (oracle 0.039) because the residual gold
  is freshly introduced (mean 0.65 facts, 58% zero) and bound intra-sententially (Centering Cb-absence; Sturt 2003). The
  residual's lever is the **intra-sentential SYNTACTIC binder** + richer p1 semantics; the fact store serves INTER-sentential
  reference (its actual population), not the residual. **DEVIATION remaining:** L1 accuracy is on a CONSTRUCTED population
  (idealized extraction + exact KG edges); real-text is unmeasured (the #1 follow-on). **Landing QUEUED** (new organ,
  discourse-age-gated, FHRR, relation-indexed; wired for QA/next-event/bridging/ToM, not a coref patch).
- **2026-08-29 — THE SITUATION-MODEL TIME DIMENSION now has a QUERYABLE before/after register (Zwaan-Radvansky event-
  indexing TIME; Reichenbach E/R/S; hippocampal-entorhinal temporal context / MTL time cells — PINNED)** (from integrated
  `situation_model_has_no_tested_temporal_order_comprehension`, owner-DONE, SOLVED/EXCELLENT; reverified 8/8 first-hand).
  A queryable before/after register scores 1.000 vs the naive "telling order = event order" floor 0.272 (twin loses;
  flashback positive control 1.000 vs 0.000); real prose has narration order wrong on 8.7% of event pairs (a live signal).
  **Representation MEASURED:** discrete toposort is adequate for ordering accuracy + robustness; the continuous magnitude
  line (transitive_ordering) reproduces the human distance-effect + calibration signature but NOT accuracy and NOT the
  forward asymmetry → keep discrete primary, layer continuous as a confidence read-out. **Serve:** temporal order constrains
  causal DIRECTION (1.000 vs 0.000). **Deviations recorded:** (a) tense EXTRACTION used a fixed 3-token "had"-window
  (OUR-INVENTION placeholder for the brain's clause-level aux→participle syntactic dependency) — partially fixed here (a
  clause-pluperfect binder, recall 0.911→0.941); (b) perfect ASPECT's resultant-STATE channel is DROPPED (27% of
  "had"-pluperfects are copular "had been X" — a different dimension, the ENTITY/state channel — Ferretti/Kutas/McRae 2007);
  (c) the continuous line is a settled magnitude, not a drifting TCM context, so it lacks forward-contiguity asymmetry.
  **Landing QUEUED** (promote `_temporal_order_register.py` → hdlab + fix `situation_reader._read_timeline`/`_read_causation`).
- **2026-08-29 — THE WHO-DID-WHAT CAP IS A HYBRID (metric-artifact + a small binder lever + a discourse-specific-memory
  residual), NOT a missing structural Cb binder; ACT-R base-level activation is ALREADY the optimal structural binder;
  pronoun→event binding is FOCUS-DRIVEN** (from integrated `pronoun_to_event_binding_caps_who_did_what`, owner-DONE,
  SOLVED/STRONG; reverified 13/13 first-hand). **REFINES the earlier name-clustering §2b framing** (which located the
  who-did-what cap at pronoun→event binding). A brain-faithful clause-level graded binder (graded Centering cue-competition
  via `graded_competition` + gender agreement + person-exclusion) DOES lift who-did-what CI-separated over the ACT-R
  incumbent (LIVE 0.143→0.226 +0.083; re-instrumented event-set 0.249→0.385 +0.136; random twin loses all 3 splits), BUT
  the lift is MODEST (~18% of the +0.44 headroom) and decomposes into THREE parts, each measured: **(1) a METRIC ARTIFACT**
  — the live who-did-what readout scored most-common-verb-per-sentence, discarding multi-event clauses; re-instrumenting as
  a situation-model EVENT-SET recall (over `situation_model_accumulate`) lifts the perfect-binding ceiling 0.589→**1.000**
  (the "39% undecodable" was not a capability limit) — the single highest-leverage fix; **(2) a small candidate-set/binder
  lever** — the graded binder + gender agreement + person-exclusion, a MODEST generic lift (NOT the brief's named Cb cue:
  the clause_role-shuffle twin is beaten only 1/3, and on CLEAN teacher-forced binding ACT-R base-level activation is
  ALREADY optimal — every geometry-heavy hand-config is WORSE, so the tracked Cb/clause_role adds ~0); **(3) a
  discourse-specific-memory residual** — the anti-typical core, PROVEN recoverable by a within-document entity-event
  affinity oracle (66% cov, beats its twin +0.138) where generic typicality is DEAD (coherence/selectional prior 0.029,
  loses to twin) → the residual needs the phase-1 SITUATION MODEL (an entity-keyed event/fact memory accumulated while
  reading), NOT a KB or coherence prior (both measured dead — the same anti-typical Winograd core as the coref-residual
  entry). **Mechanism:** pronoun→event binding is FOCUS-DRIVEN (Grosz/Joshi/Weinstein Centering; a persistent Cb focus
  register; the event indexes onto the focused entity; resolution is a confirmatory readout — Gernsbacher Structure
  Building; Zwaan-Radvansky event-indexing). **No hdlab landed this round** — STEP-1 (re-instrument the metric) + STEP-2
  (wire the graded binder onto the live path) are COUPLED live-path/measured-no-regression work, QUEUED; STEP-3 (wire the
  built-but-unwired `decode_set` + `CausalLinkRegister` into who-did-what on the sparse multibank) is the successor problem.
- **2026-08-29 — CORRECTION: the read-terminal divnorm rule is READOUT-CLASS + LOAD, not "every read-terminal bundle";
  and the register divnorm is OUR-EXTENSION-UNDER-TEST, NOT PINNED** (from integrated
  `read_terminal_bundle_stores_normalize_per_component_not_pooled`, owner-DONE, a rigorous negative / PARTIAL EXCELLENT;
  reverified W1–W11 ALL PASS first-hand). **REFINES/REFUTES** the earlier §2b implication that "a read-terminal bundle
  must be pooled-divisive-normed, never per-component." **Corrected rule (measured per-caller + literature-grounded):**
  per-component renorm (`S_i/|S_i|`) distorts a bundle's DIRECTION; pooled divisive norm (a SHARED scalar — Carandini-
  Heeger, ratio-preserving) preserves it, so divnorm ≥ per-component **only for a DIRECTION-SENSITIVE read, the gap grows
  with STORE LOAD, and is LARGEST for the gain-matched ITERATIVE serial decode** (register serial 0.37→0.99); MODEST for
  per-slot argmax; UNUSED by low-load/coarse tasks. Among all enumerated `bundling.bundle` callers only
  `situation_model_accumulate` + `multibank` have BOTH overload and the serial readout — already switched; every other is
  measured neutral-to-harmful (typer HURTS −0.0375 at low load; cosine/goal_achievement NULL) → keep per-component.
  **Three gating conditions:** (i) benefit needs OVERLOAD + a direction-sensitive readout — a shared pooled divisor is
  ARGMAX-INVARIANT, hence inert for pure winner-take-all; (ii) do NOT stack an automatic normalization gain onto a pipeline
  that already carries an explicit learned precision/reliability weight (measured-harmful — the brain leaves per-source RAW
  magnitude intact because magnitude IS the reliability code; PPC MLE); (iii) the map's "no caller re-binds" is false (the
  typer sub-bundle is a re-bound unbind key, though inert). **Fidelity labels:** pooled divnorm at a DECISION/combine
  population = **PINNED** (measured LIP/OFC/MSTd, 11 sources); at a hippocampal/WM memory-register READOUT (the register
  divnorm) = **OUR-EXTENSION-UNDER-TEST** — an exhaustively-searched absence (4 lanes, ~28 sources; closest misses ruled
  out — Bhatia 2019 wrong locus, Buschman 2011 is ENCODING, Hahn 2021 wrong species; WM-capacity THEORY converges on
  global divnorm — Schneegans/Bays 2024, Wei/Wang/Compte 2012 — so right computational CLASS, not circuit-measured).
  **DO NOT claim PINNED for the register divnorm.** per-component magnitude-erasure = **OUR-INVENTION** (every fast
  biological divisor is pooled/shared, never per-component — 5 mechanism classes, zero counter-examples). **NEW gap
  located (measured):** register CAPACITY is set at the WRITE path, not read — the flat running-sum has a hard capacity
  wall (recent-recovery 0.125 @256) read-norm cannot move; the brain-faithful fix is an ASYMMETRIC CONTINUOUS leaky/recency
  write (reproduces the primate-PFC 66/45/39 recency gradient; Warden-Miller 2007/Konecky 2017 = MEASURED/PINNED-WEAK), a
  single-store trade needing a content/salience-gated hand-off into the existing `HDFactStore` (NOT a new CLS mechanism) —
  packaged as a new build problem. **No hdlab change landed** (the result is "no further switching").
- **2026-08-29 — SPATIAL-ROLE ASSIGNMENT IS GRADED EVENT-SEMANTICS (preposition-telicity + VerbNet event-class + animacy +
  the constructional caused-motion gate), NOT a curated motion-verb list; and there is NO shared predicate-argument
  front-end — the role organs are ISLANDED** (from integrated `no_shared_shallow_predicate_argument_front_end`, owner-DONE,
  PARTIAL/STRONG; reverified 14/14 first-hand). **Scope fact:** `situation_reader` (inline positional who-did-what),
  `location_register._goal_node`, and `parse_goal_extraction` each re-derive argument structure inline with their OWN
  passive detectors; the landed `thematic_role_labeler` / `graded_role_assigner` / `incremental_parser` / relcl resolver
  read `WIRED` in the registry but `gate_decision: WIRE_CANDIDATE`, `used_by` = tests only (registered+witnessed, NOT on a
  live path). **Mechanism:** the brain types spatial roles by GRADED cue-integration — the PREPOSITION's telicity as the
  primary Place-vs-Path cue (Jackendoff Place/Path; Talmy Figure/Ground; Zwarts boundedness), modulated by the verb's
  VerbNet event-class and object animacy; place vs path are separable networks (Kemmerer & Tranel 2003: frontal operculum
  vs supramarginal gyrus); caused-motion is CONSTRUCTIONAL (Goldberg — binds the goal to the moved THEME, any verb can
  enter, "she sneezed the napkin off the table"). A curated motion-verb list is the wrong SHAPE. **Validation:** on FrameNet
  1.7 FE gold (58,808 items) the event-semantic router recovers location/path/source/recipient/direction — five roles the
  conflating inline rule scores exactly 0.000 on — all CI-separated, info-free twin below each; theme/agent above; goal-vs-
  recipient mislabel 27.7%→9.1%; caused-motion 8/8. **Bounds:** goal RECALL loses to the blunt inline grabber (precision/
  recall trade); the goal-vs-location boundary at shared prepositions (at/in) is GRADED by verb telicity (a hard Destination
  gate trades goal +0.061 for location −0.073); the spatial-role ceiling is PP-ATTACHMENT (batch arc parser UAS ~0.79 is a
  placeholder — oracle-parse recovers path +0.18/location +0.10/source +0.10; a verb-led anticipatory attacher [Altmann &
  Kamide; pMTG expectation + LIFG builder] recovers a MODEST CI-sep slice, the full incremental-parser swap is the bigger
  lever) — NOT a representation wall (richer-rep drill negative). **Brief correction:** the "coref caused-motion 'to X'
  residual" does NOT exist in coref.py — it lives only in `location_register._COMM_TRANSFER_BLOCK`. **QUEUED (one careful
  landing, not yet landed):** create `hdlab/predicate_argument_frontend.py` (the event-semantic router + v1 parse helpers +
  live-nltk VerbNet lookup + WordNet place-typing, composing the landed binder/passive/animacy organs) + route
  `situation_reader` default-off + de-dup the 3 inline copies with measured no-regression — a ~300-line multi-dependency
  port + run-the-reader work, a dedicated effort (the validated mechanism stays green in `exp_shared_predarg_frontend_v2`).
  **Component fidelity:** agent/theme binder + PP-role router + caused-motion gate are now
  BRAIN-FOUNDATIONAL; the parse/PP-attachment is a PLACEHOLDER with a proven brain-faithful partial fix; the single-cue
  `thematic_role_labeler` is a placeholder to deprecate.
- **2026-08-29 — THE COREF RESIDUAL IS THE ANTI-TYPICAL WINOGRAD CORE, a SEMANTIC/WORLD-KNOWLEDGE bound — NOT a
  coherence-prior, NOT parse-quality, NOT a static KG** (from integrated `the_reader_has_no_coherence_next_mention_prior`,
  owner-DONE, a RIGOROUS NEGATIVE = full pass; reverified 11/11 first-hand). **REFINES/REFUTES the earlier coref
  two-term-Bayes sub-claim** (that the ~19% structural residual is the coherence-PRIOR-decisive half of a
  LIKELIHOOD×PRIOR computation). Measured on the LitBank competitive-pronoun residual (n=205, TEST, doc-bootstrap): a
  faithful coherence next-mention prior (selectional-fit + thematic, Bayesian-product fused, DEV-tuned) recovers 0.068
  but its 20-shuffle **info-free twin recovers MORE (0.100, NOT_SEP)** — it does not beat its own noise (oracle ceiling
  2.9%). **SIX** independent brain-faithful channels are all dead/anti-predictive: coherence prior, fine linear distance
  (37.6% oracle but UNGATEABLE — regresses structure-decisive ≥ it fixes), item-level structural-proxy cues (Kush 2013,
  0/205), **clean-parse structure on cross-domain GAP (modern Wikipedia, BELOW chance 0.256 → the wall is
  SEMANTIC_WALL_NOT_PARSE_WALL)**, WordNet selectional (2.0%), ConceptNet/CSKG commonsense (2.8% DESPITE 86.8%
  coverage — the KB *connects* every candidate but cannot *discriminate*). **UNIFYING INSIGHT:** the residual is BY
  CONSTRUCTION the anti-typical cases (gold is NOT most-recent/max-subjecthood/most-frequent), so every typicality-tracking
  cue is anti-predictive — ONE structural reason for six identical failures. The **positive control passes** (the SAME
  prior flips 8/8 selectional + 8/8 implicit-causality constructed pairs where the structural likelihood is at chance) →
  the mechanism is faithful and works; the population lacks the cases. **NET: the ~0.78 pronoun-coref ceiling is a REAL
  bound for a glass-box no-LLM structural resolver; the two-system boundary is SYNTAX×SEMANTICS×WORLD-KNOWLEDGE, not
  LIKELIHOOD×coherence-PRIOR.** The residual is a defer-and-flag case (the parent's Track B entropy abstain), not a
  resolve case. **Real levers = separate follow-ons:** the SITUATION MODEL accumulating specific-discourse entity facts +
  reasoning (Garrod-Sanford RESOLUTION; the brain builds this-discourse knowledge BY READING, not from a static KG) +
  richer DISTRIBUTIONAL semantics (the ATL PDP hub is distributional, NOT symbolic — a KG is not implementation-faithful;
  the p1 lane). **LANDED:** only the separately-measured pool cleanup (+0.022 CI-sep, twin loses) — a person-feature
  agreement filter (`is_first_second_person_artifact`/`keep_after_pool_cleanup` in `hdlab/graded_coref_pick.py`); the
  coherence prior / fine-distance / structural-proxy / static-KG cues were all NOT landed (measured dead).
- **2026-08-28 — THE LEARN-FROM-READING LEARNER IS VALIDATED + SAFE TO GROW THE FOUNDATION ONLY BEHIND A CLS GATE
  (default-OFF): the brain-faithful lever is CONTEXT SHAPE (grammatical relations), NOT the update rule** (from
  `optimize_and_validate_the_learner_before_it_grows_the_foundation`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  re-verified FIRST-HAND — BAR1 + BAR4 + the CLS safe-growth flip all PASS, recomputed off the landed vectors). The most
  consequential organ (it can GROW the static offline-built foundation) validated to the owner's demanded standard.
  **PINNED / measured:** (1) a DEPENDENCY-TYPED (grammatical-relation) distributional learner beats the ±2-window
  PPMI-SVD baseline on the SIMILARITY axis CI-separated at matched 15M scale (SimLex 0.270 vs 0.210, +0.060; SimVerb
  0.119 vs 0.084, +0.034; 2/3 populations — WordSim relatedness stays the window's, the PREDICTED dissociation), info-free
  twins lose, DEP_TYPED > DEP_UNTYPED isolates the relation TYPE, ~2.5× more data-efficient. **(2) The update-rule
  premise is REFUTED — this CONFIRMS DEVIATION #2 (the sign()/averaging-machine line): SGNS == shifted-PPMI factorisation
  (Levy & Goldberg 2014) and CBOW == counting is already landed, so ONLINE == BATCH; 'update the brain's way (online/from
  error)' is a proven dead end — the lever is WHAT it learns over, not HOW it updates.** (3) BAR3: under a
  reliability-weighted combiner the learned channel is NET-NEUTRAL-not-harmful in the full pool (the supervised WordNet
  channel dominates its own golds); the window→dependency upgrade net-improves the reading read-out CI-sep; the
  one-pool combiner regresses where the dissociation-aware one does not. **(4) THE SAFETY GATE (the durable finding):
  growing the meaning by reading HELPS downstream comprehension (who-did-what 0.071→0.149, info-free growth controls fall
  below baseline = real structure), BUT a NAIVE overwrite CORRUPTS ~25.6% of previously-correct meanings (uniform across
  confidence = genuine knowledge loss, not churn). A CLS-FAITHFUL keep-both-stores update (ENSEMBLE_MEAN — the
  hippocampal+cortical dual store; Norman & O'Reilly CLS) cuts corruption ~3.3× to 7.9% (CI-sep) while keeping 71% of the
  gain; a rate-limited α=0.25 blend keeps 84% at 18.5%; accuracy SATURATES while corruption climbs monotonically toward
  the naive value — the CLS signature (slow replay-preserving integration beats wholesale overwrite). So the naive
  corruption was a MISSING-MECHANISM artifact, not a ceiling.** Fidelity: 4/5 mechanisms pinned; code-decorrelation,
  distributional is-a, curriculum, affect-grounding, grounded-selpref centroid-averaging all tested + rigorously REFUTED
  (null/redundant/over-compressing). **hdlab landing QUEUED (careful multi-module port) — the CRITICAL invariant:
  FOUNDATION-GROWTH STAYS OFF BY DEFAULT, behind the CLS keep-both-stores / regression-checked-rollback gate; the reader
  remains STATIC offline-built until an explicit, gated, monitored growth step.** NET: the learn-at-runtime capability is
  PROVEN-and-SAFE-behind-a-gate but stays OFF; the roadmap the learner traces is validated-learner → the SPARSE-CODE
  store (multibank/sparse-DG) → RELATIONAL REASONING (transitive_ordering).

- **2026-08-28 — NAME CLUSTERING IS NOT THE WHO-DID-WHAT CAP: a RIGOROUS NEGATIVE that CORRECTS the coref §2b entry — the
  head-token name branch is a STRONG floor (head=surname), and the who-did-what cap is PRONOUN→EVENT BINDING + the
  register FAN, not name clustering** (from `the_name_branch_shatters_one_character_into_many_entities`, integrated
  SOLVED/EXCELLENT [rigorous negative], owner-DONE; witness re-verified FIRST-HAND ALL 9 checks PASS + the register-lift
  arm +0.0149 CI-sep). **CORRECTS the immediately-prior coref §2b framing** (which — from the brief STRATEGY packaged —
  said "name/nominal clustering shatters 65.6% of multi-name entities → caps who-did-what, oracle-coref 0.62 vs binder
  0.17"): the solver BUILT the brain-faithful complete-or-separate person-identity-node organ (PIN — Bruce&Young 1986;
  CA3-completion/DG-separation; conflicting-given-name VETO = pattern separation; ACT-R salience tie-break) + a
  full-span+entity-type cache loader, then the disk REFUTED both premises. **(1)** The organ TIES the strong floor (B³-F
  0.785 vs the live head-token-Jaccard floor 0.770, NOT_SEP; more PRECISE 0.90 vs 0.82 but trades recall) — because the
  head token IS the surname, single-token clustering already unifies surname-family forms; the brief's own full-span fix
  BACKFIRES (0.705 CI-sep below, over-merge); info-free twin loses. **(2)** Decomposition of the 0.17→0.62 who-did-what
  gap: swapping the organ in does NOT lift who-did-what (+0.010 NOT_SEP); PERFECT pronoun binding on the SAME head
  clusters recovers the WHOLE gap (HEAD_OPB 0.606 vs 0.161, **+0.444 CI-sep**), and given perfect pronouns better name
  clustering adds **+0.000** — and unifying aliases actually HURTS who-did-what (HEAD_OPB 0.606 > ORACLE 0.562 = the
  register FAN effect). **So the who-did-what cap = PRONOUN→EVENT BINDING + register capacity, NOT name clustering.**
  **PINNED:** structured person-node slots (given/surname/title/gender) are the right representation for the single-novel
  timescale; the head=surname floor is strong. **Deviations/levers to record:** (a) the real dominant lever is
  clause-level graded PRONOUN→EVENT binding (+0.444 ceiling), which needs the tracked-but-UNUSED `clause_role`/Centering-
  Cb topicality wired into the graded scorer — this is now the **3rd measurement** flagging clause_role/Cb as
  tracked-but-unused; (b) the sparse `MultiBankAccumulateRegister` (built, and its divnorm+serial readout LANDED this
  session, but NOT WIRED into the reader) lifts who-did-what +0.0149 CI-sep on the oracle config (masked on the live
  system until pronoun binding is fixed) — the register FAN is real; (c) same-surname disambiguation ('which Miss
  Bennet') is rare (~80 resolvable/100 novels) and every brain cue measured (Centering-Cb topicality; the eldest-daughter
  convention) is null-or-worse against an info-free twin — the eldest fact needs an entity-fact store we lack (a missing
  organ, not forbidden knowledge). **hdlab landing QUEUED (small, opt-in):** the full-span+entity-type cache LOADER +
  an opt-in default-off `run_person_node_clustering` for high-precision same-surname CHARACTER separation; do NOT replace
  `_resolve_name_branch`. **NET: the highest cross-cutting leverage is the entity-keyed FACT/EVENT store (multibank,
  built-but-unwired) + clause-level pronoun→event binding — NOT name clustering.**

- **2026-08-28 — THE VERB-POLYSEMY WALL IS BUILT: a glass-box event-FRAME disambiguator beats most-frequent-sense with
  CONTEXT (reordered access) + a per-verb reliability GATE, and lifts the downstream event-miner — a SELF-CORRECTION of a
  wrong 'MFS is a wall' verdict** (from `no_glass_box_verb_sense_disambiguation`, integrated SOLVED/EXCELLENT, owner-DONE;
  all three witnesses re-verified FIRST-HAND — witness 11/11, BAR-3 HARD_PASS, BAR-2 gated-context > MFS). **PINNED
  (research-validated, a 4-lane brain-foundational drill):** verb sense is selected by a frequency PRIOR (reordered
  access — Duffy/Morris/Rayner) + a near-categorical argument-structure CONSTRUCTION cue (Goldberg; Levin 1993) + the
  COMPLEMENT-TYPE discriminator ('saw him leave'=perception vs 'saw that S'=cognition — Barwise & Perry 1983; Sweetser
  mind-as-body) + holistic stored-unit IDIOM retrieval (Jackendoff; Cutting & Bock) + graded thematic FIT + a
  reliability-gated CONTEXT cue, combined through the substrate's own `graded_competition`, with Frazier & Rayner
  UNDERSPECIFICATION as the default. **THE CORRECTION (the discipline in action):** the solver first concluded 'MFS is a
  wall' (PARTIAL); the OWNER caught it (a brain-faithful mechanism must match the brain — 'brain-faithful losing =
  presumed impl-bug until proven structural'); the omitted lever was CONTEXT, and the key move was a **per-verb
  RELIABILITY GATE (Friston precision-weighting)** — un-gated context HURTS the broad task, but trusting it only for the
  163/1379 verbs where it beats MFS on train flips it to a robust win. **Numbers:** BAR-2 gated context beats MFS on the
  broad frame-alternating multiclass (Δacc +0.007 CI [+0.002,+0.012], McNemar p=0.003, override precision 0.558);
  info-free shuffled-label-context twin loses below null p95. BAR-3 (the load-bearing downstream lift): the mined
  MOTION-event decision — the exact call the ToM ledger makes — DISAMBIG+context 0.685 [0.655,0.713] beats the
  un-disambiguated verb-string front-end 0.611 [0.580,0.642] CI-sep, McNemar p=8e-06, twin loses. **Deviations to
  record:** (a) the additive→softmax combiner has an accuracy-optimal ARGMAX but only APPROXIMATELY-calibrated confidence
  (ECE ~0.21) because the cues are not conditionally independent — 'additive→softmax = Bayesian posterior' is structurally
  isomorphic, not exact; (b) the win is over the UN-DISAMBIGUATED front-end and TIES the per-lemma-MFS-binary oracle (the
  value is REMOVING false motion events, not beating an oracle prior); (c) CONTEXT is IN-DOMAIN (SemCor) — out-of-domain
  bootstrap REGRESSES (0.761→0.700), so **the bottleneck is IN-DOMAIN sense-tagged data, not model cleverness or volume**
  (in-domain oracle +0.045 headroom); (d) CONTEXT does not help the perception/speech confusion (shared contexts — needs
  semantics the no-LLM invariant precludes). **hdlab landing QUEUED (careful spaCy-coupled multi-module port):** the IDIOM
  stored-unit lexicon (1852 phrasal + 566 object MWEs) is the spaCy-FREE FOUNDATION that can land first (a shared
  MWE-flagging asset); do NOT promote a WSD organ. **NET: the verb-polysemy wall that bit the ToM extractor + the mined
  gold is BUILT; the coarse EVENT-FRAME is a candidate SHARED PRIMITIVE to wire into situation_model + location_register +
  the ToM ledger (a queued wiring follow-on).**

- **2026-08-28 — THE REGISTER'S PER-COMPONENT BUNDLE RENORM WALL IS RESOLVED: the brain-faithful fix is POOLED DIVISIVE
  NORMALIZATION, and it generalises to a SUBSTRATE-WIDE rule for read-terminal bundles** (from
  `the_register_bundle_renorm_breaks_the_serial_readout`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `test_register_divisive_norm.py` 8/8 re-verified FIRST-HAND). The register's per-component renorm (`S_i/|S_i|`,
  `hdlab/bundling.py` default) — a non-invertible per-channel magnitude-erasure — is the OUR-INVENTION outlier that breaks
  the theta-gamma serial readout. **PINNED computation:** a cortical/hippocampal population SUMS its inputs (linear
  superposition) and controls magnitude by **DIVISIVE NORMALIZATION** — dividing the summed response by a **POOLED gain**,
  ONE scalar over the pool (Carandini & Heeger 2012, canonical cortical computation) — plus homeostatic synaptic scaling
  (Turrigiano 2008). A pooled/scalar divisor is a global rescale that preserves the linear/relative structure exactly, so
  the strongest component stays largest and suppress-and-repeat still decodes. **Numbers:** serial:per-component 0.367 →
  serial:divisive 0.988 @M=64 (+0.62 CI-sep), TIES the raw-sum ceiling at every load; argmax NO-REGRESSION and IMPROVES
  0.529→0.644 (scale-invariant → bit-identical to raw-sum argmax); info-free twin 0.027 loses; PARAMETER-FLAT (serial=1.000
  across every C-H sigma + homeostatic target → the OPERATION, not a tuned number). **POSITIVE CONTROL:** even the
  gain-matched serial readout cannot recover the per-component store (0.367 vs 0.988) → the STORE norm is the constraint.
  **One divisive normalization serves BOTH the argmax cleanup AND the serial readout — no raw-sum shadow copy needed**
  (the brief's fidelity question, answered positively). **COMPOSE (measured):** on the DEFAULT multibank backend (M=384/8
  banks) serial 0.733→1.000, argmax 0.654→0.765 → the p2 store-distribution lever + this norm fix are the 12-16× compose.
  **LABELING (2 adversarial drills):** pooled divisive normalization is DIRECTLY CONFIRMED in sensory/decision cortex but
  its application to a WM/memory register is **OUR-EXTENSION-UNDER-TEST** (not PINNED; pooled precedent Eliasmith NEF/SPA,
  Frady/Kleyko/Sommer 2018); the NEGATIVE half is well-grounded — per-component instantaneous magnitude-erasure has NO fast
  biological analogue (Turrigiano scaling is slow/weight-level/structure-PRESERVING). **Honest scope:** M≥96 is a TRUE
  capacity bound (divisive serial == raw-sum serial, both fall), NOT a norm win — the measured M-transition IS the
  **WM→episodic (CLS) boundary** (normalize a bounded WM bundle vs sparse-DG-pattern-separate a large one), i.e. exactly
  the p2 sparse-store lever; so this norm fix and p2 are the two halves of CLS and they compose. **GENERAL SUBSTRATE RULE
  (owner's evaluate-adjacent-components directive applied — `ADJACENT_COMPONENTS_brain_fidelity_map.md`):** *a bundle that
  is READ (unbind+cleanup, or cosine-compared) — not RE-BOUND as an operand — must be normalized by a POOLED/SCALAR
  divisive gain, never by a per-component nonlinearity.* Every enumerated `bundling.bundle` caller is READ-terminal (none
  re-bind → the per-component default is sub-optimal for its ENTIRE consumer set); the `sign()`-on-a-bundle sites
  (`grounding_acquisition_loop`, `situation_focus`, `role_slot_summarizer`, `event_bundle` — audit ~1001/1176, "graded
  beats sign CI-sep growing") are the SAME wrong-op in a bipolar code. **The per-component renorm's correct scope narrows
  to torus-closure for RE-BINDING an atom only.** Wall status: OPEN → MECHANISM-IDENTIFIED-AND-BUILT. **hdlab landing
  QUEUED (Q111, careful coupled default-off port):** `norm="divnorm"` on `bundling.bundle` + a `bundle_norm="percomp"`
  (default) arg on AccumulateRegister/multibank + the gain-matched `decode_serial_pooled` (the store-norm-agnostic
  generalization of the `decode_serial` landed this session — g≈1 on raw sum → identical); the read-terminal-bundle
  substrate audit is the flagged next candidate brief. NET: the register-readout §2b wall is closed; a substrate-wide
  bundle-normalization fidelity rule is now stated + partially measured.

- **2026-08-28 — THE ~0.65 COREF CAP IS BROKEN + DIAGNOSED ON REAL NARRATIVE, and the fix REVERSES a prior §2b HARD_FAIL
  as population-specific** (from `coreference_is_capped_at_065_on_real_narrative`, integrated SOLVED/EXCELLENT, owner-DONE;
  witness re-verified FIRST-HAND against the current file — ALL 8 checks PASS). The reader's rigid hard-tiered pronoun pick
  (`coreference_resolver._pick_strict_cb`) is replaced by the brain's actual reference computation — **GRADED cue-based
  retrieval** (Lewis & Vasishth 2005; McElree 2003): a softmax over the pinned **ACT-R base-level activation**
  (recency×frequency×role), reusing the LANDED `graded_competition` organ verbatim. **PINNED result:** on LitBank (100
  novels, 50 held-out) competitive pronouns (≥2 gn-compatible priors, n=4693), graded **0.775** vs the incumbent hard-tier
  recomputed same-population **0.603** (+0.172 CI-sep, half-width 0.031); info-free twins collapse (0.055/0.044). **The cap
  was the TIER, and its mechanism is now measured:** the rigid subject-first tier scores BELOW plain recency (0.603 <
  0.717) — it picks subjects ~2.2 sentences STALER because strict-Cb has NO graded recency decay within the subject class;
  the brain's dt^−d decay is exactly what the hard rule discarded (copy-the-computation, made quantitative). **HONESTY
  (MAP-optimality theorem):** graded-argmax == the argmax of the same net → graded TIES ACT-R base-level activation (0.782,
  NOT_SEP); the accuracy win is over the incumbent TIER, and the graded FORM's unique value is the calibrated DISTRIBUTION.
  **Track B (legible uncertainty):** posterior normalized-entropy predicts its OWN errors **AUC 0.806** vs the incumbent
  margin **0.617 same-population** (apples-to-apples); deferring the highest-entropy 33% lifts kept accuracy 0.775→0.894
  CI-sep, random twin flat; gain-invariant for argmax so Track A is untouched. Brain-faithful "flat posterior → defer"
  (Levy 2008; the Nref "hold both" ERP, Nieuwland & Van Berkum 2008). **REVERSES the 08-27 §2b finding** ("cue-based-
  activation coref pick HARD_FAILED −0.1348; resolving WHO is dominated by simple SALIENCE/RECENCY"): that HARD_FAIL was
  **population-specific** (QA-SRL/McGuffey — short, dense, few entities, where the hard Centering tier + pure salience
  excel); on REAL narrative graded ACT-R retrieval is the WINNER and the hard tier is the WORST arm. **The right mechanism
  is population-dependent** — a clean instance of "no number crosses populations." **New PINNED sub-claim:** pronoun
  reference is a **two-term Bayesian computation** (Kehler & Rohde 2013) — a Centering LIKELIHOOD (grammatical
  role/topichood, what we compute) × a coherence-driven next-mention PRIOR (verb-semantics/discourse, what we do NOT
  compute); the ~19% structural residual is the prior-decisive cases (the two-system boundary, not a tuning failure), and a
  slice is LitBank ANNOTATION-FIAT ambiguity (ezCoref) where entropy-defer is the brain-faithful output. Optimization
  levers tested + REJECTED with numbers (parallelism, gender/animacy pre-filter → pool 39.9→39.3 null, lexical IC → frame
  n=0, role-weighting exhausted) → the ~0.78 structural ceiling is DEMONSTRATED. hdlab landing QUEUED (Q111, opt-in
  default-off `run_graded_retrieval` + entropy-abstain; existing behaviour byte-identical). **NET: the coref organ's
  "competitive resolution is the open case" is resolved for the PRONOUN branch; the NEW open case is the NAME/NOMINAL
  branch — it shatters 65.6% of multi-name gold entities (single-head-token cache root cause) and caps who-did-what
  (oracle-coref 0.62 vs binder 0.17), the highest-leverage entity-tracking follow-on.**

- **2026-08-28 — THE MISSING SPACE DIMENSION IS NOW BUILT: a first-class per-entity LOCATION REGISTER (Zwaan & Radvansky
  event-indexing SPACE), COMPOSED with the (entity,role,event) binding, not bolted on** (from
  `situation_model_has_no_spatial_location_dimension`, integrated SOLVED/EXCELLENT, owner-DONE; three witnesses
  re-verified FIRST-HAND — test_location_register.py 13/13, where-is-X HARD_PASS, serves-ToM HARD_PASS). This CLOSES the
  "NO SPACE dimension in the situation model" gap that the ToM §2b entry named as the highest-leverage MISSING organ.
  **PINNED (computation COPIED):** per-entity location STATE as presence intervals `(node, t_open, t_close)`, updated
  ONLY by MOTION events read off the realized **PATH satellite / Source-Goal-Path**, **deixis dominating** (come/return
  vs go/leave — Talmy 1985; Papafragou 2008), **Goal-over-Source** (Lakusta & Landau 2005), explicit RETURN override;
  PERSISTING between updates. Neural referents: hippocampal place / entorhinal grid allocentric map (O'Keefe & Nadel;
  Moser & Moser), parahippocampal place area, Speer & Zacks 2009 (location-change firing during ordinary reading).
  **NOT a manner-verb whitelist** ("she florped out" still departs via the satellite — the whitelist is the
  implementation trap the ToM solver had already proven). **OUR-INVENTION-UNDER-TEST (swept + labelled):** the
  REPRESENTATION — categorical **topological scene nodes** (Rinck, Hahnel, Bower & Glowalla 1997 rule OUT metric/Euclidean
  coords for narrative space), with an FHRR-bound alternative giving the identical answer (round-trip cos 1.000 → the
  SPACE dimension lives in the substrate's own binding algebra). **Deviations to record:** (a) SPACE is the WEAKEST /
  most-effortful event-indexing dimension (Zwaan, Langston & Graesser 1995) → the register is LAZY/on-demand (updates
  only on motion, queries on demand) — a faithful match, not a shortcut; (b) raw-prose motion EXTRACTION is gated at
  **0.909 Goal precision** (VerbNet **Destination-vs-Recipient** event frames + ATL WordNet place-typing + an
  argument-structure gate — the brain's actual Goal-vs-Addressee mechanism, Rappaport Hovav & Levin 2008), residual =
  ambiguous **caused-motion** (throw/send) that carries zero verb-class signal and needs the coref/entity-STATUS of the
  "to X" head (a direct coreference consumer, mapped). **Hierarchy BUILT** (region containment: "in the study" ⊨ "in the
  house" 1.000 vs flat 0.500; Wiener & Mallot 2003; Peer & Epstein 2025) — the cognitive map is nested REGIONS, not flat
  places. **Deictic-center SKIPPED on evidence** (Deictic Shift Theory refuted-as-worth-building: spatial-alone
  discontinuity doesn't reliably cost reading time — Rinck & Weber 2003; tracking ABSOLUTE per-entity location is the
  better choice than a single moving center). Numbers: "where is X at T?" REGISTER 1.000 [1.000,1.000] vs strongest
  stateless floor 0.417 [0.354,0.479] (n=240 construction gold), info-free twin 0.422 landing EXACTLY at floor (100%
  correctly-ordered tracking); distance-flat 0.967 at K=0..20 while windowed/last-mention collapse; SERVES the ToM cue on
  real mined LitBank clauses (0.976 vs lexical 0.500, n=246) → DELETES the inline spaCy-proxy `PresenceState` stopgap the
  ToM residual entry flagged. Convergence MEASURED not asserted (conveyance/passenger-with-vehicle a real brain-can-we-
  can't gap but 1/7182 sentences = 0.01% → documented follow-on). Honest scope: the CI-sep headline is on CONSTRUCTION
  gold isolating TRACKING; the real-prose burden is carried by the serve + the 0.909 gate + hand-verified motions.
  hdlab landing QUEUED (Q111 — careful multi-fn port `hdlab/location_register.py`, default-on gates; point the queued
  `perceptual_access` landing at it). **NET: the situation model's MISSING-organ count drops by one; SPACE is now a
  wired-pending, brain-faithful dimension; coref (~0.65) is confirmed the dominant real-narrative cap AND the resolver of
  the caused-motion residual (p3).**

- **2026-08-28 — REASONING PHASE HAS ITS FIRST PRIMITIVE: TRANSITIVE-COMPARISON over a MAGNITUDE LINE, and the mechanism
  is SELECTED by a MEASURED human signature (not asserted)** (from `transitive_comparison_reasoning_over_the_magnitude_ordering`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness re-verified FIRST-HAND, ALL checks PASS). The reader now reads pairwise
  comparisons (A>B, B>C) and answers the UN-STATED pair (A vs C). PINNED: relational integration by **delta-rule /
  value-transfer settling** (Frank-Rudy-O'Reilly 2003; Dusek & Eichenbaum hippocampal relational memory) onto a bounded
  FHRR **magnitude line** (item_key ⊗ FPE(position) — the parietal ATOM number-line), read natively by FPE — a COPIED
  computation, NOT a symbolic sort. Un-stated-pair sign accuracy 1.000 vs the ASSOCIATION-MATCHED net-win floor 0.500
  (+0.500 CI-sep; the Dusek/Eichenbaum control where association gives zero signal by construction — isolates integration
  from associative strength), twin loses, stated-only at chance; grounded on real words via the landed p1 ruler (human
  concreteness order 1.000 vs 0.673). **Method note for the audit: a distance effect ALONE does NOT distinguish a
  magnitude line from a discrete rank code (both show it as a readout-noise property); the distance-effect DIRECTION does
  — serial chaining gives a NEGATIVE slope (far pairs need more hops), a magnitude line gives the human POSITIVE slope
  (far pairs easier). The human positive symbolic-distance effect + end-anchor effect SELECT the magnitude line and RULE
  OUT chaining.** Two-systems boundary: on a GROUNDED, directly-readable 1-D axis, integration TIES direct-reading —
  reasoning's VALUE is on NOVEL / text-defined orderings you cannot read off (integration 0.845 vs a local reader 0.500
  on never-stated pairs). The GROUNDED bottleneck is the p1 front-end reading CLOSE comparisons at ~60% (the top
  adjacency). hdlab landing QUEUED (default-off `transitive_ordering.py`). This is the comprehension→REASONING phase's
  first organ.

- **2026-08-28 — REGISTER READOUT: the capacity "cliff" is largely an ARGMAX-READOUT artifact; the brain reads a
  superposition by THETA-GAMMA SERIAL DECODE-AND-SUPPRESS (Lisman & Idiart 1995), NOT CA3 attractor completion — and
  the gain is known-key CROSSTALK CANCELLATION** (from `the_register_reads_by_argmax_not_recurrent_completion`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness re-verified FIRST-HAND, ALL checks PASS). CORRECTS the phase-diagram
  audit's own §2b entry (which said "a CA3/SIC joint-completion readout recovers the register cliff argmax 0.644→0.971"):
  the mechanism is not attractor completion — a per-slot modern-Hopfield ATTRACTOR ties argmax exactly (no manifold on
  the register's separated i.i.d. codes; O'Reilly & McClelland 1994). The recovery is theta-gamma SERIAL decode (decode
  strongest → inhibition-of-return → decode next from the residual) reading the LINEAR raw sum, and its gain is
  known-key crosstalk cancellation. Numbers: synthetic D=256 argmax 0.509→serial 0.983 @M=64 (+0.454 CI-sep); real
  LitBank D=1024 INERT on the bulk (<64 events, no false current-task win), recovers the high-fan tail (91 entities ≥64
  events: 0.959→1.000, +0.041 CI-sep). **The readout lever (~2×) is DISTINCT from p2's sparse store (~8×) and they
  COMPOSE to 12–16× at fixed D.** **Help-vs-hurt is real and RESOLVED:** attractor/graded-completion HURTS RANKING (hub
  bias +0.587) — so completion is for RECALL, the graded read is for RANK, and a CA1-comparator exact-match gate routes
  by query structure (beats both blanket policies 0.968 vs 0.802/0.668; refuses spurious resonator divergence at M≥96).
  **New fidelity wall:** the register's per-component BUNDLE RENORM is non-brain-faithful — it breaks the serial readout
  (serial must read the raw linear sum); flagged as the strongest adjacency. The resonator DIVERGENCE at extreme
  overload is a TRUE capacity bound (not a readout artifact) → distribute load = the store (p2). hdlab landing QUEUED
  (additive `decode_serial` + `decode_gated` on AccumulateRegister, no storage change; `cleanup_argmax` stays default).

- **2026-08-28 — READING FORAGING ("what to read next"): the MVT value/gap/LEARNING-PROGRESS forager is REFUTED for
  corpus SELECTION; the brain-faithful mechanism is COMPREHENSIBLE INPUT / ZPD; MVT's faithful role is within-source
  LEAVE only** (from `the_reader_cannot_choose_what_to_read_next`, integrated SOLVED/EXCELLENT, owner-DONE; fast witness
  6/6 + full multi-seed HARD_PASS re-verified FIRST-HAND). The attention/information-foraging + gap_detector entries
  should record: (a) the MVT forager on a value/gap/learning-progress signal LOSES to the fixed curriculum
  register-controlled 3/3 seeds AND its learning-progress arm's info-free twin does NOT lose — the LP signal carries NO
  between-source information (LP = the time-derivative of two noisy estimates, unusable in the few-episodes-per-source
  regime; fraction-known is a directly-observable low-variance state statistic). (b) The WORKING "what to read next"
  mechanism is COMPREHENSIBLE INPUT (Krashen i+1; Vygotsky ZPD; Metcalfe region-of-proximal-learning): read the source
  with the most NEW words in ≥COMP_THRESH-already-known sentences — 0.0813 register-controlled coverage vs FROZEN 0.0314
  / RANDOM 0.0287, CI-sep 3/3 seeds, info-free twin 0.0150 loses. (c) The optimal comprehensibility threshold is
  COMPETENCE-DEPENDENT (LOW at a small seed vocabulary, rising with it = ROPL): stricter 0.85/adaptive arms STARVE. (d)
  MVT's faithful home is the WITHIN-source LEAVE-rule on a grounding-yield currency (Charnov 1976), NOT between-source
  selection; a separate EVC-halt is redundant (the zero-marginal limit the MVT stop-rule already computes). The
  gap_detector's home is per-item novelty, not between-source choice. hdlab landing QUEUED (default-off): corpus_registry
  shelf + comprehensible-input selector + within-source MVT leave. Next fidelity increment: depth-of-encounter (spaced
  revisitation; words need 6–20 encounters, not 4).

- **2026-08-28 — THEORY OF MIND: the OBSERVATION-CUE RESIDUAL now has a brain-faithful mechanism — a per-agent
  PERCEPTUAL-ACCESS REGISTRATION LEDGER — and the landed lexical extractor is exposed as a non-generalising OUR-INVENTION
  stand-in** (from `theory_of_mind_residual_is_the_observation_cue_front_end`, integrated SOLVED/EXCELLENT, owner-DONE;
  4 witnesses re-verified FIRST-HAND). Reading "did agent A witness the change?" is NOT a keyword problem — it is a
  SITUATION-MODEL read: **`observed = RULE0 explicit-narrator-statement (event-local), else RULE1 co-present-AND-in-the-
  perceptual-field, OR RULE2 informed`**, maintained as a STICKY per-agent ledger; **false belief = the ledger being
  STALE vs reality** (maps exactly onto the landed `believed_location(observed, initial, final)` gate). PINNED (Butterfill
  & Apperly 2013 registration; Zwaan & Radvansky event-indexing SPACE dimension; Talmy 1985 PATH-lives-in-the-satellite-
  not-the-verb; Harris & Koenig 2006 testimony). **The landed lexical extractor is an OUR-INVENTION stand-in that does NOT
  generalise: 0.808 on its own phrasings → 0.500 (chance) on real corpus prose**; the ledger reads 0.992 [0.980,1.000]
  CI-sep, lifting the end-to-end belief accuracy 0.50→0.99 past the 0.821 residual. **New first-class sub-mechanisms /
  walls to record:** (a) **OCCLUSION / perceptual availability** as a PINNED PER-MODALITY FIELD (vision needs light+LOS+
  not-closed-opaque+attending+awake; audition penetrates dark/thin-barriers but needs a non-silent event; touch needs
  contact) over an occluder ontology, UNKNOWN as a first-class value — the precisely-diagnosed NLP-vs-brain wall (FANToM
  Kim 2023; Ullman 2023 transparent-bag), previously unnamed in the ToM entry. (b) **VERB POLYSEMY** as a cross-cutting
  text-front-end fidelity wall (the brain uses full lexical semantics; our glass-box reader cannot) — distinct from coref.
  (c) **SEQUENTIAL registration**: belief over a CHAIN = the last change the agent perceived (sticky per-agent cell,
  world-track separate) with the MOTION-PERSISTENCE exception (watched-into-an-occluder registers the destination) and
  IGNORANCE (registration=None) as a state distinct from false belief; epistemic markers are EVENT-LOCAL. `belief_partition`'s
  binary gate should extend to this. (d) **TWO-ROUTE dissociation**: an EXPLICIT-STATEMENT route (narrator asserts the mind-
  state; local) vs a SPATIAL-INFERENCE route (needs the FULL incremental situation model — Zwaan); on intact 3-sentence
  WINDOWS the spatial route is at CHANCE because the cause is out-of-window (PROVEN a windowing artifact: full-text spatial
  route holds 0.99 at K=0..20, windowed→0.00) → the deployed front-end must run over the running model, not windows.
  **The diagnosed walls are OCCLUSION + verb POLYSEMY, NOT coreference.** hdlab landing QUEUED (promote
  `hdlab/perceptual_access.py` + extend `belief_partition` to a sequence ledger — must consume the coref/situation-model
  organs to avoid a spaCy dependency). **Surfaced a genuinely MISSING organ (highest-leverage adjacency): NO SPACE
  dimension in the situation model — `situation_model_accumulate`/`factorized_entity_store`/`event_bundle` bind
  (entity,role,event) but track no per-entity location-over-time register** (the Zwaan SPACE dimension, PINNED, absent;
  the ledger implements a minimal one inline as a stopgap).

- **2026-08-28 — DIMENSIONALITY (N) IS NOT A FIDELITY/PERFORMANCE LEVER ANYWHERE; the real axis is CODE ORTHOGONALITY (+ readout
  + sparsity), and the substrate is NOT uniformly D=1024** (from `dimensional_phase_diagram_audit_of_the_current_organs`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness `test_dim_phase_diagram.py` 18/18 PASS re-verified FIRST-HAND, positive-control
  cliff seen 0.526→0.988). A full-pass NEGATIVE on the owner's "did we probe each piece at full dimensionality" question:
  the load-sensitive REGISTER decodes FLAT across D=256..8192 (0.60→0.61, CIs overlap) → **STRUCTURAL @1024** (the wall is
  front-end LINKING — ACT-R 0.17 vs oracle 0.60 — not capacity); MEANING is sparse-EXACT (K*≈256, not rising at 1024); and the
  memory stores were ALREADY pinned to **N_DIM=8192** on disk → **the substrate is NOT uniformly D=1024** (correct any claim that
  says so). **PROMOTE CODE ORTHOGONALITY / FEATURE_OVERLAP to a first-class fidelity axis:** it DOMINATES N (ρ0.0→0.651 vs
  ρ0.8→0.026 at fixed D), real WordNet codes ARE correlated (0.039 vs 0.025 ideal) and cost capacity, and DG sparse pattern
  separation recovers it (dense M32 0.742 → DG-sparse 0.979). This makes concrete the standing flag that our
  **iid-random / maximal-orthogonality code is an unflagged OUR-INVENTION** — the fix is DG decorrelation before autoassociative
  storage, NOT more dimensions. **Store families obey FOUR distinct capacity laws** (vector-bundle ~N/log2(N); sparse Willshaw
  > bundle; matrix-Hebbian relational ~16·N ≈190× the bundle = the real multihop store; multi-timescale temporal set by the
  PERIOD spectrum, not 1/√D) → **no single capacity number crosses store families.** Other BEYOND-N verdicts: binding DEPTH is
  NOT a lever (exact-invertible bind, depth1≈depth5); numeric PRECISION bites only at q=2 (sign-binary 0.311 vs full 0.653); the
  register argmax "cliff" is largely a READOUT artifact (CA3/SIC joint completion 0.644→0.971). **Two corrections carried:** the
  synthetic cliff REPRODUCES the closed-form `k_cliff_scaling.k_cliff(N)=0.87·N/log2(N)` (a positive control, NOT a new law); and
  the naive "multihop directedness defect" is a naive-commutative-store artifact — the real `kg_traversal.KGStore`+`multi_hop`
  organ is directed by construction (8-hop clean) and is fine. **DO NOT** raise D as a capacity fix (ruled out everywhere) or
  quote one capacity number across families. hdlab: NONE landed (a negative); proposed follow-on landings QUEUED (CA3/resonator
  readout swap; orthogonality+precision audit axes + DG-decorrelation pre-store check; adaptive readout controller).

- **2026-08-28 — THE SCALAR-MAGNITUDE "RULER" IS COMPOSED + PROVEN, and it re-frames meaning as OPERATION-SPECIFIC: pole+degree
  are ONE oriented place code (not three stacked ops), and the magnitude system is a COMPARISON system where the incumbent
  cosine INVERTS** (from `build_the_composed_scalar_magnitude_meaning_channel`, integrated SOLVED/EXCELLENT, owner-DONE +
  authorized in-session; witness `verify_composed_magnitude_channel.py` ALL PASS re-verified FIRST-HAND). Completes the p3
  meaning-operation-routing line: the composed magnitude channel (dimension-select → grounded ORIENTED signed-magnitude place
  code → markedness fine-degree → FPE-log Weber comparator) beats the strongest single sub-op (+0.081 CI-sep) AND the
  incumbent cosine (+0.40 CI-sep); the word-class ROUTER beats gloss-only (0.616 vs 0.424) AND magnitude-only (0.339) with
  EXACT N/V no-regression. **CORRECTS the "three operations" framing to be MORE brain-faithful:** pole and degree are NOT two
  separable operations — the brain fuses them into ONE oriented place code (opponent pools → peaked log-Gaussian → oriented
  axis: Roitman 2007, Nieder, Verguts & Fias 2004, SNARC), confirmed on-disk (within-scale oriented ordering 0.72 ≈ markedness
  0.77). The faithful decomposition = {dimension-select (semantic control); ONE grounded oriented magnitude place code;
  markedness fine-degree; FPE-log Weber code}. **The magnitude system is a COMPARISON system** (Moyer distance effect;
  Holyoak congruity) — measured as one it beats the incumbent CLEANLY (relative-comparison 0.758 vs 0.552 +0.206 CI-sep,
  distance effect +0.340, semantic-congruity AUC 1.000 where the incumbent gloss cosine INVERTS to 0.215: it ranks antonyms
  as MORE similar than same-pole pairs — a concrete measured instance of "opposition is irreducible / a cosine is the wrong
  operator for magnitude"). **PINNED/INVENTED:** the combination = ONE oriented place code (PINNED); an opponent-pool readout
  is MONOTONE-EQUIVALENT to the linear projection for recovery (the place-code stage is load-bearing, the opponent-readout is
  not — a rigorous negative). `quality_relation` Channel B is LINEAR FPE (uniform-resolution = the WRONG magnitude code) → the
  upgrade to FPE(log) + pole/dim binding preserves Weber (proven on the real degrees) and makes the comparator a native
  `unbind`. **hdlab LANDING QUEUED (careful multi-module port, NOT rushed):** ADD `scalar_adjective_operation`; UPGRADE
  quality_relation Ch.B linear→FPE-log; ROUTE the meaning read-out by word class (gradable adj → magnitude, else gloss; gate =
  has_antonym-or-satellite AND NOT pertainym-relational); wire dimension-select to `semantic_control`. HONEST: the sub-op
  CI-win is concreteness-routing (evaluative dims tie by construction); the gate is coarse; markedness/FPE-log value is
  comparison + the Weber code, not static recovery; the deeper frontier (comparison-class re-anchoring, negativity bias,
  congruity RT) is DATA-blocked, not mechanism-blocked.

- **2026-08-28 — THEORY OF MIND is no longer synthetic-only: first-order FALSE BELIEF validated on REAL TEXT on the
  substrate's own organs; the live reader has NO belief tracking and needs a per-agent belief partition (TPJ)** (from
  `theory_of_mind_is_proven_only_in_a_synthetic_microworld`, integrated SOLVED/EXCELLENT, owner-authorized in-session;
  witness `test_theory_of_mind_realtext.py` 2/2 PASS re-verified FIRST-HAND). The per-agent belief-partition mechanism (an
  agent who did NOT observe a change keeps the STALE binding = false belief; belief tracks KNOWLEDGE not vision) runs on
  `hdlab.binding` + `cleanup_argmax` (not hand-rolled numpy) and scores belief-acc **1.000** on 26 real-English false-belief
  passages, CI-separated over the shared-reality floor 0.357 (which LEAKS the observer's knowledge to the agent and fails
  false-belief), the trivial always-initial floor 0.643, and the info-free twin; true-belief controls (saw/informed) make it
  can-fail; reality intact; robust to location interference. **DEVIATION:** the situation model is SINGLE-PERSPECTIVE; a
  faithful reader needs PER-AGENT belief partitions (Saxe TPJ/mPFC keeps belief separate from the observer's own knowledge).
  **LANDED `hdlab/belief_partition.py`** (`BeliefPartition` + the `believed_location` knowledge-gate; witness PASS; registered
  `belief_partition_v1`, default-off island). **RESIDUAL = the OBSERVATION-CUE front-end** (did agent A witness event E? from
  text — a lexical version 0.808, dropping end-to-end to 0.821): same front-end-is-the-wall class as the verb-argument role
  assigner; route with the reader front-end work. HONEST SCOPE: the gold is AUTHORED real-English narrative (a mechanism
  demonstration, not corpus-generality); first-order only. `hdlab/state_of_mind.py` is coreference, MISLABELLED — do NOT wire
  it as ToM.

- **2026-08-27 — THE ENTITY-STORE "FAN" IS AN ADDRESSING COLLISION, NOT SUPERPOSITION BLUR; the fix is the KEY + the READ
  (finer conjunctive temporal context + SET-RETURN), and dense→sparse is the HIGH-LOAD CAPACITY fix, not the fan fix**
  (from `the_entity_store_is_a_dense_bundle_that_fans`, integrated SOLVED/EXCELLENT, owner-DONE; reverify witnesses
  `test_entity_store_fan.py` 21/21 + `test_entity_store_frontier.py` 26/26 re-verified FIRST-HAND). **CORRECTS the prior
  fan-effect entry** (which called the fan "within-register SUPERPOSITION crosstalk" fixed by "sparse DG k-WTA + CA3
  completion, NOT a pointer"). **Measured on LitBank (28,569 queries, oracle linking):** the fan (decode 0.945@few →
  0.657@many, slope 0.288) is an ADDRESSING COLLISION on a coarse (entity,sentence) key + an ARGMAX read — unique-(entity,
  slot) addresses decode at **1.0000 at every load level**, a top-m read recovers the co-slot set at ~1.0, and 22.7% of
  addresses hold >1 verb. **The dense bundle does NOT lose information.** The faithful fix is a FINER CONJUNCTIVE temporal
  key (TCM continuous drift) + a SET-RETURN read (CA3 context-cued reactivation): slope **0.288 → ~0.000 CI-sep**, info-free
  shuffled-order twin LOSES (1.000 vs 0.502). Sparse coding is NEUTRAL for the measured fan (FINER_CTX === FINER_CTX_SPARSE).
  **Sparse DG's true home = the high-unique-load EXACT-RECALL regime** (holds 1.0 to N=800 where the multibank organ falls
  to 0.78; residual SIMILARITY-gated 3.5× not count-gated) — the brief's mechanism was right for a DIFFERENT regime.
  **The maximally faithful store is FACTORIZED** (sparse DG exact-recall × graded multi-timescale context × within-moment
  order, bound only at storage, read separately): on real LitBank it gets BOTH a flat fan (0.001) AND temporal contiguity
  (0.585) where a single graded key trades them (0.194/0.585) — **independently confirmed by Bausch et al. 2026 (Nature,
  human single-unit: content & context SEPARATE populations bound by timing) + TEM**. Also measured (each with an info-free
  twin losing): reconstructive DRM intrusions (5.5×), event-boundary contiguity cut, path-integration relational transfer,
  a local-rule SR next-event predictor. **NEW PINNED/INVENTED:** set-vs-argmax read + the factorized separate-populations
  store = PINNED (Bausch/TEM); the `rel_margin` set-return threshold = OUR-INVENTION (the CMR race-to-stop is the faithful
  self-terminating stop). **Q1 unification:** DG conjunctive separation and TCM context reinstatement are ONE architecture
  (the finer context IS the drift). **LANDED (cheap core):** `cleanup_set` + `decode_set` SET-return on both register
  backends (witness PASS, registered `situation_register_setreturn_v1`, additive/default-safe). **QUEUED proven-ready:** the
  finer conjunctive key; the FACTORIZED two-system store; schema/gist; race-to-stop; path-integration + SR scaffolds. **Honest
  scope:** the fan fix is retrievability, not a downstream comprehension win; set-return ≈ a pointer on this data (the value
  is the mechanism + graceful degradation in the high-load/partial-cue regime); kWTA partial-cue robustness needs the
  iterative CA3 completer (unfixed). Heavy LitBank-scale validations of the factorized store → remote GPU box.

- **2026-08-27 — COMPOSITION-BY-INDEPENDENT-CONJUNCTION deviation TESTED + RESOLVED at the READ side: the brain-faithful
  CONVERGENT-CUE rule (log-Bayes product of the two posteriors) beats the strongest floor, fused is refuted, and the double
  dissociation is preserved** (from `compose_the_reader_by_convergent_cue_not_independent_conjunction`, integrated
  SOLVED/EXCELLENT, owner-DONE; witness `test_convergent_cue_composed_reader.py` 7/7 PASS re-verified FIRST-HAND). Replaces
  the STEP-18 independent post-hoc AND with `argmax_c [log softmax(epi/tau_e) + w·log softmax(sem/tau_s)]` = CA3 pattern
  completion (Norman & O'Reilly 2003) + reliability-weighted cue combination (Ma/Beck/Latham/Pouget 2006; Ernst-Banks 2002;
  Hemmer & Steyvers 2009). **Held-out n=3681:** convergent **0.7438 beats the STRONGEST floor meaning-solo 0.6998 (+0.044
  CI-sep [0.030,0.058])**; shuffled-MEANING twin collapses (0.041); **shuffled-EPISODIC twin FALLS BELOW meaning-solo** →
  the win needs REAL episodic evidence = genuine convergence (not meaning relabeled); FUSED one-pool loses (+0.384) and its
  lesion read 0.134 < separated entity-solo 0.178; **double dissociation preserved**; lift LOCALISED (rescues 20.5% of
  meaning-solo-WRONG, keeps 97.6% of RIGHT); equal-weight (w=1) below meaning-solo → reliability weighting load-bearing.
  **NEW PINNED/INVENTED line:** the combination rule (product of posteriors) = **PINNED**; the reliability weight `w` being
  **CALIBRATED (not emergent)** = **OUR-INVENTION-UNDER-TEST** (our two cue codes aren't one shared PPC population, so the
  automatic-gain story does not give the cross-cue ratio for free). **The RULE is AT CEILING** (0.744 vs argmax-union oracle
  0.750, NOT_SEP); the residual headroom is the DENSE episodic store, and the gain rises monotonically with episodic
  reliability → **FORWARD HOOK: convergent-cue + p2's sparse DG+CA3 store should COMPOUND** (predicted w→1, larger gain;
  recalibrate on the sparse store when p2 lands). **Straw-floor correction (to the solver's credit):** the STEP-18/brief
  baseline (independent-AND 0.119) is LOWER than either system alone — not a valid floor; the claim is the CI-sep beat over
  meaning-solo 0.70 + the controls. **LANDED `hdlab/convergent_cue_reader.py`** (`convergent_pick`, witness PASS, registered
  `convergent_cue_reader_v1`, default-off ISLAND). Supersedes the "combination rule is a fidelity gap" status of the entry below.

- **2026-08-27 — COMPOSITION FIDELITY: the entity and meaning systems COMPOSE end-to-end (both load-bearing in one reader),
  but the COMBINATION RULE is a fidelity gap — the brain uses CONVERGENT-CUE pattern completion, not an independent
  post-hoc conjunction** (strategy fidelity extension, CONSOLIDATION STEP 18 measurement + STEP 19 brain-foundationality
  drill; `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py`; NOT a solver integration). On a LitBank
  paraphrased pronoun who-did-what task (answer "what did X PURSUE?" when the story said "chased" — needs BOTH the
  pronoun-linked entity AND the paraphrase recognition), composing the landed `salience_binder` (episodic) + landed
  `conceptual_meaning` (ATL) shows **BOTH axes load-bearing**: FULL 0.1190 [0.0976,0.1424] vs ENTITY_OFF (string-identity)
  0.0337 (+0.0853 CI-sep) vs MEANING_OFF (exact) 0.0000 (+0.1190) vs shuffled-binding twin 0.0660 (+0.0530). **FIDELITY
  VERDICT (STEP-19 drill):** (a) keeping the two as SEPARATE POOLS is EVIDENCE-PINNED by the canonical DOUBLE DISSOCIATION
  (semantic dementia spares episodic binding; hippocampal amnesia spares semantics) — the composition RESPECTS this ✅;
  (b) BUT the strict independent AND (FULL ≈ entity-solo 0.167 × meaning-solo 0.700 = 0.117, i.e. treated as statistically
  INDEPENDENT) is only a LATE-MERGE decision (Norris "Merge") — for the RETRIEVAL step the faithful mechanism is CLS
  CONVERGENT-CUE pattern completion where the meaning cue provides TOP-DOWN support to the hippocampal read, so it should
  BEAT the independent product by rescuing weak-binding cases. **DEVIATION (new, under-test):** composition-by-independent-
  conjunction where the brain composes by convergent-cue retrieval. **QUEUED as the READ-side fix** (problem
  `compose_the_reader_by_convergent_cue_not_independent_conjunction`, priority 3) — the counterpart of p2's WRITE/STORE-side
  sparse DG+CA3 fix; both are the content-addressable-retrieval convergence flagged 4× by the entity work. Individual organs
  UNCHANGED / no regression. **Deflations honoured:** absolute FULL low (strict conjunction of two moderate independent
  capabilities on the hardest subset); entity-solo 0.167 = the dense-store ceiling p2 refines (this is a BASELINE); meaning
  keeps the WordNet-circularity caveat.

- **2026-08-27 — MEANING-SIMILARITY IS OPERATION-SPECIFIC PER WORD CLASS, and the adjective SIGNED-MAGNITUDE op clears
  CI-separation AT POWER on an independent human gold; the cosine is wrong for ADJECTIVES ONLY (verbs are already served
  by the gloss); and the magnitude CODE is FPE(log degree), validated to human behaviour** (from
  `the_meaning_read_out_is_one_operation_where_the_brain_has_three`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `verify_perclass_meaning_operations.py` ALL CHECKS PASS, re-verified first-hand). **Resolves the prior "one cosine loses
  adjectives + verbs" deviation and CORRECTS it to ONE class:** the feature-overlap conceptual cosine WINS nouns (0.599)
  and VERBS (0.492 vs blended 0.152 — a definition is a relational description), and loses ADJECTIVES only (0.479<0.585,
  no signed-magnitude structure). **The adjective op = GloVe projection onto a bipolar dimension axis ANCHORED by the
  explicit WordNet antonym relation** — recovers the human magnitude CI-separated over BOTH the incumbent cosine AND the
  info-free random-axis twin on an ADEQUATELY-POWERED INDEPENDENT non-WordNet gold (Warriner VAD + Brysbaert, n~3600–5300,
  the SimLex n=111 power wall RESOLVED): **valence 0.724 vs incumbent 0.165 (+0.559 CI-sep) vs random 0.067 (+0.657
  CI-sep)**, dominance/concreteness/arousal all CI-sep at full power, shuffled-gold twin ~0, **MOYER distance effect
  present** (an analog graded scale, not a binary flag). The n=111 wall was the SIMILARITY-gold instrument (conflates
  dimension-membership with degree), not the op — the magnitude-native RECOVERY/ORDERING task is the right instrument.
  **NEW substructure (deeper drills, each controlled):** (1) **"adjectives" is a 3-WAY class** — gradable-denotational
  (per-dim magnitude) / evaluative (Osgood VAD affect) / classificatory (wooden/medical → the TAXONOMIC noun op is
  already right); a gradability gate routes; (2) the adjective op is TWO sub-ops — **DIMENSION/POLARITY = geometric
  (SemAxis) + DEGREE/INTENSITY = MARKEDNESS (frequency/AoA), NOT geometry** (on WordNet-independent crowd
  intensity-ordering golds the SemAxis is at its random floor while frequency/AoA orders intensity CI-above chance,
  shuffled-freq twin at chance — Horn/Zipf/Greenberg, developmental "big" before "enormous"); (3) **OPPOSITION is
  RELATIONAL not geometric** (raw GloVe cosine separates antonyms/synonyms at AUC 0.356 — INVERTS; opposition needs the
  explicit relation / definitional channel — the SAME antonym relation the landed `wordnet_polarity_propagation` valence
  organ uses → record opposition as a shared relational primitive); (4) **ATOM's single shared magnitude axis is REFUTED**
  on our rep (the 4 dim axes are largely orthogonal, shared component 0.446 ~ random 0.379) → keep per-dimension axes
  INDEPENDENT; (5) **grounding source is per-dimension** — evaluative from antonym poles, denotational (concreteness) from
  Lancaster PERCEPTUAL strength (recovery 0.26→0.53 CI-sep); (6) **the magnitude CODE is FPE(log degree) in FHRR** — the
  substrate's Fractional Power Encoding (`hdlab/binding`, `hdlab/quality_relation` Ch.B) is currently LINEAR
  (uniform-resolution = a linear number line = WRONG); encoding LOG(degree) yields the tuned Weber number-neuron code
  (scale-invariant kernel, log-Gaussian tuning), the **log PINNED by Laughlin efficient coding** (the info-max transform
  of the Zipfian degree is ~log: CDF~log R 0.96 vs linear 0.07), the reference-point comparator = native
  `unbind(FPE_log x, FPE_log ref)=FPE_log(x/ref)` (corr 1.000), and **VALIDATED against 240k human number-comparison
  trials** (the FPE-log kernel predicts human RT rho 0.96 / error 0.92, beats a difference kernel CI-sep, size effect
  CI-sep). (7) **dimension/standard SELECTION = the semantic-control organ** (context selects the scale, 0.661 vs MFS
  0.529 CI-sep) — wire the router to context-override WSD, not a global axis. **CORRECTIONS to the audit:** VerbNet (429
  classes) + FrameNet (1221 frames) are LIVE in nltk (OWNED, not "not-yet-owned"), but the explicit verb op does NOT beat
  the gloss (net-neutral) — keep verbs on the gloss; rating-recovery rho is monotone-BLIND to log-compression/tuned
  coding (validate the code on confusability/comparison, done in PROBE E/H). 🔌 **NO hdlab landed; EARNED proven-ready:** a
  `scalar_adjective_operation` (per-dim bipolar axes, appropriate grounding source, independent axes, opposition from the
  relation, degree from markedness, FPE-log encoded) + operation-ROUTE the meaning read-out by word class (gradability
  gate; noun/verb/classificatory-adj stay on the gloss) + wire dimension SELECTION to semantic-control + upgrade
  `quality_relation` Ch.B linear→log. **Completes the MEANING operation-routing line (p3 of the 3 parallel solvers).**


- **2026-08-27 — NON-CANONICAL role assignment: a routed graded CUE-COMPETITION (Competition Model) beats the front-end
  on non-canonical structure CI-separated; the reduced-relative residual is a verb-subcat SUPPLY bound (broken with
  WordNet) + an ARCHITECTURE gap (incremental parsing + reanalysis), NOT a cue-mechanism defect** (from
  `the_front_end_mishandles_non_canonical_argument_structure`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `test_noncanonical_role_assigner.py` 6/6 PASS, re-verified first-hand). **Scopes the prior front-end "CONVERGED for
  natural-corpus role labeling (gains need DATA not mechanisms)" to CANONICAL/aggregate only** — the NON-canonical slice
  has a real MECHANISM gain. A HYBRID graded cue-competition assigner (MacWhinney/Bates Competition Model: additive
  learned-validity cue integration over the landed `graded_competition` `net_activation`/`map_pick`, morphology/voice
  overriding word order) beats the composed front-end on the pre-verbal/non-canonical slice **0.6000 vs 0.5758 (+0.0242
  CI-sep)**, net-positive overall (+0.0113 CI-sep), canonical PRESERVED, shuffled-validity twin losing, seed-robust.
  **KEY ARCHITECTURE FINDING: a FLAT integrator is NET-NEGATIVE (canonical −0.041, relcl 0.85→0.55) → the faithful
  Competition Model ROUTES (word-order validity stays high, overridden ONLY on marked cues) — it does NOT replace the
  cascade.** Learned validities are brain-consistent (order 1.67, passive_strong 3.23, **passive_weak −2.99** — the
  `-ed` past/participle garden-path correctly distrusted; animacy +0.47, small-but-positive where order is uninformative,
  refining not contradicting "word order dominates"). **The reduced-relative headroom (the 408 bucket, 95.6% REACHABLE →
  a mechanism gap not annotation noise; ~60% relativizer-LESS reduced object-relatives) is a verb-SUBCATEGORIZATION
  SUPPLY bound** — CI-proven (the Trueswell/MacDonald transitivity cue helps monotone in corpus exposure, +0.108
  CI[0.061,0.162] on well-attested verbs, ~0 on unseen) — **now BROKEN with WordNet verb FRAMES (coverage 30%→99%, a
  static asset).** Supplying it EXPOSED the true binding residual: **CLAUSE STRUCTURE — an ARCHITECTURE gap (incremental
  predictive parsing + reanalysis), tested as a rigorous root-caused NEGATIVE**: the incremental-parser+reanalysis route
  lifts the slice but CRASHES canonical (net-negative), root-caused to (a) the reanalysis TRIGGER being
  meaning-representation-limited (oracle-trigger restores canonical → the OPERATION is right, the SIGNAL is weak = the
  12-dim grounded-space ceiling, the standing p1 coupling), (b) parser sophistication on long sentences (NOT a
  Now-or-Never/buffer bound — buffer sweep identical), (c) an unwired COREFERENCE organ (~25% of the bucket). **The
  solver WITHDREW its own "~7 points from coref" overclaim when the anti-gaming twin caught it** (real Centering-recency
  coref scored BELOW a random-antecedent twin; the landed coref organ needs multi-sentence discourse it lacks on isolated
  sentences — do NOT wire blind pronoun resolution here, it net-hurts). **Also: ~1% of "errors" are a metric-fairness
  ruler misfire (right head, wrong span index) — a same-referent-lenient role-span scorer fixes it free.** **Effect on
  the audit:** role assignment's non-canonical residual is UPSTREAM-bound (meaning-representation SUPPLY for the
  reanalysis trigger + the coref organ + the incremental structure-builder), with verb-subcat now SUPPLIED (WordNet
  frames); drop "converged" for the non-canonical slice; keep it for canonical order-dominant items. 🔌 **NO hdlab landed;
  EARNED proven-ready:** a `graded_role_assigner` (robust graded voice + relativizer-less gap + cue-support builder +
  graded competition + offline validities) wired as a HYBRID route inside `resolve_patient` (confident routes
  byte-identical; competition only on the non-canonical fall-through), default-off. **This closes the FRONT-END fix (p1);
  the residual routes to the existing meaning-supply / coref / incremental-parser lines.**

- **2026-08-27 — THE MISSING ATL CONCEPTUAL/DEFINITIONAL MEANING HUB IS BUILT + PROVEN as a second meaning system; the two
  systems DOUBLE-DISSOCIATE; and the deepest finding is that MEANING-SIMILARITY IS OPERATION-SPECIFIC PER WORD CLASS (one
  cosine is the wrong operator for adjectives + verbs)** (from `the_reader_has_no_conceptual_meaning_channel`, integrated
  SOLVED/EXCELLENT, owner-DONE; witness `test_conceptual_meaning_channel.py` PASS, re-verified first-hand). Closes the #0
  next step the meaning-context integration named: the reader had ONLY the associative/co-occurrence system (at chance on
  human meaning-IDENTITY). **BUILT — the amodal ATL CONCEPTUAL HUB (Controlled Semantic Cognition; Lambon Ralph/Jefferies/
  Patterson/Rogers 2017):** a glass-box STATIC asset = per-word WordNet gloss+genus/hypernym feature bag, distinctive-feature
  weighted by global IDF (the sparse-space analog of the ATL's privilege-distinctive-features operation), cosine — NO
  learning, NO LLM. **IDENTITY WIN (bar MET) vs a STEELMANNED competitor** (GloVe-300, not the reader's weak 0.04
  co-occurrence): SimLex-999 (human similarity, OFF-WordNet) **0.5210 vs 0.3705, +0.1505 CI[0.0855,0.2149] CI-separated
  over GloVe's upper bound**; SimVerb 0.4988 vs 0.2199 (+0.2788); the info-free shuffled-gloss twin LOSES (p95 ~0.04–0.065);
  gloss CONTENT alone (zero taxonomy graph) already ties GloVe (0.40) → the win is definitional content, not a WordNet-
  taxonomy lookup artefact. **The distinctive-feature operation earns its keep:** IDF beats UNWEIGHTED feature overlap
  CI-sep (a second confirmation of the `lexical_similarity.py` "unweighted overlap is the INVERSE of privileging distinctive
  features" WRONG-OP). **TWO-SYSTEM DOUBLE DISSOCIATION (the real brain signature, real-but-PARTIAL):** on the SAME SimLex
  pairs, conceptual tracks SIMILARITY (0.521) over association (0.342) while GloVe tracks association ≥ similarity; crossover
  +0.197 CI-sep; and GloVe wins WordSim-353 RELATEDNESS (0.610 vs 0.403) CI-sep → conceptual/definitional = the IDENTITY
  system, distributional/associative = the RELATEDNESS system, each winning its own axis (channels OVERLAP — Mirman 2017 /
  Jackson 2015 — not an orthogonal split). **SUPPLY-DEPENDENT distinctiveness (extends the prior two-systems SOLVED):** the
  literature-proposed ATL covariance-DISTILLATION (SVD+whiten over gloss features) does NOT beat sparse IDF (a fidelity
  BOUNDARY) → one ATL principle (privilege distinctive features), two supply-dependent realisations — DENSE grounding →
  whiten (suppress a dominant shared axis), SPARSE definitional → IDF; the prior SOLVED's "next distinctiveness gain is a
  richer feature SUPPLY" is confirmed (the definitional space IS that supply). **ROUTING vs FUSION reconciled (§4 below):**
  for decontextualised graded RATING a fixed FUSION ties/beats demand-ROUTING (route−fusion −0.030, TIE leaning fusion) —
  semantic control is COMPETITION-GATED (Badre/Wagner; Jefferies) and inert on easy items → **the brief's "route, fusion
  hard-failed" is WSD-SPECIFIC; routing/control's true home is context SELECTION = the already-built semantic-control organ
  (`context_override...`, trigger AUC 0.79).** So the faithful two-channel design = conceptual hub as a 2nd representation,
  DEMAND-ROUTED for identity/similarity, FUSED for graded rating, conflict-gated SELECTION handled by semantic control.
  **THE DEEPEST FINDING (a NEW cross-cutting fidelity principle) — MEANING-SIMILARITY IS OPERATION-SPECIFIC PER WORD CLASS,
  so a single cosine is the wrong operator for two of three classes:** NOUNS = taxonomic feature/genus overlap (the gloss
  channel's home, 0.599); ADJECTIVES = SIGNED-MAGNITUDE distance on a shared oriented scale with opposition = the two POLES
  of one axis (Walsh ATOM/IPS magnitude; Moyer distance-effect; Kennedy degree semantics) — feature-overlap cosine has no
  order/sign, structurally wrong (adj: conceptual 0.479 < GloVe 0.585); VERBS = relational/argument-structure (gloss carries
  it 0.492; GloVe's single blended vector fails 0.152). The adjective op BUILT from OWNED resources (GloVe scale-membership
  + WordNet antonym-pole SIGNED opposition, SemAxis-style; NO new data) lifts SimLex adjectives 0.585→0.623 with the
  INFO-FREE RANDOM-AXIS control LOSING (0.553) — **DIRECTIONALLY confirmed, mechanism nailed, but CI-separation
  POWER-LIMITED (n=111 adj pairs: +0.038 CI[−0.050,0.127] vs GloVe, +0.070 CI[−0.002,0.151] vs random) → a POWER limit,
  not a mechanism failure; honestly NOT allowed to gate SOLVED.** The meaning read-out should be OPERATION-ROUTED BY WORD
  CLASS — the natural home for the semantic-control router (route by word-class demand as well as task demand). **Effect on
  the audit (§6 semantic control / §7 meaning):** the meaning system is now explicitly TWO channels (conceptual IDENTITY +
  associative RELATEDNESS), the ATL conceptual hub is BUILT + validated (no longer "the reader has one meaning system"), the
  distinctive-feature op is supply-dependent, and a new operation-specific-per-word-class principle supersedes "the
  adjective gap is missing supply" (it is a wrong-OPERATION, fixable from owned resources). **Tested-negative, do NOT wire:**
  SVD distillation over definitional features; a task-SWITCH gate for graded rating (fusion wins); the grounded SENSORIMOTOR
  spoke for adjectives (LOSES CI-sep — it is sensorimotor, not scalar-magnitude); a symbolic antonym-flag as if it were the
  mechanism; a GPU learned hub over a SINGLE spoke (premature — earns its keep only reconciling ≥2 heterogeneous spokes,
  Silberer & Lapata 2014). 🔌 **NO hdlab landed; QUEUED proven-ready for the consolidation:** the conceptual/definitional
  channel (default-off, gated on the SimLex/SimVerb margins) + demand-routing + operation-routing-by-word-class, composing
  with the semantic-control router. **p3 of 3 in-flight — its integration COMPLETES the trilogy and fires the CONSOLIDATION.**

- **2026-08-27 — THE SUBSTRATE-WIDE "DISCRETE WHERE THE BRAIN IS GRADED" DEVIATION IS RESOLVED: the discrete parser/
  role-assigner is MEASURED to be the noise→0 argmax COLLAPSE of a graded Bayesian cue-competition, and the maintained
  distribution's ENTROPY is a shared gold-free DIFFICULTY currency that beats the shipped binary route-conflict** (from
  `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `verify_graded_competition_parsing_role.py` ALL CHECKS PASS, re-verified first-hand, scaffold-free on the real QA-SRL
  front-end). **Closes the standing §1 cross-cutting deviation** (surfaced by the incremental-parser + relcl SOLVEDs).
  **The MECHANISM is PINNED, not our invention:** a single graded cue-based competition — additive-log cue activation →
  softmax MAINTAINED DISTRIBUTION over candidate role-fillers — **IS the Bayesian/FLMP posterior for discrete cue
  integration** (McClelland 2013: softmax units exactly compute Bayesian posteriors with `net = log P(h)+Σlog P(e|h)`;
  Massaro-Friedman FLMP; the COPIED operation), and the discrete organs are its **noise→0 argmax collapse** (graded argmax
  == the discrete fixed-priority resolver on EVERY item, 0.0[0.0,0.0]). **THE WIN (difficulty-signal clause of the bar,
  MET):** the maintained-distribution normalized ENTROPY is a valid gold-free difficulty signal — predicts where the
  discrete rule ERRS +0.384 [+0.377,+0.391] CI-sep (n=7200), is CI-sep higher on the literature-hard object-extraction
  constructions +0.420 (Gordon/Gibson, a measure NOT derived from our cues), the settling-view cycles-to-settle
  corroborates (+0.845, McRae normalized recurrence), and **it BEATS the substrate's shipped BINARY route-conflict on REAL
  QA-SRL (AUC 0.646 vs 0.512 near-chance, +0.133 [+0.123,+0.144] CI-sep)** — the continuous graded competition, not merely
  detecting conflict, is the value. Info-free twins LOSE: random-settling −0.004 (null p95 +0.001), shuffled-cue-validity
  +0.071 (~18% of real). **THE ACCURACY CLAUSE IS A THEOREM, NOT A SHORTFALL — record this so the audit STOPS implying a
  graded ACCURACY win is available:** by MAP-optimality (Bishop §1.5) the argmax of the posterior is the accuracy-optimal
  point estimate, so graded competition provably CANNOT beat its own argmax on gold accuracy; graded's unique value is the
  DISTRIBUTION (uncertainty/difficulty/underspecification), never the point estimate. **CROSS-LINGUISTIC CORRECTION** (apply
  wherever the audit repeats "freer-word-order → graded wins"): per MacWhinney/Bates/Kliegl 1984 the accuracy-win
  population is "NO single cue near-ceiling reliable" (GERMAN-style ~50%-ambiguous case), NOT "freer word order" (Italian is
  free-order but single-cue/agreement-dominated); English word-order dominance (93%; ~50% of variance) is a
  correctly-inherited INPUT fact, not a model deficiency. **NEW deviations recorded:** (i) the competition DYNAMICS
  (settling/normalized-recurrence vs racing/LCA/ACT-R) is NEURALLY UNRESOLVED for sentence processing — mark UNPINNED; we
  straddle it (entropy = distributional/race view + cycles = settling view, they AGREE); LCA is the successor if a
  commitment is needed. (ii) argmax is a TASK-TRIGGERED COLLAPSE, not the default output (Swets 2008) — the brain-faithful
  default is a MAINTAINED DISTRIBUTION (underspecification), collapse-to-one a later task-driven step (a buildable
  refinement: expose the distribution). **ONE SHARED GRADED DIFFICULTY CURRENCY (cross-organ):** the maintained-distribution
  entropy is the CONTINUOUS generalization of the relcl BINARY route-conflict (which it beats) and the same currency as the
  predictive reader's surprisal (Levy) and the N400 — record a single shared graded difficulty signal feeding
  N400/write-gating/route-conflict, with attachment and role binding as SEPARATE POOLS (Matchin-Hickok/Friederici/eADM;
  same additive+softmax FORM, distinct cue weights — do NOT fuse). **Honest bounds:** point-entropy is validated for
  DECISION-ERROR flagging, not reading TIME (surprisal/entropy-reduction are the RT currencies, untested here); one
  difficulty measure uses the discrete rule's own error as a gold-free proxy (corroborated by the independent
  hard-construction measure); population largely synthetic + real-QA-SRL generalization; the ACCURACY-win population
  (German ~50% case) is named but UNTESTED; "Beber 2025" is a contested citation (conclusion rests on verified
  Matchin-Hickok/Friederici/eADM). 🔌 **NO hdlab landed; QUEUED proven-ready for the consolidation:** a shared
  `hdlab/graded_competition.py` (additive-cue→softmax, entropy/margin/cycles; argmax == the discrete resolver, drop-in) +
  wire the entropy as the shared difficulty currency; make the softmax gain a PRECISION term (Friston; reuse the
  predictive-reader precision-weighting); expose the DISTRIBUTION downstream (collapse under task pressure). p1 of the 3
  in-flight consolidation-gating problems, now integrated.

- **2026-08-27 — ENTITY TRACKING COMPOSED END-TO-END ON RUNNING NARRATIVE: correct pronoun linking buys cross-sentence
  ATTRIBUTION, NOT anticipatory PREDICTION — a clean, brain-real DISSOCIATION** (from
  `wire_entity_tracking_end_to_end_on_running_narrative`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `test_entity_tracking_end_to_end.py` 7/7 PASS, re-verified first-hand, 183s, on the real
  `hdlab.situation_model_accumulate` register). Composes the two separately-validated halves of entity tracking (the ACT-R
  salience BINDER + the content-addressable PREDICT channel) + coref threads on LitBank novels, varying ONLY how pronouns
  link. **BAR MET on cross-sentence who-did-what** (decode what an entity did at a queried sentence): salience-bound ACT-R
  linking **0.1739 beats string-identity 0.0589 CI-separated** (pronoun subset +0.115, full +0.0249), and the info-free
  shuffled-link twin (pronoun→random compatible entity) **LOSES (ACT-R +0.0731 CI-sep)** → CORRECT binding, not merely a
  link, is the source. **DECISIVE THE OTHER WAY on PREDICTION:** adding the entity state to the discourse gist HURTS the
  next-object predictor (−0.219), correct linking is not better than string-identity (−0.099), and this holds even for
  ORACLE linking (−0.131) → **the value of coreference for the situation model is RETRIEVABILITY of an entity's event
  history, not a predictive prior.** Neurally supported: Step-2 (pronoun→REACTIVATES the referent's stored representation)
  is PINNED by direct evidence (Dijksterhuis 2024 *Science* single-unit; Ding/ten Oever/Martin 2023 MEG), but Step-3
  (reinstatement→improves prediction) is UNTESTED in humans and here measures NULL — the loop does not auto-close;
  item-episodic retrieval (hippocampal) and entity-AGNOSTIC generalized event knowledge (schema/verb-thematic-fit,
  mPFC/cerebellar) are separable systems (Preston & Eichenbaum; Knowlton & Squire; Brown-Schmidt/Duff 2020: amnesia SPARES
  online prediction). **DEEPENING WIN (the cron's purpose): GRADED activation-weighted binding BEATS hard argmax**
  downstream (SOFT 0.2051 > HARD 0.1783, +0.0268 CI-sep) with a uniform-weight control WORSE than hard (0.1322) → it is the
  ACTIVATION weighting, not mere hedging; a temperature sweep is a textbook INTERIOR optimum (peak temp~2.0, both
  winner-take-all and uniform worse) = the divisive-normalization family (Carandini & Heeger 2012: `a^n/(σ^n+Σa^n)` nests
  uniform/graded/argmax; intermediate n is the canonical cortical computation). **Record: mis-binding under ambiguity is a
  graded activation-WEIGHTED multi-entity update (Nref-faithful), the SHAPE pinned, the temperature a fitted parameter (no
  biological constant).** **FAN EFFECT MEASURED** (oracle decode 0.6954→0.6079 as entity event-count grows 1-3→17+) →
  **upgrade the standing dense→sparse deviation from SUSPECTED to MEASURED on running narrative**; the faithful fix is a
  pattern-separated per-entity trace store (sparse DG-style k-WTA conjunctive encode + CA3 attractor completion — NOT a
  pointer, which fixes cross-entity lookup but not within-register superposition crosstalk; Norman & O'Reilly 2003
  explicitly names fan effects), keeping the bundle as a gist. **Honest deflations (reported against self):** the
  string-identity margin is partly STRUCTURAL (a pronoun can't string-match a name → floor ~0 on pronouns by construction),
  so the load-bearing controls are ACT-R>twin and graded>hard; **ACT-R does NOT clearly beat simple RECENCY downstream**
  (+0.0129 NOT separated) — the expensive ACT-R form's isolated-pick advantage does not propagate; only 28% of the oracle
  ceiling (0.618) recovered; the dilution stratification is INCONCLUSIVE (candidate-count proxy saturated: 9,006/9,078 in
  the 3+ bucket). **PROHIBITION honored:** framed as a computational-level decomposition (salience selects → content
  reinstates → conditions readout), NOT a strict serial two-stage brain architecture (Kehler & Rohde; ACT-R additive
  activation; McKoon & Ratcliff resonance argue JOINT scoring). **Effect on the audit:** the coreference/binding + discourse
  situation-model entries gain (i) the measured attribution-not-prediction dissociation, (ii) graded activation-weighted
  binding as the brain-correct competitive SHAPE, (iii) the fan effect promoted to measured evidence for dense→sparse. The
  entity's real contribution to PREDICTION, if any, is its current abstract SCHEMA-ROLE (a SEPARATE organ; Cohn & Paczynski
  2013 role-not-identity; Chen/Norman 2021 role and filler must be kept separate), NOT the coreference channel. 🔌 **NO
  hdlab landed; QUEUED proven-ready for the consolidation:** a GRADED activation-weighted softmax pronoun-write into the
  entity register (temp swept ~2.0; NOT hard argmax; NOT a predictive prior; keep salience-based binding). The sparse store
  is a BUILD proposal (consolidation/store-design target), not a landed fix. **This closes the ENTITY LINE** (BIND +
  PREDICT + compose): p2 of the 3 in-flight consolidation-gating problems, now integrated.

- **2026-08-27 — ENTITY BINDING (who a pronoun refers to) is GRAMMATICAL-PROMINENCE SALIENCE, not recency and not
  semantics — validated on hard same-gender ambiguous pronouns** (from `entity_binding_needs_a_modern_pronoun_corpus`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness `test_gap_pronoun_binding.py` 6/6 PASS, re-verified first-hand).
  Completes the BIND half of entity tracking (the PREDICT half was the entity-structured situation model). On GAP
  (n=1773 human-labeled same-gender ambiguous pronouns) a grammatical-prominence salience binder resolves at **0.699,
  beating string-identity 0.508 (+0.191), most-recent-mention/RECENCY 0.514 (+0.184), and the shuffled-salience twin
  0.490 (+0.181), all CI-separated**. **STRIKING REFINEMENT:** on the HARD ambiguous cases **RECENCY IS AT CHANCE** — the
  load-bearing cue is GRAMMATICAL PROMINENCE (Centering's subject-preference Cf-ranking), NOT recency (which only
  correlated with prominence on the easy QA-SRL cases). Binding is STRUCTURAL/salience, NOT semantic (the
  implicit-causality semantic cue does not replicate + loses to its scramble — consistent with the entity-tracking
  dissociation: predict-via-content, bind-via-salience). Acquired 3 foundation corpora (GAP, Ferstl IC norms, LitBank).
  The unifying mechanism = **ACT-R base-level activation** `B = ln Σ w_role·dt^−d` (prominence + recency + frequency in
  one scalar; beats the live `salience()` +0.213 on running narrative). 🔌 **hdlab landing EARNED, QUEUED proven-ready:**
  a drop-in ACT-R base-level activation for the pronoun-branch `salience()`; no settling for the pick. **Successor:** wire
  entity tracking (bind + predict + coref threads) end-to-end on running narrative (LitBank) and measure the downstream
  marginal value of correct pronoun linking.

- **2026-08-27 — THE BATCH DEPENDENCY PARSER IS REPLACEABLE: an INCREMENTAL left-corner builder beats it at finding a
  verb's arguments (the structural half of "feed-forward where the brain is predictive"); + a substrate-wide
  DISCRETE→GRADED deviation surfaced** (from `the_argument_parser_is_batch_where_the_brain_is_incremental`, integrated
  SOLVED/EXCELLENT, owner-DONE; witness `verify_incremental_argstruct_builder.py` PASS, re-verified first-hand). A
  brain-faithful INCREMENTAL LEFT-CORNER argument-structure builder (left-to-right, eager verb-slot projection, bounded
  Now-or-Never buffer, NO arc graph) beats the BATCH UD parser (`candidate_generator`/`arc_parser`) at candidate-argument
  identification on modern QA-SRL (n=28,149): **F1 0.6201 vs 0.5849 (+0.0352 CI-sep) via a precision gain +0.0998** — the
  batch parser OVER-GENERATES +1.03 args/predicate. Genuinely incremental (prefix-consistency 0.985 vs 0.941; glass-box,
  no dependency-heads). Beats the crude positional floor +0.0264 at higher precision; info-free twin loses −0.177.
  **HONEST attribution:** the F1 win is the EAGER BOUNDED "good-enough" attachment (Now-or-Never; Ferreira/Frazier), NOT
  prediction (ablates +0.0007 NS) or revision (ablates −0.0101 on edited prose) — BUT revision IS brain-faithful
  (garden-path positive control: re-attaches +0.0852 CI-sep, ZERO false-fire), so revision is default-OFF "don't
  reanalyse unless forced." Downstream: the batch parse does NOT earn its place for word-order role assignment (even
  all-nominals matches it), but structure helps on the non-canonical PASSIVE slice (+0.0344). **Effect on the audit:**
  **(Tier 1, arc_parser)** — as a CANDIDATE GENERATOR feeding role assignment on modern prose, the batch arc parse is
  MEASURABLY REPLACEABLE; the structural front-end is an INCREMENTAL/PREDICTIVE build target. **(Tier 3, role
  assignment)** — Beber 2025 (VLSM+TMS+fMRI) double dissociation: structure-BUILDING (frontal/pMTG) and role-BINDING
  (posterior-temporal/angular) are SEPARATE ORGANS — keep the candidate/structure builder and the role assigner separate,
  never fuse. **The "feed-forward where the brain is predictive" gap now has its STRUCTURAL instance closed** — the
  incremental builder + the predictive reader are the two levels (structure + semantics) of one predictive front-end,
  relcl the specialised tail. **NEW substrate-wide deviation — DISCRETE where the brain is GRADED:** this builder + the
  role assigner make hard discrete decisions where human parsing is graded probabilistic competition — the *noise→0
  limit of graded cue-based retrieval* (Lewis & Vasishth 2005), the SAME mechanism as reversible role binding and the
  retrieval convergence (§1). **Honestly bounded (decompose-the-wall):** on canonical English the graded win is small
  (oracle ceiling +0.028, weak fit signal AUC 0.59) — a task ceiling + a p1 signal-quality symptom, NOT a clean lever —
  so the graded attack belongs on NON-CANONICAL/ambiguous populations → packaged as a substrate-wide successor problem.
  🔌 **hdlab landing EARNED, QUEUED proven-ready:** the incremental builder as a new organ behind a flag as the candidate
  source (role assigner unchanged; prediction ON, revision OFF; route to relcl) — measure live.

- **2026-08-27 — CONTEXT OVERRIDES THE FREQUENCY PRIOR ON MODERN DATA (the McGuffey data-limit confirmed), and the
  MISSING ORGAN is SEMANTIC CONTROL (LIFG/pMTG) — a gold-blind conflict trigger + graded suppression of the dominant
  sense** (from `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark`, integrated SOLVED/EXCELLENT,
  owner-DONE; witness `test_context_override_frequency.py` PASS, re-verified first-hand). **VINDICATES the SemCor
  acquisition (owner-directed):** the meaning_win result's "no context channel beats the frequency prior" was a
  ~200-year-old-corpus DATA limit, now confirmed — on held-out SUBORDINATE-congruent SemCor items (gold sense strictly
  less frequent; MFS=0 by construction) a structured context-likelihood read (held-out sense prototypes over BAG + local
  positional collocations) **recovers the rarer sense at 0.39–0.46 vs MFS 0.0000, beating UNIFORM chance (0.17–0.25) and
  both info-free twins CI-separated, SURVIVING leave-one-DOCUMENT-out** (real understanding, not topic memorization).
  **THE MISSING ORGAN, BUILT — SEMANTIC CONTROL:** the reader had the look-up but not the LIFG/pMTG CONTROL that
  SUPPRESSES the habitual sense when context disagrees. A GOLD-BLIND two-sided conflict trigger (coherence of the best
  non-dominant sense minus the dominant) predicts "the prior is wrong" at **AUC 0.79–0.81 (shuffled-context twin 0.58)**;
  conflict-gated GRADED suppression of the dominant sense is NET-POSITIVE CI-separated and lifts the frequency-OVERRIDE
  cases **+0.007–0.033** (gain attributable to the real trigger — the shuffled-trigger twin loses). **RETIRED FOUR levers
  with strong controls (all honestly reported):** grounded read-out for selection (refuted); SETTLING (formally IDENTICAL
  to the argmax read — McClelland 2013 — a tautology, not a finding); DIAGNOSTICITY word-weighting (null); FUSION of the
  associative + conceptual channels (HARD-FAILED → the CSC-faithful design is demand ROUTING, not fusion); compositional
  role-binding (HARD-FAILED → sense is resolved by topical/collocational context the bag captures). **HONEST:** all on the
  SemCor instrument (naturalistic-context ceiling ~0.39); the net semantic-control gain is modest (63% dominant,
  trigger-quality-limited) — quote the TRIGGER (AUC 0.79 gold-blind) + the override-case gain, not the aggregate.
  **Effect on the audit (§6 semantic control THIN; §7 meaning re-frame):** semantic control is no longer only "THIN" — a
  brain-faithful conflict-trigger + suppression organ is BUILT + validated (the LIFG/pMTG gate the two-systems integration
  flagged as needed); the meaning re-frame's context-override cell is now POSITIVE on modern data. 🔌 **hdlab landing
  EARNED, QUEUED proven-ready:** a default-off per-sense reordered-access read (frequency prior + structured-context
  log-likelihood) + the semantic-control conflict-trigger + graded-suppression organ; do NOT wire settling /
  grounding-for-selection / diagnosticity — a live-wiring composition, measure before any capability claim. **THE #0
  HIGHEST-PRIORITY NEXT STEP (owner-driven, packaged as the successor):** the reader is at CHANCE on human-graded
  meaning-IDENTITY (WiC) because it only has the ASSOCIATIVE (co-occurrence) system — add the ATL CONCEPTUAL/DEFINITIONAL
  meaning hub (WordNet/dictionary gloss + relational closure, a glass-box static asset) as a SECOND, DEMAND-ROUTED channel
  (conceptual for meaning-identity, associative for fine online selection); do NOT FUSE (fusion hard-failed).

- **2026-08-27 — THE SITUATION MODEL SHOULD BE ENTITY-STRUCTURED (AUGMENT the gist, don't replace it) — and entity
  tracking is TWO computations: PREDICT-via-content, BIND-via-salience** (from `the_situation_model_tracks_words_not_entities`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness `verify_entity_structured_situation_model.py` PASS, re-verified
  first-hand). On modern QA-SRL reconstructed documents, predicting a recurring entity's next argument, an
  entity-structured model (the bag-of-words discourse gist PLUS the active entity's ROLE-CONDITIONED accumulated state,
  retrieved by identity via the situation-register decode) beats the bag-of-words gist alone **CI-separated (+0.0545,
  REPLICATED on an independent split +0.0402)**. **Controls:** the info-free twin (a random other entity's history)
  ACTIVELY HURTS (−0.06) → the win requires the CORRECT entity; role-CONDITIONED beats role-BLIND (+0.0217 CI-sep) → the
  register's role STRUCTURE earns its place; **naive REPLACEMENT of the gist LOSES (−0.0355) → AUGMENT, not replace (the
  brain keeps both a global gist AND entity nodes)**; glass-box (ridge over grounded features + entity identity).
  **UNIFIES with the retrieval convergence (§1) a 4th time:** swapping the ridge for cue-based content-addressable
  retrieval (Lewis-Vasishth) makes the entity win LARGER (+0.072–0.085). **SHARP DISSOCIATION (a real architectural
  finding):** the two halves of entity tracking are DIFFERENT computations — **PREDICTING what an entity does next uses
  the richer MEANING-MEMORY (content-addressable retrieval); resolving WHO a mention refers to (binding) is dominated by
  simple SALIENCE/RECENCY (Centering; recency 0.493 ≫ content 0.308, and content does not augment binding)**. So keep
  content retrieval for the PREDICTION channel and the salience/Centering coref resolver for the pronoun pick (the
  cue-based-activation coref pick HARD_FAILED, −0.1348). **HONEST:** small effect (coarse 12-dim grounded space + ~2
  items/entity — the standing representation-quality coupling). **Effect on the audit:** the discourse/situation-model
  entry gains a validated entity structure (AUGMENT); coreference splits into a salience-BINDING channel + a
  content-PREDICTION channel. 🔌 **hdlab landing EARNED, QUEUED proven-ready:** augment the forward predictor's top-down
  context with the active entity's role-conditioned state (default-off; do NOT replace the gist; bind by salience, not
  content) — a live-wiring composition, measure before any capability claim. **Successor:** the entity-BINDING half on a
  MODERN pronoun corpus (does the coref organ / salience add over string-identity? QA-SRL cannot test pronoun resolution).

- **2026-08-27 — THE FRONT-END WALL IS RECOVERED (0.48→0.75, CI-separated) — and the lever is WORD ORDER + quote
  exclusion + a learnable speech-verb class, NOT thematic-fit or animacy (both refuted); PARTIAL (majority-floor-bound on
  an agent-saturated gold)** (from `the_live_front_end_mislabels_who_did_what_to_whom`, integrated PARTIAL/EXCELLENT,
  owner-DONE; witness `test_frontend_role_who_did_what.py` 6/6 PASS, re-verified first-hand). Executes the wire-and-measure's
  Branch B AND delivers the fix. On the live McGuffey entity-role task the fair brain-faithful assigner (core-mention
  selection + QUOTE EXCLUSION + a speech-verb/quotative class + the organ's graded perceptron over SELECTED mentions) =
  **0.747 [0.680,0.809], beating the live positional baseline 0.483 CI-separated** (role-balanced macro 0.191 > majority
  0.125). **REFUTES two premises on disk:** (1) naively wiring the learned organ is WORSE (0.385 — it over-generates 9.96
  candidates/clause and labels quoted-span nominals + `said Fred` speakers as PATIENT); (2) fixing animacy-dominance via
  thematic-fit does NOT help — **WORD ORDER dominates English role assignment** (learned order+voice = 0.918 on QA-SRL
  two-animate where animacy is exactly chance 0.500; MacWhinney/Bates/Kliegl 1984 cue-validity, PINNED). Deepening (4
  lit-VET'd passes, self-corrected): **thematic-fit is a REAL but LOW-VALIDITY backup cue** (pure/order-removed 0.585
  CI-sep above chance + its shuffled twin, correctly dominated by order — Dowty 1991 indeterminacy prediction; additive-fit
  HURTS, the Cai/Zhao/Pickering 2022 human analog) → **TESTED: not a role-labeling lever for English** (keep it for the
  predictive reader's anticipation job). The **speech-verb cue is genuinely SEMANTIC + brain-faithfully LEARNABLE from
  quote co-occurrence** (verba dicendi; beats a proper 40-draw NULL DISTRIBUTION on the role-balanced metric — a single
  random draw is NOT a valid twin, a caught overclaim). **Normalized-recurrence dynamics (Spivey-Knowlton 1996) is a more
  brain-faithful cue-integrator than the perceptron at EQUAL accuracy** (its settling-time difficulty signal unproven on
  this word-order-dominant corpus — needs human RT / a cue-conflict gold). **VERDICT PARTIAL:** ties (does not clear) the
  agent-saturated 78% majority floor on McGuffey plain accuracy — the rigorous-negative branch; the clean floor-clearing
  win is on the role-balanced metric + modern QA-SRL (0.93 vs 0.50), pending a role-balanced reading gold. **CONVERGED for
  natural-corpus role labeling** (the brain's mechanism is identified + replicated + tested; further gains need DATA, not
  mechanisms). **Effect on the audit (thematic-role entry, Tier 1):** the `thematic_role_labeler` "animacy-dominance
  HARD_FAIL" is partly a MEASUREMENT ARTIFACT (a fixed positional strawman at 0.48; a learned order+voice model does 0.93)
  — its real deviation is a TRAINING-DISTRIBUTION confound (McGuffey-canonical confounds animacy with role). Word order
  (+verb-class/quotative) is the PINNED dominant English cue. 🔌 **hdlab landing EARNED, QUEUED proven-ready:** wire the
  specific improved assigner into `situation_reader`/`thematic_role_labeler` DEFAULT-OFF (quote exclusion in
  `_pick_role_mentions` + a WordNet-`verb.communication`/distributionally-learned speech-verb graded cue + the perceptron
  over selected core mentions; NO thematic-fit) — beats the live baseline CI-sep, a multi-part live wiring = a focused
  deliberate landing. **PROXIMITY-AUDIT: the biggest remaining front-end fidelity gap is the batch UD dependency parser
  (`candidate_generator.py`) vs the brain's INCREMENTAL/PREDICTIVE structure-building** — the "feed-forward where the brain
  is predictive" gap one level down (structure, not semantics), composing with the predictive reader + relcl filler-gap →
  packaged as the successor problem.

- **2026-08-26 — 🧭 THE DECISIVE WIRE-AND-MEASURE: the composed organs FAIL end-to-end through the LIVE front-end but
  WORK on clean inputs → the FRONT-END (event/role extraction) is the binding constraint, not the memory organs; FHRR is
  CONFIRMED faithful; the fix is an EXISTING islanded learned organ** (from
  `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end`, integrated PARTIAL/EXCELLENT, owner-DONE;
  witness `test_wire_organs_endtoend.py` 9/9 PASS, re-verified first-hand). **This is the result that PICKS THE NEXT
  STAGE — Branch B fired (`NEXT_STAGE_after_wire_and_measure.md`).** Three validated organs (content-addressable additive
  retrieval, the distinctive-feature meaning read-out, a top-down coherence merge) composed into a real McGuffey
  entity-role reading task (57 passages, 178 gold queries), organs OFF vs ON, identical inputs. **VERDICT — a rigorous,
  well-attributed NEGATIVE = a full PASS:** end-to-end through the LIVE front-end the composed reader answers at 0.483
  [0.410,0.556] — BELOW the trivial majority-role floor 0.781; but on CLEAN/oracle inputs the SAME pipeline recovers the
  right event (hit@1 1.000) and role (0.983), beating the majority floor AND the exact-key live baseline (recency 0.730)
  CI-separated, info-free twin losing. **The oracle-vs-live contrast LOCALISES the wall to the front-end — the organs are
  not broken.** Error taxonomy (the cheap decisive control, done FIRST): MISASSIGNMENT-dominant (role-label 86 > entity
  50 > miss 30; 104 gold roles OUT-OF-SCOPE for an agent/patient front-end). **Stage 4 PROVED the lever:** a brain-faithful
  verb-argument role assigner (verb-class + quotative inversion + animacy) lifts front-end in-scope 0.36→0.82 and
  end-to-end 0.483→0.736 CI-separated (biggest single error class = quotative/dialogue POSTVERBAL speaker); it ties (not
  clears) the 0.908 in-scope majority floor, residual = the out-of-scope roles + two-animate who-did-what (needs verb
  selectional preference). **TWO caught+RETRACTED overreaches** (Stage 5 "organs add nothing" — a surface-cue no-headroom
  artifact; first Stage 6 "meaning supply fails" — three confounds), resolved by **Stage 7's clean instrument: content-
  addressable MEANING retrieval DOES recover lexically-disjoint paraphrase cues (0.528 [0.434,0.623] CI-separated over the
  collapsed count 0.217 and the twin 0.179) — REAL but PARTIAL** (0.528 << the exact-word ceiling 0.783). So the organs
  add value on the task they are FOR (recognise-not-recite), which the surface task could not show. **COMPOSITION FIDELITY
  (overturns the brief's §3):** the brain-faithful reading composition is a **late algebraic MERGE of forward-computed
  streams (Norris/McQueen/Cutler 2000 "Merge") + bounded revision — NOT a feedforward cascade, NOT recurrence.** **🔒
  FHRR CONFIRMED FAITHFUL — do NOT replace (converges with the owner-lock):** SEM (Franklin, Norman, Ranganath, Zacks &
  Gershman 2020, Psych Review — a peer-reviewed brain event-memory model) binds role→filler with **HRR circular
  convolution + bundling and a hippocampus/cortex CLS split = our exact machinery**; binding-by-synchrony is partly
  disconfirmed; VSA is the best-specified computational-level theory with a neural existence proof (Eliasmith SPA/Spaun).
  → **the audit's "central binding op UNPINNED → our-invention" framing is CORRECTED to "unpinned at the neural-
  IMPLEMENTATION level; a defensible PUBLISHED model (SEM)"** (see §5 #1). The real FHRR-compatible fidelity gaps
  (flagged, do NOT chase as a comprehension fix — they do not move this front-end-bound number): a sparse/indexed +
  boundary-gated STORE of FHRR codes (wire the shelved dg_ca3 gate + N400 segmentation — the same sparse-code lever as
  consolidation) and a role-labeled CASE-FRAME content unit (McRae role×filler asymmetry disproves bag-of-words). **F5
  N400 fidelity gap:** the monitor segments on a running-mean CONTENT gist with NO schema/goal term, but boundary
  PLACEMENT is top-down-laden (Zacks 2007) — seed an "expected content" prior before wiring segmentation live. **🔌 NO
  hdlab landed (the decision-shaping negative): do NOT wire the swamped downstream organs as a comprehension lift.**
  **🧠 WIRE-DON'T-ISLAND FINDING: the learned front-end organ ALREADY EXISTS + is ISLANDED** —
  `hdlab/thematic_role_labeler.py` (a LEARNED averaged-perceptron Competition-Model role labeler, roles incl.
  AGENT/PATIENT/EXPERIENCER/RECIPIENT/GOAL — addressing the 104 out-of-scope, 228 verb frames, real animacy lexicon,
  registered `..._islanded_2026-08-10`, ZERO live wirings). The Stage-4 hand-cascade re-derived a worse subset. **So the
  re-pointed FRONT-END fix is to WIRE + MEASURE this existing organ (its own revalidation HARD_FAILED on modern prose as
  animacy-dominant — a genuine wire-and-measure, not a slam-dunk), + `hdlab/learner/` for selectional preference,
  composing the integrated predictive-reader verb-preference + the relcl filler-gap resolver** — packaged as the new
  top-priority problem.

- **2026-08-26 — THE READER'S MISSING FORWARD-PREDICTION LOOP is BUILT: the verb pre-activates its argument's GROUNDED
  features and the resulting −log P surprisal is a real graded difficulty signal — closing the #1 architecture-fidelity
  gap (feed-forward → predictive)** (from `the_reader_is_feed_forward_where_the_brain_is_predictive`, integrated
  SOLVED/EXCELLENT, owner-DONE; witness `verify_predictive_reader.py` 8/8 PASS, re-verified first-hand). The relcl drill's
  top gap ("FEED-FORWARD where the brain is PREDICTIVE") is now a built, validated mechanism. **BOTH bar routes met on
  held-out REAL QA-SRL** (modern text — the McGuffey age confound does not apply): a role-specific grounded-feature
  forward predictor (verb → the expected argument's ATL-spoke features; the literature-standard thematic-fit prototype,
  Altmann-Kamide/McRae) read out as −log P softmax surprisal **beats an identical REACTIVE reader by +0.199 and an
  info-free WRONG-VERB twin by +0.095** (pseudo-disambiguation 0.589 vs the twin 0.514 AT CHANCE; only the verb-conditioned
  arm clears top-1 chance), AND its surprisal is a **valid graded difficulty signal** (Spearman 0.239 vs an independent
  distributional thematic-fit measure, twin ~0; reversibility AUC 0.619). **THE FREQUENCY CONFOUND (the field's central
  trap) is decisively excluded:** frequency-matched distractors + TRAIN-ONLY base rates + a WRONG-VERB twin with IDENTICAL
  frequency structure sitting at chance. Glass-box (grounded features + a verb KEY only — no word-form, no external model).
  **PINNED build choices (5 literature drills):** predict MEANING FEATURES not word-FORM (Nieuwland 2018 — our coarse
  12-dim grounded space is aligned with the ROBUST level); agent+verb JOINTLY constrain the patient (Bicknell — built,
  +0.037); **PRECISION-WEIGHTING built** (Friston constraint strength — HIGH-precision verbs +0.157 vs LOW +0.046, CI-sep;
  the precision term `predictive_coding.py` was missing); **HIERARCHICAL top-down prediction built** — within-clause
  (L0→L1 verb→L2 +agent→L3 +EVENT, monotone CI-sep) AND the full **CROSS-SENTENCE DISCOURSE hierarchy** that runs the
  ACTUAL `n400_coherence_monitor` across reconstructed real documents to top-down condition the word predictor (discourse
  beats local +0.088; the random-document twin HURTS) — the real fronto-temporal generative hierarchy, composing two
  organs we already have. **HONEST:** the effect is CI-separated but MODEST, ceiling'd by the 12-dim grounded space (the
  representation-quality coupling with p1 — the MACHINERY is correct now; the PAYOFF scales with representation). **THE
  UNIFICATION:** one forward predictor produces BOTH an anticipation win on IRREVERSIBLE role assignment AND a
  "hand-to-syntax" difficulty flag on REVERSIBLE cases (its margin collapses to ~0 there) — the exact regime the relcl
  filler-gap parser exists for. Semantics predicts what it can; its surprisal flags what only syntax resolves; the same
  surprisal feeds write-gating + the N400 confidence. **LOCUS-faithful:** verb-argument thematic prediction localises to
  ATL (entity features) + angular gyrus (verb+noun combination), distinct from IFG (structure) — so predicting in our
  grounded (ATL-spoke) space matches the region, not just the behaviour. **🔌 NO hdlab landed this integration, but a
  landing is EARNED and QUEUED (proven-ready deliberate):** BUILD the forward-prediction organ — a verb×role →
  grounded-centroid selectional-preference table (offline-built from a predicate-argument corpus; a static asset,
  admissible per the pivot) + a −log P softmax surprisal readout + a per-verb PRECISION scalar; reuses
  `grounded_similarity.grounded_vector`; DEFAULT-OFF; wire surprisal ONCE as shared difficulty infrastructure (relcl
  route-conflict / write-gating / N400 confidence); condition on agent+verb (Bicknell); do NOT predict word-forms or route
  through `predictive_coding.predict`'s sign()-quantised residual. A focused build (the offline table), not a
  heartbeat-cram — measure on the live reader before any capability claim. **Tier-5 sharpened (see §4); the forward
  predictor + the N400 coherence monitor are TWO LEVELS of ONE predictive hierarchy, not competitors.**

- **2026-08-26 — REVERSIBLE-SENTENCE ROLE ASSIGNMENT SOLVED by a SPECIALISED filler-gap circuit (route AROUND the arc
  parser, which is HARMFUL not weak); and it UNIFIES with the p3 content-addressable retrieval — filler-gap role binding
  IS cue-based retrieval** (from `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment`, integrated SOLVED/EXCELLENT,
  owner-DONE; witness `verify_relcl_incremental_fillergap_parser.py` 8/8 PASS, re-verified first-hand). On sentences where
  word order underdetermines who-did-what-to-whom ("the doctor that the lawyer chased"), a brain-faithful INCREMENTAL
  filler-gap resolver (active-filler strategy over UPOS + closed-class relativizers, **NO dependency graph**) beats the
  precise-voice two-line floor **CI-separated on a POWERED BALANCED held-out reversible set** — INC 0.9533 [0.9473,0.9592]
  vs 0.4994 at n=4800, ties the ORACLE 0.9981. **The general arc parser is MEASURABLY HARMFUL** here (FILLERGAP_ARCPARSER
  0.198, BELOW the info-free twin 0.305): greedy first-order unlabelled decoding mis-attaches the embedded-verb→antecedent
  arc, so routing role assignment through it loses to guessing. **Non-degenerate + glass-box:** a PICK_FRONTED degeneracy
  control (0.487, capped ~0.50 by the balanced design) isolates gap-DIRECTION resolution (INC−PICK_FRONTED +0.466); the
  resolver's signature takes NO `heads` arg and is invariant to permuting the arc heads → the win is function-words+position,
  not laundered parser output. **Gate no-leak, net-POSITIVE:** the two-condition construction gate (attached relativizer +
  empty object slot) leaves canonical clauses untouched (INC==two-line) and is net-positive overall (the prior ungated arm
  was −0.107). **HONEST real-text bound:** on QA-SRL the gate fires on 0.75% of items and moves the aggregate by +0.001 —
  genuine reversibles are <1% of real text, so the value is CORRECTNESS on rare hard sentences a situation model needs,
  NOT a headline metric. **THE DEEP FIDELITY RESULT (two literature drills):** the discrete resolver is the **noise→0
  COMPETENCE LIMIT of GRADED ADDITIVE CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL** (Lewis & Vasishth 2005; McElree 2000; the
  active-filler strategy EMERGES from it, Dotlacil 2021) — the SAME additive operation as the p3 store. Built + measured,
  it reproduces what the discrete rule structurally cannot: similarity-based interference (dissimilar 0.957 vs same-type
  0.857, +0.10 CI-sep) over the substrate's REAL grounded vectors (interference tracks real similarity: near 0.645 < far
  0.766), the reversibility contrast, and the subject<object asymmetry from dependency-locality decay (Gibson DLT). The
  center-embedding outer-gap collapse (0.048, oracle 1.000) matches human breakdown and is the RETRIEVAL half — its fix is
  the p3 mechanism, not a parser upgrade. **So filler-gap role binding UNIFIES with E1/E2/E3 under one cue-based
  content-addressable retrieval primitive** — reused at the sentence gap and the episodic store. **Framing caveat
  (honestly flagged):** this is a Marr-level computational HOMOLOGY, NOT a neural identity — single-sentence syntax is
  intact in amnesia (Ullman DP model; Kurczek & Duff 2020), so the "parser-retrieval = hippocampal CA3" link is
  under-test. **NEURAL-LOCALISATION CORRECTION for the audit:** reversible role binding localises to POSTERIOR-TEMPORAL /
  pMTG / inferior-parietal (Beber et al. 2025 lesion dissociation; Matchin & Hickok 2020), NOT a BA44 "syntactic movement"
  operator (Grodzinsky & Santi 2008 is now minority; BA44 supports WM/sequencing). **ARCHITECTURE-FIDELITY findings (a
  second drill, whole-pipeline):** the modules are largely fine but the WIRING copies an engineering NLP stack — (1)
  FEED-FORWARD where the brain is PREDICTIVE (verbs pre-activate fillers; N400 = prediction error; the biggest gap,
  architecture-wide) → packaged as a NEW problem; (2) STAGED tag→parse→interpret where the brain is INTERACTIVE/parallel
  and "good-enough" → noted; (3) an if/else route-gate where the brain runs PARALLEL COMPETING STREAMS whose DISAGREEMENT
  is the error signal (semantic P600) — the route-CONFLICT is a validated gold-free difficulty readout (heuristic error
  1.000 when routes conflict vs 0.093 when they agree). **🔌 NO new hdlab organ this integration:** the specialised
  resolver + the route-conflict UPGRADE (two always-on competing scorers + a conflict term, NOT if/else) fold into the p1
  retrieval-first wire-and-measure (the front-end the retrieval composition sits on), gated on a live number — consistent
  with the p2 treatment; the resolver's value is only measurable end-to-end (aggregate +0.001).

- **2026-08-26 — SIMILAR-MEMORY INTERFERENCE (the fan effect) RESOLVED IN PRINCIPLE: the missing organ is CONTEXT
  REINSTATEMENT at retrieval — the SAME additive rule, given one context feature** (from
  `resolve_retrieval_interference_among_similar_memories`, integrated SOLVED/EXCELLENT, owner-DONE; witness
  `test_context_interference_resolution.py` 6 assertions PASS, re-verified first-hand). Closes the open loop the
  content_addressable integration explicitly handed over ("the fan effect… open it as its own problem"). On a
  same-content-cluster interference instrument built on the REAL organ (`AdditiveCueRetrieval`; each memory = per-feature
  FHRR codes {entity,event,role} + a TCM Howard-Kahana drifting CONTEXT code + payload; a CLUSTER shares entity/event/role
  and differs only in encoding context): adding the encoding context to the additive Lewis-Vasishth activation
  (CTX_ADD = content + w_ctx·context) resolves interference **CI-separated at every fan level** — K=8 (9 near-identical
  competitors) CTX_ADD hit@1 **0.928 [0.880,0.957] vs the context-free additive baseline 0.400 [0.331,0.473]**, paired
  Δ +0.528 CI[+0.450,+0.606]; the baseline is bit-identical to the live `AdditiveCueRetrieval` argmax (0 mismatches).
  **Genuinely LEAK-SAFE cue combination:** info-free twins (shuffled / random context) LOSE CI-separated; context ALONE
  is 0.306 ≪ the exact-context oracle 0.994 and ≤ content-only — neither weak cue resolves it alone, their SUM does
  (Bayesian cue integration). **Residual fan effect EXHIBITED** (CTX_ADD 0.972→0.928 as K 1→8; content-only steeper
  0.722→0.400; also in the latency/activation-margin dimension) — the ACT-R noisy competitive read makes the fan cost
  EMERGE, not a penalty. **Decisive NEGATIVE boundary:** competitors encoded ADJACENT in time (non-separable context)
  collapse CTX_ADD to 0.494 — context resolves interference ONLY when it is separable (names WHY interference can be
  irreducible). Survives content-correlated (CMR) context (0.95→0.77) and partial-fragment reinstatement (30% ctx →
  0.917). **Self-caught soft-oracle:** a diagnosticity-weighted arm beat the exact-context oracle (impossible unless
  peeking) → demoted to a labelled ceiling; headline is fixed-weight CTX_ADD. **Effect on the audit (E2/E3):** the
  additive cue-retrieval rule is COMPLETE only WITH a context cue; context enters ADDITIVELY (one more Lewis-Vasishth
  feature), not as a multiplicative gate. **DG re-framed** — tested with the REAL `dg_separate` organ at encoding on the
  content code it is NEUTRAL (DG_CONTENT 0.367 ~ CONTENT_ONLY 0.372); the faithful hippocampal separator is
  context-INDEXING (Teyler-Rudy), NOT content-sparsification (extends the prior DG-at-retrieval negative). **The
  substrate's REAL `context_vector` is content-derived (bag-of-words, Kanerva/BEAGLE) and `sign()`-quantized** → the
  faithful wiring regime is the content-correlated one, and it should use the organ's GRADED context (`graded=True`), not
  the lossy sign() default (a fresh, concrete instance of deviation #4 at the context feature). 🔌 **NO new hdlab organ**
  — `AdditiveCueRetrieval` is already feature-agnostic, so context reinstatement is a USAGE (add a `context` feature to
  stored items + cue), not a new organ. The live wiring (store the situation-model/reading-loop GRADED context as a
  per-item feature) is a COMPOSITION folded into the p1 retrieval-first wire-and-measure, GATED on a live coref/
  situation-model number — SYNTHETIC construction proof; the load-bearing open question is whether the substrate's ACTUAL
  context is separable across genuinely similar memories (the boundary shows the mechanism collapses when it is not).

- **2026-08-26 — THE OFFLINE MEANING WIN DOES NOT TRANSFER TO CONTEXT-SELECTION: the wire-able half is the frequency
  PRIOR (unwired, the reader is sense-blind); NO context channel beats it; the frequency-defeating cell is DATA-limited**
  (from `the_meaning_win_is_offline_context_free_and_unwired`, integrated PARTIAL/EXCELLENT, owner-DONE; witness
  `test_meaning_win_context_transfer.py` PASS, re-verified first-hand — all four checks including the power-check).
  The just-integrated offline win (grounded feature-similarity beats the frequency floor on isolated pairs) was put
  into the CONTEXT-conditioned WSD instrument (v3 definitional, 288 words / 841 trials, leakage-controlled: eval
  sentences removed from the RI-fit corpus, symmetric answer-masking, held-out experience prototype) using the EXACT
  offline-winning rep (GNOC = concreteness-stripped 11-dim sensorimotor cosine). **REFUTED for context-SELECTION:**
  the frequency prior (MFS) 0.4637 beats uniform 0.3995 CI-sep [0.4303,0.4975] (the WORKING half, UNWIRED); NO context
  arm beats it — CTX_GNOC 0.4159, CTX_DIST 0.3976, CTX_FUSE 0.4431, CTXFREE_GNOC 0.3796, all below the prior. On the
  81 subordinate-congruent (frequency-defeating) items — the ONLY place context could add value — grounded is at
  chance (0.407 vs uniform 0.338, NOT separated) and **TIES its shuffled-grounding twin** (Δ −0.0043 CI [−0.063,+0.053]):
  the OPPOSITE of the offline base, where the twin LOST decisively (0.468 vs 0.741) — so there is no context-selection
  signal to destroy. **HONEST POWER-CORRECTION (the owner's "confirm it" prompt forced it):** the first pass claimed
  fusing grounding into the associative channel HURTS (FUSE−DIST −0.044 CI-sep, n=49 words); re-run AT POWER (n~154)
  it flips to +0.017 CI [−0.027,+0.063] and straddles zero → **the "grounding hurts / is the wrong system" claim is
  WITHDRAWN.** What survives: the two context channels are statistically INDISTINGUISHABLE and both sit below the
  prior (consistent with the two-systems LENS — grounded feature-similarity has no special advantage for a
  relatedness/associative SELECTION task — but with NO CI-separated evidence it is worse). **Un-testable cell, with a
  SPECIFIC reason:** context OVERRIDING frequency on subordinate senses cannot be tested here because subordinate
  senses are attested ONCE (prototype n=6; label subordinate n=81 at chance) — a DATA limit of the ~200-year-old
  McGuffey corpus, not a mechanism limit; the decisive re-test needs a MODERN balanced contextual WSD gold
  (SCWS/WiC/SemCor), NONE on disk. **Effect on the audit:** §7 "route it, and condition it on context" — the
  condition-on-context half is now TESTED and NEGATIVE (see §7); §6 semantic-control THIN is confirmed and its
  near-term substrate is the frequency prior, not a grounded context channel; the offline meaning-win row is marked
  CONTEXT-FREE + SIMILARITY-typed. **🔌 NO hdlab landing this integration.** The one well-supported gain (wire the MFS
  frequency prior as the reader's sense default) is a LIVE ARCHITECTURAL change, not a flag flip: the reader's
  ConceptSpace is sense-blind (one blended vector per lemma → floor (b) == MFS), so wiring a per-sense DEFAULT
  requires the reader to FIRST have per-sense representations. That belongs in the wire-and-measure lane, GATED on a
  live downstream comprehension measurement (measure-before-capability-claim), NOT pre-paid — packaged as a follow-on
  build. Do NOT wire any context-conditioning channel for selection (moves no number here); wire grounding where
  SIMILARITY matters (the whitening + fixed two-system fusion), its proven role. The subordinate-OVERRIDE capability
  is filed MODERN-BENCHMARK-CONTINGENT (an acquisition need, surfaced to the owner).

- **2026-08-26 — CONSOLIDATION (deviation #5) REFRAMED: the store not the schedule was the divergence — SPARSE coding
  is the primary anti-forgetting lever, selective replay works ONLY in the sparse regime, and the real gap is a
  retention↔generalisation TRADEOFF (content-bound)** (from `one_store_does_two_jobs_and_consolidation_is_a_single_average`,
  integrated PARTIAL/EXCELLENT, owner-DONE; witness `test_consolidation_real_reading.py` PASS, re-verified first-hand).
  On REAL simplewiki reading (era fixed): **(A)** dense/overlapping cortex — uniform interleaved replay prevents
  catastrophic forgetting CI-separated (SEQ 0.076 → 0.349) but SELECTIVE replay is a zero-sum WASH (no lever at any
  budget). **(B)** SPARSE k-WTA pattern-separated cortex (the brain-faithful architecture) — sparse coding SHARPLY
  reduces interference (an EQUAL-CAPACITY dense-hidden control collapses to 0.000 → **sparsity, not capacity, is
  causal**; French 1991), AND selective interleaved replay NOW BEATS the uniform twin CI-separated (keep=0.01 0.784 vs
  0.680; keep=0.02 0.979 vs 0.896). **So the brief's mechanism IS met, but ONLY in the sparse regime — the earlier
  dense-cortex "selection isn't a lever" negative was a modelling artifact.** **(C) retention↔generalisation TRADEOFF:**
  the sparse cortex RETAINS (0.68–1.0) but does NOT generalise (~0.05); overlapping generalises slightly but forgets →
  ONE store cannot do both (the two-store premise, measured). **(D) FORK B:** the LIVE store is separable-row
  (SEP_LOOKUP 1.0, never forgets) → **catastrophic forgetting is NOT the live binding constraint.** **(E) CONTENT WALL:**
  generalisation is at the first-order floor for EVERY arm → representation/content-bound. **Effect on the audit:** D4
  (sparse+graded) is now tested on REAL TEXT and is **load-bearing on the WRITE as well as the READ (p2)** — but
  COMPLEMENTARY to replay (CLS: sparse-encode + replay-extract-structure are different jobs; O'Reilly & McClelland 1994),
  NOT "sparse beats replay"; the SELECTION function is regime-dependent (zero-sum dense / a real lever sparse), correcting
  the flat negative; **deviation #5 is reframed** — "one store, single average" is not causing forgetting (live store is
  already hippocampal-separable); the gap is the retention↔generalisation tradeoff → two-store CLS + sparse coding, and
  generalisation itself is content-bound (routes to the meaning-supply line, converging with every recent result).
  ⚠️ Independent literature-fidelity scan CORRECTED two over-claims (sparse is complementary-not-superior to replay;
  DG neurogenesis is DOUBLE-EDGED — Akers/Frankland 2014 — so the idealised disjoint-units arm OVERSTATES retention).
  🔌 hdlab landing EARNED (ordered): PRIMARY make the consolidated cortical code SPARSE/k-WTA (default-off; the same
  deviation-#4 lever as the cortical-read p2); SECONDARY wire `continual.replay_cycle` as uniform interleaved replay
  (default-off, selective variant only in the sparse regime); KEEP the separable fast store. Coordinate with the p2
  cortical-read landing (both are the sparse-code lever). Synthetic-on-real-text construction proof — measure end-to-end.

- **2026-08-26 — CONTENT-ADDRESSABLE RETRIEVAL: bar MET, and it RE-FRAMES the fix — the missing organ is cue-based
  RETRIEVAL (additive Lewis-Vasishth), NOT "separate the store"** (from `content_addressable_retrieval_over_a_separated_store`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness `verify_content_addressable_register_retrieval.py` PASS, re-verified
  first-hand). Content-addressable retrieval over the SEPARATED register (match the partial cue against the stored slots,
  read the clean slot) beats the LIVE exact-key routes CI-separated under a partial cue: **SEP_CA 0.991 [0.988,0.993] vs
  the exact-key HASH route 0.287 and the naive flat register 0.068**; twins at chance (~0.05); at a FULL cue everything
  ties (the Nakazawa CA3 partial-cue dissociation, predicted not swept); generalises across D×load×rho. **BUT the drills
  RE-FRAME the fix, with multiple honest self-corrections:** (1) an **EQUAL-TOTAL-STORAGE flat store (`FLAT_MATCHED`)
  recovers to 1.000** — so separation is NOT uniquely necessary; the flat register's partial-cue failure is
  CAPACITY/crosstalk, curable by separation OR dimension. **The genuinely-missing, brain-foundational mechanism is
  content-addressable RETRIEVAL (the cue-MATCH), which the substrate lacks entirely; separation (DG / multibank) is its
  storage-EFFICIENT substrate, not the lever.** (2) The **CA3 iterative settle is NOT load-bearing** — 1-step argmax
  (SEP_ARGMAX 0.990) ties SEP_CA in every regime (the 1-step match is already the MAP estimate). (3) **DG pattern
  separation did NOT help** in any tested regime (worse at rho=0, neutral at rho=0.5) — a rigorous negative on the DG→CA3
  pairing the binding SOLVED flagged. (4) **LOAD-BEARING NEGATIVE reproduced on the register:** CA3 cleanup on the flat
  readback TIES argmax exactly (0.607=0.607) — you cannot clean your way out of superposition; the fix is architecture.
  **NEW DEVIATION (the deeper E2/E3 fidelity gap):** our register retrieves by a MULTIPLICATIVE composite key (`bind` the
  cue features, match one vector); FHRR bind orthogonalises the whole composite on any one wrong/missing feature, so a
  partial/competitor-dominated cue COLLAPSES. **The brain's PINNED cue-based retrieval (Lewis & Vasishth 2005; ACT-R;
  already pinned for E3 coref) is ADDITIVE:** activation = Σ_f w_f·sim(cue_f, item_f), retrieve the max — degrading
  GRACEFULLY (additive 0.33–0.70 vs composite 0.03–0.04 under a dropped/interfering feature). ⚠️ **Honestly DEFLATED by
  the owner-directed real-grounded drill:** with the substrate's OWN grounded feature vectors (real graded similarity) the
  additive-vs-composite gap is mostly a TIE (clean/near/dropped tie; additive only edges under a truly-dissimilar
  corruption, which real similarity makes rare) — so additive is the RIGHT DEFAULT (never worse, natively serves partial
  cues, no unphysical collapse) but the everyday lift is SMALL. **The REAL open problem is similarity-INTERFERENCE
  resolution (the fan effect) — and it should NOT be "solved": the fan effect / false memories are real human behaviour, a
  faithful model must EXHIBIT it. Open it as its own problem, not a switch here.** **[RESOLVED 2026-08-26 — see the
  newest §2b entry: the missing organ is CONTEXT REINSTATEMENT at retrieval (same additive rule + a context feature);
  it resolves interference CI-separated while still exhibiting the residual fan effect, and collapses when context is
  non-separable.]** **Effect on the audit:** E2 gains a
  RETRIEVAL deviation (missing content-addressable read path — both registers' `decode()` require the exact key); the
  E1/E2/E3 re-location is SHARPENED (the lever is content-addressable RETRIEVAL, separation is the substrate); the owned
  fix is HALF-owned (`ca3_completer` needs an FHRR [Re;Im] adapter + its settle is un-earned; `dg_pattern_separation`
  didn't help); the retrieval RULE should be ADDITIVE (Lewis-Vasishth), not a multiplicative composite. 🔌 hdlab landing
  EARNED (a default-off additive `decode_cue` over the separated multibank register + an FHRR adapter for `ca3_completer`)
  — queued as a focused default-off landing with its own witness; SYNTHETIC construction proof, measure on the LIVE
  reading/QA task before any capability claim.

- **2026-08-26 — THE TWO-SIMILARITY-SYSTEMS BUILD: the FEATURE-SIMILARITY system is BUILT + PROVEN; the
  SEMANTIC-CONTROL SWITCH is REFUTED (fixed fusion wins)** (from `the_substrate_has_one_meaning_system_where_the_brain_has_two`,
  integrated PARTIAL/EXCELLENT, owner-DONE; witness `test_two_meaning_systems_feature_similarity_and_gate.py` PASS,
  re-verified first-hand). The re-point's #1 lever, delivered. **BAR #1 MET — the missing feature-similarity system,
  built brain-faithfully:** the ATL's "privilege DISTINCTIVE features" = DECORRELATION (WHITEN away the dominant shared
  axis — concreteness, the top PC is 26.7% of the grounding variance — which is exactly the grounding carrier's own
  documented "raw cosine can't separate synonym from sibling; apple/orange 0.952" ceiling, stated as a bug). The
  distinctive-feature-weighted grounding rep beats RAW grounded cosine **CI-separated on two HELD-OUT similarity golds**
  (SimLex 0.291 vs 0.245, +0.046 CI_lo 0.019; SimVerb 0.287 vs 0.264, +0.023 CI_lo 0.008 — reproduced first-hand) and
  it LOWERS relatedness (the exact brain signature — specialises toward alike-in-kind); it beats the ASSOCIATIVE
  co-occurrence rep on similarity by +0.197/+0.233; info-free twin (shuffled grounding rows) loses (~0.014), floors
  cleared, whitening fit gold-blind + vocab-disjoint, hyperparams fit only on a dev split. **A REPRESENTATION-level op
  (suppress shared covariance), different-in-kind from the refuted sign/graded/sparse read-out family.** **FINER DRILL
  (a fidelity BOUNDARY, honestly found):** LINEAR whitening is SUFFICIENT — a per-concept NONLINEAR distinctiveness (the
  sharper McRae/semantic-dementia account) does NOT add on a 12-dim CONTINUOUS grounding space (Δ 0.000) and the
  zebra→horse signature does NOT reproduce, because that space lacks the rich binary "few-concepts-have-this-feature"
  structure the account assumes → the next distinctiveness gain is a RICHER FEATURE SUPPLY, not a fancier transform.
  **BAR #2 REFUTED (robustly; a brief-named valid outcome) — the two systems are better FUSED than SWITCHED:** a
  task-gate does not beat the best FIXED blend even with a STRONG associative system (gate−fixed −0.026 CI[−0.048,−0.006])
  or on a conflict population, and it ties its random-switch control on a mixed pool. The brain-grounded reason (NOT an
  exhausted-engineering wall): the IFG gate resolves COMPETITION using CONTEXT, and a decontextualised word pair gives
  it nothing to gate on — so for graded similarity/relatedness RATING the faithful op is FIXED multiplicative
  INTEGRATION (recovers BOTH axes, mean 0.378 > feature-pure 0.309 > associative-pure 0.338); the gate's proving ground
  is a genuine-selection task (homonym WSD), owned by `reader_meaning_channel` (which HARD_FAILED there) and deliberately
  not re-built here. **Effect on the audit:** (a) Tier-2 ATL/sensorimotor RIGHT-OP-WRONG-METRIC now has a fix + a number
  (whitening); (b) the "semantic control THIN" gap is RE-POINTED — the near-term win is the FIXED two-system fusion, the
  task-switch gate is a later SELECTION-task deliverable, NOT for graded rating; (c) the two-similarity-systems row (from
  the sign_quantiser drill) is CONFIRMED + BUILT. Converges with the session theme: the remaining wall is meaning SUPPLY
  (richer features), not the transform. 🔌 hdlab landing **LANDED 2026-08-26**: the distinctive-feature WHITENING read-out is in
  `hdlab/grounded_similarity.py` (`distinctive_grounded_vector` / `distinctive_grounded_similarity`, a NEW uncapped
  meaning read-out; the capped link score is byte-identical), witness `test_distinctive_feature_grounding_organ.py`
  PASS (distinctive rho 0.292 > raw 0.245 on SimLex through the organ's own transform; whitened covariance is exactly
  identity), registered `distinctive_feature_grounding_v1` (WIRE_CANDIDATE, ISLAND). Use it as the feature-similarity
  axis + a FIXED two-system fusion, NOT a switch; measure on the live read-out before any capability claim.

- **2026-08-26 — F5 (N400 COHERENCE MONITOR): the MISSING organ now has a validated build spec + a decisive
  existence proof; and DEVIATION #6 SPLITS** (from `the_substrate_does_not_learn_or_update_by_prediction_error`,
  integrated EXCELLENT, owner-DONE; witness `verify_prediction_error_event_segmentation.py` PASS, re-verified
  first-hand). The brain's UPDATE signal was MISSING, not impossible. A **GRADED forward CONTENT prediction error
  against the RUNNING (reset-per-event) situation-model state** — `e = 1 − cos(content, running_event_gist)`,
  boundary-posted via the existing EST `relative_threshold_gate` (Reynolds/Zacks/Braver 2007, already in
  `predictive_coding.py`) — segments a discourse near-perfectly and fills the situation model: downstream within-event
  cross-role recovery **0.988 [0.980,0.995]** vs FIXED 0.523 / RANDOM 0.438 / FORM_NOVELTY 0.737 (strongest floor) /
  PERMUTED_SURPRISE 0.487, boundary F1 0.987, WIN in all 9 D×coherence cells, at a MATCHED boundary rate (so the win
  is boundary POSITION, not rate). **Key dissociation — the p1 coupling made concrete:** the naive `||Δregister||` in
  the near-orthogonal BINDING space TIES no-segmentation (0.202 vs 0.198); the residual must be graded AND computed in
  a CONTENT-similar space, not the sign-quantised/near-orthogonal one. Escapes the two prior negatives' trap:
  FORM_NOVELTY (surprise vs a whole-stream anchor that NEVER resets) caps at 0.737 — the RUNNING RESET is what makes it
  the N400. Foundationality drill: the win does not hinge on the predictor (running-mean / last-item / online
  Rao-Ballard learned transition all win identically). **Effect on the audit:** (1) **F5 (§4 Tier 3) MISSING → spec'd +
  existence-proven.** (2) **E2's "missing the PE segmentation that decides WHEN to write" confirmed + actionable** —
  advance `situation_model_accumulate`'s event slot on an F5 boundary (0.20→0.99 in-instrument). (3) **DEVIATION #6
  SPLITS into two rows with OPPOSITE verdicts:** the UPDATE half (N400/SEM segmentation) is missing-buildable-and-WINS
  → BUILD; the LEARNING half ("cloze not forward-PC") is a RIGOROUS NEGATIVE (forward-PC does NOT beat cloze on
  paradigmatic meaning) → DEPRIORITISE. (4) **Tier 5 `predictive_coding.py` RIGHT-OP-WRONG-METRIC confirmed** + a
  companion positive: the residual is graded in salience (ρ 0.77) and the EST relative-threshold machinery there is
  correct but UNWIRED. ⚠️ Synthetic construction proof — the N400 organ (graded content-PE + EST boundary + wire to
  `situation_model_accumulate`) is **LANDED 2026-08-26 as `hdlab/n400_coherence_monitor.py`** — off-path
  WIRE_CANDIDATE, witness `test_n400_coherence_monitor_organ.py` PASS (running-reset F1 1.0 > never-reset anchor 0.44;
  a near-orthogonal binding-like code is unsegmentable F1 0.0 — the content-space finding; coherent stream quiet),
  reuses the pinned `predictive_coding.running_avg_update`, registered `n400_coherence_monitor_v1`. **Next:** wire a
  posted boundary → advance `situation_model_accumulate`'s event slot, and MEASURE on the live reader before any
  capability claim (the win is still a synthetic construction proof).

- **2026-08-26 — DEVIATION #2 (`sign()`) BINDING REGIME: CONFIRMED-but-LATENT, coupled to B4** (from
  `the_sign_quantiser_makes_the_substrate_an_averaging_machine`, **RE-INTEGRATED PROPERLY on the owner's per-problem
  owner-DONE**; the binding drill + live verification re-verified scaffold-free first-hand, both reproduce). This is the
  ADDITIVE binding half that makes the FINAL verdict **PARTIAL** — the read-out refutation (next entry) STANDS. In the
  binding/superposition regime sign() IS a real averaging machine for CORRELATED bound codes: recovering B role-filler
  pairs from a bundle (MAP-VSA, 512-filler cleanup, d=256), GRADED beats SIGN by a CI-separated, GROWING margin (B6
  0.98/0.73, B8 0.88/0.58, B12 0.67/0.36 — reproduced), raising the capacity cliff **B\*=8 → 12** for correlated codes
  (~50% capacity loss at d=256; correlation-specific — RANDOM gap +0.08 vs CORRELATED +0.146). **BUT LIVE VERIFICATION
  shows it does NOT bite today:** the real StructuralEncoder binds at mean B=2.85 (median 3; 14% B>4) with ATOMIC
  near-orthogonal fillers (|cos| 0.063) → recovery gap +0.013 (~0 for B≤4). It becomes real ONLY when binding is made
  brain-faithful (graded-semantic fillers, |cos| 0.248) → gap +0.044 overall, **+0.087 on the 14% B>4 tail** (verdict
  `SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL`, reproduced first-hand). **So deviation #2 at binding is a
  GUARDRAIL COUPLED to the graded-code (B4) fix — NOT a current bug, NOT a standalone win:** when B4 makes fillers
  graded-semantic, the `sign()`-on-a-bundle sites (`situation_focus.py`, `role_slot_summarizer.py`, `event_bundle.py`,
  CA3 `cleanup_family.py`) must go graded in the SAME change, gated on `exp_live_binding_load_signgap_v1` /
  `exp_superposition_capacity_binding_v1`. Connects to the binding/memory line (p3 content-addressable retrieval, p5
  one-store). **NO hdlab landing now** (latent; the solver's explicit guidance: do NOT land it standalone). §8 lever #1
  (`sign→graded`) is demoted only AS A READ-OUT lever; it is ALIVE as this binding-site guardrail.

- **2026-08-26 — DEVIATION #2 (`sign()` QUANTISER) REFUTED AS THE AVERAGING-MACHINE LEVER *ON THE READ-OUT*; the
  read-out wall is meaning SUPPLY, and there are TWO SIMILARITY SYSTEMS** (from
  `the_sign_quantiser_makes_the_substrate_an_averaging_machine` — the READ-OUT half of the PARTIAL verdict; the binding
  half is the entry ABOVE; headline re-verified scaffold-free PASS + the stale-premise correction confirmed on disk).
  **Three load-bearing corrections:** (1) **STALE PREMISE** — `GRADED_COMPARATOR`/`graded_query` have been **default-ON since 2026-08-14**
  (env `HD_GRADED_COMPARATOR` defaults "1"; confirmed in `reading_grounding_loop.py`). The comparator field+query are
  already graded; the only unconditional live `sign()` left is the banking query (`canonicalize()`), measured ~0 cost.
  The audit's "graded flags exist default-OFF" (§5.2) is WRONG. (2) **REFUTED** — on the REAL open-vocab hit@1 task,
  graded vs sign = `+0.0015` NULL, and the ENTIRE brain-faithful code-format family (graded / divisive-norm at read-out
  or composition / in-place sparse / DG expansive-sparse) **plus a faithful self-supervised CBOW learner** ALL land at
  the same distributional ceiling ~`0.05`, all CI-BELOW a generic-word averaging floor `0.171`. The read-out is
  strictly WORSE than naming the average thing — "averaging machine" is a signal-EXTRACTION failure, not a quantiser
  artifact. Only WordNet-**SUPERVISED** learning exceeds the floor (`0.108`); the brain gets no such labels from
  reading (CBOW-NS ≈ shifted-PMI factorisation, Levy & Goldberg 2014 — the self-supervised learner and the counting
  cosine are two compressions of one signal and land together). **So the loss is a meaning-SUPPLY gap (grounding /
  knowledge source), UPSTREAM of the `sign()` and every read-out mechanism.** (3) **NEW & first-class — TWO SIMILARITY
  SYSTEMS, measured on our own reps:** the distribution/co-occurrence channel carries **ASSOCIATIVE RELATEDNESS**
  (WordSim ρ `0.25`, twin loses) but ~0 **FEATURE SIMILARITY** (SimLex `0.04`); GROUNDING carries **both** (`0.42`/`0.21`).
  This is the ATL-feature-similarity vs LIFG/pMTG-associative dissociation, now quantified here. Consequences: (a)
  grading meaning against WordNet **TAXONOMIC** gold systematically UNDER-credits the associative channel we actually
  have — prefer human relatedness/similarity or a relation-controlled gold as the standing meaning metric; (b) the
  SIMILARITY axis is recovered by brain-faithful **STRUCTURE** (narrow ordered context: SimLex `0.075→0.112` as window
  0→±1) and by grounding, **not** by any read-out format; (c) the two systems need **SEMANTIC CONTROL** (IFG,
  task-gated multiplicative gain) — a fixed blend HELPS relatedness but HURTS similarity, so the currently-THIN
  semantic-control deviation now has a concrete measured need. **Effect on this audit:** DEVIATION #2 re-pointed from
  "quantiser/format lever" to "meaning-SUPPLY + two-systems + semantic-control"; §8 lever #1 (`sign→graded`) DEMOTED;
  §7 (meaning present-but-unwired) BOUNDED (distribution alone is insufficient on the taxonomic/similarity axis — it
  carries relatedness; supply/grounding + structure carry similarity). ⚠️ Corpus-age is NOT this instrument's confound
  (`load_corpus_v5` is MODERN — OneStopEnglish + OpenStax — the solver's disk-checked correction; the confound here is
  taxonomic-gold-vs-associative-representation, not archaism). Optional default-off micro-win NOT yet landed:
  divisive-normalisation `center_field` read-out option (direction-correct `+0.007` but within noise — an option, never
  a capability). **This is the concrete brain-foundational re-point: the foundation is not the code FORMAT — it is the
  two-similarity-systems architecture (grounding + structured context) + semantic-control gating + meaning supply.**

- **2026-08-26 — DEVIATION #3 (WRONG MEMORY) REFINED: the cortical READ is real and fixable, but the wall is
  the consolidated CONTENT/CODE, not the read** (from `the_consolidated_cortical_store_is_written_but_never_read`,
  integrated PARTIAL/EXCELLENT, owner-DONE; witness `test_cortical_store_read_path.py` PASS). Built the actual CLS
  read (consolidation by `continual.replay_cycle` → read by pattern completion) and ran the two controls no prior
  cortical problem had: the **live EPISODIC arm** ("wrong memory") and the **consolidation-ablation positive
  control**. Result, 6 held-out units: the brain-faithful cortical read **beats the episodic path ~7-10× on
  transfer, CI-separated over its info-free twin in-domain** (0.484 vs episodic 0.064 vs twin 0.158), and ablating
  consolidation collapses it to 0 while episodic is invariant (the 0.0000 becomes a real drop). **BUT** it does NOT
  clear the first-order counting floor (ties 0.474 in-domain) and on the **powered unseen-cooc regime it sits
  at/below its own twin at no k on any unit** → no cue-specific transfer on genuinely novel queries. **So the
  read-path defect is real and worth wiring, but the standing "memorises-not-transfers" wall is NOT dissolved by
  the read alone — the residual is the consolidated CONTENT/CODE.** Reframe the missing-organ verdict (dev #3):
  "missing cortical-read organ **AND** transfer-bearing consolidated content." Two deeper findings folded in:
  **(a) DEVIATION #4 (dense vs sparse+graded) is LOAD-BEARING ON THE READ** — a dense frequency-summed associator
  collapses to hubs (0.025); **k-WTA sparse coding + frequency-normalised inhibition rescues it to 0.156**, beating
  cosine. Couple B4 with the cortical-read work, not only the `sign()` line. **(b) NEW DEVIATION — recurrent
  ATTRACTOR completion (CA3-class) HURTS pool-RANKING**: settling re-promotes concept-code hubs (a hub jumps rank
  2→0, robust across temperature 1-64), so the faithful semantic *ranking* read is a **graded population read**, and
  the attractor is a *recognition* op, not a ranking op (`cleanup_family`'s modern-Hopfield variant terminates in
  `sign()` — another dev #2 site). **(c) DEVIATION #5 tested and closed:** the interleaved-online CLS process
  (`continual.py` replay actually building the code) is **more data-hungry than batch SVD** and shares its
  data-bound ceiling (SGNS ≈ SVD-of-shifted-PPMI; Levy & Goldberg 2014) — it fails the seen-cooc positive control at
  our ~2400-8000-sentence scale. So "make the code-learning more brain-faithful" is a FALSE lever when the constraint
  is the DATA the process needs; the honest deepening names the binding constraint (lifetime-scale experience). The
  hippocampus (which we have) is what the brain uses for zero-experience concepts; cortical transfer needs experience
  we lack. ⚠️ Proposed hdlab landing (the CLS matched pair — graded sparse+inhibited `space="overlap"` cortical read
  routed against episodic by the p2 recollection-confidence gate) is architecture validation, NOT a floor-beater;
  land default-off. **Re-points §8 lever #2 (cortical-read): validated-but-content-bound, not a stand-alone win.**

- **2026-08-26 — E1 (BINDING) RE-LOCATED: the OPERATOR is VALIDATED; the deviation is the flat-superposition
  RETRIEVAL** (from `the_core_binding_operator_may_not_be_brain_faithful`, integrated EXCELLENT). At EQUAL storage
  our compressed FHRR bind **beats the two WRITABLE brain theories** (tensor-product / TEM product; Rigotti-Fusi
  conjunctive) — TPR loses to FHRR in every exact-cue cell. **So E1's "UNSCORABLE, the deepest deviation, our
  central op has no brain equation" framing is mis-located: the operator is an EFFICIENT choice, validated, not a
  liability.** The REAL deviation is one level up (the superposition-and-unbind RETRIEVAL, shared with E2/E3): we
  superpose many bindings into one vector and un-mix on demand; the brain SEPARATES into slots and retrieves
  CONTENT-ADDRESSABLY, so a brain-faithful version (theta-gamma temporal separation) beats FHRR **CI-separated by
  ~5x under a PARTIAL cue at equal storage** (0.128 vs 0.025), info-free twins losing (predicted by the CA3
  partial-cue dissociation, Nakazawa 2002). **Load-bearing negative:** routing FHRR through the real CA3 attractor
  TIES argmax — you cannot clean your way out of superposition; the fix is the STORAGE architecture, not a terminal
  cleanup. **Sharpens E1:** the per-component normaliser only ever HURTS (L2/raw-sum beat it 32/32 on binding
  recovery, wins zero). **Confirms E2:** `situation_model_multibank` routes by deterministic hash (exact key only,
  no partial-cue path); the owned `ca3_completer` (default-off) is the content-addressable fix, realised only over
  the SEPARATED store. **UNIFIES E1/E2/E3** under one brain mechanism — cue-based content-addressable retrieval with
  similarity interference (Lewis & Vasishth 2005; McElree; Nakazawa 2002). ⚠️ Synthetic construction proof — the
  fix (owned `ca3_completer` + `dg_pattern_separation`, unwired) must be measured on the LIVE reading task before
  any capability claim.

- **2026-08-26 — GOALS/REWARD & METACOGNITION tiers fidelity-scored (strategy extension, closing the §6 scope gap).**
  **GOALS/REWARD:** only two organs are PINNABLE and both are already in the ORGAN_MAP — `action_selection` (BG
  Go/NoGo + TD) is **SAME op-class**, and `successor_representation` (D7) is a **FULLY-PINNED closed form** (faithful
  but MEASURED-AND-LOST). The goal-COMPREHENSION organs (`goal_typing`, `goal_outcome_relation(_grounded)`,
  `goal_achievement`, `outcome_event_extraction`, `parse_goal_extraction`) are **UNSCORABLE** — goal / means-end
  comprehension is a cognitive-level function with NO pinned neural equation, so they are OUR-INVENTIONS judged on
  task, not brain-fidelity (like the POS/parse organs F1/F2). Their live weakness (`organ_abstains`: refuses 2/3)
  is a **COVERAGE** gap — missing broad grounded meaning — NOT a fidelity flaw. `self_manager` (DA vigor / ACC-EVC
  halting) mirrors the neuromodulatory G3 deviation (global scalars, not per-dimension task-driven gain).
  **METACOGNITION (TIER 5):** `gap_detector` is **SAME** ("the healthiest organ"); the abstention family
  (`refuse_gate` / `conformal` / `clarify_gate`) has a real deviation — **no floor on refusal CORRECTNESS**, and
  `state.refusals` is written, counted, reloaded, then never consulted. **NET:** affect (p3) + goals + metacognition
  are now scored; the honest finding is that the higher cognitive tiers are largely **UNSCORABLE** (brain equation
  unpinned), so "brain-faithful" is undefined there and they are inventions judged on task — the fidelity levers
  concentrate in the reading→meaning→memory pipeline.

- **2026-08-26 — AFFECT / VALENCE TIER now has a fidelity verdict** (from `propagate_along_the_relation_that_carries_valence`,
  integrated EXCELLENT). This tier was flagged "built but never fidelity-scored" (§6 scope gap); it now has one.
  `wordnet_polarity_propagation.py`'s shipped **Stage B (taxonomic path-similarity vote) is UNFAITHFUL** — taxonomic
  distance carries NO valence (Spearman −0.0023, inside its null). **The faithful shape** is SIGNED propagation along
  the relations that transfer affect (antonym FLIPS, synonym/derivational/verb-group PRESERVE), plus an **explicit,
  irreducible opposition operator**: antonyms are similar in EVERY feature space (embodied 0.270 ≈ synonym 0.266) yet
  flip the human valence rating (−0.556), so no similarity metric can supply the flip — it must be an explicit
  relation `[P]`. **The one real deviation is the READOUT:** valence is a graded bipolar axis (Osgood; OFC), but the
  organ reports a discrete pole — the signed-vote magnitude already tracks the continuous rating at ρ 0.400, so the
  binary readout hides ~half the signal. Signed propagation reaches 0.726 on 485 words (vs shipped 0.660 on 326);
  universal across POS, sharpest on adjectives (0.8845). **LANDED 2026-08-26** in
  `hdlab/wordnet_polarity_propagation.py` as `dictionary_lookup(..., signed_propagation=True)` (DEFAULT-OFF,
  byte-identical when off, verified identical to the proven cell mechanism; witness
  `test_valence_signed_propagation_landing.py` PASS) -- turn on when the consumer wants the wider/sharper axis.

- **2026-08-26 — MEMORY TIER / DEVIATION #2 advanced** (from `no_automatic_reliability_signal_reaches_the_source_oracle`,
  integrated EXCELLENT). A **DG pattern-separation + CA3 completion recollection gate** was built and re-verified:
  recollection now **self-certifies** (top-5% precision 0.938 vs counting 0.533 on the same items) and dual-process
  routing beats the counting floor CI-separated for the first time (0.365 vs UB 0.336), capturing ~half the oracle
  headroom; info-free twin loses, scramble collapses to 0.00. **Effect on this audit:** D1 (DG separation) moves
  from "SAME but orphan" toward a **proven role**; D2 (CA3 completion) gains the **self-certifying confidence** it
  lacked (for this use it no longer just "terminates in sign and buys nothing"). Answers board Q118 — a label-free
  selection signal IS CA3 completion confidence. **NOT closed:** deviation #3's *cortical-consolidated* read — this
  is the *episodic* recollection side. Lever for more = reading VOLUME (coverage), not a better gate. **Organ LANDED
  2026-08-26 as `hdlab/dg_ca3_recollection_gate.py`** (off-path WIRE_CANDIDATE, witness `test_dg_ca3_recollection_gate_organ.py`
  PASS, registered `dg_ca3_recollection_gate_v1`) — so D1 (DG separation) now has a live, importable, self-certifying
  recollection organ; wire it into the episodic retrieval path (see p2 `the_consolidated_cortical_store...`).

---

## 3. THE SCORECARD (from ORGAN_MAP §1 tally, 38 organs)

| fidelity of our op vs the brain's | count |
|---|---|
| **SAME — our equation IS the brain's** | **5 / 38** |
| RIGHT-OP, WRONG-METRIC | 13 / 38 |
| RIGHT-OP, WRONG-PLACE | 3 / 38 |
| WRONG-OP | 6 / 38 |
| **MISSING entirely** | **6 / 38** (was 7; the N400 coherence monitor was BUILT 2026-08-26, §2b) |
| UNSCORABLE (brain math UNPINNED) | 4 / 38 |

| how well the brain itself is pinned | count |
|---|---|
| an implementable equation exists in the literature | 12 / 38 |
| form pinned, key function/parameter UNPINNED | 12 / 38 |
| **core operation UNPINNED** | **14 / 38** |

Reachability: **~23 / 38 organs are on the live path (44 of 155 modules)** → ~54% of code unreachable.
Evidence: **10 / 38 organs' only evidence is a self-test PASS** (a construction proof, not a capability).

---

## 4. THE ARCHITECTURE, RECONCILED — every system, its organ, its fidelity

Grouped by the brain's functional tiers. `[P]` = brain equation PINNED, `[U]` = UNPINNED/contested (we invent).

### TIER 1 — PERCEPTION & LEXICAL FORM
- **Visual word form** (VWFA) `[U]` — `vwfa.py`/`char_*`. **RIGHT-OP-WRONG-METRIC:** 1-bit terminal quantiser; trigram order destroyed (position is a hashed atom, not a rotation).
- **Lexical category / POS** (post. temporal) `[U]` — `pos_tagger.py`+`perceptron.py`. **UNSCORABLE** (brain unpinned); own learned perceptron, HARD_PASS 0.906.
- **Dependency / argument-structure parse** (LIFG/pSTS) `[U]` — `arc_parser.py`. **UNSCORABLE**, and a real hole: head/deprel fields are **PLACEHOLDERS at inference** (only form+upos read). **SHARPENED 2026-08-26 (§2b, p4 relcl SOLVED): for filler-gap / reversible role assignment the general arc parser is MEASURABLY HARMFUL, not merely weak** (0.198 vs a random-nominal twin 0.305 — greedy first-order unlabelled decoding mis-attaches the embedded-verb→antecedent arc). **Route AROUND it:** a specialised incremental filler-gap resolver over UPOS + closed-class relativizers (no arc graph) reaches oracle level (0.953) where the arc route scores below chance. Do NOT invest in a stronger general parser for this.

### TIER 2 — SEMANTIC MEMORY (meaning)
- **Amodal concept hub** (ATL) `[U]` (sub-fact: combination ≈ additive `[P]`) — `lexical_similarity.py`. **WRONG-OP:** unweighted feature overlap is the *inverse* of the brain privileging distinctive features; feature dict hand-built.
- **Per-occurrence pooling** (cortical, divisive normalisation `[P]`) — `grounding_acquisition_loop.py`. **WRONG-OP:** `sign(Σ±1)` where the brain does pooled divisive normalisation; amplifies a noise dim to full weight ~1 in 7.
- **Across-occurrence accumulation** (CLS) `[U]` (weight function) — `reading_grounding_loop.py::observe`. **RIGHT-OP-WRONG-PLACE:** a real graded accumulator, thrown away by `sign()` one line before use (`freeze_graded` default OFF).
- **Representation format** (cortex: graded, low-dim, sparse `[P]`) — 256-dim bipolar default. **WRONG-OP + under-capacity:** dense binary where the brain is graded/sparse; 2,377 concepts in 256 dims; **16× dims buys +0.0843 (largest measured single lever we own).**
- **Sensorimotor spokes** (modality→hub, rule `[U]`) — `grounded_similarity.py`/`sensorimotor_spoke.py`. **RIGHT-OP-WRONG-METRIC + mis-applied:** cosine can't separate synonym from sibling (apple/orange 0.952), capped 0.45 so it never decides; SUPPLY not learning.
- **Semantic comparison** (ATL recurrent settling `[U]`) — `canonicalize_fast`. **RIGHT-OP-WRONG-METRIC:** Hamming between two 256-bit majority patterns ("there is no cosine in the brain").
- **Semantic control** (IFG, multiplicative gain `[P]`; gain function `[U]`) — `context_vector_masked`; dedicated organ is `modern_hopfield_readout.py` (softmax sharpen/blend) + scattered sub-parts. **RIGHT-IDEA-WRONG-ALGEBRA:** context enters *additively*, not as multiplicative gain; the faithful multiplicative version scored WORSE — but that is an estimation-noise result **blocked behind the dense-code defect (B4)**, not evidence against the brain. **Dedicated semantic control is THIN** — a gap.

### TIER 3 — COMBINATORICS & STRUCTURE
- **Thematic role assignment** (Competition Model: cue validity `[P]`) — `thematic_role_labeler.py`. **RIGHT-OP-WRONG-METRIC:** raw counts are not cue-validity; cue *cost* absent; animacy-dominant; HARD_FAIL on real text. **BRAIN-PINNED MECHANISM 2026-08-26 (§2b, p4 relcl SOLVED):** for the reversible non-canonical regime the faithful operation is GRADED ADDITIVE CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (Lewis & Vasishth 2005; McElree 2000) — the SAME operation as the p3 store; our validated discrete filler-gap resolver is its noise→0 competence limit. **LOCALISATION CORRECTION:** reversible role binding is POSTERIOR-TEMPORAL / pMTG / inferior-parietal (Beber 2025; Matchin & Hickok 2020), **NOT** a BA44 "syntactic movement" operator (soften any BA44-movement text). Unifies with E1/E2/E3 (computational homology, under-test — intact single-sentence syntax in amnesia).
- **Role–filler binding** (theta-gamma / conjunctive / tensor-product — **UNPINNED & 3-way CONTESTED** `[U]`) — `binding.py` (FHRR complex-multiply). **OPERATOR VALIDATED 2026-08-26** (see §2b): at EQUAL storage FHRR beats the writable brain theories (TPR/conjunctive), so it is an efficient choice, NOT the "deepest deviation." ➡️ **The deviation is one level up — the flat-superposition RETRIEVAL (shared with E2/E3): the brain SEPARATES into slots + retrieves CONTENT-ADDRESSABLY; a faithful version beats FHRR ~5x under a partial cue.** The owned fix (`ca3_completer` + `dg_pattern_separation`, both default-off) is unwired.
- **Situation-model register / event indexing** (SEM, PE-segmented `[U]`) — `situation_model_accumulate.py`/`_multibank`, `situation_reader.py`. **RIGHT-OP-WRONG-PLACE:** has the register; **missing the prediction-error segmentation that decides WHEN to write.**
- **N400 coherence monitor** (running-model update magnitude; reference `[P]`, norm `[U]`) — **BUILT 2026-08-26 (§2b): `hdlab/n400_coherence_monitor.py`** (off-path WIRE_CANDIDATE, witness PASS). No longer MISSING. The norm that WORKS is a GRADED forward CONTENT prediction error `1 − cos(content, running_event_gist)` (running reset per event), boundary-posted via the EST relative threshold; it segments discourse and fills the situation model 0.988 vs ≤0.762 floors. The norm that FAILS is the literal `||Δregister||` in the binding space (ties no-op). **Still ISLAND** — wire to `situation_model_accumulate` + measure on the live reader before any capability claim.
- **Construction-Integration** (Kintsch `[P]-ish`) — **MISSING.**

### TIER 4 — MEMORY SYSTEMS
- **DG pattern separation** `[U]` (level ~0.2% `[P]`) — `dg_pattern_separation.py`. **SAME** — but orphan (WIRED NO), untested.
- **CA3 completion** (auto-assoc; update rule = our Hopfield import `[U]`) — `cleanup_family.py`/`iterative_attractor.py`. **RIGHT-OP-WRONG-METRIC:** terminates in `sign()`; measured settling buys nothing. **2026-08-26 (§2b): recurrent attractor completion HURTS semantic pool-RANKING** — it re-promotes concept-code hubs (robust across temperature); the faithful ranking read is a *graded population read*, not a settled attractor (the attractor is a recognition op). *Consistent with the binding load-bearing negative: CA3 cleanup on a flat superposed read TIES argmax.*
- **Hippocampal one-shot write** (Marr `[P]`; allocation `[U]`) — `hippocampal_encoder.py`. **SAME (write op)** — index/allocation half missing; its 14/14 self-test is a **ceiling, not evidence** (exact cue solved by projection alone).
- **Consolidation / replay** (SWR; selection function `[U]`) — live: `reading_grounding_loop.py::checkpoint`; faithful: `continual.py` (**ISLANDED**). **WRONG-OP-CLASS at the live site:** single averaging op, ungated/un-interleaved/un-budgeted.
- **Working memory** (attractor vs synaptic — CONTESTED `[U]`) — `working_memory.py` **contains no WM (filename trap)**; `slot_attention_wm.py` = learned softmax head. **MISSING / RIGHT-OP-WRONG-METRIC.**
- **Sequence/order** (asymmetric Hebbian `[U]`) — `sequence_memory.py`. **SAME op-class.**
- **Successor representation** (`M=(I−γP)⁻¹` **FULLY PINNED** `[P]`) — `successor_representation.py`. **Faithfully implemented but MEASURED AND LOST** — 0/24 arms clear the bar; **degrades with scale** (its own ladder refutes "scale it up").
- **Cascade synapse** (multi-timescale, **FULLY PINNED** `[P]`) — **MISSING.** PARKED-BY-SCALE (advantage crossover N>~1e6; we run d≤4096, so a null here is the *published prediction*).
- **Synaptic tag & capture** (tag×PRP product `[P]`, but §10.1 says drop from pinned) — `excitability.py`. **RIGHT-OP-WRONG-METRIC:** single EWMA, not a two-factor product; WIRED NO.
- **Theta-gamma ordered buffer** (~7 slots `[P]`; encoding op `[U]`) — `situation_focus.py`. **RIGHT-OP-WRONG-METRIC:** capacity 4 vs ~7; order channel empty (HARD_FAIL).
- **Long-term semantic store** (no single brain analogue `[U]`) — `hd_fact_store.py`. **RIGHT-OP-WRONG-METRIC** ("the fourth prototype operator"); 65.7% of grounded facts are self-referential tautologies.

### TIER 5 — CONTROL, PREDICTION, METACOGNITION
- **Prediction / predictive coding** (residual precision-weighted `[P]`) — `predictive_coding.py`, `slot_attention_wm.py`. **RIGHT-OP-WRONG-METRIC:** residual computed on a `sign()`-quantised prediction (big & small flips indistinguishable); no precision term; WIRED NO; MIDDLE_BAND. *Encoder objective is also cloze, not forward-PC — see DEVIATIONS.* **FORWARD HALF NOW BUILT 2026-08-26 (§2b, predictive-reader SOLVED):** a role-specific grounded-feature forward predictor (verb → expected argument features) with GRADED −log P softmax surprisal (NOT the sign()-quantised residual) beats reactive + an at-chance wrong-verb twin on real anticipation, and PRECISION-WEIGHTING is validated (the missing term — high-precision verbs carry the benefit). The forward predictor (WORD/FEATURE level, ATL/angular) + the `n400_coherence_monitor` (EVENT level, frontal, backward-gist) are **TWO LEVELS of ONE predictive hierarchy**, composed across sentences (the discourse build). Organ landing QUEUED (proven-ready, default-off). *This entry's `sign()`/no-precision defects are the exact things the forward build avoids.*
- **Attention / information foraging** (MVT leave rule `[P]`) — `information_foraging.py`, `gap_driven_reader.py`, `corpus_registry.py`, `self_manager.py` (ACC/EVC halting), `situation_focus.py`. **The leave-rule exists but "WHAT TO READ NEXT" is effectively MISSING:** readable universe is a hard-coded 4-entry dict vs 36 corpora on disk; downgraded to MIDDLE_BAND (FROZEN beats FORAGE); the organ has never seen real text.
- **Metacognition / familiarity / abstention** (SDT criterion `[U]`) — `gap_detector.py` (**SAME — "the healthiest organ," AUC 1.000**, but its output has nowhere to go because foraging is unbuilt), plus a rich family: `refuse_gate.py`, `conformal.py`, `clarify_gate.py`, `completeness_checker.py`, `reachability_audit.py`, `quality_proxy.py`, `coref_distractor_suppress.py`. **Deviation:** no floor on refusal *correctness*; `state.refusals` written, counted, reloaded, then **never consulted**.
- **Reasoning over knowledge** (constraint satisfaction) — `reasoner.py` (**FAITHFUL, banked**), `multi_hop.py`, `gather_reason.py`, `glass_box_loop.py`, `kg_traversal.py`. Coverage-bound, not mechanism-bound.

### TIER 6 — AFFECT · GOALS · SOCIAL (BUILT, BUT LARGELY OUTSIDE THE FIDELITY AUDIT)
> These systems have real organs but are **NOT in the ORGAN_MAP's 38** — so their brain-fidelity has **never been
> scored.** That is itself a finding: the fidelity audit stops at the reading/memory pipeline.
- **Affect / valence / appraisal** (amygdala, vmPFC) — **richly built, UN-AUDITED:** `context_grounded_valence.py`, `consequence_learning_loop.py`, `wordnet_polarity_propagation.py`, `word_learning_tool.py`, `word_acquisition_loop.py`, `idiom_grounding.py`. *p3 (`propagate_along_the_relation`) lives here.*
- **Goals / reward / motivation** (BG, OFC) — **richly built:** `goal_typing.py`, `goal_owner_select.py`, `goal_achievement.py`, `goal_outcome_relation(_grounded).py`, `outcome_event_extraction.py`, `parse_goal_extraction.py`, `action_selection.py` (**BG Go/NoGo + TD, SAME op-class**), `successor_representation.py`, `self_manager.py` (DA vigor). *p1's convergent line (`organ_abstains`) lives here.*
- **Theory of mind / mentalizing** (TPJ, mPFC) — **ABSENT.** `state_of_mind.py` is explicitly *not* ToM (it's a coref tracker); the only false-belief (Sally-Anne, nested-HRR) work sits in `experiments/` and **was never promoted to `hdlab/`.** Clean gap + clean build target.

### TIER 7 — LEARNING & OUTPUT
- **Cortical learning rule** (lexical-semantic acquisition **UNPINNED, deliberately** `[U]`) — `learner/core.py`. **WRONG-OP:** MDL is model-selection, not a synaptic update rule; **the loop was never measured as a learner.**
- **Read→extract→consolidate loop** — PARTIAL (CLS shape right; the "what to extract from reading" step unsolved).
- **Language production / generation** (Levelt staged; lemma/lexeme split `[P]`) — **THIN, essentially ABSENT:** only `generation.py` (S-matrix + Langevin + cleanup). `substrate.py` production slots are EMPTY. The expressive side does not exist as an organ.

### COREFERENCE / ENTITY TRACKING — (spans tiers; the 07-30 "ABSENT" is corrected)
Heavily built: `coref.py`, `coreference_resolver.py`, `coref_distractor_suppress.py`, `bundle_focus_coref.py`,
`event_centrality_coref.py`, `scene_segment.py`, `state_of_mind.py`, `entity_slot_gate.py`, `slot_attention_wm.py`,
`situation_reader.py`, `event_bundle.py`. **RIGHT-OP-WRONG-METRIC:** invented arithmetic (`count + β·exp(−λΔ)`)
over a pinned *ordering*; **mentions are SUPPLIED (gold), so it does not transfer to raw prose**; margin over the
strong floor NOT CI-separated at n=57. ~~*Competitive antecedent resolution among 2+ plausible referents remains the
real open case.*~~ **MEASURED + FIXED 2026-08-28 (§2b, `coreference_is_capped_at_065_on_real_narrative` SOLVED/EXCELLENT,
owner-DONE):** the PRONOUN branch is now brain-faithful GRADED cue-based retrieval (softmax over pinned ACT-R activation,
reusing `graded_competition`) — 0.775 vs the incumbent hard-tier 0.603 (+0.172 CI-sep) on LitBank held-out competitive
pronouns; the incumbent hard tier was the CAP (below plain recency 0.717). Ties ACT-R by the MAP theorem; posterior
entropy = a calibrated abstain (AUC 0.617→0.806). Residual ~19% = the missing 2nd Bayesian term (coherence PRIOR). The
NAME/NOMINAL branch is now the open case: it SHATTERS 65.6% of multi-name gold entities (single-head-token cache root
cause) and caps who-did-what (oracle-coref 0.62 vs binder 0.17). hdlab landing QUEUED (opt-in default-off
`run_graded_retrieval`).

### DISCOURSE / BRIDGING — (also corrected from "ABSENT")
Exists as *relation* inference (`situation_model_accumulate` CausalLinkRegister, `goal_outcome_relation*`,
`gather_reason`, `multi_hop`). **Explicit causal/elaborative bridging of the UNSTATED** (Graesser) is still
thin/UNPINNED and, structurally, "IS coreference in disguise → must reuse the coref organ."

---

## 5. THE LARGE-SCALE DEVIATIONS (we do it, not the brain's way)

1. **MOST OF THE ARCHITECTURE IS INVENTION, NOT REPLICATION** — 14/38 core operations UNPINNED, 4 UNSCORABLE,
   only 5 SAME. Honestly labelled, but it means "brain-faithful" is *undefined* for a large fraction of the substrate;
   those parts are bets, and should be named as bets. **CORRECTED 2026-08-26 for BINDING (§2b, wire-and-measure machinery
   drill): the central binding operation is NOT a bare "our-invention" — FHRR is UNPINNED at the neural-IMPLEMENTATION
   level, but it is a DEFENSIBLE, PUBLISHED brain model:** SEM (Franklin, Norman, Ranganath, Zacks & Gershman 2020, Psych
   Review) binds role→filler with HRR circular convolution + bundling + a CLS split — our exact machinery — and VSA is the
   best-specified computational-level theory with a neural existence proof (Eliasmith SPA/Spaun). **Owner-locked: KEEP
   FHRR; do NOT propose replacing the binding algebra.** The fidelity lever is STORE ORGANIZATION (dense bundle →
   sparse/indexed + case-frame content), which is FHRR-compatible.
2. **~~THE `sign()` QUANTISER EVERYWHERE~~ — REFUTED 2026-08-26 AS THE AVERAGING-MACHINE LEVER (see §2b).** The
   34-site `sign()` was theorised to make the system an averaging machine. **It does not, and the graded flags are
   already default-ON (since 08-14), not default-OFF.** On the real open-vocab task graded vs sign is NULL, and the
   whole brain-faithful code-format family + a self-supervised learner all tie plain counting below a generic-word
   floor. **The SUM is faithful; the terminal normaliser is a non-issue.** The real deviation is one level up:
   **meaning SUPPLY + the TWO SIMILARITY SYSTEMS (associative relatedness vs feature similarity) + SEMANTIC CONTROL
   gating.** The averaging machine is a signal-EXTRACTION/supply failure, not a quantiser artifact.
3. **WE QUERY THE WRONG MEMORY** — retrieval answers out of the fast episodic (hippocampal) codes and **never
   reads the consolidated cortical store** (ablating consolidation moved the read-out by 0.0000). The standing
   "memorises but does not transfer" negative is the *signature of hippocampus-only retrieval*. **REFINED
   2026-08-26 (measured, §2b):** reading the store the brain's way DOES beat the episodic path ~10× on transfer
   (CI-separated over the twin), so the cortical-read organ is real and fixable — BUT it does not clear counting
   and carries no cue-specific signal on powered unseen queries, so the wall is **BOTH a MISSING cortical-read
   organ AND transfer-bearing consolidated CONTENT** (data/lifetime-scale, not the read op).
4. **DENSE where the brain is SPARSE + GRADED** (B4) — the largest measured single lever we own (16× dims).
5. **ONE STORE DOING TWO JOBS** — fast hippocampal binding and slow cortical consolidation are conflated; the
   faithful consolidation engine (`continual.py`) is **islanded**.
6. **ADDITIVE where control is MULTIPLICATIVE** (IFG gain, C3); **CLOZE where learning is FORWARD-PREDICTIVE** —
   **SPLIT 2026-08-26 (§2b) into two rows with OPPOSITE verdicts:** the UPDATE/segmentation half (the N400 coherence
   monitor, F5) is missing-buildable-and-WINS → BUILD; the LEARNING half ("we learn by cloze not forward-PC") is a
   RIGOROUS NEGATIVE (forward-PC does NOT beat cloze on paradigmatic meaning) → DEPRIORITISE. Do not couple them.
7. **~54% OF THE CODE IS UNREACHABLE** — built-but-unwired islands; several *faithful* organs (DG separation,
   cascade-adjacent, `continual.py`) sit unwired.

---

## 6. THE LARGE-SCALE GAPS (absent or thin systems)

- **6 organs MISSING outright** (was 7; the **N400 coherence monitor was BUILT 2026-08-26**, §2b — off-path, awaiting
  live wiring), the load-bearing remainder being: the **cortical-read organ** (fixes deviation #3),
  **Construction-Integration**, **corpus-selection foraging** ("what to read next"), the **cascade synapse**
  (parked-by-scale), and **discourse bridging of the unstated**.
- **Theory of Mind — ABSENT** (mechanism exists in `experiments/`, never promoted).
- **Dedicated semantic control — THIN** (one primitive + scattered sub-parts). **CONFIRMED 2026-08-26 (§2b):** even
  additive context-coherence with the offline-winning grounded rep is at chance on the frequency-defeating items and
  ties its info-free twin; its near-term working substrate is the frequency PRIOR (+ the associative channel on
  data-rich senses), NOT a grounded context channel — and a real test of context OVERRIDING the prior needs a modern
  WSD benchmark not on disk.
- **Language production — THIN** (one file; the expressive half of a brain is missing).
- **Scope gap in the audit itself:** affect, goals/reward, and metacognition are **built but never fidelity-scored**
  against the brain — likely deviations are hiding there, unmeasured.

---

## 7. THE MEANING RE-FRAME (2026-08-26 — updates the plan's foundational premise)

`LONG_TERM_PLAN.md` is built on "meaning is absent / you cannot route meaning that was never supplied / every
downstream fix is a better filing system for empty folders," and every phase is gated **supply-before-architecture**.

**This session weakened that premise.** On a **frequency-controlled (fair) metric**, the grounded meaning signal
**beats the strongest frequency floor CI-separated** (0.741 vs 0.558; info-free twins lose) — the old "counting
beats us" was measured on a metric that was secretly scoring frequency. **So meaning is present-but-unwired and
context-free, not empty.** The block has moved from "there is nothing to route" to "route it, and condition it on
context." The plan's Phase-1 "supply more norms" lever is also downgraded (projecting the norms we
have covers the gap). **Reconcile the plan's §3 diagnosis with this before quoting it.**

**TESTED 2026-08-26 (§2b — `the_meaning_win...` negative): the "condition it on context" half does NOT transfer.**
The offline win is CONTEXT-FREE and SIMILARITY-typed. Put into a leakage-controlled context-conditioned WSD
instrument, NO context channel — grounded OR associative, label OR experience-prototype — beats the frequency PRIOR,
and on the frequency-defeating (subordinate) items the grounded channel is at chance and ties its info-free twin
(no context-selection signal). So the block splits AGAIN: the **frequency PRIOR** (most-frequent-sense; Duffy &
Rayner reordered-access) is a real WIRE-ABLE gain (beats uniform CI-sep) but NOT a flag flip — the reader is
SENSE-BLIND (one blended vector per lemma → no per-sense representation to default over); context OVERRIDING
frequency is UN-TESTABLE here (subordinate senses attested once) and needs a MODERN WSD benchmark (SCWS/WiC/SemCor,
none on disk). Wire grounding for SIMILARITY, the frequency prior for the sense default; do NOT wire a
context-selection channel until a modern instrument shows one earning its keep.

**BOUNDED 2026-08-26 (§2b — the `sign()` refutation drills):** "meaning present-but-unwired" is TRUE for the
**ASSOCIATIVE RELATEDNESS** system (distribution carries it, WordSim ρ 0.25) — that read-out we can wire. It is
**NOT** true for the **FEATURE SIMILARITY** system (distribution ~0 on SimLex): that axis is genuinely thin and must
be BUILT brain-faithfully from grounding + structured local context, then GATED against the associative system by
semantic control. So "present-but-unwired" splits: one system to wire, a second system to build. Grade meaning on
human relatedness/similarity, not taxonomic WordNet, or the associative system reads as broken when it is not.

---

## 8. LEVERAGE RANKING — and how it reshuffles the queue

> **🧭 STRATEGIC DECISIONS 2026-08-26 (owner: "do the right things, not the easy ones; most effective + most brain
> foundational"). The programme is now WIRE-AND-MEASURE, sequenced by this ranking — not more isolated parts:**
> 1. **RETRIEVAL ARCHITECTURE FIRST (the #1 LIVE deviation, §5 #3 "we query the wrong memory").** The live reader
>    stores/retrieves by exact-key hash with no partial-cue path; three integrations (binding, content_addressable,
>    cortical_store) all re-located their fix here. The FIRST end-to-end composition (p1) is content-addressable
>    additive retrieval over the live register + the recollection gate, measured on a cross-event/partial-cue task —
>    and it DOUBLES as the front-end attribution test (no gain on the ~0.32 front-end ⇒ the front-end is the wall).
>    p2 (fan effect) is the SAME machinery from the interference side — coupled, one shared build.
> 2. **THE CODE (sparse+graded, B4/D4)** — load-bearing on the retrieval READ; couple with #1, not the retired sign() line.
> 3. **MISSING CONTROL/UPDATE ORGANS** (N400 segmentation, the frequency PRIOR sense-default) — follow-on compositions in p1.
> 4. **MEANING CONTENT/SUPPLY** — the recurring wall; the SIMILARITY axis is built (whitening), the CONTEXT-SELECTION
>    axis is **DATA-blocked, DEFERRED** (see below).
> **✅ ACQUIRED 2026-08-26 (owner-directed), but SHELVED BEHIND retrieval-first.** The modern-WSD-benchmark data block
> is REMOVED: **SemCor** (sense-tagged text via nltk — subordinate senses attested MANY times, the exact thing McGuffey
> lacked; VET: 1,872 multiply-sensed lemmas in 80/352 files) + **WiC** (5428/638/1400 balanced human-judged binary
> contextual-sense pairs, in repo) are VETTED and loadable (`tools/load_wsd_benchmarks.py`, `data/wsd_benchmarks/MANIFEST.md`).
> SCWS (the continuous-modulation frame) NOT acquired — canonical mirrors dead. The asset is READY but the WORK stays
> BEHIND the retrieval wire-and-measure (the sequencing is unchanged — acquiring the data does not reprioritise the
> lane; it just removes the block for when we reach it). The front-end fix is already in flight (p7 relcl, awaiting owner).
> **🚫 NO new find-a-part problems** until the accumulated modifications are proven to compose (or diagnosed as swamped).

The current problem queue (p1–p4) captures **only one** of the top brain-fidelity levers. The biggest
cross-cutting deviations are **not queued.** Candidates, ranked by leverage (blast radius × tractability):

1. **The `sign()` → graded path — DEMOTED *as a READ-OUT lever* 2026-08-26; but ALIVE as a BINDING-SITE guardrail
   (§2b CORRECTION).** On the read-out the graded switch is already ON and buys ~null. **BUT** in the
   binding/superposition regime sign() IS a real averaging machine for CORRELATED fillers, coupled to B4 (graded
   fillers + a signed bundle re-creates the averaging machine; capacity cliff B*=8→B*=12) — so keep it as a joint
   sign()+B4 guardrail on the binding/memory line (p3, p5), NOT a read-out change. **At the read-out, REPLACED at the
   top by the meaning-SUPPLY / TWO-SIMILARITY-SYSTEMS / SEMANTIC-CONTROL line.** **✅ DELIVERED 2026-08-26 (§2b,
   integrated PARTIAL/EXCELLENT):** the feature-similarity system is BUILT + proven (distinctive-feature WHITENING beats
   raw grounding CI-separated on held-out SimLex/SimVerb; specialises toward similarity); the semantic-control SWITCH is
   REFUTED (fixed multiplicative FUSION beats the task-gate even with a strong associative system) — so the near-term
   wire is the whitening transform + a FIXED two-system fusion, NOT a switch; the gate is a later selection-task (WSD)
   deliverable. Residual = meaning SUPPLY (richer features, per the finer drill's fidelity boundary).
2. **The cortical-read organ (deviation #3) — VALIDATED-BUT-CONTENT-BOUND 2026-08-26 (§2b).** The read beats the
   wrong memory ~10× but the residual wall is the consolidated CONTENT (data/scale), not the read op. Land the CLS
   matched-pair read default-off (architecture hygiene); route the residual to the content/supply lane (item #1).
3. **Meaning wiring + context-conditioning — CONTEXT-SELECTION REFUTED 2026-08-26 (§2b, `the_meaning_win...`
   integrated PARTIAL).** Conditioning the read-out on context does NOT beat the frequency prior in EITHER meaning
   system; the offline win is context-FREE + similarity-typed. **The wire-able residual is the frequency PRIOR** (a
   real gain, but a LIVE architectural change because the reader is sense-blind → packaged as a follow-on
   wire-and-measure build, gated on a downstream comprehension number). Do NOT wire a context-selection channel;
   context OVERRIDING frequency is MODERN-BENCHMARK-CONTINGENT (SCWS/WiC/SemCor, none on disk — an acquisition need).
4. **Dense → sparse+graded code (B4, deviation #4).** Now measured LOAD-BEARING on the cortical READ (0.025→0.156),
   NOT on the open-vocab read-out (null there). Couple with the cortical-read work (#2), not the retired `sign()` line.
5. **The binding operator (E1) — RESOLVED 2026-08-26 (p3, EXCELLENT).** The operator is VALIDATED at equal
   storage (beats the writable brain theories); the REAL lever is one level up — the flat-superposition
   **RETRIEVAL**. Wire the owned content-addressable path (`ca3_completer` + `dg_pattern_separation`) into the
   separated store, measured on the live task (~5x under partial cue). See §2b + the binding SOLVED Rec B.
6. **Fidelity-audit the affect / goals / metacognition systems** — built but never scored against the brain.
7. **Promote Theory of Mind** from `experiments/` into a real organ.
8. p2 (reliability signal), p3 (valence propagation), p4 (relcl parser) — the existing queue, unchanged.

**Recommendation:** the next problems to package are #1 (`sign→graded`) and #2 (cortical-read), because they are
cross-cutting, tractable (flags/organs partly exist), and outrank most of the current queue on blast radius. Do
NOT flood — package them as the current builds converge.

---

## 9. OPEN RECONCILIATION ITEMS (to close in later passes)
- Re-verify the ORGAN_MAP verdicts that are load-bearing here against HEAD (esp. B4's +0.0843, the `sign()`
  2AFC/hit@1 split, the retrieval-order 0.0000 ablation).
- Fold the affect/goals/metacognition organs into a fidelity table (currently un-scored).
- Reconcile `LONG_TERM_PLAN.md` §3 with the §7 re-frame in the plan file itself.
