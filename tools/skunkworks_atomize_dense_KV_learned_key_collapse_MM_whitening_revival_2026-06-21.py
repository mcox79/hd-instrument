"""Skunkworks 2026-06-21 -- landed-VET atomize the dense-KV learned-key + calibration follow-up = MEASURED_MECHANISM
(CERT-NEUTRAL). Verified off per_unit: GATE-2 ARM1 superposition on REAL learned pythia-2.8b-projected keys COLLAPSES to
near-CHANCE (0.015@M=3k, 0.008@M=10k; 1/C=256=0.0039) vs random-core 1.0@3k/0.824@10k; ARM2 softmax-attention HOLDS
(0.9995/0.997). GATE-1 cal=0.4107 (meter NOT yet formally validated -- the protocol-fix [HELDOUT_FRAC 0.25->2500 cands,
train 7500] is not in this run; clean re-run pending) BUT the projection demonstrably WORKS (GATE-1 0.41 >> chance 1e-4 for
10k-way retrieval + ARM2 0.997) -> ARM1's collapse is NOT under-training, it is the LINEAR-SUPERPOSITION readout failing on
ANISOTROPIC keys (common-mode: r ~ c*sum(all codes) swamps the per-key signal; softmax survives via normalize+contrast).
TIER: dense-KV does NOT upgrade to chain-grade-at-bound (vindicates the MM-gated landed-VET inflation-backstop); the random-
core 0.824 was best-case-isotropic-keys only. NOT a final negative: the collapse is FIXABLE by isotropization (mean-center/
shrinkage-ZCA-whiten) -- random-core isotropic success + flagship whiten-before-topk = existence proof -> WHITENING REVIVAL
routed (does ARM1 recover >=0.80 on WHITENED learned keys?). Item #4 attention (ARM2, O(M*d) dict-equivalent) is the working
real-key retrieval; item #3 M-indep store gated on the whitening-revival.
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
    id='T3/EXP_dense_KV_learned_key_calibration_v1',
    name=('Experiment record (MEASURED_MECHANISM): the M-INDEPENDENT superposition KV store COLLAPSES to near-chance on '
          'REAL anisotropic learned pythia-2.8b keys (0.015@M=3k, 0.008@M=10k vs random-core 1.0/0.824) -- the projection '
          'works (GATE-1 0.41>>chance, ARM2 softmax 0.997 holds) so it is the LINEAR-SUPERPOSITION readout failing on '
          'anisotropy (common-mode), NOT under-training. Dense-KV does NOT upgrade to chain-grade-at-bound. NOT a final '
          'negative -> whitening/isotropization revival routed'),
    description=(
        'The dense-KV learned-key + calibration GPU follow-up (the gate to upgrade the random-core MM to SUBSTRATE chain-'
        'grade-at-bound), pythia-2.8b fp16 proj256 3-seed. RESULT (verified off per_unit, landed-VET): GATE-2 ARM1 '
        'superposition (M-indep O(d^2), C=256 codebook decode) on REAL learned pythia-projected keys = 0.015 @M=3k, 0.008 '
        '@M=10k = near-CHANCE (1/256=0.0039) -- COLLAPSE from the random-core best-case (1.0@3k / 0.824@10k). ARM2 softmax-'
        'attention HOLDS (1.0/0.9955). MECHANISM (verified, not under-training): the projection WORKS -- GATE-1 cue->key '
        'recall 0.604 >> chance (1/2500=4e-4 for the 2500-way retrieval, CLEAN train-7500 run) AND ARM2 0.9955 -- so the keys '
        'are good for retrieval; only the LINEAR superposition readout collapses. CONFOUND-FREE: the collapse REPRODUCES on '
        'the clean train-7500 run (rules out the train-size confound -- full training, ARM1 still ~chance). Anisotropic '
        'pythia keys -> high common-mode (cue.k_j ~ '
        'c for all j) -> r = W.cue ~ c*(sum_j code[y_j]) + signal -> the common-mode sum-of-all-codes SWAMPS the per-key '
        'signal -> chance decode. ARM2 softmax survives (normalize + exponential-contrast removes the common-mode). '
        'TIER: dense-KV (T3/EXP_dense_projected_KV_envelope_v1) does NOT upgrade to chain-grade-at-bound -- the random-core '
        '0.824 was BEST-CASE isotropic-random-keys only; M-indep superposition does NOT transfer to real anisotropic keys. '
        'This vindicates the MM-gated landed-VET (inflation-backstop: a chain-grade minted on the random-core would have '
        'been inflation). NOT A FINAL NEGATIVE: the collapse is anisotropy-induced common-mode, which is FIXABLE by '
        'ISOTROPIZATION (mean-center / shrinkage-ZCA-whiten the learned keys) -- the random-core isotropic success (0.824) + '
        'the flagship whiten-before-topk shrinkage-ZCA (in-codebase) are the existence proof -> WHITENING REVIVAL routed '
        '(does ARM1 superposition recover >=0.80 on WHITENED learned keys?). GATE-1 meter NOT formally validated: the param-'
        'fix (2500 cands, train 7500) moved cal 0.411->0.604 (confirming the candidate-pool diagnosis) but a ~0.22 residual '
        'gap to CERT591 0.827 remains (a SEPARATE CERT591-setup puzzle -- proj_dim/train_steps/fresh-vs-saved-weights/data; '
        'routed as a cheap CODE-DIFF diagnosis, NOT more GPU). The collapse finding STANDS regardless (projection works '
        '0.604>>chance; collapse is pool-independent + the 256-codebook decode is selftest-validated; ACCEPT-GATE2 endorsed '
        'by Orchestrator + Research). STORAGE: item #4 attention-'
        'over-learned-keys (ARM2, O(M*d) dict-equivalent) is the working real-key retrieval (Phase-3 candidate); item #3 '
        'M-indep store is GATED on the whitening-revival (not abandoned).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'HIGH','run_mode':'full','verdict':'MEASURED_MECHANISM_learned_key_collapse_no_upgrade',
              'metrics_path':'data/exp_dense_KV_envelope_learned_key_calibration_v1_gpu/metrics.json',
              'key_metrics':{'arm1_superpos_learned_M3k':0.0205,'arm1_superpos_learned_M10k':0.008,'chance_1_over_C':0.0039,
                             'arm2_softmax_learned_M3k':1.0,'arm2_softmax_learned_M10k':0.9955,
                             'random_core_arm1_M3k':1.0,'random_core_arm1_M10k':0.824,
                             'gate1_cal_clean_train7500':0.604,'gate1_cal_first_train4000':0.4107,'gate1_meter_valid':False,
                             'train_7500_confound_free':True,'collapse_robust_to_full_training':True,
                             'collapse':'ARM1 1.0->0.02 random->learned at M=3k (near-total, anisotropy common-mode); reproduces on train-7500 confound-free run',
                             'projection_works':'GATE1 cal 0.604>>chance(1/2500=4e-4) + ARM2 0.996 -> NOT under-training','n_seeds':3},
              'honest_scope':('M-indep superposition KV COLLAPSES to near-chance on REAL anisotropic learned pythia keys '
                              '(0.02@3k/0.008@10k vs random-core 1.0/0.824), reproduced on the CLEAN train-7500 run '
                              '(confound-free); the projection works (GATE-1 cal 0.604>>chance, ARM2 0.9955) so it is the '
                              'linear-superposition readout failing on anisotropy (common-mode), not under-training. Dense-KV '
                              'does NOT upgrade to chain-grade-at-bound (random-core was best-case-isotropic only). NOT final: '
                              'FIXABLE by isotropization (mean-center/shrinkage-ZCA) -> whitening revival routed (CPU PoC '
                              'CONFIRMS recovery). GATE-1 meter NOT formally validated (cal 0.604, ~0.22 residual gap to 0.827 '
                              '= separate code-diff puzzle, ACCEPT-GATE2 per Orch+Research; collapse pool-independent stands). '
                              'Item #4 attention holds 0.9955 (O(M*d) dict-equivalent).'),
              'composes_with':['T3/EXP_dense_projected_KV_envelope_v1','T3/EXP_kv_learned_projection_v1',
                               'T3/EXP_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1',
                               'RULE_info_theoretic_floor_check_before_M_independence_claim',
                               'RULE_metric_referent_carries_implicit_eval_protocol_match_it_to_reproduce'],
              'verified_off_data':('skunkworks L1 re-VET independent recompute off per_unit -- BOTH runs: first train-4000 '
                                   '(ARM1 0.015/0.008) + CLEAN train-7500 confound-free (ARM1 0.0205/0.008=chance, ARM2 '
                                   '1.0/0.9955, cal 0.604); mechanism verified (projection works via cal 0.604>>chance + ARM2 '
                                   '0.9955 -> linear-superposition common-mode collapse, NOT under-training -- collapse robust '
                                   'to full training); the whitening fix CONFIRMED on a CPU PoC (isotropic 0.807 / anisotropic '
                                   '0.004 / mean-center 0.806 + ZCA 0.843 recover); Exp-Dev + Orchestrator + Director 4-layer '
                                   'cross-check concur ACCEPT-GATE2 (collapse pool-independent, robust)'),
              'cert_vet_status':'RE_VET_skunkworks_2026-06-21_MM_no_upgrade_whitening_revival_routed',
              'revival_routed':('WHITENING REVIVAL -> Research/Exp-Dev: shrinkage-ZCA-whiten (or mean-center) the learned '
                                'pythia-projected keys -> ARM1 superposition + C-codebook @M={3k,10k} -> recover >=0.80? '
                                '(existence proof: random-core isotropic 0.824 + flagship whiten-before-topk in-codebase). '
                                'If recovers -> item #3 M-indep store VIABLE on real keys WITH isotropization (chain-grade-'
                                'at-bound candidate; CPU PoC pre-confirms recovery); if not -> THEN item #3 is the honest '
                                'negative. SEPARATE: GATE-1-repro-gap (cal 0.604 not 0.827 at protocol-match) = a cheap '
                                'CODE-DIFF diagnosis (proj_dim/train_steps/fresh-vs-saved-weights/data vs CERT591), NOT more '
                                'GPU -- matters for the whitening cell projection quality.'),
              'atomized_by':'skunkworks','atomized_date':'2026-06-21','era':'comprehensive_program_phase3_glassbox',
              'milestone':('storage-chain item #3 substrate-grounding: M-indep superposition does NOT transfer from best-'
                           'case random keys to real anisotropic learned keys (common-mode collapse) -> dense-KV stays MM; '
                           'NOT abandoned (whitening-revival routed). Item #4 attention (O(M*d)) is the working real-key '
                           'retrieval. Vindicates the MM-gated inflation-backstop.')})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_dense_KV_learned_key_collapse_MM_whitening_revival_2026_06_21', note='dense-KV learned-key collapse MM (CERT-neutral); no upgrade; whitening-revival routed')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- dense-KV learned-key collapse MM atomized, CERT 583 UNCHANGED (no upgrade; whitening-revival routed)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
