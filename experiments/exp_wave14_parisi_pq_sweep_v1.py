"""Bet E v1 - Parisi P(q) comparative test across substrate configurations.

3 codebook types (random_bsc, hadamard, kerdock) x 3 M_stored values (0.5N, N, 2N).
Per cell: pairwise overlap distribution, Binder cumulant, ultrametricity fraction.
Test claim: P(q) discriminates substrate configuration with >=2sigma separation.

v1 covers comparative core; full 6-test battery + finite-size scaling deferred to v2.

Pre-reg: preregs/2026-05-21_wave14_parisi_pq_sweep_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)

SEPARATION_THRESHOLD_SIGMA = 2.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_pool(codebook_type, N, M_stored, seed, device):
    """Build a pool of M_stored bipolar atoms from the given codebook type."""
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    if codebook_type == "random_bsc":
        return 2.0 * (torch.rand((M_stored, N), generator=gen, device=device) > 0.5).float() - 1.0
    if codebook_type == "hadamard":
        n_log2 = int(round(math.log2(N)))
        H = v1.sylvester_hadamard(n_log2, device)  # (N, N)
        idx = torch.randperm(N, generator=cpu_gen)[:M_stored]
        if M_stored > N:
            # tile then perturb
            extra = M_stored - N
            extra_idx = torch.randperm(N, generator=cpu_gen)[:extra]
            pool = torch.cat([H, H[extra_idx]], dim=0)
            return pool[:M_stored]
        return H[idx]
    if codebook_type == "kerdock":
        codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
        keys = v3.sample_kerdock_keys(codebook, M_stored, cpu_gen, device)
        return keys
    raise ValueError(f"unknown codebook_type {codebook_type}")


def edwards_anderson_overlap_distribution(pool, N):
    Q = (pool @ pool.T) / N
    P = pool.shape[0]
    mask = torch.triu(torch.ones(P, P, dtype=torch.bool, device=pool.device), diagonal=1)
    return Q[mask]


def binder_cumulant(overlaps):
    q2 = float((overlaps ** 2).mean())
    q4 = float((overlaps ** 4).mean())
    if q2 < 1e-12:
        return 0.0
    return 1.0 - q4 / (3.0 * q2 * q2)


def ultrametricity_fraction(pool, n_triples, gen_seed, N):
    P = pool.shape[0]
    gen = torch.Generator().manual_seed(gen_seed)
    sat = 0
    eps = 0.01
    for _ in range(n_triples):
        idxs = torch.randperm(P, generator=gen)[:3]
        i, j, k = int(idxs[0]), int(idxs[1]), int(idxs[2])
        q_ij = float((pool[i] @ pool[j]) / N)
        q_jk = float((pool[j] @ pool[k]) / N)
        q_ik = float((pool[i] @ pool[k]) / N)
        vals = sorted([q_ij, q_jk, q_ik], reverse=True)
        if abs(vals[0] - vals[1]) < eps:
            sat += 1
    return sat / n_triples


def compute_verdict(summary):
    cells = summary.get("per_cell")
    if not cells:
        return ("PARISI_INCONCLUSIVE", "Missing per-cell data.")
    # Group by M_stored, compute mean+std of binder across codebook types
    by_M = {}
    for c in cells.values():
        M = c["M_stored"]
        ck = c["codebook_type"]
        by_M.setdefault(M, {}).setdefault(ck, []).append(c["binder"])
    # For each M, check >=2sigma separation across codebooks
    max_sep_sigma = 0.0
    discrim_at_M = []
    for M, by_ck in by_M.items():
        means = {ck: sum(vs) / len(vs) for ck, vs in by_ck.items()}
        stds = {ck: (sum((v - means[ck]) ** 2 for v in vs) / max(len(vs) - 1, 1)) ** 0.5
                  for ck, vs in by_ck.items()}
        # pairwise separation
        cks = list(means.keys())
        for i in range(len(cks)):
            for j in range(i + 1, len(cks)):
                ck1, ck2 = cks[i], cks[j]
                diff = abs(means[ck1] - means[ck2])
                pooled = (stds[ck1] + stds[ck2]) / 2.0 + 1e-6
                sep_sigma = diff / pooled
                if sep_sigma >= SEPARATION_THRESHOLD_SIGMA:
                    discrim_at_M.append((M, ck1, ck2, sep_sigma))
                if sep_sigma > max_sep_sigma:
                    max_sep_sigma = sep_sigma
    if discrim_at_M:
        examples = ", ".join(f"M={m}:{c1}-{c2}={s:.1f}sigma"
                              for m, c1, c2, s in discrim_at_M[:3])
        return ("PARISI_DISCRIMINATES_CODEBOOK",
                f"P(q) discriminates codebook >= {SEPARATION_THRESHOLD_SIGMA}sigma at "
                f"{len(discrim_at_M)} (M, codebook-pair) cells. Examples: {examples}. "
                f"Max separation: {max_sep_sigma:.1f}sigma.")
    # Check M_stored discrimination at fixed codebook
    by_ck = {}
    for c in cells.values():
        ck = c["codebook_type"]
        M = c["M_stored"]
        by_ck.setdefault(ck, {}).setdefault(M, []).append(c["binder"])
    m_discrim = False
    for ck, by_M2 in by_ck.items():
        if len(by_M2) >= 2:
            means = {M: sum(vs) / len(vs) for M, vs in by_M2.items()}
            stds = {M: (sum((v - means[M]) ** 2 for v in vs) / max(len(vs) - 1, 1)) ** 0.5
                      for M, vs in by_M2.items()}
            Ms = list(means.keys())
            for i in range(len(Ms)):
                for j in range(i + 1, len(Ms)):
                    diff = abs(means[Ms[i]] - means[Ms[j]])
                    pooled = (stds[Ms[i]] + stds[Ms[j]]) / 2.0 + 1e-6
                    if diff / pooled >= SEPARATION_THRESHOLD_SIGMA:
                        m_discrim = True
    if m_discrim:
        return ("PARISI_DISCRIMINATES_M_STORED",
                f"P(q) does NOT discriminate codebook but DOES discriminate M_stored at "
                f">= {SEPARATION_THRESHOLD_SIGMA}sigma. Max codebook sep: {max_sep_sigma:.1f}sigma. "
                f"Bet E fingerprint claim weak; substrate operating-point dependence dominates.")
    return ("PARISI_NO_DISCRIMINATION",
            f"P(q) does not discriminate codebook or M_stored at >= {SEPARATION_THRESHOLD_SIGMA}sigma. "
            f"Max separation: {max_sep_sigma:.1f}sigma. Bet E fingerprint claim weakens.")


def self_test_verdict():
    def cell(ck, M, binder, seed=17):
        return {"codebook_type": ck, "M_stored": M, "binder": binder, "seed": seed,
                "ultrametricity": 0.3}
    # Case 1: codebook discriminates (random=0.1, hadamard=0.5, kerdock=0.4 with small std)
    s1 = {"per_cell": {f"{ck}_{M}_{s}": cell(ck, M, binder + (s - 17) * 0.005)
                          for ck, binder in [("random_bsc", 0.1), ("hadamard", 0.5), ("kerdock", 0.4)]
                          for M in [2048, 4096]
                          for s in [17, 23, 31]}}
    # Case 2: codebooks similar but M_stored differs
    s2 = {"per_cell": {f"random_bsc_{M}_{s}": cell("random_bsc", M, 0.1 + (M / 8192.0) * 0.5 + (s - 17) * 0.005)
                          for M in [2048, 4096]
                          for s in [17, 23, 31]}}
    # Case 3: no discrimination
    s3 = {"per_cell": {f"{ck}_{M}_{s}": cell(ck, M, 0.3 + (s - 17) * 0.01)
                          for ck in ["random_bsc", "hadamard"]
                          for M in [2048, 4096]
                          for s in [17, 23, 31]}}
    cases = [
        (s1, "PARISI_DISCRIMINATES_CODEBOOK"),
        (s2, "PARISI_DISCRIMINATES_M_STORED"),
        (s3, "PARISI_NO_DISCRIMINATION"),
        ({}, "PARISI_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_cell(codebook_type, M_stored, seed, N, n_triples, device):
    pool = make_pool(codebook_type, N, M_stored, seed, device)
    overlaps = edwards_anderson_overlap_distribution(pool, N)
    binder = binder_cumulant(overlaps)
    um = ultrametricity_fraction(pool, n_triples, seed + 7, N)
    q2 = float((overlaps ** 2).mean())
    q4 = float((overlaps ** 4).mean())
    return {"codebook_type": codebook_type, "M_stored": M_stored, "seed": seed,
             "binder": binder, "ultrametricity": um, "q2": q2, "q4": q4,
             "n_overlaps": int(overlaps.numel())}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "codebook_types": ["random_bsc", "hadamard"] if smoke else
                                  ["random_bsc", "hadamard", "kerdock"],
              "M_ratios": [1.0] if smoke else [0.5, 1.0, 2.0],
              "seeds": [17] if smoke else [17, 23, 31],
              "n_triples": 500 if smoke else 5000}
    N = config["N"]
    per_cell = {}
    for ck in config["codebook_types"]:
        for ratio in config["M_ratios"]:
            M = int(ratio * N)
            for seed in config["seeds"]:
                key = f"{ck}_{M}_{seed}"
                print(f"[cell] {key} ...", flush=True)
                per_cell[key] = run_one_cell(ck, M, seed, N, config["n_triples"], device)
                print(f"  binder={per_cell[key]['binder']:.4f} "
                      f"um={per_cell[key]['ultrametricity']:.3f}", flush=True)
    summary = {"per_cell": per_cell}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
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
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["per_cell"].values())[0]
    oracle.assert_baseline_high("n_overlaps", float(first["n_overlaps"]), 100.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
