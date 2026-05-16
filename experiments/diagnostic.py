"""End-to-end diagnostic run: exercises the substrate, modulators, learning, and observability stack.

Writes:
- data/diagnostic/trace.duckdb      (full op trace)
- data/diagnostic/dashboard.pdf     (the report)
- data/diagnostic/metrics.json      (structured numeric results)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import torch

from hdlab import atoms, binding, bundling, learning, memory, modulators, store, tracing
from hdlab.dashboard.report import generate_report


def run_diagnostic() -> dict:
    name = "diagnostic"
    out_dir = Path("data") / name
    out_dir.mkdir(parents=True, exist_ok=True)

    bus = tracing.TraceBus(enabled=True)
    metrics: dict = {
        "run_name": name,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    with tracing.using(bus):
        gen = torch.Generator().manual_seed(42)
        n = 1024
        metrics["substrate"] = {"n": n, "dtype": "complex64", "seed": 42}

        # Phase 1: build a codebook of named atoms.
        codebook = memory.Codebook(n, torch.complex64)
        people = [f"person_{i:02d}" for i in range(20)]
        person_vecs = {}
        for name_ in people:
            v = atoms.make_atom_fhrr(n, gen)
            codebook.add(name_, v)
            person_vecs[name_] = v
        agent_role = atoms.make_atom_fhrr(n, gen)
        patient_role = atoms.make_atom_fhrr(n, gen)
        codebook.add("AGENT", agent_role)
        codebook.add("PATIENT", patient_role)

        # Phase 2: encode "loves(person_00, person_01)" and recover the agent by unbinding.
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

        # Phase 3: attention sweep on a noisy query.
        attention_results = []
        for att in [0.0, 0.2, 0.5]:
            with modulators.using(attention=att):
                jitter = (torch.rand(n, generator=gen) - 0.5) * 0.6
                rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(mary.dtype)
                noisy = mary * rot
                got, score = codebook.lookup(noisy)
                attention_results.append({"attention": att, "name": got, "score": float(score)})
        metrics["attention_sweep"] = attention_results

        # Phase 4: reward-modulated Hebbian over a small co-activation pattern.
        decay = 0.05
        h = learning.HebbianAssociations(decay=decay)
        steps = 400
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(steps):
                h.update(["person_00", "person_01"])
        w_empirical = h.weight("person_00", "person_01")
        w_theory = 1.0 / decay  # eta * activation / decay; here eta = arousal*reward = 1
        metrics["hebbian"] = {
            "decay": decay,
            "steps": steps,
            "empirical": float(w_empirical),
            "theoretical": float(w_theory),
            "ratio": float(w_empirical / w_theory),
        }

    events = bus.flush()
    metrics["total_events"] = len(events)
    metrics["total_wall_time_us"] = sum(e.elapsed_ns for e in events) / 1000.0

    # Persist artifacts.
    trace_path = out_dir / "trace.duckdb"
    if trace_path.exists():
        trace_path.unlink()
    with store.TraceStore(trace_path) as ts:
        ts.append(events)

    pdf_path = out_dir / "dashboard.pdf"
    extra = {
        "agent_recovery": f"{metrics['agent_recovery']['got']} (sim={metrics['agent_recovery']['score']:.3f})",
        "hebbian_ratio_to_theory": f"{metrics['hebbian']['ratio']:.4f}",
    }
    generate_report(events, pdf_path, run_name=name, extra=extra)

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))

    # Append a one-line summary to the rolling results log.
    results_md = Path("RESULTS.md")
    if not results_md.exists():
        results_md.write_text(
            "# Results log\n\n"
            "| Date | Experiment | Outcome | Key metric | Notes |\n"
            "|---|---|---|---|---|\n"
        )
    agent_ok = metrics["agent_recovery"]["got"] == metrics["agent_recovery"]["expected"]
    hebbian_ratio = metrics["hebbian"]["ratio"]
    outcome = "PASS" if agent_ok and 0.99 < hebbian_ratio < 1.01 else "REVIEW"
    line = (
        f"| {metrics['timestamp'][:10]} "
        f"| {name} "
        f"| {outcome} "
        f"| Hebbian ratio={hebbian_ratio:.4f}, agent_sim={metrics['agent_recovery']['score']:.3f} "
        f"| [pdf]({pdf_path.as_posix()}) [trace]({trace_path.as_posix()}) [metrics]({metrics_path.as_posix()}) |\n"
    )
    with results_md.open("a", encoding="utf-8") as fh:
        fh.write(line)

    return metrics


def main() -> None:
    m = run_diagnostic()
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
