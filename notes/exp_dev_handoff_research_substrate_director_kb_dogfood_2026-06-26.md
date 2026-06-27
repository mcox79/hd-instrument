# exp_dev hand-off — research: SUBSTRATE-AS-DIRECTOR-KB (eat-our-own-dogfood; no-lock-in architecture)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26 — Director's context-window + compaction-fragility is the bottleneck on multi-turn research coherence. Substrate has chain-grade primitives for exactly this storage problem (KG ingest ch_584/585/588 + multi-hop ch_588 + SEMANTIC concept learner just chain-grade today + refuse-gate ch_V_REL=256). We're not eating our own dogfood.

**USER constraint (load-bearing):** "Make sure we're not locking ourselves into a particular architecture that will be hard to correct should we need to." Architecture below is built around NO-LOCK-IN principles. Each is enumerated explicitly so cell-author can preserve them.

## Pause state

Check `data/orchestrator_paused.flag`. If paused, file this hand-off, do NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchor pointers only. exp_dev authors cells.

## No-lock-in architecture principles (USER CONSTRAINT; mandatory)

These principles MUST be preserved in the cell design. If exp_dev's design violates any, route back to research before shipping:

1. **Source-of-truth stays in the filesystem.** `notes/`, `memory/`, `data/*/metrics.json`, `data/cert_*` remain the canonical store. Substrate is a CACHE/INDEX over them, NOT the authoritative record. Director can always grep raw files if substrate is wrong, broken, or stale.

2. **Substrate-KB is wipe-and-rebuild safe.** Any time we change schema/encoder/binding, we wipe the substrate-KB-W matrix and re-ingest from the unchanged filesystem source. No data loss from cutover. The ingest pipeline is deterministic given the source.

3. **Versioned ingest pipeline.** `substrate_director_kb_ingest_vN.py` — multiple versions can coexist as separate atoms (atom-tag `kb_version=v1`). Query layer can choose which version to read or compare across. No need to "migrate" old atoms; just ingest new version alongside.

4. **Schema-as-config, not hardcoded.** Relations + entity types + atom tags defined in `config/director_kb_schema.json`. Adding a new relation type = config edit + selective re-ingest, not code change.

5. **Multiple parallel encodings supported.** Each atom carries its encoder tag (`encoder=char_trigram_v1` vs `encoder=semantic_concept_learner_v1` vs `encoder=word2vec_substrate_bind_v1`). Query can choose encoder OR query all and disjoin results. Encoder choice is not locked.

6. **Read-only substrate from Director's perspective.** Director NEVER directly writes to the KB W matrix. Director's role: ingest-trigger (declarative; "re-ingest this file") + query. Writes are owned by the ingest cell. Prevents Director context corruption from corrupting the long-term store.

7. **Graceful-degradation fallback.** Query layer returns `(answer, confidence, atoms_consulted)`. If confidence < tau, Director MUST fall back to filesystem grep — explicitly, with the refusal logged. The substrate is not the only path; it's the FIRST path.

8. **Modular separation: ingest / query / maintenance / eviction.** Four separate small cells, not one monolith. Each replaceable. If query primitive changes, ingest doesn't. If schema changes, query interface signature preserved.

9. **Compute envelope cap.** Ingest of full notes/ + memory/ + cert_ledger snapshot must run in ≤ 15 min on local_cpu_queue. If it exceeds, we shard — but never let ingest become the bottleneck that prevents iteration on Director-KB itself.

10. **Self-eviction policy.** Stale atoms (e.g., USER feedback later contradicted) get tagged superseded_by=<atom_id>, NOT deleted. Query layer filters out superseded by default; debug mode can include them. Never lose history.

11. **Use existing chain-grade primitives ONLY for ingest/query.** No novel-synthesis primitives. The KB cell is a SCAFFOLDING build, not a research experiment. Substrate-as-tool, not substrate-as-test. Composes on: KG ingest primitive (chain-grade) + multi-hop primitive (chain-grade) + cleanup/refuse-gate (chain-grade) + SEMANTIC concept learner (chain-grade today).

12. **Architecture spec lives in source-controlled config + readme**, not just in the cell code. Future Director can re-derive what schema looks like by reading `config/director_kb_schema.json` + `docs/director_kb_arch.md` (cell-author authors).

## Anchor candidates (rank-ordered; each modular per principle 8)

### ANCHOR 1 (TOP — load-bearing): substrate_director_kb_ingest_v1

- **Anchor pointer:** new cell `experiments/exp_substrate_director_kb_ingest_v1.py` + new tooling `tools/director_kb_ingest.py` + new config `config/director_kb_schema.json`
- **Substrate-product reading:** walks `notes/*.md` + `memory/*.md` + `data/*/metrics.json` + `data/cert_*` + `MEMORY.md`; extracts typed triples per schema config; ingests via chain-grade KG primitive into dedicated KB W matrix (`data/substrate_director_kb_v1/`); per-atom tags include source-path, ingest-version, encoder, schema-version, ingest-timestamp.
- **Triple schema (v1; in config, not hardcoded):** `(source_file, type, target)` where types include: VERDICT_OF, AUTHOR_OF, USER_DIRECTIVE, SUPERSEDES, REFERENCES, MECHANISM_OF, ANCHOR_FOR, HARD_PASS, HARD_FAIL, MIDDLE_BAND, CHAIN_GRADE, DATE_FILED, COMPOSES_WITH.
- **Tier hint:** TOOLING cell (not chain-grade-candidate); success criterion is OPERATIONAL not CERT-bands.
- **Arms (3 mandatory):**
  - ARM_INGEST_NOTES_ONLY (sanity: walk + extract + ingest ~500 recent notes; verify count + tag-correctness)
  - ARM_INGEST_FULL (notes + memory + metrics; verify atom count matches source line count + no encoder errors)
  - ARM_REINGEST_DETERMINISTIC (run ingest twice from same source; verify identical atom set — deterministic guarantee load-bearing for wipe-and-rebuild)
- **Pre-reg success criteria:** ingest completes in ≤ 15 min on local_cpu_queue at current corpus size (~4000 notes + ~250 memory files + ~600 metrics); deterministic across re-runs (atom_set identity); covers ≥ 95% of source files (rejects must be logged with reason); schema config externalized (changing schema = config edit only)
- **Pre-reg failure criteria:** ingest exceeds 30 min (re-shard); ingest non-deterministic across runs (mechanism bug); schema can't be changed without code edits (lock-in violation — REJECT cell)
- **Cost:** ~6-8 hr build + 15-min smoke ingest + 15-min full ingest; local_cpu_queue
- **Source:** USER request 2026-06-26 + chain-grade primitive scaffolding

### ANCHOR 2 (decisive): substrate_director_kb_query_v1

- **Anchor pointer:** new cell + new tooling `tools/director_kb_query.py` (CLI Director uses on every turn-start)
- **Substrate-product reading:** natural-language question → encode via configured encoder → multi-hop retrieval over KB W → cleanup top-K → refuse-gate on energy gap → return `(top_k_atoms, confidence, paths_consulted, fallback_recommendation)`. Composes ENTIRELY on chain-grade primitives.
- **Query API contract (versioned):** `query(question: str, schema_version: str = "v1", encoder: str = "default", k: int = 5, confidence_floor: float = 0.5) → QueryResult`
- **Tier hint:** TOOLING cell.
- **Arms (4 mandatory):**
  - ARM_KNOWN_QUERY_BASELINE (queries Director has answered correctly recently from grep; verify KB returns same answer with high confidence — ~30 hand-picked queries from this session)
  - ARM_UNKNOWN_QUERY_REFUSE (queries with no source data; verify KB refuses rather than confabulates — load-bearing for trust)
  - ARM_AMBIGUOUS_QUERY_TOPK (queries with multiple valid answers; verify KB returns top-K disjunctively per ANCHOR 3 of first-wave handoff)
  - ARM_SUPERSEDED_FILTER (queries about a fact that got superseded; verify KB returns current fact by default + can return history in debug mode)
- **Pre-reg success criteria:** known-query recall ≥ 0.85; unknown-query refuse-rate ≥ 0.90; ambiguous-query disjunctive recall@K=2 ≥ 0.80; superseded filter correct ≥ 0.95
- **Pre-reg failure criteria:** known-query recall < 0.60 (KB worse than grep — KB rejected as tool); refuse-rate < 0.50 (confabulation — KB rejected as trustworthy source)
- **Cost:** ~4-6 hr build + 1-hr eval; local_cpu_queue
- **Dependency:** ANCHOR 1 must HARD_PASS first (ingest must produce useable KB)

### ANCHOR 3 (continuous): substrate_director_kb_continuous_ingest_v1

- **Anchor pointer:** new cell + integration with existing notes-monitor + scheduled-task for metrics ingestion
- **Substrate-product reading:** on every new note filed (notes-monitor fires) AND every new metrics.json landed (recent_landings.jsonl tail), trigger incremental ingest of that single file via ANCHOR 1's pipeline. KB stays current within minutes of source.
- **Tier hint:** TOOLING/INFRA cell.
- **Arms (2 mandatory):**
  - ARM_FILE_DROP_LATENCY (drop a synthetic note in notes/; measure time-to-queryable)
  - ARM_BATCH_BACKPRESSURE (drop 50 notes in rapid succession; verify ingest queues correctly + no atoms lost)
- **Pre-reg success criteria:** single-file ingest latency ≤ 60 sec; backpressure handles 50 notes/min without data loss
- **Cost:** ~3-4 hr build; runs as scheduled-task / monitor-hook (zero-incremental compute)
- **Dependency:** ANCHORS 1 + 2 HARD_PASS first

### ANCHOR 4 (maintenance): substrate_director_kb_supersede_compaction_v1

- **Anchor pointer:** new cell + tooling
- **Substrate-product reading:** weekly maintenance run: scan for atom pairs where a newer atom semantically supersedes an older (e.g., USER feedback v2 supersedes USER feedback v1); tag older with `superseded_by=<atom_id>`. Query layer filters superseded by default. Atoms are tagged not deleted (principle 10 — never lose history). Also: detect orphan atoms (source file deleted) and tag with `orphan=true` for review.
- **Tier hint:** TOOLING/MAINTENANCE cell.
- **Arms (2 mandatory):**
  - ARM_SUPERSEDE_DETECTION (synthetic test: ingest USER directive v1, then v2 that revokes v1; verify v1 tagged superseded_by=v2 + query returns v2 by default)
  - ARM_ORPHAN_DETECTION (synthetic test: ingest from file, delete file from source, run maintenance; verify atom tagged orphan)
- **Pre-reg success criteria:** supersede detection F1 ≥ 0.80; orphan detection precision = 1.000 (no false-orphans — those would be lost history)
- **Cost:** ~4-5 hr build; runs weekly on scheduled-task
- **Dependency:** ANCHORS 1 + 2 HARD_PASS first

## Recommended dispatch sequence

**Wave 0 (foundational; serial):**
- ANCHOR 1 ingest (~6-8 hr build + smoke; local_cpu)

**Wave 1 (after ANCHOR 1 verdict):**
- ANCHOR 2 query (~4-6 hr build + eval; local_cpu)

**Wave 2 (after ANCHORS 1+2 verdict):**
- ANCHOR 3 continuous-ingest (~3-4 hr build)
- ANCHOR 4 supersede-compaction (~4-5 hr build) — parallel with ANCHOR 3

Total build time: ~17-23 hr CPU. End state: Director's first action on every turn becomes `python tools/director_kb_query.py "<question>"` instead of grep-then-grep-then-read.

## Director-side workflow (post-build)

After all 4 anchors HARD_PASS, my workflow changes:

1. **Turn start:** `python tools/director_kb_query.py "what's the current state of cortex content-extraction work?"` → KB returns top-K atoms with paths + confidence + history. Less context burn than re-reading notes.
2. **Before any synthesis:** query KB for "have I addressed X?" — catches the kind of overlooks USER caught today (multi-bank already chain-grade, PC primitive already exists).
3. **After every USER directive:** explicit ingest trigger ensures KB has the latest standing rule before next turn.
4. **On compaction:** zero loss — KB is on disk, query interface unchanged.
5. **On disagreement:** if KB says one thing and filesystem says another, filesystem wins (principle 1). KB gets re-ingested to fix the drift.

## Context pointers

- USER request: this conversation 2026-06-26
- Chain-grade primitives this composes on:
  - KG ingest (FB15k-237 ch_584; ConceptNet ch_585; HotpotQA ch_588)
  - Multi-hop (depth-15 at 0.808 cv≤0.024 today — `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`)
  - SEMANTIC concept learner (`data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json`)
  - Refuse-gate (V_REL=256 chain-grade)
  - TWO_TIER architecture (`data/exp_gap4_two_tier_generational_W_v1/metrics.json`) — natural fit for fast-recent-ingest + slow-consolidated KB
- Prior self-mapping attempts (read for what went wrong; do NOT repeat):
  - `data/exp_substrate_self_map_v2*` HARD_FAIL series (lacked proper Director-query frontend; tried to map state without an interface)
- USER no-lock-in constraint: this conversation 2026-06-26 verbatim "Make sure we're not locking ourselves into a particular architecture that will be hard to correct should we need to."

## Contract

- ALL 12 no-lock-in principles must be preserved. If cell design violates any, route back to research.
- Schema config lives at `config/director_kb_schema.json` — version-controlled.
- Architecture doc lives at `docs/director_kb_arch.md` — cell-author authors as part of ANCHOR 1.
- Ingest cell + query cell + monitor cell + maintenance cell are SEPARATE modules (principle 8).
- Filesystem is source-of-truth; substrate-KB is index (principle 1, 2).
- Director reads only; ingest cell writes (principle 6).
- Graceful degradation to filesystem grep on low-confidence (principle 7).
- USER directive memory ingestion priority: ALL files in `memory/` get ingested with priority tag (USER_DIRECTIVE relation type) — these are load-bearing across compactions.
- Pre-flight Fix #26 verify-the-referent before dispatching each anchor.

## Autonomy declaration

exp_dev owns: cell authoring within research-note guidance; smoke gates; queue routing; modular cell-split decisions (could split ANCHOR 1 into ingest + schema-loader + tag-extractor sub-cells if cleaner); encoder choice from existing chain-grade options.

exp_dev does NOT own: relaxing any of the 12 no-lock-in principles; using substrate as primary store (filesystem stays canonical); skipping the deterministic-reingest arm in ANCHOR 1 (load-bearing for wipe-and-rebuild safety); skipping refuse-arm in ANCHOR 2 (load-bearing for trust); making ingest write irreversibly (must support wipe-and-rebuild).

USER green-lit this build 2026-06-26 with explicit no-lock-in constraint. No further research approval needed for Wave 0 dispatch.

---

-- Research (Opus 4.7-1M)
