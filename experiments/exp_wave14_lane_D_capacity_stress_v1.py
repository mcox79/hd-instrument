"""Lane D capacity stress — find where COMPOSE breaks.

Lane D COMPOSE shipped at S=0.98 T=0.98 U=1.00 X=1.00 with M_S=50 facts,
K=3 hypotheses, U_stream=40 facts, X_alphabet=5. This pushes each primitive's
load and finds the joint capacity envelope on a shared substrate.

Sweep:
  - M_S in {50, 150, 300} (Bet S fact-count)
  - K in {3, 10, 25} (Bet T hypothesis count)
  - U_stream in {40, 200, 1000} (Bet U memory horizon)
  - X_alphabet in {5, 20, 50} (Bet X skill alphabet)

Hold all-but-one fixed, sweep one axis at a time. Record the breakpoint per
axis (where ANY primitive drops below 0.70).

Verdict thresholds:
  CAPACITY_HEALTHY: all 4 axes scale to their max value without breaking
  CAPACITY_BOUNDED: at least one primitive hits a breakpoint within the sweep
  CAPACITY_FRAGILE: COMPOSE fails at baseline params (regression)

Pre-reg: preregs/2026-05-22_wave14_lane_D_capacity_stress_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "breakpoints" not in summary:
        return ("LANE_D_CAPACITY_INCONCLUSIVE", "Missing breakpoints.")
    bp = summary["breakpoints"]
    baseline = summary.get("baseline_pass", False)
    if not baseline:
        return ("LANE_D_CAPACITY_FRAGILE",
                f"Baseline COMPOSE fails at default params (regression). "
                f"baseline_metrics={summary.get('baseline_metrics')}.")
    # Check if any axis was bounded
    n_bounded = sum(1 for axis, v in bp.items() if v is not None)
    if n_bounded == 0:
        return ("LANE_D_CAPACITY_HEALTHY",
                f"All 4 axes scale to max sweep value without breaking. breakpoints={bp}.")
    return ("LANE_D_CAPACITY_BOUNDED",
            f"{n_bounded} of 4 axes hit breakpoints in sweep. breakpoints={bp}. "
            f"Substrate has measurable joint capacity envelope.")


def self_test_verdict():
    cases = [
        ({"breakpoints": {"M_S": None, "K": None, "U_stream": None, "X_alphabet": None}, "baseline_pass": True}, "LANE_D_CAPACITY_HEALTHY"),
        ({"breakpoints": {"M_S": 300, "K": None, "U_stream": 1000, "X_alphabet": None}, "baseline_pass": True}, "LANE_D_CAPACITY_BOUNDED"),
        ({"breakpoints": {}, "baseline_pass": False, "baseline_metrics": {"S": 0.3}}, "LANE_D_CAPACITY_FRAGILE"),
        ({}, "LANE_D_CAPACITY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_codebooks(N, gen, device, K, X_alphabet, skill_len=8):
    return {
        "entity": t.make_bsc_codebook(500, N, gen, device),
        "relation": t.make_bsc_codebook(50, N, gen, device),
        "hyp": t.make_bsc_codebook(K, N, gen, device),
        "position": t.make_bsc_codebook(skill_len, N, gen, device),
        "skill": t.make_bsc_codebook(X_alphabet, N, gen, device),
    }


def measure_S(M_S, N, cbs, cpu_gen, device):
    facts = [(int(torch.randint(0, 500, (1,), generator=cpu_gen)),
              int(torch.randint(0, 50, (1,), generator=cpu_gen)),
              int(torch.randint(0, 500, (1,), generator=cpu_gen))) for _ in range(M_S)]
    M = t.sign_quantize(torch.stack([t.sign_quantize(cbs["entity"][s] * cbs["relation"][r] * cbs["entity"][o])
                                       for s, r, o in facts], dim=0).sum(dim=0))
    correct = 0; n = min(30, M_S)
    for s, r, o in facts[:n]:
        probe = M * cbs["entity"][s] * cbs["relation"][r]
        if int((cbs["entity"] @ probe).argmax()) == o: correct += 1
    return correct / n


def measure_T(K, F, N, cbs, cpu_gen, device):
    hyp_facts = [[(int(torch.randint(0, 500, (1,), generator=cpu_gen)),
                    int(torch.randint(0, 50, (1,), generator=cpu_gen)),
                    int(torch.randint(0, 500, (1,), generator=cpu_gen))) for _ in range(F)]
                  for _ in range(K)]
    M = t.sign_quantize(torch.stack([
        cbs["hyp"][k] * t.sign_quantize(torch.stack([
            t.sign_quantize(cbs["entity"][s] * cbs["relation"][r] * cbs["entity"][o])
            for s, r, o in facts], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_facts)], dim=0).sum(dim=0))
    correct = 0; total = 0
    n_per_k = min(10, F)
    for k, facts in enumerate(hyp_facts):
        for s, r, o in facts[:n_per_k]:
            probe = M * cbs["hyp"][k] * cbs["entity"][s] * cbs["relation"][r]
            if int((cbs["entity"] @ probe).argmax()) == o: correct += 1
            total += 1
    return correct / max(total, 1)


def measure_U(U_stream, N, cbs, cpu_gen, device):
    facts = [(int(torch.randint(0, 500, (1,), generator=cpu_gen)),
              int(torch.randint(0, 50, (1,), generator=cpu_gen)),
              int(torch.randint(0, 500, (1,), generator=cpu_gen))) for _ in range(U_stream)]
    B = torch.zeros(N, device=device); decay = 0.95
    for s, r, o in facts:
        B = decay * B + (cbs["entity"][s] * cbs["relation"][r] * cbs["entity"][o]).float()
    B_q = t.sign_quantize(B)
    correct = 0; n = min(5, U_stream)
    for s, r, o in facts[-n:]:
        probe = B_q * cbs["entity"][s] * cbs["relation"][r]
        if int((cbs["entity"] @ probe).argmax()) == o: correct += 1
    return correct / n


def measure_X(X_alphabet, N, cbs, cpu_gen, device, skill_len=8):
    correct = 0; total = 0
    for _ in range(10):
        idx = torch.randint(0, X_alphabet, (skill_len // 2,), generator=cpu_gen).to(device)
        prog = t.sign_quantize((cbs["skill"][idx] * cbs["position"][:skill_len // 2]).sum(dim=0))
        for i in range(skill_len // 2):
            probe = prog * cbs["position"][i]
            if int((cbs["skill"] @ probe).argmax()) == int(idx[i]): correct += 1
            total += 1
    return correct / total


def run_one_axis_sweep(axis_name, axis_values, fixed, N, gen, cpu_gen, device):
    """Sweep one axis; return list of (value, S, T, U, X) and breakpoint."""
    rows = []
    for v in axis_values:
        params = dict(fixed)
        params[axis_name] = v
        cbs = make_codebooks(N, gen, device, params["K"], params["X_alphabet"])
        s_acc = measure_S(params["M_S"], N, cbs, cpu_gen, device)
        t_acc = measure_T(params["K"], 10, N, cbs, cpu_gen, device)
        u_acc = measure_U(params["U_stream"], N, cbs, cpu_gen, device)
        x_acc = measure_X(params["X_alphabet"], N, cbs, cpu_gen, device)
        rows.append({"value": v, "S": s_acc, "T": t_acc, "U": u_acc, "X": x_acc})
        print(f"    {axis_name}={v}: S={s_acc:.3f} T={t_acc:.3f} U={u_acc:.3f} X={x_acc:.3f}", flush=True)
    # Breakpoint = first value where ANY metric < 0.70
    breakpoint = None
    for r in rows:
        if min(r["S"], r["T"], r["U"], r["X"]) < 0.70:
            breakpoint = r["value"]
            break
    return rows, breakpoint


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "fixed_baseline": {"M_S": 50, "K": 3, "U_stream": 40, "X_alphabet": 5},
              "sweeps": {
                  "M_S": [50, 150, 300] if not smoke else [50, 150],
                  "K": [3, 10, 25] if not smoke else [3, 10],
                  "U_stream": [40, 200, 1000] if not smoke else [40, 200],
                  "X_alphabet": [5, 20, 50] if not smoke else [5, 20]},
              "seed": 17}
    N = config["N"]
    gen = torch.Generator(device=device).manual_seed(config["seed"])
    cpu_gen = torch.Generator().manual_seed(config["seed"] + 1009)

    # Baseline check first
    cbs = make_codebooks(N, gen, device, config["fixed_baseline"]["K"], config["fixed_baseline"]["X_alphabet"])
    base = {"S": measure_S(config["fixed_baseline"]["M_S"], N, cbs, cpu_gen, device),
            "T": measure_T(config["fixed_baseline"]["K"], 10, N, cbs, cpu_gen, device),
            "U": measure_U(config["fixed_baseline"]["U_stream"], N, cbs, cpu_gen, device),
            "X": measure_X(config["fixed_baseline"]["X_alphabet"], N, cbs, cpu_gen, device)}
    print(f"  baseline: S={base['S']:.3f} T={base['T']:.3f} U={base['U']:.3f} X={base['X']:.3f}", flush=True)
    baseline_pass = all(v >= 0.70 for v in base.values())

    sweeps_data = {}
    breakpoints = {}
    if baseline_pass:
        for axis in ["M_S", "K", "U_stream", "X_alphabet"]:
            print(f"  sweep {axis}:", flush=True)
            rows, bp = run_one_axis_sweep(axis, config["sweeps"][axis], config["fixed_baseline"],
                                            N, gen, cpu_gen, device)
            sweeps_data[axis] = rows
            breakpoints[axis] = bp

    summary = {"baseline_pass": baseline_pass, "baseline_metrics": base,
                "sweeps": sweeps_data, "breakpoints": breakpoints}
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
    out_dir = get_output_dir("wave14_lane_D_capacity_stress_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("baseline_any", max(summary["baseline_metrics"].values()), 0.30)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_capacity_stress_v1")
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
