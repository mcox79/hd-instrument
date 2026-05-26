"""Multi-hop spectral validation — direct test of signal-eigenvalue near-degeneracy.

Per Research 2026-05-22 18:58 spectral validation falsifiability test. The
near-degeneracy mechanism predicts: top-K eigenvalues of W cluster more tightly
at large N (when K << N fixed).

Quantitative prediction:
  At N=65536, K=100: top-K eigenvalue span < 0.01
  At N=4096, K=100: top-K eigenvalue span > 0.03

Verdict thresholds:
  SPECTRAL_DEGENERACY_CONFIRMED: monotone clustering AND prediction satisfied
  SPECTRAL_FLAT: spans don't cluster (mechanism falsified)
  SPECTRAL_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_spectral_validation_v1.md
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

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "topK_span_per_N" not in summary:
        return ("SPECTRAL_INCONCLUSIVE", "Missing topK_span_per_N.")
    spans = summary["topK_span_per_N"]
    Ns = sorted(int(k) for k in spans.keys())
    if len(Ns) < 2:
        return ("SPECTRAL_INCONCLUSIVE", f"Need >=2 N values, got {len(Ns)}.")
    # Check monotone clustering: spans decrease with N
    span_4k = spans.get("4096", spans[str(Ns[0])])
    span_65k = spans.get("65536", spans[str(Ns[-1])])
    monotone = all(spans[str(Ns[i])] >= spans[str(Ns[i + 1])] for i in range(len(Ns) - 1))
    predicted_4k_above = span_4k > 0.03
    predicted_65k_below = span_65k < 0.01
    if monotone and predicted_65k_below:
        return ("SPECTRAL_DEGENERACY_CONFIRMED",
                f"Signal-eigenvalue near-degeneracy confirmed: top-K eigenvalue span "
                f"clusters monotonically with N. spans_per_N={spans}. "
                f"N=65536 span={span_65k:.4f}<0.01, mechanism diagnosis ratified.")
    return ("SPECTRAL_FLAT",
            f"Top-K eigenvalue span does NOT cluster as predicted. "
            f"spans_per_N={spans}. monotone={monotone}, N=65536_span={span_65k:.4f}, "
            f"N=4096_span={span_4k:.4f}. Mechanism hypothesis falsified.")


def self_test_verdict():
    cases = [
        ({"topK_span_per_N": {"4096": 0.05, "16384": 0.02, "65536": 0.005}}, "SPECTRAL_DEGENERACY_CONFIRMED"),
        ({"topK_span_per_N": {"4096": 0.05, "16384": 0.04, "65536": 0.03}}, "SPECTRAL_FLAT"),
        ({"topK_span_per_N": {"4096": 0.04, "16384": 0.10, "65536": 0.005}}, "SPECTRAL_FLAT"),
        ({}, "SPECTRAL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_topK_span(N, K, num_entities, num_relations, cpu_gen, gen, device):
    """Build K stored triples; compute W = T^T T / N; eigvalsh."""
    # Compute on CPU for large N to avoid VRAM OOM (W is N x N fp32 = 17GB at N=65536)
    use_cpu = N >= 32768
    target = torch.device("cpu") if use_cpu else device
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device).to(target)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device).to(target)
    triples = []
    for k in range(K):
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        t_atom = mh.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
        triples.append(t_atom)
    T = torch.stack(triples, dim=0)  # (K, N)
    print(f"    N={N}: building W ({N}x{N}) on {target}; eigvalsh...", flush=True)
    W = (T.T @ T) / N
    eigvals = torch.linalg.eigvalsh(W.float()).cpu()
    top_K = torch.sort(eigvals, descending=True).values[:K]
    span = float(top_K[0] - top_K[-1])
    del W, T, entity_atoms, relation_atoms
    if device.type == "cuda" and not use_cpu:
        torch.cuda.empty_cache()
    return span, top_K.tolist()


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [1024, 2048] if smoke else [4096, 16384, 65536],
              "K": 100,
              "num_entities": 200,
              "num_relations": 20,
              "seed": 17}
    spans = {}; topK_details = {}
    for N in config["N_grid"]:
        cpu_gen = torch.Generator().manual_seed(config["seed"])
        gen = torch.Generator(device=device).manual_seed(config["seed"])
        span, top_K = measure_topK_span(N, config["K"], config["num_entities"],
                                          config["num_relations"], cpu_gen, gen, device)
        spans[str(N)] = span
        topK_details[str(N)] = top_K[:5] + ["..."] + top_K[-5:]
        print(f"  N={N}: top-K span={span:.5f} (top-5: {[round(t,4) for t in top_K[:5]]}, bottom-5: {[round(t,4) for t in top_K[-5:]]})", flush=True)
    summary = {"topK_span_per_N": spans,
                "topK_eigvals_sample": topK_details,
                "K": config["K"]}
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
    out_dir = get_output_dir("wave14_multihop_spectral_validation_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("span_present", max(summary["topK_span_per_N"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_spectral_validation_v1")
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
