"""Skunkworks 2026-06-18 at-bandwidth substrate-build: 2 audit-lesson actions (A5-safe).
  (a) UPDATE the verify-the-referent PARENT (inst-80) -- add the A2-v6 top-gap MISATTRIBUTION
      witness (witnesses 11->12) + the new layer 'cert-VET result-narrative vs actual-data'.
      result-narrative NAMED wrong drivers (Tarjan/Hopcroft below floor); verify ACTUAL top items.
  (b) ADD the GPU-routed-!=-exercised AUDIT_LESSON (CANDIDATE w=1) backing the 7th checklist item.
META corpus, TIER_METHODOLOGY, algebra=None (process-knowledge -> NOT cert-counted -> CERT 571 unchanged).
A5-safe: snapshot CERT/axiom/cap_pres before -> update + add (single guarded invocation) -> verify + read-back.
Net atoms +1 (one update [count unchanged] + one add). ASCII.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

VTR_PARENT = 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'
GPU_ID = 'AUDIT_gpu_routed_not_gpu_exercised_full_run_0_util_cpu_default_device'

A2_MISATTR_WITNESS = (
    'A2 v6 cert-VET top-gap MISATTRIBUTION (2026-06-18): the refuse-gate cell verdict_msg NAMED '
    'Tarjan-SCC + Hopcroft-Karp (A2-GAP-000/002) as the high-confidence false-gap DRIVERS (the precision-limit '
    'examples), but those are conf 0.569/0.686 -- BOTH BELOW the in-cov floor 0.695 -> NOT the actual drivers. '
    'The ACTUAL top-ranked drivers are 7 DIFFERENT near-gaps (009/015/013/012/014/020/022 at conf 0.705-0.789). '
    'LESSON: when a result-narrative (verdict_msg / abstract / summary) NAMES specific examples as the drivers or '
    'top-items, VERIFY THE ACTUAL TOP-RANKED DATA-ITEMS -- do NOT trust the pre-named examples. Layer = '
    'result-narrative-vs-actual-data (distinct from the atom-field layers + the consumer-delivery layers); composes '
    'with actual-not-bar (read per-item data, not the headline). CAUGHT by Skunkworks actual-not-bar VET at the '
    'verdict-VET stage + corroborated INDEPENDENTLY by Exp-Dev per-gap inspection. Cert-grade-PRESERVING catch: the '
    '0.965 AUROC stayed CERT_CHAIN_GRADE; only the caveat-attribution was corrected (leakage ruled out -> real '
    'near-gap semantic proximity).'
)
A2_NEW_LAYER = ('cert-VET result-narrative-vs-actual-data (verdict_msg named wrong top-items; verify ACTUAL '
                'top-ranked data-items not the pre-named examples; A2 v6 misattribution; composes actual-not-bar)')
A2_SOURCE = 'skunkworks_A2v6_top_gap_misattribution_verify_actual_top_items_not_pre_named_examples_2026_06_18'

GPU_DESC = (
    "A FULL GPU-routed experiment can execute ENTIRELY ON CPU (0% GPU utilization) if the cell heavy compute "
    "silently defaults to device=cpu -- e.g. bge_encoder DEFAULT_DEVICE='cpu' made a GPU-routed pre-cache run on "
    "CPU. GPU-ROUTED (dispatched to a GPU queue) != GPU-EXERCISED (the GPU actually did the work). The result/atom "
    "is BYTE-EQUIVALENT (CPU and GPU produce the same embeddings) -> this is NOT a cert-correctness defect (per the "
    "engine/checklist-separation rule, device-exercise is a DISPATCH property, not an atom-truth property); it is a "
    "COST/THROUGHPUT defect (slow, wastes the allocated GPU, may smoke-default). TELL-TALE: a FULL GPU-routed run + "
    "0% nvidia-smi util + python absent from the compute-apps list + CPU-pace per-chunk (~87-220s/chunk vs GPU "
    "~5-15s). DISPOSITION: the 7th pre-dispatch BLOCKING checklist item (device-exercise) -- a GPU-queue cell must "
    "EXERCISE the GPU (device=cuda for the heavy compute) OR be declared + routed to cpu_queue. Enforced at "
    "SCHEMA-VET (verify the GPU-routed heavy-compute = device=cuda OR flag for cpu-route) + Orchestrator "
    "route-by-declared-device + empirical 0%-util backstop. CANDIDATE (w=1; the bge pre-cache cell); NOT load-bearing "
    "until 3 witnesses."
)
GPU_WITNESS = (
    "exp_prebuild_bge_index_cache_gpu_v1 pre-cache cell (2026-06-18): GPU-routed but ran 0% GPU util because "
    "bge_encoder DEFAULT_DEVICE='cpu' -> CPU-executed; byte-equivalent output (NOT a cert defect, verified) but slow "
    "+ wasted the allocated GPU; CAUGHT by Skunkworks (0%-util + CPU-pace observation) -> became the 7th checklist item."
)


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def update_parent_witness(ps, target):
    md = dict(target.metadata or {})
    ws = list(md.get('witnesses', []))
    ws.append(A2_MISATTR_WITNESS)
    md['witnesses'] = ws
    old = md.get('witnesses_count', 0)
    md['witnesses_count'] = old + 1
    layers = list(md.get('layers', []))
    if A2_NEW_LAYER not in layers:
        layers.append(A2_NEW_LAYER)
    md['layers'] = layers
    md.setdefault('witness_additions_log', []).append({
        'source': A2_SOURCE, 'witness_head': A2_MISATTR_WITNESS[:200],
        'old_count': old, 'new_count': old + 1, 'layer_added': A2_NEW_LAYER})
    md['A2v6_misattribution_witness_added_skunkworks_2026_06_18'] = True
    updated = Atom(
        id=target.id, name=target.name, description=target.description, kind=target.kind,
        tier=target.tier, corpus=target.corpus, algebra=target.algebra, metadata=md,
        aliases=target.aliases, concept_links=target.concept_links, complexity=target.complexity,
        current_best_solution=target.current_best_solution, equivalences=target.equivalences,
        serves_capability=target.serves_capability, signature=target.signature,
        solution_history=target.solution_history)
    ps.add_atom(updated, source=A2_SOURCE, note=f'A2v6 misattribution witness add {old}->{old+1} + result-narrative layer')
    return old, old + 1


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    # robust next instance_number among AUDIT_LESSON atoms (exclude the 238 outlier cross-ref scheme)
    al_inst = [a.metadata.get('instance_number') for a in ps.all_atoms()
               if (a.kind.value if hasattr(a.kind, 'value') else a.kind) == 'audit_lesson'
               and isinstance(a.metadata.get('instance_number'), int)]
    al_inst_sane = [n for n in al_inst if n < 200]
    next_inst = (max(al_inst_sane) + 1) if al_inst_sane else 1
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    print(f"  AUDIT_LESSON instance_numbers (sane<200): max={max(al_inst_sane) if al_inst_sane else None} -> next_inst={next_inst} | all_top={sorted(al_inst, reverse=True)[:8]}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL. HALT."); return 1

    # (a) update PARENT
    parent = ps.get_atom(VTR_PARENT) or next((a for a in ps.all_atoms() if a.id == VTR_PARENT), None)
    if parent is None:
        print("PARENT NOT FOUND. HALT."); return 2
    o, n = update_parent_witness(ps, parent)
    print(f"  (a) PARENT witness {o}->{n} + result-narrative layer")

    # (b) add GPU lesson
    gpu = Atom(
        id=GPU_ID,
        name=('Audit lesson (CANDIDATE; dispatch): a FULL GPU-routed run can execute on CPU (0% util) if compute '
              'defaults to device=cpu -- GPU-ROUTED != GPU-EXERCISED; the 7th pre-dispatch checklist item'),
        description=GPU_DESC,
        kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            'lesson_class': 'dispatch', 'confirmed_or_candidate': 'CANDIDATE', 'witnesses_count': 1,
            'witnesses': [GPU_WITNESS], 'NOT_load_bearing_until_3_witnesses': True,
            'instance_number': next_inst,
            'instance_number_provenance': ('Skunkworks 2026-06-18 bandwidth: GPU-routed-!=-exercised CANDIDATE '
                                           'backing the 7th pre-dispatch checklist item (device-exercise); promote on 3 witnesses'),
            'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
            'tell_tale': 'FULL GPU-routed run + 0% nvidia-smi util + python absent from compute-apps + CPU-pace per-chunk (~87-220s vs GPU ~5-15s)',
            'seventh_pre_dispatch_checklist_item': 'device-exercise (GPU-queue cell must exercise GPU OR route to cpu_queue)',
            'enforced_at': 'SCHEMA-VET (device=cuda heavy-compute OR flag cpu-route) + Orchestrator route-by-declared-device + empirical 0%-util backstop',
            'not_cert_correctness_defect': True,
            'composes_with': ['RULE_cert_architecture_engine_atomize_vs_checklist_dispatch_separation',
                              'reference_remote_dispatch_cell_readiness_checklist_2026-06-17'],
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': 'gpu_routed_not_exercised_bge_default_cpu_7th_checklist_item_skunkworks_2026_06_18',
        })
    if ps.get_atom(gpu.qualified_id) is not None:
        print(f"  (b) SKIP exists: {gpu.id}")
    else:
        ps.add_atom(gpu, source='skunkworks_bandwidth_gpu_lesson_2026_06_18', note='GPU-routed!=exercised CANDIDATE (7th checklist item)')
        print(f"  (b) GPU lesson ADDED inst={next_inst}")

    # POST gate + read-back
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    pcheck = ps2.get_atom(VTR_PARENT) or next((a for a in ps2.all_atoms() if a.id == VTR_PARENT), None)
    gcheck = ps2.get_atom(gpu.qualified_id) or next((a for a in ps2.all_atoms() if a.id == GPU_ID), None)
    p_wc = (pcheck.metadata or {}).get('witnesses_count') if pcheck else None
    g_alg = gcheck.algebra if gcheck else 'MISSING'
    g_layer_ok = A2_NEW_LAYER in ((pcheck.metadata or {}).get('layers', []) if pcheck else [])
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}; expect +1) CERT={post_cert} (expect {pre_cert}) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod}")
    print(f"  PARENT witnesses_count={p_wc} (expect 12) | new_layer_present={g_layer_ok}")
    print(f"  GPU atom present={gcheck is not None} algebra={g_alg} (expect None)")
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and post_atoms == pre_atoms + 1
            and p_wc == o + 1 and gcheck is not None and g_alg is None and g_layer_ok)
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 3


if __name__ == '__main__':
    raise SystemExit(main())
