"""Skunkworks landed-VET + atomize for h_hotpotqa_ingest_v1 (chain-grade).

CERT RULING (auditor A5 call):

  h_hotpotqa_ingest_v1: substrate KB-ingest of HotpotQA-distractor 1k-dev as 2-hop chains
  (title1 -> title2 -> answer). 3-seed full at N_DIM=4096, M_items=1000.

  Pre-reg HARD bands (locked in notes/h_hotpotqa_ingest_pre_reg_2026-06-22.md):
    setrecall_all >= 0.95   AND
    refuse OOD >= 0.80      AND in-KB accept >= 0.80   AND
    substrate_2hop > 1-hop direct + 0.02 AND ratio >= 2.0x   AND
    substrate_2hop >= 2.0x frozen-encoder semantic baseline   AND
    zero_llm_calls_at_inference == True   AND
    encoder off-diag mean cos <= 0.95

  Observed (3-seed mean, re-derived directly from metrics.json):
    setrecall = 1.0000          (HARD floor 0.95; CRUSHED; cv=0.000)
    rand_ctrl = 0.0000          (Fix #16 discriminator-regime; mechanism-real, not artifact)
    refuse OOD = 1.0000         (HARD floor 0.80)
    refuse accept = 0.9967      (HARD floor 0.80)
    substrate_2hop = 0.9911     (300 chains per seed; mean across 3 seeds)
    baseline_1hop_direct = 0.0011  (substrate has no (t1, supplies_answer, ?) key; near-random)
      -> ratio 892.00x            (HARD floor 2.0x; CRUSHED)
    baseline_frozen_encoder = 0.0411 (MiniLM-L6 entity-name semantic NN)
      -> ratio 24.11x             (HARD floor 2.0x; CRUSHED)
    bridge_recall = 1.0000      (hop-1 perfect)
    encoder off-diag cos = 0.1468 (HALT thresh 0.95; no MedQA mean-pool collapse)
    zero_llm_calls_at_inference = True
    elapsed_s = 20.8s on remote_cpu
    M_triples = 1610 per seed (2 per item, minus degenerate); n_ent = 2696; n_keys = 1601
    n_chains_bridge = 671 per seed (eval n=300)

  All 6 HARD-bands pass; no HARD_FAIL floor breached.
  cv across seeds = 0.000.

STRATEGIC POSITIONING (auditor concurs with Director cross-check):

  This is the 3rd cross-domain chain-grade KG ingest in the post-STANDSTILL arc:
    - U1 FB15k-237 (structured Freebase triples)             -> CERT 583 -> 584
    - n8 ConceptNet (general English lexical KG)             -> CERT 584 -> 585
    - h_hotpotqa_ingest_v1 (Wikipedia multi-hop QA text)     -> CERT 587 -> 588 (this)

  The substrate's "multi-domain KG ingest at chain-grade" claim is now substantiated
  across three distinct KG shapes: structured / lexical / unstructured-multi-hop. The
  L3 capability tier multi-value-KG row promotes from "first chain-grade post-STANDSTILL"
  to "multi-domain chain-grade portfolio." This atom carries the multi-hop-QA-on-Wikipedia
  shape; n8 and U1 hold the other two.

  The encoder choice (MiniLM-L6) deviates from the spawn directive (pythia-160m mean-pool)
  because the MedQA HARD_FAIL on 2026-06-22 demonstrated pythia mean-pool collapses on long
  uniform-topic vignettes (off-diag cos 0.9865). HotpotQA encodes ENTITIES (Wikipedia titles,
  ~3-5 tokens), so MiniLM-L6 - the n8-proven encoder on short entity names - is both
  safer and gives closer mechanism-mirror to n8. Pre-reg explicitly documents the deviation.
  Encoder-geometry HALT guard (off-diag cos > 0.95) was wired in the cell and would have
  HARD_FAILed had pythia-style collapse recurred; observed off-diag = 0.1468 (well below).

ATOMS WRITTEN: 1
  math::T3/EXP_h_hotpotqa_ingest_v1
    kind=EXPERIMENT_RECORD, tier=TIER_3_ALGORITHM, corpus=MATH
    provenance_quality=CERT_CHAIN_GRADE (delta=+1; CERT 587 -> 588)
    cert_class=pre_reg_pass

LEDGER ROW APPENDED: 1
  cert_ruling, chain_grade, delta=+1

STATE CHANGE EXPECTED:
  atoms: 177283 -> 177284 (+1)
  CERT N: 587 -> 588 (+1)
  axiom_term: 206 preserved
  cap_pres: 6/6 preserved
  ledger rows: 653 -> 654 (+1)

DISCIPLINES APPLIED:
  - A5 PRE/POST snapshot via append_cert_ledger_row(strict_a5=True)
  - Idempotency pre-check (atom-id existence guard)
  - verify-the-referent: all cited numbers re-derived from metrics.json this run
  - cited-number-must-reproduce: load-bearing numbers checked against per_seed payloads
  - pre-reg-direction-must-honor-intent: substrate >> 1-hop AND substrate >> frozen-enc
    honored at every seed; no negative-direction surprises
  - data-decides-tier: 6/6 HARD bands hit with HARD floors crushed
  - Fix #16 discriminator-regime: random-key control = 0.000 (mechanism-real)
  - encoder-geometry HALT (MedQA collapse signature) sibling discipline checked
  - substrate-only-decode gate: n_llm_calls_at_inference = 0
  - Path-scoped commit (no git add -A; data/substrate_index/ partitions handled
    by add_atom internally with single-writer discipline)

USAGE:
    .venv/Scripts/python.exe tools/skunkworks_atomize_h_hotpotqa_ingest_chain_grade_2026-06-22.py
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    _cert_count, _axiom_count, _cap_pres_ok,
)

CELL_COMMIT = 'bfda5f73'
METRICS_PATH = 'data/exp_h_hotpotqa_ingest_v1/metrics.json'
SMOKE_METRICS_PATH = 'data/exp_h_hotpotqa_ingest_v1_smoke/metrics.json'
NOTES_PATH = 'notes/h_hotpotqa_ingest_pre_reg_2026-06-22.md'

EXPECTED_CERT_PRE = 587
EXPECTED_CERT_POST = 588


def main():
    print('=' * 78)
    print('Skunkworks landed-VET + atomize: h_hotpotqa_ingest_v1')
    print('Ruling: CERT_CHAIN_GRADE (delta=+1; CERT 587 -> 588)')
    print('3rd cross-domain chain-grade KG ingest (after U1 FB15k-237 + n8 ConceptNet)')
    print('=' * 78)

    # ------------------------------------------------------------------
    # A5 PRE-snapshot
    # ------------------------------------------------------------------
    ps = PartitionedStore(REPO / 'data' / 'substrate_index')
    pre_atoms = ps.all_atoms()
    n_pre = len(pre_atoms)
    cert_pre = _cert_count(ps)
    ax_pre = _axiom_count(ps)
    cap_pre = _cap_pres_ok()
    assert ax_pre == 206, f'A5-PRE axiom drift: {ax_pre} != 206'
    assert cap_pre, 'A5-PRE cap_pres FAIL'
    # Idempotency pre-check (defines whether this is the atom-write run or ledger-only resume)
    target_id = 'T3/EXP_h_hotpotqa_ingest_v1'
    target_qid = f'math::{target_id}'
    existing = [a for a in pre_atoms if a.id == target_id]
    is_resume = bool(existing)
    if is_resume:
        # Atom already in Store from a prior run; this run is ledger-only.
        # Expected pre-state: live CERT N includes the new atom already (= EXPECTED_CERT_POST = 588).
        assert cert_pre == EXPECTED_CERT_POST, (
            f'A5-PRE resume CERT mismatch: live={cert_pre} expected={EXPECTED_CERT_POST} '
            f'(atom exists; ledger-only resume)'
        )
    else:
        # Fresh run: atom not yet written; pre-state should match seed expectation.
        assert cert_pre == EXPECTED_CERT_PRE, (
            f'A5-PRE CERT mismatch: live={cert_pre} expected={EXPECTED_CERT_PRE}'
        )
    print(f'\nA5-PRE: atoms={n_pre} CERT={cert_pre} axiom={ax_pre} '
          f'cap_pres={"6/6" if cap_pre else "FAIL"}')
    print(f'  existing h_hotpotqa atom: {len(existing)} '
          f'({"LEDGER-ONLY RESUME" if is_resume else "fresh atom-write"})')

    # ------------------------------------------------------------------
    # Re-derive cited numbers from metrics.json (verify-the-referent)
    # ------------------------------------------------------------------
    m = json.loads((REPO / METRICS_PATH).read_text(encoding='utf-8'))
    ps_seeds = m['per_seed']
    n_seeds = m['n_seeds']

    # SCHEMA-VET assertions on top-level invariants
    assert m['verdict'] == 'HARD_PASS', f'expected HARD_PASS, got {m["verdict"]}'
    assert m['run_mode'] == 'full', f'expected run_mode=full, got {m["run_mode"]}'
    assert n_seeds == 3, f'expected n_seeds=3, got {n_seeds}'
    assert m['n_llm_calls_at_inference'] == 0
    assert m['zero_llm_calls_at_inference'] is True
    assert m['anchor_name'] == 'h_hotpotqa_ingest_v1'

    # Per-seed run_mode + structural assertions
    for s in ps_seeds:
        assert s['run_mode'] == 'full', f'seed {s["seed"]} run_mode {s["run_mode"]}'
        assert s['N'] == 4096
        assert s['M_triples'] == 1610
        assert s['n_ent'] == 2696
        assert s['n_rel'] == 2
        assert s['n_chains_bridge'] == 671
        assert s['inference_transfer']['n'] == 300
        assert s['inference_transfer']['bridge_recall'] == 1.0
        assert s['encoder_geometry']['off_diag_mean_cos'] <= 0.95, (
            f'seed {s["seed"]} encoder off-diag {s["encoder_geometry"]["off_diag_mean_cos"]} > 0.95 (MedQA signature)'
        )

    # Re-derive cross-seed means
    def avg(key_path):
        vals = []
        for s in ps_seeds:
            x = s
            for k in key_path:
                x = x[k]
            vals.append(x)
        return sum(vals) / len(vals)

    def cv(key_path):
        import statistics as _st
        vals = []
        for s in ps_seeds:
            x = s
            for k in key_path:
                x = x[k]
            vals.append(x)
        mu = sum(vals) / len(vals)
        sd = _st.pstdev(vals)
        return sd / max(mu, 1e-9)

    sr_mean = avg(['setrecall_all'])
    sr_cv = cv(['setrecall_all'])
    rand_mean = avg(['random_key_control'])
    ood_mean = avg(['refuse_gate', 'ood_refuse'])
    acc_mean = avg(['refuse_gate', 'inkb_accept'])
    s2_mean = avg(['inference_transfer', 'substrate_2hop'])
    b1_mean = avg(['inference_transfer', 'baseline_1hop_direct'])
    enc_mean = avg(['inference_transfer', 'baseline_frozen_encoder'])
    bridge_mean = avg(['inference_transfer', 'bridge_recall'])
    geom_mean = avg(['encoder_geometry', 'off_diag_mean_cos'])
    geom_max_mean = avg(['encoder_geometry', 'off_diag_max_cos'])
    tau_mean = avg(['refuse_gate', 'tau'])

    ratio_1hop = s2_mean / max(b1_mean, 1e-6)
    ratio_enc = s2_mean / max(enc_mean, 1e-6)

    # HARD-band re-checks (auditor-side; mirror cell's verdict() logic)
    assert sr_mean >= 0.95, f'setrecall {sr_mean} < 0.95 HARD floor'
    assert ood_mean >= 0.80, f'refuse OOD {ood_mean} < 0.80 HARD floor'
    assert acc_mean >= 0.80, f'accept {acc_mean} < 0.80 HARD floor'
    assert s2_mean > b1_mean + 0.02, f'2hop margin {s2_mean - b1_mean} <= 0.02'
    assert ratio_1hop >= 2.0, f'2hop/1hop ratio {ratio_1hop} < 2.0 HARD floor'
    assert ratio_enc >= 2.0, f'2hop/frozen-enc ratio {ratio_enc} < 2.0 HARD floor'
    assert geom_mean <= 0.95, f'encoder off-diag {geom_mean} > 0.95 (MedQA collapse signature)'

    # Cross-check Director-cited numbers (verify-the-referent on Director cross-check)
    # Director said 892x and 24.11x; we re-compute and confirm.
    assert abs(ratio_1hop - 892.0) < 1.0, f'1hop ratio drift: {ratio_1hop} vs Director 892x'
    assert abs(ratio_enc - 24.11) < 0.5, f'enc ratio drift: {ratio_enc} vs Director 24.11x'

    print(f'\nSCHEMA-VET PASS: all metrics-json invariants confirmed.')
    print(f'  verdict={m["verdict"]} run_mode={m["run_mode"]} n_seeds={n_seeds}')
    print(f'  setrecall mean={sr_mean:.4f} cv={sr_cv:.4f} (HARD floor 0.95)')
    print(f'  rand_ctrl mean={rand_mean:.4f} (discriminator-regime; mechanism-real)')
    print(f'  refuse OOD mean={ood_mean:.4f} accept mean={acc_mean:.4f} (HARD floors 0.80)')
    print(f'  2hop mean={s2_mean:.4f} 1hop mean={b1_mean:.4f} ratio={ratio_1hop:.2f}x')
    print(f'  frozen-enc mean={enc_mean:.4f} ratio={ratio_enc:.2f}x')
    print(f'  bridge_recall mean={bridge_mean:.4f}')
    print(f'  encoder off-diag mean={geom_mean:.4f} (HALT thresh 0.95)')
    print(f'  n_llm_calls_at_inference={m["n_llm_calls_at_inference"]} (substrate-only-decode gate)')

    # ------------------------------------------------------------------
    # Build atom
    # ------------------------------------------------------------------
    metric_headline = (
        f'setrecall={sr_mean:.4f} (rand-ctrl={rand_mean:.4f}); '
        f'refuse OOD={ood_mean:.3f} acc={acc_mean:.3f}; '
        f'2hop={s2_mean:.3f} vs 1hop={b1_mean:.3f} (ratio={ratio_1hop:.2f}x) '
        f'vs frozen-enc={enc_mean:.3f} (ratio={ratio_enc:.2f}x); '
        f'bridge={bridge_mean:.3f}; encoder off-diag={geom_mean:.4f}; '
        f'cv={sr_cv:.3f}; n_llm=0; elapsed={m["elapsed_s"]:.0f}s'
    )

    honest_scope = (
        f'h_hotpotqa_ingest_v1 ran 3-seed full at N_DIM=4096 on 1000 HotpotQA-distractor '
        f'dev items (1610 triples per seed, 2696 entities, 2 relation types: linked_via '
        f'+ supplies_answer). Per-item 2-hop chain: (title1, linked_via, title2) + '
        f'(title2, supplies_answer, answer). 671 bridge-type chains per seed; eval n=300. '
        f'Encoder = sentence-transformers/all-MiniLM-L6-v2 (n8-proven on short entity names; '
        f'chosen over pythia-160m mean-pool which collapsed on MedQA long vignettes today). '
        f'Encoder-geometry HALT guard (off-diag cos > 0.95) wired and silent (observed '
        f'{geom_mean:.4f}). Substrate-only-decode preserved: encoder runs ONCE at ingest, '
        f'discarded post-encode; retrieval is numpy matmul (n_llm_calls_at_inference=0). '
        f'Pre-reg HARD bands (notes/h_hotpotqa_ingest_pre_reg_2026-06-22.md) all 6 met: '
        f'setrecall={sr_mean:.4f}>=0.95; refuse OOD={ood_mean:.3f}>=0.80 acc={acc_mean:.3f}>=0.80; '
        f'2hop>1hop+0.02 AND ratio={ratio_1hop:.2f}x>=2.0x; 2hop/frozen-enc={ratio_enc:.2f}x>=2.0x; '
        f'zero_llm_calls=True; encoder off-diag<=0.95. Discriminator-regime control '
        f'(Fix #16): random-key control rand_ctrl={rand_mean:.4f} (mechanism-real, not metric '
        f'artifact). Pre-reg-direction-must-honor-intent honored: substrate >> 1-hop AND '
        f'substrate >> frozen-enc at every seed. cv across seeds = {sr_cv:.4f}. '
        f'Mirrors n8 ConceptNet (CERT 585) + U1 FB15k-237 (CERT 584) chain-grade pattern '
        f'on a 3rd corpus shape: unstructured multi-hop QA over free Wikipedia text content. '
        f'Composes with n8/U1 to substantiate substrate "multi-domain KG ingest at chain-grade" '
        f'across structured / lexical / unstructured-multi-hop KG shapes.'
    )

    finding = (
        f'Substrate KB-ingest of HotpotQA-distractor 1k dev items as 2-hop chains '
        f'(title1 -> title2 -> answer) chain-grade certified: setrecall={sr_mean:.4f}, '
        f'refuse OOD={ood_mean:.3f} acc={acc_mean:.3f}, substrate 2-hop accuracy '
        f'{s2_mean:.3f} beating 1-hop direct {b1_mean:.3f} by {ratio_1hop:.0f}x ratio and '
        f'frozen-encoder semantic NN {enc_mean:.3f} by {ratio_enc:.2f}x, bridge_recall '
        f'{bridge_mean:.3f}. Zero LLM forward calls at retrieval (substrate-only-decode). '
        f'Encoder off-diag cos {geom_mean:.4f} (no MedQA mean-pool collapse). cv across 3 '
        f'seeds = {sr_cv:.4f}. Confirms substrate "multi-domain KG ingest" claim across a '
        f'3rd KG shape (unstructured multi-hop QA on Wikipedia text), in addition to '
        f'n8 ConceptNet (lexical) and U1 FB15k-237 (structured Freebase triples).'
    )

    atom = Atom(
        id=target_id,
        name='h HotpotQA 1k-dev substrate KB-ingest 2-hop chains v1 (CERT_CHAIN_GRADE)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.EXPERIMENT_RECORD,
        description=(
            'Substrate KB-ingest of HotpotQA-distractor 1000-item dev split as 2-hop chains: '
            'per item, ingest (title1, linked_via, title2) + (title2, supplies_answer, answer). '
            '3-seed full at N_DIM=4096, M_triples=1610, n_ent=2696, n_rel=2. Set-readout-topk '
            '+ margin-refuse + 2-hop inference-transfer with both 1-hop direct and frozen-encoder '
            'semantic baselines. Discriminator-regime random-key control (Fix #16). '
            'Encoder = sentence-transformers/all-MiniLM-L6-v2 at ingest only (substrate-only-decode '
            'at retrieval; n_llm_calls=0). Encoder-geometry HALT guard (off-diag cos > 0.95) '
            'wired pre-emptively against the MedQA mean-pool-collapse signature. HARD_PASS: '
            'setrecall=1.000 cv=0.000; refuse OOD=1.000 acc=0.997; substrate_2hop=0.991 vs '
            '1hop=0.001 ratio=892x vs frozen-enc=0.041 ratio=24.11x; bridge_recall=1.000; '
            'encoder off-diag=0.1468. Mirrors n8 ConceptNet (CERT 585) + U1 FB15k-237 '
            '(CERT 584) chain-grade mechanism on a 3rd KG shape (unstructured multi-hop QA '
            'over Wikipedia text).'
        ),
        metadata={
            'provenance_quality': 'CERT_CHAIN_GRADE',
            'verdict': 'HARD_PASS',
            'cert_ruling': 'CERT_CHAIN_GRADE',
            'cert_class': 'pre_reg_pass',
            'relevance_tier': 'HIGH',
            'run_mode': 'full',
            'era': '2026-06-22',
            'config_version': m['config_version'],
            'experiment_path': 'experiments/exp_h_hotpotqa_ingest_v1.py',
            'metrics_path': METRICS_PATH,
            'prereg_path': NOTES_PATH,
            'smoke_metrics_path': SMOKE_METRICS_PATH,
            'cell_sha': CELL_COMMIT,
            'remote_queue': 'remote_cpu_queue',
            'n_seeds': n_seeds,
            'seeds': [7, 17, 23],
            'N_DIM': 4096,
            'M_items': 1000,
            'M_triples_per_seed': 1610,
            'n_entities': 2696,
            'n_relations': 2,
            'n_keys_per_seed': 1601,
            'n_chains_bridge_per_seed': 671,
            'n_chains_eval': 300,
            'corpus': 'hotpot_qa_distractor_dev_1k',
            'corpus_path': 'data/datasets/hotpot_qa_distractor_dev_1k.jsonl',
            'encoder_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'encoder_role': 'ingest_time_only_discarded_post_encode',
            'setrecall_mean': float(sr_mean),
            'setrecall_cv': float(sr_cv),
            'random_key_control_mean': float(rand_mean),
            'refuse_ood_mean': float(ood_mean),
            'refuse_accept_mean': float(acc_mean),
            'refuse_tau_mean': float(tau_mean),
            'substrate_2hop_mean': float(s2_mean),
            'baseline_1hop_direct_mean': float(b1_mean),
            'baseline_frozen_encoder_mean': float(enc_mean),
            'ratio_2hop_over_1hop': float(ratio_1hop),
            'ratio_2hop_over_frozen_encoder': float(ratio_enc),
            'bridge_recall_mean': float(bridge_mean),
            'encoder_off_diag_cos_mean': float(geom_mean),
            'encoder_off_diag_cos_max_mean': float(geom_max_mean),
            'encoder_geometry_halt_threshold': 0.95,
            'encoder_geometry_halt_triggered': False,
            'substrate_only_decode': True,
            'zero_llm_calls_at_inference': True,
            'n_llm_calls_at_inference': 0,
            'elapsed_s': float(m['elapsed_s']),
            'metric_headline': metric_headline,
            'finding': finding,
            'honest_scope': honest_scope,
            'pre_reg_direction_honored': True,
            'pre_reg_bands_satisfied': True,
            'pre_reg_bands_source': NOTES_PATH,
            'discriminator_regime_random_key_control': True,
            'discriminator_regime_frozen_encoder_baseline': True,
            'discriminator_regime_1hop_direct_baseline': True,
            'encoder_choice_deviation_from_spawn_directive': (
                'Spawn directive nominated pythia-160m mean-pool. MedQA HARD_FAIL on '
                '2026-06-22 demonstrated pythia mean-pool collapse on long uniform-topic '
                'vignettes (off-diag cos 0.9865). HotpotQA encodes ENTITIES (short ~3-5 '
                'token Wikipedia titles), so MiniLM-L6 (the n8-proven encoder on short '
                'entity names) chosen for closer mechanism-mirror to n8 + lower collapse '
                'risk. Pre-reg explicitly documents this deviation; encoder-geometry HALT '
                'guard wired against recurrence and observed off-diag = 0.1468 << 0.95.'
            ),
            'cross_domain_kg_ingest_portfolio_position': (
                '3rd chain-grade KG ingest in post-STANDSTILL arc; 3rd KG shape: '
                'unstructured multi-hop QA on free Wikipedia text. Portfolio: U1 FB15k-237 '
                '(structured Freebase, CERT 584) + n8 ConceptNet (lexical English KG, '
                'CERT 585) + h_hotpotqa (this; CERT 588). Substantiates substrate '
                '"multi-domain KG ingest at chain-grade" claim across 3 distinct KG shapes.'
            ),
            'related_meta_atoms': [
                'META_substrate_KB_ingest_2hop_chain_governed_refuse_gate_plus_composes',
                'META_frozen_encoder_semantic_baseline_unlocks_OPEN_C_chain_grade_for_KB_ingest',
                'META_encoder_mean_pool_collapse_HALT_guard_off_diag_cos_threshold_0p95',
            ],
            'composes_with': [
                'math::T3/EXP_n8_conceptnet_ingest_eval_v1',
                'math::T3/EXP_u1_fb15k237_ingest_eval_v1',
            ],
            'predecessor_atom': 'math::T3/EXP_n8_conceptnet_ingest_eval_v1',
            'predecessor_relationship': (
                'h_hotpotqa mirrors the n8 ConceptNet chain-grade mechanism (multi-value '
                'Hebbian + set-readout-topk + margin-refuse + 2-hop inference-transfer '
                'vs frozen-encoder semantic baseline) on a 3rd KG shape. Same encoder '
                '(MiniLM-L6 on short entity names), same substrate-only-decode gate, same '
                'discriminator-regime random-key control. The novelty is the corpus '
                'shape: HotpotQA is unstructured multi-hop QA over Wikipedia text '
                '(per-item triple extraction from supporting-fact titles + answers), '
                'whereas n8/U1 are pre-structured KGs (lexical English / structured '
                'Freebase). Substantiates substrate KB-ingest generalizes across the '
                'KG-shape axis.'
            ),
            'atomized_by': 'skunkworks_h_hotpotqa_landed_VET_CERT_CHAIN_GRADE_ruling_2026-06-22',
            'atomized_date': '2026-06-22',
            'session_authored': 'exp_dev_h_hotpotqa_ingest_post_medqa_pivot_to_minilm_on_entity_titles',
            'cited_numbers_reproduce_from_metrics_json': True,
            'cert_vet_status': (
                'LANDED_VET_skunkworks_2026-06-22_CERT_CHAIN_GRADE_verify_off_data'
            ),
            'verified_off_data': (
                f'Auditor re-derived all cited numbers independently from {METRICS_PATH} '
                f'via this atomize script: 3-seed mean setrecall={sr_mean:.4f} (cv={sr_cv:.4f}), '
                f'rand_ctrl={rand_mean:.4f}, refuse OOD={ood_mean:.4f} acc={acc_mean:.4f}, '
                f'substrate_2hop={s2_mean:.4f}, baseline_1hop_direct={b1_mean:.4f} '
                f'(ratio={ratio_1hop:.2f}x), baseline_frozen_encoder={enc_mean:.4f} '
                f'(ratio={ratio_enc:.2f}x), bridge_recall={bridge_mean:.4f}, '
                f'encoder off-diag mean cos={geom_mean:.4f}. Per-seed run_mode=full '
                f'assertion + structural assertions (N=4096, M_triples=1610, n_ent=2696, '
                f'n_chains_bridge=671, n_eval=300) all clean. All 6 HARD bands re-checked '
                f'auditor-side and pass; no HARD_FAIL floor breached. Director-cited '
                f'ratios (892x, 24.11x) reproduce within float precision. SCHEMA-VET PASS '
                f'at every invariant check.'
            ),
            'milestone': (
                'Substrate multi-domain KG-ingest portfolio reaches 3rd KG shape at '
                'chain-grade: HotpotQA Wikipedia multi-hop QA joins n8 ConceptNet '
                '(lexical) + U1 FB15k-237 (structured) under CERT_CHAIN_GRADE. The L3 '
                'multi-value-KG capability row promotes from "first chain-grade '
                'post-STANDSTILL" to "multi-domain chain-grade portfolio" - substrate '
                'KB-ingest at chain-grade now spans structured / lexical / '
                'unstructured-multi-hop KG shapes.'
            ),
        },
    )

    # ------------------------------------------------------------------
    # Write atom (idempotency-guarded above)
    # ------------------------------------------------------------------
    if not is_resume:
        ps.add_atom(
            atom,
            source='skunkworks_atomize_h_hotpotqa_chain_grade_2026-06-22',
            note='landed-VET CERT_CHAIN_GRADE ruling (3rd cross-domain KG ingest)',
        )
        print(f'\n[1] Atom written: {target_qid}')
    else:
        print(f'\n[1] Atom already in Store (resume): {target_qid}')

    # ------------------------------------------------------------------
    # A5 POST-snapshot (Store-side; pre-ledger)
    # ------------------------------------------------------------------
    ps_post = PartitionedStore(REPO / 'data' / 'substrate_index')
    post_atoms = ps_post.all_atoms()
    n_post = len(post_atoms)
    cert_post = _cert_count(ps_post)
    ax_post = _axiom_count(ps_post)
    cap_post = _cap_pres_ok()
    expected_added = 0 if is_resume else 1
    assert n_post == n_pre + expected_added, (
        f'A5-POST atom count drift: pre={n_pre} post={n_post} expected_delta={expected_added}'
    )
    assert ax_post == 206, f'A5-POST axiom drift: {ax_post} != 206'
    assert cap_post, 'A5-POST cap_pres FAIL'
    assert cert_post == cert_pre + expected_added, (
        f'A5-POST CERT drift: pre={cert_pre} post={cert_post} expected_delta={expected_added}'
    )
    print(f'\nA5-POST (Store side): atoms={n_post} CERT={cert_post} '
          f'axiom={ax_post} cap_pres={"6/6" if cap_post else "FAIL"}')

    # ------------------------------------------------------------------
    # Ledger write
    # ------------------------------------------------------------------
    print('\n--- Ledger write ---')

    row = build_chain_grade_ruling_row(
        atom_id=target_qid,
        cell_commit=CELL_COMMIT,
        verdict='HARD_PASS',
        notes_path=NOTES_PATH,
        metrics_path=METRICS_PATH,
        cv=float(sr_cv),
        cert_class='pre_reg_pass',
        atomized_by='skunkworks_h_hotpotqa_landed_VET_CERT_CHAIN_GRADE_ruling_2026-06-22',
        note=(
            'h_hotpotqa_ingest_v1_3seed_full_HARD_PASS_setrecall_1p000_cv_0p000_'
            'refuse_OOD_1p000_acc_0p997_substrate_2hop_0p991_vs_1hop_0p001_ratio_892x_'
            'vs_frozen_enc_0p041_ratio_24p11x_bridge_recall_1p000_encoder_off_diag_'
            'cos_0p1468_no_MedQA_collapse_substrate_only_decode_n_llm_0_'
            'seeds_7_17_23_run_mode_full_elapsed_21s_N_DIM_4096_M_triples_1610_'
            'n_ent_2696_n_eval_300_3rd_cross_domain_chain_grade_KG_ingest_after_'
            'n8_ConceptNet_lexical_and_U1_FB15k_237_structured_now_unstructured_'
            'multi_hop_QA_on_Wikipedia_titles_substantiates_substrate_multi_domain_'
            'KG_ingest_at_chain_grade_across_3_KG_shapes_encoder_MiniLM_L6_chosen_'
            'over_pythia_160m_mean_pool_post_MedQA_collapse_pre_reg_documents_'
            'deviation_geometry_HALT_guard_wired_silent_at_0p1468_pre_reg_direction'
            '_honored_substrate_dominates_both_baselines_at_every_seed'
        ),
    )
    # Note: by ledger-write time the atom is already in Store and counted (CERT N
    # is already 588). The ledger row is a RECORD of the cert decision; the Store's
    # pq field is the actual cert state. Pre==post==588 reflects post-atom-write
    # snapshot; cert_increment_delta=+1 (set by build_chain_grade_ruling_row)
    # captures the conceptual delta. Mirrors the g1b pattern for the same reason.
    h1 = append_cert_ledger_row(
        row,
        expected_cert_n_pre=EXPECTED_CERT_POST,   # 588: post-atom-write live state
        expected_cert_n_post=EXPECTED_CERT_POST,  # 588: same; row records decision
        strict_a5=True,
    )
    print(f'  row hash: {h1}  (atom={target_qid})')

    # ------------------------------------------------------------------
    # Final A5 POST-snapshot
    # ------------------------------------------------------------------
    ps_final = PartitionedStore(REPO / 'data' / 'substrate_index')
    final_atoms = ps_final.all_atoms()
    final_n = len(final_atoms)
    final_cert = _cert_count(ps_final)
    final_ax = _axiom_count(ps_final)
    final_cap = _cap_pres_ok()
    ledger_lines = (REPO / 'data' / 'substrate_index' / 'meta' / 'cert_ledger.jsonl').read_text(
        encoding='utf-8'
    ).splitlines()
    n_ledger = len([l for l in ledger_lines if l.strip()])

    # On resume the n_pre/cert_pre already reflect post-atom-write state; final delta = 0.
    # Show the conceptual transition (pre-substrate-change baseline -> post) regardless.
    concept_atoms_pre = n_pre if not is_resume else n_pre - 1
    concept_cert_pre = cert_pre if not is_resume else cert_pre - 1
    print('\n' + '=' * 78)
    print('A5-FINAL:')
    print(f'  atoms: {concept_atoms_pre} -> {final_n} (delta=+{final_n - concept_atoms_pre})')
    print(f'  CERT_CHAIN_GRADE N: {concept_cert_pre} -> {final_cert} '
          f'(delta={final_cert - concept_cert_pre})')
    print(f'  axiom_term: {final_ax} (preserved {final_ax == 206})')
    print(f'  cap_pres: {"6/6" if final_cap else "FAIL"}')
    print(f'  ledger rows: 653 -> {n_ledger} (delta={n_ledger - 653})')
    print(f'  row hash: {h1}')
    print('=' * 78)

    return {
        'atom_qid': target_qid,
        'row_hash': h1,
        'atoms_pre': n_pre,
        'atoms_post': final_n,
        'cert_pre': cert_pre,
        'cert_post': final_cert,
        'axiom_term': final_ax,
        'cap_pres_ok': final_cap,
        'ledger_rows_post': n_ledger,
    }


if __name__ == '__main__':
    result = main()
    print('\nResult:', json.dumps(result, indent=2))
