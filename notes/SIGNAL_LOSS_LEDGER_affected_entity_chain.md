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
| 5 | Grammatical roles / heads (the parse) | the brain's parse is graded, acquired from reading; roles feed binding + parallelism + targets | `pos_tagger` + `arc_parser` + `arc_labeler` (supervised averaged perceptrons) | **NOT_BF** (5 organs; declared scaffold) | gold roles 0.5403 → predicted 0.4789 = **−0.061** on the decision; decomposition into POS / heads / labels TO MEASURE (probe v11); reading-learned acquisition exists (fully-BF chain 0.4057 UAS, pri-11 wiring brief) | cell (gold vs predicted) |
| 6 | Tokenisation / sentence segmentation | — | CoNLL gold tokens (GUM) | n/a here | 0 on this instrument (gold tokens) | — |

## Order of the upstream pass (by measured loss × BF status)
1. **Rung 5, the parse spine (−0.061, NOT_BF):** measure the per-component loss (POS / heads / labels) on THIS decision (probe v11);
   then route the decision's role inputs through the reading-learned graded parser (`pri-11` brief: register-general second track)
   and measure the recovered fraction. This is the first lossy non-BF rung and the owner's named target.
2. **Rung 2, the prior's operating point:** DONE (v10) — at optimum; nothing to change.
3. **Rung 4, the mention source:** count the 62 unreachable items by cause (cataphora / abstract referent / missed NP head).
4. **Rung 3, entity tokens:** coordinate with the coref two-half line (oracle +0.091).
5. **Rung 1, the event expectation:** build the JOINT store from our own parsed events only after rungs 5/2/4 are BF — its input
   (roles, tokens) must be lossless first, or its measured value is a lie.
