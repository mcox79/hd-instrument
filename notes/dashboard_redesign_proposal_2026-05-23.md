# Dashboard Redesign Proposal — 2026-05-23

Author: research sub-agent
Brief from: feedback-orchestrator-status-visibility, feedback-design-space-and-audit-cadence

---

## (a) HEADLINE — top design principles

**Principle 1 — "Now / Next / Lately / Known" as the spine of the UI.**
The user's actual question is never "show me everything," it is one of four:
1. **NOW**: what is the system doing this second? (orchestrator + runners)
2. **NEXT**: what is queued, what sub-agents are in-flight, what's about to happen?
3. **LATELY**: what just happened — verdicts, sub-agent returns, cap-map version bumps, audits
4. **KNOWN**: what does the substrate currently *know it can do* — the capability map as a live truth surface

Every panel must answer exactly one of those four. Anything that doesn't, gets cut. This is the Stephen Few discipline ("a visual display of the most important information needed to achieve one or more objectives ... monitored at a glance") applied to a *single-user research operator* rather than a business KPI dashboard. ([Few, *Information Dashboard Design*](https://www.amazon.com/Information-Dashboard-Design-At-Glance/dp/1938377001))

**Principle 2 — One status feed is the spine, everything else is context.**
The orchestrator already writes `data/orchestrator_status_log.jsonl`. That file IS the user's status update. The dashboard's primary job is to make that file readable at a glance and to surface the *structured* fields (event_kind, sub_agents dispatched, outcome) as chips/badges rather than prose. This mirrors the activity-feed pattern used in W&B, MLflow, Hatica, and Datadog event streams — the *event stream is the dashboard*, panels are filtered/derived views of it. ([Grafana state-timeline](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/state-timeline/), [W&B experiment tracking](https://wandb.ai/site/experiment-tracking/), [Hatica activity log](https://www.hatica.io/docs/dashboards/catalog/activity-log/))

Corollary: the current "Events" ribbon at the bottom of Live should be promoted to *the headline strip at the top* and the orchestrator status log should be merged into it (not a separate panel). The user wants one place to read "what happened lately."

---

## (b) Tab structure proposal

| Tab | Keep / Drop / Add | Rationale |
|---|---|---|
| **Live** | KEEP, RESHAPE | This is the "Now + Next" tab — it answers the load-bearing question. Restructured below. |
| **Tests (194)** | KEEP, RENAME → "Experiments" | The 194-row table is useful as a deep dive but it's NOT the "what is happening now" surface — it's the "ledger." Demote from headline. |
| **Capability** | KEEP, REVAMP HARD | This is the "Known" tab. Today it just renders raw markdown. Replace with a tier-summary panel + drillable rows. |
| **Experiment** | DROP | User-confirmed dead. |
| **Status** | ADD (NEW) | Dedicated tab for the orchestrator status log + sub-agent dispatch timeline + audit results. This is what the user MISSES from the previous setup. |

Tab order should be: **Live → Status → Experiments → Capability**. Live is the home tab; Status is one click away; Experiments and Capability are the deep dives.

---

## (c) Per-tab content layout

### LIVE tab (revised — answers NOW + NEXT)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  HEADLINE BANNER  (always at top, full width, height ≈ 56px)              │
│  "v158 cap_map · 12✅ 6🟢 4🟡 17🔬 13❌ · GPU 84% · runners 2/2 alive"      │
│  + one-line "currently working on: " from latest status log entry         │
└───────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────┬─────────────────────────────────────────────┐
│  NOW RUNNING (left col)     │  ORCHESTRATOR STATUS STREAM (right col)     │
│  ─ gpu/overnight_queue/...  │  ─ tail of orchestrator_status_log.jsonl    │
│    [progress bar · ETA]     │    (12 most-recent entries, newest top)     │
│    cell 47/96 · 23m elapsed │  ─ each row = one icon + ts + chip + line: │
│  ─ cpu/remote_cpu_queue/... │    ✓ 12:28  VERDICT  crooks_noise_corrected│
│    [progress bar · ETA]     │      _pass FULL · cap1 SLA widens          │
│  ─ ad-hoc runs (if any)     │    ◐ 12:15  DISPATCH research:opus crooks  │
│  GPU%/mem mini-bar          │    ◑ 12:00  RETURN  research:sagawa-ueda  │
│                             │    ✎ 11:58  CAP_MAP v157 → v158            │
│                             │    ⚙ 11:40  HARD_GATE bet_A continual_edit │
│                             │  [filter by event_kind ▾]                  │
└─────────────────────────────┴─────────────────────────────────────────────┘
┌─────────────────────────────┬─────────────────────────────────────────────┐
│  QUEUE DEPTH (NEXT)         │  IN-FLIGHT / OPEN ROUTINGS (NEXT)           │
│  gpu  3 queued · 0 failed   │  Routings without delivery:                 │
│  cpu  7 queued · 2 failed   │  ─ exp_dev_to_queue_betA_M_init_v2 (open)  │
│  ─ next 5 in each queue:    │  ─ exp_dev_to_strategy_priority_B_deferral │
│    betA_5seed_v3            │  Sub-agents currently dispatched:           │
│    crooks_forensic_erase    │  ─ research:opus (post_v149_batch, 8m)     │
│    observability_v2_kovacs  │  ─ exp_dev:sonnet (idle 4m)                │
└─────────────────────────────┴─────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────────────────┐
│  RECENT VERDICTS (LATELY)  — chip row, scrolls horizontally                │
│  [✓ 12:28 crooks_noise_corrected_pass]  [✓ 12:28 streaming_noise_envelope_pass] │
│  [✗ 11:40 betA_continual_edit FAIL]  [✓ 10:53 BETA_M_INIT_OOM_INCONCLUSIVE] │
└───────────────────────────────────────────────────────────────────────────┘
```

State markers in the Status Stream column use a consistent icon legend (already partially defined in `EVENT_ICONS`):

| Icon | event_kind | Color |
|---|---|---|
| ✓ | verdict / experiment_done (positive) | green (var(--ok)) |
| ✗ | verdict / experiment_done (negative) | red (var(--err)) |
| ◐ | sub_agent_dispatched | violet (#b58fd9) |
| ◑ | sub_agent_returned | violet (#b58fd9) |
| ✎ | cap_map_committed / note_committed | dim |
| ⚙ | hard_gate / config_change | warn-yellow |
| ▶ | experiment_started | blue |
| • | observation / generic | info-blue |
| 🔬 | research_delivery | violet |
| 🛠 | migration / orchestrator_init | dim |

### STATUS tab (NEW — deep dive into the status log)

```
┌─────────────────────────────────────────────────────────────────┐
│  filters: [event_kind ▾]  [since 24h ▾]  [sub_agent ▾]  [grep] │
├─────────────────────────────────────────────────────────────────┤
│  TIMELINE (state-timeline style, last 24h)                      │
│   00:00 ──────────●─────●●──●────●───────●●──●─── 24:00         │
│         each ● = one status_log entry, colored by event_kind    │
├─────────────────────────────────────────────────────────────────┤
│  FULL FEED — one row per status_log entry                       │
│  ts        kind          summary               sub_agents  outc │
│  12:28:00  verdict       crooks_noise_corr…    [strategy] PASS │
│  12:15:00  dispatch      Sagawa-Ueda drill     [research]  —   │
│  ...                                                            │
│  (click row to expand: full JSON payload, link to source note)  │
├─────────────────────────────────────────────────────────────────┤
│  TODAY'S AUDIT (collapsible)                                    │
│  ─ Dropped items: 2 (from notes/audit_dropped_…2026-05-23.md)  │
│  ─ Stale 🔬 rows: 4 (older than 5 cycles)                       │
│  ─ Re-review candidates: 1                                      │
└─────────────────────────────────────────────────────────────────┘
```

The state-timeline pattern follows the Grafana state-timeline visualization: discrete events on a horizontal time axis with color encoding the state. ([Grafana state-timeline](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/state-timeline/))

### EXPERIMENTS tab (current Tests tab, renamed + lightly trimmed)

Keep the filter chips, keep the row format, keep the expand-for-log behavior. Two small additions:

1. Add a tiny "since cap_map vN" filter so the user can see "what's run since the last map version" — useful for tracking which experiments fed which cap_map bump.
2. The existing per-row "tier / research / status / verdict" badges are already good. Don't gold-plate.

### CAPABILITY tab (REVAMPED — answers KNOWN)

Replace the current "render the raw markdown of substrate_capability_map.md" approach with a **structured live tier table** at the top, with the markdown below as fallback / detail. Parse the cap_map's known sections.

```
┌───────────────────────────────────────────────────────────────────┐
│  v158 · committed 2026-05-23 12:28 · 49 experiments tracked       │
├───────────────────────────────────────────────────────────────────┤
│  TIER SUMMARY                                                     │
│  ✅ Validated         12  (memory primitives 3, R10 1, CL 3, ...) │
│  🟢 Want stronger      6                                          │
│  🟡 Inconclusive       4                                          │
│  🔬 Research-only     17                                          │
│  ⚪ Untested          12                                          │
│  ❌ Closed            13  [includes HARD-GATED: 1]                │
├───────────────────────────────────────────────────────────────────┤
│  ACTIVELY BEING EXPANDED  (probes/sub-agents touched in last 24h) │
│  ─ crooks_noise (Cap 1)  ✓ widened to tiered SLA today           │
│  ─ streaming envelope    ✓ noise-tolerant variant landed today    │
│  ─ betA M_init           🟡 OOM characterization complete         │
│  ─ continual_edit N≥16k  ⚙ hard-gated pending chunked-matmul     │
├───────────────────────────────────────────────────────────────────┤
│  HEADLINE CAPABILITIES (top 5 by tier + recency)                 │
│  [click any to jump to the corresponding markdown section]        │
│  ─ ✅ In-context learning via pool (Tier 1 killer)               │
│  ─ ✅ Auditable decomposition                                    │
│  ─ ✅ Autoregressive generation (Tier 1 killer)                  │
│  ─ ✅ R10 K-scaling falsifies Lippl-Stachenfeld                  │
│  ─ ✅ Hebbian-only training (no backprop)                        │
├───────────────────────────────────────────────────────────────────┤
│  FULL MAP (current rendered markdown, anchor-linkable)            │
│  ... (existing markdown view continues here, with anchor links    │
│       wired up so Headline rows jump to the right section)        │
└───────────────────────────────────────────────────────────────────┘
```

The tier-counts row should match the cap_map's own "Summary tally" table — extracted programmatically by parsing the last `| Section | ✅ | 🟢 | ... |` table in the file. If parse fails, surface a banner: "tier-summary parse failed — showing raw map below."

---

## (d) Data sources

| Panel | Source file | Pulled by |
|---|---|---|
| Headline banner | `notes/substrate_capability_map.md` (tier counts), `data/local_dashboard_snapshot.json` (gpu%/runners), latest `orchestrator_status_log.jsonl` line (current work) | poller.py (already pulls cap_map; new: status_log tail) |
| Now Running | `overnight_queue/heartbeat.json`, `overnight_queue/queue.json`, `remote_cpu_queue/heartbeat.json`, `*/queue.log`, `exp_<name>/progress.json` | poller.py (already does this) |
| Orchestrator Status Stream | `data/orchestrator_status_log.jsonl` (NEW source — currently not pulled) | poller.py (add new SSH command) |
| Queue Depth | `*/queue.json` | poller.py (already) |
| In-flight routings | List `notes/*_to_*_*.md` files; cross-ref against `notes/orchestrator_status_log.jsonl` for "delivered" events. Also `notes/active_priorities.md` for the official open list. | poller.py (NEW: list notes/ via SFTP) |
| Sub-agents dispatched | `orchestrator_status_log.jsonl` filtered to event_kind ∈ {sub_agent_dispatched, research_agent_launched} without a paired returned event | poller.py (already has events; new derivation) |
| Recent Verdicts | `data/event_outcomes/*.json` (already pulled by local monitor) + status_log entries with event_kind="verdict" | poller.py (add event_outcomes listing) |
| Status tab Timeline | `data/orchestrator_status_log.jsonl` (last 24h, all entries) | poller.py |
| Today's Audit | `notes/audit_dropped_and_review_<date>.md` (newest) | poller.py SFTP read |
| Tier Summary | parse last "Summary tally" markdown table in `notes/substrate_capability_map.md` | server.py (new derived endpoint `/api/capability/tiers`) |
| Actively being expanded | join orchestrator_status_log entries (last 24h) with cap_map capability names | server.py |
| Experiments table | unchanged — `session_events.jsonl` + queue.log + queue.json | poller.py (already) |

---

## (e) Implementation plan — concrete file changes

### `tools/dashboard/poller.py`
1. Add to `_build_cmds()`:
   ```
   ("orchestrator_status_log",
    'powershell -Command "Get-Content C:\\dev\\hd-instrument\\data\\orchestrator_status_log.jsonl -Tail 300"')
   ```
2. Add to `_build_cmds()` a listing of routing files:
   ```
   ("notes_routing_files",
    'powershell -Command "Get-ChildItem C:\\dev\\hd-instrument\\notes -Filter *_to_*_*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 30 Name,LastWriteTime"')
   ```
3. In `_build_snapshot()`:
   - Parse `orchestrator_status_log` via a new `parsers.parse_status_log(text) -> list[dict]`.
   - Compute `in_flight_dispatches`: status entries with `event_kind="sub_agent_dispatched"` whose matching `sub_agent_returned` is missing or older.
   - Compute `open_routings`: file list filtered to those whose name doesn't appear as `delivered_routing` in the status log.
   - Add `status_log`, `in_flight_dispatches`, `open_routings`, `tier_summary` to the snapshot dict.
4. Add `fetch_audit_doc(date)` to atomic-read `notes/audit_dropped_and_review_<date>.md` if present.

### `tools/dashboard/parsers.py`
1. New function `parse_status_log(text: str) -> list[dict]`: same shape as `parse_event_log`, jsonl-tolerant.
2. New function `extract_tier_summary(cap_md: str) -> dict | None`: regex/state-machine for the final "Summary tally" table; returns `{counts_by_section: {...}, totals: {"validated": 12, "want_stronger": 6, ...}, parse_ok: bool}`.
3. New function `extract_active_capability_expansions(status_log: list[dict], window_h: float=24.0) -> list[dict]`: collect distinct capability names mentioned in `summary` fields of recent verdict/research_delivery entries.

### `tools/dashboard/server.py`
1. Add endpoints:
   - `GET /api/status_log?limit=50&since=2026-05-23T00:00&kind=verdict` — paginated/filtered status feed.
   - `GET /api/capability/tiers` — derived tier summary.
   - `GET /api/in_flight` — dispatched-but-not-returned sub-agents + open routings.
   - `GET /api/audit/today` — today's audit_dropped_and_review_<date>.md if present.

### `tools/dashboard/static/index.html`
1. Reshape grid: add a top banner row before `main`; rearrange `main` grid areas to `headline / runs status / queue inflight / verdicts`.
2. Add a Status tab and a new `<section id="status-view">` with the timeline + full feed.
3. Replace `renderEvents` with `renderStatusStream` that consumes `snap.status_log` (richer schema: event_kind + sub_agents + outcome) and renders the right-column status panel.
4. Add `renderHeadlineBanner(snap)` and call it at the top of `refresh()`.
5. Add `renderCapabilityTierSummary(tierSummary)` and prepend it to the Capability tab.
6. Add `renderInFlight(snap.in_flight_dispatches, snap.open_routings)` for the new right-bottom panel.
7. CSS: a new `.status-stream` block + reuse `.event-chip` styling. New `.headline-banner` with one-line layout.

### Orchestrator-side (out of dashboard repo but required for the loop to close)
The status log already exists at `data/orchestrator_status_log.jsonl` (11 entries today). Going forward:
- Every sub-agent dispatch writes a `sub_agent_dispatched` entry with an `agent_id`.
- Every sub-agent return writes a `sub_agent_returned` entry referencing the same `agent_id`.
- Every cap_map version bump writes a `cap_map_committed` entry with the new version.
- Every routing file creation writes a `routing_created` entry with the file path.
- Every audit run writes an `audit_completed` entry with path to the audit doc.

This is a documentation/protocol change for the orchestrator prompt — out of scope for the dashboard PR itself but called out explicitly because the dashboard's value scales linearly with how diligently this file is written.

---

## (f) Cheapest MVP

If we want the user's core ask delivered TODAY with minimal code, ship these three changes and nothing else:

**MVP-1: Status stream visible on Live tab (≈90 minutes)**
- poller.py: add the one new SSH command for `orchestrator_status_log.jsonl`, parse it as jsonl.
- parsers.py: add `parse_status_log` (≈10 lines, copy of `parse_event_log`).
- server.py: add `status_log` to the snapshot payload.
- index.html: replace the existing Events ribbon's content with status_log entries (richer fields). Keep CSS as-is; reuse `.event-chip` classes; add icons for the new event_kinds (`verdict`, `research_delivery`, `cap_map_committed`).
- Net result: user opens dashboard, sees the orchestrator status feed at the bottom of Live, no longer needs to ask "what are you doing?"

**MVP-2: Capability tab tier summary banner (≈45 minutes)**
- parsers.py: add `extract_tier_summary` (parse the last `Summary tally` markdown table).
- server.py: add it to the snapshot via the existing capability-map fetch.
- index.html: render a small tier-counts bar at the top of the Capability tab, above the existing markdown.
- Net result: user opens Capability, sees `12✅ 6🟢 4🟡 17🔬 13❌` as the headline instead of having to read the whole document.

**MVP-3: Drop the Experiment tab and rename Tests → Experiments (≈10 minutes)**
- index.html: remove the Experiment tab button + view section. Rename Tests label.

**Total MVP scope: ≈2.5 hours of work, single PR.** Delivers the user's headline ask: status visibility + reality-reflective capability tab + no dead tabs.

Everything else in this proposal (Status tab, in-flight panel, audit display, tier expansions, routing tracking, full timeline) is post-MVP polish.

---

## (g) Citations / design pattern references

1. Stephen Few, *Information Dashboard Design: Displaying Data for At-a-Glance Monitoring* — canonical reference for the "single screen, monitored at a glance" discipline and the data-ink minimization that motivated the headline-banner + four-panel layout. ([Amazon listing](https://www.amazon.com/Information-Dashboard-Design-At-Glance/dp/1938377001), [Goodreads](https://www.goodreads.com/book/show/336258.Information_Dashboard_Design))

2. Weights & Biases experiment-tracking dashboard pattern — the "central place to organize ML experiments, search/filter/sort/group" pattern is the antecedent for the Experiments tab; the live-update stream pattern is the antecedent for the Status Stream. ([wandb.ai experiment tracking](https://wandb.ai/site/experiment-tracking/))

3. MLflow runs dashboard — sortable per-run table + metrics/parameters/artifacts pattern. Antecedent for the Experiments tab's expandable-row design (already present in current dashboard). ([MLflow ML tracking docs](https://mlflow.org/docs/latest/ml/tracking/))

4. Grafana state-timeline visualization — the horizontal-timeline-of-state-changes pattern proposed for the new Status tab. ([Grafana state-timeline docs](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/state-timeline/), [Grafana status-history](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/status-history/))

5. Datadog event stream / events-query pattern — the "tail the event stream as the system of record" pattern that drives the Status Stream design (events are structured, dashboard panels are derived views). ([Datadog dashboards](https://docs.datadoghq.com/dashboards/))

6. Hatica activity-log dashboard pattern — "bird's-eye view of daily activity, surface blockers" pattern motivates the Audit section of the Status tab. ([Hatica activity log docs](https://www.hatica.io/docs/dashboards/catalog/activity-log/))

7. Event-log vs application-log distinction (Last9 / general SRE practice) — motivates keeping the status_log as a *structured* JSONL separate from raw stdout tails; the status log is for *business/decision events*, the queue.log is for *application execution events*. ([Last9 on event logs](https://last9.io/blog/event-logs/))

---

## Open questions (decisions the user/orchestrator should make)

1. **Status log granularity**: should `sub_agent_dispatched` fire for every Sonnet lit-scan agent, or only for Opus orchestrator-level dispatches? Default proposal: every dispatch, with a `model` field so the UI can filter Opus-vs-Sonnet noise.
2. **Routing-delivered tracking**: how does a routing get marked "delivered"? Proposal: the consuming session writes a `routing_delivered` event with the path. Or: a routing is considered delivered if any subsequent commit to `notes/research_*.md` or `notes/exp_dev_*.md` references its filename. Cheaper: just track creation time and let the user eyeball staleness.
3. **Headline banner currently-working-on line**: which status log entry counts? Proposal: the most recent entry whose `event_kind` is in `{dispatch, sub_agent_dispatched, verdict, research_delivery, cap_map_committed}`. Skip `observation` and `orchestrator_init`.
