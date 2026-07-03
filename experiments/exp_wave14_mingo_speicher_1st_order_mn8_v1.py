"""Mingo-Speicher 1st-order moments at M/N=8: AMP-vs-VAMP comparison.

Motivation
----------
The 2nd-order Mingo-Speicher probe at M/N=8 just returned INCONCLUSIVE
(wave14_mingo_speicher_2nd_order_mn8_v1, 2026-05-24). 2nd-order moments
require K ~ 200+ independent samples to resolve fluctuations at the
1/sqrt(K) noise floor at this aspect ratio. Before scaling K up, we
should verify that the 1st-order moments (the spectral density limits
themselves) match between AMP-equivalent (iid Gauss) and VAMP-equivalent
(SRHT, Kerdock) at M/N=8. If 1st-order moments already diverge, no
amount of 2nd-order resolution will help.

Scientific question
-------------------
For codebooks {iid_gauss (AMP-equivalent), srht, kerdock (VAMP-equivalent)}
at M/N = 8, do their 1st-order spectral moments m_1, m_2, m_3, m_4 of
(1/N) A^T A match the rectangular Marchenko-Pastur prediction at c=8?

Vertices: MS_1ST_ORDER_MATCH / MS_1ST_ORDER_DIVERGE / MS_1ST_ORDER_INCONCLUSIVE.

Pre-reg: preregs/2026-05-24_wave14_mingo_speicher_1st_order_mn8_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, importlib.util, json, math, os, time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
_kp_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec = importlib.util.spec_from_file_location("kp_v1", _kp_path)
_kp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kp)
build_iid_gauss = _kp.build_iid_gauss
build_srht = _kp.build_srht
build_kerdock = _kp.build_kerdock


def rect_mp_moments(c: float, n_max: int) -> list[float]:
    """Rectangular MP moments m_p = E[lambda^p] for the eigenvalue distribution
    of (1/N) A^T A where A is M x N with iid N(0, 1/N) entries, c = M/N >= 1.

    Closed form (Narayanan-type, equivalent to Catalan numbers weighted by c):
      m_p = sum_{k=0}^{p-1} (1/(k+1)) C(p, k) C(p-1, k) c^{k+1}
    """
    moments = []
    for p in range(1, n_max + 1):
        m = 0.0
        for k in range(p):
            from math import comb
            m += (1.0 / (k + 1)) * comb(p, k) * comb(p - 1, k) * (c ** (k + 1))
        moments.append(m)
    return moments


def empirical_spectral_moments(A: np.ndarray, n_max: int) -> list[float]:
    """For A (M, N), eigenvalues lambda_i of W = (1/N) A^T A; return m_p = mean(lambda^p)."""
    M, N = A.shape
    _, s, _ = np.linalg.svd(A, full_matrices=False)
    eig = (s ** 2).astype(np.float64)  # s are singular values of A; eig = sigma^2; W eigenvalues
    return [float(np.mean(eig ** p)) for p in range(1, n_max + 1)]


def self_test() -> None:
    # MP closed-form sanity at c=1: m_1 = 1, m_2 = 1+c = 2 (for c=1)
    m = rect_mp_moments(1.0, 2)
    assert abs(m[0] - 1.0) < 1e-9, f"m_1 at c=1: {m[0]}"
    assert abs(m[1] - 2.0) < 1e-9, f"m_2 at c=1: {m[1]}"
    # At c=8: m_1 = 8, m_2 = 8 + 64 = 72
    m8 = rect_mp_moments(8.0, 2)
    assert abs(m8[0] - 8.0) < 1e-9, f"m_1 at c=8: {m8[0]}"
    assert abs(m8[1] - 72.0) < 1e-9, f"m_2 at c=8: {m8[1]}"
    print(f"  cell 1: MP closed-form moments at c=8: m1={m8[0]:.2f} m2={m8[1]:.2f}", flush=True)

    # Empirical moments on small iid Gaussian: should approach MP(c=8) at large N
    A = build_iid_gauss(N=64, M=512, seed=42)
    em = empirical_spectral_moments(A, 2)
    print(f"  cell 2: empirical iid_gauss N=64 c=8: m1={em[0]:.2f} m2={em[1]:.2f}", flush=True)
    # Loose check: within 30% (small N has 1/sqrt(N) ≈ 12.5% noise)
    assert abs(em[0] - 8.0) / 8.0 < 0.30
    assert abs(em[1] - 72.0) / 72.0 < 0.50

    # Verdict bands
    s_match = {"by_cb": {
        "iid_gauss": {"moments": [8.0, 72.0, 720.0, 7920.0], "rel_dev": [0.0, 0.0, 0.0, 0.0]},
        "kerdock":   {"moments": [8.05, 72.5, 728.0, 7950.0], "rel_dev": [0.006, 0.007, 0.011, 0.004]},
    }, "mp_reference": [8.0, 72.0, 720.0, 7920.0]}
    v, _ = compute_verdict(s_match)
    assert v == "MS_1ST_ORDER_MATCH", f"MATCH got {v}"

    s_div = {"by_cb": {
        "iid_gauss": {"moments": [8.0, 72.0, 720.0, 7920.0], "rel_dev": [0.0, 0.0, 0.0, 0.0]},
        "kerdock":   {"moments": [12.0, 100.0, 800.0, 9000.0], "rel_dev": [0.5, 0.39, 0.11, 0.14]},
    }, "mp_reference": [8.0, 72.0, 720.0, 7920.0]}
    v, _ = compute_verdict(s_div)
    assert v == "MS_1ST_ORDER_DIVERGE", f"DIV got {v}"
    print("  cell 3: verdict bands OK", flush=True)
    print("self-tests passed", flush=True)


PASS_REL_DEV = 0.05
FAIL_REL_DEV = 0.20


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_cb = summary.get("by_cb", {})
    if "kerdock" not in by_cb or "iid_gauss" not in by_cb:
        return ("MS_1ST_ORDER_INCONCLUSIVE", "Need iid_gauss + kerdock cells.")
    ker_dev = by_cb["kerdock"]["rel_dev"]
    iid_dev = by_cb["iid_gauss"]["rel_dev"]
    iid_max = max(iid_dev)
    ker_max = max(ker_dev)

    msg = f"iid_gauss max_rel_dev={iid_max:.4f}; kerdock max_rel_dev={ker_max:.4f}"

    # Control must pass first
    if iid_max > PASS_REL_DEV * 2:
        return ("MS_1ST_ORDER_INCONCLUSIVE",
                f"iid_gauss control too noisy (max_dev={iid_max:.4f} > {PASS_REL_DEV * 2}); "
                f"need larger N or more seeds. {msg}.")
    if ker_max < PASS_REL_DEV:
        return ("MS_1ST_ORDER_MATCH",
                f"Kerdock 1st-order moments match rect-MP(c=8) within {PASS_REL_DEV}. "
                f"{msg}. AMP and VAMP are 1st-order equivalent at this aspect ratio.")
    if ker_max > FAIL_REL_DEV:
        return ("MS_1ST_ORDER_DIVERGE",
                f"Kerdock 1st-order moments diverge from rect-MP(c=8) by {ker_max:.4f} > {FAIL_REL_DEV}. "
                f"{msg}. AMP and VAMP are NOT 1st-order equivalent.")
    return ("MS_1ST_ORDER_INCONCLUSIVE",
            f"Middle band ({PASS_REL_DEV} < ker_max={ker_max:.4f} < {FAIL_REL_DEV}). {msg}.")


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    if smoke:
        cfg = {"N": 64, "ratio": 8, "n_seeds": 3, "codebooks": ["iid_gauss"],
                "n_moments": 4, "mode": "smoke"}
    else:
        cfg = {"N": 512, "ratio": 8, "n_seeds": 20, "codebooks": ["iid_gauss", "srht", "kerdock"],
                "n_moments": 4, "mode": "full"}

    mp_ref = rect_mp_moments(float(cfg["ratio"]), cfg["n_moments"])
    print(f"Config: N={cfg['N']} M={cfg['ratio']*cfg['N']} c={cfg['ratio']} seeds={cfg['n_seeds']}", flush=True)
    print(f"MP reference moments (c={cfg['ratio']}): {[f'{m:.2f}' for m in mp_ref]}", flush=True)

    builders = {"iid_gauss": build_iid_gauss, "srht": build_srht, "kerdock": build_kerdock}
    by_cb = {}
    for cb_name in cfg["codebooks"]:
        build_fn = builders[cb_name]
        all_moments = []
        for seed in range(cfg["n_seeds"]):
            try:
                A = build_fn(cfg["N"], cfg["ratio"] * cfg["N"], seed=seed)
                m = empirical_spectral_moments(A, cfg["n_moments"])
                all_moments.append(m)
            except Exception as e:
                print(f"  [{cb_name}, seed={seed}] ERROR: {e}", flush=True)
        if not all_moments:
            print(f"  [{cb_name}] no successful samples", flush=True)
            continue
        all_moments = np.array(all_moments)  # (n_seeds, n_moments)
        mean_m = list(all_moments.mean(axis=0))
        rel_dev = [abs(mean_m[i] - mp_ref[i]) / abs(mp_ref[i]) for i in range(cfg["n_moments"])]
        by_cb[cb_name] = {"moments": mean_m, "rel_dev": rel_dev, "n_seeds": len(all_moments)}
        print(f"  [{cb_name}] moments={[f'{x:.3f}' for x in mean_m]} rel_dev={[f'{x:.4f}' for x in rel_dev]}", flush=True)

    summary = {"by_cb": by_cb, "mp_reference": mp_ref, "config": cfg}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    self_test()
    out_dir = get_output_dir("wave14_mingo_speicher_1st_order_mn8_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test()
    out_dir = get_output_dir("wave14_mingo_speicher_1st_order_mn8_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
