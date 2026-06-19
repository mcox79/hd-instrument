# exp_dev hand-off — Path 1 token-level substrate K=128+ head-to-head vs GPT-2-small (GPT-quality reframe)

**Filed:** 2026-05-24 by orchestrator (inline-via-main-thread per orchestrator post-compaction brief Section 2 Agent dispatch unavailable in sub-agent context)

**WHAT** — design + ship the Path 1 token-level substrate generator at K=128 or
higher, and run head-to-head against GPT-2-small on a standard eval set. This is
the load-bearing capability test for the GPT-quality-generation Tier-1 reframe.
Substantial build (2-3 days build + GPU day); user flagged this may need to file
as **multi-cycle hand-off** — design + scaffold in this cycle, ship full
comparison in subsequent cycle(s).

**WHY (pointers, not summaries)**

- Reframe note: `notes/research_tier1_gpt_quality_reframe_2026-05-24.md` (read this first)
- Current substrate generation: byte-K=16 in v3 cap_map; the K=128+ jump is
  where the substrate-physics frameworks predict generation quality should
  meaningfully start matching transformer perplexity (per R16 capacity + R23
  coding rate)
- GPT-2-small reference: 124M params, ~10B tokens. Standard perplexity on
  WikiText-103 or equivalent.
- Path 3 (AGS scaling extrapolation) is the cheap answer; Path 1 is the
  expensive load-bearing answer. Both ship in parallel.
- Pause flag: ACTIVE (no pause) — confirmed at orchestrator cycle 16:20

**CONTRACT** — deliverable shape

- Design the token-level substrate generator at K >= 128 (you pick exact K).
  Decisions to make: tokenizer choice (BPE / WordPiece / SentencePiece /
  byte-pair pickup from GPT-2's own tokenizer); substrate dimension N;
  bundle structure for token-key mapping; readout mechanism for next-token
  distribution; training corpus + scale.
- Decide whether to scaffold + smoke this cycle and FULL-ship next cycle, or
  ship a smaller-K FULL this cycle to gather an interim data point.
- Choose head-to-head eval discipline: paired-evaluation (substrate and
  GPT-2-small same prompts/contexts); perplexity primary metric; qualitative
  generation samples secondary; ablations to taste.
- Pre-register HARD-PASS / HARD-FAIL gates against GPT-2-small perplexity (you
  decide thresholds; consider a banded scheme: HARD-PASS within 0.X ppl,
  MIDDLE-BAND within Y ppl, HARD-FAIL >Z ppl).
- Multi-seed at the comparison anchor.
- File queue entry note + decision log per standard discipline.

**AUTONOMY DECLARATION** — you decide:
- Anchor name(s)
- Multi-cycle decomposition (this cycle scaffolds; next cycle FULL — or
  alternative pacing)
- Tokenizer + K + N + corpus + scale
- HARD-PASS / HARD-FAIL gates + formula
- Queue choice (GPU for the FULL comparison; smoke + scaffold may be local /
  remote_cpu)
- Pre-registered prediction (which paths in the reframe note this updates)
- Verdict template

**Discipline pointers** (citations only — no verbatim re-statement):
- Per [[feedback-no-experiment-design-in-prompts]]: autonomy is declared above
- Per project_research_playbook item 5 (verify-lit): K=128+ build must verify
  against established sequence-modeling-via-VSA literature, not just substrate
  internal precedent
- Per [[feedback-for-you-tab-primary-channel]]: status_log entry on hand-off
  consumed and on scaffold smoke completion (medium importance) and FULL ship
  completion (high importance)
- Per PROT-005: exp_dev /loop is the cadence; given multi-cycle scope, file the
  cycle-1 scaffold + decision log this cycle, then re-pickup the FULL in a
  subsequent cycle

**Return format**: one-line summary at end of decision-log entry — anchor
name(s), queue, cycle-1 vs cycle-2 split, ETA, pre-registered prediction in one
line. Main thread relays to user via routine status_log update.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
