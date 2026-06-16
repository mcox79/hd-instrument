"""
PHASE-B CARDINALITY STAGE-1 SMOKE-GATE (DECISION 172a + Skunkworks run_mode-asymmetry lock).
EARLY-KILL pre-flight (~30 min CPU) run BEFORE the STAGE-2 full GPU sweep. Catches the 3 pre-registered
HARD-FAIL modes cheaply at K<=16, M in {200,2000}, n=2.

RUN_MODE ASYMMETRY (LOCKED, Skunkworks/DECISION 149): a smoke PASS confers ZERO load-bearing verdict --
it ONLY licenses proceeding to STAGE 2; it is NEVER recorded as HARD-PASS/corroboration; and it does NOT
clear the 3 modes at full scale (STAGE 2 independently re-checks all 3). A smoke FAIL is a valid abort/redesign.

ANTI-GAMING (Skunkworks): the abort thresholds are PRE-REGISTERED IN CODE here, COLD, before any STAGE-1
run -- no ex-post tuning (same Lakatos discipline as the cardinality compute_verdict bands). Modes (i)+(iii)
are fixed from Drill 1; mode (ii) cleanup-noise threshold is PARAMETERIZED pending Drill 3 (which refines
the M=2000 cleanup-breakdown line; set CLEANUP_RECOVERY_MIN from Drill 3 before the GO STAGE-1 run).

STATUS: gate-ready harness; pre-registered abort thresholds + abort-logic self-tests. The STAGE-1 smoke RUN
fires at the 2026-06-17 GO (NOT during the HOLD). CPU. ASCII.
"""
import sys

# ===== PRE-REGISTERED STAGE-1 ABORT THRESHOLDS (cold; no ex-post tuning) =====
SMOKE_PARAMS = {"K_max": 16, "M_list": [200, 2000], "n_seeds": 2, "N": 1024}

# mode (i) basis-null-too-close: at K<=16, C1 basis-only must FAIL (cardinality-REQUIRED). If C1 closes,
# the basis already does cardinality -> the task is EVADABLE / basis-null too strong -> ABORT (recalibrate).
SMOKE_ABORT_C1_BASIS_NULL = 0.70        # C1 accuracy >= this at K<=16 -> ABORT (basis closes; Drill-1 mode i)

# mode (ii) cleanup-noise breakdown at M=2000: C2 cleanup distinct-set recovery must hold. Below this line
# the cleanup is broken BELOW N-capacity -> a STAGE-2 low C2 would be artifact, not primitive -> ABORT+fix.
# PARAMETERIZED pending Drill 3 (cleanup-noise drill refines this). Conservative default until Drill 3 lands.
CLEANUP_RECOVERY_MIN = 0.50             # PENDING DRILL 3 -- set from Drill 3 cleanup-noise thresholds before GO

# mode (iii) multi-seed drift-to-attractor: at n=2, seed-variance must be reasonable. Wide std => drift =>
# n>=3 won't deliver tight CI -> ABORT (investigate before STAGE 2). Drill-1 value.
SMOKE_ABORT_SEED_STD_MAX = 0.40         # seed std > this at n=2 -> ABORT (drift-to-attractor; Drill-1 mode iii)


def stage1_abort_decision(c1_basis_acc_K16, c2_cleanup_recovery_M2000, seed_std):
    """Pure pre-registered abort logic. Returns (proceed_to_stage2: bool, reasons: list).
    proceed only if ALL 3 modes pass; ANY fail -> redesign + re-smoke before STAGE 2.
    A PASS confers ZERO verdict -- it ONLY licenses STAGE 2 (run_mode asymmetry)."""
    reasons = []
    if c1_basis_acc_K16 >= SMOKE_ABORT_C1_BASIS_NULL:
        reasons.append(f"ABORT mode-i: C1 basis-null acc {c1_basis_acc_K16:.3f} >= {SMOKE_ABORT_C1_BASIS_NULL} "
                       f"(basis closes cardinality at K<=16 -> EVADABLE / basis-orthogonality recalibrate)")
    if c2_cleanup_recovery_M2000 < CLEANUP_RECOVERY_MIN:
        reasons.append(f"ABORT mode-ii: C2 cleanup recovery {c2_cleanup_recovery_M2000:.3f} < {CLEANUP_RECOVERY_MIN} "
                       f"at M=2000 (cleanup-noise breakdown below capacity -> fix cleanup before STAGE 2)")
    if seed_std > SMOKE_ABORT_SEED_STD_MAX:
        reasons.append(f"ABORT mode-iii: seed std {seed_std:.3f} > {SMOKE_ABORT_SEED_STD_MAX} "
                       f"(multi-seed drift-to-attractor -> investigate before STAGE 2)")
    proceed = len(reasons) == 0
    return proceed, reasons


def _abort_logic_selftests():
    # all pass -> proceed (smoke PASS = license STAGE 2 ONLY; zero verdict)
    p, r = stage1_abort_decision(0.55, 0.80, 0.05); assert p and not r
    # mode i: C1 too strong -> abort
    p, r = stage1_abort_decision(0.75, 0.80, 0.05); assert (not p) and any("mode-i" in x for x in r)
    # mode ii: cleanup broken at M=2000 -> abort
    p, r = stage1_abort_decision(0.55, 0.40, 0.05); assert (not p) and any("mode-ii" in x for x in r)
    # mode iii: seed drift -> abort
    p, r = stage1_abort_decision(0.55, 0.80, 0.50); assert (not p) and any("mode-iii" in x for x in r)
    # multiple modes
    p, r = stage1_abort_decision(0.75, 0.40, 0.50); assert (not p) and len(r) == 3
    print("[stage1-abort-selftests] PASS: 5 pre-registered abort cases verified", flush=True)


_abort_logic_selftests()


def main():
    # The STAGE-1 smoke RUN fires at the 2026-06-17 GO: run cardinality C1/C2 at K<=16, M in {200,2000},
    # n=2 (reuse exp_cardinality_phase_B_skeleton readouts), feed metrics to stage1_abort_decision().
    # NOT run during the HOLD; this main is the GO-time entry. Mode (ii) threshold set from Drill 3 first.
    print("[STAGE-1 smoke-gate] gate-ready harness. RUN at 2026-06-17 GO (NOT during HOLD).", flush=True)
    print(f"[STAGE-1] params={SMOKE_PARAMS}", flush=True)
    print(f"[STAGE-1] PRE-REGISTERED abort thresholds: C1_basis_null>={SMOKE_ABORT_C1_BASIS_NULL} (mode i) | "
          f"cleanup_recovery<{CLEANUP_RECOVERY_MIN} (mode ii; PENDING DRILL 3) | seed_std>{SMOKE_ABORT_SEED_STD_MAX} (mode iii)", flush=True)
    print("[STAGE-1] run_mode asymmetry: smoke PASS = license STAGE 2 ONLY, ZERO verdict, never corroboration;", flush=True)
    print("[STAGE-1]   STAGE 2 full re-checks all 3 modes at scale (smoke cannot clear them).", flush=True)


if __name__ == "__main__":
    main()
