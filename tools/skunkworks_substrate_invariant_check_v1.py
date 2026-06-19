"""Skunkworks 2026-06-18 -- Sprint-3 Item 2: PERIODIC WHOLE-STORE INVARIANT SCHEMA-VET (the cert-FLOOR).

A NEW cert-layer ALONGSIDE the engine (per-atom atomize-time) + the checklist (per-cell dispatch-time):
this asserts integrity invariants across the FULL Store, periodically. Substrate-autonomy at the whole-Store
layer (self-certify the substrate's own invariants, not just per-atom). Read-ONLY (asserts, never mutates).

Per the engine/checklist-separation METHODOLOGY_RULE: engine=atomize cert-correctness; checklist=dispatch
cell-readiness; INVARIANT=periodic whole-Store integrity. Distinct layer.

HARD invariants (cert-breaking -> non-zero exit):
  H1 axiom_term == 206 (the canonical axiom-core count; algebra>=3 MATH TIER_2/3, ex-oeis/wikidata)
  H2 cap_pres 6/6 (the 6 capability modules import-live)
  H3 CERT-count self-consistent + (optional) == --expect-cert (drift-detect vs a known snapshot)
  H4 0-phantom typed-EDGES: every iter_all_relations() endpoint resolves to a Store atom (qid or bare id)
  H5 algebra-guard: NO non-axiom-eligible kind carries algebra (AUDIT_LESSON/METHODOLOGY_RULE/SEMANTIC_FRAME/
     CONCEPT_NODE/SCIENCE_CONCEPT/EXPERIMENT_RECORD/phase_portrait/capability_map must be algebra=None)
SOFT invariants (hygiene -> WARN, do NOT fail; some dangles are legitimate forward/memory refs):
  S1 0-duplicate instance_number within a kind (catches the 234-238 AUDIT_LESSON cluster Skunkworks found)
  S2 cross-ref resolution: strengthens_cert/composes_with/parent_of/verify_the_referent_parent/depends_on/
     composes_with_siblings values resolve to atoms (the value-RESOLVES lesson, Store-wide). Memory-file refs
     (feedback_/reference_/project_/session_/MEMORY) are EXPECTED-dangling (not phantoms); reported separately.

Usage: python tools/skunkworks_substrate_invariant_check_v1.py [--expect-cert N --expect-atoms N --expect-axiom N]
  (the --expect-* asserts are for the push-fix pre/post landed-verify; omit for a standing report.)
Read-only; prints a report; exit 0 iff all HARD pass. ASCII.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

NON_AXIOM_KINDS = {'audit_lesson', 'methodology_rule', 'semantic_frame', 'concept_node',
                   'science_concept', 'experiment_record', 'phase_portrait', 'capability_map',
                   'proof_record', 'lexicon'}
MEMORY_REF_PREFIXES = ('feedback_', 'reference_', 'project_', 'session_', 'MEMORY', 'milestone_')
CROSSREF_FIELDS = ('strengthens_cert', 'strengthens', 'composes_with', 'composes_with_siblings',
                   'parent_of', 'verify_the_referent_parent', 'depends_on')


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def axiom_term(atoms):
    return sum(1 for a in atoms
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cap_pres():
    import importlib
    try:
        return all(hasattr(importlib.import_module(m), s) for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ])
    except Exception:
        return False


def endpoints(rel):
    """Robustly extract (src, tgt) from a relation (tuple or object)."""
    if isinstance(rel, (tuple, list)):
        if len(rel) == 3:
            return rel[0], rel[2]
        if len(rel) == 2:
            return rel[0], rel[1]
    for s, t in (('source', 'target'), ('src', 'tgt'), ('source_id', 'target_id'), ('src_id', 'tgt_id')):
        if hasattr(rel, s) and hasattr(rel, t):
            return getattr(rel, s), getattr(rel, t)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--expect-cert', type=int, default=None)
    ap.add_argument('--expect-atoms', type=int, default=None)
    ap.add_argument('--expect-axiom', type=int, default=206)
    args = ap.parse_args()

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    qids = set(ps.all_qualified_ids())
    bare = {a.id for a in atoms}
    resolvable = qids | bare

    n_atoms = len(atoms)
    cert = sum(1 for a in atoms if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    ax = axiom_term(atoms)
    caps = cap_pres()

    hard = []  # (name, ok, detail)
    # H1 axiom
    hard.append(('H1 axiom_term==%d' % args.expect_axiom, ax == args.expect_axiom, f'actual={ax}'))
    # H2 cap_pres
    hard.append(('H2 cap_pres 6/6', caps, f'modules_live={caps}'))
    # H3 CERT
    cert_ok = (args.expect_cert is None) or (cert == args.expect_cert)
    hard.append(('H3 CERT-count', cert_ok, f'actual={cert}' + ('' if args.expect_cert is None else f' expect={args.expect_cert}')))
    # H4 phantom edges
    n_rel = 0
    bad_edges = []
    try:
        for rel in ps.iter_all_relations():
            n_rel += 1
            s, t = endpoints(rel)
            for ep in (s, t):
                if ep is not None and ep not in resolvable:
                    # try corpus-stripped / both forms
                    ep2 = str(ep).split('::')[-1]
                    if ep not in resolvable and ep2 not in resolvable:
                        bad_edges.append((s, t, ep))
                        break
    except Exception as e:
        bad_edges.append(('ITER_ERROR', str(e), ''))
    hard.append(('H4 0-phantom-edges', len(bad_edges) == 0, f'relations={n_rel} phantom={len(bad_edges)}'))
    # H5 algebra-guard
    alg_violators = [a.id for a in atoms if kname(a) in NON_AXIOM_KINDS and a.algebra is not None]
    hard.append(('H5 algebra-guard (non-axiom kinds algebra=None)', len(alg_violators) == 0, f'violators={len(alg_violators)}'))

    soft = []
    # S1 duplicate instance_number within kind
    from collections import defaultdict, Counter
    by_kind_inst = defaultdict(list)
    for a in atoms:
        n = (a.metadata or {}).get('instance_number')
        if isinstance(n, int):
            by_kind_inst[kname(a)].append(n)
    dups = {}
    for k, lst in by_kind_inst.items():
        c = Counter(lst)
        d = {n: cnt for n, cnt in c.items() if cnt > 1}
        if d:
            dups[k] = d
    soft.append(('S1 0-duplicate instance_number/kind', not dups, f'dup_kinds={list(dups.keys())} detail={dups}'))
    # S2 cross-ref resolution
    unresolved = []
    mem_refs = 0
    for a in atoms:
        md = a.metadata or {}
        for f in CROSSREF_FIELDS:
            v = md.get(f)
            if not v:
                continue
            vals = v if isinstance(v, list) else [v]
            for ref in vals:
                if not isinstance(ref, str):
                    continue
                r2 = ref.split('::')[-1]
                if ref in resolvable or r2 in resolvable:
                    continue
                if ref.startswith(MEMORY_REF_PREFIXES):
                    mem_refs += 1
                else:
                    unresolved.append((a.id, f, ref))
    soft.append(('S2 cross-ref resolution (value-RESOLVES)', not unresolved,
                 f'unresolved_candidate_phantoms={len(unresolved)} expected_memory_refs={mem_refs}'))

    # report
    print('=' * 78)
    print('SUBSTRATE INVARIANT CHECK v1 (whole-Store cert-FLOOR) -- READ-ONLY')
    print(f'  atoms={n_atoms}' + ('' if args.expect_atoms is None else f' (expect {args.expect_atoms}: {"OK" if n_atoms==args.expect_atoms else "MISMATCH"})')
          + f' | CERT={cert} | axiom_term={ax} | relations={n_rel}')
    print('-' * 78)
    print('HARD invariants (cert-breaking):')
    all_hard_ok = True
    for name, ok, detail in hard:
        all_hard_ok = all_hard_ok and ok
        print(f'  [{"PASS" if ok else "FAIL"}] {name}  ({detail})')
    print('SOFT invariants (hygiene; WARN-only):')
    for name, ok, detail in soft:
        print(f'  [{"ok  " if ok else "WARN"}] {name}  ({detail})')
    if alg_violators:
        print('  H5 violators:', alg_violators[:10])
    if unresolved:
        print('  S2 unresolved candidate-phantoms (first 10):', unresolved[:10])
    if bad_edges:
        print('  H4 phantom-edge samples (first 5):', bad_edges[:5])
    print('-' * 78)
    print('RESULT:', 'HARD-PASS' if all_hard_ok else 'HARD-FAIL', '| atoms_expect:',
          'n/a' if args.expect_atoms is None else ('OK' if n_atoms == args.expect_atoms else 'MISMATCH'))
    print('=' * 78)
    return 0 if all_hard_ok else 4


if __name__ == '__main__':
    raise SystemExit(main())
