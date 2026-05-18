"""Memory-augmented HDC: encode nested structure as a pointer chain instead of nested bundles.

For depth-d 'believes(p_d, ... believes(p_2, loves(p_0, p_1)) ... )' encode as:
  - frame_0  = bundle(bind(AGENT, p_0), bind(PATIENT, p_1))
  - ptr_0    = random pointer atom; address book stores (ptr_0, frame_0)
  - frame_k  = bundle(bind(BELIEVER, p_{k+1}), bind(CONTENT_PTR, ptr_{k-1}))
  - ptr_k    = random pointer atom; address book stores (ptr_k, frame_k)
  - return ptr_{d-1} as the 'address' of the whole structure

Query for the leaf AGENT at depth d:
  1. start with top pointer
  2. resolve via cleanup against address-book pointers -> frame_k
  3. unbind by CONTENT_PTR -> ptr_{k-1} (with noise)
  4. cleanup -> frame_{k-1}
  5. repeat until innermost frame
  6. unbind by AGENT -> leaf atom (with noise)
  7. cleanup against filler pool

The key claim: EVERY frame is at depth 1 (k=2 bundle), which our substrate recovers cleanly.
Depth comes from the number of pointer hops, not from compression inside one vector.

If this works, the log(N) substrate depth ceiling is SIDESTEPPED, not broken: we compose by
chaining lookups instead of compressing into one vector.
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
N_VALUES = [1024, 4096, 16384, 65536]
DEPTH_VALUES = [1, 2, 3, 5, 8, 13, 20, 30, 50, 75, 100]
POOL_SIZE = 100
TRIALS = 100


def encode_pointer_chain(
    depth: int,
    people_vecs: torch.Tensor,  # (depth+1, n) of filler atoms for this trial
    agent_role: torch.Tensor,
    patient_role: torch.Tensor,
    believer_role: torch.Tensor,
    content_ptr_role: torch.Tensor,
    n: int,
    gen: torch.Generator,
) -> tuple[torch.Tensor, torch.Tensor, list[torch.Tensor]]:
    """Build the pointer-chain encoding. Returns (top_ptr, ptr_pool tensor, frames list)."""
    pointers: list[torch.Tensor] = []
    frames: list[torch.Tensor] = []

    # Innermost frame: loves(p_0, p_1)
    inner_frame = bundling.bundle(
        torch.stack(
            [
                binding.bind(agent_role, people_vecs[0]),
                binding.bind(patient_role, people_vecs[1]),
            ]
        )
    )
    inner_ptr = atoms.make_atom_fhrr(n, gen)
    pointers.append(inner_ptr)
    frames.append(inner_frame)

    current_ptr = inner_ptr
    for k in range(depth - 1):
        # Bundle bind(BELIEVER, p_{k+2}) with bind(CONTENT_PTR, current_ptr)
        new_frame = bundling.bundle(
            torch.stack(
                [
                    binding.bind(believer_role, people_vecs[k + 2]),
                    binding.bind(content_ptr_role, current_ptr),
                ]
            )
        )
        new_ptr = atoms.make_atom_fhrr(n, gen)
        pointers.append(new_ptr)
        frames.append(new_frame)
        current_ptr = new_ptr

    return current_ptr, torch.stack(pointers), frames


def query_pointer_chain(
    top_ptr: torch.Tensor,
    ptr_pool: torch.Tensor,
    frames: list[torch.Tensor],
    agent_role: torch.Tensor,
    content_ptr_role: torch.Tensor,
    filler_pool: torch.Tensor,
    depth: int,
    n: int,
) -> int:
    """Walk pointer chain from top_ptr down to leaf. Return predicted filler index."""
    # Resolve top_ptr -> frame
    sims = (ptr_pool @ top_ptr.conj()).real / n
    idx = int(sims.argmax().item())
    frame = frames[idx]

    # Walk down (depth - 1) pointer hops
    for _ in range(depth - 1):
        next_ptr_raw = binding.unbind(frame, content_ptr_role)
        sims = (ptr_pool @ next_ptr_raw.conj()).real / n
        idx = int(sims.argmax().item())
        frame = frames[idx]

    # At innermost, unbind by AGENT
    leaf_raw = binding.unbind(frame, agent_role)
    sims = (filler_pool @ leaf_raw.conj()).real / n
    return int(sims.argmax().item())


def measure_recovery_pointer(
    n: int,
    depth: int,
    pool: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    trials: int,
    gen: torch.Generator,
) -> float:
    pool_size = pool.shape[0]
    correct = 0
    for _ in range(trials):
        n_needed = depth + 1
        if n_needed > pool_size:
            return 0.0
        perm = torch.randperm(pool_size, generator=gen)[:n_needed]
        people_vecs = pool[perm]
        target_idx = int(perm[0].item())

        top_ptr, ptr_pool, frames = encode_pointer_chain(
            depth=depth,
            people_vecs=people_vecs,
            agent_role=role_atoms["AGENT"],
            patient_role=role_atoms["PATIENT"],
            believer_role=role_atoms["BELIEVER"],
            content_ptr_role=role_atoms["CONTENT_PTR"],
            n=n,
            gen=gen,
        )

        predicted = query_pointer_chain(
            top_ptr=top_ptr,
            ptr_pool=ptr_pool,
            frames=frames,
            agent_role=role_atoms["AGENT"],
            content_ptr_role=role_atoms["CONTENT_PTR"],
            filler_pool=pool,
            depth=depth,
            n=n,
        )
        if predicted == target_idx:
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
            pool = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(POOL_SIZE)]).to(DEVICE)
            role_atoms = {
                r: atoms.make_atom_fhrr(n, gen)
                for r in ("AGENT", "PATIENT", "BELIEVER", "CONTENT_PTR")
            }
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_recovery_pointer(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"Memory-augmented HDC (pointer chain) beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"reference: HRR pinned 1.232, permutation 1.015, FHRR 0.717"
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
        ax.set_xlabel("nesting depth (pointer chain length)")
        ax.set_ylabel("leaf-atom recovery rate")
        ax.set_title(f"Memory-augmented HDC: pointer-chain depth recovery (beta = {beta:.3f})")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in N_VALUES if d_50_by_n[n] is not None]
        if ns:
            d50s = [d_50_by_n[n] for n in ns]
            ax.scatter(ns, d50s, color="darkgreen", s=100, zorder=3, label="Memory-augmented HDC")
            if not math.isnan(beta):
                n_fit = np.geomspace(min(ns), max(ns), 50)
                d_fit = beta * np.log2(n_fit) + intercept
                ax.plot(n_fit, d_fit, color="darkgreen", linewidth=2,
                        label=f"Memory-aug fit: beta={beta:.3f}, R^2={r2:.4f}")
        n_arr = np.array(N_VALUES)
        ax.plot(n_arr, 1.232 * np.log2(n_arr) - 6.807, color="steelblue", linewidth=1.5, linestyle="--",
                label="HRR pinned: beta=1.232")
        ax.plot(n_arr, 1.015 * np.log2(n_arr) - 2.661, color="darkorange", linewidth=1.5, linestyle="--",
                label="Permutation: beta=1.015")
        ax.plot(n_arr, 0.717 * np.log2(n_arr) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR k=2: beta=0.717")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("Memory-augmented HDC vs conventional VSA depth scaling")
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
    spec = experiment.ExperimentSpec(name="exp_pointer_chain", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
