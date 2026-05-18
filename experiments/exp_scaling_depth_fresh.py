"""Depth-recovery scaling with FRESH role atoms at each level.

Replicates exp_scaling_depth.py but generates new BELIEVER and CONTENT atoms for each
nesting level instead of reusing the same two. The querier walks a per-level role list
when unwinding the structure.

Hypothesis: with fresh roles per level the coherent cross-talk vanishes; beta should
approach 1.0 (vs the 0.717 measured when roles are shared).
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def _measure_depth_recovery_fresh(
    n: int,
    depth: int,
    pool: torch.Tensor,
    agent_role: torch.Tensor,
    patient_role: torch.Tensor,
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

        # Innermost bundle uses fixed agent/patient roles
        innermost = bundling.bundle(
            torch.stack(
                [
                    binding.bind(agent_role, people_vecs[0]),
                    binding.bind(patient_role, people_vecs[1]),
                ]
            )
        )
        structure = innermost
        # Fresh per-level (BELIEVER, CONTENT) roles, recorded so we can unwind.
        outer_role_pairs: list[tuple[torch.Tensor, torch.Tensor]] = []
        for d in range(depth - 1):
            believer_role_d = atoms.make_atom_fhrr(n, gen)
            content_role_d = atoms.make_atom_fhrr(n, gen)
            outer_role_pairs.append((believer_role_d, content_role_d))
            structure = bundling.bundle(
                torch.stack(
                    [
                        binding.bind(believer_role_d, people_vecs[d + 2]),
                        binding.bind(content_role_d, structure),
                    ]
                )
            )

        queried = structure
        # Unwind outer levels in reverse (using the same CONTENT atom we encoded with)
        for d in range(depth - 1, 0, -1):
            _, content_role_d = outer_role_pairs[d - 1]
            queried = binding.unbind(queried, content_role_d)
        queried = binding.unbind(queried, agent_role)

        sims = (queried.unsqueeze(0) @ pool.conj().T).real / n
        best = int(sims.argmax(dim=1).item())
        if best == target_idx:
            correct += 1
    return correct / trials


def _find_d_50(recovery_by_d: dict[int, float]) -> float | None:
    ds_sorted = sorted(recovery_by_d.keys())
    for i in range(len(ds_sorted) - 1):
        d_lo, d_hi = ds_sorted[i], ds_sorted[i + 1]
        r_lo, r_hi = recovery_by_d[d_lo], recovery_by_d[d_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            t = (0.5 - r_lo) / (r_hi - r_lo)
            return d_lo + t * (d_hi - d_lo)
    return None


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    n_values = [1024, 2048, 4096, 8192, 16384]
    depth_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20]
    pool_size = 100
    trials = 30

    quiet_bus = tracing.TraceBus(enabled=False)

    sweep: dict[int, dict[int, float]] = {}
    d_50_by_n: dict[int, float | None] = {}

    with tracing.using(quiet_bus):
        for n in n_values:
            phases = torch.rand((pool_size, n), generator=gen) * (2.0 * math.pi)
            pool = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)
            agent_role = atoms.make_atom_fhrr(n, gen)
            patient_role = atoms.make_atom_fhrr(n, gen)
            recovery_by_d: dict[int, float] = {}
            for d in depth_values:
                if d + 1 > pool_size:
                    recovery_by_d[d] = 0.0
                    continue
                rate = _measure_depth_recovery_fresh(
                    n=n,
                    depth=d,
                    pool=pool,
                    agent_role=agent_role,
                    patient_role=patient_role,
                    trials=trials,
                    gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = _find_d_50(recovery_by_d)

    pairs = [(n, d) for n, d in d_50_by_n.items() if d is not None]
    if len(pairs) >= 2:
        log2_n = np.array([math.log2(n) for n, _ in pairs])
        d_vals = np.array([d for _, d in pairs])
        coeffs = np.polyfit(log2_n, d_vals, 1)
        beta = float(coeffs[0])
        intercept = float(coeffs[1])
        predicted = beta * log2_n + intercept
        ss_res = float(((d_vals - predicted) ** 2).sum())
        ss_tot = float(((d_vals - d_vals.mean()) ** 2).sum())
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
    else:
        beta = float("nan")
        intercept = float("nan")
        r2 = float("nan")

    headline = (
        f"fresh-roles beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"d50(1024)={d_50_by_n.get(1024)}, d50(16384)={d_50_by_n.get(16384)}; "
        f"shared-roles beta was 0.717"
    )

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(n_values)))
        for color, n in zip(colors, n_values):
            ds = sorted(sweep[n].keys())
            rs = [sweep[n][d] for d in ds]
            ax.plot(ds, rs, marker="o", color=color, linewidth=2, label=f"N={n}")
            d50 = d_50_by_n.get(n)
            if d50:
                ax.axvline(d50, color=color, linestyle=":", alpha=0.4)
        ax.set_xlabel("nesting depth")
        ax.set_ylabel("leaf-atom recovery rate")
        ax.set_title("Week 8b: depth recovery with FRESH roles per level")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_beta_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in n_values if d_50_by_n[n] is not None]
        d50s = [d_50_by_n[n] for n in ns]
        ax.scatter(ns, d50s, color="seagreen", s=80, zorder=3, label="fresh roles (this run)")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="seagreen", linewidth=2,
                    label=f"fresh-roles fit: beta={beta:.3f}, R^2={r2:.4f}")
        # Shared-roles reference (from exp_scaling_depth.py):
        shared_beta = 0.717
        shared_intercept = -0.629
        n_pred = np.array(ns)
        d_shared = shared_beta * np.log2(n_pred) + shared_intercept
        ax.plot(n_pred, d_shared, color="firebrick", linewidth=1.5, linestyle="--",
                label="shared-roles reference: beta=0.717")
        # Naive prediction beta=1
        d_naive = (np.log2(n_pred) - np.log2(np.log2(np.array([math.log(100)] * len(n_pred)))))
        # actually plot the simple beta=1 prediction shifted
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("Week 8b: fresh-roles vs shared-roles depth scaling")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": n_values,
        "depth_values": depth_values,
        "pool_size": pool_size,
        "trials_per_cell": trials,
        "recovery_sweep": {str(n): sweep[n] for n in n_values},
        "d_50_by_n": {str(n): d_50_by_n[n] for n in n_values},
        "beta": beta,
        "intercept": intercept,
        "r2": r2,
        "shared_roles_beta_reference": 0.717,
        "headline": headline,
        "review": math.isnan(beta),
        "_pdf_extras": [page_curves, page_beta_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_scaling_depth_fresh", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
