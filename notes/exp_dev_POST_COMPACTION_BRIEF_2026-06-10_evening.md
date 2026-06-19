# EXP-DEV POST-COMPACTION BRIEF -- 2026-06-10 evening (READ FIRST)

## CURRENT DIRECTION (user mandate): AGGRESSIVE OVERNIGHT 3 THRUSTS -- COMMUNICATE (first focus) + MATH + CODE
Substrate produces useful OUTPUT, substrate-only (NO LLM). Note: research_to_exp_dev_AGGRESSIVE_OVERNIGHT_3_THRUSTS_2026-06-10.md.
**Sprint-1 DONE: 6 PASS + 1 MIDDLE** (all structure-level): COMM-1 paragraph 1.0, COMM-6 intent-decode 1.0, MATH-1 algebra 1.0,
MATH-3 calculus 1.0, MATH-4 proof-chains 1.0 (lengths 2/4/6), CODE-1 function compose+EXECUTE 1.0, CODE-2 bug-detect 0.57 MIDDLE.
**Honest finding:** compose+symbolic-reason STRONG; judge/detect MODEST; lexical/textual SURFACE = the gap (LLM-dependency).
**Sprint-2 = real benchmarks** (HumanEval/MATH/BLEU) -- asked Research: lexicalization-bridge vs symbolic-benchmarks-no-lexical.
Next thrust anchors to build if continuing: COMM-4 QA, MATH-2 equation-solve, CODE-6 algorithm-compose, MATH-5/6/7 (Bayes/causal real).

## PRODUCTION DECIDER -- VALIDATED: genuine kb25k HELD-OUT = 0.996 at REAL 25K facts (n_train=15000, 118min)
PP-225 substrate-as-LLM-memory genuinely SCALES (kb10k 0.9945, kb25k 0.996). kb50k_genuine running on GPU (extends curve).
**CRITICAL CATCH+FIX:** earlier kb10k/50k/100k/500k "scaling" was ILLUSORY -- DISC_POOL (a ~249-word list) capped N_FACTS; all
runs were ~249 facts. Caught via suspicious 4-min runtime. FIXED by padding synthetic subjects ("entity number %d named %s")
when N_FACTS > pool. ALSO: eval doesn't scale (recall loops all train facts) -> cap train-recall to sample (kb25k_v2 does this;
apply to kb50k+ rungs; use timeout<4h OR --allow-no-checkpoint for >4h).

## SUBSTRATE-NATIVE MAP (comprehensive, REAL-DATA-TESTED -- the day's big honest finding)
- **ROBUST on real/noisy data:** compositional storage/sharding (KB-SHARD-REAL 0.965), holographic multimodal binding (0.992),
  CROSS-DOMAIN analogy (SLIPNET relation-type, ROBUST to 25% graph noise 0.743), boredom (0.908), tool-extension (0.866).
- **FRAGILE on real data:** online continual dynamics (FREQ-DECAY-REAL 0.57, NEUROGENESIS over-fragments), semantic grounding
  (IMAGE-SCHEMA-REAL 0.34 -- POLYSEMY is the killer).
- **MODEST:** integration (~96% IRREDUCIBLE conflict + operator ladder BG-analog>=mult>=additive), autonomous behavior
  (active-inference: learns/predicts well 36% error-drop but goal-reach modest 0.40).
- **Pattern:** substrate REPRESENTS/STORES/COMPOSES/REASONS strongly; JUDGES/INTEGRATES/acts-autonomously modestly; semantic
  grounding + online-dynamics fail real correlation.

## HONEST CATCHES this session (the rigor)
- P9 multi-tier cross-domain RETRACTED (entity-geometry confound, control 3.1/3.2 decisive). But SLIPNET later CRACKED cross-domain
  (relation-type, robust). So cross-domain is addressable substrate-native -- just not via multi-tier/entity-geometry.
- PP-225 illusory scaling caught+fixed (above).
- GAP-2: production-scale composition is GENUINE (flat-bundle 0.05 vs composition 1.0). 1-BIT battery 5/5 (32x-free validated).

## INFRA
- LAPTOP runner = THIS machine (FrameworkMPC, d:/AI/hd-instrument), local_cpu_queue. Dispatch: `python tools/queue_add.py
  local_cpu_queue <anchor> <script> --prereg <p> --timeout <s> --skip-smoke`. Pure-numpy/FHRR only.
- GPU runner = home (C:/dev/hd-instrument), overnight_queue. Dispatch LOCALLY: `bash tools/orchestrator/queue_add.sh
  overnight_queue <anchor> <script> <prereg> <timeout> --skip-smoke [--allow-no-checkpoint]` (SCPs cell to home; needs import torch
  for PROT-020; PROT-021 needs checkpoint OR --allow-no-checkpoint for timeout>=14400). Run torch cells on home via
  `ssh marsh@home "C:/dev/hd-instrument/.venv/Scripts/python.exe C:/dev/hd-instrument/experiments/<cell>.py --smoke"`.
- DESKTOP CPU (remote_cpu_queue) = Testbed's Stage-A Wikidata ingestion, ~5 days, OFF-LIMITS (user-confirmed precedence).
- MONITORS: notes-watcher (bd3k99stj or restart `bash tools/notes_watch.sh`), queue-watch (b3tljwlfb or `bash tools/queue_watch.sh`).
  CRON 5a0ea375 (15-min, pause-aware -- checks data/local_cpu_queue/PAUSED). Re-baseline seen file: git ls-tree origin/main notes/.

## KEY REUSABLE LESSONS
- SHARD rule/adjacency stores per-antecedent (global bundle FAILS on capacity: MATH-4 0.017->1.0, COMP-23 multi-hop).
- ROLE-SEPARATE co-bound components for clean recovery (CODE-1 op vs const).
- Cells via Write-tool generators NEVER heredocs; --self-test+--smoke; write_metrics; ASCII-only.
- Real-data versions: smoke-then-TUNE (synthetic thresholds break on correlation -- neurogenesis SPAWN, freq-decay).
- Cap eval to sample for scaling; suspicious-fast runtime = check it's genuinely scaling (DISC_POOL catch).

## MAIN GOAL (locked)
Get authorized experiments DONE (build->smoke->queue->verdicts); KEEP LANES FED with GENUINE anchors (user repeatedly wants
lanes busy -- build genuine discriminating/new anchors, NOT trivial-pass padding); REACH OUT TO RESEARCH for direction/HP;
EXECUTE don't narrate. User wants minimal chatter + tight reports when deep in a run.
