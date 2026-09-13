# SIGNAL-LOSS LEDGER — the affected-entity (pronoun-undergoer) chain, rung by rung (started 2026-09-12; LIVING)

**Why (owner 2026-09-12, at compaction):** "+4 points is fine, but not great. ... a dedicated focus on establishing mathematical
brain foundational operation to all upstream components. This is how we break through walls — if items are clearly brain
foundational, they correctly separate and send signals downstream, essentially lossless." This ledger walks the chain from the
end decision UP, and records at each rung: the brain computation it must perform (the `BRAIN_MATH_REFERENCE.md` row), what the
organ does today, its BF status, and the MEASURED loss when that rung is replaced by gold / an oracle (the prize for making it
BF). The first lossy non-BF rung is the next build. Slice: THIRD-person GUM undergoer pronouns (n=596 gold / 593 predicted),
competent-reader reference ~0.85–0.90.

| # | rung (downstream → upstream) | brain computation (math row) | organ today | BF status | measured loss / prize | source |
|---|---|---|---|---|---|---|
| 0 | END: pick the affected entity | arg-max posterior = prior (salience) × likelihood (binding, parallelism) × expectation (event) | `affected_entity_resolver.resolve` + `EntityTokens` | BF_SPIRIT (pinned cascade, swept params) | deployed 0.4789; gold roles 0.5403; competent reader ~0.85–0.90 → total gap ~0.37 | cell `exp_affected_entity_token_history_gum_v1` |
| 1 | Event expectation (who the event acts on) | P(kind(X) \| agent, verb), JOINT, in-focus, precision-gated (N400 update) | NOT BUILT; marginals (simplewiki selectional, ROC GEK, hub relatedness) REFUTED-AS-BUILT | — | in-focus ceiling: gold within top-3 = 0.753 vs 0.540 → prize ≤ +0.21; residual anatomy: gold = NEW low-prominence referent (single mention 57 vs 21) | probes v2/v3/v8/v9 |
| 2 | Salience prior operating point (role prominence, history depth, decay) | ACT-R base-level B = ln Σ w(role)·Δt^−d | `salience_binder.actr_activation` with w=(4,2.5,2,1), d=2 (fitted on LitBank subject pronouns) | BF (computation) / swept params | **MEASURED (probe v10, THIRD n=570): the landed operating point is at its optimum — no swept variant is CI-sep better** (role magnitudes (4,2,1)/(2,2,1)/(1,1,1)/(4,4,2)… all within CI; history depth m=1..5 = full; d=1 −0.045 / d=5 −0.066 CI-sep worse; parallelism gammas (0,0) −0.105 CI-sep) → rung 2 is NOT lossy; the prior's parameters are not the lever | probes v6/v10 |
| 3 | Entity tokens (object files) | token identity by discourse continuity; every reference accrues | head-lemma buckets + pronoun accrual (`EntityTokens`); gold-free Heim files = parity | MODEL | ORACLE gold tokens with full history +0.091 — circular (needs correct pronoun resolution); the coref two-half line owns it | probes v5/v7 |
| 4 | Mention source (which NPs are referents) | every referring expression is a token (pronouns, reflexives, NP heads) | `referent_per_np_source` (content-head NPs + PRONOUN_SCOPE pronouns; reflexives fixed 2026-09-12) | BF_SPIRIT? (unaudited here) | 10% of items have NO prior non-pronoun mention of the gold (62/596) — partly cataphora/abstract, partly mention-source misses → TO MEASURE | probe v6 |
| 5 | Grammatical roles / heads (the parse) | the brain's parse is graded, acquired from reading; roles feed binding + parallelism + targets | `pos_tagger` + `arc_parser` + `arc_labeler` (supervised averaged perceptrons) | **NOT_BF** (5 organs; declared scaffold) | **MEASURED (probe v11, same 596 items, forward-half decision): total parse loss −0.0705 CI[−0.096,−0.045]; LABELS alone −0.0369 CI[−0.057,−0.019] (52%); HEADS alone −0.0117 CI[−0.022,−0.003] (17%); tagger ≈14% (gold POS recovers −0.0705→−0.0604); interaction the rest.** The lossy rung is the dependency LABELER (`arc_labeler`): it sets the undergoer targets, the Principle-B co-argument and the parallelism roles. Reading-learned arc acquisition (pri-11) fixes heads only (17%). → the BF replacement is a ROLE-ASSIGNMENT organ (cue competition: word order / case / agreement / animacy — Bates-MacWhinney Competition Model) | probe v11 |
| 6 | Tokenisation / sentence segmentation | statistical-orthographic segmentation (Saffran; VWFA) | `situation_reader.read(conll_path)` consumes CoNLL GOLD tokens/sentences on every board instrument; a free-text front-end (`token_vocab`, regex in cells) is NOT on the scored path | n/a here (gold) — the live free-text path is unaudited | 0 on this instrument | audit 2026-09-12 |
| 5b | Word form → lemma (morphology) | decomposition into stem + affix (Taft-Forster; dual-route) | WordNet `morphy` AT READ TIME in ~10 organs (nltk wordnet corpus = offline lexical foundation, admissible as an asset; the runtime stemmer call is the pri-12 defect) | NOT_BF (runtime external tool) | not measured on this decision (lemmas key the entity tokens, rung 3) | pri-12 brief |

## Order of the upstream pass — OWNER 2026-09-12: TOP-DOWN BY POSITION (the organs that START the reading chain first), not by loss share
0. Tokenisation/segmentation: gold on every board instrument (rung 6 row) → no loss here; the free-text front-end is a separate audit.
0b. Morphology (rung 5b): WordNet morphy at read time = pri-12 (posted); the only rung above categories that is non-BF at inference.
0c. **CATEGORIES (the tagger) = the first lossy organ of the chain → `exp_reading_induced_categories_v1` (0.745 type / 0.722 token @1M lines; research note `notes/RESEARCH_reading_induced_categories_2026-09-12.md`).** Then heads, then labels (done).

### (superseded ordering, kept for lineage) by measured loss × BF status
1. **Rung 5, the parse spine (−0.0705, NOT_BF) — DECOMPOSED (v11): labels 52% > heads 17% > tagger 14%.** The first build of the
   upstream pass is a brain-foundational ROLE LABELER for the coarse relations this decision consumes (SUBJ / OBJ / passive-subject /
   by-agent / OBL): the Competition Model's cue competition (word order, case morphology, agreement, animacy), graded; measure it on
   the same 596 items against the supervised labeler (−0.037 to recover) and on UD-EWT/GUM label accuracy. Then the reading-learned
   arc scorer for heads (17%), then reading-learned categories for the tagger (14%).
2. **Rung 2, the prior's operating point:** DONE (v10) — at optimum; nothing to change.
3. **Rung 4, the mention source:** count the 62 unreachable items by cause (cataphora / abstract referent / missed NP head).
4. **Rung 3, entity tokens:** coordinate with the coref two-half line (oracle +0.091).
5. **Rung 1, the event expectation:** build the JOINT store from our own parsed events only after rungs 5/2/4 are BF — its input
   (roles, tokens) must be lossless first, or its measured value is a lie.

## Build sketch — the brain-foundational coarse ROLE LABELER (rung 5, first build; written 2026-09-12 before compaction)
- **Brain computation (PINNED):** grammatical roles are assigned by PARALLEL CUE COMPETITION (Bates & MacWhinney): word order
  (English-dominant), case morphology (him/her/them/me/us/whom are OBJECT-case — a categorical cue the supervised labeler can only
  learn statistically), voice morphology (be/get + participle, by-PP → passive subject / by-agent), agreement, animacy; cue weights
  = learned cue validity; additive activation → softmax posterior (`hdlab.graded_competition`).
- **Reuse (one structure, one organ):** extend `hdlab/graded_role_assigner.py` (BF_SPIRIT; already has `voice_cues`, `robust_passive`,
  `gap_config`, `cue_supports`, `competition_pick`, `agent_supports`, `agent_competition_pick`) with a `coarse_roles(toks, pos, heads)`
  readout: for every nominal/pronoun head, the posterior over {SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER} relative to its
  governing verb (heads from the parser; the heads rung costs only 17%). Case morphology enters as a categorical cue (PINNED).
- **Consumer wiring:** `affected_entity_resolver` / the cell read roles via `role_class(dep)` and `PATIENT_DEPS`; the board arm and
  the reader's `_router_roles` consume labels. Add a switch in `exp_affected_entity_token_history_gum_v1._overlay_predicted`-style
  path: labels from (a) supervised `arc_labeler`, (b) `coarse_roles` competition, (c) gold — same 596 items.
- **Bar:** recover a CI-sep share of the −0.0369 label loss on the decision (gold 0.5403 / supervised labels 0.5034), no regression
  on the board's who-did-what dims (they consume roles too), label accuracy on UD-EWT/GUM reported for the coarse set; twin =
  cue weights shuffled. Params (cue validities) learned from cue validity counts or swept — never hand-fitted to this slice.
- **Labeler confusion measured (probe v12, GUM test, 41,977 nominal/pronoun tokens):** coarse-class accuracy SUBJ 0.742, OBJ 0.776,
  PASS_SUBJ 0.581, **BY_AGENT 0.106**, OBL 0.778, OTHER 0.718; biggest confusions are with OTHER (SUBJ→OTHER 1637, OBJ→OTHER 843) and
  OBL↔OBJ (579/396). **25.4% of gold undergoer PRONOUNS (428/1682) are labelled out of the undergoer set** — the target-loss mechanism.
  Pronoun CASE violations are rare (obj-case→SUBJ 1.4%; subj-case→OBJ/OBL 0.5%), so case is not the missing cue; the losses are
  order/attachment/voice: a post-verbal bare nominal dependent of the verb mis-filed as OTHER, and passives/by-agents (Principle-C
  co-argument) badly handled. The Competition-Model labeler must therefore weight WORD ORDER relative to the governing verb, the
  PREPOSITION cue (by + passive morphology → BY_AGENT), and VOICE morphology highest; measure per class against these numbers.
- **First Competition-Model coarse labeler (probe v13, `graded_role_assigner.coarse_roles`, hand-ORDERED validities, verb-governed
  nominals only):** decision on the 596 items: CM 0.4765 vs supervised 0.4698 (+0.0067, CI incl. 0) on predicted heads; with GOLD heads
  CM 0.5017 vs SUP 0.5034 (parity) — i.e., BOTH labelers lose the same −0.037 vs gold labels given the heads. Per-class label accuracy
  (GUM test, predicted heads): BY_AGENT 0.736 vs 0.106, OBJ 0.792 vs 0.776, PASS_SUBJ 0.588 vs 0.581, OTHER 0.788 vs 0.718 — but
  SUBJ 0.526 vs 0.742 and OBL 0.24 vs 0.778. Causes (structural blindness, not cue weights): copular clauses (the subject's head is
  an ADJ/NOUN predicate, not a VERB → filed OTHER), noun-governed obliques (nmod → my OTHER), and the preposition cue requires the
  ADP to attach to the nominal (fails under predicted heads). Next: surface/structure cues for these three, validities LEARNED on
  UD-EWT train (`tools/build_coarse_role_validities.py`), re-measure.
- **Competition-Model coarse labeler v3 (2026-09-12, post-compaction; `graded_role_assigner.coarse_role_cues/coarse_roles`,
  asset `data/frontend_assets/coarse_role_validities_ud_ewt.json`, learner `tools/build_coarse_role_validities.py`):** the v1
  learned validities PROVED the loss was cue design (`non_verb_head` reliability 0.497 on 51% of nominals = chance; `voice_passive`
  0.397 = negative weight). v3 = categorical cue VALUES with per-role learned strengths, read WITHIN the head-class x order
  configuration as contrasts log P(role|config,value) - log P(role|config) (an always-on value = exactly 0; Dirichlet prior
  centered on the configuration, m=2) + the three missing structural cues (copula `aux_between` 0.92 -> SUBJ; surface preposition
  preceding the nominal span; ADJ/NOUN-predicate configurations) + a GRADED voice cue (be/get/being+participle `strong` 0.89 ->
  PASS_SUBJ vs `weak` by-PP/reduced evidence 0.85 -> SUBJ). Intermediate lesson kept: a flat additive table over all cue values
  (v2-naive) double-counted the majority class through redundant "absent" values (OBJ -> OBL 1031x on UD-EWT test, OBJ 0.099);
  the configuration-conditioned form fixes it. **Held-out UD-EWT TEST, gold heads/POS, 8362 nominals: overall 0.872; SUBJ 0.925,
  OBJ 0.951, PASS_SUBJ 0.769, BY_AGENT 0.944, OBL 0.745, OTHER 0.905** (residual: OBL -> OTHER 523 = bare post-nominal nmod
  without a preposition, e.g. dates/measure nominals). Witness `verification/test_coarse_role_competition.py` 18/18 (cues, canonical
  constructions, posterior, zero-contrast rule, shuffled-strength twin breaks the labels). Decision-level result on the 596 items
  (probe v13 re-run) recorded below when it lands.
- **v3 DECISION-LEVEL (probe v13 re-run, same 596 items, predicted POS + predicted heads = deployment):** CM 0.4899 vs supervised
  0.4698 = **+0.0201 CI95 [−0.0017, +0.0419]** (29% of the −0.0705 parse loss recovered; CM − GOLD −0.0503 vs SUP − GOLD −0.0705);
  with gold heads CM 0.5151 vs SUP 0.5034 (+0.0117 [−0.010, +0.034]). OTHER→supervised fallback is WORSE for the decision (+0.0067):
  the competition's own abstention is more precise than the perceptron's fine label. GUM coarse-label accuracy (predicted heads)
  CM vs SUP: BY_AGENT **0.773 vs 0.106**, OBJ 0.776 = 0.776, SUBJ 0.714 vs 0.742, PASS_SUBJ 0.527 vs 0.581, OBL 0.654 vs 0.778,
  OTHER 0.710 vs 0.718. Not yet CI-sep: the remaining losses are PASS_SUBJ (the voice cue reads the HEAD's POS/aux window — when the
  parser heads the pronoun on the AUX, config = AUX_pre → SUBJ) and GUM's OBL→OTHER (bare nmod/tmod nominals). Next: surface-robust
  passive cue (nominal + be/get + participle regardless of which token is the head), GUM-vs-EWT label-convention check, re-measure.
- **✅ v3 FINAL (2026-09-12 late; DET-edge preposition scan + possessives classed OTHER; asset relearned):** held-out UD-EWT test,
  gold heads: **0.917** (SUBJ .926 OBJ .953 PASS_SUBJ .769 BY_AGENT .944 OBL .887 OTHER .920). **Decision on the 596 items,
  deployment parse (predicted POS + heads): CM 0.4933 vs supervised 0.4698 = +0.0235 CI95 [+0.0033, +0.0436] — CI-SEPARATED**
  (CM − GOLD −0.0470 vs SUP − GOLD −0.0705: a third of the parse loss recovered); gold heads +0.0151 [−0.007, +0.037];
  fallback-to-perceptron variant +0.0084 n.s. (the competition's own abstention is the better decision). GUM label accuracy
  (predicted heads) CM vs SUP: BY_AGENT 0.773 vs 0.106, OBJ 0.779 vs 0.776, OBL 0.763 vs 0.757, OTHER 0.742 vs 0.609, SUBJ 0.712
  vs 0.742, PASS_SUBJ 0.536 vs 0.581. **Decomposition on GUM (CM, 41,977 nominals): gold POS+heads 0.845 → predicted POS 0.781
  (−0.064) → predicted heads 0.698 (−0.083)** → the labeler is a clean rung; its signal is lost in the TAGGER and HEADS above it
  (rung 5 continues upward: pri-8 categories, pri-11 heads). **LIVE WIRE:** `arc_labeler.COMPETITION_ROLES=True` (the one
  `label()` every consumer reads): argument roles of nominal dependents = the competition's; a perceptron argument label the
  competition rejects → `dep`; fine non-argument relations kept. In flight: full board no-regress (agent) + perceived-cue
  validities (learned on predicted POS/heads over train, `--perceived`) vs gold-learned on the same items.
- **Live-wire rule settled by ablation (probe v14, same 596 items):** the first overlay (competition argument roles + every perceptron
  fine relation kept) scored 0.4765 = −0.0168 CI95 [−0.030, −0.005] below the pure competition labels (0.4933). Wiping ONE retained
  relation class at a time to `dep`: `nmod` alone recovers the full +0.0168 (→ 0.4933, = pure); compound/flat, conj, appos,
  modifiers, root/parataxis each change NOTHING (Δ exactly 0). Mechanism: 3154 bare nominals the competition calls OTHER kept the
  perceptron's `nmod`, which `affected_entity_resolver.OBJ_DEPS` consumes as an OBJECT-class role (parallelism + Principle-B
  co-argument) → wrong role parallels. Rule landed: **the competition owns its whole CLASS SPACE** (nsubj/csubj/obj/iobj/obl/nmod
  except nmod:poss) — an in-space perceptron label the competition rejects becomes `dep`; fine non-argument relations
  (compound/conj/appos/flat…) stay the perceptron's (measured irrelevant to this decision; needed by other consumers). Perceived-cue
  validities (learned on predicted POS/heads): +0.0252 vs SUP, +0.0017 [−0.003, +0.008] vs gold-learned = a tie → keep gold-learned
  (simpler asset); the perceived asset is kept on disk for the tagger/heads rungs where perceived cues should diverge more.
- **✅ LIVE PATH VERIFIED (probe v13 final, `LIVE_labels` = `ArcLabeler.label()` with module defaults):** 0.4933 = the pure competition
  labels exactly (Δ 0.0000), **+0.0235 CI95 [+0.0050, +0.0436] over the supervised labeler** on the deployment parse. Rung 5's LABEL
  share of the loss (−0.0369) is now −0.0134 (CM − SUP_goldheads −0.0101 n.s.); the residual parse loss is HEADS + TAGGER.
- **TOP RUNG — categories induced from reading (`exp_reading_induced_categories_v1`, 2026-09-12):** Harris/Mintz/Redington
  substitution classes over immediate frames; gold UPOS for EVALUATION only. Phase-diagram moves at 20k Simple-Wiki lines, k=34
  (many-to-one on UD-EWT test): log-weighted k-means 0.542 → exposure-weighted (one update per token read; Rumelhart-Zipser
  competitive learning) 0.669 → + orthographic form classes (punctuation/numerals by visual form, pre-lexical) **0.707**
  (majority floor 0.141, shuffled twin 0.38; ADP 0.93, DET 0.93, NOUN 0.82, VERB 0.71, SCONJ 0.56; CCONJ/PART still 0 —
  "and" patterns like a comma). Token-level graded readout P(c|w,left,right) with a learned suffix/digit form cue for unknown
  words: 0.653 at 100% coverage. Ward hierarchical REFUTED (0.395 = twin; no brain story). Prior attempt 0.323 @8k sentences
  (exp_parser_fully_bf_chain_v1) was a weak implementation, not a ceiling. Exposure-weighted sweep (50k→1M lines × k∈{17,34,68})
  running; 50k/k34 (pre-form-class code) 0.693. LANDING FORM (owner: plastic, never frozen): online Hebbian accrual +
  competitive-learning updates with observe(tokens), state persisted as a grown asset; batch = measurement only.
- **Plastic form measured (`--online`, 20k lines in 4 consolidations, k=34, eta 0.05):** Hebbian accrual + competitive-learning
  centroid updates (MacQueen/Rumelhart-Zipser) reach 0.677 → 0.654 → 0.689 → 0.670 many-to-one (batch equilibrium 0.707),
  coverage 0.792 (inventory fixed at the first consolidation → an inventory-GROWTH arm is the next plasticity step). The learner
  keeps adapting after landing; eta and the consolidation period are swept parameters. Sweep (exposure-weighted, pre-form-class
  code): 50k/k17 0.577, 50k/k34 0.693, 200k/k17 0.618 — k matters more than budget so far; 200k/k34, 200k/k68, 1M pending.
- **FULL BOARD with the competition labels LIVE (2026-09-12 16:31Z, commit e03e710bc, 1565 s):** pooled AGG 0.6408 → 0.6377.
  UP: affected_entity 0.3874 → 0.3972 (n 777 → 851: more pronouns now carry undergoer labels), forward half 0.4789 → 0.5008
  (n 593 → 613), crosstype_experiencer +0.003. DOWN: who_did_what_patient 0.8303 → 0.8088 (n=1255), state 0.8333 → 0.8148
  (n=378), selective_reliability.patient_defer 0.967 → 0.951 — the UD-EWT deprel-graded consumers. Everything else identical.
  **OWNER RULING (verbatim intent): a downstream regression after a more-BF upstream is NOT failure — the top now carries MORE
  signal; REPAIR THE CONSUMERS to receive it, never revert the BF rung.** Diagnosis (UD-EWT test, deployment parse, 8362
  nominals): competition 0.804 vs perceptron 0.766 overall; SUBJ 0.796 vs 0.844 (post-verbal subjects labelled OBJ by raw
  order ×34; pre-verbal subjects labelled OBL by a preposition scan crossing into a preceding phrase ×26); PASS_SUBJ 0.481 vs
  0.583 (n=108); copular subjects 0.720 vs 0.782 (n=528); BY_AGENT 0.694 vs 0.056; OTHER 0.806 vs 0.683. Work-list: (1) cue
  fixes for the two named gaps (pre-verbal-slot cue; direct-vs-far preposition) — more upstream signal; (2) the patient read
  and the copular holder read consume the competition's GRADED posterior, not its MAP label; re-run the board.
- **Hand-off probes (2026-09-12 late):** (a) labeler reading the TAGGER's calibrated posterior for the head's category
  (`coarse_role_posterior_tagmarg`, CRF marginals) on UD-EWT test deployment parse: 0.8063 → 0.8064 = NULL at this config (UD-EWT
  is the tagger's home domain; GUM, where the tagger costs 0.064, not yet tested) — function kept, not wired. (b) Exposure-weighted
  category sweep DONE: 50k/k17 0.577, 50k/k34 0.693, 200k/k17 0.618, 200k/k34 0.684, 200k/k68 0.699, 1M/k34 0.645, **1M/k68 0.706**
  (token readout 0.678 @100% coverage); Mintz frames at 1M 0.410. The cluster COUNT is the lever; the reading budget saturates
  early at k=34 (the child's categories form from modest input). Final-code run (form classes + form cue) at 1M/k68 running.
  (c) Graded hand-offs in `labeled_pick` / `extract_entity_states` measured on the two regressed board dims: IDENTICAL at every
  threshold incl. OFF (0.8088 / 0.8148) → the graded branch is not on the scored path or the loss is in WRONG hard labels, not
  ABSENT ones — tracing the instruments' actual call path next.
- **TOP RUNG FINAL CONFIG (1M Simple-Wiki lines, k=68 + 2 orthographic form classes, exposure-weighted competitive learning,
  learned form cue for unknown words): type-level many-to-one 0.745 (majority 0.157, twin 0.481, V 0.592); token-level graded
  readout 0.722 at 100% coverage.** Per class: PRON .87, NOUN .85, DET .85, AUX .83, ADP .83, ADJ .80, VERB .78, PART .74,
  NUM .66, PROPN .54; ADV .05, CCONJ/SCONJ 0 ("and" ≈ comma; adverbs scatter). Prior attempt 0.323 → 0.745 by moving the
  operating point (exposure weighting, form classes, k), no labels anywhere. Supervised tagger 0.944 = the remaining gap.
- **Patient-consumer trace (instrument mirror, UD-EWT n=1255):** LIVE vs RAW labels: 1008 both right, 18 LIVE-only, 37 RAW-only,
  192 both wrong. 23 of the 37: the competition labelled the gold object `obj` AND a second post-verbal nominal `obj` (iobj folded
  into OBJ) and the consumer takes the first → added the IOBJ class + animacy + double-object cues: the double-labelling is gone
  but "saw him yesterday" now reads `him` as recipient (time adjuncts look like second objects by order) → the disambiguator is
  the VERB'S ARGUMENT FRAME (give/tell/show take recipients) — adding the frame cue from the reader's verb-frame knowledge.
- **Consumer regressions mostly REPAIRED UPSTREAM (more signal, not a revert), 2026-09-12 late:** (1) IOBJ class (recipient) with
  animacy + the verb's recipient propensity (`frame` cue: per-lemma iobj share accrued from the treebank counts; plastic form keeps
  accruing); (2) the two post-verbal cues merged into ONE slot coalition (`post_slot` = first/later × single/pair) — as separate
  cues their contrasts double-counted "second post-verbal nominal" and sent the PATIENT of "give me a call" to OTHER (12 examples
  printed). Held-out UD-EWT test gold heads: 0.9235 (OBJ 0.944, SUBJ 0.941, IOBJ 0.662). Instrument mirror (patient, n=1255):
  LIVE-only 23 vs RAW-only 27 (was 18 vs 37). **Board dims standalone: who_did_what_patient 0.8088 → 0.8207 (prev 0.8303);
  state 0.8148 → 0.8280 (prev 0.8333).** Residual: "saw him yesterday" reads `him` as recipient (a time noun looks like a second
  object by order) → a lexical TIME/measure class for the nominal is the next cue; 6 items where the object is labelled nsubj.
- **PLASTIC FORM of the role labeler's validities (owner: "the brain doesn't use anything frozen"):** the asset now carries the
  accrual COUNTS; strengths are a pure function of counts (`graded_role_assigner.strengths_from_counts`, the ONE implementation
  the offline learner also calls); `observe_role_outcome(toks,pos,heads,i,role)` accrues a confirmed comprehension outcome
  online and recomputes; `save_coarse_validities` persists the grown table. Verified: rebuilt == loaded (0.9235 unchanged);
  200 observations move P(IOBJ|"him" in "she saw him") 0.16 → 0.58; save/load round-trip exact. Witness 23/23. The OUTCOME
  source at read time (what confirms a role without gold) is the next design question — candidates: agreement/number checks,
  resolved-event consistency, the reader's own high-margin decisions (self-confirmation, to be measured for drift).
- **596-item decision with the FINAL labeler (IOBJ + animacy + frame + post-slot coalition; probe v13 re-run):** LIVE 0.4966 vs
  supervised 0.4698 = **+0.0268 CI95 [+0.0067, +0.0487]** (was +0.0235); gold heads +0.0201 [0.000, +0.042]; perceived-learned
  validities = identical decisions (tie, kept gold-learned); fallback-to-perceptron +0.0101 n.s. Witness 23/23 (incl. plasticity).
- **Why the closed classes score 0 (1M/k68 clusters inspected):** the induced clusters are coherent SUBSTITUTION classes coarser than
  UD's tagset — {of, and, in, for, as, on, by, with, from, or} = connectives (ADP 1685 / CCONJ 625 / SCONJ 137 → named ADP, so
  CCONJ recall 0); {that, can, but, when, because, if, will, would, however, while} = clause introducers + modals; {are, be, also,
  not, were, have, only, often, usually, now} = the auxiliary field incl. its adverbs; {the, a, an, its, each, every, X's} = DET
  (0.99 pure); {it, they, this, which, there, you, we} = PRON. Not a bug: the brain's categories are not UD's. Phase-diagram move:
  more clusters (k=136 run launched) or a within-cluster refinement by finer frames; the consumer-facing question is whether the
  parser/role rungs need UD's split at all (they read SUBJ/OBJ configurations, not CCONJ vs ADP).
- **HAND-OFF categories → heads (probe v15, the fully-BF chain re-run with the 1M categories; UD-EWT smoke slice 2.5k/150):**
  raw 70-way inventory → chain UAS **0.0115** (below its shuffled twin 0.118; v1 with 8k/k17 categories 0.034); the SAME categories
  collapsed to a 17-way inventory → **0.2083** (gold-POS-no-prior reference 0.2755; adjacent-right floor 0.290); UNK→gold tag changes
  nothing (0.004) → the loss is the INVENTORY SIZE at the hand-off: the reading-learned attachment scorer learns category-pair ×
  direction × distance statistics from 8k sentences and cannot estimate them over 70 categories. The top rung's signal is real
  (0.208 = 75% of gold-POS); the next rung's INPUT GRANULARITY and its READING BUDGET are the levers — not the categories' quality.
  BF fixes to test: (a) a coarse inventory from the same reading, no labels (1M/k17 run launched); (b) the scorer learns from the same
  million lines' induced-category sequences instead of 8k treebank sentences.
- 1M/k136 categories: 0.758 type / 0.728 token (SCONJ 0.55, ADV 0.26 now separate; CCONJ 0 — "and/or" stay with the prepositions).
- **FULL BOARD after the upstream repair (17:15Z, 1094 s): pooled AGG 0.6377 → 0.6395** (pre-switch 0.6408). who_did_what_patient
  0.8088 → 0.8207 (pre 0.8303), state 0.8148 → 0.8280 (pre 0.8333), patient_defer 0.9512 → 0.9611 (pre 0.9670); forward-half row
  0.5036 (pre-switch 0.4789); affected_entity 0.3884 (0.3874). Every other arm identical; per-dimension gate OK vs the previous run.
  **Instrument note:** the board's affected-entity POPULATION is defined by the LIVE undergoer labels (pronouns labelled obj /
  nsubj:pass): 777 → 851 → 708 items as the labeler changed (recipients "gave HIM" correctly left the undergoer set once IOBJ
  existed) — the rate held; the fixed-target probe v13 (596 gold items, +0.0268 CI-sep) is the clean comparison. Residual vs
  pre-switch: patient −0.0096, state −0.0053 — the remaining items are post-verbal SUBJECTS read as objects (×35, word order
  alone) and copular subjects under predicted heads/tags; both trace UP to the tagger/heads rungs.
- **Hand-off categories → heads, conclusion so far (probes v15/v16):** the reading-learned attachment scorer (SelfSupEM over category
  sequences) needs a SMALL set of the RIGHT functional classes: fine 70-way inventory → UAS 0.012–0.019 whether it learns from 8k
  treebank sentences or 8k/20k Simple-Wiki lines (more reading does NOT help); gold-NAMED collapse of the same clusters to 17 → 0.208
  (gold POS 0.276); a LABEL-FREE k=17 clustering → 0.126 = its twin (the merge destroys the syntactic distinctions). So the next
  build is a label-free COARSENING guided by the consumer: merge fine clusters where the merge does not hurt the attachment
  learner's own objective (joint category/attachment induction; the brain's coarse functional classes are defined by their
  syntactic behaviour, i.e. "functional naming" from the prior SOLVED). Two-level hand-down: fine clusters for lexical/role cues,
  the merged functional level for attachment.
- **Attachment learner, two probes (smoke slice 2.5k/150):** (a) base-rate backoff smoothing instead of flat +0.5 → NO change
  (k68 0.0111, k17 0.1214, gold 0.2755) — the collapse is not smoothing. (b) ROOT-CAUSE found: the learner's root prior is
  frequency-driven (+0.3 per non-initial token), so under the fine inventory the PUNCTUATION class (in every sentence) collects
  the most root mass (804 vs connectives 676) → the final period becomes the root and tokens hang off it (UAS 0.012 < twin).
  **Form-class constraint (punctuation / numerals cannot head or root — a mark is not a word; pre-lexical, label-free):**
  k68 0.012 → 0.036, k17 0.121 → 0.170, gold POS 0.2755 → 0.2960 (above the adjacent-right floor 0.290). The constraint helps
  every inventory; the fine inventory still needs its functional coarsening. `FormAwareEM` prototype in the probe log.
- **Consumer-guided coarsening (probe v17 smoke): merging fine clusters by their attachment-behaviour profile → K=17 UAS 0.088 =
  twin 0.084 → REFUTED at this config (the profiles come from the fine learner's own poor statistics — circular).** Decisive
  reframe: with GOLD categories the attachment learner reaches only 0.296 vs the adjacent-right floor 0.290 → **the heads rung's
  bottleneck is the attachment LEARNER, not the categories feeding it.** Owner (2026-09-12): punctuation carries serious signal
  that should be picked up elsewhere → in writing, punctuation = PROSODY (boundaries/closure; Kjelgaard & Speer 1999): it belongs
  in segmentation (already), the role competition's clause edge (pre_slot stops at PUNCT, already) and ATTACHMENT as a BOUNDARY
  cue (arcs rarely cross a prosodic boundary; closure before it) — never as a head. Next probe: a boundary penalty on arcs spanning
  punctuation, swept, label-free.
- **Punctuation as a PROSODIC BOUNDARY cue in the attachment learner (arcs spanning a mark penalised β per mark; marks never
  head):** monotone gain — gold POS 0.296 → 0.301 / 0.306 / 0.312 / **0.315** (β 0.5/1/2/4; floor 0.290); fine-70 0.036 → 0.058.
  Small but the right direction and label-free; β swept, not adopted. The attachment LEARNER stays the bottleneck of the heads
  rung (pri-11 / pri-2's full-scale reading-learned scorer with constructions reaches 0.46–0.48; this reduced config 0.30).
- **Probe v16 FINAL (attachment scorer learning from the same READING, category sequences of Simple-Wiki lines, UD-EWT test 700):**
  k68: 8k 0.019 / 20k 0.018 / 50k 0.018 (twin 0.098); k17: 8k 0.096 / 20k 0.088 / 50k 0.070 — MORE READING HURTS with both
  inventories → NEGATIVE: the reading budget is not the lever for this attachment learner (hard windowed co-occurrence + EM);
  the learner itself (its root prior, its lack of boundary/constructional structure) is. Consistent with pri-2's located negative.
- **Transfer set for the desktop created 2026-09-12 13:29–13:39 local: `C:\AI\hd-instrument_desktop_2026-09-12\`** (repo minus
  .venv 191.9 GB, git bundle, frozen requirements, Claude memory + session folders c--AI/d--AI, MIGRATION_README.md with next steps).
- **Full-scale cached reading-learned scorer (em_n11991, gold POS, UD-EWT test 700, floor 0.285): r2 plain 0.4626 → form-class
  constraint 0.4693 → + prosodic boundary β=4 0.4755; r0 0.4193 → 0.4421 → 0.4495.** Decode-time patches only; the constraints
  belong INSIDE the learner's E-step. Owner: understand what the organ should compute and how the brain separates signals
  optimally BEFORE building further → `notes/RESEARCH_attachment_organ_spec_2026-09-12.md` (the spec: cue competition + cue-based
  retrieval + keep-alternatives-alive = Matrix-Tree posterior; reliability weighting, decorrelation by conditioning, divisive
  normalisation, exact marginalisation, form knowledge as constraints; the cue table; every consumer's signal requirement; the
  build plan as an ARM of the Competition-Model organ, self-supervised soft counts from the tree posterior).
- **Attachment as CUE COMPETITION (probe v18, the spec's first build; smoke 1.5k/150):** unconditioned additive cues: taught by the
  teacher's tree posterior 0.406, self-taught 0.369 (drift) — the same double-counting failure as the v2 role table; with
  configuration-conditioned contrasts (config = category pair; locality/frame/form/boundary/agreement as within-config contrasts)
  + self-teaching anchored on the teacher: **r0 0.4386 = teacher 0.4382; r1 0.4443 (> teacher); shuffled-strength twin 0.032.**
  Decorrelation-by-conditioning is load-bearing for attachment too. Full-size run (6k/700) in progress; teacher there 0.4626,
  teacher + constraints 0.4755.
- **Heads → roles hand-off (probe v19, UD-EWT test, deployment tagger, live arc-factored head posterior):** role competition on
  the MAP head 0.8075 → marginalised over P(head) 0.8091 (supervised labeler 0.767); per class unchanged to 3 dp — right
  direction, small on UD-EWT; the spec predicts more on GUM (heads cost 0.083 there). To test on the 596 items next.
- **Owner (2026-09-12): "the brain hits .9+ on this right? We're pretty far behind."** Yes: readers attach >95% of words; supervised
  0.78 here (0.95 SOTA); our label-free chain 0.46–0.48. The gap, by size: (1) EXPERIENCE volume (12k sentences vs tens of
  millions of words — the category learner went 0.32 → 0.75 with scale); (2) a LEXICON of argument structure learned from reading
  (our frame cue is a sketch); (3) MEANING / plausibility feeding structure (the generative world model); (4) INCREMENTAL
  prediction with reanalysis (surprisal as the learning signal). The competition machinery itself now matches its teacher.
- **v18 FULL (6k/700): student r0 0.4715 > teacher 0.4626** — the cue competition with learned, configuration-conditioned
  strengths REPLACES the teacher's hand-authored Naseem prior (pw=3) and beats it; r1/r2 + twin pending. Next lever per the gap
  analysis: EXPERIENCE VOLUME (probe v20: the learner accrues from 20k / 60k Simple-Wiki sentences tagged by the substrate's tagger).
- **v18 FULL r1 (anchored self-teaching): 0.4801** — the attachment cue competition now beats the cached teacher (0.4626) AND the
  teacher + decode-time constraints (0.4755): the best label-free attachment in the substrate; twin pending. Lexical cue
  (head lemma × dependent class × direction) at 1.5k sentences: r0 0.4386 → 0.4185, r1 0.4443 → 0.4292 = too sparse at that
  volume (lever 2 needs lever 1 first); flag off; retest at 60k.
- **v18 FULL FINAL: r0 0.4715 → r1 0.4801 → r2 0.4834; shuffled-strength twin 0.0918** (teacher 0.4626; teacher + decode constraints
  0.4755; floor 0.285; supervised 0.782). Each anchored self-teaching round still improves. Landing gate (spec §7) pending: the
  prior-free-teacher bootstrap (running), one knowledge form + one lexicon, one organ one cue pass.
- **Owner: volume alone will not get us to 0.9 — what other levers?** Ordered by expected size × BF fit: (1) the LEARNING SIGNAL
  itself — prediction error (surprisal of the next word / of the situation) instead of a static co-occurrence teacher; BUT the
  pri-2 record already shows the text-only form route is near its field ceiling: the 0-EM scale curve was FLAT (0.428@2k → 0.478),
  EM peaks at round 2 then declines (DMV signature), online/Hebbian re-estimation 0.434 < 0.478, Klein-Manning text-only ceiling
  ~0.5; constructions lifted 0.478 → **0.514** (content 0.544). So the next jumps are not form-only: (2) MEANING feeding structure —
  a plausibility cue from the forward-prediction organ (`composed_hub_predictor.surprisal`: the dependent as an argument of the
  candidate verb) and, beyond it, the generative world model as the parse's outcome signal (predictive-coding loop closure);
  (3) the argument-structure LEXICON at scale (one grown asset); (4) CONSTRUCTIONS as cue coalitions in the competition (+0.036 in
  pri-2); (5) INCREMENTAL decode with reanalysis. First test: the plausibility cue inside the competition (available today).
- **Meaning cue (plausibility of the nominal as the candidate verb's argument, forward-prediction organ; smoke 1.5k/150):** r0 0.4386 →
  0.4393, r1 0.4443 → 0.4458 (+0.0015) — the organ covers few verbs (`has(verb)`) and only verb→nominal arcs: a small lever until
  the world model is richer; kept behind `--plaus`.
- **LANDING GATE 1 (prior-free bootstrap, full 6k/700): prior-free teacher 0.2722 (BELOW the adjacency floor 0.285) → competition
  student r0 0.3505** (+0.078, above the floor): the organ's own cues (locality, category pair, frame, form, boundary, agreement)
  recover structure from a knowledge-free start; r1/r2 pending. Transfer at 19 GB.
- **CONSTRUCTIONS as a coalition cue in the attachment competition (smoke 1.5k/150):** r0 0.4386 → 0.4558, r1 0.4443 → **0.4917**
  (twin 0.033) — the largest single gain of the day, as pri-2 predicted ("the path past the distributional ceiling is structure");
  the cue value = which item-based construction (verbarg / coord / npmod / clausal, the landed detectors) proposes the arc; its
  strength is LEARNED within the category-pair configuration, not hand-weighted. Full run + prior-free+constructions queued.
  Prior-free gate r1 0.3631 (rising).
- **LANDING GATE 1 FULL (prior-free bootstrap, 6k/700): teacher 0.2722 (< floor 0.285) → student r0 0.3505 → r1 0.3631 → r2 0.3751**
  (still rising); the organ's cues build structure from a knowledge-free start, but 0.11 below the prior-informed bootstrap
  (0.4834) — the hand-authored Naseem prior was carrying ~0.1 of the earlier number. Knowledge-free + constructions queued.
- **SEMANTIC BOOTSTRAPPING test (probe v21, smoke 1.5k/150) — VETTED NEGATIVE on the headline, useful residue:** meaning-only teacher
  (typed selectional association for verb→nominal arcs + locality + form; no treebank, no hand table) UAS 0.203, core-argument
  recall (verb→nsubj/obj/iobj/nsubj:pass) 0.364; the competition taught by it: UAS 0.361 / 0.369, core-arg recall **0.840**.
  CONTROL reproduces it from the wrong source: "every nominal → nearest verb" heuristic 0.837 (supervised parser 0.847; floor
  0.211; prior-informed co-occurrence teacher 0.571). → the 0.84 is LOCALITY, not meaning; head-verb identification is ~solved by
  proximity; the consumer-relevant losses sit in ROLES (the competition's job) and in the structure proximity cannot give (PP
  attachment, NP internals, clauses, coordination) = the CONSTRUCTIONS domain. Meaning as the outcome signal stays a hypothesis
  for PP/clausal disambiguation (Hindle-Rooth), not for core arguments.
- **Constructions full (6k/700): r0 0.4715 → 0.4941** with the coalition cue; r1/r2 pending. Transfer 29.5 GB.
- **Constructions coalition cue, FULL (6k/700): r0 0.4941 → r1 0.5228** — past pri-2's constructions-in-the-scorer 0.514 and the
  co-occurrence teacher 0.4626; the best label-free attachment in the substrate so far; r2 pending.
- **Volume (probe v20): 20k Simple-Wiki sentences (substrate tagger) r0 0.4688 / r1 0.4781 ≈ 6k UD sentences (0.4715 / 0.4801) —
  FLAT.** Confirms the pri-2 scale curve: more text does not move this learner; STRUCTURE does. 60k arm pending.
- **Constructions coalition cue FULL FINAL: r2 0.5303 (twin 0.089)** — 0.4626 → 0.5303 (+0.068) from the competition + learned
  conditioned strengths + the construction coalition; still rising per round. Knowledge-free + constructions run started.
- **Induced constructions v22, n-gram form (smoke 20k lines / 1.5k / 150): 509 schemas, student r0 0.4404 / r1 0.4501** vs no
  constructions 0.4386 / 0.4443 and hand-coded 0.4558 / 0.4917 → NEGATIVE at this form: frequent category n-grams are not
  constituents ("DET_ADJ_NOUN_ADP" headed by DET) so the substitution test is asked about the wrong units. Stronger brain version:
  find the UNITS first by statistical segmentation (Saffran: chunk boundaries where category transition probability dips), then
  heads by substitution — being built (v22 --boundary).
- **Induced constructions, segmentation-first form (v22 --boundary, τ=0.08, smoke):** only 45 units and they still straddle phrases
  ("NOUN_ADP_DET_ADJ_PROPN" headed by PROPN): category transition probabilities do NOT dip at phrase boundaries (NOUN→ADP, ADP→DET
  are frequent), so Saffran-style dips find no constituents at the category level. Infants get those boundaries from PROSODY,
  which text lacks beyond punctuation. → BOTH induced forms NEGATIVE as built; the four hand-written item-based schemas stay the
  coalition cue (they encode what prosody + meaning would teach). Remaining label-free route: constituency by SPAN SUBSTITUTABILITY
  (Clark 2001: a span is a unit if its external-context distribution is peaked / substitutable by one category), not dips.
- Segmentation-first induced constructions (smoke) final: r0 0.4422 / r1 0.4573 vs no constructions 0.4386 / 0.4443 and hand-written
  schemas 0.4558 / 0.4917 — a third of the hand-written gain; confirms the diagnosis (units are not constituents). Knowledge-free
  bootstrap + hand-written constructions (full): r0 0.3712 → r1 0.4227 (rising faster than without constructions); r2 pending.
- **LANDING GATE 1 FINAL (knowledge-free bootstrap + constructions, 6k/700): 0.2722 → 0.3712 → 0.4227 → 0.4316 (twin 0.085)**, still
  rising per round; prior-informed + constructions 0.5303. The hand-authored universal prior carries ~0.10; the BF organ's own
  learning has not converged (anchor α=0.5 on a weak teacher; 2 rounds). Next: more rounds + a lower anchor; then land the
  knowledge-free form (BF) with the gap documented, keep the prior OUT of the organ.
- **LANDED (organ code, 2026-09-12 evening): `hdlab/attachment_arm.py`** — the attachment arm of the Competition-Model organ (one cue
  pass per sentence; locality / category-pair config / frame / form / boundary / agreement / construction cues; strengths = one
  pure function of plastic soft counts; `observe_arc_outcome` / save; exact Matrix-Tree head posterior handed down; the four
  item-based constructions promoted from the experiments cells) + `tools/build_attachment_validities.py` (knowledge-free teacher +
  anchored self-teaching; --rounds/--alpha swept). Registry BF_SPIRIT. Asset build waits for the extended-rounds gate
  (--rounds 5 --alpha 0.8 running); the hand-authored prior stays OUT of the organ.
- **ERROR ANATOMY (UD-EWT test 700; supervised 0.7793 vs our teacher+constraints 0.4755; gap 0.30 by share):** punct 0.056 (ours 0.20),
  case 0.037 (0.48), nsubj 0.022, nmod 0.019, cop 0.017 (ours 0.03!), det 0.015, cc 0.015, flat 0.012, xcomp 0.011 (0.13), obl 0.011,
  conj 0.010, ccomp 0.009, amod/advmod/obj ~0.008 each, advcl 0.007 (0.02). By arc length: length-1 arcs carry 0.11 of the gap
  (sup 0.89 vs ours 0.59). → A THIRD of the gap is FUNCTION-WORD CONVENTION (punct/case/cop/det/cc/flat) = deterministic item-based
  frames (Mintz), NOT comprehension; the comprehension-relevant gap (nsubj/obj/obl/nmod/clausal) ≈ 0.10. Built `function_word_arcs`
  into the landed organ (ADP → its NP head; AUX → following verb; copula → following predicate; SCONJ/'to' → following verb; PROPN
  runs left-headed; punct → nearest verb); probe v18 now reads the organ's construction map.
- **Research drill 2 (`notes/RESEARCH_sota_parser_anatomy_and_glassbox_recovery_2026-09-12.md`):** SOTA = the labelled signal (~100 gold
  trees → 75–80 UAS; they buy CONVENTION); label-free ceiling 67.9–68.8 (sibling second-order = +13.3, the biggest label-free lever);
  per-failure label-free sources: unambiguous-case mining for PP (Ratnaparkhi 81.9%), parallelism-as-priming for coordination, frame
  occupancy for clausal; token-level categories. Learning-time mechanisms from drill 1 (delta+punct-hard+curriculum combined):
  r0 0.3463, r1 0.3953, r2 0.4004 vs plain knowledge-free 0.3712/0.4279/0.4368 → NOT helping as built (DMV-regime result; disentangle).
- **Second-order via valence OCCUPANCY (probe v18 --sibling):** the biggest published label-free lever is sibling factorisation
  (+13.3, Yang et al. 2020); our Matrix-Tree is first-order, so the brain-faithful approximation is a CUE: "how many dependents of this
  class on this side does the candidate head already have" under the previous pass's posterior (Lewis-Vasishth retrieval cue =
  valence occupancy; mean-field second order), learned like every other cue, two-pass decode. Smoke with constructions running.
- **Knowledge-free + constructions, 5 rounds, α=0.8 (student-heavy anchor): 0.3712 → 0.4279 → 0.4368 → 0.4361 → 0.4430 → 0.4495**
  (twin 0.067) — still creeping up at round 5; the fully knowledge-free organ is at ~0.45 before the function-word constructions.
- **Learning-time mechanisms combined (δ=0.6 in the E-step, hard punctuation segmentation in learning, short-sentence curriculum),
  knowledge-free + constructions, 3 rounds: 0.3463 → 0.3953 → 0.4004 → 0.3982 (twin 0.085) vs the plain path 0.3712 → 0.4279 →
  0.4368 → 0.4361 → NEGATIVE as built (−0.04).** The published +20.2 (Smith & Eisner) is a DMV generative-EM result; in a
  contrast-learned competition the learning-time length bias distorts the configuration counts the strengths are read from, and the
  hard segmentation removes the cross-punctuation arcs the constructions and the root decision need. Not re-tried as a bundle;
  if revisited, ONE mechanism at a time, and the length bias applied to the TEACHER's posterior only.
- **Occupancy (second-order mean-field) cue + constructions incl. function-word frames, smoke 1.5k/150: r0 0.4616, r1 0.4946 (twin
  0.036)** vs the earlier constructions-only smoke (four schemas, no fw, no sibling) 0.4558 / 0.4917 → +0.006 / +0.003 confounded
  between the two additions; control (fw constructions without the occupancy cue) running.
- **Control smoke (function-word frames as a LEARNED cue, no occupancy): r0 0.4662 / r1 0.5050** vs four schemas 0.4558 / 0.4917 →
  +0.013; knowledge-free full r0 0.3817 vs 0.3712 (+0.01). **Occupancy cue = NEGATIVE as built** (0.4946 with it vs 0.5050 without).
  **Volume FINAL (v20): 60k read sentences r0 0.4678 / r1 0.4599 (declining; twin 0.070) — CLOSED as a lever for this learner.**
  Why function-word frames recover so little of the anatomy's 0.10: their strengths are learned from a teacher that does not know
  where ADP/punct/cop attach → self-supervision cannot teach ANNOTATION CONVENTIONS (no raw-text statistic determines them; that is
  exactly what labelled trees buy). Design consequence: a separate, explicitly-labelled CONVENTION layer that applies the frames
  deterministically at decode for the UD metric, while the learned competition remains the comprehension organ (consumers read it).
- **CONVENTION layer (function-word frames applied deterministically at decode, --fw-force 5), smoke: r0 0.5172 / r1 0.5413 (twin
  0.052)** vs 0.4662 / 0.5050 with the frames as a learned cue only → +0.036: the convention share is recoverable, but only as a
  stated convention, not as learned knowledge. Decisive full run launched: knowledge-free bootstrap + learned constructions +
  convention layer (3 rounds). Owner: "these tasks have been running for a very long time" — the probes are unvectorised
  measurement loops (25–40 min per full run, worse when several run at once); sweeping stops here; the landed organ is the place for
  speed.
- **DECISIVE (landing) RUN — knowledge-free bootstrap + learned constructions + CONVENTION layer, 6k/700: 0.2722 → 0.4186 → 0.4737 →
  0.4826 → 0.4826 (converged; twin 0.158 — the convention layer alone yields arcs).** The fully BF organ (no hand prior; conventions
  stated as such) = **0.4826** vs the prior-informed co-occurrence teacher 0.4626, prior-informed + constructions 0.5303, supervised
  0.78, field label-free ceiling 0.68. Asset build with this configuration launched (`tools/build_attachment_validities.py`).
- **Asset built (`attachment_validities_v1.json`, 514 KB): organ 0.4792 (probe 0.4826). ANATOMY of the LANDED knowledge-free organ
  vs supervised (0.4825 vs 0.7793):** conventions largely recovered (case 0.743, cop 0.400, cc 0.440, punct 0.284) BUT the CORE
  collapsed: **obj 0.189** (prior-informed path 0.755), obl 0.118, nmod 0.188, root 0.413, nsubj 0.611, xcomp 0.256, ccomp 0.206,
  advcl 0.056. The knowledge-free teacher never learned that the VERB HEADS ITS ARGUMENTS (the witness: "dog" → root, "bitten" →
  "man"), so the 0.48 is conventions + NP internals while who-did-what-to-whom is wrong — worse for the consumers than the
  prior-informed 0.53. That is precisely the knowledge the hand-written universal table supplied, and the brain gets it from
  MEANING (the event predicate heads its participants; semantic bootstrapping). Next: the knowledge-free teacher + the MEANING
  teacher (probe v21: verb→nominal plausibility, root = the predicate with the most plausible arguments) as ONE teacher posterior.
- **Core-structure readout (smoke 1.5k/150), knowledge-free + constructions + convention layer: UAS 0.4594; obj 0.081, obl 0.037,
  nmod 0.304, root 0.34, nsubj 0.495, xcomp 0.047, ccomp 0.0; + MEANING teacher (β=2): UAS 0.4626; obj 0.13, obl 0.067, root 0.353.**
  The core stays broken in the knowledge-free regime (prior-informed path: obj 0.755): the co-occurrence teacher prefers noun→noun
  neighbours and the meaning bonus at β=2 is too weak against its log-probabilities. Sweeping β (5, 10).
- **SEMANTIC BOOTSTRAPPING RESTORES THE CORE (2026-09-12, smoke 1.5k/150, knowledge-free co-occurrence teacher + meaning teacher as
  ONE tree posterior, constructions + convention layer): β=5: UAS 0.5341, obj 0.715, obl 0.437, root 0.833, nsubj 0.648; β=10: UAS
  0.5399, obj 0.756, obl 0.556, root 0.793, nsubj 0.662, nmod 0.23 (vs β=0: 0.4594, obj 0.081, obl 0.037, root 0.34; β=2: 0.4626).**
  The smoke student at β=10 already exceeds the FULL prior-informed path (0.5303) that the hand-authored universal table bought — the
  head-direction knowledge the table supplied IS what meaning supplies (Pinker 1984/1989 semantic bootstrapping: the event predicate
  takes its participants as arguments, so the predicate word heads the participant words). A different BF method = a jump (+0.08 UAS,
  obj ×9), not a climb. REFUTED as built: a HARD GATE (nominal + verb dependents take the meaning teacher's column outright, other
  dependents the co-occurrence column, both column-normalised): UAS 0.523, obj 0.707, obl 0.489, root 0.827 but **nmod 0.104** —
  forcing nominals onto meaning+locality throws away noun→noun structure; the soft one-posterior sum wins. HONEST LABEL: the
  plausibility store (`typed_selectional_preference`, Resnik class association over the reading-grown selectional store) was
  EXTRACTED from simplewiki with a UD-shaped parse (extraction_report_v1: 737k sentences parsed) → the teacher is FOUNDATION-INFORMED,
  not knowledge-free; only verb–noun ASSOCIATION is read, never slot position; head direction comes from the bootstrapping account
  itself. Landed into the organ as `attachment_arm.SemanticBootstrapTeacher` + `tools/build_attachment_validities.py --beta`
  (default 10 = the swept operating point, never adopted from the brain). Full rebuild (6k, 3 anchored rounds, α 0.8) running.
  Ops note: detached launches (`( … ) &`, PowerShell Start-Process) die with exit 127 / silently on this laptop; the Bash tool's
  background mode is intermittent; a FOREGROUND run that exceeds the tool timeout is moved to background and keeps running — use that.
- **ASSET REBUILT WITH SEMANTIC BOOTSTRAPPING (2026-09-12 21:03; `tools/build_attachment_validities.py --beta 10 --eval`, 6k
  sentences, 3 anchored rounds α 0.8; commit 32191dbfb): organ on UD-EWT test 700, gold categories: UAS 0.4792 → 0.5573** (teacher
  alone 0.3156 — the student extracts the configuration statistics the teacher's own MAP parse does not show); per relation: root
  0.413 → 0.791, nsubj 0.611 → 0.709, obj 0.189 → 0.708, obl 0.118 → 0.453, nmod 0.188 → 0.283, xcomp 0.256 → 0.591, ccomp 0.206 →
  0.147 (↓), advcl 0.056 → 0.06, conj 0.236, case 0.743 → 0.735, punct 0.284 → 0.273. Witness 15/15 — the former known limit ('dog'
  → verb) is now an assertion. The comprehension core (who did what to whom) is RESTORED above the prior-informed path (0.5303) that
  the hand-authored table used to buy; remaining comprehension-relevant losses: obl/nmod (PP attachment — brief pri-17), ccomp/advcl
  (clausal complements need verb-frame occupancy — brief pri-16 sibling/occupancy), conj (parallelism). NEXT on the chain: hand the
  head posterior DOWN to the role competition (`graded_role_assigner.coarse_roles` reads heads) and re-measure the 596-item decision
  + the board (haiku runner) — a downstream dip is a consumer to repair, not a failure of the rung.
- **HEADS → ROLES HAND-OFF ON THE REBUILT ASSET (2026-09-12 21:10, probe v19 `--attachment-arm`, UD-EWT test 2077 sentences /
  8362 nominals, deployment tagger): role competition over the BF attachment arm's heads: hard head 0.7129, HEAD-MARGINALISED 0.7260
  (supervised labeler on the same heads 0.6891) vs over the supervised arc-parser heads: 0.8075 / 0.8091 / 0.767.** Expected dip
  (heads 0.557 vs 0.78 UAS) — NOT a failure of the rung: (i) the graded read now buys +0.013 (was +0.0016 on near-certain heads):
  the posterior carries signal the hard head drops, exactly the hand-off the spec asks for; (ii) our competition beats the supervised
  labeler on BF heads by +0.037 (it is the more robust consumer); (iii) per class on BF heads: SUBJ 0.750 (marg), OBJ 0.681, OBL
  0.725 (UP from 0.609 supervised-labeler), OTHER 0.736, PASS_SUBJ 0.602, BY_AGENT 0.556, IOBJ 0.62. Where the loss sits: OBJ 0.861
  → 0.681 and SUBJ 0.812 → 0.750 follow the heads rung's obj 0.708 / nsubj 0.709 — the repair is UPSTREAM (briefs pri-16/17) plus
  a consumer that reads P(head) rather than the MAP (marg > hard). Board A/B with `HDLAB_HEADS_SOURCE=attachment_arm` running.
  Ops: a RUNNER agent's background shell dies when the agent's turn ends — long runs must be launched from the main session's Bash
  (foreground → auto-moved to background) or the agent must block on them.
- **CATEGORIES → HEADS HAND-OFF MEASURED (2026-09-12 22:20; `tools/build_attachment_validities.py --categories`, 1.5k sentences,
  β=10, 3 rounds, UD-EWT test 700): reading-induced categories (type-level asset k=68+2, clusters NAMED by majority UPOS; agreement
  with UPOS on the test slice 0.7065) in place of UPOS → attachment arm UAS 0.4649 vs 0.5640 with UPOS on the SAME slice (−0.099).**
  Per relation (induced vs UPOS): root 0.611 vs 0.79, nsubj 0.523 vs 0.74, obj 0.502 vs 0.735, obl 0.344 vs 0.486, nmod 0.277 vs
  0.264 (=), xcomp 0.511 vs 0.533, ccomp 0.086 vs 0.112, advcl 0.052 vs 0.037, **conj 0.086 vs 0.24**, case 0.63 vs 0.737, punct 0.245
  vs 0.268. THE FIRST NUMBER FOR A CHAIN LEARNED FROM READING ALONE (categories from distribution + heads from co-occurrence + meaning):
  **0.465** (floor 0.285; supervised parser on supervised tags 0.78). WHERE THE TOP RUNG'S SIGNAL IS LOST, by consumer (§2e): (a) the
  PREDICATE class — unseen verbs fall to NOUN (type-level asset, 20k words, no form/suffix cue: 'barked' → NOUN) so the semantic
  teacher and verbarg construction miss them → root/nsubj/obj; (b) the CLOSED CLASSES — CCONJ merged with ADP ('because' → AUX) →
  the coord/clausal constructions cannot fire → conj 0.09; (c) case 0.63: ADP partly merged. nmod/advcl unaffected (already weak).
  This is pri-15's target, now with the hand-off number the brief asks for; the build tool's `--categories` is the test harness.
  Also: the UPOS reference on 1.5k sentences (0.5640) ≥ the 6k asset (0.5573) — volume flat for this learner (third confirmation).

- **SELF-GROWN PLAUSIBILITY STORE REPLACES THE PARSER-EXTRACTED ONE (2026-09-12 22:50; `tools/grow_selectional_store_bf.py`: induced
  categories -> attachment arm -> role competition over 60k simplewiki lines -> 891 verbs; typed asset
  `typed_selectional_preference_bf_v1.json`): heads-rung smoke UAS 0.5642 vs 0.5640 with the August UD-parsed store (737k
  sentences); root 0.793 / 0.79, nsubj 0.719 / 0.74, obj 0.71 / 0.735, obl 0.459 / 0.486, xcomp 0.606 / 0.533.** The teacher now
  defaults to the self-grown store (`attachment_arm.BF_TSP_ASSET`): the heads rung's LAST non-BF dependency is removed at no cost --
  structure and meaning co-develop from the substrate's own reading (semantic + syntactic bootstrapping as one loop). Full 6k rebuild
  with the self-grown store running (runner).
- **BOARD A/B, BF HEADS (hard read) -- `HDLAB_HEADS_SOURCE=attachment_arm`, traced run, exit 0 (22:45): AGG 0.6395 -> 0.6294; coref
  0.4681 =, common_noun 0.5671 =, salience 0.2555 =, who_did_what_agent 0.832 =, who_did_what_patient 0.8207 =, wic 0.7493 =,
  STATE 0.828 -> 0.5265 (floor 0.5714; CI-sep lost).** Two facts: (1) the who-did-what dimensions and coref are BYTE-IDENTICAL --
  their arms instantiate their own parser (exp_board_patient_slot_v1 / exp_board_agent_slot_ud_v1 / GUM coref) and never read the
  reader's shared parse, so the BF switch does not reach them: the chain is not yet end-to-end through the board (next wiring item:
  route those arms through `situation_reader._cached_parse_heads` / the same switch); (2) STATE broke on SHAPE, not content: the
  attachment arm builds the copular clause holder-headed ("dog" <- "big", "is" -> "big") where UD makes the predicate the head.
  CONSUMER REPAIR (commit a4670ae3f): `copular_binding.extract_entity_states` reads the holder either way (a copular predicate's own
  nominal head is the holder when no subject is labelled); default path byte-identical. Residual misses are heads-rung quality
  ("hot" under "yesterday"; "tall" under "hat" -- obl/nmod locality). State-dim A/B with the repair on a runner. The earlier silent
  exit-1 board run was not reproducible under tracing (exit 0, identical arms) -- environmental; recorded, not chased.
- **INTEGRATION 1 (owner-DONE pri-12, the lemmatizer): LANDED `hdlab/morphology.py` (glass-box morphy port, 0 divergences over 6.3M;
  Rastle-Davis/Taft/Pinker-Ullman dual-route computation) and repointed 13 read-path modules; witnesses green (morphology PASS, roles
  23/23, attachment 15/15; fused-sense/meaning-fusion/board self-test on a runner). NOT wired: the dual-route optimum (+0.023 on human
  gold; needs the lemma-keyed stores rebuilt first) and the solver's BF POS prototype (count-based generative tagger, graded
  posterior; acquisition supervised) -- the latter handed to pri-15 as the INFERENCE half for token-level readout over induced classes.

- **STATE DIM REPAIRED UNDER BF HEADS (2026-09-12 23:05): `copular_binding.robust_cop` made DIRECTION-AGNOSTIC (the copula is a
  closed-class linker between two content words: the tree says which word it is bound to, linear order says which is the
  predicate (after) and which the holder (before; after in inverted questions) -- UD's predicate-headed shape and the attachment
  arm's holder-headed shape are the same content) + the extractor's holder = the predicate's own nominal head when no subject
  is labelled. STATE dim, BF heads: 0.5265 -> 0.6561 (floor 0.5714; CI-sep over the floor restored: [0.048, 0.124]); supervised
  path 0.828 (was 0.8307; the inversion fallback moves one item). Diagnostic (378 gold pairs): supervised heads pair-ok 315 /
  pred-only 14 / holder-only 18 / none 31; BF heads pair-ok 247 / holder-ok-pred-wrong 54 / pred-ok-holder-wrong 24 / none 53 -->
  the residual is the heads rung misplacing the COPULAR PREDICATE (copula bound to the wrong content word) -- a heads-rung item
  (convention layer: AUX -> the predicate content word), not the consumer.**
- **GRADED BOARD A/B (BF heads + role posterior) = identical to the hard read (AGG 0.6294, STATE 0.5265 before the repair):** the
  graded heads->roles hand-off is INERT on the board because the who-did-what / coref arms instantiate their own parser and never
  read the reader's parse; the hand-off shows only on the UD-EWT role probe (+0.013). Wiring item stands.
- **CATEGORY ORGAN LANDED LIVE (2026-09-12 23:15, owner: "take the step even if it causes short-term pain"): `hdlab/lexical_categories.py`
  -- the owner-DONE pri-12 solver's BF POS prototype (count-based generative model: lexical + suffix + transition COUNTS, settled by
  forward-backward into a per-token POSTERIOR; plastic `observe`; save/load) is the reader's DEFAULT tagger (`HDLAB_TAG_SOURCE=
  perceptron` restores the NOT_BF max-margin stand-in). UD-EWT test 25,094 tokens: 0.9120 vs perceptron 0.9445 (-3.3 points), same
  speed (1.4 ms/sentence); unknown words by suffix ('barked' -> VERB 0.99). The posterior is cached (`_cached_tag_posterior`) for the
  graded hand-off to the heads rung (next). Inventory/counts = offline labelled supply until pri-15's induced classes replace them
  (same organ, `accrue` over any (word, class) stream). Board A/B running: counts alone; counts + attachment-arm heads (the fully
  BF-inference chain). Witness test_lexical_categories 7/7; roles 23/23; attachment 15/15.
