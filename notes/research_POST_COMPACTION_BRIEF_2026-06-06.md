# Research POST-COMPACTION BRIEF -- read this FIRST on resume

**Compiled:** 2026-06-06 ~10:00 (pre-compaction)
**Read these first on resume:**
1. This file (current state + standing responsibilities)
2. `notes/PRIORITY_QUEUE_LIVE.md` (queue priorities; I OWN this)
3. `notes/capability_scorecard.md` (capability matrix; check against queue every cycle)

---

## MY ROLE + STANDING RESPONSIBILITIES (do not deviate from these)

I am the Research session for hd-instrument substrate cognitive-core. Per user directive 2026-06-06:

1. **I OWN `notes/PRIORITY_QUEUE_LIVE.md`** as single source of truth for experiment priorities
2. **Exp-Dev pulls from top** of LIVE queue; reports verdicts; I cross off + add follow-ons
3. **Every Monitor event (real-time):** read note, categorize, dispatch 2x drill if genuine HF/MIDDLE, ship direct note if recipient has action
4. **Every cadence wake (30 min fallback):** check queue depth, cross-reference capability scorecard, add cells if weak axes
5. **Every drill landing:** synthesize, add cells, direct note to recipient
6. **No padding ever** -- if I can't justify a cell, it doesn't go in
7. **Direct notes to recipients** when there's something for them (Testbed for cloud, Orchestrator for runners, Exp-Dev for cells)
8. **Capability matrix check** every cycle -- if a high-value capability is stalled, queue cells must address it

---

## MONITOR + WAKEUP (active background tasks)

- **Monitor task `b3hggokoz`** (persistent): watches `notes/exp_dev_*.md`, `notes/testbed_*.md`, `notes/orchestrator_to_research*.md`; emits NEW_NOTE event per new file (30s poll)
- **Older Monitor task `bz0v8tcmj`** is also running (overlapping coverage; can be killed with TaskStop if want to deduplicate)
- **ScheduleWakeup at 22:20 (LAST set) -- NEED TO RESET** post-compaction: schedule 1800s (30 min) as fallback heartbeat

---

## CURRENT STATE -- 26 FLAGSHIP ANCHORS + DIAGNOSTIC+RESCUE+REASONING TRIPLE EMPIRICALLY ANCHORED

### Today's wins (rapid-fire morning of 2026-06-06)

**Diagnostic+Rescue+Reasoning triple complete:**
- Matthiessen at N=4096 FULL: codebook-collision = **100% of substrate noise** (label conservative >=60%; actual 100%); 24th flagship strengthened
- ETF Hadamard codebook init: **10.04x at N=4096 FULL** (random_cap=204 vs hadamard_cap=2048; orchestrator cycle 117; 26th flagship; advantage GROWS with N from 8.02x at N=1024 to 10.04x at N=4096)
- K-hop native reasoning: **lossless to K>=6** (label conservative K=3; actual K>=6 at test grid; ceiling unknown; 25th flagship strengthened)
- Sparse-PATTERN coding: **~12x at f=0.10** (sparse_alpha 0.30 vs dense_alpha 0.025 at N=1024 smoke; exceeds Tsodyks-Feigelman 4x classical bound; Slot 3 HP)
- Norm-gate HARDFAIL: rescue identified -- per-cluster stratified keep gives 100% coverage + 100-1000x speedup (rescue drill output)

**Phase 3 capacity story dramatically improved:**
- Yesterday's revision: 2,621 facts at N=65536 (alpha=0.040)
- If ETF + sparse compound holds: potentially **200k-300k facts per substrate at N=65536**
- D=8 production = **1.6-2.4M facts in LINEAR mode** (Wikipedia subset viable without cubic-tensor)
- Critical confirmation: Slot 10 ETF Hadamard N-sweep across {4096, 16384, 32768, 65536}

**Overnight wins (yesterday 22:30 - this morning 02:05):**
- KF-1 hallucination detection at MiniLM AUC=0.999 (21st flagship)
- Real-encoder capability transfer 1.000 with MiniLM AND Pythia (22nd flagship; encoder-invariant)
- Continual KV injection 60 sessions / 3,600 facts / 99.8% (23rd flagship; PP-19 data point)
- Capacity scaling XL: two-regime alpha LVH catch (alpha=0.040 large N; spawned today's chain)
- HP-12 V2 crypto 2.234ms reproducible

### HP-12 V1 SHIPPED (yesterday 16:50; 5-min manual screen recording pending User)

---

## WHAT'S IN FLIGHT NOW

### Exp-Dev pulling from PRIORITY_QUEUE_LIVE
- **Slot 7** K-hop K=10 at N=16384 (in flight; ~60 min CPU)
- Slot 3 full N=4096 + N=16384 (queued post-smoke)
- T2-9 k=4 XOR at N=16384 (queued)

### Slots queued (in priority order; Exp-Dev pulls next)
- Slot 1 cubic-tensor n=3 BUILD (multi-day eng project; NOT started)
- Slot 7 K-hop K=10/K=20 sweep
- Slot 8 ETF + sparse compound test (potentially ~100x; high strategic value)
- Slot 9 Phase 4a infrastructure ETF eval (does the 10x persist on MiniLM?)
- Slot 10 ETF Hadamard N-sweep {4096, 16384, 32768, 65536} (CRITICAL Phase 3 gate)
- Slot 11 U2 stacked defense (codebook + query layer)
- Slot 12 per-cluster stratified extraction (cost-story rescue)
- Slot 13 concept-uniform random extraction (floor case)
- 2 varied-seed re-runs (capacity_xl seeds=10; hp12_v2_crypto seeds=10)
- 12 Tier-2 backlog cells

### Pending USER decisions
- **CLOUD-1 7B vs 70B** ($0.50-1; binding extraction-infrastructure test) -- NOT YET AUTHORIZED
- **CLOUD-2 distilled student** ($15; 20-40x permanent speedup) -- NOT YET AUTHORIZED
- HP-12 V1 5-min screen recording (manual)

### Pending ORCHESTRATOR
- Acknowledged my retraction (runners healthy in venv launcher->child pattern; no kills needed)
- No active asks

### Pending TESTBED
- Watchdog fix permanent commit confirmation
- FAISS env Windows OpenMP fix (gates HP-12 V2; Tier-3 cells)
- Llama-1B weights local download (optional; gates HotpotQA-1B Tier-3 cell)

---

## CRITICAL STRATEGIC CONTEXT FOR RESUME

### The "audacious vision" status

Goal: Wikipedia substrate cognitive core (memory + reasoning + audit moat) paired with LLM partner, deployable at consumer-hardware cost.

Today's compounding wins:
- Capacity: ETF + sparse compound could give ~100x linear-mode capacity rescue
- Reasoning: K-hop lossless to K>=6 (substrate-native; LLM-free)
- Cost: per-cluster stratified rescues "$333k -> $31" extraction story
- Audit: HP-12 V1 SHIPPED (cert <1ms; 0 phantom; frontier-LLM contrast 0% vs ROME 38%/MEMIT 29%)

If Slot 8 (ETF+sparse compound) HPs AND Slot 10 (N-sweep) confirms at N=65536, **Phase 3 linear-mode could reach 1.6-2.4M facts at D=8 -- Wikipedia subset viable without cubic-tensor**.

Cubic-tensor (Slot 1 BUILD) is still needed for full Wikipedia (35-70M facts) but no longer the only path to Wikipedia-subset.

### Process changes today (don't forget)

1. **PRIORITY_QUEUE_LIVE.md is the SSOT** -- user explicitly asked for this; do not regress to scattered routing notes
2. **Direct notes to recipients** -- if Testbed has cloud action, ship Testbed note; if Orchestrator has runner action, ship Orchestrator note; if Exp-Dev has cell spec change, ship Exp-Dev note
3. **No re-run padding ever** -- byte-identical metrics = zero info; brief idle gaps acceptable
4. **Varied-seed re-runs only for MIDDLE-band cells where CI/variance gates a decision** (Exp-Dev needs to add seed-randomization flag)
5. **Metric hygiene:** auto-assoc Hopfield + FLIP=0.05 + unique patterns + 0.95 accuracy (NOT lenient hetero-saturating); applies to ALL future capacity-comparison drills

### Drill prompt checklist (updated today)

When dispatching capacity-comparison drills, specify EXACTLY:
- Auto-assoc not hetero (unless hetero IS the target)
- Unique patterns (M = distinct memories)
- Flip-corrupted cue (NON-trivial retrieval; FLIP=0.05 is the clean regime)
- Strict >=0.95 accuracy threshold
- Single-step retrieval (iterating can fill sparse zeros and destroy signal)
- For sparse: option-(a) sparse PATTERN coding (k-of-N active components), NOT write pruning or sparse connectivity

### Today's negatives + rescue paths

- **Norm-gate HARDFAIL** -> rescue: per-cluster stratified (Slot 12) or concept-uniform random (Slot 13)
- **Capacity two-regime alpha MIDDLE** (cycle 116) -> rescue: ETF Hadamard 10x (cycle 117 HP)

---

## RECENT NOTES + COMMITS (last 12 commits; all 2026-06-06)

```
64673e0 exp_dev: queue way more genuine cells (4 batch) -- Slot 3/6/7 + T2-9
f525157 research: triple landing -- Slot 3 sparse HP + cycle 118 + extraction rescue
88cd098 exp_dev: queue more genuine cells -- Slot 7 K-hop N=16384 + T2-9 k4-XOR
9744356 research: cycle 118 -- Matthiessen 100% + K-hop K>=6
53e0ee9 exp_dev: Slot 3 sparse-PATTERN HARD_PASS ~12x
3d411eb orchestrator: results summary cycle 118 (v440)
c2ce9e5 Cap map: v439->v440 CYCLE 118 2HP
468a9f3 research: Slot 6 norm-gate HARDFAIL + 2x rescue drill dispatched
3f0368f research: RETRACT prior kill request -- runners healthy
2295cb6 research: ETF Hadamard FULL RUN 10.04x at N=4096 + Slot 10/11
9157937 research: Slot 3 sparse-write spec clarified -- sparse PATTERN coding
2a416d2 research: ETF Hadamard HP -- 8.02x capacity at zero cost (26th flagship)
```

---

## IMMEDIATE NEXT ACTIONS ON RESUME

1. **Reset ScheduleWakeup** -- 1800s (30 min) heartbeat (the prior one from yesterday is stale)
2. **Verify Monitor `b3hggokoz` still active** -- if not, restart with same command
3. **Check for any new notes** since this brief (`ls -lat notes/exp_dev_*.md notes/testbed_*.md notes/orchestrator_to_research*.md | head -3`)
4. **Synthesize any landed verdicts** per standing rule (cross off LIVE queue + add follow-ons + commit)
5. **Standing items to follow up on:**
   - User cloud auth decisions (CLOUD-1 / CLOUD-2)
   - Slot 7 K-hop K=10 verdict (most likely next landing)
   - Slot 8 ETF+sparse compound (key strategic test)
   - Slot 10 Hadamard N-sweep (Phase 3 critical gate)

---

## STRATEGIC PRIORITIES (in priority order)

1. **Confirm ETF + sparse compound** (Slot 8) -- if ~100x holds, Phase 3 linear mode hits Wikipedia subset
2. **Confirm ETF persistence at N=65536** (Slot 10) -- gates the entire Phase 3 commitment
3. **K-hop ceiling identification** (Slot 7) -- empirically anchor substrate-native reasoning depth
4. **Per-cluster stratified extraction** (Slot 12) -- rescues cost-reduction story
5. **Cubic-tensor BUILD** (Slot 1) -- still needed for full Wikipedia 35-70M scale; multi-day eng
6. **Cloud experiments** (CLOUD-1/CLOUD-2) -- user-auth-gated; informs extraction infrastructure choice

---

## END OF BRIEF

Compaction may now happen. On resume: read PRIORITY_QUEUE_LIVE.md + capability_scorecard.md + this brief first. Standing responsibilities continue as documented above.
