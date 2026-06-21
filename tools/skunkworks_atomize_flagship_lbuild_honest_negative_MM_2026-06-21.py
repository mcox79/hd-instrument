"""Skunkworks 2026-06-21 -- landed-VET atomize the flagship sparse-projected-KV L-BUILD = MEASURED_MECHANISM HONEST-NEGATIVE
(CERT-NEUTRAL). 4-layer-confirmed (L1 me off per_unit + L3 Orchestrator + L4 Research cross-check). Verified off per_unit:
capacity_M(recall>=0.80)=0 for ALL 5 arms (A_naive/B_shrinkage/raw/dense/analytic); best=A_naive maxrec=0.536 DROPPING with
M (0.536@1k->0.333@10k->0.14@100k = crowding); seed-unstable worst_cv=0.707; bf16 RESOLVED by my C2 (float32_dense=0.828
vs bf16=0.961 -> bf16 does NOT depress -> shortfall GENUINE). The flagship's premise (sparse stores more AT recall>=0.80)
FAILS: sparsification degrades recall below 0.80 + no arm robustly hits 0.80 across the M-sweep (seed-unstable). NOT
chain-grade (MIDDLE_BAND, unstable -> MEASURED_MECHANISM honest-negative, not a clean stable proven-negative). My rigorous
conditions (recall>=0.80-genuine + bf16-sanity + A/B capacity-scan) produced this HONEST verdict (not a forced/confounded pass).
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
    id='T3/EXP_flagship_sparse_projected_KV_LBUILD_v1',
    name=('Experiment record (MEASURED_MECHANISM, HONEST-NEGATIVE): the flagship sparse-projected-KV does NOT hold '
          'recall>=0.80 at scale -- sparsification degrades recall (best A_naive maxrec=0.536, dropping with M) + no arm '
          '(incl dense) robustly reaches 0.80 across the M-sweep (seed-unstable cv=0.707); bf16 NOT the cause. The '
          'capacity-via-sparsification premise FAILS'),
    description=(
        'The flagship sparse-projected-KV storage capability, rigorously built+tested at scale (pythia-2.8b, N=8192, '
        '5 arms [A_naive/B_shrinkage-whiten/raw/dense/analytic] x M-sweep {1k,10k,100k} x 3-seed + float32 control). '
        'RESULT (verified off per_unit, 4-layer L1-me/L3-Orch/L4-Research): capacity_M(recall>=0.80)=0 for ALL 5 arms; '
        'best=A_naive maxrec=0.536 DROPPING with M (0.536@1k -> 0.333@10k -> 0.14@100k = crowding); B_shrinkage worse '
        '(consistent with the probe A>B); seed-unstable worst_cv=0.707. bf16-confound RESOLVED by C2 (float32_dense=0.8281 '
        'vs bf16_dense=0.961 -> bf16 does NOT depress -> the shortfall is GENUINE, not the OOM-fix artifact). HONEST-NEGATIVE: '
        'the flagship premise (sparse-projected stores MORE facts AT recall>=0.80, the Willshaw super-capacity translated to '
        'KV) FAILS -- sparsification degrades recall below 0.80 (super-capacity is more PATTERNS but not at usable recall), '
        'and no arm (incl dense-projected) robustly hits 0.80 across the M-sweep (seed-unstable). The probe HARD_PASS was '
        'gate-trivial (raw bar 0.006); the L-build is the real verdict = MIDDLE_BAND. NOTE: the C2 single-config float32_dense '
        '=0.828 shows DENSE-projected CAN hit 0.80 at a favorable config -- so dense-projected-KV (CERT 591, no sparsify) is '
        'the candidate real storage capability; the SPARSE capacity-boost does not hold recall. MEASURED_MECHANISM (not a '
        'clean stable proven-negative -- the cv=0.707 instability -> MIDDLE_BAND honest-negative). My rigorous conditions '
        '(recall>=0.80-genuine + bf16-sanity + A/B-capacity-scan) produced this HONEST verdict, not a forced/confounded pass.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'HIGH','run_mode':'full','verdict':'MIDDLE_BAND_honest_negative',
              'metrics_path':'data/exp_flagship_sparse_projected_KV_LBUILD_v1/metrics.json',
              'key_metrics':{'capacity_M_rec80_all_arms':0,'best_arm':'A_naive','best_maxrec':0.536,
                             'A_naive_recall_by_M':{'1k':0.536,'10k':0.333,'100k':0.1425},'worst_cv':0.7071,
                             'C2_float32_dense':0.8281,'C2_bf16_dense':0.961,'bf16_depresses':False,'n_seeds':3,'n_arms':5},
              'honest_scope':('Flagship sparse-projected-KV does NOT hold recall>=0.80 at scale: sparse arms degrade '
                              '(A_naive maxrec 0.536, dropping with M = crowding; B worse), no arm (incl dense) robustly hits '
                              '0.80 across the M-sweep (seed-unstable cv=0.707). bf16 NOT the cause (C2 float32_dense=0.828). '
                              'Capacity-via-sparsification premise FAILS (more patterns, not at usable recall). Dense-projected '
                              '(CERT591, C2 0.828 single-config) is the candidate real capability. MIDDLE_BAND honest-negative '
                              '(unstable -> MEASURED_MECHANISM, not a clean proven-negative). Revival routed to Research.'),
              'composes_with':['T3/EXP_kv_learned_projection_v1','T3/EXP_sparse_boundary_v2_cpu_v1','T3/EXP_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1'],
              'verified_off_data':'skunkworks L1 landed-VET independent recompute off per_unit (capacity_M=0 all arms; A recall-by-M 0.536/0.333/0.14; cv 0.707; bf16-resolved-by-C2); L3 Orchestrator + L4 Research cross-check concur MIDDLE_BAND honest-negative',
              'cert_vet_status':'LANDED_VET_skunkworks_2026-06-21_MIDDLE_BAND_honest_negative_4layer_confirmed',
              'atomized_by':'skunkworks','atomized_date':'2026-06-21','era':'comprehensive_program_phase3_glassbox',
              'revival_routed':'Research: why sparsification costs recall; is there a recall-holding sparse-encode; is dense-projected-KV the stable storage capability; is cv=0.707 a limit or config/seed artifact',
              'milestone':'flagship saga end: GREEN-misjudge(mine)->RED-overcall(ExpDev)->reconcile->whiten-before-topk->probe HARD_PASS-mechanism-but-A>B->L-build HONEST-NEGATIVE. Capacity-via-sparsification premise failed rigorously+honestly. My conditions produced the honest verdict.'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_flagship_lbuild_honest_negative_MM_2026_06_21', note='flagship L-build MM honest-negative (CERT-neutral, 4-layer-confirmed)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- flagship L-build MM honest-negative atomized, CERT 583 UNCHANGED" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
