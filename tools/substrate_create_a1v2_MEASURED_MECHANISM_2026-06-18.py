"""Scoped single-atom creation: A1-v2 ratio-profile as MEASURED_MECHANISM (Skunkworks verdict-VET disposition 2026-06-18).

Skunkworks verdict-VET: GATE-0 PASS + C2 gate0_self_check first-dogfood CLEAN, BUT CERT-CATCH (referent mismatch) ->
A1-v2 does NOT localize the canonical measured-8a non-monotonicity (different net_speedup implementation [~9x value gap],
T-range below the 8a break-even 65536, missed the k4-saturated regime). So localization REMAINS OPEN -- atomize with the
HONEST "OPEN, different-referent" scope, NOT "closed." measured-8a HARD_FAIL STANDS.

Scoped single-atom create (NOT the corpus-wide atomizer -- no-wholesale-recompute discipline; mirrors the A1 attribution
atom T3/EXP_a1_8a_4channel_attribution_v1). pq=MEASURED_MECHANISM (the C2 tier; measured ATTRIBUTION, NOT cert-counted).
ASCII-only. No LLM. Laptop-safe.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_a1v2_ratio_profile_v1'
A1_ID = 'math::T3/EXP_a1_8a_4channel_attribution_v1'
M8A_ID = 'math::T3/EXP_active_gating_8a_break_even_v1_measured'

# Skunkworks verdict-VET CORRECTED scope (verbatim).
CORRECTED_SCOPE = (
    "A1-v2's own net_speedup (dense-all-experts/topk) is MONOTONE in T=512-32768 (noise-guarded). This does NOT "
    "localize the canonical measured-8a non-monotonicity: A1-v2's net_speedup is a DIFFERENT measurement (~9x value "
    "gap at matched T,k -> different implementation), its T-range does not reach the 8a break-even (65536), and the "
    "8a non-monotonicity is k4-saturated-specific. The measured-8a net_speedup non-monotonicity localization REMAINS "
    "OPEN. Future drill: a ratio-profiler matching the measured-8a implementation + T-range (down to 64, up to "
    ">=65536) + the k4-saturated regime."
)

DESCRIPTION = (
    "MEASURED_MECHANISM (verdict ATTRIBUTION; NOT cert-counted): A1-v2 net_speedup ratio-profiler (dense-all-experts "
    "vs topk). " + CORRECTED_SCOPE
)

# queryable attribution findings (all-scalar; mirrors the A3/A1 queryability pattern)
ATTR_FINDINGS = {
    "a1v2_own_net_speedup": "MONOTONE_in_T_512_32768_noise_guarded_dense_all_experts_over_topk",
    "localization_of_measured_8a": "OPEN_different_referent_NOT_closed",
    "referent_mismatch_1_implementation": "9x_value_gap_at_matched_T1024_k1_measured_8a_0.054_vs_a1v2_0.495",
    "referent_mismatch_2_t_range": "a1v2_max_T_32768_below_measured_8a_break_even_65536",
    "referent_mismatch_3_regime": "measured_8a_nonmonotonicity_is_k4_saturated_specific_break_even_4096_a1v2_missed_it",
    "measured_8a_hard_fail": "STANDS_k4_saturated_nonmonotonicity_real_in_own_measurement_NOT_noise",
    "future_drill": "a1v3_ratio_profiler_match_8a_implementation_T_64_to_ge_65536_k4_saturated_regime",
    "gate0_self_check": "PASS_first_C2_producer_gate_dogfood_clean_21_of_21_full_measured_torch_gpu",
}


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


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_atom() -> Atom:
    metadata = {
        'record_class': 'measured_mechanism',
        'verdict': 'ATTRIBUTION',
        'provenance_quality': 'MEASURED_MECHANISM',   # C2 tier; measured but NOT cert-counted
        'relevance_tier': 'ARCHIVE',
        'run_mode': 'full',
        'metrics_source': 'measured_torch_gpu',
        'metrics_path': 'data/exp_a1v2_ratio_profile_v1/metrics.json',
        'experiment_path': 'experiments/exp_substrate_a1v2_ratio_profile_v1.py',
        'cell_commit': 'd78ffe8a',
        'n_cells': 21,
        'elapsed_s': 15.03,
        'gate0_self_check_pass': True,
        'attribution_findings': ATTR_FINDINGS,
        'localization_status': 'OPEN_different_referent',
        'measured_8a_hard_fail_stands': True,
        'bears_on': 'T3/EXP_a1_8a_4channel_attribution_v1 (A1; A1-v2 does NOT close its OPEN localization -- different referent) '
                    '+ T3/EXP_active_gating_8a_break_even_v1_measured (measured-8a HARD_FAIL; localization REMAINS OPEN)',
        'verdict_vet_by': 'skunkworks',
        'verdict_vet_date': '2026-06-18',
        'verdict_vet_note': 'GATE-0 PASS + C2 gate0_self_check first-dogfood CLEAN; CERT-CATCH referent-mismatch -> localization OPEN not closed',
        'referent_mismatch_witness': 'composes_with_anchor_mechanism_match_83 (attribution cell must match verdict referent: metric+implementation+regime)',
        'eleventh_rule_clean': True,
        'deterministic_no_llm': True,
        'source': 'a1v2_verdict_vet_skunkworks_disposition_measured_mechanism_localization_open',
    }
    return Atom(
        id=ATOM_ID,
        name='Measured mechanism (MEASURED_MECHANISM): A1-v2 net_speedup ratio-profiler (localization OPEN, different referent)',
        description=DESCRIPTION,
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata=metadata,
    )


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(mod6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halting; no mutation.')
        return 1

    # verify bears_on targets resolve (0-phantom)
    if ps.get_atom(A1_ID) is None or ps.get_atom(M8A_ID) is None:
        print(f'PHANTOM: bears_on target missing (A1={ps.get_atom(A1_ID) is not None}, 8a={ps.get_atom(M8A_ID) is not None}). Halt.')
        return 4

    atom = build_atom()
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID} already present.')
        return 0

    ps.add_atom(atom, source='a1v2_measured_mechanism', note='A1-v2 verdict-VET disposition; localization OPEN; bears_on A1+8a')
    # bears_on edges (role semantics on source-atom metadata too, since Store drops edge metadata)
    ps.add_relation(f'math::{ATOM_ID}', RelationType.RELATES, A1_ID, source='a1v2_bears_on',
                    note='bears_on A1 (does NOT close its OPEN localization -- different referent)')
    ps.add_relation(f'math::{ATOM_ID}', RelationType.RELATES, M8A_ID, source='a1v2_bears_on',
                    note='bears_on measured-8a (localization REMAINS OPEN; HARD_FAIL stands)')

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    rb = ps.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'MEASURED_MECHANISM'
             and rb.metadata.get('localization_status') == 'OPEN_different_referent')
    gate_ok = (post_axiom == 206) and post_mod and (post_n == pre_n + 1) and rb_ok
    print(f'POST: atoms={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  read-back_ok={rb_ok}')
    print(f'  pq={rb.metadata.get("provenance_quality")}  verdict={rb.metadata.get("verdict")}  localization={rb.metadata.get("localization_status")}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail')
        return 2
    print('=' * 72)
    print(f'A1-v2 MEASURED_MECHANISM landed: math::{ATOM_ID}  (localization OPEN; bears_on A1+8a; axiom_term 206; cap_pres 6/6)')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
