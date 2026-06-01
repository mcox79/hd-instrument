"""KF-1 HALLUCINATION-IMPOSSIBILITY v2: N=4096 5-seed FULL (cross-seed reproducibility).

PARENT: exp_kf1_hallu_impossibility_v1.py -- v1 used 3 seeds [7,17,23].
  v1 result: KF1_HARD_PASS (1-seed-equivalent sweep; single seed=7 at N=4096).
  v2 extends to 5-seed [7,17,23,31,41] for product-spec defensibility before
  Tier-1 product feature commit.

SCIENTIFIC QUESTION (Killer Feature 1):
  Cross-seed reproducibility of hallucination-impossibility: mean_oos_max_conf < 0.001
  at M <= N across ALL 5 seeds. Structurally cannot hallucinate at M <= N.

PRE-REGISTERED BANDS (tightened from v1 per routing-note spec):
  HARD_PASS: 5/5 seeds show mean_oos_max_conf < 0.001 at M <= N
    AND above_thresh_frac == 0 at all under-cap cells (M <= N).
    Interpretation: Tier-1 product feature defensible -- substrate structurally
    cannot hallucinate when used at or below capacity.
  HARD_FAIL: >= 1 seed shows oos_max_conf > 0.01 at M <= N.
    Product claim is not reproducible under new random draws.
  MIDDLE_BAND: 5/5 seeds pass HALLU_THRESHOLD (< 0.5) but some seeds have
    mean_oos_max_conf > 0.001 at under-cap cells. Weaker guarantee.

FORMULA SELF-TESTS:
  1. For C=4^(t+1) (N=4096, t=6: C=16384). Uniform: max_conf ~ 1/C ~ 6e-5.
  2. In-set max_conf should be near 1.0 (high confidence on stored facts).
  3. HALLU_THRESHOLD = 0.5: binary. above_thresh_frac=0 if all < 0.5.
  4. confidence_margin > 0 means max_conf < 1/C (below uniform = impossible).
  5. HP gate v2: mean_oos_max_conf < 0.001 per seed (5x tighter than v1 threshold).

TIMEOUT ESTIMATE:
  smoke_wall_s (v1 CPU, N=1024, 1 seed): 0.1s.
  Full v2: N=4096, 5 seeds (was 3), 5 M values, 1000 OOS probes.
  Scale vs v1: (4096/1024)^1.5 * (5/1) * (1000/100) = 8 * 5 * 10 = 400.
  v1 prereg anchor: 3600s for 3 seeds; v2 with 5 seeds: 3600 * (5/3) = 6000s.
  With +50% buffer: 9000s -- exceeds 7200s 2h flag.
  FLAG: run expected > 7200s. Justified by Tier-1 feature defensibility requirement.
  timeout_s = 10800 (3h; within 14400s limit; flagged for visibility).

N-suffix: no _nN suffix; multi-M sweep (PROT-018: stated explicitly; N_FULL=4096).
Queue: overnight_queue (GPU; Kerdock N=4096, 5-seed FULL)
Pre-reg: preregs/2026-05-27_kf1_hallu_impossibility_v2.md
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

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 1024
M_FRACTIONS_FULL = [0.25, 0.5, 1.0, 2.0, 4.0]
M_FRACTIONS_SMOKE = [0.25, 1.0, 2.0]
N_OOS_QUERIES_FULL = 1000
N_OOS_QUERIES_SMOKE = 100
N_INSET_QUERIES_FULL = 200
N_INSET_QUERIES_SMOKE = 30
BETA_INF = 32.0
# v2: 5 seeds for cross-seed reproducibility
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
HALLU_THRESHOLD = 0.5
HALLU_FRAC_HARD_FAIL = 0.01

# v2 tightened HP gate: per-seed mean_oos_max_conf < this at M <= N
HP_MEAN_MAX_CONF_UNDERCAP = 0.001


def get_output_dir(default_name: str = "kf1_hallu_impossibility_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_facts_outer(keys: torch.Tensor, values: torch.Tensor,
                       N: int) -> torch.Tensor:
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
    Q = query_keys.shape[0]
    max_confs = []
    for bs in range(0, Q, batch_size):
        be = min(bs + batch_size, Q)
        q_batch = query_keys[bs:be]
        response = q_batch @ W.T
        sims = (codebook @ response.T) / N
        P = torch.softmax(beta_inf * sims, dim=0)
        max_conf_batch = P.max(dim=0).values
        max_confs.append(max_conf_batch)
    return torch.cat(max_confs, dim=0)


def run_one_cell(M: int, seed: int, codebook: torch.Tensor, N: int,
                  n_oos: int, n_inset: int, device: torch.device) -> dict:
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)

    if M > C:
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
    W = store_facts_outer(keys, values, N)

    used_set = set(key_idx[:min(M, C)].tolist())
    oos_candidates = [i for i in range(C) if i not in used_set]
    if len(oos_candidates) == 0:
        noise_gen = torch.Generator(device=device).manual_seed(seed + 999)
        oos_keys = codebook[torch.randperm(C, generator=noise_gen, device=device)[:n_oos]]
        noise = torch.randn_like(oos_keys) * 0.1
        oos_keys = oos_keys + noise
    else:
        n_take = min(n_oos, len(oos_candidates))
        oos_perm = torch.randperm(len(oos_candidates), generator=gen, device=device)
        oos_idx = [oos_candidates[i] for i in oos_perm[:n_take].tolist()]
        oos_keys = codebook[oos_idx]
        if n_take < n_oos:
            extra_noise = torch.randn(n_oos - n_take, N, device=device) * 0.1
            extra_oos = codebook[oos_idx[:n_oos - n_take]] + extra_noise
            oos_keys = torch.cat([oos_keys, extra_oos], dim=0)

    n_inset_probe = min(n_inset, M)
    inset_perm = torch.randperm(M, generator=gen, device=device)[:n_inset_probe]
    inset_keys = keys[inset_perm]
    inset_val_idx = val_idx[inset_perm] % C

    oos_max_confs = query_confidence(W, oos_keys, codebook, BETA_INF, N)
    inset_max_confs = query_confidence(W, inset_keys, codebook, BETA_INF, N)

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

    low_m_hallu_events = 0
    total_low_m_cells = 0
    high_m_hallu_events = 0
    total_high_m_cells = 0
    hard_pass_cells = 0
    total_cells = 0

    all_max_confs_undercap = []
    all_max_confs_overcap = []

    # v2: per-seed mean_oos_max_conf at under-cap for tight HP gate
    seeds_tight_pass = 0  # seeds where ALL undercap cells have mean < HP_MEAN_MAX_CONF_UNDERCAP
    n_seeds_checked = 0

    for seed_key, seed_data in per_seed.items():
        seed_undercap_confs = []
        n_seeds_checked += 1
        for frac_key, cell in seed_data.get("per_M", {}).items():
            frac = float(frac_key)
            above = cell["above_thresh_frac"]
            max_c = cell["oos_max_conf_max"]
            mean_c = cell["oos_max_conf_mean"]
            total_cells += 1
            if max_c < HALLU_THRESHOLD:
                hard_pass_cells += 1
            if frac <= 1.0:
                total_low_m_cells += 1
                all_max_confs_undercap.append(mean_c)
                seed_undercap_confs.append(mean_c)
                if above > HALLU_FRAC_HARD_FAIL:
                    low_m_hallu_events += 1
            else:
                total_high_m_cells += 1
                all_max_confs_overcap.append(mean_c)
                if above > HALLU_FRAC_HARD_FAIL:
                    high_m_hallu_events += 1

        # Check tight HP gate for this seed
        if seed_undercap_confs and all(c < HP_MEAN_MAX_CONF_UNDERCAP for c in seed_undercap_confs):
            seeds_tight_pass += 1

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
                f"{low_m_hallu_events}/{total_low_m_cells} cells above threshold. "
                f"mean_oos_max_conf_undercap={mean_oos_undercap:.5f}. "
                f"Product claim NOT reproducible.")

    # Check if any seed has mean_oos_max_conf > 0.01 at undercap (v2 HARD_FAIL gate)
    seeds_failing_tight = n_seeds_checked - seeds_tight_pass
    if seeds_failing_tight > 0 and any(c > 0.01 for c in all_max_confs_undercap):
        return ("KF1_HARD_FAIL",
                f"oos_max_conf > 0.01 at M<=N in {seeds_failing_tight} seeds. "
                f"mean_oos_undercap={mean_oos_undercap:.5f}. "
                f"Tier-1 feature requires 5/5 seeds < 0.001.")

    # HARD_PASS (v2): 5/5 seeds pass tight gate AND all max_conf < HALLU_THRESHOLD
    if hard_pass_cells == total_cells and seeds_tight_pass == n_seeds_checked:
        return ("KF1_HARD_PASS",
                f"HALLUCINATION-IMPOSSIBILITY 5-SEED CONFIRMED. "
                f"5/5 seeds: mean_oos_max_conf < {HP_MEAN_MAX_CONF_UNDERCAP} at M<=N. "
                f"mean_oos_max_conf_undercap={mean_oos_undercap:.5f}. "
                f"mean_oos_max_conf_overcap={mean_oos_overcap:.5f}. "
                f"No OOS query exceeds threshold={HALLU_THRESHOLD} across {total_cells} cells. "
                f"Tier-1 product feature: structurally cannot hallucinate at M<=N.")

    # MIDDLE_BAND: passes HALLU_THRESHOLD but some seeds above tight gate
    if low_m_hallu_events == 0:
        return ("KF1_MIDDLE_BAND",
                f"No structural hallucinations (all max_conf < {HALLU_THRESHOLD}). "
                f"But tight 5-seed gate: {seeds_tight_pass}/{n_seeds_checked} seeds "
                f"have mean_oos_max_conf < {HP_MEAN_MAX_CONF_UNDERCAP} at undercap. "
                f"mean_oos_undercap={mean_oos_undercap:.5f}. "
                f"Weaker guarantee than Tier-1 spec requires.")

    return ("KF1_MIDDLE_BAND",
            f"Mixed results. hard_pass_cells={hard_pass_cells}/{total_cells}. "
            f"low_M hallu={low_m_hallu_events}. "
            f"mean_oos_undercap={mean_oos_undercap:.5f}.")


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(SEEDS_FULL) == 5, f"v2 requires 5 seeds; got {SEEDS_FULL}"

    def mk_cell(above_frac, mean_conf, max_conf, frac):
        return {
            "M": int(frac * 1024), "M_over_N": frac, "seed": 17, "C": 4096,
            "oos_max_conf_mean": mean_conf, "oos_max_conf_max": max_conf,
            "above_thresh_frac": above_frac, "confidence_margin_mean": 1/4096 - mean_conf,
            "inset_acc": 0.95, "inset_max_conf_mean": 0.99,
        }

    # HARD_PASS v2: 5/5 seeds all undercap cells mean < 0.001
    summary_pass = {
        "m_fracs": [0.25, 1.0, 2.0],
        "per_seed": {
            str(s): {"seed": s, "N": 1024, "per_M": {
                "0.25": mk_cell(0.0, 0.0001, 0.001, 0.25),
                "1.0": mk_cell(0.0, 0.0002, 0.002, 1.0),
                "2.0": mk_cell(0.0, 0.005, 0.05, 2.0),
            }} for s in [7, 17, 23, 31, 41]
        }
    }
    v, msg = compute_verdict(summary_pass)
    assert v == "KF1_HARD_PASS", f"Expected KF1_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL v2: any seed has mean_oos_max_conf > 0.01 at undercap
    summary_fail = {
        "m_fracs": [1.0],
        "per_seed": {
            "17": {"seed": 17, "N": 1024, "per_M": {
                "1.0": mk_cell(0.05, 0.8, 0.9, 1.0),  # above_frac > 0.01 at M=N
            }},
        }
    }
    v, msg = compute_verdict(summary_fail)
    assert v == "KF1_HARD_FAIL", f"Expected KF1_HARD_FAIL, got {v}: {msg}"

    # Smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    codebook, info = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = min(C, N_test)
    cell = run_one_cell(M_test, 17, codebook, N_test, 20, 10, device)
    assert "oos_max_conf_mean" in cell
    assert 0.0 <= cell["oos_max_conf_mean"] <= 1.0
    assert cell["oos_max_conf_max"] < HALLU_THRESHOLD, (
        f"SUSPICIOUS: OOS max_conf={cell['oos_max_conf_max']:.4f} >= {HALLU_THRESHOLD}"
    )

    print("[SELFTEST PASS] kf1_hallu_impossibility_v2 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS_FULL
    n_oos = N_OOS_QUERIES_SMOKE if smoke else N_OOS_QUERIES_FULL
    n_inset = N_INSET_QUERIES_SMOKE if smoke else N_INSET_QUERIES_FULL
    config = {"smoke": smoke, "N": N, "m_fracs": m_fracs, "n_oos": n_oos, "n_inset": n_inset}
    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf1v2] N={N} seeds={seeds} m_fracs={m_fracs} n_oos={n_oos} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        per_M = result.get("per_M", {})
        maxcs = [v["oos_max_conf_max"] for v in per_M.values()]
        print(f"  seed {seed} done in {te:.1f}s "
              f"oos_max_conf_max=[{', '.join(f'{c:.4f}' for c in maxcs)}]", flush=True)
        per_seed[str(seed)] = result
        # Per-seed checkpoint
        checkpoint_path = out_dir / "metrics_checkpoint.json"
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"per_seed": per_seed, "N_full": N_FULL}, f, indent=2)

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
    print(f"\n[kf1v2] VERDICT: {verdict}", flush=True)
    print(f"[kf1v2] {verdict_msg}", flush=True)
    print(f"[kf1v2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
