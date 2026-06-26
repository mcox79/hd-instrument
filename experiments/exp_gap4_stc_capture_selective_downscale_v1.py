"""gap4_stc_capture_selective_downscale_v1 -- Gap 4 brain SELECTIVE homeostasis ANCHOR_2.

SCIENTIFIC QUESTION (Gap 4 brain SELECTIVE homeostasis 2026-06-26):
  Cell B (substrate REM-homeostasis global downscale) HARD_FAIL_DESTROYS_OLDER on
  3 schedules. Brain does NOT do global downscale -- it does selective
  Synaptic Tagging and Capture (STC, Frey-Morris 1997).

  Substrate analog (this cell): three matrices alongside W
    W[i,j]   -- Hebbian outer-product weight matrix (as Cell A/B)
    T[i,j]   -- tag flag (bool, decays after K cycles)
    P[i,j]   -- persistent flag (bool, immune to future downscale)

  STC mechanism:
    1. AT WRITE TIME: T[i,j] := True for entries where |dW[i,j]| > theta_tag.
       Stamp tag_birth_cycle[i,j] = current cycle.
    2. EVERY J_REPLAY CYCLES: sample N_PRP from currently-tagged-and-unfaded
       weights (uniform among tagged), mark P[i,j] = True.
    3. EVERY J_DOWNSCALE CYCLES: global downscale, BUT skips persistent:
         W[~P] *= gamma; W[P] *= 1.0
    4. TAG DECAY: every cycle, T[i,j] -> False if (current_cycle - tag_birth_cycle)
       > K cycles AND not yet captured to P.

  KEY: bounded N_PRP enforces COMPETITION under scarce protein resources -- this
  is what makes brain selectivity scarce-resource-bounded rather than
  threshold-bounded. ZERO substrate prior on Frey-Morris STC with bounded PRP.

  Anchor #2 of three rank-ordered candidates (research drill 2026-06-26).
  Composes architecturally with gap4_two_tier_generational_W_v1 (STC provides
  the PROMOTION CRITERION for TWO_TIER young->old).

PRE-REGISTERED BANDS (LOCKED via module-init assert; sacrosanct both ways):
  HARD_PASS_STC_SELECTIVITY_WORKS:
    best_STC_arm.final_forget <= 0.20 AND min_integrity >= 0.95
    AND beats BASELINE drift by >= 0.30 AND cv <= 0.07
  HARD_PASS_PARTIAL:
    drift_reduction >= 0.20 absolute but not all conditions met
  MIDDLE_BAND: drift_reduction in (0.05, 0.20)
  HARD_FAIL_STC_DOESNT_HELP: drift_reduction <= 0.05 OR best STC arm worse than BASELINE
  HARD_FAIL_DESTROYS_OLDER_LIKE_GLOBAL:
    any STC arm WORSE than baseline by 0.05 (reproduces Cell B failure mode --
    selectivity not working)

Forget metric: 1 - mean retrieval accuracy on first RECALL_PROBE_M oldest atoms
(forget-prone tail). Integrity = mean cleanup-cosine on probe set.

FORMULA SELF-TESTS:
  1. tag_at_write: writing a high-magnitude atom flips T entries above theta_tag.
  2. tag_decay: after K+1 cycles with no capture, tagged entries decay back to T=False.
  3. capture_marks_persistent: PRP allocation flips P at sampled tagged entries.
  4. selective_downscale_skips_persistent: W[P]=1.0 unchanged after downscale;
     W[~P] reduced by gamma.
  5. bands_locked at module init.

NESS-HANG PREVENTION (Fix #28 + Two_tier lesson):
  Sub-arm checkpointing: write partial AFTER each arm (cap a single hang to 1
  arm worth of compute). Per-cycle CHECKPOINT_INTERVAL progress logs for
  liveness.

ASCII-only. Substrate-only (numpy + sign() Hopfield cleanup). Zero LLM forward
calls. ENCODER_PROVENANCE = SUBSTRATE_NATIVE.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import atexit
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_partial_key, load_partial_key,
)

ANCHOR_NAME = "gap4_stc_capture_selective_downscale_v1"
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED at module init) ----------
HARD_PASS_FORGET_CEILING = 0.20
HARD_PASS_INTEGRITY_FLOOR = 0.95
HARD_PASS_DRIFT_REDUCTION_FLOOR = 0.30
HARD_PASS_CV_CEILING = 0.07
HARD_PASS_PARTIAL_DRIFT_FLOOR = 0.20
MIDDLE_BAND_DRIFT_LOWER = 0.05  # MIDDLE band: (0.05, 0.20)
MIDDLE_BAND_DRIFT_UPPER = 0.20
HARD_FAIL_DOESNT_HELP_DRIFT_CEIL = 0.05
HARD_FAIL_DESTROYS_OLDER_TOL = 0.05  # arm WORSE than baseline by >= 0.05 = REPRO Cell B

assert 0.0 < HARD_PASS_FORGET_CEILING < 1.0, "forget ceiling sanity"
assert 0.0 < HARD_PASS_INTEGRITY_FLOOR < 1.0, "integrity floor sanity"
assert HARD_PASS_DRIFT_REDUCTION_FLOOR > HARD_PASS_PARTIAL_DRIFT_FLOOR, \
    "hard-pass drift floor must exceed partial-pass floor"
assert HARD_PASS_PARTIAL_DRIFT_FLOOR > MIDDLE_BAND_DRIFT_UPPER - 1e-9, \
    "partial threshold = middle band upper edge"
assert MIDDLE_BAND_DRIFT_LOWER < MIDDLE_BAND_DRIFT_UPPER, "middle band inverted"
assert HARD_FAIL_DOESNT_HELP_DRIFT_CEIL == MIDDLE_BAND_DRIFT_LOWER, \
    "fail ceil aligns with middle lower edge"

# ---------- Config (capacity-sensitive dims IDENTICAL smoke/full per META_M7) ----------
# Both smoke and FULL use identical N to avoid capacity-regime swap.
# Smoke just reduces N_CYCLES, SEEDS, RECALL_PROBE_M, CHECKPOINT_INTERVAL.
N = 4096

if RUN_MODE == "smoke":
    SEEDS = [11]
    # 500 cycles at N=4096 = alpha=0.122 (under Hopfield cliff at 0.14);
    # validates mechanism + per-arm wall (Fix #17 measurement strict).
    # Use J_REPLAY=100 so capture fires 4x, J_DOWNSCALE=200 so downscale fires
    # 2x. Both visible in smoke metrics.
    N_CYCLES = 500
    RECALL_PROBE_M = 30
    CHECKPOINT_INTERVAL = 100
    J_REPLAY_SMOKE_FACTOR = 1   # use arm config as-is in smoke
    J_DOWNSCALE_SMOKE_FACTOR = 1
else:
    SEEDS = [11, 13, 19]
    # 2500 cycles at N=4096 -> alpha at end = 2500/4096 = 0.61 (~4.4x Hopfield).
    # Matches Cell A NREM replay + Cell B baseline so we reproduce the cliff
    # behavior. Fix #17 budget: smoke per-arm-seed wall * 5 arms * 3 seeds *
    # 1.5 safety < 4h target on remote_cpu.
    N_CYCLES = 2500
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 250
    J_REPLAY_SMOKE_FACTOR = 1
    J_DOWNSCALE_SMOKE_FACTOR = 1

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# STC mechanism hyperparameters per arm. Five arms:
#   1. ARM_BASELINE_NO_DOWNSCALE -- rail (reproduces Cell A/B baseline drift)
#   2. ARM_GLOBAL_DOWNSCALE_99_100 -- reproduces Cell B HARD_FAIL pattern (sanity)
#   3. ARM_STC_TAG_DECAY_K100_PRP_BUDGET_100 -- main test (default STC)
#   4. ARM_STC_TAG_DECAY_K500_PRP_BUDGET_50 -- sparser PRP (scarcity test)
#   5. ARM_STC_TAG_DECAY_K100_PRP_BUDGET_INFINITY -- control (no bounded PRP)
#
# arm_cfg schema:
#   mode: "baseline" | "global" | "stc"
#   gamma: downscale factor (1.0 = no downscale)
#   J_downscale: cycles between downscale events (None = never)
#   theta_tag: |dW| threshold for tag firing (None for baseline/global)
#   K_tag_decay: cycles after which untagged tag fades (None for baseline/global)
#   J_replay: cycles between PRP allocation events
#   N_PRP: PRP budget per replay event (None = infinity / no cap)
#
# theta_tag: outer-product Hebbian writes use atoms in {-1, +1}, so |dW[i,j]|
# from a single atom write is exactly 1.0. We set theta_tag = 0.5 to ensure
# every write-event tags every (i,j) for the written atom (substrate-friendly
# default; brain-analogous "tag fires on coincident high-Ca write").
ARMS: Dict[str, Dict[str, object]] = {
    "ARM_BASELINE_NO_DOWNSCALE": {
        "mode": "baseline", "gamma": 1.0, "J_downscale": None,
        "theta_tag": None, "K_tag_decay": None, "J_replay": None, "N_PRP": None,
    },
    "ARM_GLOBAL_DOWNSCALE_99_100": {
        "mode": "global", "gamma": 0.99, "J_downscale": 100,
        "theta_tag": None, "K_tag_decay": None, "J_replay": None, "N_PRP": None,
    },
    "ARM_STC_TAG_DECAY_K100_PRP_BUDGET_100": {
        "mode": "stc", "gamma": 0.99, "J_downscale": 100,
        "theta_tag": 0.5, "K_tag_decay": 100, "J_replay": 100, "N_PRP": 100,
    },
    "ARM_STC_TAG_DECAY_K500_PRP_BUDGET_50": {
        "mode": "stc", "gamma": 0.99, "J_downscale": 100,
        "theta_tag": 0.5, "K_tag_decay": 500, "J_replay": 100, "N_PRP": 50,
    },
    "ARM_STC_TAG_DECAY_K100_PRP_BUDGET_INFINITY": {
        "mode": "stc", "gamma": 0.99, "J_downscale": 100,
        "theta_tag": 0.5, "K_tag_decay": 100, "J_replay": 100, "N_PRP": None,
    },
}
assert len(ARMS) == 5, "expected 5 arms (baseline + global + 3 STC)"
assert "ARM_BASELINE_NO_DOWNSCALE" in ARMS, "baseline rail must exist"
assert "ARM_GLOBAL_DOWNSCALE_99_100" in ARMS, "global-downscale sanity rail must exist"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray,
                      n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def write_atom_hebbian(W: np.ndarray, atom: np.ndarray) -> np.ndarray:
    """In-place outer-product Hebbian write. Returns dW = outer(atom, atom).

    Returns dW so caller can stamp tags by magnitude (|dW| > theta_tag).
    For atoms in {-1,+1}, |dW[i,j]| = 1.0 everywhere; theta_tag=0.5 -> all entries tagged
    on each write. This is the substrate-friendly STC default (every write event creates
    a synaptic tag).
    """
    dW = np.outer(atom, atom)
    W += dW
    return dW


def stc_tag_at_write(T: np.ndarray, tag_birth: np.ndarray, dW: np.ndarray,
                     theta_tag: float, cycle: int) -> int:
    """Stamp T[i,j]=True for entries where |dW| > theta_tag; record tag_birth.

    Returns number of tag flips applied this write.
    """
    mask = np.abs(dW) > theta_tag
    # only set tag if not already tagged (preserve earliest tag_birth)
    fresh_mask = mask & (~T)
    T[fresh_mask] = True
    tag_birth[fresh_mask] = cycle
    return int(fresh_mask.sum())


def stc_tag_decay(T: np.ndarray, P: np.ndarray, tag_birth: np.ndarray,
                  cycle: int, K_tag_decay: int) -> int:
    """Decay tags: T[i,j] -> False if (cycle - tag_birth) > K AND not captured.

    Persistent (P=True) tags are immune to decay (already captured).
    Returns number of decayed tags.
    """
    age = cycle - tag_birth
    decay_mask = T & (~P) & (age > K_tag_decay)
    T[decay_mask] = False
    return int(decay_mask.sum())


def stc_capture(T: np.ndarray, P: np.ndarray, N_PRP: Optional[int],
                rng: np.random.RandomState) -> int:
    """At a replay event, sample N_PRP currently-tagged-and-not-yet-persistent
    entries (uniform), mark them P=True.

    If N_PRP is None: NO budget cap -- all tagged-unpersistent become persistent
    (this is the ARM_..._INFINITY control: tests whether bounded-pool is the lever).

    Returns number of entries promoted to persistent.
    """
    candidates = T & (~P)
    n_cand = int(candidates.sum())
    if n_cand == 0:
        return 0
    if N_PRP is None or N_PRP >= n_cand:
        # No-cap (or budget exceeds supply): promote all candidates
        P[candidates] = True
        return n_cand
    # Bounded: sample uniformly N_PRP entries from candidates
    flat_idx = np.flatnonzero(candidates)
    chosen = rng.choice(flat_idx, size=N_PRP, replace=False)
    # Convert flat -> 2D indices
    rows, cols = np.unravel_index(chosen, P.shape)
    P[rows, cols] = True
    return int(N_PRP)


def selective_downscale(W: np.ndarray, P: np.ndarray, gamma: float) -> None:
    """In-place selective downscale: W[~P] *= gamma; W[P] *= 1.0."""
    if gamma >= 1.0:
        return
    # Per-element mask multiply (numpy broadcast). Avoid temporaries.
    mask_keep = ~P
    W[mask_keep] *= gamma


def global_downscale(W: np.ndarray, gamma: float) -> None:
    """In-place global downscale (Cell B baseline reproduction)."""
    if gamma >= 1.0:
        return
    W *= gamma


def eval_recall_and_integrity(W: np.ndarray, probe_atoms: np.ndarray,
                               rng: np.random.RandomState) -> Tuple[float, float]:
    """Return (accuracy at cos>0.8, mean cleanup-cosine = integrity)."""
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
    integ = cos_sum / float(probe_atoms.shape[0])
    return acc, integ


def run_arm(seed: int, arm_label: str, arm_cfg: Dict,
            all_atoms: np.ndarray, probe_set: np.ndarray) -> Dict:
    """Run one arm for one seed. arm_cfg dict per ARMS schema."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    mode = arm_cfg["mode"]
    gamma = float(arm_cfg["gamma"])
    J_downscale = arm_cfg["J_downscale"]
    theta_tag = arm_cfg["theta_tag"]
    K_tag_decay = arm_cfg["K_tag_decay"]
    J_replay = arm_cfg["J_replay"]
    N_PRP = arm_cfg["N_PRP"]

    # State
    W = np.zeros((N, N), dtype=np.float64)
    if mode == "stc":
        T = np.zeros((N, N), dtype=bool)
        P = np.zeros((N, N), dtype=bool)
        # tag_birth as int16 (cycles fit in 32k, smoke 500 + full 2500)
        tag_birth = np.zeros((N, N), dtype=np.int32)
    else:
        T = None
        P = None
        tag_birth = None

    curve = []
    capture_log = []  # [(cycle, n_promoted, n_persistent_total), ...]
    decay_log = []    # [(cycle, n_decayed, n_tags_total), ...]

    last_progress_t = t0
    for c in range(N_CYCLES):
        # Hebbian write
        dW = write_atom_hebbian(W, all_atoms[c])

        # STC tag-at-write (only if STC mode)
        if mode == "stc":
            stc_tag_at_write(T, tag_birth, dW, float(theta_tag), c)

            # Tag decay every cycle (cheap; mask operation)
            if K_tag_decay is not None:
                n_dec = stc_tag_decay(T, P, tag_birth, c, int(K_tag_decay))
                if n_dec > 0 and (c + 1) % CHECKPOINT_INTERVAL == 0:
                    decay_log.append({
                        "cycle": int(c), "n_decayed_this_cycle": n_dec,
                        "n_tags_total": int(T.sum()),
                    })

            # PRP allocation every J_replay cycles
            if J_replay is not None and c > 0 and (c % int(J_replay)) == 0:
                n_prom = stc_capture(T, P, N_PRP, rng)
                capture_log.append({
                    "cycle": int(c), "n_promoted_to_persistent": int(n_prom),
                    "n_persistent_total": int(P.sum()),
                    "n_tags_at_capture_time": int(T.sum()),
                })

        # Downscale every J_downscale cycles (mode-dependent)
        if J_downscale is not None and c > 0 and (c % int(J_downscale)) == 0:
            if mode == "global":
                global_downscale(W, gamma)
            elif mode == "stc":
                selective_downscale(W, P, gamma)
            # baseline mode: no downscale event

        # Checkpoint eval
        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == N_CYCLES - 1:
            acc, integ = eval_recall_and_integrity(W, probe_set, rng)
            curve.append((c + 1, acc, integ))
            now = time.time()
            since_last = now - last_progress_t
            n_pers = int(P.sum()) if P is not None else 0
            n_tag = int(T.sum()) if T is not None else 0
            print(f"  [seed={seed} arm={arm_label} c={c+1}/{N_CYCLES} "
                  f"acc={acc:.4f} forget={1-acc:.4f} integ={integ:.4f} "
                  f"n_tag={n_tag} n_pers={n_pers} +{since_last:.1f}s]",
                  flush=True)
            last_progress_t = now

    elapsed = time.time() - t0
    final_cycle, final_acc, final_integ = curve[-1]
    final_forget = 1.0 - final_acc
    min_integ = min(pt[2] for pt in curve)

    # Final tier metrics
    n_persistent_final = int(P.sum()) if P is not None else 0
    persistent_fraction = float(n_persistent_final) / float(N * N)
    W_frob = float(np.linalg.norm(W))

    print(f"  [seed={seed} arm={arm_label}] DONE final_cycle={final_cycle} "
          f"final_acc={final_acc:.4f} final_forget={final_forget:.4f} "
          f"min_integ={min_integ:.4f} n_pers={n_persistent_final} "
          f"frac_pers={persistent_fraction:.4f} ||W||_F={W_frob:.2f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": arm_label,
        "arm_cfg": {k: (None if v is None else v) for k, v in arm_cfg.items()},
        "curve": [{"cycle": cy, "recall_acc": a, "cleanup_integrity": i,
                   "forget": 1.0 - a} for cy, a, i in curve],
        "capture_log_summary": capture_log[-5:] if capture_log else [],
        "decay_log_summary": decay_log[-5:] if decay_log else [],
        "final_cycle": int(final_cycle),
        "final_acc": float(final_acc),
        "final_forget": float(final_forget),
        "final_integrity": float(final_integ),
        "min_integrity": float(min_integ),
        "n_persistent_final": n_persistent_final,
        "persistent_fraction_final": float(persistent_fraction),
        "W_frob_final": W_frob,
        "elapsed_s": float(elapsed),
    }


# ---------- Sub-arm checkpoint helpers (TWO_TIER pattern) ----------
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
    if (body.get("N") != N or body.get("run_mode") != RUN_MODE
            or body.get("n_cycles") != N_CYCLES):
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

    # Pre-generate all atoms for this seed (deterministic; arm-comparable)
    rng_atoms = np.random.RandomState(seed)
    all_atoms = rng_atoms.choice([-1.0, 1.0], size=(N_CYCLES, N)).astype(np.float64)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()

    for arm_label, arm_cfg in ARMS.items():
        cached = _load_arm_partial(out_dir, seed, arm_label)
        if cached is not None:
            print(f"  [resume seed={seed} arm={arm_label}] loaded from arm partial",
                  flush=True)
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
        forgets = [s["arms"][label]["final_forget"] for s in per_seed if label in s["arms"]]
        integs = [s["arms"][label]["min_integrity"] for s in per_seed if label in s["arms"]]
        n_pers = [s["arms"][label].get("n_persistent_final", 0)
                  for s in per_seed if label in s["arms"]]
        frac_pers = [s["arms"][label].get("persistent_fraction_final", 0.0)
                     for s in per_seed if label in s["arms"]]
        W_frob = [s["arms"][label].get("W_frob_final", 0.0)
                  for s in per_seed if label in s["arms"]]
        mean_f = float(np.mean(forgets)) if forgets else 1.0
        std_f = float(np.std(forgets)) if forgets else 1.0
        cv_f = (std_f / mean_f) if mean_f > 1e-9 else 0.0
        mean_i = float(np.mean(integs)) if integs else 0.0
        agg[label] = {
            "mean_final_forget": mean_f, "std_forget": std_f, "cv_forget": cv_f,
            "mean_min_integrity": mean_i,
            "mean_n_persistent_final": float(np.mean(n_pers)) if n_pers else 0.0,
            "mean_persistent_fraction_final": float(np.mean(frac_pers)) if frac_pers else 0.0,
            "mean_W_frob_final": float(np.mean(W_frob)) if W_frob else 0.0,
            "per_seed_forget": forgets, "per_seed_min_integ": integs,
        }

    baseline = agg["ARM_BASELINE_NO_DOWNSCALE"]
    stc_arms = [l for l in arm_labels if l.startswith("ARM_STC_")]
    assert stc_arms, "no STC arms found"
    # Best STC arm = lowest final forget
    best_label = min(stc_arms, key=lambda l: agg[l]["mean_final_forget"])
    best = agg[best_label]

    drift_reduction = baseline["mean_final_forget"] - best["mean_final_forget"]

    # Failure-mode check: did ANY STC arm reproduce Cell B HARD_FAIL_DESTROYS_OLDER?
    destroys_older_offenders = []
    for l in stc_arms:
        overage = agg[l]["mean_final_forget"] - baseline["mean_final_forget"]
        if overage >= HARD_FAIL_DESTROYS_OLDER_TOL:
            destroys_older_offenders.append((l, overage))

    arm_summary = " | ".join(
        f"{l}=fin_forget={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std_forget']:.4f} "
        f"min_integ={agg[l]['mean_min_integrity']:.4f} "
        f"n_pers={int(agg[l]['mean_n_persistent_final'])}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "best_stc_arm": best_label,
        "baseline_label": "ARM_BASELINE_NO_DOWNSCALE",
        "drift_reduction_abs": drift_reduction,
        "destroys_older_offenders": [
            {"arm": l, "overage_vs_baseline": ov} for l, ov in destroys_older_offenders
        ],
        "honest_scope": (
            f"STC-with-bounded-PRP over {N_CYCLES} cycles N={N}; "
            f"5 arms (baseline + global + 3 STC variants); forget on first "
            f"{RECALL_PROBE_M} oldest atoms (forget-prone tail)"
        ),
        "encoder_provenance": ENCODER_PROVENANCE,
    }

    # HARD_FAIL_DESTROYS_OLDER_LIKE_GLOBAL guard FIRST
    if destroys_older_offenders:
        # Rank by overage; report worst
        destroys_older_offenders.sort(key=lambda x: x[1], reverse=True)
        worst = destroys_older_offenders[0]
        return ("HARD_FAIL",
                f"HARD_FAIL_DESTROYS_OLDER_LIKE_GLOBAL: STC arm {worst[0]} has forget "
                f"{agg[worst[0]]['mean_final_forget']:.4f} vs baseline "
                f"{baseline['mean_final_forget']:.4f} (overage {worst[1]:.4f} >= "
                f"{HARD_FAIL_DESTROYS_OLDER_TOL}). Selectivity NOT working: STC reproduces "
                f"Cell B failure mode. arms: {arm_summary}",
                detail)

    # HARD_PASS_STC_SELECTIVITY_WORKS
    cond_low_forget = best["mean_final_forget"] <= HARD_PASS_FORGET_CEILING
    cond_integ = best["mean_min_integrity"] >= HARD_PASS_INTEGRITY_FLOOR
    cond_drift = drift_reduction >= HARD_PASS_DRIFT_REDUCTION_FLOOR
    cond_cv = best["cv_forget"] <= HARD_PASS_CV_CEILING

    if cond_low_forget and cond_integ and cond_drift and cond_cv:
        return ("HARD_PASS",
                f"HARD_PASS_STC_SELECTIVITY_WORKS: Frey-Morris STC with bounded PRP "
                f"closes Cell B HARD_FAIL. best_stc={best_label} "
                f"final_forget={best['mean_final_forget']:.4f}<={HARD_PASS_FORGET_CEILING} "
                f"min_integ={best['mean_min_integrity']:.4f}>={HARD_PASS_INTEGRITY_FLOOR} "
                f"drift_red={drift_reduction:.4f}>={HARD_PASS_DRIFT_REDUCTION_FLOOR} "
                f"cv={best['cv_forget']:.4f}<={HARD_PASS_CV_CEILING}. arms: {arm_summary}",
                detail)

    if drift_reduction >= HARD_PASS_PARTIAL_DRIFT_FLOOR:
        return ("HARD_PASS",
                f"HARD_PASS_PARTIAL: STC drift_red={drift_reduction:.4f} "
                f">= {HARD_PASS_PARTIAL_DRIFT_FLOOR} but full conditions not met "
                f"(low_forget={cond_low_forget} integ={cond_integ} cv={cond_cv}). "
                f"best_stc={best_label}. arms: {arm_summary}",
                detail)

    if drift_reduction <= HARD_FAIL_DOESNT_HELP_DRIFT_CEIL:
        return ("HARD_FAIL",
                f"HARD_FAIL_STC_DOESNT_HELP: drift_red={drift_reduction:.4f} <= "
                f"{HARD_FAIL_DOESNT_HELP_DRIFT_CEIL}; STC arm not meaningfully better "
                f"than baseline. best_stc={best_label}. arms: {arm_summary}",
                detail)

    # Default: MIDDLE_BAND (drift_red in (0.05, 0.20))
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: drift_red={drift_reduction:.4f} in "
            f"({MIDDLE_BAND_DRIFT_LOWER}, {MIDDLE_BAND_DRIFT_UPPER}). "
            f"STC selectivity partial. best_stc={best_label}. arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_tag_at_write():
    """T1: stc_tag_at_write flips T entries above theta_tag at the right cells."""
    rng = np.random.RandomState(1)
    n_t = 16
    W = np.zeros((n_t, n_t), dtype=np.float64)
    T = np.zeros((n_t, n_t), dtype=bool)
    tag_birth = np.zeros((n_t, n_t), dtype=np.int32)
    atom = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
    dW = write_atom_hebbian(W, atom)
    n_flips = stc_tag_at_write(T, tag_birth, dW, theta_tag=0.5, cycle=42)
    # For bipolar atoms, |dW[i,j]| = 1 everywhere -> ALL entries should tag
    assert n_flips == n_t * n_t, f"T1 FAIL: expected {n_t*n_t} flips got {n_flips}"
    assert T.all(), "T1 FAIL: not all T entries are True"
    assert (tag_birth == 42).all(), "T1 FAIL: tag_birth not stamped"
    # Higher theta -> no flips
    T2 = np.zeros((n_t, n_t), dtype=bool)
    tag_birth2 = np.zeros((n_t, n_t), dtype=np.int32)
    n_flips2 = stc_tag_at_write(T2, tag_birth2, dW, theta_tag=1.5, cycle=42)
    assert n_flips2 == 0, f"T1 FAIL: theta=1.5 should give 0 flips got {n_flips2}"
    print("[selftest T1] stc_tag_at_write numerical PASS", flush=True)


def _selftest_tag_decay():
    """T2: stc_tag_decay clears T entries past K_tag_decay if not captured."""
    n_t = 8
    T = np.ones((n_t, n_t), dtype=bool)  # all tagged
    P = np.zeros((n_t, n_t), dtype=bool)  # none captured
    tag_birth = np.full((n_t, n_t), 10, dtype=np.int32)  # all born at cycle 10
    # At cycle 100 with K_tag_decay=50: age=90 > 50 -> all decay
    n_dec = stc_tag_decay(T, P, tag_birth, cycle=100, K_tag_decay=50)
    assert n_dec == n_t * n_t, f"T2 FAIL: expected {n_t*n_t} decayed got {n_dec}"
    assert not T.any(), "T2 FAIL: T should be all False after decay"
    # Persistent entries IMMUNE to decay
    T = np.ones((n_t, n_t), dtype=bool)
    P = np.ones((n_t, n_t), dtype=bool)  # all persistent
    tag_birth = np.full((n_t, n_t), 10, dtype=np.int32)
    n_dec2 = stc_tag_decay(T, P, tag_birth, cycle=100, K_tag_decay=50)
    assert n_dec2 == 0, f"T2 FAIL: persistent should resist decay got {n_dec2}"
    assert T.all(), "T2 FAIL: persistent T should stay True"
    print("[selftest T2] stc_tag_decay (persistent-immune) PASS", flush=True)


def _selftest_capture_marks_persistent():
    """T3: stc_capture flips P at sampled tagged entries; bounded by N_PRP."""
    rng = np.random.RandomState(2)
    n_t = 8
    T = np.ones((n_t, n_t), dtype=bool)  # all tagged (64 entries)
    P = np.zeros((n_t, n_t), dtype=bool)
    n_prom = stc_capture(T, P, N_PRP=10, rng=rng)
    assert n_prom == 10, f"T3 FAIL: expected 10 promoted got {n_prom}"
    assert int(P.sum()) == 10, f"T3 FAIL: expected 10 P=True got {int(P.sum())}"
    # Re-capture with N_PRP exceeding remaining candidates
    n_prom2 = stc_capture(T, P, N_PRP=1000, rng=rng)
    assert n_prom2 == n_t * n_t - 10, \
        f"T3 FAIL: should promote remaining {n_t*n_t-10} got {n_prom2}"
    assert P.all(), "T3 FAIL: P should be all True now"
    # Infinity (N_PRP=None) on fresh: all promoted
    T = np.ones((n_t, n_t), dtype=bool)
    P = np.zeros((n_t, n_t), dtype=bool)
    n_prom3 = stc_capture(T, P, N_PRP=None, rng=rng)
    assert n_prom3 == n_t * n_t, f"T3 FAIL: infinity should promote all got {n_prom3}"
    print("[selftest T3] stc_capture (bounded + infinity) PASS", flush=True)


def _selftest_selective_downscale():
    """T4: selective_downscale skips persistent, downscales non-persistent."""
    n_t = 4
    W = np.full((n_t, n_t), 1.0, dtype=np.float64)
    P = np.zeros((n_t, n_t), dtype=bool)
    P[0, 0] = True
    P[1, 1] = True
    selective_downscale(W, P, gamma=0.9)
    assert math.isclose(W[0, 0], 1.0), f"T4 FAIL: persistent should be 1.0 got {W[0,0]}"
    assert math.isclose(W[1, 1], 1.0), f"T4 FAIL: persistent should be 1.0 got {W[1,1]}"
    assert math.isclose(W[0, 1], 0.9), f"T4 FAIL: non-persistent should be 0.9 got {W[0,1]}"
    assert math.isclose(W[2, 2], 0.9), f"T4 FAIL: non-persistent should be 0.9 got {W[2,2]}"
    # gamma=1.0 -> no-op
    W = np.full((n_t, n_t), 1.0, dtype=np.float64)
    selective_downscale(W, P, gamma=1.0)
    assert np.allclose(W, 1.0), "T4 FAIL: gamma=1.0 should be no-op"
    print("[selftest T4] selective_downscale (persistent-immune) PASS", flush=True)


def _selftest_bands_locked():
    assert HARD_PASS_FORGET_CEILING == 0.20, "T5 forget ceiling drift"
    assert HARD_PASS_INTEGRITY_FLOOR == 0.95, "T5 integrity floor drift"
    assert HARD_PASS_DRIFT_REDUCTION_FLOOR == 0.30, "T5 drift floor drift"
    assert HARD_PASS_CV_CEILING == 0.07, "T5 cv ceiling drift"
    assert HARD_PASS_PARTIAL_DRIFT_FLOOR == 0.20, "T5 partial floor drift"
    assert MIDDLE_BAND_DRIFT_LOWER == 0.05, "T5 middle lower drift"
    assert MIDDLE_BAND_DRIFT_UPPER == 0.20, "T5 middle upper drift"
    assert HARD_FAIL_DESTROYS_OLDER_TOL == 0.05, "T5 destroys-older tol drift"
    print("[selftest T5] bands LOCKED PASS", flush=True)


def _instrumentation_selftest():
    _selftest_tag_at_write()
    _selftest_tag_decay()
    _selftest_capture_marks_persistent()
    _selftest_selective_downscale()
    _selftest_bands_locked()
    print("[selftest] PASS: 4 formula tests + bands lock", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
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
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_substrate_STC_capture_5arm_continual_writes",
    "encoder_provenance": ENCODER_PROVENANCE,
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
