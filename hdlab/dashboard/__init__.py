"""PDF + Streamlit dashboards for hd-instrument observability."""

from .report import (
    cleanup_lookup_df,
    events_to_df,
    generate_report,
    hebbian_weights_df,
)

__all__ = [
    "generate_report",
    "events_to_df",
    "hebbian_weights_df",
    "cleanup_lookup_df",
]
