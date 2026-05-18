"""M4: nested recursive structures. believes(Bob, loves(Mary, John)) at depths 1-4.

depth 1: bind(role, filler), recover filler
depth 2: bundle of two bindings, recover one filler via role
depth 3: outer bundle whose CONTENT is itself a depth-2 structure
depth 4: outer bundle whose CONTENT is a depth-3 structure
...

At each level we chain unbinds and finally do cleanup of the leaf atom. We track recovery as
the cleanup similarity of the recovered leaf vs the true leaf; "success" = correct atom name.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, memory  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    trials = 30
    depths = [1, 2, 3, 4, 5]

    # Codebook of named atoms
    cb = memory.Codebook(n, torch.complex64)
    persons = [f"person_{i:03d}" for i in range(100)]
    person_vec: dict[str, torch.Tensor] = {}
    for name in persons:
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(name, v)
        person_vec[name] = v
    # Shared role atoms across all depths
    agent_role = atoms.make_atom_fhrr(n, gen)
    patient_role = atoms.make_atom_fhrr(n, gen)
    believer_role = atoms.make_atom_fhrr(n, gen)
    content_role = atoms.make_atom_fhrr(n, gen)

    def loves_struct(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        return bundling.bundle(torch.stack([
            binding.bind(agent_role, a),
            binding.bind(patient_role, b),
        ]))

    def believes_struct(believer: torch.Tensor, content: torch.Tensor) -> torch.Tensor:
        return bundling.bundle(torch.stack([
            binding.bind(believer_role, believer),
            binding.bind(content_role, content),
        ]))

    recovery_by_depth: dict[int, float] = {}
    raw_sim_by_depth: dict[int, float] = {}

    for depth in depths:
        correct = 0
        sim_sum = 0.0
        for _ in range(trials):
            # Sample distinct fillers
            perm = torch.randperm(len(persons), generator=gen)[: depth + 1].tolist()
            chosen = [persons[i] for i in perm]
            mary, john = chosen[0], chosen[1]
            # Build inner-most loves(Mary, John); target leaf = Mary (the AGENT)
            inner = loves_struct(person_vec[mary], person_vec[john])
            # Wrap depth-1 worth of believes() around it for depth >= 2
            structure = inner
            for d in range(depth - 1):
                believer = chosen[d + 2] if d + 2 < len(chosen) else chosen[-1]
                structure = believes_struct(person_vec[believer], structure)

            # Unwind: for depth d, we need to unbind CONTENT (d-1) times, then AGENT once.
            queried = structure
            for _ in range(depth - 1):
                queried = binding.unbind(queried, content_role)
            queried = binding.unbind(queried, agent_role)
            recovered_name, score = cb.lookup(queried)
            sim_sum += float(score)
            if recovered_name == mary:
                correct += 1
        recovery_by_depth[depth] = correct / trials
        raw_sim_by_depth[depth] = sim_sum / trials

    headline = " ".join(
        f"d{d}={recovery_by_depth[d] * 100:.0f}%"
        for d in depths
    )
    failure_depth = next(
        (d for d in depths if recovery_by_depth[d] < 0.5),
        None,
    )

    def page_depth(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        ds = list(recovery_by_depth.keys())
        rs = [recovery_by_depth[d] for d in ds]
        ms = [raw_sim_by_depth[d] for d in ds]
        ax1.plot(ds, rs, marker="o", color="seagreen", linewidth=2)
        ax1.set_xlabel("nesting depth")
        ax1.set_ylabel("leaf-atom recovery rate")
        ax1.set_title(f"M4: nested-structure recovery at N={n}")
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, alpha=0.3)
        if failure_depth is not None:
            ax1.axvline(failure_depth, color="firebrick", linestyle=":", alpha=0.6,
                        label=f"failure (>50%) at depth {failure_depth}")
            ax1.legend()

        ax2.plot(ds, ms, marker="o", color="steelblue", linewidth=2)
        ax2.set_xlabel("nesting depth")
        ax2.set_ylabel("mean raw cleanup similarity")
        ax2.set_title("M4: signal decay with depth")
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "trials_per_depth": trials,
        "depths": depths,
        "recovery_by_depth": recovery_by_depth,
        "raw_sim_by_depth": raw_sim_by_depth,
        "failure_depth": failure_depth,
        "headline": headline,
        "review": recovery_by_depth[1] < 0.99,
        "_pdf_extras": [page_depth],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m4_nested", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
