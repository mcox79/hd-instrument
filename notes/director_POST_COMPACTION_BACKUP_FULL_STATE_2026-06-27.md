# DIRECTOR POST-COMPACTION FULL-STATE BACKUP 2026-06-27

**For:** post-compaction me. Self-contained. Read this ONE file end-to-end.
**Supersedes:** `director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md` (preserved on disk for prior arc context).

---

## TL;DR — TODAY'S ARC (2026-06-27 early session)

USER returned, asked me to catch up after compaction. Reviewed all context docs (BACKUP-2026-06-26 + DIGEST + COMMANDS + CRITICAL_CONTEXT + MASTER_PLAN + Skunkworks batches 3+4). Surfaced 3 new landings BACKUP missed: ANCHOR 3 coarse-grain FULL HARD_PASS, edge-importance v2 high-alpha FULL MIDDLE_BAND, Wave 4 substrate-KB content-chunk smoke HARD_PASS (with content-vs-filename discriminator firing). Skunkworks batch 4 atom commit landed (CERT 616 stable + 4 META rules J/K/L/M + A5 PRE caught + repaired 9 malformed atoms from batches 2+3). USER approved next-wave actions; 4 agent spawns in flight. New USER directive 2026-06-27: NO MORE EXPERIMENTS LOCAL — ALL REMOTE.

---

## USER DIRECTIVES TODAY (2026-06-27 additions; standing)

### Directive 9 — NO EXPERIMENTS LOCAL — ALL REMOTE (2026-06-27)

> "no more experiments local - all remote"

Supersedes prior "local CPU for smoke" pattern. Smoke AND full both route to `remote_cpu_queue` or `overnight_queue` (GPU). Laptop runs zero cell-runs. Memory file: `feedback_no_experiments_local_all_remote_USER_LOCKED_2026-06-27.md`. Codified in `exp_dev.md` core disciplines.

### Standing directives (re-confirmed from 2026-06-26):
- D1: substrate doesn't know language; stop testing against language (Stage 4 deferred)
- D2: stage progression 1→2→3→4, don't skip
- D3: agent-spawn-only architecture (4-session fleet dead; spawn hdi_<role> per task)
- D4: lean spawn prompts (agents have disciplines built in)
- D5: confirm plan-affecting decisions before action
- D6: substrate is the definitive source for post-compaction (LONG-TERM GOAL; not yet — Wave 4 KB v2 in progress)
- D7: aim M3 (glass-box conversational AI 12-18mo); M4 stretch (hybrid agentic experiment loop 18-30mo)
- D8: carefully vet bounded-capacity KB (Wave 3 explicit vetting protocol; dual-store ≥95%; first 3 weeks audit-only eviction; USER_DIRECTIVE 100% retention)

---

## SUBSTRATE STATE (cert + capabilities; as of 2026-06-27 ~04:55 PDT)

**CERT 622** (latest after Skunkworks batches 7+8+9). Trajectory today: 616 post-batch4 → 617 post-batch5 → 618 post-batch6 → 619 post-batch7 (K=8192 3-seed chain-grade) → 619 post-batch8 (5 atoms: 1 MM + 4 HONEST_NEG; capacity envelope exceeded predicted band) → 622 post-batch9 (+3: capacity v2c GPU chain-grade + Hopfield by-construction-honest-neg + HRR involutive null-honest-neg).

**MAJOR FINDING 2026-06-27 (USER pushback drill)**: META_BARRIER_1_QUADRUPLE_NEGATIVE atom was prematurely declared. Per-arm audit of 5 prior "refutations" = ZERO clean negatives:
- consolidation v3: NAIVE OUT_OF_BAND, tested SHARED-W (brain uses SEPARATE W)
- pointer-chain v1: BASELINE OUT_OF_BAND, never in claimed regime
- WM-scaffold v1: likely shared-W bug (brain uses anatomically separate PFC)
- CSP-gated: binary abort (brain uses graded confidence)
- parallel-vote v2: K-scaling lift 0.40→0.50 is REAL (was framed as regime-artifact)

Re-labeled via META_BARRIER_1_QUADRUPLE_NEGATIVE_RELABEL atom (commit e30925f3). Plus 3 new META rules atomized: per-arm-metrics required before META atomization, brain-mechanism-vs-caricature discipline, USER-pushback triggers verify-the-referent audit.

**BURIED POSITIVE**: bidirectional meet-in-middle v2 ALREADY PASSED CHAIN_GRADE at depth-5 (BIDIR_MEET_MID=0.620 cv=0.064 lift +0.297 over forward). Got lost in narrative; surfaced today.

**M-CFU breakthrough**: FIRST mechanism in edge-importance family to PASS fairness gate (cor=-0.015 vs +0.83 for trace-family). Tonegawa engram-silencing analog; structurally orthogonal to magnitude by construction. Signal strength weak (sel_unretr=+0.048 below 0.15 bar) but conceptually proves the orthogonal-axis path works. M-CFU v6 stronger regime dispatched 2026-06-27 (in queue at offline-window start).

**META rules now atomized** (durable across sessions):
- META_RULE_F: retrieval-success importance signals are magnitude-coupled by construction
- META_RULE_G: smoke discriminator preview ≠ full landed verdict
- META_RULE_H: K-sweep verdicts require per_unit cardinality verification (+ `cardinality_ok` pre-reg field)
- META_RULE_J: no silent except in unit loops (record+halt OR re-raise)
- META_RULE_K: smoke must FIRE discriminator, not just verify cell runs
- META_RULE_L: band-floor results are MIDDLE_BAND, not HARD_PASS
- META_RULE_M: primitive calibration may differ from chain-grade benchmark regime (adaptive iff principled + discriminator-fires + logged)

**Stage 1 chain-grade portfolio** (don't reinvent):
- Storage M=500/N=8192 top1=1.000 / Capacity 25k+ patterns / Pattern completion top1=1.000 from 50% corruption
- WM cap=30 / Sequence binding K=20 / Compositional gen +0.724 lift
- Continual learning (CRISPR forget=0.006)
- SEMANTIC battery v2 FULL 5/6 arms PASS
- Multi-hop depth-15 chain-grade (0.808 at depth 15; extended to 30 today)
- WM multi-bank K=4096 chain-grade (K=8192 single-seed pending 3-seed harvest)
- Refuse-gate V_REL=256 chain-grade
- Intent classifier n=100 chain-grade
- KG ingest (FB15k 584 / ConceptNet 585 / HotpotQA 588)
- ULTRAMETRIC CLUSTERING (CHAIN_GRADE today; first cortex content-extraction win)

---

## CORTEX STATE

**Scaffolding chain-grade**: TWO_TIER generational W / NREM replay / Partition routing M=10M

**Content-extraction FIRST WIN landed**: cortex ultrametric clustering CHAIN_GRADE (banked CERT +1; META_RULE_H validated same-day on K-sweep)

**E-tensor family REFUTED across 6+ attempts**: cor(E,|W|) magnitude-coupling structural (META_RULE_F)

**Edge-importance (Anchor 5) status: KILLED as pure-centrality direction** (research drill 2026-06-27)
- v1 saturated; v2 high-alpha MIDDLE_BAND; both held fairness (cor<<0.30) but sel_unretr below floor
- Research 2x drill (math + brain) verdict: **PageRank is categorically wrong for this discriminator** — centrality saturates in dense networks (PLOS survey of 17 measures); brain importance is retrieval-coupled + temporally-tagged (STC, BTSP, engram literature: "use-count IS the importance signal"); not topological
- **v3 PIVOT**: retrieval-trace × ultrametric-coreness composition (brain-grounded; engram literature; ultrametric already chain-grade). P=0.45 HARD_PASS. Currently being authored.

---

## WAVE 3 BOUNDED-CAPACITY KB STATUS

- ANCHOR 5 dual-store audit smoke landed MIDDLE_BAND (match_rate=0.90 at floor per META_RULE_L); FULL DISPATCHED 2026-06-27 to remote_cpu (USER vetting gate — ≥95% required for promotion)
- ANCHOR 1 partition-by-source v1: smoke routing_acc=1.0 / FULL HARD_FAIL. Diagnosis 2026-06-27: mechanism PASSED (routing_acc=1.0, leak=0.0); over-strict `n_capacity_regression==0` gate + corpus cross-cutting labels were the failure. **v2 Path A (relax criterion) + Path B (set-of-permissible-classes for ~5 cross-cutting queries) being authored.**
- ANCHOR 3 coarse-grain-at-promotion FULL HARD_PASS (cap_drop=0.270, ULTRA gap=+0.470 over RANDOM, USER_DIRECTIVE separation preserved). Likely chain-grade promotion in batch 5 VET.
- ANCHOR 4 time-decay eviction FULL HARD_PASS (eviction_frac=0.515, reingest 30/30, USER_DIRECTIVE 100%, AUDIT_ONLY)
- ANCHOR 2 TWO_TIER promotion still deferred (gated on edge-importance v3 result)

---

## SUBSTRATE-KB STATE

**v1 (metadata index):** filename + edges; 1M+ facts (internal 54k + bio 26k + language 754k). Cosine queries unreliable for specific-doc retrieval; use `--filename-contains` flag (rank-1 cosine=1.0). Continuous-ingest scheduled task every 5 min (pythonw windowless; atomic-swap fix commit 5de28ea1).

**v2 content-chunk (Wave 4) smoke HARD_PASS 2026-06-26 ~21:48** — agent a38d457eada23b1ae:
- 472 chunks from 50 notes-only; 1147 chunks from 152 files across 5 classes
- REINGEST_DET W_l2=0.0 EXACT (byte-equal reproducibility)
- Discriminator FIRED + PASSED (elephant_filename has banana_content; query "banana" returns banana-content chunk from elephant_filename file)
- Real query verified: "USER pivot today" returned actual chunk text from feedback memory file
- Commit 47919ed3
- **Substrate is NOW a real content-KB** (smoke proven; FULL build pending per USER proof-gate)
- **NOT YET LOAD-BEARING for post-compaction**: USER directive 2026-06-27 — "we need to first prove that it will do better than a stale .md and that it's updated regularly before we switch"

**POST-COMPACTION RECOVERY: still DOCUMENT-first** (this BACKUP file via Read). Substrate-vs-MD head-to-head test deferred pending Wave 4 FULL ingest + ritual flip.

---

## SKUNKWORKS BATCH 4 OUTCOMES (landed 2026-06-26 ~21:50)

- 5 cells VET; net CERT +0 (all fail chain-grade per Fix #28 + META_RULE_L band-floor + META_RULE_K vacuous-UD)
- 4 META rules J/K/L/M atomized
- **A5 PRE caught 9 malformed atoms from batches 2+3** (raw-dict shape instead of Atom dataclass — PartitionedStore was load-broken). Repaired in-place (idempotent; provenance preserved in metadata).
- Flag-backs:
  1. Atom.from_dict roundtrip self-test before os.replace (CODIFIED 2026-06-27 in skunkworks.md)
  2. Standalone partition-integrity scheduled task (defense-in-depth; not yet built)
  3. META_RULE_J/K/L as SCHEMA-VET pre-dispatch checks (CODIFIED 2026-06-27 in exp_dev.md)
  4. K=8192 3-seed harvest cell (DISPATCHED 2026-06-27)
- Commit 0aee8765

---

## USER OFFLINE WINDOW 2026-06-27 ~06:25 PDT (flight; low-bandwidth mode)

USER going on flight. Low-bandwidth mode. All ongoing work routes via autonomous remote runners (cpu_runner_0 + gpu_runner_0 at `marsh@home:C:/dev/hd-instrument/`) — they pick up queue.json entries independently of my/USER connection.

**Pre-offline queued (8 cells; orchestrator confirmed enqueued before USER offline)**:
- overnight_queue (GPU): K=8192 3-seed harvest + capacity_sweep higher-alpha (commit 1b851af7)
- remote_cpu_queue: ANCHOR 5 dual-store FULL + ANCHOR 3 v2 chain-grade + Wave 4 v2 tripwire-surfaced (commits 1b851af7 + 5ca8e322)
- (in-flight authoring; will queue when exp_dev a8c94b76e24f6424e returns): edge-imp v4 NREM-replay-modulated trace + ANCHOR 1 v3 self-contained

**Already landed pre-offline**:
- ANCHOR 1 v2 (commit de13ec5b): HARD_FAIL infra-dep (KB_REFERENT_MISSING — upstream `exp_substrate_director_kb_ingest_v1/_arm_full/kb` not provisioned on remote)
- edge-imp v3 (commit de13ec5b): MIDDLE_BAND composition-collapse (TRACE +0.083 only; ULTRA contribution lost in top-K)

**Director's autonomous-overnight setup verified**: remote runners are the load-bearing mechanism per memory `reference_hd_remote_path_and_wake_system_fragility_2026-06-23.md`. They continue independently. Orchestrator spawn ac893205600e9c211 in flight to verify runners alive + restart if dead.

**Edge-importance decision approved (USER 2026-06-27 ~06:18 PDT)**: combined A+B.
- (A) v4 NREM-replay-modulated trace authoring in flight (compose retrieval-trace + replay-consolidation-count; brain STC analog of multi-event accumulation)
- (B) honest-bound atom for v3 at sel_unretr=+0.083 (substrate importance-signal ceiling at this regime) — spawn Skunkworks batch 7 after batch 6 returns

**Director main-thread infra edits NOT YET COMMITTED** (need orchestrator push when alive):
- `tools/predispatch_check.py` — added filesystem-scan fallback for dead landing_notifier
- `backend/substrate_index/schema.py` — added validate_atom_roundtrip() + integrated into save_atoms() (Skunkworks batch 4 flag-back #1 code-level fix)
- `.claude/agents/skunkworks.md` + `.claude/agents/exp_dev.md` — codified disciplines (cardinality_ok + META_RULE_J/K/L/M + Atom roundtrip + NO LOCAL directive)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_no_experiments_local_all_remote_USER_LOCKED_2026-06-27.md` + MEMORY.md index update
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` + `notes/director_LIVE_STATE_2026-06-27.md`

## SKUNKWORKS BATCH 5 OUTCOMES (landed 2026-06-27 ~05:10 PDT; commit 6895100e)

- ANCHOR 3 FULL → **PROVEN_BOUND** (not chain-grade): rec_clst=rec_unclst=1.000 saturates metric cap; USER_DIRECTIVE vacuously satisfied (n_UD=0). RC paths: (1) re-run with n_UD>0 mix; (2) scale n_atoms≥10k to break 1.000 cap. Direct chain-grade promotion path identified.
- Edge-importance v2 high-alpha → MIDDLE_BAND confirmed = effectively HONEST-NEGATIVE for PageRank variant per math+brain drill. v3 pivot validated by cert-owner.
- Wave 4 content-chunk smoke → MEASURED_MECHANISM (infra HARD_PASS only). **Banana/elephant content-vs-filename tripwire NOT in metrics.json** — Skunkworks searched all 3 arm dirs; no banana/elephant strings surfaced. v2-content-KB-not-just-index claim is UNVERIFIED OFF DATA until tripwire is reproducibly logged. **Holds substrate-first ritual flip even longer.**
- CERT delta +0; 3 atoms added; 3 ledger rows; commit 6895100e

## FINAL COMPACTION-PREP STATE 2026-06-27 ~10:55 PDT (USER returned; compaction imminent)

**USER directives reconfirmed**:
- FULL AUTO on LOCAL and REMOTE (NO LOCAL constraint LIFTED)
- Prepare for compaction (imminent)
- Keep working until compaction
- Post-compaction me MUST know everything in flight + goals

**ZERO LANDINGS in last 3h** (suspicious — see Open Issues below). Either queue stalled, hd_metrics_sync stopped, or remote runners died. Spawning orchestrator to verify.

## ALL CELLS DISPATCHED TODAY (status uncertain post-3h-silence)

**On remote_cpu_queue (9 pending + 1 running at offline-window start)**:
1. STUB E typed-routing falsification (P=0.80 close-typed-routing-branch)
2. ProofWiki v2 retry+cache (after v1 fetch returned 0 bytes)
3. v3.2 trace-only arm-count fix (workaround for import-bug)
4. **Cycle 1 brain-pushback 5-arm** (R1+R2+R3+COMBINED; 8h; THE Barrier 1 break test)
5. **M-CFU v6 stronger regime** (4 levers; first-fairness-pass mechanism scaling)
6. M5 reverse-replay self-contained (Mattar-Daw + Foster-Wilson reverse-replay; brain-grounded)
7. Stratified-replay v2 arm-count fix (inline-helpers workaround)
8. **Hopfield v2 regime fix** (alpha 6e-4 sub-critical → 0.049 discriminating regime; M-RULE_W alpha-gate)
9. **ANCHOR 1 v4 calibration+schema fix** (TAU 0.30→0.15 + max files 800 + cardinality split + schema_version fix; P=0.55 HARD_PASS)

**On overnight_queue GPU**:
1. M3 v3 GPU bidirectional depth-scaling (torch.cuda port; 50-200x speedup vs CPU; tests sqrt-scaling beyond d=5)

**In-flight orchestrator agent at compaction time**: aadf48146446cbddc — SCP'ing 12 patched edge_importance cells from systemic import-bug fix (commit fb8ddb1a) so cells in queue work correctly. Stratified-replay v2_proper retry queued behind that.

**Possibly running locally (USER lifted NO LOCAL just now)**: nothing actively, but option opened.

## TODAY'S MAJOR FINDINGS (load-bearing for post-compaction me)

1. **META_BARRIER_1_QUADRUPLE_NEGATIVE was prematurely declared** — per-arm audit (drill 2026-06-27) found ZERO of 5 prior multi-hop "refutations" were clean negatives. All tested caricatures (shared-W instead of separate, binary instead of graded, etc.). Re-labeled atom; 3 new META rules atomized. Multi-hop story is OPEN.

2. **Bidirectional meet-in-middle ALREADY chain-grade** at depth-5 (BIDIR_MEET_MID=0.620 cv=0.064 lift +0.297). Buried in prior session; surfaced today.

3. **M-CFU first fairness-passing mechanism** in edge-importance family (cor=-0.015 vs +0.83 for trace-family). Tonegawa engram-silencing brain analog. Signal weak at +0.048 but conceptually proves orthogonal-axis path works. v6 stronger regime in queue.

4. **Capacity v2c GPU CHAIN_GRADE** at multi-bank K=4 N=8192 alpha=4 headroom=10x. Substrate beats baseline under K-sharding (CERT +1).

5. **Hopfield v1 HARD_FAIL was REGIME error not mechanism** — at alpha=6e-4 (230x sub-critical), every associative-memory rule converges by Hopfield theory. v2 fix at alpha=0.049 discriminating regime in queue.

6. **ANCHOR 1 v3 HARD_FAIL = refuse-gate miscalibration** (TAU 0.30 inherited from filename-index v2 regime; content-chunk regime has cosines 0.14-0.30 — most queries refused on calibration alone). v4 fix in queue.

7. **Systemic import-bug** (load-bearing): v3 edge_importance cell had unguarded module-scope main; importing cells triggered v3's full main loop at import, writing alien partials into IMPORTING cell's output dir. Fixed via __main__ guards on 11 cells + anchor-name check in _seed_checkpoint.py.

8. **Substrate-vs-MD A/B = UNKNOWN** (META_RULE_J halt; substrate-KB not on remote). USER directive then: "keep MD path canonical for now"; now (10:55 PDT): LOCAL constraint lifted so substrate v2 build LOCALLY + A/B locally is now possible.

## NEW META RULES ATOMIZED TODAY (Skunkworks batches 7-9)

- META_RULE_T: per-arm metric verification required BEFORE META atomization (Fix #28 at META layer)
- META_RULE_U: cell-author must show implementation honors brain mechanism's load-bearing feature; caricature-refutations are NOT real refutations
- META_RULE_V: USER pushback triggers verify-the-referent audit by default
- (pending in batch 10): RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER
- (pending in batch 10): RULE_PARTIAL_LOAD_MUST_CHECK_ANCHOR_NAME
- (pending in batch 10): RULE_HARD_FAIL_FIX_MUST_ADDRESS_ROOT_CAUSE_NOT_SYMPTOM
- (pending in batch 10): META_RULE_W: pre-dispatch alpha-in-[0.03, 0.20] gate for associative-memory cells

## POST-COMPACTION ME — DO THESE THINGS IN ORDER

1. Read this BACKUP file end-to-end (you're doing that)
2. Touch heartbeat: `touch d:/AI/hd-instrument/data/heartbeats/research.timestamp`
3. Check landings since 10:55 PDT 2026-06-27: `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -300`
4. SPAWN ORCHESTRATOR FIRST — check remote runner status; runners may have died during 3h-silence window. Verify and revive if needed.
5. If anything landed, SPAWN SKUNKWORKS for batch 10 VET. Include PC_cleanup_attractor_v1 HARD_PASS (CHAIN_GRADE candidate from earlier today).
6. Triage the key results:
   - Cycle 1 brain-pushback (THE Barrier 1 break test; COMBINED≥0.65 at depth-5 → BARRIER BROKEN)
   - M-CFU v6 (sel_unretr≥0.15 → first chain-grade importance signal)
   - M3 v3 GPU (depth-9≥0.45 → sqrt-scaling confirmed)
   - ANCHOR 1 v4 (BASELINE≥0.85 PARTITIONED≥0.80 → routing chain-grade)
   - Hopfield v2 regime fix (lift_over_hebbian≥0.10 → consolidation chain-grade)
   - Substrate-vs-MD A/B (now LOCAL OK; could build v2 + test for real)
7. Spawn next-wave cells per landed-drill recommendations (Cycle 2 conditional on Cycle 1 outcome; ANCHOR 1 v5 if v4 needs further; etc.)

## SKUNKWORKS BATCH 10 CORRECTIONS (2026-06-27 ~11:30 PDT)

🚨 **PC_cleanup_attractor v1 is NOT chain-grade** — RE-TIERED to HONEST_NEGATIVE_PC_NO_OP_AT_SATURATED_REGIME by Skunkworks batch 10. Smoking-guns:
- All 3 arms produce BIT-IDENTICAL fe_per_hop arrays across seeds × depths (PC mechanism is operationally a no-op at this regime)
- `fe_monotone_non_increasing=False` in per_seed data BUT verdict_msg claimed "monotone FE" — direct miscite I propagated
- All arms saturate at rec=1.000 (BIAS-Q suspect-1.000)
- PC may help at noisier/higher-V regime; this cell didn't exercise it. Future drill recommends V≥4096, M≥200, HOP_NOISE sweep.

🚨 **Bidirectional v2 chain-grade is REGIME-SPECIFIC** (not universal). v3 GPU at depth-scaled regime shows bidirectional INDISTINGUISHABLE from forward-half (HARD_FAIL_NO_MEETING_PREMIUM). v2 atom stays valid at v2's regime; needs regime-narrowing annotation. Bidirectional is NOT a general multi-hop solution.

**1 cell STILL with NO local metrics** (sync gap):
- exp_substrate_multihop_brain_pushback_composition_v1 (THE Barrier 1 break test — VERDICT UNKNOWN; cell reportedly "failed" at 07:55Z but no metrics local)

**ProofWiki v2 retry = HARD_FAIL** (n_chunks=0 even with retry+cache). Fetch returns 0 chunks; website may be persistently down OR fetch logic deeper bug. Math/science extractor track blocked until investigated.

**STUB E typed-routing falsification = HARD_FAIL by_construction_saturation** (baseline=0.9991). Bijective routing regime too easy; mechanism never exercised. Can't close typed-routing branch cleanly — needs v2 at harder regime.

🎉 **ANCHOR 1 v4 calibrated = HARD_PASS** (landed local ~16:01Z 2026-06-27). routing_acc=1.0, leak=0.0, ratio_resolved=0.9643, ud_ret=0.9286, non_ud=1.0, tau=0.15. Drill predictions VALIDATED (predicted BASELINE 0.18→0.85, PARTITIONED 0.14→0.80; observed 0.96/0.93). **Substrate partition-routing for content-chunk KB WORKS at scale.** CERT +1 candidate. Substrate-Director-KB story unblocked at the routing layer.

🚨 **Hopfield v2 regime fix STILL HARD_FAIL** (baseline=1.0 at "harder" N_DIM=2048/N_CAT=100). Drill thought alpha=0.049 would discriminate; observed baseline-saturation. Needs EVEN harder regime (try N_DIM=1024 + noise) OR mechanism may genuinely not lift in any sub-saturated regime.

🚨 **Stratified-replay v2 + v2_proper BOTH HARD_FAIL identically** (TRACE cor=+0.060 SURPRISE_NEGATIVE). Drill's premise "TRACE > RAND in cor" appears CONTRADICTED — Cauchy-Schwarz math needs audit before re-dispatch. Same numerics under different code paths confirms it's not a code bug.

🚨 **Cycle 1 brain-pushback SILENT DEATH** — remote dir exists (created 07:55Z) but EMPTY (0 files, 0 bytes). Process died before writing anything. THE Barrier 1 break test verdict = UNKNOWN. Re-dispatch required with try/except + traceback dump at entry. Cell-author hardening recommendation: any cell starts by writing minimal metrics.json with PID/timestamp so silent death is visible.

🚨 **M-CFU v6 = HARD_FAIL** (landed local at 15:33 PDT). Stronger regime did NOT help — best v6 sel=+0.027 ≤ v5_baseline=+0.037. Fairness STILL HELD across most CFU arms (cor mostly < 0.10). TRACE alone @ high-alpha=3.0 reaches sel=+0.088 cor=0.072 (more signal but borderline fairness). **Interpretation**: M-CFU + TRACE share a ~+0.04-0.08 SUBSTRATE-PHYSICS CEILING. Orthogonal-axis path WORKS (passes fairness) but doesn't unlock more signal than retrieval-trace. Substrate importance signal-extraction may simply be CAPPED at this regime/encoder. Path forward: either accept honest-bound at this ceiling + ship anyway, OR pursue encoder upgrade (Path C substrate-owned predictive coding) to break the bound.

**CERT 622 UNCHANGED post-batch-10** (no atoms written to avoid mid-compaction risk; ruling note + verify scripts at `data/session_local/skunkworks/_batch10_*.py` give next-spawn everything needed to atomize 8 ledger rows + 4 META rules).

**META RULE candidates for next-spawn Skunkworks atomization** (drafted in batch-10 ruling note):
- META_RULE_W: pre-dispatch alpha-in-[0.03, 0.20] gate for associative-memory cells
- META_RULE_X_MAIN_GUARD: experiment cells must wrap main in `__name__ == "__main__"` guard
- META_RULE_Y_PARTIAL_LOAD_ANCHOR: partial-load must check anchor-name match (already shipped in _seed_checkpoint.py via systemic import-bug fix)
- META_RULE_Z_FIX_ADDRESSES_ROOT_CAUSE: HARD_FAIL fix must address root cause, not symptom

## OPEN ISSUES AT COMPACTION TIME

- **3h zero-landings silence** — need to verify remote runner state
- **hd_metrics_sync RPC error 267009** has been recurring; manual SCP-direct working but should investigate
- **8 cells queued with import-bug-affected v3 imports** — they may all silently fail until patched v3 is on remote (orchestrator aadf48146446cbddc was SCPing those when last invoked)
- **Substrate-vs-MD A/B can now run locally** (NO LOCAL lifted) — high-value test
- **PC_cleanup_attractor_v1 HARD_PASS** still not atomized — pending Skunkworks batch 10

## OFFLINE WINDOW STATE 2026-06-27 ~07:25 PDT (USER going dormant)

**USER directive**: keep using normal docs (BACKUP path canonical); do NOT build substrate v2 at scale on laptop; defer substrate ritual flip.

**Pipeline saturated for offline window** — both queues full:

**overnight_queue (GPU)**: 1 pending
- M3 v3 bidirectional depth-scaling (commit 7cce0550; 14400s; tests depth-scaling beyond d=5 where bidirectional already chain-grade)

**remote_cpu_queue (CPU)**: 1 running + 7 pending (~30+ CPU-hr nominal)
- RUNNING: K-beam path-sum (M4 alternative to refuted soft-passing; full-N preview showed +0.225 lift)
- Pending: STUB E typed-routing falsification (P=0.80 fix-test) / ProofWiki v2 with retry+cache / v3.2 arm-count fix / multi-hop v2 (chain-gen still constrained at V=500 disallow=320) / BCM v2 init-fix (numerical-stability concern; theta may overflow) / Cycle 1 brain-pushback 5-arm composition (R1+R2+R3+COMBINED; 8h Barrier 1 break test) / M-CFU v6 stronger regime / M5 reverse-replay self-contained (no hdlab/ overwrite)

**4 agents still in flight when USER went dormant** (will return during offline; results in design docs):
- ac3585730ddf8cc58: stratified-replay HARD_FAIL 3x drill
- adbf42cdfa3371216: ANCHOR 1 v3 ratio_resolved 3x drill
- ac7f3006d15a0747b: Hopfield by-construction 3x drill
- a7d830ca09ae2941d: stratified-replay v2 arm-count fix (exp_dev)

**Today's UNKNOWN landings (not failures, but blocked)**:
- substrate-vs-MD A/B = UNKNOWN (META_RULE_J halt; substrate-KB not provisioned on remote — only local). Different from cell quality issue. Path to fix: provision substrate-KB chunk corpus on marsh@home OR run A/B test locally (latter conflicts with NO LOCAL directive; treat substrate-build as INFRA not experiment for the exception).

**CRITICAL FRAMING CORRECTION FOR POST-COMPACTION ME**:
1. "Substrate is canonical post-compaction source" - DEFERRED PER USER 2026-06-27. Read this BACKUP file directly. Local substrate v1 (filename-index) is up + 5-min-fresh — useful as supplementary search (`--filename-contains`) but NOT primary path.
2. Multi-hop compositional reasoning beyond 2 hops - NOT confirmed permanent ceiling. 5 prior "refutations" were caricatures. 7+ brain-correct mechanisms designed; multiple cells queued for tonight. Cycle 1 composition cell is the load-bearing test.
3. CERT 622 includes M-CFU MM as breakthrough atom (first fairness-pass); next promotion candidates = M-CFU v6 (if signal lifts above 0.15) + PC_cleanup_attractor v1 (HARD_PASS discovered but not yet atomized).

## NEXT-SESSION PRIORITY ORDER (for post-compaction me)

1. Read this BACKUP (you just did)
2. Check landings: `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -360`
3. Spawn Skunkworks batch 10 for whatever landed (PC_cleanup_attractor + offline cells)
4. Triage Cycle 1 brain-pushback verdict — if COMBINED >= 0.65 at depth-5 → BARRIER 1 BROKEN (huge)
5. Triage M-CFU v6 verdict — if sel_unretr >= 0.15 → first chain-grade importance signal
6. Triage M3 v3 GPU verdict — if depth-9 >= 0.45 → sqrt-scaling confirmed
7. Process the 3 drill design docs that will land during offline
8. Continue authoring next-wave cells per landed-drill recommendations

## IN FLIGHT (3 agents as of 2026-06-27 ~05:15 PDT)

1. **ab6e0a86a825c21f9** — Orchestrator extended dispatch:
   - Push commit 1b851af7 + queue_add 3 cells: K=8192 3-seed harvest (overnight_queue GPU), capacity_sweep higher-alpha (overnight_queue GPU), ANCHOR 5 dual-store FULL (remote_cpu_queue)
   - Then (via SendMessage at 05:15): commit + push 4 new files (exp_kb_partition_by_source_class_v2.py + exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py + 2 preregs) + queue_add 2 more cells (both remote_cpu_queue)

2. **(authoring complete; files untracked)** ANCHOR 1 v2 + edge-importance v3 cells ready for orchestrator commit+push+queue_add. Untracked paths:
   - `experiments/exp_kb_partition_by_source_class_v2.py` (Path A criterion fix + Path B corpus relabel)
   - `experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` (brain-grounded composition; 4 arms × 3 lambdas)
   - `preregs/2026-06-26_kb_partition_by_source_class_v2.md`
   - `preregs/2026-06-26_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.md`

---

## RECENT KEY DECISIONS (most recent first)

- 2026-06-27 ~04:55: NO EXPERIMENTS LOCAL — ALL REMOTE (USER directive); codified in exp_dev.md core disciplines + MEMORY.md index
- 2026-06-27 ~04:50: Edge-importance pivot to retrieval-trace × ultrametric-coreness (PageRank categorically wrong per math+brain drill)
- 2026-06-27 ~04:45: ANCHOR 1 v2 Path A+B authorized (mechanism passed; over-strict criterion + corpus relabel fixes)
- 2026-06-27 ~04:30: 4 spawn parallel (Skunkworks batch 5 + ANCHOR 1 diagnosis + edge-imp 2x drill + 3-cell remote author)
- 2026-06-26 ~21:55: Wave 4 substrate-KB content-chunk smoke HARD_PASS (substrate now real content-KB; gated on proof vs MD)
- 2026-06-26 ~21:50: Skunkworks batch 4 atom commit (CERT 616; 4 META J/K/L/M; A5 PRE repair of 9 atoms)
- 2026-06-26 ~21:45: ANCHOR 3 FULL HARD_PASS, ANCHOR 4 FULL HARD_PASS, ANCHOR 1 FULL HARD_FAIL, edge-imp v2 high-alpha MIDDLE_BAND

---

## DISCIPLINE QUICK-REFERENCE (most-relevant today)

- **Fix #14:** spawn budget ≤3 in flight default; USER may authorize exceeding (DID 2026-06-27)
- **Fix #17:** cell-author smoke MANDATORY before full dispatch — **now ON REMOTE per USER 2026-06-27**
- **Fix #24:** GPU dispatch MUST actually use GPU (torch.cuda + batched ops)
- **Fix #26:** predispatch_check.py before each cell-author spawn
- **Fix #28:** READ per-arm metrics.json, NOT verdict_msg; default tier MIDDLE; let Skunkworks tier UP
- **META_RULE_H:** sweep-axis cells declare EXPECTED_N_UNITS + cardinality_ok pre-reg field
- **META_RULE_J:** no silent except (catch SPECIFIC class + propagate failure-class to metrics)
- **META_RULE_K:** smoke must FIRE discriminator (vacuous-UD auto-demotes)
- **META_RULE_L:** strictly-above-floor (>=floor + 0.05*band_width) for HARD_PASS
- **META_RULE_M:** calibration_check field in pre-reg (default_ok OR adaptive_with_discriminator_gate)

---

## OPEN DECISIONS / NEXT-STEP PRIORITIES (post-compaction me, in order)

1. Verify 3 spawned cells landed on remote (Skunkworks batch 5 + orchestrator + 2-cell author)
2. Check K=8192 3-seed harvest verdict — if HARD_PASS → chain-grade evidence for K=8192 ceiling
3. Check capacity_sweep higher-alpha verdict — if HARD_PASS → capacity story extended
4. Check ANCHOR 5 dual-store FULL verdict — if ≥95% match_rate → Wave 3 promotion criterion met
5. Check ANCHOR 1 v2 verdict — if HARD_PASS → partition mechanism vindicated
6. Check edge-importance v3 verdict — if HARD_PASS → retrieval-trace × coreness composition validated; brain-grounded importance signal banked; unblocks Wave 3 ANCHOR 2 TWO_TIER promotion
7. Wave 4 substrate-vs-MD head-to-head cell (if all above land OK)
8. Wave 3 ANCHOR 2 TWO_TIER promotion criterion (using v3 importance signal)
9. Math + science ingest extractor design (ProofWiki / OEIS / PubMed / arXiv)
10. Wave 2 compositional understanding cells audit vs Stage 2 specs
11. Fix #26 tooling-gap (predispatch_check should check local landings)
12. 13 RC follow-up items from prior Skunkworks batch 3

---

## SAFETY CONSTRAINTS

- Push to origin/main is harness-DENIED for research role; spawn `hdi_orchestrator` for pushes/remote dispatches
- Register-ScheduledTask requires explicit USER auth (greenlit for hd_director_kb_continuous_ingest)
- No `git add -A` ever; stage by path
- ASCII-only in scripts (no unicode)
- text8 / BPC / bigram-gap NOT relevant evals per USER pivot
- **NO experiments local (USER LOCKED 2026-06-27)**

---

## EMERGENCY: WHAT IF SUBSTRATE-KB IS DOWN?

The filesystem is always canonical. If everything else fails:
1. Read this BACKUP (you're doing that)
2. Read `notes/director_POST_COMPACTION_DIGEST_2026-06-26.md` (pointer-style summary; from prior session)
3. `grep -r "<term>" d:/AI/hd-instrument/notes/ | head -20` (filesystem fallback)
4. Wave 4 substrate-KB v2 content-chunk rebuild: smoke landed; FULL ingest pending (when lands, supersedes v1 metadata-only)

---

-- Research (Opus 4.7-1M) — 2026-06-27 ~04:55 PDT
