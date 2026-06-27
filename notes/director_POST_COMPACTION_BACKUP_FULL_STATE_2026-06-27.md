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

**CERT 616** (per Skunkworks batch 4 A5 POST verification; batches 3+4 net +0 chain-grade; +9 atoms total of which 1 chain-grade ultrametric clustering + various MM/META; A5 PRE repaired 9 malformed atoms from prior batches 2+3 = preserved cert-intent without count change).

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

## SKUNKWORKS BATCH 5 OUTCOMES (landed 2026-06-27 ~05:10 PDT; commit 6895100e)

- ANCHOR 3 FULL → **PROVEN_BOUND** (not chain-grade): rec_clst=rec_unclst=1.000 saturates metric cap; USER_DIRECTIVE vacuously satisfied (n_UD=0). RC paths: (1) re-run with n_UD>0 mix; (2) scale n_atoms≥10k to break 1.000 cap. Direct chain-grade promotion path identified.
- Edge-importance v2 high-alpha → MIDDLE_BAND confirmed = effectively HONEST-NEGATIVE for PageRank variant per math+brain drill. v3 pivot validated by cert-owner.
- Wave 4 content-chunk smoke → MEASURED_MECHANISM (infra HARD_PASS only). **Banana/elephant content-vs-filename tripwire NOT in metrics.json** — Skunkworks searched all 3 arm dirs; no banana/elephant strings surfaced. v2-content-KB-not-just-index claim is UNVERIFIED OFF DATA until tripwire is reproducibly logged. **Holds substrate-first ritual flip even longer.**
- CERT delta +0; 3 atoms added; 3 ledger rows; commit 6895100e

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
