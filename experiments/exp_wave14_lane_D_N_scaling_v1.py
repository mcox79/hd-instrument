"""Lane D N-scaling — does the COMPOSE capacity envelope scale with N?

Capacity stress at N=4096 found breakpoints M_S=300 facts, K=25 hypotheses
(U_stream and X_alphabet healthy through max sweep). This re-runs the stress
sweep at N in {4096, 8192, 16384} to characterize Lane D capacity scaling.

Substrate-product question: does Lane D capacity scale linearly with N
(M_S_breakpoint(N) = c*N) or sublinearly?

Verdict:
  N_SCALING_LINEAR: M_S_breakpoint roughly tracks N (c ratio within +/-30%)
  N_SCALING_SUBLINEAR: M_S_breakpoint grows slower than N (substrate saturation)
  N_SCALING_INVERTED: M_S_breakpoint shrinks with N (rare; flag)
  N_SCALING_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_lane_D_N_scaling_v1.md
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

_cs = importlib.util.spec_from_file_location("cs",
    REPO / "experiments" / "exp_wave14_lane_D_capacity_stress_v1.py")
cs = importlib.util.module_from_spec(_cs); _cs.loader.exec_module(cs)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "M_S_breakpoint_per_N" not in summary:
        return ("N_SCALING_INCONCLUSIVE", "Missing breakpoint table.")
    bp_per_N = summary["M_S_breakpoint_per_N"]
    Ns = sorted(int(k) for k in bp_per_N.keys())
    if len(Ns) < 2:
        return ("N_SCALING_INCONCLUSIVE", f"Need >=2 Ns, got {len(Ns)}.")
    # Replace 'None' (no breakpoint = beyond max sweep) with max-sweep ceiling for ratio
    cs = []
    for N in Ns:
        bp = bp_per_N[str(N)]
        if bp is None: bp = summary["max_M_S_swept"]
        cs.append(bp / N)
    mean_c = sum(cs) / len(cs)
    spread = max(cs) - min(cs)
    rel_spread = spread / max(mean_c, 1e-9)
    if rel_spread <= 0.30:
        return ("N_SCALING_LINEAR",
                f"M_S breakpoint scales linearly with N: c ratio per N = {[round(c,3) for c in cs]} "
                f"(rel spread {rel_spread:.2f}<=0.30, mean c={mean_c:.3f}).")
    # INVERTED = absolute breakpoint shrinks; SUBLINEAR = breakpoint grows but slower than N
    bps_resolved = [bp_per_N[str(N)] if bp_per_N[str(N)] is not None else summary["max_M_S_swept"]
                     for N in Ns]
    if bps_resolved[-1] < bps_resolved[0]:
        return ("N_SCALING_INVERTED",
                f"M_S breakpoint shrinks with N (absolute): bps={bps_resolved}. "
                f"Substrate capacity inverted.")
    return ("N_SCALING_SUBLINEAR",
            f"M_S breakpoint grows sublinearly with N: per-N c ratio = {[round(c,3) for c in cs]} "
            f"(rel spread {rel_spread:.2f}>0.30). Substrate saturates.")


def self_test_verdict():
    cases = [
        ({"M_S_breakpoint_per_N": {"4096": 300, "8192": 600, "16384": 1200}, "max_M_S_swept": 2400}, "N_SCALING_LINEAR"),
        ({"M_S_breakpoint_per_N": {"4096": 300, "8192": 400, "16384": 500}, "max_M_S_swept": 2400}, "N_SCALING_SUBLINEAR"),
        ({"M_S_breakpoint_per_N": {"4096": 800, "8192": 400, "16384": 200}, "max_M_S_swept": 2400}, "N_SCALING_INVERTED"),
        ({}, "N_SCALING_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def find_M_S_breakpoint(N, M_S_grid, K, U_stream, X_alphabet, gen, cpu_gen, device):
    """Sweep M_S only; return first M_S where any metric < 0.70."""
    cbs = cs.make_codebooks(N, gen, device, K, X_alphabet)
    for M_S in M_S_grid:
        s_acc = cs.measure_S(M_S, N, cbs, cpu_gen, device)
        t_acc = cs.measure_T(K, 10, N, cbs, cpu_gen, device)
        u_acc = cs.measure_U(U_stream, N, cbs, cpu_gen, device)
        x_acc = cs.measure_X(X_alphabet, N, cbs, cpu_gen, device)
        print(f"    N={N} M_S={M_S}: S={s_acc:.3f} T={t_acc:.3f} U={u_acc:.3f} X={x_acc:.3f}", flush=True)
        if min(s_acc, t_acc, u_acc, x_acc) < 0.70:
            return M_S
    return None


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [1024, 2048] if smoke else [4096, 8192, 16384],
              "M_S_grid": [50, 150, 300] if smoke else [50, 150, 300, 600, 1200, 2400],
              "K": 3, "U_stream": 40, "X_alphabet": 5,
              "seed": 17}
    breakpoints = {}
    for N in config["N_grid"]:
        gen = torch.Generator(device=device).manual_seed(config["seed"])
        cpu_gen = torch.Generator().manual_seed(config["seed"] + 1009)
        print(f"[N={N}]", flush=True)
        bp = find_M_S_breakpoint(N, config["M_S_grid"], config["K"],
                                   config["U_stream"], config["X_alphabet"],
                                   gen, cpu_gen, device)
        breakpoints[str(N)] = bp
        print(f"  N={N} M_S_breakpoint={bp}", flush=True)
    summary = {"M_S_breakpoint_per_N": breakpoints,
                "max_M_S_swept": config["M_S_grid"][-1]}
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
    out_dir = get_output_dir("wave14_lane_D_N_scaling_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("breakpoint_table_present", float(len(summary["M_S_breakpoint_per_N"])), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_N_scaling_v1")
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
