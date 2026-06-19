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

# mode (ii) REFINED by Drill 3+4 (DECISION 174a/175): the binding constraint is NOT classical cleanup-noise
# (Frady/Sommer k_max~269 comfortable at k=5) but FPE-PHASE-KERNEL near-neighbor confusion at M>=2000.
# Measured by the STAGE-1.2 FPE-amplification probe (exp_cardinality_phase_B_stage1_2_*). RECONCILED
# pre-registered routes (closes Skunkworks GAP-1 MIDDLE-band + GAP-2 dual-trigger; cold, no ex-post):
FPE_TOP1_HARD_BLOCK = 0.80              # FPE top-1 < this -> HARD STAGE-2 BLOCK (swap to Hopfield head first)
FPE_TOP1_CLEAN = 0.95                   # FPE top-1 >= this (+ low confusion + low amp) -> CLEAN pass
FPE_NN_CONFUSION_CLEAN = 0.10          # near-neighbor confusion <= this -> clean
FPE_NN_CONFUSION_BANDLIMIT = 0.30      # confusion > this -> BAND-LIMIT base phases (separate route)
FPE_AMP_DUALHEAD = 0.05                # amplification delta (discrete-FPE top-1) >= this -> dual-head-control (MIDDLE)
# GAP-2 reconciliation (auditor lean): FPE<0.80 = HARD block (most severe); amp-delta>=0.05 = dual-head-control
# trigger (MIDDLE, proceed with both naive-max-cos AND Hopfield, verdict must hold/disambiguate under both).

# mode (iii) multi-seed drift-to-attractor: at n=2, seed-variance must be reasonable. Wide std => drift =>
# n>=3 won't deliver tight CI -> ABORT (investigate before STAGE 2). Drill-1 value.
SMOKE_ABORT_SEED_STD_MAX = 0.40         # seed std > this at n=2 -> ABORT (drift-to-attractor; Drill-1 mode iii)


def stage1_2_fpe_route(fpe_top1, nn_confusion, amp_delta):
    """RECONCILED pre-registered mode-ii (FPE-phase-kernel) route (closes Skunkworks GAP-1+GAP-2).
    Returns (route, reason). Routes (severity-ordered):
      HARD-BLOCK-HOPFIELD : FPE top-1 < 0.80 -> swap to modern-Hopfield cleanup head BEFORE STAGE 2
      BAND-LIMIT          : nn confusion > 0.30 -> band-limit base phases / hex-grid / Lu-Bremer before STAGE 2
      MIDDLE-DUAL-HEAD    : FPE in [0.80,0.95) OR confusion in (0.10,0.30] OR amp-delta >= 0.05
                            -> proceed to STAGE 2 BUT dual-head confound-control MANDATORY (run cardinality C2
                               under BOTH naive-max-cos AND Hopfield; verdict must hold/disambiguate under both)
      CLEAN               : FPE >= 0.95 AND confusion <= 0.10 AND amp-delta < 0.05 -> naive cleanup sufficient"""
    if fpe_top1 < FPE_TOP1_HARD_BLOCK:
        return ("HARD-BLOCK-HOPFIELD", f"FPE top-1 {fpe_top1:.3f} < {FPE_TOP1_HARD_BLOCK}: FPE-cleanup dominant -> Hopfield head before STAGE 2")
    if nn_confusion > FPE_NN_CONFUSION_BANDLIMIT:
        return ("BAND-LIMIT", f"nn-confusion {nn_confusion:.3f} > {FPE_NN_CONFUSION_BANDLIMIT}: kernel too coarse -> band-limit base phases before STAGE 2")
    if (fpe_top1 < FPE_TOP1_CLEAN) or (nn_confusion > FPE_NN_CONFUSION_CLEAN) or (amp_delta >= FPE_AMP_DUALHEAD):
        return ("MIDDLE-DUAL-HEAD", f"FPE {fpe_top1:.3f}/conf {nn_confusion:.3f}/amp {amp_delta:+.3f}: proceed STAGE 2 with dual-head (naive+Hopfield) confound-control MANDATORY")
    return ("CLEAN", f"FPE {fpe_top1:.3f}>=0.95 + conf {nn_confusion:.3f}<=0.10 + amp {amp_delta:+.3f}<0.05: naive cleanup sufficient")


def stage1_abort_decision(c1_basis_acc_K16, fpe_top1, nn_confusion, amp_delta, seed_std):
    """Pre-registered STAGE-1 decision. Returns (proceed_to_stage2, mode_ii_route, reasons).
    proceed=False if mode-i, mode-ii (HARD-BLOCK/BAND-LIMIT), or mode-iii fail. MIDDLE-DUAL-HEAD proceeds
    (with the dual-head confound-control flag). A PASS confers ZERO verdict -- licenses STAGE 2 only."""
    reasons = []
    if c1_basis_acc_K16 >= SMOKE_ABORT_C1_BASIS_NULL:
        reasons.append(f"ABORT mode-i: C1 basis-null acc {c1_basis_acc_K16:.3f} >= {SMOKE_ABORT_C1_BASIS_NULL} (basis closes -> EVADABLE/recalibrate)")
    route, rmsg = stage1_2_fpe_route(fpe_top1, nn_confusion, amp_delta)
    if route in ("HARD-BLOCK-HOPFIELD", "BAND-LIMIT"):
        reasons.append(f"ABORT mode-ii ({route}): {rmsg}")
    if seed_std > SMOKE_ABORT_SEED_STD_MAX:
        reasons.append(f"ABORT mode-iii: seed std {seed_std:.3f} > {SMOKE_ABORT_SEED_STD_MAX} (drift-to-attractor)")
    proceed = len(reasons) == 0
    return proceed, route, reasons


def _abort_logic_selftests():
    # clean all -> proceed CLEAN
    p, route, r = stage1_abort_decision(0.55, 0.97, 0.05, 0.02, 0.05); assert p and route == "CLEAN" and not r
    # mode-ii MIDDLE (FPE 0.90 in [0.80,0.95)) -> proceed but dual-head
    p, route, r = stage1_abort_decision(0.55, 0.90, 0.05, 0.03, 0.05); assert p and route == "MIDDLE-DUAL-HEAD"
    # mode-ii MIDDLE via amp-delta>=0.05 even if FPE high
    p, route, r = stage1_abort_decision(0.55, 0.97, 0.05, 0.06, 0.05); assert p and route == "MIDDLE-DUAL-HEAD"
    # mode-ii HARD-BLOCK (FPE<0.80) -> abort
    p, route, r = stage1_abort_decision(0.55, 0.70, 0.05, 0.30, 0.05); assert (not p) and route == "HARD-BLOCK-HOPFIELD"
    # mode-ii BAND-LIMIT (confusion>0.30) -> abort
    p, route, r = stage1_abort_decision(0.55, 0.90, 0.40, 0.03, 0.05); assert (not p) and route == "BAND-LIMIT"
    # mode-i abort
    p, route, r = stage1_abort_decision(0.75, 0.97, 0.05, 0.02, 0.05); assert (not p) and any("mode-i:" in x for x in r)
    # mode-iii abort
    p, route, r = stage1_abort_decision(0.55, 0.97, 0.05, 0.02, 0.50); assert (not p) and any("mode-iii" in x for x in r)
    print("[stage1-decision-selftests] PASS: 7 pre-registered cases (CLEAN/MIDDLE-dual-head/HARD-BLOCK/BAND-LIMIT/mode-i/mode-iii) verified", flush=True)


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
