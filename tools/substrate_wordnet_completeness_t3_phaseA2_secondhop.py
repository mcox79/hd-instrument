"""T3 Phase A2: SECOND-HOP completion (the discriminating-contrast arm; Skunkworks 2026-06-18: MEASURED_MECHANISM).

Phase A (1-level) was FLAT (CERT HONEST_NEGATIVE): it added the new intermediates Y + their INCOMING edges (in5k->Y) but
0 OUTGOING (Y->z) -> dangling-upward -> 0 two-hop chains completed. Phase A2 completes the SECOND hop: materialize each
new-intermediate Y's direct-parent edge (Y->z) where z is ALREADY in-corpus -- i.e. extend the SAME gold-INDEPENDENT
"every synset has its WordNet-canonical direct parent" completeness rule to the new parents. NO new atoms (all targets
in-corpus); EDGES ONLY (~1110: 777 Y->in5k + 333 among-new).

Effect (measured by re-running BROAD after apply): the 2-hop chains x->Y->z now complete -> recall recovers (probe:
HYP-2 0.607->0.993, HYP-3 0.368->0.931). CERT-TIER (Skunkworks ruling): the recovery atom = MEASURED_MECHANISM
(verdict=ATTRIBUTION), NOT CERT -- gold-independent SELECTION (not fraud) BUT the intervention materializes the 2-level
hypernym CLOSURE = COEXTENSIVE with what 2-level QA traverses -> near-tautological (A1 parallel). The 1-level-FLAT vs
2-level-RECOVERS CONTRAST is what DISCRIMINATES coverage-vs-algorithmic -> depth-cliff = COVERAGE-limited, not algorithmic.

DEFAULT --dry-run (edge-budget + 0-phantom + 0-new-atoms + snapshot for the pre-ingest cert-gate). --apply: edges-only,
captured-pre + edge-READBACK gate + SERIAL flush-retry + gated. Gold-independent + deterministic (11th-rule). ASCII.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import RelationType

SRC_TAG = 'wordnet_completeness_t3_phaseA2_secondhop_2026_06_18'


def _persisted_hypernym_edges(ps):
    from backend.substrate_index.schema import Corpus
    cs = ps._store_for(Corpus.CONCEPT)
    return {(s[3:], t[3:]) for (s, rt, t) in cs._all_relations
            if rt == RelationType.HYPERNYM.value and s.startswith('WN_') and t.startswith('WN_')}


def compute_secondhop_edges(wn, in_store_names, new_targets, persisted):
    """Each new-intermediate Y -> its nltk direct hypernym z, where z is ALREADY in-corpus + edge not yet persisted.
    Gold-INDEPENDENT (iterates the new parents' own canonical direct-parent links; no gold look-ahead). Deterministic."""
    edges = set()
    for Y in sorted(new_targets):
        try:
            s = wn.synset(Y)
        except Exception:
            continue
        for h in s.hypernyms() + s.instance_hypernyms():
            if h.name() in in_store_names and (Y, h.name()) not in persisted:
                edges.add((Y, h.name()))
    return edges


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


def analyze():
    from backend.substrate_index.partition import PartitionedStore
    from nltk.corpus import wordnet as wn
    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    in_store_names = {a.id[3:] for a in atoms if str(a.id).startswith('WN_')}
    new_targets = {a.id[3:] for a in atoms if (a.metadata or {}).get('completeness_target')}
    persisted = _persisted_hypernym_edges(ps)
    edges = compute_secondhop_edges(wn, in_store_names, new_targets, persisted)
    to_in5k = sum(1 for (Y, z) in edges if z not in new_targets)
    among_new = sum(1 for (Y, z) in edges if z in new_targets)
    return dict(ps=ps, n_new_targets=len(new_targets), edges=edges, n_edges=len(edges),
                to_in5k=to_in5k, among_new=among_new)


def _flush_relations_with_retry(cstore, attempts=12):
    for attempt in range(attempts):
        try:
            cstore._flush_relations(); return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def dry_run() -> int:
    a = analyze(); ps = a['ps']
    print('=' * 74)
    print('T3 Phase A2 SECOND-HOP completion -- DRY-RUN (no mutation) for Skunkworks pre-ingest cert-gate')
    print('=' * 74)
    print(f"new-intermediate targets (Phase A added): {a['n_new_targets']}")
    print(f"SECOND-HOP edges (new-Y -> already-in-corpus direct-parent; gold-INDEPENDENT; NO new atoms): {a['n_edges']}")
    print(f"  Y->in5k: {a['to_in5k']} | among-new (Y->other-new-Y): {a['among_new']}")
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} | CERT={cert_count(ps)}")
    print('--- gates on --apply ---')
    print('  EDGES ONLY (0 new atoms; all endpoints already in-corpus -> 0-phantom). captured-pre + edge-READBACK.')
    print('  POST: axiom_term==206 + cap_pres + CERT unchanged + all intended edges read-back')
    print('=' * 74)
    print('DRY-RUN complete. Awaiting Skunkworks SCHEMA-VET before --apply. Then re-run BROAD -> atomize recovery as MEASURED_MECHANISM.')
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, Relation
    a = analyze(); ps = a['ps']
    intended = set(a['edges'])
    persisted_pre = _persisted_hypernym_edges(ps)
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | intended_edges={len(intended)}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    cstore = ps._store_for(Corpus.CONCEPT)
    edge_added = 0
    for (Y, z) in sorted(intended):
        triple = (f"WN_{Y}", RelationType.HYPERNYM.value, f"WN_{z}")
        if triple in cstore._all_relations:
            continue
        cstore._index_relation(Relation(src_id=f"WN_{Y}", tgt_id=f"WN_{z}", rel_type=RelationType.HYPERNYM))
        edge_added += 1
    if edge_added and not _flush_relations_with_retry(cstore):
        print('HARD_FAIL: os.replace race on relations flush.'); return 3
    print(f"  HYPERNYM second-hop edges added: {edge_added} (0 new atoms)")
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    persisted_now = _persisted_hypernym_edges(ps3)
    edges_present = intended.issubset(persisted_now)
    edge_count_ok = (edge_added == len(intended - persisted_pre))
    atoms_unchanged = (post_atoms == pre_atoms)   # EDGES ONLY -> 0 new atoms
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and atoms_unchanged
               and edges_present and edge_count_ok)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be 0) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged) | edges_present={edges_present} edge_added={edge_added} expected={len(intended-persisted_pre)}")
    if not gate_ok:
        print('HARD_FAIL: gate failed (0 new atoms + axiom 206 + cap_pres + CERT unchanged + all edges read-back).'); return 2
    print('=' * 74)
    print(f"T3 Phase A2 APPLY complete: +{edge_added} second-hop HYPERNYM edges (0 new atoms; all read-back) | axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged")
    print('  Now re-run BROAD -> recovery (coverage-lever) -> atomize MEASURED_MECHANISM (coextensive caveat).')
    print('=' * 74)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
