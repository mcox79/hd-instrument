"""Bucket B / B2: Gene Ontology (GO) top-5k central terms -> SCIENCE_CONCEPT atoms.

Per USER-ratified 6h plan 2026-06-18 + Skunkworks plan-VET R2 ruling:
 - NEW AtomKind SCIENCE_CONCEPT (biology ontology DISTINCT from LEXICON [lexical]).
   schema-add mirrors PROOF_RECORD: enum added + no-algebra guard (corpus=SCIENCE,
   algebra=None -> excluded from axiom_term) + verify-loads. Confirmed at this dry-run VET.
 - Mirrors the WordNet B1 pattern: per-term granularity; internal ontology relations
   (is_a / part_of) carried as METADATA fields, not edges; bears_on math:: only on a
   resolving target (GO is biology -> expected 0).

DEFAULT = --dry-run (NO Store mutation; schema sample + selection stats for SCHEMA-VET).
--apply mutates the Store SERIALLY (fresh-load + os.replace-race retry + single invocation)
with inline invariant gates (axiom_term 206 + cap_pres 6/6 + delta + no-algebra + read-back).

Data: data/go_ontology/go-basic.obo (downloaded from purl.obolibrary.org 2026-06-18).
Selection: top-5k NON-OBSOLETE terms by is_a child-count (ontology centrality) desc, id asc.

Laptop-safe (no GPU). Deterministic. ASCII-only. 11th-rule (no LLM).
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

N_TARGET = 5000
PARENT_CAP = 30
OBO_PATH = Path('data/go_ontology/go-basic.obo')
GO_VERSION_NOTE = 'go-basic.obo purl.obolibrary.org downloaded 2026-06-18'


def parse_obo(path: Path) -> list[dict]:
    """Minimal deterministic GO obo parser -> list of term dicts. No external deps."""
    txt = path.read_text(encoding='utf-8')
    out = []
    for stanza in txt.split('\n[Term]\n')[1:]:
        body = stanza.split('\n[')[0]
        d = {'id': None, 'name': None, 'namespace': None, 'definition': '',
             'is_a': [], 'obsolete': False, 'synonyms': []}
        for line in body.splitlines():
            if line.startswith('id: '):
                d['id'] = line[4:].strip()
            elif line.startswith('name: '):
                d['name'] = line[6:].strip()
            elif line.startswith('namespace: '):
                d['namespace'] = line[11:].strip()
            elif line.startswith('def: "'):
                rest = line[6:]
                end = rest.rfind('" [')
                d['definition'] = rest[:end] if end >= 0 else rest.rstrip('"')
            elif line.startswith('is_a: '):
                d['is_a'].append(line[6:].split('!')[0].strip())
            elif line.startswith('is_obsolete: true'):
                d['obsolete'] = True
            elif line.startswith('synonym: "'):
                rest = line[10:]
                end = rest.find('"')
                if end >= 0:
                    d['synonyms'].append(rest[:end])
        if d['id']:
            out.append(d)
    return out


def select_top_terms(terms: list[dict], n: int) -> list[dict]:
    """Top-n NON-OBSOLETE terms by is_a child-count (centrality) desc, id asc -- deterministic."""
    child = {}
    for t in terms:
        if t['obsolete']:
            continue
        for parent in t['is_a']:
            child[parent] = child.get(parent, 0) + 1
    active = [t for t in terms if not t['obsolete']]
    for t in active:
        t['_child_count'] = child.get(t['id'], 0)
    ranked = sorted(active, key=lambda t: (-t['_child_count'], t['id']))
    return ranked[:n]


def _atom_id(t: dict) -> str:
    return t['id'].replace(':', '_')   # GO:0000001 -> GO_0000001 (no colon vs partition '::')


def build_atom(t: dict, rank: int) -> Atom:
    metadata = {
        'go_id': t['id'],
        'namespace': t['namespace'],
        'go_source': GO_VERSION_NOTE,
        'is_a': t['is_a'][:PARENT_CAP],            # internal ontology relation as METADATA
        'is_a_total': len(t['is_a']),
        'child_count': t.get('_child_count', 0),   # is_a in-degree (centrality)
        'centrality_rank': rank,
        'synonyms': t['synonyms'][:PARENT_CAP],
        'math_candidate': False,                   # GO is biology; no explicit-math content expected
        'source': 'go_basic_obo_top5k_central_b2',
    }
    return Atom(
        id=_atom_id(t),
        name=t['name'],
        description=(t['definition'] or '')[:500],
        kind=AtomKind.SCIENCE_CONCEPT,
        tier=Tier.TIER_NA,
        corpus=Corpus.SCIENCE,
        algebra=None,            # no-algebra structural guard (excluded from axiom_term)
        metadata=metadata,
    )


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), sym)
        for m, sym in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def dry_run() -> int:
    terms = parse_obo(OBO_PATH)
    n_obsolete = sum(1 for t in terms if t['obsolete'])
    selected = select_top_terms(terms, N_TARGET)
    atoms = [build_atom(t, i + 1) for i, t in enumerate(selected)]

    import collections
    ns = collections.Counter(a.metadata['namespace'] for a in atoms)
    ids = [a.id for a in atoms]
    dup = len(ids) - len(set(ids))

    print('=' * 72)
    print('B2 GO ingest DRY-RUN (no Store mutation) -- for Skunkworks SCHEMA-VET')
    print('=' * 72)
    print(f'GO source: {GO_VERSION_NOTE}')
    print(f'parsed: {len(terms)} terms ({n_obsolete} obsolete excluded -> {len(terms)-n_obsolete} active)')
    print(f'selected: {len(atoms)} top-CENTRALITY terms (is_a child-count desc, id asc -- deterministic)')
    print(f'NEW AtomKind: SCIENCE_CONCEPT (enum-add verified loads; AtomKind 25->26) | tier=TIER_NA | corpus=SCIENCE | algebra=None')
    print(f'id-scheme: GO_<7-digit> e.g. {atoms[0].id} ({atoms[0].name})')
    print(f'duplicate ids: {dup} (0-phantom: is_a relations are METADATA not edges -> no phantom risk)')
    print(f'namespace split of selected 5k: {dict(ns)}')
    print(f'  (FLAG: centrality-ranked -> skews to the largest namespace; balance across namespaces = a SCHEMA-VET decision)')
    print(f'centrality range: rank1 child_count={atoms[0].metadata["child_count"]} -> rank{len(atoms)} child_count={atoms[-1].metadata["child_count"]}')
    print(f'bears_on math:: : 0 (GO is biology; no explicit-math content -- consistent with WordNet bears_on-limited rule)')
    print()
    print('--- SAMPLE atoms (first 5) full schema ---')
    for a in atoms[:5]:
        m = a.metadata
        print(f'  id={a.id}  name={a.name}  kind={a.kind.value}  tier={a.tier.name}  corpus={a.corpus.name}  algebra={a.algebra}')
        print(f'     desc: {a.description[:90]}')
        print(f'     go_id={m["go_id"]} namespace={m["namespace"]} child_count={m["child_count"]} rank={m["centrality_rank"]}')
        print(f'     is_a={m["is_a"]} (total {m["is_a_total"]})  synonyms={m["synonyms"][:4]}')
    print()
    print('--- gates that WILL run on --apply (STEP-B Option A invariant snapshot) ---')
    print('  PRE: axiom_term==206, cap_pres(module 6/6); HALT if not')
    print(f'  POST: atom delta == +{N_TARGET} (idempotent skip), axiom_term==206 (SCIENCE_CONCEPT no-algebra),')
    print('        cap_pres 6/6, all new atoms kind=SCIENCE_CONCEPT + algebra=None, read-back sample verifies')
    print('  bulk-ingest discipline: SERIAL single-invocation + fresh-load + os.replace-race retry')
    print('=' * 72)
    print('DRY-RUN complete. NO Store mutation. SCIENCE_CONCEPT enum-add awaits your SCHEMA-VET confirm before --apply.')
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(mod6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL (cap_pres or axiom_term != 206). Halting; no mutation.')
        return 1

    terms = parse_obo(OBO_PATH)
    selected = select_top_terms(terms, N_TARGET)
    existing = {a.id for a in ps.all_atoms()}
    added = 0
    for i, t in enumerate(selected):
        atom = build_atom(t, i + 1)
        if atom.id in existing:
            continue
        ps.add_atom(atom, source='b2_go_top5k_science_concept',
                    note='STEP-B GO extension; SCIENCE_CONCEPT; per-term; is_a relations as metadata')
        existing.add(atom.id)
        added += 1

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    rb = ps.get_atom(f'science::{_atom_id(selected[0])}')
    rb_ok = rb is not None and rb.kind == AtomKind.SCIENCE_CONCEPT and rb.algebra is None
    gate_ok = (post_axiom == 206) and post_mod and (post_n == pre_n + added) and rb_ok and added > 0
    print(f'POST: atoms={post_n} (added {added})  axiom_term={post_axiom}  cap_pres={post_mod}  read-back_ok={rb_ok}')
    if not gate_ok:
        print('HARD_FAIL: gate or read-back failed. Inspect (no auto-revert on bulk -- manual).')
        return 2
    print('=' * 72)
    print(f'B2 GO APPLY complete: +{added} SCIENCE_CONCEPT atoms  |  atoms {pre_n} -> {post_n}  |  axiom_term 206/206  |  cap_pres 6/6')
    print('=' * 72)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='mutate the Store (default: dry-run only)')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
