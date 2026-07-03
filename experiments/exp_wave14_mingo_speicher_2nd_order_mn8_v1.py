"""Mingo-Speicher 2nd-order freeness moment of P(h) at M/N=8 — anchor A.

Motivation
----------
The substrate's 4-coset Kerdock codebook produced anomalous spectral behavior
at the rectangular M/N=8 regime in prior cycles. Standard free probability
(1st-order) only constrains the LIMIT density (the moments m_n = E[lambda^n]
on the limit). Mingo & Speicher (J. Funct. Anal. 235, 2006: "Second order
freeness and fluctuations of random matrices") show that the FLUCTUATIONS of
moments around their limit -- specifically the CENTERED 2nd-moment

  alpha_pq = lim_{N -> infty} N * Cov( tr(W^p) / N, tr(W^q) / N )

(the entries of the "second-order moment array") -- satisfy their own
universality with structure given by NON-CROSSING ANNULAR partitions and
"second-order free cumulants" kappa_{p,q}.

For iid Gaussian / Wishart matrices and the canonical rectangular MP limit
at general aspect ratio c=M/N, the predicted second-order moments alpha_pq
are known (Mingo-Speicher 2006 Theorem 1.4; Capitaine-Donati-Martin 2007 for
the rectangular Wishart case). Departures of empirical alpha_pq from rect-MP
prediction are 2nd-order substrate signatures invisible to 1st-order
(spectral moment) probes.

Scientific question
-------------------
Does the substrate Kerdock codebook produce SECOND-ORDER moment fluctuations
alpha_pq that match the rectangular Wishart prediction at c=M/N=8, or does
the substrate have a 2nd-order departure that is invisible to standard
spectral KS tests?

Approach
--------
For each codebook in {iid_gauss, kerdock} and each (p, q) in {(2,2), (2,3),
(3,3)}, estimate alpha_pq from K independent matrix samples:

  alpha_pq_hat = K * Cov( tr(W^p) / N, tr(W^q) / N )

where W = (1/N) A^T A (so tr(W^p) = sum lambda^p). Compare to rect-MP
analytical prediction.

For iid-Gaussian rectangular Wishart at c=M/N>=1, the 2nd-order moments
can be computed from non-crossing annular partitions of (p+q) elements
on a two-circle annulus, weighted by c. Closed forms for low (p,q) are
known: e.g. alpha_22 = c^2 (2 c + 2) for the limit (rectangular Wishart
fluctuation).

The control is iid-Gaussian: it should match the rect-MP 2nd-order
prediction. The substrate test is Kerdock: it gets the same 2nd-order
analysis; departure from prediction = 2nd-order substrate signature.

Vertices: MS_2ND_ORDER_MATCH / MS_2ND_ORDER_DIVERGE / INCONCLUSIVE.

Pre-reg: preregs/2026-05-24_wave14_mingo_speicher_2nd_order_mn8_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse codebook builders from kappa_profile_cross_codebook
_kp_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec = importlib.util.spec_from_file_location("kp_v1", _kp_path)
_kp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kp)
build_iid_gauss = _kp.build_iid_gauss
build_srht = _kp.build_srht
build_hadamard = _kp.build_hadamard
build_kerdock = _kp.build_kerdock


# ---------------------------------------------------------------------------
# Empirical 2nd-order moment estimation
# ---------------------------------------------------------------------------

def spectral_power_traces(eig: np.ndarray, p_list: list[int]) -> dict:
    """For an eigenvalue array eig (size = min(M, N) of (1/N) A^T A), return
    {p: sum(eig**p) / N_dim}. We use the NORMALIZED form
        tau_p = tr(W^p) / N
    where N is the side-length of W = (1/N) A^T A (here = min(M, N)).
    Equivalently sum_i lambda_i^p / N_dim.
    """
    out = {}
    N_dim = len(eig)
    for p in p_list:
        out[p] = float(np.sum(eig ** p) / max(N_dim, 1))
    return out


def estimate_alpha_pq(samples: list[dict], p: int, q: int) -> float:
    """Estimate alpha_pq = N * Cov( tr(W^p) / N, tr(W^q) / N ) from K samples
    of {p: tau_p, q: tau_q} dicts.

    Reference: Mingo-Speicher 2006 def (1.3); the Cov is the empirical
    covariance over independent matrix samples and the leading N scaling
    is part of the second-order universality framework.

    Note: we report alpha_pq normalized by the SAMPLE N_dim, so the result
    is a finite-N estimator of the limit alpha_pq.
    """
    if len(samples) < 2:
        return float("nan")
    tau_p = np.array([s[p] for s in samples])
    tau_q = np.array([s[q] for s in samples])
    # N-scaled covariance; we use the sample-N (the N_dim) embedded in tau
    # Already tau_p = tr(W^p)/N, so cov is at scale 1/N^2; multiply by N to
    # get alpha = N * cov(tau_p, tau_q).
    # We need access to N_dim; we infer from samples[0]['__N__'] if present.
    N_dim = samples[0].get("__N__", 1)
    cov = float(np.mean((tau_p - tau_p.mean()) * (tau_q - tau_q.mean())))
    # multiply by (K / (K-1)) for unbiased; ignore since K small
    return float(N_dim * cov)


# ---------------------------------------------------------------------------
# Reference: rect-MP 2nd-order moment estimates from iid-Gaussian (Monte Carlo)
# ---------------------------------------------------------------------------
#
# Rather than derive closed-form alpha_pq for rect-MP(c=8), we use iid_gauss as
# the empirical reference (it IS the rect-MP limit by definition). Substrate
# departure = substrate alpha_pq significantly differs from iid_gauss alpha_pq.


def relative_diff(x: float, ref: float) -> float:
    if not np.isfinite(x) or not np.isfinite(ref) or abs(ref) < 1e-12:
        return float("nan")
    return float(abs(x - ref) / abs(ref))


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

PASS_REL_DIFF = 0.20   # within 20% of iid-Gauss reference
FAIL_REL_DIFF = 0.50   # outside 50%


def compute_verdict(summary: dict) -> tuple[str, str]:
    # by_cb_pq: {codebook: {(p,q): alpha_pq}}
    by_cb_pq = summary.get("by_cb_pq", {})
    if not by_cb_pq:
        return ("MS_2ND_ORDER_INCONCLUSIVE", "No cells.")

    iid = by_cb_pq.get("iid_gauss", {})
    ker = by_cb_pq.get("kerdock", {})
    if not iid or not ker:
        return ("MS_2ND_ORDER_INCONCLUSIVE",
                "Need both iid_gauss and kerdock results.")

    # For each (p,q), check rel_diff
    devs = []
    for pq, alpha_iid in iid.items():
        if pq not in ker:
            continue
        alpha_ker = ker[pq]
        d = relative_diff(alpha_ker, alpha_iid)
        if np.isfinite(d):
            devs.append((pq, d, alpha_iid, alpha_ker))

    if not devs:
        return ("MS_2ND_ORDER_INCONCLUSIVE", "No (p,q) overlap.")

    max_dev = max(d[1] for d in devs)
    msg_devs = ", ".join(
        f"alpha_{p}{q}: iid={ai:.3f}, ker={ak:.3f}, rel_dev={d:.3f}"
        for (p, q), d, ai, ak in devs
    )

    if max_dev > FAIL_REL_DIFF:
        return (
            "MS_2ND_ORDER_DIVERGE",
            f"Kerdock 2nd-order moments DIVERGE from iid-Gauss reference. "
            f"max_rel_dev={max_dev:.3f} (> {FAIL_REL_DIFF}). {msg_devs}. "
            f"Substrate carries 2nd-order (fluctuation-level) signature "
            f"beyond rect-MP universality.",
        )
    if max_dev < PASS_REL_DIFF:
        return (
            "MS_2ND_ORDER_MATCH",
            f"Kerdock 2nd-order moments MATCH iid-Gauss reference. "
            f"max_rel_dev={max_dev:.3f} (< {PASS_REL_DIFF}). {msg_devs}. "
            f"Substrate is 2nd-order-free indistinguishable from iid Gaussian "
            f"at rectangular c=M/N=8.",
        )
    return (
        "MS_2ND_ORDER_INCONCLUSIVE",
        f"max_rel_dev={max_dev:.3f} in [{PASS_REL_DIFF}, {FAIL_REL_DIFF}]. "
        f"{msg_devs}",
    )


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    rng = np.random.default_rng(123)

    # 1. spectral_power_traces matches direct moment computation
    eig = np.array([1.0, 2.0, 3.0])
    pt = spectral_power_traces(eig, [1, 2, 3])
    assert abs(pt[1] - (1 + 2 + 3) / 3) < 1e-12
    assert abs(pt[2] - (1 + 4 + 9) / 3) < 1e-12
    assert abs(pt[3] - (1 + 8 + 27) / 3) < 1e-12
    print(f"  cell 1: spectral_power_traces OK", flush=True)

    # 2. estimate_alpha_pq on perfectly-correlated samples gives N_dim * var
    samples = [
        {2: 1.0, 3: 2.0, "__N__": 100},
        {2: 2.0, 3: 4.0, "__N__": 100},
        {2: 3.0, 3: 6.0, "__N__": 100},
    ]
    a22 = estimate_alpha_pq(samples, 2, 2)
    # var of (1,2,3) = 2/3; N_dim * var = 100 * 2/3 ≈ 66.67
    expected = 100.0 * (2.0 / 3.0)
    assert abs(a22 - expected) < 1e-6, f"a22={a22} expected {expected}"
    print(f"  cell 2: alpha_22 estimator OK ({a22:.2f})", flush=True)

    # 3. iid_gauss at c=8: spectral_power_traces returns finite values
    A = build_iid_gauss(64, 512, 42)
    _, s, _ = np.linalg.svd(A, full_matrices=False)
    eig = (s ** 2).astype(np.float64)
    pt = spectral_power_traces(eig, [2, 3])
    assert np.isfinite(pt[2]) and np.isfinite(pt[3]) and pt[2] > 0
    print(f"  cell 3: iid_gauss N=64 c=8 tau_2={pt[2]:.3f}, tau_3={pt[3]:.3f}", flush=True)

    # 4. Verdict bands
    fake_match = {"by_cb_pq": {
        "iid_gauss": {(2,2): 100.0, (2,3): 200.0},
        "kerdock":   {(2,2): 110.0, (2,3): 215.0},
    }}
    v, _ = compute_verdict(fake_match)
    assert v == "MS_2ND_ORDER_MATCH", f"MATCH -> {v}"

    fake_div = {"by_cb_pq": {
        "iid_gauss": {(2,2): 100.0, (2,3): 200.0},
        "kerdock":   {(2,2): 200.0, (2,3): 220.0},
    }}
    v, _ = compute_verdict(fake_div)
    assert v == "MS_2ND_ORDER_DIVERGE", f"DIV -> {v}"

    fake_mid = {"by_cb_pq": {
        "iid_gauss": {(2,2): 100.0, (2,3): 200.0},
        "kerdock":   {(2,2): 130.0, (2,3): 260.0},
    }}
    v, _ = compute_verdict(fake_mid)
    assert v == "MS_2ND_ORDER_INCONCLUSIVE", f"MID -> {v}"

    fake_missing = {"by_cb_pq": {"iid_gauss": {(2,2): 100.0}}}
    v, _ = compute_verdict(fake_missing)
    assert v == "MS_2ND_ORDER_INCONCLUSIVE", f"MISSING -> {v}"

    print(f"self-tests passed (4 cells)", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CODEBOOK_BUILDERS = {
    "iid_gauss": build_iid_gauss,
    "srht": build_srht,
    "hadamard": build_hadamard,
    "kerdock": build_kerdock,
}


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "ratio": 8,
            "K_samples": 5,
            "codebooks": ["iid_gauss"],  # kerdock skipped at small N
            "pq_list": [(2,2), (2,3), (3,3)],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "ratio": 8,
            "K_samples": 40,
            "codebooks": ["iid_gauss", "srht", "hadamard", "kerdock"],
            "pq_list": [(2,2), (2,3), (3,3)],
        }

    N = config["N"]
    M = config["ratio"] * N
    K = config["K_samples"]
    p_values = sorted(set([p for (p, q) in config["pq_list"]] + [q for (p, q) in config["pq_list"]]))

    by_cb_samples: dict[str, list[dict]] = {}
    by_cb_pq: dict[str, dict[tuple, float]] = {}
    for cb_name in config["codebooks"]:
        build_fn = CODEBOOK_BUILDERS[cb_name]
        samples = []
        for k in range(K):
            try:
                A = build_fn(N, M, seed=k * 7 + 11)
                _, s, _ = np.linalg.svd(A, full_matrices=False)
                eig = (s ** 2).astype(np.float64)
                taus = spectral_power_traces(eig, p_values)
                taus["__N__"] = len(eig)
                samples.append(taus)
                if k < 3 or k == K - 1:
                    print(
                        f"[N={N} cb={cb_name} k={k}] tau_2={taus[2]:.3f} "
                        f"tau_3={taus[3]:.3f}", flush=True,
                    )
            except Exception as e:
                print(f"  ERROR N={N} cb={cb_name} k={k}: {e}", flush=True)
        by_cb_samples[cb_name] = samples
        # estimate alpha_pq
        pq_map = {}
        for (p, q) in config["pq_list"]:
            alpha = estimate_alpha_pq(samples, p, q)
            pq_map[(p, q)] = alpha
            print(f"  [{cb_name}] alpha_{p}{q} = {alpha:.4f}", flush=True)
        by_cb_pq[cb_name] = pq_map

    # JSON-friendly format: stringify (p,q) keys
    by_cb_pq_json = {
        cb: {f"{p},{q}": v for (p, q), v in pq_map.items()}
        for cb, pq_map in by_cb_pq.items()
    }

    summary = {
        "by_cb_pq": by_cb_pq,
        "by_cb_pq_json": by_cb_pq_json,
        "by_cb_K": {cb: len(s) for cb, s in by_cb_samples.items()},
        "config": config,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    # by_cb_pq has tuple keys -> not JSON serializable. Drop the tuple-keyed
    # form; keep the JSON-friendly one.
    summary_out = dict(summary)
    summary_out.pop("by_cb_pq", None)
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary_out,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mingo_speicher_2nd_order_mn8_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_mingo_speicher_2nd_order_mn8_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
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
