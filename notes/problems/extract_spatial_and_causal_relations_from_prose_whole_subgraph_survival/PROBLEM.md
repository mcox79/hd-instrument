---
slug: extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival
status: INTEGRATED
review: EXCELLENT
review_text: Reverified 11/11. THE UNIFYING LAW (a joint-front-end channel clears iff its cheap positional prior solves its sub-task). SPATIAL = brain-foundational WIN (Figure-Ground TYPE-precision +0.0533 CI-sep); CAUSAL = blessed located-negative (unmarked 65.6%, generative simulator wins precision but coverage-capped, coref-unlocked 3.29x); the KEYSTONE (reader reads meaning-blind). Landed across continuations: P2+P4 live+scored, P3 already-live, P5 delegated, P1 deferred.
---

> ## SOLVER REVIEW -- EXCELLENT (integrated across CONT-25/26, 2026-09-08; the large spatial+causal chain)
> Reverified FIRST-HAND **11/11**. **THE UNIFYING LAW (measured):** a joint-front-end channel clears the bar iff its cheap positional prior solves its sub-task — temporal iconicity 84% (detection wins), spatial proximity collapses to 0.185 (needs the semantic typer), causal has no cheap high-coverage+high-precision prior (needs world-knowledge). **SPATIAL = brain-foundational WIN:** the Figure-Ground semantic typer beats the incumbent +0.0533 CI-sep on TYPE-PRECISION + a density floor +0.3864 on hard negatives (recall-survival is DENSITY-CONFOUNDED → score on precision). **CAUSAL = the blessed LOCATED NEGATIVE:** causal type is UNMARKED (65.6% MAVEN), the generative causal-antecedent simulator wins binding precision +0.339 but is coverage-capped ~5% (CSKG refuted at 2%), coref lifts it 3.29×. **THE KEYSTONE (owner's root principle):** the meaning/entity channel is built but never CONSUMED in read() — the reader reads meaning-blind; the fix is CHANNEL-SPECIFIC.
> **FINAL LANDING STATE (the P1-P5 chain, landed carefully across continuations — full detail: ledger CONT-25/26 + audit §2b):**
> - **P2 spatial semantic-typing — LANDED + LIVE + SCORED** (`891d13861` `joint_spatial_frames_ext` byte-parity 0/12; wired into `_read_spatial_reasoning` — 109 edges from a real Bleak House read; board arm `board_spatial_extraction_precision` `4c8413cab`, 0.5913 vs 0.5147 CI-sep). Finding: the board's SpartQA `spatial_relational` dim is a DIFFERENT vocabulary/domain (the ext craters on it) — the reader's win is narrative extraction PRECISION, its own arm.
> - **P4 exact-MAP decode — LANDED** (`ff8008131`, byte-identical temporal, prior).
> - **P3 nominal-event for causal detection — ALREADY LIVE** (`joint_nominal_events` default-on since CONT-20; the causal channel's event set includes nominals → the 0.61→0.85 detectable ceiling is realized). No new landing.
> - **P5 coref→causal generative simulator — DELEGATED** to the active `generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation` solver (which built exactly this — a generative causal-antecedent reader over coref-resolved participants; owner-DONE-pending).
> - **P1 one-parse read() restructure — DEFERRED** (a byte-identical read()-architecture optimization: 4× fewer parses; the exact-MAP decode P4 already landed; deep, not a capability gap).
> - **BUILD follow-ons P6-P8** map to filed problems (P6 meaning-consumption keystone; P7 spatial parser residual; P8 full causal reader = the causal-edges solver). **status:INTEGRATED, priority 2 dropped.**

# PROBLEM: the temporal half of relation extraction was SOLVED (a joint parse-once front-end lifted whole-subgraph survival 0.11 -> 0.73) but the SPATIAL and CAUSAL reasoners are still STARVED -- near-perfect on gold relations yet end-to-end extraction-capped (spatial edge recall 0.22 containment / 0.06 position / 0.02 move, multi-hop chain survival 6/90; the real narrative causal network is SPARSE, only 3.2% of stories support a >=2-hop chain) -- so extend the SAME whole-subgraph-survival joint front-end to SPATIAL (Figure-Ground / RCC8) and CAUSAL edges and prove whole-subgraph survival CI-separated over the incumbent extractor on modern gold, extraction ISOLATED (each reasoner held at gold), with a shuffled-relation info-free twin LOSING -- NO external LLM, glass-box.

**slug:** `extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival` -- **opened:** 2026-09-07 by the
strategy session. The just-integrated temporal joint front-end (`hdlab/joint_relation_frontend.py`) proved the
whole-subgraph-survival approach and EXPLICITLY left spatial + causal as named follow-ons. Two more solved-in-isolation
reasoners (`spatial_relational_model`, `causal_reasoner`) are STARVED on the SAME text->relation extraction bottleneck the
temporal fix already cracked. **status:** CANDIDATE -- a BUILD problem. You build + validate in `experiments/`; strategy
lands any hdlab change (Q111). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `2` because it is
> the highest-fan-out remaining relation-extraction lever with a PROVEN method: the temporal joint front-end already lifted
> whole-subgraph survival 0.11 -> 0.73 and its SOLVED named spatial + causal as the next channels, so this is
> extend-the-proven-architecture, not a from-scratch gamble; and two more already-solved reasoners are unstarved by it at
> once. It sits behind the coref/common-noun tier only in that coref is a broader shared cap; it is a real BUILD (not pure
> wiring). Set the real priority when promoted from CANDIDATE to OPEN.

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
We already gave the reader three ways to reason -- about space, time, and cause -- and each works almost perfectly on clean
facts. We recently fixed the READING step for TIME: one pass over the sentence now pulls out the little "this happened
before that" facts well enough that whole chains of reasoning survive (it went from surviving one time in nine to about
seven times in ten). But the same reading step for SPACE and for CAUSE is still weak: for space we recover only about one
containment fact in five, far fewer for position and movement, so a two- or three-step spatial deduction almost never has
all its links; and for cause, real stories barely connect one event to the next, so only about one story in thirty even has
a chain to reason over. This job is to extend the SAME joint reading step to space and cause, and prove it the same way we
proved time -- not "how many single facts did we get" but "how often did we get EVERY fact a multi-step answer needs" --
with a scrambled-facts version falling apart so we know the real structure is doing the work. No outside AI does the reading.

## 2. WHY THIS ONE
The temporal joint front-end PROVED the approach (whole-subgraph survival 0.1111 -> 0.4054 -> 0.7327 with nominal events;
live recall 0.3203 -> 0.7562; end-to-end 0.0971 -> 0.4937, 87% of ceiling; MAVEN 0.086 -> 0.777) and its SOLVED explicitly
LEFT spatial + causal as named follow-ons ("Spatial NOT landed: the lever is construction coverage 74%, not parse UAS
10%"; the causal L3 located negative: only 3.2% of ROCStories support a >=2-hop chain). Two more solved-in-isolation
reasoners (`spatial_relational_model` 1.000 on gold; `causal_reasoner` sound + densify 3% -> 95% on constructed graphs) are
STARVED on the SAME front-end bottleneck the temporal fix already cracked -- so this is the highest-fan-out remaining
relation-extraction lever, and the METHOD is proven, not hypothesized. Test 4 (does a NUMBER show the DEFECT costs us?):
YES -- spatial multi-hop chain survival 6/90 and causal 3.2%-support are MEASURED end-to-end costs of the current extractor,
not "an alternative exists".

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Same as the temporal front-end: comprehension builds a RELATIONAL structure at the
  syntax-semantics interface -- hierarchical structure-building in left IFG (Friederici 2011/2017) hands a constituent
  structure to thematic-role / argument binding in posterior MTG and the ATL (Bornkessel-Schlesewsky eADM; Frankland &
  Greene 2015/2020), composing meaning via FRAMES in ONE structural pass. For SPACE: Talmy / Jackendoff Figure-Ground +
  Place/Path schemas (a locative predicate binds a Figure, a Ground, and a spatial relation; RCC8 region-connection for
  containment / position), served by the parietal "where" stream + hippocampal spatial schema. For CAUSE: Talmy
  force-dynamics + Trabasso causal-network reachability (the temporal reasoner's causal cousin), driven by connective +
  mental-bridge cues. The load-bearing property (identical to temporal): the brain extracts a clause's relations JOINTLY in
  ONE parse -- Figure/Ground/Path and the causal link fall out of the SAME structural pass -- so WHOLE-SUBGRAPH survival
  (every edge of a >=2-hop chain), not per-edge recall, is the right target.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The spatial construction inventory (which locative / motion
  constructions map to containment / position / path); the causal connective + mental-bridge cue set; the ENTITY-RESOLUTION
  that lets two clauses' edges share a node (the spatial SOLVED's second lever); the abstention thresholds; and every
  substrate operating-point knob. SWEEP these, adopt no number.
- **NOT brain-faithful (do NOT do).** An external LLM / learned seq2seq relation extractor at inference (the invariant);
  adding ONE more per-construction rule and calling it done (the spatial SOLVED MEASURED per-construction returns DIMINISH --
  the whole subgraph must survive); scoring per-edge recall as end-to-end capability; densifying the causal graph with
  contiguity + plausibility and reading Story-Cloze as causal-chain proof (the causal SOLVED's L4/L5 located negative: Story
  Cloze is affect-dominated, a topical baseline is ALSO ~chance); a 19c corpus as load-bearing gold (BANNED 2026-09-06).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - TEMPORAL front-end SOLVED (INTEGRATED): the joint parse-once front-end (`hdlab/joint_relation_frontend.py`) lifted
    whole-subgraph survival 0.1111 -> 0.4054 (+0.2943 CI-sep) -> 0.7327 with nominal events; live recall 0.3203 -> 0.7562;
    end-to-end 0.0971 -> 0.4937 (87% of ceiling); MAVEN 0.086 -> 0.777. It EXPLICITLY did NOT land spatial ("located
    negative -- the lever is CONSTRUCTION COVERAGE 74%, not parse UAS 10%").
  - SPATIAL reasoner SOLVED: 1.000 on gold containment / position / path; end-to-end over the reader's OWN extraction
    (`exp_spatial_extraction_recall_v1`) containment recall 0.223, position 0.058, moves 0.024, multi-hop containment CHAIN
    SURVIVAL 6/90 = 0.067. KEY REALIZATION: "13% edge recall -> 1% chain survival" (the exponent is the wall).
  - CAUSAL reasoner SOLVED: sound on constructed graphs (Trabasso reachability + Pearl counterfactual); L3 located negative --
    the REAL ROCStories network is SPARSE (0.560 edges/story, median 0, only 3.2% support a >=2-hop chain); L4 densify fixed
    3.0% -> 94.8% multi-hop support on CONSTRUCTED edges but is NOT the real-prose extraction fix and Story Cloze does not
    measure causal-chain depth (affect-dominated, topical ~ chance).
  - The shared joint front-end + the three reasoners are landed: `hdlab/joint_relation_frontend.py`,
    `hdlab/spatial_relational_model.py`, `hdlab/causal_reasoner.py`, riding `hdlab/arc_parser.py` + `hdlab/pos_tagger.py`;
    `experiments/spatial_relation_extractor.py` (`extract_edges`) + `experiments/exp_spatial_extraction_recall_v1.py` are the
    incumbent per-channel extractor + the survival-metric harness template.
- **INFERRED (you must prove):** that extending the JOINT parse-once front-end to SPATIAL (Figure-Ground / RCC8 containment /
  position / path) and CAUSAL edges raises WHOLE-SUBGRAPH SURVIVAL CI-separated over the incumbent per-channel extractor on
  MODERN gold, with extraction ISOLATED (each reasoner held at gold) and a shuffled-relation twin LOSING; OR a rigorous
  located negative naming the residual with counts (e.g. "construction coverage lifts spatial containment survival from 6/90
  to N/90 but path survival does not move because motion source/goal binding is PP-attachment-gated, enumerated -- a distinct
  upstream parse organ"; or "causal edge recall rises but cross-sentence causal links need a discourse-coherence bridge, N of
  M, a distinct SDRT organ").

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-do the TEMPORAL channel -- it is SOLVED + INTEGRATED (`joint_relation_frontend`). This problem is the SPATIAL +
  CAUSAL channels of the SAME front-end. Read the temporal SOLVED in full and REUSE its parse-once architecture + survival
  harness.
- Do NOT rebuild the three reasoners -- landed (owner-DONE). This problem CONSUMES them; it feeds them better relations. Do
  NOT re-measure the gold-relation reasoner (1.000) and call it end-to-end -- that isolates the REASONING, already solved.
- Do NOT add one more per-construction rule and call it converged -- the spatial SOLVED MEASURED per-construction returns
  DIMINISH; the levers are CONSTRUCTION COVERAGE (74%) + ENTITY RESOLUTION (10%), not another trigger word.
- Do NOT densify the causal graph with contiguity + plausibility and score Story Cloze as causal-chain proof -- the causal
  SOLVED's located negative (Story Cloze affect-dominated, topical ~ chance). The deliverable is real-prose causal EDGE
  extraction, scored on whole-subgraph survival.
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold; do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "spatial"` /
  `"causal"` / `"extraction"` / `"subgraph"` / `"chain"` / `"figure"` / `"rcc8"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm
  `joint_relation_frontend` is landed (temporal + nominal events) and the spatial + causal reasoners consume the reader's OWN
  extraction; skim `hdlab/` so you EXTEND the joint front-end, not build beside it.
- READ IN FULL (build ON them, credit them): the THREE SOLVED.md files --
  `notes/problems/extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck/SOLVED.md` (the joint
  parse-once architecture, the survival metric, the "spatial NOT landed -- construction coverage 74% not parse UAS 10%"
  split), `notes/problems/reason_over_the_spatial_relational_model_containment_position_path_modern_gold/SOLVED.md` (its
  Sec 4/4c extraction wall + chain-survival + "per-construction returns diminish"), and
  `notes/problems/reason_over_the_causal_network_multi_hop_chains_and_counterfactuals/SOLVED.md` (its L3 sparsity 3.2% + the
  L4/L5 densify-and-Story-Cloze located negative). And `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.1 (front-end is the
  constraint) + the SPACE / CAUSE entries in sec.2b.
- INSPECT what you REUSE: `hdlab/joint_relation_frontend.py` (the parse-once front-end -- extend it with the spatial + causal
  channels); `hdlab/spatial_relational_model.py` + `hdlab/causal_reasoner.py` (the reasoners this feeds);
  `experiments/spatial_relation_extractor.py` (`extract_edges` -> containment / position / path / proximity -- the incumbent
  to beat); `hdlab/arc_parser.py` + `hdlab/pos_tagger.py` (the upstream parse).
- CONSUME the measured wall + survival template (do NOT re-derive): `experiments/exp_spatial_extraction_recall_v1.py` (edge
  recall + chain survival per type) -- generalize it to the causal subgraph.
- ENUMERATE what is extracted TODAY vs what each reasoner NEEDS (an absence claim requires an enumeration, not a search): for
  a sample of modern-gold passages per channel, list the gold subgraph edges, mark which the incumbent front-end recovers,
  compute per-passage whole-subgraph survival, and SPLIT the misses into CONSTRUCTION-COVERAGE vs ENTITY-RESOLUTION (the
  spatial SOLVED's 74%/10% split). State how you enumerated in your submission.
- GOLD: reuse what is on disk -- SpaceEval/ISO-Space + SpartQA-HUMAN (spatial), and a modern causal gold (the causal SOLVED
  fetched `data/corpora/tellmewhy/`; ROCStories for the sparsity baseline; consider a connective / discourse causal gold).
  You are PRE-AUTHORIZED to acquire an open MODERN gold under `data/corpora/<name>/` with a pinned fetch script in
  `experiments/` + a provenance note. Do NOT lean on 19c (informational only).

## 7. THE BAR
PASSES only with ALL of:
1. **The JOINT parse-once front-end EXTENDED to SPATIAL edges (containment / relative position / path-transfer,
   Figure-Ground / RCC8) AND CAUSAL edges (connective + mental-bridge + force-dynamic), built + validated in `experiments/`
   (strategy lands the hdlab change, Q111), as ONE structured extraction over the reader's OWN parse -- NOT N independent
   per-edge rules.** COPY the syntax-semantics / frame-binding computation; SWEEP the construction inventory, the causal cue
   set, the entity-resolution, every operating-point knob. NO external LLM.
2. **WHOLE-SUBGRAPH SURVIVAL is the headline metric** -- the fraction of gold MULTI-HOP chains (>=2 edges) for which EVERY
   edge is recovered -- reported per channel (spatial AND/OR causal) AND aggregated, CI-separated over the INCUMBENT
   extractor recomputed on the SAME population; ALSO report end-to-end reasoning accuracy over the front-end's own
   extraction. Gate on the floor's UPPER CI bound; report CI half-width + null p95; recompute each floor on the item's OWN
   population; NO number crosses populations. The gold-relation reasoner (near-perfect) is the CEILING, not a floor.
3. **The info-free twin LOSES CI-separated:** shuffle the extracted relations (edges permuted, node set + counts kept) -- the
   reasoner over the shuffled subgraph collapses, proving the EXTRACTED STRUCTURE is load-bearing (the spatial SOLVED's
   shuffled-relation twin, per channel).
4. **Extraction quality is ISOLATED.** Hold each reasoner FIXED (solved); vary ONLY the front-end. A gold-vs-extracted split
   shows the reasoner near-perfect on gold and the lift attributable to recovered edges. A can-fail POSITIVE control the
   incumbent CANNOT get: a multi-clause sentence whose spatial / causal subgraph the joint pass recovers WHOLE but the
   per-relation path fragments.
5. **NO-regress full-stack (FULL-STACK UPSTREAM).** Prototype THIS front-end AND its upstream (the parse -- `arc_parser` UAS
   + the entity-resolution that shares nodes across clauses) all the way to EXCEL/EXCEED; then CONFIRM no other live consumer
   of the parse / the shared front-end (temporal survival, coref, the meaning channel) REGRESSES, and note which should be
   REVISITED to exploit the improved extraction. The reader stays byte-identical where the channel is off.
6. **One-screen summary:** front-end design per channel -> modern gold + provenance -> incumbent-extraction floor -> twin ->
   whole-subgraph-survival + end-to-end margins (CI half-width + null p95) per channel + aggregate -> the
   construction-coverage / entity-resolution split -> upstream no-regress -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "construction coverage lifts spatial containment survival 6/90 -> N/90 CI-sep but
path survival does not move because motion source/goal binding is PP-attachment-gated, enumerated -- a distinct upstream
parse organ"; OR "causal edge recall rises CI-sep but cross-sentence causal chains still die because unmarked causal links
need a discourse-coherence bridge, N of M -- a distinct SDRT organ, filed").
**STRETCH (name it, do NOT require it):** unify spatial + causal behind the SAME joint pass that already serves temporal, so
a single extraction serves all four channels; report the aggregate whole-subgraph survival as an additional arm if you reach it.

## 8. FILES AND ENTRY POINTS
- **REUSE / EXTEND (landed -- do NOT rebuild):** `hdlab/joint_relation_frontend.py` (the parse-once front-end -- add the
  spatial + causal channels); `hdlab/spatial_relational_model.py` + `hdlab/causal_reasoner.py` (the reasoners this feeds);
  `hdlab/arc_parser.py` + `hdlab/pos_tagger.py` (the upstream parse); `hdlab/situation_reader.py` (the live reader + its
  channel routing).
- **EXTEND (the incumbent per-channel extractor to fold into the joint pass):** `experiments/spatial_relation_extractor.py`
  (`extract_edges`).
- **CONSUME (the measured wall + the survival-metric template -- do NOT re-derive):**
  `experiments/exp_spatial_extraction_recall_v1.py` (edge recall + chain survival).
- **Gold:** SpaceEval/ISO-Space + SpartQA-HUMAN (spatial) on disk; `data/corpora/tellmewhy/` + ROCStories (causal) on disk;
  acquire a modern connective / discourse causal gold under `data/corpora/<name>/` with a pinned fetch script if needed.
- **Motivation + fence:** the three SOLVED.md files + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.1 (front-end-is-the-constraint)
  + sec.2b (SPACE / CAUSE entries). Build in `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy
  -> REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the spatial + causal extraction wall closed / partly closed on modern gold via
  whole-subgraph survival, or a located negative naming the residual upstream organ).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote a reasoner's GOLD-relation score (spatial 1.000; causal soundness) as an END-TO-END result -- those ISOLATE
  the reasoning, already solved. The bar is EXTRACTION quality (whole-subgraph survival on real prose), floor = the incumbent
  extractor recomputed on the item's own population. No number crosses scorers / populations.
- Do NOT quote per-edge RECALL as the capability -- the metric is WHOLE-SUBGRAPH SURVIVAL (every edge of a multi-hop chain).
  13% edge recall is 1% chain survival; a per-edge number OVERSTATES end-to-end reach.
- Do NOT quote the causal densify 3% -> 95% or the Story-Cloze numbers as an extraction win -- densify is on CONSTRUCTED
  graphs and Story Cloze is affect-dominated (the causal SOLVED's located negative). The deliverable is real-prose edge
  extraction.
- Do NOT re-do the temporal channel (SOLVED / INTEGRATED), add one more per-construction rule and declare convergence, lean
  on a 19c corpus as load-bearing gold (BANNED 2026-09-06 -- informational only), or use an external LLM at inference (the
  invariant). Strategy owns any hdlab landing (Q111).

---

**TLDR (plain English):** We built three reasoners -- for space, time, and cause -- and each works almost perfectly on clean
facts. We just fixed the reading step for TIME so whole chains of reasoning survive (from one time in nine to about seven in
ten). Space and cause still fail in the same spot: for space we recover only about one containment fact in five (far fewer
for position and movement), so multi-step spatial deductions almost never have all their links; for cause, real stories
barely connect events, so only about one story in thirty even has a chain to reason over. The job is to extend the SAME
one-pass reading step to space and cause, and prove it the way we proved time -- how often we recover EVERY fact a multi-step
answer needs, not how many single facts -- with a scrambled-facts version falling apart so we know the real structure carries
the load. One reading step unstarves two more reasoners; no outside AI does the reading.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm `joint_relation_frontend` is landed for temporal + nominal
events and the spatial + causal reasoners are live and starved), reads the three SOLVEDs and the audit sec.1/sec.2b in full,
generalizes the spatial chain-survival harness to the causal subgraph on modern gold, extends the joint parse-once pass with
the spatial (Figure-Ground / RCC8) and causal (connective + mental-bridge + force-dynamic) channels, and reports
whole-subgraph survival + end-to-end margins over the incumbent extractor and the shuffled-relation twin, with the
construction-coverage / entity-resolution split named and the upstream parse improved with no live consumer regressed -- or a
located negative naming the exact residual (most likely PP-attachment for spatial paths, or a discourse-coherence bridge for
unmarked cross-sentence causal links). The STRETCH (one joint pass serving all four channels) is named as the full prize.
