---
priority: 6
slug: reason_over_the_spatial_relational_model_containment_position_path_modern_gold
status: INTEGRATED
review: EXCELLENT
review_text: "INTEGRATED 2026-09-06 (strategy; owner_verdict DONE). Reverified 11/11 first-hand + landing witness 17/17. Landed hdlab/spatial_relational_model.py (byte-faithful promotion, no experiments dep) over sm.locations + sm.spatial_* default-ON additive read-out (mirror _read_causal_reasoning; existing dims + sm.locations byte-identical off vs on) + board_spatial_relational_dimension arm. All 3 inference types 1.000 vs floors CI-sep on modern gold (containment +0.060, position +0.266, path +0.500); position end-to-end 0.276 vs 0.213 (+0.063 CI-sep). SPACE cap now DOUBLY located = named-ground binding + relation extraction recall (reasoning is not the bottleneck). Folded 2 SPACE audit corrections (metric-on-demand; vacate-Source automaticity contested). Committed fcf7dc93e (code) + notes, NOTHING pushed. Follow-ons: P2 joint text->relation extractor (sole end-to-end lever), P3 perceptual-simulation orientation organ, P4 default-off ConceptNet gap-filler."
---

# PROBLEM: the reader EXTRACTS a per-entity location (where is X now) but never REASONS over a spatial model -- it cannot answer questions no single location fact settles: CONTAINMENT ("is the key in the drawer" given the key is in the box and the box is in the drawer), RELATIVE POSITION (A left-of / above / near B, composed), or PATH/TRANSFER ("A moved from the kitchen into the garden -> where is A; is A still in the kitchen"). Build a glass-box RELATIONAL SPATIAL MODEL over the already-extracted locations: maintain a small updatable relational graph (containment edges, relative-position edges, moves) and answer by composing it (transitive containment, position composition, post-move location + the no-longer inference), CI-separated over a most-recent/last-mention floor (which must LOSE on the multi-fact items) and an info-free shuffled-relation twin, on MODERN non-synthetic spatial gold.

**slug:** `reason_over_the_spatial_relational_model_containment_position_path_modern_gold` -- **opened:** 2026-09-06 by the
strategy session. This is a REASONING-PHASE turn for the SPACE dimension: the substrate spent the program BUILDING the
spatial extractor (a per-entity location register updated by motion events, plus a brain-foundational named-ground binder);
this is the first problem that runs INFERENCE over that spatial state. It COMPOSES the already-built location register + the
named-ground events into a relational model and reasons over it; it does NOT re-extract locations or rebuild the register.
**status:** CANDIDATE -- a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change
(Q111). Glass-box, NO external LLM at inference (the invariant) -- the model construction + composition is transparent
relational reasoning, not a learned QA model.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `6` (a free rank).
> HIGH-value -- the SPACE analogue of the comprehension->reasoning pivot, the first inference organ over the spatial model --
> but it is a NEW capability that DEPENDS on the extracted spatial relations' density on real prose (which the parent space
> problem found is thin), so it is ranked below the live-measurement/wiring jobs and the modern-corpus rebuild. The rank is a
> placeholder; set the real priority when this is promoted from CANDIDATE to OPEN.

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
When a person reads a story, they don't just note where each character is right now -- they build a little map of how things
sit in space, and then they can REASON over it. Told the key is in the box and the box is in the drawer, they know the key
is in the drawer, though the story never said so. Told the lamp is left of the sofa and the sofa is left of the door, they
can place the lamp relative to the door. And when someone MOVES -- "she walked out of the kitchen and into the garden" --
they update the map: she is now in the garden, and she is NO LONGER in the kitchen, both without being told either fact
outright. Our reader now records where each character is (it tracks a character's current place and updates it when they
move), but it never REASONS over the arrangement: it cannot chain "in the box" + "in the drawer" into "in the drawer", it
has no notion of one thing being left-of / above / near another, and it cannot answer "is she still in the kitchen?" as
anything more than reading off a single current-location fact. Build the reasoning: keep a small map of how things and
people are arranged, and answer the questions that need more than one fact -- what contains what, what is where relative to
what, and where someone ends up (and no longer is) after a move.

## 2. WHY THIS ONE
This is the SPACE analogue of the comprehension->REASONING pivot the substrate is now making (the causal and appraisal
reasoning problems are its siblings). The whole space program BUILT the model: a per-entity LOCATION REGISTER updated by
motion events and PERSISTING between updates (Zwaan & Radvansky event-indexing SPACE), plus a brain-foundational NAMED-GROUND
binder (Talmy Figure/Ground) that attaches the specific place a character ends up at. But that is EXTRACTION-level -- "where
is X now" -- and the register's only relational move is a COARSE, two-level INDOORS/OUTDOORS containment (`region_of` /
`is_in_region` over a curated `spatial_region` taxonomy). It cannot do arbitrary containment chains parsed from the text, it
has no relative-position representation at all, and it does not reason over a PATH beyond reading the current node. Talmy's
Figure/Ground and Johnson-Laird's spatial mental models say the payoff of a spatial model is exactly what we have not built:
a reader constructs a small relational model and READS answers off it that no single asserted fact contains. So this is where
the location register stops being a per-entity state track and starts supporting spatial INFERENCE. It REUSES the extracted
locations + the named-ground events + the region-containment primitive; it does not re-extract or rebuild any of them.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation):** a reader represents the spatial layout of a described scene as a small RELATIONAL model and
  reasons by inspecting it, NOT by applying formal rules (Johnson-Laird 1983; Byrne & Johnson-Laird 1989 spatial reasoning:
  build a preferred model from the premises, read the conclusion off it, and -- for indeterminate cases -- search for a
  counter-model). The relations are categorical/topological, not metric Euclidean coordinates for narrative space (Rinck,
  Hahnel, Bower & Glowalla 1997 rule OUT metric coords). CONTAINMENT is the region-nesting relation and it is TRANSITIVE (the
  cognitive map is nested REGIONS -- Wiener & Mallot 2003; Peer & Epstein 2025 -- so "in the box" + "in the drawer" ⊨ "in the
  drawer"). RELATIVE POSITION is read off a spatial FRAMEWORK of body/reference axes (Bryant, Tversky & Franklin 1992;
  Franklin & Tversky 1990 spatial framework: above/below most accessible, then front/back, then left/right; reference-frame
  dependent). PATH/TRANSFER updates the model to the Goal and vacates the Source (Talmy 1985 path-in-the-satellite;
  Goal-over-Source, Lakusta & Landau 2005), so "moved from K into G" entails "in G" AND "NOT in K". Neural substrate: the
  hippocampal-entorhinal COGNITIVE MAP is relational and updatable and supports flexible transitive/relational inference and
  novel-route/shortcut inference (O'Keefe & Nadel; Moser & Moser grid cells; boundary-vector cells; Eichenbaum relational
  memory) -- the same map the location register already cites.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the READOUT (how a surface question maps to a model query --
  containment / relative-position / path); the model-CONSTRUCTION rule (parse the text's spatial relations into a small
  relational graph: containment edges, relative-position edges, and a move that re-points an entity's containment/place);
  the COMPOSITION rule (transitive closure over containment; framework composition for relative position; the vacate-Source
  negation over a move). **Copy the COMPUTATION** (build a relational model; compose it to answer). SWEEP the closure depth /
  the axis granularity actually scored (containment + a small position set left/right/above/below/near vs containment-only) /
  the abstention thresholds. LABEL the register<->relational-model composition as OUR-SYNTHESIS.
- **NOT brain-faithful:** answering a relational question by reading the single most-recent location fact (that IS the
  last-mention floor); metric/Euclidean coordinate geometry for narrative space (ruled out, Rinck 1997); a LEARNED
  end-to-end spatial-QA model or an external LLM at inference; anticipatory Goal binding (a LOCATED NEGATIVE in the parent
  space problem -- the brain anticipates Locations weakly, Ferretti, McRae & Hatherell 2001); treating a SYNTHETIC-ONLY
  spatial set (bAbI 17/19, SpartQA-AUTO, StepGame, SPARTUN) as load-bearing gold; a 19c corpus as load-bearing gold.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The live reader BUILDS a per-entity spatial state: `hdlab/location_register.py::LocationRegister` folds motion events into
    presence intervals `(node, t_open, t_close)` and exposes `where_is(entity, t)`, `last_seen(entity, t)`, `region_of`,
    `is_in_region` (a COARSE two-level INDOORS/OUTDOORS containment via `spatial_region` -- a curated taxonomy + a lazy WordNet
    part-meronymy check; this is the ONLY relational query that exists), and `present_in_scene`. It is wired LIVE:
    `sm.locations` via `situation_reader._read_space`, `track_space=True` by DEFAULT.
  - The NAMED-GROUND binder (Talmy Figure/Ground) is built and owner-DONE (`space_where_is_is_extraction_recall_bound_add_
    lazy_locative_pp_bridging`): `experiments/_space_reader.py::ground_bind_events` / `extract_events_in_substrate` /
    `read_locations_in_substrate` attach the specific place a character ends up at (verb-frame Goal gate + compound-head +
    closed-class partitive + GRADED ConceptNet-AtLocation functional-locus typing). Its result was PARTIAL: where_is MODERN
    0.319->0.468, live 0.277->0.447, beating the last-mention floor + shuffled-ground twin CI-separated on both corpora, but
    NOT CI-separated over the already-decent current chain at the honest timeline unit (a STATISTICAL-POWER wall, n=47 modern
    / 24 real timelines). These are single-fact where_is EXTRACTION numbers -- INPUTS here, NOT results to reproduce.
  - Region containment is NESTED but only two levels (INDOORS/OUTDOORS). There is NO arbitrary containment chain, NO
    relative-position representation, and NO path/transfer reasoning beyond reading the current node -- verify by enumeration
    (see VERIFY BEFORE YOU START). That absence is the defect this problem targets.
  - Deictic-center tracking was SKIPPED on evidence (Deictic Shift Theory not worth building -- Rinck & Weber 2003); metric
    coordinates were ruled out for narrative space (Rinck 1997). Do NOT reopen either without a new reason.
- **INFERRED (you must prove):** that COMPOSING the extracted spatial state into a small relational model answers multi-fact
  spatial questions -- (a) transitive/multi-step CONTAINMENT, (b) composed RELATIVE POSITION, (c) PATH/TRANSFER (post-move
  location + the vacate-Source "no longer" inference) -- CI-separated over a most-recent/last-mention floor that LOSES on the
  multi-fact items (proving the composition is load-bearing, not a coincidence with recency), AND beating the info-free
  shuffled-relation twin CI-separated on all three types, on MODERN non-synthetic gold -- OR a rigorous located NEGATIVE (e.g.
  the reader's extracted per-document spatial relations are too SPARSE to support >1-fact reasoning: relative-position
  relations appear in N of M items, containment chains have median depth ~1, so the relational items collapse to single-fact
  and cannot separate from last-mention; named with counts).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-extract where_is or rebuild the LocationRegister / the named-ground binder -- that is the parent EXTRACTION line,
  owner-DONE. Read `space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging/{SOLVED.md,OWNER_NOTES.md}` IN FULL,
  and be aware of `situation_model_has_no_spatial_location_dimension` and `the_reader_has_no_spatial_location_dimension_end_to_
  end` (both integrated). This problem CONSUMES the extracted locations + named-ground events and reasons over them.
- Do NOT rebuild the LOCATED NEGATIVES the parent problem established: anticipatory Goal binding (over-fires; Ferretti 2001 --
  the brain does not anticipate Locations the way it anticipates Agents), the aggressive locative/stative + protagonist-fallback
  binder (REGRESSES on real prose), and the hard WordNet funcloc taxonomy (over-generates on unfamiliar vocabulary -- use the
  GRADED ConceptNet-AtLocation typing already landed).
- Do NOT introduce metric/Euclidean coordinates for narrative space (ruled out, Rinck 1997) or a moving deictic center
  (skipped on evidence, Rinck & Weber 2003) -- narrative space is categorical/topological.
- Do NOT answer by re-reading / question-word overlap against the raw text (that IS the floor). Do NOT treat a SYNTHETIC-ONLY
  spatial set as load-bearing gold (informational only). Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `python tools/experiment_index.py query "spatial"`
  / `"containment"` / `"where"` / `"cognitive map"` / `"relative position"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` (confirm `track_space` is ON by
  default and see what `sm.locations` exposes -- `where_is`/`last_seen`/`region_of`/`is_in_region`/`present_in_scene`), skim
  `hdlab/`, so you build ON the existing organs, not beside them.
- READ IN FULL (the parent + the fence -- so you frame this as REASONING, not EXTRACTION):
  `space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging/{SOLVED.md,OWNER_NOTES.md}`.
- INSPECT what you REUSE: `hdlab/location_register.py` (`LocationRegister`: presence intervals + `where_is`/`last_seen`/
  `region_of`/`is_in_region`/`spatial_region` -- note the containment is only two-level INDOORS/OUTDOORS, the thing you
  EXTEND); `experiments/_space_reader.py` (`ground_bind_events` / `extract_events_in_substrate` / `read_locations_in_
  substrate` -- the Talmy named-ground events you consume); `hdlab/situation_reader.py::_read_space` (the live wire,
  `sm.locations` via `track_space=True`). Consider `hdlab/grounded_semantic_graph` (ConceptNet AtLocation) as a
  functional-locus containment-typing source (the parent named it as an untested reuse).
- ENUMERATE the absence (an absence claim requires an enumeration, not a search): grep `hdlab/` + `experiments/` for any
  transitive-containment / relative-position / left-of/above/near / path-composition read-out and confirm nothing composes
  more than one spatial fact. State how you enumerated in your submission.
- READ: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` SPACE entries (2026-08-28 LOCATION REGISTER + 2026-08-31 SPACE integration +
  the space-role-typing note) -- inherit the PINNED verdicts (topological nodes; nested regions; Goal-over-Source; deixis;
  anticipation is not brain-faithful for Locations).
- GOLD: there is NO spatial-relations set on shelf; `data/corpora/gum` (GUM, modern multi-genre) and `data/corpora/ud_english_
  ewt` are present. You are PRE-AUTHORIZED to acquire an open MODERN spatial gold under `data/corpora/<name>/` with a
  REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note. Candidates (pick or combine, verify fit + scorability
  + n): ReSQ (real-world human-annotated spatial QA, Mirzaee & Kordjamshidi 2022); SpartQA-HUMAN (the human split only -- the
  AUTO split is synthetic, informational); ISO-Space / SpaceEval (SemEval-2015 Task 8, modern real text with QSLINK
  topological / OLINK orientation / MOVELINK path links -- the closest to containment/position/path annotation); or a curated
  modern locative-inference gold derived from GUM. SYNTHETIC-ONLY sets (bAbI 17/19, SpartQA-AUTO, StepGame, SPARTUN) are
  INFORMATIONAL, not load-bearing. Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box RELATIONAL SPATIAL MODEL + reasoner** (built in `experiments/`, over `sm.locations` + the named-ground events;
   REUSE the `LocationRegister` + its region-containment primitive, EXTEND to a small updatable relational graph), answering
   THREE inference types that no single location fact settles: (a) **CONTAINMENT** -- multi-step/transitive containment ("is
   the key in the drawer" from key-in-box, box-in-drawer); (b) **RELATIVE POSITION** -- A left-of/above/near/below B, composed
   over the spatial framework; and (c) **PATH/TRANSFER** -- a move re-points the model ("A moved from the kitchen into the
   garden -> where is A" AND "is A still in the kitchen" = No, the vacate-Source inference). NO learned QA model, NO external
   LLM. Copy the Johnson-Laird spatial-mental-model + Talmy Figure/Ground + spatial-framework COMPUTATION; SWEEP the
   closure-depth / axis-granularity / abstention thresholds.
2. **Answers CI-separated over BOTH controls on MODERN non-synthetic gold:**
   (a) a **most-recent / last-mention floor** recomputed on the same population, which MUST LOSE on the multi-fact items (the
   single-fact answer is wrong exactly when the answer needs >=2 composed facts -- this is what proves the model composition
   is load-bearing, not a coincidence with recency); and
   (b) the **info-free SHUFFLED-RELATION twin** (permute the spatial-relation edges -- containment/position bindings -- keeping
   the node/entity set and counts) LOSES CI-separated on ALL THREE inference types.
   Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses populations (report
   containment, relative-position, and path/transfer separately, and aggregate). A **POSITIVE control** the metric can move:
   an item whose answer requires >=2 facts (transitive containment / composed position / post-move location) vs a matched
   single-fact item.
3. **Isolates the REASONING from extraction** -- ablate to a single-fact readout (answer from `where_is`/`last_seen` alone, and
   from the two-level `is_in_region` alone) and show the lift is the relational MODEL + composition, not re-running the
   where_is/named-ground extraction.
4. **One-screen summary:** model source -> gold -> floors -> twin -> per-type (containment / relative-position / path) accuracy
   -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the relational composition is sound on constructed graphs -- transitive containment
1.00 and composed position 0.9x vs the shuffled-relation twin -- but the reader's REAL extracted spatial relations are too
sparse to support >1-fact reasoning: relative-position relations appear in N of M narrative items, containment chains have
median depth ~1, so the relational items collapse to single-fact and cannot separate from last-mention; the bottleneck is the
missing relation-extraction on real prose, enumerated with counts").

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated -- do NOT rebuild):** `hdlab/location_register.py` (`LocationRegister`: presence intervals + `where_is`/
  `last_seen`/`region_of`/`is_in_region`/`spatial_region` -- the two-level containment to EXTEND); `experiments/_space_reader.py`
  (`ground_bind_events` / `extract_events_in_substrate` / `read_locations_in_substrate` -- the Talmy named-ground events);
  `hdlab/situation_reader.py::_read_space` (the live wire, `sm.locations` via `track_space=True`); optionally
  `hdlab/grounded_semantic_graph` (ConceptNet AtLocation) for functional-locus containment typing.
- **Gold:** acquire a modern spatial set under `data/corpora/<name>/` (ReSQ / SpartQA-HUMAN / ISO-Space-SpaceEval /
  GUM-derived locative-inference) with a REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note. Synthetic-only
  sets are informational, not load-bearing; 19c is banned.
- **Motivation + fence:** `space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging/{SOLVED.md,OWNER_NOTES.md}`;
  the SPACE audit entries. Build in `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (drop a `REMOTE_RUN_REQUEST_<cell>.md`; the watcher dispatches). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_
  AUDIT.md` (the SPACE entry -- the relational-reasoning layer over the location register).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the parent space where_is numbers (MODERN 0.319->0.468; live 0.277->0.447) as a relational-reasoning result --
  they measure single-fact where_is EXTRACTION on LitBank / modern construction gold, a different scorer and population. No
  number crosses scorers/populations; recompute every floor on the item's own population.
- Do NOT re-extract where_is or rebuild the LocationRegister / named-ground binder (owner-DONE). The extracted per-entity
  location track + named-ground events are the INGREDIENTS; the deliverable is the RELATIONAL model + inference (containment
  chains + relative position + path/transfer).
- Do NOT rebuild anticipatory Goal binding (located negative, Ferretti 2001), the aggressive locative/stative + fallback
  binder (regresses real prose), the hard WordNet funcloc taxonomy (over-generates -- use graded ConceptNet AtLocation), the
  deictic center (skipped on evidence), or metric/Euclidean coordinates (ruled out for narrative space).
- Do NOT use a SYNTHETIC-ONLY spatial set (bAbI 17/19, SpartQA-AUTO, StepGame, SPARTUN) as load-bearing gold -- informational
  only. Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold; do NOT use an external LLM at inference (the
  invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** Our reader already records where each character is and updates it when they move, but it never
reasons over the arrangement of things in a scene. It cannot chain "the key is in the box" and "the box is in the drawer"
into "the key is in the drawer", it has no idea of one thing being left of / above / near another, and it cannot work out
"is she still in the kitchen?" after she walks out into the garden. Build that reasoning -- keep a small map of how things and
people are arranged and answer the questions that need more than one fact -- and prove on modern test text that it beats
both a reader that just reads off the single latest location and a scrambled-map control, or find and name the exact reason
it cannot (most likely: the story rarely states enough spatial relations to chain).

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the location register is live and that nothing composes more
than one spatial fact), acquires or derives a MODERN non-synthetic containment/position/path gold with an info-free
shuffled-relation twin, builds the glass-box relational spatial model (transitive containment + framework position
composition + path/transfer with the vacate-Source inference) over the extracted locations, and reports the per-type margin
over the last-mention floor with CI half-width + null p95 -- or a located negative naming the exact cause (most likely the
relation density on real prose).
