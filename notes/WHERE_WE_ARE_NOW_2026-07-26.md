# WHERE WE ARE NOW — clean current state (tier 3; REWRITE this each session, keep tight) — 2026-07-26 (updated PM)

## Direction (authoritative — read these FIRST)
1. GOAL/invariants/anti-drift: `notes/SUBSTRATE_CHARTER_read_first.md`
2. The plan: `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md` (now encodes the CLS KNOWLEDGE-ACQUISITION ARCHITECTURE: seed -> read -> sleep, coupled to the self-teacher)
3. Conversion scoping + blueprint anchors: `notes/kb_foundation_conversion_scoping_2026-07-26.md`, `notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md`

## THE ARCHITECTURE (USER-directed 2026-07-26) — CLS end-to-end
SEED the cortex from large relational KBs -> READ new material (hippocampal fast-write) -> SLEEP consolidates into the foundation. The optimized relational foundation is ALSO the R3/R4 self-teacher's training signal (a concept earns meaning from its relational neighborhood). One loop, not two phases.

## CURRENT FOCUS / STATUS (the frontier)
**LAYER 2 (KNOWLEDGE) seed = LANDED this session.** `cskg_foundation_v1` (data/cskg_foundation_v1/, 258MB, gitignored/local): CSKG cross-cutting spine = **482,588 nodes / 1,238,686 typed edges** (16 shards + 24,774 held-out), 79.1% lexical dilution stripped, canonicalized (lemma sense-merge), grounded (Lancaster/concreteness/VAD/AoA on ~41k single-token nodes, honest 5.25% partial), dense 12-14 k-core flagged (`is_dense_core`), hd_fact_store PLAIN-filler schema (NO borrowed vectors). Can-fail gate HARD_PASS: relation-reconstruction real 0.696 vs shuffle 0.237 vs base 0.259 (pre-registered, control collapses). Cell exp_cskg_foundation_v1.py + prereg committed; artifact gitignored.
**Director VET (on disk) = CLEAN** (blueprint match, no borrowed vectors, held-out disjoint 0/3000, gate numbers confirmed in metrics). Independent skunkworks landed-VET IN FLIGHT (aa214747) — recompute gate + spine integrity + banking decision.

## What's DONE (banked / landed — do NOT rebuild)
- **KNOWLEDGE seed:** cskg_foundation_v1 (above). Full raw KBs on disk: ConceptNet 5.7 (498MB), CSKG (112MB), ATOMIC v4. Grounding norms in data/grounding_testbed/ (Binder NOT on disk; Lancaster is our experiential set).
- **Learned-rep MECHANISM (synthetic):** Stage-1 SEMANTIC concept-learner battery CHAIN_GRADE; Stage-2 spokes HARD_PASS (competitive-Hebbian, temporal-contiguity, sparse-DG-CA3, predictive-coding). hdlab/concept_encoder.py.
- **Encoder R1 intel (for next step):** v4_joint_reverify_relock = HARD_PASS dense~0.90 mid-scale via in-batch RKD; teacher-free start point = teacher_free_relational_encoder_cn_subgraph_v1 (RKD-only; NCE is a geometry-corruptor). Open gaps = full-178k scale + teacher-free weaning.
- **Reader+sleep loop (prototype):** situation_reader + clarify_gate + condenser + learner(MDL sleep) = exp_ingest_learn_sleep_loop_cycle1 CYCLE_COMPLETE; p4_replay_consolidation HARD_PASS. Not yet KB-scale. (CLIMB is a retrieval-QA benchmark, NOT a reader.)
- **Reasoning:** verification-by-derivation reasoner hdlab/reasoner.py.
- **Infra:** sharded CG store hdlab/hd_fact_store.py (trust/provenance schema); director-KB ingest hdlab/director_kb.py (indexes 16k notes/2.66M triples = the substrate IS our searchable memory — query via tools/director_kb_query.py, NOT grep).

## Fixed this session
- **Director-KB continuous ingest** was failing on WinError 1450 (resource exhaustion over ~26k files) -> FIXED (bab7b0f00): resilient (skip+log bad/locked files, no abort), bounded handles, noise-exclusion. Resilience PROVEN; full clean-pass verification running detached (PID 14392) under Monitor b4wf8nlba.
- Docs: THE_PLAN now encodes the CLS architecture + corrects Binder->Lancaster + surfaces grounding-arc assets; superseded banners on old plans; tangent doc banner-flagged. Optimal-state audit GREEN (notes/optimal_state_review_2026-07-26.md).

## In flight (read on resume)
- skunkworks landed-VET of cskg_foundation_v1 = **aa214747** (recompute gate, spine integrity, banking decision).
- ingest full clean-pass verification = detached PID 14392, Monitor b4wf8nlba.
- background commit of foundation cell/prereg = bash b1skog5qw.

## Store
Banked 29560-29584 LOCAL-only; cert ledger tail 29584. NO push / NO remote-persist without in-session USER auth. cskg_foundation_v1 atom may be banked by skunkworks VET (local-only).

## ENCODER ARC RESULT (v1->v2->v3, VET'd — read honestly, do NOT over-read)
Teacher-free inductive encoder self-teaching from cskg_foundation_v1, judged on held-out-NEW-concept.
- v1 (grounding-only): HARD_FAIL (lost to popularity). v2 (+mean-pool relational context, degree-matched eval): MIDDLE_BAND (beat popularity, tied structure). v3 (+neighbor-identity codes, stratified eval): the "beats Adamic-Adar +0.234 on structure-poor" headline was a **CONSTRUCTION ARTIFACT** (poor-slice = 0-shared-neighbours pins AA<=0.5 by construction). **Skunkworks DOWNGRADE, banked seq 29586 MEASURED_MECHANISM.**
- **What is REAL (3-seed stable):** grounded encoder places novel concepts above popularity (+0.165) and collapse (+0.18), BUT **learning adds only +0.043 over RAW grounding norms** — the raw Lancaster/concreteness/VAD/AoA carry the signal; the learned self-teacher barely helps; v3's identity mechanism REGRESSED. The whole mechanism arc added ~nothing.
- SCOPE: modest real novel-concept signal from grounding; LEARNING does not yet earn meaning beyond the input norms; "generalizes where structure can't" NOT established.

## Reader+sleep (Track B, VET-pending)
cls_read_sleep_foundation_acquire_v1 FULL HARD_PASS but acquisition text was TEMPLATED from held-out triples = plumbing+stability demo (read->episodic->sleep->semantic pipeline + trust-gated interference-resistance are REAL), NOT comprehension. Next: real prose + independent extractor (hdlab/situation_reader).

## Immediate next (the frontier — full-auto)
1. IN FLIGHT (af0723e5): **R1 graded-semantic-geometry encoder** (Rogers-McClelland differentiation, teacher-free) judged on SEMANTIC-NEIGHBOURHOOD generalization (WordNet category) — the untried load-bearing lever. THE bar = does LEARNING beat RAW GROUNDING on new concepts (grow +0.043). If not, honest evidence of an INPUT-CEILING (grounding+1-hop-relational insufficient -> need richer input), not an objective tweak.
2. Track B real-prose extraction to test comprehension.
3. Reader+sleep KB-scale.
CHECK prior work FILESYSTEM-first (query the substrate KB, not grep). Brain-first, can-fail, VET every load-bearing verdict; DO NOT over-read positives (v3 was over-read, VET caught it).
