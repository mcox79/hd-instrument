"""Skunkworks 2026-06-20 -- atomize 2 nodded CERT-NEUTRAL MM characterizations (lever family). CERT 588 UNCHANGED.
- T3/EXP_capacity_sweet_spot_v2_cpu_v1 (LEVER 1.5 v2): MM -- adaptive sparsity selector mechanically correct but NO
  selection value (fixed-f=0.01 never beaten; broad sweet-spot; cue-noise cost flip=0.3 did NOT create a narrow sweet-spot).
- T3/EXP_pca_dimension_selector_lever_v1_cpu_v1 (LEVER 2): MM-NEGATIVE -- PCA-to-top-k NEVER beats full-N cosine recall
  (non-circular, measured on recall out-of-sample); no noise-only subspace to shed for cosine NN; denoising premise refuted.
Both EXPERIMENT_RECORD / MATH / TIER_3_ALGORITHM / algebra=None / pq=MEASURED_MECHANISM (CERT-neutral).
A5: PRE CERT=588 -> POST 588; axiom 206; cap_pres 6/6; +2 atoms; Store re-loads. ASCII. Idempotent.
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


def mm(rid, name, desc, mp, km, scope):
    return Atom(id=rid, name=name, description=desc, kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
        metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'MEDIUM','run_mode':'full',
                  'verdict':'MEASURED_MECHANISM','metrics_path':mp,'key_metrics':km,'honest_scope':scope,
                  'composes_with':['T3/EXP_sparse_boundary_v2_cpu_v1','T3/EXP_crosstalk_capacity_law_v1',
                                   'RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best'],
                  'cert_vet_status':'landed_VET_skunkworks_2026-06-20_MEASURED_MECHANISM','atomized_by':'skunkworks',
                  'atomized_date':'2026-06-20','era':'comprehensive_program_phase3_glassbox'})


ATOMS = [
  mm('T3/EXP_capacity_sweet_spot_v2_cpu_v1',
     'Experiment record (MEASURED_MECHANISM): LEVER 1.5 capacity sweet-spot -- a load-adaptive sparsity selector is mechanically correct (sel_f varies with load) but earns NO selection value (a fixed sparsest-f=0.01 is NEVER beaten; the sweet-spot is BROAD)',
     ('Load-adaptive sparsity-f selector (largest-viable-f meeting 2x capacity margin + K_MIN=8 bits, under cue-noise flip=0.3). '
      'The selector ADAPTS (sel_f={alpha0.1:0.1, 0.5:0.05, 1.0:0.02, 2.0:0.01}) -- the v1 non-adaptive bug is fixed. BUT earns_keep=False: '
      'a single fixed f=0.01 is NEVER beaten by the adaptive selector (within 0.019 of oracle), because the capacity sweet-spot is BROAD '
      'and the cue-noise cost (flip=0.3) does NOT create a narrow sweet-spot where selection is needed. Per the lever-design discipline '
      '(selector chain-grade requires a COST that makes the naive-best-fixed lose): no such cost here (capacity OR cue-noise) -> "always '
      'sparsest f" suffices -> the measurement machinery adds no selection value. MEASURED_MECHANISM (NOT a chain-grade lever; the honest '
      'close of the LEVER 1.5 arc -- v1 caught non-adaptive, v2 fixed it + tested the cost, found no selection value).'),
     'data/exp_capacity_sweet_spot_v2_cpu_v1/metrics.json',
     {'selector_adaptive': True, 'sel_f_by_load': {'0.1':0.1,'0.5':0.05,'1.0':0.02,'2.0':0.01}, 'earns_keep': False,
      'never_beaten_fixed_f': 0.01, 'within_of_oracle': 0.019, 'cue_noise_flip': 0.3, 'n_seeds': 3,
      'finding': 'broad sweet-spot -> fixed sparsest-f suffices -> no selection value (capacity OR cue-noise cost)'},
     ('Load-adaptive sparsity selection is mechanically correct but adds NO selection value at N=4096/flip=0.3: a fixed f=0.01 is '
      'never beaten (broad sweet-spot; no over-sparsity cost on capacity OR cue-noise creates a narrow optimum). NOT chain-grade; '
      'MEASURED_MECHANISM. Characterizes WHEN selection earns its keep (only when the sweet-spot is NARROW).')),
  mm('T3/EXP_pca_dimension_selector_lever_v1_cpu_v1',
     'Experiment record (MEASURED_MECHANISM, NEGATIVE): LEVER 2 PCA dimension-selector -- PCA-to-top-k NEVER beats full-N cosine recall (non-circular); the denoising-via-PCA premise is REFUTED',
     ('PCA dimension-selector: reduce substrate-KV dimensionality to top-k eigencomponents to "denoise" / trade capacity for SNR. '
      'Built NON-CIRCULAR (measured on RECALL out-of-sample, NOT the crosstalk-moment which is by-construction circular per 7315be3c). '
      'FINDING (refutes the premise empirically): PCA-to-top-k does NOT beat full-N cosine recall at ANY noise level or anisotropy '
      '(sf=3.0: full 0.94 > selk 0.91; ranks_PCA_robustly_helps=[] on 3 seeds; never_worse but never robustly-better). MECHANISM: full-N '
      'cosine nearest-neighbor already uses all dims efficiently + isotropic query noise averages out in the normalized dot product -> '
      'there is NO noise-only subspace to shed for cosine recall. The denoising-via-PCA premise is WRONG; data refuted it. '
      'MEASURED_MECHANISM negative-bound (PCA dim-reduction does not help substrate-KV cosine recall).'),
     'data/exp_pca_dimension_selector_lever_v1_cpu_v1/metrics.json',
     {'pca_beats_full_N': False, 'ranks_PCA_robustly_helps': [], 'never_worse_than_full': True,
      'example_sf3_full': 0.94, 'example_sf3_selk': 0.91, 'non_circular': 'measured on recall out-of-sample not the moment',
      'n_seeds': 3, 'finding': 'no noise-only subspace to shed for cosine NN -> PCA only loses discriminative info'},
     ('PCA-to-top-k never beats full-N cosine recall (non-circular, recall-measured): full-N cosine NN already uses all dims + '
      'isotropic noise averages out -> no noise-only subspace to shed. Denoising-via-PCA premise REFUTED. MEASURED_MECHANISM '
      'negative-bound. (Possible revival angle routed to Research: a non-cosine/non-normalized readout where a discardable null-space exists.)')),
]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 588:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=588). HALT."); return 1
    added = 0
    for at in ATOMS:
        if ps.get_atom(at.qualified_id) is not None:
            print(f"  SKIP exists: {at.id}")
        else:
            ps.add_atom(at, source='skunkworks_lever1_5v2_lever2_MM_2026_06_20', note='lever-family MM characterizations (CERT-neutral)')
            print(f"  ADD: {at.id}"); added += 1
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = all(ps2.get_atom(at.qualified_id) is not None for at in ATOMS)
    bad = any((ps2.get_atom(at.qualified_id).algebra is not None) or
              ((ps2.get_atom(at.qualified_id).metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE') for at in ATOMS)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==588 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+added)
    print("GATE:", "OK -- 2 lever MM atoms, CERT 588 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
