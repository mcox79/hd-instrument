---
problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain
status: PARTIAL
bar: "Beats the LIVE incumbent CI-separated on the MODERN GUM he/she pronoun-pick population (n~1240; the incumbent ~0.503 recomputed on the SAME population + scorer as the hybrid), with (a) the info-free TWIN ... LOSING CI-separated ... (b) NO-regress on NAMED coref ... A rigorous NEGATIVE is a FULL PASS (e.g. 'the hybrid TIES the live incumbent, Delta within CI of 0, because the generic-suppress + agreement-narrow pool already prunes exactly the fragments the unification merges -- the merged cross-type history is redundant with the tuned graded retrieval on this population; the unification value is SUBSUMED by the live pool ... keep hdlab/unified_referent.py correctly DEFAULT-OFF')."
result: "TWO findings on MODERN gold (GUM V12.1.0, 137-doc TEST, n=1240 he/she anaphoric targets; primary scorer = last-nominal-mention identity, which is size-robust and == the live reader's head_to_cluster on the fragmented arm). (1) LOCATED NEGATIVE (the brief's compose mechanism): the HYBRID (unified pool -> incumbent graded_antecedent_pick + suppression pool) scores 0.4750 vs the LIVE incumbent 0.5032, delta -0.0282 CI[-0.123,+0.056] -- does NOT beat the incumbent; the shuffled-grouping twin LOSES (0.3556, hybrid-twin +0.119 CI-sep, so the merges ARE real signal); ORACLE (perfect gold-cluster unification) also fails (0.4661 vs 0.5032); no ACT-R decay d in {2..6} recovers it. Unification MONOTONICALLY helps the weak isolation scorer (frag 0.3411 -> uni 0.3935 -> oracle 0.4065) but HURTS the strong incumbent scorer (frag 0.5032 -> uni 0.4750 -> oracle 0.4661): the two systems are ANTAGONISTIC on this population, so keep hdlab/unified_referent.py DEFAULT-OFF. (2) LIVE GAIN via a DIFFERENT lever: the brief ASSUMED person-feature exclusion is in the incumbent pool, but graded_coref_pick.phi_agreement_keep is LANDED-but-DORMANT (never called by _graded_pool_pick). Wiring it into the ACTUAL EventCentralityReader lifts the live he/she coref (native head_to_cluster) 0.5032 -> 0.5419, PAIRED doc-bootstrap delta +0.0387 CI[+0.0115,+0.0745] CI-SEPARATED; the random-drop twin (drop the same COUNT at random) LOSES (0.4637, phi-twin +0.0815 CI-sep) so it removes person-feature POLLUTION not pool size; named-antecedent no-regress (it RISES +0.036)."
floor: "The strongest floor actually run, recomputed on the SAME he/she GUM TEST population + the SAME primary scorer as each comparison: for the compose question, the LIVE incumbent = 0.5032 (native head_to_cluster; identical under the size-robust last-nominal scorer since the incumbent pool is fragmented); the hybrid does NOT clear it. Info-free floors: shuffled-grouping twin 0.3556, fragmented-x-isolation 0.3411. For the phi live-gain, the floor is the same LIVE incumbent 0.5032; phi clears it +0.0387 CI-sep. Perfect-unification ceiling under the incumbent scorer = oracle 0.4661 (BELOW the incumbent -- subsumption)."
controls: "COMPOSE negative: (1) pool x scorer 2x2 on ONE population, identical scorer machinery per cell -- isolates the pool-representation factor; (2) info-free TWIN = shuffled unified grouping (same #entities + size shape), LOSES CI-sep -> the grouping is load-bearing, the negative is subsumption not 'any re-keying'; (3) ORACLE = perfect gold-cluster unification fed to the incumbent scorer -> STILL loses -> the ceiling is SUBSUMPTION, not clustering quality (excludes 'better upstream clustering would fix it'); (4) phase-diagram d-sweep {2.0..6.0} dev-tuned/test-reported -> no decay recovers (excludes 'a tuning gap'); (5) NO-regress named subset; (6) POSITIVE control on the fragmented-protagonist subset (name variants that split the surface-head pool) -> hybrid still does NOT beat the incumbent there. PHI gain: (7) random-drop info-free twin (same drop COUNT, random which) LOSES CI-sep -> pollution-removal not pool-shrink; (8) named-antecedent no-regress (RISES); (9) the gain reproduces on the ACTUAL EventCentralityReader (native scorer), not only the reimplementation. FAITHFULNESS: the 2x2 arms reproduce the live substrate EXACTLY -- fragmented x incumbent == real EventCentralityReader (0.5342 slice / 0.5032 full, byte-exact) and unified x isolation == real resolve_unified_stream (0.4868 slice)."
files_changed: "experiments/exp_hybrid_unified_incumbent_coref_gum_v1.py, verification/test_hybrid_unified_incumbent_coref.py, notes/problems/compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain/SOLVED.md. NO hdlab/ writes (Q111 -- proposed wires stated below). Reuses data/corpora/gum/ (already on disk, pinned V12.1.0)."
reverify: ".venv/Scripts/python.exe verification/test_hybrid_unified_incumbent_coref.py  (11/11; includes the faithfulness self-test that reproduces the live incumbent 0.5032 and the port 0.4331 exactly)"
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

## PROPOSED hdlab WIRES (Q111 -- STRATEGY lands them; solver is scope-barred from hdlab/)
> I cannot land these. Reference implementations: `exp_hybrid_unified_incumbent_coref_gum_v1.py`
> (`resolve_arm`, the `_PhiReader` subclass in `real_reader_phi_gain`).

1. **LAND THE PHI GAIN (the actionable win).** In `hdlab/event_centrality_coref.EventCentralityReader._graded_pool_pick`,
   apply `graded_coref_pick.phi_agreement_keep(pronoun_low, prior_mention_heads, animacy=None)` as a **pool pre-filter**
   before `graded_antecedent_pick` (TIER1, animacy all-None = recall-safe, never empties the pool). It needs the pronoun's
   surface form and each candidate's prior mention-head list -- thread a `midx -> head` map through `resolve_stream`
   (already builds `midx_to_role` the same way). Measured live gain +0.0387 CI-sep on modern GUM he/she, twin loses, named
   no-regress. Put it behind a `phi_person_filter` flag; per no-more-default-off, default-ON is justified (CI-sep win +
   recall-safe + no-regress). This is a **dormant-organ activation**, not a new organ.
2. **KEEP `unified_referent` DEFAULT-OFF (do NOT land the hybrid path).** The compose is a measured located negative even
   with perfect clustering and a swept decay. Do NOT add a `unified_referent_hybrid` path -- it would regress the live
   incumbent (-0.028) for the same reason the faithful port did. The audit's DEFAULT-OFF disposition for
   `hdlab/unified_referent.py` is confirmed correct and the reason is now mechanistic (subsumption + antagonism, not just
   "measured net-negative").

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
- **`phi_agreement_keep` / `keep_after_pool_cleanup` -- DORMANT in the live coref pick.** Brain-foundational (person +
  animacy agreement), measured live gain, ready to wire. **The recommended next problem.** TIER2 (add animacy exclusion:
  no place for "he", no person for "it") needs a candidate-animacy signal the reader can supply from NER/lexical animacy --
  a further lever untested here.
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
3. Revisit the **non-coref consumers** (entity-KB hard-link, affect-experiencer, the situation-model entity layer) to draw
   on the unified referent -- that is where the +0.052-to-+0.106 unification lever actually lives, not the tuned he/she pick.
