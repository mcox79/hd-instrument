"""KF-1 HALLUCINATION-IMPOSSIBILITY Rescue v4: N=8192 BSC-codebook substitute.

PARENT: exp_kf1_hallu_rescue_v3_n8192.py (v3 FAILED wall_s=2.8 SCRIPT_PRECONDITION_VIOLATION)
  v3 attempted N=8192 but loaded kf1_tier1_rescue_v1_n4096 which calls
  make_kerdock_4coset_codebook(N=8192). N=8192 log2=13 (odd) -> ValueError.
  v4 FIX: replace Kerdock codebook with BSC random codebook (random +/-1 atoms).
  BSC is valid at any N including N=8192.

SCIENTIFIC QUESTION:
  Does KF-1 hallucination-detection hold at N=8192 with BSC codebook?
  Specifically: does above_thresh_frac=0 persist at N=8192 for all seeds, all M_fracs?
  This replicates v2 (N=4096 HARD_PASS) at N=8192 using BSC instead of Kerdock.

  BSC CODEBOOK NOTE: With BSC atoms, C=4*N=32768 random vectors at N=8192.
  BSC is NOT equidistant (unlike Kerdock). OOS keys will have small cosine similarity
  to W (sub-Gaussian noise ~1/sqrt(N)). The impossibility property should hold
  even more strongly with BSC because there is no structured codebook to exploit.

PRE-REGISTERED BANDS:
  Prior anchor: v2 N=4096 KF1T1_HARD_PASS (above_thresh_frac=0 all seeds, Kerdock).
  NOTE: BSC has same or weaker near-uniform property than Kerdock (BSC is random,
  Kerdock is structured). Bands identical to v2/v3 (applying same Tier-1 claim).

  HARD_PASS: (a) above_thresh_frac=0 in ALL 5 seeds at M <= N
    AND (b) mean_oos_max_conf <= 10/C in >= 4/5 seeds at M <= N
    AND max_oos_max_conf < 50/C.
    C = 4*N = 32768 at N=8192.
    Interpretation: KF-1 N-axis replication at N=8192 confirmed with BSC codebook.
  HARD_FAIL: any seed shows above_thresh_frac > 0 at M <= N.
  MIDDLE_BAND: above_thresh_frac=0 but near-uniform bound exceeded in >1 seed.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding): _n8192 suffix.
  2. C = 4*N = 32768. 1/C = 3.052e-5. 10/C = 3.052e-4. 50/C = 1.526e-3.
  3. BSC codebook: C random +/-1 vectors, shape (C, N).
  4. above_thresh_frac=0 in all seeds -> HARD_PASS (part a).
  5. OOM: W float32 at N=8192 = 8192*8192*4 = 268MB. Codebook=32768*8192*4=1GB.
     TOTAL ~1.3GB. Under 6GB GPU limit. OK.

KERDOCK AUDIT: SAFE -- no make_kerdock_4coset_codebook call in this script.
BSC codebook replaces Kerdock entirely.

TIMEOUT ESTIMATE:
  v2 at N=4096 elapsed ~5-10s. N=8192: (8192/4096)^1.5 = 2.83x (matrix ops).
  Codebook at N=8192 C=32768: 32768*8192*4=1GB -> may slow down sims computation.
  Estimate: 10 * 2.83 * 3 = 85s. Safety 30x: 2550s.
  Floor _n8192 = 21600. timeout_s = 21600.

OOM CHECK: 1.3GB total. Under 6GB. OK.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf1_hallu_rescue_v4_n8192_bsc
Queue: overnight_queue (GPU; N=8192 5-seed BSC-codebook KF-1 Tier-1 N-axis replication)
Pre-reg: preregs/2026-05-29_kf1_hallu_rescue_v4_n8192_bsc.md
Parent: kf1_hallu_rescue_v2_n4096 (HARD_PASS at N=4096); v3_n8192 (BLOCKED by Kerdock-even-log2)
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
from typing import Dict

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v2 (kf1_hallu_impossibility_v2) for store_facts_outer (W construction)
_v2_path = REPO / "experiments" / "exp_kf1_hallu_impossibility_v2.py"
spec2 = importlib.util.spec_from_file_location("kf1v2_v4bsc", _v2_path)
v2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v2)

store_facts_outer = v2.store_facts_outer

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192    # PROT-018 binding contract; also ensures BSC codebook works (no log2 restriction)
N_SMOKE = 1024    # BSC valid at any N

assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACTIONS_FULL  = [0.25, 0.50, 1.0]    # UNDERCAP only (M <= N)
M_FRACTIONS_SMOKE = [0.25, 1.0]

N_OOS_FULL  = 1000
N_OOS_SMOKE = 100
N_INSET_FULL  = 200
N_INSET_SMOKE = 30

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HALLU_THRESHOLD = 0.5
BETA_INF = 32.0

# BSC codebook: C = 4*N random +/-1 vectors
BSC_CODEBOOK_SCALE = 4   # C = BSC_CODEBOOK_SCALE * N


def make_bsc_codebook(N: int, device: torch.device, seed: int = 0) -> torch.Tensor:
    """Generate C = 4*N random BSC (+/-1) patterns of dimension N."""
    C = BSC_CODEBOOK_SCALE * N
    gen = torch.Generator(device="cpu").manual_seed(seed + 999999)  # fixed seed for codebook
    raw = torch.randint(0, 2, (C, N), generator=gen).float() * 2 - 1  # +/-1
    return raw.to(device)


def get_output_dir(default_name: str = "kf1_hallu_rescue_v4_n8192_bsc") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run one seed: per-M analysis of OOS max confidence with BSC codebook."""
    smoke = config["smoke"]
    N = config["N"]
    m_fracs = config["m_fracs"]
    n_oos = config["n_oos"]
    n_inset = config["n_inset"]

    # Build BSC codebook (C = 4*N, random +/-1); NOT Kerdock
    codebook = make_bsc_codebook(N, device)  # (C, N)
    C = codebook.shape[0]

    gen = torch.Generator(device="cpu").manual_seed(seed)
    per_M = {}

    for mf in m_fracs:
        M = int(mf * N)

        # Sample M keys from codebook (with replacement if M > C)
        key_idx = torch.randint(0, C, (M,), generator=gen)
        keys = codebook[key_idx].to(device)
        values = codebook[torch.randint(0, C, (M,), generator=gen)].to(device)

        W = store_facts_outer(keys, values, N)

        # OOS probes: draw keys NOT in key_idx set
        used_set = set(key_idx.tolist())
        available = [i for i in range(C) if i not in used_set]
        if len(available) < n_oos:
            oos_idx = torch.randint(0, C, (n_oos,), generator=gen)
        else:
            oos_idx = torch.tensor(
                [available[i % len(available)] for i in range(n_oos)],
                dtype=torch.long
            )
        oos_keys = codebook[oos_idx].to(device)

        # Inference: W @ q -> softmax similarities
        q = oos_keys @ W.T      # (n_oos, N)
        sims = (codebook @ q.T) / N  # (C, n_oos) -- normalize by N for BSC
        P = torch.softmax(BETA_INF * sims, dim=0)  # (C, n_oos)
        max_conf = P.max(dim=0).values  # (n_oos,)

        above_thresh_frac = (max_conf >= HALLU_THRESHOLD).float().mean().item()
        oos_max_conf_mean = max_conf.mean().item()
        oos_max_conf_max = max_conf.max().item()

        bound_10x = 10.0 / C
        bound_50x = 50.0 / C
        near_uniform_mean = oos_max_conf_mean <= bound_10x
        near_uniform_max = oos_max_conf_max < bound_50x

        # Inset probes
        inset_idx_list = key_idx[:min(n_inset, M)].tolist()
        if len(inset_idx_list) > 0:
            inset_keys = codebook[torch.tensor(inset_idx_list, dtype=torch.long)].to(device)
            q_in = inset_keys @ W.T
            sims_in = (codebook @ q_in.T) / N
            P_in = torch.softmax(BETA_INF * sims_in, dim=0)
            inset_acc = (P_in.argmax(dim=0) == torch.tensor(
                inset_idx_list, dtype=torch.long, device=device
            )).float().mean().item()
            inset_max_conf_mean = P_in.max(dim=0).values.mean().item()
        else:
            inset_acc = float("nan")
            inset_max_conf_mean = float("nan")

        per_M[str(mf)] = {
            "M": M,
            "M_over_N": mf,
            "C": C,
            "oos_max_conf_mean": round(oos_max_conf_mean, 8),
            "oos_max_conf_max": round(oos_max_conf_max, 8),
            "above_thresh_frac": round(above_thresh_frac, 8),
            "near_uniform_mean": near_uniform_mean,
            "near_uniform_max": near_uniform_max,
            "bound_10x": round(bound_10x, 8),
            "bound_50x": round(bound_50x, 8),
            "ratio_to_uniform_mean": round(oos_max_conf_mean * C, 4),
            "inset_acc": inset_acc,
            "inset_max_conf_mean": inset_max_conf_mean,
        }
        print(f"    mf={mf} M={M} above_thresh={above_thresh_frac:.4f} "
              f"oos_mean={oos_max_conf_mean:.4e} ratio={oos_max_conf_mean*C:.2f}x", flush=True)

    return {"seed": seed, "N": N, "per_M": per_M, "codebook_type": "BSC"}


def compute_verdict(summary: dict) -> tuple:
    """Compute KF1 v4 BSC verdict (same Tier-1 claim as v2/v3)."""
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF1V4_INCONCLUSIVE", "No per-seed data.")

    n_seeds = len(per_seed)
    undercap_fracs = [f for f in M_FRACTIONS_FULL if f <= 1.0]

    any_hallu = False
    seeds_near_uniform = 0
    all_max_within_50x = True
    ratios = []

    for seed_key, seed_data in per_seed.items():
        per_M = seed_data.get("per_M", {})
        seed_near_uniform = True
        for mf_key, cell in per_M.items():
            mf = float(mf_key)
            if mf > 1.0:
                continue
            if cell["above_thresh_frac"] > 0:
                any_hallu = True
            if not cell["near_uniform_mean"]:
                seed_near_uniform = False
            if not cell["near_uniform_max"]:
                all_max_within_50x = False
            ratios.append(cell["ratio_to_uniform_mean"])
        if seed_near_uniform:
            seeds_near_uniform += 1

    mean_ratio = sum(ratios) / len(ratios) if ratios else float("nan")

    if any_hallu:
        return ("KF1V4_BSC_HARD_FAIL",
                f"Hallucination detected: above_thresh_frac > 0 at M <= N. "
                f"KF-1 fails at N=8192 BSC. mean_ratio={mean_ratio:.2f}x.")

    if seeds_near_uniform >= 4 and all_max_within_50x:
        return ("KF1V4_BSC_HARD_PASS",
                f"KF-1 Tier-1 PASSES at N=8192 BSC. "
                f"(a) above_thresh_frac=0 all {n_seeds} seeds. "
                f"(b) {seeds_near_uniform}/{n_seeds} seeds near-uniform (mean<=10/C). "
                f"max_max_conf < 50/C. mean_ratio={mean_ratio:.2f}x. "
                f"KF-1 N-axis replication confirmed (BSC codebook).")

    return ("KF1V4_BSC_MIDDLE_BAND",
            f"Zero hallucinations but near-uniform weak. "
            f"{seeds_near_uniform}/{n_seeds} seeds within 10/C; "
            f"50x max bound {'OK' if all_max_within_50x else 'VIOLATED'}. "
            f"mean_ratio={mean_ratio:.2f}x.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: C formula
    C = BSC_CODEBOOK_SCALE * N_FULL
    assert C == 32768, f"C at N=8192: {C}"
    bound_10x = 10.0 / C
    assert abs(bound_10x - 3.052e-4) < 1e-5, f"bound_10x at N=8192: {bound_10x:.6e}"

    # Self-test 2: BSC codebook construction
    device = torch.device("cpu")
    cb_smoke = make_bsc_codebook(N_SMOKE, device)  # (4*N_SMOKE, N_SMOKE)
    C_smoke = BSC_CODEBOOK_SCALE * N_SMOKE
    assert cb_smoke.shape == (C_smoke, N_SMOKE), f"BSC codebook shape: {cb_smoke.shape}"
    assert torch.all((cb_smoke == 1.0) | (cb_smoke == -1.0)), "BSC values must be +/-1"

    # Self-test 3: forward pass at smoke scale
    cfg = {
        "smoke": True,
        "N": N_SMOKE,
        "m_fracs": M_FRACTIONS_SMOKE,
        "n_oos": N_OOS_SMOKE,
        "n_inset": N_INSET_SMOKE,
    }
    result = run_one_seed(17, cfg, device)
    per_M = result["per_M"]
    assert len(per_M) > 0, "per_M empty"
    for mf_key, cell in per_M.items():
        assert "above_thresh_frac" in cell, f"missing above_thresh_frac at mf={mf_key}"
        assert cell["above_thresh_frac"] is not None, f"above_thresh_frac is None"
        atf = cell["above_thresh_frac"]
        assert isinstance(atf, float), f"above_thresh_frac type: {type(atf)}"

    # Self-test 4: verdict gates
    # HP case: zero hallucinations, near-uniform
    hp_per_seed = {
        str(s): {"per_M": {
            "0.25": {"above_thresh_frac": 0.0, "near_uniform_mean": True, "near_uniform_max": True, "ratio_to_uniform_mean": 2.5},
            "0.5":  {"above_thresh_frac": 0.0, "near_uniform_mean": True, "near_uniform_max": True, "ratio_to_uniform_mean": 3.0},
            "1.0":  {"above_thresh_frac": 0.0, "near_uniform_mean": True, "near_uniform_max": True, "ratio_to_uniform_mean": 3.5},
        }}
        for s in SEEDS_FULL
    }
    v, msg = compute_verdict({"per_seed": hp_per_seed})
    assert "HARD_PASS" in v, f"HP gate: {v}: {msg}"

    # HF case: hallucination
    hf_per_seed = {
        str(s): {"per_M": {
            "0.25": {"above_thresh_frac": 0.1, "near_uniform_mean": False, "near_uniform_max": False, "ratio_to_uniform_mean": 50.0},
        }}
        for s in SEEDS_FULL
    }
    v, msg = compute_verdict({"per_seed": hf_per_seed})
    assert "HARD_FAIL" in v, f"HF gate: {v}: {msg}"

    # Self-test 5: OOM check
    oom_bytes = N_FULL * N_FULL * 4 + BSC_CODEBOOK_SCALE * N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: {oom_bytes:.2e}"

    # Self-test 6: multi-scale smoke (N_SMOKE * 4)
    cb_4x = make_bsc_codebook(N_SMOKE * 4, device)
    assert cb_4x.shape == (BSC_CODEBOOK_SCALE * N_SMOKE * 4, N_SMOKE * 4), f"4x cb shape: {cb_4x.shape}"

    print(f"[selftest] kf1_hallu_rescue_v4_n8192_bsc PASS "
          f"N_FULL={N_FULL} C={C} "
          f"smoke_mfs={list(per_M.keys())} "
          f"above_thresh_sample={list(per_M.values())[0]['above_thresh_frac']:.4f} "
          f"OOM_bytes={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS_FULL
    n_oos = N_OOS_SMOKE if smoke else N_OOS_FULL
    n_inset = N_INSET_SMOKE if smoke else N_INSET_FULL

    print(f"[kf1v4] BSC-CODEBOOK N={N} seeds={seeds} m_fracs={m_fracs} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)
    t0 = time.time()
    out_dir = get_output_dir()

    config = {
        "smoke": smoke, "N": N, "m_fracs": m_fracs,
        "n_oos": n_oos, "n_inset": n_inset,
    }
    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        per_M = result.get("per_M", {})
        print(f"  seed {seed}: {te:.1f}s cells={list(per_M.keys())}", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "smoke": smoke,
        "codebook_type": "BSC",
        "bsc_codebook_scale": BSC_CODEBOOK_SCALE,
    }

    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)

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

    print(f"\n[kf1v4] VERDICT: {verdict}", flush=True)
    print(f"[kf1v4] {verdict_msg}", flush=True)
    print(f"[kf1v4] elapsed={elapsed}s output={out_path}", flush=True)


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
