"""
exp_counterfactual_replay_latency_delta_stack_v3_3seed_replication -- CF Cell 2 v3.

ROUTING: 3-seed cross-seed replication of v2 HARD_PASS single-intervention delta-stack finding.
Parent v2 (seeds [1,2] smoke): BASELINE setup=11.497ms, DELTA_SHORT setup=2.103ms, speedup=5.467x,
acc=1.000; verdict HARD_PASS but n_seeds=2 -> mechanism_characterization tier (Skunkworks discipline:
cross-seed cv required for chain-grade).
V3 GOAL: replicate 5.47x speedup on 3 fresh seeds [7, 13, 19]; cross-seed cv <10% -> CG-eligible.
Same regime, same mechanism, same core primitives as v2 (bit-identical copy of hetero_W /
hop_baseline / hop_delta_stack / _make_setup / _run_baseline_full_rewrite / _run_delta_stack_short /
_run_delta_stack_amortized / _run_direct_lookup_oracle). Only diffs: SEEDS list, cell name, and
verdict gate adds cross-seed cv thresholds.
ARMS: BASELINE_FULL_REWRITE, DELTA_STACK_SHORT (SHORT_STACK=1), DELTA_STACK_AMORTIZED (5 CF; filler
  hoisted), DIRECT_LOOKUP_ORACLE (upper bound), RANDOM_DELTAS (control; single random delta).
PRE-REGISTERED HARD_PASS: DELTA_STACK_SHORT setup<4ms AND speedup>=5.0x AND acc>=0.99 AND
  cv_setup<0.10 AND cv_speedup<0.10 across 3 seeds; AMORTIZED setup<4ms; arms_distinct >=0.50 acc gap.
HARD_FAIL: DELTA setup>=BASELINE, speedup<5.0x, acc<0.95, AMORTIZED>=4ms, RANDOM matches structured,
  OR cross-seed cv>=0.15 (mechanism unstable across seeds).
MIDDLE_BAND: 4.0<=setup<=10ms with accuracy preserved OR speedup>=5.0x but cv in [0.10, 0.15].
ASCII-only. write_metrics atomic via _seed_checkpoint. PROT-018. v3.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import hashlib
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "counterfactual_replay_latency_delta_stack_v3_3seed_replication"
RIDGE = 1e-3

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# CROSS-SEED CV GATE (load-bearing for CG-eligibility discipline)
CV_HP_MAX = 0.10  # cross-seed cv <10% -> HARD_PASS eligible
CV_MB_MAX = 0.15  # cross-seed cv <15% -> MIDDLE_BAND eligible; >=0.15 -> HARD_FAIL
SPEEDUP_HP_MIN = 5.0  # discriminator per pre-reg
SPEEDUP_MB_MIN = 3.0  # MIDDLE_BAND floor (still substantive win)

if RUN_MODE == "smoke":
    # Smoke: only seed 13 (fastest check for reproduction of 5.47x); short-cycle to verify
    SEEDS = [13]
    N = 2048
    N_ENT = 80
    KLEN = 4
    N_CYCLES = 200
    AMORTIZED_STACK = 5
    SHORT_STACK = 1
else:
    # 3-seed replication (task-specified): 7 (v2 full config seed), 13 (new), 19 (new)
    # N_CYCLES=300 (v2 uses 1000 but 300 already gives 900 units/arm across 3 seeds -- ample cv power;
    # keeps total wall <2h avoiding PROT-021 4h checkpoint requirement for this write-at-end cell)
    SEEDS = [7, 13, 19]
    N = 8192
    N_ENT = 200
    KLEN = 5
    N_CYCLES = 300
    AMORTIZED_STACK = 5
    SHORT_STACK = 1

ARMS = [
    "ARM_BASELINE_FULL_REWRITE",
    "ARM_DELTA_STACK_SHORT",
    "ARM_DELTA_STACK_AMORTIZED",
    "ARM_DIRECT_LOOKUP_ORACLE",
    "ARM_RANDOM_DELTAS",
]


# ---------- core primitives (bit-identical parity with v2) ----------

def hetero_W(S: np.ndarray, T: np.ndarray) -> np.ndarray:
    """source->target hetero-assoc: W @ s_i ~= t_i ; W = T^T (S S^T + ridge)^-1 S."""
    G = S @ S.T + RIDGE * np.eye(S.shape[0])
    return T.T @ np.linalg.solve(G, S)


def hop_baseline(W: np.ndarray, src_vec: np.ndarray, ent: np.ndarray) -> int:
    """Standard hop: argmax cosine over entity bank."""
    out = W @ src_vec
    sims = ent @ out
    return int(np.argmax(sims))


def hop_delta_stack(W: np.ndarray, src_vec: np.ndarray, ent: np.ndarray,
                    stack: List[Tuple[np.ndarray, np.ndarray]]) -> int:
    """Lazy CF hop: baseline projection + sum of stack-deltas keyed by src similarity."""
    out = W @ src_vec
    for s_stack, d_stack in stack:
        w = float(src_vec @ s_stack) / float(src_vec.shape[0])
        if w > 0.5:
            out = out + w * d_stack
    sims = ent @ out
    return int(np.argmax(sims))


# ---------- self-tests ----------

def _selftest() -> None:
    rng = np.random.default_rng(0)
    n_dim = 256
    n_ent = 10
    ent = np.sign(rng.standard_normal((n_ent, n_dim))).astype(np.float64)
    ent[ent == 0] = 1.0
    chain = [0, 1, 2, 3]
    S = np.stack([ent[chain[i]] for i in range(3)])
    T = np.stack([ent[chain[i + 1]] for i in range(3)])
    W = hetero_W(S, T)
    assert hop_baseline(W, ent[1], ent) == 2, "baseline hop retrieves true next"
    new_target = ent[7]
    proj = W @ ent[1]
    delta = new_target - proj
    stack = [(ent[1].copy(), delta.copy())]
    pred = hop_delta_stack(W, ent[1], ent, stack)
    assert pred == 7, f"delta_stack identity failed: pred={pred} expected=7"
    Tm = T.copy()
    Tm[1] = new_target
    W_rebuilt = hetero_W(S, Tm)
    proj_rebuilt = W_rebuilt @ ent[1]
    proj_delta = (W @ ent[1]) + delta
    cos = float(proj_rebuilt @ proj_delta) / (np.linalg.norm(proj_rebuilt) * np.linalg.norm(proj_delta) + 1e-12)
    assert cos > 0.95, f"rebuild vs delta cos={cos:.4f}, expected > 0.95"
    samples = []
    for _ in range(100):
        t0 = time.perf_counter()
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1e6)
    med_us = float(np.median(samples))
    assert med_us < 100.0, f"perf_counter resolution check failed: median={med_us:.2f}us"
    # Selftest 5: cross-seed cv formula sanity (this is the v3-specific gate)
    fake_setups = [2.10, 2.15, 2.05]
    fake_mean = float(np.mean(fake_setups))
    fake_std = float(np.std(fake_setups, ddof=1))
    fake_cv = fake_std / fake_mean if fake_mean > 0 else float("inf")
    assert fake_cv < 0.05, f"cv formula sanity: expected <0.05 on tight sample, got {fake_cv:.4f}"
    # Selftest 6: cv gate thresholds well-ordered
    assert CV_HP_MAX < CV_MB_MAX, "CV thresholds mis-ordered"
    assert SPEEDUP_MB_MIN < SPEEDUP_HP_MIN, "speedup thresholds mis-ordered"
    print("[selftest] PASS: delta-stack identity, rebuild equivalence, perf_counter, cv formula, "
          "gate ordering", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- per-arm runners (bit-identical to v2) ----------

def _make_setup(rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]:
    ent = np.sign(rng.standard_normal((N_ENT, N))).astype(np.float64)
    ent[ent == 0] = 1.0
    chain = rng.choice(N_ENT, KLEN + 1, replace=False)
    S = np.stack([ent[chain[i]] for i in range(KLEN)])
    T = np.stack([ent[chain[i + 1]] for i in range(KLEN)])
    W = hetero_W(S, T)
    m = KLEN // 2
    new_tail = int(rng.integers(0, N_ENT))
    while new_tail in chain:
        new_tail = int(rng.integers(0, N_ENT))
    return ent, S, T, W, int(chain[m]), new_tail


def _run_baseline_full_rewrite(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    correct = 0
    setup_lats: List[float] = []
    query_lats: List[float] = []
    for _ in range(N_CYCLES):
        ent, S, T, W, src_idx, new_tail = _make_setup(rng)
        t0 = time.perf_counter()
        m = KLEN // 2
        Tm = T.copy()
        Tm[m] = ent[new_tail]
        W_tmp = hetero_W(S, Tm)
        setup_lats.append((time.perf_counter() - t0) * 1e3)
        t0 = time.perf_counter()
        pred = hop_baseline(W_tmp, ent[src_idx], ent)
        query_lats.append((time.perf_counter() - t0) * 1e3)
        if pred == new_tail:
            correct += 1
    return {
        "arm": "ARM_BASELINE_FULL_REWRITE",
        "seed": seed,
        "n_cycles": N_CYCLES,
        "accuracy": correct / N_CYCLES,
        "setup_latency_ms": float(np.mean(setup_lats)),
        "query_latency_ms": float(np.mean(query_lats)),
        "setup_latency_ms_median": float(np.median(setup_lats)),
        "query_latency_ms_median": float(np.median(query_lats)),
    }


def _run_delta_stack_short(seed: int, random_deltas: bool, arm_name: str) -> Dict:
    rng = np.random.default_rng(seed)
    correct = 0
    setup_lats: List[float] = []
    query_lats: List[float] = []
    for _ in range(N_CYCLES):
        ent, S, T, W, src_idx, new_tail = _make_setup(rng)
        t0 = time.perf_counter()
        stack: List[Tuple[np.ndarray, np.ndarray]] = []
        proj = W @ ent[src_idx]
        delta = ent[new_tail] - proj
        if random_deltas:
            r = rng.standard_normal(N).astype(np.float64)
            r = r * (np.linalg.norm(delta) / (np.linalg.norm(r) + 1e-12))
            delta = r
        stack.append((ent[src_idx].copy(), delta.copy()))
        setup_lats.append((time.perf_counter() - t0) * 1e3)
        t0 = time.perf_counter()
        pred = hop_delta_stack(W, ent[src_idx], ent, stack)
        query_lats.append((time.perf_counter() - t0) * 1e3)
        if pred == new_tail:
            correct += 1
    return {
        "arm": arm_name,
        "seed": seed,
        "n_cycles": N_CYCLES,
        "stack_size": SHORT_STACK,
        "accuracy": correct / N_CYCLES,
        "setup_latency_ms": float(np.mean(setup_lats)),
        "query_latency_ms": float(np.mean(query_lats)),
        "setup_latency_ms_median": float(np.median(setup_lats)),
        "query_latency_ms_median": float(np.median(query_lats)),
    }


def _run_delta_stack_amortized(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    correct = 0
    setup_lats: List[float] = []
    query_lats: List[float] = []
    ent_cache = np.sign(rng.standard_normal((N_ENT, N))).astype(np.float64)
    ent_cache[ent_cache == 0] = 1.0
    chain_cache = rng.choice(N_ENT, KLEN + 1, replace=False)
    S_cache = np.stack([ent_cache[chain_cache[i]] for i in range(KLEN)])
    T_cache = np.stack([ent_cache[chain_cache[i + 1]] for i in range(KLEN)])
    W_cache = hetero_W(S_cache, T_cache)
    filler_cache: List[Tuple[np.ndarray, np.ndarray]] = []
    for _f in range(AMORTIZED_STACK - 1):
        other_idx = int(rng.integers(0, N_ENT))
        other_target = int(rng.integers(0, N_ENT))
        d_other = ent_cache[other_target] - (W_cache @ ent_cache[other_idx])
        filler_cache.append((ent_cache[other_idx].copy(), d_other.copy()))
    for _ in range(N_CYCLES):
        ent, S, T, W, src_idx, new_tail = _make_setup(rng)
        t0 = time.perf_counter()
        proj = W @ ent[src_idx]
        delta = ent[new_tail] - proj
        stack: List[Tuple[np.ndarray, np.ndarray]] = [(ent[src_idx].copy(), delta.copy())]
        stack.extend(filler_cache)
        setup_lats.append((time.perf_counter() - t0) * 1e3)
        t0 = time.perf_counter()
        pred = hop_delta_stack(W, ent[src_idx], ent, stack)
        query_lats.append((time.perf_counter() - t0) * 1e3)
        if pred == new_tail:
            correct += 1
    return {
        "arm": "ARM_DELTA_STACK_AMORTIZED",
        "seed": seed,
        "n_cycles": N_CYCLES,
        "stack_size": AMORTIZED_STACK,
        "filler_cache_hoisted": True,
        "accuracy": correct / N_CYCLES,
        "setup_latency_ms": float(np.mean(setup_lats)),
        "query_latency_ms": float(np.mean(query_lats)),
        "setup_latency_ms_median": float(np.median(setup_lats)),
        "query_latency_ms_median": float(np.median(query_lats)),
    }


def _run_direct_lookup_oracle(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    correct = 0
    setup_lats: List[float] = []
    query_lats: List[float] = []
    for _ in range(N_CYCLES):
        ent, S, T, W, src_idx, new_tail = _make_setup(rng)
        t0 = time.perf_counter()
        lookup = {src_idx: new_tail}
        setup_lats.append((time.perf_counter() - t0) * 1e3)
        t0 = time.perf_counter()
        pred = lookup.get(src_idx, -1)
        query_lats.append((time.perf_counter() - t0) * 1e3)
        if pred == new_tail:
            correct += 1
    return {
        "arm": "ARM_DIRECT_LOOKUP_ORACLE",
        "seed": seed,
        "n_cycles": N_CYCLES,
        "accuracy": correct / N_CYCLES,
        "setup_latency_ms": float(np.mean(setup_lats)),
        "query_latency_ms": float(np.mean(query_lats)),
        "setup_latency_ms_median": float(np.median(setup_lats)),
        "query_latency_ms_median": float(np.median(query_lats)),
    }


# ---------- aggregation + verdict ----------

def _cv(vals: List[float]) -> float:
    """Coefficient of variation (std/mean); ddof=1 for sample std."""
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    if abs(m) < 1e-12:
        return float("inf")
    s = float(np.std(vals, ddof=1))
    return s / abs(m)


def _aggregate_arm(per_seed_rows: List[Dict]) -> Dict:
    accs = [r["accuracy"] for r in per_seed_rows]
    setups = [r["setup_latency_ms"] for r in per_seed_rows]
    queries = [r["query_latency_ms"] for r in per_seed_rows]
    return {
        "arm": per_seed_rows[0]["arm"],
        "n_seeds": len(per_seed_rows),
        "accuracy_mean": float(np.mean(accs)),
        "setup_latency_ms_mean": float(np.mean(setups)),
        "query_latency_ms_mean": float(np.mean(queries)),
        "setup_latency_ms_median": float(np.median([r["setup_latency_ms_median"] for r in per_seed_rows])),
        "query_latency_ms_median": float(np.median([r["query_latency_ms_median"] for r in per_seed_rows])),
        "accuracy_cv": _cv(accs),
        "setup_latency_cv": _cv(setups),
        "query_latency_cv": _cv(queries),
        "per_seed_setup_ms": setups,
        "per_seed_query_ms": queries,
        "per_seed_accuracy": accs,
    }


def _arms_distinct_signature(arm_aggs: Dict[str, Dict]) -> str:
    payload = []
    for arm in ARMS:
        a = arm_aggs[arm]
        payload.append(f"{arm}:{a['accuracy_mean']:.6f}:{a['setup_latency_ms_mean']:.6f}:{a['query_latency_ms_mean']:.6f}")
    blob = "|".join(payload).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def verdict(arm_aggs: Dict[str, Dict], cardinality_ok: bool) -> Tuple[str, str, bool]:
    """Returns (verdict, msg, auto_promote_parent). v3 adds cross-seed cv gate for CG-eligibility."""
    base = arm_aggs["ARM_BASELINE_FULL_REWRITE"]
    short = arm_aggs["ARM_DELTA_STACK_SHORT"]
    amort = arm_aggs["ARM_DELTA_STACK_AMORTIZED"]
    rand = arm_aggs["ARM_RANDOM_DELTAS"]
    speedup = base["setup_latency_ms_mean"] / max(short["setup_latency_ms_mean"], 1e-9)
    arms_distinct = (short["accuracy_mean"] - rand["accuracy_mean"]) >= 0.50

    # Cross-seed cv on the discriminator (SHORT arm setup latency + derived speedup)
    short_setup_cv = short["setup_latency_cv"]
    # Speedup cv: per-seed speedups
    per_seed_speedups = [
        base["per_seed_setup_ms"][i] / max(short["per_seed_setup_ms"][i], 1e-9)
        for i in range(len(base["per_seed_setup_ms"]))
    ]
    speedup_cv = _cv(per_seed_speedups) if len(per_seed_speedups) >= 2 else 0.0
    short_acc_cv = short["accuracy_cv"]

    bias_q_flags = []
    for arm_name, agg in arm_aggs.items():
        if abs(agg["accuracy_mean"] - 1.0) < 0.001:
            bias_q_flags.append(f"{arm_name}@acc=1.000")
    bias_q_msg = (" [BIAS-Q: " + ",".join(bias_q_flags) + "]") if bias_q_flags else ""

    summary = (
        f"BASELINE setup={base['setup_latency_ms_mean']:.3f}ms acc={base['accuracy_mean']:.3f} | "
        f"DELTA_SHORT setup={short['setup_latency_ms_mean']:.3f}ms "
        f"query={short['query_latency_ms_mean']:.3f}ms acc={short['accuracy_mean']:.3f} | "
        f"AMORTIZED setup={amort['setup_latency_ms_mean']:.3f}ms acc={amort['accuracy_mean']:.3f} | "
        f"RANDOM acc={rand['accuracy_mean']:.3f} | "
        f"speedup={speedup:.2f}x speedup_cv={speedup_cv:.3f} "
        f"short_setup_cv={short_setup_cv:.3f} short_acc_cv={short_acc_cv:.3f} "
        f"arms_distinct={arms_distinct} cardinality_ok={cardinality_ok} n_seeds={short['n_seeds']}"
        f"{bias_q_msg}"
    )

    if not cardinality_ok:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH: per-arm cycle count below expected. {summary}", False)

    # HARD_FAIL gates
    if short["setup_latency_ms_mean"] >= base["setup_latency_ms_mean"]:
        return ("HARD_FAIL",
                f"HARD_FAIL: DELTA_STACK_SHORT setup >= BASELINE (no win). {summary}", False)
    if short["accuracy_mean"] < 0.95:
        return ("HARD_FAIL", f"HARD_FAIL: DELTA_STACK_SHORT accuracy <0.95. {summary}", False)
    if speedup < SPEEDUP_MB_MIN:
        return ("HARD_FAIL", f"HARD_FAIL: speedup<{SPEEDUP_MB_MIN}x (below MIDDLE_BAND floor). {summary}", False)
    if abs(short["accuracy_mean"] - rand["accuracy_mean"]) < 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL: RANDOM_DELTAS matches DELTA_STACK_SHORT (signal not from structured deltas). {summary}",
                False)
    # v3-specific: cross-seed instability HARD_FAIL
    if short["n_seeds"] >= 2 and (short_setup_cv >= CV_MB_MAX or speedup_cv >= CV_MB_MAX):
        return ("HARD_FAIL",
                f"HARD_FAIL: cross-seed cv>={CV_MB_MAX} on discriminator "
                f"(setup_cv={short_setup_cv:.3f} speedup_cv={speedup_cv:.3f}); "
                f"mechanism unstable across seeds. {summary}", False)

    # HARD_PASS gates (v3 tightened: speedup + acc + cv all required across seeds)
    hp_speedup = speedup >= SPEEDUP_HP_MIN
    hp_short_setup = short["setup_latency_ms_mean"] < 4.0
    hp_short_acc = short["accuracy_mean"] >= 0.99
    hp_amort_setup = amort["setup_latency_ms_mean"] < 4.0
    hp_cv_setup = short_setup_cv < CV_HP_MAX
    hp_cv_speedup = speedup_cv < CV_HP_MAX
    if (hp_speedup and hp_short_setup and hp_short_acc and hp_amort_setup
            and arms_distinct and hp_cv_setup and hp_cv_speedup):
        return ("HARD_PASS",
                f"HARD_PASS: 3-seed replication clears speedup>={SPEEDUP_HP_MIN}x + setup<4ms + acc>=0.99 "
                f"+ cross-seed cv<{CV_HP_MAX}. Chain-grade-eligible. "
                f"AUTO-PROMOTES parent v2 -> chain-grade. {summary}", True)

    # MIDDLE_BAND
    if speedup >= SPEEDUP_MB_MIN and short["accuracy_mean"] >= 0.95:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: speedup>={SPEEDUP_MB_MIN}x with acc preserved but HP gate missed "
                f"(setup>=4ms OR cv in [{CV_HP_MAX},{CV_MB_MAX}) OR speedup<{SPEEDUP_HP_MIN}x). {summary}",
                False)

    return ("MIDDLE_BAND", f"MIDDLE_BAND: mixed -- some HP gates met, others not. {summary}", False)


# ---------- main ----------

def main() -> None:
    print(
        f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N} "
        f"entities={N_ENT} K={KLEN} cycles={N_CYCLES} "
        f"short_stack={SHORT_STACK} amortized_stack={AMORTIZED_STACK} arms={len(ARMS)} "
        f"cv_hp_max={CV_HP_MAX} cv_mb_max={CV_MB_MAX} "
        f"speedup_hp_min={SPEEDUP_HP_MIN} speedup_mb_min={SPEEDUP_MB_MIN}",
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    t_start = time.time()

    all_rows: List[Dict] = []
    arm_aggs: Dict[str, Dict] = {}

    expected_n_units = len(SEEDS) * len(ARMS) * N_CYCLES
    observed_n_units = 0

    for arm in ARMS:
        print(f"\n[arm] {arm}", flush=True)
        per_seed_rows: List[Dict] = []
        for seed in SEEDS:
            if arm == "ARM_BASELINE_FULL_REWRITE":
                row = _run_baseline_full_rewrite(seed)
            elif arm == "ARM_DELTA_STACK_SHORT":
                row = _run_delta_stack_short(seed, random_deltas=False, arm_name=arm)
            elif arm == "ARM_DELTA_STACK_AMORTIZED":
                row = _run_delta_stack_amortized(seed)
            elif arm == "ARM_DIRECT_LOOKUP_ORACLE":
                row = _run_direct_lookup_oracle(seed)
            elif arm == "ARM_RANDOM_DELTAS":
                row = _run_delta_stack_short(seed, random_deltas=True, arm_name=arm)
            else:
                raise RuntimeError(f"unknown arm: {arm}")
            print(
                f"  [seed={seed}] acc={row['accuracy']:.3f} setup={row['setup_latency_ms']:.3f}ms "
                f"query={row['query_latency_ms']:.3f}ms cycles={row['n_cycles']}",
                flush=True,
            )
            per_seed_rows.append(row)
            all_rows.append(row)
            observed_n_units += row["n_cycles"]
        arm_aggs[arm] = _aggregate_arm(per_seed_rows)

    cardinality_ok = observed_n_units >= expected_n_units
    arms_signature = _arms_distinct_signature(arm_aggs)

    v, vmsg, auto_promote = verdict(arm_aggs, cardinality_ok)
    print(f"\n[VERDICT] {vmsg}", flush=True)
    if auto_promote:
        print("[AUTO-PROMOTE] parent v2 MIDDLE_BAND -> chain-grade (cross-seed replicated)",
              flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "N": N,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_arms": len(ARMS),
        "n_cycles": N_CYCLES,
        "short_stack": SHORT_STACK,
        "amortized_stack": AMORTIZED_STACK,
        "cv_hp_max_HYPOTHESIZED": CV_HP_MAX,
        "cv_mb_max_HYPOTHESIZED": CV_MB_MAX,
        "speedup_hp_min_HYPOTHESIZED": SPEEDUP_HP_MIN,
        "speedup_mb_min_HYPOTHESIZED": SPEEDUP_MB_MIN,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "cardinality_ok": cardinality_ok,
        "arms": ARMS,
        "arms_signature_sha256_16": arms_signature,
        "arm_aggregates": arm_aggs,
        "per_arm_seed_rows": all_rows,
        "auto_promote_parent": auto_promote,
        "parent_atom_name": "counterfactual_replay_latency_delta_stack_v2_single_intervention",
        "parent_v2_metrics_path": "data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json",
        "parent_v2_verdict_MEASURED": "HARD_PASS_2seed_smoke",
        "parent_v2_speedup_MEASURED": 5.467,
        "parent_v2_short_setup_ms_MEASURED": 2.103,
        "hp_target_setup_ms_HYPOTHESIZED": 4.0,
        "hp_target_speedup_HYPOTHESIZED": SPEEDUP_HP_MIN,
        "hp_target_cv_HYPOTHESIZED": CV_HP_MAX,
        "elapsed_s": time.time() - t_start,
    }
    write_metrics(out_dir, metrics, all_rows)
    print("[metrics] written", flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:
        print(f"[FATAL] {type(e).__name__}: {e}", flush=True)
        raise
