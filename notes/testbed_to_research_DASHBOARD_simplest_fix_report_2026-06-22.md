# TESTBED -> RESEARCH (team lead): DASHBOARD STATE + SIMPLEST FIX PATH

## TL;DR
Dashboard is **8/9 endpoints working**. Only the **Health tab** times out. **One small edit to `tools/dashboard/server.py` likely fixes it** (cache git log result that's currently redundantly invoked per in-progress priority). Phase 4 architecture updates (Agent-Teams-aware detectors) are optional follow-ups, NOT urgent.

## Empirical state (verified 2026-06-22 ~01:55Z)

| Endpoint | Status | Tab |
|---|---|---|
| `/api/dashboard/v2/health` | ❌ **TIMES OUT @ 8s** | Health (broken) |
| `/api/snapshot` | ✅ 200 | For You / Live / Inbox / Tests |
| `/api/substrate` | ✅ 200 | Substrate |
| `/api/tests` | ✅ 200 | Experiments |
| `/api/director_plan` | ✅ 200 | Health (sub-section; this part works) |
| `/api/fleet_engagement` | ✅ 200 | Health (sub-section; works) |
| `/api/sessions` | ✅ 200 | Live fleet view |
| `/api/research_map` | ✅ 200 | Research |

## Root cause (the SINGLE bug)

In `tools/dashboard/server.py` the **D3 plan-stall detector** runs git log subprocess INSIDE a per-priority loop. The first git log call is FIXED-output (doesn't depend on priority); it should run ONCE outside the loop.

**Location:** approx lines 845-870 of `tools/dashboard/server.py` (the `plan_stalls` block). Look for `for pr in plan.get("priorities", []) if isinstance(plan, dict) else []:` then `try: import subprocess as _sp; out = _sp.check_output(["git", "-C", str(_REPO_ROOT), "log", "--since=6.hours.ago", ...]`.

With 5 in-progress priorities = 5 redundant git log calls × ~1-3s each = up to 15s. Plus D2 + D3-per-priority `git log -1 -- <cell>` = total exceeds 8s timeout.

## SIMPLEST FIX (one edit, 5 minutes)

In `tools/dashboard/server.py`, **move the reframe-check git log call OUTSIDE the per-priority loop**. Run once, cache result, check for each priority's keyword in the cached output.

### Edit pattern

Find this block (around line 850-868):
```python
for pr in plan.get("priorities", []) if isinstance(plan, dict) else []:
    if pr.get("status") != "in-progress":
        continue
    cell = pr.get("cell")
    ...
    try:
        import subprocess as _sp
        out = _sp.check_output(
            ["git", "-C", str(_REPO_ROOT), "log", "--since=6.hours.ago",
             "--pretty=format:%s"],
            timeout=5, text=True, errors="replace",
            creationflags=_CREATE_NO_WINDOW,
        )
        reframe_found = False
        if pid_keyword and len(pid_keyword) >= 4:
            for ln in out.splitlines():
                ...
```

Refactor to:
```python
# Cache once outside the loop
_reframe_log_cached = None
try:
    import subprocess as _sp
    _reframe_log_cached = _sp.check_output(
        ["git", "-C", str(_REPO_ROOT), "log", "--since=6.hours.ago",
         "--pretty=format:%s"],
        timeout=5, text=True, errors="replace",
        creationflags=_CREATE_NO_WINDOW,
    )
except Exception:
    _reframe_log_cached = ""

for pr in plan.get("priorities", []) if isinstance(plan, dict) else []:
    if pr.get("status") != "in-progress":
        continue
    cell = pr.get("cell")
    ...
    out = _reframe_log_cached  # use cached
    reframe_found = False
    if pid_keyword and len(pid_keyword) >= 4:
        for ln in out.splitlines():
            ...
```

### After the edit

1. **Restart dashboard server** to pick up changes:
   ```
   schtasks /End /TN hd_dashboard ; Start-Sleep 2 ; schtasks /Run /TN hd_dashboard
   ```
2. **Verify fix:**
   ```
   curl -sS --max-time 15 -o NUL -w "HTTP %{http_code} in %{time_total}s\n" http://localhost:8765/api/dashboard/v2/health
   ```
   Expected: `HTTP 200 in <5s`.

If still slow, the per-cell `git log -1 -- <cell>` calls (also inside the loop) may also need similar caching — but try the above first.

## Where the dashboard ties in under Agent Teams (your real architectural question)

**Short answer: it doesn't need to change much. It's session-architecture-agnostic.**

The dashboard reads disk state:
- `data/substrate_index/*/atoms.jsonl + audit.jsonl` — same under Agent Teams
- `data/director_plan.json` — you (Research as lead) maintain it
- `data/fleet_waiting_on.md` — same shape; mostly Research's section now
- `notes/*.md` — same (HYBRID architecture keeps cert-trail here)
- Git log — same

Tabs that work as-is under new arch: For You, Live (sessions), Inbox, Experiments, Capability, Research, Substrate, Substrate 3D.

Tab that needs fix (this report): Health.

## Phase 4 optional follow-ups (NOT URGENT — defer until USER asks)

- **D5 fleet-section-stale** detector assumes 5 active per-role sections; under Agent Teams only Research's is meaningfully live. Will throw false-RED for ex-session sections. Fix: scope detector to only "lead" role under Agent Teams (or just disable until needed).
- **D6 idle-without-reason** (my recent addition) same assumption. Same fix.
- **Live / Sessions tab** shows 5 sessions; under Agent Teams really shows Research + spawned teammates. Cosmetic; works but conceptually misaligned.
- **Cycle history panel** assumes cycle protocol still runs; under Agent Teams this is retired. Can be removed eventually.

These are non-breaking issues. False-REDs from D5/D6 are noise, not blockers. Recommend addressing in a single "Phase 4 dashboard cleanup" cycle when convenient.

## What I (Testbed) am NOT doing

- NOT applying the fix myself (I committed to no Bash/commits during USER popup-sensitive window)
- NOT spawning teammates (under new arch, that's your call as lead)
- NOT making architectural decisions about Phase 4 detector updates (your call after USER ratifies the Agent Teams transition fully)

## What I CAN still do

- Verify the fix worked after you apply it (one curl call; accept 1 popup)
- Document the change in fleet_status_NOW.md
- Cross-witness on dashboard endpoint behavior over time

## Recommended hand-off action for you

Spawn `hdi_testbed` with this prompt:
```
Apply the dashboard fix per testbed_to_research_DASHBOARD_simplest_fix_report_2026-06-22.md (D3 detector caches git log outside per-priority loop; one edit in tools/dashboard/server.py around line 850). Restart hd_dashboard scheduled task. Verify Health endpoint returns HTTP 200 in <5s. Reply with verification result.
```

That's ~10 minutes of teammate work, no decisions required, clear pass/fail. After it lands, Health tab works and you can proceed with Phase 3 autonomous arc unbothered by dashboard noise.

— Testbed (Integrator), under "check but don't control" Phase 3 audit role
