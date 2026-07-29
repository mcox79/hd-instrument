# WHERE WE ARE NOW — clean current state (REWRITE each session) — updated 2026-07-29 (compaction-prep, brain-alignment focus)

## Direction (read FIRST, in order)
1. GOAL + invariants + disciplines: `notes/SUBSTRATE_CHARTER_read_first.md`
2. Plan: `notes/THE_PLAN.md`
3. This = live snapshot.
4. **METHODOLOGY: `notes/component_brain_fidelity_ledger.md`** (nail each component brain-faithful, judged on the BRAIN's metric not task-win).
5. **THE ANALYSIS (load-bearing): `notes/brain_foundational_component_analysis.md`** + `notes/drill_language_world_model_framing.md` + `notes/stateful_core_situation_model_build_design.md`.

## 🧠 THE MANDATE (USER, standing + emphasized 2026-07-29)
ALIGN TO THE BRAIN as much as possible to overcome the comprehension barrier — we've been trying to show comprehension for OVER A WEEK. Do the HARD thing, not easy paths (frozen-head shortcuts have failed repeatedly). Nail each component brain-faithful, then assemble. Do NOT lose focus or drift. [[feedback_do_the_hard_blocking_thing_not_easy_paths_easy_bias_disastrous_2026-07-29]]

## THE GOAL
A glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS/COMPREHENDS, earning meaning the brain's way (NO borrowed embeddings/LLM at inference; NO bolt-on reader). Foundation (CSKG, 1.24M edges) is BANKED; the frontier is COMPREHENSION.

## 🧭 THE CONVERGED DIAGNOSIS (the barrier, named precisely)
Our encoder is **FEED-FORWARD + BIDIRECTIONAL (MLM) + STATELESS**, where the brain is **RECURRENT + FORWARD-PREDICTIVE + STATEFUL**. A feed-forward net computes a static function of a fixed window; it CANNOT maintain/update a situation model — so comprehension can't be decoded out of it, because it was never CONSTRUCTED. **THE RECURRING ERROR behind a week of failures: we kept bolting ISOLATED pieces onto a FROZEN feed-forward encoder** (contrastive objectives, slot-memory compressed to scalars, position-bind readouts, loop-extraction) instead of building the coupled maintain-and-update machinery END-TO-END.

## 🌍 THE FRAMING (resolved via deep drill, brain-lit-grounded)
Comprehension = using language to UPDATE/QUERY a pre-existing WORLD MODEL, not building meaning from a blank slate (Spelke, Barsalou/Zwaan/Bergen, Friston/Clark, Lambon-Ralph hub-and-spoke; LLM Othello-GPT / space-time = world models emerge from text-at-scale). CORRECTIONS: "grounded" = RELATIONAL/amodal-hub (= our foundation KB), NOT sensorimotor (contested + failed). It's a TARGET-UPGRADE to the stateful core, not a pivot — framing + mechanism are the same missing organ. OUR THIRD ROUTE (vs LLM emergence-at-scale, vs embodiment we lack): SUPPLY the world model (foundation KB as a PRIOR) + LEARN to update it, glass-box.

## 🔨 THE CURRENT BUILD — coupled stateful core (THE hard build, IN PROGRESS)
`experiments/exp_stateful_core_situation_model_v1.py` + `hdlab/slot_attention_wm.py` (committed d92d52c59, 22df65218). Brain-faithful: K=6 FULL-d-dim entity slots (NO scalar compression), recurrently maintained; LEARNED PE-gated write (PBWM analog); role-general HRR binding (content-key, position-invariant, hdlab/binding); encoder UNFROZEN, trained END-TO-END. Objective = forward-prediction from WM + comprehension-consistency. **ARMS (one variable = the framing test): Arm A blank slots vs Arm B KB-grounded** (slots seeded/keyed by foundation-KB concepts, KB prior encoded through OUR OWN encoder — invariant-checked, not borrowed). Reuses prior blueprint (notes/research_drill_substrate_operand_selection_mwp 2026-06-12 + contentgate v6/v8).
- **STATUS: SMOKE = DISCRIMINATOR_WEAK (both arms ~chance) BUT train_loss ~0.75 ≈ chance => the mechanism can't even OVERFIT 64 training items = a GRADIENT/WIRING red flag, NOT a clean mechanism refutation and NOT just undertraining.**
- **IMMEDIATE NEXT (do NOT ship the GPU full run yet): DEBUG the gradient path — prove the core can OVERFIT a tiny training set (train_loss -> ~0). Likely culprits: gradients not flowing through the WM PE-gate / slot-attention / HRR-bind into the judgment head; or the judgment head not actually consuming the WM output; or LR/optimization. Fix the wiring, re-smoke, THEN the full GPU run.**
- FULL run (HELD, GPU, --full --n-random-init-seeds 5): verdict signature = Arm B beats Arm A SELECTIVELY on KD (bridging) + beats worst-case random-init-core, both seeds.

## 📏 MEASUREMENT (done, honest)
Both in `experiments/diag_order_critical_comprehension_calib_v1.py`, LOCKED_CONSTRUCTION.json + KD_FRAMING_FINDING.json.
- **MES** (MULTI_ENTITY_STATE distE4/distEv6) = MAINTENANCE test. Validated (BGE +0.19-0.25) but NOT bulletproof (~20% structure-alone: 4/5 random-init seeds fail, seed_101 solves at +0.075). GUARD: mechanism must beat WORST-case (~+0.08) random-init across >=5 seeds.
- **KD** (gen_knowledge_dependent, real CSKG facts) = BRIDGING/framing test. MEASUREMENT-LIMIT INSIGHT: you CANNOT frozen-reader-validate a bridging task (bridging IS the capability; a frozen linear reader can't do the 2-step conditional inference even with the KB fact injected). So KD is judged by the SELECTIVE Arm-B-vs-A delta DIRECTLY (no frozen-reader gate) + random-init-fails guard + provably-solvable-by-construction.

## ✅ BANKED this week (do NOT rebuild) + ❌ what's SPENT
- WINS: learned readout (relational placement is readout-limited, +0.038, WIRE); gated_fusion island cashed in (two-seed HARD_PASS, per-axis gate > z-avg, WIRE). Foundation (29585), scale-encoder (29591), reasoner — banked.
- NULLS (all clean, both seeds): grounding (HARD_FAIL_NO_TRANSFER — sensorimotor is for concrete, not relational); objective axis (relObj + full R3/R4 self-teacher); breadth (data lever refuted, equal-budget); forward-PC-alone v5 (crashed CUDA OOM on full-position logits — causal-LM logits chunking needed; and forward-PC-alone is stateless anyway -> folded into the coupled build as an arm).
- **READOUT EASY-PATH SPENT for comprehension**: cross-boundary VET failed-to-replicate (seed-luck); AttnBilinearReadout HARD_FAIL_STRUCTURE_ALONE (random-init matched). A decoder can't fix a signal the encoder never built -> the fix is UPSTREAM (this build).

## 🛠️ PROCESS FIXES (2026-07-29, durable)
- **FS: fixed the right way** — `git config core.fsmonitor/untrackedCache/fscache true` (git 2.53). git status 2min-timeout -> 0.68s. Non-destructive; store (data/substrate_index/concept/atoms.jsonl + corpora) + tracking design intact. (Root: 42k tracked files incl. intentional data/*/metrics.json; NOT a runaway cron.) Deferred (careful): the metrics-in-git tracking design bloats history but fsmonitor makes it fast, store is intermingled -> don't untrack rashly.
- **SUBSTRATE-SEARCH (USER-relocked)**: knowledge/prior-work -> `tools/director_kb_query.py` / `substrate_query.sh`, NOT grep/find. (git/file plumbing stays filesystem.) It surfaces prior work I'd miss + avoids slow fs scans.
- **BUILD-AGENT STALLS diagnosed**: (1) 2-min tool timeout vs multi-minute experiments -> agents background runs + stall at "started it"; (2) fs slowness (now fixed). FIX = SPLIT WORKFLOW: exp_dev builds+self-tests+COMMITS only (fast), returns the run command; DIRECTOR runs the long smoke/full + reads the result off disk. This WORKED for the stateful-core build. Smokes go REMOTE (USER: no local smokes).
- Remote liveness truth = ckpt-mtime + GPU-util, NOT the heartbeat (fooled the Director 3x).

## STORE / OPS
Local-only; NO origin push / remote-persist without in-session USER auth. Only stop/kill what THIS session spawned. Heartbeat every turn-end. Brain = existence proof; on every negative, the difference vs the brain + iterate (diligently, not defeatist). VET+REPLICATE positives before believing.
