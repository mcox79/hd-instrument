# Director Delegation Audit — 2026-08-12 session (139818eb)

Read-only forensic pass over `139818eb-7f83-457e-928d-a8db02a0214d.jsonl` (1493 lines,
2026-08-12T14:49:29Z -> 23:37:57Z, span 31,723s / 8h48m). All main-thread events
(`isSidechain:false`) counted directly from the transcript; sidechain (in-agent) events
excluded from main-thread totals. No self-assessment text was used as evidence.

## 1. Main-thread tool calls
Total 162 main-thread tool_use calls: Agent 42, PowerShell 34, Read 21, Bash 18,
SendMessage 12, Edit 10, Write 7, Glob 4, WebSearch 4(+2 dup lines), Grep 3, ToolSearch 2,
WebFetch 2, update_session_meta 2, Skill 1.
Assistant turns with >=3 tool calls before replying: **0 / 500** turns (max observed = 1
tool call per turn). The director does not batch main-thread tool calls; it is
single-call-per-turn throughout, before and after the protocol change.

## 2. Agent dispatches
42 total, all after line 320 (0 before). subagent_type: hdi_exp_dev 12, hdi_research 11,
hdi_skunkworks 8, general-purpose 5, hdi_testbed 5, hdi_orchestrator 1.
model specified: sonnet 23 / opus 19 (100% specify a model — none left default).
run_in_background: **True for all 42/42** — no foreground Agent dispatches found.
Return latency for the Agent tool_result itself (ack, not agent completion): median ~0.1s,
i.e. dispatch truly hands off and does not block the caller.

## 3. Time — wall-clock reality
Total session 31,723s. Main-thread tool-exec time (sum of call->result latency, real
blocking on synchronous tools): **3023s (9.5% of session)**. Generation-time proxy (gap
before each text-only assistant reply; correlates r=0.918 with reply char length, i.e. this
genuinely tracks output-length-driven latency, not idle wait): **1305s (4.1%)**. Combined
measured main-thread "work" ≈ 4328s / 13.6% of the session; the remaining ~86% is gaps not
attributable to a synchronous main-thread call (background-agent wait, notification
latency, or genuine idle — this transcript alone can't fully separate those).

Top 5 time sinks (main thread, synchronous tool call->result):
1. 578.9s — PowerShell, line 403->405, "Inspect the five disabled scheduled tasks" (15:53-16:02, **14 min after** the delegation protocol was first written at line 320/15:39)
2. 567.6s — PowerShell, line 402->404, "Finish archiving watchdog files with robocopy" (15:53-16:02, same burst as #1, back-to-back)
3. 544.9s — PowerShell, line 313->317, "Archive watchdog ping files out of notes" (15:29-15:38, **before** the protocol write)
4. 193.7s — Bash, line 327->332, "Time the capability registry audit" (15:40, right after protocol write)
5. 192.0s — Read, line 328->333 (large-file read paired with #4)
Together items 1-3 alone = 1691.4s = **56% of all main-thread tool-exec time**, and 2 of
the 3 fired *after* the director had already written the delegation protocol into
session_start_hook.py.

session_start_hook.py delegation-protocol edits: line 320 (15:39:13, first Write), line 341
(15:43:58), line 584 (16:57:51), line 1070 (20:06:21) — 4 iterations, ~4h27m apart from
first to last.

## 4. Before/after the protocol (split at line 320, the first write)
- **Before** (14:49-15:39, 50 min): 47 main-thread tool calls, 0 Agent dispatches, 879.9s
  shell-exec blocking = **29.3% of that segment's wall time** spent blocked in foreground
  Bash/PowerShell.
- **15:39-20:06** (after write, through the 3 follow-up edits, ~4h27m): 1656.1s shell-exec
  blocking over ~16,020s segment = **10.3%** — improved, but two of the three biggest
  single blocking calls in the whole session (items 1-2 above) happened *in this window*,
  minutes after the first protocol write.
- **After 20:06** (last edit, through 23:38, ~3h32m): shell-exec blocking = **9.7s total
  over 3 calls / 0.08% of segment** — effectively zero. This is the only segment where the
  protocol visibly held.
- **Verdict: main-thread blocking dropped, but only after the 4th edit, ~4.5 hours and two
  more ~10-minute self-inflicted blocking incidents after the director first claimed to
  have fixed it.** The first write did not stop the behavior it was meant to stop.

## 5. Character counts (verbosity hypothesis)
Director text replies: n=181, median 732 chars, max 5887.
- First half of session (lines 0-746): n=95, median **290**, sum 111,038 chars, gap-sum 572s.
- Second half (lines 747-1492): n=86, median **1394 (4.8x higher)**, sum 122,115 chars, gap-sum 733s.
Director Agent-prompt lengths: n=42, median 3309 chars, max 5051.
Reply length vs preceding wall-clock gap: **Pearson r = 0.918** — strongly linear. This
directly supports the live hypothesis: verbosity is not free, it costs real thread time in
close to 1:1 proportion to length, and the director got *more* verbose per reply (not less)
in the second half even as tool-call counts and shell-blocking fell. Total generation-time
did not drop (572s -> 733s) — fewer replies, each much longer, roughly wash out.

## 6. WebSearch/WebFetch in main thread
6 calls total (WebSearch x4, WebFetch x2), all in the **first half**: lines 228-239
(15:17:16-15:17:33Z) and lines 735-736 (17:42:42-17:42:43Z). All predate or coincide with
early protocol iterations; **zero WebSearch/WebFetch in main thread after 17:43**, i.e.
after that point research was in fact routed to hdi_research (11 dispatches, all
background). This one sub-behavior did change and stuck.

## 7. Large tool_result payloads landing in main thread (>20k chars)
7 occurrences, all `Read` of large files, all in main thread (none delegated to Explore/
general-purpose for extraction): line 876 (46,820 chars, 18:37:45), line 867 (41,689,
18:37:01), line 834 (37,379, 17:59:37), line 199 (29,800, 15:14:37), line 55 (24,847,
14:55:05), line 39 (24,818, 14:54:36), line 556 (24,323, 16:55:58). Note 3 of 7 are in the
*second half*, well after the protocol write — large self-reads were never delegated away.

## Bottom line (numbers, not narrative)
- Main-thread work did **not** cleanly drop the moment the protocol was written; it dropped
  gradually over 4 edits and ~4.5 hours, with a ~1146s (19-minute) regression 14 minutes
  after the first write. It only reads as "fixed" from ~20:06 onward (last third of the
  session).
- Top 3 time sinks by wall-clock are **all foreground Bash/PowerShell housekeeping**
  (watchdog/scheduled-task archiving), not Agent orchestration overhead — 1691s, 56% of all
  measured main-thread tool-exec time, concentrated in one 33-minute window (15:29-16:02).
- **Tool use, not verbosity, is the bigger raw-second cost** (3023s tool-exec vs 1305s
  generation-time), but verbosity is the one that got *worse* over the session (median
  reply length 4.8x higher in the second half) while tool-blocking got better — so as a
  *trend*, verbosity is the active risk, not a fixed cost that's already been addressed.
- Defensible main-thread work: WebSearch/WebFetch cleanly stopped after 17:43 (fully
  delegated to hdi_research thereafter); all 42 Agent dispatches used
  run_in_background=True with an explicit model, so orchestration itself is not blocking —
  the blocking is self-executed shell housekeeping and long self-reads that were never
  handed to an agent.
