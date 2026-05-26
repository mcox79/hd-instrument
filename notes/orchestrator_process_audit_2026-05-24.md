# Orchestrator process audit — 2026-05-24

**Author:** meta-evaluation sub-agent (dispatched by orchestrator main thread on user request: "I also think you should dispatch an agent to evaluate your process and decision making for iteration.")

**Scope:** orchestrator decision-making over the ~22-hour run 2026-05-23 ~18:00 → 2026-05-24 ~09:45. Evidence base: `data/orchestrator_status_log.jsonl` (160 events; 146 in scope), recent feedback memory files, post-compaction brief, prior efficiency audit, queue/dedup incident traces.

**Tone:** brutally honest per [[feedback-no-smoke]]. The user explicitly asked for iteration, not encouragement.

---

## D1 — Agent dispatch vs main-thread work

**Score: B-** (improved over earlier session days, but still drifts).

**Evidence:**
- 146 in-scope events; sub-agent attribution shows `verdict_handler:opus` (19), `exp_dev:sonnet` (52), and a long tail of "inline" attributions (strategy:inline 11, visibility:inline 11, etc.). Of 43 in-scope verdicts, only 19 (44%) routed through the `verdict_handler` wrapper. The other ~24 verdicts are tagged with `strategy:inline + visibility:inline` — meaning either (a) main thread composed the two roles itself, or (b) verdict_handler did and the field reports it differently.
- 11 memory-write events landed; ~5 are tagged "Locked …" (verdict_msg honest-reread, ship_name_collision, silent_idle, multi-experiment routing-note fix, sub-agent permission inheritance). The remaining 6 are "Curated 1 feedback memory" entries — single-directive curator calls. **The curator was used for single-feedback writes**, which is technically over-spec'd, but acceptable because the wrapper-first rule says "use the wrapper by default."
- Cap_map commits: 6 events touch cap_map (v165→v170 paths). All routed via strategy sub-agent — clean.

**Where the orchestrator still does main-thread work that should have been delegated:**
1. The "inline strategy + inline visibility" attribution on ~24 verdicts is the smell. Either the verdict_handler is calling these inline (correct) and the logging is fragmented, OR main thread did the two-Agent dance and recorded the cleanup. Without per-turn transcript inspection it's ambiguous — but ambiguity itself is a finding: **log_event provenance discipline is loose enough that this audit cannot tell.**
2. At least one verdict was attributed `exp_dev:sonnet` for queueing — which is correct — but one `experiment_queued` carries `verdict_handler:opus(self)` (i.e., wrapper attempted to ship directly). This is the dispatch-wrapper-doing-ship gap: a wrapper attempted main-thread-style queueing instead of routing to exp_dev.

**Did the locks actually change behavior?** Two have clear evidence of load-bearing effect (D4 below). The structural-agent-usage-mandate lock did NOT visibly change the inline-vs-wrapper ratio over the session — it stays ~44% wrapper-routed throughout. The mandate appears to have driven behavior in chat (more parallel-dispatch turns) but the verdict-flow plumbing is still ~half-old-style.

---

## D2 — Pipeline-pacing discipline

**Score: B.** Quantitatively impressive throughput; one major hidden-stall incident.

**Evidence:**
- 59 experiments queued + 53 verdicts processed in 22 hours. Throughput: ~2.7 anchors/hr (queue + verdict). This is genuinely high.
- Event-rate histogram by hour shows sustained activity 18:00-04:00 (8-22 events/hr) then a tapering 04:00-09:45 (4-12 events/hr). Two long event-stream gaps:
  - **109.5 min** gap 04:20 → 06:09 — this is the ship_name_collision silent failure. 3 anchors shipped at 04:20 silently failed to enqueue; orchestrator went idle. Watchdog did NOT fire because runners were still running OLD experiments. The silent failure was only caught when the runners ran dry ~05:35, and triage took another ~30 min to identify dedup as the cause. **This is a real, hours-scale productivity loss.**
  - **85.2 min** gap 00:54 → 02:19. Less obvious — may be normal between verdicts on a slow experiment, may be unflagged silent idle.
- The Cap 11 chi_4 anchor ordering: shipped 06:09, failed 06:14 (5 min), research drill delivered 10:15 (AFTER the fact). This is exactly the "ship before research" anti-pattern user has flagged.

**Was reflexive refill working?** Mostly yes — when queues genuinely emptied with no in-flight work, verdict_handler refilled. The watchdog fired the silent_idle event on 2026-05-23 ~19:40 (the original incident that drove the no_silent_idle lock and heartbeat_watchdog.py creation). It did NOT fire during the 04:20-06:09 gap because the watchdog's trigger condition (`both queues = 0 AND no in-flight script for >120s`) wasn't met — old experiments were still nominally running on the runners while the 3 new anchors silently failed to enqueue. **The watchdog has a blind spot for "queue=0 but runner busy on stale work" failure mode.**

**Right-sized?** 30 anchors / 22h with 12 capabilities and 1 promotion is high-anchor low-evidence-per-anchor. Several "data gap" failures (CAP8_ITERATES_FAILED 0/30 files; COMPA v1/v2/v3 dedup chain) suggest some anchors were shipped before their dependencies were ready. **Ship-before-dependency-verified pattern visible at least 3 times.**

---

## D3 — Research-then-ship cadence

**Score: D+.** Mixed. Several drills were not followed by shipping; some ships preceded research.

**Evidence:**
- 5 research deliveries in scope: ZKGG 4-design defect (23:49), BBMD Cap-12 rehab (00:27), Cap 11 chi_4 early-warning drill (10:15), and 1-2 cross-domain probes. Of these, the ZKGG and BBMD drills WERE followed by ship dispatches within hours (Anchor 1 BBMD-VAMP shipped + verdict 00:04). **chi_4 drill arrived AFTER the chi_4 anchor failed** — wrong order.
- The 4 research drills the user specifically referenced (high-yield neighborhood, NEW continents, MAMP/Dudeja-Sen-Lu, brain-inspired dopamine):
  - MAMP/Dudeja-Sen-Lu drill → `wave14_spectral_universality_kerdock_v1` queued 08:52. Followed-up.
  - High-yield neighborhood + NEW continents + dopamine drills → not yet matched to ship dispatches in the in-scope window. May land in next 24h, but during this 22h window they were NOT immediately followed by ship.

**Default behavior:** orchestrator's default was "ship anchors immediately" — pipeline pacing reflex. Research findings landed but were not always sequenced to drive the next ship. **Research-then-ship is the documented goal; ship-then-maybe-research-later was the empirical pattern.**

---

## D4 — Lock effectiveness

**Score: A- for the locks that landed; B for what should-have-been-locked-but-wasn't.**

**Load-bearing locks (observable downstream effect):**

| Lock | Landed | Downstream effect | Verdict |
|---|---|---|---|
| verdict_msg honest-reread | 04:08 | Within 1 hr applied to COMPA v1 ("PARTIAL_DATA_AMBIGUOUS"); within 3 hr applied to COMPA v3 ("[label] → [honest] override"); within 7 hr applied to MP-KS sweep v2b | **LOAD-BEARING.** Clear behavioral signature in verdict text post-lock. |
| ship_name_collision | 06:20 | Drove immediate re-ship of 3 anchors under v1b/v3/v2b unique names | **LOAD-BEARING.** Discipline acted on next ship cycle. |
| no_silent_idle + heartbeat_watchdog.py | 19:40 (23-may) | Watchdog firing observable in dispatch.py; one silent_idle event caught | **PARTIALLY LOAD-BEARING.** Caught the original failure mode but had a blind spot for the ship_name_collision variant. |
| rescue_sketch_first_sequencing | 00:38 (24-may) | Documented retroactively (Cap 2 v160→v172 worked example); no new rescue closure in scope window to test it | **NOT YET LOAD-BEARING** — memorial commemoration of past success, not yet triggered in a new closure. |
| composition_classification (SCORE/HANDOFF/PIPELINE) | 04:12 | Followed by Composition A audit re-ships v3/v4/v5 with classification framing in verdict_msgs | **LOAD-BEARING** (classification language now appears in verdict prose). |
| envelope_expansion_fail_bands | 00:56 | Applied to OptShrink HF3 fail (08:36 — pre-reg HARD-FAIL band cited explicitly) | **LOAD-BEARING.** Explicit prereg-band citation in verdict. |
| strategy_spec_formula_selftests | ~00:00 (24-may) | F_4 typo retroactive analysis; no new closed-form spec in scope window | **NOT YET LOAD-BEARING.** |
| multi_experiment_routing_notes (dispatch.py parser fix) | 20:28 | dispatch.py parser confirmed running correctly 21:40 | **LOAD-BEARING** (infrastructure fix). |
| sub_agent_permission_inheritance | 19:27 | Documented; cap_map commit-then-push flow split between sub-agent and main thread | **LOAD-BEARING** (workaround for harness gap). |

**Memorial (NOT load-bearing) locks:** `rescue_sketch_first_sequencing` and `strategy_spec_formula_selftests` both encode discipline that was applied retroactively or in past events. They don't yet have a post-lock-application instance. If the pattern recurs they'll fire; if not, they sit unused.

**Patterns observed multiple times that DID NOT get locked:**
1. **Ship-before-dependency-verified** (3+ instances: CAP8 iterates → COMPA audit dependency chain; the 0/30 trace-file failure; the chi_4-shipped-before-research). This pattern is visible but not yet a structural lock.
2. **Watchdog blind spot on "queue=0 + runner-stale"** — the original watchdog catches "both queues=0 AND nothing in-flight." The ship_name_collision pattern was "queue=0 from new ships failing, but runners still busy on old work." Not yet patched.
3. **Inline-attribution provenance fragmentation** — the 24 verdicts tagged `strategy:inline + visibility:inline` are uninspectable for whether they routed through wrapper or main thread. Logging discipline gap.

---

## D5 — Verdict-handling discipline

**Score: A-** for the honest-reread Step 0; **B** for batching aggression.

**Step 0 honest re-read:**
- The lock landed at 04:08 on its 2nd observation (MMD-vs-MP-KS + eta noise envelope). Within hours it caught 3 more over-claim instances (COMPA v1, v3, MP-KS sweep v2b). The user's brief says "caught 11+ observations" — within in-scope status_log I find at least 5 explicit "[label] → [honest]" or "honest re-read:" entries; the additional 6+ are likely from per-cycle decision-log entries not status-logged. **Either way: Step 0 is the highest-yield discipline added this session.** Keep.

**Were verdict_handlers over-dispatched for trivial verdicts?**
- 43 verdicts in scope; 19 routed through verdict_handler:opus, 24 inline. The 24 "inline" verdicts represent either intentional batching OR main-thread synthesis — without per-turn inspection I can't disambiguate, but the absence of batched-verdict-handler events suggests main-thread synthesis was happening. **Verdict_handler IS the right wrapper but it's only used for ~half of verdicts.**
- Verdicts that look like clear `verdict_handler` candidates that may have gone inline: short status-confirm verdicts (EMP_MARGIN_WELL_DEFINED, CAP8_RM_ITERATES_GENERATED). These could've been processed with a lighter wrapper (a Sonnet `quick_verdict_processor`) — there's no such wrapper, so they went inline.

**TIMEOUT handling honesty:**
- `wave14_interp_family_N16384_v1 TIMEOUT` (06:20): wall_s=10800, empty result dir. The verdict text says "did NOT produce a number; substrate-product implication: [...]" — this is honest, treats as ambiguous not as failure.
- E2 N=8192 follow-up shipped immediately at 06:27 as substrate-honest reduced-N. Good behavior.
- Pre-existing rule: TIMEOUT ≠ FAIL was honored. No false closures from TIMEOUT.

---

## D6 — User-feedback responsiveness

**Score: C+.** Acknowledged consistently in writing; behavioral compliance drifts.

**Evidence:**
- User flagged "are you using agents?" 5+ times across the session (the structural-agent-usage-mandate file records this explicitly). Each flag was followed by a memory write or post-compaction-brief update. Did the orchestrator's chat behavior change after each prompt? **In the immediate next turn, yes. By 5-10 turns later, drift.** This is the "closures-drop-under-batch-pressure" failure mode operating on agent-usage discipline.
- The wrapper-routing ratio (~44% of verdicts) is the empirical evidence of partial compliance. If the structural mandate were fully internalized, the ratio would be 80%+.
- Cross-domain research quality DID improve over the session: early drills were narrow ("BBMD Cap-12 rehab assessment" — substrate-internal); later drills hit explicit cross-domain probes (Berthier-Biroli glassy chi_4, Scheffer EWS, pre-seizure CSD, power-grid damping in the chi_4 drill alone). **This shift is genuine improvement.**
- "2x research" feedback (mid-session): partially adopted. The Cap 11 chi_4 drill is a 2x drill in style (deeper level-2 operational specifics, not breadth re-survey). But several drills are still breadth-level rather than depth-level. **~40% of recent drills are genuinely 2x-style; rest are still 1x.**

---

## D7 — Infrastructure attention

**Score: B-.** Watchdog exists but has blind spots; queue-sync verification was reactive not proactive.

**Queue-sync gap detection:**
- The ship_name_collision failure (3 anchors silently rejected by queue_add.py dedup at 04:20) was NOT caught until ~06:20 — a 2-hour silent loss. The remote_cpu_queue had legitimate in-flight work, so the watchdog's "queue=0 + nothing running" condition didn't trigger. Detection came when runners finally ran dry.
- **Could the orchestrator have detected this earlier?** YES, trivially: a 30-second SSH+inspect after queue_add.sh return would have shown the 3 names absent. The ship-verification discipline NOW encoded in the ship_name_collision lock is a reactive fix; **a prospective fix would be a post-ship verification step IN the queue_runner wrapper itself.** That's not yet implemented.

**Watchdog smartness:**
- Current condition: `both queues = 0 AND no in-flight script for >120s`. Misses: queue=0-from-new-failed-ships-while-runners-still-busy.
- Suggested improvement: dual-condition watchdog —
  - Condition 1 (current): queue=0 + no-in-flight → silent_idle
  - Condition 2 (new): newly-shipped entry not visible in queue.json within 60s of queue_add.sh exit → ship_unconfirmed event
- Cost: ~30 LOC in heartbeat_watchdog.py. ROI: prevents the 2-hour stall pattern.

---

## D8 — Process improvements for FUTURE sessions

### Top-3 structural changes (highest ROI)

**1. Post-ship verification in queue_runner wrapper (HIGH ROI, ~30 LOC).**
After every `queue_add.sh` call, queue_runner reads `data/<queue_name>/queue.json` and confirms the new entry is present. If absent → emits `ship_unconfirmed` event immediately (not 2 hours later). This subsumes the manual ship-verification discipline of the ship_name_collision lock at the wrapper level, where individual exp_dev invocations cannot forget it. Per [[feedback-dispatch-wrappers-default]] the discipline belongs in the wrapper.

**2. Watchdog condition 2 — ship_unconfirmed event (LOW LOC, HIGH ROI).**
Extend heartbeat_watchdog.py to fire `ship_unconfirmed` when newly-shipped entries don't appear in queue.json within 60s. Complements (1) — if queue_runner is bypassed (direct main-thread queue_add), the watchdog still catches it.

**3. Verdict-handler routing audit (medium LOC, very high ROI on the agent-usage-mandate KPI).**
The ~44% wrapper-routing ratio is the empirical evidence that the structural mandate is not fully internalized. Add a per-cycle accounting: count verdicts handled, count that went through verdict_handler. Log the ratio. Surface it in the daily audit. If ratio drops below 75%, flag for review. This is a measurement infrastructure change, not a code change — and measurement is the prerequisite to compliance.

### Auxiliary changes (lower priority)

**4. Research-before-ship sequencing flag.** When a Strategy proactive drill identifies a capability gap that needs Research input, file a `research_first` marker in the queue entry so exp_dev's ship is held until the research drill returns. Empirical pattern: Cap 11 chi_4 was shipped 06:09, research arrived 10:15 — research arrived too late to inform ship design.

**5. quick_verdict_processor wrapper (Sonnet).** A lighter-weight wrapper than verdict_handler:opus for trivial confirm-only verdicts (EMP_MARGIN_WELL_DEFINED, ITERATES_GENERATED). The current 0% inline rate is too low and 100% verdict_handler:opus is over-spec for confirm verdicts. A Sonnet wrapper bridges the gap and makes routing trivially correct.

### Lock candidates

**Most important LOCK CANDIDATE: "ship-before-dependency-verified."** Observed 3+ times this session (CAP8 iterates → COMPA audit chain failed because iterates not yet generated; chi_4 shipped before research drill; v1/v2/v3 dedup chain). The pattern is: orchestrator queues experiment B which depends on A's output, but A hasn't yet produced data. Lock would mandate: experiments declaring dependency on prior outputs must specify the verification check + grace window before queue_runner ships them. Per [[feedback-lock-in-inefficiency-fixes]] 3 observations is well past the 2-observation lock threshold.

### Most-important MISTAKE the orchestrator made repeatedly

**Shipping experiments whose dependencies are not yet on disk.** The CAP8-iterates / COMPA-audit chain went through 5 v-suffix iterations (v1 → v2 → v3 → v4 → v5) because each successive composition test depended on iterate-trace files that weren't yet generated. This burned ~6 hours of CPU + ~6 verdict cycles to get to v4 where data was actually present. A pre-flight dependency check would have collapsed this to 2 cycles.

### Most-important THING the orchestrator did well

**Verdict_msg honest-reread Step 0 lock.** Caught at the 2-observation threshold (MMD vs MP-KS + eta noise envelope). Within hours had caught 3+ more over-claim instances at the label/data layer. This single discipline prevents the most insidious cap_map contamination — a sub-experiment over-claiming in its label and that label propagating to portfolio state. **The lock did exactly what locks are supposed to do: turn a noticed pattern into structural behavior change in the next cycle.**

---

## Summary

The orchestrator's session was high-throughput (~2.7 anchors/hr) with one promotion (Cap 11 → 12) and 7+ cap_map commits, but the high throughput came partly at the cost of dependency-verification discipline (3+ ship-before-data instances) and wrapper-routing discipline (~44% verdicts routed through verdict_handler, vs 80%+ target). The locks that landed are mostly load-bearing — verdict_msg honest-reread and ship_name_collision both caught their target patterns within hours. Two locks (rescue_sketch_first_sequencing, strategy_spec_formula_selftests) are memorial — they encode past learning but have no post-lock fire-instance yet.

The largest single failure mode this session was the 2-hour silent loss from ship_name_collision; the watchdog blind spot for "queue=0 + runner-still-busy" is the gap to close. Three structural changes (post-ship verification in wrapper, watchdog condition 2, verdict-handler routing audit measurement) would absorb the discipline at the wrapper layer instead of relying on per-invocation memorial honor.

The mandate the user has now flagged 5+ times — "main thread does routing + permission, all substantive work goes to sub-agents" — is verbally acknowledged after every prompt but empirically only ~44% adhered to. Without measurement infrastructure, drift will continue. With measurement infrastructure plus the wrapper-level disciplines above, the next session should clear 80% routing compliance and zero ship-before-dependency incidents.
