"""SKUNKWORKS AUDITOR probe: prove (or refute) the local-stale-SMOKE vs remote-FULL gap on live cases.
Read-only; SSHes marsh@home via the existing get_remote_metrics path (12s timeout/fetch). No compute."""
import sys
sys.path.insert(0, r"D:\AI\hd-instrument")
from tools.orchestrator.remote_state import get_remote_metrics, get_local_metrics

def vN(d):
    if not d:
        return ("--", "--", "--")
    cfg = d.get("config") or {}
    N = d.get("N") if d.get("N") is not None else cfg.get("N")
    rm = d.get("run_mode") or cfg.get("mode")
    return (str(d.get("verdict")), str(N), str(rm))

anchors = [
    "wave14_saddle_cascade_plateau_v6_n4096_gpu",          # documented local-smoke / remote-full case
    "substrate_drosophila_mb_sparse_single_modulator_v1_n4096",  # local HARD_FAIL smoke N=256
    "substrate_stage_a_bio_smoke_B5_stdp_replay_v1",       # local HARD_FAIL
    "substrate_tier6_phase_D_4layer_charLM_shakespeare_CPU_v1",   # scorecard FLAGSHIP; local MIDDLE-smoke
    "substrate_efficiency_composition_b3axb3b_v1_n2048",   # local MIDDLE_BAND
]
print(f"{'anchor':52} | {'LOCAL v/N/mode':28} | {'REMOTE v/N/mode':28}")
print("-" * 116)
n_remote_ok = 0
for a in anchors:
    loc = get_local_metrics(a)
    rem = get_remote_metrics(a)
    if rem is not None:
        n_remote_ok += 1
    lv = "/".join(vN(loc)); rv = "/".join(vN(rem)) if rem else "NO-REMOTE (unreachable/absent)"
    print(f"{a[:52]:52} | {lv:28} | {rv:28}")
print(f"\nremote reachable on {n_remote_ok}/{len(anchors)} fetches")
