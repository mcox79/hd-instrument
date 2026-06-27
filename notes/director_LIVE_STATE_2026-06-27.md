# DIRECTOR LIVE STATE SNAPSHOT 2026-06-27

**Updated:** 2026-06-27 ~05:25 PDT (rewrite on todo changes)
**Purpose:** capture granular CURRENT IN-FLIGHT + TODO state. BACKUP doc has high-level state; this has the fluid in-flight.

## CURRENT TODOS (truncate + rewrite on TodoWrite)

1. **[in-flight]** Orchestrator (ab6e0a86a825c21f9): commit 1b851af7 push + queue 3 cells (K=8192 / capacity_sweep / ANCHOR 5 FULL); after, commit+push 4 new files + queue 2 more (ANCHOR 1 v2 + edge-imp v3) per SendMessage
2. **[in-flight]** exp_dev (a7d9e55fa8e358d47): ANCHOR 3 v2 chain-grade promotion (RC-1+RC-2: USER_DIRECTIVE mix + n_atoms>=10k) + Wave 4 KB v2 tripwire surfacing patch
3. **[done]** Skunkworks batch 5 VET: ANCHOR 3 PROVEN_BOUND / edge-imp v2 MIDDLE_BAND confirmed / Wave 4 MEASURED_MECHANISM (tripwire unsurfaced) — commit 6895100e; CERT 616 stable; 3 atoms + 3 ledger rows
4. **[done]** exp_dev 3-cell author (ab1a8c04ff673f272): K=8192 3-seed + capacity_sweep higher-alpha + ANCHOR 5 FULL dispatch — commit 1b851af7 (5 files)
5. **[done]** exp_dev ANCHOR 1 v2 + edge-imp v3 author (acb2d59133693986f): 4 files uncommitted; in orchestrator queue via SendMessage
6. **[done]** ANCHOR 1 v1 HARD_FAIL diagnosis: mechanism PASSED (routing_acc=1.0, leak=0.0); over-strict criterion + corpus cross-cutting labels
7. **[done]** Edge-importance 2x drill: PageRank categorically wrong; pivot to retrieval-trace × ultrametric-coreness
8. **[done]** Codified cardinality_ok + META_RULE_J/K/L/M SCHEMA-VET checklist in exp_dev.md
9. **[done]** Codified Atom roundtrip self-test in skunkworks.md (batch 4 flag-back)
10. **[done]** NO EXPERIMENTS LOCAL directive: memory + index + exp_dev.md + live-agent message
11. **[done]** BACKUP file 2026-06-27 written
12. **[pending]** ANCHOR 5 dual-store FULL verdict (USER vetting gate; ≥95% match_rate for Wave 3 promotion)
13. **[pending]** K=8192 3-seed harvest verdict (chain-grade evidence for K=8192 ceiling)
14. **[pending]** capacity_sweep higher-alpha verdict (capacity story extension)
15. **[pending]** ANCHOR 1 v2 verdict (partition mechanism vindication)
16. **[pending]** Edge-importance v3 verdict (retrieval-trace × ultrametric composition)
17. **[pending]** ANCHOR 3 v2 chain-grade promotion verdict (USER_DIRECTIVE mix + n>=10k cap-breaking)
18. **[pending]** Wave 4 KB v2 tripwire surfaced verdict
19. **[pending]** Wave 4 substrate-vs-MD head-to-head cell (needs Wave 4 tripwire + FULL ingest first)
20. **[pending]** Wave 3 ANCHOR 2 TWO_TIER promotion (gated on edge-importance v3 chain-grade)
21. **[pending]** Math + science ingest extractors (ProofWiki / OEIS / PubMed / arXiv)
22. **[pending]** Wave 2 compositional understanding cells audit vs Stage 2 specs
23. **[pending]** Fix #26 tooling-gap: predispatch_check check local landings
24. **[pending]** 13 RC follow-up items from prior Skunkworks batch 3
25. **[pending]** Standalone partition-integrity scheduled task (Skunkworks batch 4 flag-back #2 defense-in-depth)

## ACTIVE SPAWNS IN FLIGHT

- **ab6e0a86a825c21f9** — Orchestrator: 5 dispatches total (3 from commit 1b851af7 + 2 via SendMessage for ANCHOR 1 v2 + edge-imp v3)
- **a7d9e55fa8e358d47** — exp_dev: ANCHOR 3 v2 chain-grade promotion + Wave 4 tripwire surfacing

## CELLS QUEUED ON REMOTE (when orchestrator finishes)

- `phase_diagram_wm_multibank_K_8192_3seed_harvest_v1` → overnight_queue GPU (1800s timeout)
- `phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1` → overnight_queue GPU (1800s timeout)
- `kb_dual_store_audit_v1` (FULL) → remote_cpu_queue (5400s timeout)
- `kb_partition_by_source_class_v2` → remote_cpu_queue (600s timeout)
- `edge_importance_retrieval_trace_x_ultrametric_coreness_v3` → remote_cpu_queue (14400s timeout)

## RECENT KEY DECISIONS (most recent first)

- 2026-06-27 ~05:25: ANCHOR 3 v2 + Wave 4 tripwire spawned (proactive Skunkworks flag-back follow-up)
- 2026-06-27 ~05:15: ANCHOR 1 v2 + edge-imp v3 authored; SendMessage to orchestrator for commit+push+queue_add
- 2026-06-27 ~05:10: Skunkworks batch 5 done; ANCHOR 3 PROVEN_BOUND not chain-grade; Wave 4 tripwire unsurfaced flagged
- 2026-06-27 ~04:55: BACKUP 2026-06-27 written; supersedes 2026-06-26 BACKUP
- 2026-06-27 ~04:50: NO EXPERIMENTS LOCAL directive codified (memory + MEMORY.md + exp_dev.md + live message)
- 2026-06-27 ~04:45: 4 parallel spawns (Skunkworks/ANCHOR 1 diagnosis/edge-imp drill/3-cell remote author)
- 2026-06-27 ~04:30: USER returned, asked to catch up; read all context docs

## OPEN QUESTIONS / DECISIONS PENDING USER

- (none currently; auto mode active)

## WHERE THIS FITS

- BACKUP `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` = load-bearing self-contained recovery doc
- DIGEST 2026-06-26 still applicable (mostly; substrate-KB v1 vs v2 story has nuance per Skunkworks)
- COMMANDS 2026-06-26 still applicable (commands unchanged)
- THIS file = granular IN-FLIGHT snapshot; updated more frequently than BACKUP

---

-- Research (Opus 4.7-1M)
