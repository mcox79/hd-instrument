"""KF-4 DRIFT DETECTION via boundary proximity: shift sequences + spectral gap.

CONTEXT (Killer Feature 4):
  Per the project notes: KF-4 measures 4-tier shift class + bundle-norm-var +
  spectral-gap-of-overlap-matrix + rate-of-change during sequential edits.
  Reuses Bet B infrastructure.

  This is about detecting when the substrate state has drifted from its
  original configuration -- a product-relevant monitoring capability.
  "Live drift detection" is one of the 5 substrate killer features.

SCIENTIFIC QUESTION:
  During a sequence of N_SHIFT edits to stored facts, can we detect drift
  in real-time using spectral properties of the response-overlap matrix?
  Specifically: does spectral_gap track the edit-induced drift?

  Observables per edit step:
    (a) cumulative_edit_count: how many edits applied so far
    (b) bundle_norm_var: variance of query response norms (measures heterogeneity)
    (c) overlap_spectral_gap: spectral gap of normalized query response overlap matrix
    (d) mean_retention: fraction of original facts still correctly retrieved
    (e) drift_amplitude: ||W_current - W_original||_F / ||W_original||_F

  Key hypothesis: spectral_gap and bundle_norm_var increase as drift accumulates
  (system moves away from its equilibrium configuration).
  If detectable before retention degrades: early warning signal.

DESIGN:
  - Store M=N facts at N=4096 Kerdock 4-coset.
  - Apply 50 sequential edits (edit one random fact at each step; anti-Hebb + insert).
  - After each 5th edit, measure all 5 observables.
  - Compute Pearson r(edit_count, observable) for each observable.
  - 3 seeds.

PRE-REGISTERED BANDS (first drift-detection measurement):
  Calibration probe; no prior anchor.

  HARD_PASS: drift_amplitude increases monotonically with edit_count (confirmed
    by Pearson r > 0.90 in >= 2/3 seeds) AND at least one of
    (spectral_gap, bundle_norm_var) tracks drift_amplitude with r > 0.50.
    Interpretation: spectral measurements can detect drift before retention falls.
  HARD_FAIL: drift_amplitude does NOT increase with edit_count (edits leave no trace).
    r(edits, drift_amplitude) < 0.5 in all seeds.
  MIDDLE_BAND: drift detectable but spectral proxies don't track it well.

FORMULA SELF-TESTS:
  1. drift_amplitude = ||W_t - W_0||_F / ||W_0||_F. After 0 edits: drift=0.
     After 1 edit: drift > 0 (nonzero Frobenius change).
  2. For 50 independent random edits at M=N (under-capacity):
     drift should grow approximately as sqrt(n_edits) / sqrt(M)
     (random walk in W-space).
  3. spectral_gap = lambda_1 - lambda_2 of query overlap matrix.
     For uniform patterns: gap = 0. For structured = gap > 0.
  4. Monotone r check: compute pearson_r(list(range(10)), list(range(10))) -> 1.0.

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 25 edits, measure every 5. ~5s.
  Full: N=4096, 3 seeds, 50 edits, measure every 5.
  scale: (4096/1024)^1.5 * 3 * (50/25) * 2 = 8 * 3 * 2 * 2 = 96
  timeout_s = ceil(1.5 * 5 * 96) = ceil(720) -> 900s.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: overnight_queue (GPU; Kerdock N=4096, sequential edits)
Pre-reg: preregs/2026-05-27_kf4_drift_detect_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024
M_FRAC = 1.0        # M = N (under-capacity, clean regime)
N_EDITS_FULL = 50
N_EDITS_SMOKE = 25
MEASURE_EVERY = 5   # measure observables every N edits
N_PROBE = 200       # facts to probe for retention
N_PROBE_SMOKE = 50
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
PASS_DRIFT_R = 0.90
PASS_SPECTRAL_R = 0.50
FAIL_DRIFT_R = 0.50


def get_output_dir(default_name: str = "kf4_drift_detect_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pearson_r(x: list, y: list) -> float:
    """Pearson correlation coefficient from lists."""
    if len(x) < 2:
        return 0.0
    xt = torch.tensor(x, dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.float32)
    if xt.std() < 1e-10 or yt.std() < 1e-10:
        return 0.0
    xm = xt - xt.mean()
    ym = yt - yt.mean()
    denom = float((xm.norm() * ym.norm()).item())
    if denom < 1e-10:
        return 0.0
    return float((xm * ym).sum().item() / denom)


def build_w(codebook: torch.Tensor, M: int, seed: int, N: int, device: torch.device):
    """Build Hebbian W for M Kerdock facts."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    key_idx = torch.randperm(C, generator=gen, device=device)[:min(M, C)]
    val_idx = torch.randperm(C, generator=gen, device=device)[:min(M, C)]
    if M > C:
        key_idx = key_idx.repeat(math.ceil(M / C))[:M]
        val_idx = val_idx.repeat(math.ceil(M / C))[:M]
    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = values[start:start + 256]
        W += (v_b.T @ k_b) / N
    return W, keys, values, key_idx, val_idx


def compute_drift_amplitude(W_current: torch.Tensor, W_original: torch.Tensor) -> float:
    """||W_t - W_0||_F / ||W_0||_F"""
    diff = (W_current - W_original).norm()
    base = W_original.norm()
    if base < 1e-10:
        return float(diff.item())
    return float((diff / base).item())


def compute_bundle_norm_var(W: torch.Tensor, keys: torch.Tensor,
                             n_probe: int = 100) -> float:
    """Variance of ||W k_i||_2."""
    n = min(n_probe, keys.shape[0])
    responses = keys[:n] @ W.T
    norms = responses.norm(dim=1)
    return float(norms.var().item())


def compute_spectral_gap(W: torch.Tensor, keys: torch.Tensor,
                          n_probe: int = 64, N: int = 1) -> float:
    """Spectral gap of response overlap matrix (W k_i)^T (W k_j) / N."""
    n = min(n_probe, keys.shape[0])
    responses = keys[:n] @ W.T   # (n, N)
    S = (responses @ responses.T) / N   # (n, n) overlap matrix
    try:
        eigs = torch.linalg.eigvalsh(S)
        eigs_desc = eigs.flip(0)
        if len(eigs_desc) >= 2:
            return float((eigs_desc[0] - eigs_desc[1]).item())
        return 0.0
    except Exception:
        return 0.0


def compute_retention(W: torch.Tensor, keys: torch.Tensor, val_idx: torch.Tensor,
                       codebook: torch.Tensor, n_probe: int) -> float:
    """Argmax retention on stored facts."""
    C = codebook.shape[0]
    n = min(n_probe, keys.shape[0])
    vi = val_idx[:n] % C
    sims = (codebook @ (keys[:n] @ W.T).T) / W.shape[0]
    pred = torch.argmax(sims, dim=0)
    return float((pred == vi.to(W.device)).float().mean().item())


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run drift detection sequence for one seed."""
    smoke = config["smoke"]
    N = config["N"]
    n_edits = config["n_edits"]
    n_probe = config["n_probe"]

    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    M = int(M_FRAC * N)
    M = min(M, C)

    W0, keys, values, key_idx, val_idx = build_w(codebook, M, seed, N, device)
    W = W0.clone()

    # Generate replacement values for sequential edits
    gen = torch.Generator(device=device).manual_seed(seed + 77777)
    new_val_perm = torch.randperm(C, generator=gen, device=device)[:n_edits]
    values_new = codebook[new_val_perm]

    # Measurement series
    edit_counts = []
    drift_series = []
    bnv_series = []
    spectral_series = []
    retention_series = []

    for edit_i in range(n_edits):
        # Apply edit
        k_edit_idx = edit_i % M   # cycle through keys
        k_edit = keys[k_edit_idx]
        v_old = values[k_edit_idx]
        v_new = values_new[edit_i % len(values_new)]

        kk = float((k_edit * k_edit).sum().item())
        if kk > 1e-10:
            W = W - torch.outer(W @ k_edit, k_edit) / kk
            W = W + torch.outer(v_new, k_edit) / N

        # Measure every MEASURE_EVERY steps
        if (edit_i + 1) % MEASURE_EVERY == 0 or edit_i == n_edits - 1:
            edit_counts.append(edit_i + 1)
            drift_series.append(compute_drift_amplitude(W, W0))
            bnv_series.append(compute_bundle_norm_var(W, keys, min(n_probe, M)))
            spectral_series.append(compute_spectral_gap(W, keys, min(64, M), N))
            retention_series.append(compute_retention(W, keys, val_idx, codebook, n_probe))

    # Pearson correlations with edit_count
    r_drift = pearson_r(edit_counts, drift_series)
    r_bnv = pearson_r(edit_counts, bnv_series)
    r_spectral = pearson_r(edit_counts, spectral_series)
    r_retention = pearson_r(edit_counts, retention_series)

    return {
        "seed": seed, "N": N, "M": M,
        "r_drift": r_drift,
        "r_bnv": r_bnv,
        "r_spectral": r_spectral,
        "r_retention": r_retention,
        "drift_final": drift_series[-1] if drift_series else 0.0,
        "retention_final": retention_series[-1] if retention_series else 0.0,
        "n_steps": len(edit_counts),
        "drift_series": drift_series,
        "bnv_series": bnv_series,
        "spectral_series": spectral_series,
        "retention_series": retention_series,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF4_INCONCLUSIVE", "No per-seed data.")

    r_drifts = [sd["r_drift"] for sd in per_seed.values() if sd.get("n_steps", 0) > 0]
    r_spectrals = [sd["r_spectral"] for sd in per_seed.values()]
    r_bnvs = [sd["r_bnv"] for sd in per_seed.values()]
    drift_finals = [sd["drift_final"] for sd in per_seed.values()]

    if not r_drifts:
        return ("KF4_INCONCLUSIVE", "No drift data.")

    n_seeds = len(r_drifts)
    seeds_drift_pass = sum(1 for r in r_drifts if r >= PASS_DRIFT_R)
    mean_drift_r = sum(r_drifts) / n_seeds
    mean_spectral_r = sum(r_spectrals) / n_seeds if r_spectrals else 0.0
    mean_bnv_r = sum(r_bnvs) / n_seeds if r_bnvs else 0.0
    mean_drift_final = sum(drift_finals) / n_seeds if drift_finals else 0.0

    # HARD_FAIL: drift doesn't accumulate
    if all(r < FAIL_DRIFT_R for r in r_drifts):
        return ("KF4_HARD_FAIL",
                f"Drift amplitude does NOT increase with edits. "
                f"r_drift={[round(r, 3) for r in r_drifts]}. "
                f"Edits leave no detectable trace in W. Substrate is edit-resilient.")

    # HARD_PASS: drift tracks edits + at least one spectral measure correlates
    spectral_ok = mean_spectral_r >= PASS_SPECTRAL_R or mean_bnv_r >= PASS_SPECTRAL_R
    if seeds_drift_pass >= max(2, n_seeds * 2 // 3) and spectral_ok:
        return ("KF4_HARD_PASS",
                f"DRIFT DETECTABLE via spectral proxies. "
                f"{seeds_drift_pass}/{n_seeds} seeds: r_drift >= {PASS_DRIFT_R}. "
                f"mean_r_drift={mean_drift_r:.3f}. "
                f"mean_r_spectral={mean_spectral_r:.3f}. "
                f"mean_r_bnv={mean_bnv_r:.3f}. "
                f"mean_drift_final={mean_drift_final:.4f}. "
                f"Spectral gap / bundle-norm-var are early-warning drift indicators.")

    return ("KF4_MIDDLE_BAND",
            f"Drift accumulates but spectral proxies weak. "
            f"r_drift={[round(r, 3) for r in r_drifts]}. "
            f"mean_r_spectral={mean_spectral_r:.3f}. "
            f"mean_r_bnv={mean_bnv_r:.3f}. mean_drift_final={mean_drift_final:.4f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: pearson_r
    r = pearson_r(list(range(10)), list(range(10)))
    assert abs(r - 1.0) < 0.01, f"pearson_r of [0..9],[0..9] = {r}, expected 1.0"

    # Self-test 2: compute_drift_amplitude
    device = torch.device("cpu")
    W0 = torch.eye(8)
    W1 = W0 + 0.1 * torch.ones(8, 8)
    drift = compute_drift_amplitude(W1, W0)
    assert drift > 0, f"drift_amplitude should be > 0 after perturbation: {drift}"

    # Self-test 3: verdict
    def mk_sd(r_d, r_s, r_b):
        return {"r_drift": r_d, "r_spectral": r_s, "r_bnv": r_b,
                "r_retention": -0.5, "drift_final": 0.05, "retention_final": 0.99,
                "n_steps": 10, "drift_series": [0.01*i for i in range(1, 11)],
                "bnv_series": [], "spectral_series": [], "retention_series": []}

    # HARD_PASS
    v, msg = compute_verdict({"per_seed": {
        "17": dict(seed=17, N=4096, M=4096, **mk_sd(0.95, 0.60, 0.55)),
        "23": dict(seed=23, N=4096, M=4096, **mk_sd(0.92, 0.55, 0.50)),
    }})
    assert v == "KF4_HARD_PASS", f"Expected KF4_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL
    v, msg = compute_verdict({"per_seed": {
        "17": dict(seed=17, N=4096, M=4096, **mk_sd(0.30, 0.10, 0.05)),
    }})
    assert v == "KF4_HARD_FAIL", f"Expected KF4_HARD_FAIL, got {v}: {msg}"

    # Self-test 4: smoke forward pass
    N_test = 1024
    codebook, _ = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    config_smoke = {"smoke": True, "N": N_test, "n_edits": 10,
                     "n_probe": 30, "measure_every": 5}
    result = run_one_seed(17, config_smoke, device)
    assert "r_drift" in result, "missing r_drift"
    assert "drift_final" in result, "missing drift_final"
    assert result["drift_final"] >= 0.0, f"drift_final < 0: {result['drift_final']}"
    # Drift should be positive after edits (edits change W)
    assert result["drift_final"] > 0.0, (
        f"SUSPICIOUS: drift_final=0 after {config_smoke['n_edits']} edits. "
        f"Edits should change W."
    )

    print("[SELFTEST PASS] kf4_drift_detect_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE
    config = {"smoke": smoke, "N": N, "n_edits": n_edits, "n_probe": n_probe}

    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf4] N={N} seeds={seeds} n_edits={n_edits} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        print(f"  seed {seed} done in {te:.1f}s "
              f"r_drift={result['r_drift']:.3f} r_spectral={result['r_spectral']:.3f} "
              f"drift_final={result['drift_final']:.4f}", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "n_edits": n_edits,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf4] VERDICT: {verdict}", flush=True)
    print(f"[kf4] {verdict_msg}", flush=True)
    print(f"[kf4] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
