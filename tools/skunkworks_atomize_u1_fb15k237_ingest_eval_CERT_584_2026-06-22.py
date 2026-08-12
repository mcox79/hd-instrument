"""Skunkworks 2026-06-22 -- atomize U1 FB15k-237 INGEST-EVAL as CERT_CHAIN_GRADE: CERT 583 -> 584.

FIRST CHAIN-GRADE POST-STANDSTILL. FIRST PRODUCTION USE OF PHASE C LIVE-WRITE HELPER.

The substrate's KB-INGEST of real FB15k-237 (50k triples) genuinely GOVERNS (refuse-gate fact-fab-bound)
and COMPOSES (inference-transfer 2-hop traversal beyond direct lookup). Multi-value Hebbian
superposition + set-readout-top-k is the FAITHFUL ingest mechanism for a multigraph (25.8% of (s,p)
keys are 1-to-many, max 160 objects); set-recall@K is NOT by-construction-saturated (random-floor
0.0001 vs observed 0.99 -> 7410x over random).

VERIFIED OFF DATA (per_seed across seeds 7/17/23):
- fidelity@M50000 set-recall all=0.9896 (cited 0.990; cv=0.0035), 1to1=0.9883 (cited 0.988; cv=0.0028)
- refuse_gate OOD-refuse=0.9744 (cited 0.974; cv=0.0138), in-KB-accept=0.9578 (cited 0.958; cv=0.0043)
- inference_transfer substrate_2hop=0.3808 (cited 0.381; cv=0.0450) vs baseline_1hop=0.0075 (cv=0.0000)
- scale_curve {5k:1.0, 10k:1.0, 25k:0.999, 50k:0.99} (matches verdict_msg)
- All cv <= 0.05 across 3 seeds; HARD_PASS verdict mechanically correct per the cell's verdict() logic.

A5 gates: PRE CERT=583 -> POST CERT=584 (+1, chain-grade increment); axiom 206 UNCHANGED (algebra=None);
cap_pres 6/6; +1 atom; Store-loads; idempotent skip-if-exists. ASCII.

Cert ledger live-write: same A5 window via tools.cert_ledger_writer.build_chain_grade_ruling_row +
append_cert_ledger_row. Phase C first production use; expected ledger 630 -> 631.

PRE-ATOMIZE SATISFIED:
- SCHEMA-VET (b9e4485f) bands locked + OPEN-E multi-value resolution VET'd
- Cell built + run on .venv full mode (3 seeds, N_DIM=8192, M=50k)
- Cell commit: 6218a69f
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row, build_chain_grade_ruling_row


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


U1 = Atom(
    id='T3/EXP_u1_fb15k237_ingest_eval_v1',
    name=('Experiment record (CERT_CHAIN_GRADE, CERT 584): substrate KB-ingest of real FB15k-237 (50k triples) '
          'GENUINELY GOVERNS (refuse-gate OOD=0.974/accept=0.958, fact-fab-bound) AND COMPOSES (inference-transfer '
          'substrate-2hop=0.381 vs 1hop-base=0.007 with heldout_in_compose_graph==0); multi-value Hebbian + '
          'set-readout-top-k delivers set-recall=0.990 at M=50k (1-to-many 25.8% of keys, not by-construction '
          '-- random-floor 0.0001, 7410x over random); 3 seeds cv<=0.05'),
    description=(
        'U1: substrate KB-INGEST of real FB15k-237 50k triples via MULTI-VALUE Hebbian-accumulate '
        '(W += sum_i outer(E[o_i], key_i)/N; key=E[s]*R[p]*sqrt(N); N_DIM=8192) with set-readout-top-k '
        'where k=|objects(s,p)|. The FAITHFUL multigraph ingest mechanism (25.8% of 29166 (s,p) keys are '
        '1-to-many; max 160 objects). Three load-bearing eval axes all pass at the SCHEMA-VET bands '
        '(b9e4485f): (1) REFUSE-GATE OOD>=0.80 & in-KB-accept>=0.80 -> achieved 0.974/0.958 '
        '(2.44x conf separation in-KB vs OOD; tau calibrated on held split, non-circular eval); '
        '(2) INFERENCE-TRANSFER substrate-2hop > 1hop-lookup baseline (heldout_in_compose_graph==0 '
        'GENUINELY asserted, leak guard firing 13-19/417 chains, NOT vacuous) -> achieved 0.381 '
        'vs 0.0075 baseline (substrate genuinely composes held-out 2-hop facts; absolute 0.381 is '
        '~5000x over random argmax 1/n_ent); (3) RETRIEVAL-AT-SCALE M=50k -> set-recall curve '
        '{5k:1.0, 10k:1.0, 25k:0.999, 50k:0.990} graceful at scale. FIDELITY (report-floor 0.95) '
        'achieved 0.99 BOTH on the 1-to-1 subset (0.988) AND on all keys including 1-to-many '
        '(0.990) -- multi-value superposition resolves the single-value ceiling 0.742 that the '
        'SCHEMA-VET addendum (8f26a6b7) flagged. Pure numpy + BLAS matmul; ZERO LLM/model-forward '
        'calls at ingest or eval (substrate-native end-to-end); verified by source audit '
        '(no transformers/AutoModel/pythia/.forward/.generate/model() in the cell). Three seeds '
        '(7,17,23); all cv <= 0.05; HARD_PASS verdict logic mechanically correct.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'HIGH',
        'verdict': 'HARD_PASS_chain_grade_first_post_STANDSTILL_substrate_KB_ingest_governs_and_composes',
        'run_mode': 'full',
        'n_seeds': 3,
        'seeds': [7, 17, 23],
        'N_DIM': 8192,
        'M_scale_points': [5000, 10000, 25000, 50000],
        'corpus': 'FB15k-237 50k triples (n_ent=12838, n_rel=237, n_keys=29166)',
        'metrics_path': 'data/exp_u1_fb15k237_ingest_eval_v1/metrics.json',
        'metrics_source': 'substrate_KB_ingest_eval_FB15k_237_50k_multi_value_hebbian_set_readout',
        'cell_commit': '6218a69f',
        'key_metrics': {
            'fidelity_setrecall_all_M50000_mean': 0.9896,
            'fidelity_setrecall_all_M50000_cv': 0.0035,
            'fidelity_setrecall_1to1_M50000_mean': 0.9883,
            'fidelity_setrecall_1to1_M50000_cv': 0.0028,
            'refuse_OOD_refuse_mean': 0.9744,
            'refuse_OOD_refuse_cv': 0.0138,
            'refuse_inkb_accept_mean': 0.9578,
            'refuse_inkb_accept_cv': 0.0043,
            'refuse_inkb_vs_ood_conf_ratio_mean': 2.4280,
            'refuse_tau_mean': 9.74e-05,
            'inference_substrate_2hop_mean': 0.3808,
            'inference_substrate_2hop_cv': 0.0450,
            'inference_baseline_1hop_mean': 0.0075,
            'inference_n_chains': 400,
            'inference_leak_skipped_per_seed': [17, 13, 19],
            'inference_heldout_in_compose_graph': 0,
            'scale_curve_setrecall_all_mean': {'M5000': 1.0, 'M10000': 1.0, 'M25000': 0.9989, 'M50000': 0.9896},
            'random_floor_setrecall_all_keys': 0.0001,
            'substrate_vs_random_floor_x': 7410,
            'n_keys_1to1': 21653,
            'n_keys_1to_many': 7513,
            'frac_1to_many': 0.2576,
            'max_objects_single_key': 160,
        },
        'honest_scope': (
            'U1 demonstrates substrate KB-INGEST on FB15k-237 50k via multi-value Hebbian + set-readout: '
            'genuine governance (refuse-gate fact-fab-bound on real vs fabricated edges, non-circular tau) '
            'and genuine composition (2-hop traversal beyond direct lookup; heldout disjoint-from-train asserted '
            'and leak guard non-vacuous). Multi-value superposition is the FAITHFUL multigraph metric; set-recall@K '
            'is NOT by-construction-saturated (random-floor 0.0001). Does NOT validate: '
            '(a) transfer to other KGs (FB15k-237 is one corpus); (b) "beats frozen-encoder semantic baseline" '
            '-- OPEN-C deferred because FB15k-237 entities are MIDs (/m/027rn) not readable strings, '
            'so a sentence-encoder baseline is meaningless here; the 1-hop-lookup is the MID-valid bar '
            '(stronger semantic bar requires staging entity-names, future work); (c) robustness under noise '
            '-- refuse-gate signal magnitude is at Hebbian-normalization scale (~1e-4 absolute) with '
            'tau~9.7e-5; the 2.44x in-KB/OOD ratio is genuine separation but small-magnitude (caveat #2 '
            'in exp_dev landed-VET request); (d) the 1-hop baseline is zero-by-construction (chains exclude '
            'direct (s,o) train edges) -- the "54x over baseline" framing is misleading, but the absolute '
            '0.381 substrate_2hop accuracy IS load-bearing (5000x over random argmax) and the load-bearing '
            'claim is "substrate composes held-out 2-hop", not "54x over baseline".'),
        'finding': (
            'First chain-grade post-STANDSTILL ingest-eval. The substrate is a working KB-ingest engine: '
            'real KG triples ingested via multi-value Hebbian, governed by a refuse-gate (97% OOD-refuse + '
            '96% in-KB-accept, fact-fab-bound), composing via 2-hop traversal (38% absolute on held-out chains). '
            'Multi-value superposition + set-readout-top-k resolves the 1-to-many fidelity ceiling that '
            'single-value stores cap at ~0.74. Path F (ingest pipeline) of the L2 substrate-native vision '
            'validated on a real KB at 50k scale.'),
        'baseline_provenance': (
            '1-hop-lookup baseline (substrate-internal): from s via either p1 or p2, can a single-hop '
            'retrieval find o? By the heldout_in_compose_graph==0 closure assert, this baseline is '
            'zero-by-construction on held-out chains; the substrate must traverse 2-hop to find o. '
            'OPEN-C deferred: frozen-encoder semantic baseline not applicable to MID-keyed FB15k-237.'),
        'composes_with': [
            'T3/EXP_ccc1_extra_fb15k237_kg_multihop_v1',  # the 5k-toy ingest+multihop base U1 scaled up
            'T3/EXP_kv_learned_projection_v1',  # CERT 591: learned key-projection generalizes (compose with Path B/A)
            'T3/EXP_kmax_ness_envelope_corrected_v1',  # CERT 592: NESS depth (complementary substrate mechanism)
        ],
        'depends_on_text': (
            'Multi-value Hebbian KB-ingest (substrate mechanism per OPEN-E SCHEMA-VET resolution); '
            'set-readout-top-k (faithful multigraph metric); margin-refuse on held split (refuse-gate '
            'non-circularity); heldout_in_compose_graph==0 closure assert (inference-transfer genuineness). '
            'Recorded in metadata (phantom-safe; FB15k-237 corpus is a data reference, not a substrate atom).'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-22_CERT_584_chain_grade_first_post_STANDSTILL',
        'verified_off_data': (
            'cert-owner re-derived all cited numbers from data/exp_u1_fb15k237_ingest_eval_v1/per_seed '
            '(seeds 7/17/23) via .venv numpy: fidelity 0.9896/0.9883, refuse 0.9744/0.9578, inference 0.3808/0.0075; '
            'all cv <= 0.05; random-floor 0.0001 for set-recall@K confirms NOT by-construction; '
            'leak guard firing 13-19/417 confirms inference closure non-vacuous; '
            'source audit confirms zero LLM/model-forward calls at ingest or eval.'),
        'prereg': 'SCHEMA-VET b9e4485f (Skunkworks bands) + OPEN-E multi-value resolution (8f26a6b7); cell ec5e5638',
        'atomized_by': 'skunkworks',
        'atomized_date': '2026-06-22',
        'era': 'agent_teams_post_STANDSTILL_phase_C_live_write_first_use',
        'milestone': (
            'First chain-grade increment post-STANDSTILL (CERT 583 -> 584). First production use of '
            'tools/cert_ledger_writer.py (Phase C live-write). Path F (ingest pipeline) of the L2 '
            'substrate-native vision validated on real FB15k-237 at 50k.'),
        'open_followups': [
            'OPEN-C: stage FB15k-237 entity-names to enable frozen-encoder semantic baseline (stronger bar)',
            'Robustness: refuse-gate at noisy / adversarial OOD (the small-tau absolute-magnitude caveat)',
            'Transfer: validate the multi-value ingest mechanism on a second KB corpus (e.g. Wikidata-subset)',
        ],
    })


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    if pre_cert != 583:
        print(f"PRE-GATE WARN: CERT={pre_cert} (expected 583). Investigate before bump."); return 1
    existed = ps.get_atom(U1.qualified_id) is not None
    if existed:
        print(f"  SKIP exists: {U1.id}")
    else:
        ps.add_atom(U1, source='skunkworks_u1_fb15k237_ingest_eval_CERT_584_2026_06_22',
                    note='U1 first chain-grade post-STANDSTILL: substrate KB-ingest governs+composes (CERT 583->584)')
        print(f"  ADD: {U1.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom(U1.qualified_id) is not None
    bad_alg = landed and ps2.get_atom(U1.qualified_id).algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 584) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert == 584 and post_ax == 206 and post_mod and landed and not bad_alg)
    print("STORE GATE:", "OK -- CERT 584 (chain-grade)" if gate else "FAIL")
    if not gate:
        return 2

    # ========================================================================
    # PHASE C LIVE-WRITE: cert_ledger row in the SAME A5 window
    # ========================================================================
    print()
    print("=== PHASE C live-write: cert_ledger row (first production use) ===")
    ledger_row = build_chain_grade_ruling_row(
        atom_id='math::T3/EXP_u1_fb15k237_ingest_eval_v1',
        cell_commit='6218a69f',
        verdict='HARD_PASS',
        notes_path='notes/skunkworks_to_research_cc_all_LANDED_VET_U1_fb15k237_ingest_eval_HARD_PASS_2026-06-22.md',
        metrics_path='data/exp_u1_fb15k237_ingest_eval_v1/metrics.json',
        cv=0.045,  # max cv across the three load-bearing dims (substrate_2hop cv=0.0450 is the loosest)
        cert_class='pre_reg_pass',
        note='u1_fb15k237_first_chain_grade_post_STANDSTILL_phase_C_first_production_use',
    )
    row_hash = append_cert_ledger_row(
        ledger_row,
        expected_cert_n_pre=584,   # at this point the upstream Store add has ALREADY moved CERT 583->584
        expected_cert_n_post=584,  # ledger append does NOT touch CERT; should remain at 584
    )
    print(f"LEDGER ROW HASH: {row_hash}")
    print("PHASE C GATE: OK -- cert_ledger row appended in the same A5 window")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms} --ledger-row {row_hash}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
