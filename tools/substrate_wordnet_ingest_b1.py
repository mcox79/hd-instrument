"""Bucket B / B1: WordNet top-5k high-frequency noun synsets -> LEXICON atoms.

Per USER-ratified 6h plan 2026-06-18 + Store-resident methodology rules:
 - RULE_wordnet_atoms_use_LEXICON_kind_not_research_finding (kind=LEXICON)
 - RULE_wordnet_atom_granularity_per_synset_not_per_word (per-synset, offset id)
 - RULE_wordnet_bears_on_LIMITED_math_only_internal_relations_metadata
     (bears_on math:: ONLY for explicit math content ~0-10%; hypernym/hyponym/
      synonym/meronym carried as METADATA FIELDS, not edges)
 - RULE_STEP_B_WordNet_extension_invariant_verify (STEP-B Option A baseline-snapshot)

DEFAULT = --dry-run (NO Store mutation; emits a schema sample + selection stats +
the gates that WILL run on APPLY, for Skunkworks SCHEMA-VET). --apply mutates the
Store SERIALLY (per the bulk-ingest concurrency gotcha: fresh-load + os.replace-race
retry + single invocation) with inline invariant gates.

VERSION NOTE (SCHEMA-VET decision): the Store methodology rule says "WordNet 3.1";
nltk ships WordNet 3.0 (different synset offsets than 3.1). This cell uses 3.0 and
records wordnet_version on every atom. id-scheme + 3.0-vs-3.1 = a SCHEMA-VET call.

Laptop-safe (no GPU, no bge). Deterministic. ASCII-only. 11th-rule (no LLM).
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

N_TARGET = 5000
HYPONYM_CAP = 30          # bound metadata size (high-freq nouns have many direct hyponyms)
WORDNET_VERSION = '3.0'   # nltk ships 3.0 (FLAG: methodology said 3.1; offsets differ)

# Conservative explicit-math detector (bears_on math:: candidates; rare for top nouns).
_MATH_LEXNAMES = {'noun.quantity', 'noun.relation'}
_MATH_KEYWORDS = (
    'number', 'integer', 'arithmetic', 'algebra', 'geometr', 'theorem', 'equation',
    'mathematic', 'numeral', 'fraction', 'quantity', 'magnitude',
)


def _synset_freq(s) -> int:
    """SemCor lemma-count frequency signal (built into WordNet; deterministic)."""
    return sum(l.count() for l in s.lemmas())


def select_top_nouns(wn, n: int):
    """Top-n noun synsets by (SemCor freq desc, offset asc) -- deterministic tiebreak."""
    nouns = list(wn.all_synsets('n'))
    ranked = sorted(nouns, key=lambda s: (-_synset_freq(s), s.offset()))
    return ranked[:n]


def _atom_id(s) -> str:
    """Namespaced SYNSET-NAME id (Skunkworks decision-2: version-STABLE across 3.0->3.1,
    unlike offsets which are version-FRAGILE). WN_<synset.name()> e.g. WN_person.n.01.
    synset.name() (lemma.pos.sense) is a unique WordNet identifier -> 0 collisions."""
    return f"WN_{s.name()}"


def _math_candidate(s) -> bool:
    """Conservative explicit-math detection for bears_on candidacy (NOT an edge yet -- 0-phantom enforced at APPLY)."""
    if s.lexname() in _MATH_LEXNAMES:
        return True
    defn = (s.definition() or '').lower()
    return any(k in defn for k in _MATH_KEYWORDS)


def build_atom(s, freq_rank: int) -> Atom:
    """One LEXICON atom per synset; internal relations as metadata fields (per methodology)."""
    direct_hyper = s.hypernyms()
    direct_hypo = s.hyponyms()
    meronyms = s.part_meronyms() + s.member_meronyms() + s.substance_meronyms()
    metadata = {
        'wordnet_version': WORDNET_VERSION,
        'pos': s.pos(),
        'synset_name': s.name(),
        'synset_offset': f"{s.offset():08d}",
        'lexname': s.lexname(),
        'lemma_freq_semcor': _synset_freq(s),
        'freq_rank': freq_rank,
        # internal relations as METADATA (not edges), per RULE_wordnet_bears_on_LIMITED:
        'synonyms': [l.name() for l in s.lemmas()],
        'hypernyms': [h.name() for h in direct_hyper],
        'hyponyms': [h.name() for h in direct_hypo[:HYPONYM_CAP]],
        'hyponyms_total': len(direct_hypo),
        'meronyms': [m.name() for m in meronyms[:HYPONYM_CAP]],
        'math_candidate': _math_candidate(s),
        'source': 'wordnet_3_0_nltk_top5k_noun_b1',
    }
    return Atom(
        id=_atom_id(s),
        name=s.name(),
        description=(s.definition() or '')[:500],
        kind=AtomKind.LEXICON,
        tier=Tier.TIER_LEXICON,
        corpus=Corpus.CONCEPT,
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
    from nltk.corpus import wordnet as wn
    synsets = select_top_nouns(wn, N_TARGET)
    atoms = [build_atom(s, i + 1) for i, s in enumerate(synsets)]

    n_math = sum(1 for a in atoms if a.metadata['math_candidate'])
    hypo_sizes = sorted((a.metadata['hyponyms_total'] for a in atoms), reverse=True)
    ids = [a.id for a in atoms]
    dup_ids = len(ids) - len(set(ids))

    print('=' * 72)
    print('B1 WordNet ingest DRY-RUN (no Store mutation) -- for Skunkworks SCHEMA-VET')
    print('=' * 72)
    print(f'WordNet version: {WORDNET_VERSION} (FLAG: methodology rule said 3.1; offsets differ)')
    print(f'selected: {len(atoms)} top-frequency noun synsets (by SemCor freq desc, offset asc)')
    print(f'AtomKind: LEXICON | tier: TIER_LEXICON | corpus: CONCEPT | algebra: None (no-algebra guard)')
    print(f'id-scheme: WN_<synset.name()> e.g. {atoms[0].id} (SYNSET-NAME, version-STABLE per Skunkworks decision-2; offset kept in metadata.synset_offset)')
    print(f'duplicate ids: {dup_ids} (0-phantom: internal relations are METADATA not edges -> no phantom risk)')
    print(f'bears_on math:: candidates (lexname noun.quantity/relation OR math-keyword in gloss): {n_math} '
          f'({100.0*n_math/len(atoms):.1f}% -- methodology expected ~0-10%)')
    print(f'  NOTE: bears_on edges are NOT emitted in dry-run; on APPLY emit ONLY if a math:: target atom resolves (0-phantom).')
    print(f'hyponyms_total distribution (capped at {HYPONYM_CAP} in stored list): max={hypo_sizes[0]} '
          f'median={hypo_sizes[len(hypo_sizes)//2]} (the cap bounds metadata size; total preserved in hyponyms_total)')
    print(f'freq range: rank1 freq={atoms[0].metadata["lemma_freq_semcor"]} ({atoms[0].name}) '
          f'-> rank{len(atoms)} freq={atoms[-1].metadata["lemma_freq_semcor"]} ({atoms[-1].name})')
    print()
    print('--- SAMPLE atoms (first 4 + 2 math-candidates) full schema ---')
    sample = atoms[:4] + [a for a in atoms if a.metadata['math_candidate']][:2]
    for a in sample:
        print(f'  id={a.id}  name={a.name}  kind={a.kind.value}  tier={a.tier.name}  corpus={a.corpus.name}  algebra={a.algebra}')
        print(f'     desc: {a.description[:90]}')
        m = a.metadata
        print(f'     pos={m["pos"]} lexname={m["lexname"]} freq={m["lemma_freq_semcor"]} rank={m["freq_rank"]} math_cand={m["math_candidate"]}')
        print(f'     synonyms={m["synonyms"][:6]}')
        print(f'     hypernyms={m["hypernyms"]}  hyponyms_total={m["hyponyms_total"]} (stored {len(m["hyponyms"])})')
        print(f'     meronyms={m["meronyms"][:4]}')
    print()
    print('--- gates that WILL run on --apply (STEP-B Option A invariant snapshot) ---')
    print('  PRE: axiom_term==206, cap_pres(module 6/6); HALT if not')
    print(f'  POST: atom delta == +{N_TARGET} (idempotent skip on existing id), axiom_term==206 (LEXICON no-algebra),')
    print('        cap_pres 6/6, all new atoms kind=LEXICON + algebra=None, read-back sample verifies')
    print('  bulk-ingest discipline: SERIAL single-invocation + fresh-load-per-batch + os.replace-race retry-fresh')
    print('=' * 72)
    print('DRY-RUN complete. NO Store mutation. Awaiting Skunkworks SCHEMA-VET before --apply.')
    return 0


def apply_run() -> int:
    from nltk.corpus import wordnet as wn
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(mod6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL (cap_pres or axiom_term != 206). Halting; no mutation.')
        return 1

    synsets = select_top_nouns(wn, N_TARGET)
    existing = {a.id for a in ps.all_atoms()}
    math_local_ids = {a.id for a in ps.all_atoms() if str(a.corpus.name) == 'MATH'}
    added = 0
    resolved_edges = []   # Skunkworks decision-3 cert-condition: report ACTUAL resolved bears_on edges
    from backend.substrate_index.schema import RelationType
    for i, s in enumerate(synsets):
        atom = build_atom(s, i + 1)
        if atom.id in existing:
            continue
        ps.add_atom(atom, source='b1_wordnet_top5k_noun_lexicon',
                    note='STEP-B WordNet extension; LEXICON; per-synset; internal relations as metadata')
        existing.add(atom.id)
        added += 1
        # bears_on math:: ONLY on a RESOLVING target (0-phantom): exact lemma == existing math:: local-id.
        if atom.metadata['math_candidate']:
            for lemma in atom.metadata['synonyms']:
                if lemma in math_local_ids:               # exact, conservative; no fuzzy matching
                    tgt = f'math::{lemma}'
                    ps.add_relation(f'concept::{atom.id}', RelationType.RELATES, tgt,
                                    source='b1_wordnet_bears_on',
                                    note='bears_on math (WordNet synset -> math atom; exact-lemma match)')
                    resolved_edges.append((atom.id, tgt))

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    # read-back sample verify
    rb = ps.get_atom(f'concept::{_atom_id(synsets[0])}')
    rb_ok = rb is not None and rb.kind == AtomKind.LEXICON and rb.algebra is None
    gate_ok = (post_axiom == 206) and post_mod and (post_n == pre_n + added) and rb_ok and added > 0
    print(f'POST: atoms={post_n} (added {added})  axiom_term={post_axiom}  cap_pres={post_mod}  read-back_ok={rb_ok}')
    # Skunkworks decision-3 cert-condition: report the ACTUAL resolved bears_on edges for spot-check
    print(f'resolved bears_on math:: edges: {len(resolved_edges)} (0-phantom: only exact-lemma==math-local-id matches)')
    for src, tgt in resolved_edges[:50]:
        print(f'    {src} -RELATES(bears_on)-> {tgt}')
    if not resolved_edges:
        print('    (none -- no top-5k noun lemma exactly matches an existing math:: atom id; '
              'math_candidate flags preserved in metadata for future curated linking)')
    if not gate_ok:
        print('HARD_FAIL: gate or read-back failed. Inspect (no auto-revert on bulk -- manual).')
        return 2
    print('=' * 72)
    print(f'B1 WordNet APPLY complete: +{added} LEXICON atoms + {len(resolved_edges)} bears_on edges  |  atoms {pre_n} -> {post_n}  |  axiom_term 206/206  |  cap_pres 6/6')
    print('=' * 72)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='mutate the Store (default: dry-run only)')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
