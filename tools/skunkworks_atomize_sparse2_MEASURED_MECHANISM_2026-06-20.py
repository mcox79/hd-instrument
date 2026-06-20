"""Skunkworks 2026-06-20 -- atomize sparse-#2 (exp_sparse_boundary_v2_cpu_v1) as MEASURED_MECHANISM (CERT-NEUTRAL).
Values VERIFIED off the remote FULL data (scp + independent recompute off per_unit via
tools/skunkworks_sparse2_landed_vet_v1.py): every gain+cap reproduces, dense denom bounded (0.02),
seed-robust (cv=0), capped alpha_c == LOADS ceiling 6.0 (>=300x is a LOWER BOUND), monotone Willshaw
super-capacity, crosstalk-onset NOT located (partial deliverable => MEASURED_MECHANISM, not chain-grade).

1 atom: T3/EXP_sparse_boundary_v2_cpu_v1 (EXPERIMENT_RECORD, pq=MEASURED_MECHANISM).
A5 gates: PRE CERT=592 -> POST CERT=592 (UNCHANGED -- MEASURED_MECHANISM is CERT-neutral);
axiom 206 UNCHANGED (algebra=None); cap_pres 6/6; +1 atom; Store-loads. ASCII. Idempotent skip-if-exists.
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
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


SPARSE = Atom(
    id='T3/EXP_sparse_boundary_v2_cpu_v1',
    name=('Experiment record (MEASURED_MECHANISM, CERT-neutral): PLAIN k-of-N sparse-pattern auto-associative '
          'critical-load alpha_c(f) is MONOTONE-INCREASING as sparsity f decreases (Willshaw super-capacity): '
          '2.5x@f0.50 -> 20x@f0.10 -> 150x@f0.02 -> >=300x@f0.005 (LOWER BOUND, LOADS-capped) vs dense, at N=8192; '
          'crosstalk-onset boundary NOT located (alpha_c monotone-rising, 2 sparsest capped)'),
    description=(
        'Auto-associative critical load alpha_c(f) = max stored LOAD with single-step non-zero-position recall >=0.95, '
        'for PLAIN k-of-N sparse patterns (k = f*N active, raw Hebbian W = P.T@P zero-diag, single-step recall '
        'sign((s@P.T)@P - s*diag)). Swept f in {0.005,0.01,0.02,0.05,0.1,0.2,0.5,1.0}, N=8192, 3 seeds {7,17,23}, '
        'run_mode=full (elapsed ~3180s). RESULT: alpha_c RISES MONOTONICALLY as f falls -- the Willshaw sparse '
        'super-capacity regime -- gain vs the dense (f=1.0) baseline = 1.0x(dense) -> 2.5x@f0.5 -> 10x@f0.2 -> 20x@f0.1 '
        '-> 50x@f0.05 -> 150x@f0.02 -> >=300x@f0.01 -> >=300x@f0.005. VERIFIED OFF DATA (cert-owner scp-read remote + '
        'independent recompute off per_unit, tool skunkworks_sparse2_landed_vet_v1.py): (1) every gain reproduces as '
        'alpha_c(f)/dense_alpha_c; (2) the DENSE DENOMINATOR is BOUNDED (dense_alpha_c=0.02, a real recall-passing '
        'load, NOT divide-by-near-zero) -> the gain is genuine NUMERATOR-driven super-capacity; (3) SEED-ROBUST '
        '(worst per-f cv=0.000 across 3 seeds); (4) the two sparsest (f0.005, f0.01) are CAPPED (alpha_c hit the grid '
        'LOADS ceiling 6.0 with recall still >=0.95) -> their >=300x is a LOWER BOUND, not the true peak. '
        'INCOMPLETE/PARTIAL deliverable: the CROSSTALK-ONSET boundary was NOT located in [0.005,1.0] at LOADS<=6.0 '
        '(alpha_c monotone-rising with no peak/drop; the predicted Willshaw onset ~1/sqrt(N)~0.011 is MASKED by the '
        'f0.01 cap) -> the onset is below f0.005 OR beyond LOADS 6.0; a higher-LOADS/sparser follow-up would locate it '
        '(OPTIONAL, not a blocker for this characterization). The gain-MULTIPLE is N-DEPENDENT via the DENSE baseline '
        '(dense alpha_c falls 0.05@N2048 -> 0.02@N8192; sparse alpha_c is N-INDEPENDENT) -> state N in any claim. '
        'DISTINCT from the novelty-gated sparse-WRITE rule (exp_substrate_sparse_vs_dense, multi-step): the prior "1.4x" '
        'cited for sparse coding does NOT reproduce from that cell (its recall = 8x, identical to this) -> that was a '
        'MIS-CITE; this plain-sparse-pattern capacity is the genuine measure. TIER = MEASURED_MECHANISM (curve '
        'characterization + honest partial onset; CERT-neutral -- not a chain-grade lever ship).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'HIGH',
        'verdict': 'MEASURED_MECHANISM_monotone_willshaw_super_capacity_onset_NOT_located',
        'run_mode': 'full',
        'N': 8192, 'n_seeds': 3, 'seeds': [7, 17, 23], 'n_f': 8, 'LOADS_ceiling': 6.0,
        'fracs': [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        'metrics_path': 'data/exp_sparse_boundary_v2_cpu_v1/metrics.json (REMOTE-only; metrics-dir non-git)',
        'metrics_source': 'measured_cpu_sparse_capacity_vs_sparsity_fraction_boundary',
        'key_metrics': {
            'alpha_c_by_f': {'0.005': 6.0, '0.01': 6.0, '0.02': 3.0, '0.05': 1.0,
                             '0.1': 0.4, '0.2': 0.2, '0.5': 0.05, '1.0': 0.02},
            'gain_vs_dense_by_f': {'0.005': 300.0, '0.01': 300.0, '0.02': 150.0, '0.05': 50.0,
                                   '0.1': 20.0, '0.2': 10.0, '0.5': 2.5, '1.0': 1.0},
            'alpha_c_capped_by_f': {'0.005': True, '0.01': True, '0.02': False, '0.05': False,
                                    '0.1': False, '0.2': False, '0.5': False, '1.0': False},
            'dense_alpha_c': 0.02, 'peak_gain_lower_bound': 300.0, 'peak_f': 0.005,
            'worst_cv': 0.0, 'crosstalk_onset_f': None, 'n_capped': 2,
        },
        'honest_scope': ('Monotone Willshaw super-capacity for PLAIN k-of-N sparse patterns (raw P.T@P, single-step '
                         'non-zero recall): alpha_c(f) rises as f falls, >=300x@f0.005 vs dense at N=8192 (LOWER BOUND '
                         '-- 2 sparsest LOADS-capped). The crosstalk-ONSET boundary was NOT located (below f0.005 or '
                         'beyond LOADS 6.0) -- partial deliverable, optional higher-LOADS follow-up. Gain-multiple is '
                         'N-dependent via the dense baseline. NOT the novelty-gated sparse-WRITE rule (1.4x was a '
                         'mis-cite). MEASURED_MECHANISM, CERT-neutral.'),
        'finding': ('Sparser plain patterns are MONOTONICALLY safer to store: critical capacity grows >=300x (N=8192) '
                    'as the active fraction drops to f=0.005. Phase-1 sparse-coding input: "sparser is monotonically '
                    'safer to at least f0.005, >=300x". The exact safe-sparsity ONSET is below the swept range / above '
                    'the LOADS ceiling (not yet located).'),
        'baseline_provenance': ('dense (f=1.0) alpha_c=0.02 measured in the SAME cell/run (same W=P.T@P, same recall '
                                'metric, same seeds) -- bounded, not assumed; the gain denominator is a real '
                                'recall-passing load.'),
        'composes_with': ['T3/EXP_crosstalk_capacity_law_v1', 'T3/EXP_kmax_ness_envelope_corrected_v1',
                          'T3/EXP_hebbian_capacity_projected_v2'],
        'depends_on_text': ('plain k-of-N sparse patterns + raw Hebbian W=P.T@P + single-step non-zero recall '
                            '(substrate auto-assoc primitive); recorded in metadata (phantom-safe, no sub-cert edges).'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-20_MEASURED_MECHANISM_file_as_is_all_gates_pass',
        'verified_off_data': ('cert-owner scp-read remote FULL metrics.json + independent recompute off per_unit '
                              '(tool skunkworks_sparse2_landed_vet_v1.py): all gates PASS -- every gain+cap reproduces, '
                              'dense denom bounded (0.02), cv=0, capped==LOADS ceiling 6.0 (>=300x lower-bound), '
                              'monotone, onset None. 1.4x mis-cite resolved (matched-config recalls identical).'),
        'incomplete_deliverable': ('crosstalk-onset boundary NOT located (alpha_c monotone-rising, f0.005+f0.01 capped); '
                                   'optional higher-LOADS (>6.0) / sparser (<0.005) follow-up to locate the onset.'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
        'milestone': 'sparse super-capacity characterized off-data (the 6x/25x sweep-endpoint phantom + 1.4x mis-cite resolved -> genuine monotone Willshaw >=300x lower-bound)',
    })


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    if pre_cert != 592:
        print(f"PRE-GATE WARN: CERT={pre_cert} (expected 592). Investigate before write."); return 1
    existed_before = ps.get_atom(SPARSE.qualified_id) is not None
    if existed_before:
        print(f"  SKIP exists: {SPARSE.id}")
    else:
        ps.add_atom(SPARSE, source='skunkworks_sparse2_MEASURED_MECHANISM_2026_06_20',
                    note='sparse-#2 monotone Willshaw super-capacity >=300x lower-bound (MEASURED_MECHANISM, CERT-neutral)')
        print(f"  ADD: {SPARSE.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom(SPARSE.qualified_id) is not None
    bad_alg = landed and ps2.get_atom(SPARSE.qualified_id).algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 592 UNCHANGED) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert == 592 and post_ax == 206 and post_mod and landed and not bad_alg
            and post_atoms == pre_atoms + (0 if existed_before else 1))
    print("GATE:", "OK -- MEASURED_MECHANISM filed, CERT 592 unchanged (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
