"""gap4_cold_storage_no_combine_v1 -- REM revival ANCHOR_1.

SCIENTIFIC QUESTION (REM revival cold-storage drill 2026-06-26):
  Cell B (REM homeostasis) HARD_FAILed across 3 schedules: global
  multiplicative downscale (W *= 0.99) eats the dwindling-but-precious old
  tail. USER reframe: substrate should NEVER delete weights. Move stale +
  low-importance weights to a separate W_cold matrix where they sit at exact
  strength forever, and aggressively NORM-NORMALIZE (not multiplicatively
  downscale) W_active.

  Brain-lit basis:
    - Liu Neuron 2024: hippocampal engram silencing, NOT deletion
    - Yang Nature 2025: systems consolidation reorganizes engram circuitry
    - Li 2017 NComms: REM-spine pruning selective to NEW uncaptured spines
  Database analog: HotRAP LSM-tree tiered storage; SEDM merge-and-recycle.

  Cell B FAILURE FRAME: in-place destructive downscale on a single W matrix.
  THIS CELL FRAME: 2-tier W_active + W_cold; activity-gated migration; never
  delete. NO schema combination (W_cold -> W_schema deferred to Anchor #2).

  4 arms (per research handoff):
    ARM_BASELINE_NO_DOWNSCALE: rail; reproduces Cell A/B BASELINE drift
    ARM_GLOBAL_DOWNSCALE_99_100: reproduces Cell B HARD_FAIL pattern
    ARM_COLD_STORAGE_NO_COMBINE: the test (W_active+W_cold; K_thresh=2000)
    ARM_COLD_STORAGE_TAU_500: different migration threshold (K_thresh=500)

PRE-REGISTERED BANDS (LOCKED via module-init assert; sacrosanct both ways):
  HARD_PASS_COLD_STORAGE_WORKS: best cold_storage arm
    final_forget <= 0.10 on old patterns
    AND min_integrity >= 0.90 (||W_active||_F bounded)
    AND beats BASELINE drift by >= 0.30 absolute
    AND cv <= 0.07
  HARD_PASS_PARTIAL: drift_reduction >= 0.20 abs but not all HP met
  MIDDLE_BAND: drift_reduction in (0.05, 0.20)
  HARD_FAIL_COLD_STORAGE_DOESNT_HELP: drift_reduction <= 0.05

Forget metric: 1 - mean retrieval accuracy on first RECALL_PROBE_M atoms
(oldest writes; forget-prone). Read uses W_active + W_cold combined for
cold-storage arms; single W for baselines.

FORMULA SELF-TESTS:
  T1: Hopfield retrieval at small alpha recovers (>= 0.70).
  T2: Cold migration preserves atom strength exactly (no decay in cold).
  T3: Norm-normalize keeps ||W||_F at target across writes.
  T4: Bands locked per pre-reg.
  T5: ARMS dict shape; 4 arms, 1 baseline + 1 cellB-pattern + 2 cold.

NESS-HANG PREVENTION (USER 2026-06-26):
  Sub-arm checkpointing: write partial AFTER each (seed, arm).

ASCII-only. Substrate-only (numpy + sign() Hopfield cleanup). Zero LLM calls.
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

ANCHOR_NAME = "gap4_cold_storage_no_combine_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_FORGET_CEILING = 0.10
HARD_PASS_INTEGRITY_FLOOR = 0.90
HARD_PASS_DRIFT_REDUCTION = 0.30
HARD_PASS_CV_CEILING = 0.07
HARD_PASS_PARTIAL_DRIFT_REDUCTION = 0.20
HARD_FAIL_DRIFT_TOL = 0.05

# Module-init assertions (bands sacrosanct both ways)
assert HARD_PASS_PARTIAL_DRIFT_REDUCTION > HARD_FAIL_DRIFT_TOL, \
    "partial-pass floor must exceed fail tolerance"
assert HARD_PASS_DRIFT_REDUCTION > HARD_PASS_PARTIAL_DRIFT_REDUCTION, \
    "HARD_PASS drift floor must exceed partial-pass floor"
assert 0.0 < HARD_PASS_FORGET_CEILING < 1.0, "forget ceiling out of range"
assert 0.0 < HARD_PASS_INTEGRITY_FLOOR < 1.0, "integrity floor out of range"

# ---------- Config (capacity-sensitive dims MUST be identical smoke/full per META_M7) ----------
N = 4096

if RUN_MODE == "smoke":
    SEEDS = [11]
    # 500 cycles smoke. K_migrate=200 fires twice => migration logic exercised.
    # Per-arm wall estimate: ~6.1s * (4096/1024)^2 * (500/500) ~= 98s baseline;
    # cold-storage arms add migration scan O(N^2 * cap_atoms) per migrate event
    # ~= +50%. 4 arms x ~150s = ~10 min smoke total.
    N_CYCLES = 500
    RECALL_PROBE_M = 30
    CHECKPOINT_INTERVAL = 100
    K_MIGRATE_DEFAULT = 200   # smoke: ensures migration fires
    K_THRESHOLD_DEFAULT = 100
    K_THRESHOLD_TAU_500_ARM = 50
else:
    SEEDS = [11, 13, 19]
    # 2500 cycles at N=4096 = alpha=0.610 (~4.4x Hopfield capacity).
    # Per Research drill: 'baseline cliffs around alpha=0.61'.
    # Matches Cell A/B regime; sufficient headroom for cold-storage to discriminate.
    # Per-arm wall: ~6.1s * 16 * (2500/500) = ~488s baseline (~8 min).
    # Cold-storage arms add migration scan ~ +30% = ~640s (~11 min).
    # 4 arms x 3 seeds = baseline 24 min + cold (2x) ~ 90 min = ~115 min ~ 2 hr.
    # 50% safety: timeout target ~3-4 hr.
    N_CYCLES = 2500
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 250
    K_MIGRATE_DEFAULT = 500    # full: every 500 cycles
    K_THRESHOLD_DEFAULT = 2000 # weight stale > 2000 cycles eligible for cold
    K_THRESHOLD_TAU_500_ARM = 500  # tau=500 arm: shorter staleness threshold

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5
IMPORTANCE_THRESHOLD = 0.10  # below = eligible for cold migration
GLOBAL_DOWNSCALE_FACTOR = 0.99  # cell B pattern (99/100 each cycle)
NORM_TARGET_FRAC = 1.10  # normalize ||W_active||_F to this multiple of initial norm at first checkpoint

# ENCODER_PROVENANCE (substrate-native rail)
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

# Arms: 4 per research handoff
ARMS = {
    "ARM_BASELINE_NO_DOWNSCALE":   {"mode": "baseline_no_downscale", "K_migrate": None, "K_threshold": None,                 "downscale": None},
    "ARM_GLOBAL_DOWNSCALE_99_100": {"mode": "global_downscale",       "K_migrate": None, "K_threshold": None,                 "downscale": GLOBAL_DOWNSCALE_FACTOR},
    "ARM_COLD_STORAGE_NO_COMBINE": {"mode": "cold_storage",           "K_migrate": K_MIGRATE_DEFAULT, "K_threshold": K_THRESHOLD_DEFAULT,         "downscale": None},
    "ARM_COLD_STORAGE_TAU_500":    {"mode": "cold_storage",           "K_migrate": K_MIGRATE_DEFAULT, "K_threshold": K_THRESHOLD_TAU_500_ARM,     "downscale": None},
}

assert len(ARMS) == 4, "expected exactly 4 arms"
assert "ARM_BASELINE_NO_DOWNSCALE" in ARMS, "rail baseline must exist"
assert "ARM_GLOBAL_DOWNSCALE_99_100" in ARMS, "cellB-pattern arm must exist"
assert sum(1 for a in ARMS.values() if a["mode"] == "cold_storage") == 2, \
    "expected 2 cold-storage arms (different K_threshold)"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    """Iterative cleanup against W (N,N). W may be W_active + W_cold."""
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
    """Recall on probe_atoms via cleanup against W_combined."""
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
    """Importance = single-probe recall cosine clipped to [0,1]."""
    N_local = atom.shape[0]
    probe = atom.copy()
    flip = rng.random(N_local) < NOISE_FRAC
    probe[flip] *= -1.0
    out = hopfield_retrieve(W_combined, probe)
    cos = float(np.dot(out, atom) / N_local)
    return max(0.0, cos)


def norm_normalize_W(W: np.ndarray, target_norm: float) -> None:
    """Scale W IN-PLACE so ||W||_F == target_norm. Non-destructive: preserves
    relative pattern strengths. This is the substitute for global downscale.
    """
    cur = float(np.linalg.norm(W))
    if cur > 1e-9:
        W *= target_norm / cur


def run_arm(seed: int, arm_label: str, arm_cfg: Dict,
             all_atoms: np.ndarray, probe_set: np.ndarray) -> Dict:
    """Run one arm for one seed. arm_cfg dict per ARMS schema."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    mode = arm_cfg["mode"]
    K_migrate = arm_cfg["K_migrate"]
    K_threshold = arm_cfg["K_threshold"]
    downscale_factor = arm_cfg["downscale"]

    W_active = np.zeros((N, N), dtype=np.float64)
    W_cold = np.zeros((N, N), dtype=np.float64) if mode == "cold_storage" else None

    # Per-atom last-touched cycle tracker (for migration; only meaningful in cold-storage mode)
    # We track at the ATOM level (cheap) rather than per-weight (expensive at N=4096).
    atom_last_touched = np.zeros(N_CYCLES, dtype=np.int64)
    atom_migrated = np.zeros(N_CYCLES, dtype=bool)

    # For cold-storage arms: target_norm is set at the END of the first K_threshold
    # cycles of writes (when W_active reaches a "natural" capacity-level norm), then
    # norm-normalize W_active EVERY cycle to that target. This is the substitute for
    # multiplicative downscale: bounded norm without destructive scaling.
    target_norm = None

    # Importance score cache (cold_storage only). Score is cheap to maintain
    # because retrieval cost dominates; we re-score on migration events but
    # only for atoms with stale cache (last_scored_at + cache_age >= now).
    # For tractability at FULL: score ONLY NEW atoms (never-scored) plus
    # atoms whose score is currently below threshold (eligibility candidates).
    importance_cache = np.zeros(N_CYCLES, dtype=np.float64)
    score_freshness = np.full(N_CYCLES, -1, dtype=np.int64)  # cycle last scored

    curve = []
    migrations_log = []
    norm_log = []

    # Target-norm initialization cycle for cold-storage arms: K_threshold (the
    # staleness threshold) is also the warm-up before normalization kicks in,
    # ensuring we don't normalize against a near-zero norm.
    target_init_cycle = K_threshold if mode == "cold_storage" else None

    last_progress_t = t0
    for c in range(N_CYCLES):
        # Write atom c into W_active (or single W in baseline / downscale)
        write_atom_to_W(W_active, all_atoms[c])
        atom_last_touched[c] = c

        # Per-mode periodic operations
        if mode == "global_downscale" and downscale_factor is not None:
            # Cell B pattern: every cycle, multiply W by 0.99
            W_active *= downscale_factor

        elif mode == "cold_storage":
            # Initialize target_norm at warm-up boundary
            if target_norm is None and c + 1 >= target_init_cycle:
                target_norm = float(np.linalg.norm(W_active))

            # NORM-NORMALIZE every cycle (substitute for multiplicative downscale).
            # This is the load-bearing mechanism: bounded ||W_active||_F via
            # non-destructive rescaling.
            if target_norm is not None:
                norm_normalize_W(W_active, target_norm)

            # Migration step every K_migrate cycles
            if K_migrate is not None and c > 0 and (c % K_migrate) == 0:
                cap = c + 1
                W_combined_for_score = W_active + W_cold

                n_migrated_this_step = 0
                # Re-score only:
                #   - never-scored atoms (score_freshness[i] == -1)
                #   - atoms last scored > K_migrate cycles ago (potentially gone stale)
                # Skip already-migrated atoms.
                for i in range(cap):
                    if atom_migrated[i]:
                        continue
                    staleness = c - int(atom_last_touched[i])
                    if staleness <= K_threshold:
                        continue
                    # Cache check: if recently scored AND score above threshold, skip re-score.
                    age_since_score = c - int(score_freshness[i])
                    if (score_freshness[i] >= 0
                            and age_since_score <= K_migrate
                            and importance_cache[i] >= IMPORTANCE_THRESHOLD):
                        # Recently confirmed important; skip
                        continue
                    importance = score_atom_importance(W_combined_for_score, all_atoms[i], rng)
                    importance_cache[i] = importance
                    score_freshness[i] = c
                    if importance >= IMPORTANCE_THRESHOLD:
                        atom_last_touched[i] = c
                        continue
                    # MIGRATE
                    outer = np.outer(all_atoms[i], all_atoms[i])
                    W_cold += outer
                    W_active -= outer
                    atom_migrated[i] = True
                    n_migrated_this_step += 1

                # Re-normalize after migration shifts the norm
                if target_norm is not None:
                    norm_normalize_W(W_active, target_norm)

                n_cold_total = int(atom_migrated.sum())
                migrations_log.append({
                    "cycle": int(c),
                    "n_migrated_this_step": int(n_migrated_this_step),
                    "n_cold_total": n_cold_total,
                    "W_active_norm": float(np.linalg.norm(W_active)),
                    "W_cold_norm": float(np.linalg.norm(W_cold)),
                })

        # Checkpoint eval
        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == N_CYCLES - 1:
            if mode == "cold_storage":
                W_combined = W_active + W_cold
            else:
                W_combined = W_active
            acc = eval_recall_combined(W_combined, probe_set, rng)
            curve.append((c + 1, acc))
            w_active_norm = float(np.linalg.norm(W_active))
            w_cold_norm = float(np.linalg.norm(W_cold)) if W_cold is not None else 0.0
            norm_log.append({
                "cycle": int(c + 1),
                "W_active_norm": w_active_norm,
                "W_cold_norm": w_cold_norm,
            })
            now = time.time()
            since_last = now - last_progress_t
            print(f"  [seed={seed} arm={arm_label} c={c+1}/{N_CYCLES} "
                  f"acc={acc:.4f} forget={1-acc:.4f} "
                  f"|W_act|={w_active_norm:.1f} |W_cold|={w_cold_norm:.1f} "
                  f"+{since_last:.1f}s]", flush=True)
            last_progress_t = now

    elapsed = time.time() - t0
    final_cycle, final_acc = curve[-1]
    final_forget = 1.0 - final_acc

    # Integrity metric: 1 - (drift_from_target_norm / target_norm) clipped to [0,1].
    # For non-normalizing arms, integrity = 1.0 (no target to drift from).
    if target_norm is not None:
        final_w_active_norm = float(np.linalg.norm(W_active))
        drift_frac = abs(final_w_active_norm - target_norm) / target_norm
        integrity = max(0.0, min(1.0, 1.0 - drift_frac))
    else:
        integrity = 1.0

    if mode == "cold_storage":
        W_active_norm = float(np.linalg.norm(W_active))
        W_cold_norm = float(np.linalg.norm(W_cold))
        total = W_active_norm + W_cold_norm
        W_cold_util = W_cold_norm / total if total > 1e-9 else 0.0
        n_cold_atoms = int(atom_migrated.sum())
    else:
        W_active_norm = float(np.linalg.norm(W_active))
        W_cold_norm = 0.0
        W_cold_util = 0.0
        n_cold_atoms = 0

    print(f"  [seed={seed} arm={arm_label}] DONE final_cycle={final_cycle} "
          f"final_acc={final_acc:.4f} final_forget={final_forget:.4f} "
          f"integrity={integrity:.4f} n_cold={n_cold_atoms} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": arm_label,
        "arm_cfg": arm_cfg,
        "curve": [{"cycle": c, "recall_acc": a, "forget": 1.0 - a} for c, a in curve],
        "migrations_log": migrations_log,
        "norm_log": norm_log,
        "final_cycle": int(final_cycle),
        "final_acc": float(final_acc),
        "final_forget": float(final_forget),
        "integrity": float(integrity),
        "W_active_norm_final": W_active_norm,
        "W_cold_norm_final": W_cold_norm,
        "W_cold_utilization": W_cold_util,
        "n_cold_atoms": n_cold_atoms,
        "target_norm": target_norm,
        "elapsed_s": float(elapsed),
    }


# Partial-arm checkpoint helpers (NESS-hang prevention)
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
        print(f"[ckpt] arm partial config mismatch; ignoring "
              f"seed={seed} arm={arm_label}", flush=True)
        return None
    return body.get("result")


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

    rng_atoms = np.random.RandomState(seed)
    all_atoms = rng_atoms.choice([-1.0, 1.0], size=(N_CYCLES, N)).astype(np.float64)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()

    for arm_label, arm_cfg in ARMS.items():
        cached = _load_arm_partial(out_dir, seed, arm_label)
        if cached is not None:
            print(f"  [resume seed={seed} arm={arm_label}] loaded from arm partial", flush=True)
            arm_results[arm_label] = cached
            _atexit_state["completed_arms"].append(f"seed{seed}/{arm_label}")
            continue
        res = run_arm(seed, arm_label, arm_cfg, all_atoms, probe_set)
        arm_results[arm_label] = res
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
    agg = {}
    for label in arm_labels:
        forgets = [s["arms"][label]["final_forget"] for s in per_seed if label in s.get("arms", {})]
        integrities = [s["arms"][label]["integrity"] for s in per_seed if label in s.get("arms", {})]
        mean_f = float(np.mean(forgets)) if forgets else 1.0
        std_f = float(np.std(forgets)) if forgets else 1.0
        cv = (std_f / mean_f) if mean_f > 1e-9 else 0.0
        mean_int = float(np.mean(integrities)) if integrities else 0.0
        agg[label] = {
            "mean_final_forget": mean_f,
            "std": std_f,
            "cv": cv,
            "mean_integrity": mean_int,
            "per_seed_forget": forgets,
            "per_seed_integrity": integrities,
        }

    baseline = agg["ARM_BASELINE_NO_DOWNSCALE"]
    cellB_pattern = agg["ARM_GLOBAL_DOWNSCALE_99_100"]
    cold_arms = [l for l in arm_labels if ARMS[l]["mode"] == "cold_storage"]
    best_cold_label = min(cold_arms, key=lambda l: agg[l]["mean_final_forget"])
    best_cold = agg[best_cold_label]

    drift_reduction = baseline["mean_final_forget"] - best_cold["mean_final_forget"]
    drift_reduction_vs_cellB = cellB_pattern["mean_final_forget"] - best_cold["mean_final_forget"]

    arm_summary = " | ".join(
        f"{l}=ff={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std']:.4f}/int={agg[l]['mean_integrity']:.3f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "best_cold_arm": best_cold_label,
        "drift_reduction_vs_baseline": drift_reduction,
        "drift_reduction_vs_cellB_pattern": drift_reduction_vs_cellB,
        "honest_scope": (
            f"COLD_STORAGE no-combine over {N_CYCLES} cycles N={N}; "
            f"{len(ARMS)} arms: baseline + cellB-pattern + 2 cold-storage configs; "
            f"forget metric on first {RECALL_PROBE_M} atoms; combined-read W_active+W_cold for cold arms"
        ),
        "encoder_provenance": ENCODER_PROVENANCE,
    }

    # HARD_PASS check (strict; all 4 conditions)
    cond_forget_low = best_cold["mean_final_forget"] <= HARD_PASS_FORGET_CEILING
    cond_integrity_ok = best_cold["mean_integrity"] >= HARD_PASS_INTEGRITY_FLOOR
    cond_drift_big = drift_reduction >= HARD_PASS_DRIFT_REDUCTION
    cond_cv_ok = best_cold["cv"] <= HARD_PASS_CV_CEILING

    if cond_forget_low and cond_integrity_ok and cond_drift_big and cond_cv_ok:
        return ("HARD_PASS",
                f"HARD_PASS_COLD_STORAGE_WORKS: cold-storage architecture closes Cell B "
                f"HARD_FAIL at N={N} cycles={N_CYCLES}. best_cold={best_cold_label} "
                f"final_forget={best_cold['mean_final_forget']:.4f} <= {HARD_PASS_FORGET_CEILING} "
                f"integrity={best_cold['mean_integrity']:.4f} >= {HARD_PASS_INTEGRITY_FLOOR} "
                f"drift_reduction={drift_reduction:.4f} >= {HARD_PASS_DRIFT_REDUCTION} "
                f"cv={best_cold['cv']:.4f} <= {HARD_PASS_CV_CEILING}. "
                f"vs cellB pattern: {drift_reduction_vs_cellB:.4f}. arms: {arm_summary}",
                detail)

    # HARD_FAIL: cold storage doesn't help
    if drift_reduction <= HARD_FAIL_DRIFT_TOL:
        return ("HARD_FAIL",
                f"HARD_FAIL_COLD_STORAGE_DOESNT_HELP: best cold-storage arm matches baseline within "
                f"{HARD_FAIL_DRIFT_TOL}. best_cold={best_cold_label} drift_reduction={drift_reduction:.4f}. "
                f"Cold-storage architecture not effective at this regime. arms: {arm_summary}",
                detail)

    # HARD_PASS_PARTIAL
    if drift_reduction >= HARD_PASS_PARTIAL_DRIFT_REDUCTION:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL_COLD_STORAGE_REDUCES_DRIFT: cold-storage reduces drift by "
                f"{drift_reduction:.4f} >= {HARD_PASS_PARTIAL_DRIFT_REDUCTION} but full HARD_PASS "
                f"conditions not all met (forget_low={cond_forget_low} integrity_ok={cond_integrity_ok} "
                f"drift_big={cond_drift_big} cv_ok={cond_cv_ok}). best_cold={best_cold_label}. arms: {arm_summary}",
                detail)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: cold-storage provides drift_reduction={drift_reduction:.4f} (between "
            f"{HARD_FAIL_DRIFT_TOL} and {HARD_PASS_PARTIAL_DRIFT_REDUCTION}). best_cold={best_cold_label}. "
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


def _selftest_cold_migration_preserves_strength():
    """T2: Migrating an outer-product preserves its strength exactly in W_cold."""
    rng = np.random.RandomState(1)
    n_t = 256
    atom = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
    W_active = np.outer(atom, atom).copy()
    W_cold = np.zeros((n_t, n_t), dtype=np.float64)
    pre_active_norm = float(np.linalg.norm(W_active))
    # Migrate
    W_cold += np.outer(atom, atom)
    W_active -= np.outer(atom, atom)
    post_active_norm = float(np.linalg.norm(W_active))
    post_cold_norm = float(np.linalg.norm(W_cold))
    assert post_cold_norm > 0.0 and abs(post_cold_norm - pre_active_norm) < 1e-9, \
        f"T2 FAIL: cold norm {post_cold_norm:.6f} != pre-migrate active norm {pre_active_norm:.6f}"
    assert post_active_norm < 1e-6, \
        f"T2 FAIL: active norm should be ~0 after single-atom-active migration; got {post_active_norm:.6e}"
    print(f"[selftest T2] cold migration preserves strength exactly: "
          f"pre_active={pre_active_norm:.4f} -> post_cold={post_cold_norm:.4f} PASS", flush=True)


def _selftest_norm_normalize():
    """T3: norm_normalize_W keeps ||W||_F at target."""
    rng = np.random.RandomState(2)
    n_t = 256
    m_t = 30
    W = np.zeros((n_t, n_t), dtype=np.float64)
    for _ in range(m_t):
        a = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
        write_atom_to_W(W, a)
    pre_norm = float(np.linalg.norm(W))
    target = pre_norm * 1.10
    norm_normalize_W(W, target)
    post_norm = float(np.linalg.norm(W))
    assert abs(post_norm - target) < 1e-6, \
        f"T3 FAIL: post-normalize norm {post_norm:.6f} != target {target:.6f}"
    # And the relative pattern strength is preserved (just scaled)
    # Write again, normalize, write again, normalize: norm should stay close to target.
    for _ in range(10):
        a = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
        write_atom_to_W(W, a)
        norm_normalize_W(W, target)
    final_norm = float(np.linalg.norm(W))
    assert abs(final_norm - target) < 1e-6, \
        f"T3 FAIL: after repeated normalize, norm {final_norm:.6f} != target {target:.6f}"
    print(f"[selftest T3] norm_normalize stable: target={target:.4f} -> "
          f"final={final_norm:.4f} PASS", flush=True)


def _selftest_bands_locked():
    """T4: bands locked per pre-reg."""
    assert HARD_PASS_FORGET_CEILING == 0.10, "T4 HARD_PASS_FORGET_CEILING drift"
    assert HARD_PASS_INTEGRITY_FLOOR == 0.90, "T4 HARD_PASS_INTEGRITY_FLOOR drift"
    assert HARD_PASS_DRIFT_REDUCTION == 0.30, "T4 HARD_PASS_DRIFT_REDUCTION drift"
    assert HARD_PASS_CV_CEILING == 0.07, "T4 HARD_PASS_CV_CEILING drift"
    assert HARD_PASS_PARTIAL_DRIFT_REDUCTION == 0.20, "T4 partial floor drift"
    assert HARD_FAIL_DRIFT_TOL == 0.05, "T4 fail tol drift"
    print(f"[selftest T4] bands LOCKED PASS", flush=True)


def _selftest_arm_schema():
    """T5: ARMS dict shape; 4 arms; correct mode distribution."""
    assert len(ARMS) == 4, f"T5 ARMS count: expected 4 got {len(ARMS)}"
    assert "ARM_BASELINE_NO_DOWNSCALE" in ARMS, "T5 baseline missing"
    assert "ARM_GLOBAL_DOWNSCALE_99_100" in ARMS, "T5 cellB-pattern missing"
    cold_n = sum(1 for k, v in ARMS.items() if v["mode"] == "cold_storage")
    assert cold_n == 2, f"T5 cold-storage arms: expected 2 got {cold_n}"
    # Check K_threshold values differ between the two cold arms
    cold_thresholds = [v["K_threshold"] for v in ARMS.values() if v["mode"] == "cold_storage"]
    assert len(set(cold_thresholds)) == 2, \
        f"T5 cold arms should have distinct K_threshold; got {cold_thresholds}"
    print(f"[selftest T5] ARMS schema PASS (n={len(ARMS)}, cold_thresholds={cold_thresholds})", flush=True)


def _instrumentation_selftest():
    _selftest_hopfield_basic()
    _selftest_cold_migration_preserves_strength()
    _selftest_norm_normalize()
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
    "metrics_source": "measured_cpu_substrate_cold_storage_no_combine",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "encoder_provenance": ENCODER_PROVENANCE,
    "substrate_only_decode_gate": ("N/A (continual-writes cold-storage cell; "
                                    "zero LLM forward calls; numpy + Hopfield sign() only)"),
    "pre_reg_bands": {
        "HARD_PASS_FORGET_CEILING": HARD_PASS_FORGET_CEILING,
        "HARD_PASS_INTEGRITY_FLOOR": HARD_PASS_INTEGRITY_FLOOR,
        "HARD_PASS_DRIFT_REDUCTION": HARD_PASS_DRIFT_REDUCTION,
        "HARD_PASS_CV_CEILING": HARD_PASS_CV_CEILING,
        "HARD_PASS_PARTIAL_DRIFT_REDUCTION": HARD_PASS_PARTIAL_DRIFT_REDUCTION,
        "HARD_FAIL_DRIFT_TOL": HARD_FAIL_DRIFT_TOL,
    },
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
