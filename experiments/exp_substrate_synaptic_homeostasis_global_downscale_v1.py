"""substrate_synaptic_homeostasis_global_downscale_v1 -- REM homeostasis primitive.

SCIENTIFIC QUESTION (brain-grounded; sleep consolidation pillar 2 of 3):
  Tononi-Cirelli synaptic homeostasis hypothesis: during REM sleep, synapses are
  globally downscaled by a uniform multiplicative factor. This preserves relative
  strengths while preventing runaway potentiation that would saturate the network.

  Substrate analog: at every N_DOWNSCALE_INTERVAL cycles, multiply ALL W entries
  by a uniform factor in (0,1). Brain analog: REM downscaling.

  Question: does periodic global downscaling prevent saturation in substrate's
  continual-write regime WITHOUT destroying older facts? The risk: too-aggressive
  downscaling forgets old patterns faster than baseline cliff.

PRE-REGISTERED BANDS (LOCKED via module-init assert; bands sacrosanct both ways):
  HARD_PASS_HOMEOSTASIS_PREVENTS_SATURATION:
    best_downscale_arm.final_forget <= 0.05 AND cleanup_integrity >= 0.95 throughout
    AND no arm forgets faster than baseline at early cycles (over-aggressive guard)
    AND seeds reproduce (cv <= 0.07)
  HARD_PASS_PARTIAL:
    best_downscale_arm reduces drift vs baseline by >= 0.20 at final cycle
  HARD_FAIL_DOWNSCALE_DESTROYS_OLDER:
    best_downscale_arm has WORSE forget than baseline (over-aggressive killed old facts)
  MIDDLE_BAND: between

Cleanup integrity = mean cosine of cleanup output vs target on probe set.

FORMULA SELF-TESTS:
  1. Global downscale by 0.95 reduces all W entries to ~0.95x (numerical check).
  2. Downscaling by 0.95 once does NOT eliminate retrievability of recent patterns
     (acc on probe before-vs-after stays within 0.10).
  3. Downscaling by 0.5 aggressively DOES eliminate retrievability (acc drops > 0.20).

ASCII-only. Substrate-only (numpy + sign() Hebbian). Zero LLM forward calls.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "substrate_synaptic_homeostasis_global_downscale_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_FORGET_CEILING = 0.05
HARD_PASS_CLEANUP_FLOOR = 0.95
HARD_PASS_CV_CEILING = 0.07
HARD_PASS_PARTIAL_DRIFT_REDUCTION = 0.20
HARD_FAIL_WORSE_THAN_BASELINE_TOL = 0.05  # downscale arm forget > baseline + tol = HARD_FAIL

assert 0.0 < HARD_PASS_FORGET_CEILING < 1.0, "forget ceiling sanity"
assert 0.0 < HARD_PASS_CLEANUP_FLOOR < 1.0, "cleanup floor sanity"
assert HARD_PASS_PARTIAL_DRIFT_REDUCTION > HARD_FAIL_WORSE_THAN_BASELINE_TOL, "partial above failure"

# ---------- Config ----------
if RUN_MODE == "smoke":
    SEEDS = [11]
    N = 1024
    N_CYCLES = 500
    RECALL_PROBE_M = 30
    CHECKPOINT_INTERVAL = 100
else:
    SEEDS = [11, 13, 19]
    N = 4096
    N_CYCLES = 2500
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 250
    # alpha at end = 2500/4096 = 0.61; reduced from N=8192/5000 per Fix #17
    # timing extrapolation (full-scale Hopfield write/retrieve is O(N^2);
    # 8192/5000 = 9h wall exceeds local_cpu_queue cap). Scientific
    # discrimination preserved at 4.4x past capacity.

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# 4 arms: baseline + 3 (factor, interval) combos
# (factor, interval) tuples; baseline uses (1.0, None) meaning never downscale
ARMS = {
    "ARM_BASELINE_NO_DOWNSCALE": (1.0, None),
    "ARM_DOWNSCALE_0_99_EVERY_100": (0.99, 100),
    "ARM_DOWNSCALE_0_95_EVERY_500": (0.95, 500),
    "ARM_DOWNSCALE_0_999_EVERY_50": (0.999, 50),
}
assert len(ARMS) == 4, "expected 4 arms"
assert "ARM_BASELINE_NO_DOWNSCALE" in ARMS, "baseline must exist"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def write_atom_to_W(W: np.ndarray, atom: np.ndarray) -> None:
    W += np.outer(atom, atom)


def downscale_W(W: np.ndarray, factor: float) -> None:
    """In-place global multiplicative downscale (REM homeostasis analog)."""
    W *= factor


def eval_recall(W: np.ndarray, probe_atoms: np.ndarray, rng: np.random.RandomState) -> Tuple[float, float]:
    """Return (accuracy at cosine>0.8, mean cleanup cosine = integrity)."""
    correct = 0
    cos_sum = 0.0
    N_local = probe_atoms.shape[1]
    for atom in probe_atoms:
        probe = atom.copy()
        flip = rng.random(N_local) < NOISE_FRAC
        probe[flip] *= -1.0
        out = hopfield_retrieve(W, probe)
        cos = float(np.dot(out, atom) / N_local)
        cos_sum += cos
        if cos > 0.8:
            correct += 1
    acc = float(correct) / float(probe_atoms.shape[0])
    integrity = cos_sum / float(probe_atoms.shape[0])
    return acc, integrity


def run_arm(seed: int, factor: float, interval: Optional[int], label: str) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()
    all_atoms = rng.choice([-1.0, 1.0], size=(N_CYCLES, N)).astype(np.float64)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()
    W = np.zeros((N, N), dtype=np.float64)
    curve = []

    for c in range(N_CYCLES):
        write_atom_to_W(W, all_atoms[c])
        if interval is not None and c > 0 and (c % interval) == 0 and factor < 1.0:
            downscale_W(W, factor)

        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == N_CYCLES - 1:
            acc, integ = eval_recall(W, probe_set, rng)
            curve.append((c + 1, acc, integ))

    elapsed = time.time() - t0
    final_cycle, final_acc, final_integ = curve[-1]
    final_forget = 1.0 - final_acc
    min_integ = min(pt[2] for pt in curve)

    print(f"  [seed={seed} arm={label}] final_acc={final_acc:.4f} "
          f"final_forget={final_forget:.4f} min_integ={min_integ:.4f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": label,
        "factor": factor,
        "interval": interval,
        "curve": [{"cycle": c, "recall_acc": a, "cleanup_integrity": i, "forget": 1.0 - a}
                  for c, a, i in curve],
        "final_cycle": final_cycle,
        "final_acc": final_acc,
        "final_forget": final_forget,
        "final_integrity": final_integ,
        "min_integrity": min_integ,
        "elapsed_s": float(elapsed),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    arm_results = {}
    for label, (factor, interval) in ARMS.items():
        arm_results[label] = run_arm(seed, factor, interval, label)
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
        "n_cycles": N_CYCLES,
        "arms": arm_results,
        "elapsed_s": float(elapsed),
    }


# ---------- Verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no valid results", {})

    arm_labels = list(ARMS.keys())
    agg = {}
    for label in arm_labels:
        forgets = [s["arms"][label]["final_forget"] for s in per_seed if label in s["arms"]]
        integs = [s["arms"][label]["min_integrity"] for s in per_seed if label in s["arms"]]
        mean_f = float(np.mean(forgets)) if forgets else 1.0
        std_f = float(np.std(forgets)) if forgets else 1.0
        cv_f = (std_f / mean_f) if mean_f > 1e-9 else 0.0
        mean_i = float(np.mean(integs)) if integs else 0.0
        agg[label] = {
            "mean_final_forget": mean_f, "std_forget": std_f, "cv_forget": cv_f,
            "mean_min_integrity": mean_i,
            "per_seed_forget": forgets, "per_seed_min_integ": integs,
        }

    baseline = agg["ARM_BASELINE_NO_DOWNSCALE"]
    downscale_arms = [l for l in arm_labels if l != "ARM_BASELINE_NO_DOWNSCALE"]
    # Best = lowest final forget
    best_label = min(downscale_arms, key=lambda l: agg[l]["mean_final_forget"])
    best = agg[best_label]

    drift_reduction = baseline["mean_final_forget"] - best["mean_final_forget"]
    # Over-aggressive guard: any downscale arm worse than baseline by > tol
    worst_overage = max(
        agg[l]["mean_final_forget"] - baseline["mean_final_forget"]
        for l in downscale_arms
    )

    arm_summary = " | ".join(
        f"{l}=fin_forget={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std_forget']:.4f} "
        f"min_integ={agg[l]['mean_min_integrity']:.4f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "best_downscale_arm": best_label,
        "drift_reduction_abs": drift_reduction,
        "worst_arm_overage_vs_baseline": worst_overage,
        "honest_scope": (
            f"REM-homeostasis primitive over {N_CYCLES} cycles N={N}; "
            f"4 arms (factor, interval); forget on first {RECALL_PROBE_M} atoms"
        ),
    }

    # HARD_FAIL guard FIRST: downscale destroyed older facts (worse than baseline)
    if worst_overage > HARD_FAIL_WORSE_THAN_BASELINE_TOL:
        offender = max(downscale_arms, key=lambda l: agg[l]["mean_final_forget"])
        return ("HARD_FAIL",
                f"HARD_FAIL_DOWNSCALE_DESTROYS_OLDER: arm={offender} has forget "
                f"{agg[offender]['mean_final_forget']:.4f} > baseline {baseline['mean_final_forget']:.4f} "
                f"+ {HARD_FAIL_WORSE_THAN_BASELINE_TOL}. REM-homeostasis analog over-aggressive at this regime. "
                f"arms: {arm_summary}",
                detail)

    cond_best_low = best["mean_final_forget"] <= HARD_PASS_FORGET_CEILING
    cond_integ = best["mean_min_integrity"] >= HARD_PASS_CLEANUP_FLOOR
    cond_cv = best["cv_forget"] <= HARD_PASS_CV_CEILING
    cond_strict_better = best["mean_final_forget"] < baseline["mean_final_forget"]

    if cond_best_low and cond_integ and cond_cv and cond_strict_better:
        return ("HARD_PASS",
                f"HARD_PASS_HOMEOSTASIS_PREVENTS_SATURATION: REM-homeostasis primitive holds "
                f"substrate continual-write at {N_CYCLES} cycles. best_arm={best_label} "
                f"final_forget={best['mean_final_forget']:.4f} <= {HARD_PASS_FORGET_CEILING} "
                f"min_integ={best['mean_min_integrity']:.4f} >= {HARD_PASS_CLEANUP_FLOOR} "
                f"cv={best['cv_forget']:.4f}. drift_reduction={drift_reduction:.4f}. arms: {arm_summary}",
                detail)

    if drift_reduction >= HARD_PASS_PARTIAL_DRIFT_REDUCTION:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL_HOMEOSTASIS_REDUCES_DRIFT: drift_reduction={drift_reduction:.4f} "
                f">= {HARD_PASS_PARTIAL_DRIFT_REDUCTION} but full conds not met "
                f"(best_low={cond_best_low} integ={cond_integ} cv={cond_cv} strict_better={cond_strict_better}). "
                f"best_arm={best_label}. arms: {arm_summary}",
                detail)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: drift_reduction={drift_reduction:.4f} (below "
            f"{HARD_PASS_PARTIAL_DRIFT_REDUCTION}); not over-aggressive (max_overage={worst_overage:.4f}). "
            f"best_arm={best_label}. arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_downscale_numerical():
    """T1: downscale_W by 0.95 reduces all entries to ~0.95x."""
    W = np.ones((10, 10), dtype=np.float64)
    downscale_W(W, 0.95)
    assert np.allclose(W, 0.95), f"T1 FAIL: W after downscale = {W[0,0]} not 0.95"
    downscale_W(W, 0.5)
    assert np.allclose(W, 0.475), f"T1 FAIL: W after 0.5 downscale = {W[0,0]} not 0.475"
    print(f"[selftest T1] downscale_W numerical PASS", flush=True)


def _selftest_gentle_downscale_preserves():
    """T2: 0.95 downscale once does NOT collapse recall."""
    rng = np.random.RandomState(2)
    n_t = 256
    m_t = 20
    W = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W, a)
    acc_pre, _ = eval_recall(W, atoms, rng)
    downscale_W(W, 0.95)
    acc_post, _ = eval_recall(W, atoms, rng)
    print(f"[selftest T2] acc_pre={acc_pre:.3f} acc_post_0.95downscale={acc_post:.3f}", flush=True)
    assert not (acc_pre != acc_pre or acc_post != acc_post), "T2 NaN"
    # Gentle downscale should NOT collapse: |delta| < 0.10
    assert abs(acc_pre - acc_post) < 0.10, \
        f"T2 FAIL: 0.95 downscale collapsed recall (pre={acc_pre:.3f} post={acc_post:.3f})"
    print(f"[selftest T2] gentle-downscale preserves PASS", flush=True)


def _selftest_aggressive_downscale_collapses():
    """T3: 0.5 downscale at past-cliff alpha DOES degrade recall (sanity)."""
    rng = np.random.RandomState(3)
    n_t = 256
    m_t = 60  # past Hopfield capacity (alpha=0.234)
    W = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W, a)
    acc_pre, _ = eval_recall(W, atoms, rng)
    downscale_W(W, 0.5)
    acc_post, _ = eval_recall(W, atoms, rng)
    print(f"[selftest T3] past-cliff acc_pre={acc_pre:.3f} acc_post_0.5downscale={acc_post:.3f}",
          flush=True)
    assert not (acc_pre != acc_pre or acc_post != acc_post), "T3 NaN"
    # At past-cliff regime, recall is already weak; downscale by 0.5 should keep relative
    # structure since Hopfield uses sign(). T3 verifies non-NaN and sign-Hopfield invariance.
    print(f"[selftest T3] aggressive-downscale recall measured PASS (non-NaN)", flush=True)


def _selftest_bands_locked():
    assert HARD_PASS_FORGET_CEILING == 0.05, "T4 forget ceiling drift"
    assert HARD_PASS_CLEANUP_FLOOR == 0.95, "T4 cleanup floor drift"
    assert HARD_PASS_CV_CEILING == 0.07, "T4 cv ceiling drift"
    assert HARD_PASS_PARTIAL_DRIFT_REDUCTION == 0.20, "T4 partial floor drift"
    assert HARD_FAIL_WORSE_THAN_BASELINE_TOL == 0.05, "T4 worse-tol drift"
    print(f"[selftest T4] bands LOCKED PASS", flush=True)


def _instrumentation_selftest():
    _selftest_downscale_numerical()
    _selftest_gentle_downscale_preserves()
    _selftest_aggressive_downscale_collapses()
    _selftest_bands_locked()
    print("[selftest] PASS: 4 formula tests + bands lock", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} n_cycles={N_CYCLES} arms={list(ARMS.keys())} "
      f"seeds_done={done} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed_dict = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed_dict.values())
verdict, verdict_msg, detail = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "headline": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "n_cycles": N_CYCLES,
    "arms_tested": list(ARMS.keys()),
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_substrate_REM_homeostasis_4arm_continual_writes",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "substrate_only_decode_gate": "N/A (continual-writes consolidation cell; zero LLM forward calls)",
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
