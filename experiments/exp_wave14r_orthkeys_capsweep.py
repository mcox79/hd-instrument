"""Capacity-envelope sweep of the wave14r_erase_orthkeys_v1 finding.

v1 validated STRUCT_KEYS_FIX_MIRAGE at M_stored=200, N=4096. This sweep
runs the Hadamard arm only at M_stored in {200, 800, 1600, 3200} to find
where the orthogonal-key Mirage protection breaks down. Output is the
operating envelope Strategy needs to upgrade the cap_map row from 🟢 to ✅.

Pre-reg: preregs/2026-05-21_wave14r_orthkeys_capsweep.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


# Import v1 functions by file path (the module name has hyphens/underscores
# that import statements handle, but using importlib is more robust against
# future renames).
_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec = importlib.util.spec_from_file_location("wave14r_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)


N_FULL = 4096
N_SMOKE = 512
M_STORED_FULL = [200, 800, 1600, 3200]
M_STORED_SMOKE = [40, 100]
N_ERASE_FULL = 30
N_ERASE_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 10
N_PARAPHRASE = 20
HAMMING_RADII_FULL = [2, 4, 8, 16]
HAMMING_RADII_SMOKE = [4, 8]
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_ARGMAX = 0.05
PASS_RANK_FRAC = 0.3  # rank > M_stored * 0.3 (per Mirage paper / wave14p)
PASS_NORM = 0.15
PASS_PARAPHRASE = 0.05
PASS_KEPT = 0.95


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def probe_row_passes(row: dict) -> tuple[bool, list[str]]:
    fails = []
    M = row.get("M_stored", 1)
    rank_threshold = max(2.0, M * PASS_RANK_FRAC)
    if row["argmax_leak"] >= PASS_ARGMAX:
        fails.append(f"argmax_leak={row['argmax_leak']:.3f}")
    if row["mean_rank"] <= rank_threshold:
        fails.append(f"rank={row['mean_rank']:.1f}<={rank_threshold:.1f}")
    if row["norm_ratio"] >= PASS_NORM:
        fails.append(f"norm={row['norm_ratio']:.3f}")
    para_h8 = row.get("paraphrase_leak_h8", 1.0)
    if para_h8 >= PASS_PARAPHRASE:
        fails.append(f"para_h8={para_h8:.3f}")
    if row["kept_preservation"] < PASS_KEPT:
        fails.append(f"kept={row['kept_preservation']:.3f}")
    return (len(fails) == 0, fails)


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_m = summary.get("by_M_stored")
    if not by_m:
        return ("CAPSWEEP_INCONCLUSIVE", "No per-M_stored data.")

    sorted_ms = sorted(by_m.keys())  # ascending
    passes_until = None
    first_failure_M = None
    first_failure_reason = None
    for m in sorted_ms:
        row = by_m[m]
        ok, fails = probe_row_passes(row)
        if ok:
            passes_until = m
        else:
            first_failure_M = m
            first_failure_reason = "; ".join(fails)
            break

    if passes_until is None:
        smallest_M = sorted_ms[0]
        return ("CAPSWEEP_BREAKS_IMMEDIATELY",
                f"Even smallest M_stored={smallest_M} fails: {first_failure_reason}. "
                f"Contradicts wave14r_erase_orthkeys_v1; audit test setup.")

    if first_failure_M is None:
        return ("CAPSWEEP_ROBUST",
                f"All M_stored values {sorted_ms} pass all 5 Mirage probes at alpha=1.0. "
                f"Orthogonal-key Mirage protection robust through "
                f"M_stored={sorted_ms[-1]}/N={by_m[sorted_ms[-1]].get('N', '?')} = "
                f"{sorted_ms[-1] / by_m[sorted_ms[-1]].get('N', N_FULL):.2f}. "
                f"Envelope characterized; cap_map upgrade candidate.")

    return (f"CAPSWEEP_BREAKS_AT_{first_failure_M}",
            f"Passes through M_stored={passes_until}; breaks at M_stored="
            f"{first_failure_M} with: {first_failure_reason}. Envelope is "
            f"[smallest_tested, {passes_until}]; cap_map row stays validated with envelope caveat.")


def self_test_verdict() -> None:
    def mk(m, args, N=4096):
        return {"M_stored": m,
                "argmax_leak": args.get("a", 0.02),
                "mean_rank": args.get("r", m * 0.5),
                "norm_ratio": args.get("n", 0.05),
                "paraphrase_leak_h8": args.get("p", 0.02),
                "kept_preservation": args.get("k", 0.98),
                "N": N}

    cases = [
        # 1. ROBUST: all pass
        ({"by_M_stored": {
            200: mk(200, {}), 800: mk(800, {}), 1600: mk(1600, {}), 3200: mk(3200, {})}},
         "CAPSWEEP_ROBUST"),
        # 2. BREAKS_AT_3200: pass 200/800/1600, fail at 3200
        ({"by_M_stored": {
            200: mk(200, {}), 800: mk(800, {}), 1600: mk(1600, {}),
            3200: mk(3200, {"a": 0.10})}},
         "CAPSWEEP_BREAKS_AT_3200"),
        # 3. BREAKS_AT_800
        ({"by_M_stored": {
            200: mk(200, {}), 800: mk(800, {"r": 50}),
            1600: mk(1600, {}), 3200: mk(3200, {})}},
         "CAPSWEEP_BREAKS_AT_800"),
        # 4. BREAKS_IMMEDIATELY
        ({"by_M_stored": {
            200: mk(200, {"a": 0.20}), 800: mk(800, {}),
            1600: mk(1600, {}), 3200: mk(3200, {})}},
         "CAPSWEEP_BREAKS_IMMEDIATELY"),
        # 5. INCONCLUSIVE
        ({}, "CAPSWEEP_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_M(M_stored: int, N: int, config: dict, device: torch.device) -> dict:
    """Run the Hadamard arm at a single M_stored, aggregate across seeds."""
    n_erase = config["n_erase"]
    n_kept = config["n_kept_probe"]
    hamming = config["hamming_radii"]
    n_para = config["n_paraphrase"]
    seeds = config["seeds"]

    per_seed = []
    pairwise_stats = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        keys = v1.make_hadamard_keys(M_stored, N, cpu_gen, device)
        values = 2.0 * (torch.rand((M_stored, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (values.T @ keys) / N

        key_ips = (keys @ keys.T) / N
        mask = ~torch.eye(M_stored, dtype=torch.bool, device=device)
        off_diag = key_ips[mask]
        pairwise_stats.append({
            "seed": seed, "max_abs": float(off_diag.abs().max()),
        })

        erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        erase_idx = sorted(torch.randperm(M_stored, generator=erase_gen)[:n_erase].tolist())
        erase_set = set(erase_idx)
        candidates = [i for i in range(M_stored) if i not in erase_set]
        kept_idx = sorted(torch.tensor(candidates)[torch.randperm(
            len(candidates), generator=kept_gen)[:n_kept]].tolist())

        W_edit = W.clone()
        for i in erase_idx:
            W_edit = v1.antihebbian_erase(W_edit, keys[i], ALPHA)

        probe = v1.multi_probe(W_edit, keys, values, erase_idx, kept_idx,
                                  hamming, n_para, cpu_gen, device)
        probe["seed"] = seed
        per_seed.append(probe)

    def avg(k):
        vals = [r[k] for r in per_seed if k in r]
        return sum(vals) / len(vals) if vals else 0.0
    out = {
        "M_stored": M_stored, "N": N,
        "argmax_leak": avg("argmax_leak"),
        "mean_rank": avg("mean_rank"),
        "norm_ratio": avg("norm_ratio"),
        "cosine": avg("cosine"),
        "kept_preservation": avg("kept_preservation"),
        "pairwise_stats": pairwise_stats,
        "per_seed": per_seed,
    }
    for h in hamming:
        out[f"paraphrase_leak_h{h}"] = avg(f"paraphrase_leak_h{h}")
    return out


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored_list": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_erase": N_ERASE_SMOKE if smoke else N_ERASE_FULL,
        "n_kept_probe": N_KEPT_PROBE_SMOKE if smoke else N_KEPT_PROBE_FULL,
        "n_paraphrase": N_PARAPHRASE,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alpha": ALPHA,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    by_M = {}
    for M in config["M_stored_list"]:
        print(f"[M_stored={M}] running...", flush=True)
        row = run_one_M(M, config["N"], config, device)
        by_M[M] = row
        paras = " ".join(f"p_h{h}={row[f'paraphrase_leak_h{h}']:.3f}"
                          for h in config["hamming_radii"])
        print(f"  M={M:5d}  argmax={row['argmax_leak']:.3f}  rank={row['mean_rank']:.1f}  "
              f"norm={row['norm_ratio']:.3f}  {paras}  kept={row['kept_preservation']:.3f}",
              flush=True)

    summary = {"by_M_stored": by_M}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14r_orthkeys_capsweep_smoke")
    log_event("experiment_started", name="wave14r_orthkeys_capsweep", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle: orthogonality check at smallest M_stored
    smallest = min(summary["by_M_stored"].keys())
    pairwise = summary["by_M_stored"][smallest]["pairwise_stats"]
    max_ip = max(p["max_abs"] for p in pairwise)
    oracle.assert_in_range("hadamard_max_pairwise_ip", max_ip, (0.0, 0.01))

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_orthkeys_capsweep",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_orthkeys_capsweep")
    log_event("experiment_started", name="wave14r_orthkeys_capsweep", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_orthkeys_capsweep",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
