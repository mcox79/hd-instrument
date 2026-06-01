# exp_dev hand-off — Path 3 AGS scaling-law extrapolation (GPT-quality reframe)

**Filed:** 2026-05-24 by orchestrator (inline-via-main-thread per orchestrator post-compaction brief Section 2 Agent dispatch unavailable in sub-agent context)

**WHAT** — design + ship the Path 3 AGS scaling-law extrapolation anchor (or
small batch of anchors) for the GPT-quality-generation Tier-1 reframe. The goal
is to measure substrate perplexity at multiple (N, K, M) points, fit an
AGS-style scaling curve, and extrapolate to compute-matched GPT-2-small. This is
the user-flagged cheapest answer to the GPT-quality question (Bet L territory).

**WHY (pointers, not summaries)**

- Reframe note: `notes/research_tier1_gpt_quality_reframe_2026-05-24.md` (read this first — has all five paths + decision rationale)
- v1 cap_map ❌ entry (line 122) `notes/substrate_capability_map.md`
- v3 grounded entry (line 425) `notes/substrate_capability_map.md` — 🟢 PARTIAL reading
- AGS framework background: scan recent strategy_decisions for "AGS" + cap_map for capacity-scaling discussion
- GPT-2-small compute envelope: standard reference point (124M params, ~10B tokens train)
- Substrate-physics frameworks: R16 superposition capacity / R23 coding-rate bounds / R26 free-probability composition / R29 noise-tolerant readout — none predict hard quality ceiling
- Pause flag: ACTIVE (no pause) — `data/orchestrator_paused.flag` absent confirmed at orchestrator cycle 16:20

**CONTRACT** — deliverable shape

- Pick (N, K, M) grid spanning at least 1 decade in each axis (you decide
  resolution, multi-seed count, smoke-vs-FULL split).
- Pick a fit form (you decide: power-law, broken-power-law, logarithmic with
  saturation, etc.). Multi-seed at each point; report R^2 + extrapolation CI.
- Pick HARD-PASS / HARD-FAIL gates against compute-matched GPT-2-small
  extrapolated perplexity (you decide thresholds; calibrate against published
  GPT-2-small perplexity on a standard byte/token corpus).
- Ship to overnight_queue or remote_cpu_queue as you judge fit; GPU if needed.
- File a queue entry note `notes/exp_dev_to_queue_path3_ags_<date>.md` documenting
  the design choices and pre-registered prediction.
- Compose a self-test + smoke run before FULL ship per the standard discipline.

**AUTONOMY DECLARATION** — you decide:
- Anchor name
- (N, K, M) grid points + spacings
- Multi-seed count + seed list
- Fit form
- HARD-PASS / HARD-FAIL thresholds + formula
- Queue choice (overnight / remote_cpu / GPU) + ETA
- Smoke vs FULL split + sequencing
- Verdict template
- Number of anchors (single-anchor with multi-point sweep, or batch of anchors)

**Discipline pointers** (citations only — no verbatim re-statement):
- Per [[feedback-no-experiment-design-in-prompts]]: this prompt declares
  autonomy; do not expect numerical specifications from main thread
- Per [[feedback-verify-implementations]]: AGS scaling form should match the
  cited literature (Ahn-Goh-Sommer or equivalent) — audit that mechanism matches
  the paper, not just the name
- Per project_research_playbook: pre-registration, 5-seed + Bayes factor,
  bandit, design-space matrix
- Per [[feedback-for-you-tab-primary-channel]]: write a status_log entry with
  plain_language + importance when the hand-off is consumed and the anchor(s)
  ship
- Per PROT-005: exp_dev /loop is your cadence; act on this within next 1-2 cycles

**Return format**: brief one-line summary at end of your decision-log entry —
anchor name(s), queue, ETA, pre-registered prediction in one line. Main thread
relays to user via routine status_log update.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
