"""Atomize Phase-portrait v1 (Director Item 3; Skunkworks SCHEMA-VET PASS sub-counts-verified; routed to Exp-Dev).

Schema-add (PHASE_PORTRAIT AtomKind) is already applied in backend/substrate_index/schema.py. This cell:
  1. verify schema loads (AtomKind.PHASE_PORTRAIT) + pre-snapshot (axiom_term 206 + cap_pres 6/6 + CERT 570).
  2. load the Director atom-draft JSON; move top-level provenance_quality/relevance_tier/era INTO metadata (the
     cap_map precedent: provenance lives in metadata, NOT a top-level Atom field; from_dict does NOT lift them).
  3. from_dict -> Atom; assert kind=PHASE_PORTRAIT, corpus=META, algebra=None (structural guard).
  4. atomize (single add_atom -> single flush; N=1 well below batched-required threshold; 6th-checklist OK).
  5. read-back (fresh Store): qualified_id resolves + kind=phase_portrait + algebra=None +
     metadata.provenance_quality=INVENTORY_NON_CERT + the v1-honest-scope caveat present in description.
  6. invariants: axiom_term 206 + cap_pres 6/6 + CERT 570 unchanged (INVENTORY_NON_CERT does NOT count toward CERT).

DEFAULT --dry-run (snapshot + constructed-atom preview + gate-preview); --apply (atomize + post-gate + readback).
Top-level Atom fields not metadata for the dedicated fields (B1 value-RESOLVES lesson). 11th-rule deterministic. ASCII.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

DRAFT = Path('data/phase_portrait_v1_atom_DRAFT_pre_skunkworks_SCHEMA_VET.json')
ATOM_ID = 'PORTRAIT_v1_2026-06-18'
CAVEAT_SUBSTR = 'SPARSE-MEASURED INVENTORY'   # the v1-honest-scope caveat marker (read-back check)


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


def build_atom():
    from backend.substrate_index.schema import Atom, AtomKind, Corpus
    d = json.loads(DRAFT.read_text(encoding='utf-8'))
    meta = dict(d.get('metadata') or {})
    # cap_map precedent: provenance lives in metadata (from_dict does NOT lift these top-level keys)
    for k in ('provenance_quality', 'relevance_tier', 'era'):
        if d.get(k) is not None and k not in meta:
            meta[k] = d[k]
    d['metadata'] = meta
    atom = Atom.from_dict(d)
    assert atom.id == ATOM_ID, f"id mismatch {atom.id}"
    assert atom.kind == AtomKind.PHASE_PORTRAIT, f"kind {atom.kind}"
    assert atom.corpus == Corpus.META, f"corpus {atom.corpus}"
    assert atom.algebra is None, "algebra MUST be None (structural guard)"
    assert (atom.metadata or {}).get('provenance_quality') == 'INVENTORY_NON_CERT', "provenance_quality must be INVENTORY_NON_CERT"
    assert CAVEAT_SUBSTR in (atom.description or ''), "v1-honest-scope caveat missing from description"
    return atom


def dry_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import AtomKind
    ps = PartitionedStore(Path('data/substrate_index'))
    a = build_atom()
    print('=' * 78)
    print('PHASE-PORTRAIT v1 ATOMIZE -- DRY-RUN (no mutation)')
    print('=' * 78)
    print(f"AtomKind.PHASE_PORTRAIT loads: {AtomKind('phase_portrait').name}")
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)} (570)")
    already = ps.get(ATOM_ID) is not None if hasattr(ps, 'get') else any(x.id == ATOM_ID for x in ps.all_atoms())
    print(f"  atom {ATOM_ID} already in Store: {already}")
    print(f"  constructed: id={a.id} kind={a.kind.name} corpus={a.corpus.name} tier={a.tier.name} algebra={a.algebra}")
    print(f"  metadata.provenance_quality={(a.metadata or {}).get('provenance_quality')} | caveat-in-desc={CAVEAT_SUBSTR in (a.description or '')}")
    print('  POST-gate on --apply: axiom 206 + cap_pres 6/6 + CERT 570 unchanged + atom reads-back (kind/algebra/provenance/caveat).')
    print('=' * 78)
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import AtomKind, Corpus
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    atom = build_atom()
    cstore = ps._store_for(Corpus.META)
    # single atom -> add_atom (single flush) with PermissionError retry
    for attempt in range(12):
        try:
            cstore.add_atom(atom, source='exp_dev_phase_portrait_v1_atomize_2026-06-18', note='Director Item 3; Skunkworks SCHEMA-VET PASS')
            break
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    else:
        print('HARD_FAIL: os.replace race on META flush.'); return 3
    # read-back (fresh load)
    ps3 = PartitionedStore(Path('data/substrate_index'))
    rb = next((x for x in ps3.all_atoms() if x.id == ATOM_ID), None)
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    rb_ok = (rb is not None and rb.kind == AtomKind.PHASE_PORTRAIT and rb.algebra is None
             and (rb.metadata or {}).get('provenance_quality') == 'INVENTORY_NON_CERT'
             and CAVEAT_SUBSTR in (rb.description or ''))
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert
               and post_atoms == pre_atoms + 1 and rb_ok)
    print('-' * 78)
    print(f"READBACK: present={rb is not None} kind={rb.kind.name if rb else None} algebra={rb.algebra if rb else None} "
          f"provenance={(rb.metadata or {}).get('provenance_quality') if rb else None} caveat={CAVEAT_SUBSTR in (rb.description or '') if rb else None}")
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be +1) axiom_term={post_axiom} cap_pres={post_mod} CERT={post_cert} (unchanged from {pre_cert})")
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 2
    print('=' * 78)
    print(f"PHASE-PORTRAIT v1 ATOMIZED: {ATOM_ID} | kind=phase_portrait | algebra=None | INVENTORY_NON_CERT | "
          f"axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged | +1 atom. Route landed-verify to Skunkworks.")
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
