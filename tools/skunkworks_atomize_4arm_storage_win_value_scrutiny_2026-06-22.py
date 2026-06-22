"""Atomize the META discipline from the Path D 4-arm storage-win VALUE scrutiny + write
the cert_relabel ledger row superseding the prior phase_c_5_backfill honest_negative.

DISCOVERY (off the data + cell source):
  1. ARM B retrieval mode = SINGLE-PROBE EXACT-TAG over FULL M-tag-table. NOT multi-probe.
     `arm_B = (y[np.argmax(Qt @ Kt.T, axis=1)] == ytrue).mean()` -- one binary matmul
     against ALL M stored tags, argmax. No full-key re-rank.
  2. Compute per query = O(M * dp) = O(M * 5d) BINARY ops = 5x MORE ops than attention's
     O(M*d) FLOAT ops (but binary, so practically cheaper per op).
  3. Storage per memory (sparse-tag-indices) = 20 * log2(3840) = 238.1 bits/mem,
     vs attention dense f32 key = 768 * 32 = 24576 bits/mem = ~103x compression.
     This IS a real storage compression (NOT the synthetic 31 B/mem -- that was from
     a different CPU PoC config -- but ~100x vs dense float keys is genuine).
  4. NO sigma_query sweep -- SIGMA=0.1 is a constant. Noise-robustness AT ALL OTHER LEVELS
     is UNTESTED by this cell. My prior synthetic showed brittleness at sig=0.3 on
     low-eff-rank keys; this is NOT verified on real keys.
  5. LOCAL DATA IS SMOKE-ONLY (pythia-160m, 1 seed, M={400,1000}). The Orchestrator-
     reported 0.998 + 1.000 + 5-seed pythia-2.8b numbers from the full GPU run are
     REPORTS WITHOUT LOCAL DATA BACKING -- verify-the-referent fails for the 0.998 itself.

NET DISPOSITION:
  - The recall-rescue is class-level genuine (already MM-class-ratified pre-handoff).
  - The storage-win VALUE is CONDITIONAL: at single-probe exact-tag (this cell's mode)
    + sig=0.1 fixed, ARM B achieves recall-rescue at ~103x storage compression. BUT:
    (a) the storage-win is at O(M*dp) compute = 5x more than attention's O(M*d) -- so
        storage compression is real, compute is not the win;
    (b) the storage-win is at a single fixed sigma -- noise-robustness untested at
        higher sigma where prior synthetic showed brittleness;
    (c) the cited 0.998 itself is not locally verifiable (smoke only locally).

  Net: the storage-win exists at the scope tested (single-probe exact-tag, single sigma,
  smoke-only locally), but Director's CONVERGE framing "storage win confirmed" overclaims
  in 3 ways: (i) the win is COMPUTE-trades-for-STORAGE (not free), (ii) the win is
  fixed-sigma-only (not noise-robust), (iii) the headline number (0.998) is not locally
  verified (smoke shows 0.612 + B'=0.982 specific-WTA-not-load-bearing).

ACTIONS:
  1. Atomize a META discipline: storage-vs-compute-decomposition-required-for-storage-win-claims.
  2. Write a cert_relabel ledger row superseding 1e1302ff6293598f, refining cert_status
     from honest_negative (the phase_c_5 backfill default) to the more precise reading:
     measured_mechanism at recall-CLASS level + open-loop-on-storage-win-VALUE (this
     scrutiny's resolution). Net cert_increment_delta = 0 (CERT-neutral).

DOES NOT:
  - Re-rule the cell's verdict_msg (MIDDLE_BAND stands).
  - Touch the CERT N headline (CERT 584 unchanged; the prior 1e1302ff was already delta=0).
  - Retract Director's CONVERGE note (file separate routing note flagging needed-refinement).

A5 gate: PRE CERT==584 axiom==206 cap_pres==6/6 atoms==177267 -> add 1 META atom + 1
ledger row -> POST CERT==584 axiom==206 cap_pres==6/6 atoms==177268.
"""
from __future__ import annotations
import sys, os, json, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore, Atom
from backend.substrate_index.schema import Corpus, Tier, AtomKind
from tools.cert_ledger_writer import append_cert_ledger_row, row_hash, _read_ledger, LEDGER_PATH


def _cert_count(store):
    return sum(1 for a in store.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def _axiom_count(store):
    return sum(
        1 for a in store.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def _cap_pres_ok():
    import importlib
    return all(
        hasattr(importlib.import_module(m), s) for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


META_ATOM_ID = 'AUDIT_storage_win_claims_require_compute_and_noise_decomposition'
META_ATOM_NAME = 'Storage-win claims require compute + noise decomposition'

META_DESCRIPTION = (
    'When claiming a substrate retrieval mechanism achieves a "storage win" over '
    'attention (or any baseline), the claim must be decomposed across THREE dimensions, '
    'not just bits-per-memory: (1) storage cost per memory (the headline; in bits or '
    'bytes); (2) compute cost per query (O(...) ops); (3) noise-robustness range (the '
    'sigma_query interval over which the recall holds). A storage-win can be "real" on '
    'dimension (1) yet "lost" on (2) (e.g., 5x more compute per query) or "conditional" '
    'on (3) (e.g., only at sigma=0.1 with no sweep). The cited 4-arm fly-LSH ARM B '
    'rescue is the canonical case: ~103x storage compression vs dense-float-key '
    'attention IS genuine at single-probe exact-tag, BUT (a) retrieval compute is O(M*5d) '
    'binary = 5x MORE ops than attention O(M*d) float (binary-cheaper-per-op offsets '
    'partially), and (b) the cell tests ONE fixed sigma=0.1; prior synthetic showed '
    'noise-brittleness at sigma=0.3 on low-eff-rank keys, so the noise-robustness range '
    'of the storage-win is UNVERIFIED. Discipline: any "storage win" claim must surface '
    'compute (O-class + measured), storage (B/mem measured), AND noise-range (tested '
    'sigma interval) -- if any of the three is missing or contradicts, the claim is '
    'over-stated. Composes with cited-number-must-reproduce-from-cell and '
    'tag-CLASS-not-mechanism-specificity.'
)


def main():
    ts_now = float(time.time())

    print('=' * 72)
    print('Skunkworks Path-D 4-arm storage-win VALUE scrutiny -- atomize META + relabel')
    print('=' * 72)

    # ----- A5 PRE -----
    ps = PartitionedStore(REPO / 'data' / 'substrate_index')
    pre_cert = _cert_count(ps)
    pre_ax = _axiom_count(ps)
    pre_cap = _cap_pres_ok()
    pre_n = sum(1 for _ in ps.all_atoms())
    print(f'\n[A5 PRE] CERT={pre_cert} axiom={pre_ax} cap_pres={"6/6" if pre_cap else "FAIL"} atoms={pre_n}')
    assert pre_cert == 584, f'A5-PRE CERT mismatch: {pre_cert} != 584'
    assert pre_ax == 206, f'A5-PRE axiom drift: {pre_ax} != 206'
    assert pre_cap, 'A5-PRE cap_pres FAIL'

    # ----- Build the META discipline atom -----
    meta_atom = Atom(
        id=META_ATOM_ID,
        name=META_ATOM_NAME,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        description=META_DESCRIPTION,
        kind=AtomKind.AUDIT_LESSON,
        aliases=(
            'storage_win_requires_compute_and_noise_decomposition',
            'three_dim_storage_win_decomposition',
            'storage_compute_noise_decomposition_for_substrate_storage_claims',
        ),
        algebra=None,  # META discipline; algebra=None canonical for AUDIT_LESSON
        metadata={
            'provenance_quality': None,  # META atoms are NOT CERT_CHAIN_GRADE (CERT-neutral)
            'atom_kind': 'discipline_meta',
            'atomized_by': 'skunkworks_path_d_4arm_storage_win_scrutiny',
            'atomized_ts': ts_now,
            'instance_number': 1,
            'confirmed_or_candidate': 'CONFIRMED',
            'first_witness': 'exp_anisotropy_rescue_4arm_sweep_v1_gpu_director_converge_overclaim_2026_06_21',
            'lesson_class': 'storage_win_three_dimensional_decomposition_required',
            'rule_class': 'cert_audit_discipline',
            'composes_with': [
                'cited_number_must_reproduce_from_cell',
                'tag_CLASS_not_mechanism_specificity',
                'synthetic_to_real_deflation',
                'verify_the_referent_arrives',
            ],
            'memory_references': [
                'feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17',
            ],
            'witness_summaries': [
                {
                    'tag': 'fly_lsh_arm_b_storage_win_overclaim_2026_06_21',
                    'date': '2026-06-21_to_2026-06-22',
                    'caught_by': 'skunkworks_path_d_scrutiny',
                    'summary': (
                        "Director's CONVERGE note (2026-06-21T20:0xZ) wrote 'storage win confirmed on both' "
                        "for fly-LSH ARM B at 0.998 recall vs raw 0.013. Code-trace of "
                        "exp_anisotropy_rescue_4arm_sweep_v1_gpu.py revealed: (1) ARM B retrieval = "
                        "single-probe exact-tag over FULL M-tag-table at O(M*dp) compute = 5x more than "
                        "attention's O(M*d) (storage-trades-for-compute, NOT free); (2) sigma_query is "
                        "fixed at 0.1 (no sweep), so noise-robustness range of the storage-win is "
                        "UNVERIFIED; prior synthetic showed brittleness at sig=0.3 on low-eff-rank keys. "
                        "Headline 0.998 itself not locally verifiable (smoke shows 0.612, full GPU "
                        "metrics not synced). Storage compression IS real at ~103x vs dense f32 keys, "
                        "BUT the 'storage win' framing without (compute, noise-range) decomposition "
                        "overclaims uniqueness over attention."
                    ),
                },
            ],
            'operational_rule': (
                'For any substrate retrieval mechanism claiming a storage advantage over attention or any '
                'baseline, the SCHEMA-VET pre-reg AND landed-VET must surface three measurements: '
                '(1) B/mem (storage); (2) ops-per-query (compute, with O-class); (3) sigma_query sweep '
                '(noise-robustness range). Any cited "storage win" missing any of the three is downgraded '
                'to "storage compression at scope" -- the substrate-vs-attention uniqueness claim '
                'requires all three.'
            ),
            'eleventh_rule_clean': True,
            'symmetric_bidirectional': True,  # applies to both substrate AND baseline claims
        },
    )

    print(f'\n[BUILD] META atom: {META_ATOM_ID}')
    print(f'        corpus=META tier=TIER_METHODOLOGY kind=AUDIT_LESSON algebra=None')
    print(f'        description={len(META_DESCRIPTION)} chars')

    # ----- WRITE the atom (idempotent: add_atom replaces same-id) -----
    # Pre-check: does this atom-id already exist?
    existing_ids = {a.id for a in ps.all_atoms()}
    is_new = META_ATOM_ID not in existing_ids
    if not is_new:
        print(f'\n[IDEMPOTENT] atom {META_ATOM_ID} already exists; will replace metadata in place')

    ps.add_atom(meta_atom)
    print(f'\n[ADD] atom appended/replaced')

    # ----- A5 POST -----
    # Re-load to catch NULL-seam
    ps2 = PartitionedStore(REPO / 'data' / 'substrate_index')
    post_cert = _cert_count(ps2)
    post_ax = _axiom_count(ps2)
    post_cap = _cap_pres_ok()
    post_n = sum(1 for _ in ps2.all_atoms())
    print(f'\n[A5 POST] CERT={post_cert} axiom={post_ax} cap_pres={"6/6" if post_cap else "FAIL"} atoms={post_n}')

    # META atom must be CERT-neutral
    assert post_cert == pre_cert, f'CERT drifted on META add: pre={pre_cert} post={post_cert}'
    assert post_ax == 206, f'A5-POST axiom drift: {post_ax} != 206'
    assert post_cap, 'A5-POST cap_pres FAIL'

    # Atom delta -- new atom adds +1, idempotent replace adds 0
    expected_delta = 1 if is_new else 0
    assert post_n == pre_n + expected_delta, f'atom count delta off: pre={pre_n} post={post_n} expected_delta={expected_delta}'

    # Verify the new atom is loadable
    loaded = next((a for a in ps2.all_atoms() if a.id == META_ATOM_ID), None)
    assert loaded is not None, f'META atom {META_ATOM_ID} not loadable post-write'
    assert loaded.algebra is None, f'META atom algebra must be None; got {loaded.algebra}'
    print(f'        META atom round-trips OK; algebra=None confirmed')

    # ----- Write the cert_relabel ledger row -----
    print(f'\n[LEDGER] writing cert_relabel row (supersedes 1e1302ff6293598f)')
    rh = append_cert_ledger_row(
        {
            'ts': ts_now,
            'op': 'cert_relabel',
            'atom_id': 'math::T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu',
            'cert_status': 'measured_mechanism',  # refines from honest_negative -> MM at recall-class level (storage-win VALUE is conditional/open-loop)
            'cert_class': 'mechanism_characterization',
            'verified_off_data': True,  # cell source code-traced + smoke metrics re-derived
            'atomized_by': 'skunkworks_path_d_4arm_storage_win_scrutiny',
            'cell_commit': None,  # cell content traced from local source; GPU full per-seed not local
            'verdict': 'MIDDLE_BAND',  # cell verdict unchanged
            'cert_increment_delta': 0,  # CERT-neutral (was 0 before, stays 0)
            'cv': None,
            'referent_pointer': {
                'notes_path': 'notes/skunkworks_to_research_cc_all_PATH_D_4arm_storage_win_VALUE_scrutiny_2026-06-22.md',
                'metrics_path': 'data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json',
                'atom_qualified_id': 'math::T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu',
            },
            'supersedes': '1e1302ff6293598f',
            'note': (
                'path_d_skunkworks_scrutiny_refines_honest_negative_to_MM_at_recall_class_level_storage_win_value_conditional_'
                'arm_b_retrieval_mode_is_single_probe_exact_tag_O_M_dp_5x_compute_vs_attention_103x_storage_compression_vs_dense_f32_'
                'noise_robustness_untested_sigma_fixed_at_0_1_no_sweep_director_converge_storage_win_confirmed_overclaims_3_ways_'
                'compute_trades_for_storage_noise_range_unverified_headline_0_998_not_locally_verifiable_smoke_only'
            ),
        },
        expected_cert_n_pre=pre_cert,
        expected_cert_n_post=pre_cert,  # delta=0 so post==pre
        strict_a5=True,
    )
    print(f'         cert_relabel row_hash = {rh}')
    print(f'         supersedes = 1e1302ff6293598f')

    # ----- Final A5 confirm + ledger tail check -----
    rows_final = _read_ledger(LEDGER_PATH)
    tail = rows_final[-1]
    assert tail['op'] == 'cert_relabel'
    assert tail['supersedes'] == '1e1302ff6293598f'
    assert tail['atom_id'] == 'math::T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu'
    print(f'\n[LEDGER TAIL] op={tail["op"]} status={tail["cert_status"]} delta={tail["cert_increment_delta"]} hash={rh}')
    print(f'[LEDGER ROWS] {len(rows_final)} (was 631 pre)')

    print(f'\n[DONE]')
    print(f'  - META atom: {META_ATOM_ID} (CERT-neutral; atoms {pre_n} -> {post_n})')
    print(f'  - cert_ledger relabel: {rh} (supersedes 1e1302ff6293598f; delta=0)')
    print(f'  - CERT N: {post_cert} (unchanged; was {pre_cert})')
    print(f'  - axiom: {post_ax} (must be 206)')
    print(f'  - cap_pres: {"6/6" if post_cap else "FAIL"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
