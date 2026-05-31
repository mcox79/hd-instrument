# Orchestrator state snapshot for compaction (2026-05-31 ~11:05 ET)

Written for post-compaction continuity. Read this AFTER `notes/orchestrator_post_compaction_brief.md`.

## Where things stand

**Cap_map**: v292 just landed (commit `03e6317`, pushed). 7 new research-only rows added under NEW "Production positioning" category from 3 research routing requests processed via strategy_scribe. Portfolio 15+36 → 22+36.

**Session model**: 4-session architecture (orchestrator + research + testbed + cloud) established 2026-05-31. Charter at `notes/session_architecture_v1_2026-05-31.md`. Synchronization protocol at `notes/session_synchronization_v1.md`. Research and testbed sessions active and producing. Cloud session not yet activated but cloud infrastructure code shipped + first Lambda canary ran end-to-end this morning.

**Big findings of last 24h** (in cap_map v290-v292):
- **Modern Hopfield activation row 🟢 0.75-0.88** (T3 N=16384 + C1 N=16384 4N confirmed; G6 cross-codebook in flight on GPU; C9 ceiling extension in flight on CPU)
- **Path D production-default with no ceiling in 16N×depth=50** (U1 HARD_PASS)
- **Adversarial vulnerabilities**: codebook-collision 100% breach + edit-semantics 99.4% breach (U2 HARD_FAIL). Regulated-industry deployment blocker. D1 query-margin-gate smoke in flight to test priority defense.
- **COW infeasible** (U3); research drilled and recommends M1+M2 log-structured store as primary alternative (2x mem-amp vs U3's 10x)
- **First real Lambda experiment ran end-to-end** (testbed delivery, 10:00 ET)

## Queue state at compaction

**GPU**: V2 24h sustained_workload still running (started 2026-05-30T21:11:08, ~10h remaining). 15 anchors pending behind it (G1-G4 + G5-G12 minus G11 + G13a + G13b_p1/p2/p3). The GPU runner is NOT actively running parallel — V2 holds the slot.

**CPU**: substrate_state_compression_v1_n4096 running (started 10:58:40 after stuck-runner cleanup). 5 pending behind it:
1. edit_audit_trail_refinement_v1_n4096
2. substrate_operation_cost_modeling_v1_n4096
3. path_d_cpu_latency_profiling_v1_n4096
4. **modern_hopfield_cpu_extended_v9_n16384** (BIG: extends T3+C1 finding past 4N ceiling)
5. **query_margin_gate_smoke_v1_n4096** (D1 defense candidate test)

## Open issue: multi_hop_caching_baseline stall

The CPU anchor `multi_hop_caching_baseline_v1_n4096` stalled at FULL config (passed `--self-test` in 6.9s but hung in production mode with no CPU work after 10+ min). Killed and marked failed; 5 `_reship` duplicate entries also canceled to clean queue. Filed research routing for investigation (see `notes/strategy_request_to_research_multi_hop_caching_stall_investigation_2026-05-31.md`).

## Operational lessons saved as memory this session

- `feedback_powershell_queue_json_bom.md` — never use Set-Content for queue.json; force UTF-8 without BOM
- `feedback_runner_schtask_path_drift.md` — schtask Execute paths pointed at root-level .bat but launchers are at `tools/orchestrator/`; both schtasks fixed 2026-05-31
- `feedback_research_synthesis_external_discussion_cycle.md` — R1 workflow for user-shared external Claude discussions
- `project_multi_session_architecture.md` — 4-session model + ownership rules

## Cross-session communications active

Three other sessions writing to `data/orchestrator_status_log.jsonl`. To check recent activity post-compaction:

```python
python -c "
import json
from pathlib import Path
log = Path('d:/AI/hd-instrument/data/orchestrator_status_log.jsonl')
lines = log.read_text(encoding='utf-8', errors='replace').splitlines()
from collections import defaultdict
by_source = defaultdict(list)
for ln in lines[-100:]:
    try:
        e = json.loads(ln)
        src = e.get('source', 'orchestrator')
        by_source[src].append((e.get('ts','?')[:19], e.get('importance','?'), (e.get('plain_language') or '?')[:120]))
    except: pass
for src in ['research', 'testbed', 'cloud']:
    if src in by_source:
        print(f'=== {src} ===')
        for ts, imp, pl in by_source[src][-5:]:
            print(f'  {ts} [{imp}] {pl}')
"
```

## Pending decisions for orchestrator

From strategy_scribe v292 return (top-3):
1. **GPU resource for PP-8 deep-integration**: 8GB-local vs 24GB-local-4090 vs cloud-H100-80GB (~$200-400). Highest-leverage decision; determines P_deflated (0.25-0.30 vs 0.40-0.45) and base-LM (Phi-3-mini-4bit vs fp16). User input needed.
2. **M2 smoke dispatch timing**: ~30 min CPU laptop test for log-structured store mechanism. Gates U3-rehab + KF-2 + PP-3. Recommended AFTER current G5/G6 modern-Hopfield batch lands.
3. **Smaller-drill sequencing**: PP-5 latency budget + PP-2 storage efficiency + PP-3 audit-rotation FIRST (small drills, ~1-2 weeks each) before PP-8 Week-1 feasibility smoke.

Plus a recommended cross-framework probe and PP-7 (multi-substrate composition) re-anchoring drill.

## What orchestrator should NOT touch (other sessions' domains)

The following appear as "modified" in my git status but are owned by other sessions:
- `tools/cloud/*` — testbed
- `tools/orchestrator/heartbeat_watchdog.py` — testbed (dashboard expansion)
- `tools/orchestrator/remote_state_emitter.py` — testbed (multi-session monitoring)
- `tools/dashboard/*` (if modified) — testbed
- `notes/research_*.md` — research

If they show as modified locally without my changes, they're likely from another session's commits that haven't synced via pull-rebase (or I have uncommitted local changes I should review).

## Inbox status

All `strategy_request_to_strategy_*2026-05-31.md` files processed and moved to `notes/routed_completed/`. Inbox clean.

Active routing files outside orchestrator inbox (for awareness):
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` — research → testbed handoff (testbed sees it, not me)
- Research-side: see `notes/research_decisions_2026-05-31.md` for what they're working on

## Action queue after compaction

1. Watch CPU queue drain (5 substantive anchors after substrate_state_compression)
2. Process verdicts as they land (especially C9 + D1 + G5-G12 when GPU slot frees)
3. Surface user decisions needed: GPU resource for PP-8, M2 smoke timing, smaller-drill sequencing
4. Process inbound routing files from research/testbed
