---
slug: gate_the_eventive_nominal_event_channel_by_context_wsd_event_vs_result
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the just-integrated joint front-end's eventive-NOMINAL event channel (a noun like "attack"/"construction"/"assistance" denotes the EVENT of its source verb) is the single biggest temporal survival lever (whole-subgraph survival 0.41 -> 0.73/0.78, NOUN-event recall 0.105 -> 0.703) but OVER-FIRES on polysemy ("building" the act vs the object) so precision drops 0.79 -> 0.65 and it landed DEFAULT-OFF -- build a glass-box, NO-LLM per-TOKEN context/WSD gate (REUSE the sense machinery) that decides, in context, whether THIS polysemous eventive nominal is the EVENT reading or the RESULT/OBJECT reading, so the nominal channel can turn DEFAULT-ON at the verb-only channel's precision.

**slug:** `gate_the_eventive_nominal_event_channel_by_context_wsd_event_vs_result` -- **opened:** 2026-09-07
by the strategy session. This is the meaning-channel follow-on named in the just-landing joint relation front-end's
SOLVED (`extract_relations...` NEXT STEPS P3): the eventive-nominal channel is that front-end's biggest survival lever,
but its precision cost is PURE POLYSEMY (a TOKEN-level sense choice, event vs result/object), NOT a type-level error,
and the syntactic shortcut (Grimshaw argument-structure as a precision gate) was DRILLED and FAILED. The fix belongs to
the MEANING channel (reuse the landed sense-selection organs), and it WIRES INTO the nominal channel of the p2 joint
front-end (forward reference -- p2 is landing now). **status:** CANDIDATE -- a BUILD + VALIDATION problem. You build +
validate in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `6` because it
> depends on the p2 joint front-end landing first (it gates that front-end's nominal channel), it is overwhelmingly
> REUSE of landed meaning-channel organs (low build risk), and the payoff -- converting the biggest temporal survival
> lever from a default-OFF liability into a safe default-ON gain -- is large but downstream of p2's own board-wiring.
> It sits below the recurrent-loop closure (`1`), the joint front-end itself (`2`), the parser (`3`), and the structured
> semantic matcher (`4`), and above the SDRT discourse reader (`7`). It stays CANDIDATE until p2 is owner-DONE and the
> nominal channel is live-wired. Set the real priority when promoted from CANDIDATE to OPEN.

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
Our reader just got much better at following a story's timeline, and the single biggest reason was learning to treat
certain NOUNS as happenings -- "the attack", "the construction", "the assistance" name an event just as much as a verb
does, and counting them roughly doubled how often the reader could follow a whole chain of what-happened-before-what.
But the same trick fires too eagerly. Some of those words have a second, NON-event meaning: "the building" can be the
ACT of building or the THING that was built; "a painting" can be the activity or the picture on the wall. When the
reader treats every such word as a happening it is right most of the time but wrong often enough that we had to leave
the whole improvement switched OFF. The fix is to look at each word IN ITS OWN SENTENCE and decide which meaning is
meant this time -- the event reading or the object reading -- and count it as a happening only when the sentence means
the event. Do that well and we can switch the big improvement safely on. A grammar-only shortcut (only count the word
if it is followed by "of something") was already tried and it backfired, because in the news these event-nouns usually
appear bare ("the attack killed 12"). So the decision has to come from meaning-in-context -- exactly the kind of
judgement the reader already has a part for, which is what we reuse here.

## 2. WHY THIS ONE
The eventive-nominal channel is the LARGEST single lever the just-landing joint relation front-end found for following
a story's timeline -- and today it is switched OFF because it costs precision. That is a measured defect, not a
hypothesis: the channel lifts whole-subgraph survival from 0.41 to 0.73/0.78 but drops precision 0.79 -> 0.65, and the
front-end's own SOLVED marks the enriched temporal pass DEFAULT-OFF and names "gate the nominal channel on the
context/WSD channel to recover the polysemy precision" as the wire that makes the gain a safe production default (its
NEXT STEPS P3). So this problem's first deliverable already exists as a number: the defect costs us the whole lever.
It is overwhelmingly REUSE -- the meaning channel already has the exact organ for "which sense of this word is meant in
context" (biased-competition sense selection over a curated sense hub), and the eventive-nominal test itself is a
WordNet sense check. The syntactic shortcut is a DRILLED negative (below), so the residual is proven to belong to the
meaning channel. It WIRES INTO the p2 joint front-end's nominal channel (a forward reference -- p2 is landing now), and
turning it on unstarves all three temporal-chain consumers at once.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Word-sense selection in context is BIASED COMPETITION / controlled semantic cognition:
  the anterior-temporal hub holds a word's competing senses and the LIFG/pMTG control network amplifies the context
  features that DISCRIMINATE the intended sense and suppresses the shared (topic) ones (Jefferies 2013; Lambon-Ralph et
  al. controlled semantic cognition 2017; Rodd 2002 shared-core polysemy). The event-vs-result reading of a polysemous
  nominal ("the building COLLAPSED" = the object; "the building OF the bridge" = the act) is one instance of that
  token-level selection, resolved by context, NOT by bare surface form. Also PINNED: a nominalization CAN denote the
  event of its source verb -- the ATL codes it as an event frame (Grimshaw 1990 argument-structure nominals; Frankland
  & Greene 2015). Comprehension is UNDERSPECIFIED-BY-DEFAULT (Frisson 2009 good-enough): the reader commits the shared-
  core / coarse reading and elaborates on demand -- which is exactly what a fire/no-fire event gate needs (event cluster
  vs object cluster), not a fine synset.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The abstention / confidence threshold at which a token is gated IN
  as an event (SWEEP -- the reader's own precision/recall trade); the mapping of the sense reader's coarse-cluster
  distribution mass (event/act/process vs object/artifact/group/location) onto a binary fire decision; whether to abstain
  TO-FIRE or abstain-TO-DROP when the context is out-of-vocabulary; the diagnostic-context precision knobs (gamma, topk)
  and the frequency log-prior (sense_prior/prior_weight) already present in `diagnostic_context_wsd`; the choice of
  vector space feeding the readout. All parameters to sweep, never fixed numbers.
- **NOT brain-faithful (do NOT do).** The Grimshaw argument-structure SYNTACTIC gate (fire only on an "of"/"by"
  complement or possessive) -- DRILLED and FAILED here because news event-nominals appear BARE; a TYPE-level lexicon that
  fires/drops a lemma regardless of the token's context (the error is TOKEN-level -- the SAME lemma is an event in one
  sentence and an object in another); an external LLM at inference; treating the ungated survival lift (0.73/0.78) as
  this problem's result (it is the precision-costly, default-off channel this must make safe).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk in the p2 joint front-end SOLVED -- REUSE, do not re-derive):**
  - The eventive-nominal channel is the single biggest temporal survival lever. Detected by `_is_event_noun`
    (`experiments/_joint_relation_frontend.py`): a NOUN is eventive iff a top-3 WordNet synset has lexname in
    {noun.act, noun.event, noun.process, noun.phenomenon} AND is DEVERBAL (a derivationally-related verb). Whole-subgraph
    survival TB-Dense 0.4054 -> **0.7327**, MAVEN-ERE 0.4134 -> **0.7766**; NOUN-event recall **0.105 -> 0.703**.
  - The precision COST is PURE POLYSEMY, TOKEN-level. Precision 0.79 -> 0.65 (TB-Dense 0.787 -> 0.690) from senses like
    "building" (act vs object); it does NOT hurt the reasoner's conditional accuracy (0.583 vs 0.598 -- coverage rises
    for free). The channel is landed DEFAULT-OFF for exactly this reason.
  - The SYNTACTIC shortcut is a DRILLED NEGATIVE. Grimshaw's argument-structure diagnostic as a precision gate
    (`exp_joint_third_reasoner_and_nominal_wsd_v1.nominal_wsd_drill`, arm `nom_wordnet_grimshaw`) raised precision
    0.652 -> 0.767 but CRUSHED NOUN-event recall **0.703 -> 0.201** -- so the residual is SEMANTIC/contextual, evidence-
    backed, NOT syntactic.
  - The meaning channel already SOLVES token-level sense selection on its own instrument (REUSE): the biased-competition
    diagnostic-context readout (`hdlab/diagnostic_context_wsd`, a_s +0.0389/+0.0430 CI-sep, shuffled-diagnosticity twin
    LOSES); the frozen curated sense hub (`hdlab/meaning_foundation`, rare-sense a_s +0.0755 CI-sep); the underspecified
    sense reader (`hdlab/underspecified_sense_reader.select_sense`, commit the COARSE cluster, +0.169 CI-sep over coarse-
    MFS + a context-shuffle twin). `select_sense` returns `coarse` = the WordNet lexname supersense of the winning sense
    -- i.e. it already tells you whether the committed reading is noun.act/event/process vs noun.artifact/object/group.
- **INFERRED (you must prove):** that a per-TOKEN context/WSD gate over the polysemous eventive-nominal tokens
  (run the biased-competition readout over the token's candidate senses in its sentence, fire the NOM event only when the
  committed reading is the EVENT/ACT/PROCESS cluster) RESTORES precision toward the verb-only channel's level WHILE
  keeping the survival/recall lift (near the ungated 0.73/0.78 -- report how much is retained), CI-separated over the
  UNGATED nominal channel AND over an info-free shuffled-sense twin, on TB-Dense AND MAVEN; OR a rigorous LOCATED
  NEGATIVE with the cause named and counted (e.g. the curated hub / w2v space does not cover the senses of N of M over-
  firing nominal lemmas so the gate abstains and the survival lift falls back to X -- a sense-signature COVERAGE
  bottleneck, a distinct upstream organ; OR the event-vs-result reading of this noun class sits below the readout's
  ~0.35 glass-box ceiling -- located and counted).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the eventive-nominal detector (`_is_event_noun`) -- it is p2's, landing via the joint front-end. You
  are GATING its per-token output, not re-deriving the WordNet eventive test.
- Do NOT re-run the Grimshaw argument-structure SYNTACTIC gate as the fix -- it is a DRILLED negative (precision
  0.652 -> 0.767 but NOUN-event recall 0.703 -> 0.201, bare event-nominals). It is the very evidence that the residual is
  semantic; re-deriving it is not progress.
- Do NOT re-derive the biased-competition readout, the curated sense hub, or the underspecified sense reader -- all are
  landed (`build_sg_lite...`, `build_and_freeze_the_clean_curated_knowledge_foundation...`,
  `select_word_sense_by_context_primed_biased_competition...`, all owner-DONE). REUSE them.
- Do NOT re-measure the UNGATED survival lift (0.41 -> 0.73/0.78) and call it done -- that is p2's motivating measurement
  of the precision-costly channel; the bar is the GATED precision/recall/survival TRIPLE.
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold, and do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "nominal"`
  / `"eventive"` / `"wsd"` / `"sense"` / `"polysemy"` / `"disambiguation"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`; skim `hdlab/` so you build
  ON the existing meaning-channel organs, not beside them.
- READ IN FULL (build ON it, credit it): `notes/problems/extract_relations_from_prose_whole_subgraph_survival_the_
  shared_reasoner_bottleneck/SOLVED.md` -- Sec 4b "Eventive-NOMINAL detection" (the single biggest lever + the polysemy
  precision residual), the "NOMINAL precision residual is SEMANTIC, not syntactic (drilled negative)" bullet, and NEXT
  STEPS **P3** (this problem). Then the meaning-channel SOLVEDs you REUSE: `build_sg_lite_self_supervised_scale_
  generative_sense_predictor`, `build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift`,
  `select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub`, and (for the readout ceiling)
  `break_the_contextual_input_encoding_ceiling_for_specific_sense_selection`.
- INSPECT what you REUSE: `hdlab/underspecified_sense_reader.py` (`select_sense` -- returns `coarse`=lexname supersense,
  `fine`, `confidence`, `distribution`; `default_vec_lookup`); `hdlab/diagnostic_context_wsd.py`
  (`diagnostic_context_scores` / `pick_sense` / `diagnostic_query` + the `gamma`/`topk` precision knobs, `shuffle_rng` =
  the info-free twin, `sense_prior`/`prior_weight` = the frequency log-prior); `hdlab/meaning_foundation.py`
  (`sense_signatures` / `sense_signature` / `covers` -- the frozen curated candidate-sense source); and the nominal
  channel in `experiments/_joint_relation_frontend.py` (`_is_event_noun`, `joint_event_ranks(..., nominal=True)`).
- ENUMERATE the over-firing population (an absence/precision claim requires an enumeration, not a search): run the
  nominal channel on TB-Dense + MAVEN, collect the NOM-fired tokens that are gold NON-events, group them by lemma. That
  set (event-vs-result polysemous nouns -- "building", "painting", etc.) is exactly what the gate must resolve. State in
  your submission how you enumerated it and its size.
- CHECK THE WIRING TARGET: p2 lands as `hdlab/joint_relation_frontend.py` with the nominal channel; this gate wires
  INTO that channel (fire a NOM event only if the gate approves). If that module is not yet on disk, build against
  `experiments/_joint_relation_frontend.py` and forward-reference the wire in your proposed diff (p2's SOLVED Sec 7 diff
  item 2 already reserves it: "Gate the nominal channel on the context/WSD channel to recover the polysemy precision").
- READ the audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- the MEANING/WSD tier and the TIME sec.2b eventive-nominal entry
  (the nominal channel is the biggest lever with a POLYSEMY precision residual = "the context channel's job").
- GOLD: TB-Dense (`experiments/_tbdense_loader.py`) + MAVEN-ERE (the p2 loaders) -- the SAME MODERN populations p2 used,
  so precision/recall/survival are comparable to p2's numbers. You are PRE-AUTHORIZED to acquire an additional open
  MODERN gold under `data/corpora/<name>/` with a pinned fetch script + provenance if you need more polysemy coverage.
  Do NOT lean on 19c.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box, NO-LLM per-TOKEN WSD gate (built + validated in `experiments/`; strategy lands the hdlab change,
   Q111).** For each polysemous eventive-nominal token the detector fires, run the biased-competition sense readout over
   its candidate WordNet senses IN CONTEXT (REUSE `underspecified_sense_reader.select_sense` and/or
   `diagnostic_context_wsd` over `meaning_foundation.sense_signatures`) and fire the NOM event ONLY when the committed
   reading is the EVENT/ACT/PROCESS cluster (coarse lexname in the eventive set), not an object/artifact/group/location
   cluster. Copy the biased-competition COMPUTATION; SWEEP the abstention/confidence threshold + gamma/topk + the
   fire-vs-drop abstention direction (phase-diagram). NO external LLM.
2. **The WSD-gated nominal channel keeps the lift AND restores precision, CI-separated over the UNGATED channel, on
   MODERN gold (TB-Dense + MAVEN, the SAME populations p2 used), reported per-gold AND aggregated.** Report the
   precision / recall / whole-subgraph-survival TRIPLE for: verb+copular only, ungated nominal, and WSD-gated nominal.
   The gated arm must retain survival/recall NEAR the ungated 0.73/0.78 (state the fraction of the lift retained) WHILE
   precision rises toward the verb-only channel's level. The FLOOR is the UNGATED nominal channel recomputed on the SAME
   population (the precision-costly incumbent this must beat on precision without losing survival); gate on the floor's
   CI. Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses populations.
3. **The info-free twin LOSES CI-separated:** shuffle the sense signatures / the diagnosticity weights (`shuffle_rng`),
   and/or score the token against a RANDOM other sentence's context, keeping shapes/balance -- this proves the gate uses
   THIS token's context, not a shape artifact.
4. **NO-regress + a positive control the type rule cannot get.** The gate is ADDITIVE: with it off the nominal channel
   is byte-identical, and the verb/copular channels + the three temporal-chain consumers are untouched (enumerate live
   consumers). The positive control: the SAME lemma fired as an event in one sentence (event reading) and dropped in
   another (object reading) -- a TYPE-level lexicon cannot pass this, a token gate can.
5. **The abstention band is isolated (load-bearing, not free).** Show the swept threshold matters: a too-permissive
   setting collapses to the ungated precision, a too-strict one collapses toward the Grimshaw recall crash -- so there
   is a real operating point that keeps survival while restoring precision, reconfirmed on each gold's own population.
6. **One-screen summary:** over-firing token population (with counts) -> gold + provenance -> ungated-nominal floor ->
   twin -> the precision/recall/survival triple (with CI half-width + null p95) -> threshold sweep -> what breaks ->
   verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the WSD gate restores precision CI-separated on TB-Dense but the curated hub /
w2v space covers the senses of only N of M over-firing nominal lemmas, so the gate ABSTAINS on those tokens and the
survival lift falls from 0.73 to X -- the bottleneck is sense-signature COVERAGE of these nominals, enumerated with
counts, a distinct upstream organ (the knowledge-foundation import factory)"; OR "the event-vs-result reading of the
residual nominals sits below the biased-competition readout's ~0.35 glass-box ceiling -- the contextual-input-encoding
wall, located and counted, a different fork").

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated / landed -- do NOT rebuild):** `hdlab/underspecified_sense_reader.py` (`select_sense`,
  `default_vec_lookup`, `coarse_cluster`); `hdlab/diagnostic_context_wsd.py` (`diagnostic_context_scores`, `pick_sense`,
  `diagnostic_query`, the gamma/topk/shuffle_rng/sense_prior knobs); `hdlab/meaning_foundation.py` (`sense_signatures`,
  `sense_signature`, `covers`).
- **WIRE INTO (forward reference -- p2 landing now):** `hdlab/joint_relation_frontend.py` -- the nominal channel
  (`joint_event_ranks(..., nominal=True)`, `_is_event_noun`). Build against `experiments/_joint_relation_frontend.py`
  until it lands; propose the gate as an additive, default-off (then default-ON once proven) hook on that channel.
- **CONSUME (the measured payoff + the drilled negative -- do NOT re-derive):**
  `experiments/exp_joint_third_reasoner_and_nominal_wsd_v1.py` (`nominal_wsd_drill` -- the ungated precision/recall and
  the DRILLED Grimshaw gate); `experiments/_tbdense_loader.py` + the MAVEN loader (the same modern golds).
- **Gold:** TB-Dense + MAVEN-ERE on disk via the p2 loaders (MODERN, same populations as p2). Acquire an extra modern
  gold under `data/corpora/<name>/` with a pinned fetch script only if you need more polysemy coverage.
- **Motivation + fence:** the p2 joint front-end SOLVED (Sec 4b + NEXT STEPS P3); the audit MEANING/WSD tier + TIME
  sec.2b. Build in `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into the MEANING/WSD tier + TIME sec.2b (the
  eventive-nominal channel is now safe to default-ON at verb-only precision, or a located coverage/ceiling negative).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the ungated survival 0.41 -> 0.73/0.78 (or NOUN-event recall 0.105 -> 0.703) as THIS problem's result --
  it is p2's MOTIVATING measurement of the precision-costly, default-off channel. The bar is the GATED precision/recall/
  survival triple, with the ungated channel as the floor. No number crosses scorers / populations.
- Do NOT re-run the Grimshaw argument-structure SYNTACTIC gate as the fix -- it is a DRILLED negative (precision up but
  NOUN-event recall 0.703 -> 0.201). It is the evidence that the residual is semantic, not a route to reopen.
- Do NOT re-derive the biased-competition readout, the curated hub, the underspecified sense reader, or the eventive-
  nominal detector -- all are landed. The deliverable is the per-TOKEN GATE that composes them onto the nominal channel.
- Do NOT gate at the TYPE level (fire/drop a lemma regardless of context) -- the error is TOKEN-level and a type rule
  cannot pass the positive control (same lemma, two readings). Do NOT lean on a 19c corpus as load-bearing gold (BANNED
  2026-09-06 -- a 19c number is informational only); do NOT use an external LLM at inference (the invariant). Strategy
  owns any hdlab landing.

---

**TLDR (plain English):** Our reader recently got much better at following a story's timeline by treating certain nouns
("the attack", "the construction") as happenings -- the single biggest improvement it found. But some of those words
have a second, non-event meaning ("the building" can be the act OR the thing built), so the reader over-counts and we
had to leave the whole improvement switched off. The job is to look at each such word in its own sentence and decide
which meaning is intended, counting it as a happening only when the sentence means the event -- using the meaning-in-
context part the reader already has. A grammar-only shortcut was already tried and backfired (these words usually appear
bare in the news). Get the in-context judgement right and we can switch the biggest timeline improvement safely on.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (read the p2 SOLVED Sec 4b + P3 and the meaning-channel SOLVEDs
in full; confirm `select_sense` returns the coarse event-vs-object cluster and that the nominal detector is p2's),
enumerates the over-firing event-vs-result nominal tokens on TB-Dense + MAVEN, builds a per-token biased-competition
gate in `experiments/` that fires a noun-event only when the committed reading is the event cluster (sweeping the
abstention threshold + gamma/topk), and reports the precision/recall/survival triple against the ungated nominal channel
with an info-free shuffled-sense twin -- or a located negative naming the exact cause (most likely sense-signature
coverage of these nominals). It wires the gate INTO the p2 joint front-end's nominal channel so the biggest temporal
survival lever can turn default-ON.
