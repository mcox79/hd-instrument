# FERRY-REQUEST (Director → USER): old-session ferry asks per Fix #15

**Per Fix #15 discipline (banked 2026-06-22 post-overnight evaluation):** ferry-requests should be EXECUTED (filed as notes FOR USER to relay to old sessions) not deferred. Three lingering ferry-asks from this autonomous arc; consolidated here for USER to relay when convenient (low-pri; not blocking).

## Ferry-ask #1 (HIGH-pri if Path A V_C=4096 overruns): pythia-160m encoding rate on `marsh@home` CPU

**To: old orchestrator session**

Question: typical pythia-160m encoding wall-time per 1000 facts on `marsh@home` CPU? n2_capacity_scaling baseline was ~10-11min/seed at V_C=1024/N=16384; n9 SMH was ~22min/seed (encoding-dominant); n10 whitening + Path A V_C=4096 are in flight with extrapolated walls 7-15hr.

Why we care: cell-author runtime estimates have been ±100-600x off this session (per Orch's own handoff Section 7b "subagent runtime estimates are not reliable"). A reference rate (e.g., "12500 facts × pythia-160m ≈ 17min CPU") would let pipeline-agent spawns set wall-budgets correctly per Fix #17.

What I already know from handoffs: Orch handoff Section 7b discipline "measure don't quote" + "30s local matmul timing test settles it." But no specific rate-norm documented.

Status if USER doesn't ferry: I'll continue measuring per-cell. Not blocking.

## Ferry-ask #2 (MEDIUM-pri; mostly resolved): watcher semantics under Agent Teams

**To: old testbed session**

Question: confirm that background bash watchers (via `run_in_background: true`) do NOT emit `task-notification` events that surface via Stop hook. The Monitor tool is the mechanism for auto-wake. Is there a way to make a background bash watcher trigger wakes?

What I already know: testbed-authored `AGENT_TEAMS_MIGRATION.md` says TeammateIdle is inbox-based (notes/ unread) not background-bash-output-based. Empirically confirmed via SMH spawn (background watchers wrote to temp files; never surfaced via Stop hook). So Fix #4 stands as banked.

Status if USER doesn't ferry: discipline already applied (no background bash watchers in cell-author spawns per Fix #4). Mostly closed.

## Ferry-ask #3 (LOW-pri; clarifying): per-seed pythia re-loading pattern

**To: old exp_dev session**

Question: in cells using `EleutherAI/pythia-160m` for ingest encoding (n3 / n4 / n5 / n6 / n7 / Path C / n9 / n10), the runner log shows multiple "Loading weights" stanzas — one per seed. Is this a known wart of the cell-author template (model re-loaded per seed instead of cached across seeds) or did individual cell-authors introduce it?

Why we care: if model can be loaded ONCE per run and reused across seeds, that's ~10-15s × n_seeds saved per cell (small but adds up; 3 seeds × 10 cells × 15s = 450s = 7.5min cumulative savings across this session).

Status if USER doesn't ferry: low-impact optimization; can defer to post-bigram-gap-closure cycle. Not blocking.

---

**Per Fix #15:** these are filed for USER ferry; not blocking ongoing work. Standing by per autonomous-loop discipline.

— Research (Director), Fix #15 ferry-execution discipline applied
