# Session architecture v1 (2026-05-31)

Authoritative SSoT for how the project's parallel Claude Code sessions coordinate. Read this BEFORE making changes that touch shared state.

## The four sessions

| Session | Mission | Primary owns | Reads (no writes) |
|---|---|---|---|
| **Orchestrator** | Experiment dispatch, verdict handling, cap_map writes, queue management, pause flag | `experiments/`, `data/`, `notes/exp_dev_*`, `notes/strategy_decisions_*`, `notes/visibility_decisions_*`, cap_map | research notes, testbed notes |
| **Research** | Substrate-physics drilling, theoretical analysis, literature scans, hypothesis generation, cross-domain probes | `notes/research_*`, `notes/research_decisions_*` | cap_map, experiment metrics, all decision logs |
| **Testbed** | Production engineering (Pattern B integration, multi-tenant, hashed codebook, public library, compliance documentation) | `testbed/`, `hdlab_service/`, `notes/testbed_*` | cap_map, experiment metrics, research notes |
| **Cloud** (later) | Cloud-GPU dispatch with cost discipline; activated after Phase 2 validation lands | `cloud/`, `notes/cloud_*`, cost tracking data | cap_map, experiment metrics |

## Single-sources-of-truth all four read

1. **Git** — code, preregs, notes, decision logs (append-only). Every session pulls before substantive work; commits with `git pull --rebase` if needed.
2. **Cap_map** (`notes/substrate_capability_map.md`) — strategic findings. **Orchestrator writes; others read.**
3. **Dashboard** (`data/orchestrator_status_log.jsonl`) — runtime state. All sessions write `log_event()` entries with `source=<session_name>`.
4. **Memory** (`C:\Users\marsh\.claude\projects\d--AI\memory\`) — behavioral feedback persisting across sessions and across days.

## Conflict prevention rules

### Cap_map write discipline
**Orchestrator session writes cap_map exclusively.** Research and testbed sessions deliver findings via routing files (`notes/strategy_request_to_strategy_*.md`); orchestrator decides cap_map impact.

Rationale: cap_map is the strategic state. Concurrent writes from multiple sessions would race. One writer + many readers is the standard MLOps pattern.

### Directory ownership (minimize git conflicts)
- Orchestrator never writes `notes/research_*` or `notes/testbed_*`
- Research never writes `experiments/`, `data/`, cap_map, or `notes/exp_dev_*`
- Testbed never writes `experiments/`, cap_map, or `notes/research_*`
- Cloud never writes `experiments/` (uses `cloud/` mirror); reads cap_map for activation gates

### Append-only decision logs
Each session writes to its own decision log:
- `notes/strategy_decisions_<date>.md` (orchestrator)
- `notes/research_decisions_<date>.md` (research)
- `notes/testbed_decisions_<date>.md` (testbed)
- `notes/cloud_decisions_<date>.md` (cloud, when active)

Append-only survives concurrent edits; no merge conflicts possible.

### Routing files for cross-session work transfer

Cross-session work goes through routing files in `notes/`:

- `strategy_request_to_strategy_<topic>_<date>.md` — research/testbed asks orchestrator for a cap_map decision
- `strategy_request_to_exp_dev_<topic>_<date>.md` — research/testbed asks orchestrator to dispatch an experiment
- `strategy_request_to_research_<topic>_<date>.md` — orchestrator/testbed asks research for a drill
- `testbed_handoff_<topic>_<date>.md` — orchestrator hands work to testbed
- `cloud_handoff_<topic>_<date>.md` — orchestrator hands cloud-eligible work to cloud session

The receiving session polls its inbox at session start.

### Pause flag halts everyone
`data/orchestrator_paused.flag` halts experiment dispatch across orchestrator and cloud sessions. Research and testbed are unaffected (they don't dispatch experiments).

### Memory writes
Memory files at `C:\Users\marsh\.claude\projects\d--AI\memory\` are shared. Each session can write feedback memories with a `source: <session>` field in frontmatter when the feedback is session-specific. Cross-session feedback (e.g., "PowerShell BOM hazard") is shared.

## Status_log contract

Every session writes `log_event()` entries to `data/orchestrator_status_log.jsonl` (gitignored — local-only). Required fields:

```python
log_event(
  '<event_kind>',
  '<technical summary>',
  plain_language='<1-2 sentences for a non-expert>',
  importance='<CRITICAL|HIGH|MEDIUM|LOW>',
  source='orchestrator|research|testbed|cloud',  # NEW field
)
```

The For-You dashboard tab filters by source. Default view shows all four; per-source tabs available.

## Cloud session activation gate

Cloud session activates only when ALL of the following are true:

- [x] Phase 1 validation: V1 modern_hopfield_pipeline_validation HARD_PASS at N=2048+4096 (DONE)
- [x] Phase 1 substrate-physics: T3 N=16384 max_M>=N (DONE)
- [ ] Phase 2 validation: G5/G6 modern_hopfield at N=8192 HARD_PASS (in flight)
- [ ] V2 24h sustained workload HARD_PASS (in flight, ~17h remaining)
- [ ] Dashboard expansion: 3rd runner panel + cost tracker + budget caps (testbed engineering, ~1-2 days)
- [ ] Lambda Labs credentials configured + SSH bootstrap automation tested
- [ ] Validation canary dispatched: V1 re-run on Lambda matches local V1 HARD_PASS

Until all checks pass, cloud work stays in orchestrator session as a "third runner" with manual cost discipline.

## Dashboard expansion required for multi-session SSoT

Currently the dashboard reads `data/remote_state_cache.json` (1 environment: marsh@home). Multi-session needs:

1. **Per-runner panels**: marsh@home GPU, marsh@home CPU, Lambda GPU (when active)
2. **Per-session activity indicators**: research-in-flight, testbed-in-flight (via heartbeat files written by those sessions)
3. **Per-stream queue depth**: experiments_queue_depth, testbed_queue_depth, cloud_queue_depth
4. **Cost tracker** (cloud especially): $/hr active, $ accumulated today, $ budget remaining
5. **For-You feed with source filter**: tabs for All / Orchestrator / Research / Testbed / Cloud
6. **Cap_map version with last-bumped-by**: shows which session's work triggered the latest bump

Testbed engineering estimate: ~1-2 days for items 1-5, ~half day for #6.

## Session kickoff protocol

When a new session starts (or resumes after compaction), the FIRST action is to read this file and the relevant kickoff prompt for its role. Each session's kickoff document is at `notes/session_kickoff_<role>_v1.md`.
