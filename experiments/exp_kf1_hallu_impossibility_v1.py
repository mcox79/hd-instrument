"""KF-1 HALLUCINATION-IMPOSSIBILITY VALIDATION: N=4096 Kerdock 4-coset.

SCIENTIFIC QUESTION (Killer Feature 1):
  Does the substrate exhibit hallucination-impossibility: when queried with
  a key that has NO stored association, does the output remain below a
  detectability threshold (confidence < 1/C + eps where C is codebook size)?

  Hallucination impossibility = the substrate cannot output a confident answer
  that is not decomposable to stored atoms. This is a product-grade security
  property: auditable memory with no silent confabulation.

DESIGN:
  - Store M facts as Kerdock 4-coset (key, value) pairs. Sweep M/N axis:
    M in {N/4, N/2, N, 2N, 4N} = {1024, 2048, 4096, 8192, 16384} at N=4096.
  - For each M, use 1000 out-of-set query keys (keys NOT in stored set).
  - Measure:
    (a) max_confidence: max(softmax(beta * sims)) over out-of-set queries
    (b) above_thresh_frac: fraction of out-of-set queries where max_conf > THRESH
    (c) confidence_margin: mean(1/C - max_conf) -- positive = safe
    (d) As control: in-set query accuracy (should be high)
  - Falsifier: any out-of-set query with confidence > HALLU_THRESHOLD=0.5
    is a hallucination event.
  - 3 seeds per M value.

PRE-REGISTERED BANDS (first systematic hallucination probe on this substrate):
  Calibration probe -- prior qualitative evidence from KF-5 smoke that
  max_softmax << 0.5. Bands set per calibration-probe policy (+-50% of theory).

  HARD_PASS: max_confidence < HALLU_THRESHOLD=0.5 in ALL M values AND ALL
    3 seeds across ALL 1000 out-of-set queries. Substrate achieves
    hallucination-impossibility across the full M/N sweep.
  HARD_FAIL: above_thresh_frac > 0.01 (>1% of OOS queries exceed threshold)
    at M <= N (under-capacity regime where substrate should be clean).
  MIDDLE_BAND: zero hallucinations at low M but threshold violations at
    M >= 2N (over-capacity degradation, not structural impossibility).

FORMULA SELF-TESTS:
  1. For C=4^(t+1) (Kerdock codebook size at N=4096, t=6: C=16384).
     Uniform output: max_conf = 1/C ~ 1/16384 ~ 6e-5. Far below 0.5.
  2. For stored facts at retrieval: in-set max_conf should be near 1.0
     (high confidence on stored facts = good memory).
  3. HALLU_THRESHOLD = 0.5: binary decision. Above = hallucination event.
  4. confidence_margin > 0 means max_conf < 1/C (BELOW uniform = impossible).
     confidence_margin < 0 means substrate has SPURIOUS confidence.

TIMEOUT ESTIMATE:
  smoke_N=1024, 1 seed, 3 M values, 100 OOS probes. ~10s smoke.
  Full: N=4096, 3 seeds, 5 M values, 1000 OOS probes.
  scale: (4096/1024)^1.5 * 3 * (1000/100) = 8 * 3 * 10 = 240
  timeout_s = ceil(1.5 * 10 * 240) = ceil(3600) -> 3600s.

N-suffix: no _nN suffix; multi-M sweep (PROT-018: stated explicitly).
Queue: overnight_queue (GPU; Kerdock 4-coset at N=4096, matrix ops)
Pre-reg: preregs/2026-05-27_kf1_hallu_impossibility_v1.md
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

# Load Kerdock v3 codebook generator
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024
# M sweep: {N/4, N/2, N, 2N, 4N}  -- computed at runtime from N
M_FRACTIONS_FULL = [0.25, 0.5, 1.0, 2.0, 4.0]
M_FRACTIONS_SMOKE = [0.25, 1.0, 2.0]
N_OOS_QUERIES_FULL = 1000
N_OOS_QUERIES_SMOKE = 100
N_INSET_QUERIES_FULL = 200
N_INSET_QUERIES_SMOKE = 30
BETA_INF = 32.0
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
HALLU_THRESHOLD = 0.5    # confidence above this = hallucination event
HALLU_FRAC_HARD_FAIL = 0.01  # >1% OOS queries above threshold = HARD_FAIL


def get_output_dir(default_name: str = "kf1_hallu_impossibility_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_facts_outer(keys: torch.Tensor, values: torch.Tensor,
                       N: int) -> torch.Tensor:
    """Outer-product Hebbian store. W = sum(v_i outer k_i^T) / N."""
    W = torch.zeros(N, N, dtype=torch.float32, device=keys.device)
    batch = 256
    M = keys.shape[0]
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = values[start:start + batch]
        W += (v_b.T @ k_b) / N
    return W


def query_confidence(W: torch.Tensor, query_keys: torch.Tensor,
                      codebook: torch.Tensor, beta_inf: float, N: int,
                      batch_size: int = 128) -> torch.Tensor:
    """For each query key, return max softmax confidence over codebook.
    Returns (Q,) tensor of max_confidence values."""
    Q = query_keys.shape[0]
    max_confs = []
    for bs in range(0, Q, batch_size):
        be = min(bs + batch_size, Q)
        q_batch = query_keys[bs:be]   # (B, N)
        # q = W^T @ q_batch^T  -- retrieval query
        response = q_batch @ W.T    # (B, N)
        sims = (codebook @ response.T) / N   # (C, B)
        P = torch.softmax(beta_inf * sims, dim=0)   # (C, B)
        max_conf_batch = P.max(dim=0).values   # (B,)
        max_confs.append(max_conf_batch)
    return torch.cat(max_confs, dim=0)


def run_one_cell(M: int, seed: int, codebook: torch.Tensor, N: int,
                  n_oos: int, n_inset: int, device: torch.device) -> dict:
    """Run one (M, seed) cell. Returns metrics dict."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)

    if M > C:
        # Over-capacity: we reuse codebook vectors as keys (with repetition)
        # Note: Kerdock codebook is designed for M <= C unique keys
        # At M > C we test behavior under aliasing stress
        perm = torch.randperm(C, generator=gen, device=device)
        key_idx = torch.cat([perm, torch.randperm(C, generator=gen, device=device)])[:M]
        val_perm = torch.randperm(C, generator=gen, device=device)
        val_idx = torch.cat([val_perm, torch.randperm(C, generator=gen, device=device)])[:M]
    else:
        perm = torch.randperm(C, generator=gen, device=device)
        key_idx = perm[:M]
        val_perm = torch.randperm(C, generator=gen, device=device)
        val_idx = val_perm[:M]

    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]

    # Train W
    W = store_facts_outer(keys, values, N)

    # Out-of-set query keys
    used_set = set(key_idx[:min(M, C)].tolist())
    oos_candidates = [i for i in range(C) if i not in used_set]
    if len(oos_candidates) == 0:
        # All codebook vectors used (over-capacity): use random perturbations
        noise_gen = torch.Generator(device=device).manual_seed(seed + 999)
        oos_keys = codebook[torch.randperm(C, generator=noise_gen, device=device)[:n_oos]]
        # Add tiny noise to create genuinely OOS keys
        noise = torch.randn_like(oos_keys) * 0.1
        oos_keys = oos_keys + noise
    else:
        n_take = min(n_oos, len(oos_candidates))
        oos_perm = torch.randperm(len(oos_candidates), generator=gen, device=device)
        oos_idx = [oos_candidates[i] for i in oos_perm[:n_take].tolist()]
        oos_keys = codebook[oos_idx]
        if n_take < n_oos:
            # Pad with random perturbations
            extra_noise = torch.randn(n_oos - n_take, N, device=device) * 0.1
            extra_oos = codebook[oos_idx[:n_oos - n_take]] + extra_noise
            oos_keys = torch.cat([oos_keys, extra_oos], dim=0)

    # In-set query
    n_inset_probe = min(n_inset, M)
    inset_perm = torch.randperm(M, generator=gen, device=device)[:n_inset_probe]
    inset_keys = keys[inset_perm]
    inset_val_idx = val_idx[inset_perm] % C

    # Compute confidence
    oos_max_confs = query_confidence(W, oos_keys, codebook, BETA_INF, N)
    inset_max_confs = query_confidence(W, inset_keys, codebook, BETA_INF, N)

    # Inset argmax accuracy
    C_code = codebook.shape[0]
    inset_pred = []
    batch = 64
    for bs in range(0, n_inset_probe, batch):
        be = min(bs + batch, n_inset_probe)
        ik = inset_keys[bs:be]
        resp = ik @ W.T
        sims = (codebook @ resp.T) / N
        pred_idx = torch.argmax(sims, dim=0)
        inset_pred.append(pred_idx)
    inset_pred = torch.cat(inset_pred, dim=0)
    inset_acc = float((inset_pred == inset_val_idx.to(device)).float().mean().item())

    return {
        "M": M,
        "M_over_N": M / N,
        "seed": seed,
        "C": C,
        "oos_max_conf_mean": float(oos_max_confs.mean().item()),
        "oos_max_conf_max": float(oos_max_confs.max().item()),
        "above_thresh_frac": float((oos_max_confs > HALLU_THRESHOLD).float().mean().item()),
        "confidence_margin_mean": float((1.0 / C - oos_max_confs).mean().item()),
        "inset_acc": inset_acc,
        "inset_max_conf_mean": float(inset_max_confs.mean().item()),
    }


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run all M values for one seed."""
    smoke = config["smoke"]
    N = config["N"]
    m_fracs = config["m_fracs"]
    n_oos = config["n_oos"]
    n_inset = config["n_inset"]

    codebook, info = v3.make_kerdock_4coset_codebook(N, device)
    per_M = {}
    for frac in m_fracs:
        M = int(frac * N)
        cell = run_one_cell(M, seed, codebook, N, n_oos, n_inset, device)
        per_M[str(frac)] = cell
    return {"seed": seed, "N": N, "per_M": per_M}


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF1_INCONCLUSIVE", "No per-seed data.")

    # Collect: any above_thresh_frac > HARD_FAIL at low M?
    low_m_hallu_events = 0
    total_low_m_cells = 0
    high_m_hallu_events = 0
    total_high_m_cells = 0
    hard_pass_cells = 0
    total_cells = 0

    all_max_confs_undercap = []
    all_max_confs_overcap = []

    for seed_key, seed_data in per_seed.items():
        for frac_key, cell in seed_data.get("per_M", {}).items():
            frac = float(frac_key)
            above = cell["above_thresh_frac"]
            max_c = cell["oos_max_conf_max"]
            total_cells += 1
            if max_c < HALLU_THRESHOLD:
                hard_pass_cells += 1
            if frac <= 1.0:
                total_low_m_cells += 1
                all_max_confs_undercap.append(cell["oos_max_conf_mean"])
                if above > HALLU_FRAC_HARD_FAIL:
                    low_m_hallu_events += 1
            else:
                total_high_m_cells += 1
                all_max_confs_overcap.append(cell["oos_max_conf_mean"])
                if above > HALLU_FRAC_HARD_FAIL:
                    high_m_hallu_events += 1

    if total_cells == 0:
        return ("KF1_INCONCLUSIVE", "No cells computed.")

    mean_oos_undercap = (sum(all_max_confs_undercap) / len(all_max_confs_undercap)
                          if all_max_confs_undercap else 0.0)
    mean_oos_overcap = (sum(all_max_confs_overcap) / len(all_max_confs_overcap)
                         if all_max_confs_overcap else 0.0)

    # HARD_FAIL: hallucinations at low M (under-capacity)
    if low_m_hallu_events > 0 and total_low_m_cells > 0:
        return ("KF1_HARD_FAIL",
                f"Hallucination events at under-capacity (M<=N): "
                f"{low_m_hallu_events}/{total_low_m_cells} cells have "
                f"above_thresh_frac > {HALLU_FRAC_HARD_FAIL}. "
                f"mean_oos_max_conf={mean_oos_undercap:.5f}. "
                f"Substrate can confabulate even at low load.")

    # HARD_PASS: no hallucinations across all M values
    if hard_pass_cells == total_cells:
        return ("KF1_HARD_PASS",
                f"HALLUCINATION-IMPOSSIBILITY VALIDATED. No OOS query exceeds "
                f"threshold={HALLU_THRESHOLD} across all {total_cells} cells "
                f"(M/N in {summary.get('m_fracs', [])}). "
                f"mean_oos_max_conf_undercap={mean_oos_undercap:.5f}. "
                f"mean_oos_max_conf_overcap={mean_oos_overcap:.5f}. "
                f"Product-grade: substrate cannot confabulate stored facts.")

    # MIDDLE_BAND: hallucinations only at over-capacity
    if low_m_hallu_events == 0 and high_m_hallu_events > 0:
        return ("KF1_MIDDLE_BAND",
                f"Hallucination-impossibility holds at M<=N "
                f"but degraded at over-capacity (M>N). "
                f"under_cap mean_oos_max_conf={mean_oos_undercap:.5f}. "
                f"over_cap events={high_m_hallu_events}/{total_high_m_cells}. "
                f"Practical product: use substrate at M<=N for safety guarantee.")

    return ("KF1_MIDDLE_BAND",
            f"Mixed results. hard_pass_cells={hard_pass_cells}/{total_cells}. "
            f"low_M hallu={low_m_hallu_events}, high_M hallu={high_m_hallu_events}. "
            f"mean_oos_undercap={mean_oos_undercap:.5f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 4096 stated explicitly
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: HALLU_THRESHOLD logic
    def mk_cell(above_frac, max_conf, frac):
        return {
            "M": int(frac * 1024), "M_over_N": frac, "seed": 17, "C": 4096,
            "oos_max_conf_mean": max_conf * 0.9, "oos_max_conf_max": max_conf,
            "above_thresh_frac": above_frac, "confidence_margin_mean": 1/4096 - max_conf,
            "inset_acc": 0.95, "inset_max_conf_mean": 0.99,
        }
    # HARD_PASS: no hallucinations
    summary_pass = {
        "m_fracs": [0.25, 1.0, 2.0],
        "per_seed": {
            "17": {"seed": 17, "N": 1024, "per_M": {
                "0.25": mk_cell(0.0, 0.001, 0.25),
                "1.0": mk_cell(0.0, 0.002, 1.0),
                "2.0": mk_cell(0.0, 0.005, 2.0),
            }},
            "23": {"seed": 23, "N": 1024, "per_M": {
                "0.25": mk_cell(0.0, 0.001, 0.25),
                "1.0": mk_cell(0.0, 0.002, 1.0),
                "2.0": mk_cell(0.0, 0.004, 2.0),
            }},
        }
    }
    v, msg = compute_verdict(summary_pass)
    assert v == "KF1_HARD_PASS", f"Expected KF1_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: hallucination at M=N (frac=1.0)
    summary_fail = {
        "m_fracs": [1.0],
        "per_seed": {
            "17": {"seed": 17, "N": 1024, "per_M": {
                "1.0": mk_cell(0.05, 0.8, 1.0),   # 5% above threshold
            }},
        }
    }
    v, msg = compute_verdict(summary_fail)
    assert v == "KF1_HARD_FAIL", f"Expected KF1_HARD_FAIL, got {v}: {msg}"

    # MIDDLE_BAND: hallucination only at over-capacity (frac=2.0)
    summary_mid = {
        "m_fracs": [1.0, 2.0],
        "per_seed": {
            "17": {"seed": 17, "N": 1024, "per_M": {
                "1.0": mk_cell(0.0, 0.002, 1.0),
                "2.0": mk_cell(0.05, 0.8, 2.0),
            }},
        }
    }
    v, msg = compute_verdict(summary_mid)
    assert v == "KF1_MIDDLE_BAND", f"Expected KF1_MIDDLE_BAND, got {v}: {msg}"

    # Self-test 2: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    codebook, info = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = min(C, N_test)

    # Quick cell run
    cell = run_one_cell(M_test, 17, codebook, N_test, 20, 10, device)
    assert "oos_max_conf_mean" in cell, "missing oos_max_conf_mean"
    assert "above_thresh_frac" in cell, "missing above_thresh_frac"
    assert 0.0 <= cell["oos_max_conf_mean"] <= 1.0, \
        f"oos_max_conf_mean out of range: {cell['oos_max_conf_mean']}"
    assert 0.0 <= cell["above_thresh_frac"] <= 1.0, \
        f"above_thresh_frac out of range: {cell['above_thresh_frac']}"
    assert cell["oos_max_conf_max"] < HALLU_THRESHOLD, (
        f"SUSPICIOUS: OOS max_conf={cell['oos_max_conf_max']:.4f} >= {HALLU_THRESHOLD} "
        f"at smoke scale. Check codebook construction."
    )

    print("[SELFTEST PASS] kf1_hallu_impossibility_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS_FULL
    n_oos = N_OOS_QUERIES_SMOKE if smoke else N_OOS_QUERIES_FULL
    n_inset = N_INSET_QUERIES_SMOKE if smoke else N_INSET_QUERIES_FULL
    config = {
        "smoke": smoke,
        "N": N,
        "m_fracs": m_fracs,
        "n_oos": n_oos,
        "n_inset": n_inset,
    }
    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf1] N={N} seeds={seeds} m_fracs={m_fracs} n_oos={n_oos} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        # Quick diagnostic
        per_M = result.get("per_M", {})
        maxcs = [v["oos_max_conf_max"] for v in per_M.values()]
        print(f"  seed {seed} done in {te:.1f}s "
              f"oos_max_conf_max=[{', '.join(f'{c:.4f}' for c in maxcs)}]", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "m_fracs": m_fracs,
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
    print(f"\n[kf1] VERDICT: {verdict}", flush=True)
    print(f"[kf1] {verdict_msg}", flush=True)
    print(f"[kf1] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
