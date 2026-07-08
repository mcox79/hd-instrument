# Director BACKUP -- CURRENT STATE 2026-07-08 (clean; supersedes 2026-07-07)

**Read end-to-end. Self-contained. The 07-07 + 07-06 docs hold detailed pre-07-08 history if needed.**

## STEP 0 on pickup
`date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp` (every turn-end).
Then `python tools/inflight_monitor.py`. INFRA NOTE (see bottom): the monitor CACHE lags (~20min sync); "empty queue" often means FINISHED not stalled -- verify metrics off-disk. Several sub-agents STALLED tonight (died on API/socket blips AFTER their work) -- a 0-byte / long-silent agent output = stalled, re-dispatch fresh. Bash recursive scans hang on the huge store (178k atoms / 15k notes / 5.9k exp dirs) -- use TARGETED grep, never broad crawl.

## >>> LATEST STATE (2026-07-08 ~02:4x Z -- READ FIRST) <<<

### USER REFRAMES/DIRECTIVES THIS SESSION (new, load-bearing -- obey)
- **BENCHMARK = DIAGNOSTIC, not scoreboard.** The LLM/encoder comparison is an INSTRUMENT to find the substrate's LOAD-BEARING POINTS OF WEAKNESS to improve -- NOT "beat the LLM." Decompose failures BY CAUSE -> load-bearing capability -> prioritized improvement map.
- **NEVER frame a baseline (BGE/LLM) as a ceiling the substrate "underperforms."** Beatable/open, brain=existence-proof. (memory: feedback_dont_frame_baselines_as_ceilings_brain_existence_proof_2026-07-08). Distinguish narrow-task-vs-encoder from big-claim-vs-LLM.
- **BRAIN-GROUND the mechanism** (predictive generation -> evaluate DEEPLY how the brain does it; brain=best-in-class reference).
- **2x-DRILL negatives after skunkworks** (revival drills; negatives don't close, they get drilled for revival/mechanism).
- **SCOUR prior experimental work FIRST** before new drills (targeted grep -- the corpus is huge; a broad scour STALLS).
- **Agent-comms = MESSAGES + store-atoms, NOT ferry/handoff docs.** (renamed one exp_dev_handoff file out of the inbox pattern; the legacy `<from>_to_<recipient>` pattern is dead).
- **Keep USER at strategic level; handle plumbing silently; do the REAL fix.**

### KEY RESULTS THIS SESSION (skunkworks-tiered honestly)
- **COMPOSITION (deep-prize crux) = PARITY.** exp_conceptnet_semantic_seeded_beam_composition_v1 FULL, VET'd: RANDOM_BEAM (substrate-native GLASS-BOX, zero external embedding) = 0.502 Hits@10 vs BGE 0.494 = **PARITY within noise** (z=0.26, McNemar p~0.13, run-to-run sigma ~0.02 > the +0.009 margin) -> a transparent substrate TIES the black-box encoder on ConceptNet multi-hop. Tier MM-TENTATIVE; CG-parity needs the multi-seed re-run (fix PYTHONHASHSEED non-determinism). NOT "beats an LLM" (encoder, within-noise). SEM_BEAM HARD_FAIL 0.227 = **CORRELATION-HURTS-CAPACITY confirmed** (semantic-seeded codes cos~0.20 collide the store; RANDOM beats SEM in both regimes) -> MEMORIALIZED (reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08: store wants DECORRELATED codes, retrieval wants correlated -> DECOUPLE; don't semantic-seed the store). 2 atoms filed (HF + MM).
- **PER-ITEM LOGGING BUILT (commit 2235071f2)** = the load-bearing infra blocker CLEARED. hdlab/per_item_log.py PerItemLogger (0.05% overhead), wired into composition + encoder-retrieval evals. Stage-attribution + per-item-property slicing now POSSIBLE (fixes the "data-absent" wall). Already isolated 99/201 composition failures to the COMPOSE stage.
- **DENSITY LAW FALSIFIED (owned honestly):** predicted m*~6 mild-growth (JL mechanism-match) -> DATA says m*=8 FLAT, scale-invariant (argmax flat to 1e-15 across 3.5x V, VET-confirmed not metric-limited). Silver lining: NO per-scale retuning needed. (I over-trusted the theory bracket.)
- **SELF-IMPROVEMENT (north-star):** loop MACHINERY validated (runs end-to-end, honest label fires, controls work on mock) but density regime is FLAT so the CAPABILITY was an honest HARD_FAIL null (VET_PASS). **REVIVAL (2x-drill) = REASONING-DEPTH regime** (CG-tier non-trivial p^D law, data ALREADY ON DISK, zero GPU) -- the north-star demonstration RELOCATED there; build dispatched (exp_dev ad784fc5). Resonator was the pre-identified n=2 but the K-sweep showed it's a WALL (sharp step, riskier/MM).
- **K-SWEEP: resonator hits a WALL at K5/K6** (smoke: oracle_any craters K3=1.0->K4=0.87->K5=0->K6=0 = basin-proliferation, the CG_META 4th-family). Honest CEILING on the recurrent-noise-contra: budget-fixable only to K4, then a wall. FULL running (~2.45h) confirms per-seed.
- **BRAIN-GROUNDED GENERATION (Stage-4 gap):** deep antidote to the noise-compounding failure = PREDICT-RESIDUAL / TD-bootstrap (successor-rep + predictive-coding: accumulate the BOUNDED residual, never raw context). CA3-cleanup = shallow version. 1st build FAILED (wrong regime: RAW didn't degrade 6.01->5.93 = INCONCLUSIVE; + skipped the deep arm). RE-DISPATCHED (exp_dev a09fd97d): reproduce the failure FIRST (dRAW>0 hard gate) THEN 3 arms (baseline + CA3-cleanup + predict-residual-TD). Honest P~0.25-0.30.
- **RECOVERY hardened:** hd-instrument FULLY on GitHub (mcox79/hd-instrument, HEAD==origin/main; the push-fault was a 1-off DNS blip, fixed). Memory on GitHub too (mcox79/ClaudeConvos) but 15k uncommitted = USER's call to push.

### EMERGING PRINCIPLES (hold until substrate-confirmed)
- **NOISE-COMPOUNDING = cross-cutting load-bearing weakness** (raw step-wise accumulation -> unbounded noise): reasoning-depth (survives via per-hop re-clean, CG), resonator (external reset), composition (beam), generation (context-hurts-with-depth). Brain fix = BOUNDED-RESIDUAL accumulation (predictive-coding) = the deep form of per-step re-clean. Theory-confirmed (brain-eval); awaits the generation-build SUBSTRATE demo. -> memory if the generation build confirms.
- **CORRELATION-HURTS-CAPACITY** = CONFIRMED + memorialized (see above).
- Substrate operating LANDSCAPES tend FLAT (density) or WALLED (resonator) -- self-improvement needs a SMOOTH non-flat law (reasoning-depth is it).

### IN-FLIGHT (all Opus exp_dev / research per policy)
- GENERATION rebuild (exp_dev a09fd97d): failure-regime-first + 3 arms.
- K-SWEEP full (running remote_cpu_queue, ~2.45h): resonator wall confirm.
- REASONING-DEPTH self-improvement loop (exp_dev ad784fc5): the north-star revival (zero-cost, data on disk).

### NEXT-SESSION FIRST ACTIONS
1. Heartbeat. `python tools/inflight_monitor.py` + verify off-disk (cache lags).
2. Check + VET the 3 in-flight: (a) REASONING-DEPTH self-improvement loop = the KEY north-star result (does the substrate demonstrate NON-TRIVIAL self-improvement -- proposal beats baselines + firing controls FIRE, unlike density's silence?); (b) GENERATION rebuild (did the smoke reproduce dRAW>0? did predict-residual beat cleanup? noise-compounding vs ceiling?); (c) K-SWEEP full (wall confirmed per-seed?).
3. QUEUED dispatches: SEM_RERANK composition arm (the semantic-negative revival -- BGE re-ranks substrate-native beam, store decorrelated, cheap); composition MULTI-SEED re-run to firm PARITY -> CG (fix PYTHONHASHSEED); resonator Control-2 (self-improvement n=2, on K-sweep full).
4. If generation build confirms noise-compounding-is-fixable -> memorialize the noise-compounding cross-cutting principle.

## WHAT THIS PROJECT IS
hd-instrument: observable VSA/HDC glass-box substrate. USER goal (locked): fully-functional glass-box-LLM-capable substrate, every capability inspectable/editable, brain-grounded. Brain = north-star + existence-proof (NOT a vs-LLM comparison -- comparisons DIAGNOSE weakness). Deep prize: substrate REASONING OVER ingested knowledge (glass-box, self-auditing), as NARROW MONITOR steps (monitor-not-control). Stages 1(found ~88%)/2(meta ~85%)/3(capability ~60%, current front)/4(LM-equiv, deferred; gaps = generation/attention-routing/action-selection/cortex-layer). Encoder = the frontend every stage inherits from (retrieval CG-unblocked @177K; density optimum FLAT so scale-invariant).

## USER-LOCKED (obey)
NO AskUserQuestion. re-encode HELD. SMOKE-local / canonical FULL via remote queue (GPU=orchestrator; the exp_dev remote-SCP GATE_FAIL routes via orchestrator). NEVER git add -A (explicit pathspec; Store in-repo but substrate_index partitions sync-managed). Agent-spawn model. No-smoke (honest tiers off-disk, skunkworks-owned; SMOKE must reproduce the phenomenon being fixed). Fix#28 verify off-disk incl agent numbers. Intuitive strategic summaries at END. Never stand -- keep lanes full, own research lane. Model+effort: research/drills=Sonnet, exp_dev/skunkworks/orchestrator/testbed=Opus, director=Opus; effort HIGH / XHIGH headline-VETs. Keep USER strategic (no plumbing narration).

## INFRA/HAZARDS (this session's live lessons)
- **AGENT STALLS:** multiple sub-agents died on API/socket blips tonight AFTER completing their work (scour, K-sweep exp_dev, generation exp_dev). Symptom: 0-byte or long-silent agent output. FIX: verify off-disk what they produced, re-dispatch fresh (their cells/notes usually landed). Do NOT assume a silent agent is working.
- **SYNC-LAG (SH-9):** remote jobs complete but metrics lag locally (~20min hd_metrics_sync cadence). "Empty queue" often = FINISHED. Force-pull via tools/scp_recover_landing.py. Recommendation flagged: shorten cadence OR pull-at-landing-confirm.
- **SCOUR/SCAN SPEED:** corpus huge (178k atoms/15k notes/5.9k exp dirs). Targeted grep only; broad reads hang/stall.
- queue_add: tools/orchestrator/queue_add.sh (POSITIONAL args, not --flags); exp_dev hits GATE_FAIL on remote SCP -> route via orchestrator. hd_metrics_sync pushes origin/main.
- Store: atoms.jsonl/cert_ledger.jsonl A5-gated; substrate_index partitions gitignored (sync-managed, not git-tracked -- persistence = A5 on-disk write + sync, NOT git commit).
- Detailed pre-07-08 history: notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-07.md.
