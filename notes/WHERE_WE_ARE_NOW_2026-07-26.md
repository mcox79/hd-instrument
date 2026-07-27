# WHERE WE ARE NOW — clean current state (tier 3; REWRITE each session) — 2026-07-27 ~22:30Z (compaction-prep rewrite)

## Direction (read FIRST)
1. GOAL + invariants + anti-drift: `notes/SUBSTRATE_CHARTER_read_first.md`
2. Plan: `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md`
3. This = the live snapshot (rewritten clean this session; older layered blocks removed).

## THE GOAL
A glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS, EARNING its meaning + knowledge the brain's way (NO borrowed embeddings/LLM at inference; the substrate learns it itself). Architecture = CLS: SEED a foundation from relational KBs -> READ new material -> SLEEP-consolidate. The 3 legs: (1) earn MEANING, (2) REASON over it, (3) LEARN continuously from reading.

## ✅ CONFIRMED + BANKED (do NOT rebuild; all VET-survived; local-only store, tail=29591)
- **LEG 1 — EARN MEANING (SCALE WIN, banked 29591 CHAIN_GRADE):** our OWN from-scratch encoder trained on 237M-token ARC (no borrowed vectors) BEATS grounding on held-out-NEW concepts: +0.050 SEMANTIC (parameter-free z-avg fusion, leak-proof) & +0.071 RELATIONAL (text-alone), both seeds, controls at chance, +0.10 over random-init. Scale WORKS + is DATA-LIMITED. Scope: modest (0.60-0.65 band), held-out-NEW placement/retrieval of concepts seen in corpus (median 655 mentions), NOT zero-shot meaning-invention.
- **LEG 2 — REASON (banked 29587/88/89):** learned encoder does GENUINE inductive relational inference on held-out-NEW concepts — beats grounding-homophily +0.108 & non-learned 2-hop +0.093; survives 1-edge context (dose-response, resolution scales with #constraints); holds TWO-NEW-CONCEPT. Local decision-time reasoning EXHAUSTED (depth/combiner/chain all flat) => composition lives IN the representation (encode-time), not bolt-on reasoning.
- **FOUNDATION (banked 29585):** cskg_foundation_v1 (data/cskg_foundation_v1/, gitignored 258MB): 482,588 concepts / 1.24M typed edges, cleaned/canonicalized/grounded (Lancaster/concreteness/VAD/AoA), glass-box, no borrowed vectors. + ingest FIXED+VERIFIED (director-KB, 2.83M triples; query via tools/director_kb_query.py NOT grep).

## 🔴 LEG 3 — LEARN FROM READING = THE OPEN FRONTIER (honest state)
The self-learning loop (read -> comprehend -> extract -> SLEEP-consolidate -> improve). Mechanism plumbing WORKS (sleep fires every cycle, controls behave, retention held, leak-proof). But COMPREHENSION-driven learning is NOT yet demonstrated:
- **loop v1/v2 (GPU):** no sustained gain — concepts were pretraining-SATURATED (median 655 mentions; re-reading the known adds nothing). Diagnosis: brain learns from NOVELTY.
- **loop v3 (exposure-stratified):** initially read HARD_PASS (+0.024 on low-exposure) but **VET DOWNGRADED** — the gain is DISTRIBUTIONAL sample-accumulation + LOW-baseline HEADROOM, NOT comprehension: **word-SCRAMBLED text produced AS MUCH gain (+0.029) as coherent.** Not banked.
- **Two USER-requested drills (committed):** (A) `notes/drill_brain_reading_comprehension_to_memory_vs_our_loop...` (B) `notes/drill_loop_fairness_audit_what_we_missed...`. Findings: brain extracts a role-labeled PROPOSITION (order-sensitive) + binds it; loop v1-v3 never a fair comprehension test.
- **DIAGNOSIS CORRECTED (both directions — honesty):** the drills' "mean-pool is permutation-invariant so can't comprehend" was TOO STRONG — each mention-rep IS an order-sensitive transformer encoding, and loop-v4's SMOKE showed comprehension-SEPARATION (coherent 0.127 > scrambled 0.082 > wrong-concept 0.045, low-power). So the honest state is OPEN, needs a properly-controlled FULL run.

## 🔥 IN FLIGHT
- **loop-v4 FULL (GPU, Monitor b5fq8yqp5):** our OWN encoder, pooling + fast-episodic-store (DG pattern-sep + context-addressed), with the STRONG WRONG-CONCEPT control v3 lacked. Q: does the loop show comprehension-SPECIFIC gain at scale (coherent > scrambled > wrong-concept)? HARD-PASS = FAST_CORRECT LOW sustained gain >+0.02 AND comprehension-specific AND LOW>HIGH AND retention/sleep/controls. Metrics -> data/exp_unified_self_learning_loop_v4/metrics.json. **VET HARDEST if positive** (check active-CONTROL gain not just level).

## 🚫 KEY LESSON (USER-LOCKED 2026-07-27): NO BOLT-ON EXISTING READER
USER: "EVERY time you used an existing reader it was a DISASTER." situation_reader is annotation-bound + mis-calibrated for ARC science prose (would measure extraction failure). I was about to repeat the anti-pattern with spaCy-SVO extraction — HALTED it. **The substrate must COMPREHEND via its OWN learned mechanism, not a supplied/bolt-on parser (situation_reader, spaCy).** This is the earn-it-ourselves invariant applied to comprehension. loop-v4 (own encoder, no external reader) is the correct path.

## 🧭 DIRECTOR DISCIPLINE (recorded — I keep over-reading)
4+ over-reads caught by VET this session (v3 double-dissociation, deep-text +0.20, loop-v3 milestone; + the drills over-stated pooling-can't-comprehend). FIX: on ANY positive, check the ACTIVE-CONTROL's GAIN (not level); separate distributional-sample from comprehension; VET every load-bearing verdict; the exp_dev de-risk (caught situation_reader broken) is the guardrail — trust it.

## ROADMAP
- IMMEDIATE: v4 FULL result (does own-encoder loop comprehend?). PASS -> genuine learning-from-reading, then breadth. FLAT -> the gain is distributional; comprehension needs the substrate's own structure-sensitive mechanism (NOT a bolt-on reader) — iterate on OUR encoder's use, e.g. use per-mention order-sensitive reps without averaging them away.
- NEAR: breadth (Simple English Wikipedia THROUGH the loop, plan in notes/breadth_corpus_expansion_plan_2026-07-27.md) once the loop genuinely learns; ingestion routes THROUGH the loop (encoder + own-comprehension), never bypass; broaden concept set beyond science.
- MEDIUM (north star): unify the 3 legs into a glass-box substrate you can CONVERSE with that reasons out loud. Quality lever = MORE + BROADER experience (scale is data-limited).
- PROCESS FIXES (bake into cell template): checkpoint-ALWAYS (a no-save cost a 6h retrain); full-eval-design up front (all arms + right control); pre-flight dependency check.

## STORE / DISCIPLINE
Tail 29591, LOCAL-ONLY (needs_orchestrator_store_sync), NO push without in-session USER auth. HEAD aa8249d00 (notes committed). CONCURRENT session may be live (only stop/kill what THIS session spawned). Heartbeat every turn-end. Brain = existence proof; on every negative evaluate the difference vs the brain + iterate (diligently, not defeatist).
