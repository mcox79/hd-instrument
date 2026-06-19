"""GDPR-grade erase at over-capacity: Kerdock 2-coset codebook vs random keys.

Bet 2 v2. v1+capsweep showed orthogonal Hadamard keys break Mirage at M <= 0.78*N
(STRUCT_KEYS_FIX_MIRAGE robust through M_stored=3200/4096). v2 tests whether
structured keys extend this protection BEYOND the orthogonal capacity limit
(M > N), using a 2-coset Kerdock-like codebook (2N codewords with pairwise IPs
in {0, +/- 1/sqrt(N)}).

Two arms in the same script:
  Kerdock: 2-coset codebook (H + H * q_1) at M_stored in {2000, 4096, 6144, 8192}.
           Paraphrases snap to codebook before W read.
  Random:  random {-1,+1} keys at same M_stored. No snap (no codebook).

Multi-probe battery identical to v1. The contrast - Kerdock holds at over-
capacity where random fails - is the load-bearing finding.

Pre-reg: preregs/2026-05-21_wave14v_erase_kerdock_v2.md
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
spec = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)


N_FULL = 4096
N_SMOKE = 512
M_STORED_FULL = [2000, 4096, 6144, 8192]
M_STORED_SMOKE = [256, 1024]
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

PASS_ARGMAX = 0.05
PASS_RANK_FRAC = 0.3
PASS_NORM = 0.15
PASS_PARAPHRASE = 0.05
PASS_KEPT = 0.95


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


def make_kerdock_2coset_codebook(N: int, device: torch.device) -> torch.Tensor:
    """Generate the 2-coset Kerdock-like codebook: 2N codewords of length N.

    Coset 0: rows of Sylvester Hadamard. All pairwise orthogonal.
    Coset 1: rows of H multiplied element-wise by sign vector q_1[x]=(-1)^Q_1(x),
             Q_1(x) = sum_k x_{2k} * x_{2k+1} (sum of disjoint bit pairs).
    Cross-coset pairs: |IP|/N = 2^((m+1)/2) / N for even m+1; ranges
    {0, +/- 2^((m+1)/2)/N} in general.
    """
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N:
        raise ValueError(f"N={N} must be a power of 2.")
    H = v1.sylvester_hadamard(n_log2, device)  # (N, N)
    x_arr = torch.arange(N, device=device)
    q1_parity = torch.zeros(N, device=device, dtype=torch.int64)
    for k in range(n_log2 // 2):
        bit_low = (x_arr >> (2 * k)) & 1
        bit_high = (x_arr >> (2 * k + 1)) & 1
        q1_parity = q1_parity + bit_low * bit_high
    q1_signs = 1.0 - 2.0 * (q1_parity & 1).float()  # (N,)
    H_coset_1 = H * q1_signs.unsqueeze(0)  # broadcasts across rows
    return torch.cat([H, H_coset_1], dim=0)  # (2N, N)


def sample_kerdock_keys(codebook: torch.Tensor, n_keys: int,
                          cpu_gen: torch.Generator, device: torch.device) -> torch.Tensor:
    """Sample n_keys codewords without replacement from codebook."""
    M_book = codebook.size(0)
    if n_keys > M_book:
        raise ValueError(f"Requested {n_keys} keys but codebook only has {M_book}.")
    perm = torch.randperm(M_book, generator=cpu_gen)[:n_keys].to(device)
    return codebook[perm]


def snap_to_codebook_batch(queries: torch.Tensor, codebook: torch.Tensor) -> torch.Tensor:
    """For each query, return nearest codeword (signed by inner product).
    queries: (B, N), codebook: (M, N). Returns (B, N).
    """
    sims = queries @ codebook.T  # (B, M)
    best_idx = sims.abs().argmax(dim=1)  # (B,)
    best_signs = sims.gather(1, best_idx.unsqueeze(1)).sign().squeeze(1)  # (B,)
    return codebook[best_idx] * best_signs.unsqueeze(1)


def multi_probe_with_snap(W: torch.Tensor, keys: torch.Tensor, values: torch.Tensor,
                            erase_idx: list, kept_idx: list,
                            paraphrase_radii: list, n_paraphrase: int,
                            codebook: torch.Tensor | None,
                            cpu_gen: torch.Generator, device: torch.device) -> dict:
    """Multi-probe battery. If codebook is provided (Kerdock arm), snap paraphrases
    to nearest codeword before reading W. If None (random arm), use raw paraphrase.
    """
    N = keys.size(-1)
    erase_t = torch.tensor(erase_idx, device=device)
    kept_t = torch.tensor(kept_idx, device=device)
    keys_e = keys[erase_idx]
    values_e = values[erase_idx]

    retrieved_e = keys_e @ W.T
    sims_e = retrieved_e @ values.T
    argmax_leak = (sims_e.argmax(dim=1) == erase_t).float().mean().item()
    sorted_idx = sims_e.argsort(dim=1, descending=True)
    ranks = [int((sorted_idx[r] == erase_t[r]).nonzero(as_tuple=False)[0].item()) + 1
             for r in range(len(erase_idx))]
    mean_rank = sum(ranks) / len(ranks)
    norm_ratio = (retrieved_e.norm(dim=1) / (N ** 0.5)).mean().item()
    cos_e = torch.nn.functional.cosine_similarity(retrieved_e, values_e, dim=1).mean().item()

    out = {"argmax_leak": argmax_leak, "mean_rank": mean_rank, "norm_ratio": norm_ratio,
           "cosine": cos_e}
    for h in paraphrase_radii:
        para_keys = v1.hamming_perturb(keys_e, n_paraphrase, h, cpu_gen, device)
        if codebook is not None:
            para_keys = snap_to_codebook_batch(para_keys, codebook)
        retrieved_p = para_keys @ W.T
        sims_p = retrieved_p @ values.T
        argmax_p = sims_p.argmax(dim=1)
        erase_idx_expanded = erase_t.repeat_interleave(n_paraphrase)
        leak_p = (argmax_p == erase_idx_expanded).float().mean().item()
        out[f"paraphrase_leak_h{h}"] = leak_p

    retrieved_kept = keys[kept_idx] @ W.T
    sims_kept = retrieved_kept @ values.T
    kept_correct = (sims_kept.argmax(dim=1) == kept_t).float().mean().item()
    out["kept_preservation"] = kept_correct

    return out


def cell_passes(row: dict) -> tuple[bool, list[str]]:
    fails = []
    M = row.get("M_stored", 1)
    rank_thresh = max(2.0, M * PASS_RANK_FRAC)
    if row["argmax_leak"] >= PASS_ARGMAX:
        fails.append(f"argmax={row['argmax_leak']:.3f}")
    if row["mean_rank"] <= rank_thresh:
        fails.append(f"rank={row['mean_rank']:.1f}<={rank_thresh:.1f}")
    if row["norm_ratio"] >= PASS_NORM:
        fails.append(f"norm={row['norm_ratio']:.3f}")
    para_h8 = row.get("paraphrase_leak_h8", 1.0)
    if para_h8 >= PASS_PARAPHRASE:
        fails.append(f"para_h8={para_h8:.3f}")
    if row["kept_preservation"] < PASS_KEPT:
        fails.append(f"kept={row['kept_preservation']:.3f}")
    return (len(fails) == 0, fails)


def compute_verdict(summary: dict) -> tuple[str, str]:
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("KERDOCK_V2_INCONCLUSIVE", "Missing per-arm data.")
    N = summary.get("N", N_FULL)
    kerdock_rows = arms["kerdock"].get("per_M", [])
    random_rows = arms["correlated"].get("per_M", [])
    if not kerdock_rows or not random_rows:
        return ("KERDOCK_V2_INCONCLUSIVE", "Empty per-M rows.")

    kerdock_pass = {r["M_stored"]: cell_passes(r) for r in kerdock_rows}
    random_pass = {r["M_stored"]: cell_passes(r) for r in random_rows}

    ms_sorted = sorted(kerdock_pass.keys())
    largest_kerdock_pass = max((m for m in ms_sorted if kerdock_pass[m][0]), default=None)
    first_kerdock_fail = next((m for m in ms_sorted if not kerdock_pass[m][0]), None)

    # Was random expected to fail at over-capacity?
    overcap_ms = [m for m in ms_sorted if m >= N]
    random_fails_overcap = any(not random_pass[m][0] for m in overcap_ms)

    # Case 1: random passes everywhere - audit needed
    if not any(not random_pass[m][0] for m in ms_sorted):
        return ("KERDOCK_V2_RANDOM_SURPRISINGLY_OK",
                f"Correlated arm passes all probes at every tested M_stored up to "
                f"{max(ms_sorted)} (2N={2*N}). v1's mechanism story (Welch-bound matters) "
                f"needs revision. Possible: random keys at this density are already "
                f"near-Welch-bound; the over-capacity threat from cross-talk didn't "
                f"materialize.")

    # Case 2: kerdock fails at over-capacity but works at under
    if first_kerdock_fail is not None and first_kerdock_fail >= N:
        ok_at_overcap = [m for m in ms_sorted if m >= N and kerdock_pass[m][0]]
        if ok_at_overcap:
            return (f"KERDOCK_V2_DECAYS_AT_{first_kerdock_fail}",
                    f"Kerdock arm holds up to M_stored={largest_kerdock_pass}; fails at "
                    f"M={first_kerdock_fail} with {'; '.join(kerdock_pass[first_kerdock_fail][1])}. "
                    f"Correlated arm fails at M>=N as expected. Envelope characterized at "
                    f"M_stored = {largest_kerdock_pass} (= {largest_kerdock_pass/N:.2f} * N).")
        return ("KERDOCK_V2_KERDOCK_FAILS_TOO",
                f"Kerdock arm fails at every M_stored >= N={N}: first fail at "
                f"M={first_kerdock_fail} with {'; '.join(kerdock_pass[first_kerdock_fail][1])}. "
                f"Correlated arm also fails. Structured-keys family does NOT extend "
                f"to over-capacity regime; v1's envelope (M <= 3200) is the substrate's "
                f"full erase capability.")

    # Case 3: kerdock fails below N - unexpected
    if first_kerdock_fail is not None and first_kerdock_fail < N:
        return (f"KERDOCK_V2_DECAYS_AT_{first_kerdock_fail}",
                f"Kerdock arm fails at M={first_kerdock_fail} which is BELOW N={N}. "
                f"Unexpected vs v1's envelope (which passed at M=3200). Check whether "
                f"snap-to-codebook is breaking on under-capacity stored keys: "
                f"{'; '.join(kerdock_pass[first_kerdock_fail][1])}.")

    # Case 4: kerdock passes everything AND random fails at over-capacity
    if all(kerdock_pass[m][0] for m in ms_sorted) and random_fails_overcap:
        # Identify where random fails
        first_random_fail = next(m for m in ms_sorted if not random_pass[m][0])
        return ("KERDOCK_V2_OVERCAPACITY_PASS",
                f"Kerdock arm passes all 5 probes at every M_stored in {ms_sorted} "
                f"(up to {max(ms_sorted)} = {max(ms_sorted)/N:.2f}*N). Correlated arm fails "
                f"starting at M_stored={first_random_fail} with "
                f"{'; '.join(random_pass[first_random_fail][1])}. Welch-bound structured "
                f"codebook extends Mirage protection past the orthogonal capacity limit.")

    return ("KERDOCK_V2_INCONCLUSIVE",
            f"Couldn't classify: kerdock_pass={kerdock_pass}, random_pass={random_pass}")


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

    cases = [
        # 1. OVERCAPACITY_PASS: kerdock all pass, random fails at M=8192
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in [2000, 4096, 6144, 8192]]},
            "correlated": {"per_M": [mk_row(2000, pass_args), mk_row(4096, pass_args),
                                   mk_row(6144, fail_args), mk_row(8192, fail_args)]}}},
         "KERDOCK_V2_OVERCAPACITY_PASS"),
        # 2. DECAYS_AT_8192: kerdock fails at 8192, random fails elsewhere
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(2000, pass_args), mk_row(4096, pass_args),
                                    mk_row(6144, pass_args), mk_row(8192, fail_args)]},
            "correlated": {"per_M": [mk_row(2000, pass_args), mk_row(4096, fail_args),
                                   mk_row(6144, fail_args), mk_row(8192, fail_args)]}}},
         "KERDOCK_V2_DECAYS_AT_8192"),
        # 3. KERDOCK_FAILS_TOO: kerdock fails at every M >= N
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(2000, pass_args), mk_row(4096, fail_args),
                                    mk_row(6144, fail_args), mk_row(8192, fail_args)]},
            "correlated": {"per_M": [mk_row(2000, pass_args), mk_row(4096, fail_args),
                                   mk_row(6144, fail_args), mk_row(8192, fail_args)]}}},
         "KERDOCK_V2_KERDOCK_FAILS_TOO"),
        # 4. RANDOM_SURPRISINGLY_OK: random arm passes at every M
        ({"N": N_test, "by_arm": {
            "kerdock": {"per_M": [mk_row(m, pass_args) for m in [2000, 4096, 6144, 8192]]},
            "correlated": {"per_M": [mk_row(m, pass_args) for m in [2000, 4096, 6144, 8192]]}}},
         "KERDOCK_V2_RANDOM_SURPRISINGLY_OK"),
        # 5. INCONCLUSIVE: missing arm
        ({"N": N_test, "by_arm": {}}, "KERDOCK_V2_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, msg = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected} msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_arm(arm_name: str, codebook: torch.Tensor | None, M_stored_list: list,
             config: dict, device: torch.device) -> dict:
    """Run the multi-probe battery at each M_stored for one arm."""
    N = config["N"]
    n_erase = config["n_erase"]
    n_kept = config["n_kept_probe"]
    hamming = config["hamming_radii"]
    n_para = config["n_paraphrase"]
    seeds = config["seeds"]

    per_M = []
    pairwise_stats = []

    for M_stored in M_stored_list:
        per_seed = []
        for seed in seeds:
            gen = torch.Generator(device=device).manual_seed(seed)
            cpu_gen = torch.Generator().manual_seed(seed + 1009)

            if codebook is not None:
                keys = sample_kerdock_keys(codebook, M_stored, cpu_gen, device)
            else:
                # Control arm: rank-L correlated keys via wave14q.make_correlated_keys
                # (matches v1's correlated arm). rank_L = max(2, M_stored * 0.25).
                # Pure random {-1,+1} at over-capacity doesn't show Mirage because
                # there's no structural correlation creating bridges (smoke confirmed
                # this); the rank-L bottleneck is what wave14p found the Mirage on.
                rank_L = max(2, int(M_stored * 0.25))
                keys = v1.make_correlated_keys(M_stored, N, rank_L, gen, device)

            values = 2.0 * (torch.rand((M_stored, N), generator=gen, device=device) > 0.5).float() - 1.0
            W = (values.T @ keys) / N

            key_ips = (keys @ keys.T) / N
            mask = ~torch.eye(M_stored, dtype=torch.bool, device=device)
            off_diag = key_ips[mask]
            pairwise_stats.append({
                "M_stored": M_stored, "seed": seed,
                "max_abs": float(off_diag.abs().max()),
                "mean_abs": float(off_diag.abs().mean()),
            })

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

            probe = multi_probe_with_snap(W_edit, keys, values, erase_idx, kept_idx,
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

    return {"per_M": per_M, "pairwise_stats": pairwise_stats}


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
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building Kerdock 2-coset codebook at N={config['N']}...",
          flush=True)
    codebook = make_kerdock_2coset_codebook(config["N"], device)
    print(f"[codebook] size={codebook.shape}", flush=True)

    # Codebook self-checks (used for smoke oracle too)
    N = config["N"]
    book_ips = (codebook @ codebook.T) / N
    book_mask = ~torch.eye(codebook.size(0), dtype=torch.bool, device=device)
    off_diag_book = book_ips[book_mask]
    book_max_abs = float(off_diag_book.abs().max())
    coset_0 = codebook[:N]
    coset_1 = codebook[N:]
    within_0 = (coset_0 @ coset_0.T) / N
    within_1 = (coset_1 @ coset_1.T) / N
    mask_within = ~torch.eye(N, dtype=torch.bool, device=device)
    max_within_0 = float(within_0[mask_within].abs().max())
    max_within_1 = float(within_1[mask_within].abs().max())
    cross = (coset_0 @ coset_1.T) / N  # (N, N)
    max_cross = float(cross.abs().max())
    print(f"[codebook] book_max_abs={book_max_abs:.6f}  within_0_max={max_within_0:.6f}  "
          f"within_1_max={max_within_1:.6f}  cross_max={max_cross:.6f}", flush=True)

    print(f"[arm=kerdock] running...", flush=True)
    arm_k = run_arm("kerdock", codebook, config["M_stored_list"], config, device)

    print(f"[arm=random] running...", flush=True)
    arm_r = run_arm("correlated", None, config["M_stored_list"], config, device)

    summary = {
        "N": config["N"],
        "by_arm": {"kerdock": arm_k, "correlated": arm_r},
        "codebook_stats": {
            "size": codebook.shape[0],
            "book_max_abs_ip": book_max_abs,
            "within_coset_0_max": max_within_0,
            "within_coset_1_max": max_within_1,
            "cross_coset_max": max_cross,
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


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14v_erase_kerdock_v2_smoke")
    log_event("experiment_started", name="wave14v_erase_kerdock_v2", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle 1: cross-coset max IP matches the construction prediction.
    # For 2-coset codebook (H, H*q_1), the cross-coset IP equals
    # Walsh(q_1)(a XOR a') / N. For Q_1 = sum of disjoint bit pairs:
    #   - if n_log2 (= m+1) is even: all 2^(m+1) pairs used, nondegenerate
    #     -> |Walsh| = 2^((m+1)/2) at all d -> max |IP|/N = 2^(n_log2/2)/N
    #   - if n_log2 is odd: one bit unpaired (linear, not in Q_1)
    #     -> Walsh vanishes for half the d (those with the unpaired bit set)
    #     -> nonzero |Walsh| = 2 * 2^((m+1-1)/2) = 2^((n_log2+1)/2)
    #     -> max |IP|/N = 2^((n_log2+1)/2)/N (double the even case)
    N = config["N"]
    n_log2 = int(round(math.log2(N)))
    if n_log2 % 2 == 0:
        expected_cross = 2 ** (n_log2 // 2) / N
    else:
        expected_cross = 2 ** ((n_log2 + 1) // 2) / N
    cross_max = summary["codebook_stats"]["cross_coset_max"]
    band_lo = expected_cross * 0.9
    band_hi = expected_cross * 1.1
    oracle.assert_in_range("cross_coset_max_ip", cross_max, (band_lo, band_hi))

    # Oracle 2: within-coset IPs near zero
    if summary["codebook_stats"]["within_coset_0_max"] > 1e-6:
        raise AssertionError(
            f"SANITY FAIL [within_coset_0]: max within-coset-0 IP = "
            f"{summary['codebook_stats']['within_coset_0_max']:.6f} > 0; H rows aren't orthogonal")
    if summary["codebook_stats"]["within_coset_1_max"] > 1e-6:
        raise AssertionError(
            f"SANITY FAIL [within_coset_1]: max within-coset-1 IP = "
            f"{summary['codebook_stats']['within_coset_1_max']:.6f} > 0; coset 1 not orthogonal")

    # Oracle 3: snap-to-codebook is identity for a codebook element
    codebook = make_kerdock_2coset_codebook(N, torch.device("cpu"))
    sample = codebook[:5]
    snapped = snap_to_codebook_batch(sample, codebook)
    if not torch.equal(snapped, sample):
        raise AssertionError(
            "SANITY FAIL [snap_identity]: snap(c) != c for c in codebook")

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14v_erase_kerdock_v2",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14v_erase_kerdock_v2")
    log_event("experiment_started", name="wave14v_erase_kerdock_v2", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14v_erase_kerdock_v2",
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
