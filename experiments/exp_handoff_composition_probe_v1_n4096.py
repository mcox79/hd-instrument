"""G3 HANDOFF COMPOSITION PROBE v1 at N=4096.

CONTEXT (Batch 1 #3, verdict_handler follow-on #2 from v289):
  Test 3 composition strategies as BACKSTOPS for Path D (not error-
  correction, which R2 closed). The goal is informing Pattern B LLM
  integration with a mechanism-selection logic.

3 STRATEGIES:
  A = HEURISTIC: Path D default; fall through to E for high-K,
                  B for sub-capacity-M, otherwise D-only.
  B = PARALLEL_VERIFY: Run B, D, E; return Path D; flag disagreements;
                        verifier_catch_rate = fraction of cells where any
                        verifier disagreed with D AND was right.
  C = TARGETED_VERIFIER: Run D + ONE selected verifier (E if high-K,
                          B if sub-capacity); confirm agreement.

3 REGIMES (depth=5, K_paths=500 fixed):
  Sub-capacity:  M=2048
  At-capacity:   M=4096
  Past-capacity: M=16384

3 strategies x 3 regimes x 5 seeds = 45 cell-seeds. PER-CELL CHECKPOINT (PROT-021).

PRE-REGISTERED BANDS:
  HP = at least 1 strategy delivers measurable advantage
       (verifier_catch_rate >= 0.10 OR accuracy_delta >= 0.05) in
       >= 1 regime in >= 3/5 seeds.
  HF = all strategies add only latency overhead with zero accuracy or
       verification value (verifier_catch_rate < 0.02 AND
       accuracy_delta < 0.01 across ALL 9 (strategy, regime) cells).
  MB = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. STRATEGIES = ["A_heuristic", "B_parallel_verify", "C_targeted_verifier"].
  3. REGIMES = [("sub_cap", 2048), ("at_cap", 4096), ("past_cap", 16384)].
  4. high_K threshold = K_paths >= 750 (here 500 so high-K branch never hits
     for A/C; A defaults to D, C selects B as verifier for sub_cap and E
     otherwise). Recorded in metadata.
  5. accuracy_delta = strat_acc - baseline_D_acc.

OOM CHECK:
  N=4096, M_max=16384. Codebook=256 MiB. W=64 MiB. Strategy B runs all 3
  paths sequentially so peak memory ~ single-path peak. Under 600 MiB.

TIMEOUT ESTIMATE:
  Per cell-seed: Strategy A ~ Path-D-only (~30s), Strategy B ~ B+D+E
  (~75s), Strategy C ~ D+verifier (~50s). 45 cell-seeds * mean 50s = 2250s.
  With overhead: 6000s. Budget 21600s per user spec for safety.

N-suffix: _n4096 (PROT-018).
Anchor: handoff_composition_probe_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_handoff_composition_probe_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)
from experiments._multi_hop_mechanisms import (  # noqa: E402
    path_b_run,
    path_d_run,
    path_e_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

STRATEGIES = ["A_heuristic", "B_parallel_verify", "C_targeted_verifier"]
REGIMES_FULL  = [("sub_cap", 2048), ("at_cap", 4096), ("past_cap", 16384)]
REGIMES_SMOKE = [("sub_cap", 256), ("past_cap", 1024)]
DEPTH_FIXED = 5
K_FIXED = 500
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_STARTS = 16

HIGH_K_THRESHOLD = 750  # for strategy selection
SUB_CAP_M_THRESHOLD = 4096  # M < this = sub-capacity

BETA_D = 4.0

# Pre-registered thresholds
HP_VERIFIER_CATCH = 0.10
HP_ACCURACY_DELTA = 0.05
HP_SEEDS_MIN = 3
HF_VERIFIER_CATCH_BELOW = 0.02
HF_ACC_DELTA_BELOW = 0.01


def get_output_dir(default_name: str = "handoff_composition_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_full(N_use: int, M: int, seed: int, device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def _path_b_acc(codebook, W, starts, depth, N_use, relation):
    pred_b = path_b_run(codebook, W, starts, depth, N_use)
    # targets: follow relation depth times
    targets = []
    for k in starts.tolist():
        cur = int(k)
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    targets_t = torch.tensor(targets, dtype=torch.long, device=starts.device)
    valid = targets_t >= 0
    correct = (pred_b == targets_t) & valid
    return correct.float()


def measure_cell(strategy: str, N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_full(
        N_use, M, seed, device)
    starts_list = list(relation.keys())[:N_STARTS]
    if not starts_list:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return _empty_result(strategy, M, depth, K_paths, seed)
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)

    # Always measure baseline Path D for delta computation
    t_d0 = time.perf_counter_ns()
    correct_d = path_d_run(codebook, W, starts, relation, depth, K_paths,
                            seed, N_use, beta=BETA_D)
    lat_d_ns = time.perf_counter_ns() - t_d0
    acc_d = float(correct_d.mean().item())

    # Selection heuristic for A and C
    high_K = (K_paths >= HIGH_K_THRESHOLD)
    sub_cap = (M < SUB_CAP_M_THRESHOLD)

    t_strat0 = time.perf_counter_ns()
    verifier_catch_rate = 0.0
    strat_acc = acc_d
    overhead_ns = 0
    strat_meta: Dict = {"high_K": high_K, "sub_cap": sub_cap}

    if strategy == "A_heuristic":
        # Fall through: high-K -> E (just use E AUC as verifier-based final score
        # mapped to accuracy via majority-correct on positives), sub-capacity ->
        # B, otherwise D. For each path we measure its accuracy directly.
        if high_K:
            pos = sample_coherent_starts(relation, depth, N_STARTS, seed)
            neg = sample_incoherent_paths(codebook.shape[0], depth, N_STARTS,
                                            seed, relation=relation)
            auc_e = path_e_run(codebook, W, pos, neg, N_use) if (pos and neg) else 0.5
            # Map AUC -> accuracy-equivalent for verifier-only branch.
            # Treat AUC>=0.5 as positives correctly ordered.
            strat_acc = float(auc_e)
            strat_meta["chosen"] = "E"
        elif sub_cap:
            correct_b = _path_b_acc(codebook, W, starts, depth, N_use, relation)
            strat_acc = float(correct_b.mean().item())
            strat_meta["chosen"] = "B"
        else:
            strat_acc = acc_d
            strat_meta["chosen"] = "D"

    elif strategy == "B_parallel_verify":
        # Run B, D, E. Return D's result. Flag disagreements with B
        # (per-start) and count where the verifier was right and D was wrong.
        correct_b = _path_b_acc(codebook, W, starts, depth, N_use, relation)
        # Path D returns indicator (1 if correctly picked coherent path).
        # Disagreement: D=0 and B=1 -> verifier caught a D error.
        # Or D=1 and B=0 -> verifier disagrees but D wins (don't count).
        d_wrong = (correct_d == 0)
        b_right = (correct_b == 1)
        catches = (d_wrong & b_right).float().sum().item()
        n_total = int(correct_d.shape[0])
        verifier_catch_rate = (catches / n_total) if n_total > 0 else 0.0
        # Also include E as second verifier on coherent/incoherent task
        pos = sample_coherent_starts(relation, depth, N_STARTS, seed)
        neg = sample_incoherent_paths(codebook.shape[0], depth, N_STARTS,
                                        seed, relation=relation)
        auc_e = path_e_run(codebook, W, pos, neg, N_use) if (pos and neg) else 0.5
        strat_meta["chosen"] = "B+D+E"
        strat_meta["verifier_E_auc"] = round(auc_e, 4)
        strat_meta["verifier_B_acc"] = round(float(correct_b.mean().item()), 4)
        # Strategy returns D's accuracy (D is the canonical output)
        strat_acc = acc_d

    elif strategy == "C_targeted_verifier":
        # D + ONE verifier; verifier chosen by query characteristic
        if high_K:
            pos = sample_coherent_starts(relation, depth, N_STARTS, seed)
            neg = sample_incoherent_paths(codebook.shape[0], depth, N_STARTS,
                                            seed, relation=relation)
            auc_e = path_e_run(codebook, W, pos, neg, N_use) if (pos and neg) else 0.5
            strat_meta["chosen_verifier"] = "E"
            strat_meta["verifier_E_auc"] = round(auc_e, 4)
            # Catch rate proxy: cells where E AUC > 0.5 disambiguates a D failure
            # Approximate verifier_catch_rate as max(0, auc_e - 0.5) * frac(D wrong)
            d_wrong_frac = float((correct_d == 0).float().mean().item())
            verifier_catch_rate = max(0.0, auc_e - 0.5) * d_wrong_frac
        else:
            correct_b = _path_b_acc(codebook, W, starts, depth, N_use, relation)
            d_wrong = (correct_d == 0)
            b_right = (correct_b == 1)
            catches = (d_wrong & b_right).float().sum().item()
            n_total = int(correct_d.shape[0])
            verifier_catch_rate = (catches / n_total) if n_total > 0 else 0.0
            strat_meta["chosen_verifier"] = "B"
            strat_meta["verifier_B_acc"] = round(float(correct_b.mean().item()), 4)
        strat_acc = acc_d

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    strat_lat_ns = time.perf_counter_ns() - t_strat0
    overhead_ns = strat_lat_ns  # strategy time including verifiers

    accuracy_delta = strat_acc - acc_d
    when_useful = 1 if (verifier_catch_rate >= HP_VERIFIER_CATCH
                          or accuracy_delta >= HP_ACCURACY_DELTA) else 0

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"strategy": strategy, "M": int(M), "depth": int(depth),
            "K_paths": int(K_paths), "seed": int(seed),
            "baseline_d_acc": round(acc_d, 5),
            "baseline_d_lat_ns": int(lat_d_ns),
            "strat_acc": round(strat_acc, 5),
            "accuracy_delta": round(accuracy_delta, 5),
            "strategy_overhead_ns": int(overhead_ns),
            "verifier_catch_rate": round(verifier_catch_rate, 5),
            "when_useful": when_useful,
            "strat_meta": strat_meta}


def _empty_result(strategy, M, depth, K_paths, seed):
    return {"strategy": strategy, "M": int(M), "depth": int(depth),
            "K_paths": int(K_paths), "seed": int(seed),
            "baseline_d_acc": 0.0, "baseline_d_lat_ns": 0,
            "strat_acc": 0.0, "accuracy_delta": 0.0,
            "strategy_overhead_ns": 0, "verifier_catch_rate": 0.0,
            "when_useful": 0, "strat_meta": {}}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("G3_INCONCLUSIVE", "no cells")

    # Group by (strategy, regime/M)
    by_sr: Dict[Tuple[str, int], List[Dict]] = {}
    for c in cells:
        by_sr.setdefault((c["strategy"], c["M"]), []).append(c)

    hp_hits = 0
    advantages: List[str] = []
    max_catch = 0.0
    max_delta = 0.0
    for (strat, M), cs in by_sr.items():
        # number of seeds where strategy delivered HP-style advantage
        seeds_advantaged = sum(
            1 for c in cs
            if (c["verifier_catch_rate"] >= HP_VERIFIER_CATCH
                or c["accuracy_delta"] >= HP_ACCURACY_DELTA))
        max_catch = max(max_catch,
                         max(c["verifier_catch_rate"] for c in cs))
        max_delta = max(max_delta, max(c["accuracy_delta"] for c in cs))
        if seeds_advantaged >= HP_SEEDS_MIN:
            hp_hits += 1
            advantages.append(f"{strat}@M{M}:{seeds_advantaged}/{len(cs)}")

    # HF check: NO catch and NO accuracy delta across ALL cells
    all_below = all(
        (c["verifier_catch_rate"] < HF_VERIFIER_CATCH_BELOW
         and c["accuracy_delta"] < HF_ACC_DELTA_BELOW)
        for c in cells)

    detail = (f"hp_hits={hp_hits}/{len(by_sr)} (need>=1) "
              f"advantages=[{','.join(advantages)}] "
              f"max_catch={max_catch:.4f} max_delta={max_delta:.4f} "
              f"n_cells={len(cells)}")

    if all_below:
        return ("G3_HARD_FAIL", "NO_COMPOSITION_VALUE: " + detail)
    if hp_hits >= 1:
        return ("G3_HARD_PASS", "COMPOSITION_USEFUL: " + detail)
    return ("G3_MIDDLE_BAND", "COMPOSITION_PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert STRATEGIES == ["A_heuristic", "B_parallel_verify",
                            "C_targeted_verifier"]
    assert len(REGIMES_FULL) == 3
    assert len(SEEDS_FULL) == 5

    # HP gate
    fake_hp: List[Dict] = []
    for strat in STRATEGIES:
        for _, M in REGIMES_FULL:
            for s in SEEDS_FULL:
                fake_hp.append({"strategy": strat, "M": M, "depth": DEPTH_FIXED,
                                  "K_paths": K_FIXED, "seed": s,
                                  "baseline_d_acc": 0.80, "baseline_d_lat_ns": 1,
                                  "strat_acc": 0.86, "accuracy_delta": 0.06,
                                  "strategy_overhead_ns": 1,
                                  "verifier_catch_rate": 0.0,
                                  "when_useful": 1, "strat_meta": {}})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # HF gate (no value)
    fake_hf: List[Dict] = []
    for strat in STRATEGIES:
        for _, M in REGIMES_FULL:
            for s in SEEDS_FULL:
                fake_hf.append({"strategy": strat, "M": M, "depth": DEPTH_FIXED,
                                  "K_paths": K_FIXED, "seed": s,
                                  "baseline_d_acc": 0.85,
                                  "baseline_d_lat_ns": 1,
                                  "strat_acc": 0.85, "accuracy_delta": 0.0,
                                  "strategy_overhead_ns": 1,
                                  "verifier_catch_rate": 0.0,
                                  "when_useful": 0, "strat_meta": {}})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # MB gate (only 1 strategy advantaged in 1 seed -> not 3/5)
    fake_mb: List[Dict] = []
    for strat in STRATEGIES:
        for _, M in REGIMES_FULL:
            for i, s in enumerate(SEEDS_FULL):
                delta = 0.06 if (strat == "A_heuristic"
                                  and M == 2048 and i == 0) else 0.0
                catch = 0.0
                fake_mb.append({"strategy": strat, "M": M, "depth": DEPTH_FIXED,
                                  "K_paths": K_FIXED, "seed": s,
                                  "baseline_d_acc": 0.80,
                                  "baseline_d_lat_ns": 1,
                                  "strat_acc": 0.80 + delta,
                                  "accuracy_delta": delta,
                                  "strategy_overhead_ns": 1,
                                  "verifier_catch_rate": catch,
                                  "when_useful": 1 if delta > 0 else 0,
                                  "strat_meta": {}})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, f"MB: {v}"

    # Smoke forward pass on CPU (smallest config + each strategy)
    device = torch.device("cpu")
    for strat in STRATEGIES:
        out = measure_cell(strat, N_SMOKE, REGIMES_SMOKE[0][1], DEPTH_FIXED,
                            50, 17, device)
        assert 0.0 <= out["strat_acc"] <= 1.0
        assert out["baseline_d_lat_ns"] > 0
    print(f"[selftest] handoff_composition_probe_v1_n4096 PASS smoke all 3 "
          f"strategies executed", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    regimes = REGIMES_SMOKE if smoke else REGIMES_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_use = 50 if smoke else K_FIXED

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] handoff_composition_probe smoke={smoke} N={N_cfg} "
          f"regimes={regimes} K={K_use} depth={DEPTH_FIXED} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for strat in STRATEGIES:
        for reg_name, M in regimes:
            for seed in seeds:
                ck = f"{strat}_{reg_name}_M{M}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(strat, N_cfg, M, DEPTH_FIXED, K_use,
                                        seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  {strat} {reg_name}(M={M}) seed={seed} "
                          f"d_acc={out['baseline_d_acc']:.3f} "
                          f"strat_acc={out['strat_acc']:.3f} "
                          f"delta={out['accuracy_delta']:+.3f} "
                          f"catch={out['verifier_catch_rate']:.3f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  {strat} {reg_name} M={M} seed={seed} FAILED: {e}",
                          flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "handoff_composition_probe_v1_n4096", "N": N_cfg,
               "smoke": smoke, "regimes": regimes, "K": K_use,
               "depth": DEPTH_FIXED, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
