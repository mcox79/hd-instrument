"""Skunkworks 2026-06-21 -- landed-VET atomize the dense-projected-KV envelope = MEASURED_MECHANISM (CERT-NEUTRAL).
Verified off per_unit (independent recompute matched: ARM1 M-indep superposition @d768/s0.1/M10k = 0.8242 cv=0.0070;
curve {1k:1.0,3k:1.0,10k:0.824,30k:0.286,100k:0.065}; ARM0 kNN + ARM2 softmax = 1.0 all M) + mechanism M-independence
CONFIRMED off cell code (W = codebook[y].T@K is (d,d) O(d^2) M-indep; decode argmax cosine over C=256 codebook, NOT over M
values). C-codebook LIFTS recall +0.21 above the i.i.d. distinct-value Phi(1/sqrt(13))~0.61 prediction (capacity-extender,
empirically confirms the info-theoretic/substrate-vocab insight).

TIER: MEASURED_MECHANISM now (genuine verified POSITIVE: best-case M-indep capacity envelope + C-codebook lift; a real win
vs the flagship sparse-negative). The SUBSTRATE chain-grade-at-bound is GATED on the GPU follow-up: (1) FLAG-3 calibration
HALT-gate UNRUN (random-keys ARM0=1.0 is by-construction, NOT the pythia meter-check vs CERT591's 0.827); (2) random keys =
BEST-CASE upper bound -- the substrate uses LEARNED keys (<= this per HMM arXiv:2503.09518); learned-key subset pending.
Symmetric: NOT over-demotion (it IS a positive, atomized as such); NOT inflation (don't mint a substrate CERT on the
upper-bound proxy + unvalidated meter). Upgradeable to chain-grade-at-bound on the follow-up re-VET (this SAME atom).
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
    id='T3/EXP_dense_projected_KV_envelope_v1',
    name=('Experiment record (MEASURED_MECHANISM): M-INDEPENDENT superposition KV with fixed C-codebook decode holds '
          'value-CLASS recall>=0.80 up to M~13xd (0.824 @ M=10k, d=768, cv=0.007) on BEST-CASE i.i.d. random keys, then '
          'RMT-crowds (0.29@30k, 0.065@100k); the C-codebook LIFTS recall +0.21 above the distinct-value Phi prediction. '
          'O(M*d) baselines (kNN, softmax-attention) are perfect (1.0) all M. SUBSTRATE chain-grade-at-bound GATED on the '
          'calibration + learned-key follow-up'),
    description=(
        'The dense-projected-KV envelope drill (revival of the flagship sparse honest-negative), 3-arm x M-sweep '
        '{1k,3k,10k,30k,100k} x sigma{0,0.1,0.3} x d{768,1024} x 5-seed, fixed C=256 codebook decode (all arms). '
        'RESULT (verified off per_unit + cell code, landed-VET): ARM1 (M-INDEPENDENT superposition, W=sum code[y]k^T at '
        'O(d^2); decode argmax cosine over C=256 codebook -- M-indep, NOT argmax over M values) holds recall=0.8242 @ '
        'M=10k (=13xd, d=768), cv=0.0070 robust; curve {1k:1.0, 3k:1.0, 10k:0.824, 30k:0.286, 100k:0.065} -- crowds at '
        'alpha>13 per RMT AGS. The fixed C-codebook LIFTS recall +0.21 above the i.i.d. distinct-value Phi(1/sqrt(13))~0.61 '
        'prediction (capacity-extender; empirically confirms the info-theoretic/substrate-vocab insight that fixed-'
        'cardinality value-space enables M-indep recall). ARM0 exact-kNN + ARM2 softmax-attention (both O(M*d), beta=1/sqrt(d) '
        'theory-fixed) = 1.0 at ALL M -> dict-equivalent ceilings; ARM2 = the attention-retrieval rescue (storage-chain '
        'item #4 candidate) viable beyond the superposition bound but at O(M*d). MECHANISM/SCOPE: the substrate-vocab '
        'M-indep superposition store has a BOUNDED capacity (~13xd at recall>=0.80) -- a genuine memory-vs-recall Pareto '
        'point (O(d^2) storage, capped capacity), NOT M-independence at arbitrary scale. POSITIVE vs the flagship sparse '
        'L-build honest-negative (there NO arm held 0.80). TIER = MEASURED_MECHANISM (not yet a SUBSTRATE chain-grade): '
        '(1) FLAG-3 calibration HALT-gate UNRUN (this is random-keys-core; ARM0=1.0 is by-construction, NOT the pythia '
        'meter-check vs CERT591 0.827); (2) RANDOM keys = BEST-CASE upper bound -- the substrate uses LEARNED keys '
        '(<= this per HMM arXiv:2503.09518); learned-key subset pending. SUBSTRATE chain-grade-at-bound GATED on the GPU '
        'follow-up (calibration anchor + learned-key subset @M={3k,10k} on CERT591 pythia keys); on land -> re-VET -> '
        'upgrade THIS atom. Symmetric: a verified POSITIVE atomized as such (not a negative); not minted as a chain-grade '
        'on the upper-bound proxy (not inflation).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'HIGH','run_mode':'full','verdict':'MEASURED_MECHANISM_chain_grade_at_bound_gated',
              'metrics_path':'data/exp_dense_projected_KV_envelope_v1/metrics.json',
              'key_metrics':{'arm1_superpos_Mindep_at_M10k_d768_s0.1':0.8242,'arm1_cv_at_win':0.0070,
                             'arm1_curve_d768_s0.1':{'1k':1.0,'3k':0.9999,'10k':0.8242,'30k':0.2842,'100k':0.0646},
                             'arm0_knn_all_M':1.0,'arm2_softmax_all_M':1.0,'C_codebook':256,
                             'codebook_lift_above_phi':0.21,'phi_distinct_value_prediction_alpha13':0.61,
                             'bound_M_at_recall80':'~13xd (10k @ d=768)','keys':'random_iid_BEST_CASE_upper_bound',
                             'n_seeds':5,'beta':'1/sqrt(d)_theory_fixed','sigma0_clean_M10k':0.8227},
              'honest_scope':('M-indep superposition KV with fixed C=256-codebook decode holds value-CLASS recall>=0.80 up '
                              'to M~13xd (0.824@M=10k, d=768, cv=0.007) on BEST-CASE i.i.d. random keys; RMT-crowds beyond '
                              '(0.29@30k, 0.065@100k). C-codebook +0.21 lift above Phi. O(M*d) baselines (kNN/softmax) '
                              'perfect all M. This is the upper-bound PROXY, NOT the substrate: FLAG-3 calibration UNRUN + '
                              'learned keys (<= random per HMM) pending. SUBSTRATE chain-grade-at-bound GATED on the GPU '
                              'follow-up. A verified POSITIVE (vs the flagship sparse-negative); MM not chain-grade because '
                              'the substrate-grounding (calibration + learned keys) is not yet run.'),
              'composes_with':['T3/EXP_kv_learned_projection_v1','T3/EXP_flagship_sparse_projected_KV_LBUILD_v1',
                               'RULE_info_theoretic_floor_check_before_M_independence_claim',
                               'RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best'],
              'verified_off_data':('skunkworks L1 landed-VET independent recompute off per_unit (ARM1@10k=0.8242 cv=0.0070; '
                                   'curve; ARM0/ARM2=1.0 all M; sigma0=0.8227) + mechanism M-indep confirmed off cell code '
                                   '(W (d,d) O(d^2); C=256 decode not argmax-over-M; selftest asserts W.shape==(d,d)); '
                                   'Director 4-layer cross-check concurs on facts+scope (leans chain-grade-at-bound; I rule '
                                   'MM-gated on the 2 unmet pre-reg gates)'),
              'cert_vet_status':'LANDED_VET_skunkworks_2026-06-21_MEASURED_MECHANISM_substrate_chain_grade_at_bound_GATED',
              'chain_grade_gated_on':('GPU follow-up: (1) FLAG-3 calibration anchor (ARM0 exact-kNN on CERT591 pythia-2.8b '
                                      'proj256 keys @M=10k sigma=0 reproduces 0.827 mean/0.805 worst = meter-check); '
                                      '(2) learned-key subset (ARM1 superposition + ARM2 on pythia-projected keys @M={3k,10k} '
                                      '= substrate ACTUAL bound, <= random per HMM). If ARM1>=0.80 at some M w/ meter '
                                      'validated -> re-VET -> upgrade THIS atom to chain-grade-at-bound.'),
              'revival_routed':'Research/Exp-Dev GPU: calibration anchor + learned-key subset (the substrate-grounding of this best-case envelope)',
              'atomized_by':'skunkworks','atomized_date':'2026-06-21','era':'comprehensive_program_phase3_glassbox',
              'milestone':'storage-chain item #3 (dense-projected superposition KV): best-case M-indep capacity envelope VALIDATED-AT-BOUND (random keys); substrate chain-grade-at-bound gated on learned-key+calibration follow-up. C-codebook capacity-lift confirms the info-theoretic insight empirically.'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_dense_KV_envelope_MM_chain_grade_at_bound_gated_2026_06_21', note='dense-KV envelope MM (CERT-neutral); substrate chain-grade-at-bound gated on calibration+learned-key follow-up')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- dense-KV envelope MM atomized, CERT 583 UNCHANGED (CERT-neutral; chain-grade-at-bound gated)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
