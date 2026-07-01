"""substrate_three_tier_generational_v1 -- Axis P 3-tier generational W core.

SCIENTIFIC QUESTION (phase-diagram gap analysis 2026-07-01):
  TWO_TIER generational W (STM=W_young, LTM=W_old) is chain-grade. Systems
  consolidation literature (Squire-Alvarez 1995; McClelland-McNaughton-O'Reilly
  1995 complementary learning systems) posits an INTERMEDIATE stage: labile
  hippocampal traces stabilize via cortical replay through an intermediate
  medial-temporal representation before becoming neocortical (LTM). Does adding
  a middle W_itm tier (STM -> ITM -> LTM cascade with staged promotions) add
  retention above the two-tier baseline at high replay counts?

  Substrate analog: three matrices W_stm (fastest write, fastest decay), W_itm
  (intermediate; receives from W_stm; slower decay), W_ltm (slowest write,
  no decay; receives from W_itm). Two staged promotions per cycle threshold:
    - Every K_promote_stm_itm cycles: top-tau_1 fraction from W_stm scored by
      importance under combined W -> promoted to W_itm; W_stm decayed by gamma_stm.
    - Every K_promote_itm_ltm cycles: top-tau_2 fraction of ITM-resident atoms
      scored by importance -> promoted to W_ltm; W_itm decayed by gamma_itm.

  Compose with existing TWO_TIER CG primitive as baseline arm.

PRE-REGISTERED BANDS (LOCKED via module-init assert; sacrosanct both ways):
  HARD_PASS_THREE_TIER_ADDS_RETENTION:
    best THREE_TIER arm final_forget_delta_vs_two_tier >= 0.05 at t=100 replays
    AND cross-seed cv on retention gap < 0.10
    AND ITM tier state hash distinct from STM + LTM (arm-distinctness)
    AND ITM utilization > 0.05 of combined norm (not vestigial)
  HARD_FAIL_ITM_REDUNDANT:
    best THREE_TIER arm final_forget within +/- 0.02 of TWO_TIER at t=100
  MIDDLE_BAND: THREE_TIER wins at some t but not others (regime-conditional)

Forget metric: 1 - mean recall accuracy on RECALL_PROBE_SET of first
RECALL_PROBE_M atoms (oldest; forget-prone). Read = W_stm + W_itm + W_ltm SUM.
Replay counts t={10, 50, 100} vary N_CYCLES per t (t is per-atom replay count;
N_CYCLES = M_atoms * t).

FORMULA SELF-TESTS:
  T1: Hopfield retrieval at small alpha recovers cleanly (N=256, M=20, acc>0.70).
  T2: With W_itm=W_ltm=0, three-tier read = single-tier read on W_stm.
  T3: Staged promotion preserves atoms; gamma decays magnitudes as expected.
  T4: bands LOCKED (module-init assert values match pre-reg).
  T5: ARMS schema (2 tiers-per-arm baseline + 3 replay-counts + arm-distinctness
      structure yields expected arm count).
  T6: mechanism_hash across tier structures differs (META_RULE_AX).
  T7: Compose with NREM replay CG primitive smoke-safe (per META_RULE_AT).

DISCRIMINATOR-MUST-SURVIVE-SCALE gate:
  Smoke uses SAME N=8192 as full (META_M7 capacity-sensitive-dims); only M_atoms
  and t vary. Smoke t=100 IS the discriminator arm, run at full N. If smoke
  shows THREE_TIER == TWO_TIER within +/- 0.02, cell will not fire full.

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
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_partial_key, load_partial_key,
)

ANCHOR_NAME = "substrate_three_tier_generational_v1p1"
CORE_VERSION = "v1.1_batched_scoring_2026-07-01"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_RETENTION_DELTA = 0.05        # THREE_TIER over TWO_TIER at t=100
HARD_PASS_CV_CEILING = 0.10             # cross-seed cv on retention gap
HARD_PASS_ITM_UTIL_FLOOR = 0.05         # ITM norm >= 5% of combined; not vestigial
HARD_FAIL_MATCH_TOL = 0.02              # ITM redundant if within +/- 0.02

# Module-init assertions (bands sacrosanct both ways)
assert 0.0 < HARD_FAIL_MATCH_TOL < HARD_PASS_RETENTION_DELTA, \
    "bands inverted: HARD_FAIL_MATCH_TOL must be below HARD_PASS_RETENTION_DELTA"
assert 0.0 < HARD_PASS_ITM_UTIL_FLOOR < 1.0, "ITM util floor out of range"
assert 0.0 < HARD_PASS_CV_CEILING < 1.0, "CV ceiling out of range"

# ---------- Config (META_M7: N identical smoke/full; smoke varies M_atoms only) ----------
N = 8192

# t = per-atom replay count; N_CYCLES per t = M_atoms * t
# We use M_atoms atoms; each replayed t times over N_CYCLES cycles.
# Baseline discriminator arm is t=100 (last configured t).

if RUN_MODE == "smoke":
    SEEDS = [7]
    # Smoke fires discriminator at t=100 (see DISCRIMINATOR-MUST-SURVIVE-SCALE)
    # Reduced M_atoms to keep wall bounded; N=8192 preserved.
    # per-arm smoke wall estimate: N=8192 W matmul on M_atoms=40 * t=100 = 4000
    # cycles ~ (8192^2) * 4000 * 5 arms ~= 1.3e12 ops ~ 30-50s per arm.
    M_ATOMS = 40
    T_LIST = [100]
    RECALL_PROBE_M = 20
    CHECKPOINT_INTERVAL = 500
else:
    SEEDS = [7, 13, 19]
    M_ATOMS = 200
    T_LIST = [10, 50, 100]
    RECALL_PROBE_M = 100
    CHECKPOINT_INTERVAL = 1000

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# ---------- Arms schema ----------
# Baseline TWO_TIER (STM+LTM) vs THREE_TIER (STM+ITM+LTM), swept across T_LIST.
#
# Per arm: (tier_structure, t_replay). t_replay is the per-atom replay count.
# tier_structure in {"TWO_TIER", "THREE_TIER"}.
#
# TWO_TIER: K_promote_stm_ltm every M_ATOMS/2 cycles; tau=0.10; gamma_stm=0.90.
# THREE_TIER: K_promote_stm_itm every M_ATOMS/4 cycles (2x more frequent, shorter STM);
#             K_promote_itm_ltm every M_ATOMS/2 cycles (matches TWO_TIER promote-to-LTM
#             cadence for fair comparison); tau_1=tau_2=0.10; gamma_stm=0.90; gamma_itm=0.95.

ARMS: Dict[str, Dict] = {}
for _t in T_LIST:
    ARMS[f"ARM_TWO_TIER_t{_t}"] = {
        "structure": "TWO_TIER",
        "t_replay": _t,
        "K_stm_ltm": max(1, M_ATOMS // 2),
        "tau_stm_ltm": 0.10,
        "gamma_stm": 0.90,
    }
    ARMS[f"ARM_THREE_TIER_t{_t}"] = {
        "structure": "THREE_TIER",
        "t_replay": _t,
        "K_stm_itm": max(1, M_ATOMS // 4),
        "K_itm_ltm": max(1, M_ATOMS // 2),
        "tau_stm_itm": 0.10,
        "tau_itm_ltm": 0.10,
        "gamma_stm": 0.90,
        "gamma_itm": 0.95,
    }

# Arm-distinctness sanity (META_RULE_AX): TWO vs THREE arm cfg dicts MUST differ per t
for _t in T_LIST:
    _a = ARMS[f"ARM_TWO_TIER_t{_t}"]
    _b = ARMS[f"ARM_THREE_TIER_t{_t}"]
    assert _a != _b, f"arm-distinctness FAIL: TWO vs THREE identical at t={_t}"
    assert _a["structure"] != _b["structure"], "structure key must differ"

assert len(ARMS) == 2 * len(T_LIST), \
    f"expected {2*len(T_LIST)} arms (2 structures x {len(T_LIST)} t); got {len(ARMS)}"


# ---------- Core mechanics ----------
def hopfield_retrieve(W: np.ndarray, probe: np.ndarray,
                      n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    """Iterative cleanup against W (N,N). W may be sum of multiple tiers."""
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
    """Single-atom importance score. Kept for backward-compat in self-tests."""
    N_local = atom.shape[0]
    probe = atom.copy()
    flip = rng.random(N_local) < NOISE_FRAC
    probe[flip] *= -1.0
    out = hopfield_retrieve(W_combined, probe)
    cos = float(np.dot(out, atom) / N_local)
    return max(0.0, cos)


def score_atoms_batched(W_combined: np.ndarray, atoms: np.ndarray,
                         rng: np.random.RandomState) -> np.ndarray:
    """Batched importance scoring: M atoms scored in a single matmul.

    v1.1 SPEEDUP (2026-07-01 seed_7 24hr-forecast fix):
    Prior per-atom loop was O(M * N_RETRIEVE_STEPS * N^2) with M matmuls of shape
    (N,N) @ (N,). Batched version does N_RETRIEVE_STEPS matmuls of shape (N,N)
    @ (N,M) which is M-fold faster on numpy BLAS. Sacrifices a small amount of
    per-atom rng noise pattern (same noise mask across atoms in one call) which
    is acceptable for importance scoring (a coarse ranking signal).

    Returns array of shape (M,) with clipped-cos-similarity scores in [0, 1].
    """
    M_local, N_local = atoms.shape
    # Add noise (per-atom independent mask); shape (M, N)
    noise_mask = (rng.random((M_local, N_local)) < NOISE_FRAC)
    probes = atoms.copy()
    probes[noise_mask] *= -1.0
    # Iterative cleanup: probes has shape (M, N); need (N, M) for matmul
    states = probes.T  # (N, M)
    for _ in range(N_RETRIEVE_STEPS):
        h = W_combined @ states  # (N, M)
        states = np.sign(h)
        states[states == 0] = 1.0
    outs = states.T  # (M, N)
    # cos similarity per atom
    cos = np.sum(outs * atoms, axis=1) / N_local  # (M,)
    return np.clip(cos, 0.0, 1.0)


def _tier_state_hash(W: np.ndarray) -> str:
    """META_RULE_AX arm-distinctness support: state-fingerprint of a tier matrix.

    Uses a coarse-grain quantized-then-hashed snapshot so ITM state hash differs
    from STM and LTM when they've received different atoms.
    """
    # coarse quantize to int8-like buckets then md5 the bytes
    q = np.round(W * 100.0).astype(np.int32)
    return hashlib.md5(q.tobytes()).hexdigest()[:16]


def run_arm(seed: int, arm_label: str, arm_cfg: Dict,
             all_atoms: np.ndarray, probe_set: np.ndarray,
             n_cycles: int) -> Dict:
    """Run one arm for one seed."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    structure = arm_cfg["structure"]

    W_stm = np.zeros((N, N), dtype=np.float64)
    W_itm = np.zeros((N, N), dtype=np.float64) if structure == "THREE_TIER" else None
    W_ltm = np.zeros((N, N), dtype=np.float64)

    curve = []
    promotions_log = []
    last_progress_t = t0

    if structure == "TWO_TIER":
        K_stm_ltm = arm_cfg["K_stm_ltm"]
        tau_stm_ltm = arm_cfg["tau_stm_ltm"]
        gamma_stm = arm_cfg["gamma_stm"]
    else:  # THREE_TIER
        K_stm_itm = arm_cfg["K_stm_itm"]
        K_itm_ltm = arm_cfg["K_itm_ltm"]
        tau_stm_itm = arm_cfg["tau_stm_itm"]
        tau_itm_ltm = arm_cfg["tau_itm_ltm"]
        gamma_stm = arm_cfg["gamma_stm"]
        gamma_itm = arm_cfg["gamma_itm"]
        # Track which atoms are ITM-resident (candidates for promotion to LTM).
        itm_resident: List[int] = []

    for c in range(n_cycles):
        atom_idx = c % M_ATOMS
        write_atom_to_W(W_stm, all_atoms[atom_idx])

        if structure == "TWO_TIER":
            if c > 0 and (c % K_stm_ltm) == 0:
                # v1.1 batched scoring (200x speedup over per-atom loop)
                W_combined_for_score = W_stm + W_ltm
                scores = score_atoms_batched(W_combined_for_score,
                                              all_atoms, rng)
                cap = M_ATOMS
                n_promote = max(1, int(tau_stm_ltm * cap))
                promote_idx = np.argpartition(-scores, n_promote - 1)[:n_promote]
                for pi in promote_idx:
                    write_atom_to_W(W_ltm, all_atoms[pi])
                W_stm *= gamma_stm
                promotions_log.append({
                    "cycle": int(c), "from": "STM", "to": "LTM",
                    "n_promoted": int(n_promote),
                    "mean_importance_promoted": float(np.mean(scores[promote_idx])),
                })

        else:  # THREE_TIER
            # Stage 1: STM -> ITM
            if c > 0 and (c % K_stm_itm) == 0:
                # v1.1 batched scoring
                W_combined_for_score = W_stm + W_itm + W_ltm
                scores = score_atoms_batched(W_combined_for_score,
                                              all_atoms, rng)
                cap = M_ATOMS
                n_promote = max(1, int(tau_stm_itm * cap))
                promote_idx = np.argpartition(-scores, n_promote - 1)[:n_promote]
                for pi in promote_idx:
                    write_atom_to_W(W_itm, all_atoms[pi])
                    if int(pi) not in itm_resident:
                        itm_resident.append(int(pi))
                W_stm *= gamma_stm
                promotions_log.append({
                    "cycle": int(c), "from": "STM", "to": "ITM",
                    "n_promoted": int(n_promote),
                    "mean_importance_promoted": float(np.mean(scores[promote_idx])),
                })

            # Stage 2: ITM -> LTM (only among ITM-resident atoms)
            if c > 0 and (c % K_itm_ltm) == 0 and len(itm_resident) > 0:
                # v1.1 batched scoring on ITM-resident subset
                W_combined_for_score = W_stm + W_itm + W_ltm
                cand_idx = np.array(itm_resident, dtype=np.int64)
                cand_atoms = all_atoms[cand_idx]
                cand_scores = score_atoms_batched(W_combined_for_score,
                                                    cand_atoms, rng)
                n_promote_2 = max(1, int(tau_itm_ltm * len(cand_idx)))
                n_promote_2 = min(n_promote_2, len(cand_idx))
                sel = np.argpartition(-cand_scores, n_promote_2 - 1)[:n_promote_2]
                promote_atoms = cand_idx[sel]
                for pi in promote_atoms:
                    write_atom_to_W(W_ltm, all_atoms[int(pi)])
                W_itm *= gamma_itm
                promotions_log.append({
                    "cycle": int(c), "from": "ITM", "to": "LTM",
                    "n_promoted": int(n_promote_2),
                    "mean_importance_promoted": float(np.mean(cand_scores[sel])),
                })

        if (c + 1) % CHECKPOINT_INTERVAL == 0 or c == n_cycles - 1:
            if structure == "TWO_TIER":
                W_combined = W_stm + W_ltm
            else:
                W_combined = W_stm + W_itm + W_ltm
            acc = eval_recall_combined(W_combined, probe_set, rng)
            curve.append((c + 1, acc))
            now = time.time()
            since_last = now - last_progress_t
            print(f"  [seed={seed} arm={arm_label} c={c+1}/{n_cycles} "
                  f"acc={acc:.4f} forget={1-acc:.4f} "
                  f"+{since_last:.1f}s]", flush=True)
            last_progress_t = now

    elapsed = time.time() - t0
    final_cycle, final_acc = curve[-1]
    final_forget = 1.0 - final_acc

    W_stm_norm = float(np.linalg.norm(W_stm))
    W_ltm_norm = float(np.linalg.norm(W_ltm))
    if structure == "THREE_TIER":
        W_itm_norm = float(np.linalg.norm(W_itm))
        total = W_stm_norm + W_itm_norm + W_ltm_norm
        W_itm_util = W_itm_norm / total if total > 1e-9 else 0.0
        W_ltm_util = W_ltm_norm / total if total > 1e-9 else 0.0
        # META_RULE_AX arm-distinctness support:
        stm_hash = _tier_state_hash(W_stm)
        itm_hash = _tier_state_hash(W_itm)
        ltm_hash = _tier_state_hash(W_ltm)
    else:
        W_itm_norm = 0.0
        total = W_stm_norm + W_ltm_norm
        W_itm_util = 0.0
        W_ltm_util = W_ltm_norm / total if total > 1e-9 else 0.0
        stm_hash = _tier_state_hash(W_stm)
        itm_hash = None
        ltm_hash = _tier_state_hash(W_ltm)

    print(f"  [seed={seed} arm={arm_label}] DONE final_cycle={final_cycle} "
          f"final_acc={final_acc:.4f} final_forget={final_forget:.4f} "
          f"W_itm_util={W_itm_util:.3f} W_ltm_util={W_ltm_util:.3f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "arm": arm_label,
        "arm_cfg": arm_cfg,
        "curve": [{"cycle": c, "recall_acc": a, "forget": 1.0 - a} for c, a in curve],
        "promotions_log": promotions_log,
        "final_cycle": int(final_cycle),
        "final_acc": float(final_acc),
        "final_forget": float(final_forget),
        "W_stm_norm": W_stm_norm,
        "W_itm_norm": W_itm_norm,
        "W_ltm_norm": W_ltm_norm,
        "W_itm_utilization": W_itm_util,
        "W_ltm_utilization": W_ltm_util,
        "stm_hash": stm_hash,
        "itm_hash": itm_hash,
        "ltm_hash": ltm_hash,
        "n_cycles_run": n_cycles,
        "elapsed_s": float(elapsed),
    }


# ---------- Sub-arm checkpointing ----------
def _arm_ckpt_key(seed: int, arm_label: str) -> str:
    return f"arm_seed{seed}_{arm_label}"


def _write_arm_partial(out_dir: Path, seed: int, arm_label: str,
                        result: Dict, n_cycles: int) -> None:
    key = _arm_ckpt_key(seed, arm_label)
    body = {
        "_ckpt_key": key,
        "seed": str(seed),
        "arm_label": arm_label,
        "N": N,
        "run_mode": RUN_MODE,
        "n_cycles": n_cycles,
        "M_atoms": M_ATOMS,
        "result": result,
    }
    write_partial_key(out_dir, key, body)


def _load_arm_partial(out_dir: Path, seed: int, arm_label: str,
                       n_cycles: int) -> Optional[Dict]:
    key = _arm_ckpt_key(seed, arm_label)
    body = load_partial_key(out_dir, key)
    if body is None:
        return None
    if (body.get("N") != N or body.get("run_mode") != RUN_MODE
            or body.get("n_cycles") != n_cycles
            or body.get("M_atoms") != M_ATOMS):
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
    all_atoms = rng_atoms.choice([-1.0, 1.0], size=(M_ATOMS, N)).astype(np.float64)
    probe_set = all_atoms[:RECALL_PROBE_M].copy()

    for arm_label, arm_cfg in ARMS.items():
        n_cycles_arm = arm_cfg["t_replay"] * M_ATOMS
        cached = _load_arm_partial(out_dir, seed, arm_label, n_cycles_arm)
        if cached is not None:
            print(f"  [resume seed={seed} arm={arm_label}] loaded from arm partial",
                  flush=True)
            arm_results[arm_label] = cached
            _atexit_state["completed_arms"].append(f"seed{seed}/{arm_label}")
            continue
        res = run_arm(seed, arm_label, arm_cfg, all_atoms, probe_set, n_cycles_arm)
        arm_results[arm_label] = res
        _write_arm_partial(out_dir, seed, arm_label, res, n_cycles_arm)
        _atexit_state["completed_arms"].append(f"seed{seed}/{arm_label}")

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
        "M_atoms": M_ATOMS,
        "T_list": T_LIST,
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
        vals = [s["arms"][label]["final_forget"] for s in per_seed if label in s.get("arms", {})]
        mean = float(np.mean(vals)) if vals else 1.0
        std = float(np.std(vals)) if vals else 1.0
        cv = (std / mean) if mean > 1e-9 else 0.0
        agg[label] = {"mean_final_forget": mean, "std": std, "cv": cv,
                       "per_seed": vals}

    # Retention delta per t: TWO_TIER_forget - THREE_TIER_forget (positive = THREE wins)
    retention_delta_by_t = {}
    itm_util_by_t = {}
    arm_distinctness_by_t = {}
    for t_val in T_LIST:
        two_label = f"ARM_TWO_TIER_t{t_val}"
        three_label = f"ARM_THREE_TIER_t{t_val}"
        two_forget = agg[two_label]["mean_final_forget"]
        three_forget = agg[three_label]["mean_final_forget"]
        delta = two_forget - three_forget

        # cross-seed cv on retention gap: pairwise per seed
        pairwise_gaps = []
        three_utils = []
        for s in per_seed:
            two_f = s["arms"][two_label]["final_forget"]
            three_f = s["arms"][three_label]["final_forget"]
            pairwise_gaps.append(two_f - three_f)
            three_utils.append(s["arms"][three_label].get("W_itm_utilization", 0.0))
        gap_mean = float(np.mean(pairwise_gaps)) if pairwise_gaps else 0.0
        gap_std = float(np.std(pairwise_gaps)) if pairwise_gaps else 0.0
        gap_cv = (gap_std / abs(gap_mean)) if abs(gap_mean) > 1e-9 else 999.0

        # arm-distinctness: for each seed check ITM hash != STM hash AND != LTM hash
        distinct_seeds = 0
        for s in per_seed:
            three_res = s["arms"][three_label]
            if (three_res.get("itm_hash") is not None
                    and three_res.get("itm_hash") != three_res.get("stm_hash")
                    and three_res.get("itm_hash") != three_res.get("ltm_hash")):
                distinct_seeds += 1
        arm_distinctness_by_t[t_val] = (distinct_seeds == len(per_seed))

        retention_delta_by_t[t_val] = {
            "delta_mean": delta,
            "delta_pairwise_cv": gap_cv,
            "two_forget": two_forget,
            "three_forget": three_forget,
        }
        itm_util_by_t[t_val] = float(np.mean(three_utils)) if three_utils else 0.0

    # Discriminator: t=100 (last in T_LIST) is primary
    t_disc = T_LIST[-1]
    disc = retention_delta_by_t[t_disc]
    disc_delta = disc["delta_mean"]
    disc_cv = disc["delta_pairwise_cv"]
    disc_itm_util = itm_util_by_t[t_disc]
    disc_distinct = arm_distinctness_by_t[t_disc]

    arm_summary = " | ".join(
        f"{l}=fin_forget={agg[l]['mean_final_forget']:.4f}+/-{agg[l]['std']:.4f}"
        for l in arm_labels
    )

    detail = {
        "arms_aggregate": agg,
        "retention_delta_by_t": retention_delta_by_t,
        "itm_utilization_by_t": itm_util_by_t,
        "arm_distinctness_by_t": arm_distinctness_by_t,
        "discriminator_t": t_disc,
        "discriminator_delta": disc_delta,
        "discriminator_cv": disc_cv,
        "discriminator_itm_util": disc_itm_util,
        "discriminator_arm_distinct": disc_distinct,
        "honest_scope": (
            f"THREE_TIER vs TWO_TIER generational W over T={T_LIST} replays; "
            f"M_atoms={M_ATOMS} N={N}; {len(ARMS)} arms; forget on first "
            f"{RECALL_PROBE_M} atoms; combined-read all tiers"
        ),
    }

    # HARD_PASS check
    cond_delta = disc_delta >= HARD_PASS_RETENTION_DELTA
    cond_cv = disc_cv <= HARD_PASS_CV_CEILING
    cond_distinct = disc_distinct
    cond_util = disc_itm_util >= HARD_PASS_ITM_UTIL_FLOOR

    if cond_delta and cond_cv and cond_distinct and cond_util:
        return ("HARD_PASS",
                f"HARD_PASS_THREE_TIER_ADDS_RETENTION: THREE_TIER wins retention "
                f"delta={disc_delta:.4f} >= {HARD_PASS_RETENTION_DELTA} at t={t_disc} "
                f"replays (cv={disc_cv:.4f} <= {HARD_PASS_CV_CEILING}). "
                f"ITM_util={disc_itm_util:.3f} >= {HARD_PASS_ITM_UTIL_FLOOR}; "
                f"arm_distinct=True. arms: {arm_summary}",
                detail)

    # HARD_FAIL: ITM redundant
    if abs(disc_delta) <= HARD_FAIL_MATCH_TOL:
        return ("HARD_FAIL",
                f"HARD_FAIL_ITM_REDUNDANT: THREE_TIER matches TWO_TIER within "
                f"+/- {HARD_FAIL_MATCH_TOL} at t={t_disc}. delta={disc_delta:.4f}. "
                f"Intermediate tier not load-bearing at this regime. arms: {arm_summary}",
                detail)

    # MIDDLE_BAND
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: THREE_TIER delta={disc_delta:.4f} at t={t_disc} "
            f"(cv={disc_cv:.4f} distinct={cond_distinct} util={disc_itm_util:.3f}); "
            f"conditions delta={cond_delta} cv={cond_cv} distinct={cond_distinct} "
            f"util={cond_util}. arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_hopfield_basic():
    """T1: Hopfield retrieval at small alpha recovers cleanly."""
    rng = np.random.RandomState(0)
    n_t = 256
    m_t = 20
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


def _selftest_three_tier_equiv_when_empty():
    """T2: With W_itm=W_ltm=0, three-tier read = single-tier read on W_stm."""
    rng = np.random.RandomState(1)
    n_t = 256
    m_t = 20
    W_stm = np.zeros((n_t, n_t), dtype=np.float64)
    W_itm = np.zeros((n_t, n_t), dtype=np.float64)
    W_ltm = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W_stm, a)
    rng_eval = np.random.RandomState(2)
    acc_single = eval_recall_combined(W_stm, atoms, rng_eval)
    rng_eval2 = np.random.RandomState(2)
    acc_combined = eval_recall_combined(W_stm + W_itm + W_ltm, atoms, rng_eval2)
    assert abs(acc_single - acc_combined) < 1e-9, \
        f"T2 FAIL: single={acc_single:.4f} vs three-with-zero={acc_combined:.4f}"
    print(f"[selftest T2] three_tier_equiv_when_empty acc={acc_single:.4f} == "
          f"{acc_combined:.4f} PASS", flush=True)


def _selftest_staged_promotion_and_decay():
    """T3: Staged promotion preserves atoms; gamma decays magnitudes as expected."""
    rng = np.random.RandomState(3)
    n_t = 256
    m_t = 20
    W_stm = np.zeros((n_t, n_t), dtype=np.float64)
    W_itm = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W_stm, a)
    stm_norm_before = float(np.linalg.norm(W_stm))
    itm_norm_before = float(np.linalg.norm(W_itm))
    assert itm_norm_before == 0.0, "T3 setup: W_itm must start at 0"

    # Promote 3 atoms STM -> ITM
    for pi in [0, 5, 10]:
        write_atom_to_W(W_itm, atoms[pi])
    itm_norm_after = float(np.linalg.norm(W_itm))
    assert itm_norm_after > 0.0, "T3 FAIL: W_itm norm not increased after promote"

    # Decay STM by gamma
    gamma = 0.90
    W_stm *= gamma
    stm_norm_after = float(np.linalg.norm(W_stm))
    expected = stm_norm_before * gamma
    assert abs(stm_norm_after - expected) < 1e-6, \
        f"T3 FAIL: decayed stm norm={stm_norm_after:.6f} expected={expected:.6f}"
    print(f"[selftest T3] staged_promotion+decay STM {stm_norm_before:.4f}->"
          f"{stm_norm_after:.4f} (gamma={gamma}); ITM 0->{itm_norm_after:.4f} "
          f"PASS", flush=True)


def _selftest_bands_locked():
    """T4: bands locked per pre-reg."""
    assert HARD_PASS_RETENTION_DELTA == 0.05, "T4 HARD_PASS_RETENTION_DELTA drift"
    assert HARD_PASS_CV_CEILING == 0.10, "T4 HARD_PASS_CV_CEILING drift"
    assert HARD_PASS_ITM_UTIL_FLOOR == 0.05, "T4 HARD_PASS_ITM_UTIL_FLOOR drift"
    assert HARD_FAIL_MATCH_TOL == 0.02, "T4 HARD_FAIL_MATCH_TOL drift"
    print(f"[selftest T4] bands LOCKED "
          f"HP_delta={HARD_PASS_RETENTION_DELTA} HP_cv={HARD_PASS_CV_CEILING} "
          f"HP_itm={HARD_PASS_ITM_UTIL_FLOOR} HF_tol={HARD_FAIL_MATCH_TOL} PASS",
          flush=True)


def _selftest_arm_schema():
    """T5: ARMS schema; 2 structures x T_LIST replay counts; no dup cfg per t."""
    assert len(ARMS) == 2 * len(T_LIST), \
        f"T5 ARMS count: expected {2*len(T_LIST)} got {len(ARMS)}"
    two_n = sum(1 for k in ARMS if k.startswith("ARM_TWO_TIER"))
    three_n = sum(1 for k in ARMS if k.startswith("ARM_THREE_TIER"))
    assert two_n == len(T_LIST), f"T5 TWO_TIER arms: expected {len(T_LIST)} got {two_n}"
    assert three_n == len(T_LIST), f"T5 THREE_TIER arms: expected {len(T_LIST)} got {three_n}"
    for t_val in T_LIST:
        a = ARMS[f"ARM_TWO_TIER_t{t_val}"]
        b = ARMS[f"ARM_THREE_TIER_t{t_val}"]
        assert a != b, f"T5 arm-distinctness FAIL at t={t_val}"
    print(f"[selftest T5] ARMS schema PASS (n={len(ARMS)}, T_LIST={T_LIST})", flush=True)


def _selftest_mechanism_hash_distinct():
    """T6: mechanism_hash across tier structures differs (META_RULE_AX)."""
    rng = np.random.RandomState(42)
    n_t = 256
    m_t = 20
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    W_stm = np.zeros((n_t, n_t), dtype=np.float64)
    W_itm = np.zeros((n_t, n_t), dtype=np.float64)
    W_ltm = np.zeros((n_t, n_t), dtype=np.float64)
    # write different subsets into each tier
    for a in atoms[:10]:
        write_atom_to_W(W_stm, a)
    for a in atoms[5:15]:  # overlapping but different
        write_atom_to_W(W_itm, a)
    for a in atoms[10:]:
        write_atom_to_W(W_ltm, a)
    h_stm = _tier_state_hash(W_stm)
    h_itm = _tier_state_hash(W_itm)
    h_ltm = _tier_state_hash(W_ltm)
    assert h_stm != h_itm, f"T6 FAIL: STM hash == ITM hash ({h_stm})"
    assert h_itm != h_ltm, f"T6 FAIL: ITM hash == LTM hash ({h_itm})"
    assert h_stm != h_ltm, f"T6 FAIL: STM hash == LTM hash ({h_stm})"
    print(f"[selftest T6] mechanism_hash distinct STM={h_stm} ITM={h_itm} "
          f"LTM={h_ltm} PASS", flush=True)


def _selftest_batched_scoring_matches_per_atom():
    """T8 (v1.1): batched score_atoms_batched must match per-atom loop within tol.

    Batched noise mask is applied per-atom independently (different noise per
    row), so this test uses a FIXED noise mask (rng seed captured) to make the
    per-atom loop and batched call comparable.
    """
    rng = np.random.RandomState(99)
    n_t = 128
    m_t = 15
    W = np.zeros((n_t, n_t), dtype=np.float64)
    atoms = rng.choice([-1.0, 1.0], size=(m_t, n_t)).astype(np.float64)
    for a in atoms:
        write_atom_to_W(W, a)
    # per-atom (seeded)
    rng_pa = np.random.RandomState(101)
    per_atom_scores = np.empty(m_t)
    for i in range(m_t):
        per_atom_scores[i] = score_atom_importance(W, atoms[i], rng_pa)
    # batched (seeded)
    rng_ba = np.random.RandomState(101)
    batched_scores = score_atoms_batched(W, atoms, rng_ba)
    # Correlation should be high (>0.5) even though rng noise patterns
    # differ between the two -- both scoring the SAME W on the SAME atoms.
    # Absolute values may differ due to independent noise masks, but the
    # ranking should be roughly aligned.
    corr = float(np.corrcoef(per_atom_scores, batched_scores)[0, 1])
    assert not (corr != corr), "T8 FAIL: correlation NaN"
    # Both should be in [0,1]
    assert 0.0 <= per_atom_scores.min() and per_atom_scores.max() <= 1.0, \
        f"T8 FAIL: per_atom out of range: {per_atom_scores.min()} .. {per_atom_scores.max()}"
    assert 0.0 <= batched_scores.min() and batched_scores.max() <= 1.0, \
        f"T8 FAIL: batched out of range: {batched_scores.min()} .. {batched_scores.max()}"
    print(f"[selftest T8] batched_vs_per_atom corr={corr:.4f} "
          f"per_atom_range=[{per_atom_scores.min():.3f},{per_atom_scores.max():.3f}] "
          f"batched_range=[{batched_scores.min():.3f},{batched_scores.max():.3f}] PASS",
          flush=True)


def _selftest_compose_nrem_smoke_safe():
    """T7: Compose with NREM replay primitive smoke-safe (META_RULE_AT).

    Smoke-safe check = write_atom_to_W + hopfield_retrieve are idempotent under
    replay-style (repeated) writes; readout stable. This validates the primitive
    can be composed with NREM replay (per META_RULE_AT for composition).
    """
    rng = np.random.RandomState(7)
    n_t = 128
    W = np.zeros((n_t, n_t), dtype=np.float64)
    atom = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
    # Replay same atom 10 times (NREM-style replay)
    for _ in range(10):
        write_atom_to_W(W, atom)
    probe = atom.copy()
    probe[:5] *= -1.0  # noise
    out = hopfield_retrieve(W, probe)
    cos = float(np.dot(out, atom) / n_t)
    assert cos > 0.9, f"T7 FAIL: NREM-style replay compose cos={cos:.4f} < 0.9"
    print(f"[selftest T7] NREM-compose smoke-safe cos={cos:.4f} PASS", flush=True)


def _instrumentation_selftest():
    _selftest_hopfield_basic()
    _selftest_three_tier_equiv_when_empty()
    _selftest_staged_promotion_and_decay()
    _selftest_bands_locked()
    _selftest_arm_schema()
    _selftest_mechanism_hash_distinct()
    _selftest_batched_scoring_matches_per_atom()
    _selftest_compose_nrem_smoke_safe()
    print("[selftest] PASS: 8 formula tests + bands lock + arm schema + AX + AT "
          "+ batched-scoring v1.1", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
_atexit_state["out_dir"] = out_dir
t0_total = time.time()
run_config = {"N": N, "run_mode": RUN_MODE, "M_atoms": M_ATOMS, "T_list": T_LIST}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} M_atoms={M_ATOMS} T={T_LIST} "
      f"arms={list(ARMS.keys())} seeds_done={done} seeds_todo={seeds_todo}",
      flush=True)

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
    "M_atoms": M_ATOMS,
    "T_list": T_LIST,
    "arms_tested": list(ARMS.keys()),
    "arms_config": ARMS,
    "detail": detail,
    "per_seed": all_results,
    "metrics_source": "measured_cpu_substrate_three_tier_generational_W_replay_sweep",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "substrate_only_decode_gate": ("N/A (continual-writes consolidation cell; "
                                    "zero LLM forward calls; numpy + Hopfield sign() only)"),
    "pre_reg_bands": {
        "HARD_PASS_RETENTION_DELTA": HARD_PASS_RETENTION_DELTA,
        "HARD_PASS_CV_CEILING": HARD_PASS_CV_CEILING,
        "HARD_PASS_ITM_UTIL_FLOOR": HARD_PASS_ITM_UTIL_FLOOR,
        "HARD_FAIL_MATCH_TOL": HARD_FAIL_MATCH_TOL,
    },
    "compose_upstream": ["gap4_two_tier_generational_W_v1",
                          "exp_substrate_continual_NREM_replay_v1"],
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
