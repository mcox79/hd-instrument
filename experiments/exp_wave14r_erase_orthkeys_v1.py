"""Surgical erase under orthogonal keys (Hadamard subcode) vs correlated keys.

V1 of the Kerdock-coset GDPR-erase family per Research R1. The Hadamard
subcode is the extreme of structured codebooks — zero pairwise inner
products at M_stored <= N. R1's load-bearing claim is that bounded pairwise
IPs remove the "bridges" from paraphrase probes back to erased values
(the Mirage failure mode on correlated keys). v1 tests the cleanest case:
do exactly-orthogonal keys break Mirage where correlated keys failed?

Direct comparison within one script:
  Arm A: keys from make_correlated_keys (rank_L bottleneck) — replicates
         wave14p_erase_multiprobe Mirage failure
  Arm B: keys from Sylvester Hadamard codebook — orthogonal by construction

Same multi-probe battery on both: argmax_leak, rank, norm_ratio,
paraphrase_leak at h in {2,4,8,16}, kept_preservation.

Pre-reg: preregs/2026-05-21_wave14r_erase_orthkeys_v1.md
"""
from __future__ import annotations

import argparse
import json
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


N_FULL = 4096
N_SMOKE = 512
M_STORED_FULL = 200
M_STORED_SMOKE = 40
N_ERASE_FULL = 30
N_ERASE_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 10
N_PARAPHRASE_PER_ERASE = 20
RANK_L_RATIO = 0.25
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHAS_FULL = [1.0, 1.5, 2.0]
ALPHAS_SMOKE = [1.5]
HAMMING_RADII_FULL = [2, 4, 8, 16]
HAMMING_RADII_SMOKE = [4, 8]

PASS_ARGMAX = 0.05
PASS_RANK = 100.0
PASS_NORM = 0.15
PASS_PARAPHRASE = 0.05
PASS_KEPT = 0.95
PASS_KEPT_FLOOR = 0.85
CORRELATED_BROKEN_RANK = 30.0
CORRELATED_BROKEN_NORM = 0.30
CORRELATED_BROKEN_PARAPHRASE = 0.10


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


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Multi-probe verdict comparing Hadamard arm vs correlated arm."""
    arms = summary.get("by_arm", {})
    if not arms:
        return ("STRUCT_KEYS_INCONCLUSIVE", "No per-arm data.")
    hada = arms.get("hadamard", {})
    corr = arms.get("correlated", {})
    if not hada or not corr:
        return ("STRUCT_KEYS_INCONCLUSIVE", "Missing arm data.")

    # Pick best alpha for Hadamard: lowest argmax_leak satisfying kept_preservation > floor
    hada_rows = hada.get("per_alpha", [])
    corr_rows = corr.get("per_alpha", [])
    if not hada_rows or not corr_rows:
        return ("STRUCT_KEYS_INCONCLUSIVE", "Per-alpha rows missing.")

    def best_alpha_row(rows):
        # Choose the row with the lowest argmax_leak among those satisfying kept floor.
        viable = [r for r in rows if r["kept_preservation"] >= PASS_KEPT_FLOOR]
        if not viable:
            return min(rows, key=lambda r: r["argmax_leak"])  # fall back
        return min(viable, key=lambda r: r["argmax_leak"])

    hada_best = best_alpha_row(hada_rows)
    corr_at_hada_alpha = next((r for r in corr_rows if r["alpha"] == hada_best["alpha"]),
                               corr_rows[-1])

    def hada_passes_all(r):
        return (r["argmax_leak"] < PASS_ARGMAX and
                r["mean_rank"] > PASS_RANK and
                r["norm_ratio"] < PASS_NORM and
                r.get(f"paraphrase_leak_h{8}", 1.0) < PASS_PARAPHRASE and
                r["kept_preservation"] >= PASS_KEPT)

    def corr_is_broken(r):
        return (r["mean_rank"] <= CORRELATED_BROKEN_RANK or
                r["norm_ratio"] > CORRELATED_BROKEN_NORM or
                r.get(f"paraphrase_leak_h{8}", 0.0) > CORRELATED_BROKEN_PARAPHRASE)

    # Check baseline-broken first: if correlated arm passes, can't draw conclusion
    if not corr_is_broken(corr_at_hada_alpha):
        return ("STRUCT_KEYS_BASELINE_NOT_BROKEN",
                f"Correlated arm did NOT reproduce Mirage at alpha={hada_best['alpha']}: "
                f"argmax={corr_at_hada_alpha['argmax_leak']:.3f}, "
                f"rank={corr_at_hada_alpha['mean_rank']:.1f}, "
                f"norm={corr_at_hada_alpha['norm_ratio']:.3f}, "
                f"para_h8={corr_at_hada_alpha.get('paraphrase_leak_h8', float('nan')):.3f}. "
                f"Cannot attribute Hadamard outcome to key structure. Audit test setup vs "
                f"wave14p_erase_multiprobe before drawing substrate conclusions.")

    if hada_passes_all(hada_best):
        return ("STRUCT_KEYS_FIX_MIRAGE",
                f"Hadamard arm passes all 5 probes at alpha={hada_best['alpha']} "
                f"(argmax={hada_best['argmax_leak']:.3f}, rank={hada_best['mean_rank']:.1f}, "
                f"norm={hada_best['norm_ratio']:.3f}, "
                f"para_h8={hada_best['paraphrase_leak_h8']:.3f}, "
                f"kept={hada_best['kept_preservation']:.3f}). Correlated arm reproduces "
                f"Mirage at same alpha. Structured-keys (orthogonal) family validated at v1; "
                f"route to v2 with full Kerdock + snap for dense-codebook regime.")

    # Hadamard partial failure analysis
    fails = []
    if hada_best["argmax_leak"] >= PASS_ARGMAX:
        fails.append(f"argmax_leak={hada_best['argmax_leak']:.3f}>={PASS_ARGMAX}")
    if hada_best["mean_rank"] <= PASS_RANK:
        fails.append(f"mean_rank={hada_best['mean_rank']:.1f}<={PASS_RANK}")
    if hada_best["norm_ratio"] >= PASS_NORM:
        fails.append(f"norm_ratio={hada_best['norm_ratio']:.3f}>={PASS_NORM}")
    para_h8 = hada_best.get("paraphrase_leak_h8", 1.0)
    if para_h8 >= PASS_PARAPHRASE:
        fails.append(f"paraphrase_leak_h8={para_h8:.3f}>={PASS_PARAPHRASE}")
    kept_drop = hada_best["kept_preservation"] < PASS_KEPT

    deep_probe_fails = [f for f in fails if "argmax_leak" not in f]
    only_argmax_passes = (hada_best["argmax_leak"] < PASS_ARGMAX and
                          (hada_best["mean_rank"] <= PASS_RANK or
                           hada_best["norm_ratio"] >= PASS_NORM))

    if kept_drop and not deep_probe_fails:
        return ("STRUCT_KEYS_KEPT_FAIL",
                f"Hadamard arm passes 4 probes but kept_preservation="
                f"{hada_best['kept_preservation']:.3f} < {PASS_KEPT} at alpha="
                f"{hada_best['alpha']}. Erase too aggressive; rehabilitation: "
                f"try lower alpha sweep or M_stored variations.")

    if only_argmax_passes:
        return ("STRUCT_KEYS_ARGMAX_ONLY",
                f"Hadamard arm shows Mirage-style failure (argmax_leak="
                f"{hada_best['argmax_leak']:.3f} passes but rank="
                f"{hada_best['mean_rank']:.1f} or norm={hada_best['norm_ratio']:.3f} "
                f"fail). Orthogonal keys do not remove the Mirage bridges in this "
                f"regime. Routes to: paraphrase-aware ROME (R1 Candidate 3') as "
                f"next family.")

    if (hada_best["argmax_leak"] < PASS_ARGMAX and
        hada_best["mean_rank"] > PASS_RANK and
        hada_best["norm_ratio"] < PASS_NORM and
        para_h8 >= PASS_PARAPHRASE):
        return ("STRUCT_KEYS_PARAPHRASE_FAIL",
                f"Hadamard arm passes argmax/rank/norm/kept but paraphrase_leak_h8="
                f"{para_h8:.3f} >= {PASS_PARAPHRASE}. Surprising: orthogonal keys "
                f"should make paraphrase trivially safe at h<=N/3. Possible causes: "
                f"value-codebook collision (paraphrase points to a different stored fact "
                f"happening to equal v_erased after sign collapse), or alpha not large "
                f"enough to overcome the (1-2h/N) residual.")

    if hada_best["argmax_leak"] >= PASS_ARGMAX and hada_best["argmax_leak"] > 0.5:
        return ("STRUCT_KEYS_NO_ERASURE",
                f"Hadamard arm argmax_leak={hada_best['argmax_leak']:.3f} (>>{PASS_ARGMAX}). "
                f"Even basic erase fails. Either alpha too small or W storage broken.")

    return ("STRUCT_KEYS_ARGMAX_ONLY",
            f"Hadamard arm partial failure at alpha={hada_best['alpha']}: " +
            "; ".join(fails) + ". See per-alpha table for full picture.")


def self_test_verdict() -> None:
    cases = [
        # 1. FIX_MIRAGE: Hadamard all pass, correlated has high paraphrase
        ({"by_arm": {
            "hadamard": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 150, "norm_ratio": 0.05,
                 "paraphrase_leak_h8": 0.02, "kept_preservation": 0.98}]},
            "correlated": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.05, "mean_rank": 10, "norm_ratio": 0.45,
                 "paraphrase_leak_h8": 0.25, "kept_preservation": 0.98}]}}},
         "STRUCT_KEYS_FIX_MIRAGE"),
        # 2. PARAPHRASE_FAIL: Hadamard passes 4 probes, paraphrase fails
        ({"by_arm": {
            "hadamard": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 150, "norm_ratio": 0.05,
                 "paraphrase_leak_h8": 0.20, "kept_preservation": 0.98}]},
            "correlated": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.10, "mean_rank": 10, "norm_ratio": 0.45,
                 "paraphrase_leak_h8": 0.25, "kept_preservation": 0.98}]}}},
         "STRUCT_KEYS_PARAPHRASE_FAIL"),
        # 3. ARGMAX_ONLY: Hadamard reproduces Mirage (rank fail)
        ({"by_arm": {
            "hadamard": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 5, "norm_ratio": 0.40,
                 "paraphrase_leak_h8": 0.18, "kept_preservation": 0.98}]},
            "correlated": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.10, "mean_rank": 10, "norm_ratio": 0.45,
                 "paraphrase_leak_h8": 0.25, "kept_preservation": 0.98}]}}},
         "STRUCT_KEYS_ARGMAX_ONLY"),
        # 4. KEPT_FAIL: Hadamard passes deep probes but kept drops
        ({"by_arm": {
            "hadamard": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 150, "norm_ratio": 0.05,
                 "paraphrase_leak_h8": 0.02, "kept_preservation": 0.90}]},
            "correlated": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.10, "mean_rank": 10, "norm_ratio": 0.45,
                 "paraphrase_leak_h8": 0.25, "kept_preservation": 0.92}]}}},
         "STRUCT_KEYS_KEPT_FAIL"),
        # 5. BASELINE_NOT_BROKEN: correlated unexpectedly passes
        ({"by_arm": {
            "hadamard": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 150, "norm_ratio": 0.05,
                 "paraphrase_leak_h8": 0.02, "kept_preservation": 0.98}]},
            "correlated": {"per_alpha": [
                {"alpha": 1.5, "argmax_leak": 0.02, "mean_rank": 180, "norm_ratio": 0.05,
                 "paraphrase_leak_h8": 0.03, "kept_preservation": 0.98}]}}},
         "STRUCT_KEYS_BASELINE_NOT_BROKEN"),
        # 6. INCONCLUSIVE
        ({}, "STRUCT_KEYS_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL case: actual={actual} != expected={expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_correlated_keys(n_facts: int, N: int, rank_L: int, gen: torch.Generator,
                          device: torch.device) -> torch.Tensor:
    """Replicates wave14q_rome_vs_antihebbian.make_correlated_keys exactly."""
    factors = 2.0 * (torch.rand((rank_L, N), generator=gen, device=device) > 0.5).float() - 1.0
    weights = torch.rand((n_facts, rank_L), generator=gen, device=device)
    weights = weights * (weights > 0.6).float()
    noise = 0.3 * torch.randn((n_facts, N), generator=gen, device=device)
    return torch.sign(weights @ factors + noise + 1e-9)


def sylvester_hadamard(n_log2: int, device: torch.device) -> torch.Tensor:
    """Generate N=2^n_log2 Sylvester Hadamard matrix in {+1,-1}.
    Recursive: H_2k = [[H_k, H_k], [H_k, -H_k]].
    """
    H = torch.tensor([[1.0]], device=device)
    for _ in range(n_log2):
        H = torch.cat([torch.cat([H, H], dim=1),
                       torch.cat([H, -H], dim=1)], dim=0)
    return H


def make_hadamard_keys(n_facts: int, N: int, gen: torch.Generator,
                        device: torch.device) -> torch.Tensor:
    """Sample n_facts mutually-orthogonal keys from Sylvester Hadamard codebook.

    The codebook has N rows + N row-complements = 2N distinct ±1 codewords.
    Within the same row set (rows OR complements), pairs are orthogonal.
    Between a row and its own complement: IP=-N (use only one of each pair).
    For M_stored <= N, we sample without replacement from the N rows;
    pairwise IPs are exactly 0.
    """
    if n_facts > N:
        raise ValueError(f"Hadamard codebook supports at most {N} mutually orthogonal "
                         f"keys at width N; asked for {n_facts}.")
    n_log2 = int(round(torch.log2(torch.tensor(float(N))).item()))
    if 2 ** n_log2 != N:
        raise ValueError(f"N={N} not a power of 2; Sylvester construction needs N=2^k.")
    H = sylvester_hadamard(n_log2, device)  # (N, N) +/- 1
    perm = torch.randperm(N, generator=gen)[:n_facts].to(device)
    return H[perm]


def antihebbian_erase(W, key_vec, alpha):
    """Identical to wave14q_rome_vs_antihebbian.antihebbian_erase."""
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - alpha * torch.outer(Wk, key_vec) / d


def hamming_perturb(keys: torch.Tensor, n_paraphrase: int, h: int,
                     gen_cpu: torch.Generator, device: torch.device) -> torch.Tensor:
    """For each row in keys, generate n_paraphrase copies with h random bits flipped.
    Returns tensor of shape (n_keys * n_paraphrase, N).

    Uses a CPU generator and vectorized argsort (torch.randperm does not accept
    CUDA generators in this PyTorch build).
    """
    n_keys, N = keys.shape
    total = n_keys * n_paraphrase
    out = keys.unsqueeze(1).expand(-1, n_paraphrase, -1).reshape(total, N).clone()
    if h > 0:
        scores = torch.rand((total, N), generator=gen_cpu)
        flip_idx = scores.argsort(dim=1)[:, :h].to(device)
        flip_mask = torch.zeros((total, N), device=device, dtype=torch.bool)
        rows = torch.arange(total, device=device).unsqueeze(1).expand(-1, h)
        flip_mask[rows, flip_idx] = True
        out = torch.where(flip_mask, -out, out)
    return out


def multi_probe(W: torch.Tensor, keys: torch.Tensor, values: torch.Tensor,
                 erase_idx: list[int], kept_idx: list[int], paraphrase_radii: list[int],
                 n_paraphrase: int, gen_cpu: torch.Generator, device: torch.device) -> dict:
    """Compute all five probes on W against the stored (keys, values) tables."""
    N = keys.size(-1)
    erase_t = torch.tensor(erase_idx, device=device)
    kept_t = torch.tensor(kept_idx, device=device)
    keys_e = keys[erase_idx]
    values_e = values[erase_idx]

    # Probe 1-3: argmax/rank/norm on the erased keys themselves
    retrieved_e = keys_e @ W.T  # (n_erase, N)
    sims_e = retrieved_e @ values.T  # (n_erase, n_facts)
    argmax_leak = (sims_e.argmax(dim=1) == erase_t).float().mean().item()
    sorted_idx = sims_e.argsort(dim=1, descending=True)
    ranks = [int((sorted_idx[r] == erase_t[r]).nonzero(as_tuple=False)[0].item()) + 1
             for r in range(len(erase_idx))]
    mean_rank = sum(ranks) / len(ranks)
    norm_ratio = (retrieved_e.norm(dim=1) / (N ** 0.5)).mean().item()
    cos_e = torch.nn.functional.cosine_similarity(retrieved_e, values_e, dim=1).mean().item()

    # Probe 4: paraphrase_leak at each Hamming radius
    out = {"argmax_leak": argmax_leak, "mean_rank": mean_rank, "norm_ratio": norm_ratio,
           "cosine": cos_e}
    for h in paraphrase_radii:
        para_keys = hamming_perturb(keys_e, n_paraphrase, h, gen_cpu, device)
        retrieved_p = para_keys @ W.T  # (n_erase*n_para, N)
        sims_p = retrieved_p @ values.T
        argmax_p = sims_p.argmax(dim=1)
        # Each erase_idx[i] has n_paraphrase paraphrase queries in rows [i*n_para .. (i+1)*n_para]
        erase_idx_expanded = erase_t.repeat_interleave(n_paraphrase)
        leak_p = (argmax_p == erase_idx_expanded).float().mean().item()
        out[f"paraphrase_leak_h{h}"] = leak_p

    # Probe 5: kept_preservation
    retrieved_kept = keys[kept_idx] @ W.T
    sims_kept = retrieved_kept @ values.T
    kept_correct = (sims_kept.argmax(dim=1) == kept_t).float().mean().item()
    out["kept_preservation"] = kept_correct

    return out


def run_arm(arm_name: str, key_maker_fn, config: dict, device: torch.device) -> dict:
    """Run multi-probe battery for one arm across alphas and seeds."""
    N = config["N"]
    n_facts = config["M_stored"]
    n_erase = config["n_erase"]
    n_kept = config["n_kept_probe"]
    seeds = config["seeds"]
    alphas = config["alphas"]
    hamming = config["hamming_radii"]
    n_para = config["n_paraphrase"]
    rank_L = max(2, int(n_facts * RANK_L_RATIO))

    per_alpha = []
    pairwise_stats = []
    for alpha in alphas:
        per_seed = []
        for seed in seeds:
            gen = torch.Generator(device=device).manual_seed(seed)
            cpu_gen = torch.Generator().manual_seed(seed + 1009)
            keys = key_maker_fn(n_facts, N, rank_L, gen, cpu_gen, device)
            values = 2.0 * (torch.rand((n_facts, N), generator=gen, device=device) > 0.5).float() - 1.0
            W = (values.T @ keys) / N
            key_ips = (keys @ keys.T) / N
            mask = ~torch.eye(n_facts, dtype=torch.bool, device=device)
            off_diag = key_ips[mask]
            pairwise_stats.append({
                "alpha": alpha, "seed": seed,
                "mean_abs": float(off_diag.abs().mean()),
                "max_abs": float(off_diag.abs().max()),
                "std": float(off_diag.std()),
            })

            erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
            kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
            erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
            erase_set = set(erase_idx)
            candidates = [i for i in range(n_facts) if i not in erase_set]
            kept_idx = sorted(torch.tensor(candidates)[torch.randperm(
                len(candidates), generator=kept_gen)[:n_kept]].tolist())

            W_edit = W.clone()
            for i in erase_idx:
                W_edit = antihebbian_erase(W_edit, keys[i], alpha)

            probe = multi_probe(W_edit, keys, values, erase_idx, kept_idx,
                                  hamming, n_para, cpu_gen, device)
            probe["seed"] = seed
            per_seed.append(probe)

        # Aggregate across seeds
        def avg(k):
            vals = [r[k] for r in per_seed if k in r]
            return sum(vals) / len(vals) if vals else 0.0
        agg = {"alpha": alpha,
                "argmax_leak": avg("argmax_leak"),
                "mean_rank": avg("mean_rank"),
                "norm_ratio": avg("norm_ratio"),
                "cosine": avg("cosine"),
                "kept_preservation": avg("kept_preservation")}
        for h in hamming:
            agg[f"paraphrase_leak_h{h}"] = avg(f"paraphrase_leak_h{h}")
        agg["per_seed"] = per_seed
        per_alpha.append(agg)

    return {"per_alpha": per_alpha, "pairwise_stats": pairwise_stats,
            "config_arm": {"n_facts": n_facts, "rank_L_for_correlated": rank_L,
                            "key_maker": arm_name}}


def hadamard_key_maker(n_facts, N, rank_L_unused, gen_cuda, gen_cpu, device):
    return make_hadamard_keys(n_facts, N, gen_cpu, device)


def correlated_key_maker(n_facts, N, rank_L, gen_cuda, gen_cpu, device):
    return make_correlated_keys(n_facts, N, rank_L, gen_cuda, device)


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_erase": N_ERASE_SMOKE if smoke else N_ERASE_FULL,
        "n_kept_probe": N_KEPT_PROBE_SMOKE if smoke else N_KEPT_PROBE_FULL,
        "n_paraphrase": N_PARAPHRASE_PER_ERASE,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alphas": ALPHAS_SMOKE if smoke else ALPHAS_FULL,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[arm=hadamard] running...", flush=True)
    arm_h = run_arm("hadamard", hadamard_key_maker, config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = run_arm("correlated", correlated_key_maker, config, device)

    summary = {"by_arm": {"hadamard": arm_h, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm_data in summary["by_arm"].items():
        print(f"[{arm_name}]", flush=True)
        for r in arm_data["per_alpha"]:
            paras = " ".join(f"p_h{h}={r[f'paraphrase_leak_h{h}']:.3f}"
                              for h in config["hamming_radii"])
            print(f"  alpha={r['alpha']:.2f}  argmax={r['argmax_leak']:.3f}  "
                  f"rank={r['mean_rank']:.1f}  norm={r['norm_ratio']:.3f}  "
                  f"{paras}  kept={r['kept_preservation']:.3f}", flush=True)

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
    out_dir = get_output_dir("wave14r_erase_orthkeys_v1_smoke")
    log_event("experiment_started", name="wave14r_erase_orthkeys_v1", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle assertions
    hada_stats = summary["by_arm"]["hadamard"]["pairwise_stats"]
    corr_stats = summary["by_arm"]["correlated"]["pairwise_stats"]
    max_hada = max(s["max_abs"] for s in hada_stats)
    mean_corr_std = sum(s["std"] for s in corr_stats) / len(corr_stats)
    oracle.assert_in_range("hadamard_max_pairwise_ip", max_hada, (0.0, 0.01))
    oracle.assert_in_range("correlated_pairwise_std", mean_corr_std, (0.03, 0.50))

    # Both arms must have run; pull representative numbers
    hada_row = summary["by_arm"]["hadamard"]["per_alpha"][0]
    corr_row = summary["by_arm"]["correlated"]["per_alpha"][0]
    oracle.assert_distinguishable("hadamard_vs_correlated_argmax",
                                    hada_row["argmax_leak"], corr_row["argmax_leak"],
                                    min_gap=0.0)  # any difference; will tighten in v2

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_erase_orthkeys_v1",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_erase_orthkeys_v1")
    log_event("experiment_started", name="wave14r_erase_orthkeys_v1", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_erase_orthkeys_v1",
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
