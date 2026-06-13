# exp_dev hand-off -- research: TOOLS-vs-MATERIALS + SYSTEMS-vs-RECORDS distinctions

**Filed-by:** research (Opus) 2026-06-13
**Trigger:** Research drill `notes/research_drill_philosophy_science_TOOLS_vs_MATERIALS_SYSTEMS_vs_RECORDS_distinction_USER_directive_3x_DONT_ACCEPT_OTHERS_LIMITS_2026-06-13.md` produced 3 substrate-novel claims (SR-1/SR-2/SR-3) and 5 cheap pre-registered cells to verify them.

**Pause state:** if `data/orchestrator_paused.flag` exists, do not queue. These cells are CPU-cheap and structural; safe to queue when resumed.

**Per [[feedback-no-experiment-design-in-prompts]]:** I am NOT designing experiments. The research note pre-registers cells with HARD-PASS / HARD-FAIL bands; exp_dev picks anchors using its own design autonomy.

## Anchor candidates (rank-ordered)

### 1. TM-LITERATURE-AUDIT (Tools-vs-Materials, highest priority)
- **Anchor pointer:** research note section (b) + (f), cell #1
- **Substrate-product reading:** verifies SR-1 substrate-novel claim ("load-bearing primitive class is empirically measurable") -- HIGH-EV positioning win if HARD-PASS, sharpens substrate-product canonical claim list.
- **Tier hint:** A (cheap structural; <1 CPU-hour for full atom-corpus reverse-index scan).
- **Why-now:** answers USER craftsman-analogy directive directly; closes Cycle 51 architectural drill; produces a measurable TOOL set substrate can publicly report.

### 2. SR-PROMOTION-PARTITION (Systems-vs-Records)
- **Anchor pointer:** research note section (b) + (f), cell #2
- **Substrate-product reading:** verifies SR-2 substrate-novel claim ("content-type gates separate promotion-vs-consolidation pipelines"). HARD-PASS = 8x partition-conditioned gap in promote-to-axiom probability.
- **Tier hint:** A-B (needs system/record classifier on ~1742 atoms + KP promotion measurement; 2-4 CPU-hours).
- **Why-now:** answers USER reframe of H3 directly; refutes-or-confirms whether substrate's existing KP+L6 pipeline already respects the system/record distinction or whether explicit content-type gating needs to be added.

### 3. TM-VS-CITATION-FREQUENCY (cheap follow-up to #1)
- **Anchor pointer:** research note section (f), cell #3
- **Substrate-product reading:** confirms USER's intuition (verbatim: "a book might be cited 1M times but might just be the FIRST book on topic; addition is extraordinarily foundational; different worlds"). Expected: <10% overlap of TOP-100-cited with TOOL set.
- **Tier hint:** A (cheap; piggyback on #1's reverse-index scan).
- **Why-now:** if TM-LITERATURE-AUDIT runs, run this in same cell.

### 4. SR-PATTERN-MINING-PROMOTION-RATE
- **Anchor pointer:** research note section (f), cell #4
- **Substrate-product reading:** confirms SR-3 unifying claim (RECORD->pattern->SYSTEM->TOOL bridge is the dominant promotion pathway). Expected: >=50% of recent Tier-5 methodology rules trace back to record-content pattern extraction.
- **Tier hint:** A (analyze last 30 days of Tier-5 mining outputs).
- **Why-now:** Tier-5 third-appearance projected Cycle 51 already provides data points; just needs counting.

### 5. TM-AND-SR-JOINTLY (the unifying cell)
- **Anchor pointer:** research note section (f), cell #5
- **Substrate-product reading:** SR-3 confirmed iff every capability primitive's dependency tree bottoms out in <=5 T0 TOOL atoms.
- **Tier hint:** B (needs full tier-ladder construction first; depends on #1 + #2).
- **Why-now:** ship after #1 + #2 land HARD-PASS.

## Context pointers (file paths, not summaries)

- Research note: `notes/research_drill_philosophy_science_TOOLS_vs_MATERIALS_SYSTEMS_vs_RECORDS_distinction_USER_directive_3x_DONT_ACCEPT_OTHERS_LIMITS_2026-06-13.md`
- USER reframe handoff that triggered this drill: `notes/exp_dev_to_research_REFRAME_systems_vs_records_NOT_universal_vs_field_USER_correction_to_H3_2026-06-13.md`
- `serves_capability` reverse-index implementation: `hdlab/` (see FINDINGS #18 Gap 1)
- KP + L6-PROOF promotion gate: substrate's existing promotion-engine code path
- Tier-5 metacognition mining: `tools/orchestrator/...` (Cycle 51 Tier-5 third-appearance projection)

## Contract

Exp_dev picks anchors from list above (own design autonomy). Pre-reg per envelope-fail-bands. Smoke gate. Ship via queue_add.sh. Post-ship REMOTE VERIFY. Self-test per formula-selftests. Honor pause flag.

Research is NOT prescribing thresholds beyond the HARD-PASS / HARD-FAIL bands already in research note section (b) + (c). Exp_dev may tighten or relax these per its own pre-reg discipline; if relaxed, log the deviation explicitly.

## Autonomy declaration

Exp_dev has full autonomy on: cell-order selection, smoke-gate threshold, ship-or-defer per pipeline depth, atom-corpus subset selection (full vs sample), whether to merge cell #1+#3 into one ship, whether to run cell #5 only after cells #1+#2 HARD-PASS or in parallel.
