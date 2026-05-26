"""Backward-compatibility shim — do not import directly in new code.

All functions live in tools.orchestrator.state now.  This module re-exports
them so existing callers (orchestrator_prompt scripts, notebooks, etc.) that
do::

    from tools.orchestrator.in_flight import record_dispatch, clear_dispatch

…continue to work without modification.
"""

from tools.orchestrator.state import (  # noqa: F401  (re-export)
    record_dispatch,
    clear_dispatch,
    clear_all_dispatches,
    list_dispatches,
)
