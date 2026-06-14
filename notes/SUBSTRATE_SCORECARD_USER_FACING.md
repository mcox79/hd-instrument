# SUBSTRATE SCORECARD (USER-facing)

**Stable path.** `d:\AI\hd-instrument\notes\SUBSTRATE_SCORECARD_USER_FACING.md`
**Last updated.** 2026-06-13 evening
**Update cadence.** Each Cycle close + each significant substrate state change
**Purpose.** Single page USER can look at to know if Research/substrate made progress. USER-verifiable from artifact paths.

## How to read this

- **Rows 1-4 = your 4 goals (lagging indicators).** What "substrate success" actually means.
- **Leading indicators.** Things that move BEFORE goals move. Use to predict whether next-cycle goal numbers will improve.
- **LAKATOS axis C floor.** External falsification gates per 22nd methodology rule. UNMET = honest failure.
- **What to watch this week.** Open measurements that can flip a row.
- **USER spot-check commands.** Bash one-liners you can run yourself to verify Research's numbers.

## Goals (lagging indicators)

| # | Goal | Current | Measurement source (USER-verifiable) | Trend (session arc today) |
|---|---|---|---|---|
| 1 | Substrate-on-all-knowledge (LLM-class capability) | **F1 macro-F1 = 0.0067 (UNMET; floor 0.50)** | `data/substrate_index/bench_reports/f1_macro_*.json` | flat at noise; not advancing this session |
| 2 | Recursive self-improvement loop operational | **5/5 steps OPERATIONAL; DISTILLATION_RATIO 0.82** | `data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json` (`distillation_ratio` field) | 0.33 -> 0.70 -> 0.82 (2.5x today) |
| 3 | Architecturally distinct from LLMs | **0 false merges across 24 integrated pairs; capability_preservation=1.0** | `data/substrate_index/bench_reports/distill_integrate_1_report.json` | 0/11 -> 0/23 -> 0/24 (sound throughout) |
| 4 | Three verbs (store / understand / improve) | **All three empirically present** | atoms count + L6-PROOF reports + distill ratio | atoms 1,758 -> 20,867 (12x today) |

## Leading indicators (should move before goals)

| Indicator | Current | Source | What it predicts |
|---|---|---|---|
| F2 abstraction ratio (substrate generalizes via type-atoms) | **0% measured; 5.6% REALIZED pending** Exp-Dev re-run | `substrate_abstraction_ratio_v0.py` output | Goal 1 capability gain (when types ground, abstractions emerge) |
| Composite type-atoms shipped | 28/28 (15 mathematical + 13 substrate-operator) | `data/substrate_index/atoms.jsonl` filtered to type-class | F2 unlock capacity |
| PROVABLY_EQUIVALENT pairs accumulated | 21 | `distill_verify_1_operator_equivalence.json` | Goal 2 self-improvement velocity |
| Methodology rules CONFIRMED today | 4 (10th + 19th + 21st + 22nd) | `C:\Users\marsh\.claude\projects\d--AI\memory\` filtered | Substrate metacognition operationalization (Goal 3) |

## LAKATOS axis C falsification floor (external gates per 22nd rule)

| Floor | Status | What it gates |
|---|---|---|
| F1 clean held-out macro-F1 >= 0.50 | **UNMET** (0.0067 on degraded data) | "Capability proven" narrative for Goal 1 |
| F2 abstraction ratio nonzero | **LIKELY MET pending** Exp-Dev measurement | "Substrate generalizes" narrative |
| F3 no-regression PASS on clean before/after | **UNMET** (no clean baseline exists yet) | Safety-under-improvement narrative |
| F4 language tracks math at scale | **FUTURE** | Goal 1 LLM-class language mastery (aspirational) |

**3 of 4 floors UNMET.** Honest disclosure. Closed-loop OPERATIONAL is necessary but not sufficient.

## What to watch this week (open measurements that can flip rows)

1. **F1 clean held-out** measurement (Testbed lane) -- can move Goal 1 from UNMET toward MET. **Highest priority.**
2. **F2 substrate_abstraction_ratio_v0.py re-run** post Phase-4 ingest (Exp-Dev lane) -- can flip F2 floor MET, validates Phase 4 work.
3. **F3 baseline** establishment (Testbed lane) -- prerequisite for F3 gate; enables before/after capability measurement.
4. **B' policy v2** decision (Testbed lane; my recommendation: ship after F1) -- enacts Goal 2 "improve" verb at storage layer.
5. **Push to origin** (blocked on USER auth) -- enables independent USER verification on remote desktop.

## USER spot-check commands (verify Research's numbers yourself)

Run these from `d:\AI\hd-instrument` to independently check the scorecard:

```bash
# Goal 4 atom count
wc -l data/substrate_index/atoms.jsonl

# Goal 2 distillation ratio (look at the "distillation_ratio" field)
python -c "import json; d=json.load(open('data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json')); print('distillation_ratio:', d.get('distillation_ratio'), 'PROVABLY_EQUIVALENT:', d.get('provably_equivalent_count'))"

# Goal 3 capability_preservation (NOT_EQUIVALENT count must be 0)
python -c "import json; d=json.load(open('data/substrate_index/bench_reports/distill_integrate_1_report.json')); print('NOT_EQUIVALENT:', d.get('not_equivalent_count', 'field missing'))"

# Methodology rule count (Goal 3 metacognition)
ls C:\Users\marsh\.claude\projects\d--AI\memory\ | findstr "methodology_rule" | find /c "methodology_rule"

# Latest commit (substrate state shipped)
git log -1 --oneline
```

If any number differs from this scorecard, Research is wrong or scorecard is stale. Flag it.

## Honest acknowledgements (what did NOT progress)

- **F1 unchanged at 0.0067 across this entire session.** Capability gate is the most important goal and it did not advance.
- **B' policy not yet enacted.** Substrate atom count still monotone additive at storage level (24 atom-removals possible but not executed).
- **Push to origin blocked.** USER cannot independently verify scorecard from remote desktop until auth resolved.
- **LAKATOS axis C 3 of 4 floors UNMET.** Substrate is PROGRESSIVE but not yet VALIDATED per Lakatos criterion.
- **Depth ceiling still ~3.** Multi-premise proof depth 7+ pending parser-v2.

## What "making progress" means going forward

The scorecard answers "are we making progress?" by row. Specifically:

- **Row 1 (Goal 1) moves when F1 measurement on clean infrastructure shows non-noise capability.** Until then we are scaling the engine but not proving it produces capability. This is the bottleneck.
- **Row 2 moves with each closed-loop cycle that integrates new PROVABLY_EQUIVALENT pairs while maintaining 0 false merges.** Saturating near 0.82 algorithm-typing ceiling; further compression requires data hygiene + B' v2 + new corpus.
- **Row 3 moves when capability_preservation invariant survives larger-scale tests (100+ pairs, scale-up, adversarial pre-screen surviving).** Currently sound at 24-pair scale.
- **Row 4 moves with atom scale + L6-PROOF depth + DISTILLATION_RATIO simultaneously.** Today: yes (12x atoms + L6 ASSEMBLY-COMPLETE + 0.82 ratio).

**Net read at 2026-06-13 evening:** the engine works (Goals 2/3/4 advanced today). The capability proof (Goal 1) did not advance. Next session's measurement of progress = whether F1 moves.

## Cross-references

- `notes/research_LAKATOS_AUDIT_1_LEDGER_*` (Cycle 51 close axis A/B/C ledger)
- Memory `session-resume-state-2026-06-13-evening-pre-compaction` (technical state)
- Memory `substrate-USER-decisions-2026-06-13` (USER goals + 22nd rule lock)
- Memory `feedback-substrate-standalone-capability-first` (USER 11th rule)
