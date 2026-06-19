"""Phase-portrait v2 IN-PLACE patch (Director Item-6; landing-mode A; routed to Exp-Dev -- proven META-atom pattern).

In-place patch the existing PORTRAIT_v1_2026-06-18 atom (NOT a new atom; same id): bump schema_version v1->v2 + refresh the
content fields from data/phase_portrait_v2_inventory.json. A5-SAFE: content-refresh, NOT a pq/cert recompute; algebra=None +
tier=TIER_NA + provenance_quality=INVENTORY_NON_CERT all PRESERVED (not cert-counted -> CERT unchanged). atoms count UNCHANGED
(in-place update). Read-back via all_atoms() scan (the proven pattern; avoids the get_atom id-FORM silent-fail).

PERMISSIVE-SCOUR caveat preserved (domain-counts are first-pass scour-buckets, NOT cert-grade capability-counts; the cert-grade
refinement is the cap-int enumerator's honest-scoped-bound-per-row at USER launch). DEFAULT --dry-run ; --apply. ASCII.
"""
from __future__ import annotations
import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

ATOM_ID = 'PORTRAIT_v1_2026-06-18'   # the v1 atom (in-place patch; id unchanged per landing-mode A)
INV = Path('data/phase_portrait_v2_inventory.json')
PERMISSIVE_CAVEAT = ("Domain-counts are PERMISSIVE-SCOUR FIRST-PASS, not cert-grade capability-counts. The cert-grade "
                     "refinement is at the cap-int enumerator's honest-scoped-bound-per-row (at USER launch). E.g. the "
                     "reasoning_multihop bucket is a permissive scour-bucket, NOT that many cert-grade reasoning capabilities.")


def module_liveness_ok() -> bool:
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def axiom_term_count(ps) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def _v2_meta(old_meta: dict, inv: dict) -> dict:
    m = dict(old_meta or {})
    m['schema_version'] = 'v2'
    m['scoured_at_ts'] = inv.get('scoured_at_ts', '2026-06-19')
    m['total_cert_atoms'] = inv.get('total_cert_atoms')
    m['domain_counts'] = inv.get('domain_counts')
    m['unclassified_count'] = inv.get('unclassified_count')
    m['item_1_bound_class_counts'] = inv.get('item_1_bound_class_counts')
    m['metric_counts'] = inv.get('metric_counts')
    m['atoms_with_structured_metrics'] = inv.get('atoms_with_structured_metrics')
    m['atoms_with_scaling_hints'] = inv.get('atoms_with_scaling_hints')
    m['atoms_with_proven_bound_hints'] = inv.get('atoms_with_proven_bound_hints')
    m['cells_sample_v2'] = (inv.get('cells') or [])[:30]
    m['permissive_scour_caveat'] = PERMISSIVE_CAVEAT
    m['v2_patch_applied_by'] = 'exp_dev'
    m['v2_patch_note'] = 'in-place landing-mode A (schema_version v1->v2; content-refresh; A5-safe; INVENTORY_NON_CERT preserved)'
    return m


def build_patched(ps):
    from backend.substrate_index.schema import AtomKind
    atom = next((a for a in ps.all_atoms() if a.id == ATOM_ID), None)
    if atom is None:
        raise SystemExit(f"HALT: v1 atom {ATOM_ID} not found")
    if atom.kind != AtomKind.PHASE_PORTRAIT or atom.algebra is not None:
        raise SystemExit(f"HALT: unexpected v1 atom shape kind={atom.kind} algebra={atom.algebra}")
    if (atom.metadata or {}).get('provenance_quality') != 'INVENTORY_NON_CERT':
        raise SystemExit("HALT: v1 provenance not INVENTORY_NON_CERT")
    inv = json.loads(INV.read_text(encoding='utf-8'))
    new_meta = _v2_meta(atom.metadata, inv)
    return dataclasses.replace(atom, metadata=new_meta), inv


def dry_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    patched, inv = build_patched(ps)
    print('=' * 74)
    print('PHASE-PORTRAIT v2 IN-PLACE PATCH -- DRY-RUN (no mutation)')
    print('=' * 74)
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)}")
    print(f"  target atom: {ATOM_ID} (in-place; id/kind/corpus/tier/algebra/provenance UNCHANGED)")
    print(f"  schema_version: v1 -> {patched.metadata['schema_version']}")
    print(f"  total_cert_atoms={patched.metadata['total_cert_atoms']} | domains={len(patched.metadata['domain_counts'] or {})} | "
          f"unclassified={patched.metadata['unclassified_count']} | item_1_bound={patched.metadata['item_1_bound_class_counts']}")
    print(f"  structured_metrics={patched.metadata['atoms_with_structured_metrics']} scaling={patched.metadata['atoms_with_scaling_hints']} proven_bound={patched.metadata['atoms_with_proven_bound_hints']}")
    print("  POST-gate on --apply: atoms UNCHANGED (in-place) + CERT unchanged + axiom 206 + cap_pres 6/6 + schema_version==v2 reads-back + algebra=None + INVENTORY_NON_CERT.")
    print('=' * 74)
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import AtomKind, Corpus
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    patched, inv = build_patched(ps)
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL.'); return 1
    cstore = ps._store_for(Corpus.META)
    for attempt in range(12):
        try:
            cstore.add_atom(patched, source='exp_dev_phase_portrait_v2_patch_2026-06-19', note='in-place v1->v2 schema_version + content-refresh (A5-safe)')
            break
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    else:
        print('HARD_FAIL: META flush race.'); return 4
    ps3 = PartitionedStore(Path('data/substrate_index'))
    rb = next((x for x in ps3.all_atoms() if x.id == ATOM_ID), None)
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    rb_ok = (rb is not None and rb.kind == AtomKind.PHASE_PORTRAIT and rb.algebra is None
             and (rb.metadata or {}).get('provenance_quality') == 'INVENTORY_NON_CERT'
             and (rb.metadata or {}).get('schema_version') == 'v2'
             and (rb.metadata or {}).get('total_cert_atoms') == inv.get('total_cert_atoms'))
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and post_atoms == pre_atoms and rb_ok)
    print(f"READBACK: present={rb is not None} schema_version={(rb.metadata or {}).get('schema_version') if rb else None} "
          f"total_cert_atoms={(rb.metadata or {}).get('total_cert_atoms') if rb else None} algebra={rb.algebra if rb else None} provenance={(rb.metadata or {}).get('provenance_quality') if rb else None}")
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be 0 in-place) axiom_term={post_axiom} cap_pres={post_mod} CERT={post_cert} (unchanged from {pre_cert})")
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 2
    print('=' * 74)
    print(f"PHASE-PORTRAIT v2 PATCHED in-place: {ATOM_ID} schema_version v1->v2 | atoms UNCHANGED | CERT {post_cert} unchanged | "
          f"axiom 206 | cap_pres 6/6 | INVENTORY_NON_CERT + algebra=None preserved. Route landed-verify to Skunkworks.")
    print('=' * 74)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
