"""Skunkworks 2026-06-21 -- landed-VET atomize the continual-write label-free-importance cell = MEASURED_MECHANISM
(scope-locating, CERT-NEUTRAL). Verified off per_unit (full 3-seed, cv=0.000): Workload A (access-correlated) PASS --
3 label-free access-proxies (LRU/access_freq/kramers) = oracle 1.0, beat write_all=0.0 + fifo=0.0 (lever-design bar MET,
robust); Workload B (access-uncorrelated) FAIL -- all 5 proxies=0.0 (info-theoretic limit: importance w/ no observable
correlate is uninferable label-free). MIDDLE_BAND scope-bound -> MEASURED_MECHANISM (locates WHERE label-free importance
works; NOT a both-workloads chain-grade). Symmetric guard: don't inflate scope-bound to chain-grade.
A5: PRE CERT=583 -> POST 583 UNCHANGED (MM); axiom 206; cap_pres 6/6; +1 atom; reloads. ASCII. Idempotent.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name)=='MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra)>=3 and 'oeis' not in str(a.id).lower() and not str(a.id).startswith('T3/wikidata_'))
def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder','viterbi_decode'),('hdlab.perceptron','StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler','NERTagger'),('hdlab.bayesian_inference','EMMixture'),
        ('backend.substrate_index.intent_classifier','IntentClassifier'),('backend.substrate_index.refuse_gated_retriever','RefuseGatedRetriever')])


ATOM = Atom(
    id='T3/EXP_continual_write_label_free_importance_v1',
    name=('Experiment record (MEASURED_MECHANISM): continual-write label-free-importance is viable IFF importance is '
          'access-correlated -- 3 label-free access-proxies (LRU/access_freq/kramers) recover the oracle + beat write-all '
          '& FIFO in the access-correlated regime; NO label-free proxy recovers the access-UNcorrelated silent-important '
          'case (info-theoretic limit). Scope-bound (MIDDLE_BAND)'),
    description=(
        'The continual-write lever (label-free importance-inference eviction policy) tested on 2 workloads x 5 proxies x '
        '4 arms, full 3-seed (cv=0.000), faithful Hopfield store (W=sum v k^T sign-readout, reuses Skunkworks GREEN-demo '
        'core verbatim). RESULT (verified off per_unit): Workload A (access-correlated) PASS -- LRU/access_freq/kramers '
        'all = oracle 1.00, vs write_all=0.00 + fifo=0.00 (the lever-design bar -- beats BOTH naive in a regime where each '
        'fails -- MET, robust across 3 independent access-proxies). Workload B (access-uncorrelated, silent-important) FAIL '
        '-- ALL 5 proxies=0.00 vs oracle 1.00. MECHANISM/SCOPE: label-free importance-inference works WHEN importance '
        'correlates with an OBSERVABLE (access-recency/-frequency); it CANNOT recover importance with NO observable '
        'correlate (Workload B) -- an INFORMATION-THEORETIC limit (not a proxy-tuning gap; marginal-utility recall_error '
        'predicted to fail B identically). MIDDLE_BAND scope-bound -> MEASURED_MECHANISM: the cell LOCATES where the lever '
        'works (~access-correlated, ~50% of realistic workloads per Director) + the fundamental limit. NOT a both-workloads '
        'chain-grade (B hard-fails -> not a clean universal capability; symmetric guard: scope-bound not inflated to '
        'chain-grade). NOTE: age_weighted + recall_error (as-implemented) scored 0.00 even on A = poor implementations '
        '(not the access-proxies that work).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'MEDIUM','run_mode':'full','verdict':'MEASURED_MECHANISM',
              'metrics_path':'data/exp_continual_write_label_free_importance_v1/metrics.json',
              'key_metrics':{'workloadA_access_correlated':{'oracle':1.0,'LRU':1.0,'access_freq':1.0,'kramers':1.0,'write_all':0.0,'fifo':0.0,'pass':True},
                             'workloadB_access_uncorrelated':{'oracle':1.0,'all_5_proxies':0.0,'pass':False},
                             'n_seeds':3,'cv':0.0,'best_proxy_switches_A_to_B':False},
              'honest_scope':('Label-free continual-write importance-inference is viable IFF importance is ACCESS-CORRELATED '
                              '(Workload A: 3 access-proxies=oracle, beat write-all+FIFO, robust 3-seed cv=0); the access-'
                              'UNcorrelated silent-important case (Workload B) is UNRECOVERABLE label-free (information-'
                              'theoretic: no observable correlate). Scope-bound MEASURED_MECHANISM (locates where the lever '
                              'works + the fundamental limit), NOT a both-workloads chain-grade. age_weighted/recall_error '
                              'as-implemented are poor (0 even on A).'),
              'composes_with':['T3/EXP_sparse_boundary_v2_cpu_v1','RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best'],
              'verified_off_data':'skunkworks landed-VET independent recompute off per_unit (full 3-seed cv=0; A 3-proxies=oracle/naive=0; B all=0); matches cell-author + Director cross-check + my SCHEMA-VET prediction',
              'cert_vet_status':'LANDED_VET_skunkworks_2026-06-21_MEASURED_MECHANISM_scope_locating',
              'atomized_by':'skunkworks','atomized_date':'2026-06-21','era':'comprehensive_program_phase3_glassbox',
              'distinctive_axis':'label-free importance via access-recency (my de-risk contribution -> Research v2/v3 adopted); B-fail is info-theoretic (my proxy-semantics ruling, empirically confirmed)'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_continual_write_label_free_MM_2026_06_21', note='continual-write label-free MM scope-locating (CERT-neutral)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- continual-write MM atomized, CERT 583 UNCHANGED (CERT-neutral scope-locating)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
