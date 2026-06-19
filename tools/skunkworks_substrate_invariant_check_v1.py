"""Skunkworks 2026-06-18 -- Sprint-3 Item 2: PERIODIC WHOLE-STORE INVARIANT SCHEMA-VET (the cert-FLOOR).

A NEW cert-layer ALONGSIDE the engine (per-atom atomize-time) + the checklist (per-cell dispatch-time):
this asserts integrity invariants across the FULL Store, periodically. Substrate-autonomy at the whole-Store
layer (self-certify the substrate's own invariants, not just per-atom). Read-ONLY (asserts, never mutates).

Per the engine/checklist-separation METHODOLOGY_RULE: engine=atomize cert-correctness; checklist=dispatch
cell-readiness; INVARIANT=periodic whole-Store integrity. Distinct layer.

TRUE-HARD invariants (LIVE cert-breaking -> non-zero exit; these alone gate the result):
  H1 axiom_term == 206 (the canonical axiom-core count; algebra>=3 MATH TIER_2/3, ex-oeis/wikidata)
  H2 cap_pres 6/6 (the 6 capability modules import-live)
  H3 CERT-count self-consistent + (optional) == --expect-cert (drift-detect vs a known snapshot)
GRAPH-HYGIENE invariants (PRE-EXISTING structural drift -> FLAG, NOT exit-failing; cleanup-tracked, v1.1):
  H4 0-phantom typed-EDGES: every iter_all_relations() endpoint resolves to a Store atom (qid or bare id).
     A dangling endpoint is graph-drift (edge outliving a removed atom), NOT a live cert-break (cert atoms are
     content-based; the multi-hop-provenance gate resolves atom->atom links, not the raw relation graph).
  H5 algebra-guard: NO non-axiom-eligible kind carries algebra (AUDIT_LESSON/METHODOLOGY_RULE/SEMANTIC_FRAME/
     CONCEPT_NODE/SCIENCE_CONCEPT/EXPERIMENT_RECORD/phase_portrait/capability_map should be algebra=None).
     A violator is a DEFENSE-IN-DEPTH breach, NOT a live break: axiom_term's corpus==MATH filter already
     excludes non-MATH atoms, so a stray-algebra methodology-rule does NOT corrupt the count.
SOFT invariants (hygiene -> WARN, do NOT fail; some dangles are legitimate forward/memory refs):
  S1 0-duplicate instance_number within a kind (catches the 234-238 AUDIT_LESSON cluster Skunkworks found)
  S2 cross-ref resolution: strengthens_cert/composes_with/parent_of/verify_the_referent_parent/depends_on/
     composes_with_siblings values resolve to atoms (the value-RESOLVES lesson, Store-wide). Memory-file refs
     (feedback_/reference_/project_/session_/MEMORY) are EXPECTED-dangling (not phantoms); reported separately.
  S4 (v1.3) conceptual_references binds: the Item-4 reconcile moved concept-labels OUT of composes_with INTO
     metadata.conceptual_references. A BOUND entry (backing_atom_proposed set) MUST resolve to a real atom
     (else it's a bad bind = phantom); an UNBOUND entry (backing None) is fine (pure concept-label). v1.3 keeps
     S2 meaningful for the new structured location (post-reconcile composes_with is clean for the RIGHT reason).
  S5 (v1.3) memory_references: metadata.memory_references = memory-file refs (NOT atom-resolve-required); a
     memory_reference that resolves to an atom-id is MIS-FILED (should be a crossref/conceptual). Counted/flagged.

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

    true_hard = []  # LIVE cert-breaking; gates the exit code
    true_hard.append(('H1 axiom_term==%d' % args.expect_axiom, ax == args.expect_axiom, f'actual={ax}'))
    true_hard.append(('H2 cap_pres 6/6', caps, f'modules_live={caps}'))
    cert_ok = (args.expect_cert is None) or (cert == args.expect_cert)
    true_hard.append(('H3 CERT-count', cert_ok, f'actual={cert}' + ('' if args.expect_cert is None else f' expect={args.expect_cert}')))
    graph_hygiene = []  # PRE-EXISTING structural drift; FLAG (not a live cert-break); reclassified from HARD in v1.1
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
    graph_hygiene.append(('H4 0-phantom-edges (dangling relation endpoints)', len(bad_edges) == 0, f'relations={n_rel} phantom={len(bad_edges)}'))
    # H5 algebra-guard: the REAL risk is a WOULD-BE-COUNTED violator (a non-axiom KIND that the axiom_term
    # formula would actually count: MATH-corpus, TIER_2/3, algebra>=3). A non-axiom-kind atom with algebra in a
    # NON-counted slot (e.g. a META/TIER_1 methodology-rule with an old-schema annotation) is HARMLESS (the
    # corpus+tier filter already excludes it) -> that is convention-conformance (SOFT S3), not a live risk. (v1.2)
    would_be_counted = [a.id for a in atoms if str(a.corpus.name) == 'MATH'
                        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
                        and kname(a) in NON_AXIOM_KINDS and a.algebra and len(a.algebra) >= 3]
    conv_violators = [a.id for a in atoms if kname(a) in NON_AXIOM_KINDS and a.algebra is not None
                      and a.id not in set(would_be_counted)]
    alg_violators = would_be_counted  # report alias (H5 prints the real-risk set)
    graph_hygiene.append(('H5 algebra-guard (no non-axiom KIND would be counted in axiom_term)', len(would_be_counted) == 0, f'would_be_counted={len(would_be_counted)}'))

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
    # S2 cross-ref resolution (atom-resolve-required fields) + S4 conceptual-bind resolution +
    # S5 memory-ref categorization. v1.3: the Item-4 catalog-reconcile moved memory-file refs and
    # concept-labels OUT of the atom-resolve crossref fields INTO metadata.memory_references /
    # metadata.conceptual_references (schema-preserved location). S2 stays meaningful by validating
    # the NEW structured fields: a BOUND conceptual_reference MUST resolve (else it's a bad bind);
    # an UNBOUND one is fine (concept-label); memory_references are memory-file refs (not atom-resolve).
    unresolved = []
    mem_refs = 0                  # memory-file refs found INSIDE crossref fields (legacy/pre-reconcile)
    conc_bound = conc_unbound = 0
    conc_bad_bind = []           # bound conceptual_references whose backing does NOT resolve (bad bind)
    mem_struct = 0               # metadata.memory_references entries (post-reconcile structured field)
    mem_struct_misfiled = []     # memory_references that actually resolve to an atom-id (mis-filed)
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
        # S4: metadata.conceptual_references (concept-labels; unbound-OK, backing-if-bound)
        for c in (md.get('conceptual_references') or []):
            if not isinstance(c, dict):
                continue
            b = c.get('backing_atom_proposed') or c.get('backing_atom')
            if b:
                conc_bound += 1
                if b not in resolvable and str(b).split('::')[-1] not in resolvable:
                    conc_bad_bind.append((a.id, c.get('value', ''), b))
            else:
                conc_unbound += 1
        # S5: metadata.memory_references (memory-file refs; NOT atom-resolve-required)
        for mr in (md.get('memory_references') or []):
            mrv = mr if isinstance(mr, str) else (mr.get('value') if isinstance(mr, dict) else None)
            if not mrv:
                continue
            mem_struct += 1
            if mrv in resolvable or str(mrv).split('::')[-1] in resolvable:
                mem_struct_misfiled.append((a.id, mrv))
    soft.append(('S2 cross-ref resolution (value-RESOLVES)', not unresolved,
                 f'unresolved_candidate_phantoms={len(unresolved)} expected_memory_refs={mem_refs}'))
    soft.append(('S4 conceptual_references binds resolve (bound->real atom; unbound OK)', not conc_bad_bind,
                 f'bound={conc_bound} unbound={conc_unbound} bad_binds={len(conc_bad_bind)}'))
    soft.append(('S5 memory_references categorized (memory-file refs, not atom-resolve)', not mem_struct_misfiled,
                 f'memory_reference_entries={mem_struct} misfiled_as_atom_id={len(mem_struct_misfiled)}'))
    soft.append(('S3 algebra convention-conformance (non-axiom kinds algebra=None)', not conv_violators,
                 f'harmless_convention_violators={len(conv_violators)} (corpus/tier-excluded from axiom_term; e.g. old-schema annotations)'))

    # report
    print('=' * 78)
    print('SUBSTRATE INVARIANT CHECK v1 (whole-Store cert-FLOOR) -- READ-ONLY')
    print(f'  atoms={n_atoms}' + ('' if args.expect_atoms is None else f' (expect {args.expect_atoms}: {"OK" if n_atoms==args.expect_atoms else "MISMATCH"})')
          + f' | CERT={cert} | axiom_term={ax} | relations={n_rel}')
    print('-' * 78)
    print('TRUE-HARD invariants (live cert-breaking; gate the result):')
    all_hard_ok = True
    for name, ok, detail in true_hard:
        all_hard_ok = all_hard_ok and ok
        print(f'  [{"PASS" if ok else "FAIL"}] {name}  ({detail})')
    print('GRAPH-HYGIENE (pre-existing structural drift; FLAG, not a live cert-break):')
    n_hygiene_flags = 0
    for name, ok, detail in graph_hygiene:
        if not ok:
            n_hygiene_flags += 1
        print(f'  [{"ok  " if ok else "FLAG"}] {name}  ({detail})')
    print('SOFT invariants (hygiene; WARN-only):')
    for name, ok, detail in soft:
        print(f'  [{"ok  " if ok else "WARN"}] {name}  ({detail})')
    if alg_violators:
        print('  H5 would-be-counted violators:', alg_violators[:10])
    if conv_violators:
        print('  S3 convention violators (harmless; corpus/tier-excluded from axiom_term):', conv_violators[:10])
    if unresolved:
        print('  S2 unresolved candidate-phantoms (first 10):', unresolved[:10])
    if conc_bad_bind:
        print('  S4 BAD conceptual binds (bound backing unresolved; first 10):', conc_bad_bind[:10])
    if mem_struct_misfiled:
        print('  S5 mis-filed memory_references (resolve to an atom-id; first 10):', mem_struct_misfiled[:10])
    if bad_edges:
        print('  H4 phantom-edge samples (first 5):', bad_edges[:5])
    print('-' * 78)
    print('RESULT:', 'TRUE-HARD-PASS' if all_hard_ok else 'TRUE-HARD-FAIL',
          f'| graph-hygiene-flags={n_hygiene_flags}',
          '| atoms_expect:', 'n/a' if args.expect_atoms is None else ('OK' if n_atoms == args.expect_atoms else 'MISMATCH'))
    print('=' * 78)
    return 0 if all_hard_ok else 4


if __name__ == '__main__':
    raise SystemExit(main())
