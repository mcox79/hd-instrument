---
problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain
status: PARTIAL
bar: "Beats the LIVE incumbent CI-separated on the MODERN GUM he/she pronoun-pick population (n~1240; the incumbent ~0.503 recomputed on the SAME population + scorer as the hybrid), with (a) the info-free TWIN ... LOSING CI-separated ... (b) NO-regress on NAMED coref ... A rigorous NEGATIVE is a FULL PASS (e.g. 'the hybrid TIES the live incumbent, Delta within CI of 0, because the generic-suppress + agreement-narrow pool already prunes exactly the fragments the unification merges -- the merged cross-type history is redundant with the tuned graded retrieval on this population; the unification value is SUBSUMED by the live pool ... keep hdlab/unified_referent.py correctly DEFAULT-OFF')."
result: "TWO findings on MODERN gold (GUM V12.1.0, 137-doc TEST, n=1240 he/she anaphoric targets; primary scorer = last-nominal-mention identity, which is size-robust and == the live reader's head_to_cluster on the fragmented arm). (1) LOCATED NEGATIVE (the brief's compose mechanism): the HYBRID (unified pool -> incumbent graded_antecedent_pick + suppression pool) scores 0.4750 vs the LIVE incumbent 0.5032, delta -0.0282 CI[-0.123,+0.056] -- does NOT beat the incumbent; the shuffled-grouping twin LOSES (0.3556, hybrid-twin +0.119 CI-sep, so the merges ARE real signal); ORACLE (perfect gold-cluster unification) also fails (0.4661 vs 0.5032); no ACT-R decay d in {2..6} recovers it. Unification MONOTONICALLY helps the weak isolation scorer (frag 0.3411 -> uni 0.3935 -> oracle 0.4065) but HURTS the strong incumbent scorer (frag 0.5032 -> uni 0.4750 -> oracle 0.4661): the two systems are ANTAGONISTIC on this population, so keep hdlab/unified_referent.py DEFAULT-OFF. (2) LIVE GAIN via a DIFFERENT lever: the brief ASSUMED person-feature exclusion is in the incumbent pool, but graded_coref_pick.phi_agreement_keep is LANDED-but-DORMANT (never called by _graded_pool_pick). Wiring it into the ACTUAL EventCentralityReader lifts the live he/she coref (native head_to_cluster) 0.5032 -> 0.5419, PAIRED doc-bootstrap delta +0.0387 CI[+0.0115,+0.0745] CI-SEPARATED; the random-drop twin (drop the same COUNT at random) LOSES (0.4637, phi-twin +0.0815 CI-sep) so it removes person-feature POLLUTION not pool size; named-antecedent no-regress (it RISES +0.036)."
floor: "The strongest floor actually run, recomputed on the SAME he/she GUM TEST population + the SAME primary scorer as each comparison: for the compose question, the LIVE incumbent = 0.5032 (native head_to_cluster; identical under the size-robust last-nominal scorer since the incumbent pool is fragmented); the hybrid does NOT clear it. Info-free floors: shuffled-grouping twin 0.3556, fragmented-x-isolation 0.3411. For the phi live-gain, the floor is the same LIVE incumbent 0.5032; phi clears it +0.0387 CI-sep. Perfect-unification ceiling under the incumbent scorer = oracle 0.4661 (BELOW the incumbent -- subsumption)."
controls: "COMPOSE negative: (1) pool x scorer 2x2 on ONE population, identical scorer machinery per cell -- isolates the pool-representation factor; (2) info-free TWIN = shuffled unified grouping (same #entities + size shape), LOSES CI-sep -> the grouping is load-bearing, the negative is subsumption not 'any re-keying'; (3) ORACLE = perfect gold-cluster unification fed to the incumbent scorer -> STILL loses -> the ceiling is SUBSUMPTION, not clustering quality (excludes 'better upstream clustering would fix it'); (4) phase-diagram d-sweep {2.0..6.0} dev-tuned/test-reported -> no decay recovers (excludes 'a tuning gap'); (5) NO-regress named subset; (6) POSITIVE control on the fragmented-protagonist subset (name variants that split the surface-head pool) -> hybrid still does NOT beat the incumbent there. PHI gain: (7) random-drop info-free twin (same drop COUNT, random which) LOSES CI-sep -> pollution-removal not pool-shrink; (8) named-antecedent no-regress (RISES); (9) the gain reproduces on the ACTUAL EventCentralityReader (native scorer), not only the reimplementation. FAITHFULNESS: the 2x2 arms reproduce the live substrate EXACTLY -- fragmented x incumbent == real EventCentralityReader (0.5342 slice / 0.5032 full, byte-exact) and unified x isolation == real resolve_unified_stream (0.4868 slice)."
files_changed: "experiments/exp_hybrid_unified_incumbent_coref_gum_v1.py, experiments/exp_person_feature_coref_optimize_gum_v1.py, experiments/exp_coref_ceiling_drill_gum_v1.py, experiments/exp_coref_gender_suppress_gum_v1.py, verification/test_hybrid_unified_incumbent_coref.py, verification/test_person_feature_coref_optimize.py, verification/test_coref_ceiling_drill.py, verification/test_coref_gender_suppress.py, notes/problems/compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain/SOLVED.md. NO hdlab/ writes (Q111 -- proposed wires stated below). Reuses data/corpora/gum/ (already on disk, pinned V12.1.0)."
reverify: ".venv/Scripts/python.exe verification/test_hybrid_unified_incumbent_coref.py  (11/11)  AND  .venv/Scripts/python.exe verification/test_person_feature_coref_optimize.py  (6/6)  AND  .venv/Scripts/python.exe verification/test_coref_ceiling_drill.py  (6/6)  AND  .venv/Scripts/python.exe verification/test_coref_gender_suppress.py  (6/6; the CUMULATIVE +0.082 upgrade ladder vs the live incumbent)"
---

# SOLVED (PARTIAL) -- compose the unified referent with the incumbent graded-pick pool

**STATUS: PARTIAL** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- the mechanism is proved in `experiments/` + `verification/`; the two Q111 wires are proposed, not landed.

Two results, both on modern GUM he/she (n=1240), both fully controlled:
1. **The brief's COMPOSE mechanism is a rigorous LOCATED NEGATIVE** (a full pass per the bar): feeding the unified
   referent to the incumbent scorer does NOT beat the live incumbent -- it is *subsumed and mildly antagonized* by the
   tuned pool. Keep `hdlab/unified_referent.py` correctly DEFAULT-OFF.
2. **The underlying goal -- a live coref gain on modern gold -- IS delivered by a DIFFERENT brain-foundational lever the
   brief mis-attributed:** the person-feature filter `graded_coref_pick.phi_agreement_keep` is LANDED but DORMANT; wiring
   it into the live pick lifts the incumbent **+0.0387 CI-separated** (0.5032 -> 0.5419 on the real reader). This is the
   "solve the real problem underneath the brief, a different way" the operating protocol asks for.

## What the disk said that the brief did not (verified first-hand)
- **The audit numbers reproduce EXACTLY.** Running the actual `EventCentralityReader(graded_pick=True)` and the actual
  `resolve_unified_stream` on the GUM TEST he/she population (via the landing witness's `_gum_to_live` bridge) gives the
  incumbent **0.5032** and the port **0.4331/0.4339**, n=1240 -- the brief's / audit sec-2b numbers hold.
- **The brief's PINNED claim "the incumbent's pool machinery includes person-feature exclusion
  (`graded_coref_pick.phi_agreement_keep`)" is WRONG on disk.** `grep` confirms `_graded_pool_pick` (and
  `event_centrality_coref` / `situation_reader`) never call `phi_agreement_keep` / `keep_after_pool_cleanup` /
  `is_discourse_participant`. The live incumbent pool is generic-suppress + agreement-narrow ONLY. The person-feature
  organ is landed-but-dormant. **This mis-attribution is the whole opening for the live gain** (finding #2).
- **The two coref paths are mutually-exclusive early-returns** (enumerated, not searched): in
  `event_centrality_coref.resolve_stream`, `if self.unified_referent: return resolve_unified_stream(...)` (L238-242, the
  SWAP) ELSE the `graded_pick` pool path -- NO path feeds unified referents THROUGH `_graded_pool_pick`. That absence is
  what this problem builds.

## How the brain does this (the frame)
- **PINNED -- the MEMORY:** Heim(1982)/Kamp DRT file-change referent (one card per entity, updated by every mention).
- **PINNED -- the RETRIEVAL:** Lewis & Vasishth(2005)/McElree ACT-R graded cue-based competition (recency x Cf-prominence
  x frequency; base-level activation `A = ln(sum w(role)*dt^-d)`), read out by a softmax = the incumbent
  `graded_antecedent_pick` (TUNED_WEIGHTS, d=3.0).
- **PINNED -- the pool machinery is ALSO brain-foundational:** generic-distractor suppression (a pronoun does not compete a
  non-referential "a man"), phi-feature agreement (agreement-narrow), and **person-feature exclusion** (a 1st/2nd-person
  SPEAKER is never a 3rd-person referent; Benveniste 1966) -- the last being the dormant one.
- **The brief's hypothesis:** these compose (the file card feeds the strong retrieval its correct input). **Measured
  result: on this population they are ANTAGONISTIC, not complementary** -- see the 2x2.

## Finding 1 -- the COMPOSE is a located negative (the pool x scorer 2x2)
Built a faithful 2x2 harness (`exp_hybrid_unified_incumbent_coref_gum_v1.py`) reusing the *actual* hdlab pick primitives
(`graded_antecedent_pick`, `GenericDistractorFilter`, `SceneProtagonistReader._agreement_narrow`,
`salience_binder.actr_activation`, `EntityAliaser`, `state_of_mind.compatible`). **The self-test asserts the arms
reproduce the live substrate EXACTLY** (fragmented x incumbent == real `EventCentralityReader`; unified x isolation ==
real `resolve_unified_stream`) -- so the harness is a byte-faithful stand-in and the hybrid cell is a true composition.

Primary scorer = **last-nominal-mention identity** (the concrete antecedent's gold cluster). It is size-robust (immune to
the merged-group inflation that makes dominant-cluster scoring reward big random groups) and equals the live reader's
`head_to_cluster` on the fragmented arm, so it reproduces the incumbent anchor 0.5032.

| POOL \ SCORER | incumbent (suppress + narrow + graded d=3.0) | isolation (recall-safe, no-suppress, ACT-R d=2.0) |
|---|---|---|
| **fragmented** (surface-head, the live overlay) | **0.5032  (= LIVE incumbent, floor)** | 0.3411 |
| **unified** (EntityAliaser + file-change writeback) | **0.4750  (HYBRID)** | 0.3935  (= PORT) |
| **oracle** (perfect gold-cluster unification) | 0.4661 | 0.4065 |

- **HEADLINE: hybrid 0.4750 vs incumbent 0.5032, delta -0.0282 CI[-0.123,+0.056] -- does NOT beat the incumbent.**
- **TWIN (shuffled unified grouping) LOSES:** 0.3556, hybrid-twin +0.119 CI[+0.029,+0.200] CI-sep. So the real merges ARE
  load-bearing signal (the negative is *subsumption*, not "any re-keying beats the incumbent").
- **SUBSUMPTION, not a clustering gap:** even ORACLE (perfect gold-cluster) unification -> incumbent = 0.4661, STILL below
  0.5032. Making the upstream clustering *perfect* does not rescue the composition -- so this is NOT an upstream-fidelity
  gap to build across; the incumbent's tuned pool already captures the lever.
- **MONOTONE ANTAGONISM:** unification HELPS the weak isolation scorer (0.3411 -> 0.3935 -> 0.4065) but HURTS the strong
  incumbent scorer (0.5032 -> 0.4750 -> 0.4661). **Mechanism:** merging inflates the protagonist card's ACT-R base-level
  activation (more mentions -> higher `A`), so the recency-dominated graded pick over-commits to the merged protagonist
  and LOSES the local-recency discrimination that GUM (modern, less protagonist-dominated than 19c novels) needs; and the
  incumbent's generic-suppression already prunes the junk fragments unification would consolidate, so there is nothing
  left for the merge to add.
- **Phase diagram swept:** the ACT-R decay d is free to move; dev-tuning it for the hybrid over {2.0..6.0} tops out at
  d=3.5 -> TEST 0.4734, still below 0.5032. Not a tuning gap.
- **Positive control (fragmented-protagonist subset, n=957 where name variants split the surface-head pool):** the hybrid
  STILL does not beat the incumbent there (0.5089 vs 0.5308) -- even where unification should pay off most.

This is exactly the negative the bar names as a full pass: *the unification value is SUBSUMED by the live pool; keep
`hdlab/unified_referent.py` DEFAULT-OFF.* And it REFUTES the brief's premise that the two systems are "complementary" on
this population -- they are antagonistic under the strong scorer.

## Finding 2 -- the live coref gain (wire the DORMANT person-feature filter)
Refuting the compose is the halfway point. The underlying goal is *a live coref gain on modern GUM he/she*. The disk
handed it to me: `phi_agreement_keep` (person-feature exclusion) is landed but never wired into `_graded_pool_pick`.
Wiring it -- proven on the ACTUAL `EventCentralityReader` (subclass injecting the filter as a pool pre-filter, native
head_to_cluster scorer, n=1240):

| arm | live he/she coref (native) | delta vs incumbent |
|---|---|---|
| **LIVE incumbent** | **0.5032** | -- |
| **+ person-feature filter (phi)** | **0.5419** | **+0.0387 CI[+0.0115,+0.0745] CI-SEP** |
| random-drop twin (same COUNT, random which) | 0.4637 | LOSES (phi-twin +0.0815 CI-sep) |

- **CI-separated live gain** on modern gold, brain-foundational (person-feature agreement: a first-person speaker is never
  a third-person referent), from activating a landed-but-dormant organ.
- **The random-drop twin LOSES** -> the gain is removing person-feature POLLUTION (1st/2nd-person "I"/"we" candidates that
  `compatible()` wrongly admits for a he/she), not shrinking the pool. GUM is heavy with first-person genres
  (interviews / vlogs / reddit) where this pollution bites, which is why the dormant filter matters more on modern
  multi-genre gold than the 19c novels it was measured on (+0.022 on LitBank).
- **No-regress on the named subset** (it RISES +0.036). Composing phi with the unified pool does NOT help further
  (hybrid+phi 0.5282 < incumbent+phi 0.5452) -- unification stays antagonistic even after cleaning the pool.

## Finding 2b -- the phi gain PROTOTYPED + OPTIMIZED + hardened (the "excel and exceed" pass)
`exp_person_feature_coref_optimize_gum_v1.py` prototypes the wire on the ACTUAL `EventCentralityReader`
(subclass injecting the filter as a pool pre-filter in `_graded_pool_pick`; `filter=off` is byte-identical to
the live reader, asserted) and optimizes it. Witness `test_person_feature_coref_optimize.py` **6/6**.

| filter (in _graded_pool_pick) | live he/she coref (native) | delta vs live incumbent |
|---|---|---|
| off (= live incumbent) | 0.5032 | -- |
| **tier1** (participant-only, recall-safe) | **0.5419** | **+0.0387 CI[+0.012,+0.075] CI-SEP** |
| tier2 (+ animacy-from-gender) | 0.5419 | +0.0387 (**identical -> animacy is REDUNDANT with gender agreement on he/she**, confirming the reference) |
| cleanup (older `keep_after_pool_cleanup`) | 0.5419 | +0.0387 (identical to tier1 on this population) |
| random-drop twin (same COUNT) | 0.4935 | -0.0097 (does NOT beat off) |

- **Deployable choice = TIER1** (the simplest recall-safe `phi_agreement_keep`, animacy all-None). TIER2 adds
  nothing because the pool reaching a he/she pick has no confirmed-inanimate candidate (gender agreement already
  excludes neuter) -- a clean confirmation of the reference's "animacy redundant with English gender".
- **MECHANISM PROOF (excel):** the gain concentrates exactly where speaker pollution lives. **First-person genres
  (conversation/interview/vlog/reddit/podcast/letter/speech) gain +0.0906 CI[+0.012,+0.168] (n=342); third-person
  genres gain +0.0189 CI[+0.002,+0.045] (n=898)** -- a ~5x concentration, both above zero but far larger where the
  narrator/speaker is a discourse participant. Top per-genre gains: conversation +0.142, letter +0.129, speech
  +0.100, vlog +0.067 (all first-person) + whow +0.300 / court +0.063 (2nd-person imperative / 1st-person testimony
  pollution). This is the brain-foundational prediction (a first-person speaker is never a 3rd-person referent) borne
  out genre-by-genre.
- **NO-REGRESS + it GROWS with distance:** by antecedent-distance bucket the delta is +0.027 (same) / +0.037 (+1) /
  +0.091 (+2) / +0.106 (long) -- no bucket regresses, and the gain rises with distance (more candidates accumulate,
  so pollution bites harder). Recall-safe by construction (a speaker is never the gold he/she antecedent, so dropping
  it cannot remove a correct answer) -- confirmed: the filter never regresses on any slice.

## Finding 3 -- the residual he/she ceiling DRILLED (where the remaining ~46% error lives)
`exp_coref_ceiling_drill_gum_v1.py` (witness `test_coref_ceiling_drill.py` **6/6**) decomposes the miss mass
of the live incumbent+phi path (n=1240), asking the discipline's question -- *could the pick have succeeded?*

| quantity | value | meaning |
|---|---|---|
| accuracy | 0.5419 | -- |
| **recall@compatible** | **0.9677** | the gold antecedent IS in the gn-compatible pool 97% of the time -- **reachable** |
| recall@pool (after all filters) | 0.6839 | only 68% survive the pool filters |
| pick@reachable | 0.7925 | of the reachable, the graded pick gets 79% right (a STRONG pick) |

**Miss-mass decomposition (0.4581):** upstream-unreachable **0.0323** | **filter-over-removal 0.2839** |
reachable-but-mispicked 0.1419. **The dominant wall is HARD-FILTER OVER-REMOVAL of the gold antecedent, NOT
world-knowledge** (only 3.2% is truly unreachable) -- this CONTRADICTS the reference's "residual is
individuation + world-knowledge" claim *for the live path* (disk outranks). Per-filter recall drop:
generic-suppress **0.1226**, agreement-narrow **0.1460**, person-phi 0.0153. **100% of the agreement-narrow
over-removals are GENDER-UNKNOWN gold entities** -- the exact mechanism: the hard narrow (keep known-gender
when any exists) drops a gender-unknown correct antecedent whenever a known-gender distractor is present. Of
the remaining mispicks, 40% face >=2 known-same-gender candidates (genuine ambiguity, the irreducible core).

**Two upgrades tested on top of phi (measured on the faithful reimplementation, == the live reader):**
- **UPGRADE A (ready): apply agreement-narrow to `him` too.** The live narrow fires only on the
  nominative/possessive slot (TOPICAL_SLOT_HEADS = he/she/his/her/hers); `him` (the object-pronoun adaptive
  path) is skipped. Agreement is a GENERAL constraint (Carminati 2002), not slot-specific. Adding it lifts the
  him subset **0.4118 -> 0.5882 (+0.176, n=102)** and the whole population **0.5419 -> 0.5548, +0.0129
  CI[+0.006,+0.021] CI-sep**. Stacks on phi (0.5032 -> +phi 0.5419 -> +him-narrow 0.5548).
- **UPGRADE B (a located negative -- do NOT do the naive thing): dropping the hard narrow HURTS
  (0.5419 -> 0.5056, -0.036).** Making agreement "graded/recall-safe" by removing the hard narrow floods the
  pool with gender-unknown distractors more than it recovers gender-unknown gold -- confirming the strengthen
  SOLVED's soft-agreement regression, *even after phi cleans the participant pollution*. So the brain-faithful
  fix for the 15% over-removal is NOT soft agreement; it is **better upstream GENDER INFERENCE** (make the
  gender-unknown gold gender-KNOWN so it survives the narrow correctly) -- a filed follow-on, not a knob here.

## Finding 4 -- the CUMULATIVE brain-foundational upgrade ladder (+0.082 CI-sep, the headline deliverable)
`exp_coref_gender_suppress_gum_v1.py` (witness `test_coref_gender_suppress.py` **6/6**) drills the last two
hard filters and assembles the stack. THREE stacking, CI-separated, brain-foundational upgrades -- all from
activating/fixing EXISTING machinery (no new organ, no gold, no LLM):

| rung | live he/she coref | cumulative delta |
|---|---|---|
| LIVE incumbent | 0.5032 | -- |
| + person-feature filter (phi, dormant organ) | 0.5419 | +0.0387 |
| + agreement-narrow on `him` (agreement is general) | 0.5581 | +0.0548 CI[+0.041,+0.069] |
| **+ soften generic-suppress (drop the never-subject STRUCT proxy)** | **0.5855** | **+0.0823 CI[+0.066,+0.098] CI-SEP** |

- **Soften-suppress = the third upgrade (+0.0274 CI-sep on top of phi+him).** Generic-suppress OVER-FIRES on
  modern GUM: it removed the gold antecedent in 152 cases, of which **147 (97%) were plain COMMON NOUNS** (real
  referents like "the woman"/"the teacher"), only 5 were actual quantifier junk. The structural never-subject
  proxy for referentiality is calibrated for 19c narrative and over-suppresses real common-noun antecedents on
  modern multi-genre text. **Fix: keep the quantifier (nonref) sub-test, drop the STRUCT sub-test** (use_struct=False).
- **The full stack is +0.082 = a 16% relative lift over the live incumbent on modern gold**, CI-separated, every
  rung recall-safe / register-fidelity, no new organ.
- **Gender inference (glass-box natural-gender cues -- titles/kinship) is a PARTIAL located lever, NOT CI-sep
  (+0.010).** It recovers reachability (recall@final 0.677 -> 0.740) but does not convert to accuracy CI-sep --
  the recovered gold re-enters the pool and still loses the graded competition (limited cue set + same-gender
  ambiguity). The info-free random-gender control HURTS (-0.052), confirming it is the RIGHT gender doing the
  (modest) work, not "any gender narrows the pool". A RICHER gender organ (occupational nouns, a name-gender model,
  confidence-gated coreferent propagation) is the real upstream fix -- a filed follow-on, quantified here.

## PROPOSED hdlab WIRES (Q111 -- STRATEGY lands them; solver is scope-barred from hdlab/)
> I cannot land these. Reference implementations: `exp_hybrid_unified_incumbent_coref_gum_v1.py`
> (`resolve_arm`, the `_PhiReader` subclass in `real_reader_phi_gain`).

1. **LAND THE PHI GAIN (the actionable win -- prototyped on the real reader, optimized, hardened).** In
   `hdlab/event_centrality_coref.EventCentralityReader._graded_pool_pick`, apply
   `graded_coref_pick.phi_agreement_keep(pronoun_low, prior_mention_heads, animacy=None)` as a **pool pre-filter** before
   `graded_antecedent_pick` (TIER1, animacy all-None = recall-safe, never empties the pool). It needs the pronoun's
   surface form and each candidate's prior mention-head list -- thread a `midx -> head` map through `resolve_stream`
   (already builds `midx_to_role` the same way). Reference implementation: the `CleanReader` subclass in
   `exp_person_feature_coref_optimize_gum_v1.py` (`filter=off` is byte-identical to the live reader; `filter=tier1` is the
   wire). **Measured live gain +0.0387 CI[+0.012,+0.075] CI-sep on modern GUM he/she (native scorer); random-drop twin
   loses; named no-regress; no distance-bucket regresses; +0.091 in first-person genres.** Use TIER1 (TIER2 animacy is
   redundant with gender agreement; `keep_after_pool_cleanup` is equivalent). Put it behind a `phi_person_filter` flag;
   per no-more-default-off, default-ON is justified (CI-sep win + recall-safe + no-regress). This is a **dormant-organ
   activation**, not a new organ. TIER2 with a REAL animacy signal (NER person/place, not gender) is a future extension
   (adjacent below), not needed for this gain.
1b. **APPLY agreement-narrow to `him` too (a small stacking upgrade).** In
   `event_centrality_coref.resolve_stream`, `him` takes the adaptive path and never gets `_agreement_narrow`.
   Add `him` to the slots that narrow (or narrow in the adaptive path). Measured +0.0129 CI-sep on top of phi
   (+0.176 on the him subset). Brain-foundational: gender agreement is a general violable constraint, not
   specific to the subject/possessive slot. Land it WITH the phi filter.
1c. **SOFTEN generic-suppress (drop the never-subject STRUCT proxy; keep the quantifier NONREF sub-test).** In
   `event_centrality_coref.resolve_stream` the pool is built with `GenericDistractorFilter(..., use_struct=True)`;
   set **`use_struct=False`** (keep `use_nonref=True`). Measured +0.0274 CI-sep on top of phi+him-narrow; 97% of
   its over-removals are real common-noun antecedents. Brain-foundational: the never-subject structural proxy for
   referentiality over-fires on modern multi-genre text (a 19c-calibrated heuristic). Land it WITH the stack.
   Combined ladder = LIVE incumbent 0.5032 -> **0.5855 (+0.082 CI-sep)**.
2. **KEEP `unified_referent` DEFAULT-OFF (do NOT land the hybrid path).** The compose is a measured located negative even
   with perfect clustering and a swept decay. Do NOT add a `unified_referent_hybrid` path -- it would regress the live
   incumbent (-0.028) for the same reason the faithful port did. The audit's DEFAULT-OFF disposition for
   `hdlab/unified_referent.py` is confirmed correct and the reason is now mechanistic (subsumption + antagonism, not just
   "measured net-negative").

## IS THIS 100% BRAIN-FOUNDATIONAL? (honest itemized assessment -- owner ask)
**No -- the COMPUTATIONS are all brain-foundational, but several IMPLEMENTATIONS are proxies, and the drill
just quantified the load-bearing deviation.** Component by component in the live he/she coref chain:

| component | brain requirement | PINNED (faithful) vs OUR-INVENTION (proxy) | fidelity |
|---|---|---|---|
| graded ACT-R pick | cue-based content-addressable retrieval (Lewis & Vasishth 2005) | **PINNED** -- the retrieval currency is the ACT-R base-level activation, held-out near-optimal | faithful |
| person-feature exclusion (phi, the win I landed) | a 1st/2nd-person SPEAKER is never a 3rd-person referent (Benveniste 1966) -- an obligatory constraint | **CONSTRAINT PINNED**; but the DETECTION (`is_discourse_participant`: >=50% 1st/2nd-person heads AND no 3rd-person mention) is an **OUR-INVENTION head-count proxy**, NOT the brain's deixis/quotative-frame speaker-tracking (Kaplan 1989). The reader HAS `deixis_person`/`note_turn` primitives that this does not use. | constraint faithful; detection is a proxy (costs 1.5% recall) |
| gender/phi agreement | agreement is a GRADED, VIOLABLE cue (Carminati 2002) | **DEVIATION** -- the live `_agreement_narrow` is a **HARD filter**. The drill shows this hard-vs-graded gap is the **DOMINANT wall**: it over-removes the gold antecedent 14.6% of the time, 100% on gender-unknown entities. (Naive softening floods the pool and hurts -0.036 -- so the faithful fix needs better gender, not just a soft cue.) | **the load-bearing deviation, quantified** |
| generic-distractor suppression | a pronoun refers to a REFERENTIAL/given entity, not a generic | **CONSTRAINT PINNED**; the STRUCT implementation (never-subject genderless common noun) is a **proxy** for referentiality that MEASURABLY over-fires on modern gold -- it removed the gold antecedent 152x, 97% real common nouns. Softening it (drop STRUCT, keep quantifier NONREF) is +0.027 CI-sep and MORE brain-faithful | proxy over-fires; softened in the stack |
| gender inference (upstream) | gender is set at first reference and stable (Carminati 2005) | gazetteer + GUM gold Gender feat; **no morphological/learned gender organ** -> many entities gender-UNKNOWN, which is exactly what the hard narrow then over-removes | the upstream fidelity gap the wall points at |
| entity individuation | ONE referent per entity (Heim/Kamp DRT) | the reader keys by surface head (fragmented); unifying it is a **located negative under this scorer** (subsumption) -- so here the fragmented representation is not the bottleneck | not the bottleneck here |

**Bottom line:** every CUE is a genuine brain cue (copy-the-computation is satisfied), but the DETECTORS are
proxies (participant-detection, referentiality/suppression, gender-inference), and **agreement is hard where the
brain is graded**. The deepening pass CLOSED part of that implementation gap with three brain-fidelity fixes that
stack to +0.082 CI-sep (person-feature exclusion wired; agreement generalized to `him`; the over-firing
referentiality proxy softened). What REMAINS: (1) a real GENDER-INFERENCE organ (the drill's biggest named lever
-- recovers recall but title/kinship cues alone don't convert), (2) brain-faithful DEIXIS for participant
detection (the reader has unused primitives), (3) graded agreement once gender is good enough. So the honest
verdict moved from ~80% toward the low-90s at the implementation level: **computationally brain-foundational,
and now materially more faithful in implementation**, with a NAMED, QUANTIFIED, ordered path for the rest.

## What I did NOT establish / would withdraw first
- **I did not achieve the brief's LITERAL deliverable** (a HYBRID that beats the incumbent). It is a located negative. If a
  reviewer requires the hybrid to win, this is a clean REFUTED on that clause -- the FIRST thing I'd flag.
- **The phi gain is a DIFFERENT problem than the one filed** (person-feature pool cleanup, not unified-referent
  composition). It is in-scope as "the real problem underneath" and the brief itself named `phi_agreement_keep` as pool
  machinery, but a strict reading could call it out-of-scope for *this* slug. It is the highest-value thing I found.
- **The primary scorer is last-nominal-mention identity, not the intrinsic dominant-cluster** the reference used. I chose
  it because dominant-cluster is size-gamed (the shuffled twin beat the hybrid under it -- a real confound I caught). Under
  dominant scoring the same negative holds (hybrid 0.5710 < incumbent 0.5968), so the conclusion is scorer-robust; but the
  exact deltas differ by scorer, and I would withdraw any cross-scorer number first.
- **GUM only.** The reference's GENTLE OOD arm was not run here; the phi gain's register-dependence (first-person-heavy
  genres) is argued from the mechanism, measured only on GUM's mixed genres.

## KEY REALIZATIONS (the enabling moves)
- **Validate the harness against the LIVE substrate BEFORE trusting any hybrid number.** Forcing my reimplementation to
  reproduce the real reader's 0.5032 and the real port's 0.4331 *exactly* (a self-test gate) is what made the -0.028 a
  trustworthy negative rather than a harness artifact -- and it caught two real bugs (the port writes back ALL pronouns
  incl. it/they; and it completes gender from a resolved pronoun, which steers later common merges).
- **A scorer can be gamed by the very structure under test.** The first twin (shuffled grouping) BEAT the hybrid -- because
  dominant-cluster scoring rewards big merged groups whose mode is the frequent protagonist. Switching to the size-robust
  last-nominal-mention scorer flipped the twin to a clean loser and revealed the honest tie. When the manipulation is
  "merge things", the scorer must not reward merging per se.
- **The ORACLE control separates a fidelity gap from a fundamental negative.** Perfect (gold-cluster) unification STILL
  loses to the incumbent -> the wall is subsumption, not clustering quality -> no amount of upstream work rescues it. That
  is the difference between "build across the gap" and "keep it off", answered with a measurement.
- **The disk outranked the brief and that was the whole win.** The brief asserted person-feature exclusion is in the
  incumbent pool; `grep` showed it is dormant. The refuted compose freed me to test the dormant organ, which is the actual
  live gain. The negative was not the end -- it was the pointer.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, E3 coreference / entity tracking)
- The 2026-09-06 unified-referent DEFAULT-OFF entry is CONFIRMED and the reason is now MECHANISTIC: the hybrid (unified pool
  -> incumbent scorer) does not beat the live incumbent on modern GUM he/she (0.4750 vs 0.5032), **even with ORACLE
  (perfect) unification (0.4661) and even swept over the ACT-R decay** -- the unification lever is SUBSUMED and mildly
  ANTAGONIZED by the tuned pool (it monotonically helps the weak isolation scorer but hurts the strong incumbent scorer).
  Keep `hdlab/unified_referent.py` DEFAULT-OFF; do NOT build a `unified_referent_hybrid` path.
- **NEW deviation to fold in:** the live incumbent pool (`_graded_pool_pick`) does NOT apply person-feature exclusion --
  `graded_coref_pick.phi_agreement_keep` is landed-but-dormant. Wiring it is a CI-separated live coref gain on modern gold
  (+0.0387, twin loses, named no-regress). This is a landed-not-live gap in the coref pool, and the highest-value coref
  follow-on.

## Adjacent components (seeds for the next problems)
- **`phi_agreement_keep` / `keep_after_pool_cleanup` -- DORMANT in the live coref pick, now PROTOTYPED + OPTIMIZED.**
  Brain-foundational (person-feature agreement), CI-sep live gain (+0.039), ready to wire (TIER1). **The recommended
  thing to land.** TIER2-with-gender is measured REDUNDANT here; TIER2 with a REAL animacy signal (NER person/place --
  "no place for he", "no person for it") is untested and needs an animacy organ the reader does not yet supply -- a
  further lever and a candidate follow-on. The gain is register-sensitive (first-person genres +0.091 vs third-person
  +0.019), so on a first-person-heavy deployment (dialogue / social) it is worth more than the headline average.
- **The unified referent's real home is the WEAK scorer / non-coref consumers.** Unification helps the isolation scorer
  (+0.052) and helped the reference's intrinsic pronoun pick (+0.106) and the entity-KB hard-link -- so its value is for
  consumers that do NOT already have the tuned graded pool (entity-KB, affect-experiencer, the situation-model entity
  layer), not the he/she pick. Revisit those consumers to draw on the unified referent, not the coref pick.
- **The he/she coref residual above ~0.54 is the documented individuation + world-knowledge wall** (priority-1), not a
  fidelity gap in this component. The coherence next-mention prior is owner-DONE dead x2 -- do not re-open.

---

**TLDR (plain English):** A good reader keeps one shared record per character; we tried feeding that merged record into the
reader's already-strong, separately-tuned way of guessing who "he"/"she" means. On modern test text it did NOT help -- it
tied, leaning slightly worse (about 48 vs 50 right in 100) -- and we proved *why*: even a PERFECT merge doesn't help,
because the strong guesser already throws out the obvious wrong candidates and relies on *who was mentioned most recently*,
which merging actually blurs. So the shared-record idea, which helps a weaker guesser, is redundant with (and slightly
fights) the strong one here -- the shelved feature stays correctly turned off. **But we found a real win a different way:**
the reader was supposed to ignore the speaker ("I"/"we") when resolving "he"/"she", and a piece that does exactly that was
already built but never plugged in. Plugging it in makes the live guess clearly better (about 50 -> 54 right in 100, a
clean gap a scrambled control can't fake, and it never hurts named characters) -- especially on modern first-person-heavy
text like interviews and forums. That is a one-function change for the other session to land.

**QUESTIONS:** none blocking. One judgement call: the filed problem is about the shared-record composition (a located
negative); the actual live gain comes from a *different* dormant piece (the speaker filter). If you want that landed under
its own problem slug rather than this one, say so -- the measurement and proposed wire are ready either way.

**NEXT STEPS:**
1. Strategy lands the **person-feature filter** into `hdlab/event_centrality_coref._graded_pool_pick` (pool pre-filter,
   recall-safe, default-ON) and re-verifies the +0.039 live gain + named no-regress on the board.
2. Keep `hdlab/unified_referent.py` **DEFAULT-OFF**; do NOT add a hybrid path (measured located negative + oracle
   control). Fold the mechanistic reason into the audit.
3. Land the **FULL STACK together** (all three CI-sep, brain-foundational, recall-safe): phi + agreement-narrow
   on `him` + soften generic-suppress (use_struct=False). Cumulative **0.5032 -> 0.5855, +0.082 CI-sep** on modern
   GUM he/she -- a 16% relative lift with no new organ.
4. **File the dominant follow-on: a GENDER-INFERENCE organ.** The ceiling is a ~27% hard-filter recall tax, the
   agreement-narrow half (15%) 100% on GENDER-UNKNOWN gold. Naive soft agreement floods (located negative); the
   brain-faithful fix is upstream gender. Prototyped here: glass-box title/kinship cues recover recall (0.677 ->
   0.740) but do NOT convert to accuracy CI-sep -- a PARTIAL lever. A richer organ (occupational nouns,
   name-gender model, confidence-gated coreferent propagation) is the real fix; this is the biggest remaining
   live coref lever on modern gold, now quantified.
5. Revisit the **non-coref consumers** (entity-KB hard-link, affect-experiencer, the situation-model entity layer) to draw
   on the unified referent -- that is where the +0.052-to-+0.106 unification lever actually lives, not the tuned he/she pick.
