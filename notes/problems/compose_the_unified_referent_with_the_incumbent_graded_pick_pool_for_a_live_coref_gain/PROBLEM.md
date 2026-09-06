---
priority: 12
slug: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the unified discourse referent lifts the GUM pronoun pick +0.106 in isolation but REGRESSES the LIVE incumbent when landed as a faithful port (0.433 vs the live graded_pick 0.503 on modern GUM) because the port SWAPS the scorer -- it throws away the incumbent's strong pool machinery (generic-distractor suppression + agreement-narrow + tuned weights + ACT-R d=3.0) for the reference's isolation config (pure ACT-R d=2.0, recall-safe gn, no suppression); realize the win LIVE by COMPOSING the two complementary brain systems -- re-key the overlay to ONE unified referent per entity (file-change history) while KEEPING the incumbent graded_antecedent_pick + suppression pool -- so the merged referent history feeds the STRONG incumbent scorer instead of replacing it.

**slug:** `compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain` -- **opened:** 2026-09-06
by the strategy session (the follow-on the unified-referent review explicitly named: *"the live win needs the HYBRID -- unify the
store ON TOP of the incumbent pool"*). **status:** CANDIDATE -- a COMPOSE + MEASURE problem over TWO landed, owner-DONE organs.
You build + validate the hybrid in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, NO external LLM at
inference (the invariant) -- the referent merge + the graded ACT-R retrieval are both transparent, not a learned coref model.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `12` (a free,
> unique rank). It REALIZES a PROVEN brain-foundational lever that is currently DORMANT (landed EXCELLENT + owner-DONE, but
> DEFAULT-OFF with a measured live regression) and is the exact follow-on the review named -- but it is a CANDIDATE compose
> that depends on the incumbent pool's live population, so it is ranked with the other CANDIDATE integration/reasoning
> builds. Set the real priority when this is promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **🎛️ (PHASE DIAGRAM — the substrate is not locked to one regime.)** The substrate's operating point — store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization — is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **🧠🔧 (FULL-STACK UPSTREAM — prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED — make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT — YOU AND UPSTREAM — TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too — and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
A good reader keeps ONE mental record per character: "Elizabeth", "the young woman", and "she" all update the same card. We
built that single-record idea and it clearly helped in a lab test -- deciding who "he"/"she" means got much better. But our
LIVE reader already has a strong, separately-tuned way of making that same guess, and it has learned extra tricks the lab
version did not: it ignores obviously-generic candidates ("a man", "the people"), it double-checks gender, and it uses
tuned dials. When we dropped the new single-record method in as a wholesale REPLACEMENT, it did WORSE than what is already
running (about 43% right vs the live 50%), because the replacement threw all those tricks away. The lab test only looked
good because it was scored against a weakened version, not against the real live system. The fix is to COMBINE, not swap:
keep the strong live guesser exactly as it is, but feed it the merged one-record-per-character memory instead of the
current fragmented one, where a single character is split into several half-remembered pieces. Then prove on modern test
text that the combination actually beats the real live system -- or show honestly that the live system's tricks already
capture everything the merged memory would have added.

## 2. WHY THIS ONE
The unified referent is a LANDED, EXCELLENT, owner-DONE result that sits DEFAULT-OFF with a MEASURED reason: as a faithful
port it REGRESSES the live incumbent (0.4331 vs 0.5032 on modern GUM, the he/she population; source: `BRAIN_FOUNDATIONAL_AUDIT.md`
sec 2b, 2026-09-06). So a proven brain-foundational lever is currently DORMANT and delivering ZERO on the board. This is the
exact HYBRID follow-on the review named. It is also the twin failure mode the owner flagged (2026-09-06): the solver measured
against an ISOLATED/DEFAULT scorer, not the LIVE (already-tuned) substrate -- so the true test is the hybrid against the LIVE
incumbent. The prize is real: the coref dim is the reader's weakest, this composes TWO complementary brain systems (Heim/Kamp
file-change referent + Lewis & Vasishth ACT-R cue-based retrieval), and it is a MODERN-gold problem (the board coref dim is
19c LitBank, BANNED as load-bearing; the modern GUM he/she pronoun population is its proper home). **The defect is measured, not
hypothetical:** the landed port is presently a −0.0702 net-negative if flipped on; this problem converts that measured
regression into either a measured LIVE gain or a rigorous located negative that keeps the port correctly default-off.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the two computations that must COMPOSE):** (1) Heim (1982) / Kamp DRT FILE-CHANGE semantics -- ONE file card per
  discourse entity, opened on first mention and UPDATED (never re-created) by every later name/common/pronoun mention, so the
  card holds the COMPLETE cross-type mention history + gender. (2) Lewis & Vasishth (2005) / McElree (2003) / Anderson ACT-R
  cue-based content-addressable RETRIEVAL -- the pronoun re-activates the antecedent by GRADED competition over cues (recency
  x frequency x Cf-prominence = base-level activation A = ln(sum_k w(role)*dt^-d)), read out by a softmax. These are NOT
  alternatives: the file card is the MEMORY (what is stored per entity), the ACT-R competition is the RETRIEVAL (how the
  pronoun selects among cards). The brain's retrieval competes over COMPLETE entity cards; our live incumbent competes over
  FRAGMENTED surface-head records. The lever is to give the strong retrieval its correct input -- one complete card per entity.
- **PINNED (the incumbent's pool machinery is ALSO brain-foundational, keep it):** generic-distractor suppression (the brain
  does not compete a non-referential generic "a man" as an antecedent) + agreement-narrow (phi-feature gating) + person-feature
  exclusion. These are `hdlab/coref_distractor_suppress.GenericDistractorFilter` + `_agreement_narrow` + `graded_coref_pick.phi_agreement_keep`.
  The faithful port dropped them; the hybrid keeps them.
- **OUR-INVENTION-UNDER-TEST (sweep, do NOT adopt):** how the unified card supplies its history to the incumbent
  `graded_antecedent_pick` (candidate-priors = the card's full (sent_idx, role) history vs the fragment's partial history); the
  ACT-R decay d (the incumbent uses d=3.0 via TUNED_WEIGHTS; the reference used d=2.0 -- SWEEP on GUM dev, do not adopt either
  number); whether the resolved-pronoun writeback into the card helps or hurts under the incumbent pool. LABEL the
  card<->pool composition as OUR-SYNTHESIS.
- **NOT brain-faithful (the swap that failed):** replacing the incumbent scorer + pool with the reference's isolation config
  (pure ACT-R d=2.0, recall-safe-only gn, NO generic suppression) -- that IS the landed port, measured −0.0702; do not
  reproduce it. Also NOT faithful: an external LLM at inference; scoring the headline on 19c prose; treating the reference's
  gender-STRANDED separate arm (0.3621) as the live baseline.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The unified referent's ISOLATED lift: GUM TEST (137 docs, n=3132 anaphoric), pronoun pick separate 0.3621 -> unified
    0.4681, +0.1060 CI[+0.079,+0.133] (hw 0.027), twin 0.2034 -- scored INTRINSICALLY (`UnifiedRef.dominant_cluster()`), and its
    0.3621 baseline is the reference's own gender-STRANDED separate arm, NOT the live reader. This is isolated-lever science,
    NOT a live number (`form_the_unified_discourse_referent.../SOLVED.md`).
  - The LANDED faithful port (`hdlab/unified_referent.py`, flag `situation_reader.unified_referent`, DEFAULT-OFF): against the
    LIVE incumbent on the he/she GUM population (n~1240), it scores **0.4331 vs the incumbent 0.5032 = −0.0702 on MODERN gold**
    (−0.085/−0.176 on 19c, informational). The live incumbent's stronger POOL config already subsumes the swap
    (`BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b, 2026-09-06 unified-referent entry).
  - The LIVE incumbent = `EventCentralityReader(graded_pick=True).resolve_stream` (`hdlab/event_centrality_coref.py`): pool =
    `overlay._compatible_entities(gender, number)` -> generic-distractor suppression (`GenericDistractorFilter.is_generic`,
    `suppress_generic=True`, L316-318) -> `_agreement_narrow` (L324) -> `_graded_pool_pick` (L422) ->
    `graded_antecedent_pick(TUNED_WEIGHTS)` with ACT-R d=3.0. When it landed it lifted live pooled coref 0.4693 -> 0.6019
    (+0.1327, LitBank, informational). This is the STRONG scorer + pool the faithful port replaced.
  - The overlay fragments the entity: `hdlab/state_of_mind.WorkingOverlay.observe` keys `self._entities` by the SURFACE HEAD
    STRING (L309-311, `self._entities[head]`), so a protagonist's name variants + resolved-pronoun writeback split across
    several `EntityState`s; each pool candidate is a FRAGMENT with partial history, and scoring uses `head_to_cluster`
    (surface-head -> cluster). This fragmentation is exactly what the unified card removes.
  - The two paths are MUTUALLY EXCLUSIVE early-returns: `resolve_stream` does `if self.unified_referent: return
    resolve_unified_stream(...)` (L238-242, the SWAP) ELSE the `graded_pick` pool path (L243+). NO path today feeds unified
    referents THROUGH `_graded_pool_pick`. That absence -- the un-built composition -- is what this problem targets (verify by
    enumeration; see VERIFY BEFORE YOU START).
- **INFERRED (you must prove):** that re-keying `_entities` to ONE unified referent per entity (EntityAliaser-canonical id +
  cross-type file-change history incl. resolved-pronoun writeback) while feeding those UNIFIED candidates through the UNCHANGED
  incumbent `_graded_pool_pick` (generic-suppress + agreement-narrow + TUNED_WEIGHTS d=3.0) BEATS the LIVE incumbent
  CI-separated on the he/she GUM population (n~1240; incumbent ~0.503), with the shuffled-identity info-free twin LOSING and
  no-regress on named coref -- OR a rigorous located NEGATIVE with the cause named + counted (e.g. the incumbent's generic-
  suppress + agreement-narrow already prune exactly the fragments the unification merges, so the merged history adds nothing on
  top of the tuned graded retrieval; the unification value is SUBSUMED by the live pool -- measured with the 2x2 below, which
  keeps the port correctly default-off).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-run the isolated-lever science or re-derive the unified representation. READ IN FULL
  `form_the_unified_discourse_referent_before_the_pronoun_pick_the_shared_entity_lever/{PROBLEM.md,SOLVED.md,OWNER_NOTES.md}`:
  it built the DRT file-change referent, decided the cue-specificity (Ariel) by measurement, and ran the nine within-component
  optimizations (all saturated). REUSE `hdlab/unified_referent.py` (the card + EntityAliaser keying + salience_binder) as-is.
- Do NOT re-derive the graded pick or its pool. READ IN FULL
  `strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap/SOLVED.md` (the incumbent graded ACT-R
  pick). REUSE `hdlab/graded_coref_pick.graded_antecedent_pick` (TUNED_WEIGHTS, d=3.0) + `_graded_pool_pick` +
  `hdlab/coref_distractor_suppress.GenericDistractorFilter` unchanged.
- Do NOT SWAP the scorer -- that IS the faithful port, measured −0.0702 on modern GUM. Do NOT weaken the incumbent to the
  reference's isolation config (d=2.0, no suppression, recall-safe-only gn); that reproduces the regression.
- The SOLVED's guardrails are measured negatives -- do NOT re-open: graded/confidence-gated Nref writeback; hard working-memory
  bound (redundant with the decay); animacy phi (redundant with English gender); the salience cue on NOMINAL resolution
  (Ariel); global decay d=1.5 (a kb-only trade). Keep event-centrality OFF (`query_memory=False`, measured net-negative).
- Do NOT use 19c LitBank as load-bearing gold (BANNED 2026-09-06 -- a 19c number is informational only); do NOT use an external
  LLM at inference (the invariant).
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "unified"` /
  `"referent"` / `"coref"` / `"graded"` / `"gum"` / `"hybrid"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm `unified_referent` is
  default-OFF and `graded_pick` is default-ON, and see what `EventCentralityReader` exposes -- then skim `hdlab/`, so you
  compose ON the existing organs, not beside them.
- READ IN FULL (build ON them, credit them): the two SOLVED.md above. READ the audit sec 2b entries dated 2026-09-06 in
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md`: the unified-referent DEFAULT-OFF entry (0.4331 vs 0.5032; "solvers measure against an
  ISOLATED/DEFAULT config, not the LIVE substrate"; the HYBRID named as the follow-on) and the graded ACT-R pick landing entry.
- INSPECT what you REUSE + compose: `hdlab/unified_referent.py` (`resolve_unified_stream`, `UnifiedRef`, the card update +
  writeback); `hdlab/event_centrality_coref.py::EventCentralityReader.resolve_stream` (L238 the `unified_referent` early-return
  SWAP; L243 `graded_pick`; L314 `_compatible_entities`; L316 `suppress_generic`; L324 `_agreement_narrow`; L422
  `_graded_pool_pick`); `hdlab/graded_coref_pick.py` (`graded_antecedent_pick`, `TUNED_WEIGHTS`, `phi_agreement_keep`,
  `keep_after_pool_cleanup`); `hdlab/coref_distractor_suppress.py` (`GenericDistractorFilter`, `build_ever_subject_heads`);
  `hdlab/coref.py` (`EntityAliaser`); `hdlab/salience_binder.py` (`actr_activation`); `hdlab/state_of_mind.py`
  (`WorkingOverlay.observe` / `_entities` L309-311, `compatible`, `PRONOUN_SCOPE`).
- ENUMERATE the absence (an absence claim requires an enumeration, not a search): confirm NO reader path feeds unified referents
  into `_graded_pool_pick` -- the two paths are exclusive early-returns in `resolve_stream`. `grep -rin "resolve_unified_stream\|_graded_pool_pick\|unified_referent" hdlab/ experiments/`
  and state how you enumerated in your submission.
- GOLD: GUM is ALREADY on disk -- `data/corpora/gum/` (pinned V12.1.0 @ 22fdf87; fetch script `experiments/fetch_gum_coref_v1.py`,
  parse via `experiments/gum_coref.py`). Reuse the SAME he/she pronoun-pick population + LIVE scorer the sec 2b comparison used
  (n~1240, incumbent ~0.503), so the floor is the LIVE incumbent recomputed on that population -- NOT the reference's intrinsic
  dominant_cluster scorer. No 19c load-bearing gold.

## 7. THE BAR
PASSES only with ALL of:
1. **A HYBRID resolver (built in `experiments/`)** that COMPOSES, not swaps: the UNCHANGED incumbent `_graded_pool_pick`
   (generic-distractor suppression + agreement-narrow + `graded_antecedent_pick` TUNED_WEIGHTS d=3.0) SCORING over a candidate
   pool of UNIFIED referents (one card per entity via `unified_referent`'s EntityAliaser-canonical keying + cross-type
   file-change history incl. resolved-pronoun writeback). The scorer + pool FILTERS are byte-unchanged from the incumbent; ONLY
   the referent representation the pool draws from is unified. NO external LLM. Copy the file-change + ACT-R COMPUTATION; SWEEP
   the history-supply rule / decay d / writeback on GUM dev.
2. **Beats the LIVE incumbent CI-separated on the MODERN GUM he/she pronoun-pick population** (n~1240; the incumbent ~0.503
   recomputed on the SAME population + scorer as the hybrid), with:
   (a) the info-free **TWIN** -- shuffle the identity evidence (shuffled EntityAliaser assignment and shuffled cross-type
   history), SAME machinery + shape -- LOSING CI-separated (proves the MERGED referent history is load-bearing, not "any
   re-keying");
   (b) **NO-regress on NAMED coref** recomputed on its own population.
   Report CI half-width + null p95; recompute the floor (the LIVE incumbent) on its OWN population; NO number crosses
   scorers/populations. A **POSITIVE control** the incumbent cannot get: a protagonist whose name variants + resolved-pronoun
   writeback FRAGMENT the incumbent surface-head pool but UNIFY into one card, so the ACT-R competition sees the complete
   history only in the hybrid.
3. **Isolates the lever with a 2x2** -- {pool: fragmented vs unified} x {scorer: incumbent (suppress + narrow + d=3.0) vs
   reference isolation (d=2.0, no suppress)} on the SAME population: fragmented x incumbent = the live ~0.503; unified x
   isolation = the port's ~0.433 (reproduce the regression); unified x incumbent = the HYBRID. Show the hybrid's number is the
   COMPOSITION (unified pool feeding the strong scorer), and name which cell it beats and by how much.
4. **One-screen summary:** the 2x2 (pool x scorer) -> floors (live incumbent, recomputed) -> twin -> named no-regress -> he/she
   accuracy + CI -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the hybrid TIES the live incumbent, Δ within CI of 0, because the generic-suppress +
agreement-narrow pool already prunes exactly the fragments the unification merges -- the merged cross-type history is redundant
with the tuned graded retrieval on this population; the unification value is SUBSUMED by the live pool, measured with the 2x2 ->
keep `hdlab/unified_referent.py` correctly DEFAULT-OFF"; OR "the hybrid beats the incumbent only on the fragmented-protagonist
subset (N of M items where name variants + writeback split the surface-head pool) and is flat elsewhere -- a located, quantified
partial win").

## 8. FILES AND ENTRY POINTS
- **REUSE (landed/owner-DONE -- do NOT rebuild):** `hdlab/unified_referent.py` (`resolve_unified_stream`, `UnifiedRef` card +
  writeback); `hdlab/event_centrality_coref.py` (`EventCentralityReader.resolve_stream`, `_graded_pool_pick`, `_agreement_narrow`);
  `hdlab/graded_coref_pick.py` (`graded_antecedent_pick`, `TUNED_WEIGHTS`, `phi_agreement_keep`, `keep_after_pool_cleanup`);
  `hdlab/coref_distractor_suppress.py` (`GenericDistractorFilter`); `hdlab/coref.py` (`EntityAliaser`); `hdlab/salience_binder.py`
  (`actr_activation`); `hdlab/state_of_mind.py` (`WorkingOverlay.observe` / `_entities` / `compatible` / `PRONOUN_SCOPE`).
- **Gold:** GUM is on disk (`data/corpora/gum/`, pinned V12.1.0; `experiments/fetch_gum_coref_v1.py`, `experiments/gum_coref.py`);
  reuse the he/she pronoun population + LIVE-incumbent scorer of the sec 2b comparison. No 19c load-bearing gold.
- **The eventual wire (STRATEGY lands it, Q111 -- solver never writes `hdlab/`):** re-key `WorkingOverlay._entities` / `observe`
  in `hdlab/state_of_mind.py` to the canonical unified referent id, AND add a COMPOSE path in
  `hdlab/event_centrality_coref.resolve_stream` that builds the unified pool then calls `_graded_pool_pick` (a NEW hybrid path,
  NOT the `resolve_unified_stream` early-return SWAP; likely behind a new `unified_referent_hybrid` capability flag). State the
  exact proposed change in `SOLVED.md`. Prototype in `experiments/` + `verification/` ONLY. Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b (E3 coreference / entity tracking -- the unified-referent DEFAULT-OFF entry:
  the hybrid result). Audit + heavy->REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the isolated +0.106 (0.3621 -> 0.4681) as a LIVE gain -- it is vs a weakened, gender-stranded baseline on a
  DIFFERENT scorer (intrinsic `dominant_cluster`) and population. No number crosses scorers/populations.
- Do NOT quote the port's 0.4331 as the HYBRID's result -- it is the SWAP (reference isolation scorer, no suppression). The
  hybrid's headline is UNIFIED-pool x INCUMBENT-scorer vs the LIVE incumbent, recomputed on the SAME he/she GUM population.
- Do NOT re-run the swap (that is the landed default-off port) or weaken the incumbent to the isolation config -- both reproduce
  the −0.0702 regression.
- Do NOT lean on a 19c corpus (McGuffey/LitBank) as load-bearing gold (BANNED 2026-09-06 -- informational only; the MODERN GUM
  number counts); do NOT use an external LLM at inference (the invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** Our reader keeps one shared mental record per character, and in a lab test that clearly improved who
"he"/"she" refers to. But the live reader already had a strong, separately-tuned way of making that guess, and when we swapped
the new method in wholesale it did WORSE, because the swap threw away the live version's extra tricks (ignoring obvious wrong
candidates, checking gender, tuned dials) -- the lab test had only been compared against a weakened version. The fix is to
COMBINE: keep the strong live guesser exactly as-is, but feed it the merged one-record-per-character memory instead of the
current split-up one. Prove on modern test text that the combination beats the real live system -- or show honestly that the
live tricks already capture everything the merged memory adds, which keeps the shelved method correctly turned off.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the two coref paths are exclusive early-returns and nothing
feeds unified referents into the incumbent pool), reuses `hdlab/unified_referent.py`'s card + `event_centrality_coref._graded_pool_pick`
unchanged, builds the hybrid (unified pool -> incumbent generic-suppress + agreement-narrow + TUNED_WEIGHTS d=3.0 scorer),
runs the pool x scorer 2x2 on the modern GUM he/she population with a shuffled-identity twin, and reports the margin over the
LIVE incumbent with CI half-width + null p95 -- or a located negative naming why the incumbent pool already subsumes the
unification value.
