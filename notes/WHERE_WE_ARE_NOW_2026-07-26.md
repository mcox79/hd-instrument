# WHERE WE ARE NOW — clean current state (tier 3; REWRITE each session, keep tight) — updated 2026-07-27 ~15:30Z

## Direction (read FIRST)
1. GOAL + invariants + anti-drift: `notes/SUBSTRATE_CHARTER_read_first.md`
2. The plan: `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md`
3. This = the live snapshot. (Charter+plan govern; this is what changed.)

## THE GOAL (one line)
A glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS, by EARNING its meaning + knowledge the brain's way (no borrowed embeddings, no external LLM at inference). Architecture = CLS: SEED a foundation from relational KBs -> READ new material -> SLEEP-consolidate. Coupled to a LEARNED grounded representation.

## ✅ CONFIRMED + BANKED (do NOT rebuild; all VET'd, local-only store, tail=29590)
- **Knowledge FOUNDATION** `cskg_foundation_v1` (data/cskg_foundation_v1/, gitignored 258MB): 482,588 concepts / 1.24M typed edges from CSKG cross-cutting spine, cleaned/canonicalized/grounded (Lancaster/concreteness/VAD/AoA), dense 12-14 k-core flagged, glass-box, NO borrowed vectors. VET-CONFIRM HARD_PASS, **seq 29585**.
- **Ingest fixed + VERIFIED**: director-KB continuous ingest was failing (WinError 1450) -> resilient + bounded; full clean pass = 2.83M triples, 0 new failures. Substrate-as-memory is queryable (tools/director_kb_query.py) — search via query, NOT grep (notes/ has 26k files).
- **Relational-inference WIN** (banked **29587/88/89**, VET-confirmed leak-proof + adversarial shuffle-control): the LEARNED encoder does GENUINE inductive relational inference on held-out-NEW concepts — beats grounding-homophily +0.108 & non-learned 2-hop +0.093; survives 1-edge context (dose-response +0.068->+0.112 = reasoning theory: resolution scales with #constraints); holds TWO-NEW-CONCEPT (+0.117/+0.073); scales with data. Modest absolute (~0.65) but real. Contradicts "VSA recalls-not-invents" prior.
- **Local decision-time REASONING space MAPPED + EXHAUSTED** (3 honest negatives: depth-FLAT, reasoner-combiner-WORSE, chain-through-hidden-intermediate-FLAT): composition already lives IN the learned representation at encode-time (distributed coding, brain-true); bolting reasoning on top adds nothing. => the lever is REPRESENTATION QUALITY (data/scale), not reasoning tricks.
- **SCALE PARTIAL WIN** (banked **29590**, VET-confirmed leak-proof): from-scratch encoder (OUR own, 237M-token ARC, no borrowed vectors) LEARNED real meaning (+0.10 over random-init) and TEXT-ALONE beats grounding **+0.039 on held-out-NEW SEMANTIC** (both seeds, controls at chance). FIRST time learning beats the grounding ceiling on new-concept generalization. Scale WORKS + is DATA-LIMITED (more data grows it). The run's "TIE_NULL" headline was a FUSION ARTIFACT (naive 50/50 fused < text-alone); tiered MM pending a fusion-fixed re-run.

## 🔬 IN FLIGHT (right now)
- **SCALE v2** (remote GPU): clean-win promotion — learned-gate fusion (primary beats grounding?) + text-alone on the RELATIONAL headroom bar (unmeasured in v1) + SAVES checkpoint. Reproduces v1 exactly. Landing-watch Monitor b4u5jy9ot. Metrics -> data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json.
- **SELF-LEARNING LOOP v1** (local CPU, on the REAL seed-7 encoder ckpt): the decisive test — does the substrate LEARN+IMPROVE from reading real prose? Mechanism VALIDATED at smoke (loop runs; SLEEP FIRES EVERY CYCLE [the old cycle2 bug FIXED]; comprehension real = real prose beats scrambled +0.05-0.07; controls clean). Knowledge-gain-across-cycles = the open question (tiny-smoke encoder regressed by averaging; real encoder is the test). Monitor b8u7gvdhx. Cell exp_unified_self_learning_loop_v1.py (636e3531e).

## 🧠 THE SELF-LEARNING LOOP = the current frontier (USER-directed 2026-07-27)
Ingestion had been BYPASSING the reader (scale run fed the encoder only). CORRECTION: every corpus feeds BOTH the encoder (representation) AND the reader (read->flag-unknowns->extract->SLEEP-consolidate into foundation). The trained encoder is the reader's comprehension engine (it was previously blocked on having none). STANDING: use ALL capabilities in every experiment; the substrate learns from all exposure — but VALIDATE the loop improves consistently BEFORE scaling it wide.

## ✅ LOOP-V2 FIX RECIPE READY (if loop v1 regresses — likely, it uses plain averaging)
From drill (notes/drill_brainfaithful_consolidation_for_read_sleep_loop_2026-07-27.md) + scour (notes/scour_prior_consolidation_fusion_selflearning_2026-07-27.md) — MOSTLY REUSE, not new research:
- CONSOLIDATION (replace plain mention-averaging, which dilutes to centroid via noise + anisotropy): **CA3-completion-before-write** (prior HARD_PASS, retention 0.933 vs 0.020) AND/OR precision-weighted Kalman update + common-mode/anisotropy subtraction (need BOTH: precision fixes noise, common-mode fixes centroid-collapse).
- FUSION (naive 50/50 dilutes): **learned convex gate** (prior HARD_PASS, +0.23 MRR).
- REAL RISK (the deeper one): reader knowledge-OVERRIDE net-HURTS cold-transfer across 3 prior tests -> needs a **COVERAGE-AWARE OVERRIDE GATE** (new read-knowledge overrides only when high-confidence/high-coverage; else defer to existing).

## NEXT (in order)
1. Loop v1 lands -> VET (knowledge-gain genuine? sleep fired? controls? leak-proof?). 
2. Build loop-v2: CA3-completion consolidation + learned-gate fusion + coverage-aware override gate. Validate CONSISTENT improvement (monotone-ish, sleep-fires, retention held, controls flat) on REAL prose.
3. v2 scale lands -> VET clean-win (fusion-fixed primary beats grounding + relational headroom answered) -> promote 29590 MM to clean win.
4. Then BREADTH: Simple English Wikipedia (~150-400M tok, clean, one-line HF download) THROUGH the loop (feeds encoder+reader), then web/books/dialogue. Plan: notes/breadth_corpus_expansion_plan_2026-07-27.md. Insight: ARC gap is REGISTER not presence.

## PROCESS FIXES (bake into cell template — cost us this session)
checkpoint-ALWAYS (v1 no-save forced a 6h retrain); design the FULL eval up front (all arms + right fusion, not naive 50/50 keyed as primary); pre-flight dependency check (gitignored data didn't travel -> gate-fail).

## STORE / DISCIPLINE
Tail 29590, LOCAL-ONLY (needs_orchestrator_store_sync), NO push without in-session USER auth. A CONCURRENT session may be live (only stop/kill what THIS session spawned). VET every load-bearing verdict — 3 tempting positives were killed by VET this session; do NOT over-read. Brain = existence proof; on every negative, evaluate the difference vs the brain and iterate.
