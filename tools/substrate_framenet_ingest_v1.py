"""FrameNet ARC-3 ingest v1 (Item 2; USER-GO 2026-06-18; Skunkworks discretion + refinements).

Orthogonal-breadth ingest: 1,221 FrameNet frames -> SEMANTIC_FRAME atoms + the frame-to-frame relations -> first-class
FRAME_* typed edges (metadata-drop lesson honored). v1 SCOPE (per scaffold + Skunkworks): frames + frame-to-frame edges
+ LU lemmas as METADATA. DEFER to v2: FRAME_ELEMENT atoms + LU-as-atoms/LU-edges (the "13,572 LU edges" need LU atoms,
not in v1's AtomKind plan -> carried as frame metadata, materializable later like B1's hypernyms->HYPERNYM edges).

Probe findings (this build): 1,221 frames; 13,572 LUs (metadata); 2,070 UNIQUE frame-to-frame relations across 10 nltk
relation types (scaffold listed 8; nltk ALSO has ReFraming_Mapping + Metaphor -> mapped all 10 as first-class rel_types).
Edge direction: sub -> super (child/specific -> parent/base; e.g. Inheritance Abandonment -> Intentionally_affect).

Atoms: id=FN_<framename>, corpus=CONCEPT, tier=TIER_NA, algebra=None (structural guard -> excluded from axiom_term),
provenance_quality=RESEARCH_FINDING (T2 non-load-bearing until cert-promoted). 0-ID-collision (FN_ namespace).

DEFAULT --dry-run (counts + edge-budget + 0-ID-collision + axiom/cap_pres SNAPSHOT for the pre-ingest cert-gate).
--apply SERIAL + gated + non-retroactive. Laptop CPU, no bge. ASCII-only. 11th-rule (lexical DB, no LLM).
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

SRC_TAG = 'framenet_v17_arc3_ingest_v1_2026_06_18'
LU_CAP = 60   # bound metadata size (most frames < 60 LUs; a few have more)

# nltk FrameNet relation-type name -> first-class rel_type (all 10)
REL_MAP = {
    'Inheritance': RelationType.FRAME_INHERITS,
    'Using': RelationType.FRAME_USES,
    'Subframe': RelationType.FRAME_SUBFRAME,
    'Perspective_on': RelationType.FRAME_PERSPECTIVE_ON,
    'Precedes': RelationType.FRAME_PRECEDES,
    'Inchoative_of': RelationType.FRAME_INCHOATIVE_OF,
    'Causative_of': RelationType.FRAME_CAUSATIVE_OF,
    'See_also': RelationType.FRAME_SEE_ALSO,
    'ReFraming_Mapping': RelationType.FRAME_REFRAMING_MAPPING,
    'Metaphor': RelationType.FRAME_METAPHOR,
}


def _fid(name: str) -> str:
    return f"FN_{name}"


def build_atom(fr) -> Atom:
    lus = sorted(fr.lexUnit.keys())
    metadata = {
        'framenet_version': '1.7', 'frame_id': fr.ID, 'frame_name': fr.name,
        'n_lexunits': len(lus),
        'lexunits': lus[:LU_CAP],                # LU lemmas as METADATA (v2: materialize as LU atoms/edges)
        'lexunits_capped': len(lus) > LU_CAP,
        'provenance_quality': 'RESEARCH_FINDING',  # T2 non-load-bearing until cert-promoted (research-can-be-wrong)
        'confidence_tier': 'T2_LEXICAL_RESOURCE',
        'frame_edge_direction': 'nltk sub->super (specific/child -> base/parent); rel_type carries the semantics '
                                '(hierarchical: Inherits/Uses/Subframe/Perspective_on; non-hierarchical: Precedes/Causative/'
                                'Inchoative/See_also/Metaphor/ReFraming -- direction is nltk convention, not a true hierarchy)',
        'source': SRC_TAG,
    }
    return Atom(id=_fid(fr.name), name=fr.name, description=(fr.definition or '')[:500],
                kind=AtomKind.SEMANTIC_FRAME, tier=Tier.TIER_NA, corpus=Corpus.CONCEPT, algebra=None, metadata=metadata)


def compute_edges(fn, frame_names):
    """Unique frame-to-frame typed edges: (sub_name, rel_type, super_name), both endpoints in frame_names. sub->super."""
    edges = set()
    unmapped = set()
    for fr in fn.frames():
        for rel in fr.frameRelations:
            t = rel.type.name
            sub, sup = rel.subFrameName, rel.superFrameName
            if not sub or not sup or sub not in frame_names or sup not in frame_names:
                continue
            rt = REL_MAP.get(t)
            if rt is None:
                unmapped.add(t); continue
            edges.add((sub, rt.value, sup))      # sub -> super (child/specific -> parent/base)
    return edges, unmapped


def module_liveness_ok() -> bool:
    import importlib
    return all(hasattr(importlib.import_module(m), sym) for m, sym in [
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
    from nltk.corpus import framenet as fn
    ps = PartitionedStore(Path('data/substrate_index'))
    kind_by_id = {a.id: a.kind for a in ps.all_atoms()}
    frames = list(fn.frames())
    frame_names = {fr.name for fr in frames}
    # collision = FN_<frame> held by a NON-SEMANTIC_FRAME atom (genuine foreign id-collision). An existing
    # SEMANTIC_FRAME at that id is OUR OWN (partial/prior) ingest -> idempotent-skip, NOT a collision.
    collisions = [fr.name for fr in frames
                  if _fid(fr.name) in kind_by_id and kind_by_id[_fid(fr.name)] != AtomKind.SEMANTIC_FRAME]
    edges, unmapped = compute_edges(fn, frame_names)
    from collections import Counter
    by_rel = Counter(rt for (_, rt, _) in edges)
    return dict(ps=ps, fn=fn, frames=frames, n_frames=len(frames), collisions=collisions,
                edges=edges, n_edges=len(edges), by_rel=dict(by_rel), unmapped=unmapped,
                n_lus=sum(len(fr.lexUnit) for fr in frames))


def _flush_relations_with_retry(cstore, attempts=12):
    for attempt in range(attempts):
        try:
            cstore._flush_relations(); return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def _save_atoms_with_retry(atoms_list, path, attempts=12):
    """SINGLE batched atom-flush with os.replace-race retry (B1 pattern; avoids the O(n^2) per-atom add_atom flush)."""
    from backend.substrate_index.schema import save_atoms
    for attempt in range(attempts):
        try:
            save_atoms(atoms_list, path); return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def dry_run() -> int:
    a = analyze()
    ps = a['ps']
    print('=' * 74)
    print('FrameNet ARC-3 ingest v1 -- DRY-RUN (no mutation) for Skunkworks pre-ingest cert-gate')
    print('=' * 74)
    print(f"frames -> SEMANTIC_FRAME atoms: {a['n_frames']}")
    print(f"LUs (carried as METADATA; LU-atoms/edges DEFERRED to v2): {a['n_lus']}")
    print(f"cross-corpus ID-COLLISIONS (FN_<frame> already an atom id): {len(a['collisions'])} (MUST be 0)")
    print(f"frame-to-frame typed edges (unique; sub->super; 0-phantom both-endpoints-frames): {a['n_edges']}")
    print(f"  by rel_type: {a['by_rel']}")
    print(f"  unmapped relation types (MUST be empty -- all 10 mapped): {sorted(a['unmapped'])}")
    print(f"SNAPSHOT before: axiom_term={axiom_term_count(ps)} (MUST stay 206) | cap_pres={module_liveness_ok()} | CERT={cert_count(ps)} (RESEARCH_FINDING != cert -> unchanged)")
    print('--- gates on --apply ---')
    print('  PRE: axiom_term==206 + cap_pres 6/6 + 0 ID-collisions (HALT else)')
    print('  ingest: SERIAL batched SEMANTIC_FRAME atom-add (CONCEPT/TIER_NA/algebra=None/pq=RESEARCH_FINDING)')
    print('  edge-mat: FRAME_* typed edges (0-phantom; both endpoints frame atoms post-ingest)')
    print('  POST: axiom_term==206 + cap_pres 6/6 + CERT unchanged + read-back')
    print('=' * 74)
    return 0 if (not a['collisions'] and not a['unmapped']) else 1


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, Relation
    a = analyze()
    if a['collisions'] or a['unmapped']:
        print(f"HALT: collisions={len(a['collisions'])} unmapped={sorted(a['unmapped'])}"); return 1
    ps = a['ps']
    # capture intended edge triples PRE-ingest (a['edges'] is corpus-state-independent, but capture-and-readback
    # makes declared==actual hold for EDGES too -- mirrors the T3 hardening; catches a partial-flush regression).
    intended_triples = {(_fid(sub), rt, _fid(sup)) for (sub, rt, sup) in a['edges']}
    cs_pre = ps._store_for(Corpus.CONCEPT)
    persisted_pre = {t for t in cs_pre._all_relations if t in intended_triples}
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | intended_edges={len(intended_triples)}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    # BATCHED atom-add (B1 pattern: _index_atom in-memory + SINGLE save_atoms; avoids O(n^2) per-atom add_atom flush
    # that timeout-killed the first apply at 576/1221). Idempotent: skip ids already in cstore._by_id.
    cstore = cs_pre   # the already-loaded CONCEPT sub-store
    added = 0
    for fr in a['frames']:
        atom = build_atom(fr)
        if atom.id in cstore._by_id:
            continue
        cstore._index_atom(atom)
        added += 1
    if added and not _save_atoms_with_retry(list(cstore._by_id.values()), cstore.atoms_path):
        print('HARD_FAIL: os.replace race on atom flush.'); return 3
    print(f"  atoms added (batched single-flush): {added}")
    # edges on the SAME cstore (atoms now persisted + in _by_id -> 0-phantom)
    edge_added = 0
    for (sub, rt, sup) in sorted(a['edges']):
        triple = (_fid(sub), rt, _fid(sup))
        if triple in cstore._all_relations:
            continue
        cstore._index_relation(Relation(src_id=_fid(sub), tgt_id=_fid(sup), rel_type=RelationType(rt)))
        edge_added += 1
    if edge_added and not _flush_relations_with_retry(cstore):
        print('HARD_FAIL: os.replace race on relations flush.'); return 3
    print(f"  FRAME_* edges added: {edge_added}")
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    # EDGE READ-BACK (mirror T3 hardening): ALL intended frame-edges persisted + declared==actual
    cs_post = ps3._store_for(Corpus.CONCEPT)
    persisted_post = {t for t in cs_post._all_relations if t in intended_triples}
    edges_present = intended_triples.issubset(set(cs_post._all_relations))
    edge_count_ok = (edge_added == len(intended_triples - persisted_pre))
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and added > 0
               and edges_present and edge_count_ok)
    print(f"POST: atoms={post_atoms} (+{post_atoms - pre_atoms}) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged from {pre_cert}) | edges_present={edges_present} edge_added={edge_added} expected_new={len(intended_triples - persisted_pre)}")
    if not gate_ok:
        print('HARD_FAIL: gate failed (axiom/cap_pres/CERT preserved + ALL intended edges read-back + declared==actual).'); return 2
    print('=' * 74)
    print(f"FrameNet ingest v1 APPLY complete: +{added} SEMANTIC_FRAME atoms, +{edge_added} FRAME_* edges | axiom_term 206 | cap_pres 6/6 | CERT {post_cert} unchanged")
    print('=' * 74)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
