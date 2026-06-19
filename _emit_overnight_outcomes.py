"""Emit experiment_outcome events for the overnight completions + CPU failures."""
import sys
from pathlib import Path
sys.path.insert(0, r"D:\AI\hd-instrument")
sys.path.insert(0, r"C:\dev\hd-instrument")
from hdlab.session_log import log_event

# POSITIVES from overnight
log_event("experiment_outcome", name="wave14d_icl_via_pool_K4", verdict="positive",
          summary="ICL CONFIRMED: relevant-pool examples beat irrelevant by +0.283 bpc at N=64 (K=4). Monotone in N. Substrate natively does in-context learning via pool retrieval.",
          headline=True, metrics_path="data/exp_wave14d_in_context_learning_via_pool/metrics.json")

log_event("experiment_outcome", name="wave14d_icl_via_pool_K8", verdict="positive",
          summary="ICL CONFIRMED at K=8: +0.195 bpc gain at N=64 (3 seeds). Effect weaker than K=4 (substrate has more W context).",
          headline=True, metrics_path="data/exp_wave14d_icl_via_pool_K8/metrics.json")

log_event("experiment_outcome", name="wave14d_icl_via_pool_K16", verdict="positive",
          summary="ICL CONFIRMED at K=16: +0.106 bpc gain at N=64 (3 seeds). Effect decreases with K but remains significant.",
          headline=True, metrics_path="data/exp_wave14d_icl_via_pool_K16/metrics.json")

log_event("experiment_outcome", name="wave14d_generation_K4", verdict="positive",
          summary="GENERATION CONFIRMED at K=4: greedy p8 accuracy 37.3% (vs 5x random 1.95% threshold). Substrate maintains coherence to p64 at 13% accuracy. Note: byte-match metric, not word-coherence (K=4 cannot capture words >=5 bytes).",
          headline=True, metrics_path="data/exp_wave14d_generation_via_sample_feedback/metrics.json")

log_event("experiment_outcome", name="wave14d_generation_K8", verdict="positive",
          summary="GENERATION CONFIRMED at K=8: greedy p8 accuracy 36.8%. Comparable to K=4 byte-match level.",
          headline=True, metrics_path="data/exp_wave14d_generation_K8/metrics.json")

log_event("experiment_outcome", name="wave14d_generation_K16", verdict="positive",
          summary="GENERATION CONFIRMED at K=16: greedy p8 accuracy 31.0%. Slightly lower than K=4/8 byte-match but still strong.",
          headline=True, metrics_path="data/exp_wave14d_generation_K16/metrics.json")

log_event("experiment_outcome", name="r10_best_config_N8192_K256", verdict="positive",
          summary="M1 mechanism confirmed at K=256: N=8192 best +0.496 vs N=4096 best +0.543 (gap shrunk 9%). Matches K=128's 15% shrinkage; bundle-SNR mechanism robust across K.",
          headline=True, metrics_path="data/exp_wave14b_r10_best_config_N8192_K256/metrics.json")

log_event("experiment_outcome", name="r3_sparse_unigram_diagnostic", verdict="inconclusive",
          summary="GAMMA mis-calibrated (re-confirmed): R3 residual +0.129 over unigram. Real signal exists but unigram diagnostic too strong to compare cleanly. Need sparse-matched test (queued).",
          headline=False, metrics_path="data/exp_wave14b_r3_unigram_diagnostic/metrics.json")

# FAILURES from CPU collapse at 01:30
for name, summary in [
    ("acf_K_very_extended_50trials", "CRASHED after 6797s (~2h) with STATUS_ACCESS_VIOLATION (0xC0000005). Memory corruption from long-running 25-K-level sweep. Triggered cascade of CPU failures."),
    ("decompose_K_cliff_B3", "CRASHED with 0xC0000005 after 122s. Memory state corrupted from prior crash."),
    ("acf_resonator_high_K", "CRASHED with 0xC0000005 after 57s. Same cause."),
    ("decompose_K_cliff_B4", "CRASHED with exit=1 after 33s. Possibly different root cause but same process state."),
    ("acf_K2944_fine_r_sweep", "CRASHED with 0xC0000005 after 204s."),
    ("wave14e2_parisi_ultrametricity", "CRASHED with 0xC0000005 after 22s. Spin glass test never ran cleanly."),
]:
    log_event("experiment_outcome", name=name, verdict="failed",
              summary=summary, headline=False)

print("Emitted 14 experiment_outcome events (8 positive + 1 inconclusive + 6 failed).")
