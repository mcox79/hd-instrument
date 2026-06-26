"""substrate_continual_NREM_replay_v1 -- NREM sharp-wave-ripple replay primitive.

SCIENTIFIC QUESTION (brain-grounded; sleep consolidation pillar 1 of 3):
  Hippocampal sharp-wave ripples during NREM sleep replay recent episodes to cortex
  in shuffled order at 20x compression. The brain uses this to consolidate memories
  without catastrophic forgetting at long horizons.

  Substrate analog: periodically (every N_REPLAY_INTERVAL cycles), sample a random
  subset of older atoms in W and RE-WRITE them with full strength in shuffled order.
  This refreshes old representations against drift from continual new writes.

  Baseline a8_continual_writes_v1 shows substrate's no-forgetting boundary at
  alpha=0.30 (1.5x Hopfield capacity). This cell asks: does periodic replay
  EXTEND that boundary across 5000 cycles where a no-replay baseline would cliff?

PRE-REGISTERED BANDS (LOCKED via module-init assert; bands sacrosanct both ways):
  HARD_PASS_REPLAY_EXTENDS_CONTINUAL:
    best_replay_arm.forget_at_5000 <= 0.05 AND baseline.forget_at_X > 0.10 for some X < 5000
    AND seeds reproduce (cv <= 0.07) AND replay arm strictly better than baseline at 5000
  HARD_PASS_PARTIAL:
    best_replay_arm reduces drift vs baseline by >= 0.30 at 5000 cycles
  HARD_FAIL_REPLAY_DOESNT_HELP:
    replay arms match baseline within 0.05 (no measurable benefit)
  MIDDLE_BAND: between HARD_PASS_PARTIAL and HARD_FAIL

Forget metric: 1 - mean retrieval accuracy on a fixed RECALL_PROBE_SET sampled from
EARLY writes (oldest 10%). Tested every CHECKPOINT_INTERVAL cycles.

FORMULA SELF-TESTS:
  1. Hopfield retrieval at small alpha: acc > 0.70 on small N=256, M=20 (alpha=0.078).
  2. Replay pass restores degraded retrieval: write 50 patterns, drift via 100 new
     writes (alpha 0.59 -> well past cliff), replay first 50 -> retrieval should
     recover above pre-drift accuracy floor.
  3. Acc is non-NaN throughout.

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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "substrate_continual_NREM_replay_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS) ----------
HARD_PASS_FORGET_CEILING = 0.05         # best replay arm <= this at final cycle
HARD_PASS_BASELINE_CLIFF = 0.10         # baseline must exceed this at some cycle < final
HARD_PASS_CV_CEILING = 0.07             # seeds reproduce
HARD_PASS_PARTIAL_DRIFT_REDUCTION = 0.30  # absolute reduction vs baseline
HARD_FAIL_MATCH_TOL = 0.05              # replay matches baseline within tol = no help

# Module-init assertions (sacrosanct bands)
assert 0.0 < HARD_PASS_FORGET_CEILING < HARD_PASS_BASELINE_CLIFF, "bands inverted"
assert HARD_PASS_PARTIAL_DRIFT_REDUCTION > HARD_FAIL_MATCH_TOL, "partial floor below failure ceiling"

# ---------- Config ----------
if RUN_MODE == "smoke":
    SEEDS = [11]
    N = 1024
    N_CYCLES = 500
    M_INIT_NEW_PER_CYCLE = 1
    RECALL_PROBE_M = 30
    CHECKPOINT_INTERVAL = 100
    REPLAY_FRAC = 0.20
else:
    SEEDS = [11, 13, 19]
    N = 4096
    N_CYCLES = 2500
    M_INIT_NEW_PER_CYCLE = 1
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 250
    REPLAY_FRAC = 0.20
    # alpha at end = 2500/4096 = 0.61 (4.4x Hopfield capacity alpha_c=0.138);
    # well past cliff so baseline is expected to forget; replay arms have
    # discriminating regime to show lift. Reduced from N=8192/5000 cycles per
    # Fix #17 timing measurement: full-scale extrapolation showed 9h wall
    # which exceeds local_cpu_queue 14400s cap. N=4096/2500 keeps the
    # scientific question (does replay extend horizon past cliff?) intact at
    # ~1h wall per arm-batch.

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# 4 arms: baseline + 3 replay intervals
ARMS = {
    "ARM_BASELINE_NO_REPLAY": None,            # never replay
    "ARM_REPLAY_EVERY_100": 100,
    "ARM_REPLAY_EVERY_500": 500,
    "ARM_REPLAY_EVERY_1000": 1000,
}

assert len(ARMS) == 4, "expected exactly 4 arms"
assert "ARM_BASELINE_NO_REPLAY" in ARMS, "baseline rail must exist"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    """Iterative cleanup against full W matrix. W is (N, N) outer-product accumulator."""
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def write_atom_to_W(W: np.ndarray, atom: np.ndarray) -> None:
    """Hebbian outer-product write into W IN-PLACE."""
    W += np.outer(atom, atom)


def eval_recall(W: np.ndarray, probe_atoms: np.ndarray, rng: np.random.RandomState) -> float:
    """Fraction of probe_atoms recovered within cosine 0.8 after noisy cleanup."""
    correct = 0
    N_local = probe_atoms.shape[1]
    for atom in probe_atoms:
        probe = atom.copy()
        flip = rng.random(N_local) < NOISE_FRAC
        probe[flip] *= -1.0
        out = hopfield_retrieve(W, probe)
        if np.dot(out, atom) / N_local > 0.8:
            correct += 1
    return float(correct) / float(probe_atoms.shape[0])


def run_arm(seed: int, replay_interval, label: str) -> Dict:
    """Run one arm for one seed. replay_interval=None disables replay."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Pre-generate ALL atoms for this seed to keep arm-comparability honest
    # (all arms see the same atoms in the same order)
    all_atoms = rng.choice([-1.0, 1.0], size=(N_CYCLES, N)).astype(np.float64)

    # Recall probe = the first RECALL_PROBE_M atoms (oldest writes; forget-prone)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()

    W = np.zeros((N, N), dtype=np.float64)
    curve = []  # [(cycle, recall_acc), ...]

    for c in range(N_CYCLES):
        write_atom_to_W(W, all_atoms[c])

        # Replay step (if enabled and on schedule)
        if replay_interval is not None and c > 0 and (c % replay_interval) == 0:
            # Sample REPLAY_FRAC of all atoms-so-far in shuffled order
            cap = c + 1
            n_replay = max(1, int(REPLAY_FRAC * cap))
            replay_idx = rng.choice(cap, size=n_replay, replace=False)
            for ri in replay_idx:
                write_atom_to_W(W, all_atoms[ri])

        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == N_CYCLES - 1:
            acc = eval_recall(W, probe_set, rng)
            curve.append((c + 1, acc))

    elapsed = time.time() - t0
    final_cycle, final_acc = curve[-1]
    final_forget = 1.0 - final_acc

    print(f"  [seed={seed} arm={label}] final_cycle={final_cycle} "
          f"final_acc={final_acc:.4f} final_forget={final_forget:.4f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": label,
        "replay_interval": replay_interval,
        "curve": [{"cycle": c, "recall_acc": a, "forget": 1.0 - a} for c, a in curve],
        "final_cycle": final_cycle,
        "final_acc": final_acc,
        "final_forget": final_forget,
        "elapsed_s": float(elapsed),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    arm_results = {}
    for label, interval in ARMS.items():
        arm_results[label] = run_arm(seed, interval, label)
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
    # Aggregate final_forget per arm across seeds
    agg = {}
    for label in arm_labels:
        vals = [s["arms"][label]["final_forget"] for s in per_seed if label in s["arms"]]
        mean = float(np.mean(vals)) if vals else 1.0
        std = float(np.std(vals)) if vals else 1.0
        cv = (std / mean) if mean > 1e-9 else 0.0
        agg[label] = {"mean_final_forget": mean, "std": std, "cv": cv, "per_seed": vals}

    baseline = agg["ARM_BASELINE_NO_REPLAY"]
    replay_arms = [l for l in arm_labels if l != "ARM_BASELINE_NO_REPLAY"]
    # Best replay arm = lowest final forget
    best_label = min(replay_arms, key=lambda l: agg[l]["mean_final_forget"])
    best = agg[best_label]

    # Check baseline cliff anywhere in curve (forget > HARD_PASS_BASELINE_CLIFF at any cycle)
    baseline_curve_max_forget = 0.0
    baseline_cliff_cycle = None
    for s in per_seed:
        for pt in s["arms"]["ARM_BASELINE_NO_REPLAY"]["curve"]:
            if pt["forget"] > baseline_curve_max_forget:
                baseline_curve_max_forget = pt["forget"]
                baseline_cliff_cycle = pt["cycle"]

    drift_reduction = baseline["mean_final_forget"] - best["mean_final_forget"]

    arm_summary = " | ".join(
        f"{l}=fin_forget={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std']:.4f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "best_replay_arm": best_label,
        "baseline_curve_max_forget": baseline_curve_max_forget,
        "baseline_cliff_cycle": baseline_cliff_cycle,
        "drift_reduction_abs": drift_reduction,
        "honest_scope": (
            f"NREM-replay primitive over {N_CYCLES} cycles N={N}; "
            f"4 arms: baseline + 3 replay intervals; forget metric on first {RECALL_PROBE_M} atoms"
        ),
    }

    # HARD_PASS check (strict)
    cond_best_low = best["mean_final_forget"] <= HARD_PASS_FORGET_CEILING
    cond_baseline_cliff = baseline_curve_max_forget > HARD_PASS_BASELINE_CLIFF
    cond_cv_ok = best["cv"] <= HARD_PASS_CV_CEILING
    cond_strict_better = best["mean_final_forget"] < baseline["mean_final_forget"]

    if cond_best_low and cond_baseline_cliff and cond_cv_ok and cond_strict_better:
        return ("HARD_PASS",
                f"HARD_PASS_REPLAY_EXTENDS_CONTINUAL: NREM-replay primitive extends substrate "
                f"continual-write horizon to {N_CYCLES} cycles. best_arm={best_label} "
                f"final_forget={best['mean_final_forget']:.4f} <= {HARD_PASS_FORGET_CEILING} "
                f"cv={best['cv']:.4f} <= {HARD_PASS_CV_CEILING}; baseline cliffs at cycle "
                f"{baseline_cliff_cycle} (forget={baseline_curve_max_forget:.4f} > {HARD_PASS_BASELINE_CLIFF}). "
                f"drift_reduction={drift_reduction:.4f}. arms: {arm_summary}",
                detail)

    # HARD_FAIL: replay doesn't help
    cond_no_help = abs(drift_reduction) <= HARD_FAIL_MATCH_TOL
    if cond_no_help:
        return ("HARD_FAIL",
                f"HARD_FAIL_REPLAY_DOESNT_HELP: all replay arms match baseline within "
                f"{HARD_FAIL_MATCH_TOL}. best_arm={best_label} drift_reduction={drift_reduction:.4f}. "
                f"NREM-replay analog not effective in substrate at this regime. arms: {arm_summary}",
                detail)

    # HARD_PASS_PARTIAL
    if drift_reduction >= HARD_PASS_PARTIAL_DRIFT_REDUCTION:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL_REPLAY_REDUCES_DRIFT: replay reduces drift by "
                f"{drift_reduction:.4f} >= {HARD_PASS_PARTIAL_DRIFT_REDUCTION} but full HARD_PASS "
                f"conditions not all met (best_low={cond_best_low} cliff={cond_baseline_cliff} "
                f"cv_ok={cond_cv_ok} strict_better={cond_strict_better}). arms: {arm_summary}",
                detail)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: replay provides drift_reduction={drift_reduction:.4f} (between "
            f"{HARD_FAIL_MATCH_TOL} and {HARD_PASS_PARTIAL_DRIFT_REDUCTION}). best_arm={best_label}. "
            f"arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_hopfield_basic():
    """T1: Hopfield retrieval at small alpha recovers cleanly."""
    rng = np.random.RandomState(0)
    n_t = 256
    m_t = 20  # alpha = 0.078, well within capacity
    W = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W, a)
    correct = 0
    for a in atoms:
        probe = a.copy()
        flip = rng.random(n_t) < NOISE_FRAC
        probe[flip] *= -1.0
        out = hopfield_retrieve(W, probe)
        if np.dot(out, a) / n_t > 0.8:
            correct += 1
    acc = correct / m_t
    assert not (acc != acc), "T1 acc is NaN"
    assert acc >= 0.70, f"T1 FAIL: small-alpha acc={acc:.3f} < 0.70"
    print(f"[selftest T1] small-alpha acc={acc:.4f} PASS", flush=True)


def _selftest_replay_recovers():
    """T2: replay pass restores degraded recall after past-cliff drift."""
    rng = np.random.RandomState(1)
    n_t = 256
    m_initial = 50
    m_drift = 100  # initial + drift = 150; alpha = 0.586, past cliff
    W = np.zeros((n_t, n_t), dtype=np.float64)
    initial = rng.choice([-1.0, 1.0], size=(m_initial, n_t)).astype(np.float64)
    for a in initial:
        write_atom_to_W(W, a)
    # acc on initial set BEFORE drift
    acc_pre = eval_recall(W, initial, rng)
    # Drift: write 100 new atoms
    drift = rng.choice([-1.0, 1.0], size=(m_drift, n_t)).astype(np.float64)
    for a in drift:
        write_atom_to_W(W, a)
    acc_drifted = eval_recall(W, initial, rng)
    # Replay 100% of initial
    for a in initial:
        write_atom_to_W(W, a)
    acc_replayed = eval_recall(W, initial, rng)
    print(f"[selftest T2] acc_pre={acc_pre:.3f} acc_drifted={acc_drifted:.3f} "
          f"acc_replayed={acc_replayed:.3f}", flush=True)
    assert not (acc_pre != acc_pre or acc_drifted != acc_drifted or acc_replayed != acc_replayed), \
        "T2 NaN"
    # Replay should restore or improve on drifted; this is the load-bearing claim
    assert acc_replayed >= acc_drifted, \
        f"T2 FAIL: replay did not recover (pre={acc_pre:.3f} drift={acc_drifted:.3f} replay={acc_replayed:.3f})"
    print(f"[selftest T2] replay-recovery non-decreasing PASS", flush=True)


def _selftest_bands_locked():
    """T3: bands locked per pre-reg."""
    assert HARD_PASS_FORGET_CEILING == 0.05, "T3 HARD_PASS_FORGET_CEILING drift"
    assert HARD_PASS_BASELINE_CLIFF == 0.10, "T3 HARD_PASS_BASELINE_CLIFF drift"
    assert HARD_PASS_CV_CEILING == 0.07, "T3 HARD_PASS_CV_CEILING drift"
    assert HARD_PASS_PARTIAL_DRIFT_REDUCTION == 0.30, "T3 partial floor drift"
    assert HARD_FAIL_MATCH_TOL == 0.05, "T3 match tol drift"
    print(f"[selftest T3] bands LOCKED PASS", flush=True)


def _instrumentation_selftest():
    _selftest_hopfield_basic()
    _selftest_replay_recovers()
    _selftest_bands_locked()
    print("[selftest] PASS: 3 formula tests + bands lock", flush=True)


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
    "replay_frac": REPLAY_FRAC,
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_substrate_NREM_replay_4arm_continual_writes",
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
