"""Cross-check capability claims in BACKUP doc vs substrate atoms.jsonl + cert_ledger.

NOT permanent - audit-spawn artifact 2026-06-28.
"""
import os, json, glob, re
from collections import defaultdict

# Capabilities BACKUP marks CG (need to verify atom presence)
# Each row: (claim_label, search_keywords, expected_status_word_in_atoms)
backup_cg = [
    ("HRR_bind_unbind", ["hrr_bind", "hrr_unbind", "fhrr_bind"]),
    ("Cleanup_attractor", ["cleanup_attractor", "iterative_cleanup", "cleanup_floor"]),
    ("Pattern_completion_cliff_v2p2", ["pattern_completion_corruption_cliff_v2p2", "pattern_completion_corruption_cliff_v2.2"]),
    ("Sequence_binding_K_cliff_v2", ["sequence_binding_k_cliff", "sequence_binding_full_v2", "seq_binding_k_cliff"]),
    ("WM_multi_bank_K_cliff_v3", ["wm_multibank_K_cliff", "wm_multi_bank_k_cliff", "wm_k_cliff_v3", "wm_multibank_k_cliff_v3"]),
    ("Refuse_gate_V_REL_256", ["refuse_gate", "v_rel"]),
    ("Continual_CRISPR", ["continual_learning_crispr", "cl_crispr"]),
    ("KG_FB15k", ["fb15k", "freebase"]),
    ("KG_ConceptNet", ["conceptnet"]),
    ("KG_HotpotQA", ["hotpotqa", "hotpot_qa"]),
    ("Partition_routing_10M", ["partition_routing", "partition_oracle"]),
    ("Intent_classifier_n100", ["intent_classifier"]),
    ("Capacity_multibank_alpha_K", ["capacity_multibank_alpha_k", "capacity_multi_bank_alpha_k"]),
    ("TWO_TIER_generational_W", ["two_tier", "generational_w"]),
    ("NREM_replay", ["nrem_replay", "nrem"]),
    ("ULTRAMETRIC_clustering", ["ultrametric_clustering", "ultrametric"]),
    ("ANCHOR1_partition_by_source", ["anchor1_partition_by_source", "partition_by_source", "anchor_1"]),
    ("Lock_in_amp", ["lock_in_amp", "lock_in_amplifier"]),
    ("Order_sensitive_seq_binding", ["order_sensitive", "seq_binding"]),
    ("ANCHOR3_coarse_grain", ["coarse_grain", "anchor3_coarse_grain", "anchor_3"]),
    ("ANCHOR4_time_decay_eviction", ["time_decay_eviction", "anchor4_time_decay", "anchor_4"]),
    ("Schema_exemplar_Bayes", ["schema_exemplar_bayes", "exemplar_bayes"]),
    ("Multi_hop_depth_15_partition_oracle", ["multihop", "depth_15", "partition_oracle_hardened"]),
    ("Compositional_generation_0p724", ["compositional_generation_lift", "compositional_gen"]),
    ("TASK_VECTOR_HRR_ICL_K_cliff", ["task_vector_k_cliff", "task_vector_hrr_icl"]),
    ("TOM_Sally_Anne_2nd_order", ["tom_sally_anne", "sally_anne", "tom_2nd"]),
    ("CF_regret_vmPFC", ["cf_regret", "vmpfc"]),
    ("CF_latency_delta_stack", ["cf_latency", "delta_stack"]),
    ("Cross_modal_visual_auditory", ["cross_modal_binding", "cross_modal_visual"]),
    ("Sequence_binding_narrative_Q3", ["sequence_binding_narrative", "narrative_q3"]),
    ("Parietal_MOVABLE_rebind", ["parietal_movable_rebind", "parietal_movable"]),
    ("Parietal_RELATIONAL_spatial", ["parietal_relational_spatial", "parietal_relational"]),
]

# Capabilities BACKUP marks CLOSED-negative - need 2x drill closure
backup_closed_neg = [
    ("Higher_order_TOM_3rd", ["higher_order_tom", "tom_3rd", "tom_recursive"]),
    ("Long_narrative_Q2_coref", ["long_narrative_q2", "coref", "lappin_leass", "hrr_recency"]),
    ("Barrier_1_hint_derivation", ["barrier_1", "hint_derivation"]),
    ("Hierarchical_planning_substrate_native", ["hierarchical_planning"]),
    ("Four_primitive_brain_composition", ["4_primitive_brain", "brain_composition", "primitive_brain_composition"]),
    ("CLS_handoff_chain_grade_M8192", ["cls_handoff", "cortex_hippo_handoff"]),
]

# Load atom IDs across all partitions
atom_idx = []  # list of (partition, atom_id_lower, atom_record)
for ppath in glob.glob('data/substrate_index/*/atoms.jsonl'):
    partition = os.path.basename(os.path.dirname(ppath))
    with open(ppath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            aid = (a.get('id', '') or a.get('atom_id', ''))
            if aid:
                atom_idx.append((partition, aid.lower(), a))

print(f'Loaded {len(atom_idx)} atom records.')

# Load ledger as atom_id -> latest record
ledger_by_aid = {}
with open('data/substrate_index/meta/cert_ledger.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        r = json.loads(line)
        aid = r.get('atom_id') or ''
        aid = aid.lower() if isinstance(aid, str) else ''
        if aid:
            ledger_by_aid.setdefault(aid, []).append(r)

def search(keywords):
    matches = []
    for partition, aid_l, a in atom_idx:
        for kw in keywords:
            if kw.lower() in aid_l:
                matches.append((partition, a.get('id', a.get('atom_id', '')), a))
                break
    return matches

def search_ledger(keywords):
    matches = []
    for aid_l, recs in ledger_by_aid.items():
        for kw in keywords:
            if kw.lower() in aid_l:
                latest = recs[-1]
                matches.append((aid_l, latest.get('cert_status', ''), latest.get('verdict', '')))
                break
    return matches

print('\n=== BACKUP CG capabilities vs atoms ===')
no_cg_in_ledger = []
for label, kws in backup_cg:
    atoms = search(kws)
    ledger = search_ledger(kws)
    chain_grade_count = sum(1 for _, st, _ in ledger if st == 'chain_grade')
    if not atoms and not ledger:
        print(f'  MISSING: {label} -- no atoms, no ledger entries')
        no_cg_in_ledger.append((label, 'NO_ATOMS_NO_LEDGER'))
    elif chain_grade_count == 0:
        statuses = [s for _, s, _ in ledger][:5]
        print(f'  NO_CG: {label} -- {len(atoms)} atoms, {len(ledger)} ledger entries, statuses: {statuses}')
        no_cg_in_ledger.append((label, f'NO_CG_LEDGER_({statuses})'))
    else:
        print(f'  OK: {label} -- {chain_grade_count} chain_grade ledger entries, {len(atoms)} atoms')

print('\n=== BACKUP CLOSED-negative capabilities vs atoms (need 2x-drill closure) ===')
for label, kws in backup_closed_neg:
    atoms = search(kws)
    ledger = search_ledger(kws)
    hf_count = sum(1 for _, st, _ in ledger if st in ('hard_fail', 'honest_negative', 'proven_bound'))
    print(f'  {label}: {len(atoms)} atoms, {len(ledger)} ledger, {hf_count} HF/HN/PB rulings')
    for aid_l, st, v in ledger[:6]:
        print(f'      [{st}] {aid_l[:90]} v={v[:30]}')

print('\n=== Suspect MISSING ledger - need attention ===')
for label, why in no_cg_in_ledger:
    print(f'  {label}: {why}')
