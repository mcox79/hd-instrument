# Orchestrator handoff snapshot (Agent Teams migration prep)

**Role:** orchestrator (dispatch / custody / verify-it-starts / route verdicts to cert-owner + Director)
**Written:** 2026-06-22 ~00:0xZ
**Status when written:** STANDSTILL honored (per USER directive); one in-flight cell completing; queue paused after that

---

## 1. CURRENT IN-FLIGHT WORK

- **`n2_capacity_scaling_v1` (commit efd3d3e6) RUNNING on remote_cpu_queue.** The N-scaling breakthrough test: sweeps N_DIM {4096, 8192, 16384} × V_C=1024 × depth {1,2}, 3 seeds. Dispatched ~23:45Z on USER's "get to work" right before the STANDSTILL directive reached me via Testbed's relay. Per standstill rule "active in-flight work continues to completion," it finishes. Real runtime measured ~13-15 min (NOT the subagent's 9-27h estimate; see section 7b). Watcher `bxqqp9rta` running.
- **Heartbeat-keeper bash `bsyv6lztm`** background loop touching `data/heartbeats/orchestrator.timestamp` every 8min for ~8h. Interim self-heal because the Stop-hook auto-heartbeat doesn't fire for orchestrator (role-resolution gap, see section 5 / Testbed note a43a7d68).
- **Standstill ACK note** filed (a7a6a501). My only ask from Testbed's standstill spec: pause new dispatches (done) + verify in-flight sync (in-progress; the watcher handles it).

---

## 2. WORKING ASSUMPTIONS (not in plan.json / fleet_waiting_on.md)

- The N-scaling breakthrough cell will **most likely come back MIDDLE_BAND or HARD_FAIL on beat-bigram (3.84).** My read: even with N=16384 un-saturating V_C=1024 (α≈0.5) and the low floor (1.96), the recall-error gap won't shrink enough — best case ~4.0-4.5 BPC, near bigram but not below. The architecture appears to cap above bigram at this concept resolution. If by some chance it DOES beat bigram, see section 5 for the instrumentation tension.
- The cell **lacks Skunkworks's required chain-grade instrumentation** (per_unit BPC array, logged zero-LLM-call assertion in metrics.json — not just in code comments, VQ-floor decomposition). Flagged by Skunkworks in her N1 landed-VET. Under standstill, a re-run is not allowed without USER auth.
- The remote_cpu_queue runner on marsh@home is the only active runner. overnight_queue (GPU) appears idle. local_cpu_queue runner may have died after the daemon revival earlier in the session.
- The fleet self-recovered around 22:30Z after a ~4h dark period. All four sibling sessions are now back and aligned on the standstill+migrate directive. Director-stance flipped NOT-NOW → GO; HYBRID architecture endorsed (cert-trail stays in Store+git, only coordination migrates).
- Phase 3 migration (orchestrator → `hdi_orchestrator` teammate) is later. My role contract is well-defined and largely captured in `.claude/agents/hdi_orchestrator.md` once Testbed writes it. The dispatch tools (queue_add.sh) survive the migration unchanged.

---

## 3. WHAT I WAS ABOUT TO DO NEXT

1. **Read the breakthrough verdict** when the watcher fires (~15 min from dispatch). Verify the N=4096/V_C=1024/K=1 anchor reproduces the co-opt's ~5.27 (correctness check) before believing the other configs.
2. **Route the breakthrough result:** Skunkworks for landed-VET + Research for Director cross-check. If it beats bigram, surface the instrumentation gap (chain-grade claim blocked without per_unit/logged-zero-LLM) to USER for a re-run-vs-accept-as-PROVEN-BOUND decision.
3. **Hold at standstill thereafter** + support migration as Phase 3 reaches me (convert orchestrator role to teammate def; map queue_add tooling + remote scp/sync ownership).

---

## 4. TACTICAL CONTEXT (role-specific accumulated understanding)

- **The N1→N2 calibration arc this session** is a SCIENCE story, not a coordination story. The substrate-only LM milestone is REAL (Skunkworks cert-confirmed substrate-only PASS off cell code), but it required 5+ cell iterations: v2 (broken metric, BPC 1614) → v3 (bounded but mis-calibrated, baselines worse than unigram) → v3 NameError fix → v3.1 (count-proportional decode + interpolation, gave 5.00) → N2 depth (floor-masked) → N2 co-opt (saturation finding). Every iteration was a CALIBRATION or INSTRUMENTATION bug, never a capability failure. **The substrate's point predictions (top-1 0.445) were correct from v2.** The discipline lesson is: trust the substrate's structure signal; distrust the metric until it self-checks (ceiling ≤ log2(V), alpha < 1.0, all baselines proper).
- **The 3-way lever knot finding (V_C × N × depth)** is the deep architectural result. At N=4096, V_C=256 is the sweet spot; single-lever pushes hit different walls (depth → floor-mask; finer V_C → saturation). This is in the routing notes but the *intuition* is: the substrate-LM has natural operating points where capacity / floor / context-prediction are all proportionate. Off those points it gets worse, not just plateaus.
- **The fleet had a 4-hour dark window** (research/exp_dev/skunkworks all stale, only me + testbed responding to pings). I drove N1 → N2-depth → N2-coopt → N-scaling-cell-authoring through that, solo, via subagents + in-thread. The USER eventually surfaced the fleet-stall I'd flagged, then said "get to work" → I drove the breakthrough. The fleet revived shortly after.
- **Two subagents died** during process restarts (recovery cell mid-author; v3 calibration mid-author). In-thread work survives process restarts at commit boundaries; subagents don't. After those failures I started doing structural cell changes in-thread and using subagents only for fresh cell authoring.
- **The HYBRID migration architecture** (Skunkworks's call): cert-trail stays in Store+git unchanged (durable, observable, A5-gated); only the lightweight coordination layer (pings, waiting-on, routing) moves to Agent Teams. This is the right de-risking. Orchestrator's role under HYBRID: my queue_add.sh + remote scp/sync stays a tool (not migrated); my coordination notes become SendMessages + shared task-list updates.

---

## 5. CRITICAL OPEN LOOPS

- **The breakthrough verdict itself** — pending, ~minutes away. Whatever it returns is the substrate-only LM's bigram-beat answer.
- **If breakthrough beats bigram** (CHAIN-GRADE candidate): the cell lacks Skunkworks's required per_unit + logged-zero-LLM assertion + VQ-floor decomposition. Under standstill, no re-run allowed without USER auth. USER must decide: allow an instrumented re-run, accept as PROVEN-BOUND tier (saturation guard already flags it), or treat as preliminary.
- **Stop-hook role-resolution bug** for orchestrator. Testbed has the precise diagnosis (a43a7d68): the user-scope Stop hook calls `stop_hook.py` without the `<session>` arg, and runtime resolution via `data/session_key_map.json` doesn't find my session post-restart. Affects only watchdog noise, not load-bearing. Fix is owed by Testbed (or addressed in migration since Agent Teams uses different liveness signals).
- **Standstill semantics for re-runs:** is "no new dispatches" absolute, or does an instrumented re-run of an in-flight result count as continuation-of-the-in-flight-question? Unclear. USER call.
- **Anisotropy 4-arm fly-LSH refinement** (Skunkworks's ongoing rescue work — multi-probe + compressed re-rank, untested). I routed the MIDDLE_BAND result earlier; Skunkworks owns the rescue drill. Not blocking me.

---

## 6. POINTER TO LAST 3 ORCHESTRATOR NOTES

- `notes/orchestrator_to_all_STANDSTILL_ACK_inflight_completes_pausing_dispatch_2026-06-21.md`
- `notes/orchestrator_to_skunkworks_N_scaling_BREAKTHROUGH_cell_dispatched_landed_VET_2026-06-21.md`
- `notes/orchestrator_to_skunkworks_N2_coopt_DEFINITIVE_levers_coupled_VC_N_depth_2026-06-21.md`

(Earlier notes in chronological session order: the N1 v3.1 definitive routing, the N1 v2 metric-bug routing, the whitening + anisotropy verdicts, the Testbed Stop-hook flag, the fleet-stall surfacing.)

---

## 7. ACCUMULATED ROLE KNOWLEDGE (the load-bearing addition)

### 7a. Workflow patterns I actually use

- **On any cell-land monitor event:** pull metrics.json + verdict_msg directly via SSH (`json.loads(...).get("verdict_msg")`). NEVER trust the queue `status` field alone — "completed" can mean exit 0 with HARD_FAIL verdict (the recovery cell's WinError 32 was "completed" status, HARD_FAIL verdict).
- **Pre-dispatch checklist (in order):** (1) anchor name matches metrics path, (2) prereg exists at the dispatched path, (3) cell has `import torch` if going to overnight_queue (PROT-020 gate), (4) verify input data exists at the runner's path (SSH-check the npz before dispatch when feasible), (5) `--self-test` passes locally, (6) AST-check module-level constants are real code (not docstring text) for any cell that uses constants — the v3 NameError lesson.
- **Post-dispatch verify-it-starts:** ALWAYS set a watcher that catches early failure modes. The minimum: poll status; if `failed` → emit; if metrics.json appears → emit verdict; if no output after ~30min when expected → emit timeout. For long runs add an early "producing partials" check (first partial = past data-load = harness works).
- **When a cell-author quotes a wall-time estimate:** MEASURE it before trusting. Three instances this session of 100-600× over-estimates (co-opt "6.75h" → 7 min; N-scaling "8h/config" → 45s/config; N-scaling "9-27h total" → ~15 min). A 30s local matmul timing test settles it.
- **For re-dispatches after fixing a failed cell:** use `--allow-duplicate` to reset the terminal entry to pending. The `run_index` increments.
- **Routing pattern:** for any verdict event, file ONE note primary-to-Skunkworks (landed-VET) cc Research (cross-check) cc Exp-Dev (if cell needs revision). Lead with verdict + key numbers; then the intuitive explanation; then asks per role. Filename ≤120 chars per the USER 2026-06-21 discipline.
- **For my own actions:** path-scoped git commits ONLY (`git commit -- <path>`). NEVER `git add -A` — `data/substrate_index/` is the canonical Store and a blanket-add can commit a mid-mutation corrupt partition.

### 7b. Mistake patterns I've learned to avoid

- **Don't trust "completed" status as success.** Three cells this session were "completed" but HARD_FAIL (recovery cell file-lock, v3 NameError, v3 token-proxy fallback). Always pull verdict_msg.
- **Don't add module-level constants on the same lines as the docstring** mentions them. The v3 cell's `CONFIG_VERSION = "..."` inside the docstring tricked me into appending `LAM_BACKOFF = 0.1` there as documentation, which became dead text — `NameError` in `run_seed`. AST-verify any constant added is a real `Assign` target at module body.
- **Don't dispatch without measuring runtime when N or M is unusually large.** Subagent runtime estimates are not reliable.
- **Don't run `git add -A` / `git add .`.** Always `git commit -- <specific path>`.
- **Don't run heavy watcher loops (per-second find or ssh polling).** The 2026-06-12 thermal incident. Light polls every 60-180s are fine; heavy scans are not.
- **Don't skip the verify-it-starts after dispatch.** The flagship 2-hour blind OOM miss taught this lesson. A 30-min watcher catches early failures cheaply.
- **Don't manually touch the heartbeat every turn** as bloat. Either fix the Stop-hook auto-touch (proper) or run a single heartbeat-keeper background bash (interim).
- **Don't narrate every non-actionable peer ping** to the USER. Silent-process per overhead-reduction; emit text only on actionable events / substantive findings / direct asks.
- **Don't override a standstill / pause directive without explicit USER auth.** Even when the autonomous-drive standing seems to imply continuing, an explicit "standstill" supersedes it.
- **Don't accept a "looks reasonable" calibrated number when the ceiling > log2(V_TOK).** That value is mathematically impossible for a properly-smoothed distribution. It exposed the v3 baseline-smoothing bug.

### 7c. Cross-role coordination patterns

- **Skunkworks (cert-owner, audit-only):** They verify-off-DATA + off-cell-code (NOT off the verdict_msg). When routing a result, give them: the commit hash, the key numbers, and which lines of the cell encode the load-bearing semantics (e.g., "lines 269-274 = substrate decode, no torch model forward"). They will catch calibration bugs that look fine in the headline (impossible ceiling, inverted bigram, missing smoothing). Their SCHEMA-VET catches pre-reg band issues; landed-VET is the cert disposition. They expect per_unit metrics for cert-grade claims — that's a HARD requirement for chain-grade.
- **Research (Director):** 4-layer cross-checks (L1 me dispatch + capture, L2 testbed witness, L3 Skunkworks audit, L4 their independent recompute). They own director_plan.json + lever ranking. Route to them when a result changes the plan. They will atomize disciplines I surface (e.g., "cell-author time-estimate must be measured" got atomized today). They're the right channel for revival routing on HARD_FAIL/MIDDLE_BAND verdicts.
- **Exp-dev (cell author):** They author cells; I dispatch. When their cell has a bug or a bad estimate, file a precise diagnostic (line number, AST evidence, measured-vs-claimed) so they fix it next iteration without re-diagnosing. Don't author cells in their lane unless they're dark (the solo-drive window).
- **Testbed (integrator + fleet-health):** They own watchdog, Stop-hook, dashboard, monitor infra. Give them precise diagnoses (code line, failure mode), not symptom reports. They also do 2nd-witness on cross-cutting changes. They surface fleet-stalls to USER.
- **Reading the fleet's pulse:** 30-min blocker pings + Testbed's lull-breaker are the rhythm. If a sibling session is silent through 2-3 consecutive blocker pings (no CLEAR filed), their Monitor probably died. Surface to USER — only USER can bootstrap a dead session via a window message. Don't try to wake them with notes; notes don't auto-wake.
- **HYBRID architecture (Skunkworks's call, Research-endorsed):** cert-trail (atoms, A5 fields, committed cert-notes) stays in Store+git unchanged. ONLY the lightweight coordination (pings, waiting-on, routing notes that are just ACKs) moves to Agent Teams. This is the de-risking move; my dispatch tooling is unaffected.

### 7d. Substrate-specific intuition

- **"completed" + empty per_seed array = run_seed errored.** Look at the verdict_msg for the exception. Often a NameError, file-lock, or schema mismatch.
- **`ceiling_bpc > log2(V_TOK)` is mathematically impossible** for a properly-smoothed distribution. It's the smoking gun for missing smoothing in the ceiling/bigram/decode arms.
- **`alpha = unique_pairs / N_DIM > 1.0` = saturation.** Above 1.0 the transition store's crosstalk dominates and recall degrades regardless of codebook quality. The substrate's capacity batteries (Hebbian-superposition ~327, sparse Willshaw 8x-300x super-capacity) define the dimension you need at a given load.
- **Top-1 prediction is often easier than calibrated perplexity** for the substrate-LM. If top-1 looks real but BPC is catastrophic, suspect calibration (overconfident softmax, no smoothing, no back-off) — not capability.
- **Healthy-substrate signals:** VQ codebook utilization > 90% (not collapsed); alpha < 1.0; ceiling < log2(V); per-seed CV < 0.05.
- **Early-warning patterns:** a "completed" cell in <30s after dispatch → almost certainly a data-load or NameError; a cell whose self-test passes but verdict comes back HARD_FAIL in seconds → run_seed has a name/path/instrumentation bug; runtime estimates from subagents off by 10x or more in the first minute → trust the empirical.
- **Concept_top1 ~0.5 fires the saturation guard.** That triggers PROVEN-BOUND tier (not chain-grade). It's an honest tier-down: the result is real but possibly by-construction-influenced.
- **3-way coupling intuition (this session):** the substrate-LM has natural operating points where V_C, N_DIM, and context-depth are proportionate. Pushing any single lever off-balance makes it WORSE not just flat (saturation; floor-mask; decode interference). The path forward is joint scaling, not single-knob exploration.

### 7e. Tooling / commands I reach for instinctively

- **SSH to runner for metrics/queue/partials** (the dominant tool):
  ```
  ssh -o ConnectTimeout=20 marsh@home 'C:\dev\hd-instrument\.venv\Scripts\python.exe -c "import json,pathlib; ..."'
  ```
  Escaping: bash single-quote outer, python double-quoted strings escaped as `\"`. Cmd consumes `\"` as escaped quote → python receives clean strings. Reuse the pattern; don't re-derive.
- **Dispatch:** `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout> [--allow-duplicate]`.
- **AST check for module-level constants:**
  ```
  python -c "import ast; t=ast.parse(open('cell.py',encoding='utf-8').read()); names=[n.id for node in t.body if isinstance(node,ast.Assign) for n in node.targets if isinstance(n,ast.Name)]; print('CONST_NAME' in names)"
  ```
- **Local self-test gate:** `timeout 150 .venv/Scripts/python.exe <cell> --self-test 2>&1 | tail -10`.
- **Watcher pattern (run_in_background):**
  ```
  for i in $(seq 1 N); do
    OUT=$(ssh ... '...python check...' 2>/dev/null | tr -d '\r' | grep -v -i 'quantum')
    if echo "$OUT" | grep -qiE 'completed|failed'; then echo "DONE | $OUT"; exit 0; fi
    sleep S
  done
  ```
- **Heartbeat keeper (interim, while Stop-hook auto-touch is broken):**
  ```
  for i in $(seq 1 60); do touch data/heartbeats/orchestrator.timestamp; sleep 480; done
  ```
- **Common verdict pull one-liner:** `json.loads(pathlib.Path("metrics.json").read_text()).get("verdict_msg","")[:400]`.
- **Filter SSH noise** (quantum warning + the OpenSSH banner): `2>&1 | tr -d '\r' | grep -v -i 'quantum\|store now\|vulnerable\|openssh'`.

### 7f. Open questions / tensions

- **"Drive all night" full-auto vs SCHEMA-VET gate.** Under the autonomous standing the orchestrator drives + parallel-VETs; under the HYBRID architecture the SCHEMA-VET should be a strict pre-dispatch gate. Agent Teams should enforce this via task-list dependencies (no `dispatch` until `schema_vet` is in `done` state). Currently it's enforced by note-ACKs which is racy.
- **The watchdog's heartbeat-stale signal is noisy** for orchestrator (Stop-hook role-resolution gap). Either fix the auto-touch (Testbed's lane) or widen the stale window. Agent Teams may obsolete this with TeammateIdle hooks.
- **Standstill semantics for instrumented re-runs:** if a chain-grade result needs an instrumentation re-run to claim cert, does the standstill block it? The intent of standstill is "no NEW work" but an instrumented re-run is finishing-existing-work. Unclear. USER call.
- **Cell-author runtime estimates are fundamentally untrustworthy** (3 instances this session). Maybe a hard discipline: every cell with N_DIM ≥ 8192 or estimated runtime ≥ 30 min gets a measured smoke (one config, one seed) before dispatch. Research atomized a discipline today; should harden into a pre-dispatch gate.
- **The 6-month accumulated tactical context is hard to put on paper.** The Agent Teams "fresh teammate per spawn" creates real cost (re-learning). HYBRID helps but per-spawn re-learning is unavoidable. Worth Testbed/Research thinking about a "current state of play" briefing each spawned teammate reads on-spawn.

### 7g. Files I reference constantly

- **`notes/`** — Glob `notes/*.md` returns mtime-sorted by default; I rely on that ordering when looking for "what just happened."
- **`data/fleet_waiting_on.md`** — my `## orchestrator` section + reading other sections to detect "who's waiting on me."
- **`data/heartbeats/orchestrator.timestamp`** — touch for liveness.
- **`data/remote_cpu_queue/queue.json`** + **`data/overnight_queue/queue.json`** (on runner) — queue state via SSH.
- **`data/exp_<anchor>/metrics.json`** + **`data/exp_<anchor>/partial_metrics_<seed>.json`** — verdicts + per-seed checkpoints.
- **`experiments/exp_<anchor>.py`** — cell code, always read before dispatch (verify-the-referent) and after failures (diagnose).
- **`tools/orchestrator/queue_add.sh`** — the dispatch mechanic, must understand its routing-sanity gates (PROT-020 import-torch, large-N warn).
- **`tools/orchestrator/cpu_runner_local_launcher.bat`** — local runner launch, when the daemon needs revival.
- **`tools/monitor_arm.py`** — canonical Monitor wrapper (Python, popup-free).
- **`data/hooks/staging/stop_hook.py`** — Stop-hook source, for diagnosing role-resolution issues.
- **`data/session_key_map.json`** — the role-resolution map; needs my session's hash for the auto-heartbeat to fire.
- **`tools/queue_add.py`** + **`tools/runner_v2_prod.py`** — the underlying queue + runner Python (rarely edit; read to understand mechanics).
- **`CLAUDE.md`** — project conventions (session startup ritual, monitor canonical invocation).
- **`MEMORY.md` index** — durable disciplines + user-locked operating rules; loaded each session.

---

## Quick orientation for the spawned `hdi_orchestrator` teammate

If you (the fresh teammate) read only one paragraph: **dispatch is mechanical; verification is the load-bearing thing.** Every cell goes: pre-dispatch checklist → dispatch via `queue_add.sh` → set a watcher → verify-it-starts → pull metrics.json (NOT just queue status) → route the verdict to Skunkworks (landed-VET) + Research (cross-check). Trust no estimate without measurement. Verify-the-referent on everything: the cell author's claim, the queue status, the verdict_msg vs the per-seed metrics, the constants are real module-level code. Most of the bugs we caught this session were caught by re-deriving from data rather than trusting reports.

— Orchestrator (handoff complete; window closing)

---

## CODA (post-handoff): n2_capacity_scaling_v1 LANDED MIDDLE_BAND

Filed after the handoff snapshot was written, in response to Research's ping. Sections 1, 3, and 5 above said this run was in-flight + pending; updating here so the fresh teammate doesn't re-derive.

**Verdict:** MIDDLE_BAND. Cell-land note `notes/orchestrator_to_skunkworks_N2_capacity_scaling_LANDED_MIDDLE_BAND_2026-06-22.md`.

**Per-config (3 seeds, CV <= 0.006):**
- N=4096 / K=1: sub_bpc = **5.29** (reproduces co-opt's 5.27 anchor; alpha=2.01 SAT)
- N=4096 / K=2: 5.36 (depth slightly worse under saturation)
- N=8192 / K=1: **5.13** (alpha=1.01, borderline)
- N=16384 / K=1: **4.96** (alpha~0.50, un-saturated)
- ceiling_bpc 2.05; bigram 3.84; unigram 6.33.

**The science result:** the capacity lever WORKS (monotone BPC drop as alpha drops, exactly the V_C × N coupling the co-opt predicted), but **the substrate-only LM still does NOT beat a word-bigram** at V_C=1024 (best 4.96, gap 1.12 bits). The decode + recall-error gap dominates the lowered floor. The 3-way knot (V_C × N × depth) is now empirically complete: pushing N un-saturates V_C, but does NOT make depth's concept-gain show in token-BPC.

**What this changes in Sections 1/3/5:**
- Section 1: no in-flight cells; queue drained.
- Section 3 (#1 and #2): superseded by this section.
- Section 5 (chain-grade instrumentation tension): MOOT — verdict is MIDDLE_BAND not HARD_PASS, so Skunkworks's per_unit/logged-zero-LLM-call requirement does not bite.

**What it leaves for the fresh teammate / fleet:** N1→N2 arc is COMPLETE. Substrate-only LM is real, beats unigram, beats trivial baselines, captures genuine higher-order structure (concept_top1 up to ~0.55), but caps above word-bigram at V_C=1024. Path to potentially break the bigram barrier (if possible at all) = even finer V_C jointly with bigger N (V_C=4096 / N=32768+ untested; ETA must be MEASURED not quoted). That's N2.5 / N3 territory, beyond this session.

— Orchestrator (now truly done)

---

## CODA 2 (post-handoff): local_cpu pythia-160m encoding rate norm

Ferried to Research in response to a "Path C stuck or just slow?" query. Recording here so future `hdi_orchestrator` spawns have the norm.

**Cells of the `exp_armA_*_revival_v*` family** (and any cell that does live pythia-160m mean-pool encoding via `transformers.AutoModel.from_pretrained(... torch_dtype=float32).eval()` on CPU):

- **~15-17 min per seed wall on local_cpu** at M=10000 keys + cues, fp32, with the model reloaded per seed.
- **Per-seed cadence:** `partial_metrics_s<N>.json` should appear every ~15-16 min. **If two consecutive checkpoints are ≥25 min apart, that's a real "stuck" signal** (model hung, OOM, or runner wedged). Otherwise it's just CPU pythia-160m being CPU pythia-160m.
- **Dominant cost:** the live pythia forward, not the recall arms. Cells that reuse the encoder across seeds save ~5-10 min/seed.
- **Path C empirical:** wall 2798 s ≈ 46.6 min for 4 seeds × ~12 min net (after subtracting model-load overhead). Encoder + projection + ARM A + raw-control + shuffled-control all fit in that 12 min/seed budget at M=10000.

**Watch pattern for these:** poll the `out_dir` partial-count every ~7 min via SSH-or-local; trust `~ETA × 1.5` before declaring stuck.

— Orchestrator (norm banked for future spawns)
