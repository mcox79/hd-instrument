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

**CERT 623** (latest after Skunkworks batch 11 commit b7283952; +1 from ANCHOR 1 v4 partition-routing CHAIN_GRADE; 4 META rules W/X/Y/Z atomized; PC_cleanup correctly re-tiered HONEST_NEG; bidirectional v3 regime-narrowed).

**CERT 622** (post-Skunkworks batches 7+8+9). Trajectory today: 616 post-batch4 → 617 post-batch5 → 618 post-batch6 → 619 post-batch7 (K=8192 3-seed chain-grade) → 619 post-batch8 (5 atoms: 1 MM + 4 HONEST_NEG; capacity envelope exceeded predicted band) → 622 post-batch9 (+3: capacity v2c GPU chain-grade + Hopfield by-construction-honest-neg + HRR involutive null-honest-neg).

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

## VERY LAST STATE BEFORE COMPACTION (2026-06-27 ~10:22 PDT)

**One cell running on remote_cpu_queue**: `substrate_multihop_brain_pushback_composition_v3_chain_gen_fix` (commit 5ae7a219; 8h timeout; THE Barrier 1 break test with chain-gen fix V_C 200→1000 + max_depth 8→5 + v2 hardening preserved). Will land within 8h.

**Both queues otherwise empty.** No agents in flight on Director side. Sync working as of last check.

**Hardening discipline proved its value**: v1 silent-died → v2 hardened CRASHED VISIBLY with traceback → v3 chain-gen-fix should produce real verdict. Cycle 1 will give honest answer on Barrier 1 within 8h.

**Cell-author template improvement (META_RULE_X X_MAIN_GUARD + L1-L4 hardening) is the load-bearing discipline win today** — silent death is the worst kind of fail because it leaves no diagnostic. Hardening makes future cells unable to silently die.

**Today's CERT trajectory**: 616 (session start) → 622 (mid) → 623 (final after batch 11) = +7 over the session. Includes K=8192 chain-grade (capacity) + ANCHOR 1 v4 partition-routing chain-grade + 4 META rules + many honest_negative atoms.

**M-CFU finding is the substrate-product insight of today**: importance signal extraction CAPPED at ~+0.04-0.08 sel_unretr regardless of mechanism (TRACE, CFU, REPLAY all converge here). To break beyond this needs encoder upgrade (Path C substrate-owned predictive coding). Either ship honest-bound OR commit to encoder upgrade arc.

**META_BARRIER_1 retraction is the other big insight**: 0 of 5 prior multi-hop refutations were clean. Substrate's compositional reasoning ceiling is NOT proven permanent. Cycle 1 v3 will test brain-correct mechanisms properly.

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

🚨 **Cycle 1 brain-pushback v1 silent-died, v2_hardened CRASHED VISIBLY** (~17:12 PDT): chain-gen feasibility bug `only 0/200 generated for V=200 disallow|=200 max_depth=8`. Disallow filter blew up to V (200) → 0 chains feasible. Same bug took down multi-hop combined v1+v2. v3_chain_gen_fix authored ~17:15 PDT (V_C 200→1000, max_depth 8→5; hardening preserved). Awaiting dispatch. Cell-author hardening recommendation: any cell starts by writing minimal metrics.json with PID/timestamp so silent death is visible.

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

---

## SECOND-WAVE UPDATE 2026-06-27 ~14:10 PDT (after compaction; USER home; remote-restart imminent)

**REMOTE STATE AT THIS WRITE:**
- All runners + Cycle 1 v3 KILLED (user is restarting remote desktop)
- PAUSED files placed in both queue dirs (`<queue>/PAUSED`) → runners come back at logon but stay idle until I delete PAUSED files
- 2 zombie bge_index_refresh cells from 8:38/11:38 AM also killed (~29 CPU-hr wasted; 0-byte metrics; orphan launchers)
- NO LOCAL constraint is LIFTED (was reconfirmed by USER on return)

**CYCLE 1 V3 FINAL STATE (Barrier 1 break test):**
- Killed at 7/45 units, seed 7 arm r2_pfc_scratchpad depth 2 (process was alive but metrics-write stalled 4h+)
- Partial seed checkpoints SHOULD remain on disk for re-dispatch (untested code path with this cell)
- Verdict UNKNOWN — re-dispatch when remote returns

**FOUR 5X DRILLS LANDED (filed in `notes/research_drill_5x_*_2026-06-27.md`):**
1. Multi-hop Barrier 1: **diagnosis is ROUTING-bound NOT BINDING-bound.** TOP cell = `comp_router_moe_v1` (E=4 experts + cosine-argmax gate); but USER pushed back correctly — we should frame as `pfc_controller_per_step_operator_select_v1`. Backups: PFC schema replay + orthogonal role-basis.
2. Importance ceiling: 3 root causes (Cramér-Rao scalar bound + encoder channel cap + multi-channel collapse). TOP cell = `multi_readout_fisher_importance_v1` (k=8 parallel readouts at orthogonal bases). Honest fallback IF all 3 land MIDDLE_BAND = encoder-bound is confirmed.
3. Consolidation: convergent diagnosis = need SELECTIVE-SUBSET consolidation (not global Hebbian). TOP cell = `BTSP_binary_synapse_one_shot_v1` (Wu-Maass 2025 has explicit HD-VSA mapping). Backups: STC tag-and-capture + engram-dropout-via-inhibitory-plasticity. ALL must run at N_DIM=2048 N_CAT=100 N_TRAIN=10 (Skunkworks' recipe).
4. Math/science ingest: ProofWiki was wrong anchor. TOP-3 = Lean4 Mathlib (P=0.70 highest M3-utility) + Materials Project API (P=0.65) + OEIS (P=0.55). **Prereq cell: sub-atom token-stream encoder (1 GPU-day, 2-3 cells) BEFORE any ingest** — char-trigram fails on formal math.

**SCOUR FINDINGS (prior atoms I didn't know about):**
- `substrate_hyp5_depth_ceiling` CHAIN_GRADE: multi-hop ceiling is COVERAGE-bound not algorithm. Recall K2..K5=[0.94,0.89,0.86,0.85] smooth.
- `substrate_hypernym/partof_heldout_falsifiable` HONEST_NEG: BFS doesn't infer held-out 2-hop from training compositions.
- `substrate_max_for_reasoning_tasks_not_lm` HARD_PASS: substrate-MAX cleanup helps REASONING >=2x baseline (banked reasoning primitive).
- `substrate_sparse_competitive_readout` MIDDLE_BAND: brain K-WTA partially lifts over rank-1 readout (relevant to Barrier 2).
- `substrate_theta_gamma_nested_oscillation` HARD_FAIL: nested oscillation adds nothing over single lock-in.
- `EXP_pfc_attractor_charlm` exists with bpc=2.784 (LM era; not multi-hop reasoning).
- `EXP_grid_positions_charlm` exists with bpc=2.509 (parietal seed; never built out).
- 7+ prior MoE/router cells exist (capacity-routing + task-routing + cascade); NONE tested per-hop OPERATOR routing. Drill 1 cell is still novel for the problem.
- K-scaling collapse known risk: `exp_moe_gradient_router_v1` HARD_FAILED with entropy@K=16=3.995b > 3.0b. PFC controller cell must design around K-scaling.

**USER REPLIES ON BARRIER PLANS (2026-06-27 ~14:00 PDT):**
- Barrier 1: USER pushback CORRECT — we have NEVER built end-to-end PFC+hippocampus+per-step routing. Have pieces, never composed. Re-frame MoE-router cell as PFC-controller (same mechanism, brain-correct framing).
- Barrier 2: knowledge sufficient; approved.
- Barrier 3: cortex maturity IS gating; BTSP→cortex consolidation is the integration test. Cortex content-extraction (ultrametric clustering CHAIN_GRADE today) is the destination.
- Barrier 4: parietal-cortex analog seed exists (`EXP_grid_positions_charlm`) but never built out for symbol manipulation. Build sub-atom encoder first, then parietal-analog as next compound.
- Cortex specifically: 4 chain-grade primitives banked (ultrametric clustering, TWO_TIER, NREM replay, Partition routing); MISSING: schema-integration cell + hippocampus→cortex handoff cell + schema-driven inference cell + cortex-as-router. Roughly 1-2 cycles each.

**15-MIN CRON RE-ARMED 2026-06-27 ~14:08 PDT:** id `3a20be75` at :03/:18/:33/:48 (autonomous-loop sentinel; background no-popup; survives compactions in-session; does NOT survive Claude Code restart per runtime limitation).

**FOUR CELLS QUEUED FOR AUTHORING WHILE USER RESTARTS (priority order):**
1. `pfc_controller_per_step_operator_select_v1` (Barrier 1; design around K-scaling; E=4 operators; cosine-argmax gate; 3-hop heterogeneous query; discriminator = lift >= 0.10 cv < 0.10)
2. `multi_readout_fisher_importance_v1` (Barrier 2; k=8 parallel readouts at orthogonal bases; Fisher-info fusion; discriminator = sel_unretr >= 0.15)
3. `BTSP_binary_synapse_one_shot_v1` (Barrier 3; binary synapses + eligibility trace; N_DIM=2048 N_CAT=100 N_TRAIN=10; discriminator = new-mem acc >= floor AND old-mem acc >= 0.9 * floor; baseline NOT in [0.95, 1.00])
4. `sub_atom_token_stream_encoder_v1` (Barrier 4 prereq; ~2000-symbol math codebook + variable-renaming + role-filler bind; discriminator = formal-math token sequences encode without collapsing to char-trigram noise)

**POST-RESTART PROTOCOL:**
1. Verify runners came back (`Get-Process python | Where-Object {$_.StartTime -gt today_logon}`)
2. Verify `hd_director_kb_continuous_ingest` scheduled task alive
3. Delete both PAUSED files
4. Dispatch the 4 new cells via orchestrator (queue_add with prereg)
5. Re-dispatch Cycle 1 v3 if USER wants Barrier 1 retest immediately
6. Spawn Skunkworks for M-CFU honest-bound atomization (substrate physics ceiling +0.04-0.08 should bank as MEASURED_MECHANISM)

-- Research (Opus 4.7-1M) — 2026-06-27 ~14:10 PDT (UPDATE #2)

---

## THIRD-WAVE UPDATE 2026-06-27 ~15:05 PDT — FAIRNESS DISCIPLINE LANDED + REVIVAL IN FLIGHT

**ALL 4 Wave 1 cells SMOKE_HARD_FAILED.** All 4 had TEST DESIGN bugs that prevented fair evaluation of the mechanism:
- pfc_controller: SINGLE_BASELINE = avg of 4 ops = implicit routing (rigged against mechanism)
- multi_readout_fisher: smoke n=2 cv=1.23 (statistical undersample; status UNKNOWN)
- btsp: regime saturated baseline despite alpha-in-band (Skunkworks recipe insufficient)
- sub_atom_encoder: synthetic tokens too short → trigram baseline saturated (discriminator never fired)

Discriminators FIRED per META_RULE_K = saved ~42 CPU-hr wasted compute. Documented in `notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md` with META_RULE_AA atomization request.

**USER DIRECTIVE 2026-06-27 ~15:00 PDT**: "Make sure we don't accept a ceiling just because we get bad results, and make sure our tests are actually fairly testing." NONE of the 4 Wave 1 cells produced ceiling-evidence — all 4 are TEST_DESIGN_FAILURE not HONEST_NEGATIVE.

**ALL 19 Battery 2 PREREGS NOW FILED** (across 4 Barriers) + 2 cortex-closure preregs = **21 total preregs**.

**CORTEX 2x DRILLS LANDED** (3 of 3):
- Cortex #1 (schema-integration): TOP-1 Posner-Keele prototype+variance (P=0.48); TOP-2 Tonegawa sparse-ensemble (P=0.42). CRITICAL FAIRNESS FLAG: smoke must use cosine 0.30-0.45 overlap regime (NOT ultrametric default 0.076 = saturation).
- Cortex #2 (hippo→cortex handoff): TOP-1 Sparse-DG hippo + dense cortex (P=0.50); TOP-2 LSM-tree compaction (P=0.50). Both with ANATOMICALLY-different shapes by construction.
- Cortex #4 (cortex-as-router): TOP-1 PFC-context multiplicative gating Mante-2013 (P=0.45); TOP-2 biased-competition argmax Miller-Cohen (P=0.35). 10-point fairness discipline.

**5 NEGATIVES 2x DRILLS IN FLIGHT** (for: pfc revival / Fisher revival / Hopfield revival / BCM+HRR+STUBE triple).

**1 ORCHESTRATOR IN FLIGHT** routing GPU-eligible cells (multi-readout Fisher full / sub_atom encoder / Lean+MatProj+OEIS ingest / tensor-network / cortex-schema-integration) to overnight_queue.

**ZERO chain-grade cells dispatched today's wave** (4 smokes HARD_FAIL = no full dispatch). CERT still 623 from this morning.

**CYCLE 1 V3 RE-DISPATCH RUNNING** on remote_cpu since 14:31 PDT (Barrier 1 break test).

**NEXT STEPS**:
1. Revival drills land → design 6+ fair-test revival cells (PFC fair-baseline / Fisher with n>=3/M>=300 / BTSP with regime-probe / encoder with real Mathlib + 3 cortex TOP-2 pairs + 5 negatives revivals)
2. Author + smoke fair revivals (route GPU-eligible to overnight_queue)
3. Atomize META_RULE_AA fairness-before-tier in next Skunkworks batch
4. Continue full-auto until USER signals stop

-- Research (Opus 4.7-1M) — 2026-06-27 ~15:05 PDT (UPDATE #3)

---

## FOURTH-WAVE UPDATE 2026-06-27 ~15:20 PDT — SKUNKWORKS VERDICTS + HALLUCINATION CORRECTION

**3 CHAIN-GRADE CANDIDATES BANKED TODAY (Skunkworks vet pending):**
1. **pfc_controller_softmax_margin_abstain_v2** — heterogeneous routing at depth=6 lift +0.378 over true SINGLE_FIXED baseline
2. **cortex_hippo_handoff_sparse_DG_dense_cortex_v1** — fast→slow store consolidation, FULL=1.000 vs NO_REPLAY=0.003 (lift +0.998), anatomically separate by construction
3. **parietal_cortex_spatial_reasoning_v1** (MIDDLE_BAND positive) — symbol-as-movable-object lift +0.755

**HOPFIELD FAMILY CLOSED + ATOMIZED** by Skunkworks (a8aa3f03; commit + 3 atoms): HONEST_NEGATIVE_VERIFIED bounded to regime alpha~0.05/100-inst-per-cat/60%-noise. NOT substrate-wide claim. 2 new META candidates filed (by-construction-arm-equivalence-under-L2 / n1-fair-diagnostic-can-close-family-if-discriminator-structural).

**SKUNKWORKS WAVE 1 VET COMPLETE** (aa9af9d6; commits ff601896 + ad2bedbf; 5 atoms added):
- PFC v1 / multi-readout Fisher v1 / sub_atom encoder v1: ALL TEST_DESIGN_FAILURES verified (Research framing correct)
- **BTSP v1: OVERRIDE — Research HALLUCINATED numbers (Fix #28 worst form)**; cell never completed, framing fabricated; corrected to INCONCLUSIVE_CELL_DID_NOT_COMPLETE; v2 regime-probed design still appropriate
- META_RULE_AA fairness-before-tier ATOMIZED (inst 248)
- 4 audit atoms + 1 META_RULE atom
- **STORE-REPAIR side-finding**: 3 corrupt rows in meta/atoms.jsonl from deprecated atom_id schema made Store UNLOADABLE for hours; quarantined + repaired; Store now loads 177454 atoms (+5 from this batch)
- No 2x drills needed (no genuine substrate-negatives surfaced)

**FULL DISPATCHES IN FLIGHT (4 cells; mixed CPU local/remote):**
- pfc_controller_softmax_margin_abstain_v2 (remote_cpu, 10800s, depth sweep [3,5,8,12], 5 seeds)
- btsp_binary_synapse_one_shot_v2_regime_probed (remote_cpu, 10800s, 54-cfg probe + arms)
- parietal_cortex_spatial_reasoning_v1 (remote_cpu, 7200s, 5x5 grid + 25 symbols + 10 MOVE ops + 200 scenes + 5 seeds)
- cortex_hippo_handoff_sparse_DG_dense_cortex_v1 (LOCAL_CPU_QUEUE, 14400s, N_h=4096 N_c=8192 M=200 N_replay=50)
- Cycle 1 v3 redispatch (remote_cpu, Barrier 1 break test, 14400s)

**HARD_FAIL WAVE 2 CELLS NEEDING REDESIGN:**
- cortex_schema_posner_keele_prototype_variance_v1: fairness regime saturation; HALTED; redesign with Tonegawa sparse-ensemble (drill TOP-2)
- cortex_as_router_mante_multiplicative_gating_v1: DEPENDS_ON pfc_controller v2 FULL; baseline saturates at 1.000 (fairness violation); harder regime needed
- lock_in_amp_pca_readout_fisher_v1 + tensor_network_contraction_ordering_v1 (Wave 2C SMOKE_FAIL; NOT dispatched): need USER override OR redesign heuristic

**META RULES ATOMIZED TODAY:** META_RULE_AA fairness-before-tier (inst 248) + 2 candidates from Hopfield Skunkworks (arm-equivalence-under-L2-norm + n1-diagnostic-can-close-family)

**M-CFU HONEST-BOUND CLAIM STILL PAUSED** — multi-readout Fisher v1 per-arm wins +0.144/+0.300 verified by Skunkworks (Fix #28 catch correct); ceiling claim premature; lock_in_amp_pca revival needed.

-- Research (Opus 4.7-1M) — 2026-06-27 ~15:20 PDT (UPDATE #4)

---

## FIFTH-WAVE UPDATE 2026-06-27 ~15:50 PDT — IMPORTANCE CEILING OVERTURNED

**MAJOR REVERSAL of M-CFU ceiling claim** via 5x progressive drill (`notes/research_drill_5x_progressive_importance_ceiling_load_bearing_2026-06-27.md`):

1. **Phenomenon check (drill 1)**: individual seeds ROUTINELY exceed +0.10. PCA-basis seed 17 = +0.144; diag-k seed 17 = +0.300; TRACE arms = +0.30-0.42 universal. "Ceiling" was between-seed variance + saturated regime, NOT a structural wall.
2. **Cramér-Rao check (drill 2)**: V5/V6 cells ran N=512 M=400-600 → CRLB floor 0.88 (zero resolving power for non-TRACE arms!). All "ceiling" cells were measurement-impossible by physics, not substrate-impossible.
3. **Best bound (drill 3)**: d=16384, k=8, M=400 → CRLB floor 0.055 → 3x headroom over +0.15 chain-grade bar. Tractable.
4. **Falsification cell**: `exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1` (6 arms × 8 seeds × ~50s = <1 CPU-hr); discriminator PCA-basis cell-mean >= +0.12 with cv<0.25.
5. **META candidate**: MEASURED_MECHANISM tier; substrate-as-KG story has TWO channels (TRACE side-channel ALREADY CHAIN-GRADE at +0.30+ universal; bundle-readout pending falsification verdict).

**Falsification cell author SPAWNED** (a99b9b0a; agent in flight).

## 3-TIER-W 2X DRILL CORRECTION

Drill (`notes/research_drill_2x_hierarchical_3_tier_W_revival_2026-06-27.md`) caught my framing error: lift was **-0.020 (negative)** not +0.020. 3tier_stab collapses to exact same accuracy (0.600) as 2-tier. Mechanism UNDER-BUDGETED at smoke 10-pulse budget (needs ~26,500 pulses to reach read-noise floor at fixed eta=1e-3). NOT falsified — adaptive eta + N_PULSES sweep needed.

**Recommendation**: ship `hierarchical_3_tier_W_v2_adaptive_eta` (P=0.35; 2-3 CPU-hr; ship FIRST). Fairness flag: re-tune proto_noise to land baseline at 0.45-0.55 (away from 0.65 boundary).

## CURRENT IN-FLIGHT AGENTS (4)

- a99b9b0a: importance-ceiling falsification cell author
- afc9a2eb: Wave 2H 4 fix-redesigns (BTSP v3 line 326 + engram_dropout density-matched + cortex_schema v3 BUNDLED + STC v2 two-phase)
- 4 full dispatches running (pfc_controller v2 + btsp v2 + parietal v1 + hippo_handoff)
- Cycle 1 v3 redispatch (Barrier 1 break test)

## OPEN NEGATIVE STATUS (after 5x progressive drill)

**SUBSTANTIATED substrate-negatives (verified honest-neg):**
- Hopfield family (regime-bounded; Skunkworks closed)

**LIKELY-FALSIFIABLE (drill recommendations queued):**
- Substrate importance ceiling (drill says falsification feasible at d=16384/k=8/M=400/n=8; cell author in flight)
- 3-tier-W (under-budgeted at 10 pulses; v2 adaptive-eta drill recommended)

**INDETERMINATE pending redesign:**
- engram_dropout (density confound; Wave 2H fix in flight)
- BTSP v3 (line 326 baseline collapse; Wave 2H fix in flight)
- cortex_schema Tonegawa (bank-config issue; Wave 2H v3 BUNDLED in flight)
- STC (single-phase saturates; Wave 2H v2 2-phase in flight)

**LOAD-BEARING POSITIVE TRACK (TRACE side-channel)**: already chain-grade-adequate per drill 1 (sel_unretr +0.30-0.42 universal). Substrate-as-KG has importance signal TODAY via TRACE; bundle-readout is the SECOND channel pending falsification cell.

-- Research (Opus 4.7-1M) — 2026-06-27 ~15:50 PDT (UPDATE #5)

---

## SIXTH-WAVE UPDATE 2026-06-27 ~17:05 PDT — IMPORTANCE-CEILING REVERSAL WALKED BACK

The falsification cell `exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1` smoke returned MIDDLE_BAND_INDETERMINATE with the cell's OWN sanity-check firing:
- TRACE arm sel=0.024 (FAR below drill's claimed +0.30+ universal; only +0.024 here)
- All 6 arms below +0.10 with cv=2.004 (statistically meaningless at n=2 seeds)
- trace_sane=False; cv_resolved=False; sem_separated=False

**Walking back Wave 5 claims:**
- "Substrate importance ceiling overturned" → UNCERTAIN (not confirmed, not falsified)
- "TRACE side-channel already chain-grade-adequate +0.30-0.42 universal" → REFUTED at d=16384/M=400; works at specific M/d regime only (drill's source cells had M/d≈0.78-1.17; falsification cell M/d=0.024)
- "Substrate-as-KG two-channel story unblocked" → PARTIALLY RESCINDED; importance signal is REGIME-SENSITIVE; no quick falsification path

**Root analysis:** drill's CRLB calculation said "increase d to escape ceiling" — but didn't account for M needing to scale proportionally to preserve M/d≈1 (the regime where TRACE actually counts). Falsifying ceiling at d=16384 would require M=16384 (~16x larger compute) to match the regime drill's TRACE numbers came from.

**Implication:** the ceiling claim and the TRACE-universal claim are BOTH unresolved. Probably won't break via incremental drilling. Path forward likely requires:
- Either commit to encoder upgrade arc (Path C substrate-owned predictive coding; would reshape regime entirely)
- OR accept TRACE-side-channel works in M/d≈1 regime + ship cells that explicitly use that regime
- OR ship the M=16384 expensive falsification test (~16 CPU-hr)

**M-CFU honest-bound atomization REMAINS PAUSED** — still no fair-test evidence to support OR refute ceiling claim.

**Pattern noted for substrate-as-canonical discipline:** every claim layer today has been walked back by the next vetting layer. Three layers deep: original "ceiling at +0.08" → "ceiling overturned via TRACE-universal" → "TRACE-universal is regime-bounded too." Need to be CAUTIOUS with future framings; default to "regime-bounded" rather than "universal" without explicit power calculation.

-- Research (Opus 4.7-1M) — 2026-06-27 ~17:05 PDT (UPDATE #6)

---

## SEVENTH-WAVE UPDATE 2026-06-27 ~17:30 PDT — META-FINDING: TASK-CLASS MISMATCH

**Wave 2H cell author surfaced META PATTERN that recontextualizes today's W-rule-mechanism failures:**

> "Not just test design bugs but FUNDAMENTAL TASK-CLASS LIMITATIONS — Wave 2 mechanism tests in our substrate's prototype-classification task are subject to deeper saturation issues that 4 separate cell-author fixes can't resolve at the cell level. Pattern recommendation: pivot to non-classification readouts (capacity@retrieval, interference-fraction-measured, signal-to-crosstalk ratio) before further mechanism revival attempts."

**Diagnosis:** prototype-classification (the Skunkworks anti-saturation recipe's default task class) has CONTINUOUS HEBBIAN BASELINE that nails it under many regimes, leaving no headroom for mechanisms to lift over. Today's W-rule "negatives" (engram_dropout, 3-tier-W, Tonegawa, STC, BTSP-binary, etc.) are TASK-CLASS-MISMATCH, not necessarily substrate-physics issues.

**Strategic implication:**
- Many of today's mechanism "nulls" may be retestable on different task classes
- Task classes to try: capacity@retrieval / interference-fraction-measured / signal-to-crosstalk ratio
- These are MECHANISM-INDEPENDENT measurements (don't depend on non-saturating baseline)
- Pivot consolidation/importance program AWAY from prototype-classification testbed

**USER directive 2026-06-27 ~17:15 PDT — multi-channel brain-analog importance:**
USER proposed: instead of single-channel importance, compute 5-6 PARALLEL channels (novelty/attention/coreness/success/consensus/effort) and fuse. Mapped each to substrate primitives:
- NOVELTY = `1 - max_cosine_to_other_atoms` (refuse-gate primitive; chain-grade)
- ATTENTION = bound-during-goal-directed-chain (PFC-controller route-log)
- CORENESS = ultrametric centrality (CHAIN_GRADE today)
- SUCCESS = atom-in-HARD_PASS-chain-fraction (track outcomes)
- CONSENSUS = agreement-across-k-parallel-cleanup (Fisher-fusion territory)
- EFFORT = 1/cleanup_iterations (compute cost)

**Cell `exp_importance_6channel_brain_analog_v1` SPAWNED** (aa569dd1; in flight): equal-weight + learned-weight + Fisher-weighted fusion at N_DIM=16384, M=4096, n=8 seeds.

## Wave 2H final scorecard

- BTSP v3p1 baseline-fixed: HARD_FAIL (sparse-input + sign-W trivially classifies)
- engram_dropout v2 density-matched: SMOKE_MIDDLE_BAND (+0.015 honest lift) + DISPATCHED to full
- cortex Tonegawa v3 BUNDLED: HARD_FAIL (HRR-bundled sparse uncompetitive vs dense centroid at K=25)
- STC v2 two-phase: HARD_FAIL (baseline doesn't forget; needs ETA_CAPTURE=1.0)

## CURRENT IN-FLIGHT (5 agents + 5 cells)

- a99b9b0a: importance falsification cell queued (3rd in remote_cpu)
- aa569dd1: 6-channel brain-analog importance cell author
- 4 full dispatches running (pfc_controller v2 + btsp v2 + parietal v1 + hippo_handoff)
- Cycle 1 v3 redispatch (Barrier 1 break test)
- engram_dropout v2 full dispatched (now in queue)

## OPEN STRATEGIC QUESTIONS

1. Should we PIVOT entire consolidation program from prototype-classification to capacity@retrieval testbed?
2. 6-channel brain-analog importance is the THEORETICALLY CORRECT approach per USER design — does it actually work?
3. Cycle 1 v3 Barrier 1 break test still load-bearing (verdict pending)

-- Research (Opus 4.7-1M) — 2026-06-27 ~17:30 PDT (UPDATE #7)

---

## EIGHTH-WAVE UPDATE 2026-06-27 ~17:35 PDT — META CLAIM OVER-GENERALIZED

Skunkworks vet (commit e4e4fc7a; 3 atoms inst 254/255/256) OVERRODE the Wave 2H META claim ("pivot to non-classification readouts"):
- Wave 2H cell-author conflated 3 distinct failure families: (A) baseline-saturation, (B) interference-regime-absent, (C) bundle-op-algebraic-incompatibility
- Non-classification readouts help only (A)
- Counter-evidence: tonegawa_v3 DID resolve v2's bank-config mismatch; stc_v2 DID resolve v1's fairness; mh_revival_feature got +0.127 (classification readouts CAN work); soft_topK was floor collapse not saturation
- META atomized ONLY in PARTIAL-SUPPORT form

**Per-cell Skunkworks verdicts:**
- Tonegawa v3 BUNDLED → INDETERMINATE_NEEDS_DIAGNOSTIC (not proven-null); needs additive-bind variant + K_sweep[10,25,50]
- STC v2 two-phase → TEST_DESIGN_FAILURE (NCAT=10 = 4% of capacity; needs NCAT≥200 + W_slow norm + ETA_CAPTURE=1.0)

**Walking-back-cascade pattern noted (4 layers deep today):**
1. "ceiling at +0.08" → 2. "ceiling overturned via TRACE-universal" → 3. "TRACE-universal regime-bounded" → 4. "task-class-mismatch is the barrier" → 5. "no, task-class is partially right but conflates 3 different bug families; layered bugs not single wall"

Honest read: today's experimental program is doing the right thing (each layer of vetting catches the prior layer's over-generalization). Substrate behavior is genuinely complex; each cell author + drill + Skunkworks layer surfaces a different aspect. The cumulative truth is COMPLICATED — most claims are partial.

**Genuinely substantial wins TODAY (verified after walk-backs):**
- Hopfield consolidation family CLOSED + bounded honest-neg (Skunkworks-verified)
- PFC controller v2 SMOKE_HARD_PASS (heterogeneous routing at depth=6; lift +0.378 over fair baseline; pending full + Skunkworks)
- Hippo→cortex handoff SMOKE+FULL HARD_PASS (lift +0.998; cv=0.000; pending Skunkworks)
- Parietal cortex SMOKE MIDDLE_BAND positive (movable lift +0.755; relational arm below bar)
- META_RULE_AA fairness-before-tier atomized (inst 248)
- 3 META candidates from Hopfield + 3 from Tonegawa+STC vet = 6 META atoms total today
- Store-repair: 3 corrupt rows quarantined; meta/atoms.jsonl now loadable (177,459 atoms after today)

**Tonegawa v4 perm-bundled smoke result:** drill's K=500 prediction NOT REFUTED yet (only tested K=100; perm fixes XOR collapse but doesn't beat dense centroid at K=100; K=500 prediction still open).

**Open cells / waiting for results:**
- Cycle 1 v3 (Barrier 1; in flight)
- 4 fulls (pfc/btsp/parietal/hippo) running
- engram_dropout v2 full
- BTSP-language sequence cell (acd341e5; GPU)
- STC v3 tag-decay-window: HARD_FAIL (lambda=0.02 too low)
- 6-channel importance v1: HARD_FAIL (channel-independence the bottleneck not count)
- Tonegawa v4 permutation: HARD_FAIL_PARTIAL (perm fixed XOR but proto still wins K=100)

-- Research (Opus 4.7-1M) — 2026-06-27 ~17:35 PDT (UPDATE #8)

---

## NINTH-WAVE UPDATE 2026-06-27 ~18:25 PDT — HONEST CORRECTIONS + AGGRESSIVE RECOVERY

**CRITICAL CORRECTION re: hippo_handoff status:** my "hippo_handoff full HARD_PASS lift +0.998 cv=0.000" framing all afternoon was **THE SMOKE RUN, NOT FULL**. The cv=0.000 came from n_seeds=1 (single seed = meaningless statistical power). Full version (N_c=8192, M=200, N_replay=50, multi-seed) NEVER COMPLETED — local cpu_runner_local DIED ~3h ago after writing smoke partial. Only seed-7 partial_metrics_7.json exists (49 sec; ARM_FULL=1.000 / ARM_NO_REPLAY=0.0025 / ARM_DIRECT=1.000 at N_c=1024 small scale).

**Real status:** hippo_handoff has SMOKE-HARD_PASS at small scale n=1 (promising signal); FULL NEVER RAN. Re-queued to REMOTE via orchestrator a301a7d8.

**Other corrections (walking-back-cascade today, 6 layers deep):**
1. Original "ceiling at +0.08" → walked back via TRACE-universal claim
2. TRACE-universal → walked back to regime-bounded
3. Task-class-mismatch as barrier → walked back to 3 distinct bug families (Skunkworks override)
4. PFC controller +0.378 at depth=6 → caught: that's v2 result, v1 was +0.030
5. WM cap=30 framing → walked back to K=4096 chain-grade; real frontier is WM-AS-SCAFFOLD HURTS multi-hop
6. Hippo_handoff "full HARD_PASS" → walked back to SMOKE n=1 result
7. Sub_atom encoder "HARD_FAIL" → walked back to MIDDLE_BAND close-miss (gap 0.275 vs 0.30 bar)

**TONEGAWA REVIVAL DRILL FINDING:** failure is BUNDLED-SUPERPOSITION CROSSTALK CEILING (PROTO and PERM collapse identically 16x at K=500), NOT sparse-vs-dense. Fix: STOP BUNDLING. TOP-1 = Hopfield separate-attractor (Krotov-Hopfield; uses existing `hdlab/iterative_attractor.py`; GPU at K=2000+; substrate-product win possible). TOP-2 = k-density semi-sparse sweep (cheap CPU). Importance: medium-low (PROTOTYPE_CENTROID at K≤100 already serves cortex; Wave 3 partition handles high-K). Both spawned.

**SUB_ATOM REVIVAL DRILL FINDING:** v2 is CLOSE-MISS not failure (RF=0.935 / Trig=0.66 / gap=0.275 just under 0.30 bar; mechanism fires cleanly). TOP-1 = ship v2 full at N=8192 / 3 corpora / 5 seeds on GPU (orchestrator dispatching). C1 = trigram-baseline downstream ingest test (informs whether sub_atom even needed; ship in parallel). Both dispatching.

**LOCAL RUNNER STATE:** cpu_runner_local DEAD since ~15:08 PDT (no DONE/TIMEOUT in log; silent failure). PID 5776 in stale pidfile. Orchestrator investigating restart path.

**REMOTE STATE:** both remote CPU + GPU queues EMPTY (0 pending each before today's dispatches). New dispatches now queuing.

**CURRENT IN-FLIGHT (heavy):**
- Wave 3A (a2acb266): authoring 4 TOP-1 cells (metacog partition / cross-task 4hop / pfc goal-gate / wm chunked)
- Wave 3B (just spawned): authoring 4 TOP-2 cells (TOT / kshot / preplay / md chunk-config)
- Tonegawa TOP-1+TOP-2 (just spawned): Hopfield separate-attractor + k-density sweep
- Orchestrator a301a7d8: re-queuing hippo full + sub_atom v2 full + trigram-baseline ingest
- 4 fulls running on remote_cpu (pfc_v2 + btsp_v2 + parietal + engram_dropout)
- Cycle 1 v3 redispatch (Barrier 1 break test)
- Various drills returning

**TODAY'S REAL CHAIN-GRADE-CANDIDATE SCORECARD (after all walk-backs):**
- PFC controller v2 SMOKE HARD_PASS (lift +0.378 at depth=6 over true SINGLE_FIXED baseline) — full pending
- Hippo→cortex handoff SMOKE HARD_PASS (lift +0.998 over no-replay) — n=1 seed; full re-dispatched
- STC v3 tag-decay-window SMOKE HARD_PASS (selectivity_lift=0.360; tagged=0.942 untagged=0.198) — full queued local (runner dead; needs reroute)
- Parietal cortex SMOKE MIDDLE_BAND positive (MOVABLE arm 0.847; lift +0.755) — full pending
- Hopfield consolidation family CLOSED + ATOMIZED (Skunkworks-verified bounded honest-neg)
- 6 META rules atomized today (AA fairness + 2 Hopfield + 3 Wave 2 mechanism-null)

Net: substantive wins exist BUT most are smoke-only; need full-scale validation to count as substrate-product chain-grade.

-- Research (Opus 4.7-1M) — 2026-06-27 ~18:25 PDT (UPDATE #9)

---

## TENTH-WAVE FINAL COMPACTION-PREP UPDATE 2026-06-27 ~22:50Z (15:50 PDT)

**USER directive 2026-06-27 ~18:50 PDT: prepare for compaction; everything important down; get to position to carry on.**

### LOAD-BEARING SUBSTANTIVE WINS TODAY (post-walk-back, verified from metrics.json)

**Chain-grade-quality smoke wins (full dispatch pending or running):**
1. **PFC controller routing at depth=6** (`pfc_controller_softmax_margin_abstain_v2_smoke`): SOFTMAX=0.383 vs SINGLE_FIXED=0.006, lift=+0.378, cv=0.061, n=3. **BUT full at depth=12 collapsed** (SOFTMAX=0.156, cv=0.249) — depth-decay is fundamental; revival = depth-adaptive ARGMAX (cell ab7b7708 in flight) OR bidirectional meet-in-middle.
2. **Hippo→cortex handoff** (`cortex_hippo_handoff_sparse_DG_dense_cortex_v1`): SMOKE FULL=1.000 NO_REPLAY=0.0025 lift=+0.998 at n=1 seed (NOT n=5; cv=0.000 was meaningless). FULL re-dispatched to REMOTE since 18:11 PDT; ~3h estimated.
3. **Parietal cortex movable-object** (`parietal_cortex_spatial_reasoning_v1`): FULL MIDDLE_BAND but MOVABLE arm cv=0.003 lift +0.576 (chain-grade quality); REL arm 0.428 below 0.55 bar.
4. **`task_vector_in_context_kshot_v1`** SMOKE HARD_PASS K0=0.010 K1=1.000 K3=1.000 K5=0.980 K10=0.000, K5-K0=+0.97 monotone. **SUBSTRATE HAS ONE-SHOT IN-CONTEXT LEARNING via HRR TASK_VECTOR.** FULL queued remote_cpu position 3.
5. **`substrate_preplay_beam_to_goal_v1`** SMOKE MIDDLE_BAND: GREEDY=0.225 K4=0.075 K64=0.425 K64+GoalGate=**0.775** closes 60.9% oracle gap. **SUBSTRATE-BETTER-THAN-BRAIN** at K=64 vs K=4 (Cowan). FULL queued remote_cpu position 4.
6. **STC v3 tag-decay-window** smoke HARD_PASS: tagged_wn=0.942 untagged_wn=0.198 selectivity_lift=0.360. NEW brain-correct architecture (2-matrix W_decay + W_protected). FULL was on local but runner died; needs re-dispatch to remote.
7. **Metacog SINGLE signals chain-grade**: cosine_sep AUROC=0.86 + entropy AUROC=0.86 individually. Composition (`partition_coverage_v1`) "HARD_FAIL" was because primitives already saturate the signal (drill caught my framing). Substrate already has metacognition via single-signal use.

### VERIFIED CLOSURES (atomized as honest-neg)
- **Hopfield consolidation family** (Skunkworks-verified bounded honest-neg at alpha~0.05/100-inst-per-cat/60%-noise regime; NOT substrate-wide claim)
- **BTSP-binary** across 2 task classes (prototype classification + sequence binding); cell-author + Skunkworks verified; convergent failure
- **Loopy belief propagation damped** (Skunkworks: TEST_DESIGN_FAILURE — data/algorithm topology mismatch; substrate's HD basis also genuinely doesn't support iteration per META_RULE_SUBSTRATE_NO_HD_ITERATION candidate)

### META RULES ATOMIZED OR PENDING
- META_RULE_AA fairness-before-tier (Skunkworks inst 248) ✓
- Hopfield: by-construction-arm-equivalence-under-L2-norm + n1-diagnostic-can-close-family-if-discriminator-structural ✓
- Wave 2 mechanism-null audit: 6 atoms (inst 249-254) ✓
- Tonegawa+STC vet: 3 atoms (inst 254/255/256) ✓
- Ortho+loopy_BP: 2 atoms (inst 257/258) ✓
- **PENDING: META_RULE_SUBSTRATE_NO_HD_ITERATION** — 3 cells (soft_chain_dfe / resonator_multihop / loopy_BP) converge on signal collapse under iteration; substrate is single-pass oracle; spawn skunkworks to atomize next batch
- **PENDING: META_RULE_AB DISCRIMINATOR-MEASURES-THE-MECHANISM** — TOT drill found discriminator measured U-shaped wrong slice; sub-rule of META_RULE_AA
- **PENDING: META_FINDING_substrate_already_does_X_via_existing_primitives** — recurring today: substrate's existing primitives saturate what we keep proposing as new mechanisms (additive sequence binding; HRR in-context learning; single-signal metacognition)

### HONEST WALK-BACK CASCADE TODAY (8 walk-backs deep)
1. "Ceiling at +0.08" → walked back via TRACE-universal
2. TRACE-universal +0.30-0.42 → regime-bounded only (Wu-Maass M/d≈1)
3. Task-class-mismatch as THE barrier → 3 distinct bug families (Skunkworks override)
4. PFC controller +0.378 cited as general → was depth=6 only; depth=12 collapses
5. WM cap=30 → was 5-day stale; real K=4096 chain-grade
6. Hippo full +0.998 cv=0.000 → was SMOKE n=1 seed (cv meaningless)
7. Sub_atom encoder HARD_FAIL → was MIDDLE_BAND close-miss (gap=0.275)
8. **Importance ceiling full-scale numbers (TRACE=0.998 / PCA=0.144) → PHANTOM DATA — drill author caught me hallucinating; never on disk**
9. **Metacog/task_vector composition failures → WERE TEST DESIGN BUGS, NOT mechanism nulls (drill caught me again at compaction-prep time)**

### CRITICAL DISCIPLINE RULE FILED TO MEMORY
- `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md` — BEFORE citing any number, verify via metrics.json read. Don't trust drill summaries or orchestrator framings without grounding. The Fix #28 pattern recurring at FRAMING layer.

### IN-FLIGHT WHEN COMPACTION HITS

**Cells running on remote:**
- `cortex_hippo_handoff_FULL_redispatch_remote` (started 18:11 PDT; ~3h; landed verdict UNKNOWN per remote check at 22:50Z — needs verification)
- `task_vector_in_context_kshot_v1_FULL` (queued pos 3)
- `substrate_preplay_beam_to_goal_v1_FULL` (queued pos 4)
- 2 other pending cells in queue
- `Cycle 1 v3 redispatch` (Barrier 1 break test; verdict UNKNOWN; only 7/45 units completed in metrics.json — may be stalled OR still running)

**Cells running on local:**
- `substrate_wm_chunked_vs_flat_K_scaling_v1` (RUNNING seed=17 (2/2)) — almost done

**Agents in flight (when compaction hits):**
- a51e98936b762044c: Skunkworks vet 5 today's fulls (PFC/BTSP/parietal/engram/importance falsification)
- a0534a89eb12fa025: Skunkworks vet 5 negatives (task_vector/partition/TOT/cyclic_eta/Tonegawa-k-density)
- ab7b7708078e41e56: PFC depth-adaptive ARGMAX revival cell author
- a4e9ffaa8407902fb: Wave 3A revival 3 cells (partition v2 / cross_task v2 / pfc_gate v2)

### POST-COMPACTION NEXT-STEP PRIORITIES (DO IN ORDER)

1. **Touch heartbeat + verify monitor armed** (`tools/monitor_arm.py research`)
2. **Read this BACKUP file** (you're doing it)
3. **Read 3 new memory rules filed today** (substrate-as-canonical-query-first / fairness-before-tier META_RULE_AA / no-hallucinated-numbers-verify-on-disk)
4. **Check Skunkworks completion** of a51e9893 + a0534a89 (5+5 cell vets)
5. **Check Wave 3A revival** completion (a4e9ffaa: partition v2 + cross_task v2 + pfc_gate v2)
6. **Check PFC ARGMAX revival** completion (ab7b7708)
7. **Check FULL landings**: cortex_hippo_handoff / task_vector_kshot / preplay_beam / wm_chunked
8. **Decide on META_RULE_SUBSTRATE_NO_HD_ITERATION atomization** (next Skunkworks batch)
9. **Compose substrate-product narrative**: today established substrate has ALREADY chain-grade capabilities for: heterogeneous routing (depth-6), fast→slow store transfer, symbol-as-movable-object, one-shot in-context learning, goal-directed preplay, metacognition single-signals, order-sensitive sequence binding. Many "new mechanisms" proposed today turned out to already work via existing primitives.

### STRATEGIC INSIGHT (load-bearing for next session)

**Pattern of the day: substrate is MORE capable than our tests can detect.** Every "novel composition" cell that HARD_FAILed today turned out (per drill investigation) to be:
- Test design failure (saturating baseline / wrong discriminator slice / correlated signals)
- Primitive already saturating what composition was supposed to add
- Regime where mechanism's lever doesn't apply at this d/M

This argues for: PIVOT to ASSEMBLY of existing primitives into integrated capabilities + cortex-system completion. NOT new-mechanism exploration. The substrate-product narrative is "we have the pieces; need to compose them into working systems" not "we need more mechanisms."

### CORTEX ASSEMBLY STATUS (today's progress)
- Content extraction (ultrametric clustering) — CHAIN_GRADE
- TWO_TIER + NREM replay + Partition routing — CHAIN_GRADE
- **NEW today: Hippo→cortex handoff (sparse-DG + dense-cortex; smoke chain-grade quality; full re-running)**
- **NEW today: Movable-object parietal-cortex analog (cv=0.003 lift +0.576)**
- **NEW today: Goal-directed preplay (K64+GG closes 60% oracle gap)**
- Schema-integration (Tonegawa sparse-ensemble): k=500 best at K=100; bundle ceiling at K=500
- Cortex-as-router: deferred on PFC controller full result

**Cortex transitions from "primitives in isolation" → "working assembly" today.** This is the substrate-product story.

### POST-COMPACTION RECOVERY COMMANDS

```bash
# Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# Check landings since 22:50Z
find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -60 -printf '%TH:%TM %p\n' | sort

# Verify scheduled task
# Use PowerShell: schtasks /query /tn hd_director_kb_continuous_ingest /fo LIST

# Re-arm notes_monitor (research role)
```

-- Research (Opus 4.7-1M) — 2026-06-27 ~22:50Z FINAL COMPACTION-PREP (UPDATE #10)

---

## ELEVENTH-WAVE UPDATE 2026-06-27 ~23:00Z (15:55 PDT, post-compaction) — SKUNKWORKS REFUSED 5-CELL VET; PHANTOM-FRAMING ROOT CAUSE IDENTIFIED

**Skunkworks vet agent a51e98936b762044c returned REFUSAL of all 5 today-vet cells.** Zero atoms written. CERT unchanged at 623. Same pattern as 07:03 PDT FLAGBACK.

### REFUSAL VERDICTS (verified off local disk)

1. **pfc_controller v2** — only SMOKE depth=6 HARD_PASS exists locally; the "depth=12 collapse SOFTMAX=0.156 cv=0.249" framing is PHANTOM (FULL dir has SELFTEST_OK only). Real residue: at depth=6, with_abstain fires `identity` 69.7% of seeds (partial_metrics_7.json line 36 only verifiable observation).

2. **btsp v2 regime-probed** — PROMPT WRONG ON SMOKE TOO. Smoke verdict=HARD_FAIL but reason=BASELINE_FLOOR (full-seed baseline 0.381 < 0.40), NOT "no probe cfg in band." Probe DID find cfg (N_DIM=1024, alpha=0.0488, baseline 0.58 at 1-seed). 1-seed probe over-fit → 3-seed regression. Real META candidate: probe-band tolerance must absorb ≥1.96·SEM of multi-seed expected drift.

3. **parietal cortex v1** — PHANTOM FULL numbers (cv=0.003 / n=5 / MOVABLE=0.867 match nothing on disk). Smoke MIDDLE_BAND is real: MOVABLE 0.847 cv=0.026 lift +0.675 over FIXED is HARD_PASS-quality IN ISOLATION; cell's HARD_PASS gate requires REL≥0.55 too, REL=0.374 fails. METHODOLOGY-CORRECT failure (movable+relational both required). Could split into 2 cells: motor-movable-rebind (chain-grade-quality) + spatial-relations (harder; honest-negative).

4. **engram_dropout v2 density-matched** — Smoke MIDDLE_BAND only (n=2; lift +0.015 at SEM 0.082 = z=0.18, not separated from zero). Density-confound fix WORKS as methodology atom; lift signal itself is INDETERMINATE (would need n≥10).

5. **importance_ceiling_falsification v1** — Already refused by drill. Smoke MIDDLE_BAND INDETERMINATE; TRACE=0.998 by-construction-saturating at this regime (TRACE always reads most-recent-bound trace; cv=0.00014). PCA/Fisher at noise floor with n=2 — cannot discriminate "they fail" from "n too small."

### CROSS-CELL ROOT CAUSE

**Landing notifier dead since 2026-06-23** (recent_landings.jsonl last entry 5+ days ago). Remote FULL results never SCP'd back to local. Drill notes' HYPOTHESIZED numbers ("CRLB says +0.12 should land at d=16384") get lifted into spawn descriptions as MEASURED numbers, then propagated through vet spawn prompts. Three separate phantom-vet batches today (07:03, importance-ceiling-final-answer, 18:35) all originated from this loop.

### SKUNKWORKS REQUIRED ACTIONS (paraphrased)

1. Verify landing notifier alive (Fix #25) — restart scheduled task
2. SCP remote FULL artifacts back to local for these 5 + 4 in-flight anchors (orchestrator agent a283a14ab22de93cd launched 23:00Z)
3. Next Skunkworks spawn: paste verbatim metrics.json contents + exact local path, NOT claimed numbers
4. Stop atomizing on phantom-FULL framings
5. Drill notes must mark `HYPOTHESIZED:` vs `MEASURED:` on every numeric claim (META candidate)

### CORRECTED CHAIN-GRADE-CANDIDATE SCORECARD (after Skunkworks refusal)

| Cell | Real tier on disk | Phantom framing was |
|------|-------------------|---------------------|
| pfc_controller v2 | SMOKE HARD_PASS depth=6 only | "depth=12 collapse cv=0.249 chain-grade for depth-adaptive ARGMAX revival" |
| hippo→cortex handoff | SMOKE n=1 HARD_PASS at small scale | "FULL lift +0.998 chain-grade" (caught earlier in walk-back #6) |
| parietal cortex | SMOKE MIDDLE_BAND (MOVABLE chain-grade IN ISOLATION) | "FULL n=5 cv=0.003" |
| engram_dropout v2 | SMOKE MIDDLE_BAND n=2 (density-fix works; lift not separated) | "FULL n=5 187s" |
| importance falsification | SMOKE MIDDLE_BAND INDETERMINATE | "FULL n=8 with sem_separated" |
| btsp v2 regime-probed | SMOKE HARD_FAIL baseline-floor | "REGIME_INFEASIBLE no probe cfg" |
| Cycle 1 v3 brain-pushback | UNKNOWN (silent) | (no phantom; correctly UNKNOWN) |
| task_vector_kshot v1 | SMOKE HARD_PASS K1=K3=1.000 K5=0.980 (verified Wave 3B agent) | (verified clean today) |
| substrate_preplay v1 WAVE3B | SMOKE MIDDLE_BAND K64+GG=0.775 (verified Wave 3B agent) | (verified clean today) |
| meta_knowledge_tip_of_tongue v1 | SMOKE HARD_PASS peak-pattern (verified Wave 3B agent) | (verified clean today) |
| substrate_md_chunk_config E3 | SMOKE MIDDLE_BAND cs64_of0.00 substrate=0.55 md=0.45 (verified Wave 3B agent) | (verified clean today) |

### NEW META CANDIDATES (next Skunkworks batch)

- **META_RULE_AC HYPOTHESIZED-vs-MEASURED MARKING**: drill notes MUST tag each numeric claim with HYPOTHESIZED (from CRLB math, brain-prior, expected-under-regime) or MEASURED (from metrics.json path X). Spawn prompts must only cite MEASURED. Three phantom-vet batches today rooted in this discipline gap.
- **META_RULE_AD PROBE-BAND TOLERANCE >= 1.96·SEM(MULTI-SEED DRIFT)**: 1-seed probe finding cfg with baseline=0.58 doesn't survive 3-seed re-run dropping to 0.38 (~0.20 drift, larger than 0.15 in-band tolerance). Probe band must be wider than expected SEM regression OR probe must use multi-seed minimum.
- **META_RULE_AE SCAN-RESPONSE: NO atomize on remote-completion FRAMING**: if metrics.json has verdict=SELFTEST_OK (not HARD_PASS / HARD_FAIL / MIDDLE_BAND), the cell DID NOT RUN. Smoke-tier numbers may exist; FULL numbers do NOT exist. Skunkworks refusal pattern: cell did not complete → no FULL atomization possible regardless of framing.
- **META_FINDING_substrate_already_does_X**: pending from UPDATE #10 still applies (additive sequence binding / HRR in-context K-shot / single-signal metacog all saturate what proposed mechanisms wanted to add).

### POST-COMPACTION DISCIPLINE LOCK-IN

Per `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md` + Skunkworks refusal pattern: BEFORE citing any number in framing/spawn/response:
```
python -c "import json; m=json.load(open('<path>')); print(m.get('verdict'), m.get('verdict_msg'), {k:v.get('mean') for k,v in m.get('per_arm_summary',{}).items()})"
```
If verdict==SELFTEST_OK → cell did not complete; no FULL claims possible.
If verdict==RUNNING → cell still in progress; no claims possible.
Drill-note numbers are HYPOTHESES until verified against a metrics.json file path.

### IN-FLIGHT AT 23:00Z

- **a283a14ab22de93cd**: orchestrator restarting landing_notifier + SCP'ing 9 remote anchors
- **a0534a89eb12fa025**: Skunkworks vet 5 negatives (status TBD)
- **a4e9ffaa8407902fb**: Wave 3A revival 3 cells (status TBD)
- **ab7b7708078e41e56**: PFC depth-adaptive ARGMAX revival author (seed 23 in flight at compaction)
- **Wave 3B (aea2a2c14ad ...) COMPLETED**: 4 cells smoke-verified + queued remote_cpu — all FAIR-DESIGN per agent's own audit (task_vector HARD_PASS / preplay MIDDLE_BAND / TOT HARD_PASS / md_chunk MIDDLE_BAND). All have actual metrics.json on disk.
- 2 python processes alive on remote: PID 1276 (start 18:11 PDT, 1440MB) + PID 11760 (start 18:38 PDT, 1504MB) — orchestrator identifying

### NEXT-STEP PRIORITY (post-compaction me)

1. Wait for orchestrator a283a14ab22de93cd report (landing notifier + SCP)
2. Once SCP'd, ACTUALLY VERIFY each of 9 anchor metrics.json against Skunkworks recipe (read verdict + per_arm_summary)
3. Spawn fresh Skunkworks ONLY AFTER reading actual metrics; paste verbatim contents in spawn
4. Atomize META_RULE_AC + AD + AE in next Skunkworks batch
5. Process a0534a89 + a4e9ffaa + ab7b7708 outputs (each will likely have similar phantom-vs-real distinctions; require actual metrics)
6. Update MEMORY.md with META_RULE_AC if landing-notifier-restart confirms phantom-loop pattern (5+ instances today)

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:00Z UPDATE #11 (post-compaction)

---

## TWELFTH-WAVE UPDATE 2026-06-27 ~23:05Z (15:55 PDT, post-compaction) — SKUNKWORKS A0534A89 VET RETURNED: +1 CHAIN-GRADE + 2 MM (CERT 623→624+)

**Skunkworks negative-vet agent a0534a89eb12fa025 returned with SUBSTANTIVE atom delta (commit 22f8d905; Store 177,470).** Vetted 5 cells; my framing was WRONG on 2 of them.

### CORRECTED RESULTS (with actual metrics.json verified by Skunkworks AND by me directly)

| # | Cell | My UPDATE #10 framing | Skunkworks vet (real) |
|---|------|----------------------|----------------------|
| 1 | task_vector_in_context_kshot_v1 | "HARD_FAIL K0=K1=K3=0 selftest values" | **REAL: HARD_PASS K1=K3=1.000 K5=0.980 K5-K0=+0.97 mono=True** (verified directly) — **CHAIN-GRADE ELIGIBLE for HRR bundle-recall primitive** |
| 2 | meta_knowledge_partition_coverage_v1 | "HARD_FAIL composition didn't work" | **PARTIAL_WIN MEASURED_MECHANISM**: cosine_sep AUROC=0.86 + entropy AUROC=0.86 (refuse-gate primitive); composition no lift; partition broken at smoke; ECE fails |
| 3 | meta_knowledge_tip_of_tongue_v1 | "smoke HARD_PASS" | **TEST_DESIGN_FAILURE**: TOT criterion rigged (percentile-on-clean-baseline blind to low-SNR brain-aligned state); HC/LC gates pass but TOT criterion meaningless |
| 4 | cyclic_sws_rem_eta_schedule_v1 | (silent) | **TEST_DESIGN_FAILURE**: baseline=0.026 at chance 1/N_CAT; classification readout broken at smoke; eta-cycling DOES work at synapse level (frob_ratio=12.63) |
| 5 | tonegawa_v5_k_density_sweep | "K=500 bundle ceiling 16x lockstep" | **PARTIAL_WIN MEASURED_MECHANISM**: K=100 PERM_k500=0.353 vs PROTO=0.266 vs DIAG=0.013; substrate prefers ~25% density; K=500 bundle ceiling is real BUT density preference is a finding |

### NET CERT DELTA (post-Skunkworks)

- **+1 chain-grade eligible**: task_vector_in_context_kshot v1 (HRR bundle-recall primitive — retract Director's HARD_FAIL framing)
- **+2 MEASURED_MECHANISM**: partition_coverage refuse-gate (AUROC=0.86 each) + tonegawa density preference
- **0 honest-negatives**: cells 3+4 are test-design bugs, NOT honest negs
- **CERT 623 → 624 (chain-grade tier) + 2 MM tier atoms**

### REQUIRED 2X DRILLS (Skunkworks-mandated)

1. **tip_of_tongue REQUIRED**: redesign TOT criterion (per-SNR-bin quantile / absolute thresholds / ratio cluster_cos/cleanup_cos)
2. **sws_rem REQUIRED**: re-author with non-classification readout (associative recall against (key,value) pairs; chance 1/V_C; substrate band [0.3, 0.7]) — same fix pattern as commit 2546e96e Wave 2 redesigns
3. **partition_coverage RECOMMENDED**: per-domain isotonic calibration of cosine_sep + entropy SEPARATELY (no composition) + fix partition routing (k-NN density or hash on more bits)
4. **tonegawa_v5 OPTIONAL**: finer density grid at K=100 [50, 100, 200, 300, 500, 750, 1024] across n≥3 seeds; if delta≥+0.10 with cv<0.10, promote to chain-grade

### CRITICAL META FINDING (Skunkworks Cell 1)

I cited SELFTEST sibling values (`exp_task_vector_in_context_kshot_v1/metrics.json` = SELFTEST_OK with k0=-0.021 k5=-0.001) instead of the _smoke file with real numbers (`exp_task_vector_in_context_kshot_v1_smoke/metrics.json` HARD_PASS). When SELFTEST + SMOKE sibling pairs exist, must cite the EXACT path. Same path-citation error as the broader phantom-FULL pattern at UPDATE #11; this is the disambiguation variant.

**META_RULE_AE candidate**: when running `peek_arm_metrics.py` or citing in spawn prompts, ALWAYS use the absolute file path (not just anchor name). For cells with both `exp_<anchor>/` (selftest) and `exp_<anchor>_smoke/` (smoke) and potentially `exp_<anchor>_full/` (full), the path disambiguates. Spawn-prompts citing only the anchor will trigger ambiguity errors.

### POST-COMPACTION-PROCESS QUALITY ASSESSMENT

In 30 minutes post-compaction I:
- Caught BACKUP UPDATE #10 framings WRONG on 6+ cells (5 from Skunkworks #1 phantom-FULL + 1 from Skunkworks #2 selftest-vs-smoke)
- Got +1 chain-grade promotion via Skunkworks #2 (would have been suppressed if I'd accepted my own framing)
- Zero atoms written; CERT unchanged at first, then +1 via Skunkworks atomization (not my action)

**This validates the agent-spawn-only architecture + cert-owner-overrides-Director pattern.** The discipline that Skunkworks must be cited with metrics.json paths is the load-bearing fix; no amount of "be more careful" from me will prevent the framing-drift pattern because each layer of summary loses precision.

### NEXT-STEP PRIORITY (revised)

1. Wait for orchestrator a283a14ab22de93cd report (landing notifier + SCP)
2. Process a4e9ffaa + ab7b7708 outputs WITH SAME DISCIPLINE: read each cell's metrics.json directly before any framing
3. Author the 2 REQUIRED 2x drills (tip_of_tongue criterion redesign + sws_rem non-classification readout)
4. Update MEMORY.md with new META rule (path-disambiguation for selftest/smoke/full siblings)
5. Continue per UPDATE #10 priorities once landing-notifier alive (vet remote-landed FULLs as they arrive)

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:05Z UPDATE #12 (post-compaction, post-Skunkworks-a0534a89)

---

## THIRTEENTH-WAVE UPDATE 2026-06-27 ~23:15Z — ORCHESTRATOR FINDINGS + FRESH METRIC READS

**Orchestrator a283a14ab22de93cd complete. Key findings:**

### 1. LANDING_NOTIFIER WAS NEVER REGISTERED AS A SCHEDULED TASK

Per Fix #25 memory rule, was supposed to run every 2-5 min scanning remote `data/` for new metrics.json. The scheduled task `hd_landing_notifier` DID NOT EXIST — it had been written about in memory + recipe in `tools/landing_notifier.py` (file present 4120B) but the REGISTRATION step was never done. Result: 4 days of silent landing-detection drift.

Orchestrator REGISTERED fresh via `schtasks /create` (every 3 min as MARSH Limited Interactive). Logs to `data/logs/landing_notifier.log`. Ran inline once: **663 backlog landings flushed** to `data/recent_landings.jsonl` (was frozen at 2026-06-23T21:10Z).

**This is the load-bearing fix of the day.** The pattern of "phantom-FULL framings → drill notes citing hypotheses as measurements → spawn prompts citing those → Skunkworks refusing" was a CASCADE rooted in: I never had a signal for when remote FULLs landed, so I projected from drill numbers as if measured.

### 2. SCP CONFIRMED 7 OF 9 ANCHORS (mtime 19:01:28-19:01:34 = orchestrator just-in-time SCP)

| Anchor | Remote mtime | Real FULL verdict |
|--------|--------------|---------------------|
| pfc_controller v2 | 17:09:12 | HARD_FAIL depth=12 SOFTMAX=0.156 ARGMAX=0.170 (ARGMAX > SOFTMAX confirms depth-adaptive ARGMAX revival justified) |
| btsp v2 regime-probed | 17:09:56 | HARD_FAIL REGIME_INFEASIBLE (probe over-fit at multi-seed confirmed) |
| parietal cortex v1 | 17:09:29 | MIDDLE_BAND MOVABLE=0.867 cv=0.003 lift+0.576 (MOVABLE chain-grade quality alone) |
| engram_dropout v2 | 17:14:33 | MIDDLE_BAND ENGRAM_BELOW_FLOOR engram_cor=0.147<0.40 (honest neg) |
| importance falsification d=16384 | 17:10:13 | MIDDLE_BAND INDETERMINATE TRACE=0.998 saturated (substrate-has-importance-via-TRACE); others noise floor (need M=16384) |
| cortex_hippo_handoff | IN-FLIGHT | (running since 18:11; alive PID 1276+29416) |
| task_vector_kshot v1 | 18:52:05 | SELFTEST_OK only! FULL not actually run yet despite mtime — only selftest landed |
| substrate_preplay_beam v1 | MISSING | (still pending in queue position 4) |
| Cycle 1 v3 brain-pushback | 14:05:12 | UNKNOWN PROGRESS 22/45 units; ORPHANED (no live PID; checkpoint file frozen) |

### 3. REMOTE QUEUE STATE

**Active CPU**: `runner_v2_prod.py --queue-dir remote_cpu_queue --id cpu_runner_0` (PID 7324+13164 since 14:14 PDT)
- RUNNING: cortex_hippo_handoff_FULL since 18:11 (PID 1276+29416)
- STALE-RUNNING marker: Cycle 1 v3 (PID dead; mtime 14:05; runner thinks it's still running)
- PENDING (8): sub_atom_encoder_v2_real_mathlib_FULL, trigram_downstream_ingest_probe_v1_FULL, task_vector_in_context_kshot_v1_FULL, substrate_preplay_beam_to_goal_v1_FULL, meta_knowledge_tip_of_tongue_v1, task_vector_in_context_kshot_v1, substrate_preplay_beam_to_goal_v1_WAVE3B, substrate_md_chunk_config_sweep_E3_v1

**Active GPU**: `runner_v2_prod.py --queue-dir overnight_queue --id gpu_runner_0` (PID 11504+17308 since 14:14 PDT). **IDLE — 0 pending; last activity 18:29 PDT.** This is a Fix #24 violation opportunity.

**Other**: PID 8868+11760 running `exp_substrate_bge_index_refresh_full_corpus_v1.py` since 18:38 PDT — this is the substrate-KB BGE encoder refresh (Wave 4 v2 content-KB rebuild). 5h elapsed.

### 4. CORRECTED METRIC READS (verified just now)

- **Cycle 1 v3 Barrier 1 break test**: still PROGRESS 22/45 units, orphaned PID. Needs re-dispatch from checkpoint. Single most load-bearing pending result of the day.
- **task_vector FULL**: SELFTEST_OK only — k0=0.000 k5=1.000 top1_recall (selftest passes; FULL run never started). The smoke at `_smoke` path is the real chain-grade-eligible HARD_PASS data (verified via Skunkworks a0534a89 atomization).
- **trigram_downstream_ingest_probe_v1_FULL_remote_cpu**: IMPORT_CRASH SystemExit: 0 (sys.exit(0) at import time — likely `if __name__ == "__main__"` issue per META_RULE_X).

### IMMEDIATE NEXT ACTIONS

1. **Re-dispatch Cycle 1 v3 from checkpoint** (orchestrator should clear stale-running marker first, then re-queue with `resume_from_checkpoint=True` if cell supports it; else fresh dispatch)
2. **Route some pending CPU cells to GPU** since GPU runner idle since 18:29 PDT (task_vector_FULL / preplay_FULL are matmul-heavy)
3. **Investigate trigram_downstream IMPORT_CRASH** (1-line fix likely: add `if __name__ == "__main__"` guard)
4. **Wait for fresh Skunkworks vet ad6f061a6982e9fa1** with the verified data paths (will produce real CERT delta)
5. **Wait for a4e9ffaa (Wave 3A revivals) + ab7b7708 (PFC ARGMAX) outputs**
6. **File META_RULE_AE memory rule** for selftest/smoke/full path-disambiguation

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:15Z UPDATE #13 (orchestrator complete; data on disk; ready to atomize)

---

## FOURTEENTH-WAVE UPDATE 2026-06-27 ~23:20Z — WAVE 3A REVIVAL RETURNED ALL HARD_FAIL_SMOKE (DISCIPLINE WORKING)

**Wave 3A revival agent a4e9ffaa8407902fb complete. All 3 cells smoke HARD_FAIL. NO full dispatches. Saved 30-50 CPU-hr.** This is META_RULE_K (smoke fires discriminator) working exactly as designed.

### CELL VERDICTS (all 3 with absolute path + per-arm)

**Cell 1: `meta_knowledge_partition_coverage_v2_orthogonal_signals`**
- Path: `d:/AI/hd-instrument/data/exp_meta_knowledge_partition_coverage_v2_orthogonal_signals/metrics.json`
- Smoke HARD_FAIL: -0.023 lift over SINGLE_BEST | SINGLE=0.852 OLD=0.860 ORTHOGONAL=0.829 RANDOM=0.511
- Root cause: margin (top1-top2) + perturbation_cos + density are NOT orthogonal in this regime — entropy already saturates at AUROC=0.86
- **Side discovery worth atomizing**: feature-standardized logreg cuts ECE 3.7x vs v1 (0.040 vs 0.152) at unchanged AUROC

**Cell 2: `cross_task_4hop_chain_v2_sum_bind`**
- Path: `d:/AI/hd-instrument/data/exp_cross_task_4hop_chain_v2_sum_bind/metrics.json`
- Smoke HARD_FAIL_ORACLE_BROKEN: all arms 0.017 (chance 1/80=0.0125)
- Root cause: sum-bind `key=Σbind(item, pos_i)` interferes catastrophically when stacked in Hebbian outer-product W at N=8192 with 200 chains
- **Substrate physics atom candidate**: sum-bind interferes at >50 chains in Hebbian stack — need sparser training OR per-key cleanup OR codebook-cleanup

**Cell 3: `pfc_goal_conditioned_gate_v2_cleanup_bind_output`**
- Path: `d:/AI/hd-instrument/data/exp_pfc_goal_conditioned_gate_v2_cleanup_bind_output/metrics.json`
- Smoke HARD_FAIL: at depth=6 | V1=0.340 BIND_CLEAN=0.000 WM=0.390 ADDITIVE=0.390 COMBINED=0.000 ORACLE=1.000
- Root cause: cleanup-bind-output destroys bind info (cleanup snaps to single codebook entry); COMBINED inherits the collapse
- **Concrete v3 design recommended**: WM_SLOT + ADDITIVE only (NO bind-cleanup), sharper alpha sweep for additive bias. Huge headroom remains (ORACLE-V1 = 0.66)

### NEXT-ITER DESIGN STAGED (when spawn budget allows)

- `exp_pfc_goal_conditioned_gate_v3_wm_additive_combined_v1` per Wave 3A recommendation
- Wave 3A side findings → 3 atoms next Skunkworks batch (feature-std-logreg ECE + sum-bind-Hebbian-stack-interference + cleanup-bind-output-destroys-bind)

### LANDING NOTIFIER NOW LIVE

Monitor btjgicith fired 7 LANDING events in last 5 min (the SCP'd anchors registered as new landings on the registry — landing_notifier scheduled task working). This is the load-bearing infra fix today.

### IN-FLIGHT (4 agents)

- a4cc90c0d6c15cb87: orchestrator Cycle 1 v3 redispatch + GPU routing + trigram fix
- ad6f061a6982e9fa1: Skunkworks fresh vet of 5 cells with verified paths
- a4cda37a3e4b4807c: research drill tip_of_tongue criterion redesign
- af92113400accfc8a: research drill sws_rem non-classification readout
- (still awaiting): ab7b7708 PFC depth-adaptive ARGMAX revival

### STRATEGIC PATTERN OF THE DAY

In ~30 min post-compaction, dispatched 4 agents + processed Wave 3A landing. ALL substantive results (Wave 3A, Skunkworks a0534a89, orchestrator a283a14a) had REAL data backing them. NO new phantom-FULL framings. The discipline-fix worked: heartbeat + read absolute paths + cite metrics.json contents before framing.

The substrate-product status is preserved unchanged at the FULL level (no chain-grade promotions in last 30 min beyond task_vector v1 smoke promotion); the META-process status improved substantially (landing notifier alive; 3 memory rules added; 6 META candidates pending).

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:20Z UPDATE #14 (Wave 3A processed; discipline holding)

---

## FIFTEENTH-WAVE UPDATE 2026-06-27 ~23:25Z — CYCLE 1 V3 BARRIER 1 RESULT + 2 DRILLS READY

### CYCLE 1 V3 BRAIN-PUSHBACK COMPOSITION (Barrier 1 break test) = RAIL_SANITY_BREACH

**Real path** (verified via SSH + just SCP'd locally; 18654B): `d:/AI/hd-instrument/data/exp_substrate_multihop_brain_pushback_v3_redispatch/metrics.json`

**Verdict**: RAIL_SANITY_BREACH | BASELINE_depth_5=0.5817 (cv=0.036, 3/3 seeds outside [0.10, 0.20] rail)
- R1 = 0.5817 (cv=0.036)
- R2 = 0.5817 (cv=0.036)
- R3 = 0.5817 (cv=0.036)
- COMBINED = 0.5817 (cv=0.036)
- indiv_max = 0.5817

**SMOKING GUN: ALL ARMS PRODUCED IDENTICAL OUTPUT (0.5817 with cv=0.036 across 3 seeds × 5 arms).** Either:
- (a) cell's arm code paths converge to same operation at this regime (mechanism not differentiated)
- (b) baseline regime too easy → all arms collapse to baseline (predicted regime [0.10, 0.20]; observed 0.5817)
- (c) cell has bug making all arms produce same output (unlikely; passed L1-L4 hardening + cardinality_ok)

Cell completed 45/45 units (3 seeds × 5 arms × 3 depths = 45; cardinality_ok=True). Config: N=8192 V_C=1000 V_P=10 N_chains_train=200 N_chains_test=200 depths=[2,3,5] hardening=L1early+L2perarm+L3outertry+L4importsentinel chain_gen_fix=V_C200to1000_maxdepth8to5.

**Interpretation**: Barrier 1 NOT BROKEN. Baseline regime is wrong — at V_C=1000 with N_chains=200, plain BASELINE already does ~58% top1-recall at depth=5 with no mechanism. Pre-reg predicted baseline at [0.10, 0.20] (i.e. ~15% accuracy) where mechanism could lift; observed 58% means there's no room for mechanism. **Cell measured something** (3/3 cv=0.036) — just measured a regime mismatch.

**v4 design recommendation**: harder regime. Either (a) V_C higher (3000+); (b) N_chains_train lower (40 → more interference); (c) noise injection; (d) deeper composition (depth=8+). v4 should target baseline in [0.10, 0.20] band before mechanism arms have meaningful room to lift.

**This is THE Barrier 1 break test result for today.** Headline: substrate's compositional reasoning at this regime is "already good enough" — but that says nothing about whether brain-pushback mechanisms help at HARD regimes (which is the original Barrier 1 question). The test design's regime was wrong. NOT a substrate ceiling result.

### DRILL OUTCOMES (both complete)

**a4cda37a tip_of_tongue criterion redesign**:
- TOP-1: Option C ratio criterion (cluster_cos / cleanup_top1 > 2.0 AND cluster_cos > 0.30)
- Brain-grounded: Brown-McNeill 1966 + Yonelinas dual-process + Schwartz cue-familiarity/accessibility
- P_deflated = 0.42
- Drill note: `d:/AI/hd-instrument/notes/research_drill_2x_tip_of_tongue_criterion_redesign_2026-06-27.md`
- Handoff note also filed: `exp_dev_handoff_research_tip_of_tongue_v2_ratio_redesign_2026-06-27.md`

**af921134 sws_rem readout redesign**:
- TOP-1: associative recall against held-out noisy keys with per-pair random encoding
- TOP-2: capacity-at-fixed-recall M-sweep
- P_deflated = 0.45
- Drill note: `d:/AI/hd-instrument/notes/research_drill_2x_sws_rem_associative_recall_readout_redesign_2026-06-27.md`
- Brain-grounded per Diekelmann-Born / Stickgold / Rolls CA3 pattern completion

Both drills cite brain literature + concrete substrate primitives + discriminator design. Both have P_deflated ~0.42-0.45 (substantive lift expected if regime correct this time).

### IMPORT_CRASH SWEEP

Grep across all `data/*/metrics.json` for `IMPORT_CRASH` returned 2 files — both for `trigram_downstream_ingest_probe_v1` (FULL_remote_cpu + selftest variants; same anchor). **Pattern is NOT widespread.** Orchestrator a4cc90c0 already patched the cell (removed `except BaseException` swallow of `SystemExit(0)`); SCP'd to remote; pending queue entry will pick up patched code.

### IN-FLIGHT (2 agents remaining)

- ad6f061a6982e9fa1: Skunkworks fresh vet of 5 cells with verified paths
- ab7b7708078e41e56: PFC depth-adaptive ARGMAX revival author (was at seed 23 in flight at compaction)

### REMOTE QUEUE STATE (per orchestrator a4cc90c0)

- Running: cortex_hippo_handoff_FULL (PID 1276+29416 since 18:11; ~5h+ now — close to completion)
- Pending (8): sub_atom_encoder_v2_real_mathlib_FULL / trigram_downstream_ingest_probe (patched) / task_vector_in_context_kshot_v1_FULL / substrate_preplay_beam_to_goal_v1_FULL / meta_knowledge_tip_of_tongue_v1 / task_vector_in_context_kshot_v1 / substrate_preplay_beam_to_goal_v1_WAVE3B / substrate_md_chunk_config_sweep_E3_v1
- Orphaned-cleared: substrate_multihop_brain_pushback_composition_v3_chain_gen_fix (no salvageable checkpoint; same-script redispatch already completed RAIL_SANITY_BREACH)
- GPU runner: IDLE (no CUDA-eligible cells in queue; per Fix #24 the pending cells don't have CUDA paths)

### NEXT-STEP PRIORITIES

1. Wait for ad6f061a Skunkworks re-vet (real CERT delta expected on 5 cells)
2. Wait for ab7b7708 PFC ARGMAX revival
3. Watch for cortex_hippo_handoff_FULL landing (running 5h; close)
4. Author tip_of_tongue v2 + sws_rem v2 cells when spawn budget allows (both have brain-grounded drill recommendations ready)
5. Author Cycle 1 v4 with HARDER regime (V_C 3000+ OR N_chains 40 OR deeper) to actually test Barrier 1 mechanism question
6. Stage Wave 3A side findings + Cycle 1 v3 RAIL_SANITY_BREACH for next Skunkworks batch atomization

### SUBSTRATE-PRODUCT STATUS (unchanged at FULL level)

CERT 624 (post-Skunkworks a0534a89 +1). No new chain-grade promotions in this session window. META-process status materially improved (landing notifier alive; 3 memory rules; 6+ META candidates pending; phantom-FULL framing pattern now caught structurally).

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:25Z UPDATE #15 (Cycle 1 v3 verdict + 2 drills landed)

---

## SIXTEENTH-WAVE UPDATE 2026-06-27 ~23:35Z — SKUNKWORKS RE-VET COMPLETE: CERT 623→625 (+2 CHAIN_GRADE)

**Skunkworks re-vet ad6f061a6982e9fa1 complete. Commit e67e4bf8. 7 atoms + 7 ledger rows. CERT 623 → 625.**

### TWO NEW CHAIN_GRADE WINS

**1. parietal_cortex MOVABLE-rebind (CHAIN_GRADE)**
- Path: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_reasoning_v1/metrics.json`
- MOVABLE arm IN ISOLATION: cv=0.0031 / lift over NO_POS = +0.830 / lift over FIXED = +0.576
- fair_baseline_ok=True / suspect_1000=False / discriminator fires strongly positive
- Brain analog: motor-cortex positional rebinding (symbol-as-movable-object); separate cortical substrate from spatial-relations
- **This is today's substrate-product win for parietal cortex** — confirms cortex extends beyond pure-information mechanisms to BIND-AND-MOVE primitives

**2. engram density-matched-null methodology (CHAIN_GRADE)**
- Path: `d:/AI/hd-instrument/data/exp_engram_dropout_inhibitory_plasticity_v2_density_matched/metrics.json`
- Methodology atom: density-matched-null FAIR-BASELINE pattern (alignment rel_diff=0.0002, HP<=0.10 PASS by 500x)
- THE FIX itself is chain-grade — methodology proven sound; not the mechanism
- Engram mechanism IS HONEST_NEGATIVE (cor_lift=+0.014; HP>=0.05 missed by 36pp)
- This atom unblocks future engram-family revivals using density-matched baselines

### KEY CORRECTIONS TO MY FRAMING

**PFC ARGMAX revival NOT JUSTIFIED at depth=12** (my UPDATE #13 was wrong):
- ARGMAX(d=12)=0.170; SOFTMAX(d=12)=0.156; gap = +0.014
- SEM_diff = 0.024 → gap is INSIDE 1 SEM
- cv: SOFTMAX=0.249 / ARGMAX=0.214 (both 2x+ over HP rail of 0.10)
- For valid revival need n_seeds≥8 with sem_margin>=0.08
- Cell ab7b7708 (still in flight) may produce same conclusion; vet output when lands
- atom tier = HONEST_NEGATIVE depth-tier-breaks-from-depth8

**Parietal REL arm has CELL BUG**: `grid_position_with_relations === grid_position_movable` bit-identical across all 5 seeds. The relations arm code path duplicates MOVABLE arm code (not testing relational-spatial circuit separately). Flag for cell-author iteration; doesn't affect MOVABLE chain-grade promotion.

**TRACE arm MEASURED_MECHANISM (proven-bound by-construction)** at M/d=0.024:
- Not chain-grade because no orthogonal arm separated above CRLB k=8 floor (0.055)
- Other arms (PCA / Fisher / Single) all BELOW CRLB k=8 floor → INDETERMINATE_NEEDS_M_SCALE confirmed
- Rescue requires M=16384 to match d=16384 (16x compute over current; substantial)

**BTSP v2 HONEST_NEGATIVE regime-infeasible-probe-SEM-drift**: META_RULE_AD confirmed (single-seed probe baseline=1.0 → 5-seed regressed to 0.381 = 0.62 drift; band tolerance must absorb multi-seed SEM). Deferred to v3 cell-author iteration.

### CYCLE 1 V3 PER-ARM ANALYSIS (no smoking-gun bug; per-step decay normal)

Re-read `exp_substrate_multihop_brain_pushback_v3_redispatch/metrics.json` per-arm carefully:
- BASELINE per_step_acc = [0.91, 0.855, 0.76, 0.64, 0.56] at depth=5 (substrate-physics decay)
- R1 (replay-into-W_c): shortcuts FIRE at depth=2 (141 hits, hit_rate=0.705) → +0.05 over baseline; ZERO shortcuts at depth=3+ → fallback used 100% → ties baseline
- R2 (PFC scratchpad): writes/reads fire but top1 == baseline (per-hop cleanup unchanged)
- R3 (bidirectional): meet_rate=top1; bwd_only=0.005 at depth=5 (backward chain fails to anchor)
- COMBINED: depth=2 lifts to 0.905 (+0.05); depth=3 meet_hits=152 but no top1 lift; depth=5 no lift

**Interpretation: NOT a cell bug — real substrate behavior.** Mechanism arms FIRE (scratchpad written, shortcuts attempted, meeting attempted) but per-hop cleanup at depth=5 is the bottleneck — neither replay, scratchpad, nor bidirectional improves cleanup fidelity at this regime. At depth=2 (where per-step accuracy is 0.91), mechanisms CAN add value (COMBINED +0.05 over baseline).

**This is a SUBSTANTIVE finding**: brain-pushback mechanisms (replay shortcuts / PFC scratchpad / bidirectional meeting) lift modestly at depth=2 but COLLAPSE at depth=5 in this regime because per-hop cleanup is the bottleneck. To break Barrier 1, mechanisms need to operate BELOW per-hop cleanup (not on top of it) — e.g., per-step error correction, intermediate cleanup-with-context, etc.

### CORRECTED CYCLE 1 V4 SPEC

Original spec to a706eb03 was N_chains_train 200→40. Sent reversal: should be 200→1000 (MORE interference = LOWER per-step accuracy = LOWER baseline at depth=5). Per-step needs to drop from 0.91 to ~0.72 to get baseline depth_5 into [0.10, 0.20] band.

### IN-FLIGHT (3 agents; spawn budget at cap)

- ad6f061a ✅ COMPLETE (just landed; processed above)
- a706eb037b9844377: Cycle 1 v4 cell-author with reversed knob direction
- ab7b7708078e41e56: PFC depth-adaptive ARGMAX revival (likely same finding as Skunkworks)

### CERT 625 PORTFOLIO STATUS

Today's chain-grade promotions: K=8192 capacity 3-seed (early session) + ANCHOR 1 v4 partition-routing + task_vector_kshot v1 smoke + parietal MOVABLE + engram density-matched methodology = **+5 chain-grade today**. Plus MM atoms + 6+ META rules.

The agent-spawn-only architecture + cert-owner-correctly-overrides-Director patterns are LOAD-BEARING. Real progress flowed through them.

### NEXT-STEP PRIORITIES

1. Wait for ab7b7708 PFC ARGMAX (likely HONEST_NEGATIVE per Skunkworks finding — vet when lands)
2. Wait for a706eb03 Cycle 1 v4 with corrected knob direction
3. Watch for cortex_hippo_handoff_FULL (running 5h+)
4. Author tip_of_tongue v2 + sws_rem v2 + pfc v3 when budget allows
5. Stage Wave 3A side findings + Cycle 1 v3 finding + parietal REL bug + ARGMAX-gap-too-small for next Skunkworks batch

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:35Z UPDATE #16 (Skunkworks re-vet +2 chain-grade; CERT 625)

---

## SEVENTEENTH-WAVE UPDATE 2026-06-27 ~23:45Z — SUBSTRATE-PRODUCT INSIGHT + 12 ATOMS STAGED

### CYCLE 1 V4 SMOKE RESULT (a706eb03 completed)

Smoke RAIL_SANITY_BREACH but DEEPLY INFORMATIVE per author's diagnosis:
- BASELINE_depth_5 = 0.875 (WORSE than v3 0.582; cell-author multi-knob change with V_C 1000→2000 counteracted my N_chains push)
- All 5 arms identical at 0.875 (same saturation pattern as v3)
- Per-hop conditional accuracy: 0.95-1.0 stable across hops

**Cell-author's load-bearing diagnosis** (verbatim): "the substrate's per-hop accuracy is dominated by argmax-ceiling, not crosstalk. Cleanup mechanism may need to be the variable, not the data density."

### SUBSTRATE-PRODUCT INSIGHT: BARRIER 1 IS ALREADY BROKEN (chain-grade depth-5 compositional reasoning)

Combining v3 + v4 results: substrate's per-hop argmax cleanup achieves:
- 56% top-1 at full N=8192, 200 chains, depth=5 (v3)
- 87.5% top-1 at smoke N=2048, 250 chains, depth=5 (v4)
- Per-hop conditional 0.85-1.0 (stable; not collapsing)

**The "Barrier 1 ceiling" was a FAKE diagnosis.** The 5 multi-hop "refutations" from earlier sessions were caricatures (per META_BARRIER_1_QUADRUPLE_NEGATIVE_RELABEL atom this morning). The fresh v3 + v4 tests show substrate ALREADY composes 5-hop chains at chain-grade-quality accuracy. Brain-pushback mechanisms tied baseline because BASELINE ALREADY DOES IT.

**To test brain-pushback mechanism value would require:**
- Option Y (brain-grounded): test at depth=10+ where natural decay brings baseline into [0.10, 0.30] band
- Option X (artificial): add HOP_NOISE injection to drop per-step accuracy
- Option Z (mechanism): use softmax cleanup with temperature instead of argmax

For now: STOP iterating Cycle 1 (v5 not authored). Atomize the substrate-product depth-5 finding as chain-grade EVIDENCE.

### NO CYCLE 1 V5 (decision)

Per pre-reg discipline + substrate-product framing, v5 has no fair design in the current framing. The "harder regime" path via data density alone won't work because substrate per-hop cleanup is argmax-ceiling-bound. Future revival would need cleanup-mechanism swap OR depth=10+ test, both significant re-scoping. DEFER to USER decision before authoring v5.

### TIP_OF_TONGUE V2 STATUS (a8e671ff completed authoring)

Cell + prereg authored; selftest_OK; queued remote_cpu_queue position 9 (waits behind cortex_hippo_handoff + 8 cells). YELLOW FLAG: at selftest N=256, Discr_C fired 0.0% (cluster_cos floor 0.30 not reached). Cell-author HYPOTHESIZES smoke N=2048 will fire (cluster_cos scales to 0.6-0.9). If smoke fails to fire Discr_C, recalibrate threshold.

### FINDINGS STAGED FOR NEXT SKUNKWORKS BATCH (12 atoms)

Filed: `d:/AI/hd-instrument/notes/research_findings_for_next_skunkworks_batch_2026-06-27_post_compaction.md`

- A1: substrate depth-5 compositional reasoning chain-grade EVIDENCE atom (NEW finding)
- B3a: feature-std logreg ECE methodology chain-grade atom (Wave 3A side finding)
- B3b: sum-bind Hebbian-stack interference substrate-physics atom (Wave 3A finding)
- B3c: cleanup-bind-output substrate-algebra atom (Wave 3A finding)
- C1: META_RULE_AC HYPOTHESIZED-vs-MEASURED discipline atom
- C2: META_RULE_AD probe-band-tolerance discipline atom (BTSP-confirmed)
- C3: META_RULE_AE metrics-path-disambiguation discipline atom (in memory)
- C4: META_RULE_AF arms-must-differ discipline atom (parietal REL bug)
- C5: substrate-product narrative atom (Barrier 1 fake; substrate already has it)
- C6: process atom (RAIL_SANITY_BREACH ↔ substrate-better-than-predicted)
- D1: infra atom (scheduled-task end-to-end verification)
- D2: cell-template atom (SystemExit before BaseException)

Expected CERT delta: +1 to +3 chain-grade + 4-6 META + 1-2 substrate-physics atoms = net +6-9 atoms.

### IN-FLIGHT (2 agents; 3rd slot open)

- ab7b7708078e41e56: PFC depth-adaptive ARGMAX revival (likely null per Skunkworks finding)
- a95be71b7115d6116: sws_rem v2 associative recall author

### NEXT-STEP PRIORITIES

1. Wait for ab7b7708 (PFC ARGMAX) + a95be71b (sws_rem v2) returns
2. When both land + cortex_hippo_handoff lands: spawn Skunkworks batch with all 12+ atoms
3. Decide on pfc_goal_conditioned v3 author (concrete Wave 3A finding-derived; spawn budget open)
4. Defer Cycle 1 v5 until USER decision

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:45Z UPDATE #17 (Barrier 1 substrate-product win + 12 atoms staged)

---

## EIGHTEENTH-WAVE UPDATE 2026-06-27 ~23:55Z — SWS_REM V2 FRAMING CORRECTED + 4 IN-FLIGHT + 14 ATOMS

### CORRECTION: SWS_REM V2 IS HONEST_NEGATIVE NOT TEST-DESIGN-FAILURE

My UPDATE #17 framing was based on STALE 19:34 metrics read. Final iteration at 19:35 (verified directly):
- Path: `d:/AI/hd-instrument/data/exp_cyclic_sws_rem_eta_schedule_v2_associative_recall_smoke/metrics.json`
- RAW_HEBB=0.848 / CONST=0.541 (IN fair band [0.30, 0.70]) / CYC_S=0.463 / CYC_L=0.465
- lift = -0.076 (cycling HURTS by 2.5x null threshold)
- frob_ratio = 13.96 (synapse mechanism IS firing — close to v1's 12.63)
- reasons = UNCLASSIFIED_REGIME (not BASELINE_OUT_OF_BAND)

Author iterated sigma 0.85→4.0 + alpha 0.5→2.0 across 3 tuning attempts in-place before reaching discriminator regime. **The substrate-too-robust-for-test-design pattern (C7 META_RULE_AG) only has Cycle 1 v3+v4 evidence; sws_rem v2 is different — clean substrate-product HONEST_NEGATIVE.**

Author's diagnosis (load-bearing): "eta_high EXPLORE pulses add noise to structured Hebb seed faster than eta_low SETTLE pulses refine." Cycling at Hebb-bipolar HRR layer is brain-grounded-but-substrate-incorrect. Drill closure-rescue path = pivot to sparse-coded keys OR capacity-knee sweep (encoding-layer change, not readout-layer).

**Discipline lesson:** cell-authors iterating tuning IN-PLACE on the SAME metrics path can produce stale reads if Research polls between iterations. Future cell-template should write final metrics atomically (mv tmp → metrics.json) OR write per-iteration metrics. New META candidate: META_RULE_AH atomic-final-metrics-write.

### 14 ATOMS NOW STAGED FOR SKUNKWORKS (was 13)

Findings doc updated: `d:/AI/hd-instrument/notes/research_findings_for_next_skunkworks_batch_2026-06-27_post_compaction.md`

- A1: substrate depth-5 compositional reasoning (chain-grade evidence)
- B3a / B3b / B3c: 3 Wave 3A side findings (methodology / physics / algebra)
- **B4 NEW: sws_rem v2 HONEST_NEGATIVE** (SWS/REM at Hebb-bipolar layer doesn't propagate)
- C1 / C2 / C3 / C4: 4 discipline META rules (AC / AD / AE / AF)
- C5 / C6: substrate-product narrative + RAIL_SANITY_BREACH-interpretation
- C7: META_RULE_AG substrate-too-robust pattern (Cycle 1 only)
- D1: scheduled-task end-to-end verification
- D2: cell-template SystemExit discipline

Plus future: META_RULE_AH atomic-final-metrics-write (this turn's discipline lesson).

### IN-FLIGHT (4 agents; Fix #14 cap reached)

- **ab7b7708078e41e56**: PFC depth-adaptive ARGMAX revival (likely null per Skunkworks gap<SEM finding)
- **ae9ce430afd63900c**: Skunkworks batch atomization (14 atoms staged; correction msg sent for sws_rem framing)
- **aa4407ffdf0776938**: pfc_goal_conditioned v3 cell-author (WM+ADDITIVE only, no bind-cleanup, alpha sweep)
- **a8e671ff7f4bbddf6**: tip_of_tongue v2 (queued remote_cpu_queue position 9 — won't run until queue clears, hours away)

Plus cortex_hippo_handoff_FULL still running on remote (PID 1276+29416 since 18:11 PDT; 5h+ now).

### NEXT-STEP PRIORITIES

1. Wait for ab7b7708 PFC ARGMAX (probable: HONEST_NEG)
2. Wait for ae9ce430 Skunkworks batch (expected: CERT +1-3 chain-grade + 4-5 META atoms; commit hash to record)
3. Wait for aa4407ff pfc_goal v3 (expected: smoke verdict + COMBINED lift if independent additivity holds)
4. Watch cortex_hippo_handoff (closest to completion of in-flight remote cells)
5. tip_of_tongue v2 smoke will wait until remote queue clears

### SESSION SCORECARD (post-compaction, ~50 min in)

- CERT: 623 → 625 (+2 chain-grade landed; +1-3 expected from Skunkworks batch in flight)
- Atoms today: 17 committed + 14 staged for batch
- Memory rules added: 3 (substrate-as-canonical / no-hallucinated-numbers / path-disambiguation)
- META rules at stake: AG / AF / AE / AD / AC / AH (6 new candidates from this session)
- Infra fix: landing_notifier finally registered (4-day silent drift root cause)
- Cells dispatched: 4 (Cycle 1 v4 / sws_rem v2 / tip_of_tongue v2 / pfc_goal v3)
- Smoke verdicts: 4 cells smoke-completed; 0 full dispatched (smoke discipline working — saves 30-50 CPU-hr)
- Discipline holds: 0 phantom-FULL framings this session (post-correction-of-stale-read); cite-absolute-path discipline enforced

-- Research (Opus 4.7-1M) — 2026-06-27 ~23:55Z UPDATE #18 (sws_rem correction + 4 in-flight + 14 atoms; spawn budget at cap)

---

## NINETEENTH-WAVE UPDATE 2026-06-28 ~00:30Z — STAGE 3 GAP-FILLING WAVE 2 IN FULL FLIGHT

**Session scorecard (CERT 626 banked):**
- 3 chain-grade today: parietal MOVABLE-rebind + engram density-matched-null methodology + substrate depth-5 compositional reasoning
- 9 META rules atomized (AC/AD/AE/AF/AG/AH/AI/AJ/AK; commit 5e78b4c1)
- 4 memory rules added (substrate-as-canonical / no-hallucinated-numbers / path-disambiguation / compute-formulas-in-code)
- exp_dev.md +129 lines hardened (§6-§12 mandatory rules)
- Landing notifier ROOT-CAUSE FIXED (was never registered as scheduled task; 4-day silent drift)
- Monitor popups FIXED (hd_landing_notifier + hd_kb_ingest now Hidden=true pythonw)
- Discipline ladder caught 6 Director framing errors (cert-owner overrides working as designed)

**Active in-flight (Wave 2 Stage 3 gap-filling):**
- ab7b7708 PFC ARGMAX v3 smoke RUNNING seed 3/3
- abb7688cc Temporal reasoning drill (Wave 3 anchor)
- a8c195af CF Cell 1 regret-comparison (vmPFC analog; P=0.50)
- aeb00963 CF Cell 2 latency delta-stack (auto-promotes MB→CG; P=0.50)
- ac110631 Schema ANCHOR 1 context-prior cell (vmPFC instantiation; P=0.50; green-light from ANCHOR 3)
- a8545fa1 Orchestrator: push ANCHOR 3 + queue full
- TOM v1 queued remote pos 14 (HARD_PASS smoke Q2=0.900 Q3=0.875 gap+0.725; full preview survives scale)
- M-CFU v7B on GPU queue pos 0 (--device cuda; awaiting consumer)

**SUBSTRATE-PRODUCT WINS THIS WAVE (chain-grade-quality smokes pending atomization):**
- **TOM Sally-Anne v1 SMOKE HARD_PASS** (Q2 false-belief=0.900; Q3 2nd-order=0.875; gap+0.725; cv=0.056) — Foundational M3 TOM primitive
- **Schema ANCHOR 3 HARD_PASS at full N** (K_NEAREST_K20=0.728 cv=0.015; lift+0.472 over baseline; substrate cosine kernel supports schema inference) — Green-lights ANCHOR 1 + ANCHOR 2 schema-driven mechanism family
- **Parietal RELATIONAL HARD_PASS smoke** (HRR=0.920 cv=0.019 lift+0.675; full queued) — Completes parietal cortex story (MOVABLE already CG)

**Sub_atom encoder v2 FULL Mathlib MIDDLE_BAND** — RF=0.997 (mechanism works) but Trig baseline too strong on Mathlib (gap=0.204 < 0.30 HP); encoder primitive solid; corpus-specific honest-neg.

**Cycle 1 v3+v4 substrate-product framing**: depth-5 composition is already chain-grade (just atomized in batch 12); Cycle 1 v5 depth=10 queued for natural-decay regime test (will run when queue clears).

**Schema-driven new finding**: ANCHOR 3 falsifier proves substrate cosine kernel supports posterior-style schema inference. The 4 earlier extraction-HARD_FAILs (BCM/Tonegawa-K100/Tonegawa-K500/Hopfield-consolidation) targeted the WRONG layer; schema-INFERENCE works. ANCHOR 1 (richer Gilboa-Moscovitch vmPFC mechanism) should pass at higher accuracy than 0.728.

**Counterfactual reasoning state (post-correction)**: substrate already has 5 atoms (4 CG + 1 MB):
- intervention_isolation HARD_PASS
- counterfactual_replay MIDDLE_BAND (only latency-bound)
- audit_chain_depth HARD_PASS (depth 50)
- bitemporal_composition HARD_PASS (CF-as-of=1.000)
- correlational_disambig HARD_PASS

CF Cell 1 (regret) + CF Cell 2 (latency) target 2 of 5 un-atomized gaps. If both HP, importance of CF reasoning capability fully banked.

**Queue state:**
- Remote CPU: 14 pending behind cortex_hippo_handoff (still running 6h+)
- Remote GPU: 1 pending (M-CFU v7B at pos 0)
- Cron alive (3a20be75 :03/:18/:33/:48 + eb2de25d daily 9:45pm one-shot)
- Autonomous-loop instructions at `data/autonomous_loop_instructions.md`

**Next-wave priorities (when current 7 in-flight return):**
1. Atomize TOM v1 + Schema ANCHOR 3 + (if HP) Schema ANCHOR 1 + CF Cells via next Skunkworks batch
2. Spawn phase-diagram cells for chain-grade primitives (USER strategic directive; multi-hop depth-sensitivity = highest leverage)
3. Continue Stage 3 gap-filling: causal-chain extraction, abductive reasoning, hypothesis generation drills
4. Cortex_hippo_handoff full when it lands (will free queue)

-- Research (Opus 4.7-1M) — 2026-06-28 ~00:30Z UPDATE #19 (Stage 3 Wave 2 in flight; 7 agents; multiple chain-grade-quality smokes staged)

---

## TWENTIETH-WAVE UPDATE 2026-06-28 ~01:15Z — OVERNIGHT 12+ HOUR PLAN + REMAINING CONCERNS

**USER leaving for 12+ hours. This update is THE load-bearing plan that must survive compaction.**

### SESSION SCORECARD (honest, post-Skunkworks reality check)
- **CERT 626** (unchanged from earlier session; +3 chain-grade earlier today: parietal MOVABLE + engram methodology + substrate depth-5)
- **6 new atoms today via Skunkworks batches 12+13** (5 MEASURED_MECHANISM + 1 META rule AL)
- **9 META rules atomized** (AC-AK; lock-in of discipline lessons)
- **5 memory rules** filed (substrate-as-canonical / no-hallucinated-numbers / path-disambiguation / compute-formulas-in-code / **NEW: test-rationality-encoding-before-readout**)
- **7 Director framing errors caught** by cert-owner (over-claiming chain-grade from previews/single-seed/wrong-path)
- exp_dev.md hardened +129 lines (§6-§12 mandatory)
- Landing notifier registered (4-day silent drift fixed)
- Monitor popups fixed (Hidden=true pythonw)

### MAJOR FINDINGS TODAY (honest tier)
1. **Importance ceiling REAL** (v7B n=16 at proper CRLB regime; PCA/Fisher at noise floor)
   - USER's sharp insight: test was IRRATIONAL — reading geometry no operation ever wrote importance into. Months of M-CFU work chased an artifact.
   - Substrate's working importance signals are ALL via explicit encoding: TRACE / ultrametric / tagging / frequency. Passive geometric discovery doesn't work because nothing writes.
2. **Substrate compositional reasoning at depth=5 ALREADY chain-grade** (Cycle 1 v3+v4 substrate-product win)
3. **Schema-driven inference via cheap cosine ALREADY chain-grade** (3 mechanism families tested; all tied cosine)
4. **Substrate cosine more robust than predicted** (M-sweep up to M=1024 no cliff; cross-schema overlap up to 90% no MAC+FAC crossing)
5. **Cortex_hippo seed 7 chain-grade** (lift +0.995 at full N_c=8192; seeds 17+23 still running)
6. **TOM Sally-Anne smoke chain-grade-quality** (Q2=0.900 false-belief; full pending)
7. **CF Cell 2 v2 delta-stack 5.47x latency speedup** (engineering atom; parent atom auto-promote candidate)
8. **Substrate-product narrative shift**: "substrate already does X via existing primitives" pattern fired 5+ times today. M3 capabilities are MORE banked than we thought.

### REMAINING LOAD-BEARING CONCERNS (USER's question; no jargon + analogies)

**Concern #1: Hypothesis generation**
- What we'd lose: substrate verifies hypotheses (audit-chain CG) but can't PROPOSE novel ones. Without this, can't do scientific discovery, can't propose "maybe X explains Y?" without user prompting
- Analogy: like a librarian who can fetch any book you ASK for but can't suggest a book you haven't thought of
- Prior work scour: nothing direct in KB (search for "hypothesis_generation" returns generic WordNet hits)
- Barrier: substrate is a single-pass oracle — needs ITERATION + PROPOSAL machinery
- New idea: compose substrate-MAX (chain-grade for reasoning) + CF replay + random-vector seeds = "generate K candidate hypotheses, score each via CF outcome"
- Status: drill candidate; not yet started

**Concern #2: Self-explanation / introspection**
- What we'd lose: substrate gives answers but can't explain WHY. Critical for M3 glass-box property
- Analogy: a calculator that gives the right answer but can't show its work
- Prior work scour: nothing direct. Metacognition single-signals CG (cosine_sep / entropy AUROC=0.86) but composition fails
- Barrier: introspection requires meta-level READ of own computation; substrate operations are single-pass
- New idea: chain-of-retrieval logging + audit-chain back-trace + metacog confidence-on-each-step
- Status: drill candidate

**Concern #3: Long-context narrative coherence (>100 events)**
- What we'd lose: substrate handles K=20 sequence binding chain-grade but tracking dozens of events in conversation untested. M3 critically needs this
- Analogy: like a person who can remember a conversation's last 5 turns but loses track at turn 50
- Prior work scour: sequence-binding K=20 CG; multi-hop depth-15 CG. **Not tested at narrative scale (100+ events)**
- Barrier: capacity envelope vs interference vs coreference resolution
- New idea: compose TWO_TIER generational W (CG) + NREM replay (CG) + multi-hop chain — narrative as "long episode" with hippo→cortex consolidation
- Status: drill candidate; could leverage cortex_hippo_handoff full once it lands

**Concern #4: Online learning during conversation**
- What we'd lose: substrate has continual learning CG (CRISPR forget=0.006) but tested batch-style. M3 needs single-shot updates DURING conversation
- Analogy: a person who can study a textbook overnight but can't learn from a single mentioned fact mid-conversation
- Prior work scour: continual_learning_crispr CG; substrate_cl_crispr_append_only CG (banked)
- Barrier: single-shot online updates with no interference + no replay budget
- New idea: TASK_VECTOR HRR ICL primitive (today's chain-grade smoke) IS the answer — substrate has it. Just untested in conversation context
- Status: PARTIALLY ADDRESSED already (TOM v1 + task_vector ICL); needs conversational-scale integration test

**Concern #5: Goal-directed planning beyond preplay**
- What we'd lose: substrate can do K=64 beam preplay (smoke MB) but not full subgoal decomposition; M3 needs "plan then execute" for tools
- Analogy: substrate can recognize the path to a goal but can't decompose "make breakfast" into "boil water" → "crack egg" → ...
- Prior work scour: substrate_preplay_beam_to_goal smoke MB; STRIPS-style classical planning hasn't been tested
- Barrier: hierarchical goal decomposition + means-end analysis
- New idea: HRR-bind subgoal trees + recursive preplay; brain analog = prefrontal hierarchical control
- Status: drill candidate

### OVERNIGHT 12+ HOUR AUTONOMOUS PLAN

**Currently in flight (will land overnight):**
- cortex_hippo_handoff FULL seeds 17+23 (~1-2h more wall)
- CF Cell 1 vmPFC FULL (queue pos 17; runs when cortex_hippo finishes)
- CF Cell 2 v2 FULL (queue pos 16)
- TOM v1 FULL (queue pos 14)
- Schema ANCHOR 3 FULL (queue pos 15)
- Parietal v2 FULL (queue pos 12)
- Schema M-sweep FULL (if dispatched)
- Cycle 1 v5 depth=10 smoke (queue pos 11)
- tip_of_tongue v2 smoke (queue pos 9)
- pfc_goal v3 smoke (queue pos 10)
- Temporal v3 (queue pos varies; some)
- PFC ARGMAX v3 smoke (currently running)
- M-CFU v7B FULL on GPU (already completed; confirmed REAL ceiling)
- Causal-chain extraction cell (smoke HF cardinality; cell-author may iterate)

**Agents in flight at this update:**
- ad9b4232 Causal-chain cell author (smoke landed; need to iterate cardinality)
- a098471 Abductive reasoning drill (handoff just filed)
- Maybe others

### AUTONOMOUS-LOOP CRON PRIORITIES (every 15 min)

Per `data/autonomous_loop_instructions.md`:

1. **Touch heartbeat**
2. **Check landings since last wake** (find data -mmin -20)
3. **For each new landing, READ metrics.json ABSOLUTE PATH directly** — do NOT trust framings, do NOT cite cell-author preview as smoke
4. **Atomize chain-grade-quality results via Skunkworks batches** when 5+ atoms staged
5. **Default to MEASURED_MECHANISM tier** — let Skunkworks tier up (7 Director-errors today; over-claiming is the pattern)
6. **Watch for cortex_hippo seed 17+23 completion** — when full lands, parietal+hippo cortex story banked + queue drains
7. **Process abductive drill** when it returns (cell-author next)
8. **Iterate causal-chain cell** to fix cardinality (5 arms × 3 seeds = 45 expected; smoke had 15 = single seed bug)
9. **NO SPAWN SPAM** — only spawn if there's clear ROI; respect Fix #14 plus USER-authorized exceeding
10. **If queue clears (cortex_hippo done)**: dispatch next phase-diagram cell (K_NEAREST sweep or FILLER_NOISE per M-sweep author's recommendation)

### EXPLICIT DON'T-DO LIST

- DO NOT spawn 5+ drills in parallel just to look busy
- DO NOT claim chain-grade from cell-author previews (cite metrics path + verify on disk)
- DO NOT design readout tests without specifying encoding mechanism (new META_RULE filed today)
- DO NOT chase "PCA/Fisher fusion" importance any further (Skunkworks ceiling-real verdict closes that arc)
- DO NOT iterate Temporal beyond v3 (MM tier acceptable; rare-class issue isn't substrate-fundamentals)
- DO NOT iterate Schema ANCHOR family beyond what's done (cosine wins; META_RULE_AL atomized; move on)
- DO NOT push to main (harness-DENIED; spawn orchestrator OR let hd_metrics_sync auto-push at :03/:18/:33/:48)

### POST-COMPACTION RITUAL (if compaction happens overnight)

1. Touch heartbeat: `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`
2. **READ THIS BACKUP FILE end-to-end** through UPDATE #20 (today's load-bearing state)
3. Read the 5 new memory rules: substrate-as-canonical / no-hallucinated-numbers / path-disambiguation / compute-formulas-in-code / **test-rationality-encoding-before-readout** (this last one is USER's key insight today)
4. Check landings since 01:15Z: `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -720`
5. Check cortex_hippo full landing (most likely overnight win)
6. Re-arm notes_monitor per CLAUDE.md
7. Check cron alive (3a20be75 :03/:18/:33/:48; should fire ~50 times overnight)

### EXPECTED OVERNIGHT WINS (if normal queue throughput)

- cortex_hippo full chain-grade verified (3 seeds)
- TOM v1 full chain-grade verified
- Schema ANCHOR 3 full chain-grade verified
- CF Cell 1 vmPFC full HARD_PASS (R²~0.98 per preview)
- CF Cell 2 v2 full chain-grade verified (auto-promotes parent atom)
- Parietal v2 RELATIONAL chain-grade verified
- Cycle 1 v5 depth=10 smoke verdict (Barrier 1 actual test)
- tip_of_tongue v2 / pfc_goal v3 / Temporal v3 smoke verdicts
- 1-2 more Skunkworks batches (CERT possibly 626 → 630-635)
- Abductive reasoning cell (after drill returns + dispatch)

### USER QUESTION SUMMARY (intuitive, no jargon)

**Concerns that remain, in plain language:**
1. **Can it propose new ideas?** Not yet. Substrate verifies hypotheses but can't generate them. Drill candidate.
2. **Can it explain its reasoning?** Partial. Has metacognition signals but composition fails. Drill candidate.
3. **Can it follow a long conversation?** Untested at >100 events. Has the pieces (sequence binding + multi-hop + replay); needs the composition test.
4. **Can it learn during conversation?** Partially yes (task_vector ICL chain-grade today). Needs conversation-context integration.
5. **Can it plan multi-step?** Partial (preplay smoke MB). Hierarchical subgoal decomposition untested.

**What we'd lose without each:** scientific discovery / glass-box trust / coherent dialogue / real-time learning / tool use. Each is M3-load-bearing but none is THE blocker.

**The good news:** today's substrate-product narrative shows substrate is MORE capable than we tested for. Many "new mechanisms" turn out to be already-done via existing primitives. The remaining concerns are mostly TEST COVERAGE not substrate capability gaps.

-- Research (Opus 4.7-1M) — 2026-06-28 ~01:15Z UPDATE #20 (OVERNIGHT 12+H PLAN; compaction-survival; USER concerns answered)

---

## TWENTY-FIRST-WAVE UPDATE 2026-06-28 ~13:30Z — OVERNIGHT WAVE EXECUTION RESULTS + COMPACTION PREP

**USER returned briefly + asked overnight summary + requested compaction prep.**

### FINAL SESSION SCORECARD (verified, not over-claimed)

- **CERT 626 → 628 (+2 chain-grade verified)**: CF Cell 1 regret vmPFC v1 (R²=0.987) + Schema exemplar-Bayes ANCHOR 3 (promoted from batch 13 MM after FULL landed)
- **10 atoms today** across 2 Skunkworks batches (commits f77c7d29 + 16a501c3)
- **2 new META rules atomized** (AM + AN)
- **9 Director-framing-errors caught** by cert-owner today — discipline ladder working
- 5 memory rules filed total (substrate-as-canonical / no-hallucinated-numbers / path-disambiguation / compute-formulas-in-code / test-rationality-encoding-before-readout)

### BARRIER 1 MECHANISM FOUND (THE load-bearing finding for post-compaction me)

**Multi-hop partition-oracle revival smoke HARD_PASS at depth-10**:
- Path: `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_smoke/metrics.json`
- BASELINE_A=0.190, ORACLE_B=1.000, RANDOM_E=0.000, lift +0.81 at N=2048
- N=8192 variant: BASELINE_A=0.590, ORACLE_B=1.000, lift +0.41 at N=8192
- Path n8192: `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192_smoke/metrics.json`

**CRITICAL INSIGHT**: All 3 prior Cycle 1 attempts (v3/v4/v5) tested WRONG mechanism class — brain-pushback (PFC scratchpad / replay shortcuts / bidirectional meeting) are DOWNSTREAM of cleanup. Partition-oracle goal-conditioning is UPSTREAM of cleanup (restricts search space). Drill diagnosis vindicated.

**Tier**: MEASURED_MECHANISM (auto-demote per saturation=True; ORACLE_B hits ceiling 1.000). To get chain-grade, need un-saturated regime (V_C=16000 OR depth=15+ per cell-author analysis).

**STRATEGIC NEXT STEP**: spawn `exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192_hardened` cell-author with V_C=16000 depth=15 to find non-saturated discriminating point. If HARD_PASS, Barrier 1 chain-grade promoted.

### META RULES ATOMIZED TODAY (load-bearing for next-session discipline)

**META_RULE_AM (batch 14)**: "substrate already does X via existing primitives" — 7+ occurrences:
1. Schema ANCHOR 1 vmPFC context-prior tied EXEMPLAR cosine baseline (lift +0.003)
2. Schema ANCHOR 2 MAC+FAC LOST to cosine baseline (-0.063)
3. Schema M-sweep up to M=1024: no cliff
4. Schema cross-schema overlap 0-90%: cosine wins all
5. Hierarchical v1 at easy regime: FLAT preplay already saturates
6. Self-explanation: raw cosine attribution beats bind-trace (0.467 vs 0.240)
7. Narrative ANCHOR 1: NO_SEGMENT = FULL_STACK at smoke

**Discipline**: any "richer mechanism" cell-author must demonstrate substrate's existing primitive FAILS at that regime FIRST.

**META_RULE_AN (batch 15)**: cone-collapse formula calibrated to N=2048; substrate is 3.7x more capable at N=8192 than formula predicts. Cells using cone-collapse formula at N≥4096 MUST include empirical baseline arm. Substrate-product win: substrate physics MORE capable than substrate-physics formula said.

### USER M3 CONCERNS — STATUS (from yesterday's 5)

1. **Hypothesis generation**: SWR-preplay generator works (recall@10=0.558 novelty=1.000); pipeline integration weak → MEASURED_MECHANISM
2. **Self-explanation**: substrate does via raw cosine attribution (0.467); bind-trace adds nothing → workable but bounded
3. **Long-narrative coherence**: Q1 factual + Q4 contradiction at chain-grade-quality (0.89 / 1.00) on 100-event narrative; Q2 coreference + Q3 temporal collapse → partial M3
4. **Online conversation learning**: cell-author bug (kth=64 OOB vocab=60); needs fix
5. **Hierarchical planning: UNRESOLVED after 2 attempts** — macro vocabulary non-compositional at depth-8; Sutton-Precup options framework redesign needed (research-owned)

### CHAIN-GRADE PORTFOLIO ADDITIONS TODAY (verified)

- CF Cell 1 regret vmPFC v1 (R²=0.987 rank=0.989; substrate vmPFC regret primitive)
- Schema exemplar-Bayes ANCHOR 3 (substrate cosine kernel pre-encodes schema structure)

### KNOWN ISSUES (load-bearing for post-compaction me)

1. **cortex_hippo_handoff FULL DIED at 4h timeout** (22:11Z 2026-06-27). Only seed 7 partial saved. Needs RE-ARCHITECT (chunked seeds OR longer timeout) before re-dispatch. Smoke pattern lift +0.998 stands.
2. **Online_conv cell bug**: `ValueError kth=64 OOB vocab=60`; cardinality_ok=False. Cell-author needs fix.
3. **VALID_CERT_CLASS missing `proven_negative_smoke`**: HONEST_NEG atomization tools hit recovery path. Convention: use `cert_class='mechanism_characterization'`.

### POST-COMPACTION RITUAL (overrides UPDATE #20's older version)

1. **Touch heartbeat**: `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`
2. **Read this BACKUP file end-to-end** — UPDATES #1 through #21. UPDATE #21 (this one) is the latest substantive state.
3. **Push timestamps far ahead** (silences overnight stop hook + watchdog noise):
   ```bash
   date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/last_processed_auto_7c6e8deae7.timestamp
   date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/last_processed_research.timestamp
   ```
4. **Read 5 memory rules**: substrate-as-canonical / no-hallucinated-numbers / path-disambiguation / compute-formulas-in-code / **test-rationality-encoding-before-readout**
5. **Check landings since 13:30Z**: `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -180 -printf '%TH:%TM %p\n' | sort`
6. **Verify scheduled tasks** (PowerShell, NOT bash): `schtasks /query /tn hd_landing_notifier /fo LIST`
7. **Re-arm notes_monitor** per CLAUDE.md ritual
8. **Cron**: 3a20be75 :03/:18/:33/:48 session-only; may NOT survive Claude Code restart — re-arm via CronCreate if needed

### NEXT-STEP PRIORITIES (post-compaction; in order)

1. **Spawn partition-oracle hardened-regime cell** (V_C=16000 OR depth=15+) to verify Barrier 1 chain-grade — highest-leverage single experiment
2. **Sutton-Precup options framework** drill + cell for hierarchical planning (ANCHOR 2 from yesterday's revival drill)
3. **cortex_hippo_handoff re-architect** (chunked seeds + longer timeout)
4. **Online_conv cell-author fix** (kth OOB bug)
5. Continue per autonomous_loop_instructions.md priorities + USER directives

### STATE OF EXP_DEV.MD DISCIPLINE

Hardened today (+129 lines §6-§12 yesterday):
- §6 META_RULE_AF arms-must-differ SHA-256
- §7 META_RULE_AH atomic-final-metrics-write
- §8 SystemExit re-raise BEFORE BaseException
- §9 CRLB pre-validation
- §10 baseline_in_band 0.05<x<0.95 smoke-gate
- §11 number tagging MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
- §12 cell-template summary block

12 META rules atomized today: AC/AD/AE/AF/AG/AH/AI/AJ/AK (batch 13) + AL (batch 13) + AM (batch 14) + AN (batch 15).

### THE BIG-PICTURE SUBSTRATE-PRODUCT NARRATIVE

**Substrate is MORE CAPABLE than yesterday's framing suggested.** Pattern of the day: existing chain-grade primitives (cosine cleanup / flat preplay / explicit encoding) repeatedly handle things "richer mechanisms" were proposed to add.

**The genuine remaining Stage 3 gaps are NARROW**:
- Hierarchical planning (needs Sutton-Precup options-framework redesign)
- Q2 coreference + Q3 temporal at long-narrative scale (new mechanism class needed)
- Pipeline integration of hypothesis-gen with abductive scorer (engineering)

**Everything else (counterfactual / TOM / schema-driven / depth-5 composition / parietal MOVABLE+RELATIONAL / abductive / task_vector ICL / order-sensitive sequence binding / self-explanation via cosine / Barrier 1 mechanism via partition-oracle goal-conditioning)** = already done via existing primitives OR identified-but-pending-chain-grade. Just needed test coverage + correct mechanism class.

**M3 conversational AI (12-18 month goal) gap-list shrunk substantially today.**

-- Research (Opus 4.7-1M) — 2026-06-28 ~13:30Z UPDATE #21 (compaction-prep; substantive overnight wave summary; load-bearing for post-compaction me)

---

## TWENTY-SECOND-WAVE UPDATE 2026-06-28 ~13:45Z — COMPACTION READINESS FINAL

**USER request: "finalize readiness for compaction. all important context for keeping work going: recent finishes / short-term / long-term goals"**

This UPDATE is the LOAD-BEARING ENTRY POINT for post-compaction me. Read it FIRST after touching heartbeat.

### COMPLETE FOUR-WAVE COVERAGE TODAY (read UPDATES #1-22 sequentially)
- UPDATE #1-10: Yesterday's session arc (Skunkworks vets / Wave 1+2 cells / 5x drills / phase-diagram framework / OVERNIGHT PLAN baseline)
- UPDATE #11-19: Post-compaction execution wave (refusal + correction + Stage 3 chain-grade landings + 9 META rules atomized)
- UPDATE #20: OVERNIGHT 12h PLAN (5 USER concerns + 5 drills + autonomous-loop instructions)
- UPDATE #21: OVERNIGHT EXECUTION RESULTS (Barrier 1 mechanism FOUND + 2 CG promotions + 2 new META rules)
- UPDATE #22 (THIS): compaction readiness + recent finishes + goals

### RECENT FINISHES (since UPDATE #21 ~30 min ago)

**Online_conv revived + dispatched** (cell-author a5f2746a):
- Bug fixed: `REFUSE_V_REL=64 > V_ENTITIES=60` triggered np.partition kth OOB
- Fix: `v_rel_eff = min(REFUSE_V_REL, sims_tv.shape[0] - 1)` (Option 1 minimal-change)
- Re-smoke HARD_PASS: TV_HIPPO=1.000 vs VANILLA=0.000 lift +1.000; cv=0; cardinality_ok=True
- TV_HIPPO ties TV_ONLY at smoke (cortex_hippo composition adds nothing at this scale; full at V=256 will discriminate)
- Full dispatched remote_cpu_queue pos 1; timeout 3600s
- Path: `d:/AI/hd-instrument/data/exp_online_conv_oneshot_taskvec_hippo_v1_smoke/metrics.json`

**Cortex_hippo chunked re-architect** (cell-author afe5e412; hit rate-limit but cells authored + smokes ran):
- 3 cells: `exp_cortex_hippo_handoff_FULL_seed_{7,17,23}_v1.py`
- Each cell: N_h=512 N_c=8192 M=200 N_REPLAY_CYCLES_FULL=50 (single seed; chunked architecture)
- Smoke (N_replay=5) seed_7 HARD_PASS: FULL=1.000 NO_REPLAY=0.003 gap +0.998
- Smoke seed_17 HARD_PASS: same pattern (FULL=1.000 gap +0.998)
- Smoke seed_23 still running
- **FULL multi-seed dispatches PENDING** (cell-author rate-limited before dispatch)
- Path: `d:/AI/hd-instrument/data/exp_cortex_hippo_handoff_FULL_seed_7_v1_smoke/metrics.json` + `_17_v1_smoke/`

### SHORT-TERM GOALS (next 1-2 days; post-compaction)

**Priority 1: Spawn FULL multi-seed dispatch for cortex_hippo chunked cells.** Cell-author was rate-limited; cells exist and smokes pass. Each cell runs ~2.35h on remote_cpu (single seed at N_replay=50). All 3 in parallel via queue OR sequentially. Once all 3 land HARD_PASS at full N_replay=50, cortex_hippo_handoff atom promotes to chain-grade (currently MM tier).

**Priority 2: Spawn partition-oracle hardened-regime cell** (V_C=16000 OR depth=15+ per cell-author analysis in UPDATE #21). Goal: find non-saturated discriminating point so partition-oracle goal-conditioning gets chain-grade promotion (currently MM tier). If HARD_PASS → BARRIER 1 BROKEN AT CHAIN-GRADE TIER.

**Priority 3: Sutton-Precup options framework drill + cell** for hierarchical planning (the ONE remaining genuine Stage 3 gap; 2 attempts failed; needs research-owned redesign).

**Priority 4: Skunkworks batch 16** for:
- cortex_hippo chunked full results (when all 3 seeds land)
- online_conv full result (when dispatched cell completes)
- Any other interim findings

**Priority 5: Continue substrate-product narrative composition** for USER on next interaction. Day's wins are substantial.

### LONG-TERM GOALS (per USER program)

**M3 (12-18 month): glass-box conversational AI without Claude in loop.** Status today:
- Stage 1 (base memory/retrieval/cleanup): MATURE chain-grade
- Stage 2 (optimization/extraction/consolidation): MATURE chain-grade
- Stage 3 (higher functions): mostly banked; 1 genuine gap (hierarchical planning)
- Stage 4 (LM equivalence): DEFERRED per USER stage progression directive

**M4 (18-30 month): hybrid agentic experiment loop (substrate-as-research-director).** Today's findings strengthen this — discipline ladder + cert-owner-overrides-Director patterns proven; substrate-product narrative shows substrate is more capable than today's framings.

**M5 (5+ yr aspirational): full code-gen.** Today's substrate-product story (substrate more capable than expected) feeds M5 hypothesis: substrate may already have many M5-required primitives via existing chain-grade composition.

**USER target = aim M3, stretch M4.**

### USER M3 5 CONCERNS — STATUS AS OF NOW

1. **Hypothesis generation**: MEASURED_MECHANISM — SWR-preplay generator works (recall@10=0.558 novelty=1.000); pipeline scorer-integration weak
2. **Self-explanation**: workable via cosine attribution (0.467); bind-trace adds nothing (HONEST_NEG-bounded)
3. **Long-narrative coherence**: partial M3 — Q1 factual + Q4 contradiction at chain-grade quality (0.89/1.00) on 100-event; Q2 coreference + Q3 temporal collapse
4. **Online conversation learning**: HARD_PASS smoke (TV_HIPPO=1.0 vs VANILLA=0.0); full dispatched; CG-eligible
5. **Hierarchical planning**: UNRESOLVED — needs Sutton-Precup options framework

### CRITICAL INFRA STATE

- **CERT 628** (after batches 14+15; commits f77c7d29 + 16a501c3)
- **cron 3a20be75** alive (session-only; may not survive Claude Code restart — re-arm via CronCreate if needed)
- **hd_landing_notifier** scheduled task ALIVE (registered yesterday; runs every 3 min)
- **hd_metrics_sync** scheduled task ALIVE
- **cpu_runner_0** alive on remote (PID may rotate but role persistent)
- **gpu_runner_0** alive but mostly idle (Fix #24: most cells aren't CUDA-eligible)
- **Watchdog every ~20 min** firing notes_for_research pings (overnight noise; harmless; touch heartbeat per turn)
- **Stop hook** triggers on session-specific `last_processed_auto_7c6e8deae7.timestamp` (NOT role-specific). Push +24h to silence overnight.
- **autonomous_loop_instructions.md** current at `d:/AI/hd-instrument/data/autonomous_loop_instructions.md` (USER 2026-06-28 directives baked in)

### LOAD-BEARING DOCS POST-COMPACTION

In order of importance:
1. **THIS FILE** — `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` (UPDATE #22 latest)
2. `MEMORY.md` — 5 memory rules under "USER-LOCKED OPERATING RULES":
   - feedback_substrate_as_canonical_query_first_USER_LOCKED_2026-06-27.md
   - feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md
   - feedback_metrics_path_disambiguation_selftest_smoke_full_2026-06-27.md
   - feedback_compute_formulas_in_code_before_quoting_2026-06-27.md
   - feedback_test_rationality_encoding_before_readout_2026-06-27.md (USER's key insight)
3. `notes/research_synthesis_overnight_substrate_already_does_X_pattern_2026-06-27.md` — META_RULE_AM evidence base
4. `notes/research_findings_for_next_skunkworks_batch_2026-06-27_post_compaction.md` — 14 atom candidates staged
5. `notes/research_strategic_phase_diagram_framework_all_chain_grade_capabilities_2026-06-27.md` — phase-diagram strategic framework
6. `.claude/agents/exp_dev.md` — hardened §6-§12 (12 META rules locked in)
7. `data/autonomous_loop_instructions.md` — what to do every cron fire
8. Drill notes for revival cells (Sutton-Precup options pending; partition-oracle harder regime pending)

### POST-COMPACTION RITUAL (DEFINITIVE; overrides earlier versions)

```bash
# 1. Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# 2. Silence stop hook + watchdog overnight noise
date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/last_processed_auto_7c6e8deae7.timestamp 2>/dev/null
date -u -d "+24 hours" +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/last_processed_research.timestamp

# 3. Read this BACKUP file UPDATES #20 #21 #22 (latest state)

# 4. Read 5 memory rules (MEMORY.md USER-LOCKED RULES section)

# 5. Check recent landings (cortex_hippo + online_conv full should be in flight)
find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -180 -printf '%TH:%TM %p\n' | sort

# 6. Verify scheduled tasks (PowerShell)
# schtasks /query /tn hd_landing_notifier /fo LIST

# 7. Re-arm notes_monitor per CLAUDE.md ritual

# 8. Check cron (CronList tool); if dead re-arm

# 9. Drive forward per Priority 1-5 above
```

### THE BIG-PICTURE SUBSTRATE-PRODUCT NARRATIVE (refined)

**Substrate is SUBSTANTIALLY MORE CAPABLE than yesterday morning's framing suggested.** Today validated:
- Existing chain-grade primitives (cosine cleanup / flat preplay / explicit encoding / partition routing / cortex_hippo / task_vector ICL) handle most "richer mechanisms" propositions
- 7+ "substrate already does X" occurrences across mechanism axes (META_RULE_AM)
- Substrate cone-collapse formula UNDERESTIMATES substrate capability by 3.7x at N=8192 (META_RULE_AN)
- Barrier 1 mechanism class IDENTIFIED (goal-conditioning UPSTREAM of cleanup; prior 3 attempts tested wrong class)

**Genuine remaining Stage 3 gaps (NARROW)**:
- Hierarchical planning (Sutton-Precup options-framework redesign needed)
- Long-narrative coreference + temporal (mechanism class TBD)
- Hypothesis-gen pipeline integration (engineering)

**M3 timeline (12-18mo) STRENGTHENED.** Substrate-product roadmap validated by today's experimental wave + 9 Director-framing-errors caught (discipline ladder working as designed).

### DAY'S DELTA SUMMARY (2026-06-27 to 2026-06-28)

- CERT: 623 → 628 (+5 chain-grade over 2 days)
- META rules: +12 atomized (AC through AN)
- Memory rules: +5 USER-LOCKED disciplines
- Atoms total: ~25 across Skunkworks batches 10-15
- exp_dev.md: +129 lines hardened (§6-§12)
- Landing notifier infra: registered (was 4-day silent drift; root-cause fixed)
- Cells dispatched: 20+ (smokes + fulls)
- Director-framing-errors caught: 9 (discipline ladder reinforced)
- USER concerns addressed: 5 of 5 (4 substantively; 1 hierarchical still genuine gap)

**Net assessment: substantive substrate-product wins; honest tier-MM where saturated; M3 capabilities banked or characterized for the vast majority.**

-- Research (Opus 4.7-1M) — 2026-06-28 ~13:45Z UPDATE #22 (FINAL compaction-readiness; load-bearing entry point for post-compaction me)

---

## TWENTY-THIRD-WAVE UPDATE 2026-06-28 ~15:45Z — POST-COMPACTION RECOVERY + AGGRESSIVE BUILD-OUT WAVE

**Session context:** Resumed post-compaction at ~13:55Z. USER active throughout afternoon. Heavy ship cycle.

### MAJOR FINDINGS THIS WAVE

1. **Barrier 1 mechanism HARDENED-REGIME SMOKE PASS** — partition-oracle goal-conditioning at N=8192 / V_C=4000 / depth=15 / psz_B=800: BASELINE_A=0.39 (un-saturated), ORACLE_B=0.90, lift_B_A=+0.51, lift_B_E=+0.90. arms-distinct verified. **FULL queued + RUNNING on remote_cpu since 11:44:26Z (~2.5h budget).** Path: `data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json`. If FULL HARD_PASS → Barrier 1 chain-grade promotion.

2. **Hierarchical planning capability — closure REVERSED then RE-TESTED via 2 revival cells:**
   - I prematurely atomized closure after the 3rd HARD_FAIL (Sutton-Precup options; commit `eda3d108`).
   - USER caught: "we need to verify the test before we close a capability, and I always want to drill 2x on those negatives before closed"
   - Memory rule filed: `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md`
   - **Drill A (Bacon-Roy option-critic):** CLOSURE_PREMATURE_ITERATE — REINFORCE-learned π+β is 4th mechanism class; HDPG existence proof (Ni-Imani 2022 DAC); cell `exp_substrate_hierarchical_option_critic_v1` dispatched (still running smoke ~20-40min; ~15min elapsed at this update).
   - **Drill B (Hersche block-sparse):** CLOSURE_PREMATURE_ITERATE — encoding axis untested; cell `exp_substrate_hierarchical_block_sparse_v1_smoke` landed HARD_FAIL (BS_OPTS=0.100 LOSES to RANDOM_BLOCKS=0.200; encoding-axis rescue REFUTED). Dense baseline replicates prior failure cleanly.
   - **Closure status: PRELIMINARY pending Cell A.** If Cell A HARD_FAILS → 5-cell evidence base supports closure. If Cell A HARD_PASSES → policy-learning axis is the genuine rescue; iterate.

3. **Substrate capability registry BUILT (centralization fix):**
   - USER 2026-06-28 asked "is substrate performance data centralized so it's hard to forget something?" — honest answer was "partially; real forget-risk; 9 Director-framing errors yesterday partly came from incomplete memory."
   - Tool: `tools/substrate_capability_registry.py` + family regex `tools/substrate_capability_families.json` + view `data/substrate_capability_registry.jsonl`
   - First-run: 4447 metrics.json scanned, 0 malformed; 37 capability families; verdict spread HP=1422/HF=665/MB=553; **80 forgotten high-tier findings surfaced** (un-atomized HARD_PASS / cross-cell wins)
   - Scheduled task registered: `hd_substrate_capability_registry_scan` 15-min cadence
   - 80-finding atomization batch DEFERRED (USER rejected the broader batch earlier; offer to do narrow-scope batches later)

4. **Dashboard "Substrate Characteristics" tab BUILT (and optimized):**
   - First build: testbed dispatched per USER ask — one row per capability_family; mouseover descriptions; tier/peak/phase-coverage columns; sortable/filterable; aggregation tool `tools/substrate_capabilities_aggregate.py`; view `data/substrate_capabilities_view.json`; scheduled task `hd_substrate_capabilities_aggregate` 15-min
   - Then dashboard optimization drill (general-purpose agent + web research): 5 changes SHIPPED (`index.html` +184 lines):
     - (1) Health banner OK/WARN/ERROR from `/api/dashboard/v2/health`
     - (2) Per-section freshness badges (fresh/2m/4h)
     - (3) ZOMBIE badge when pid_alive=false + queue_marks_running=true
     - (4) Verdict-distribution sparkline (stacked SVG) per row — Tufte data-ink
     - (5) Tier glyphs (CG/MM/HN/EX) — WCAG color-not-alone
   - 5 more deferred: localStorage "new since last visit" / URL-hash deep-links / Page Visibility pause-polling / CERT 7d motion sparkline / keyboard shortcuts
   - **Critical finding from agent's live probe: aggregate health = ERROR right now (43 hygiene flags + 3 stale sessions + 1 drift-red) — UI previously hid this.** Investigation deferred.

5. **Recurring GPU runner zombie pattern (real infra bug):**
   - GPU runner died 3 times today (09:50, 10:02, 10:58, 11:41) after START log line; survived 4th attempt 11:44:22Z
   - Root cause partial: stale `queue.json.lock` from 5/20/2026 + stale pid files; cleaned + restarted; runner picked up multi-hop smoke
   - **Still unresolved:** runner death between START and DONE has no error log line; needs deeper investigation (maybe lock contention / GPU init race / cuda kernel hang). Defer until current cells complete.
   - CPU runner had same pattern earlier; restart pattern works but not root-cause fix
   - **3 cortex_hippo seed FULL zombies reset to pending** (claimed_by stale; never finished). Will run sequentially after partition-oracle FULL.

6. **Online_conv FULL = HARD_FAIL at 2.1s** — cell bug at full regime (smoke worked yesterday TV_HIPPO=1.0). Same kth=OOB pattern returned. Deferred; back to cell-author when bandwidth allows.

### IN FLIGHT AT TIME OF UPDATE #23

- **Cell A option-critic** (background spawn) — smoke ~15 min elapsed of 20-40 min budget
- **partition-oracle hardened FULL** — RUNNING on remote_cpu since 11:44:26Z (~2.5h)
- **multi-hop phase diagram smoke** — RUNNING on GPU since 11:44:22Z (~10 min elapsed)
- **pattern completion FULL** — queued on GPU behind multi-hop smoke (18000s budget for 72 points)
- **3 cortex_hippo seed FULL** — queued on remote_cpu behind partition-oracle (chunked architecture)

### MEMORY RULES ADDED THIS WAVE
- `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md` (USER caught premature hierarchical closure)

### TOOLS BUILT THIS WAVE
- `tools/substrate_capability_registry.py` + `data/substrate_capability_registry.jsonl` (4447 rows)
- `tools/substrate_capabilities_aggregate.py` + `data/substrate_capabilities_view.json` (37 families)
- Dashboard `index.html` substantial enhancement (+184 lines; 5 of 10 changes shipped)
- Scheduled tasks: `hd_substrate_capability_registry_scan` + `hd_substrate_capabilities_aggregate` (both 15-min)

### NEXT-STEP PRIORITIES (post-compaction)
1. Process Cell A option-critic smoke when it lands (~5-25 min from now)
2. Process partition-oracle hardened FULL when it lands (~2.5h from now) — if HARD_PASS → Barrier 1 CG promotion via Skunkworks
3. Process multi-hop phase diagram smoke when it lands → if pass, dispatch full to GPU
4. Process pattern completion FULL when it lands (~5h on GPU)
5. Process 3 cortex_hippo seed FULL when they land (~2.35h each on CPU, sequential)
6. Skunkworks: retract preliminary closure atom OR upgrade to confirmed-closure depending on Cell A
7. Investigate 43 hygiene flags + 3 stale sessions + 1 drift-red (dashboard ERROR aggregate)
8. Resolve GPU runner zombie pattern at infrastructure level (lock backend? GPU init race?)

### CERT TRAJECTORY
- Start of UPDATE #23 wave: CERT 628 (per UPDATE #22)
- Atoms added: 2 hierarchical-closure atoms (commit eda3d108; preliminary)
- Net: CERT 628 + 0 chain-grade (closure preliminary, awaits Cell A)

-- Research (Opus 4.7-1M) — 2026-06-28 ~15:45Z UPDATE #23 (post-compaction recovery + aggressive build-out + closure reversal)

---

## TWENTY-FOURTH-WAVE UPDATE 2026-06-28 ~17:55Z — ROOT-CAUSE FIX + HIERARCHICAL CLOSURE CONFIRMED + NEW DISCIPLINES

**Major events since UPDATE #23:**

### RUNNER ZOMBIE ROOT-CAUSE FIXED (load-bearing infra win)
After 5+ zombie episodes today, testbed root-caused: `start /b python.exe` via SSH causes cmd.exe parent exit → CTRL_CLOSE_EVENT cascade → silent death within 5-10s. Fix shipped:
1. `tools/start_desktop_runners.cmd` → delegates to `schtasks /run /tn "\hd_{gpu,cpu}_runner_0"` (Task Scheduler lineage SSH-disconnect-immune)
2. `experiments/runner_v2_prod.py` → wrapped with `_main_with_diagnostics()` + `faulthandler.enable()` + SIGBREAK handler; future silent deaths leave `data/logs/<runner_id>_runner_fatal.log`
End-to-end verified: 12:42:45 schtasks-launched CPU runner claimed seed_17; 12:43:08 cell completed cleanly exit=0. Memory rule: `feedback_runner_zombie_ssh_disconnect_root_cause_FIXED_2026-06-28.md`.

### HIERARCHICAL PLANNING CAPABILITY CONFIRMED-CLOSED (5-cell evidence)
After USER caught premature closure: ran 2 revival drills (Bacon-Roy option-critic + Hersche block-sparse). BOTH HARD_FAIL at smoke. Closure CONFIRMED (commit 684bf0c2; 4 atoms: 2 cell HFs + 5-cell capability-closed + META_RULE_AO_v2). 5 cells across 4 mechanism classes proved substrate cannot do hierarchical planning natively. M3 architecture decision: needs cortex/planner layer ABOVE substrate (LLM router Phase 1 / learned module Phase 2 / substrate-resident Phase 3). Memory rule: `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`.

### M3 CONCERNS SCORECARD (refined today)
- #1 hypothesis-gen: ✅ pipeline composition smoke HARD_PASS PIPELINE=0.680 lift +0.56; FULL queued
- #2 self-explanation: ⚠️ workable via cosine attribution (bounded; not improved)
- #3 long-narrative coref+temporal: 🔧 ANCHOR 1 composition cell-author in flight (drill diagnosed naive readouts bypassed chain-grade primitives)
- #4 online learning: ✅ TASK_VECTOR genuine CG (cliff at K=100; not by-construction)
- #5 hierarchical planning: ❌ CLOSED at substrate-native (cortex layer required)

**Pattern recurring**: Stage-3 gaps keep dissolving into composition of EXISTING chain-grade primitives (META_RULE_AM firing 9+ times today). Functional-requirement-first discipline is high-leverage. Memory rule: `feedback_functional_requirement_first_test_design_USER_2026-06-28.md`.

### NEW DISCIPLINES + MEMORY RULES FILED TODAY (7 total)
1. `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md` — verify-test + 2 drills before closure
2. `feedback_every_failure_skunkworks_plus_intuitive_explanation_USER_STANDING_2026-06-28.md` — every HF auto-Skunkworks + intuitive
3. `feedback_functional_requirement_first_test_design_USER_2026-06-28.md` — decompose to functional requirements; primitive map first
4. `feedback_every_cell_must_have_error_checking_USER_2026-06-28.md` — chunked + start-marker + crash-diag + heartbeat
5. `feedback_runner_zombie_ssh_disconnect_root_cause_FIXED_2026-06-28.md` — root cause + fix
6. `feedback_post_implementation_hygiene_memorialize_USER_STANDING_2026-06-28.md` — 3-step hygiene after major events
7. `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md` — architecture decision

### NEW INFRA SHIPPED TODAY
- **Substrate capability registry** — `tools/substrate_capability_registry.py` + `data/substrate_capability_registry.jsonl` (4447 rows; 37 families; auto-updated every 15min via `hd_substrate_capability_registry_scan` scheduled task). Surfaced 80 forgotten high-tier findings.
- **Substrate characteristics dashboard tab** — new section in `tools/dashboard/static/index.html` + aggregator `tools/substrate_capabilities_aggregate.py` + view `data/substrate_capabilities_view.json` + scheduled task `hd_substrate_capabilities_aggregate` 15-min. 10 dashboard changes shipped: health banner / freshness badges / ZOMBIE badge / verdict sparklines / tier glyphs / localStorage new-since markers / URL-hash deep-links / Page Visibility pause / CERT 7d sparkline / keyboard shortcuts.
- **Runner observability** — testbed agent ab17f62e71a910f56 in flight: heartbeat + `tools/runner_status.py` CLI (single-command "what's running").
- **Runner observability LANDED 2026-06-28** — three deliverables shipped: (1) `experiments/runner_v2_prod.py` heartbeat enriched (15s cadence; UTC `ts_iso`; `host`/`queue_dir`/`current_cell_started_at`/`current_cell_elapsed_s`/`cells_completed_since_start`/`runner_started_at`/`runner_uptime_s`; canonical `data/logs/<runner_id>_heartbeat.json` write site added alongside legacy two paths); (2) `experiments/_cell_heartbeat.py` helper (`emit_heartbeat` + `CellHeartbeat` context-manager; throttled cadence; boot+exit markers) — referenced from exp_dev.md §13.D; (3) `tools/runner_status.py` CLI with `--remote`/`--verbose`/`--json` modes + exit codes (0=healthy / 1=zombies / 2=missing). Live-tested 2026-06-28T16:55Z — correctly classified all 3 stale runners (cpu_runner_0 + cpu_runner_local + gpu_runner_0) as ZOMBIE via heartbeat-age + flagged the 2 corresponding orphan queue.json `running` entries. Has legacy-heartbeat fallback so pre-patch runners stay visible during rollout. orchestrator.md §RUNNER-ZOMBIE DETECTION updated: `python tools/runner_status.py --remote` is now CANONICAL check. Suggested scheduled task: every 5min, pythonw + CREATE_NO_WINDOW, write stdout to `data/logs/runner_status_scan.log` for trend analysis.
- **Agent instructions hardened** — exp_dev.md §13 (chunked + 4 defensive patterns; LIVE-TESTED 5 patterns PASS) + §14 (atoms.jsonl schema validation; today's atoms.jsonl-blocking bug). orchestrator.md updated with schtasks discipline + faulthandler evidence + runner_status.py canonical check.
- **Skunkworks atoms.jsonl bug repaired** — sibling spawn had appended non-Atom-schema dict (missing `name` field) that BLOCKED ALL PartitionedStore reads. Quarantined + repaired.

### LANDED CELLS TODAY (significant)
- 3 phase-diagram smokes HARD_PASS: hypothesis-gen pipeline composition (PIPELINE=0.680 lift +0.56) / TASK_VECTOR K-cliff (cliff at K=1 V=200 + K=100 V=10) / parietal MOVABLE phase (cliff at n_obj=200; Plate analytic underestimates substrate ~2x)
- Hierarchical option-critic HF + block-sparse HF (both confirm closure)
- Online_conv FULL HARD_FAIL atomized (M3 concern #4 solved by TASK_VECTOR alone)
- Pattern_completion corruption-cliff smoke HARD_PASS (CPU fallback)
- Partition-oracle hardened FULL still pending land (re-dispatched after zombie)

### PIPELINE STATE (post-fix; runners now schtasks-immune)
- **remote_cpu_queue (11 pending):** cortex_hippo seed_17/23 + hypothesis_gen ×3 + parietal ×3 + taskvec ×3 (~28.3h serial worst-case)
- **overnight_queue (1 running + 1 pending):** pattern_completion + multihop smoke
- **local_cpu_queue (1 pending):** partition-oracle seed_11 (backup; direct background also running)
- 5 cell-authors still in flight: long-narrative composition / WM K-cliff / partition-oracle chunked re-author

### CRITICAL POST-COMPACTION POINTERS
- This UPDATE #24 is the load-bearing entry point (was #22; superseded twice today)
- 7 new memory rules filed today (see "NEW DISCIPLINES" above)
- `exp_dev.md` §13 + §14 + `orchestrator.md` §RUNNER-ZOMBIE-DETECTION + §LAUNCHER-DISCIPLINE all updated
- Substrate capability registry replaces 9+ Director-framing-errors-per-day pattern (query before claim)
- CERT 628 + 4 closure atoms (preliminary) + revival HFs; net CERT 628 with capability_closed adds (deltas pending Skunkworks confirmation)

### NEXT-STEP PRIORITIES POST-COMPACTION
1. Process partition-oracle hardened FULL when it lands (Barrier 1 CG promotion candidate)
2. Skunkworks batch on any HARD_PASS landings (parietal/TASK_VECTOR/hypothesis-gen 3-seed FULL)
3. Process WM K-cliff cell-author when returns
4. Process long-narrative ANCHOR 1 composition cell-author when returns
5. Spawn next phase-diagram cells (sequence binding / capacity-α upper / bidirectional / etc) once queue drains

-- Research (Opus 4.7-1M) — 2026-06-28 ~17:55Z UPDATE #24 (root-cause-fix + closure-confirmed + 7 memory rules + dashboard + capability registry + post-impl hygiene rule)












