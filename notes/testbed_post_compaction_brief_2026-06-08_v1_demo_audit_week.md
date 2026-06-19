# Testbed POST-COMPACTION BRIEF — v1 demo audit week + open issues

**Compiled:** 2026-06-08 ~16:15 UTC  (just before compaction)
**Read this FIRST after compaction. Single source of truth for resume.**

---

## 🔴 CURRENT STATE: Day 1 of v1 demo audit week COMPLETE; Day 2 next

Testbed lane has PIVOTED from per-cell GPU experiments to the **v1 demo APP BUILD**
(routed by Research + Exp-Dev). 4-6 week timeline. This session JUST FINISHED audit
Day 1 (substrate primitive portability audit on laptop, no GPU).

## 🔒 LOCKED architecture (user-signed off 2026-06-08)

| Decision | Value |
|---|---|
| Hosting | **Desktop hosts everything** (marsh@home: 64 GB RAM, RTX 4060 Ti 8 GB, i5-12400F) |
| Public access | **Cloudflare Tunnel** → free public URL accessible from anywhere |
| Tier-5 KV path | **PATH A primary** (Pythia-1.4B fp16 on 4060 Ti; substrate-KV layer); PATH B (K-hop only) fallback per Research |
| Infrastructure cost | **$0** (desktop already owned; tunnel free); only API costs (user-handled) |
| Frontend | Next.js dark sophisticated style |
| Backend | FastAPI |
| KB | Hybrid Wikipedia 5.84M + Corporate Intelligence overlay (bootstrap: SEC EDGAR free + News RSS); paid Crunchbase deferred |
| Acceptance gate | ≥3/5 corporate-OR-multi-hop queries (revised per Research clarification; NOT random 3/5) |
| KB scale target | 5-10M facts in 64 GB RAM |

## 📝 USER QUESTION RAISED JUST BEFORE COMPACTION (must address)

> "since we're setting this up on the desktop, could we have a trigger (for demo use)
> that pauses all the experiments we're running on CPU and GPU, while the demo is
> active? Or there's a toggle on the demo window or something? I want it hardened
> against not working as we want it to"

**Answer to bring back post-compaction:**

YES — and this is a real concern. Desktop runs (a) experiment dispatch queues (CPU
`hd_cpu_runner_0` + GPU `hd_gpu_runner_0` schtasks) AND (b) the demo backend. Both
compete for the 4060 Ti GPU + the i5-12400F + 64 GB RAM. Without isolation, a heavy
experiment during a customer demo = perceived demo slowness or crash.

**Proposed mechanism (to design Day 2)**:

1. **Hard pause endpoint**: a `/admin/demo-mode-on` HTTP endpoint on the backend that:
   - Writes a flag file at `data/demo_mode_active.flag`
   - Sends SIGSTOP to all dispatched experiment processes (suspended, not killed)
   - Sets a watchdog cron that re-suspends any new experiment proc within 30 sec
   - Returns OK only when no `python.*exp_*.py` procs are RUNNING (not just present)
2. **Resume endpoint**: `/admin/demo-mode-off` removes the flag, SIGCONT all suspended
3. **Auto-pause on demo activity**: when a `/query` arrives, set the flag if not already
   set. After 5 min of demo inactivity, auto-clear.
4. **UI toggle on demo window**: settings gear → "demo mode" toggle (red/green). Default
   red (paused) when in customer demo; green (sharing) for routine browsing.
5. **Hardening against partial failure**:
   - Flag file persists across desktop restarts (filesystem, not memory)
   - Watchdog runs every 30 sec via existing cron infra (`/loop`-style)
   - If watchdog dies, demo-mode auto-clears after 10 min (fail-open to keep experiments running rather than fail-closed)
   - Logs every state change for forensic
   - Test by: launch demo, dispatch a CPU experiment, confirm experiment is suspended
6. **Don't break the experiment-dispatcher contract**: experiments use `tools/orchestrator/` schtasks that respect `data/orchestrator_paused.flag` per memory. We CAN piggyback on that mechanism: demo-mode-on = `touch data/orchestrator_paused.flag` (and SIGSTOP any running children); demo-mode-off = `rm` it and SIGCONT.

**This goes into Audit Day 2 + becomes part of Week 1 backend foundation.**

## ☁️ CELL-A2 CLOSED — killed pre-verdict

- Dispatched Llama-3.1-8B Path B multi-hop revival test on Lambda GH200 us-east-3
- Stuck in `flash-attn` aarch64+cu128 source compile 87 min; GPU 0% util; Llama download never started
- Killed at $3.30 sunk cost
- **A2 is not load-bearing** — cycle 187 PUBLIC BENCHMARK WIN (WebQSP 98.2%, CWQ 94.7%,
  FB15K 1.0/0.85 vs monolithic 0.05 = 140× gap) already proves substrate multi-hop categorically
- Wikipedia NER for v1 demo uses spaCy fallback (Llama-8B can be revisited in v1.5 if needed)
- Memory entry saved: [[feedback-pip-install-timeout-on-aarch64-compiled-packages]]
- Research note filed: `notes/testbed_note_cell_a2_killed_pre_verdict_2026-06-08.md` (commit `e3e4d57b`)

## ✅ AUDIT DAY 1 DELIVERABLE

**File:** `notes/testbed_audit_day1_substrate_portability_2026-06-08.md`

Read 9 of 11 PP-* primitive cells. Findings:
- All cells are 50-110 line research POCs on **synthetic numpy data**
- Share 4 common FHRR primitives (cphasor, cidx, bind, unbind) — extract to `substrate/core.py`
- No shared substrate engine; each cell builds its own M matrix from scratch
- Algorithmic logic is the production blueprint; production wrapping (persistence, indexing, multi-tenant) is what I add
- Proposed library structure: `substrate/{core,shards,khop,cascade,disambig,confidence,inverted,cross_shard,gdpr,bitemporal,counterfactual,audit,kv_memory,persistence}.py`
- Week 1 port-priority list: 5 days, ending with `/query` endpoint working over 10K-fact demo KB

**Deferred to Week 1 Day 1:** read `mechanism_composition_v1_n4096.py` (544 lines, the biggest port; the small cells suggest it composes primitives but worth confirming).

## 📋 OPEN AUDIT-WEEK TASKS (resume here after compaction)

| Day | Task | Status |
|---|---|---|
| 1 | Substrate primitive portability audit | ✅ DONE; output filed |
| 2 | Cloudflare Tunnel setup on desktop | pending |
| 2 | Pythia-1.4B + substrate-KV GPU smoke on 4060 Ti (VRAM fit check; if tight, drop to int8 or PATH B) | pending |
| 2 | **DEMO-MODE EXPERIMENT-PAUSE TOGGLE** (per user request above) | pending |
| 2 | Node.js + Next.js + Tailwind toolchain install on desktop | pending |
| 2 | API key + budget setup (OpenAI + Anthropic accounts; user handles) | pending |
| 2 | Risk register re-review | pending |
| 3 (gated) | If A2 needed: redispatch without flash-attn (use SDPA fallback); ~30 min wall, ~$1.20 | DECISION |

Audit Day 2-3 can run in parallel — most are independent.

## 💸 Today's cost ledger

| Item | Cost |
|---|---|
| CELL-A2 (killed pre-verdict) | $3.30 |
| Plan iterations (filing notes) | ~$1.50 |
| **Today total** | **~$4.80** |
| **Drill Y envelope remaining** | ~$96 (of $100-200) |

## 🧠 NEW MEMORIES SAVED TODAY

| Memory | Key takeaway |
|---|---|
| [[feedback-pip-install-timeout-on-aarch64-compiled-packages]] | Wrap source-compile pip installs in `timeout 600` OR drop entirely if graceful runtime fallback exists |
| [[feedback-pre-dispatch-speed-harden-progress-discipline]] | Apply 3 audits BEFORE every cloud dispatch: speed + failure-mode + progress-saving |
| [[project-multihop-revive-priority]] | User mandate: revive multi-hop despite Research closure; Research designs revival, Testbed executes routings |
| [[feedback-always-send-research-note-on-results]] | EVERY result → Research note immediately; not optional |
| [[feedback-never-edit-bash-script-mid-run]] | Bash byte-offset position tracking breaks if file modified mid-run |
| [[feedback-no-survey-questions]] | Plain chat questions only, no AskUserQuestion tool |

Plus 11 earlier today: bash heredoc piped stdin, --gpus conflict, YAML accelerators, any_of validation, kill_switch stale log, sky api stop killing server, preflight prefix isolation, function signature mismatch self-test blind, torch pin arch wheels, WSL distro auto-shutdown, debug discipline silent kills.

**Total memory entries from today: ~17**.

## 📌 NOTES FILED TODAY (Testbed → Research/Exp-Dev)

1. `testbed_to_research_a2_llama8b_priority_verify_2026-06-08.md` — pre-dispatch verification
2. `testbed_note_cell_a2_killed_pre_verdict_2026-06-08.md` — A2 kill report
3. `testbed_to_research_user_multihop_revive_mandate_2026-06-07.md` — user mandate filed
4. `testbed_v1_demo_BUILD_PLAN_2026-06-08.md` (REV 1) — 4-6 week build plan; user-signed off
5. `testbed_audit_day1_substrate_portability_2026-06-08.md` — TODAY'S audit doc

## 📥 NOTES RECEIVED FROM OTHERS

1. `research_to_testbed_v1_demo_SPEC_2026-06-08.md` — the formal spec (PRIMARY)
2. `exp_dev_to_testbed_v1_demo_app_build_handoff_2026-06-08.md` — Exp-Dev confirms split
3. `research_to_testbed_BUILD_PLAN_response_2026-06-08.md` — Research signed off + 2 clarifications
4. `research_to_testbed_A2_CONFIRM_proceed_with_n100_2026-06-08.md` — A2 confirm (n=100)
5. `exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md` — concrete substrate-side numbers for demo head-to-head panels

## 🎯 IMMEDIATE NEXT STEP (resume here)

**Audit Day 2** kicks off. Tasks (parallelizable):

1. **Design demo-mode experiment-pause toggle** — write the actual `/admin/demo-mode-on` endpoint spec + watchdog cron + UI toggle + hardening rules. Document in the build plan and start the actual code in Week 1 Day 1.
2. **Cloudflare Tunnel install + auth on desktop** — `cloudflared` from Cloudflare, `cloudflared tunnel create v1-demo`, test from external network. ~30 min.
3. **Pythia-1.4B GPU smoke** — small Python script on desktop runner: load Pythia-1.4B fp16, verify <4 GB VRAM, basic forward pass. ~30 min.
4. **Node.js install + Next.js scaffold** — `npm create next-app substrate-demo` with Tailwind. ~30 min.
5. **API key setup** — user creates OpenAI + Anthropic accounts; I write `.env.local.example` template. ~15 min.
6. **Risk register re-review** — read REV1 plan; surface any newly-discovered risks. ~30 min.

Total Day 2: ~3 hr work (audit-style, no engineering yet).

## ⚠️ THINGS TO RE-LEARN POST-COMPACTION

- Most of today's bug-fix history is in memory entries; safety stack scripts at `skypilot/safety/*.sh` are battle-tested
- `marsh@home` runner is the DEMO HOST (64 GB / 4060 Ti 8 GB / i5-12400F)
- This laptop (32 GB / Intel UHD) is just the dev terminal
- Cycle 187 = PUBLIC BENCHMARK WIN (substrate sharded vs monolithic = 140× gap on FB15K-237)
- v1 demo SPEC is locked at `research_to_testbed_v1_demo_SPEC_2026-06-08.md`
- I am Testbed, NOT Research, NOT Exp-Dev. My lane is engineering the demo + cloud dispatch.

## 🔗 KEY FILES

| File | What |
|---|---|
| `notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md` | The 4-6 week build plan REV1 |
| `notes/testbed_audit_day1_substrate_portability_2026-06-08.md` | Today's substrate library design |
| `notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md` | Research's authoritative demo spec |
| `notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md` | Substrate-side benchmark numbers |
| `skypilot/safety/` | Cloud dispatch safety stack (still works for any future cell) |
| `MEMORY.md` | Index of all 17+ memory entries from today |

---

**END OF BRIEF**

If compaction hits between now and Audit Day 2 start, resume by:
1. Read this brief
2. Read `notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md`
3. Read `notes/testbed_audit_day1_substrate_portability_2026-06-08.md`
4. Pull repo (`git -C D:/AI/hd-instrument pull`)
5. Check `notes/` for any new Research/Exp-Dev routings since 16:15 UTC today
6. Pick up at "Audit Day 2 tasks" above. First priority: design the demo-mode toggle.
