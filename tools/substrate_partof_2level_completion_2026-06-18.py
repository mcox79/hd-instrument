"""PART_OF 2-level completion -- the discriminating-contrast arm for the depth-cliff verdict (Item 1, 20h sprint).

The depth-cliff verdict (CERT) established HYPERNYM is COVERAGE-limited (the 1-level-FLAT vs 2-level-RECOVERS contrast:
HYP-2 0.607->0.993 after the second-hop completion), and PART_OF was depth-ROBUST at baseline (PART_OF_2hop 0.627,
3hop 0.500; "separate axis, not densified"). The OPEN question: is PART_OF's relative depth-robustness because the
PART_OF subgraph was already 2-level coverage-COMPLETE (-> a completeness ARTIFACT, the SAME coverage story explains
BOTH), or is it an ALGORITHMIC property (-> a new cause)? This cell DISCRIMINATES by applying the SAME completeness
intervention to PART_OF that recovered HYPERNYM, then re-running BROAD.

THE COMPLETION (gold-INDEPENDENT, mirrors the hypernym second-hop completeness rule): the original PART_OF ingest was
MERONYM-based (for each in-corpus whole, add its in-corpus parts: part PART_OF whole, from metadata.meronyms). This cell
extends the canonical-direct-link completeness rule from the HOLONYM direction: for each in-corpus synset X, materialize
X's direct in-corpus HOLONYM edges (X PART_OF Z, Z in {part/member/substance}_holonyms(X), Z in-corpus) not yet persisted.
Gold-INDEPENDENT (iterates each synset's OWN canonical holonyms; NO gold look-ahead; all 3 holonym types = the SAME
relation the BROAD PART_OF gold uses). EDGES ONLY (both endpoints already in-corpus -> 0 new atoms -> 0-phantom).

The COMPLETION-EDGE COUNT is itself the first discriminator:
  ~0 edges to add  -> PART_OF was ALREADY 2-level complete (meronym ingest already symmetric) -> robustness is a
                      completeness ARTIFACT before BROAD even re-runs.
  many edges to add -> there was a coverage gap; the BROAD delta (re-run after apply) tells whether it MATTERS.

Verdict tier-by-outcome (Skunkworks pre-stated; decided AFTER re-running BROAD post-apply):
  PART_OF recall barely-moves -> cert-grade DISCRIMINATING NULL (completeness-artifact CONFIRMED; coverage explains BOTH
                                 the HYPERNYM cliff and the PART_OF robustness -- one mechanism).
  PART_OF recall JUMPS         -> MEASURED_MECHANISM ATTRIBUTION (PART_OF was coverage-limited too; the completion is the
                                 lever) + a new-cause-to-investigate (why baseline looked robust despite the gap).

DEFAULT --dry-run (completion-edge count + 0-new-atoms + 0-phantom + snapshot for the pre-dispatch cert-gate). --apply:
edges-only, intended captured PRE-ingest (the T3 re-analyze flip-bug lesson applied forward), edge-READBACK gate,
SERIAL flush-retry, post-gate (axiom_term 206 + cap_pres 6/6 + CERT unchanged + 0 new atoms). Needs nltk (run locally,
CPU). The BROAD cell does NOT need nltk (frozen gold). Deterministic (11th-rule). ASCII.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import RelationType

SRC_TAG = 'partof_2level_completion_2026_06_18'
HOLONYM_BASELINE = {'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500}   # from the BROAD CERT envelope (pre-completion)


def _persisted_partof_edges(ps):
    from backend.substrate_index.schema import Corpus
    cs = ps._store_for(Corpus.CONCEPT)
    return {(s[3:], t[3:]) for (s, rt, t) in cs._all_relations
            if rt == RelationType.PART_OF.value and s.startswith('WN_') and t.startswith('WN_')}


def compute_completion_edges(wn, in_store_names, persisted):
    """Each in-corpus synset X -> its nltk direct HOLONYM Z (part/member/substance), where Z is ALREADY in-corpus + edge
    not yet persisted. Direction (X PART_OF Z) = part->whole, matching the original ingest + the BROAD walker adjacency.
    Gold-INDEPENDENT (iterates each synset's own canonical holonyms; no gold look-ahead). Deterministic (sorted)."""
    edges = set()
    for X in sorted(in_store_names):
        try:
            s = wn.synset(X)
        except Exception:
            continue
        for Z in s.part_holonyms() + s.member_holonyms() + s.substance_holonyms():
            zn = Z.name()
            if zn in in_store_names and zn != X and (X, zn) not in persisted:
                edges.add((X, zn))
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
    persisted = _persisted_partof_edges(ps)
    edges = compute_completion_edges(wn, in_store_names, persisted)
    return dict(ps=ps, n_in_store=len(in_store_names), n_persisted=len(persisted), edges=edges, n_edges=len(edges))


def _flush_relations_with_retry(cstore, attempts=12):
    for attempt in range(attempts):
        try:
            cstore._flush_relations(); return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def dry_run() -> int:
    a = analyze(); ps = a['ps']
    print('=' * 78)
    print('PART_OF 2-LEVEL completion -- DRY-RUN (no mutation) for Skunkworks pre-dispatch SCHEMA-VET')
    print('=' * 78)
    print(f"in-corpus WN_ synsets: {a['n_in_store']} | persisted PART_OF edges (baseline): {a['n_persisted']}")
    print(f"COMPLETION edges (in-corpus X -> in-corpus HOLONYM Z; gold-INDEPENDENT; NO new atoms): {a['n_edges']}")
    if a['n_persisted']:
        print(f"  completion vs baseline ratio: +{100.0*a['n_edges']/a['n_persisted']:.1f}% over the {a['n_persisted']} persisted PART_OF edges")
    print(f"  FIRST discriminator: {'~0 completion edges -> PART_OF already 2-level complete (artifact-leaning)' if a['n_edges'] < 20 else 'substantial coverage gap -> BROAD delta will decide'}")
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)}")
    print(f"BROAD baseline to beat (pre-completion): PART_OF_2hop={HOLONYM_BASELINE['PART_OF_2hop']} PART_OF_3hop={HOLONYM_BASELINE['PART_OF_3hop']}")
    print('--- gates on --apply ---')
    print('  EDGES ONLY (0 new atoms; all endpoints already in-corpus -> 0-phantom). intended captured-PRE + edge-READBACK.')
    print('  POST: axiom_term==206 + cap_pres 6/6 + CERT unchanged + all intended edges read-back + 0 new atoms')
    print('=' * 78)
    print('DRY-RUN complete. Awaiting Skunkworks SCHEMA-VET before --apply. Then re-run BROAD -> recall delta -> verdict tier-by-outcome.')
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, Relation
    a = analyze(); ps = a['ps']
    intended = set(a['edges'])                     # captured PRE-ingest (no re-analyze flip)
    persisted_pre = _persisted_partof_edges(ps)
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | intended_edges={len(intended)}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    cstore = ps._store_for(Corpus.CONCEPT)
    edge_added = 0
    for (X, Z) in sorted(intended):
        triple = (f"WN_{X}", RelationType.PART_OF.value, f"WN_{Z}")
        if triple in cstore._all_relations:
            continue
        cstore._index_relation(Relation(src_id=f"WN_{X}", tgt_id=f"WN_{Z}", rel_type=RelationType.PART_OF))
        edge_added += 1
    if edge_added and not _flush_relations_with_retry(cstore):
        print('HARD_FAIL: os.replace race on relations flush.'); return 3
    print(f"  PART_OF completion edges added: {edge_added} (0 new atoms)")
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    persisted_now = _persisted_partof_edges(ps3)
    edges_present = intended.issubset(persisted_now)
    edge_count_ok = (edge_added == len(intended - persisted_pre))
    atoms_unchanged = (post_atoms == pre_atoms)
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and atoms_unchanged
               and edges_present and edge_count_ok)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be 0) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged) | edges_present={edges_present} edge_added={edge_added} expected={len(intended-persisted_pre)}")
    if not gate_ok:
        print('HARD_FAIL: gate failed (0 new atoms + axiom 206 + cap_pres + CERT unchanged + all edges read-back).'); return 2
    print('=' * 78)
    print(f"PART_OF 2-LEVEL APPLY complete: +{edge_added} PART_OF completion edges (0 new atoms; all read-back) | axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged")
    print('  Now re-run BROAD (exp_substrate_b_alpha_broad_envelope_cpu_v1.py --full) -> compare PART_OF_2hop/3hop vs '
          f"baseline {HOLONYM_BASELINE} -> verdict tier-by-outcome (barely-moves=discriminating-null / jumps=MEASURED_MECHANISM).")
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
