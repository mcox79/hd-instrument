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
