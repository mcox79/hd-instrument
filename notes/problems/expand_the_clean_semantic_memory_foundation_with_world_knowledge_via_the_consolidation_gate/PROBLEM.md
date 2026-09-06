---
priority: 11
slug: expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the frozen semantic-memory foundation is thin -- it holds lexical-conceptual sense signatures but almost no encyclopedic/world knowledge (entity types, is-a taxonomies, part-whole, attributes, affordances, scripts, thematic fit, social/causal commonsense); INGEST curated glass-box world-knowledge KBs OFFLINE through the PROVEN consolidation-gate pipeline, typed and correctly-resolved to the right synset/entity, into the frozen store, and prove that admitting it lifts a downstream consumer CI-separated on MODERN gold -- with the RAW-ungated info-free twin LOSING and no regression on existing consumers.

**slug:** `expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate` -- **opened:**
2026-09-06 by the strategy session. This is the "clean foundation expanded to ALL knowledge" turn: the machinery is
BUILT and PROVEN (the consolidation gate + the frozen meaning store + the reversible growth engine), and the foundation
is FREE to build offline. What is thin is the CONTENT -- the store has lexical sense signatures but not the world/
encyclopedic knowledge the reader's consumers need. **status:** CANDIDATE -- a BUILD + VALIDATE problem that REUSES the
gate and the store; it does not re-propose them. You build + validate in `experiments/`; strategy lands any hdlab change
(Q111). Glass-box, NO external LLM at inference OR in gold construction (the invariant) -- every source is a curated
structured KB, ingested OFFLINE.

> **THE ONE BRAIN-FOUNDATIONAL DISTINCTION THAT MUST NOT BLUR (owner 2026-09-06):** querying a raw external dump AT
> INFERENCE is a BARRED shortcut (external-tool-at-inference). INGESTING curated knowledge OFFLINE through the
> consolidation/prune gate into the frozen typed store is the BRAIN'S OWN MECHANISM (systems consolidation during
> sleep -- raw experience is filtered/typed/pruned, never admitted raw), ADMISSIBLE ("the foundation is FREE to build;
> a static offline-built asset is admissible"), and glass-box. This problem is entirely the second thing. The
> north-star: "more knowledge = CLEAN / TYPED / CORRECTLY-RESOLVED" -- RAW reading-derived admission REGRESSES the
> meaning channel (measured -0.033); only the consolidated/typed set helps (+0.067). The value is NOT volume; it is
> clean, correctly-resolved, per-fact-linked-to-the-right-sense/entity knowledge, admitted through the gate.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `11`, a free
> rank clear of the contested band (1-10 are held by the modern-board rebuild, the meaning-channel live-wire, and the
> reasoning-phase builds). It is HIGH-leverage -- the foundation feeds the WHOLE semantic store the meaning channel /
> bridging / coref / temporal-event-schema read -- but it is SEQUENCED after the meaning channel is live (the store is
> largely latent until read()-time consumers exist), so it sits below the live-wiring jobs. The rank is a placeholder;
> set the real priority when this is promoted from CANDIDATE to OPEN.

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
A person's semantic memory is a large, tidy, organized store of world knowledge: that Argentina is a country and a dog is
a kind of animal, that a wheel is part of a car and a page is part of a book, that ice is cold and a knife is for
cutting, that you order food before you eat it and pay after, that "arrest" is something police do to a person. They did
not memorize this from a dump they look things up in mid-sentence; they built it up slowly from experience, and their
sleeping brain filed it away in clean, sorted form -- throwing out the noise, keeping the reliable regularities, and
linking each fact to the right meaning of the right word. Our reader has the FILING MACHINE for exactly this (we proved
it works: feeding it a clean, curated dictionary of word-meanings measurably improved it), and it has a frozen store with
that dictionary in it -- but the store is nearly EMPTY of world knowledge. It knows what words mean in isolation, not the
web of facts about the things they name. This job fills the store: take good, hand-curated fact databases (never a
learned AI, never a lookup done while reading), run them through the same filing machine OFFLINE so each fact is cleaned
and attached to the right meaning, freeze the result, and show that the reader's downstream abilities measurably improve
because of it.

## 2. WHY THIS ONE
The meaning channel is the program's current bottleneck, and its foundation is thin. The proven lift so far came from ONE
knowledge TYPE (lexical-conceptual sense signatures) admitted through the gate; the other twelve types below are absent
or sparse, and each feeds a DIFFERENT live consumer (bridging, coref, temporal, affect, spatial, causal, thematic-fit,
ToM). The value is BROAD: this is not a point fix, it is the "clean foundation expanded to all knowledge" program
(`notes/KNOWLEDGE_LEVER_MAP...`, `WALL_MAP...` sec.3). Two facts make it timely: (a) the machinery is DONE and PROVEN --
the gate (+0.067 CI-sep, raw twin LOSES -0.033), the frozen store (`meaning_foundation`, 117,614 synsets), and the
reversible growth engine (`cls_growth`) are landed; (b) the meaning channel now has its FIRST live read()-time consumer
-- the bridging organ (`hdlab/bridging_inference.py`, landed 2026-09-06) reads `meaning_foundation` + the ATL hub live,
so part-whole and instrument/affordance knowledge is MEASURABLE on a live instrument TODAY (bridging over curated
`meaning_foundation`: ConceptNet PartOf 0.6087, curated 0.6541; CI-scale over floors, shuffled-meaning twin collapses to
chance). It REUSES all of that; it does not rebuild the gate, the store, or the engine, and it does not query a dump at
inference.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation):** semantic memory is a large, TYPED, glass-box knowledge store -- is-a taxonomies,
  part-whole, scripts, event schemas (Collins & Quillian 1969 hierarchies; Rogers & McClelland 2004; Schank & Abelson
  1977 scripts; Lambon-Ralph ATL transmodal hub) -- grown from experience and CONSOLIDATED OFFLINE by SYSTEMS
  CONSOLIDATION during sleep (McClelland/O'Reilly 1995 CLS; Tse et al. 2007 schema-gated consolidation): raw experience
  is NOT admitted raw -- it is filtered, typed, and pruned into the neocortical store. The store is organized as a
  transmodal HUB on shared concept nodes with TYPED SPOKES; different processes read different spoke-projections. Salience
  and structure are in the graph, not in a re-derivation at use-time -- "consult a consolidated store, don't re-derive"
  is itself the pinned principle (the frozen store makes the read an O(1) lookup).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the mapping of each STRUCTURED KB relation onto the store's typed
  spoke + the right synset/entity key (the linking/resolution step), the per-type ingest configuration through the gate
  (`consolidate` cfg: recurrence K / multi-seed M / PPMI P / schema-margin / cap -- for a curated already-resolved KB
  many of these degenerate, so decide which stages apply and SWEEP the rest), and the store ORGANIZATION per type
  (dense/sparse, indexed/superposed, dimension -- a FREE parameter, constraint (e) below). LABEL the KB-relation ->
  spoke composition OUR-SYNTHESIS.
- **NOT brain-faithful:** an inference-time RAW LOOKUP of an external dump (external-tool-at-inference -- BARRED); an
  external LLM at inference OR to construct gold (BARRED); admitting a fact keyed to a raw STRING rather than a resolved
  sense/entity (that is the raw-ungated twin, which REGRESSES -0.033); ungated raw admission of any kind (the gate is
  mandatory).

**THE DIRECTOR'S STARTING INDICATION (enumerate + prioritize the FULL set as part of the work -- this is a starting map,
by semantic-memory TYPE -> the reader consumer it feeds -> a candidate GLASS-BOX curated source):**
1. **Lexical-conceptual semantics (HAVE -- the baseline):** WordNet synsets/hypernymy/meronymy + SyntagNet + ConceptNet
   core + the distributional hub -> WSD / meaning channel. (Expand coverage + the rare-sense tail.)
2. **Encyclopedic named-entity TYPES (instance-of):** Argentina->country, Frontiers->publisher -> common-noun coref +
   bridging + entity-KB. Source: Wikidata P31 / DBpedia InstanceOf / YAGO.
3. **Taxonomic is-a / subclass (concept + instance):** dog->mammal->animal -> coref, categorization,
   selectional-preference generalization. Source: WordNet + Wikidata P279.
4. **Part-whole / meronymy:** wheel->car, page->book -> BRIDGING inference (already the bridging organ's gold). Source:
   WordNet part-meronyms + ConceptNet PartOf + Wikidata P361.
5. **Attributes / properties:** ice->cold, lemon->sour -> affect/valence, plausibility, WSD. Source: ConceptNet
   HasProperty/HasA + feature norms (McRae) + sensorimotor norms (Lancaster).
6. **Functional / affordance:** knife->cut, key->open -> instrument bridging + goal/means-end + WSD. Source: ConceptNet
   UsedFor/CapableOf + VerbNet.
7. **Spatial / typical-location:** desk->office, ship->sea -> spatial reasoning (p6) + where_is functional-locus typing.
   Source: ConceptNet AtLocation (already used by the space organ).
8. **Causal / force-dynamic:** fire->smoke, drop->break -> causal reasoning (p10) + causal plausibility + temporal
   ordering. Source: ConceptNet Causes + FrameNet causatives + ATOMIC.
9. **Event / SCRIPT knowledge (Schank scripts; typical sequences + participants):** order->eat->pay; "poured then drank"
   -> temporal reasoning (p5, non-cued ordering) + causal plausibility + predictive inference + the event_type schema.
   Source: FrameNet frames + frame relations, PropBank, VerbNet event structure, ATOMIC event chains, InScript/DeScript.
10. **Thematic-fit / selectional preferences (verb->typical args):** eat->{food}, arrest->{police,person} -> who-did-what
    (the two-valid-agents residual) + WSD + parser top-down expectation. Source: distributional (Erk) + FrameNet frame
    elements + VerbNet thematic roles.
11. **Social / psychological (mental-state / goal / emotion knowledge):** intends/wants/reacts -> ToM
    (belief+goal->action) + affect OCC appraisal (p3) + goal inference. Source: ATOMIC (xIntent/xReact/xNeed) +
    event2mind + the OCC appraisal structure + SocialIQA-derived schemas.
12. **Kinship / social-role:** mother->parent, king->ruler -> coref (kinship binding) + entity-KB. Source: the existing
    role/kinship/scenario KB + Wikidata + ConceptNet.
13. **Numerical / temporal commonsense (durations/magnitudes/frequencies):** "a war lasts years, a meeting hours" ->
    temporal-duration reasoning (p5) + quantifier reasoning. Source: numeric distributional norms + MCTACO-derived
    typicals.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The consolidation gate is PROVEN and landed: admitting a CONSOLIDATED clean foundation (WordNet relations + curated
    SyntagNet + ConceptNet) through `hdlab/diagnostic_context_wsd` raises a_s 0.2512 -> 0.3178 (+0.067 CI-sep), the
    RAW-ungated twin LOSING (-0.033), MFS no-regression passing, on strict document-disjoint SemCor subordinate, n=2676.
    `hdlab/consolidation_gate.py` exposes `consolidate` (recurrence/multi-seed/PPMI/schema-margin) + `raw_assocs` (the
    twin) + `regression_guard` (raw can never silently ship); witness `test_consolidation_gate.py` 14/14.
  - `hdlab/meaning_foundation.py` = the FROZEN typed store: 117,614 WordNet synsets, one 200-d unit signature each,
    float16, 44MB; +0.0755 CI-sep through the live readout; keep-all is the MEASURED optimum (trimming curated knowledge
    only removes coverage). It emits a multi-index hub-and-spoke MANIFEST (the concrete spoke registry).
  - `hdlab/cls_growth.py` = the reversibility engine (keep-both fusion + rollback gate + EMA slow-anchor), proven safe
    (+0.110/6 rounds, drift-free); composes with the gate (gate = admission quality, cls_growth = reversibility).
  - The meaning channel's FIRST live consumer exists: `hdlab/bridging_inference.py` (landed 2026-09-06) reads
    `meaning_foundation` + the ATL hub live; part-whole (ConceptNet PartOf 0.6087, curated `meaning_foundation` 0.6541 =
    best source, WordNet meronymy 0.4720) and instrument/affordance (UsedFor 0.4522) knowledge score CI-scale over the
    no-inference (0.20) + most-salient floors, shuffled-meaning twin at chance. So types 4 + 6 have a LIVE instrument NOW.
  - RAW reading-derived admission REGRESSES the meaning channel (-0.033, topical not sense-substitutable); only the
    consolidated/typed set helps. Schema-congruence consolidation gating is confirmation-biased on the DISTRIBUTIONAL
    learner but WORKS on the EPISODIC is-a KB (AUC 0.868) -- so a structured is-a/type KB is the right home for it.
- **INFERRED (you must prove):** that the SAME offline consolidation-gate pipeline, fed a CURATED STRUCTURED world/
  encyclopedic KB (per the inventory) typed and correctly-resolved to the right synset/entity, lifts a DOWNSTREAM
  CONSUMER CI-separated over the PRE-INGEST foundation on MODERN gold, for AT LEAST N (>=2) high-leverage knowledge
  types, with the RAW-ungated info-free twin LOSING and NO regression on the existing consumers -- OR a rigorous located
  NEGATIVE per type WITH the measured reason (e.g. topical-not-substitutable, coverage-thin, or the consumer cannot
  receive the signal yet because it is latent -- named with counts).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-attempt READING-DERIVED (raw co-occurrence) growth of the sense-discriminative store: mechanism-complete
  located NEGATIVE (top-down / grounded / bottom-up all tested; caps at gloss ~0.251; raw regresses -0.033). Read
  `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner/SOLVED.md` IN FULL. THIS problem ingests
  CURATED STRUCTURED KBs (already sense/entity-resolved), not reading co-occurrence -- a different, admissible source.
- Do NOT re-derive or re-build the gate, the store, or `cls_growth`. REUSE them. Do NOT TRIM the curated store for
  capability (keep-all is the knee; three independent trims fail).
- Do NOT gate a DISTRIBUTIONAL learner on schema-congruence (confirmation-biased, refuted); the schema gate's home is the
  EPISODIC is-a KB. Route an ALREADY-clean/typed STRUCTURED KB through the import-factory ADMISSION path, not the
  reading-co-occurrence filters (`WALL_MAP...` sec.3 note).
- Do NOT query a raw dump at inference (BARRED shortcut) and do NOT use an external LLM at inference OR to build gold
  (the invariant). The admissible path is OFFLINE ingest through the gate into the frozen typed store.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "consolidation"`
  / `"knowledge"` / `"foundation"` / `"conceptnet"` / `"wikidata"` / `"is-a"` / `"bridging"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`, skim `hdlab/`, so you build
  ON the existing organs, not beside them. READ IN FULL the four SOLVED files: `build_and_freeze_the_clean_curated_
  knowledge_foundation_the_proven_meaning_lift`, `build_the_controlled_knowledge_growth_consolidation_gate_for_the_
  learner`, `turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation`, `grow_broad_coverage_correctly_
  resolved_rare_sense_experience_the_meaning_channel_learner_on`.
- REVERIFY the machinery: `.venv/Scripts/python.exe verification/test_consolidation_gate.py` (14/14) and
  `.venv/Scripts/python.exe verification/test_knowledge_factory_meaning_store.py` (6/6, +0.0755 through the live readout).
- INSPECT what you REUSE: `hdlab/consolidation_gate.py` (`consolidate(agg, mat, w2i, sig_self, sig_sibs, cfg)` where
  agg = {word:(multiseed_support, recurrence_count, ppmi)}, cfg = {K,M,P,margin,cap,drop} -- `drop` disables stages for
  ablation; `raw_assocs` = the twin; `regression_guard`); `hdlab/meaning_foundation.py` (`sense_signatures`, `covers`,
  `manifest_path`); `hdlab/cls_growth.py` (keep-both + rollback + `align_and_fuse` anchor); `hdlab/bridging_inference.py`
  (the LIVE meaning-channel consumer -- your readiest instrument for types 4 + 6); `hdlab/learner/` (core.py, registry.py,
  plugins). Note the frozen assets live under `data/frontend_assets/` (gitignored, on-disk per convention).
- READ: `notes/WALL_MAP_non_brain_foundational_decisions_2026-09-06.md` sec.3 (the world-knowledge misframe + the forward
  plan: expand the foundation AFTER the meaning channel is live), `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.7 (the meaning
  re-frame) + sec.2b (newest bridging + meaning entries), `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md`.
- GOLD: you are PRE-AUTHORIZED to acquire an open MODERN annotated gold corpus under `data/corpora/<name>/` with a
  REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note (source URL, version, license, date) -- prefer
  the instrument OF THE CONSUMER you target (WiC / modern SemEval for WSD; the bridging organ's held-out set for
  part-whole + instrument; UD-EWT / QA-SRL for thematic-fit; a modern temporal set for scripts; GUM for coref/entity).
  19c (McGuffey / LitBank) is BANNED as load-bearing gold. The STRUCTURED KB sources (Wikidata, ConceptNet, FrameNet,
  VerbNet, ATOMIC, feature/sensorimotor norms) are curated glass-box assets -- acquire them the same reproducible-fetch
  way; they are foundation, not inference-time lookups.

## 7. THE BAR
PASSES with ALL of:
1. **For AT LEAST N (solver's choice, N >= 2) high-leverage knowledge TYPES from the inventory:** a curated glass-box KB
   INGESTED THROUGH the consolidation gate + TYPED/LINKED (each fact resolved to the right synset/entity, NOT a raw
   string) into the frozen store, such that a DOWNSTREAM CONSUMER rises CI-separated over the PRE-INGEST foundation on
   MODERN gold, with (a) the RAW-ungated info-free twin LOSING CI-separated (raw admission regresses -- the load-bearing
   guard; reproduce it), and (b) NO regression on the existing consumers (the MFS-style no-regress check on each affected
   population). Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses
   scorers/populations. Measure each TYPE on ITS OWN consumer's instrument (WSD for sense; the bridging organ for
   meronymy/instrument; the temporal organ for event-scripts; etc.).
2. **Enumerate + PRIORITIZE the FULL inventory** (the 13 types above, plus any you add) by consumer leverage -- which
   consumer, which live instrument, how latent, expected lift -- and state which N you took and why. This enumeration is
   PART of the work, not a preamble.
3. **CONSTRAINTS that must hold (state them, hold them):**
   (a) GLASS-BOX, NO external LLM at inference OR in gold construction; all sources curated structured KBs.
   (b) CLEAN/TYPED/CORRECTLY-RESOLVED -- each fact linked to the right synset/sense/entity; admitted ONLY through the gate;
   the RAW-ungated twin MUST LOSE (raw regresses -- the load-bearing guard).
   (c) ONE unified typed store keyed by synset/entity, consumed by spreading activation -- NOT siloed dumps.
   (d) OFFLINE foundation-build (free), frozen; each knowledge type measured on ITS OWN downstream consumer's instrument
   on MODERN gold (19c banned).
   (e) PHASE-DIAGRAM (owner 2026-09-06): the store organization -- dense vs sparse, indexed vs superposed, dimension -- is
   a FREE parameter to SWEEP per organ, not a fixed constraint. Do not freeze a movable parameter.
   (f) SEQUENCING: this composes with the meaning-channel live-wire (the store is latent until a read()-time consumer
   exists), but is INDEPENDENTLY measurable NOW on each consumer's own instrument through the gate (as the +0.067 was
   measured through `diagnostic_context_wsd`, and as types 4 + 6 are measurable through the LIVE bridging organ today).
4. **One-screen summary:** inventory + priorities -> the N types taken -> KB source -> resolution/typing method -> gate
   config (which stages, swept params) -> store organization (swept) -> consumer + MODERN gold -> floors -> raw-ungated
   twin -> no-regress -> per-type CI-sep lift -> what breaks -> verdict. Heavy -> REMOTE.

A rigorous LOCATED NEGATIVE is a FULL PASS: a knowledge type that does NOT help, or that regresses, WITH the measured
reason (e.g. "type-8 causal ConceptNet edges are topical-not-substitutable for the causal consumer -- lift +0.004 not
CI-sep, twin ties; the discriminative signal is the FrameNet frame relation the KB lacks", or "type-2 entity-types cannot
be measured -- the entity-KB consumer is latent, no read()-time reader; N of M items un-scorable, enumerated"). But a
negative must be a FAIR test of the brain's actual mechanism (curated -> gate -> typed store -> consumer), not of an
un-ingested dump or a raw-string key.

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated -- do NOT rebuild):** `hdlab/consolidation_gate.py` (`consolidate` / `raw_assocs` /
  `regression_guard`); `hdlab/meaning_foundation.py` (the frozen typed store + manifest); `hdlab/cls_growth.py`
  (keep-both + rollback + anchor); `hdlab/bridging_inference.py` (the LIVE meaning-channel consumer for types 4 + 6);
  `hdlab/learner/` (core.py, registry.py, plugins); the knowledge-factory experiment cells
  (`experiments/exp_knowledge_factory_*`, `experiments/exp_consolidation_gate_v1.py`) as the ingest->prune->freeze
  reference. NOTE `hdlab/director_kb_chunk_ingest.py` is DEPRECATED (content-chunk index, not a typed-fact path) -- do NOT
  route structured facts through it; use the consolidation-gate admission path.
- **Gold (modern, per consumer):** acquire under `data/corpora/<name>/` with a pinned fetch script in `experiments/` +
  provenance. The bridging organ's held-out set is on-shelf for types 4 + 6.
- **Structured KB sources (curated glass-box foundation):** Wikidata (P31/P279/P361), ConceptNet
  (PartOf/UsedFor/CapableOf/HasProperty/AtLocation/Causes), FrameNet, VerbNet, PropBank, ATOMIC, feature norms (McRae) +
  sensorimotor norms (Lancaster) -- fetch reproducibly, treat as offline foundation.
- **Frame + context:** the four SOLVED files (sec.6); `notes/WALL_MAP...` sec.3; `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
  sec.7 + sec.2b; `notes/KNOWLEDGE_LEVER_MAP...`. Build in `experiments/` + `verification/`; strategy lands any hdlab
  change (Q111). Heavy -> REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b.

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the +0.067 / +0.0755 as a world-knowledge result -- it is the LEXICAL-CONCEPTUAL (type-1) sense-signature
  lift on SemCor subordinate through `diagnostic_context_wsd`; it is the PRIOR that motivates this problem, not a number
  this problem produces. Each new type carries its OWN consumer, gold, floor, and CI inline.
- Do NOT re-run the reading-derived-beats-gloss route (mechanism-complete located negative) or the curated-store trimming
  (keep-all is the knee) -- both are closed.
- Do NOT query a raw dump at inference and do NOT use an external LLM at inference OR to construct gold (the invariant);
  do NOT admit a fact keyed to a raw string (that is the raw-ungated twin, which regresses). Do NOT use a 19c corpus
  (McGuffey / LitBank) as load-bearing gold. Strategy owns any hdlab landing (Q111).
