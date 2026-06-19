# Efficiency rollout — 2026-06-02

User auth: "start implementing the efficiency wins. all of them. anything with medium risk we should track carefully the first few runs"

Source: `notes/efficiency_review_2026-06-02_thread.md` (this turn's analysis).

## Goals
Reduce exp_dev + verdict_handler waste without cutting corners on:
- NEUTRAL classification
- Honest re-read
- PROT-018/019/021/022 compliance
- Pre-flight script-exists + queue-name uniqueness
- Smoke verification

## Items + status

| # | Change | Impact | Risk | Status | First-run verification |
|---|---|---|---|---|---|
| 6 | `data/blocked_items.json` global skip list | -200 char/prompt | very low | LANDED | Visual check next dispatch |
| 7 | `preregs/_template.md` jinja-style template | -50% prereg write | very low | LANDED | Diff vs hand-written |
| 2 | `notes/pre_context_pruning_recipe_2026-06-02.md` | -40% exp_dev input tokens | very low | LANDED | Token count delta over 3 cycles |
| 3 | `tools/ship_anchor.py` helper (smoke+queue+verify) | -10-20s/anchor, -2 SSH RTs | low | LANDED (untested) | Match against current pattern × 2 ships |
| 1 | `experiments/_templates/q_b1_chain_depth.py.template` + `tools/stamp_anchor.py` | -50% exp_dev wall (Q-B1 only) | low | LANDED-PARTIAL (Q-B1 only; PP-48/Q-A3/PP-52 TODO) | Stamped d90 verified vs hand-written d80 |
| 5 | `tools/cap_map_append.py` (sub-property append + version bump) | -90% cap_map I/O | MEDIUM | LANDED (shadow-mode required first 3 runs) | Dual-write + diff × 3 cycles |
| 4 | `tools/orchestrator/agents/cycle_processor.md` | -1 commit, -context reload | MEDIUM | LANDED (skill scaffold TODO; shadow-mode required first 3 runs) | Compare combined vs parallel × 3 cycles |
| 8 | `tools/orchestrator/agents/smoke_runner.md` + handoff protocol | -30% tokens, Sonnet smoke | MEDIUM | LANDED (skill scaffold TODO; manual audit required first 2 runs) | exp_dev dual-smoke × 2 cycles |

## Outstanding TODOs
1. Add anchor templates for PP-48 NKT depth, Q-A3 cross-layer (refactor M_MID per-level constants to parametric list), PP-52 exact_rollback + one_shot
2. Wire `cycle_processor` + `smoke_runner` as ~/.claude/skills/ entries
3. Run first shadow-mode cycle for #5 cap_map_append (dual-write next verdict batch)
4. Run first shadow-mode cycle for #4 cycle_processor (dispatch BOTH paths next HP-dominant batch + diff)
5. Run first manual-audit cycle for #8 smoke_runner (exp_dev keeps smoke; smoke_runner dual-ships; diff)
6. ship_anchor.py first-use: run it on one anchor and verify SHIPPED line + REMOTE VERIFY hit (no dual-path needed; idempotent)
7. Q-B1 stamp_anchor first-use: stamp d100, verify by self-test, ship, await verdict

## Risk-tracking conventions

For MEDIUM-risk items (#4, #5, #8):
- First 3 runs: dual-path execution OR side-by-side comparison
- Log diff in this doc with PASS/FAIL/PARTIAL per run
- Promote to full-rollout only after 3 PASS runs
- Rollback flag: `data/efficiency_rollback_<item>.flag` halts the new path

## Rollout order
PHASE 1 (very low risk; ship tonight): #6 → #7 → #2
PHASE 2 (low risk; ship over next 1-2 cycles): #3 → #1
PHASE 3 (medium risk; ship with shadow-mode tracking): #5 → #4 → #8

## Per-item changelog
(Entries added as items land)
