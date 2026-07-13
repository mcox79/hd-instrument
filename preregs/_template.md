# Pre-registration template
# Copy this file as preregs/<DATE>_<ANCHOR_BASE_NAME>.md
# Replace each {{TOKEN}} below. Delete this header block when filing.
# Do NOT delete the headers below — they are load-bearing for verdict_handler's honest re-read.

# Pre-registration: {{ANCHOR_NAME}}

**Date:** {{DATE}}
**Anchor:** {{ANCHOR_NAME}}
**Queue:** {{QUEUE_NAME}}
**N:** {{N}}, **Seeds:** {{SEEDS}}, **{{PARAM_LABEL}}:** {{PARAM_VALUE}}

## Scientific question
{{QUESTION_ONE_OR_TWO_SENTENCES}}

## Pre-registered bands

**HARD-PASS:**
- {{HP_CRITERION_1}}
- {{HP_CRITERION_2}}
{{HP_CRITERION_OPTIONAL_3}}

**MIDDLE:** {{MID_CRITERION}}.

**HARD-FAIL:** {{HF_CRITERION_1}} OR {{HF_CRITERION_2}}.

## Calibration rationale
{{ONE_PARAGRAPH_WHY_BANDS_ARE_THESE_VALUES}}

## N-suffix section
Anchor _n{{N}}; production N = {{N}}; scripts enforce N = _N_SUFFIX = {{N}}.

## Timeout estimate
Smoke ~ {{SMOKE_WALL_S}}s at N={{SMOKE_N}} smoke. FULL: N={{N}}, seeds={{SEEDS}}.
formula: ceil(1.5 * {{SMOKE_WALL_S}} * ({{N}}/{{SMOKE_N}})^{{SCALING_EXPONENT}} * ({{SEEDS}}/{{SMOKE_SEEDS}})) = {{COMPUTED_VALUE}}
timeout_s = {{TIMEOUT_S}}

## Validity-preflight declarations (§15-F; run_validity_preflight in self_test)
# Required for any cell that calls a live substrate object (KGStore / store-build helper / fit module).
# Declare N/A per line if the cell has no such call (pure-synthetic-mechanism cell).
real_code_path_exercised: {{LIST_REAL_SUBSTRATE_ENTRYPOINTS_THE_SELFTEST_CONSTRUCTS}}   # gate F.1 — self-test builds the REAL objects at N~16, not a synthetic-only branch
substrate_signature_checked: {{LIST_SUBSTRATE_CALLABLES_BOUND_AGAINST_inspect_signature}}   # gate F.2/F.3 — BASE/portable kwargs only; no version-specific optional kwargs (local/remote drift)
guard_baseline_validated: {{LIST_CONTROL_VS_BASELINE_BREAK_GUARDS_OR_NA}}   # gate F.4 — each control-beats-baseline guard validated NOT at the arena floor

# -----------------------------------------------------------------------------
# Token glossary
# -----------------------------------------------------------------------------
# ANCHOR_NAME       Full PROT-018 anchor name including _n<N> suffix
# DATE              ISO date (YYYY-MM-DD)
# QUEUE_NAME        "overnight_queue" (GPU) | "remote_cpu_queue" (CPU)
# N                 Production vector dim (1024 / 4096 / 8192 / 16384 / 32768)
# SEEDS             Production seed count (typically 5)
# PARAM_LABEL       The varying parameter label for this anchor family
#                   ("depth", "L-depth", "K", "alpha", etc.)
# PARAM_VALUE       The varying parameter value
# QUESTION          1-2 sentence capability question (no "X will pass" preframing)
# HP_CRITERION_*    Quantitative criteria; cite per-cell metrics
#                   (e.g., "L_fid >= 0.9999 unanimous 5/5 seeds")
# MID_CRITERION     Quantitative band (e.g., "any L_fid in [0.85, 1.0)")
# HF_CRITERION_*    Quantitative trip-wire (e.g., "L_fid < 0.85")
# SCALING_EXPONENT  Empirical wall-scaling exponent in N
#                   (1.0 for batched MMUL; 1.5 for vector ops with extra logs;
#                    1.7 for kernel/path-storage; 2.0 for full O(N^2) operators)
# SMOKE_WALL_S      Measured smoke wall in seconds
# SMOKE_N           Smoke N (typically 1024 or 4096)
# SMOKE_SEEDS       Smoke seeds (typically 2)
# TIMEOUT_S         Final per-PROT-019 floor (>=600s; <=14400s)
# -----------------------------------------------------------------------------
