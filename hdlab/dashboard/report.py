"""Multi-page PDF dashboard report generated with matplotlib + PdfPages."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend; no display needed

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from hdlab.tracing import TraceEvent  # noqa: E402


def events_to_df(events: list[TraceEvent]) -> pd.DataFrame:
    """Flatten a list of TraceEvents into a tabular DataFrame for plotting."""
    rows: list[dict[str, Any]] = []
    for e in events:
        ms = e.modulator_state or {}
        rows.append(
            {
                "step": e.step,
                "op": e.op,
                "elapsed_ns": e.elapsed_ns,
                "timestamp_ns": e.timestamp_ns,
                "attention": ms.get("attention", 0.0),
                "reward": ms.get("reward", 0.0),
                "arousal": ms.get("arousal", 1.0),
                "recency": ms.get("recency", 0.0),
            }
        )
    cols = ["step", "op", "elapsed_ns", "timestamp_ns", "attention", "reward", "arousal", "recency"]
    return pd.DataFrame(rows, columns=cols)


def hebbian_weights_df(events: list[TraceEvent]) -> pd.DataFrame:
    """Reconstruct Hebbian weight time series from learning.update events."""
    rows: list[dict[str, Any]] = []
    for e in events:
        if e.op == "learning.update":
            weight = e.output.get("weight") if isinstance(e.output, dict) else None
            rows.append(
                {
                    "hebbian_step": e.inputs.get("hebbian_step"),
                    "pair": f"{e.inputs.get('a')}|{e.inputs.get('b')}",
                    "weight": weight,
                }
            )
    return pd.DataFrame(rows, columns=["hebbian_step", "pair", "weight"])


def cleanup_lookup_df(events: list[TraceEvent]) -> pd.DataFrame:
    """Extract memory.lookup outcomes (name, score) for inspection."""
    rows: list[dict[str, Any]] = []
    for e in events:
        if e.op == "memory.lookup" and isinstance(e.output, dict):
            rows.append(
                {
                    "step": e.step,
                    "name": e.output.get("name"),
                    "score": e.output.get("score"),
                    "k": e.inputs.get("k"),
                }
            )
    return pd.DataFrame(rows, columns=["step", "name", "score", "k"])


def connection_trace_df(events: list[TraceEvent], query_id: str) -> pd.DataFrame:
    """Filter semantic events for a single query span and tabulate them by hop."""
    rows: list[dict[str, Any]] = []
    for e in events:
        if e.query_id != query_id or not e.op.startswith("semantic."):
            continue
        rows.append(
            {
                "step": e.step,
                "op": e.op,
                "hop_idx": e.inputs.get("hop_idx"),
                "relation": e.inputs.get("relation"),
                "src": e.inputs.get("src"),
                "dst": e.inputs.get("dst"),
                "weight": e.inputs.get("weight"),
                "score": e.inputs.get("score"),
                "target_name": e.inputs.get("target_name"),
                "contribution": e.inputs.get("contribution"),
                "n_edges_fired": e.inputs.get("n_edges_fired"),
            }
        )
    cols = ["step", "op", "hop_idx", "relation", "src", "dst", "weight", "score", "target_name", "contribution", "n_edges_fired"]
    return pd.DataFrame(rows, columns=cols)


def _page_overview(pdf: PdfPages, df: pd.DataFrame, run_name: str, extra: dict | None) -> None:
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_subplot(111)
    ax.axis("off")

    lines: list[str] = [
        "hd-instrument session report",
        f"Run: {run_name}",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Total events: {len(df)}",
    ]
    if not df.empty:
        total_us = df["elapsed_ns"].sum() / 1000.0
        lines.append(f"Total recorded wall time: {total_us:,.1f} us")
        lines.append(f"Distinct ops: {df['op'].nunique()}")
        lines.append("")
        lines.append("Op counts:")
        for op, count in df["op"].value_counts().items():
            lines.append(f"  {op:<32s} {count}")
    if extra:
        lines.append("")
        lines.append("Notes:")
        for k, v in extra.items():
            lines.append(f"  {k}: {v}")

    ax.text(0.05, 0.95, "\n".join(lines), va="top", ha="left", fontsize=10, family="monospace")
    pdf.savefig(fig)
    plt.close(fig)


def _page_modulators(pdf: PdfPages, df: pd.DataFrame) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 8.5))
    for col in ["attention", "reward", "arousal", "recency"]:
        ax.plot(df["step"], df[col], label=col, linewidth=1.2)
    ax.set_xlabel("event step")
    ax.set_ylabel("modulator value")
    ax.set_title("Modulator timeline")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    pdf.savefig(fig)
    plt.close(fig)


def _page_op_stats(pdf: PdfPages, df: pd.DataFrame) -> None:
    if df.empty:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))

    counts = df["op"].value_counts()
    ax1.barh(counts.index, counts.values, color="steelblue")
    ax1.set_title("Op frequency")
    ax1.set_xlabel("count")
    ax1.invert_yaxis()

    grouped = df.groupby("op")["elapsed_ns"].agg(["mean", "max"]).sort_values("mean", ascending=True)
    ax2.barh(grouped.index, grouped["max"].values, label="max", color="tomato", alpha=0.45)
    ax2.barh(grouped.index, grouped["mean"].values, label="mean", color="darkred")
    ax2.set_title("Per-op latency (ns)")
    ax2.set_xlabel("ns")
    ax2.legend()

    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _page_hebbian(pdf: PdfPages, hw: pd.DataFrame) -> None:
    if hw.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 8.5))
    for pair, group in hw.groupby("pair"):
        ax.plot(group["hebbian_step"], group["weight"], label=pair, marker=".", markersize=2, linewidth=1)
    ax.set_xlabel("Hebbian step")
    ax.set_ylabel("association weight")
    ax.set_title("Hebbian weight trajectories")
    if hw["pair"].nunique() <= 10:
        ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    pdf.savefig(fig)
    plt.close(fig)


def _page_cleanup(pdf: PdfPages, cu: pd.DataFrame) -> None:
    if cu.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 8.5))
    accepted = cu[cu["name"].notna()]
    rejected = cu[cu["name"].isna()]
    if not accepted.empty:
        ax.scatter(accepted["step"], accepted["score"], color="seagreen", label="accepted", s=20)
    if not rejected.empty:
        ax.scatter(rejected["step"], rejected["score"], color="firebrick", label="rejected", s=20, marker="x")
    ax.set_xlabel("event step")
    ax.set_ylabel("similarity score")
    ax.set_title("Cleanup outcomes")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    pdf.savefig(fig)
    plt.close(fig)


def _page_connection_trace(pdf: PdfPages, events: list[TraceEvent], query_id: str) -> None:
    """Render the connection trace for a single query span: hop-by-hop edges and cleanups."""
    df = connection_trace_df(events, query_id)
    if df.empty:
        return

    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 2, 2])

    # Header with query metadata
    ax_h = fig.add_subplot(gs[0])
    ax_h.axis("off")
    start = [e for e in events if e.op == "semantic.query_start" and e.query_id == query_id]
    answer = [e for e in events if e.op == "semantic.query_answer" and e.query_id == query_id]
    abl = [e for e in events if e.op == "semantic.ablation_active" and e.query_id == query_id]
    header: list[str] = [f"Connection trace for query: {query_id}"]
    if start:
        header.append(f"Span inputs: {start[0].inputs}")
        if start[0].tags:
            header.append(f"Span tags: {start[0].tags}")
    if abl:
        header.append("Ablations active in this span:")
        for e in abl:
            header.append(f"  - {e.inputs['target_kind']}: {e.inputs['target_id']}")
    if answer:
        a = answer[0]
        header.append(f"Answer: {a.output.get('answer')}  confidence={a.inputs.get('confidence'):.3f}  hops={a.inputs.get('hops_taken')}")
    ax_h.text(0.0, 1.0, "\n".join(header), va="top", ha="left", fontsize=9, family="monospace")

    # Edge traversals per hop (scatter w/ weight on y, hop on x, color per relation)
    ax_e = fig.add_subplot(gs[1])
    edges = df[df["op"] == "semantic.edge_traversed"].dropna(subset=["hop_idx"])
    if not edges.empty:
        relations = sorted(edges["relation"].dropna().unique().tolist())
        cmap = plt.get_cmap("tab10")
        for i, rel in enumerate(relations):
            r = edges[edges["relation"] == rel]
            ax_e.scatter(r["hop_idx"], r["weight"], label=rel, color=cmap(i % 10), s=30, alpha=0.85)
            for _, row in r.iterrows():
                ax_e.annotate(
                    f"{row['src']}->{row['dst']}",
                    (row["hop_idx"], row["weight"]),
                    fontsize=6,
                    alpha=0.7,
                    xytext=(3, 3),
                    textcoords="offset points",
                )
        ax_e.set_xlabel("hop")
        ax_e.set_ylabel("edge weight")
        ax_e.set_title("Edges traversed per hop, colored by relation")
        ax_e.legend(loc="best", fontsize=8)
        ax_e.grid(True, alpha=0.3)
    else:
        ax_e.text(0.5, 0.5, "no edge_traversed events", ha="center", va="center")
        ax_e.axis("off")

    # Cleanup hits per hop (line of accepted scores)
    ax_c = fig.add_subplot(gs[2])
    hits = df[df["op"] == "semantic.cleanup_hit"].dropna(subset=["hop_idx"])
    if not hits.empty:
        ax_c.plot(hits["hop_idx"], hits["score"], marker="o", linewidth=1.5, color="steelblue")
        for _, row in hits.iterrows():
            ax_c.annotate(
                str(row["target_name"]),
                (row["hop_idx"], row["score"]),
                fontsize=7,
                xytext=(3, 3),
                textcoords="offset points",
            )
        ax_c.set_xlabel("hop")
        ax_c.set_ylabel("cleanup similarity")
        ax_c.set_title("Cleanup hits per hop (target = projected entity)")
        ax_c.grid(True, alpha=0.3)
    else:
        ax_c.text(0.5, 0.5, "no cleanup_hit events", ha="center", va="center")
        ax_c.axis("off")

    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _page_query_summary(pdf: PdfPages, events: list[TraceEvent]) -> None:
    """One-page summary of all query spans in the trace."""
    spans: dict[str, dict[str, Any]] = {}
    for e in events:
        if e.query_id is None:
            continue
        s = spans.setdefault(e.query_id, {"start_step": e.step, "end_step": e.step, "n_events": 0, "tags": {}})
        s["end_step"] = max(s["end_step"], e.step)
        s["n_events"] += 1
        if e.tags:
            s["tags"].update(e.tags)
        if e.op == "semantic.query_answer":
            s["answer"] = e.output.get("answer") if isinstance(e.output, dict) else None
            s["confidence"] = e.inputs.get("confidence")
            s["hops_taken"] = e.inputs.get("hops_taken")
    if not spans:
        return
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    lines = ["Query spans in this session", ""]
    lines.append(f"{'query_id':<24s} {'events':>6s} {'hops':>5s} {'conf':>6s}  answer")
    for qid, s in spans.items():
        ans = str(s.get("answer", ""))[:30]
        conf = s.get("confidence")
        hops = s.get("hops_taken")
        lines.append(
            f"{qid:<24s} {s['n_events']:>6d} {('-' if hops is None else hops):>5} "
            f"{('-' if conf is None else f'{conf:.3f}'):>6}  {ans}"
        )
    ax.text(0.02, 0.98, "\n".join(lines), va="top", ha="left", fontsize=9, family="monospace")
    pdf.savefig(fig)
    plt.close(fig)


def _page_recent_events(pdf: PdfPages, df: pd.DataFrame, n_recent: int = 40) -> None:
    if df.empty:
        return
    cols = ["step", "op", "elapsed_ns", "attention", "reward", "arousal", "recency"]
    recent = df.tail(n_recent)[cols]

    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    cell_text = [[f"{v}" for v in row] for row in recent.values]
    table = ax.table(
        cellText=cell_text,
        colLabels=recent.columns.tolist(),
        loc="upper center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1.0, 1.2)
    ax.set_title(f"Last {len(recent)} events", pad=20)
    pdf.savefig(fig)
    plt.close(fig)


def generate_report(
    events: list[TraceEvent],
    output_path: Path | str,
    run_name: str = "session",
    extra: dict | None = None,
    extra_pages: list[Any] | None = None,
) -> Path:
    """Write a multi-page PDF dashboard for a sequence of TraceEvents.

    `extra_pages`: optional list of callables each taking a PdfPages instance, appended after
    the standard pages. Use this to attach experiment-specific headline plots.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = events_to_df(events)
    hw = hebbian_weights_df(events)
    cu = cleanup_lookup_df(events)

    query_ids = sorted({e.query_id for e in events if e.query_id is not None})

    with PdfPages(output_path) as pdf:
        _page_overview(pdf, df, run_name, extra)
        _page_modulators(pdf, df)
        _page_op_stats(pdf, df)
        _page_hebbian(pdf, hw)
        _page_cleanup(pdf, cu)
        if query_ids:
            _page_query_summary(pdf, events)
            for qid in query_ids:
                _page_connection_trace(pdf, events, qid)
        _page_recent_events(pdf, df)
        if extra_pages:
            for page_fn in extra_pages:
                page_fn(pdf)

    return output_path
