---
slug: structured_semantic_matching_for_event_goal_and_type_converse_role_filler_knowledge_not_the_hub
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the affect, spatial, temporal, and bridging reasoners all need to know when an EVENT satisfies/thwarts a GOAL, is-a TYPE, or fills a converse ROLE -- and the distributional meaning hub (`hdlab/bridging_inference`) is POLARITY-BLIND (rel(win,lose) ~= rel(sell,buy)), so it cannot SIGN or DIRECT these relations -- build ONE glass-box, reusable STRUCTURED SEMANTIC-MATCHING organ (converse/perspective + antonymy + role-filler + type-membership, seeded from FrameNet/WordNet/ConceptNet, NO external LLM) that COMPLEMENTS the hub (which stays the fuzzy fallback) and prove it beats BOTH the distributional-hub baseline AND an info-free shuffled-KB twin CI-separated on event<->goal congruence, AND that the SAME organ transfers to at least one other consumer (spatial type or temporal script).

**slug:** `structured_semantic_matching_for_event_goal_and_type_converse_role_filler_knowledge_not_the_hub` --
**opened:** 2026-09-06 by the strategy session. The just-integrated OCC affect reasoner PROVED that the ATL
distributional hub cannot decide satisfy-vs-thwart (rel(sell,buy) ~= rel(win,lose), so "won the race" against the
goal "win" is indistinguishable from "lost"), and it MEASURED the fix: a structured knowledge-asset matcher
(FrameNet Perspective_on converse frames + WordNet antonymy + role-filler/beneficiary frames) recovers +0.417 on
event<->goal matching with the shuffle twin losing. The SAME shape recurs in three integrated reasoners -- affect
(event<->goal), spatial (AtLocation / containment TYPE-membership), and temporal (script/TYPE step-match) -- and each
is currently gated on the same polarity-blind distributional similarity. Build the shared organ once.
**status:** CANDIDATE -- a BUILD + VALIDATION problem. You build + validate in `experiments/`; strategy lands any
hdlab change (Q111). Glass-box, NO external LLM at inference (the invariant); a static offline-built knowledge asset
(WordNet / FrameNet / ConceptNet) is FOUNDATION-admissible.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `4`
> because it is a SHARED enabler named across THREE already-integrated reasoners (the OCC affect SOLVED's dominant
> ceiling, and the spatial/temporal type-match consumers), the direction is ALREADY MEASURED (+0.417 recovery on the
> converse slice, twin loses), and it is largely REUSE of FREE static lexical assets (WordNet antonymy + FrameNet
> Perspective_on already on the nltk path). It sits below the recurrent-loop closure (1) and the relation-extraction
> bottleneck (2) because those unblock more at once, but it is higher than the deeper meaning-growth candidates
> because it converts a MEASURED, buildable win into a wired capability three reasoners consume. It stays CANDIDATE
> because the +0.417 was on a 12-item CONSTRUCTED converse gold in an experiment cell -- the modern-gold end-to-end
> proof and the cross-consumer transfer are still owed. Set the real priority when promoted from CANDIDATE to OPEN.

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
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When you read that someone "won the race" and you know they wanted to win, you instantly feel the thrill -- and if
they "lost", the sting. The two outcomes are opposite, yet to a machine that only measures how RELATED two words are,
"win" and "lose" look almost identical (they occur in all the same race stories), just as "buy" and "sell" do. So a
reader that judges outcomes by word-relatedness alone literally cannot tell a goal met from a goal blocked. The same
blind spot shows up all over: is a "kitchen" the kind of place a "room" question is about? does "she stood on the
podium" count as the "winning" step of a race script? Each of these is a STRUCTURED fact -- an opposite, a role
swap, a kind-of, a step-in-a-script -- that relatedness cannot supply. The job is to build one small, transparent,
hand-checkable lookup of those structured facts (drawn from free public word dictionaries -- no outside AI), so the
reader can decide "these two are OPPOSITES" or "this is a KIND of that" with certainty, while still falling back on
the fuzzy relatedness measure when no exact fact applies. We already measured, on a small test, that adding this
recovers the right answer about 40 points more often. The job is to prove it on modern test text -- beating both the
relatedness-only baseline and a scrambled-dictionary version -- and to show the SAME lookup helps a second, different
reader (the one that reasons about places, or the one that reasons about story steps), so it is a shared tool and not
a one-off patch.

## 2. WHY THIS ONE
Three ALREADY-INTEGRATED reasoners share one wall. The OCC affect reasoner (owner-DONE) proved its dominant ceiling
is deciding satisfy-vs-thwart when the outcome event shares no word with the goal, and localized the cause: the LIVE
ATL hub `hdlab/bridging_inference` is POLARITY-BLIND (rel(sell,buy) ~= rel(win,lose)), so distributional similarity
CANNOT sign the relation. The spatial reasoner (owner-DONE) reasons over containment / AtLocation, which is a
TYPE-membership + part-whole structured relation, not cosine; the temporal reasoner (owner-DONE) built a script/schema
organ whose step-match is a TYPE decision, not cosine. The OCC SOLVED's cross-cutting lesson, measured three times,
names the shared shape exactly: "every STRUCTURED relation the reasoners need (converse, result-state, meronymy, type)
is a KNOWLEDGE-ASSET job; the distributional similarity hub is ONLY the fuzzy-similarity fallback." This problem
builds that knowledge-asset matcher ONCE, as a reusable organ, so all four reasoners consume it instead of each
re-inventing an ad-hoc lexicon (the OCC SOLVED already listed "promote the role-filler polarity layer" as its P2).
It is high-value (three consumers), low-risk (free static assets, the direction MEASURED), and it does NOT touch the
ATL hub -- it COMPLEMENTS it, keeping the hub as the fuzzy fallback the hub is good at.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the two-store split).** Semantic memory is NOT one store. The anterior temporal lobe (ATL) is a
  transmodal HUB that supplies GRADED, distributional relatedness (Lambon Ralph et al. 2017 hub-and-spoke) -- this is
  exactly what `bridging_inference` reads, and it is good at "how related", bad at "which relation / which
  direction". The COMBINATORIAL / relational reading -- the specific TYPE and SIGN of a relation (is-a, part-of,
  converse, antonym) -- is a SEPARATE computation on the structured relational network (angular gyrus / temporo-
  parietal combinatorial semantics; Binder & Desai 2011). The polarity/direction of a relation is a STRUCTURAL fact,
  not a similarity magnitude. `bridging_inference`'s own docstring already states this by the substrate's own audit:
  it does antecedent SELECTION (which) but relation TYPING "is structural, not distributional" -- a DIFFERENT organ.
- **PINNED (the specific relations).** CONVERSENESS (Cruse 1986: buy/sell, lend/borrow, teach/learn -- the SAME event
  from opposite participant PERSPECTIVES; FrameNet Perspective_on frames profile one scene from different roles).
  ANTONYMY (win/lose, pass/fail -- WordNet antonym edges; the sign flip). ROLE-FILLER / BENEFICIARY (who ends up in
  the goal-holder's valued role -- FrameNet Assistance Helper/Benefited_party; Primus Proto-Recipient; Dowty has no
  beneficiary role so the frame store fills it). TYPE-MEMBERSHIP / TAXONOMY (kitchen IS-A room; podium AtLocation
  stadium -- WordNet hypernymy + ConceptNet IsA/AtLocation/PartOf edges). Kintsch (1988) construction-integration
  SELECTS the coherent reading; the structured EDGE supplies the sign the selection cannot.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The converse/antonym/role/type lexicon coverage seeded from the
  free assets; the ABSTAIN margin at which the structured matcher hands off to the ATL-hub fuzzy fallback; the FUSION
  weight between the structured sign and the hub relatedness (for the "top step" ~ "podium" fuzzy match onto a script
  slot); the type-membership similarity threshold. All are parameters over PINNED operations, none a new mechanism.
- **NOT brain-faithful (do NOT do).** Using distributional cosine to decide satisfy-vs-thwart / is-a (the polarity-
  blind incumbent this must beat); REPLACING the ATL hub with the structured store (they are COMPLEMENTARY -- keep the
  hub as the fuzzy fallback); a learned end-to-end relation classifier; FITTING the converse/type table to the eval
  gold's verb pairs (circular -- seed from free resources, hold out the eval); an external LLM at inference.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The ATL hub is POLARITY-BLIND. `hdlab/bridging_inference` relatedness: rel(sell,buy)=0.29 but rel(win,lose)=0.26
    (high, OPPOSITE outcome) -- similarity cannot sign satisfy-vs-thwart (OCC SOLVED section 5). It is also a LOCATED
    NEGATIVE on meronymy/type: rel(report,file)=0.047, rel(garden,flowers)=0.066, rel(keys,house)=0.015, several OOV
    (OCC SOLVED P4) -- the distributional hub is too thin + non-directional for the structured relations.
  - The converse/role-filler layer is BUILT + MEASURED. `experiments/exp_occ_converse_matching_v1.py` (n=12 converse
    gold: sell/buy, lend/borrow, teach/learn, give/receive; win/lose, catch/miss, pass/fail, remember/forget;
    beneficiary-dispossess): a role-filler polarity layer lifts BASELINE (head-match only) 0.417 -> CONVERSE 0.833
    (+0.417), fire 0.50 -> 0.92, and the goal<->event-shuffle TWIN LOSES 0.333. Default-off; it did not touch the OCC
    headline. The landed `hdlab/goal_register.track_status_thwart(..., converse=True)` is the first consumer's hook.
  - The cross-cutting lesson (measured 3x across the OCC drills): every STRUCTURED relation (converse, result-state,
    meronymy, type) is a KNOWLEDGE-ASSET job; the distributional hub is ONLY the fuzzy-similarity fallback.
- **INFERRED (you must prove):** that a glass-box STRUCTURED SEMANTIC-MATCHING organ (converse/perspective + antonymy
  + role-filler + type-membership, seeded from WordNet/FrameNet/ConceptNet) beats BOTH (a) the distributional-hub
  baseline (`bridging_inference` relatedness thresholded to a sign) AND (b) an info-free shuffled-KB twin, CI-separated,
  on event<->goal congruence on a MODERN gold; AND that the SAME organ TRANSFERS to at least one OTHER consumer
  (spatial AtLocation / containment TYPE-membership OR temporal script/TYPE step-match) with the same shape and the
  twin losing; OR a rigorous LOCATED NEGATIVE naming the cause with counts (e.g. the closed-class converse/antonym/
  role-filler slice clears but the open-ended SCENE/TYPE-inference tail -- "stood on the podium" = won -- is a distinct
  Talmy/Schank world-knowledge script organ the structured lexical store does not cover; the OCC SOLVED already split
  this).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-derive that `bridging_inference` is polarity-blind -- MEASURED (OCC SOLVED section 5: rel(win,lose) ~=
  rel(sell,buy)). Do NOT re-run the n=12 converse probe and call it done -- it NAMES the direction (+0.417); the bar
  is a MODERN gold with the hub baseline + shuffled-KB twin + a SECOND consumer.
- Do NOT replace or rebuild the ATL hub (`hdlab/bridging_inference`) -- it is the COMPLEMENTARY fuzzy-match fallback,
  owner-DONE. You COMPLEMENT it; the structured store signs where the hub cannot, and hands off to the hub below margin.
- Do NOT rebuild `hdlab/occ_appraisal.py` or `hdlab/goal_register.track_status_thwart` -- landed. You feed the
  structured matcher INTO them (the `converse=True` hook + FAILURE_VERBS/IRREG_PAST closed-class path already exist).
- Do NOT FIT the converse/antonym/type table to the eval's verb/noun pairs (circular) -- seed from FREE WordNet
  antonymy/hypernymy + FrameNet Perspective_on + a closed-class converse set + ConceptNet IsA/AtLocation, and HOLD OUT
  the eval items.
- Do NOT open a THIRD generic bridging variant (Phase-2 kill condition fired 2026-08-17) -- this is a STRUCTURED-
  relation SIGN/TYPE matcher, not a distributional bridging mechanism; it is a different kind of thing.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "converse"`
  / `"antonym"` / `"polarity"` / `"role-filler"` / `"framenet"` / `"wordnet"` / `"atlocation"` / `"type"` / `"script"`
  / `"meronymy"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`; skim `hdlab/` so you
  build ON the existing organs. Confirm `hdlab/occ_appraisal.py` + `hdlab/goal_register.track_status_thwart`
  (`converse=True`) are landed (the first consumer's hook), and that `hdlab/bridging_inference.py` is the LIVE ATL-hub
  meaning consumer whose `.relatedness()` / `.select()` you will use as the distributional-hub baseline.
- READ IN FULL (build ON it, credit it): `notes/problems/infer_unstated_emotion_via_occ_appraisal_over_event_goal_
  congruence/SOLVED.md` -- the polarity-blind finding (section 5), the +0.417 converse/role-filler layer (section 9a),
  and the cross-cutting KNOWLEDGE-ASSET lesson (P2/P4) -- and its `experiments/exp_occ_converse_matching_v1.py` +
  `experiments/data/occ_converse_probe_v1.jsonl`. Read the SPATIAL SOLVED (`notes/problems/reason_over_the_spatial_
  relational_model_containment_position_path_modern_gold/SOLVED.md` -- containment / AtLocation TYPE-membership is the
  same shape) and the TEMPORAL SOLVED (`notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/
  SOLVED.md` -- the script/schema organ's step-match is a TYPE decision) to pick your SECOND, transfer consumer.
- INSPECT what you REUSE: `hdlab/bridging_inference.py` (`BridgeInference.relatedness` / `.select` -- the hub baseline
  + the fuzzy fallback); `hdlab/occ_appraisal.py` (`infer_emotion` -- the first consumer); `hdlab/goal_register.py`
  (`track_status_thwart` `converse=True`, `FAILURE_VERBS`, `IRREG_PAST` -- the closed-class converse hook);
  `hdlab/spatial_relational_model.py` + `hdlab/location_register.py` (`is_in_region` containment / AtLocation type --
  transfer target A); `hdlab/temporal_script_schema.py` + `hdlab/temporal_reasoner.py` (script terminal-state /
  precedes step-match -- transfer target B); `hdlab/meaning_foundation.py` (WordNet MFS signatures -- the fuzzy match).
- ENUMERATE the structured relations EACH reasoner needs (an absence claim requires an enumeration, not a search;
  state HOW you enumerated): affect = converse-satisfy / antonym-thwart / beneficiary-dispossess / prospect
  confirm-disconfirm; spatial = AtLocation + containment TYPE-membership (is a kitchen a room?) + part-whole; temporal
  = script-step / precedes / result-state TYPE; bridging = part-of / instrument-of TYPE. Grep the live consumers to
  confirm each currently routes through distributional similarity (or a private ad-hoc lexicon) for these.
- ASSETS: WordNet (antonymy/hypernymy) via nltk (already on the path -- `bridging_inference` / `meaning_foundation`
  use it), FrameNet (Perspective_on + role frames) via nltk framenet, ConceptNet (IsA/AtLocation/PartOf). A static
  offline KB is FOUNDATION-admissible (the invariant is NO external LLM AT INFERENCE, not no offline asset); if you
  acquire ConceptNet, put it under `data/corpora/<name>/` with a REPRODUCIBLE pinned fetch script in `experiments/` +
  a provenance note. Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the meaning-channel + Tier-6 affect/appraisal entries).
- GOLD: acquire/construct a MODERN event<->goal congruence gold (balanced satisfy/thwart, with converse + antonym +
  type slices); the constructed OCC converse probe is a CONSTRUCTION control, labelled as such. For the SECOND
  consumer, reuse a MODERN gold already on disk -- spatial (SpaceEval / SpartQA containment under `data/corpora/`) or
  temporal (TRACIE script under `data/corpora/tracie`). Do NOT lean on a 19c corpus as load-bearing; NO external LLM.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box STRUCTURED SEMANTIC-MATCHING organ (built + validated in `experiments/`; strategy lands the hdlab
   change, Q111).** Given an observed EVENT/entity and a target RELATION (converse / antonym / role-filler /
   type-membership), return the SIGNED match (satisfy vs thwart; is-a vs not; fills-role vs not) read from the
   STRUCTURED store, and ABSTAIN to the ATL-hub fuzzy relatedness ONLY below a margin. Seed the store from FREE static
   assets (WordNet antonymy/hypernymy + FrameNet Perspective_on + a closed-class converse set + ConceptNet
   IsA/AtLocation/PartOf); SWEEP the abstain margin, the fuzzy-match threshold, the structured-vs-hub fusion weight.
   Copy the two-store COMPUTATION (structured relational edge signs; ATL hub supplies fuzzy relatedness). NO external LLM.
2. **Beats BOTH floors CI-separated on a MODERN gold, on event<->goal congruence, reported separately AND aggregated:**
   (a) the DISTRIBUTIONAL-HUB baseline = `bridging_inference` relatedness thresholded to a sign (the polarity-blind
   incumbent -- it MUST lose on the antonym/converse items); (b) an info-free SHUFFLED-KB twin (permute the structured
   edges, keep node set + counts). Gate on the floor's UPPER CI bound; recompute each floor on the item's OWN
   population; report CI half-width + null p95; NO number crosses populations.
3. **The SAME organ TRANSFERS to at least one OTHER consumer** -- spatial AtLocation / containment TYPE-membership OR
   temporal script/TYPE step-match -- demonstrated on THAT consumer's modern gold, beating its stateless floor with the
   same shuffled-KB twin LOSING CI-separated. This proves it is the shared SHAPE, not an OCC-only patch.
4. **NO-regress + the hub stays.** The structured matcher must not degrade any LIVE consumer where it abstains (the
   reader stays byte-identical with the matcher off), and the ATL hub is NOT removed (it remains the fuzzy fallback). A
   POSITIVE control the hub CANNOT get: a converse/antonym pair (win/lose) whose cosine relatedness is HIGH but whose
   SIGN is opposite -- the structured matcher gets it, the hub baseline cannot.
5. **Polarity isolated (a can-fail control).** On the antonym/converse SUBSET the hub baseline is at/below chance
   (rel(win,lose) ~= rel(sell,buy)) while the structured matcher is CI-separated above -- so the SIGN comes from the
   edge, not the similarity. Reconfirm on the modern gold's own population.
6. **One-screen summary:** structured-store source + provenance -> modern gold -> hub baseline -> shuffled-KB twin ->
   event<->goal margin + the SECOND-consumer margin (with CI half-width + null p95) -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the CLOSED-CLASS converse/antonym/role-filler slice clears BOTH floors
CI-separated on affect AND transfers to spatial containment-type, but the OPEN-ENDED scene/type-inference tail
('stood on the podium' = won; kitchen is-a room via loose commonsense) is a distinct Talmy/Schank world-knowledge /
script organ the structured LEXICAL store does not cover -- enumerated with counts; the OCC SOLVED already located
this split into a closed-class lexical win + an open-ended scene residual"; OR "the affect slice clears but the
temporal script-step transfer does not, because the script schema's slots are event-TYPES the WordNet/FrameNet edges
do not name -- located and counted").

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated / landed -- do NOT rebuild):** `hdlab/bridging_inference.py` (the ATL-hub baseline +
  fuzzy-match fallback -- `.relatedness` / `.select`); `hdlab/occ_appraisal.py` + `hdlab/goal_register.py`
  (`track_status_thwart` `converse=True` + `FAILURE_VERBS`/`IRREG_PAST` -- the FIRST consumer's hook);
  `hdlab/spatial_relational_model.py` + `hdlab/location_register.py` (containment / AtLocation type -- transfer target
  A); `hdlab/temporal_script_schema.py` + `hdlab/temporal_reasoner.py` (script/type step-match -- transfer target B);
  `hdlab/meaning_foundation.py` (WordNet MFS signatures for the fuzzy match).
- **CONSUME (the measured payoff -- do NOT re-derive):** `experiments/exp_occ_converse_matching_v1.py` +
  `experiments/data/occ_converse_probe_v1.jsonl` + `data/exp_occ_converse_matching_v1/metrics.json` (the +0.417
  direction, twin loses).
- **Assets:** nltk WordNet + FrameNet (on the path); ConceptNet under `data/corpora/<name>/` with a pinned fetch
  script in `experiments/` if acquired. **Gold:** a MODERN event<->goal congruence gold + a MODERN gold for the second
  consumer (spatial SpaceEval/SpartQA or temporal TRACIE, on disk).
- **Motivation + fence:** the OCC SOLVED (section 5 polarity-blind; section 9a the converse layer; P2/P4 the
  cross-cutting KNOWLEDGE-ASSET lesson); the spatial + temporal SOLVEDs (the transfer consumers). Build in
  `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
  (the structured relational store COMPLEMENTS the ATL hub; relation polarity/typing is now a scored organ across
  affect + one other consumer, or a located negative naming the open-ended scene/type tail).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the +0.417 (0.417 -> 0.833) converse recovery, or rel(win,lose) ~= rel(sell,buy), as a MODERN
  benchmark result -- both were measured on a 12-item CONSTRUCTED converse gold / a probe inside an experiment cell.
  They NAME the direction and the wall; the bar requires a MODERN gold with the hub baseline + shuffled-KB twin + a
  SECOND consumer, floors recomputed on each item's own population. No number crosses scorers / populations.
- Do NOT rebuild the ATL hub or the OCC / goal / spatial / temporal organs -- all are landed. The deliverable is the
  SHARED structured matcher that COMPLEMENTS + feeds them, not a re-derivation of any of them.
- Do NOT FIT the converse/type table to the eval verbs (circular); do NOT REMOVE the hub fuzzy fallback (it is
  complementary); do NOT lean on a 19c corpus as load-bearing gold (BANNED 2026-09-06 -- a 19c number is informational
  only); do NOT use an external LLM at inference (the invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** Our reader judges outcomes by how RELATED words are, but "win" and "lose" (or "buy" and
"sell") are equally related while meaning the OPPOSITE -- so it cannot tell a goal MET from a goal BLOCKED, cannot
tell whether a "kitchen" is the "room" a question is about, and cannot tell whether "stood on the podium" is the
"winning" step of a race. Those are all STRUCTURED facts -- an opposite, a kind-of, a step-in-a-story -- that
relatedness cannot supply. Build one small, transparent lookup of those facts from free public word dictionaries (no
outside AI), so the reader can decide "opposites" or "a kind of" with certainty and fall back on the fuzzy
relatedness measure only when no exact fact applies. A small test already showed this recovers the right answer about
40 points more often. The job is to prove it on modern test text -- beating the relatedness-only baseline AND a
scrambled-dictionary version -- and to show the SAME lookup helps a second, different reader (places, or story
steps), so it is a shared tool, not a one-off patch.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the ATL hub is polarity-blind on the win/lose vs
sell/buy pair and that the OCC + goal organs expose the `converse=True` hook), reads the OCC / spatial / temporal
SOLVEDs in full, enumerates the structured relations each reasoner needs, seeds the structured store from free
WordNet + FrameNet (+ ConceptNet) assets with a held-out eval, builds the glass-box matcher (structured edge signs;
ATL-hub fuzzy fallback below margin) in `experiments/`, acquires a modern event<->goal congruence gold + a modern
gold for one transfer consumer (spatial containment-type or temporal script-step) each with a shuffled-KB twin, and
reports the margins over the distributional-hub baseline with CI half-width + null p95 and the polarity-isolation
control -- or a located negative naming the exact cause (most likely the open-ended scene/type-inference tail that
the closed-class lexical store does not cover). The deeper follow-on (named, not required) is the online script/
world-knowledge scene-inference organ for that open-ended tail.
