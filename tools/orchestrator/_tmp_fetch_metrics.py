import sys
sys.path.insert(0, r"d:\AI\hd-instrument")
from tools.orchestrator.remote_state import get_metrics, is_stale

print("bridge_stale:", is_stale())
anchors = [
    "khop_bundle_noise_battery_gpu_v1",
    "khop_sparse_bsweep_battery_gpu_v1",
    "khop_noise_model_AB_compare_gpu_v1",
    "lvh245_mmr_topology_spectral_gap_v1",
    "zkl_curve_k_sweep_realkeys_v1"
]
for a in anchors:
    m = get_metrics(a)
    if m:
        print("---", a, "---")
        print("  source:", m.get("_source","?"), "| verdict:", m.get("verdict","?"))
        print("  verdict_msg:", str(m.get("verdict_msg","?"))[:300])
        print("  elapsed_s:", m.get("elapsed_s","?"))
        for k, v in m.items():
            if k not in ("_source","verdict","verdict_msg","elapsed_s","summary") and not k.startswith("_"):
                print("  ", k, ":", str(v)[:400])
    else:
        print("---", a, "--- NOT FOUND (None)")
