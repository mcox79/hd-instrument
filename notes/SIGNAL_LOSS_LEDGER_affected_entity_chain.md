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
| 6 | Tokenisation / sentence segmentation | — | CoNLL gold tokens (GUM) | n/a here | 0 on this instrument (gold tokens) | — |

## Order of the upstream pass (by measured loss × BF status)
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
