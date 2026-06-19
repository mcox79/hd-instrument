"""Bet 2 v7 - 32-coset Kerdock MM. M_stored up to 32N=131072.

Risky: GPU memory at 32N is 2 GB just for codebook. If OOMs at smoke, back off.

Pre-reg: preregs/2026-05-21_wave14zc_erase_kerdock_v7_32coset.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v2 = importlib.util.spec_from_file_location("v2", REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py")
v2 = importlib.util.module_from_spec(_v2); _v2.loader.exec_module(v2)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_v4 = importlib.util.spec_from_file_location("v4", REPO / "experiments" / "exp_wave14ya_erase_kerdock_v4.py")
v4 = importlib.util.module_from_spec(_v4); _v4.loader.exec_module(v4)

NUM_COSETS = 32


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def make_kerdock_32coset_codebook(N, device):
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N or n_log2 % 2 != 0:
        raise ValueError(f"N={N} must be 2^even")
    t = n_log2 // 2
    period = (1 << t) - 1
    if NUM_COSETS - 1 > period:
        raise ValueError(f"NUM_COSETS-1={NUM_COSETS-1} > GF(2^{t}) period {period}")
    log_tab, antilog_tab = v3.build_gf2t_tables(t)
    H = v1.sylvester_hadamard(n_log2, device)
    b_values = [0] + [antilog_tab[i] for i in range(NUM_COSETS - 1)]
    if len(set(b_values)) != len(b_values):
        raise ValueError(f"b_values not distinct")
    cosets = []
    for b in b_values:
        q_b = v3.build_q_b_signs(b, N, t, log_tab, antilog_tab, device)
        cosets.append(H * q_b.unsqueeze(0))
    codebook = torch.cat(cosets, dim=0)
    return codebook, {"t": t, "n_cosets": len(b_values),
                       "codebook_size": codebook.shape[0]}


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("KERDOCK_V7_INCONCLUSIVE", "Missing.")
    N = summary.get("N", 4096)
    kerdock_rows = arms["kerdock"].get("per_M", [])
    correlated_rows = arms["correlated"].get("per_M", [])
    if not kerdock_rows or not correlated_rows:
        return ("KERDOCK_V7_INCONCLUSIVE", "Empty.")
    kerdock_pass = {r["M_stored"]: v3.cell_passes(r) for r in kerdock_rows}
    ms_sorted = sorted(kerdock_pass.keys())
    largest_pass = max((m for m in ms_sorted if kerdock_pass[m][0]), default=None)
    first_fail = next((m for m in ms_sorted if not kerdock_pass[m][0]), None)
    if first_fail is None:
        return ("KERDOCK_V7_EXTENDS_TO_32N",
                f"Kerdock passes all M in {ms_sorted} (up to {max(ms_sorted)} = "
                f"{max(ms_sorted)/N:.2f}*N). Bet 2 envelope confirmed at 32x over-capacity. "
                f"Substrate stores 32x its rank-N capacity worth of (v, k) pairs with "
                f"erase remaining Mirage-clean.")
    return (f"KERDOCK_V7_DECAYS_AT_{first_fail}",
            f"Kerdock holds up to M={largest_pass}; fails at M={first_fail} "
            f"(= {first_fail/N:.2f}*N): {'; '.join(kerdock_pass[first_fail][1])}.")


def self_test_verdict():
    def mk_row(M, args):
        return {"M_stored": M,
                "argmax_leak": args.get("a", 0.02),
                "mean_rank": args.get("r", max(2.0, M * v3.PASS_RANK_FRAC * 2)),
                "norm_ratio": args.get("n", 0.05),
                "paraphrase_leak_h8": args.get("p", 0.02),
                "kept_preservation": args.get("k", 0.98)}
    ms = [16384, 32768, 65536, 98304, 131072]
    cases = [
        ({"N": 4096, "by_arm": {"kerdock": {"per_M": [mk_row(m, {}) for m in ms]},
                                    "correlated": {"per_M": [mk_row(m, {"a": 0.20}) for m in ms]}}},
         "KERDOCK_V7_EXTENDS_TO_32N"),
        ({"N": 4096, "by_arm": {"kerdock": {"per_M": [mk_row(16384, {}), mk_row(32768, {}),
                                                          mk_row(65536, {"a": 0.20}),
                                                          mk_row(98304, {"a": 0.20}),
                                                          mk_row(131072, {"a": 0.20})]},
                                    "correlated": {"per_M": [mk_row(m, {"a": 0.20}) for m in ms]}}},
         "KERDOCK_V7_DECAYS_AT_65536"),
        ({}, "KERDOCK_V7_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (3/3 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored_list": [4096, 8192] if smoke else [16384, 32768, 65536, 98304, 131072],
              "n_erase": 5 if smoke else 30,
              "n_kept_probe": 10 if smoke else 100,
              "n_paraphrase": 20,
              "hamming_radii": [8] if smoke else [4, 8, 16],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53],
              "alpha": 1.0, "num_cosets": NUM_COSETS}
    print(f"[config] {config}", flush=True)
    codebook, info = make_kerdock_32coset_codebook(config["N"], device)
    print(f"[codebook] size={codebook.shape}, info={info}", flush=True)
    arm_k = v4.run_arm("kerdock", codebook, config["M_stored_list"], config, device)
    arm_c = v4.run_arm("correlated", None, config["M_stored_list"], config, device)
    summary = {"N": config["N"], "by_arm": {"kerdock": arm_k, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
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
    out_dir = get_output_dir("wave14zc_erase_kerdock_v7_32coset_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zc_erase_kerdock_v7_32coset")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
