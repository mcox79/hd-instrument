"""Permutation binding for depth-recovery scaling.

Standard VSAs (HRR/FHRR/BSC) use binding operators (convolution / elementwise mul / XOR) that
introduce noise per operation because both operands are random vectors. Permutation binding is
different: roles are permutations (not vectors), bind = apply the permutation, unbind = apply
the inverse permutation. **Information is perfectly preserved per bind**.

The noise floor for depth recovery then comes only from bundling interference, not from the
binding cascade. The hypothesis: this should give dramatically better depth scaling -- potentially
beta >> the HRR ~1.2 we measured, because the per-bind noise term is structurally zero.

Substrate: HRR-style atoms (real Gaussian, L2-normalized), permutation binding, L2 bundle,
cosine similarity. Same N grid as other depth experiments for direct comparison.

This is the most promising test for a substrate that could uniquely enable large-context /
LLM-style structured memory: linear capacity scaling (like HRR) + lossless depth.
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import experiment, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_VALUES = [2048, 4096, 8192, 16384, 32768, 65536]
DEPTH_VALUES = [3, 5, 7, 9, 11, 13, 16, 20, 25, 30, 40, 50]
POOL_SIZE = 100
TRIALS = 150


def apply_permutation(x: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """bind(role_perm, atom) = atom permuted by role_perm. Exact, noiseless."""
    return x[perm]


def inverse_permutation(perm: torch.Tensor) -> torch.Tensor:
    return perm.argsort()


def make_role_perms(n: int, role_names: list[str], gen: torch.Generator) -> dict[str, torch.Tensor]:
    return {name: torch.randperm(n, generator=gen) for name in role_names}


def l2_bundle(vectors: torch.Tensor) -> torch.Tensor:
    """Whole-vector L2 normalization on a real-valued sum."""
    s = vectors.sum(dim=0)
    norm = s.norm()
    if float(norm) > 0:
        return s / norm
    return s


def measure_depth_recovery_permutation(
    n: int,
    depth: int,
    pool: torch.Tensor,
    role_perms: dict[str, torch.Tensor],
    inv_perms: dict[str, torch.Tensor],
    trials: int,
    gen: torch.Generator,
) -> float:
    pool_size = pool.shape[0]
    correct = 0
    for _ in range(trials):
        n_needed = depth + 1
        perm = torch.randperm(pool_size, generator=gen)[:n_needed]
        people_vecs = pool[perm]
        target_idx = int(perm[0].item())

        # Innermost: bundle of 2 (role_perm-applied, filler) pairs.
        innermost = l2_bundle(
            torch.stack(
                [
                    apply_permutation(people_vecs[0], role_perms["AGENT"]),
                    apply_permutation(people_vecs[1], role_perms["PATIENT"]),
                ]
            )
        )
        structure = innermost
        for d in range(depth - 1):
            structure = l2_bundle(
                torch.stack(
                    [
                        apply_permutation(people_vecs[d + 2], role_perms["BELIEVER"]),
                        apply_permutation(structure, role_perms["CONTENT"]),
                    ]
                )
            )

        queried = structure
        for _ in range(depth - 1):
            queried = apply_permutation(queried, inv_perms["CONTENT"])
        queried = apply_permutation(queried, inv_perms["AGENT"])

        # cosine similarity vs pool
        dot = (pool * queried).sum(dim=-1)
        nq = queried.norm()
        np_ = pool.norm(dim=-1)
        sims = dot / (nq * np_ + 1e-12)
        best = int(sims.argmax().item())
        if best == target_idx:
            correct += 1
    return correct / trials


def find_d_50(recovery_by_d):
    ds = sorted(recovery_by_d.keys())
    for i in range(len(ds) - 1):
        d_lo, d_hi = ds[i], ds[i + 1]
        r_lo, r_hi = recovery_by_d[d_lo], recovery_by_d[d_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            t = (0.5 - r_lo) / (r_hi - r_lo)
            return d_lo + t * (d_hi - d_lo)
    return None


def fit_beta(d_50_by_n):
    pairs = [(n, d) for n, d in d_50_by_n.items() if d is not None]
    if len(pairs) < 2:
        return float("nan"), float("nan"), float("nan")
    log2_n = np.array([math.log2(n) for n, _ in pairs])
    d_vals = np.array([d for _, d in pairs])
    coeffs = np.polyfit(log2_n, d_vals, 1)
    beta, intercept = float(coeffs[0]), float(coeffs[1])
    predicted = beta * log2_n + intercept
    ss_res = float(((d_vals - predicted) ** 2).sum())
    ss_tot = float(((d_vals - d_vals.mean()) ** 2).sum())
    r2 = 1 - ss_res / max(ss_tot, 1e-12)
    return beta, intercept, r2


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)
    sweep: dict[int, dict[int, float]] = {}
    d_50_by_n: dict[int, float | None] = {}

    with tracing.using(quiet_bus):
        for n in N_VALUES:
            pool = torch.randn((POOL_SIZE, n), generator=gen, dtype=torch.float32) / math.sqrt(n)
            role_perms = make_role_perms(n, ["AGENT", "PATIENT", "BELIEVER", "CONTENT"], gen)
            inv_perms = {name: inverse_permutation(p) for name, p in role_perms.items()}
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_depth_recovery_permutation(
                    n=n, depth=d, pool=pool,
                    role_perms=role_perms, inv_perms=inv_perms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"Permutation binding beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"HRR pinned 1.232; FHRR k=2 standard 0.717"
    )

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(N_VALUES)))
        for color, n in zip(colors, N_VALUES):
            ds = sorted(sweep[n].keys())
            rs = [sweep[n][d] for d in ds]
            ax.plot(ds, rs, marker="o", color=color, linewidth=2, label=f"N={n}")
            d50 = d_50_by_n.get(n)
            if d50:
                ax.axvline(d50, color=color, linestyle=":", alpha=0.4)
        ax.set_xlabel("nesting depth")
        ax.set_ylabel("leaf-atom recovery rate")
        ax.set_title(f"Permutation binding: beta={beta:.3f}")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in N_VALUES if d_50_by_n[n] is not None]
        d50s = [d_50_by_n[n] for n in ns]
        ax.scatter(ns, d50s, color="darkorange", s=80, zorder=3, label="Permutation binding (this run)")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="darkorange", linewidth=2,
                    label=f"permutation fit: beta={beta:.3f}")
        n_pred = np.array(ns) if ns else np.array(N_VALUES)
        ax.plot(n_pred, 1.232 * np.log2(n_pred) - 6.807, color="steelblue", linewidth=1.5, linestyle="--",
                label="HRR pinned: beta=1.232")
        ax.plot(n_pred, 0.717 * np.log2(n_pred) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR standard: beta=0.717")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("Permutation vs convolution/elementwise binding")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": N_VALUES,
        "depth_values": DEPTH_VALUES,
        "pool_size": POOL_SIZE,
        "trials_per_cell": TRIALS,
        "recovery_sweep": {str(n): sweep[n] for n in N_VALUES},
        "d_50_by_n": {str(n): d_50_by_n[n] for n in N_VALUES},
        "beta": beta,
        "intercept": intercept,
        "r2": r2,
        "headline": headline,
        "_pdf_extras": [page_curves, page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_depth_permutation", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
