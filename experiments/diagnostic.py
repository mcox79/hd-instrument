"""End-to-end diagnostic run: exercises the substrate, modulators, learning, and observability stack.

Uses the experiment harness (hdlab.experiment.run) so artifacts (trace, PDF, metrics, results
log entry) are persisted with one call.
"""

from __future__ import annotations

import json

import torch

from hdlab import atoms, binding, bundling, experiment, learning, memory, modulators




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def diagnostic_workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    metrics: dict = {"substrate": {"n": n, "dtype": ctx.spec.dtype, "seed": ctx.spec.seed}}

    # Phase 1: build codebook of named atoms + two role atoms.
    codebook = memory.Codebook(n, torch.complex64)
    people = [f"person_{i:02d}" for i in range(20)]
    person_vecs: dict[str, torch.Tensor] = {}
    for name_ in people:
        v = atoms.make_atom_fhrr(n, gen)
        codebook.add(name_, v)
        person_vecs[name_] = v
    agent_role = atoms.make_atom_fhrr(n, gen)
    patient_role = atoms.make_atom_fhrr(n, gen)
    codebook.add("AGENT", agent_role)
    codebook.add("PATIENT", patient_role)

    # Phase 2: encode loves(person_00, person_01) and recover fillers by role.
    mary = person_vecs["person_00"]
    john = person_vecs["person_01"]
    loves_event = bundling.bundle(
        torch.stack(
            [
                binding.bind(agent_role, mary),
                binding.bind(patient_role, john),
            ]
        )
    )
    agent_query = binding.unbind(loves_event, agent_role)
    agent_name, agent_score = codebook.lookup(agent_query)
    metrics["agent_recovery"] = {
        "expected": "person_00",
        "got": agent_name,
        "score": float(agent_score),
    }
    patient_query = binding.unbind(loves_event, patient_role)
    patient_name, patient_score = codebook.lookup(patient_query)
    metrics["patient_recovery"] = {
        "expected": "person_01",
        "got": patient_name,
        "score": float(patient_score),
    }

    # Phase 3: attention sweep with stronger phase jitter so rejection actually fires.
    attention_results = []
    for att in [0.0, 0.2, 0.5, 0.9]:
        with modulators.using(attention=att):
            jitter = (torch.rand(n, generator=gen) - 0.5) * 3.0  # stronger noise
            rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(mary.dtype)
            noisy = mary * rot
            got, score = codebook.lookup(noisy)
            attention_results.append({"attention": att, "name": got, "score": float(score)})
    metrics["attention_sweep"] = attention_results
    rejected = sum(1 for r in attention_results if r["name"] is None)
    metrics["attention_rejections"] = rejected

    # Phase 4: reward-modulated Hebbian to closed-form steady state.
    decay = 0.05
    h = learning.HebbianAssociations(decay=decay)
    steps = 400
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(steps):
            h.update(["person_00", "person_01"])
    w_empirical = float(h.weight("person_00", "person_01"))
    w_theory = 1.0 / decay
    metrics["hebbian"] = {
        "decay": decay,
        "steps": steps,
        "empirical": w_empirical,
        "theoretical": w_theory,
        "ratio": w_empirical / w_theory,
    }

    # Outcome / headline for the results log.
    agent_ok = metrics["agent_recovery"]["got"] == "person_00"
    patient_ok = metrics["patient_recovery"]["got"] == "person_01"
    hebbian_ok = 0.99 < metrics["hebbian"]["ratio"] < 1.01
    metrics["headline"] = (
        f"Hebbian ratio={metrics['hebbian']['ratio']:.4f}, "
        f"agent_sim={metrics['agent_recovery']['score']:.3f}, "
        f"attention_rejections={rejected}/4"
    )
    metrics["review"] = not (agent_ok and patient_ok and hebbian_ok)
    return metrics


def main() -> None:
    spec = experiment.ExperimentSpec(name="diagnostic", seed=42, n=1024)
    result = experiment.run(spec, diagnostic_workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
