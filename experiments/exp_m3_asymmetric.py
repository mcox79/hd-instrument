"""M3: asymmetric relations. loves(Mary, John) vs loves(John, Mary) recover the right role.

Two structures encoded with the same role atoms (AGENT, PATIENT) but swapped fillers should
yield distinct queries: AGENT extracts the agent, PATIENT extracts the patient, regardless of
filler identity.
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
    n_pairs = 30

    cb = memory.Codebook(n, torch.complex64)
    # Build pool of person fillers
    people = [f"person_{i:03d}" for i in range(60)]
    person_vec = {}
    for name in people:
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(name, v)
        person_vec[name] = v
    # Two shared role atoms
    agent_role = atoms.make_atom_fhrr(n, gen)
    patient_role = atoms.make_atom_fhrr(n, gen)

    correct_forward = 0   # loves(A, B): AGENT -> A, PATIENT -> B
    correct_swapped = 0   # loves(B, A): AGENT -> B, PATIENT -> A
    confusion = 0         # forward AGENT recovered as B (the patient)

    for _ in range(n_pairs):
        # pick two distinct fillers
        perm = torch.randperm(len(people), generator=gen)[:2].tolist()
        a_name, b_name = people[perm[0]], people[perm[1]]
        a, b = person_vec[a_name], person_vec[b_name]

        # loves(A, B): AGENT=a, PATIENT=b
        forward = bundling.bundle(torch.stack([
            binding.bind(agent_role, a),
            binding.bind(patient_role, b),
        ]))
        # loves(B, A): AGENT=b, PATIENT=a
        swapped = bundling.bundle(torch.stack([
            binding.bind(agent_role, b),
            binding.bind(patient_role, a),
        ]))

        # Forward queries
        f_agent_recov, _ = cb.lookup(binding.unbind(forward, agent_role))
        f_patient_recov, _ = cb.lookup(binding.unbind(forward, patient_role))
        if f_agent_recov == a_name and f_patient_recov == b_name:
            correct_forward += 1
        if f_agent_recov == b_name:
            confusion += 1

        # Swapped queries
        s_agent_recov, _ = cb.lookup(binding.unbind(swapped, agent_role))
        s_patient_recov, _ = cb.lookup(binding.unbind(swapped, patient_role))
        if s_agent_recov == b_name and s_patient_recov == a_name:
            correct_swapped += 1

    headline = (
        f"forward={correct_forward}/{n_pairs}, swapped={correct_swapped}/{n_pairs}, "
        f"role_confusion={confusion}/{n_pairs}"
    )

    def page_bars(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        bars = ["forward correct", "swapped correct", "role confusion"]
        vals = [correct_forward, correct_swapped, confusion]
        ax.bar(bars, vals, color=["seagreen", "steelblue", "firebrick"])
        ax.set_ylim(0, n_pairs)
        ax.axhline(n_pairs, color="black", linestyle="--", alpha=0.4, label=f"max ({n_pairs})")
        ax.set_ylabel("count")
        ax.set_title("M3: asymmetric relation role recovery")
        for i, v in enumerate(vals):
            ax.text(i, v + 0.5, f"{v}/{n_pairs}", ha="center", fontsize=12)
        ax.legend()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_pairs": n_pairs,
        "correct_forward": correct_forward,
        "correct_swapped": correct_swapped,
        "role_confusion": confusion,
        "headline": headline,
        "review": correct_forward < n_pairs or correct_swapped < n_pairs,
        "_pdf_extras": [page_bars],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m3_asymmetric", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
