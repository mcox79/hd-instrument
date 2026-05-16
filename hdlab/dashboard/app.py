"""Streamlit dashboard for live observability. Run with: streamlit run hdlab/dashboard/app.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from hdlab import store
from hdlab.tracing import TraceEvent


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
    return pd.DataFrame(rows)


def hebbian_weights_at(events: list[TraceEvent]) -> pd.DataFrame:
    """Reconstruct Hebbian weight time series from learning.update events."""
    rows = []
    for e in events:
        if e.op == "learning.update":
            rows.append(
                {
                    "step": e.step,
                    "hebbian_step": e.inputs.get("hebbian_step"),
                    "a": e.inputs.get("a"),
                    "b": e.inputs.get("b"),
                    "delta": e.inputs.get("delta"),
                    "weight": e.output.get("weight") if isinstance(e.output, dict) else None,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    import streamlit as st  # imported lazily so non-dashboard code paths don't need streamlit

    st.set_page_config(page_title="hd-instrument", layout="wide")
    st.title("hd-instrument observability")

    default_path = "data/trace.duckdb"
    store_path = st.sidebar.text_input("Trace store path", value=default_path)
    if not Path(store_path).exists():
        st.warning(f"No trace file at {store_path}. Run an experiment first.")
        st.code("from hdlab import tracing, store\nbus = tracing.TraceBus(enabled=True)\nwith tracing.using(bus):\n    ...  # run some ops\nts = store.TraceStore('data/trace.duckdb')\nts.append(bus.flush()); ts.close()")
        return

    with store.TraceStore(store_path) as ts:
        events = ts.all_events()

    df = events_to_df(events)
    hw = hebbian_weights_at(events)

    st.metric("Total events", len(events))
    if len(events):
        st.metric("Total wall time (ms)", f"{df['elapsed_ns'].sum() / 1e6:.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Modulator timeline")
        if not df.empty:
            mod_df = df.set_index("step")[["attention", "reward", "arousal", "recency"]]
            st.line_chart(mod_df)

    with col2:
        st.subheader("Op frequency")
        if not df.empty:
            st.bar_chart(df["op"].value_counts())

    st.subheader("Per-op latency (ns) summary")
    if not df.empty:
        st.dataframe(df.groupby("op")["elapsed_ns"].agg(["mean", "max", "count"]).reset_index())

    if not hw.empty:
        st.subheader("Hebbian weight trajectories")
        pivoted = hw.assign(pair=hw["a"] + "|" + hw["b"]).pivot_table(
            index="hebbian_step", columns="pair", values="weight"
        )
        st.line_chart(pivoted)

    st.subheader("Recent events")
    st.dataframe(df.tail(100))


if __name__ == "__main__":
    main()
