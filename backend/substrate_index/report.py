"""Report generator for substrate self-index findings.

Two flow patterns:
1. **Automated weekly/cycle report**: triggered by evolve.py after a cap_map
   cycle ingest; runs discover + meta + spectral observability; emits a
   templated markdown note ready to file as
   `testbed_to_research_INDEX_FINDINGS_<NNN>_<date>.md`.
2. **On-demand analysis report**: triggered by Research filing a
   `research_to_testbed_INDEX_QUERY_*.md` note; runs the requested analysis
   and emits a focused reply.

The output format follows the project's note conventions: short header +
TL;DR + structured sections. Notes are written to a path the caller chooses
(usually `notes/testbed_to_research_INDEX_FINDINGS_<NNN>_<date>.md`).
"""
from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.substrate_index.discover import DiscoveryReport, Finding, discover_all
from backend.substrate_index.meta import (
    describe_self,
    identify_exposed_atoms,
    identify_strongest_claims,
    summarize_state,
)
from backend.substrate_index.metrics import SystemDiagnostic, render_report
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever


# ============================================================
# Section helpers
# ============================================================


def _section_tldr(state, n_findings: int, top_findings: list[Finding]) -> str:
    parts = [
        f"- **{state.total_atoms}** atoms across {len(state.atoms_by_corpus)} partitions; "
        f"**{state.total_relations}** relations ({state.cross_corpus_relations} cross-corpus).",
        f"- Discovery surfaced **{n_findings}** findings this run.",
    ]
    if top_findings:
        parts.append(f"- Most-actionable finding: **{top_findings[0].hypothesis}**")
    return "\n".join(parts)


def _section_findings_grouped(findings: tuple[Finding, ...]) -> str:
    """Group findings by kind, render as collapsible-style markdown."""
    by_kind = {}
    for f in findings:
        by_kind.setdefault(f.kind, []).append(f)
    lines = []
    for kind, group in sorted(by_kind.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {kind} ({len(group)} found)")
        lines.append("")
        for f in group[:8]:  # cap per-kind detail
            subj = ", ".join(f.subject) if len(f.subject) <= 3 else (
                ", ".join(f.subject[:3]) + f", +{len(f.subject) - 3} more"
            )
            lines.append(f"- **{f.severity}** | {subj}")
            lines.append(f"  - {f.hypothesis}")
            lines.append(f"  - *Suggested:* {f.suggested_action}")
        if len(group) > 8:
            lines.append(f"- ... and {len(group) - 8} more findings of this kind.")
        lines.append("")
    return "\n".join(lines)


def _section_strongest_claims(claims) -> str:
    if not claims:
        return ""
    lines = ["### Strongest concept claims by structural support", ""]
    lines.append("| atom | score | validates_in | uses_out | cross | refutes_in |")
    lines.append("|---|---|---|---|---|---|")
    for c in claims[:10]:
        lines.append(
            f"| {c.atom_id} ({c.name}) | {c.score} | {c.validates_in} | "
            f"{c.uses_out} | {c.cross_corpus_uses} | {c.refutes_in} |"
        )
    return "\n".join(lines)


def _section_exposed_atoms(exposed) -> str:
    if not exposed:
        return ""
    lines = ["### Most exposed math atoms (high fan-in, weak own support)", ""]
    lines.append("| atom | exposure | fan_in | fan_out | own_support |")
    lines.append("|---|---|---|---|---|")
    for e in exposed[:10]:
        lines.append(
            f"| {e.atom_id} ({e.name}) | {e.exposure_score} | "
            f"{e.fan_in} | {e.fan_out} | {e.own_support} |"
        )
    return "\n".join(lines)


# ============================================================
# Main report renderer
# ============================================================


def render_findings_note(
    pstore: PartitionedStore,
    retriever: Optional[Retriever] = None,
    bench_diagnostic: Optional[SystemDiagnostic] = None,
    n_revision: int = 0,
    notes: str = "",
) -> tuple[str, dict]:
    """Render a full findings note for Research + return the structured JSON
    payload for archival.

    Outputs:
        markdown_str: the full markdown note body
        payload:      dict with state + discovery + meta serialized
    """
    state = summarize_state(pstore)
    report = discover_all(pstore, retriever=retriever)
    strong = identify_strongest_claims(pstore, top_n=10)
    exposed = identify_exposed_atoms(pstore, top_n=10)

    ranked = sorted(
        report.findings,
        key=lambda f: ({"warning": 0, "suggest": 1, "info": 2}.get(f.severity, 3), -f.confidence),
    )

    lines = []
    lines.append(f"# Testbed -> Research: substrate self-index findings #{n_revision}")
    lines.append("")
    lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    if notes:
        lines.append(notes)
        lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    lines.append(_section_tldr(state, len(report.findings), ranked))
    lines.append("")
    lines.append("## State summary")
    lines.append("")
    lines.append(describe_self(pstore))
    lines.append("")
    if bench_diagnostic is not None:
        lines.append("## Benchmark scores")
        lines.append("")
        lines.append(f"- mean recall@1: {bench_diagnostic.mean_recall_at_1:.3f}")
        lines.append(f"- mean recall@3: {bench_diagnostic.mean_recall_at_3:.3f}")
        lines.append(f"- mean MRR: {bench_diagnostic.mean_mrr:.3f}")
        lines.append(f"- mean NDCG: {bench_diagnostic.mean_ndcg:.3f}")
        lines.append(f"- mean latency: {bench_diagnostic.mean_latency_ms:.1f} ms")
        if bench_diagnostic.substrate_wins or bench_diagnostic.llm_wins or bench_diagnostic.ties:
            lines.append(
                f"- substrate vs LLM: wins {bench_diagnostic.substrate_wins} / "
                f"losses {bench_diagnostic.llm_wins} / ties {bench_diagnostic.ties}"
            )
        lines.append("")
        lines.append("**Auto-generated improvement recommendations:**")
        for r in bench_diagnostic.recommendations:
            lines.append(f"- {r}")
        lines.append("")
    lines.append("## Discoveries (grouped by kind)")
    lines.append("")
    lines.append(_section_findings_grouped(report.findings))
    lines.append("")
    if strong:
        lines.append(_section_strongest_claims(strong))
        lines.append("")
    if exposed:
        lines.append(_section_exposed_atoms(exposed))
        lines.append("")

    markdown = "\n".join(lines)
    payload = {
        "state": state.to_dict(),
        "discovery": report.to_dict(),
        "strongest_claims": [c.to_dict() for c in strong],
        "exposed_atoms": [e.to_dict() for e in exposed],
        "bench_diagnostic": bench_diagnostic.to_dict() if bench_diagnostic else None,
        "generated_at": time.time(),
    }
    return markdown, payload


def write_findings_note(
    pstore: PartitionedStore,
    out_path: Path,
    retriever: Optional[Retriever] = None,
    bench_diagnostic: Optional[SystemDiagnostic] = None,
    n_revision: int = 0,
    notes: str = "",
) -> tuple[Path, Path]:
    """Render and write the findings note + JSON payload alongside.

    Returns: (markdown_path, json_path)
    """
    markdown, payload = render_findings_note(
        pstore, retriever, bench_diagnostic, n_revision, notes
    )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    json_path = out_path.with_suffix(".json")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path, json_path


# ============================================================
# Research-query reply builder
# ============================================================


@dataclass(frozen=True)
class ResearchQuery:
    """Structured form of a Research-initiated analysis question."""
    question: str
    target_atoms: tuple[str, ...] = ()         # optional qualified ids the
                                              # question is about
    analysis_kinds: tuple[str, ...] = ()       # 'centrality' / 'gap' /
                                              # 'transitive' / 'cluster' / etc.


def reply_to_research_query(
    pstore: PartitionedStore,
    query: ResearchQuery,
    retriever: Optional[Retriever] = None,
) -> str:
    """Render a focused reply to a Research-initiated query.

    The Research workflow file is `research_to_testbed_INDEX_QUERY_*.md`
    with a structured question. This renders a focused testbed reply that
    runs the requested analyses and reports the results.

    For now this is a structural sketch -- the analysis dispatching is
    pluggable. Actual analysis depth depends on populated corpus.
    """
    from backend.substrate_index.meta import knowledge_pertaining_to

    lines = []
    lines.append(f"# Testbed -> Research: reply to INDEX_QUERY")
    lines.append("")
    lines.append(f"**Question:** {query.question}")
    lines.append("")
    if query.target_atoms:
        lines.append("## Subject atoms")
        lines.append("")
        for atom_id in query.target_atoms:
            profile = knowledge_pertaining_to(pstore, atom_id, retriever=retriever)
            if profile is None:
                lines.append(f"- {atom_id}: **NOT IN CORPUS**")
                continue
            lines.append(f"### {profile.name} ({profile.qualified_id})")
            lines.append(f"- Corpus: {profile.corpus} / Tier: {profile.tier} / Kind: {profile.kind}")
            lines.append(f"- Description: {profile.description}")
            if profile.outgoing:
                lines.append(f"- Outgoing edges:")
                for rt, neighbors in profile.outgoing.items():
                    lines.append(f"  - {rt}: {', '.join(neighbors)}")
            if profile.incoming:
                lines.append(f"- Incoming edges:")
                for rt, neighbors in profile.incoming.items():
                    lines.append(f"  - {rt}: {', '.join(neighbors)}")
            if profile.semantic_top_5:
                lines.append(f"- Semantic neighbors: {', '.join(profile.semantic_top_5)}")
            if profile.isolation:
                lines.append("- **ISOLATED**: no relations of any kind")
            lines.append("")

    if "centrality" in query.analysis_kinds:
        from backend.substrate_index.discover import centrality_snapshot
        snap = centrality_snapshot(pstore)
        top10 = sorted(snap, key=lambda s: -(s.in_degree + s.out_degree))[:10]
        lines.append("## Top-10 centrality")
        lines.append("")
        for s in top10:
            lines.append(f"- {s.qid}: in={s.in_degree}, out={s.out_degree}")
        lines.append("")

    return "\n".join(lines)
