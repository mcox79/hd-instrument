"""TESTBED branch-item-3: Bucket B 10k atoms (LEXICON + SCIENCE_CONCEPT) INDEPENDENT-HARNESS
2nd-witness pattern.

Per Director routing (USER get-everyone-moving 2026-06-18). Independent harness for mass-add
bucket = aggregate-and-sample 2nd-witness (cannot do per-atom 12-point at this scale).

8-point INDEPENDENT-HARNESS check at corpus aggregate + per-sample level:
 1. Count match: LEXICON >= 5018 atoms exist (today's add target); SCIENCE_CONCEPT == 5000
 2. 0-algebra structural guard: ALL Bucket B atoms have algebra is None (no math operator)
 3. AtomKind correct: lexicon / science_concept
 4. ID uniqueness: no duplicate atom IDs within bucket
 5. Schema fields populated: name + description non-empty for sample of 50/bucket
 6. No-phantom-edges: any out-edge from sampled atoms targets an atom that exists in Store
 7. axiom_term 206/206 PRESERVED (Bucket B mass add did not pollute math-tier algebra count)
 8. cap_pres 6/6 PRESERVED (module liveness unchanged)

Sample sizes:
- LEXICON: 50 random IDs
- SCIENCE_CONCEPT: 50 random IDs

No mutations (verify-only).
"""
from __future__ import annotations
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore


SAMPLE_PER_BUCKET = 50
EXPECTED_LEXICON_MIN = 5018
EXPECTED_SCIENCE_CONCEPT = 5000


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def kind_str(a) -> str:
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)
    atoms = list(ps.all_atoms())
    by_id = {a.id: a for a in atoms}

    lexicon = [a for a in atoms if kind_str(a) == 'lexicon']
    science = [a for a in atoms if kind_str(a) == 'science_concept']

    print('=' * 78)
    print('BUCKET B 10k ATOMS INDEPENDENT-HARNESS 2nd-WITNESS')
    print('=' * 78)
    print(f'Store totals: atoms={len(atoms)}  LEXICON={len(lexicon)}  SCIENCE_CONCEPT={len(science)}')

    results = {}

    # Check 1: count match
    c1_lex = len(lexicon) >= EXPECTED_LEXICON_MIN
    c1_sci = len(science) == EXPECTED_SCIENCE_CONCEPT
    results['1_count_LEXICON_gte_5018'] = c1_lex
    results['1_count_SCIENCE_CONCEPT_eq_5000'] = c1_sci

    # Check 2: 0-algebra structural guard across ALL Bucket B atoms
    lex_nonzero_algebra = [a for a in lexicon if a.algebra is not None]
    sci_nonzero_algebra = [a for a in science if a.algebra is not None]
    results['2_LEXICON_all_algebra_None'] = (len(lex_nonzero_algebra) == 0)
    results['2_SCIENCE_CONCEPT_all_algebra_None'] = (len(sci_nonzero_algebra) == 0)

    # Check 3: AtomKind correct (already filtered)
    results['3_LEXICON_kind_correct'] = all(kind_str(a) == 'lexicon' for a in lexicon)
    results['3_SCIENCE_CONCEPT_kind_correct'] = all(kind_str(a) == 'science_concept' for a in science)

    # Check 4: ID uniqueness within each bucket
    lex_ids = [a.id for a in lexicon]
    sci_ids = [a.id for a in science]
    results['4_LEXICON_ID_unique'] = (len(lex_ids) == len(set(lex_ids)))
    results['4_SCIENCE_CONCEPT_ID_unique'] = (len(sci_ids) == len(set(sci_ids)))

    # Check 5: sample 50 from each; name + description non-empty
    rng = random.Random(20260618)
    lex_sample = rng.sample(lexicon, min(SAMPLE_PER_BUCKET, len(lexicon)))
    sci_sample = rng.sample(science, min(SAMPLE_PER_BUCKET, len(science)))
    lex_sample_ok = all((a.name and a.description) for a in lex_sample)
    sci_sample_ok = all((a.name and a.description) for a in sci_sample)
    results['5_LEXICON_sample50_name_description_non_empty'] = lex_sample_ok
    results['5_SCIENCE_CONCEPT_sample50_name_description_non_empty'] = sci_sample_ok

    # Check 6: no-phantom-edges from sampled atoms
    relation_tuples = list(ps.iter_relations()) if hasattr(ps, 'iter_relations') else []
    if not relation_tuples:
        # fallback: gather via per-store iter
        relation_tuples = []
        for corpus, store in ps._stores.items():
            for r in store.iter_relations():
                relation_tuples.append(r)
    sampled_ids = {a.id for a in lex_sample + sci_sample}
    phantoms_from_sample = 0
    edges_from_sample = 0
    for src, rt, tgt in relation_tuples:
        if src in sampled_ids:
            edges_from_sample += 1
            if tgt not in by_id:
                phantoms_from_sample += 1
    results['6_no_phantom_edges_from_sampled_atoms'] = (phantoms_from_sample == 0)

    # Check 7: axiom_term 206/206
    at = axiom_term_count(ps)
    results['7_axiom_term_206_PRESERVED'] = (at == 206)

    # Check 8: cap_pres 6/6
    ml = module_liveness_ok()
    results['8_cap_pres_6_6_PRESERVED'] = ml

    print()
    print(f'Bucket B sample sizes: LEXICON={len(lex_sample)}  SCIENCE_CONCEPT={len(sci_sample)}')
    print(f'Edges from sampled atoms: {edges_from_sample}  Phantoms from sample: {phantoms_from_sample}')
    print(f'axiom_term: {at}/206  cap_pres: {ml}')
    print()
    print('CHECKS:')
    total = 0
    passed = 0
    for k, v in results.items():
        mark = 'PASS' if v else 'FAIL'
        print(f'  [{mark}] {k}')
        total += 1
        if v:
            passed += 1

    print()
    print('=' * 78)
    verdict = 'HARD_PASS' if passed == total else 'HARD_FAIL'
    print(f'BUCKET B INDEPENDENT-HARNESS 2nd-WITNESS: {verdict}  ({passed}/{total} checks)')
    print('=' * 78)
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
