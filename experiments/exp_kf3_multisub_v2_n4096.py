"""KF-3 MULTI-SUBSTRATE ISOLATION v2: TRUE N=4096 FULL SCALE with M/N variation.

PARENT: kf3_multisub_isolation_v1 (KF3_MIDDLE_BAND at N=1024 smoke: leakage=0.0142,
  contam=0.0664). v1 completed in smoke mode only; N=4096 FULL was never measured.

SCIENTIFIC QUESTION:
  Does multi-substrate isolation hold at production N=4096?
  At N=1024 (v1), max_leakage=0.0142 > HP threshold 0.01 and max_contam=0.0664 > 0.05.
  Random cross-talk scales as ~1/sqrt(N) for orthogonal HD vectors.
  Prediction: at N=4096 (4x larger), leakage and contamination should be ~0.5x lower:
    expected_leakage ~ 0.0142 * sqrt(1024/4096) = 0.0142 * 0.5 = 0.007 (below HP 0.01)
    expected_contam ~ 0.0664 * sqrt(1024/4096) = 0.0664 * 0.5 = 0.033 (below HP 0.05)
  This would flip v1 MIDDLE_BAND -> v2 HARD_PASS.

FORMULA SELF-TESTS:
  1. Contamination scaling: for random HD vectors at dim N, cosine-sim ~ N(0, 1/sqrt(N)).
     Expected max over n=200 probes: ~ sqrt(2 * ln(200) / N) = sqrt(2 * 5.3 / 4096) ~ 0.051.
     At N=4096: expected_max_contam ~ 0.051. HP threshold 0.05 is near this bound.
  2. Info leakage for orthogonal W_A, W_B: W_A^T k and W_B^T k should be uncorrelated.
     Expected |corr| ~ 1/sqrt(N). At N=4096: ~1/64 = 0.0156. HP=0.01 is tight.
     Note: corr is sample-mean over probes, so CI width ~0.0156/sqrt(50) = 0.0022.

SCOPE: 5 seeds, M/N in {4, 8, 12} (clean/transition/loaded regimes), 5 coupling counts.

PRE-REGISTERED BANDS:
  HARD_PASS: max_leakage < 0.01 AND max_contam < 0.05 at M/N=4 (clean regime).
    Interpretation: structural isolation confirmed at production scale.
  HARD_FAIL: max_leakage > 0.10 OR max_contam > 0.30 at coupling=0, any M/N.
    Interpretation: substrates share state structurally; product isolation claim is false.
  MIDDLE_BAND: leakage or contam exceeds HP but below HF.
    Outcome plan: investigate M/N dependence; if M/N=4 is borderline but M/N=12 fails,
    isolation holds in clean regime and product claim holds for M <= 4N.

CALIBRATION:
  Prior empirical anchor: v1 N=1024 leakage=0.014, contam=0.066.
  HP threshold = v1_value * sqrt(N_v1 / N_v2) = v1 * 0.5 (N-scaling prediction).
  Bands set at +-50% of scaling prediction per calibration-probe policy.

TIMEOUT ESTIMATE:
  v1 smoke elapsed ~5s at N=1024, 3 coupling_counts, 1 seed, 30 probes.
  Per-cell ~ 5/3 = 1.7s at N=1024.
  Full: N=4096, 5 coupling_counts, 5 seeds, 200 probes/seed.
  N-scale: (4096/1024)^2 = 16x (matrix-vector ops).
  seed-scale: 5. coupling-scale: 5/3. probe-scale: 200/30 ~ 6.7.
  But coupling loop is cheap (no W recompute). Dominant cost: codebook build + seed setup.
  Conservative: 1.5 * 1.7 * 16 * 5 * (5/3) * (200/30) = 1.5 * 1.7 * 16 * 5 * 11.1 = 2263s.
  PROT-019: _n4096 -> floor 3600s. timeout_s = 3600.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf3_multisub_v2_n4096
Queue: overnight_queue (GPU; 2 x N=4096 Kerdock substrates, 5-seed 3-M/N isolation probe)
Pre-reg: preregs/2026-05-28_kf3_multisub_v2_n4096.md
Parent: kf3_multisub_isolation_v1 (MIDDLE_BAND at N=1024)
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

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock: even log2; log2(1024)=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M/N values to test isolation across loading regimes
M_FRAC_FULL = [4, 8, 12]    # M = M_frac * N_FULL for full run
M_FRAC_SMOKE = [4]           # smoke: just clean regime

# Coupling counts (non-destructive reads between substrates)
COUPLING_COUNTS_FULL = [0, 1, 5, 25, 100]
COUPLING_COUNTS_SMOKE = [0, 5]

# Probes per cell
N_PROBE_FULL = 200
N_PROBE_SMOKE = 50

# Seeds
SEEDS_FULL = [7, 17, 23, 31, 41]   # 5 seeds for 5-seed FULL
SEEDS_SMOKE = [17]

BETA_INF = 32.0     # inference temperature (same as v1)

# HARD_PASS thresholds (based on N-scaling prediction from v1)
HP_LEAKAGE_MAX = 0.01      # expected at N=4096: ~0.007
HP_CONTAM_MAX = 0.05       # expected at N=4096: ~0.033
# HARD_FAIL thresholds (structural failure)
HF_LEAKAGE_MIN = 0.10
HF_CONTAM_MIN = 0.30


def get_output_dir(default_name: str = "kf3_multisub_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate(codebook: torch.Tensor, M: int, seed: int,
                     N: int, device: torch.device) -> tuple:
    """Build substrate W with M stored facts. Returns (W, keys, val_idx)."""
    C = codebook.shape[0]
    M = min(M, C)
    gen_cpu = torch.Generator(device='cpu').manual_seed(seed)
    perm = torch.randperm(C, generator=gen_cpu)
    key_idx = perm[:M].to(device)
    val_idx = torch.randperm(C, generator=torch.Generator(device='cpu').manual_seed(seed + 99999))[:M].to(device)
    keys = codebook[key_idx]
    values = codebook[val_idx]
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    batch = 256
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = values[start:start + batch]
        W += (v_b.T @ k_b) / N
    return W, keys, val_idx


def query_response(W: torch.Tensor, keys: torch.Tensor, N: int) -> torch.Tensor:
    """Raw query response vectors. Returns (n, N)."""
    return keys @ W.T   # (n, N)


def measure_info_leakage(resp_A: torch.Tensor, resp_B: torch.Tensor) -> float:
    """Mean absolute cosine similarity between independent query responses.
    For orthogonal HD spaces: expected ~1/sqrt(N) for N-dimensional random vectors."""
    n = min(resp_A.shape[0], resp_B.shape[0], 50)
    a = resp_A[:n]
    b = resp_B[:n]
    norms_a = a.norm(dim=1, keepdim=True).clamp(min=1e-10)
    norms_b = b.norm(dim=1, keepdim=True).clamp(min=1e-10)
    cos_sims = ((a / norms_a) * (b / norms_b)).sum(dim=1)  # (n,)
    return float(cos_sims.abs().mean().item())


def measure_state_contamination(resp_A: torch.Tensor, resp_B: torch.Tensor) -> float:
    """Max cosine similarity between A and B response vectors."""
    n = min(resp_A.shape[0], resp_B.shape[0])
    a = resp_A[:n]
    b = resp_B[:n]
    norms_a = a.norm(dim=1, keepdim=True).clamp(min=1e-10)
    norms_b = b.norm(dim=1, keepdim=True).clamp(min=1e-10)
    cos_sims = ((a / norms_a) * (b / norms_b)).sum(dim=1)
    return float(cos_sims.abs().max().item())


def measure_acc_B_own(W_B: torch.Tensor, codebook: torch.Tensor,
                       keys_B: torch.Tensor, val_idx_B: torch.Tensor,
                       n_probe: int, N: int) -> float:
    """B's accuracy on its own stored facts."""
    n = min(n_probe, keys_B.shape[0])
    resp_B = query_response(W_B, keys_B[:n], N)
    sims = (codebook @ resp_B.T) / N   # (C, n)
    preds = sims.argmax(dim=0)  # (n,)
    return float((preds == val_idx_B[:n]).float().mean().item())


def run_one_cell(W_A: torch.Tensor, W_B: torch.Tensor,
                  codebook: torch.Tensor,
                  keys_A: torch.Tensor, val_idx_A: torch.Tensor,
                  keys_B: torch.Tensor, val_idx_B: torch.Tensor,
                  coupling_count: int, n_probe: int,
                  N: int) -> dict:
    """Measure isolation for one (seed, M_frac, coupling_count) cell."""
    n = min(n_probe, keys_A.shape[0], keys_B.shape[0])

    # A's query responses
    resp_A = query_response(W_A, keys_A[:n], N)   # (n, N)
    # B's query responses (queried with A's keys)
    resp_B_Akeys = query_response(W_B, keys_A[:n], N)   # (n, N)
    # B's query responses on B's own keys
    resp_B_own = query_response(W_B, keys_B[:n], N)   # (n, N)

    info_leakage = measure_info_leakage(resp_A, resp_B_Akeys)
    state_contamination = measure_state_contamination(resp_A, resp_B_Akeys)
    acc_B_own = measure_acc_B_own(W_B, codebook, keys_B, val_idx_B, n, N)

    return {
        "coupling_count": coupling_count,
        "info_leakage": info_leakage,
        "state_contamination": state_contamination,
        "acc_B_own": acc_B_own,
    }


def run_one_seed_mfrac(seed: int, M_frac: int, config: dict,
                        device: torch.device) -> dict:
    """Run all coupling counts for one (seed, M_frac) pair."""
    N = config["N"]
    M = M_frac * N
    coupling_counts = config["coupling_counts"]
    n_probe = config["n_probe"]

    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)

    W_A, keys_A, val_idx_A = build_substrate(codebook, M, seed, N, device)
    W_B, keys_B, val_idx_B = build_substrate(codebook, M, seed + 10000, N, device)

    per_coupling = {}
    for cc in coupling_counts:
        # Reads are non-destructive; coupling_count doesn't change W
        # We test structural isolation: different memories, same vocabulary
        cell = run_one_cell(
            W_A, W_B, codebook,
            keys_A, val_idx_A, keys_B, val_idx_B,
            cc, n_probe, N
        )
        per_coupling[str(cc)] = cell

    return {
        "seed": seed,
        "M_frac": M_frac,
        "M": M,
        "N": N,
        "per_coupling": per_coupling,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Verdict: HARD_PASS, HARD_FAIL, MIDDLE_BAND, or INCONCLUSIVE."""
    results = summary.get("results", [])
    if not results:
        return ("KF3V2_INCONCLUSIVE", "No result cells.")

    # Check HARD_FAIL at coupling=0 for any M/N
    hf_triggered = False
    hf_details = []
    for r in results:
        cell0 = r.get("per_coupling", {}).get("0")
        if cell0:
            if (cell0["info_leakage"] > HF_LEAKAGE_MIN
                    or cell0["state_contamination"] > HF_CONTAM_MIN):
                hf_triggered = True
                hf_details.append(
                    f"seed={r['seed']} M/N={r['M_frac']}: "
                    f"leakage={cell0['info_leakage']:.4f} "
                    f"contam={cell0['state_contamination']:.4f}"
                )

    if hf_triggered:
        return ("KF3V2_HARD_FAIL",
                f"STRUCTURAL ISOLATION FAILURE at coupling=0. "
                + "; ".join(hf_details[:3]))

    # Collect all metrics across cells
    all_leakage = []
    all_contam = []
    all_accB = []
    # Focus on M/N=4 (clean regime) for HP judgment
    clean_leakage = []
    clean_contam = []

    for r in results:
        for cc_key, cell in r.get("per_coupling", {}).items():
            all_leakage.append(cell["info_leakage"])
            all_contam.append(cell["state_contamination"])
            all_accB.append(cell["acc_B_own"])
            if r.get("M_frac", 99) == 4:
                clean_leakage.append(cell["info_leakage"])
                clean_contam.append(cell["state_contamination"])

    if not all_leakage:
        return ("KF3V2_INCONCLUSIVE", "No metric cells.")

    max_leakage = max(all_leakage)
    max_contam = max(all_contam)
    mean_accB = sum(all_accB) / len(all_accB)
    max_clean_leakage = max(clean_leakage) if clean_leakage else 1.0
    max_clean_contam = max(clean_contam) if clean_contam else 1.0

    # HARD_PASS: isolation holds in clean regime (M/N=4)
    if (max_clean_leakage < HP_LEAKAGE_MAX
            and max_clean_contam < HP_CONTAM_MAX):
        return ("KF3V2_HARD_PASS",
                f"MULTI-SUBSTRATE ISOLATION CONFIRMED at N=4096 clean regime. "
                f"max_leakage_clean={max_clean_leakage:.5f}<{HP_LEAKAGE_MAX}. "
                f"max_contam_clean={max_clean_contam:.5f}<{HP_CONTAM_MAX}. "
                f"max_leakage_all={max_leakage:.5f}. max_contam_all={max_contam:.5f}. "
                f"mean_acc_B={mean_accB:.3f}.")

    return ("KF3V2_MIDDLE_BAND",
            f"Partial isolation at N=4096. "
            f"max_leakage_clean={max_clean_leakage:.4f} (HP<{HP_LEAKAGE_MAX}). "
            f"max_contam_clean={max_clean_contam:.4f} (HP<{HP_CONTAM_MAX}). "
            f"max_leakage_all={max_leakage:.4f}. max_contam_all={max_contam:.4f}. "
            f"mean_acc_B={mean_accB:.3f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at tiny scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: verdict logic (HARD_PASS path)
    summary_pass = {"results": [
        {"seed": 17, "M_frac": 4, "M": 4096, "N": 4096,
         "per_coupling": {"0": {"coupling_count": 0, "info_leakage": 0.005,
                                 "state_contamination": 0.03, "acc_B_own": 0.99}}}
    ]}
    v, msg = compute_verdict(summary_pass)
    assert v == "KF3V2_HARD_PASS", f"Expected HARD_PASS, got {v}: {msg}"

    # Self-test 2: verdict logic (HARD_FAIL path)
    summary_fail = {"results": [
        {"seed": 17, "M_frac": 4, "M": 4096, "N": 4096,
         "per_coupling": {"0": {"coupling_count": 0, "info_leakage": 0.15,
                                 "state_contamination": 0.03, "acc_B_own": 0.99}}}
    ]}
    v, msg = compute_verdict(summary_fail)
    assert v == "KF3V2_HARD_FAIL", f"Expected HARD_FAIL, got {v}: {msg}"

    # Self-test 3: forward pass at tiny scale
    device = torch.device("cpu")
    N_test = 1024
    codebook, _ = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = min(C, 100)

    W_A, keys_A, val_idx_A = build_substrate(codebook, M_test, 17, N_test, device)
    W_B, keys_B, val_idx_B = build_substrate(codebook, M_test, 10017, N_test, device)

    cell = run_one_cell(W_A, W_B, codebook,
                         keys_A, val_idx_A, keys_B, val_idx_B,
                         0, 20, N_test)

    assert "info_leakage" in cell, "missing info_leakage"
    assert "state_contamination" in cell, "missing state_contamination"
    assert "acc_B_own" in cell, "missing acc_B_own"
    assert 0.0 <= cell["info_leakage"] <= 1.0, f"info_leakage={cell['info_leakage']}"
    assert 0.0 <= cell["state_contamination"] <= 1.0, \
        f"state_contamination={cell['state_contamination']}"
    assert 0.0 <= cell["acc_B_own"] <= 1.0, f"acc_B_own={cell['acc_B_own']}"
    assert cell["info_leakage"] is not None and not math.isnan(cell["info_leakage"]), \
        "info_leakage is NaN"

    print("[SELFTEST PASS] kf3_multisub_v2_n4096 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRAC_SMOKE if smoke else M_FRAC_FULL
    coupling_counts = COUPLING_COUNTS_SMOKE if smoke else COUPLING_COUNTS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL
    config = {
        "smoke": smoke,
        "N": N,
        "coupling_counts": coupling_counts,
        "n_probe": n_probe,
    }
    t0 = time.time()
    out_dir = get_output_dir()
    n_cells = len(seeds) * len(m_fracs) * len(coupling_counts)
    print(f"[kf3v2] N={N} seeds={seeds} m_fracs={m_fracs} "
          f"coupling={coupling_counts} n_probe={n_probe} "
          f"device={device} mode={'smoke' if smoke else 'full'} "
          f"total_cells={n_cells}", flush=True)

    all_results = []
    for seed in seeds:
        for M_frac in m_fracs:
            print(f"  seed={seed} M/N={M_frac}...", flush=True)
            ts = time.time()
            result = run_one_seed_mfrac(seed, M_frac, config, device)
            te = time.time() - ts
            cell0 = result.get("per_coupling", {}).get("0", {})
            print(f"  done in {te:.1f}s "
                  f"leakage_0={cell0.get('info_leakage', 0):.5f} "
                  f"contam_0={cell0.get('state_contamination', 0):.5f} "
                  f"accB={cell0.get('acc_B_own', 0):.3f}", flush=True)
            all_results.append(result)

    summary = {
        "results": all_results,
        "N_full": N_FULL,
        "N_used": N,
        "m_fracs": m_fracs,
        "coupling_counts": coupling_counts,
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
    print(f"\n[kf3v2] VERDICT: {verdict}", flush=True)
    print(f"[kf3v2] {verdict_msg}", flush=True)
    print(f"[kf3v2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
