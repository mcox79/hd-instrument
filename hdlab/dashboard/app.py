"""Streamlit dashboard for live observability. Run with: streamlit run hdlab/dashboard/app.py.

Primary observability output is the PDF report at `python -m hdlab.dashboard`; this Streamlit
app is here for interactive exploration when you want to dial things live.
"""

from __future__ import annotations

from pathlib import Path

from hdlab import store
from hdlab.dashboard.report import events_to_df, hebbian_weights_df


def main() -> None:
    import streamlit as st  # imported lazily so non-dashboard code paths don't need streamlit

    st.set_page_config(page_title="hd-instrument", layout="wide")
    st.title("hd-instrument observability")

    default_path = "data/trace.duckdb"
    store_path = st.sidebar.text_input("Trace store path", value=default_path)
    if not Path(store_path).exists():
        st.warning(f"No trace file at {store_path}. Run an experiment first.")
        return

    with store.TraceStore(store_path) as ts:
        events = ts.all_events()

    df = events_to_df(events)
    hw = hebbian_weights_df(events)

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
        pivoted = hw.pivot_table(index="hebbian_step", columns="pair", values="weight")
        st.line_chart(pivoted)

    st.subheader("Recent events")
    st.dataframe(df.tail(100))


if __name__ == "__main__":
    main()
