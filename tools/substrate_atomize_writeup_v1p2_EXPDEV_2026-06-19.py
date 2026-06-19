"""Atomize WRITEUP v1.2 (Item-3; routed to Exp-Dev -- Director's atomize-script hit a silent add-fail edge-case).

Distinct filename from the Director-side script (preserved for their next-cycle debug). Reuses the PROVEN phase-portrait
META-atom pattern (worked this window): move top-level provenance_quality/relevance_tier/era INTO metadata (cap_map
precedent; from_dict does NOT lift them), from_dict -> Atom, add_atom, READ-BACK via all_atoms() scan (robust; avoids the
get_atom id-form sensitivity that likely caused the Director-side silent-fail). Skunkworks v1.1 framing-VET PASS; v1.2 adds
the M1 multi-relation-robust upgrade (cites BOTH heldout atoms).

Conditions (Skunkworks): kind=finding (existing AtomKind; no proliferation) + algebra=None + provenance_quality=RESEARCH_FINDING
in metadata + corpus=meta + tier=TIER_NA + top-level Atom fields + single add (N=1) + PRE/POST snapshot. CERT UNCHANGED
(RESEARCH_FINDING not cert-counted) + atoms +1 + axiom 206 + cap_pres 6/6. CITATION-RESOLVE GATE: all math:: cert-atom
citations must RESOLVE (pre-gate halts if any dangle) + persisted-atom citations resolve (landed-verify). ASCII. No LLM.
DEFAULT --dry-run ; --apply.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

DRAFT = Path('data/writeup_v1_substrate_as_reasoning_engine_DRAFT_pre_skunkworks_framing_VET.json')
ATOM_ID = 'WRITEUP_substrate_as_reasoning_engine_v1_2026-06-19'


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


def _all_ids(ps):
    ids = set()
    for a in ps.all_atoms():
        ids.add(a.id)
        try:
            ids.add(a.qualified_id)
        except Exception:
            pass
    return ids


def citations(d) -> list:
    return sorted(set(re.findall(r'math::[A-Za-z0-9_/\-]+', json.dumps(d))))


def build_atom():
    from backend.substrate_index.schema import Atom, AtomKind, Corpus
    d = json.loads(DRAFT.read_text(encoding='utf-8'))
    meta = dict(d.get('metadata') or {})
    for k in ('provenance_quality', 'relevance_tier', 'era'):
        if d.get(k) is not None and k not in meta:
            meta[k] = d[k]
    d['metadata'] = meta
    atom = Atom.from_dict(d)
    assert atom.id == ATOM_ID, f"id mismatch {atom.id}"
    assert atom.kind == AtomKind.FINDING, f"kind {atom.kind} (expected finding)"
    assert atom.corpus == Corpus.META, f"corpus {atom.corpus}"
    assert atom.algebra is None, "algebra MUST be None"
    assert (atom.metadata or {}).get('provenance_quality') == 'RESEARCH_FINDING', "provenance must be RESEARCH_FINDING"
    return atom, citations(d)


def dry_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    atom, cites = build_atom()
    ids = _all_ids(ps)
    unresolved = [c for c in cites if c not in ids]
    print('=' * 78)
    print('WRITEUP v1.2 ATOMIZE -- DRY-RUN (no mutation)')
    print('=' * 78)
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)}")
    print(f"  atom: id={atom.id} kind={atom.kind.name} corpus={atom.corpus.name} tier={atom.tier.name} algebra={atom.algebra} provenance={(atom.metadata or {}).get('provenance_quality')}")
    print(f"  citations ({len(cites)}): all-resolve={not unresolved}" + (f"  UNRESOLVED={unresolved}" if unresolved else ""))
    print('=' * 78)
    return 0 if not unresolved else 1


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import AtomKind, Corpus
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    atom, cites = build_atom()
    ids = _all_ids(ps)
    unresolved = [c for c in cites if c not in ids]
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | citations_unresolved={unresolved}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL.'); return 1
    if unresolved:
        print('HARD_FAIL: citation(s) do NOT resolve (value-RESOLVES gate). Halt.'); return 3
    cstore = ps._store_for(Corpus.META)
    for attempt in range(12):
        try:
            cstore.add_atom(atom, source='exp_dev_writeup_v1p2_atomize_2026-06-19', note='Item-3 WRITEUP v1.2; Director-routed; Skunkworks v1.1 PASS + M1 multi-relation upgrade')
            break
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    else:
        print('HARD_FAIL: META flush race.'); return 4
    ps3 = PartitionedStore(Path('data/substrate_index'))
    rb = next((x for x in ps3.all_atoms() if x.id == ATOM_ID), None)
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    ids3 = _all_ids(ps3)
    cites_resolve = all(c in ids3 for c in cites)
    rb_ok = (rb is not None and rb.kind == AtomKind.FINDING and rb.algebra is None
             and (rb.metadata or {}).get('provenance_quality') == 'RESEARCH_FINDING')
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert
               and post_atoms == pre_atoms + 1 and rb_ok and cites_resolve)
    print(f"READBACK: present={rb is not None} kind={rb.kind.name if rb else None} algebra={rb.algebra if rb else None} "
          f"provenance={(rb.metadata or {}).get('provenance_quality') if rb else None} citations_resolve={cites_resolve}")
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be +1) axiom_term={post_axiom} cap_pres={post_mod} CERT={post_cert} (unchanged from {pre_cert})")
    if not gate_ok:
        print('HARD_FAIL: post-gate failed. Reverting.')
        ps3.remove_atom(ATOM_ID, source='revert', note='gate fail'); return 2
    print('=' * 78)
    print(f"WRITEUP v1.2 ATOMIZED: {ATOM_ID} | kind=finding | algebra=None | RESEARCH_FINDING | META | atoms +1 | "
          f"CERT {post_cert} unchanged | axiom 206 | cap_pres 6/6 | {len(cites)} citations resolve. Route landed-verify to Skunkworks.")
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
