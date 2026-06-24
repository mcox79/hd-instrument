# exp_dev hand-off — research: substrate-LM experimental methodology 3x drill (META protocols)

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-23
**Trigger:** USER 2026-06-23 directive — "we've done a lot wrong, and clearly we need to learn what the right way to run them is. release a 3x drill to elucidate the design space."
**Source research note:** `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` before any dispatch (per [[feedback-orchestrator-pause-experiments]])

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off provides anchor candidates + substrate-product reading + context pointers; exp_dev authors the tool/protocol and pre-reg.

**META scope:** these anchors are TOOLING / PROTOCOL ships, not substrate-mechanism experiments. They are CERT-discipline infrastructure. Each ship is a small (1-4 hour) tool-writing task plus a discipline-integration step.

---

## Anchor candidates (rank-ordered by leverage / ship-cost ratio)

### 1. PRIMARY: ship `tools/preflight_check.py` + `preflight_spec.yaml` template (Tier-1; load-bearing)

**Anchor pointer:** source drill section L3.1 ("FIX #1 — Machine-checkable 5-FIELD PREFLIGHT SPEC") + L4 Tier-1 item 1

**Substrate-product reading:** **THE single highest-leverage methodology fix.** A 5-field YAML spec (`metric_scope` / `baseline_provenance` / `config_validity` / `discriminator_ratio` / `harm_prediction`) becomes a REQUIRED file in every cell directory. `tools/preflight_check.py <cell_dir>` validates structurally; missing or malformed field returns non-zero exit. `tools/dispatch.sh` (and orchestrator queue_add wrapper) call preflight_check.py and HARD_BLOCK dispatch on non-zero exit.

Schema (full YAML template provided in source drill section L3.1). Five sections, all REQUIRED:
- `metric_scope`: primary_metric + metric_class + metric_appropriate_for_mechanism_class + justification + class-mismatch protection
- `baseline_provenance`: baseline_name + same_harness_as_arm + rerun_in_this_cell + same-seed/corpus/tokenizer flags + honest_comparison_clause
- `config_validity`: required_resources (gpu_mem_gb, cpu_cores, wall_time_max_s) + oom_handling + per_config_exit_logging
- `discriminator_ratio`: expected_arm_separation + null_arm_separation + by_construction_saturation_check
- `harm_prediction`: setup_implies_metric_floor + what_would_falsify_setup_vs_mechanism + fidelity_gap_documentation

**Retroactive effectiveness:** 7 of 10 observed session-2026-06-23 failures CAUGHT at preflight; 3 of 10 PARTIAL.

**Tier hint:** tool-ship + discipline-integration (no substrate cert tier; orchestrator infrastructure). Counts as a Director-tooling fix in the Fix #25-#28 series. Number it Fix #29.

**Why-now:** USER explicitly directed methodology fix; 10 observed failures this session represent ~30+ hours of corrective work that would have been prevented at ~12-15 min/cell discipline cost.

**Cost:** ~2-3 hours of tool-writing; ~5-10 min/cell ongoing (templated from prior cell after first ~3 cells).

**HARD_PASS criterion (for the ship itself):** preflight_check.py rejects 5/5 of the test-cases derived from session failures 1, 2, 3, 5, 9. HARD_FAIL: rejects < 4/5.

### 2. SECONDARY: ship `tools/verdict_lint.py` (WHAT_THIS_DOES_NOT_SHOW lint; cultural-anti-framing)

**Anchor pointer:** source drill section L3.2 ("FIX #2 — MANDATORY post-flight HONEST_NEGATIVE_FRAMING line") + L4 Tier-1 item 3

**Substrate-product reading:** structurally inverts the writing-cost gradient that drives over-claiming. Every verdict_msg must end with a `WHAT_THIS_DOES_NOT_SHOW:` clause (1-3 bullets minimum). `tools/verdict_lint.py` parses verdict_msg; missing clause = lint_error; commit hook rejects. The discipline change: writing 2-3 honest bullets becomes the SHORT path (~2 min); omitting becomes the LONG path (visible in commit diff; Skunkworks audit will catch).

Example template (provided to cell authors):
```
VERDICT: <PASS/FAIL/PARTIAL>
SUMMARY: <one-line>
WHAT_THIS_DOES_NOT_SHOW:
- <does not compare to X baseline because Y>
- <does not generalize beyond Z corpus>
- <does not establish W mechanism is responsible>
```

**Retroactive effectiveness:** 2 of 10 observed failures CAUGHT directly (6, 7); structurally protects against future framing-cost-gradient failures across all categories.

**Tier hint:** tool-ship + commit-hook integration; counts as Fix #30 in the autonomous-arc series.

**Why-now:** Fix #28 violations recurred 4x in one session 2026-06-23 despite explicit cultural awareness; structural fix is the only path that scales.

**Cost:** ~1 hour tool-writing + ~2-3 min/cell ongoing.

**HARD_PASS criterion (for the ship itself):** lint catches 4/4 retroactively-tested verdict_msg's from Fix #28 violation cells. HARD_FAIL: catches < 3/4.

### 3. TERTIARY: extend `tools/peek_arm_metrics.py` with 3 new flags (Director-readability lift)

**Anchor pointer:** source drill section L4 Tier-1 item 2

**Substrate-product reading:** extend the existing Fix #28 automation with three new structural-check flags:
- `--check-by-construction-saturation` (flags max-arm >= 0.99 or cv < 0.005)
- `--check-baseline-provenance` (greps for cross-cell baseline references; warns if found)
- `--check-metric-class` (reads `preflight_spec.yaml`; warns on metric/mechanism mismatch)

Lower priority than (1) and (2) because peek_arm_metrics already exists and is used; this is incremental. But adds Director-side checks at READ time (before atomization framing is written).

**Retroactive effectiveness:** 2-3 of 10 caught at READ time (Director check before atomization commits the framing error).

**Tier hint:** tool-extension; counts as Fix #28a (extension of Fix #28, not a new fix).

**Why-now:** complements (1) and (2); low cost; ships next.

**Cost:** ~1-2 hours.

### 4. DEFERRED: Tier 2 protocols (next-week ships; structural)

Items 4-6 from source drill section L4 Tier-2:
- **Skunkworks pre-dispatch vet** (`tools/skunkworks_predispatch_vet.py`) — promote Skunkworks SCHEMA-VET to mandatory PRE-dispatch step
- **Cell-author template update** — `tools/cell_template/` with preflight_spec.yaml stub
- **Runner-health monitor extension** — already partially live per Fix #25; extend to publish `data/runner_health.jsonl`

These are DEFERRED for sequencing reasons (Skunkworks bandwidth re-planning required; cell template depends on preflight_spec.yaml shipping first; runner-health is orthogonal). After (1), (2), (3) ship and stabilize, queue these next week.

### 5. NOT FOR EXP_DEV (cultural; out-of-scope here)

Items 10-12 from source drill section L4 Tier-4 (training, REFORMS adoption, quarterly audit) — these are USER + Director cultural disciplines, not exp_dev tool ships. Document them in the source drill but do NOT include in this hand-off.

---

## Context pointers (file paths only; no summaries per [[feedback-overhead-reduction]])

### Source research drill (MUST READ first)
- `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (THIS hand-off's parent)

### Prior methodology-audit precursors
- `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` (2x mechanism-level audit)
- `notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (10-negative synthesis)
- `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter receiver SNR diagnosis)
- `notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md` (Skunkworks META atomization)
- `notes/exp_dev_handoff_research_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` (sibling 2x hand-off; mechanism-level cells)

### Existing tools to extend / reference
- `tools/peek_arm_metrics.py` (Fix #28 automation; reference for proposed extensions)
- `tools/predispatch_check.py` (Fix #26; reference for runner-health integration)
- `tools/landing_notifier.py` (Fix #25; reference for runner-health monitor pattern)
- `tools/atomize_meta_harness_rigged_substrate_as_lm_2026-06-23.py` (Skunkworks atomization tool; reference for SCHEMA-VET extension)

### Discipline-pattern references (MEMORY.md feedback entries)
- Fix #14-#28 autonomous-arc series
- `feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23.md`
- `feedback_use_peek_arm_metrics_before_framing_2026-06-23.md`
- `feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17.md`

---

## Contract section

**This hand-off authorizes exp_dev to:**
- Ship `tools/preflight_check.py` + initial `preflight_spec.yaml` template + dispatch-integration (priority 1)
- Ship `tools/verdict_lint.py` + commit-hook integration (priority 2)
- Extend `tools/peek_arm_metrics.py` with 3 new flags (priority 3)
- Test each ship retroactively against named session-2026-06-23 failure cases as defined in source drill section L3.4
- Coordinate with Skunkworks for the SCHEMA-VET integration step (Tier 2)

**This hand-off does NOT authorize exp_dev to:**
- Mutate any existing cells, atoms, or verdicts (out of scope)
- Ship Tier 2 items 4-6 in same cycle as Tier 1 (sequence: Tier 1 first)
- Ship Tier 4 cultural items (out of scope; USER + Director decisions)
- Add the preflight HARD_BLOCK without first running in WARN-only mode for 5-10 cells to validate templates and surface friction

**Recommended ship sequence:**
1. Ship preflight_check.py in WARN-only mode (logs warnings, does not block)
2. Run for 3-5 cells; gather friction reports; iterate template
3. Ship verdict_lint.py + commit-hook (independent of preflight)
4. Ship peek_arm_metrics extensions (independent)
5. Once preflight_check.py has been WARN-stable for 5+ cells, promote to HARD_BLOCK mode
6. Coordinate Tier 2 ship cadence with Skunkworks separately

---

## Autonomy declaration

exp_dev decides:
- Exact YAML schema details (field names, optional-vs-required granularity beyond the 5 required sections)
- Tool implementation language (Python preferred but free choice)
- WARN-mode duration before HARD_BLOCK promotion (target 5-10 cells; expand if friction is high)
- Test cases beyond the 5 named session-2026-06-23 failure retroactive checks
- Commit-hook implementation details (pre-commit framework vs. git hooks directly)
- Whether to bundle (1), (2), (3) into one ship-cycle or sequence them across 2-3 cycles
- WHAT_THIS_DOES_NOT_SHOW: minimum bullet count (recommended 2; exp_dev may justify 1 or 3)

Research does NOT decide:
- Cell timing / queue routing for these ships (exp_dev + orchestrator domain)
- Whether to override Tier 2 sequencing for time-pressure reasons (USER decision)
- Whether to skip WARN-mode and go directly to HARD_BLOCK (exp_dev judgment with USER consult if risky)

— Research (Opus 4.7-1M), 2026-06-23
