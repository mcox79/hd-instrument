"""Bet 2 v4 - 8-coset Kerdock MM codebook, M_stored up to 8N.

v3 validated Mirage protection through M=4N=16384 with 4 cosets. v4
extends to 8 cosets (b values {0, 1, alpha, alpha^2, ..., alpha^6} from
GF(2^t)). All C(8,2)=28 pairwise differences are nonzero distinct GF
elements, so all 28 cross-coset XOR quadratics are bent (Welch bound).

M_stored sweep: {N, 2N, 4N, 6N, 8N} = {4096, 8192, 16384, 24576, 32768}.

At M=8N the substrate is 8x over-capacity; Kerdock's cross-talk bound
holds by construction but W can't actually store 32K facts in an N*N
matrix of rank <= N. kept_preservation may degrade before erase-side
probes fail.

Pre-reg: preregs/2026-05-21_wave14ya_erase_kerdock_v4.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec1 = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(v1)

_v2_path = REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py"
spec2 = importlib.util.spec_from_file_location("kerdock_v2", _v2_path)
v2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v2)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = [4096, 8192, 16384, 24576, 32768]
M_STORED_SMOKE = [1024, 4096, 8192]
N_ERASE_FULL = 30
N_ERASE_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 10
N_PARAPHRASE = 20
HAMMING_RADII_FULL = [4, 8, 16]
HAMMING_RADII_SMOKE = [8]
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0
NUM_COSETS = 8

PASS_ARGMAX = v3.PASS_ARGMAX
PASS_RANK_FRAC = v3.PASS_RANK_FRAC
PASS_NORM = v3.PASS_NORM
PASS_PARAPHRASE = v3.PASS_PARAPHRASE
PASS_KEPT = v3.PASS_KEPT


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def make_kerdock_8coset_codebook(N: int, device: torch.device) -> tuple[torch.Tensor, dict]:
    """Extend v3.make_kerdock_4coset_codebook to 8 cosets.

    b values: {0, 1, alpha, alpha^2, alpha^3, alpha^4, alpha^5, alpha^6}.
    For GF(2^5): period 31, so all 8 powers are distinct.
    For GF(2^6): period 63, so all 8 powers are distinct.
    """
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N:
        raise ValueError(f"N={N} must be power of 2")
    if n_log2 % 2 != 0:
        raise ValueError(f"N={N} requires even log2(N) for MM construction "
                         f"(got n_log2={n_log2})")
    t = n_log2 // 2

    log_tab, antilog_tab = v3.build_gf2t_tables(t)
    H = v1.sylvester_hadamard(n_log2, device)

    # b values: 0, then alpha^0, alpha^1, ..., alpha^(NUM_COSETS-2)
    # antilog_tab[i] = alpha^i for i in 0..period-1.
    period = (1 << t) - 1
    if NUM_COSETS - 1 > period:
        raise ValueError(f"NUM_COSETS-1={NUM_COSETS-1} exceeds GF(2^{t}) period {period}")
    b_values = [0] + [antilog_tab[i] for i in range(NUM_COSETS - 1)]

    # Verify all b values are distinct (MM property requires this)
    if len(set(b_values)) != len(b_values):
        raise ValueError(f"b_values not distinct: {b_values}")

    cosets = []
    for b in b_values:
        q_b = v3.build_q_b_signs(b, N, t, log_tab, antilog_tab, device)
        coset = H * q_b.unsqueeze(0)
        cosets.append(coset)
    codebook = torch.cat(cosets, dim=0)  # (NUM_COSETS * N, N)

    info = {
        "t": t,
        "primitive_poly": bin(v3.PRIMITIVE_POLY[t]),
        "b_values": b_values,
        "n_cosets": len(b_values),
        "codebook_size": codebook.shape[0],
    }
    return codebook, info


def cell_passes(row: dict) -> tuple[bool, list[str]]:
    return v3.cell_passes(row)


def compute_verdict(summary: dict) -> tuple[str, str]:
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("KERDOCK_V4_INCONCLUSIVE", "Missing per-arm data.")
    N = summary.get("N", N_FULL)
    kerdock_rows = arms["kerdock"].get("per_M", [])
    correlated_rows = arms["correlated"].get("per_M", [])
    if not kerdock_rows or not correlated_rows:
        return ("KERDOCK_V4_INCONCLUSIVE", "Empty per-M rows.")

    kerdock_pass = {r["M_stored"]: cell_passes(r) for r in kerdock_rows}
    corr_pass = {r["M_stored"]: cell_passes(r) for r in correlated_rows}
    ms_sorted = sorted(kerdock_pass.keys())

    if all(corr_pass[m][0] for m in ms_sorted):
        return ("KERDOCK_V4_CORRELATED_PASSES",
                f"Correlated arm passes all probes at every tested M_stored. "
                f"Audit setup.")

    largest_kerdock_pass = max((m for m in ms_sorted if kerdock_pass[m][0]),
                                  default=None)
    first_kerdock_fail = next((m for m in ms_sorted if not kerdock_pass[m][0]),
                                 None)

    if first_kerdock_fail is not None and first_kerdock_fail <= 4 * N:
        return ("KERDOCK_V4_REGRESSES_BELOW_V3",
                f"Kerdock arm fails at M_stored={first_kerdock_fail} <= 4N. "
                f"This contradicts v3's EXTENDS_TO_4N verdict. Audit.")

    if first_kerdock_fail is None:
        return ("KERDOCK_V4_EXTENDS_TO_8N",
                f"Kerdock arm passes at all M_stored in {ms_sorted} (up to "
                f"{max(ms_sorted)} = {max(ms_sorted)/N:.2f}*N). Correlated arm "
                f"fails as expected. Welch-bound structured codebook extends "
                f"Mirage protection through 8N=32768 at N={N}; substrate is "
                f"8x over-capacity but kept_preservation holds.")

    return (f"KERDOCK_V4_DECAYS_AT_{first_kerdock_fail}",
            f"Kerdock arm holds up to M_stored={largest_kerdock_pass}; fails at "
            f"M_stored={first_kerdock_fail} (= {first_kerdock_fail/N:.2f}*N) with: "
            f"{'; '.join(kerdock_pass[first_kerdock_fail][1])}. Envelope sized at "
            f"M_stored={largest_kerdock_pass} (= {largest_kerdock_pass/N:.2f}*N).")


def self_test_verdict() -> None:
    N_test = 4096

    def mk_row(M, args):
        rank_default = max(2.0, M * PASS_RANK_FRAC * 2)
        return {"M_stored": M,
                "argmax_leak": args.get("a", 0.02),
                "mean_rank": args.get("r", rank_default),
                "norm_ratio": args.get("n", 0.05),
                "paraphrase_leak_h8": args.get("p", 0.02),
                "kept_preservation": args.get("k", 0.98)}

    pass_args = {}
    fail_args = {"a": 0.20}
    kept_fail_args = {"k": 0.85}

    ms = [4096, 8192, 16384, 24576, 32768]
    cases = [
        # 1. EXTENDS_TO_8N: all pass
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in ms]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V4_EXTENDS_TO_8N"),
        # 2. DECAYS at 24576 (6N): kept_preservation cliff
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(4096, pass_args), mk_row(8192, pass_args),
                                    mk_row(16384, pass_args), mk_row(24576, kept_fail_args),
                                    mk_row(32768, kept_fail_args)]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V4_DECAYS_AT_24576"),
        # 3. REGRESSES below v3 (fails at 4N)
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(4096, pass_args), mk_row(8192, pass_args),
                                    mk_row(16384, fail_args), mk_row(24576, fail_args),
                                    mk_row(32768, fail_args)]},
            "correlated": {"per_M": [mk_row(m, fail_args) for m in ms]}}},
         "KERDOCK_V4_REGRESSES_BELOW_V3"),
        # 4. CORRELATED_PASSES
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in ms]},
            "correlated": {"per_M": [mk_row(m, pass_args) for m in ms]}}},
         "KERDOCK_V4_CORRELATED_PASSES"),
        # 5. INCONCLUSIVE
        ({"N": N_test, "by_arm": {}}, "KERDOCK_V4_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, msg = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected} msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def sample_kerdock_keys(codebook, n_keys, cpu_gen, device):
    return v3.sample_kerdock_keys(codebook, n_keys, cpu_gen, device)


def run_arm(arm_name, codebook, M_stored_list, config, device):
    """Reuse v3.run_arm structure (functionally identical)."""
    N = config["N"]
    n_erase = config["n_erase"]
    n_kept = config["n_kept_probe"]
    hamming = config["hamming_radii"]
    n_para = config["n_paraphrase"]
    seeds = config["seeds"]

    per_M = []
    for M_stored in M_stored_list:
        per_seed = []
        for seed in seeds:
            gen = torch.Generator(device=device).manual_seed(seed)
            cpu_gen = torch.Generator().manual_seed(seed + 1009)

            if codebook is not None:
                keys = sample_kerdock_keys(codebook, M_stored, cpu_gen, device)
            else:
                rank_L = max(2, int(M_stored * 0.25))
                keys = v1.make_correlated_keys(M_stored, N, rank_L, gen, device)

            values = 2.0 * (torch.rand((M_stored, N), generator=gen,
                                          device=device) > 0.5).float() - 1.0
            W = (values.T @ keys) / N

            erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
            kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
            erase_idx = sorted(torch.randperm(M_stored, generator=erase_gen)[:n_erase].tolist())
            erase_set = set(erase_idx)
            candidates = [i for i in range(M_stored) if i not in erase_set]
            n_kept_actual = min(n_kept, len(candidates))
            kept_idx = sorted(torch.tensor(candidates)[torch.randperm(
                len(candidates), generator=kept_gen)[:n_kept_actual]].tolist())

            W_edit = W.clone()
            for i in erase_idx:
                W_edit = v1.antihebbian_erase(W_edit, keys[i], ALPHA)

            probe = v2.multi_probe_with_snap(W_edit, keys, values, erase_idx, kept_idx,
                                                hamming, n_para, codebook, cpu_gen, device)
            probe["seed"] = seed
            per_seed.append(probe)

        def avg(k):
            vals = [r[k] for r in per_seed if k in r]
            return sum(vals) / len(vals) if vals else 0.0

        row = {"M_stored": M_stored,
                "argmax_leak": avg("argmax_leak"),
                "mean_rank": avg("mean_rank"),
                "norm_ratio": avg("norm_ratio"),
                "cosine": avg("cosine"),
                "kept_preservation": avg("kept_preservation"),
                "per_seed": per_seed}
        for h in hamming:
            row[f"paraphrase_leak_h{h}"] = avg(f"paraphrase_leak_h{h}")
        per_M.append(row)

    return {"per_M": per_M}


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored_list": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_erase": N_ERASE_SMOKE if smoke else N_ERASE_FULL,
        "n_kept_probe": N_KEPT_PROBE_SMOKE if smoke else N_KEPT_PROBE_FULL,
        "n_paraphrase": N_PARAPHRASE,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alpha": ALPHA,
        "num_cosets": NUM_COSETS,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building 8-coset MM codebook at N={config['N']}...", flush=True)
    codebook, info = make_kerdock_8coset_codebook(config["N"], device)
    print(f"[codebook] {info}", flush=True)

    # Codebook self-checks
    N = config["N"]
    book_ips = (codebook @ codebook.T) / N
    book_mask = ~torch.eye(codebook.size(0), dtype=torch.bool, device=device)
    book_max_abs = float(book_ips[book_mask].abs().max())
    n_cosets = info["n_cosets"]
    within_max = 0.0
    for c in range(n_cosets):
        coset = codebook[c * N:(c + 1) * N]
        ips = (coset @ coset.T) / N
        mask = ~torch.eye(N, dtype=torch.bool, device=device)
        within_max = max(within_max, float(ips[mask].abs().max()))
    print(f"[codebook] book_max_abs={book_max_abs:.6f}  "
          f"within_coset_max={within_max:.6f}  "
          f"welch_bound=1/sqrt(N)={1.0/math.sqrt(N):.6f}", flush=True)

    print(f"[arm=kerdock] running...", flush=True)
    arm_k = run_arm("kerdock", codebook, config["M_stored_list"], config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = run_arm("correlated", None, config["M_stored_list"], config, device)

    summary = {
        "N": config["N"],
        "by_arm": {"kerdock": arm_k, "correlated": arm_c},
        "codebook_stats": {
            "size": codebook.shape[0],
            "info": info,
            "book_max_abs_ip": book_max_abs,
            "within_coset_max": within_max,
            "expected_welch_bound": 1.0 / math.sqrt(N),
        },
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm_data in summary["by_arm"].items():
        print(f"[{arm_name}]", flush=True)
        for row in arm_data["per_M"]:
            paras = " ".join(f"p_h{h}={row[f'paraphrase_leak_h{h}']:.3f}"
                              for h in config["hamming_radii"])
            print(f"  M={row['M_stored']:5d}  argmax={row['argmax_leak']:.3f}  "
                  f"rank={row['mean_rank']:.1f}  norm={row['norm_ratio']:.3f}  "
                  f"{paras}  kept={row['kept_preservation']:.3f}", flush=True)

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
    out_dir = get_output_dir("wave14ya_erase_kerdock_v4_smoke")
    log_event("experiment_started", name="wave14ya_erase_kerdock_v4", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    N = config["N"]
    expected = 1.0 / math.sqrt(N)
    max_abs = summary["codebook_stats"]["book_max_abs_ip"]
    oracle.assert_in_range("kerdock_v4_welch_bound", max_abs,
                            (expected * 0.95, expected * 1.05))
    within = summary["codebook_stats"]["within_coset_max"]
    if within > 1e-5:
        raise AssertionError(
            f"SANITY FAIL [within_coset]: max within-coset IP = {within:.6f} > 1e-5")

    codebook, _ = make_kerdock_8coset_codebook(N, torch.device("cpu"))
    sample = codebook[:5]
    snapped = v2.snap_to_codebook_batch(sample, codebook)
    if not torch.equal(snapped, sample):
        raise AssertionError("SANITY FAIL [snap_identity]: snap(c) != c")

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14ya_erase_kerdock_v4",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14ya_erase_kerdock_v4")
    log_event("experiment_started", name="wave14ya_erase_kerdock_v4", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14ya_erase_kerdock_v4",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
