---
slug: extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck
status: INTEGRATED
review: EXCELLENT
review_text: "INTEGRATED 2026-09-07 (strategy; owner_verdict DONE). Reverified 22 checks/7 witnesses first-hand + landing witness 6/6. Promoted hdlab/joint_relation_frontend.py (parse-once, tense-agnostic+copular temporal events; byte-identical core, no experiments dep) + wired behind joint_temporal_events/joint_nominal_events flags (DEFAULT-OFF, byte-identical when off: sm.events/timeline/causal_links/goals identical) + board_temporal_survival_dimension arm. Whole-subgraph survival 0.1111->0.4054 (+0.2943 CI-sep) -> +nominal 0.7327; live recall 0.3203->0.7562; end-to-end 0.0971->0.4937 (87% of ceiling); MAVEN 0.086->0.777. Committed 102641f3b (code) + notes, NOTHING pushed. DEFAULT-OFF = flip-on-find-the-break: ON is byte-identical for all board dims but regresses the W3 synthetic-OOD probe (joint UD parser weaker on throwaway sentences, not yet a strict superset of NLTK) -> flip-on enabler = UNION the NLTK aspect events with the joint-only events (a follow-on). Spatial NOT landed (located negative: construction coverage 74% not parse UAS 10%). Follow-ons: the UNION flip-on enabler; a live reader-consumer of the enriched temporal reasoner; p6 nominal-WSD-gate (filed); spatial construction+entity extractor; appraisal semantic-matching (=p4, filed)."
---

# PROBLEM: three reasoning organs are solved but STARVED -- build ONE glass-box RELATION-extraction front-end that lifts the SHARED relational structure they consume (spatial containment/position/path edges, temporal before/after/overlap links + the DROPPED copular/stative channel, and event->argument/role structure) from real MODERN prose, and prove it on WHOLE-SUBGRAPH SURVIVAL (every edge of a multi-hop chain, not per-edge recall) -- NO external LLM, glass-box.

**slug:** `extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck` -- **opened:** 2026-09-06
by the strategy session. This session integrated three inference organs -- `hdlab/spatial_relational_model.py`
(containment/position/path), `hdlab/temporal_reasoner.py` (before/after + Allen overlap + relative duration), and
`hdlab/occ_appraisal.py` (event x goal appraisal) -- and ALL THREE returned the SAME located negative: near-perfect on
GOLD relations, but end-to-end is capped because the reader extracts too FEW relations from real prose. The whole-brain
audit reached the same conclusion independently (`BRAIN_FOUNDATIONAL_AUDIT.md` sec.1: "the binding constraint is the
FRONT-END (event/role extraction), NOT the memory/retrieval stages"). This problem builds the front-end that unstarves
all three. **status:** CANDIDATE -- a BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab
change (Q111). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `2` (behind
> the recurrent-loop closure at 1) because it is the SINGLE shared bottleneck three independent, already-solved
> reasoners converge on -- the highest-fan-out lever the substrate has right now (one front-end unstarves spatial,
> temporal, AND appraisal reasoning at once), the defect is MEASURED not hypothesized (spatial chain survival 6/90;
> appraisal 0.94->0.06 as cues go sparse; temporal cue-sparsity ~12% + a dropped copular/stative channel), and the
> deeper parse it depends on is landed. It is a real BUILD (not pure wiring), so it sits below the loop-closure wire.
> Set the real priority when promoted from CANDIDATE to OPEN.

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
We just gave the reader three ways to think about a story: it can work out how things sit in space (what is inside
what, what is left of or above what, where someone ends up after moving), when things happen (before, after, at the
same time, how long), and how a character feels about an event given what they wanted. When we hand each of these
clean, correct facts, they all work almost perfectly. But when we let them read the actual story and pull out the
facts for themselves, they nearly always come up short -- because the step that turns sentences into those little
"X relates to Y" facts recovers only a small fraction of them. And a chain of reasoning needs EVERY link: to conclude
"the key is in the drawer" from "key in box" and "box in drawer" you must recover BOTH facts; miss either and the
whole conclusion is lost. So even when each single fact is recovered one time in five, a two-fact chain survives only
one time in twenty-five, and three-fact chains essentially never. That is why three separately-excellent reasoners all
stall on real prose in the same place. This job is to build the reading step that pulls those relationships out of
modern text well enough that whole chains survive -- and to prove it by measuring exactly that: not "how many single
facts did we get" but "how often did we get EVERY fact a multi-step answer needs". No outside AI does the reading; it
must be a transparent, inspectable mechanism.

## 2. WHY THIS ONE
This is the single defect the substrate's own evidence points at from three independent directions at once. Each of
the three just-solved reasoning organs delivered a rigorous LOCATED NEGATIVE with the SAME cause: the reasoner is
sound and brain-faithful on gold relations, and the end-to-end wall is text->relation EXTRACTION (spatial: chain
survival 6/90; appraisal: end-to-end 0.94 -> 0.06 as goal->outcome cues go from lexical to semantic; temporal: only
~12% of real pairs carry a cue the extractor reads, and the copular/stative overlap channel is DROPPED outright). The
whole-brain audit reached the identical conclusion by a different route: composed into a real reading task the
downstream organs work perfectly on clean inputs but the whole reader scores BELOW a trivial floor, "swamped by a
front-end that mislabels who-did-what-to-whom" -- so "the next lever is the front-end, not more downstream organs"
(`BRAIN_FOUNDATIONAL_AUDIT.md` sec.1). One front-end unstarves three reasoners; nothing else in the queue has that
fan-out. It is worth, if solved, the difference between three organs that pass in isolation and three organs that
comprehend real modern prose.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Comprehension builds a RELATIONAL structure from language at the syntax-semantics
  interface: hierarchical structure-building (Merge/parse) in left posterior IFG (BA44/45; Friederici 2011, 2017)
  hands a constituent structure to thematic-role / argument-structure assignment in posterior MTG and the anterior
  temporal lobe (Bornkessel-Schlesewsky & Schlesewsky eADM -- the extended Argument Dependency Model; Frankland &
  Greene 2015/2020 -- lateral-ATL codes structured "who did what to whom" role bindings). Meaning is composed via
  FRAMES: a predicate evokes a frame and BINDS its arguments to roles (Fillmore frame semantics; Jackendoff/Talmy
  Figure-Ground + Place/Path for spatial roles; Reichenbach/Allen for temporal endpoints). The load-bearing property
  for THIS problem: the brain extracts the relations of a clause JOINTLY in ONE structural pass -- a single parse
  yields the whole local subgraph (agent, patient, location, path, the interval endpoints, the containment nesting) at
  once -- it does NOT run N independent per-relation classifiers. That is exactly why WHOLE-SUBGRAPH survival is the
  right target: the brain's unit of extraction is the structured clause, not the isolated edge.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The cue-precedence and construction rules that map a parsed
  clause to each edge type (containment/position/path triggers, the aspect->interval endpoint rule, the copular/stative
  overlap detector, the goal->outcome role-filler match); the parse-robustness backstops; the abstention thresholds;
  and every substrate operating-point knob (parse-evidence density, closure depth, the sparse-vs-dense extraction
  regime) -- SWEEP these, do not adopt any number.
- **NOT brain-faithful (do NOT do).** An external LLM (or any learned end-to-end seq2seq relation extractor) at
  inference (the invariant); adding ONE more per-construction rule and calling it done (the spatial SOLVED measured
  per-construction returns DIMINISH -- the whole subgraph must survive, so isolated edges do not compound); scoring
  per-edge recall and reading it as end-to-end capability; a 19c corpus as load-bearing gold (BANNED 2026-09-06).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The three reasoners are near-perfect on GOLD relations and the wall is extraction (each SOLVED, owner-DONE):
    - SPATIAL (`reason_over_the_spatial_relational_model...`): reasoner 1.000 on all three types on gold; end-to-end
      over the reader's OWN extraction, `exp_spatial_extraction_recall_v1` measures containment recall 0.223,
      position 0.058, moves 0.024, and MULTI-HOP CONTAINMENT CHAIN SURVIVAL 6/90 = 0.067 (was 1/90 before an
      extraction upgrade). Its own KEY REALIZATION: "13% edge recall -> 1% chain survival" -- the exponent is the wall.
    - APPRAISAL (`infer_unstated_emotion_via_occ_appraisal...`): the OCC RULE is exact (oracle 1.000); a matched
      density phase-cut holds the rule at 1.000 while end-to-end falls 0.94 (dense cues) -> 0.06 (semantic goal->outcome),
      "the entire remaining gap is EXTRACTION density" (event<->goal semantic matching). `bridging_inference` is
      POLARITY-BLIND (rel(sell,buy) ~= rel(win,lose)) so similarity cannot sign the relation -- a role-filler match is
      needed.
    - TEMPORAL (`reason_over_event_time_order_and_duration...`): overlap was structurally impossible until an upstream
      fix recovered the DROPPED finite progressive; the biggest remaining real-prose OVERLAP lever is the COPULAR/STATIVE
      co-occurrence channel the verb-based extractor DROPS (its named P2 next-problem); before/after rides on cues
      present in only ~12% of pairs.
  - A SHARED relation front-end already partly exists and is LATENT: `hdlab/predicate_argument_frontend.py` (shallow SRL:
    agent/theme/goal/location/path/source/recipient/direction/instrument) is LANDED but DEFAULT-OFF in the live reader
    ("the live-reader routing ... is a queued careful follow-on"); on FrameNet gold it recovers five roles the inline
    rule scores 0.000 on, CI-separated. The spatial extractor (`experiments/spatial_relation_extractor.py`) and the
    temporal event front-ends (`experiments/_temporal_ordering.py` / `_temporal_ordering_multiframe.py`) are the
    current per-channel extraction paths; the deeper upstream is `hdlab/arc_parser.py` (UAS ~0.79) + `hdlab/pos_tagger.py`.
  - The audit's central, first-hand finding: the binding constraint is the FRONT-END (event/role extraction), and a
    brain-faithful verb-argument front-end already recovered most of the end-to-end loss on a clean task (0.48 -> 0.74
    CI-separated) -- so this is a MEASURED lever, not a hypothesis.
- **INFERRED (you must prove):** that a glass-box, NO-LLM relation-extraction front-end that lifts the SHARED relational
  structure JOINTLY (spatial edges + temporal links incl. the copular/stative channel + event->argument/role structure)
  raises WHOLE-SUBGRAPH SURVIVAL and end-to-end reasoning accuracy CI-separated over the incumbent extraction path AND
  over an info-free twin, on MODERN gold, with extraction quality isolated; OR a rigorous LOCATED NEGATIVE naming the
  exact residual with counts (e.g. "joint parse raises single-edge recall to X but chains still die because the parse
  UAS on multi-clause sentences drops to Y, enumerated" -- a distinct UPSTREAM organ).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the three reasoners -- `hdlab/spatial_relational_model.py`, `hdlab/temporal_reasoner.py`,
  `hdlab/occ_appraisal.py` are LANDED (owner-DONE). Read their three SOLVED.md files IN FULL: they proved the reasoners
  sound on gold and located the extraction wall with counts. This problem CONSUMES them; it feeds them BETTER relations.
- Do NOT re-derive the shared shallow-SRL front-end from scratch -- `hdlab/predicate_argument_frontend.py` exists
  (landed, default-off). REUSE/extend it as the event->role backbone; the job is to (a) make it live and (b) fold the
  spatial + temporal-overlap channels into ONE joint pass, then measure whole-subgraph survival.
- Do NOT add one more per-construction rule and call it converged -- the spatial SOLVED (Sec 4c) MEASURED that
  per-construction returns DIMINISH because a multi-hop answer needs the COMPLETE sub-graph; the remaining lever is
  JOINT high-quality extraction (parse UAS + relation binding), not another trigger word.
- Do NOT re-measure the gold-relation reasoner (1.000) and call it end-to-end -- that isolates the REASONING, which is
  already solved. The deliverable here is EXTRACTION quality feeding the reasoner.
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold, and do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "extraction"`
  / `"relation"` / `"subgraph"` / `"chain"` / `"srl"` / `"attachment"` / `"parse"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm the three
  reasoners are live and consume the reader's OWN extraction, and confirm `predicate_argument_frontend` routing is
  DEFAULT-OFF in `situation_reader.py` (grep `route_predicate_arguments` / `role_route`); skim `hdlab/` so you build ON
  the existing extractors, not beside them.
- READ IN FULL (build ON them, credit them): the THREE SOLVED.md files --
  `notes/problems/reason_over_the_spatial_relational_model_containment_position_path_modern_gold/SOLVED.md` (its Sec 4/4c
  extraction wall + chain-survival metric + "per-construction returns diminish"),
  `notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/SOLVED.md` (its P2 copular/stative channel +
  Wall-2 cue-sparsity), and
  `notes/problems/infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence/SOLVED.md` (its density phase-cut +
  event<->goal role-filler matching). And `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.1 (the front-end-is-the-constraint
  headline) + the SPACE/TIME/affect entries in sec.2b.
- INSPECT what you REUSE: `hdlab/predicate_argument_frontend.py` (the shared shallow-SRL router);
  `experiments/spatial_relation_extractor.py` (`extract_edges` -> containment/position/path/proximity);
  `experiments/_temporal_ordering.py` (`extract_events`) + `_temporal_ordering_multiframe.py` (`extract_events_punct` +
  the constraint-edge graph -- note it emits only VBD/had+VBN/be+VBN and DROPS copular/stative + present-tense);
  `hdlab/arc_parser.py` + `hdlab/pos_tagger.py` (the upstream parse this rides on).
- CONSUME the measured wall (do NOT re-derive): `experiments/exp_spatial_extraction_recall_v1.py` (edge recall + chain
  survival per type) -- this is your whole-subgraph-survival harness template; generalize it to the temporal + event-role
  subgraphs.
- ENUMERATE what is extracted TODAY vs what each reasoner NEEDS (an absence claim requires an enumeration, not a search):
  for a sample of modern-gold passages, list the gold subgraph edges per channel, mark which the current front-end
  recovers, and compute per-passage whole-subgraph survival. State how you enumerated in your submission.
- GOLD: you are PRE-AUTHORIZED to acquire an open MODERN gold under `data/corpora/<name>/` with a REPRODUCIBLE pinned
  fetch script in `experiments/` + a provenance note. Reuse what is already on disk where possible: SpaceEval/ISO-Space +
  SpartQA-HUMAN (spatial, on disk), TB-Dense + TORQUE (temporal, on disk), and a MODERN shallow-SRL gold for event-roles
  (prefer QA-SRL / OntoNotes-modern / UD-EWT; GUM for multi-genre). State provenance + license + n; note any genre
  confound. Do NOT lean on 19c because it is better-powered (a 19c number is informational only).

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box RELATION-extraction front-end (built + validated in `experiments/`; strategy lands any hdlab change,
   Q111).** It lifts the SHARED relational structure a JOINT pass over the reader's OWN parse produces -- (a) spatial
   edges (containment / relative position / path-transfer), (b) temporal links (before/after + Allen overlap endpoints,
   INCLUDING the DROPPED copular/stative channel), (c) event->argument/role structure (agent/patient/goal/location/...,
   extending `predicate_argument_frontend`) -- as ONE structured extraction, not N independent per-edge rules. Copy the
   syntax-semantics / frame-binding COMPUTATION; SWEEP the cue-precedence, endpoint rule, and every substrate
   operating-point knob. NO external LLM.
2. **The front-end beats the INCUMBENT extraction path CI-separated on MODERN gold, reported per channel AND aggregated,
   with WHOLE-SUBGRAPH SURVIVAL as the headline metric.** The primary metric is whole-subgraph survival = the fraction
   of gold MULTI-HOP chains (>=2 edges) for which EVERY edge is recovered (so end-to-end reasoning is even POSSIBLE); ALSO
   report end-to-end reasoning accuracy over the front-end's own extraction. The FLOOR is the current live extraction path
   recomputed on the SAME population (the strongest floor actually run -- it is what this must beat); gate on the floor's
   UPPER CI bound. Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses
   populations. The gold-relation reasoner (near-perfect) is the CEILING, not a floor.
3. **The info-free twin LOSES CI-separated:** shuffle the extracted relations (edges permuted, node set + counts kept) --
   the reasoner over the shuffled subgraph must collapse, proving the EXTRACTED STRUCTURE is load-bearing, not a shape
   artifact. (This is the spatial SOLVED's shuffled-relation twin, generalized to all three channels.)
4. **Extraction quality is ISOLATED.** Hold each reasoner FIXED (they are solved); vary ONLY the front-end. A gold-vs-
   extracted split must show the reasoner near-perfect on gold and the lift attributable to recovered edges. A POSITIVE
   control the incumbent CANNOT get: a multi-clause sentence whose subgraph the joint pass recovers whole but the
   per-relation path fragments.
5. **NO-regress full-stack (FULL-STACK UPSTREAM).** Prototype THIS front-end AND its upstream (the parse -- `arc_parser`
   UAS + relation binding) all the way to EXCEL/EXCEED; then CONFIRM no other live consumer of the parse / the shared
   front-end REGRESSES (coref, causal typing, the meaning channel, the reasoners), and note which consumers should be
   REVISITED to exploit the improved extraction. The reader stays byte-identical where the front-end is off.
6. **One-screen summary:** front-end design -> modern gold + provenance per channel -> incumbent-extraction floor -> twin
   -> whole-subgraph-survival + end-to-end margins (with CI half-width + null p95) per channel + aggregate -> upstream
   no-regress -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the joint pass lifts single-edge recall from 0.22 to 0.55 and chain survival
from 6/90 to N/90, CI-separated over the incumbent and the twin, BUT three-hop chains still die because parse UAS on
sentences with >2 clauses drops to Y, enumerated with counts -- the residual is a distinct UPSTREAM parse-accuracy
organ"; OR "the copular/stative channel lifts temporal overlap survival CI-separated but spatial path survival does not
move because motion source/goal binding is gated by PP-attachment, located and counted").
**STRETCH (name it, do NOT require it):** unify all three channels behind ONE joint parse pass so a single extraction
serves spatial + temporal + appraisal simultaneously (and feeds the OCC event<->goal role-filler match), and show the
aggregate whole-subgraph survival exceeds the best per-channel front-end -- the full "one front-end unstarves three
reasoners" claim. Report as an additional arm if you reach it.

## 8. FILES AND ENTRY POINTS
- **REUSE (landed -- do NOT rebuild):** `hdlab/predicate_argument_frontend.py` (the shared shallow-SRL router -- the
  event->role backbone to extend + make live); `hdlab/spatial_relational_model.py`, `hdlab/temporal_reasoner.py`,
  `hdlab/occ_appraisal.py` (the three reasoners this feeds); `hdlab/arc_parser.py` + `hdlab/pos_tagger.py` (the upstream
  parse); `hdlab/situation_reader.py` (the live reader + its default-off routing).
- **EXTEND (the per-channel extractors to fold into ONE joint pass):** `experiments/spatial_relation_extractor.py`
  (`extract_edges`); `experiments/_temporal_ordering.py` + `_temporal_ordering_multiframe.py` (event + tense/connective
  extraction -- add the copular/stative + present-tense channels).
- **CONSUME (the measured wall + the survival-metric template -- do NOT re-derive):**
  `experiments/exp_spatial_extraction_recall_v1.py` (edge recall + chain survival).
- **Gold:** SpaceEval/ISO-Space + SpartQA-HUMAN (spatial), TB-Dense + TORQUE (temporal) on disk; acquire a MODERN
  shallow-SRL / role gold (QA-SRL / OntoNotes-modern / UD-EWT / GUM) under `data/corpora/<name>/` with a pinned fetch
  script in `experiments/`.
- **Motivation + fence:** the three SOLVED.md files + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.1 (front-end-is-the-
  constraint) + sec.2b (SPACE/TIME/affect entries). Build in `experiments/` + `verification/`; strategy lands any hdlab
  change (Q111). Heavy -> REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the front-end extraction wall is now closed / partly closed and measured on a
  modern gold via whole-subgraph survival, or a located negative naming the residual upstream organ).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote any reasoner's GOLD-relation score (spatial 1.000, appraisal oracle 1.000, temporal overlap 0.994) as an
  end-to-end result -- those ISOLATE the reasoning, which is already solved. The bar here is EXTRACTION quality feeding
  the reasoner (whole-subgraph survival on real prose), floor = the incumbent extraction path recomputed on the item's
  own population. No number crosses scorers / populations.
- Do NOT quote per-edge RECALL as the capability -- the metric is WHOLE-SUBGRAPH SURVIVAL (every edge of a multi-hop
  chain). 13% edge recall is 1% chain survival; a per-edge number OVERSTATES end-to-end reach.
- Do NOT re-derive the three reasoners or the shallow-SRL front-end -- all are landed. The ingredients are the parse +
  the existing extractors; the deliverable is a JOINT high-recall extraction that makes chains survive.
- Do NOT add one more per-construction rule and declare convergence (per-construction returns are MEASURED to diminish);
  do NOT lean on a 19c corpus as load-bearing gold (BANNED 2026-09-06 -- informational only); do NOT use an external LLM
  at inference (the invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** We built three separate reasoners -- for space, for time, and for how a character feels --
and each one works almost perfectly when we hand it clean facts, but each one stalls on real stories in the exact same
spot: the step that reads sentences and pulls out the little "X relates to Y" facts recovers too few of them. A chain
of reasoning needs every link, so recovering one fact in five means a two-fact chain survives only one time in
twenty-five and longer chains essentially never. The job is to build that reading step so whole chains survive, and to
prove it on modern text by measuring exactly that -- how often we recover EVERY fact a multi-step answer needs, not how
many single facts we get -- with a scrambled-facts version falling apart so we know the real structure is doing the
work. One reading step fixes all three reasoners at once, which is why it is worth doing now.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the three reasoners are live and starved, and that the
shared shallow-SRL front-end is landed but default-off), reads the three SOLVED files and the audit sec.1/sec.2b in
full, generalizes the spatial chain-survival harness to all three channels on modern gold, builds ONE joint
glass-box extraction pass (extend `predicate_argument_frontend` for roles; fold in the spatial edges and the dropped
copular/stative temporal channel), and reports whole-subgraph survival + end-to-end margins over the incumbent
extraction path and the shuffled-relation twin, with the upstream parse improved and no live consumer regressed -- or a
located negative naming the exact residual (most likely parse UAS on multi-clause sentences). The STRETCH (one front-end
serving all three reasoners from a single pass) is named as the full prize.
