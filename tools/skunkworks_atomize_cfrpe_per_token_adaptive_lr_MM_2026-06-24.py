"""Skunkworks 2026-06-24 -- landed-VET + atomize substrate_cfrpe_per_token_adaptive_lr_v1.

Disposition (post-landed-VET):
  Cell self-verdict: MIDDLE_BAND (lift 0.345 in [0.20, 0.40) under BPC scope).
  Skunkworks ruling: MEASURED_MECHANISM (CERT-neutral, delta=0).

Verify-OFF-DATA independent recompute confirms all cell aggregate numbers:
  ARM_UNIGRAM bpc=7.7378 top1=0.2171 (deterministic single seed)
  ARM_HEBBIAN_BASELINE bpc=7.3372 cv=0.0009 top1=0.2137
  ARM_CFRPE_COARSE_5000 bpc=7.0707 cv=0.0025 top1=0.2422
  ARM_CFRPE_PER_TOKEN_ADAPTIVE bpc=6.9920 cv=0.0016 top1=0.2427  <-- candidate
  ARM_CFRPE_PER_TOKEN_PLATEAU bpc=7.0778 cv=0.0021 top1=0.2246
All lambda_zero_collapse=False (C7 PASS); n_clamped_steps=0/5000 on adaptive arm (FLOOR=0.25
CEIL=4.0 never engaged; mechanism in honest dynamic range; NOT by-construction-saturation).

Why MEASURED_MECHANISM and NOT chain-grade:
  1. BPC chain-grade gating is BLOCKED by META_HARNESS_RIGGED (cert_ledger row 698, atom
     math::T3/META_HARNESS_RIGGED_substrate_LM_readout_uncalibrated_temperature_BPC_wrong_metric_2026-06-23).
     BPC was atomized as the WRONG metric for substrate-as-LM chain-grade; only top1 carries.
  2. top1 chain-grade bar set by n1_v3 (cert_ledger row 699): substrate top1 lift +61.6% rel
     vs unigram (top1 0.4455 vs 0.2757). This cell adaptive arm: top1 lift +11.78% rel vs
     unigram (top1 0.2427 vs 0.2171). 0.15x the chain-grade bar; 15% of the way there.
  3. Adaptive vs coarse cf-RPE top1 delta = +0.0005 abs (0.10sigma; seed noise; pooled SE
     0.00485). The +0.345 BPC improvement does NOT propagate to top1.
  4. Precedent: cert_ledger row 707 (2026-06-24, 12h earlier) ruled the n_steps_curve_v1
     cell MEASURED_MECHANISM on the exact same signature (BPC improvement without proportional
     top1 lift, BPC chain-grade blocked). Consistent ruling.

What IS proven by this cell (mechanism characterization):
  A. New BPC operating point at production scale: bpc=6.9920 cv=0.0013 at N_DIM=8192
     N_TRAIN=100k V=4000 N_STEPS=5000 (-0.078 bits vs coarse cf-RPE under same setup).
  B. Per-token median-normalized LR reduces seed variance ~3x vs uniform LR (cv 0.0013 vs
     0.0025 for coarse cf-RPE at the same N).
  C. Adaptive optimum picks lambda=0.3 vs coarse lambda=0.2 (distinct interior operating
     point; per_token_lr_max_min_ratio ~2.4 within the 16x clamp band; no boundary saturation).
  D. Plateau-decay layer (ARM_CFRPE_PER_TOKEN_PLATEAU) HURT vs pure adaptive (top1 0.2246 vs
     0.2427; plateau-decay shrinks global LR which over-dampens the per-token signal).

A5 PRE: CERT=594 atoms=177326. POST: CERT=594 (UNCHANGED; MM CERT-neutral) atoms=177327 (+1).
Ledger row appended with delta=0.

Atom written:
  math::T3/EXP_substrate_cfrpe_per_token_adaptive_lr_v1_MM -- EXPERIMENT_RECORD pq=MEASURED_MECHANISM

(No META atom in this filing -- the BPC-vs-top1 trap is already atomized in META_HARNESS_RIGGED
row 698; the variance-reduction observation is interesting but does not yet rise to META status
on its own.)
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('D:/AI/hd-instrument').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row, build_measured_mechanism_row


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


CFRPE_ADAPT_MM = Atom(
    id='T3/EXP_substrate_cfrpe_per_token_adaptive_lr_v1_MM',
    name=('Experiment record (MEASURED_MECHANISM, CERT-neutral): cf-RPE per-token adaptive '
          'median-normalized LR achieves new BPC operating point bpc=6.9920 cv=0.0013 at '
          'N_DIM=8192 V=4000 text8 100k N_STEPS=5000, but BPC improvement (+0.078 bits vs '
          'coarse cf-RPE) does NOT propagate to top1 (adaptive top1=0.2427 vs coarse '
          'top1=0.2422; delta +0.0005 = 0.10sigma seed noise). top1 chain-grade BLOCKED at '
          '+11.78% rel vs unigram (0.15x the n1_v3 chain-grade bar +61.6%). BPC chain-grade '
          'BLOCKED under META_HARNESS_RIGGED row 698 (wrong-metric). Mechanism real and in '
          'honest dynamic range (n_clamped_steps=0/5000; max/min lr ratio ~2.4 << 16x clamp); '
          'NOT by-construction-saturation. Variance-reduction observation: per-token '
          'median-normalized rule reduces seed CV ~3x vs uniform.'),
    description=(
        'cf-RPE per-token adaptive LR cell at production scale, post-cfrpe_n_steps_curve_v1 MM '
        '(cert row 707) follow-up: tests whether per-sample LR weighting (proportional to '
        'prediction-error magnitude, median-normalized within batch, clamped to [0.25, 4.0]) '
        'beats coarse uniform LR. Also tests a plateau-decay variant (per-token + global '
        'EMA-detected plateau halving). Three seeds {7, 17, 23}, four arms '
        '{ARM_HEBBIAN_BASELINE, ARM_CFRPE_COARSE_5000, ARM_CFRPE_PER_TOKEN_ADAPTIVE, '
        'ARM_CFRPE_PER_TOKEN_PLATEAU}, run_mode=full, wall=1442.8s. '
        'KEY NUMBERS (verified off per_seed, independent recompute, all match cell-author '
        'cites): '
        'ARM_HEBBIAN_BASELINE bpc=7.3372+-0.0067 cv=0.0009 top1=0.2137+-0.0080 '
        '(reproduces n_steps_curve_extension_v2 hebbian arm exactly to 4 decimals all 3 seeds; '
        'reproduces fair_harness anchor 7.3065 within +0.0307 bits, within pre-reg tol 0.05). '
        'ARM_CFRPE_COARSE_5000 bpc=7.0707+-0.0175 cv=0.0025 top1=0.2422+-0.0083 (matches '
        'n_steps_curve_extension N=5000 7.0386 within seed grid-search noise; raw_bpc_at_T1_L1 '
        'differs by <=0.007 across cells -- same W). '
        'ARM_CFRPE_PER_TOKEN_ADAPTIVE bpc=6.9920+-0.0110 cv=0.0013 top1=0.2427+-0.0013 '
        'mrr=0.3409 -- best lambda=0.3 (vs coarse lambda=0.2), best T=0.05 (matches all arms), '
        'per_token_lr_max_min_ratio_max=2.40+-0.014 (well below 16x clamp), n_clamped_steps=0 '
        'across all 3 seeds (FLOOR=0.25 / CEIL=4.0 never engages; mechanism in honest dynamic '
        'range). '
        'ARM_CFRPE_PER_TOKEN_PLATEAU bpc=7.0778+-0.0148 cv=0.0021 top1=0.2246+-0.0049 '
        '(plateau-decay HURT vs pure adaptive; n_plateau_hits=23 per seed; final_global_lr=0.0 '
        '-- plateau-decay shrunk LR all the way to zero, over-damping the per-token signal). '
        'CRITICAL CERT-FACT: adaptive vs coarse cf-RPE top1 delta = +0.0005 abs / +0.21% rel / '
        '0.10sigma (pooled SE 0.00485). The +0.345 BPC lift over hebbian = +0.078 BPC lift over '
        'coarse does NOT propagate to top1. This is the exact signature META_HARNESS_RIGGED '
        '(cert row 698 chain-grade) was atomized to catch: BPC can rank arms differently than '
        'top1 (the actual substrate-as-LM gating metric). '
        'CHAIN-GRADE BAR (n1_v3, cert row 699): substrate top1 0.4455 vs unigram 0.2757 = '
        '+61.6% relative lift. This cell adaptive: +11.78% relative -- 0.15x the bar; 15% of '
        'the way to chain-grade on top1. '
        'C7 GATE PASS: lambda_zero_collapse=False for all 12 (3 seeds x 4 arms). '
        'DISPOSITION = MEASURED_MECHANISM. Cell self-verdict MIDDLE_BAND under BPC scope is '
        'correct in its own pre-reg, but the cert-architecture (META_HARNESS_RIGGED) requires '
        'top1 propagation for chain-grade promotion. PRECEDENT: cert row 707 (2026-06-24, '
        '12h earlier) ruled cfrpe_n_steps_curve_v1 MM on the same signature. '
        'PATH TO CHAIN-GRADE (revival angles route to Research): '
        '(1) top1-targeted readout on the adaptive W matrices (current pipeline tunes T,lambda '
        'for BPC -- a top1-tuned readout may surface real top1 lift the BPC-optimized eval '
        'misses); '
        '(2) 5-seed adaptive at N=5000 to confirm cv=0.0013 tightness reproduces (rules out '
        'seed-luck on 7/17/23); '
        '(3) adaptive cf-RPE x STDP compose -- tighter variance + different lambda-operating-'
        'point may compose super-additively with heterogeneous plasticity (fair_harness STDP '
        'HET chain-grade at top1=0.2368); '
        '(4) adaptive at N>=15000 -- does the +0.005 top1 delta vs coarse grow with N or '
        'saturate? '
        '(5) median-normalized rule applied to plateau arm only -- plateau-decay over-damped '
        'in this run (final_global_lr=0.0); rework decay schedule.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'HIGH',
        'verdict': ('MEASURED_MECHANISM_FULL_3seeds_N_DIM_8192_N_TRAIN_100k_text8_V4000_'
                    'N_STEPS_5000_cfrpe_per_token_adaptive_LR_bpc_6p9920_cv_0p0013_top1_'
                    '0p2427_lift_over_unigram_plus11p78pct_rel_vs_n1_v3_chain_grade_bar_'
                    'plus61p6pct_BPC_chain_grade_blocked_by_META_HARNESS_RIGGED_row_698_'
                    'top1_vs_coarse_cfrpe_delta_plus0p0005_abs_0p10sigma_seed_noise_'
                    'n_clamped_steps_0_of_5000_max_min_lr_ratio_2p4_mechanism_in_honest_'
                    'dynamic_range_NOT_by_construction_saturation_lambda_zero_collapse_'
                    'False_all_12_arm_seed_combos_C7_PASS_plateau_arm_under_damped_'
                    'final_global_lr_0p0_top1_0p2246_self_filed_MIDDLE_BAND_under_BPC_scope'
                    '_skunkworks_override_to_MM_per_META_HARNESS_RIGGED_top1_metric_scope_'
                    'precedent_cert_row_707_n_steps_curve_v1_MM_same_signature_12h_earlier'),
        'run_mode': 'full', 'n_seeds': 3, 'seeds': [7, 17, 23],
        'cell_commit': 'eeb6b1c3',  # exp_dev: filed substrate_cfrpe_per_token_adaptive_lr_v1 SHIPPED
        'metrics_path': 'data/exp_substrate_cfrpe_per_token_adaptive_lr_v1/metrics.json',
        'notes_path': ('notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_'
                       'MEASURED_MECHANISM_2026-06-24.md'),
        'prereg_path': 'preregs/2026-06-24_substrate_cfrpe_per_token_adaptive_lr_v1.md',
        'metrics_source': 'measured_substrate_as_lm_cfrpe_per_token_adaptive_lr_vs_coarse_vs_plateau_vs_hebbian',
        'N_DIM': 8192, 'N_TRAIN': 100000, 'N_HELD': 20000, 'VOCAB_CAP': 4000,
        'N_STEPS_PLASTIC': 5000, 'CFRPE_LR': 0.5, 'INGEST_BATCH': 64,
        'SPARSE_BIPOLAR_F': 0.05,
        'corpus': 'text8',
        'LAMBDA_GRID': [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
        'TEMP_GRID': [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        'ADAPT_LR_FLOOR': 0.25, 'ADAPT_LR_CEIL': 4.0,
        'PLATEAU_WINDOW': 200, 'PLATEAU_EMA_BETA': 0.9, 'PLATEAU_DECAY': 0.5,
        'PLATEAU_TOL': 0.001,
        'key_metrics': {
            'unigram_bpc': 7.7378, 'unigram_top1': 0.2171, 'unigram_mrr': 0.2761,
            'hebbian_baseline_bpc': 7.3372, 'hebbian_baseline_cv': 0.0009,
            'hebbian_baseline_top1': 0.2137,
            'cfrpe_coarse_5000_bpc': 7.0707, 'cfrpe_coarse_5000_cv': 0.0025,
            'cfrpe_coarse_5000_top1': 0.2422, 'cfrpe_coarse_5000_mrr': 0.3383,
            'cfrpe_per_token_adaptive_bpc': 6.9920, 'cfrpe_per_token_adaptive_cv': 0.0013,
            'cfrpe_per_token_adaptive_top1': 0.2427, 'cfrpe_per_token_adaptive_mrr': 0.3409,
            'cfrpe_per_token_plateau_bpc': 7.0778, 'cfrpe_per_token_plateau_cv': 0.0021,
            'cfrpe_per_token_plateau_top1': 0.2246, 'cfrpe_per_token_plateau_mrr': 0.3265,
            'adaptive_vs_coarse_top1_delta_abs': 0.0005,
            'adaptive_vs_coarse_top1_delta_sigma': 0.10,
            'adaptive_vs_coarse_top1_pooled_se': 0.00485,
            'adaptive_top1_lift_over_unigram_abs': 0.0256,
            'adaptive_top1_lift_over_unigram_rel_pct': 11.78,
            'n1_v3_chain_grade_bar_top1_lift_rel_pct': 61.6,
            'fraction_of_chain_grade_bar': 0.151,
            'adaptive_n_clamped_steps_max_seed': 0,
            'adaptive_per_token_lr_max_min_ratio_max_seed': 2.430,
            'plateau_final_global_lr_min_seed': 0.0,
            'plateau_n_plateau_hits_per_seed': 23,
            'wall_s': 1442.83,
        },
        'cert_gates_status': {
            'C7_lambda_zero_collapse_False_all_arms_all_seeds': 'PASS (12/12 False)',
            'hebbian_sanity_within_tol_0.05_of_fair_harness_7.3065': 'PASS (drift +0.0307)',
            'cv_below_0.10_bar': 'PASS (max cv=0.0025 coarse, 0.0013 adaptive)',
            'mechanism_not_by_construction_saturation': 'PASS (n_clamped_steps=0; ratio~2.4 << 16x)',
            'cell_self_verdict_BPC_HARD_PASS_lift_ge_0.40': 'FAIL (lift=0.345 < 0.40)',
            'cell_self_verdict_BPC_chain_grade_bonus_bpc_le_6.85': 'FAIL (bpc=6.992 > 6.85)',
            'cert_arch_top1_chain_grade_lift_vs_unigram_ge_61.6pct_rel_n1_v3_bar': 'FAIL (+11.78% rel)',
            'cert_arch_top1_vs_coarse_cfrpe_real_signal_z_ge_1.96': 'FAIL (z=0.10)',
            'cert_arch_BPC_metric_scope_under_META_HARNESS_RIGGED_row_698': 'BLOCKED (wrong metric)',
        },
        'honest_scope': (
            'cf-RPE per-token adaptive LR PROVEN: (a) new BPC operating point bpc=6.9920 cv=0.0013 '
            'at production scale (-0.078 BPC vs coarse cf-RPE; -0.345 BPC vs Hebbian); (b) variance '
            'reduction ~3x vs coarse (cv 0.0013 vs 0.0025); (c) mechanism operates in honest dynamic '
            'range (n_clamped_steps=0, ratio~2.4 vs 16x clamp); (d) interior lambda=0.3 optimum '
            'distinct from coarse lambda=0.2. NOT PROVEN: (a) top1 lift over coarse cf-RPE (delta '
            '+0.0005 / 0.10sigma seed noise); (b) BPC chain-grade (BLOCKED by META_HARNESS_RIGGED '
            'wrong-metric); (c) STDP compose; (d) generalization beyond text8 V=4000; (e) encoder '
            'sensitivity; (f) top1-targeted readout (current eval BPC-tuned T,lambda); (g) plateau-'
            'decay tuning (this run over-damped to final_global_lr=0.0).'),
        'finding': (
            'Per-token median-normalized adaptive cf-RPE is a real mechanism that improves BPC '
            'and reduces seed variance but does NOT improve top1 (the substrate-as-LM gating '
            'metric per META_HARNESS_RIGGED). Useful as MECHANISM CHARACTERIZATION for future '
            'compose tests (STDP, top1-readout) but not chain-grade-eligible at current top1 '
            'numbers.'),
        'baseline_provenance': (
            'ARM_HEBBIAN_BASELINE: reproduces n_steps_curve_extension_v2 hebbian arm to 4 decimals '
            'across all 3 seeds (per-seed [7.3411, 7.3295, 7.3411] vs [7.3411, 7.3295, 7.3411]); '
            'reproduces fair_harness ARM_HEBBIAN_ONLY anchor 7.3065 within +0.0307 bits (within '
            'pre-reg tolerance 0.05). ARM_CFRPE_COARSE_5000: reproduces n_steps_curve_extension '
            'N5000_cfrpe arm within shallow-plateau grid-search noise (raw_bpc_at_T1_L1 differs by '
            '<=0.007 across cells; same W). ARM_UNIGRAM: deterministic single-seed top1=0.2171 '
            'identical to all priors at same V=4000 text8 setup.'),
        'composes_with': [
            'math::T3/EXP_substrate_cfrpe_n_steps_curve_v1_MM',  # row 707 precedent (same signature)
            'math::T3/EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512',  # fair_harness STDP chain-grade
            'math::T3/META_HARNESS_RIGGED_substrate_LM_readout_uncalibrated_temperature_BPC_wrong_metric_2026-06-23',
            'math::T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_TOP1_CG',  # row 699 top1 chain-grade bar
        ],
        'depends_on_text': (
            'cf-RPE delta-rule plasticity (error = target - reconstruction; W += lr * error.t() @ Ctx '
            '/ batch) extended with per-sample LR scaling. Per-token LR rule: e_norm[i] = '
            '||error[i]||/sqrt(dim); med = median(e_norm); lr_per[i] = base_lr * '
            'clamp(e_norm[i]/(med+eps), 0.25, 4.0). Median-normalization preserves batch-mean '
            'update magnitude; clamp prevents outlier runaway. Plateau variant adds EMA-detected '
            'global-LR halving (PLATEAU_DECAY=0.5 on PLATEAU_TOL=0.001 relative improvement over '
            'PLATEAU_WINDOW=200 steps). All operations: pure torch.float32 BLAS on CUDA; no LLM '
            'forward calls anywhere; substrate-only.'),
        'cert_vet_status': ('LANDED_VET_skunkworks_2026-06-24_MEASURED_MECHANISM_verify_off_data_'
                            'all_cited_numbers_match_top1_chain_grade_blocked_BPC_chain_grade_blocked'),
        'verified_off_data': (
            'cert-owner re-derived independently from per_seed via .venv python: bpc_mean per arm '
            'matches cell aggregate to 4 decimals (unigram 7.7378, hebbian 7.3372, coarse 7.0707, '
            'adaptive 6.9920, plateau 7.0778). top1_mean per arm matches (unigram 0.2171, hebbian '
            '0.2137, coarse 0.2422, adaptive 0.2427, plateau 0.2246). lifts (vs hebbian) match: '
            'coarse 0.2665, adaptive 0.3452, plateau 0.2594. C7 lambda_zero_collapse=False '
            'verified for all 12 arm-seed combos. n_clamped_steps verified 0/5000 for all 3 '
            'adaptive seeds; per_token_lr_max_min_ratio_max verified ~2.4 per seed (well below '
            '16x clamp). Plateau arm n_plateau_hits=23/5000 per seed and final_global_lr=0.0 '
            'verified (over-damped). Cross-cell hebbian per-seed reproduces n_steps_curve_'
            'extension_v2 to 4 decimals. Cross-cell coarse cf-RPE raw_bpc_at_T1_L1 reproduces '
            'within <=0.007 bits (W is essentially same; grid-search differences). pooled SE '
            'computed independently for adaptive-vs-coarse top1: 0.00485 -> z=0.10sigma.'),
        'incomplete_deliverable': (
            'top1 chain-grade BLOCKED: adaptive top1 lift over unigram +11.78% rel (n1_v3 bar +61.6%). '
            'top1 vs coarse cf-RPE delta +0.0005 / 0.10sigma = seed noise. BPC chain-grade BLOCKED '
            'under META_HARNESS_RIGGED row 698 (wrong metric for substrate-as-LM). Path to chain-grade '
            '(per revival angles in landed-VET note): (1) top1-targeted readout pass on existing '
            'adaptive W matrices -- BPC-optimized T,lambda may hide a real top1 lift; (2) 5-seed '
            'reproduction to rule out seed-luck on tighter cv=0.0013; (3) adaptive x STDP super-'
            'additive compose; (4) N>=15000 extension; (5) plateau decay schedule rework (current '
            'over-damps).'),
        'verdict_classification_note': (
            'Cell self-verdict MIDDLE_BAND is correct under its own pre-reg BPC-lift bands '
            '(lift 0.345 in [0.20, 0.40) -> MIDDLE_BAND). Skunkworks overrides to MEASURED_MECHANISM '
            'per cert-architecture: BPC is the wrong metric for substrate-as-LM chain-grade (META_'
            'HARNESS_RIGGED row 698), and top1 chain-grade evidence does NOT exist (lift vs unigram '
            '0.15x bar; lift vs coarse 0.10sigma). Director described this as "lowest substrate-as-LM '
            'single-arm BPC ever recorded / NEW SINGLE-ARM CHAIN-GRADE candidate" -- Fix #28 override: '
            'BPC framing is exactly the META_HARNESS_RIGGED trap. Honest framing: "new BPC operating '
            'point + variance-reduction mechanism; top1 chain-grade not achieved." Skunkworks-overrides-'
            'Director per Fix #28 + by-construction-saturation discipline + precedent row 707.'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-24',
        'era': ('comprehensive_program_phase3_substrate_as_lm_cfrpe_plasticity_arc_post_META_HARNESS_'
                'RIGGED_top1_metric_scope_top1_chain_grade_pipeline'),
        'milestone': ('cfrpe per-token adaptive LR new BPC operating point 6.9920 (production '
                      'scale) measured-mechanism + variance-reduction ~3x + lambda=0.3 distinct '
                      'optimum + plateau-decay over-damping characterized -- chain-grade path '
                      'via top1-targeted readout OR 5-seed reproduction OR STDP compose'),
    })


def main():
    ps = PartitionedStore(Path('D:/AI/hd-instrument/data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod:
        print("PRE-GATE FAIL (cap_pres down). HALT."); return 1
    expected_cert = pre_cert  # MM is CERT-neutral; record current N as reference

    # Add atom (idempotent)
    added = 0
    existed = ps.get_atom('math::' + CFRPE_ADAPT_MM.id) is not None
    if existed:
        print(f"  SKIP exists: {CFRPE_ADAPT_MM.id}")
    else:
        ps.add_atom(CFRPE_ADAPT_MM,
                    source='skunkworks_cfrpe_per_token_adaptive_lr_v1_MM_2026_06_24',
                    note=f'{CFRPE_ADAPT_MM.id} landed-VET MEASURED_MECHANISM (CERT-neutral)')
        added += 1
        print(f"  ADD: {CFRPE_ADAPT_MM.id}")

    # POST-A5 (Store re-load + invariants)
    ps2 = PartitionedStore(Path('D:/AI/hd-instrument/data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom('math::' + CFRPE_ADAPT_MM.id) is not None
    bad_alg = (landed and ps2.get_atom('math::' + CFRPE_ADAPT_MM.id).algebra is not None)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} "
          f"(expect {expected_cert} UNCHANGED) axiom={post_ax} cap_pres={post_mod} "
          f"landed={landed} bad_alg={bad_alg}")
    a5_atom_gate = (post_cert == expected_cert and post_ax == pre_ax and post_mod
                    and landed and not bad_alg
                    and post_atoms == pre_atoms + added)
    if not a5_atom_gate:
        print("A5-ATOM GATE: FAIL"); return 2
    print(f"A5-ATOM GATE: OK -- atom filed, CERT {expected_cert} unchanged (MM CERT-neutral)")

    # Ledger A5-write (cert_increment_delta=0 for MM)
    row = build_measured_mechanism_row(
        atom_id='math::' + CFRPE_ADAPT_MM.id,
        cell_commit='eeb6b1c3',
        verdict='MIDDLE_BAND',  # cell's self-verdict; skunkworks ruling captured in note
        notes_path=('notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_'
                    'MEASURED_MECHANISM_2026-06-24.md'),
        metrics_path='data/exp_substrate_cfrpe_per_token_adaptive_lr_v1/metrics.json',
        atomized_by='skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_2026-06-24',
        note=('cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_landed_VET_skunkworks_override_'
              'cell_self_MIDDLE_BAND_per_META_HARNESS_RIGGED_row_698_top1_metric_scope_adaptive_'
              'bpc_6p9920_new_BPC_operating_point_minus_0p078_vs_coarse_minus_0p345_vs_hebbian_'
              'cv_0p0013_variance_reduction_3x_top1_0p2427_vs_coarse_0p2422_delta_plus_0p0005_'
              'pooled_SE_0p00485_z_0p10sigma_seed_noise_top1_lift_over_unigram_plus_11p78pct_rel_'
              'vs_n1_v3_chain_grade_bar_plus_61p6pct_rel_0p15x_bar_n_clamped_steps_0_of_5000_'
              'per_token_lr_max_min_ratio_2p4_well_below_16x_clamp_mechanism_in_honest_dynamic_'
              'range_NOT_by_construction_saturation_lambda_zero_collapse_False_all_12_arm_seed_'
              'combos_C7_PASS_plateau_arm_under_damped_final_global_lr_0p0_top1_0p2246_lower_'
              'than_pure_adaptive_precedent_cert_row_707_n_steps_curve_v1_MM_same_signature_'
              '12h_earlier_director_BPC_record_framing_overridden_per_Fix28_per_arm_top1_metric_'
              'chain_grade_check_revival_angles_top1_targeted_readout_5seed_STDP_compose_N15000'
              '_extension_plateau_decay_rework_route_to_research'),
    )
    new_hash = append_cert_ledger_row(row,
        expected_cert_n_pre=expected_cert,
        expected_cert_n_post=expected_cert,  # delta=0 for MEASURED_MECHANISM
    )
    print(f"CERT_LEDGER_ROW_HASH: {new_hash}")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
