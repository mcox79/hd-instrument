"""Bet 2 v5 - 16-coset Kerdock MM, M_stored up to 16N=65536.

Extends v4 (8 cosets, EXTENDS_TO_8N) to 16 cosets. Tests if Kerdock has
any envelope ceiling at all.

Pre-reg: preregs/2026-05-21_wave14ye_erase_kerdock_v5.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
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


_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec1 = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(v1)

_v2_path = REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py"
spec2 = importlib.util.spec_from_file_location("kerdock_v2", _v2_path)
v2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v2)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

_v4_path = REPO / "experiments" / "exp_wave14ya_erase_kerdock_v4.py"
spec4 = importlib.util.spec_from_file_location("kerdock_v4", _v4_path)
v4 = importlib.util.module_from_spec(spec4)
spec4.loader.exec_module(v4)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = [8192, 16384, 32768, 49152, 65536]
M_STORED_SMOKE = [2048, 8192, 16384]
N_ERASE_FULL = 30
N_ERASE_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 10
N_PARAPHRASE = 20
HAMMING_RADII_FULL = [4, 8, 16]
HAMMING_RADII_SMOKE = [8]
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0
NUM_COSETS = 16

PASS_ARGMAX = v3.PASS_ARGMAX
PASS_RANK_FRAC = v3.PASS_RANK_FRAC
PASS_NORM = v3.PASS_NORM
PASS_PARAPHRASE = v3.PASS_PARAPHRASE
PASS_KEPT = v3.PASS_KEPT


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing: {required - set(d.keys())}")


def make_kerdock_16coset_codebook(N, device):
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N or n_log2 % 2 != 0:
        raise ValueError(f"N={N} must be 2^even")
    t = n_log2 // 2
    period = (1 << t) - 1
    if NUM_COSETS - 1 > period:
        raise ValueError(f"NUM_COSETS-1={NUM_COSETS-1} > GF period {period}")
    log_tab, antilog_tab = v3.build_gf2t_tables(t)
    H = v1.sylvester_hadamard(n_log2, device)
    b_values = [0] + [antilog_tab[i] for i in range(NUM_COSETS - 1)]
    if len(set(b_values)) != len(b_values):
        raise ValueError(f"b_values not distinct: {b_values}")
    cosets = []
    for b in b_values:
        q_b = v3.build_q_b_signs(b, N, t, log_tab, antilog_tab, device)
        cosets.append(H * q_b.unsqueeze(0))
    codebook = torch.cat(cosets, dim=0)
    info = {"t": t, "n_cosets": len(b_values), "codebook_size": codebook.shape[0],
            "b_values": b_values}
    return codebook, info


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("KERDOCK_V5_INCONCLUSIVE", "Missing arms.")
    N = summary.get("N", N_FULL)
    kerdock_rows = arms["kerdock"].get("per_M", [])
    correlated_rows = arms["correlated"].get("per_M", [])
    if not kerdock_rows or not correlated_rows:
        return ("KERDOCK_V5_INCONCLUSIVE", "Empty rows.")

    kerdock_pass = {r["M_stored"]: v3.cell_passes(r) for r in kerdock_rows}
    corr_pass = {r["M_stored"]: v3.cell_passes(r) for r in correlated_rows}
    ms_sorted = sorted(kerdock_pass.keys())

    if all(corr_pass[m][0] for m in ms_sorted):
        return ("KERDOCK_V5_CORRELATED_PASSES",
                f"Correlated arm passes all M. Audit setup.")

    largest_pass = max((m for m in ms_sorted if kerdock_pass[m][0]), default=None)
    first_fail = next((m for m in ms_sorted if not kerdock_pass[m][0]), None)

    if first_fail is not None and first_fail <= 8 * N:
        return ("KERDOCK_V5_REGRESSES_BELOW_V4",
                f"Kerdock fails at M={first_fail} <= 8N. Contradicts v4. Audit.")

    if first_fail is None:
        return ("KERDOCK_V5_EXTENDS_TO_16N",
                f"Kerdock arm passes at all M in {ms_sorted} (up to "
                f"{max(ms_sorted)} = {max(ms_sorted)/N:.2f}*N). Correlated fails "
                f"as expected. Bet 2 envelope effectively unbounded by codebook "
                f"density at substrate width N={N}; the substrate stores "
                f"16x its rank-N capacity worth of (v, k) pairs while "
                f"kept_preservation holds and erase remains Mirage-clean.")

    return (f"KERDOCK_V5_DECAYS_AT_{first_fail}",
            f"Kerdock arm holds up to M={largest_pass}; fails at "
            f"M={first_fail} (= {first_fail/N:.2f}*N) with: "
            f"{'; '.join(kerdock_pass[first_fail][1])}.")


def self_test_verdict():
    N_test = 4096

    def mk_row(M, args):
        rank_default = max(2.0, M * PASS_RANK_FRAC * 2)
        return {"M_stored": M,
                "argmax_leak": args.get("a", 0.02),
                "mean_rank": args.get("r", rank_default),
                "norm_ratio": args.get("n", 0.05),
                "paraphrase_leak_h8": args.get("p", 0.02),
                "kept_preservation": args.get("k", 0.98)}

    pass_args, fail_args = {}, {"a": 0.20}
    ms = [8192, 16384, 32768, 49152, 65536]

    cases = [
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in ms]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V5_EXTENDS_TO_16N"),
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(8192, pass_args), mk_row(16384, pass_args),
                                    mk_row(32768, pass_args), mk_row(49152, fail_args),
                                    mk_row(65536, fail_args)]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V5_DECAYS_AT_49152"),
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(8192, fail_args)] +
                                    [mk_row(m, fail_args) for m in ms[1:]]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V5_REGRESSES_BELOW_V4"),
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in ms]},
            "correlated": {"per_M": [mk_row(m, pass_args) for m in ms]}}},
         "KERDOCK_V5_CORRELATED_PASSES"),
        ({"N": N_test, "by_arm": {}}, "KERDOCK_V5_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
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
        "alpha": ALPHA, "num_cosets": NUM_COSETS,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building 16-coset MM codebook at N={config['N']}...", flush=True)
    codebook, info = make_kerdock_16coset_codebook(config["N"], device)
    print(f"[codebook] size={codebook.shape}", flush=True)

    # Codebook stats
    N = config["N"]
    book_ips = (codebook @ codebook.T) / N
    book_mask = ~torch.eye(codebook.size(0), dtype=torch.bool, device=device)
    book_max = float(book_ips[book_mask].abs().max())
    print(f"[codebook] book_max_abs={book_max:.6f}  expected=1/sqrt(N)="
          f"{1.0/math.sqrt(N):.6f}", flush=True)

    print(f"[arm=kerdock] running...", flush=True)
    arm_k = v4.run_arm("kerdock", codebook, config["M_stored_list"], config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = v4.run_arm("correlated", None, config["M_stored_list"], config, device)

    summary = {
        "N": config["N"],
        "by_arm": {"kerdock": arm_k, "correlated": arm_c},
        "codebook_stats": {"size": codebook.shape[0], "info": info,
                             "book_max_abs_ip": book_max,
                             "expected_welch_bound": 1.0 / math.sqrt(N)},
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm_data in summary["by_arm"].items():
        print(f"[{arm_name}]", flush=True)
        for row in arm_data["per_M"]:
            paras = " ".join(f"p_h{h}={row[f'paraphrase_leak_h{h}']:.3f}"
                              for h in config["hamming_radii"])
            print(f"  M={row['M_stored']:6d}  argmax={row['argmax_leak']:.3f}  "
                  f"rank={row['mean_rank']:.1f}  norm={row['norm_ratio']:.3f}  "
                  f"{paras}  kept={row['kept_preservation']:.3f}", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14ye_erase_kerdock_v5_smoke")
    log_event("experiment_started", name="wave14ye_erase_kerdock_v5", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    N = config["N"]
    expected = 1.0 / math.sqrt(N)
    max_abs = summary["codebook_stats"]["book_max_abs_ip"]
    oracle.assert_in_range("kerdock_v5_welch", max_abs,
                            (expected * 0.95, expected * 1.05))
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14ye_erase_kerdock_v5",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14ye_erase_kerdock_v5")
    log_event("experiment_started", name="wave14ye_erase_kerdock_v5", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14ye_erase_kerdock_v5",
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
