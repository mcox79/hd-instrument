"""Atomize the ConceptNet KG inference-transfer eval as 1 CERT_CHAIN_GRADE EXPERIMENT_RECORD (Skunkworks verdict-VET
PASS 2026-06-19; the FIRST Track-B knowledge_graph cert-grade pull-up). CERT 579 -> 580.

One run = one record (NOT two; the 2 findings are 2 verdicts within the single run -- no-double-count discipline).
Primary verdict = HARD_FAIL inference-transfer (rigorous discriminating null; coverage-completion-not-reasoning
REPLICATED multi-corpus WordNet+ConceptNet). Sub-finding = HARD_PASS fact-fabrication-bound (the refuse-gate
generalizes to KG-completion; composes A2-v6).

Cert-requirements (Skunkworks gate): (1) HONEST-SCOPE the HARD_FAIL to substrate-VS-BGE (closure=1.0 perfect-by-
construction is NOT the load-bearing comparison); claim = "underperforms frozen-bge single-hop cosine on firewalled
held-out KG-completion". (2) cite the metrics' authoritative cell_commit=8046977b0292.

SAFE atomize: Atom-construction (enum MEMBERS) -> add_atom -> fresh-Store all_atoms() LOAD gate. MATH partition (run in
a serialized single-writer window). DRY-RUN default; --apply. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

DATE = '2026-06-19'
ATOM_ID = 'T3/EXP_conceptnet_kg_inference_transfer_cpu_v1'
METRICS = Path('data/substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json')
CELL_COMMIT = '8046977b0292'   # metrics.json authoritative (Skunkworks req-2)


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def build_metadata(m):
    sub = m['substrate']; clo = m['closure_baseline']; bge = m['frozen_bge_baseline']
    honest = ("HARD_FAIL is EARNED on substrate-VS-frozen-bge: substrate Hits@10=%.4f < frozen-bge single-hop cosine "
              "Hits@10=%.4f (substrate rank-AUROC=%.3f < bge %.3f). The transitive-closure baseline (Hits@10=1.0) is "
              "PERFECT-BY-CONSTRUCTION (WITH-path == closure-reachable set) and is NOT the load-bearing comparison. "
              "CLAIM: the substrate's cf-RPE HDC multi-hop completion UNDERPERFORMS frozen-bge single-hop cosine on "
              "firewalled NEVER-INGESTED held-out KG-completion (no positive KG-reasoning lift)."
              % (sub['hits@10'], bge['hits@10'], m['substrate_auroc_with_path'], m['bge_auroc_with_path']))
    return {
        'provenance_quality': 'CERT_CHAIN_GRADE', 'relevance_tier': 'ACTIVE',
        'verdict': 'HARD_FAIL', 'verdict_raw': 'HARD_FAIL_inference_transfer',
        'fact_fabrication_bound_verdict': 'HARD_PASS',
        'run_mode': m.get('run_mode', 'full'), 'metrics_source': m.get('metrics_source'),
        'cell_commit': CELL_COMMIT, 'experiment_path': 'experiments/exp_substrate_conceptnet_kg_inference_transfer_cpu_v1.py',
        'metrics_path': str(METRICS), 'scope': m.get('scope', 'v1.1-transitive-scoped'),
        'prereg': 'ConceptNet eval pre-reg v1.1-transitive-scoped (Skunkworks SCHEMA-VET STRONG-PASS 2026-06-19)',
        'hypothesis': ('the substrate composes multi-hop KG inferences on never-ingested held-out edges (inference-'
                       'transfer) with a LIFT above transitive-closure + frozen-bge single-hop cosine'),
        'honest_scope': honest,
        'heldout_edges_in_compose_graph': m.get('heldout_edges_in_compose_graph'),
        'heldout_edges_in_store': m.get('heldout_edges_in_store'),
        'key_metrics': {
            'n_with_path': m['n_with_path'], 'n_without_path': m['n_without_path'],
            'n_trivial': m['n_trivial'], 'n_nontrivial': m['n_nontrivial'],
            'substrate_hits10': sub['hits@10'], 'substrate_hits1': sub['hits@1'], 'substrate_mrr': sub['mrr'],
            'substrate_auroc': m['substrate_auroc_with_path'],
            'frozen_bge_hits10': bge['hits@10'], 'frozen_bge_auroc': m['bge_auroc_with_path'],
            'closure_hits10': clo['hits@10'], 'closure_auroc': m['closure_auroc_with_path'],
            'lift_hits10_vs_bge': m['lift_hits10_vs_bge'], 'min_lift_hits10': m['min_lift_hits10'],
            'nontrivial_lift_hits10': m['nontrivial_lift_hits10'], 'trivial_lift_hits10': m['trivial_lift_hits10'],
            'fact_fabrication_bound_auroc': m['fact_fabrication_bound_auroc'],
        },
        'metrics_headline': ('inference-transfer HARD_FAIL (substrate Hits@10 %.3f < frozen-bge single-hop %.3f < exact-'
                             'closure 1.0; substrate AUROC %.3f < bge %.3f) -> substrate UNDERPERFORMS single-hop bge. '
                             'fact-fabrication-bound HARD_PASS (AUROC %.3f = refuse-gate). Coverage-completion-not-'
                             'reasoning REPLICATED multi-corpus (WordNet Item-1/M1/HYP-5 -> ConceptNet).'
                             % (sub['hits@10'], bge['hits@10'], m['substrate_auroc_with_path'], m['bge_auroc_with_path'],
                                m['fact_fabrication_bound_auroc'])),
        'metric_type': 'filtered_hits_mrr_rank_auroc',
        'transitive_rels': m.get('transitive_rels'),
        'prior_art_baselines_cited': m.get('prior_art_baselines_cited'),
        'strengthens_cert': ['math::T3/EXP_a2_decisive_test_untuned_auroc_grown_cpu_v1 (refuse-gate generalizes KG->KG-completion)'],
        'composes': ['Item-1 PART_OF heldout', 'M1 HYPERNYM heldout', 'HYP-5 depth-ceiling (coverage-completion-not-reasoning, now multi-corpus)'],
        'record_class': 'cert_grade_honest_negative', 'term_class': 'EXPERIMENT_RECORD',
        'deterministic_no_llm': True, 'eleventh_rule_clean': True,
        'source': 'conceptnet_5.7_en_bounded_v1', 'era': DATE,
        'significance': 'FIRST Track-B knowledge_graph cert-grade pull-up; pipeline ingest->eval->verdict-VET->cert validated end-to-end',
    }


def run(apply: bool) -> int:
    if not METRICS.exists():
        print(f'metrics not found: {METRICS}'); return 5
    m = json.loads(METRICS.read_text(encoding='utf-8'))
    if m.get('verdict') != 'HARD_FAIL' or m.get('fact_fabrication_bound_verdict') != 'HARD_PASS':
        print(f'metrics verdicts unexpected: {m.get("verdict")} / {m.get("fact_fabrication_bound_verdict")}'); return 6
    if m.get('heldout_edges_in_compose_graph') != 0 or m.get('heldout_edges_in_store') != 0:
        print('FIREWALL not clean in metrics; refuse to atomize.'); return 7
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_axiom = axiom_term_count(ps)
    existing = {str(a.id) for a in ps.all_atoms()}
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom} | atom present already: {ATOM_ID in existing}', flush=True)
    if ATOM_ID in existing:
        print('atom already present -> idempotent skip.'); return 0
    md = build_metadata(m)
    atom = Atom(id=ATOM_ID, name='ConceptNet knowledge_graph inference-transfer (Track-B pilot)',
                corpus=Corpus.MATH, tier=Tier.TIER_3_ALGORITHM, kind=AtomKind.EXPERIMENT_RECORD, algebra=None,
                description=('ConceptNet bounded-v1 KG inference-transfer eval (firewalled never-ingested held-out): the '
                             'substrate cf-RPE HDC multi-hop completion underperforms frozen-bge single-hop cosine '
                             '(HARD_FAIL, no positive lift) BUT the fact-fabrication-bound HARD_PASSes (refuse-gate). '
                             'Coverage-completion-not-reasoning replicated multi-corpus.'),
                metadata=md)
    print(f'  built {atom.id}: kind={atom.kind.name} tier={atom.tier.name} corpus={atom.corpus.name} pq={md["provenance_quality"]} verdict={md["verdict"]}/{md["fact_fabrication_bound_verdict"]}')
    if not apply:
        print('\nDRY-RUN OK. Re-run with --apply -> CERT 579->580.'); return 0
    ps.add_atom(atom, source='atomize_conceptnet_kg_eval_CERT580',
                note='Skunkworks verdict-VET PASS; Track-B knowledge_graph honest-negative + fact-fab-bound; CERT 579->580')
    # fresh-Store LOAD gate
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    by = {str(a.id): a for a in ps2.all_atoms()}
    present = ATOM_ID in by
    pq = (by.get(ATOM_ID).metadata or {}).get('provenance_quality') if present else None
    gate_ok = (present and pq == 'CERT_CHAIN_GRADE' and post_cert == pre_cert + 1 and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +1) axiom={post_axiom} | present={present} pq={pq} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate / CERT count.'); return 8
    print(f'\nATOMIZE OK: {ATOM_ID} CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. Route for Skunkworks landed-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
