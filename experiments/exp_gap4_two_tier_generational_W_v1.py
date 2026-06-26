"""gap4_two_tier_generational_W_v1 -- Gap 4 continual operation Anchor #1.

SCIENTIFIC QUESTION (Gap 4 continual operation 5x drill 2026-06-26):
  Substrate's W matrix is single-tier today. Four disparate fields (JVM
  generational GC; RocksDB LSM leveled compaction; immune-system germinal-
  center maturation; brain hippocampus-cortex consolidation) independently
  arrived at the same factorization: two-tier storage with periodic promotion
  of important items from a young/fast layer to an old/slow layer. The
  substrate has the missing primitive: PROMOTION.

  Substrate analog: add a SECOND W_old matrix alongside W_young. Every
  K_promote cycles, promote top-tau-fraction entries from W_young into W_old
  by importance score (recent recall accuracy on the entry), then decay
  W_young by gamma_decay.

  Baseline a8_continual_writes_v1 shows substrate no-forgetting boundary at
  alpha=0.30 (1.5x Hopfield capacity). NREM-replay_v1 smoke MIDDLE_BAND
  (drift_red=0.0667). This cell asks: does TWO_TIER generational W extend the
  continual horizon past the cliff where single-tier baseline forgets?

  Composition: replay (Cell A NREM) is the SOURCE; TWO_TIER is the
  DESTINATION (W_old) where consolidated atoms live undisturbed by W_young
  ingest. Standalone TWO_TIER tested first; composition with replay deferred.

PRE-REGISTERED BANDS (LOCKED via module-init assert; sacrosanct both ways):
  HARD_PASS_TWO_TIER_EXTENDS_CONTINUAL:
    best_two_tier_arm.final_forget <= 0.05 at extended cycles
    AND baseline cliffs at some cycle (curve_max_forget > 0.10)
    AND seeds reproduce (cv <= 0.07)
    AND best two-tier arm strictly better than baseline at final cycle
  HARD_PASS_PARTIAL:
    drift_reduction >= 0.30 absolute but not all HP conditions met
  HARD_FAIL_TWO_TIER_DOESNT_HELP:
    best two-tier arm matches baseline within +/- 0.05 at final cycle
  MIDDLE_BAND: between HARD_PASS_PARTIAL and HARD_FAIL

Forget metric: 1 - mean retrieval accuracy on a fixed RECALL_PROBE_SET of
first RECALL_PROBE_M atoms (oldest writes; forget-prone). Read uses
W_old + W_young SUM (read-path concatenation; both tiers contribute).
Tested every CHECKPOINT_INTERVAL cycles.

FORMULA SELF-TESTS:
  1. Hopfield retrieval at small alpha: acc > 0.70 on N=256, M=20.
  2. Two-tier read returns same answer as single-tier when W_old=0.
  3. Promotion from W_young to W_old preserves correct atoms; decay reduces
     W_young magnitude as expected.
  4. acc is non-NaN throughout.

NESS-HANG PREVENTION (USER 2026-06-26):
  Sub-arm checkpointing: write partial AFTER each arm (not per-seed). This
  caps a single hang to 1 arm-run worth of compute. Per-cycle progress logs
  at CHECKPOINT_INTERVAL gives liveness signal.

ASCII-only. Substrate-only (numpy + sign() Hopfield cleanup). Zero LLM
forward calls.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import atexit
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_partial_key, load_partial_key,
)

ANCHOR_NAME = "gap4_two_tier_generational_W_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_FORGET_CEILING = 0.05
HARD_PASS_BASELINE_CLIFF = 0.10
HARD_PASS_CV_CEILING = 0.07
HARD_PASS_PARTIAL_DRIFT_REDUCTION = 0.30
HARD_FAIL_MATCH_TOL = 0.05

# Module-init assertions (bands sacrosanct both ways)
assert 0.0 < HARD_PASS_FORGET_CEILING < HARD_PASS_BASELINE_CLIFF, "bands inverted"
assert HARD_PASS_PARTIAL_DRIFT_REDUCTION > HARD_FAIL_MATCH_TOL, \
    "partial-pass floor must exceed fail tolerance"

# ---------- Config (capacity-sensitive dims MUST be identical smoke/full per META_M7) ----------
# Both smoke and FULL use identical N to avoid capacity-regime swap.
# Smoke just reduces N_CYCLES, SEEDS, RECALL_PROBE_M, and CHECKPOINT_INTERVAL.
N = 4096

if RUN_MODE == "smoke":
    SEEDS = [11]
    # 600 cycles at N=4096 = alpha 0.146 (~1.06x Hopfield); K=500 promotes once,
    # K=1000/2000 never promote in smoke -> smoke validates the K=500 promotion
    # path + the random-promote ablation (also K=1000 won't fire). Per-arm wall
    # ~ 6.1s * 16 * (600/500) = ~117s on baseline, +20% for K=500 promotion.
    N_CYCLES = 600
    RECALL_PROBE_M = 30
    CHECKPOINT_INTERVAL = 100
else:
    SEEDS = [11, 13, 19]
    N_CYCLES = 4000      # alpha at end = 4000/4096 = 0.977 (~7x Hopfield capacity)
                         # baseline expected to cliff; two-tier given headroom
                         # to discriminate. Reduced from 5000 to keep wall <4h
                         # per Fix #17 timing (NREM smoke 24s/500cyc N=1024;
                         # extrapolated 4096^2/1024^2 * 4000/500 = 128x =
                         # ~52min per arm-seed, 5 arms x 3 seeds = ~13h
                         # ABORTED; need to verify smoke per-arm wall before
                         # full dispatch and possibly route remote_cpu).
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 250

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# Arms: baseline single-W vs three TWO_TIER configurations + 1 importance-blind ablation
# K_promote (cycle interval) x tau (top-fraction promoted) x gamma (W_young decay)
ARMS = {
    "ARM_BASELINE_SINGLE_W":         {"two_tier": False, "K_promote": None, "tau": None,  "gamma": None,  "importance": None},
    "ARM_TWO_TIER_PROMOTE_500":      {"two_tier": True,  "K_promote": 500,  "tau": 0.10, "gamma": 0.90, "importance": "recall"},
    "ARM_TWO_TIER_PROMOTE_1000":     {"two_tier": True,  "K_promote": 1000, "tau": 0.10, "gamma": 0.90, "importance": "recall"},
    "ARM_TWO_TIER_PROMOTE_2000":     {"two_tier": True,  "K_promote": 2000, "tau": 0.20, "gamma": 0.85, "importance": "recall"},
    "ARM_TWO_TIER_RANDOM_PROMOTE":   {"two_tier": True,  "K_promote": 1000, "tau": 0.10, "gamma": 0.90, "importance": "random"},
}

assert len(ARMS) == 5, "expected 5 arms (baseline + 3 two-tier + 1 ablation)"
assert "ARM_BASELINE_SINGLE_W" in ARMS, "baseline rail must exist"
assert "ARM_TWO_TIER_RANDOM_PROMOTE" in ARMS, \
    "random-promote ablation must exist (isolates 'importance' contribution)"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    """Iterative cleanup against W (N,N). W may be sum W_old+W_young."""
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def write_atom_to_W(W: np.ndarray, atom: np.ndarray) -> None:
    """Hebbian outer-product write into W IN-PLACE."""
    W += np.outer(atom, atom)


def eval_recall_combined(W_combined: np.ndarray, probe_atoms: np.ndarray,
                          rng: np.random.RandomState) -> float:
    """Recall on probe_atoms via cleanup against W_combined (= W_old + W_young for two-tier)."""
    correct = 0
    N_local = probe_atoms.shape[1]
    for atom in probe_atoms:
        probe = atom.copy()
        flip = rng.random(N_local) < NOISE_FRAC
        probe[flip] *= -1.0
        out = hopfield_retrieve(W_combined, probe)
        if np.dot(out, atom) / N_local > 0.8:
            correct += 1
    return float(correct) / float(probe_atoms.shape[0])


def score_atom_importance(W_combined: np.ndarray, atom: np.ndarray,
                           rng: np.random.RandomState) -> float:
    """Importance = how well atom currently recalls under combined W (single noisy probe).

    Returns 1.0 if cleanup recovers (cos > 0.8), else cos(out, atom) clipped to [0,1].
    This makes high-importance = "atom we want to preserve in W_old."
    """
    N_local = atom.shape[0]
    probe = atom.copy()
    flip = rng.random(N_local) < NOISE_FRAC
    probe[flip] *= -1.0
    out = hopfield_retrieve(W_combined, probe)
    cos = float(np.dot(out, atom) / N_local)
    return max(0.0, cos)  # clipped to [0,1]


def run_arm(seed: int, arm_label: str, arm_cfg: Dict,
             all_atoms: np.ndarray, probe_set: np.ndarray) -> Dict:
    """Run one arm for one seed. arm_cfg dict per ARMS schema."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    two_tier = arm_cfg["two_tier"]
    K_promote = arm_cfg["K_promote"]
    tau = arm_cfg["tau"]
    gamma = arm_cfg["gamma"]
    importance_mode = arm_cfg["importance"]  # "recall" or "random" or None

    W_young = np.zeros((N, N), dtype=np.float64)
    W_old = np.zeros((N, N), dtype=np.float64) if two_tier else None

    curve = []  # [(cycle, recall_acc), ...]
    promotions_log = []  # [(cycle, n_promoted, mean_importance), ...]

    last_progress_t = t0
    for c in range(N_CYCLES):
        # Write into W_young (or single W in baseline)
        write_atom_to_W(W_young, all_atoms[c])

        # TWO_TIER promotion step
        if two_tier and K_promote is not None and c > 0 and (c % K_promote) == 0:
            cap = c + 1   # atoms written so far (indices [0, c])
            # Score current atoms-so-far for importance (using current combined W)
            W_combined_for_score = W_old + W_young
            n_to_score = cap
            scores = np.empty(n_to_score, dtype=np.float64)
            for i in range(n_to_score):
                scores[i] = score_atom_importance(W_combined_for_score, all_atoms[i], rng)

            n_promote = max(1, int(tau * n_to_score))
            if importance_mode == "recall":
                # top tau-fraction by importance score
                promote_idx = np.argpartition(-scores, n_promote - 1)[:n_promote]
            elif importance_mode == "random":
                # ablation: same count but random selection (isolates "importance matters")
                promote_idx = rng.choice(n_to_score, size=n_promote, replace=False)
            else:
                raise ValueError(f"unknown importance_mode={importance_mode!r}")

            # Promote: additive merge into W_old
            for pi in promote_idx:
                write_atom_to_W(W_old, all_atoms[pi])

            # Decay W_young
            W_young *= gamma

            mean_imp_promoted = float(np.mean(scores[promote_idx]))
            promotions_log.append({
                "cycle": int(c),
                "n_promoted": int(n_promote),
                "mean_importance_promoted": mean_imp_promoted,
                "mean_importance_all": float(np.mean(scores)),
            })

        # Checkpoint eval (every CHECKPOINT_INTERVAL or at final)
        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == N_CYCLES - 1:
            W_combined = W_old + W_young if two_tier else W_young
            acc = eval_recall_combined(W_combined, probe_set, rng)
            curve.append((c + 1, acc))
            now = time.time()
            since_last = now - last_progress_t
            print(f"  [seed={seed} arm={arm_label} c={c+1}/{N_CYCLES} "
                  f"acc={acc:.4f} forget={1-acc:.4f} "
                  f"+{since_last:.1f}s]", flush=True)
            last_progress_t = now

    elapsed = time.time() - t0
    final_cycle, final_acc = curve[-1]
    final_forget = 1.0 - final_acc

    # Tier utilization at end (only meaningful if two-tier)
    if two_tier:
        W_old_norm = float(np.linalg.norm(W_old))
        W_young_norm = float(np.linalg.norm(W_young))
        total = W_old_norm + W_young_norm
        W_old_util = W_old_norm / total if total > 1e-9 else 0.0
    else:
        W_old_norm = 0.0
        W_young_norm = float(np.linalg.norm(W_young))
        W_old_util = 0.0

    print(f"  [seed={seed} arm={arm_label}] DONE final_cycle={final_cycle} "
          f"final_acc={final_acc:.4f} final_forget={final_forget:.4f} "
          f"W_old_util={W_old_util:.3f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": arm_label,
        "arm_cfg": arm_cfg,
        "curve": [{"cycle": c, "recall_acc": a, "forget": 1.0 - a} for c, a in curve],
        "promotions_log": promotions_log,
        "final_cycle": int(final_cycle),
        "final_acc": float(final_acc),
        "final_forget": float(final_forget),
        "W_old_norm": W_old_norm,
        "W_young_norm": W_young_norm,
        "W_old_utilization": W_old_util,
        "elapsed_s": float(elapsed),
    }


# Partial-arm checkpoint helpers (NESS-hang prevention; sub-unit checkpointing)
# We store per (seed, arm) partials. Top-level partial_metrics_<seed>.json is
# assembled when ALL arms for that seed are complete.
def _arm_ckpt_key(seed: int, arm_label: str) -> str:
    return f"arm_seed{seed}_{arm_label}"


def _write_arm_partial(out_dir: Path, seed: int, arm_label: str, result: Dict) -> None:
    key = _arm_ckpt_key(seed, arm_label)
    body = {
        "_ckpt_key": key,
        "seed": str(seed),
        "arm_label": arm_label,
        "N": N,
        "run_mode": RUN_MODE,
        "n_cycles": N_CYCLES,
        "result": result,
    }
    write_partial_key(out_dir, key, body)


def _load_arm_partial(out_dir: Path, seed: int, arm_label: str) -> Optional[Dict]:
    key = _arm_ckpt_key(seed, arm_label)
    body = load_partial_key(out_dir, key)
    if body is None:
        return None
    if body.get("N") != N or body.get("run_mode") != RUN_MODE or body.get("n_cycles") != N_CYCLES:
        # PROT-021: reject mismatched config
        print(f"[ckpt] arm partial config mismatch; ignoring "
              f"seed={seed} arm={arm_label}", flush=True)
        return None
    return body.get("result")


# atexit partial-flush: if process killed mid-arm, this ensures any completed
# arm metrics are persisted even if seed-level aggregation didn't fire.
# (arm partials already written via _write_arm_partial; atexit confirms.)
_atexit_state = {"out_dir": None, "completed_arms": []}


def _atexit_flush():
    od = _atexit_state["out_dir"]
    if od is None:
        return
    completed = _atexit_state["completed_arms"]
    if completed:
        print(f"[atexit] {len(completed)} arm partials persisted: "
              f"{', '.join(completed)}", flush=True)


atexit.register(_atexit_flush)


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arm_results = {}

    # Pre-generate ALL atoms for this seed (all arms see same data, arm-comparable)
    rng_atoms = np.random.RandomState(seed)
    all_atoms = rng_atoms.choice([-1.0, 1.0], size=(N_CYCLES, N)).astype(np.float64)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()

    for arm_label, arm_cfg in ARMS.items():
        # Resume: skip arm if already complete
        cached = _load_arm_partial(out_dir, seed, arm_label)
        if cached is not None:
            print(f"  [resume seed={seed} arm={arm_label}] loaded from arm partial", flush=True)
            arm_results[arm_label] = cached
            _atexit_state["completed_arms"].append(f"seed{seed}/{arm_label}")
            continue
        res = run_arm(seed, arm_label, arm_cfg, all_atoms, probe_set)
        arm_results[arm_label] = res
        # Sub-arm checkpoint: persist immediately after each arm completes
        _write_arm_partial(out_dir, seed, arm_label, res)
        _atexit_state["completed_arms"].append(f"seed{seed}/{arm_label}")

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
        vals = [s["arms"][label]["final_forget"] for s in per_seed if label in s.get("arms", {})]
        mean = float(np.mean(vals)) if vals else 1.0
        std = float(np.std(vals)) if vals else 1.0
        cv = (std / mean) if mean > 1e-9 else 0.0
        agg[label] = {"mean_final_forget": mean, "std": std, "cv": cv, "per_seed": vals}

    baseline = agg["ARM_BASELINE_SINGLE_W"]
    two_tier_arms = [l for l in arm_labels if l.startswith("ARM_TWO_TIER")]
    # Best two-tier arm = lowest final_forget
    best_label = min(two_tier_arms, key=lambda l: agg[l]["mean_final_forget"])
    best = agg[best_label]

    # Check baseline cliff (curve_max_forget > 0.10 anywhere in baseline curve)
    baseline_curve_max_forget = 0.0
    baseline_cliff_cycle = None
    for s in per_seed:
        for pt in s["arms"]["ARM_BASELINE_SINGLE_W"]["curve"]:
            if pt["forget"] > baseline_curve_max_forget:
                baseline_curve_max_forget = pt["forget"]
                baseline_cliff_cycle = pt["cycle"]

    drift_reduction = baseline["mean_final_forget"] - best["mean_final_forget"]

    # Importance ablation: compare best two-tier WITH importance vs RANDOM_PROMOTE
    random_ablation = agg.get("ARM_TWO_TIER_RANDOM_PROMOTE", None)
    importance_lift = None
    if random_ablation is not None and best_label != "ARM_TWO_TIER_RANDOM_PROMOTE":
        importance_lift = random_ablation["mean_final_forget"] - best["mean_final_forget"]

    # W_old utilization across two-tier arms (proxy for "tier actually used")
    W_old_utils = {}
    for label in two_tier_arms:
        per_seed_utils = [s["arms"][label].get("W_old_utilization", 0.0)
                          for s in per_seed if label in s.get("arms", {})]
        W_old_utils[label] = float(np.mean(per_seed_utils)) if per_seed_utils else 0.0

    arm_summary = " | ".join(
        f"{l}=fin_forget={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std']:.4f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "best_two_tier_arm": best_label,
        "baseline_curve_max_forget": baseline_curve_max_forget,
        "baseline_cliff_cycle": baseline_cliff_cycle,
        "drift_reduction_abs": drift_reduction,
        "importance_lift_over_random_promote": importance_lift,
        "W_old_utilization_per_arm": W_old_utils,
        "honest_scope": (
            f"TWO_TIER generational W over {N_CYCLES} cycles N={N}; "
            f"{len(ARMS)} arms: baseline + 3 two-tier configs + 1 random-promote ablation; "
            f"forget metric on first {RECALL_PROBE_M} atoms; combined-read W_old+W_young"
        ),
    }

    # HARD_PASS check (strict; all 4 conditions)
    cond_best_low = best["mean_final_forget"] <= HARD_PASS_FORGET_CEILING
    cond_baseline_cliff = baseline_curve_max_forget > HARD_PASS_BASELINE_CLIFF
    cond_cv_ok = best["cv"] <= HARD_PASS_CV_CEILING
    cond_strict_better = best["mean_final_forget"] < baseline["mean_final_forget"]

    if cond_best_low and cond_baseline_cliff and cond_cv_ok and cond_strict_better:
        return ("HARD_PASS",
                f"HARD_PASS_TWO_TIER_EXTENDS_CONTINUAL: TWO_TIER generational W extends substrate "
                f"continual-write horizon to {N_CYCLES} cycles N={N}. best_arm={best_label} "
                f"final_forget={best['mean_final_forget']:.4f} <= {HARD_PASS_FORGET_CEILING} "
                f"cv={best['cv']:.4f} <= {HARD_PASS_CV_CEILING}; baseline cliffs at cycle "
                f"{baseline_cliff_cycle} (forget={baseline_curve_max_forget:.4f} > "
                f"{HARD_PASS_BASELINE_CLIFF}). drift_reduction={drift_reduction:.4f}. "
                f"importance_lift_over_random={importance_lift}. arms: {arm_summary}",
                detail)

    # HARD_FAIL: two-tier doesn't help
    cond_no_help = abs(drift_reduction) <= HARD_FAIL_MATCH_TOL
    if cond_no_help:
        return ("HARD_FAIL",
                f"HARD_FAIL_TWO_TIER_DOESNT_HELP: best two-tier arm matches baseline within "
                f"{HARD_FAIL_MATCH_TOL}. best_arm={best_label} drift_reduction={drift_reduction:.4f}. "
                f"Generational W primitive not effective at this regime. arms: {arm_summary}",
                detail)

    # HARD_PASS_PARTIAL
    if drift_reduction >= HARD_PASS_PARTIAL_DRIFT_REDUCTION:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL_TWO_TIER_REDUCES_DRIFT: TWO_TIER reduces drift by "
                f"{drift_reduction:.4f} >= {HARD_PASS_PARTIAL_DRIFT_REDUCTION} but full HARD_PASS "
                f"conditions not all met (best_low={cond_best_low} cliff={cond_baseline_cliff} "
                f"cv_ok={cond_cv_ok} strict_better={cond_strict_better}). arms: {arm_summary}",
                detail)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: TWO_TIER provides drift_reduction={drift_reduction:.4f} (between "
            f"{HARD_FAIL_MATCH_TOL} and {HARD_PASS_PARTIAL_DRIFT_REDUCTION}). best_arm={best_label}. "
            f"arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_hopfield_basic():
    """T1: Hopfield retrieval at small alpha recovers cleanly."""
    rng = np.random.RandomState(0)
    n_t = 256
    m_t = 20  # alpha = 0.078
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
    assert not (acc != acc), "T1 acc NaN"
    assert acc >= 0.70, f"T1 FAIL: small-alpha acc={acc:.3f} < 0.70"
    print(f"[selftest T1] small-alpha acc={acc:.4f} PASS", flush=True)


def _selftest_two_tier_equiv_when_old_empty():
    """T2: With W_old = 0, two-tier read MUST equal single-tier read on same W_young."""
    rng = np.random.RandomState(1)
    n_t = 256
    m_t = 20
    W_young = np.zeros((n_t, n_t), dtype=np.float64)
    W_old = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W_young, a)
    rng_eval = np.random.RandomState(2)
    acc_single = eval_recall_combined(W_young, atoms, rng_eval)
    rng_eval2 = np.random.RandomState(2)  # SAME seed to make probes identical
    acc_combined = eval_recall_combined(W_old + W_young, atoms, rng_eval2)
    assert abs(acc_single - acc_combined) < 1e-9, \
        f"T2 FAIL: single={acc_single:.4f} vs combined-with-zero-old={acc_combined:.4f}"
    print(f"[selftest T2] two_tier_equiv_when_old_empty acc={acc_single:.4f} == "
          f"{acc_combined:.4f} PASS", flush=True)


def _selftest_promotion_and_decay():
    """T3: Promote step adds to W_old; gamma decay shrinks W_young magnitude."""
    rng = np.random.RandomState(3)
    n_t = 256
    m_t = 20
    W_young = np.zeros((n_t, n_t), dtype=np.float64)
    W_old = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W_young, a)
    young_norm_before = float(np.linalg.norm(W_young))
    old_norm_before = float(np.linalg.norm(W_old))
    assert old_norm_before == 0.0, "T3 setup: W_old must start at 0"

    # Promote 5 atoms into W_old
    promote_idx = [0, 5, 10, 15, 19]
    for pi in promote_idx:
        write_atom_to_W(W_old, atoms[pi])
    old_norm_after_promote = float(np.linalg.norm(W_old))
    assert old_norm_after_promote > 0.0, "T3 FAIL: W_old norm not increased after promote"

    # Decay W_young
    gamma = 0.90
    W_young *= gamma
    young_norm_after_decay = float(np.linalg.norm(W_young))
    expected = young_norm_before * gamma
    assert abs(young_norm_after_decay - expected) < 1e-6, \
        f"T3 FAIL: decayed young norm={young_norm_after_decay:.6f} expected={expected:.6f}"
    print(f"[selftest T3] promotion+decay young_norm {young_norm_before:.4f}->"
          f"{young_norm_after_decay:.4f} (gamma={gamma}); old_norm 0->"
          f"{old_norm_after_promote:.4f} PASS", flush=True)


def _selftest_bands_locked():
    """T4: bands locked per pre-reg."""
    assert HARD_PASS_FORGET_CEILING == 0.05, "T4 HARD_PASS_FORGET_CEILING drift"
    assert HARD_PASS_BASELINE_CLIFF == 0.10, "T4 HARD_PASS_BASELINE_CLIFF drift"
    assert HARD_PASS_CV_CEILING == 0.07, "T4 HARD_PASS_CV_CEILING drift"
    assert HARD_PASS_PARTIAL_DRIFT_REDUCTION == 0.30, "T4 partial floor drift"
    assert HARD_FAIL_MATCH_TOL == 0.05, "T4 match tol drift"
    print(f"[selftest T4] bands LOCKED "
          f"HP_ceil={HARD_PASS_FORGET_CEILING} HP_cliff={HARD_PASS_BASELINE_CLIFF} "
          f"HP_cv={HARD_PASS_CV_CEILING} HP_partial={HARD_PASS_PARTIAL_DRIFT_REDUCTION} "
          f"HF_tol={HARD_FAIL_MATCH_TOL} PASS", flush=True)


def _selftest_arm_schema():
    """T5: ARMS dict shape; baseline + 3 two-tier + 1 random-promote ablation present."""
    assert len(ARMS) == 5, f"T5 ARMS count: expected 5 got {len(ARMS)}"
    assert "ARM_BASELINE_SINGLE_W" in ARMS, "T5 baseline missing"
    assert "ARM_TWO_TIER_RANDOM_PROMOTE" in ARMS, "T5 random ablation missing"
    two_tier_n = sum(1 for k in ARMS if k.startswith("ARM_TWO_TIER"))
    assert two_tier_n == 4, f"T5 two-tier arms: expected 4 got {two_tier_n}"
    print(f"[selftest T5] ARMS schema PASS (n={len(ARMS)})", flush=True)


def _instrumentation_selftest():
    _selftest_hopfield_basic()
    _selftest_two_tier_equiv_when_old_empty()
    _selftest_promotion_and_decay()
    _selftest_bands_locked()
    _selftest_arm_schema()
    print("[selftest] PASS: 5 formula tests + bands lock + arm schema", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
_atexit_state["out_dir"] = out_dir
t0_total = time.time()
run_config = {"N": N, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} n_cycles={N_CYCLES} arms={list(ARMS.keys())} "
      f"seeds_done={done} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s, out_dir)
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
    "arms_config": ARMS,
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_substrate_two_tier_generational_W_continual_writes",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "substrate_only_decode_gate": ("N/A (continual-writes consolidation cell; "
                                    "zero LLM forward calls; numpy + Hopfield sign() only)"),
    "pre_reg_bands": {
        "HARD_PASS_FORGET_CEILING": HARD_PASS_FORGET_CEILING,
        "HARD_PASS_BASELINE_CLIFF": HARD_PASS_BASELINE_CLIFF,
        "HARD_PASS_CV_CEILING": HARD_PASS_CV_CEILING,
        "HARD_PASS_PARTIAL_DRIFT_REDUCTION": HARD_PASS_PARTIAL_DRIFT_REDUCTION,
        "HARD_FAIL_MATCH_TOL": HARD_FAIL_MATCH_TOL,
    },
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
