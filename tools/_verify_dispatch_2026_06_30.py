"""Quick verify of the 6 dispatch verdicts. One-shot."""
import json, os, sys
targets = [
    "exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_7",
    "exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_13",
    "exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_19",
    "exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_7",
    "exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_13",
    "exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_19",
]
for t in targets:
    p = os.path.join("data", t, "metrics.json")
    if not os.path.exists(p):
        print(f"{t}: MISSING_METRICS")
        continue
    m = json.load(open(p))
    print(f"{t}: verdict={m.get('verdict')} run_mode={m.get('run_mode')} elapsed_s={m.get('elapsed_s')} n_seeds={m.get('n_seeds')} cardinality_ok={m.get('cardinality_ok')}")
    vm = m.get("verdict_msg", "")[:200]
    print(f"  verdict_msg: {vm}")
