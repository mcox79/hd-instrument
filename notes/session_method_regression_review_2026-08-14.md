# Session method regression review — last ~7 days of transcripts

**Scope:** all 9 Claude Code transcripts under `C:/Users/marsh/.claude/projects/{d--AI, D--AI-hd-instrument}` (~4.1 GB), streamed line-by-line, bucketed **per day from per-record timestamps** (sessions span days and are resumed, so per-session buckets are wrong).
**Method:** `D:/AI/hd-instrument/scratch/transcript_metrics.py` + `user_msgs.py` (throwaway, gitignored). Counters only; no file loaded into context.
**Status:** READ-ONLY review. No code, config, or experiment touched.

---

## TL;DR

The user's instinct is **correct, and datable**. But the cause is only half the model.

On **2026-08-12** two things changed *on the same day*:

1. **Model:** `claude-opus-4-8` → `claude-opus-5`, first Opus 5 record at **2026-08-12T15:14:09Z**.
2. **Harness:** entrypoint `claude-vscode` v2.1.198 → `sdk-cli` v2.1.221 (Nimbalyst). The user announces the move himself at 08-12T14:51: *"I have a max account on anthropic I'd like to log into here... I'm transitioning from VS Code, and the chat there is called 'Research'."*

The regression the user actually *feels* is **the main thread became blocking**. That is the single cleanest signal in the whole corpus:

> **Lock-out complaints in user messages: 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 — across 4,203 user messages from 07-28 to 08-11. Then 12 on 08-12 and 4 on 08-13.**

Not a drift. A step change, on migration day.

The *science* did not regress. Commits/day are flat (69/65/79/71/78/59 for 08-08..08-13), experiment directories touched per day are **higher** in the recent window (53/59/78/33/54 for 08-09..08-13 vs 14–51 for 08-01..08-08), and pre-registration language per turn is at its **all-time high** on 08-13. What collapsed is the *interaction loop*, not the output.

---

## Per-day metric table

| day | env | model | main-thread turns | out-tok (M) | main tools | Agent calls | deleg ratio | med reply (chars) | p90 user-gap (min) | gaps >30m | lock-out complaints |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 | VS Code | opus-4.8 | 8327 | 22.5 | 2687 | 88 | 0.033 | 317 | 6.3 | 4 | 0 |
| 2026-07-30 | VS Code | opus-4.8 | 18379 | 33.4 | 7477 | 170 | 0.023 | 260 | 5.9 | 6 | 0 |
| 2026-07-31 | VS Code | opus-4.8 | 13075 | 25.5 | 4980 | 231 | 0.046 | 277 | 5.3 | 9 | 0 |
| 2026-08-01 | VS Code | opus-4.8 | 9139 | 17.9 | 3005 | 117 | 0.039 | 252 | 5.4 | 7 | 0 |
| 2026-08-02 | VS Code | opus-4.8 | 4205 | 9.2 | 1373 | 88 | 0.064 | 352 | 11.9 | 3 | 0 |
| 2026-08-03 | VS Code | opus-4.8 | 1898 | 5.2 | 472 | 103 | 0.218 | 962 | 15.2 | 0 | 0 |
| 2026-08-04 | VS Code | opus-4.8 | 3087 | 6.3 | 1033 | 88 | 0.085 | 309 | 12.6 | 5 | 0 |
| 2026-08-05 | VS Code | opus-4.8 | 9257 | 20.5 | 3057 | 285 | 0.093 | 304 | 7.8 | 3 | 0 |
| 2026-08-06 | VS Code | opus-4.8 | 6193 | 14.7 | 1960 | 202 | 0.103 | 345 | 12.0 | 9 | 0 |
| 2026-08-07 | VS Code | opus-4.8 | 2638 | 7.1 | 812 | 63 | 0.078 | 389 | 22.2 | 7 | 0 |
| 2026-08-08 | VS Code | opus-4.8 | 2122 | 5.7 | 604 | 81 | 0.134 | 581 | 24.6 | 5 | 0 |
| 2026-08-09 | VS Code | opus-4.8 | 5338 | 16.2 | 1327 | 171 | 0.129 | 466 | 11.2 | 14 | 0 |
| 2026-08-10 | VS Code | opus-4.8 | 2762 | 8.9 | 680 | 123 | 0.181 | 530 | 18.2 | 12 | 0 |
| 2026-08-11 | VS Code | opus-4.8 | 1118 | 3.5 | 255 | 38 | 0.149 | 416 | 31.1 | 12 | 0 |
| **2026-08-12** | **MIXED** | **4.8→5** | 880 | 2.2 | 179 | 60 | 0.335 | 421 | 19.2 | 8 | **12** |
| **2026-08-13** | **Nimbalyst** | **opus-5** | 627 | 1.5 | 55 | 125 | **2.273** | **1084** | 15.2 | 4 | **4** |

*deleg ratio = Agent-tool calls ÷ main-thread Bash/Read/Grep/Edit/Write/Glob calls.*

### Method markers, normalised per 100 main-thread turns

| day | brain-fid | prereg | controls | rework | HARD_PASS | HARD_FAIL | HP:HF |
|---|---|---|---|---|---|---|---|
| 2026-07-31 | 0.96 | 0.68 | 1.95 | 1.04 | 42 | 30 | 1.40 |
| 2026-08-05 | 2.77 | 0.92 | 3.19 | 2.45 | 165 | 67 | 2.46 |
| 2026-08-06 | 4.10 | 1.86 | 4.12 | 1.99 | 166 | 164 | 1.01 |
| 2026-08-09 | 7.06 | 1.11 | 6.86 | 1.52 | 196 | 133 | 1.47 |
| 2026-08-10 | 6.26 | 0.65 | 8.62 | 1.34 | 92 | 78 | 1.18 |
| 2026-08-11 | 5.37 | 0.36 | 10.38 | 1.79 | 27 | 35 | 0.77 |
| 2026-08-12 | 2.84 | **2.39** | 5.68 | **4.43** | 36 | 12 | 3.00 |
| 2026-08-13 | 2.55 | **5.10** | 9.41 | **3.99** | 9 | 14 | 0.64 |

---

## Verdict

### Real regression — YES, but narrowly, and it is an interaction-loop regression

**1. The main thread stopped being available to the user.** (strongest evidence)
Zero lock-out complaints in 4,203 user messages up to 08-11; 16 in the 365 messages of 08-12/08-13 — a rate of 0.0% → 4.4%. The user's language escalates accordingly:
- 08-12T17:38 — *"i've been killing them because it has locked up the main thread... i think you're wrong these have absolutely been locking the main thread up"*
- 08-12T17:42 — *"backgrounding agents are absolutely not supposed to block the main thread - look this up, are you just doing it wrong?"*
- 08-12T23:34 — *"you were just locked up and I had to interrupt you to get you to respond"*
- 08-13T00:03 — *"you need to fucking figure this out it's infuriating. I KNOW you can run agents in the background."*
- 08-13T00:46 — *"this serial operation is ridiculous."*

Explicit "I interrupted / I killed it" mentions: **0–2 per day for two weeks, then 5 (08-12) and 10 (08-13).**

**2. Main-thread work volume collapsed ~15x.** Output tokens 16.2M (08-09) → 2.2M (08-12) → 1.5M (08-13). Main-thread tool calls 3,057 (08-05) → 55 (08-13). Turns 9,257 → 627.

**3. Replies got long while turns got rare.** Median main-thread reply 252–420 chars for most of the window → **1,084 chars on 08-13** (2.6–4x). The old rhythm was many short turns; the new one is few long monologues. Long replies are exactly what locks the user out.

**4. Rework language roughly doubled**, 1.3–2.5 per 100 turns → 4.43 / 3.99. *Caveat: 08-12/08-13 were explicitly a cleanup/audit phase (registry tighten, "foundation validation overstated", encoder landed correction), so elevated correction language is partly the assigned task, not necessarily degraded work. This one is ambiguous.*

### NOT a regression — the following got better or held

- **Experiment throughput is up.** exp dirs touched/day: 08-09..08-13 = 53/59/78/33/54, vs 08-01..08-08 = 14/40/51/26/40/21/32/5.
- **Commit rate is flat.** 69/65/79/71/78/59 across 08-08..08-13.
- **Pre-registration discipline is at its peak.** 5.10 prereg mentions per 100 turns on 08-13, the highest of the entire 17-day window (prior best 1.86).
- **Control declaration is near-peak** (9.41/100, second only to 08-11's 10.38).
- **Delegation ratio is 15–100x higher** (0.023–0.15 → 2.27). The Director now delegates rather than hand-rolls — which is what the standing discipline asks for.
- **The user's corrective-message rate actually fell** on the Opus 5 day: 36.1% (08-09) and 30.6% (08-07) under Opus 4.8, vs 14.6% on 08-13.

### Two hypotheses tested and rejected

- **"Context pressure from huge transcripts."** REJECTED. The 3.16 GB and 895 MB files are big because they are *long-lived sessions dating to 2026-05-31*, not because recent days are bloated. Per-day bytes on 08-12/08-13 are 8.2 MB and 6.5 MB — among the *smallest* in the window. Max per-request context is flat at ~0.92–1.0M tokens every single day; it did not rise.
- **"Gradual process drift."** REJECTED for the lock-out symptom. It is a step function on 08-12, not a slope. (There *is* a milder, separate slope: p90 user-gap rose from ~5–6 min in late July to 22–31 min over 08-07..08-11, still under Opus 4.8/VS Code. That is a real but smaller pre-existing drift toward longer unattended stretches.)

### Model vs harness — honestly, NOT separable from this data

Both changed within 23 minutes of each other on 08-12 (harness at ~14:51, model at 15:14). The `sdk-cli` + Opus-4.8 window is 23 minutes long — far too short to be a fair test. **Attribution to the model alone is not licensed.**

What evidence there is points more at the **harness**: every user complaint and every attempted fix is about background-subagent execution semantics, not reasoning quality. The user never says "your answers got worse" — he says the thread blocks. Under VS Code the user also had a 30-minute self-drive cron (*08-12T21:17: "I used to use a 30min cron to keep the main agent moving - even overnight"*) that did not survive the move. The user separately flags that the new environment initially had the wrong picture of the project entirely (*08-12T16:25: "I think you're not actually interfacing with the right substrate?... look at the recent conversation from VS code - what we have now is way more capable"*).

**Net:** most of the felt regression is **migration cost** — lost crons, lost dispatch wiring, foreground-blocking subagents, and a fresh session with no accumulated context — landing simultaneously with a model swap that then absorbed the blame.

---

## Ranked practices to reinstate

1. **Never block the main thread. Default every dispatch to background.** The single metric that went from 0 → 16 complaints. Sub-agents must be launched with background execution and the Director must return to the user immediately. This is the whole ballgame; everything else is second order.
2. **Restore the 30-minute self-drive cron.** It existed under VS Code and kept the loop moving overnight without holding the thread. It did not survive migration. The user asked for it back explicitly on 08-12T21:17.
3. **Restore the short-turn rhythm.** Target a median main-thread reply near **300 characters**, not 1,084. The best-throughput days (07-30, 08-01, 08-05) had 250–305 char medians and 3,000–7,500 main-thread tool calls. Report in short beats; put the long prose in a note file and link it.
4. **Check in at ≤10 minutes.** p90 user-gap was 5–6 minutes on the strongest days; it is now 15–31. Emit a one-line progress beat before any step that will exceed ~10 minutes.
5. **Keep the delegation gain, but stop hoarding the residue.** Delegation ratio 2.27 is good and should stay. The failure mode on 08-12 was mixed: heavy delegation *plus* the Director still personally running long tasks (memory trimming, note listing) — user, 08-13T15:38: *"trimming down the memory should NOT be a task that you do."*
6. **Pin sub-agent models deliberately.** The user caught Sonnet being used where the established convention is Opus for research/director work (08-13T14:38: *"do you really want all those subagents to be sonnet?? didn't we evaluate these and determine what models are ideal?"*). Re-assert the standing rule: research/exp_dev = Sonnet, skunkworks/director = Opus.
7. **Re-run the environment-parity audit once.** Confirm every capability that existed in the VS Code session (crons, hooks, hdi_* dispatch, remote queue, heartbeat watchdog) is live under sdk-cli. Migration silently dropped at least the cron; assume it dropped more.
8. **Hold the gains that are genuinely up** — pre-registration (5.10/100, best ever) and control declaration (9.41/100). These are not the problem and should not be traded away in the rush to fix pacing.

---

## Caveats on this analysis

- Sub-agent transcripts are **not** in these files (`isSidechain` is 0 in every record). Post-migration main-thread counts therefore *understate* total work, because work moved into invisible sub-agents. This is why "main-thread output tokens fell 15x" must NOT be read as "15x less work done" — commit and experiment-artifact counts say otherwise.
- "Lock-out", "interrupt", "rework" and method-marker counts are regex heuristics over message text; they are directionally reliable at these effect sizes (0 → 16) but not exact.
- 08-13 is a single day of Opus 5 under a settled harness. Any model-quality claim from n=1.5 days, confounded with a migration, would be exactly the kind of narrow-failure-to-impossible generalisation the standing disciplines forbid.
