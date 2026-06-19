"""Emit the 4 missing experiment_outcome events."""
import sys
from pathlib import Path
sys.path.insert(0, r"D:\AI\hd-instrument")
sys.path.insert(0, r"C:\dev\hd-instrument")
from hdlab.session_log import log_event

log_event("experiment_outcome",
          name="r10_best_config_K8_verify",
          verdict="positive",
          summary="K=8 best-config verified at +0.142 (3 seeds, sd 0.021) vs default near-zero. K-curve K=8 to K=512 now multi-seed monotone confirmed.",
          headline=True,
          metrics_path="data/exp_wave14b_r10_best_config_K8_verify/metrics.json")

log_event("experiment_outcome",
          name="r3_disjoint_K64",
          verdict="negative",
          summary="HYPOTHESIS REJECTED. R3-disjoint compound delta -0.0003 at K=64 (vs +0.025 at K=4). Both r3same and r3disj near-zero -- R3 entirely dies at K=64 regardless of source. Confirms R3 is low-K-only.",
          headline=False,
          metrics_path="data/exp_wave14b_r3_disjoint_K64/metrics.json")

log_event("experiment_outcome",
          name="acf_K_dependent_extended_redo",
          verdict="positive",
          summary="Cross-validates the extended ACF K-sweep. K=2944 dip reproduces (50%); cliff substructure is real.",
          headline=False,
          metrics_path="data/exp_wave14b_acf_K_dependent_extended_redo/metrics.json")

log_event("experiment_outcome",
          name="acf_K2944_100trials",
          verdict="inconclusive",
          summary="K=2944 dip is REAL but smaller than 30-trial measurement. 100 trials gives 61.0% (vs 50% at 30 trials, 75% smooth interpolation). Sub-step in cliff confirmed but magnitude overestimated initially.",
          headline=False,
          metrics_path="data/exp_wave14b_acf_K2944_100trials/metrics.json")

print("Emitted 4 experiment_outcome events.")
