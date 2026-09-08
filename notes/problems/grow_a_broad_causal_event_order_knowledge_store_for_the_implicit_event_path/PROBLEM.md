---
slug: grow_a_broad_causal_event_order_knowledge_store_for_the_implicit_event_path
status: INTEGRATED
review: EXCELLENT
review_text: Reverified 8/8 first-hand. Broader tense-agnostic-mined store (454k verb-pairs) lifts TRACIE implicit-event ordering 0.5296->0.5655 (+0.0359 CI-sep), coverage 0.29->0.607, twin loses, narrated path byte-identical. Deep story-conditioning ceiling finding + 2 located negatives. Store-swap wire (reasoner implicit branch) tracked as the realization.
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-09-08; store-swap wire tracked as the realization)
> Reverified FIRST-HAND **8/8** (`verification/test_broaden_causal_order_store.py`): tense-agnostic re-mine recovery 2.06x (0.339->0.699); broader coverage 0.590>seed 0.295; broader acc 0.5650>seed 0.5275; shuffled-order twin 0.49 collapses (order load-bearing); narrated path byte-identical under store swap; positive control (41 pairs the seed abstains on).
> **What makes it excellent:** it correctly LOCATED the seed store's limit as an UPSTREAM front-end gap (a tense-GATED offline mine), not a small corpus -- and proved the 4.9% corpus lever the brief guessed is the SMALL one, the extraction fix is the big one (coverage 2.1x). Re-mining 98,161 ROCStories through the ALREADY-LIVE tense-agnostic detector -> 454,129 ordered verb-pairs (seed 177,800) through the consolidation gate; TRACIE n=1924 ungated 0.5655 vs seed floor 0.5296 (+0.0359 CI[+0.0117,+0.0616] CI-sep), vs abstain +0.0655, twin loses +0.0759 CI-sep; both coverage AND per-pair accuracy hold-or-lift.
> **Volunteered against itself + drilled DEEP (owner "why 0.61 not 0.94?"):** the ceiling is STORY-CONDITIONING, measured not asserted -- the aggregate store IS the context-free SCRIPT PRIOR (Schank-Abelson), right when a story follows its script (~60%), wrong on the ~40% deviations; closing that needs READING the implicit event's context (a categorically deeper mechanism, not a fidelity bug). Field-corroborated (Chambers-Jurafsky "typical not causal"; McKoon-Ratcliff online causal-link limit; SymTime needs 3.5M distant examples for 0.80).
> **What did not reproduce under my check:** nothing -- 8/8 held.
> **FULL FIX/PROTOTYPE INVENTORY tracked (ledger CONT-26; owner directive):** (1) FIX broader store (454k) + wire to the reasoner's implicit branch as a strength-gated override [realization, tracked]; (2) UPSTREAM the tense-agnostic extractor = the real coverage lever (already LIVE; this is an offline-mine fidelity fix); (3) LOCATED NEGATIVE transitive closure (coverage up, tail-accuracy chance); (4) LOCATED NEGATIVE causal-cue directional blend (+0.001, ROCStories connective-sparse); (5) the confidence gate (reasoner's `SCRIPT_M_MIN`) is the speed-accuracy SAT dial (margin up -> per-pair up, coverage down); (6) brain-fidelity: tense-agnostic detection = Zwaan-Langston-Graesser event-indexing (time is a CUE not a GATE); aspect = graded confidence feature not a filter; causal typing partially grounded (do not over-claim).
> **AUDIT UPDATE folded (§2b):** the script/event-order store's ceiling is context-free script-prior (~0.61-0.68 per-pair); the residual is story-grounded instance-order needing the implicit event's context. **status:INTEGRATED, priority 12 dropped.** **Realization (tracked): rebuild the 454k store asset offline + point `hdlab/temporal_reasoner` implicit branch + `hdlab/temporal_script_schema` at it (narrated path byte-identical; blast radius = the implicit branch only).**

# PROBLEM: the landed script/schema store that would place UNNARRATED events on the timeline is LATENT and thin -- it covers only ~29% of implicit-event verb-pairs at 0.60 and no reader consumes it, so the temporal reasoner ABSTAINS ("unknown -- needs world knowledge") on implicit-event ordering; GROW a BROADER glass-box CAUSAL / EVENT-ORDER knowledge store (irreversibility / entropy-typed verb-pair order, mined offline from more narrative + causal-cue corpora through the PROVEN consolidation gate) and WIRE it to the reasoner's implicit-event / abstention path as a strength-gated override on the iconicity default, and prove it lifts implicit-event ordering CI-separated over the current abstention AND the seed store's own floor on a modern gold, info-free twin LOSING, narrated-event path byte-identical.

**slug:** `grow_a_broad_causal_event_order_knowledge_store_for_the_implicit_event_path` -- **opened:** 2026-09-07 by the
strategy session. This is the named follow-on the temporal-reasoning SOLVED handed off (`reason_over_event_time_order_and_duration_on_a_modern_gold`, §NEXT-STEPS P5): the seed script/schema organ (`hdlab.temporal_script_schema`, 177,800
Chambers-Jurafsky ROCStories verb-pair orders) is landed but LATENT and covers only ~29% of TRACIE implicit-event pairs at
0.60, and the live temporal reasoner returns "unknown -- needs world knowledge" on the rest. **status:** CANDIDATE -- a BUILD +
VALIDATE + WIRE problem that REUSES the seed store + the consolidation gate + the typed-foundation loader; it does not re-propose
them. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, NO external LLM at inference OR
in gold construction (the invariant) -- every source is a curated / narrative corpus, mined OFFLINE through the gate.

> **THIS PROBLEM IS SCOPED INSIDE THE UMBRELLA `expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate` (INTEGRATED).** That umbrella is "grow the foundation with CLEAN / TYPED / CORRECTLY-RESOLVED world knowledge
> through the gate"; THIS is a concrete instantiation of its EVENT / SCRIPT knowledge type -- causal / event-order knowledge for
> the implicit-event path. REUSE the umbrella's machinery (the consolidation gate + the typed-foundation north star); do not
> re-propose it. The one distinction that must not blur: querying a raw dump AT INFERENCE is BARRED; INGESTING narrative/causal
> knowledge OFFLINE through the consolidation/prune gate into a frozen typed store is the brain's own mechanism (systems
> consolidation), admissible, glass-box. This problem is entirely the second thing.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `12`, a free rank just
> after its umbrella parent (`...consolidation_gate`, filed 11) and clear of the contested 1-10 band held by the modern-board
> rebuild, the meaning-channel live-wire, and the reasoning-phase builds. It is a real BUILD (broaden the store + type it +
> wire it), not pure wiring, and it is subordinate to its umbrella -- so it sits behind the contested reasoning/board work, not
> inside it. It is HIGH-leverage on ONE narrow axis: it turns a LATENT organ live and unstarves the reasoner's implicit-event
> abstention. Set the real priority when promoted from CANDIDATE to OPEN.

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
Stories often leave out the obvious steps: "She paid and left the restaurant" never says she ordered, ate, and got the bill --
but a reader knows those happened, and in what order, because they know how the world works (you break an egg before you cook
it, not after; you can't unscramble it). Our reader recently learned to work out the order of events a story actually tells,
and to say "I don't know -- that needs world knowledge" when an event is only implied. We even built a small store of "which
kind of event usually comes before which" by reading a hundred thousand short stories -- but it only knows about one implied
pair in three, it is often wrong on the harder ones, and nothing in the live reader actually uses it, so today the reader just
says "I don't know" on most implied-order questions. This job is to GROW that store much broader -- read more stories and, in
particular, learn the CAUSE-and-effect and can't-be-undone direction of events -- and plug it into the reader so that, where it
used to shrug, it now gives a confident, explainable answer; and prove that the bigger store answers more implied-order
questions, and more of them correctly, than both "shrug" and the small starter store -- with a scrambled-store version
falling apart so we know the real cause-and-order structure is doing the work. No outside AI does the reading.

## 2. WHY THIS ONE
The temporal-reasoning SOLVED PROVED the narrated timeline (before/after 0.5933 vs iconicity 0.5236 CI-sep on modern newswire;
overlap; relative duration) and EXPLICITLY scoped implicit-event ordering as a SEPARATE knowledge organ -- built the seed
(`temporal_script_schema`, 177,800 ROCStories verb-pair orders, 0.6022 on the covered 29% of TRACIE vs chance 0.500 and the
story-internal reader's 0.478) and left "richer script induction for the TRACIE tail" as its named P5 next-problem. That seed
is LATENT (no read()-time consumer) and thin (29% coverage), and the live reasoner ABSTAINS ("unknown -- needs world
knowledge") on implicit-event queries -- so on the ~71% of implicit pairs the seed does not cover, the reader has NO answer.
This is the highest-leverage move to turn a landed-but-dormant organ live and unstarve the reasoner's abstention path, and the
METHOD is proven (mine narrative chains through the consolidation gate), not hypothesized. Test 4 (does a NUMBER show the
DEFECT costs us?): YES with a caveat, stated honestly -- the reasoner's ABSTENTION on ~96%-implicit-event TRACIE (measured
3.8% story-internal) is the defect's cost (no answer where the brain answers confidently), and the seed's 0.60@29% is the
floor to beat; the RISK to guard (same shape as the refuted `flat_store`) is treating the seed's 0.60 as the cost rather than
the abstention -- so the FIRST deliverable is the per-population enumeration of covered-vs-abstained implicit pairs (§6).

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Comprehension assumes ICONICITY by default -- order-of-mention approximates order-of-events
  (Zwaan's chronological / iconicity assumption; this IS the temporal reasoner's iconicity floor). When events are NOT narrated
  in order, or one is UNNARRATED (implicit), the reader infers order from CAUSAL and IRREVERSIBILITY world knowledge:
  **Trabasso's causal-network model** of narrative comprehension (events are linked by enabling / causing relations and the
  reader traverses that network to place unstated steps), and the **arrow-of-time / entropy irreversibility** prior over event
  types (you break before you cook; you cannot unscramble) -- a DIRECTIONAL knowledge accumulated across many stories (Schank &
  Abelson 1977 scripts; Chambers & Jurafsky 2008 narrative event chains -- the seed store's own method). The load-bearing
  property: this causal / irreversibility knowledge is a **STRENGTH-GATED OVERRIDE** -- it fires only when confident, overriding
  the iconicity default; otherwise the reader falls back to iconicity or abstains. The seed store is the flat aggregate
  verb-pair-order statistic; the brain-faithful extension is to TYPE those orders by causal / irreversibility STRENGTH so the
  override is confidence-gated, not a flat lookup.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** Which corpora to mine (more narrative + causal-cue corpora); the causal-cue
  set (connectives + result / enable frames that mark a directional link); the irreversibility / entropy typing (how to score a
  verb-pair's directional strength); the override confidence threshold vs iconicity; the consolidation-gate params that admit a
  verb-pair; and every substrate operating-point knob. SWEEP these, adopt no number.
- **NOT brain-faithful (do NOT do).** An external LLM / learned seq2seq event-order model at inference (the invariant); admitting
  RAW reading-derived co-occurrence straight into the store (the north star: raw admission REGRESSES the meaning channel -0.033;
  only consolidated / typed helps +0.067 -- everything passes the gate); a FLAT lookup with no confidence gate (the brain
  overrides iconicity only when confident); densifying with contiguity + plausibility and reading Story-Cloze as causal-chain
  proof (the causal SOLVED's located negative -- Story Cloze is affect-dominated, a topical baseline is ~chance); a 19c corpus
  as load-bearing gold (BANNED 2026-09-06 -- informational only).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - SEED store `hdlab.temporal_script_schema` (landed, owner-DONE, Q111): mined 98,161 ROCStories -> 177,800 ordered verb-pairs;
    on TRACIE implicit-event it scores 0.6022 on the covered **29%** vs chance 0.500 and the story-internal register's 0.478.
    **LATENT:** no reader consumes it at read() time -- it abstains (None) with no live wire. (SymTime reaches 0.80 only with
    ~3.5M distantly-supervised examples; a glass-box chain mine gets 0.60.)
  - The live `hdlab.temporal_reasoner` returns **"unknown -- needs world knowledge"** on implicit-event queries (per-judgment
    signal-class provenance); TRACIE is ~100% implicit-event by design (measured 3.8% story-internal) -- so the reasoner
    structurally cannot place those events from the narrated timeline. That abstention is the defect.
  - The NARRATED before/after channel is SOLVED on modern newswire (0.5933 vs iconicity 0.5236 CI-sep; cue channel 0.909) -- do
    NOT reopen it (the story-internal path is at/near the human-agreement noise ceiling for these judgments, per the SOLVED).
  - `hdlab.consolidation_gate` (owner-DONE): RAW reading-derived admission REGRESSES the meaning channel (a_s -0.033 below
    gloss); only a CONSOLIDATED (recurrence + multi-seed + PPMI + schema-margin) set is safe (+0.067 CI-sep, raw twin LOSING).
    Every mined association must pass through it.
  - `hdlab.generalized_event_knowledge` (FORWARD GEK, owner-DONE): a DISTINCT sibling -- graded FORWARD continuation
    discrimination (Story Cloze 0.5922 val, ties a 1-step co-occurrence counter). It is a NEXT-event generator, not a
    before/after ORDER store. Not this problem (fence, §5).
- **INFERRED (you must prove):** that GROWING the seed verb-pair-order store (more narrative + causal-cue corpora + causal /
  irreversibility typing, all admitted through the consolidation gate) and WIRING it to the reasoner's implicit-event /
  abstention path as a strength-gated override raises implicit-event / abstained-pair ordering -- BOTH coverage and accuracy --
  CI-separated over BOTH the abstention baseline AND the seed's 0.60@29% floor on a MODERN gold, with a shuffled-store info-free
  twin LOSING and the narrated path byte-identical; OR a rigorous located negative naming the residual with counts (e.g.
  "coverage lifts 29% -> N% CI-sep but accuracy on the new tail ties chance because the causal-cue mine admits topical
  co-occurrence the schema-margin gate does not catch, M of the new pairs -- a distinct gate-tightening lever"; or
  "irreversibility typing lifts physical-state verb-pairs but social / mental-event order needs a distinct commonsense KB, N of
  M -- a distinct ATOMIC-style organ").

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the temporal reasoner's NARRATED channels (before/after / overlap / relative duration) -- SOLVED + INTEGRATED
  (`hdlab.temporal_reasoner`). This problem feeds its IMPLICIT-EVENT / abstention path ONLY, and keeps the narrated path
  byte-identical. Read the temporal SOLVED in full and REUSE its script/schema organ + provenance design.
- Do NOT just re-mine ROCStories the same way and call it converged -- the seed already did (177,800 pairs, 29% coverage,
  0.6022). The levers are BROADER COVERAGE (more narrative corpora) + CAUSAL / IRREVERSIBILITY TYPING + the CONFIDENCE-GATED
  override, not re-running the same flat mine.
- FENCE -- do NOT build a generative next-event SIMULATOR: that is the FORWARD GEK organ
  (`hdlab.generalized_event_knowledge`, owner-DONE `predictive_inference_forward_project_the_next_event_and_state_from_the_situation_model`). THIS is a STATIC before/after ORDER store, not a forward rollout.
- FENCE -- do NOT build the narrated-order-correction discourse READER: that is
  `sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose` (filed, priority 7 -- reads a
  passage and corrects narrated order via discourse relations). THIS is a knowledge STORE that answers where the reasoner
  abstains. (They are complementary -- the STRETCH couples them, §7 -- but do not duplicate the reader here.)
- Do NOT admit RAW co-occurrence into the store (regresses -0.033); every mined association passes the consolidation gate. Do NOT
  densify with contiguity + plausibility and score Story Cloze as causal-chain proof (the causal SOLVED's located negative --
  affect-dominated, topical ~ chance). Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold; do NOT use an external
  LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "script"` /
  `"schema"` / `"temporal"` / `"causal"` / `"irreversible"` / `"implicit"` / `"chain"` / `"order"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm `temporal_script_schema`
  is landed but LATENT (no read()-time consumer), the `temporal_reasoner` abstains ("unknown -- needs world knowledge") on
  implicit-event queries, and `consolidation_gate` + `meaning_foundation` are landed; skim `hdlab/` so you EXTEND the seed store
  and its gate, not build beside them.
- READ IN FULL (build ON them, credit them): `notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/SOLVED.md`
  (Wall 2 = implicit-event / TRACIE; the SCRIPT/SCHEMA organ = upgrade #5; the NEXT-STEPS P5 "richer script induction for the
  TRACIE tail"); `notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/PROBLEM.md`
  (the umbrella -- the consolidation-gate + typed-foundation north star this scopes inside); and
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b (the TIME dimension -- implicit-event ordering is a separate world-knowledge / script organ).
- INSPECT what you REUSE: `hdlab/temporal_script_schema.py` (the seed verb-pair-order store -- EXTEND it: more corpora + causal /
  irreversibility typing); `hdlab/temporal_reasoner.py` (the consumer -- WIRE the store into its implicit-event abstention path,
  as a strength-gated override on iconicity, narrated channels UNCHANGED); `hdlab/consolidation_gate.py` (the admission gate --
  every mined pair passes it); `hdlab/meaning_foundation.py` (the frozen-typed-static-asset LOADER pattern to follow);
  `hdlab/generalized_event_knowledge.py` (the FORWARD sibling -- confirm you are DISTINCT from it).
- CONSUME the seed mine + TRACIE harness (do NOT re-derive): `experiments/exp_temporal_reason_tracie_script_v1.py` (the ROCStories
  verb-pair mine + the TRACIE implicit-event scorer) -- generalize it to more corpora + the typed store + the coverage/accuracy split.
- ENUMERATE what the seed covers vs abstains (an absence claim requires an enumeration, not a search): for a sample of TRACIE
  implicit-event pairs, mark which the seed store covers (29%) vs abstains on, and SPLIT the uncovered into (a) verb-pair NOT in
  the mined corpus [the COVERAGE lever -- more corpora] vs (b) covered but WRONG order [the TYPING lever -- causal / irreversibility
  strength]. State how you enumerated in your submission.
- GOLD: TRACIE implicit-event on disk (`data/corpora/tracie/`); ROCStories (`data/corpora/roc_stories/`) is the seed corpus. You
  are PRE-AUTHORIZED to acquire MORE open MODERN narrative + causal-cue corpora under `data/corpora/<name>/` with a pinned fetch
  script in `experiments/` + a provenance note (a static offline foundation asset is admissible). Consider a narrative-order gold
  (a modern story-ordering / temporal-order set) as a second population. Do NOT lean on 19c (informational only).

## 7. THE BAR
PASSES only with ALL of:
1. **A BROADER glass-box causal / event-order KNOWLEDGE STORE, built + validated in `experiments/`** (strategy lands the hdlab
   change, Q111): the seed verb-pair-order store EXTENDED with (a) MORE narrative + causal-cue corpora [the coverage lever] and
   (b) CAUSAL / IRREVERSIBILITY / entropy TYPING of the verb-pair order [the confidence lever], every mined association ADMITTED
   THROUGH the consolidation gate (consolidated, not raw; the RAW twin must be shown to regress or be gated out). COPY the
   narrative-event-chain / causal-network computation; SWEEP the corpora, the cue set, the typing, the override threshold, every
   operating-point knob. NO external LLM.
2. **WIRED to the temporal reasoner's IMPLICIT-EVENT / abstention path** as a STRENGTH-GATED OVERRIDE on the iconicity default:
   where the reasoner today returns "unknown -- needs world knowledge", the store supplies a graded before/after WITH provenance
   (which corpus / cue / typing fired), and abstains honestly when below the confidence gate. Headline metrics: implicit-event /
   abstained-pair ordering **ACCURACY and COVERAGE**, CI-separated over BOTH (a) the current ABSTENTION baseline (no-answer /
   chance on those pairs) AND (b) the SEED store's 0.6022@29% floor recomputed on the SAME population, on a MODERN gold (TRACIE
   implicit-event and/or a narrative-order gold). Gate on the floor's UPPER CI bound; report CI half-width + null p95; recompute
   each floor on the item's OWN population; NO number crosses populations.
3. **The info-free twin LOSES CI-separated:** shuffle the store's verb-pair orders (or shuffle the causal / irreversibility
   typing), node set + counts kept -- the reasoner over the shuffled store collapses to chance, proving the EXTRACTED ORDER /
   CAUSAL STRUCTURE is load-bearing, not corpus frequency.
4. **The COVERAGE lever is named and measured.** The 29% coverage is the seed's wall; the broadened store must LIFT coverage
   (report 29% -> N%) AND hold-or-lift accuracy on the newly-covered tail -- report the coverage/accuracy tradeoff explicitly,
   with the covered-vs-abstained enumeration (§6) and the construction split (corpus-coverage vs typing). A can-fail POSITIVE
   control the seed CANNOT get: an implicit pair whose CAUSAL / irreversibility direction the typed store places correctly but
   the flat frequency lookup gets wrong or abstains on.
5. **NO-regress full-stack (FULL-STACK UPSTREAM).** Prototype THIS store AND its upstream (the shared front-end tagger the mine
   rides + the consolidation gate) all the way to EXCEL/EXCEED; then CONFIRM no other live consumer regresses -- the NARRATED
   before/after / overlap / duration channels stay BYTE-IDENTICAL (the store answers ONLY where the reasoner abstains), the
   meaning channel and any other gate consumer unchanged -- and note which consumers should be REVISITED to exploit the typed
   causal knowledge (e.g. the causal reasoner's edge weights, the SDRT reader's unmarked-causal inference).
6. **One-screen summary:** store design (corpora + cue set + typing + gate params) -> modern gold + provenance -> abstention +
   seed-0.60@29% floors -> shuffled-store twin -> implicit-event coverage + accuracy margins (CI half-width + null p95) over both
   floors -> the coverage / typing split -> upstream + downstream no-regress -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "coverage lifts 29% -> N% CI-sep but accuracy on the new tail ties chance because the
causal-cue mine admits topical co-occurrence the schema-margin gate does not filter, M of N new pairs -- a distinct
gate-tightening lever, filed"; OR "irreversibility typing lifts physical-state verb-pairs CI-sep but social / mental-event order
needs a distinct commonsense KB, N of M -- a distinct ATOMIC-style organ, filed").
**STRETCH (name it, do NOT require it):** feed the typed causal / irreversibility store to the SDRT discourse reader's
unmarked-causal inference (the "Max slipped / had spilt water" reversal is INFERRED from causal knowledge, the marker-only
version is a proven located negative) and/or the causal reasoner's edge weights -- report an aggregate arm if you reach it.

## 8. FILES AND ENTRY POINTS
- **REUSE / EXTEND (landed -- do NOT rebuild):** `hdlab/temporal_script_schema.py` (the seed verb-pair-order store -- broaden the
  corpora + add causal / irreversibility typing); `hdlab/temporal_reasoner.py` (the consumer -- wire the store into its
  implicit-event abstention path, narrated channels byte-identical); `hdlab/consolidation_gate.py` (the admission gate every
  mined pair passes); `hdlab/meaning_foundation.py` (the frozen-typed-static-asset loader pattern); `hdlab/generalized_event_knowledge.py` (the FORWARD sibling -- stay DISTINCT).
- **CONSUME (the seed mine + implicit-event harness -- do NOT re-derive):** `experiments/exp_temporal_reason_tracie_script_v1.py`
  (ROCStories verb-pair mine + TRACIE implicit-event scorer) -- generalize it to more corpora + the typed store + the
  coverage/accuracy split.
- **Gold:** `data/corpora/tracie/` (implicit-event) + `data/corpora/roc_stories/` (the seed corpus) on disk; acquire more open
  MODERN narrative + causal-cue corpora under `data/corpora/<name>/` with a pinned fetch script in `experiments/` + a provenance note.
- **Motivation + fence:** `notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/SOLVED.md` (the seed +
  P5 hand-off) + the umbrella `.../expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/PROBLEM.md`
  + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b (TIME). Build in `experiments/` + `verification/`; strategy lands any hdlab change
  (Q111). Heavy -> REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (implicit-event ordering: the LATENT script/schema store grown + wired + causal-typed, the
  abstention path answered on modern gold via a confidence-gated override -- or a located negative naming the residual organ).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the SEED's 0.6022 as an END-TO-END implicit-event capability -- it is the FLOOR to beat, on the covered **29%**
  only; the ~71% uncovered (where the reasoner abstains) is the measured gap. No number crosses populations.
- Do NOT quote the NARRATED before/after 0.5933 (vs iconicity 0.5236) as this problem's result -- that is the SOLVED narrated
  channel, at/near the human-agreement noise ceiling; this problem is ONLY the implicit-event (abstained) path.
- Do NOT quote SymTime's 0.80 as the target -- it uses ~3.5M distantly-supervised examples; the glass-box no-LLM bar is different
  (the seed's 0.60 is the comparable glass-box point).
- Do NOT quote a FORWARD-GEK number (Story Cloze 0.5922) as this store -- that is the generative next-event sibling, a different
  capability (fence).
- Do NOT re-do the narrated-order channel, build a generative next-event simulator, build the SDRT discourse reader (filed
  separately), admit RAW co-occurrence, densify + score Story-Cloze as causal proof, lean on a 19c corpus as load-bearing gold
  (BANNED 2026-09-06 -- informational only), or use an external LLM at inference (the invariant). Strategy owns any hdlab
  landing (Q111).

---

**TLDR (plain English):** Stories skip the obvious steps -- "she paid and left" leaves out ordering, eating, and getting the
bill -- and a reader fills them in, in the right order, because they know how the world works (you break an egg before you cook
it; you can't unscramble it). Our reader recently learned to order the events a story actually tells, and to say "I don't know --
that needs world knowledge" when a step is only implied. We built a small starter store of "which kind of event usually comes
before which" from a hundred thousand short stories, but it covers only one implied pair in three, is shaky on the hard ones,
and nothing in the live reader uses it -- so today the reader just shrugs on most implied-order questions. The job: grow that
store much broader (more stories, and specifically the cause-and-effect / can't-be-undone direction of events), plug it into the
reader so it gives a confident, explainable answer where it used to shrug, and prove the bigger store answers more implied-order
questions -- and more of them correctly -- than both "shrug" and the small starter store, with a scrambled-store version falling
apart so we know the real cause-and-order structure carries the load. No outside AI does the reading.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the seed script/schema store is landed-but-LATENT and the
reasoner abstains on implicit-event queries), reads the temporal SOLVED (Wall 2 + the script/schema organ + P5) and the
consolidation-gate umbrella in full, enumerates the covered-vs-abstained implicit pairs and splits the misses into
corpus-coverage vs causal/irreversibility-typing, grows the store from more narrative + causal-cue corpora through the
consolidation gate with causal / irreversibility typing, wires it into the reasoner's implicit-event abstention path as a
strength-gated override on the iconicity default, and reports implicit-event coverage + accuracy margins over both the abstention
baseline and the seed's 0.60@29% floor on a modern gold with a shuffled-store twin losing and the narrated path byte-identical --
or a located negative naming the exact residual (most likely a gate-tightening lever for topical causal cues, or a distinct
commonsense KB for social / mental-event order). The STRETCH (feed the typed causal store to the SDRT reader / the causal
reasoner) is named as the onward prize.
