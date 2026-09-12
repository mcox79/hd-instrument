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
