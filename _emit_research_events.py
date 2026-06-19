"""Emit experiment_research events for completed wave14c agents (registry tab spec)."""
import sys
sys.path.insert(0, r"d:\AI\hd-instrument")
from hdlab.session_log import log_event

log_event("experiment_research",
          name="r3_disjoint_K16",
          level="exhaustive",
          notes=["notes/wave14c_r3_disjoint_K_flatness_research.md"])

log_event("experiment_research",
          name="r3_disjoint_K32",
          level="exhaustive",
          notes=["notes/wave14c_r3_disjoint_K_flatness_research.md"])

log_event("experiment_research",
          name="r3_unigram_diagnostic",
          level="exhaustive",
          notes=["notes/wave14c_r3_unigram_failure_research.md"])

log_event("experiment_research",
          name="replay_preshift_K4",
          level="exhaustive",
          notes=["notes/wave14c_stein_pred1_rejection_research.md"])

log_event("experiment_research",
          name="r10_best_config_K2_K4_K8",
          level="in-progress",
          notes=[])

log_event("experiment_research",
          name="r10_best_config_K512",
          level="in-progress",
          notes=[])

print("Emitted 6 experiment_research events to session_events.jsonl")
